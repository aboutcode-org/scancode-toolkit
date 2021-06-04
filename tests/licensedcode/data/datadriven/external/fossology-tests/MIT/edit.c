/*	$OpenBSD: edit.c,v 1.34 2010/05/20 01:13:07 fgsch Exp $	*/
/*	$OpenBSD: edit.h,v 1.8 2005/03/28 21:28:22 deraadt Exp $	*/
/*	$OpenBSD: emacs.c,v 1.42 2009/06/02 06:47:47 halex Exp $	*/
/*	$OpenBSD: vi.c,v 1.26 2009/06/29 22:50:19 martynas Exp $	*/

/*-
 * Copyright (c) 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010
 *	Thorsten Glaser <tg@mirbsd.org>
 *
 * Provided that these terms and disclaimer and all copyright notices
 * are retained or reproduced in an accompanying document, permission
 * is granted to deal in this work without restriction, including un-
 * limited rights to use, publicly perform, distribute, sell, modify,
 * merge, give away, or sublicence.
 *
 * This work is provided "AS IS" and WITHOUT WARRANTY of any kind, to
 * the utmost extent permitted by applicable law, neither express nor
 * implied; without malicious intent or gross negligence. In no event
 * may a licensor, author or contributor be held liable for indirect,
 * direct, other damage, loss, or other issues arising in any way out
 * of dealing in the work, even if advised of the possibility of such
 * damage or existence of a defect, except proven that it results out
 * of said person's immediate fault when using the work as intended.
 */

#include "sh.h"

__RCSID("$MirOS: src/bin/mksh/edit.c,v 1.196 2010/07/25 11:35:40 tg Exp $");

/*
 * in later versions we might use libtermcap for this, but since external
 * dependencies are problematic, this has not yet been decided on; another
 * good string is "\033c" except on hardware terminals like the DEC VT420
 * which do a full power cycle then...
 */
#ifndef MKSH_CLS_STRING
#define MKSH_CLS_STRING		"\033[;H\033[J"
#endif
#ifndef MKSH_CLRTOEOL_STRING
#define MKSH_CLRTOEOL_STRING	"\033[K"
#endif

/* tty driver characters we are interested in */
typedef struct {
	int erase;
	int kill;
	int werase;
	int intr;
	int quit;
	int eof;
} X_chars;

static X_chars edchars;

/* x_fc_glob() flags */
#define XCF_COMMAND	BIT(0)	/* Do command completion */
#define XCF_FILE	BIT(1)	/* Do file completion */
#define XCF_FULLPATH	BIT(2)	/* command completion: store full path */
#define XCF_COMMAND_FILE (XCF_COMMAND|XCF_FILE)

static char editmode;
static int xx_cols;			/* for Emacs mode */
static int modified;			/* buffer has been "modified" */
static char holdbuf[LINE];		/* place to hold last edit buffer */

static int x_getc(void);
static void x_putcf(int);
static bool x_mode(bool);
static int x_do_comment(char *, int, int *);
static void x_print_expansions(int, char *const *, bool);
static int x_cf_glob(int, const char *, int, int, int *, int *, char ***,
    bool *);
static int x_longest_prefix(int, char *const *);
static int x_basename(const char *, const char *);
static void x_free_words(int, char **);
static int x_escape(const char *, size_t, int (*)(const char *, size_t));
static int x_emacs(char *, size_t);
static void x_init_emacs(void);
static void x_init_prompt(void);
#if !MKSH_S_NOVI
static int x_vi(char *, size_t);
#endif

#define x_flush()	shf_flush(shl_out)
#ifdef MKSH_SMALL
#define x_putc(c)	x_putcf(c)
#else
#define x_putc(c)	shf_putc((c), shl_out)
#endif

static int path_order_cmp(const void *aa, const void *bb);
static char *add_glob(const char *, int)
    MKSH_A_NONNULL((nonnull (1)))
    MKSH_A_BOUNDED(string, 1, 2);
static void glob_table(const char *, XPtrV *, struct table *);
static void glob_path(int flags, const char *, XPtrV *, const char *);
static int x_file_glob(int, const char *, int, char ***)
    MKSH_A_NONNULL((nonnull (2)))
    MKSH_A_BOUNDED(string, 2, 3);
static int x_command_glob(int, const char *, int, char ***)
    MKSH_A_NONNULL((nonnull (2)))
    MKSH_A_BOUNDED(string, 2, 3);
static int x_locate_word(const char *, int, int, int *, bool *);

static int x_e_getmbc(char *);
static int x_e_rebuildline(const char *);

/* +++ generic editing functions +++ */

/* Called from main */
void
x_init(void)
{
	/* set to -2 to force initial binding */
	edchars.erase = edchars.kill = edchars.intr = edchars.quit =
	    edchars.eof = -2;
	/* default value for deficient systems */
	edchars.werase = 027;	/* ^W */
	x_init_emacs();
}

/*
 * read an edited command line
 */
int
x_read(char *buf, size_t len)
{
	int i;

	x_mode(true);
	modified = 1;
	if (Flag(FEMACS) || Flag(FGMACS))
		i = x_emacs(buf, len);
#if !MKSH_S_NOVI
	else if (Flag(FVI))
		i = x_vi(buf, len);
#endif
	else
		i = -1;		/* internal error */
	editmode = 0;
	x_mode(false);
	return (i);
}

/* tty I/O */

static int
x_getc(void)
{
	char c;
	int n;

	while ((n = blocking_read(STDIN_FILENO, &c, 1)) < 0 && errno == EINTR)
		if (trap) {
			x_mode(false);
			runtraps(0);
#ifdef SIGWINCH
			if (got_winch) {
				change_winsz();
				if (x_cols != xx_cols && editmode == 1) {
					/* redraw line in Emacs mode */
					xx_cols = x_cols;
					x_e_rebuildline(MKSH_CLRTOEOL_STRING);
				}
			}
#endif
			x_mode(true);
		}
	return ((n == 1) ? (int)(unsigned char)c : -1);
}

static void
x_putcf(int c)
{
	shf_putc(c, shl_out);
}

/*********************************
 * Misc common code for vi/emacs *
 *********************************/

/* Handle the commenting/uncommenting of a line.
 * Returns:
 *	1 if a carriage return is indicated (comment added)
 *	0 if no return (comment removed)
 *	-1 if there is an error (not enough room for comment chars)
 * If successful, *lenp contains the new length. Note: cursor should be
 * moved to the start of the line after (un)commenting.
 */
static int
x_do_comment(char *buf, int bsize, int *lenp)
{
	int i, j, len = *lenp;

	if (len == 0)
		return (1); /* somewhat arbitrary - it's what AT&T ksh does */

	/* Already commented? */
	if (buf[0] == '#') {
		bool saw_nl = false;

		for (j = 0, i = 1; i < len; i++) {
			if (!saw_nl || buf[i] != '#')
				buf[j++] = buf[i];
			saw_nl = buf[i] == '\n';
		}
		*lenp = j;
		return (0);
	} else {
		int n = 1;

		/* See if there's room for the #s - 1 per \n */
		for (i = 0; i < len; i++)
			if (buf[i] == '\n')
				n++;
		if (len + n >= bsize)
			return (-1);
		/* Now add them... */
		for (i = len, j = len + n; --i >= 0; ) {
			if (buf[i] == '\n')
				buf[--j] = '#';
			buf[--j] = buf[i];
		}
		buf[0] = '#';
		*lenp += n;
		return (1);
	}
}

/****************************************************
 * Common file/command completion code for vi/emacs *
 ****************************************************/

static void
x_print_expansions(int nwords, char * const *words, bool is_command)
{
	bool use_copy = false;
	int prefix_len;
	XPtrV l = { NULL, NULL, NULL };

	/* Check if all matches are in the same directory (in this
	 * case, we want to omit the directory name)
	 */
	if (!is_command &&
	    (prefix_len = x_longest_prefix(nwords, words)) > 0) {
		int i;

		/* Special case for 1 match (prefix is whole word) */
		if (nwords == 1)
			prefix_len = x_basename(words[0], NULL);
		/* Any (non-trailing) slashes in non-common word suffixes? */
		for (i = 0; i < nwords; i++)
			if (x_basename(words[i] + prefix_len, NULL) >
			    prefix_len)
				break;
		/* All in same directory? */
		if (i == nwords) {
			while (prefix_len > 0 && words[0][prefix_len - 1] != '/')
				prefix_len--;
			use_copy = true;
			XPinit(l, nwords + 1);
			for (i = 0; i < nwords; i++)
				XPput(l, words[i] + prefix_len);
			XPput(l, NULL);
		}
	}
	/*
	 * Enumerate expansions
	 */
	x_putc('\r');
	x_putc('\n');
	pr_list(use_copy ? (char **)XPptrv(l) : words);

	if (use_copy)
		XPfree(l); /* not x_free_words() */
}

/**
 * Do file globbing:
 *	- appends * to (copy of) str if no globbing chars found
 *	- does expansion, checks for no match, etc.
 *	- sets *wordsp to array of matching strings
 *	- returns number of matching strings
 */
static int
x_file_glob(int flags MKSH_A_UNUSED, const char *str, int slen, char ***wordsp)
{
	char *toglob, **words;
	int nwords, i, idx;
	bool escaping;
	XPtrV w;
	struct source *s, *sold;

	if (slen < 0)
		return (0);

	toglob = add_glob(str, slen);

	/* remove all escaping backward slashes */
	escaping = false;
	for (i = 0, idx = 0; toglob[i]; i++) {
		if (toglob[i] == '\\' && !escaping) {
			escaping = true;
			continue;
		}
		/* specially escape escaped [ or $ or ` for globbing */
		if (escaping && (toglob[i] == '[' ||
		    toglob[i] == '$' || toglob[i] == '`'))
			toglob[idx++] = QCHAR;

		toglob[idx] = toglob[i];
		idx++;
		if (escaping)
			escaping = false;
	}
	toglob[idx] = '\0';

	/*
	 * Convert "foo*" (toglob) to an array of strings (words)
	 */
	sold = source;
	s = pushs(SWSTR, ATEMP);
	s->start = s->str = toglob;
	source = s;
	if (yylex(ONEWORD | LQCHAR) != LWORD) {
		source = sold;
		internal_warningf("fileglob: substitute error");
		return (0);
	}
	source = sold;
	XPinit(w, 32);
	expand(yylval.cp, &w, DOGLOB | DOTILDE | DOMARKDIRS);
	XPput(w, NULL);
	words = (char **)XPclose(w);

	for (nwords = 0; words[nwords]; nwords++)
		;
	if (nwords == 1) {
		struct stat statb;

		/* Check if globbing failed (returned glob pattern),
		 * but be careful (E.g. toglob == "ab*" when the file
		 * "ab*" exists is not an error).
		 * Also, check for empty result - happens if we tried
		 * to glob something which evaluated to an empty
		 * string (e.g., "$FOO" when there is no FOO, etc).
		 */
		if ((strcmp(words[0], toglob) == 0 &&
		    stat(words[0], &statb) < 0) ||
		    words[0][0] == '\0') {
			x_free_words(nwords, words);
			words = NULL;
			nwords = 0;
		}
	}
	afree(toglob, ATEMP);

	if ((*wordsp = nwords ? words : NULL) == NULL && words != NULL)
		x_free_words(nwords, words);

	return (nwords);
}

/* Data structure used in x_command_glob() */
struct path_order_info {
	char *word;
	int base;
	int path_order;
};

/* Compare routine used in x_command_glob() */
static int
path_order_cmp(const void *aa, const void *bb)
{
	const struct path_order_info *a = (const struct path_order_info *)aa;
	const struct path_order_info *b = (const struct path_order_info *)bb;
	int t;

	t = strcmp(a->word + a->base, b->word + b->base);
	return (t ? t : a->path_order - b->path_order);
}

static int
x_command_glob(int flags, const char *str, int slen, char ***wordsp)
{
	char *toglob, *pat, *fpath;
	int nwords;
	XPtrV w;
	struct block *l;

	if (slen < 0)
		return (0);

	toglob = add_glob(str, slen);

	/* Convert "foo*" (toglob) to a pattern for future use */
	pat = evalstr(toglob, DOPAT | DOTILDE);
	afree(toglob, ATEMP);

	XPinit(w, 32);

	glob_table(pat, &w, &keywords);
	glob_table(pat, &w, &aliases);
	glob_table(pat, &w, &builtins);
	for (l = e->loc; l; l = l->next)
		glob_table(pat, &w, &l->funs);

	glob_path(flags, pat, &w, path);
	if ((fpath = str_val(global("FPATH"))) != null)
		glob_path(flags, pat, &w, fpath);

	nwords = XPsize(w);

	if (!nwords) {
		*wordsp = NULL;
		XPfree(w);
		return (0);
	}
	/* Sort entries */
	if (flags & XCF_FULLPATH) {
		/* Sort by basename, then path order */
		struct path_order_info *info, *last_info = NULL;
		char **words = (char **)XPptrv(w);
		int i, path_order = 0;

		info = (struct path_order_info *)
		    alloc(nwords * sizeof(struct path_order_info), ATEMP);
		for (i = 0; i < nwords; i++) {
			info[i].word = words[i];
			info[i].base = x_basename(words[i], NULL);
			if (!last_info || info[i].base != last_info->base ||
			    strncmp(words[i], last_info->word, info[i].base) != 0) {
				last_info = &info[i];
				path_order++;
			}
			info[i].path_order = path_order;
		}
		qsort(info, nwords, sizeof(struct path_order_info),
		    path_order_cmp);
		for (i = 0; i < nwords; i++)
			words[i] = info[i].word;
		afree(info, ATEMP);
	} else {
		/* Sort and remove duplicate entries */
		char **words = (char **)XPptrv(w);
		int i, j;

		qsort(words, nwords, sizeof(void *), xstrcmp);
		for (i = j = 0; i < nwords - 1; i++) {
			if (strcmp(words[i], words[i + 1]))
				words[j++] = words[i];
			else
				afree(words[i], ATEMP);
		}
		words[j++] = words[i];
		nwords = j;
		w.cur = (void **)&words[j];
	}

	XPput(w, NULL);
	*wordsp = (char **)XPclose(w);

	return (nwords);
}

#define IS_WORDC(c)	(!ctype(c, C_LEX1) && (c) != '\'' && (c) != '"' && \
			    (c) != '`' && (c) != '=' && (c) != ':')

static int
x_locate_word(const char *buf, int buflen, int pos, int *startp,
    bool *is_commandp)
{
	int start, end;

	/* Bad call? Probably should report error */
	if (pos < 0 || pos > buflen) {
		*startp = pos;
		*is_commandp = false;
		return (0);
	}
	/* The case where pos == buflen happens to take care of itself... */

	start = pos;
	/* Keep going backwards to start of word (has effect of allowing
	 * one blank after the end of a word)
	 */
	for (; (start > 0 && IS_WORDC(buf[start - 1])) ||
	    (start > 1 && buf[start - 2] == '\\'); start--)
		;
	/* Go forwards to end of word */
	for (end = start; end < buflen && IS_WORDC(buf[end]); end++) {
		if (buf[end] == '\\' && (end + 1) < buflen)
			end++;
	}

	if (is_commandp) {
		bool iscmd;
		int p = start - 1;

		/* Figure out if this is a command */
		while (p >= 0 && ksh_isspace(buf[p]))
			p--;
		iscmd = p < 0 || vstrchr(";|&()`", buf[p]);
		if (iscmd) {
			/* If command has a /, path, etc. is not searched;
			 * only current directory is searched which is just
			 * like file globbing.
			 */
			for (p = start; p < end; p++)
				if (buf[p] == '/')
					break;
			iscmd = p == end;
		}
		*is_commandp = iscmd;
	}
	*startp = start;

	return (end - start);
}

static int
x_cf_glob(int flags, const char *buf, int buflen, int pos, int *startp,
    int *endp, char ***wordsp, bool *is_commandp)
{
	int len, nwords;
	char **words = NULL;
	bool is_command;

	len = x_locate_word(buf, buflen, pos, startp, &is_command);
	if (!(flags & XCF_COMMAND))
		is_command = false;
	/* Don't do command globing on zero length strings - it takes too
	 * long and isn't very useful. File globs are more likely to be
	 * useful, so allow these.
	 */
	if (len == 0 && is_command)
		return (0);

	nwords = is_command ?
	    x_command_glob(flags, buf + *startp, len, &words) :
	    x_file_glob(flags, buf + *startp, len, &words);
	if (nwords == 0) {
		*wordsp = NULL;
		return (0);
	}
	if (is_commandp)
		*is_commandp = is_command;
	*wordsp = words;
	*endp = *startp + len;

	return (nwords);
}

/* Given a string, copy it and possibly add a '*' to the end.
 * The new string is returned.
 */
static char *
add_glob(const char *str, int slen)
{
	char *toglob, *s;
	bool saw_slash = false;

	if (slen < 0)
		return (NULL);

	/* for clang's static analyser, the nonnull attribute isn't enough */
	mkssert(str != NULL);

	strndupx(toglob, str, slen + 1, ATEMP); /* + 1 for "*" */
	toglob[slen] = '\0';

	/*
	 * If the pathname contains a wildcard (an unquoted '*',
	 * '?', or '[') or parameter expansion ('$'), or a ~username
	 * with no trailing slash, then it is globbed based on that
	 * value (i.e., without the appended '*').
	 */
	for (s = toglob; *s; s++) {
		if (*s == '\\' && s[1])
			s++;
		else if (*s == '*' || *s == '[' || *s == '?' || *s == '$' ||
		    (s[1] == '(' /*)*/ && /* *s in '*','?' already checked */
		    (*s == '+' || *s == '@' || *s == '!')))
			break;
		else if (*s == '/')
			saw_slash = true;
	}
	if (!*s && (*toglob != '~' || saw_slash)) {
		toglob[slen] = '*';
		toglob[slen + 1] = '\0';
	}
	return (toglob);
}

/*
 * Find longest common prefix
 */
static int
x_longest_prefix(int nwords, char * const * words)
{
	int i, j, prefix_len;
	char *p;

	if (nwords <= 0)
		return (0);

	prefix_len = strlen(words[0]);
	for (i = 1; i < nwords; i++)
		for (j = 0, p = words[i]; j < prefix_len; j++)
			if (p[j] != words[0][j]) {
				prefix_len = j;
				break;
			}
	return (prefix_len);
}

static void
x_free_words(int nwords, char **words)
{
	while (nwords)
		afree(words[--nwords], ATEMP);
	afree(words, ATEMP);
}

/* Return the offset of the basename of string s (which ends at se - need not
 * be null terminated). Trailing slashes are ignored. If s is just a slash,
 * then the offset is 0 (actually, length - 1).
 *	s		Return
 *	/etc		1
 *	/etc/		1
 *	/etc//		1
 *	/etc/fo		5
 *	foo		0
 *	///		2
 *			0
 */
static int
x_basename(const char *s, const char *se)
{
	const char *p;

	if (se == NULL)
		se = s + strlen(s);
	if (s == se)
		return (0);

	/* Skip trailing slashes */
	for (p = se - 1; p > s && *p == '/'; p--)
		;
	for (; p > s && *p != '/'; p--)
		;
	if (*p == '/' && p + 1 < se)
		p++;

	return (p - s);
}

/*
 * Apply pattern matching to a table: all table entries that match a pattern
 * are added to wp.
 */
static void
glob_table(const char *pat, XPtrV *wp, struct table *tp)
{
	struct tstate ts;
	struct tbl *te;

	ktwalk(&ts, tp);
	while ((te = ktnext(&ts)))
		if (gmatchx(te->name, pat, false)) {
			char *cp;

			strdupx(cp, te->name, ATEMP);
			XPput(*wp, cp);
		}
}

static void
glob_path(int flags, const char *pat, XPtrV *wp, const char *lpath)
{
	const char *sp, *p;
	char *xp, **words;
	int staterr, pathlen, patlen, oldsize, newsize, i, j;
	XString xs;

	patlen = strlen(pat) + 1;
	sp = lpath;
	Xinit(xs, xp, patlen + 128, ATEMP);
	while (sp) {
		xp = Xstring(xs, xp);
		if (!(p = cstrchr(sp, ':')))
			p = sp + strlen(sp);
		pathlen = p - sp;
		if (pathlen) {
			/* Copy sp into xp, stuffing any MAGIC characters
			 * on the way
			 */
			const char *s = sp;

			XcheckN(xs, xp, pathlen * 2);
			while (s < p) {
				if (ISMAGIC(*s))
					*xp++ = MAGIC;
				*xp++ = *s++;
			}
			*xp++ = '/';
			pathlen++;
		}
		sp = p;
		XcheckN(xs, xp, patlen);
		memcpy(xp, pat, patlen);

		oldsize = XPsize(*wp);
		glob_str(Xstring(xs, xp), wp, 1); /* mark dirs */
		newsize = XPsize(*wp);

		/* Check that each match is executable... */
		words = (char **)XPptrv(*wp);
		for (i = j = oldsize; i < newsize; i++) {
			staterr = 0;
			if ((search_access(words[i], X_OK, &staterr) >= 0) ||
			    (staterr == EISDIR)) {
				words[j] = words[i];
				if (!(flags & XCF_FULLPATH))
					memmove(words[j], words[j] + pathlen,
					    strlen(words[j] + pathlen) + 1);
				j++;
			} else
				afree(words[i], ATEMP);
		}
		wp->cur = (void **)&words[j];

		if (!*sp++)
			break;
	}
	Xfree(xs, xp);
}

/*
 * if argument string contains any special characters, they will
 * be escaped and the result will be put into edit buffer by
 * keybinding-specific function
 */
static int
x_escape(const char *s, size_t len, int (*putbuf_func)(const char *, size_t))
{
	size_t add = 0, wlen = len;
	const char *ifs = str_val(local("IFS", 0));
	int rval = 0;

	while (wlen - add > 0)
		if (vstrchr("\"#$&'()*:;<=>?[\\`{|}", s[add]) ||
		    vstrchr(ifs, s[add])) {
			if (putbuf_func(s, add) != 0) {
				rval = -1;
				break;
			}
			putbuf_func(s[add] == '\n' ? "'" : "\\", 1);
			putbuf_func(&s[add], 1);
			if (s[add] == '\n')
				putbuf_func("'", 1);

			add++;
			wlen -= add;
			s += add;
			add = 0;
		} else
			++add;
	if (wlen > 0 && rval == 0)
		rval = putbuf_func(s, wlen);

	return (rval);
}


/* +++ emacs editing mode +++ */

static	Area	aedit;
#define	AEDIT	&aedit		/* area for kill ring and macro defns */

/* values returned by keyboard functions */
#define	KSTD	0
#define	KEOL	1		/* ^M, ^J */
#define	KINTR	2		/* ^G, ^C */

struct x_ftab {
	int (*xf_func)(int c);
	const char *xf_name;
	short xf_flags;
};

struct x_defbindings {
	unsigned char xdb_func;	/* XFUNC_* */
	unsigned char xdb_tab;
	unsigned char xdb_char;
};

#define XF_ARG		1	/* command takes number prefix */
#define	XF_NOBIND	2	/* not allowed to bind to function */
#define	XF_PREFIX	4	/* function sets prefix */

/* Separator for completion */
#define	is_cfs(c)	((c) == ' ' || (c) == '\t' || (c) == '"' || (c) == '\'')
/* Separator for motion */
#define	is_mfs(c)	(!(ksh_isalnux(c) || (c) == '$' || ((c) & 0x80)))

#define X_NTABS		3			/* normal, meta1, meta2 */
#define X_TABSZ		256			/* size of keydef tables etc */

/* Arguments for do_complete()
 * 0 = enumerate	M-=	complete as much as possible and then list
 * 1 = complete		M-Esc
 * 2 = list		M-?
 */
typedef enum {
	CT_LIST,	/* list the possible completions */
	CT_COMPLETE,	/* complete to longest prefix */
	CT_COMPLIST	/* complete and then list (if non-exact) */
} Comp_type;

/*
 * The following are used for my horizontal scrolling stuff
 */
static char *xbuf;		/* beg input buffer */
static char *xend;		/* end input buffer */
static char *xcp;		/* current position */
static char *xep;		/* current end */
static char *xbp;		/* start of visible portion of input buffer */
static char *xlp;		/* last char visible on screen */
static int x_adj_ok;
/*
 * we use x_adj_done so that functions can tell
 * whether x_adjust() has been called while they are active.
 */
static int x_adj_done;

static int x_col;
static int x_displen;
static int x_arg;		/* general purpose arg */
static int x_arg_defaulted;	/* x_arg not explicitly set; defaulted to 1 */

static int xlp_valid;

static char **x_histp;		/* history position */
static int x_nextcmd;		/* for newline-and-next */
static char *xmp;		/* mark pointer */
static unsigned char x_last_command;
static unsigned char (*x_tab)[X_TABSZ];	/* key definition */
#ifndef MKSH_SMALL
static char *(*x_atab)[X_TABSZ];	/* macro definitions */
#endif
static unsigned char x_bound[(X_TABSZ * X_NTABS + 7) / 8];
#define KILLSIZE	20
static char *killstack[KILLSIZE];
static int killsp, killtp;
static int x_curprefix;
#ifndef MKSH_SMALL
static char *macroptr = NULL;	/* bind key macro active? */
#endif
#if !MKSH_S_NOVI
static int cur_col;		/* current column on line */
static int pwidth;		/* width of prompt */
static int prompt_trunc;	/* how much of prompt to truncate */
static int winwidth;		/* width of window */
static char *wbuf[2];		/* window buffers */
static int wbuf_len;		/* length of window buffers (x_cols - 3) */
static int win;			/* window buffer in use */
static char morec;		/* more character at right of window */
static int lastref;		/* argument to last refresh() */
static int holdlen;		/* length of holdbuf */
#endif
static int prompt_redraw;	/* 0 if newline forced after prompt */

static int x_ins(const char *);
static void x_delete(int, int);
static int x_bword(void);
static int x_fword(int);
static void x_goto(char *);
static void x_bs3(char **);
static int x_size_str(char *);
static int x_size2(char *, char **);
static void x_zots(char *);
static void x_zotc2(int);
static void x_zotc3(char **);
static void x_load_hist(char **);
static int x_search(char *, int, int);
#ifndef MKSH_SMALL
static int x_search_dir(int);
#endif
static int x_match(char *, char *);
static void x_redraw(int);
static void x_push(int);
static char *x_mapin(const char *, Area *)
    MKSH_A_NONNULL((nonnull (1)));
static char *x_mapout(int);
static void x_mapout2(int, char **);
static void x_print(int, int);
static void x_adjust(void);
static void x_e_ungetc(int);
static int x_e_getc(void);
static void x_e_putc2(int);
static void x_e_putc3(const char **);
static void x_e_puts(const char *);
#ifndef MKSH_SMALL
static int x_fold_case(int);
#endif
static char *x_lastcp(void);
static void do_complete(int, Comp_type);

static int unget_char = -1;

static int x_do_ins(const char *, size_t);
static void bind_if_not_bound(int, int, int);

enum emacs_funcs {
#define EMACSFN_ENUMS
#include "emacsfn.h"
	XFUNC_MAX
};

#define EMACSFN_DEFNS
#include "emacsfn.h"

static const struct x_ftab x_ftab[] = {
#define EMACSFN_ITEMS
#include "emacsfn.h"
	{ 0, NULL, 0 }
};

static struct x_defbindings const x_defbindings[] = {
	{ XFUNC_del_back,		0, CTRL('?')	},
	{ XFUNC_del_bword,		1, CTRL('?')	},
	{ XFUNC_eot_del,		0, CTRL('D')	},
	{ XFUNC_del_back,		0, CTRL('H')	},
	{ XFUNC_del_bword,		1, CTRL('H')	},
	{ XFUNC_del_bword,		1,	'h'	},
	{ XFUNC_mv_bword,		1,	'b'	},
	{ XFUNC_mv_fword,		1,	'f'	},
	{ XFUNC_del_fword,		1,	'd'	},
	{ XFUNC_mv_back,		0, CTRL('B')	},
	{ XFUNC_mv_forw,		0, CTRL('F')	},
	{ XFUNC_search_char_forw,	0, CTRL(']')	},
	{ XFUNC_search_char_back,	1, CTRL(']')	},
	{ XFUNC_newline,		0, CTRL('M')	},
	{ XFUNC_newline,		0, CTRL('J')	},
	{ XFUNC_end_of_text,		0, CTRL('_')	},
	{ XFUNC_abort,			0, CTRL('G')	},
	{ XFUNC_prev_com,		0, CTRL('P')	},
	{ XFUNC_next_com,		0, CTRL('N')	},
	{ XFUNC_nl_next_com,		0, CTRL('O')	},
	{ XFUNC_search_hist,		0, CTRL('R')	},
	{ XFUNC_beg_hist,		1,	'<'	},
	{ XFUNC_end_hist,		1,	'>'	},
	{ XFUNC_goto_hist,		1,	'g'	},
	{ XFUNC_mv_end,			0, CTRL('E')	},
	{ XFUNC_mv_begin,		0, CTRL('A')	},
	{ XFUNC_draw_line,		0, CTRL('L')	},
	{ XFUNC_cls,			1, CTRL('L')	},
	{ XFUNC_meta1,			0, CTRL('[')	},
	{ XFUNC_meta2,			0, CTRL('X')	},
	{ XFUNC_kill,			0, CTRL('K')	},
	{ XFUNC_yank,			0, CTRL('Y')	},
	{ XFUNC_meta_yank,		1,	'y'	},
	{ XFUNC_literal,		0, CTRL('^')	},
	{ XFUNC_comment,		1,	'#'	},
	{ XFUNC_transpose,		0, CTRL('T')	},
	{ XFUNC_complete,		1, CTRL('[')	},
	{ XFUNC_comp_list,		0, CTRL('I')	},
	{ XFUNC_comp_list,		1,	'='	},
	{ XFUNC_enumerate,		1,	'?'	},
	{ XFUNC_expand,			1,	'*'	},
	{ XFUNC_comp_file,		1, CTRL('X')	},
	{ XFUNC_comp_comm,		2, CTRL('[')	},
	{ XFUNC_list_comm,		2,	'?'	},
	{ XFUNC_list_file,		2, CTRL('Y')	},
	{ XFUNC_set_mark,		1,	' '	},
	{ XFUNC_kill_region,		0, CTRL('W')	},
	{ XFUNC_xchg_point_mark,	2, CTRL('X')	},
	{ XFUNC_literal,		0, CTRL('V')	},
	{ XFUNC_version,		1, CTRL('V')	},
	{ XFUNC_prev_histword,		1,	'.'	},
	{ XFUNC_prev_histword,		1,	'_'	},
	{ XFUNC_set_arg,		1,	'0'	},
	{ XFUNC_set_arg,		1,	'1'	},
	{ XFUNC_set_arg,		1,	'2'	},
	{ XFUNC_set_arg,		1,	'3'	},
	{ XFUNC_set_arg,		1,	'4'	},
	{ XFUNC_set_arg,		1,	'5'	},
	{ XFUNC_set_arg,		1,	'6'	},
	{ XFUNC_set_arg,		1,	'7'	},
	{ XFUNC_set_arg,		1,	'8'	},
	{ XFUNC_set_arg,		1,	'9'	},
#ifndef MKSH_SMALL
	{ XFUNC_fold_upper,		1,	'U'	},
	{ XFUNC_fold_upper,		1,	'u'	},
	{ XFUNC_fold_lower,		1,	'L'	},
	{ XFUNC_fold_lower,		1,	'l'	},
	{ XFUNC_fold_capitalise,	1,	'C'	},
	{ XFUNC_fold_capitalise,	1,	'c'	},
#endif
	/* These for ansi arrow keys: arguablely shouldn't be here by
	 * default, but its simpler/faster/smaller than using termcap
	 * entries.
	 */
	{ XFUNC_meta2,			1,	'['	},
	{ XFUNC_meta2,			1,	'O'	},
	{ XFUNC_prev_com,		2,	'A'	},
	{ XFUNC_next_com,		2,	'B'	},
	{ XFUNC_mv_forw,		2,	'C'	},
	{ XFUNC_mv_back,		2,	'D'	},
#ifndef MKSH_SMALL
	{ XFUNC_vt_hack,		2,	'1'	},
	{ XFUNC_mv_begin | 0x80,	2,	'7'	},
	{ XFUNC_mv_begin,		2,	'H'	},
	{ XFUNC_mv_end | 0x80,		2,	'4'	},
	{ XFUNC_mv_end | 0x80,		2,	'8'	},
	{ XFUNC_mv_end,			2,	'F'	},
	{ XFUNC_del_char | 0x80,	2,	'3'	},
	{ XFUNC_search_hist_up | 0x80,	2,	'5'	},
	{ XFUNC_search_hist_dn | 0x80,	2,	'6'	},
	/* more non-standard ones */
	{ XFUNC_edit_line,		2,	'e'	}
#endif
};

#ifdef MKSH_SMALL
static void x_modified(void);
static void
x_modified(void)
{
	if (!modified) {
		x_histp = histptr + 1;
		modified = 1;
	}
}
#define XFUNC_VALUE(f) (f)
#else
#define x_modified() do {			\
	if (!modified) {			\
		x_histp = histptr + 1;		\
		modified = 1;			\
	}					\
} while (/* CONSTCOND */ 0)
#define XFUNC_VALUE(f) (f & 0x7F)
#endif

static int
x_e_getmbc(char *sbuf)
{
	int c, pos = 0;
	unsigned char *buf = (unsigned char *)sbuf;

	memset(buf, 0, 4);
	buf[pos++] = c = x_e_getc();
	if (c == -1)
		return (-1);
	if (UTFMODE) {
		if ((buf[0] >= 0xC2) && (buf[0] < 0xF0)) {
			c = x_e_getc();
			if (c == -1)
				return (-1);
			if ((c & 0xC0) != 0x80) {
				x_e_ungetc(c);
				return (1);
			}
			buf[pos++] = c;
		}
		if ((buf[0] >= 0xE0) && (buf[0] < 0xF0)) {
			/* XXX x_e_ungetc is one-octet only */
			buf[pos++] = c = x_e_getc();
			if (c == -1)
				return (-1);
		}
	}
	return (pos);
}

static void
x_init_prompt(void)
{
	x_col = promptlen(prompt);
	x_adj_ok = 1;
	prompt_redraw = 1;
	if (x_col >= xx_cols)
		x_col %= xx_cols;
	x_displen = xx_cols - 2 - x_col;
	x_adj_done = 0;

	pprompt(prompt, 0);
	if (x_displen < 1) {
		x_col = 0;
		x_displen = xx_cols - 2;
		x_e_putc2('\n');
		prompt_redraw = 0;
	}
}

static int
x_emacs(char *buf, size_t len)
{
	int c, i;
	unsigned char f;

	xbp = xbuf = buf; xend = buf + len;
	xlp = xcp = xep = buf;
	*xcp = 0;
	xlp_valid = true;
	xmp = NULL;
	x_curprefix = 0;
	x_histp = histptr + 1;
	x_last_command = XFUNC_error;

	xx_cols = x_cols;
	x_init_prompt();

	if (x_nextcmd >= 0) {
		int off = source->line - x_nextcmd;
		if (histptr - history >= off)
			x_load_hist(histptr - off);
		x_nextcmd = -1;
	}
	editmode = 1;
	while (1) {
		x_flush();
		if ((c = x_e_getc()) < 0)
			return (0);

		f = x_curprefix == -1 ? XFUNC_insert :
		    x_tab[x_curprefix][c];
#ifndef MKSH_SMALL
		if (f & 0x80) {
			f &= 0x7F;
			if ((i = x_e_getc()) != '~')
				x_e_ungetc(i);
		}

		/* avoid bind key macro recursion */
		if (macroptr && f == XFUNC_ins_string)
			f = XFUNC_insert;
#endif

		if (!(x_ftab[f].xf_flags & XF_PREFIX) &&
		    x_last_command != XFUNC_set_arg) {
			x_arg = 1;
			x_arg_defaulted = 1;
		}
		i = c | (x_curprefix << 8);
		x_curprefix = 0;
		switch ((*x_ftab[f].xf_func)(i)) {
		case KSTD:
			if (!(x_ftab[f].xf_flags & XF_PREFIX))
				x_last_command = f;
			break;
		case KEOL:
			i = xep - xbuf;
			return (i);
		case KINTR:	/* special case for interrupt */
			trapsig(SIGINT);
			x_mode(false);
			unwind(LSHELL);
		}
		/* ad-hoc hack for fixing the cursor position */
		x_goto(xcp);
	}
}

static int
x_insert(int c)
{
	static int left = 0, pos, save_arg;
	static char str[4];

	/*
	 * Should allow tab and control chars.
	 */
	if (c == 0) {
 invmbs:
		left = 0;
		x_e_putc2(7);
		return (KSTD);
	}
	if (UTFMODE) {
		if (((c & 0xC0) == 0x80) && left) {
			str[pos++] = c;
			if (!--left) {
				str[pos] = '\0';
				x_arg = save_arg;
				while (x_arg--)
					x_ins(str);
			}
			return (KSTD);
		}
		if (left) {
			if (x_curprefix == -1) {
				/* flush invalid multibyte */
				str[pos] = '\0';
				while (save_arg--)
					x_ins(str);
			}
		}
		if ((c >= 0xC2) && (c < 0xE0))
			left = 1;
		else if ((c >= 0xE0) && (c < 0xF0))
			left = 2;
		else if (c > 0x7F)
			goto invmbs;
		else
			left = 0;
		if (left) {
			save_arg = x_arg;
			pos = 1;
			str[0] = c;
			return (KSTD);
		}
	}
	left = 0;
	str[0] = c;
	str[1] = '\0';
	while (x_arg--)
		x_ins(str);
	return (KSTD);
}

#ifndef MKSH_SMALL
static int
x_ins_string(int c)
{
	macroptr = x_atab[c >> 8][c & 255];
	/*
	 * we no longer need to bother checking if macroptr is
	 * not NULL but first char is NUL; x_e_getc() does it
	 */
	return (KSTD);
}
#endif

static int
x_do_ins(const char *cp, size_t len)
{
	if (xep + len >= xend) {
		x_e_putc2(7);
		return (-1);
	}
	memmove(xcp + len, xcp, xep - xcp + 1);
	memmove(xcp, cp, len);
	xcp += len;
	xep += len;
	x_modified();
	return (0);
}

static int
x_ins(const char *s)
{
	char *cp = xcp;
	int adj = x_adj_done;

	if (x_do_ins(s, strlen(s)) < 0)
		return (-1);
	/*
	 * x_zots() may result in a call to x_adjust()
	 * we want xcp to reflect the new position.
	 */
	xlp_valid = false;
	x_lastcp();
	x_adj_ok = (xcp >= xlp);
	x_zots(cp);
	if (adj == x_adj_done) {	/* has x_adjust() been called? */
		/* no */
		cp = xlp;
		while (cp > xcp)
			x_bs3(&cp);
	}
	if (xlp == xep - 1)
		x_redraw(xx_cols);
	x_adj_ok = 1;
	return (0);
}

static int
x_del_back(int c MKSH_A_UNUSED)
{
	int i = 0;

	if (xcp == xbuf) {
		x_e_putc2(7);
		return (KSTD);
	}
	do {
		x_goto(xcp - 1);
	} while ((++i < x_arg) && (xcp != xbuf));
	x_delete(i, false);
	return (KSTD);
}

static int
x_del_char(int c MKSH_A_UNUSED)
{
	char *cp, *cp2;
	int i = 0;

	cp = xcp;
	while (i < x_arg) {
		utf_ptradjx(cp, cp2);
		if (cp2 > xep)
			break;
		cp = cp2;
		i++;
	}

	if (!i) {
		x_e_putc2(7);
		return (KSTD);
	}
	x_delete(i, false);
	return (KSTD);
}

/* Delete nc chars to the right of the cursor (including cursor position) */
static void
x_delete(int nc, int push)
{
	int i, nb, nw;
	char *cp;

	if (nc == 0)
		return;

	nw = 0;
	cp = xcp;
	for (i = 0; i < nc; ++i) {
		char *cp2;
		int j;

		j = x_size2(cp, &cp2);
		if (cp2 > xep)
			break;
		cp = cp2;
		nw += j;
	}
	nb = cp - xcp;
	/* nc = i; */

	if (xmp != NULL && xmp > xcp) {
		if (xcp + nb > xmp)
			xmp = xcp;
		else
			xmp -= nb;
	}
	/*
	 * This lets us yank a word we have deleted.
	 */
	if (push)
		x_push(nb);

	xep -= nb;
	memmove(xcp, xcp + nb, xep - xcp + 1);	/* Copies the NUL */
	x_adj_ok = 0;			/* don't redraw */
	xlp_valid = false;
	x_zots(xcp);
	/*
	 * if we are already filling the line,
	 * there is no need to ' ','\b'.
	 * But if we must, make sure we do the minimum.
	 */
	if ((i = xx_cols - 2 - x_col) > 0 || xep - xlp == 0) {
		nw = i = (nw < i) ? nw : i;
		while (i--)
			x_e_putc2(' ');
		if (x_col == xx_cols - 2) {
			x_e_putc2((xep > xlp) ? '>' : (xbp > xbuf) ? '<' : ' ');
			++nw;
		}
		while (nw--)
			x_e_putc2('\b');
	}
	/*x_goto(xcp);*/
	x_adj_ok = 1;
	xlp_valid = false;
	cp = x_lastcp();
	while (cp > xcp)
		x_bs3(&cp);

	x_modified();
	return;
}

static int
x_del_bword(int c MKSH_A_UNUSED)
{
	x_delete(x_bword(), true);
	return (KSTD);
}

static int
x_mv_bword(int c MKSH_A_UNUSED)
{
	x_bword();
	return (KSTD);
}

static int
x_mv_fword(int c MKSH_A_UNUSED)
{
	x_fword(1);
	return (KSTD);
}

static int
x_del_fword(int c MKSH_A_UNUSED)
{
	x_delete(x_fword(0), true);
	return (KSTD);
}

static int
x_bword(void)
{
	int nc = 0, nb = 0;
	char *cp = xcp;

	if (cp == xbuf) {
		x_e_putc2(7);
		return (0);
	}
	while (x_arg--) {
		while (cp != xbuf && is_mfs(cp[-1])) {
			cp--;
			nb++;
		}
		while (cp != xbuf && !is_mfs(cp[-1])) {
			cp--;
			nb++;
		}
	}
	x_goto(cp);
	for (cp = xcp; cp < (xcp + nb); ++nc)
		cp += utf_ptradj(cp);
	return (nc);
}

static int
x_fword(int move)
{
	int nc = 0;
	char *cp = xcp, *cp2;

	if (cp == xep) {
		x_e_putc2(7);
		return (0);
	}
	while (x_arg--) {
		while (cp != xep && is_mfs(*cp))
			cp++;
		while (cp != xep && !is_mfs(*cp))
			cp++;
	}
	for (cp2 = xcp; cp2 < cp; ++nc)
		cp2 += utf_ptradj(cp2);
	if (move)
		x_goto(cp);
	return (nc);
}

static void
x_goto(char *cp)
{
	if (UTFMODE)
		while ((cp > xbuf) && ((*cp & 0xC0) == 0x80))
			--cp;
	if (cp < xbp || cp >= utf_skipcols(xbp, x_displen)) {
		/* we are heading off screen */
		xcp = cp;
		x_adjust();
	} else if (cp < xcp) {		/* move back */
		while (cp < xcp)
			x_bs3(&xcp);
	} else if (cp > xcp) {		/* move forward */
		while (cp > xcp)
			x_zotc3(&xcp);
	}
}

static void
x_bs3(char **p)
{
	int i;

	(*p)--;
	if (UTFMODE)
		while (((unsigned char)**p & 0xC0) == 0x80)
			(*p)--;

	i = x_size2(*p, NULL);
	while (i--)
		x_e_putc2('\b');
}

static int
x_size_str(char *cp)
{
	int size = 0;
	while (*cp)
		size += x_size2(cp, &cp);
	return (size);
}

static int
x_size2(char *cp, char **dcp)
{
	int c = *(unsigned char *)cp;

	if (UTFMODE && (c > 0x7F))
		return (utf_widthadj(cp, (const char **)dcp));
	if (dcp)
		*dcp = cp + 1;
	if (c == '\t')
		return (4);	/* Kludge, tabs are always four spaces. */
	if (c < ' ' || c == 0x7f)
		return (2);	/* control unsigned char */
	return (1);
}

static void
x_zots(char *str)
{
	int adj = x_adj_done;

	x_lastcp();
	while (*str && str < xlp && adj == x_adj_done)
		x_zotc3(&str);
}

static void
x_zotc2(int c)
{
	if (c == '\t') {
		/* Kludge, tabs are always four spaces. */
		x_e_puts("    ");
	} else if (c < ' ' || c == 0x7f) {
		x_e_putc2('^');
		x_e_putc2(UNCTRL(c));
	} else
		x_e_putc2(c);
}

static void
x_zotc3(char **cp)
{
	unsigned char c = **(unsigned char **)cp;

	if (c == '\t') {
		/* Kludge, tabs are always four spaces. */
		x_e_puts("    ");
		(*cp)++;
	} else if (c < ' ' || c == 0x7f) {
		x_e_putc2('^');
		x_e_putc2(UNCTRL(c));
		(*cp)++;
	} else
		x_e_putc3((const char **)cp);
}

static int
x_mv_back(int c MKSH_A_UNUSED)
{
	if (xcp == xbuf) {
		x_e_putc2(7);
		return (KSTD);
	}
	while (x_arg--) {
		x_goto(xcp - 1);
		if (xcp == xbuf)
			break;
	}
	return (KSTD);
}

static int
x_mv_forw(int c MKSH_A_UNUSED)
{
	char *cp = xcp, *cp2;

	if (xcp == xep) {
		x_e_putc2(7);
		return (KSTD);
	}
	while (x_arg--) {
		utf_ptradjx(cp, cp2);
		if (cp2 > xep)
			break;
		cp = cp2;
	}
	x_goto(cp);
	return (KSTD);
}

static int
x_search_char_forw(int c MKSH_A_UNUSED)
{
	char *cp = xcp;
	char tmp[4];

	*xep = '\0';
	if (x_e_getmbc(tmp) < 0) {
		x_e_putc2(7);
		return (KSTD);
	}
	while (x_arg--) {
		if ((cp = (cp == xep) ? NULL : strstr(cp + 1, tmp)) == NULL &&
		    (cp = strstr(xbuf, tmp)) == NULL) {
			x_e_putc2(7);
			return (KSTD);
		}
	}
	x_goto(cp);
	return (KSTD);
}

static int
x_search_char_back(int c MKSH_A_UNUSED)
{
	char *cp = xcp, *p, tmp[4];
	bool b;

	if (x_e_getmbc(tmp) < 0) {
		x_e_putc2(7);
		return (KSTD);
	}
	for (; x_arg--; cp = p)
		for (p = cp; ; ) {
			if (p-- == xbuf)
				p = xep;
			if (p == cp) {
				x_e_putc2(7);
				return (KSTD);
			}
			if ((tmp[1] && ((p+1) > xep)) ||
			    (tmp[2] && ((p+2) > xep)))
				continue;
			b = true;
			if (*p != tmp[0])
				b = false;
			if (b && tmp[1] && p[1] != tmp[1])
				b = false;
			if (b && tmp[2] && p[2] != tmp[2])
				b = false;
			if (b)
				break;
		}
	x_goto(cp);
	return (KSTD);
}

static int
x_newline(int c MKSH_A_UNUSED)
{
	x_e_putc2('\r');
	x_e_putc2('\n');
	x_flush();
	*xep++ = '\n';
	return (KEOL);
}

static int
x_end_of_text(int c MKSH_A_UNUSED)
{
	x_zotc2(edchars.eof);
	x_putc('\r');
	x_putc('\n');
	x_flush();
	return (KEOL);
}

static int
x_beg_hist(int c MKSH_A_UNUSED)
{
	x_load_hist(history);
	return (KSTD);
}

static int
x_end_hist(int c MKSH_A_UNUSED)
{
	x_load_hist(histptr);
	return (KSTD);
}

static int
x_prev_com(int c MKSH_A_UNUSED)
{
	x_load_hist(x_histp - x_arg);
	return (KSTD);
}

static int
x_next_com(int c MKSH_A_UNUSED)
{
	x_load_hist(x_histp + x_arg);
	return (KSTD);
}

/* Goto a particular history number obtained from argument.
 * If no argument is given history 1 is probably not what you
 * want so we'll simply go to the oldest one.
 */
static int
x_goto_hist(int c MKSH_A_UNUSED)
{
	if (x_arg_defaulted)
		x_load_hist(history);
	else
		x_load_hist(histptr + x_arg - source->line);
	return (KSTD);
}

static void
x_load_hist(char **hp)
{
	int oldsize;
	char *sp = NULL;

	if (hp == histptr + 1) {
		sp = holdbuf;
		modified = 0;
	} else if (hp < history || hp > histptr) {
		x_e_putc2(7);
		return;
	}
	if (sp == NULL)
		sp = *hp;
	x_histp = hp;
	oldsize = x_size_str(xbuf);
	if (modified)
		strlcpy(holdbuf, xbuf, sizeof(holdbuf));
	strlcpy(xbuf, sp, xend - xbuf);
	xbp = xbuf;
	xep = xcp = xbuf + strlen(xbuf);
	xlp_valid = false;
	if (xep <= x_lastcp()) {
		x_redraw(oldsize);
	}
	x_goto(xep);
	modified = 0;
}

static int
x_nl_next_com(int c MKSH_A_UNUSED)
{
	x_nextcmd = source->line - (histptr - x_histp) + 1;
	return (x_newline('\n'));
}

static int
x_eot_del(int c)
{
	if (xep == xbuf && x_arg_defaulted)
		return (x_end_of_text(c));
	else
		return (x_del_char(c));
}

/* reverse incremental history search */
static int
x_search_hist(int c)
{
	int offset = -1;	/* offset of match in xbuf, else -1 */
	char pat[256 + 1];	/* pattern buffer */
	char *p = pat;
	unsigned char f;

	*p = '\0';
	while (1) {
		if (offset < 0) {
			x_e_puts("\nI-search: ");
			x_e_puts(pat);
		}
		x_flush();
		if ((c = x_e_getc()) < 0)
			return (KSTD);
		f = x_tab[0][c];
		if (c == CTRL('[')) {
			if ((f & 0x7F) == XFUNC_meta1) {
				if ((c = x_e_getc()) < 0)
					return (KSTD);
				f = x_tab[1][c] & 0x7F;
				if (f == XFUNC_meta1 || f == XFUNC_meta2)
					x_meta1(CTRL('['));
				x_e_ungetc(c);
			}
			break;
		}
#ifndef MKSH_SMALL
		if (f & 0x80) {
			f &= 0x7F;
			if ((c = x_e_getc()) != '~')
				x_e_ungetc(c);
		}
#endif
		if (f == XFUNC_search_hist)
			offset = x_search(pat, 0, offset);
		else if (f == XFUNC_del_back) {
			if (p == pat) {
				offset = -1;
				break;
			}
			if (p > pat)
				*--p = '\0';
			if (p == pat)
				offset = -1;
			else
				offset = x_search(pat, 1, offset);
			continue;
		} else if (f == XFUNC_insert) {
			/* add char to pattern */
			/* overflow check... */
			if (p >= &pat[sizeof(pat) - 1]) {
				x_e_putc2(7);
				continue;
			}
			*p++ = c, *p = '\0';
			if (offset >= 0) {
				/* already have partial match */
				offset = x_match(xbuf, pat);
				if (offset >= 0) {
					x_goto(xbuf + offset + (p - pat) -
					    (*pat == '^'));
					continue;
				}
			}
			offset = x_search(pat, 0, offset);
		} else if (f == XFUNC_abort) {
			if (offset >= 0)
				x_load_hist(histptr + 1);
			break;
		} else { /* other command */
			x_e_ungetc(c);
			break;
		}
	}
	if (offset < 0)
		x_redraw(-1);
	return (KSTD);
}

/* search backward from current line */
static int
x_search(char *pat, int sameline, int offset)
{
	char **hp;
	int i;

	for (hp = x_histp - (sameline ? 0 : 1); hp >= history; --hp) {
		i = x_match(*hp, pat);
		if (i >= 0) {
			if (offset < 0)
				x_e_putc2('\n');
			x_load_hist(hp);
			x_goto(xbuf + i + strlen(pat) - (*pat == '^'));
			return (i);
		}
	}
	x_e_putc2(7);
	x_histp = histptr;
	return (-1);
}

#ifndef MKSH_SMALL
/* anchored search up from current line */
static int
x_search_hist_up(int c MKSH_A_UNUSED)
{
	return (x_search_dir(-1));
}

/* anchored search down from current line */
static int
x_search_hist_dn(int c MKSH_A_UNUSED)
{
	return (x_search_dir(1));
}

/* anchored search in the indicated direction */
static int
x_search_dir(int search_dir /* should've been bool */)
{
	char **hp = x_histp + search_dir;
	size_t curs = xcp - xbuf;

	while (histptr >= hp && hp >= history) {
		if (strncmp(xbuf, *hp, curs) == 0) {
			x_load_hist(hp);
			x_goto(xbuf + curs);
			break;
		}
		hp += search_dir;
	}
	return (KSTD);
}
#endif

/* return position of first match of pattern in string, else -1 */
static int
x_match(char *str, char *pat)
{
	if (*pat == '^') {
		return ((strncmp(str, pat + 1, strlen(pat + 1)) == 0) ? 0 : -1);
	} else {
		char *q = strstr(str, pat);
		return ((q == NULL) ? -1 : q - str);
	}
}

static int
x_del_line(int c MKSH_A_UNUSED)
{
	int i, j;

	*xep = 0;
	i = xep - xbuf;
	j = x_size_str(xbuf);
	xcp = xbuf;
	x_push(i);
	xlp = xbp = xep = xbuf;
	xlp_valid = true;
	*xcp = 0;
	xmp = NULL;
	x_redraw(j);
	x_modified();
	return (KSTD);
}

static int
x_mv_end(int c MKSH_A_UNUSED)
{
	x_goto(xep);
	return (KSTD);
}

static int
x_mv_begin(int c MKSH_A_UNUSED)
{
	x_goto(xbuf);
	return (KSTD);
}

static int
x_draw_line(int c MKSH_A_UNUSED)
{
	x_redraw(-1);
	return (KSTD);
}

static int
x_e_rebuildline(const char *clrstr)
{
	shf_puts(clrstr, shl_out);
	x_adjust();
	return (KSTD);
}

static int
x_cls(int c MKSH_A_UNUSED)
{
	return (x_e_rebuildline(MKSH_CLS_STRING));
}

/* Redraw (part of) the line. If limit is < 0, the everything is redrawn
 * on a NEW line, otherwise limit is the screen column up to which needs
 * redrawing.
 */
static void
x_redraw(int limit)
{
	int i, j, x_trunc = 0;
	char *cp;

	x_adj_ok = 0;
	if (limit == -1)
		x_e_putc2('\n');
	else
		x_e_putc2('\r');
	x_flush();
	if (xbp == xbuf) {
		x_col = promptlen(prompt);
		if (x_col >= xx_cols)
			x_trunc = (x_col / xx_cols) * xx_cols;
		if (prompt_redraw)
			pprompt(prompt, x_trunc);
	}
	if (x_col >= xx_cols)
		x_col %= xx_cols;
	x_displen = xx_cols - 2 - x_col;
	if (x_displen < 1) {
		x_col = 0;
		x_displen = xx_cols - 2;
	}
	xlp_valid = false;
	x_lastcp();
	x_zots(xbp);
	if (xbp != xbuf || xep > xlp)
		limit = xx_cols;
	if (limit >= 0) {
		if (xep > xlp)
			i = 0;			/* we fill the line */
		else {
			char *cpl = xbp;

			i = limit;
			while (cpl < xlp)
				i -= x_size2(cpl, &cpl);
		}

		j = 0;
		while ((j < i) || (x_col < (xx_cols - 2))) {
			if (!(x_col < (xx_cols - 2)))
				break;
			x_e_putc2(' ');
			j++;
		}
		i = ' ';
		if (xep > xlp) {		/* more off screen */
			if (xbp > xbuf)
				i = '*';
			else
				i = '>';
		} else if (xbp > xbuf)
			i = '<';
		x_e_putc2(i);
		j++;
		while (j--)
			x_e_putc2('\b');
	}
	cp = xlp;
	while (cp > xcp)
		x_bs3(&cp);
	x_adj_ok = 1;
	return;
}

static int
x_transpose(int c MKSH_A_UNUSED)
{
	unsigned int tmpa, tmpb;

	/* What transpose is meant to do seems to be up for debate. This
	 * is a general summary of the options; the text is abcd with the
	 * upper case character or underscore indicating the cursor position:
	 *	Who			Before	After	Before	After
	 *	AT&T ksh in emacs mode:	abCd	abdC	abcd_	(bell)
	 *	AT&T ksh in gmacs mode:	abCd	baCd	abcd_	abdc_
	 *	gnu emacs:		abCd	acbD	abcd_	abdc_
	 * Pdksh currently goes with GNU behavior since I believe this is the
	 * most common version of emacs, unless in gmacs mode, in which case
	 * it does the AT&T ksh gmacs mode.
	 * This should really be broken up into 3 functions so users can bind
	 * to the one they want.
	 */
	if (xcp == xbuf) {
		x_e_putc2(7);
		return (KSTD);
	} else if (xcp == xep || Flag(FGMACS)) {
		if (xcp - xbuf == 1) {
			x_e_putc2(7);
			return (KSTD);
		}
		/* Gosling/Unipress emacs style: Swap two characters before the
		 * cursor, do not change cursor position
		 */
		x_bs3(&xcp);
		if (utf_mbtowc(&tmpa, xcp) == (size_t)-1) {
			x_e_putc2(7);
			return (KSTD);
		}
		x_bs3(&xcp);
		if (utf_mbtowc(&tmpb, xcp) == (size_t)-1) {
			x_e_putc2(7);
			return (KSTD);
		}
		utf_wctomb(xcp, tmpa);
		x_zotc3(&xcp);
		utf_wctomb(xcp, tmpb);
		x_zotc3(&xcp);
	} else {
		/* GNU emacs style: Swap the characters before and under the
		 * cursor, move cursor position along one.
		 */
		if (utf_mbtowc(&tmpa, xcp) == (size_t)-1) {
			x_e_putc2(7);
			return (KSTD);
		}
		x_bs3(&xcp);
		if (utf_mbtowc(&tmpb, xcp) == (size_t)-1) {
			x_e_putc2(7);
			return (KSTD);
		}
		utf_wctomb(xcp, tmpa);
		x_zotc3(&xcp);
		utf_wctomb(xcp, tmpb);
		x_zotc3(&xcp);
	}
	x_modified();
	return (KSTD);
}

static int
x_literal(int c MKSH_A_UNUSED)
{
	x_curprefix = -1;
	return (KSTD);
}

static int
x_meta1(int c MKSH_A_UNUSED)
{
	x_curprefix = 1;
	return (KSTD);
}

static int
x_meta2(int c MKSH_A_UNUSED)
{
	x_curprefix = 2;
	return (KSTD);
}

static int
x_kill(int c MKSH_A_UNUSED)
{
	int col = xcp - xbuf;
	int lastcol = xep - xbuf;
	int ndel;

	if (x_arg_defaulted)
		x_arg = lastcol;
	else if (x_arg > lastcol)
		x_arg = lastcol;
	ndel = x_arg - col;
	if (ndel < 0) {
		x_goto(xbuf + x_arg);
		ndel = -ndel;
	}
	x_delete(ndel, true);
	return (KSTD);
}

static void
x_push(int nchars)
{
	char *cp;

	strndupx(cp, xcp, nchars, AEDIT);
	if (killstack[killsp])
		afree(killstack[killsp], AEDIT);
	killstack[killsp] = cp;
	killsp = (killsp + 1) % KILLSIZE;
}

static int
x_yank(int c MKSH_A_UNUSED)
{
	if (killsp == 0)
		killtp = KILLSIZE;
	else
		killtp = killsp;
	killtp--;
	if (killstack[killtp] == 0) {
		x_e_puts("\nnothing to yank");
		x_redraw(-1);
		return (KSTD);
	}
	xmp = xcp;
	x_ins(killstack[killtp]);
	return (KSTD);
}

static int
x_meta_yank(int c MKSH_A_UNUSED)
{
	int len;

	if ((x_last_command != XFUNC_yank && x_last_command != XFUNC_meta_yank) ||
	    killstack[killtp] == 0) {
		killtp = killsp;
		x_e_puts("\nyank something first");
		x_redraw(-1);
		return (KSTD);
	}
	len = strlen(killstack[killtp]);
	x_goto(xcp - len);
	x_delete(len, false);
	do {
		if (killtp == 0)
			killtp = KILLSIZE - 1;
		else
			killtp--;
	} while (killstack[killtp] == 0);
	x_ins(killstack[killtp]);
	return (KSTD);
}

static int
x_abort(int c MKSH_A_UNUSED)
{
	/* x_zotc(c); */
	xlp = xep = xcp = xbp = xbuf;
	xlp_valid = true;
	*xcp = 0;
	x_modified();
	return (KINTR);
}

static int
x_error(int c MKSH_A_UNUSED)
{
	x_e_putc2(7);
	return (KSTD);
}

#ifndef MKSH_SMALL
/* special VT100 style key sequence hack */
static int
x_vt_hack(int c)
{
	/* we only support PF2-'1' for now */
	if (c != (2 << 8 | '1'))
		return (x_error(c));

	/* what's the next character? */
	switch ((c = x_e_getc())) {
	case '~':
		x_arg = 1;
		x_arg_defaulted = 1;
		return (x_mv_begin(0));
	case ';':
		/* "interesting" sequence detected */
		break;
	default:
		goto unwind_err;
	}

	/* XXX x_e_ungetc is one-octet only */
	if ((c = x_e_getc()) != '5' && c != '3')
		goto unwind_err;

	/*-
	 * At this point, we have read the following octets so far:
	 * - ESC+[ or ESC+O or Ctrl-X (Præfix 2)
	 * - 1 (vt_hack)
	 * - ;
	 * - 5 (Ctrl key combiner) or 3 (Alt key combiner)
	 * We can now accept one more octet designating the key.
	 */

	switch ((c = x_e_getc())) {
	case 'C':
		return (x_mv_fword(c));
	case 'D':
		return (x_mv_bword(c));
	}

 unwind_err:
	x_e_ungetc(c);
	return (x_error(c));
}
#endif

static char *
x_mapin(const char *cp, Area *ap)
{
	char *news, *op;

	/* for clang's static analyser, the nonnull attribute isn't enough */
	mkssert(cp != NULL);

	strdupx(news, cp, ap);
	op = news;
	while (*cp) {
		/* XXX -- should handle \^ escape? */
		if (*cp == '^') {
			cp++;
			if (*cp >= '?')	/* includes '?'; ASCII */
				*op++ = CTRL(*cp);
			else {
				*op++ = '^';
				cp--;
			}
		} else
			*op++ = *cp;
		cp++;
	}
	*op = '\0';

	return (news);
}

static void
x_mapout2(int c, char **buf)
{
	char *p = *buf;

	if (c < ' ' || c == 0x7f) {
		*p++ = '^';
		*p++ = UNCTRL(c);
	} else
		*p++ = c;
	*p = 0;
	*buf = p;
}

static char *
x_mapout(int c)
{
	static char buf[8];
	char *bp = buf;

	x_mapout2(c, &bp);
	return (buf);
}

static void
x_print(int prefix, int key)
{
	int f = x_tab[prefix][key];

	if (prefix)
		/* prefix == 1 || prefix == 2 */
		shf_puts(x_mapout(prefix == 1 ?
		    CTRL('[') : CTRL('X')), shl_stdout);
#ifdef MKSH_SMALL
	shprintf("%s = ", x_mapout(key));
#else
	shprintf("%s%s = ", x_mapout(key), (f & 0x80) ? "~" : "");
	if (XFUNC_VALUE(f) != XFUNC_ins_string)
#endif
		shprintf("%s\n", x_ftab[XFUNC_VALUE(f)].xf_name);
#ifndef MKSH_SMALL
	else
		shprintf("'%s'\n", x_atab[prefix][key]);
#endif
}

int
x_bind(const char *a1, const char *a2,
#ifndef MKSH_SMALL
    bool macro,			/* bind -m */
#endif
    bool list)			/* bind -l */
{
	unsigned char f;
	int prefix, key;
	char *m1, *m2;
#ifndef MKSH_SMALL
	char *sp = NULL;
	bool hastilde;
#endif

	if (x_tab == NULL) {
		bi_errorf("cannot bind, not a tty");
		return (1);
	}
	/* List function names */
	if (list) {
		for (f = 0; f < NELEM(x_ftab); f++)
			if (x_ftab[f].xf_name &&
			    !(x_ftab[f].xf_flags & XF_NOBIND))
				shprintf("%s\n", x_ftab[f].xf_name);
		return (0);
	}
	if (a1 == NULL) {
		for (prefix = 0; prefix < X_NTABS; prefix++)
			for (key = 0; key < X_TABSZ; key++) {
				f = XFUNC_VALUE(x_tab[prefix][key]);
				if (f == XFUNC_insert || f == XFUNC_error
#ifndef MKSH_SMALL
				    || (macro && f != XFUNC_ins_string)
#endif
				    )
					continue;
				x_print(prefix, key);
			}
		return (0);
	}
	m2 = m1 = x_mapin(a1, ATEMP);
	prefix = 0;
	for (;; m1++) {
		key = (unsigned char)*m1;
		f = XFUNC_VALUE(x_tab[prefix][key]);
		if (f == XFUNC_meta1)
			prefix = 1;
		else if (f == XFUNC_meta2)
			prefix = 2;
		else
			break;
	}
	if (*++m1
#ifndef MKSH_SMALL
	    && ((*m1 != '~') || *(m1 + 1))
#endif
	    ) {
		char msg[256] = "key sequence '";
		const char *c = a1;
		m1 = msg + strlen(msg);
		while (*c && m1 < (msg + sizeof(msg) - 3))
			x_mapout2(*c++, &m1);
		bi_errorf("%s' too long", msg);
		return (1);
	}
#ifndef MKSH_SMALL
	hastilde = *m1;
#endif
	afree(m2, ATEMP);

	if (a2 == NULL) {
		x_print(prefix, key);
		return (0);
	}
	if (*a2 == 0) {
		f = XFUNC_insert;
#ifndef MKSH_SMALL
	} else if (macro) {
		f = XFUNC_ins_string;
		sp = x_mapin(a2, AEDIT);
#endif
	} else {
		for (f = 0; f < NELEM(x_ftab); f++)
			if (x_ftab[f].xf_name &&
			    strcmp(x_ftab[f].xf_name, a2) == 0)
				break;
		if (f == NELEM(x_ftab) || x_ftab[f].xf_flags & XF_NOBIND) {
			bi_errorf("%s: no such function", a2);
			return (1);
		}
	}

#ifndef MKSH_SMALL
	if (XFUNC_VALUE(x_tab[prefix][key]) == XFUNC_ins_string &&
	    x_atab[prefix][key])
		afree(x_atab[prefix][key], AEDIT);
#endif
	x_tab[prefix][key] = f
#ifndef MKSH_SMALL
	    | (hastilde ? 0x80 : 0)
#endif
	    ;
#ifndef MKSH_SMALL
	x_atab[prefix][key] = sp;
#endif

	/* Track what the user has bound so x_mode(true) won't toast things */
	if (f == XFUNC_insert)
		x_bound[(prefix * X_TABSZ + key) / 8] &=
		    ~(1 << ((prefix * X_TABSZ + key) % 8));
	else
		x_bound[(prefix * X_TABSZ + key) / 8] |=
		    (1 << ((prefix * X_TABSZ + key) % 8));

	return (0);
}

static void
x_init_emacs(void)
{
	int i, j;

	ainit(AEDIT);
	x_nextcmd = -1;

	x_tab = alloc(X_NTABS * sizeof(*x_tab), AEDIT);
	for (j = 0; j < X_TABSZ; j++)
		x_tab[0][j] = XFUNC_insert;
	for (i = 1; i < X_NTABS; i++)
		for (j = 0; j < X_TABSZ; j++)
			x_tab[i][j] = XFUNC_error;
	for (i = 0; i < (int)NELEM(x_defbindings); i++)
		x_tab[x_defbindings[i].xdb_tab][x_defbindings[i].xdb_char]
		    = x_defbindings[i].xdb_func;

#ifndef MKSH_SMALL
	x_atab = alloc(X_NTABS * sizeof(*x_atab), AEDIT);
	for (i = 1; i < X_NTABS; i++)
		for (j = 0; j < X_TABSZ; j++)
			x_atab[i][j] = NULL;
#endif
}

static void
bind_if_not_bound(int p, int k, int func)
{
	/* Has user already bound this key? If so, don't override it */
	if (x_bound[((p) * X_TABSZ + (k)) / 8] &
	    (1 << (((p) * X_TABSZ + (k)) % 8)))
		return;

	x_tab[p][k] = func;
}

static int
x_set_mark(int c MKSH_A_UNUSED)
{
	xmp = xcp;
	return (KSTD);
}

static int
x_kill_region(int c MKSH_A_UNUSED)
{
	int rsize;
	char *xr;

	if (xmp == NULL) {
		x_e_putc2(7);
		return (KSTD);
	}
	if (xmp > xcp) {
		rsize = xmp - xcp;
		xr = xcp;
	} else {
		rsize = xcp - xmp;
		xr = xmp;
	}
	x_goto(xr);
	x_delete(rsize, true);
	xmp = xr;
	return (KSTD);
}

static int
x_xchg_point_mark(int c MKSH_A_UNUSED)
{
	char *tmp;

	if (xmp == NULL) {
		x_e_putc2(7);
		return (KSTD);
	}
	tmp = xmp;
	xmp = xcp;
	x_goto(tmp);
	return (KSTD);
}

static int
x_noop(int c MKSH_A_UNUSED)
{
	return (KSTD);
}

/*
 *	File/command name completion routines
 */
static int
x_comp_comm(int c MKSH_A_UNUSED)
{
	do_complete(XCF_COMMAND, CT_COMPLETE);
	return (KSTD);
}

static int
x_list_comm(int c MKSH_A_UNUSED)
{
	do_complete(XCF_COMMAND, CT_LIST);
	return (KSTD);
}

static int
x_complete(int c MKSH_A_UNUSED)
{
	do_complete(XCF_COMMAND_FILE, CT_COMPLETE);
	return (KSTD);
}

static int
x_enumerate(int c MKSH_A_UNUSED)
{
	do_complete(XCF_COMMAND_FILE, CT_LIST);
	return (KSTD);
}

static int
x_comp_file(int c MKSH_A_UNUSED)
{
	do_complete(XCF_FILE, CT_COMPLETE);
	return (KSTD);
}

static int
x_list_file(int c MKSH_A_UNUSED)
{
	do_complete(XCF_FILE, CT_LIST);
	return (KSTD);
}

static int
x_comp_list(int c MKSH_A_UNUSED)
{
	do_complete(XCF_COMMAND_FILE, CT_COMPLIST);
	return (KSTD);
}

static int
x_expand(int c MKSH_A_UNUSED)
{
	char **words;
	int start, end, nwords, i;
	bool is_command;

	nwords = x_cf_glob(XCF_FILE, xbuf, xep - xbuf, xcp - xbuf,
	    &start, &end, &words, &is_command);

	if (nwords == 0) {
		x_e_putc2(7);
		return (KSTD);
	}
	x_goto(xbuf + start);
	x_delete(end - start, false);
	for (i = 0; i < nwords;) {
		if (x_escape(words[i], strlen(words[i]), x_do_ins) < 0 ||
		    (++i < nwords && x_ins(" ") < 0)) {
			x_e_putc2(7);
			return (KSTD);
		}
	}
	x_adjust();

	return (KSTD);
}

/* type == 0 for list, 1 for complete and 2 for complete-list */
static void
do_complete(int flags,	/* XCF_{COMMAND,FILE,COMMAND_FILE} */
    Comp_type type)
{
	char **words;
	int start, end, nlen, olen, nwords;
	bool is_command, completed = false;

	nwords = x_cf_glob(flags, xbuf, xep - xbuf, xcp - xbuf,
	    &start, &end, &words, &is_command);
	/* no match */
	if (nwords == 0) {
		x_e_putc2(7);
		return;
	}
	if (type == CT_LIST) {
		x_print_expansions(nwords, words, is_command);
		x_redraw(0);
		x_free_words(nwords, words);
		return;
	}
	olen = end - start;
	nlen = x_longest_prefix(nwords, words);
	/* complete */
	if (nwords == 1 || nlen > olen) {
		x_goto(xbuf + start);
		x_delete(olen, false);
		x_escape(words[0], nlen, x_do_ins);
		x_adjust();
		completed = true;
	}
	/* add space if single non-dir match */
	if (nwords == 1 && words[0][nlen - 1] != '/') {
		x_ins(" ");
		completed = true;
	}
	if (type == CT_COMPLIST && !completed) {
		x_print_expansions(nwords, words, is_command);
		completed = true;
	}
	if (completed)
		x_redraw(0);

	x_free_words(nwords, words);
}

/* NAME:
 *	x_adjust - redraw the line adjusting starting point etc.
 *
 * DESCRIPTION:
 *	This function is called when we have exceeded the bounds
 *	of the edit window. It increments x_adj_done so that
 *	functions like x_ins and x_delete know that we have been
 *	called and can skip the x_bs() stuff which has already
 *	been done by x_redraw.
 *
 * RETURN VALUE:
 *	None
 */
static void
x_adjust(void)
{
	x_adj_done++;			/* flag the fact that we were called. */
	/*
	 * we had a problem if the prompt length > xx_cols / 2
	 */
	if ((xbp = xcp - (x_displen / 2)) < xbuf)
		xbp = xbuf;
	if (UTFMODE)
		while ((xbp > xbuf) && ((*xbp & 0xC0) == 0x80))
			--xbp;
	xlp_valid = false;
	x_redraw(xx_cols);
	x_flush();
}

static void
x_e_ungetc(int c)
{
	unget_char = c < 0 ? -1 : (c & 255);
}

static int
x_e_getc(void)
{
	int c;

	if (unget_char >= 0) {
		c = unget_char;
		unget_char = -1;
		return (c);
	}

#ifndef MKSH_SMALL
	if (macroptr) {
		if ((c = (unsigned char)*macroptr++))
			return (c);
		macroptr = NULL;
	}
#endif

	return (x_getc());
}

static void
x_e_putc2(int c)
{
	int width = 1;

	if (c == '\r' || c == '\n')
		x_col = 0;
	if (x_col < xx_cols) {
		if (UTFMODE && (c > 0x7F)) {
			char utf_tmp[3];
			size_t x;

			if (c < 0xA0)
				c = 0xFFFD;
			x = utf_wctomb(utf_tmp, c);
			x_putc(utf_tmp[0]);
			if (x > 1)
				x_putc(utf_tmp[1]);
			if (x > 2)
				x_putc(utf_tmp[2]);
			width = utf_wcwidth(c);
		} else
			x_putc(c);
		switch (c) {
		case 7:
			break;
		case '\r':
		case '\n':
			break;
		case '\b':
			x_col--;
			break;
		default:
			x_col += width;
			break;
		}
	}
	if (x_adj_ok && (x_col < 0 || x_col >= (xx_cols - 2)))
		x_adjust();
}

static void
x_e_putc3(const char **cp)
{
	int width = 1, c = **(const unsigned char **)cp;

	if (c == '\r' || c == '\n')
		x_col = 0;
	if (x_col < xx_cols) {
		if (UTFMODE && (c > 0x7F)) {
			char *cp2;

			width = utf_widthadj(*cp, (const char **)&cp2);
			while (*cp < cp2)
				x_putcf(*(*cp)++);
		} else {
			(*cp)++;
			x_putc(c);
		}
		switch (c) {
		case 7:
			break;
		case '\r':
		case '\n':
			break;
		case '\b':
			x_col--;
			break;
		default:
			x_col += width;
			break;
		}
	}
	if (x_adj_ok && (x_col < 0 || x_col >= (xx_cols - 2)))
		x_adjust();
}

static void
x_e_puts(const char *s)
{
	int adj = x_adj_done;

	while (*s && adj == x_adj_done)
		x_e_putc3(&s);
}

/* NAME:
 *	x_set_arg - set an arg value for next function
 *
 * DESCRIPTION:
 *	This is a simple implementation of M-[0-9].
 *
 * RETURN VALUE:
 *	KSTD
 */
static int
x_set_arg(int c)
{
	int n = 0, first = 1;

	c &= 255;	/* strip command prefix */
	for (; c >= 0 && ksh_isdigit(c); c = x_e_getc(), first = 0)
		n = n * 10 + (c - '0');
	if (c < 0 || first) {
		x_e_putc2(7);
		x_arg = 1;
		x_arg_defaulted = 1;
	} else {
		x_e_ungetc(c);
		x_arg = n;
		x_arg_defaulted = 0;
	}
	return (KSTD);
}

/* Comment or uncomment the current line. */
static int
x_comment(int c MKSH_A_UNUSED)
{
	int oldsize = x_size_str(xbuf);
	int len = xep - xbuf;
	int ret = x_do_comment(xbuf, xend - xbuf, &len);

	if (ret < 0)
		x_e_putc2(7);
	else {
		x_modified();
		xep = xbuf + len;
		*xep = '\0';
		xcp = xbp = xbuf;
		x_redraw(oldsize);
		if (ret > 0)
			return (x_newline('\n'));
	}
	return (KSTD);
}

static int
x_version(int c MKSH_A_UNUSED)
{
	char *o_xbuf = xbuf, *o_xend = xend;
	char *o_xbp = xbp, *o_xep = xep, *o_xcp = xcp;
	int vlen, lim = x_lastcp() - xbp;
	char *v;

	strdupx(v, KSH_VERSION, ATEMP);

	xbuf = xbp = xcp = v;
	xend = xep = v + (vlen = strlen(v));
	x_redraw(lim);
	x_flush();

	c = x_e_getc();
	xbuf = o_xbuf;
	xend = o_xend;
	xbp = o_xbp;
	xep = o_xep;
	xcp = o_xcp;
	x_redraw(vlen);

	if (c < 0)
		return (KSTD);
	/* This is what AT&T ksh seems to do... Very bizarre */
	if (c != ' ')
		x_e_ungetc(c);

	afree(v, ATEMP);
	return (KSTD);
}

#ifndef MKSH_SMALL
static int
x_edit_line(int c MKSH_A_UNUSED)
{
	if (x_arg_defaulted) {
		if (xep == xbuf) {
			x_e_putc2(7);
			return (KSTD);
		}
		if (modified) {
			*xep = '\0';
			histsave(&source->line, xbuf, true, true);
			x_arg = 0;
		} else
			x_arg = source->line - (histptr - x_histp);
	}
	if (x_arg)
		shf_snprintf(xbuf, xend - xbuf, "%s %d",
		    "fc -e ${VISUAL:-${EDITOR:-vi}} --", x_arg);
	else
		strlcpy(xbuf, "fc -e ${VISUAL:-${EDITOR:-vi}} --", xend - xbuf);
	xep = xbuf + strlen(xbuf);
	return (x_newline('\n'));
}
#endif

/* NAME:
 *	x_prev_histword - recover word from prev command
 *
 * DESCRIPTION:
 *	This function recovers the last word from the previous
 *	command and inserts it into the current edit line. If a
 *	numeric arg is supplied then the n'th word from the
 *	start of the previous command is used.
 *	As a side effect, trashes the mark in order to achieve
 *	being called in a repeatable fashion.
 *
 *	Bound to M-.
 *
 * RETURN VALUE:
 *	KSTD
 */
static int
x_prev_histword(int c MKSH_A_UNUSED)
{
	char *rcp, *cp;
	char **xhp;
	int m;

	if (xmp && modified > 1)
		x_kill_region(0);
	m = modified ? modified : 1;
	xhp = histptr - (m - 1);
	if ((xhp < history) || !(cp = *xhp)) {
		x_e_putc2(7);
		x_modified();
		return (KSTD);
	}
	x_set_mark(0);
	if (x_arg_defaulted) {
		rcp = &cp[strlen(cp) - 1];
		/*
		 * ignore white-space after the last word
		 */
		while (rcp > cp && is_cfs(*rcp))
			rcp--;
		while (rcp > cp && !is_cfs(*rcp))
			rcp--;
		if (is_cfs(*rcp))
			rcp++;
		x_ins(rcp);
	} else {
		char ch;

		rcp = cp;
		/*
		 * ignore white-space at start of line
		 */
		while (*rcp && is_cfs(*rcp))
			rcp++;
		while (x_arg-- > 1) {
			while (*rcp && !is_cfs(*rcp))
				rcp++;
			while (*rcp && is_cfs(*rcp))
				rcp++;
		}
		cp = rcp;
		while (*rcp && !is_cfs(*rcp))
			rcp++;
		ch = *rcp;
		*rcp = '\0';
		x_ins(cp);
		*rcp = ch;
	}
	modified = m + 1;
	return (KSTD);
}

#ifndef MKSH_SMALL
/* Uppercase N(1) words */
static int
x_fold_upper(int c MKSH_A_UNUSED)
{
	return (x_fold_case('U'));
}

/* Lowercase N(1) words */
static int
x_fold_lower(int c MKSH_A_UNUSED)
{
	return (x_fold_case('L'));
}

/* Lowercase N(1) words */
static int
x_fold_capitalise(int c MKSH_A_UNUSED)
{
	return (x_fold_case('C'));
}

/* NAME:
 *	x_fold_case - convert word to UPPER/lower/Capital case
 *
 * DESCRIPTION:
 *	This function is used to implement M-U,M-u,M-L,M-l,M-C and M-c
 *	to UPPER case, lower case or Capitalise words.
 *
 * RETURN VALUE:
 *	None
 */
static int
x_fold_case(int c)
{
	char *cp = xcp;

	if (cp == xep) {
		x_e_putc2(7);
		return (KSTD);
	}
	while (x_arg--) {
		/*
		 * first skip over any white-space
		 */
		while (cp != xep && is_mfs(*cp))
			cp++;
		/*
		 * do the first char on its own since it may be
		 * a different action than for the rest.
		 */
		if (cp != xep) {
			if (c == 'L')		/* lowercase */
				*cp = ksh_tolower(*cp);
			else			/* uppercase, capitalise */
				*cp = ksh_toupper(*cp);
			cp++;
		}
		/*
		 * now for the rest of the word
		 */
		while (cp != xep && !is_mfs(*cp)) {
			if (c == 'U')		/* uppercase */
				*cp = ksh_toupper(*cp);
			else			/* lowercase, capitalise */
				*cp = ksh_tolower(*cp);
			cp++;
		}
	}
	x_goto(cp);
	x_modified();
	return (KSTD);
}
#endif

/* NAME:
 *	x_lastcp - last visible char
 *
 * SYNOPSIS:
 *	x_lastcp()
 *
 * DESCRIPTION:
 *	This function returns a pointer to that char in the
 *	edit buffer that will be the last displayed on the
 *	screen. The sequence:
 *
 *	cp = x_lastcp();
 *	while (cp > xcp)
 *		x_bs3(&cp);
 *
 *	Will position the cursor correctly on the screen.
 *
 * RETURN VALUE:
 *	cp or NULL
 */
static char *
x_lastcp(void)
{
	if (!xlp_valid) {
		int i = 0, j;
		char *xlp2;

		xlp = xbp;
		while (xlp < xep) {
			j = x_size2(xlp, &xlp2);
			if ((i + j) > x_displen)
				break;
			i += j;
			xlp = xlp2;
		}
	}
	xlp_valid = true;
	return (xlp);
}

static bool
x_mode(bool onoff)
{
	static bool x_cur_mode;
	bool prev;

	if (x_cur_mode == onoff)
		return (x_cur_mode);
	prev = x_cur_mode;
	x_cur_mode = onoff;

	if (onoff) {
		struct termios cb;

		cb = tty_state;

		edchars.erase = cb.c_cc[VERASE];
		edchars.kill = cb.c_cc[VKILL];
		edchars.intr = cb.c_cc[VINTR];
		edchars.quit = cb.c_cc[VQUIT];
		edchars.eof = cb.c_cc[VEOF];
#ifdef VWERASE
		edchars.werase = cb.c_cc[VWERASE];
#endif
		cb.c_iflag &= ~(INLCR | ICRNL);
		cb.c_lflag &= ~(ISIG | ICANON | ECHO);
#if defined(VLNEXT) && defined(_POSIX_VDISABLE)
		/* osf/1 processes lnext when ~icanon */
		cb.c_cc[VLNEXT] = _POSIX_VDISABLE;
#endif
		/* sunos 4.1.x & osf/1 processes discard(flush) when ~icanon */
#if defined(VDISCARD) && defined(_POSIX_VDISABLE)
		cb.c_cc[VDISCARD] = _POSIX_VDISABLE;
#endif
		cb.c_cc[VTIME] = 0;
		cb.c_cc[VMIN] = 1;

		tcsetattr(tty_fd, TCSADRAIN, &cb);

#ifdef _POSIX_VDISABLE
		/* Convert unset values to internal 'unset' value */
		if (edchars.erase == _POSIX_VDISABLE)
			edchars.erase = -1;
		if (edchars.kill == _POSIX_VDISABLE)
			edchars.kill = -1;
		if (edchars.intr == _POSIX_VDISABLE)
			edchars.intr = -1;
		if (edchars.quit == _POSIX_VDISABLE)
			edchars.quit = -1;
		if (edchars.eof == _POSIX_VDISABLE)
			edchars.eof = -1;
		if (edchars.werase == _POSIX_VDISABLE)
			edchars.werase = -1;
#endif

		if (edchars.erase >= 0) {
			bind_if_not_bound(0, edchars.erase, XFUNC_del_back);
			bind_if_not_bound(1, edchars.erase, XFUNC_del_bword);
		}
		if (edchars.kill >= 0)
			bind_if_not_bound(0, edchars.kill, XFUNC_del_line);
		if (edchars.werase >= 0)
			bind_if_not_bound(0, edchars.werase, XFUNC_del_bword);
		if (edchars.intr >= 0)
			bind_if_not_bound(0, edchars.intr, XFUNC_abort);
		if (edchars.quit >= 0)
			bind_if_not_bound(0, edchars.quit, XFUNC_noop);
	} else
		tcsetattr(tty_fd, TCSADRAIN, &tty_state);

	return (prev);
}

#if !MKSH_S_NOVI
/* +++ vi editing mode +++ */

#define Ctrl(c)		(c&0x1f)

struct edstate {
	char *cbuf;
	int winleft;
	int cbufsize;
	int linelen;
	int cursor;
};

static int vi_hook(int);
static int nextstate(int);
static int vi_insert(int);
static int vi_cmd(int, const char *);
static int domove(int, const char *, int);
static int redo_insert(int);
static void yank_range(int, int);
static int bracktype(int);
static void save_cbuf(void);
static void restore_cbuf(void);
static int putbuf(const char *, int, int);
static void del_range(int, int);
static int findch(int, int, int, int);
static int forwword(int);
static int backword(int);
static int endword(int);
static int Forwword(int);
static int Backword(int);
static int Endword(int);
static int grabhist(int, int);
static int grabsearch(int, int, int, char *);
static void redraw_line(int);
static void refresh(int);
static int outofwin(void);
static void rewindow(void);
static int newcol(int, int);
static void display(char *, char *, int);
static void ed_mov_opt(int, char *);
static int expand_word(int);
static int complete_word(int, int);
static int print_expansions(struct edstate *, int);
#define char_len(c)	((c) < ' ' || (c) == 0x7F ? 2 : 1)
static void x_vi_zotc(int);
static void vi_error(void);
static void vi_macro_reset(void);
static int x_vi_putbuf(const char *, size_t);

#define C_	0x1		/* a valid command that isn't a M_, E_, U_ */
#define M_	0x2		/* movement command (h, l, etc.) */
#define E_	0x4		/* extended command (c, d, y) */
#define X_	0x8		/* long command (@, f, F, t, T, etc.) */
#define U_	0x10		/* an UN-undoable command (that isn't a M_) */
#define B_	0x20		/* bad command (^@) */
#define Z_	0x40		/* repeat count defaults to 0 (not 1) */
#define S_	0x80		/* search (/, ?) */

#define is_bad(c)	(classify[(c)&0x7f]&B_)
#define is_cmd(c)	(classify[(c)&0x7f]&(M_|E_|C_|U_))
#define is_move(c)	(classify[(c)&0x7f]&M_)
#define is_extend(c)	(classify[(c)&0x7f]&E_)
#define is_long(c)	(classify[(c)&0x7f]&X_)
#define is_undoable(c)	(!(classify[(c)&0x7f]&U_))
#define is_srch(c)	(classify[(c)&0x7f]&S_)
#define is_zerocount(c)	(classify[(c)&0x7f]&Z_)

static const unsigned char classify[128] = {
/*	 0	1	2	3	4	5	6	7	*/
/* 0	^@	^A	^B	^C	^D	^E	^F	^G	*/
	B_,	0,	0,	0,	0,	C_|U_,	C_|Z_,	0,
/* 1	^H	^I	^J	^K	^L	^M	^N	^O	*/
	M_,	C_|Z_,	0,	0,	C_|U_,	0,	C_,	0,
/* 2	^P	^Q	^R	^S	^T	^U	^V	^W	*/
	C_,	0,	C_|U_,	0,	0,	0,	C_,	0,
/* 3	^X	^Y	^Z	^[	^\	^]	^^	^_	*/
	C_,	0,	0,	C_|Z_,	0,	0,	0,	0,
/* 4	<space>	!	"	#	$	%	&	'	*/
	M_,	0,	0,	C_,	M_,	M_,	0,	0,
/* 5	(	)	*	+	,	-	.	/	*/
	0,	0,	C_,	C_,	M_,	C_,	0,	C_|S_,
/* 6	0	1	2	3	4	5	6	7	*/
	M_,	0,	0,	0,	0,	0,	0,	0,
/* 7	8	9	:	;	<	=	>	?	*/
	0,	0,	0,	M_,	0,	C_,	0,	C_|S_,
/* 8	@	A	B	C	D	E	F	G	*/
	C_|X_,	C_,	M_,	C_,	C_,	M_,	M_|X_,	C_|U_|Z_,
/* 9	H	I	J	K	L	M	N	O	*/
	0,	C_,	0,	0,	0,	0,	C_|U_,	0,
/* A	P	Q	R	S	T	U	V	W	*/
	C_,	0,	C_,	C_,	M_|X_,	C_,	0,	M_,
/* B	X	Y	Z	[	\	]	^	_	*/
	C_,	C_|U_,	0,	0,	C_|Z_,	0,	M_,	C_|Z_,
/* C	`	a	b	c	d	e	f	g	*/
	0,	C_,	M_,	E_,	E_,	M_,	M_|X_,	C_|Z_,
/* D	h	i	j	k	l	m	n	o	*/
	M_,	C_,	C_|U_,	C_|U_,	M_,	0,	C_|U_,	0,
/* E	p	q	r	s	t	u	v	w	*/
	C_,	0,	X_,	C_,	M_|X_,	C_|U_,	C_|U_|Z_, M_,
/* F	x	y	z	{	|	}	~	^?	*/
	C_,	E_|U_,	0,	0,	M_|Z_,	0,	C_,	0
};

#define MAXVICMD	3
#define SRCHLEN		40

#define INSERT		1
#define REPLACE		2

#define VNORMAL		0		/* command, insert or replace mode */
#define VARG1		1		/* digit prefix (first, eg, 5l) */
#define VEXTCMD		2		/* cmd + movement (eg, cl) */
#define VARG2		3		/* digit prefix (second, eg, 2c3l) */
#define VXCH		4		/* f, F, t, T, @ */
#define VFAIL		5		/* bad command */
#define VCMD		6		/* single char command (eg, X) */
#define VREDO		7		/* . */
#define VLIT		8		/* ^V */
#define VSEARCH		9		/* /, ? */
#define VVERSION	10		/* <ESC> ^V */

static char		undocbuf[LINE];

static struct edstate	*save_edstate(struct edstate *old);
static void		restore_edstate(struct edstate *old, struct edstate *news);
static void		free_edstate(struct edstate *old);

static struct edstate	ebuf;
static struct edstate	undobuf = { undocbuf, 0, LINE, 0, 0 };

static struct edstate	*es;			/* current editor state */
static struct edstate	*undo;

static char ibuf[LINE];			/* input buffer */
static int first_insert;		/* set when starting in insert mode */
static int saved_inslen;		/* saved inslen for first insert */
static int inslen;			/* length of input buffer */
static int srchlen;			/* length of current search pattern */
static char ybuf[LINE];			/* yank buffer */
static int yanklen;			/* length of yank buffer */
static int fsavecmd = ' ';		/* last find command */
static int fsavech;			/* character to find */
static char lastcmd[MAXVICMD];		/* last non-move command */
static int lastac;			/* argcnt for lastcmd */
static int lastsearch = ' ';		/* last search command */
static char srchpat[SRCHLEN];		/* last search pattern */
static int insert;			/* non-zero in insert mode */
static int hnum;			/* position in history */
static int ohnum;			/* history line copied (after mod) */
static int hlast;			/* 1 past last position in history */
static int state;

/* Information for keeping track of macros that are being expanded.
 * The format of buf is the alias contents followed by a NUL byte followed
 * by the name (letter) of the alias. The end of the buffer is marked by
 * a double NUL. The name of the alias is stored so recursive macros can
 * be detected.
 */
struct macro_state {
	unsigned char *p;	/* current position in buf */
	unsigned char *buf;	/* pointer to macro(s) being expanded */
	int len;		/* how much data in buffer */
};
static struct macro_state macro;

enum expand_mode {
	NONE, EXPAND, COMPLETE, PRINT
};
static enum expand_mode expanded = NONE;	/* last input was expanded */

static int
x_vi(char *buf, size_t len)
{
	int c;

	state = VNORMAL;
	ohnum = hnum = hlast = histnum(-1) + 1;
	insert = INSERT;
	saved_inslen = inslen;
	first_insert = 1;
	inslen = 0;
	vi_macro_reset();

	es = &ebuf;
	es->cbuf = buf;
	undo = &undobuf;
	undo->cbufsize = es->cbufsize = len > LINE ? LINE : len;

	es->linelen = undo->linelen = 0;
	es->cursor = undo->cursor = 0;
	es->winleft = undo->winleft = 0;

	cur_col = promptlen(prompt);
	prompt_trunc = (cur_col / x_cols) * x_cols;
	cur_col -= prompt_trunc;

	pprompt(prompt, 0);
	if (cur_col > x_cols - 3 - MIN_EDIT_SPACE) {
		prompt_redraw = cur_col = 0;
		x_putc('\n');
	} else
		prompt_redraw = 1;
	pwidth = cur_col;

	if (!wbuf_len || wbuf_len != x_cols - 3) {
		wbuf_len = x_cols - 3;
		wbuf[0] = aresize(wbuf[0], wbuf_len, APERM);
		wbuf[1] = aresize(wbuf[1], wbuf_len, APERM);
	}
	(void)memset(wbuf[0], ' ', wbuf_len);
	(void)memset(wbuf[1], ' ', wbuf_len);
	winwidth = x_cols - pwidth - 3;
	win = 0;
	morec = ' ';
	lastref = 1;
	holdlen = 0;

	editmode = 2;
	x_flush();
	while (1) {
		if (macro.p) {
			c = *macro.p++;
			/* end of current macro? */
			if (!c) {
				/* more macros left to finish? */
				if (*macro.p++)
					continue;
				/* must be the end of all the macros */
				vi_macro_reset();
				c = x_getc();
			}
		} else
			c = x_getc();

		if (c == -1)
			break;
		if (state != VLIT) {
			if (c == edchars.intr || c == edchars.quit) {
				/* pretend we got an interrupt */
				x_vi_zotc(c);
				x_flush();
				trapsig(c == edchars.intr ? SIGINT : SIGQUIT);
				x_mode(false);
				unwind(LSHELL);
			} else if (c == edchars.eof && state != VVERSION) {
				if (es->linelen == 0) {
					x_vi_zotc(edchars.eof);
					c = -1;
					break;
				}
				continue;
			}
		}
		if (vi_hook(c))
			break;
		x_flush();
	}

	x_putc('\r');
	x_putc('\n');
	x_flush();

	if (c == -1 || (ssize_t)len <= es->linelen)
		return (-1);

	if (es->cbuf != buf)
		memmove(buf, es->cbuf, es->linelen);

	buf[es->linelen++] = '\n';

	return (es->linelen);
}

static int
vi_hook(int ch)
{
	static char curcmd[MAXVICMD], locpat[SRCHLEN];
	static int cmdlen, argc1, argc2;

	switch (state) {

	case VNORMAL:
		if (insert != 0) {
			if (ch == Ctrl('v')) {
				state = VLIT;
				ch = '^';
			}
			switch (vi_insert(ch)) {
			case -1:
				vi_error();
				state = VNORMAL;
				break;
			case 0:
				if (state == VLIT) {
					es->cursor--;
					refresh(0);
				} else
					refresh(insert != 0);
				break;
			case 1:
				return (1);
			}
		} else {
			if (ch == '\r' || ch == '\n')
				return (1);
			cmdlen = 0;
			argc1 = 0;
			if (ch >= '1' && ch <= '9') {
				argc1 = ch - '0';
				state = VARG1;
			} else {
				curcmd[cmdlen++] = ch;
				state = nextstate(ch);
				if (state == VSEARCH) {
					save_cbuf();
					es->cursor = 0;
					es->linelen = 0;
					if (ch == '/') {
						if (putbuf("/", 1, 0) != 0)
							return (-1);
					} else if (putbuf("?", 1, 0) != 0)
						return (-1);
					refresh(0);
				}
				if (state == VVERSION) {
					save_cbuf();
					es->cursor = 0;
					es->linelen = 0;
					putbuf(KSH_VERSION,
					    strlen(KSH_VERSION), 0);
					refresh(0);
				}
			}
		}
		break;

	case VLIT:
		if (is_bad(ch)) {
			del_range(es->cursor, es->cursor + 1);
			vi_error();
		} else
			es->cbuf[es->cursor++] = ch;
		refresh(1);
		state = VNORMAL;
		break;

	case VVERSION:
		restore_cbuf();
		state = VNORMAL;
		refresh(0);
		break;

	case VARG1:
		if (ksh_isdigit(ch))
			argc1 = argc1 * 10 + ch - '0';
		else {
			curcmd[cmdlen++] = ch;
			state = nextstate(ch);
		}
		break;

	case VEXTCMD:
		argc2 = 0;
		if (ch >= '1' && ch <= '9') {
			argc2 = ch - '0';
			state = VARG2;
			return (0);
		} else {
			curcmd[cmdlen++] = ch;
			if (ch == curcmd[0])
				state = VCMD;
			else if (is_move(ch))
				state = nextstate(ch);
			else
				state = VFAIL;
		}
		break;

	case VARG2:
		if (ksh_isdigit(ch))
			argc2 = argc2 * 10 + ch - '0';
		else {
			if (argc1 == 0)
				argc1 = argc2;
			else
				argc1 *= argc2;
			curcmd[cmdlen++] = ch;
			if (ch == curcmd[0])
				state = VCMD;
			else if (is_move(ch))
				state = nextstate(ch);
			else
				state = VFAIL;
		}
		break;

	case VXCH:
		if (ch == Ctrl('['))
			state = VNORMAL;
		else {
			curcmd[cmdlen++] = ch;
			state = VCMD;
		}
		break;

	case VSEARCH:
		if (ch == '\r' || ch == '\n' /*|| ch == Ctrl('[')*/ ) {
			restore_cbuf();
			/* Repeat last search? */
			if (srchlen == 0) {
				if (!srchpat[0]) {
					vi_error();
					state = VNORMAL;
					refresh(0);
					return (0);
				}
			} else {
				locpat[srchlen] = '\0';
				memcpy(srchpat, locpat, srchlen + 1);
			}
			state = VCMD;
		} else if (ch == edchars.erase || ch == Ctrl('h')) {
			if (srchlen != 0) {
				srchlen--;
				es->linelen -= char_len((unsigned char)locpat[srchlen]);
				es->cursor = es->linelen;
				refresh(0);
				return (0);
			}
			restore_cbuf();
			state = VNORMAL;
			refresh(0);
		} else if (ch == edchars.kill) {
			srchlen = 0;
			es->linelen = 1;
			es->cursor = 1;
			refresh(0);
			return (0);
		} else if (ch == edchars.werase) {
			int i, n = srchlen;
			struct edstate new_es, *save_es;

			new_es.cursor = n;
			new_es.cbuf = locpat;

			save_es = es;
			es = &new_es;
			n = backword(1);
			es = save_es;

			for (i = srchlen; --i >= n; )
				es->linelen -= char_len((unsigned char)locpat[i]);
			srchlen = n;
			es->cursor = es->linelen;
			refresh(0);
			return (0);
		} else {
			if (srchlen == SRCHLEN - 1)
				vi_error();
			else {
				locpat[srchlen++] = ch;
				if (ch < ' ' || ch == 0x7f) {
					if (es->linelen + 2 > es->cbufsize)
						vi_error();
					es->cbuf[es->linelen++] = '^';
					es->cbuf[es->linelen++] = ch ^ '@';
				} else {
					if (es->linelen >= es->cbufsize)
						vi_error();
					es->cbuf[es->linelen++] = ch;
				}
				es->cursor = es->linelen;
				refresh(0);
			}
			return (0);
		}
		break;
	}

	switch (state) {
	case VCMD:
		state = VNORMAL;
		switch (vi_cmd(argc1, curcmd)) {
		case -1:
			vi_error();
			refresh(0);
			break;
		case 0:
			if (insert != 0)
				inslen = 0;
			refresh(insert != 0);
			break;
		case 1:
			refresh(0);
			return (1);
		case 2:
			/* back from a 'v' command - don't redraw the screen */
			return (1);
		}
		break;

	case VREDO:
		state = VNORMAL;
		if (argc1 != 0)
			lastac = argc1;
		switch (vi_cmd(lastac, lastcmd)) {
		case -1:
			vi_error();
			refresh(0);
			break;
		case 0:
			if (insert != 0) {
				if (lastcmd[0] == 's' || lastcmd[0] == 'c' ||
				    lastcmd[0] == 'C') {
					if (redo_insert(1) != 0)
						vi_error();
				} else {
					if (redo_insert(lastac) != 0)
						vi_error();
				}
			}
			refresh(0);
			break;
		case 1:
			refresh(0);
			return (1);
		case 2:
			/* back from a 'v' command - can't happen */
			break;
		}
		break;

	case VFAIL:
		state = VNORMAL;
		vi_error();
		break;
	}
	return (0);
}

static int
nextstate(int ch)
{
	if (is_extend(ch))
		return (VEXTCMD);
	else if (is_srch(ch))
		return (VSEARCH);
	else if (is_long(ch))
		return (VXCH);
	else if (ch == '.')
		return (VREDO);
	else if (ch == Ctrl('v'))
		return (VVERSION);
	else if (is_cmd(ch))
		return (VCMD);
	else
		return (VFAIL);
}

static int
vi_insert(int ch)
{
	int tcursor;

	if (ch == edchars.erase || ch == Ctrl('h')) {
		if (insert == REPLACE) {
			if (es->cursor == undo->cursor) {
				vi_error();
				return (0);
			}
			if (inslen > 0)
				inslen--;
			es->cursor--;
			if (es->cursor >= undo->linelen)
				es->linelen--;
			else
				es->cbuf[es->cursor] = undo->cbuf[es->cursor];
		} else {
			if (es->cursor == 0)
				return (0);
			if (inslen > 0)
				inslen--;
			es->cursor--;
			es->linelen--;
			memmove(&es->cbuf[es->cursor], &es->cbuf[es->cursor + 1],
			    es->linelen - es->cursor + 1);
		}
		expanded = NONE;
		return (0);
	}
	if (ch == edchars.kill) {
		if (es->cursor != 0) {
			inslen = 0;
			memmove(es->cbuf, &es->cbuf[es->cursor],
			    es->linelen - es->cursor);
			es->linelen -= es->cursor;
			es->cursor = 0;
		}
		expanded = NONE;
		return (0);
	}
	if (ch == edchars.werase) {
		if (es->cursor != 0) {
			tcursor = backword(1);
			memmove(&es->cbuf[tcursor], &es->cbuf[es->cursor],
			    es->linelen - es->cursor);
			es->linelen -= es->cursor - tcursor;
			if (inslen < es->cursor - tcursor)
				inslen = 0;
			else
				inslen -= es->cursor - tcursor;
			es->cursor = tcursor;
		}
		expanded = NONE;
		return (0);
	}
	/* If any chars are entered before escape, trash the saved insert
	 * buffer (if user inserts & deletes char, ibuf gets trashed and
	 * we don't want to use it)
	 */
	if (first_insert && ch != Ctrl('['))
		saved_inslen = 0;
	switch (ch) {
	case '\0':
		return (-1);

	case '\r':
	case '\n':
		return (1);

	case Ctrl('['):
		expanded = NONE;
		if (first_insert) {
			first_insert = 0;
			if (inslen == 0) {
				inslen = saved_inslen;
				return (redo_insert(0));
			}
			lastcmd[0] = 'a';
			lastac = 1;
		}
		if (lastcmd[0] == 's' || lastcmd[0] == 'c' ||
		    lastcmd[0] == 'C')
			return (redo_insert(0));
		else
			return (redo_insert(lastac - 1));

	/* { Begin nonstandard vi commands */
	case Ctrl('x'):
		expand_word(0);
		break;

	case Ctrl('f'):
		complete_word(0, 0);
		break;

	case Ctrl('e'):
		print_expansions(es, 0);
		break;

	case Ctrl('i'):
		if (Flag(FVITABCOMPLETE)) {
			complete_word(0, 0);
			break;
		}
		/* FALLTHROUGH */
	/* End nonstandard vi commands } */

	default:
		if (es->linelen >= es->cbufsize - 1)
			return (-1);
		ibuf[inslen++] = ch;
		if (insert == INSERT) {
			memmove(&es->cbuf[es->cursor + 1], &es->cbuf[es->cursor],
			    es->linelen - es->cursor);
			es->linelen++;
		}
		es->cbuf[es->cursor++] = ch;
		if (insert == REPLACE && es->cursor > es->linelen)
			es->linelen++;
		expanded = NONE;
	}
	return (0);
}

static int
vi_cmd(int argcnt, const char *cmd)
{
	int ncursor;
	int cur, c1, c2, c3 = 0;
	int any;
	struct edstate *t;

	if (argcnt == 0 && !is_zerocount(*cmd))
		argcnt = 1;

	if (is_move(*cmd)) {
		if ((cur = domove(argcnt, cmd, 0)) >= 0) {
			if (cur == es->linelen && cur != 0)
				cur--;
			es->cursor = cur;
		} else
			return (-1);
	} else {
		/* Don't save state in middle of macro.. */
		if (is_undoable(*cmd) && !macro.p) {
			undo->winleft = es->winleft;
			memmove(undo->cbuf, es->cbuf, es->linelen);
			undo->linelen = es->linelen;
			undo->cursor = es->cursor;
			lastac = argcnt;
			memmove(lastcmd, cmd, MAXVICMD);
		}
		switch (*cmd) {

		case Ctrl('l'):
		case Ctrl('r'):
			redraw_line(1);
			break;

		case '@':
			{
				static char alias[] = "_\0";
				struct tbl *ap;
				int olen, nlen;
				char *p, *nbuf;

				/* lookup letter in alias list... */
				alias[1] = cmd[1];
				ap = ktsearch(&aliases, alias, hash(alias));
				if (!cmd[1] || !ap || !(ap->flag & ISSET))
					return (-1);
				/* check if this is a recursive call... */
				if ((p = (char *)macro.p))
					while ((p = strnul(p)) && p[1])
						if (*++p == cmd[1])
							return (-1);
				/* insert alias into macro buffer */
				nlen = strlen(ap->val.s) + 1;
				olen = !macro.p ? 2 :
				    macro.len - (macro.p - macro.buf);
				nbuf = alloc(nlen + 1 + olen, APERM);
				memcpy(nbuf, ap->val.s, nlen);
				nbuf[nlen++] = cmd[1];
				if (macro.p) {
					memcpy(nbuf + nlen, macro.p, olen);
					afree(macro.buf, APERM);
					nlen += olen;
				} else {
					nbuf[nlen++] = '\0';
					nbuf[nlen++] = '\0';
				}
				macro.p = macro.buf = (unsigned char *)nbuf;
				macro.len = nlen;
			}
			break;

		case 'a':
			modified = 1;
			hnum = hlast;
			if (es->linelen != 0)
				es->cursor++;
			insert = INSERT;
			break;

		case 'A':
			modified = 1;
			hnum = hlast;
			del_range(0, 0);
			es->cursor = es->linelen;
			insert = INSERT;
			break;

		case 'S':
			es->cursor = domove(1, "^", 1);
			del_range(es->cursor, es->linelen);
			modified = 1;
			hnum = hlast;
			insert = INSERT;
			break;

		case 'Y':
			cmd = "y$";
			/* ahhhhhh... */
		case 'c':
		case 'd':
		case 'y':
			if (*cmd == cmd[1]) {
				c1 = *cmd == 'c' ? domove(1, "^", 1) : 0;
				c2 = es->linelen;
			} else if (!is_move(cmd[1]))
				return (-1);
			else {
				if ((ncursor = domove(argcnt, &cmd[1], 1)) < 0)
					return (-1);
				if (*cmd == 'c' &&
				    (cmd[1] == 'w' || cmd[1] == 'W') &&
				    !ksh_isspace(es->cbuf[es->cursor])) {
					do {
						--ncursor;
					} while (ksh_isspace(es->cbuf[ncursor]));
					ncursor++;
				}
				if (ncursor > es->cursor) {
					c1 = es->cursor;
					c2 = ncursor;
				} else {
					c1 = ncursor;
					c2 = es->cursor;
					if (cmd[1] == '%')
						c2++;
				}
			}
			if (*cmd != 'c' && c1 != c2)
				yank_range(c1, c2);
			if (*cmd != 'y') {
				del_range(c1, c2);
				es->cursor = c1;
			}
			if (*cmd == 'c') {
				modified = 1;
				hnum = hlast;
				insert = INSERT;
			}
			break;

		case 'p':
			modified = 1;
			hnum = hlast;
			if (es->linelen != 0)
				es->cursor++;
			while (putbuf(ybuf, yanklen, 0) == 0 && --argcnt > 0)
				;
			if (es->cursor != 0)
				es->cursor--;
			if (argcnt != 0)
				return (-1);
			break;

		case 'P':
			modified = 1;
			hnum = hlast;
			any = 0;
			while (putbuf(ybuf, yanklen, 0) == 0 && --argcnt > 0)
				any = 1;
			if (any && es->cursor != 0)
				es->cursor--;
			if (argcnt != 0)
				return (-1);
			break;

		case 'C':
			modified = 1;
			hnum = hlast;
			del_range(es->cursor, es->linelen);
			insert = INSERT;
			break;

		case 'D':
			yank_range(es->cursor, es->linelen);
			del_range(es->cursor, es->linelen);
			if (es->cursor != 0)
				es->cursor--;
			break;

		case 'g':
			if (!argcnt)
				argcnt = hlast;
			/* FALLTHROUGH */
		case 'G':
			if (!argcnt)
				argcnt = 1;
			else
				argcnt = hlast - (source->line - argcnt);
			if (grabhist(modified, argcnt - 1) < 0)
				return (-1);
			else {
				modified = 0;
				hnum = argcnt - 1;
			}
			break;

		case 'i':
			modified = 1;
			hnum = hlast;
			insert = INSERT;
			break;

		case 'I':
			modified = 1;
			hnum = hlast;
			es->cursor = domove(1, "^", 1);
			insert = INSERT;
			break;

		case 'j':
		case '+':
		case Ctrl('n'):
			if (grabhist(modified, hnum + argcnt) < 0)
				return (-1);
			else {
				modified = 0;
				hnum += argcnt;
			}
			break;

		case 'k':
		case '-':
		case Ctrl('p'):
			if (grabhist(modified, hnum - argcnt) < 0)
				return (-1);
			else {
				modified = 0;
				hnum -= argcnt;
			}
			break;

		case 'r':
			if (es->linelen == 0)
				return (-1);
			modified = 1;
			hnum = hlast;
			if (cmd[1] == 0)
				vi_error();
			else {
				int n;

				if (es->cursor + argcnt > es->linelen)
					return (-1);
				for (n = 0; n < argcnt; ++n)
					es->cbuf[es->cursor + n] = cmd[1];
				es->cursor += n - 1;
			}
			break;

		case 'R':
			modified = 1;
			hnum = hlast;
			insert = REPLACE;
			break;

		case 's':
			if (es->linelen == 0)
				return (-1);
			modified = 1;
			hnum = hlast;
			if (es->cursor + argcnt > es->linelen)
				argcnt = es->linelen - es->cursor;
			del_range(es->cursor, es->cursor + argcnt);
			insert = INSERT;
			break;

		case 'v':
			if (!argcnt) {
				if (es->linelen == 0)
					return (-1);
				if (modified) {
					es->cbuf[es->linelen] = '\0';
					histsave(&source->line, es->cbuf, true,
					    true);
				} else
					argcnt = source->line + 1 -
					    (hlast - hnum);
			}
			if (argcnt)
				shf_snprintf(es->cbuf, es->cbufsize, "%s %d",
				    "fc -e ${VISUAL:-${EDITOR:-vi}} --",
				    argcnt);
			else
				strlcpy(es->cbuf,
				    "fc -e ${VISUAL:-${EDITOR:-vi}} --",
				    es->cbufsize);
			es->linelen = strlen(es->cbuf);
			return (2);

		case 'x':
			if (es->linelen == 0)
				return (-1);
			modified = 1;
			hnum = hlast;
			if (es->cursor + argcnt > es->linelen)
				argcnt = es->linelen - es->cursor;
			yank_range(es->cursor, es->cursor + argcnt);
			del_range(es->cursor, es->cursor + argcnt);
			break;

		case 'X':
			if (es->cursor > 0) {
				modified = 1;
				hnum = hlast;
				if (es->cursor < argcnt)
					argcnt = es->cursor;
				yank_range(es->cursor - argcnt, es->cursor);
				del_range(es->cursor - argcnt, es->cursor);
				es->cursor -= argcnt;
			} else
				return (-1);
			break;

		case 'u':
			t = es;
			es = undo;
			undo = t;
			break;

		case 'U':
			if (!modified)
				return (-1);
			if (grabhist(modified, ohnum) < 0)
				return (-1);
			modified = 0;
			hnum = ohnum;
			break;

		case '?':
			if (hnum == hlast)
				hnum = -1;
			/* ahhh */
		case '/':
			c3 = 1;
			srchlen = 0;
			lastsearch = *cmd;
			/* FALLTHROUGH */
		case 'n':
		case 'N':
			if (lastsearch == ' ')
				return (-1);
			if (lastsearch == '?')
				c1 = 1;
			else
				c1 = 0;
			if (*cmd == 'N')
				c1 = !c1;
			if ((c2 = grabsearch(modified, hnum,
			    c1, srchpat)) < 0) {
				if (c3) {
					restore_cbuf();
					refresh(0);
				}
				return (-1);
			} else {
				modified = 0;
				hnum = c2;
				ohnum = hnum;
			}
			break;
		case '_':
			{
				int inspace;
				char *p, *sp;

				if (histnum(-1) < 0)
					return (-1);
				p = *histpos();
#define issp(c)		(ksh_isspace(c) || (c) == '\n')
				if (argcnt) {
					while (*p && issp(*p))
						p++;
					while (*p && --argcnt) {
						while (*p && !issp(*p))
							p++;
						while (*p && issp(*p))
							p++;
					}
					if (!*p)
						return (-1);
					sp = p;
				} else {
					sp = p;
					inspace = 0;
					while (*p) {
						if (issp(*p))
							inspace = 1;
						else if (inspace) {
							inspace = 0;
							sp = p;
						}
						p++;
					}
					p = sp;
				}
				modified = 1;
				hnum = hlast;
				if (es->cursor != es->linelen)
					es->cursor++;
				while (*p && !issp(*p)) {
					argcnt++;
					p++;
				}
				if (putbuf(" ", 1, 0) != 0)
					argcnt = -1;
				else if (putbuf(sp, argcnt, 0) != 0)
					argcnt = -1;
				if (argcnt < 0) {
					if (es->cursor != 0)
						es->cursor--;
					return (-1);
				}
				insert = INSERT;
			}
			break;

		case '~':
			{
				char *p;
				int i;

				if (es->linelen == 0)
					return (-1);
				for (i = 0; i < argcnt; i++) {
					p = &es->cbuf[es->cursor];
					if (ksh_islower(*p)) {
						modified = 1;
						hnum = hlast;
						*p = ksh_toupper(*p);
					} else if (ksh_isupper(*p)) {
						modified = 1;
						hnum = hlast;
						*p = ksh_tolower(*p);
					}
					if (es->cursor < es->linelen - 1)
						es->cursor++;
				}
				break;
			}

		case '#':
			{
				int ret = x_do_comment(es->cbuf, es->cbufsize,
				    &es->linelen);
				if (ret >= 0)
					es->cursor = 0;
				return (ret);
			}

		case '=':			/* AT&T ksh */
		case Ctrl('e'):			/* Nonstandard vi/ksh */
			print_expansions(es, 1);
			break;


		case Ctrl('i'):			/* Nonstandard vi/ksh */
			if (!Flag(FVITABCOMPLETE))
				return (-1);
			complete_word(1, argcnt);
			break;

		case Ctrl('['):			/* some annoying AT&T kshs */
			if (!Flag(FVIESCCOMPLETE))
				return (-1);
		case '\\':			/* AT&T ksh */
		case Ctrl('f'):			/* Nonstandard vi/ksh */
			complete_word(1, argcnt);
			break;


		case '*':			/* AT&T ksh */
		case Ctrl('x'):			/* Nonstandard vi/ksh */
			expand_word(1);
			break;
		}
		if (insert == 0 && es->cursor != 0 && es->cursor >= es->linelen)
			es->cursor--;
	}
	return (0);
}

static int
domove(int argcnt, const char *cmd, int sub)
{
	int bcount, i = 0, t;
	int ncursor = 0;

	switch (*cmd) {
	case 'b':
		if (!sub && es->cursor == 0)
			return (-1);
		ncursor = backword(argcnt);
		break;

	case 'B':
		if (!sub && es->cursor == 0)
			return (-1);
		ncursor = Backword(argcnt);
		break;

	case 'e':
		if (!sub && es->cursor + 1 >= es->linelen)
			return (-1);
		ncursor = endword(argcnt);
		if (sub && ncursor < es->linelen)
			ncursor++;
		break;

	case 'E':
		if (!sub && es->cursor + 1 >= es->linelen)
			return (-1);
		ncursor = Endword(argcnt);
		if (sub && ncursor < es->linelen)
			ncursor++;
		break;

	case 'f':
	case 'F':
	case 't':
	case 'T':
		fsavecmd = *cmd;
		fsavech = cmd[1];
		/* drop through */

	case ',':
	case ';':
		if (fsavecmd == ' ')
			return (-1);
		i = fsavecmd == 'f' || fsavecmd == 'F';
		t = fsavecmd > 'a';
		if (*cmd == ',')
			t = !t;
		if ((ncursor = findch(fsavech, argcnt, t, i)) < 0)
			return (-1);
		if (sub && t)
			ncursor++;
		break;

	case 'h':
	case Ctrl('h'):
		if (!sub && es->cursor == 0)
			return (-1);
		ncursor = es->cursor - argcnt;
		if (ncursor < 0)
			ncursor = 0;
		break;

	case ' ':
	case 'l':
		if (!sub && es->cursor + 1 >= es->linelen)
			return (-1);
		if (es->linelen != 0) {
			ncursor = es->cursor + argcnt;
			if (ncursor > es->linelen)
				ncursor = es->linelen;
		}
		break;

	case 'w':
		if (!sub && es->cursor + 1 >= es->linelen)
			return (-1);
		ncursor = forwword(argcnt);
		break;

	case 'W':
		if (!sub && es->cursor + 1 >= es->linelen)
			return (-1);
		ncursor = Forwword(argcnt);
		break;

	case '0':
		ncursor = 0;
		break;

	case '^':
		ncursor = 0;
		while (ncursor < es->linelen - 1 &&
		    ksh_isspace(es->cbuf[ncursor]))
			ncursor++;
		break;

	case '|':
		ncursor = argcnt;
		if (ncursor > es->linelen)
			ncursor = es->linelen;
		if (ncursor)
			ncursor--;
		break;

	case '$':
		if (es->linelen != 0)
			ncursor = es->linelen;
		else
			ncursor = 0;
		break;

	case '%':
		ncursor = es->cursor;
		while (ncursor < es->linelen &&
		    (i = bracktype(es->cbuf[ncursor])) == 0)
			ncursor++;
		if (ncursor == es->linelen)
			return (-1);
		bcount = 1;
		do {
			if (i > 0) {
				if (++ncursor >= es->linelen)
					return (-1);
			} else {
				if (--ncursor < 0)
					return (-1);
			}
			t = bracktype(es->cbuf[ncursor]);
			if (t == i)
				bcount++;
			else if (t == -i)
				bcount--;
		} while (bcount != 0);
		if (sub && i > 0)
			ncursor++;
		break;

	default:
		return (-1);
	}
	return (ncursor);
}

static int
redo_insert(int count)
{
	while (count-- > 0)
		if (putbuf(ibuf, inslen, insert == REPLACE) != 0)
			return (-1);
	if (es->cursor > 0)
		es->cursor--;
	insert = 0;
	return (0);
}

static void
yank_range(int a, int b)
{
	yanklen = b - a;
	if (yanklen != 0)
		memmove(ybuf, &es->cbuf[a], yanklen);
}

static int
bracktype(int ch)
{
	switch (ch) {

	case '(':
		return (1);

	case '[':
		return (2);

	case '{':
		return (3);

	case ')':
		return (-1);

	case ']':
		return (-2);

	case '}':
		return (-3);

	default:
		return (0);
	}
}

/*
 *	Non user interface editor routines below here
 */

static void
save_cbuf(void)
{
	memmove(holdbuf, es->cbuf, es->linelen);
	holdlen = es->linelen;
	holdbuf[holdlen] = '\0';
}

static void
restore_cbuf(void)
{
	es->cursor = 0;
	es->linelen = holdlen;
	memmove(es->cbuf, holdbuf, holdlen);
}

/* return a new edstate */
static struct edstate *
save_edstate(struct edstate *old)
{
	struct edstate *news;

	news = alloc(sizeof(struct edstate), APERM);
	news->cbuf = alloc(old->cbufsize, APERM);
	memcpy(news->cbuf, old->cbuf, old->linelen);
	news->cbufsize = old->cbufsize;
	news->linelen = old->linelen;
	news->cursor = old->cursor;
	news->winleft = old->winleft;
	return (news);
}

static void
restore_edstate(struct edstate *news, struct edstate *old)
{
	memcpy(news->cbuf, old->cbuf, old->linelen);
	news->linelen = old->linelen;
	news->cursor = old->cursor;
	news->winleft = old->winleft;
	free_edstate(old);
}

static void
free_edstate(struct edstate *old)
{
	afree(old->cbuf, APERM);
	afree(old, APERM);
}

/*
 * this is used for calling x_escape() in complete_word()
 */
static int
x_vi_putbuf(const char *s, size_t len)
{
	return (putbuf(s, len, 0));
}

static int
putbuf(const char *buf, int len, int repl)
{
	if (len == 0)
		return (0);
	if (repl) {
		if (es->cursor + len >= es->cbufsize)
			return (-1);
		if (es->cursor + len > es->linelen)
			es->linelen = es->cursor + len;
	} else {
		if (es->linelen + len >= es->cbufsize)
			return (-1);
		memmove(&es->cbuf[es->cursor + len], &es->cbuf[es->cursor],
		    es->linelen - es->cursor);
		es->linelen += len;
	}
	memmove(&es->cbuf[es->cursor], buf, len);
	es->cursor += len;
	return (0);
}

static void
del_range(int a, int b)
{
	if (es->linelen != b)
		memmove(&es->cbuf[a], &es->cbuf[b], es->linelen - b);
	es->linelen -= b - a;
}

static int
findch(int ch, int cnt, int forw, int incl)
{
	int ncursor;

	if (es->linelen == 0)
		return (-1);
	ncursor = es->cursor;
	while (cnt--) {
		do {
			if (forw) {
				if (++ncursor == es->linelen)
					return (-1);
			} else {
				if (--ncursor < 0)
					return (-1);
			}
		} while (es->cbuf[ncursor] != ch);
	}
	if (!incl) {
		if (forw)
			ncursor--;
		else
			ncursor++;
	}
	return (ncursor);
}

static int
forwword(int argcnt)
{
	int ncursor;

	ncursor = es->cursor;
	while (ncursor < es->linelen && argcnt--) {
		if (ksh_isalnux(es->cbuf[ncursor]))
			while (ksh_isalnux(es->cbuf[ncursor]) &&
			    ncursor < es->linelen)
				ncursor++;
		else if (!ksh_isspace(es->cbuf[ncursor]))
			while (!ksh_isalnux(es->cbuf[ncursor]) &&
			    !ksh_isspace(es->cbuf[ncursor]) &&
			    ncursor < es->linelen)
				ncursor++;
		while (ksh_isspace(es->cbuf[ncursor]) &&
		    ncursor < es->linelen)
			ncursor++;
	}
	return (ncursor);
}

static int
backword(int argcnt)
{
	int ncursor;

	ncursor = es->cursor;
	while (ncursor > 0 && argcnt--) {
		while (--ncursor > 0 && ksh_isspace(es->cbuf[ncursor]))
			;
		if (ncursor > 0) {
			if (ksh_isalnux(es->cbuf[ncursor]))
				while (--ncursor >= 0 &&
				    ksh_isalnux(es->cbuf[ncursor]))
					;
			else
				while (--ncursor >= 0 &&
				    !ksh_isalnux(es->cbuf[ncursor]) &&
				    !ksh_isspace(es->cbuf[ncursor]))
					;
			ncursor++;
		}
	}
	return (ncursor);
}

static int
endword(int argcnt)
{
	int ncursor;

	ncursor = es->cursor;
	while (ncursor < es->linelen && argcnt--) {
		while (++ncursor < es->linelen - 1 &&
		    ksh_isspace(es->cbuf[ncursor]))
			;
		if (ncursor < es->linelen - 1) {
			if (ksh_isalnux(es->cbuf[ncursor]))
				while (++ncursor < es->linelen &&
				    ksh_isalnux(es->cbuf[ncursor]))
					;
			else
				while (++ncursor < es->linelen &&
				    !ksh_isalnux(es->cbuf[ncursor]) &&
				    !ksh_isspace(es->cbuf[ncursor]))
					;
			ncursor--;
		}
	}
	return (ncursor);
}

static int
Forwword(int argcnt)
{
	int ncursor;

	ncursor = es->cursor;
	while (ncursor < es->linelen && argcnt--) {
		while (!ksh_isspace(es->cbuf[ncursor]) &&
		    ncursor < es->linelen)
			ncursor++;
		while (ksh_isspace(es->cbuf[ncursor]) &&
		    ncursor < es->linelen)
			ncursor++;
	}
	return (ncursor);
}

static int
Backword(int argcnt)
{
	int ncursor;

	ncursor = es->cursor;
	while (ncursor > 0 && argcnt--) {
		while (--ncursor >= 0 && ksh_isspace(es->cbuf[ncursor]))
			;
		while (ncursor >= 0 && !ksh_isspace(es->cbuf[ncursor]))
			ncursor--;
		ncursor++;
	}
	return (ncursor);
}

static int
Endword(int argcnt)
{
	int ncursor;

	ncursor = es->cursor;
	while (ncursor < es->linelen - 1 && argcnt--) {
		while (++ncursor < es->linelen - 1 &&
		    ksh_isspace(es->cbuf[ncursor]))
			;
		if (ncursor < es->linelen - 1) {
			while (++ncursor < es->linelen &&
			    !ksh_isspace(es->cbuf[ncursor]))
				;
			ncursor--;
		}
	}
	return (ncursor);
}

static int
grabhist(int save, int n)
{
	char *hptr;

	if (n < 0 || n > hlast)
		return (-1);
	if (n == hlast) {
		restore_cbuf();
		ohnum = n;
		return (0);
	}
	(void)histnum(n);
	if ((hptr = *histpos()) == NULL) {
		internal_warningf("grabhist: bad history array");
		return (-1);
	}
	if (save)
		save_cbuf();
	if ((es->linelen = strlen(hptr)) >= es->cbufsize)
		es->linelen = es->cbufsize - 1;
	memmove(es->cbuf, hptr, es->linelen);
	es->cursor = 0;
	ohnum = n;
	return (0);
}

static int
grabsearch(int save, int start, int fwd, char *pat)
{
	char *hptr;
	int hist;
	int anchored;

	if ((start == 0 && fwd == 0) || (start >= hlast - 1 && fwd == 1))
		return (-1);
	if (fwd)
		start++;
	else
		start--;
	anchored = *pat == '^' ? (++pat, 1) : 0;
	if ((hist = findhist(start, fwd, pat, anchored)) < 0) {
		/* if (start != 0 && fwd && match(holdbuf, pat) >= 0) { */
		/* XXX should strcmp be strncmp? */
		if (start != 0 && fwd && strcmp(holdbuf, pat) >= 0) {
			restore_cbuf();
			return (0);
		} else
			return (-1);
	}
	if (save)
		save_cbuf();
	histnum(hist);
	hptr = *histpos();
	if ((es->linelen = strlen(hptr)) >= es->cbufsize)
		es->linelen = es->cbufsize - 1;
	memmove(es->cbuf, hptr, es->linelen);
	es->cursor = 0;
	return (hist);
}

static void
redraw_line(int newl)
{
	(void)memset(wbuf[win], ' ', wbuf_len);
	if (newl) {
		x_putc('\r');
		x_putc('\n');
	}
	if (prompt_redraw)
		pprompt(prompt, prompt_trunc);
	cur_col = pwidth;
	morec = ' ';
}

static void
refresh(int leftside)
{
	if (leftside < 0)
		leftside = lastref;
	else
		lastref = leftside;
	if (outofwin())
		rewindow();
	display(wbuf[1 - win], wbuf[win], leftside);
	win = 1 - win;
}

static int
outofwin(void)
{
	int cur, col;

	if (es->cursor < es->winleft)
		return (1);
	col = 0;
	cur = es->winleft;
	while (cur < es->cursor)
		col = newcol((unsigned char)es->cbuf[cur++], col);
	if (col >= winwidth)
		return (1);
	return (0);
}

static void
rewindow(void)
{
	int tcur, tcol;
	int holdcur1, holdcol1;
	int holdcur2, holdcol2;

	holdcur1 = holdcur2 = tcur = 0;
	holdcol1 = holdcol2 = tcol = 0;
	while (tcur < es->cursor) {
		if (tcol - holdcol2 > winwidth / 2) {
			holdcur1 = holdcur2;
			holdcol1 = holdcol2;
			holdcur2 = tcur;
			holdcol2 = tcol;
		}
		tcol = newcol((unsigned char)es->cbuf[tcur++], tcol);
	}
	while (tcol - holdcol1 > winwidth / 2)
		holdcol1 = newcol((unsigned char)es->cbuf[holdcur1++],
		    holdcol1);
	es->winleft = holdcur1;
}

static int
newcol(int ch, int col)
{
	if (ch == '\t')
		return ((col | 7) + 1);
	return (col + char_len(ch));
}

static void
display(char *wb1, char *wb2, int leftside)
{
	unsigned char ch;
	char *twb1, *twb2, mc;
	int cur, col, cnt;
	int ncol = 0;
	int moreright;

	col = 0;
	cur = es->winleft;
	moreright = 0;
	twb1 = wb1;
	while (col < winwidth && cur < es->linelen) {
		if (cur == es->cursor && leftside)
			ncol = col + pwidth;
		if ((ch = es->cbuf[cur]) == '\t')
			do {
				*twb1++ = ' ';
			} while (++col < winwidth && (col & 7) != 0);
		else if (col < winwidth) {
			if (ch < ' ' || ch == 0x7f) {
				*twb1++ = '^';
				if (++col < winwidth) {
					*twb1++ = ch ^ '@';
					col++;
				}
			} else {
				*twb1++ = ch;
				col++;
			}
		}
		if (cur == es->cursor && !leftside)
			ncol = col + pwidth - 1;
		cur++;
	}
	if (cur == es->cursor)
		ncol = col + pwidth;
	if (col < winwidth) {
		while (col < winwidth) {
			*twb1++ = ' ';
			col++;
		}
	} else
		moreright++;
	*twb1 = ' ';

	col = pwidth;
	cnt = winwidth;
	twb1 = wb1;
	twb2 = wb2;
	while (cnt--) {
		if (*twb1 != *twb2) {
			if (cur_col != col)
				ed_mov_opt(col, wb1);
			x_putc(*twb1);
			cur_col++;
		}
		twb1++;
		twb2++;
		col++;
	}
	if (es->winleft > 0 && moreright)
		/* POSIX says to use * for this but that is a globbing
		 * character and may confuse people; + is more innocuous
		 */
		mc = '+';
	else if (es->winleft > 0)
		mc = '<';
	else if (moreright)
		mc = '>';
	else
		mc = ' ';
	if (mc != morec) {
		ed_mov_opt(pwidth + winwidth + 1, wb1);
		x_putc(mc);
		cur_col++;
		morec = mc;
	}
	if (cur_col != ncol)
		ed_mov_opt(ncol, wb1);
}

static void
ed_mov_opt(int col, char *wb)
{
	if (col < cur_col) {
		if (col + 1 < cur_col - col) {
			x_putc('\r');
			if (prompt_redraw)
				pprompt(prompt, prompt_trunc);
			cur_col = pwidth;
			while (cur_col++ < col)
				x_putcf(*wb++);
		} else {
			while (cur_col-- > col)
				x_putc('\b');
		}
	} else {
		wb = &wb[cur_col - pwidth];
		while (cur_col++ < col)
			x_putcf(*wb++);
	}
	cur_col = col;
}


/* replace word with all expansions (ie, expand word*) */
static int
expand_word(int cmd)
{
	static struct edstate *buf;
	int rval = 0;
	int nwords;
	int start, end;
	char **words;
	int i;

	/* Undo previous expansion */
	if (cmd == 0 && expanded == EXPAND && buf) {
		restore_edstate(es, buf);
		buf = 0;
		expanded = NONE;
		return (0);
	}
	if (buf) {
		free_edstate(buf);
		buf = 0;
	}

	nwords = x_cf_glob(XCF_COMMAND_FILE|XCF_FULLPATH,
	    es->cbuf, es->linelen, es->cursor,
	    &start, &end, &words, NULL);
	if (nwords == 0) {
		vi_error();
		return (-1);
	}

	buf = save_edstate(es);
	expanded = EXPAND;
	del_range(start, end);
	es->cursor = start;
	for (i = 0; i < nwords; ) {
		if (x_escape(words[i], strlen(words[i]), x_vi_putbuf) != 0) {
			rval = -1;
			break;
		}
		if (++i < nwords && putbuf(" ", 1, 0) != 0) {
			rval = -1;
			break;
		}
	}
	i = buf->cursor - end;
	if (rval == 0 && i > 0)
		es->cursor += i;
	modified = 1;
	hnum = hlast;
	insert = INSERT;
	lastac = 0;
	refresh(0);
	return (rval);
}

static int
complete_word(int cmd, int count)
{
	static struct edstate *buf;
	int rval, nwords, start, end, match_len;
	char **words;
	char *match;
	bool is_command, is_unique;

	/* Undo previous completion */
	if (cmd == 0 && expanded == COMPLETE && buf) {
		print_expansions(buf, 0);
		expanded = PRINT;
		return (0);
	}
	if (cmd == 0 && expanded == PRINT && buf) {
		restore_edstate(es, buf);
		buf = 0;
		expanded = NONE;
		return (0);
	}
	if (buf) {
		free_edstate(buf);
		buf = 0;
	}

	/* XCF_FULLPATH for count 'cause the menu printed by print_expansions()
	 * was done this way.
	 */
	nwords = x_cf_glob(XCF_COMMAND_FILE | (count ? XCF_FULLPATH : 0),
	    es->cbuf, es->linelen, es->cursor,
	    &start, &end, &words, &is_command);
	if (nwords == 0) {
		vi_error();
		return (-1);
	}
	if (count) {
		int i;

		count--;
		if (count >= nwords) {
			vi_error();
			x_print_expansions(nwords, words, is_command);
			x_free_words(nwords, words);
			redraw_line(0);
			return (-1);
		}
		/*
		 * Expand the count'th word to its basename
		 */
		if (is_command) {
			match = words[count] +
			    x_basename(words[count], NULL);
			/* If more than one possible match, use full path */
			for (i = 0; i < nwords; i++)
				if (i != count &&
				    strcmp(words[i] + x_basename(words[i],
				    NULL), match) == 0) {
					match = words[count];
					break;
				}
		} else
			match = words[count];
		match_len = strlen(match);
		is_unique = true;
		/* expanded = PRINT;	next call undo */
	} else {
		match = words[0];
		match_len = x_longest_prefix(nwords, words);
		expanded = COMPLETE;	/* next call will list completions */
		is_unique = nwords == 1;
	}

	buf = save_edstate(es);
	del_range(start, end);
	es->cursor = start;

	/* escape all shell-sensitive characters and put the result into
	 * command buffer */
	rval = x_escape(match, match_len, x_vi_putbuf);

	if (rval == 0 && is_unique) {
		/* If exact match, don't undo. Allows directory completions
		 * to be used (ie, complete the next portion of the path).
		 */
		expanded = NONE;

		/* If not a directory, add a space to the end... */
		if (match_len > 0 && match[match_len - 1] != '/')
			rval = putbuf(" ", 1, 0);
	}
	x_free_words(nwords, words);

	modified = 1;
	hnum = hlast;
	insert = INSERT;
	lastac = 0;	 /* prevent this from being redone... */
	refresh(0);

	return (rval);
}

static int
print_expansions(struct edstate *est, int cmd MKSH_A_UNUSED)
{
	int start, end, nwords;
	char **words;
	bool is_command;

	nwords = x_cf_glob(XCF_COMMAND_FILE | XCF_FULLPATH,
	    est->cbuf, est->linelen, est->cursor,
	    &start, &end, &words, &is_command);
	if (nwords == 0) {
		vi_error();
		return (-1);
	}
	x_print_expansions(nwords, words, is_command);
	x_free_words(nwords, words);
	redraw_line(0);
	return (0);
}

/* Similar to x_zotc(emacs.c), but no tab weirdness */
static void
x_vi_zotc(int c)
{
	if (c < ' ' || c == 0x7f) {
		x_putc('^');
		c ^= '@';
	}
	x_putc(c);
}

static void
vi_error(void)
{
	/* Beem out of any macros as soon as an error occurs */
	vi_macro_reset();
	x_putc(7);
	x_flush();
}

static void
vi_macro_reset(void)
{
	if (macro.p) {
		afree(macro.buf, APERM);
		memset((char *)&macro, 0, sizeof(macro));
	}
}
#endif /* !MKSH_S_NOVI */
