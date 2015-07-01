// stacktrace.cpp:  adapted heavily from lhn/cluster/censemble/infr/stacktrace.c
#include "stacktrace.h"

#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <signal.h>
#include <sys/wait.h>

#include <execinfo.h>

#include "lhn_defines.h"

typedef char *string_t ;

// these aren't normally defined for C++
#ifndef __PRIPTR_PREFIX
# if __WORDSIZE == 64
#  define __PRIPTR_PREFIX	"l"
# else
#  define __PRIPTR_PREFIX
# endif
#endif

uint32_t string_length(
	string_t const s
) {
    return strlen(s) ;
}

string_t string_copy(
	string_t const s
) {
    uint32_t const len = string_length(s) + 1 ;
    string_t t = (char *)malloc(len) ;
    memcpy(t, s, len) ;
    return t ;
}

void string_free(
	string_t const s
) {
    free(s) ;
}

typedef struct libmap {
	uintptr_t start ;
	uintptr_t end ;
	string_t path ;
} *map_t ;
static map_t map ;
static int32_t nmaps ;

// This may only work on Linux
static int
readmaps(map_t map, const uint32_t maxmaps)
{
    char mapfile[1024] ;
    FILE *mf ;
    char line[256] ;
    char *start ;
    char *end ;
    char *mode ;
    char *path ;
    char *c ;
    uint32_t entries = 0 ;

    sprintf(mapfile, "/proc/%d/maps", getpid()) ;
    if ((mf = fopen(mapfile, "ro")) == NULL) {
	   return 0 ;
    }

    while (fgets(line, 256, mf)) {
        c = line ;
        start = c ;
        while (*c != '-') {
            c++ ;
        }
	*c++ = '\0' ;
	end = c ;
        while (*c != ' ') {
            c++ ;
        }
	*c++ = '\0' ;
	mode = c ;
        while (*c != ' ') {
            c++ ;
        }
	*c++ = '\0' ;
	if (mode[0] != 'r' || mode[1] != '-' || mode[2] != 'x' || mode[3] != 'p') {
	    continue ;
	}
        while (*c != '/') {
            c++ ;
        }
	path = c ;
        while (*c != '\n' && *c != ' ') {
            c++ ;
        }
	*c = '\0' ;

	if (sscanf(start, "%" __PRIPTR_PREFIX "x", &map[entries].start) != 1) {
	    continue ;
	}
	if (sscanf(end, "%" __PRIPTR_PREFIX "x", &map[entries].end) != 1) {
	    continue ;
	}
	map[entries].path = string_copy((string_t)path) ;
	entries++ ;
	if (entries == maxmaps) {
	    break ;
	}
    }

    fclose(mf) ;
    return entries ;
}

// For stripped libraries, these next two define a hack will allow tracing to work
#define SIGACTION_LIBC_OFFSET 0x2e868
#define LHN_LIBC_NAME "/lib/libc-2.2.4.so"
static
int addr2line_obj_dump(
	struct pcset *basepc,
	struct pcset *sigpc,
	struct pcset *syssigpc,
	char *info
) {
    char exec[1024] ;
    char file[1024] ;
    char func[1024] ;
    uintptr_t offset ;
    FILE *ap ;
    char *slashptr ;

    offset = (uintptr_t)basepc->pc - basepc->start ;
    if (basepc->obj) {
	sprintf(exec, "/usr/bin/addr2line --functions -C -e %s 0x%" __PRIPTR_PREFIX "x", basepc->obj, offset) ;
    }
    else {
	sprintf(exec, "/usr/bin/addr2line --functions -C -e /proc/%d/exe 0x%" __PRIPTR_PREFIX "x", getpid(), offset) ;
    }

    ap = popen(exec, "r") ;
    fgets(func, sizeof(func), ap) ;
    fgets(file, sizeof(file), ap) ;
    fclose(ap) ;

    if (strchr(func, '\n')) {
	*strchr(func, '\n') = 0 ;
    }

    if (strchr(file, '\n')) {
	*strchr(file, '\n') = 0 ;
    }

    // Some RedHat Libraries don't do the offset thing
    if (!strcmp(file, "??:0") && !strcmp(func, "??")) {
	if (basepc->obj) {
	    sprintf(exec, "/usr/bin/addr2line --functions -C -e %s 0x%" __PRIPTR_PREFIX "x", basepc->obj, (uintptr_t)basepc->pc) ;
	}
	else {
	    sprintf(exec, "/usr/bin/addr2line --functions -C -e /proc/%d/exe 0x%" __PRIPTR_PREFIX "x", getpid(), (uintptr_t)basepc->pc) ;
	}

	ap = popen(exec, "r") ;
	fgets(func, sizeof(func), ap) ;
	fgets(file, sizeof(file), ap) ;
	fclose(ap) ;

	if (strchr(func, '\n')) {
	    *strchr(func, '\n') = 0 ;
	}

	if (strchr(file, '\n')) {
	    *strchr(file, '\n') = 0 ;
	}
    }

    slashptr = strrchr(file, '/') ;
    if (((slashptr && !strcmp(++slashptr, "sigaction.c:149"))
	// LHN hack for gcc 3.0.1 libraries which were stripped
        || ((offset == SIGACTION_LIBC_OFFSET) && !strcmp(basepc->obj, LHN_LIBC_NAME))
	// RedHat libpthread signal hander
	|| (!strcmp(func, "__pthread_sighandler"))
	// RedHat Libraries Signal Trampoline Code
	|| (!strcmp(func, "__restore")))
	&& sigpc && sigpc->pc) {
	if (!addr2line_obj_dump(sigpc, NULL, NULL, info) && syssigpc && syssigpc->pc) {
	    (void)addr2line_obj_dump(syssigpc, NULL, NULL, info) ;
	    basepc->pc = syssigpc->pc ;
	}
	else {
	    basepc->pc = sigpc->pc ;
	}
    }
    else {
	sprintf(info, "%s %s", file, func) ;
    }

    if (!strcmp(info, "??:0 ??")) {
	return 0 ;
    } else {
	return 1 ;
    }
}

void stacktrace_dump(stacktrace_t *s) {
    unsigned i ;
    char info[1024] ;
    bool foundinfo ;
    struct pcset pcs ;
    
    // If can't find this function, then all the symbols were probably stripped.
    memset(&pcs, 0, sizeof(pcs)) ;
    pcs.pc = (void *)stacktrace_dump ;
    if (!addr2line_obj_dump(&pcs, NULL, NULL, info)) {
	return ;
    }

    LHN_PRINT(0,0,"STACKTRACE:dump\n")
    for (i=0; i<STACKTRACE_NITEMS; i++) {
	foundinfo = true ;
	if (!s->basepc[i].pc) {
	    break ;
	}

	if (!addr2line_obj_dump(&s->basepc[i], &s->sigpc[i], &s->syssigpc[i], info)) {
	    foundinfo = false ;
	}

	if (foundinfo) {
	    LHN_PRINT(0,0,"  frame=%02d pc=0x%0*" __PRIPTR_PREFIX "x %s\n", i, (int)sizeof(uintptr_t)*2, (uintptr_t)s->basepc[i].pc, info) ;
	}
	else {
	    LHN_PRINT(0,0,"  frame=%02d pc=0x%0*" __PRIPTR_PREFIX "x unknown\n", i, (int)sizeof(uintptr_t)*2, (uintptr_t)s->basepc[i].pc) ;
	}
    }
}

void stacktrace_close(void) {
    int i ;
    if (map) {
	for (i=0; i<nmaps; i++) {
	    if (map[i].path) {
		string_free(map[i].path) ;
		map[i].path = NULL ;
	    }
	}
        free(map) ;
	map = NULL ;
    }
}

// In theory this code could be made to work without EXECINFO.

// This tracing code that follows was adapted from the following, but
// modified almost beyond any recognition of the original source.  The
// main purpose was to find a way to trace through signal frames.
//
// backtrace.c -- 
// Created: Sun Feb  9 10:06:01 2003 by faith@dict.org
// Copyright 2003, 2004 Rickard E. Faith (faith@dict.org)
//  
// Permission is hereby granted, free of charge, to any person obtaining a
// copy of this software and associated documentation files (the "Software"),
// to deal in the Software without restriction, including without limitation
// the rights to use, copy, modify, merge, publish, distribute, sublicense,
// and/or sell copies of the Software, and to permit persons to whom the
// Software is furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included
// in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
// THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
// OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
// ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
// OTHER DEALINGS IN THE SOFTWARE.
//  
// $Id: stacktrace.c 16423 2007-09-29 03:36:09Z jlilienk $

// EIP in sigaction frame is this offset from fp
#define EIP_IN_SIGNAL_FRAME 17
// EIP in sigaction frame is this offset from fp when interrupting a system call
#define EIP_IN_SYSTEM_SIGNAL_FRAME 189

#define H(X)                                                                \
    do {                                                                    \
        if (!count) {                                                       \
            if (!(frame[X+1] = __builtin_frame_address(X))) count = X ;     \
        }                                                                   \
    } while (0)

#define GETFRAMES(max)                                                      \
    do {                                                                    \
        int i = 0 ;                                                         \
        memset(frame, 0, sizeof(frame)) ;                                   \
        while(++i < max) {                                                  \
            switch (i) {                                                    \
                case 0:  H(0);  break ;                                     \
                case 1:  H(1);  break ;                                     \
                case 2:  H(2);  break ;                                     \
                case 3:  H(3);  break ;                                     \
                case 4:  H(4);  break ;                                     \
                case 5:  H(5);  break ;                                     \
                case 6:  H(6);  break ;                                     \
                case 7:  H(7);  break ;                                     \
                case 8:  H(8);  break ;                                     \
                case 9:  H(9);  break ;                                     \
                case 10: H(10); break ;                                     \
                case 11: H(11); break ;                                     \
                case 12: H(12); break ;                                     \
                case 13: H(13); break ;                                     \
                case 14: H(14); break ;                                     \
                case 15: H(15); break ;                                     \
                case 16: H(16); break ;                                     \
                case 17: H(17); break ;                                     \
                case 18: H(18); break ;                                     \
                case 19: H(19); break ;                                     \
                case 20: H(20); break ;                                     \
                case 21: H(21); break ;                                     \
                case 22: H(22); break ;                                     \
                case 23: H(23); break ;                                     \
                case 24: H(24); break ;                                     \
                case 25: H(25); break ;                                     \
                case 26: H(26); break ;                                     \
                case 27: H(27); break ;                                     \
                case 28: H(28); break ;                                     \
                case 29: H(29); break ;                                     \
                case 30: H(30); break ;                                     \
                case 31: H(31); break ;                                     \
                default: break ;                                            \
            }                                                               \
        }                                                                   \
    } while (0)

void stacktrace_get(stacktrace_t *s)
{
    int         bcount = 0 ;
    int         count = 0 ;
    void        *addr[STACKTRACE_NITEMS] ;
    void        *frame[STACKTRACE_NITEMS+1] ;
    int         framecount ;
    int         mapidx ;
    int         amapidx ;

    memset(s->basepc, 0, STACKTRACE_NITEMS*sizeof(struct pcset)) ;
    memset(s->sigpc, 0, STACKTRACE_NITEMS*sizeof(struct pcset)) ;

    bcount = backtrace(addr, STACKTRACE_NITEMS) ;
    GETFRAMES(STACKTRACE_NITEMS) ;
    if (!count) {
        count = STACKTRACE_NITEMS ;
    }
    else {
	count = (count >= STACKTRACE_NITEMS) ? STACKTRACE_NITEMS : (count+1) ;
    }

    // been here before; only for some debugging things
    if (!map) {
	map = (map_t)malloc(sizeof(map[0]) * STACKTRACE_NMAPS) ;
    }

    memset(map, 0, sizeof(*map)*STACKTRACE_NMAPS) ;
    nmaps = readmaps(map, STACKTRACE_NMAPS) ;

    for (framecount = 0; framecount<count; framecount++) {
	s->basepc[framecount].pc = addr[framecount] ;
	for (mapidx = 0; mapidx < nmaps; mapidx++) {
	    if (((uintptr_t)s->basepc[framecount].pc >= map[mapidx].start)
	     && ((uintptr_t)s->basepc[framecount].pc <= map[mapidx].end)) {
		s->basepc[framecount].obj = (char *)map[mapidx].path ;
		s->basepc[framecount].start = map[mapidx].start ;

		if (!frame[framecount])
		    break ;

		void **vvp = (void **)frame[framecount] ;
		void *vp = *vvp ;
		int limit = ((uintptr_t)vp - (uintptr_t)vvp) / 4 ;

		if (limit < 190 || !vp)
		    break ;

		// If a signal comes during executing code, the application return address is here
		s->sigpc[framecount].pc = *(void **)((uintptr_t)frame[framecount]+(EIP_IN_SIGNAL_FRAME*sizeof(void *))) ;
		for (amapidx = 0 ; amapidx < nmaps ; amapidx++) {
		    if (((uintptr_t)s->sigpc[framecount].pc >= map[amapidx].start)
		     && ((uintptr_t)s->sigpc[framecount].pc <= map[amapidx].end)) {
			s->sigpc[framecount].obj = (char *)map[amapidx].path ;
			s->sigpc[framecount].start = map[amapidx].start ;
			break ;
		    }
		}

		// If a signal comes during a blocking system call, the application return address is in a different place
		s->syssigpc[framecount].pc = *(void **)((uintptr_t)frame[framecount]+(EIP_IN_SYSTEM_SIGNAL_FRAME*sizeof(void *))) ;
		for (amapidx = 0 ; amapidx < nmaps ; amapidx++) {
		    if (((uintptr_t)s->syssigpc[framecount].pc >= map[amapidx].start)
		     && ((uintptr_t)s->syssigpc[framecount].pc <= map[amapidx].end)) {
			s->syssigpc[framecount].obj = (char *)map[amapidx].path ;
			s->syssigpc[framecount].start = map[amapidx].start ;
			break ;
		    }
		}
		break ;
	    }
	}
    }
}
