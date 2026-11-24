/*
 * utils.h
 *
 * Copyright (C) 2009 Hector Martin <hector@marcansoft.com>
 * Copyright (C) 2009 Nikias Bassen <nikias@gmx.li>
 *
 * This library is free software; you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation, either version 2.1 of the
 * License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * SPDX-License-Identifier: LGPL-2.1-or-later
 */

#ifndef UTILS_H
#define UTILS_H

#include <poll.h>
#include <plist/plist.h>

enum fdowner {
	FD_LISTEN,
	FD_CLIENT,
	FD_USB
};

struct fdlist {
	int count;
	int capacity;
	enum fdowner *owners;
	struct pollfd *fds;
};

void fdlist_create(struct fdlist *list);
void fdlist_add(struct fdlist *list, enum fdowner owner, int fd, short events);
void fdlist_free(struct fdlist *list);
void fdlist_reset(struct fdlist *list);

uint64_t mstime64(void);
void get_tick_count(struct timeval * tv);

#endif
