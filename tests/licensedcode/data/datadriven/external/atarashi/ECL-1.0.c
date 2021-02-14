/*   Copyright (c) 2005 Iowa State University, Glenn Luecke, James Coyle,
  James Hoekstra, Marina Kraeva, Olga Taborskaia, Andre Wehe, Ying Xu,
  and Ziyu Zhang, All rights reserved.
  Licensed under the Educational Community License version 1.0.
  See the full agreement at http://rted.public.iastate.edu/license.txt . */
/*
*    Test name:		c_J_4_b.c
*
*    Test description:	Access unallocated memory.
*                       Allocate (sizeof(int)+1) bytes of memory, 
*                       then write to ptrA[1]. 
*
*    Error line:        49
*
*    Support files:     index_array.txt, TEST_CONST.H, TEST_PARAM.H
*
*    Env. requirement:  Not needed
*
*    Keywords:		access unallocated memory
*                       write
*                       main
*
*    Last modified:	July 31, 2005
*/

#include "TEST_PARAM.H"

#ifndef EXITCODE_OK
#define EXITCODE_OK 1
#endif

#ifndef EXITCODE_ERROR
#define EXITCODE_ERROR 2
#endif

int main(void)
{
   int *ptrA, varA=0;
   int i;

   ptrA = (int *)malloc(sizeof(int)+1);
   if(!ptrA)
    { 
      printf("Out of memory.\n");
      exit(EXITCODE_ERROR);
    }   

   ptrA[0] = varA + 1;
   ptrA[1] = varA + 2;   /* write to unallocated memory */

   ret();
   if(ret1!=1) printf("Variable ptrA=%d", *ptrA);

   return EXITCODE_OK;
}


