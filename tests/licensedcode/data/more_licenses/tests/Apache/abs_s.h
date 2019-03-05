
/* ------------------------------------------------------------------
* Copyright (C) 1998-2009 PacketVideo
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
* http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
* express or implied.
* See the License for the specific language governing permissions
* and limitations under the License.
* -------------------------------------------------------------------
*/
/****************************************************************************************
Portions of this file are derived from the following 3GPP standard:

3GPP TS 26.073
ANSI-C code for the Adaptive Multi-Rate (AMR) speech codec
Available from http://www.3gpp.org

(C) 2004, 3GPP Organizational Partners (ARIB, ATIS, CCSA, ETSI, TTA, TTC)
Permission to distribute, modify and use this file under the standard license
terms listed above has been obtained from the copyright holder.
****************************************************************************************/
/*

Pathname: ./gsm-amr/c/include/abs_s.h

------------------------------------------------------------------------------
REVISION HISTORY

Description: Created separate header file for abs_s function.

Description: Updated template to make it build for Symbian.

Description: Moved _cplusplus #ifdef after Include section.

Who: Date:
Description:

------------------------------------------------------------------------------
INCLUDE DESCRIPTION

This file contains all the constant definitions and prototype definitions
needed by the abs_s function.

------------------------------------------------------------------------------
*/

/*----------------------------------------------------------------------------
; CONTINUE ONLY IF NOT ALREADY DEFINED
----------------------------------------------------------------------------*/
#ifndef ABS_S_H
#define ABS_S_H

/*----------------------------------------------------------------------------
; INCLUDES
----------------------------------------------------------------------------*/
#include "basicop_malloc.h"

/*--------------------------------------------------------------------------*/
#ifdef __cplusplus
extern "C"
{
#endif

/*----------------------------------------------------------------------------
; MACROS
; Define module specific macros here
----------------------------------------------------------------------------*/

/*----------------------------------------------------------------------------
; DEFINES
; Include all pre-processor statements here.
----------------------------------------------------------------------------*/

/*----------------------------------------------------------------------------
; EXTERNAL VARIABLES REFERENCES
; Declare variables used in this module but defined elsewhere
----------------------------------------------------------------------------*/

/*----------------------------------------------------------------------------
; SIMPLE TYPEDEF'S
----------------------------------------------------------------------------*/

/*----------------------------------------------------------------------------
; ENUMERATED TYPEDEF'S
----------------------------------------------------------------------------*/

/*----------------------------------------------------------------------------
; STRUCTURES TYPEDEF'S
----------------------------------------------------------------------------*/

/*----------------------------------------------------------------------------
; GLOBAL FUNCTION DEFINITIONS
; Function Prototype declaration
----------------------------------------------------------------------------*/
Word16 abs_s(Word16 var1);

/*----------------------------------------------------------------------------
; END
----------------------------------------------------------------------------*/
#ifdef __cplusplus
}
#endif

#endif /* ABS_S_H */
