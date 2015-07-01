is supposed to have been given to you along with ansi2knr so you can know
your rights and responsibilities.  It should be in a file named COPYLEFT.
[In the IJG distribution, the GPL appears below, not in a separate file.]
Among other things, the copyright notice and this notice must be preserved
on all copies.

		    GHOSTSCRIPT GENERAL PUBLIC LICENSE
		    (Clarified 11 Feb 1988)

 Copyright (C) 1988 Richard M. Stallman
 Everyone is permitted to copy and distribute verbatim copies of this
 license, but changing it is not allowed.  You can also use this wording

  1. You may copy and distribute verbatim copies of Ghostscript source
code as you receive it, in any medium, provided that you conspicuously
and appropriately publish on each copy a valid copyright and license
notice "Copyright (C) 1989 Aladdin Enterprises.  All rights reserved.
Distributed by Free Software Foundation, Inc." (or with whatever year is
appropriate); keep intact the notices on all files that refer to this
	lpd 95-06-22 removed #ifndefs whose sole purpose was to define
		undefined preprocessor symbols as 0; changed all #ifdefs
		for configuration symbols to #ifs
	lpd 95-04-05 changed copyright notice to make it clear that
		including ansi2knr in a program does not bring the entire
		program under the GPL
#else
#endif
#if STDC_HEADERS || !HAVE_ISASCII
#  define is_ascii(c) 1
#else
#  define is_ascii(c) isascii(c)
#endif

#define is_space(c) (is_ascii(c) && isspace(c))
#define is_alpha(c) (is_ascii(c) && isalpha(c))
#define is_alnum(c) (is_ascii(c) && isalnum(c))

/* Scanning macros */