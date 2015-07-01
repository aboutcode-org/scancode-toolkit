/* goption.c - Option parser
 *
 *  Copyright (C) 1999, 2003 Red Hat Software
 *  Copyright (C) 2004       Anders Carlsson <andersca@gnome.org>
 *
 * This library is free software; you can redistribute it and/or
static int
_g_unichar_get_width (gunichar c)
{
  if (G_UNLIKELY (g_unichar_iszerowidth (c)))
    return 0;

  /* we ignore the fact that we should call g_unichar_iswide_cjk() under
   * some locales (legacy East Asian ones) */
  if (g_unichar_iswide (c))
    return 2;

    {
      gchar c = group->entries[i].short_name;

      if (c)
	{
	  if (c == '-' || !g_ascii_isprint (c))
	    {
	      g_warning (G_STRLOC": ignoring invalid short option '%c' (%d)", c, c);