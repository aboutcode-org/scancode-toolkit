/* lnstat - Unified linux network statistics
 *
 * Copyright (C) 2004 by Harald Welte <laforge@gnumonks.org>
 *
 * Development of this code was funded by Astaro AG, http://www.astaro.com/
 *
 * Based on original concept and ideas from predecessor rtstat.c:
 *
 * Copyright 2001 by Robert Olsson <robert.olsson@its.uu.se>
 *                                 Uppsala University, Sweden
 *
static int usage(char *name, int exit_code)
{
	fprintf(stderr, "%s Version %s\n", name, LNSTAT_VERSION);
	fprintf(stderr, "Copyright (C) 2004 by Harald Welte "
			"<laforge@gnumonks.org>\n");
	fprintf(stderr, "This program is free software licensed under GNU GPLv2"
		int i, len = 0;
		char *tmp, *tok;

		switch (c) {
			case 'c':
				count = strtoul(optarg, NULL, 0);