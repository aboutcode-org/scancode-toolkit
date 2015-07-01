/* quotearg.c - quote arguments for output

   Copyright (C) 1998, 1999, 2000, 2001, 2002, 2004, 2005, 2006 Free
   Software Foundation, Inc.

  bool backslash_escapes = false;
  bool unibyte_locale = MB_CUR_MAX == 1;

#define STORE(c) \
    do \
      { \
	if (len < buffersize) \
	  buffer[len] = (c); \
	len++; \
      } \
	STORE ('\\');

      c = arg[i];
      switch (c)
	{
	case '\0':
	    if (unibyte_locale)
	      {
		m = 1;
		printable = isprint (c) != 0;
	      }
	    else
		      }
		    if (ilim <= i + 1)
		      break;
		    STORE (c);
		    c = arg[++i];
		  }
      STORE ('\\');

    store_c:
      STORE (c);
    }
