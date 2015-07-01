/*                                                                         */
/*    FreeType high-level API and common types (specification only).       */
/*                                                                         */
/*  Copyright 1996-2011 by                                                 */
/*  David Turner, Robert Wilhelm, and Werner Lemberg.                      */
/*                                                                         */
#define FT_ENC_TAG( value, a, b, c, d )         \
          value = ( ( (FT_UInt32)(a) << 24 ) |  \
                    ( (FT_UInt32)(b) << 16 ) |  \
                    ( (FT_UInt32)(c) <<  8 ) |  \
                      (FT_UInt32)(d)         )

  /*    FT_FSTYPE_RESTRICTED_LICENSE_EMBEDDING ::                          */
  /*      Fonts that have only this bit set must not be modified, embedded */
  /*      or exchanged in any manner without first obtaining permission of */
  /*      the font software copyright owner.                               */
  /*                                                                       */
  /*    FT_FSTYPE_PREVIEW_AND_PRINT_EMBEDDING ::                           */