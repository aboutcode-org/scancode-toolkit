/*
  Copyright . 2008 Mycom Pany, inc.
  Change: Add functions
  		"local void make_crc_table()",
  		"local void write_table(out, table)",
		"static const unsigned long FAR * ZEXPORT get_crc_table(void)",
		"static unsigned long ZEXPORT crc32( unsigned long crc,
			const unsigned char FAR *buf,unsigned len)",
		"int  DaHua_uncompress( unsigned char *dest, unsigned long *destLen, 
		const unsigned char *source, unsigned char* baseMem)" and so on
*/

/* uncompr.c -- decompress a memory buffer
 * Copyright (C) 1995-2003 Jean-loup Gailly.
 * For conditions of distribution and use, see copyright notice in zlib.h
 */

