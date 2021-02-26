/* $Id: netbsd.h,v 1.1 2009-10-24 00:27:16 khorben Exp $ */
/* Copyright (c) 2009 Pierre Pronchery <khorben@defora.org> */
/* This file is part of DeforaOS Devel strace */
/* strace is not free software; you can redistribute it and/or modify it under
 * the terms of the Creative Commons Attribution-NonCommercial-ShareAlike 3.0
 * Unported as published by the Creative Commons organization.
 *
 * strace is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
 * A PARTICULAR PURPOSE.  See the Creative Commons Attribution-NonCommercial-
 * ShareAlike 3.0 Unported license for more details.
 *
 * You should have received a copy of the Creative Commons Attribution-
 * NonCommercial-ShareAlike 3.0 along with strace; if not, browse to
 * http://creativecommons.org/licenses/by-nc-sa/3.0/ */



#ifndef STRACE_NETBSD_H
# define STRACE_NETBSD_H

# ifdef __NetBSD__
#  include <sys/syscall.h>
#  include <machine/reg.h>


/* types */
typedef long ptrace_data_t; /* XXX really is int */
struct user
{
	struct reg regs;
};


/* constants */
#  define PTRACE_CONT		PT_CONTINUE
#  define PTRACE_GETREGS	PT_GETREGS
#  define PTRACE_SYSCALL	PT_SYSCALL
#  define PTRACE_TRACEME	PT_TRACE_ME

#  if defined(__amd64__)
#   define _REG32_EAX		11 /* XXX or #define _KERNEL */
#   define orig_eax		regs[_REG32_EAX]
#  elif defined(__i386__)
#   define orig_eax		r_eax
#  endif


/* variables */
extern char const * stracecall[SYS_getpid + 1];
# endif /* __NetBSD__ */

#endif /* !STRACE_NETBSD_H */
