/* dhcp.c

   DHCP Protocol engine. */

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
"$Id: dhcp.c,v 1.192.2.15 2001/10/04 22:21:00 mellon Exp $ Copyright (c) 1995-2001 The Internet Software Consortium.  All rights reserved.\n";
#endif /* not lint */

#include "dhcpd.h"

int outstanding_pings;

static char dhcp_message [256];

static const char *dhcp_type_names [] = { 
	"DHCPDISCOVER",
	"DHCPOFFER",
	"DHCPREQUEST",
	"DHCPDECLINE",
	"DHCPACK",
	"DHCPNAK",
	"DHCPRELEASE",
	"DHCPINFORM"
};
const int dhcp_type_name_max = ((sizeof dhcp_type_names) / sizeof (char *));

#if defined (TRACING)
# define send_packet trace_packet_send
#endif

void dhcp (packet)
	struct packet *packet;
{
	int ms_nulltp = 0;
	struct option_cache *oc;
	struct lease *lease = (struct lease *)0;
	const char *errmsg;
	struct data_string data;

	if (!locate_network (packet) &&
	    packet -> packet_type != DHCPREQUEST &&
	    packet -> packet_type != DHCPINFORM) {
		const char *s;
		char typebuf [32];
		errmsg = "unknown network segment";
	      bad_packet:
		
		if (packet -> packet_type > 0 &&
		    packet -> packet_type < dhcp_type_name_max - 1) {
			s = dhcp_type_names [packet -> packet_type - 1];
		} else {
#if defined (HAVE_SNPRINTF)
			snprintf (typebuf, sizeof typebuf,
				  "type %d", packet -> packet_type);
#else
			sprintf (typebuf, 
				  "type %d", packet -> packet_type);
#endif
			s = typebuf;
		}
		
		log_info ("%s from %s via %s: %s", s,
			  (packet -> raw -> htype
			   ? print_hw_addr (packet -> raw -> htype,
					    packet -> raw -> hlen,
					    packet -> raw -> chaddr)
			   : "<no identifier>"),
			  packet -> raw -> giaddr.s_addr
			  ? inet_ntoa (packet -> raw -> giaddr)
			  : packet -> interface -> name, errmsg);
		goto out;
	}

	/* There is a problem with the relay agent information option,
	   which is that in order for a normal relay agent to append
	   this option, the relay agent has to have been involved in
	   getting the packet from the client to the server.  Note
	   that this is the software entity known as the relay agent,
	   _not_ the hardware entity known as a router in which the
	   relay agent may be running, so the fact that a router has
	   forwarded a packet does not mean that the relay agent in
	   the router was involved.

	   So when the client is in INIT or INIT-REBOOT or REBINDING
	   state, the relay agent gets to tack on its options, but
	   when it's not, the relay agent doesn't get to do this,
	   which means that any decisions the DHCP server may make
	   based on the agent options will be made incorrectly.  

	   We work around this in the following way: if this is a
	   DHCPREQUEST and doesn't have relay agent information
	   options, we see if there's an existing lease for this IP
	   address and this client that _does_ have stashed agent
	   options.   If so, then we tack those options onto the
	   packet as if they came from the client.   Later on, when we
	   are deciding whether to steal the agent options from the
	   packet, if the agent options stashed on the lease are the
	   same as those stashed on the packet, we don't steal them -
	   this ensures that the client never receives its agent
	   options. */

	if (packet -> packet_type == DHCPREQUEST &&
	    packet -> raw -> ciaddr.s_addr &&
	    !packet -> raw -> giaddr.s_addr &&
	    (packet -> options -> universe_count < agent_universe.index ||
	     !packet -> options -> universes [agent_universe.index]))
	{
		struct iaddr cip;

		cip.len = sizeof packet -> raw -> ciaddr;
		memcpy (cip.iabuf, &packet -> raw -> ciaddr,
			sizeof packet -> raw -> ciaddr);
		if (!find_lease_by_ip_addr (&lease, cip, MDL))
			goto nolease;

		/* If there are no agent options on the lease, it's not
		   interesting. */
		if (!lease -> agent_options)
			goto nolease;

		/* The client should not be unicasting a renewal if its lease
		   has expired, so make it go through the process of getting
		   its agent options legally. */
		if (lease -> ends < cur_time)
			goto nolease;

		if (lease -> uid_len) {
			oc = lookup_option (&dhcp_universe, packet -> options,
					    DHO_DHCP_CLIENT_IDENTIFIER);
			if (!oc)
				goto nolease;

			memset (&data, 0, sizeof data);
			if (!evaluate_option_cache (&data,
						    packet, (struct lease *)0,
						    (struct client_state *)0,
						    packet -> options,
						    (struct option_state *)0,
						    &global_scope, oc, MDL))
				goto nolease;
			if (lease -> uid_len != data.len ||
			    memcmp (lease -> uid, data.data, data.len)) {
				data_string_forget (&data, MDL);
				goto nolease;
			}
			data_string_forget (&data, MDL);
		} else
			if ((lease -> hardware_addr.hbuf [0] !=
			     packet -> raw -> htype) ||
			    (lease -> hardware_addr.hlen - 1 !=
			     packet -> raw -> hlen) ||
			    memcmp (&lease -> hardware_addr.hbuf [1],
				    packet -> raw -> chaddr,
				    packet -> raw -> hlen))
				goto nolease;

		/* Okay, so we found a lease that matches the client. */
		option_chain_head_reference ((struct option_chain_head **)
					     &(packet -> options -> universes
					       [agent_universe.index]),
					     lease -> agent_options, MDL);
	}
      nolease:

	/* Classify the client. */
	if ((oc = lookup_option (&dhcp_universe, packet -> options,
				 DHO_HOST_NAME))) {
		if (!oc -> expression)
			if (oc -> data.len &&
			    oc -> data.data [oc -> data.len - 1] == 0) {
				ms_nulltp = 1;
				oc -> data.len--;
			}
	}

	classify_client (packet);

	switch (packet -> packet_type) {
	      case DHCPDISCOVER:
		dhcpdiscover (packet, ms_nulltp);
		break;

	      case DHCPREQUEST:
		dhcprequest (packet, ms_nulltp, lease);
		break;

	      case DHCPRELEASE:
		dhcprelease (packet, ms_nulltp);
		break;

	      case DHCPDECLINE:
		dhcpdecline (packet, ms_nulltp);
		break;

	      case DHCPINFORM:
		dhcpinform (packet, ms_nulltp);
		break;


	      case DHCPACK:
	      case DHCPOFFER:
	      case DHCPNAK:
		break;

	      default:
		errmsg = "unknown packet type";
		goto bad_packet;
	}
      out:
	if (lease)
		lease_dereference (&lease, MDL);
}

void dhcpdiscover (packet, ms_nulltp)
	struct packet *packet;
	int ms_nulltp;
{
	struct lease *lease = (struct lease *)0;
	char msgbuf [1024]; /* XXX */
	TIME when;
	char *s;
	int allocatedp = 0;
	int peer_has_leases = 0;
#if defined (FAILOVER_PROTOCOL)
	dhcp_failover_state_t *peer;
#endif

	find_lease (&lease, packet, packet -> shared_network,
		    0, &allocatedp, (struct lease *)0, MDL);

	if (lease && lease -> client_hostname &&
	    db_printable (lease -> client_hostname))
		s = lease -> client_hostname;
	else
		s = (char *)0;

	/* Say what we're doing... */
	sprintf (msgbuf, "DHCPDISCOVER from %s %s%s%svia %s",
		 (packet -> raw -> htype
		  ? print_hw_addr (packet -> raw -> htype,
				   packet -> raw -> hlen,
				   packet -> raw -> chaddr)
		  : (lease
		     ? print_hex_1 (lease -> uid_len, lease -> uid, 
				    lease -> uid_len)
		     : "<no identifier>")),
		  s ? "(" : "", s ? s : "", s ? ") " : "",
		  packet -> raw -> giaddr.s_addr
		  ? inet_ntoa (packet -> raw -> giaddr)
		  : packet -> interface -> name);

	/* Sourceless packets don't make sense here. */
	if (!packet -> shared_network) {
		log_info ("Packet from unknown subnet: %s",
		      inet_ntoa (packet -> raw -> giaddr));
		goto out;
	}

#if defined (FAILOVER_PROTOCOL)
	if (lease && lease -> pool && lease -> pool -> failover_peer) {
		peer = lease -> pool -> failover_peer;

		/* If the lease is ours to allocate, then allocate it,
		   but set the allocatedp flag. */
		if (lease_mine_to_reallocate (lease))
			allocatedp = 1;

		/* If the lease is active, do load balancing to see who
		   allocates the lease (if it's active, it already belongs
		   to the client, or we wouldn't have gotten it from
		   find_lease (). */
		else if (lease -> binding_state == FTS_ACTIVE &&
			 (peer -> service_state != cooperating ||
			  load_balance_mine (packet, peer)))
			;

		/* Otherwise, we can't let the client have this lease. */
		else {
#if defined (DEBUG_FIND_LEASE)
		    log_debug ("discarding %s - %s",
			       piaddr (lease -> ip_addr),
			       binding_state_print (lease -> binding_state));
#endif
		    lease_dereference (&lease, MDL);
		}
	}
#endif

	/* If we didn't find a lease, try to allocate one... */
	if (!lease) {
		if (!allocate_lease (&lease, packet,
				     packet -> shared_network -> pools, 
				     &peer_has_leases)) {
			if (peer_has_leases)
				log_error ("%s: peer holds all free leases",
					   msgbuf);
			else
				log_error ("%s: network %s: no free leases",
					   msgbuf,
					   packet -> shared_network -> name);
			return;
		}
#if defined (FAILOVER_PROTOCOL)
		if (lease -> pool && lease -> pool -> failover_peer)
			dhcp_failover_pool_check (lease -> pool);
#endif
		allocatedp = 1;
	}

#if defined (FAILOVER_PROTOCOL)
	if (lease && lease -> pool && lease -> pool -> failover_peer) {
		peer = lease -> pool -> failover_peer;
		if (peer -> service_state == not_responding ||
		    peer -> service_state == service_startup) {
			log_info ("%s: not responding%s",
				  msgbuf, peer -> nrr);
			goto out;
		}
	} else
		peer = (dhcp_failover_state_t *)0;

	/* Do load balancing if configured. */
	/* If the lease is newly allocated, and we're not the server that
	   the client would normally get with load balancing, and the
	   failover protocol state is normal, let the other server get this.
	   XXX Check protocol spec to make sure that predicating this on
	   XXX allocatedp is okay - I'm doing this so that the client won't
	   XXX be forced to switch servers (and IP addresses) just because
	   XXX of bad luck, when it's possible for it to get the address it
	   XXX is requesting.    Not sure this is allowed.  */
	if (allocatedp && peer) {
		if (peer -> service_state == cooperating) {
			if (!load_balance_mine (packet, peer)) {
				log_debug ("%s: load balance to peer %s",
					   msgbuf, peer -> name);
				goto out;
			}
		}
	}
#endif

	/* If it's an expired lease, get rid of any bindings. */
	if (lease -> ends < cur_time && lease -> scope)
		binding_scope_dereference (&lease -> scope, MDL);

	/* Set the lease to really expire in 2 minutes, unless it has
	   not yet expired, in which case leave its expiry time alone. */
	when = cur_time + 120;
	if (when < lease -> ends)
		when = lease -> ends;

	ack_lease (packet, lease, DHCPOFFER, when, msgbuf, ms_nulltp);
      out:
	if (lease)
		lease_dereference (&lease, MDL);
}

void dhcprequest (packet, ms_nulltp, ip_lease)
	struct packet *packet;
	int ms_nulltp;
	struct lease *ip_lease;
{
	struct lease *lease;
	struct iaddr cip;
	struct iaddr sip;
	struct subnet *subnet;
	int ours = 0;
	struct option_cache *oc;
	struct data_string data;
	int status;
	char msgbuf [1024]; /* XXX */
	char *s;
	char smbuf [19];
#if defined (FAILOVER_PROTOCOL)
	dhcp_failover_state_t *peer;
#endif
	int have_server_identifier = 0;
	int have_requested_addr = 0;

	oc = lookup_option (&dhcp_universe, packet -> options,
			    DHO_DHCP_REQUESTED_ADDRESS);
	memset (&data, 0, sizeof data);
	if (oc &&
	    evaluate_option_cache (&data, packet, (struct lease *)0,
				   (struct client_state *)0,
				   packet -> options, (struct option_state *)0,
				   &global_scope, oc, MDL)) {
		cip.len = 4;
		memcpy (cip.iabuf, data.data, 4);
		data_string_forget (&data, MDL);
		have_requested_addr = 1;
	} else {
		oc = (struct option_cache *)0;
		cip.len = 4;
		memcpy (cip.iabuf, &packet -> raw -> ciaddr.s_addr, 4);
	}

	/* Find the lease that matches the address requested by the
	   client. */

	subnet = (struct subnet *)0;
	lease = (struct lease *)0;
	if (find_subnet (&subnet, cip, MDL))
		find_lease (&lease, packet,
			    subnet -> shared_network, &ours, 0, ip_lease, MDL);
	/* XXX consider using allocatedp arg to find_lease to see
	   XXX that this isn't a compliant DHCPREQUEST. */

	if (lease && lease -> client_hostname &&
	    db_printable (lease -> client_hostname))
		s = lease -> client_hostname;
	else
		s = (char *)0;

	oc = lookup_option (&dhcp_universe, packet -> options,
			    DHO_DHCP_SERVER_IDENTIFIER);
	memset (&data, 0, sizeof data);
	if (oc &&
	    evaluate_option_cache (&data, packet, (struct lease *)0,
				   (struct client_state *)0,
				   packet -> options, (struct option_state *)0,
				   &global_scope, oc, MDL)) {
		sip.len = 4;
		memcpy (sip.iabuf, data.data, 4);
		data_string_forget (&data, MDL);
		sprintf (smbuf, " (%s)", piaddr (sip));
		have_server_identifier = 1;
	} else
		smbuf [0] = 0;

	/* Say what we're doing... */
	sprintf (msgbuf, "DHCPREQUEST for %s%s from %s %s%s%svia %s",
		 piaddr (cip), smbuf,
		 (packet -> raw -> htype
		  ? print_hw_addr (packet -> raw -> htype,
				   packet -> raw -> hlen,
				   packet -> raw -> chaddr)
		  : (lease
		     ? print_hex_1 (lease -> uid_len, lease -> uid, 
				    lease -> uid_len)
		     : "<no identifier>")),
		 s ? "(" : "", s ? s : "", s ? ") " : "",
		  packet -> raw -> giaddr.s_addr
		  ? inet_ntoa (packet -> raw -> giaddr)
		  : packet -> interface -> name);

#if defined (FAILOVER_PROTOCOL)
	if (lease && lease -> pool && lease -> pool -> failover_peer) {
		peer = lease -> pool -> failover_peer;
		if (peer -> service_state == not_responding ||
		    peer -> service_state == service_startup) {
			log_info ("%s: not responding%s",
				  msgbuf, peer -> nrr);
			goto out;
		}
		/* Don't load balance if the client is RENEWING or REBINDING.
		   If it's RENEWING, we are the only server to hear it, so
		   we have to serve it.   If it's REBINDING, it's out of
		   communication with the other server, so there's no point
		   in waiting to serve it.    However, if the lease we're
		   offering is not a free lease, then we may be the only
		   server that can offer it, so we can't load balance if
		   the lease isn't in the free or backup state. */
		if (peer -> service_state == cooperating &&
		    !packet -> raw -> ciaddr.s_addr &&
		    (lease -> binding_state == FTS_FREE ||
		     lease -> binding_state == FTS_BACKUP)) {
			if (!load_balance_mine (packet, peer)) {
				log_debug ("%s: load balance to peer %s",
					   msgbuf, peer -> name);
				goto out;
			}
		}

		/* Don't let a client allocate a lease using DHCPREQUEST
		   if the lease isn't ours to allocate. */
		if ((lease -> binding_state == FTS_FREE ||
		     lease -> binding_state == FTS_BACKUP) &&
		    !lease_mine_to_reallocate (lease)) {
			log_debug ("%s: lease owned by peer", msgbuf);
			goto out;
		}

		/* At this point it's possible that we will get a broadcast
		   DHCPREQUEST for a lease that we didn't offer, because
		   both we and the peer are in a position to offer it.
		   In that case, we probably shouldn't answer.   In order
		   to not answer, we would have to compare the server
		   identifier sent by the client with the list of possible
		   server identifiers we can send, and if the client's
		   identifier isn't on the list, drop the DHCPREQUEST.
		   We aren't currently doing that for two reasons - first,
		   it's not clear that all clients do the right thing
		   with respect to sending the client identifier, which
		   could mean that we might simply not respond to a client
		   that is depending on us to respond.   Secondly, we allow
		   the user to specify the server identifier to send, and
		   we don't enforce that the server identifier should be
		   one of our IP addresses.   This is probably not a big
		   deal, but it's theoretically an issue.

		   The reason we care about this is that if both servers
		   send a DHCPACK to the DHCPREQUEST, they are then going
		   to send dueling BNDUPD messages, which could cause
		   trouble.   I think it causes no harm, but it seems
		   wrong. */
	} else
		peer = (dhcp_failover_state_t *)0;
#endif

	/* If a client on a given network REQUESTs a lease on an
	   address on a different network, NAK it.  If the Requested
	   Address option was used, the protocol says that it must
	   have been broadcast, so we can trust the source network
	   information.

	   If ciaddr was specified and Requested Address was not, then
	   we really only know for sure what network a packet came from
	   if it came through a BOOTP gateway - if it came through an
	   IP router, we'll just have to assume that it's cool.

	   If we don't think we know where the packet came from, it
	   came through a gateway from an unknown network, so it's not
	   from a RENEWING client.  If we recognize the network it
	   *thinks* it's on, we can NAK it even though we don't
	   recognize the network it's *actually* on; otherwise we just
	   have to ignore it.

	   We don't currently try to take advantage of access to the
	   raw packet, because it's not available on all platforms.
	   So a packet that was unicast to us through a router from a
	   RENEWING client is going to look exactly like a packet that
	   was broadcast to us from an INIT-REBOOT client.

	   Since we can't tell the difference between these two kinds
	   of packets, if the packet appears to have come in off the
	   local wire, we have to treat it as if it's a RENEWING
	   client.  This means that we can't NAK a RENEWING client on
	   the local wire that has a bogus address.  The good news is
	   that we won't ACK it either, so it should revert to INIT
	   state and send us a DHCPDISCOVER, which we *can* work with.

	   Because we can't detect that a RENEWING client is on the
	   wrong wire, it's going to sit there trying to renew until
	   it gets to the REBIND state, when we *can* NAK it because
	   the packet will get to us through a BOOTP gateway.  We
	   shouldn't actually see DHCPREQUEST packets from RENEWING
	   clients on the wrong wire anyway, since their idea of their
	   local router will be wrong.  In any case, the protocol
	   doesn't really allow us to NAK a DHCPREQUEST from a
	   RENEWING client, so we can punt on this issue. */

	if (!packet -> shared_network ||
	    (packet -> raw -> ciaddr.s_addr &&
	     packet -> raw -> giaddr.s_addr) ||
	    (have_requested_addr && !packet -> raw -> ciaddr.s_addr)) {
		
		/* If we don't know where it came from but we do know
		   where it claims to have come from, it didn't come
		   from there. */
		if (!packet -> shared_network) {
			if (subnet && subnet -> group -> authoritative) {
				log_info ("%s: wrong network.", msgbuf);
				nak_lease (packet, &cip);
				goto out;
			}
			/* Otherwise, ignore it. */
			log_info ("%s: ignored (%s).", msgbuf,
				  (subnet
				   ? "not authoritative" : "unknown subnet"));
			goto out;
		}

		/* If we do know where it came from and it asked for an
		   address that is not on that shared network, nak it. */
		if (subnet)
			subnet_dereference (&subnet, MDL);
		if (!find_grouped_subnet (&subnet, packet -> shared_network,
					  cip, MDL)) {
			if (packet -> shared_network -> group -> authoritative)
			{
				log_info ("%s: wrong network.", msgbuf);
				nak_lease (packet, &cip);
				goto out;
			}
			log_info ("%s: ignored (not authoritative).", msgbuf);
			return;
		}
	}

	/* If the address the client asked for is ours, but it wasn't
           available for the client, NAK it. */
	if (!lease && ours) {
		log_info ("%s: lease %s unavailable.", msgbuf, piaddr (cip));
		nak_lease (packet, &cip);
		goto out;
	}

	/* Otherwise, send the lease to the client if we found one. */
	if (lease) {
		ack_lease (packet, lease, DHCPACK, 0, msgbuf, ms_nulltp);
	} else
		log_info ("%s: unknown lease %s.", msgbuf, piaddr (cip));

      out:
	if (subnet)
		subnet_dereference (&subnet, MDL);
	if (lease)
		lease_dereference (&lease, MDL);
	return;
}

void dhcprelease (packet, ms_nulltp)
	struct packet *packet;
	int ms_nulltp;
{
	struct lease *lease = (struct lease *)0, *next = (struct lease *)0;
	struct iaddr cip;
	struct option_cache *oc;
	struct data_string data;
	char *s;
	char msgbuf [1024]; /* XXX */


	/* DHCPRELEASE must not specify address in requested-address
           option, but old protocol specs weren't explicit about this,
           so let it go. */
	if ((oc = lookup_option (&dhcp_universe, packet -> options,
				 DHO_DHCP_REQUESTED_ADDRESS))) {
		log_info ("DHCPRELEASE from %s specified requested-address.",
		      print_hw_addr (packet -> raw -> htype,
				     packet -> raw -> hlen,
				     packet -> raw -> chaddr));
	}

	oc = lookup_option (&dhcp_universe, packet -> options,
			    DHO_DHCP_CLIENT_IDENTIFIER);
	memset (&data, 0, sizeof data);
	if (oc &&
	    evaluate_option_cache (&data, packet, (struct lease *)0,
				   (struct client_state *)0,
				   packet -> options, (struct option_state *)0,
				   &global_scope, oc, MDL)) {
		find_lease_by_uid (&lease, data.data, data.len, MDL);
		data_string_forget (&data, MDL);

		/* See if we can find a lease that matches the IP address
		   the client is claiming. */
		while (lease) {
			if (lease -> n_uid)
				lease_reference (&next, lease -> n_uid, MDL);
			if (!memcmp (&packet -> raw -> ciaddr,
				     lease -> ip_addr.iabuf, 4)) {
				break;
			}
			lease_dereference (&lease, MDL);
			if (next) {
				lease_reference (&lease, next, MDL);
				lease_dereference (&next, MDL);
			}
		}
		if (next)
			lease_dereference (&next, MDL);
	}

	/* The client is supposed to pass a valid client-identifier,
	   but the spec on this has changed historically, so try the
	   IP address in ciaddr if the client-identifier fails. */
	if (!lease) {
		cip.len = 4;
		memcpy (cip.iabuf, &packet -> raw -> ciaddr, 4);
		find_lease_by_ip_addr (&lease, cip, MDL);
	}


	if (lease && lease -> client_hostname &&
	    db_printable (lease -> client_hostname))
		s = lease -> client_hostname;
	else
		s = (char *)0;

	/* Say what we're doing... */
	sprintf (msgbuf,
		 "DHCPRELEASE of %s from %s %s%s%svia %s (%sfound)",
		 inet_ntoa (packet -> raw -> ciaddr),
		 (packet -> raw -> htype
		  ? print_hw_addr (packet -> raw -> htype,
				   packet -> raw -> hlen,
				   packet -> raw -> chaddr)
		  : (lease
		     ? print_hex_1 (lease -> uid_len, lease -> uid, 
				    lease -> uid_len)
		     : "<no identifier>")),
		 s ? "(" : "", s ? s : "", s ? ") " : "",
		 packet -> raw -> giaddr.s_addr
		 ? inet_ntoa (packet -> raw -> giaddr)
		 : packet -> interface -> name,
		 lease ? "" : "not ");

#if defined (FAILOVER_PROTOCOL)
	if (lease && lease -> pool && lease -> pool -> failover_peer) {
		dhcp_failover_state_t *peer = lease -> pool -> failover_peer;
		if (peer -> service_state == not_responding ||
		    peer -> service_state == service_startup) {
			log_info ("%s: ignored%s",
				  peer -> name, peer -> nrr);
			goto out;
		}

		/* DHCPRELEASE messages are unicast, so if the client
		   sent the DHCPRELEASE to us, it's not going to send it
		   to the peer.   Not sure why this would happen, and
		   if it does happen I think we still have to change the
		   lease state, so that's what we're doing.
		   XXX See what it says in the draft about this. */
	}
#endif

	/* If we found a lease, release it. */
	if (lease && lease -> ends > cur_time) {
		release_lease (lease, packet);
	} 
	log_info ("%s", msgbuf);
      out:
	if (lease)
		lease_dereference (&lease, MDL);
}

void dhcpdecline (packet, ms_nulltp)
	struct packet *packet;
	int ms_nulltp;
{
	struct lease *lease = (struct lease *)0;
	struct option_state *options = (struct option_state *)0;
	int ignorep = 0;
	int i;
	const char *status;
	char *s;
	char msgbuf [1024]; /* XXX */
	struct iaddr cip;
	struct option_cache *oc;
	struct data_string data;

	/* DHCPDECLINE must specify address. */
	if (!(oc = lookup_option (&dhcp_universe, packet -> options,
				  DHO_DHCP_REQUESTED_ADDRESS)))
		return;
	memset (&data, 0, sizeof data);
	if (!evaluate_option_cache (&data, packet, (struct lease *)0,
				    (struct client_state *)0,
				    packet -> options,
				    (struct option_state *)0,
				    &global_scope, oc, MDL))
		return;

	cip.len = 4;
	memcpy (cip.iabuf, data.data, 4);
	data_string_forget (&data, MDL);
	find_lease_by_ip_addr (&lease, cip, MDL);

	if (lease && lease -> client_hostname &&
	    db_printable (lease -> client_hostname))
		s = lease -> client_hostname;
	else
		s = (char *)0;

	sprintf (msgbuf, "DHCPDECLINE of %s from %s %s%s%svia %s",
		 piaddr (cip),
		 (packet -> raw -> htype
		  ? print_hw_addr (packet -> raw -> htype,
				   packet -> raw -> hlen,
				   packet -> raw -> chaddr)
		  : (lease
		     ? print_hex_1 (lease -> uid_len, lease -> uid, 
				    lease -> uid_len)
		     : "<no identifier>")),
		 s ? "(" : "", s ? s : "", s ? ") " : "",
		 packet -> raw -> giaddr.s_addr
		 ? inet_ntoa (packet -> raw -> giaddr)
		 : packet -> interface -> name);

	option_state_allocate (&options, MDL);

	/* Execute statements in scope starting with the subnet scope. */
	if (lease)
		execute_statements_in_scope ((struct binding_value **)0,
					     packet, (struct lease *)0,
					     (struct client_state *)0,
					     packet -> options, options,
					     &global_scope,
					     lease -> subnet -> group,
					     (struct group *)0);

	/* Execute statements in the class scopes. */
	for (i = packet -> class_count; i > 0; i--) {
		execute_statements_in_scope
			((struct binding_value **)0, packet, (struct lease *)0,
			 (struct client_state *)0, packet -> options, options,
			 &global_scope, packet -> classes [i - 1] -> group,
			 lease ? lease -> subnet -> group : (struct group *)0);
	}

	/* Drop the request if dhcpdeclines are being ignored. */
	oc = lookup_option (&server_universe, options, SV_DECLINES);
	if (!oc ||
	    evaluate_boolean_option_cache (&ignorep, packet, lease,
					   (struct client_state *)0,
					   packet -> options, options,
					   &lease -> scope, oc, MDL)) {
	    /* If we found a lease, mark it as unusable and complain. */
	    if (lease) {
#if defined (FAILOVER_PROTOCOL)
		if (lease -> pool && lease -> pool -> failover_peer) {
		    dhcp_failover_state_t *peer =
			    lease -> pool -> failover_peer;
		    if (peer -> service_state == not_responding ||
			peer -> service_state == service_startup) {
			if (!ignorep)
			    log_info ("%s: ignored%s",
				      peer -> name, peer -> nrr);
			goto out;
		    }

		    /* DHCPDECLINE messages are broadcast, so we can safely
		       ignore the DHCPDECLINE if the peer has the lease.
		       XXX Of course, at this point that information has been
		       lost. */
		}
#endif

		abandon_lease (lease, "declined.");
		status = "abandoned";
	    }
	    status = "not found";
	} else
	    status = "ignored";

	if (!ignorep)
		log_info ("%s: %s", msgbuf, status);
		
      out:
	if (options)
		option_state_dereference (&options, MDL);
	if (lease)
		lease_dereference (&lease, MDL);
}

void dhcpinform (packet, ms_nulltp)
	struct packet *packet;
	int ms_nulltp;
{
	char msgbuf [1024];
	struct data_string d1, prl;
	struct option_cache *oc;
	struct expression *expr;
	struct option_state *options = (struct option_state *)0;
	struct dhcp_packet raw;
	struct packet outgoing;
	unsigned char dhcpack = DHCPACK;
	struct subnet *subnet = (struct subnet *)0;
	struct iaddr cip;
	unsigned i, j;
	int nulltp;
	struct sockaddr_in to;
	struct in_addr from;

	/* The client should set ciaddr to its IP address, but apparently
	   it's common for clients not to do this, so we'll use their IP
	   source address if they didn't set ciaddr. */
	if (!packet -> raw -> ciaddr.s_addr) {
		cip.len = 4;
		memcpy (cip.iabuf, &packet -> client_addr, 4);
	} else {
		cip.len = 4;
		memcpy (cip.iabuf, &packet -> raw -> ciaddr, 4);
	}

	sprintf (msgbuf, "DHCPINFORM from %s via %s",
		 piaddr (cip), packet -> interface -> name);

	/* If the IP source address is zero, don't respond. */
	if (!memcmp (cip.iabuf, "\0\0\0", 4)) {
		log_info ("%s: ignored (null source address).", msgbuf);
		return;
	}

	/* Find the subnet that the client is on. */
	oc = (struct option_cache *)0;
	find_subnet (&subnet , cip, MDL);

	/* Sourceless packets don't make sense here. */
	if (!subnet) {
		log_info ("%s: unknown subnet %s",
			  msgbuf, inet_ntoa (packet -> raw -> giaddr));
		return;
	}

	/* We don't respond to DHCPINFORM packets if we're not authoritative.
	   It would be nice if a per-host value could override this, but
	   there's overhead involved in checking this, so let's see how people
	   react first. */
	if (subnet && !subnet -> group -> authoritative) {
		static int eso = 0;
		log_info ("%s: not authoritative for subnet %s",
			  msgbuf, piaddr (subnet -> net));
		if (!eso) {
			log_info ("If this DHCP server is authoritative for%s",
				  " that subnet,");
			log_info ("please write an `authoritative;' directi%s",
				  "ve either in the");
			log_info ("subnet declaration or in some scope that%s",
				  "encloses the");
			log_info ("subnet declaration - for example, write %s",
				  "it at the top");
			log_info ("of the dhcpd.conf file.");
		}
		if (eso++ == 100)
			eso = 0;
		subnet_dereference (&subnet, MDL);
		return;
	}

	memset (&d1, 0, sizeof d1);
	option_state_allocate (&options, MDL);
	memset (&outgoing, 0, sizeof outgoing);
	memset (&raw, 0, sizeof raw);
	outgoing.raw = &raw;

	/* Execute statements in scope starting with the subnet scope. */
	if (subnet)
		execute_statements_in_scope ((struct binding_value **)0,
					     packet, (struct lease *)0,
					     (struct client_state *)0,
					     packet -> options, options,
					     &global_scope, subnet -> group,
					     (struct group *)0);

	/* Execute statements in the class scopes. */
	for (i = packet -> class_count; i > 0; i--) {
		execute_statements_in_scope
			((struct binding_value **)0, packet, (struct lease *)0,
			 (struct client_state *)0, packet -> options, options,
			 &global_scope, packet -> classes [i - 1] -> group,
			 subnet ? subnet -> group : (struct group *)0);
	}

	/* Figure out the filename. */
	memset (&d1, 0, sizeof d1);
	oc = lookup_option (&server_universe, options, SV_FILENAME);
	if (oc &&
	    evaluate_option_cache (&d1, packet, (struct lease *)0,
				   (struct client_state *)0,
				   packet -> options, (struct option_state *)0,
				   &global_scope, oc, MDL)) {
		i = d1.len;
		if (i > sizeof raw.file)
			i = sizeof raw.file;
		else
			raw.file [i] = 0;
		memcpy (raw.file, d1.data, i);
		data_string_forget (&d1, MDL);
	}

	/* Choose a server name as above. */
	oc = lookup_option (&server_universe, options, SV_SERVER_NAME);
	if (oc &&
	    evaluate_option_cache (&d1, packet, (struct lease *)0,
				   (struct client_state *)0,
				   packet -> options, (struct option_state *)0,
				   &global_scope, oc, MDL)) {
		i = d1.len;
		if (i > sizeof raw.sname)
			i = sizeof raw.sname;
		else
			raw.sname [i] = 0;
		memcpy (raw.sname, d1.data, i);
		data_string_forget (&d1, MDL);
	}

	/* Set a flag if this client is a lame Microsoft client that NUL
	   terminates string options and expects us to do likewise. */
	nulltp = 0;
	if ((oc = lookup_option (&dhcp_universe, packet -> options,
				 DHO_HOST_NAME))) {
		if (evaluate_option_cache (&d1, packet, (struct lease *)0,
					   (struct client_state *)0,
					   packet -> options, options,
					   &global_scope, oc, MDL)) {
			if (d1.data [d1.len - 1] == '\0')
				nulltp = 1;
			data_string_forget (&d1, MDL);
		}
	}

	/* Put in DHCP-specific options. */
	i = DHO_DHCP_MESSAGE_TYPE;
	oc = (struct option_cache *)0;
	if (option_cache_allocate (&oc, MDL)) {
		if (make_const_data (&oc -> expression,
				     &dhcpack, 1, 0, 0, MDL)) {
			oc -> option = dhcp_universe.options [i];
			save_option (&dhcp_universe, options, oc);
		}
		option_cache_dereference (&oc, MDL);
	}

	i = DHO_DHCP_SERVER_IDENTIFIER;
	if (!(oc = lookup_option (&dhcp_universe, options, i))) {
	      use_primary:
		oc = (struct option_cache *)0;
		if (option_cache_allocate (&oc, MDL)) {
			if (make_const_data
			    (&oc -> expression,
			     ((unsigned char *)
			      &packet -> interface -> primary_address),
			     sizeof packet -> interface -> primary_address,
			     0, 0, MDL)) {
				oc -> option =
					dhcp_universe.options [i];
				save_option (&dhcp_universe,
					     options, oc);
			}
			option_cache_dereference (&oc, MDL);
		}
		from = packet -> interface -> primary_address;
	} else {
		if (evaluate_option_cache (&d1, packet, (struct lease *)0,
					   (struct client_state *)0,
					   packet -> options, options,
					   &global_scope, oc, MDL)) {
			if (!d1.len || d1.len != sizeof from) {
				data_string_forget (&d1, MDL);
				goto use_primary;
			}
			memcpy (&from, d1.data, sizeof from);
			data_string_forget (&d1, MDL);
		} else
			goto use_primary;
	}

	/* Use the subnet mask from the subnet declaration if no other
	   mask has been provided. */
	i = DHO_SUBNET_MASK;
	if (subnet && !lookup_option (&dhcp_universe, options, i)) {
		oc = (struct option_cache *)0;
		if (option_cache_allocate (&oc, MDL)) {
			if (make_const_data (&oc -> expression,
					     subnet -> netmask.iabuf,
					     subnet -> netmask.len,
					     0, 0, MDL)) {
				oc -> option = dhcp_universe.options [i];
				save_option (&dhcp_universe, options, oc);
			}
			option_cache_dereference (&oc, MDL);
		}
	}

	/* If a site option space has been specified, use that for
	   site option codes. */
	i = SV_SITE_OPTION_SPACE;
	if ((oc = lookup_option (&server_universe, options, i)) &&
	    evaluate_option_cache (&d1, packet, (struct lease *)0,
				   (struct client_state *)0,
				   packet -> options, options,
				   &global_scope, oc, MDL)) {
		struct universe *u = (struct universe *)0;
		
		if (!universe_hash_lookup (&u, universe_hash,
					   (const char *)d1.data, d1.len,
					   MDL)) {
			log_error ("unknown option space %s.", d1.data);
			option_state_dereference (&options, MDL);
			if (subnet)
				subnet_dereference (&subnet, MDL);
			return;
		}

		options -> site_universe = u -> index;
		options -> site_code_min = 128; /* XXX */
		data_string_forget (&d1, MDL);
	} else {
		options -> site_universe = dhcp_universe.index;
		options -> site_code_min = 0; /* Trust me, it works. */
	}

	memset (&prl, 0, sizeof prl);

	/* Use the parameter list from the scope if there is one. */
	oc = lookup_option (&dhcp_universe, options,
			    DHO_DHCP_PARAMETER_REQUEST_LIST);

	/* Otherwise, if the client has provided a list of options
	   that it wishes returned, use it to prioritize.  Otherwise,
	   prioritize based on the default priority list. */

	if (!oc)
		oc = lookup_option (&dhcp_universe, packet -> options,
				    DHO_DHCP_PARAMETER_REQUEST_LIST);

	if (oc)
		evaluate_option_cache (&prl, packet, (struct lease *)0,
				       (struct client_state *)0,
				       packet -> options, options,
				       &global_scope, oc, MDL);

#ifdef DEBUG_PACKET
	dump_packet (packet);
	dump_raw ((unsigned char *)packet -> raw, packet -> packet_length);
#endif

	log_info ("%s", msgbuf);

	/* Figure out the address of the boot file server. */
	raw.siaddr = from;
	if ((oc =
	     lookup_option (&server_universe, options, SV_NEXT_SERVER))) {
		if (evaluate_option_cache (&d1, packet, (struct lease *)0,
					   (struct client_state *)0,
					   packet -> options, options,
					   &global_scope, oc, MDL)) {
			/* If there was more than one answer,
			   take the first. */
			if (d1.len >= 4 && d1.data)
				memcpy (&raw.siaddr, d1.data, 4);
			data_string_forget (&d1, MDL);
		}
	}

	/* Set up the option buffer... */
	outgoing.packet_length =
		cons_options (packet, outgoing.raw, (struct lease *)0,
			      (struct client_state *)0,
			      0, packet -> options, options, &global_scope,
			      0, nulltp, 0,
			      prl.len ? &prl : (struct data_string *)0,
			      (char *)0);
	option_state_dereference (&options, MDL);
	data_string_forget (&prl, MDL);

	/* Make sure that the packet is at least as big as a BOOTP packet. */
	if (outgoing.packet_length < BOOTP_MIN_LEN)
		outgoing.packet_length = BOOTP_MIN_LEN;

	raw.giaddr = packet -> raw -> giaddr;
	raw.ciaddr = packet -> raw -> ciaddr;
	memcpy (raw.chaddr, packet -> raw -> chaddr, sizeof raw.chaddr);
	raw.hlen = packet -> raw -> hlen;
	raw.htype = packet -> raw -> htype;

	raw.xid = packet -> raw -> xid;
	raw.secs = packet -> raw -> secs;
	raw.flags = packet -> raw -> flags;
	raw.hops = packet -> raw -> hops;
	raw.op = BOOTREPLY;

	/* Report what we're sending... */
	log_info ("DHCPACK to %s", inet_ntoa (raw.ciaddr));

#ifdef DEBUG_PACKET
	dump_packet (&outgoing);
	dump_raw ((unsigned char *)&raw, outgoing.packet_length);
#endif

	/* Set up the common stuff... */
	to.sin_family = AF_INET;
#ifdef HAVE_SA_LEN
	to.sin_len = sizeof to;
#endif
	memset (to.sin_zero, 0, sizeof to.sin_zero);

	/* Use the IP address we derived for the client. */
	memcpy (&to.sin_addr, cip.iabuf, 4);
	to.sin_port = remote_port;

	errno = 0;
	send_packet ((fallback_interface
		      ? fallback_interface : packet -> interface),
		     &outgoing, &raw, outgoing.packet_length,
		     from, &to, (struct hardware *)0);
	if (subnet)
		subnet_dereference (&subnet, MDL);
}

void nak_lease (packet, cip)
	struct packet *packet;
	struct iaddr *cip;
{
	struct sockaddr_in to;
	struct in_addr from;
	int result;
	struct dhcp_packet raw;
	unsigned char nak = DHCPNAK;
	struct packet outgoing;
	struct hardware hto;
	unsigned i;
	struct data_string data;
	struct option_state *options = (struct option_state *)0;
	struct expression *expr;
	struct option_cache *oc = (struct option_cache *)0;
	struct iaddr myfrom;

	option_state_allocate (&options, MDL);
	memset (&outgoing, 0, sizeof outgoing);
	memset (&raw, 0, sizeof raw);
	outgoing.raw = &raw;

	/* Set DHCP_MESSAGE_TYPE to DHCPNAK */
	if (!option_cache_allocate (&oc, MDL)) {
		log_error ("No memory for DHCPNAK message type.");
		option_state_dereference (&options, MDL);
		return;
	}
	if (!make_const_data (&oc -> expression, &nak, sizeof nak,
			      0, 0, MDL)) {
		log_error ("No memory for expr_const expression.");
		option_cache_dereference (&oc, MDL);
		option_state_dereference (&options, MDL);
		return;
	}
	oc -> option = dhcp_universe.options [DHO_DHCP_MESSAGE_TYPE];
	save_option (&dhcp_universe, options, oc);
	option_cache_dereference (&oc, MDL);
		     
	/* Set DHCP_MESSAGE to whatever the message is */
	if (!option_cache_allocate (&oc, MDL)) {
		log_error ("No memory for DHCPNAK message type.");
		option_state_dereference (&options, MDL);
		return;
	}
	if (!make_const_data (&oc -> expression,
			      (unsigned char *)dhcp_message,
			      strlen (dhcp_message), 1, 0, MDL)) {
		log_error ("No memory for expr_const expression.");
		option_cache_dereference (&oc, MDL);
		option_state_dereference (&options, MDL);
		return;
	}
	oc -> option = dhcp_universe.options [DHO_DHCP_MESSAGE];
	save_option (&dhcp_universe, options, oc);
	option_cache_dereference (&oc, MDL);
		     
	i = DHO_DHCP_SERVER_IDENTIFIER;
	if (!(oc = lookup_option (&dhcp_universe, options, i))) {
	      use_primary:
		oc = (struct option_cache *)0;
		if (option_cache_allocate (&oc, MDL)) {
			if (make_const_data
			    (&oc -> expression,
			     ((unsigned char *)
			      &packet -> interface -> primary_address),
			     sizeof packet -> interface -> primary_address,
			     0, 0, MDL)) {
				oc -> option =
					dhcp_universe.options [i];
				save_option (&dhcp_universe, options, oc);
			}
			option_cache_dereference (&oc, MDL);
		}
		myfrom.len = sizeof packet -> interface -> primary_address;
		memcpy (myfrom.iabuf,
			&packet -> interface -> primary_address, myfrom.len);
	} else {
		memset (&data, 0, sizeof data);
		if (evaluate_option_cache (&data, packet, (struct lease *)0,
					   (struct client_state *)0,
					   packet -> options, options,
					   &global_scope, oc, MDL)) {
			if (!data.len ||
			    data.len > sizeof myfrom.iabuf) {
				data_string_forget (&data, MDL);
				goto use_primary;
			}
			memcpy (myfrom.iabuf, data.data, data.len);
			myfrom.len = data.len;
			data_string_forget (&data, MDL);
		} else
			goto use_primary;
	}

	/* Do not use the client's requested parameter list. */
	delete_option (&dhcp_universe, packet -> options,
		       DHO_DHCP_PARAMETER_REQUEST_LIST);

	/* Set up the option buffer... */
	outgoing.packet_length =
		cons_options (packet, outgoing.raw, (struct lease *)0,
			      (struct client_state *)0,
			      0, packet -> options, options, &global_scope,
			      0, 0, 0, (struct data_string *)0, (char *)0);
	option_state_dereference (&options, MDL);

/*	memset (&raw.ciaddr, 0, sizeof raw.ciaddr);*/
	raw.siaddr = packet -> interface -> primary_address;
	raw.giaddr = packet -> raw -> giaddr;
	memcpy (raw.chaddr, packet -> raw -> chaddr, sizeof raw.chaddr);
	raw.hlen = packet -> raw -> hlen;
	raw.htype = packet -> raw -> htype;

	raw.xid = packet -> raw -> xid;
	raw.secs = packet -> raw -> secs;
	raw.flags = packet -> raw -> flags | htons (BOOTP_BROADCAST);
	raw.hops = packet -> raw -> hops;
	raw.op = BOOTREPLY;

	/* Report what we're sending... */
	log_info ("DHCPNAK on %s to %s via %s",
	      piaddr (*cip),
	      print_hw_addr (packet -> raw -> htype,
			     packet -> raw -> hlen,
			     packet -> raw -> chaddr),
	      packet -> raw -> giaddr.s_addr
	      ? inet_ntoa (packet -> raw -> giaddr)
	      : packet -> interface -> name);



#ifdef DEBUG_PACKET
	dump_packet (packet);
	dump_raw ((unsigned char *)packet -> raw, packet -> packet_length);
	dump_packet (&outgoing);
	dump_raw ((unsigned char *)&raw, outgoing.packet_length);
#endif

#if 0
	hto.hbuf [0] = packet -> raw -> htype;
	hto.hlen = packet -> raw -> hlen;
	memcpy (&hto.hbuf [1], packet -> raw -> chaddr, hto.hlen);
	hto.hlen++;
#endif

	/* Set up the common stuff... */
	to.sin_family = AF_INET;
#ifdef HAVE_SA_LEN
	to.sin_len = sizeof to;
#endif
	memset (to.sin_zero, 0, sizeof to.sin_zero);

	memcpy (&from, myfrom.iabuf, sizeof from);

	/* Make sure that the packet is at least as big as a BOOTP packet. */
	if (outgoing.packet_length < BOOTP_MIN_LEN)
		outgoing.packet_length = BOOTP_MIN_LEN;

	/* If this was gatewayed, send it back to the gateway.
	   Otherwise, broadcast it on the local network. */
	if (raw.giaddr.s_addr) {
		to.sin_addr = raw.giaddr;
		if (raw.giaddr.s_addr != htonl (INADDR_LOOPBACK))
			to.sin_port = local_port;
		else
			to.sin_port = remote_port; /* for testing. */

		if (fallback_interface) {
			result = send_packet (fallback_interface,
					      packet, &raw,
					      outgoing.packet_length,
					      from, &to, &hto);
			return;
		}
	} else {
		to.sin_addr = limited_broadcast;
		to.sin_port = remote_port;
	}

	errno = 0;
	result = send_packet (packet -> interface,
			      packet, &raw, outgoing.packet_length,
			      from, &to, (struct hardware *)0);
}

void ack_lease (packet, lease, offer, when, msg, ms_nulltp)
	struct packet *packet;
	struct lease *lease;
	unsigned int offer;
	TIME when;
	char *msg;
	int ms_nulltp;
{
	struct lease *lt;
	struct lease_state *state;
	struct lease *next;
	TIME lease_time;
	TIME offered_lease_time;
	struct data_string d1;
	TIME min_lease_time;
	TIME max_lease_time;
	TIME default_lease_time;
	struct option_cache *oc;
	struct expression *expr;
	int status;
	isc_result_t result;
	int did_ping = 0;

	unsigned i, j;
	int s1, s2;
	int val;
	int ignorep;

	/* If we're already acking this lease, don't do it again. */
	if (lease -> state)
		return;

	/* Allocate a lease state structure... */
	state = new_lease_state (MDL);
	if (!state)
		log_fatal ("unable to allocate lease state!");
	state -> got_requested_address = packet -> got_requested_address;
	shared_network_reference (&state -> shared_network,
				  packet -> interface -> shared_network, MDL);

	/* See if we got a server identifier option. */
	if (lookup_option (&dhcp_universe,
			   packet -> options, DHO_DHCP_SERVER_IDENTIFIER))
		state -> got_server_identifier = 1;

	/* If there were agent options in the incoming packet, return
	   them.  Do not return the agent options if they were stashed
	   on the lease. */
	if (packet -> raw -> giaddr.s_addr &&
	    packet -> options -> universe_count > agent_universe.index &&
	    packet -> options -> universes [agent_universe.index] &&
	    (state -> options -> universe_count <= agent_universe.index ||
	     !state -> options -> universes [agent_universe.index]) &&
	    lease -> agent_options !=
	    ((struct option_chain_head *)
	     packet -> options -> universes [agent_universe.index])) {
		option_chain_head_reference
		    ((struct option_chain_head **)
		     &(state -> options -> universes [agent_universe.index]),
		     (struct option_chain_head *)
		     packet -> options -> universes [agent_universe.index],
		     MDL);
	}

	/* If we are offering a lease that is still currently valid, preserve
	   the events.  We need to do this because if the client does not
	   REQUEST our offer, it will expire in 2 minutes, overriding the
	   expire time in the currently in force lease.  We want the expire
	   events to be executed at that point. */
	if (lease -> ends <= cur_time && offer != DHCPOFFER) {
		/* Get rid of any old expiry or release statements - by
		   executing the statements below, we will be inserting new
		   ones if there are any to insert. */
		if (lease -> on_expiry)
			executable_statement_dereference (&lease -> on_expiry,
							  MDL);
		if (lease -> on_commit)
			executable_statement_dereference (&lease -> on_commit,
							  MDL);
		if (lease -> on_release)
			executable_statement_dereference (&lease -> on_release,
							  MDL);
	}

	/* Execute statements in scope starting with the subnet scope. */
	execute_statements_in_scope ((struct binding_value **)0,
				     packet, lease, (struct client_state *)0,
				     packet -> options,
				     state -> options, &lease -> scope,
				     lease -> subnet -> group,
				     (struct group *)0);

	/* If the lease is from a pool, run the pool scope. */
	if (lease -> pool)
		execute_statements_in_scope ((struct binding_value **)0,
					     packet, lease,
					     (struct client_state *)0,
					     packet -> options,
					     state -> options, &lease -> scope,
					     lease -> pool -> group,
					     lease -> subnet -> group);

	/* Execute statements from class scopes. */
	for (i = packet -> class_count; i > 0; i--) {
		execute_statements_in_scope
			((struct binding_value **)0,
			 packet, lease, (struct client_state *)0,
			 packet -> options, state -> options,
			 &lease -> scope, packet -> classes [i - 1] -> group,
			 (lease -> pool
			  ? lease -> pool -> group
			  : lease -> subnet -> group));
	}

	/* If we have a host_decl structure, run the options associated
	   with its group. */
	if (lease -> host)
		execute_statements_in_scope ((struct binding_value **)0,
					     packet, lease,
					     (struct client_state *)0,
					     packet -> options,
					     state -> options, &lease -> scope,
					     lease -> host -> group,
					     (lease -> pool
					      ? lease -> pool -> group
					      : lease -> subnet -> group));
	
	/* See if the client is only supposed to have one lease at a time,
	   and if so, find its other leases and release them.    We can only
	   do this on DHCPREQUEST.    It's a little weird to do this before
	   looking at permissions, because the client might not actually
	   _get_ a lease after we've done the permission check, but the
	   assumption for this option is that the client has exactly one
	   network interface, and will only ever remember one lease.   So
	   if it sends a DHCPREQUEST, and doesn't get the lease, it's already
	   forgotten about its old lease, so we can too. */
	if (packet -> packet_type == DHCPREQUEST &&
	    (oc = lookup_option (&server_universe, state -> options,
				 SV_ONE_LEASE_PER_CLIENT)) &&
	    evaluate_boolean_option_cache (&ignorep,
					   packet, lease,
					   (struct client_state *)0,
					   packet -> options,
					   state -> options, &lease -> scope,
					   oc, MDL)) {
	    struct lease *seek;
	    if (lease -> uid_len) {
		do {
		    seek = (struct lease *)0;
		    find_lease_by_uid (&seek, lease -> uid,
				       lease -> uid_len, MDL);
		    if (!seek)
			break;
		    if (seek == lease && !seek -> n_uid) {
			lease_dereference (&seek, MDL);
			break;
		    }
		    next = (struct lease *)0;

		    /* Don't release expired leases, and don't
		       release the lease we're going to assign. */
		    next = (struct lease *)0;
		    while (seek) {
			if (seek -> n_uid)
			    lease_reference (&next, seek -> n_uid, MDL);
			if (seek != lease &&
			    seek -> binding_state != FTS_RELEASED &&
			    seek -> binding_state != FTS_EXPIRED &&
			    seek -> binding_state != FTS_RESET &&
			    seek -> binding_state != FTS_FREE &&
			    seek -> binding_state != FTS_BACKUP)
				break;
			lease_dereference (&seek, MDL);
			if (next) {
			    lease_reference (&seek, next, MDL);
			    lease_dereference (&next, MDL);
			}
		    }
		    if (next)
			lease_dereference (&next, MDL);
		    if (seek) {
			release_lease (seek, packet);
			lease_dereference (&seek, MDL);
		    } else
			break;
		} while (1);
	    }
	    if (!lease -> uid_len ||
		(lease -> host &&
		 !lease -> host -> client_identifier.len &&
		 (oc = lookup_option (&server_universe, state -> options,
				      SV_DUPLICATES)) &&
		 !evaluate_boolean_option_cache (&ignorep, packet, lease,
						 (struct client_state *)0,
						 packet -> options,
						 state -> options,
						 &lease -> scope,
						 oc, MDL))) {
		do {
		    seek = (struct lease *)0;
		    find_lease_by_hw_addr
			    (&seek, lease -> hardware_addr.hbuf,
			     lease -> hardware_addr.hlen, MDL);
		    if (!seek)
			    break;
		    if (seek == lease && !seek -> n_hw) {
			    lease_dereference (&seek, MDL);
			    break;
		    }
		    next = (struct lease *)0;
		    while (seek) {
			if (seek -> n_hw)
			    lease_reference (&next, seek -> n_hw, MDL);
			if (seek != lease &&
			    seek -> binding_state != FTS_RELEASED &&
			    seek -> binding_state != FTS_EXPIRED &&
			    seek -> binding_state != FTS_RESET &&
			    seek -> binding_state != FTS_FREE &&
			    seek -> binding_state != FTS_BACKUP)
				break;
			lease_dereference (&seek, MDL);
			if (next) {
			    lease_reference (&seek, next, MDL);
			    lease_dereference (&next, MDL);
			}
		    }
		    if (next)
			lease_dereference (&next, MDL);
		    if (seek) {
			release_lease (seek, packet);
			lease_dereference (&seek, MDL);
		    } else
			break;
		} while (1);
	    }
	}
	

	/* Make sure this packet satisfies the configured minimum
	   number of seconds. */
	memset (&d1, 0, sizeof d1);
	if (offer == DHCPOFFER &&
	    (oc = lookup_option (&server_universe, state -> options,
				 SV_MIN_SECS))) {
		if (evaluate_option_cache (&d1, packet, lease,
					   (struct client_state *)0,
					   packet -> options, state -> options,
					   &lease -> scope, oc, MDL)) {
			if (d1.len &&
			    ntohs (packet -> raw -> secs) < d1.data [0]) {
				log_info ("%s: %d secs < %d", msg,
					  ntohs (packet -> raw -> secs),
					  d1.data [0]);
				data_string_forget (&d1, MDL);
				free_lease_state (state, MDL);
				return;
			}
			data_string_forget (&d1, MDL);
		}
	}

	/* Try to find a matching host declaration for this lease. */
	if (!lease -> host) {
		struct host_decl *hp = (struct host_decl *)0;
		struct host_decl *h;

		/* Try to find a host_decl that matches the client
		   identifier or hardware address on the packet, and
		   has no fixed IP address.   If there is one, hang
		   it off the lease so that its option definitions
		   can be used. */
		oc = lookup_option (&dhcp_universe, packet -> options,
				    DHO_DHCP_CLIENT_IDENTIFIER);
		if (oc &&
		    evaluate_option_cache (&d1, packet, lease,
					   (struct client_state *)0,
					   packet -> options, state -> options,
					   &lease -> scope, oc, MDL)) {
			find_hosts_by_uid (&hp, d1.data, d1.len, MDL);
			data_string_forget (&d1, MDL);
			if (hp)
				host_reference (&lease -> host, hp, MDL);
		}
		if (!hp) {
			find_hosts_by_haddr (&hp,
					     packet -> raw -> htype,
					     packet -> raw -> chaddr,
					     packet -> raw -> hlen,
					     MDL);
			for (h = hp; h; h = h -> n_ipaddr) {
				if (!h -> fixed_addr)
					break;
			}
			if (h)
				host_reference (&lease -> host, h, MDL);
		}
		if (hp)
			host_dereference (&hp, MDL);
	}

	/* Drop the request if it's not allowed for this client.   By
	   default, unknown clients are allowed. */
	if (!lease -> host &&
	    (oc = lookup_option (&server_universe, state -> options,
				 SV_BOOT_UNKNOWN_CLIENTS)) &&
	    !evaluate_boolean_option_cache (&ignorep,
					    packet, lease,
					    (struct client_state *)0,
					    packet -> options,
					    state -> options,
					    &lease -> scope, oc, MDL)) {
		if (!ignorep)
			log_info ("%s: unknown client", msg);
		free_lease_state (state, MDL);
		return;
	} 

	/* Drop the request if it's not allowed for this client. */
	if (!offer &&
	    (oc = lookup_option (&server_universe, state -> options,
				   SV_ALLOW_BOOTP)) &&
	    !evaluate_boolean_option_cache (&ignorep,
					    packet, lease,
					    (struct client_state *)0,
					    packet -> options,
					    state -> options,
					    &lease -> scope, oc, MDL)) {
		if (!ignorep)
			log_info ("%s: bootp disallowed", msg);
		free_lease_state (state, MDL);
		return;
	} 

	/* Drop the request if booting is specifically denied. */
	oc = lookup_option (&server_universe, state -> options,
			    SV_ALLOW_BOOTING);
	if (oc &&
	    !evaluate_boolean_option_cache (&ignorep,
					    packet, lease,
					    (struct client_state *)0,
					    packet -> options,
					    state -> options,
					    &lease -> scope, oc, MDL)) {
		if (!ignorep)
			log_info ("%s: booting disallowed", msg);
		free_lease_state (state, MDL);
		return;
	}

	/* If we are configured to do per-class billing, do it. */
	if (have_billing_classes && !(lease -> flags & STATIC_LEASE)) {
		/* See if the lease is currently being billed to a
		   class, and if so, whether or not it can continue to
		   be billed to that class. */
		if (lease -> billing_class) {
			for (i = 0; i < packet -> class_count; i++)
				if (packet -> classes [i] ==
				    lease -> billing_class)
					break;
			if (i == packet -> class_count)
				unbill_class (lease, lease -> billing_class);
		}
		
		/* If we don't have an active billing, see if we need
		   one, and if we do, try to do so. */
		if (!lease -> billing_class) {
			for (i = 0; i < packet -> class_count; i++) {
				if (packet -> classes [i] -> lease_limit)
					break;
			}
			if (i != packet -> class_count) {
				for (i = 0; i < packet -> class_count; i++)
					if ((packet -> 
					     classes [i] -> lease_limit) &&
					    bill_class (lease,
							packet -> classes [i]))
						break;
				if (i == packet -> class_count) {
					log_info ("%s: no available billing",
						  msg);
					free_lease_state (state, MDL);
					/* XXX probably not necessary: */
					return;
				}
			}
		}
	}

	/* Figure out the filename. */
	oc = lookup_option (&server_universe, state -> options, SV_FILENAME);
	if (oc)
		evaluate_option_cache (&state -> filename, packet, lease,
				       (struct client_state *)0,
				       packet -> options, state -> options,
				       &lease -> scope, oc, MDL);

	/* Choose a server name as above. */
	oc = lookup_option (&server_universe, state -> options,
			    SV_SERVER_NAME);
	if (oc)
		evaluate_option_cache (&state -> server_name, packet, lease,
				       (struct client_state *)0,
				       packet -> options, state -> options,
				       &lease -> scope, oc, MDL);

	/* At this point, we have a lease that we can offer the client.
	   Now we construct a lease structure that contains what we want,
	   and call supersede_lease to do the right thing with it. */
	lt = (struct lease *)0;
	result = lease_allocate (&lt, MDL);
	if (result != ISC_R_SUCCESS) {
		log_info ("%s: can't allocate temporary lease structure: %s",
			  msg, isc_result_totext (result));
		free_lease_state (state, MDL);
		return;
	}
		
	/* Use the ip address of the lease that we finally found in
	   the database. */
	lt -> ip_addr = lease -> ip_addr;

	/* Start now. */
	lt -> starts = cur_time;

	/* Figure out how long a lease to assign.    If this is a
	   dynamic BOOTP lease, its duration must be infinite. */
	if (offer) {
		default_lease_time = DEFAULT_DEFAULT_LEASE_TIME;
		if ((oc = lookup_option (&server_universe, state -> options,
					 SV_DEFAULT_LEASE_TIME))) {
			if (evaluate_option_cache (&d1, packet, lease,
						   (struct client_state *)0,
						   packet -> options,
						   state -> options,
						   &lease -> scope, oc, MDL)) {
				if (d1.len == sizeof (u_int32_t))
					default_lease_time =
						getULong (d1.data);
				data_string_forget (&d1, MDL);
			}
		}

		if ((oc = lookup_option (&dhcp_universe, packet -> options,
					 DHO_DHCP_LEASE_TIME)))
			s1 = evaluate_option_cache (&d1, packet, lease,
						    (struct client_state *)0,
						    packet -> options,
						    state -> options,
						    &lease -> scope, oc, MDL);
		else
			s1 = 0;
		if (s1 && d1.len == sizeof (u_int32_t)) {
			lease_time = getULong (d1.data);
			data_string_forget (&d1, MDL);
		} else {
			if (s1)
				data_string_forget (&d1, MDL);
			lease_time = default_lease_time;
		}
		
		/* See if there's a maximum lease time. */
		max_lease_time = DEFAULT_MAX_LEASE_TIME;
		if ((oc = lookup_option (&server_universe, state -> options,
					 SV_MAX_LEASE_TIME))) {
			if (evaluate_option_cache (&d1, packet, lease,
						   (struct client_state *)0,
						   packet -> options,
						   state -> options,
						   &lease -> scope, oc, MDL)) {
				if (d1.len == sizeof (u_int32_t))
					max_lease_time =
						getULong (d1.data);
				data_string_forget (&d1, MDL);
			}
		}

		/* Enforce the maximum lease length. */
		if (lease_time < 0 /* XXX */
		    || lease_time > max_lease_time)
			lease_time = max_lease_time;
			
		min_lease_time = DEFAULT_MIN_LEASE_TIME;
		if (min_lease_time > max_lease_time)
			min_lease_time = max_lease_time;

		if ((oc = lookup_option (&server_universe, state -> options,
					 SV_MIN_LEASE_TIME))) {
			if (evaluate_option_cache (&d1, packet, lease,
						   (struct client_state *)0,
						   packet -> options,
						   state -> options,
						   &lease -> scope, oc, MDL)) {
				if (d1.len == sizeof (u_int32_t))
					min_lease_time = getULong (d1.data);
				data_string_forget (&d1, MDL);
			}
		}

		if (lease_time < min_lease_time) {
			if (min_lease_time)
				lease_time = min_lease_time;
			else
				lease_time = default_lease_time;
		}

#if defined (FAILOVER_PROTOCOL)
		/* Okay, we know the lease duration.   Now check the
		   failover state, if any. */
		if (lease -> pool && lease -> pool -> failover_peer) {
			dhcp_failover_state_t *peer =
			    lease -> pool -> failover_peer;

			/* If the lease time we arrived at exceeds what
			   the peer has, we can only issue a lease of
			   peer -> mclt, but we can tell the peer we
			   want something longer in the future. */
			/* XXX This may result in updates that only push
			   XXX the peer's expiry time for this lease up
			   XXX by a few seconds - think about this again
			   XXX later. */
			if (lease_time > peer -> mclt &&
			    cur_time + lease_time > lease -> tsfp) {
				/* Here we're assuming that if we don't have
				   to update tstp, there's already an update
				   queued.   May want to revisit this.  */
				if (peer -> me.state != partner_down &&
				    cur_time + lease_time > lease -> tstp)
					lt -> tstp = (cur_time + lease_time +
						      peer -> mclt / 2);

				/* Now choose a lease time that is either
				   MCLT, for a lease that's never before been
				   assigned, or TSFP + MCLT for a lease that
				   has.
				   XXX Note that TSFP may be < cur_time.
				   XXX What do we do in this case?
				   XXX should the expiry timer on the lease
				   XXX set tsfp and tstp to zero? */
				if (lease -> tsfp < cur_time) {
					lease_time = peer -> mclt;
				} else {
					lease_time = (lease -> tsfp  - cur_time
						      + peer -> mclt);
				}
			} else {
				if (cur_time + lease_time > lease -> tsfp &&
				    lease_time > peer -> mclt / 2) {
					lt -> tstp = (cur_time + lease_time +
						      peer -> mclt / 2);
				} else { 
					lt -> tstp = (cur_time + lease_time +
						      lease_time / 2);
				}
			}

			lt -> cltt = cur_time;
		}
#endif /* FAILOVER_PROTOCOL */

		/* If the lease duration causes the time value to wrap,
		   use the maximum expiry time. */
		if (cur_time + lease_time < cur_time)
			state -> offered_expiry = MAX_TIME - 1;
		else
			state -> offered_expiry = cur_time + lease_time;
		if (when)
			lt -> ends = when;
		else
			lt -> ends = state -> offered_expiry;

		/* Don't make lease active until we actually get a
		   DHCPREQUEST. */
		if (offer == DHCPACK)
			lt -> next_binding_state = FTS_ACTIVE;
		else
			lt -> next_binding_state = lease -> binding_state;
	} else {
		lease_time = MAX_TIME - cur_time;

		if ((oc = lookup_option (&server_universe, state -> options,
					 SV_BOOTP_LEASE_LENGTH))) {
			if (evaluate_option_cache (&d1, packet, lease,
						   (struct client_state *)0,
						   packet -> options,
						   state -> options,
						   &lease -> scope, oc, MDL)) {
				if (d1.len == sizeof (u_int32_t))
					lease_time = getULong (d1.data);
				data_string_forget (&d1, MDL);
			}
		}

		if ((oc = lookup_option (&server_universe, state -> options,
					 SV_BOOTP_LEASE_CUTOFF))) {
			if (evaluate_option_cache (&d1, packet, lease,
						   (struct client_state *)0,
						   packet -> options,
						   state -> options,
						   &lease -> scope, oc, MDL)) {
				if (d1.len == sizeof (u_int32_t))
					lease_time = (getULong (d1.data) -
						      cur_time);
				data_string_forget (&d1, MDL);
			}
		}

		lt -> ends = state -> offered_expiry = cur_time + lease_time;
		lt -> next_binding_state = FTS_BOOTP;
	}

	lt -> timestamp = cur_time;

	/* Record the uid, if given... */
	oc = lookup_option (&dhcp_universe, packet -> options,
			    DHO_DHCP_CLIENT_IDENTIFIER);
	if (oc &&
	    evaluate_option_cache (&d1, packet, lease,
				   (struct client_state *)0,
				   packet -> options, state -> options,
				   &lease -> scope, oc, MDL)) {
		if (d1.len <= sizeof lt -> uid_buf) {
			memcpy (lt -> uid_buf, d1.data, d1.len);
			lt -> uid = lt -> uid_buf;
			lt -> uid_max = sizeof lt -> uid_buf;
			lt -> uid_len = d1.len;
		} else {
			unsigned char *tuid;
			lt -> uid_max = d1.len;
			lt -> uid_len = d1.len;
			tuid = (unsigned char *)dmalloc (lt -> uid_max, MDL);
			/* XXX inelegant */
			if (!tuid)
				log_fatal ("no memory for large uid.");
			memcpy (tuid, d1.data, lt -> uid_len);
			lt -> uid = tuid;
		}
		data_string_forget (&d1, MDL);
	}

	if (lease -> host)
		host_reference (&lt -> host, lease -> host, MDL);
	if (lease -> subnet)
		subnet_reference (&lt -> subnet, lease -> subnet, MDL);
	if (lease -> billing_class)
		class_reference (&lt -> billing_class,
				 lease -> billing_class, MDL);

	/* Set a flag if this client is a broken client that NUL
	   terminates string options and expects us to do likewise. */
	if (ms_nulltp)
		lease -> flags |= MS_NULL_TERMINATION;
	else
		lease -> flags &= ~MS_NULL_TERMINATION;

	/* Save any bindings. */
	if (lease -> scope) {
		binding_scope_reference (&lt -> scope, lease -> scope, MDL);
		binding_scope_dereference (&lease -> scope, MDL);
	}
	if (lease -> agent_options)
		option_chain_head_reference (&lt -> agent_options,
					     lease -> agent_options, MDL);

	/* If we got relay agent information options, and the packet really
	   looks like it came through a relay agent, and if this feature is
	   not disabled, save the relay agent information options that came
	   in with the packet, so that we can use them at renewal time when
	   the packet won't have gone through a relay agent. */
	if (packet -> raw -> giaddr.s_addr &&
	    packet -> options -> universe_count > agent_universe.index &&
	    packet -> options -> universes [agent_universe.index] &&
	    (state -> options -> universe_count <= agent_universe.index ||
	     state -> options -> universes [agent_universe.index] ==
	     packet -> options -> universes [agent_universe.index])) {
	    oc = lookup_option (&server_universe, state -> options,
				SV_STASH_AGENT_OPTIONS);
	    if (!oc ||
		evaluate_boolean_option_cache (&ignorep, packet, lease,
					       (struct client_state *)0,
					       packet -> options,
					       state -> options,
					       &lease -> scope, oc, MDL)) {
		if (lt -> agent_options)
		    option_chain_head_dereference (&lt -> agent_options, MDL);
		option_chain_head_reference
			(&lt -> agent_options,
			 (struct option_chain_head *)
			 packet -> options -> universes [agent_universe.index],
			 MDL);
	    }
	}

	/* Replace the old lease hostname with the new one, if it's changed. */
	oc = lookup_option (&dhcp_universe, packet -> options, DHO_HOST_NAME);
	if (oc)
		s1 = evaluate_option_cache (&d1, packet, (struct lease *)0,
					    (struct client_state *)0,
					    packet -> options,
					    (struct option_state *)0,
					    &global_scope, oc, MDL);
	if (oc && s1 &&
	    lease -> client_hostname &&
	    strlen (lease -> client_hostname) == d1.len &&
	    !memcmp (lease -> client_hostname, d1.data, d1.len)) {
		/* Hasn't changed. */
		data_string_forget (&d1, MDL);
		lt -> client_hostname = lease -> client_hostname;
		lease -> client_hostname = (char *)0;
	} else if (oc && s1) {
		lt -> client_hostname = dmalloc (d1.len + 1, MDL);
		if (!lt -> client_hostname)
			log_error ("no memory for client hostname.");
		else {
			memcpy (lt -> client_hostname, d1.data, d1.len);
			lt -> client_hostname [d1.len] = 0;
		}
		data_string_forget (&d1, MDL);
	}

	/* Record the hardware address, if given... */
	lt -> hardware_addr.hlen = packet -> raw -> hlen + 1;
	lt -> hardware_addr.hbuf [0] = packet -> raw -> htype;
	memcpy (&lt -> hardware_addr.hbuf [1], packet -> raw -> chaddr,
		sizeof packet -> raw -> chaddr);

	lt -> flags = lease -> flags & ~PERSISTENT_FLAGS;

	/* If there are statements to execute when the lease is
	   committed, execute them. */
	if (lease -> on_commit && (!offer || offer == DHCPACK)) {
		execute_statements ((struct binding_value **)0,
				    packet, lt, (struct client_state *)0,
				    packet -> options,
				    state -> options, &lt -> scope,
				    lease -> on_commit);
		if (lease -> on_commit)
			executable_statement_dereference (&lease -> on_commit,
							  MDL);
	}

#ifdef NSUPDATE
	/* Perform DDNS updates, if configured to. */
	if ((!offer || offer == DHCPACK) &&
	    (!(oc = lookup_option (&server_universe, state -> options,
				   SV_DDNS_UPDATES)) ||
	     evaluate_boolean_option_cache (&ignorep, packet, lt,
					    (struct client_state *)0,
					    packet -> options,
					    state -> options,
					    &lt -> scope, oc, MDL))) {
		ddns_updates (packet, lt, lease, state);
	}
#endif /* NSUPDATE */

	/* Don't call supersede_lease on a mocked-up lease. */
	if (lease -> flags & STATIC_LEASE) {
		/* Copy the hardware address into the static lease
		   structure. */
		lease -> hardware_addr.hlen = packet -> raw -> hlen + 1;
		lease -> hardware_addr.hbuf [0] = packet -> raw -> htype;
		memcpy (&lease -> hardware_addr.hbuf [1],
			packet -> raw -> chaddr,
			sizeof packet -> raw -> chaddr); /* XXX */
	} else {
		/* Install the new information about this lease in the
		   database.  If this is a DHCPACK or a dynamic BOOTREPLY
		   and we can't write the lease, don't ACK it (or BOOTREPLY
		   it) either. */

		if (!supersede_lease (lease, lt, !offer || offer == DHCPACK,
				      offer == DHCPACK, offer == DHCPACK)) {
			log_info ("%s: database update failed", msg);
			free_lease_state (state, MDL);
			lease_dereference (&lt, MDL);
			return;
		}
	}
	lease_dereference (&lt, MDL);

	/* Remember the interface on which the packet arrived. */
	state -> ip = packet -> interface;

	/* Remember the giaddr, xid, secs, flags and hops. */
	state -> giaddr = packet -> raw -> giaddr;
	state -> ciaddr = packet -> raw -> ciaddr;
	state -> xid = packet -> raw -> xid;
	state -> secs = packet -> raw -> secs;
	state -> bootp_flags = packet -> raw -> flags;
	state -> hops = packet -> raw -> hops;
	state -> offer = offer;

	/* If we're always supposed to broadcast to this client, set
	   the broadcast bit in the bootp flags field. */
	if ((oc = lookup_option (&server_universe, state -> options,
				SV_ALWAYS_BROADCAST)) &&
	    evaluate_boolean_option_cache (&ignorep, packet, lease,
					   (struct client_state *)0,
					   packet -> options, state -> options,
					   &lease -> scope, oc, MDL))
		state -> bootp_flags |= htons (BOOTP_BROADCAST);

	/* Get the Maximum Message Size option from the packet, if one
	   was sent. */
	oc = lookup_option (&dhcp_universe, packet -> options,
			    DHO_DHCP_MAX_MESSAGE_SIZE);
	if (oc &&
	    evaluate_option_cache (&d1, packet, lease,
				   (struct client_state *)0,
				   packet -> options, state -> options,
				   &lease -> scope, oc, MDL)) {
		if (d1.len == sizeof (u_int16_t))
			state -> max_message_size = getUShort (d1.data);
		data_string_forget (&d1, MDL);
	} else {
		oc = lookup_option (&dhcp_universe, state -> options,
				    DHO_DHCP_MAX_MESSAGE_SIZE);
		if (oc &&
		    evaluate_option_cache (&d1, packet, lease,
					   (struct client_state *)0,
					   packet -> options, state -> options,
					   &lease -> scope, oc, MDL)) {
			if (d1.len == sizeof (u_int16_t))
				state -> max_message_size =
					getUShort (d1.data);
			data_string_forget (&d1, MDL);
		}
	}

	/* Get the Subnet Selection option from the packet, if one
	   was sent. */
	if ((oc = lookup_option (&dhcp_universe, packet -> options,
				 DHO_SUBNET_SELECTION))) {

		/* Make a copy of the data. */
		struct option_cache *noc = (struct option_cache *)0;
		if (option_cache_allocate (&noc, MDL)) {
			if (oc -> data.len)
				data_string_copy (&noc -> data,
						  &oc -> data, MDL);
			if (oc -> expression)
				expression_reference (&noc -> expression,
						      oc -> expression, MDL);
			if (oc -> option)
				noc -> option = oc -> option;
		}

		save_option (&dhcp_universe, state -> options, noc);
		option_cache_dereference (&noc, MDL);
	}

	/* Now, if appropriate, put in DHCP-specific options that
           override those. */
	if (state -> offer) {
		i = DHO_DHCP_MESSAGE_TYPE;
		oc = (struct option_cache *)0;
		if (option_cache_allocate (&oc, MDL)) {
			if (make_const_data (&oc -> expression,
					     &state -> offer, 1, 0, 0, MDL)) {
				oc -> option =
					dhcp_universe.options [i];
				save_option (&dhcp_universe,
					     state -> options, oc);
			}
			option_cache_dereference (&oc, MDL);
		}
		i = DHO_DHCP_SERVER_IDENTIFIER;
		if (!(oc = lookup_option (&dhcp_universe,
					  state -> options, i))) {
		 use_primary:
			oc = (struct option_cache *)0;
			if (option_cache_allocate (&oc, MDL)) {
				if (make_const_data
				    (&oc -> expression,
				     ((unsigned char *)
				      &state -> ip -> primary_address),
				     sizeof state -> ip -> primary_address,
				     0, 0, MDL)) {
					oc -> option =
						dhcp_universe.options [i];
					save_option (&dhcp_universe,
						     state -> options, oc);
				}
				option_cache_dereference (&oc, MDL);
			}
			state -> from.len =
				sizeof state -> ip -> primary_address;
			memcpy (state -> from.iabuf,
				&state -> ip -> primary_address,
				state -> from.len);
		} else {
			if (evaluate_option_cache (&d1, packet, lease,
						   (struct client_state *)0,
						   packet -> options,
						   state -> options,
						   &lease -> scope, oc, MDL)) {
				if (!d1.len ||
				    d1.len > sizeof state -> from.iabuf) {
					data_string_forget (&d1, MDL);
					goto use_primary;
				}
				memcpy (state -> from.iabuf, d1.data, d1.len);
				state -> from.len = d1.len;
				data_string_forget (&d1, MDL);
			} else
				goto use_primary;
		}

		offered_lease_time =
			state -> offered_expiry - cur_time;

		putULong ((unsigned char *)&state -> expiry,
			  (unsigned long)offered_lease_time);
		i = DHO_DHCP_LEASE_TIME;
		if (lookup_option (&dhcp_universe, state -> options, i))
			log_error ("dhcp-lease-time option for %s overridden.",
			      inet_ntoa (state -> ciaddr));
		oc = (struct option_cache *)0;
		if (option_cache_allocate (&oc, MDL)) {
			if (make_const_data (&oc -> expression,
					     (unsigned char *)&state -> expiry,
					     sizeof state -> expiry,
					     0, 0, MDL)) {
				oc -> option = dhcp_universe.options [i];
				save_option (&dhcp_universe,
					     state -> options, oc);
			}
			option_cache_dereference (&oc, MDL);
		}

		/* Renewal time is lease time * 0.5. */
		offered_lease_time /= 2;
		putULong ((unsigned char *)&state -> renewal,
			  (unsigned long)offered_lease_time);
		i = DHO_DHCP_RENEWAL_TIME;
		if (lookup_option (&dhcp_universe, state -> options, i))
			log_error ("overriding dhcp-renewal-time for %s.",
				   inet_ntoa (state -> ciaddr));
		oc = (struct option_cache *)0;
		if (option_cache_allocate (&oc, MDL)) {
			if (make_const_data (&oc -> expression,
					     (unsigned char *)
					     &state -> renewal,
					     sizeof state -> renewal,
					     0, 0, MDL)) {
				oc -> option = dhcp_universe.options [i];
				save_option (&dhcp_universe,
					     state -> options, oc);
			}
			option_cache_dereference (&oc, MDL);
		}

		/* Rebinding time is lease time * 0.875. */
		offered_lease_time += (offered_lease_time / 2
				       + offered_lease_time / 4);
		putULong ((unsigned char *)&state -> rebind,
			  (unsigned)offered_lease_time);
		i = DHO_DHCP_REBINDING_TIME;
		if (lookup_option (&dhcp_universe, state -> options, i))
			log_error ("overriding dhcp-rebinding-time for %s.",
			      inet_ntoa (state -> ciaddr));
		oc = (struct option_cache *)0;
		if (option_cache_allocate (&oc, MDL)) {
			if (make_const_data (&oc -> expression,
					     (unsigned char *)&state -> rebind,
					     sizeof state -> rebind,
					     0, 0, MDL)) {
				oc -> option = dhcp_universe.options [i];
				save_option (&dhcp_universe,
					     state -> options, oc);
			}
			option_cache_dereference (&oc, MDL);
		}
	} else {
		state -> from.len =
			sizeof state -> ip -> primary_address;
		memcpy (state -> from.iabuf,
			&state -> ip -> primary_address,
			state -> from.len);
	}

	/* Figure out the address of the boot file server. */
	memcpy (&state -> siaddr, state -> from.iabuf, sizeof state -> siaddr);
	if ((oc =
	     lookup_option (&server_universe,
			    state -> options, SV_NEXT_SERVER))) {
		if (evaluate_option_cache (&d1, packet, lease,
					   (struct client_state *)0,
					   packet -> options, state -> options,
					   &lease -> scope, oc, MDL)) {
			/* If there was more than one answer,
			   take the first. */
			if (d1.len >= 4 && d1.data)
				memcpy (&state -> siaddr, d1.data, 4);
			data_string_forget (&d1, MDL);
		}
	}

	/* Use the subnet mask from the subnet declaration if no other
	   mask has been provided. */
	i = DHO_SUBNET_MASK;
	if (!lookup_option (&dhcp_universe, state -> options, i)) {
		oc = (struct option_cache *)0;
		if (option_cache_allocate (&oc, MDL)) {
			if (make_const_data (&oc -> expression,
					     lease -> subnet -> netmask.iabuf,
					     lease -> subnet -> netmask.len,
					     0, 0, MDL)) {
				oc -> option = dhcp_universe.options [i];
				save_option (&dhcp_universe,
					     state -> options, oc);
			}
			option_cache_dereference (&oc, MDL);
		}
	}

	/* Use the hostname from the host declaration if there is one
	   and no hostname has otherwise been provided, and if the 
	   use-host-decl-name flag is set. */
	i = DHO_HOST_NAME;
	j = SV_USE_HOST_DECL_NAMES;
	if (!lookup_option (&dhcp_universe, state -> options, i) &&
	    lease -> host && lease -> host -> name &&
	    (evaluate_boolean_option_cache
	     (&ignorep, packet, lease, (struct client_state *)0,
	      packet -> options, state -> options, &lease -> scope,
	      lookup_option (&server_universe, state -> options, j), MDL))) {
		oc = (struct option_cache *)0;
		if (option_cache_allocate (&oc, MDL)) {
			if (make_const_data (&oc -> expression,
					     ((unsigned char *)
					      lease -> host -> name),
					     strlen (lease -> host -> name),
					     1, 0, MDL)) {
				oc -> option = dhcp_universe.options [i];
				save_option (&dhcp_universe,
					     state -> options, oc);
			}
			option_cache_dereference (&oc, MDL);
		}
	}

	/* If we don't have a hostname yet, and we've been asked to do
	   a reverse lookup to find the hostname, do it. */
	j = SV_GET_LEASE_HOSTNAMES;
	if (!lookup_option (&server_universe, state -> options, i) &&
	    (evaluate_boolean_option_cache
	     (&ignorep, packet, lease, (struct client_state *)0,
	      packet -> options, state -> options, &lease -> scope,
	      lookup_option (&server_universe, state -> options, j), MDL))) {
		struct in_addr ia;
		struct hostent *h;
		
		memcpy (&ia, lease -> ip_addr.iabuf, 4);
		
		h = gethostbyaddr ((char *)&ia, sizeof ia, AF_INET);
		if (!h)
			log_error ("No hostname for %s", inet_ntoa (ia));
		else {
			oc = (struct option_cache *)0;
			if (option_cache_allocate (&oc, MDL)) {
				if (make_const_data (&oc -> expression,
						     ((unsigned char *)
						      h -> h_name),
						     strlen (h -> h_name) + 1,
						     1, 1, MDL)) {
					oc -> option =
						dhcp_universe.options [i];
					save_option (&dhcp_universe,
						     state -> options, oc);
				}
				option_cache_dereference (&oc, MDL);
			}
		}
	}

	/* If so directed, use the leased IP address as the router address.
	   This supposedly makes Win95 machines ARP for all IP addresses,
	   so if the local router does proxy arp, you win. */

	if (evaluate_boolean_option_cache
	    (&ignorep, packet, lease, (struct client_state *)0,
	     packet -> options, state -> options, &lease -> scope,
	     lookup_option (&server_universe, state -> options,
			    SV_USE_LEASE_ADDR_FOR_DEFAULT_ROUTE), MDL)) {
		i = DHO_ROUTERS;
		oc = lookup_option (&dhcp_universe, state -> options, i);
		if (!oc) {
			oc = (struct option_cache *)0;
			if (option_cache_allocate (&oc, MDL)) {
				if (make_const_data (&oc -> expression,
						     lease -> ip_addr.iabuf,
						     lease -> ip_addr.len,
						     0, 0, MDL)) {
					oc -> option =
						dhcp_universe.options [i];
					save_option (&dhcp_universe,
						     state -> options, oc);
				}
				option_cache_dereference (&oc, MDL);	
			}
		}
	}

	/* If a site option space has been specified, use that for
	   site option codes. */
	i = SV_SITE_OPTION_SPACE;
	if ((oc = lookup_option (&server_universe, state -> options, i)) &&
	    evaluate_option_cache (&d1, packet, lease,
				   (struct client_state *)0,
				   packet -> options, state -> options,
				   &lease -> scope, oc, MDL)) {
		struct universe *u = (struct universe *)0;

		if (!universe_hash_lookup (&u, universe_hash,
					   (const char *)d1.data, d1.len,
					   MDL)) {
			log_error ("unknown option space %s.", d1.data);
			return;
		}

		state -> options -> site_universe = u -> index;
		state -> options -> site_code_min = 128; /* XXX */
		data_string_forget (&d1, MDL);
	} else {
		state -> options -> site_code_min = 0;
		state -> options -> site_universe = dhcp_universe.index;
	}

	/* If the client has provided a list of options that it wishes
	   returned, use it to prioritize.  If there's a parameter
	   request list in scope, use that in preference.  Otherwise
	   use the default priority list. */

	oc = lookup_option (&dhcp_universe, state -> options,
			    DHO_DHCP_PARAMETER_REQUEST_LIST);

	if (!oc)
		oc = lookup_option (&dhcp_universe, packet -> options,
				    DHO_DHCP_PARAMETER_REQUEST_LIST);
	if (oc)
		evaluate_option_cache (&state -> parameter_request_list,
				       packet, lease, (struct client_state *)0,
				       packet -> options, state -> options,
				       &lease -> scope, oc, MDL);

#ifdef DEBUG_PACKET
	dump_packet (packet);
	dump_raw ((unsigned char *)packet -> raw, packet -> packet_length);
#endif

	lease -> state = state;

	log_info ("%s", msg);

	/* Hang the packet off the lease state. */
	packet_reference (&lease -> state -> packet, packet, MDL);

	/* If this is a DHCPOFFER, ping the lease address before actually
	   sending the offer. */
	if (offer == DHCPOFFER && !(lease -> flags & STATIC_LEASE) &&
	    cur_time - lease -> timestamp > 60 &&
	    (!(oc = lookup_option (&server_universe, state -> options,
				   SV_PING_CHECKS)) ||
	     evaluate_boolean_option_cache (&ignorep, packet, lease,
					    (struct client_state *)0,
					    packet -> options,
					    state -> options,
					    &lease -> scope, oc, MDL))) {
		lease -> timestamp = cur_time;
		icmp_echorequest (&lease -> ip_addr);
		add_timeout (cur_time + 1, lease_ping_timeout, lease,
			     (tvref_t)lease_reference,
			     (tvunref_t)lease_dereference);
		++outstanding_pings;
	} else {
		lease -> timestamp = cur_time;
		dhcp_reply (lease);
	}
}

void dhcp_reply (lease)
	struct lease *lease;
{
	int bufs = 0;
	unsigned packet_length;
	struct dhcp_packet raw;
	struct sockaddr_in to;
	struct in_addr from;
	struct hardware hto;
	int result;
	int i;
	struct lease_state *state = lease -> state;
	int nulltp, bootpp, unicastp = 1;
	struct option_tag *ot, *not;
	struct data_string d1;
	struct option_cache *oc;
	char *s;

	if (!state)
		log_fatal ("dhcp_reply was supplied lease with no state!");

	/* Compose a response for the client... */
	memset (&raw, 0, sizeof raw);
	memset (&d1, 0, sizeof d1);

	/* Copy in the filename if given; otherwise, flag the filename
	   buffer as available for options. */
	if (state -> filename.len && state -> filename.data) {
		memcpy (raw.file,
			state -> filename.data,
			state -> filename.len > sizeof raw.file
			? sizeof raw.file : state -> filename.len);
		if (sizeof raw.file > state -> filename.len)
			memset (&raw.file [state -> filename.len], 0,
				(sizeof raw.file) - state -> filename.len);
	} else
		bufs |= 1;

	/* Copy in the server name if given; otherwise, flag the
	   server_name buffer as available for options. */
	if (state -> server_name.len && state -> server_name.data) {
		memcpy (raw.sname,
			state -> server_name.data,
			state -> server_name.len > sizeof raw.sname
			? sizeof raw.sname : state -> server_name.len);
		if (sizeof raw.sname > state -> server_name.len)
			memset (&raw.sname [state -> server_name.len], 0,
				(sizeof raw.sname) - state -> server_name.len);
	} else
		bufs |= 2; /* XXX */

	memcpy (raw.chaddr,
		&lease -> hardware_addr.hbuf [1], sizeof raw.chaddr);
	raw.hlen = lease -> hardware_addr.hlen - 1;
	raw.htype = lease -> hardware_addr.hbuf [0];

	/* See if this is a Microsoft client that NUL-terminates its
	   strings and expects us to do likewise... */
	if (lease -> flags & MS_NULL_TERMINATION)
		nulltp = 1;
	else
		nulltp = 0;

	/* See if this is a bootp client... */
	if (state -> offer)
		bootpp = 0;
	else
		bootpp = 1;

	/* Insert such options as will fit into the buffer. */
	packet_length = cons_options (state -> packet, &raw, lease,
				      (struct client_state *)0,
				      state -> max_message_size,
				      state -> packet -> options,
				      state -> options, &global_scope,
				      bufs, nulltp, bootpp,
				      &state -> parameter_request_list,
				      (char *)0);

	memcpy (&raw.ciaddr, &state -> ciaddr, sizeof raw.ciaddr);
	memcpy (&raw.yiaddr, lease -> ip_addr.iabuf, 4);
	raw.siaddr = state -> siaddr;
	raw.giaddr = state -> giaddr;

	raw.xid = state -> xid;
	raw.secs = state -> secs;
	raw.flags = state -> bootp_flags;
	raw.hops = state -> hops;
	raw.op = BOOTREPLY;

	if (lease -> client_hostname &&
	    db_printable (lease -> client_hostname))
		s = lease -> client_hostname;
	else
		s = (char *)0;

	/* Say what we're doing... */
	log_info ("%s on %s to %s %s%s%svia %s",
		  (state -> offer
		   ? (state -> offer == DHCPACK ? "DHCPACK" : "DHCPOFFER")
		   : "BOOTREPLY"),
		  piaddr (lease -> ip_addr),
		  (lease -> hardware_addr.hlen
		   ? print_hw_addr (lease -> hardware_addr.hbuf [0],
				    lease -> hardware_addr.hlen - 1,
				    &lease -> hardware_addr.hbuf [1])
		   : print_hex_1 (lease -> uid_len, lease -> uid, 
				  lease -> uid_len)),
		  s ? "(" : "", s ? s : "", s ? ") " : "",
		  (state -> giaddr.s_addr
		   ? inet_ntoa (state -> giaddr)
		   : state -> ip -> name));

	/* Set up the hardware address... */
	hto.hlen = lease -> hardware_addr.hlen;
	memcpy (hto.hbuf, lease -> hardware_addr.hbuf, hto.hlen);

	to.sin_family = AF_INET;
#ifdef HAVE_SA_LEN
	to.sin_len = sizeof to;
#endif
	memset (to.sin_zero, 0, sizeof to.sin_zero);

#ifdef DEBUG_PACKET
	dump_raw ((unsigned char *)&raw, packet_length);
#endif

	/* Make sure outgoing packets are at least as big
	   as a BOOTP packet. */
	if (packet_length < BOOTP_MIN_LEN)
		packet_length = BOOTP_MIN_LEN;

	/* If this was gatewayed, send it back to the gateway... */
	if (raw.giaddr.s_addr) {
		to.sin_addr = raw.giaddr;
		if (raw.giaddr.s_addr != htonl (INADDR_LOOPBACK))
			to.sin_port = local_port;
		else
			to.sin_port = remote_port; /* For debugging. */

		if (fallback_interface) {
			result = send_packet (fallback_interface,
					      (struct packet *)0,
					      &raw, packet_length,
					      raw.siaddr, &to,
					      (struct hardware *)0);

			free_lease_state (state, MDL);
			lease -> state = (struct lease_state *)0;
			return;
		}

	/* If the client is RENEWING, unicast to the client using the
	   regular IP stack.  Some clients, particularly those that
	   follow RFC1541, are buggy, and send both ciaddr and server
	   identifier.  We deal with this situation by assuming that
	   if we got both dhcp-server-identifier and ciaddr, and
	   giaddr was not set, then the client is on the local
	   network, and we can therefore unicast or broadcast to it
	   successfully.  A client in REQUESTING state on another
	   network that's making this mistake will have set giaddr,
	   and will therefore get a relayed response from the above
	   code. */
	} else if (raw.ciaddr.s_addr &&
		   !((state -> got_server_identifier ||
		      (raw.flags & htons (BOOTP_BROADCAST))) &&
		     /* XXX This won't work if giaddr isn't zero, but it is: */
		     (state -> shared_network ==
		      lease -> subnet -> shared_network)) &&
		   state -> offer == DHCPACK) {
		to.sin_addr = raw.ciaddr;
		to.sin_port = remote_port;

		if (fallback_interface) {
			result = send_packet (fallback_interface,
					      (struct packet *)0,
					      &raw, packet_length,
					      raw.siaddr, &to,
					      (struct hardware *)0);
			free_lease_state (state, MDL);
			lease -> state = (struct lease_state *)0;
			return;
		}

	/* If it comes from a client that already knows its address
	   and is not requesting a broadcast response, and we can
	   unicast to a client without using the ARP protocol, sent it
	   directly to that client. */
	} else if (!(raw.flags & htons (BOOTP_BROADCAST)) &&
		   can_unicast_without_arp (state -> ip)) {
		to.sin_addr = raw.yiaddr;
		to.sin_port = remote_port;

	/* Otherwise, broadcast it on the local network. */
	} else {
		to.sin_addr = limited_broadcast;
		to.sin_port = remote_port;
		if (!(lease -> flags & UNICAST_BROADCAST_HACK))
			unicastp = 0;
	}

	memcpy (&from, state -> from.iabuf, sizeof from);

	result = send_packet (state -> ip,
			      (struct packet *)0, &raw, packet_length,
			      from, &to,
			      unicastp ? &hto : (struct hardware *)0);

	/* Free all of the entries in the option_state structure
	   now that we're done with them. */

	free_lease_state (state, MDL);
	lease -> state = (struct lease_state *)0;
}

int find_lease (struct lease **lp,
		struct packet *packet, struct shared_network *share, int *ours,
		int *allocatedp, struct lease *ip_lease_in,
		const char *file, int line)
{
	struct lease *uid_lease = (struct lease *)0;
	struct lease *ip_lease = (struct lease *)0;
	struct lease *hw_lease = (struct lease *)0;
	struct lease *lease = (struct lease *)0;
	struct iaddr cip;
	struct host_decl *hp = (struct host_decl *)0;
	struct host_decl *host = (struct host_decl *)0;
	struct lease *fixed_lease = (struct lease *)0;
	struct lease *next = (struct lease *)0;
	struct option_cache *oc;
	struct data_string d1;
	int have_client_identifier = 0;
	struct data_string client_identifier;
	int status;
	struct hardware h;

	if (packet -> raw -> ciaddr.s_addr) {
		cip.len = 4;
		memcpy (cip.iabuf, &packet -> raw -> ciaddr, 4);
	} else {
		/* Look up the requested address. */
		oc = lookup_option (&dhcp_universe, packet -> options,
				    DHO_DHCP_REQUESTED_ADDRESS);
		memset (&d1, 0, sizeof d1);
		if (oc &&
		    evaluate_option_cache (&d1, packet, (struct lease *)0,
					   (struct client_state *)0,
					   packet -> options,
					   (struct option_state *)0,
					   &global_scope, oc, MDL)) {
			packet -> got_requested_address = 1;
			cip.len = 4;
			memcpy (cip.iabuf, d1.data, cip.len);
			data_string_forget (&d1, MDL);
		} else 
			cip.len = 0;
	}

	/* Try to find a host or lease that's been assigned to the
	   specified unique client identifier. */
	oc = lookup_option (&dhcp_universe, packet -> options,
			    DHO_DHCP_CLIENT_IDENTIFIER);
	memset (&client_identifier, 0, sizeof client_identifier);
	if (oc &&
	    evaluate_option_cache (&client_identifier,
				   packet, (struct lease *)0,
				   (struct client_state *)0,
				   packet -> options, (struct option_state *)0,
				   &global_scope, oc, MDL)) {
		/* Remember this for later. */
		have_client_identifier = 1;

		/* First, try to find a fixed host entry for the specified
		   client identifier... */
		if (find_hosts_by_uid (&hp, client_identifier.data,
				       client_identifier.len, MDL)) {
			/* Remember if we know of this client. */
			packet -> known = 1;
			mockup_lease (&fixed_lease, packet, share, hp);
		}

#if defined (DEBUG_FIND_LEASE)
		if (fixed_lease) {
			log_info ("Found host for client identifier: %s.",
			      piaddr (fixed_lease -> ip_addr));
		}
#endif
		if (hp) {
			if (!fixed_lease) /* Save the host if we found one. */
				host_reference (&host, hp, MDL);
			host_dereference (&hp, MDL);
		}

		find_lease_by_uid (&uid_lease, client_identifier.data,
				   client_identifier.len, MDL);
	}

	/* If we didn't find a fixed lease using the uid, try doing
	   it with the hardware address... */
	if (!fixed_lease && !host) {
		if (find_hosts_by_haddr (&hp, packet -> raw -> htype,
					 packet -> raw -> chaddr,
					 packet -> raw -> hlen, MDL)) {
			/* Remember if we know of this client. */
			packet -> known = 1;
			if (host)
				host_dereference (&host, MDL);
			host_reference (&host, hp, MDL);
			host_dereference (&hp, MDL);
			mockup_lease (&fixed_lease, packet, share, host);
#if defined (DEBUG_FIND_LEASE)
			if (fixed_lease) {
				log_info ("Found host for link address: %s.",
				      piaddr (fixed_lease -> ip_addr));
			}
#endif
		}
	}

	/* If fixed_lease is present but does not match the requested
	   IP address, and this is a DHCPREQUEST, then we can't return
	   any other lease, so we might as well return now. */
	if (packet -> packet_type == DHCPREQUEST && fixed_lease &&
	    (fixed_lease -> ip_addr.len != cip.len ||
	     memcmp (fixed_lease -> ip_addr.iabuf,
		     cip.iabuf, cip.len))) {
		if (ours)
			*ours = 1;
		strcpy (dhcp_message, "requested address is incorrect");
#if defined (DEBUG_FIND_LEASE)
		log_info ("Client's fixed-address %s doesn't match %s%s",
			  piaddr (fixed_lease -> ip_addr), "request ",
			  print_dotted_quads (cip.len, cip.iabuf));
#endif
		goto out;
	}

	/* If we found leases matching the client identifier, loop through
	   the n_uid pointer looking for one that's actually valid.   We
	   can't do this until we get here because we depend on
	   packet -> known, which may be set by either the uid host
	   lookup or the haddr host lookup. */
	while (uid_lease) {
#if defined (DEBUG_FIND_LEASE)
		log_info ("trying next lease matching client id: %s",
			  piaddr (uid_lease -> ip_addr));
#endif

#if defined (FAILOVER_PROTOCOL)
		/* When failover is active, it's possible that there could
		   be two "free" leases for the same uid, but only one of
		   them that's available for this failover peer to allocate. */
		if (uid_lease -> binding_state != FTS_ACTIVE &&
		    uid_lease -> binding_state != FTS_BOOTP &&
		    !lease_mine_to_reallocate (uid_lease)) {
#if defined (DEBUG_FIND_LEASE)
			log_info ("not mine to allocate: %s",
				  piaddr (uid_lease -> ip_addr));
#endif
			goto n_uid;
		}
#endif

		if (uid_lease -> subnet -> shared_network != share) {
#if defined (DEBUG_FIND_LEASE)
			log_info ("wrong network segment: %s",
				  piaddr (uid_lease -> ip_addr));
#endif
			goto n_uid;
		}

		if ((uid_lease -> pool -> prohibit_list &&
		     permitted (packet, uid_lease -> pool -> prohibit_list)) ||
		    (uid_lease -> pool -> permit_list &&
		     !permitted (packet, uid_lease -> pool -> permit_list))) {
#if defined (DEBUG_FIND_LEASE)
			log_info ("not permitted: %s",
				  piaddr (uid_lease -> ip_addr));
#endif
		       n_uid:
			if (uid_lease -> n_uid)
				lease_reference (&next,
						 uid_lease -> n_uid, MDL);
			if (!packet -> raw -> ciaddr.s_addr)
				release_lease (uid_lease, packet);
			lease_dereference (&uid_lease, MDL);
			if (next) {
				lease_reference (&uid_lease, next, MDL);
				lease_dereference (&next, MDL);
			}
			continue;
		}
		break;
	}
#if defined (DEBUG_FIND_LEASE)
	if (uid_lease)
		log_info ("Found lease for client id: %s.",
		      piaddr (uid_lease -> ip_addr));
#endif

	/* Find a lease whose hardware address matches, whose client
	   identifier matches, that's permitted, and that's on the
	   correct subnet. */
	h.hlen = packet -> raw -> hlen + 1;
	h.hbuf [0] = packet -> raw -> htype;
	memcpy (&h.hbuf [1], packet -> raw -> chaddr, packet -> raw -> hlen);
	find_lease_by_hw_addr (&hw_lease, h.hbuf, h.hlen, MDL);
	while (hw_lease) {
#if defined (DEBUG_FIND_LEASE)
		log_info ("trying next lease matching hw addr: %s",
			  piaddr (hw_lease -> ip_addr));
#endif
#if defined (FAILOVER_PROTOCOL)
		/* When failover is active, it's possible that there could
		   be two "free" leases for the same uid, but only one of
		   them that's available for this failover peer to allocate. */
		if (hw_lease -> binding_state != FTS_ACTIVE &&
		    hw_lease -> binding_state != FTS_BOOTP &&
		    !lease_mine_to_reallocate (hw_lease)) {
#if defined (DEBUG_FIND_LEASE)
			log_info ("not mine to allocate: %s",
				  piaddr (hw_lease -> ip_addr));
#endif
			goto n_hw;
		}
#endif

		if (hw_lease -> binding_state != FTS_FREE &&
		    hw_lease -> binding_state != FTS_BACKUP &&
		    hw_lease -> uid &&
		    (!have_client_identifier ||
		     hw_lease -> uid_len != client_identifier.len ||
		     memcmp (hw_lease -> uid, client_identifier.data,
			     hw_lease -> uid_len))) {
#if defined (DEBUG_FIND_LEASE)
			log_info ("wrong client identifier: %s",
				  piaddr (hw_lease -> ip_addr));
#endif
			goto n_hw;
			continue;
		}
		if (hw_lease -> subnet -> shared_network != share) {
#if defined (DEBUG_FIND_LEASE)
			log_info ("wrong network segment: %s",
				  piaddr (hw_lease -> ip_addr));
#endif
			goto n_hw;
			continue;
		}
		if ((hw_lease -> pool -> prohibit_list &&
		      permitted (packet, hw_lease -> pool -> prohibit_list)) ||
		    (hw_lease -> pool -> permit_list &&
		     !permitted (packet, hw_lease -> pool -> permit_list))) {
#if defined (DEBUG_FIND_LEASE)
			log_info ("not permitted: %s",
				  piaddr (hw_lease -> ip_addr));
#endif
			if (!packet -> raw -> ciaddr.s_addr)
				release_lease (hw_lease, packet);
		       n_hw:
			if (hw_lease -> n_hw)
				lease_reference (&next, hw_lease -> n_hw, MDL);
			lease_dereference (&hw_lease, MDL);
			if (next) {
				lease_reference (&hw_lease, next, MDL);
				lease_dereference (&next, MDL);
			}
			continue;
		}
		break;
	}
#if defined (DEBUG_FIND_LEASE)
	if (hw_lease)
		log_info ("Found lease for hardware address: %s.",
		      piaddr (hw_lease -> ip_addr));
#endif

	/* Try to find a lease that's been allocated to the client's
	   IP address. */
	if (ip_lease_in)
		lease_reference (&ip_lease, ip_lease_in, MDL);
	else if (cip.len)
		find_lease_by_ip_addr (&ip_lease, cip, MDL);

#if defined (DEBUG_FIND_LEASE)
	if (ip_lease)
		log_info ("Found lease for requested address: %s.",
		      piaddr (ip_lease -> ip_addr));
#endif

	/* If ip_lease is valid at this point, set ours to one, so that
	   even if we choose a different lease, we know that the address
	   the client was requesting was ours, and thus we can NAK it. */
	if (ip_lease && ours)
		*ours = 1;

	/* If the requested IP address isn't on the network the packet
	   came from, don't use it.  Allow abandoned leases to be matched
	   here - if the client is requesting it, there's a decent chance
	   that it's because the lease database got trashed and a client
	   that thought it had this lease answered an ARP or PING, causing the
	   lease to be abandoned.   If so, this request probably came from
	   that client. */
	if (ip_lease && (ip_lease -> subnet -> shared_network != share)) {
		if (ours)
			*ours = 1;
#if defined (DEBUG_FIND_LEASE)
		log_info ("...but it was on the wrong shared network.");
#endif
		strcpy (dhcp_message, "requested address on bad subnet");
		lease_dereference (&ip_lease, MDL);
	}

	/* Toss ip_lease if it hasn't yet expired and doesn't belong to the
	   client. */
	if (ip_lease &&
	    (ip_lease -> uid ?
	     (!have_client_identifier ||
	      ip_lease -> uid_len != client_identifier.len ||
	      memcmp (ip_lease -> uid, client_identifier.data,
		      ip_lease -> uid_len)) :
	     (ip_lease -> hardware_addr.hbuf [0] != packet -> raw -> htype ||
	      ip_lease -> hardware_addr.hlen != packet -> raw -> hlen + 1 ||
	      memcmp (&ip_lease -> hardware_addr.hbuf [1],
		      packet -> raw -> chaddr,
		      (unsigned)(ip_lease -> hardware_addr.hlen - 1))))) {
		/* If we're not doing failover, the only state in which
		   we can allocate this lease to the client is FTS_FREE.
		   If we are doing failover, things are more complicated.
		   If the lease is free or backup, we let the caller decide
		   whether or not to give it out. */
		if (ip_lease -> binding_state != FTS_FREE &&
		    ip_lease -> binding_state != FTS_BACKUP) {
#if defined (DEBUG_FIND_LEASE)
			log_info ("rejecting lease for requested address.");
#endif
			/* If we're rejecting it because the peer has
			   it, don't set "ours", because we shouldn't NAK. */
			if (ours && ip_lease -> binding_state != FTS_ACTIVE)
				*ours = 0;
			lease_dereference (&ip_lease, MDL);
		} else
			if (allocatedp)
				*allocatedp = 1;
	}

	/* If we got an ip_lease and a uid_lease or hw_lease, and ip_lease
	   is not active, and is not ours to reallocate, forget about it. */
	if (ip_lease && (uid_lease || hw_lease) &&
	    ip_lease -> binding_state != FTS_ACTIVE &&
	    ip_lease -> binding_state != FTS_BOOTP &&
	    !lease_mine_to_reallocate (ip_lease) &&
	    packet -> packet_type == DHCPDISCOVER) {
#if defined (DEBUG_FIND_LEASE)
		log_info ("ip lease not ours to offer.");
#endif
		lease_dereference (&ip_lease, MDL);
	}

	/* If for some reason the client has more than one lease
	   on the subnet that matches its uid, pick the one that
	   it asked for and (if we can) free the other. */
	if (ip_lease &&
	    (ip_lease -> binding_state == FTS_ACTIVE ||
	     ip_lease -> binding_state == FTS_BOOTP) &&
	    ip_lease -> uid && ip_lease != uid_lease) {
		if (have_client_identifier &&
		    (ip_lease -> uid_len == client_identifier.len) &&
		    !memcmp (client_identifier.data,
			     ip_lease -> uid, ip_lease -> uid_len)) {
			if (uid_lease) {
			    if (uid_lease -> binding_state == FTS_ACTIVE ||
				uid_lease -> binding_state == FTS_BOOTP) {
				log_error ("client %s has duplicate%s on %s",
					   (print_hw_addr
					    (packet -> raw -> htype,
					     packet -> raw -> hlen,
					     packet -> raw -> chaddr)),
					   " leases",
					   (ip_lease -> subnet ->
					    shared_network -> name));

				/* If the client is REQUESTing the lease,
				   it shouldn't still be using the old
				   one, so we can free it for allocation. */
				if (uid_lease &&
				    (uid_lease -> binding_state == FTS_ACTIVE
				     ||
				     uid_lease -> binding_state == FTS_BOOTP)
				    &&
				    !packet -> raw -> ciaddr.s_addr &&
				    (share ==
				     uid_lease -> subnet -> shared_network) &&
				    packet -> packet_type == DHCPREQUEST)
					dissociate_lease (uid_lease);
			    }
			    lease_dereference (&uid_lease, MDL);
			    lease_reference (&uid_lease, ip_lease, MDL);
			}
		}

		/* If we get to here and fixed_lease is not null, that means
		   that there are both a dynamic lease and a fixed-address
		   declaration for the same IP address. */
		if (packet -> packet_type == DHCPREQUEST && fixed_lease) {
			lease_dereference (&fixed_lease, MDL);
		      db_conflict:
			log_error ("Dynamic and static leases present for %s.",
				   piaddr (cip));
			log_error ("Remove host declaration %s or remove %s",
				   (fixed_lease && fixed_lease -> host
				    ? (fixed_lease -> host -> name
				       ? fixed_lease -> host -> name
				       : piaddr (cip))
				    : piaddr (cip)),
				    piaddr (cip));
			log_error ("from the dynamic address pool for %s",
				   ip_lease -> subnet -> shared_network -> name
				  );
			if (fixed_lease)
				lease_dereference (&ip_lease, MDL);
			strcpy (dhcp_message,
				"database conflict - call for help!");
		}

		if (ip_lease && ip_lease != uid_lease) {
#if defined (DEBUG_FIND_LEASE)
			log_info ("requested address not available.");
#endif
			lease_dereference (&ip_lease, MDL);
		}
	}

	/* If we get to here with both fixed_lease and ip_lease not
	   null, then we have a configuration file bug. */
	if (packet -> packet_type == DHCPREQUEST && fixed_lease && ip_lease)
		goto db_conflict;

	/* Toss extra pointers to the same lease... */
	if (hw_lease && hw_lease == uid_lease) {
#if defined (DEBUG_FIND_LEASE)
		log_info ("hardware lease and uid lease are identical.");
#endif
		lease_dereference (&hw_lease, MDL);
	}
	if (ip_lease && ip_lease == hw_lease) {
		lease_dereference (&hw_lease, MDL);
#if defined (DEBUG_FIND_LEASE)
		log_info ("hardware lease and ip lease are identical.");
#endif
	}
	if (ip_lease && ip_lease == uid_lease) {
		lease_dereference (&uid_lease, MDL);
#if defined (DEBUG_FIND_LEASE)
		log_info ("uid lease and ip lease are identical.");
#endif
	}

	/* Make sure the client is permitted to use the requested lease. */
	if (ip_lease &&
	    ((ip_lease -> pool -> prohibit_list &&
	      permitted (packet, ip_lease -> pool -> prohibit_list)) ||
	     (ip_lease -> pool -> permit_list &&
	      !permitted (packet, ip_lease -> pool -> permit_list)))) {
		if (!packet -> raw -> ciaddr.s_addr)
			release_lease (ip_lease, packet);
		lease_dereference (&ip_lease, MDL);
	}

	if (uid_lease &&
	    ((uid_lease -> pool -> prohibit_list &&
	      permitted (packet, uid_lease -> pool -> prohibit_list)) ||
	     (uid_lease -> pool -> permit_list &&
	      !permitted (packet, uid_lease -> pool -> permit_list)))) {
		if (!packet -> raw -> ciaddr.s_addr)
			release_lease (uid_lease, packet);
		lease_dereference (&uid_lease, MDL);
	}

	if (hw_lease &&
	    ((hw_lease -> pool -> prohibit_list &&
	      permitted (packet, hw_lease -> pool -> prohibit_list)) ||
	     (hw_lease -> pool -> permit_list &&
	      !permitted (packet, hw_lease -> pool -> permit_list)))) {
		if (!packet -> raw -> ciaddr.s_addr)
			release_lease (hw_lease, packet);
		lease_dereference (&hw_lease, MDL);
	}

	/* If we've already eliminated the lease, it wasn't there to
	   begin with.   If we have come up with a matching lease,
	   set the message to bad network in case we have to throw it out. */
	if (!ip_lease) {
		strcpy (dhcp_message, "requested address not available");
	}

	/* If this is a DHCPREQUEST, make sure the lease we're going to return
	   matches the requested IP address.   If it doesn't, don't return a
	   lease at all. */
	if (packet -> packet_type == DHCPREQUEST &&
	    !ip_lease && !fixed_lease) {
#if defined (DEBUG_FIND_LEASE)
		log_info ("no applicable lease found for DHCPREQUEST.");
#endif
		goto out;
	}

	/* At this point, if fixed_lease is nonzero, we can assign it to
	   this client. */
	if (fixed_lease) {
		lease_reference (&lease, fixed_lease, MDL);
		lease_dereference (&fixed_lease, MDL);
#if defined (DEBUG_FIND_LEASE)
		log_info ("choosing fixed address.");
#endif
	}

	/* If we got a lease that matched the ip address and don't have
	   a better offer, use that; otherwise, release it. */
	if (ip_lease) {
		if (lease) {
			if (!packet -> raw -> ciaddr.s_addr)
				release_lease (ip_lease, packet);
#if defined (DEBUG_FIND_LEASE)
			log_info ("not choosing requested address (!).");
#endif
		} else {
#if defined (DEBUG_FIND_LEASE)
			log_info ("choosing lease on requested address.");
#endif
			lease_reference (&lease, ip_lease, MDL);
			if (lease -> host)
				host_dereference (&lease -> host, MDL);
		}
		lease_dereference (&ip_lease, MDL);
	}

	/* If we got a lease that matched the client identifier, we may want
	   to use it, but if we already have a lease we like, we must free
	   the lease that matched the client identifier. */
	if (uid_lease) {
		if (lease) {
			if (!packet -> raw -> ciaddr.s_addr &&
			    packet -> packet_type == DHCPREQUEST &&
			    (uid_lease -> binding_state == FTS_ACTIVE ||
			     uid_lease -> binding_state == FTS_BOOTP))
				dissociate_lease (uid_lease);
#if defined (DEBUG_FIND_LEASE)
			log_info ("not choosing uid lease.");
#endif
		} else {
			lease_reference (&lease, uid_lease, MDL);
			if (lease -> host)
				host_dereference (&lease -> host, MDL);
#if defined (DEBUG_FIND_LEASE)
			log_info ("choosing uid lease.");
#endif
		}
		lease_dereference (&uid_lease, MDL);
	}

	/* The lease that matched the hardware address is treated likewise. */
	if (hw_lease) {
		if (lease) {
#if defined (DEBUG_FIND_LEASE)
			log_info ("not choosing hardware lease.");
#endif
		} else {
			/* We're a little lax here - if the client didn't
			   send a client identifier and it's a bootp client,
			   but the lease has a client identifier, we still
			   let the client have a lease. */
			if (!hw_lease -> uid_len ||
			    (have_client_identifier
			     ? (hw_lease -> uid_len ==
				client_identifier.len &&
				!memcmp (hw_lease -> uid,
					 client_identifier.data,
					 client_identifier.len))
			     : packet -> packet_type == 0)) {
				lease_reference (&lease, hw_lease, MDL);
				if (lease -> host)
					host_dereference (&lease -> host, MDL);
#if defined (DEBUG_FIND_LEASE)
				log_info ("choosing hardware lease.");
#endif
			} else {
#if defined (DEBUG_FIND_LEASE)
				log_info ("not choosing hardware lease: %s.",
					  "uid mismatch");
#endif
			}
		}
		lease_dereference (&hw_lease, MDL);
	}

	/* If we found a host_decl but no matching address, try to
	   find a host_decl that has no address, and if there is one,
	   hang it off the lease so that we can use the supplied
	   options. */
	if (lease && host && !lease -> host) {
		struct host_decl *p = (struct host_decl *)0;
		struct host_decl *n = (struct host_decl *)0;
		host_reference (&p, host, MDL);
		while (p) {
			if (!p -> fixed_addr) {
				host_reference (&lease -> host, p, MDL);
				host_dereference (&p, MDL);
				break;
			}
			if (p -> n_ipaddr)
				host_reference (&n, p -> n_ipaddr, MDL);
			host_dereference (&p, MDL);
			if (n) {
				host_reference (&p, n, MDL);
				host_dereference (&n, MDL);
			}
		}
	}

	/* If we find an abandoned lease, but it's the one the client
	   requested, we assume that previous bugginess on the part
	   of the client, or a server database loss, caused the lease to
	   be abandoned, so we reclaim it and let the client have it. */
	if (lease &&
	    (lease -> binding_state == FTS_ABANDONED) &&
	    lease == ip_lease &&
	    packet -> packet_type == DHCPREQUEST) {
		log_error ("Reclaiming REQUESTed abandoned IP address %s.",
		      piaddr (lease -> ip_addr));
	} else if (lease && (lease -> binding_state == FTS_ABANDONED)) {
	/* Otherwise, if it's not the one the client requested, we do not
	   return it - instead, we claim it's ours, causing a DHCPNAK to be
	   sent if this lookup is for a DHCPREQUEST, and force the client
	   to go back through the allocation process. */
		if (ours)
			*ours = 1;
		lease_dereference (&lease, MDL);
	}

	if (lease && allocatedp && lease -> ends <= cur_time)
		*allocatedp = 1;

      out:
	if (have_client_identifier)
		data_string_forget (&client_identifier, MDL);

	if (fixed_lease)
		lease_dereference (&fixed_lease, MDL);
	if (hw_lease)
		lease_dereference (&hw_lease, MDL);
	if (uid_lease)
		lease_dereference (&uid_lease, MDL);
	if (ip_lease)
		lease_dereference (&ip_lease, MDL);
	if (host)
		host_dereference (&host, MDL);

	if (lease) {
#if defined (DEBUG_FIND_LEASE)
		log_info ("Returning lease: %s.",
		      piaddr (lease -> ip_addr));
#endif
		lease_reference (lp, lease, file, line);
		lease_dereference (&lease, MDL);
		return 1;
	}
#if defined (DEBUG_FIND_LEASE)
	log_info ("Not returning a lease.");
#endif
	return 0;
}

/* Search the provided host_decl structure list for an address that's on
   the specified shared network.  If one is found, mock up and return a
   lease structure for it; otherwise return the null pointer. */

int mockup_lease (struct lease **lp, struct packet *packet,
		  struct shared_network *share, struct host_decl *hp)
{
	struct lease *lease = (struct lease *)0;
	const unsigned char **s;
	isc_result_t status;
	struct host_decl *rhp = (struct host_decl *)0;
	
	status = lease_allocate (&lease, MDL);
	if (status != ISC_R_SUCCESS)
		return 0;
	if (host_reference (&rhp, hp, MDL) != ISC_R_SUCCESS)
		return 0;
	if (!find_host_for_network (&lease -> subnet,
				    &rhp, &lease -> ip_addr, share)) {
		lease_dereference (&lease, MDL);
		return 0;
	}
	host_reference (&lease -> host, rhp, MDL);
	if (rhp -> client_identifier.len > sizeof lease -> uid_buf)
		lease -> uid = dmalloc (rhp -> client_identifier.len, MDL);
	else
		lease -> uid = lease -> uid_buf;
	if (!lease -> uid) {
		lease_dereference (&lease, MDL);
		host_dereference (&rhp, MDL);
		return 0;
	}
	memcpy (lease -> uid, rhp -> client_identifier.data,
		rhp -> client_identifier.len);
	lease -> uid_len = rhp -> client_identifier.len;
	lease -> hardware_addr = rhp -> interface;
	lease -> starts = lease -> timestamp = lease -> ends = MIN_TIME;
	lease -> flags = STATIC_LEASE;
	lease -> binding_state = FTS_FREE;
	lease_reference (lp, lease, MDL);
	lease_dereference (&lease, MDL);
	host_dereference (&rhp, MDL);
	return 1;
}

/* Look through all the pools in a list starting with the specified pool
   for a free lease.   We try to find a virgin lease if we can.   If we
   don't find a virgin lease, we try to find a non-virgin lease that's
   free.   If we can't find one of those, we try to reclaim an abandoned
   lease.   If all of these possibilities fail to pan out, we don't return
   a lease at all. */

int allocate_lease (struct lease **lp, struct packet *packet,
		    struct pool *pool, int *peer_has_leases)
{
	struct lease *lease = (struct lease *)0;
	struct lease **lq;
	struct permit *permit;

	if (!pool)
		return 0;

	/* If we aren't elegible to try this pool, try a subsequent one. */
	if ((pool -> prohibit_list &&
	     permitted (packet, pool -> prohibit_list)) ||
	    (pool -> permit_list && !permitted (packet, pool -> permit_list)))
		return allocate_lease (lp, packet, pool -> next,
				       peer_has_leases);

#if defined (FAILOVER_PROTOCOL)
	/* Peer_has_leases just says that we found at least one free lease.
	   If no free lease is returned, the caller can deduce that this
	   means the peer is hogging all the free leases, so we can print
	   a better error message. */

	/* XXX Do we need code here to ignore PEER_IS_OWNER and just check
	   XXX tstp if we're in, e.g., PARTNER_DOWN?   Where do we deal with
	   XXX CONFLICT_DETECTED, et al? */
	/* XXX This should be handled by the lease binding "state machine" -
	   XXX that is, when we get here, if a lease could be allocated, it
	   XXX will have the correct binding state so that the following code
	   XXX will result in its being allocated. */
	/* Skip to the most expired lease in the pool that is not owned by a
	   failover peer. */
	if (pool -> failover_peer) {
		if (pool -> failover_peer -> i_am == primary) {
			if (pool -> backup)
				*peer_has_leases = 1;
			lease = pool -> free;
			if (!lease)
				lease = pool -> abandoned;
		} else {
			if (pool -> free)
				*peer_has_leases = 1;
			lease = pool -> backup;
		}
	} else
#endif
	{
		if (pool -> free)
			lease = pool -> free;
		else
			lease = pool -> abandoned;
	}

	/* If there are no leases in the pool that have
	   expired, try the next one. */
	if (!lease || lease -> ends > cur_time)
		return allocate_lease (lp, packet,
				       pool -> next, peer_has_leases);

	/* If we find an abandoned lease, and no other lease qualifies
	   better, take it. */
	/* XXX what if there are non-abandoned leases that are younger
	   XXX than this?   Shouldn't we hunt for those here? */
	if (lease -> binding_state == FTS_ABANDONED) {
		/* If we already have a non-abandoned lease that we didn't
		   love, but that's okay, don't reclaim the abandoned lease. */
		if (*lp)
			return allocate_lease (lp, packet, pool -> next,
					       peer_has_leases);
		if (!allocate_lease (lp, packet,
				     pool -> next, peer_has_leases)) {
			log_error ("Reclaiming abandoned IP address %s.",
			      piaddr (lease -> ip_addr));
			lease_reference (lp, lease, MDL);
		}
		return 1;
	}

	/* If there's a lease we could take, but it had previously been
	   allocated to a different client, try for a virgin lease before
	   stealing it. */
	if (lease -> uid_len || lease -> hardware_addr.hlen) {
		/* If we're already in that boat, no need to consider
		   allocating this particular lease. */
		if (*lp)
			return allocate_lease (lp, packet, pool -> next,
					       peer_has_leases);

		allocate_lease (lp, packet, pool -> next, peer_has_leases);
		if (*lp)
			return 1;
	}

	lease_reference (lp, lease, MDL);
	return 1;
}

/* Determine whether or not a permit exists on a particular permit list
   that matches the specified packet, returning nonzero if so, zero if
   not. */

int permitted (packet, permit_list)
	struct packet *packet;
	struct permit *permit_list;
{
	struct permit *p;
	int i;

	for (p = permit_list; p; p = p -> next) {
		switch (p -> type) {
		      case permit_unknown_clients:
			if (!packet -> known)
				return 1;
			break;

		      case permit_known_clients:
			if (packet -> known)
				return 1;
			break;

		      case permit_authenticated_clients:
			if (packet -> authenticated)
				return 1;
			break;

		      case permit_unauthenticated_clients:
			if (!packet -> authenticated)
				return 1;
			break;

		      case permit_all_clients:
			return 1;

		      case permit_dynamic_bootp_clients:
			if (!packet -> options_valid ||
			    !packet -> packet_type)
				return 1;
			break;
			
		      case permit_class:
			for (i = 0; i < packet -> class_count; i++) {
				if (p -> class == packet -> classes [i])
					return 1;
				if (packet -> classes [i] &&
				    packet -> classes [i] -> superclass &&
				    (packet -> classes [i] -> superclass ==
				     p -> class))
					return 1;
			}
			break;
		}
	}
	return 0;
}

int locate_network (packet)
	struct packet *packet;
{
	struct iaddr ia;
	struct data_string data;
	struct subnet *subnet = (struct subnet *)0;
	struct option_cache *oc;

	/* See if there's a subnet selection option. */
	oc = lookup_option (&dhcp_universe, packet -> options,
			    DHO_SUBNET_SELECTION);

	/* If there's no SSO and no giaddr, then use the shared_network
	   from the interface, if there is one.   If not, fail. */
	if (!oc && !packet -> raw -> giaddr.s_addr) {
		if (packet -> interface -> shared_network) {
			shared_network_reference
				(&packet -> shared_network,
				 packet -> interface -> shared_network, MDL);
			return 1;
		}
		return 0;
	}

	/* If there's an SSO, and it's valid, use it to figure out the
	   subnet.    If it's not valid, fail. */
	if (oc) {
		memset (&data, 0, sizeof data);
		if (!evaluate_option_cache (&data, packet, (struct lease *)0,
					    (struct client_state *)0,
					    packet -> options,
					    (struct option_state *)0,
					    &global_scope, oc, MDL)) {
			return 0;
		}
		if (data.len != 4) {
			return 0;
		}
		ia.len = 4;
		memcpy (ia.iabuf, data.data, 4);
		data_string_forget (&data, MDL);
	} else {
		ia.len = 4;
		memcpy (ia.iabuf, &packet -> raw -> giaddr, 4);
	}

	/* If we know the subnet on which the IP address lives, use it. */
	if (find_subnet (&subnet, ia, MDL)) {
		shared_network_reference (&packet -> shared_network,
					  subnet -> shared_network, MDL);
		subnet_dereference (&subnet, MDL);
		return 1;
	}

	/* Otherwise, fail. */
	return 0;
}
