/* dhcpd.c

   DHCP Server Daemon. */

/*
 * Copyright (c) 1996-2003 Internet Software Consortium.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of Internet Software Consortium nor the names
 *    of its contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE INTERNET SOFTWARE CONSORTIUM AND
 * CONTRIBUTORS ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED.  IN NO EVENT SHALL THE INTERNET SOFTWARE CONSORTIUM OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
 * USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 *
 * This software has been written for the Internet Software Consortium
 * by Ted Lemon in cooperation with Vixie Enterprises and Nominum, Inc.
 * To learn more about the Internet Software Consortium, see
 * ``http://www.isc.org/''.  To learn more about Vixie Enterprises,
 * see ``http://www.vix.com''.   To learn more about Nominum, Inc., see
 * ``http://www.nominum.com''.
 */

#ifndef lint
static char ocopyright[] =
"$Id: dhcpd.c,v 1.115.2.6.2.1 2003/01/14 23:02:33 dhankins Exp $ Copyright 1995-2003 Internet Software Consortium.";
#endif

  static char copyright[] =
"Copyright 1995-2003 Internet Software Consortium.";
static char arr [] = "All rights reserved.";
static char message [] = "Internet Software Consortium DHCP Server";
static char url [] = "For info, please visit http://www.isc.org/products/DHCP";

#include "dhcpd.h"
#include "version.h"
#include <omapip/omapip_p.h>

static void usage PROTO ((void));

TIME cur_time;

struct iaddr server_identifier;
int server_identifier_matched;

#if defined (NSUPDATE)

/* This stuff is always executed to figure the default values for certain
   ddns variables. */

char std_nsupdate [] = "						    \n\
option server.ddns-hostname =						    \n\
  pick (option fqdn.hostname, option host-name);			    \n\
option server.ddns-domainname =	config-option domain-name;		    \n\
option server.ddns-ttl = encode-int(lease-time / 2, 32);		    \n\
option server.ddns-rev-domainname = \"in-addr.arpa.\";";

/* This is the old-style name service updater that is executed
   whenever a lease is committed.  It does not follow the DHCP-DNS
   draft at all. */

char old_nsupdate [] = "						    \n\
on commit {								    \n\
  if (not static and							    \n\
      ((config-option server.ddns-updates = null) or			    \n\
       (config-option server.ddns-updates != 0))) {			    \n\
    set new-ddns-fwd-name =						    \n\
      concat (pick (config-option server.ddns-hostname,			    \n\
		    option host-name), \".\",				    \n\
	      pick (config-option server.ddns-domainname,		    \n\
		    config-option domain-name));			    \n\
    if (defined (ddns-fwd-name) and ddns-fwd-name != new-ddns-fwd-name) {   \n\
      switch (ns-update (delete (IN, A, ddns-fwd-name, leased-address))) {  \n\
      case NOERROR:							    \n\
	unset ddns-fwd-name;						    \n\
	on expiry or release {						    \n\
	}								    \n\
      }									    \n\
    }									    \n\
									    \n\
    if (not defined (ddns-fwd-name)) {					    \n\
      set ddns-fwd-name = new-ddns-fwd-name;				    \n\
      if defined (ddns-fwd-name) {					    \n\
	switch (ns-update (not exists (IN, A, ddns-fwd-name, null),	    \n\
			   add (IN, A, ddns-fwd-name, leased-address,	    \n\
				lease-time / 2))) {			    \n\
	default:							    \n\
	  unset ddns-fwd-name;						    \n\
	  break;							    \n\
									    \n\
	case NOERROR:							    \n\
	  set ddns-rev-name =						    \n\
	    concat (binary-to-ascii (10, 8, \".\",			    \n\
				     reverse (1,			    \n\
					      leased-address)), \".\",	    \n\
		    pick (config-option server.ddns-rev-domainname,	    \n\
			  \"in-addr.arpa.\"));				    \n\
	  switch (ns-update (delete (IN, PTR, ddns-rev-name, null),	    \n\
			     add (IN, PTR, ddns-rev-name, ddns-fwd-name,    \n\
				  lease-time / 2)))			    \n\
	    {								    \n\
	    default:							    \n\
	      unset ddns-rev-name;					    \n\
	      on release or expiry {					    \n\
		switch (ns-update (delete (IN, A, ddns-fwd-name,	    \n\
					   leased-address))) {		    \n\
		case NOERROR:						    \n\
		  unset ddns-fwd-name;					    \n\
		  break;						    \n\
		}							    \n\
		on release or expiry;					    \n\
	      }								    \n\
	      break;							    \n\
									    \n\
	    case NOERROR:						    \n\
	      on release or expiry {					    \n\
		switch (ns-update (delete (IN, PTR, ddns-rev-name, null))) {\n\
		case NOERROR:						    \n\
		  unset ddns-rev-name;					    \n\
		  break;						    \n\
		}							    \n\
		switch (ns-update (delete (IN, A, ddns-fwd-name,	    \n\
					   leased-address))) {		    \n\
		case NOERROR:						    \n\
		  unset ddns-fwd-name;					    \n\
		  break;						    \n\
		}							    \n\
		on release or expiry;					    \n\
	      }								    \n\
	    }								    \n\
	}								    \n\
      }									    \n\
    }									    \n\
    unset new-ddns-fwd-name;						    \n\
  }									    \n\
}";

int ddns_update_style;
#endif /* NSUPDATE */

const char *path_dhcpd_conf = _PATH_DHCPD_CONF;
const char *path_dhcpd_db = _PATH_DHCPD_DB;
const char *path_dhcpd_pid = _PATH_DHCPD_PID;

int dhcp_max_agent_option_packet_length = DHCP_MTU_MAX;

static omapi_auth_key_t *omapi_key = (omapi_auth_key_t *)0;
int omapi_port;

#if defined (TRACING)
trace_type_t *trace_srandom;
#endif

static isc_result_t verify_addr (omapi_object_t *l, omapi_addr_t *addr) {
	return ISC_R_SUCCESS;
}

static isc_result_t verify_auth (omapi_object_t *p, omapi_auth_key_t *a) {
	if (a != omapi_key)
		return ISC_R_INVALIDKEY;
	return ISC_R_SUCCESS;
}

static void omapi_listener_start (void *foo)
{
	omapi_object_t *listener;
	isc_result_t result;

	listener = (omapi_object_t *)0;
	result = omapi_generic_new (&listener, MDL);
	if (result != ISC_R_SUCCESS)
		log_fatal ("Can't allocate new generic object: %s",
			   isc_result_totext (result));
	result = omapi_protocol_listen (listener,
					(unsigned)omapi_port, 1);
	if (result == ISC_R_SUCCESS && omapi_key)
		result = omapi_protocol_configure_security
			(listener, verify_addr, verify_auth);
	if (result != ISC_R_SUCCESS) {
		log_error ("Can't start OMAPI protocol: %s",
			   isc_result_totext (result));
		add_timeout (cur_time + 5, omapi_listener_start, 0, 0, 0);
	}
	omapi_object_dereference (&listener, MDL);
}

int main (argc, argv, envp)
	int argc;
	char **argv, **envp;
{
	int i, status;
	struct servent *ent;
	char *s;
	int cftest = 0;
	int lftest = 0;
#ifndef DEBUG
	int pidfilewritten = 0;
	int pid;
	char pbuf [20];
	int daemon = 1;
#endif
	int quiet = 0;
	char *server = (char *)0;
	isc_result_t result;
	unsigned seed;
	struct interface_info *ip;
	struct parse *parse;
	int lose;
	omapi_object_t *auth;
	struct tsig_key *key;
	omapi_typed_data_t *td;
	int no_dhcpd_conf = 0;
	int no_dhcpd_db = 0;
	int no_dhcpd_pid = 0;
#if defined (TRACING)
	char *traceinfile = (char *)0;
	char *traceoutfile = (char *)0;
#endif

	/* Make sure we have stdin, stdout and stderr. */
	status = open ("/dev/null", O_RDWR);
	if (status == 0)
		status = open ("/dev/null", O_RDWR);
	if (status == 1) {
		status = open ("/dev/null", O_RDWR);
		log_perror = 0; /* No sense logging to /dev/null. */
	} else if (status != -1)
		close (status);

	/* Set up the client classification system. */
	classification_setup ();

	/* Initialize the omapi system. */
	result = omapi_init ();
	if (result != ISC_R_SUCCESS)
		log_fatal ("Can't initialize OMAPI: %s",
			   isc_result_totext (result));

	/* Set up the OMAPI wrappers for common objects. */
	dhcp_db_objects_setup ();
	/* Set up the OMAPI wrappers for various server database internal
	   objects. */
	dhcp_common_objects_setup ();

	/* Initially, log errors to stderr as well as to syslogd. */
#ifdef SYSLOG_4_2
	openlog ("dhcpd", LOG_NDELAY);
	log_priority = DHCPD_LOG_FACILITY;
#else
	openlog ("dhcpd", LOG_NDELAY, DHCPD_LOG_FACILITY);
#endif

	for (i = 1; i < argc; i++) {
		if (!strcmp (argv [i], "-p")) {
			if (++i == argc)
				usage ();
			for (s = argv [i]; *s; s++)
				if (!isdigit (*s))
					log_fatal ("%s: not a valid UDP port",
					       argv [i]);
			status = atoi (argv [i]);
			if (status < 1 || status > 65535)
				log_fatal ("%s: not a valid UDP port",
				       argv [i]);
			local_port = htons (status);
			log_debug ("binding to user-specified port %d",
			       ntohs (local_port));
		} else if (!strcmp (argv [i], "-f")) {
#ifndef DEBUG
			daemon = 0;
#endif
		} else if (!strcmp (argv [i], "-d")) {
#ifndef DEBUG
			daemon = 0;
#endif
			log_perror = -1;
		} else if (!strcmp (argv [i], "-s")) {
			if (++i == argc)
				usage ();
			server = argv [i];
		} else if (!strcmp (argv [i], "-cf")) {
			if (++i == argc)
				usage ();
			path_dhcpd_conf = argv [i];
			no_dhcpd_conf = 1;
		} else if (!strcmp (argv [i], "-lf")) {
			if (++i == argc)
				usage ();
			path_dhcpd_db = argv [i];
			no_dhcpd_db = 1;
		} else if (!strcmp (argv [i], "-pf")) {
			if (++i == argc)
				usage ();
			path_dhcpd_pid = argv [i];
			no_dhcpd_pid = 1;
                } else if (!strcmp (argv [i], "-t")) {
			/* test configurations only */
#ifndef DEBUG
			daemon = 0;
#endif
			cftest = 1;
			log_perror = -1;
                } else if (!strcmp (argv [i], "-T")) {
			/* test configurations and lease file only */
#ifndef DEBUG
			daemon = 0;
#endif
			cftest = 1;
			lftest = 1;
			log_perror = -1;
		} else if (!strcmp (argv [i], "-q")) {
			quiet = 1;
			quiet_interface_discovery = 1;
		} else if (!strcmp (argv [i], "--version")) {
			log_info ("isc-dhcpd-%s", DHCP_VERSION);
			exit (0);
#if defined (TRACING)
		} else if (!strcmp (argv [i], "-tf")) {
			if (++i == argc)
				usage ();
			traceoutfile = argv [i];
		} else if (!strcmp (argv [i], "-play")) {
			if (++i == argc)
				usage ();
			traceinfile = argv [i];
			trace_replay_init ();
#endif /* TRACING */
		} else if (argv [i][0] == '-') {
			usage ();
		} else {
			struct interface_info *tmp =
				(struct interface_info *)0;
			result = interface_allocate (&tmp, MDL);
			if (result != ISC_R_SUCCESS)
				log_fatal ("Insufficient memory to %s %s: %s",
					   "record interface", argv [i],
					   isc_result_totext (result));
			strcpy (tmp -> name, argv [i]);
			if (interfaces) {
				interface_reference (&tmp -> next,
						     interfaces, MDL);
				interface_dereference (&interfaces, MDL);
			}
			interface_reference (&interfaces, tmp, MDL);
			tmp -> flags = INTERFACE_REQUESTED;
		}
	}

	if (!no_dhcpd_conf && (s = getenv ("PATH_DHCPD_CONF"))) {
		path_dhcpd_conf = s;
	}
	if (!no_dhcpd_db && (s = getenv ("PATH_DHCPD_DB"))) {
		path_dhcpd_db = s;
	}
	if (!no_dhcpd_pid && (s = getenv ("PATH_DHCPD_PID"))) {
		path_dhcpd_pid = s;
	}

	if (!quiet) {
		log_info ("%s %s", message, DHCP_VERSION);
		log_info (copyright);
		log_info (arr);
		log_info (url);
	} else {
		quiet = 0;
		log_perror = 0;
	}

#if defined (TRACING)
	trace_init (set_time, MDL);
	if (traceoutfile)
		trace_begin (traceoutfile, MDL);
	interface_trace_setup ();
	parse_trace_setup ();
	trace_srandom = trace_type_register ("random-seed", (void *)0,
					     trace_seed_input,
					     trace_seed_stop, MDL);
#endif

	/* Default to the DHCP/BOOTP port. */
	if (!local_port)
	{
		if ((s = getenv ("DHCPD_PORT"))) {
			local_port = htons (atoi (s));
			log_debug ("binding to environment-specified port %d",
				   ntohs (local_port));
		} else {
			ent = getservbyname ("dhcp", "udp");
			if (!ent)
				local_port = htons (67);
			else
				local_port = ent -> s_port;
#ifndef __CYGWIN32__ /* XXX */
			endservent ();
#endif
		}
	}
  
	remote_port = htons (ntohs (local_port) + 1);

	if (server) {
		if (!inet_aton (server, &limited_broadcast)) {
			struct hostent *he;
			he = gethostbyname (server);
			if (he) {
				memcpy (&limited_broadcast,
					he -> h_addr_list [0],
					sizeof limited_broadcast);
			} else
				limited_broadcast.s_addr = INADDR_BROADCAST;
		}
	} else {
		limited_broadcast.s_addr = INADDR_BROADCAST;
	}

	/* Get the current time... */
	GET_TIME (&cur_time);

	/* Set up the initial dhcp option universe. */
	initialize_common_option_spaces ();
	initialize_server_option_spaces ();

	/* Add the ddns update style enumeration prior to parsing. */
	add_enumeration (&ddns_styles);
	add_enumeration (&syslog_enum);

	if (!group_allocate (&root_group, MDL))
		log_fatal ("Can't allocate root group!");
	root_group -> authoritative = 0;

	/* Set up various hooks. */
	dhcp_interface_setup_hook = dhcpd_interface_setup_hook;
	bootp_packet_handler = do_packet;

#if defined (NSUPDATE)
	/* Set up the standard name service updater routine. */
	parse = (struct parse *)0;
	status = new_parse (&parse, -1,
			    std_nsupdate, (sizeof std_nsupdate) - 1,
			    "standard name service update routine", 0);
	if (status != ISC_R_SUCCESS)
		log_fatal ("can't begin parsing name service updater!");

	lose = 0;
	if (!(parse_executable_statements
	      (&root_group -> statements, parse, &lose, context_any))) {
		end_parse (&parse);
		log_fatal ("can't parse standard name service updater!");
	}
	end_parse (&parse);
#endif

	/* Initialize icmp support... */
	if (!cftest && !lftest)
		icmp_startup (1, lease_pinged);

#if defined (TRACING)
	if (traceinfile) {
	    if (!no_dhcpd_db) {
		    log_error ("%s", "");
		    log_error ("** You must specify a lease file with -lf.");
		    log_error ("   Dhcpd will not overwrite your default");
		    log_fatal ("   lease file when playing back a trace. **");
	    }		
	    trace_file_replay (traceinfile);

#if defined (DEBUG_MEMORY_LEAKAGE) || \
                defined (DEBUG_MEMORY_LEAKAGE_ON_EXIT)
            free_everything ();
            omapi_print_dmalloc_usage_by_caller (); 
#endif

	    exit (0);
	}
#endif

	/* Read the dhcpd.conf file... */
	if (readconf () != ISC_R_SUCCESS)
		log_fatal ("Configuration file errors encountered -- exiting");

	postconf_initialization (quiet);

        /* test option should cause an early exit */
 	if (cftest && !lftest) 
 		exit(0);

	group_write_hook = group_writer;

	/* Start up the database... */
	db_startup (lftest);

	if (lftest)
		exit (0);

	/* Discover all the network interfaces and initialize them. */
	discover_interfaces (DISCOVER_SERVER);

	/* Make up a seed for the random number generator from current
	   time plus the sum of the last four bytes of each
	   interface's hardware address interpreted as an integer.
	   Not much entropy, but we're booting, so we're not likely to
	   find anything better. */
	seed = 0;
	for (ip = interfaces; ip; ip = ip -> next) {
		int junk;
		memcpy (&junk,
			&ip -> hw_address.hbuf [ip -> hw_address.hlen -
					       sizeof seed], sizeof seed);
		seed += junk;
	}
	srandom (seed + cur_time);
#if defined (TRACING)
	trace_seed_stash (trace_srandom, seed + cur_time);
#endif
	postdb_startup ();

#ifndef DEBUG
	if (daemon) {
		/* First part of becoming a daemon... */
		if ((pid = fork ()) < 0)
			log_fatal ("Can't fork daemon: %m");
		else if (pid)
			exit (0);
	}

	/* Read previous pid file. */
	if ((i = open (path_dhcpd_pid, O_RDONLY)) >= 0) {
		status = read (i, pbuf, (sizeof pbuf) - 1);
		close (i);
		pbuf [status] = 0;
		pid = atoi (pbuf);

		/* If the previous server process is not still running,
		   write a new pid file immediately. */
		if (pid && (pid == getpid() || kill (pid, 0) < 0)) {
			unlink (path_dhcpd_pid);
			if ((i = open (path_dhcpd_pid,
				       O_WRONLY | O_CREAT, 0644)) >= 0) {
				sprintf (pbuf, "%d\n", (int)getpid ());
				write (i, pbuf, strlen (pbuf));
				close (i);
				pidfilewritten = 1;
			}
		} else
			log_fatal ("There's already a DHCP server running.");
	}

	/* If we were requested to log to stdout on the command line,
	   keep doing so; otherwise, stop. */
	if (log_perror == -1)
		log_perror = 1;
	else
		log_perror = 0;

	if (daemon) {
		/* Become session leader and get pid... */
		close (0);
		close (1);
		close (2);
		pid = setsid ();
	}

	/* If we didn't write the pid file earlier because we found a
	   process running the logged pid, but we made it to here,
	   meaning nothing is listening on the bootp port, then write
	   the pid file out - what's in it now is bogus anyway. */
	if (!pidfilewritten) {
		unlink (path_dhcpd_pid);
		if ((i = open (path_dhcpd_pid,
			       O_WRONLY | O_CREAT, 0644)) >= 0) {
			sprintf (pbuf, "%d\n", (int)getpid ());
			write (i, pbuf, strlen (pbuf));
			close (i);
			pidfilewritten = 1;
		}
	}
#endif /* !DEBUG */

#if defined (DEBUG_MEMORY_LEAKAGE) || defined (DEBUG_MALLOC_POOL) || \
		defined (DEBUG_MEMORY_LEAKAGE_ON_EXIT)
	dmalloc_cutoff_generation = dmalloc_generation;
	dmalloc_longterm = dmalloc_outstanding;
	dmalloc_outstanding = 0;
#endif

#if defined (DEBUG_RC_HISTORY_EXHAUSTIVELY)
	dump_rc_history ();
#endif

	omapi_set_int_value ((omapi_object_t *)dhcp_control_object,
			     (omapi_object_t *)0, "state", server_running);

	/* Receive packets and dispatch them... */
	dispatch ();

	/* Not reached */
	return 0;
}

void postconf_initialization (int quiet)
{
	struct option_state *options = (struct option_state *)0;
	struct data_string db;
	struct option_cache *oc;
	char *s;
	isc_result_t result;
	struct parse *parse;
	int tmp;

	/* Now try to get the lease file name. */
	option_state_allocate (&options, MDL);

	execute_statements_in_scope ((struct binding_value **)0,
				     (struct packet *)0,
				     (struct lease *)0,
				     (struct client_state *)0,
				     (struct option_state *)0,
				     options, &global_scope,
				     root_group,
				     (struct group *)0);
	memset (&db, 0, sizeof db);
	oc = lookup_option (&server_universe, options, SV_LEASE_FILE_NAME);
	if (oc &&
	    evaluate_option_cache (&db, (struct packet *)0,
				   (struct lease *)0, (struct client_state *)0,
				   options, (struct option_state *)0,
				   &global_scope, oc, MDL)) {
		s = dmalloc (db.len + 1, MDL);
		if (!s)
			log_fatal ("no memory for lease db filename.");
		memcpy (s, db.data, db.len);
		s [db.len] = 0;
		data_string_forget (&db, MDL);
		path_dhcpd_db = s;
	}
	
	oc = lookup_option (&server_universe, options, SV_PID_FILE_NAME);
	if (oc &&
	    evaluate_option_cache (&db, (struct packet *)0,
				   (struct lease *)0, (struct client_state *)0,
				   options, (struct option_state *)0,
				   &global_scope, oc, MDL)) {
		s = dmalloc (db.len + 1, MDL);
		if (!s)
			log_fatal ("no memory for lease db filename.");
		memcpy (s, db.data, db.len);
		s [db.len] = 0;
		data_string_forget (&db, MDL);
		path_dhcpd_pid = s;
	}

	omapi_port = -1;
	oc = lookup_option (&server_universe, options, SV_OMAPI_PORT);
	if (oc &&
	    evaluate_option_cache (&db, (struct packet *)0,
				   (struct lease *)0, (struct client_state *)0,
				   options, (struct option_state *)0,
				   &global_scope, oc, MDL)) {
		if (db.len == 2) {
			omapi_port = getUShort (db.data);
		} else
			log_fatal ("invalid omapi port data length");
		data_string_forget (&db, MDL);
	}

	oc = lookup_option (&server_universe, options, SV_OMAPI_KEY);
	if (oc &&
	    evaluate_option_cache (&db, (struct packet *)0,
				   (struct lease *)0, (struct client_state *)0,
				   options,
				   (struct option_state *)0,
				   &global_scope, oc, MDL)) {
		s = dmalloc (db.len + 1, MDL);
		if (!s)
			log_fatal ("no memory for OMAPI key filename.");
		memcpy (s, db.data, db.len);
		s [db.len] = 0;
		data_string_forget (&db, MDL);
		result = omapi_auth_key_lookup_name (&omapi_key, s);
		dfree (s, MDL);
		if (result != ISC_R_SUCCESS)
			log_fatal ("OMAPI key %s: %s",
				   s, isc_result_totext (result));
	}

	oc = lookup_option (&server_universe, options, SV_LOCAL_PORT);
	if (oc &&
	    evaluate_option_cache (&db, (struct packet *)0,
				   (struct lease *)0, (struct client_state *)0,
				   options,
				   (struct option_state *)0,
				   &global_scope, oc, MDL)) {
		if (db.len == 2) {
			local_port = htons (getUShort (db.data));
		} else
			log_fatal ("invalid local port data length");
		data_string_forget (&db, MDL);
	}

	oc = lookup_option (&server_universe, options, SV_REMOTE_PORT);
	if (oc &&
	    evaluate_option_cache (&db, (struct packet *)0,
				   (struct lease *)0, (struct client_state *)0,
				   options, (struct option_state *)0,
				   &global_scope, oc, MDL)) {
		if (db.len == 2) {
			remote_port = htons (getUShort (db.data));
		} else
			log_fatal ("invalid remote port data length");
		data_string_forget (&db, MDL);
	}

	oc = lookup_option (&server_universe, options,
			    SV_LIMITED_BROADCAST_ADDRESS);
	if (oc &&
	    evaluate_option_cache (&db, (struct packet *)0,
				   (struct lease *)0, (struct client_state *)0,
				   options, (struct option_state *)0,
				   &global_scope, oc, MDL)) {
		if (db.len == 4) {
			memcpy (&limited_broadcast, db.data, 4);
		} else
			log_fatal ("invalid remote port data length");
		data_string_forget (&db, MDL);
	}

	oc = lookup_option (&server_universe, options,
			    SV_LOCAL_ADDRESS);
	if (oc &&
	    evaluate_option_cache (&db, (struct packet *)0,
				   (struct lease *)0, (struct client_state *)0,
				   options, (struct option_state *)0,
				   &global_scope, oc, MDL)) {
		if (db.len == 4) {
			memcpy (&local_address, db.data, 4);
		} else
			log_fatal ("invalid remote port data length");
		data_string_forget (&db, MDL);
	}

	oc = lookup_option (&server_universe, options, SV_DDNS_UPDATE_STYLE);
	if (oc) {
		if (evaluate_option_cache (&db, (struct packet *)0,
					   (struct lease *)0,
					   (struct client_state *)0,
					   options,
					   (struct option_state *)0,
					   &global_scope, oc, MDL)) {
			if (db.len == 1) {
				ddns_update_style = db.data [0];
			} else
				log_fatal ("invalid dns update type");
			data_string_forget (&db, MDL);
		}
	} else {
		log_info ("%s", "");
		log_error ("** You must add a ddns-update-style %s%s.",
			   "statement to ", path_dhcpd_conf);
		log_error ("   To get the same behaviour as in 3.0b2pl11 %s",
			   "and previous");
		log_error ("   versions, add a line that says \"%s\"",
			   "ddns-update-style ad-hoc;");
		log_fatal ("   Please read the dhcpd.conf manual page %s",
			   "for more information. **");
	}

	oc = lookup_option (&server_universe, options, SV_LOG_FACILITY);
	if (oc) {
		if (evaluate_option_cache (&db, (struct packet *)0,
					   (struct lease *)0,
					   (struct client_state *)0,
					   options,
					   (struct option_state *)0,
					   &global_scope, oc, MDL)) {
			if (db.len == 1) {
				closelog ();
#ifdef SYSLOG_4_2
				openlog ("dhcpd", LOG_NDELAY);
				log_priority = db.data [0];
#else
				openlog ("dhcpd",
					 LOG_NDELAY, db.data [0]);
#endif
				/* Log the startup banner into the new
				   log file. */
				if (!quiet) {
					/* Don't log to stderr twice. */
					tmp = log_perror;
					log_perror = 0;
					log_info ("%s %s",
						  message, DHCP_VERSION);
					log_info (copyright);
					log_info (arr);
					log_info (url);
					log_perror = tmp;
				}
			} else
				log_fatal ("invalid log facility");
			data_string_forget (&db, MDL);
		}
	}

	/* Don't need the options anymore. */
	option_state_dereference (&options, MDL);
	
#if defined (NSUPDATE)
	/* If old-style ddns updates have been requested, parse the
	   old-style ddns updater. */
	if (ddns_update_style == 1) {
		struct executable_statement **e, *s;

		if (root_group -> statements) {
			s = (struct executable_statement *)0;
			if (!executable_statement_allocate (&s, MDL))
				log_fatal ("no memory for ddns updater");
			executable_statement_reference
				(&s -> next, root_group -> statements, MDL);
			executable_statement_dereference
				(&root_group -> statements, MDL);
			executable_statement_reference
				(&root_group -> statements, s, MDL);
			s -> op = statements_statement;
			e = &s -> data.statements;
			executable_statement_dereference (&s, MDL);
		} else {
			e = &root_group -> statements;
		}

		/* Set up the standard name service updater routine. */
		parse = (struct parse *)0;
		result = new_parse (&parse, -1,
				 old_nsupdate, (sizeof old_nsupdate) - 1,
				 "old name service update routine", 0);
		if (result != ISC_R_SUCCESS)
			log_fatal ("can't begin parsing old ddns updater!");

		tmp = 0;
		if (!(parse_executable_statements (e, parse,
						   &tmp, context_any))) {
			end_parse (&parse);
			log_fatal ("can't parse standard ddns updater!");
		}
		end_parse (&parse);
	}
#endif
}

void postdb_startup (void)
{
	/* Initialize the omapi listener state. */
	if (omapi_port != -1) {
		omapi_listener_start (0);
	}

#if defined (FAILOVER_PROTOCOL)
	/* Initialize the failover listener state. */
	dhcp_failover_startup ();
#endif
}

/* Print usage message. */

static void usage ()
{
	log_info ("%s %s", message, DHCP_VERSION);
	log_info (copyright);
	log_info (arr);

	log_fatal ("Usage: dhcpd [-p <UDP port #>] [-d] [-f]%s%s%s%s",
		   "\n             [-cf config-file] [-lf lease-file]",
#if defined (TRACING)
		   "\n		   [-tf trace-output-file]",
		   "\n		   [-play trace-input-file]",
#else
		   "", "",
#endif /* TRACING */
		   "\n             [-t] [-T] [-s server] [if0 [...ifN]]");
}

void lease_pinged (from, packet, length)
	struct iaddr from;
	u_int8_t *packet;
	int length;
{
	struct lease *lp;

	/* Don't try to look up a pinged lease if we aren't trying to
	   ping one - otherwise somebody could easily make us churn by
	   just forging repeated ICMP EchoReply packets for us to look
	   up. */
	if (!outstanding_pings)
		return;

	lp = (struct lease *)0;
	if (!find_lease_by_ip_addr (&lp, from, MDL)) {
		log_debug ("unexpected ICMP Echo Reply from %s",
			   piaddr (from));
		return;
	}

	if (!lp -> state) {
#if defined (FAILOVER_PROTOCOL)
		if (!lp -> pool ||
		    !lp -> pool -> failover_peer)
#endif
			log_debug ("ICMP Echo Reply for %s late or spurious.",
				   piaddr (from));
		goto out;
	}

	if (lp -> ends > cur_time) {
		log_debug ("ICMP Echo reply while lease %s valid.",
			   piaddr (from));
	}

	/* At this point it looks like we pinged a lease and got a
	   response, which shouldn't have happened. */
	data_string_forget (&lp -> state -> parameter_request_list, MDL);
	free_lease_state (lp -> state, MDL);
	lp -> state = (struct lease_state *)0;

	abandon_lease (lp, "pinged before offer");
	cancel_timeout (lease_ping_timeout, lp);
	--outstanding_pings;
      out:
	lease_dereference (&lp, MDL);
}

void lease_ping_timeout (vlp)
	void *vlp;
{
	struct lease *lp = vlp;

#if defined (DEBUG_MEMORY_LEAKAGE)
	unsigned long previous_outstanding = dmalloc_outstanding;
#endif

	--outstanding_pings;
	dhcp_reply (lp);

#if defined (DEBUG_MEMORY_LEAKAGE)
	log_info ("generation %ld: %ld new, %ld outstanding, %ld long-term",
		  dmalloc_generation,
		  dmalloc_outstanding - previous_outstanding,
		  dmalloc_outstanding, dmalloc_longterm);
#endif
#if defined (DEBUG_MEMORY_LEAKAGE)
	dmalloc_dump_outstanding ();
#endif
}

int dhcpd_interface_setup_hook (struct interface_info *ip, struct iaddr *ia)
{
	struct subnet *subnet;
	struct shared_network *share;
	isc_result_t status;

	/* Special case for fallback network - not sure why this is
	   necessary. */
	if (!ia) {
		const char *fnn = "fallback-net";
		char *s;
		status = shared_network_allocate (&ip -> shared_network, MDL);
		if (status != ISC_R_SUCCESS)
			log_fatal ("No memory for shared subnet: %s",
				   isc_result_totext (status));
		ip -> shared_network -> name = dmalloc (strlen (fnn) + 1, MDL);
		strcpy (ip -> shared_network -> name, fnn);
		return 1;
	}

	/* If there's a registered subnet for this address,
	   connect it together... */
	subnet = (struct subnet *)0;
	if (find_subnet (&subnet, *ia, MDL)) {
		/* If this interface has multiple aliases on the same
		   subnet, ignore all but the first we encounter. */
		if (!subnet -> interface) {
			interface_reference (&subnet -> interface, ip, MDL);
			subnet -> interface_address = *ia;
		} else if (subnet -> interface != ip) {
			log_error ("Multiple interfaces match the %s: %s %s", 
				   "same subnet",
				   subnet -> interface -> name, ip -> name);
		}
		share = subnet -> shared_network;
		if (ip -> shared_network &&
		    ip -> shared_network != share) {
			log_fatal ("Interface %s matches multiple shared %s",
				   ip -> name, "networks");
		} else {
			if (!ip -> shared_network)
				shared_network_reference
					(&ip -> shared_network, share, MDL);
		}
		
		if (!share -> interface) {
			interface_reference (&share -> interface, ip, MDL);
		} else if (share -> interface != ip) {
			log_error ("Multiple interfaces match the %s: %s %s", 
				   "same shared network",
				   share -> interface -> name, ip -> name);
		}
		subnet_dereference (&subnet, MDL);
	}
	return 1;
}

static TIME shutdown_time;
static int omapi_connection_count;
enum dhcp_shutdown_state shutdown_state;

isc_result_t dhcp_io_shutdown (omapi_object_t *obj, void *foo)
{
	/* Shut down all listeners. */
	if (shutdown_state == shutdown_listeners &&
	    obj -> type == omapi_type_listener &&
	    obj -> inner &&
	    obj -> inner -> type == omapi_type_protocol_listener) {
		omapi_listener_destroy (obj, MDL);
		return ISC_R_SUCCESS;
	}

	/* Shut down all existing omapi connections. */
	if (obj -> type == omapi_type_connection &&
	    obj -> inner &&
	    obj -> inner -> type == omapi_type_protocol) {
		if (shutdown_state == shutdown_drop_omapi_connections) {
			omapi_disconnect (obj, 1);
		}
		omapi_connection_count++;
		if (shutdown_state == shutdown_omapi_connections) {
			omapi_disconnect (obj, 0);
			return ISC_R_SUCCESS;
		}
	}

	/* Shutdown all DHCP interfaces. */
	if (obj -> type == dhcp_type_interface &&
	    shutdown_state == shutdown_dhcp) {
		dhcp_interface_remove (obj, (omapi_object_t *)0);
		return ISC_R_SUCCESS;
	}
	return ISC_R_SUCCESS;
}

static isc_result_t dhcp_io_shutdown_countdown (void *vlp)
{
	dhcp_failover_state_t *state;
#if defined (FAILOVER_PROTOCOL)
	int failover_connection_count = 0;
#endif

      oncemore:
	if (shutdown_state == shutdown_listeners ||
	    shutdown_state == shutdown_omapi_connections ||
	    shutdown_state == shutdown_drop_omapi_connections ||
	    shutdown_state == shutdown_dhcp) {
		omapi_connection_count = 0;
		omapi_io_state_foreach (dhcp_io_shutdown, 0);
	}

	if ((shutdown_state == shutdown_listeners ||
	     shutdown_state == shutdown_omapi_connections ||
	     shutdown_state == shutdown_drop_omapi_connections) &&
	    omapi_connection_count == 0) {
		shutdown_state = shutdown_dhcp;
		shutdown_time = cur_time;
		goto oncemore;
	} else if (shutdown_state == shutdown_listeners &&
		   cur_time - shutdown_time > 4) {
		shutdown_state = shutdown_omapi_connections;
		shutdown_time = cur_time;
	} else if (shutdown_state == shutdown_omapi_connections &&
		   cur_time - shutdown_time > 4) {
		shutdown_state = shutdown_drop_omapi_connections;
		shutdown_time = cur_time;
	} else if (shutdown_state == shutdown_drop_omapi_connections &&
		   cur_time - shutdown_time > 4) {
		shutdown_state = shutdown_dhcp;
		shutdown_time = cur_time;
		goto oncemore;
	} else if (shutdown_state == shutdown_dhcp &&
		   cur_time - shutdown_time > 4) {
		shutdown_state = shutdown_done;
		shutdown_time = cur_time;
	}

#if defined (FAILOVER_PROTOCOL)
	/* Set all failover peers into the shutdown state. */
	if (shutdown_state == shutdown_dhcp) {
	    for (state = failover_states; state; state = state -> next) {
		if (state -> me.state == normal) {
		    dhcp_failover_set_state (state, shut_down);
		    failover_connection_count++;
		}
		if (state -> me.state == shut_down &&
		    state -> partner.state != partner_down)
			failover_connection_count++;
	    }
	}

	if (shutdown_state == shutdown_done) {
	    for (state = failover_states; state; state = state -> next) {
		if (state -> me.state == shut_down) {
		    if (state -> link_to_peer)
			dhcp_failover_link_dereference (&state -> link_to_peer,
							MDL);
		    dhcp_failover_set_state (state, recover);
		}
	    }
#if defined (DEBUG_MEMORY_LEAKAGE) || \
		defined (DEBUG_MEMORY_LEAKAGE_ON_EXIT)
	    free_everything ();
	    omapi_print_dmalloc_usage_by_caller ();
#endif
	    exit (0);
	}		
#else
	if (shutdown_state == shutdown_done) {
#if defined (DEBUG_MEMORY_LEAKAGE) || \
                defined (DEBUG_MEMORY_LEAKAGE_ON_EXIT)
            free_everything ();
            omapi_print_dmalloc_usage_by_caller (); 
#endif
		exit (0);
	}
#endif
	if (shutdown_state == shutdown_dhcp &&
	    !failover_connection_count) {
		shutdown_state = shutdown_done;
		shutdown_time = cur_time;
		goto oncemore;
	}
	add_timeout (cur_time + 1,
		     (void (*)(void *))dhcp_io_shutdown_countdown, 0, 0, 0);
	return ISC_R_SUCCESS;
}

isc_result_t dhcp_set_control_state (control_object_state_t oldstate,
				     control_object_state_t newstate)
{
	if (newstate == server_shutdown) {
		shutdown_time = cur_time;
		shutdown_state = shutdown_listeners;
		dhcp_io_shutdown_countdown (0);
		return ISC_R_SUCCESS;
	}
	return ISC_R_INVALIDARG;
}
