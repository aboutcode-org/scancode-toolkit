// $Id$
/////////////////////////////////////////////////////////////////////////
//
//  Copyright (C) 2002  MandrakeSoft S.A.
//
//    MandrakeSoft S.A.

static char bios_cvs_version_string[] = "$Revision$ $Date$";

#define BIOS_COPYRIGHT_STRING "(c) 2002 MandrakeSoft S.A. Written by Kevin Lawton & the Bochs team."

#if DEBUG_ATA
#endif

  void
wrch(c)
  Bit8u  c;
{
#endif
  if (action & BIOS_PRINTF_SCREEN) {
    if (c == '\n') wrch('\r');
    wrch(c);
  }
}


.org 0xff00
.ascii BIOS_COPYRIGHT_STRING

;------------------------------------------------
.org 0xfa6e ;; Character Font for 320x200 & 640x200 Graphics (lower 128 characters)
ASM_END
/*
 * This font comes from the fntcol16.zip package (c) by  Joseph Gil
 * found at ftp://ftp.simtel.net/pub/simtelnet/msdos/screen/fntcol16.zip
 * This font is public domain