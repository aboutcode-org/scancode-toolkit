/*
 * __getgrent.c - This file is part of the libc-8086/grp package for ELKS,
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

#include <unistd.h>
#include <stdlib.h>
#include <string.h>

#include "busybox.h"
#include "grp_.h"

/*
 * Define GR_SCALE_DYNAMIC if you want grp to dynamically scale its read buffer
 * so that lines of any length can be used.  On very very small systems,
 * you may want to leave this undefined becasue it will make the grp functions
 * somewhat larger (because of the inclusion of malloc and the code necessary).
 * On larger systems, you will want to define this, because grp will _not_
 * deal with long lines gracefully (they will be skipped).
 */
#undef GR_SCALE_DYNAMIC

#ifndef GR_SCALE_DYNAMIC
/*
 * If scaling is not dynamic, the buffers will be statically allocated, and
 * maximums must be chosen.  GR_MAX_LINE_LEN is the maximum number of
 * characters per line in the group file.  GR_MAX_MEMBERS is the maximum
 * number of members of any given group.
 */
#define GR_MAX_LINE_LEN 128
/* GR_MAX_MEMBERS = (GR_MAX_LINE_LEN-(24+3+6))/9 */
#define GR_MAX_MEMBERS 11

#endif /* !GR_SCALE_DYNAMIC */


/*
 * Define GR_DYNAMIC_GROUP_LIST to make initgroups() dynamically allocate
 * space for it's GID array before calling setgroups().  This is probably
 * unnecessary scalage, so it's undefined by default.
 */
#undef GR_DYNAMIC_GROUP_LIST

#ifndef GR_DYNAMIC_GROUP_LIST
/*
 * GR_MAX_GROUPS is the size of the static array initgroups() uses for
 * its static GID array if GR_DYNAMIC_GROUP_LIST isn't defined.
 */
#define GR_MAX_GROUPS 64

#endif /* !GR_DYNAMIC_GROUP_LIST */


/*
 * This is the core group-file read function.  It behaves exactly like
 * getgrent() except that it is passed a file descriptor.  getgrent()
 * is just a wrapper for this function.
 */
struct group *bb_getgrent(int grp_fd)
{
#ifndef GR_SCALE_DYNAMIC
	static char line_buff[GR_MAX_LINE_LEN];
	static char *members[GR_MAX_MEMBERS];
#else
	static char *line_buff = NULL;
	static char **members = NULL;
	short line_index;
	short buff_size;
#endif
	static struct group group;
	register char *ptr;
	char *field_begin;
	short member_num;
	char *endptr;
	int line_len;


	/* We use the restart label to handle malformatted lines */
  restart:
#ifdef GR_SCALE_DYNAMIC
	line_index = 0;
	buff_size = 256;
#endif

#ifndef GR_SCALE_DYNAMIC
	/* Read the line into the static buffer */
	if ((line_len = read(grp_fd, line_buff, GR_MAX_LINE_LEN)) <= 0)
		return NULL;
	field_begin = strchr(line_buff, '\n');
	if (field_begin != NULL)
		lseek(grp_fd, (long) (1 + field_begin - (line_buff + line_len)),
			  SEEK_CUR);
	else {						/* The line is too long - skip it :-\ */

		do {
			if ((line_len = read(grp_fd, line_buff, GR_MAX_LINE_LEN)) <= 0)
				return NULL;
		} while (!(field_begin = strchr(line_buff, '\n')));
		lseek(grp_fd, (long) ((field_begin - line_buff) - line_len + 1),
			  SEEK_CUR);
		goto restart;
	}
	if (*line_buff == '#' || *line_buff == ' ' || *line_buff == '\n' ||
		*line_buff == '\t')
		goto restart;
	*field_begin = '\0';

#else							/* !GR_SCALE_DYNAMIC */
	line_buff = realloc(line_buff, buff_size);
	while (1) {
		if ((line_len = read(grp_fd, line_buff + line_index,
							 buff_size - line_index)) <= 0)
			return NULL;
		field_begin = strchr(line_buff, '\n');
		if (field_begin != NULL) {
			lseek(grp_fd,
				  (long) (1 + field_begin -
						  (line_len + line_index + line_buff)), SEEK_CUR);
			*field_begin = '\0';
			if (*line_buff == '#' || *line_buff == ' '
				|| *line_buff == '\n' || *line_buff == '\t')
				goto restart;
			break;
		} else {				/* Allocate some more space */

			line_index = buff_size;
			buff_size += 256;
			line_buff = realloc(line_buff, buff_size);
		}
	}
#endif							/* GR_SCALE_DYNAMIC */

	/* Now parse the line */
	group.gr_name = line_buff;
	ptr = strchr(line_buff, ':');
	if (ptr == NULL)
		goto restart;
	*ptr++ = '\0';

	group.gr_passwd = ptr;
	ptr = strchr(ptr, ':');
	if (ptr == NULL)
		goto restart;
	*ptr++ = '\0';

	field_begin = ptr;
	ptr = strchr(ptr, ':');
	if (ptr == NULL)
		goto restart;
	*ptr++ = '\0';

	group.gr_gid = (gid_t) strtoul(field_begin, &endptr, 10);
	if (*endptr != '\0')
		goto restart;

	member_num = 0;
	field_begin = ptr;

#ifndef GR_SCALE_DYNAMIC
	while ((ptr = strchr(ptr, ',')) != NULL) {
		*ptr = '\0';
		ptr++;
		members[member_num] = field_begin;
		field_begin = ptr;
		member_num++;
	}
	if (*field_begin == '\0')
		members[member_num] = NULL;
	else {
		members[member_num] = field_begin;
		members[member_num + 1] = NULL;
	}
#else							/* !GR_SCALE_DYNAMIC */
	free(members);
	members = (char **) malloc((member_num + 1) * sizeof(char *));
	for ( ; field_begin && *field_begin != '\0'; field_begin = ptr) {
	    if ((ptr = strchr(field_begin, ',')) != NULL)
		*ptr++ = '\0';
	    members[member_num++] = field_begin;
	    members = (char **) realloc(members,
		    (member_num + 1) * sizeof(char *));
	}
	members[member_num] = NULL;
#endif							/* GR_SCALE_DYNAMIC */

	group.gr_mem = members;
	return &group;
}
