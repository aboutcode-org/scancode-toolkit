
/* A test program written to test robustness to decompression of
   corrupted data.  Usage is 
       unzcrash filename
   and the program will read the specified file, compress it (in memory),
   and then repeatedly decompress it, each time with a different bit of
   the compressed data inverted, so as to test all possible one-bit errors.
   This should not cause any invalid memory accesses.  If it does, 
   I want to know about it!

   PS.  As you can see from the above description, the process is
   incredibly slow.  A file of size eg 5KB will cause it to run for
   many hours.
*/

/* ------------------------------------------------------------------
   This file is part of bzip2/libbzip2, a program and library for
   lossless, block-sorting data compression.

   bzip2/libbzip2 version 1.0.6 of 6 September 2010
   Copyright (C) 1996-2010 Julian Seward <jseward@bzip.org>

   Please read the WARNING, DISCLAIMER and PATENTS sections in the 
   README file.

   This program is released under the terms of the license contained
   in the file LICENSE.
   ------------------------------------------------------------------ */


#include <stdio.h>
#include <assert.h>
#include "bzlib.h"

#define M_BLOCK 1000000

typedef unsigned char uchar;

#define M_BLOCK_OUT (M_BLOCK + 1000000)
uchar inbuf[M_BLOCK];
uchar outbuf[M_BLOCK_OUT];
uchar zbuf[M_BLOCK + 600 + (M_BLOCK / 100)];

int nIn, nOut, nZ;

