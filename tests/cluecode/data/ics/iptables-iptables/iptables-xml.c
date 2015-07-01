/* Code to convert iptables-save format to xml format,
 * (C) 2006 Ufo Mechanic <azez@ufomechanic.net>
 * based on iptables-restore (C) 2000-2002 by Harald Welte <laforge@gnumonks.org>
 * based on previous code from Rusty Russell <rusty@linuxcare.com.au>
 *

	xtables_set_params(&iptables_xml_globals);
	while ((c = getopt_long(argc, argv, "cvh", options, NULL)) != -1) {
		switch (c) {
		case 'c':
			combine = 1;