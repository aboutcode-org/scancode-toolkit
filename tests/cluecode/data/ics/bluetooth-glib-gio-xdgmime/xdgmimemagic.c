 *
 * More info can be found at http://www.freedesktop.org/standards/
 *
 * Copyright (C) 2003  Red Hat, Inc.
 * Copyright (C) 2003  Jonathan Blandford <jrb@alum.mit.edu>
 *
 * Licensed under the Academic Free License version 2.0
	  *end_of_file = TRUE;
	  break;
	}
      if (! isdigit (c))
	{
	  ungetc (c, magic_file);

  /* At this point, it must be a digit or a '>' */
  end_of_file = FALSE;
  if (isdigit (c))
    {
      ungetc (c, magic_file);