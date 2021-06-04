/* confpars.c

   Parser for dhcpd config file... */

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
"$Id: confpars.c,v 1.143.2.8 2001/10/04 22:08:35 mellon Exp $ Copyright (c) 1995-2001 The Internet Software Consortium.  All rights reserved.\n";
#endif /* not lint */

#include "dhcpd.h"

static TIME parsed_time;

#if defined (TRACING)
trace_type_t *trace_readconf_type;
trace_type_t *trace_readleases_type;

void parse_trace_setup ()
{
	trace_readconf_type = trace_type_register ("readconf", (void *)0,
						   trace_conf_input,
						   trace_conf_stop, MDL);
	trace_readleases_type = trace_type_register ("readleases", (void *)0,
						     trace_conf_input,
						     trace_conf_stop, MDL);
}
#endif

/* conf-file :== parameters declarations END_OF_FILE
   parameters :== <nil> | parameter | parameters parameter
   declarations :== <nil> | declaration | declarations declaration */

isc_result_t readconf ()
{
	return read_conf_file (path_dhcpd_conf, root_group, ROOT_GROUP, 0);
}

isc_result_t read_conf_file (const char *filename, struct group *group,
			     int group_type, int leasep)
{
	int file;
	struct parse *cfile;
	isc_result_t status;
#if defined (TRACING)
	char *fbuf, *dbuf;
	off_t flen;
	int result;
	unsigned tflen, ulen;
	trace_type_t *ttype;

	if (leasep)
		ttype = trace_readleases_type;
	else
		ttype = trace_readconf_type;

	/* If we're in playback, we need to snarf the contents of the
	   named file out of the playback file rather than trying to
	   open and read it. */
	if (trace_playback ()) {
		dbuf = (char *)0;
		tflen = 0;
		status = trace_get_file (ttype, filename, &tflen, &dbuf);
		if (status != ISC_R_SUCCESS)
			return status;
		ulen = tflen;

		/* What we get back is filename\0contents, where contents is
		   terminated just by the length.  So we figure out the length
		   of the filename, and subtract that and the NUL from the
		   total length to get the length of the contents of the file.
		   We make fbuf a pointer to the contents of the file, and
		   leave dbuf as it is so we can free it later. */
		tflen = strlen (dbuf);
		ulen = ulen - tflen - 1;
		fbuf = dbuf + tflen + 1;
		goto memfile;
	}
#endif

	if ((file = open (filename, O_RDONLY)) < 0) {
		if (leasep) {
			log_error ("Can't open lease database %s: %m --",
				   path_dhcpd_db);
			log_error ("  check for failed database %s!",
				   "rewrite attempt");
			log_error ("Please read the dhcpd.leases manual%s",
				   " page if you");
			log_fatal ("don't know what to do about this.");
		} else {
			log_fatal ("Can't open %s: %m", filename);
		}
	}

	cfile = (struct parse *)0;
#if defined (TRACING)
	flen = lseek (file, (off_t)0, SEEK_END);
	if (flen < 0) {
	      boom:
		log_fatal ("Can't lseek on %s: %m", filename);
	}
	if (lseek (file, (off_t)0, SEEK_SET) < 0)
		goto boom;
	/* Can't handle files greater than 2^31-1. */
	if (flen > 0x7FFFFFFFUL)
		log_fatal ("%s: file is too long to buffer.", filename);
	ulen = flen;

	/* Allocate a buffer that will be what's written to the tracefile,
	   and also will be what we parse from. */
	tflen = strlen (filename);
	dbuf = dmalloc (ulen + tflen + 1, MDL);
	if (!dbuf)
		log_fatal ("No memory for %s (%d bytes)",
			   filename, ulen);

	/* Copy the name into the beginning, nul-terminated. */
	strcpy (dbuf, filename);

	/* Load the file in after the NUL. */
	fbuf = dbuf + tflen + 1;
	result = read (file, fbuf, ulen);
	if (result < 0)
		log_fatal ("Can't read in %s: %m", filename);
	if (result != ulen)
		log_fatal ("%s: short read of %d bytes instead of %d.",
			   filename, ulen, result);
      memfile:
	/* If we're recording, write out the filename and file contents. */
	if (trace_record ())
		trace_write_packet (ttype, ulen + tflen + 1, dbuf, MDL);
	new_parse (&cfile, -1, fbuf, ulen, filename, 0); /* XXX */
#else
	new_parse (&cfile, file, (char *)0, 0, filename, 0);
#endif
	if (leasep)
		status = lease_file_subparse (cfile);
	else
		status = conf_file_subparse (cfile, group, group_type);
	end_parse (&cfile);
#if defined (TRACING)
	dfree (dbuf, MDL);
#endif
	close (file);
	return status;
}

#if defined (TRACING)
void trace_conf_input (trace_type_t *ttype, unsigned len, char *data)
{
	char *fbuf;
	unsigned flen;
	unsigned tflen;
	struct parse *cfile = (struct parse *)0;
	static int postconf_initialized;
	static int leaseconf_initialized;
	
	/* Do what's done above, except that we don't have to read in the
	   data, because it's already been read for us. */
	tflen = strlen (data);
	flen = len - tflen - 1;
	fbuf = data + tflen + 1;

	/* If we're recording, write out the filename and file contents. */
	if (trace_record ())
		trace_write_packet (ttype, len, data, MDL);
	new_parse (&cfile, -1, fbuf, flen, data, 0);
	if (ttype == trace_readleases_type)
		lease_file_subparse (cfile);
	else
		conf_file_subparse (cfile, root_group, ROOT_GROUP);
	end_parse (&cfile);

	/* Postconfiguration needs to be done after the config file
	   has been loaded. */
	if (!postconf_initialized && ttype == trace_readconf_type) {
		postconf_initialization (0);
		postconf_initialized = 1;
	}

	if (!leaseconf_initialized && ttype == trace_readleases_type) {
		db_startup (0);
		leaseconf_initialized = 1;
		postdb_startup ();
	}
}

void trace_conf_stop (trace_type_t *ttype) { }
#endif

/* conf-file :== parameters declarations END_OF_FILE
   parameters :== <nil> | parameter | parameters parameter
   declarations :== <nil> | declaration | declarations declaration */

isc_result_t conf_file_subparse (struct parse *cfile, struct group *group,
				 int group_type)
{
	const char *val;
	enum dhcp_token token;
	int declaration = 0;
	int status;

	do {
		token = peek_token (&val, (unsigned *)0, cfile);
		if (token == END_OF_FILE)
			break;
		declaration = parse_statement (cfile, group, group_type,
					       (struct host_decl *)0,
					       declaration);
	} while (1);
	token = next_token (&val, (unsigned *)0, cfile);

	status = cfile -> warnings_occurred ? ISC_R_BADPARSE : ISC_R_SUCCESS;
	return status;
}

/* lease-file :== lease-declarations END_OF_FILE
   lease-statments :== <nil>
   		     | lease-declaration
		     | lease-declarations lease-declaration */

isc_result_t lease_file_subparse (struct parse *cfile)
{
	const char *val;
	enum dhcp_token token;
	isc_result_t status;

	do {
		token = next_token (&val, (unsigned *)0, cfile);
		if (token == END_OF_FILE)
			break;
		if (token == LEASE) {
			struct lease *lease = (struct lease *)0;
			if (parse_lease_declaration (&lease, cfile)) {
				enter_lease (lease);
				lease_dereference (&lease, MDL);
			} else
				parse_warn (cfile,
					    "possibly corrupt lease file");
		} else if (token == HOST) {
			parse_host_declaration (cfile, root_group);
		} else if (token == GROUP) {
			parse_group_declaration (cfile, root_group);
#if defined (FAILOVER_PROTOCOL)
		} else if (token == FAILOVER) {
			parse_failover_state_declaration
				(cfile, (dhcp_failover_state_t *)0);
#endif
		} else {
			log_error ("Corrupt lease file - possible data loss!");
			skip_to_semi (cfile);
		}

	} while (1);

	status = cfile -> warnings_occurred ? ISC_R_BADPARSE : ISC_R_SUCCESS;
	return status;
}

/* statement :== parameter | declaration

   parameter :== timestamp
   	       | DEFAULT_LEASE_TIME lease_time
	       | MAX_LEASE_TIME lease_time
	       | DYNAMIC_BOOTP_LEASE_CUTOFF date
	       | DYNAMIC_BOOTP_LEASE_LENGTH lease_time
	       | BOOT_UNKNOWN_CLIENTS boolean
	       | ONE_LEASE_PER_CLIENT boolean
	       | GET_LEASE_HOSTNAMES boolean
	       | USE_HOST_DECL_NAME boolean
	       | NEXT_SERVER ip-addr-or-hostname SEMI
	       | option_parameter
	       | SERVER-IDENTIFIER ip-addr-or-hostname SEMI
	       | FILENAME string-parameter
	       | SERVER_NAME string-parameter
	       | hardware-parameter
	       | fixed-address-parameter
	       | ALLOW allow-deny-keyword
	       | DENY allow-deny-keyword
	       | USE_LEASE_ADDR_FOR_DEFAULT_ROUTE boolean
	       | AUTHORITATIVE
	       | NOT AUTHORITATIVE

   declaration :== host-declaration
		 | group-declaration
		 | shared-network-declaration
		 | subnet-declaration
		 | VENDOR_CLASS class-declaration
		 | USER_CLASS class-declaration
		 | RANGE address-range-declaration */

int parse_statement (cfile, group, type, host_decl, declaration)
	struct parse *cfile;
	struct group *group;
	int type;
	struct host_decl *host_decl;
	int declaration;
{
	enum dhcp_token token;
	const char *val;
	struct shared_network *share;
	char *t, *n;
	struct expression *expr;
	struct data_string data;
	struct hardware hardware;
	struct executable_statement *et, *ep;
	struct option *option;
	struct option_cache *cache;
	int lose;
	struct data_string key_id;
	int known;
	isc_result_t status;

	token = peek_token (&val, (unsigned *)0, cfile);

	switch (token) {
	      case INCLUDE:
		next_token (&val, (unsigned *)0, cfile);
		token = next_token (&val, (unsigned *)0, cfile);
		if (token != STRING) {
			parse_warn (cfile, "filename string expected.");
			skip_to_semi (cfile);
		} else {
			status = read_conf_file (val, group, type, 0);
			if (status != ISC_R_SUCCESS)
				parse_warn (cfile, "%s: bad parse.", val);
			parse_semi (cfile);
		}
		return 1;
		
	      case HOST:
		next_token (&val, (unsigned *)0, cfile);
		if (type != HOST_DECL && type != CLASS_DECL)
			parse_host_declaration (cfile, group);
		else {
			parse_warn (cfile,
				    "host declarations not allowed here.");
			skip_to_semi (cfile);
		}
		return 1;

	      case GROUP:
		next_token (&val, (unsigned *)0, cfile);
		if (type != HOST_DECL && type != CLASS_DECL)
			parse_group_declaration (cfile, group);
		else {
			parse_warn (cfile,
				    "group declarations not allowed here.");
			skip_to_semi (cfile);
		}
		return 1;

	      case TIMESTAMP:
		next_token (&val, (unsigned *)0, cfile);
		parsed_time = parse_timestamp (cfile);
		break;

	      case SHARED_NETWORK:
		next_token (&val, (unsigned *)0, cfile);
		if (type == SHARED_NET_DECL ||
		    type == HOST_DECL ||
		    type == SUBNET_DECL ||
		    type == CLASS_DECL) {
			parse_warn (cfile, "shared-network parameters not %s.",
				    "allowed here");
			skip_to_semi (cfile);
			break;
		}

		parse_shared_net_declaration (cfile, group);
		return 1;

	      case SUBNET:
		next_token (&val, (unsigned *)0, cfile);
		if (type == HOST_DECL || type == SUBNET_DECL ||
		    type == CLASS_DECL) {
			parse_warn (cfile,
				    "subnet declarations not allowed here.");
			skip_to_semi (cfile);
			return 1;
		}

		/* If we're in a subnet declaration, just do the parse. */
		if (group -> shared_network) {
			parse_subnet_declaration (cfile,
						  group -> shared_network);
			break;
		}

		/* Otherwise, cons up a fake shared network structure
		   and populate it with the lone subnet... */

		share = (struct shared_network *)0;
		status = shared_network_allocate (&share, MDL);
		if (status != ISC_R_SUCCESS)
			log_fatal ("Can't allocate shared subnet: %s",
				   isc_result_totext (status));
		if (!clone_group (&share -> group, group, MDL))
			log_fatal ("Can't allocate group for shared net");
		shared_network_reference (&share -> group -> shared_network,
					  share, MDL);

		parse_subnet_declaration (cfile, share);

		/* share -> subnets is the subnet we just parsed. */
		if (share -> subnets) {
			interface_reference (&share -> interface,
					     share -> subnets -> interface,
					     MDL);

			/* Make the shared network name from network number. */
			n = piaddrmask (share -> subnets -> net,
					share -> subnets -> netmask, MDL);
			share -> name = n;

			/* Copy the authoritative parameter from the subnet,
			   since there is no opportunity to declare it here. */
			share -> group -> authoritative =
				share -> subnets -> group -> authoritative;
			enter_shared_network (share);
		}
		shared_network_dereference (&share, MDL);
		return 1;

	      case VENDOR_CLASS:
		next_token (&val, (unsigned *)0, cfile);
		if (type == CLASS_DECL) {
			parse_warn (cfile,
				    "class declarations not allowed here.");
			skip_to_semi (cfile);
			break;
		}
		parse_class_declaration ((struct class **)0, cfile, group, 0);
		return 1;

	      case USER_CLASS:
		next_token (&val, (unsigned *)0, cfile);
		if (type == CLASS_DECL) {
			parse_warn (cfile,
				    "class declarations not allowed here.");
			skip_to_semi (cfile);
			break;
		}
		parse_class_declaration ((struct class **)0, cfile, group, 1);
		return 1;

	      case CLASS:
		next_token (&val, (unsigned *)0, cfile);
		if (type == CLASS_DECL) {
			parse_warn (cfile,
				    "class declarations not allowed here.");
			skip_to_semi (cfile);
			break;
		}
		parse_class_declaration ((struct class **)0, cfile, group, 2);
		return 1;

	      case SUBCLASS:
		next_token (&val, (unsigned *)0, cfile);
		if (type == CLASS_DECL) {
			parse_warn (cfile,
				    "class declarations not allowed here.");
			skip_to_semi (cfile);
			break;
		}
		parse_class_declaration ((struct class **)0, cfile, group, 3);
		return 1;

	      case HARDWARE:
		next_token (&val, (unsigned *)0, cfile);
		memset (&hardware, 0, sizeof hardware);
		parse_hardware_param (cfile, &hardware);
		if (host_decl)
			host_decl -> interface = hardware;
		else
			parse_warn (cfile, "hardware address parameter %s",
				    "not allowed here.");
		break;

	      case FIXED_ADDR:
		next_token (&val, (unsigned *)0, cfile);
		cache = (struct option_cache *)0;
		if (parse_fixed_addr_param (&cache, cfile)) {
			if (host_decl) {
				if (host_decl -> fixed_addr) {
					option_cache_dereference (&cache, MDL);
					parse_warn (cfile,
						    "Only one fixed address%s",
						    " declaration per host.");
				} else {
					host_decl -> fixed_addr = cache;
				}
			} else {
				parse_warn (cfile,
					    "fixed-address parameter not %s",
					    "allowed here.");
				option_cache_dereference (&cache, MDL);
			}
		}
		break;

	      case POOL:
		next_token (&val, (unsigned *)0, cfile);
		if (type != SUBNET_DECL && type != SHARED_NET_DECL) {
			parse_warn (cfile, "pool declared outside of network");
		}
		if (type == POOL_DECL) {
			parse_warn (cfile, "pool declared within pool.");
		}
		parse_pool_statement (cfile, group, type);
		return declaration;

	      case RANGE:
		next_token (&val, (unsigned *)0, cfile);
		if (type != SUBNET_DECL || !group -> subnet) {
			parse_warn (cfile,
				    "range declaration not allowed here.");
			skip_to_semi (cfile);
			return declaration;
		}
		parse_address_range (cfile, group, type, (struct pool *)0);
		return declaration;

	      case TOKEN_NOT:
		token = next_token (&val, (unsigned *)0, cfile);
		token = next_token (&val, (unsigned *)0, cfile);
		switch (token) {
		      case AUTHORITATIVE:
			group -> authoritative = 0;
			goto authoritative;
		      default:
			parse_warn (cfile, "expecting assertion");
			skip_to_semi (cfile);
			break;
		}
		break;
	      case AUTHORITATIVE:
		token = next_token (&val, (unsigned *)0, cfile);
		group -> authoritative = 1;
	      authoritative:
		if (type == HOST_DECL)
			parse_warn (cfile, "authority makes no sense here."); 
		parse_semi (cfile);
		break;

		/* "server-identifier" is a special hack, equivalent to
		   "option dhcp-server-identifier". */
	      case SERVER_IDENTIFIER:
		option = dhcp_universe.options [DHO_DHCP_SERVER_IDENTIFIER];
		token = next_token (&val, (unsigned *)0, cfile);
		goto finish_option;

	      case OPTION:
		token = next_token (&val, (unsigned *)0, cfile);
		token = peek_token (&val, (unsigned *)0, cfile);
		if (token == SPACE) {
			if (type != ROOT_GROUP) {
				parse_warn (cfile,
					    "option space definitions %s",
					    "may not be scoped.");
				skip_to_semi (cfile);
				break;
			}
			parse_option_space_decl (cfile);
			return declaration;
		}

		known = 0;
		option = parse_option_name (cfile, 1, &known);
		if (option) {
			token = peek_token (&val, (unsigned *)0, cfile);
			if (token == CODE) {
				if (type != ROOT_GROUP) {
					parse_warn (cfile,
						    "option definitions%s",
						    " may not be scoped.");
					skip_to_semi (cfile);
					free_option (option, MDL);
					break;
				}
				next_token (&val, (unsigned *)0, cfile);
				if (!parse_option_code_definition (cfile,
								   option))
					free_option (option, MDL);
				return declaration;
			}

			/* If this wasn't an option code definition, don't
			   allow an unknown option. */
			if (!known) {
				parse_warn (cfile, "unknown option %s.%s",
					    option -> universe -> name,
					    option -> name);
				skip_to_semi (cfile);
				free_option (option, MDL);
				return declaration;
			}

		      finish_option:
			et = (struct executable_statement *)0;
			if (!parse_option_statement
				(&et, cfile, 1, option,
				 supersede_option_statement))
				return declaration;
			goto insert_statement;
		} else
			return declaration;

		break;

	      case FAILOVER:
		if (type != ROOT_GROUP && type != SHARED_NETWORK) {
			parse_warn (cfile, "failover peers may only be %s",
				    "defined in shared-network");
			log_error ("declarations and the outer scope.");
			skip_to_semi (cfile);
			break;
		}
		token = next_token (&val, (unsigned *)0, cfile);
#if defined (FAILOVER_PROTOCOL)
		parse_failover_peer (cfile, group, type);
#else
		parse_warn (cfile, "No failover support.");
		skip_to_semi (cfile);
#endif
		break;

	      default:
		et = (struct executable_statement *)0;
		lose = 0;
		if (!parse_executable_statement (&et, cfile, &lose,
						 context_any)) {
			if (!lose) {
				if (declaration)
					parse_warn (cfile,
						    "expecting a declaration");
				else
					parse_warn (cfile,
						    "expecting a parameter %s",
						    "or declaration");
				skip_to_semi (cfile);
			}
			return declaration;
		}
		if (!et)
			return declaration;
	      insert_statement:
		if (group -> statements) {
			int multi = 0;

			/* If this set of statements is only referenced
			   by this group, just add the current statement
			   to the end of the chain. */
			for (ep = group -> statements; ep -> next;
			     ep = ep -> next)
				if (ep -> refcnt > 1) /* XXX */
					multi = 1;
			if (!multi) {
				executable_statement_reference (&ep -> next,
								et, MDL);
				executable_statement_dereference (&et, MDL);
				return declaration;
			}

			/* Otherwise, make a parent chain, and put the
			   current group statements first and the new
			   statement in the next pointer. */
			ep = (struct executable_statement *)0;
			if (!executable_statement_allocate (&ep, MDL))
				log_fatal ("No memory for statements.");
			ep -> op = statements_statement;
			executable_statement_reference (&ep -> data.statements,
							group -> statements,
							MDL);
			executable_statement_reference (&ep -> next, et, MDL);
			executable_statement_dereference (&group -> statements,
							  MDL);
			executable_statement_reference (&group -> statements,
							ep, MDL);
			executable_statement_dereference (&ep, MDL);
		} else {
			executable_statement_reference (&group -> statements,
							et, MDL);
		}
		executable_statement_dereference (&et, MDL);
		return declaration;
	}

	return 0;
}

#if defined (FAILOVER_PROTOCOL)
void parse_failover_peer (cfile, group, type)
	struct parse *cfile;
	struct group *group;
	int type;
{
	enum dhcp_token token;
	const char *val;
	dhcp_failover_state_t *peer;
	u_int32_t *tp;
	char *name;
	u_int32_t split;
	u_int8_t hba [32];
	unsigned hba_len = sizeof hba;
	int i;
	struct expression *expr;
	isc_result_t status;
	dhcp_failover_config_t *cp;

	token = next_token (&val, (unsigned *)0, cfile);
	if (token != PEER) {
		parse_warn (cfile, "expecting \"peer\"");
		skip_to_semi (cfile);
		return;
	}

	token = next_token (&val, (unsigned *)0, cfile);
	if (is_identifier (token) || token == STRING) {
		name = dmalloc (strlen (val) + 1, MDL);
		if (!name)
			log_fatal ("no memory for peer name %s", name);
		strcpy (name, val);
	} else {
		parse_warn (cfile, "expecting failover peer name.");
		skip_to_semi (cfile);
		return;
	}

	/* See if there's a peer declaration by this name. */
	peer = (dhcp_failover_state_t *)0;
	find_failover_peer (&peer, name, MDL);

	token = next_token (&val, (unsigned *)0, cfile);
	if (token == SEMI) {
		dfree (name, MDL);
		if (type != SHARED_NET_DECL)
			parse_warn (cfile, "failover peer reference not %s",
				    "in shared-network declaration");
		else {
			if (!peer) {
				parse_warn (cfile, "reference to unknown%s%s",
					    " failover peer ", name);
				return;
			}
			dhcp_failover_state_reference
				(&group -> shared_network -> failover_peer,
				 peer, MDL);
		}
		dhcp_failover_state_dereference (&peer, MDL);
		return;
	} else if (token == STATE) {
		if (!peer) {
			parse_warn (cfile, "state declaration for unknown%s%s",
				    " failover peer ", name);
			return;
		}
		parse_failover_state_declaration (cfile, peer);
		dhcp_failover_state_dereference (&peer, MDL);
		return;
	} else if (token != LBRACE) {
		parse_warn (cfile, "expecting left brace");
		skip_to_semi (cfile);
	}

	/* Make sure this isn't a redeclaration. */
	if (peer) {
		parse_warn (cfile, "redeclaration of failover peer %s", name);
		skip_to_rbrace (cfile, 1);
		dhcp_failover_state_dereference (&peer, MDL);
		return;
	}

	status = dhcp_failover_state_allocate (&peer, MDL);
	if (status != ISC_R_SUCCESS)
		log_fatal ("Can't allocate failover peer %s: %s",
			   name, isc_result_totext (status));

	/* Save the name. */
	peer -> name = name;

	do {
		cp = &peer -> me;
	      peer:
		token = next_token (&val, (unsigned *)0, cfile);
		switch (token) {
		      case RBRACE:
			break;

		      case PRIMARY:
			peer -> i_am = primary;
			break;

		      case SECONDARY:
			peer -> i_am = secondary;
			if (peer -> hba)
				parse_warn (cfile,
					    "secondary may not define %s",
					    "load balance settings.");
			break;

		      case PEER:
			cp = &peer -> partner;
			goto peer;

		      case ADDRESS:
			expr = (struct expression *)0;
			if (!parse_ip_addr_or_hostname (&expr, cfile, 0)) {
				skip_to_rbrace (cfile, 1);
				dhcp_failover_state_dereference (&peer, MDL);
				return;
			}
			option_cache (&cp -> address,
				      (struct data_string *)0, expr,
				      (struct option *)0, MDL);
			expression_dereference (&expr, MDL);
			break;

		      case PORT:
			token = next_token (&val, (unsigned *)0, cfile);
			if (token != NUMBER) {
				parse_warn (cfile, "expecting number");
				skip_to_rbrace (cfile, 1);
			}
			cp -> port = atoi (val);
			break;

		      case MAX_RESPONSE_DELAY:
			tp = &cp -> max_response_delay;
		      parse_idle:
			token = next_token (&val, (unsigned *)0, cfile);
			if (token != NUMBER) {
				parse_warn (cfile, "expecting number.");
				skip_to_rbrace (cfile, 1);
				dhcp_failover_state_dereference (&peer, MDL);
				return;
			}
			*tp = atoi (val);
			break;

		      case MAX_UNACKED_UPDATES:
			tp = &cp -> max_flying_updates;
			goto parse_idle;

		      case MCLT:
			tp = &peer -> mclt;
			goto parse_idle;

		      case HBA:
			hba_len = 32;
			if (peer -> i_am == secondary)
				parse_warn (cfile,
					    "secondary may not define %s",
					    "load balance settings.");
			if (!parse_numeric_aggregate (cfile, hba, &hba_len,
						      COLON, 16, 8)) {
				skip_to_rbrace (cfile, 1);
				dhcp_failover_state_dereference (&peer, MDL);
				return;
			}
			if (hba_len != 32) {
				parse_warn (cfile,
					    "HBA must be exactly 32 bytes.");
				dfree (hba, MDL);
				break;
			}
		      make_hba:
			peer -> hba = dmalloc (32, MDL);
			if (!peer -> hba) {
				dfree (peer -> name, MDL);
				dfree (peer, MDL);
			}
			memcpy (peer -> hba, hba, 32);
			break;

		      case SPLIT:
			token = next_token (&val, (unsigned *)0, cfile);
			if (peer -> i_am == secondary)
				parse_warn (cfile,
					    "secondary may not define %s",
					    "load balance settings.");
			if (token != NUMBER) {
				parse_warn (cfile, "expecting number");
			      badsplit:
				skip_to_rbrace (cfile, 1);
				dhcp_failover_state_dereference (&peer, MDL);
				return;
			}
			split = atoi (val);
			if (split > 255) {
				parse_warn (cfile, "split must be < 256");
			} else {
				memset (hba, 0, sizeof hba);
				for (i = 0; i < split; i++) {
					if (i < split)
						hba [i / 8] |= (1 << (i & 7));
				}
				goto make_hba;
			}
			break;
			
		      case LOAD:
			token = next_token (&val, (unsigned *)0, cfile);
			if (token != BALANCE) {
				parse_warn (cfile, "expecting 'balance'");
			      badload:
				skip_to_rbrace (cfile, 1);
				break;
			}
			token = next_token (&val, (unsigned *)0, cfile);
			if (token != TOKEN_MAX) {
				parse_warn (cfile, "expecting 'max'");
				goto badload;
			}
			token = next_token (&val, (unsigned *)0, cfile);
			if (token != SECONDS) {
				parse_warn (cfile, "expecting 'secs'");
				goto badload;
			}
			token = next_token (&val, (unsigned *)0, cfile);
			if (token != NUMBER) {
				parse_warn (cfile, "expecting number");
				goto badload;
			}
			peer -> load_balance_max_secs = atoi (val);
			break;
			
		      default:
			parse_warn (cfile,
				    "invalid statement in peer declaration");
			skip_to_rbrace (cfile, 1);
			dhcp_failover_state_dereference (&peer, MDL);
			return;
		}
		if (token != RBRACE && !parse_semi (cfile)) {
			skip_to_rbrace (cfile, 1);
			dhcp_failover_state_dereference (&peer, MDL);
			return;
		}
	} while (token != RBRACE);
		
	if (peer -> i_am == primary) {
	    if (!peer -> hba) {
		parse_warn (cfile,
			    "primary failover server must have hba or split.");
	    } else if (!peer -> mclt) {
		parse_warn (cfile,
			    "primary failover server must have mclt.");
	    }
	}

	if (type == SHARED_NET_DECL) {
		group -> shared_network -> failover_peer = peer;
	}

	/* Set the initial state. */
	if (peer -> i_am == primary) {
		peer -> me.state = recover;
		peer -> me.stos = cur_time;
		peer -> partner.state = unknown_state;
		peer -> partner.stos = cur_time;
	} else {
		peer -> me.state = recover;
		peer -> me.stos = cur_time;
		peer -> partner.state = unknown_state;
		peer -> partner.stos = cur_time;
	}

	status = enter_failover_peer (peer);
	if (status != ISC_R_SUCCESS)
		parse_warn (cfile, "failover peer %s: %s",
			    peer -> name, isc_result_totext (status));
	dhcp_failover_state_dereference (&peer, MDL);
}

void parse_failover_state_declaration (struct parse *cfile,
				       dhcp_failover_state_t *peer)
{
	enum dhcp_token token;
	const char *val;
	char *name;
	dhcp_failover_state_t *state;
	dhcp_failover_config_t *cp;

	if (!peer) {
		token = next_token (&val, (unsigned *)0, cfile);
		if (token != PEER) {
			parse_warn (cfile, "expecting \"peer\"");
			skip_to_semi (cfile);
			return;
		}

		token = next_token (&val, (unsigned *)0, cfile);
		if (is_identifier (token) || token == STRING) {
			name = dmalloc (strlen (val) + 1, MDL);
			if (!name)
				log_fatal ("failover peer name %s: no memory",
					   name);
			strcpy (name, val);
		} else {
			parse_warn (cfile, "expecting failover peer name.");
			skip_to_semi (cfile);
			return;
		}

		/* See if there's a peer declaration by this name. */
		state = (dhcp_failover_state_t *)0;
		find_failover_peer (&state, name, MDL);
		if (!state) {
			parse_warn (cfile, "unknown failover peer: %s", name);
			skip_to_semi (cfile);
			return;
		}

		token = next_token (&val, (unsigned *)0, cfile);
		if (token != STATE) {
			parse_warn (cfile, "expecting 'state'");
			if (token != SEMI)
				skip_to_semi (cfile);
			return;
		}
	} else {
		state = (dhcp_failover_state_t *)0;
		dhcp_failover_state_reference (&state, peer, MDL);
	}
	token = next_token (&val, (unsigned *)0, cfile);
	if (token != LBRACE) {
		parse_warn (cfile, "expecting left brace");
		if (token != SEMI)
			skip_to_semi (cfile);
		dhcp_failover_state_dereference (&state, MDL);
		return;
	}
	do {
		token = next_token (&val, (unsigned *)0, cfile);
		switch (token) {
		      case RBRACE:
			break;
		      case MY:
			cp = &state -> me;
		      do_state:
			token = next_token (&val, (unsigned *)0, cfile);
			if (token != STATE) {
				parse_warn (cfile, "expecting 'state'");
				goto bogus;
			}
			parse_failover_state (cfile,
					      &cp -> state, &cp -> stos);
			break;

		      case PARTNER:
			cp = &state -> partner;
			goto do_state;

		      case MCLT:
			if (state -> i_am == primary) {
				parse_warn (cfile,
					    "mclt not valid for primary");
				goto bogus;
			}
			token = next_token (&val, (unsigned *)0, cfile);
			if (token != NUMBER) {
				parse_warn (cfile, "expecting a number.");
				goto bogus;
			}
			state -> mclt = atoi (val);
			parse_semi (cfile);
			break;
			
		      default:
			parse_warn (cfile, "expecting state setting.");
		      bogus:
			skip_to_rbrace (cfile, 1);	
			dhcp_failover_state_dereference (&state, MDL);
			return;
		}
	} while (token != RBRACE);
	dhcp_failover_state_dereference (&state, MDL);
}

void parse_failover_state (cfile, state, stos)
	struct parse *cfile;
	enum failover_state *state;
	TIME *stos;
{
	enum dhcp_token token;
	const char *val;
	enum failover_state state_in;
	TIME stos_in;

	token = next_token (&val, (unsigned *)0, cfile);
	switch (token) {
	      case UNKNOWN_STATE:
		state_in = unknown_state;
		break;

	      case PARTNER_DOWN:
		state_in = partner_down;
		break;

	      case NORMAL:
		state_in = normal;
		break;

	      case COMMUNICATIONS_INTERRUPTED:
		state_in = communications_interrupted;
		break;

	      case RESOLUTION_INTERRUPTED:
		state_in = resolution_interrupted;
		break;

	      case POTENTIAL_CONFLICT:
		state_in = potential_conflict;
		break;

	      case RECOVER:
		state_in = recover;
		break;
		
	      case RECOVER_WAIT:
		state_in = recover_wait;
		break;
		
	      case RECOVER_DONE:
		state_in = recover_done;
		break;
		
	      case SHUTDOWN:
		state_in = shut_down;
		break;
		
	      case PAUSED:
		state_in = paused;
		break;
		
	      case STARTUP:
		state_in = startup;
		break;

	      default:
		parse_warn (cfile, "unknown failover state");
		skip_to_semi (cfile);
		return;
	}

	token = next_token (&val, (unsigned *)0, cfile);
	if (token == SEMI) {
		stos_in = cur_time;
	} else {
		if (token != AT) {
			parse_warn (cfile, "expecting \"at\"");
			skip_to_semi (cfile);
			return;
		}
		
		stos_in = parse_date (cfile);
		if (!stos_in)
			return;
	}

	/* Now that we've apparently gotten a clean parse, we
	   can trust that this is a state that was fully committed to
	   disk, so we can install it. */
	*stos = stos_in;
	*state = state_in;
}
#endif /* defined (FAILOVER_PROTOCOL) */

void parse_pool_statement (cfile, group, type)
	struct parse *cfile;
	struct group *group;
	int type;
{
	enum dhcp_token token;
	const char *val;
	int done = 0;
	struct pool *pool, **p;
	struct permit *permit;
	struct permit **permit_head;
	int declaration = 0;
	isc_result_t status;

	pool = (struct pool *)0;
	status = pool_allocate (&pool, MDL);
	if (status != ISC_R_SUCCESS)
		log_fatal ("no memory for pool: %s",
			   isc_result_totext (status));

	if (!clone_group (&pool -> group, group, MDL))
		log_fatal ("can't clone pool group.");

	if (type == SUBNET_DECL)
		shared_network_reference (&pool -> shared_network,
					  group -> subnet -> shared_network,
					  MDL);
	else
		shared_network_reference (&pool -> shared_network,
					  group -> shared_network, MDL);

#if defined (FAILOVER_PROTOCOL)
	/* Inherit the failover peer from the shared network. */
	if (pool -> shared_network -> failover_peer)
	    dhcp_failover_state_reference
		    (&pool -> failover_peer, 
		     pool -> shared_network -> failover_peer, MDL);
#endif

	if (!parse_lbrace (cfile)) {
		pool_dereference (&pool, MDL);
		return;
	}

	do {
		token = peek_token (&val, (unsigned *)0, cfile);
		switch (token) {
		      case NO:
			next_token (&val, (unsigned *)0, cfile);
			token = next_token (&val, (unsigned *)0, cfile);
			if (token != FAILOVER ||
			    (token = next_token (&val, (unsigned *)0,
						 cfile)) != PEER) {
				parse_warn (cfile,
					    "expecting \"failover peer\".");
				skip_to_semi (cfile);
				continue;
			}
#if defined (FAILOVER_PROTOCOL)
			if (pool -> failover_peer)
				dhcp_failover_state_dereference
					(&pool -> failover_peer, MDL);
#endif
			break;
				
#if defined (FAILOVER_PROTOCOL)
		      case FAILOVER:
			next_token (&val, (unsigned *)0, cfile);
			token = next_token (&val, (unsigned *)0, cfile);
			if (token != PEER) {
				parse_warn (cfile, "expecting 'peer'.");
				skip_to_semi (cfile);
				break;
			}
			token = next_token (&val, (unsigned *)0, cfile);
			if (token != STRING) {
				parse_warn (cfile, "expecting string.");
				skip_to_semi (cfile);
				break;
			}
			if (pool -> failover_peer)
				dhcp_failover_state_dereference
					(&pool -> failover_peer, MDL);
			status = find_failover_peer (&pool -> failover_peer,
						     val, MDL);
			if (status != ISC_R_SUCCESS)
				parse_warn (cfile,
					    "failover peer %s: %s", val,
					    isc_result_totext (status));
			else
				pool -> failover_peer -> pool_count++;
			parse_semi (cfile);
			break;
#endif

		      case RANGE:
			next_token (&val, (unsigned *)0, cfile);
			parse_address_range (cfile, group, type, pool);
			break;
		      case ALLOW:
			permit_head = &pool -> permit_list;
		      get_permit:
			permit = new_permit (MDL);
			if (!permit)
				log_fatal ("no memory for permit");
			next_token (&val, (unsigned *)0, cfile);
			token = next_token (&val, (unsigned *)0, cfile);
			switch (token) {
			      case UNKNOWN:
				permit -> type = permit_unknown_clients;
			      get_clients:
				if (next_token (&val, (unsigned *)0,
						cfile) != CLIENTS) {
					parse_warn (cfile,
						    "expecting \"clients\"");
					skip_to_semi (cfile);
					free_permit (permit, MDL);
					continue;
				}
				break;
				
			      case UNKNOWN_CLIENTS:
				permit -> type = permit_unknown_clients;
				break;

			      case KNOWN:
				permit -> type = permit_known_clients;
				goto get_clients;
				
			      case AUTHENTICATED:
				permit -> type = permit_authenticated_clients;
				goto get_clients;
				
			      case UNAUTHENTICATED:
				permit -> type =
					permit_unauthenticated_clients;
				goto get_clients;

			      case ALL:
				permit -> type = permit_all_clients;
				goto get_clients;
				break;
				
			      case DYNAMIC:
				permit -> type = permit_dynamic_bootp_clients;
				if (next_token (&val, (unsigned *)0,
						cfile) != TOKEN_BOOTP) {
					parse_warn (cfile,
						    "expecting \"bootp\"");
					skip_to_semi (cfile);
					free_permit (permit, MDL);
					continue;
				}
				goto get_clients;
				
			      case MEMBERS:
				if (next_token (&val, (unsigned *)0,
						cfile) != OF) {
					parse_warn (cfile, "expecting \"of\"");
					skip_to_semi (cfile);
					free_permit (permit, MDL);
					continue;
				}
				if (next_token (&val, (unsigned *)0,
						cfile) != STRING) {
					parse_warn (cfile,
						    "expecting class name.");
					skip_to_semi (cfile);
					free_permit (permit, MDL);
					continue;
				}
				permit -> type = permit_class;
				permit -> class = (struct class *)0;
				find_class (&permit -> class, val, MDL);
				if (!permit -> class)
					parse_warn (cfile,
						    "no such class: %s", val);
				break;

			      default:
				parse_warn (cfile, "expecting permit type.");
				skip_to_semi (cfile);
				break;
			}
			while (*permit_head)
				permit_head = &((*permit_head) -> next);
			*permit_head = permit;
			parse_semi (cfile);
			break;

		      case DENY:
			permit_head = &pool -> prohibit_list;
			goto get_permit;
			
		      case RBRACE:
			next_token (&val, (unsigned *)0, cfile);
			done = 1;
			break;

		      default:
			declaration = parse_statement (cfile, pool -> group,
						       POOL_DECL,
						       (struct host_decl *)0,
						       declaration);
			break;
		}
	} while (!done);

#if defined (FAILOVER_PROTOCOL)
	/* We can't do failover on a pool that supports dynamic bootp,
	   because BOOTP doesn't support leases, and failover absolutely
	   depends on lease timing. */
	if (pool -> failover_peer) {
		for (permit = pool -> permit_list;
		     permit; permit = permit -> next) {
			if (permit -> type == permit_dynamic_bootp_clients ||
			    permit -> type == permit_all_clients) {
				  dynamic_bootp_clash:
				parse_warn (cfile,
					    "pools with failover peers %s",
					    "may not permit dynamic bootp.");
				log_error ("Either write a \"no failover\" %s",
					   "statement and use disjoint");
				log_error ("pools, or don't permit dynamic%s",
					   " bootp.");
				log_error ("This is a protocol limitation,%s",
					   " not an ISC DHCP limitation, so");
				log_error ("please don't request an %s",
					   "enhancement or ask why this is.");
				goto clash_testing_done;
			}
		}
		if (!pool -> permit_list) {
			if (!pool -> prohibit_list)
				goto dynamic_bootp_clash;

			for (permit = pool -> prohibit_list; permit;
			     permit = permit -> next) {
				if (permit -> type ==
				    permit_dynamic_bootp_clients ||
				    permit -> type == permit_all_clients)
					goto clash_testing_done;
			}
		}
	}
      clash_testing_done:				
#endif /* FAILOVER_PROTOCOL */

	p = &pool -> shared_network -> pools;
	for (; *p; p = &((*p) -> next))
		;
	pool_reference (p, pool, MDL);
	pool_dereference (&pool, MDL);
}

/* boolean :== ON SEMI | OFF SEMI | TRUE SEMI | FALSE SEMI */

int parse_boolean (cfile)
	struct parse *cfile;
{
	enum dhcp_token token;
	const char *val;
	int rv;

	token = next_token (&val, (unsigned *)0, cfile);
	if (!strcasecmp (val, "true")
	    || !strcasecmp (val, "on"))
		rv = 1;
	else if (!strcasecmp (val, "false")
		 || !strcasecmp (val, "off"))
		rv = 0;
	else {
		parse_warn (cfile,
			    "boolean value (true/false/on/off) expected");
		skip_to_semi (cfile);
		return 0;
	}
	parse_semi (cfile);
	return rv;
}

/* Expect a left brace; if there isn't one, skip over the rest of the
   statement and return zero; otherwise, return 1. */

int parse_lbrace (cfile)
	struct parse *cfile;
{
	enum dhcp_token token;
	const char *val;

	token = next_token (&val, (unsigned *)0, cfile);
	if (token != LBRACE) {
		parse_warn (cfile, "expecting left brace.");
		skip_to_semi (cfile);
		return 0;
	}
	return 1;
}


/* host-declaration :== hostname RBRACE parameters declarations LBRACE */

void parse_host_declaration (cfile, group)
	struct parse *cfile;
	struct group *group;
{
	const char *val;
	enum dhcp_token token;
	struct host_decl *host;
	char *name;
	int declaration = 0;
	int dynamicp = 0;
	int deleted = 0;
	isc_result_t status;

	name = parse_host_name (cfile);
	if (!name) {
		parse_warn (cfile, "expecting a name for host declaration.");
		skip_to_semi (cfile);
		return;
	}

	host = (struct host_decl *)0;
	status = host_allocate (&host, MDL);
	if (status != ISC_R_SUCCESS)
		log_fatal ("can't allocate host decl struct %s: %s",
			   name, isc_result_totext (status));
	host -> name = name;
	if (!clone_group (&host -> group, group, MDL)) {
		log_fatal ("can't clone group for host %s", name);
	      boom:
		host_dereference (&host, MDL);
		return;
	}

	if (!parse_lbrace (cfile))
		goto boom;

	do {
		token = peek_token (&val, (unsigned *)0, cfile);
		if (token == RBRACE) {
			token = next_token (&val, (unsigned *)0, cfile);
			break;
		}
		if (token == END_OF_FILE) {
			token = next_token (&val, (unsigned *)0, cfile);
			parse_warn (cfile, "unexpected end of file");
			break;
		}
		/* If the host declaration was created by the server,
		   remember to save it. */
		if (token == DYNAMIC) {
			dynamicp = 1;
			token = next_token (&val, (unsigned *)0, cfile);
			if (!parse_semi (cfile))
				break;
			continue;
		}
		/* If the host declaration was created by the server,
		   remember to save it. */
		if (token == TOKEN_DELETED) {
			deleted = 1;
			token = next_token (&val, (unsigned *)0, cfile);
			if (!parse_semi (cfile))
				break;
			continue;
		}

		if (token == GROUP) {
			struct group_object *go;
			token = next_token (&val, (unsigned *)0, cfile);
			token = next_token (&val, (unsigned *)0, cfile);
			if (token != STRING && !is_identifier (token)) {
				parse_warn (cfile,
					    "expecting string or identifier.");
				skip_to_rbrace (cfile, 1);
				break;
			}
			go = (struct group_object *)0;
			if (!group_hash_lookup (&go, group_name_hash,
						val, strlen (val), MDL)) {
			    parse_warn (cfile, "unknown group %s in host %s",
					val, host -> name);
			} else {
				if (host -> named_group)
					group_object_dereference
						(&host -> named_group, MDL);
				group_object_reference (&host -> named_group,
							go, MDL);
				group_object_dereference (&go, MDL);
			}
			if (!parse_semi (cfile))
				break;
			continue;
		}

		if (token == UID) {
			const char *s;
			unsigned char *t = 0;
			unsigned len;

			token = next_token (&val, (unsigned *)0, cfile);
			data_string_forget (&host -> client_identifier, MDL);

			/* See if it's a string or a cshl. */
			token = peek_token (&val, (unsigned *)0, cfile);
			if (token == STRING) {
				token = next_token (&val, &len, cfile);
				s = val;
				host -> client_identifier.terminated = 1;
			} else {
				len = 0;
				t = parse_numeric_aggregate
					(cfile,
					 (unsigned char *)0, &len, ':', 16, 8);
				if (!t) {
					parse_warn (cfile,
						    "expecting hex list.");
					skip_to_semi (cfile);
				}
				s = (const char *)t;
			}
			if (!buffer_allocate
			    (&host -> client_identifier.buffer,
			     len + host -> client_identifier.terminated, MDL))
				log_fatal ("no memory for uid for host %s.",
					   host -> name);
			host -> client_identifier.data =
				host -> client_identifier.buffer -> data;
			host -> client_identifier.len = len;
			memcpy (host -> client_identifier.buffer -> data, s,
				len + host -> client_identifier.terminated);
			if (t)
				dfree (t, MDL);

			if (!parse_semi (cfile))
				break;
			continue;
		}
		declaration = parse_statement (cfile, host -> group,
					       HOST_DECL, host,
					       declaration);
	} while (1);

	if (deleted) {
		struct host_decl *hp = (struct host_decl *)0;
		if (host_hash_lookup (&hp, host_name_hash,
				      (unsigned char *)host -> name,
				      strlen (host -> name), MDL)) {
			delete_host (hp, 0);
			host_dereference (&hp, MDL);
		}
	} else {
		if (host -> named_group && host -> named_group -> group) {
			if (host -> group -> statements ||
			    (host -> group -> authoritative !=
			     host -> named_group -> group -> authoritative)) {
				if (host -> group -> next)
				    group_dereference (&host -> group -> next,
						       MDL);
				group_reference (&host -> group -> next,
						 host -> named_group -> group,
						 MDL);
			} else {
				group_dereference (&host -> group, MDL);
				group_reference (&host -> group,
						 host -> named_group -> group,
						 MDL);
			}
		}
				
		if (dynamicp)
			host -> flags |= HOST_DECL_DYNAMIC;
		else
			host -> flags |= HOST_DECL_STATIC;

		status = enter_host (host, dynamicp, 0);
		if (status != ISC_R_SUCCESS)
			parse_warn (cfile, "host %s: %s", host -> name,
				    isc_result_totext (status));
	}
	host_dereference (&host, MDL);
}

/* class-declaration :== STRING LBRACE parameters declarations RBRACE
*/

int parse_class_declaration (cp, cfile, group, type)
	struct class **cp;
	struct parse *cfile;
	struct group *group;
	int type;
{
	const char *val;
	enum dhcp_token token;
	struct class *class = (struct class *)0, *pc = (struct class *)0;
	int declaration = 0;
	int lose = 0;
	struct data_string data;
	char *name;
	const char *tname;
	struct executable_statement *stmt = (struct executable_statement *)0;
	struct expression *expr;
	int new = 1;
	isc_result_t status;

	token = next_token (&val, (unsigned *)0, cfile);
	if (token != STRING) {
		parse_warn (cfile, "Expecting class name");
		skip_to_semi (cfile);
		return 0;
	}

	/* See if there's already a class with the specified name. */
	find_class (&pc, val, MDL);

	/* If this isn't a subclass, we're updating an existing class. */
	if (pc && type != 0 && type != 1 && type != 3) {
		class_reference (&class, pc, MDL);
		new = 0;
		class_dereference (&pc, MDL);
	}

	/* If this _is_ a subclass, there _must_ be a class with the
	   same name. */
	if (!pc && (type == 0 || type == 1 || type == 3)) {
		parse_warn (cfile, "no class named %s", val);
		skip_to_semi (cfile);
		return 0;
	}

	/* The old vendor-class and user-class declarations had an implicit
	   match.   We don't do the implicit match anymore.   Instead, for
	   backward compatibility, we have an implicit-vendor-class and an
	   implicit-user-class.   vendor-class and user-class declarations
	   are turned into subclasses of the implicit classes, and the
	   submatch expression of the implicit classes extracts the contents of
	   the vendor class or user class. */
	if (type == 0 || type == 1) {
		data.len = strlen (val);
		data.buffer = (struct buffer *)0;
		if (!buffer_allocate (&data.buffer, data.len + 1, MDL))
			log_fatal ("no memory for class name.");
		data.data = &data.buffer -> data [0];
		data.terminated = 1;

		tname = type ? "implicit-vendor-class" : "implicit-user-class";
	} else if (type == 2) {
		tname = val;
	} else {
		tname = (const char *)0;
	}

	if (tname) {
		name = dmalloc (strlen (tname) + 1, MDL);
		if (!name)
			log_fatal ("No memory for class name %s.", tname);
		strcpy (name, val);
	} else
		name = (char *)0;

	/* If this is a straight subclass, parse the hash string. */
	if (type == 3) {
		token = peek_token (&val, (unsigned *)0, cfile);
		if (token == STRING) {
			token = next_token (&val, &data.len, cfile);
			data.buffer = (struct buffer *)0;
			if (!buffer_allocate (&data.buffer,
					      data.len + 1, MDL)) {
				if (pc)
					class_dereference (&pc, MDL);
				
				return 0;
			}
			data.terminated = 1;
			data.data = &data.buffer -> data [0];
			memcpy ((char *)data.buffer -> data, val,
				data.len + 1);
		} else if (token == NUMBER_OR_NAME || token == NUMBER) {
			memset (&data, 0, sizeof data);
			if (!parse_cshl (&data, cfile)) {
				class_dereference (&pc, MDL);
				return 0;
			}
		} else {
			parse_warn (cfile, "Expecting string or hex list.");
			if (pc)
				class_dereference (&pc, MDL);
			return 0;
		}
	}

	/* See if there's already a class in the hash table matching the
	   hash data. */
	if (type == 0 || type == 1 || type == 3)
		class_hash_lookup (&class, pc -> hash,
				   (const char *)data.data, data.len, MDL);

	/* If we didn't find an existing class, allocate a new one. */
	if (!class) {
		/* Allocate the class structure... */
		status = class_allocate (&class, MDL);
		if (pc) {
			group_reference (&class -> group, pc -> group, MDL);
			class_reference (&class -> superclass, pc, MDL);
			class -> lease_limit = pc -> lease_limit;
			if (class -> lease_limit) {
				class -> billed_leases =
					dmalloc (class -> lease_limit *
						 sizeof (struct lease *), MDL);
				if (!class -> billed_leases)
					log_fatal ("no memory for billing");
				memset (class -> billed_leases, 0,
					(class -> lease_limit *
					 sizeof class -> billed_leases));
			}
			data_string_copy (&class -> hash_string, &data, MDL);
			if (!pc -> hash)
				pc -> hash =
					new_hash ((hash_reference)
						  omapi_object_reference,
						  (hash_dereference)
						  omapi_object_dereference,
						  0, MDL);
			add_hash (pc -> hash,
				  class -> hash_string.data,
				  class -> hash_string.len,
				  (void *)class, MDL);
		} else {
			if (!clone_group (&class -> group, group, MDL))
				log_fatal ("no memory to clone class group.");
		}

		/* If this is an implicit vendor or user class, add a
		   statement that causes the vendor or user class ID to
		   be sent back in the reply. */
		if (type == 0 || type == 1) {
			stmt = (struct executable_statement *)0;
			if (!executable_statement_allocate (&stmt, MDL))
				log_fatal ("no memory for class statement.");
			stmt -> op = supersede_option_statement;
			if (option_cache_allocate (&stmt -> data.option,
						   MDL)) {
				stmt -> data.option -> data = data;
				stmt -> data.option -> option =
					dhcp_universe.options
					[type
					? DHO_VENDOR_CLASS_IDENTIFIER
					: DHO_USER_CLASS];
			}
			class -> statements = stmt;
		}

		/* Save the name, if there is one. */
		class -> name = name;
	}

	if (type == 0 || type == 1 || type == 3)
		data_string_forget (&data, MDL);

	/* Spawned classes don't have to have their own settings. */
	if (class -> superclass) {
		token = peek_token (&val, (unsigned *)0, cfile);
		if (token == SEMI) {
			next_token (&val, (unsigned *)0, cfile);
			if (cp)
				status = class_reference (cp, class, MDL);
			class_dereference (&class, MDL);
			if (pc)
				class_dereference (&pc, MDL);
			return cp ? (status == ISC_R_SUCCESS) : 1;
		}
		/* Give the subclass its own group. */
		if (!clone_group (&class -> group, class -> group, MDL))
			log_fatal ("can't clone class group.");

	}

	if (!parse_lbrace (cfile)) {
		class_dereference (&class, MDL);
		if (pc)
			class_dereference (&pc, MDL);
		return 0;
	}

	do {
		token = peek_token (&val, (unsigned *)0, cfile);
		if (token == RBRACE) {
			token = next_token (&val, (unsigned *)0, cfile);
			break;
		} else if (token == END_OF_FILE) {
			token = next_token (&val, (unsigned *)0, cfile);
			parse_warn (cfile, "unexpected end of file");
			break;
		} else if (token == MATCH) {
			if (pc) {
				parse_warn (cfile,
					    "invalid match in subclass.");
				skip_to_semi (cfile);
				break;
			}
			if (class -> expr) {
				parse_warn (cfile, "can't override match.");
				skip_to_semi (cfile);
				break;
			}
			token = next_token (&val, (unsigned *)0, cfile);
			token = peek_token (&val, (unsigned *)0, cfile);
			if (token != IF)
				goto submatch;
			token = next_token (&val, (unsigned *)0, cfile);
			if (!parse_boolean_expression (&class -> expr, cfile,
						       &lose)) {
				if (!lose) {
					parse_warn (cfile,
						    "expecting boolean expr.");
					skip_to_semi (cfile);
				}
			} else {
#if defined (DEBUG_EXPRESSION_PARSE)
				print_expression ("class match",
						  class -> expr);
#endif
				parse_semi (cfile);
			}
		} else if (token == SPAWN) {
			if (pc) {
				parse_warn (cfile,
					    "invalid spawn in subclass.");
				skip_to_semi (cfile);
				break;
			}
			token = next_token (&val, (unsigned *)0, cfile);
			class -> spawning = 1;
			token = next_token (&val, (unsigned *)0, cfile);
			if (token != WITH) {
				parse_warn (cfile,
					    "expecting with after spawn");
				skip_to_semi (cfile);
				break;
			}
		      submatch:
			if (class -> submatch) {
				parse_warn (cfile,
					    "can't override existing %s.",
					    "submatch/spawn");
				skip_to_semi (cfile);
				break;
			}
			if (!parse_data_expression (&class -> submatch,
						    cfile, &lose)) {
				if (!lose) {
					parse_warn (cfile,
						    "expecting data expr.");
					skip_to_semi (cfile);
				}
			} else {
#if defined (DEBUG_EXPRESSION_PARSE)
				print_expression ("class submatch",
						  class -> submatch);
#endif
				parse_semi (cfile);
			}
		} else if (token == LEASE) {
			next_token (&val, (unsigned *)0, cfile);
			token = next_token (&val, (unsigned *)0, cfile);
			if (token != LIMIT) {
				parse_warn (cfile, "expecting \"limit\"");
				if (token != SEMI)
					skip_to_semi (cfile);
				break;
			}
			token = next_token (&val, (unsigned *)0, cfile);
			if (token != NUMBER) {
				parse_warn (cfile, "expecting a number");
				if (token != SEMI)
					skip_to_semi (cfile);
				break;
			}
			class -> lease_limit = atoi (val);
			class -> billed_leases =
				dmalloc (class -> lease_limit *
					 sizeof (struct lease *), MDL);
			if (!class -> billed_leases)
				log_fatal ("no memory for billed leases.");
			memset (class -> billed_leases, 0,
				(class -> lease_limit *
				 sizeof class -> billed_leases));
			have_billing_classes = 1;
			parse_semi (cfile);
		} else {
			declaration = parse_statement (cfile, class -> group,
						       CLASS_DECL,
						       (struct host_decl *)0,
						       declaration);
		}
	} while (1);
	if (type == 2 && new) {
		if (!collections -> classes)
			class_reference (&collections -> classes, class, MDL);
		else {
			struct class *c;
			for (c = collections -> classes;
			     c -> nic; c = c -> nic)
				;
			class_reference (&c -> nic, class, MDL);
		}
	}
	if (cp)
		status = class_reference (cp, class, MDL);
	class_dereference (&class, MDL);
	if (pc)
		class_dereference (&pc, MDL);
	return cp ? (status == ISC_R_SUCCESS) : 1;
}

/* shared-network-declaration :==
			hostname LBRACE declarations parameters RBRACE */

void parse_shared_net_declaration (cfile, group)
	struct parse *cfile;
	struct group *group;
{
	const char *val;
	enum dhcp_token token;
	struct shared_network *share;
	char *name;
	int declaration = 0;
	isc_result_t status;

	share = (struct shared_network *)0;
	status = shared_network_allocate (&share, MDL);
	if (status != ISC_R_SUCCESS)
		log_fatal ("Can't allocate shared subnet: %s",
			   isc_result_totext (status));
	clone_group (&share -> group, group, MDL);
	shared_network_reference (&share -> group -> shared_network,
				  share, MDL);

	/* Get the name of the shared network... */
	token = peek_token (&val, (unsigned *)0, cfile);
	if (token == STRING) {
		token = next_token (&val, (unsigned *)0, cfile);

		if (val [0] == 0) {
			parse_warn (cfile, "zero-length shared network name");
			val = "<no-name-given>";
		}
		name = dmalloc (strlen (val) + 1, MDL);
		if (!name)
			log_fatal ("no memory for shared network name");
		strcpy (name, val);
	} else {
		name = parse_host_name (cfile);
		if (!name) {
			parse_warn (cfile,
				     "expecting a name for shared-network");
			skip_to_semi (cfile);
			shared_network_dereference (&share, MDL);
			return;
		}
	}
	share -> name = name;

	if (!parse_lbrace (cfile)) {
		shared_network_dereference (&share, MDL);
		return;
	}

	do {
		token = peek_token (&val, (unsigned *)0, cfile);
		if (token == RBRACE) {
			token = next_token (&val, (unsigned *)0, cfile);
			if (!share -> subnets)
				parse_warn (cfile,
					    "empty shared-network decl");
			else
				enter_shared_network (share);
			shared_network_dereference (&share, MDL);
			return;
		} else if (token == END_OF_FILE) {
			token = next_token (&val, (unsigned *)0, cfile);
			parse_warn (cfile, "unexpected end of file");
			break;
		} else if (token == INTERFACE) {
			token = next_token (&val, (unsigned *)0, cfile);
			token = next_token (&val, (unsigned *)0, cfile);
			new_shared_network_interface (cfile, share, val);
			if (!parse_semi (cfile))
				break;
			continue;
		}

		declaration = parse_statement (cfile, share -> group,
					       SHARED_NET_DECL,
					       (struct host_decl *)0,
					       declaration);
	} while (1);
	shared_network_dereference (&share, MDL);
}

/* subnet-declaration :==
	net NETMASK netmask RBRACE parameters declarations LBRACE */

void parse_subnet_declaration (cfile, share)
	struct parse *cfile;
	struct shared_network *share;
{
	const char *val;
	enum dhcp_token token;
	struct subnet *subnet, *t, *u;
	struct iaddr iaddr;
	unsigned char addr [4];
	unsigned len = sizeof addr;
	int declaration = 0;
	struct interface_info *ip;
	isc_result_t status;

	subnet = (struct subnet *)0;
	status = subnet_allocate (&subnet, MDL);
	if (status != ISC_R_SUCCESS)
		log_fatal ("Allocation of new subnet failed: %s",
			   isc_result_totext (status));
	shared_network_reference (&subnet -> shared_network, share, MDL);
	if (!clone_group (&subnet -> group, share -> group, MDL))
		log_fatal ("allocation of group for new subnet failed.");
	subnet_reference (&subnet -> group -> subnet, subnet, MDL);

	/* Get the network number... */
	if (!parse_numeric_aggregate (cfile, addr, &len, DOT, 10, 8)) {
		subnet_dereference (&subnet, MDL);
		return;
	}
	memcpy (iaddr.iabuf, addr, len);
	iaddr.len = len;
	subnet -> net = iaddr;

	token = next_token (&val, (unsigned *)0, cfile);
	if (token != NETMASK) {
		parse_warn (cfile, "Expecting netmask");
		skip_to_semi (cfile);
		return;
	}

	/* Get the netmask... */
	if (!parse_numeric_aggregate (cfile, addr, &len, DOT, 10, 8)) {
		subnet_dereference (&subnet, MDL);
		return;
	}
	memcpy (iaddr.iabuf, addr, len);
	iaddr.len = len;
	subnet -> netmask = iaddr;

	/* Validate the network number/netmask pair. */
	if (host_addr (subnet -> net, subnet -> netmask)) {
		parse_warn (cfile,
			    "subnet %s: bad subnet number/mask combination.",
			    piaddr (subnet -> net));
		subnet_dereference (&subnet, MDL);
		skip_to_semi (cfile);
		return;
	}

	enter_subnet (subnet);

	if (!parse_lbrace (cfile)) {
		subnet_dereference (&subnet, MDL);
		return;
	}

	do {
		token = peek_token (&val, (unsigned *)0, cfile);
		if (token == RBRACE) {
			token = next_token (&val, (unsigned *)0, cfile);
			break;
		} else if (token == END_OF_FILE) {
			token = next_token (&val, (unsigned *)0, cfile);
			parse_warn (cfile, "unexpected end of file");
			break;
		} else if (token == INTERFACE) {
			token = next_token (&val, (unsigned *)0, cfile);
			token = next_token (&val, (unsigned *)0, cfile);
			new_shared_network_interface (cfile, share, val);
			if (!parse_semi (cfile))
				break;
			continue;
		}
		declaration = parse_statement (cfile, subnet -> group,
					       SUBNET_DECL,
					       (struct host_decl *)0,
					       declaration);
	} while (1);

	/* Add the subnet to the list of subnets in this shared net. */
	if (!share -> subnets)
		subnet_reference (&share -> subnets, subnet, MDL);
	else {
		u = (struct subnet *)0;
		for (t = share -> subnets;
		     t -> next_sibling; t = t -> next_sibling) {
			if (subnet_inner_than (subnet, t, 0)) {
				subnet_reference (&subnet -> next_sibling,
						  t, MDL);
				if (u) {
					subnet_dereference (&u -> next_sibling,
							    MDL);
					subnet_reference (&u -> next_sibling,
							  subnet, MDL);
				} else {
					subnet_dereference (&share -> subnets,
							    MDL);
					subnet_reference (&share -> subnets,
							  subnet, MDL);
				}
				subnet_dereference (&subnet, MDL);
				return;
			}
			u = t;
		}
		subnet_reference (&t -> next_sibling, subnet, MDL);
	}
	subnet_dereference (&subnet, MDL);
}

/* group-declaration :== RBRACE parameters declarations LBRACE */

void parse_group_declaration (cfile, group)
	struct parse *cfile;
	struct group *group;
{
	const char *val;
	enum dhcp_token token;
	struct group *g;
	int declaration = 0;
	struct group_object *t;
	isc_result_t status;
	char *name = NULL;
	int deletedp = 0;
	int dynamicp = 0;
	int staticp = 0;

	g = (struct group *)0;
	if (!clone_group (&g, group, MDL))
		log_fatal ("no memory for explicit group.");

	token = peek_token (&val, (unsigned *)0, cfile);
	if (is_identifier (token) || token == STRING) {
		next_token (&val, (unsigned *)0, cfile);
		
		name = dmalloc (strlen (val) + 1, MDL);
		if (!name)
			log_fatal ("no memory for group decl name %s", val);
		strcpy (name, val);
	}		

	if (!parse_lbrace (cfile)) {
		group_dereference (&g, MDL);
		return;
	}

	do {
		token = peek_token (&val, (unsigned *)0, cfile);
		if (token == RBRACE) {
			token = next_token (&val, (unsigned *)0, cfile);
			break;
		} else if (token == END_OF_FILE) {
			token = next_token (&val, (unsigned *)0, cfile);
			parse_warn (cfile, "unexpected end of file");
			break;
		} else if (token == TOKEN_DELETED) {
			token = next_token (&val, (unsigned *)0, cfile);
			parse_semi (cfile);
			deletedp = 1;
		} else if (token == DYNAMIC) {
			token = next_token (&val, (unsigned *)0, cfile);
			parse_semi (cfile);
			dynamicp = 1;
		} else if (token == STATIC) {
			token = next_token (&val, (unsigned *)0, cfile);
			parse_semi (cfile);
			staticp = 1;
		}
		declaration = parse_statement (cfile, g, GROUP_DECL,
					       (struct host_decl *)0,
					       declaration);
	} while (1);

	if (name) {
		if (deletedp) {
			if (group_name_hash) {
				t = (struct group_object *)0;
				if (group_hash_lookup (&t, group_name_hash,
						       name,
						       strlen (name), MDL)) {
					delete_group (t, 0);
				}
			}
		} else {
			t = (struct group_object *)0;
			status = group_object_allocate (&t, MDL);
			if (status != ISC_R_SUCCESS)
				log_fatal ("no memory for group decl %s: %s",
					   val, isc_result_totext (status));
			group_reference (&t -> group, g, MDL);
			t -> name = name;
			t -> flags = ((staticp ? GROUP_OBJECT_STATIC : 0) |
				      (dynamicp ? GROUP_OBJECT_DYNAMIC : 0) |
				      (deletedp ? GROUP_OBJECT_DELETED : 0));
			supersede_group (t, 0);
		}
		if (t)
			group_object_dereference (&t, MDL);
	}
}

/* fixed-addr-parameter :== ip-addrs-or-hostnames SEMI
   ip-addrs-or-hostnames :== ip-addr-or-hostname
			   | ip-addrs-or-hostnames ip-addr-or-hostname */

int parse_fixed_addr_param (oc, cfile)
	struct option_cache **oc;
	struct parse *cfile;
{
	const char *val;
	enum dhcp_token token;
	struct expression *expr = (struct expression *)0;
	struct expression *tmp, *new;
	int status;

	do {
		tmp = (struct expression *)0;
		if (parse_ip_addr_or_hostname (&tmp, cfile, 1)) {
			if (expr) {
				new = (struct expression *)0;
				status = make_concat (&new, expr, tmp);
				expression_dereference (&expr, MDL);
				expression_dereference (&tmp, MDL);
				if (!status)
					return 0;
				expr = new;
			} else
				expr = tmp;
		} else {
			if (expr)
				expression_dereference (&expr, MDL);
			return 0;
		}
		token = peek_token (&val, (unsigned *)0, cfile);
		if (token == COMMA)
			token = next_token (&val, (unsigned *)0, cfile);
	} while (token == COMMA);

	if (!parse_semi (cfile)) {
		if (expr)
			expression_dereference (&expr, MDL);
		return 0;
	}
	status = option_cache (oc, (struct data_string *)0, expr,
			       (struct option *)0, MDL);
	expression_dereference (&expr, MDL);
	return status;
}

/* timestamp :== date

   Timestamps are actually not used in dhcpd.conf, which is a static file,
   but rather in the database file and the journal file.  (Okay, actually
   they're not even used there yet). */

TIME parse_timestamp (cfile)
	struct parse *cfile;
{
	TIME rv;

	rv = parse_date (cfile);
	return rv;
}
		
/* lease_declaration :== LEASE ip_address LBRACE lease_parameters RBRACE

   lease_parameters :== <nil>
		      | lease_parameter
		      | lease_parameters lease_parameter

   lease_parameter :== STARTS date
		     | ENDS date
		     | TIMESTAMP date
		     | HARDWARE hardware-parameter
		     | UID hex_numbers SEMI
		     | HOSTNAME hostname SEMI
		     | CLIENT_HOSTNAME hostname SEMI
		     | CLASS identifier SEMI
		     | DYNAMIC_BOOTP SEMI */

int parse_lease_declaration (struct lease **lp, struct parse *cfile)
{
	const char *val;
	enum dhcp_token token;
	unsigned char addr [4];
	unsigned len = sizeof addr;
	int seenmask = 0;
	int seenbit;
	char tbuf [32];
	struct lease *lease;
	struct executable_statement *on;
	struct expression *exp;
	struct data_string ds;
	int lose;
	TIME t;
	char *s;
	int noequal, newbinding;
	struct binding *binding;
	isc_result_t status;
	struct option_cache *oc;
	pair *p;
	binding_state_t new_state;
	unsigned buflen = 0;
	struct class *class;

	lease = (struct lease *)0;
	status = lease_allocate (&lease, MDL);
	if (status != ISC_R_SUCCESS)
		return 0;

	/* Get the address for which the lease has been issued. */
	if (!parse_numeric_aggregate (cfile, addr, &len, DOT, 10, 8)) {
		lease_dereference (&lease, MDL);
		return 0;
	}
	memcpy (lease -> ip_addr.iabuf, addr, len);
	lease -> ip_addr.len = len;

	if (!parse_lbrace (cfile)) {
		lease_dereference (&lease, MDL);
		return 0;
	}

	do {
		token = next_token (&val, (unsigned *)0, cfile);
		if (token == RBRACE)
			break;
		else if (token == END_OF_FILE) {
			parse_warn (cfile, "unexpected end of file");
			break;
		}
		strncpy (tbuf, val, sizeof tbuf);
		tbuf [(sizeof tbuf) - 1] = 0;

		/* Parse any of the times associated with the lease. */
		switch (token) {
		      case STARTS:
		      case ENDS:
		      case TIMESTAMP:
		      case TSTP:
		      case TSFP:
		      case CLTT:
			t = parse_date (cfile);
			switch (token) {
			      case STARTS:
				seenbit = 1;
				lease -> starts = t;
				break;
			
			      case ENDS:
				seenbit = 2;
				lease -> ends = t;
				break;
				
			      case TIMESTAMP:
				seenbit = 4;
				lease -> timestamp = t;
				break;

			      case TSTP:
				seenbit = 65536;
				lease -> tstp = t;
				break;
				
			      case TSFP:
				seenbit = 131072;
				lease -> tsfp = t;
				break;
				
			      case CLTT:
				seenbit = 524288;
				lease -> cltt = t;
				break;
				
			      default: /* for gcc, we'll never get here. */
				break;
			}
			break;

			/* Colon-seperated hexadecimal octets... */
		      case UID:
			seenbit = 8;
			token = peek_token (&val, (unsigned *)0, cfile);
			if (token == STRING) {
				unsigned char *tuid;
				token = next_token (&val, &buflen, cfile);
				if (buflen < sizeof lease -> uid_buf) {
					tuid = lease -> uid_buf;
					lease -> uid_max =
						sizeof lease -> uid_buf;
				} else {
					tuid = ((unsigned char *)
						dmalloc (buflen, MDL));
					if (!tuid) {
						log_error ("no space for uid");
						lease_dereference (&lease,
								   MDL);
						return 0;
					}
					lease -> uid_max = buflen;
				}
				lease -> uid_len = buflen;
				memcpy (tuid, val, lease -> uid_len);
				lease -> uid = tuid;
			} else {
				buflen = 0;
				lease -> uid = (parse_numeric_aggregate
						(cfile, (unsigned char *)0,
						 &buflen, ':', 16, 8));
				if (!lease -> uid) {
					lease_dereference (&lease, MDL);
					return 0;
				}
				lease -> uid_len = buflen;
				lease -> uid_max = buflen;
				if (lease -> uid_len == 0) {
					lease -> uid = (unsigned char *)0;
					parse_warn (cfile, "zero-length uid");
					seenbit = 0;
					parse_semi (cfile);
					break;
				}
			}
			parse_semi (cfile);
			if (!lease -> uid) {
				log_fatal ("No memory for lease uid");
			}
			break;
			
		      case CLASS:
			seenbit = 32;
			token = next_token (&val, (unsigned *)0, cfile);
			if (!is_identifier (token)) {
				if (token != SEMI)
					skip_to_rbrace (cfile, 1);
				lease_dereference (&lease, MDL);
				return 0;
			}
			parse_semi (cfile);
			/* for now, we aren't using this. */
			break;

		      case HARDWARE:
			seenbit = 64;
			parse_hardware_param (cfile,
					      &lease -> hardware_addr);
			break;

		      case DYNAMIC_BOOTP:
			seenbit = 256;
			lease -> binding_state = FTS_BOOTP;
			lease -> next_binding_state = FTS_BOOTP;
			parse_semi (cfile);
			break;
			
		      case TOKEN_ABANDONED:
			seenbit = 256;
			lease -> binding_state = FTS_ABANDONED;
			lease -> next_binding_state = FTS_ABANDONED;
			parse_semi (cfile);
			break;

		      case TOKEN_NEXT:
			seenbit = 128;
			token = next_token (&val, (unsigned *)0, cfile);
			if (token != BINDING) {
				parse_warn (cfile, "expecting 'binding'");
				skip_to_semi (cfile);
				break;
			}
			goto do_binding_state;

		      case BINDING:
			seenbit = 256;

		      do_binding_state:
			token = next_token (&val, (unsigned *)0, cfile);
			if (token != STATE) {
				parse_warn (cfile, "expecting 'state'");
				skip_to_semi (cfile);
				break;
			}
			token = next_token (&val, (unsigned *)0, cfile);
			switch (token) {
			      case TOKEN_ABANDONED:
				new_state = FTS_ABANDONED;
				break;
			      case TOKEN_FREE:
				new_state = FTS_FREE;
				break;
			      case TOKEN_ACTIVE:
				new_state = FTS_ACTIVE;
				break;
			      case TOKEN_EXPIRED:
				new_state = FTS_EXPIRED;
				break;
			      case TOKEN_RELEASED:
				new_state = FTS_RELEASED;
				break;
			      case TOKEN_RESET:
				new_state = FTS_RESET;
				break;
			      case TOKEN_BACKUP:
				new_state = FTS_BACKUP;
				break;
			      case TOKEN_RESERVED:
				new_state = FTS_RESERVED;
				break;
			      case TOKEN_BOOTP:
				new_state = FTS_BOOTP;
				break;
			      default:
				parse_warn (cfile,
					    "%s: expecting a binding state.",
					    val);
				skip_to_semi (cfile);
				break;
			}

			if (seenbit == 256) {
				lease -> binding_state = new_state;

				/* If no next binding state is specified, it's
				   the same as the current state. */
				if (!(seenmask & 128))
				    lease -> next_binding_state = new_state;
			} else
				lease -> next_binding_state = new_state;
				
			parse_semi (cfile);
			break;

		      case CLIENT_HOSTNAME:
			seenbit = 1024;
			token = peek_token (&val, (unsigned *)0, cfile);
			if (token == STRING) {
				if (!parse_string (cfile,
						   &lease -> client_hostname,
						   (unsigned *)0)) {
					lease_dereference (&lease, MDL);
					return 0;
				}
			} else {
				lease -> client_hostname =
					parse_host_name (cfile);
				if (lease -> client_hostname)
					parse_semi (cfile);
				else {
					parse_warn (cfile,
						    "expecting a hostname.");
					skip_to_semi (cfile);
					lease_dereference (&lease, MDL);
					return 0;
				}
			}
			break;
			
		      case BILLING:
			seenbit = 2048;
			class = (struct class *)0;
			token = next_token (&val, (unsigned *)0, cfile);
			if (token == CLASS) {
				token = next_token (&val,
						    (unsigned *)0, cfile);
				if (token != STRING) {
					parse_warn (cfile, "expecting string");
					if (token != SEMI)
						skip_to_semi (cfile);
					token = BILLING;
					break;
				}
				if (lease -> billing_class)
				    class_dereference (&lease -> billing_class,
						       MDL);
				find_class (&class, val, MDL);
				if (!class)
					parse_warn (cfile,
						    "unknown class %s", val);
				parse_semi (cfile);
			} else if (token == SUBCLASS) {
				if (lease -> billing_class)
				    class_dereference (&lease -> billing_class,
						       MDL);
				parse_class_declaration
					(&class,
					 cfile, (struct group *)0, 3);
			} else {
				parse_warn (cfile, "expecting \"class\"");
				if (token != SEMI)
					skip_to_semi (cfile);
			}
			if (class) {
				class_reference (&lease -> billing_class,
						 class, MDL);
				class_dereference (&class, MDL);
			}
			break;

		      case ON:
			on = (struct executable_statement *)0;
			lose = 0;
			if (!parse_on_statement (&on, cfile, &lose)) {
				skip_to_rbrace (cfile, 1);
				lease_dereference (&lease, MDL);
				return 0;
			}
			seenbit = 0;
			if ((on -> data.on.evtypes & ON_EXPIRY) &&
			    on -> data.on.statements) {
				seenbit |= 16384;
				executable_statement_reference
					(&lease -> on_expiry,
					 on -> data.on.statements, MDL);
			}
			if ((on -> data.on.evtypes & ON_RELEASE) &&
			    on -> data.on.statements) {
				seenbit |= 32768;
				executable_statement_reference
					(&lease -> on_release,
					 on -> data.on.statements, MDL);
			}
			executable_statement_dereference (&on, MDL);
			break;
			
		      case OPTION:
		      case SUPERSEDE:
			noequal = 0;
			seenbit = 0;
			oc = (struct option_cache *)0;
			if (parse_option_decl (&oc, cfile)) {
			    if (oc -> option -> universe !=
				&agent_universe) {
				    parse_warn (cfile,
						"agent option expected.");
				    option_cache_dereference (&oc, MDL);
				    break;
			    }
			    if (!lease -> agent_options &&
				!(option_chain_head_allocate
				  (&lease -> agent_options, MDL))) {
				log_error ("no memory to stash agent option");
				break;
			    }
			    for (p = &lease -> agent_options -> first;
				 *p; p = &((*p) -> cdr))
				    ;
			    *p = cons (0, 0);
			    option_cache_reference (((struct option_cache **)
						     &((*p) -> car)), oc, MDL);
			    option_cache_dereference (&oc, MDL);
			}
			break;

		      case TOKEN_SET:
			noequal = 0;
			
			token = next_token (&val, (unsigned *)0, cfile);
			if (token != NAME && token != NUMBER_OR_NAME) {
				parse_warn (cfile,
					    "%s can't be a variable name",
					    val);
			      badset:
				skip_to_semi (cfile);
				lease_dereference (&lease, MDL);
				return 0;
			}
			
			seenbit = 0;
		      special_set:
			if (lease -> scope)
				binding = find_binding (lease -> scope, val);
			else
				binding = (struct binding *)0;
			if (!binding) {
			    if (!lease -> scope)
				if (!(binding_scope_allocate
				      (&lease -> scope, MDL)))
					log_fatal ("no memory for scope");
			    binding = dmalloc (sizeof *binding, MDL);
			    if (!binding)
				    log_fatal ("No memory for lease %s.",
					       "binding");
			    memset (binding, 0, sizeof *binding);
			    binding -> name =
				    dmalloc (strlen (val) + 1, MDL);
			    if (!binding -> name)
				    log_fatal ("No memory for binding %s.",
					       "name");
			    strcpy (binding -> name, val);
			    newbinding = 1;
			} else if (binding -> value) {
				binding_value_dereference (&binding -> value,
							   MDL);
				newbinding = 0;
			}
			if (!binding_value_allocate (&binding -> value, MDL))
				log_fatal ("no memory for binding value.");

			if (!noequal) {
			    token = next_token (&val, (unsigned *)0, cfile);
			    if (token != EQUAL) {
				parse_warn (cfile,
					    "expecting '=' in set statement.");
				goto badset;
			    }
			}

			token = peek_token (&val, (unsigned *)0, cfile);
			if (token == STRING) {
			    unsigned char *tuid;
			    token = next_token (&val, &buflen, cfile);
			    binding -> value -> type = binding_data;
			    binding -> value -> value.data.len = buflen;
			    if (!(buffer_allocate
				  (&binding -> value -> value.data.buffer,
				   buflen + 1, MDL)))
				log_fatal ("No memory for binding.");
			    memcpy ((char *)
				    (binding -> value ->
				     value.data.buffer -> data),
				    val, buflen + 1);
			    binding -> value -> value.data.data =
				binding -> value -> value.data.buffer -> data;
			    binding -> value -> value.data.terminated = 1;
			} else if (token == NUMBER_OR_NAME) {
			    binding -> value -> type = binding_data;
			    s = ((char *)
				 (parse_numeric_aggregate
				  (cfile, (unsigned char *)0,
				   &binding -> value -> value.data.len,
				   ':', 16, 8)));
			    if (!s) {
				    binding_value_dereference
					    (&binding -> value, MDL);
				    lease_dereference (&lease, MDL);
				    return 0;
			    }
			    if (binding -> value -> value.data.len) {
				if (!(buffer_allocate
				      (&binding -> value -> value.data.buffer,
				       binding -> value -> value.data.len + 1,
				       MDL)))
					log_fatal ("No memory for binding.");
				memcpy ((binding -> value ->
					 value.data.buffer -> data), s,
					binding -> value -> value.data.len);
				dfree (s, MDL);
				binding -> value -> value.data.data =
				 binding -> value -> value.data.buffer -> data;
			    }
			} else if (token == PERCENT) {
			    token = next_token (&val, (unsigned *)0, cfile);
			    token = next_token (&val, (unsigned *)0, cfile);
			    if (token != NUMBER) {
				    parse_warn (cfile,
						"expecting decimal number.");
				    if (token != SEMI)
					    skip_to_semi (cfile);
				    binding_value_dereference
					    (&binding -> value, MDL);
				    lease_dereference (&lease, MDL);
				    return 0;
			    }
			    binding -> value -> type = binding_numeric;
			    binding -> value -> value.intval = atol (val);
			} else if (token == NAME) {
				token = next_token (&val,
						    (unsigned *)0, cfile);
				binding -> value -> type = binding_boolean;
				if (!strcasecmp (val, "true"))
					binding -> value -> value.boolean = 1;
				else if (!strcasecmp (val, "false"))
					binding -> value -> value.boolean = 0;
				else
					goto badbool;
			} else {
			      badbool:
				parse_warn (cfile,
					    "expecting a constant value.");
				skip_to_semi (cfile);
				binding_value_dereference (&binding -> value,
							   MDL);
				lease_dereference (&lease, MDL);
				return 0;
			}
				
			if (newbinding) {
				binding -> next = lease -> scope -> bindings;
				lease -> scope -> bindings = binding;
			}
			parse_semi (cfile);
			break;

		      default:
			if (!strcasecmp (val, "ddns-fwd-name")) {
				seenbit = 4096;
				noequal = 1;
				goto special_set;
			} else if (!strcasecmp (val, "ddns-rev-name")) {
				seenbit = 8192;
				noequal = 1;
				goto special_set;
			}
			skip_to_semi (cfile);
			seenbit = 0;
			lease_dereference (&lease, MDL);
			return 0;
		}

		if (seenmask & seenbit) {
			parse_warn (cfile,
				    "Too many %s parameters in lease %s\n",
				    tbuf, piaddr (lease -> ip_addr));
		} else
			seenmask |= seenbit;

	} while (1);

	/* If no binding state is specified, make one up. */
	if (!(seenmask & 256)) {
		if (lease -> ends > cur_time ||
		    lease -> on_expiry || lease -> on_release)
			lease -> binding_state = FTS_ACTIVE;
#if defined (FAILOVER_PROTOCOL)
		else if (lease -> pool && lease -> pool -> failover_peer)
			lease -> binding_state = FTS_EXPIRED;
#endif
		else
			lease -> binding_state = FTS_FREE;
		if (lease -> binding_state == FTS_ACTIVE) {
#if defined (FAILOVER_PROTOCOL)
			if (lease -> pool && lease -> pool -> failover_peer)
				lease -> next_binding_state = FTS_EXPIRED;
			else
#endif
				lease -> next_binding_state = FTS_FREE;
		} else
			lease -> next_binding_state = lease -> binding_state;
	}

	if (!(seenmask & 65536))
		lease -> tstp = lease -> ends;

	lease_reference (lp, lease, MDL);
	lease_dereference (&lease, MDL);
	return 1;
}

/* address-range-declaration :== ip-address ip-address SEMI
			       | DYNAMIC_BOOTP ip-address ip-address SEMI */

void parse_address_range (cfile, group, type, inpool)
	struct parse *cfile;
	struct group *group;
	int type;
	struct pool *inpool;
{
	struct iaddr low, high, net;
	unsigned char addr [4];
	unsigned len = sizeof addr;
	enum dhcp_token token;
	const char *val;
	int dynamic = 0;
	struct subnet *subnet;
	struct shared_network *share;
	struct pool *p;
	struct pool *pool;
	isc_result_t status;

	if ((token = peek_token (&val,
				 (unsigned *)0, cfile)) == DYNAMIC_BOOTP) {
		token = next_token (&val, (unsigned *)0, cfile);
		dynamic = 1;
	}

	/* Get the bottom address in the range... */
	if (!parse_numeric_aggregate (cfile, addr, &len, DOT, 10, 8))
		return;
	memcpy (low.iabuf, addr, len);
	low.len = len;

	/* Only one address? */
	token = peek_token (&val, (unsigned *)0, cfile);
	if (token == SEMI)
		high = low;
	else {
	/* Get the top address in the range... */
		if (!parse_numeric_aggregate (cfile, addr, &len, DOT, 10, 8))
			return;
		memcpy (high.iabuf, addr, len);
		high.len = len;
	}

	token = next_token (&val, (unsigned *)0, cfile);
	if (token != SEMI) {
		parse_warn (cfile, "semicolon expected.");
		skip_to_semi (cfile);
		return;
	}

	if (type == SUBNET_DECL) {
		subnet = group -> subnet;
		share = subnet -> shared_network;
	} else {
		share = group -> shared_network;
		for (subnet = share -> subnets;
		     subnet; subnet = subnet -> next_sibling) {
			net = subnet_number (low, subnet -> netmask);
			if (addr_eq (net, subnet -> net))
				break;
		}
		if (!subnet) {
			parse_warn (cfile, "address range not on network %s",
				    group -> shared_network -> name);
			log_error ("Be sure to place pool statement after %s",
				   "related subnet declarations.");
			return;
		}
	}

	if (!inpool) {
		struct pool *last = (struct pool *)0;

		/* If we're permitting dynamic bootp for this range,
		   then look for a pool with an empty prohibit list and
		   a permit list with one entry that permits all clients. */
		for (pool = share -> pools; pool; pool = pool -> next) {
			if ((!dynamic && !pool -> permit_list && 
			     pool -> prohibit_list &&
			     !pool -> prohibit_list -> next &&
			     (pool -> prohibit_list -> type ==
			      permit_dynamic_bootp_clients)) ||
			    (dynamic && !pool -> prohibit_list &&
			     pool -> permit_list &&
			     !pool -> permit_list -> next &&
			     (pool -> permit_list -> type ==
			      permit_all_clients))) {
  				break;
			}
			last = pool;
		}

		/* If we didn't get a pool, make one. */
		if (!pool) {
			struct permit *p;
			status = pool_allocate (&pool, MDL);
			if (status != ISC_R_SUCCESS)
				log_fatal ("no memory for ad-hoc pool: %s",
					   isc_result_totext (status));
			p = new_permit (MDL);
			if (!p)
				log_fatal ("no memory for ad-hoc permit.");

			/* Dynamic pools permit all clients.   Otherwise
			   we prohibit BOOTP clients. */
			if (dynamic) {
				p -> type = permit_all_clients;
				pool -> permit_list = p;
			} else {
				p -> type = permit_dynamic_bootp_clients;
				pool -> prohibit_list = p;
			}

			if (share -> pools)
				pool_reference (&last -> next, pool, MDL);
			else
				pool_reference (&share -> pools, pool, MDL);
			shared_network_reference (&pool -> shared_network,
						  share, MDL);
			if (!clone_group (&pool -> group, share -> group, MDL))
				log_fatal ("no memory for anon pool group.");
		} else {
			pool = (struct pool *)0;
			if (last)
				pool_reference (&pool, last, MDL);
			else
				pool_reference (&pool, share -> pools, MDL);
		}
	} else {
		pool = (struct pool *)0;
		pool_reference (&pool, inpool, MDL);
	}

#if defined (FAILOVER_PROTOCOL)
	if (pool -> failover_peer && dynamic) {
		/* Doctor, do you think I'm overly sensitive
		   about getting bug reports I can't fix? */
		parse_warn (cfile, "dynamic-bootp flag is %s",
			    "not permitted for address");
		log_error ("range declarations where there is a failover");
		log_error ("peer in scope.   If you wish to declare an");
		log_error ("address range from which dynamic bootp leases");
		log_error ("can be allocated, please declare it within a");
		log_error ("pool declaration that also contains the \"no");
		log_error ("failover\" statement.   The failover protocol");
		log_error ("itself does not permit dynamic bootp - this");
		log_error ("is not a limitation specific to the ISC DHCP");
		log_error ("server.   Please don't ask me to defend this");
		log_error ("until you have read and really tried %s",
			   "to understand");
		log_error ("the failover protocol specification.");

		/* We don't actually bomb at this point - instead,
		   we let parse_lease_file notice the error and
		   bomb at that point - it's easier. */
	}
#endif /* FAILOVER_PROTOCOL */

	/* Create the new address range... */
	new_address_range (low, high, subnet, pool);
	pool_dereference (&pool, MDL);
}

/* allow-deny-keyword :== BOOTP
   			| BOOTING
			| DYNAMIC_BOOTP
			| UNKNOWN_CLIENTS */

int parse_allow_deny (oc, cfile, flag)
	struct option_cache **oc;
	struct parse *cfile;
	int flag;
{
	enum dhcp_token token;
	const char *val;
	unsigned char rf = flag;
	struct expression *data = (struct expression *)0;
	int status;

	if (!make_const_data (&data, &rf, 1, 0, 1, MDL))
		return 0;

	token = next_token (&val, (unsigned *)0, cfile);
	switch (token) {
	      case TOKEN_BOOTP:
		status = option_cache (oc, (struct data_string *)0, data,
				       &server_options [SV_ALLOW_BOOTP], MDL);
		break;

	      case BOOTING:
		status = option_cache (oc, (struct data_string *)0, data,
				       &server_options [SV_ALLOW_BOOTING],
				       MDL);
		break;

	      case DYNAMIC_BOOTP:
		status = option_cache (oc, (struct data_string *)0, data,
				       &server_options [SV_DYNAMIC_BOOTP],
				       MDL);
		break;

	      case UNKNOWN_CLIENTS:
		status = (option_cache
			  (oc, (struct data_string *)0, data,
			   &server_options [SV_BOOT_UNKNOWN_CLIENTS], MDL));
		break;

	      case DUPLICATES:
		status = option_cache (oc, (struct data_string *)0, data,
				       &server_options [SV_DUPLICATES], MDL);
		break;

	      case DECLINES:
		status = option_cache (oc, (struct data_string *)0, data,
				       &server_options [SV_DECLINES], MDL);
		break;

	      case CLIENT_UPDATES:
		status = option_cache (oc, (struct data_string *)0, data,
				       &server_options [SV_CLIENT_UPDATES],
				       MDL);
		break;

	      default:
		parse_warn (cfile, "expecting allow/deny key");
		skip_to_semi (cfile);
		return 0;
	}
	expression_dereference (&data, MDL);
	parse_semi (cfile);
	return status;
}

