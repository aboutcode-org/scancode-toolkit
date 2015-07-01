/* GLIB - Library of useful routines for C programming
 *
 * gconvert.c: Convert between character sets using iconv
 * Copyright Red Hat Inc., 2000
 * Authors: Havoc Pennington <hp@redhat.com>, Owen Taylor <otaylor@redhat.com>
 *
  for (p = string; *p != '\0'; p++)
    {
      c = (guchar) *p;
      if (!ACCEPTABLE (c)) 
	unacceptable++;
    }
    {
      c = (guchar) *p;
      
      if (!ACCEPTABLE (c))
	{
	  *q++ = '%'; /* means hex coming */
static gboolean
is_asciialphanum (gunichar c)
{
  return c <= 0x7F && g_ascii_isalnum (c);
}

static gboolean
is_asciialpha (gunichar c)
{
  return c <= 0x7F && g_ascii_isalpha (c);
}

      /* read in a label */
      c = g_utf8_get_char (p);
      p = g_utf8_next_char (p);
      if (!is_asciialphanum (c))
	return FALSE;
      first_char = c;
	  c = g_utf8_get_char (p);
	  p = g_utf8_next_char (p);
	}
      while (is_asciialphanum (c) || c == '-');
      if (last_char == '-')
	return FALSE;