/*
 * GIFtoRI8
 *
 * 
 *
 * Copyright (c) 1988, 1989 by Patrick J. Naughton
 *
 * written by: Patrick J. Naughton
 * modified by Scott Bulmahn for NCSA   March, 1990
 * modified by Peter Webb (NCSA) Summer 1990
 *   - calling interface
 *   - error handling
 *
 * Permission to use, copy, modify, and distribute this software and its
 * documentation for any purpose and without fee is hereby granted,
 * provided that the above copyright notice appear in all copies and that
 * both that copyright notice and this permission notice appear in
 * supporting documentation.
 *
 * This file is provided AS IS with no warranties of any kind.  The author
 * shall have no liability with respect to the infringement of copyrights,
 * trade secrets or any patents by this file or any part thereof.  In no
 * event will the author be liable for any lost revenue or profits or
 * other special, indirect and consequential damages.
 *
 */

#include <stdio.h>

/* Package-wide include files */

#include "reformat.h"
#include "extern.h"
#include "types.h"
#include "error.h"

int            iWIDE,iHIGH,eWIDE,eHIGH,expand,numcols,strip,nostrip;
unsigned long  cols[256];
char          *cmd;

typedef int boolean;

#define NEXTBYTE (*ptr++)
#define IMAGESEP 0x2c
#define INTERLACEMASK 0x40
#define COLORMAPMASK 0x80

FILE *fp;

static int BitOffset = 0,	/* Bit Offset of next code */
    XC = 0, YC = 0,		/* Output X and Y coords of current pixel */
    Pass = 0,			/* Used by output routine if interlaced pic */
    OutCount = 0,		/* Decompressor output 'stack count' */
    RWidth, RHeight,		/* screen dimensions */
    IWidth, IHeight,		/* image dimensions */
    LeftOfs, TopOfs,		/* image offset */
    BitsPerPixel,		/* Bits per pixel, read from GIF header */
    BytesPerScanline,		/* bytes per scanline in output raster */
    ColorMapSize,		/* number of colors */
    Background,			/* background color */
    CodeSize,			/* Code size, read from GIF header */
    InitCodeSize,		/* Starting code size, used during Clear */
    Code,			/* Value returned by ReadCode */
    MaxCode,			/* limiting value for current code size */
    ClearCode,			/* GIF clear code */
    EOFCode,			/* GIF end-of-information code */
    CurCode, OldCode, InCode,	/* Decompressor variables */
    FirstFree,			/* First free code, generated per GIF spec */
    FreeCode,			/* Decompressor, next free slot in hash table */
    FinChar,			/* Decompressor variable */
    DataMask,			/* AND mask for data size */
  ReadMask;                     /* Code AND mask for current code size */

#define False 0
#define True 1



boolean Interlace, HasColormap;


byte *Image;			/* The result array */
byte *RawGIF;			/* The heap array to hold it, raw */
byte *Raster;			/* The raster data stream, unblocked */

/* The hash table used by the decompressor */

int Prefix[4096];
int Suffix[4096];

/* An output array used by the decompressor */

int OutCode[1025];

/* The color map, read from the GIF header */

byte Red[256], Green[256], Blue[256], used[256];
int  numused;

char *id = "GIF87a";

/* Main routine.  Convert a GIF image to an HDF image */

ErrorCode GIFToRI8(fname, file_info)
     char *fname;
     FileInfo *file_info;
{
    int filesize;
    register byte  ch, ch1;
    register byte *ptr, *ptr1;
    register int   i, offset;
    register int loop1;
    
/* Check parameters */

    if (fname == NULL || file_info == NULL)
      return(err_msg(GIF2RI8, NullPtr));

/* Open the GIF file */

    if (strcmp(fname,"-")==0)
      {
	fp = stdin;
	fname = "<stdin>";
      }
    else fp = fopen(fname,"r");
    if (!fp) return(err_msg(GIF2RI8, InputOpenFailed));

/* find the size of the file */

    fseek(fp, 0L, 2);
    filesize = ftell(fp);
    fseek(fp, 0L, 0);

/* Allocate space for various data structures.  Check file for consistiency. */

    if (!(ptr = RawGIF = (byte *) malloc(filesize)))
      return(err_msg(GIF2RI8, NoMemory));

    if (!(Raster = (byte *) malloc(filesize)))
      return(err_msg(GIF2RI8, NoMemory));

    if (fread(ptr, filesize, 1, fp) != 1)
      return(err_msg(GIF2RI8, CorruptedInputFile));

    if (strncmp((char *)ptr, id, 6))
      return(err_msg(GIF2RI8, BadFileData));

    ptr += 6;

/* Get variables from the GIF screen descriptor */

    ch = NEXTBYTE;
    RWidth = ch + 0x100 * NEXTBYTE;	/* screen dimensions... not used. */
    ch = NEXTBYTE;
    RHeight = ch + 0x100 * NEXTBYTE;

    ch = NEXTBYTE;
    HasColormap = ((ch & COLORMAPMASK) ? True : False);

    BitsPerPixel = (ch & 7) + 1;
    numcols = ColorMapSize = 1 << BitsPerPixel;
    DataMask = ColorMapSize - 1;

    Background = NEXTBYTE;		/* background color... not used. */

    if (NEXTBYTE)		/* supposed to be NULL */
      return(err_msg(GIF2RI8, CorruptedInputFile));

/* Read in global colormap. */

    if (HasColormap)
      {
	offset = (MAX_PAL/3) - ColorMapSize;
	for (i = 0; i < ColorMapSize; i++)
	  {
	    Red[i + offset] = NEXTBYTE;
	    Green[i + offset] = NEXTBYTE;
	    Blue[i + offset] = NEXTBYTE;
            used[i + offset] = 0;
	  }
        numused = 0;

/* Fill in the rest of the palette with a smooth gray scale.  Just for fun */

	if (ColorMapSize < 256)
	  for (i=offset-1; i>=0; i--)
	    Red[i] = Green[i] = Blue[i] = 256 - i;
      }

    else /* no colormap in GIF file, so make one up, a nice grayscale. */
      { 
        if (!numcols) numcols=256;
        for (i=0; i<numcols; i++)
	  Red[i] = Green[i] = Blue[i] = cols[i] = (unsigned long) i;
      }

/* Check for image seperator */

    if (NEXTBYTE != IMAGESEP)
      return(err_msg(GIF2RI8, CorruptedInputFile));

/* Now read in values from the image descriptor */

    ch = NEXTBYTE;
    LeftOfs = ch + 0x100 * NEXTBYTE;
    ch = NEXTBYTE;
    TopOfs = ch + 0x100 * NEXTBYTE;
    ch = NEXTBYTE;
    IWidth = ch + 0x100 * NEXTBYTE;
    ch = NEXTBYTE;
    IHeight = ch + 0x100 * NEXTBYTE;
    Interlace = ((NEXTBYTE & INTERLACEMASK) ? True : False);

/* Note that I ignore the possible existence of a local color map.
 * I'm told there aren't many files around that use them, and the spec
 * says it's defined for future use.  This could lead to an error
 * reading some files. 
 */

/* Start reading the raster data. First we get the intial code size
 * and compute decompressor constant values, based on this code size.
 */

    CodeSize = NEXTBYTE;
    ClearCode = (1 << CodeSize);
    EOFCode = ClearCode + 1;
    FreeCode = FirstFree = ClearCode + 2;

/* The GIF spec has it that the code size is the code size used to
 * compute the above values is the code size given in the file, but the
 * code size used in compression/decompression is the code size given in
 * the file plus one. (thus the ++).
 */

    CodeSize++;
    InitCodeSize = CodeSize;
    MaxCode = (1 << CodeSize);
    ReadMask = MaxCode - 1;

/* Read the raster data.  Here we just transpose it from the GIF array
 * to the Raster array, turning it from a series of blocks into one long
 * data stream, which makes life much easier for ReadCode().
 */

    ptr1 = Raster;
    do {
	ch = ch1 = NEXTBYTE;
	while (ch--) *ptr1++ = NEXTBYTE;
	if ((ptr - Raster) > filesize)
	  return(err_msg(GIF2RI8, CorruptedInputFile));
      } while(ch1);
    
    free(RawGIF);		/* We're done with the raw data now... */

/* Allocate the Image */

    Image = (byte *)malloc(IWidth*IHeight);

    BytesPerScanline = IWidth;

/* Decompress the file, continuing until you see the GIF EOF code.
 * One obvious enhancement is to add checking for corrupt files here.
 */

    Code = ReadCode();
    while (Code != EOFCode) {

/* Clear code sets everything back to its initial value, then reads the
 * immediately subsequent code as uncompressed data.
 */

      if (Code == ClearCode) {
	    CodeSize = InitCodeSize;
	    MaxCode = (1 << CodeSize);
	    ReadMask = MaxCode - 1;
	    FreeCode = FirstFree;
	    CurCode = OldCode = Code = ReadCode();
	    FinChar = CurCode & DataMask;
	    AddToPixel(FinChar);
	}
	else {

/* If not a clear code, then must be data: save same as CurCode and InCode */

	  CurCode = InCode = Code;

/* If greater or equal to FreeCode, not in the hash table yet;
 * repeat the last character decoded
 */

	    if (CurCode >= FreeCode) {
		CurCode = OldCode;
		OutCode[OutCount++] = FinChar;
	    }

/* Unless this code is raw data, pursue the chain pointed to by CurCode
 * through the hash table to its end; each code in the chain puts its
 * associated output code on the output queue.
 */

	    while (CurCode > DataMask) {
		if (OutCount > 1024) {
		  return(err_msg(GIF2RI8, CorruptedInputFile));
                    }
		OutCode[OutCount++] = Suffix[CurCode];
		CurCode = Prefix[CurCode];
	     }

/* The last code in the chain is treated as raw data. */

	    FinChar = CurCode & DataMask;
	    OutCode[OutCount++] = FinChar;

/* Now we put the data out to the Output routine.
 * It's been stacked LIFO, so deal with it that way...
 */

	    for (i = OutCount - 1; i >= 0; i--)
		AddToPixel(OutCode[i]);
	    OutCount = 0;

/* Build the hash table on-the-fly. No table is stored in the file. */

	    Prefix[FreeCode] = OldCode;
	    Suffix[FreeCode] = FinChar;
	    OldCode = InCode;

/* Point to the next slot in the table.  If we exceed the current
 * MaxCode value, increment the code size unless it's already 12.  If it
 * is, do nothing: the next code decompressed better be CLEAR
 */

	    FreeCode++;
	    if (FreeCode >= MaxCode) {
		if (CodeSize < 12) {
		    CodeSize++;
		    MaxCode *= 2;
		    ReadMask = (1 << CodeSize) - 1;
		}
	    }
	}
	Code = ReadCode();
    }

    free(Raster);

    if (fp != stdin)
      fclose(fp);
    
/* Put the color map into an HDF palette.  Use the values near the top of the
 * palette first, to avoid conflict with X servers, which usually use the lower
 * values first.
 */

    for (i = 0 ; i < (MAX_PAL/3); i++)
      {
	file_info->palette [i*3] = Red[i];
	file_info->palette [i*3+1] = Green[i];
	file_info->palette [i*3+2] = Blue[i];
      }

/* Conversion done, fill in return values. */
    
    for(loop1=0;loop1<(IHeight*IWidth);loop1++)
      *(Image + loop1) += offset;

    file_info->width = (long)IWidth;
    file_info->height = (long)IHeight;
    file_info->image = (unsigned char *)Image;
    file_info->values |= (BitMask)(CvtImage | CvtPalette);
    return (AllOk);
  }
 
/* Fetch the next code from the raster data stream.  The codes can be
 * any length from 3 to 12 bits, packed into 8-bit bytes, so we have to
 * maintain our location in the Raster array as a BIT Offset.  We compute
 * the byte Offset into the raster array by dividing this by 8, pick up
 * three bytes, compute the bit Offset into our 24-bit chunk, shift to
 * bring the desired code to the bottom, then mask it off and return it. 
 */
ReadCode()
{
int RawCode, ByteOffset;

    ByteOffset = BitOffset / 8;
    RawCode = Raster[ByteOffset] + (0x100 * Raster[ByteOffset + 1]);
    if (CodeSize >= 8)
	RawCode += (0x10000 * Raster[ByteOffset + 2]);
    RawCode >>= (BitOffset % 8);
    BitOffset += CodeSize;
    return(RawCode & ReadMask);
}


AddToPixel(Index)
byte Index;
{
    if (YC<IHeight)
        *(Image + YC * BytesPerScanline + XC) = Index;

    if (!used[Index]) { used[Index]=1;  numused++; }

/* Update the X-coordinate, and if it overflows, update the Y-coordinate */
    if (++XC == IWidth) {

/* If a non-interlaced picture, just increment YC to the next scan line. 
 * If it's interlaced, deal with the interlace as described in the GIF
 * spec.  Put the decoded scan line out to the screen if we haven't gone
 * past the bottom of it.
 */

	XC = 0;
	if (!Interlace) YC++;
	else {
	    switch (Pass) {
		case 0:
		    YC += 8;
		    if (YC >= IHeight) {
			Pass++;
			YC = 4;
		    }
		break;
		case 1:
		    YC += 8;
		    if (YC >= IHeight) {
			Pass++;
			YC = 2;
		    }
		break;
		   
		case 2:
		    YC += 4;
		    if (YC >= IHeight) {
			Pass++;
			YC = 1;
		    }
		break;
		case 3:
		    YC += 2;
		break;
		default:
		break;
	    }
	}
    }
}




