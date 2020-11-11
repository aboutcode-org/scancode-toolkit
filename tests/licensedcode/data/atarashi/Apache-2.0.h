/***************************************************************
 *
 * Copyright (C) 1990-2007, Condor Team, Computer Sciences Department,
 * University of Wisconsin-Madison, WI.
 * 
 * Licensed under the Apache License, Version 2.0 (the "License"); you
 * may not use this file except in compliance with the License.  You may
 * obtain a copy of the License at
 * 
 *    http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 ***************************************************************/

#ifndef _CONDOR_BLKNG_FULL_DISK_IO_H
#define _CONDOR_BLKNG_FULL_DISK_IO_H

/* This file implements blocking read/write operations on a regular
	files only.  The main purpose is to read/write however many
	bytes you actually specified ans these functions will try very
	hard to do just that. */

BEGIN_C_DECLS

/* These functions are the actual implementation, and must be used if
	you want this functionality in the remote i/o or condor_checkpointing
	libraries. Be warned, however, that they do require libc to be mapped
	correctly. */
ssize_t _condor_full_read(int fd, void *ptr, size_t nbytes);
ssize_t _condor_full_write(int fd, const void *ptr, size_t nbytes);

/* For generic Condor code not in the above libraries, use these functions */
ssize_t full_read(int filedes, void *ptr, size_t nbyte);
ssize_t full_write(int filedes, const void *ptr, size_t nbyte);

END_C_DECLS

#endif
