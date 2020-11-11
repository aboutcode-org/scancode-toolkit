

/* SPDX-License-Identifier: GPL-2.0-with-font-exception */
/*
insert GPL v2 license text here

Font Exception

As a special
exception, if you create a document which uses this font, and embed
this font or unaltered portions of this font into the document, this
font does not by itself cause the resulting document to be covered by
the GNU General Public License. This exception does not however
invalidate any other reasons why the document might be covered by the
GNU General Public License. If you modify this font, you may extend
this exception to your version of the font, but you are not obligated
to do so. If you do not wish to do so, delete this exception statement
from your version.
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

