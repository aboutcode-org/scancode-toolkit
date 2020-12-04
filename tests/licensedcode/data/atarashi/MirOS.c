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
