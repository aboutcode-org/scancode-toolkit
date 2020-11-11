


/* SPDX-License-Identifier: libtiff */
/*
Copyright (c) 1988-1997 Sam Leffler

Copyright (c) 1991-1997 Silicon
Graphics, Inc.

Permission to use, copy, modify, distribute, and sell
this software and its documentation for any purpose is hereby granted
without fee, provided that (i) the above copyright notices and this
permission notice appear in all copies of the software and related
documentation, and (ii) the names of Sam Leffler and Silicon Graphics
may not be used in any advertising or publicity relating to the
software without the specific, prior written permission of Sam Leffler
and Silicon Graphics.

THE SOFTWARE IS PROVIDED "AS-IS" AND WITHOUT
WARRANTY OF ANY KIND, EXPRESS, IMPLIED OR OTHERWISE, INCLUDING WITHOUT
LIMITATION, ANY WARRANTY OF MERCHANTABILITY OR FITNESS FOR A
PARTICULAR PURPOSE.

IN NO EVENT SHALL SAM LEFFLER OR SILICON GRAPHICS
BE LIABLE FOR ANY SPECIAL, INCIDENTAL, INDIRECT OR CONSEQUENTIAL
DAMAGES OF ANY KIND, OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
USE, DATA OR PROFITS, WHETHER OR NOT ADVISED OF THE POSSIBILITY OF
DAMAGE, AND ON ANY THEORY OF LIABILITY, ARISING OUT OF OR IN
CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
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

