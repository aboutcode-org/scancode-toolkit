/*
 * grent.c - This file is part of the libc-8086/grp package for ELKS,
 * Copyright (C) 1995, 1996 Nat Friedman <ndf@linux.mit.edu>.
 *
 *  This library is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU Library General Public
 *  License as published by the Free Software Foundation; either
 *  version 2 of the License, or (at your option) any later version.
 *
 *  This library is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 *  Library General Public License for more details.
 *
 *  You should have received a copy of the GNU Library General Public
 *  License along with this library; if not, write to the Free
 *  Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 *
 */

/*
 * setgrent(), endgrent(), and getgrent() are mutually-dependent functions,
 * so they are all included in the same object file, and thus all linked
 * in together.
 */

#include "busybox.h"

#include <unistd.h>
#include <fcntl.h>
#include "grp_.h"

static int grp_fd = -1;

void setgrent(void)
{
	if (grp_fd != -1)
		close(grp_fd);
	grp_fd = open(bb_path_group_file, O_RDONLY);
}

void endgrent(void)
{
	if (grp_fd != -1)
		close(grp_fd);
	grp_fd = -1;
}

struct group *getgrent(void)
{
	if (grp_fd == -1)
		return NULL;
	return bb_getgrent(grp_fd);
}
