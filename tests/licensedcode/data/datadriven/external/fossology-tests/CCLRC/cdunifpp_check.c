/*
 *
 *    Copyright (C) 2004-2006 NERC DataGrid
 *    This software may be distributed under the terms of the
 *    CCLRC Licence for CCLRC Software
 * <CDATDIR>/External_License/CCLRC_CDAT_License.txt 
 *
 */
#ifdef HAVE_PP
#include "cdunifpp.h"

/* check compiled-in type sizes */

int pp_check_sizes()
{
  if (sizeof(Freal4) != 4 ||
      sizeof(Freal8) != 8 ||
      sizeof(Fint4) != 4 ||
      sizeof(Fint8) != 8 ||
      sizeof(Fint) != sizeof (Freal) ||
      cutypelen(inttype) != sizeof(Fint) ||
      cutypelen(realtype) != sizeof(Freal)) {

    pp_error("pp_check_sizes");
    return -1;
  }

  return 0;
}

#endif
