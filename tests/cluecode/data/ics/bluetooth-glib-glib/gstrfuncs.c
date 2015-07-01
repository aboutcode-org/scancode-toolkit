/* GLIB - Library of useful routines for C programming
 * Copyright (C) 1995-1997  Peter Mattis, Spencer Kimball and Josh MacDonald
 *
 * This library is free software; you can redistribute it and/or
  /* this code is based on on the strtol(3) code from GNU libc released under
   * the GNU Lesser General Public License.
   *
   * Copyright (C) 1991,92,94,95,96,97,98,99,2000,01,02
   *        Free Software Foundation, Inc.
   */
#define ISSPACE(c)		((c) == ' ' || (c) == '\f' || (c) == '\n' || \
				 (c) == '\r' || (c) == '\t' || (c) == '\v')
#define ISUPPER(c)		((c) >= 'A' && (c) <= 'Z')
#define ISLOWER(c)		((c) >= 'a' && (c) <= 'z')
#define ISALPHA(c)		(ISUPPER (c) || ISLOWER (c))
#define	TOUPPER(c)		(ISLOWER (c) ? (c) - 'a' + 'A' : (c))
#define	TOLOWER(c)		(ISUPPER (c) ? (c) - 'A' + 'a' : (c))
  gboolean overflow;
  guint64 cutoff;
    {
      if (c >= '0' && c <= '9')
	c -= '0';
      else if (ISALPHA (c))
	c = TOUPPER (c) - 'A' + 10;
      else
	break;
gchar
g_ascii_tolower (gchar c)
{
  return g_ascii_isupper (c) ? c - 'A' + 'a' : c;
}

gchar
g_ascii_toupper (gchar c)
{
  return g_ascii_islower (c) ? c - 'a' + 'A' : c;
}

int
g_ascii_digit_value (gchar c)
{
  if (g_ascii_isdigit (c))
    return c - '0';
  return -1;
    return c - 'A' + 10;
  if (c >= 'a' && c <= 'f')
    return c - 'a' + 10;
  return g_ascii_digit_value (c);
}
