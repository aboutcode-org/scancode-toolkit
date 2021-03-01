/* camellia.c	ver 1.0.1
 *
 * ***** BEGIN LICENSE BLOCK *****
 * Version: MPL 1.1
 *
 * The contents of this file are subject to the Mozilla Public License Version
 * 1.1 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 * http://www.mozilla.org/MPL/
 *
 * Software distributed under the License is distributed on an "AS IS" basis,
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
 * for the specific language governing rights and limitations under the
 * License.
 *
 * The Original Code is Camellia code.
 *
 * The Initial Developer of the Original Code is
 * NTT(Nippon Telegraph and Telephone Corporation).
 * Portions created by the Initial Developer are Copyright (C) 2006
 * the Initial Developer. All Rights Reserved.
 *
 * Contributor(s):
 *
 * ***** END LICENSE BLOCK ***** */

/*
 *-------------------------------------------------------------------------------------------------
 * NOTE --- NOTE --- NOTE --- NOTE
 * This implementation assumes that all memory addresses passed as parameters are
 * four-byte aligned.
 *-------------------------------------------------------------------------------------------------
 */

#include "camellia.h"
#include <string.h>
#include <stdlib.h>

/*
 *-------------------------------------------------------------------------------------------------
 * These macro variables select what code is used in the creation of the Camellia library objects
 *-------------------------------------------------------------------------------------------------
 */

#define ZERO_MEMORY     0     /* Set to 1 to add variable cleanse code, 0 otherwise */

#define USE_C_FEISTEL_CODE  0     /* Set to 1 to use C code, 0 to inline via macro      */
