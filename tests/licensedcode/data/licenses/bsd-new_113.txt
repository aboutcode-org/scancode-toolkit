/* bootp.c

   BOOTP Protocol support. */

/*
 * Copyright (c) 1995-2001 Internet Software Consortium.
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
 * 3. Neither the name of The Internet Software Consortium nor the names
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
static char copyright[] =
"$Id: bootp.c,v 1.69.2.3 2001/06/22 01:49:49 mellon Exp $ Copyright (c) 1995-2000 The Internet Software Consortium.  All rights reserved.\n";
#endif /* not lint */

#include "dhcpd.h"

#if defined (TRACING)
# define send_packet trace_packet_send
#endif

void bootp (packet)
	struct packet *packet;
{
	int result;
	struct host_decl *hp = (struct host_decl *)0;
	struct host_decl *host = (struct host_decl *)0;
	struct packet outgoing;
	struct dhcp_packet raw;
	struct sockaddr_in to;
	struct in_addr from;
	struct hardware hto;
	struct option_state *options = (struct option_state *)0;
	struct subnet *subnet;
	struct lease *lease;
	struct iaddr ip_address;
	unsigned i;
	struct data_string d1;
	struct option_cache *oc;
	char msgbuf [1024];
	int ignorep;
	int peer_has_leases = 0;

	if (packet -> raw -> op != BOOTREQUEST)
		return;

	sprintf (msgbuf, "BOOTREQUEST from %s via %s",
		 print_hw_addr (packet -> raw -> htype,
				packet -> raw -> hlen,
				packet -> raw -> chaddr),
		 packet -> raw -> giaddr.s_addr
		 ? inet_ntoa (packet -> raw -> giaddr)
		 : packet -> interface -> name);



	if (!locate_network (packet)) {
		log_info ("%s: network unknown", msgbuf);
		return;
	}

	find_hosts_by_haddr (&hp, packet -> raw -> htype,
			     packet -> raw -> chaddr,
			     packet -> raw -> hlen, MDL);

	lease  = (struct lease *)0;
	find_lease (&lease, packet, packet -> shared_network,
		    0, 0, (struct lease *)0, MDL);

	/* Find an IP address in the host_decl that matches the
	   specified network. */
	subnet = (struct subnet *)0;
	if (hp)
		find_host_for_network (&subnet, &hp, &ip_address,
				       packet -> shared_network);

	if (!subnet) {
		struct host_decl *h;
		/* We didn't find an applicable host declaration.
		   Just in case we may be able to dynamically assign
		   an address, see if there's a host declaration
		   that doesn't have an ip address associated with it. */
		for (h = hp; h; h = h -> n_ipaddr) {
			if (!h -> fixed_addr) {
				host_reference (&host, h, MDL);
				break;
			}
		}
		if (hp) {
			host_dereference (&hp, MDL);
			if (host)
				host_reference (&hp, host, MDL);
		}			

		/* If a lease has already been assigned to this client,
		   use it. */
		if (lease) {
			if (host && host != lease -> host) {
				if (lease -> host)
					host_dereference (&lease -> host, MDL);
				host_reference (&lease -> host, host, MDL);
			}
			ack_lease (packet, lease, 0, 0, msgbuf, 0);
			goto out;
		}

		/* Otherwise, try to allocate one. */
		allocate_lease (&lease, packet,
				packet -> shared_network -> pools,
				&peer_has_leases);
		if (lease) {
			if (host && host != lease -> host) {
				if (lease -> host)
					host_dereference (&lease -> host, MDL);
				host_reference (&lease -> host, host, MDL);
			} else if (lease -> host)
				host_dereference (&lease -> host, MDL);
			ack_lease (packet, lease, 0, 0, msgbuf, 0);
			goto out;
		}
		/* XXX just ignore BOOTREQUESTS from unknown clients if
		   XXX we can't allocate IP addresses for them. */
#if 0
		log_info ("%s: no available leases", msgbuf);
#endif
		goto out;
	}

	/* Run the executable statements to compute the client and server
	   options. */
	option_state_allocate (&options, MDL);
	
	/* Execute the subnet statements. */
	execute_statements_in_scope ((struct binding_value **)0,
				     packet, lease, (struct client_state *)0,
				     packet -> options, options,
				     &lease -> scope, lease -> subnet -> group,
				     (struct group *)0);
	
	/* Execute statements from class scopes. */
	for (i = packet -> class_count; i > 0; i--) {
		execute_statements_in_scope
			((struct binding_value **)0,
			 packet, lease, (struct client_state *)0,
			 packet -> options, options,
			 &lease -> scope, packet -> classes [i - 1] -> group,
			 lease -> subnet -> group);
	}

	/* Execute the host statements. */
	execute_statements_in_scope ((struct binding_value **)0,
				     packet, lease, (struct client_state *)0,
				     packet -> options, options,
				     &lease -> scope,
				     hp -> group, subnet -> group);
	
	/* Drop the request if it's not allowed for this client. */
	if ((oc = lookup_option (&server_universe, options, SV_ALLOW_BOOTP)) &&
	    !evaluate_boolean_option_cache (&ignorep, packet, lease,
					    (struct client_state *)0,
					    packet -> options, options,
					    &lease -> scope, oc, MDL)) {
		if (!ignorep)
			log_info ("%s: bootp disallowed", msgbuf);
		goto out;
	} 

	if ((oc = lookup_option (&server_universe,
				 options, SV_ALLOW_BOOTING)) &&
	    !evaluate_boolean_option_cache (&ignorep, packet, lease,
					    (struct client_state *)0,
					    packet -> options, options,
					    &lease -> scope, oc, MDL)) {
		if (!ignorep)
			log_info ("%s: booting disallowed", msgbuf);
		goto out;
	}

	/* Set up the outgoing packet... */
	memset (&outgoing, 0, sizeof outgoing);
	memset (&raw, 0, sizeof raw);
	outgoing.raw = &raw;

	/* If we didn't get a known vendor magic number on the way in,
	   just copy the input options to the output. */
	if (!packet -> options_valid &&
	    !(evaluate_boolean_option_cache
	      (&ignorep, packet, lease, (struct client_state *)0,
	       packet -> options, options, &lease -> scope,
	       lookup_option (&server_universe, options,
			      SV_ALWAYS_REPLY_RFC1048), MDL))) {
		memcpy (outgoing.raw -> options,
			packet -> raw -> options, DHCP_OPTION_LEN);
		outgoing.packet_length = BOOTP_MIN_LEN;
	} else {

		/* Use the subnet mask from the subnet declaration if no other
		   mask has been provided. */

		oc = (struct option_cache *)0;
		i = DHO_SUBNET_MASK;
		if (!lookup_option (&dhcp_universe, options, i)) {
			if (option_cache_allocate (&oc, MDL)) {
				if (make_const_data
				    (&oc -> expression,
				     lease -> subnet -> netmask.iabuf,
				     lease -> subnet -> netmask.len,
				     0, 0, MDL)) {
					oc -> option =
						dhcp_universe.options [i];
					save_option (&dhcp_universe,
						     options, oc);
				}
				option_cache_dereference (&oc, MDL);
			}
		}

		/* Pack the options into the buffer.  Unlike DHCP, we
		   can't pack options into the filename and server
		   name buffers. */

		outgoing.packet_length =
			cons_options (packet, outgoing.raw, lease,
				      (struct client_state *)0, 0,
				      packet -> options, options,
				      &lease -> scope,
				      0, 0, 1, (struct data_string *)0,
				      (const char *)0);
		if (outgoing.packet_length < BOOTP_MIN_LEN)
			outgoing.packet_length = BOOTP_MIN_LEN;
	}

	/* Take the fields that we care about... */
	raw.op = BOOTREPLY;
	raw.htype = packet -> raw -> htype;
	raw.hlen = packet -> raw -> hlen;
	memcpy (raw.chaddr, packet -> raw -> chaddr, sizeof raw.chaddr);
	raw.hops = packet -> raw -> hops;
	raw.xid = packet -> raw -> xid;
	raw.secs = packet -> raw -> secs;
	raw.flags = packet -> raw -> flags;
	raw.ciaddr = packet -> raw -> ciaddr;
	memcpy (&raw.yiaddr, ip_address.iabuf, sizeof raw.yiaddr);

	/* If we're always supposed to broadcast to this client, set
	   the broadcast bit in the bootp flags field. */
	if ((oc = lookup_option (&server_universe,
				options, SV_ALWAYS_BROADCAST)) &&
	    evaluate_boolean_option_cache (&ignorep, packet, lease,
					   (struct client_state *)0,
					   packet -> options, options,
					   &lease -> scope, oc, MDL))
		raw.flags |= htons (BOOTP_BROADCAST);

	/* Figure out the address of the next server. */
	memset (&d1, 0, sizeof d1);
	oc = lookup_option (&server_universe, options, SV_NEXT_SERVER);
	if (oc &&
	    evaluate_option_cache (&d1, packet, lease,
				   (struct client_state *)0,
				   packet -> options, options,
				   &lease -> scope, oc, MDL)) {
		/* If there was more than one answer, take the first. */
		if (d1.len >= 4 && d1.data)
			memcpy (&raw.siaddr, d1.data, 4);
		data_string_forget (&d1, MDL);
	} else {
		if (lease -> subnet -> shared_network -> interface)
			raw.siaddr = (lease -> subnet -> shared_network ->
				      interface -> primary_address);
		else
			raw.siaddr = packet -> interface -> primary_address;
	}

	raw.giaddr = packet -> raw -> giaddr;

	/* Figure out the filename. */
	oc = lookup_option (&server_universe, options, SV_FILENAME);
	if (oc &&
	    evaluate_option_cache (&d1, packet, lease,
				   (struct client_state *)0,
				   packet -> options, options,
				   &lease -> scope, oc, MDL)) {
		memcpy (raw.file, d1.data,
			d1.len > sizeof raw.file ? sizeof raw.file : d1.len);
		if (sizeof raw.file > d1.len)
			memset (&raw.file [d1.len],
				0, (sizeof raw.file) - d1.len);
		data_string_forget (&d1, MDL);
	} else
		memcpy (raw.file, packet -> raw -> file, sizeof raw.file);

	/* Choose a server name as above. */
	oc = lookup_option (&server_universe, options, SV_SERVER_NAME);
	if (oc &&
	    evaluate_option_cache (&d1, packet, lease,
				   (struct client_state *)0,
				   packet -> options, options,
				   &lease -> scope, oc, MDL)) {
		memcpy (raw.sname, d1.data,
			d1.len > sizeof raw.sname ? sizeof raw.sname : d1.len);
		if (sizeof raw.sname > d1.len)
			memset (&raw.sname [d1.len],
				0, (sizeof raw.sname) - d1.len);
		data_string_forget (&d1, MDL);
	}

	/* Execute the commit statements, if there are any. */
	execute_statements ((struct binding_value **)0,
			    packet, lease, (struct client_state *)0,
			    packet -> options,
			    options, &lease -> scope, lease -> on_commit);

	/* We're done with the option state. */
	option_state_dereference (&options, MDL);

	/* Set up the hardware destination address... */
	hto.hbuf [0] = packet -> raw -> htype;
	hto.hlen = packet -> raw -> hlen + 1;
	memcpy (&hto.hbuf [1], packet -> raw -> chaddr, packet -> raw -> hlen);

	from = packet -> interface -> primary_address;

	/* Report what we're doing... */
	log_info ("%s", msgbuf);
	log_info ("BOOTREPLY for %s to %s (%s) via %s",
	      piaddr (ip_address), hp -> name,
	      print_hw_addr (packet -> raw -> htype,
			     packet -> raw -> hlen,
			     packet -> raw -> chaddr),
	      packet -> raw -> giaddr.s_addr
	      ? inet_ntoa (packet -> raw -> giaddr)
	      : packet -> interface -> name);

	/* Set up the parts of the address that are in common. */
	to.sin_family = AF_INET;
#ifdef HAVE_SA_LEN
	to.sin_len = sizeof to;
#endif
	memset (to.sin_zero, 0, sizeof to.sin_zero);

	/* If this was gatewayed, send it back to the gateway... */
	if (raw.giaddr.s_addr) {
		to.sin_addr = raw.giaddr;
		to.sin_port = local_port;

		if (fallback_interface) {
			result = send_packet (fallback_interface,
					      (struct packet *)0,
					      &raw, outgoing.packet_length,
					      from, &to, &hto);
			goto out;
		}

	/* If it comes from a client that already knows its address
	   and is not requesting a broadcast response, and we can
	   unicast to a client without using the ARP protocol, sent it
	   directly to that client. */
	} else if (!(raw.flags & htons (BOOTP_BROADCAST)) &&
		   can_unicast_without_arp (packet -> interface)) {
		to.sin_addr = raw.yiaddr;
		to.sin_port = remote_port;

	/* Otherwise, broadcast it on the local network. */
	} else {
		to.sin_addr = limited_broadcast;
		to.sin_port = remote_port; /* XXX */
	}

	errno = 0;
	result = send_packet (packet -> interface,
			      packet, &raw, outgoing.packet_length,
			      from, &to, &hto);
      out:
	if (options)
		option_state_dereference (&options, MDL);
	if (lease)
		lease_dereference (&lease, MDL);
	if (hp)
		host_dereference (&hp, MDL);
	if (host)
		host_dereference (&host, MDL);
	if (subnet)
		subnet_dereference (&subnet, MDL);
}
