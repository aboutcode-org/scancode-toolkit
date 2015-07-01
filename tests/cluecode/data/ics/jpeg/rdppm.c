/*
 * rdppm.c
 *
 * Copyright (C) 1991-1997, Thomas G. Lane.
 * This file is part of the Independent JPEG Group's software.
 * For conditions of distribution and use, see the accompanying README file.

/* Portions of this code are based on the PBMPLUS library, which is:
**
** Copyright (C) 1988 by Jef Poskanzer.
**
** Permission to use, copy, modify, and distribute this software and its
** documentation for any purpose and without fee is hereby granted, provided
** that the above copyright notice appear in all copies and that both that
** copyright notice and this permission notice appear in supporting
** documentation.  This software is provided "as is" without express or
** implied warranty.
  c = getc(source->pub.input_file); /* subformat discriminator character */

  /* detect unsupported variants (ie, PBM) before trying to read header */
  switch (c) {
  case '2':			/* it's a text-format PGM file */
  case '3':			/* it's a text-format PPM file */
  use_raw_buffer = FALSE;	/* do we map input buffer onto I/O buffer? */
  need_rescale = TRUE;		/* do we need a rescale array? */

  switch (c) {
  case '2':			/* it's a text-format PGM file */
    cinfo->input_components = 1;