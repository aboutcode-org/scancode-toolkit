/* Convert string representation of a number into an integer value.

   Copyright (C) 1991, 1992, 1994, 1995, 1996, 1997, 1998, 1999, 2003, 2005
   Free Software Foundation, Inc.

# endif
#else
# if defined STDC_HEADERS || (!defined isascii && !defined HAVE_ISASCII)
#  define IN_CTYPE_DOMAIN(c) 1
# else
#  define IN_CTYPE_DOMAIN(c) isascii(c)
# endif
# define L_(Ch) Ch
      for (c = *end; c != L_('\0'); c = *++end)
	if ((wchar_t) c != thousands
	    && ((wchar_t) c < L_('0') || (wchar_t) c > L_('9'))
	    && (!ISALPHA (c) || (int) (TOUPPER (c) - L_('A') + 10) >= base))
	  break;
      if (*s == thousands)
	break;
      if (c >= L_('0') && c <= L_('9'))
	c -= L_('0');
      else if (ISALPHA (c))
	c = TOUPPER (c) - L_('A') + 10;
      else
	break;