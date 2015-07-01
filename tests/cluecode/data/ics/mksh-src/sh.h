/*	$OpenBSD: tty.h,v 1.5 2004/12/20 11:34:26 otto Exp $	*/

/*-
 * Copyright (c) 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010
 *	Thorsten Glaser <tg@mirbsd.org>
 *
 * Provided that these terms and disclaimer and all copyright notices
 * are retained or reproduced in an accompanying document, permission
 * is granted to deal in this work without restriction, including un-
    defined(__ELF__) && defined(__GNUC__) && \
    !defined(__llvm__) && !defined(__NWCC__)
/*
 * We got usable __IDSTRING __COPYRIGHT __RCSID __SCCSID macros
 * which work for all cases; no need to redefine them using the
 * "portable" macros from below when we might have the "better"
#undef __IDSTRING
#undef __IDSTRING_CONCAT
#undef __IDSTRING_EXPAND
#undef __COPYRIGHT
#undef __RCSID
#undef __SCCSID
#define __IDSTRING(prefix, string)				\
	static const char __IDSTRING_EXPAND(__LINE__,prefix) []	\
	    MKSH_A_USED = "@(""#)" #prefix ": " string
#define __COPYRIGHT(x)		__IDSTRING(copyright,x)
#define __RCSID(x)		__IDSTRING(rcsid,x)
#define __SCCSID(x)		__IDSTRING(sccsid,x)
	} while (/* CONSTCOND */ 0)
#endif

#define ksh_isdigit(c)	(((c) >= '0') && ((c) <= '9'))
#define ksh_islower(c)	(((c) >= 'a') && ((c) <= 'z'))
#define ksh_isupper(c)	(((c) >= 'A') && ((c) <= 'Z'))
#define ksh_tolower(c)	(((c) >= 'A') && ((c) <= 'Z') ? (c) - 'A' + 'a' : (c))
#define ksh_toupper(c)	(((c) >= 'a') && ((c) <= 'z') ? (c) - 'a' + 'A' : (c))
#define ksh_isdash(s)	(((s) != NULL) && ((s)[0] == '-') && ((s)[1] == '\0'))
#define ksh_isspace(c)	((((c) >= 0x09) && ((c) <= 0x0D)) || ((c) == 0x20))

#ifdef NO_PATH_MAX
 * portability problems (calling strchr(x, 0x80|'x') is error prone).
 */
#define MAGIC		(7)	/* prefix for *?[!{,} during expand */
#define ISMAGIC(c)	((unsigned char)(c) == MAGIC)
#define NOT		'!'	/* might use ^ (ie, [!...] vs [^..]) */

	union mksh_cchack in, out;	\
					\
	in.ro = (s);			\
	out.rw = ucstrchr(in.rw, (c));	\
	(out.ro);			\
})
	out.rw = ucstrstr(in.rw, (l));	\
	(out.ro);			\
})
#define vstrchr(s,c)	(cstrchr((s), (c)) != NULL)
#define vstrstr(b,l)	(cstrstr((b), (l)) != NULL)
#define mkssert(e)	((e) ? (void)0 : exit(255))
#else /* !DEBUG, !gcc */
#define cstrchr(s,c)	((const char *)strchr((s), (c)))
#define cstrstr(s,c)	((const char *)strstr((s), (c)))
#define vstrchr(s,c)	(strchr((s), (c)) != NULL)
#define vstrstr(b,l)	(strstr((b), (l)) != NULL)
#define mkssert(e)	((void)0)
extern unsigned char chtypes[];

#define ctype(c, t)	!!( ((t) == C_SUBOP2) ?				\
			    (((c) == '#' || (c) == '%') ? 1 : 0) :	\
			    (chtypes[(unsigned char)(c)]&(t)) )
#define ksh_isalphx(c)	ctype((c), C_ALPHA)
#define ksh_isalnux(c)	ctype((c), C_ALPHA | C_DIGIT)

EXTERN int ifs0 I__(' ');	/* for "$*" */
				    (shf)->rnleft--, *(shf)->rp++ : \
				    shf_getchar(shf))
#define shf_putc(c, shf)	((shf)->wnleft == 0 ? \
				    shf_putchar((c), (shf)) : \
				    ((shf)->wnleft--, *(shf)->wp++ = (c)))
#endif
#define shf_eof(shf)		((shf)->flags & SHF_EOF)
} while (/* CONSTCOND */ 0)

/* stuff char into string */
#define Xput(xs, xp, c)	(*xp++ = (c))

/* check if there are at least n bytes left */