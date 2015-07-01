/* dhcrelay.c

   DHCP/BOOTP Relay Agent. */

/*
 * Copyright (c) 1997-2001 Internet Software Consortium.
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
"$Id: dhcrelay.c,v 1.52 2001/04/19 16:48:53 mellon Exp $ Copyright (c) 1997-2000 Internet Software Consortium.  All rights reserved.\n";
#endif /* not lint */

#include "dhcpd.h"
#include "version.h"

static void usage PROTO ((void));

TIME cur_time;
TIME default_lease_time = 43200; /* 12 hours... */
TIME max_lease_time = 86400; /* 24 hours... */
struct tree_cache *global_options [256];

/* Needed to prevent linking against conflex.c. */
int lexline;
int lexchar;
char *token_line;
char *tlname;

const char *path_dhcrelay_pid = _PATH_DHCRELAY_PID;

int bogus_agent_drops = 0;	/* Packets dropped because agent option
				   field was specified and we're not relaying
				   packets that already have an agent option
				   specified. */
int bogus_giaddr_drops = 0;	/* Packets sent to us to relay back to a
				   client, but with a bogus giaddr. */
int client_packets_relayed = 0;	/* Packets relayed from client to server. */
int server_packet_errors = 0;	/* Errors sending packets to servers. */
int server_packets_relayed = 0;	/* Packets relayed from server to client. */
int client_packet_errors = 0;	/* Errors sending packets to clients. */

int add_agent_options = 0;	/* If nonzero, add relay agent options. */
int drop_agent_mismatches = 0;	/* If nonzero, drop server replies that
				   don't contain a Relay Agent Information
				   option whose Agent ID suboption matches
				   our giaddr. */
int corrupt_agent_options = 0;	/* Number of packets dropped because
				   relay agent information option was bad. */
int missing_agent_option = 0;	/* Number of packets dropped because no
				   RAI option matching our ID was found. */
int bad_circuit_id = 0;		/* Circuit ID option in matching RAI option
				   did not match any known circuit ID. */
int missing_circuit_id = 0;	/* Circuit ID option in matching RAI option
				   was missing. */

	/* Maximum size of a packet with agent options added. */
int dhcp_max_agent_option_packet_length = 576;

	/* What to do about packets we're asked to relay that
	   already have a relay option: */
enum { forward_and_append,	/* Forward and append our own relay option. */
       forward_and_replace,	/* Forward, but replace theirs with ours. */
       forward_untouched,	/* Forward without changes. */
       discard } agent_relay_mode = forward_and_replace;

u_int16_t local_port;
u_int16_t remote_port;

struct server_list {
	struct server_list *next;
	struct sockaddr_in to;
} *servers;

static char copyright [] = "Copyright 1997-2000 Internet Software Consortium.";
static char arr [] = "All rights reserved.";
static char message [] = "Internet Software Consortium DHCP Relay Agent";
static char url [] = "For info, please visit http://www.isc.org/products/DHCP";

int main (argc, argv, envp)
	int argc;
	char **argv, **envp;
{
	int i;
	struct servent *ent;
	struct server_list *sp = (struct server_list *)0;
	int no_daemon = 0;
	int quiet = 0;
	isc_result_t status;
	char *s;

	/* Make sure we have stdin, stdout and stderr. */
	i = open ("/dev/null", O_RDWR);
	if (i == 0)
		i = open ("/dev/null", O_RDWR);
	if (i == 1) {
		i = open ("/dev/null", O_RDWR);
		log_perror = 0; /* No sense logging to /dev/null. */
	} else if (i != -1)
		close (i);

#ifdef SYSLOG_4_2
	openlog ("dhcrelay", LOG_NDELAY);
	log_priority = LOG_DAEMON;
#else
	openlog ("dhcrelay", LOG_NDELAY, LOG_DAEMON);
#endif

#if !(defined (DEBUG) || defined (SYSLOG_4_2))
	setlogmask (LOG_UPTO (LOG_INFO));
#endif	

	/* Set up the OMAPI. */
	status = omapi_init ();
	if (status != ISC_R_SUCCESS)
		log_fatal ("Can't initialize OMAPI: %s",
			   isc_result_totext (status));

	/* Set up the OMAPI wrappers for the interface object. */
	interface_setup ();

	for (i = 1; i < argc; i++) {
		if (!strcmp (argv [i], "-p")) {
			if (++i == argc)
				usage ();
			local_port = htons (atoi (argv [i]));
			log_debug ("binding to user-specified port %d",
			       ntohs (local_port));
		} else if (!strcmp (argv [i], "-d")) {
			no_daemon = 1;
 		} else if (!strcmp (argv [i], "-i")) {
			struct interface_info *tmp =
				(struct interface_info *)0;
			status = interface_allocate (&tmp, MDL);
			if (status != ISC_R_SUCCESS)
				log_fatal ("%s: interface_allocate: %s",
					   argv [i],
					   isc_result_totext (status));
			if (++i == argc) {
				usage ();
			}
			strcpy (tmp -> name, argv [i]);
			interface_snorf (tmp, INTERFACE_REQUESTED);
			interface_dereference (&tmp, MDL);
		} else if (!strcmp (argv [i], "-q")) {
			quiet = 1;
			quiet_interface_discovery = 1;
		} else if (!strcmp (argv [i], "-a")) {
			add_agent_options = 1;
		} else if (!strcmp (argv [i], "-A")) {
			if (++i == argc)
				usage ();
			dhcp_max_agent_option_packet_length = atoi (argv [i]);
		} else if (!strcmp (argv [i], "-m")) {
			if (++i == argc)
				usage ();
			if (!strcasecmp (argv [i], "append")) {
				agent_relay_mode = forward_and_append;
			} else if (!strcasecmp (argv [i], "replace")) {
				agent_relay_mode = forward_and_replace;
			} else if (!strcasecmp (argv [i], "forward")) {
				agent_relay_mode = forward_untouched;
			} else if (!strcasecmp (argv [i], "discard")) {
				agent_relay_mode = discard;
			} else
				usage ();
		} else if (!strcmp (argv [i], "-D")) {
			drop_agent_mismatches = 1;
 		} else if (argv [i][0] == '-') {
 		    usage ();
		} else if (!strcmp (argv [i], "--version")) {
			log_info ("isc-dhcrelay-%s", DHCP_VERSION);
			exit (0);
 		} else {
			struct hostent *he;
			struct in_addr ia, *iap = (struct in_addr *)0;
			if (inet_aton (argv [i], &ia)) {
				iap = &ia;
			} else {
				he = gethostbyname (argv [i]);
				if (!he) {
					log_error ("%s: host unknown",
						   argv [i]);
				} else {
					iap = ((struct in_addr *)
					       he -> h_addr_list [0]);
				}
			}
			if (iap) {
				sp = ((struct server_list *)
				      dmalloc (sizeof *sp, MDL));
				if (!sp)
					log_fatal ("no memory for server.\n");
				sp -> next = servers;
				servers = sp;
				memcpy (&sp -> to.sin_addr,
					iap, sizeof *iap);
			}
 		}
	}

	if ((s = getenv ("PATH_DHCRELAY_PID"))) {
		path_dhcrelay_pid = s;
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

	/* Default to the DHCP/BOOTP port. */
	if (!local_port) {
		ent = getservbyname ("dhcps", "udp");
		if (!ent)
			local_port = htons (67);
		else
			local_port = ent -> s_port;
		endservent ();
	}
	remote_port = htons (ntohs (local_port) + 1);
  
	/* We need at least one server. */
	if (!sp) {
		usage ();
	}

	/* Set up the server sockaddrs. */
	for (sp = servers; sp; sp = sp -> next) {
		sp -> to.sin_port = local_port;
		sp -> to.sin_family = AF_INET;
#ifdef HAVE_SA_LEN
		sp -> to.sin_len = sizeof sp -> to;
#endif
	}

	/* Get the current time... */
	GET_TIME (&cur_time);

	/* Discover all the network interfaces. */
	discover_interfaces (DISCOVER_RELAY);

	/* Set up the bootp packet handler... */
	bootp_packet_handler = relay;

	/* Become a daemon... */
	if (!no_daemon) {
		int pid;
		FILE *pf;
		int pfdesc;

		log_perror = 0;

		if ((pid = fork()) < 0)
			log_fatal ("can't fork daemon: %m");
		else if (pid)
			exit (0);

		pfdesc = open (path_dhcrelay_pid,
			       O_CREAT | O_TRUNC | O_WRONLY, 0644);

		if (pfdesc < 0) {
			log_error ("Can't create %s: %m", path_dhcrelay_pid);
		} else {
			pf = fdopen (pfdesc, "w");
			if (!pf)
				log_error ("Can't fdopen %s: %m",
				      path_dhcrelay_pid);
			else {
				fprintf (pf, "%ld\n", (long)getpid ());
				fclose (pf);
			}	
		}

		close (0);
		close (1);
		close (2);
		pid = setsid ();
	}

	/* Start dispatching packets and timeouts... */
	dispatch ();

	/*NOTREACHED*/
	return 0;
}

void relay (ip, packet, length, from_port, from, hfrom)
	struct interface_info *ip;
	struct dhcp_packet *packet;
	unsigned length;
	unsigned int from_port;
	struct iaddr from;
	struct hardware *hfrom;
{
	struct server_list *sp;
	struct sockaddr_in to;
	struct interface_info *out;
	struct hardware hto;

	if (packet -> hlen > sizeof packet -> chaddr) {
		log_info ("Discarding packet with invalid hlen.");
		return;
	}

	/* Find the interface that corresponds to the giaddr
	   in the packet. */
	if (packet -> giaddr.s_addr) {
		for (out = interfaces; out; out = out -> next) {
			if (!memcmp (&out -> primary_address,
				     &packet -> giaddr,
				     sizeof packet -> giaddr))
				break;
		}
	} else {
		out = (struct interface_info *)0;
	}

	/* If it's a bootreply, forward it to the client. */
	if (packet -> op == BOOTREPLY) {
		if (!(packet -> flags & htons (BOOTP_BROADCAST)) &&
			can_unicast_without_arp (out)) {
			to.sin_addr = packet -> yiaddr;
			to.sin_port = remote_port;
		} else {
			to.sin_addr.s_addr = htonl (INADDR_BROADCAST);
			to.sin_port = remote_port;
		}
		to.sin_family = AF_INET;
#ifdef HAVE_SA_LEN
		to.sin_len = sizeof to;
#endif

		memcpy (&hto.hbuf [1], packet -> chaddr, packet -> hlen);
		hto.hbuf [0] = packet -> htype;
		hto.hlen = packet -> hlen + 1;

		/* Wipe out the agent relay options and, if possible, figure
		   out which interface to use based on the contents of the
		   option that we put on the request to which the server is
		   replying. */
		if (!(length =
		      strip_relay_agent_options (ip, &out, packet, length)))
			return;

		if (!out) {
			log_error ("packet to bogus giaddr %s.\n",
			      inet_ntoa (packet -> giaddr));
			++bogus_giaddr_drops;
			return;
		}

		if (send_packet (out,
				 (struct packet *)0,
				 packet, length, out -> primary_address,
				 &to, &hto) < 0) {
			++server_packet_errors;
		} else {
			log_debug ("forwarded BOOTREPLY for %s to %s",
			       print_hw_addr (packet -> htype, packet -> hlen,
					      packet -> chaddr),
			       inet_ntoa (to.sin_addr));

			++server_packets_relayed;
		}
		return;
	}

	/* If giaddr matches one of our addresses, ignore the packet -
	   we just sent it. */
	if (out)
		return;

	/* Add relay agent options if indicated.   If something goes wrong,
	   drop the packet. */
	if (!(length = add_relay_agent_options (ip, packet, length,
						ip -> primary_address)))
		return;

	/* If giaddr is not already set, Set it so the server can
	   figure out what net it's from and so that we can later
	   forward the response to the correct net.    If it's already
	   set, the response will be sent directly to the relay agent
	   that set giaddr, so we won't see it. */
	if (!packet -> giaddr.s_addr)
		packet -> giaddr = ip -> primary_address;

	/* Otherwise, it's a BOOTREQUEST, so forward it to all the
	   servers. */
	for (sp = servers; sp; sp = sp -> next) {
		if (send_packet ((fallback_interface
				  ? fallback_interface : interfaces),
				 (struct packet *)0,
				 packet, length, ip -> primary_address,
				 &sp -> to, (struct hardware *)0) < 0) {
			++client_packet_errors;
		} else {
			log_debug ("forwarded BOOTREQUEST for %s to %s",
			       print_hw_addr (packet -> htype, packet -> hlen,
					      packet -> chaddr),
			       inet_ntoa (sp -> to.sin_addr));
			++client_packets_relayed;
		}
	}
				 
}

static void usage ()
{
	log_fatal ("Usage: dhcrelay [-p <port>] [-d] [-D] [-i %s%s%s",
	       "interface]\n                ",
	       "[-q] [-a] [-A length] [-m append|replace|forward|discard]\n",
	       "                [server1 [... serverN]]");
}

int write_lease (lease)
	struct lease *lease;
{
	return 1;
}

int write_host (host)
	struct host_decl *host;
{
	return 1;
}

int commit_leases ()
{
	return 1;
}

void bootp (packet)
	struct packet *packet;
{
}

void dhcp (packet)
	struct packet *packet;
{
}

int find_subnet (struct subnet **sp,
		 struct iaddr addr, const char *file, int line)
{
	return 0;
}

#if defined (DEBUG)
int check_collection (struct packet *p, struct lease *l,
		      struct collection *c)
{
	return 0;
}

void classify (struct packet *p, struct class *c)
{
}

isc_result_t find_class (struct class **class, const char *c1,
			 const char *c2, int i)
{
	return ISC_R_NOTFOUND;
}

int parse_allow_deny (struct option_cache **oc, struct parse *p, int i)
{
	return 0;
}

#endif

/* Strip any Relay Agent Information options from the DHCP packet
   option buffer.   If an RAI option is found whose Agent ID matches
   the giaddr (i.e., ours), try to look up the outgoing interface
   based on the circuit ID suboption. */

int strip_relay_agent_options (in, out, packet, length)
	struct interface_info *in, **out;
	struct dhcp_packet *packet;
	unsigned length;
{
	int is_dhcp = 0;
	u_int8_t *op, *sp, *max;
	int good_agent_option = 0;
	int status;

	/* If we're not adding agent options to packets, we're not taking
	   them out either. */
	if (!add_agent_options)
		return length;

	/* If there's no cookie, it's a bootp packet, so we should just
	   forward it unchanged. */
	if (memcmp (packet -> options, DHCP_OPTIONS_COOKIE, 4))
		return length;

	max = ((u_int8_t *)packet) + length;
	sp = op = &packet -> options [4];

	while (op < max) {
		switch (*op) {
			/* Skip padding... */
		      case DHO_PAD:
			if (sp != op)
				*sp = *op;
			++op;
			++sp;
			continue;

			/* If we see a message type, it's a DHCP packet. */
		      case DHO_DHCP_MESSAGE_TYPE:
			is_dhcp = 1;
			goto skip;
			break;

			/* Quit immediately if we hit an End option. */
		      case DHO_END:
			if (sp != op)
				*sp++ = *op++;
			goto out;

		      case DHO_DHCP_AGENT_OPTIONS:
			/* We shouldn't see a relay agent option in a
			   packet before we've seen the DHCP packet type,
			   but if we do, we have to leave it alone. */
			if (!is_dhcp)
				goto skip;

			status = find_interface_by_agent_option (packet,
								 out, op + 2,
								 op [1]);
			if (status == -1 && drop_agent_mismatches)
				return 0;
			if (status)
				good_agent_option = 1;
			op += op [1] + 2;
			break;

		      skip:
			/* Skip over other options. */
		      default:
			if (sp != op)
				memcpy (sp, op, (unsigned)(op [1] + 2));
			sp += op [1] + 2;
			op += op [1] + 2;
			break;
		}
	}
      out:

	/* If it's not a DHCP packet, we're not supposed to touch it. */
	if (!is_dhcp)
		return length;

	/* If none of the agent options we found matched, or if we didn't
	   find any agent options, count this packet as not having any
	   matching agent options, and if we're relying on agent options
	   to determine the outgoing interface, drop the packet. */

	if (!good_agent_option) {
		++missing_agent_option;
		if (drop_agent_mismatches)
			return 0;
	}

	/* Adjust the length... */
	if (sp != op) {
		length = sp - ((u_int8_t *)packet);

		/* Make sure the packet isn't short (this is unlikely,
                   but WTH) */
		if (length < BOOTP_MIN_LEN) {
			memset (sp, 0, BOOTP_MIN_LEN - length);
			length = BOOTP_MIN_LEN;
		}
	}
	return length;
}


/* Find an interface that matches the circuit ID specified in the
   Relay Agent Information option.   If one is found, store it through
   the pointer given; otherwise, leave the existing pointer alone.

   We actually deviate somewhat from the current specification here:
   if the option buffer is corrupt, we suggest that the caller not
   respond to this packet.  If the circuit ID doesn't match any known
   interface, we suggest that the caller to drop the packet.  Only if
   we find a circuit ID that matches an existing interface do we tell
   the caller to go ahead and process the packet. */

int find_interface_by_agent_option (packet, out, buf, len)
	struct dhcp_packet *packet;
	struct interface_info **out;
	u_int8_t *buf;
	int len;
{
	int i = 0;
	u_int8_t *circuit_id = 0;
	unsigned circuit_id_len;
	struct interface_info *ip;

	while (i < len) {
		/* If the next agent option overflows the end of the
		   packet, the agent option buffer is corrupt. */
		if (i + 1 == len ||
		    i + buf [i + 1] + 2 > len) {
			++corrupt_agent_options;
			return -1;
		}
		switch (buf [i]) {
			/* Remember where the circuit ID is... */
		      case RAI_CIRCUIT_ID:
			circuit_id = &buf [i + 2];
			circuit_id_len = buf [i + 1];
			i += circuit_id_len + 2;
			continue;

		      default:
			i += buf [i + 1] + 2;
			break;
		}
	}

	/* If there's no circuit ID, it's not really ours, tell the caller
	   it's no good. */
	if (!circuit_id) {
		++missing_circuit_id;
		return -1;
	}

	/* Scan the interface list looking for an interface whose
	   name matches the one specified in circuit_id. */

	for (ip = interfaces; ip; ip = ip -> next) {
		if (ip -> circuit_id &&
		    ip -> circuit_id_len == circuit_id_len &&
		    !memcmp (ip -> circuit_id, circuit_id, circuit_id_len))
			break;
	}

	/* If we got a match, use it. */
	if (ip) {
		*out = ip;
		return 1;
	}

	/* If we didn't get a match, the circuit ID was bogus. */
	++bad_circuit_id;
	return -1;
}

/* Examine a packet to see if it's a candidate to have a Relay
   Agent Information option tacked onto its tail.   If it is, tack
   the option on.  */

int add_relay_agent_options (ip, packet, length, giaddr)
	struct interface_info *ip;
	struct dhcp_packet *packet;
	unsigned length;
	struct in_addr giaddr;
{
	int is_dhcp = 0, agent_options_present = 0;
	u_int8_t *op, *sp, *max, *end_pad = 0;

	/* If we're not adding agent options to packets, we can skip
	   this. */
	if (!add_agent_options)
		return length;

	/* If there's no cookie, it's a bootp packet, so we should just
	   forward it unchanged. */
	if (memcmp (packet -> options, DHCP_OPTIONS_COOKIE, 4))
		return length;

	max = ((u_int8_t *)packet) + length;
	sp = op = &packet -> options [4];

	while (op < max) {
		switch (*op) {
			/* Skip padding... */
		      case DHO_PAD:
			end_pad = sp;
			if (sp != op)
				*sp = *op;
			++op;
			++sp;
			continue;

			/* If we see a message type, it's a DHCP packet. */
		      case DHO_DHCP_MESSAGE_TYPE:
			is_dhcp = 1;
			goto skip;
			break;

			/* Quit immediately if we hit an End option. */
		      case DHO_END:
			goto out;

		      case DHO_DHCP_AGENT_OPTIONS:
			/* We shouldn't see a relay agent option in a
			   packet before we've seen the DHCP packet type,
			   but if we do, we have to leave it alone. */
			if (!is_dhcp)
				goto skip;
			end_pad = 0;

			/* There's already a Relay Agent Information option
			   in this packet.   How embarrassing.   Decide what
			   to do based on the mode the user specified. */

			switch (agent_relay_mode) {
			      case forward_and_append:
				goto skip;
			      case forward_untouched:
				return length;
			      case discard:
				return 0;
			      case forward_and_replace:
			      default:
				break;
			}

			/* Skip over the agent option and start copying
			   if we aren't copying already. */
			op += op [1] + 2;
			break;

		      skip:
			/* Skip over other options. */
		      default:
			end_pad = 0;
			if (sp != op)
				memcpy (sp, op, (unsigned)(op [1] + 2));
			sp += op [1] + 2;
			op += op [1] + 2;
			break;
		}
	}
      out:

	/* If it's not a DHCP packet, we're not supposed to touch it. */
	if (!is_dhcp)
		return length;

	/* If the packet was padded out, we can store the agent option
	   at the beginning of the padding. */

	if (end_pad)
		sp = end_pad;

	/* Remember where the end of the packet was after parsing
	   it. */
	op = sp;

	/* XXX Is there room? */

	/* Okay, cons up *our* Relay Agent Information option. */
	*sp++ = DHO_DHCP_AGENT_OPTIONS;
	*sp++ = 0;	/* Dunno... */

	/* Copy in the circuit id... */
	*sp++ = RAI_CIRCUIT_ID;
	/* Sanity check.   Had better not every happen. */
	if (ip -> circuit_id_len > 255 || ip -> circuit_id_len < 1)
		log_fatal ("completely bogus circuit id length %d on %s\n",
		       ip -> circuit_id_len, ip -> name);
	*sp++ = ip -> circuit_id_len;
	memcpy (sp, ip -> circuit_id, ip -> circuit_id_len);
	sp += ip -> circuit_id_len;

	/* Copy in remote ID... */
	if (ip -> remote_id) {
		*sp++ = RAI_REMOTE_ID;
		if (ip -> remote_id_len > 255 || ip -> remote_id_len < 1)
			log_fatal ("bogus remote id length %d on %s\n",
			       ip -> circuit_id_len, ip -> name);
		*sp++ = ip -> remote_id_len;
		memcpy (sp, ip -> remote_id, ip -> remote_id_len);
		sp += ip -> remote_id_len;
	}

	/* Relay option's total length shouldn't ever get to be more than
	   257 bytes. */
	if (sp - op > 257)
	    log_fatal ("total agent option length exceeds 257 (%ld) on %s\n",
		       (long)(sp - op), ip -> name);

	/* Calculate length of RAI option. */
	op [1] = sp - op - 2;

	/* Deposit an END token. */
	*sp++ = DHO_END;

	/* Recalculate total packet length. */
	length = sp - ((u_int8_t *)packet);

	/* Make sure the packet isn't short (this is unlikely, but WTH) */
	if (length < BOOTP_MIN_LEN) {
		memset (sp, 0, BOOTP_MIN_LEN - length);
		length = BOOTP_MIN_LEN;
	}

	return length;
}
