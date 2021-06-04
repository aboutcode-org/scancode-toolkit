

/* SPDX-License-Identifier: APAFML */
/*
Copyright (c) 1985, 1987, 1989, 1990, 1991, 1992, 1993, 1997 Adobe
Systems Incorporated. All Rights Reserved.

This file and the 14
PostScript(R) AFM files it accompanies may be used, copied, and
distributed for any purpose and without charge, with or without
modification, provided that all copyright notices are retained; that
the AFM files are not distributed without this file; that all
modifications to this file or any of the AFM files are prominently
noted in the modified file(s); and that this paragraph is not
modified. Adobe Systems has no responsibility or obligation to support
the use of the AFM files.
*/

/*
** Fake code so we have something.
*/
#include <nothing.h>


int
noop_fun(int arg1)
{
	short retval;

	recalculatearg(&arg1);

	switch (arg1)
	{
		case 0:
			if (arg1) {
					retval = 1;
			} else {
			retval = 2;
			}
		case 1:
			retval = 2;
		case 2:
			retval = morpharg(arg1);
		case 3:
			if (arg1) {
				retval = 6;
			} else {
				retval = 7;
			}
		case 4:
			retval = upscalearg(arg1);
		default:
			retval = 0;
	}

	return retval;
}

