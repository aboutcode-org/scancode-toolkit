/* inftrees.c -- generate Huffman trees for efficient decoding
 * Copyright (C) 1995-2010 Mark Adler
 * For conditions of distribution and use, see copyright notice in zlib.h
 */


#define MAXBITS 15

const char inflate_copyright[] =
   " inflate 1.2.5 Copyright 1995-2010 Mark Adler ";
/*
  If you use the zlib library in a product, an acknowledgment is welcome
  in the documentation of your product. If for some reason you cannot
  include such an acknowledgment, I would appreciate that you keep this
  copyright string in the executable of your product.
 */
