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
** SPDX License to detect: https://spdx.org/licenses/mpich2.html				
*/



/* SPDX-License-Identifier: mpich2 */
/*
COPYRIGHT

The following is a notice of limited availability of the
code, and disclaimer which must be included in the prologue of the
code and in all source listings of the code.

Copyright Notice

+ 2002
University of Chicago

Permission is hereby granted to use, reproduce,
prepare derivative works, and to redistribute to others. This software
was authored by:

Argonne National Laboratory Group W. Gropp: (630)
252-4318; FAX: (630) 252-5986; e-mail: gropp@mcs.anl.gov E. Lusk:
(630) 252-7852; FAX: (630) 252-5986; e-mail: lusk@mcs.anl.gov
Mathematics and Computer Science Division Argonne National Laboratory,
Argonne IL 60439

GOVERNMENT LICENSE

Portions of this material
resulted from work developed under a U.S. Government Contract and are
subject to the following license: the Government is granted for itself
and others acting on its behalf a paid-up, nonexclusive, irrevocable
worldwide license in this computer software to reproduce, prepare
derivative works, and perform publicly and display
publicly.

DISCLAIMER

This computer code material was prepared, in
part, as an account of work sponsored by an agency of the United
States Government. Neither the United States, nor the University of
Chicago, nor any of their employees, makes any warranty express or
implied, or assumes any legal liability or responsibility for the
accuracy, completeness, or usefulness of any information, apparatus,
product, or process disclosed, or represents that its use would not
infringe privately owned rights.
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

