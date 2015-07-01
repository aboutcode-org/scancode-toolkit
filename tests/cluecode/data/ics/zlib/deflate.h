/* deflate.h -- internal compression state
 * Copyright (C) 1995-2010 Jean-loup Gailly
 * For conditions of distribution and use, see copyright notice in zlib.h
 */

/* Output a byte on the stream.
 * IN assertion: there is enough room in pending_buf.
 */
#define put_byte(s, c) {s->pending_buf[s->pending++] = (c);}


#endif

# define _tr_tally_lit(s, c, flush) \
  { uch cc = (c); \
    s->d_buf[s->last_lit] = 0; \
    s->l_buf[s->last_lit++] = cc; \