/*  ftsnames.h                                                             */
/*                                                                         */
/*    Simple interface to access SFNT name tables (which are used          */
/*    to hold font names, copyright info, notices, etc.) (specification).  */
/*                                                                         */
/*    This is _not_ used to retrieve glyph names!                          */
/*                                                                         */
/*  Copyright 1996-2001, 2002, 2003, 2006, 2009, 2010 by                   */
/*  David Turner, Robert Wilhelm, and Werner Lemberg.                      */
/*                                                                         */
  /*    The TrueType and OpenType specifications allow the inclusion of    */
  /*    a special `names table' in font files.  This table contains        */
  /*    textual (and internationalized) information regarding the font,    */
  /*    like family name, copyright, version, etc.                         */
  /*                                                                       */
  /*    The definitions below are used to access them if available.        */