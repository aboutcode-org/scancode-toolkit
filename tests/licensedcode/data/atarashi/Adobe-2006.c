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
** SPDX License to detect: https://spdx.org/licenses/Adobe-2006.html				
*/



/* SPDX-License-Identifier: Adobe-2006 */
/*
Adobe Systems Incorporated(r) Source Code License Agreement
Copyright(c) 2006 Adobe Systems Incorporated. All rights
reserved.

Please read this Source Code License Agreement carefully
before using the source code.

Adobe Systems Incorporated grants to
you a perpetual, worldwide, non-exclusive, no-charge, royalty-free,
irrevocable copyright license, to reproduce, prepare derivative works
of, publicly display, publicly perform, and distribute this source
code and such derivative works in source or object code form without
any attribution requirements.

The name "Adobe Systems Incorporated"
must not be used to endorse or promote products derived from the
source code without prior written permission.

You agree to indemnify,
hold harmless and defend Adobe Systems Incorporated from and against
any loss, damage, claims or lawsuits, including attorney's fees that
arise or result from your use or distribution of the source
code.

THIS SOURCE CODE IS PROVIDED "AS IS" AND "WITH ALL FAULTS",
WITHOUT ANY TECHNICAL SUPPORT OR ANY EXPRESSED OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
ALSO, THERE IS NO WARRANTY OF NON-INFRINGEMENT, TITLE OR QUIET
ENJOYMENT. IN NO EVENT SHALL MACROMEDIA OR ITS SUPPLIERS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOURCE CODE, EVEN
IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
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

