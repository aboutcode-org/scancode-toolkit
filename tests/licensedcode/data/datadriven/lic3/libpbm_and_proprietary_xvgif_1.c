/*
 * xvgif.c  -  GIF loading code for 'xv'.  Based strongly on...
 *
 * gif2ras.c - Converts from a Compuserve GIF (tm) image to a Sun Raster image.
 *
 * Copyright (c) 1988, 1989 by Patrick J. Naughton
 *
 * Author: Patrick J. Naughton
 * naughton@wind.sun.com
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

/*
 * Copyright 1989, 1990, 1991, 1992 by John Bradley and
 *                       The University of Pennsylvania
 *
 * Permission to use, copy, and distribute for non-commercial purposes,
 * is hereby granted without fee, providing that the above copyright
 * notice appear in all copies and that both the copyright notice and this
 * permission notice appear in supporting documentation.
 *
 * The software may be modified for your own purposes, but modified versions
 * may not be distributed.
 *
 * This software is provided "as is" without any expressed or implied warranty.
 *
 * The author may be contacted via:
 *    US Mail:   John Bradley
 *               GRASP Lab, Room 301C
 *               3401 Walnut St.
 *               Philadelphia, PA  19104
 *
 *    Phone:     (215) 898-8813
 *    EMail:     bradley@cis.upenn.edu
 */

#include "xv.h"

typedef int boolean;

#define NEXTBYTE (*ptr++)
#define EXTENSION     0x21
#define IMAGESEP      0x2c
#define TRAILER       0x3b
#define INTERLACEMASK 0x40
#define COLORMAPMASK  0x80

  

FILE *fp;

int BitOffset = 0,		/* Bit Offset of next code */
    XC = 0, YC = 0,		/* Output X and Y coords of current pixel */
    Pass = 0,			/* Used by output routine if interlaced pic */
    OutCount = 0,		/* Decompressor output 'stack count' */
    RWidth, RHeight,		/* screen dimensions */
    Width, Height,		/* image dimensions */
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
    FreeCode,			/* Decompressor,next free slot in hash table */
    FinChar,			/* Decompressor variable */
    BitMask,			/* AND mask for data size */
    ReadMask,			/* Code AND mask for current code size */
    Misc;                       /* miscellaneous bits (interlace, local cmap)*/


boolean Interlace, HasColormap;

byte *RawGIF;			/* The heap array to hold it, raw */
byte *Raster;			/* The raster data stream, unblocked */

    /* The hash table used by the decompressor */
int Prefix[4096];
int Suffix[4096];

    /* An output array used by the decompressor */
int OutCode[4097];

int   gif89 = 0;
char *id87 = "GIF87a";
char *id89 = "GIF89a";

static int EGApalette[16][3] = {
  {0,0,0},       {0,0,128},     {0,128,0},     {0,128,128}, 
  {128,0,0},     {128,0,128},   {128,128,0},   {200,200,200},
  {100,100,100}, {100,100,255}, {100,255,100}, {100,255,255},
  {255,100,100}, {255,100,255}, {255,255,100}, {255,255,255} };
  

static int  ReadCode();
static void DoInterlace();
static int  GifError();

int filesize;

/*****************************/
int LoadGIF(fname,nc)
  char *fname;
  int   nc;
/*****************************/
{
  register byte  ch, ch1;
  register byte *ptr, *ptr1, *picptr;
  register int   i, block;
  int            npixels, maxpixels, aspect;

#ifdef VMS
  int status, gif_fget_counted(), ii;
  char vms_name[256];
  typedef struct {
    unsigned char *pos, *start, *end;	/* file positions */
    int chan, size;
  } map_block;
  map_block *gif_fopen(), *map;	/* routine to map file to memory */
#endif

  /* initialize variables */
  BitOffset = XC = YC = Pass = OutCount = npixels = maxpixels = 0;
  RawGIF = Raster = pic = NULL;
  gif89 = 0;

  fp = fopen(fname,"r");
  if (!fp) {
    fprintf(stderr,"%s: LoadGIF() - unable to open file '%s'\n",cmd,fname);
    return 1;
  }
  
#ifdef VMS
  (void) fgetname ( fp, vms_name, 1 );
  map = gif_fopen ( vms_name  );
  filesize = map->size;
  if ( filesize == -1 ) return ( GifError ( "Can't map file to memory") );
  gif_fgetc();	/* get first segment */
  ptr = RawGIF = map->start;
#else

  /* find the size of the file */
  fseek(fp, 0L, 2);
  filesize = ftell(fp);
  fseek(fp, 0L, 0);
  
  /* the +256's are so we can read truncated GIF files without fear of 
     segmentation violation */
  if (!(ptr = RawGIF = (byte *) calloc(filesize+256,1)))
    return( GifError("not enough memory to read gif file") );
  
  if (!(Raster = (byte *) calloc(filesize+256,1)))    
    return( GifError("not enough memory to read gif file") );
  
  if (fread(ptr, filesize, 1, fp) != 1) 
    return( GifError("GIF data read failed") );
#endif /* !VMS */
  
  if      (strncmp((char *) ptr, id87, 6)==0) gif89 = 0;
  else if (strncmp((char *) ptr, id89, 6)==0) gif89 = 1;
  else    return( GifError("not a GIF file"));
  
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
  BitMask = ColorMapSize - 1;
  
  Background = NEXTBYTE;		/* background color... not used. */
  
  aspect = NEXTBYTE;
  if (aspect) {
    if (!gif89) return(GifError("corrupt GIF file (screen descriptor)"));
    else normaspect = (float) (aspect + 15) / 64.0;   /* gif89 aspect ratio */
    if (DEBUG) fprintf(stderr,"GIF89 aspect = %f\n", normaspect);
  }
  
  
  /* Read in global colormap. */
  
  if (HasColormap)
    for (i=0; i<ColorMapSize; i++) {
      r[i] = NEXTBYTE;
      g[i] = NEXTBYTE;
      b[i] = NEXTBYTE;
    }
  else {  /* no colormap in GIF file */
    /* put std EGA palette (repeated 16 times) into colormap, for lack of
       anything better to do */

    for (i=0; i<256; i++) {
      r[i] = EGApalette[i&15][0];
      g[i] = EGApalette[i&15][1];
      b[i] = EGApalette[i&15][2];
    }
  }

  /* possible things at this point are:
   *   an application extension block
   *   a comment extension block
   *   an (optional) graphic control extension block
   *       followed by either an image
   *	   or a plaintext extension
   */

  while (1) {
    block = NEXTBYTE;

    if (block == EXTENSION) {  /* parse extension blocks */
      int i, fn, blocksize, aspnum, aspden;

      /* read extension block */
      fn = NEXTBYTE;

      if (DEBUG) fprintf(stderr,"GIF extension type 0x%02x\n", fn);

      if (fn == 'R') {                  /* GIF87 aspect extension */
	blocksize = NEXTBYTE;
	if (blocksize == 2) {
	  aspnum = NEXTBYTE;
	  aspden = NEXTBYTE;
	  if (aspden>0 && aspnum>0) 
	    normaspect = (float) aspnum / (float) aspden;
	  else { normaspect = 1.0;  aspnum = aspden = 1; }

	  if (DEBUG) fprintf(stderr,"GIF87 aspect extension: %d:%d = %f\n\n", 
			     aspnum, aspden,normaspect);
	}
	else {
	  for (i=0; i<blocksize; i++) NEXTBYTE;
	}
      }

      else if (fn == 0xFE) {  /* Comment Extension.  just eat it */
	int ch, j, sbsize;
	
	if (DEBUG) fprintf(stderr,"Comment extension:  ");
	/* read (and ignore) data sub-blocks */
	do {
	  j = 0;  sbsize = NEXTBYTE;
	  while (j<sbsize) {
	    ch = NEXTBYTE;  j++;
	    if (DEBUG) fprintf(stderr,"%c", ch);
	  }
	} while (sbsize);
	if (DEBUG) fprintf(stderr,"\n\n");
      }

      else if (fn == 0x01) {  /* PlainText Extension */
	int j,sbsize,ch;
	int tgLeft, tgTop, tgWidth, tgHeight, cWidth, cHeight, fg, bg;
      
	SetISTR(ISTR_WARNING, 
		"PlainText extension found in GIF file.  Ignored.");

	sbsize   = NEXTBYTE;
	tgLeft   = NEXTBYTE;  tgLeft   += (NEXTBYTE)<<8;
	tgTop    = NEXTBYTE;  tgTop    += (NEXTBYTE)<<8;
	tgWidth  = NEXTBYTE;  tgWidth  += (NEXTBYTE)<<8;
	tgHeight = NEXTBYTE;  tgHeight += (NEXTBYTE)<<8;
	cWidth   = NEXTBYTE;
	cHeight  = NEXTBYTE;
	fg       = NEXTBYTE;
	bg       = NEXTBYTE;
	i=12;
	for ( ; i<sbsize; i++) NEXTBYTE;   /* read rest of first subblock */
      
	if (DEBUG) fprintf(stderr,
	   "PlainText: tgrid=%d,%d %dx%d  cell=%dx%d  col=%d,%d\n",
	   tgLeft, tgTop, tgWidth, tgHeight, cWidth, cHeight, fg, bg);
	
	/* read (and ignore) data sub-blocks */
	do {
	  j = 0;
	  sbsize = NEXTBYTE;
	  while (j<sbsize) {
	    ch = NEXTBYTE;  j++;
	    if (DEBUG) fprintf(stderr,"%c", ch);
	  }
	} while (sbsize);
	if (DEBUG) fprintf(stderr,"\n\n");
      }


      else if (fn == 0xF9) {  /* Graphic Control Extension */
	int j, sbsize;

	if (DEBUG) fprintf(stderr,"Graphic Control extension\n\n");

	SetISTR(ISTR_WARNING, 
		"Graphic Control Extension in GIF file.  Ignored.");
	
	/* read (and ignore) data sub-blocks */
	do {
	  j = 0; sbsize = NEXTBYTE;
	  while (j<sbsize) { NEXTBYTE;  j++; }
	} while (sbsize);
      }
      

      else { /* unknown extension */
	int j, sbsize;

	if (DEBUG) fprintf(stderr,"unknown GIF extension 0x%02x\n\n", fn);

	SetISTR(ISTR_WARNING, 
		"Unknown extension 0x%02x in GIF file.  Ignored.",fn);
	
	/* read (and ignore) data sub-blocks */
	do {
	  j = 0; sbsize = NEXTBYTE;
	  while (j<sbsize) { NEXTBYTE;  j++; }
	} while (sbsize);
      }
    }
    
    else if (block == IMAGESEP) break;   /* read an image */

    else if (block == TRAILER) {
      return( GifError("no image data found in GIF file") );
    }

    else return (GifError("Unknown block type found in file."));
  }


  /* read in values from the image descriptor */
  
  ch = NEXTBYTE;
  LeftOfs = ch + 0x100 * NEXTBYTE;
  ch = NEXTBYTE;
  TopOfs = ch + 0x100 * NEXTBYTE;
  ch = NEXTBYTE;
  Width = ch + 0x100 * NEXTBYTE;
  ch = NEXTBYTE;
  Height = ch + 0x100 * NEXTBYTE;

  Misc = NEXTBYTE;
  Interlace = ((Misc & INTERLACEMASK) ? True : False);

  if (Misc & 0x80) {
    for (i=0; i< 1 << ((Misc&7)+1); i++) {
      r[i] = NEXTBYTE;
      g[i] = NEXTBYTE;
      b[i] = NEXTBYTE;
    }
  }


  if (!HasColormap && !(Misc&0x80)) {
    /* no global or local colormap */
    SetISTR(ISTR_WARNING,
	    "No colormap in this GIF file.  Assuming EGA colors.");
  }
    

  
  /* Start reading the raster data. First we get the intial code size
   * and compute decompressor constant values, based on this code size.
   */
  
  SetISTR(ISTR_FORMAT, "GIF%s, %d bits per pixel, %sinterlaced.  (%d bytes)",
 	  (gif89) ? "89" : "87", BitsPerPixel, 
 	  Interlace ? "" : "non-", filesize);

  CodeSize = NEXTBYTE;

#ifdef VMS
  GIF_DECOMPRESS_INIT( &CodeSize );
  map->pos = ptr;

  /* Allocate the 'pic' */
  pWIDE = Width;  pHIGH = Height;
  maxpixels = Width*Height;

  picptr = pic = (byte *) malloc(maxpixels);
  if (!pic) 
    return( GifError("not enough memory for 'pic'") );
  if ( !Interlace )
    status = GIF_DECOMPRESS ( gif_fget_counted, map, maxpixels, picptr );
  else {
    /* decompress a line at a time into the proper position. */
    int pass, step, i, y;
    step = 8;
    y = pass = 0;
    for ( i = 0; i < Height; i++ ) {
      status = GIF_DECOMPRESS(gif_fget_counted, map, Width, &picptr[y*Width]);
      if ( (status&1) != 1 ) break;
      
      y += step;
      if ( y >= Height ) {
	/* Stepsize/start-Y progression: 8/0, 8/4, 4/2, 2/1  */
	if ( pass > 0 ) step = step/2;
	y =  step/2;
	pass++;
      }
    }
  }
  
  gif_fclose();
  if ( (status&1) == 0 ) {
    char msg[256];
    SetISTR(ISTR_WARNING,
	    "Error decompressing data.  Winging it.");
    sprintf ( msg, "Error decompressing data, code %d, start: %x, pos: %x",
	     status, map->start, map->pos );
    return( GifError(msg) );
  }

#else  /* !VMS */
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
  


  /* UNBLOCK:
   * Read the raster data.  Here we just transpose it from the GIF array
   * to the Raster array, turning it from a series of blocks into one long
   * data stream, which makes life much easier for ReadCode().
   */
  
  ptr1 = Raster;
  do {
    ch = ch1 = NEXTBYTE;
    while (ch--) { *ptr1 = NEXTBYTE; ptr1++; }
    if ((ptr - RawGIF) > filesize) {
      SetISTR(ISTR_WARNING,
	      "This GIF file seems to be truncated.  Winging it.");
      break;
    }
  } while(ch1);
  free(RawGIF);	 RawGIF = NULL; 	/* We're done with the raw data now */



  if (DEBUG) {
    fprintf(stderr,"xv: LoadGIF() - picture is %dx%d, %d bits, %sinterlaced\n",
	    Width, Height, BitsPerPixel, Interlace ? "" : "non-");
  }
  

  /* Allocate the 'pic' */
  pWIDE = Width;  pHIGH = Height;
  maxpixels = Width*Height;
  picptr = pic = (byte *) malloc(maxpixels);
  sprintf(formatStr, "%dx%d GIF%s.", pWIDE, pHIGH, (gif89) ? "89" : "87");

  if (!pic) 
    return( GifError("not enough memory for 'pic'") );

  
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
      Code = ReadCode();
      CurCode = OldCode = Code;
      FinChar = CurCode & BitMask;
      if (!Interlace) *picptr++ = FinChar;
         else DoInterlace(FinChar);
      npixels++;
    }
    else {
      /* If not a clear code, must be data: save same as CurCode and InCode */

      /* if we're at maxcode and didn't get a clear, stop loading */
      if (FreeCode>=4096) { /* printf("freecode blew up\n"); */
			    break; }

      CurCode = InCode = Code;
      
      /* If greater or equal to FreeCode, not in the hash table yet;
       * repeat the last character decoded
       */
      
      if (CurCode >= FreeCode) {
	CurCode = OldCode;
	if (OutCount > 4096) {  /* printf("outcount1 blew up\n"); */ break; }
	OutCode[OutCount++] = FinChar;
      }
      
      /* Unless this code is raw data, pursue the chain pointed to by CurCode
       * through the hash table to its end; each code in the chain puts its
       * associated output code on the output queue.
       */
      
      while (CurCode > BitMask) {
	if (OutCount > 4096) break;   /* corrupt file */
	OutCode[OutCount++] = Suffix[CurCode];
	CurCode = Prefix[CurCode];
      }
      
      if (OutCount > 4096) { /* printf("outcount blew up\n"); */ break; }
      
      /* The last code in the chain is treated as raw data. */
      
      FinChar = CurCode & BitMask;
      OutCode[OutCount++] = FinChar;
      
      /* Now we put the data out to the Output routine.
       * It's been stacked LIFO, so deal with it that way...
       */

      /* safety thing:  prevent exceeding range of 'pic' */
      if (npixels + OutCount > maxpixels) OutCount = maxpixels-npixels;
	
      npixels += OutCount;
      if (!Interlace) for (i=OutCount-1; i>=0; i--) *picptr++ = OutCode[i];
                else  for (i=OutCount-1; i>=0; i--) DoInterlace(OutCode[i]);
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
    if (npixels >= maxpixels) break;
  }
  free(Raster);  Raster = NULL;
  
  if (npixels != maxpixels) {
    SetISTR(ISTR_WARNING,"This GIF file seems to be truncated.  Winging it.");
    if (!Interlace)
      memset(pic+npixels, 0, maxpixels-npixels);  /* clear to EOBuffer */
  }

#endif  /* !VMS */

  if (fp != stdin) fclose(fp);

  SetDirRButt(F_FORMAT, F_GIF);
  SetDirRButt(F_COLORS, F_FULLCOLOR);

  return 0;
}


/* Fetch the next code from the raster data stream.  The codes can be
 * any length from 3 to 12 bits, packed into 8-bit bytes, so we have to
 * maintain our location in the Raster array as a BIT Offset.  We compute
 * the byte Offset into the raster array by dividing this by 8, pick up
 * three bytes, compute the bit Offset into our 24-bit chunk, shift to
 * bring the desired code to the bottom, then mask it off and return it. 
 */

static int ReadCode()
{
  int RawCode, ByteOffset;
  
  ByteOffset = BitOffset / 8;
  RawCode = Raster[ByteOffset] + (Raster[ByteOffset + 1] << 8);
  if (CodeSize >= 8)
    RawCode += ( ((int) Raster[ByteOffset + 2]) << 16);
  RawCode >>= (BitOffset % 8);
  BitOffset += CodeSize;

  return(RawCode & ReadMask);
}


/***************************/
static void DoInterlace(Index)
     byte Index;
{
  static byte *ptr = NULL;
  static int   oldYC = -1;
  
  if (oldYC != YC) {  ptr = pic + YC * Width;  oldYC = YC; }
  
  if (YC<Height)
    *ptr++ = Index;
  
  /* Update the X-coordinate, and if it overflows, update the Y-coordinate */
  
  if (++XC == Width) {
    
    /* deal with the interlace as described in the GIF
     * spec.  Put the decoded scan line out to the screen if we haven't gone
     * past the bottom of it
     */
    
    XC = 0;
    
    switch (Pass) {
    case 0:
      YC += 8;
      if (YC >= Height) { Pass++; YC = 4; }
      break;
      
    case 1:
      YC += 8;
      if (YC >= Height) { Pass++; YC = 2; }
      break;
      
    case 2:
      YC += 4;
      if (YC >= Height) { Pass++; YC = 1; }
      break;
      
    case 3:
      YC += 2;  break;
      
    default:
      break;
    }
  }
}


      
/*****************************/
static int GifError(st)
     char *st;
{
  fprintf(stderr,"%s: LoadGIF() - %s\n",cmd,st);

#ifndef VMS  
  if (RawGIF != NULL) free(RawGIF);
  if (Raster != NULL) free(Raster);
#endif

  if (pic    != NULL) free(pic);
  
  return -1;
}

