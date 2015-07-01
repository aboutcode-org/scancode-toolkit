/* Copyright (C) 1996, 1997, 1998, 1999 Free Software Foundation, Inc.
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

/* Declaration of types and functions for shadow password suite.  */

#if !defined CONFIG_USE_BB_SHADOW
#include <shadow.h>
#else

#ifndef _SHADOW_H
#define _SHADOW_H	1

#include <stdio.h>

/* Paths to the user database files.  */
#ifndef _PATH_SHADOW
#define	_PATH_SHADOW	"/etc/shadow"
#endif
#define	SHADOW _PATH_SHADOW


/* Structure of the password file.  */
struct spwd
{
    char *sp_namp;		/* Login name.  */
    char *sp_pwdp;		/* Encrypted password.  */
    long int sp_lstchg;		/* Date of last change.  */
    long int sp_min;		/* Minimum number of days between changes.  */
    long int sp_max;		/* Maximum number of days between changes.  */
    long int sp_warn;		/* Number of days to warn user to change
				   the password.  */
    long int sp_inact;		/* Number of days the account may be
				   inactive.  */
    long int sp_expire;		/* Number of days since 1970-01-01 until
				   account expires.  */
    unsigned long int sp_flag;	/* Reserved.  */
};


/* Open database for reading.  */
extern void setspent (void);

/* Close database.  */
extern void endspent (void);

/* Get next entry from database, perhaps after opening the file.  */
extern struct spwd *getspent (void);

/* Get shadow entry matching NAME.  */
extern struct spwd *getspnam (__const char *__name);

/* Read shadow entry from STRING.  */
extern struct spwd *sgetspent (__const char *__string);

/* Read next shadow entry from STREAM.  */
extern struct spwd *fgetspent (FILE *__stream);

/* Write line containing shadow password entry to stream.  */
extern int putspent (__const struct spwd *__p, FILE *__stream);

/* Reentrant versions of some of the functions above.  */
extern int getspent_r (struct spwd *__result_buf, char *__buffer,
		       size_t __buflen, struct spwd **__result);

extern int getspnam_r (__const char *__name, struct spwd *__result_buf,
		       char *__buffer, size_t __buflen,
		       struct spwd **__result);

extern int sgetspent_r (__const char *__string, struct spwd *__result_buf,
			char *__buffer, size_t __buflen,
			struct spwd **__result);

extern int fgetspent_r (FILE *__stream, struct spwd *__result_buf,
			char *__buffer, size_t __buflen,
			struct spwd **__result);
/* Protect password file against multi writers.  */
extern int lckpwdf (void);

/* Unlock password file.  */
extern int ulckpwdf (void);

#endif /* shadow.h */
#endif
