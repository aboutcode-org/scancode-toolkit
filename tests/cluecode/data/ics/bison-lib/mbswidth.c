/* Determine the number of screen columns needed for a string.
   Copyright (C) 2000-2005 Free Software Foundation, Inc.

   This program is free software; you can redistribute it and/or modify

/* Get ISPRINT.  */
#if defined (STDC_HEADERS) || (!defined (isascii) && !defined (HAVE_ISASCII))
# define IN_CTYPE_DOMAIN(c) 1
#else
# define IN_CTYPE_DOMAIN(c) isascii(c)
#endif
/* Undefine to protect against the definition in wctype.h of Solaris 2.6.   */
#undef ISPRINT
#define ISPRINT(c) (IN_CTYPE_DOMAIN (c) && isprint (c))
#undef ISCNTRL
#define ISCNTRL(c) (IN_CTYPE_DOMAIN (c) && iscntrl (c))

/* Returns the number of columns needed to represent the multibyte
    {
      unsigned char c = (unsigned char) *p++;

      if (ISPRINT (c))
	width++;
      else if (!(flags & MBSW_REJECT_UNPRINTABLE))
	width += (ISCNTRL (c) ? 0 : 1);
      else
	return -1;