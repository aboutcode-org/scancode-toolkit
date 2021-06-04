/* vi: set sw=4 ts=4: */
/*
 * ash shell port for busybox
 *
 * Copyright (c) 1989, 1991, 1993, 1994
 *      The Regents of the University of California.  All rights reserved.
 *
 * Copyright (c) 1997-2005 Herbert Xu <herbert@gondor.apana.org.au>
 * was re-ported from NetBSD and debianized.
 *
 *
 * This code is derived from software contributed to Berkeley by
 * Kenneth Almquist.
 *
 * Licensed under the GPL v2 or later, see the file LICENSE in this tarball.
 *
 * Original BSD copyright notice is retained at the end of this file.
 */

/*
 * rewrite arith.y to micro stack based cryptic algorithm by
 * Copyright (c) 2001 Aaron Lehmann <aaronl@vitelus.com>
 *
 * Modified by Paul Mundt <lethal@linux-sh.org> (c) 2004 to support
 * dynamic variables.
 *
 * Modified by Vladimir Oleynik <dzo@simtreas.ru> (c) 2001-2005 to be
 * used in busybox and size optimizations,
 * rewrote arith (see notes to this), added locale support,
 * rewrote dynamic variables.
 *
 */


/*
 * The follow should be set to reflect the type of system you have:
 *      JOBS -> 1 if you have Berkeley job control, 0 otherwise.
 *      define SYSV if you are running under System V.
 *      define DEBUG=1 to compile in debugging ('set -o debug' to turn on)
 *      define DEBUG=2 to compile in and turn on debugging.
 *
 * When debugging is on, debugging info will be written to ./trace and
 * a quit signal will generate a core dump.
 */


#define IFS_BROKEN

#define PROFILE 0

#include "busybox.h"

#ifdef DEBUG
#define _GNU_SOURCE
#endif

#include <sys/types.h>
#include <sys/ioctl.h>
#include <sys/param.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <sys/wait.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <stdarg.h>
#include <stddef.h>
#include <assert.h>
#include <ctype.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <paths.h>
#include <setjmp.h>
#include <signal.h>
/*#include <stdint.h>*/
#include <time.h>
#include <fnmatch.h>

#include "pwd_.h"

#ifdef CONFIG_ASH_JOB_CONTROL
#define JOBS 1
#else
#undef JOBS
#endif

#if JOBS || defined(CONFIG_ASH_READ_NCHARS)
#include <termios.h>
#endif

#include "cmdedit.h"

#ifdef __GLIBC__
/* glibc sucks */
static int *dash_errno;
#undef errno
#define errno (*dash_errno)
#endif

#if defined(__uClinux__)
#error "Do not even bother, ash will not run on uClinux"
#endif

#ifdef DEBUG
#define _DIAGASSERT(assert_expr) assert(assert_expr)
#else
#define _DIAGASSERT(assert_expr)
#endif


#ifdef CONFIG_ASH_ALIAS
/*      alias.h       */

#define ALIASINUSE      1
#define ALIASDEAD       2

struct alias {
	struct alias *next;
	char *name;
	char *val;
	int flag;
};

static struct alias *lookupalias(const char *, int);
static int aliascmd(int, char **);
static int unaliascmd(int, char **);
static void rmaliases(void);
static int unalias(const char *);
static void printalias(const struct alias *);
#endif

/*      cd.h  */


static void    setpwd(const char *, int);

/*      error.h      */


/*
 * Types of operations (passed to the errmsg routine).
 */


static const char not_found_msg[] = "%s: not found";


#define E_OPEN  "No such file"          /* opening a file */
#define E_CREAT "Directory nonexistent" /* creating a file */
#define E_EXEC  not_found_msg+4         /* executing a program */

/*
 * We enclose jmp_buf in a structure so that we can declare pointers to
 * jump locations.  The global variable handler contains the location to
 * jump to when an exception occurs, and the global variable exception
 * contains a code identifying the exception.  To implement nested
 * exception handlers, the user should save the value of handler on entry
 * to an inner scope, set handler to point to a jmploc structure for the
 * inner scope, and restore handler on exit from the scope.
 */

struct jmploc {
	jmp_buf loc;
};

static struct jmploc *handler;
static int exception;
static volatile int suppressint;
static volatile sig_atomic_t intpending;

/* exceptions */
#define EXINT 0         /* SIGINT received */
#define EXERROR 1       /* a generic error */
#define EXSHELLPROC 2   /* execute a shell procedure */
#define EXEXEC 3        /* command execution failed */
#define EXEXIT 4        /* exit the shell */
#define EXSIG 5         /* trapped signal in wait(1) */


/* do we generate EXSIG events */
static int exsig;
/* last pending signal */
static volatile sig_atomic_t pendingsigs;

/*
 * These macros allow the user to suspend the handling of interrupt signals
 * over a period of time.  This is similar to SIGHOLD to or sigblock, but
 * much more efficient and portable.  (But hacking the kernel is so much
 * more fun than worrying about efficiency and portability. :-))
 */

#define xbarrier() ({ __asm__ __volatile__ ("": : :"memory"); })
#define INTOFF \
	({ \
		suppressint++; \
		xbarrier(); \
		0; \
	})
#define SAVEINT(v) ((v) = suppressint)
#define RESTOREINT(v) \
	({ \
		xbarrier(); \
		if ((suppressint = (v)) == 0 && intpending) onint(); \
		0; \
	})
#define EXSIGON() \
	({ \
		exsig++; \
		xbarrier(); \
		if (pendingsigs) \
			exraise(EXSIG); \
		0; \
	})
/* EXSIG is turned off by evalbltin(). */


static void exraise(int) ATTRIBUTE_NORETURN;
static void onint(void) ATTRIBUTE_NORETURN;

static void sh_error(const char *, ...) ATTRIBUTE_NORETURN;
static void exerror(int, const char *, ...) ATTRIBUTE_NORETURN;

static void sh_warnx(const char *, ...);

#ifdef CONFIG_ASH_OPTIMIZE_FOR_SIZE
static void
inton(void) {
	if (--suppressint == 0 && intpending) {
		onint();
	}
}
#define INTON inton()
static void forceinton(void)
{
	suppressint = 0;
	if (intpending)
		onint();
}
#define FORCEINTON forceinton()
#else
#define INTON \
	({ \
		xbarrier(); \
		if (--suppressint == 0 && intpending) onint(); \
		0; \
	})
#define FORCEINTON \
	({ \
		xbarrier(); \
		suppressint = 0; \
		if (intpending) onint(); \
		0; \
	})
#endif /* CONFIG_ASH_OPTIMIZE_FOR_SIZE */

/*      expand.h     */

struct strlist {
	struct strlist *next;
	char *text;
};


struct arglist {
	struct strlist *list;
	struct strlist **lastp;
};

/*
 * expandarg() flags
 */
#define EXP_FULL        0x1     /* perform word splitting & file globbing */
#define EXP_TILDE       0x2     /* do normal tilde expansion */
#define EXP_VARTILDE    0x4     /* expand tildes in an assignment */
#define EXP_REDIR       0x8     /* file glob for a redirection (1 match only) */
#define EXP_CASE        0x10    /* keeps quotes around for CASE pattern */
#define EXP_RECORD      0x20    /* need to record arguments for ifs breakup */
#define EXP_VARTILDE2   0x40    /* expand tildes after colons only */
#define EXP_WORD        0x80    /* expand word in parameter expansion */
#define EXP_QWORD       0x100   /* expand word in quoted parameter expansion */


union node;
static void expandarg(union node *, struct arglist *, int);
#define rmescapes(p) _rmescapes((p), 0)
static char *_rmescapes(char *, int);
static int casematch(union node *, char *);

#ifdef CONFIG_ASH_MATH_SUPPORT
static void expari(int);
#endif

/*      eval.h       */

static char *commandname;              /* currently executing command */
static struct strlist *cmdenviron;     /* environment for builtin command */
static int exitstatus;                 /* exit status of last command */
static int back_exitstatus;            /* exit status of backquoted command */


struct backcmd {                /* result of evalbackcmd */
	int fd;                 /* file descriptor to read from */
	char *buf;              /* buffer */
	int nleft;              /* number of chars in buffer */
	struct job *jp;         /* job structure for command */
};

/*
 * This file was generated by the mknodes program.
 */

#define NCMD 0
#define NPIPE 1
#define NREDIR 2
#define NBACKGND 3
#define NSUBSHELL 4
#define NAND 5
#define NOR 6
#define NSEMI 7
#define NIF 8
#define NWHILE 9
#define NUNTIL 10
#define NFOR 11
#define NCASE 12
#define NCLIST 13
#define NDEFUN 14
#define NARG 15
#define NTO 16
#define NCLOBBER 17
#define NFROM 18
#define NFROMTO 19
#define NAPPEND 20
#define NTOFD 21
#define NFROMFD 22
#define NHERE 23
#define NXHERE 24
#define NNOT 25



struct ncmd {
      int type;
      union node *assign;
      union node *args;
      union node *redirect;
};


struct npipe {
      int type;
      int backgnd;
      struct nodelist *cmdlist;
};


struct nredir {
      int type;
      union node *n;
      union node *redirect;
};


struct nbinary {
      int type;
      union node *ch1;
      union node *ch2;
};


struct nif {
      int type;
      union node *test;
      union node *ifpart;
      union node *elsepart;
};


struct nfor {
      int type;
      union node *args;
      union node *body;
      char *var;
};


struct ncase {
      int type;
      union node *expr;
      union node *cases;
};


struct nclist {
      int type;
      union node *next;
      union node *pattern;
      union node *body;
};


struct narg {
      int type;
      union node *next;
      char *text;
      struct nodelist *backquote;
};


struct nfile {
      int type;
      union node *next;
      int fd;
      union node *fname;
      char *expfname;
};


struct ndup {
      int type;
      union node *next;
      int fd;
      int dupfd;
      union node *vname;
};


struct nhere {
      int type;
      union node *next;
      int fd;
      union node *doc;
};


struct nnot {
      int type;
      union node *com;
};


union node {
      int type;
      struct ncmd ncmd;
      struct npipe npipe;
      struct nredir nredir;
      struct nbinary nbinary;
      struct nif nif;
      struct nfor nfor;
      struct ncase ncase;
      struct nclist nclist;
      struct narg narg;
      struct nfile nfile;
      struct ndup ndup;
      struct nhere nhere;
      struct nnot nnot;
};


struct nodelist {
	struct nodelist *next;
	union node *n;
};


struct funcnode {
	int count;
	union node n;
};


static void freefunc(struct funcnode *);
/*      parser.h     */

/* control characters in argument strings */
#define CTL_FIRST '\201'        /* first 'special' character */
#define CTLESC '\201'           /* escape next character */
#define CTLVAR '\202'           /* variable defn */
#define CTLENDVAR '\203'
#define CTLBACKQ '\204'
#define CTLQUOTE 01             /* ored with CTLBACKQ code if in quotes */
/*      CTLBACKQ | CTLQUOTE == '\205' */
#define CTLARI  '\206'          /* arithmetic expression */
#define CTLENDARI '\207'
#define CTLQUOTEMARK '\210'
#define CTL_LAST '\210'         /* last 'special' character */

/* variable substitution byte (follows CTLVAR) */
#define VSTYPE  0x0f            /* type of variable substitution */
#define VSNUL   0x10            /* colon--treat the empty string as unset */
#define VSQUOTE 0x80            /* inside double quotes--suppress splitting */

/* values of VSTYPE field */
#define VSNORMAL        0x1             /* normal variable:  $var or ${var} */
#define VSMINUS         0x2             /* ${var-text} */
#define VSPLUS          0x3             /* ${var+text} */
#define VSQUESTION      0x4             /* ${var?message} */
#define VSASSIGN        0x5             /* ${var=text} */
#define VSTRIMRIGHT     0x6             /* ${var%pattern} */
#define VSTRIMRIGHTMAX  0x7             /* ${var%%pattern} */
#define VSTRIMLEFT      0x8             /* ${var#pattern} */
#define VSTRIMLEFTMAX   0x9             /* ${var##pattern} */
#define VSLENGTH        0xa             /* ${#var} */

/* values of checkkwd variable */
#define CHKALIAS        0x1
#define CHKKWD          0x2
#define CHKNL           0x4

#define IBUFSIZ (BUFSIZ + 1)

/*
 * NEOF is returned by parsecmd when it encounters an end of file.  It
 * must be distinct from NULL, so we use the address of a variable that
 * happens to be handy.
 */
static int plinno = 1;                  /* input line number */

/* number of characters left in input buffer */
static int parsenleft;                  /* copy of parsefile->nleft */
static int parselleft;                  /* copy of parsefile->lleft */

/* next character in input buffer */
static char *parsenextc;                /* copy of parsefile->nextc */

struct strpush {
	struct strpush *prev;   /* preceding string on stack */
	char *prevstring;
	int prevnleft;
#ifdef CONFIG_ASH_ALIAS
	struct alias *ap;       /* if push was associated with an alias */
#endif
	char *string;           /* remember the string since it may change */
};

struct parsefile {
	struct parsefile *prev; /* preceding file on stack */
	int linno;              /* current line */
	int fd;                 /* file descriptor (or -1 if string) */
	int nleft;              /* number of chars left in this line */
	int lleft;              /* number of chars left in this buffer */
	char *nextc;            /* next char in buffer */
	char *buf;              /* input buffer */
	struct strpush *strpush; /* for pushing strings at this level */
	struct strpush basestrpush; /* so pushing one is fast */
};

static struct parsefile basepf;         /* top level input file */
#define basebuf bb_common_bufsiz1       /* buffer for top level input file */
static struct parsefile *parsefile = &basepf;  /* current input file */


static int tokpushback;                 /* last token pushed back */
#define NEOF ((union node *)&tokpushback)
static int parsebackquote;             /* nonzero if we are inside backquotes */
static int doprompt;                   /* if set, prompt the user */
static int needprompt;                 /* true if interactive and at start of line */
static int lasttoken;                  /* last token read */
static char *wordtext;                 /* text of last word returned by readtoken */
static int checkkwd;
static struct nodelist *backquotelist;
static union node *redirnode;
static struct heredoc *heredoc;
static int quoteflag;                  /* set if (part of) last token was quoted */
static int startlinno;                 /* line # where last token started */

static union node *parsecmd(int);
static void fixredir(union node *, const char *, int);
static const char *const *findkwd(const char *);
static char *endofname(const char *);

/*      shell.h   */

typedef void *pointer;

static char nullstr[1];                /* zero length string */
static const char spcstr[] = " ";
static const char snlfmt[] = "%s\n";
static const char dolatstr[] = { CTLVAR, VSNORMAL|VSQUOTE, '@', '=', '\0' };
static const char illnum[] = "Illegal number: %s";
static const char homestr[] = "HOME";

#ifdef DEBUG
#define TRACE(param)    trace param
#define TRACEV(param)   tracev param
#else
#define TRACE(param)
#define TRACEV(param)
#endif

#if !defined(__GNUC__) || (__GNUC__ == 2 && __GNUC_MINOR__ < 96)
#define __builtin_expect(x, expected_value) (x)
#endif

#define xlikely(x)       __builtin_expect((x),1)


#define TEOF 0
#define TNL 1
#define TREDIR 2
#define TWORD 3
#define TSEMI 4
#define TBACKGND 5
#define TAND 6
#define TOR 7
#define TPIPE 8
#define TLP 9
#define TRP 10
#define TENDCASE 11
#define TENDBQUOTE 12
#define TNOT 13
#define TCASE 14
#define TDO 15
#define TDONE 16
#define TELIF 17
#define TELSE 18
#define TESAC 19
#define TFI 20
#define TFOR 21
#define TIF 22
#define TIN 23
#define TTHEN 24
#define TUNTIL 25
#define TWHILE 26
#define TBEGIN 27
#define TEND 28

/* first char is indicating which tokens mark the end of a list */
static const char *const tokname_array[] = {
	"\1end of file",
	"\0newline",
	"\0redirection",
	"\0word",
	"\0;",
	"\0&",
	"\0&&",
	"\0||",
	"\0|",
	"\0(",
	"\1)",
	"\1;;",
	"\1`",
#define KWDOFFSET 13
	/* the following are keywords */
	"\0!",
	"\0case",
	"\1do",
	"\1done",
	"\1elif",
	"\1else",
	"\1esac",
	"\1fi",
	"\0for",
	"\0if",
	"\0in",
	"\1then",
	"\0until",
	"\0while",
	"\0{",
	"\1}",
};

static const char *tokname(int tok)
{
	static char buf[16];

	if (tok >= TSEMI)
		buf[0] = '"';
	sprintf(buf + (tok >= TSEMI), "%s%c",
			tokname_array[tok] + 1, (tok >= TSEMI ? '"' : 0));
	return buf;
}

/*      machdep.h    */

/*
 * Most machines require the value returned from malloc to be aligned
 * in some way.  The following macro will get this right on many machines.
 */

#define SHELL_SIZE (sizeof(union {int i; char *cp; double d; }) - 1)
/*
 * It appears that grabstackstr() will barf with such alignments
 * because stalloc() will return a string allocated in a new stackblock.
 */
#define SHELL_ALIGN(nbytes) (((nbytes) + SHELL_SIZE) & ~SHELL_SIZE)

/*
 * This file was generated by the mksyntax program.
 */


/* Syntax classes */
#define CWORD 0                 /* character is nothing special */
#define CNL 1                   /* newline character */
#define CBACK 2                 /* a backslash character */
#define CSQUOTE 3               /* single quote */
#define CDQUOTE 4               /* double quote */
#define CENDQUOTE 5             /* a terminating quote */
#define CBQUOTE 6               /* backwards single quote */
#define CVAR 7                  /* a dollar sign */
#define CENDVAR 8               /* a '}' character */
#define CLP 9                   /* a left paren in arithmetic */
#define CRP 10                  /* a right paren in arithmetic */
#define CENDFILE 11             /* end of file */
#define CCTL 12                 /* like CWORD, except it must be escaped */
#define CSPCL 13                /* these terminate a word */
#define CIGN 14                 /* character should be ignored */

#ifdef CONFIG_ASH_ALIAS
#define SYNBASE 130
#define PEOF -130
#define PEOA -129
#define PEOA_OR_PEOF PEOA
#else
#define SYNBASE 129
#define PEOF -129
#define PEOA_OR_PEOF PEOF
#endif

#define is_digit(c)     ((unsigned)((c) - '0') <= 9)
#define is_name(c)      ((c) == '_' || isalpha((unsigned char)(c)))
#define is_in_name(c)   ((c) == '_' || isalnum((unsigned char)(c)))

/* C99 say: "char" declaration may be signed or unsigned default */
#define SC2INT(chr2may_be_negative_int) (int)((signed char)chr2may_be_negative_int)

/*
 * is_special(c) evaluates to 1 for c in "!#$*-0123456789?@"; 0 otherwise
 * (assuming ascii char codes, as the original implementation did)
 */
#define is_special(c) \
    ( (((unsigned int)c) - 33 < 32) \
			 && ((0xc1ff920dUL >> (((unsigned int)c) - 33)) & 1))

#define digit_val(c)    ((c) - '0')

/*
 * This file was generated by the mksyntax program.
 */

#ifdef CONFIG_ASH_OPTIMIZE_FOR_SIZE
#define USE_SIT_FUNCTION
#endif

/* number syntax index */
#define  BASESYNTAX  0  /* not in quotes */
#define  DQSYNTAX    1  /* in double quotes */
#define  SQSYNTAX    2  /* in single quotes */
#define  ARISYNTAX   3  /* in arithmetic */

#ifdef CONFIG_ASH_MATH_SUPPORT
static const char S_I_T[][4] = {
#ifdef CONFIG_ASH_ALIAS
	{CSPCL, CIGN, CIGN, CIGN},              /* 0, PEOA */
#endif
	{CSPCL, CWORD, CWORD, CWORD},           /* 1, ' ' */
	{CNL, CNL, CNL, CNL},                   /* 2, \n */
	{CWORD, CCTL, CCTL, CWORD},             /* 3, !*-/:=?[]~ */
	{CDQUOTE, CENDQUOTE, CWORD, CWORD},     /* 4, '"' */
	{CVAR, CVAR, CWORD, CVAR},              /* 5, $ */
	{CSQUOTE, CWORD, CENDQUOTE, CWORD},     /* 6, "'" */
	{CSPCL, CWORD, CWORD, CLP},             /* 7, ( */
	{CSPCL, CWORD, CWORD, CRP},             /* 8, ) */
	{CBACK, CBACK, CCTL, CBACK},            /* 9, \ */
	{CBQUOTE, CBQUOTE, CWORD, CBQUOTE},     /* 10, ` */
	{CENDVAR, CENDVAR, CWORD, CENDVAR},     /* 11, } */
#ifndef USE_SIT_FUNCTION
	{CENDFILE, CENDFILE, CENDFILE, CENDFILE},       /* 12, PEOF */
	{CWORD, CWORD, CWORD, CWORD},           /* 13, 0-9A-Za-z */
	{CCTL, CCTL, CCTL, CCTL}                /* 14, CTLESC ... */
#endif
};
#else
static const char S_I_T[][3] = {
#ifdef CONFIG_ASH_ALIAS
	{CSPCL, CIGN, CIGN},                    /* 0, PEOA */
#endif
	{CSPCL, CWORD, CWORD},                  /* 1, ' ' */
	{CNL, CNL, CNL},                        /* 2, \n */
	{CWORD, CCTL, CCTL},                    /* 3, !*-/:=?[]~ */
	{CDQUOTE, CENDQUOTE, CWORD},            /* 4, '"' */
	{CVAR, CVAR, CWORD},                    /* 5, $ */
	{CSQUOTE, CWORD, CENDQUOTE},            /* 6, "'" */
	{CSPCL, CWORD, CWORD},                  /* 7, ( */
	{CSPCL, CWORD, CWORD},                  /* 8, ) */
	{CBACK, CBACK, CCTL},                   /* 9, \ */
	{CBQUOTE, CBQUOTE, CWORD},              /* 10, ` */
	{CENDVAR, CENDVAR, CWORD},              /* 11, } */
#ifndef USE_SIT_FUNCTION
	{CENDFILE, CENDFILE, CENDFILE},         /* 12, PEOF */
	{CWORD, CWORD, CWORD},                  /* 13, 0-9A-Za-z */
	{CCTL, CCTL, CCTL}                      /* 14, CTLESC ... */
#endif
};
#endif /* CONFIG_ASH_MATH_SUPPORT */

#ifdef USE_SIT_FUNCTION

#define U_C(c) ((unsigned char)(c))

static int SIT(int c, int syntax)
{
	static const char spec_symbls[] = "\t\n !\"$&'()*-/:;<=>?[\\]`|}~";
#ifdef CONFIG_ASH_ALIAS
	static const char syntax_index_table[] = {
		1, 2, 1, 3, 4, 5, 1, 6,         /* "\t\n !\"$&'" */
		7, 8, 3, 3, 3, 3, 1, 1,         /* "()*-/:;<" */
		3, 1, 3, 3, 9, 3, 10, 1,        /* "=>?[\\]`|" */
		11, 3                           /* "}~" */
	};
#else
	static const char syntax_index_table[] = {
		0, 1, 0, 2, 3, 4, 0, 5,         /* "\t\n !\"$&'" */
		6, 7, 2, 2, 2, 2, 0, 0,         /* "()*-/:;<" */
		2, 0, 2, 2, 8, 2, 9, 0,         /* "=>?[\\]`|" */
		10, 2                           /* "}~" */
	};
#endif
	const char *s;
	int indx;

	if (c == PEOF)          /* 2^8+2 */
		return CENDFILE;
#ifdef CONFIG_ASH_ALIAS
	if (c == PEOA)          /* 2^8+1 */
		indx = 0;
	else
#endif
		if (U_C(c) >= U_C(CTLESC) && U_C(c) <= U_C(CTLQUOTEMARK))
			return CCTL;
	else {
		s = strchr(spec_symbls, c);
		if (s == 0 || *s == 0)
			return CWORD;
		indx = syntax_index_table[(s - spec_symbls)];
	}
	return S_I_T[indx][syntax];
}

#else   /* USE_SIT_FUNCTION */

#define SIT(c, syntax) S_I_T[(int)syntax_index_table[((int)c)+SYNBASE]][syntax]

#ifdef CONFIG_ASH_ALIAS
#define CSPCL_CIGN_CIGN_CIGN                           0
#define CSPCL_CWORD_CWORD_CWORD                        1
#define CNL_CNL_CNL_CNL                                2
#define CWORD_CCTL_CCTL_CWORD                          3
#define CDQUOTE_CENDQUOTE_CWORD_CWORD                  4
#define CVAR_CVAR_CWORD_CVAR                           5
#define CSQUOTE_CWORD_CENDQUOTE_CWORD                  6
#define CSPCL_CWORD_CWORD_CLP                          7
#define CSPCL_CWORD_CWORD_CRP                          8
#define CBACK_CBACK_CCTL_CBACK                         9
#define CBQUOTE_CBQUOTE_CWORD_CBQUOTE                 10
#define CENDVAR_CENDVAR_CWORD_CENDVAR                 11
#define CENDFILE_CENDFILE_CENDFILE_CENDFILE           12
#define CWORD_CWORD_CWORD_CWORD                       13
#define CCTL_CCTL_CCTL_CCTL                           14
#else
#define CSPCL_CWORD_CWORD_CWORD                        0
#define CNL_CNL_CNL_CNL                                1
#define CWORD_CCTL_CCTL_CWORD                          2
#define CDQUOTE_CENDQUOTE_CWORD_CWORD                  3
#define CVAR_CVAR_CWORD_CVAR                           4
#define CSQUOTE_CWORD_CENDQUOTE_CWORD                  5
#define CSPCL_CWORD_CWORD_CLP                          6
#define CSPCL_CWORD_CWORD_CRP                          7
#define CBACK_CBACK_CCTL_CBACK                         8
#define CBQUOTE_CBQUOTE_CWORD_CBQUOTE                  9
#define CENDVAR_CENDVAR_CWORD_CENDVAR                 10
#define CENDFILE_CENDFILE_CENDFILE_CENDFILE           11
#define CWORD_CWORD_CWORD_CWORD                       12
#define CCTL_CCTL_CCTL_CCTL                           13
#endif

static const char syntax_index_table[258] = {
	/* BASESYNTAX_DQSYNTAX_SQSYNTAX_ARISYNTAX */
	/*   0  PEOF */      CENDFILE_CENDFILE_CENDFILE_CENDFILE,
#ifdef CONFIG_ASH_ALIAS
	/*   1  PEOA */      CSPCL_CIGN_CIGN_CIGN,
#endif
	/*   2  -128 0x80 */ CWORD_CWORD_CWORD_CWORD,
	/*   3  -127 CTLESC       */ CCTL_CCTL_CCTL_CCTL,
	/*   4  -126 CTLVAR       */ CCTL_CCTL_CCTL_CCTL,
	/*   5  -125 CTLENDVAR    */ CCTL_CCTL_CCTL_CCTL,
	/*   6  -124 CTLBACKQ     */ CCTL_CCTL_CCTL_CCTL,
	/*   7  -123 CTLQUOTE     */ CCTL_CCTL_CCTL_CCTL,
	/*   8  -122 CTLARI       */ CCTL_CCTL_CCTL_CCTL,
	/*   9  -121 CTLENDARI    */ CCTL_CCTL_CCTL_CCTL,
	/*  10  -120 CTLQUOTEMARK */ CCTL_CCTL_CCTL_CCTL,
	/*  11  -119      */ CWORD_CWORD_CWORD_CWORD,
	/*  12  -118      */ CWORD_CWORD_CWORD_CWORD,
	/*  13  -117      */ CWORD_CWORD_CWORD_CWORD,
	/*  14  -116      */ CWORD_CWORD_CWORD_CWORD,
	/*  15  -115      */ CWORD_CWORD_CWORD_CWORD,
	/*  16  -114      */ CWORD_CWORD_CWORD_CWORD,
	/*  17  -113      */ CWORD_CWORD_CWORD_CWORD,
	/*  18  -112      */ CWORD_CWORD_CWORD_CWORD,
	/*  19  -111      */ CWORD_CWORD_CWORD_CWORD,
	/*  20  -110      */ CWORD_CWORD_CWORD_CWORD,
	/*  21  -109      */ CWORD_CWORD_CWORD_CWORD,
	/*  22  -108      */ CWORD_CWORD_CWORD_CWORD,
	/*  23  -107      */ CWORD_CWORD_CWORD_CWORD,
	/*  24  -106      */ CWORD_CWORD_CWORD_CWORD,
	/*  25  -105      */ CWORD_CWORD_CWORD_CWORD,
	/*  26  -104      */ CWORD_CWORD_CWORD_CWORD,
	/*  27  -103      */ CWORD_CWORD_CWORD_CWORD,
	/*  28  -102      */ CWORD_CWORD_CWORD_CWORD,
	/*  29  -101      */ CWORD_CWORD_CWORD_CWORD,
	/*  30  -100      */ CWORD_CWORD_CWORD_CWORD,
	/*  31   -99      */ CWORD_CWORD_CWORD_CWORD,
	/*  32   -98      */ CWORD_CWORD_CWORD_CWORD,
	/*  33   -97      */ CWORD_CWORD_CWORD_CWORD,
	/*  34   -96      */ CWORD_CWORD_CWORD_CWORD,
	/*  35   -95      */ CWORD_CWORD_CWORD_CWORD,
	/*  36   -94      */ CWORD_CWORD_CWORD_CWORD,
	/*  37   -93      */ CWORD_CWORD_CWORD_CWORD,
	/*  38   -92      */ CWORD_CWORD_CWORD_CWORD,
	/*  39   -91      */ CWORD_CWORD_CWORD_CWORD,
	/*  40   -90      */ CWORD_CWORD_CWORD_CWORD,
	/*  41   -89      */ CWORD_CWORD_CWORD_CWORD,
	/*  42   -88      */ CWORD_CWORD_CWORD_CWORD,
	/*  43   -87      */ CWORD_CWORD_CWORD_CWORD,
	/*  44   -86      */ CWORD_CWORD_CWORD_CWORD,
	/*  45   -85      */ CWORD_CWORD_CWORD_CWORD,
	/*  46   -84      */ CWORD_CWORD_CWORD_CWORD,
	/*  47   -83      */ CWORD_CWORD_CWORD_CWORD,
	/*  48   -82      */ CWORD_CWORD_CWORD_CWORD,
	/*  49   -81      */ CWORD_CWORD_CWORD_CWORD,
	/*  50   -80      */ CWORD_CWORD_CWORD_CWORD,
	/*  51   -79      */ CWORD_CWORD_CWORD_CWORD,
	/*  52   -78      */ CWORD_CWORD_CWORD_CWORD,
	/*  53   -77      */ CWORD_CWORD_CWORD_CWORD,
	/*  54   -76      */ CWORD_CWORD_CWORD_CWORD,
	/*  55   -75      */ CWORD_CWORD_CWORD_CWORD,
	/*  56   -74      */ CWORD_CWORD_CWORD_CWORD,
	/*  57   -73      */ CWORD_CWORD_CWORD_CWORD,
	/*  58   -72      */ CWORD_CWORD_CWORD_CWORD,
	/*  59   -71      */ CWORD_CWORD_CWORD_CWORD,
	/*  60   -70      */ CWORD_CWORD_CWORD_CWORD,
	/*  61   -69      */ CWORD_CWORD_CWORD_CWORD,
	/*  62   -68      */ CWORD_CWORD_CWORD_CWORD,
	/*  63   -67      */ CWORD_CWORD_CWORD_CWORD,
	/*  64   -66      */ CWORD_CWORD_CWORD_CWORD,
	/*  65   -65      */ CWORD_CWORD_CWORD_CWORD,
	/*  66   -64      */ CWORD_CWORD_CWORD_CWORD,
	/*  67   -63      */ CWORD_CWORD_CWORD_CWORD,
	/*  68   -62      */ CWORD_CWORD_CWORD_CWORD,
	/*  69   -61      */ CWORD_CWORD_CWORD_CWORD,
	/*  70   -60      */ CWORD_CWORD_CWORD_CWORD,
	/*  71   -59      */ CWORD_CWORD_CWORD_CWORD,
	/*  72   -58      */ CWORD_CWORD_CWORD_CWORD,
	/*  73   -57      */ CWORD_CWORD_CWORD_CWORD,
	/*  74   -56      */ CWORD_CWORD_CWORD_CWORD,
	/*  75   -55      */ CWORD_CWORD_CWORD_CWORD,
	/*  76   -54      */ CWORD_CWORD_CWORD_CWORD,
	/*  77   -53      */ CWORD_CWORD_CWORD_CWORD,
	/*  78   -52      */ CWORD_CWORD_CWORD_CWORD,
	/*  79   -51      */ CWORD_CWORD_CWORD_CWORD,
	/*  80   -50      */ CWORD_CWORD_CWORD_CWORD,
	/*  81   -49      */ CWORD_CWORD_CWORD_CWORD,
	/*  82   -48      */ CWORD_CWORD_CWORD_CWORD,
	/*  83   -47      */ CWORD_CWORD_CWORD_CWORD,
	/*  84   -46      */ CWORD_CWORD_CWORD_CWORD,
	/*  85   -45      */ CWORD_CWORD_CWORD_CWORD,
	/*  86   -44      */ CWORD_CWORD_CWORD_CWORD,
	/*  87   -43      */ CWORD_CWORD_CWORD_CWORD,
	/*  88   -42      */ CWORD_CWORD_CWORD_CWORD,
	/*  89   -41      */ CWORD_CWORD_CWORD_CWORD,
	/*  90   -40      */ CWORD_CWORD_CWORD_CWORD,
	/*  91   -39      */ CWORD_CWORD_CWORD_CWORD,
	/*  92   -38      */ CWORD_CWORD_CWORD_CWORD,
	/*  93   -37      */ CWORD_CWORD_CWORD_CWORD,
	/*  94   -36      */ CWORD_CWORD_CWORD_CWORD,
	/*  95   -35      */ CWORD_CWORD_CWORD_CWORD,
	/*  96   -34      */ CWORD_CWORD_CWORD_CWORD,
	/*  97   -33      */ CWORD_CWORD_CWORD_CWORD,
	/*  98   -32      */ CWORD_CWORD_CWORD_CWORD,
	/*  99   -31      */ CWORD_CWORD_CWORD_CWORD,
	/* 100   -30      */ CWORD_CWORD_CWORD_CWORD,
	/* 101   -29      */ CWORD_CWORD_CWORD_CWORD,
	/* 102   -28      */ CWORD_CWORD_CWORD_CWORD,
	/* 103   -27      */ CWORD_CWORD_CWORD_CWORD,
	/* 104   -26      */ CWORD_CWORD_CWORD_CWORD,
	/* 105   -25      */ CWORD_CWORD_CWORD_CWORD,
	/* 106   -24      */ CWORD_CWORD_CWORD_CWORD,
	/* 107   -23      */ CWORD_CWORD_CWORD_CWORD,
	/* 108   -22      */ CWORD_CWORD_CWORD_CWORD,
	/* 109   -21      */ CWORD_CWORD_CWORD_CWORD,
	/* 110   -20      */ CWORD_CWORD_CWORD_CWORD,
	/* 111   -19      */ CWORD_CWORD_CWORD_CWORD,
	/* 112   -18      */ CWORD_CWORD_CWORD_CWORD,
	/* 113   -17      */ CWORD_CWORD_CWORD_CWORD,
	/* 114   -16      */ CWORD_CWORD_CWORD_CWORD,
	/* 115   -15      */ CWORD_CWORD_CWORD_CWORD,
	/* 116   -14      */ CWORD_CWORD_CWORD_CWORD,
	/* 117   -13      */ CWORD_CWORD_CWORD_CWORD,
	/* 118   -12      */ CWORD_CWORD_CWORD_CWORD,
	/* 119   -11      */ CWORD_CWORD_CWORD_CWORD,
	/* 120   -10      */ CWORD_CWORD_CWORD_CWORD,
	/* 121    -9      */ CWORD_CWORD_CWORD_CWORD,
	/* 122    -8      */ CWORD_CWORD_CWORD_CWORD,
	/* 123    -7      */ CWORD_CWORD_CWORD_CWORD,
	/* 124    -6      */ CWORD_CWORD_CWORD_CWORD,
	/* 125    -5      */ CWORD_CWORD_CWORD_CWORD,
	/* 126    -4      */ CWORD_CWORD_CWORD_CWORD,
	/* 127    -3      */ CWORD_CWORD_CWORD_CWORD,
	/* 128    -2      */ CWORD_CWORD_CWORD_CWORD,
	/* 129    -1      */ CWORD_CWORD_CWORD_CWORD,
	/* 130     0      */ CWORD_CWORD_CWORD_CWORD,
	/* 131     1      */ CWORD_CWORD_CWORD_CWORD,
	/* 132     2      */ CWORD_CWORD_CWORD_CWORD,
	/* 133     3      */ CWORD_CWORD_CWORD_CWORD,
	/* 134     4      */ CWORD_CWORD_CWORD_CWORD,
	/* 135     5      */ CWORD_CWORD_CWORD_CWORD,
	/* 136     6      */ CWORD_CWORD_CWORD_CWORD,
	/* 137     7      */ CWORD_CWORD_CWORD_CWORD,
	/* 138     8      */ CWORD_CWORD_CWORD_CWORD,
	/* 139     9 "\t" */ CSPCL_CWORD_CWORD_CWORD,
	/* 140    10 "\n" */ CNL_CNL_CNL_CNL,
	/* 141    11      */ CWORD_CWORD_CWORD_CWORD,
	/* 142    12      */ CWORD_CWORD_CWORD_CWORD,
	/* 143    13      */ CWORD_CWORD_CWORD_CWORD,
	/* 144    14      */ CWORD_CWORD_CWORD_CWORD,
	/* 145    15      */ CWORD_CWORD_CWORD_CWORD,
	/* 146    16      */ CWORD_CWORD_CWORD_CWORD,
	/* 147    17      */ CWORD_CWORD_CWORD_CWORD,
	/* 148    18      */ CWORD_CWORD_CWORD_CWORD,
	/* 149    19      */ CWORD_CWORD_CWORD_CWORD,
	/* 150    20      */ CWORD_CWORD_CWORD_CWORD,
	/* 151    21      */ CWORD_CWORD_CWORD_CWORD,
	/* 152    22      */ CWORD_CWORD_CWORD_CWORD,
	/* 153    23      */ CWORD_CWORD_CWORD_CWORD,
	/* 154    24      */ CWORD_CWORD_CWORD_CWORD,
	/* 155    25      */ CWORD_CWORD_CWORD_CWORD,
	/* 156    26      */ CWORD_CWORD_CWORD_CWORD,
	/* 157    27      */ CWORD_CWORD_CWORD_CWORD,
	/* 158    28      */ CWORD_CWORD_CWORD_CWORD,
	/* 159    29      */ CWORD_CWORD_CWORD_CWORD,
	/* 160    30      */ CWORD_CWORD_CWORD_CWORD,
	/* 161    31      */ CWORD_CWORD_CWORD_CWORD,
	/* 162    32  " " */ CSPCL_CWORD_CWORD_CWORD,
	/* 163    33  "!" */ CWORD_CCTL_CCTL_CWORD,
	/* 164    34  """ */ CDQUOTE_CENDQUOTE_CWORD_CWORD,
	/* 165    35  "#" */ CWORD_CWORD_CWORD_CWORD,
	/* 166    36  "$" */ CVAR_CVAR_CWORD_CVAR,
	/* 167    37  "%" */ CWORD_CWORD_CWORD_CWORD,
	/* 168    38  "&" */ CSPCL_CWORD_CWORD_CWORD,
	/* 169    39  "'" */ CSQUOTE_CWORD_CENDQUOTE_CWORD,
	/* 170    40  "(" */ CSPCL_CWORD_CWORD_CLP,
	/* 171    41  ")" */ CSPCL_CWORD_CWORD_CRP,
	/* 172    42  "*" */ CWORD_CCTL_CCTL_CWORD,
	/* 173    43  "+" */ CWORD_CWORD_CWORD_CWORD,
	/* 174    44  "," */ CWORD_CWORD_CWORD_CWORD,
	/* 175    45  "-" */ CWORD_CCTL_CCTL_CWORD,
	/* 176    46  "." */ CWORD_CWORD_CWORD_CWORD,
	/* 177    47  "/" */ CWORD_CCTL_CCTL_CWORD,
	/* 178    48  "0" */ CWORD_CWORD_CWORD_CWORD,
	/* 179    49  "1" */ CWORD_CWORD_CWORD_CWORD,
	/* 180    50  "2" */ CWORD_CWORD_CWORD_CWORD,
	/* 181    51  "3" */ CWORD_CWORD_CWORD_CWORD,
	/* 182    52  "4" */ CWORD_CWORD_CWORD_CWORD,
	/* 183    53  "5" */ CWORD_CWORD_CWORD_CWORD,
	/* 184    54  "6" */ CWORD_CWORD_CWORD_CWORD,
	/* 185    55  "7" */ CWORD_CWORD_CWORD_CWORD,
	/* 186    56  "8" */ CWORD_CWORD_CWORD_CWORD,
	/* 187    57  "9" */ CWORD_CWORD_CWORD_CWORD,
	/* 188    58  ":" */ CWORD_CCTL_CCTL_CWORD,
	/* 189    59  ";" */ CSPCL_CWORD_CWORD_CWORD,
	/* 190    60  "<" */ CSPCL_CWORD_CWORD_CWORD,
	/* 191    61  "=" */ CWORD_CCTL_CCTL_CWORD,
	/* 192    62  ">" */ CSPCL_CWORD_CWORD_CWORD,
	/* 193    63  "?" */ CWORD_CCTL_CCTL_CWORD,
	/* 194    64  "@" */ CWORD_CWORD_CWORD_CWORD,
	/* 195    65  "A" */ CWORD_CWORD_CWORD_CWORD,
	/* 196    66  "B" */ CWORD_CWORD_CWORD_CWORD,
	/* 197    67  "C" */ CWORD_CWORD_CWORD_CWORD,
	/* 198    68  "D" */ CWORD_CWORD_CWORD_CWORD,
	/* 199    69  "E" */ CWORD_CWORD_CWORD_CWORD,
	/* 200    70  "F" */ CWORD_CWORD_CWORD_CWORD,
	/* 201    71  "G" */ CWORD_CWORD_CWORD_CWORD,
	/* 202    72  "H" */ CWORD_CWORD_CWORD_CWORD,
	/* 203    73  "I" */ CWORD_CWORD_CWORD_CWORD,
	/* 204    74  "J" */ CWORD_CWORD_CWORD_CWORD,
	/* 205    75  "K" */ CWORD_CWORD_CWORD_CWORD,
	/* 206    76  "L" */ CWORD_CWORD_CWORD_CWORD,
	/* 207    77  "M" */ CWORD_CWORD_CWORD_CWORD,
	/* 208    78  "N" */ CWORD_CWORD_CWORD_CWORD,
	/* 209    79  "O" */ CWORD_CWORD_CWORD_CWORD,
	/* 210    80  "P" */ CWORD_CWORD_CWORD_CWORD,
	/* 211    81  "Q" */ CWORD_CWORD_CWORD_CWORD,
	/* 212    82  "R" */ CWORD_CWORD_CWORD_CWORD,
	/* 213    83  "S" */ CWORD_CWORD_CWORD_CWORD,
	/* 214    84  "T" */ CWORD_CWORD_CWORD_CWORD,
	/* 215    85  "U" */ CWORD_CWORD_CWORD_CWORD,
	/* 216    86  "V" */ CWORD_CWORD_CWORD_CWORD,
	/* 217    87  "W" */ CWORD_CWORD_CWORD_CWORD,
	/* 218    88  "X" */ CWORD_CWORD_CWORD_CWORD,
	/* 219    89  "Y" */ CWORD_CWORD_CWORD_CWORD,
	/* 220    90  "Z" */ CWORD_CWORD_CWORD_CWORD,
	/* 221    91  "[" */ CWORD_CCTL_CCTL_CWORD,
	/* 222    92  "\" */ CBACK_CBACK_CCTL_CBACK,
	/* 223    93  "]" */ CWORD_CCTL_CCTL_CWORD,
	/* 224    94  "^" */ CWORD_CWORD_CWORD_CWORD,
	/* 225    95  "_" */ CWORD_CWORD_CWORD_CWORD,
	/* 226    96  "`" */ CBQUOTE_CBQUOTE_CWORD_CBQUOTE,
	/* 227    97  "a" */ CWORD_CWORD_CWORD_CWORD,
	/* 228    98  "b" */ CWORD_CWORD_CWORD_CWORD,
	/* 229    99  "c" */ CWORD_CWORD_CWORD_CWORD,
	/* 230   100  "d" */ CWORD_CWORD_CWORD_CWORD,
	/* 231   101  "e" */ CWORD_CWORD_CWORD_CWORD,
	/* 232   102  "f" */ CWORD_CWORD_CWORD_CWORD,
	/* 233   103  "g" */ CWORD_CWORD_CWORD_CWORD,
	/* 234   104  "h" */ CWORD_CWORD_CWORD_CWORD,
	/* 235   105  "i" */ CWORD_CWORD_CWORD_CWORD,
	/* 236   106  "j" */ CWORD_CWORD_CWORD_CWORD,
	/* 237   107  "k" */ CWORD_CWORD_CWORD_CWORD,
	/* 238   108  "l" */ CWORD_CWORD_CWORD_CWORD,
	/* 239   109  "m" */ CWORD_CWORD_CWORD_CWORD,
	/* 240   110  "n" */ CWORD_CWORD_CWORD_CWORD,
	/* 241   111  "o" */ CWORD_CWORD_CWORD_CWORD,
	/* 242   112  "p" */ CWORD_CWORD_CWORD_CWORD,
	/* 243   113  "q" */ CWORD_CWORD_CWORD_CWORD,
	/* 244   114  "r" */ CWORD_CWORD_CWORD_CWORD,
	/* 245   115  "s" */ CWORD_CWORD_CWORD_CWORD,
	/* 246   116  "t" */ CWORD_CWORD_CWORD_CWORD,
	/* 247   117  "u" */ CWORD_CWORD_CWORD_CWORD,
	/* 248   118  "v" */ CWORD_CWORD_CWORD_CWORD,
	/* 249   119  "w" */ CWORD_CWORD_CWORD_CWORD,
	/* 250   120  "x" */ CWORD_CWORD_CWORD_CWORD,
	/* 251   121  "y" */ CWORD_CWORD_CWORD_CWORD,
	/* 252   122  "z" */ CWORD_CWORD_CWORD_CWORD,
	/* 253   123  "{" */ CWORD_CWORD_CWORD_CWORD,
	/* 254   124  "|" */ CSPCL_CWORD_CWORD_CWORD,
	/* 255   125  "}" */ CENDVAR_CENDVAR_CWORD_CENDVAR,
	/* 256   126  "~" */ CWORD_CCTL_CCTL_CWORD,
	/* 257   127      */ CWORD_CWORD_CWORD_CWORD,
};

#endif  /* USE_SIT_FUNCTION */

/*      alias.c      */


#define ATABSIZE 39

static int     funcblocksize;          /* size of structures in function */
static int     funcstringsize;         /* size of strings in node */
static pointer funcblock;              /* block to allocate function from */
static char   *funcstring;             /* block to allocate strings from */

static const short nodesize[26] = {
      SHELL_ALIGN(sizeof (struct ncmd)),
      SHELL_ALIGN(sizeof (struct npipe)),
      SHELL_ALIGN(sizeof (struct nredir)),
      SHELL_ALIGN(sizeof (struct nredir)),
      SHELL_ALIGN(sizeof (struct nredir)),
      SHELL_ALIGN(sizeof (struct nbinary)),
      SHELL_ALIGN(sizeof (struct nbinary)),
      SHELL_ALIGN(sizeof (struct nbinary)),
      SHELL_ALIGN(sizeof (struct nif)),
      SHELL_ALIGN(sizeof (struct nbinary)),
      SHELL_ALIGN(sizeof (struct nbinary)),
      SHELL_ALIGN(sizeof (struct nfor)),
      SHELL_ALIGN(sizeof (struct ncase)),
      SHELL_ALIGN(sizeof (struct nclist)),
      SHELL_ALIGN(sizeof (struct narg)),
      SHELL_ALIGN(sizeof (struct narg)),
      SHELL_ALIGN(sizeof (struct nfile)),
      SHELL_ALIGN(sizeof (struct nfile)),
      SHELL_ALIGN(sizeof (struct nfile)),
      SHELL_ALIGN(sizeof (struct nfile)),
      SHELL_ALIGN(sizeof (struct nfile)),
      SHELL_ALIGN(sizeof (struct ndup)),
      SHELL_ALIGN(sizeof (struct ndup)),
      SHELL_ALIGN(sizeof (struct nhere)),
      SHELL_ALIGN(sizeof (struct nhere)),
      SHELL_ALIGN(sizeof (struct nnot)),
};


static void calcsize(union node *);
static void sizenodelist(struct nodelist *);
static union node *copynode(union node *);
static struct nodelist *copynodelist(struct nodelist *);
static char *nodesavestr(char *);


static int evalstring(char *, int mask);
union node;     /* BLETCH for ansi C */
static void evaltree(union node *, int);
static void evalbackcmd(union node *, struct backcmd *);

static int evalskip;                   /* set if we are skipping commands */
static int skipcount;           /* number of levels to skip */
static int funcnest;                   /* depth of function calls */

/* reasons for skipping commands (see comment on breakcmd routine) */
#define SKIPBREAK      (1 << 0)
#define SKIPCONT       (1 << 1)
#define SKIPFUNC       (1 << 2)
#define SKIPFILE       (1 << 3)
#define SKIPEVAL       (1 << 4)

/*
 * This file was generated by the mkbuiltins program.
 */

#if JOBS
static int bgcmd(int, char **);
#endif
static int breakcmd(int, char **);
static int cdcmd(int, char **);
#ifdef CONFIG_ASH_CMDCMD
static int commandcmd(int, char **);
#endif
static int dotcmd(int, char **);
static int evalcmd(int, char **);
#ifdef CONFIG_ASH_BUILTIN_ECHO
static int echocmd(int, char **);
#endif
#ifdef CONFIG_ASH_BUILTIN_TEST
static int testcmd(int, char **);
#endif
static int execcmd(int, char **);
static int exitcmd(int, char **);
static int exportcmd(int, char **);
static int falsecmd(int, char **);
#if JOBS
static int fgcmd(int, char **);
#endif
#ifdef CONFIG_ASH_GETOPTS
static int getoptscmd(int, char **);
#endif
static int hashcmd(int, char **);
#ifndef CONFIG_FEATURE_SH_EXTRA_QUIET
static int helpcmd(int argc, char **argv);
#endif
#if JOBS
static int jobscmd(int, char **);
#endif
#ifdef CONFIG_ASH_MATH_SUPPORT
static int letcmd(int, char **);
#endif
static int localcmd(int, char **);
static int pwdcmd(int, char **);
static int readcmd(int, char **);
static int returncmd(int, char **);
static int setcmd(int, char **);
static int shiftcmd(int, char **);
static int timescmd(int, char **);
static int trapcmd(int, char **);
static int truecmd(int, char **);
static int typecmd(int, char **);
static int umaskcmd(int, char **);
static int unsetcmd(int, char **);
static int waitcmd(int, char **);
static int ulimitcmd(int, char **);
#if JOBS
static int killcmd(int, char **);
#endif

/*      mail.h        */

#ifdef CONFIG_ASH_MAIL
static void chkmail(void);
static void changemail(const char *);
#endif

/*      exec.h    */

/* values of cmdtype */
#define CMDUNKNOWN      -1      /* no entry in table for command */
#define CMDNORMAL       0       /* command is an executable program */
#define CMDFUNCTION     1       /* command is a shell function */
#define CMDBUILTIN      2       /* command is a shell builtin */

struct builtincmd {
	const char *name;
	int (*builtin)(int, char **);
	/* unsigned flags; */
};


#define COMMANDCMD (builtincmd + 5 + \
	2 * ENABLE_ASH_BUILTIN_TEST + \
	ENABLE_ASH_ALIAS + \
	ENABLE_ASH_JOB_CONTROL)
#define EXECCMD (builtincmd + 7 + \
	2 * ENABLE_ASH_BUILTIN_TEST + \
	ENABLE_ASH_ALIAS + \
	ENABLE_ASH_JOB_CONTROL + \
	ENABLE_ASH_CMDCMD + \
	ENABLE_ASH_BUILTIN_ECHO)

#define BUILTIN_NOSPEC  "0"
#define BUILTIN_SPECIAL "1"
#define BUILTIN_REGULAR "2"
#define BUILTIN_SPEC_REG "3"
#define BUILTIN_ASSIGN  "4"
#define BUILTIN_SPEC_ASSG  "5"
#define BUILTIN_REG_ASSG   "6"
#define BUILTIN_SPEC_REG_ASSG   "7"

#define IS_BUILTIN_SPECIAL(builtincmd) ((builtincmd)->name[0] & 1)
#define IS_BUILTIN_REGULAR(builtincmd) ((builtincmd)->name[0] & 2)
#define IS_BUILTIN_ASSIGN(builtincmd) ((builtincmd)->name[0] & 4)

/* make sure to keep these in proper order since it is searched via bsearch() */
static const struct builtincmd builtincmd[] = {
	{ BUILTIN_SPEC_REG      ".", dotcmd },
	{ BUILTIN_SPEC_REG      ":", truecmd },
#ifdef CONFIG_ASH_BUILTIN_TEST
	{ BUILTIN_REGULAR	"[", testcmd },
	{ BUILTIN_REGULAR	"[[", testcmd },
#endif
#ifdef CONFIG_ASH_ALIAS
	{ BUILTIN_REG_ASSG      "alias", aliascmd },
#endif
#if JOBS
	{ BUILTIN_REGULAR       "bg", bgcmd },
#endif
	{ BUILTIN_SPEC_REG      "break", breakcmd },
	{ BUILTIN_REGULAR       "cd", cdcmd },
	{ BUILTIN_NOSPEC        "chdir", cdcmd },
#ifdef CONFIG_ASH_CMDCMD
	{ BUILTIN_REGULAR       "command", commandcmd },
#endif
	{ BUILTIN_SPEC_REG      "continue", breakcmd },
#ifdef CONFIG_ASH_BUILTIN_ECHO
	{ BUILTIN_REGULAR       "echo", echocmd },
#endif
	{ BUILTIN_SPEC_REG      "eval", evalcmd },
	{ BUILTIN_SPEC_REG      "exec", execcmd },
	{ BUILTIN_SPEC_REG      "exit", exitcmd },
	{ BUILTIN_SPEC_REG_ASSG "export", exportcmd },
	{ BUILTIN_REGULAR       "false", falsecmd },
#if JOBS
	{ BUILTIN_REGULAR       "fg", fgcmd },
#endif
#ifdef CONFIG_ASH_GETOPTS
	{ BUILTIN_REGULAR       "getopts", getoptscmd },
#endif
	{ BUILTIN_NOSPEC        "hash", hashcmd },
#ifndef CONFIG_FEATURE_SH_EXTRA_QUIET
	{ BUILTIN_NOSPEC        "help", helpcmd },
#endif
#if JOBS
	{ BUILTIN_REGULAR       "jobs", jobscmd },
	{ BUILTIN_REGULAR       "kill", killcmd },
#endif
#ifdef CONFIG_ASH_MATH_SUPPORT
	{ BUILTIN_NOSPEC        "let", letcmd },
#endif
	{ BUILTIN_ASSIGN        "local", localcmd },
	{ BUILTIN_NOSPEC        "pwd", pwdcmd },
	{ BUILTIN_REGULAR       "read", readcmd },
	{ BUILTIN_SPEC_REG_ASSG "readonly", exportcmd },
	{ BUILTIN_SPEC_REG      "return", returncmd },
	{ BUILTIN_SPEC_REG      "set", setcmd },
	{ BUILTIN_SPEC_REG      "shift", shiftcmd },
	{ BUILTIN_SPEC_REG      "source", dotcmd },
#ifdef CONFIG_ASH_BUILTIN_TEST
	{ BUILTIN_REGULAR	"test", testcmd },
#endif
	{ BUILTIN_SPEC_REG      "times", timescmd },
	{ BUILTIN_SPEC_REG      "trap", trapcmd },
	{ BUILTIN_REGULAR       "true", truecmd },
	{ BUILTIN_NOSPEC        "type", typecmd },
	{ BUILTIN_NOSPEC        "ulimit", ulimitcmd },
	{ BUILTIN_REGULAR       "umask", umaskcmd },
#ifdef CONFIG_ASH_ALIAS
	{ BUILTIN_REGULAR       "unalias", unaliascmd },
#endif
	{ BUILTIN_SPEC_REG      "unset", unsetcmd },
	{ BUILTIN_REGULAR       "wait", waitcmd },
};

#define NUMBUILTINS  (sizeof (builtincmd) / sizeof (struct builtincmd) )



struct cmdentry {
	int cmdtype;
	union param {
		int index;
		const struct builtincmd *cmd;
		struct funcnode *func;
	} u;
};


/* action to find_command() */
#define DO_ERR          0x01    /* prints errors */
#define DO_ABS          0x02    /* checks absolute paths */
#define DO_NOFUNC       0x04    /* don't return shell functions, for command */
#define DO_ALTPATH      0x08    /* using alternate path */
#define DO_ALTBLTIN     0x20    /* %builtin in alt. path */

static const char *pathopt;     /* set by padvance */

static void shellexec(char **, const char *, int)
    ATTRIBUTE_NORETURN;
static char *padvance(const char **, const char *);
static void find_command(char *, struct cmdentry *, int, const char *);
static struct builtincmd *find_builtin(const char *);
static void hashcd(void);
static void changepath(const char *);
static void defun(char *, union node *);
static void unsetfunc(const char *);

#ifdef CONFIG_ASH_MATH_SUPPORT_64
typedef int64_t arith_t;
#define arith_t_type (long long)
#else
typedef long arith_t;
#define arith_t_type (long)
#endif

#ifdef CONFIG_ASH_MATH_SUPPORT
static arith_t dash_arith(const char *);
static arith_t arith(const char *expr, int *perrcode);
#endif

#ifdef CONFIG_ASH_RANDOM_SUPPORT
static unsigned long rseed;
static void change_random(const char *);
# ifndef DYNAMIC_VAR
#  define DYNAMIC_VAR
# endif
#endif

/*      init.h        */

static void reset(void);

/*      var.h     */

/*
 * Shell variables.
 */

/* flags */
#define VEXPORT         0x01    /* variable is exported */
#define VREADONLY       0x02    /* variable cannot be modified */
#define VSTRFIXED       0x04    /* variable struct is statically allocated */
#define VTEXTFIXED      0x08    /* text is statically allocated */
#define VSTACK          0x10    /* text is allocated on the stack */
#define VUNSET          0x20    /* the variable is not set */
#define VNOFUNC         0x40    /* don't call the callback function */
#define VNOSET          0x80    /* do not set variable - just readonly test */
#define VNOSAVE         0x100   /* when text is on the heap before setvareq */
#ifdef DYNAMIC_VAR
# define VDYNAMIC        0x200   /* dynamic variable */
# else
# define VDYNAMIC        0
#endif

struct var {
	struct var *next;               /* next entry in hash list */
	int flags;                      /* flags are defined above */
	const char *text;               /* name=value */
	void (*func)(const char *);     /* function to be called when  */
					/* the variable gets set/unset */
};

struct localvar {
	struct localvar *next;          /* next local variable in list */
	struct var *vp;                 /* the variable that was made local */
	int flags;                      /* saved flags */
	const char *text;               /* saved text */
};


static struct localvar *localvars;

/*
 * Shell variables.
 */

#ifdef CONFIG_ASH_GETOPTS
static void getoptsreset(const char *);
#endif

#ifdef CONFIG_LOCALE_SUPPORT
#include <locale.h>
static void change_lc_all(const char *value);
static void change_lc_ctype(const char *value);
#endif


#define VTABSIZE 39

static const char defpathvar[] = "PATH=/usr/local/bin:/usr/bin:/sbin:/bin";
#ifdef IFS_BROKEN
static const char defifsvar[] = "IFS= \t\n";
#define defifs (defifsvar + 4)
#else
static const char defifs[] = " \t\n";
#endif


static struct var varinit[] = {
#ifdef IFS_BROKEN
	{ 0,    VSTRFIXED|VTEXTFIXED,           defifsvar,      0 },
#else
	{ 0,    VSTRFIXED|VTEXTFIXED|VUNSET,    "IFS\0",        0 },
#endif

#ifdef CONFIG_ASH_MAIL
	{ 0,    VSTRFIXED|VTEXTFIXED|VUNSET,    "MAIL\0",       changemail },
	{ 0,    VSTRFIXED|VTEXTFIXED|VUNSET,    "MAILPATH\0",   changemail },
#endif

	{ 0,    VSTRFIXED|VTEXTFIXED,           defpathvar,     changepath },
	{ 0,    VSTRFIXED|VTEXTFIXED,           "PS1=$ ",       0          },
	{ 0,    VSTRFIXED|VTEXTFIXED,           "PS2=> ",       0          },
	{ 0,    VSTRFIXED|VTEXTFIXED,           "PS4=+ ",       0          },
#ifdef CONFIG_ASH_GETOPTS
	{ 0,    VSTRFIXED|VTEXTFIXED,           "OPTIND=1",     getoptsreset },
#endif
#ifdef CONFIG_ASH_RANDOM_SUPPORT
	{0, VSTRFIXED|VTEXTFIXED|VUNSET|VDYNAMIC, "RANDOM\0", change_random },
#endif
#ifdef CONFIG_LOCALE_SUPPORT
	{0, VSTRFIXED | VTEXTFIXED | VUNSET, "LC_ALL\0", change_lc_all },
	{0, VSTRFIXED | VTEXTFIXED | VUNSET, "LC_CTYPE\0", change_lc_ctype },
#endif
#ifdef CONFIG_FEATURE_COMMAND_SAVEHISTORY
	{0, VSTRFIXED | VTEXTFIXED | VUNSET, "HISTFILE\0", NULL },
#endif
};

#define vifs varinit[0]
#ifdef CONFIG_ASH_MAIL
#define vmail (&vifs)[1]
#define vmpath (&vmail)[1]
#else
#define vmpath vifs
#endif
#define vpath (&vmpath)[1]
#define vps1 (&vpath)[1]
#define vps2 (&vps1)[1]
#define vps4 (&vps2)[1]
#define voptind (&vps4)[1]
#ifdef CONFIG_ASH_GETOPTS
#define vrandom (&voptind)[1]
#else
#define vrandom (&vps4)[1]
#endif
#define defpath (defpathvar + 5)

/*
 * The following macros access the values of the above variables.
 * They have to skip over the name.  They return the null string
 * for unset variables.
 */

#define ifsval()        (vifs.text + 4)
#define ifsset()        ((vifs.flags & VUNSET) == 0)
#define mailval()       (vmail.text + 5)
#define mpathval()      (vmpath.text + 9)
#define pathval()       (vpath.text + 5)
#define ps1val()        (vps1.text + 4)
#define ps2val()        (vps2.text + 4)
#define ps4val()        (vps4.text + 4)
#define optindval()     (voptind.text + 7)

#define mpathset()      ((vmpath.flags & VUNSET) == 0)

static void setvar(const char *, const char *, int);
static void setvareq(char *, int);
static void listsetvar(struct strlist *, int);
static char *lookupvar(const char *);
static char *bltinlookup(const char *);
static char **listvars(int, int, char ***);
#define environment() listvars(VEXPORT, VUNSET, 0)
static int showvars(const char *, int, int);
static void poplocalvars(void);
static int unsetvar(const char *);
#ifdef CONFIG_ASH_GETOPTS
static int setvarsafe(const char *, const char *, int);
#endif
static int varcmp(const char *, const char *);
static struct var **hashvar(const char *);


static inline int varequal(const char *a, const char *b) {
	return !varcmp(a, b);
}


static int loopnest;            /* current loop nesting level */

/*
 * The parsefile structure pointed to by the global variable parsefile
 * contains information about the current file being read.
 */


struct redirtab {
	struct redirtab *next;
	int renamed[10];
	int nullredirs;
};

static struct redirtab *redirlist;
static int nullredirs;

extern char **environ;

/*      output.h     */


static void outstr(const char *, FILE *);
static void outcslow(int, FILE *);
static void flushall(void);
static void flusherr(void);
static int  out1fmt(const char *, ...)
    __attribute__((__format__(__printf__,1,2)));
static int fmtstr(char *, size_t, const char *, ...)
    __attribute__((__format__(__printf__,3,4)));

static int preverrout_fd;   /* save fd2 before print debug if xflag is set. */


static void out1str(const char *p)
{
	outstr(p, stdout);
}

static void out2str(const char *p)
{
	outstr(p, stderr);
	flusherr();
}

/*
 * Initialization code.
 */

/*
 * This routine initializes the builtin variables.
 */

static inline void
initvar(void)
{
	struct var *vp;
	struct var *end;
	struct var **vpp;

	/*
	 * PS1 depends on uid
	 */
#if defined(CONFIG_FEATURE_COMMAND_EDITING) && defined(CONFIG_FEATURE_SH_FANCY_PROMPT)
	vps1.text = "PS1=\\w \\$ ";
#else
	if (!geteuid())
		vps1.text = "PS1=# ";
#endif
	vp = varinit;
	end = vp + sizeof(varinit) / sizeof(varinit[0]);
	do {
		vpp = hashvar(vp->text);
		vp->next = *vpp;
		*vpp = vp;
	} while (++vp < end);
}

static inline void
init(void)
{

      /* from input.c: */
      {
	      basepf.nextc = basepf.buf = basebuf;
      }

      /* from trap.c: */
      {
	      signal(SIGCHLD, SIG_DFL);
      }

      /* from var.c: */
      {
	      char **envp;
	      char ppid[32];
	      const char *p;
	      struct stat st1, st2;

	      initvar();
	      for (envp = environ ; envp && *envp ; envp++) {
		      if (strchr(*envp, '=')) {
			      setvareq(*envp, VEXPORT|VTEXTFIXED);
		      }
	      }

	      snprintf(ppid, sizeof(ppid), "%d", (int) getppid());
	      setvar("PPID", ppid, 0);

	      p = lookupvar("PWD");
	      if (p)
	      if (*p != '/' || stat(p, &st1) || stat(".", &st2) ||
		  st1.st_dev != st2.st_dev || st1.st_ino != st2.st_ino)
		      p = 0;
	      setpwd(p, 0);
      }
}

/* PEOF (the end of file marker) */

enum {
	INPUT_PUSH_FILE = 1,
	INPUT_NOFILE_OK = 2,
};

/*
 * The input line number.  Input.c just defines this variable, and saves
 * and restores it when files are pushed and popped.  The user of this
 * package must set its value.
 */

static int pgetc(void);
static int pgetc2(void);
static int preadbuffer(void);
static void pungetc(void);
static void pushstring(char *, void *);
static void popstring(void);
static void setinputfd(int, int);
static void setinputstring(char *);
static void popfile(void);
static void popallfiles(void);
static void closescript(void);


/*      jobs.h    */


/* Mode argument to forkshell.  Don't change FORK_FG or FORK_BG. */
#define FORK_FG 0
#define FORK_BG 1
#define FORK_NOJOB 2

/* mode flags for showjob(s) */
#define SHOW_PGID       0x01    /* only show pgid - for jobs -p */
#define SHOW_PID        0x04    /* include process pid */
#define SHOW_CHANGED    0x08    /* only jobs whose state has changed */


/*
 * A job structure contains information about a job.  A job is either a
 * single process or a set of processes contained in a pipeline.  In the
 * latter case, pidlist will be non-NULL, and will point to a -1 terminated
 * array of pids.
 */

struct procstat {
	pid_t   pid;            /* process id */
	int     status;         /* last process status from wait() */
	char    *cmd;           /* text of command being run */
};

struct job {
	struct procstat ps0;    /* status of process */
	struct procstat *ps;    /* status or processes when more than one */
#if JOBS
	int stopstatus;         /* status of a stopped job */
#endif
	uint32_t
		nprocs: 16,     /* number of processes */
		state: 8,
#define JOBRUNNING      0       /* at least one proc running */
#define JOBSTOPPED      1       /* all procs are stopped */
#define JOBDONE         2       /* all procs are completed */
#if JOBS
		sigint: 1,      /* job was killed by SIGINT */
		jobctl: 1,      /* job running under job control */
#endif
		waited: 1,      /* true if this entry has been waited for */
		used: 1,        /* true if this entry is in used */
		changed: 1;     /* true if status has changed */
	struct job *prev_job;   /* previous job */
};

static pid_t backgndpid;        /* pid of last background process */
static int job_warning;         /* user was warned about stopped jobs */
#if JOBS
static int jobctl;              /* true if doing job control */
#endif

static struct job *makejob(union node *, int);
static int forkshell(struct job *, union node *, int);
static int waitforjob(struct job *);
static int stoppedjobs(void);

#if ! JOBS
#define setjobctl(on)   /* do nothing */
#else
static void setjobctl(int);
static void showjobs(FILE *, int);
#endif

/*      main.h        */


/* pid of main shell */
static int rootpid;
/* shell level: 0 for the main shell, 1 for its children, and so on */
static int shlvl;
#define rootshell (!shlvl)

static void readcmdfile(char *);
static int cmdloop(int);

/*      memalloc.h        */


struct stackmark {
	struct stack_block *stackp;
	char *stacknxt;
	size_t stacknleft;
	struct stackmark *marknext;
};

/* minimum size of a block */
#define MINSIZE SHELL_ALIGN(504)

struct stack_block {
	struct stack_block *prev;
	char space[MINSIZE];
};

static struct stack_block stackbase;
static struct stack_block *stackp = &stackbase;
static struct stackmark *markp;
static char *stacknxt = stackbase.space;
static size_t stacknleft = MINSIZE;
static char *sstrend = stackbase.space + MINSIZE;
static int herefd = -1;


static pointer ckmalloc(size_t);
static pointer ckrealloc(pointer, size_t);
static char *savestr(const char *);
static pointer stalloc(size_t);
static void stunalloc(pointer);
static void setstackmark(struct stackmark *);
static void popstackmark(struct stackmark *);
static void growstackblock(void);
static void *growstackstr(void);
static char *makestrspace(size_t, char *);
static char *stnputs(const char *, size_t, char *);
static char *stputs(const char *, char *);


static inline char *_STPUTC(int c, char *p) {
	if (p == sstrend)
		p = growstackstr();
	*p++ = c;
	return p;
}

#define stackblock() ((void *)stacknxt)
#define stackblocksize() stacknleft
#define STARTSTACKSTR(p) ((p) = stackblock())
#define STPUTC(c, p) ((p) = _STPUTC((c), (p)))
#define CHECKSTRSPACE(n, p) \
	({ \
		char *q = (p); \
		size_t l = (n); \
		size_t m = sstrend - q; \
		if (l > m) \
			(p) = makestrspace(l, q); \
		0; \
	})
#define USTPUTC(c, p)   (*p++ = (c))
#define STACKSTRNUL(p)  ((p) == sstrend? (p = growstackstr(), *p = '\0') : (*p = '\0'))
#define STUNPUTC(p)     (--p)
#define STTOPC(p)       p[-1]
#define STADJUST(amount, p)     (p += (amount))

#define grabstackstr(p) stalloc((char *)(p) - (char *)stackblock())
#define ungrabstackstr(s, p) stunalloc((s))
#define stackstrend() ((void *)sstrend)

#define ckfree(p)       free((pointer)(p))

/*      mystring.h   */


#define DOLATSTRLEN 4

static char *prefix(const char *, const char *);
static int number(const char *);
static int is_number(const char *);
static char *single_quote(const char *);
static char *sstrdup(const char *);

#define equal(s1, s2)   (strcmp(s1, s2) == 0)
#define scopy(s1, s2)   ((void)strcpy(s2, s1))

/*      options.h */

struct shparam {
	int nparam;             /* # of positional parameters (without $0) */
	unsigned char malloc;   /* if parameter list dynamically allocated */
	char **p;               /* parameter list */
#ifdef CONFIG_ASH_GETOPTS
	int optind;             /* next parameter to be processed by getopts */
	int optoff;             /* used by getopts */
#endif
};


#define eflag optlist[0]
#define fflag optlist[1]
#define Iflag optlist[2]
#define iflag optlist[3]
#define mflag optlist[4]
#define nflag optlist[5]
#define sflag optlist[6]
#define xflag optlist[7]
#define vflag optlist[8]
#define Cflag optlist[9]
#define aflag optlist[10]
#define bflag optlist[11]
#define uflag optlist[12]
#define viflag optlist[13]

#ifdef DEBUG
#define nolog optlist[14]
#define debug optlist[15]
#endif

#ifndef CONFIG_FEATURE_COMMAND_EDITING_VI
#define setvimode(on) viflag = 0   /* forcibly keep the option off */
#endif

/*      options.c */


static const char *const optletters_optnames[] = {
	"e"   "errexit",
	"f"   "noglob",
	"I"   "ignoreeof",
	"i"   "interactive",
	"m"   "monitor",
	"n"   "noexec",
	"s"   "stdin",
	"x"   "xtrace",
	"v"   "verbose",
	"C"   "noclobber",
	"a"   "allexport",
	"b"   "notify",
	"u"   "nounset",
	"\0"  "vi",
#ifdef DEBUG
	"\0"  "nolog",
	"\0"  "debug",
#endif
};

#define optletters(n) optletters_optnames[(n)][0]
#define optnames(n) (&optletters_optnames[(n)][1])

#define NOPTS (sizeof(optletters_optnames)/sizeof(optletters_optnames[0]))

static char optlist[NOPTS];


static char *arg0;                     /* value of $0 */
static struct shparam shellparam;      /* $@ current positional parameters */
static char **argptr;                  /* argument list for builtin commands */
static char *optionarg;                /* set by nextopt (like getopt) */
static char *optptr;                   /* used by nextopt */

static char *minusc;                   /* argument to -c option */


static void procargs(int, char **);
static void optschanged(void);
static void setparam(char **);
static void freeparam(volatile struct shparam *);
static int shiftcmd(int, char **);
static int setcmd(int, char **);
static int nextopt(const char *);

/*      redir.h      */

/* flags passed to redirect */
#define REDIR_PUSH 01           /* save previous values of file descriptors */
#define REDIR_SAVEFD2 03       /* set preverrout */

union node;
static void redirect(union node *, int);
static void popredir(int);
static void clearredir(int);
static int copyfd(int, int);
static int redirectsafe(union node *, int);

/*      show.h     */


#ifdef DEBUG
static void showtree(union node *);
static void trace(const char *, ...);
static void tracev(const char *, va_list);
static void trargs(char **);
static void trputc(int);
static void trputs(const char *);
static void opentrace(void);
#endif

/*      trap.h       */


/* trap handler commands */
static char *trap[NSIG];
/* current value of signal */
static char sigmode[NSIG - 1];
/* indicates specified signal received */
static char gotsig[NSIG - 1];

static void clear_traps(void);
static void setsignal(int);
static void ignoresig(int);
static void onsig(int);
static int dotrap(void);
static void setinteractive(int);
static void exitshell(void) ATTRIBUTE_NORETURN;
static int decode_signal(const char *, int);

/*
 * This routine is called when an error or an interrupt occurs in an
 * interactive shell and control is returned to the main command loop.
 */

static void
reset(void)
{
      /* from eval.c: */
      {
	      evalskip = 0;
	      loopnest = 0;
      }

      /* from input.c: */
      {
	      parselleft = parsenleft = 0;      /* clear input buffer */
	      popallfiles();
      }

      /* from parser.c: */
      {
	      tokpushback = 0;
	      checkkwd = 0;
      }

      /* from redir.c: */
      {
	      clearredir(0);
      }

}

#ifdef CONFIG_ASH_ALIAS
static struct alias *atab[ATABSIZE];

static void setalias(const char *, const char *);
static struct alias *freealias(struct alias *);
static struct alias **__lookupalias(const char *);

static void
setalias(const char *name, const char *val)
{
	struct alias *ap, **app;

	app = __lookupalias(name);
	ap = *app;
	INTOFF;
	if (ap) {
		if (!(ap->flag & ALIASINUSE)) {
			ckfree(ap->val);
		}
		ap->val = savestr(val);
		ap->flag &= ~ALIASDEAD;
	} else {
		/* not found */
		ap = ckmalloc(sizeof (struct alias));
		ap->name = savestr(name);
		ap->val = savestr(val);
		ap->flag = 0;
		ap->next = 0;
		*app = ap;
	}
	INTON;
}

static int
unalias(const char *name)
{
	struct alias **app;

	app = __lookupalias(name);

	if (*app) {
		INTOFF;
		*app = freealias(*app);
		INTON;
		return (0);
	}

	return (1);
}

static void
rmaliases(void)
{
	struct alias *ap, **app;
	int i;

	INTOFF;
	for (i = 0; i < ATABSIZE; i++) {
		app = &atab[i];
		for (ap = *app; ap; ap = *app) {
			*app = freealias(*app);
			if (ap == *app) {
				app = &ap->next;
			}
		}
	}
	INTON;
}

static struct alias *
lookupalias(const char *name, int check)
{
	struct alias *ap = *__lookupalias(name);

	if (check && ap && (ap->flag & ALIASINUSE))
		return (NULL);
	return (ap);
}

/*
 * TODO - sort output
 */
static int
aliascmd(int argc, char **argv)
{
	char *n, *v;
	int ret = 0;
	struct alias *ap;

	if (argc == 1) {
		int i;

		for (i = 0; i < ATABSIZE; i++)
			for (ap = atab[i]; ap; ap = ap->next) {
				printalias(ap);
			}
		return (0);
	}
	while ((n = *++argv) != NULL) {
		if ((v = strchr(n+1, '=')) == NULL) { /* n+1: funny ksh stuff */
			if ((ap = *__lookupalias(n)) == NULL) {
				fprintf(stderr, "%s: %s not found\n", "alias", n);
				ret = 1;
			} else
				printalias(ap);
		} else {
			*v++ = '\0';
			setalias(n, v);
		}
	}

	return (ret);
}

static int
unaliascmd(int argc, char **argv)
{
	int i;

	while ((i = nextopt("a")) != '\0') {
		if (i == 'a') {
			rmaliases();
			return (0);
		}
	}
	for (i = 0; *argptr; argptr++) {
		if (unalias(*argptr)) {
			fprintf(stderr, "%s: %s not found\n", "unalias", *argptr);
			i = 1;
		}
	}

	return (i);
}

static struct alias *
freealias(struct alias *ap) {
	struct alias *next;

	if (ap->flag & ALIASINUSE) {
		ap->flag |= ALIASDEAD;
		return ap;
	}

	next = ap->next;
	ckfree(ap->name);
	ckfree(ap->val);
	ckfree(ap);
	return next;
}

static void
printalias(const struct alias *ap) {
	out1fmt("%s=%s\n", ap->name, single_quote(ap->val));
}

static struct alias **
__lookupalias(const char *name) {
	unsigned int hashval;
	struct alias **app;
	const char *p;
	unsigned int ch;

	p = name;

	ch = (unsigned char)*p;
	hashval = ch << 4;
	while (ch) {
		hashval += ch;
		ch = (unsigned char)*++p;
	}
	app = &atab[hashval % ATABSIZE];

	for (; *app; app = &(*app)->next) {
		if (equal(name, (*app)->name)) {
			break;
		}
	}

	return app;
}
#endif /* CONFIG_ASH_ALIAS */


/*      cd.c      */

/*
 * The cd and pwd commands.
 */

#define CD_PHYSICAL 1
#define CD_PRINT 2

static int docd(const char *, int);
static int cdopt(void);

static char *curdir = nullstr;          /* current working directory */
static char *physdir = nullstr;         /* physical working directory */

static int
cdopt(void)
{
	int flags = 0;
	int i, j;

	j = 'L';
	while ((i = nextopt("LP"))) {
		if (i != j) {
			flags ^= CD_PHYSICAL;
			j = i;
		}
	}

	return flags;
}

static int
cdcmd(int argc, char **argv)
{
	const char *dest;
	const char *path;
	const char *p;
	char c;
	struct stat statb;
	int flags;

	flags = cdopt();
	dest = *argptr;
	if (!dest)
		dest = bltinlookup(homestr);
	else if (dest[0] == '-' && dest[1] == '\0') {
		dest = bltinlookup("OLDPWD");
		flags |= CD_PRINT;
	}
	if (!dest)
		dest = nullstr;
	if (*dest == '/')
		goto step7;
	if (*dest == '.') {
		c = dest[1];
dotdot:
		switch (c) {
		case '\0':
		case '/':
			goto step6;
		case '.':
			c = dest[2];
			if (c != '.')
				goto dotdot;
		}
	}
	if (!*dest)
		dest = ".";
	if (!(path = bltinlookup("CDPATH"))) {
step6:
step7:
		p = dest;
		goto docd;
	}
	do {
		c = *path;
		p = padvance(&path, dest);
		if (stat(p, &statb) >= 0 && S_ISDIR(statb.st_mode)) {
			if (c && c != ':')
				flags |= CD_PRINT;
docd:
			if (!docd(p, flags))
				goto out;
			break;
		}
	} while (path);
	sh_error("can't cd to %s", dest);
	/* NOTREACHED */
out:
	if (flags & CD_PRINT)
		out1fmt(snlfmt, curdir);
	return 0;
}


/*
 * Update curdir (the name of the current directory) in response to a
 * cd command.
 */

static inline const char *
updatepwd(const char *dir)
{
	char *new;
	char *p;
	char *cdcomppath;
	const char *lim;

	cdcomppath = sstrdup(dir);
	STARTSTACKSTR(new);
	if (*dir != '/') {
		if (curdir == nullstr)
			return 0;
		new = stputs(curdir, new);
	}
	new = makestrspace(strlen(dir) + 2, new);
	lim = stackblock() + 1;
	if (*dir != '/') {
		if (new[-1] != '/')
			USTPUTC('/', new);
		if (new > lim && *lim == '/')
			lim++;
	} else {
		USTPUTC('/', new);
		cdcomppath++;
		if (dir[1] == '/' && dir[2] != '/') {
			USTPUTC('/', new);
			cdcomppath++;
			lim++;
		}
	}
	p = strtok(cdcomppath, "/");
	while (p) {
		switch(*p) {
		case '.':
			if (p[1] == '.' && p[2] == '\0') {
				while (new > lim) {
					STUNPUTC(new);
					if (new[-1] == '/')
						break;
				}
				break;
			} else if (p[1] == '\0')
				break;
			/* fall through */
		default:
			new = stputs(p, new);
			USTPUTC('/', new);
		}
		p = strtok(0, "/");
	}
	if (new > lim)
		STUNPUTC(new);
	*new = 0;
	return stackblock();
}

/*
 * Actually do the chdir.  We also call hashcd to let the routines in exec.c
 * know that the current directory has changed.
 */

static int
docd(const char *dest, int flags)
{
	const char *dir = 0;
	int err;

	TRACE(("docd(\"%s\", %d) called\n", dest, flags));

	INTOFF;
	if (!(flags & CD_PHYSICAL)) {
		dir = updatepwd(dest);
		if (dir)
			dest = dir;
	}
	err = chdir(dest);
	if (err)
		goto out;
	setpwd(dir, 1);
	hashcd();
out:
	INTON;
	return err;
}

/*
 * Find out what the current directory is. If we already know the current
 * directory, this routine returns immediately.
 */
static inline char *
getpwd(void)
{
	char *dir = getcwd(0, 0);
	return dir ? dir : nullstr;
}

static int
pwdcmd(int argc, char **argv)
{
	int flags;
	const char *dir = curdir;

	flags = cdopt();
	if (flags) {
		if (physdir == nullstr)
			setpwd(dir, 0);
		dir = physdir;
	}
	out1fmt(snlfmt, dir);
	return 0;
}

static void
setpwd(const char *val, int setold)
{
	char *oldcur, *dir;

	oldcur = dir = curdir;

	if (setold) {
		setvar("OLDPWD", oldcur, VEXPORT);
	}
	INTOFF;
	if (physdir != nullstr) {
		if (physdir != oldcur)
			free(physdir);
		physdir = nullstr;
	}
	if (oldcur == val || !val) {
		char *s = getpwd();
		physdir = s;
		if (!val)
			dir = s;
	} else
		dir = savestr(val);
	if (oldcur != dir && oldcur != nullstr) {
		free(oldcur);
	}
	curdir = dir;
	INTON;
	setvar("PWD", dir, VEXPORT);
}

/*      error.c   */

/*
 * Errors and exceptions.
 */

/*
 * Code to handle exceptions in C.
 */



static void exverror(int, const char *, va_list)
    ATTRIBUTE_NORETURN;

/*
 * Called to raise an exception.  Since C doesn't include exceptions, we
 * just do a longjmp to the exception handler.  The type of exception is
 * stored in the global variable "exception".
 */

static void
exraise(int e)
{
#ifdef DEBUG
	if (handler == NULL)
		abort();
#endif
	INTOFF;

	exception = e;
	longjmp(handler->loc, 1);
}


/*
 * Called from trap.c when a SIGINT is received.  (If the user specifies
 * that SIGINT is to be trapped or ignored using the trap builtin, then
 * this routine is not called.)  Suppressint is nonzero when interrupts
 * are held using the INTOFF macro.  (The test for iflag is just
 * defensive programming.)
 */

static void
onint(void) {
	int i;

	intpending = 0;
#if 0
	/* comment by vodz: its strange for me, this programm don`t use other
	   signal block */
	sigsetmask(0);
#endif
	i = EXSIG;
	if (gotsig[SIGINT - 1] && !trap[SIGINT]) {
		if (!(rootshell && iflag)) {
			signal(SIGINT, SIG_DFL);
			raise(SIGINT);
		}
		i = EXINT;
	}
	exraise(i);
	/* NOTREACHED */
}

static void
exvwarning(const char *msg, va_list ap)
{
	 FILE *errs;

	 errs = stderr;
	 fprintf(errs, "%s: ", arg0);
	 if (commandname) {
		 const char *fmt = (!iflag || parsefile->fd) ?
					"%s: %d: " : "%s: ";
		 fprintf(errs, fmt, commandname, startlinno);
	 }
	 vfprintf(errs, msg, ap);
	 outcslow('\n', errs);
}

/*
 * Exverror is called to raise the error exception.  If the second argument
 * is not NULL then error prints an error message using printf style
 * formatting.  It then raises the error exception.
 */
static void
exverror(int cond, const char *msg, va_list ap)
{
#ifdef DEBUG
	if (msg) {
		TRACE(("exverror(%d, \"", cond));
		TRACEV((msg, ap));
		TRACE(("\") pid=%d\n", getpid()));
	} else
		TRACE(("exverror(%d, NULL) pid=%d\n", cond, getpid()));
	if (msg)
#endif
		exvwarning(msg, ap);

	flushall();
	exraise(cond);
	/* NOTREACHED */
}


static void
sh_error(const char *msg, ...)
{
	va_list ap;

	va_start(ap, msg);
	exverror(EXERROR, msg, ap);
	/* NOTREACHED */
	va_end(ap);
}


static void
exerror(int cond, const char *msg, ...)
{
	va_list ap;

	va_start(ap, msg);
	exverror(cond, msg, ap);
	/* NOTREACHED */
	va_end(ap);
}

/*
 * error/warning routines for external builtins
 */

static void
sh_warnx(const char *fmt, ...)
{
	va_list ap;

	va_start(ap, fmt);
	exvwarning(fmt, ap);
	va_end(ap);
}


/*
 * Return a string describing an error.  The returned string may be a
 * pointer to a static buffer that will be overwritten on the next call.
 * Action describes the operation that got the error.
 */

static const char *
errmsg(int e, const char *em)
{
	if(e == ENOENT || e == ENOTDIR) {

		return em;
	}
	return strerror(e);
}


/*      eval.c  */

/*
 * Evaluate a command.
 */

/* flags in argument to evaltree */
#define EV_EXIT 01              /* exit after evaluating tree */
#define EV_TESTED 02            /* exit status is checked; ignore -e flag */
#define EV_BACKCMD 04           /* command executing within back quotes */


static void evalloop(union node *, int);
static void evalfor(union node *, int);
static void evalcase(union node *, int);
static void evalsubshell(union node *, int);
static void expredir(union node *);
static void evalpipe(union node *, int);
static void evalcommand(union node *, int);
static int evalbltin(const struct builtincmd *, int, char **);
static int evalfun(struct funcnode *, int, char **, int);
static void prehash(union node *);
static int bltincmd(int, char **);


static const struct builtincmd bltin = {
	"\0\0", bltincmd
};


/*
 * Called to reset things after an exception.
 */

/*
 * The eval command.
 */

static int
evalcmd(int argc, char **argv)
{
	char *p;
	char *concat;
	char **ap;

	if (argc > 1) {
		p = argv[1];
		if (argc > 2) {
			STARTSTACKSTR(concat);
			ap = argv + 2;
			for (;;) {
				concat = stputs(p, concat);
				if ((p = *ap++) == NULL)
					break;
				STPUTC(' ', concat);
			}
			STPUTC('\0', concat);
			p = grabstackstr(concat);
		}
		evalstring(p, ~SKIPEVAL);

	}
	return exitstatus;
}


/*
 * Execute a command or commands contained in a string.
 */

static int
evalstring(char *s, int mask)
{
	union node *n;
	struct stackmark smark;
	int skip;

	setinputstring(s);
	setstackmark(&smark);

	skip = 0;
	while ((n = parsecmd(0)) != NEOF) {
		evaltree(n, 0);
		popstackmark(&smark);
		skip = evalskip;
		if (skip)
			break;
	}
	popfile();

	skip &= mask;
	evalskip = skip;
	return skip;
}



/*
 * Evaluate a parse tree.  The value is left in the global variable
 * exitstatus.
 */

static void
evaltree(union node *n, int flags)
{
	int checkexit = 0;
	void (*evalfn)(union node *, int);
	unsigned isor;
	int status;
	if (n == NULL) {
		TRACE(("evaltree(NULL) called\n"));
		goto out;
	}
	TRACE(("pid %d, evaltree(%p: %d, %d) called\n",
	    getpid(), n, n->type, flags));
	switch (n->type) {
	default:
#ifdef DEBUG
		out1fmt("Node type = %d\n", n->type);
		fflush(stdout);
		break;
#endif
	case NNOT:
		evaltree(n->nnot.com, EV_TESTED);
		status = !exitstatus;
		goto setstatus;
	case NREDIR:
		expredir(n->nredir.redirect);
		status = redirectsafe(n->nredir.redirect, REDIR_PUSH);
		if (!status) {
			evaltree(n->nredir.n, flags & EV_TESTED);
			status = exitstatus;
		}
		popredir(0);
		goto setstatus;
	case NCMD:
		evalfn = evalcommand;
checkexit:
		if (eflag && !(flags & EV_TESTED))
			checkexit = ~0;
		goto calleval;
	case NFOR:
		evalfn = evalfor;
		goto calleval;
	case NWHILE:
	case NUNTIL:
		evalfn = evalloop;
		goto calleval;
	case NSUBSHELL:
	case NBACKGND:
		evalfn = evalsubshell;
		goto calleval;
	case NPIPE:
		evalfn = evalpipe;
		goto checkexit;
	case NCASE:
		evalfn = evalcase;
		goto calleval;
	case NAND:
	case NOR:
	case NSEMI:
#if NAND + 1 != NOR
#error NAND + 1 != NOR
#endif
#if NOR + 1 != NSEMI
#error NOR + 1 != NSEMI
#endif
		isor = n->type - NAND;
		evaltree(
			n->nbinary.ch1,
			(flags | ((isor >> 1) - 1)) & EV_TESTED
		);
		if (!exitstatus == isor)
			break;
		if (!evalskip) {
			n = n->nbinary.ch2;
evaln:
			evalfn = evaltree;
calleval:
			evalfn(n, flags);
			break;
		}
		break;
	case NIF:
		evaltree(n->nif.test, EV_TESTED);
		if (evalskip)
			break;
		if (exitstatus == 0) {
			n = n->nif.ifpart;
			goto evaln;
		} else if (n->nif.elsepart) {
			n = n->nif.elsepart;
			goto evaln;
		}
		goto success;
	case NDEFUN:
		defun(n->narg.text, n->narg.next);
success:
		status = 0;
setstatus:
		exitstatus = status;
		break;
	}
out:
	if ((checkexit & exitstatus))
		evalskip |= SKIPEVAL;
	else if (pendingsigs && dotrap())
		goto exexit;

	if (flags & EV_EXIT) {
exexit:
		exraise(EXEXIT);
	}
}


#if !defined(__alpha__) || (defined(__GNUC__) && __GNUC__ >= 3)
static
#endif
void evaltreenr(union node *, int) __attribute__ ((alias("evaltree"),__noreturn__));


static void
evalloop(union node *n, int flags)
{
	int status;

	loopnest++;
	status = 0;
	flags &= EV_TESTED;
	for (;;) {
		int i;

		evaltree(n->nbinary.ch1, EV_TESTED);
		if (evalskip) {
skipping:         if (evalskip == SKIPCONT && --skipcount <= 0) {
				evalskip = 0;
				continue;
			}
			if (evalskip == SKIPBREAK && --skipcount <= 0)
				evalskip = 0;
			break;
		}
		i = exitstatus;
		if (n->type != NWHILE)
			i = !i;
		if (i != 0)
			break;
		evaltree(n->nbinary.ch2, flags);
		status = exitstatus;
		if (evalskip)
			goto skipping;
	}
	loopnest--;
	exitstatus = status;
}



static void
evalfor(union node *n, int flags)
{
	struct arglist arglist;
	union node *argp;
	struct strlist *sp;
	struct stackmark smark;

	setstackmark(&smark);
	arglist.lastp = &arglist.list;
	for (argp = n->nfor.args ; argp ; argp = argp->narg.next) {
		expandarg(argp, &arglist, EXP_FULL | EXP_TILDE | EXP_RECORD);
		/* XXX */
		if (evalskip)
			goto out;
	}
	*arglist.lastp = NULL;

	exitstatus = 0;
	loopnest++;
	flags &= EV_TESTED;
	for (sp = arglist.list ; sp ; sp = sp->next) {
		setvar(n->nfor.var, sp->text, 0);
		evaltree(n->nfor.body, flags);
		if (evalskip) {
			if (evalskip == SKIPCONT && --skipcount <= 0) {
				evalskip = 0;
				continue;
			}
			if (evalskip == SKIPBREAK && --skipcount <= 0)
				evalskip = 0;
			break;
		}
	}
	loopnest--;
out:
	popstackmark(&smark);
}



static void
evalcase(union node *n, int flags)
{
	union node *cp;
	union node *patp;
	struct arglist arglist;
	struct stackmark smark;

	setstackmark(&smark);
	arglist.lastp = &arglist.list;
	expandarg(n->ncase.expr, &arglist, EXP_TILDE);
	exitstatus = 0;
	for (cp = n->ncase.cases ; cp && evalskip == 0 ; cp = cp->nclist.next) {
		for (patp = cp->nclist.pattern ; patp ; patp = patp->narg.next) {
			if (casematch(patp, arglist.list->text)) {
				if (evalskip == 0) {
					evaltree(cp->nclist.body, flags);
				}
				goto out;
			}
		}
	}
out:
	popstackmark(&smark);
}



/*
 * Kick off a subshell to evaluate a tree.
 */

static void
evalsubshell(union node *n, int flags)
{
	struct job *jp;
	int backgnd = (n->type == NBACKGND);
	int status;

	expredir(n->nredir.redirect);
	if (!backgnd && flags & EV_EXIT && !trap[0])
		goto nofork;
	INTOFF;
	jp = makejob(n, 1);
	if (forkshell(jp, n, backgnd) == 0) {
		INTON;
		flags |= EV_EXIT;
		if (backgnd)
			flags &=~ EV_TESTED;
nofork:
		redirect(n->nredir.redirect, 0);
		evaltreenr(n->nredir.n, flags);
		/* never returns */
	}
	status = 0;
	if (! backgnd)
		status = waitforjob(jp);
	exitstatus = status;
	INTON;
}



/*
 * Compute the names of the files in a redirection list.
 */

static void
expredir(union node *n)
{
	union node *redir;

	for (redir = n ; redir ; redir = redir->nfile.next) {
		struct arglist fn;
		fn.lastp = &fn.list;
		switch (redir->type) {
		case NFROMTO:
		case NFROM:
		case NTO:
		case NCLOBBER:
		case NAPPEND:
			expandarg(redir->nfile.fname, &fn, EXP_TILDE | EXP_REDIR);
			redir->nfile.expfname = fn.list->text;
			break;
		case NFROMFD:
		case NTOFD:
			if (redir->ndup.vname) {
				expandarg(redir->ndup.vname, &fn, EXP_FULL | EXP_TILDE);
				fixredir(redir, fn.list->text, 1);
			}
			break;
		}
	}
}



/*
 * Evaluate a pipeline.  All the processes in the pipeline are children
 * of the process creating the pipeline.  (This differs from some versions
 * of the shell, which make the last process in a pipeline the parent
 * of all the rest.)
 */

static void
evalpipe(union node *n, int flags)
{
	struct job *jp;
	struct nodelist *lp;
	int pipelen;
	int prevfd;
	int pip[2];

	TRACE(("evalpipe(0x%lx) called\n", (long)n));
	pipelen = 0;
	for (lp = n->npipe.cmdlist ; lp ; lp = lp->next)
		pipelen++;
	flags |= EV_EXIT;
	INTOFF;
	jp = makejob(n, pipelen);
	prevfd = -1;
	for (lp = n->npipe.cmdlist ; lp ; lp = lp->next) {
		prehash(lp->n);
		pip[1] = -1;
		if (lp->next) {
			if (pipe(pip) < 0) {
				close(prevfd);
				sh_error("Pipe call failed");
			}
		}
		if (forkshell(jp, lp->n, n->npipe.backgnd) == 0) {
			INTON;
			if (pip[1] >= 0) {
				close(pip[0]);
			}
			if (prevfd > 0) {
				dup2(prevfd, 0);
				close(prevfd);
			}
			if (pip[1] > 1) {
				dup2(pip[1], 1);
				close(pip[1]);
			}
			evaltreenr(lp->n, flags);
			/* never returns */
		}
		if (prevfd >= 0)
			close(prevfd);
		prevfd = pip[0];
		close(pip[1]);
	}
	if (n->npipe.backgnd == 0) {
		exitstatus = waitforjob(jp);
		TRACE(("evalpipe:  job done exit status %d\n", exitstatus));
	}
	INTON;
}



/*
 * Execute a command inside back quotes.  If it's a builtin command, we
 * want to save its output in a block obtained from malloc.  Otherwise
 * we fork off a subprocess and get the output of the command via a pipe.
 * Should be called with interrupts off.
 */

static void
evalbackcmd(union node *n, struct backcmd *result)
{
	int saveherefd;

	result->fd = -1;
	result->buf = NULL;
	result->nleft = 0;
	result->jp = NULL;
	if (n == NULL) {
		goto out;
	}

	saveherefd = herefd;
	herefd = -1;

	{
		int pip[2];
		struct job *jp;

		if (pipe(pip) < 0)
			sh_error("Pipe call failed");
		jp = makejob(n, 1);
		if (forkshell(jp, n, FORK_NOJOB) == 0) {
			FORCEINTON;
			close(pip[0]);
			if (pip[1] != 1) {
				close(1);
				copyfd(pip[1], 1);
				close(pip[1]);
			}
			eflag = 0;
			evaltreenr(n, EV_EXIT);
			/* NOTREACHED */
		}
		close(pip[1]);
		result->fd = pip[0];
		result->jp = jp;
	}
	herefd = saveherefd;
out:
	TRACE(("evalbackcmd done: fd=%d buf=0x%x nleft=%d jp=0x%x\n",
		result->fd, result->buf, result->nleft, result->jp));
}

#ifdef CONFIG_ASH_CMDCMD
static inline char **
parse_command_args(char **argv, const char **path)
{
	char *cp, c;

	for (;;) {
		cp = *++argv;
		if (!cp)
			return 0;
		if (*cp++ != '-')
			break;
		if (!(c = *cp++))
			break;
		if (c == '-' && !*cp) {
			argv++;
			break;
		}
		do {
			switch (c) {
			case 'p':
				*path = defpath;
				break;
			default:
				/* run 'typecmd' for other options */
				return 0;
			}
		} while ((c = *cp++));
	}
	return argv;
}
#endif

static inline int
isassignment(const char *p)
{
	const char *q = endofname(p);
	if (p == q)
		return 0;
	return *q == '=';
}

#ifdef CONFIG_ASH_EXPAND_PRMT
static const char *expandstr(const char *ps);
#else
#define expandstr(s) s
#endif

/*
 * Execute a simple command.
 */

static void
evalcommand(union node *cmd, int flags)
{
	struct stackmark smark;
	union node *argp;
	struct arglist arglist;
	struct arglist varlist;
	char **argv;
	int argc;
	const struct strlist *sp;
	struct cmdentry cmdentry;
	struct job *jp;
	char *lastarg;
	const char *path;
	int spclbltin;
	int cmd_is_exec;
	int status;
	char **nargv;
	struct builtincmd *bcmd;
	int pseudovarflag = 0;

	/* First expand the arguments. */
	TRACE(("evalcommand(0x%lx, %d) called\n", (long)cmd, flags));
	setstackmark(&smark);
	back_exitstatus = 0;

	cmdentry.cmdtype = CMDBUILTIN;
	cmdentry.u.cmd = &bltin;
	varlist.lastp = &varlist.list;
	*varlist.lastp = NULL;
	arglist.lastp = &arglist.list;
	*arglist.lastp = NULL;

	argc = 0;
	if (cmd->ncmd.args)
	{
		bcmd = find_builtin(cmd->ncmd.args->narg.text);
		pseudovarflag = bcmd && IS_BUILTIN_ASSIGN(bcmd);
	}

	for (argp = cmd->ncmd.args; argp; argp = argp->narg.next) {
		struct strlist **spp;

		spp = arglist.lastp;
		if (pseudovarflag && isassignment(argp->narg.text))
			expandarg(argp, &arglist, EXP_VARTILDE);
		else
			expandarg(argp, &arglist, EXP_FULL | EXP_TILDE);

		for (sp = *spp; sp; sp = sp->next)
			argc++;
	}

	argv = nargv = stalloc(sizeof (char *) * (argc + 1));
	for (sp = arglist.list ; sp ; sp = sp->next) {
		TRACE(("evalcommand arg: %s\n", sp->text));
		*nargv++ = sp->text;
	}
	*nargv = NULL;

	lastarg = NULL;
	if (iflag && funcnest == 0 && argc > 0)
		lastarg = nargv[-1];

	preverrout_fd = 2;
	expredir(cmd->ncmd.redirect);
	status = redirectsafe(cmd->ncmd.redirect, REDIR_PUSH|REDIR_SAVEFD2);

	path = vpath.text;
	for (argp = cmd->ncmd.assign; argp; argp = argp->narg.next) {
		struct strlist **spp;
		char *p;

		spp = varlist.lastp;
		expandarg(argp, &varlist, EXP_VARTILDE);

		/*
		 * Modify the command lookup path, if a PATH= assignment
		 * is present
		 */
		p = (*spp)->text;
		if (varequal(p, path))
			path = p;
	}

	/* Print the command if xflag is set. */
	if (xflag) {
		int n;
		const char *p = " %s";

		p++;
		dprintf(preverrout_fd, p, expandstr(ps4val()));

		sp = varlist.list;
		for(n = 0; n < 2; n++) {
			while (sp) {
				dprintf(preverrout_fd, p, sp->text);
				sp = sp->next;
				if(*p == '%') {
					p--;
				}
			}
			sp = arglist.list;
		}
		bb_full_write(preverrout_fd, "\n", 1);
	}

	cmd_is_exec = 0;
	spclbltin = -1;

	/* Now locate the command. */
	if (argc) {
		const char *oldpath;
		int cmd_flag = DO_ERR;

		path += 5;
		oldpath = path;
		for (;;) {
			find_command(argv[0], &cmdentry, cmd_flag, path);
			if (cmdentry.cmdtype == CMDUNKNOWN) {
				status = 127;
				flusherr();
				goto bail;
			}

			/* implement bltin and command here */
			if (cmdentry.cmdtype != CMDBUILTIN)
				break;
			if (spclbltin < 0)
				spclbltin = IS_BUILTIN_SPECIAL(cmdentry.u.cmd);
			if (cmdentry.u.cmd == EXECCMD)
				cmd_is_exec++;
#ifdef CONFIG_ASH_CMDCMD
			if (cmdentry.u.cmd == COMMANDCMD) {

				path = oldpath;
				nargv = parse_command_args(argv, &path);
				if (!nargv)
					break;
				argc -= nargv - argv;
				argv = nargv;
				cmd_flag |= DO_NOFUNC;
			} else
#endif
				break;
		}
	}

	if (status) {
		/* We have a redirection error. */
		if (spclbltin > 0)
			exraise(EXERROR);
bail:
		exitstatus = status;
		goto out;
	}

	/* Execute the command. */
	switch (cmdentry.cmdtype) {
	default:
		/* Fork off a child process if necessary. */
		if (!(flags & EV_EXIT) || trap[0]) {
			INTOFF;
			jp = makejob(cmd, 1);
			if (forkshell(jp, cmd, FORK_FG) != 0) {
				exitstatus = waitforjob(jp);
				INTON;
				break;
			}
			FORCEINTON;
		}
		listsetvar(varlist.list, VEXPORT|VSTACK);
		shellexec(argv, path, cmdentry.u.index);
		/* NOTREACHED */

	case CMDBUILTIN:
		cmdenviron = varlist.list;
		if (cmdenviron) {
			struct strlist *list = cmdenviron;
			int i = VNOSET;
			if (spclbltin > 0 || argc == 0) {
				i = 0;
				if (cmd_is_exec && argc > 1)
					i = VEXPORT;
			}
			listsetvar(list, i);
		}
		if (evalbltin(cmdentry.u.cmd, argc, argv)) {
			int exit_status;
			int i, j;

			i = exception;
			if (i == EXEXIT)
				goto raise;

			exit_status = 2;
			j = 0;
			if (i == EXINT)
				j = SIGINT;
			if (i == EXSIG)
				j = pendingsigs;
			if (j)
				exit_status = j + 128;
			exitstatus = exit_status;

			if (i == EXINT || spclbltin > 0) {
raise:
				longjmp(handler->loc, 1);
			}
			FORCEINTON;
		}
		break;

	case CMDFUNCTION:
		listsetvar(varlist.list, 0);
		if (evalfun(cmdentry.u.func, argc, argv, flags))
			goto raise;
		break;
	}

out:
	popredir(cmd_is_exec);
	if (lastarg)
		/* dsl: I think this is intended to be used to support
		 * '_' in 'vi' command mode during line editing...
		 * However I implemented that within libedit itself.
		 */
		setvar("_", lastarg, 0);
	popstackmark(&smark);
}

static int
evalbltin(const struct builtincmd *cmd, int argc, char **argv) {
	char *volatile savecmdname;
	struct jmploc *volatile savehandler;
	struct jmploc jmploc;
	int i;

	savecmdname = commandname;
	if ((i = setjmp(jmploc.loc)))
		goto cmddone;
	savehandler = handler;
	handler = &jmploc;
	commandname = argv[0];
	argptr = argv + 1;
	optptr = NULL;                  /* initialize nextopt */
	exitstatus = (*cmd->builtin)(argc, argv);
	flushall();
cmddone:
	exitstatus |= ferror(stdout);
	clearerr(stdout);
	commandname = savecmdname;
	exsig = 0;
	handler = savehandler;

	return i;
}

static int
evalfun(struct funcnode *func, int argc, char **argv, int flags)
{
	volatile struct shparam saveparam;
	struct localvar *volatile savelocalvars;
	struct jmploc *volatile savehandler;
	struct jmploc jmploc;
	int e;

	saveparam = shellparam;
	savelocalvars = localvars;
	if ((e = setjmp(jmploc.loc))) {
		goto funcdone;
	}
	INTOFF;
	savehandler = handler;
	handler = &jmploc;
	localvars = NULL;
	shellparam.malloc = 0;
	func->count++;
	funcnest++;
	INTON;
	shellparam.nparam = argc - 1;
	shellparam.p = argv + 1;
#ifdef CONFIG_ASH_GETOPTS
	shellparam.optind = 1;
	shellparam.optoff = -1;
#endif
	evaltree(&func->n, flags & EV_TESTED);
funcdone:
	INTOFF;
	funcnest--;
	freefunc(func);
	poplocalvars();
	localvars = savelocalvars;
	freeparam(&shellparam);
	shellparam = saveparam;
	handler = savehandler;
	INTON;
	evalskip &= ~SKIPFUNC;
	return e;
}


static inline int
goodname(const char *p)
{
	return !*endofname(p);
}

/*
 * Search for a command.  This is called before we fork so that the
 * location of the command will be available in the parent as well as
 * the child.  The check for "goodname" is an overly conservative
 * check that the name will not be subject to expansion.
 */

static void
prehash(union node *n)
{
	struct cmdentry entry;

	if (n->type == NCMD && n->ncmd.args)
		if (goodname(n->ncmd.args->narg.text))
			find_command(n->ncmd.args->narg.text, &entry, 0,
				     pathval());
}



/*
 * Builtin commands.  Builtin commands whose functions are closely
 * tied to evaluation are implemented here.
 */

/*
 * No command given.
 */

static int
bltincmd(int argc, char **argv)
{
	/*
	 * Preserve exitstatus of a previous possible redirection
	 * as POSIX mandates
	 */
	return back_exitstatus;
}


/*
 * Handle break and continue commands.  Break, continue, and return are
 * all handled by setting the evalskip flag.  The evaluation routines
 * above all check this flag, and if it is set they start skipping
 * commands rather than executing them.  The variable skipcount is
 * the number of loops to break/continue, or the number of function
 * levels to return.  (The latter is always 1.)  It should probably
 * be an error to break out of more loops than exist, but it isn't
 * in the standard shell so we don't make it one here.
 */

static int
breakcmd(int argc, char **argv)
{
	int n = argc > 1 ? number(argv[1]) : 1;

	if (n <= 0)
		sh_error(illnum, argv[1]);
	if (n > loopnest)
		n = loopnest;
	if (n > 0) {
		evalskip = (**argv == 'c')? SKIPCONT : SKIPBREAK;
		skipcount = n;
	}
	return 0;
}


/*
 * The return command.
 */

static int
returncmd(int argc, char **argv)
{
	/*
	 * If called outside a function, do what ksh does;
	 * skip the rest of the file.
	 */
	evalskip = funcnest ? SKIPFUNC : SKIPFILE;
	return argv[1] ? number(argv[1]) : exitstatus;
}


static int
falsecmd(int argc, char **argv)
{
	return 1;
}


static int
truecmd(int argc, char **argv)
{
	return 0;
}


static int
execcmd(int argc, char **argv)
{
	if (argc > 1) {
		iflag = 0;              /* exit on error */
		mflag = 0;
		optschanged();
		shellexec(argv + 1, pathval(), 0);
	}
	return 0;
}


/*      exec.c    */

/*
 * When commands are first encountered, they are entered in a hash table.
 * This ensures that a full path search will not have to be done for them
 * on each invocation.
 *
 * We should investigate converting to a linear search, even though that
 * would make the command name "hash" a misnomer.
 */

#define CMDTABLESIZE 31         /* should be prime */
#define ARB 1                   /* actual size determined at run time */



struct tblentry {
	struct tblentry *next;  /* next entry in hash chain */
	union param param;      /* definition of builtin function */
	short cmdtype;          /* index identifying command */
	char rehash;            /* if set, cd done since entry created */
	char cmdname[ARB];      /* name of command */
};


static struct tblentry *cmdtable[CMDTABLESIZE];
static int builtinloc = -1;             /* index in path of %builtin, or -1 */


static void tryexec(char *, char **, char **);
static void clearcmdentry(int);
static struct tblentry *cmdlookup(const char *, int);
static void delete_cmd_entry(void);


/*
 * Exec a program.  Never returns.  If you change this routine, you may
 * have to change the find_command routine as well.
 */

static void
shellexec(char **argv, const char *path, int idx)
{
	char *cmdname;
	int e;
	char **envp;
	int exerrno;

	clearredir(1);
	envp = environment();
	if (strchr(argv[0], '/') != NULL
#ifdef CONFIG_FEATURE_SH_STANDALONE_SHELL
		|| find_applet_by_name(argv[0])
#endif
						) {
		tryexec(argv[0], argv, envp);
		e = errno;
	} else {
		e = ENOENT;
		while ((cmdname = padvance(&path, argv[0])) != NULL) {
			if (--idx < 0 && pathopt == NULL) {
				tryexec(cmdname, argv, envp);
				if (errno != ENOENT && errno != ENOTDIR)
					e = errno;
			}
			stunalloc(cmdname);
		}
	}

	/* Map to POSIX errors */
	switch (e) {
	case EACCES:
		exerrno = 126;
		break;
	case ENOENT:
		exerrno = 127;
		break;
	default:
		exerrno = 2;
		break;
	}
	exitstatus = exerrno;
	TRACE(("shellexec failed for %s, errno %d, suppressint %d\n",
		argv[0], e, suppressint ));
	exerror(EXEXEC, "%s: %s", argv[0], errmsg(e, E_EXEC));
	/* NOTREACHED */
}


static void
tryexec(char *cmd, char **argv, char **envp)
{
	int repeated = 0;
#ifdef CONFIG_FEATURE_SH_STANDALONE_SHELL
	if(find_applet_by_name(cmd) != NULL) {
		/* re-exec ourselves with the new arguments */
		execve(CONFIG_BUSYBOX_EXEC_PATH,argv,envp);
		/* If they called chroot or otherwise made the binary no longer
		 * executable, fall through */
	}
#endif

repeat:
#ifdef SYSV
	do {
		execve(cmd, argv, envp);
	} while (errno == EINTR);
#else
	execve(cmd, argv, envp);
#endif
	if (repeated++) {
		ckfree(argv);
	} else if (errno == ENOEXEC) {
		char **ap;
		char **new;

		for (ap = argv; *ap; ap++)
			;
		ap = new = ckmalloc((ap - argv + 2) * sizeof(char *));
		ap[1] = cmd;
		*ap = cmd = (char *)DEFAULT_SHELL;
		ap += 2;
		argv++;
		while ((*ap++ = *argv++))
			;
		argv = new;
		goto repeat;
	}
}



/*
 * Do a path search.  The variable path (passed by reference) should be
 * set to the start of the path before the first call; padvance will update
 * this value as it proceeds.  Successive calls to padvance will return
 * the possible path expansions in sequence.  If an option (indicated by
 * a percent sign) appears in the path entry then the global variable
 * pathopt will be set to point to it; otherwise pathopt will be set to
 * NULL.
 */

static char *
padvance(const char **path, const char *name)
{
	const char *p;
	char *q;
	const char *start;
	size_t len;

	if (*path == NULL)
		return NULL;
	start = *path;
	for (p = start ; *p && *p != ':' && *p != '%' ; p++);
	len = p - start + strlen(name) + 2;     /* "2" is for '/' and '\0' */
	while (stackblocksize() < len)
		growstackblock();
	q = stackblock();
	if (p != start) {
		memcpy(q, start, p - start);
		q += p - start;
		*q++ = '/';
	}
	strcpy(q, name);
	pathopt = NULL;
	if (*p == '%') {
		pathopt = ++p;
		while (*p && *p != ':')  p++;
	}
	if (*p == ':')
		*path = p + 1;
	else
		*path = NULL;
	return stalloc(len);
}


/*** Command hashing code ***/

static void
printentry(struct tblentry *cmdp)
{
	int idx;
	const char *path;
	char *name;

	idx = cmdp->param.index;
	path = pathval();
	do {
		name = padvance(&path, cmdp->cmdname);
		stunalloc(name);
	} while (--idx >= 0);
	out1fmt("%s%s\n", name, (cmdp->rehash ? "*" : nullstr));
}


static int
hashcmd(int argc, char **argv)
{
	struct tblentry **pp;
	struct tblentry *cmdp;
	int c;
	struct cmdentry entry;
	char *name;

	while ((c = nextopt("r")) != '\0') {
		clearcmdentry(0);
		return 0;
	}
	if (*argptr == NULL) {
		for (pp = cmdtable ; pp < &cmdtable[CMDTABLESIZE] ; pp++) {
			for (cmdp = *pp ; cmdp ; cmdp = cmdp->next) {
				if (cmdp->cmdtype == CMDNORMAL)
					printentry(cmdp);
			}
		}
		return 0;
	}
	c = 0;
	while ((name = *argptr) != NULL) {
		if ((cmdp = cmdlookup(name, 0)) != NULL
		 && (cmdp->cmdtype == CMDNORMAL
		     || (cmdp->cmdtype == CMDBUILTIN && builtinloc >= 0)))
			delete_cmd_entry();
		find_command(name, &entry, DO_ERR, pathval());
		if (entry.cmdtype == CMDUNKNOWN)
			c = 1;
		argptr++;
	}
	return c;
}


/*
 * Resolve a command name.  If you change this routine, you may have to
 * change the shellexec routine as well.
 */

static void
find_command(char *name, struct cmdentry *entry, int act, const char *path)
{
	struct tblentry *cmdp;
	int idx;
	int prev;
	char *fullname;
	struct stat statb;
	int e;
	int updatetbl;
	struct builtincmd *bcmd;

	/* If name contains a slash, don't use PATH or hash table */
	if (strchr(name, '/') != NULL) {
		entry->u.index = -1;
		if (act & DO_ABS) {
			while (stat(name, &statb) < 0) {
#ifdef SYSV
				if (errno == EINTR)
					continue;
#endif
				entry->cmdtype = CMDUNKNOWN;
				return;
			}
		}
		entry->cmdtype = CMDNORMAL;
		return;
	}

#ifdef CONFIG_FEATURE_SH_STANDALONE_SHELL
	if (find_applet_by_name(name)) {
		entry->cmdtype = CMDNORMAL;
		entry->u.index = -1;
		return;
	}
#endif

	updatetbl = (path == pathval());
	if (!updatetbl) {
		act |= DO_ALTPATH;
		if (strstr(path, "%builtin") != NULL)
			act |= DO_ALTBLTIN;
	}

	/* If name is in the table, check answer will be ok */
	if ((cmdp = cmdlookup(name, 0)) != NULL) {
		int bit;

		switch (cmdp->cmdtype) {
		default:
#if DEBUG
			abort();
#endif
		case CMDNORMAL:
			bit = DO_ALTPATH;
			break;
		case CMDFUNCTION:
			bit = DO_NOFUNC;
			break;
		case CMDBUILTIN:
			bit = DO_ALTBLTIN;
			break;
		}
		if (act & bit) {
			updatetbl = 0;
			cmdp = NULL;
		} else if (cmdp->rehash == 0)
			/* if not invalidated by cd, we're done */
			goto success;
	}

	/* If %builtin not in path, check for builtin next */
	bcmd = find_builtin(name);
	if (bcmd && (IS_BUILTIN_REGULAR(bcmd) || (
		act & DO_ALTPATH ? !(act & DO_ALTBLTIN) : builtinloc <= 0
	)))
		goto builtin_success;

	/* We have to search path. */
	prev = -1;              /* where to start */
	if (cmdp && cmdp->rehash) {     /* doing a rehash */
		if (cmdp->cmdtype == CMDBUILTIN)
			prev = builtinloc;
		else
			prev = cmdp->param.index;
	}

	e = ENOENT;
	idx = -1;
loop:
	while ((fullname = padvance(&path, name)) != NULL) {
		stunalloc(fullname);
		idx++;
		if (pathopt) {
			if (prefix(pathopt, "builtin")) {
				if (bcmd)
					goto builtin_success;
				continue;
			} else if (!(act & DO_NOFUNC) &&
				   prefix(pathopt, "func")) {
				/* handled below */
			} else {
				/* ignore unimplemented options */
				continue;
			}
		}
		/* if rehash, don't redo absolute path names */
		if (fullname[0] == '/' && idx <= prev) {
			if (idx < prev)
				continue;
			TRACE(("searchexec \"%s\": no change\n", name));
			goto success;
		}
		while (stat(fullname, &statb) < 0) {
#ifdef SYSV
			if (errno == EINTR)
				continue;
#endif
			if (errno != ENOENT && errno != ENOTDIR)
				e = errno;
			goto loop;
		}
		e = EACCES;     /* if we fail, this will be the error */
		if (!S_ISREG(statb.st_mode))
			continue;
		if (pathopt) {          /* this is a %func directory */
			stalloc(strlen(fullname) + 1);
			readcmdfile(fullname);
			if ((cmdp = cmdlookup(name, 0)) == NULL ||
			    cmdp->cmdtype != CMDFUNCTION)
				sh_error("%s not defined in %s", name, fullname);
			stunalloc(fullname);
			goto success;
		}
		TRACE(("searchexec \"%s\" returns \"%s\"\n", name, fullname));
		if (!updatetbl) {
			entry->cmdtype = CMDNORMAL;
			entry->u.index = idx;
			return;
		}
		INTOFF;
		cmdp = cmdlookup(name, 1);
		cmdp->cmdtype = CMDNORMAL;
		cmdp->param.index = idx;
		INTON;
		goto success;
	}

	/* We failed.  If there was an entry for this command, delete it */
	if (cmdp && updatetbl)
		delete_cmd_entry();
	if (act & DO_ERR)
		sh_warnx("%s: %s", name, errmsg(e, E_EXEC));
	entry->cmdtype = CMDUNKNOWN;
	return;

builtin_success:
	if (!updatetbl) {
		entry->cmdtype = CMDBUILTIN;
		entry->u.cmd = bcmd;
		return;
	}
	INTOFF;
	cmdp = cmdlookup(name, 1);
	cmdp->cmdtype = CMDBUILTIN;
	cmdp->param.cmd = bcmd;
	INTON;
success:
	cmdp->rehash = 0;
	entry->cmdtype = cmdp->cmdtype;
	entry->u = cmdp->param;
}


/*
 * Wrapper around strcmp for qsort/bsearch/...
 */
static int pstrcmp(const void *a, const void *b)
{
	return strcmp((const char *) a, (*(const char *const *) b) + 1);
}

/*
 * Search the table of builtin commands.
 */

static struct builtincmd *
find_builtin(const char *name)
{
	struct builtincmd *bp;

	bp = bsearch(
		name, builtincmd, NUMBUILTINS, sizeof(struct builtincmd),
		pstrcmp
	);
	return bp;
}



/*
 * Called when a cd is done.  Marks all commands so the next time they
 * are executed they will be rehashed.
 */

static void
hashcd(void)
{
	struct tblentry **pp;
	struct tblentry *cmdp;

	for (pp = cmdtable ; pp < &cmdtable[CMDTABLESIZE] ; pp++) {
		for (cmdp = *pp ; cmdp ; cmdp = cmdp->next) {
			if (cmdp->cmdtype == CMDNORMAL || (
				cmdp->cmdtype == CMDBUILTIN &&
				!(IS_BUILTIN_REGULAR(cmdp->param.cmd)) &&
				builtinloc > 0
			))
				cmdp->rehash = 1;
		}
	}
}



/*
 * Fix command hash table when PATH changed.
 * Called before PATH is changed.  The argument is the new value of PATH;
 * pathval() still returns the old value at this point.
 * Called with interrupts off.
 */

static void
changepath(const char *newval)
{
	const char *old, *new;
	int idx;
	int firstchange;
	int idx_bltin;

	old = pathval();
	new = newval;
	firstchange = 9999;     /* assume no change */
	idx = 0;
	idx_bltin = -1;
	for (;;) {
		if (*old != *new) {
			firstchange = idx;
			if ((*old == '\0' && *new == ':')
			 || (*old == ':' && *new == '\0'))
				firstchange++;
			old = new;      /* ignore subsequent differences */
		}
		if (*new == '\0')
			break;
		if (*new == '%' && idx_bltin < 0 && prefix(new + 1, "builtin"))
			idx_bltin = idx;
		if (*new == ':') {
			idx++;
		}
		new++, old++;
	}
	if (builtinloc < 0 && idx_bltin >= 0)
		builtinloc = idx_bltin;             /* zap builtins */
	if (builtinloc >= 0 && idx_bltin < 0)
		firstchange = 0;
	clearcmdentry(firstchange);
	builtinloc = idx_bltin;
}


/*
 * Clear out command entries.  The argument specifies the first entry in
 * PATH which has changed.
 */

static void
clearcmdentry(int firstchange)
{
	struct tblentry **tblp;
	struct tblentry **pp;
	struct tblentry *cmdp;

	INTOFF;
	for (tblp = cmdtable ; tblp < &cmdtable[CMDTABLESIZE] ; tblp++) {
		pp = tblp;
		while ((cmdp = *pp) != NULL) {
			if ((cmdp->cmdtype == CMDNORMAL &&
			     cmdp->param.index >= firstchange)
			 || (cmdp->cmdtype == CMDBUILTIN &&
			     builtinloc >= firstchange)) {
				*pp = cmdp->next;
				ckfree(cmdp);
			} else {
				pp = &cmdp->next;
			}
		}
	}
	INTON;
}



/*
 * Locate a command in the command hash table.  If "add" is nonzero,
 * add the command to the table if it is not already present.  The
 * variable "lastcmdentry" is set to point to the address of the link
 * pointing to the entry, so that delete_cmd_entry can delete the
 * entry.
 *
 * Interrupts must be off if called with add != 0.
 */

static struct tblentry **lastcmdentry;


static struct tblentry *
cmdlookup(const char *name, int add)
{
	unsigned int hashval;
	const char *p;
	struct tblentry *cmdp;
	struct tblentry **pp;

	p = name;
	hashval = (unsigned char)*p << 4;
	while (*p)
		hashval += (unsigned char)*p++;
	hashval &= 0x7FFF;
	pp = &cmdtable[hashval % CMDTABLESIZE];
	for (cmdp = *pp ; cmdp ; cmdp = cmdp->next) {
		if (equal(cmdp->cmdname, name))
			break;
		pp = &cmdp->next;
	}
	if (add && cmdp == NULL) {
		cmdp = *pp = ckmalloc(sizeof (struct tblentry) - ARB
					+ strlen(name) + 1);
		cmdp->next = NULL;
		cmdp->cmdtype = CMDUNKNOWN;
		strcpy(cmdp->cmdname, name);
	}
	lastcmdentry = pp;
	return cmdp;
}

/*
 * Delete the command entry returned on the last lookup.
 */

static void
delete_cmd_entry(void)
{
	struct tblentry *cmdp;

	INTOFF;
	cmdp = *lastcmdentry;
	*lastcmdentry = cmdp->next;
	if (cmdp->cmdtype == CMDFUNCTION)
		freefunc(cmdp->param.func);
	ckfree(cmdp);
	INTON;
}


/*
 * Add a new command entry, replacing any existing command entry for
 * the same name - except special builtins.
 */

static inline void
addcmdentry(char *name, struct cmdentry *entry)
{
	struct tblentry *cmdp;

	cmdp = cmdlookup(name, 1);
	if (cmdp->cmdtype == CMDFUNCTION) {
		freefunc(cmdp->param.func);
	}
	cmdp->cmdtype = entry->cmdtype;
	cmdp->param = entry->u;
	cmdp->rehash = 0;
}

/*
 * Make a copy of a parse tree.
 */

static inline struct funcnode *
copyfunc(union node *n)
{
	struct funcnode *f;
	size_t blocksize;

	funcblocksize = offsetof(struct funcnode, n);
	funcstringsize = 0;
	calcsize(n);
	blocksize = funcblocksize;
	f = ckmalloc(blocksize + funcstringsize);
	funcblock = (char *) f + offsetof(struct funcnode, n);
	funcstring = (char *) f + blocksize;
	copynode(n);
	f->count = 0;
	return f;
}

/*
 * Define a shell function.
 */

static void
defun(char *name, union node *func)
{
	struct cmdentry entry;

	INTOFF;
	entry.cmdtype = CMDFUNCTION;
	entry.u.func = copyfunc(func);
	addcmdentry(name, &entry);
	INTON;
}


/*
 * Delete a function if it exists.
 */

static void
unsetfunc(const char *name)
{
	struct tblentry *cmdp;

	if ((cmdp = cmdlookup(name, 0)) != NULL &&
	    cmdp->cmdtype == CMDFUNCTION)
		delete_cmd_entry();
}

/*
 * Locate and print what a word is...
 */


#ifdef CONFIG_ASH_CMDCMD
static int
describe_command(char *command, int describe_command_verbose)
#else
#define describe_command_verbose 1
static int
describe_command(char *command)
#endif
{
	struct cmdentry entry;
	struct tblentry *cmdp;
#ifdef CONFIG_ASH_ALIAS
	const struct alias *ap;
#endif
	const char *path = pathval();

	if (describe_command_verbose) {
		out1str(command);
	}

	/* First look at the keywords */
	if (findkwd(command)) {
		out1str(describe_command_verbose ? " is a shell keyword" : command);
		goto out;
	}

#ifdef CONFIG_ASH_ALIAS
	/* Then look at the aliases */
	if ((ap = lookupalias(command, 0)) != NULL) {
		if (describe_command_verbose) {
			out1fmt(" is an alias for %s", ap->val);
		} else {
			out1str("alias ");
			printalias(ap);
			return 0;
		}
		goto out;
	}
#endif
	/* Then check if it is a tracked alias */
	if ((cmdp = cmdlookup(command, 0)) != NULL) {
		entry.cmdtype = cmdp->cmdtype;
		entry.u = cmdp->param;
	} else {
		/* Finally use brute force */
		find_command(command, &entry, DO_ABS, path);
	}

	switch (entry.cmdtype) {
	case CMDNORMAL: {
		int j = entry.u.index;
		char *p;
		if (j == -1) {
			p = command;
		} else {
			do {
				p = padvance(&path, command);
				stunalloc(p);
			} while (--j >= 0);
		}
		if (describe_command_verbose) {
			out1fmt(" is%s %s",
				(cmdp ? " a tracked alias for" : nullstr), p
			);
		} else {
			out1str(p);
		}
		break;
	}

	case CMDFUNCTION:
		if (describe_command_verbose) {
			out1str(" is a shell function");
		} else {
			out1str(command);
		}
		break;

	case CMDBUILTIN:
		if (describe_command_verbose) {
			out1fmt(" is a %sshell builtin",
				IS_BUILTIN_SPECIAL(entry.u.cmd) ?
					"special " : nullstr
			);
		} else {
			out1str(command);
		}
		break;

	default:
		if (describe_command_verbose) {
			out1str(": not found\n");
		}
		return 127;
	}

out:
	outstr("\n", stdout);
	return 0;
}

static int
typecmd(int argc, char **argv)
{
	int i;
	int err = 0;

	for (i = 1; i < argc; i++) {
#ifdef CONFIG_ASH_CMDCMD
		err |= describe_command(argv[i], 1);
#else
		err |= describe_command(argv[i]);
#endif
	}
	return err;
}

#ifdef CONFIG_ASH_CMDCMD
static int
commandcmd(int argc, char **argv)
{
	int c;
	enum {
		VERIFY_BRIEF = 1,
		VERIFY_VERBOSE = 2,
	} verify = 0;

	while ((c = nextopt("pvV")) != '\0')
		if (c == 'V')
			verify |= VERIFY_VERBOSE;
		else if (c == 'v')
			verify |= VERIFY_BRIEF;
#ifdef DEBUG
		else if (c != 'p')
			abort();
#endif
	if (verify)
		return describe_command(*argptr, verify - VERIFY_BRIEF);

	return 0;
}
#endif

/*      expand.c     */

/*
 * Routines to expand arguments to commands.  We have to deal with
 * backquotes, shell variables, and file metacharacters.
 */

/*
 * _rmescape() flags
 */
#define RMESCAPE_ALLOC  0x1     /* Allocate a new string */
#define RMESCAPE_GLOB   0x2     /* Add backslashes for glob */
#define RMESCAPE_QUOTED 0x4     /* Remove CTLESC unless in quotes */
#define RMESCAPE_GROW   0x8     /* Grow strings instead of stalloc */
#define RMESCAPE_HEAP   0x10    /* Malloc strings instead of stalloc */

/*
 * Structure specifying which parts of the string should be searched
 * for IFS characters.
 */

struct ifsregion {
	struct ifsregion *next; /* next region in list */
	int begoff;             /* offset of start of region */
	int endoff;             /* offset of end of region */
	int nulonly;            /* search for nul bytes only */
};

/* output of current string */
static char *expdest;
/* list of back quote expressions */
static struct nodelist *argbackq;
/* first struct in list of ifs regions */
static struct ifsregion ifsfirst;
/* last struct in list */
static struct ifsregion *ifslastp;
/* holds expanded arg list */
static struct arglist exparg;

static void argstr(char *, int);
static char *exptilde(char *, char *, int);
static void expbackq(union node *, int, int);
static const char *subevalvar(char *, char *, int, int, int, int, int);
static char *evalvar(char *, int);
static void strtodest(const char *, int, int);
static void memtodest(const char *p, size_t len, int syntax, int quotes);
static ssize_t varvalue(char *, int, int);
static void recordregion(int, int, int);
static void removerecordregions(int);
static void ifsbreakup(char *, struct arglist *);
static void ifsfree(void);
static void expandmeta(struct strlist *, int);
static int patmatch(char *, const char *);

static int cvtnum(arith_t);
static size_t esclen(const char *, const char *);
static char *scanleft(char *, char *, char *, char *, int, int);
static char *scanright(char *, char *, char *, char *, int, int);
static void varunset(const char *, const char *, const char *, int)
	ATTRIBUTE_NORETURN;


#define pmatch(a, b) !fnmatch((a), (b), 0)
/*
 * Prepare a pattern for a expmeta (internal glob(3)) call.
 *
 * Returns an stalloced string.
 */

static inline char *
preglob(const char *pattern, int quoted, int flag) {
	flag |= RMESCAPE_GLOB;
	if (quoted) {
		flag |= RMESCAPE_QUOTED;
	}
	return _rmescapes((char *)pattern, flag);
}


static size_t
esclen(const char *start, const char *p) {
	size_t esc = 0;

	while (p > start && *--p == CTLESC) {
		esc++;
	}
	return esc;
}


/*
 * Expand shell variables and backquotes inside a here document.
 */

static inline void
expandhere(union node *arg, int fd)
{
	herefd = fd;
	expandarg(arg, (struct arglist *)NULL, 0);
	bb_full_write(fd, stackblock(), expdest - (char *)stackblock());
}


/*
 * Perform variable substitution and command substitution on an argument,
 * placing the resulting list of arguments in arglist.  If EXP_FULL is true,
 * perform splitting and file name expansion.  When arglist is NULL, perform
 * here document expansion.
 */

void
expandarg(union node *arg, struct arglist *arglist, int flag)
{
	struct strlist *sp;
	char *p;

	argbackq = arg->narg.backquote;
	STARTSTACKSTR(expdest);
	ifsfirst.next = NULL;
	ifslastp = NULL;
	argstr(arg->narg.text, flag);
	p = _STPUTC('\0', expdest);
	expdest = p - 1;
	if (arglist == NULL) {
		return;                 /* here document expanded */
	}
	p = grabstackstr(p);
	exparg.lastp = &exparg.list;
	/*
	 * TODO - EXP_REDIR
	 */
	if (flag & EXP_FULL) {
		ifsbreakup(p, &exparg);
		*exparg.lastp = NULL;
		exparg.lastp = &exparg.list;
		expandmeta(exparg.list, flag);
	} else {
		if (flag & EXP_REDIR) /*XXX - for now, just remove escapes */
			rmescapes(p);
		sp = (struct strlist *)stalloc(sizeof (struct strlist));
		sp->text = p;
		*exparg.lastp = sp;
		exparg.lastp = &sp->next;
	}
	if (ifsfirst.next)
		ifsfree();
	*exparg.lastp = NULL;
	if (exparg.list) {
		*arglist->lastp = exparg.list;
		arglist->lastp = exparg.lastp;
	}
}


/*
 * Perform variable and command substitution.  If EXP_FULL is set, output CTLESC
 * characters to allow for further processing.  Otherwise treat
 * $@ like $* since no splitting will be performed.
 */

static void
argstr(char *p, int flag)
{
	static const char spclchars[] = {
		'=',
		':',
		CTLQUOTEMARK,
		CTLENDVAR,
		CTLESC,
		CTLVAR,
		CTLBACKQ,
		CTLBACKQ | CTLQUOTE,
#ifdef CONFIG_ASH_MATH_SUPPORT
		CTLENDARI,
#endif
		0
	};
	const char *reject = spclchars;
	int c;
	int quotes = flag & (EXP_FULL | EXP_CASE);      /* do CTLESC */
	int breakall = flag & EXP_WORD;
	int inquotes;
	size_t length;
	int startloc;

	if (!(flag & EXP_VARTILDE)) {
		reject += 2;
	} else if (flag & EXP_VARTILDE2) {
		reject++;
	}
	inquotes = 0;
	length = 0;
	if (flag & EXP_TILDE) {
		char *q;

		flag &= ~EXP_TILDE;
tilde:
		q = p;
		if (*q == CTLESC && (flag & EXP_QWORD))
			q++;
		if (*q == '~')
			p = exptilde(p, q, flag);
	}
start:
	startloc = expdest - (char *)stackblock();
	for (;;) {
		length += strcspn(p + length, reject);
		c = p[length];
		if (c && (!(c & 0x80)
#ifdef CONFIG_ASH_MATH_SUPPORT
					|| c == CTLENDARI
#endif
		   )) {
			/* c == '=' || c == ':' || c == CTLENDARI */
			length++;
		}
		if (length > 0) {
			int newloc;
			expdest = stnputs(p, length, expdest);
			newloc = expdest - (char *)stackblock();
			if (breakall && !inquotes && newloc > startloc) {
				recordregion(startloc, newloc, 0);
			}
			startloc = newloc;
		}
		p += length + 1;
		length = 0;

		switch (c) {
		case '\0':
			goto breakloop;
		case '=':
			if (flag & EXP_VARTILDE2) {
				p--;
				continue;
			}
			flag |= EXP_VARTILDE2;
			reject++;
			/* fall through */
		case ':':
			/*
			 * sort of a hack - expand tildes in variable
			 * assignments (after the first '=' and after ':'s).
			 */
			if (*--p == '~') {
				goto tilde;
			}
			continue;
		}

		switch (c) {
		case CTLENDVAR: /* ??? */
			goto breakloop;
		case CTLQUOTEMARK:
			/* "$@" syntax adherence hack */
			if (
				!inquotes &&
				!memcmp(p, dolatstr, DOLATSTRLEN) &&
				(p[4] == CTLQUOTEMARK || (
					p[4] == CTLENDVAR &&
					p[5] == CTLQUOTEMARK
				))
			) {
				p = evalvar(p + 1, flag) + 1;
				goto start;
			}
			inquotes = !inquotes;
addquote:
			if (quotes) {
				p--;
				length++;
				startloc++;
			}
			break;
		case CTLESC:
			startloc++;
			length++;
			goto addquote;
		case CTLVAR:
			p = evalvar(p, flag);
			goto start;
		case CTLBACKQ:
			c = 0;
		case CTLBACKQ|CTLQUOTE:
			expbackq(argbackq->n, c, quotes);
			argbackq = argbackq->next;
			goto start;
#ifdef CONFIG_ASH_MATH_SUPPORT
		case CTLENDARI:
			p--;
			expari(quotes);
			goto start;
#endif
		}
	}
breakloop:
	;
}

static char *
exptilde(char *startp, char *p, int flag)
{
	char c;
	char *name;
	struct passwd *pw;
	const char *home;
	int quotes = flag & (EXP_FULL | EXP_CASE);
	int startloc;

	name = p + 1;

	while ((c = *++p) != '\0') {
		switch(c) {
		case CTLESC:
			return (startp);
		case CTLQUOTEMARK:
			return (startp);
		case ':':
			if (flag & EXP_VARTILDE)
				goto done;
			break;
		case '/':
		case CTLENDVAR:
			goto done;
		}
	}
done:
	*p = '\0';
	if (*name == '\0') {
		home = lookupvar(homestr);
	} else {
		if ((pw = getpwnam(name)) == NULL)
			goto lose;
		home = pw->pw_dir;
	}
	if (!home || !*home)
		goto lose;
	*p = c;
	startloc = expdest - (char *)stackblock();
	strtodest(home, SQSYNTAX, quotes);
	recordregion(startloc, expdest - (char *)stackblock(), 0);
	return (p);
lose:
	*p = c;
	return (startp);
}


static void
removerecordregions(int endoff)
{
	if (ifslastp == NULL)
		return;

	if (ifsfirst.endoff > endoff) {
		while (ifsfirst.next != NULL) {
			struct ifsregion *ifsp;
			INTOFF;
			ifsp = ifsfirst.next->next;
			ckfree(ifsfirst.next);
			ifsfirst.next = ifsp;
			INTON;
		}
		if (ifsfirst.begoff > endoff)
			ifslastp = NULL;
		else {
			ifslastp = &ifsfirst;
			ifsfirst.endoff = endoff;
		}
		return;
	}

	ifslastp = &ifsfirst;
	while (ifslastp->next && ifslastp->next->begoff < endoff)
		ifslastp=ifslastp->next;
	while (ifslastp->next != NULL) {
		struct ifsregion *ifsp;
		INTOFF;
		ifsp = ifslastp->next->next;
		ckfree(ifslastp->next);
		ifslastp->next = ifsp;
		INTON;
	}
	if (ifslastp->endoff > endoff)
		ifslastp->endoff = endoff;
}


#ifdef CONFIG_ASH_MATH_SUPPORT
/*
 * Expand arithmetic expression.  Backup to start of expression,
 * evaluate, place result in (backed up) result, adjust string position.
 */
void
expari(int quotes)
{
	char *p, *start;
	int begoff;
	int flag;
	int len;

	/*      ifsfree(); */

	/*
	 * This routine is slightly over-complicated for
	 * efficiency.  Next we scan backwards looking for the
	 * start of arithmetic.
	 */
	start = stackblock();
	p = expdest - 1;
	*p = '\0';
	p--;
	do {
		int esc;

		while (*p != CTLARI) {
			p--;
#ifdef DEBUG
			if (p < start) {
				sh_error("missing CTLARI (shouldn't happen)");
			}
#endif
		}

		esc = esclen(start, p);
		if (!(esc % 2)) {
			break;
		}

		p -= esc + 1;
	} while (1);

	begoff = p - start;

	removerecordregions(begoff);

	flag = p[1];

	expdest = p;

	if (quotes)
		rmescapes(p + 2);

	len = cvtnum(dash_arith(p + 2));

	if (flag != '"')
		recordregion(begoff, begoff + len, 0);
}
#endif

/*
 * Expand stuff in backwards quotes.
 */

static void
expbackq(union node *cmd, int quoted, int quotes)
{
	struct backcmd in;
	int i;
	char buf[128];
	char *p;
	char *dest;
	int startloc;
	int syntax = quoted? DQSYNTAX : BASESYNTAX;
	struct stackmark smark;

	INTOFF;
	setstackmark(&smark);
	dest = expdest;
	startloc = dest - (char *)stackblock();
	grabstackstr(dest);
	evalbackcmd(cmd, (struct backcmd *) &in);
	popstackmark(&smark);

	p = in.buf;
	i = in.nleft;
	if (i == 0)
		goto read;
	for (;;) {
		memtodest(p, i, syntax, quotes);
read:
		if (in.fd < 0)
			break;
		i = safe_read(in.fd, buf, sizeof buf);
		TRACE(("expbackq: read returns %d\n", i));
		if (i <= 0)
			break;
		p = buf;
	}

	if (in.buf)
		ckfree(in.buf);
	if (in.fd >= 0) {
		close(in.fd);
		back_exitstatus = waitforjob(in.jp);
	}
	INTON;

	/* Eat all trailing newlines */
	dest = expdest;
	for (; dest > (char *)stackblock() && dest[-1] == '\n';)
		STUNPUTC(dest);
	expdest = dest;

	if (quoted == 0)
		recordregion(startloc, dest - (char *)stackblock(), 0);
	TRACE(("evalbackq: size=%d: \"%.*s\"\n",
		(dest - (char *)stackblock()) - startloc,
		(dest - (char *)stackblock()) - startloc,
		stackblock() + startloc));
}


static char *
scanleft(char *startp, char *rmesc, char *rmescend, char *str, int quotes,
	int zero)
{
	char *loc;
	char *loc2;
	char c;

	loc = startp;
	loc2 = rmesc;
	do {
		int match;
		const char *s = loc2;
		c = *loc2;
		if (zero) {
			*loc2 = '\0';
			s = rmesc;
		}
		match = pmatch(str, s);
		*loc2 = c;
		if (match)
			return loc;
		if (quotes && *loc == CTLESC)
			loc++;
		loc++;
		loc2++;
	} while (c);
	return 0;
}


static char *
scanright(char *startp, char *rmesc, char *rmescend, char *str, int quotes,
	int zero)
{
	int esc = 0;
	char *loc;
	char *loc2;

	for (loc = str - 1, loc2 = rmescend; loc >= startp; loc2--) {
		int match;
		char c = *loc2;
		const char *s = loc2;
		if (zero) {
			*loc2 = '\0';
			s = rmesc;
		}
		match = pmatch(str, s);
		*loc2 = c;
		if (match)
			return loc;
		loc--;
		if (quotes) {
			if (--esc < 0) {
				esc = esclen(startp, loc);
			}
			if (esc % 2) {
				esc--;
				loc--;
			}
		}
	}
	return 0;
}

static const char *
subevalvar(char *p, char *str, int strloc, int subtype, int startloc, int varflags, int quotes)
{
	char *startp;
	char *loc;
	int saveherefd = herefd;
	struct nodelist *saveargbackq = argbackq;
	int amount;
	char *rmesc, *rmescend;
	int zero;
	char *(*scan)(char *, char *, char *, char *, int , int);

	herefd = -1;
	argstr(p, subtype != VSASSIGN && subtype != VSQUESTION ? EXP_CASE : 0);
	STPUTC('\0', expdest);
	herefd = saveherefd;
	argbackq = saveargbackq;
	startp = stackblock() + startloc;

	switch (subtype) {
	case VSASSIGN:
		setvar(str, startp, 0);
		amount = startp - expdest;
		STADJUST(amount, expdest);
		return startp;

	case VSQUESTION:
		varunset(p, str, startp, varflags);
		/* NOTREACHED */
	}

	subtype -= VSTRIMRIGHT;
#ifdef DEBUG
	if (subtype < 0 || subtype > 3)
		abort();
#endif

	rmesc = startp;
	rmescend = stackblock() + strloc;
	if (quotes) {
		rmesc = _rmescapes(startp, RMESCAPE_ALLOC | RMESCAPE_GROW);
		if (rmesc != startp) {
			rmescend = expdest;
			startp = stackblock() + startloc;
		}
	}
	rmescend--;
	str = stackblock() + strloc;
	preglob(str, varflags & VSQUOTE, 0);

	/* zero = subtype == VSTRIMLEFT || subtype == VSTRIMLEFTMAX */
	zero = subtype >> 1;
	/* VSTRIMLEFT/VSTRIMRIGHTMAX -> scanleft */
	scan = (subtype & 1) ^ zero ? scanleft : scanright;

	loc = scan(startp, rmesc, rmescend, str, quotes, zero);
	if (loc) {
		if (zero) {
			memmove(startp, loc, str - loc);
			loc = startp + (str - loc) - 1;
		}
		*loc = '\0';
		amount = loc - expdest;
		STADJUST(amount, expdest);
	}
	return loc;
}


/*
 * Expand a variable, and return a pointer to the next character in the
 * input string.
 */
static char *
evalvar(char *p, int flag)
{
	int subtype;
	int varflags;
	char *var;
	int patloc;
	int c;
	int startloc;
	ssize_t varlen;
	int easy;
	int quotes;
	int quoted;

	quotes = flag & (EXP_FULL | EXP_CASE);
	varflags = *p++;
	subtype = varflags & VSTYPE;
	quoted = varflags & VSQUOTE;
	var = p;
	easy = (!quoted || (*var == '@' && shellparam.nparam));
	startloc = expdest - (char *)stackblock();
	p = strchr(p, '=') + 1;

again:
	varlen = varvalue(var, varflags, flag);
	if (varflags & VSNUL)
		varlen--;

	if (subtype == VSPLUS) {
		varlen = -1 - varlen;
		goto vsplus;
	}

	if (subtype == VSMINUS) {
vsplus:
		if (varlen < 0) {
			argstr(
				p, flag | EXP_TILDE |
					(quoted ?  EXP_QWORD : EXP_WORD)
			);
			goto end;
		}
		if (easy)
			goto record;
		goto end;
	}

	if (subtype == VSASSIGN || subtype == VSQUESTION) {
		if (varlen < 0) {
			if (subevalvar(p, var, 0, subtype, startloc,
				       varflags, 0)) {
				varflags &= ~VSNUL;
				/*
				 * Remove any recorded regions beyond
				 * start of variable
				 */
				removerecordregions(startloc);
				goto again;
			}
			goto end;
		}
		if (easy)
			goto record;
		goto end;
	}

	if (varlen < 0 && uflag)
		varunset(p, var, 0, 0);

	if (subtype == VSLENGTH) {
		cvtnum(varlen > 0 ? varlen : 0);
		goto record;
	}

	if (subtype == VSNORMAL) {
		if (!easy)
			goto end;
record:
		recordregion(startloc, expdest - (char *)stackblock(), quoted);
		goto end;
	}

#ifdef DEBUG
	switch (subtype) {
	case VSTRIMLEFT:
	case VSTRIMLEFTMAX:
	case VSTRIMRIGHT:
	case VSTRIMRIGHTMAX:
		break;
	default:
		abort();
	}
#endif

	if (varlen >= 0) {
		/*
		 * Terminate the string and start recording the pattern
		 * right after it
		 */
		STPUTC('\0', expdest);
		patloc = expdest - (char *)stackblock();
		if (subevalvar(p, NULL, patloc, subtype,
			       startloc, varflags, quotes) == 0) {
			int amount = expdest - (
				(char *)stackblock() + patloc - 1
			);
			STADJUST(-amount, expdest);
		}
		/* Remove any recorded regions beyond start of variable */
		removerecordregions(startloc);
		goto record;
	}

end:
	if (subtype != VSNORMAL) {      /* skip to end of alternative */
		int nesting = 1;
		for (;;) {
			if ((c = *p++) == CTLESC)
				p++;
			else if (c == CTLBACKQ || c == (CTLBACKQ|CTLQUOTE)) {
				if (varlen >= 0)
					argbackq = argbackq->next;
			} else if (c == CTLVAR) {
				if ((*p++ & VSTYPE) != VSNORMAL)
					nesting++;
			} else if (c == CTLENDVAR) {
				if (--nesting == 0)
					break;
			}
		}
	}
	return p;
}


/*
 * Put a string on the stack.
 */

static void
memtodest(const char *p, size_t len, int syntax, int quotes) {
	char *q = expdest;

	q = makestrspace(len * 2, q);

	while (len--) {
		int c = SC2INT(*p++);
		if (!c)
			continue;
		if (quotes && (SIT(c, syntax) == CCTL || SIT(c, syntax) == CBACK))
			USTPUTC(CTLESC, q);
		USTPUTC(c, q);
	}

	expdest = q;
}


static void
strtodest(const char *p, int syntax, int quotes)
{
	memtodest(p, strlen(p), syntax, quotes);
}


/*
 * Add the value of a specialized variable to the stack string.
 */

static ssize_t
varvalue(char *name, int varflags, int flags)
{
	int num;
	char *p;
	int i;
	int sep = 0;
	int sepq = 0;
	ssize_t len = 0;
	char **ap;
	int syntax;
	int quoted = varflags & VSQUOTE;
	int subtype = varflags & VSTYPE;
	int quotes = flags & (EXP_FULL | EXP_CASE);

	if (quoted && (flags & EXP_FULL))
		sep = 1 << CHAR_BIT;

	syntax = quoted ? DQSYNTAX : BASESYNTAX;
	switch (*name) {
	case '$':
		num = rootpid;
		goto numvar;
	case '?':
		num = exitstatus;
		goto numvar;
	case '#':
		num = shellparam.nparam;
		goto numvar;
	case '!':
		num = backgndpid;
		if (num == 0)
			return -1;
numvar:
		len = cvtnum(num);
		break;
	case '-':
		p = makestrspace(NOPTS, expdest);
		for (i = NOPTS - 1; i >= 0; i--) {
			if (optlist[i]) {
				USTPUTC(optletters(i), p);
				len++;
			}
		}
		expdest = p;
		break;
	case '@':
		if (sep)
			goto param;
		/* fall through */
	case '*':
		sep = ifsset() ? SC2INT(ifsval()[0]) : ' ';
		if (quotes && (SIT(sep, syntax) == CCTL || SIT(sep, syntax) == CBACK))
			sepq = 1;
param:
		if (!(ap = shellparam.p))
			return -1;
		while ((p = *ap++)) {
			size_t partlen;

			partlen = strlen(p);
			len += partlen;

			if (!(subtype == VSPLUS || subtype == VSLENGTH))
				memtodest(p, partlen, syntax, quotes);

			if (*ap && sep) {
				char *q;

				len++;
				if (subtype == VSPLUS || subtype == VSLENGTH) {
					continue;
				}
				q = expdest;
				if (sepq)
					STPUTC(CTLESC, q);
				STPUTC(sep, q);
				expdest = q;
			}
		}
		return len;
	case '0':
	case '1':
	case '2':
	case '3':
	case '4':
	case '5':
	case '6':
	case '7':
	case '8':
	case '9':
		num = atoi(name);
		if (num < 0 || num > shellparam.nparam)
			return -1;
		p = num ? shellparam.p[num - 1] : arg0;
		goto value;
	default:
		p = lookupvar(name);
value:
		if (!p)
			return -1;

		len = strlen(p);
		if (!(subtype == VSPLUS || subtype == VSLENGTH))
			memtodest(p, len, syntax, quotes);
		return len;
	}

	if (subtype == VSPLUS || subtype == VSLENGTH)
		STADJUST(-len, expdest);
	return len;
}


/*
 * Record the fact that we have to scan this region of the
 * string for IFS characters.
 */

static void
recordregion(int start, int end, int nulonly)
{
	struct ifsregion *ifsp;

	if (ifslastp == NULL) {
		ifsp = &ifsfirst;
	} else {
		INTOFF;
		ifsp = (struct ifsregion *)ckmalloc(sizeof (struct ifsregion));
		ifsp->next = NULL;
		ifslastp->next = ifsp;
		INTON;
	}
	ifslastp = ifsp;
	ifslastp->begoff = start;
	ifslastp->endoff = end;
	ifslastp->nulonly = nulonly;
}


/*
 * Break the argument string into pieces based upon IFS and add the
 * strings to the argument list.  The regions of the string to be
 * searched for IFS characters have been stored by recordregion.
 */
static void
ifsbreakup(char *string, struct arglist *arglist)
{
	struct ifsregion *ifsp;
	struct strlist *sp;
	char *start;
	char *p;
	char *q;
	const char *ifs, *realifs;
	int ifsspc;
	int nulonly;


	start = string;
	if (ifslastp != NULL) {
		ifsspc = 0;
		nulonly = 0;
		realifs = ifsset() ? ifsval() : defifs;
		ifsp = &ifsfirst;
		do {
			p = string + ifsp->begoff;
			nulonly = ifsp->nulonly;
			ifs = nulonly ? nullstr : realifs;
			ifsspc = 0;
			while (p < string + ifsp->endoff) {
				q = p;
				if (*p == CTLESC)
					p++;
				if (strchr(ifs, *p)) {
					if (!nulonly)
						ifsspc = (strchr(defifs, *p) != NULL);
					/* Ignore IFS whitespace at start */
					if (q == start && ifsspc) {
						p++;
						start = p;
						continue;
					}
					*q = '\0';
					sp = (struct strlist *)stalloc(sizeof *sp);
					sp->text = start;
					*arglist->lastp = sp;
					arglist->lastp = &sp->next;
					p++;
					if (!nulonly) {
						for (;;) {
							if (p >= string + ifsp->endoff) {
								break;
							}
							q = p;
							if (*p == CTLESC)
								p++;
							if (strchr(ifs, *p) == NULL ) {
								p = q;
								break;
							} else if (strchr(defifs, *p) == NULL) {
								if (ifsspc) {
									p++;
									ifsspc = 0;
								} else {
									p = q;
									break;
								}
							} else
								p++;
						}
					}
					start = p;
				} else
					p++;
			}
		} while ((ifsp = ifsp->next) != NULL);
		if (nulonly)
			goto add;
	}

	if (!*start)
		return;

add:
	sp = (struct strlist *)stalloc(sizeof *sp);
	sp->text = start;
	*arglist->lastp = sp;
	arglist->lastp = &sp->next;
}

static void
ifsfree(void)
{
	struct ifsregion *p;

	INTOFF;
	p = ifsfirst.next;
	do {
		struct ifsregion *ifsp;
		ifsp = p->next;
		ckfree(p);
		p = ifsp;
	} while (p);
	ifslastp = NULL;
	ifsfirst.next = NULL;
	INTON;
}

static void expmeta(char *, char *);
static struct strlist *expsort(struct strlist *);
static struct strlist *msort(struct strlist *, int);

static char *expdir;


static void
expandmeta(struct strlist *str, int flag)
{
	static const char metachars[] = {
		'*', '?', '[', 0
	};
	/* TODO - EXP_REDIR */

	while (str) {
		struct strlist **savelastp;
		struct strlist *sp;
		char *p;

		if (fflag)
			goto nometa;
		if (!strpbrk(str->text, metachars))
			goto nometa;
		savelastp = exparg.lastp;

		INTOFF;
		p = preglob(str->text, 0, RMESCAPE_ALLOC | RMESCAPE_HEAP);
		{
			int i = strlen(str->text);
			expdir = ckmalloc(i < 2048 ? 2048 : i); /* XXX */
		}

		expmeta(expdir, p);
		ckfree(expdir);
		if (p != str->text)
			ckfree(p);
		INTON;
		if (exparg.lastp == savelastp) {
			/*
			 * no matches
			 */
nometa:
			*exparg.lastp = str;
			rmescapes(str->text);
			exparg.lastp = &str->next;
		} else {
			*exparg.lastp = NULL;
			*savelastp = sp = expsort(*savelastp);
			while (sp->next != NULL)
				sp = sp->next;
			exparg.lastp = &sp->next;
		}
		str = str->next;
	}
}

/*
 * Add a file name to the list.
 */

static void
addfname(const char *name)
{
	struct strlist *sp;

	sp = (struct strlist *)stalloc(sizeof *sp);
	sp->text = sstrdup(name);
	*exparg.lastp = sp;
	exparg.lastp = &sp->next;
}


/*
 * Do metacharacter (i.e. *, ?, [...]) expansion.
 */

static void
expmeta(char *enddir, char *name)
{
	char *p;
	const char *cp;
	char *start;
	char *endname;
	int metaflag;
	struct stat statb;
	DIR *dirp;
	struct dirent *dp;
	int atend;
	int matchdot;

	metaflag = 0;
	start = name;
	for (p = name; *p; p++) {
		if (*p == '*' || *p == '?')
			metaflag = 1;
		else if (*p == '[') {
			char *q = p + 1;
			if (*q == '!')
				q++;
			for (;;) {
				if (*q == '\\')
					q++;
				if (*q == '/' || *q == '\0')
					break;
				if (*++q == ']') {
					metaflag = 1;
					break;
				}
			}
		} else if (*p == '\\')
			p++;
		else if (*p == '/') {
			if (metaflag)
				goto out;
			start = p + 1;
		}
	}
out:
	if (metaflag == 0) {    /* we've reached the end of the file name */
		if (enddir != expdir)
			metaflag++;
		p = name;
		do {
			if (*p == '\\')
				p++;
			*enddir++ = *p;
		} while (*p++);
		if (metaflag == 0 || lstat(expdir, &statb) >= 0)
			addfname(expdir);
		return;
	}
	endname = p;
	if (name < start) {
		p = name;
		do {
			if (*p == '\\')
				p++;
			*enddir++ = *p++;
		} while (p < start);
	}
	if (enddir == expdir) {
		cp = ".";
	} else if (enddir == expdir + 1 && *expdir == '/') {
		cp = "/";
	} else {
		cp = expdir;
		enddir[-1] = '\0';
	}
	if ((dirp = opendir(cp)) == NULL)
		return;
	if (enddir != expdir)
		enddir[-1] = '/';
	if (*endname == 0) {
		atend = 1;
	} else {
		atend = 0;
		*endname++ = '\0';
	}
	matchdot = 0;
	p = start;
	if (*p == '\\')
		p++;
	if (*p == '.')
		matchdot++;
	while (! intpending && (dp = readdir(dirp)) != NULL) {
		if (dp->d_name[0] == '.' && ! matchdot)
			continue;
		if (pmatch(start, dp->d_name)) {
			if (atend) {
				scopy(dp->d_name, enddir);
				addfname(expdir);
			} else {
				for (p = enddir, cp = dp->d_name;
				     (*p++ = *cp++) != '\0';)
					continue;
				p[-1] = '/';
				expmeta(p, endname);
			}
		}
	}
	closedir(dirp);
	if (! atend)
		endname[-1] = '/';
}

/*
 * Sort the results of file name expansion.  It calculates the number of
 * strings to sort and then calls msort (short for merge sort) to do the
 * work.
 */

static struct strlist *
expsort(struct strlist *str)
{
	int len;
	struct strlist *sp;

	len = 0;
	for (sp = str ; sp ; sp = sp->next)
		len++;
	return msort(str, len);
}


static struct strlist *
msort(struct strlist *list, int len)
{
	struct strlist *p, *q = NULL;
	struct strlist **lpp;
	int half;
	int n;

	if (len <= 1)
		return list;
	half = len >> 1;
	p = list;
	for (n = half ; --n >= 0 ; ) {
		q = p;
		p = p->next;
	}
	q->next = NULL;                 /* terminate first half of list */
	q = msort(list, half);          /* sort first half of list */
	p = msort(p, len - half);               /* sort second half */
	lpp = &list;
	for (;;) {
#ifdef CONFIG_LOCALE_SUPPORT
		if (strcoll(p->text, q->text) < 0)
#else
		if (strcmp(p->text, q->text) < 0)
#endif
						{
			*lpp = p;
			lpp = &p->next;
			if ((p = *lpp) == NULL) {
				*lpp = q;
				break;
			}
		} else {
			*lpp = q;
			lpp = &q->next;
			if ((q = *lpp) == NULL) {
				*lpp = p;
				break;
			}
		}
	}
	return list;
}


/*
 * Returns true if the pattern matches the string.
 */

static inline int
patmatch(char *pattern, const char *string)
{
	return pmatch(preglob(pattern, 0, 0), string);
}


/*
 * Remove any CTLESC characters from a string.
 */

static char *
_rmescapes(char *str, int flag)
{
	char *p, *q, *r;
	static const char qchars[] = { CTLESC, CTLQUOTEMARK, 0 };
	unsigned inquotes;
	int notescaped;
	int globbing;

	p = strpbrk(str, qchars);
	if (!p) {
		return str;
	}
	q = p;
	r = str;
	if (flag & RMESCAPE_ALLOC) {
		size_t len = p - str;
		size_t fulllen = len + strlen(p) + 1;

		if (flag & RMESCAPE_GROW) {
			r = makestrspace(fulllen, expdest);
		} else if (flag & RMESCAPE_HEAP) {
			r = ckmalloc(fulllen);
		} else {
			r = stalloc(fulllen);
		}
		q = r;
		if (len > 0) {
			q = mempcpy(q, str, len);
		}
	}
	inquotes = (flag & RMESCAPE_QUOTED) ^ RMESCAPE_QUOTED;
	globbing = flag & RMESCAPE_GLOB;
	notescaped = globbing;
	while (*p) {
		if (*p == CTLQUOTEMARK) {
			inquotes = ~inquotes;
			p++;
			notescaped = globbing;
			continue;
		}
		if (*p == '\\') {
			/* naked back slash */
			notescaped = 0;
			goto copy;
		}
		if (*p == CTLESC) {
			p++;
			if (notescaped && inquotes && *p != '/') {
				*q++ = '\\';
			}
		}
		notescaped = globbing;
copy:
		*q++ = *p++;
	}
	*q = '\0';
	if (flag & RMESCAPE_GROW) {
		expdest = r;
		STADJUST(q - r + 1, expdest);
	}
	return r;
}


/*
 * See if a pattern matches in a case statement.
 */

int
casematch(union node *pattern, char *val)
{
	struct stackmark smark;
	int result;

	setstackmark(&smark);
	argbackq = pattern->narg.backquote;
	STARTSTACKSTR(expdest);
	ifslastp = NULL;
	argstr(pattern->narg.text, EXP_TILDE | EXP_CASE);
	STACKSTRNUL(expdest);
	result = patmatch(stackblock(), val);
	popstackmark(&smark);
	return result;
}

/*
 * Our own itoa().
 */

static int
cvtnum(arith_t num)
{
	int len;

	expdest = makestrspace(32, expdest);
#ifdef CONFIG_ASH_MATH_SUPPORT_64
	len = fmtstr(expdest, 32, "%lld", (long long) num);
#else
	len = fmtstr(expdest, 32, "%ld", num);
#endif
	STADJUST(len, expdest);
	return len;
}

static void
varunset(const char *end, const char *var, const char *umsg, int varflags)
{
	const char *msg;
	const char *tail;

	tail = nullstr;
	msg = "parameter not set";
	if (umsg) {
		if (*end == CTLENDVAR) {
			if (varflags & VSNUL)
				tail = " or null";
		} else
			msg = umsg;
	}
	sh_error("%.*s: %s%s", end - var - 1, var, msg, tail);
}


/*      input.c      */

/*
 * This implements the input routines used by the parser.
 */

#define EOF_NLEFT -99           /* value of parsenleft when EOF pushed back */

static void pushfile(void);

/*
 * Read a character from the script, returning PEOF on end of file.
 * Nul characters in the input are silently discarded.
 */


#define pgetc_as_macro()   (--parsenleft >= 0? SC2INT(*parsenextc++) : preadbuffer())

#ifdef CONFIG_ASH_OPTIMIZE_FOR_SIZE
#define pgetc_macro() pgetc()
static int
pgetc(void)
{
	return pgetc_as_macro();
}
#else
#define pgetc_macro()   pgetc_as_macro()
static int
pgetc(void)
{
	return pgetc_macro();
}
#endif


/*
 * Same as pgetc(), but ignores PEOA.
 */
#ifdef CONFIG_ASH_ALIAS
static int pgetc2(void)
{
	int c;

	do {
		c = pgetc_macro();
	} while (c == PEOA);
	return c;
}
#else
static inline int pgetc2(void)
{
	return pgetc_macro();
}
#endif

/*
 * Read a line from the script.
 */

static inline char *
pfgets(char *line, int len)
{
	char *p = line;
	int nleft = len;
	int c;

	while (--nleft > 0) {
		c = pgetc2();
		if (c == PEOF) {
			if (p == line)
				return NULL;
			break;
		}
		*p++ = c;
		if (c == '\n')
			break;
	}
	*p = '\0';
	return line;
}



#ifdef CONFIG_FEATURE_COMMAND_EDITING
#ifdef CONFIG_ASH_EXPAND_PRMT
static char *cmdedit_prompt;
#else
static const char *cmdedit_prompt;
#endif
static inline void putprompt(const char *s)
{
#ifdef CONFIG_ASH_EXPAND_PRMT
	free(cmdedit_prompt);
	cmdedit_prompt = bb_xstrdup(s);
#else
	cmdedit_prompt = s;
#endif
}
#else
static inline void putprompt(const char *s)
{
	out2str(s);
}
#endif

static inline int
preadfd(void)
{
	int nr;
	char *buf =  parsefile->buf;
	parsenextc = buf;

retry:
#ifdef CONFIG_FEATURE_COMMAND_EDITING
	if (!iflag || parsefile->fd)
		nr = safe_read(parsefile->fd, buf, BUFSIZ - 1);
	else {
#ifdef CONFIG_FEATURE_COMMAND_TAB_COMPLETION
		cmdedit_path_lookup = pathval();
#endif
		nr = cmdedit_read_input((char *) cmdedit_prompt, buf);
		if(nr == 0) {
			/* Ctrl+C presend */
			if(trap[SIGINT]) {
				buf[0] = '\n';
				buf[1] = 0;
				raise(SIGINT);
				return 1;
			}
			goto retry;
		}
		if(nr < 0 && errno == 0) {
			/* Ctrl+D presend */
			nr = 0;
		}
	}
#else
	nr = safe_read(parsefile->fd, buf, BUFSIZ - 1);
#endif

	if (nr < 0) {
		if (parsefile->fd == 0 && errno == EWOULDBLOCK) {
			int flags = fcntl(0, F_GETFL, 0);
			if (flags >= 0 && flags & O_NONBLOCK) {
				flags &=~ O_NONBLOCK;
				if (fcntl(0, F_SETFL, flags) >= 0) {
					out2str("sh: turning off NDELAY mode\n");
					goto retry;
				}
			}
		}
	}
	return nr;
}

/*
 * Refill the input buffer and return the next input character:
 *
 * 1) If a string was pushed back on the input, pop it;
 * 2) If an EOF was pushed back (parsenleft == EOF_NLEFT) or we are reading
 *    from a string so we can't refill the buffer, return EOF.
 * 3) If the is more stuff in this buffer, use it else call read to fill it.
 * 4) Process input up to the next newline, deleting nul characters.
 */

int
preadbuffer(void)
{
	char *q;
	int more;
	char savec;

	while (parsefile->strpush) {
#ifdef CONFIG_ASH_ALIAS
		if (parsenleft == -1 && parsefile->strpush->ap &&
			parsenextc[-1] != ' ' && parsenextc[-1] != '\t') {
			return PEOA;
		}
#endif
		popstring();
		if (--parsenleft >= 0)
			return SC2INT(*parsenextc++);
	}
	if (parsenleft == EOF_NLEFT || parsefile->buf == NULL)
		return PEOF;
	flushall();

	more = parselleft;
	if (more <= 0) {
again:
		if ((more = preadfd()) <= 0) {
			parselleft = parsenleft = EOF_NLEFT;
			return PEOF;
		}
	}

	q = parsenextc;

	/* delete nul characters */
	for (;;) {
		int c;

		more--;
		c = *q;

		if (!c)
			memmove(q, q + 1, more);
		else {
			q++;
			if (c == '\n') {
				parsenleft = q - parsenextc - 1;
				break;
			}
		}

		if (more <= 0) {
			parsenleft = q - parsenextc - 1;
			if (parsenleft < 0)
				goto again;
			break;
		}
	}
	parselleft = more;

	savec = *q;
	*q = '\0';

	if (vflag) {
		out2str(parsenextc);
	}

	*q = savec;

	return SC2INT(*parsenextc++);
}

/*
 * Undo the last call to pgetc.  Only one character may be pushed back.
 * PEOF may be pushed back.
 */

void
pungetc(void)
{
	parsenleft++;
	parsenextc--;
}

/*
 * Push a string back onto the input at this current parsefile level.
 * We handle aliases this way.
 */
void
pushstring(char *s, void *ap)
{
	struct strpush *sp;
	size_t len;

	len = strlen(s);
	INTOFF;
/*dprintf("*** calling pushstring: %s, %d\n", s, len);*/
	if (parsefile->strpush) {
		sp = ckmalloc(sizeof (struct strpush));
		sp->prev = parsefile->strpush;
		parsefile->strpush = sp;
	} else
		sp = parsefile->strpush = &(parsefile->basestrpush);
	sp->prevstring = parsenextc;
	sp->prevnleft = parsenleft;
#ifdef CONFIG_ASH_ALIAS
	sp->ap = (struct alias *)ap;
	if (ap) {
		((struct alias *)ap)->flag |= ALIASINUSE;
		sp->string = s;
	}
#endif
	parsenextc = s;
	parsenleft = len;
	INTON;
}

void
popstring(void)
{
	struct strpush *sp = parsefile->strpush;

	INTOFF;
#ifdef CONFIG_ASH_ALIAS
	if (sp->ap) {
		if (parsenextc[-1] == ' ' || parsenextc[-1] == '\t') {
			checkkwd |= CHKALIAS;
		}
		if (sp->string != sp->ap->val) {
			ckfree(sp->string);
		}
		sp->ap->flag &= ~ALIASINUSE;
		if (sp->ap->flag & ALIASDEAD) {
			unalias(sp->ap->name);
		}
	}
#endif
	parsenextc = sp->prevstring;
	parsenleft = sp->prevnleft;
/*dprintf("*** calling popstring: restoring to '%s'\n", parsenextc);*/
	parsefile->strpush = sp->prev;
	if (sp != &(parsefile->basestrpush))
		ckfree(sp);
	INTON;
}

/*
 * Set the input to take input from a file.  If push is set, push the
 * old input onto the stack first.
 */

static int
setinputfile(const char *fname, int flags)
{
	int fd;
	int fd2;

	INTOFF;
	if ((fd = open(fname, O_RDONLY)) < 0) {
		if (flags & INPUT_NOFILE_OK)
			goto out;
		sh_error("Can't open %s", fname);
	}
	if (fd < 10) {
		fd2 = copyfd(fd, 10);
		close(fd);
		if (fd2 < 0)
			sh_error("Out of file descriptors");
		fd = fd2;
	}
	setinputfd(fd, flags & INPUT_PUSH_FILE);
out:
	INTON;
	return fd;
}


/*
 * Like setinputfile, but takes an open file descriptor.  Call this with
 * interrupts off.
 */

static void
setinputfd(int fd, int push)
{
	(void) fcntl(fd, F_SETFD, FD_CLOEXEC);
	if (push) {
		pushfile();
		parsefile->buf = 0;
	}
	parsefile->fd = fd;
	if (parsefile->buf == NULL)
		parsefile->buf = ckmalloc(IBUFSIZ);
	parselleft = parsenleft = 0;
	plinno = 1;
}


/*
 * Like setinputfile, but takes input from a string.
 */

static void
setinputstring(char *string)
{
	INTOFF;
	pushfile();
	parsenextc = string;
	parsenleft = strlen(string);
	parsefile->buf = NULL;
	plinno = 1;
	INTON;
}


/*
 * To handle the "." command, a stack of input files is used.  Pushfile
 * adds a new entry to the stack and popfile restores the previous level.
 */

static void
pushfile(void)
{
	struct parsefile *pf;

	parsefile->nleft = parsenleft;
	parsefile->lleft = parselleft;
	parsefile->nextc = parsenextc;
	parsefile->linno = plinno;
	pf = (struct parsefile *)ckmalloc(sizeof (struct parsefile));
	pf->prev = parsefile;
	pf->fd = -1;
	pf->strpush = NULL;
	pf->basestrpush.prev = NULL;
	parsefile = pf;
}


static void
popfile(void)
{
	struct parsefile *pf = parsefile;

	INTOFF;
	if (pf->fd >= 0)
		close(pf->fd);
	if (pf->buf)
		ckfree(pf->buf);
	while (pf->strpush)
		popstring();
	parsefile = pf->prev;
	ckfree(pf);
	parsenleft = parsefile->nleft;
	parselleft = parsefile->lleft;
	parsenextc = parsefile->nextc;
	plinno = parsefile->linno;
	INTON;
}


/*
 * Return to top level.
 */

static void
popallfiles(void)
{
	while (parsefile != &basepf)
		popfile();
}


/*
 * Close the file(s) that the shell is reading commands from.  Called
 * after a fork is done.
 */

static void
closescript(void)
{
	popallfiles();
	if (parsefile->fd > 0) {
		close(parsefile->fd);
		parsefile->fd = 0;
	}
}

/*      jobs.c    */

/* mode flags for set_curjob */
#define CUR_DELETE 2
#define CUR_RUNNING 1
#define CUR_STOPPED 0

/* mode flags for dowait */
#define DOWAIT_NORMAL 0
#define DOWAIT_BLOCK 1

/* array of jobs */
static struct job *jobtab;
/* size of array */
static unsigned njobs;
#if JOBS
/* pgrp of shell on invocation */
static int initialpgrp;
static int ttyfd = -1;
#endif
/* current job */
static struct job *curjob;
/* number of presumed living untracked jobs */
static int jobless;

static void set_curjob(struct job *, unsigned);
#if JOBS
static int restartjob(struct job *, int);
static void xtcsetpgrp(int, pid_t);
static char *commandtext(union node *);
static void cmdlist(union node *, int);
static void cmdtxt(union node *);
static void cmdputs(const char *);
static void showpipe(struct job *, FILE *);
#endif
static int sprint_status(char *, int, int);
static void freejob(struct job *);
static struct job *getjob(const char *, int);
static struct job *growjobtab(void);
static void forkchild(struct job *, union node *, int);
static void forkparent(struct job *, union node *, int, pid_t);
static int dowait(int, struct job *);
static int getstatus(struct job *);

static void
set_curjob(struct job *jp, unsigned mode)
{
	struct job *jp1;
	struct job **jpp, **curp;

	/* first remove from list */
	jpp = curp = &curjob;
	do {
		jp1 = *jpp;
		if (jp1 == jp)
			break;
		jpp = &jp1->prev_job;
	} while (1);
	*jpp = jp1->prev_job;

	/* Then re-insert in correct position */
	jpp = curp;
	switch (mode) {
	default:
#ifdef DEBUG
		abort();
#endif
	case CUR_DELETE:
		/* job being deleted */
		break;
	case CUR_RUNNING:
		/* newly created job or backgrounded job,
		   put after all stopped jobs. */
		do {
			jp1 = *jpp;
#if JOBS
			if (!jp1 || jp1->state != JOBSTOPPED)
#endif
				break;
			jpp = &jp1->prev_job;
		} while (1);
		/* FALLTHROUGH */
#if JOBS
	case CUR_STOPPED:
#endif
		/* newly stopped job - becomes curjob */
		jp->prev_job = *jpp;
		*jpp = jp;
		break;
	}
}

#if JOBS
/*
 * Turn job control on and off.
 *
 * Note:  This code assumes that the third arg to ioctl is a character
 * pointer, which is true on Berkeley systems but not System V.  Since
 * System V doesn't have job control yet, this isn't a problem now.
 *
 * Called with interrupts off.
 */

void
setjobctl(int on)
{
	int fd;
	int pgrp;

	if (on == jobctl || rootshell == 0)
		return;
	if (on) {
		int ofd;
		ofd = fd = open(_PATH_TTY, O_RDWR);
		if (fd < 0) {
			fd += 3;
			while (!isatty(fd) && --fd >= 0)
				;
		}
		fd = fcntl(fd, F_DUPFD, 10);
		close(ofd);
		if (fd < 0)
			goto out;
		fcntl(fd, F_SETFD, FD_CLOEXEC);
		do { /* while we are in the background */
			if ((pgrp = tcgetpgrp(fd)) < 0) {
out:
				sh_warnx("can't access tty; job control turned off");
				mflag = on = 0;
				goto close;
			}
			if (pgrp == getpgrp())
				break;
			killpg(0, SIGTTIN);
		} while (1);
		initialpgrp = pgrp;

		setsignal(SIGTSTP);
		setsignal(SIGTTOU);
		setsignal(SIGTTIN);
		pgrp = rootpid;
		setpgid(0, pgrp);
		xtcsetpgrp(fd, pgrp);
	} else {
		/* turning job control off */
		fd = ttyfd;
		pgrp = initialpgrp;
		xtcsetpgrp(fd, pgrp);
		setpgid(0, pgrp);
		setsignal(SIGTSTP);
		setsignal(SIGTTOU);
		setsignal(SIGTTIN);
close:
		close(fd);
		fd = -1;
	}
	ttyfd = fd;
	jobctl = on;
}

static int
killcmd(int argc, char **argv)
{
	int signo = -1;
	int list = 0;
	int i;
	pid_t pid;
	struct job *jp;

	if (argc <= 1) {
usage:
		sh_error(
"Usage: kill [-s sigspec | -signum | -sigspec] [pid | job]... or\n"
"kill -l [exitstatus]"
		);
	}

	if (**++argv == '-') {
		signo = decode_signal(*argv + 1, 1);
		if (signo < 0) {
			int c;

			while ((c = nextopt("ls:")) != '\0')
				switch (c) {
				default:
#ifdef DEBUG
					abort();
#endif
				case 'l':
					list = 1;
					break;
				case 's':
					signo = decode_signal(optionarg, 1);
					if (signo < 0) {
						sh_error(
							"invalid signal number or name: %s",
							optionarg
						);
					}
					break;
				}
			argv = argptr;
		} else
			argv++;
	}

	if (!list && signo < 0)
		signo = SIGTERM;

	if ((signo < 0 || !*argv) ^ list) {
		goto usage;
	}

	if (list) {
		const char *name;

		if (!*argv) {
			for (i = 1; i < NSIG; i++) {
				name = u_signal_names(0, &i, 1);
				if (name)
					out1fmt(snlfmt, name);
			}
			return 0;
		}
		name = u_signal_names(*argptr, &signo, -1);
		if (name)
			out1fmt(snlfmt, name);
		else
			sh_error("invalid signal number or exit status: %s", *argptr);
		return 0;
	}

	i = 0;
	do {
		if (**argv == '%') {
			jp = getjob(*argv, 0);
			pid = -jp->ps[0].pid;
		} else {
			pid = **argv == '-' ?
				-number(*argv + 1) : number(*argv);
		}
		if (kill(pid, signo) != 0) {
			sh_warnx("(%d) - %m", pid);
			i = 1;
		}
	} while (*++argv);

	return i;
}
#endif /* JOBS */

#if defined(JOBS) || defined(DEBUG)
static int
jobno(const struct job *jp)
{
	return jp - jobtab + 1;
}
#endif

#if JOBS
static int
fgcmd(int argc, char **argv)
{
	struct job *jp;
	FILE *out;
	int mode;
	int retval;

	mode = (**argv == 'f') ? FORK_FG : FORK_BG;
	nextopt(nullstr);
	argv = argptr;
	out = stdout;
	do {
		jp = getjob(*argv, 1);
		if (mode == FORK_BG) {
			set_curjob(jp, CUR_RUNNING);
			fprintf(out, "[%d] ", jobno(jp));
		}
		outstr(jp->ps->cmd, out);
		showpipe(jp, out);
		retval = restartjob(jp, mode);
	} while (*argv && *++argv);
	return retval;
}

static int bgcmd(int, char **) __attribute__((__alias__("fgcmd")));


static int
restartjob(struct job *jp, int mode)
{
	struct procstat *ps;
	int i;
	int status;
	pid_t pgid;

	INTOFF;
	if (jp->state == JOBDONE)
		goto out;
	jp->state = JOBRUNNING;
	pgid = jp->ps->pid;
	if (mode == FORK_FG)
		xtcsetpgrp(ttyfd, pgid);
	killpg(pgid, SIGCONT);
	ps = jp->ps;
	i = jp->nprocs;
	do {
		if (WIFSTOPPED(ps->status)) {
			ps->status = -1;
		}
	} while (ps++, --i);
out:
	status = (mode == FORK_FG) ? waitforjob(jp) : 0;
	INTON;
	return status;
}
#endif

static int
sprint_status(char *s, int status, int sigonly)
{
	int col;
	int st;

	col = 0;
	if (!WIFEXITED(status)) {
#if JOBS
		if (WIFSTOPPED(status))
			st = WSTOPSIG(status);
		else
#endif
			st = WTERMSIG(status);
		if (sigonly) {
			if (st == SIGINT || st == SIGPIPE)
				goto out;
#if JOBS
			if (WIFSTOPPED(status))
				goto out;
#endif
		}
		st &= 0x7f;
		col = fmtstr(s, 32, strsignal(st));
		if (WCOREDUMP(status)) {
			col += fmtstr(s + col, 16, " (core dumped)");
		}
	} else if (!sigonly) {
		st = WEXITSTATUS(status);
		if (st)
			col = fmtstr(s, 16, "Done(%d)", st);
		else
			col = fmtstr(s, 16, "Done");
	}

out:
	return col;
}

#if JOBS
static void
showjob(FILE *out, struct job *jp, int mode)
{
	struct procstat *ps;
	struct procstat *psend;
	int col;
	int indent;
	char s[80];

	ps = jp->ps;

	if (mode & SHOW_PGID) {
		/* just output process (group) id of pipeline */
		fprintf(out, "%d\n", ps->pid);
		return;
	}

	col = fmtstr(s, 16, "[%d]   ", jobno(jp));
	indent = col;

	if (jp == curjob)
		s[col - 2] = '+';
	else if (curjob && jp == curjob->prev_job)
		s[col - 2] = '-';

	if (mode & SHOW_PID)
		col += fmtstr(s + col, 16, "%d ", ps->pid);

	psend = ps + jp->nprocs;

	if (jp->state == JOBRUNNING) {
		scopy("Running", s + col);
		col += strlen("Running");
	} else {
		int status = psend[-1].status;
#if JOBS
		if (jp->state == JOBSTOPPED)
			status = jp->stopstatus;
#endif
		col += sprint_status(s + col, status, 0);
	}

	goto start;

	do {
		/* for each process */
		col = fmtstr(s, 48, " |\n%*c%d ", indent, ' ', ps->pid) - 3;

start:
		fprintf(out, "%s%*c%s",
			s, 33 - col >= 0 ? 33 - col : 0, ' ', ps->cmd
		);
		if (!(mode & SHOW_PID)) {
			showpipe(jp, out);
			break;
		}
		if (++ps == psend) {
			outcslow('\n', out);
			break;
		}
	} while (1);

	jp->changed = 0;

	if (jp->state == JOBDONE) {
		TRACE(("showjob: freeing job %d\n", jobno(jp)));
		freejob(jp);
	}
}


static int
jobscmd(int argc, char **argv)
{
	int mode, m;
	FILE *out;

	mode = 0;
	while ((m = nextopt("lp")))
		if (m == 'l')
			mode = SHOW_PID;
		else
			mode = SHOW_PGID;

	out = stdout;
	argv = argptr;
	if (*argv)
		do
			showjob(out, getjob(*argv,0), mode);
		while (*++argv);
	else
		showjobs(out, mode);

	return 0;
}


/*
 * Print a list of jobs.  If "change" is nonzero, only print jobs whose
 * statuses have changed since the last call to showjobs.
 */

static void
showjobs(FILE *out, int mode)
{
	struct job *jp;

	TRACE(("showjobs(%x) called\n", mode));

	/* If not even one one job changed, there is nothing to do */
	while (dowait(DOWAIT_NORMAL, NULL) > 0)
		continue;

	for (jp = curjob; jp; jp = jp->prev_job) {
		if (!(mode & SHOW_CHANGED) || jp->changed)
			showjob(out, jp, mode);
	}
}
#endif /* JOBS */

/*
 * Mark a job structure as unused.
 */

static void
freejob(struct job *jp)
{
	struct procstat *ps;
	int i;

	INTOFF;
	for (i = jp->nprocs, ps = jp->ps ; --i >= 0 ; ps++) {
		if (ps->cmd != nullstr)
			ckfree(ps->cmd);
	}
	if (jp->ps != &jp->ps0)
		ckfree(jp->ps);
	jp->used = 0;
	set_curjob(jp, CUR_DELETE);
	INTON;
}


static int
waitcmd(int argc, char **argv)
{
	struct job *job;
	int retval;
	struct job *jp;

	EXSIGON();

	nextopt(nullstr);
	retval = 0;

	argv = argptr;
	if (!*argv) {
		/* wait for all jobs */
		for (;;) {
			jp = curjob;
			while (1) {
				if (!jp) {
					/* no running procs */
					goto out;
				}
				if (jp->state == JOBRUNNING)
					break;
				jp->waited = 1;
				jp = jp->prev_job;
			}
			dowait(DOWAIT_BLOCK, 0);
		}
	}

	retval = 127;
	do {
		if (**argv != '%') {
			pid_t pid = number(*argv);
			job = curjob;
			goto start;
			do {
				if (job->ps[job->nprocs - 1].pid == pid)
					break;
				job = job->prev_job;
start:
				if (!job)
					goto repeat;
			} while (1);
		} else
			job = getjob(*argv, 0);
		/* loop until process terminated or stopped */
		while (job->state == JOBRUNNING)
			dowait(DOWAIT_BLOCK, 0);
		job->waited = 1;
		retval = getstatus(job);
repeat:
		;
	} while (*++argv);

out:
	return retval;
}


/*
 * Convert a job name to a job structure.
 */

static struct job *
getjob(const char *name, int getctl)
{
	struct job *jp;
	struct job *found;
	const char *err_msg = "No such job: %s";
	unsigned num;
	int c;
	const char *p;
	char *(*match)(const char *, const char *);

	jp = curjob;
	p = name;
	if (!p)
		goto currentjob;

	if (*p != '%')
		goto err;

	c = *++p;
	if (!c)
		goto currentjob;

	if (!p[1]) {
		if (c == '+' || c == '%') {
currentjob:
			err_msg = "No current job";
			goto check;
		} else if (c == '-') {
			if (jp)
				jp = jp->prev_job;
			err_msg = "No previous job";
check:
			if (!jp)
				goto err;
			goto gotit;
		}
	}

	if (is_number(p)) {
		num = atoi(p);
		if (num < njobs) {
			jp = jobtab + num - 1;
			if (jp->used)
				goto gotit;
			goto err;
		}
	}

	match = prefix;
	if (*p == '?') {
		match = strstr;
		p++;
	}

	found = 0;
	while (1) {
		if (!jp)
			goto err;
		if (match(jp->ps[0].cmd, p)) {
			if (found)
				goto err;
			found = jp;
			err_msg = "%s: ambiguous";
		}
		jp = jp->prev_job;
	}

gotit:
#if JOBS
	err_msg = "job %s not created under job control";
	if (getctl && jp->jobctl == 0)
		goto err;
#endif
	return jp;
err:
	sh_error(err_msg, name);
}


/*
 * Return a new job structure.
 * Called with interrupts off.
 */

static struct job *
makejob(union node *node, int nprocs)
{
	int i;
	struct job *jp;

	for (i = njobs, jp = jobtab ; ; jp++) {
		if (--i < 0) {
			jp = growjobtab();
			break;
		}
		if (jp->used == 0)
			break;
		if (jp->state != JOBDONE || !jp->waited)
			continue;
#if JOBS
		if (jobctl)
			continue;
#endif
		freejob(jp);
		break;
	}
	memset(jp, 0, sizeof(*jp));
#if JOBS
	if (jobctl)
		jp->jobctl = 1;
#endif
	jp->prev_job = curjob;
	curjob = jp;
	jp->used = 1;
	jp->ps = &jp->ps0;
	if (nprocs > 1) {
		jp->ps = ckmalloc(nprocs * sizeof (struct procstat));
	}
	TRACE(("makejob(0x%lx, %d) returns %%%d\n", (long)node, nprocs,
	    jobno(jp)));
	return jp;
}

static struct job *
growjobtab(void)
{
	size_t len;
	ptrdiff_t offset;
	struct job *jp, *jq;

	len = njobs * sizeof(*jp);
	jq = jobtab;
	jp = ckrealloc(jq, len + 4 * sizeof(*jp));

	offset = (char *)jp - (char *)jq;
	if (offset) {
		/* Relocate pointers */
		size_t l = len;

		jq = (struct job *)((char *)jq + l);
		while (l) {
			l -= sizeof(*jp);
			jq--;
#define joff(p) ((struct job *)((char *)(p) + l))
#define jmove(p) (p) = (void *)((char *)(p) + offset)
			if (xlikely(joff(jp)->ps == &jq->ps0))
				jmove(joff(jp)->ps);
			if (joff(jp)->prev_job)
				jmove(joff(jp)->prev_job);
		}
		if (curjob)
			jmove(curjob);
#undef joff
#undef jmove
	}

	njobs += 4;
	jobtab = jp;
	jp = (struct job *)((char *)jp + len);
	jq = jp + 3;
	do {
		jq->used = 0;
	} while (--jq >= jp);
	return jp;
}


/*
 * Fork off a subshell.  If we are doing job control, give the subshell its
 * own process group.  Jp is a job structure that the job is to be added to.
 * N is the command that will be evaluated by the child.  Both jp and n may
 * be NULL.  The mode parameter can be one of the following:
 *      FORK_FG - Fork off a foreground process.
 *      FORK_BG - Fork off a background process.
 *      FORK_NOJOB - Like FORK_FG, but don't give the process its own
 *                   process group even if job control is on.
 *
 * When job control is turned off, background processes have their standard
 * input redirected to /dev/null (except for the second and later processes
 * in a pipeline).
 *
 * Called with interrupts off.
 */

static inline void
forkchild(struct job *jp, union node *n, int mode)
{
	int oldlvl;

	TRACE(("Child shell %d\n", getpid()));
	oldlvl = shlvl;
	shlvl++;

	closescript();
	clear_traps();
#if JOBS
	/* do job control only in root shell */
	jobctl = 0;
	if (mode != FORK_NOJOB && jp->jobctl && !oldlvl) {
		pid_t pgrp;

		if (jp->nprocs == 0)
			pgrp = getpid();
		else
			pgrp = jp->ps[0].pid;
		/* This can fail because we are doing it in the parent also */
		(void)setpgid(0, pgrp);
		if (mode == FORK_FG)
			xtcsetpgrp(ttyfd, pgrp);
		setsignal(SIGTSTP);
		setsignal(SIGTTOU);
	} else
#endif
	if (mode == FORK_BG) {
		ignoresig(SIGINT);
		ignoresig(SIGQUIT);
		if (jp->nprocs == 0) {
			close(0);
			if (open(bb_dev_null, O_RDONLY) != 0)
				sh_error("Can't open %s", bb_dev_null);
		}
	}
	if (!oldlvl && iflag) {
		setsignal(SIGINT);
		setsignal(SIGQUIT);
		setsignal(SIGTERM);
	}
	for (jp = curjob; jp; jp = jp->prev_job)
		freejob(jp);
	jobless = 0;
}

static inline void
forkparent(struct job *jp, union node *n, int mode, pid_t pid)
{
	TRACE(("In parent shell:  child = %d\n", pid));
	if (!jp) {
		while (jobless && dowait(DOWAIT_NORMAL, 0) > 0);
		jobless++;
		return;
	}
#if JOBS
	if (mode != FORK_NOJOB && jp->jobctl) {
		int pgrp;

		if (jp->nprocs == 0)
			pgrp = pid;
		else
			pgrp = jp->ps[0].pid;
		/* This can fail because we are doing it in the child also */
		(void)setpgid(pid, pgrp);
	}
#endif
	if (mode == FORK_BG) {
		backgndpid = pid;               /* set $! */
		set_curjob(jp, CUR_RUNNING);
	}
	if (jp) {
		struct procstat *ps = &jp->ps[jp->nprocs++];
		ps->pid = pid;
		ps->status = -1;
		ps->cmd = nullstr;
#if JOBS
		if (jobctl && n)
			ps->cmd = commandtext(n);
#endif
	}
}

static int
forkshell(struct job *jp, union node *n, int mode)
{
	int pid;

	TRACE(("forkshell(%%%d, %p, %d) called\n", jobno(jp), n, mode));
	pid = fork();
	if (pid < 0) {
		TRACE(("Fork failed, errno=%d", errno));
		if (jp)
			freejob(jp);
		sh_error("Cannot fork");
	}
	if (pid == 0)
		forkchild(jp, n, mode);
	else
		forkparent(jp, n, mode, pid);
	return pid;
}

/*
 * Wait for job to finish.
 *
 * Under job control we have the problem that while a child process is
 * running interrupts generated by the user are sent to the child but not
 * to the shell.  This means that an infinite loop started by an inter-
 * active user may be hard to kill.  With job control turned off, an
 * interactive user may place an interactive program inside a loop.  If
 * the interactive program catches interrupts, the user doesn't want
 * these interrupts to also abort the loop.  The approach we take here
 * is to have the shell ignore interrupt signals while waiting for a
 * foreground process to terminate, and then send itself an interrupt
 * signal if the child process was terminated by an interrupt signal.
 * Unfortunately, some programs want to do a bit of cleanup and then
 * exit on interrupt; unless these processes terminate themselves by
 * sending a signal to themselves (instead of calling exit) they will
 * confuse this approach.
 *
 * Called with interrupts off.
 */

int
waitforjob(struct job *jp)
{
	int st;

	TRACE(("waitforjob(%%%d) called\n", jobno(jp)));
	while (jp->state == JOBRUNNING) {
		dowait(DOWAIT_BLOCK, jp);
	}
	st = getstatus(jp);
#if JOBS
	if (jp->jobctl) {
		xtcsetpgrp(ttyfd, rootpid);
		/*
		 * This is truly gross.
		 * If we're doing job control, then we did a TIOCSPGRP which
		 * caused us (the shell) to no longer be in the controlling
		 * session -- so we wouldn't have seen any ^C/SIGINT.  So, we
		 * intuit from the subprocess exit status whether a SIGINT
		 * occurred, and if so interrupt ourselves.  Yuck.  - mycroft
		 */
		if (jp->sigint)
			raise(SIGINT);
	}
	if (jp->state == JOBDONE)
#endif
		freejob(jp);
	return st;
}


/*
 * Do a wait system call.  If job control is compiled in, we accept
 * stopped processes.  If block is zero, we return a value of zero
 * rather than blocking.
 *
 * System V doesn't have a non-blocking wait system call.  It does
 * have a SIGCLD signal that is sent to a process when one of it's
 * children dies.  The obvious way to use SIGCLD would be to install
 * a handler for SIGCLD which simply bumped a counter when a SIGCLD
 * was received, and have waitproc bump another counter when it got
 * the status of a process.  Waitproc would then know that a wait
 * system call would not block if the two counters were different.
 * This approach doesn't work because if a process has children that
 * have not been waited for, System V will send it a SIGCLD when it
 * installs a signal handler for SIGCLD.  What this means is that when
 * a child exits, the shell will be sent SIGCLD signals continuously
 * until is runs out of stack space, unless it does a wait call before
 * restoring the signal handler.  The code below takes advantage of
 * this (mis)feature by installing a signal handler for SIGCLD and
 * then checking to see whether it was called.  If there are any
 * children to be waited for, it will be.
 *
 * If neither SYSV nor BSD is defined, we don't implement nonblocking
 * waits at all.  In this case, the user will not be informed when
 * a background process until the next time she runs a real program
 * (as opposed to running a builtin command or just typing return),
 * and the jobs command may give out of date information.
 */

static inline int
waitproc(int block, int *status)
{
	int flags = 0;

#if JOBS
	if (jobctl)
		flags |= WUNTRACED;
#endif
	if (block == 0)
		flags |= WNOHANG;
	return wait3(status, flags, (struct rusage *)NULL);
}

/*
 * Wait for a process to terminate.
 */

static int
dowait(int block, struct job *job)
{
	int pid;
	int status;
	struct job *jp;
	struct job *thisjob;
	int state;

	TRACE(("dowait(%d) called\n", block));
	pid = waitproc(block, &status);
	TRACE(("wait returns pid %d, status=%d\n", pid, status));
	if (pid <= 0)
		return pid;
	INTOFF;
	thisjob = NULL;
	for (jp = curjob; jp; jp = jp->prev_job) {
		struct procstat *sp;
		struct procstat *spend;
		if (jp->state == JOBDONE)
			continue;
		state = JOBDONE;
		spend = jp->ps + jp->nprocs;
		sp = jp->ps;
		do {
			if (sp->pid == pid) {
				TRACE(("Job %d: changing status of proc %d from 0x%x to 0x%x\n", jobno(jp), pid, sp->status, status));
				sp->status = status;
				thisjob = jp;
			}
			if (sp->status == -1)
				state = JOBRUNNING;
#if JOBS
			if (state == JOBRUNNING)
				continue;
			if (WIFSTOPPED(sp->status)) {
				jp->stopstatus = sp->status;
				state = JOBSTOPPED;
			}
#endif
		} while (++sp < spend);
		if (thisjob)
			goto gotjob;
	}
#if JOBS
	if (!WIFSTOPPED(status))
#endif

		jobless--;
	goto out;

gotjob:
	if (state != JOBRUNNING) {
		thisjob->changed = 1;

		if (thisjob->state != state) {
			TRACE(("Job %d: changing state from %d to %d\n", jobno(thisjob), thisjob->state, state));
			thisjob->state = state;
#if JOBS
			if (state == JOBSTOPPED) {
				set_curjob(thisjob, CUR_STOPPED);
			}
#endif
		}
	}

out:
	INTON;

	if (thisjob && thisjob == job) {
		char s[48 + 1];
		int len;

		len = sprint_status(s, status, 1);
		if (len) {
			s[len] = '\n';
			s[len + 1] = 0;
			out2str(s);
		}
	}
	return pid;
}


/*
 * return 1 if there are stopped jobs, otherwise 0
 */

int
stoppedjobs(void)
{
	struct job *jp;
	int retval;

	retval = 0;
	if (job_warning)
		goto out;
	jp = curjob;
	if (jp && jp->state == JOBSTOPPED) {
		out2str("You have stopped jobs.\n");
		job_warning = 2;
		retval++;
	}

out:
	return retval;
}

/*
 * Return a string identifying a command (to be printed by the
 * jobs command).
 */

#if JOBS
static char *cmdnextc;

static char *
commandtext(union node *n)
{
	char *name;

	STARTSTACKSTR(cmdnextc);
	cmdtxt(n);
	name = stackblock();
	TRACE(("commandtext: name %p, end %p\n\t\"%s\"\n",
		name, cmdnextc, cmdnextc));
	return savestr(name);
}

static void
cmdtxt(union node *n)
{
	union node *np;
	struct nodelist *lp;
	const char *p;
	char s[2];

	if (!n)
		return;
	switch (n->type) {
	default:
#if DEBUG
		abort();
#endif
	case NPIPE:
		lp = n->npipe.cmdlist;
		for (;;) {
			cmdtxt(lp->n);
			lp = lp->next;
			if (!lp)
				break;
			cmdputs(" | ");
		}
		break;
	case NSEMI:
		p = "; ";
		goto binop;
	case NAND:
		p = " && ";
		goto binop;
	case NOR:
		p = " || ";
binop:
		cmdtxt(n->nbinary.ch1);
		cmdputs(p);
		n = n->nbinary.ch2;
		goto donode;
	case NREDIR:
	case NBACKGND:
		n = n->nredir.n;
		goto donode;
	case NNOT:
		cmdputs("!");
		n = n->nnot.com;
donode:
		cmdtxt(n);
		break;
	case NIF:
		cmdputs("if ");
		cmdtxt(n->nif.test);
		cmdputs("; then ");
		n = n->nif.ifpart;
		if (n->nif.elsepart) {
			cmdtxt(n);
			cmdputs("; else ");
			n = n->nif.elsepart;
		}
		p = "; fi";
		goto dotail;
	case NSUBSHELL:
		cmdputs("(");
		n = n->nredir.n;
		p = ")";
		goto dotail;
	case NWHILE:
		p = "while ";
		goto until;
	case NUNTIL:
		p = "until ";
until:
		cmdputs(p);
		cmdtxt(n->nbinary.ch1);
		n = n->nbinary.ch2;
		p = "; done";
dodo:
		cmdputs("; do ");
dotail:
		cmdtxt(n);
		goto dotail2;
	case NFOR:
		cmdputs("for ");
		cmdputs(n->nfor.var);
		cmdputs(" in ");
		cmdlist(n->nfor.args, 1);
		n = n->nfor.body;
		p = "; done";
		goto dodo;
	case NDEFUN:
		cmdputs(n->narg.text);
		p = "() { ... }";
		goto dotail2;
	case NCMD:
		cmdlist(n->ncmd.args, 1);
		cmdlist(n->ncmd.redirect, 0);
		break;
	case NARG:
		p = n->narg.text;
dotail2:
		cmdputs(p);
		break;
	case NHERE:
	case NXHERE:
		p = "<<...";
		goto dotail2;
	case NCASE:
		cmdputs("case ");
		cmdputs(n->ncase.expr->narg.text);
		cmdputs(" in ");
		for (np = n->ncase.cases; np; np = np->nclist.next) {
			cmdtxt(np->nclist.pattern);
			cmdputs(") ");
			cmdtxt(np->nclist.body);
			cmdputs(";; ");
		}
		p = "esac";
		goto dotail2;
	case NTO:
		p = ">";
		goto redir;
	case NCLOBBER:
		p = ">|";
		goto redir;
	case NAPPEND:
		p = ">>";
		goto redir;
	case NTOFD:
		p = ">&";
		goto redir;
	case NFROM:
		p = "<";
		goto redir;
	case NFROMFD:
		p = "<&";
		goto redir;
	case NFROMTO:
		p = "<>";
redir:
		s[0] = n->nfile.fd + '0';
		s[1] = '\0';
		cmdputs(s);
		cmdputs(p);
		if (n->type == NTOFD || n->type == NFROMFD) {
			s[0] = n->ndup.dupfd + '0';
			p = s;
			goto dotail2;
		} else {
			n = n->nfile.fname;
			goto donode;
		}
	}
}

static void
cmdlist(union node *np, int sep)
{
	for (; np; np = np->narg.next) {
		if (!sep)
			cmdputs(spcstr);
		cmdtxt(np);
		if (sep && np->narg.next)
			cmdputs(spcstr);
	}
}

static void
cmdputs(const char *s)
{
	const char *p, *str;
	char c, cc[2] = " ";
	char *nextc;
	int subtype = 0;
	int quoted = 0;
	static const char vstype[VSTYPE + 1][4] = {
		"", "}", "-", "+", "?", "=",
		"%", "%%", "#", "##"
	};
	nextc = makestrspace((strlen(s) + 1) * 8, cmdnextc);
	p = s;
	while ((c = *p++) != 0) {
		str = 0;
		switch (c) {
		case CTLESC:
			c = *p++;
			break;
		case CTLVAR:
			subtype = *p++;
			if ((subtype & VSTYPE) == VSLENGTH)
				str = "${#";
			else
				str = "${";
			if (!(subtype & VSQUOTE) != !(quoted & 1)) {
				quoted ^= 1;
				c = '"';
			} else
				goto dostr;
			break;
		case CTLENDVAR:
			str = "\"}" + !(quoted & 1);
			quoted >>= 1;
			subtype = 0;
			goto dostr;
		case CTLBACKQ:
			str = "$(...)";
			goto dostr;
		case CTLBACKQ+CTLQUOTE:
			str = "\"$(...)\"";
			goto dostr;
#ifdef CONFIG_ASH_MATH_SUPPORT
		case CTLARI:
			str = "$((";
			goto dostr;
		case CTLENDARI:
			str = "))";
			goto dostr;
#endif
		case CTLQUOTEMARK:
			quoted ^= 1;
			c = '"';
			break;
		case '=':
			if (subtype == 0)
				break;
			if ((subtype & VSTYPE) != VSNORMAL)
				quoted <<= 1;
			str = vstype[subtype & VSTYPE];
			if (subtype & VSNUL)
				c = ':';
			else
				goto checkstr;
			break;
		case '\'':
		case '\\':
		case '"':
		case '$':
			/* These can only happen inside quotes */
			cc[0] = c;
			str = cc;
			c = '\\';
			break;
		default:
			break;
		}
		USTPUTC(c, nextc);
checkstr:
		if (!str)
			continue;
dostr:
		while ((c = *str++)) {
			USTPUTC(c, nextc);
		}
	}
	if (quoted & 1) {
		USTPUTC('"', nextc);
	}
	*nextc = 0;
	cmdnextc = nextc;
}


static void
showpipe(struct job *jp, FILE *out)
{
	struct procstat *sp;
	struct procstat *spend;

	spend = jp->ps + jp->nprocs;
	for (sp = jp->ps + 1; sp < spend; sp++)
		fprintf(out, " | %s", sp->cmd);
	outcslow('\n', out);
	flushall();
}

static void
xtcsetpgrp(int fd, pid_t pgrp)
{
	if (tcsetpgrp(fd, pgrp))
		sh_error("Cannot set tty process group (%m)");
}
#endif /* JOBS */

static int
getstatus(struct job *job) {
	int status;
	int retval;

	status = job->ps[job->nprocs - 1].status;
	retval = WEXITSTATUS(status);
	if (!WIFEXITED(status)) {
#if JOBS
		retval = WSTOPSIG(status);
		if (!WIFSTOPPED(status))
#endif
		{
			/* XXX: limits number of signals */
			retval = WTERMSIG(status);
#if JOBS
			if (retval == SIGINT)
				job->sigint = 1;
#endif
		}
		retval += 128;
	}
	TRACE(("getstatus: job %d, nproc %d, status %x, retval %x\n",
		jobno(job), job->nprocs, status, retval));
	return retval;
}

#ifdef CONFIG_ASH_MAIL
/*      mail.c       */

/*
 * Routines to check for mail.  (Perhaps make part of main.c?)
 */

#define MAXMBOXES 10

/* times of mailboxes */
static time_t mailtime[MAXMBOXES];
/* Set if MAIL or MAILPATH is changed. */
static int mail_var_path_changed;



/*
 * Print appropriate message(s) if mail has arrived.
 * If mail_var_path_changed is set,
 * then the value of MAIL has mail_var_path_changed,
 * so we just update the values.
 */

static void
chkmail(void)
{
	const char *mpath;
	char *p;
	char *q;
	time_t *mtp;
	struct stackmark smark;
	struct stat statb;

	setstackmark(&smark);
	mpath = mpathset() ? mpathval() : mailval();
	for (mtp = mailtime; mtp < mailtime + MAXMBOXES; mtp++) {
		p = padvance(&mpath, nullstr);
		if (p == NULL)
			break;
		if (*p == '\0')
			continue;
		for (q = p ; *q ; q++);
#ifdef DEBUG
		if (q[-1] != '/')
			abort();
#endif
		q[-1] = '\0';                   /* delete trailing '/' */
		if (stat(p, &statb) < 0) {
			*mtp = 0;
			continue;
		}
		if (!mail_var_path_changed && statb.st_mtime != *mtp) {
			fprintf(
				stderr, snlfmt,
				pathopt ? pathopt : "you have mail"
			);
		}
		*mtp = statb.st_mtime;
	}
	mail_var_path_changed = 0;
	popstackmark(&smark);
}


static void
changemail(const char *val)
{
	mail_var_path_changed++;
}

#endif /* CONFIG_ASH_MAIL */

/*      main.c       */


#if PROFILE
static short profile_buf[16384];
extern int etext();
#endif

static int isloginsh;

static void read_profile(const char *);

/*
 * Main routine.  We initialize things, parse the arguments, execute
 * profiles if we're a login shell, and then call cmdloop to execute
 * commands.  The setjmp call sets up the location to jump to when an
 * exception occurs.  When an exception occurs the variable "state"
 * is used to figure out how far we had gotten.
 */

int
ash_main(int argc, char **argv)
{
	char *shinit;
	volatile int state;
	struct jmploc jmploc;
	struct stackmark smark;

#ifdef __GLIBC__
	dash_errno = __errno_location();
#endif

#if PROFILE
	monitor(4, etext, profile_buf, sizeof profile_buf, 50);
#endif
	state = 0;
	if (setjmp(jmploc.loc)) {
		int e;
		int s;

		reset();

		e = exception;
		if (e == EXERROR)
			exitstatus = 2;
		s = state;
		if (e == EXEXIT || s == 0 || iflag == 0 || shlvl)
			exitshell();

		if (e == EXINT) {
			outcslow('\n', stderr);
		}
		popstackmark(&smark);
		FORCEINTON;                             /* enable interrupts */
		if (s == 1)
			goto state1;
		else if (s == 2)
			goto state2;
		else if (s == 3)
			goto state3;
		else
			goto state4;
	}
	handler = &jmploc;
#ifdef DEBUG
	opentrace();
	trputs("Shell args:  ");  trargs(argv);
#endif
	rootpid = getpid();

#ifdef CONFIG_ASH_RANDOM_SUPPORT
	rseed = rootpid + ((time_t)time((time_t *)0));
#endif
	init();
	setstackmark(&smark);
	procargs(argc, argv);
#ifdef CONFIG_FEATURE_COMMAND_SAVEHISTORY
	if ( iflag ) {
		const char *hp = lookupvar("HISTFILE");

		if(hp == NULL ) {
			hp = lookupvar("HOME");
			if(hp != NULL) {
				char *defhp = concat_path_file(hp, ".ash_history");
				setvar("HISTFILE", defhp, 0);
				free(defhp);
			}
		}
	}
#endif
	if (argv[0] && argv[0][0] == '-')
		isloginsh = 1;
	if (isloginsh) {
		state = 1;
		read_profile("/etc/profile");
state1:
		state = 2;
		read_profile(".profile");
	}
state2:
	state = 3;
	if (
#ifndef linux
		getuid() == geteuid() && getgid() == getegid() &&
#endif
		iflag
	) {
		if ((shinit = lookupvar("ENV")) != NULL && *shinit != '\0') {
			read_profile(shinit);
		}
	}
state3:
	state = 4;
	if (minusc)
		evalstring(minusc, 0);

	if (sflag || minusc == NULL) {
#ifdef CONFIG_FEATURE_COMMAND_SAVEHISTORY
	    if ( iflag ) {
		const char *hp = lookupvar("HISTFILE");

		if(hp != NULL )
			load_history ( hp );
	    }
#endif
state4: /* XXX ??? - why isn't this before the "if" statement */
		cmdloop(1);
	}
#if PROFILE
	monitor(0);
#endif
#if GPROF
	{
		extern void _mcleanup(void);
		_mcleanup();
	}
#endif
	exitshell();
	/* NOTREACHED */
}


/*
 * Read and execute commands.  "Top" is nonzero for the top level command
 * loop; it turns on prompting if the shell is interactive.
 */

static int
cmdloop(int top)
{
	union node *n;
	struct stackmark smark;
	int inter;
	int numeof = 0;

	TRACE(("cmdloop(%d) called\n", top));
	for (;;) {
		int skip;

		setstackmark(&smark);
#if JOBS
		if (jobctl)
			showjobs(stderr, SHOW_CHANGED);
#endif
		inter = 0;
		if (iflag && top) {
			inter++;
#ifdef CONFIG_ASH_MAIL
			chkmail();
#endif
		}
		n = parsecmd(inter);
		/* showtree(n); DEBUG */
		if (n == NEOF) {
			if (!top || numeof >= 50)
				break;
			if (!stoppedjobs()) {
				if (!Iflag)
					break;
				out2str("\nUse \"exit\" to leave shell.\n");
			}
			numeof++;
		} else if (nflag == 0) {
			job_warning = (job_warning == 2) ? 1 : 0;
			numeof = 0;
			evaltree(n, 0);
		}
		popstackmark(&smark);
		skip = evalskip;

		if (skip) {
			evalskip = 0;
			return skip & SKIPEVAL;
		}
	}

	return 0;
}


/*
 * Read /etc/profile or .profile.  Return on error.
 */

static void
read_profile(const char *name)
{
	int skip;

	if (setinputfile(name, INPUT_PUSH_FILE | INPUT_NOFILE_OK) < 0)
		return;

	skip = cmdloop(0);
	popfile();

	if (skip)
		exitshell();
}


/*
 * Read a file containing shell functions.
 */

static void
readcmdfile(char *name)
{
	setinputfile(name, INPUT_PUSH_FILE);
	cmdloop(0);
	popfile();
}


/*
 * Take commands from a file.  To be compatible we should do a path
 * search for the file, which is necessary to find sub-commands.
 */

static inline char *
find_dot_file(char *name)
{
	char *fullname;
	const char *path = pathval();
	struct stat statb;

	/* don't try this for absolute or relative paths */
	if (strchr(name, '/'))
		return name;

	while ((fullname = padvance(&path, name)) != NULL) {
		if ((stat(fullname, &statb) == 0) && S_ISREG(statb.st_mode)) {
			/*
			 * Don't bother freeing here, since it will
			 * be freed by the caller.
			 */
			return fullname;
		}
		stunalloc(fullname);
	}

	/* not found in the PATH */
	sh_error(not_found_msg, name);
	/* NOTREACHED */
}

static int dotcmd(int argc, char **argv)
{
	struct strlist *sp;
	volatile struct shparam saveparam;
	int status = 0;

	for (sp = cmdenviron; sp; sp = sp->next)
		setvareq(bb_xstrdup(sp->text), VSTRFIXED | VTEXTFIXED);

	if (argc >= 2) {        /* That's what SVR2 does */
		char *fullname;

		fullname = find_dot_file(argv[1]);

		if (argc > 2) {
			saveparam = shellparam;
			shellparam.malloc = 0;
			shellparam.nparam = argc - 2;
			shellparam.p = argv + 2;
		};

		setinputfile(fullname, INPUT_PUSH_FILE);
		commandname = fullname;
		cmdloop(0);
		popfile();

		if (argc > 2) {
			freeparam(&shellparam);
			shellparam = saveparam;
		};
		status = exitstatus;
	}
	return status;
}


static int
exitcmd(int argc, char **argv)
{
	if (stoppedjobs())
		return 0;
	if (argc > 1)
		exitstatus = number(argv[1]);
	exraise(EXEXIT);
	/* NOTREACHED */
}

#ifdef CONFIG_ASH_BUILTIN_ECHO
static int
echocmd(int argc, char **argv)
{
	return bb_echo(argc, argv);
}
#endif

#ifdef CONFIG_ASH_BUILTIN_TEST
static int
testcmd(int argc, char **argv)
{
	return bb_test(argc, argv);
}
#endif

/*      memalloc.c        */

/*
 * Same for malloc, realloc, but returns an error when out of space.
 */

static pointer
ckrealloc(pointer p, size_t nbytes)
{
	p = realloc(p, nbytes);
	if (p == NULL)
		sh_error(bb_msg_memory_exhausted);
	return p;
}

static pointer
ckmalloc(size_t nbytes)
{
	return ckrealloc(NULL, nbytes);
}

/*
 * Make a copy of a string in safe storage.
 */

static char *
savestr(const char *s)
{
	char *p = strdup(s);
	if (!p)
		sh_error(bb_msg_memory_exhausted);
	return p;
}


/*
 * Parse trees for commands are allocated in lifo order, so we use a stack
 * to make this more efficient, and also to avoid all sorts of exception
 * handling code to handle interrupts in the middle of a parse.
 *
 * The size 504 was chosen because the Ultrix malloc handles that size
 * well.
 */


static pointer
stalloc(size_t nbytes)
{
	char *p;
	size_t aligned;

	aligned = SHELL_ALIGN(nbytes);
	if (aligned > stacknleft) {
		size_t len;
		size_t blocksize;
		struct stack_block *sp;

		blocksize = aligned;
		if (blocksize < MINSIZE)
			blocksize = MINSIZE;
		len = sizeof(struct stack_block) - MINSIZE + blocksize;
		if (len < blocksize)
			sh_error(bb_msg_memory_exhausted);
		INTOFF;
		sp = ckmalloc(len);
		sp->prev = stackp;
		stacknxt = sp->space;
		stacknleft = blocksize;
		sstrend = stacknxt + blocksize;
		stackp = sp;
		INTON;
	}
	p = stacknxt;
	stacknxt += aligned;
	stacknleft -= aligned;
	return p;
}


void
stunalloc(pointer p)
{
#ifdef DEBUG
	if (!p || (stacknxt < (char *)p) || ((char *)p < stackp->space)) {
		write(2, "stunalloc\n", 10);
		abort();
	}
#endif
	stacknleft += stacknxt - (char *)p;
	stacknxt = p;
}


void
setstackmark(struct stackmark *mark)
{
	mark->stackp = stackp;
	mark->stacknxt = stacknxt;
	mark->stacknleft = stacknleft;
	mark->marknext = markp;
	markp = mark;
}


void
popstackmark(struct stackmark *mark)
{
	struct stack_block *sp;

	INTOFF;
	markp = mark->marknext;
	while (stackp != mark->stackp) {
		sp = stackp;
		stackp = sp->prev;
		ckfree(sp);
	}
	stacknxt = mark->stacknxt;
	stacknleft = mark->stacknleft;
	sstrend = mark->stacknxt + mark->stacknleft;
	INTON;
}


/*
 * When the parser reads in a string, it wants to stick the string on the
 * stack and only adjust the stack pointer when it knows how big the
 * string is.  Stackblock (defined in stack.h) returns a pointer to a block
 * of space on top of the stack and stackblocklen returns the length of
 * this block.  Growstackblock will grow this space by at least one byte,
 * possibly moving it (like realloc).  Grabstackblock actually allocates the
 * part of the block that has been used.
 */

void
growstackblock(void)
{
	size_t newlen;

	newlen = stacknleft * 2;
	if (newlen < stacknleft)
		sh_error(bb_msg_memory_exhausted);
	if (newlen < 128)
		newlen += 128;

	if (stacknxt == stackp->space && stackp != &stackbase) {
		struct stack_block *oldstackp;
		struct stackmark *xmark;
		struct stack_block *sp;
		struct stack_block *prevstackp;
		size_t grosslen;

		INTOFF;
		oldstackp = stackp;
		sp = stackp;
		prevstackp = sp->prev;
		grosslen = newlen + sizeof(struct stack_block) - MINSIZE;
		sp = ckrealloc((pointer)sp, grosslen);
		sp->prev = prevstackp;
		stackp = sp;
		stacknxt = sp->space;
		stacknleft = newlen;
		sstrend = sp->space + newlen;

		/*
		 * Stack marks pointing to the start of the old block
		 * must be relocated to point to the new block
		 */
		xmark = markp;
		while (xmark != NULL && xmark->stackp == oldstackp) {
			xmark->stackp = stackp;
			xmark->stacknxt = stacknxt;
			xmark->stacknleft = stacknleft;
			xmark = xmark->marknext;
		}
		INTON;
	} else {
		char *oldspace = stacknxt;
		int oldlen = stacknleft;
		char *p = stalloc(newlen);

		/* free the space we just allocated */
		stacknxt = memcpy(p, oldspace, oldlen);
		stacknleft += newlen;
	}
}

static inline void
grabstackblock(size_t len)
{
	len = SHELL_ALIGN(len);
	stacknxt += len;
	stacknleft -= len;
}

/*
 * The following routines are somewhat easier to use than the above.
 * The user declares a variable of type STACKSTR, which may be declared
 * to be a register.  The macro STARTSTACKSTR initializes things.  Then
 * the user uses the macro STPUTC to add characters to the string.  In
 * effect, STPUTC(c, p) is the same as *p++ = c except that the stack is
 * grown as necessary.  When the user is done, she can just leave the
 * string there and refer to it using stackblock().  Or she can allocate
 * the space for it using grabstackstr().  If it is necessary to allow
 * someone else to use the stack temporarily and then continue to grow
 * the string, the user should use grabstack to allocate the space, and
 * then call ungrabstr(p) to return to the previous mode of operation.
 *
 * USTPUTC is like STPUTC except that it doesn't check for overflow.
 * CHECKSTACKSPACE can be called before USTPUTC to ensure that there
 * is space for at least one character.
 */

void *
growstackstr(void)
{
	size_t len = stackblocksize();
	if (herefd >= 0 && len >= 1024) {
		bb_full_write(herefd, stackblock(), len);
		return stackblock();
	}
	growstackblock();
	return stackblock() + len;
}

/*
 * Called from CHECKSTRSPACE.
 */

char *
makestrspace(size_t newlen, char *p)
{
	size_t len = p - stacknxt;
	size_t size = stackblocksize();

	for (;;) {
		size_t nleft;

		size = stackblocksize();
		nleft = size - len;
		if (nleft >= newlen)
			break;
		growstackblock();
	}
	return stackblock() + len;
}

char *
stnputs(const char *s, size_t n, char *p)
{
	p = makestrspace(n, p);
	p = mempcpy(p, s, n);
	return p;
}

char *
stputs(const char *s, char *p)
{
	return stnputs(s, strlen(s), p);
}

/*      mystring.c   */

/*
 * String functions.
 *
 *      number(s)               Convert a string of digits to an integer.
 *      is_number(s)            Return true if s is a string of digits.
 */

/*
 * prefix -- see if pfx is a prefix of string.
 */

char *
prefix(const char *string, const char *pfx)
{
	while (*pfx) {
		if (*pfx++ != *string++)
			return 0;
	}
	return (char *) string;
}


/*
 * Convert a string of digits to an integer, printing an error message on
 * failure.
 */

int
number(const char *s)
{

	if (! is_number(s))
		sh_error(illnum, s);
	return atoi(s);
}


/*
 * Check for a valid number.  This should be elsewhere.
 */

int
is_number(const char *p)
{
	do {
		if (! is_digit(*p))
			return 0;
	} while (*++p != '\0');
	return 1;
}


/*
 * Produce a possibly single quoted string suitable as input to the shell.
 * The return string is allocated on the stack.
 */

char *
single_quote(const char *s) {
	char *p;

	STARTSTACKSTR(p);

	do {
		char *q;
		size_t len;

		len = strchrnul(s, '\'') - s;

		q = p = makestrspace(len + 3, p);

		*q++ = '\'';
		q = mempcpy(q, s, len);
		*q++ = '\'';
		s += len;

		STADJUST(q - p, p);

		len = strspn(s, "'");
		if (!len)
			break;

		q = p = makestrspace(len + 3, p);

		*q++ = '"';
		q = mempcpy(q, s, len);
		*q++ = '"';
		s += len;

		STADJUST(q - p, p);
	} while (*s);

	USTPUTC(0, p);

	return stackblock();
}

/*
 * Like strdup but works with the ash stack.
 */

char *
sstrdup(const char *p)
{
	size_t len = strlen(p) + 1;
	return memcpy(stalloc(len), p, len);
}


static void
calcsize(union node *n)
{
      if (n == NULL)
	    return;
      funcblocksize += nodesize[n->type];
      switch (n->type) {
      case NCMD:
	    calcsize(n->ncmd.redirect);
	    calcsize(n->ncmd.args);
	    calcsize(n->ncmd.assign);
	    break;
      case NPIPE:
	    sizenodelist(n->npipe.cmdlist);
	    break;
      case NREDIR:
      case NBACKGND:
      case NSUBSHELL:
	    calcsize(n->nredir.redirect);
	    calcsize(n->nredir.n);
	    break;
      case NAND:
      case NOR:
      case NSEMI:
      case NWHILE:
      case NUNTIL:
	    calcsize(n->nbinary.ch2);
	    calcsize(n->nbinary.ch1);
	    break;
      case NIF:
	    calcsize(n->nif.elsepart);
	    calcsize(n->nif.ifpart);
	    calcsize(n->nif.test);
	    break;
      case NFOR:
	    funcstringsize += strlen(n->nfor.var) + 1;
	    calcsize(n->nfor.body);
	    calcsize(n->nfor.args);
	    break;
      case NCASE:
	    calcsize(n->ncase.cases);
	    calcsize(n->ncase.expr);
	    break;
      case NCLIST:
	    calcsize(n->nclist.body);
	    calcsize(n->nclist.pattern);
	    calcsize(n->nclist.next);
	    break;
      case NDEFUN:
      case NARG:
	    sizenodelist(n->narg.backquote);
	    funcstringsize += strlen(n->narg.text) + 1;
	    calcsize(n->narg.next);
	    break;
      case NTO:
      case NCLOBBER:
      case NFROM:
      case NFROMTO:
      case NAPPEND:
	    calcsize(n->nfile.fname);
	    calcsize(n->nfile.next);
	    break;
      case NTOFD:
      case NFROMFD:
	    calcsize(n->ndup.vname);
	    calcsize(n->ndup.next);
	    break;
      case NHERE:
      case NXHERE:
	    calcsize(n->nhere.doc);
	    calcsize(n->nhere.next);
	    break;
      case NNOT:
	    calcsize(n->nnot.com);
	    break;
      };
}


static void
sizenodelist(struct nodelist *lp)
{
	while (lp) {
		funcblocksize += SHELL_ALIGN(sizeof(struct nodelist));
		calcsize(lp->n);
		lp = lp->next;
	}
}


static union node *
copynode(union node *n)
{
      union node *new;

      if (n == NULL)
	    return NULL;
      new = funcblock;
      funcblock = (char *) funcblock + nodesize[n->type];
      switch (n->type) {
      case NCMD:
	    new->ncmd.redirect = copynode(n->ncmd.redirect);
	    new->ncmd.args = copynode(n->ncmd.args);
	    new->ncmd.assign = copynode(n->ncmd.assign);
	    break;
      case NPIPE:
	    new->npipe.cmdlist = copynodelist(n->npipe.cmdlist);
	    new->npipe.backgnd = n->npipe.backgnd;
	    break;
      case NREDIR:
      case NBACKGND:
      case NSUBSHELL:
	    new->nredir.redirect = copynode(n->nredir.redirect);
	    new->nredir.n = copynode(n->nredir.n);
	    break;
      case NAND:
      case NOR:
      case NSEMI:
      case NWHILE:
      case NUNTIL:
	    new->nbinary.ch2 = copynode(n->nbinary.ch2);
	    new->nbinary.ch1 = copynode(n->nbinary.ch1);
	    break;
      case NIF:
	    new->nif.elsepart = copynode(n->nif.elsepart);
	    new->nif.ifpart = copynode(n->nif.ifpart);
	    new->nif.test = copynode(n->nif.test);
	    break;
      case NFOR:
	    new->nfor.var = nodesavestr(n->nfor.var);
	    new->nfor.body = copynode(n->nfor.body);
	    new->nfor.args = copynode(n->nfor.args);
	    break;
      case NCASE:
	    new->ncase.cases = copynode(n->ncase.cases);
	    new->ncase.expr = copynode(n->ncase.expr);
	    break;
      case NCLIST:
	    new->nclist.body = copynode(n->nclist.body);
	    new->nclist.pattern = copynode(n->nclist.pattern);
	    new->nclist.next = copynode(n->nclist.next);
	    break;
      case NDEFUN:
      case NARG:
	    new->narg.backquote = copynodelist(n->narg.backquote);
	    new->narg.text = nodesavestr(n->narg.text);
	    new->narg.next = copynode(n->narg.next);
	    break;
      case NTO:
      case NCLOBBER:
      case NFROM:
      case NFROMTO:
      case NAPPEND:
	    new->nfile.fname = copynode(n->nfile.fname);
	    new->nfile.fd = n->nfile.fd;
	    new->nfile.next = copynode(n->nfile.next);
	    break;
      case NTOFD:
      case NFROMFD:
	    new->ndup.vname = copynode(n->ndup.vname);
	    new->ndup.dupfd = n->ndup.dupfd;
	    new->ndup.fd = n->ndup.fd;
	    new->ndup.next = copynode(n->ndup.next);
	    break;
      case NHERE:
      case NXHERE:
	    new->nhere.doc = copynode(n->nhere.doc);
	    new->nhere.fd = n->nhere.fd;
	    new->nhere.next = copynode(n->nhere.next);
	    break;
      case NNOT:
	    new->nnot.com = copynode(n->nnot.com);
	    break;
      };
      new->type = n->type;
	return new;
}


static struct nodelist *
copynodelist(struct nodelist *lp)
{
	struct nodelist *start;
	struct nodelist **lpp;

	lpp = &start;
	while (lp) {
		*lpp = funcblock;
		funcblock = (char *) funcblock +
		    SHELL_ALIGN(sizeof(struct nodelist));
		(*lpp)->n = copynode(lp->n);
		lp = lp->next;
		lpp = &(*lpp)->next;
	}
	*lpp = NULL;
	return start;
}


static char *
nodesavestr(char   *s)
{
	char   *rtn = funcstring;

	funcstring = stpcpy(funcstring, s) + 1;
	return rtn;
}


/*
 * Free a parse tree.
 */

static void
freefunc(struct funcnode *f)
{
	if (f && --f->count < 0)
		ckfree(f);
}


static void options(int);
static void setoption(int, int);


/*
 * Process the shell command line arguments.
 */

void
procargs(int argc, char **argv)
{
	int i;
	const char *xminusc;
	char **xargv;

	xargv = argv;
	arg0 = xargv[0];
	if (argc > 0)
		xargv++;
	for (i = 0; i < NOPTS; i++)
		optlist[i] = 2;
	argptr = xargv;
	options(1);
	xargv = argptr;
	xminusc = minusc;
	if (*xargv == NULL) {
		if (xminusc)
			sh_error(bb_msg_requires_arg, "-c");
		sflag = 1;
	}
	if (iflag == 2 && sflag == 1 && isatty(0) && isatty(1))
		iflag = 1;
	if (mflag == 2)
		mflag = iflag;
	for (i = 0; i < NOPTS; i++)
		if (optlist[i] == 2)
			optlist[i] = 0;
#if DEBUG == 2
	debug = 1;
#endif
	/* POSIX 1003.2: first arg after -c cmd is $0, remainder $1... */
	if (xminusc) {
		minusc = *xargv++;
		if (*xargv)
			goto setarg0;
	} else if (!sflag) {
		setinputfile(*xargv, 0);
setarg0:
		arg0 = *xargv++;
		commandname = arg0;
	}

	shellparam.p = xargv;
#ifdef CONFIG_ASH_GETOPTS
	shellparam.optind = 1;
	shellparam.optoff = -1;
#endif
	/* assert(shellparam.malloc == 0 && shellparam.nparam == 0); */
	while (*xargv) {
		shellparam.nparam++;
		xargv++;
	}
	optschanged();
}


void
optschanged(void)
{
#ifdef DEBUG
	opentrace();
#endif
	setinteractive(iflag);
	setjobctl(mflag);
	setvimode(viflag);
}

static inline void
minus_o(char *name, int val)
{
	int i;

	if (name == NULL) {
		out1str("Current option settings\n");
		for (i = 0; i < NOPTS; i++)
			out1fmt("%-16s%s\n", optnames(i),
				optlist[i] ? "on" : "off");
	} else {
		for (i = 0; i < NOPTS; i++)
			if (equal(name, optnames(i))) {
				optlist[i] = val;
				return;
			}
		sh_error("Illegal option -o %s", name);
	}
}

/*
 * Process shell options.  The global variable argptr contains a pointer
 * to the argument list; we advance it past the options.
 */

static void
options(int cmdline)
{
	char *p;
	int val;
	int c;

	if (cmdline)
		minusc = NULL;
	while ((p = *argptr) != NULL) {
		argptr++;
		if ((c = *p++) == '-') {
			val = 1;
			if (p[0] == '\0' || (p[0] == '-' && p[1] == '\0')) {
				if (!cmdline) {
					/* "-" means turn off -x and -v */
					if (p[0] == '\0')
						xflag = vflag = 0;
					/* "--" means reset params */
					else if (*argptr == NULL)
						setparam(argptr);
				}
				break;    /* "-" or  "--" terminates options */
			}
		} else if (c == '+') {
			val = 0;
		} else {
			argptr--;
			break;
		}
		while ((c = *p++) != '\0') {
			if (c == 'c' && cmdline) {
				minusc = p;     /* command is after shell args*/
			} else if (c == 'o') {
				minus_o(*argptr, val);
				if (*argptr)
					argptr++;
			} else if (cmdline && (c == '-')) {     // long options
				if (strcmp(p, "login") == 0)
					isloginsh = 1;
				break;
			} else {
				setoption(c, val);
			}
		}
	}
}


static void
setoption(int flag, int val)
{
	int i;

	for (i = 0; i < NOPTS; i++)
		if (optletters(i) == flag) {
			optlist[i] = val;
			return;
		}
	sh_error("Illegal option -%c", flag);
	/* NOTREACHED */
}



/*
 * Set the shell parameters.
 */

void
setparam(char **argv)
{
	char **newparam;
	char **ap;
	int nparam;

	for (nparam = 0 ; argv[nparam] ; nparam++);
	ap = newparam = ckmalloc((nparam + 1) * sizeof *ap);
	while (*argv) {
		*ap++ = savestr(*argv++);
	}
	*ap = NULL;
	freeparam(&shellparam);
	shellparam.malloc = 1;
	shellparam.nparam = nparam;
	shellparam.p = newparam;
#ifdef CONFIG_ASH_GETOPTS
	shellparam.optind = 1;
	shellparam.optoff = -1;
#endif
}


/*
 * Free the list of positional parameters.
 */

void
freeparam(volatile struct shparam *param)
{
	char **ap;

	if (param->malloc) {
		for (ap = param->p ; *ap ; ap++)
			ckfree(*ap);
		ckfree(param->p);
	}
}



/*
 * The shift builtin command.
 */

int
shiftcmd(int argc, char **argv)
{
	int n;
	char **ap1, **ap2;

	n = 1;
	if (argc > 1)
		n = number(argv[1]);
	if (n > shellparam.nparam)
		sh_error("can't shift that many");
	INTOFF;
	shellparam.nparam -= n;
	for (ap1 = shellparam.p ; --n >= 0 ; ap1++) {
		if (shellparam.malloc)
			ckfree(*ap1);
	}
	ap2 = shellparam.p;
	while ((*ap2++ = *ap1++) != NULL);
#ifdef CONFIG_ASH_GETOPTS
	shellparam.optind = 1;
	shellparam.optoff = -1;
#endif
	INTON;
	return 0;
}



/*
 * The set command builtin.
 */

int
setcmd(int argc, char **argv)
{
	if (argc == 1)
		return showvars(nullstr, 0, VUNSET);
	INTOFF;
	options(0);
	optschanged();
	if (*argptr != NULL) {
		setparam(argptr);
	}
	INTON;
	return 0;
}


#ifdef CONFIG_ASH_GETOPTS
static void
getoptsreset(const char *value)
{
	shellparam.optind = number(value);
	shellparam.optoff = -1;
}
#endif

#ifdef CONFIG_LOCALE_SUPPORT
static void change_lc_all(const char *value)
{
	if (value != 0 && *value != 0)
		setlocale(LC_ALL, value);
}

static void change_lc_ctype(const char *value)
{
	if (value != 0 && *value != 0)
		setlocale(LC_CTYPE, value);
}

#endif

#ifdef CONFIG_ASH_RANDOM_SUPPORT
/* Roughly copied from bash.. */
static void change_random(const char *value)
{
	if(value == NULL) {
		/* "get", generate */
		char buf[16];

		rseed = rseed * 1103515245 + 12345;
		sprintf(buf, "%d", (unsigned int)((rseed & 32767)));
		/* set without recursion */
		setvar(vrandom.text, buf, VNOFUNC);
		vrandom.flags &= ~VNOFUNC;
	} else {
		/* set/reset */
		rseed = strtoul(value, (char **)NULL, 10);
	}
}
#endif


#ifdef CONFIG_ASH_GETOPTS
static int
getopts(char *optstr, char *optvar, char **optfirst, int *param_optind, int *optoff)
{
	char *p, *q;
	char c = '?';
	int done = 0;
	int err = 0;
	char s[12];
	char **optnext;

	if(*param_optind < 1)
		return 1;
	optnext = optfirst + *param_optind - 1;

	if (*param_optind <= 1 || *optoff < 0 || strlen(optnext[-1]) < *optoff)
		p = NULL;
	else
		p = optnext[-1] + *optoff;
	if (p == NULL || *p == '\0') {
		/* Current word is done, advance */
		p = *optnext;
		if (p == NULL || *p != '-' || *++p == '\0') {
atend:
			p = NULL;
			done = 1;
			goto out;
		}
		optnext++;
		if (p[0] == '-' && p[1] == '\0')        /* check for "--" */
			goto atend;
	}

	c = *p++;
	for (q = optstr; *q != c; ) {
		if (*q == '\0') {
			if (optstr[0] == ':') {
				s[0] = c;
				s[1] = '\0';
				err |= setvarsafe("OPTARG", s, 0);
			} else {
				fprintf(stderr, "Illegal option -%c\n", c);
				(void) unsetvar("OPTARG");
			}
			c = '?';
			goto out;
		}
		if (*++q == ':')
			q++;
	}

	if (*++q == ':') {
		if (*p == '\0' && (p = *optnext) == NULL) {
			if (optstr[0] == ':') {
				s[0] = c;
				s[1] = '\0';
				err |= setvarsafe("OPTARG", s, 0);
				c = ':';
			} else {
				fprintf(stderr, "No arg for -%c option\n", c);
				(void) unsetvar("OPTARG");
				c = '?';
			}
			goto out;
		}

		if (p == *optnext)
			optnext++;
		err |= setvarsafe("OPTARG", p, 0);
		p = NULL;
	} else
		err |= setvarsafe("OPTARG", nullstr, 0);

out:
	*optoff = p ? p - *(optnext - 1) : -1;
	*param_optind = optnext - optfirst + 1;
	fmtstr(s, sizeof(s), "%d", *param_optind);
	err |= setvarsafe("OPTIND", s, VNOFUNC);
	s[0] = c;
	s[1] = '\0';
	err |= setvarsafe(optvar, s, 0);
	if (err) {
		*param_optind = 1;
		*optoff = -1;
		flushall();
		exraise(EXERROR);
	}
	return done;
}

/*
 * The getopts builtin.  Shellparam.optnext points to the next argument
 * to be processed.  Shellparam.optptr points to the next character to
 * be processed in the current argument.  If shellparam.optnext is NULL,
 * then it's the first time getopts has been called.
 */

int
getoptscmd(int argc, char **argv)
{
	char **optbase;

	if (argc < 3)
		sh_error("Usage: getopts optstring var [arg]");
	else if (argc == 3) {
		optbase = shellparam.p;
		if (shellparam.optind > shellparam.nparam + 1) {
			shellparam.optind = 1;
			shellparam.optoff = -1;
		}
	}
	else {
		optbase = &argv[3];
		if (shellparam.optind > argc - 2) {
			shellparam.optind = 1;
			shellparam.optoff = -1;
		}
	}

	return getopts(argv[1], argv[2], optbase, &shellparam.optind,
		       &shellparam.optoff);
}
#endif /* CONFIG_ASH_GETOPTS */

/*
 * XXX - should get rid of.  have all builtins use getopt(3).  the
 * library getopt must have the BSD extension static variable "optreset"
 * otherwise it can't be used within the shell safely.
 *
 * Standard option processing (a la getopt) for builtin routines.  The
 * only argument that is passed to nextopt is the option string; the
 * other arguments are unnecessary.  It return the character, or '\0' on
 * end of input.
 */

static int
nextopt(const char *optstring)
{
	char *p;
	const char *q;
	char c;

	if ((p = optptr) == NULL || *p == '\0') {
		p = *argptr;
		if (p == NULL || *p != '-' || *++p == '\0')
			return '\0';
		argptr++;
		if (p[0] == '-' && p[1] == '\0')        /* check for "--" */
			return '\0';
	}
	c = *p++;
	for (q = optstring ; *q != c ; ) {
		if (*q == '\0')
			sh_error("Illegal option -%c", c);
		if (*++q == ':')
			q++;
	}
	if (*++q == ':') {
		if (*p == '\0' && (p = *argptr++) == NULL)
			sh_error("No arg for -%c option", c);
		optionarg = p;
		p = NULL;
	}
	optptr = p;
	return c;
}


/*      output.c     */

void
outstr(const char *p, FILE *file)
{
	INTOFF;
	fputs(p, file);
	INTON;
}

void
flushall(void)
{
	INTOFF;
	fflush(stdout);
	fflush(stderr);
	INTON;
}

void
flusherr(void)
{
	INTOFF;
	fflush(stderr);
	INTON;
}

static void
outcslow(int c, FILE *dest)
{
	INTOFF;
	putc(c, dest);
	fflush(dest);
	INTON;
}


static int
out1fmt(const char *fmt, ...)
{
	va_list ap;
	int r;

	INTOFF;
	va_start(ap, fmt);
	r = vprintf(fmt, ap);
	va_end(ap);
	INTON;
	return r;
}


int
fmtstr(char *outbuf, size_t length, const char *fmt, ...)
{
	va_list ap;
	int ret;

	va_start(ap, fmt);
	INTOFF;
	ret = vsnprintf(outbuf, length, fmt, ap);
	va_end(ap);
	INTON;
	return ret;
}



/*      parser.c     */


/*
 * Shell command parser.
 */

#define EOFMARKLEN 79


struct heredoc {
	struct heredoc *next;   /* next here document in list */
	union node *here;               /* redirection node */
	char *eofmark;          /* string indicating end of input */
	int striptabs;          /* if set, strip leading tabs */
};



static struct heredoc *heredoclist;    /* list of here documents to read */


static union node *list(int);
static union node *andor(void);
static union node *pipeline(void);
static union node *command(void);
static union node *simplecmd(void);
static union node *makename(void);
static void parsefname(void);
static void parseheredoc(void);
static char peektoken(void);
static int readtoken(void);
static int xxreadtoken(void);
static int readtoken1(int firstc, int syntax, char *eofmark, int striptabs);
static int noexpand(char *);
static void synexpect(int) ATTRIBUTE_NORETURN;
static void synerror(const char *) ATTRIBUTE_NORETURN;
static void setprompt(int);




/*
 * Read and parse a command.  Returns NEOF on end of file.  (NULL is a
 * valid parse tree indicating a blank line.)
 */

union node *
parsecmd(int interact)
{
	int t;

	tokpushback = 0;
	doprompt = interact;
	if (doprompt)
		setprompt(doprompt);
	needprompt = 0;
	t = readtoken();
	if (t == TEOF)
		return NEOF;
	if (t == TNL)
		return NULL;
	tokpushback++;
	return list(1);
}


static union node *
list(int nlflag)
{
	union node *n1, *n2, *n3;
	int tok;

	checkkwd = CHKNL | CHKKWD | CHKALIAS;
	if (nlflag == 2 && peektoken())
		return NULL;
	n1 = NULL;
	for (;;) {
		n2 = andor();
		tok = readtoken();
		if (tok == TBACKGND) {
			if (n2->type == NPIPE) {
				n2->npipe.backgnd = 1;
			} else {
				if (n2->type != NREDIR) {
					n3 = stalloc(sizeof(struct nredir));
					n3->nredir.n = n2;
					n3->nredir.redirect = NULL;
					n2 = n3;
				}
				n2->type = NBACKGND;
			}
		}
		if (n1 == NULL) {
			n1 = n2;
		}
		else {
			n3 = (union node *)stalloc(sizeof (struct nbinary));
			n3->type = NSEMI;
			n3->nbinary.ch1 = n1;
			n3->nbinary.ch2 = n2;
			n1 = n3;
		}
		switch (tok) {
		case TBACKGND:
		case TSEMI:
			tok = readtoken();
			/* fall through */
		case TNL:
			if (tok == TNL) {
				parseheredoc();
				if (nlflag == 1)
					return n1;
			} else {
				tokpushback++;
			}
			checkkwd = CHKNL | CHKKWD | CHKALIAS;
			if (peektoken())
				return n1;
			break;
		case TEOF:
			if (heredoclist)
				parseheredoc();
			else
				pungetc();              /* push back EOF on input */
			return n1;
		default:
			if (nlflag == 1)
				synexpect(-1);
			tokpushback++;
			return n1;
		}
	}
}



static union node *
andor(void)
{
	union node *n1, *n2, *n3;
	int t;

	n1 = pipeline();
	for (;;) {
		if ((t = readtoken()) == TAND) {
			t = NAND;
		} else if (t == TOR) {
			t = NOR;
		} else {
			tokpushback++;
			return n1;
		}
		checkkwd = CHKNL | CHKKWD | CHKALIAS;
		n2 = pipeline();
		n3 = (union node *)stalloc(sizeof (struct nbinary));
		n3->type = t;
		n3->nbinary.ch1 = n1;
		n3->nbinary.ch2 = n2;
		n1 = n3;
	}
}



static union node *
pipeline(void)
{
	union node *n1, *n2, *pipenode;
	struct nodelist *lp, *prev;
	int negate;

	negate = 0;
	TRACE(("pipeline: entered\n"));
	if (readtoken() == TNOT) {
		negate = !negate;
		checkkwd = CHKKWD | CHKALIAS;
	} else
		tokpushback++;
	n1 = command();
	if (readtoken() == TPIPE) {
		pipenode = (union node *)stalloc(sizeof (struct npipe));
		pipenode->type = NPIPE;
		pipenode->npipe.backgnd = 0;
		lp = (struct nodelist *)stalloc(sizeof (struct nodelist));
		pipenode->npipe.cmdlist = lp;
		lp->n = n1;
		do {
			prev = lp;
			lp = (struct nodelist *)stalloc(sizeof (struct nodelist));
			checkkwd = CHKNL | CHKKWD | CHKALIAS;
			lp->n = command();
			prev->next = lp;
		} while (readtoken() == TPIPE);
		lp->next = NULL;
		n1 = pipenode;
	}
	tokpushback++;
	if (negate) {
		n2 = (union node *)stalloc(sizeof (struct nnot));
		n2->type = NNOT;
		n2->nnot.com = n1;
		return n2;
	} else
		return n1;
}



static union node *
command(void)
{
	union node *n1, *n2;
	union node *ap, **app;
	union node *cp, **cpp;
	union node *redir, **rpp;
	union node **rpp2;
	int t;

	redir = NULL;
	rpp2 = &redir;

	switch (readtoken()) {
	default:
		synexpect(-1);
		/* NOTREACHED */
	case TIF:
		n1 = (union node *)stalloc(sizeof (struct nif));
		n1->type = NIF;
		n1->nif.test = list(0);
		if (readtoken() != TTHEN)
			synexpect(TTHEN);
		n1->nif.ifpart = list(0);
		n2 = n1;
		while (readtoken() == TELIF) {
			n2->nif.elsepart = (union node *)stalloc(sizeof (struct nif));
			n2 = n2->nif.elsepart;
			n2->type = NIF;
			n2->nif.test = list(0);
			if (readtoken() != TTHEN)
				synexpect(TTHEN);
			n2->nif.ifpart = list(0);
		}
		if (lasttoken == TELSE)
			n2->nif.elsepart = list(0);
		else {
			n2->nif.elsepart = NULL;
			tokpushback++;
		}
		t = TFI;
		break;
	case TWHILE:
	case TUNTIL: {
		int got;
		n1 = (union node *)stalloc(sizeof (struct nbinary));
		n1->type = (lasttoken == TWHILE)? NWHILE : NUNTIL;
		n1->nbinary.ch1 = list(0);
		if ((got=readtoken()) != TDO) {
TRACE(("expecting DO got %s %s\n", tokname(got), got == TWORD ? wordtext : ""));
			synexpect(TDO);
		}
		n1->nbinary.ch2 = list(0);
		t = TDONE;
		break;
	}
	case TFOR:
		if (readtoken() != TWORD || quoteflag || ! goodname(wordtext))
			synerror("Bad for loop variable");
		n1 = (union node *)stalloc(sizeof (struct nfor));
		n1->type = NFOR;
		n1->nfor.var = wordtext;
		checkkwd = CHKKWD | CHKALIAS;
		if (readtoken() == TIN) {
			app = &ap;
			while (readtoken() == TWORD) {
				n2 = (union node *)stalloc(sizeof (struct narg));
				n2->type = NARG;
				n2->narg.text = wordtext;
				n2->narg.backquote = backquotelist;
				*app = n2;
				app = &n2->narg.next;
			}
			*app = NULL;
			n1->nfor.args = ap;
			if (lasttoken != TNL && lasttoken != TSEMI)
				synexpect(-1);
		} else {
			n2 = (union node *)stalloc(sizeof (struct narg));
			n2->type = NARG;
			n2->narg.text = (char *)dolatstr;
			n2->narg.backquote = NULL;
			n2->narg.next = NULL;
			n1->nfor.args = n2;
			/*
			 * Newline or semicolon here is optional (but note
			 * that the original Bourne shell only allowed NL).
			 */
			if (lasttoken != TNL && lasttoken != TSEMI)
				tokpushback++;
		}
		checkkwd = CHKNL | CHKKWD | CHKALIAS;
		if (readtoken() != TDO)
			synexpect(TDO);
		n1->nfor.body = list(0);
		t = TDONE;
		break;
	case TCASE:
		n1 = (union node *)stalloc(sizeof (struct ncase));
		n1->type = NCASE;
		if (readtoken() != TWORD)
			synexpect(TWORD);
		n1->ncase.expr = n2 = (union node *)stalloc(sizeof (struct narg));
		n2->type = NARG;
		n2->narg.text = wordtext;
		n2->narg.backquote = backquotelist;
		n2->narg.next = NULL;
		do {
			checkkwd = CHKKWD | CHKALIAS;
		} while (readtoken() == TNL);
		if (lasttoken != TIN)
			synexpect(TIN);
		cpp = &n1->ncase.cases;
next_case:
		checkkwd = CHKNL | CHKKWD;
		t = readtoken();
		while(t != TESAC) {
			if (lasttoken == TLP)
				readtoken();
			*cpp = cp = (union node *)stalloc(sizeof (struct nclist));
			cp->type = NCLIST;
			app = &cp->nclist.pattern;
			for (;;) {
				*app = ap = (union node *)stalloc(sizeof (struct narg));
				ap->type = NARG;
				ap->narg.text = wordtext;
				ap->narg.backquote = backquotelist;
				if (readtoken() != TPIPE)
					break;
				app = &ap->narg.next;
				readtoken();
			}
			ap->narg.next = NULL;
			if (lasttoken != TRP)
				synexpect(TRP);
			cp->nclist.body = list(2);

			cpp = &cp->nclist.next;

			checkkwd = CHKNL | CHKKWD;
			if ((t = readtoken()) != TESAC) {
				if (t != TENDCASE)
					synexpect(TENDCASE);
				else
					goto next_case;
			}
		}
		*cpp = NULL;
		goto redir;
	case TLP:
		n1 = (union node *)stalloc(sizeof (struct nredir));
		n1->type = NSUBSHELL;
		n1->nredir.n = list(0);
		n1->nredir.redirect = NULL;
		t = TRP;
		break;
	case TBEGIN:
		n1 = list(0);
		t = TEND;
		break;
	case TWORD:
	case TREDIR:
		tokpushback++;
		return simplecmd();
	}

	if (readtoken() != t)
		synexpect(t);

redir:
	/* Now check for redirection which may follow command */
	checkkwd = CHKKWD | CHKALIAS;
	rpp = rpp2;
	while (readtoken() == TREDIR) {
		*rpp = n2 = redirnode;
		rpp = &n2->nfile.next;
		parsefname();
	}
	tokpushback++;
	*rpp = NULL;
	if (redir) {
		if (n1->type != NSUBSHELL) {
			n2 = (union node *)stalloc(sizeof (struct nredir));
			n2->type = NREDIR;
			n2->nredir.n = n1;
			n1 = n2;
		}
		n1->nredir.redirect = redir;
	}

	return n1;
}


static union node *
simplecmd(void) {
	union node *args, **app;
	union node *n = NULL;
	union node *vars, **vpp;
	union node **rpp, *redir;
	int savecheckkwd;

	args = NULL;
	app = &args;
	vars = NULL;
	vpp = &vars;
	redir = NULL;
	rpp = &redir;

	savecheckkwd = CHKALIAS;
	for (;;) {
		checkkwd = savecheckkwd;
		switch (readtoken()) {
		case TWORD:
			n = (union node *)stalloc(sizeof (struct narg));
			n->type = NARG;
			n->narg.text = wordtext;
			n->narg.backquote = backquotelist;
			if (savecheckkwd && isassignment(wordtext)) {
				*vpp = n;
				vpp = &n->narg.next;
			} else {
				*app = n;
				app = &n->narg.next;
				savecheckkwd = 0;
			}
			break;
		case TREDIR:
			*rpp = n = redirnode;
			rpp = &n->nfile.next;
			parsefname();   /* read name of redirection file */
			break;
		case TLP:
			if (
				args && app == &args->narg.next &&
				!vars && !redir
			) {
				struct builtincmd *bcmd;
				const char *name;

				/* We have a function */
				if (readtoken() != TRP)
					synexpect(TRP);
				name = n->narg.text;
				if (
					!goodname(name) || (
						(bcmd = find_builtin(name)) &&
						IS_BUILTIN_SPECIAL(bcmd)
					)
				)
					synerror("Bad function name");
				n->type = NDEFUN;
				checkkwd = CHKNL | CHKKWD | CHKALIAS;
				n->narg.next = command();
				return n;
			}
			/* fall through */
		default:
			tokpushback++;
			goto out;
		}
	}
out:
	*app = NULL;
	*vpp = NULL;
	*rpp = NULL;
	n = (union node *)stalloc(sizeof (struct ncmd));
	n->type = NCMD;
	n->ncmd.args = args;
	n->ncmd.assign = vars;
	n->ncmd.redirect = redir;
	return n;
}

static union node *
makename(void)
{
	union node *n;

	n = (union node *)stalloc(sizeof (struct narg));
	n->type = NARG;
	n->narg.next = NULL;
	n->narg.text = wordtext;
	n->narg.backquote = backquotelist;
	return n;
}

void fixredir(union node *n, const char *text, int err)
{
	TRACE(("Fix redir %s %d\n", text, err));
	if (!err)
		n->ndup.vname = NULL;

	if (is_digit(text[0]) && text[1] == '\0')
		n->ndup.dupfd = digit_val(text[0]);
	else if (text[0] == '-' && text[1] == '\0')
		n->ndup.dupfd = -1;
	else {

		if (err)
			synerror("Bad fd number");
		else
			n->ndup.vname = makename();
	}
}


static void
parsefname(void)
{
	union node *n = redirnode;

	if (readtoken() != TWORD)
		synexpect(-1);
	if (n->type == NHERE) {
		struct heredoc *here = heredoc;
		struct heredoc *p;
		int i;

		if (quoteflag == 0)
			n->type = NXHERE;
		TRACE(("Here document %d\n", n->type));
		if (! noexpand(wordtext) || (i = strlen(wordtext)) == 0 || i > EOFMARKLEN)
			synerror("Illegal eof marker for << redirection");
		rmescapes(wordtext);
		here->eofmark = wordtext;
		here->next = NULL;
		if (heredoclist == NULL)
			heredoclist = here;
		else {
			for (p = heredoclist ; p->next ; p = p->next);
			p->next = here;
		}
	} else if (n->type == NTOFD || n->type == NFROMFD) {
		fixredir(n, wordtext, 0);
	} else {
		n->nfile.fname = makename();
	}
}


/*
 * Input any here documents.
 */

static void
parseheredoc(void)
{
	struct heredoc *here;
	union node *n;

	here = heredoclist;
	heredoclist = 0;

	while (here) {
		if (needprompt) {
			setprompt(2);
		}
		readtoken1(pgetc(), here->here->type == NHERE? SQSYNTAX : DQSYNTAX,
				here->eofmark, here->striptabs);
		n = (union node *)stalloc(sizeof (struct narg));
		n->narg.type = NARG;
		n->narg.next = NULL;
		n->narg.text = wordtext;
		n->narg.backquote = backquotelist;
		here->here->nhere.doc = n;
		here = here->next;
	}
}

static char peektoken(void)
{
	int t;

	t = readtoken();
	tokpushback++;
	return tokname_array[t][0];
}

static int
readtoken(void)
{
	int t;
#ifdef DEBUG
	int alreadyseen = tokpushback;
#endif

#ifdef CONFIG_ASH_ALIAS
top:
#endif

	t = xxreadtoken();

	/*
	 * eat newlines
	 */
	if (checkkwd & CHKNL) {
		while (t == TNL) {
			parseheredoc();
			t = xxreadtoken();
		}
	}

	if (t != TWORD || quoteflag) {
		goto out;
	}

	/*
	 * check for keywords
	 */
	if (checkkwd & CHKKWD) {
		const char *const *pp;

		if ((pp = findkwd(wordtext))) {
			lasttoken = t = pp - tokname_array;
			TRACE(("keyword %s recognized\n", tokname(t)));
			goto out;
		}
	}

	if (checkkwd & CHKALIAS) {
#ifdef CONFIG_ASH_ALIAS
		struct alias *ap;
		if ((ap = lookupalias(wordtext, 1)) != NULL) {
			if (*ap->val) {
				pushstring(ap->val, ap);
			}
			goto top;
		}
#endif
	}
out:
	checkkwd = 0;
#ifdef DEBUG
	if (!alreadyseen)
	    TRACE(("token %s %s\n", tokname(t), t == TWORD ? wordtext : ""));
	else
	    TRACE(("reread token %s %s\n", tokname(t), t == TWORD ? wordtext : ""));
#endif
	return (t);
}


/*
 * Read the next input token.
 * If the token is a word, we set backquotelist to the list of cmds in
 *      backquotes.  We set quoteflag to true if any part of the word was
 *      quoted.
 * If the token is TREDIR, then we set redirnode to a structure containing
 *      the redirection.
 * In all cases, the variable startlinno is set to the number of the line
 *      on which the token starts.
 *
 * [Change comment:  here documents and internal procedures]
 * [Readtoken shouldn't have any arguments.  Perhaps we should make the
 *  word parsing code into a separate routine.  In this case, readtoken
 *  doesn't need to have any internal procedures, but parseword does.
 *  We could also make parseoperator in essence the main routine, and
 *  have parseword (readtoken1?) handle both words and redirection.]
 */

#define NEW_xxreadtoken
#ifdef NEW_xxreadtoken

/* singles must be first! */
static const char xxreadtoken_chars[7] = { '\n', '(', ')', '&', '|', ';', 0 };

static const char xxreadtoken_tokens[] = {
	TNL, TLP, TRP,          /* only single occurrence allowed */
	TBACKGND, TPIPE, TSEMI, /* if single occurrence */
	TEOF,                   /* corresponds to trailing nul */
	TAND, TOR, TENDCASE,    /* if double occurrence */
};

#define xxreadtoken_doubles \
	(sizeof(xxreadtoken_tokens) - sizeof(xxreadtoken_chars))
#define xxreadtoken_singles \
	(sizeof(xxreadtoken_chars) - xxreadtoken_doubles - 1)

static int xxreadtoken(void)
{
	int c;

	if (tokpushback) {
		tokpushback = 0;
		return lasttoken;
	}
	if (needprompt) {
		setprompt(2);
	}
	startlinno = plinno;
	for (;;) {                      /* until token or start of word found */
		c = pgetc_macro();

		if ((c != ' ') && (c != '\t')
#ifdef CONFIG_ASH_ALIAS
			&& (c != PEOA)
#endif
			) {
			if (c == '#') {
				while ((c = pgetc()) != '\n' && c != PEOF);
				pungetc();
			} else if (c == '\\') {
				if (pgetc() != '\n') {
					pungetc();
					goto READTOKEN1;
				}
				startlinno = ++plinno;
				if (doprompt)
					setprompt(2);
			} else {
				const char *p
					= xxreadtoken_chars + sizeof(xxreadtoken_chars) - 1;

				if (c != PEOF) {
					if (c == '\n') {
						plinno++;
						needprompt = doprompt;
					}

					p = strchr(xxreadtoken_chars, c);
					if (p == NULL) {
					  READTOKEN1:
						return readtoken1(c, BASESYNTAX, (char *) NULL, 0);
					}

					if (p - xxreadtoken_chars >= xxreadtoken_singles) {
						if (pgetc() == *p) {    /* double occurrence? */
							p += xxreadtoken_doubles + 1;
						} else {
							pungetc();
						}
					}
				}

				return lasttoken = xxreadtoken_tokens[p - xxreadtoken_chars];
			}
		}
	}
}


#else
#define RETURN(token)   return lasttoken = token

static int
xxreadtoken(void)
{
	int c;

	if (tokpushback) {
		tokpushback = 0;
		return lasttoken;
	}
	if (needprompt) {
		setprompt(2);
	}
	startlinno = plinno;
	for (;;) {      /* until token or start of word found */
		c = pgetc_macro();
		switch (c) {
		case ' ': case '\t':
#ifdef CONFIG_ASH_ALIAS
		case PEOA:
#endif
			continue;
		case '#':
			while ((c = pgetc()) != '\n' && c != PEOF);
			pungetc();
			continue;
		case '\\':
			if (pgetc() == '\n') {
				startlinno = ++plinno;
				if (doprompt)
					setprompt(2);
				continue;
			}
			pungetc();
			goto breakloop;
		case '\n':
			plinno++;
			needprompt = doprompt;
			RETURN(TNL);
		case PEOF:
			RETURN(TEOF);
		case '&':
			if (pgetc() == '&')
				RETURN(TAND);
			pungetc();
			RETURN(TBACKGND);
		case '|':
			if (pgetc() == '|')
				RETURN(TOR);
			pungetc();
			RETURN(TPIPE);
		case ';':
			if (pgetc() == ';')
				RETURN(TENDCASE);
			pungetc();
			RETURN(TSEMI);
		case '(':
			RETURN(TLP);
		case ')':
			RETURN(TRP);
		default:
			goto breakloop;
		}
	}
breakloop:
	return readtoken1(c, BASESYNTAX, (char *)NULL, 0);
#undef RETURN
}
#endif /* NEW_xxreadtoken */


/*
 * If eofmark is NULL, read a word or a redirection symbol.  If eofmark
 * is not NULL, read a here document.  In the latter case, eofmark is the
 * word which marks the end of the document and striptabs is true if
 * leading tabs should be stripped from the document.  The argument firstc
 * is the first character of the input token or document.
 *
 * Because C does not have internal subroutines, I have simulated them
 * using goto's to implement the subroutine linkage.  The following macros
 * will run code that appears at the end of readtoken1.
 */

#define CHECKEND()      {goto checkend; checkend_return:;}
#define PARSEREDIR()    {goto parseredir; parseredir_return:;}
#define PARSESUB()      {goto parsesub; parsesub_return:;}
#define PARSEBACKQOLD() {oldstyle = 1; goto parsebackq; parsebackq_oldreturn:;}
#define PARSEBACKQNEW() {oldstyle = 0; goto parsebackq; parsebackq_newreturn:;}
#define PARSEARITH()    {goto parsearith; parsearith_return:;}

static int
readtoken1(int firstc, int syntax, char *eofmark, int striptabs)
{
	int c = firstc;
	char *out;
	int len;
	char line[EOFMARKLEN + 1];
	struct nodelist *bqlist = 0;
	int quotef = 0;
	int dblquote = 0;
	int varnest = 0;    /* levels of variables expansion */
	int arinest = 0;    /* levels of arithmetic expansion */
	int parenlevel = 0; /* levels of parens in arithmetic */
	int dqvarnest = 0;  /* levels of variables expansion within double quotes */
	int oldstyle = 0;
	int prevsyntax = 0; /* syntax before arithmetic */
#if __GNUC__
	/* Avoid longjmp clobbering */
	(void) &out;
	(void) &quotef;
	(void) &dblquote;
	(void) &varnest;
	(void) &arinest;
	(void) &parenlevel;
	(void) &dqvarnest;
	(void) &oldstyle;
	(void) &prevsyntax;
	(void) &syntax;
#endif

	startlinno = plinno;
	dblquote = 0;
	if (syntax == DQSYNTAX)
		dblquote = 1;
	quotef = 0;
	bqlist = NULL;
	varnest = 0;
	arinest = 0;
	parenlevel = 0;
	dqvarnest = 0;

	STARTSTACKSTR(out);
	loop: { /* for each line, until end of word */
		CHECKEND();     /* set c to PEOF if at end of here document */
		for (;;) {      /* until end of line or end of word */
			CHECKSTRSPACE(4, out);  /* permit 4 calls to USTPUTC */
			switch(SIT(c, syntax)) {
			case CNL:       /* '\n' */
				if (syntax == BASESYNTAX)
					goto endword;   /* exit outer loop */
				USTPUTC(c, out);
				plinno++;
				if (doprompt)
					setprompt(2);
				c = pgetc();
				goto loop;              /* continue outer loop */
			case CWORD:
				USTPUTC(c, out);
				break;
			case CCTL:
				if (eofmark == NULL || dblquote)
					USTPUTC(CTLESC, out);
				USTPUTC(c, out);
				break;
			case CBACK:     /* backslash */
				c = pgetc2();
				if (c == PEOF) {
					USTPUTC(CTLESC, out);
					USTPUTC('\\', out);
					pungetc();
				} else if (c == '\n') {
					if (doprompt)
						setprompt(2);
				} else {
					if (dblquote &&
						c != '\\' && c != '`' &&
						c != '$' && (
							c != '"' ||
							eofmark != NULL)
					) {
						USTPUTC(CTLESC, out);
						USTPUTC('\\', out);
					}
					if (SIT(c, SQSYNTAX) == CCTL)
						USTPUTC(CTLESC, out);
					USTPUTC(c, out);
					quotef++;
				}
				break;
			case CSQUOTE:
				syntax = SQSYNTAX;
quotemark:
				if (eofmark == NULL) {
					USTPUTC(CTLQUOTEMARK, out);
				}
				break;
			case CDQUOTE:
				syntax = DQSYNTAX;
				dblquote = 1;
				goto quotemark;
			case CENDQUOTE:
				if (eofmark != NULL && arinest == 0 &&
				    varnest == 0) {
					USTPUTC(c, out);
				} else {
					if (dqvarnest == 0) {
						syntax = BASESYNTAX;
						dblquote = 0;
					}
					quotef++;
					goto quotemark;
				}
				break;
			case CVAR:      /* '$' */
				PARSESUB();             /* parse substitution */
				break;
			case CENDVAR:   /* '}' */
				if (varnest > 0) {
					varnest--;
					if (dqvarnest > 0) {
						dqvarnest--;
					}
					USTPUTC(CTLENDVAR, out);
				} else {
					USTPUTC(c, out);
				}
				break;
#ifdef CONFIG_ASH_MATH_SUPPORT
			case CLP:       /* '(' in arithmetic */
				parenlevel++;
				USTPUTC(c, out);
				break;
			case CRP:       /* ')' in arithmetic */
				if (parenlevel > 0) {
					USTPUTC(c, out);
					--parenlevel;
				} else {
					if (pgetc() == ')') {
						if (--arinest == 0) {
							USTPUTC(CTLENDARI, out);
							syntax = prevsyntax;
							if (syntax == DQSYNTAX)
								dblquote = 1;
							else
								dblquote = 0;
						} else
							USTPUTC(')', out);
					} else {
						/*
						 * unbalanced parens
						 *  (don't 2nd guess - no error)
						 */
						pungetc();
						USTPUTC(')', out);
					}
				}
				break;
#endif
			case CBQUOTE:   /* '`' */
				PARSEBACKQOLD();
				break;
			case CENDFILE:
				goto endword;           /* exit outer loop */
			case CIGN:
				break;
			default:
				if (varnest == 0)
					goto endword;   /* exit outer loop */
#ifdef CONFIG_ASH_ALIAS
				if (c != PEOA)
#endif
					USTPUTC(c, out);

			}
			c = pgetc_macro();
		}
	}
endword:
#ifdef CONFIG_ASH_MATH_SUPPORT
	if (syntax == ARISYNTAX)
		synerror("Missing '))'");
#endif
	if (syntax != BASESYNTAX && ! parsebackquote && eofmark == NULL)
		synerror("Unterminated quoted string");
	if (varnest != 0) {
		startlinno = plinno;
		/* { */
		synerror("Missing '}'");
	}
	USTPUTC('\0', out);
	len = out - (char *)stackblock();
	out = stackblock();
	if (eofmark == NULL) {
		if ((c == '>' || c == '<')
		 && quotef == 0
		 && len <= 2
		 && (*out == '\0' || is_digit(*out))) {
			PARSEREDIR();
			return lasttoken = TREDIR;
		} else {
			pungetc();
		}
	}
	quoteflag = quotef;
	backquotelist = bqlist;
	grabstackblock(len);
	wordtext = out;
	return lasttoken = TWORD;
/* end of readtoken routine */



/*
 * Check to see whether we are at the end of the here document.  When this
 * is called, c is set to the first character of the next input line.  If
 * we are at the end of the here document, this routine sets the c to PEOF.
 */

checkend: {
	if (eofmark) {
#ifdef CONFIG_ASH_ALIAS
		if (c == PEOA) {
			c = pgetc2();
		}
#endif
		if (striptabs) {
			while (c == '\t') {
				c = pgetc2();
			}
		}
		if (c == *eofmark) {
			if (pfgets(line, sizeof line) != NULL) {
				char *p, *q;

				p = line;
				for (q = eofmark + 1 ; *q && *p == *q ; p++, q++);
				if (*p == '\n' && *q == '\0') {
					c = PEOF;
					plinno++;
					needprompt = doprompt;
				} else {
					pushstring(line, NULL);
				}
			}
		}
	}
	goto checkend_return;
}


/*
 * Parse a redirection operator.  The variable "out" points to a string
 * specifying the fd to be redirected.  The variable "c" contains the
 * first character of the redirection operator.
 */

parseredir: {
	char fd = *out;
	union node *np;

	np = (union node *)stalloc(sizeof (struct nfile));
	if (c == '>') {
		np->nfile.fd = 1;
		c = pgetc();
		if (c == '>')
			np->type = NAPPEND;
		else if (c == '|')
			np->type = NCLOBBER;
		else if (c == '&')
			np->type = NTOFD;
		else {
			np->type = NTO;
			pungetc();
		}
	} else {        /* c == '<' */
		np->nfile.fd = 0;
		switch (c = pgetc()) {
		case '<':
			if (sizeof (struct nfile) != sizeof (struct nhere)) {
				np = (union node *)stalloc(sizeof (struct nhere));
				np->nfile.fd = 0;
			}
			np->type = NHERE;
			heredoc = (struct heredoc *)stalloc(sizeof (struct heredoc));
			heredoc->here = np;
			if ((c = pgetc()) == '-') {
				heredoc->striptabs = 1;
			} else {
				heredoc->striptabs = 0;
				pungetc();
			}
			break;

		case '&':
			np->type = NFROMFD;
			break;

		case '>':
			np->type = NFROMTO;
			break;

		default:
			np->type = NFROM;
			pungetc();
			break;
		}
	}
	if (fd != '\0')
		np->nfile.fd = digit_val(fd);
	redirnode = np;
	goto parseredir_return;
}


/*
 * Parse a substitution.  At this point, we have read the dollar sign
 * and nothing else.
 */

parsesub: {
	int subtype;
	int typeloc;
	int flags;
	char *p;
	static const char types[] = "}-+?=";

	c = pgetc();
	if (
		c <= PEOA_OR_PEOF  ||
		(c != '(' && c != '{' && !is_name(c) && !is_special(c))
	) {
		USTPUTC('$', out);
		pungetc();
	} else if (c == '(') {  /* $(command) or $((arith)) */
		if (pgetc() == '(') {
#ifdef CONFIG_ASH_MATH_SUPPORT
			PARSEARITH();
#else
			synerror("We unsupport $((arith))");
#endif
		} else {
			pungetc();
			PARSEBACKQNEW();
		}
	} else {
		USTPUTC(CTLVAR, out);
		typeloc = out - (char *)stackblock();
		USTPUTC(VSNORMAL, out);
		subtype = VSNORMAL;
		if (c == '{') {
			c = pgetc();
			if (c == '#') {
				if ((c = pgetc()) == '}')
					c = '#';
				else
					subtype = VSLENGTH;
			}
			else
				subtype = 0;
		}
		if (c > PEOA_OR_PEOF && is_name(c)) {
			do {
				STPUTC(c, out);
				c = pgetc();
			} while (c > PEOA_OR_PEOF && is_in_name(c));
		} else if (is_digit(c)) {
			do {
				STPUTC(c, out);
				c = pgetc();
			} while (is_digit(c));
		}
		else if (is_special(c)) {
			USTPUTC(c, out);
			c = pgetc();
		}
		else
badsub:                 synerror("Bad substitution");

		STPUTC('=', out);
		flags = 0;
		if (subtype == 0) {
			switch (c) {
			case ':':
				flags = VSNUL;
				c = pgetc();
				/*FALLTHROUGH*/
			default:
				p = strchr(types, c);
				if (p == NULL)
					goto badsub;
				subtype = p - types + VSNORMAL;
				break;
			case '%':
			case '#':
				{
					int cc = c;
					subtype = c == '#' ? VSTRIMLEFT :
							     VSTRIMRIGHT;
					c = pgetc();
					if (c == cc)
						subtype++;
					else
						pungetc();
					break;
				}
			}
		} else {
			pungetc();
		}
		if (dblquote || arinest)
			flags |= VSQUOTE;
		*((char *)stackblock() + typeloc) = subtype | flags;
		if (subtype != VSNORMAL) {
			varnest++;
			if (dblquote || arinest) {
				dqvarnest++;
			}
		}
	}
	goto parsesub_return;
}


/*
 * Called to parse command substitutions.  Newstyle is set if the command
 * is enclosed inside $(...); nlpp is a pointer to the head of the linked
 * list of commands (passed by reference), and savelen is the number of
 * characters on the top of the stack which must be preserved.
 */

parsebackq: {
	struct nodelist **nlpp;
	int savepbq;
	union node *n;
	char *volatile str;
	struct jmploc jmploc;
	struct jmploc *volatile savehandler;
	size_t savelen;
	int saveprompt = 0;
#ifdef __GNUC__
	(void) &saveprompt;
#endif

	savepbq = parsebackquote;
	if (setjmp(jmploc.loc)) {
		if (str)
			ckfree(str);
		parsebackquote = 0;
		handler = savehandler;
		longjmp(handler->loc, 1);
	}
	INTOFF;
	str = NULL;
	savelen = out - (char *)stackblock();
	if (savelen > 0) {
		str = ckmalloc(savelen);
		memcpy(str, stackblock(), savelen);
	}
	savehandler = handler;
	handler = &jmploc;
	INTON;
	if (oldstyle) {
		/* We must read until the closing backquote, giving special
		   treatment to some slashes, and then push the string and
		   reread it as input, interpreting it normally.  */
		char *pout;
		int pc;
		size_t psavelen;
		char *pstr;


		STARTSTACKSTR(pout);
		for (;;) {
			if (needprompt) {
				setprompt(2);
			}
			switch (pc = pgetc()) {
			case '`':
				goto done;

			case '\\':
				if ((pc = pgetc()) == '\n') {
					plinno++;
					if (doprompt)
						setprompt(2);
					/*
					 * If eating a newline, avoid putting
					 * the newline into the new character
					 * stream (via the STPUTC after the
					 * switch).
					 */
					continue;
				}
				if (pc != '\\' && pc != '`' && pc != '$'
				    && (!dblquote || pc != '"'))
					STPUTC('\\', pout);
				if (pc > PEOA_OR_PEOF) {
					break;
				}
				/* fall through */

			case PEOF:
#ifdef CONFIG_ASH_ALIAS
			case PEOA:
#endif
				startlinno = plinno;
				synerror("EOF in backquote substitution");

			case '\n':
				plinno++;
				needprompt = doprompt;
				break;

			default:
				break;
			}
			STPUTC(pc, pout);
		}
done:
		STPUTC('\0', pout);
		psavelen = pout - (char *)stackblock();
		if (psavelen > 0) {
			pstr = grabstackstr(pout);
			setinputstring(pstr);
		}
	}
	nlpp = &bqlist;
	while (*nlpp)
		nlpp = &(*nlpp)->next;
	*nlpp = (struct nodelist *)stalloc(sizeof (struct nodelist));
	(*nlpp)->next = NULL;
	parsebackquote = oldstyle;

	if (oldstyle) {
		saveprompt = doprompt;
		doprompt = 0;
	}

	n = list(2);

	if (oldstyle)
		doprompt = saveprompt;
	else {
		if (readtoken() != TRP)
			synexpect(TRP);
	}

	(*nlpp)->n = n;
	if (oldstyle) {
		/*
		 * Start reading from old file again, ignoring any pushed back
		 * tokens left from the backquote parsing
		 */
		popfile();
		tokpushback = 0;
	}
	while (stackblocksize() <= savelen)
		growstackblock();
	STARTSTACKSTR(out);
	if (str) {
		memcpy(out, str, savelen);
		STADJUST(savelen, out);
		INTOFF;
		ckfree(str);
		str = NULL;
		INTON;
	}
	parsebackquote = savepbq;
	handler = savehandler;
	if (arinest || dblquote)
		USTPUTC(CTLBACKQ | CTLQUOTE, out);
	else
		USTPUTC(CTLBACKQ, out);
	if (oldstyle)
		goto parsebackq_oldreturn;
	else
		goto parsebackq_newreturn;
}

#ifdef CONFIG_ASH_MATH_SUPPORT
/*
 * Parse an arithmetic expansion (indicate start of one and set state)
 */
parsearith: {

	if (++arinest == 1) {
		prevsyntax = syntax;
		syntax = ARISYNTAX;
		USTPUTC(CTLARI, out);
		if (dblquote)
			USTPUTC('"',out);
		else
			USTPUTC(' ',out);
	} else {
		/*
		 * we collapse embedded arithmetic expansion to
		 * parenthesis, which should be equivalent
		 */
		USTPUTC('(', out);
	}
	goto parsearith_return;
}
#endif

} /* end of readtoken */



/*
 * Returns true if the text contains nothing to expand (no dollar signs
 * or backquotes).
 */

static int
noexpand(char *text)
{
	char *p;
	char c;

	p = text;
	while ((c = *p++) != '\0') {
		if (c == CTLQUOTEMARK)
			continue;
		if (c == CTLESC)
			p++;
		else if (SIT(c, BASESYNTAX) == CCTL)
			return 0;
	}
	return 1;
}


/*
 * Return of a legal variable name (a letter or underscore followed by zero or
 * more letters, underscores, and digits).
 */

static char *
endofname(const char *name)
{
	char *p;

	p = (char *) name;
	if (! is_name(*p))
		return p;
	while (*++p) {
		if (! is_in_name(*p))
			break;
	}
	return p;
}


/*
 * Called when an unexpected token is read during the parse.  The argument
 * is the token that is expected, or -1 if more than one type of token can
 * occur at this point.
 */

static void synexpect(int token)
{
	char msg[64];
	int l;

	l = sprintf(msg, "%s unexpected", tokname(lasttoken));
	if (token >= 0)
		sprintf(msg + l, " (expecting %s)", tokname(token));
	synerror(msg);
	/* NOTREACHED */
}

static void
synerror(const char *msg)
{
	sh_error("Syntax error: %s", msg);
	/* NOTREACHED */
}


/*
 * called by editline -- any expansions to the prompt
 *    should be added here.
 */

#ifdef CONFIG_ASH_EXPAND_PRMT
static const char *
expandstr(const char *ps)
{
	union node n;

	/* XXX Fix (char *) cast. */
	setinputstring((char *)ps);
	readtoken1(pgetc(), DQSYNTAX, nullstr, 0);
	popfile();

	n.narg.type = NARG;
	n.narg.next = NULL;
	n.narg.text = wordtext;
	n.narg.backquote = backquotelist;

	expandarg(&n, NULL, 0);
	return stackblock();
}
#endif

static void setprompt(int whichprompt)
{
	const char *prompt;
#ifdef CONFIG_ASH_EXPAND_PRMT
	struct stackmark smark;
#endif

	needprompt = 0;

	switch (whichprompt) {
	case 1:
		prompt = ps1val();
		break;
	case 2:
		prompt = ps2val();
		break;
	default:                        /* 0 */
		prompt = nullstr;
	}
#ifdef CONFIG_ASH_EXPAND_PRMT
	setstackmark(&smark);
	stalloc(stackblocksize());
#endif
	putprompt(expandstr(prompt));
#ifdef CONFIG_ASH_EXPAND_PRMT
	popstackmark(&smark);
#endif
}


static const char *const *findkwd(const char *s)
{
	return bsearch(s, tokname_array + KWDOFFSET,
		       (sizeof(tokname_array) / sizeof(const char *)) - KWDOFFSET,
				   sizeof(const char *), pstrcmp);
}

/*      redir.c      */

/*
 * Code for dealing with input/output redirection.
 */

#define EMPTY -2                /* marks an unused slot in redirtab */
#ifndef PIPE_BUF
# define PIPESIZE 4096          /* amount of buffering in a pipe */
#else
# define PIPESIZE PIPE_BUF
#endif

/*
 * Open a file in noclobber mode.
 * The code was copied from bash.
 */
static inline int
noclobberopen(const char *fname)
{
	int r, fd;
	struct stat finfo, finfo2;

	/*
	 * If the file exists and is a regular file, return an error
	 * immediately.
	 */
	r = stat(fname, &finfo);
	if (r == 0 && S_ISREG(finfo.st_mode)) {
		errno = EEXIST;
		return -1;
	}

	/*
	 * If the file was not present (r != 0), make sure we open it
	 * exclusively so that if it is created before we open it, our open
	 * will fail.  Make sure that we do not truncate an existing file.
	 * Note that we don't turn on O_EXCL unless the stat failed -- if the
	 * file was not a regular file, we leave O_EXCL off.
	 */
	if (r != 0)
		return open(fname, O_WRONLY|O_CREAT|O_EXCL, 0666);
	fd = open(fname, O_WRONLY|O_CREAT, 0666);

	/* If the open failed, return the file descriptor right away. */
	if (fd < 0)
		return fd;

	/*
	 * OK, the open succeeded, but the file may have been changed from a
	 * non-regular file to a regular file between the stat and the open.
	 * We are assuming that the O_EXCL open handles the case where FILENAME
	 * did not exist and is symlinked to an existing file between the stat
	 * and open.
	 */

	/*
	 * If we can open it and fstat the file descriptor, and neither check
	 * revealed that it was a regular file, and the file has not been
	 * replaced, return the file descriptor.
	 */
	 if (fstat(fd, &finfo2) == 0 && !S_ISREG(finfo2.st_mode) &&
	     finfo.st_dev == finfo2.st_dev && finfo.st_ino == finfo2.st_ino)
		return fd;

	/* The file has been replaced.  badness. */
	close(fd);
	errno = EEXIST;
	return -1;
}

/*
 * Handle here documents.  Normally we fork off a process to write the
 * data to a pipe.  If the document is short, we can stuff the data in
 * the pipe without forking.
 */

static inline int
openhere(union node *redir)
{
	int pip[2];
	size_t len = 0;

	if (pipe(pip) < 0)
		sh_error("Pipe call failed");
	if (redir->type == NHERE) {
		len = strlen(redir->nhere.doc->narg.text);
		if (len <= PIPESIZE) {
			bb_full_write(pip[1], redir->nhere.doc->narg.text, len);
			goto out;
		}
	}
	if (forkshell((struct job *)NULL, (union node *)NULL, FORK_NOJOB) == 0) {
		close(pip[0]);
		signal(SIGINT, SIG_IGN);
		signal(SIGQUIT, SIG_IGN);
		signal(SIGHUP, SIG_IGN);
#ifdef SIGTSTP
		signal(SIGTSTP, SIG_IGN);
#endif
		signal(SIGPIPE, SIG_DFL);
		if (redir->type == NHERE)
			bb_full_write(pip[1], redir->nhere.doc->narg.text, len);
		else
			expandhere(redir->nhere.doc, pip[1]);
		_exit(0);
	}
out:
	close(pip[1]);
	return pip[0];
}

static int
openredirect(union node *redir)
{
	char *fname;
	int f;

	switch (redir->nfile.type) {
	case NFROM:
		fname = redir->nfile.expfname;
		if ((f = open(fname, O_RDONLY)) < 0)
			goto eopen;
		break;
	case NFROMTO:
		fname = redir->nfile.expfname;
		if ((f = open(fname, O_RDWR|O_CREAT|O_TRUNC, 0666)) < 0)
			goto ecreate;
		break;
	case NTO:
		/* Take care of noclobber mode. */
		if (Cflag) {
			fname = redir->nfile.expfname;
			if ((f = noclobberopen(fname)) < 0)
				goto ecreate;
			break;
		}
		/* FALLTHROUGH */
	case NCLOBBER:
		fname = redir->nfile.expfname;
		if ((f = open(fname, O_WRONLY|O_CREAT|O_TRUNC, 0666)) < 0)
			goto ecreate;
		break;
	case NAPPEND:
		fname = redir->nfile.expfname;
		if ((f = open(fname, O_WRONLY|O_CREAT|O_APPEND, 0666)) < 0)
			goto ecreate;
		break;
	default:
#ifdef DEBUG
		abort();
#endif
		/* Fall through to eliminate warning. */
	case NTOFD:
	case NFROMFD:
		f = -1;
		break;
	case NHERE:
	case NXHERE:
		f = openhere(redir);
		break;
	}

	return f;
ecreate:
	sh_error("cannot create %s: %s", fname, errmsg(errno, E_CREAT));
eopen:
	sh_error("cannot open %s: %s", fname, errmsg(errno, E_OPEN));
}

static inline void
dupredirect(union node *redir, int f)
{
	int fd = redir->nfile.fd;

	if (redir->nfile.type == NTOFD || redir->nfile.type == NFROMFD) {
		if (redir->ndup.dupfd >= 0) {   /* if not ">&-" */
				copyfd(redir->ndup.dupfd, fd);
		}
		return;
	}

	if (f != fd) {
		copyfd(f, fd);
		close(f);
	}
	return;
}

/*
 * Process a list of redirection commands.  If the REDIR_PUSH flag is set,
 * old file descriptors are stashed away so that the redirection can be
 * undone by calling popredir.  If the REDIR_BACKQ flag is set, then the
 * standard output, and the standard error if it becomes a duplicate of
 * stdout, is saved in memory.
 */

static void
redirect(union node *redir, int flags)
{
	union node *n;
	struct redirtab *sv;
	int i;
	int fd;
	int newfd;
	int *p;
	nullredirs++;
	if (!redir) {
		return;
	}
	sv = NULL;
	INTOFF;
	if (flags & REDIR_PUSH) {
		struct redirtab *q;
		q = ckmalloc(sizeof (struct redirtab));
		q->next = redirlist;
		redirlist = q;
		q->nullredirs = nullredirs - 1;
		for (i = 0 ; i < 10 ; i++)
			q->renamed[i] = EMPTY;
		nullredirs = 0;
		sv = q;
	}
	n = redir;
	do {
		fd = n->nfile.fd;
		if ((n->nfile.type == NTOFD || n->nfile.type == NFROMFD) &&
		    n->ndup.dupfd == fd)
			continue; /* redirect from/to same file descriptor */

		newfd = openredirect(n);
		if (fd == newfd)
			continue;
		if (sv && *(p = &sv->renamed[fd]) == EMPTY) {
			i = fcntl(fd, F_DUPFD, 10);

			if (i == -1) {
				i = errno;
				if (i != EBADF) {
					close(newfd);
					errno = i;
					sh_error("%d: %m", fd);
					/* NOTREACHED */
				}
			} else {
				*p = i;
				close(fd);
			}
		} else {
			close(fd);
		}
		dupredirect(n, newfd);
	} while ((n = n->nfile.next));
	INTON;
	if (flags & REDIR_SAVEFD2 && sv && sv->renamed[2] >= 0)
		preverrout_fd = sv->renamed[2];
}


/*
 * Undo the effects of the last redirection.
 */

void
popredir(int drop)
{
	struct redirtab *rp;
	int i;

	if (--nullredirs >= 0)
		return;
	INTOFF;
	rp = redirlist;
	for (i = 0 ; i < 10 ; i++) {
		if (rp->renamed[i] != EMPTY) {
			if (!drop) {
				close(i);
				copyfd(rp->renamed[i], i);
			}
			close(rp->renamed[i]);
		}
	}
	redirlist = rp->next;
	nullredirs = rp->nullredirs;
	ckfree(rp);
	INTON;
}

/*
 * Undo all redirections.  Called on error or interrupt.
 */

/*
 * Discard all saved file descriptors.
 */

void
clearredir(int drop)
{
	for (;;) {
		nullredirs = 0;
		if (!redirlist)
			break;
		popredir(drop);
	}
}


/*
 * Copy a file descriptor to be >= to.  Returns -1
 * if the source file descriptor is closed, EMPTY if there are no unused
 * file descriptors left.
 */

int
copyfd(int from, int to)
{
	int newfd;

	newfd = fcntl(from, F_DUPFD, to);
	if (newfd < 0) {
		if (errno == EMFILE)
			return EMPTY;
		else
			sh_error("%d: %m", from);
	}
	return newfd;
}


int
redirectsafe(union node *redir, int flags)
{
	int err;
	volatile int saveint;
	struct jmploc *volatile savehandler = handler;
	struct jmploc jmploc;

	SAVEINT(saveint);
	if (!(err = setjmp(jmploc.loc) * 2)) {
		handler = &jmploc;
		redirect(redir, flags);
	}
	handler = savehandler;
	if (err && exception != EXERROR)
		longjmp(handler->loc, 1);
	RESTOREINT(saveint);
	return err;
}

/*      show.c    */

#ifdef DEBUG
static void shtree(union node *, int, char *, FILE*);
static void shcmd(union node *, FILE *);
static void sharg(union node *, FILE *);
static void indent(int, char *, FILE *);
static void trstring(char *);


void
showtree(union node *n)
{
	trputs("showtree called\n");
	shtree(n, 1, NULL, stdout);
}


static void
shtree(union node *n, int ind, char *pfx, FILE *fp)
{
	struct nodelist *lp;
	const char *s;

	if (n == NULL)
		return;

	indent(ind, pfx, fp);
	switch(n->type) {
	case NSEMI:
		s = "; ";
		goto binop;
	case NAND:
		s = " && ";
		goto binop;
	case NOR:
		s = " || ";
binop:
		shtree(n->nbinary.ch1, ind, NULL, fp);
	   /*    if (ind < 0) */
			fputs(s, fp);
		shtree(n->nbinary.ch2, ind, NULL, fp);
		break;
	case NCMD:
		shcmd(n, fp);
		if (ind >= 0)
			putc('\n', fp);
		break;
	case NPIPE:
		for (lp = n->npipe.cmdlist ; lp ; lp = lp->next) {
			shcmd(lp->n, fp);
			if (lp->next)
				fputs(" | ", fp);
		}
		if (n->npipe.backgnd)
			fputs(" &", fp);
		if (ind >= 0)
			putc('\n', fp);
		break;
	default:
		fprintf(fp, "<node type %d>", n->type);
		if (ind >= 0)
			putc('\n', fp);
		break;
	}
}


static void
shcmd(union node *cmd, FILE *fp)
{
	union node *np;
	int first;
	const char *s;
	int dftfd;

	first = 1;
	for (np = cmd->ncmd.args ; np ; np = np->narg.next) {
		if (! first)
			putchar(' ');
		sharg(np, fp);
		first = 0;
	}
	for (np = cmd->ncmd.redirect ; np ; np = np->nfile.next) {
		if (! first)
			putchar(' ');
		switch (np->nfile.type) {
			case NTO:       s = ">";  dftfd = 1; break;
			case NCLOBBER:  s = ">|"; dftfd = 1; break;
			case NAPPEND:   s = ">>"; dftfd = 1; break;
			case NTOFD:     s = ">&"; dftfd = 1; break;
			case NFROM:     s = "<";  dftfd = 0; break;
			case NFROMFD:   s = "<&"; dftfd = 0; break;
			case NFROMTO:   s = "<>"; dftfd = 0; break;
			default:        s = "*error*"; dftfd = 0; break;
		}
		if (np->nfile.fd != dftfd)
			fprintf(fp, "%d", np->nfile.fd);
		fputs(s, fp);
		if (np->nfile.type == NTOFD || np->nfile.type == NFROMFD) {
			fprintf(fp, "%d", np->ndup.dupfd);
		} else {
			sharg(np->nfile.fname, fp);
		}
		first = 0;
	}
}



static void
sharg(union node *arg, FILE *fp)
{
	char *p;
	struct nodelist *bqlist;
	int subtype;

	if (arg->type != NARG) {
		out1fmt("<node type %d>\n", arg->type);
		abort();
	}
	bqlist = arg->narg.backquote;
	for (p = arg->narg.text ; *p ; p++) {
		switch (*p) {
		case CTLESC:
			putc(*++p, fp);
			break;
		case CTLVAR:
			putc('$', fp);
			putc('{', fp);
			subtype = *++p;
			if (subtype == VSLENGTH)
				putc('#', fp);

			while (*p != '=')
				putc(*p++, fp);

			if (subtype & VSNUL)
				putc(':', fp);

			switch (subtype & VSTYPE) {
			case VSNORMAL:
				putc('}', fp);
				break;
			case VSMINUS:
				putc('-', fp);
				break;
			case VSPLUS:
				putc('+', fp);
				break;
			case VSQUESTION:
				putc('?', fp);
				break;
			case VSASSIGN:
				putc('=', fp);
				break;
			case VSTRIMLEFT:
				putc('#', fp);
				break;
			case VSTRIMLEFTMAX:
				putc('#', fp);
				putc('#', fp);
				break;
			case VSTRIMRIGHT:
				putc('%', fp);
				break;
			case VSTRIMRIGHTMAX:
				putc('%', fp);
				putc('%', fp);
				break;
			case VSLENGTH:
				break;
			default:
				out1fmt("<subtype %d>", subtype);
			}
			break;
		case CTLENDVAR:
		     putc('}', fp);
		     break;
		case CTLBACKQ:
		case CTLBACKQ|CTLQUOTE:
			putc('$', fp);
			putc('(', fp);
			shtree(bqlist->n, -1, NULL, fp);
			putc(')', fp);
			break;
		default:
			putc(*p, fp);
			break;
		}
	}
}


static void
indent(int amount, char *pfx, FILE *fp)
{
	int i;

	for (i = 0 ; i < amount ; i++) {
		if (pfx && i == amount - 1)
			fputs(pfx, fp);
		putc('\t', fp);
	}
}



/*
 * Debugging stuff.
 */


FILE *tracefile;


void
trputc(int c)
{
	if (debug != 1)
		return;
	putc(c, tracefile);
}

void
trace(const char *fmt, ...)
{
	va_list va;

	if (debug != 1)
		return;
	va_start(va, fmt);
	(void) vfprintf(tracefile, fmt, va);
	va_end(va);
}

void
tracev(const char *fmt, va_list va)
{
	if (debug != 1)
		return;
	(void) vfprintf(tracefile, fmt, va);
}


void
trputs(const char *s)
{
	if (debug != 1)
		return;
	fputs(s, tracefile);
}


static void
trstring(char *s)
{
	char *p;
	char c;

	if (debug != 1)
		return;
	putc('"', tracefile);
	for (p = s ; *p ; p++) {
		switch (*p) {
		case '\n':  c = 'n';  goto backslash;
		case '\t':  c = 't';  goto backslash;
		case '\r':  c = 'r';  goto backslash;
		case '"':  c = '"';  goto backslash;
		case '\\':  c = '\\';  goto backslash;
		case CTLESC:  c = 'e';  goto backslash;
		case CTLVAR:  c = 'v';  goto backslash;
		case CTLVAR+CTLQUOTE:  c = 'V';  goto backslash;
		case CTLBACKQ:  c = 'q';  goto backslash;
		case CTLBACKQ+CTLQUOTE:  c = 'Q';  goto backslash;
backslash:        putc('\\', tracefile);
			putc(c, tracefile);
			break;
		default:
			if (*p >= ' ' && *p <= '~')
				putc(*p, tracefile);
			else {
				putc('\\', tracefile);
				putc(*p >> 6 & 03, tracefile);
				putc(*p >> 3 & 07, tracefile);
				putc(*p & 07, tracefile);
			}
			break;
		}
	}
	putc('"', tracefile);
}


void
trargs(char **ap)
{
	if (debug != 1)
		return;
	while (*ap) {
		trstring(*ap++);
		if (*ap)
			putc(' ', tracefile);
		else
			putc('\n', tracefile);
	}
}


void
opentrace(void)
{
	char s[100];
#ifdef O_APPEND
	int flags;
#endif

	if (debug != 1) {
		if (tracefile)
			fflush(tracefile);
		/* leave open because libedit might be using it */
		return;
	}
	scopy("./trace", s);
	if (tracefile) {
		if (!freopen(s, "a", tracefile)) {
			fprintf(stderr, "Can't re-open %s\n", s);
			debug = 0;
			return;
		}
	} else {
		if ((tracefile = fopen(s, "a")) == NULL) {
			fprintf(stderr, "Can't open %s\n", s);
			debug = 0;
			return;
		}
	}
#ifdef O_APPEND
	if ((flags = fcntl(fileno(tracefile), F_GETFL, 0)) >= 0)
		fcntl(fileno(tracefile), F_SETFL, flags | O_APPEND);
#endif
	setlinebuf(tracefile);
	fputs("\nTracing started.\n", tracefile);
}
#endif /* DEBUG */


/*      trap.c       */

/*
 * Sigmode records the current value of the signal handlers for the various
 * modes.  A value of zero means that the current handler is not known.
 * S_HARD_IGN indicates that the signal was ignored on entry to the shell,
 */

#define S_DFL 1                 /* default signal handling (SIG_DFL) */
#define S_CATCH 2               /* signal is caught */
#define S_IGN 3                 /* signal is ignored (SIG_IGN) */
#define S_HARD_IGN 4            /* signal is ignored permenantly */
#define S_RESET 5               /* temporary - to reset a hard ignored sig */



/*
 * The trap builtin.
 */

int
trapcmd(int argc, char **argv)
{
	char *action;
	char **ap;
	int signo;

	nextopt(nullstr);
	ap = argptr;
	if (!*ap) {
		for (signo = 0 ; signo < NSIG ; signo++) {
			if (trap[signo] != NULL) {
				const char *sn;

				sn = u_signal_names(0, &signo, 0);
				if (sn == NULL)
					sn = "???";
				out1fmt("trap -- %s %s\n",
					single_quote(trap[signo]), sn);
			}
		}
		return 0;
	}
	if (!ap[1])
		action = NULL;
	else
		action = *ap++;
	while (*ap) {
		if ((signo = decode_signal(*ap, 0)) < 0)
			sh_error("%s: bad trap", *ap);
		INTOFF;
		if (action) {
			if (action[0] == '-' && action[1] == '\0')
				action = NULL;
			else
				action = savestr(action);
		}
		if (trap[signo])
			ckfree(trap[signo]);
		trap[signo] = action;
		if (signo != 0)
			setsignal(signo);
		INTON;
		ap++;
	}
	return 0;
}


/*
 * Clear traps on a fork.
 */

void
clear_traps(void)
{
	char **tp;

	for (tp = trap ; tp < &trap[NSIG] ; tp++) {
		if (*tp && **tp) {      /* trap not NULL or SIG_IGN */
			INTOFF;
			ckfree(*tp);
			*tp = NULL;
			if (tp != &trap[0])
				setsignal(tp - trap);
			INTON;
		}
	}
}


/*
 * Set the signal handler for the specified signal.  The routine figures
 * out what it should be set to.
 */

void
setsignal(int signo)
{
	int action;
	char *t, tsig;
	struct sigaction act;

	if ((t = trap[signo]) == NULL)
		action = S_DFL;
	else if (*t != '\0')
		action = S_CATCH;
	else
		action = S_IGN;
	if (rootshell && action == S_DFL) {
		switch (signo) {
		case SIGINT:
			if (iflag || minusc || sflag == 0)
				action = S_CATCH;
			break;
		case SIGQUIT:
#ifdef DEBUG
			if (debug)
				break;
#endif
			/* FALLTHROUGH */
		case SIGTERM:
			if (iflag)
				action = S_IGN;
			break;
#if JOBS
		case SIGTSTP:
		case SIGTTOU:
			if (mflag)
				action = S_IGN;
			break;
#endif
		}
	}

	t = &sigmode[signo - 1];
	tsig = *t;
	if (tsig == 0) {
		/*
		 * current setting unknown
		 */
		if (sigaction(signo, 0, &act) == -1) {
			/*
			 * Pretend it worked; maybe we should give a warning
			 * here, but other shells don't. We don't alter
			 * sigmode, so that we retry every time.
			 */
			return;
		}
		if (act.sa_handler == SIG_IGN) {
			if (mflag && (signo == SIGTSTP ||
			     signo == SIGTTIN || signo == SIGTTOU)) {
				tsig = S_IGN;   /* don't hard ignore these */
			} else
				tsig = S_HARD_IGN;
		} else {
			tsig = S_RESET; /* force to be set */
		}
	}
	if (tsig == S_HARD_IGN || tsig == action)
		return;
	switch (action) {
	case S_CATCH:
		act.sa_handler = onsig;
		break;
	case S_IGN:
		act.sa_handler = SIG_IGN;
		break;
	default:
		act.sa_handler = SIG_DFL;
	}
	*t = action;
	act.sa_flags = 0;
	sigfillset(&act.sa_mask);
	sigaction(signo, &act, 0);
}

/*
 * Ignore a signal.
 */

void
ignoresig(int signo)
{
	if (sigmode[signo - 1] != S_IGN && sigmode[signo - 1] != S_HARD_IGN) {
		signal(signo, SIG_IGN);
	}
	sigmode[signo - 1] = S_HARD_IGN;
}


/*
 * Signal handler.
 */

void
onsig(int signo)
{
	gotsig[signo - 1] = 1;
	pendingsigs = signo;

	if (exsig || (signo == SIGINT && !trap[SIGINT])) {
		if (!suppressint)
			onint();
		intpending = 1;
	}
}


/*
 * Called to execute a trap.  Perhaps we should avoid entering new trap
 * handlers while we are executing a trap handler.
 */

int
dotrap(void)
{
	char *p;
	char *q;
	int i;
	int savestatus;
	int skip = 0;

	savestatus = exitstatus;
	pendingsigs = 0;
	xbarrier();

	for (i = 0, q = gotsig; i < NSIG - 1; i++, q++) {
		if (!*q)
			continue;
		*q = 0;

		p = trap[i + 1];
		if (!p)
			continue;
		skip = evalstring(p, SKIPEVAL);
		exitstatus = savestatus;
		if (skip)
			break;
	}

	return skip;
}


/*
 * Controls whether the shell is interactive or not.
 */

void
setinteractive(int on)
{
	static int is_interactive;

	if (++on == is_interactive)
		return;
	is_interactive = on;
	setsignal(SIGINT);
	setsignal(SIGQUIT);
	setsignal(SIGTERM);
#ifndef CONFIG_FEATURE_SH_EXTRA_QUIET
		if(is_interactive > 1) {
			/* Looks like they want an interactive shell */
			static int do_banner;

				if(!do_banner) {
					out1fmt(
			"\n\n%s Built-in shell (ash)\n"
			"Enter 'help' for a list of built-in commands.\n\n",
					BB_BANNER);
					do_banner++;
				}
		}
#endif
}


#ifndef CONFIG_FEATURE_SH_EXTRA_QUIET
/*** List the available builtins ***/

static int helpcmd(int argc, char **argv)
{
	int col, i;

	out1fmt("\nBuilt-in commands:\n-------------------\n");
	for (col = 0, i = 0; i < NUMBUILTINS; i++) {
		col += out1fmt("%c%s", ((col == 0) ? '\t' : ' '),
					  builtincmd[i].name + 1);
		if (col > 60) {
			out1fmt("\n");
			col = 0;
		}
	}
#ifdef CONFIG_FEATURE_SH_STANDALONE_SHELL
	{
		extern const struct BB_applet applets[];
		extern const size_t NUM_APPLETS;

		for (i = 0; i < NUM_APPLETS; i++) {

			col += out1fmt("%c%s", ((col == 0) ? '\t' : ' '), applets[i].name);
			if (col > 60) {
				out1fmt("\n");
				col = 0;
			}
		}
	}
#endif
	out1fmt("\n\n");
	return EXIT_SUCCESS;
}
#endif /* CONFIG_FEATURE_SH_EXTRA_QUIET */

/*
 * Called to exit the shell.
 */

void
exitshell(void)
{
	struct jmploc loc;
	char *p;
	int status;

	status = exitstatus;
	TRACE(("pid %d, exitshell(%d)\n", getpid(), status));
	if (setjmp(loc.loc)) {
		if (exception == EXEXIT)
			_exit(exitstatus);
		goto out;
	}
	handler = &loc;
	if ((p = trap[0])) {
		trap[0] = NULL;
		evalstring(p, 0);
	}
	flushall();
	setjobctl(0);
#ifdef CONFIG_FEATURE_COMMAND_SAVEHISTORY
	if (iflag && rootshell) {
		const char *hp = lookupvar("HISTFILE");

		if(hp != NULL )
			save_history ( hp );
	}
#endif
out:
	_exit(status);
	/* NOTREACHED */
}

static int decode_signal(const char *string, int minsig)
{
	int signo;
	const char *name = u_signal_names(string, &signo, minsig);

	return name ? signo : -1;
}

/*      var.c     */

static struct var *vartab[VTABSIZE];

static int vpcmp(const void *, const void *);
static struct var **findvar(struct var **, const char *);

/*
 * Initialize the variable symbol tables and import the environment
 */


#ifdef CONFIG_ASH_GETOPTS
/*
 * Safe version of setvar, returns 1 on success 0 on failure.
 */

int
setvarsafe(const char *name, const char *val, int flags)
{
	int err;
	volatile int saveint;
	struct jmploc *volatile savehandler = handler;
	struct jmploc jmploc;

	SAVEINT(saveint);
	if (setjmp(jmploc.loc))
		err = 1;
	else {
		handler = &jmploc;
		setvar(name, val, flags);
		err = 0;
	}
	handler = savehandler;
	RESTOREINT(saveint);
	return err;
}
#endif

/*
 * Set the value of a variable.  The flags argument is ored with the
 * flags of the variable.  If val is NULL, the variable is unset.
 */

static void
setvar(const char *name, const char *val, int flags)
{
	char *p, *q;
	size_t namelen;
	char *nameeq;
	size_t vallen;

	q = endofname(name);
	p = strchrnul(q, '=');
	namelen = p - name;
	if (!namelen || p != q)
		sh_error("%.*s: bad variable name", namelen, name);
	vallen = 0;
	if (val == NULL) {
		flags |= VUNSET;
	} else {
		vallen = strlen(val);
	}
	INTOFF;
	p = mempcpy(nameeq = ckmalloc(namelen + vallen + 2), name, namelen);
	if (val) {
		*p++ = '=';
		p = mempcpy(p, val, vallen);
	}
	*p = '\0';
	setvareq(nameeq, flags | VNOSAVE);
	INTON;
}


/*
 * Same as setvar except that the variable and value are passed in
 * the first argument as name=value.  Since the first argument will
 * be actually stored in the table, it should not be a string that
 * will go away.
 * Called with interrupts off.
 */

void
setvareq(char *s, int flags)
{
	struct var *vp, **vpp;

	vpp = hashvar(s);
	flags |= (VEXPORT & (((unsigned) (1 - aflag)) - 1));
	vp = *findvar(vpp, s);
	if (vp) {
		if ((vp->flags & (VREADONLY|VDYNAMIC)) == VREADONLY) {
			const char *n;

			if (flags & VNOSAVE)
				free(s);
			n = vp->text;
			sh_error("%.*s: is read only", strchrnul(n, '=') - n, n);
		}

		if (flags & VNOSET)
			return;

		if (vp->func && (flags & VNOFUNC) == 0)
			(*vp->func)(strchrnul(s, '=') + 1);

		if ((vp->flags & (VTEXTFIXED|VSTACK)) == 0)
			ckfree(vp->text);

		flags |= vp->flags & ~(VTEXTFIXED|VSTACK|VNOSAVE|VUNSET);
	} else {
		if (flags & VNOSET)
			return;
		/* not found */
		vp = ckmalloc(sizeof (*vp));
		vp->next = *vpp;
		vp->func = NULL;
		*vpp = vp;
	}
	if (!(flags & (VTEXTFIXED|VSTACK|VNOSAVE)))
		s = savestr(s);
	vp->text = s;
	vp->flags = flags;
}


/*
 * Process a linked list of variable assignments.
 */

static void
listsetvar(struct strlist *list_set_var, int flags)
{
	struct strlist *lp = list_set_var;

	if (!lp)
		return;
	INTOFF;
	do {
		setvareq(lp->text, flags);
	} while ((lp = lp->next));
	INTON;
}


/*
 * Find the value of a variable.  Returns NULL if not set.
 */

static char *
lookupvar(const char *name)
{
	struct var *v;

	if ((v = *findvar(hashvar(name), name))) {
#ifdef DYNAMIC_VAR
	/*
	 * Dynamic variables are implemented roughly the same way they are
	 * in bash. Namely, they're "special" so long as they aren't unset.
	 * As soon as they're unset, they're no longer dynamic, and dynamic
	 * lookup will no longer happen at that point. -- PFM.
	 */
		if((v->flags & VDYNAMIC))
			(*v->func)(NULL);
#endif
		if(!(v->flags & VUNSET))
			return strchrnul(v->text, '=') + 1;
	}

	return NULL;
}


/*
 * Search the environment of a builtin command.
 */

static char *
bltinlookup(const char *name)
{
	struct strlist *sp;

	for (sp = cmdenviron ; sp ; sp = sp->next) {
		if (varequal(sp->text, name))
			return strchrnul(sp->text, '=') + 1;
	}
	return lookupvar(name);
}


/*
 * Generate a list of variables satisfying the given conditions.
 */

static char **
listvars(int on, int off, char ***end)
{
	struct var **vpp;
	struct var *vp;
	char **ep;
	int mask;

	STARTSTACKSTR(ep);
	vpp = vartab;
	mask = on | off;
	do {
		for (vp = *vpp ; vp ; vp = vp->next)
			if ((vp->flags & mask) == on) {
				if (ep == stackstrend())
					ep = growstackstr();
				*ep++ = (char *) vp->text;
			}
	} while (++vpp < vartab + VTABSIZE);
	if (ep == stackstrend())
		ep = growstackstr();
	if (end)
		*end = ep;
	*ep++ = NULL;
	return grabstackstr(ep);
}


/*
 * POSIX requires that 'set' (but not export or readonly) output the
 * variables in lexicographic order - by the locale's collating order (sigh).
 * Maybe we could keep them in an ordered balanced binary tree
 * instead of hashed lists.
 * For now just roll 'em through qsort for printing...
 */

static int
showvars(const char *sep_prefix, int on, int off)
{
	const char *sep;
	char **ep, **epend;

	ep = listvars(on, off, &epend);
	qsort(ep, epend - ep, sizeof(char *), vpcmp);

	sep = *sep_prefix ? spcstr : sep_prefix;

	for (; ep < epend; ep++) {
		const char *p;
		const char *q;

		p = strchrnul(*ep, '=');
		q = nullstr;
		if (*p)
			q = single_quote(++p);

		out1fmt("%s%s%.*s%s\n", sep_prefix, sep, (int)(p - *ep), *ep, q);
	}

	return 0;
}



/*
 * The export and readonly commands.
 */

static int
exportcmd(int argc, char **argv)
{
	struct var *vp;
	char *name;
	const char *p;
	char **aptr;
	int flag = argv[0][0] == 'r'? VREADONLY : VEXPORT;
	int notp;

	notp = nextopt("p") - 'p';
	if (notp && ((name = *(aptr = argptr)))) {
		do {
			if ((p = strchr(name, '=')) != NULL) {
				p++;
			} else {
				if ((vp = *findvar(hashvar(name), name))) {
					vp->flags |= flag;
					continue;
				}
			}
			setvar(name, p, flag);
		} while ((name = *++aptr) != NULL);
	} else {
		showvars(argv[0], flag, 0);
	}
	return 0;
}


/*
 * Make a variable a local variable.  When a variable is made local, it's
 * value and flags are saved in a localvar structure.  The saved values
 * will be restored when the shell function returns.  We handle the name
 * "-" as a special case.
 */

static inline void
mklocal(char *name)
{
	struct localvar *lvp;
	struct var **vpp;
	struct var *vp;

	INTOFF;
	lvp = ckmalloc(sizeof (struct localvar));
	if (name[0] == '-' && name[1] == '\0') {
		char *p;
		p = ckmalloc(sizeof(optlist));
		lvp->text = memcpy(p, optlist, sizeof(optlist));
		vp = NULL;
	} else {
		char *eq;

		vpp = hashvar(name);
		vp = *findvar(vpp, name);
		eq = strchr(name, '=');
		if (vp == NULL) {
			if (eq)
				setvareq(name, VSTRFIXED);
			else
				setvar(name, NULL, VSTRFIXED);
			vp = *vpp;      /* the new variable */
			lvp->flags = VUNSET;
		} else {
			lvp->text = vp->text;
			lvp->flags = vp->flags;
			vp->flags |= VSTRFIXED|VTEXTFIXED;
			if (eq)
				setvareq(name, 0);
		}
	}
	lvp->vp = vp;
	lvp->next = localvars;
	localvars = lvp;
	INTON;
}

/*
 * The "local" command.
 */

static int
localcmd(int argc, char **argv)
{
	char *name;

	argv = argptr;
	while ((name = *argv++) != NULL) {
		mklocal(name);
	}
	return 0;
}


/*
 * Called after a function returns.
 * Interrupts must be off.
 */

static void
poplocalvars(void)
{
	struct localvar *lvp;
	struct var *vp;

	while ((lvp = localvars) != NULL) {
		localvars = lvp->next;
		vp = lvp->vp;
		TRACE(("poplocalvar %s", vp ? vp->text : "-"));
		if (vp == NULL) {       /* $- saved */
			memcpy(optlist, lvp->text, sizeof(optlist));
			ckfree(lvp->text);
			optschanged();
		} else if ((lvp->flags & (VUNSET|VSTRFIXED)) == VUNSET) {
			unsetvar(vp->text);
		} else {
			if (vp->func)
				(*vp->func)(strchrnul(lvp->text, '=') + 1);
			if ((vp->flags & (VTEXTFIXED|VSTACK)) == 0)
				ckfree(vp->text);
			vp->flags = lvp->flags;
			vp->text = lvp->text;
		}
		ckfree(lvp);
	}
}


/*
 * The unset builtin command.  We unset the function before we unset the
 * variable to allow a function to be unset when there is a readonly variable
 * with the same name.
 */

int
unsetcmd(int argc, char **argv)
{
	char **ap;
	int i;
	int flag = 0;
	int ret = 0;

	while ((i = nextopt("vf")) != '\0') {
		flag = i;
	}

	for (ap = argptr; *ap ; ap++) {
		if (flag != 'f') {
			i = unsetvar(*ap);
			ret |= i;
			if (!(i & 2))
				continue;
		}
		if (flag != 'v')
			unsetfunc(*ap);
	}
	return ret & 1;
}


/*
 * Unset the specified variable.
 */

int
unsetvar(const char *s)
{
	struct var **vpp;
	struct var *vp;
	int retval;

	vpp = findvar(hashvar(s), s);
	vp = *vpp;
	retval = 2;
	if (vp) {
		int flags = vp->flags;

		retval = 1;
		if (flags & VREADONLY)
			goto out;
#ifdef DYNAMIC_VAR
		vp->flags &= ~VDYNAMIC;
#endif
		if (flags & VUNSET)
			goto ok;
		if ((flags & VSTRFIXED) == 0) {
			INTOFF;
			if ((flags & (VTEXTFIXED|VSTACK)) == 0)
				ckfree(vp->text);
			*vpp = vp->next;
			ckfree(vp);
			INTON;
		} else {
			setvar(s, 0, 0);
			vp->flags &= ~VEXPORT;
		}
ok:
		retval = 0;
	}

out:
	return retval;
}



/*
 * Find the appropriate entry in the hash table from the name.
 */

static struct var **
hashvar(const char *p)
{
	unsigned int hashval;

	hashval = ((unsigned char) *p) << 4;
	while (*p && *p != '=')
		hashval += (unsigned char) *p++;
	return &vartab[hashval % VTABSIZE];
}



/*
 * Compares two strings up to the first = or '\0'.  The first
 * string must be terminated by '='; the second may be terminated by
 * either '=' or '\0'.
 */

int
varcmp(const char *p, const char *q)
{
	int c, d;

	while ((c = *p) == (d = *q)) {
		if (!c || c == '=')
			goto out;
		p++;
		q++;
	}
	if (c == '=')
		c = 0;
	if (d == '=')
		d = 0;
out:
	return c - d;
}

static int
vpcmp(const void *a, const void *b)
{
	return varcmp(*(const char **)a, *(const char **)b);
}

static struct var **
findvar(struct var **vpp, const char *name)
{
	for (; *vpp; vpp = &(*vpp)->next) {
		if (varequal((*vpp)->text, name)) {
			break;
		}
	}
	return vpp;
}
/*      setmode.c      */

#include <sys/times.h>

static const unsigned char timescmd_str[] = {
	' ',  offsetof(struct tms, tms_utime),
	'\n', offsetof(struct tms, tms_stime),
	' ',  offsetof(struct tms, tms_cutime),
	'\n', offsetof(struct tms, tms_cstime),
	0
};

static int timescmd(int ac, char **av)
{
	long int clk_tck, s, t;
	const unsigned char *p;
	struct tms buf;

	clk_tck = sysconf(_SC_CLK_TCK);
	times(&buf);

	p = timescmd_str;
	do {
		t = *(clock_t *)(((char *) &buf) + p[1]);
		s = t / clk_tck;
		out1fmt("%ldm%ld.%.3lds%c",
			s/60, s%60,
			((t - s * clk_tck) * 1000) / clk_tck,
			p[0]);
	} while (*(p += 2));

	return 0;
}

#ifdef CONFIG_ASH_MATH_SUPPORT
static arith_t
dash_arith(const char *s)
{
	arith_t result;
	int errcode = 0;

	INTOFF;
	result = arith(s, &errcode);
	if (errcode < 0) {
		if (errcode == -3)
			sh_error("exponent less than 0");
		else if (errcode == -2)
			sh_error("divide by zero");
		else if (errcode == -5)
			sh_error("expression recursion loop detected");
		else
			synerror(s);
	}
	INTON;

	return (result);
}


/*
 *  The let builtin. partial stolen from GNU Bash, the Bourne Again SHell.
 *  Copyright (C) 1987, 1989, 1991 Free Software Foundation, Inc.
 *
 *  Copyright (C) 2003 Vladimir Oleynik <dzo@simtreas.ru>
 */

static int
letcmd(int argc, char **argv)
{
	char **ap;
	arith_t i;

	ap = argv + 1;
	if(!*ap)
		sh_error("expression expected");
	for (ap = argv + 1; *ap; ap++) {
		i = dash_arith(*ap);
	}

	return (!i);
}
#endif /* CONFIG_ASH_MATH_SUPPORT */

/*      miscbltin.c  */

/*
 * Miscellaneous builtins.
 */

#undef rflag

#ifdef __GLIBC__
#if __GLIBC__ == 2 && __GLIBC_MINOR__ < 1
typedef enum __rlimit_resource rlim_t;
#endif
#endif


/*
 * The read builtin.  The -e option causes backslashes to escape the
 * following character.
 *
 * This uses unbuffered input, which may be avoidable in some cases.
 */

static int
readcmd(int argc, char **argv)
{
	char **ap;
	int backslash;
	char c;
	int rflag;
	char *prompt;
	const char *ifs;
	char *p;
	int startword;
	int status;
	int i;
#if defined(CONFIG_ASH_READ_NCHARS)
	int nch_flag = 0;
	int nchars = 0;
	int silent = 0;
	struct termios tty, old_tty;
#endif
#if defined(CONFIG_ASH_READ_TIMEOUT)
	fd_set set;
	struct timeval ts;

	ts.tv_sec = ts.tv_usec = 0;
#endif

	rflag = 0;
	prompt = NULL;
#if defined(CONFIG_ASH_READ_NCHARS) && defined(CONFIG_ASH_READ_TIMEOUT)
	while ((i = nextopt("p:rt:n:s")) != '\0')
#elif defined(CONFIG_ASH_READ_NCHARS)
	while ((i = nextopt("p:rn:s")) != '\0')
#elif defined(CONFIG_ASH_READ_TIMEOUT)
	while ((i = nextopt("p:rt:")) != '\0')
#else
	while ((i = nextopt("p:r")) != '\0')
#endif
	{
		switch(i) {
		case 'p':
			prompt = optionarg;
			break;
#if defined(CONFIG_ASH_READ_NCHARS)
		case 'n':
			nchars = strtol(optionarg, &p, 10);
			if (*p)
				sh_error("invalid count");
			nch_flag = (nchars > 0);
			break;
		case 's':
			silent = 1;
			break;
#endif
#if defined(CONFIG_ASH_READ_TIMEOUT)
		case 't':
			ts.tv_sec = strtol(optionarg, &p, 10);
			ts.tv_usec = 0;
			if (*p == '.') {
				char *p2;
				if (*++p) {
					int scale;
					ts.tv_usec = strtol(p, &p2, 10);
					if (*p2)
						sh_error("invalid timeout");
					scale = p2 - p;
					/* normalize to usec */
					if (scale > 6)
						sh_error("invalid timeout");
					while (scale++ < 6)
						ts.tv_usec *= 10;
				}
			} else if (*p) {
				sh_error("invalid timeout");
			}
			if ( ! ts.tv_sec && ! ts.tv_usec)
				sh_error("invalid timeout");
			break;
#endif
		case 'r':
			rflag = 1;
			break;
		default:
			break;
		}
	}
	if (prompt && isatty(0)) {
		out2str(prompt);
	}
	if (*(ap = argptr) == NULL)
		sh_error("arg count");
	if ((ifs = bltinlookup("IFS")) == NULL)
		ifs = defifs;
#if defined(CONFIG_ASH_READ_NCHARS)
	if (nch_flag || silent) {
		tcgetattr(0, &tty);
		old_tty = tty;
		if (nch_flag) {
		    tty.c_lflag &= ~ICANON;
		    tty.c_cc[VMIN] = nchars;
		}
		if (silent) {
		    tty.c_lflag &= ~(ECHO|ECHOK|ECHONL);

		}
		tcsetattr(0, TCSANOW, &tty);
	}
#endif
#if defined(CONFIG_ASH_READ_TIMEOUT)
	if (ts.tv_sec || ts.tv_usec) {
		FD_ZERO (&set);
		FD_SET (0, &set);

		i = select (FD_SETSIZE, &set, NULL, NULL, &ts);
		if (!i) {
#if defined(CONFIG_ASH_READ_NCHARS)
			if (nch_flag)
				tcsetattr(0, TCSANOW, &old_tty);
#endif
			return 1;
		}
	}
#endif
	status = 0;
	startword = 1;
	backslash = 0;
	STARTSTACKSTR(p);
#if defined(CONFIG_ASH_READ_NCHARS)
	while (!nch_flag || nchars--)
#else
	for (;;)
#endif
	{
		if (read(0, &c, 1) != 1) {
			status = 1;
			break;
		}
		if (c == '\0')
			continue;
		if (backslash) {
			backslash = 0;
			if (c != '\n')
				goto put;
			continue;
		}
		if (!rflag && c == '\\') {
			backslash++;
			continue;
		}
		if (c == '\n')
			break;
		if (startword && *ifs == ' ' && strchr(ifs, c)) {
			continue;
		}
		startword = 0;
		if (ap[1] != NULL && strchr(ifs, c) != NULL) {
			STACKSTRNUL(p);
			setvar(*ap, stackblock(), 0);
			ap++;
			startword = 1;
			STARTSTACKSTR(p);
		} else {
put:
			STPUTC(c, p);
		}
	}
#if defined(CONFIG_ASH_READ_NCHARS)
	if (nch_flag || silent)
		tcsetattr(0, TCSANOW, &old_tty);
#endif

	STACKSTRNUL(p);
	/* Remove trailing blanks */
	while ((char *)stackblock() <= --p && strchr(ifs, *p) != NULL)
		*p = '\0';
	setvar(*ap, stackblock(), 0);
	while (*++ap != NULL)
		setvar(*ap, nullstr, 0);
	return status;
}


static int umaskcmd(int argc, char **argv)
{
	static const char permuser[3] = "ugo";
	static const char permmode[3] = "rwx";
	static const short int permmask[] = {
		S_IRUSR, S_IWUSR, S_IXUSR,
		S_IRGRP, S_IWGRP, S_IXGRP,
		S_IROTH, S_IWOTH, S_IXOTH
	};

	char *ap;
	mode_t mask;
	int i;
	int symbolic_mode = 0;

	while (nextopt("S") != '\0') {
		symbolic_mode = 1;
	}

	INTOFF;
	mask = umask(0);
	umask(mask);
	INTON;

	if ((ap = *argptr) == NULL) {
		if (symbolic_mode) {
			char buf[18];
			char *p = buf;

			for (i = 0; i < 3; i++) {
				int j;

				*p++ = permuser[i];
				*p++ = '=';
				for (j = 0; j < 3; j++) {
					if ((mask & permmask[3 * i + j]) == 0) {
						*p++ = permmode[j];
					}
				}
				*p++ = ',';
			}
			*--p = 0;
			puts(buf);
		} else {
			out1fmt("%.4o\n", mask);
		}
	} else {
		if (is_digit((unsigned char) *ap)) {
			mask = 0;
			do {
				if (*ap >= '8' || *ap < '0')
					sh_error(illnum, argv[1]);
				mask = (mask << 3) + (*ap - '0');
			} while (*++ap != '\0');
			umask(mask);
		} else {
			mask = ~mask & 0777;
			if (!bb_parse_mode(ap, &mask)) {
				sh_error("Illegal mode: %s", ap);
			}
			umask(~mask & 0777);
		}
	}
	return 0;
}

/*
 * ulimit builtin
 *
 * This code, originally by Doug Gwyn, Doug Kingston, Eric Gisin, and
 * Michael Rendell was ripped from pdksh 5.0.8 and hacked for use with
 * ash by J.T. Conklin.
 *
 * Public domain.
 */

struct limits {
	const char *name;
	int     cmd;
	int     factor; /* multiply by to get rlim_{cur,max} values */
	char    option;
};

static const struct limits limits[] = {
#ifdef RLIMIT_CPU
	{ "time(seconds)",              RLIMIT_CPU,        1, 't' },
#endif
#ifdef RLIMIT_FSIZE
	{ "file(blocks)",               RLIMIT_FSIZE,    512, 'f' },
#endif
#ifdef RLIMIT_DATA
	{ "data(kbytes)",               RLIMIT_DATA,    1024, 'd' },
#endif
#ifdef RLIMIT_STACK
	{ "stack(kbytes)",              RLIMIT_STACK,   1024, 's' },
#endif
#ifdef  RLIMIT_CORE
	{ "coredump(blocks)",           RLIMIT_CORE,     512, 'c' },
#endif
#ifdef RLIMIT_RSS
	{ "memory(kbytes)",             RLIMIT_RSS,     1024, 'm' },
#endif
#ifdef RLIMIT_MEMLOCK
	{ "locked memory(kbytes)",      RLIMIT_MEMLOCK, 1024, 'l' },
#endif
#ifdef RLIMIT_NPROC
	{ "process",                    RLIMIT_NPROC,      1, 'p' },
#endif
#ifdef RLIMIT_NOFILE
	{ "nofiles",                    RLIMIT_NOFILE,     1, 'n' },
#endif
#ifdef RLIMIT_AS
	{ "vmemory(kbytes)",            RLIMIT_AS,      1024, 'v' },
#endif
#ifdef RLIMIT_LOCKS
	{ "locks",                      RLIMIT_LOCKS,      1, 'w' },
#endif
	{ (char *) 0,                   0,                 0,  '\0' }
};

enum limtype { SOFT = 0x1, HARD = 0x2 };

static void printlim(enum limtype how, const struct rlimit *limit,
			const struct limits *l)
{
	rlim_t val;

	val = limit->rlim_max;
	if (how & SOFT)
		val = limit->rlim_cur;

	if (val == RLIM_INFINITY)
		out1fmt("unlimited\n");
	else {
		val /= l->factor;
		out1fmt("%lld\n", (long long) val);
	}
}

int
ulimitcmd(int argc, char **argv)
{
	int     c;
	rlim_t val = 0;
	enum limtype how = SOFT | HARD;
	const struct limits     *l;
	int             set, all = 0;
	int             optc, what;
	struct rlimit   limit;

	what = 'f';
	while ((optc = nextopt("HSa"
#ifdef RLIMIT_CPU
				"t"
#endif
#ifdef RLIMIT_FSIZE
				"f"
#endif
#ifdef RLIMIT_DATA
				"d"
#endif
#ifdef RLIMIT_STACK
				"s"
#endif
#ifdef RLIMIT_CORE
				"c"
#endif
#ifdef RLIMIT_RSS
				"m"
#endif
#ifdef RLIMIT_MEMLOCK
				"l"
#endif
#ifdef RLIMIT_NPROC
				"p"
#endif
#ifdef RLIMIT_NOFILE
				"n"
#endif
#ifdef RLIMIT_AS
				"v"
#endif
#ifdef RLIMIT_LOCKS
				"w"
#endif
						)) != '\0')
		switch (optc) {
		case 'H':
			how = HARD;
			break;
		case 'S':
			how = SOFT;
			break;
		case 'a':
			all = 1;
			break;
		default:
			what = optc;
		}

	for (l = limits; l->option != what; l++)
		;

	set = *argptr ? 1 : 0;
	if (set) {
		char *p = *argptr;

		if (all || argptr[1])
			sh_error("too many arguments");
		if (strncmp(p, "unlimited\n", 9) == 0)
			val = RLIM_INFINITY;
		else {
			val = (rlim_t) 0;

			while ((c = *p++) >= '0' && c <= '9')
			{
				val = (val * 10) + (long)(c - '0');
				if (val < (rlim_t) 0)
					break;
			}
			if (c)
				sh_error("bad number");
			val *= l->factor;
		}
	}
	if (all) {
		for (l = limits; l->name; l++) {
			getrlimit(l->cmd, &limit);
			out1fmt("%-20s ", l->name);
			printlim(how, &limit, l);
		}
		return 0;
	}

	getrlimit(l->cmd, &limit);
	if (set) {
		if (how & HARD)
			limit.rlim_max = val;
		if (how & SOFT)
			limit.rlim_cur = val;
		if (setrlimit(l->cmd, &limit) < 0)
			sh_error("error setting limit (%m)");
	} else {
		printlim(how, &limit, l);
	}
	return 0;
}


#ifdef CONFIG_ASH_MATH_SUPPORT

/* Copyright (c) 2001 Aaron Lehmann <aaronl@vitelus.com>

   Permission is hereby granted, free of charge, to any person obtaining
   a copy of this software and associated documentation files (the
   "Software"), to deal in the Software without restriction, including
   without limitation the rights to use, copy, modify, merge, publish,
   distribute, sublicense, and/or sell copies of the Software, and to
   permit persons to whom the Software is furnished to do so, subject to
   the following conditions:

   The above copyright notice and this permission notice shall be
   included in all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
   MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
   CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
   TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
   SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

/* This is my infix parser/evaluator. It is optimized for size, intended
 * as a replacement for yacc-based parsers. However, it may well be faster
 * than a comparable parser written in yacc. The supported operators are
 * listed in #defines below. Parens, order of operations, and error handling
 * are supported. This code is thread safe. The exact expression format should
 * be that which POSIX specifies for shells. */

/* The code uses a simple two-stack algorithm. See
 * http://www.onthenet.com.au/~grahamis/int2008/week02/lect02.html
 * for a detailed explanation of the infix-to-postfix algorithm on which
 * this is based (this code differs in that it applies operators immediately
 * to the stack instead of adding them to a queue to end up with an
 * expression). */

/* To use the routine, call it with an expression string and error return
 * pointer */

/*
 * Aug 24, 2001              Manuel Novoa III
 *
 * Reduced the generated code size by about 30% (i386) and fixed several bugs.
 *
 * 1) In arith_apply():
 *    a) Cached values of *numptr and &(numptr[-1]).
 *    b) Removed redundant test for zero denominator.
 *
 * 2) In arith():
 *    a) Eliminated redundant code for processing operator tokens by moving
 *       to a table-based implementation.  Also folded handling of parens
 *       into the table.
 *    b) Combined all 3 loops which called arith_apply to reduce generated
 *       code size at the cost of speed.
 *
 * 3) The following expressions were treated as valid by the original code:
 *       1()  ,    0!  ,    1 ( *3 )   .
 *    These bugs have been fixed by internally enclosing the expression in
 *    parens and then checking that all binary ops and right parens are
 *    preceded by a valid expression (NUM_TOKEN).
 *
 * Note: It may be desirable to replace Aaron's test for whitespace with
 * ctype's isspace() if it is used by another busybox applet or if additional
 * whitespace chars should be considered.  Look below the "#include"s for a
 * precompiler test.
 */

/*
 * Aug 26, 2001              Manuel Novoa III
 *
 * Return 0 for null expressions.  Pointed out by Vladimir Oleynik.
 *
 * Merge in Aaron's comments previously posted to the busybox list,
 * modified slightly to take account of my changes to the code.
 *
 */

/*
 *  (C) 2003 Vladimir Oleynik <dzo@simtreas.ru>
 *
 * - allow access to variable,
 *   used recursive find value indirection (c=2*2; a="c"; $((a+=2)) produce 6)
 * - realize assign syntax (VAR=expr, +=, *= etc)
 * - realize exponentiation (** operator)
 * - realize comma separated - expr, expr
 * - realise ++expr --expr expr++ expr--
 * - realise expr ? expr : expr (but, second expr calculate always)
 * - allow hexadecimal and octal numbers
 * - was restored loses XOR operator
 * - remove one goto label, added three ;-)
 * - protect $((num num)) as true zero expr (Manuel`s error)
 * - always use special isspace(), see comment from bash ;-)
 */


#define arith_isspace(arithval) \
	(arithval == ' ' || arithval == '\n' || arithval == '\t')


typedef unsigned char operator;

/* An operator's token id is a bit of a bitfield. The lower 5 bits are the
 * precedence, and 3 high bits are an ID unique across operators of that
 * precedence. The ID portion is so that multiple operators can have the
 * same precedence, ensuring that the leftmost one is evaluated first.
 * Consider * and /. */

#define tok_decl(prec,id) (((id)<<5)|(prec))
#define PREC(op) ((op) & 0x1F)

#define TOK_LPAREN tok_decl(0,0)

#define TOK_COMMA tok_decl(1,0)

#define TOK_ASSIGN tok_decl(2,0)
#define TOK_AND_ASSIGN tok_decl(2,1)
#define TOK_OR_ASSIGN tok_decl(2,2)
#define TOK_XOR_ASSIGN tok_decl(2,3)
#define TOK_PLUS_ASSIGN tok_decl(2,4)
#define TOK_MINUS_ASSIGN tok_decl(2,5)
#define TOK_LSHIFT_ASSIGN tok_decl(2,6)
#define TOK_RSHIFT_ASSIGN tok_decl(2,7)

#define TOK_MUL_ASSIGN tok_decl(3,0)
#define TOK_DIV_ASSIGN tok_decl(3,1)
#define TOK_REM_ASSIGN tok_decl(3,2)

/* all assign is right associativity and precedence eq, but (7+3)<<5 > 256 */
#define convert_prec_is_assing(prec) do { if(prec == 3) prec = 2; } while(0)

/* conditional is right associativity too */
#define TOK_CONDITIONAL tok_decl(4,0)
#define TOK_CONDITIONAL_SEP tok_decl(4,1)

#define TOK_OR tok_decl(5,0)

#define TOK_AND tok_decl(6,0)

#define TOK_BOR tok_decl(7,0)

#define TOK_BXOR tok_decl(8,0)

#define TOK_BAND tok_decl(9,0)

#define TOK_EQ tok_decl(10,0)
#define TOK_NE tok_decl(10,1)

#define TOK_LT tok_decl(11,0)
#define TOK_GT tok_decl(11,1)
#define TOK_GE tok_decl(11,2)
#define TOK_LE tok_decl(11,3)

#define TOK_LSHIFT tok_decl(12,0)
#define TOK_RSHIFT tok_decl(12,1)

#define TOK_ADD tok_decl(13,0)
#define TOK_SUB tok_decl(13,1)

#define TOK_MUL tok_decl(14,0)
#define TOK_DIV tok_decl(14,1)
#define TOK_REM tok_decl(14,2)

/* exponent is right associativity */
#define TOK_EXPONENT tok_decl(15,1)

/* For now unary operators. */
#define UNARYPREC 16
#define TOK_BNOT tok_decl(UNARYPREC,0)
#define TOK_NOT tok_decl(UNARYPREC,1)

#define TOK_UMINUS tok_decl(UNARYPREC+1,0)
#define TOK_UPLUS tok_decl(UNARYPREC+1,1)

#define PREC_PRE (UNARYPREC+2)

#define TOK_PRE_INC tok_decl(PREC_PRE, 0)
#define TOK_PRE_DEC tok_decl(PREC_PRE, 1)

#define PREC_POST (UNARYPREC+3)

#define TOK_POST_INC tok_decl(PREC_POST, 0)
#define TOK_POST_DEC tok_decl(PREC_POST, 1)

#define SPEC_PREC (UNARYPREC+4)

#define TOK_NUM tok_decl(SPEC_PREC, 0)
#define TOK_RPAREN tok_decl(SPEC_PREC, 1)

#define NUMPTR (*numstackptr)

static inline int tok_have_assign(operator op)
{
	operator prec = PREC(op);

	convert_prec_is_assing(prec);
	return (prec == PREC(TOK_ASSIGN) ||
			prec == PREC_PRE || prec == PREC_POST);
}

static inline int is_right_associativity(operator prec)
{
    return (prec == PREC(TOK_ASSIGN) || prec == PREC(TOK_EXPONENT) ||
	    prec == PREC(TOK_CONDITIONAL));
}


typedef struct ARITCH_VAR_NUM {
	arith_t val;
	arith_t contidional_second_val;
	char contidional_second_val_initialized;
	char *var;      /* if NULL then is regular number,
			   else is variable name */
} v_n_t;


typedef struct CHK_VAR_RECURSIVE_LOOPED {
	const char *var;
	struct CHK_VAR_RECURSIVE_LOOPED *next;
} chk_var_recursive_looped_t;

static chk_var_recursive_looped_t *prev_chk_var_recursive;


static int arith_lookup_val(v_n_t *t)
{
    if(t->var) {
	const char * p = lookupvar(t->var);

	if(p) {
	    int errcode;

	    /* recursive try as expression */
	    chk_var_recursive_looped_t *cur;
	    chk_var_recursive_looped_t cur_save;

	    for(cur = prev_chk_var_recursive; cur; cur = cur->next) {
		if(strcmp(cur->var, t->var) == 0) {
		    /* expression recursion loop detected */
		    return -5;
		}
	    }
	    /* save current lookuped var name */
	    cur = prev_chk_var_recursive;
	    cur_save.var = t->var;
	    cur_save.next = cur;
	    prev_chk_var_recursive = &cur_save;

	    t->val = arith (p, &errcode);
	    /* restore previous ptr after recursiving */
	    prev_chk_var_recursive = cur;
	    return errcode;
	} else {
	    /* allow undefined var as 0 */
	    t->val = 0;
	}
    }
    return 0;
}

/* "applying" a token means performing it on the top elements on the integer
 * stack. For a unary operator it will only change the top element, but a
 * binary operator will pop two arguments and push a result */
static inline int
arith_apply(operator op, v_n_t *numstack, v_n_t **numstackptr)
{
	v_n_t *numptr_m1;
	arith_t numptr_val, rez;
	int ret_arith_lookup_val;

	if (NUMPTR == numstack) goto err; /* There is no operator that can work
										 without arguments */
	numptr_m1 = NUMPTR - 1;

	/* check operand is var with noninteger value */
	ret_arith_lookup_val = arith_lookup_val(numptr_m1);
	if(ret_arith_lookup_val)
		return ret_arith_lookup_val;

	rez = numptr_m1->val;
	if (op == TOK_UMINUS)
		rez *= -1;
	else if (op == TOK_NOT)
		rez = !rez;
	else if (op == TOK_BNOT)
		rez = ~rez;
	else if (op == TOK_POST_INC || op == TOK_PRE_INC)
		rez++;
	else if (op == TOK_POST_DEC || op == TOK_PRE_DEC)
		rez--;
	else if (op != TOK_UPLUS) {
		/* Binary operators */

	    /* check and binary operators need two arguments */
	    if (numptr_m1 == numstack) goto err;

	    /* ... and they pop one */
	    --NUMPTR;
	    numptr_val = rez;
	    if (op == TOK_CONDITIONAL) {
		if(! numptr_m1->contidional_second_val_initialized) {
		    /* protect $((expr1 ? expr2)) without ": expr" */
		    goto err;
		}
		rez = numptr_m1->contidional_second_val;
	    } else if(numptr_m1->contidional_second_val_initialized) {
		    /* protect $((expr1 : expr2)) without "expr ? " */
		    goto err;
	    }
	    numptr_m1 = NUMPTR - 1;
	    if(op != TOK_ASSIGN) {
		/* check operand is var with noninteger value for not '=' */
		ret_arith_lookup_val = arith_lookup_val(numptr_m1);
		if(ret_arith_lookup_val)
		    return ret_arith_lookup_val;
	    }
	    if (op == TOK_CONDITIONAL) {
		    numptr_m1->contidional_second_val = rez;
	    }
	    rez = numptr_m1->val;
	    if (op == TOK_BOR || op == TOK_OR_ASSIGN)
			rez |= numptr_val;
	    else if (op == TOK_OR)
			rez = numptr_val || rez;
	    else if (op == TOK_BAND || op == TOK_AND_ASSIGN)
			rez &= numptr_val;
	    else if (op == TOK_BXOR || op == TOK_XOR_ASSIGN)
			rez ^= numptr_val;
	    else if (op == TOK_AND)
			rez = rez && numptr_val;
	    else if (op == TOK_EQ)
			rez = (rez == numptr_val);
	    else if (op == TOK_NE)
			rez = (rez != numptr_val);
	    else if (op == TOK_GE)
			rez = (rez >= numptr_val);
	    else if (op == TOK_RSHIFT || op == TOK_RSHIFT_ASSIGN)
			rez >>= numptr_val;
	    else if (op == TOK_LSHIFT || op == TOK_LSHIFT_ASSIGN)
			rez <<= numptr_val;
	    else if (op == TOK_GT)
			rez = (rez > numptr_val);
	    else if (op == TOK_LT)
			rez = (rez < numptr_val);
	    else if (op == TOK_LE)
			rez = (rez <= numptr_val);
	    else if (op == TOK_MUL || op == TOK_MUL_ASSIGN)
			rez *= numptr_val;
	    else if (op == TOK_ADD || op == TOK_PLUS_ASSIGN)
			rez += numptr_val;
	    else if (op == TOK_SUB || op == TOK_MINUS_ASSIGN)
			rez -= numptr_val;
	    else if (op == TOK_ASSIGN || op == TOK_COMMA)
			rez = numptr_val;
	    else if (op == TOK_CONDITIONAL_SEP) {
			if (numptr_m1 == numstack) {
			    /* protect $((expr : expr)) without "expr ? " */
			    goto err;
			}
			numptr_m1->contidional_second_val_initialized = op;
			numptr_m1->contidional_second_val = numptr_val;
	    }
	    else if (op == TOK_CONDITIONAL) {
			rez = rez ?
			      numptr_val : numptr_m1->contidional_second_val;
	    }
	    else if(op == TOK_EXPONENT) {
			if(numptr_val < 0)
				return -3;      /* exponent less than 0 */
			else {
				arith_t c = 1;

				if(numptr_val)
					while(numptr_val--)
						c *= rez;
				rez = c;
			}
	    }
	    else if(numptr_val==0)          /* zero divisor check */
			return -2;
	    else if (op == TOK_DIV || op == TOK_DIV_ASSIGN)
			rez /= numptr_val;
	    else if (op == TOK_REM || op == TOK_REM_ASSIGN)
			rez %= numptr_val;
	}
	if(tok_have_assign(op)) {
		char buf[32];

		if(numptr_m1->var == NULL) {
			/* Hmm, 1=2 ? */
			goto err;
		}
		/* save to shell variable */
#ifdef CONFIG_ASH_MATH_SUPPORT_64
		snprintf(buf, sizeof(buf), "%lld", arith_t_type rez);
#else
		snprintf(buf, sizeof(buf), "%ld", arith_t_type rez);
#endif
		setvar(numptr_m1->var, buf, 0);
		/* after saving, make previous value for v++ or v-- */
		if(op == TOK_POST_INC)
			rez--;
		else if(op == TOK_POST_DEC)
			rez++;
	}
	numptr_m1->val = rez;
	/* protect geting var value, is number now */
	numptr_m1->var = NULL;
	return 0;
err: return(-1);
}

/* longest must first */
static const char op_tokens[] = {
	'<','<','=',0, TOK_LSHIFT_ASSIGN,
	'>','>','=',0, TOK_RSHIFT_ASSIGN,
	'<','<',    0, TOK_LSHIFT,
	'>','>',    0, TOK_RSHIFT,
	'|','|',    0, TOK_OR,
	'&','&',    0, TOK_AND,
	'!','=',    0, TOK_NE,
	'<','=',    0, TOK_LE,
	'>','=',    0, TOK_GE,
	'=','=',    0, TOK_EQ,
	'|','=',    0, TOK_OR_ASSIGN,
	'&','=',    0, TOK_AND_ASSIGN,
	'*','=',    0, TOK_MUL_ASSIGN,
	'/','=',    0, TOK_DIV_ASSIGN,
	'%','=',    0, TOK_REM_ASSIGN,
	'+','=',    0, TOK_PLUS_ASSIGN,
	'-','=',    0, TOK_MINUS_ASSIGN,
	'-','-',    0, TOK_POST_DEC,
	'^','=',    0, TOK_XOR_ASSIGN,
	'+','+',    0, TOK_POST_INC,
	'*','*',    0, TOK_EXPONENT,
	'!',        0, TOK_NOT,
	'<',        0, TOK_LT,
	'>',        0, TOK_GT,
	'=',        0, TOK_ASSIGN,
	'|',        0, TOK_BOR,
	'&',        0, TOK_BAND,
	'*',        0, TOK_MUL,
	'/',        0, TOK_DIV,
	'%',        0, TOK_REM,
	'+',        0, TOK_ADD,
	'-',        0, TOK_SUB,
	'^',        0, TOK_BXOR,
	/* uniq */
	'~',        0, TOK_BNOT,
	',',        0, TOK_COMMA,
	'?',        0, TOK_CONDITIONAL,
	':',        0, TOK_CONDITIONAL_SEP,
	')',        0, TOK_RPAREN,
	'(',        0, TOK_LPAREN,
	0
};
/* ptr to ")" */
#define endexpression &op_tokens[sizeof(op_tokens)-7]


static arith_t arith (const char *expr, int *perrcode)
{
    register char arithval; /* Current character under analysis */
    operator lasttok, op;
    operator prec;

    const char *p = endexpression;
    int errcode;

    size_t datasizes = strlen(expr) + 2;

    /* Stack of integers */
    /* The proof that there can be no more than strlen(startbuf)/2+1 integers
     * in any given correct or incorrect expression is left as an exercise to
     * the reader. */
    v_n_t *numstack = alloca(((datasizes)/2)*sizeof(v_n_t)),
	    *numstackptr = numstack;
    /* Stack of operator tokens */
    operator *stack = alloca((datasizes) * sizeof(operator)),
	    *stackptr = stack;

    *stackptr++ = lasttok = TOK_LPAREN;     /* start off with a left paren */
    *perrcode = errcode = 0;

    while(1) {
	if ((arithval = *expr) == 0) {
		if (p == endexpression) {
			/* Null expression. */
			return 0;
		}

		/* This is only reached after all tokens have been extracted from the
		 * input stream. If there are still tokens on the operator stack, they
		 * are to be applied in order. At the end, there should be a final
		 * result on the integer stack */

		if (expr != endexpression + 1) {
			/* If we haven't done so already, */
			/* append a closing right paren */
			expr = endexpression;
			/* and let the loop process it. */
			continue;
		}
		/* At this point, we're done with the expression. */
		if (numstackptr != numstack+1) {
			/* ... but if there isn't, it's bad */
		  err:
			return (*perrcode = -1);
		}
		if(numstack->var) {
		    /* expression is $((var)) only, lookup now */
		    errcode = arith_lookup_val(numstack);
		}
	ret:
		*perrcode = errcode;
		return numstack->val;
	} else {
		/* Continue processing the expression. */
		if (arith_isspace(arithval)) {
			/* Skip whitespace */
			goto prologue;
		}
		if((p = endofname(expr)) != expr) {
			size_t var_name_size = (p-expr) + 1;  /* trailing zero */

			numstackptr->var = alloca(var_name_size);
			safe_strncpy(numstackptr->var, expr, var_name_size);
			expr = p;
		num:
			numstackptr->contidional_second_val_initialized = 0;
			numstackptr++;
			lasttok = TOK_NUM;
			continue;
		} else if (is_digit(arithval)) {
			numstackptr->var = NULL;
#ifdef CONFIG_ASH_MATH_SUPPORT_64
			numstackptr->val = strtoll(expr, (char **) &expr, 0);
#else
			numstackptr->val = strtol(expr, (char **) &expr, 0);
#endif
			goto num;
		}
		for(p = op_tokens; ; p++) {
			const char *o;

			if(*p == 0) {
				/* strange operator not found */
				goto err;
			}
			for(o = expr; *p && *o == *p; p++)
				o++;
			if(! *p) {
				/* found */
				expr = o - 1;
				break;
			}
			/* skip tail uncompared token */
			while(*p)
				p++;
			/* skip zero delim */
			p++;
		}
		op = p[1];

		/* post grammar: a++ reduce to num */
		if(lasttok == TOK_POST_INC || lasttok == TOK_POST_DEC)
		    lasttok = TOK_NUM;

		/* Plus and minus are binary (not unary) _only_ if the last
		 * token was as number, or a right paren (which pretends to be
		 * a number, since it evaluates to one). Think about it.
		 * It makes sense. */
		if (lasttok != TOK_NUM) {
			switch(op) {
				case TOK_ADD:
				    op = TOK_UPLUS;
				    break;
				case TOK_SUB:
				    op = TOK_UMINUS;
				    break;
				case TOK_POST_INC:
				    op = TOK_PRE_INC;
				    break;
				case TOK_POST_DEC:
				    op = TOK_PRE_DEC;
				    break;
			}
		}
		/* We don't want a unary operator to cause recursive descent on the
		 * stack, because there can be many in a row and it could cause an
		 * operator to be evaluated before its argument is pushed onto the
		 * integer stack. */
		/* But for binary operators, "apply" everything on the operator
		 * stack until we find an operator with a lesser priority than the
		 * one we have just extracted. */
		/* Left paren is given the lowest priority so it will never be
		 * "applied" in this way.
		 * if associativity is right and priority eq, applied also skip
		 */
		prec = PREC(op);
		if ((prec > 0 && prec < UNARYPREC) || prec == SPEC_PREC) {
			/* not left paren or unary */
			if (lasttok != TOK_NUM) {
				/* binary op must be preceded by a num */
				goto err;
			}
			while (stackptr != stack) {
			    if (op == TOK_RPAREN) {
				/* The algorithm employed here is simple: while we don't
				 * hit an open paren nor the bottom of the stack, pop
				 * tokens and apply them */
				if (stackptr[-1] == TOK_LPAREN) {
				    --stackptr;
				    /* Any operator directly after a */
				    lasttok = TOK_NUM;
				    /* close paren should consider itself binary */
				    goto prologue;
				}
			    } else {
				operator prev_prec = PREC(stackptr[-1]);

				convert_prec_is_assing(prec);
				convert_prec_is_assing(prev_prec);
				if (prev_prec < prec)
					break;
				/* check right assoc */
				if(prev_prec == prec && is_right_associativity(prec))
					break;
			    }
			    errcode = arith_apply(*--stackptr, numstack, &numstackptr);
			    if(errcode) goto ret;
			}
			if (op == TOK_RPAREN) {
				goto err;
			}
		}

		/* Push this operator to the stack and remember it. */
		*stackptr++ = lasttok = op;

	  prologue:
		++expr;
	}
    }
}
#endif /* CONFIG_ASH_MATH_SUPPORT */


#ifdef DEBUG
const char *bb_applet_name = "debug stuff usage";
int main(int argc, char **argv)
{
	return ash_main(argc, argv);
}
#endif

/*-
 * Copyright (c) 1989, 1991, 1993, 1994
 *      The Regents of the University of California.  All rights reserved.
 *
 * This code is derived from software contributed to Berkeley by
 * Kenneth Almquist.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the University nor the names of its contributors
 *    may be used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 */
