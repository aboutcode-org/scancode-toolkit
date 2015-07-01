/* Code to save the iptables state, in human readable-form. */
/* (C) 1999 by Paul 'Rusty' Russell <rusty@rustcorp.com.au> and
 * (C) 2000-2002 by Harald Welte <laforge@gnumonks.org>
 *
 * This code is distributed under the terms of GNU GPL v2
#endif

	while ((c = getopt_long(argc, argv, "bcdt:", options, NULL)) != -1) {
		switch (c) {
		case 'b':
			show_binary = 1;