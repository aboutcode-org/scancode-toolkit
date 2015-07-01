/*
 * Copyright (c) 1990, 1993, 1994, 1995, 1996
 *	The Regents of the University of California.  All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that: (1) source code distributions
 * retain the above copyright notice and this paragraph in its entirety, (2)
 * distributions including binary code include the above copyright notice and
 * this paragraph in its entirety in the documentation or other materials
 * provided with the distribution, and (3) all advertising materials mentioning

/* Hex digit to integer. */
static inline int
xdtoi(c)
	register int c;
{
	if (isdigit(c))
		return c - '0';
	else if (islower(c))
		return c - 'a' + 10;
	else

	do {
		c = getc(f);
	} while (isspace(c) && c != '\n');

	return c;

		/* If this is a comment, or first thing on line
		   cannot be etehrnet address, skip the line. */
		if (!isxdigit(c)) {
			c = skip_line(fp);
			continue;

		/* must be the start of an address */
		for (i = 0; i < 6; i += 1) {
			d = xdtoi(c);
			c = getc(fp);
			if (isxdigit(c)) {
				d <<= 4;
				d |= xdtoi(c);
				c = getc(fp);
			}
			break;

		/* Must be whitespace */
		if (!isspace(c)) {
			c = skip_line(fp);
			continue;
		do {
			*bp++ = c;
			c = getc(fp);
		} while (!isspace(c) && c != EOF && --d > 0);
		*bp = '\0';
