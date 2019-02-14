/*
**	ualarm.c	- 
**
**
** Copyright (c) 1993-95  David J. Hughes
** Copyright (c) 1995  Hughes Technologies
**
** Permission to use, copy, and distribute for non-commercial purposes,
** is hereby granted without fee, providing that the above copyright
** notice appear in all copies and that both the copyright notice and this
** permission notice appear in supporting documentation.
**
** This software is provided "as is" without any expressed or implied warranty.
**
*/


#ifndef lint
static char RCSid[] = 
	"ualarm.c,v 1.2 1994/07/05 02:01:00 bambi Exp";
#endif 



#include<sys/time.h>

#include <common/portability.h>


#ifndef HAVE_UALARM


ualarm(val, interval)
	unsigned	val,
			interval;
{
	struct	itimerval	value;

	value.it_interval.tv_sec = 0;
	value.it_interval.tv_usec = (long) interval;
	value.it_value.tv_sec = 0;
	value.it_value.tv_usec = (long) val;
	setitimer(ITIMER_REAL,&value,(struct itimerval *)0);
}


#endif
