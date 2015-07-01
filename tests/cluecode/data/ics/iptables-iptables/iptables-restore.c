/* Code to restore the iptables state, from file by iptables-save.
 * (C) 2000-2002 by Harald Welte <laforge@gnumonks.org>
 * based on previous code from Rusty Russell <rusty@linuxcare.com.au>
 *
#endif

	while ((c = getopt_long(argc, argv, "bcvthnM:T:", options, NULL)) != -1) {
		switch (c) {
			case 'b':
				binary = 1;