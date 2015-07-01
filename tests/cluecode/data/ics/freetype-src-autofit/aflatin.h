/*                                                                         */
/*    Auto-fitter hinting routines for latin script (specification).       */
/*                                                                         */
/*  Copyright 2003-2007, 2009, 2011 by                                     */
/*  David Turner, Robert Wilhelm, and Werner Lemberg.                      */
/*                                                                         */

  /* constants are given with units_per_em == 2048 in mind */
#define AF_LATIN_CONSTANT( metrics, c )                                      \
  ( ( (c) * (FT_Long)( (AF_LatinMetrics)(metrics) )->units_per_em ) / 2048 )

