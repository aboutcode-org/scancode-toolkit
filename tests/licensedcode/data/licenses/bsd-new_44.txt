/* omapi.c

   OMAPI object interfaces for the DHCP server. */

/*
 * Copyright (c) 1999-2001 Internet Software Consortium.
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

/* Many, many thanks to Brian Murrell and BCtel for this code - BCtel
   provided the funding that resulted in this code and the entire
   OMAPI support library being written, and Brian helped brainstorm
   and refine the requirements.  To the extent that this code is
   useful, you have Brian and BCtel to thank.  Any limitations in the
   code are a result of mistakes on my part.  -- Ted Lemon */

#ifndef lint
static char copyright[] =
"$Id: omapi.c,v 1.46.2.7 2001/06/22 02:28:51 mellon Exp $ Copyright (c) 1999-2001 The Internet Software Consortium.  All rights reserved.\n";
#endif /* not lint */

#include "dhcpd.h"
#include <omapip/omapip_p.h>

omapi_object_type_t *dhcp_type_lease;
omapi_object_type_t *dhcp_type_pool;
omapi_object_type_t *dhcp_type_class;
omapi_object_type_t *dhcp_type_subclass;
omapi_object_type_t *dhcp_type_host;
#if defined (FAILOVER_PROTOCOL)
omapi_object_type_t *dhcp_type_failover_state;
omapi_object_type_t *dhcp_type_failover_link;
omapi_object_type_t *dhcp_type_failover_listener;
#endif

void dhcp_db_objects_setup ()
{
	isc_result_t status;

	status = omapi_object_type_register (&dhcp_type_lease,
					     "lease",
					     dhcp_lease_set_value,
					     dhcp_lease_get_value,
					     dhcp_lease_destroy,
					     dhcp_lease_signal_handler,
					     dhcp_lease_stuff_values,
					     dhcp_lease_lookup, 
					     dhcp_lease_create,
					     dhcp_lease_remove,
#if defined (COMPACT_LEASES)
					     dhcp_lease_free,
					     dhcp_lease_get,
#else
					     0, 0,
#endif
					     0,
					     sizeof (struct lease), 0);
	if (status != ISC_R_SUCCESS)
		log_fatal ("Can't register lease object type: %s",
			   isc_result_totext (status));

	status = omapi_object_type_register (&dhcp_type_class,
					     "class",
					     dhcp_class_set_value,
					     dhcp_class_get_value,
					     dhcp_class_destroy,
					     dhcp_class_signal_handler,
					     dhcp_class_stuff_values,
					     dhcp_class_lookup, 
					     dhcp_class_create,
					     dhcp_class_remove, 0, 0, 0,
					     sizeof (struct class), 0);
	if (status != ISC_R_SUCCESS)
		log_fatal ("Can't register class object type: %s",
			   isc_result_totext (status));

	status = omapi_object_type_register (&dhcp_type_subclass,
					     "subclass",
					     dhcp_subclass_set_value,
					     dhcp_subclass_get_value,
					     dhcp_class_destroy,
					     dhcp_subclass_signal_handler,
					     dhcp_subclass_stuff_values,
					     dhcp_subclass_lookup, 
					     dhcp_subclass_create,
					     dhcp_subclass_remove, 0, 0, 0,
					     sizeof (struct class), 0);
	if (status != ISC_R_SUCCESS)
		log_fatal ("Can't register subclass object type: %s",
			   isc_result_totext (status));

	status = omapi_object_type_register (&dhcp_type_pool,
					     "pool",
					     dhcp_pool_set_value,
					     dhcp_pool_get_value,
					     dhcp_pool_destroy,
					     dhcp_pool_signal_handler,
					     dhcp_pool_stuff_values,
					     dhcp_pool_lookup, 
					     dhcp_pool_create,
					     dhcp_pool_remove, 0, 0, 0,
					     sizeof (struct pool), 0);

	if (status != ISC_R_SUCCESS)
		log_fatal ("Can't register pool object type: %s",
			   isc_result_totext (status));

	status = omapi_object_type_register (&dhcp_type_host,
					     "host",
					     dhcp_host_set_value,
					     dhcp_host_get_value,
					     dhcp_host_destroy,
					     dhcp_host_signal_handler,
					     dhcp_host_stuff_values,
					     dhcp_host_lookup, 
					     dhcp_host_create,
					     dhcp_host_remove, 0, 0, 0,
					     sizeof (struct host_decl), 0);

	if (status != ISC_R_SUCCESS)
		log_fatal ("Can't register host object type: %s",
			   isc_result_totext (status));

#if defined (FAILOVER_PROTOCOL)
	status = omapi_object_type_register (&dhcp_type_failover_state,
					     "failover-state",
					     dhcp_failover_state_set_value,
					     dhcp_failover_state_get_value,
					     dhcp_failover_state_destroy,
					     dhcp_failover_state_signal,
					     dhcp_failover_state_stuff,
					     dhcp_failover_state_lookup, 
					     dhcp_failover_state_create,
					     dhcp_failover_state_remove,
					     0, 0, 0,
					     sizeof (dhcp_failover_state_t),
					     0);

	if (status != ISC_R_SUCCESS)
		log_fatal ("Can't register failover state object type: %s",
			   isc_result_totext (status));

	status = omapi_object_type_register (&dhcp_type_failover_link,
					     "failover-link",
					     dhcp_failover_link_set_value,
					     dhcp_failover_link_get_value,
					     dhcp_failover_link_destroy,
					     dhcp_failover_link_signal,
					     dhcp_failover_link_stuff_values,
					     0, 0, 0, 0, 0, 0,
					     sizeof (dhcp_failover_link_t), 0);

	if (status != ISC_R_SUCCESS)
		log_fatal ("Can't register failover link object type: %s",
			   isc_result_totext (status));

	status = omapi_object_type_register (&dhcp_type_failover_listener,
					     "failover-listener",
					     dhcp_failover_listener_set_value,
					     dhcp_failover_listener_get_value,
					     dhcp_failover_listener_destroy,
					     dhcp_failover_listener_signal,
					     dhcp_failover_listener_stuff,
					     0, 0, 0, 0, 0, 0,
					     sizeof
					     (dhcp_failover_listener_t), 0);

	if (status != ISC_R_SUCCESS)
		log_fatal ("Can't register failover listener object type: %s",
			   isc_result_totext (status));
#endif /* FAILOVER_PROTOCOL */
}

isc_result_t dhcp_lease_set_value  (omapi_object_t *h,
				    omapi_object_t *id,
				    omapi_data_string_t *name,
				    omapi_typed_data_t *value)
{
	struct lease *lease;
	isc_result_t status;
	int foo;

	if (h -> type != dhcp_type_lease)
		return ISC_R_INVALIDARG;
	lease = (struct lease *)h;

	/* We're skipping a lot of things it might be interesting to
	   set - for now, we just make it possible to whack the state. */
	if (!omapi_ds_strcmp (name, "state")) {
	    unsigned long bar;
	    status = omapi_get_int_value (&bar, value);
	    if (status != ISC_R_SUCCESS)
		return status;
	    
	    if (bar < 1 || bar > FTS_BOOTP)
		return ISC_R_INVALIDARG;
	    if (lease -> binding_state != bar) {
		lease -> next_binding_state = bar;
		if (supersede_lease (lease, 0, 1, 1, 1))
			return ISC_R_SUCCESS;
		return ISC_R_IOERROR;
	    }
	    return ISC_R_UNCHANGED;
	} else if (!omapi_ds_strcmp (name, "ip-address")) {
	    return ISC_R_NOPERM;
	} else if (!omapi_ds_strcmp (name, "dhcp-client-identifier")) {
	    return ISC_R_UNCHANGED;	/* XXX take change. */
	} else if (!omapi_ds_strcmp (name, "hostname")) {
	    return ISC_R_UNCHANGED;	/* XXX take change. */
	} else if (!omapi_ds_strcmp (name, "client-hostname")) {
	    return ISC_R_UNCHANGED;	/* XXX take change. */
	} else if (!omapi_ds_strcmp (name, "host")) {
	    return ISC_R_UNCHANGED;	/* XXX take change. */
	} else if (!omapi_ds_strcmp (name, "subnet")) {
	    return ISC_R_INVALIDARG;
	} else if (!omapi_ds_strcmp (name, "pool")) {
	    return ISC_R_NOPERM;
	} else if (!omapi_ds_strcmp (name, "starts")) {
	    return ISC_R_NOPERM;
	} else if (!omapi_ds_strcmp (name, "ends")) {
	    return ISC_R_NOPERM;
	} else if (!omapi_ds_strcmp (name, "billing-class")) {
	    return ISC_R_UNCHANGED;	/* XXX carefully allow change. */
	} else if (!omapi_ds_strcmp (name, "hardware-address")) {
	    return ISC_R_UNCHANGED;	/* XXX take change. */
	} else if (!omapi_ds_strcmp (name, "hardware-type")) {
	    return ISC_R_UNCHANGED;	/* XXX take change. */
	} else if (lease -> scope) {
	    status = binding_scope_set_value (lease -> scope, 0, name, value);
	    if (status == ISC_R_SUCCESS) {
		    if (write_lease (lease) && commit_leases ())
			    return ISC_R_SUCCESS;
		    return ISC_R_IOERROR;
	    }
	}

	/* Try to find some inner object that can take the value. */
	if (h -> inner && h -> inner -> type -> set_value) {
		status = ((*(h -> inner -> type -> set_value))
			  (h -> inner, id, name, value));
		if (status == ISC_R_SUCCESS || status == ISC_R_UNCHANGED)
			return status;
	}
			  
	if (!lease -> scope) {
		if (!binding_scope_allocate (&lease -> scope, MDL))
			return ISC_R_NOMEMORY;
	}
	status = binding_scope_set_value (lease -> scope, 1, name, value);
	if (status != ISC_R_SUCCESS)
		return status;

	if (write_lease (lease) && commit_leases ())
		return ISC_R_SUCCESS;
	return ISC_R_IOERROR;
}


isc_result_t dhcp_lease_get_value (omapi_object_t *h, omapi_object_t *id,
				   omapi_data_string_t *name,
				   omapi_value_t **value)
{
	struct lease *lease;
	isc_result_t status;

	if (h -> type != dhcp_type_lease)
		return ISC_R_INVALIDARG;
	lease = (struct lease *)h;

	if (!omapi_ds_strcmp (name, "state"))
		return omapi_make_int_value (value, name,
					     (int)lease -> binding_state, MDL);
	else if (!omapi_ds_strcmp (name, "ip-address"))
		return omapi_make_const_value (value, name,
					       lease -> ip_addr.iabuf,
					       lease -> ip_addr.len, MDL);
	else if (!omapi_ds_strcmp (name, "dhcp-client-identifier")) {
		return omapi_make_const_value (value, name,
					       lease -> uid,
					       lease -> uid_len, MDL);
	} else if (!omapi_ds_strcmp (name, "client-hostname")) {
		if (lease -> client_hostname)
			return omapi_make_string_value
				(value, name, lease -> client_hostname, MDL);
		return ISC_R_NOTFOUND;
	} else if (!omapi_ds_strcmp (name, "host")) {
		if (lease -> host)
			return omapi_make_handle_value
				(value, name,
				 ((omapi_object_t *)lease -> host), MDL);
	} else if (!omapi_ds_strcmp (name, "subnet"))
		return omapi_make_handle_value (value, name,
						((omapi_object_t *)
						 lease -> subnet), MDL);
	else if (!omapi_ds_strcmp (name, "pool"))
		return omapi_make_handle_value (value, name,
						((omapi_object_t *)
						 lease -> pool), MDL);
	else if (!omapi_ds_strcmp (name, "billing-class")) {
		if (lease -> billing_class)
			return omapi_make_handle_value
				(value, name,
				 ((omapi_object_t *)lease -> billing_class),
				 MDL);
		return ISC_R_NOTFOUND;
	} else if (!omapi_ds_strcmp (name, "hardware-address")) {
		if (lease -> hardware_addr.hlen)
			return omapi_make_const_value
				(value, name, &lease -> hardware_addr.hbuf [1],
				 (unsigned)(lease -> hardware_addr.hlen - 1),
				 MDL);
		return ISC_R_NOTFOUND;
	} else if (!omapi_ds_strcmp (name, "hardware-type")) {
		if (lease -> hardware_addr.hlen)
			return omapi_make_int_value
				(value, name, lease -> hardware_addr.hbuf [0],
				 MDL);
		return ISC_R_NOTFOUND;
	} else if (lease -> scope) {
		status = binding_scope_get_value (value, lease -> scope, name);
		if (status != ISC_R_NOTFOUND)
			return status;
	}

	/* Try to find some inner object that can take the value. */
	if (h -> inner && h -> inner -> type -> get_value) {
		status = ((*(h -> inner -> type -> get_value))
			  (h -> inner, id, name, value));
		if (status == ISC_R_SUCCESS)
			return status;
	}
	return ISC_R_UNKNOWNATTRIBUTE;
}

isc_result_t dhcp_lease_destroy (omapi_object_t *h, const char *file, int line)
{
	struct lease *lease;
	isc_result_t status;

	if (h -> type != dhcp_type_lease)
		return ISC_R_INVALIDARG;
	lease = (struct lease *)h;

	if (lease -> uid)
		uid_hash_delete (lease);
	hw_hash_delete (lease);

	if (lease -> on_release)
		executable_statement_dereference (&lease -> on_release,
						  file, line);
	if (lease -> on_expiry)
		executable_statement_dereference (&lease -> on_expiry,
						  file, line);
	if (lease -> on_commit)
		executable_statement_dereference (&lease -> on_commit,
						  file, line);
	if (lease -> scope)
		binding_scope_dereference (&lease -> scope, file, line);

	if (lease -> agent_options)
		option_chain_head_dereference (&lease -> agent_options,
					       file, line);
	if (lease -> uid && lease -> uid != lease -> uid_buf) {
		dfree (lease -> uid, MDL);
		lease -> uid = &lease -> uid_buf [0];
		lease -> uid_len = 0;
	}

	if (lease -> client_hostname) {
		dfree (lease -> client_hostname, MDL);
		lease -> client_hostname = (char *)0;
	}

	if (lease -> host)
		host_dereference (&lease -> host, file, line);
	if (lease -> subnet)
		subnet_dereference (&lease -> subnet, file, line);
	if (lease -> pool)
		pool_dereference (&lease -> pool, file, line);

	if (lease -> state) {
		free_lease_state (lease -> state, file, line);
		lease -> state = (struct lease_state *)0;

		cancel_timeout (lease_ping_timeout, lease);
		--outstanding_pings; /* XXX */
	}

	if (lease -> billing_class)
		class_dereference
			(&lease -> billing_class, file, line);

#if defined (DEBUG_MEMORY_LEAKAGE) || \
		defined (DEBUG_MEMORY_LEAKAGE_ON_EXIT)
	/* XXX we should never be destroying a lease with a next
	   XXX pointer except on exit... */
	if (lease -> next)
		lease_dereference (&lease -> next, file, line);
	if (lease -> n_hw)
		lease_dereference (&lease -> n_hw, file, line);
	if (lease -> n_uid)
		lease_dereference (&lease -> n_uid, file, line);
	if (lease -> next_pending)
		lease_dereference (&lease -> next_pending, file, line);
#endif

	return ISC_R_SUCCESS;
}

isc_result_t dhcp_lease_signal_handler (omapi_object_t *h,
					const char *name, va_list ap)
{
	struct lease *lease;
	isc_result_t status;
	int updatep = 0;

	if (h -> type != dhcp_type_lease)
		return ISC_R_INVALIDARG;
	lease = (struct lease *)h;

	if (!strcmp (name, "updated"))
		return ISC_R_SUCCESS;

	/* Try to find some inner object that can take the value. */
	if (h -> inner && h -> inner -> type -> signal_handler) {
		status = ((*(h -> inner -> type -> signal_handler))
			  (h -> inner, name, ap));
		if (status == ISC_R_SUCCESS)
			return status;
	}
	return ISC_R_NOTFOUND;
}

isc_result_t dhcp_lease_stuff_values (omapi_object_t *c,
				      omapi_object_t *id,
				      omapi_object_t *h)
{
	struct lease *lease;
	isc_result_t status;

	if (h -> type != dhcp_type_lease)
		return ISC_R_INVALIDARG;
	lease = (struct lease *)h;

	/* Write out all the values. */

	status = omapi_connection_put_name (c, "state");
	if (status != ISC_R_SUCCESS)
		return status;
	status = omapi_connection_put_uint32 (c, sizeof (int));
	if (status != ISC_R_SUCCESS)
		return status;
	status = omapi_connection_put_uint32 (c, lease -> binding_state);
	if (status != ISC_R_SUCCESS)
		return status;

	status = omapi_connection_put_name (c, "ip-address");
	if (status != ISC_R_SUCCESS)
		return status;
	status = omapi_connection_put_uint32 (c, lease -> ip_addr.len);
	if (status != ISC_R_SUCCESS)
		return status;
	status = omapi_connection_copyin (c, lease -> ip_addr.iabuf,
					  lease -> ip_addr.len);
	if (status != ISC_R_SUCCESS)
		return status;

	if (lease -> uid_len) {
		status = omapi_connection_put_name (c,
						    "dhcp-client-identifier");
		if (status != ISC_R_SUCCESS)
			return status;
		status = omapi_connection_put_uint32 (c, lease -> uid_len);
		if (status != ISC_R_SUCCESS)
			return status;
		if (lease -> uid_len) {
			status = omapi_connection_copyin (c, lease -> uid,
							  lease -> uid_len);
			if (status != ISC_R_SUCCESS)
				return status;
		}
	}

	if (lease -> client_hostname) {
		status = omapi_connection_put_name (c, "client-hostname");
		if (status != ISC_R_SUCCESS)
			return status;
		status =
			omapi_connection_put_string (c,
						     lease -> client_hostname);
		if (status != ISC_R_SUCCESS)
			return status;
	}

	if (lease -> host) {
		status = omapi_connection_put_name (c, "host");
		if (status != ISC_R_SUCCESS)
			return status;
		status = omapi_connection_put_handle (c,
						      (omapi_object_t *)
						      lease -> host);
		if (status != ISC_R_SUCCESS)
			return status;
	}

	status = omapi_connection_put_name (c, "subnet");
	if (status != ISC_R_SUCCESS)
		return status;
	status = omapi_connection_put_handle
		(c, (omapi_object_t *)lease -> subnet);
	if (status != ISC_R_SUCCESS)
		return status;

	status = omapi_connection_put_name (c, "pool");
	if (status != ISC_R_SUCCESS)
		return status;
	status = omapi_connection_put_handle (c,
					      (omapi_object_t *)lease -> pool);
	if (status != ISC_R_SUCCESS)
		return status;

	if (lease -> billing_class) {
		status = omapi_connection_put_name (c, "billing-class");
		if (status != ISC_R_SUCCESS)
			return status;
		status = omapi_connection_put_handle
			(c, (omapi_object_t *)lease -> billing_class);
		if (status != ISC_R_SUCCESS)
			return status;
	}

	if (lease -> hardware_addr.hlen) {
		status = omapi_connection_put_name (c, "hardware-address");
		if (status != ISC_R_SUCCESS)
			return status;
		status = (omapi_connection_put_uint32
			  (c,
			   (unsigned long)(lease -> hardware_addr.hlen - 1)));
		if (status != ISC_R_SUCCESS)
			return status;
		status = (omapi_connection_copyin
			  (c, &lease -> hardware_addr.hbuf [1],
			   (unsigned long)(lease -> hardware_addr.hlen - 1)));

		if (status != ISC_R_SUCCESS)
			return status;

		status = omapi_connection_put_name (c, "hardware-type");
		if (status != ISC_R_SUCCESS)
			return status;
		status = omapi_connection_put_uint32 (c, sizeof (int));
		if (status != ISC_R_SUCCESS)
			return status;
		status = omapi_connection_put_uint32
			(c, lease -> hardware_addr.hbuf [0]);
		if (status != ISC_R_SUCCESS)
			return status;
	}


	status = omapi_connection_put_name (c, "ends");
	if (status != ISC_R_SUCCESS)
		return status;
	status = omapi_connection_put_uint32 (c, sizeof (TIME));
	if (status != ISC_R_SUCCESS)
		return status;
	status = (omapi_connection_copyin
		  (c, (const unsigned char *)&(lease -> ends), sizeof(TIME)));
	if (status != ISC_R_SUCCESS)
		return status;

	status = omapi_connection_put_name (c, "starts");
	if (status != ISC_R_SUCCESS)
		return status;
	status = omapi_connection_put_uint32 (c, sizeof (TIME));
	if (status != ISC_R_SUCCESS)
		return status;
	status = (omapi_connection_copyin
		  (c,
		   (const unsigned char *)&(lease -> starts), sizeof (TIME)));
	if (status != ISC_R_SUCCESS)
		return status;

	status = omapi_connection_put_name (c, "tstp");
	if (status != ISC_R_SUCCESS)
		return status;
	status = omapi_connection_put_uint32 (c, sizeof (TIME));
	if (status != ISC_R_SUCCESS)
		return status;
	status = (omapi_connection_copyin
		  (c,
		   (const unsigned char *)&(lease -> tstp), sizeof (TIME)));
	if (status != ISC_R_SUCCESS)
		return status;

	status = omapi_connection_put_name (c, "tsfp");
	if (status != ISC_R_SUCCESS)
		return status;
	status = omapi_connection_put_uint32 (c, sizeof (TIME));
	if (status != ISC_R_SUCCESS)
		return status;
	status = (omapi_connection_copyin
		  (c,
		   (const unsigned char *)&(lease -> tsfp), sizeof (TIME)));
	if (status != ISC_R_SUCCESS)
		return status;

	status = omapi_connection_put_name (c, "cltt");
	if (status != ISC_R_SUCCESS)
		return status;
	status = omapi_connection_put_uint32 (c, sizeof (TIME));
	if (status != ISC_R_SUCCESS)
		return status;
	status = (omapi_connection_copyin
		  (c,
		   (const unsigned char *)&(lease -> cltt), sizeof (TIME)));
	if (status != ISC_R_SUCCESS)
		return status;

	if (lease -> scope) {
		status = binding_scope_stuff_values (c, lease -> scope);
		if (status != ISC_R_SUCCESS)
			return status;
	}

	/* Write out the inner object, if any. */
	if (h -> inner && h -> inner -> type -> stuff_values) {
		status = ((*(h -> inner -> type -> stuff_values))
			  (c, id, h -> inner));
		if (status == ISC_R_SUCCESS)
			return status;
	}

	return ISC_R_SUCCESS;
}

isc_result_t dhcp_lease_lookup (omapi_object_t **lp,
				omapi_object_t *id, omapi_object_t *ref)
{
	omapi_value_t *tv = (omapi_value_t *)0;
	isc_result_t status;
	struct lease *lease;

	if (!ref)
		return ISC_R_NOKEYS;

	/* First see if we were sent a handle. */
	status = omapi_get_value_str (ref, id, "handle", &tv);
	if (status == ISC_R_SUCCESS) {
		status = omapi_handle_td_lookup (lp, tv -> value);

		omapi_value_dereference (&tv, MDL);
		if (status != ISC_R_SUCCESS)
			return status;

		/* Don't return the object if the type is wrong. */
		if ((*lp) -> type != dhcp_type_lease) {
			omapi_object_dereference (lp, MDL);
			return ISC_R_INVALIDARG;
		}
	}

	/* Now look for an IP address. */
	status = omapi_get_value_str (ref, id, "ip-address", &tv);
	if (status == ISC_R_SUCCESS) {
		lease = (struct lease *)0;
		lease_hash_lookup (&lease, lease_ip_addr_hash,
				   tv -> value -> u.buffer.value,
				   tv -> value -> u.buffer.len, MDL);

		omapi_value_dereference (&tv, MDL);

		/* If we already have a lease, and it's not the same one,
		   then the query was invalid. */
		if (*lp && *lp != (omapi_object_t *)lease) {
			omapi_object_dereference (lp, MDL);
			lease_dereference (&lease, MDL);
			return ISC_R_KEYCONFLICT;
		} else if (!lease) {
			if (*lp)
				omapi_object_dereference (lp, MDL);
			return ISC_R_NOTFOUND;
		} else if (!*lp) {
			/* XXX fix so that hash lookup itself creates
			   XXX the reference. */
			omapi_object_reference (lp,
						(omapi_object_t *)lease, MDL);
			lease_dereference (&lease, MDL);
		}
	}

	/* Now look for a client identifier. */
	status = omapi_get_value_str (ref, id, "dhcp-client-identifier", &tv);
	if (status == ISC_R_SUCCESS) {
		lease = (struct lease *)0;
		lease_hash_lookup (&lease, lease_uid_hash,
				   tv -> value -> u.buffer.value,
				   tv -> value -> u.buffer.len, MDL);
		omapi_value_dereference (&tv, MDL);
			
		if (*lp && *lp != (omapi_object_t *)lease) {
			omapi_object_dereference (lp, MDL);
			lease_dereference (&lease, MDL);
			return ISC_R_KEYCONFLICT;
		} else if (!lease) {
			if (*lp)
			    omapi_object_dereference (lp, MDL);
			return ISC_R_NOTFOUND;
		} else if (lease -> n_uid) {
			if (*lp)
			    omapi_object_dereference (lp, MDL);
			return ISC_R_MULTIPLE;
		} else if (!*lp) {
			/* XXX fix so that hash lookup itself creates
			   XXX the reference. */
			omapi_object_reference (lp,
						(omapi_object_t *)lease, MDL);
			lease_dereference (&lease, MDL);
		}
	}

	/* Now look for a hardware address. */
	status = omapi_get_value_str (ref, id, "hardware-address", &tv);
	if (status == ISC_R_SUCCESS) {
		lease = (struct lease *)0;
		lease_hash_lookup (&lease, lease_hw_addr_hash,
				   tv -> value -> u.buffer.value,
				   tv -> value -> u.buffer.len, MDL);
		omapi_value_dereference (&tv, MDL);
			
		if (*lp && *lp != (omapi_object_t *)lease) {
			omapi_object_dereference (lp, MDL);
			lease_dereference (&lease, MDL);
			return ISC_R_KEYCONFLICT;
		} else if (!lease) {
			if (*lp)
			    omapi_object_dereference (lp, MDL);
			return ISC_R_NOTFOUND;
		} else if (lease -> n_hw) {
			if (*lp)
			    omapi_object_dereference (lp, MDL);
			lease_dereference (&lease, MDL);
			return ISC_R_MULTIPLE;
		} else if (!*lp) {
			/* XXX fix so that hash lookup itself creates
			   XXX the reference. */
			omapi_object_reference (lp,
						(omapi_object_t *)lease, MDL);
			lease_dereference (&lease, MDL);
		}
	}

	/* If we get to here without finding a lease, no valid key was
	   specified. */
	if (!*lp)
		return ISC_R_NOKEYS;
	return ISC_R_SUCCESS;
}

isc_result_t dhcp_lease_create (omapi_object_t **lp,
				omapi_object_t *id)
{
	return ISC_R_NOTIMPLEMENTED;
}

isc_result_t dhcp_lease_remove (omapi_object_t *lp,
				omapi_object_t *id)
{
	return ISC_R_NOTIMPLEMENTED;
}

isc_result_t dhcp_host_set_value  (omapi_object_t *h,
				   omapi_object_t *id,
				   omapi_data_string_t *name,
				   omapi_typed_data_t *value)
{
	struct host_decl *host, *hp;
	isc_result_t status;
	int foo;

	if (h -> type != dhcp_type_host)
		return ISC_R_INVALIDARG;
	host = (struct host_decl *)h;

	/* XXX For now, we can only set these values on new host objects. 
	   XXX Soon, we need to be able to update host objects. */
	if (!omapi_ds_strcmp (name, "name")) {
		if (host -> name)
			return ISC_R_EXISTS;
		if (value -> type == omapi_datatype_data ||
		    value -> type == omapi_datatype_string) {
			host -> name = dmalloc (value -> u.buffer.len + 1,
						MDL);
			if (!host -> name)
				return ISC_R_NOMEMORY;
			memcpy (host -> name,
				value -> u.buffer.value,
				value -> u.buffer.len);
			host -> name [value -> u.buffer.len] = 0;
		} else
			return ISC_R_INVALIDARG;
		return ISC_R_SUCCESS;
	}

	if (!omapi_ds_strcmp (name, "group")) {
		if (value -> type == omapi_datatype_data ||
		    value -> type == omapi_datatype_string) {
			struct group_object *group;
			group = (struct group_object *)0;
			group_hash_lookup (&group, group_name_hash,
					   (char *)value -> u.buffer.value,
					   value -> u.buffer.len, MDL);
			if (!group || (group -> flags & GROUP_OBJECT_DELETED))
				return ISC_R_NOTFOUND;
			if (host -> group)
				group_dereference (&host -> group, MDL);
			group_reference (&host -> group, group -> group, MDL);
			if (host -> named_group)
				group_object_dereference (&host -> named_group,
							  MDL);
			group_object_reference (&host -> named_group,
						group, MDL);
			group_object_dereference (&group, MDL);
		} else
			return ISC_R_INVALIDARG;
		return ISC_R_SUCCESS;
	}

	if (!omapi_ds_strcmp (name, "hardware-address")) {
		if (host -> interface.hlen)
			return ISC_R_EXISTS;
		if (value -> type == omapi_datatype_data ||
		    value -> type == omapi_datatype_string) {
			if (value -> u.buffer.len >
			    (sizeof host -> interface.hbuf) - 1)
				return ISC_R_INVALIDARG;
			memcpy (&host -> interface.hbuf [1],
				value -> u.buffer.value,
				value -> u.buffer.len);
			host -> interface.hlen = value -> u.buffer.len + 1;
		} else
			return ISC_R_INVALIDARG;
		return ISC_R_SUCCESS;
	}

	if (!omapi_ds_strcmp (name, "hardware-type")) {
		int type;
		if (value -> type == omapi_datatype_data &&
		    value -> u.buffer.len == sizeof type) {
			if (value -> u.buffer.len > sizeof type)
				return ISC_R_INVALIDARG;
			memcpy (&type,
				value -> u.buffer.value,
				value -> u.buffer.len);
			type = ntohl (type);
		} else if (value -> type == omapi_datatype_int)
			type = value -> u.integer;
		else
			return ISC_R_INVALIDARG;
		host -> interface.hbuf [0] = type;
		return ISC_R_SUCCESS;
	}

	if (!omapi_ds_strcmp (name, "dhcp-client-identifier")) {
		if (host -> client_identifier.data)
			return ISC_R_EXISTS;
		if (value -> type == omapi_datatype_data ||
		    value -> type == omapi_datatype_string) {
		    if (!buffer_allocate (&host -> client_identifier.buffer,
					  value -> u.buffer.len, MDL))
			    return ISC_R_NOMEMORY;
		    host -> client_identifier.data =
			    &host -> client_identifier.buffer -> data [0];
		    memcpy (host -> client_identifier.buffer -> data,
			    value -> u.buffer.value,
			    value -> u.buffer.len);
		    host -> client_identifier.len = value -> u.buffer.len;
		} else
		    return ISC_R_INVALIDARG;
		return ISC_R_SUCCESS;
	}

	if (!omapi_ds_strcmp (name, "ip-address")) {
		if (host -> fixed_addr)
			option_cache_dereference (&host -> fixed_addr, MDL);
		if (!value)
			return ISC_R_SUCCESS;
		if (value -> type == omapi_datatype_data ||
		    value -> type == omapi_datatype_string) {
			struct data_string ds;
			memset (&ds, 0, sizeof ds);
			ds.len = value -> u.buffer.len;
			if (!buffer_allocate (&ds.buffer, ds.len, MDL))
				return ISC_R_NOMEMORY;
			ds.data = (&ds.buffer -> data [0]);
			memcpy (ds.buffer -> data,
				value -> u.buffer.value, ds.len);
			if (!option_cache (&host -> fixed_addr,
					   &ds, (struct expression *)0,
					   (struct option *)0, MDL)) {
				data_string_forget (&ds, MDL);
				return ISC_R_NOMEMORY;
			}
			data_string_forget (&ds, MDL);
		} else
			return ISC_R_INVALIDARG;
		return ISC_R_SUCCESS;
	}

	if (!omapi_ds_strcmp (name, "statements")) {
		if (!host -> group) {
			if (!clone_group (&host -> group, root_group, MDL))
				return ISC_R_NOMEMORY;
		} else {
			if (host -> group -> statements &&
			    (!host -> named_group ||
			     host -> group != host -> named_group -> group) &&
			    host -> group != root_group)
				return ISC_R_EXISTS;
			if (!clone_group (&host -> group, host -> group, MDL))
				return ISC_R_NOMEMORY;
		}
		if (!host -> group)
			return ISC_R_NOMEMORY;
		if (value -> type == omapi_datatype_data ||
		    value -> type == omapi_datatype_string) {
			struct parse *parse;
			int lose = 0;
			parse = (struct parse *)0;
			status = new_parse (&parse, -1,
					    (char *)value -> u.buffer.value,
					    value -> u.buffer.len,
					    "network client", 0);
			if (status != ISC_R_SUCCESS)
				return status;
			if (!(parse_executable_statements
			      (&host -> group -> statements, parse, &lose,
			       context_any))) {
				end_parse (&parse);
				return ISC_R_BADPARSE;
			}
			end_parse (&parse);
		} else
			return ISC_R_INVALIDARG;
		return ISC_R_SUCCESS;
	}

	/* The "known" flag isn't supported in the database yet, but it's
	   legitimate. */
	if (!omapi_ds_strcmp (name, "known")) {
		return ISC_R_SUCCESS;
	}

	/* Try to find some inner object that can take the value. */
	if (h -> inner && h -> inner -> type -> set_value) {
		status = ((*(h -> inner -> type -> set_value))
			  (h -> inner, id, name, value));
		if (status == ISC_R_SUCCESS || status == ISC_R_UNCHANGED)
			return status;
	}
			  
	return ISC_R_UNKNOWNATTRIBUTE;
}


isc_result_t dhcp_host_get_value (omapi_object_t *h, omapi_object_t *id,
				   omapi_data_string_t *name,
				   omapi_value_t **value)
{
	struct host_decl *host;
	isc_result_t status;
	struct data_string ip_addrs;

	if (h -> type != dhcp_type_host)
		return ISC_R_INVALIDARG;
	host = (struct host_decl *)h;

	if (!omapi_ds_strcmp (name, "ip-addresses")) {
	    memset (&ip_addrs, 0, sizeof ip_addrs);
	    if (host -> fixed_addr &&
		evaluate_option_cache (&ip_addrs, (struct packet *)0,
				       (struct lease *)0,
				       (struct client_state *)0,
				       (struct option_state *)0,
				       (struct option_state *)0,
				       &global_scope,
				       host -> fixed_addr, MDL)) {
		    status = omapi_make_const_value (value, name,
						     ip_addrs.data,
						     ip_addrs.len, MDL);
		    data_string_forget (&ip_addrs, MDL);
		    return status;
	    }
	    return ISC_R_NOTFOUND;
	}

	if (!omapi_ds_strcmp (name, "dhcp-client-identifier")) {
		if (!host -> client_identifier.len)
			return ISC_R_NOTFOUND;
		return omapi_make_const_value (value, name,
					       host -> client_identifier.data,
					       host -> client_identifier.len,
					       MDL);
	}

	if (!omapi_ds_strcmp (name, "name"))
		return omapi_make_string_value (value, name, host -> name,
						MDL);

	if (!omapi_ds_strcmp (name, "hardware-address")) {
		if (!host -> interface.hlen)
			return ISC_R_NOTFOUND;
		return (omapi_make_const_value
			(value, name, &host -> interface.hbuf [1],
			 (unsigned long)(host -> interface.hlen - 1), MDL));
	}

	if (!omapi_ds_strcmp (name, "hardware-type")) {
		if (!host -> interface.hlen)
			return ISC_R_NOTFOUND;
		return omapi_make_int_value (value, name,
					     host -> interface.hbuf [0], MDL);
	}

	/* Try to find some inner object that can take the value. */
	if (h -> inner && h -> inner -> type -> get_value) {
		status = ((*(h -> inner -> type -> get_value))
			  (h -> inner, id, name, value));
		if (status == ISC_R_SUCCESS)
			return status;
	}
	return ISC_R_UNKNOWNATTRIBUTE;
}

isc_result_t dhcp_host_destroy (omapi_object_t *h, const char *file, int line)
{
	struct host_decl *host;
	isc_result_t status;

	if (h -> type != dhcp_type_host)
		return ISC_R_INVALIDARG;
	host = (struct host_decl *)h;

#if defined (DEBUG_MEMORY_LEAKAGE) || \
		defined (DEBUG_MEMORY_LEAKAGE_ON_EXIT)
	if (host -> n_ipaddr)
		host_dereference (&host -> n_ipaddr, file, line);
	if (host -> n_dynamic)
		host_dereference (&host -> n_dynamic, file, line);
	if (host -> name) {
		dfree (host -> name, file, line);
		host -> name = (char *)0;
	}
	data_string_forget (&host -> client_identifier, file, line);
	if (host -> fixed_addr)
		option_cache_dereference (&host -> fixed_addr, file, line);
	if (host -> group)
		group_dereference (&host -> group, file, line);
	if (host -> named_group)
		omapi_object_dereference ((omapi_object_t **)
					  &host -> named_group, file, line);
	data_string_forget (&host -> auth_key_id, file, line);
#endif

	return ISC_R_SUCCESS;
}

isc_result_t dhcp_host_signal_handler (omapi_object_t *h,
				       const char *name, va_list ap)
{
	struct host_decl *host;
	isc_result_t status;
	int updatep = 0;

	if (h -> type != dhcp_type_host)
		return ISC_R_INVALIDARG;
	host = (struct host_decl *)h;

	if (!strcmp (name, "updated")) {
		/* There must be a client identifier of some sort. */
		if (host -> interface.hlen == 0 &&
		    !host -> client_identifier.len)
			return ISC_R_INVALIDARG;

		if (!host -> name) {
			char hnbuf [64];
			sprintf (hnbuf, "nh%08lx%08lx",
				 (unsigned long)cur_time, (unsigned long)host);
			host -> name = dmalloc (strlen (hnbuf) + 1, MDL);
			if (!host -> name)
				return ISC_R_NOMEMORY;
			strcpy (host -> name, hnbuf);
		}

#ifdef DEBUG_OMAPI
		log_debug ("OMAPI added host %s", host -> name);
#endif
		status = enter_host (host, 1, 1);
		if (status != ISC_R_SUCCESS)
			return status;
		updatep = 1;
	}

	/* Try to find some inner object that can take the value. */
	if (h -> inner && h -> inner -> type -> signal_handler) {
		status = ((*(h -> inner -> type -> signal_handler))
			  (h -> inner, name, ap));
		if (status == ISC_R_SUCCESS)
			return status;
	}
	if (updatep)
		return ISC_R_SUCCESS;
	return ISC_R_NOTFOUND;
}

isc_result_t dhcp_host_stuff_values (omapi_object_t *c,
				      omapi_object_t *id,
				      omapi_object_t *h)
{
	struct host_decl *host;
	isc_result_t status;
	struct data_string ip_addrs;

	if (h -> type != dhcp_type_host)
		return ISC_R_INVALIDARG;
	host = (struct host_decl *)h;

	/* Write out all the values. */

	memset (&ip_addrs, 0, sizeof ip_addrs);
	if (host -> fixed_addr &&
	    evaluate_option_cache (&ip_addrs, (struct packet *)0,
				   (struct lease *)0,
				   (struct client_state *)0,
				   (struct option_state *)0,
				   (struct option_state *)0,
				   &global_scope,
				   host -> fixed_addr, MDL)) {
		status = omapi_connection_put_name (c, "ip-address");
		if (status != ISC_R_SUCCESS)
			return status;
		status = omapi_connection_put_uint32 (c, ip_addrs.len);
		if (status != ISC_R_SUCCESS)
			return status;
		status = omapi_connection_copyin (c,
						  ip_addrs.data, ip_addrs.len);
		if (status != ISC_R_SUCCESS)
			return status;
	}

	if (host -> client_identifier.len) {
		status = omapi_connection_put_name (c,
						    "dhcp-client-identifier");
		if (status != ISC_R_SUCCESS)
			return status;
		status = (omapi_connection_put_uint32
			  (c, host -> client_identifier.len));
		if (status != ISC_R_SUCCESS)
			return status;
		status = (omapi_connection_copyin
			  (c,
			   host -> client_identifier.data,
			   host -> client_identifier.len));
		if (status != ISC_R_SUCCESS)
			return status;
	}

	if (host -> name) {
		status = omapi_connection_put_name (c, "name");
		if (status != ISC_R_SUCCESS)
			return status;
		status = omapi_connection_put_string (c, host -> name);
		if (status != ISC_R_SUCCESS)
			return status;
	}

	if (host -> interface.hlen) {
		status = omapi_connection_put_name (c, "hardware-address");
		if (status != ISC_R_SUCCESS)
			return status;
		status = (omapi_connection_put_uint32
			  (c, (unsigned long)(host -> interface.hlen - 1)));
		if (status != ISC_R_SUCCESS)
			return status;
		status = (omapi_connection_copyin
			  (c, &host -> interface.hbuf [1],
			   (unsigned long)(host -> interface.hlen - 1)));
		if (status != ISC_R_SUCCESS)
			return status;

		status = omapi_connection_put_name (c, "hardware-type");
		if (status != ISC_R_SUCCESS)
			return status;
		status = omapi_connection_put_uint32 (c, sizeof (int));
		if (status != ISC_R_SUCCESS)
			return status;
		status = (omapi_connection_put_uint32
			  (c, host -> interface.hbuf [0]));
		if (status != ISC_R_SUCCESS)
			return status;
	}

	/* Write out the inner object, if any. */
	if (h -> inner && h -> inner -> type -> stuff_values) {
		status = ((*(h -> inner -> type -> stuff_values))
			  (c, id, h -> inner));
		if (status == ISC_R_SUCCESS)
			return status;
	}

	return ISC_R_SUCCESS;
}

isc_result_t dhcp_host_lookup (omapi_object_t **lp,
				omapi_object_t *id, omapi_object_t *ref)
{
	omapi_value_t *tv = (omapi_value_t *)0;
	isc_result_t status;
	struct host_decl *host;

	if (!ref)
		return ISC_R_NOKEYS;

	/* First see if we were sent a handle. */
	status = omapi_get_value_str (ref, id, "handle", &tv);
	if (status == ISC_R_SUCCESS) {
		status = omapi_handle_td_lookup (lp, tv -> value);

		omapi_value_dereference (&tv, MDL);
		if (status != ISC_R_SUCCESS)
			return status;

		/* Don't return the object if the type is wrong. */
		if ((*lp) -> type != dhcp_type_host) {
			omapi_object_dereference (lp, MDL);
			return ISC_R_INVALIDARG;
		}
		if (((struct host_decl *)(*lp)) -> flags & HOST_DECL_DELETED) {
			omapi_object_dereference (lp, MDL);
		}
	}

	/* Now look for a client identifier. */
	status = omapi_get_value_str (ref, id, "dhcp-client-identifier", &tv);
	if (status == ISC_R_SUCCESS) {
		host = (struct host_decl *)0;
		host_hash_lookup (&host, host_uid_hash,
				  tv -> value -> u.buffer.value,
				  tv -> value -> u.buffer.len, MDL);
		omapi_value_dereference (&tv, MDL);
			
		if (*lp && *lp != (omapi_object_t *)host) {
			omapi_object_dereference (lp, MDL);
			if (host)
				host_dereference (&host, MDL);
			return ISC_R_KEYCONFLICT;
		} else if (!host || (host -> flags & HOST_DECL_DELETED)) {
			if (*lp)
			    omapi_object_dereference (lp, MDL);
			if (host)
				host_dereference (&host, MDL);
			return ISC_R_NOTFOUND;
		} else if (!*lp) {
			/* XXX fix so that hash lookup itself creates
			   XXX the reference. */
			omapi_object_reference (lp,
						(omapi_object_t *)host, MDL);
			host_dereference (&host, MDL);
		}
	}

	/* Now look for a hardware address. */
	status = omapi_get_value_str (ref, id, "hardware-address", &tv);
	if (status == ISC_R_SUCCESS) {
		unsigned char *haddr;
		unsigned int len;

		len = tv -> value -> u.buffer.len + 1;
		haddr = dmalloc (len, MDL);
		if (!haddr) {
			omapi_value_dereference (&tv, MDL);
			return ISC_R_NOMEMORY;
		}

		memcpy (haddr + 1, tv -> value -> u.buffer.value, len - 1);
		omapi_value_dereference (&tv, MDL);

		status = omapi_get_value_str (ref, id, "hardware-type", &tv);
		if (status == ISC_R_SUCCESS) {
			if (tv -> value -> type == omapi_datatype_data) {
				if ((tv -> value -> u.buffer.len != 4) ||
				    (tv -> value -> u.buffer.value[0] != 0) ||
				    (tv -> value -> u.buffer.value[1] != 0) ||
				    (tv -> value -> u.buffer.value[2] != 0)) {
					omapi_value_dereference (&tv, MDL);
					dfree (haddr, MDL);
					return ISC_R_INVALIDARG;
				}

				haddr[0] = tv -> value -> u.buffer.value[3];
			} else if (tv -> value -> type == omapi_datatype_int) {
				haddr[0] = (unsigned char)
					tv -> value -> u.integer;
			} else {
				omapi_value_dereference (&tv, MDL);
				dfree (haddr, MDL);
				return ISC_R_INVALIDARG;
			}

			omapi_value_dereference (&tv, MDL);
		} else {
			/* If no hardware-type is specified, default to
			   ethernet.  This may or may not be a good idea,
			   but Telus is currently relying on this behavior.
			   - DPN */
			haddr[0] = HTYPE_ETHER;
		}

		host = (struct host_decl *)0;
		host_hash_lookup (&host, host_hw_addr_hash, haddr, len, MDL);
		dfree (haddr, MDL);
			
		if (*lp && *lp != (omapi_object_t *)host) {
			omapi_object_dereference (lp, MDL);
			if (host)
				host_dereference (&host, MDL);
			return ISC_R_KEYCONFLICT;
		} else if (!host || (host -> flags & HOST_DECL_DELETED)) {
			if (*lp)
			    omapi_object_dereference (lp, MDL);
			if (host)
				host_dereference (&host, MDL);
			return ISC_R_NOTFOUND;
		} else if (!*lp) {
			/* XXX fix so that hash lookup itself creates
			   XXX the reference. */
			omapi_object_reference (lp,
						(omapi_object_t *)host, MDL);
			host_dereference (&host, MDL);
		}
	}

	/* Now look for an ip address. */
	status = omapi_get_value_str (ref, id, "ip-address", &tv);
	if (status == ISC_R_SUCCESS) {
		struct lease *l;

		/* first find the lease for this ip address */
		l = (struct lease *)0;
		lease_hash_lookup (&l, lease_ip_addr_hash,
				   tv -> value -> u.buffer.value,
				   tv -> value -> u.buffer.len, MDL);
		omapi_value_dereference (&tv, MDL);

		if (!l && !*lp)
			return ISC_R_NOTFOUND;

		if (l) {
			/* now use that to get a host */
			host = (struct host_decl *)0;
			host_hash_lookup (&host, host_hw_addr_hash,
					  l -> hardware_addr.hbuf,
					  l -> hardware_addr.hlen, MDL);
			
			if (host && *lp && *lp != (omapi_object_t *)host) {
			    omapi_object_dereference (lp, MDL);
			    if (host)
				host_dereference (&host, MDL);
			    return ISC_R_KEYCONFLICT;
			} else if (!host || (host -> flags &
					     HOST_DECL_DELETED)) {
			    if (host)
				host_dereference (&host, MDL);
			    if (!*lp)
				    return ISC_R_NOTFOUND;
			} else if (!*lp) {
				/* XXX fix so that hash lookup itself creates
				   XXX the reference. */
			    omapi_object_reference (lp, (omapi_object_t *)host,
						    MDL);
			    host_dereference (&host, MDL);
			}
			lease_dereference (&l, MDL);
		}
	}

	/* Now look for a name. */
	status = omapi_get_value_str (ref, id, "name", &tv);
	if (status == ISC_R_SUCCESS) {
		host = (struct host_decl *)0;
		host_hash_lookup (&host, host_name_hash,
				  tv -> value -> u.buffer.value,
				  tv -> value -> u.buffer.len, MDL);
		omapi_value_dereference (&tv, MDL);
			
		if (*lp && *lp != (omapi_object_t *)host) {
			omapi_object_dereference (lp, MDL);
			if (host)
			    host_dereference (&host, MDL);
			return ISC_R_KEYCONFLICT;
		} else if (!host || (host -> flags & HOST_DECL_DELETED)) {
			if (host)
			    host_dereference (&host, MDL);
			return ISC_R_NOTFOUND;	
		} else if (!*lp) {
			/* XXX fix so that hash lookup itself creates
			   XXX the reference. */
			omapi_object_reference (lp,
						(omapi_object_t *)host, MDL);
			host_dereference (&host, MDL);
		}
	}

	/* If we get to here without finding a host, no valid key was
	   specified. */
	if (!*lp)
		return ISC_R_NOKEYS;
	return ISC_R_SUCCESS;
}

isc_result_t dhcp_host_create (omapi_object_t **lp,
			       omapi_object_t *id)
{
	struct host_decl *hp;
	isc_result_t status;
	hp = (struct host_decl *)0;
	status = host_allocate (&hp, MDL);
	if (status != ISC_R_SUCCESS)
		return status;
	group_reference (&hp -> group, root_group, MDL);
	hp -> flags = HOST_DECL_DYNAMIC;
	status = omapi_object_reference (lp, (omapi_object_t *)hp, MDL);
	host_dereference (&hp, MDL);
	return status;
}

isc_result_t dhcp_host_remove (omapi_object_t *lp,
			       omapi_object_t *id)
{
	struct host_decl *hp;
	if (lp -> type != dhcp_type_host)
		return ISC_R_INVALIDARG;
	hp = (struct host_decl *)lp;

#ifdef DEBUG_OMAPI
	log_debug ("OMAPI delete host %s", hp -> name);
#endif
	delete_host (hp, 1);
	return ISC_R_SUCCESS;
}

isc_result_t dhcp_pool_set_value  (omapi_object_t *h,
				   omapi_object_t *id,
				   omapi_data_string_t *name,
				   omapi_typed_data_t *value)
{
	struct pool *pool;
	isc_result_t status;
	int foo;

	if (h -> type != dhcp_type_pool)
		return ISC_R_INVALIDARG;
	pool = (struct pool *)h;

	/* No values to set yet. */

	/* Try to find some inner object that can take the value. */
	if (h -> inner && h -> inner -> type -> set_value) {
		status = ((*(h -> inner -> type -> set_value))
			  (h -> inner, id, name, value));
		if (status == ISC_R_SUCCESS || status == ISC_R_UNCHANGED)
			return status;
	}
			  
	return ISC_R_UNKNOWNATTRIBUTE;
}


isc_result_t dhcp_pool_get_value (omapi_object_t *h, omapi_object_t *id,
				  omapi_data_string_t *name,
				  omapi_value_t **value)
{
	struct pool *pool;
	isc_result_t status;

	if (h -> type != dhcp_type_pool)
		return ISC_R_INVALIDARG;
	pool = (struct pool *)h;

	/* No values to get yet. */

	/* Try to find some inner object that can provide the value. */
	if (h -> inner && h -> inner -> type -> get_value) {
		status = ((*(h -> inner -> type -> get_value))
			  (h -> inner, id, name, value));
		if (status == ISC_R_SUCCESS)
			return status;
	}
	return ISC_R_UNKNOWNATTRIBUTE;
}

isc_result_t dhcp_pool_destroy (omapi_object_t *h, const char *file, int line)
{
	struct pool *pool;
	isc_result_t status;
	struct permit *pc, *pn;

	if (h -> type != dhcp_type_pool)
		return ISC_R_INVALIDARG;
	pool = (struct pool *)h;

#if defined (DEBUG_MEMORY_LEAKAGE) || \
		defined (DEBUG_MEMORY_LEAKAGE_ON_EXIT)
	if (pool -> next)
		pool_dereference (&pool -> next, file, line);
	if (pool -> group)
		group_dereference (&pool -> group, file, line);
	if (pool -> shared_network)
	    shared_network_dereference (&pool -> shared_network, file, line);
	if (pool -> active)
		lease_dereference (&pool -> active, file, line);
	if (pool -> expired)
		lease_dereference (&pool -> expired, file, line);
	if (pool -> free)
		lease_dereference (&pool -> free, file, line);
	if (pool -> backup)
		lease_dereference (&pool -> backup, file, line);
	if (pool -> abandoned)
		lease_dereference (&pool -> abandoned, file, line);
#if defined (FAILOVER_PROTOCOL)
	if (pool -> failover_peer)
		dhcp_failover_state_dereference (&pool -> failover_peer,
						 file, line);
#endif
	for (pc = pool -> permit_list; pc; pc = pn) {
		pn = pc -> next;
		free_permit (pc, file, line);
	}
	pool -> permit_list = (struct permit *)0;

	for (pc = pool -> prohibit_list; pc; pc = pn) {
		pn = pc -> next;
		free_permit (pc, file, line);
	}
	pool -> prohibit_list = (struct permit *)0;
#endif

	return ISC_R_SUCCESS;
}

isc_result_t dhcp_pool_signal_handler (omapi_object_t *h,
				       const char *name, va_list ap)
{
	struct pool *pool;
	isc_result_t status;
	int updatep = 0;

	if (h -> type != dhcp_type_pool)
		return ISC_R_INVALIDARG;
	pool = (struct pool *)h;

	/* Can't write pools yet. */

	/* Try to find some inner object that can take the value. */
	if (h -> inner && h -> inner -> type -> signal_handler) {
		status = ((*(h -> inner -> type -> signal_handler))
			  (h -> inner, name, ap));
		if (status == ISC_R_SUCCESS)
			return status;
	}
	if (updatep)
		return ISC_R_SUCCESS;
	return ISC_R_NOTFOUND;
}

isc_result_t dhcp_pool_stuff_values (omapi_object_t *c,
				     omapi_object_t *id,
				     omapi_object_t *h)
{
	struct pool *pool;
	isc_result_t status;

	if (h -> type != dhcp_type_pool)
		return ISC_R_INVALIDARG;
	pool = (struct pool *)h;

	/* Can't stuff pool values yet. */

	/* Write out the inner object, if any. */
	if (h -> inner && h -> inner -> type -> stuff_values) {
		status = ((*(h -> inner -> type -> stuff_values))
			  (c, id, h -> inner));
		if (status == ISC_R_SUCCESS)
			return status;
	}

	return ISC_R_SUCCESS;
}

isc_result_t dhcp_pool_lookup (omapi_object_t **lp,
			       omapi_object_t *id, omapi_object_t *ref)
{
	omapi_value_t *tv = (omapi_value_t *)0;
	isc_result_t status;
	struct pool *pool;

	/* Can't look up pools yet. */

	/* If we get to here without finding a pool, no valid key was
	   specified. */
	if (!*lp)
		return ISC_R_NOKEYS;
	return ISC_R_SUCCESS;
}

isc_result_t dhcp_pool_create (omapi_object_t **lp,
			       omapi_object_t *id)
{
	return ISC_R_NOTIMPLEMENTED;
}

isc_result_t dhcp_pool_remove (omapi_object_t *lp,
			       omapi_object_t *id)
{
	return ISC_R_NOTIMPLEMENTED;
}

isc_result_t dhcp_class_set_value  (omapi_object_t *h,
				    omapi_object_t *id,
				    omapi_data_string_t *name,
				    omapi_typed_data_t *value)
{
	struct class *class;
	isc_result_t status;
	int foo;

	if (h -> type != dhcp_type_class)
		return ISC_R_INVALIDARG;
	class = (struct class *)h;

	/* No values to set yet. */

	/* Try to find some inner object that can take the value. */
	if (h -> inner && h -> inner -> type -> set_value) {
		status = ((*(h -> inner -> type -> set_value))
			  (h -> inner, id, name, value));
		if (status == ISC_R_SUCCESS || status == ISC_R_UNCHANGED)
			return status;
	}
			  
	return ISC_R_UNKNOWNATTRIBUTE;
}


isc_result_t dhcp_class_get_value (omapi_object_t *h, omapi_object_t *id,
				   omapi_data_string_t *name,
				   omapi_value_t **value)
{
	struct class *class;
	isc_result_t status;

	if (h -> type != dhcp_type_class)
		return ISC_R_INVALIDARG;
	class = (struct class *)h;

	/* No values to get yet. */

	/* Try to find some inner object that can provide the value. */
	if (h -> inner && h -> inner -> type -> get_value) {
		status = ((*(h -> inner -> type -> get_value))
			  (h -> inner, id, name, value));
		if (status == ISC_R_SUCCESS)
			return status;
	}
	return ISC_R_UNKNOWNATTRIBUTE;
}

isc_result_t dhcp_class_destroy (omapi_object_t *h, const char *file, int line)
{
	struct class *class;
	isc_result_t status;
	int i;

	if (h -> type != dhcp_type_class && h -> type != dhcp_type_subclass)
		return ISC_R_INVALIDARG;
	class = (struct class *)h;

#if defined (DEBUG_MEMORY_LEAKAGE) || \
		defined (DEBUG_MEMORY_LEAKAGE_ON_EXIT)
	if (class -> nic)
		class_dereference (&class -> nic, file, line);
	if (class -> superclass)
		class_dereference (&class -> superclass, file, line);
	if (class -> name) {
		dfree (class -> name, file, line);
		class -> name = (char *)0;
	}
	if (class -> billed_leases) {
		for (i = 0; i < class -> lease_limit; i++) {
			if (class -> billed_leases [i]) {
				lease_dereference (&class -> billed_leases [i],
						   file, line);
			}
		}
		dfree (class -> billed_leases, file, line);
		class -> billed_leases = (struct lease **)0;
	}
	if (class -> hash) {
		free_hash_table (class -> hash, file, line);
		class -> hash = (struct hash_table *)0;
	}
	data_string_forget (&class -> hash_string, file, line);

	if (class -> expr)
		expression_dereference (&class -> expr, file, line);
	if (class -> submatch)
		expression_dereference (&class -> submatch, file, line);
	if (class -> group)
		group_dereference (&class -> group, file, line);
	if (class -> statements)
		executable_statement_dereference (&class -> statements,
						  file, line);
	if (class -> superclass)
		class_dereference (&class -> superclass, file, line);
#endif

	return ISC_R_SUCCESS;
}

isc_result_t dhcp_class_signal_handler (omapi_object_t *h,
					const char *name, va_list ap)
{
	struct class *class;
	isc_result_t status;
	int updatep = 0;

	if (h -> type != dhcp_type_class)
		return ISC_R_INVALIDARG;
	class = (struct class *)h;

	/* Can't write classs yet. */

	/* Try to find some inner object that can take the value. */
	if (h -> inner && h -> inner -> type -> signal_handler) {
		status = ((*(h -> inner -> type -> signal_handler))
			  (h -> inner, name, ap));
		if (status == ISC_R_SUCCESS)
			return status;
	}
	if (updatep)
		return ISC_R_SUCCESS;
	return ISC_R_NOTFOUND;
}

isc_result_t dhcp_class_stuff_values (omapi_object_t *c,
				      omapi_object_t *id,
				      omapi_object_t *h)
{
	struct class *class;
	isc_result_t status;

	if (h -> type != dhcp_type_class)
		return ISC_R_INVALIDARG;
	class = (struct class *)h;

	/* Can't stuff class values yet. */

	/* Write out the inner object, if any. */
	if (h -> inner && h -> inner -> type -> stuff_values) {
		status = ((*(h -> inner -> type -> stuff_values))
			  (c, id, h -> inner));
		if (status == ISC_R_SUCCESS)
			return status;
	}

	return ISC_R_SUCCESS;
}

isc_result_t dhcp_class_lookup (omapi_object_t **lp,
				omapi_object_t *id, omapi_object_t *ref)
{
	omapi_value_t *tv = (omapi_value_t *)0;
	isc_result_t status;
	struct class *class;

	/* Can't look up classs yet. */

	/* If we get to here without finding a class, no valid key was
	   specified. */
	if (!*lp)
		return ISC_R_NOKEYS;
	return ISC_R_SUCCESS;
}

isc_result_t dhcp_class_create (omapi_object_t **lp,
				omapi_object_t *id)
{
	return ISC_R_NOTIMPLEMENTED;
}

isc_result_t dhcp_class_remove (omapi_object_t *lp,
				omapi_object_t *id)
{
	return ISC_R_NOTIMPLEMENTED;
}

isc_result_t dhcp_subclass_set_value  (omapi_object_t *h,
				       omapi_object_t *id,
				       omapi_data_string_t *name,
				       omapi_typed_data_t *value)
{
	struct subclass *subclass;
	isc_result_t status;
	int foo;

	if (h -> type != dhcp_type_subclass)
		return ISC_R_INVALIDARG;
	subclass = (struct subclass *)h;

	/* No values to set yet. */

	/* Try to find some inner object that can take the value. */
	if (h -> inner && h -> inner -> type -> set_value) {
		status = ((*(h -> inner -> type -> set_value))
			  (h -> inner, id, name, value));
		if (status == ISC_R_SUCCESS || status == ISC_R_UNCHANGED)
			return status;
	}
			  
	return ISC_R_UNKNOWNATTRIBUTE;
}


isc_result_t dhcp_subclass_get_value (omapi_object_t *h, omapi_object_t *id,
				      omapi_data_string_t *name,
				      omapi_value_t **value)
{
	struct subclass *subclass;
	isc_result_t status;

	if (h -> type != dhcp_type_subclass)
		return ISC_R_INVALIDARG;
	subclass = (struct subclass *)h;

	/* No values to get yet. */

	/* Try to find some inner object that can provide the value. */
	if (h -> inner && h -> inner -> type -> get_value) {
		status = ((*(h -> inner -> type -> get_value))
			  (h -> inner, id, name, value));
		if (status == ISC_R_SUCCESS)
			return status;
	}
	return ISC_R_UNKNOWNATTRIBUTE;
}

isc_result_t dhcp_subclass_signal_handler (omapi_object_t *h,
					   const char *name, va_list ap)
{
	struct subclass *subclass;
	isc_result_t status;
	int updatep = 0;

	if (h -> type != dhcp_type_subclass)
		return ISC_R_INVALIDARG;
	subclass = (struct subclass *)h;

	/* Can't write subclasss yet. */

	/* Try to find some inner object that can take the value. */
	if (h -> inner && h -> inner -> type -> signal_handler) {
		status = ((*(h -> inner -> type -> signal_handler))
			  (h -> inner, name, ap));
		if (status == ISC_R_SUCCESS)
			return status;
	}
	if (updatep)
		return ISC_R_SUCCESS;
	return ISC_R_NOTFOUND;
}

isc_result_t dhcp_subclass_stuff_values (omapi_object_t *c,
					 omapi_object_t *id,
					 omapi_object_t *h)
{
	struct subclass *subclass;
	isc_result_t status;

	if (h -> type != dhcp_type_subclass)
		return ISC_R_INVALIDARG;
	subclass = (struct subclass *)h;

	/* Can't stuff subclass values yet. */

	/* Write out the inner object, if any. */
	if (h -> inner && h -> inner -> type -> stuff_values) {
		status = ((*(h -> inner -> type -> stuff_values))
			  (c, id, h -> inner));
		if (status == ISC_R_SUCCESS)
			return status;
	}

	return ISC_R_SUCCESS;
}

isc_result_t dhcp_subclass_lookup (omapi_object_t **lp,
				   omapi_object_t *id, omapi_object_t *ref)
{
	omapi_value_t *tv = (omapi_value_t *)0;
	isc_result_t status;
	struct subclass *subclass;

	/* Can't look up subclasss yet. */

	/* If we get to here without finding a subclass, no valid key was
	   specified. */
	if (!*lp)
		return ISC_R_NOKEYS;
	return ISC_R_SUCCESS;
}

isc_result_t dhcp_subclass_create (omapi_object_t **lp,
				   omapi_object_t *id)
{
	return ISC_R_NOTIMPLEMENTED;
}

isc_result_t dhcp_subclass_remove (omapi_object_t *lp,
				   omapi_object_t *id)
{
	return ISC_R_NOTIMPLEMENTED;
}

isc_result_t binding_scope_set_value (struct binding_scope *scope, int createp,
				      omapi_data_string_t *name,
				      omapi_typed_data_t *value)
{
	struct binding *bp;
	char *nname;
	struct binding_value *nv;
	nname = dmalloc (name -> len + 1, MDL);
	if (!nname)
		return ISC_R_NOMEMORY;
	memcpy (nname, name -> value, name -> len);
	nname [name -> len] = 0;
	bp = find_binding (scope, nname);
	if (!bp && !createp) {
		dfree (nname, MDL);
		return ISC_R_UNKNOWNATTRIBUTE;
	} 
	if (!value) {
		dfree (nname, MDL);
		if (!bp)
			return ISC_R_UNKNOWNATTRIBUTE;
		binding_value_dereference (&bp -> value, MDL);
		return ISC_R_SUCCESS;
	}

	nv = (struct binding_value *)0;
	if (!binding_value_allocate (&nv, MDL)) {
		dfree (nname, MDL);
		return ISC_R_NOMEMORY;
	}
	switch (value -> type) {
	      case omapi_datatype_int:
		nv -> type = binding_numeric;
		nv -> value.intval = value -> u.integer;
		break;

	      case omapi_datatype_string:
	      case omapi_datatype_data:
		if (!buffer_allocate (&nv -> value.data.buffer,
				      value -> u.buffer.len, MDL)) {
			binding_value_dereference (&nv, MDL);
			dfree (nname, MDL);
			return ISC_R_NOMEMORY;
		}
		memcpy (&nv -> value.data.buffer -> data [1],
			value -> u.buffer.value, value -> u.buffer.len);
		nv -> value.data.len = value -> u.buffer.len;
		break;

	      case omapi_datatype_object:
		binding_value_dereference (&nv, MDL);
		dfree (nname, MDL);
		return ISC_R_INVALIDARG;
	}

	if (!bp) {
		bp = dmalloc (sizeof *bp, MDL);
		if (!bp) {
			binding_value_dereference (&nv, MDL);
			dfree (nname, MDL);
			return ISC_R_NOMEMORY;
		}
		memset (bp, 0, sizeof *bp);
		bp -> name = nname;
		nname = (char *)0;
		bp -> next = scope -> bindings;
		scope -> bindings = bp;
	} else {
		if (bp -> value)
			binding_value_dereference (&bp -> value, MDL);
		dfree (nname, MDL);
	}
	binding_value_reference (&bp -> value, nv, MDL);
	binding_value_dereference (&nv, MDL);
	return ISC_R_SUCCESS;
}

isc_result_t binding_scope_get_value (omapi_value_t **value,
				      struct binding_scope *scope,
				      omapi_data_string_t *name)
{
	struct binding *bp;
	omapi_typed_data_t *td;
	isc_result_t status;
	char *nname;
	nname = dmalloc (name -> len + 1, MDL);
	if (!nname)
		return ISC_R_NOMEMORY;
	memcpy (nname, name -> value, name -> len);
	nname [name -> len] = 0;
	bp = find_binding (scope, nname);
	dfree (nname, MDL);
	if (!bp)
		return ISC_R_UNKNOWNATTRIBUTE;
	if (!bp -> value)
		return ISC_R_UNKNOWNATTRIBUTE;

	switch (bp -> value -> type) {
	      case binding_boolean:
		td = (omapi_typed_data_t *)0;
		status = omapi_typed_data_new (MDL, &td, omapi_datatype_int,
					       bp -> value -> value.boolean);
		break;

	      case binding_numeric:
		td = (omapi_typed_data_t *)0;
		status = omapi_typed_data_new (MDL, &td, omapi_datatype_int,
					       (int)
					       bp -> value -> value.intval);
		break;

	      case binding_data:
		td = (omapi_typed_data_t *)0;
		status = omapi_typed_data_new (MDL, &td, omapi_datatype_data,
					       bp -> value -> value.data.len);
		if (status != ISC_R_SUCCESS)
			return status;
		memcpy (&td -> u.buffer.value [0],
			bp -> value -> value.data.data,
			bp -> value -> value.data.len);
		break;

		/* Can't return values for these two (yet?). */
	      case binding_dns:
	      case binding_function:
		return ISC_R_INVALIDARG;
	}

	if (status != ISC_R_SUCCESS)
		return status;
	status = omapi_value_new (value, MDL);
	if (status != ISC_R_SUCCESS) {
		omapi_typed_data_dereference (&td, MDL);
		return status;
	}
	
	omapi_data_string_reference (&(*value) -> name, name, MDL);
	omapi_typed_data_reference (&(*value) -> value, td, MDL);
	omapi_typed_data_dereference (&td, MDL);

	return ISC_R_SUCCESS;
}

isc_result_t binding_scope_stuff_values (omapi_object_t *c,
					 struct binding_scope *scope)
{
	struct binding *bp;
	unsigned len;
	isc_result_t status;

	for (bp = scope -> bindings; bp; bp = bp -> next) {
	    if (bp -> value) {
		if (bp -> value -> type == binding_dns ||
		    bp -> value -> type == binding_function)
			continue;

		/* Stuff the name. */
		len = strlen (bp -> name);
		status = omapi_connection_put_uint16 (c, len);
		if (status != ISC_R_SUCCESS)
		    return status;
		status = omapi_connection_copyin (c,
						  (unsigned char *)bp -> name,
						  len);
		if (status != ISC_R_SUCCESS)
			return status;

		switch (bp -> value -> type) {
		  case binding_boolean:
		    status = omapi_connection_put_uint32 (c,
							  sizeof (u_int32_t));
		    if (status != ISC_R_SUCCESS)
			return status;
		    status = (omapi_connection_put_uint32
			      (c,
			       ((u_int32_t)(bp -> value -> value.boolean))));
		    break;

		  case binding_data:
		    status = (omapi_connection_put_uint32
			      (c, bp -> value -> value.data.len));
		    if (status != ISC_R_SUCCESS)
			return status;
		    if (bp -> value -> value.data.len) {
			status = (omapi_connection_copyin
				  (c, bp -> value -> value.data.data,
				   bp -> value -> value.data.len));
			if (status != ISC_R_SUCCESS)
			    return status;
		    }
		    break;

		  case binding_numeric:
		    status = (omapi_connection_put_uint32
			      (c, sizeof (u_int32_t)));
		    if (status != ISC_R_SUCCESS)
			    return status;
		    status = (omapi_connection_put_uint32
			      (c, ((u_int32_t)
				   (bp -> value -> value.intval))));
		    break;


		    /* NOTREACHED */
		  case binding_dns:
		  case binding_function:
		    break;
		}
	    }
	}
	return ISC_R_SUCCESS;
}

/* vim: set tabstop=8: */
