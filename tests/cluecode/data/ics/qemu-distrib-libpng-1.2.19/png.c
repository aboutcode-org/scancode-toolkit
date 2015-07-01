/* png.c - location for general purpose libpng functions
 *
 * Last changed in libpng 1.2.19 August 18, 2007
 * For conditions of distribution and use, see copyright notice in png.h
 * Copyright (c) 1998-2007 Glenn Randers-Pehrson
 * (Version 0.96 Copyright (c) 1996, 1997 Andreas Dilger)
 * (Version 0.88 Copyright (c) 1995, 1996 Guy Eric Schalnat, Group 42, Inc.)
 */

#endif /* defined(PNG_READ_SUPPORTED) || defined(PNG_WRITE_SUPPORTED) */

png_charp PNGAPI
png_get_copyright(png_structp png_ptr)
{
   png_ptr = png_ptr;  /* silence compiler warning about unused png_ptr */
   return ((png_charp) "\n libpng version 1.2.19 - August 18, 2007\n\
   Copyright (c) 1998-2007 Glenn Randers-Pehrson\n\
   Copyright (c) 1996-1997 Andreas Dilger\n\
   Copyright (c) 1995-1996 Guy Eric Schalnat, Group 42, Inc.\n");
}
