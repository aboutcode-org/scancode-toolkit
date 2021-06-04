/**********************************************************************
 *                        gost89.c                                    *
 *             Copyright (c) 2005-2006 Cryptocom LTD                  *
 *         This file is distributed under the same license as OpenSSL *
 *                                                                    *
 *          Implementation of GOST 28147-89 encryption algorithm      *
 *            No OpenSSL libraries required to compile and use        *
 *                              this code                             *
 **********************************************************************/
#include <string.h>
#include "gost89.h"
/* Substitution blocks from RFC 4357

   Note: our implementation of gost 28147-89 algorithm
   uses S-box matrix rotated 90 degrees counterclockwise, relative to
   examples given in RFC.


*/

/* Substitution blocks from test examples for GOST R 34.11-94*/
gost_subst_block GostR3411_94_TestParamSet = {
	{0X1,0XF,0XD,0X0,0X5,0X7,0XA,0X4,0X9,0X2,0X3,0XE,0X6,0XB,0X8,0XC},
	{0XD,0XB,0X4,0X1,0X3,0XF,0X5,0X9,0X0,0XA,0XE,0X7,0X6,0X8,0X2,0XC},
	{0X4,0XB,0XA,0X0,0X7,0X2,0X1,0XD,0X3,0X6,0X8,0X5,0X9,0XC,0XF,0XE},
	{0X6,0XC,0X7,0X1,0X5,0XF,0XD,0X8,0X4,0XA,0X9,0XE,0X0,0X3,0XB,0X2},
	{0X7,0XD,0XA,0X1,0X0,0X8,0X9,0XF,0XE,0X4,0X6,0XC,0XB,0X2,0X5,0X3},
	{0X5,0X8,0X1,0XD,0XA,0X3,0X4,0X2,0XE,0XF,0XC,0X7,0X6,0X0,0X9,0XB},
	{0XE,0XB,0X4,0XC,0X6,0XD,0XF,0XA,0X2,0X3,0X8,0X1,0X0,0X7,0X5,0X9},
	{0X4,0XA,0X9,0X2,0XD,0X8,0X0,0XE,0X6,0XB,0X1,0XC,0X7,0XF,0X5,0X3}
	};
