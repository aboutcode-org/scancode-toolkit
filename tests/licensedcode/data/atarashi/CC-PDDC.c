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
** SPDX License to detect: https://spdx.org/licenses/CC-PDDC.html				
*/



/* SPDX-License-Identifier: CC-PDDC */
/*
The person or persons who have associated work with this document (the
"Dedicator" or "Certifier") hereby either (a) certifies that, to the
best of his knowledge, the work of authorship identified is in the
public domain of the country from which the work is published, or (b)
hereby dedicates whatever copyright the dedicators holds in the work
of authorship identified below (the "Work") to the public domain. A
certifier, moreover, dedicates any copyright interest he may have in
the associated work, and for these purposes, is described as a
"dedicator" below.

A certifier has taken reasonable steps to verify
the copyright status of this work. Certifier recognizes that his good
faith efforts may not shield him from liability if in fact the work
certified is not in the public domain.

Dedicator makes this
dedication for the benefit of the public at large and to the detriment
of the Dedicator's heirs and successors. Dedicator intends this
dedication to be an overt act of relinquishment in perpetuity of all
present and future rights under copyright law, whether vested or
contingent, in the Work. Dedicator understands that such
relinquishment of all rights includes the relinquishment of all rights
to enforce (by lawsuit or otherwise) those copyrights in the
Work.

Dedicator recognizes that, once placed in the public domain,
the Work may be freely reproduced, distributed, transmitted, used,
modified, built upon, or otherwise exploited by anyone for any
purpose, commercial or non-commercial, and in any way, including by
methods that have not yet been invented or conceived.
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

