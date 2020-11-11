/*
** THIS IS A TEST FILE FOR THE SPDX LICENSE DETECTION TESTS											
**																										
** This file has been auto generated using the SPDX License List as represented by
** the JSON files:  https://github.com/spdx/license-list-data 
** 
** This file is for test purposes only. It WILL NOT compile or do anything useful otherwise.
**
** Test File Version: Unofficial version
**
** DISCLAIMER
**
** Any copyrights appearing in this test file do so because they were part of the license text as stored by SPDX and are included 
** only for test purposes as they are part of the license text.	They have no meaning, implied or specific, otherwise.	
*/




/*
** LICENSE HEADER AND COPYRIGHT TO DETECT	
** This section either uses either the standard license header, or if one does not exist, the license 
** text as shown on the SPDX License List. In addition, if the file was generated using the write 
** license identifiers option, they will appear before the license text.
** 										
**
** SPDX License to detect: https://spdx.org/licenses/Abstyles.html				
*/



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

