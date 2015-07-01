/*	$OpenBSD: vi.c,v 1.26 2009/06/29 22:50:19 martynas Exp $	*/

/*-
 * Copyright (c) 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010
 *	Thorsten Glaser <tg@mirbsd.org>
 *
 * Provided that these terms and disclaimer and all copyright notices
 * are retained or reproduced in an accompanying document, permission
 * is granted to deal in this work without restriction, including un-

#define x_flush()	shf_flush(shl_out)
#ifdef MKSH_SMALL
#define x_putc(c)	x_putcf(c)
#else
#define x_putc(c)	shf_putc((c), shl_out)
#endif

	return (nwords);
}

#define IS_WORDC(c)	(!ctype(c, C_LEX1) && (c) != '\'' && (c) != '"' && \
			    (c) != '`' && (c) != '=' && (c) != ':')

static int
#define	XF_PREFIX	4	/* function sets prefix */

/* Separator for completion */
#define	is_cfs(c)	((c) == ' ' || (c) == '\t' || (c) == '"' || (c) == '\'')
/* Separator for motion */
#define	is_mfs(c)	(!(ksh_isalnux(c) || (c) == '$' || ((c) & 0x80)))

#define X_NTABS		3			/* normal, meta1, meta2 */
			if (c == -1)
				return (-1);
			if ((c & 0xC0) != 0x80) {
				x_e_ungetc(c);
				return (1);
			}
		x_e_puts("    ");
	} else if (c < ' ' || c == 0x7f) {
		x_e_putc2('^');
		x_e_putc2(UNCTRL(c));
	} else
		x_e_putc2(c);
}

		(*cp)++;
	} else if (c < ' ' || c == 0x7f) {
		x_e_putc2('^');
		x_e_putc2(UNCTRL(c));
		(*cp)++;
	} else
x_eot_del(int c)
{
	if (xep == xbuf && x_arg_defaulted)
		return (x_end_of_text(c));
	else
		return (x_del_char(c));
}

				f = x_tab[1][c] & 0x7F;
				if (f == XFUNC_meta1 || f == XFUNC_meta2)
					x_meta1(CTRL('['));
				x_e_ungetc(c);
			}
			break;
		if (f & 0x80) {
			f &= 0x7F;
			if ((c = x_e_getc()) != '~')
				x_e_ungetc(c);
		}
#endif
				x_load_hist(histptr + 1);
			break;
		} else { /* other command */
			x_e_ungetc(c);
			break;
		}
static int
x_abort(int c MKSH_A_UNUSED)
{
	/* x_zotc(c); */
	xlp = xep = xcp = xbp = xbuf;
	xlp_valid = true;
{
	/* we only support PF2-'1' for now */
	if (c != (2 << 8 | '1'))
		return (x_error(c));

	/* what's the next character? */

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

	if (c < ' ' || c == 0x7f) {
		*p++ = '^';
		*p++ = UNCTRL(c);
	} else
		*p++ = c;
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
				x_putc(utf_tmp[1]);
			if (x > 2)
				x_putc(utf_tmp[2]);
			width = utf_wcwidth(c);
		} else
			x_putc(c);
		switch (c) {
		case 7:
			break;
				x_putcf(*(*cp)++);
		} else {
			(*cp)++;
			x_putc(c);
		}
		switch (c) {
		case 7:
			break;
	int n = 0, first = 1;

	c &= 255;	/* strip command prefix */
	for (; c >= 0 && ksh_isdigit(c); c = x_e_getc(), first = 0)
		n = n * 10 + (c - '0');
	if (c < 0 || first) {
		x_arg = 1;
		x_arg_defaulted = 1;
	} else {
		x_e_ungetc(c);
		x_arg = n;
		x_arg_defaulted = 0;
		return (KSTD);
	/* This is what AT&T ksh seems to do... Very bizarre */
	if (c != ' ')
		x_e_ungetc(c);

	afree(v, ATEMP);
#if !MKSH_S_NOVI
/* +++ vi editing mode +++ */

#define Ctrl(c)		(c&0x1f)

struct edstate {
static int expand_word(int);
static int complete_word(int, int);
static int print_expansions(struct edstate *, int);
#define char_len(c)	((c) < ' ' || (c) == 0x7F ? 2 : 1)
static void x_vi_zotc(int);
static void vi_error(void);
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
		if (state != VLIT) {
			if (c == edchars.intr || c == edchars.quit) {
				/* pretend we got an interrupt */
				x_vi_zotc(c);
				x_flush();
				trapsig(c == edchars.intr ? SIGINT : SIGQUIT);
				continue;
			}
		}
		if (vi_hook(c))
			break;
		x_flush();
				if (histnum(-1) < 0)
					return (-1);
				p = *histpos();
#define issp(c)		(ksh_isspace(c) || (c) == '\n')
				if (argcnt) {
					while (*p && issp(*p))
		x_putc('^');
		c ^= '@';
	}
	x_putc(c);
}
