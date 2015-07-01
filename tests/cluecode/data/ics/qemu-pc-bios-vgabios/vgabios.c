 */
// ============================================================================================
//  
//  Copyright (C) 2001-2008 the LGPL VGABios developers Team
//
//  This library is free software; you can redistribute it and/or
//   - rombios.c of plex86 
//
//  This VGA Bios contains fonts from :
//   - fntcol16.zip (c) by Joseph Gil avalable at :
//      ftp://ftp.simtel.net/pub/simtelnet/msdos/screen/fntcol16.zip
//     These fonts are public domain 
.byte   0x0a,0x0d
.byte	0x00

vgabios_copyright:
.ascii	"(C) 2008 the LGPL VGABios developers Team"
.byte	0x0a,0x0d
.byte	0x00
 mov si,#vgabios_version
 call _display_string
 
 ;;mov si,#vgabios_copyright
 ;;call _display_string
 ;;mov si,#crlf