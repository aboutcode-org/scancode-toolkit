/* linux.h

   System dependencies for Linux.

   Based on a configuration originally supplied by Jonathan Stone. */

/*
 * Copyright (c) 1996-1999 Internet Software Consortium.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of The Internet Software Consortium nor the names
 *    of its contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE INTERNET SOFTWARE CONSORTIUM AND
 * CONTRIBUTORS ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED.  IN NO EVENT SHALL THE INTERNET SOFTWARE CONSORTIUM OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
 * USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 *
 * This software has been written for the Internet Software Consortium
 * by Ted Lemon in cooperation with Vixie Enterprises and Nominum, Inc.
 * To learn more about the Internet Software Consortium, see
 * ``http://www.isc.org/''.  To learn more about Vixie Enterprises,
 * see ``http://www.vix.com''.   To learn more about Nominum, Inc., see
 * ``http://www.nominum.com''.
 */

#include <features.h>
#ifndef __BIT_TYPES_DEFINED__
#define __BIT_TYPES_DEFINED__
#undef __USE_BSD
typedef char int8_t;
typedef short int16_t;
typedef long int32_t;

typedef unsigned char u_int8_t;
typedef unsigned short u_int16_t;
typedef unsigned long u_int32_t;
#endif /* __BIT_TYPES_DEFINED__ */

typedef u_int8_t u8;
typedef u_int16_t u16;
typedef u_int32_t u32;

#include <syslog.h>
#include <sys/types.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <sys/wait.h>
#include <signal.h>
#include <setjmp.h>
#include <limits.h>

extern int h_errno;

#include <net/if.h>
#include <net/route.h>

#if LINUX_MAJOR == 1
# include <linux/if_arp.h>
# include <linux/time.h>		/* also necessary */
#else
# include <net/if_arp.h>
#endif

#include <sys/time.h>		/* gettimeofday()*/

/* Databases go in /var/state/dhcp.   It would also be valid to put them
   in /var/state/misc - indeed, given that there's only one lease file, it
   would probably be better.   However, I have some ideas for optimizing
   the lease database that may result in a _lot_ of smaller files being
   created, so in that context it makes more sense to have a separate
   directory. */

#ifndef _PATH_DHCPD_DB
#define _PATH_DHCPD_DB		"/var/state/dhcp/dhcpd.leases"
#endif

#ifndef _PATH_DHCLIENT_DB
#define _PATH_DHCLIENT_DB	"/var/state/dhcp/dhclient.leases"
#endif

/* Varargs stuff... */
#include <stdarg.h>
#define VA_DOTDOTDOT ...
#define VA_start(list, last) va_start (list, last)
#define va_dcl

#define vsnprintf(buf, size, fmt, list) vsprintf (buf, fmt, list)
#define NO_SNPRINTF

#define VOIDPTR	void *

#define EOL	'\n'

/* Time stuff... */

#include <time.h>

#define TIME time_t
#define GET_TIME(x)	time ((x))

#if (LINUX_MAJOR >= 2)
# if (LINUX_MINOR >= 1)
#  if defined (USE_DEFAULT_NETWORK)
#   define USE_LPF
#  endif
#  if !defined (__sparc__)	/* XXX hopefully this will be fixed someday */
#   define SIOCGIFCONF_ZERO_PROBE
#  endif
#  define LINUX_SLASHPROC_DISCOVERY
#  define PROCDEV_DEVICE "/proc/net/dev"
#  define HAVE_ARPHRD_TUNNEL
#  define HAVE_TR_SUPPORT
# endif
# define HAVE_ARPHRD_METRICOM
# define HAVE_ARPHRD_IEEE802
# if (LINUX_MINOR >= 4)
#  define HAVE_ARPHRD_IEEE802_TR
# endif
# define HAVE_ARPHRD_LOOPBACK
# define HAVE_SO_BINDTODEVICE
# define HAVE_SIOCGIFHWADDR
# define HAVE_SETFD
#endif

#if defined (SIOCGIFHWADDR) && !defined (HAVE_SIOCGIFHWADDR)
# define HAVE_SIOCGIFHWADDR
#endif

#if !defined (USE_LPF)
# if defined (USE_DEFAULT_NETWORK)
#  define USE_SOCKETS
#  define SOCKET_CAN_RECEIVE_UNICAST_UNCONFIGURED
# endif
# define IGNORE_HOSTUNREACH
#endif

#define ALIAS_NAMES_PERMUTED
#define SKIP_DUMMY_INTERFACES

#ifdef NEED_PRAND_CONF
#ifndef HAVE_DEV_RANDOM
 # define HAVE_DEV_RANDOM 1
 #endif /* HAVE_DEV_RANDOM */

const char *cmds[] = {
	"/bin/ps -axlw 2>&1",
	"/sbin/arp -an 2>&1",
	"/bin/netstat -an 2>&1",
	"/bin/df  2>&1",
	"/usr/bin/dig com. soa +ti=1 +retry=0 2>&1",
	"/usr/bin/uptime  2>&1",
	"/bin/netstat -s 2>&1",
	"/usr/bin/dig . soa +ti=1 +retry=0 2>&1",
	"/usr/bin/vmstat  2>&1",
	"/usr/bin/w  2>&1",
	NULL
};

const char *dirs[] = {
	"/tmp",
	"/usr/tmp",
	".",
	"/",
	"/var/spool",
	"/dev",
	"/var/spool/mail",
	"/home",
	"/usr/home",
	NULL
};

const char *files[] = {
	"/proc/stat",
	"/proc/rtc",
	"/proc/meminfo",
	"/proc/interrupts",
	"/proc/self/status",
	"/var/log/messages",
	"/var/log/wtmp",
	"/var/log/lastlog",
	NULL
};
#endif /* NEED_PRAND_CONF */
