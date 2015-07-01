/*
 * Calendar implementation for busybox
 *
 * See original copyright at the end of this file
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
 *
*/

/* BB_AUDIT SUSv3 compliant with -j and -y extensions (from util-linux). */
/* BB_AUDIT BUG: The output of 'cal -j 1752' is incorrect.  The upstream
 * BB_AUDIT BUG: version in util-linux seems to be broken as well. */
/* http://www.opengroup.org/onlinepubs/007904975/utilities/cal.html */

/* Mar 16, 2003      Manuel Novoa III   (mjn3@codepoet.org)
 *
 * Major size reduction... over 50% (>1.5k) on i386.
 */

#include <sys/types.h>
#include <ctype.h>
#include <err.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#include "busybox.h"

#ifdef CONFIG_LOCALE_SUPPORT
#include <locale.h>
#endif

#define	THURSDAY		4		/* for reformation */
#define	SATURDAY 		6		/* 1 Jan 1 was a Saturday */

#define	FIRST_MISSING_DAY 	639787		/* 3 Sep 1752 */
#define	NUMBER_MISSING_DAYS 	11		/* 11 day correction */

#define	MAXDAYS			42		/* max slots in a month array */
#define	SPACE			-1		/* used in day array */

static const char days_in_month[] = {
	0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31
};

static const char sep1752[] = {
	         1,	2,	14,	15,	16,
	17,	18,	19,	20,	21,	22,	23,
	24,	25,	26,	27,	28,	29,	30
};

static int julian;

/* leap year -- account for gregorian reformation in 1752 */
#define	leap_year(yr) \
	((yr) <= 1752 ? !((yr) % 4) : \
	(!((yr) % 4) && ((yr) % 100)) || !((yr) % 400))

static int is_leap_year(int year)
{
	return leap_year(year);
}
#undef leap_year
#define leap_year(yr) is_leap_year(yr)

/* number of centuries since 1700, not inclusive */
#define	centuries_since_1700(yr) \
	((yr) > 1700 ? (yr) / 100 - 17 : 0)

/* number of centuries since 1700 whose modulo of 400 is 0 */
#define	quad_centuries_since_1700(yr) \
	((yr) > 1600 ? ((yr) - 1600) / 400 : 0)

/* number of leap years between year 1 and this year, not inclusive */
#define	leap_years_since_year_1(yr) \
	((yr) / 4 - centuries_since_1700(yr) + quad_centuries_since_1700(yr))

static void center __P((char *, int, int));
static void day_array __P((int, int, int *));
static void trim_trailing_spaces_and_print __P((char *));

static void blank_string(char *buf, size_t buflen);
static char *build_row(char *p, int *dp);

#define	DAY_LEN		3		/* 3 spaces per day */
#define	J_DAY_LEN	(DAY_LEN + 1)
#define	WEEK_LEN	20		/* 7 * 3 - one space at the end */
#define	J_WEEK_LEN	(WEEK_LEN + 7)
#define	HEAD_SEP	2		/* spaces between day headings */

int cal_main(int argc, char **argv)
{
	struct tm *local_time;
	struct tm zero_tm;
	time_t now;
	int month, year, flags, i;
	char *month_names[12];
	char day_headings[28];	/* 28 for julian, 21 for nonjulian */
	char buf[40];

#ifdef CONFIG_LOCALE_SUPPORT
	setlocale(LC_TIME, "");
#endif

	flags = bb_getopt_ulflags(argc, argv, "jy");

	julian = flags & 1;

	argv += optind;

	month = 0;

	if ((argc -= optind) > 2) {
		bb_show_usage();
	}

	if (!argc) {
		time(&now);
		local_time = localtime(&now);
		year = local_time->tm_year + 1900;
		if (!(flags & 2)) {
			month = local_time->tm_mon + 1;
		}
	} else {
		if (argc == 2) {
			month = bb_xgetularg10_bnd(*argv++, 1, 12);
		}
		year = bb_xgetularg10_bnd(*argv, 1, 9999);
	}

	blank_string(day_headings, sizeof(day_headings) - 7 +  7*julian);

	i = 0;
	do {
		zero_tm.tm_mon = i;
		strftime(buf, sizeof(buf), "%B", &zero_tm);
		month_names[i] = bb_xstrdup(buf);

		if (i < 7) {
			zero_tm.tm_wday = i;
			strftime(buf, sizeof(buf), "%a", &zero_tm);
			strncpy(day_headings + i * (3+julian) + julian, buf, 2);
		}
	} while (++i < 12);

	if (month) {
		int row, len, days[MAXDAYS];
		int *dp = days;
		char lineout[30];

		day_array(month, year, dp);
		len = sprintf(lineout, "%s %d", month_names[month - 1], year);
		bb_printf("%*s%s\n%s\n",
			   ((7*julian + WEEK_LEN) - len) / 2, "",
			   lineout, day_headings);
		for (row = 0; row < 6; row++) {
			build_row(lineout, dp)[0] = '\0';
			dp += 7;
			trim_trailing_spaces_and_print(lineout);
		}
	} else {
		int row, which_cal, week_len, days[12][MAXDAYS];
		int *dp;
		char lineout[80];

		sprintf(lineout, "%d", year);
		center(lineout,
			   (WEEK_LEN * 3 + HEAD_SEP * 2)
			   + julian * (J_WEEK_LEN * 2 + HEAD_SEP
						   - (WEEK_LEN * 3 + HEAD_SEP * 2)),
			   0);
		puts("\n");		/* two \n's */
		for (i = 0; i < 12; i++) {
			day_array(i + 1, year, days[i]);
		}
		blank_string(lineout, sizeof(lineout));
		week_len = WEEK_LEN + julian * (J_WEEK_LEN - WEEK_LEN);
		for (month = 0; month < 12; month += 3-julian) {
			center(month_names[month], week_len, HEAD_SEP);
			if (!julian) {
				center(month_names[month + 1], week_len, HEAD_SEP);
			}
			center(month_names[month + 2 - julian], week_len, 0);
			bb_printf("\n%s%*s%s", day_headings, HEAD_SEP, "", day_headings);
			if (!julian) {
				bb_printf("%*s%s", HEAD_SEP, "", day_headings);
			}
			putchar('\n');
			for (row = 0; row < (6*7); row += 7) {
				for (which_cal = 0; which_cal < 3-julian; which_cal++) {
					dp = days[month + which_cal] + row;
					build_row(lineout + which_cal * (week_len + 2), dp);
				}
				/* blank_string took care of nul termination. */
				trim_trailing_spaces_and_print(lineout);
			}
		}
	}

	bb_fflush_stdout_and_exit(0);
}

/*
 * day_array --
 *	Fill in an array of 42 integers with a calendar.  Assume for a moment
 *	that you took the (maximum) 6 rows in a calendar and stretched them
 *	out end to end.  You would have 42 numbers or spaces.  This routine
 *	builds that array for any month from Jan. 1 through Dec. 9999.
 */
static void day_array(int month, int year, int *days)
{
	long temp;
	int i;
	int j_offset;
	int day, dw, dm;

	memset(days, SPACE, MAXDAYS * sizeof(int));

	if ((month == 9) && (year == 1752)) {
		j_offset = julian * 244;
		i = 0;
		do {
			days[i+2] = sep1752[i] + j_offset;
		} while (++i < sizeof(sep1752));

		return;
	}

	/* day_in_year
	 *	return the 1 based day number within the year
	 */
	day = 1;
	if ((month > 2) && leap_year(year)) {
		++day;
	}

	i = month;
	while (i) {
		day += days_in_month[--i];
	}

	/* day_in_week
	 *	return the 0 based day number for any date from 1 Jan. 1 to
	 *	31 Dec. 9999.  Assumes the Gregorian reformation eliminates
	 *	3 Sep. 1752 through 13 Sep. 1752.  Returns Thursday for all
	 *	missing days.
	 */
	dw = THURSDAY;
	temp = (long)(year - 1) * 365 + leap_years_since_year_1(year - 1)
		+ day;
	if (temp < FIRST_MISSING_DAY) {
		dw = ((temp - 1 + SATURDAY) % 7);
	} else if (temp >= (FIRST_MISSING_DAY + NUMBER_MISSING_DAYS)) {
		dw = (((temp - 1 + SATURDAY) - NUMBER_MISSING_DAYS) % 7);
	}

	if (!julian) {
		day = 1;
	}

	dm = days_in_month[month];
	if ((month == 2) && leap_year(year)) {
		++dm;
	}

	while (dm) {
		days[dw++] = day++;
		--dm;
	}
}

static void trim_trailing_spaces_and_print(char *s)
{
	char *p = s;

	while (*p) {
		++p;
	}
	while (p > s) {
		--p;
		if (!(isspace)(*p)) {	/* We want the function... not the inline. */
			p[1] = '\0';
			break;
		}
	}

	puts(s);
}

static void center(char *str, int len, int separate)
{
	int n = strlen(str);
	len -= n;
	bb_printf("%*s%*s", (len/2) + n, str, (len/2) + (len % 2) + separate, "");
}

static void blank_string(char *buf, size_t buflen)
{
	memset(buf, ' ', buflen);
	buf[buflen-1] = '\0';
}

static char *build_row(char *p, int *dp)
{
	int col, val, day;

	memset(p, ' ', (julian + DAY_LEN) * 7);

	col = 0;
	do {
		if ((day = *dp++) != SPACE) {
			if (julian) {
				++p;
				if (day >= 100) {
					*p = '0';
					p[-1] = (day / 100) + '0';
					day %= 100;
				}
			}
			if ((val = day / 10) > 0) {
				*p = val + '0';
			}
			*++p = day % 10 + '0';
			p += 2;
		} else {
			p += DAY_LEN + julian;
		}
	} while (++col < 7);

	return p;
}

/*
 * Copyright (c) 1989, 1993, 1994
 *	The Regents of the University of California.  All rights reserved.
 *
 * This code is derived from software contributed to Berkeley by
 * Kim Letkeman.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the University nor the names of its contributors
 *    may be used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 */


