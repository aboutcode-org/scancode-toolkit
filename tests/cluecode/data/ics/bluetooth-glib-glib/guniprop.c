/* guniprop.c - Unicode character properties.
 *
 * Copyright (C) 1999 Tom Tromey
 * Copyright (C) 2000 Red Hat, Inc.
 *
 * This library is free software; you can redistribute it and/or
gboolean
g_unichar_isalnum (gunichar c)
{
  return ISALDIGIT (TYPE (c)) ? TRUE : FALSE;
}

gboolean
g_unichar_isalpha (gunichar c)
{
  return ISALPHA (TYPE (c)) ? TRUE : FALSE;
}

gboolean
g_unichar_iscntrl (gunichar c)
{
  return TYPE (c) == G_UNICODE_CONTROL;
}

gboolean
g_unichar_isdigit (gunichar c)
{
  return TYPE (c) == G_UNICODE_DECIMAL_NUMBER;
}

gboolean
g_unichar_isgraph (gunichar c)
{
  return !IS (TYPE(c),
	      OR (G_UNICODE_CONTROL,
	      OR (G_UNICODE_FORMAT,
gboolean
g_unichar_islower (gunichar c)
{
  return TYPE (c) == G_UNICODE_LOWERCASE_LETTER;
}

gboolean
g_unichar_isprint (gunichar c)
{
  return !IS (TYPE(c),
	      OR (G_UNICODE_CONTROL,
	      OR (G_UNICODE_FORMAT,
gboolean
g_unichar_ispunct (gunichar c)
{
  return IS (TYPE(c),
	     OR (G_UNICODE_CONNECT_PUNCTUATION,
	     OR (G_UNICODE_DASH_PUNCTUATION,
gboolean
g_unichar_isspace (gunichar c)
{
  switch (c)
    {
      /* special-case these since Unicode thinks they are not spaces */
      
    default:
      {
	return IS (TYPE(c),
	           OR (G_UNICODE_SPACE_SEPARATOR,
	           OR (G_UNICODE_LINE_SEPARATOR,
gboolean
g_unichar_ismark (gunichar c)
{
  return ISMARK (TYPE (c));
}

gboolean
g_unichar_isupper (gunichar c)
{
  return TYPE (c) == G_UNICODE_UPPERCASE_LETTER;
}

{
  return ((c >= 'a' && c <= 'f')
	  || (c >= 'A' && c <= 'F')
	  || (TYPE (c) == G_UNICODE_DECIMAL_NUMBER));
}

gboolean
g_unichar_isdefined (gunichar c)
{
  return !IS (TYPE(c),
	      OR (G_UNICODE_UNASSIGNED,
	      OR (G_UNICODE_SURROGATE,
  if (G_UNLIKELY (c == 0x00AD))
    return FALSE;

  if (G_UNLIKELY (ISZEROWIDTHTYPE (TYPE (c))))
    return TRUE;

    {0x30000, 0x3FFFD}
  };

  if (bsearch (GUINT_TO_POINTER (c), wide, G_N_ELEMENTS (wide), sizeof wide[0],
	       interval_compare))
    return TRUE;
    {0xE0100, 0xE01EF}, {0xF0000, 0xFFFFD}, {0x100000, 0x10FFFD}
  };

  if (g_unichar_iswide (c))
    return TRUE;

  if (bsearch (GUINT_TO_POINTER (c), ambiguous, G_N_ELEMENTS (ambiguous), sizeof ambiguous[0],
	       interval_compare))
    return TRUE;
gunichar
g_unichar_toupper (gunichar c)
{
  int t = TYPE (c);
  if (t == G_UNICODE_LOWERCASE_LETTER)
    {
gunichar
g_unichar_tolower (gunichar c)
{
  int t = TYPE (c);
  if (t == G_UNICODE_UPPERCASE_LETTER)
    {
	return title_table[i][0];
    }
    
  if (TYPE (c) == G_UNICODE_LOWERCASE_LETTER)
    return g_unichar_toupper (c);

  return c;
int
g_unichar_digit_value (gunichar c)
{
  if (TYPE (c) == G_UNICODE_DECIMAL_NUMBER)
    return ATTTABLE (c >> 8, c & 0xff);
  return -1;
    return c - 'A' + 10;
  if (c >= 'a' && c <= 'f')
    return c - 'a' + 10;
  if (TYPE (c) == G_UNICODE_DECIMAL_NUMBER)
    return ATTTABLE (c >> 8, c & 0xff);
  return -1;
GUnicodeType
g_unichar_type (gunichar c)
{
  return TYPE (c);
}

    {
      gunichar c = g_utf8_get_char (p);
      
      if (ISMARK (TYPE (c)))
	{
	  if (!remove_dot || c != 0x307 /* COMBINING DOT ABOVE */)
  while ((max_len < 0 || p < str + max_len) && *p)
    {
      gunichar c = g_utf8_get_char (p);
      int t = TYPE (c);
      gunichar val;

  while ((max_len < 0 || p < str + max_len) && *p)
    {
      gunichar c = g_utf8_get_char (p);
      int t = TYPE (c);
      gunichar val;

          len += g_unichar_to_utf8 (0x0069, out_buffer ? out_buffer + len : NULL); 
          len += g_unichar_to_utf8 (0x0307, out_buffer ? out_buffer + len : NULL); 

          switch (c)
            {
            case 0x00cc: 
               (c == 'I' || c == 'J' || c == 0x012e) && 
               has_more_above (p))
        {
          len += g_unichar_to_utf8 (g_unichar_tolower (c), out_buffer ? out_buffer + len : NULL); 
          len += g_unichar_to_utf8 (0x0307, out_buffer ? out_buffer + len : NULL); 
        }