/*
* snpf.c -- snprintf() empulation functions for lsof library
*
* V. Abell
* Purdue University Computing Center
*/

/*
* Copyright 2000 Purdue Research Foundation, West Lafayette, Indiana
* 47907. All rights reserved.
*
* Written by Victor A. Abell
*
* This software is not subject to any license of the American Telephone
* and Telegraph Company or the Regents of the University of California.
*
* This software has been adapted from snprintf.c in sendmail 8.9.3. It
* is subject to the sendmail copyright statements listed below, and the
* sendmail licensing terms stated in the sendmail LICENSE file comment
* section of this file.
*
* Permission is granted to anyone to use this software for any purpose on
* any computer system, and to alter it and redistribute it freely, subject
* to the following restrictions:
*
* 1. Neither the authors nor Purdue University are responsible for any
* consequences of the use of this software.
*
* 2. The origin of this software must not be misrepresented, either by
* explicit claim or by omission. Credit to the authors and Purdue
* University must appear in documentation and sources.
*
* 3. Altered versions must be plainly marked as such, and must not be
* misrepresented as being the original software.
*
* 4. This notice may not be removed or altered.
*/

#include "../machine.h"

#ifdef USE_LIB_SNPF

/*
* Sendmail copyright statements:
*
* Copyright (c) 1998 Sendmail, Inc. All rights reserved.
* Copyright (c) 1997 Eric P. Allman. All rights reserved.
* Copyright (c) 1988, 1993
* The Regents of the University of California. All rights reserved.
*
* By using this file, you agree to the terms and conditions set
* forth in the LICENSE file which can be found at the top level of
* the sendmail distribution.
*
* The LICENSE file may be found in the following comment section.
*/


/*
* Begin endmail LICENSE file.

SENDMAIL LICENSE

The following license terms and conditions apply, unless a different
license is obtained from Sendmail, Inc., 1401 Park Avenue, Emeryville, CA
94608, or by electronic mail at license@sendmail.com.

License Terms:

Use, Modification and Redistribution (including distribution of any
modified or derived work) in source and binary forms is permitted only if
each of the following conditions is met:

1. Redistributions qualify as "freeware" or "Open Source Software" under
one of the following terms:

(a) Redistributions are made at no charge beyond the reasonable cost of
materials and delivery.

(b) Redistributions are accompanied by a copy of the Source Code or by an
irrevocable offer to provide a copy of the Source Code for up to three
years at the cost of materials and delivery. Such redistributions
must allow further use, modification, and redistribution of the Source
Code under substantially the same terms as this license. For the
purposes of redistribution "Source Code" means the complete source
code of sendmail including all modifications.

Other forms of redistribution are allowed only under a separate royalty-
free agreement permitting such redistribution subject to standard
commercial terms and conditions. A copy of such agreement may be
obtained from Sendmail, Inc. at the above address.

2. Redistributions of source code must retain the copyright notices as they
appear in each source code file, these license terms, and the
disclaimer/limitation of liability set forth as paragraph 6 below.

3. Redistributions in binary form must reproduce the Copyright Notice,
these license terms, and the disclaimer/limitation of liability set
forth as paragraph 6 below, in the documentation and/or other materials
provided with the distribution. For the purposes of binary distribution
the "Copyright Notice" refers to the following language:
"Copyright (c) 1998 Sendmail, Inc. All rights reserved."

4. Neither the name of Sendmail, Inc. nor the University of California nor
the names of their contributors may be used to endorse or promote
products derived from this software without specific prior written
permission. The name "sendmail" is a trademark of Sendmail, Inc.

5. All redistributions must comply with the conditions imposed by the
University of California on certain embedded code, whose copyright
notice and conditions for redistribution are as follows:

(a) Copyright (c) 1988, 1993 # The Regents of the University of
California. All rights reserved.

(b) Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

(i) Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

(ii) Redistributions in binary form must reproduce the above
copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided
with the distribution.

(iii) All advertising materials mentioning features or use of this
software must display the following acknowledgement: "This
product includes software developed by the University of
California, Berkeley and its contributors."

(iv) Neither the name of the University nor the names of its
contributors may be used to endorse or promote products derived
from this software without specific prior written permission.

6. Disclaimer/Limitation of Liability: THIS SOFTWARE IS PROVIDED BY
SENDMAIL, INC. AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN
NO EVENT SHALL SENDMAIL, INC., THE REGENTS OF THE UNIVERSITY OF
CALIFORNIA OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH # DAMAGES.

(Version 8.6, last updated 6/24/1998)

* End endmail LICENSE file.
*/

