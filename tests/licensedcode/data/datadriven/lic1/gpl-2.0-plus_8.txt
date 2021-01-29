/*
 * Rexec program for system have fork() as vfork() with foregound option
 *
 * Copyright (C) Vladimir N. Oleynik <dzo@simtreas.ru>
 * Copyright (C) 2003 Russ Dill <Russ.Dill@asu.edu>
 *
 * daemon() portion taken from uclibc:
 *
 * Copyright (c) 1991, 1993
 *      The Regents of the University of California.  All rights reserved.
 *
 * Modified for uClibc by Erik Andersen <andersee@debian.org>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 */

#include <unistd.h>
#include <stdio.h>
#include <fcntl.h>
#include <paths.h>
#include "libbb.h"


#if defined(__uClinux__)
void vfork_daemon_rexec(int nochdir, int noclose,
		int argc, char **argv, char *foreground_opt)
{
	int fd;
	char **vfork_args;
	int a = 0;

	setsid();

	if (!nochdir)
		chdir("/");

	if (!noclose && (fd = open(_PATH_DEVNULL, O_RDWR, 0)) != -1) {
		dup2(fd, STDIN_FILENO);
		dup2(fd, STDOUT_FILENO);
		dup2(fd, STDERR_FILENO);
		if (fd > 2)
			close(fd);
	}

	vfork_args = xcalloc(sizeof(char *), argc + 3);
	vfork_args[a++] = "/bin/busybox";
	while(*argv) {
	    vfork_args[a++] = *argv;
	    argv++;
	}
	vfork_args[a] = foreground_opt;
	switch (vfork()) {
	case 0: /* child */
		/* Make certain we are not a session leader, or else we
		 * might reacquire a controlling terminal */
		if (vfork())
			_exit(0);
		execv(vfork_args[0], vfork_args);
		bb_perror_msg_and_die("execv %s", vfork_args[0]);
	case -1: /* error */
		bb_perror_msg_and_die("vfork");
	default: /* parent */
		exit(0);
	}
}
#endif /* uClinux */
