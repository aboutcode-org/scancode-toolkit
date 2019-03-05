/* 
 * dlfcn.h --
 *
 *	This file provides a replacement for the header file "dlfcn.h"
 *	on systems where dlfcn.h is missing.  It's primary use is for
 *	AIX, where Tcl emulates the dl library.
 *
 *	This file is subject to the following copyright notice, which is
 *	different from the notice used elsewhere in Tcl but rougly
 *	equivalent in meaning.
 *
 *	Copyright (c) 1992,1993,1995,1996, Jens-Uwe Mager, Helios Software GmbH
 *	Not derived from licensed software.
 *
 *	Permission is granted to freely use, copy, modify, and redistribute
 *	this software, provided that the author is not construed to be liable
 *	for any results of using the software, alterations are clearly marked
 *	as such, and this notice is not modified.
 *
 * RCS: @(#) $Id: dlfcn.h,v 1.2 1998/09/14 18:39:44 stanton Exp $
 */

/*
 * @(#)dlfcn.h	1.4 revision of 95/04/25  09:36:52
 * This is an unpublished work copyright (c) 1992 HELIOS Software GmbH
 * 30159 Hannover, Germany
 */

#ifndef __dlfcn_h__
#define __dlfcn_h__

#ifndef _TCL
#include <tcl.h>
#endif

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Mode flags for the dlopen routine.
 */
#define RTLD_LAZY	1	/* lazy function call binding */
#define RTLD_NOW	2	/* immediate function call binding */
#define RTLD_GLOBAL	0x100	/* allow symbols to be global */

/*
 * To be able to intialize, a library may provide a dl_info structure
 * that contains functions to be called to initialize and terminate.
 */
struct dl_info {
	void (*init) _ANSI_ARGS_((void));
	void (*fini) _ANSI_ARGS_((void));
};

VOID *dlopen _ANSI_ARGS_((const char *path, int mode));
VOID *dlsym _ANSI_ARGS_((void *handle, const char *symbol));
char *dlerror _ANSI_ARGS_((void));
int dlclose _ANSI_ARGS_((void *handle));

#ifdef __cplusplus
}
#endif

#endif /* __dlfcn_h__ */
