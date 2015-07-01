/* trees.c -- output deflated data using Huffman coding
 * Copyright (C) 1995-2005 Jean-loup Gailly
 * For conditions of distribution and use, see copyright notice in zlib.h
 */


#else /* DEBUG */
#  define send_code(s, c, tree) \
     { if (z_verbose>2) fprintf(stderr,"\ncd %3d ",(c)); \
       send_bits(s, tree[c].Code, tree[c].Len); }
#endif