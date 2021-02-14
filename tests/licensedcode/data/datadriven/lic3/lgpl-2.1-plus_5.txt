/* Copyright (C) 1991,92,95,96,97,98,99,2001 Free Software Foundation, Inc.
   This file is part of the GNU C Library.

   The GNU C Library is free software; you can redistribute it and/or
   modify it under the terms of the GNU Lesser General Public
   License as published by the Free Software Foundation; either
   version 2.1 of the License, or (at your option) any later version.

   The GNU C Library is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
   Lesser General Public License for more details.

   You should have received a copy of the GNU Lesser General Public
   License along with the GNU C Library; if not, write to the Free
   Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
   02111-1307 USA.  */

/*
 *	POSIX Standard: 9.2.2 User Database Access	<pwd.h>
 */

#if !defined CONFIG_USE_BB_PWD_GRP
#include <pwd.h>

#else

#ifndef	_PWD_H
#define	_PWD_H	1

#include <sys/types.h>
#include <features.h>
#include <stdio.h>

/* The passwd structure.  */
struct passwd
{
    char *pw_name;		/* Username.  */
    char *pw_passwd;		/* Password.  */
    uid_t pw_uid;			/* User ID.  */
    gid_t pw_gid;			/* Group ID.  */
    char *pw_gecos;		/* Real name.  */
    char *pw_dir;			/* Home directory.  */
    char *pw_shell;		/* Shell program.  */
};


/* Rewind the password-file stream.  */
extern void setpwent (void);

/* Close the password-file stream.  */
extern void endpwent (void);

/* Read an entry from the password-file stream, opening it if necessary.  */
extern struct passwd *getpwent (void);

/* Read an entry from STREAM.  */
extern struct passwd *fgetpwent (FILE *__stream);

/* Write the given entry onto the given stream.  */
extern int putpwent (__const struct passwd *__restrict __p,
		     FILE *__restrict __f);

/* Search for an entry with a matching user ID.  */
extern struct passwd *getpwuid (uid_t __uid);

/* Search for an entry with a matching username.  */
extern struct passwd *getpwnam (__const char *__name);

/* Reentrant versions of some of the functions above.

   PLEASE NOTE: the `getpwent_r' function is not (yet) standardized.
   The interface may change in later versions of this library.  But
   the interface is designed following the principals used for the
   other reentrant functions so the chances are good this is what the
   POSIX people would choose.  */

extern int getpwent_r (struct passwd *__restrict __resultbuf,
		       char *__restrict __buffer, size_t __buflen,
		       struct passwd **__restrict __result);

extern int getpwuid_r (uid_t __uid,
		       struct passwd *__restrict __resultbuf,
		       char *__restrict __buffer, size_t __buflen,
		       struct passwd **__restrict __result);

extern int getpwnam_r (__const char *__restrict __name,
		       struct passwd *__restrict __resultbuf,
		       char *__restrict __buffer, size_t __buflen,
		       struct passwd **__restrict __result);


/* Read an entry from STREAM.  This function is not standardized and
   probably never will.  */
extern int fgetpwent_r (FILE *__restrict __stream,
			struct passwd *__restrict __resultbuf,
			char *__restrict __buffer, size_t __buflen,
			struct passwd **__restrict __result);

/* Re-construct the password-file line for the given uid
   in the given buffer.  This knows the format that the caller
   will expect, but this need not be the format of the password file.  */
extern int getpw (uid_t __uid, char *__buffer);

#endif /* pwd.h  */
#endif
