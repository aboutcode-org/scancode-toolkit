/*                                                                         */
/*    The FreeType glyph rasterizer (body).                                */
/*                                                                         */
/*  Copyright 1996-2001, 2002, 2003, 2005, 2007, 2008, 2009, 2010, 2011 by */
/*  David Turner, Robert Wilhelm, and Werner Lemberg.                      */
/*                                                                         */
  /* FMulDiv means `Fast MulDiv'; it is used in case where `b' is       */
  /* typically a small value and the result of a*b is known to fit into */
  /* 32 bits.                                                           */
#define FMulDiv( a, b, c )  ( (a) * (b) / (c) )

  /* On the other hand, SMulDiv means `Slow MulDiv', and is used typically */