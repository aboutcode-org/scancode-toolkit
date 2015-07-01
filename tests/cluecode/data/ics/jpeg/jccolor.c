/*
 * jccolor.c
 *
 * Copyright (C) 1991-1996, Thomas G. Lane.
 * This file is part of the Independent JPEG Group's software.
 * For conditions of distribution and use, see the accompanying README file.
#define B2(n)   (((n) >> 16) & 0xFF)
#define B3(n)   ((n) >> 24)

#define PACK(a, b, c, d)    ((a) | ((b) << 8) | ((c) << 16) | ((d) << 24))

static int ptr_is_quad(const void* p)