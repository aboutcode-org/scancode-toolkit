/* pngrtran.c - transforms the data in a row for PNG readers
 *
 * Last changed in libpng 1.2.19 August 18, 2007
 * For conditions of distribution and use, see copyright notice in png.h
 * Copyright (c) 1998-2007 Glenn Randers-Pehrson
 * (Version 0.96 Copyright (c) 1996, 1997 Andreas Dilger)
 * (Version 0.88 Copyright (c) 1995, 1996 Guy Eric Schalnat, Group 42, Inc.)
 *
 * This file contains functions optionally called by an application
/* reduce RGB files to grayscale, with or without alpha
 * using the equation given in Poynton's ColorFAQ at
 * <http://www.inforamp.net/~poynton/>
 * Copyright (c) 1998-01-04 Charles Poynton poynton at inforamp.net
 *
 *     Y = 0.212671 * R + 0.715160 * G + 0.072169 * B