
/* HOW TO COMPILE:

     gcc -O -g -Wall -maltivec -mabi=altivec -DALTIVEC -DGCC_COMPILER 
         testVMX.c -o testVMX

*/

/*
 * testVMX - A test program to check the correctness of VMX instructions
 * 
 * Copyright (C) 2004 CEPBA-IBM Research Institute
 * 
 * Authors: Jose Maria Cela, Raul de la Cruz,
 *          Rogeli Grima, Xavier Saez <blade_support@ciri.upc.es>
 *
 * Web page: http://www.ciri.upc.es/cela_pblade/
 * 
 * This file is part of testVMX.
 * 
 * testVMX is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * testVMX is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with testVMX; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  US
 */

/*
 * Version 0.2.2 2004/09/02
 * Removed some not useful flags for compilation and changed the GPL license
 * header updating the contact email and adding the web page URL
 *
 * Version 0.2.1 2004/07/07
 * Some flags added in Makefile for XLC compilation (-qalias, -qinline)
 *
 * Version 0.2 2004/07/02
 * Makefile and testVMX.c patched to compile with SLES 9 (Linux - GCC 3.3.3),
 * IBM XLC Enterprise Edition and MacOS X 10.3 (Darwin - GCC 3.3)
 *
 * Version 0.1 2004/03/05
 * First public version release
 */


#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <limits.h>
#include <string.h>

/* Calloc for align data to 16 bytes boundaries */

/* ----------- BEGIN #include "memoryVector.h" ----------- */

/*
 * testVMX - A test program to check the correctness of VMX instructions
 * 
 * Copyright (C) 2004 CEPBA-IBM Research Institute
 * 
 * Authors: Jose Maria Cela, Raul de la Cruz,
 *          Rogeli Grima, Xavier Saez <blade_support@ciri.upc.es>
 *
 * Web page: http://www.ciri.upc.es/cela_pblade/
 * 
 * This file is part of testVMX.
 * 
 * testVMX is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * testVMX is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with testVMX; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  US
 */

#ifndef MEMORY_VECTOR_H
# define MEMORY_VECTOR_H

# include <stdlib.h>

  void *calloc_vec( size_t nmemb, size_t size );
  void  free_vec( void *ptr );

#endif

/* ----------- END #include "memoryVector.h" ----------- */

/* ----------- BEGIN #include "memoryVector.c" ----------- */

/*
 * testVMX - A test program to check the correctness of VMX instructions
 * 
 * Copyright (C) 2004 CEPBA-IBM Research Institute
 * 
 * Authors: Jose Maria Cela, Raul de la Cruz,
 *          Rogeli Grima, Xavier Saez <blade_support@ciri.upc.es>
 *
 * Web page: http://www.ciri.upc.es/cela_pblade/
 * 
 * This file is part of testVMX.
 * 
 * testVMX is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * testVMX is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with testVMX; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  US
 */

#include <stdio.h>
#include <string.h>
/* #include "memoryVector.h"*/

typedef struct
        {
          char  *realAdd;
          char  *returnAdd;
        } Tmemtab;


static Tmemtab *memTab    = NULL;
static size_t   nadd      =   0;
static size_t   MAX_N_ADD = 100;


void *calloc_vec( size_t nmemb, size_t size )
{
/* ---------------------------------------------------------- Local Variables */
    char   *realadd;
    char   *retadd;
    size_t  nbytes, cc, rr;

/* -------------------------------------------------------------------- BEGIN */
  if (memTab == (Tmemtab*)NULL)
  {
    memTab = (Tmemtab *) malloc( MAX_N_ADD*sizeof(Tmemtab) );
    if (memTab == (Tmemtab*)NULL)
    {
      fprintf(stderr, "\n------------ FATAL ERRROR ------------------\n");
      fprintf(stderr, "Memory table out of memory\n");
      return NULL; 
    }
  }

  /* 16 extra bytes are allocated for adjust alignement */
  nbytes = (size*nmemb)+16;

  /* Alloc a block of 'nbytes' */
  realadd = (char *) malloc( nbytes );
  if (realadd == (char *)NULL)
  {
      fprintf(stderr, "\n------------ FATAL ERRROR ------------------\n");
      fprintf(stderr, "Out of memory\n");
      return NULL;
  }

  memset( realadd, 0, nbytes );

  cc = ((size_t)realadd)/16;
  rr = ((size_t)realadd)%16;
  if (rr == 0)
    retadd = realadd;
  else
    retadd = (char *)((cc+1)*16);

  if (nadd == MAX_N_ADD)
  {
    MAX_N_ADD += 100;
    memTab = (Tmemtab*) realloc( memTab, MAX_N_ADD*sizeof(Tmemtab) );
    if (memTab == (Tmemtab*)NULL)
    {
      free( realadd );
      fprintf(stderr, "\n------------ FATAL ERRROR ------------------\n");
      fprintf(stderr, "Memory table out of memory\n");
      return NULL; 
    }
  }

  memTab[nadd].realAdd   =  realadd;
  memTab[nadd].returnAdd =  retadd;;
  nadd++;

  return (void*)retadd;
/* ---------------------------------------------------------------------- END */
}


void free_vec( void *ptr )
{
/* ---------------------------------------------------------- Local Variables */
  int ii, pos;

/* -------------------------------------------------------------------- BEGIN */
  pos = -1;
  for (ii= 0; ii< nadd; ii++)
    if (memTab[ii].returnAdd == ptr)
    {
      pos = ii;
      break;
    }

  if (pos == -1)
  {
      fprintf(stderr, "\n------------ WARNING ------------------------\n");
      fprintf(stderr, "Pointer not found in memory table\n\n");
  }
  else
  {
    free( memTab[ii].realAdd );

    for (ii= pos+1; ii< nadd; ii++)
      memTab[ii-1] = memTab[ii];
    nadd--;

    if (nadd == 0)
    {
      free( memTab );
      memTab    = NULL;
      MAX_N_ADD = 100;
    }
  }
/* ---------------------------------------------------------------------- END */
}


/* ----------- END #include "memoryVector.c" ----------- */


#ifdef ALTIVEC
# ifdef GCC_COMPILER
#  include <altivec.h>
# endif



//#define TEST_FLOATS



/* Redefinition for undefined NAN and xlC compiling C++ code */
# if !defined(NAN) || ( defined(__IBMCPP__) && defined(XLC_COMPILER) )
#  undef   NAN
#  define  NAN 0x7FC00000
/* #  define  NAN 0xFFFA5A5A
 * #  define  NAN 0x80000000 
 * #  define  NAN 0x00008000 
 */
# endif


int part1( );
int part2( );
int part3( );
int part4( );
int part5( );


typedef union
{
   vector signed char    v;
   signed char           e[16];
} TvecChar;

typedef union
{
   vector unsigned char  v;
   unsigned char         e[16];
} TvecUChar;

typedef union
{
   vector bool char      v;
   unsigned char         e[16];
} TvecBChar;

typedef union
{
   vector signed short   v;
   signed short          e[8];
} TvecShort;

typedef union
{
   vector unsigned short v;
   unsigned short        e[8];
} TvecUShort;

typedef union
{
   vector bool short     v;
   unsigned short        e[8];
} TvecBShort;

typedef union
{
   vector signed int     v;
   signed int            e[4];
} TvecInt;

typedef union
{
   vector unsigned int   v;
   unsigned int          e[4];
} TvecUInt;

typedef union
{
   vector bool int       v;
   unsigned int          e[4];
} TvecBInt;

#if defined TEST_FLOATS
typedef union
{
   vector float          v;
   float                 e[4];
   signed int            i[4];
} TvecFloat;
#endif

/* Scalar bool types declaration */
typedef unsigned char   TboolChar;
typedef unsigned short  TboolShort;
typedef unsigned int    TboolInt;

#endif






/**********************************************************************
 Main()
 **********************************************************************/



int main()
{
  TvecChar      Caux1,  Caux2,  Caux3;//,  Caux4;
  TvecUChar     UCaux1, UCaux2, UCaux3;//, UCaux4;
  TvecBChar     BCaux1;//, BCaux2, BCaux3, BCaux4;
  TvecShort     Saux1,  Saux2,  Saux3;//,  Saux4;
  TvecUShort    USaux1, USaux2, USaux3;//, USaux4;
  TvecBShort    BSaux1;//, BSaux2, BSaux3, BSaux4;
  TvecInt       Iaux1,  Iaux2,  Iaux3;//,  Iaux4;
  TvecUInt      UIaux1, UIaux2, UIaux3;//, UIaux4;
  TvecBInt      BIaux1;//, BIaux2, BIaux3, BIaux4;
#if defined TEST_FLOATS
  TvecFloat     Faux1,  Faux2,  Faux3;//,  Faux4;
#endif  
  
  int                  i, err, j;//, b, bAux;
#if defined TEST_FLOATS
  int                  b;
  signed   int         Ivec1, Ivec2, Ivec3;
#endif

//  unsigned char        *UCvec1;
//  signed   short       *Svec1;
//  unsigned short       *USvec1;
//  unsigned int         *UIvec1;
#if defined TEST_FLOATS
//  float                *Fvec1;
#endif

  /* For saturated rutines */
//  long long int         LLaux;

  signed   char         Caux;
  unsigned char         UCaux;
  signed   short        Saux;
  unsigned short        USaux;
  signed   int          Iaux;//, I1, I2;
  unsigned int          UIaux;//, UI1, UI2;
#if defined TEST_FLOATS
  float                 Faux;
#endif
  
  /* Scalar bool types definition */
  TboolChar             BCaux;
  TboolShort            BSaux;
  TboolInt              BIaux;

/*
  union
  {
    float          f;
    signed   int   si;
    unsigned int   ui;
    signed   short ss[2];
    unsigned short us[2];
    signed   char  sc[4];
    unsigned char  uc[4];
  } INTunion1, INTunion2;

  union
  {
    signed   short  ss;
    unsigned short  us;
    signed   char   sc[2];
    unsigned char   uc[2];
  } SHOunion1, SHOunion2;
*/

#if defined (GCC_COMPILER)
  vector signed char    Ccons1   = (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
  vector signed char    Ccons2   = (vector signed char){1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1};
  vector signed char    Ccons3   = (vector signed char){-128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127};
  vector unsigned char  UCcons1  = (vector unsigned char){248, 249, 250, 251, 252, 253, 254, 255, 0, 1, 2, 3, 4, 5, 6, 7};
  vector unsigned char  UCcons2  = (vector unsigned char){2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2};
  vector unsigned char  UCcons3  = (vector unsigned char){1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8};
  vector signed short   Scons1   = (vector signed short){-4, -3, -2, -1, 0, 1, 2, 3};
  vector signed short   Scons2   = (vector signed short){-32768, 10000, 1, 1, 1, 1, -10000, -10000};
  vector signed short   Scons3   = (vector signed short){-32768, 32767, -32768, 32767, -32768, 32767, -32768, 32767};
  vector unsigned short UScons1  = (vector unsigned short){65532, 65533, 65534, 65535, 0, 1, 2, 3};
  vector unsigned short UScons2  = (vector unsigned short){1, 1, 1, 1, 1, 1, 1, 1};
  vector unsigned short UScons3  = (vector unsigned short){1, 2, 3, 4, 1, 2, 3, 4};
  vector signed int     Icons1   = (vector signed int){-4, -1, 1, 4};
  vector signed int     Icons2   = (vector signed int){1, 1, 1, 1};
  vector signed int     Icons3   = (vector signed int){0x80000000, 0x7FFFFFFF, 0x80000000, 0x7FFFFFFF};
  vector unsigned int   UIcons1  = (vector unsigned int){0xFFFFFFFE, 0xFFFFFFFF, 0, 1};
  vector unsigned int   UIcons2  = (vector unsigned int){1, 1, 1, 1};
  vector unsigned int   UIcons3  = (vector unsigned int){1, 2, 1, 2};

#if defined TEST_FLOATS
  vector float          Fcons1   = (vector float){-1.5, 1.0, 0.5, -3.999};
  vector float          Fcons2   = (vector float){1.0, 1.0, 1.0, 1.0};
  vector float          Fcons3   = (vector float){100000000000.0, 1.0, -1.0, -1234567890.0};
#endif

#elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
  vector signed char    Ccons1   = (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
  vector signed char    Ccons2   = (vector signed char)(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1);
  vector signed char    Ccons3   = (vector signed char)(-128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127);
  vector unsigned char  UCcons1  = (vector unsigned char)(248, 249, 250, 251, 252, 253, 254, 255, 0, 1, 2, 3, 4, 5, 6, 7);
  vector unsigned char  UCcons2  = (vector unsigned char)(2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2);
  vector unsigned char  UCcons3  = (vector unsigned char)(1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8);
  vector signed short   Scons1   = (vector signed short)(-4, -3, -2, -1, 0, 1, 2, 3);
  vector signed short   Scons2   = (vector signed short)(-32768, 10000, 1, 1, 1, 1, -10000, -10000);
  vector signed short   Scons3   = (vector signed short)(-32768, 32767, -32768, 32767, -32768, 32767, -32768, 32767);
  vector unsigned short UScons1  = (vector unsigned short)(65532, 65533, 65534, 65535, 0, 1, 2, 3);
  vector unsigned short UScons2  = (vector unsigned short)(1, 1, 1, 1, 1, 1, 1, 1);
  vector unsigned short UScons3  = (vector unsigned short)(1, 2, 3, 4, 1, 2, 3, 4);
  vector signed int     Icons1   = (vector signed int)(-4, -1, 1, 4);
  vector signed int     Icons2   = (vector signed int)(1, 1, 1, 1);
  vector signed int     Icons3   = (vector signed int)(0x80000000, 0x7FFFFFFF, 0x80000000, 0x7FFFFFFF);
  vector unsigned int   UIcons1  = (vector unsigned int)(0xFFFFFFFE, 0xFFFFFFFF, 0, 1);
  vector unsigned int   UIcons2  = (vector unsigned int)(1, 1, 1, 1);
  vector unsigned int   UIcons3  = (vector unsigned int)(1, 2, 1, 2);

#if defined TEST_FLOATS
  vector float          Fcons1   = (vector float)(-1.5, 1.0, 0.5, -3.999);
  vector float          Fcons2   = (vector float)(1.0, 1.0, 1.0, 1.0);
  vector float          Fcons3   = (vector float)(100000000000.0, 1.0, -1.0, -1234567890.0);
#endif

#endif


/*    Function vec_abs    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_abs( Ccons1 );
  Caux2.v = Ccons1;
  for( i=0; i< 16; i++ )
    if (Caux1.e[i] != abs( Caux2.e[i] ))
      err++;
  if (err)
    printf("Function vec_abs [type char]              ===> Error\n");
  else
    printf("Function vec_abs [type char]              ===> OK\n");

  err = 0;
  Saux1.v = vec_abs( Scons1 );
  Saux2.v = Scons1;
  for( i=0; i< 8; i++ )
    if (Saux1.e[i] != abs( Saux2.e[i] ))
      err++;
  if (err)
    printf("Function vec_abs [type short]             ===> Error\n");
  else
    printf("Function vec_abs [type short]             ===> OK\n");

  err = 0;
  Iaux1.v = vec_abs( Icons1 );
  Iaux2.v = Icons1;
  for( i=0; i< 4; i++ )
    if (Iaux1.e[i] != abs( Iaux2.e[i] ))
      err++;
  if (err)
    printf("Function vec_abs [type integer]           ===> Error\n");
  else
    printf("Function vec_abs [type integer]           ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
  Faux1.v = vec_abs( Fcons1 );
  Faux2.v = Fcons1;
  for( i=0; i< 4; i++ )
    if (Faux1.e[i] != fabs( Faux2.e[i] ))
      err++;
  if (err)
    printf("Function vec_abs [type float]             ===> Error\n");
  else
    printf("Function vec_abs [type float]             ===> OK\n");
#endif

/*    Function vec_abss    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_abss( Ccons1 );
  Caux2.v = Ccons1;
  for( i=0; i< 16; i++ )
    if (Caux1.e[i] != abs( Caux2.e[i] ))
      err++;
  if (err)
    printf("Function vec_abss [type char]             ===> Error\n");
  else
    printf("Function vec_abss [type char]             ===> OK\n");

  err = 0;
  Saux1.v = vec_abss( Scons1 );
  Saux2.v = Scons1;
  for( i=0; i< 8; i++ )
    if (Saux1.e[i] != abs( Saux2.e[i] ))
      err++;
  if (err)
    printf("Function vec_abss [type short]            ===> Error\n");
  else
    printf("Function vec_abss [type short]            ===> OK\n");

  err = 0;
  Iaux1.v = vec_abss( Icons1 );
  Iaux2.v = Icons1;
  for( i=0; i< 4; i++ )
    if (Iaux1.e[i] != abs( Iaux2.e[i] ))
      err++;
  if (err)
    printf("Function vec_abss [type integer]          ===> Error\n");
  else
    printf("Function vec_abss [type integer]          ===> OK\n");

/*    Function vec_add    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_add( Ccons1, Ccons2 );
  Caux2.v = Ccons1;
  Caux3.v = Ccons2;
  for( i=0; i< 16; i++ )
  {
    Caux = Caux2.e[i]+Caux3.e[i];
    if (Caux1.e[i] != Caux)
      err++;
  }
  if (err)
    printf("Function vec_add [type char]              ===> Error\n");
  else
    printf("Function vec_add [type char]              ===> OK\n");

  err = 0;
  UCaux1.v = vec_add( UCcons1, UCcons2 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons2;
  for( i=0; i< 16; i++ )
  {
    UCaux = UCaux2.e[i]+UCaux3.e[i];
    if (UCaux1.e[i] != UCaux)
      err++;
  }
  if (err)
    printf("Function vec_add [type unsigned char]     ===> Error\n");
  else
    printf("Function vec_add [type unsigned char]     ===> OK\n");

  err = 0;
  Saux1.v = vec_add( Scons1, Scons2 );
  Saux2.v = Scons1;
  Saux3.v = Scons2;
  for( i=0; i< 8; i++ )
  {
    Saux = Saux2.e[i]+Saux3.e[i];
    if (Saux1.e[i] != Saux)
      err++;
  }
  if (err)
    printf("Function vec_add [type short]             ===> Error\n");
  else
    printf("Function vec_add [type short]             ===> OK\n");

  err = 0;
  USaux1.v = vec_add( UScons1, UScons2 );
  USaux2.v = UScons1;
  USaux3.v = UScons2;
  for( i=0; i< 8; i++ )
  {
    USaux = USaux2.e[i]+USaux3.e[i];
    if (USaux1.e[i] != USaux)
      err++;
  }
  if (err)
    printf("Function vec_add [type unsigned short]    ===> Error\n");
  else
    printf("Function vec_add [type unsigned short]    ===> OK\n");

  err = 0;
  Iaux1.v = vec_add( Icons1, Icons2 );
  Iaux2.v = Icons1;
  Iaux3.v = Icons2;
  for( i=0; i< 4; i++ )
  {
    Iaux = Iaux2.e[i]+Iaux3.e[i];
    if (Iaux1.e[i] != Iaux)
      err++;
  }
  if (err)
    printf("Function vec_add [type integer]           ===> Error\n");
  else
    printf("Function vec_add [type integer]           ===> OK\n");

  err = 0;
  UIaux1.v = vec_add( UIcons1, UIcons3 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons3;
  for( i=0; i< 4; i++ )
  {
    UIaux = UIaux2.e[i]+UIaux3.e[i];
    if (UIaux1.e[i] != UIaux)
      err++;
  }
  if (err)
    printf("Function vec_add [type unsigned int]      ===> Error\n");
  else
    printf("Function vec_add [type unsigned int]      ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
  Faux1.v = vec_add( Fcons1, Fcons2 );
  Faux2.v = Fcons1;
  Faux3.v = Fcons2;
  for( i=0; i< 4; i++ )
  {
    Faux = Faux2.e[i]+Faux3.e[i];
    if (Faux1.e[i] != Faux)
      err++;
  }
  if (err)
    printf("Function vec_add [type float]             ===> Error\n");
  else
    printf("Function vec_add [type float]             ===> OK\n");
#endif


/*    Function vec_addc    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  UIaux1.v = vec_addc( UIcons1, UIcons3 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons3;
  for( i=0; i< 4; i++ )
  {
    UIaux = (unsigned int)(UIaux2.e[i]+UIaux3.e[i]);
    if ((UIaux< UIaux2.e[i]) || (UIaux< UIaux3.e[i]))
      UIaux=1;
    else
      UIaux=0;
    if (UIaux1.e[i] != UIaux)
      err++;
  }
  if (err)
    printf("Function vec_addc [type unsigned int]     ===> Error\n");
  else
    printf("Function vec_addc [type unsigned int]     ===> OK\n");

/*    Function vec_adds    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_adds( Ccons1, Ccons3 );
  Caux2.v = Ccons1;
  Caux3.v = Ccons3;
  for( i=0; i< 16; i++ )
  {
    Caux = Caux2.e[i]+Caux3.e[i];
    if ((Caux2.e[i]>0)&&(Caux3.e[i]>0))
    {
      if (Caux< 0)
        Caux=0x7F;
    }
    else if ((Caux2.e[i]<0)&&(Caux3.e[i]<0))
    {
      if (Caux> 0)
        Caux=0x80;
    } 
    if (Caux1.e[i] != Caux)
      err++;
  }
  if (err)
    printf("Function vec_adds [type char]             ===> Error\n");
  else
    printf("Function vec_adds [type char]             ===> OK\n");

  err = 0;
  UCaux1.v = vec_adds( UCcons1, UCcons3 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons3;
  for( i=0; i< 16; i++ )
  {
    UCaux = (unsigned char)(UCaux2.e[i]+UCaux3.e[i]);
    if ((UCaux< UCaux2.e[i]) || (UCaux< UCaux3.e[i]))
      UCaux=0xFF;
    if (UCaux1.e[i] != UCaux)
      err++;
  }
  if (err)
    printf("Function vec_adds [type unsigned char]    ===> Error\n");
  else
    printf("Function vec_adds [type unsigned char]    ===> OK\n");

  err = 0;
  Saux1.v = vec_adds( Scons1, Scons3 );
  Saux2.v = Scons1;
  Saux3.v = Scons3;
  for( i=0; i< 8; i++ )
  {
    Saux = Saux2.e[i]+Saux3.e[i];
    if ((Saux2.e[i]>0)&&(Saux3.e[i]>0))
    {
      if (Saux< 0)
        Saux=0x7FFF;
    }
    else if ((Saux2.e[i]<0)&&(Saux3.e[i]<0))
    {
      if (Saux> 0)
        Saux=0x8000;
    } 
    if (Saux1.e[i] != Saux)
      err++;
  }
  if (err)
    printf("Function vec_adds [type short]            ===> Error\n");
  else
    printf("Function vec_adds [type short]            ===> OK\n");

  err = 0;
  USaux1.v = vec_adds( UScons1, UScons3 );
  USaux2.v = UScons1;
  USaux3.v = UScons3;
  for( i=0; i< 8; i++ )
  {
    USaux = (unsigned short)(USaux2.e[i]+USaux3.e[i]);
    if ((USaux< USaux2.e[i]) || (USaux< USaux3.e[i]))
      USaux=0xFFFF;
    if (USaux1.e[i] != USaux)
      err++;
  }
  if (err)
    printf("Function vec_adds [type unsigned short]   ===> Error\n");
  else
    printf("Function vec_adds [type unsigned short]   ===> OK\n");


  err = 0;
  Iaux1.v = vec_adds( Icons1, Icons3 );
  Iaux2.v = Icons1;
  Iaux3.v = Icons3;
  for( i=0; i< 4; i++ )
  {
    Iaux = Iaux2.e[i]+Iaux3.e[i];
    if ((Iaux2.e[i]>0)&&(Iaux3.e[i]>0))
    {
      if (Iaux< 0)
        Iaux=0x7FFFFFFF;
    }
    else if ((Iaux2.e[i]<0)&&(Iaux3.e[i]<0))
    {
      if (Iaux> 0)
        Iaux=0x80000000;
    } 
    if (Iaux1.e[i] != Iaux)
      err++;
  }
  if (err)
    printf("Function vec_adds [type integer]          ===> Error\n");
  else
    printf("Function vec_adds [type integer]          ===> OK\n");

  err = 0;
  UIaux1.v = vec_adds( UIcons1, UIcons3 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons3;
  for( i=0; i< 4; i++ )
  {
    UIaux = (unsigned int)(UIaux2.e[i]+UIaux3.e[i]);
    if ((UIaux< UIaux2.e[i]) || (UIaux< UIaux3.e[i]))
      UIaux=0xFFFFFFFF;
    if (UIaux1.e[i] != UIaux)
      err++;
  }
  if (err)
    printf("Function vec_adds [type unsigned int]     ===> Error\n");
  else
    printf("Function vec_adds [type unsigned int]     ===> OK\n");

/*    Function vec_and    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_and( Ccons1, Ccons2 );
  Caux2.v = Ccons1;
  Caux3.v = Ccons2;
  for( i=0; i< 16; i++ )
    if (Caux1.e[i] != (Caux2.e[i] & Caux3.e[i]))
      err++;
  if (err)
    printf("Function vec_and [type char]              ===> Error\n");
  else
    printf("Function vec_and [type char]              ===> OK\n");

  err = 0;
  UCaux1.v = vec_and( UCcons1, UCcons2 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons2;
  for( i=0; i< 16; i++ )
    if (UCaux1.e[i] != (UCaux2.e[i] & UCaux3.e[i]))
      err++;
  if (err)
    printf("Function vec_and [type unsigned char]     ===> Error\n");
  else
    printf("Function vec_and [type unsigned char]     ===> OK\n");

  err = 0;
  Saux1.v = vec_and( Scons1, Scons2 );
  Saux2.v = Scons1;
  Saux3.v = Scons2;
  for( i=0; i< 8; i++ )
    if (Saux1.e[i] != (Saux2.e[i] & Saux3.e[i]))
      err++;
  if (err)
    printf("Function vec_and [type short]             ===> Error\n");
  else
    printf("Function vec_and [type short]             ===> OK\n");

  err = 0;
  USaux1.v = vec_and( UScons1, UScons2 );
  USaux2.v = UScons1;
  USaux3.v = UScons2;
  for( i=0; i< 8; i++ )
    if (USaux1.e[i] != (USaux2.e[i] & USaux3.e[i]))
      err++;
  if (err)
    printf("Function vec_and [type unsigned short]    ===> Error\n");
  else
    printf("Function vec_and [type unsigned short]    ===> OK\n");

  err = 0;
  Iaux1.v = vec_and( Icons1, Icons2 );
  Iaux2.v = Icons1;
  Iaux3.v = Icons2;
  for( i=0; i< 4; i++ )
    if (Iaux1.e[i] != (Iaux2.e[i] & Iaux3.e[i]))
      err++;
  if (err)
    printf("Function vec_and [type integer]           ===> Error\n");
  else
    printf("Function vec_and [type integer]           ===> OK\n");

  err = 0;
  UIaux1.v = vec_and( UIcons1, UIcons2 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons2;
  for( i=0; i< 4; i++ )
    if (UIaux1.e[i] != (UIaux2.e[i] & UIaux3.e[i]))
      err++;
  if (err)
    printf("Function vec_and [type unsigned int]      ===> Error\n");
  else
    printf("Function vec_and [type unsigned int]      ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
  Faux1.v = vec_and( Fcons1, Fcons2 );
  Faux2.v = Fcons1;
  Faux3.v = Fcons2;
  for( i=0; i< 4; i++ )
  {
    Ivec1 = Faux1.i[i];
    Ivec2 = Faux2.i[i];
    Ivec3 = Faux3.i[i];
    if ((Ivec1) != ((Ivec2) & (Ivec3)))
      err++;
  }
  if (err)
    printf("Function vec_and [type float]             ===> Error\n");
  else
    printf("Function vec_and [type float]             ===> OK\n");
#endif

/*    Function vec_andc    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_andc( Ccons1, Ccons2 );
  Caux2.v = Ccons1;
  Caux3.v = Ccons2;
  for( i=0; i< 16; i++ )
    if (Caux1.e[i] != (Caux2.e[i] & ~Caux3.e[i]))
      err++;
  if (err)
    printf("Function vec_andc [type char]             ===> Error\n");
  else
    printf("Function vec_andc [type char]             ===> OK\n");

  err = 0;
  UCaux1.v = vec_andc( UCcons1, UCcons2 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons2;
  for( i=0; i< 16; i++ )
    if (UCaux1.e[i] != (UCaux2.e[i] & ~UCaux3.e[i]))
      err++;
  if (err)
    printf("Function vec_andc [type unsigned char]    ===> Error\n");
  else
    printf("Function vec_andc [type unsigned char]    ===> OK\n");

  err = 0;
  Saux1.v = vec_andc( Scons1, Scons2 );
  Saux2.v = Scons1;
  Saux3.v = Scons2;
  for( i=0; i< 8; i++ )
    if (Saux1.e[i] != (Saux2.e[i] & ~Saux3.e[i]))
      err++;
  if (err)
    printf("Function vec_andc [type short]            ===> Error\n");
  else
    printf("Function vec_andc [type short]            ===> OK\n");

  err = 0;
  USaux1.v = vec_andc( UScons1, UScons2 );
  USaux2.v = UScons1;
  USaux3.v = UScons2;
  for( i=0; i< 8; i++ )
    if (USaux1.e[i] != (USaux2.e[i] & ~USaux3.e[i]))
      err++;
  if (err)
    printf("Function vec_andc [type unsigned short]   ===> Error\n");
  else
    printf("Function vec_andc [type unsigned short]   ===> OK\n");

  err = 0;
  Iaux1.v = vec_andc( Icons1, Icons2 );
  Iaux2.v = Icons1;
  Iaux3.v = Icons2;
  for( i=0; i< 4; i++ )
    if (Iaux1.e[i] != (Iaux2.e[i] & ~Iaux3.e[i]))
      err++;
  if (err)
    printf("Function vec_andc [type integer]          ===> Error\n");
  else
    printf("Function vec_andc [type integer]          ===> OK\n");

  err = 0;
  UIaux1.v = vec_andc( UIcons1, UIcons2 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons2;
  for( i=0; i< 4; i++ )
    if (UIaux1.e[i] != (UIaux2.e[i] & ~UIaux3.e[i]))
      err++;
  if (err)
    printf("Function vec_andc [type unsigned int]     ===> Error\n");
  else
    printf("Function vec_andc [type unsigned int]     ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
  Faux1.v = vec_andc( Fcons1, Fcons2 );
  Faux2.v = Fcons1;
  Faux3.v = Fcons2;
  for( i=0; i< 4; i++ )
  {
    Ivec1 = Faux1.i[i];
    Ivec2 = Faux2.i[i];
    Ivec3 = Faux3.i[i];
    if ((Ivec1) != ((Ivec2) & ~(Ivec3)))
      err++;
  }
  if (err)
    printf("Function vec_andc [type float]            ===> Error\n");
  else
    printf("Function vec_andc [type float]            ===> OK\n");
#endif

/*    Function vec_avg    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_avg( Ccons1, Ccons2 );
  Caux2.v = Ccons1;
  Caux3.v = Ccons2;
  for( i=0; i< 16; i++ )
  {
    j = (Caux2.e[i]+Caux3.e[i]+1) >> 1;
    if (Caux1.e[i] != j)
      err++;
  }
  if (err)
    printf("Function vec_avg [type char]              ===> Error\n");
  else
    printf("Function vec_avg [type char]              ===> OK\n");

  err = 0;
  UCaux1.v = vec_avg( UCcons1, UCcons2 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons2;
  for( i=0; i< 16; i++ )
  {
    j = (UCaux2.e[i]+UCaux3.e[i]+1) >> 1;
    if (UCaux1.e[i] != j)
      err++;
  }
  if (err)
    printf("Function vec_avg [type unsigned char]     ===> Error\n");
  else
    printf("Function vec_avg [type unsigned char]     ===> OK\n");

  err = 0;
  Saux1.v = vec_avg( Scons1, Scons2 );
  Saux2.v = Scons1;
  Saux3.v = Scons2;
  for( i=0; i< 8; i++ )
  {
    j = (Saux2.e[i]+Saux3.e[i]+1) >> 1;
    if (Saux1.e[i] != j)
      err++;
  }
  if (err)
    printf("Function vec_avg [type short]             ===> Error\n");
  else
    printf("Function vec_avg [type short]             ===> OK\n");

  err = 0;
  USaux1.v = vec_avg( UScons1, UScons2 );
  USaux2.v = UScons1;
  USaux3.v = UScons2;
  for( i=0; i< 8; i++ )
  {
    j = (USaux2.e[i]+USaux3.e[i]+1) >> 1;
    if (USaux1.e[i] != j)
      err++;
  }
  if (err)
    printf("Function vec_avg [type unsigned short]    ===> Error\n");
  else
    printf("Function vec_avg [type unsigned short]    ===> OK\n");

  err = 0;
  Iaux1.v = vec_avg( Icons1, Icons2 );
  Iaux2.v = Icons1;
  Iaux3.v = Icons2;
  for( i=0; i< 4; i++ )
  {
    Iaux = Iaux2.e[i]%2;
    if (Iaux2.e[i]<0)
      Iaux = -Iaux;

    if (Iaux3.e[i]<0)
      Iaux = (Iaux - Iaux3.e[i]%2 + 1)>>1;
    else
      Iaux = (Iaux + Iaux3.e[i]%2 + 1)>>1;
    Iaux = (Iaux2.e[i] >> 1) + (Iaux3.e[i] >> 1) + Iaux;
    if (Iaux1.e[i] != Iaux)
      err++;
  }
  if (err)
    printf("Function vec_avg [type integer]           ===> Error\n");
  else
    printf("Function vec_avg [type integer]           ===> OK\n");

  err = 0;
  UIaux1.v = vec_avg( UIcons1, UIcons2 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons2;
  for( i=0; i< 4; i++ )
  {
    UIaux = (UIaux2.e[i] >> 1) + (UIaux3.e[i] >> 1) +
            ((UIaux2.e[i]%2 + UIaux3.e[i]%2 + 1 )>>1);
    if (UIaux1.e[i] != UIaux)
      err++;
  }
  if (err)
    printf("Function vec_avg [type unsigned int]      ===> Error\n");
  else
    printf("Function vec_avg [type unsigned int]      ===> OK\n");

#if defined TEST_FLOATS
/*    Function vec_ceil    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Faux1.v = vec_ceil( Fcons1 );
  Faux2.v = Fcons1;
  for( i=0; i< 4; i++ )
    if (Faux1.e[i] != ceil(Faux2.e[i]))
      err++;
  if (err)
    printf("Function vec_ceil [type float]            ===> Error\n");
  else
    printf("Function vec_ceil [type float]            ===> OK\n");
#endif

#if defined TEST_FLOATS
/*    Function vec_cmpb    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Iaux1.v = vec_cmpb( Fcons1, Fcons2 );
  Faux2.v = Fcons1;
  Faux3.v = Fcons2;
  for( i=0; i< 4; i++ )
  {
    j = 0;
    if (Faux2.e[i]>Faux3.e[i])
     j+=(1 << 31);
    if (Faux2.e[i]<-Faux3.e[i])
     j+=(1 << 30);
    if (Iaux1.e[i] != j)
      err++;
  }

  if (err)
    printf("Function vec_cmpb [type float]            ===> Error\n");
  else
    printf("Function vec_cmpb [type float]            ===> OK\n");
#endif

/*    Function vec_cmpeq    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  BCaux1.v = vec_cmpeq( Ccons1, Ccons2 );
  Caux2.v = Ccons1;
  Caux3.v = Ccons2;
  for( i=0; i< 16; i++ )
  {
    if (Caux2.e[i] == Caux3.e[i])
      BCaux = 0xFF;
    else
      BCaux = 0;
    if (BCaux1.e[i] != BCaux)
      err++;
  }
  if (err)
    printf("Function vec_cmpeq [type char]            ===> Error\n");
  else
    printf("Function vec_cmpeq [type char]            ===> OK\n");

  err = 0;
  BCaux1.v = vec_cmpeq( UCcons1, UCcons2 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons2;
  for( i=0; i< 16; i++ )
  {
    if (UCaux2.e[i] == UCaux3.e[i])
      BCaux = 0xFF;
    else
      BCaux = 0;
    if (BCaux1.e[i] != BCaux)
      err++;
  }
  if (err)
    printf("Function vec_cmpeq [type unsigned char]   ===> Error\n");
  else
    printf("Function vec_cmpeq [type unsigned char]   ===> OK\n");

  err = 0;
  BSaux1.v = vec_cmpeq( Scons1, Scons2 );
  Saux2.v = Scons1;
  Saux3.v = Scons2;
  for( i=0; i< 8; i++ )
  {
    if (Saux2.e[i] == Saux3.e[i])
      BSaux = 0xFFFF;
    else
      BSaux = 0;
    if (BSaux1.e[i] != BSaux)
      err++;
  }
  if (err)
    printf("Function vec_cmpeq [type short]           ===> Error\n");
  else
    printf("Function vec_cmpeq [type short]           ===> OK\n");

  err = 0;
  BSaux1.v = vec_cmpeq( UScons1, UScons2 );
  USaux2.v = UScons1;
  USaux3.v = UScons2;
  for( i=0; i< 8; i++ )
  {
    if (USaux2.e[i] == USaux3.e[i])
      BSaux = 0xFFFF;
    else
      BSaux = 0;
    if (BSaux1.e[i] != BSaux)
      err++;
  }
  if (err)
    printf("Function vec_cmpeq [type unsigned short]  ===> Error\n");
  else
    printf("Function vec_cmpeq [type unsigned short]  ===> OK\n");

  err = 0;
  BIaux1.v = vec_cmpeq( Icons1, Icons2 );
  Iaux2.v = Icons1;
  Iaux3.v = Icons2;
  for( i=0; i< 4; i++ )
  {
    if (Iaux2.e[i] == Iaux3.e[i])
      BIaux = 0xFFFFFFFF;
    else
      BIaux = 0;
    if (BIaux1.e[i] != BIaux)
      err++;
  }
  if (err)
    printf("Function vec_cmpeq [type integer]         ===> Error\n");
  else
    printf("Function vec_cmpeq [type integer]         ===> OK\n");

  err = 0;
  BIaux1.v = vec_cmpeq( UIcons1, UIcons2 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons2;
  for( i=0; i< 4; i++ )
  {
    if (UIaux2.e[i] == UIaux3.e[i])
      BIaux = 0xFFFFFFFF;
    else
      BIaux = 0;
    if (BIaux1.e[i] != BIaux)
      err++;
  }
  if (err)
    printf("Function vec_cmpeq [type unsigned int]    ===> Error\n");
  else
    printf("Function vec_cmpeq [type unsigned int]    ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
  BIaux1.v = vec_cmpeq( Fcons1, Fcons2 );
  Faux2.v = Fcons1;
  Faux3.v = Fcons2;
  for( i=0; i< 4; i++ )
  {
    if (Faux2.e[i] == Faux3.e[i])
      BIaux = 0xFFFFFFFF;
    else
      BIaux = 0;
    if (BIaux1.e[i] != BIaux)
      err++;
  }
  if (err)
    printf("Function vec_cmpeq [type float]           ===> Error\n");
  else
    printf("Function vec_cmpeq [type float]           ===> OK\n");
#endif

#if defined TEST_FLOATS
/*    Function vec_cmpge    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  BIaux1.v = vec_cmpge( Fcons1, Fcons2 );
  Faux2.v = Fcons1;
  Faux3.v = Fcons2;
  for( i=0; i< 4; i++ )
  {
    if (Faux2.e[i] >= Faux3.e[i])
      BIaux = 0xFFFFFFFF;
    else
      BIaux = 0;
    if (BIaux1.e[i] != BIaux)
      err++;
  }
  if (err)
    printf("Function vec_cmpge [type float]           ===> Error\n");
  else
    printf("Function vec_cmpge [type float]           ===> OK\n");
#endif

/*    Function vec_cmpgt    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  BCaux1.v = vec_cmpgt( Ccons1, Ccons2 );
  Caux2.v = Ccons1;
  Caux3.v = Ccons2;
  for( i=0; i< 16; i++ )
  {
    if (Caux2.e[i] > Caux3.e[i])
      BCaux = 0xFF;
    else
      BCaux = 0;
    if (BCaux1.e[i] != BCaux)
      err++;
  }
  if (err)
    printf("Function vec_cmpgt [type char]            ===> Error\n");
  else
    printf("Function vec_cmpgt [type char]            ===> OK\n");

  err = 0;
  BCaux1.v = vec_cmpgt( UCcons1, UCcons2 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons2;
  for( i=0; i< 16; i++ )
  {
    if (UCaux2.e[i] > UCaux3.e[i])
      BCaux = 0xFF;
    else
      BCaux = 0;
    if (BCaux1.e[i] != BCaux)
      err++;
  }
  if (err)
    printf("Function vec_cmpgt [type unsigned char]   ===> Error\n");
  else
    printf("Function vec_cmpgt [type unsigned char]   ===> OK\n");

  err = 0;
  BSaux1.v = vec_cmpgt( Scons1, Scons2 );
  Saux2.v = Scons1;
  Saux3.v = Scons2;
  for( i=0; i< 8; i++ )
  {
    if (Saux2.e[i] > Saux3.e[i])
      BSaux = 0xFFFF;
    else
      BSaux = 0;
    if (BSaux1.e[i] != BSaux)
      err++;
  }
  if (err)
    printf("Function vec_cmpgt [type short]           ===> Error\n");
  else
    printf("Function vec_cmpgt [type short]           ===> OK\n");

  err = 0;
  BSaux1.v = vec_cmpgt( UScons1, UScons2 );
  USaux2.v = UScons1;
  USaux3.v = UScons2;
  for( i=0; i< 8; i++ )
  {
    if (USaux2.e[i] > USaux3.e[i])
      BSaux = 0xFFFF;
    else
      BSaux = 0;
    if (BSaux1.e[i] != BSaux)
      err++;
  }
  if (err)
    printf("Function vec_cmpgt [type unsigned short]  ===> Error\n");
  else
    printf("Function vec_cmpgt [type unsigned short]  ===> OK\n");

  err = 0;
  BIaux1.v = vec_cmpgt( Icons1, Icons2 );
  Iaux2.v = Icons1;
  Iaux3.v = Icons2;
  for( i=0; i< 4; i++ )
  {
    if (Iaux2.e[i] > Iaux3.e[i])
      BIaux = 0xFFFFFFFF;
    else
      BIaux = 0;
    if (BIaux1.e[i] != BIaux)
      err++;
  }
  if (err)
    printf("Function vec_cmpgt [type integer]         ===> Error\n");
  else
    printf("Function vec_cmpgt [type integer]         ===> OK\n");

  err = 0;
  BIaux1.v = vec_cmpgt( UIcons1, UIcons2 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons2;
  for( i=0; i< 4; i++ )
  {
    if (UIaux2.e[i] > UIaux3.e[i])
      BIaux=0xFFFFFFFF;
    else
      BIaux = 0;
    if (BIaux1.e[i] != BIaux)
      err++;
  }
  if (err)
    printf("Function vec_cmpgt [type unsigned int]    ===> Error\n");
  else
    printf("Function vec_cmpgt [type unsigned int]    ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
  BIaux1.v = vec_cmpgt( Fcons1, Fcons2 );
  Faux2.v = Fcons1;
  Faux3.v = Fcons2;
  for( i=0; i< 4; i++ )
  {
    if (Faux2.e[i] > Faux3.e[i])
      BIaux = 0xFFFFFFFF;
    else
      BIaux = 0;
    if (BIaux1.e[i] != BIaux)
      err++;
  }
  if (err)
    printf("Function vec_cmpgt [type float]           ===> Error\n");
  else
    printf("Function vec_cmpgt [type float]           ===> OK\n");
#endif

#if defined TEST_FLOATS
/*    Function vec_cmple    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  BIaux1.v = vec_cmple( Fcons1, Fcons2 );
  Faux2.v = Fcons1;
  Faux3.v = Fcons2;
  for( i=0; i< 4; i++ )
  {
    if (Faux2.e[i] <= Faux3.e[i])
      BIaux = 0xFFFFFFFF;
    else
      BIaux = 0;
    if (BIaux1.e[i] != BIaux)
      err++;
  }
  if (err)
    printf("Function vec_cmple [type float]           ===> Error\n");
  else
    printf("Function vec_cmple [type float]           ===> OK\n");
#endif

/*    Function vec_cmplt    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  BCaux1.v = vec_cmplt( Ccons1, Ccons2 );
  Caux2.v = Ccons1;
  Caux3.v = Ccons2;
  for( i=0; i< 16; i++ )
  {
    if (Caux2.e[i] < Caux3.e[i])
      BCaux = 0xFF;
    else
      BCaux = 0;
    if (BCaux1.e[i] != BCaux)
      err++;
  }
  if (err)
    printf("Function vec_cmplt [type char]            ===> Error\n");
  else
    printf("Function vec_cmplt [type char]            ===> OK\n");

  err = 0;
  BCaux1.v = vec_cmplt( UCcons1, UCcons2 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons2;
  for( i=0; i< 16; i++ )
  {
    if (UCaux2.e[i] < UCaux3.e[i])
      BCaux = 0xFF;
    else
      BCaux = 0;
    if (BCaux1.e[i] != BCaux)
      err++;
  }
  if (err)
    printf("Function vec_cmplt [type unsigned char]   ===> Error\n");
  else
    printf("Function vec_cmplt [type unsigned char]   ===> OK\n");

  err = 0;
  BSaux1.v = vec_cmplt( Scons1, Scons2 );
  Saux2.v = Scons1;
  Saux3.v = Scons2;
  for( i=0; i< 8; i++ )
  {
    if (Saux2.e[i] < Saux3.e[i])
      BSaux = 0xFFFF;
    else
      BSaux = 0;
    if (BSaux1.e[i] != BSaux)
      err++;
  }
  if (err)
    printf("Function vec_cmplt [type short]           ===> Error\n");
  else
    printf("Function vec_cmplt [type short]           ===> OK\n");

  err = 0;
  BSaux1.v = vec_cmplt( UScons1, UScons2 );
  USaux2.v = UScons1;
  USaux3.v = UScons2;
  for( i=0; i< 8; i++ )
  {
    if (USaux2.e[i] < USaux3.e[i])
      BSaux = 0xFFFF;
    else
      BSaux = 0;
    if (BSaux1.e[i] != BSaux)
      err++;
  }
  if (err)
    printf("Function vec_cmplt [type unsigned short]  ===> Error\n");
  else
    printf("Function vec_cmplt [type unsigned short]  ===> OK\n");

  err = 0;
  BIaux1.v = vec_cmplt( Icons1, Icons2 );
  Iaux2.v = Icons1;
  Iaux3.v = Icons2;
  for( i=0; i< 4; i++ )
  {
    if (Iaux2.e[i] < Iaux3.e[i])
      BIaux = 0xFFFFFFFF;
    else
      BIaux = 0;
    if (BIaux1.e[i] != BIaux)
      err++;
  }
  if (err)
    printf("Function vec_cmplt [type integer]         ===> Error\n");
  else
    printf("Function vec_cmplt [type integer]         ===> OK\n");

  err = 0;
  BIaux1.v = vec_cmplt( UIcons1, UIcons2 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons2;
  for( i=0; i< 4; i++ )
  {
    if (UIaux2.e[i] < UIaux3.e[i])
      BIaux=0xFFFFFFFF;
    else
      BIaux = 0;
    if (BIaux1.e[i] != BIaux)
      err++;
  }
  if (err)
    printf("Function vec_cmplt [type unsigned int]    ===> Error\n");
  else
    printf("Function vec_cmplt [type unsigned int]    ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
  BIaux1.v = vec_cmplt( Fcons1, Fcons2 );
  Faux2.v = Fcons1;
  Faux3.v = Fcons2;
  for( i=0; i< 4; i++ )
  {
    if (Faux2.e[i] < Faux3.e[i])
      BIaux = 0xFFFFFFFF;
    else
      BIaux = 0;
    if (BIaux1.e[i] != BIaux)
      err++;
  }
  if (err)
    printf("Function vec_cmplt [type float]           ===> Error\n");
  else
    printf("Function vec_cmplt [type float]           ===> OK\n");
#endif

#if defined TEST_FLOATS
/*    Function vec_ctf    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  b   = 2;
  Faux1.v = vec_ctf( Icons1, 2 );
  Iaux1.v = Icons1;
  for( i=0; i< 4; i++ )
    if (Faux1.e[i] != (((float)Iaux1.e[i])/(1<<b)))
      err++;
  if (err)
    printf("Function vec_ctf [type integer]           ===> Error\n");
  else
    printf("Function vec_ctf [type integer]           ===> OK\n");

  err = 0;
  b   = 2;
  Faux1.v = vec_ctf( UIcons1, 2 );
  UIaux1.v = UIcons1;
  for( i=0; i< 4; i++ )
    if (Faux1.e[i] != (((float)UIaux1.e[i])/(1<<b)))
      err++;
  if (err)
    printf("Function vec_ctf [type unsigned int]      ===> Error\n");
  else
    printf("Function vec_ctf [type unsigned int]      ===> OK\n");
#endif

#if defined TEST_FLOATS
/*    Function vec_cts    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  b   = 2;
  Iaux1.v = vec_cts( Fcons3, 2 );
  Faux1.v = Fcons3;
  for( i=0; i< 4; i++ )
    if (Iaux1.e[i] != (int)(Faux1.e[i]*(1<<b)))
      err++;
  if (err)
    printf("Function vec_cts [type float]             ===> Error\n");
  else
    printf("Function vec_cts [type float]             ===> OK\n");
#endif

#if defined TEST_FLOATS
/*    Function vec_ctu    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  b   = 2;
  UIaux1.v = vec_ctu( Fcons3, 2 );
  Faux1.v = Fcons3;
  for( i=0; i< 4; i++ )
    {
      double d = Faux1.e[i]*(1<<b);
      if (d > 0xffffffff)
	d = 0xffffffff;
      if (d < 0)
	d = 0;
      if (UIaux1.e[i] != (unsigned int)(d))
        err++;
    }
  if (err)
    printf("Function vec_ctu [type float]             ===> Error\n");
  else
    printf("Function vec_ctu [type float]             ===> OK\n");
#endif

  part1();

  part2();

  part3();

  part4();
  
  part5();

  return 0;
}




int part1()
{
  TvecChar      Caux1;//,  Caux2,  Caux3,  Caux4;
  TvecUChar     UCaux1;//, UCaux2, UCaux3, UCaux4;
  TvecShort     Saux1;//,  Saux2,  Saux3,  Saux4;
  TvecUShort    USaux1;//, USaux2, USaux3, USaux4;
  TvecInt       Iaux1;//,  Iaux2,  Iaux3,  Iaux4;
  TvecUInt      UIaux1;//, UIaux2, UIaux3, UIaux4;
#if defined TEST_FLOATS
  TvecFloat     Faux1,  Faux2;//,  Faux3,  Faux4;
#endif

  int                  i, err, j;//, b, bAux;
//  signed   int         Ivec1, Ivec2, Ivec3;
//  signed   short       *Svec1;
//  unsigned int         *UIvec1;
//  unsigned short       *USvec1;
//  unsigned char        *UCvec1;
#if defined TEST_FLOATS
//  float                *Fvec1;
#endif

  /* For saturated rutines */
//  long long int         LLaux;

#if defined TEST_FLOATS
  float                 Faux;
#endif
  signed   int          Iaux;//, I1, I2;
//  unsigned int          UIaux, UI1, UI2;
//  signed   short        Saux;
//  unsigned short        USaux;
//  signed   char         Caux;
//  unsigned char         UCaux;

/*
  union
  {
    float          f;
    signed   int   si;
    unsigned int   ui;
    signed   short ss[2];
    unsigned short us[2];
    signed   char  sc[4];
    unsigned char  uc[4];
  } INTunion1, INTunion2;

  union
  {
    signed   short  ss;
    unsigned short  us;
    signed   char   sc[2];
    unsigned char   uc[2];
  } SHOunion1, SHOunion2;
*/

#if defined (GCC_COMPILER)
  vector signed char    Ccons1   = (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
//  vector signed char    Ccons2   = (vector signed char){1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1};
//  vector signed char    Ccons3   = (vector signed char){-128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127};
  vector unsigned char  UCcons1  = (vector unsigned char){248, 249, 250, 251, 252, 253, 254, 255, 0, 1, 2, 3, 4, 5, 6, 7};
//  vector unsigned char  UCcons2  = (vector unsigned char){2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2};
//  vector unsigned char  UCcons3  = (vector unsigned char){1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8};
  vector signed short   Scons1   = (vector signed short){-4, -3, -2, -1, 0, 1, 2, 3};
//  vector signed short   Scons2   = (vector signed short){-32768, 10000, 1, 1, 1, 1, -10000, -10000};
//  vector signed short   Scons3   = (vector signed short){-32768, 32767, -32768, 32767, -32768, 32767, -32768, 32767};
//  vector unsigned short UScons1  = (vector unsigned short){65532, 65533, 65534, 65535, 0, 1, 2, 3};
//  vector unsigned short UScons2  = (vector unsigned short){1, 1, 1, 1, 1, 1, 1, 1};
  vector unsigned short UScons3  = (vector unsigned short){1, 2, 3, 4, 1, 2, 3, 4};
  vector signed int     Icons1   = (vector signed int){-4, -1, 1, 4};
//  vector signed int     Icons2   = (vector signed int){1, 1, 1, 1};
//  vector signed int     Icons3   = (vector signed int){0x80000000, 0x7FFFFFFF, 0x80000000, 0x7FFFFFFF};
  vector unsigned int   UIcons1  = (vector unsigned int){0xFFFFFFFE, 0xFFFFFFFF, 0, 1};
//  vector unsigned int   UIcons2  = (vector unsigned int){1, 1, 1, 1};
//  vector unsigned int   UIcons3  = (vector unsigned int){1, 2, 1, 2};

#if defined TEST_FLOATS
  vector float          Fcons1   = (vector float){-1.5, 1.0, 0.5, -3.999};
//  vector float          Fcons2   = (vector float){1.0, 1.0, 1.0, 1.0};
  vector float          Fcons3   = (vector float){100000000000.0, 1.0, -1.0, -1234567890.0};
#endif

#elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
  vector signed char    Ccons1   = (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
  vector signed char    Ccons2   = (vector signed char)(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1);
  vector signed char    Ccons3   = (vector signed char)(-128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127);
  vector unsigned char  UCcons1  = (vector unsigned char)(248, 249, 250, 251, 252, 253, 254, 255, 0, 1, 2, 3, 4, 5, 6, 7);
  vector unsigned char  UCcons2  = (vector unsigned char)(2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2);
  vector unsigned char  UCcons3  = (vector unsigned char)(1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8);
  vector signed short   Scons1   = (vector signed short)(-4, -3, -2, -1, 0, 1, 2, 3);
  vector signed short   Scons2   = (vector signed short)(-32768, 10000, 1, 1, 1, 1, -10000, -10000);
  vector signed short   Scons3   = (vector signed short)(-32768, 32767, -32768, 32767, -32768, 32767, -32768, 32767);
  vector unsigned short UScons1  = (vector unsigned short)(65532, 65533, 65534, 65535, 0, 1, 2, 3);
  vector unsigned short UScons2  = (vector unsigned short)(1, 1, 1, 1, 1, 1, 1, 1);
  vector unsigned short UScons3  = (vector unsigned short)(1, 2, 3, 4, 1, 2, 3, 4);
  vector signed int     Icons1   = (vector signed int)(-4, -1, 1, 4);
  vector signed int     Icons2   = (vector signed int)(1, 1, 1, 1);
  vector signed int     Icons3   = (vector signed int)(0x80000000, 0x7FFFFFFF, 0x80000000, 0x7FFFFFFF);
  vector unsigned int   UIcons1  = (vector unsigned int)(0xFFFFFFFE, 0xFFFFFFFF, 0, 1);
  vector unsigned int   UIcons2  = (vector unsigned int)(1, 1, 1, 1);
  vector unsigned int   UIcons3  = (vector unsigned int)(1, 2, 1, 2);

#if defined TEST_FLOATS
  vector float          Fcons1   = (vector float)(-1.5, 1.0, 0.5, -3.999);
  vector float          Fcons2   = (vector float)(1.0, 1.0, 1.0, 1.0);
  vector float          Fcons3   = (vector float)(100000000000.0, 1.0, -1.0, -1234567890.0);
#endif

#endif


/* Variables to be allocated with calloc_vec (16 bytes aligned) */
  unsigned char   *UCmem = (unsigned char*)calloc_vec( 1, sizeof(vector unsigned char) );
  signed char     *Cmem  = (signed char*)calloc_vec( 1, sizeof(vector signed char) );
  unsigned short  *USmem = (unsigned short*)calloc_vec( 1, sizeof(vector unsigned short) );
  signed short    *Smem  = (signed short*)calloc_vec( 1, sizeof(vector signed short) );
  unsigned int    *UImem = (unsigned int*)calloc_vec( 1, sizeof(vector unsigned int) );
  signed int      *Imem  = (signed int*)calloc_vec( 1, sizeof(vector signed int) );
#if defined TEST_FLOATS
  float           *Fmem  = (float*)calloc_vec( 1, sizeof(vector float) );
#endif

/*    Function vec_dss    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  printf("Function vec_dss [Vector data Stream Stop] not checked\n");

/*    Function vec_dssall    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  printf("Function vec_dssall [Vector Stream Stop all] not checked\n");

/*    Function vec_dst    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  printf("Function vec_dst [Vector Data Stream Touch] not checked\n");

/*    Function vec_dstst    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  printf("Function vec_dstst [Vector Data Stream Touch for Store] not checked\n");
 
/*    Function vec_dststt    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  printf("Function vec_dststt [Vector Data Stream Touch for Store Transient] not checked\n");

/*    Function vec_dstt    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  printf("Function vec_dstt [Vector Data Stream Touch Transient] not checked\n");

#if defined TEST_FLOATS
/*    Function vec_expte    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Faux1.v = vec_expte( Fcons1 );
  Faux2.v = Fcons1;
  for( i=0; i< 4; i++ )
  {
    Faux = pow(2,Faux2.e[i]);
/*
    Ivec1 = (signed int*)(&Faux1.e[i]);
    Ivec2 = (signed int*)(&Faux);
    *Ivec1 = (*Ivec1) & 0xFFF00000;
    *Ivec2 = (*Ivec2) & 0xFFF00000;
    if (Faux1.e[i] != Faux)
      err++;
*/
    Faux = (Faux - Faux1.e[i])/Faux;
    if (Faux>0.1)
      err++;
  }
  if (err)
    printf("Function vec_expte [type float]           ===> Error\n");
  else
    printf("Function vec_expte [type float]           ===> OK\n");
#endif

#if defined TEST_FLOATS
/*    Function vec_floor    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Faux1.v = vec_floor( Fcons1 );
  Faux2.v = Fcons1;
  for( i=0; i< 4; i++ )
    if (Faux1.e[i] != floor(Faux2.e[i]))
      err++;
  if (err)
    printf("Function vec_floor [type float]           ===> Error\n");
  else
    printf("Function vec_floor [type float]           ===> OK\n");
#endif

/*    Function vec_ld    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  memcpy( UCmem, &UCcons1, sizeof(vector unsigned char) );
  UCaux1.v = vec_ld( 0, UCmem );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (UCaux1.e[i]==UCmem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_ld [type unsigned char]      ===> Error\n");
  else
    printf("Function vec_ld [type unsigned char]      ===> OK\n");
  
  err = 0;
  memcpy( Cmem, &Ccons1, sizeof(vector signed char) );
  Caux1.v = vec_ld( 0, Cmem );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (Caux1.e[i]==Cmem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_ld [type char]               ===> Error\n");
  else
    printf("Function vec_ld [type char]               ===> OK\n");
  
  err = 0;
  memcpy( USmem, &UScons3, sizeof(vector unsigned short) );
  USaux1.v = vec_ld( 0, USmem );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (USaux1.e[i]==USmem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_ld [type unsigned short]     ===> Error\n");
  else
    printf("Function vec_ld [type unsigned short]     ===> OK\n");
  
  err = 0;
  memcpy( Smem, &Scons1, sizeof(vector signed short) );
  Saux1.v = vec_ld( 0, Smem );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (Saux1.e[i]==Smem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_ld [type short]              ===> Error\n");
  else
    printf("Function vec_ld [type short]              ===> OK\n");
  
  err = 0;
  memcpy( UImem, &UIcons1, sizeof(vector unsigned int) );
  UIaux1.v = vec_ld( 0, UImem );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (UIaux1.e[i]==UImem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_ld [type unsigned int]       ===> Error\n");
  else
    printf("Function vec_ld [type unsigned int]       ===> OK\n");
  
  err = 0;
  memcpy( Imem, &Icons1, sizeof(vector signed int) );
  Iaux1.v = vec_ld( 0, Imem );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Iaux1.e[i]==Imem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_ld [type int]                ===> Error\n");
  else
    printf("Function vec_ld [type int]                ===> OK\n");
  
#if defined TEST_FLOATS
  err = 0;
  memcpy( Fmem, &Fcons1, sizeof(vector float) );
  Faux1.v = vec_ld( 0, Fmem );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Faux1.e[i]==Fmem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_ld [type float]              ===> Error\n");
  else
    printf("Function vec_ld [type float]              ===> OK\n");
#endif

/*    Function vec_lde    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");

  err = 0;
  for (i= 0; i< 16; i++)
    UCmem[i] = (unsigned char)i;
  j = 1;   
  i = j*sizeof(unsigned char);
  UCaux1.v = vec_lde( i, UCmem );
  
  if (UCaux1.e[j] != UCmem[j]) err++;
  
  if (err)
    printf("Function vec_lde [type unsigned char]     ===> Error\n");
  else
    printf("Function vec_lde [type unsigned char]     ===> OK\n");
  
  err = 0;
  for (i= 0; i< 16; i++)
    Cmem[i] = (char)(-i);
  j = 1;   
  i = j*sizeof(char);
  Caux1.v = vec_lde( i, Cmem );
  
  if (Caux1.e[j] != Cmem[j]) err++;
  
  if (err)
    printf("Function vec_lde [type char]              ===> Error\n");
  else
    printf("Function vec_lde [type char]              ===> OK\n");
  
  err = 0;
  for (i= 0; i< 8; i++)
    USmem[i] = (unsigned short)(i);
  j = 1;   
  i = j*sizeof(unsigned short);
  USaux1.v = vec_lde( i, USmem );
  
  if (USaux1.e[j] != USmem[j]) err++;
  
  if (err)
    printf("Function vec_lde [type unsigned short]    ===> Error\n");
  else
    printf("Function vec_lde [type unsigned short]    ===> OK\n");
  
  err = 0;
  for (i= 0; i< 8; i++)
    Smem[i] = (short)(-i);
  j = 1;   
  i = j*sizeof(short);
  Saux1.v = vec_lde( i, Smem );
  
  if (Saux1.e[j] != Smem[j]) err++;

  if (err)
    printf("Function vec_lde [type short]             ===> Error\n");
  else
    printf("Function vec_lde [type short]             ===> OK\n");
  
  err = 0;
  for (i= 0; i< 4; i++)
    UImem[i] = (unsigned int)(i);
  j = 1;   
  i = j*sizeof(unsigned int);
  UIaux1.v = vec_lde( i, UImem );
  
  if (UIaux1.e[j] != UImem[j]) err++;
  
  if (err)
    printf("Function vec_lde [type unsigned int]      ===> Error\n");
  else
    printf("Function vec_lde [type unsigned int]      ===> OK\n");
  
  err = 0;
  for (i= 0; i< 4; i++)
    Imem[i] = (int)(-i);
  j = 1;   
  i = j*sizeof(int);
  Iaux1.v = vec_lde( i, Imem );
  
  if (Iaux1.e[j] != Imem[j]) err++;
  
  if (err)
    printf("Function vec_lde [type int]               ===> Error\n");
  else
    printf("Function vec_lde [type int]               ===> OK\n");
  
#if defined TEST_FLOATS
  err = 0;
  for (i= 0; i< 4; i++)
    Fmem[i] = ((float)(-i)) - 0.5;
  j = 1;   
  i = j*sizeof(float);
  Faux1.v = vec_lde( i, Fmem );
  
  if (Faux1.e[j] != Fmem[j]) err++;
  
  if (err)
    printf("Function vec_lde [type float]             ===> Error\n");
  else
    printf("Function vec_lde [type float]             ===> OK\n");
#endif

#if 0
/*    Function vec_ldl    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  memcpy( UCmem, &UCcons1, sizeof(vector unsigned char) );
  UCaux1.v = vec_ldl( 0, UCmem );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (UCaux1.e[i]==UCmem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_ldl [type unsigned char]     ===> Error\n");
  else
    printf("Function vec_ldl [type unsigned char]     ===> OK\n");

  err = 0;
  memcpy( Cmem, &Ccons1, sizeof(vector signed char) );
  Caux1.v = vec_ldl( 0, Cmem );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (Caux1.e[i]==Cmem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_ldl [type char]              ===> Error\n");
  else
    printf("Function vec_ldl [type char]              ===> OK\n");
  
  err = 0;
  memcpy( USmem, &UScons3, sizeof(vector unsigned short) );
  USaux1.v = vec_ldl( 0, USmem );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (USaux1.e[i]==USmem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_ldl [type unsigned short]    ===> Error\n");
  else
    printf("Function vec_ldl [type unsigned short]    ===> OK\n");
  
  err = 0;
  memcpy( Smem, &Scons1, sizeof(vector signed short) );
  Saux1.v = vec_ldl( 0, Smem );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (Saux1.e[i]==Smem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_ldl [type short]             ===> Error\n");
  else
    printf("Function vec_ldl [type short]             ===> OK\n");
  
  err = 0;
  memcpy( UImem, &UIcons1, sizeof(vector unsigned int) );
  UIaux1.v = vec_ldl( 0, UImem );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (UIaux1.e[i]==UImem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_ldl [type unsigned int]      ===> Error\n");
  else
    printf("Function vec_ldl [type unsigned int]      ===> OK\n");
  
  err = 0;
  memcpy( Imem, &Icons1, sizeof(vector signed int) );
  Iaux1.v = vec_ldl( 0, Imem );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Iaux1.e[i]==Imem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_ldl [type int]               ===> Error\n");
  else
    printf("Function vec_ldl [type int]               ===> OK\n");
  
#if defined TEST_FLOATS
  err = 0;
  memcpy( Fmem, &Fcons1, sizeof(vector float) );
  Faux1.v = vec_ldl( 0, Fmem );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Faux1.e[i]==Fmem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_ldl [type float]             ===> Error\n");
  else
    printf("Function vec_ldl [type float]             ===> OK\n");
#endif
#endif  // #if 0

  /* Free dynamic vector variables */
  free_vec( UCmem );
  free_vec( Cmem );
  free_vec( USmem );
  free_vec( Smem );
  free_vec( UImem );
  free_vec( Imem );
#if defined TEST_FLOATS
  free_vec( Fmem );
#endif

#if defined TEST_FLOATS
/*    Function vec_loge    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Faux1.v = vec_loge( Fcons3 );
  Faux2.v = Fcons3;
  for( i=0; i< 4; i++ )
  {
    Faux = log2(Faux2.e[i]);
    if (Faux!=0.0)
      Faux = (Faux - Faux1.e[i])/Faux;
    else
      Faux = Faux - Faux1.e[i];
    if (Faux>0.1)
      err++;
  }
  if (err)
    printf("Function vec_loge [type float]            ===> Error\n");
  else
    printf("Function vec_loge [type float]            ===> OK\n");
#endif

  return 0;
}




int part2()
{
  TvecChar      Caux1,  Caux2,  Caux3;//,  Caux4;
  TvecUChar     UCaux1, UCaux2, UCaux3;//, UCaux4;
  TvecShort     Saux1,  Saux2,  Saux3,  Saux4;
  TvecUShort    USaux1, USaux2, USaux3, USaux4;
  TvecInt       Iaux1,  Iaux2,  Iaux3;//,  Iaux4;
  TvecUInt      UIaux1, UIaux2, UIaux3;//, UIaux4;
#if defined TEST_FLOATS
  TvecFloat     Faux1,  Faux2,  Faux3,  Faux4;
#endif

  int                  i, err, j, b, bAux;
#if defined TEST_FLOATS
  signed   int         Ivec1, Ivec2, Ivec3;
#endif
//  signed   short       *Svec1;
//  unsigned int         *UIvec1;
//  unsigned short       *USvec1;
//  unsigned char        *UCvec1;
#if defined TEST_FLOATS
//  float                *Fvec1;
#endif

  /* For saturated rutines */
//  long long int         LLaux;

#if defined TEST_FLOATS
  float                 Faux;
#endif
  signed   int          Iaux, I1, I2;
  unsigned int          UIaux, UI1, UI2;
  signed   short        Saux;
  unsigned short        USaux;
  signed   char         Caux;
  unsigned char         UCaux;

  union
  {
    float          f;
    signed   int   si;
    unsigned int   ui;
    signed   short ss[2];
    unsigned short us[2];
    signed   char  sc[4];
    unsigned char  uc[4];
  } INTunion1;//, INTunion2;

/*
  union
  {
    signed   short  ss;
    unsigned short  us;
    signed   char   sc[2];
    unsigned char   uc[2];
  } SHOunion1, SHOunion2;
*/

#if defined (GCC_COMPILER)
  vector signed char    Ccons1   = (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
  vector signed char    Ccons2   = (vector signed char){1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1};
//  vector signed char    Ccons3   = (vector signed char){-128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127};
  vector unsigned char  UCcons1  = (vector unsigned char){248, 249, 250, 251, 252, 253, 254, 255, 0, 1, 2, 3, 4, 5, 6, 7};
  vector unsigned char  UCcons2  = (vector unsigned char){2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2};
//  vector unsigned char  UCcons3  = (vector unsigned char){1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8};
  vector signed short   Scons1   = (vector signed short){256, 320, 340, -1, 0, 1, 2, 3};
  vector signed short   Scons2   = (vector signed short){256, 320, 340, 1, 1, 1, -10000, -10000};
  vector signed short   Scons3   = (vector signed short){256, 320, 340, 32767, -32768, 32767, -32768, 32767};
  vector unsigned short UScons1  = (vector unsigned short){65532, 65533, 65534, 65535, 0, 1, 2, 3};
  vector unsigned short UScons2  = (vector unsigned short){1, 1, 1, 1, 1, 1, 1, 1};
  vector unsigned short UScons3  = (vector unsigned short){1, 2, 3, 4, 1, 2, 3, 4};
  vector signed int     Icons1   = (vector signed int){-4, -1, 1, 4};
  vector signed int     Icons2   = (vector signed int){1, 1, 1, 1};
  vector signed int     Icons3   = (vector signed int){0x80000000, 0x7FFFFFFF, 0x80000000, 0x7FFFFFFF};
  vector unsigned int   UIcons1  = (vector unsigned int){0xFFFFFFFE, 0xFFFFFFFF, 0, 1};
  vector unsigned int   UIcons2  = (vector unsigned int){1, 1, 1, 1};
  vector unsigned int   UIcons3  = (vector unsigned int){1, 2, 1, 2};

#if defined TEST_FLOATS
  vector float          Fcons1   = (vector float){-1.5, 1.0, 0.5, -3.999};
  vector float          Fcons2   = (vector float){1.0, 1.0, 1.0, 1.0};
  vector float          Fcons3   = (vector float){100000000000.0, 1.0, -1.0, -1234567890.0};
#endif

#elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
  vector signed char    Ccons1   = (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
  vector signed char    Ccons2   = (vector signed char)(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1);
  vector signed char    Ccons3   = (vector signed char)(-128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127);
  vector unsigned char  UCcons1  = (vector unsigned char)(248, 249, 250, 251, 252, 253, 254, 255, 0, 1, 2, 3, 4, 5, 6, 7);
  vector unsigned char  UCcons2  = (vector unsigned char)(2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2);
//  vector unsigned char  UCcons3  = (vector unsigned char)(1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8);
  vector signed short   Scons1   = (vector signed short)(-4, -3, -2, -1, 0, 1, 2, 3);
  vector signed short   Scons2   = (vector signed short)(-32768, 10000, 1, 1, 1, 1, -10000, -10000);
  vector signed short   Scons3   = (vector signed short)(-32768, 32767, -32768, 32767, -32768, 32767, -32768, 32767);
  vector unsigned short UScons1  = (vector unsigned short)(65532, 65533, 65534, 65535, 0, 1, 2, 3);
  vector unsigned short UScons2  = (vector unsigned short)(1, 1, 1, 1, 1, 1, 1, 1);
  vector unsigned short UScons3  = (vector unsigned short)(1, 2, 3, 4, 1, 2, 3, 4);
  vector signed int     Icons1   = (vector signed int)(-4, -1, 1, 4);
  vector signed int     Icons2   = (vector signed int)(1, 1, 1, 1);
  vector signed int     Icons3   = (vector signed int)(0x80000000, 0x7FFFFFFF, 0x80000000, 0x7FFFFFFF);
  vector unsigned int   UIcons1  = (vector unsigned int)(0xFFFFFFFE, 0xFFFFFFFF, 0, 1);
  vector unsigned int   UIcons2  = (vector unsigned int)(1, 1, 1, 1);
  vector unsigned int   UIcons3  = (vector unsigned int)(1, 2, 1, 2);

#if defined TEST_FLOATS
  vector float          Fcons1   = (vector float)(-1.5, 1.0, 0.5, -3.999);
  vector float          Fcons2   = (vector float)(1.0, 1.0, 1.0, 1.0);
  vector float          Fcons3   = (vector float)(100000000000.0, 1.0, -1.0, -1234567890.0);
#endif

#endif


/*    Function vec_lvsl    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  b = 3;
  UCaux1.v = vec_lvsl( b, &b);
  bAux = b + (size_t)(&b);
  b = bAux & 0xF;
# if defined(GCC_COMPILER)
   UCaux2.v =(vector unsigned char){0x0,0x1,0x2,0x3,0x4,0x5,0x6,0x7,0x8,0x9,0xA,0xB,0xC,0xD,0xE,0xF};
# elif defined(MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux2.v =(vector unsigned char)(0x0,0x1,0x2,0x3,0x4,0x5,0x6,0x7,0x8,0x9,0xA,0xB,0xC,0xD,0xE,0xF);
# endif
  for( i=0; i< 16; i++ )
  {
    UCaux = UCaux2.e[i]+b;
    if (UCaux1.e[i] != UCaux)
      err++;
  }
  if (err)
    printf("Function vec_lvsl [type unsigned char]    ===> Error\n");
  else
    printf("Function vec_lvsl [type unsigned char]    ===> OK\n");

/*    Function vec_lvsr    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  b = 3;
  UCaux1.v = vec_lvsr( b, &b);
  bAux = b + (size_t)(&b);
  b = bAux & 0xF;
# if defined (GCC_COMPILER)
   UCaux2.v =(vector unsigned char){0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17,0x18,0x19,0x1A,0x1B,0x1C,0x1D,0x1E,0x1F};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux2.v =(vector unsigned char)(0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17,0x18,0x19,0x1A,0x1B,0x1C,0x1D,0x1E,0x1F);
# endif
  for( i=0; i< 16; i++ )
  {
    UCaux = UCaux2.e[i]-b;
    if (UCaux1.e[i] != UCaux)
      err++;
  }
  if (err)
    printf("Function vec_lvsr [type unsigned char]    ===> Error\n");
  else
    printf("Function vec_lvsr [type unsigned char]    ===> OK\n");

#if defined TEST_FLOATS
/*    Function vec_madd    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Faux1.v = vec_madd( Fcons1, Fcons2, Fcons3 );
  Faux2.v = Fcons1;
  Faux3.v = Fcons2;
  Faux4.v = Fcons3;
  for( i=0; i< 4; i++ )
    if (Faux1.e[i] != (Faux2.e[i]*Faux3.e[i]+Faux4.e[i]))
      err++;
  if (err)
    printf("Function vec_madd [type float]            ===> Error\n");
  else
    printf("Function vec_madd [type float]            ===> OK\n");
#endif

/*    Function vec_madds    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Saux1.v = vec_madds( Scons1, Scons3, Scons2 );
  Saux2.v = Scons1;
  Saux3.v = Scons3;
  Saux4.v = Scons2;
  for( i=0; i< 8; i++ )
  {
    INTunion1.si = Saux2.e[i]*Saux3.e[i];
    INTunion1.si = INTunion1.si >> 15;
    INTunion1.si = INTunion1.si + Saux4.e[i];
    if (INTunion1.si>32767)
      Saux=0x7FFF;
    else if (INTunion1.si<(-32768))
      Saux=0x8000;
    else
      Saux= INTunion1.ss[1];
    if (Saux1.e[i] != Saux)
      err++;
  }
  if (err)
    printf("Function vec_madds [type short]           ===> Error\n");
  else
    printf("Function vec_madds [type short]           ===> OK\n");

/*    Function vec_max    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_max( Ccons1, Ccons2 );
  Caux2.v = Ccons1;
  Caux3.v = Ccons2;
  for( i=0; i< 16; i++ )
  {
    if (Caux2.e[i]>Caux3.e[i])
      Caux = Caux2.e[i];
    else
      Caux = Caux3.e[i];
    if (Caux1.e[i] != Caux)
      err++;
  }
  if (err)
    printf("Function vec_max [type char]              ===> Error\n");
  else
    printf("Function vec_max [type char]              ===> OK\n");

  err = 0;
  UCaux1.v = vec_max( UCcons1, UCcons2 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons2;
  for( i=0; i< 16; i++ )
  {
    if (UCaux2.e[i]>UCaux3.e[i])
      UCaux = UCaux2.e[i];
    else
      UCaux = UCaux3.e[i];
    if (UCaux1.e[i] != UCaux)
      err++;
  }
  if (err)
    printf("Function vec_max [type unsigned char]     ===> Error\n");
  else
    printf("Function vec_max [type unsigned char]     ===> OK\n");

  err = 0;
  Saux1.v = vec_max( Scons1, Scons3 );
  Saux2.v = Scons1;
  Saux3.v = Scons3;
  for( i=0; i< 8; i++ )
  {
    if (Saux2.e[i]>Saux3.e[i])
      Saux = Saux2.e[i];
    else
      Saux = Saux3.e[i];
    if (Saux1.e[i] != Saux)
      err++;
  }
  if (err)
    printf("Function vec_max [type short]             ===> Error\n");
  else
    printf("Function vec_max [type short]             ===> OK\n");

  err = 0;
  USaux1.v = vec_max( UScons1, UScons2 );
  USaux2.v = UScons1;
  USaux3.v = UScons2;
  for( i=0; i< 8; i++ )
  {
    if (USaux2.e[i]>USaux3.e[i])
      USaux = USaux2.e[i];
    else
      USaux = USaux3.e[i];
    if (USaux1.e[i] != USaux)
      err++;
  }
  if (err)
    printf("Function vec_max [type unsigned short]    ===> Error\n");
  else
    printf("Function vec_max [type unsigned short]    ===> OK\n");

  err = 0;
  Iaux1.v = vec_max( Icons1, Icons2 );
  Iaux2.v = Icons1;
  Iaux3.v = Icons2;
  for( i=0; i< 4; i++ )
  {
    if (Iaux2.e[i]>Iaux3.e[i])
      Iaux = Iaux2.e[i];
    else
      Iaux = Iaux3.e[i];
    if (Iaux1.e[i] != Iaux)
      err++;
  }
  if (err)
    printf("Function vec_max [type integer]           ===> Error\n");
  else
    printf("Function vec_max [type integer]           ===> OK\n");

  err = 0;
  UIaux1.v = vec_max( UIcons1, UIcons2 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons2;
  for( i=0; i< 4; i++ )
  {
    if (UIaux2.e[i]>UIaux3.e[i])
      UIaux = UIaux2.e[i];
    else
      UIaux = UIaux3.e[i];
    if (UIaux1.e[i] != UIaux)
      err++;
  }
  if (err)
    printf("Function vec_max [type unsigned int]      ===> Error\n");
  else
    printf("Function vec_max [type unsigned int]      ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
  Faux1.v = vec_max( Fcons1, Fcons2 );
  Faux2.v = Fcons1;
  Faux3.v = Fcons2;
  for( i=0; i< 4; i++ )
  {
    if (Faux2.e[i]>Faux3.e[i])
      Faux = Faux2.e[i];
    else
      Faux = Faux3.e[i];
    if (Faux1.e[i] != Faux)
      err++;
  }
  if (err)
    printf("Function vec_max [type float]             ===> Error\n");
  else
    printf("Function vec_max [type float]             ===> OK\n");
#endif

/*    Function vec_mergeh    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_mergeh( Ccons1, Ccons2 );
  Caux2.v = Ccons1;
  Caux3.v = Ccons2;
  for( i=0; i< 8; i++ )
    if ((Caux1.e[2*i] != Caux2.e[i])||(Caux1.e[2*i+1]!=Caux3.e[i]))
      err++;
  if (err)
    printf("Function vec_mergeh [type char]           ===> Error\n");
  else
    printf("Function vec_mergeh [type char]           ===> OK\n");

  err = 0;
  UCaux1.v = vec_mergeh( UCcons1, UCcons2 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons2;
  for( i=0; i< 8; i++ )
    if ((UCaux1.e[2*i] != UCaux2.e[i])||(UCaux1.e[2*i+1]!=UCaux3.e[i]))
      err++;
  if (err)
    printf("Function vec_mergeh [type unsigned char]  ===> Error\n");
  else
    printf("Function vec_mergeh [type unsigned char]  ===> OK\n");

  err = 0;
  Saux1.v = vec_mergeh( Scons1, Scons2 );
  Saux2.v = Scons1;
  Saux3.v = Scons2;
  for( i=0; i< 4; i++ )
    if ((Saux1.e[2*i] != Saux2.e[i])||(Saux1.e[2*i+1]!=Saux3.e[i]))
      err++;
  if (err)
    printf("Function vec_mergeh [type short]          ===> Error\n");
  else
    printf("Function vec_mergeh [type short]          ===> OK\n");

  err = 0;
  USaux1.v = vec_mergeh( UScons1, UScons2 );
  USaux2.v = UScons1;
  USaux3.v = UScons2;
  for( i=0; i< 4; i++ )
    if ((USaux1.e[2*i] != USaux2.e[i])||(USaux1.e[2*i+1]!=USaux3.e[i]))
      err++;
  if (err)
    printf("Function vec_mergeh [type unsigned short] ===> Error\n");
  else
    printf("Function vec_mergeh [type unsigned short] ===> OK\n");

  err = 0;
  Iaux1.v = vec_mergeh( Icons1, Icons2 );
  Iaux2.v = Icons1;
  Iaux3.v = Icons2;
  for( i=0; i< 2; i++ )
    if ((Iaux1.e[2*i] != Iaux2.e[i])||(Iaux1.e[2*i+1]!=Iaux3.e[i]))
      err++;
  if (err)
    printf("Function vec_mergeh [type integer]        ===> Error\n");
  else
    printf("Function vec_mergeh [type integer]        ===> OK\n");

  err = 0;
  UIaux1.v = vec_mergeh( UIcons1, UIcons2 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons2;
  for( i=0; i< 2; i++ )
    if ((UIaux1.e[2*i] != UIaux2.e[i])||(UIaux1.e[2*i+1]!=UIaux3.e[i]))
      err++;
  if (err)
    printf("Function vec_mergeh [type unsigned int]   ===> Error\n");
  else
    printf("Function vec_mergeh [type unsigned int]   ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
  Faux1.v = vec_mergeh( Fcons1, Fcons2 );
  Faux2.v = Fcons1;
  Faux3.v = Fcons2;
  for( i=0; i< 2; i++ )
    if ((Faux1.e[2*i] != Faux2.e[i])||(Faux1.e[2*i+1]!=Faux3.e[i]))
      err++;
  if (err)
    printf("Function vec_mergeh [type float]          ===> Error\n");
  else
    printf("Function vec_mergeh [type float]          ===> OK\n");
#endif

/*    Function vec_mergel    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_mergel( Ccons1, Ccons2 );
  Caux2.v = Ccons1;
  Caux3.v = Ccons2;
  for( i=0; i< 8; i++ )
    if ((Caux1.e[2*i] != Caux2.e[i+8])||(Caux1.e[2*i+1]!=Caux3.e[i+8]))
      err++;
  if (err)
    printf("Function vec_mergel [type char]           ===> Error\n");
  else
    printf("Function vec_mergel [type char]           ===> OK\n");

  err = 0;
  UCaux1.v = vec_mergel( UCcons1, UCcons2 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons2;
  for( i=0; i< 8; i++ )
    if ((UCaux1.e[2*i] != UCaux2.e[i+8])||(UCaux1.e[2*i+1]!=UCaux3.e[i+8]))
      err++;
  if (err)
    printf("Function vec_mergel [type unsigned char]  ===> Error\n");
  else
    printf("Function vec_mergel [type unsigned char]  ===> OK\n");

  err = 0;
  Saux1.v = vec_mergel( Scons1, Scons2 );
  Saux2.v = Scons1;
  Saux3.v = Scons2;
  for( i=0; i< 4; i++ )
    if ((Saux1.e[2*i] != Saux2.e[i+4])||(Saux1.e[2*i+1]!=Saux3.e[i+4]))
      err++;
  if (err)
    printf("Function vec_mergel [type short]          ===> Error\n");
  else
    printf("Function vec_mergel [type short]          ===> OK\n");

  err = 0;
  USaux1.v = vec_mergel( UScons1, UScons2 );
  USaux2.v = UScons1;
  USaux3.v = UScons2;
  for( i=0; i< 4; i++ )
    if ((USaux1.e[2*i] != USaux2.e[i+4])||(USaux1.e[2*i+1]!=USaux3.e[i+4]))
      err++;
  if (err)
    printf("Function vec_mergel [type unsigned short] ===> Error\n");
  else
    printf("Function vec_mergel [type unsigned short] ===> OK\n");

  err = 0;
  Iaux1.v = vec_mergel( Icons1, Icons2 );
  Iaux2.v = Icons1;
  Iaux3.v = Icons2;
  for( i=0; i< 2; i++ )
    if ((Iaux1.e[2*i] != Iaux2.e[i+2])||(Iaux1.e[2*i+1]!=Iaux3.e[i+2]))
      err++;
  if (err)
    printf("Function vec_mergel [type integer]        ===> Error\n");
  else
    printf("Function vec_mergel [type integer]        ===> OK\n");

  err = 0;
  UIaux1.v = vec_mergel( UIcons1, UIcons2 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons2;
  for( i=0; i< 2; i++ )
    if ((UIaux1.e[2*i] != UIaux2.e[i+2])||(UIaux1.e[2*i+1]!=UIaux3.e[i+2]))
      err++;
  if (err)
    printf("Function vec_mergel [type unsigned int]   ===> Error\n");
  else
    printf("Function vec_mergel [type unsigned int]   ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
  Faux1.v = vec_mergel( Fcons1, Fcons2 );
  Faux2.v = Fcons1;
  Faux3.v = Fcons2;
  for( i=0; i< 2; i++ )
    if ((Faux1.e[2*i] != Faux2.e[i+2])||(Faux1.e[2*i+1]!=Faux3.e[i+2]))
      err++;
  if (err)
    printf("Function vec_mergel [type float]          ===> Error\n");
  else
    printf("Function vec_mergel [type float]          ===> OK\n");
#endif

/*    Function vec_mfvscr    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  printf("Function vec_mfvscr [Vector Move from Vector Status and Control Register] not checked\n");

/*    Function vec_min    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
#ifndef XLC_COMPILER
  err = 0;
  Caux1.v = vec_min( Ccons1, Ccons2 );
  Caux2.v = Ccons1;
  Caux3.v = Ccons2;
  for( i=0; i< 8; i++ )
  {
    if (Caux2.e[i]<Caux3.e[i])
      Caux = Caux2.e[i];
    else
      Caux = Caux3.e[i];
    if (Caux1.e[i] != Caux)
      err++;
  }
  if (err)
    printf("Function vec_min [type char]              ===> Error\n");
  else
    printf("Function vec_min [type char]              ===> OK\n");
#endif

  err = 0;
  UCaux1.v = vec_min( UCcons1, UCcons2 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons2;
  for( i=0; i< 8; i++ )
  {
    if (UCaux2.e[i]<UCaux3.e[i])
      UCaux = UCaux2.e[i];
    else
      UCaux = UCaux3.e[i];
    if (UCaux1.e[i] != UCaux)
      err++;
  }
  if (err)
    printf("Function vec_min [type unsigned char]     ===> Error\n");
  else
    printf("Function vec_min [type unsigned char]     ===> OK\n");

#ifndef XLC_COMPILER
  err = 0;
  Saux1.v = vec_min( Scons1, Scons2 );
  Saux2.v = Scons1;
  Saux3.v = Scons2;
  for( i=0; i< 8; i++ )
  {
    if (Saux2.e[i]<Saux3.e[i])
      Saux = Saux2.e[i];
    else
      Saux = Saux3.e[i];
    if (Saux1.e[i] != Saux)
      err++;
  }
  if (err)
    printf("Function vec_min [type short]             ===> Error\n");
  else
    printf("Function vec_min [type short]             ===> OK\n");

  err = 0;
  USaux1.v = vec_min( UScons1, UScons2 );
  USaux2.v = UScons1;
  USaux3.v = UScons2;
  for( i=0; i< 8; i++ )
  {
    if (USaux2.e[i]<USaux3.e[i])
      USaux = USaux2.e[i];
    else
      USaux = USaux3.e[i];
    if (USaux1.e[i] != USaux)
      err++;
  }
  if (err)
    printf("Function vec_min [type unsigned short]    ===> Error\n");
  else
    printf("Function vec_min [type unsigned short]    ===> OK\n");

  err = 0;
  Iaux1.v = vec_min( Icons1, Icons2 );
  Iaux2.v = Icons1;
  Iaux3.v = Icons2;
  for( i=0; i< 4; i++ )
  {
    if (Iaux2.e[i]<Iaux3.e[i])
      Iaux = Iaux2.e[i];
    else
      Iaux = Iaux3.e[i];
    if (Iaux1.e[i] != Iaux)
      err++;
  }
  if (err)
    printf("Function vec_min [type integer]           ===> Error\n");
  else
    printf("Function vec_min [type integer]           ===> OK\n");

  err = 0;
  UIaux1.v = vec_min( UIcons1, UIcons2 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons2;
  for( i=0; i< 4; i++ )
  {
    if (UIaux2.e[i]<UIaux3.e[i])
      UIaux = UIaux2.e[i];
    else
      UIaux = UIaux3.e[i];
    if (UIaux1.e[i] != UIaux)
      err++;
  }
  if (err)
    printf("Function vec_min [type unsigned int]      ===> Error\n");
  else
    printf("Function vec_min [type unsigned int]      ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
  Faux1.v = vec_min( Fcons1, Fcons2 );
  Faux2.v = Fcons1;
  Faux3.v = Fcons2;
  for( i=0; i< 4; i++ )
  {
    if (Faux2.e[i]<Faux3.e[i])
      Faux = Faux2.e[i];
    else
      Faux = Faux3.e[i];
    if (Faux1.e[i] != Faux)
      err++;
  }
  if (err)
    printf("Function vec_min [type float]             ===> Error\n");
  else
    printf("Function vec_min [type float]             ===> OK\n");
#endif

#endif

/*    Function vec_mladd    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
#ifndef XLC_COMPILER
  err = 0;
  Saux1.v = vec_mladd( Scons1, Scons2, Scons3 );
  Saux2.v = Scons1;
  Saux3.v = Scons2;
  Saux4.v = Scons3;
  for( i=0; i< 8; i++ )
  {
    INTunion1.si = Saux2.e[i]*Saux3.e[i];
    INTunion1.si = INTunion1.si + Saux4.e[i];
    if (Saux1.e[i] != INTunion1.ss[1])
      err++;
  }
  if (err)
    printf("Function vec_mladd [type short]           ===> Error\n");
  else
    printf("Function vec_mladd [type short]           ===> OK\n");
#endif

  err = 0;
  USaux1.v = vec_mladd( UScons1, UScons2, UScons3 );
  USaux2.v = UScons1;
  USaux3.v = UScons2;
  USaux4.v = UScons3;
  for( i=0; i< 8; i++ )
  {
    INTunion1.ui = USaux2.e[i]*USaux3.e[i];
    INTunion1.ui = INTunion1.ui + USaux4.e[i];
    if (USaux1.e[i] != INTunion1.us[1])
      err++;
  }
  if (err)
    printf("Function vec_mladd [type unsigned short]  ===> Error\n");
  else
    printf("Function vec_mladd [type unsigned short]  ===> OK\n");

/*    Function vec_mradds    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Saux1.v = vec_mradds( Scons1, Scons2, Scons3 );
  Saux2.v = Scons1;
  Saux3.v = Scons2;
  Saux4.v = Scons3;
  for( i=0; i< 8; i++ )
  {
    INTunion1.si = Saux2.e[i]*Saux3.e[i]+0x4000;
    INTunion1.si = INTunion1.si >> 15;
    INTunion1.si = INTunion1.si + Saux4.e[i];
    if (INTunion1.si>32767)
      Saux = 0x7FFF;
    else if (INTunion1.si<(-32768))
      Saux = 0x8000;
    else
      Saux = INTunion1.ss[1];
    if (Saux1.e[i] != Saux)
      err++;

printf("vector: %d \n", Saux1.e[i]);
printf("scalar: %d \n", Saux);
  }

  if (err)
    printf("Function vec_mradds [type short]          ===> Error\n");
  else
    printf("Function vec_mradds [type short]          ===> OK\n");

/*    Function vec_msum    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
#ifndef XLC_COMPILER
  err = 0;
  Iaux1.v = vec_msum( Ccons1, UCcons2, Icons1 );
  Caux1.v = Ccons1;
  UCaux1.v = UCcons2;
  Iaux2.v = Icons1;
  for( i=0; i< 4; i++ )
  {
    Iaux = Iaux2.e[i];
    for (j=0; j< 4; j++)
      Iaux = Iaux + Caux1.e[4*i+j]*UCaux1.e[4*i+j];
    if (Iaux1.e[i] != Iaux)
      err++;
  }
  if (err)
    printf("Function vec_msum [type char]             ===> Error\n");
  else
    printf("Function vec_msum [type char]             ===> OK\n");
#endif

  err = 0;
  UIaux1.v = vec_msum( UCcons1, UCcons2, UIcons1 );
  UCaux1.v = UCcons1;
  UCaux2.v = UCcons2;
  UIaux2.v = UIcons1;
  for( i=0; i< 4; i++ )
  {
    UIaux = UIaux2.e[i];
    for (j=0; j< 4; j++)
      UIaux = UIaux + UCaux1.e[4*i+j]*UCaux2.e[4*i+j];
    if (UIaux1.e[i] != UIaux)
      err++;
  }
  if (err)
    printf("Function vec_msum [type unsigned char]    ===> Error\n");
  else
    printf("Function vec_msum [type unsigned char]    ===> OK\n");

#ifndef XLC_COMPILER
  err = 0;
  Iaux1.v = vec_msum( Scons1, Scons2, Icons1 );
  Saux1.v = Scons1;
  Saux2.v = Scons2;
  Iaux2.v = Icons1;
  for( i=0; i< 4; i++ )
  {
    Iaux = Iaux2.e[i];
    for (j=0; j< 2; j++)
      Iaux = Iaux + Saux1.e[2*i+j]*Saux2.e[2*i+j];
    if (Iaux1.e[i] != Iaux)
      err++;
  }
  if (err)
    printf("Function vec_msum [type short]            ===> Error\n");
  else
    printf("Function vec_msum [type short]            ===> OK\n");

  err = 0;
  UIaux1.v = vec_msum( UScons1, UScons2, UIcons1 );
  USaux1.v = UScons1;
  USaux2.v = UScons2;
  UIaux2.v = UIcons1;
  for( i=0; i< 4; i++ )
  {
    UIaux = UIaux2.e[i];
    for (j=0; j< 2; j++)
      UIaux = UIaux + USaux1.e[2*i+j]*USaux2.e[2*i+j];
    if (UIaux1.e[i] != UIaux)
      err++;
  }
  if (err)
    printf("Function vec_msum [type unsigned short]   ===> Error\n");
  else
    printf("Function vec_msum [type unsigned short]   ===> OK\n");
#endif

/*    Function vec_msums    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Iaux1.v = vec_msums( Scons2, Scons3, Icons3 );
  Saux1.v = Scons2;
  Saux2.v = Scons3;
  Iaux2.v = Icons3;
  for( i=0; i< 4; i++ )
  {
    I1 = Saux1.e[2*i]*Saux2.e[2*i];
    I2 = Saux1.e[2*i+1]*Saux2.e[2*i+1];
    Iaux = I1 + I2;
    if ((I1>0)&&(I2>0)&&(Iaux<0))
      Iaux=0x7FFFFFFF;
    else if ((I1<0)&&(I2<0)&&(Iaux>0))
      Iaux=0x80000000;
    I1 = Iaux2.e[i];
    I2 = Iaux;
    Iaux = I1 + I2;
    if ((I1>0)&&(I2>0)&&(Iaux<0))
      Iaux=0x7FFFFFFF;
    else if ((I1<0)&&(I2<0)&&(Iaux>0))
      Iaux=0x80000000;
    if (Iaux1.e[i] != Iaux)
      err++;
  }
  if (err)
    printf("Function vec_msums [type short]           ===> Error\n");
  else
    printf("Function vec_msums [type short]           ===> OK\n");

  err = 0;
  UIaux1.v = vec_msums( UScons2, UScons3, UIcons3 );
  USaux1.v = UScons2;
  USaux2.v = UScons3;
  UIaux2.v = UIcons3;
  for( i=0; i< 4; i++ )
  {
    UI1 = USaux1.e[2*i]*USaux2.e[2*i];
    UI2 = USaux1.e[2*i+1]*USaux2.e[2*i+1];
    UIaux = UI1 + UI2;
    if ((UIaux<UI1)||(UIaux<UI2))
      UIaux=0xFFFFFFFF;
    UI1 = UIaux2.e[i];
    UI2 = UIaux;
    UIaux = UI1 + UI2;
    if ((UIaux<UI1)||(UIaux<UI2))
      UIaux=0xFFFFFFFF;
    if (UIaux1.e[i] != UIaux)
      err++;
  }
  if (err)
    printf("Function vec_msums [type unsigned short]  ===> Error\n");
  else
    printf("Function vec_msums [type unsigned short]  ===> OK\n");

/*    Function vec_mtvscr    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  printf("Function vec_mtvscr [Vector Move to Vector Status and Control Register] not checked\n");

/*    Function vec_mule    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Saux1.v = vec_mule( Ccons1, Ccons2 );
  Caux1.v = Ccons1;
  Caux2.v = Ccons2;
  for( i=0; i< 4; i++ )
    if (Saux1.e[i] != (Caux1.e[2*i]*Caux2.e[2*i]))
      err++;
  if (err)
    printf("Function vec_mule [type char]             ===> Error\n");
  else
    printf("Function vec_mule [type char]             ===> OK\n");

  err = 0;
  USaux1.v = vec_mule( UCcons1, UCcons2 );
  UCaux1.v = UCcons1;
  UCaux2.v = UCcons2;
  for( i=0; i< 4; i++ )
    if (USaux1.e[i] != (UCaux1.e[2*i]*UCaux2.e[2*i]))
      err++;
  if (err)
    printf("Function vec_mule [type unsigned char]    ===> Error\n");
  else
    printf("Function vec_mule [type unsigned char]    ===> OK\n");

  err = 0;
  Iaux1.v = vec_mule( Scons1, Scons2 );
  Saux1.v = Scons1;
  Saux2.v = Scons2;
  for( i=0; i< 4; i++ )
    if (Iaux1.e[i] != (Saux1.e[2*i]*Saux2.e[2*i]))
      err++;
  if (err)
    printf("Function vec_mule [type short]            ===> Error\n");
  else
    printf("Function vec_mule [type short]            ===> OK\n");

  err = 0;
  UIaux1.v = vec_mule( UScons1, UScons2 );
  USaux1.v = UScons1;
  USaux2.v = UScons2;
  for( i=0; i< 4; i++ )
    if (UIaux1.e[i] != (USaux1.e[2*i] * USaux2.e[2*i]))
      err++;
  if (err)
    printf("Function vec_mule [type unsigned short]   ===> Error\n");
  else
    printf("Function vec_mule [type unsigned short]   ===> OK\n");

/*    Function vec_mulo    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Saux1.v = vec_mulo( Ccons1, Ccons2 );
  Caux1.v = Ccons1;
  Caux2.v = Ccons2;
  for( i=0; i< 4; i++ )
    if (Saux1.e[i] != (Caux1.e[2*i+1]*Caux2.e[2*i+1]))
      err++;
  if (err)
    printf("Function vec_mulo [type char]             ===> Error\n");
  else 
    printf("Function vec_mulo [type char]             ===> OK\n");

  err = 0;
  USaux1.v = vec_mulo( UCcons1, UCcons2 );
  UCaux1.v = UCcons1;
  UCaux2.v = UCcons2;
  for( i=0; i< 4; i++ )
    if (USaux1.e[i] != (UCaux1.e[2*i+1]*UCaux2.e[2*i+1]))
      err++;
  if (err)
    printf("Function vec_mulo [type unsigned char]    ===> Error\n");
  else 
    printf("Function vec_mulo [type unsigned char]    ===> OK\n");

  err = 0;
  Iaux1.v = vec_mulo( Scons1, Scons2 );
  Saux1.v = Scons1;
  Saux2.v = Scons2;
  for( i=0; i< 4; i++ )
    if (Iaux1.e[i] != (Saux1.e[2*i+1]*Saux2.e[2*i+1]))
      err++;
  if (err)
    printf("Function vec_mulo [type short]            ===> Error\n");
  else
    printf("Function vec_mulo [type short]            ===> OK\n");

  err = 0;
  UIaux1.v = vec_mulo( UScons1, UScons2 );
  USaux1.v = UScons1;
  USaux2.v = UScons2;
  for( i=0; i< 4; i++ )
    if (UIaux1.e[i] != (USaux1.e[2*i+1]*USaux2.e[2*i+1]))
      err++;
  if (err)
    printf("Function vec_mulo [type unsigned short]   ===> Error\n");
  else
    printf("Function vec_mulo [type unsigned short]   ===> OK\n");

#if defined TEST_FLOATS
/*    Function vec_nmsub    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Faux1.v = vec_nmsub( Fcons1, Fcons2, Fcons3 );
  Faux2.v = Fcons1;
  Faux3.v = Fcons2;
  Faux4.v = Fcons3;
  for( i=0; i< 4; i++ )
  {
    if (Faux1.e[i] != (-Faux2.e[i]*Faux3.e[i]+Faux4.e[i]))
      err++;
  }
  if (err)
    printf("Function vec_nmsub [type float]           ===> Error\n");
  else
    printf("Function vec_nmsub [type float]           ===> OK\n");
#endif

/*    Function vec_nor    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");  
  err = 0;
  Caux1.v = vec_nor( Ccons1, Ccons2 );
  Caux2.v = Ccons1;
  Caux3.v = Ccons2;
  for( i=0; i< 16; i++ )
    if (Caux1.e[i] != ~(Caux2.e[i] | Caux3.e[i]))
      err++;
  if (err)
    printf("Function vec_nor [type char]              ===> Error\n");
  else
    printf("Function vec_nor [type char]              ===> OK\n");

  err = 0;
  UCaux1.v = vec_nor( UCcons1, UCcons2 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons2;
  for( i=0; i< 16; i++ )
  {
    UCaux = UCaux2.e[i] | UCaux3.e[i];
    UCaux = ~UCaux;
    if (UCaux1.e[i] != UCaux )
      err++;
  }
  if (err)
    printf("Function vec_nor [type unsigened char]    ===> Error\n");
  else
    printf("Function vec_nor [type unsigened char]    ===> OK\n");

  err = 0;
  Saux1.v = vec_nor( Scons1, Scons2 );
  Saux2.v = Scons1;
  Saux3.v = Scons2;
  for( i=0; i< 8; i++ )
    if (Saux1.e[i] != ~(Saux2.e[i] | Saux3.e[i]))
      err++;
  if (err)
    printf("Function vec_nor [type short]             ===> Error\n");
  else
    printf("Function vec_nor [type short]             ===> OK\n");

  err = 0;
  USaux1.v = vec_nor( UScons1, UScons2 );
  USaux2.v = UScons1;
  USaux3.v = UScons2;
  for( i=0; i< 8; i++ )
  {
    USaux = USaux2.e[i] | USaux3.e[i];
    USaux = ~USaux;
    if (USaux1.e[i] != USaux )
      err++;
  }
  if (err)
    printf("Function vec_nor [type unsigned short]    ===> Error\n");
  else
    printf("Function vec_nor [type unsigned short]    ===> OK\n");

  err = 0;
  Iaux1.v = vec_nor( Icons1, Icons2 );
  Iaux2.v = Icons1;
  Iaux3.v = Icons2;
  for( i=0; i< 4; i++ )
    if (Iaux1.e[i] != ~(Iaux2.e[i] | Iaux3.e[i]))
      err++;
  if (err)
    printf("Function vec_nor [type integer]           ===> Error\n");
  else
    printf("Function vec_nor [type integer]           ===> OK\n");

  err = 0;
  UIaux1.v = vec_nor( UIcons1, UIcons2 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons2;
  for( i=0; i< 4; i++ )
    if (UIaux1.e[i] != ~(UIaux2.e[i] | UIaux3.e[i]))
      err++;
  if (err)
    printf("Function vec_nor [type unsigened int]     ===> Error\n");
  else
    printf("Function vec_nor [type unsigened int]     ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
  Faux1.v = vec_nor( Fcons1, Fcons2 );
  Faux2.v = Fcons1;
  Faux3.v = Fcons2;
  for( i=0; i< 4; i++ )
  {
    Ivec1 = Faux1.i[i];
    Ivec2 = Faux2.i[i];
    Ivec3 = Faux3.i[i];
    if ((Ivec1) != ~((Ivec2) | (Ivec3)))
      err++;
  }
  if (err)
    printf("Function vec_nor [type float]             ===> Error\n");
  else
    printf("Function vec_nor [type float]             ===> OK\n");
#endif

/*    Function vec_or    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");  
  err = 0;
  Caux1.v = vec_or( Ccons1, Ccons2 );
  Caux2.v = Ccons1;
  Caux3.v = Ccons2;
  for( i=0; i< 16; i++ )
    if (Caux1.e[i] != (Caux2.e[i] | Caux3.e[i]))
      err++;
  if (err)
    printf("Function vec_or [type char]               ===> Error\n");
  else
    printf("Function vec_or [type char]               ===> OK\n");

  err = 0;
  UCaux1.v = vec_or( UCcons1, UCcons2 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons2;
  for( i=0; i< 16; i++ )
  {
    UCaux = UCaux2.e[i] | UCaux3.e[i];
    if (UCaux1.e[i] != UCaux )
      err++;
  }
  if (err)
    printf("Function vec_or [type unsigened char]     ===> Error\n");
  else
    printf("Function vec_or [type unsigened char]     ===> OK\n");

  err = 0;
  Saux1.v = vec_or( Scons1, Scons2 );
  Saux2.v = Scons1;
  Saux3.v = Scons2;
  for( i=0; i< 8; i++ )
    if (Saux1.e[i] != (Saux2.e[i] | Saux3.e[i]))
      err++;
  if (err)
    printf("Function vec_or [type short]              ===> Error\n");
  else
    printf("Function vec_or [type short]              ===> OK\n");

  err = 0;
  USaux1.v = vec_or( UScons1, UScons2 );
  USaux2.v = UScons1;
  USaux3.v = UScons2;
  for( i=0; i< 8; i++ )
  {
    USaux = USaux2.e[i] | USaux3.e[i];
    if (USaux1.e[i] != USaux )
      err++;
  }
  if (err)
    printf("Function vec_or [type unsigned short]     ===> Error\n");
  else
    printf("Function vec_or [type unsigned short]     ===> OK\n");

  err = 0;
  Iaux1.v = vec_or( Icons1, Icons2 );
  Iaux2.v = Icons1;
  Iaux3.v = Icons2;
  for( i=0; i< 4; i++ )
    if (Iaux1.e[i] != (Iaux2.e[i] | Iaux3.e[i]))
      err++;
  if (err)
    printf("Function vec_or [type integer]            ===> Error\n");
  else
    printf("Function vec_or [type integer]            ===> OK\n");

  err = 0;
  UIaux1.v = vec_or( UIcons1, UIcons2 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons2;
  for( i=0; i< 4; i++ )
    if (UIaux1.e[i] != (UIaux2.e[i] | UIaux3.e[i]))
      err++;
  if (err)
    printf("Function vec_or [type unsigened int]      ===> Error\n");
  else
    printf("Function vec_or [type unsigened int]      ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
  Faux1.v = vec_or( Fcons1, Fcons2 );
  Faux2.v = Fcons1;
  Faux3.v = Fcons2;
  for( i=0; i< 4; i++ )
  {
    Ivec1 = Faux1.i[i];
    Ivec2 = Faux2.i[i];
    Ivec3 = Faux3.i[i];
    if ((Ivec1) != ((Ivec2) | (Ivec3)))
      err++;
  }
  if (err)
    printf("Function vec_or [type float]              ===> Error\n");
  else
    printf("Function vec_or [type float]              ===> OK\n");
#endif

  return 0;
}




int part3( )
{
  TvecChar      Caux1,  Caux2,  Caux3;//,  Caux4;
  TvecUChar     UCaux1, UCaux2, UCaux3, UCaux4;
  TvecShort     Saux1,  Saux2,  Saux3;//,  Saux4;
  TvecUShort    USaux1, USaux2, USaux3, USaux4;
  TvecInt       Iaux1,  Iaux2,  Iaux3;//,  Iaux4;
  TvecUInt      UIaux1, UIaux2, UIaux3, UIaux4;
#if defined TEST_FLOATS
  TvecFloat     Faux1,  Faux2,  Faux3;//,  Faux4;
#endif
 
  int                  i, err, /*j,*/ b;//, bAux;
#if defined TEST_FLOATS
  signed   int         Ivec1, Ivec2;//, Ivec3;
#endif
//  signed   short       *Svec1;
  unsigned int         *UIvec1;
  unsigned short       *USvec1;
  unsigned char        *UCvec1;
#if defined TEST_FLOATS
  //  float                *Fvec1;
#endif

  /* For saturated rutines */
//  long long int         LLaux;

#if defined TEST_FLOATS
  float                 Faux;
#endif
  signed   int          Iaux;//, I1, I2;
  unsigned int          UIaux;//, UI1, UI2;
  signed   short        Saux;
  unsigned short        USaux;
  signed   char         Caux;
  unsigned char         UCaux;

  union
  {
    float          f;
    signed   int   si;
    unsigned int   ui;
    signed   short ss[2];
    unsigned short us[2];
    signed   char  sc[4];
    unsigned char  uc[4];
  } INTunion1, INTunion2;

  union
  {
    signed   short  ss;
    unsigned short  us;
    signed   char   sc[2];
    unsigned char   uc[2];
  } SHOunion1, SHOunion2;


#if defined (GCC_COMPILER)
  vector signed char    Ccons1   = (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
  vector signed char    Ccons2   = (vector signed char){1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1};
  vector signed char    Ccons3   = (vector signed char){-128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127};
  vector unsigned char  UCcons1  = (vector unsigned char){248, 249, 250, 251, 252, 253, 254, 255, 0, 1, 2, 3, 4, 5, 6, 7};
  vector unsigned char  UCcons2  = (vector unsigned char){2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2};
  vector unsigned char  UCcons3  = (vector unsigned char){1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8};
  vector signed short   Scons1   = (vector signed short){-4, -3, -2, -1, 0, 1, 2, 3};
  vector signed short   Scons2   = (vector signed short){-32768, 10000, 1, 1, 1, 1, -10000, -10000};
  vector signed short   Scons3   = (vector signed short){-32768, 32767, -32768, 32767, -32768, 32767, -32768, 32767};
  vector unsigned short UScons1  = (vector unsigned short){65532, 65533, 65534, 65535, 0, 1, 2, 3};
  vector unsigned short UScons2  = (vector unsigned short){1, 1, 1, 1, 1, 1, 1, 1};
  vector unsigned short UScons3  = (vector unsigned short){1, 2, 3, 4, 1, 2, 3, 4};
  vector signed int     Icons1   = (vector signed int){-4, -1, 1, 4};
  vector signed int     Icons2   = (vector signed int){1, 1, 1, 1};
  vector signed int     Icons3   = (vector signed int){0x80000000, 0x7FFFFFFF, 0x80000000, 0x7FFFFFFF};
  vector unsigned int   UIcons1  = (vector unsigned int){0xFFFFFFFE, 0xFFFFFFFF, 0, 1};
  vector unsigned int   UIcons2  = (vector unsigned int){1, 1, 1, 1};
  vector unsigned int   UIcons3  = (vector unsigned int){1, 2, 1, 2};

#if defined TEST_FLOATS
  vector float          Fcons1   = (vector float){-1.5, 1.0, 0.5, -3.999};
  vector float          Fcons2   = (vector float){1.0, 1.0, 1.0, 1.0};
  vector float          Fcons3   = (vector float){100000000000.0, 1.0, -1.0, -1234567890.0};
#endif

#elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
  vector signed char    Ccons1   = (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
  vector signed char    Ccons2   = (vector signed char)(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1);
  vector signed char    Ccons3   = (vector signed char)(-128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127);
  vector unsigned char  UCcons1  = (vector unsigned char)(248, 249, 250, 251, 252, 253, 254, 255, 0, 1, 2, 3, 4, 5, 6, 7);
  vector unsigned char  UCcons2  = (vector unsigned char)(2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2);
  vector unsigned char  UCcons3  = (vector unsigned char)(1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8);
  vector signed short   Scons1   = (vector signed short)(-4, -3, -2, -1, 0, 1, 2, 3);
  vector signed short   Scons2   = (vector signed short)(-32768, 10000, 1, 1, 1, 1, -10000, -10000);
  vector signed short   Scons3   = (vector signed short)(-32768, 32767, -32768, 32767, -32768, 32767, -32768, 32767);
  vector unsigned short UScons1  = (vector unsigned short)(65532, 65533, 65534, 65535, 0, 1, 2, 3);
  vector unsigned short UScons2  = (vector unsigned short)(1, 1, 1, 1, 1, 1, 1, 1);
  vector unsigned short UScons3  = (vector unsigned short)(1, 2, 3, 4, 1, 2, 3, 4);
  vector signed int     Icons1   = (vector signed int)(-4, -1, 1, 4);
  vector signed int     Icons2   = (vector signed int)(1, 1, 1, 1);
  vector signed int     Icons3   = (vector signed int)(0x80000000, 0x7FFFFFFF, 0x80000000, 0x7FFFFFFF);
  vector unsigned int   UIcons1  = (vector unsigned int)(0xFFFFFFFE, 0xFFFFFFFF, 0, 1);
  vector unsigned int   UIcons2  = (vector unsigned int)(1, 1, 1, 1);
  vector unsigned int   UIcons3  = (vector unsigned int)(1, 2, 1, 2);

#if defined TEST_FLOATS
  vector float          Fcons1   = (vector float)(-1.5, 1.0, 0.5, -3.999);
  vector float          Fcons2   = (vector float)(1.0, 1.0, 1.0, 1.0);
  vector float          Fcons3   = (vector float)(100000000000.0, 1.0, -1.0, -1234567890.0);
#endif

#endif


/* Variables to be allocated with calloc_vec (16 bytes aligned) */
  unsigned char   *UCmem = (unsigned char*)calloc_vec( 1, sizeof(vector unsigned char) );
  signed char     *Cmem  = (signed char*)calloc_vec( 1, sizeof(vector signed char) );
  unsigned short  *USmem = (unsigned short*)calloc_vec( 1, sizeof(vector unsigned short) );
  signed short    *Smem  = (signed short*)calloc_vec( 1, sizeof(vector signed short) );
  unsigned int    *UImem = (unsigned int*)calloc_vec( 1, sizeof(vector unsigned int) );
  signed int      *Imem  = (signed int*)calloc_vec( 1, sizeof(vector signed int) );
#if defined TEST_FLOATS
  float           *Fmem  = (float*)calloc_vec( 1, sizeof(vector float) );
#endif

/*    Function vec_pack    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_pack( Scons1, Scons2 );
  Saux1.v = Scons1;
  Saux2.v = Scons2;
  for( i=0; i< 8; i++ )
  {
    SHOunion1.ss = Saux1.e[i];
    if (Caux1.e[i] != SHOunion1.sc[1])
      err++;
    SHOunion1.ss = Saux2.e[i];
    if (Caux1.e[i+8] != SHOunion1.sc[1])
      err++;
  }
  if (err)
    printf("Function vec_pack [type char]             ===> Error\n");
  else
    printf("Function vec_pack [type char]             ===> OK\n");

  err = 0;
  UCaux1.v = vec_pack( UScons1, UScons2 );
  USaux1.v = UScons1;
  USaux2.v = UScons2;
  for( i=0; i< 8; i++ )
  {
    SHOunion1.ss = USaux1.e[i];
    if (UCaux1.e[i] != SHOunion1.uc[1])
      err++;
    SHOunion1.ss = USaux2.e[i];
    if (UCaux1.e[i+8] != SHOunion1.uc[1])
      err++;
  }
  if (err)
    printf("Function vec_pack [type unsigned char]    ===> Error\n");
  else
    printf("Function vec_pack [type unsigned char]    ===> OK\n");

  err = 0;
  Saux1.v = vec_pack( Icons1, Icons2 );
  Iaux1.v = Icons1;
  Iaux2.v = Icons2;
  for( i=0; i< 4; i++ )
  {
    INTunion1.si = Iaux1.e[i];
    if (Saux1.e[i] != INTunion1.ss[1])
      err++;
    INTunion1.si = Iaux2.e[i];
    if (Saux1.e[i+4] != INTunion1.ss[1])
      err++;
  }
  if (err)
    printf("Function vec_pack [type short]            ===> Error\n");
  else
    printf("Function vec_pack [type short]            ===> OK\n");

  err = 0;
  USaux1.v = vec_pack( UIcons1, UIcons2 );
  UIaux1.v = UIcons1;
  UIaux2.v = UIcons2;
  for( i=0; i< 4; i++ )
  {
    INTunion1.ui = UIaux1.e[i];
    if (USaux1.e[i] != INTunion1.us[1])
      err++;
    INTunion1.ui = UIaux2.e[i];
    if (USaux1.e[i+4] != INTunion1.us[1])
      err++;
  }
  if (err)
    printf("Function vec_pack [type unsigned short]   ===> Error\n");
  else
    printf("Function vec_pack [type unsigned short]   ===> OK\n");

/*    Function vec_packpx    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  printf("Function vec_packpx [Vector Pack Pixel] not checked\n");

/*    Function vec_packs    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_packs( Scons1, Scons2 );
  Saux1.v = Scons1;
  Saux2.v = Scons2;
  for( i=0; i< 8; i++ )
  {
    if (Saux1.e[i]>127)
      Caux = 127;
    else if (Saux1.e[i]<(-128))
      Caux = -128;
    else
      Caux = (signed char)Saux1.e[i];
    if (Caux1.e[i] != Caux)
      err++;
    if (Saux2.e[i]>127)
      Caux = 127;
    else if (Saux2.e[i]<(-128))
      Caux = -128;
    else
      Caux = (signed char)Saux2.e[i];
    if (Caux1.e[i+8] != Caux)
      err++;
  }
  if (err)
    printf("Function vec_packs [type char]            ===> Error\n");
  else
    printf("Function vec_packs [type char]            ===> OK\n");

  err = 0;
  UCaux1.v = vec_packs( UScons1, UScons2 );
  USaux1.v = UScons1;
  USaux2.v = UScons2;
  for( i=0; i< 8; i++ )
  {
    if (USaux1.e[i]>255)
      UCaux = 255;
    else
      UCaux = (unsigned char)USaux1.e[i];
    if (UCaux1.e[i] != UCaux)
      err++;
    if (USaux2.e[i]>255)
      UCaux = 255;
    else
      UCaux = (unsigned char)USaux2.e[i];
    if (UCaux1.e[i+8] != UCaux)
      err++;
  }
  if (err)
    printf("Function vec_packs [type unsigned char]   ===> Error\n");
  else
    printf("Function vec_packs [type unsigned char]   ===> OK\n");

  err = 0;
  Saux1.v = vec_packs( Icons1, Icons2 );
  Iaux1.v = Icons1;
  Iaux2.v = Icons2;
  for( i=0; i< 4; i++ )
  {
    if (Iaux1.e[i]>32767)
      Saux = 32767;
    else if (Iaux1.e[i]<(-32768))
      Saux = -32768;
    else
      Saux = (signed char)Iaux1.e[i];
    if (Saux1.e[i] != Saux)
      err++;
    if (Iaux2.e[i]>32767)
      Saux = 32767;
    else if (Iaux2.e[i]<(-32768))
      Saux = -32768;
    else
      Saux = (signed char)Iaux2.e[i];
    if (Saux1.e[i+4] != Saux)
      err++;
  }
  if (err)
    printf("Function vec_packs [type short]           ===> Error\n");
  else
    printf("Function vec_packs [type short]           ===> OK\n");

  err = 0;
  USaux1.v = vec_packs( UIcons1, UIcons2 );
  UIaux1.v = UIcons1;
  UIaux2.v = UIcons2;
  for( i=0; i< 4; i++ )
  {
    if (UIaux1.e[i]>65535)
      USaux = 65535;
    else
      USaux = (unsigned char)UIaux1.e[i];
    if (USaux1.e[i] != USaux)
      err++;
    if (UIaux2.e[i]>65535)
      USaux = 65535;
    else
      USaux = (unsigned char)UIaux2.e[i];
    if (USaux1.e[i+4] != USaux)
      err++;
  }
  if (err)
    printf("Function vec_packs [type unsigned short]  ===> Error\n");
  else
    printf("Function vec_packs [type unsigned short]  ===> OK\n");

/*    Function vec_packsu    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  UCaux1.v = vec_packsu( Scons1, Scons2 );
  Saux1.v = Scons1;
  Saux2.v = Scons2;
  for( i=0; i< 8; i++ )
  {
    if (Saux1.e[i]>255)
      UCaux = 255;
    else if  (Saux1.e[i]<0)
      UCaux = 0;
    else
      UCaux = (unsigned char)Saux1.e[i];
    if (UCaux1.e[i] != UCaux)
      err++;
    if (Saux2.e[i]>255)
      UCaux = 255;
    else if  (Saux2.e[i]<0)
      UCaux = 0;
    else
      UCaux = (unsigned char)Saux2.e[i];
    if (UCaux1.e[i+8] != UCaux)
      err++;
  }
  if (err)
    printf("Function vec_packsu [type char]           ===> Error\n");
  else
    printf("Function vec_packsu [type char]           ===> OK\n");

  err = 0;
  UCaux1.v = vec_packsu( UScons1, UScons2 );
  USaux1.v = UScons1;
  USaux2.v = UScons2;
  for( i=0; i< 8; i++ )
  {
    if (USaux1.e[i]>255)
      UCaux = 255;
    else
      UCaux = (unsigned char)USaux1.e[i];
    if (UCaux1.e[i] != UCaux)
      err++;
    if (USaux2.e[i]>255)
      UCaux = 255;
    else
      UCaux = (unsigned char)USaux2.e[i];
    if (UCaux1.e[i+8] != UCaux)
      err++;
  }
  if (err)
    printf("Function vec_packsu [type unsigned char]  ===> Error\n");
  else
    printf("Function vec_packsu [type unsigned char]  ===> OK\n");

  err = 0;
  USaux1.v = vec_packsu( Icons1, Icons2 );
  Iaux1.v = Icons1;
  Iaux2.v = Icons2;
  for( i=0; i< 4; i++ )
  {
    if (Iaux1.e[i]>65535)
      USaux = 65535;
    else if  (Iaux1.e[i]<0)
      USaux = 0;
    else
      USaux = (unsigned short)Iaux1.e[i];
    if (USaux1.e[i] != USaux)
      err++;
    if (Iaux2.e[i]>65535)
      USaux = 65535;
    else if  (Iaux2.e[i]<0)
      USaux = 0;
    else
      USaux = (unsigned short)Iaux2.e[i];
    if (USaux1.e[i+4] != USaux)
      err++;
  }
  if (err)
    printf("Function vec_packsu [type short]          ===> Error\n");
  else
    printf("Function vec_packsu [type short]          ===> OK\n");

  err = 0;
  USaux1.v = vec_packsu( UIcons1, UIcons2 );
  UIaux1.v = UIcons1;
  UIaux2.v = UIcons2;
  for( i=0; i< 4; i++ )
  {
    if (UIaux1.e[i]>65535)
      USaux = 65535;
    else
      USaux = (unsigned char)UIaux1.e[i];
    if (USaux1.e[i] != USaux)
      err++;
    if (UIaux2.e[i]>65535)
      USaux = 65535;
    else
      USaux = (unsigned char)UIaux2.e[i];
    if (USaux1.e[i+4] != USaux)
      err++;
  }
  if (err)
    printf("Function vec_packsu [type unsigned short] ===> Error\n");
  else
    printf("Function vec_packsu [type unsigned short] ===> OK\n");

/*    Function vec_perm    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  printf("Function vec_perm [Vector Permute] not checked\n");

#if defined TEST_FLOATS
/*    Function vec_re    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Faux1.v = vec_re( Fcons1 );
  Faux2.v = Fcons1;
  for( i=0; i< 4; i++ )
  {
    Faux = 1/Faux2.e[i];
    if (Faux!=0.0)
      Faux = (Faux - Faux1.e[i])/Faux;
    else
      Faux = Faux - Faux1.e[i];
    if (Faux>(1.0/4096.0))
      err++;
  }
  if (err)
    printf("Function vec_re [type float]              ===> Error\n");
  else
    printf("Function vec_re [type float]              ===> OK\n");
#endif

/*    Function vec_rl    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_rl( Ccons1, UCcons3 );
  Caux2.v = Ccons1;
  UCaux1.v = UCcons3;
  for( i=0; i< 16; i++ )
  {
    b = UCaux1.e[i];
    UCvec1 = (unsigned char *)(&Caux2.e[i]);
    Caux = ((*UCvec1)>>(8-b)) | ((*UCvec1)<<b);
    if (Caux1.e[i] != Caux)
      err++;
  }
  if (err)
    printf("Function vec_rl [type char]               ===> Error\n");
  else
    printf("Function vec_rl [type char]               ===> OK\n");

  err = 0;
  UCaux1.v = vec_rl( UCcons1, UCcons3 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons3;
  for( i=0; i< 16; i++ )
  {
    b = UCaux3.e[i];
    UCaux = (UCaux2.e[i]>>(8-b)) | (UCaux2.e[i]<<b);
    if (UCaux1.e[i] != UCaux)
      err++;
  }
  if (err)
    printf("Function vec_rl [type unsigned char]      ===> Error\n");
  else
    printf("Function vec_rl [type unsigned char]      ===> OK\n");

  err = 0;
  Saux1.v = vec_rl( Scons1, UScons3 );
  Saux2.v = Scons1;
  USaux1.v = UScons3;
  for( i=0; i< 8; i++ )
  {
    b = USaux1.e[i];
    USvec1 = (unsigned short *)(&Saux2.e[i]);
    Saux = ((*USvec1)>>(16-b)) | ((*USvec1)<<b);
    if (Saux1.e[i] != Saux)
      err++;
  }
  if (err)
    printf("Function vec_rl [type short]              ===> Error\n");
  else
    printf("Function vec_rl [type short]              ===> OK\n");

  err = 0;
  USaux1.v = vec_rl( UScons1, UScons3 );
  USaux2.v = UScons1;
  USaux3.v = UScons3;
  for( i=0; i< 8; i++ )
  {
    b = USaux3.e[i];
    USaux = (USaux2.e[i]>>(16-b)) | (USaux2.e[i]<<b);
    if (USaux1.e[i] != USaux)
      err++;
  }
  if (err)
    printf("Function vec_rl [type unsigned short]     ===> Error\n");
  else
    printf("Function vec_rl [type unsigned short]     ===> OK\n");

  err = 0;
  Iaux1.v = vec_rl( Icons1, UIcons3 );
  Iaux2.v = Icons1;
  UIaux1.v = UIcons3;
  for( i=0; i< 4; i++ )
  {
    b = UIaux1.e[i];
    UIvec1 = (unsigned int *)(&Iaux2.e[i]);
    Iaux = ((*UIvec1)>>(32-b)) | ((*UIvec1)<<b);
    if (Iaux1.e[i] != Iaux)
      err++;
  }
  if (err)
    printf("Function vec_rl [type integer]            ===> Error\n");
  else
    printf("Function vec_rl [type integer]            ===> OK\n");

  err = 0;
  UIaux1.v = vec_rl( UIcons1, UIcons3 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons3;
  for( i=0; i< 4; i++ )
  {
    b = UIaux3.e[i];
    UIaux = (UIaux2.e[i]>>(32-b)) | (UIaux2.e[i]<<b);
    if (UIaux1.e[i] != UIaux)
      err++;
  }
  if (err)
    printf("Function vec_rl [type unsigned int]       ===> Error\n");
  else
    printf("Function vec_rl [type unsigned int]       ===> OK\n");

#if defined TEST_FLOATS
/*    Function vec_round    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Faux1.v = vec_round( Fcons1 );
  Faux2.v = Fcons1;
  for( i=0; i< 4; i++ )
  {
    Faux = floor(Faux2.e[i]);
    if ((Faux2.e[i]-Faux)>0.5)
      Faux = Faux + 1.0;
    else if (((Faux2.e[i]-Faux)==0.5)&&(Iaux%2))
      Faux = Faux + 1.0;
    if (Faux1.e[i] != Faux)
      err++;
  }
  if (err)
    printf("Function vec_round [type float]           ===> Error\n");
  else
    printf("Function vec_round [type float]           ===> OK\n");
#endif

#if defined TEST_FLOATS
/*    Function vec_rsqrte    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Faux1.v = vec_rsqrte( Fcons1 );
  Faux2.v = Fcons1;
  for( i=0; i< 4; i++ )
  {
    Faux = sqrtf(Faux2.e[i]);
    if (Faux>0.0)
      Faux = (Faux - Faux1.e[i])/Faux;
    else if (Faux==0.0)
      Faux = Faux - Faux1.e[i];
    if (Faux>(1.0/4096.0))
      err++;
  }
  if (err)
    printf("Function vec_rsqrte [type float]          ===> Error\n");
  else
    printf("Function vec_rsqrte [type float]          ===> OK\n");
#endif

/*    Function vec_sel    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_sel( Ccons1, Ccons2, UCcons1 );
  Caux2.v = Ccons1;
  Caux3.v = Ccons2;
  UCaux1.v = UCcons1;
  for( i=0; i< 16; i++ )
  {
    Caux = (Caux2.e[i] & (~UCaux1.e[i])) | (Caux3.e[i] & UCaux1.e[i]);
    if (Caux1.e[i] != Caux)
      err++;
  }
  if (err)
    printf("Function vec_sel [type char]              ===> Error\n");
  else
    printf("Function vec_sel [type char]              ===> OK\n");

  err = 0;
  UCaux1.v = vec_sel( UCcons1, UCcons2, UCcons3 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons2;
  UCaux4.v = UCcons3;
  for( i=0; i< 16; i++ )
  {
    UCaux = (UCaux2.e[i] & (~UCaux4.e[i])) | (UCaux3.e[i] & UCaux4.e[i]);
    if (UCaux1.e[i] != UCaux)
      err++;
  }
  if (err)
    printf("Function vec_sel [type unsigned char]     ===> Error\n");
  else
    printf("Function vec_sel [type unsigned char]     ===> OK\n");

  err = 0;
  Saux1.v = vec_sel( Scons1, Scons2, UScons1 );
  Saux2.v = Scons1;
  Saux3.v = Scons2;
  USaux1.v = UScons1;
  for( i=0; i< 8; i++ )
  {
    Saux = (Saux2.e[i] & (~USaux1.e[i])) | (Saux3.e[i] & USaux1.e[i]);
    if (Saux1.e[i] != Saux)
      err++;
  }
  if (err)
    printf("Function vec_sel [type short]             ===> Error\n");
  else
    printf("Function vec_sel [type short]             ===> OK\n");

  err = 0;
  USaux1.v = vec_sel( UScons1, UScons2, UScons3 );
  USaux2.v = UScons1;
  USaux3.v = UScons2;
  USaux4.v = UScons3;
  for( i=0; i< 8; i++ )
  {
    USaux = (USaux2.e[i] & (~USaux4.e[i])) | (USaux3.e[i] & USaux4.e[i]);
    if (USaux1.e[i] != USaux)
      err++;
  }
  if (err)
    printf("Function vec_sel [type unsigned short]    ===> Error\n");
  else
    printf("Function vec_sel [type unsigned short]    ===> OK\n");

  err = 0;
  Iaux1.v = vec_sel( Icons1, Icons2, UIcons1 );
  Iaux2.v = Icons1;
  Iaux3.v = Icons2;
  UIaux1.v = UIcons1;
  for( i=0; i< 4; i++ )
  {
    Iaux = (Iaux2.e[i] & (~UIaux1.e[i])) | (Iaux3.e[i] & UIaux1.e[i]);
    if (Iaux1.e[i] != Iaux)
      err++;
  }
  if (err)
    printf("Function vec_sel [type integer]           ===> Error\n");
  else
    printf("Function vec_sel [type integer]           ===> OK\n");

  err = 0;
  UIaux1.v = vec_sel( UIcons1, UIcons2, UIcons3 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons2;
  UIaux4.v = UIcons3;
  for( i=0; i< 4; i++ )
  {
    UIaux = (UIaux2.e[i] & (~UIaux4.e[i])) | (UIaux3.e[i] & UIaux4.e[i]);
    if (UIaux1.e[i] != UIaux)
      err++;
  }
  if (err)
    printf("Function vec_sel [type unsigned int]      ===> Error\n");
  else
    printf("Function vec_sel [type unsigned int]      ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
  Faux1.v = vec_sel( Fcons1, Fcons2, UIcons1 );
  Faux2.v = Fcons1;
  Faux3.v = Fcons2;
  UIaux1.v = UIcons1;
  for( i=0; i< 4; i++ )
  {
    Ivec1 = Faux2.i[i];
    Ivec2 = Faux3.i[i];
    Iaux = (Ivec1 & (~UIaux1.e[i])) | (Ivec2 & UIaux1.e[i]);
    Ivec1 = Faux1.i[i];
    if ((Ivec1) != Iaux)
      err++;
  }
  if (err)
    printf("Function vec_sel [type float]             ===> Error\n");
  else
    printf("Function vec_sel [type float]             ===> OK\n");
#endif

/*    Function vec_sl    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_sl( Ccons1, UCcons3 );
  Caux2.v = Ccons1;
  UCaux1.v = UCcons3;
  for( i=0; i< 16; i++ )
  {
    b = UCaux1.e[i]%(128/16);
    Caux = Caux2.e[i] << b;
    if (Caux1.e[i] != Caux)
      err++;
  }
  if (err)
    printf("Function vec_sl [type char]               ===> Error\n");
  else
    printf("Function vec_sl [type char]               ===> OK\n");

  err = 0;
  UCaux1.v = vec_sl( UCcons1, UCcons3 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons3;
  for( i=0; i< 16; i++ )
  {
    b = UCaux3.e[i]%(128/16);
    UCaux = UCaux2.e[i] << b;
    if (UCaux1.e[i] != UCaux)
      err++;
  }
  if (err)
    printf("Function vec_sl [type unsigned char]      ===> Error\n");
  else
    printf("Function vec_sl [type unsigned char]      ===> OK\n");

  err = 0;
  Saux1.v = vec_sl( Scons1, UScons3 );
  Saux2.v = Scons1;
  USaux1.v = UScons3;
  for( i=0; i< 8; i++ )
  {
    b = USaux1.e[i]%(128/8);
    Saux = Saux2.e[i] << b;
    if (Saux1.e[i] != Saux)
      err++;
  }
  if (err)
    printf("Function vec_sl [type short]              ===> Error\n");
  else
    printf("Function vec_sl [type short]              ===> OK\n");

  err = 0;
  USaux1.v = vec_sl( UScons1, UScons3 );
  USaux2.v = UScons1;
  USaux3.v = UScons3;
  for( i=0; i< 8; i++ )
  {
    b = USaux3.e[i]%(128/8);
    USaux = USaux2.e[i] << b;
    if (USaux1.e[i] != USaux)
      err++;
  }
  if (err)
    printf("Function vec_sl [type unsigned short]     ===> Error\n");
  else
    printf("Function vec_sl [type unsigned short]     ===> OK\n");

  err = 0;
  Iaux1.v = vec_sl( Icons1, UIcons3 );
  Iaux2.v = Icons1;
  UIaux1.v = UIcons3;
  for( i=0; i< 4; i++ )
  {
    b = UIaux1.e[i]%(128/4);
    Iaux = Iaux2.e[i] << b;
    if (Iaux1.e[i] != Iaux)
      err++;
  }
  if (err)
    printf("Function vec_sl [type int]                ===> Error\n");
  else
    printf("Function vec_sl [type int]                ===> OK\n");

  err = 0;
  UIaux1.v = vec_sl( UIcons1, UIcons3 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons3;
  for( i=0; i< 4; i++ )
  {
    b = UIaux3.e[i]%(128/4);
    UIaux = UIaux2.e[i] << b;
    if (UIaux1.e[i] != UIaux)
      err++;
  }
  if (err)
    printf("Function vec_sl [type unsigned integer]   ===> Error\n");
  else
    printf("Function vec_sl [type unsigned integer]   ===> OK\n");

/*    Function vec_sld    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  b = 3;
  Caux1.v = vec_sld( Ccons1, Ccons2, 3 );
  Caux2.v = Ccons1;
  Caux3.v = Ccons2;
  for( i=0; i< 16; i++ )
  {
    if ((i+b)<16)
    {
      if (Caux1.e[i] != Caux2.e[i+b])
        err++;
    }
    else
    {
      if (Caux1.e[i] != Caux3.e[i+b-16])
        err++;
    }
  }
  if (err)
    printf("Function vec_sld [type char]              ===> Error\n");
  else
    printf("Function vec_sld [type char]              ===> OK\n");

  err = 0;
  b = 3;
  UCaux1.v = vec_sld( UCcons1, UCcons2, 3 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons2;
  for( i=0; i< 16; i++ )
  {
    if ((i+b)<16)
    {
      if (UCaux1.e[i] != UCaux2.e[i+b])
        err++;
    }
    else
    {
      if (UCaux1.e[i] != UCaux3.e[i+b-16])
        err++;
    }
  }
  if (err)
    printf("Function vec_sld [type unsigned char]     ===> Error\n");
  else
    printf("Function vec_sld [type unsigned char]     ===> OK\n");

  err = 0;
  b = 3;
  Saux1.v = vec_sld( Scons1, Scons2, 3 );
  Saux2.v = Scons1;
  Saux3.v = Scons2;
  for( i=0; i< 16; i++ )
  {
    SHOunion1.ss  = Saux1.e[i/2];
    if ((i+b)<16)
      SHOunion2.ss = Saux2.e[(i+b)/2];
    else
      SHOunion2.ss = Saux3.e[(i+b-16)/2];
    if (SHOunion1.sc[i%2] != SHOunion2.sc[(i+b)%2])
      err++;
  }
  if (err)
    printf("Function vec_sld [type short]             ===> Error\n");
  else
    printf("Function vec_sld [type short]             ===> OK\n");

  err = 0;
  b = 3;
  USaux1.v = vec_sld( UScons1, UScons2, 3 );
  USaux2.v = UScons1;
  USaux3.v = UScons2;
  for( i=0; i< 16; i++ )
  {
    SHOunion1.us  = USaux1.e[i/2];
    if ((i+b)<16)
      SHOunion2.us = USaux2.e[(i+b)/2];
    else
      SHOunion2.us = USaux3.e[(i+b-16)/2];
    if (SHOunion1.uc[i%2] != SHOunion2.uc[(i+b)%2])
      err++;
  }
  if (err)
    printf("Function vec_sld [type unsigned short]    ===> Error\n");
  else
    printf("Function vec_sld [type unsigned short]    ===> OK\n");

  err = 0;
  b = 3;
  Iaux1.v = vec_sld( Icons1, Icons2, 3 );
  Iaux2.v = Icons1;
  Iaux3.v = Icons2;
  for( i=0; i< 16; i++ )
  {
    INTunion1.si  = Iaux1.e[i/4];
    if ((i+b)<16)
      INTunion2.si = Iaux2.e[(i+b)/4];
    else
      INTunion2.si = Iaux3.e[(i+b-16)/4];
    if (INTunion1.sc[i%4] != INTunion2.sc[(i+b)%4])
      err++;
  }
  if (err)
    printf("Function vec_sld [type integer]           ===> Error\n");
  else
    printf("Function vec_sld [type integer]           ===> OK\n");

  err = 0;
  b = 3;
  UIaux1.v = vec_sld( UIcons1, UIcons2, 3 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons2;
  for( i=0; i< 16; i++ )
  {
    INTunion1.ui  = UIaux1.e[i/4];
    if ((i+b)<16)
      INTunion2.ui = UIaux2.e[(i+b)/4];
    else
      INTunion2.ui = UIaux3.e[(i+b-16)/4];
    if (INTunion1.uc[i%4] != INTunion2.uc[(i+b)%4])
      err++;
  }
  if (err)
    printf("Function vec_sld [type unsigned int]      ===> Error\n");
  else
    printf("Function vec_sld [type unsigned int]      ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
  b = 3;
  Faux1.v = vec_sld( Fcons1, Fcons2, 3 );
  Faux2.v = Fcons1;
  Faux3.v = Fcons2;
  for( i=0; i< 16; i++ )
  {
    INTunion1.f  = Faux1.e[i/4];
    if ((i+b)<16)
      INTunion2.f = Faux2.e[(i+b)/4];
    else
      INTunion2.f = Faux3.e[(i+b-16)/4];
    if (INTunion1.sc[i%4] != INTunion2.sc[(i+b)%4])
      err++;
  }
  if (err)
    printf("Function vec_sld [type float]             ===> Error\n");
  else
    printf("Function vec_sld [type float]             ===> OK\n");
#endif

/*    Function vec_sll    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_sll( Ccons1, UCcons2 );
  Caux2.v = Ccons1;
  UCaux1.v = UCcons2;
  b = UCaux1.e[15] & 0x7;
  for( i=0; i< 15; i++ )
    if ((UCaux1.e[i] & 0x7)!=b)
      err++;
  if (err)
  {
    printf("The three low-order bits of all byte elements in b must be the same\n");
    printf("otherwise the value into d is undefined\n");
  }
  else
  {
    for( i=0; i< 16; i++ )
    {
      UCvec1 = (unsigned char *)(&Caux2.e[i]);
      Caux = UCvec1[0]<<b;
      if (i != 15)
        Caux = Caux | (UCvec1[1]>>(8-b));
      if (Caux != Caux1.e[i])
        err++;
    }
    if (err)
      printf("Function vec_sll [type char]              ===> Error\n");
    else
      printf("Function vec_sll [type char]              ===> OK\n");
  }

  UCaux1.v = vec_sll( UCcons1, UCcons2 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons2;
  b = UCaux3.e[15] & 0x7;
  for( i=0; i< 15; i++ )
    if ((UCaux3.e[i] & 0x7)!=b)
      err++;
  if (err)
  {
    printf("The three low-order bits of all byte elements in b must be the same\n");
    printf("otherwise the value into d is undefined\n");
  }
  else
  {
    for( i=0; i< 16; i++ )
    {
      UCvec1 = (unsigned char *)(&UCaux2.e[i]);
      UCaux  = UCvec1[0]<<b; 
      if (i != 15) 
        UCaux = UCaux | (UCvec1[1]>>(8-b));
      if (UCaux != UCaux1.e[i])
        err++;
    }
    if (err)
      printf("Function vec_sll [type unsigned char]     ===> Error\n");
    else
      printf("Function vec_sll [type unsigned char]     ===> OK\n");
  }

  err = 0;
  Saux1.v = vec_sll( Scons1, UCcons2 );
  Saux2.v = Scons1;
  UCaux1.v = UCcons2;
  b = UCaux1.e[15] & 0x7;
  for( i=0; i< 15; i++ )
    if ((UCaux1.e[i] & 0x7)!=b)
      err++;
  if (err)
  {
    printf("The three low-order bits of all byte elements in b must be the same\n");
    printf("otherwise the value into d is undefined\n");
  }
  else
  {
    for( i=0; i< 8; i++ )
    {
      USvec1 = (unsigned short *)(&Saux2.e[i]);
      Saux   = USvec1[0]<<b; 
      if (i != 7) 
        Saux = Saux | (USvec1[1]>>(16-b));
      if (Saux != Saux1.e[i])
        err++;
    }
    if (err)
      printf("Function vec_sll [type short]             ===> Error\n");
    else
      printf("Function vec_sll [type short]             ===> OK\n");
  }

  USaux1.v = vec_sll( UScons1, UCcons2 );
  USaux2.v = UScons1;
  UCaux1.v = UCcons2;
  b = UCaux1.e[15] & 0x7;
  for( i=0; i< 15; i++ )
    if ((UCaux1.e[i] & 0x7)!=b)
      err++;
  if (err)
  {
    printf("The three low-order bits of all byte elements in b must be the same\n");
    printf("otherwise the value into d is undefined\n");
  }
  else
  {
    for( i=0; i< 8; i++ )
    {
      USvec1 = (unsigned short *)(&USaux2.e[i]);
      USaux   = USvec1[0]<<b; 
      if (i != 7) 
        USaux = USaux | (USvec1[1]>>(16-b));
      if (USaux != USaux1.e[i])
        err++;
    }
    if (err)
      printf("Function vec_sll [type unsigned char]     ===> Error\n");
    else
      printf("Function vec_sll [type unsigned char]     ===> OK\n");
  }

  err = 0;
  Iaux1.v = vec_sll( Icons1, UCcons2 );
  Iaux2.v = Icons1;
  UCaux1.v = UCcons2;
  b = UCaux1.e[15] & 0x7;
  for( i=0; i< 15; i++ )
    if ((UCaux1.e[i] & 0x7)!=b)
      err++;
  if (err)
  {
    printf("The three low-order bits of all byte elements in b must be the same\n");
    printf("otherwise the value into d is undefined\n");
  }
  else
  {
    for( i=0; i< 4; i++ )
    {
      UIvec1 = (unsigned int *)(&Iaux2.e[i]);
      Iaux   = UIvec1[0]<<b; 
      if (i != 3) 
        Iaux = Iaux | (UIvec1[1]>>(32-b));
      if (Iaux != Iaux1.e[i])
        err++;
    }
    if (err)
      printf("Function vec_sll [type integer]           ===> Error\n");
    else
      printf("Function vec_sll [type integer]           ===> OK\n");
  }

  UIaux1.v = vec_sll( UIcons1, UCcons2 );
  UIaux2.v = UIcons1;
  UCaux1.v = UCcons2;
  b = UCaux1.e[15] & 0x7;
  for( i=0; i< 15; i++ )
    if ((UCaux1.e[i] & 0x7)!=b)
      err++;
  if (err)
  {
    printf("The three low-order bits of all byte elements in b must be the same\n");
    printf("otherwise the value into d is undefined\n");
  }
  else
  {
    for( i=0; i< 4; i++ )
    {
      UIvec1 = (unsigned int *)(&UIaux2.e[i]);
      UIaux   = UIvec1[0]<<b; 
      if (i != 3) 
        UIaux = UIaux | (UIvec1[1]>>(32-b));
      if (UIaux != UIaux1.e[i])
        err++;
    }
    if (err)
      printf("Function vec_sll [type unsigned int]      ===> Error\n");
    else
      printf("Function vec_sll [type unsigned int]      ===> OK\n");
  }

/*    Function vec_slo    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_slo( Ccons3, Ccons1 );
  Caux2.v = Ccons3;
  Caux3.v = Ccons1;
  b = (Caux3.e[15] & 0x78) >> 3;
  for( i=0; i< 16; i++ )
  {
    if ((i+b)<16)
    {
      if (Caux1.e[i] != Caux2.e[i+b])
        err++;
    }
    else
    {
      if (Caux1.e[i] != 0)
        err++;
    }
  }
  if (err)
    printf("Function vec_slo [type char]              ===> Error\n");
  else
    printf("Function vec_slo [type char]              ===> OK\n");

  err = 0;
  UCaux1.v = vec_slo( UCcons3, UCcons1 );
  UCaux2.v = UCcons3;
  UCaux3.v = UCcons1;
  b = (UCaux3.e[15] & 0x78) >> 3;
  for( i=0; i< 16; i++ )
  {
    if ((i+b)<16)
    {
      if (UCaux1.e[i] != UCaux2.e[i+b])
        err++;
    }
    else
    {
      if (UCaux1.e[i] != 0)
        err++;
    }
  }
  if (err)
    printf("Function vec_slo [type unsigned char]     ===> Error\n");
  else
    printf("Function vec_slo [type unsigned char]     ===> OK\n");

  err = 0;
  Saux1.v  = vec_slo( Scons3, UCcons1 );
  Saux2.v  = Scons3;
  UCaux3.v = UCcons1;
  b = (UCaux3.e[15] & 0x78) >> 3;
  for( i=0; i< 16; i++ )
  {
    SHOunion1.ss  = Saux1.e[i/2];
    if ((i+b)<16)
      SHOunion2.ss = Saux2.e[(i+b)/2];
    else
      SHOunion2.ss = 0;
    if (SHOunion1.sc[i%2] != SHOunion2.sc[(i+b)%2])
      err++;
  }
  if (err)
    printf("Function vec_slo [type short]             ===> Error\n");
  else
    printf("Function vec_slo [type short]             ===> OK\n");

  err = 0;
  USaux1.v = vec_slo( UScons3, UCcons1 );
  USaux2.v = UScons3;
  UCaux3.v = UCcons1;
  b = (UCaux3.e[15] & 0x78) >> 3;
  for( i=0; i< 16; i++ )
  {
    SHOunion1.us  = USaux1.e[i/2];
    if ((i+b)<16)
      SHOunion2.us = USaux2.e[(i+b)/2];
    else
      SHOunion2.us = 0;
    if (SHOunion1.uc[i%2] != SHOunion2.uc[(i+b)%2])
      err++;
  }
  if (err)
    printf("Function vec_slo [type unsigned short]    ===> Error\n");
  else
    printf("Function vec_slo [type unsigned short]    ===> OK\n");

  err = 0;
  Iaux1.v  = vec_slo( Icons3, UCcons1 );
  Iaux2.v  = Icons3;
  UCaux3.v = UCcons1;
  b = (UCaux3.e[15] & 0x78) >> 3;
  for( i=0; i< 16; i++ )
  {
    INTunion1.si  = Iaux1.e[i/4];
    if ((i+b)<16)
      INTunion2.si = Iaux2.e[(i+b)/4];
    else
      INTunion2.si = 0;
    if (INTunion1.sc[i%4] != INTunion2.sc[(i+b)%4])
      err++;
  }
  if (err)
    printf("Function vec_slo [type integer]           ===> Error\n");
  else
    printf("Function vec_slo [type integer]           ===> OK\n");

  err = 0;
  UIaux1.v = vec_slo( UIcons3, UCcons1 );
  UIaux2.v = UIcons3;
  UCaux3.v = UCcons1;
  b = (UCaux3.e[15] & 0x78) >> 3;
  for( i=0; i< 16; i++ )
  {
    INTunion1.ui  = UIaux1.e[i/4];
    if ((i+b)<16)
      INTunion2.ui = UIaux2.e[(i+b)/4];
    else
      INTunion2.ui = 0;
    if (INTunion1.uc[i%4] != INTunion2.uc[(i+b)%4])
      err++;
  }
  if (err)
    printf("Function vec_slo [type unsigned int]      ===> Error\n");
  else
    printf("Function vec_slo [type unsigned int]      ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
  Faux1.v  = vec_slo( Fcons3, UCcons1 );
  Faux2.v  = Fcons3;
  UCaux3.v = UCcons1;
  b = (UCaux3.e[15] & 0x78) >> 3;
  for( i=0; i< 16; i++ )
  {
    INTunion1.f  = Faux1.e[i/4];
    if ((i+b)<16)
      INTunion2.f = Faux2.e[(i+b)/4];
    else
      INTunion2.si = 0;
    if (INTunion1.sc[i%4] != INTunion2.sc[(i+b)%4])
      err++;
  }
  if (err)
    printf("Function vec_slo [type float]             ===> Error\n");
  else
    printf("Function vec_slo [type float]             ===> OK\n");
#endif

/*    Function vec_splat    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  b = 3;
  Caux1.v = vec_splat( Ccons1, 3 );
  Caux2.v = Ccons1;
  for( i=0; i< 16; i++ )
    if (Caux1.e[i] != Caux2.e[b])
      err++;
  if (err)
    printf("Function vec_splat [type char]            ===> Error\n");
  else
    printf("Function vec_splat [type char]            ===> OK\n");

  err = 0;
  b = 3;
  UCaux1.v = vec_splat( UCcons1, 3 );
  UCaux2.v = UCcons1;
  for( i=0; i< 16; i++ )
    if (UCaux1.e[i] != UCaux2.e[b])
      err++;
  if (err)
    printf("Function vec_splat [type unsigned char]   ===> Error\n");
  else
    printf("Function vec_splat [type unsigned char]   ===> OK\n");

  err = 0;
  b = 3;
  Saux1.v = vec_splat( Scons1, 3 );
  Saux2.v = Scons1;
  for( i=0; i< 8; i++ )
    if (Saux1.e[i] != Saux2.e[b])
      err++;
  if (err)
    printf("Function vec_splat [type short]           ===> Error\n");
  else
    printf("Function vec_splat [type short]           ===> OK\n");

  err = 0;
  b = 3;
  USaux1.v = vec_splat( UScons1, 3 );
  USaux2.v = UScons1;
  for( i=0; i< 8; i++ )
    if (USaux1.e[i] != USaux2.e[b])
      err++;
  if (err)
    printf("Function vec_splat [type unsigned short]  ===> Error\n");
  else
    printf("Function vec_splat [type unsigned short]  ===> OK\n");

  err = 0;
  b = 3;
  Iaux1.v = vec_splat( Icons1, 3 );
  Iaux2.v = Icons1;
  for( i=0; i< 4; i++ )
    if (Iaux1.e[i] != Iaux2.e[b])
      err++;
  if (err)
    printf("Function vec_splat [type integer]         ===> Error\n");
  else
    printf("Function vec_splat [type integer]         ===> OK\n");

  err = 0;
  b = 3;
  UIaux1.v = vec_splat( UIcons1, 3 );
  UIaux2.v = UIcons1;
  for( i=0; i< 4; i++ )
    if (UIaux1.e[i] != UIaux2.e[b])
      err++;
  if (err)
    printf("Function vec_splat [type unsigned int]    ===> Error\n");
  else
    printf("Function vec_splat [type unsigned int]    ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
  b = 3;
  Faux1.v = vec_splat( Fcons1, 3 );
  Faux2.v = Fcons1;
  for( i=0; i< 4; i++ )
    if (Faux1.e[i] != Faux2.e[b])
      err++;
  if (err)
    printf("Function vec_splat [type float]           ===> Error\n");
  else
    printf("Function vec_splat [type float]           ===> OK\n");
#endif

/*    Function vec_splat_s8    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux = 15;
  Caux1.v = vec_splat_s8( 15 );
  for( i=0; i< 16; i++ )
    if (Caux1.e[i] != Caux)
      err++;
  if (err)
    printf("Function vec_splat_s8 [type char]         ===> Error\n");
  else
    printf("Function vec_splat_s8 [type char]         ===> OK\n");

/*    Function vec_splat_s16    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Saux = 15;
  Saux1.v = vec_splat_s16( 15 );
  for( i=0; i< 8; i++ )
    if (Saux1.e[i] != Saux)
      err++;
  if (err)
    printf("Function vec_splat_s16 [type short]       ===> Error\n");
  else
    printf("Function vec_splat_s16 [type short]       ===> OK\n");

/*    Function vec_splat_s32    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Iaux = 15;
  Iaux1.v = vec_splat_s32( 15 );
  for( i=0; i< 4; i++ )
    if (Iaux1.e[i] != Iaux)
      err++;
  if (err)
    printf("Function vec_splat_s32 [type integer]     ===> Error\n");
  else
    printf("Function vec_splat_s32 [type integer]     ===> OK\n");

/*    Function vec_splat_u8    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  UCaux = 15;
  UCaux1.v = vec_splat_u8( 15 );
  for( i=0; i< 16; i++ )
    if (UCaux1.e[i] != UCaux)
      err++;
  if (err)
    printf("Function vec_splat_u8 [type unsig. char]  ===> Error\n");
  else
    printf("Function vec_splat_u8 [type unsig. char]  ===> OK\n");

/*    Function vec_splat_u16    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  USaux = 15;
  USaux1.v = vec_splat_u16( 15 );
  for( i=0; i< 8; i++ )
    if (USaux1.e[i] != Saux)
      err++;
  if (err)
    printf("Function vec_splat_u16 [type unsg. short] ===> Error\n");
  else
    printf("Function vec_splat_u16 [type unsg. short] ===> OK\n");

/*    Function vec_splat_u32    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  UIaux = 15;
  UIaux1.v = vec_splat_u32( 15 );
  for( i=0; i< 4; i++ )
    if (UIaux1.e[i] != UIaux)
      err++;
  if (err)
    printf("Function vec_splat_u32 [type unsig. int]  ===> Error\n");
  else
    printf("Function vec_splat_u32 [type unsig. int]  ===> OK\n");

/*    Function vec_sr    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_sr( Ccons3, UCcons3 );
  Caux2.v = Ccons3;
  UCaux3.v = UCcons3;
  for( i=0; i< 16; i++ )
  {
    SHOunion1.sc[0] = Caux2.e[i];
    SHOunion1.uc[0] = SHOunion1.uc[0] >> (UCaux3.e[i]%8);
    if (Caux1.e[i] != SHOunion1.sc[0])
      err++;
  }
  if (err)
    printf("Function vec_sr [type char]               ===> Error\n");
  else
    printf("Function vec_sr [type char]               ===> OK\n");

  err = 0;
  UCaux1.v = vec_sr( UCcons1, UCcons3 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons3;
  for( i=0; i< 16; i++ )
  {
    UCaux = UCaux2.e[i] >> (UCaux3.e[i]%8);
    if (UCaux1.e[i] != UCaux)
      err++;
  }
  if (err)
    printf("Function vec_sr [type unsigned char]      ===> Error\n");
  else
    printf("Function vec_sr [type unsigned char]      ===> OK\n");

  err = 0;
  Saux1.v = vec_sr( Scons3, UScons3 );
  Saux2.v = Scons3;
  USaux3.v = UScons3;
  for( i=0; i< 8; i++ )
  {
    SHOunion1.ss = Saux2.e[i];
    SHOunion1.us = SHOunion1.us >> (USaux3.e[i]%16);
    if (Saux1.e[i] != SHOunion1.ss)
      err++;
  }
  if (err)
    printf("Function vec_sr [type short]              ===> Error\n");
  else
    printf("Function vec_sr [type short]              ===> OK\n");

  err = 0;
  USaux1.v = vec_sr( UScons1, UScons3 );
  USaux2.v = UScons1;
  USaux3.v = UScons3;
  for( i=0; i< 8; i++ )
  {
    USaux = USaux2.e[i] >> (USaux3.e[i]%16);
    if (USaux1.e[i] != USaux)
      err++;
  }
  if (err)
    printf("Function vec_sr [type unsigned short]     ===> Error\n");
  else
    printf("Function vec_sr [type unsigned short]     ===> OK\n");

  err = 0;
  Iaux1.v = vec_sr( Icons3, UIcons3 );
  Iaux2.v = Icons3;
  UIaux3.v = UIcons3;
  for( i=0; i< 4; i++ )
  {
    INTunion1.si = Iaux2.e[i];
    INTunion1.ui = INTunion1.ui >> (UIaux3.e[i]%32);
    if (Iaux1.e[i] != INTunion1.si)
      err++;
  }
  if (err)
    printf("Function vec_sr [type integer]            ===> Error\n");
  else
    printf("Function vec_sr [type integer]            ===> OK\n");

  err = 0;
  UIaux1.v = vec_sr( UIcons1, UIcons3 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons3;
  for( i=0; i< 4; i++ )
  {
    UIaux = UIaux2.e[i] >> (UIaux3.e[i]%32);
    if (UIaux1.e[i] != UIaux)
      err++;
  }
  if (err)
    printf("Function vec_sr [type unsigned int]       ===> Error\n");
  else
    printf("Function vec_sr [type unsigned int]       ===> OK\n");

/*    Function vec_sra    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_sra( Ccons3, UCcons3 );
  Caux2.v = Ccons3;
  UCaux3.v = UCcons3;
  for( i=0; i< 16; i++ )
  {
    Caux = Caux2.e[i] >> (UCaux3.e[i]%8);
    if (Caux1.e[i] != Caux)
      err++;
  }
  if (err)
    printf("Function vec_sra [type char]              ===> Error\n");
  else
    printf("Function vec_sra [type char]              ===> OK\n");

  err = 0;
  UCaux1.v = vec_sra( UCcons1, UCcons3 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons3;
  for( i=0; i< 16; i++ )
  {
    INTunion1.uc[0] = UCaux2.e[i];
    INTunion1.sc[0] = INTunion1.sc[0] >> (UCaux3.e[i]%8);
    if (UCaux1.e[i] != INTunion1.uc[0])
      err++;
  }
  if (err)
    printf("Function vec_sra [type unsigned char]     ===> Error\n");
  else
    printf("Function vec_sra [type unsigned char]     ===> OK\n");

  err = 0;
  Saux1.v = vec_sra( Scons3, UScons3 );
  Saux2.v = Scons3;
  USaux3.v = UScons3;
  for( i=0; i< 8; i++ )
  {
    Saux = Saux2.e[i] >> (USaux3.e[i]%16);
    if (Saux1.e[i] != Saux)
      err++;
  }
  if (err)
    printf("Function vec_sra [type short]             ===> Error\n");
  else
    printf("Function vec_sra [type short]             ===> OK\n");

  err = 0;
  USaux1.v = vec_sra( UScons1, UScons3 );
  USaux2.v = UScons1;
  USaux3.v = UScons3;
  for( i=0; i< 8; i++ )
  {
    INTunion1.us[0] = USaux2.e[i];
    INTunion1.ss[0] = INTunion1.ss[0] >> (USaux3.e[i]%16);
    if (USaux1.e[i] != INTunion1.us[0])
      err++;
  }
  if (err)
    printf("Function vec_sra [type unsigned short]    ===> Error\n");
  else
    printf("Function vec_sra [type unsigned short]    ===> OK\n");

  err = 0;
  Iaux1.v = vec_sra( Icons3, UIcons3 );
  Iaux2.v = Icons3;
  UIaux3.v = UIcons3;
  for( i=0; i< 4; i++ )
  {
    Iaux = Iaux2.e[i] >> (UIaux3.e[i]%32);
    if (Iaux1.e[i] != Iaux)
      err++;
  }
  if (err)
    printf("Function vec_sra [type integer]           ===> Error\n");
  else
    printf("Function vec_sra [type integer]           ===> OK\n");

  err = 0;
  UIaux1.v = vec_sra( UIcons1, UIcons3 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons3;
  for( i=0; i< 4; i++ )
  {
    INTunion1.ui = UIaux2.e[i];
    INTunion1.si = INTunion1.si >> (UIaux3.e[i]%32);
    if (UIaux1.e[i] != INTunion1.ui)
      err++;
  }
  if (err)
    printf("Function vec_sra [type unsigned int]      ===> Error\n");
  else
    printf("Function vec_sra [type unsigned int]      ===> OK\n");

/*    Function vec_srl    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_srl( Ccons1, UCcons2 );
  Caux2.v = Ccons1;
  UCaux3.v = UCcons2;
  b = UCaux3.e[15] & 0x7;
  for( i=0; i< 15; i++ )
    if ((UCaux3.e[i] & 0x7)!=b)
      err++;
  if (err)
  {
    printf("The three low-order bits of all byte elements in b must be the same\n");
    printf("otherwise the value into d is undefined\n");
  }
  else
  {
    Caux = 0;
    for( i=0; i< 16; i++ )
    {
      INTunion1.sc[0] = Caux2.e[i];
      Caux = Caux | (INTunion1.uc[0]>>b);
      if (Caux != Caux1.e[i])
        err++;
      Caux = INTunion1.uc[0]<<(8-b);
    }
    if (err)
      printf("Function vec_srl [type char]              ===> Error\n");
    else
      printf("Function vec_srl [type char]              ===> OK\n");
  }

  err = 0;
  UCaux1.v = vec_srl( UCcons1, UCcons2 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons2;
  b = UCaux3.e[15] & 0x7;
  for( i=0; i< 15; i++ )
    if ((UCaux3.e[i] & 0x7)!=b)
      err++;
  if (err)
  {
    printf("The three low-order bits of all byte elements in b must be the same\n");
    printf("otherwise the value into d is undefined\n");
  }
  else
  {
    UCaux = 0;
    for( i=0; i< 16; i++ )
    {
      UCaux = UCaux | (UCaux2.e[i]>>b);
      if (UCaux != UCaux1.e[i])
        err++;
      UCaux = UCaux2.e[i]<<(8-b);
    }
    if (err)
      printf("Function vec_srl [type unsigned char]     ===> Error\n");
    else
      printf("Function vec_srl [type unsigned char]     ===> OK\n");
  }

  err = 0;
  Saux1.v = vec_srl( Scons1, UCcons2 );
  Saux2.v = Scons1;
  UCaux3.v = UCcons2;
  b = UCaux3.e[15] & 0x7;
  for( i=0; i< 15; i++ )
    if ((UCaux3.e[i] & 0x7)!=b)
      err++;
  if (err)
  {
    printf("The three low-order bits of all byte elements in b must be the same\n");
    printf("otherwise the value into d is undefined\n");
  }
  else
  {
    Saux = 0;
    for( i=0; i< 8; i++ )
    {
      INTunion1.ss[0] = Saux2.e[i];
      Saux = Saux | (INTunion1.us[0]>>b);
      if (Saux != Saux1.e[i])
        err++;
      Saux = INTunion1.us[0]<<(16-b);
    }
    if (err)
      printf("Function vec_srl [type short]             ===> Error\n");
    else
      printf("Function vec_srl [type short]             ===> OK\n");
  }

  err = 0;
  USaux1.v = vec_srl( UScons1, UCcons2 );
  USaux2.v = UScons1;
  UCaux3.v = UCcons2;
  b = UCaux3.e[15] & 0x7;
  for( i=0; i< 15; i++ )
    if ((UCaux3.e[i] & 0x7)!=b)
      err++;
  if (err)
  {
    printf("The three low-order bits of all byte elements in b must be the same\n");
    printf("otherwise the value into d is undefined\n");
  }
  else
  {
    USaux = 0;
    for( i=0; i< 8; i++ )
    {
      USaux = USaux | (USaux2.e[i]>>b);
      if (USaux != USaux1.e[i])
        err++;
      USaux = USaux2.e[i]<<(16-b);
    }
    if (err)
      printf("Function vec_srl [type unsigned short]    ===> Error\n");
    else
      printf("Function vec_srl [type unsigned short]    ===> OK\n");
  }

  err = 0;
  Iaux1.v = vec_srl( Icons1, UCcons2 );
  Iaux2.v = Icons1;
  UCaux3.v = UCcons2;
  b = UCaux3.e[15] & 0x7;
  for( i=0; i< 15; i++ )
    if ((UCaux3.e[i] & 0x7)!=b)
      err++;
  if (err)
  {
    printf("The three low-order bits of all byte elements in b must be the same\n");
    printf("otherwise the value into d is undefined\n");
  }
  else
  {
    Iaux = 0;
    for( i=0; i< 4; i++ )
    {
      INTunion1.si = Iaux2.e[i];
      Iaux = Iaux | (INTunion1.ui>>b);
      if (Iaux != Iaux1.e[i])
        err++;
      Iaux = INTunion1.ui<<(32-b);
    }
    if (err)
      printf("Function vec_srl [type integer]           ===> Error\n");
    else
      printf("Function vec_srl [type integer]           ===> OK\n");
  }

  err = 0;
  UIaux1.v = vec_srl( UIcons1, UCcons2 );
  UIaux2.v = UIcons1;
  UCaux3.v = UCcons2;
  b = UCaux3.e[15] & 0x7;
  for( i=0; i< 15; i++ )
    if ((UCaux3.e[i] & 0x7)!=b)
      err++;
  if (err)
  {
    printf("The three low-order bits of all byte elements in b must be the same\n");
    printf("otherwise the value into d is undefined\n");
  }
  else
  {
    UIaux = 0;
    for( i=0; i< 4; i++ )
    {
      UIaux = UIaux | (UIaux2.e[i]>>b);
      if (UIaux != UIaux1.e[i])
        err++;
      UIaux = UIaux2.e[i]<<(32-b);
    }
    if (err)
      printf("Function vec_srl [type unsigned int]      ===> Error\n");
    else
      printf("Function vec_srl [type unsigned int]      ===> OK\n");
  }

/*    Function vec_sro    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_sro( Ccons3, Ccons1 );
  Caux2.v = Ccons3;
  Caux3.v = Ccons1;
  b = (Caux3.e[15] & 0x78) >>3;
  for( i=0; i< 16; i++ )
  {
    if ((i-b)>=0)
    {
      if (Caux1.e[i] != Caux2.e[i-b])
        err++;
    }
    else
    {
      if (Caux1.e[i] != 0)
        err++;
    }
  }
  if (err)
    printf("Function vec_sro [type char]              ===> Error\n");
  else
    printf("Function vec_sro [type char]              ===> OK\n");

  err = 0;
  UCaux1.v = vec_sro( UCcons3, UCcons1 );
  UCaux2.v = UCcons3;
  UCaux3.v  = UCcons1;
  b = (UCaux3.e[15] & 0x78) >>3;
  for( i=0; i< 16; i++ )
  {
    if ((i-b)>=0)
    {
      if (UCaux1.e[i] != UCaux2.e[i-b])
        err++;
    }
    else
    {
      if (UCaux1.e[i] != 0)
        err++;
    }
  }
  if (err)
    printf("Function vec_sro [type unsigned char]     ===> Error\n");
  else
    printf("Function vec_sro [type unsigned char]     ===> OK\n");

  err = 0;
  Saux1.v = vec_sro( Scons3, Ccons1 );
  Saux2.v = Scons3;
  Caux3.v = Ccons1;
  b = (Caux3.e[15] & 0x78) >>3;
  for( i=0; i< 16; i++ )
  {
    SHOunion1.ss = Saux1.e[i/2];
    if ((i-b)>=0)
    {
      SHOunion2.ss = Saux2.e[(i-b)/2];
      if (SHOunion1.sc[i%2] != SHOunion2.sc[(i-b)%2])
        err++;
    }
    else
    {
      if (SHOunion1.sc[i%2] != 0)
        err++;
    }
  }
  if (err)
    printf("Function vec_sro [type short]             ===> Error\n");
  else
    printf("Function vec_sro [type short]             ===> OK\n");

  err = 0;
  USaux1.v = vec_sro( UScons3, UCcons1 );
  USaux2.v = UScons3;
  UCaux3.v = UCcons1;
  b = (UCaux3.e[15] & 0x78) >>3;
  for( i=0; i< 16; i++ )
  {
    SHOunion1.us = USaux1.e[i/2];
    if ((i-b)>=0)
    {
      SHOunion2.us = USaux2.e[(i-b)/2];
      if (SHOunion1.uc[i%2] != SHOunion2.uc[(i-b)%2])
        err++;
    }
    else
    {
      if (SHOunion1.uc[i%2] != 0)
        err++;
    }
  }
  if (err)
    printf("Function vec_sro [type unsigned short]    ===> Error\n");
  else
    printf("Function vec_sro [type unsigned short]    ===> OK\n");

  err = 0;
  Iaux1.v = vec_sro( Icons3, Ccons1 );
  Iaux2.v = Icons3;
  Caux3.v = Ccons1;
  b = (Caux3.e[15] & 0x78) >>3;
  for( i=0; i< 16; i++ )
  {
    INTunion1.si = Iaux1.e[i/4];
    if ((i-b)>=0)
    {
      INTunion2.si = Iaux2.e[(i-b)/4];
      if (INTunion1.sc[i%4] != INTunion2.sc[(i-b)%4])
        err++;
    }
    else
    {
      if (INTunion1.sc[i%4] != 0)
        err++;
    }
  }
  if (err)
    printf("Function vec_sro [type integer]           ===> Error\n");
  else
    printf("Function vec_sro [type integer]           ===> OK\n");

  err = 0;
  UIaux1.v = vec_sro( UIcons3, UCcons1 );
  UIaux2.v = UIcons3;
  UCaux3.v = UCcons1;
  b = (UCaux3.e[15] & 0x78) >>3;
  for( i=0; i< 16; i++ )
  {
    INTunion1.ui = UIaux1.e[i/4];
    if ((i-b)>=0)
    {
      INTunion2.ui = UIaux2.e[(i-b)/4];
      if (INTunion1.uc[i%4] != INTunion2.sc[(i-b)%4])
        err++;
    }
    else
    {
      if (INTunion1.uc[i%4] != 0)
        err++;
    }
  }
  if (err)
    printf("Function vec_sro [type unsigned int]      ===> Error\n");
  else
    printf("Function vec_sro [type unsigned int]      ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
  Faux1.v = vec_sro( Fcons3, Ccons1 );
  Faux2.v = Fcons3;
  Caux3.v = Ccons1;
  b = (Caux3.e[15] & 0x78) >>3;
  for( i=0; i< 16; i++ )
  {
    INTunion1.f = Faux1.e[i/4];
    if ((i-b)>=0)
    {
      INTunion2.f = Faux2.e[(i-b)/4];
      if (INTunion1.sc[i%4] != INTunion2.sc[(i-b)%4])
        err++;
    }
    else
    {
      if (INTunion1.sc[i%4] != 0)
        err++;
    }
  }
  if (err)
    printf("Function vec_sro [type float]             ===> Error\n");
  else
    printf("Function vec_sro [type float]             ===> OK\n");
#endif

/*    Function vec_st    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  UCaux1.v = UCcons1;
  vec_st( UCaux1.v, 0, UCmem );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (UCaux1.e[i]==UCmem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_st [type unsigned char]      ===> Error\n");
  else
    printf("Function vec_st [type unsigned char]      ===> OK\n");
  
  err = 0;
  Caux1.v = Ccons1;
  vec_st( Caux1.v, 0, Cmem );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (Caux1.e[i]==Cmem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_st [type char]               ===> Error\n");
  else
    printf("Function vec_st [type char]               ===> OK\n");
  
  err = 0;
  USaux1.v = UScons3;
  vec_st( USaux1.v, 0, USmem );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (USaux1.e[i]==USmem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_st [type unsigned short]     ===> Error\n");
  else
    printf("Function vec_st [type unsigned short]     ===> OK\n");
  
  err = 0;
  Saux1.v = Scons1;
  vec_st( Saux1.v, 0, Smem );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (Saux1.e[i]==Smem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_st [type short]              ===> Error\n");
  else
    printf("Function vec_st [type short]              ===> OK\n");
  
  err = 0;
  UIaux1.v = UIcons1;
  vec_st( UIaux1.v, 0, UImem );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (UIaux1.e[i]==UImem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_st [type unsigned int]       ===> Error\n");
  else
    printf("Function vec_st [type unsigned int]       ===> OK\n");
  
  err = 0;
  Iaux1.v = Icons1;
  vec_st( Iaux1.v, 0, Imem );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Iaux1.e[i]==Imem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_st [type int]                ===> Error\n");
  else
    printf("Function vec_st [type int]                ===> OK\n");
  
#if defined TEST_FLOATS
  err = 0;
  Faux1.v = Fcons1;
  vec_st( Faux1.v, 0, Fmem );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Faux1.e[i]==Fmem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_st [type float]              ===> Error\n");
  else
    printf("Function vec_st [type float]              ===> OK\n");
#endif

/*    Function vec_ste    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  b = 11;
  UCaux1.v = UCcons1;
  vec_ste( UCaux1.v, b, UCmem );
  i = b;
  if (UCaux1.e[i]!=UCmem[i]) err++;
  
  if (err)
    printf("Function vec_ste [type unsigned char]     ===> Error\n");
  else
    printf("Function vec_ste [type unsigned char]     ===> OK\n");
  
  err = 0;
  b = 11;
  Caux1.v = Ccons1;
  vec_ste( Caux1.v, b, Cmem );
  i = b;
  if (Caux1.e[i]!=Cmem[i]) err++;
  
  if (err)
    printf("Function vec_ste [type char]              ===> Error\n");
  else
    printf("Function vec_ste [type char]              ===> OK\n");
  
  err = 0;
  b = 11;
  USaux1.v = UScons1;
  vec_ste( USaux1.v, b, USmem );
  i = b/2;
  if (USaux1.e[i]!=USmem[i]) err++;
  if (err)
    printf("Function vec_ste [type unsigned short]    ===> Error\n");
  else
    printf("Function vec_ste [type unsigned short]    ===> OK\n");
  
  err = 0;
  b = 11;
  Saux1.v = Scons1;
  vec_ste( Saux1.v, b, Smem );
  i = b/2;
  if (Saux1.e[i]!=Smem[i]) err++;
  if (err)
    printf("Function vec_ste [type short]             ===> Error\n");
  else
    printf("Function vec_ste [type short]             ===> OK\n");
  
  err = 0;
  b = 11;
  UIaux1.v = UIcons1;
  vec_ste( UIaux1.v, b, UImem );
  i = b/4;
  if (UIaux1.e[i]!=UImem[i]) err++;
  if (err)
    printf("Function vec_ste [type unsigned int]      ===> Error\n");
  else
    printf("Function vec_ste [type unsigned int]      ===> OK\n");
  
  err = 0;
  b = 11;
  Iaux1.v = Icons1;
  vec_ste( Iaux1.v, b, Imem );
  i = b/4;
  if (Iaux1.e[i]!=Imem[i]) err++;
  if (err)
    printf("Function vec_ste [type int]               ===> Error\n");
  else
    printf("Function vec_ste [type int]               ===> OK\n");
  
#if defined TEST_FLOATS
  err = 0;
  b = 11;
  Faux1.v = Fcons1;
  vec_ste( Faux1.v, b, Fmem );
  i = b/4;
  if (Faux1.e[i]!=Fmem[i]) err++;
  if (err)
    printf("Function vec_ste [type float]             ===> Error\n");
  else
    printf("Function vec_ste [type float]             ===> OK\n");
#endif

#if 0
/*    Function vec_stl    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  UCaux1.v = UCcons1;
  vec_stl( UCaux1.v, 0, UCmem );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (UCaux1.e[i]==UCmem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_stl [type unsigned char]     ===> Error\n");
  else
    printf("Function vec_stl [type unsigned char]     ===> OK\n");
  
  err = 0;
  Caux1.v = Ccons1;
  vec_stl( Caux1.v, 0, Cmem );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (Caux1.e[i]==Cmem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_stl [type char]              ===> Error\n");
  else
    printf("Function vec_stl [type char]              ===> OK\n");
  
  err = 0;
  USaux1.v = UScons3;
  vec_stl( USaux1.v, 0, USmem );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (USaux1.e[i]==USmem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_stl [type unsigned short]    ===> Error\n");
  else
    printf("Function vec_stl [type unsigned short]    ===> OK\n");
  
  err = 0;
  Saux1.v = Scons1;
  vec_stl( Saux1.v, 0, Smem );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (Saux1.e[i]==Smem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_stl [type short]             ===> Error\n");
  else
    printf("Function vec_stl [type short]             ===> OK\n");
  
  err = 0;
  UIaux1.v = UIcons1;
  vec_stl( UIaux1.v, 0, UImem );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (UIaux1.e[i]==UImem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_stl [type unsigned int]      ===> Error\n");
  else
    printf("Function vec_stl [type unsigned int]      ===> OK\n");
  
  err = 0;
  Iaux1.v = Icons1;
  vec_stl( Iaux1.v, 0, Imem );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Iaux1.e[i]==Imem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_stl [type int]               ===> Error\n");
  else
    printf("Function vec_stl [type int]               ===> OK\n");
  
#if defined TEST_FLOATS
  err = 0;
  Faux1.v = Fcons1;
  vec_stl( Faux1.v, 0, Fmem );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Faux1.e[i]==Fmem[i]);
  }
  if (Iaux!=1) err++;
  
  if (err)
    printf("Function vec_stl [type float]             ===> Error\n");
  else
    printf("Function vec_stl [type float]             ===> OK\n");
#endif
#endif // #if 0

  /* Free dynamic vector variables */
  free_vec( UCmem );
  free_vec( Cmem );
  free_vec( USmem );
  free_vec( Smem );
  free_vec( UImem );
  free_vec( Imem );
#if defined TEST_FLOATS
  free_vec( Fmem );
#endif

  return 0;
}




int part4( )
{
  TvecChar      Caux1,  Caux2,  Caux3;//,  Caux4;
  TvecUChar     UCaux1, UCaux2, UCaux3;//, UCaux4;
  TvecShort     Saux1,  Saux2,  Saux3;//,  Saux4;
  TvecUShort    USaux1, USaux2, USaux3;//, USaux4;
  TvecInt       Iaux1,  Iaux2,  Iaux3;//,  Iaux4;
  TvecUInt      UIaux1, UIaux2, UIaux3;//, UIaux4;
#if defined TEST_FLOATS
  TvecFloat     Faux1,  Faux2,  Faux3;//,  Faux4;
#endif

  int                  i, err, j;//, b, bAux;
//  signed   int         Ivec1, Ivec2, Ivec3;
//  signed   short       *Svec1;
//  unsigned int         *UIvec1;
//  unsigned short       *USvec1;
//  unsigned char        *UCvec1;
#if defined TEST_FLOATS
//  float                *Fvec1;
#endif

  /* For saturated rutines */
  long long int         LLaux;

#if defined TEST_FLOATS
  float                 Faux;
#endif
  signed   int          Iaux;//, I1, I2;
  unsigned int          UIaux;//, UI1, UI2;
  signed   short        Saux;
  unsigned short        USaux;
  signed   char         Caux;
  unsigned char         UCaux;

/*
  union
  {
    float          f;
    signed   int   si;
    unsigned int   ui;
    signed   short ss[2];
    unsigned short us[2];
    signed   char  sc[4];
    unsigned char  uc[4];
  } INTunion1, INTunion2;

  union
  {
    signed   short  ss;
    unsigned short  us;
    signed   char   sc[2];
    unsigned char   uc[2];
  } SHOunion1, SHOunion2;
*/

#if defined (GCC_COMPILER)
  vector signed char    Ccons1   = (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
  vector signed char    Ccons2   = (vector signed char){1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1};
  vector signed char    Ccons3   = (vector signed char){-128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127};
  vector unsigned char  UCcons1  = (vector unsigned char){248, 249, 250, 251, 252, 253, 254, 255, 0, 1, 2, 3, 4, 5, 6, 7};
  vector unsigned char  UCcons2  = (vector unsigned char){2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2};
  vector unsigned char  UCcons3  = (vector unsigned char){1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8};
  vector signed short   Scons1   = (vector signed short){-4, -3, -2, -1, 0, 1, 2, 3};
  vector signed short   Scons2   = (vector signed short){-32768, 10000, 1, 1, 1, 1, -10000, -10000};
  vector signed short   Scons3   = (vector signed short){-32768, 32767, -32768, 32767, -32768, 32767, -32768, 32767};
  vector unsigned short UScons1  = (vector unsigned short){65532, 65533, 65534, 65535, 0, 1, 2, 3};
  vector unsigned short UScons2  = (vector unsigned short){1, 1, 1, 1, 1, 1, 1, 1};
  vector unsigned short UScons3  = (vector unsigned short){1, 2, 3, 4, 1, 2, 3, 4};
  vector signed int     Icons1   = (vector signed int){-4, -1, 1, 4};
  vector signed int     Icons2   = (vector signed int){1, 1, 1, 1};
  vector signed int     Icons3   = (vector signed int){0x80000000, 0x7FFFFFFF, 0x80000000, 0x7FFFFFFF};
  vector unsigned int   UIcons1  = (vector unsigned int){0xFFFFFFFE, 0xFFFFFFFF, 0, 1};
  vector unsigned int   UIcons2  = (vector unsigned int){1, 1, 1, 1};
  vector unsigned int   UIcons3  = (vector unsigned int){1, 2, 1, 2};

#if defined TEST_FLOATS
  vector float          Fcons1   = (vector float){-1.5, 1.0, 0.5, -3.999};
  vector float          Fcons2   = (vector float){1.0, 1.0, 1.0, 1.0};
  vector float          Fcons3   = (vector float){100000000000.0, 1.0, -1.0, -1234567890.0};
#endif

#elif defined (MAC_COMPILER) || defined(XLC_COMPILER)
  vector signed char    Ccons1   = (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
  vector signed char    Ccons2   = (vector signed char)(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1);
  vector signed char    Ccons3   = (vector signed char)(-128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127);
  vector unsigned char  UCcons1  = (vector unsigned char)(248, 249, 250, 251, 252, 253, 254, 255, 0, 1, 2, 3, 4, 5, 6, 7);
  vector unsigned char  UCcons2  = (vector unsigned char)(2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2);
  vector unsigned char  UCcons3  = (vector unsigned char)(1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8);
  vector signed short   Scons1   = (vector signed short)(-4, -3, -2, -1, 0, 1, 2, 3);
  vector signed short   Scons2   = (vector signed short)(-32768, 10000, 1, 1, 1, 1, -10000, -10000);
  vector signed short   Scons3   = (vector signed short)(-32768, 32767, -32768, 32767, -32768, 32767, -32768, 32767);
  vector unsigned short UScons1  = (vector unsigned short)(65532, 65533, 65534, 65535, 0, 1, 2, 3);
  vector unsigned short UScons2  = (vector unsigned short)(1, 1, 1, 1, 1, 1, 1, 1);
  vector unsigned short UScons3  = (vector unsigned short)(1, 2, 3, 4, 1, 2, 3, 4);
  vector signed int     Icons1   = (vector signed int)(-4, -1, 1, 4);
  vector signed int     Icons2   = (vector signed int)(1, 1, 1, 1);
  vector signed int     Icons3   = (vector signed int)(0x80000000, 0x7FFFFFFF, 0x80000000, 0x7FFFFFFF);
  vector unsigned int   UIcons1  = (vector unsigned int)(0xFFFFFFFE, 0xFFFFFFFF, 0, 1);
  vector unsigned int   UIcons2  = (vector unsigned int)(1, 1, 1, 1);
  vector unsigned int   UIcons3  = (vector unsigned int)(1, 2, 1, 2);

#if defined TEST_FLOATS
  vector float          Fcons1   = (vector float)(-1.5, 1.0, 0.5, -3.999);
  vector float          Fcons2   = (vector float)(1.0, 1.0, 1.0, 1.0);
  vector float          Fcons3   = (vector float)(100000000000.0, 1.0, -1.0, -1234567890.0);
#endif

#endif


/*    Function vec_sub    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_sub( Ccons1, Ccons2 );
  Caux2.v = Ccons1;
  Caux3.v = Ccons2;
  for( i=0; i< 16; i++ )
  {
    Caux = Caux2.e[i] - Caux3.e[i];
    if (Caux1.e[i] != Caux)
        err++;
  }
  if (err)
    printf("Function vec_sub [type char]              ===> Error\n");
  else
    printf("Function vec_sub [type char]              ===> OK\n");

  err = 0;
  UCaux1.v = vec_sub( UCcons1, UCcons2 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons2;
  for( i=0; i< 16; i++ )
  {
    UCaux = UCaux2.e[i] - UCaux3.e[i];
    if (UCaux1.e[i] != UCaux)
        err++;
  }
  if (err)
    printf("Function vec_sub [type unsigned char]     ===> Error\n");
  else
    printf("Function vec_sub [type unsigned char]     ===> OK\n");

  err = 0;
  Saux1.v = vec_sub( Scons1, Scons2 );
  Saux2.v = Scons1;
  Saux3.v = Scons2;
  for( i=0; i< 8; i++ )
  {
    Saux = Saux2.e[i] - Saux3.e[i];
    if (Saux1.e[i] != Saux)
        err++;
  }
  if (err)
    printf("Function vec_sub [type short]             ===> Error\n");
  else
    printf("Function vec_sub [type short]             ===> OK\n");

  err = 0;
  USaux1.v = vec_sub( UScons1, UScons2 );
  USaux2.v = UScons1;
  USaux3.v = UScons2;
  for( i=0; i< 8; i++ )
  {
    USaux = USaux2.e[i] - USaux3.e[i];
    if (USaux1.e[i] != USaux)
        err++;
  }
  if (err)
    printf("Function vec_sub [type unsigned short]    ===> Error\n");
  else
    printf("Function vec_sub [type unsigned short]    ===> OK\n");

  err = 0;
  Iaux1.v = vec_sub( Icons1, Icons2 );
  Iaux2.v = Icons1;
  Iaux3.v = Icons2;
  for( i=0; i< 4; i++ )
  {
    Iaux = Iaux2.e[i] - Iaux3.e[i];
    if (Iaux1.e[i] != Iaux)
        err++;
  }
  if (err)
    printf("Function vec_sub [type integer]           ===> Error\n");
  else
    printf("Function vec_sub [type integer]           ===> OK\n");

  err = 0;
  UIaux1.v = vec_sub( UIcons1, UIcons2 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons2;
  for( i=0; i< 4; i++ )
  {
    UIaux = UIaux2.e[i] - UIaux3.e[i];
    if (UIaux1.e[i] != UIaux)
        err++;
  }
  if (err)
    printf("Function vec_sub [type unsigned int]      ===> Error\n");
  else
    printf("Function vec_sub [type unsigned int]      ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
  Faux1.v = vec_sub( Fcons1, Fcons2 );
  Faux2.v = Fcons1;
  Faux3.v = Fcons2;
  for( i=0; i< 4; i++ )
  {
    Faux = Faux2.e[i] - Faux3.e[i];
    if (Faux1.e[i] != Faux)
        err++;
  }
  if (err)
    printf("Function vec_sub [type float]             ===> Error\n");
  else
    printf("Function vec_sub [type float]             ===> OK\n");
#endif

/*    Function vec_subc    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  UIaux1.v = vec_subc( UIcons2, UIcons3 );
  UIaux2.v = UIcons2;
  UIaux3.v = UIcons3;
  for( i=0; i< 4; i++ )
  {
    if (UIaux3.e[i]>UIaux2.e[i])
    {
      if (UIaux1.e[i] != 0)
        err++;
    }
    else
    {
      if (UIaux1.e[i] != 1)
        err++;
    }
  }
  if (err)
    printf("Function vec_subc [type unsigned int]     ===> Error\n");
  else
    printf("Function vec_subc [type unsigned int]     ===> OK\n");

/*    Function vec_subs    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = vec_subs( Ccons1, Ccons3 );
  Caux2.v = Ccons1;
  Caux3.v = Ccons3;
  for( i=0; i< 16; i++ )
  {
    Caux = (signed char)Caux2.e[i]-Caux3.e[i];
    if ((Caux2.e[i]>=0)&&(Caux3.e[i]<0))
    {
      if (Caux< Caux2.e[i])
        Caux=0x7F;
    }
    else if ((Caux2.e[i]<0)&&(Caux3.e[i]>0))
    {
      if (Caux> Caux2.e[i])
        Caux=0x80;
    } 
    if (Caux1.e[i] != Caux)
      err++;
  }
  if (err)
    printf("Function vec_subs [type char]             ===> Error\n");
  else
    printf("Function vec_subs [type char]             ===> OK\n");

  err = 0;
  UCaux1.v = vec_subs( UCcons1, UCcons3 );
  UCaux2.v = UCcons1;
  UCaux3.v = UCcons3;
  for( i=0; i< 16; i++ )
  {
    UCaux = (unsigned char)(UCaux2.e[i]-UCaux3.e[i]);
    if (UCaux> UCaux2.e[i])
      UCaux=0;
    if (UCaux1.e[i] != UCaux)
      err++;
  }
  if (err)
    printf("Function vec_subs [type unsigned char]    ===> Error\n");
  else
    printf("Function vec_subs [type unsigned char]    ===> OK\n");

  err = 0;
  Saux1.v = vec_subs( Scons1, Scons3 );
  Saux2.v = Scons1;
  Saux3.v = Scons3;
  for( i=0; i< 8; i++ )
  {
    Saux = (signed short)(Saux2.e[i] - Saux3.e[i]);
    if ((Saux2.e[i]>=0)&&(Saux3.e[i]<0))
    {
      if (Saux< Saux2.e[i])
        Saux=0x7FFF;
    }
    else if ((Saux2.e[i]<0)&&(Saux3.e[i]>0))
    {
      if (Saux> Saux2.e[i])
        Saux=0x8000;
    } 
    if (Saux1.e[i] != Saux)
      err++;
  }
  if (err)
    printf("Function vec_subs [type short]            ===> Error\n");
  else
    printf("Function vec_subs [type short]            ===> OK\n");

  err = 0;
  USaux1.v = vec_subs( UScons1, UScons3 );
  USaux2.v = UScons1;
  USaux3.v = UScons3;
  for( i=0; i< 8; i++ )
  {
    USaux = (unsigned short)(USaux2.e[i] - USaux3.e[i]);
    if (USaux> USaux2.e[i])
      USaux=0x0;
    if (USaux1.e[i] != USaux)
      err++;
  }
  if (err)
    printf("Function vec_subs [type unsigned short]   ===> Error\n");
  else
    printf("Function vec_subs [type unsigned short]   ===> OK\n");


  err = 0;
  Iaux1.v = vec_subs( Icons1, Icons3 );
  Iaux2.v = Icons1;
  Iaux3.v = Icons3;
  for( i=0; i< 4; i++ )
  {
    Iaux = (signed int)(Iaux2.e[i] - Iaux3.e[i]);
    if ((Iaux2.e[i]>=0)&&(Iaux3.e[i]<0))
    {
      if (Iaux< Iaux2.e[i])
        Iaux=0x7FFFFFFF;
    }
    else if ((Iaux2.e[i]<0)&&(Iaux3.e[i]>0))
    {
      if (Iaux> Iaux2.e[i])
      {
        printf("%d > %d\n", Iaux, Iaux2.e[i]);
        Iaux=0x80000000;
      }
    } 
    if (Iaux1.e[i] != Iaux)
      err++;
  }
  if (err)
    printf("Function vec_subs [type integer]          ===> Error\n");
  else
    printf("Function vec_subs [type integer]          ===> OK\n");

  err = 0;
  UIaux1.v = vec_subs( UIcons1, UIcons3 );
  UIaux2.v = UIcons1;
  UIaux3.v = UIcons3;
  for( i=0; i< 4; i++ )
  {
    UIaux = (unsigned int)(UIaux2.e[i] - UIaux3.e[i]);
    if (UIaux> UIaux2.e[i])
      UIaux=0x0;
    if (UIaux1.e[i] != UIaux)
      err++;
  }
  if (err)
    printf("Function vec_subs [type unsigned int]     ===> Error\n");
  else
    printf("Function vec_subs [type unsigned int]     ===> OK\n");

/*    Function vec_sum4s    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Iaux1.v = vec_sum4s( Ccons2, Icons2 );
  Caux1.v = Ccons2;
  Iaux2.v = Icons2;
  for( i=0; i< 4; i++ )
  {
    Iaux = Iaux2.e[i];
    for( j=0; j< 4; j++ )
      Iaux = Iaux + Caux1.e[4*i+j];
    if (Iaux1.e[i] != Iaux)
        err++;
  }
  if (err)
    printf("Function vec_sum4s [type char]            ===> Error\n");
  else
    printf("Function vec_sum4s [type char]            ===> OK\n");

  err = 0;
  UIaux1.v = vec_sum4s( UCcons2, UIcons2 );
  UCaux1.v = UCcons2;
  UIaux2.v = UIcons2;
  for( i=0; i< 4; i++ )
  {
    UIaux = UIaux2.e[i];
    for( j=0; j< 4; j++ )
      UIaux = UIaux + UCaux1.e[4*i+j];
    if (UIaux1.e[i] != UIaux)
        err++;
  }
  if (err)
    printf("Function vec_sum4s [type unsigned char]   ===> Error\n");
  else
    printf("Function vec_sum4s [type unsigned char]   ===> OK\n");

  err = 0;
  Iaux1.v = vec_sum4s( Scons2, Icons2 );
  Saux1.v = Scons2;
  Iaux2.v = Icons2;
  for( i=0; i< 4; i++ )
  {
    Iaux = Iaux2.e[i];
    for( j=0; j< 2; j++ )
      Iaux = Iaux + Saux1.e[2*i+j];
    if (Iaux1.e[i] != Iaux)
        err++;
  }
  if (err)
    printf("Function vec_sum4s [type short]           ===> Error\n");
  else
    printf("Function vec_sum4s [type short]           ===> OK\n");

/*    Function vec_sum2s    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Iaux1.v = Icons1;
  Iaux2.v = Icons3;
  Iaux3.v = vec_sum2s( Iaux1.v, Iaux2.v );
  for( i=0; i< 2; i++ )
  {
    LLaux = (long long int) Iaux1.e[2*i] + Iaux1.e[(2*i)+1] + Iaux2.e[(2*i)+1];
    if (LLaux > INT_MAX)
    {
      Iaux=0x7FFFFFFF;  /* INT_MAX */
    }
    else if (LLaux < INT_MIN)
    {
      Iaux=0x80000000;  /* INT_MIN */
    }
    else Iaux = (signed int) LLaux;
    
    if ((Iaux3.e[2*i] != 0) || (Iaux3.e[(2*i)+1] != Iaux))
      err++;
  }
  if (err)
    printf("Function vec_sum2s [type integer]         ===> Error\n");
  else
    printf("Function vec_sum2s [type integer]         ===> OK\n");
  
/*    Function vec_sums    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;

  /* Not saturated test */
  Iaux1.v = Icons1;
  Iaux2.v = Icons3;
  Iaux3.v = vec_sums( Iaux1.v, Iaux2.v );
  
  LLaux = (long long int) Iaux1.e[0] + Iaux1.e[1] + Iaux1.e[2] + Iaux1.e[3] + Iaux2.e[3];
  if (LLaux > INT_MAX)
  { 
    Iaux=0x7FFFFFFF;  /* INT_MAX */
  }
  else if (LLaux < INT_MIN)
  {
    Iaux=0x80000000;  /* INT_MIN */
  }
  else Iaux = (signed int) LLaux;
  
  if ((Iaux3.e[0] != 0) || (Iaux3.e[1] != 0) || (Iaux3.e[2] != 0) || 
      (Iaux3.e[3] != Iaux))
    err++;
  
  /* Saturated test */
  Iaux1.v = Icons2;
  Iaux2.v = Icons3;
  Iaux3.v = vec_sums( Iaux1.v, Iaux2.v );
  
  LLaux = (long long int) Iaux1.e[0] + Iaux1.e[1] + Iaux1.e[2] + Iaux1.e[3] + Iaux2.e[3];
  if (LLaux > INT_MAX)
  { 
    Iaux=0x7FFFFFFF;  /* INT_MAX */
  }
  else if (LLaux < INT_MIN)
  {
    Iaux=0x80000000;  /* INT_MIN */
  }
  else Iaux = (signed int) LLaux;
  
  if ((Iaux3.e[0] != 0) || (Iaux3.e[1] != 0) || (Iaux3.e[2] != 0) || 
      (Iaux3.e[3] != Iaux))
    err++;
  
  if (err)
    printf("Function vec_sums [type integer]          ===> Error\n");
  else
    printf("Function vec_sums [type integer]          ===> OK\n");
  
#if defined TEST_FLOATS
/*    Function vec_trunc    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Faux1.v = Fcons1;
  Faux2.v = vec_trunc( Faux1.v );
  for( i=0; i< 4; i++ )
  {
    Faux = truncf(Faux1.e[i]);
    if (Faux2.e[i] != Faux)
      err++;
  }
  if (err)
    printf("Function vec_trunc [type float]           ===> Error\n");
  else
    printf("Function vec_trunc [type float]           ===> OK\n");
#endif

/*    Function vec_unpackh    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = Ccons1;
  Saux1.v = vec_unpackh( Caux1.v );
  for ( i=0; i< 8; i++ )
  {
    Saux = (signed short)Caux1.e[i];
    if (Saux1.e[i] != Saux)
      err++;
  }
  
  if (err)
    printf("Function vec_unpackh [type short-char]    ===> Error\n");
  else
    printf("Function vec_unpackh [type short-char]    ===> OK\n");
  
  err = 0;
  Saux1.v = Scons3;
  Iaux1.v = vec_unpackh( Saux1.v );
  for ( i=0; i< 4; i++ )
  {
    Iaux = (signed int)Saux1.e[i];
    if (Iaux1.e[i] != Iaux)
      err++;
  }
  
  if (err)
    printf("Function vec_unpackh [type int-short]     ===> Error\n");
  else
    printf("Function vec_unpackh [type int-short]     ===> OK\n");
  
/*    Function vec_unpackl    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v = Ccons3;
  Saux1.v = vec_unpackl( Caux1.v );
  for ( i=0; i< 8; i++ )
  {
    Saux = (signed short)Caux1.e[i+8];
    if (Saux1.e[i] != Saux)
      err++;
  }
  
  if (err)
    printf("Function vec_unpackl [type short-char]    ===> Error\n");
  else
    printf("Function vec_unpackl [type short-char]    ===> OK\n");
  
  err = 0;
  Saux1.v = Scons1;
  Iaux1.v = vec_unpackl( Saux1.v );
  for ( i=0; i< 4; i++ )
  {
    Iaux = (signed int)Saux1.e[i+4];
    if (Iaux1.e[i] != Iaux)
      err++;
  }
  
  if (err)
    printf("Function vec_unpackl [type int-short]     ===> Error\n");
  else
    printf("Function vec_unpackl [type int-short]     ===> OK\n");

/*    Function vec_xor    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  UCaux1.v = UCcons1;
  UCaux2.v = UCcons3;
  UCaux3.v = vec_xor( UCaux1.v, UCaux2.v );
  for( i=0; i< 16; i++ )
  {
    UCaux = UCaux1.e[i] ^ UCaux2.e[i];
    if (UCaux3.e[i] != UCaux)
      err++;
  }
  if (err)
    printf("Function vec_xor [type unsigned char]     ===> Error\n");
  else
    printf("Function vec_xor [type unsigned char]     ===> OK\n");

  err = 0;
  Caux1.v = Ccons1;
  Caux2.v = Ccons3;
  Caux3.v = vec_xor( Caux1.v, Caux2.v );
  for( i=0; i< 16; i++ )
  {
    Caux = Caux1.e[i] ^ Caux2.e[i];
    if (Caux3.e[i] != Caux)
      err++;
  }
  if (err)
    printf("Function vec_xor [type char]              ===> Error\n");
  else
    printf("Function vec_xor [type char]              ===> OK\n");

  err = 0;
  USaux1.v = UScons1;
  USaux2.v = UScons3;
  USaux3.v = vec_xor( USaux1.v, USaux2.v );
  for( i=0; i< 8; i++ )
  {
    USaux = USaux1.e[i] ^ USaux2.e[i];
    if (USaux3.e[i] != USaux)
      err++;
  }
  if (err)
    printf("Function vec_xor [type unsigned short]    ===> Error\n");
  else
    printf("Function vec_xor [type unsigned short]    ===> OK\n");

  err = 0;
  Saux1.v = Scons1;
  Saux2.v = Scons3;
  Saux3.v = vec_xor( Saux1.v, Saux2.v );
  for( i=0; i< 8; i++ )
  {
    Saux = Saux1.e[i] ^ Saux2.e[i];
    if (Saux3.e[i] != Saux)
      err++;
  }
  if (err)
    printf("Function vec_xor [type short]             ===> Error\n");
  else
    printf("Function vec_xor [type short]             ===> OK\n");

  err = 0;
  UIaux1.v = UIcons1;
  UIaux2.v = UIcons3;
  UIaux3.v = vec_xor( UIaux1.v, UIaux2.v );
  for( i=0; i< 4; i++ )
  {
    UIaux = UIaux1.e[i] ^ UIaux2.e[i];
    if (UIaux3.e[i] != UIaux)
      err++;
  }
  if (err)
    printf("Function vec_xor [type unsigned int]      ===> Error\n");
  else
    printf("Function vec_xor [type unsigned int]      ===> OK\n");

  err = 0;
  Iaux1.v = Icons1;
  Iaux2.v = Icons3;
  Iaux3.v = vec_xor( Iaux1.v, Iaux2.v );
  for( i=0; i< 4; i++ )
  {
    Iaux = Iaux1.e[i] ^ Iaux2.e[i];
    if (Iaux3.e[i] != Iaux)
      err++;
  }
  if (err)
    printf("Function vec_xor [type int]               ===> Error\n");
  else
    printf("Function vec_xor [type int]               ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
  Faux1.v = Fcons1;
  Faux2.v = Fcons3;
  Faux3.v = vec_xor( Faux1.v, Faux2.v );
  for( i=0; i< 4; i++ )
  {
    Iaux = Faux1.i[i] ^ Faux2.i[i];
    
    if (Faux3.i[i] != Iaux)
      err++;
  }
  if (err)
    printf("Function vec_xor [type float]             ===> Error\n");
  else
    printf("Function vec_xor [type float]             ===> OK\n");
#endif

  return 0;
}




int part5()
{
  TvecChar      Caux1,  Caux2;//,  Caux3,  Caux4;
  TvecUChar     UCaux1, UCaux2;//, UCaux3, UCaux4;
  TvecShort     Saux1,  Saux2;//,  Saux3,  Saux4;
  TvecUShort    USaux1, USaux2;//, USaux3, USaux4;
  TvecInt       Iaux1,  Iaux2;//,  Iaux3,  Iaux4;
  TvecUInt      UIaux1, UIaux2;//, UIaux3, UIaux4;
#if defined TEST_FLOATS
  TvecFloat     Faux1,  Faux2;//,  Faux3,  Faux4;
#endif

  int                  i, err, /*j,*/ b, bAux;
//  signed   int         Ivec1, Ivec2, Ivec3;
//  signed   short       *Svec1;
//  unsigned int         *UIvec1;
//  unsigned short       *USvec1;
//  unsigned char        *UCvec1;
#if defined TEST_FLOATS
//  float                *Fvec1;
#endif

  /* For saturated rutines */
//  long long int         LLaux;

#if defined TEST_FLOATS
//  float                 Faux;
#endif
  signed   int          Iaux, I1;//, I2;
//  unsigned int          UIaux, UI1, UI2;
//  signed   short        Saux;
//  unsigned short        USaux;
//  signed   char         Caux;
//  unsigned char         UCaux;

/*
  union
  {
    float          f;
    signed   int   si;
    unsigned int   ui;
    signed   short ss[2];
    unsigned short us[2];
    signed   char  sc[4];
    unsigned char  uc[4];
  } INTunion1, INTunion2;

  union
  {
    signed   short  ss;
    unsigned short  us;
    signed   char   sc[2];
    unsigned char   uc[2];
  } SHOunion1, SHOunion2;
*/


#if defined (GCC_COMPILER)
  vector signed char    Ccons1   = (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
  vector signed char    Ccons2   = (vector signed char){1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1};
  vector signed char    Ccons3   = (vector signed char){-128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127};
  vector unsigned char  UCcons1  = (vector unsigned char){248, 249, 250, 251, 252, 253, 254, 255, 0, 1, 2, 3, 4, 5, 6, 7};
  vector unsigned char  UCcons2  = (vector unsigned char){2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2};
  vector unsigned char  UCcons3  = (vector unsigned char){1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8};
  vector signed short   Scons1   = (vector signed short){-4, -3, -2, -1, 0, 1, 2, 3};
  vector signed short   Scons2   = (vector signed short){-32768, 10000, 1, 1, 1, 1, -10000, -10000};
  vector signed short   Scons3   = (vector signed short){-32768, 32767, -32768, 32767, -32768, 32767, -32768, 32767};
  vector unsigned short UScons1  = (vector unsigned short){65532, 65533, 65534, 65535, 0, 1, 2, 3};
  vector unsigned short UScons2  = (vector unsigned short){1, 1, 1, 1, 1, 1, 1, 1};
  vector unsigned short UScons3  = (vector unsigned short){1, 2, 3, 4, 1, 2, 3, 4};
  vector signed int     Icons1   = (vector signed int){-4, -1, 1, 4};
  vector signed int     Icons2   = (vector signed int){1, 1, 1, 1};
  vector signed int     Icons3   = (vector signed int){0x80000000, 0x7FFFFFFF, 0x80000000, 0x7FFFFFFF};
  vector unsigned int   UIcons1  = (vector unsigned int){0xFFFFFFFE, 0xFFFFFFFF, 0, 1};
  vector unsigned int   UIcons2  = (vector unsigned int){1, 1, 1, 1};
  vector unsigned int   UIcons3  = (vector unsigned int){1, 2, 1, 2};

#if defined TEST_FLOATS
  vector float          Fcons1   = (vector float){-1.5, 1.0, 0.5, -3.999};
  vector float          Fcons2   = (vector float){1.0, 1.0, 1.0, 1.0};
  vector float          Fcons3   = (vector float){100000000000.0, 1.0, -1.0, -1234567890.0};
#endif

#elif defined (MAC_COMPILER) || defined(XLC_COMPILER)
  vector signed char    Ccons1   = (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
  vector signed char    Ccons2   = (vector signed char)(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1);
  vector signed char    Ccons3   = (vector signed char)(-128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127, -128, 127);
  vector unsigned char  UCcons1  = (vector unsigned char)(248, 249, 250, 251, 252, 253, 254, 255, 0, 1, 2, 3, 4, 5, 6, 7);
  vector unsigned char  UCcons2  = (vector unsigned char)(2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2);
  vector unsigned char  UCcons3  = (vector unsigned char)(1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8);
  vector signed short   Scons1   = (vector signed short)(-4, -3, -2, -1, 0, 1, 2, 3);
  vector signed short   Scons2   = (vector signed short)(-32768, 10000, 1, 1, 1, 1, -10000, -10000);
  vector signed short   Scons3   = (vector signed short)(-32768, 32767, -32768, 32767, -32768, 32767, -32768, 32767);
  vector unsigned short UScons1  = (vector unsigned short)(65532, 65533, 65534, 65535, 0, 1, 2, 3);
  vector unsigned short UScons2  = (vector unsigned short)(1, 1, 1, 1, 1, 1, 1, 1);
  vector unsigned short UScons3  = (vector unsigned short)(1, 2, 3, 4, 1, 2, 3, 4);
  vector signed int     Icons1   = (vector signed int)(-4, -1, 1, 4);
  vector signed int     Icons2   = (vector signed int)(1, 1, 1, 1);
  vector signed int     Icons3   = (vector signed int)(0x80000000, 0x7FFFFFFF, 0x80000000, 0x7FFFFFFF);
  vector unsigned int   UIcons1  = (vector unsigned int)(0xFFFFFFFE, 0xFFFFFFFF, 0, 1);
  vector unsigned int   UIcons2  = (vector unsigned int)(1, 1, 1, 1);
  vector unsigned int   UIcons3  = (vector unsigned int)(1, 2, 1, 2);

#if defined TEST_FLOATS
  vector float          Fcons1   = (vector float)(-1.5, 1.0, 0.5, -3.999);
  vector float          Fcons2   = (vector float)(1.0, 1.0, 1.0, 1.0);
  vector float          Fcons3   = (vector float)(100000000000.0, 1.0, -1.0, -1234567890.0);
#endif

#endif


/*    Function vec_all_eq    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  UCaux1.v = UCcons1;
  UCaux2.v = UCcons1;
  I1 = vec_all_eq( UCaux1.v, UCaux2.v );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (UCaux1.e[i]==UCaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  UCaux1.v = UCcons2;
  UCaux2.v = UCcons3;
  I1 = vec_all_eq( UCaux1.v, UCaux2.v );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (UCaux1.e[i]==UCaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_eq [type unsigned char]  ===> Error\n");
  else
    printf("Function vec_all_eq [type unsigned char]  ===> OK\n");
  
  err = 0;
  Caux1.v = Ccons1;
  Caux2.v = Ccons1;
  I1 = vec_all_eq( Caux1.v, Caux2.v );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (Caux1.e[i]==Caux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  Caux1.v = Ccons1;
  Caux2.v = Ccons2;
  I1 = vec_all_eq( Caux1.v, Caux2.v );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (Caux1.e[i]==Caux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_eq [type char]           ===> Error\n");
  else
    printf("Function vec_all_eq [type char]           ===> OK\n");
  
  err = 0;
  USaux1.v = UScons1;
  USaux2.v = UScons1;
  I1 = vec_all_eq( USaux1.v, USaux2.v );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (USaux1.e[i]==USaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  USaux1.v = UScons2;
  USaux2.v = UScons3;
  I1 = vec_all_eq( USaux1.v, USaux2.v );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (USaux1.e[i]==USaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_eq [type unsigned short] ===> Error\n");
  else
    printf("Function vec_all_eq [type unsigned short] ===> OK\n");
  
  err = 0;
  Saux1.v = Scons1;
  Saux2.v = Scons1;
  I1 = vec_all_eq( Saux1.v, Saux2.v );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (Saux1.e[i]==Saux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  Saux1.v = Scons2;
  Saux2.v = Scons3;
  I1 = vec_all_eq( Saux1.v, Saux2.v );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (Saux1.e[i]==Saux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_eq [type short]          ===> Error\n");
  else
    printf("Function vec_all_eq [type short]          ===> OK\n");
  
  err = 0;
  UIaux1.v = UIcons1;
  UIaux2.v = UIcons1;
  I1 = vec_all_eq( UIaux1.v, UIaux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (UIaux1.e[i]==UIaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  UIaux1.v = UIcons2;
  UIaux2.v = UIcons3;
  I1 = vec_all_eq( UIaux1.v, UIaux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (UIaux1.e[i]==UIaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_eq [type unsigned int]   ===> Error\n");
  else
    printf("Function vec_all_eq [type unsigned int]   ===> OK\n");
  
  err = 0;
  Iaux1.v = Icons1;
  Iaux2.v = Icons1;
  I1 = vec_all_eq( Iaux1.v, Iaux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Iaux1.e[i]==Iaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  Iaux1.v = Icons1;
  Iaux2.v = Icons2;
  I1 = vec_all_eq( Iaux1.v, Iaux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Iaux1.e[i]==Iaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_eq [type int]            ===> Error\n");
  else
    printf("Function vec_all_eq [type int]            ===> OK\n");
  
#if defined TEST_FLOATS
  err = 0;
  Faux1.v = Fcons1;
  Faux2.v = Fcons1;
  I1 = vec_all_eq( Faux1.v, Faux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Faux1.e[i]==Faux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  Faux1.v = Fcons1;
  Faux2.v = Fcons2;
  I1 = vec_all_eq( Faux1.v, Faux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Faux1.e[i]==Faux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_eq [type float]          ===> Error\n");
  else
    printf("Function vec_all_eq [type float]          ===> OK\n");
#endif

/*    Function vec_all_ge    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  UCaux1.v = UCcons2;
  UCaux2.v = UCcons2;
  I1 = vec_all_ge( UCaux1.v, UCaux2.v );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (UCaux1.e[i]>=UCaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  UCaux1.v = UCcons2;
  UCaux2.v = UCcons3;
  I1 = vec_all_ge( UCaux1.v, UCaux2.v );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (UCaux1.e[i]>=UCaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_ge [type unsigned char]  ===> Error\n");
  else
    printf("Function vec_all_ge [type unsigned char]  ===> OK\n");
  
  err = 0;
  Caux1.v = Ccons2;
  Caux2.v = Ccons2;
  I1 = vec_all_ge( Caux1.v, Caux2.v );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (Caux1.e[i]>=Caux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  Caux1.v = Ccons2;
  Caux2.v = Ccons3;
  I1 = vec_all_ge( Caux1.v, Caux2.v );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (Caux1.e[i]>=Caux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_ge [type char]           ===> Error\n");
  else
    printf("Function vec_all_ge [type char]           ===> OK\n");
  
  err = 0;
  USaux1.v = UScons3;
  USaux2.v = UScons2;
  I1 = vec_all_ge( USaux1.v, USaux2.v );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (USaux1.e[i]>=USaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  USaux1.v = UScons1;
  USaux2.v = UScons2;
  I1 = vec_all_ge( USaux1.v, USaux2.v );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (USaux1.e[i]>=USaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_ge [type unsigned short] ===> Error\n");
  else
    printf("Function vec_all_ge [type unsigned short] ===> OK\n");
  
  err = 0;
  Saux1.v = Scons1;
  Saux2.v = Scons1;
  I1 = vec_all_ge( Saux1.v, Saux2.v );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (Saux1.e[i]>=Saux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  Saux1.v = Scons2;
  Saux2.v = Scons3;
  I1 = vec_all_ge( Saux1.v, Saux2.v );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (Saux1.e[i]>=Saux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_ge [type short]          ===> Error\n");
  else
    printf("Function vec_all_ge [type short]          ===> OK\n");
  
  err = 0;
  UIaux1.v = UIcons3;
  UIaux2.v = UIcons2;
  I1 = vec_all_ge( UIaux1.v, UIaux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (UIaux1.e[i]>=UIaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  UIaux1.v = UIcons1;
  UIaux2.v = UIcons2;
  I1 = vec_all_ge( UIaux1.v, UIaux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (UIaux1.e[i]>=UIaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_ge [type unsigned int]   ===> Error\n");
  else
    printf("Function vec_all_ge [type unsigned int]   ===> OK\n");
  
  err = 0;
  Iaux1.v = Icons2;
  Iaux2.v = Icons2;
  I1 = vec_all_ge( Iaux1.v, Iaux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Iaux1.e[i]>=Iaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  Iaux1.v = Icons2;
  Iaux2.v = Icons1;
  I1 = vec_all_ge( Iaux1.v, Iaux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Iaux1.e[i]>=Iaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_ge [type int]            ===> Error\n");
  else
    printf("Function vec_all_ge [type int]            ===> OK\n");
  
#if defined TEST_FLOATS
  err = 0;
  Faux1.v = Fcons2;
  Faux2.v = Fcons1;
  I1 = vec_all_ge( Faux1.v, Faux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Faux1.e[i]>=Faux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  Faux1.v = Fcons2;
  Faux2.v = Fcons3;
  I1 = vec_all_ge( Faux1.v, Faux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Faux1.e[i]>=Faux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_ge [type float]          ===> Error\n");
  else
    printf("Function vec_all_ge [type float]          ===> OK\n");
#endif

/*    Function vec_all_gt    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
# if defined (GCC_COMPILER)
   UCaux1.v = (vector unsigned char){248, 249, 250, 251, 252, 253, 254, 255, 2, 3, 4, 5, 6, 7, 8, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux1.v = (vector unsigned char)(248, 249, 250, 251, 252, 253, 254, 255, 2, 3, 4, 5, 6, 7, 8, 9);
# endif
  UCaux2.v = UCcons2;
  I1 = vec_all_gt( UCaux1.v, UCaux2.v );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (UCaux1.e[i]>UCaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  UCaux1.v = UCcons2;
  UCaux2.v = UCcons3;
  I1 = vec_all_gt( UCaux1.v, UCaux2.v );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (UCaux1.e[i]>UCaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_gt [type unsigned char]  ===> Error\n");
  else
    printf("Function vec_all_gt [type unsigned char]  ===> OK\n");
  
  err = 0;
# if defined (GCC_COMPILER)
   Caux1.v = (vector signed char){9, 8, 7, 6, 5, 4, 3, 2, 3, 4, 5, 6, 7, 8, 9, 10};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Caux1.v = (vector signed char)(9, 8, 7, 6, 5, 4, 3, 2, 3, 4, 5, 6, 7, 8, 9, 10);
# endif
  Caux2.v = Ccons2;
  I1 = vec_all_gt( Caux1.v, Caux2.v );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (Caux1.e[i]>Caux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  Caux1.v = Ccons2;
  Caux2.v = Ccons3;
  I1 = vec_all_gt( Caux1.v, Caux2.v );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (Caux1.e[i]>Caux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_gt [type char]           ===> Error\n");
  else
    printf("Function vec_all_gt [type char]           ===> OK\n");
  
  err = 0;
# if defined (GCC_COMPILER)
   USaux1.v = (vector unsigned short){65532, 65533, 65534, 65535, 2, 3, 4, 5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   USaux1.v = (vector unsigned short)(65532, 65533, 65534, 65535, 2, 3, 4, 5);
# endif
  USaux2.v = UScons2;
  I1 = vec_all_gt( USaux1.v, USaux2.v );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (USaux1.e[i]>USaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  USaux1.v = UScons1;
  USaux2.v = UScons2;
  I1 = vec_all_gt( USaux1.v, USaux2.v );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (USaux1.e[i]>USaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_gt [type unsigned short] ===> Error\n");
  else
    printf("Function vec_all_gt [type unsigned short] ===> OK\n");
  
  err = 0;
# if defined (GCC_COMPILER)
   Saux1.v = (vector signed short){4, 3, 2, 1, 2, 3, 4, 5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Saux1.v = (vector signed short)(4, 3, 2, 1, 2, 3, 4, 5);
# endif
  Saux2.v = Scons1;
  I1 = vec_all_gt( Saux1.v, Saux2.v );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (Saux1.e[i]>Saux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  Saux1.v = Scons2;
  Saux2.v = Scons3;
  I1 = vec_all_gt( Saux1.v, Saux2.v );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (Saux1.e[i]>Saux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_gt [type short]          ===> Error\n");
  else
    printf("Function vec_all_gt [type short]          ===> OK\n");
  
  err = 0;
# if defined (GCC_COMPILER)
   UIaux1.v = (vector unsigned int){3, 2, 3, 2};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UIaux1.v = (vector unsigned int)(3, 2, 3, 2);
# endif
  UIaux2.v = UIcons2;
  I1 = vec_all_gt( UIaux1.v, UIaux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (UIaux1.e[i]>UIaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  UIaux1.v = UIcons1;
  UIaux2.v = UIcons2;
  I1 = vec_all_gt( UIaux1.v, UIaux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (UIaux1.e[i]>UIaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_gt [type unsigned int]   ===> Error\n");
  else
    printf("Function vec_all_gt [type unsigned int]   ===> OK\n");
  
  err = 0;
# if defined (GCC_COMPILER)
   Iaux1.v = (vector signed int){4, 10, 10, 4};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Iaux1.v = (vector signed int)(4, 10, 10, 4);
# endif
  Iaux2.v = Icons2;
  I1 = vec_all_gt( Iaux1.v, Iaux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Iaux1.e[i]>Iaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  Iaux1.v = Icons2;
  Iaux2.v = Icons1;
  I1 = vec_all_gt( Iaux1.v, Iaux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Iaux1.e[i]>Iaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_gt [type int]            ===> Error\n");
  else
    printf("Function vec_all_gt [type int]            ===> OK\n");
  
#if defined TEST_FLOATS
  err = 0;
# if defined (GCC_COMPILER)
   Faux1.v = (vector float){100000000000.0, 12.0, 12.0, 1234567890.0};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float)(100000000000.0, 12.0, 12.0, 1234567890.0);
# endif
  Faux2.v = Fcons1;
  I1 = vec_all_gt( Faux1.v, Faux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Faux1.e[i]>Faux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  Faux1.v = Fcons2;
  Faux2.v = Fcons3;
  I1 = vec_all_gt( Faux1.v, Faux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Faux1.e[i]>Faux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_gt [type float]          ===> Error\n");
  else
    printf("Function vec_all_gt [type float]          ===> OK\n");
#endif

#if defined TEST_FLOATS
/*    Function vec_all_in    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Faux1.v = Fcons1;
  Faux2.v = Fcons2;
  I1 = vec_all_in( Faux1.v, Faux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && ((Faux1.e[i]<=Faux2.e[i]) && (Faux1.e[i]>=-Faux2.e[i]));
  }
  if (I1 != Iaux) err++;
  
  Faux1.v = Fcons2;
# if defined (GCC_COMPILER)
   Faux2.v = (vector float){100000000000.0, 1.0, 1.0, 1234567890.0};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux2.v = (vector float)(100000000000.0, 1.0, 1.0, 1234567890.0);
# endif
  I1 = vec_all_in( Faux1.v, Faux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && ((Faux1.e[i]<=Faux2.e[i]) && (Faux1.e[i]>=-Faux2.e[i]));
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_in [type float]          ===> Error\n");
  else
    printf("Function vec_all_in [type float]          ===> OK\n");
#endif

/*    Function vec_all_le    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  UCaux1.v = UCcons2;
  UCaux2.v = UCcons3;
  I1 = vec_all_le( UCaux1.v, UCaux2.v );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (UCaux1.e[i]<=UCaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  UCaux1.v = UCcons1;
  UCaux2.v = UCcons2;
  I1 = vec_all_le( UCaux1.v, UCaux2.v );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (UCaux1.e[i]<=UCaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_le [type unsigned char]  ===> Error\n");
  else
    printf("Function vec_all_le [type unsigned char]  ===> OK\n");
  
  err = 0;
  Caux1.v = Ccons2;
  Caux2.v = Ccons2;
  I1 = vec_all_le( Caux1.v, Caux2.v );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (Caux1.e[i]<=Caux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  Caux1.v = Ccons2;
  Caux2.v = Ccons3;
  I1 = vec_all_le( Caux1.v, Caux2.v );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (Caux1.e[i]<=Caux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_le [type char]           ===> Error\n");
  else
    printf("Function vec_all_le [type char]           ===> OK\n");
  
  err = 0;
  USaux1.v = UScons2;
  USaux2.v = UScons3;
  I1 = vec_all_le( USaux1.v, USaux2.v );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (USaux1.e[i]<=USaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  USaux1.v = UScons1;
  USaux2.v = UScons2;
  I1 = vec_all_le( USaux1.v, USaux2.v );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (USaux1.e[i]<=USaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_le [type unsigned short] ===> Error\n");
  else
    printf("Function vec_all_le [type unsigned short] ===> OK\n");
  
  err = 0;
  Saux1.v = Scons1;
  Saux2.v = Scons1;
  I1 = vec_all_le( Saux1.v, Saux2.v );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (Saux1.e[i]<=Saux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  Saux1.v = Scons2;
  Saux2.v = Scons3;
  I1 = vec_all_le( Saux1.v, Saux2.v );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (Saux1.e[i]<=Saux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_le [type short]          ===> Error\n");
  else
    printf("Function vec_all_le [type short]          ===> OK\n");
  
  err = 0;
  UIaux1.v = UIcons2;
  UIaux2.v = UIcons3;
  I1 = vec_all_le( UIaux1.v, UIaux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (UIaux1.e[i]<=UIaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  UIaux1.v = UIcons1;
  UIaux2.v = UIcons2;
  I1 = vec_all_le( UIaux1.v, UIaux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (UIaux1.e[i]<=UIaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_le [type unsigned int]   ===> Error\n");
  else
    printf("Function vec_all_le [type unsigned int]   ===> OK\n");
  
  err = 0;
  Iaux1.v = Icons2;
  Iaux2.v = Icons2;
  I1 = vec_all_le( Iaux1.v, Iaux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Iaux1.e[i]<=Iaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  Iaux1.v = Icons1;
  Iaux2.v = Icons2;
  I1 = vec_all_le( Iaux1.v, Iaux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Iaux1.e[i]<=Iaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_le [type int]            ===> Error\n");
  else
    printf("Function vec_all_le [type int]            ===> OK\n");
  
#if defined TEST_FLOATS
  err = 0;
  Faux1.v = Fcons1;
  Faux2.v = Fcons2;
  I1 = vec_all_le( Faux1.v, Faux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Faux1.e[i]<=Faux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  Faux1.v = Fcons2;
  Faux2.v = Fcons3;
  I1 = vec_all_le( Faux1.v, Faux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Faux1.e[i]<=Faux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_le [type float]          ===> Error\n");
  else
    printf("Function vec_all_le [type float]          ===> OK\n");
#endif

/*    Function vec_all_lt    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  UCaux1.v = UCcons2;
# if defined (GCC_COMPILER)
   UCaux2.v = (vector unsigned char){248, 249, 250, 251, 252, 253, 254, 255, 2, 3, 4, 5, 6, 7, 8, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux2.v = (vector unsigned char)(248, 249, 250, 251, 252, 253, 254, 255, 2, 3, 4, 5, 6, 7, 8, 9);
# endif
  I1 = vec_all_lt( UCaux1.v, UCaux2.v );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (UCaux1.e[i]<UCaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  UCaux1.v = UCcons3;
  UCaux2.v = UCcons2;
  I1 = vec_all_lt( UCaux1.v, UCaux2.v );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (UCaux1.e[i]<UCaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_lt [type unsigned char]  ===> Error\n");
  else
    printf("Function vec_all_lt [type unsigned char]  ===> OK\n");
  
  err = 0;
  Caux1.v = Ccons2;
# if defined (GCC_COMPILER)
   Caux2.v = (vector signed char){9, 8, 7, 6, 5, 4, 3, 2, 3, 4, 5, 6, 7, 8, 9, 10};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Caux2.v = (vector signed char)(9, 8, 7, 6, 5, 4, 3, 2, 3, 4, 5, 6, 7, 8, 9, 10);
# endif
  I1 = vec_all_lt( Caux1.v, Caux2.v );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (Caux1.e[i]<Caux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  Caux1.v = Ccons3;
  Caux2.v = Ccons2;
  I1 = vec_all_lt( Caux1.v, Caux2.v );
  Iaux = 1;
  for ( i=0; i< 16; i++ )
  {
    Iaux = Iaux && (Caux1.e[i]<Caux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_lt [type char]           ===> Error\n");
  else
    printf("Function vec_all_lt [type char]           ===> OK\n");
  
  err = 0;
  USaux1.v = UScons2;
# if defined (GCC_COMPILER)
   USaux2.v = (vector unsigned short){65532, 65533, 65534, 65535, 2, 3, 4, 5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   USaux2.v = (vector unsigned short)(65532, 65533, 65534, 65535, 2, 3, 4, 5);
# endif
  I1 = vec_all_lt( USaux1.v, USaux2.v );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (USaux1.e[i]<USaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  USaux1.v = UScons2;
  USaux2.v = UScons1;
  I1 = vec_all_lt( USaux1.v, USaux2.v );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (USaux1.e[i]<USaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_lt [type unsigned short] ===> Error\n");
  else
    printf("Function vec_all_lt [type unsigned short] ===> OK\n");
  
  err = 0;
  Saux1.v = Scons1;
# if defined (GCC_COMPILER)
   Saux2.v = (vector signed short){4, 3, 2, 1, 2, 3, 4, 5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Saux2.v = (vector signed short)(4, 3, 2, 1, 2, 3, 4, 5);
# endif
  I1 = vec_all_lt( Saux1.v, Saux2.v );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (Saux1.e[i]<Saux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  Saux1.v = Scons3;
  Saux2.v = Scons2;
  I1 = vec_all_lt( Saux1.v, Saux2.v );
  Iaux = 1;
  for ( i=0; i< 8; i++ )
  {
    Iaux = Iaux && (Saux1.e[i]<Saux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_lt [type short]          ===> Error\n");
  else
    printf("Function vec_all_lt [type short]          ===> OK\n");
  
  err = 0;
  UIaux1.v = UIcons2;
# if defined (GCC_COMPILER)
   UIaux2.v = (vector unsigned int){3, 2, 3, 2};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UIaux2.v = (vector unsigned int)(3, 2, 3, 2);
# endif
  I1 = vec_all_lt( UIaux1.v, UIaux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (UIaux1.e[i]<UIaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  UIaux1.v = UIcons2;
  UIaux2.v = UIcons1;
  I1 = vec_all_lt( UIaux1.v, UIaux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (UIaux1.e[i]<UIaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_lt [type unsigned int]   ===> Error\n");
  else
    printf("Function vec_all_lt [type unsigned int]   ===> OK\n");
  
  err = 0;
  Iaux1.v = Icons2;
# if defined (GCC_COMPILER)
   Iaux2.v = (vector signed int){4, 10, 10, 4};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Iaux2.v = (vector signed int)(4, 10, 10, 4);
# endif
  I1 = vec_all_lt( Iaux1.v, Iaux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Iaux1.e[i]<Iaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  Iaux1.v = Icons1;
  Iaux2.v = Icons2;
  I1 = vec_all_lt( Iaux1.v, Iaux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Iaux1.e[i]<Iaux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_lt [type int]            ===> Error\n");
  else
    printf("Function vec_all_lt [type int]            ===> OK\n");
  
#if defined TEST_FLOATS
  err = 0;
  Faux1.v = Fcons1;
# if defined (GCC_COMPILER)
   Faux2.v = (vector float){100000000000.0, 12.0, 12.0, 1234567890.0};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux2.v = (vector float)(100000000000.0, 12.0, 12.0, 1234567890.0);
# endif
  I1 = vec_all_lt( Faux1.v, Faux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Faux1.e[i]<Faux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  Faux1.v = Fcons3;
  Faux2.v = Fcons2;
  I1 = vec_all_lt( Faux1.v, Faux2.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (Faux1.e[i]<Faux2.e[i]);
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_lt [type float]          ===> Error\n");
  else
    printf("Function vec_all_lt [type float]          ===> OK\n");
#endif

#if defined TEST_FLOATS
/*    Function vec_all_nan    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
# if defined (GCC_COMPILER)
   Faux1.v = (vector float){NAN, NAN, NAN, NAN};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float)(NAN, NAN, NAN, NAN);
# endif
  I1 = vec_all_nan( Faux1.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (isnan(Faux1.e[i]));
  }
  if (I1 != Iaux) err++;
  
  Faux1.v = Fcons1;
  I1 = vec_all_nan( Faux1.v );
  Iaux = 1;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux && (isnan(Faux1.e[i]));
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_all_nan [type float]         ===> Error\n");
  else
    printf("Function vec_all_nan [type float]         ===> OK\n");
#endif

/*    Function vec_all_ne   */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
# if defined (GCC_COMPILER)
   Caux1.v = (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6,  7};
   Caux2.v = (vector signed char){-7, -6, -5, -4, -3, -2, -1,  0, 1, 2, 3, 4, 5, 6, 7, -8};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Caux1.v = (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6,  7);
   Caux2.v = (vector signed char)(-7, -6, -5, -4, -3, -2, -1,  0, 1, 2, 3, 4, 5, 6, 7, -8);
# endif
  b = vec_all_ne (Caux1.v, Caux2.v);
  bAux = 1;
  for (i=0; i<16; i++)
    bAux = bAux && (Caux1.e[i]!=Caux2.e[i]);
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   Caux1.v = (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6,  7};
   Caux2.v = (vector signed char){-7, -6, -5, -4, -3, -2, -1,  0, 1, 2, 3, 4, 4, 6, 7, -8};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Caux1.v = (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6,  7);
   Caux2.v = (vector signed char)(-7, -6, -5, -4, -3, -2, -1,  0, 1, 2, 3, 4, 4, 6, 7, -8);
# endif
  b = vec_all_ne (Caux1.v, Caux2.v);
  bAux= 1;
  for (i=0; i<16; i++)
    bAux= bAux && (Caux1.e[i]!=Caux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Caux1.v = (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6,  7};
   Caux2.v = (vector signed char){-7, -6, -5, -4, -3, -2, -1,  0, 1, 2, 3, 4, 4, 6, 7, -8};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Caux1.v = (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6,  7);
   Caux2.v = (vector signed char)(-7, -6, -5, -4, -3, -2, -1,  0, 1, 2, 3, 4, 4, 6, 7, -8);
# endif
  b = vec_all_ne (Caux1.v, Caux2.v);
  bAux = 1;
  for (i=0; i<16; i++)
    bAux = bAux && (Caux1.e[i] != Caux2.e[i]);
  if (bAux != b) err = 1;

  if (err)
    printf("Function vec_all_ne [type char]           ===> Error\n");
  else
    printf("Function vec_all_ne [type char]           ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   UCaux1.v = (vector unsigned char){200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15, 16, 17};
   UCaux2.v = (vector unsigned char){201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17,200};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux1.v = (vector unsigned char)(200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15, 16, 17);
   UCaux2.v = (vector unsigned char)(201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17,200);
# endif
  
  b = vec_all_ne (UCaux1.v, UCaux2.v);
  bAux= 1;
  for (i=0; i<16; i++)
    bAux= bAux && (UCaux1.e[i]!=UCaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   UCaux1.v = (vector unsigned char){200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15, 16, 17};
   UCaux2.v = (vector unsigned char){201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17,200};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux1.v = (vector unsigned char)(200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15, 16, 17);
   UCaux2.v = (vector unsigned char)(201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17,200);
# endif
  b = vec_all_ne (UCaux1.v, UCaux2.v);
  bAux = 1;
  for (i=0; i<16; i++)
    bAux = bAux && (UCaux1.e[i] != UCaux2.e[i]);
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   UCaux1.v = (vector unsigned char){200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15, 16, 17};
   UCaux2.v = (vector unsigned char){201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17,200};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux1.v = (vector unsigned char)(200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15, 16, 17);
   UCaux2.v = (vector unsigned char)(201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17,200);
# endif
  b = vec_all_ne (UCaux1.v, UCaux2.v);
  bAux = 1;
  for (i=0; i<16; i++)
    bAux = bAux && (UCaux1.e[i] != UCaux2.e[i]);
  if (bAux != b) err = 1;

  if (err)
    printf("Function vec_all_ne [type unsigned char]  ===> Error\n");
  else
    printf("Function vec_all_ne [type unsigned char]  ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   Saux1.v = (vector signed short){-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100};
   Saux2.v = (vector signed short){-3700, -3600, -3500,     0, 3300, 3200, 3100,-3800};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Saux1.v = (vector signed short)(-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100);
   Saux2.v = (vector signed short)(-3700, -3600, -3500,     0, 3300, 3200, 3100,-3800);
# endif
  b = vec_all_ne (Saux1.v, Saux2.v);
  bAux = 1;
  for (i=0; i<8; i++)
    bAux = bAux && (Saux1.e[i] != Saux2.e[i]);
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   Saux1.v = (vector signed short){-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100};
   Saux2.v = (vector signed short){-3700, -3600, -3500,     0, 3300, 3200, 3100,-3800};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Saux1.v = (vector signed short)(-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100);
   Saux2.v = (vector signed short)(-3700, -3600, -3500,     0, 3300, 3200, 3100,-3800);
# endif
  b = vec_all_ne (Saux1.v, Saux2.v);
  bAux = 1;
  for (i=0; i<8; i++)
    bAux = bAux && (Saux1.e[i] != Saux2.e[i]);
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   Saux1.v = (vector signed short){-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100};
   Saux2.v = (vector signed short){-3700, -3600, -3500,     0, 3300, 3200, 3100,-3800};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Saux1.v = (vector signed short)(-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100);
   Saux2.v = (vector signed short)(-3700, -3600, -3500,     0, 3300, 3200, 3100,-3800);
# endif
  b = vec_all_ne (Saux1.v, Saux2.v);
  bAux = 1;
  for (i=0; i<8; i++)
    bAux = bAux && (Saux1.e[i] != Saux2.e[i]);
  if (bAux != b) err = 1;

  if (err)
    printf("Function vec_all_ne [type short]          ===> Error\n");
  else
    printf("Function vec_all_ne [type short]          ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   USaux1.v = (vector unsigned short){48000, 47000, 46000, 45000,    0, 3300, 3200, 3100};
   USaux2.v = (vector unsigned short){47000, 46000, 45000,     0, 3300, 3200, 3100,48000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   USaux1.v = (vector unsigned short)(48000, 47000, 46000, 45000,    0, 3300, 3200, 3100);
   USaux2.v = (vector unsigned short)(47000, 46000, 45000,     0, 3300, 3200, 3100,48000);
# endif
  b = vec_all_ne (USaux1.v, USaux2.v);
  bAux = 1;
  for (i=0; i<8; i++)
    bAux = bAux && (USaux1.e[i] != USaux2.e[i]);
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   USaux1.v = (vector unsigned short){48000, 47000, 46000, 45000,    0, 3300, 3200, 3100};
   USaux2.v = (vector unsigned short){47000, 46000, 45000,     0, 3300, 3200, 3100,48000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   USaux1.v = (vector unsigned short)(48000, 47000, 46000, 45000,    0, 3300, 3200, 3100);
   USaux2.v = (vector unsigned short)(47000, 46000, 45000,     0, 3300, 3200, 3100,48000);
# endif
  b = vec_all_ne (USaux1.v, USaux2.v);
  bAux = 1;
  for (i=0; i<8; i++)
    bAux = bAux && (USaux1.e[i] != USaux2.e[i]);
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   USaux1.v = (vector unsigned short){48000, 47000, 46000, 45000,    0, 3300, 3200, 3100};
   USaux2.v = (vector unsigned short){47000, 46000, 45000,     0, 3300, 3200, 3100,48000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   USaux1.v = (vector unsigned short)(48000, 47000, 46000, 45000,    0, 3300, 3200, 3100);
   USaux2.v = (vector unsigned short)(47000, 46000, 45000,     0, 3300, 3200, 3100,48000);
# endif
  b = vec_all_ne (USaux1.v, USaux2.v);
  bAux = 1;
  for (i=0; i<8; i++)
    bAux = bAux && (USaux1.e[i] != USaux2.e[i]);
  if (bAux != b) err = 1;

  if (err)
    printf("Function vec_all_ne [type unsigned short] ===> Error\n");
  else
    printf("Function vec_all_ne [type unsigned short] ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   Iaux1.v = (vector signed int){-1003800, -1003700,       0, 1003300};
   Iaux2.v = (vector signed int){-1003700,        0, 1003300,-1003800};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Iaux1.v = (vector signed int)(-1003800, -1003700,       0, 1003300);
   Iaux2.v = (vector signed int)(-1003700,        0, 1003300,-1003800);
# endif
  b = vec_all_ne (Iaux1.v, Iaux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && (Iaux1.e[i] != Iaux2.e[i]);
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   Iaux1.v = (vector signed int){-1003800, -1003700,       0, 1003300};
   Iaux2.v = (vector signed int){-1003700,        0, 1003300,-1003800};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Iaux1.v = (vector signed int)(-1003800, -1003700,       0, 1003300);
   Iaux2.v = (vector signed int)(-1003700,        0, 1003300,-1003800);
# endif
  b = vec_all_ne (Iaux1.v, Iaux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && (Iaux1.e[i] != Iaux2.e[i]);
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   Iaux1.v= (vector signed int){-1003800, -1003700,       0, 1003300};
   Iaux2.v= (vector signed int){-1003700,        0, 1003300,-1003800};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Iaux1.v= (vector signed int)(-1003800, -1003700,       0, 1003300);
   Iaux2.v= (vector signed int)(-1003700,        0, 1003300,-1003800);
# endif
  b = vec_all_ne (Iaux1.v, Iaux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && (Iaux1.e[i] != Iaux2.e[i]);
  if (bAux != b) err = 1;
  
  if (err)
    printf("Function vec_all_ne [type int]            ===> Error\n");
  else
    printf("Function vec_all_ne [type int]            ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   UIaux1.v = (vector unsigned int){0xFFFFF000, 12345678, 0,         1};
   UIaux2.v = (vector unsigned int){  12345678,        0, 1,0xFFFFF000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UIaux1.v = (vector unsigned int)(0xFFFFF000, 12345678, 0,         1);
   UIaux2.v = (vector unsigned int)(  12345678,        0, 1,0xFFFFF000);
# endif
  b = vec_all_ne (UIaux1.v, UIaux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && (UIaux1.e[i] != UIaux2.e[i]);
  if (bAux != b) err = 1;
    
# if defined (GCC_COMPILER)
   UIaux1.v = (vector unsigned int){0xFFFFF000, 12345678, 0,         1};
   UIaux2.v = (vector unsigned int){  12345678,        0, 1,0xFFFFF000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UIaux1.v = (vector unsigned int)(0xFFFFF000, 12345678, 0,         1);
   UIaux2.v = (vector unsigned int)(  12345678,        0, 1,0xFFFFF000);
# endif
  b = vec_all_ne (UIaux1.v, UIaux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && (UIaux1.e[i] != UIaux2.e[i]);
  if (bAux != b) err = 1;
    
# if defined (GCC_COMPILER)
   UIaux1.v = (vector unsigned int){0xFFFFF000, 12345678, 0,         1};
   UIaux2.v = (vector unsigned int){  12345678,        0, 1,0xFFFFF000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UIaux1.v = (vector unsigned int)(0xFFFFF000, 12345678, 0,         1);
   UIaux2.v = (vector unsigned int)(  12345678,        0, 1,0xFFFFF000);
# endif
  b = vec_all_ne (UIaux1.v, UIaux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && (UIaux1.e[i] != UIaux2.e[i]);
  if (bAux != b) err = 1;
    
  if (err)
    printf("Function vec_all_ne [type unsigned int]   ===> Error\n");
  else
    printf("Function vec_all_ne [type unsigned int]   ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
# if defined (GCC_COMPILER)
   Faux1.v = (vector float) {-1.5, 1.0,    0.5, -3.999};
   Faux2.v = (vector float) { 1.0, 0.5, -3.999, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) (-1.5, 1.0,    0.5, -3.999);
   Faux2.v = (vector float) ( 1.0, 0.5, -3.999, -1.5);
# endif
  b = vec_all_ne (Faux1.v, Faux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && (Faux1.e[i] != Faux2.e[i]);
  if (bAux != b) err = 1;
    
# if defined (GCC_COMPILER)
   Faux1.v = (vector float) {-1.5, 1.0,    0.5, -3.999};
   Faux2.v = (vector float) { 1.0, 0.5, -3.999, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) (-1.5, 1.0,    0.5, -3.999);
   Faux2.v = (vector float) ( 1.0, 0.5, -3.999, -1.5);
# endif
  b = vec_all_ne (Faux1.v, Faux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && (Faux1.e[i] != Faux2.e[i]);
  if (bAux != b) err = 1;
    
# if defined (GCC_COMPILER)
   Faux1.v = (vector float) {-1.5, 1.0,    0.5, -3.999};
   Faux2.v = (vector float) { 1.0, 0.5, -3.999, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) (-1.5, 1.0,    0.5, -3.999);
   Faux2.v = (vector float) ( 1.0, 0.5, -3.999, -1.5);
# endif
  b = vec_all_ne (Faux1.v, Faux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && (Faux1.e[i] != Faux2.e[i]);
  if (bAux != b) err = 1;
    
  if (err)
    printf("Function vec_all_ne [type float]          ===> Error\n");
  else
    printf("Function vec_all_ne [type float]          ===> OK\n");
#endif

#if defined TEST_FLOATS
/*    Function vec_all_nge    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
# if defined (GCC_COMPILER)
   Faux1.v = (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux2.v = (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux2.v = (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif
  b = vec_all_nge (Faux1.v, Faux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || 
         (Faux1.e[i] < Faux2.e[i]));
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   Faux1.v = (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux2.v = (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux2.v = (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif
  b = vec_all_nge (Faux1.v, Faux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || 
         (Faux1.e[i] < Faux2.e[i]));
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   Faux1.v = (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux2.v = (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux2.v = (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif
  b = vec_all_nge (Faux1.v, Faux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || 
         (Faux1.e[i] < Faux2.e[i]));
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   Faux1.v = (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux2.v = (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux2.v = (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif 
  b = vec_all_nge (Faux1.v, Faux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || 
         (Faux1.e[i] < Faux2.e[i]));
  if (bAux != b) err = 1;

  if (err)
    printf("Function vec_all_nge [type float]         ===> Error\n");
  else
    printf("Function vec_all_nge [type float]         ===> OK\n");
#endif

#if defined TEST_FLOATS
/*    Function vec_all_ngt    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
# if defined (GCC_COMPILER)
   Faux1.v = (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux2.v = (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux2.v = (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif
  b = vec_all_ngt (Faux1.v, Faux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && 
         (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || !(Faux1.e[i] > Faux2.e[i]));
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   Faux1.v = (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux2.v = (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux2.v = (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif
  b = vec_all_ngt (Faux1.v, Faux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && 
         (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || !(Faux1.e[i] > Faux2.e[i]));
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   Faux1.v = (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux2.v = (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux2.v = (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif
  b = vec_all_ngt (Faux1.v, Faux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && 
         (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || !(Faux1.e[i] > Faux2.e[i]));
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v = (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux2.v = (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux2.v = (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif
  b = vec_all_ngt (Faux1.v, Faux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && 
         (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || !(Faux1.e[i] > Faux2.e[i]));
  if (bAux != b) err = 1;

  if (err)
    printf("Function vec_all_ngt [type float]         ===> Error\n");
  else
    printf("Function vec_all_ngt [type float]         ===> OK\n");
#endif

#if defined TEST_FLOATS
/*    Function vec_all_nle    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
# if defined (GCC_COMPILER)
   Faux1.v = (vector float) { 0.0, 3.5, 0.55, -1.5};
   Faux2.v = (vector float) {-1.5, 1.0, 0.5, -3.999};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) ( 0.0, 3.5, 0.55, -1.5);
   Faux2.v = (vector float) (-1.5, 1.0, 0.5, -3.999);
# endif
  b = vec_all_nle (Faux1.v, Faux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && 
         (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || !(Faux1.e[i] <= Faux2.e[i]));
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   Faux1.v = (vector float) { 0.0, 3.5, 0.55, -1.5};
   Faux2.v = (vector float) {-1.5, 1.0, 0.5, -3.999};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) ( 0.0, 3.5, 0.55, -1.5);
   Faux2.v = (vector float) (-1.5, 1.0, 0.5, -3.999);
# endif
  b = vec_all_nle (Faux1.v, Faux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && 
         (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || !(Faux1.e[i] <= Faux2.e[i]));
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   Faux1.v = (vector float) { 0.0, 3.5, 0.55, -1.5};
   Faux2.v = (vector float) {-1.5, 1.0, 0.5, -3.999};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) ( 0.0, 3.5, 0.55, -1.5);
   Faux2.v = (vector float) (-1.5, 1.0, 0.5, -3.999);
# endif
  b = vec_all_nle (Faux1.v, Faux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && 
         (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || !(Faux1.e[i] <=Faux2.e[i]));
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   Faux1.v = (vector float) { 0.0, 3.5, 0.55, -1.5};
   Faux2.v = (vector float) {-1.5, 1.0, NAN, -3.999};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) ( 0.0, 3.5, 0.55, -1.5);
   Faux2.v = (vector float) (-1.5, 1.0, NAN, -3.999);
# endif
  b = vec_all_nle (Faux1.v, Faux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && 
         (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || !(Faux1.e[i] <= Faux2.e[i]));
  if (bAux != b) err = 1;

  if (err)
    printf("Function vec_all_nle [type float]         ===> Error\n");
  else
    printf("Function vec_all_nle [type float]         ===> OK\n");
#endif


#if defined TEST_FLOATS
/*    Function vec_all_nlt    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
# if defined (GCC_COMPILER)
   Faux1.v = (vector float) { 0.0, 3.5, 0.55, -1.5};
   Faux2.v = (vector float) {-1.5, 1.0, 0.5, -3.999};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) ( 0.0, 3.5, 0.55, -1.5);
   Faux2.v = (vector float) (-1.5, 1.0, 0.5, -3.999);
# endif
  b = vec_all_nlt (Faux1.v, Faux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && 
         (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || !(Faux1.e[i] < Faux2.e[i]));
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   Faux1.v = (vector float) { 0.0, 3.5, 0.55, -1.5};
   Faux2.v = (vector float) {-1.5, 5.0, 0.5, -3.999};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) ( 0.0, 3.5, 0.55, -1.5);
   Faux2.v = (vector float) (-1.5, 5.0, 0.5, -3.999);
# endif
  b = vec_all_nlt (Faux1.v, Faux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && 
         (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || !(Faux1.e[i] < Faux2.e[i]));
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   Faux1.v = (vector float) { 0.0, 3.5, 0.55, -1.5};
   Faux2.v = (vector float) {-1.5, 1.0, 0.55, -3.999};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) ( 0.0, 3.5, 0.55, -1.5);
   Faux2.v = (vector float) (-1.5, 1.0, 0.55, -3.999);
# endif
  b = vec_all_nlt (Faux1.v, Faux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && 
         (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || !(Faux1.e[i] < Faux2.e[i]));
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   Faux1.v = (vector float) { 0.0, 3.5, 0.55, -1.5};
   Faux2.v = (vector float) {-1.5, 1.0, NAN, -3.999};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) ( 0.0, 3.5, 0.55, -1.5);
   Faux2.v = (vector float) (-1.5, 1.0, NAN, -3.999);
# endif
  b = vec_all_nlt (Faux1.v, Faux2.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && 
         (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || !(Faux1.e[i] < Faux2.e[i]));
  if (bAux != b) err = 1;

  if (err)
    printf("Function vec_all_nlt [type float]         ===> Error\n");
  else
    printf("Function vec_all_nlt [type float]         ===> OK\n");
#endif


#if defined TEST_FLOATS
/*    Function vec_all_numeric    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
# if defined (GCC_COMPILER)
   Faux1.v = (vector float) {0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) (0.0, 3.5, 0.55, -1.5);
# endif
  b = vec_all_numeric (Faux1.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && !isnan(Faux1.e[i]);
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   Faux1.v = (vector float) {0.0, 3.5, 0.5, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) (0.0, 3.5, 0.5, -1.5);
# endif
  b = vec_all_numeric (Faux1.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && !isnan(Faux1.e[i]);
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   Faux1.v = (vector float) {0.0, 3.5, NAN, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) (0.0, 3.5, NAN, -1.5);
# endif
  b = vec_all_numeric (Faux1.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && !isnan(Faux1.e[i]);
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   Faux1.v = (vector float) {NAN, NAN, NAN, NAN};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) (NAN, NAN, NAN, NAN);
# endif
  b = vec_all_numeric (Faux1.v);
  bAux = 1;
  for (i=0; i<4; i++)
    bAux = bAux && !isnan(Faux1.e[i]);
  if (bAux != b) err = 1;
  
  if (err)
    printf("Function vec_all_numeric [type float]     ===> Error\n");
  else
    printf("Function vec_all_numeric [type float]     ===> OK\n");
#endif

/*    Function vec_any_eq    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Caux1.v= Ccons1;
  Caux2.v= Ccons3;
  b= vec_any_eq (Caux1.v, Caux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (Caux1.e[i]==Caux2.e[i]);
  if (bAux!=b) err= 1;

  Caux1.v= Ccons1;
  Caux2.v= Ccons2;
  b= vec_any_eq (Caux1.v, Caux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (Caux1.e[i]==Caux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_eq [type char]           ===> Error\n");
  else
    printf("Function vec_any_eq [type char]           ===> OK\n");


  err = 0;
  UCaux1.v= UCcons1;
  UCaux2.v= UCcons3;
  b= vec_any_eq (UCaux1.v, UCaux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (UCaux1.e[i]==UCaux2.e[i]);
  if (bAux!=b) err= 1;

  UCaux1.v= UCcons1;
  UCaux2.v= UCcons2;
  b= vec_any_eq (UCaux1.v, UCaux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (UCaux1.e[i]==UCaux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_eq [type unsigned char]  ===> Error\n");
  else
    printf("Function vec_any_eq [type unsigned char]  ===> OK\n");


  err = 0;
  Saux1.v= Scons1;
  Saux2.v= Scons3;
  b= vec_any_eq (Saux1.v, Saux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (Saux1.e[i]==Saux2.e[i]);
  if (bAux!=b) err= 1;

  Saux1.v= Scons1;
  Saux2.v= Scons2;
  b= vec_any_eq (Saux1.v, Saux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (Saux1.e[i]==Saux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_eq [type short]          ===> Error\n");
  else
    printf("Function vec_any_eq [type short]          ===> OK\n");


  err = 0;
  USaux1.v= UScons1;
  USaux2.v= UScons3;
  b= vec_any_eq (USaux1.v, USaux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (USaux1.e[i]==USaux2.e[i]);
  if (bAux!=b) err= 1;

  USaux1.v= UScons1;
  USaux2.v= UScons2;
  b= vec_any_eq (USaux1.v, USaux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (USaux1.e[i]==USaux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_eq [type unsigned short] ===> Error\n");
  else
    printf("Function vec_any_eq [type unsigned short] ===> OK\n");


  err = 0;
  Iaux1.v= Icons1;
  Iaux2.v= Icons3;
  b= vec_any_eq (Iaux1.v, Iaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Iaux1.e[i]==Iaux2.e[i]);
  if (bAux!=b) err= 1;

  Iaux1.v= Icons1;
  Iaux2.v= Icons2;
  b= vec_any_eq (Iaux1.v, Iaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Iaux1.e[i]==Iaux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_eq [type int]            ===> Error\n");
  else
    printf("Function vec_any_eq [type int]            ===> OK\n");


  err = 0;
  UIaux1.v= UIcons1;
  UIaux2.v= UIcons3;
  b= vec_any_eq (UIaux1.v, UIaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (UIaux1.e[i]==UIaux2.e[i]);
  if (bAux!=b) err= 1;

  UIaux1.v= UIcons1;
  UIaux2.v= UIcons2;
  b= vec_any_eq (UIaux1.v, UIaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (UIaux1.e[i]==UIaux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_eq [type unsigned int]   ===> Error\n");
  else
    printf("Function vec_any_eq [type unsigned int]   ===> OK\n");


#if defined TEST_FLOATS
  err = 0;
# if defined (GCC_COMPILER)
   Faux1.v = (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux2.v = (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux2.v = (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif
  b = vec_any_eq (Faux1.v, Faux2.v);
  bAux = 0;
  for (i=0; i<4; i++)
    bAux = bAux || (Faux1.e[i] == Faux2.e[i]);
  if (bAux != b) err = 1;

# if defined (GCC_COMPILER)
   Faux1.v = (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux2.v = (vector float) { 0.0, 3.5, 0.5, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux2.v = (vector float) ( 0.0, 3.5, 0.5, -1.5);
# endif
  b= vec_any_eq (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Faux1.e[i]==Faux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_eq [type float]          ===> Error\n");
  else
    printf("Function vec_any_eq [type float]          ===> OK\n");
#endif

/*    Function vec_any_ge    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
# if defined (GCC_COMPILER)
   Caux1.v= (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
   Caux2.v= (vector signed char){ 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Caux1.v= (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
   Caux2.v= (vector signed char)( 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9);
# endif
  b= vec_any_ge (Caux1.v, Caux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (Caux1.e[i]>=Caux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Caux1.v= (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
   Caux2.v= (vector signed char){ 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Caux1.v= (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
   Caux2.v= (vector signed char)( 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9);
# endif
  b= vec_any_ge (Caux1.v, Caux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (Caux1.e[i]>=Caux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Caux1.v= (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
   Caux2.v= (vector signed char){ 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Caux1.v= (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
   Caux2.v= (vector signed char)( 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9);
# endif
  b= vec_any_ge (Caux1.v, Caux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (Caux1.e[i]>=Caux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_ge [type char]           ===> Error\n");
  else
    printf("Function vec_any_ge [type char]           ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   UCaux1.v= (vector unsigned char){200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17};
   UCaux2.v= (vector unsigned char){250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux1.v= (vector unsigned char)(200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17);
   UCaux2.v= (vector unsigned char)(250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250);
# endif
  b= vec_any_ge (UCaux1.v, UCaux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (UCaux1.e[i]>=UCaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   UCaux1.v= (vector unsigned char){200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17};
   UCaux2.v= (vector unsigned char){250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux1.v= (vector unsigned char)(200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17);
   UCaux2.v= (vector unsigned char)(250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250);
# endif
  b= vec_any_ge (UCaux1.v, UCaux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (UCaux1.e[i]>=UCaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   UCaux1.v= (vector unsigned char){200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17};
   UCaux2.v= (vector unsigned char){250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux1.v= (vector unsigned char)(200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17);
   UCaux2.v= (vector unsigned char)(250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250);
# endif
  b= vec_any_ge (UCaux1.v, UCaux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (UCaux1.e[i]>=UCaux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_ge [type unsigned char]  ===> Error\n");
  else
    printf("Function vec_any_ge [type unsigned char]  ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   Saux1.v= (vector signed short){-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100};
   Saux2.v= (vector signed short){ 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Saux1.v= (vector signed short)(-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100);
   Saux2.v= (vector signed short)( 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000);
# endif
  b= vec_any_ge (Saux1.v, Saux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (Saux1.e[i]>=Saux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Saux1.v= (vector signed short){-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100};
   Saux2.v= (vector signed short){ 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Saux1.v= (vector signed short)(-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100);
   Saux2.v= (vector signed short)( 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000);
# endif
  b= vec_any_ge (Saux1.v, Saux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (Saux1.e[i]>=Saux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Saux1.v= (vector signed short){-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100};
   Saux2.v= (vector signed short){ 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Saux1.v= (vector signed short)(-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100);
   Saux2.v= (vector signed short)( 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000);
# endif
  b= vec_any_ge (Saux1.v, Saux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (Saux1.e[i]>=Saux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_ge [type short]          ===> Error\n");
  else
    printf("Function vec_any_ge [type short]          ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   USaux1.v= (vector unsigned short){48000, 47000, 46000, 45000,    0, 3300, 3200, 3100};
   USaux2.v= (vector unsigned short){59000, 59000, 59000, 59000,59000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   USaux1.v= (vector unsigned short)(48000, 47000, 46000, 45000,    0, 3300, 3200, 3100);
   USaux2.v= (vector unsigned short)(59000, 59000, 59000, 59000,59000, 9000, 9000, 9000);
# endif
  b= vec_any_ge (USaux1.v, USaux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (USaux1.e[i]>=USaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   USaux1.v= (vector unsigned short){48000, 47000, 46000, 45000,    0, 3300, 3200, 3100};
   USaux2.v= (vector unsigned short){59000, 59000, 59000, 59000,59000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   USaux1.v= (vector unsigned short)(48000, 47000, 46000, 45000,    0, 3300, 3200, 3100);
   USaux2.v= (vector unsigned short)(59000, 59000, 59000, 59000,59000, 9000, 9000, 9000);
# endif
  b= vec_any_ge (USaux1.v, USaux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (USaux1.e[i]>=USaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   USaux1.v= (vector unsigned short){48000, 47000, 46000, 45000,    0, 3300, 3200, 3100};
   USaux2.v= (vector unsigned short){59000, 59000, 59000, 59000,59000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   USaux1.v= (vector unsigned short)(48000, 47000, 46000, 45000,    0, 3300, 3200, 3100);
   USaux2.v= (vector unsigned short)(59000, 59000, 59000, 59000,59000, 9000, 9000, 9000);
# endif
  b= vec_any_ge (USaux1.v, USaux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (USaux1.e[i]>=USaux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_ge [type unsigned short] ===> Error\n");
  else
    printf("Function vec_any_ge [type unsigned short] ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   Iaux1.v= (vector signed int){-1003800, -1003700,       0,1003300};
   Iaux2.v= (vector signed int){ 9000000,  9000000, 9000000,9000000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Iaux1.v= (vector signed int)(-1003800, -1003700,       0,1003300);
   Iaux2.v= (vector signed int)( 9000000,  9000000, 9000000,9000000);
# endif
  b= vec_any_ge (Iaux1.v, Iaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Iaux1.e[i]>=Iaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Iaux1.v= (vector signed int){-1003800, -1003700,       0,1003300};
   Iaux2.v= (vector signed int){ 9000000,  9000000, 9000000,9000000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Iaux1.v= (vector signed int)(-1003800, -1003700,       0,1003300);
   Iaux2.v= (vector signed int)( 9000000,  9000000, 9000000,9000000);
# endif
  b= vec_any_ge (Iaux1.v, Iaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Iaux1.e[i]>=Iaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Iaux1.v= (vector signed int){-1003800, -1003700,       0,1003300};
   Iaux2.v= (vector signed int){ 9000000,  9000000, 9000000,9000000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Iaux1.v= (vector signed int)(-1003800, -1003700,       0,1003300);
   Iaux2.v= (vector signed int)( 9000000,  9000000, 9000000,9000000);
# endif
  b= vec_any_ge (Iaux1.v, Iaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Iaux1.e[i]>=Iaux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_ge [type int]            ===> Error\n");
  else
    printf("Function vec_any_ge [type int]            ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   UIaux1.v= (vector unsigned int){0xFFFFF000, 12345678, 0, 1};
   UIaux2.v= (vector unsigned int){0xFFFFFFF0, 20000000, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UIaux1.v= (vector unsigned int)(0xFFFFF000, 12345678, 0, 1);
   UIaux2.v= (vector unsigned int)(0xFFFFFFF0, 20000000, 9, 9);
# endif
  b= vec_any_ge (UIaux1.v, UIaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (UIaux1.e[i]>=UIaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   UIaux1.v= (vector unsigned int){0xFFFFF000, 12345678, 0, 1};
   UIaux2.v= (vector unsigned int){0xFFFFFFF0, 20000000, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UIaux1.v= (vector unsigned int)(0xFFFFF000, 12345678, 0, 1);
   UIaux2.v= (vector unsigned int)(0xFFFFFFF0, 20000000, 9, 9);
# endif
  b= vec_any_ge (UIaux1.v, UIaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (UIaux1.e[i]>=UIaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   UIaux1.v= (vector unsigned int){0xFFFFF000, 12345678, 0, 1};
   UIaux2.v= (vector unsigned int){0xFFFFFFF0, 20000000, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UIaux1.v= (vector unsigned int)(0xFFFFF000, 12345678, 0, 1);
   UIaux2.v= (vector unsigned int)(0xFFFFFFF0, 20000000, 9, 9);
# endif
  b= vec_any_ge (UIaux1.v, UIaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (UIaux1.e[i]>=UIaux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_ge [type unsigned int]   ===> Error\n");
  else
    printf("Function vec_any_ge [type unsigned int]   ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
# if defined (GCC_COMPILER)
   Faux1.v= (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux2.v= (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux2.v= (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif
  b= vec_any_ge (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Faux1.e[i]>=Faux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux2.v= (vector float) { 0.0, 3.5, 0.5, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux2.v= (vector float) ( 0.0, 3.5, 0.5, -1.5);
# endif
  b= vec_any_ge (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Faux1.e[i]>=Faux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux2.v= (vector float) { 0.0, 3.5,-0.5, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux2.v= (vector float) ( 0.0, 3.5,-0.5, -1.5);
# endif
  b= vec_any_ge (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Faux1.e[i]>=Faux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_ge [type float]          ===> Error\n");
  else
    printf("Function vec_any_ge [type float]          ===> OK\n");
#endif

/*    Function vec_any_gt    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
# if defined (GCC_COMPILER)
   Caux1.v= (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
   Caux2.v= (vector signed char){ 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Caux1.v= (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
   Caux2.v= (vector signed char)( 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9);
# endif
  b= vec_any_gt (Caux1.v, Caux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (Caux1.e[i]>Caux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Caux1.v= (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
   Caux2.v= (vector signed char){ 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Caux1.v= (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
   Caux2.v= (vector signed char)( 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9);
# endif
  b= vec_any_gt (Caux1.v, Caux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (Caux1.e[i]>Caux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Caux1.v= (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
   Caux2.v= (vector signed char){ 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Caux1.v= (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
   Caux2.v= (vector signed char)( 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9);
# endif
  b= vec_any_gt (Caux1.v, Caux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (Caux1.e[i]>Caux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_gt [type char]           ===> Error\n");
  else
    printf("Function vec_any_gt [type char]           ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   UCaux1.v= (vector unsigned char){200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17};
   UCaux2.v= (vector unsigned char){250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux1.v= (vector unsigned char)(200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17);
   UCaux2.v= (vector unsigned char)(250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250);
# endif
  b= vec_any_gt (UCaux1.v, UCaux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (UCaux1.e[i]>UCaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   UCaux1.v= (vector unsigned char){200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17};
   UCaux2.v= (vector unsigned char){250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux1.v= (vector unsigned char)(200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17);
   UCaux2.v= (vector unsigned char)(250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250);
# endif
  b= vec_any_gt (UCaux1.v, UCaux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (UCaux1.e[i]>UCaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   UCaux1.v= (vector unsigned char){200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17};
   UCaux2.v= (vector unsigned char){250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux1.v= (vector unsigned char)(200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17);
   UCaux2.v= (vector unsigned char)(250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250);
# endif
  b= vec_any_gt (UCaux1.v, UCaux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (UCaux1.e[i]>UCaux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_gt [type unsigned char]  ===> Error\n");
  else
    printf("Function vec_any_gt [type unsigned char]  ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   Saux1.v= (vector signed short){-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100};
   Saux2.v= (vector signed short){ 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Saux1.v= (vector signed short)(-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100);
   Saux2.v= (vector signed short)( 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000);
# endif
  b= vec_any_gt (Saux1.v, Saux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (Saux1.e[i]>Saux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Saux1.v= (vector signed short){-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100};
   Saux2.v= (vector signed short){ 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Saux1.v= (vector signed short)(-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100);
   Saux2.v= (vector signed short)( 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000);
# endif
  b= vec_any_gt (Saux1.v, Saux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (Saux1.e[i]>Saux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Saux1.v= (vector signed short){-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100};
   Saux2.v= (vector signed short){ 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Saux1.v= (vector signed short)(-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100);
   Saux2.v= (vector signed short)( 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000);
# endif
  b= vec_any_gt (Saux1.v, Saux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (Saux1.e[i]>Saux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_gt [type short]          ===> Error\n");
  else
    printf("Function vec_any_gt [type short]          ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   USaux1.v= (vector unsigned short){48000, 47000, 46000, 45000,    0, 3300, 3200, 3100};
   USaux2.v= (vector unsigned short){59000, 59000, 59000, 59000,59000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   USaux1.v= (vector unsigned short)(48000, 47000, 46000, 45000,    0, 3300, 3200, 3100);
   USaux2.v= (vector unsigned short)(59000, 59000, 59000, 59000,59000, 9000, 9000, 9000);
# endif
  b= vec_any_gt (USaux1.v, USaux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (USaux1.e[i]>USaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   USaux1.v= (vector unsigned short){48000, 47000, 46000, 45000,    0, 3300, 3200, 3100};
   USaux2.v= (vector unsigned short){59000, 59000, 59000, 59000,59000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   USaux1.v= (vector unsigned short)(48000, 47000, 46000, 45000,    0, 3300, 3200, 3100);
   USaux2.v= (vector unsigned short)(59000, 59000, 59000, 59000,59000, 9000, 9000, 9000);
# endif
  b= vec_any_gt (USaux1.v, USaux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (USaux1.e[i]>USaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   USaux1.v= (vector unsigned short){48000, 47000, 46000, 45000,    0, 3300, 3200, 3100};
   USaux2.v= (vector unsigned short){59000, 59000, 59000, 59000,59000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   USaux1.v= (vector unsigned short)(48000, 47000, 46000, 45000,    0, 3300, 3200, 3100);
   USaux2.v= (vector unsigned short)(59000, 59000, 59000, 59000,59000, 9000, 9000, 9000);
# endif
  b= vec_any_gt (USaux1.v, USaux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (USaux1.e[i]>USaux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_gt [type unsigned short] ===> Error\n");
  else
    printf("Function vec_any_gt [type unsigned short] ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   Iaux1.v= (vector signed int){-1003800, -1003700,       0,1003300};
   Iaux2.v= (vector signed int){ 9000000,  9000000, 9000000,9000000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Iaux1.v= (vector signed int)(-1003800, -1003700,       0,1003300);
   Iaux2.v= (vector signed int)( 9000000,  9000000, 9000000,9000000);
# endif
  b= vec_any_gt (Iaux1.v, Iaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Iaux1.e[i]>Iaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Iaux1.v= (vector signed int){-1003800, -1003700,       0,1003300};
   Iaux2.v= (vector signed int){ 9000000,  9000000, 9000000,9000000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Iaux1.v= (vector signed int)(-1003800, -1003700,       0,1003300);
   Iaux2.v= (vector signed int)( 9000000,  9000000, 9000000,9000000);
# endif
  b= vec_any_gt (Iaux1.v, Iaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Iaux1.e[i]>Iaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Iaux1.v= (vector signed int){-1003800, -1003700,       0,1003300};
   Iaux2.v= (vector signed int){ 9000000,  9000000, 9000000,9000000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Iaux1.v= (vector signed int)(-1003800, -1003700,       0,1003300);
   Iaux2.v= (vector signed int)( 9000000,  9000000, 9000000,9000000);
# endif
  b= vec_any_gt (Iaux1.v, Iaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Iaux1.e[i]>Iaux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_gt [type int]            ===> Error\n");
  else
    printf("Function vec_any_gt [type int]            ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   UIaux1.v= (vector unsigned int){0xFFFFF000, 12345678, 0, 1};
   UIaux2.v= (vector unsigned int){0xFFFFFFF0, 20000000, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UIaux1.v= (vector unsigned int)(0xFFFFF000, 12345678, 0, 1);
   UIaux2.v= (vector unsigned int)(0xFFFFFFF0, 20000000, 9, 9);
# endif
  b= vec_any_gt (UIaux1.v, UIaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (UIaux1.e[i]>UIaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   UIaux1.v= (vector unsigned int){0xFFFFF000, 12345678, 0, 1};
   UIaux2.v= (vector unsigned int){0xFFFFFFF0, 20000000, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UIaux1.v= (vector unsigned int)(0xFFFFF000, 12345678, 0, 1);
   UIaux2.v= (vector unsigned int)(0xFFFFFFF0, 20000000, 9, 9);
# endif
  b= vec_any_gt (UIaux1.v, UIaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (UIaux1.e[i]>UIaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   UIaux1.v= (vector unsigned int){0xFFFFF000, 12345678, 0, 1};
   UIaux2.v= (vector unsigned int){0xFFFFFFF0, 20000000, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UIaux1.v= (vector unsigned int)(0xFFFFF000, 12345678, 0, 1);
   UIaux2.v= (vector unsigned int)(0xFFFFFFF0, 20000000, 9, 9);
# endif
  b= vec_any_gt (UIaux1.v, UIaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (UIaux1.e[i]>UIaux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_gt [type unsigned int]   ===> Error\n");
  else
    printf("Function vec_any_gt [type unsigned int]   ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
# if defined (GCC_COMPILER)
   Faux1.v= (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux2.v= (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux2.v= (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif
  b= vec_any_gt (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Faux1.e[i]>Faux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux2.v= (vector float) { 0.0, 3.5, 0.5, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux2.v= (vector float) ( 0.0, 3.5, 0.5, -1.5);
# endif
  b= vec_any_gt (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Faux1.e[i]>Faux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux2.v= (vector float) { 0.0, 3.5,-0.5, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux2.v= (vector float) ( 0.0, 3.5,-0.5, -1.5);
# endif
  b= vec_any_gt (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Faux1.e[i]>Faux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_gt [type float]          ===> Error\n");
  else
    printf("Function vec_any_gt [type float]          ===> OK\n");
#endif


/*    Function vec_any_le   */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
# if defined (GCC_COMPILER)
   Caux2.v= (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
   Caux1.v= (vector signed char){ 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Caux2.v= (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
   Caux1.v= (vector signed char)( 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9);
# endif
  b= vec_any_le (Caux1.v, Caux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (Caux1.e[i]<=Caux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Caux2.v= (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
   Caux1.v= (vector signed char){ 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Caux2.v= (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
   Caux1.v= (vector signed char)( 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9);
# endif
  b= vec_any_le (Caux1.v, Caux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (Caux1.e[i]<=Caux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Caux2.v= (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
   Caux1.v= (vector signed char){ 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Caux2.v= (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
   Caux1.v= (vector signed char)( 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9);
# endif
  b= vec_any_le (Caux1.v, Caux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (Caux1.e[i]<=Caux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_le [type char]           ===> Error\n");
  else
    printf("Function vec_any_le [type char]           ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   UCaux2.v= (vector unsigned char){200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17};
   UCaux1.v= (vector unsigned char){250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux2.v= (vector unsigned char)(200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17);
   UCaux1.v= (vector unsigned char)(250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250);
# endif
  b= vec_any_le (UCaux1.v, UCaux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (UCaux1.e[i]<=UCaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   UCaux2.v= (vector unsigned char){200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17};
   UCaux1.v= (vector unsigned char){250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux2.v= (vector unsigned char)(200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17);
   UCaux1.v= (vector unsigned char)(250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250);
# endif
  b= vec_any_le (UCaux1.v, UCaux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (UCaux1.e[i]<=UCaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   UCaux2.v= (vector unsigned char){200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17};
   UCaux1.v= (vector unsigned char){250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux2.v= (vector unsigned char)(200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17);
   UCaux1.v= (vector unsigned char)(250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250);
# endif
  b= vec_any_le (UCaux1.v, UCaux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (UCaux1.e[i]<=UCaux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_le [type unsigned char]  ===> Error\n");
  else
    printf("Function vec_any_le [type unsigned char]  ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   Saux2.v= (vector signed short){-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100};
   Saux1.v= (vector signed short){ 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Saux2.v= (vector signed short)(-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100);
   Saux1.v= (vector signed short)( 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000);
# endif
  b= vec_any_le (Saux1.v, Saux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (Saux1.e[i]<=Saux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Saux2.v= (vector signed short){-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100};
   Saux1.v= (vector signed short){ 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Saux2.v= (vector signed short)(-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100);
   Saux1.v= (vector signed short)( 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000);
# endif
  b= vec_any_le (Saux1.v, Saux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (Saux1.e[i]<=Saux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Saux2.v= (vector signed short){-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100};
   Saux1.v= (vector signed short){ 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Saux2.v= (vector signed short)(-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100);
   Saux1.v= (vector signed short)( 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000);
# endif
  b= vec_any_le (Saux1.v, Saux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (Saux1.e[i]<=Saux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_le [type short]          ===> Error\n");
  else
    printf("Function vec_any_le [type short]          ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   USaux2.v= (vector unsigned short){48000, 47000, 46000, 45000,    0, 3300, 3200, 3100};
   USaux1.v= (vector unsigned short){59000, 59000, 59000, 59000,59000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   USaux2.v= (vector unsigned short)(48000, 47000, 46000, 45000,    0, 3300, 3200, 3100);
   USaux1.v= (vector unsigned short)(59000, 59000, 59000, 59000,59000, 9000, 9000, 9000);
# endif
  b= vec_any_le (USaux1.v, USaux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (USaux1.e[i]<=USaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   USaux2.v= (vector unsigned short){48000, 47000, 46000, 45000,    0, 3300, 3200, 3100};
   USaux1.v= (vector unsigned short){59000, 59000, 59000, 59000,59000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   USaux2.v= (vector unsigned short)(48000, 47000, 46000, 45000,    0, 3300, 3200, 3100);
   USaux1.v= (vector unsigned short)(59000, 59000, 59000, 59000,59000, 9000, 9000, 9000);
# endif
  b= vec_any_le (USaux1.v, USaux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (USaux1.e[i]<=USaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   USaux2.v= (vector unsigned short){48000, 47000, 46000, 45000,    0, 3300, 3200, 3100};
   USaux1.v= (vector unsigned short){59000, 59000, 59000, 59000,59000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   USaux2.v= (vector unsigned short)(48000, 47000, 46000, 45000,    0, 3300, 3200, 3100);
   USaux1.v= (vector unsigned short)(59000, 59000, 59000, 59000,59000, 9000, 9000, 9000);
# endif
  b= vec_any_le (USaux1.v, USaux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (USaux1.e[i]<=USaux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_le [type unsigned short] ===> Error\n");
  else
    printf("Function vec_any_le [type unsigned short] ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   Iaux2.v= (vector signed int){-1003800, -1003700,       0,1003300};
   Iaux1.v= (vector signed int){ 9000000,  9000000, 9000000,9000000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Iaux2.v= (vector signed int)(-1003800, -1003700,       0,1003300);
   Iaux1.v= (vector signed int)( 9000000,  9000000, 9000000,9000000);
# endif
  b= vec_any_le (Iaux1.v, Iaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Iaux1.e[i]<=Iaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Iaux2.v= (vector signed int){-1003800, -1003700,       0,1003300};
   Iaux1.v= (vector signed int){ 9000000,  9000000, 9000000,9000000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Iaux2.v= (vector signed int)(-1003800, -1003700,       0,1003300);
   Iaux1.v= (vector signed int)( 9000000,  9000000, 9000000,9000000);
# endif
  b= vec_any_le (Iaux1.v, Iaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Iaux1.e[i]<=Iaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Iaux2.v= (vector signed int){-1003800, -1003700,       0,1003300};
   Iaux1.v= (vector signed int){ 9000000,  9000000, 9000000,9000000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Iaux2.v= (vector signed int)(-1003800, -1003700,       0,1003300);
   Iaux1.v= (vector signed int)( 9000000,  9000000, 9000000,9000000);
# endif
  b= vec_any_le (Iaux1.v, Iaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Iaux1.e[i]<=Iaux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_le [type int]            ===> Error\n");
  else
    printf("Function vec_any_le [type int]            ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   UIaux2.v= (vector unsigned int){0xFFFFF000, 12345678, 0, 1};
   UIaux1.v= (vector unsigned int){0xFFFFFFF0, 20000000, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UIaux2.v= (vector unsigned int)(0xFFFFF000, 12345678, 0, 1);
   UIaux1.v= (vector unsigned int)(0xFFFFFFF0, 20000000, 9, 9);
# endif
  b= vec_any_le (UIaux1.v, UIaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (UIaux1.e[i]<=UIaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   UIaux2.v= (vector unsigned int){0xFFFFF000, 12345678, 0, 1};
   UIaux1.v= (vector unsigned int){0xFFFFFFF0, 20000000, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UIaux2.v= (vector unsigned int)(0xFFFFF000, 12345678, 0, 1);
   UIaux1.v= (vector unsigned int)(0xFFFFFFF0, 20000000, 9, 9);
# endif
  b= vec_any_le (UIaux1.v, UIaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (UIaux1.e[i]<=UIaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   UIaux2.v= (vector unsigned int){0xFFFFF000, 12345678, 0, 1};
   UIaux1.v= (vector unsigned int){0xFFFFFFF0, 20000000, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UIaux2.v= (vector unsigned int)(0xFFFFF000, 12345678, 0, 1);
   UIaux1.v= (vector unsigned int)(0xFFFFFFF0, 20000000, 9, 9);
# endif
  b= vec_any_le (UIaux1.v, UIaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (UIaux1.e[i]<=UIaux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_le [type unsigned int]   ===> Error\n");
  else
    printf("Function vec_any_le [type unsigned int]   ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
# if defined (GCC_COMPILER)
   Faux2.v= (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux1.v= (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux2.v= (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux1.v= (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif
  b= vec_any_le (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Faux1.e[i]<=Faux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux2.v= (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux1.v= (vector float) { 0.0, 3.5, 0.5, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux2.v= (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux1.v= (vector float) ( 0.0, 3.5, 0.5, -1.5);
# endif
  b= vec_any_le (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Faux1.e[i]<=Faux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux2.v= (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux1.v= (vector float) { 0.0, 3.5,-0.5, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux2.v= (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux1.v= (vector float) ( 0.0, 3.5,-0.5, -1.5);
# endif
  b= vec_any_le (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Faux1.e[i]<=Faux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_le [type float]          ===> Error\n");
  else
    printf("Function vec_any_le [type float]          ===> OK\n");
#endif


/*    Function vec_any_lt   */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
# if defined (GCC_COMPILER)
   Caux2.v= (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
   Caux1.v= (vector signed char){ 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Caux2.v= (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
   Caux1.v= (vector signed char)( 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9);
# endif
  b= vec_any_lt (Caux1.v, Caux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (Caux1.e[i]<Caux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Caux2.v= (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
   Caux1.v= (vector signed char){ 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Caux2.v= (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
   Caux1.v= (vector signed char)( 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9);
# endif
  b= vec_any_lt (Caux1.v, Caux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (Caux1.e[i]<Caux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Caux2.v= (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
   Caux1.v= (vector signed char){ 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Caux2.v= (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
   Caux1.v= (vector signed char)( 9,  9,  9,  9,  9,  9,  9,  9, 9, 9, 9, 9, 9, 9, 9, 9);
# endif
  b= vec_any_lt (Caux1.v, Caux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (Caux1.e[i]<Caux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_lt [type char]           ===> Error\n");
  else
    printf("Function vec_any_lt [type char]           ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   UCaux2.v= (vector unsigned char){200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17};
   UCaux1.v= (vector unsigned char){250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux2.v= (vector unsigned char)(200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17);
   UCaux1.v= (vector unsigned char)(250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250);
# endif
  b= vec_any_lt (UCaux1.v, UCaux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (UCaux1.e[i]<UCaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   UCaux2.v= (vector unsigned char){200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17};
   UCaux1.v= (vector unsigned char){250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux2.v= (vector unsigned char)(200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17);
   UCaux1.v= (vector unsigned char)(250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250);
# endif
  b= vec_any_lt (UCaux1.v, UCaux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (UCaux1.e[i]<UCaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   UCaux2.v= (vector unsigned char){200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17};
   UCaux1.v= (vector unsigned char){250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux2.v= (vector unsigned char)(200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17);
   UCaux1.v= (vector unsigned char)(250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250);
# endif
  b= vec_any_lt (UCaux1.v, UCaux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (UCaux1.e[i]<UCaux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_lt [type unsigned char]  ===> Error\n");
  else
    printf("Function vec_any_lt [type unsigned char]  ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   Saux2.v= (vector signed short){-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100};
   Saux1.v= (vector signed short){ 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Saux2.v= (vector signed short)(-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100);
   Saux1.v= (vector signed short)( 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000);
# endif
  b= vec_any_lt (Saux1.v, Saux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (Saux1.e[i]<Saux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Saux2.v= (vector signed short){-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100};
   Saux1.v= (vector signed short){ 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Saux2.v= (vector signed short)(-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100);
   Saux1.v= (vector signed short)( 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000);
# endif
  b= vec_any_lt (Saux1.v, Saux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (Saux1.e[i]<Saux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Saux2.v= (vector signed short){-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100};
   Saux1.v= (vector signed short){ 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Saux2.v= (vector signed short)(-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100);
   Saux1.v= (vector signed short)( 9000,  9000,  9000,  9000, 9000, 9000, 9000, 9000);
# endif
  b= vec_any_lt (Saux1.v, Saux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (Saux1.e[i]<Saux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_lt [type short]          ===> Error\n");
  else
    printf("Function vec_any_lt [type short]          ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   USaux2.v= (vector unsigned short){48000, 47000, 46000, 45000,    0, 3300, 3200, 3100};
   USaux1.v= (vector unsigned short){59000, 59000, 59000, 59000,59000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   USaux2.v= (vector unsigned short)(48000, 47000, 46000, 45000,    0, 3300, 3200, 3100);
   USaux1.v= (vector unsigned short)(59000, 59000, 59000, 59000,59000, 9000, 9000, 9000);
# endif
  b= vec_any_lt (USaux1.v, USaux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (USaux1.e[i]<USaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   USaux2.v= (vector unsigned short){48000, 47000, 46000, 45000,    0, 3300, 3200, 3100};
   USaux1.v= (vector unsigned short){59000, 59000, 59000, 59000,59000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   USaux2.v= (vector unsigned short)(48000, 47000, 46000, 45000,    0, 3300, 3200, 3100);
   USaux1.v= (vector unsigned short)(59000, 59000, 59000, 59000,59000, 9000, 9000, 9000);
# endif
  b= vec_any_lt (USaux1.v, USaux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (USaux1.e[i]<USaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   USaux2.v= (vector unsigned short){48000, 47000, 46000, 45000,    0, 3300, 3200, 3100};
   USaux1.v= (vector unsigned short){59000, 59000, 59000, 59000,59000, 9000, 9000, 9000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   USaux2.v= (vector unsigned short)(48000, 47000, 46000, 45000,    0, 3300, 3200, 3100);
   USaux1.v= (vector unsigned short)(59000, 59000, 59000, 59000,59000, 9000, 9000, 9000);
# endif
  b= vec_any_lt (USaux1.v, USaux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (USaux1.e[i]<USaux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_lt [type unsigned short] ===> Error\n");
  else
    printf("Function vec_any_lt [type unsigned short] ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   Iaux2.v= (vector signed int){-1003800, -1003700,       0,1003300};
   Iaux1.v= (vector signed int){ 9000000,  9000000, 9000000,9000000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Iaux2.v= (vector signed int)(-1003800, -1003700,       0,1003300);
   Iaux1.v= (vector signed int)( 9000000,  9000000, 9000000,9000000);
# endif
  b= vec_any_lt (Iaux1.v, Iaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Iaux1.e[i]<Iaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Iaux2.v= (vector signed int){-1003800, -1003700,       0,1003300};
   Iaux1.v= (vector signed int){ 9000000,  9000000, 9000000,9000000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Iaux2.v= (vector signed int)(-1003800, -1003700,       0,1003300);
   Iaux1.v= (vector signed int)( 9000000,  9000000, 9000000,9000000);
# endif
  b= vec_any_lt (Iaux1.v, Iaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Iaux1.e[i]<Iaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Iaux2.v= (vector signed int){-1003800, -1003700,       0,1003300};
   Iaux1.v= (vector signed int){ 9000000,  9000000, 9000000,9000000};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Iaux2.v= (vector signed int)(-1003800, -1003700,       0,1003300);
   Iaux1.v= (vector signed int)( 9000000,  9000000, 9000000,9000000);
# endif
  b= vec_any_lt (Iaux1.v, Iaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Iaux1.e[i]<Iaux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_lt [type int]            ===> Error\n");
  else
    printf("Function vec_any_lt [type int]            ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   UIaux2.v= (vector unsigned int){0xFFFFF000, 12345678, 0, 1};
   UIaux1.v= (vector unsigned int){0xFFFFFFF0, 20000000, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UIaux2.v= (vector unsigned int)(0xFFFFF000, 12345678, 0, 1);
   UIaux1.v= (vector unsigned int)(0xFFFFFFF0, 20000000, 9, 9);
# endif
  b= vec_any_lt (UIaux1.v, UIaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (UIaux1.e[i]<UIaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   UIaux2.v= (vector unsigned int){0xFFFFF000, 12345678, 0, 1};
   UIaux1.v= (vector unsigned int){0xFFFFFFF0, 12345678, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UIaux2.v= (vector unsigned int)(0xFFFFF000, 12345678, 0, 1);
   UIaux1.v= (vector unsigned int)(0xFFFFFFF0, 12345678, 9, 9);
# endif
  b= vec_any_lt (UIaux1.v, UIaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (UIaux1.e[i]<UIaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   UIaux2.v= (vector unsigned int){0xFFFFF000, 12345678, 0, 1};
   UIaux1.v= (vector unsigned int){0xFFFFFFF0, 10000000, 9, 9};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UIaux2.v= (vector unsigned int)(0xFFFFF000, 12345678, 0, 1);
   UIaux1.v= (vector unsigned int)(0xFFFFFFF0, 10000000, 9, 9);
# endif
  b= vec_any_lt (UIaux1.v, UIaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (UIaux1.e[i]<UIaux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_lt [type unsigned int]   ===> Error\n");
  else
    printf("Function vec_any_lt [type unsigned int]   ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
# if defined (GCC_COMPILER)
   Faux2.v= (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux1.v= (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux2.v= (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux1.v= (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif
  b= vec_any_lt (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Faux1.e[i]<Faux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux2.v= (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux1.v= (vector float) { 0.0, 3.5, 0.5, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux2.v= (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux1.v= (vector float) ( 0.0, 3.5, 0.5, -1.5);
# endif
  b= vec_any_lt (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Faux1.e[i]<Faux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux2.v= (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux1.v= (vector float) { 0.0, 3.5,-0.5, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux2.v= (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux1.v= (vector float) ( 0.0, 3.5,-0.5, -1.5);
# endif
  b= vec_any_lt (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Faux1.e[i]<Faux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_lt [type float]          ===> Error\n");
  else
    printf("Function vec_any_lt [type float]          ===> OK\n");
#endif


#if defined TEST_FLOATS
/*    Function vec_any_nan    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
# if defined (GCC_COMPILER)
   Faux1.v= (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif
  b= vec_any_nan (Faux1.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || isnan(Faux1.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) { 0.0, 3.5, NAN, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) ( 0.0, 3.5, NAN, -1.5);
# endif
  b= vec_any_nan (Faux1.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || isnan(Faux1.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) { NAN, 3.5, NAN, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) ( NAN, 3.5, NAN, -1.5);
# endif
  b= vec_any_nan (Faux1.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || isnan(Faux1.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_nan [type float]         ===> Error\n");
  else
    printf("Function vec_any_nan [type float]         ===> OK\n");
#endif


/*    Function vec_any_ne   */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
# if defined (GCC_COMPILER)
   Caux1.v= (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
   Caux2.v= (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Caux1.v= (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
   Caux2.v= (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
# endif
  b= vec_any_ne (Caux1.v, Caux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (Caux1.e[i]!=Caux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Caux1.v= (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
   Caux2.v= (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Caux1.v= (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
   Caux2.v= (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
# endif
  b= vec_any_ne (Caux1.v, Caux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (Caux1.e[i]!=Caux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Caux1.v= (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
   Caux2.v= (vector signed char){-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Caux1.v= (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
   Caux2.v= (vector signed char)(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7);
# endif
  b= vec_any_ne (Caux1.v, Caux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (Caux1.e[i]!=Caux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_ne [type char]           ===> Error\n");
  else
    printf("Function vec_any_ne [type char]           ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   UCaux1.v= (vector unsigned char){200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17};
   UCaux2.v= (vector unsigned char){200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux1.v= (vector unsigned char)(200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17);
   UCaux2.v= (vector unsigned char)(200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17);
# endif
  b= vec_any_ne (UCaux1.v, UCaux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (UCaux1.e[i]!=UCaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   UCaux1.v= (vector unsigned char){200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17};
   UCaux2.v= (vector unsigned char){200, 201, 206, 205,   0, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux1.v= (vector unsigned char)(200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17);
   UCaux2.v= (vector unsigned char)(200, 201, 206, 205,   0, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17);
# endif
  b= vec_any_ne (UCaux1.v, UCaux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (UCaux1.e[i]!=UCaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   UCaux1.v= (vector unsigned char){200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17};
   UCaux2.v= (vector unsigned char){200, 201, 206, 206,   0, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UCaux1.v= (vector unsigned char)(200, 201, 206, 205, 204, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17);
   UCaux2.v= (vector unsigned char)(200, 201, 206, 206,   0, 203, 202, 201, 200, 101, 102,  13,  14,  15,  16, 17);
# endif
  b= vec_any_ne (UCaux1.v, UCaux2.v);
  bAux= 0;
  for (i=0; i<16; i++)
    bAux= bAux || (UCaux1.e[i]!=UCaux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_ne [type unsigned char]  ===> Error\n");
  else
    printf("Function vec_any_ne [type unsigned char]  ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   Saux1.v= (vector signed short){-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100};
   Saux2.v= (vector signed short){-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Saux1.v= (vector signed short)(-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100);
   Saux2.v= (vector signed short)(-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100);
# endif
  b= vec_any_ne (Saux1.v, Saux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (Saux1.e[i]!=Saux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Saux1.v= (vector signed short){-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100};
   Saux2.v= (vector signed short){-3800,  3700, -3600, -3500,    0, 3300, 3200, 3100};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Saux1.v= (vector signed short)(-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100);
   Saux2.v= (vector signed short)(-3800,  3700, -3600, -3500,    0, 3300, 3200, 3100);
# endif
  b= vec_any_ne (Saux1.v, Saux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (Saux1.e[i]!=Saux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Saux1.v= (vector signed short){-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100};
   Saux2.v= (vector signed short){-3800, -3700, -3600, -3500,    0, 3300, 3100, 3100};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Saux1.v= (vector signed short)(-3800, -3700, -3600, -3500,    0, 3300, 3200, 3100);
   Saux2.v= (vector signed short)(-3800, -3700, -3600, -3500,    0, 3300, 3100, 3100);
# endif
  b= vec_any_ne (Saux1.v, Saux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (Saux1.e[i]!=Saux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_ne [type short]          ===> Error\n");
  else
    printf("Function vec_any_ne [type short]          ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   USaux1.v= (vector unsigned short){48000, 47000, 46000, 45000,    0, 3300, 3200, 3100};
   USaux2.v= (vector unsigned short){48000, 47000, 46000, 45000,    0, 3300, 3200, 3100};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   USaux1.v= (vector unsigned short)(48000, 47000, 46000, 45000,    0, 3300, 3200, 3100);
   USaux2.v= (vector unsigned short)(48000, 47000, 46000, 45000,    0, 3300, 3200, 3100);
# endif
  b= vec_any_ne (USaux1.v, USaux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (USaux1.e[i]!=USaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   USaux1.v= (vector unsigned short){48000, 47000, 46000, 45000,    0, 3300, 3200, 3100};
   USaux2.v= (vector unsigned short){48000, 47000, 46000, 45000,    0, 3300, 3100, 3100};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   USaux1.v= (vector unsigned short)(48000, 47000, 46000, 45000,    0, 3300, 3200, 3100);
   USaux2.v= (vector unsigned short)(48000, 47000, 46000, 45000,    0, 3300, 3100, 3100);
# endif
  b= vec_any_ne (USaux1.v, USaux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (USaux1.e[i]!=USaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   USaux1.v= (vector unsigned short){48000, 47000, 46000, 45000,    0, 3300, 3200, 3100};
   USaux2.v= (vector unsigned short){48000, 47000, 46000,     0,    0, 3300, 3100, 3100};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   USaux1.v= (vector unsigned short)(48000, 47000, 46000, 45000,    0, 3300, 3200, 3100);
   USaux2.v= (vector unsigned short)(48000, 47000, 46000,     0,    0, 3300, 3100, 3100);
# endif
  b= vec_any_ne (USaux1.v, USaux2.v);
  bAux= 0;
  for (i=0; i<8; i++)
    bAux= bAux || (USaux1.e[i]!=USaux2.e[i]);
  if (bAux!=b) err= 1;
  
  if (err)
    printf("Function vec_any_ne [type unsigned short] ===> Error\n");
  else
    printf("Function vec_any_ne [type unsigned short] ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   Iaux1.v= (vector signed int){-1003800, -1003700,       0,1003300};
   Iaux2.v= (vector signed int){-1003800, -1003700,       0,1003300};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Iaux1.v= (vector signed int)(-1003800, -1003700,       0,1003300);
   Iaux2.v= (vector signed int)(-1003800, -1003700,       0,1003300);
# endif
  b= vec_any_ne (Iaux1.v, Iaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Iaux1.e[i]!=Iaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Iaux1.v= (vector signed int){-1003800, -1003700,       0,1003300};
   Iaux2.v= (vector signed int){-1003800, -1003700,       0,1113300};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Iaux1.v= (vector signed int)(-1003800, -1003700,       0,1003300);
   Iaux2.v= (vector signed int)(-1003800, -1003700,       0,1113300);
# endif  
  b= vec_any_ne (Iaux1.v, Iaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Iaux1.e[i]!=Iaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Iaux1.v= (vector signed int){-1003800, -1003700,       0,1003300};
   Iaux2.v= (vector signed int){-1003800,       10,       0,1113300};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Iaux1.v= (vector signed int)(-1003800, -1003700,       0,1003300);
   Iaux2.v= (vector signed int)(-1003800,       10,       0,1113300);
# endif  
  b= vec_any_ne (Iaux1.v, Iaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Iaux1.e[i]!=Iaux2.e[i]);
  if (bAux!=b) err= 1;
  
  if (err)
    printf("Function vec_any_ne [type int]            ===> Error\n");
  else
    printf("Function vec_any_ne [type int]            ===> OK\n");


  err = 0;
# if defined (GCC_COMPILER)
   UIaux1.v= (vector unsigned int){0xFFFFF000, 12345678, 0, 1};
   UIaux2.v= (vector unsigned int){0xFFFFF000, 12345678, 0, 1};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UIaux1.v= (vector unsigned int)(0xFFFFF000, 12345678, 0, 1);
   UIaux2.v= (vector unsigned int)(0xFFFFF000, 12345678, 0, 1);
# endif  
  b= vec_any_ne (UIaux1.v, UIaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (UIaux1.e[i]!=UIaux2.e[i]);
  if (bAux!=b) err= 1;
  
# if defined (GCC_COMPILER)
   UIaux1.v= (vector unsigned int){0xFFFFF000, 12345678, 0, 1};
   UIaux2.v= (vector unsigned int){0xFFFFF000, 12345678, 5, 1};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UIaux1.v= (vector unsigned int)(0xFFFFF000, 12345678, 0, 1);
   UIaux2.v= (vector unsigned int)(0xFFFFF000, 12345678, 5, 1);
# endif
  b= vec_any_ne (UIaux1.v, UIaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (UIaux1.e[i]!=UIaux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   UIaux1.v= (vector unsigned int){0xFFFFF000, 12345678, 0, 1};
   UIaux2.v= (vector unsigned int){0xFFFFFFF0, 12345678, 5, 1};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   UIaux1.v= (vector unsigned int)(0xFFFFF000, 12345678, 0, 1);
   UIaux2.v= (vector unsigned int)(0xFFFFFFF0, 12345678, 5, 1);
# endif
  b= vec_any_ne (UIaux1.v, UIaux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (UIaux1.e[i]!=UIaux2.e[i]);
  if (bAux!=b) err= 1;
  
  if (err)
    printf("Function vec_any_ne [type unsigned int]   ===> Error\n");
  else
    printf("Function vec_any_ne [type unsigned int]   ===> OK\n");

#if defined TEST_FLOATS
  err = 0;
# if defined (GCC_COMPILER)
   Faux1.v= (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux2.v= (vector float) {-1.5, 1.0, 0.5, -3.999};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux2.v= (vector float) (-1.5, 1.0, 0.5, -3.999);
# endif
  b= vec_any_ne (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Faux1.e[i]!=Faux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux2.v= (vector float) {-1.5, 1.0, 0.5, -3.998};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux2.v= (vector float) (-1.5, 1.0, 0.5, -3.998);
# endif
  b= vec_any_ne (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Faux1.e[i]!=Faux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux2.v= (vector float) {-1.5, 0.0, 0.5, -3.998};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux2.v= (vector float) (-1.5, 0.0, 0.5, -3.998);
# endif
  b= vec_any_ne (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || (Faux1.e[i]!=Faux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_ne [type float]          ===> Error\n");
  else
    printf("Function vec_any_ne [type float]          ===> OK\n");
#endif


#if defined TEST_FLOATS
/*    Function vec_any_nge    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
# if defined (GCC_COMPILER)
   Faux1.v= (vector float) { 0.0, 3.5, 0.55, -1.5};
   Faux2.v= (vector float) {-1.5, 1.0, 0.5, -3.999};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) ( 0.0, 3.5, 0.55, -1.5);
   Faux2.v= (vector float) (-1.5, 1.0, 0.5, -3.999);
# endif
  b= vec_any_nge (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || 
         (Faux1.e[i]<Faux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) { 0.0, 3.5, 0.55, -1.5};
   Faux2.v= (vector float) {-1.5, 1.0, 0.55, -3.999};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) ( 0.0, 3.5, 0.55, -1.5);
   Faux2.v= (vector float) (-1.5, 1.0, 0.55, -3.999);
# endif
  b= vec_any_nge (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || 
         (Faux1.e[i]<Faux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) { 0.0, 3.5, 0.55, -1.5};
   Faux2.v= (vector float) {-1.5, 5.0, 0.5, -3.999};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) ( 0.0, 3.5, 0.55, -1.5);
   Faux2.v= (vector float) (-1.5, 5.0, 0.5, -3.999);
# endif
  b= vec_any_nge (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || 
         (Faux1.e[i]<Faux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) { 0.0, 3.5, 0.55, -1.5};
   Faux2.v= (vector float) {-1.5, 1.0, NAN, -3.999};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) ( 0.0, 3.5, 0.55, -1.5);
   Faux2.v= (vector float) (-1.5, 1.0, NAN, -3.999);
# endif
  b= vec_any_nge (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || 
         (Faux1.e[i]<Faux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_nge [type float]         ===> Error\n");
  else
    printf("Function vec_any_nge [type float]         ===> OK\n");
#endif


#if defined TEST_FLOATS
/*    Function vec_any_ngt    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
# if defined (GCC_COMPILER)
   Faux1.v= (vector float) { 0.0, 3.5, 0.55, -1.5};
   Faux2.v= (vector float) {-1.5, 1.0, 0.5, -3.999};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) ( 0.0, 3.5, 0.55, -1.5);
   Faux2.v= (vector float) (-1.5, 1.0, 0.5, -3.999);
# endif
  b= vec_any_ngt (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || isnan(Faux1.e[i]) || isnan(Faux2.e[i]) ||
          !(Faux1.e[i]>Faux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) { 0.0, 3.5, 0.55, -1.5};
   Faux2.v= (vector float) {-1.5, 1.0, 0.55, -3.999};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) ( 0.0, 3.5, 0.55, -1.5);
   Faux2.v= (vector float) (-1.5, 1.0, 0.55, -3.999);
# endif
  b= vec_any_ngt (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || isnan(Faux1.e[i]) || isnan(Faux2.e[i]) ||
          !(Faux1.e[i]>Faux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) { 0.0, 3.5, 0.55, -1.5};
   Faux2.v= (vector float) {-1.5, 5.0, 0.5, -3.999};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) ( 0.0, 3.5, 0.55, -1.5);
   Faux2.v= (vector float) (-1.5, 5.0, 0.5, -3.999);
# endif
  b= vec_any_ngt (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || isnan(Faux1.e[i]) || isnan(Faux2.e[i]) ||
          !(Faux1.e[i]>Faux2.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) { 0.0, 3.5, 0.55, -1.5};
   Faux2.v= (vector float) {-1.5, 1.0, NAN, -3.999};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) ( 0.0, 3.5, 0.55, -1.5);
   Faux2.v= (vector float) (-1.5, 1.0, NAN, -3.999);
# endif
  b= vec_any_ngt (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || isnan(Faux1.e[i]) || isnan(Faux2.e[i]) ||
          !(Faux1.e[i]>Faux2.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_ngt [type float]         ===> Error\n");
  else
    printf("Function vec_any_ngt [type float]         ===> OK\n");
#endif


#if defined TEST_FLOATS
/*    Function vec_any_nle    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
# if defined (GCC_COMPILER)
   Faux1.v= (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux2.v= (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux2.v= (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif
  b= vec_any_nle (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || 
         (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || !(Faux1.e[i]<=Faux2.e[i]));
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) {-1.5, 1.0, 0.55, -3.999};
   Faux2.v= (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) (-1.5, 1.0, 0.55, -3.999);
   Faux2.v= (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif
  b= vec_any_nle (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || 
         (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || !(Faux1.e[i]<=Faux2.e[i]));
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) {-1.5, 5.0, 0.5, -3.999};
   Faux2.v= (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) (-1.5, 5.0, 0.5, -3.999);
   Faux2.v= (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif
  b= vec_any_nle (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || 
         (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || !(Faux1.e[i]<=Faux2.e[i]));
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) {-1.5, 1.0, NAN, -3.999};
   Faux2.v= (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) (-1.5, 1.0, NAN, -3.999);
   Faux2.v= (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif
  b= vec_any_nle (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || 
         (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || !(Faux1.e[i]<=Faux2.e[i]));
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_nle [type float]         ===> Error\n");
  else
    printf("Function vec_any_nle [type float]         ===> OK\n");
#endif


#if defined TEST_FLOATS
/*    Function vec_any_nlt    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
# if defined (GCC_COMPILER)
   Faux1.v= (vector float) {-1.5, 1.0, 0.5, -3.999};
   Faux2.v= (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) (-1.5, 1.0, 0.5, -3.999);
   Faux2.v= (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif
  b= vec_any_nlt (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || 
         (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || !(Faux1.e[i]<Faux2.e[i]));
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) {-1.5, 1.0, 0.55, -3.999};
   Faux2.v= (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) (-1.5, 1.0, 0.55, -3.999);
   Faux2.v= (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif
  b= vec_all_nlt (Faux1.v, Faux2.v);
  b= vec_any_nlt (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || 
         (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || !(Faux1.e[i]<Faux2.e[i]));
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) {-1.5, 5.0, 0.5, -3.999};
   Faux2.v= (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) (-1.5, 5.0, 0.5, -3.999);
   Faux2.v= (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif
  b= vec_any_nlt (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || 
         (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || !(Faux1.e[i]<Faux2.e[i]));
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) {-1.5, 1.0, NAN, -3.999};
   Faux2.v= (vector float) { 0.0, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) (-1.5, 1.0, NAN, -3.999);
   Faux2.v= (vector float) ( 0.0, 3.5, 0.55, -1.5);
# endif
  b= vec_any_nlt (Faux1.v, Faux2.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || 
         (isnan(Faux1.e[i]) || isnan(Faux2.e[i]) || !(Faux1.e[i]<Faux2.e[i]));
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_nlt [type float]         ===> Error\n");
  else
    printf("Function vec_any_nlt [type float]         ===> OK\n");
#endif


#if defined TEST_FLOATS
/*    Function vec_any_numeric    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
# if defined (GCC_COMPILER)
   Faux1.v= (vector float) { NAN, NAN, NAN, NAN};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) ( NAN, NAN, NAN, NAN);
# endif
  b= vec_any_numeric (Faux1.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || !isnan(Faux1.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) { NAN, 3.5, NAN, NAN};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) ( NAN, 3.5, NAN, NAN);
# endif
  b= vec_any_numeric (Faux1.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || !isnan(Faux1.e[i]);
  if (bAux!=b) err= 1;

# if defined (GCC_COMPILER)
   Faux1.v= (vector float) { -1.5, 3.5, 0.55, -1.5};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v= (vector float) ( -1.5, 3.5, 0.55, -1.5);
# endif
  b= vec_any_numeric (Faux1.v);
  bAux= 0;
  for (i=0; i<4; i++)
    bAux= bAux || !isnan(Faux1.e[i]);
  if (bAux!=b) err= 1;

  if (err)
    printf("Function vec_any_numeric [type float]     ===> Error\n");
  else
    printf("Function vec_any_numeric [type float]     ===> OK\n");
#endif


#if defined TEST_FLOATS
/*    Function vec_any_out    */
  printf("\n:::::::::::::::::::::::::::::::::::::::\n");
  err = 0;
  Faux1.v = Fcons1;
  Faux2.v = Fcons2;
  I1 = vec_any_out( Faux1.v, Faux2.v );
  Iaux = 0;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux || ((isnan(Faux1.e[i])) || (isnan(Faux2.e[i])) || 
                    (Faux1.e[i]>Faux2.e[i]) || (Faux1.e[i]<-Faux2.e[i]));
  }
  if (I1 != Iaux) err++;
  
# if defined (GCC_COMPILER)
   Faux1.v = (vector float){-0.5, 1.0, 0, -0.999};
# elif defined (MAC_COMPILER) || defined (XLC_COMPILER)
   Faux1.v = (vector float)(-0.5, 1.0, 0, -0.999);
# endif
  Faux2.v = Fcons2;
  I1 = vec_any_out( Faux1.v, Faux2.v );
  Iaux = 0;
  for ( i=0; i< 4; i++ )
  {
    Iaux = Iaux || ((isnan(Faux1.e[i])) || (isnan(Faux2.e[i])) || 
                    (Faux1.e[i]>Faux2.e[i]) || (Faux1.e[i]<-Faux2.e[i]));
  }
  if (I1 != Iaux) err++;
  
  if (err)
    printf("Function vec_any_out [type float]         ===> Error\n");
  else
    printf("Function vec_any_out [type float]         ===> OK\n");
#endif

  return 0;
}
