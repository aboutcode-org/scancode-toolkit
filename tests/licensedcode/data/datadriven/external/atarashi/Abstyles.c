
/* SPDX-License-Identifier: Abstyles */
/*
This is APREAMBL.TEX, version 1.10e, written by Hans-Hermann
Bode

(HHBODE@DOSUNI1.BITNET), for the BibTeX `adaptable' family,
version 1.10.

See the file APREAMBL.DOC for a detailed
documentation.

This program is distributed WITHOUT ANY WARRANTY,
express or implied.

Copyright (C) 1991, 1992 Hans-Hermann
Bode

Permission is granted to make and distribute verbatim copies of
this document provided that the copyright notice and this permission
notice are preserved on all copies.

Permission is granted to copy and
distribute modified versions of this document under the conditions for
verbatim copying, provided that the entire resulting derived work is
distributed under the terms of a permission notice identical to this
one.
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

