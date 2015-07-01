/* db.c

   Persistent database management routines for DHCPD... */

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
"$Id: db.c,v 1.63.2.4 2001/06/22 23:58:08 mellon Exp $ Copyright (c) 1995-2001 The Internet Software Consortium.  All rights reserved.\n";
#endif /* not lint */

#include "dhcpd.h"
#include <ctype.h>
#include "version.h"

FILE *db_file;

static int counting = 0;
static int count = 0;
TIME write_time;
int lease_file_is_corrupt = 0;

/* Write the specified lease to the current lease database file. */

int write_lease (lease)
	struct lease *lease;
{
	struct tm *t;
	char tbuf [64];
	int errors = 0;
	int i;
	struct binding *b;
	char *s;

	/* If the lease file is corrupt, don't try to write any more leases
	   until we've written a good lease file. */
	if (lease_file_is_corrupt)
		if (!new_lease_file ())
			return 0;

	if (counting)
		++count;
	errno = 0;
	fprintf (db_file, "lease %s {", piaddr (lease -> ip_addr));
	if (errno) {
		++errors;
	}

	/* Note: the following is not a Y2K bug - it's a Y1.9K bug.   Until
	   somebody invents a time machine, I think we can safely disregard
	   it. */
	if (lease -> starts) {
		if (lease -> starts != MAX_TIME) {
			t = gmtime (&lease -> starts);
			sprintf (tbuf, "%d %d/%02d/%02d %02d:%02d:%02d;",
				 t -> tm_wday, t -> tm_year + 1900,
				 t -> tm_mon + 1, t -> tm_mday,
				 t -> tm_hour, t -> tm_min, t -> tm_sec);
		} else
			strcpy (tbuf, "never;");
		errno = 0;
		fprintf (db_file, "\n  starts %s", tbuf);
		if (errno) {
			++errors;
		}
	}

	if (lease -> ends) {
		if (lease -> ends != MAX_TIME) {
			t = gmtime (&lease -> ends);
			sprintf (tbuf, "%d %d/%02d/%02d %02d:%02d:%02d;",
				 t -> tm_wday, t -> tm_year + 1900,
				 t -> tm_mon + 1, t -> tm_mday,
				 t -> tm_hour, t -> tm_min, t -> tm_sec);
		} else
			strcpy (tbuf, "never;");
		errno = 0;
		fprintf (db_file, "\n  ends %s", tbuf);
		if (errno) {
			++errors;
		}
	}

	if (lease -> tstp) {
		t = gmtime (&lease -> tstp);
		errno = 0;
		fprintf (db_file, "\n  tstp %d %d/%02d/%02d %02d:%02d:%02d;",
			 t -> tm_wday, t -> tm_year + 1900,
			 t -> tm_mon + 1, t -> tm_mday,
			 t -> tm_hour, t -> tm_min, t -> tm_sec);
		if (errno) {
			++errors;
		}
	}
	if (lease -> tsfp) {
		t = gmtime (&lease -> tsfp);
		errno = 0;
		fprintf (db_file, "\n  tsfp %d %d/%02d/%02d %02d:%02d:%02d;",
			 t -> tm_wday, t -> tm_year + 1900,
			 t -> tm_mon + 1, t -> tm_mday,
			 t -> tm_hour, t -> tm_min, t -> tm_sec);
		if (errno) {
			++errors;
		}
	}
	if (lease -> cltt) {
		t = gmtime (&lease -> cltt);
		errno = 0;
		fprintf (db_file, "\n  cltt %d %d/%02d/%02d %02d:%02d:%02d;",
			 t -> tm_wday, t -> tm_year + 1900,
			 t -> tm_mon + 1, t -> tm_mday,
			 t -> tm_hour, t -> tm_min, t -> tm_sec);
		if (errno) {
			++errors;
		}
	}

	fprintf (db_file, "\n  binding state %s;",
		 ((lease -> binding_state > 0 &&
		   lease -> binding_state <= FTS_BOOTP)
		  ? binding_state_names [lease -> binding_state - 1]
		  : "abandoned"));

	if (lease -> binding_state != lease -> next_binding_state)
		fprintf (db_file, "\n  next binding state %s;",
			 ((lease -> next_binding_state > 0 &&
			   lease -> next_binding_state <= FTS_BOOTP)
			  ? (binding_state_names
			     [lease -> next_binding_state - 1])
		  : "abandoned"));

	/* If this lease is billed to a class and is still valid,
	   write it out. */
	if (lease -> billing_class && lease -> ends > cur_time)
		if (!write_billing_class (lease -> billing_class))
			++errors;

	if (lease -> hardware_addr.hlen) {
		errno = 0;
		fprintf (db_file, "\n  hardware %s %s;",
			 hardware_types [lease -> hardware_addr.hbuf [0]],
			 print_hw_addr (lease -> hardware_addr.hbuf [0],
					lease -> hardware_addr.hlen - 1,
					&lease -> hardware_addr.hbuf [1]));
		if (errno) {
			++errors;
		}
	}
	if (lease -> uid_len) {
		int i;
		s = quotify_buf (lease -> uid, lease -> uid_len, MDL);
		if (s) {
			fprintf (db_file, "\n  uid \"%s\";", s);
			if (errno)
				++errors;
			dfree (s, MDL);
		} else
			++errors;
	}
	if (lease -> scope) {
	    for (b = lease -> scope -> bindings; b; b = b -> next) {
		if (!b -> value)
			continue;
		if (b -> value -> type == binding_data) {
		    if (b -> value -> value.data.data) {
			s = quotify_buf (b -> value -> value.data.data,
					 b -> value -> value.data.len, MDL);
			if (s) {
			    errno = 0;
			    fprintf (db_file, "\n  set %s = \"%s\";",
				     b -> name, s);
			    if (errno)
				++errors;
			    dfree (s, MDL);
			} else
			    ++errors;
		    }
		} else if (b -> value -> type == binding_numeric) {
		    errno = 0;
		    fprintf (db_file, "\n  set %s = %%%ld;",
			     b -> name, b -> value -> value.intval);
		    if (errno)
			++errors;
		} else if (b -> value -> type == binding_boolean) {
		    errno = 0;
		    fprintf (db_file, "\n  set %s = %s;",
			     b -> name,
			     b -> value -> value.intval ? "true" : "false");
		    if (errno)
			    ++errors;
		} else if (b -> value -> type == binding_dns) {
			log_error ("%s: persistent dns values not supported.",
				   b -> name);
		} else if (b -> value -> type == binding_function) {
			log_error ("%s: persistent functions not supported.",
				   b -> name);
		} else {
			log_error ("%s: unknown binding type %d",
				   b -> name, b -> value -> type);
		}
	    }
	}
	if (lease -> agent_options) {
	    struct option_cache *oc;
	    struct data_string ds;
	    pair p;

	    memset (&ds, 0, sizeof ds);
	    if (lease -> agent_options) {
		for (p = lease -> agent_options -> first; p; p = p -> cdr) {
		    oc = (struct option_cache *)p -> car;
		    if (oc -> data.len) {
			errno = 0;
			fprintf (db_file, "\n  option agent.%s %s;",
				 oc -> option -> name,
				 pretty_print_option (oc -> option,
						      oc -> data.data,
						      oc -> data.len,
						      1, 1));
			if (errno)
			    ++errors;
		    }
		}
	    }
	}
	if (lease -> client_hostname &&
	    db_printable (lease -> client_hostname)) {
		s = quotify_string (lease -> client_hostname, MDL);
		if (s) {
			errno = 0;
			fprintf (db_file, "\n  client-hostname \"%s\";", s);
			if (errno)
				++errors;
			dfree (s, MDL);
		} else
			++errors;
	}
	if (lease -> on_expiry) {
		errno = 0;
		fprintf (db_file, "\n  on expiry%s {",
			 lease -> on_expiry == lease -> on_release
			 ? " or release" : "");
		if (errno)
			++errors;
		write_statements (db_file, lease -> on_expiry, 4);
		/* XXX */
		fprintf (db_file, "\n  }");
	}
	if (lease -> on_release && lease -> on_release != lease -> on_expiry) {
		errno = 0;
		fprintf (db_file, "\n  on release {");
		if (errno)
			++errors;
		write_statements (db_file, lease -> on_release, 4);
		/* XXX */
		fprintf (db_file, "\n  }");
	}
	errno = 0;
	fputs ("\n}\n", db_file);
	if (errno) {
		++errors;
	}
	if (errors)
		log_info ("write_lease: unable to write lease %s",
		      piaddr (lease -> ip_addr));
	if (errors)
		lease_file_is_corrupt = 1;
	return !errors;
}

int write_host (host)
	struct host_decl *host;
{
	int errors = 0;
	int i;
	struct data_string ip_addrs;

	/* If the lease file is corrupt, don't try to write any more leases
	   until we've written a good lease file. */
	if (lease_file_is_corrupt)
		if (!new_lease_file ())
			return 0;

	if (!db_printable (host -> name))
		return 0;

	if (counting)
		++count;
	errno = 0;

	fprintf (db_file, "host %s {", host -> name);
	if (errno) {
		++errors;
	}

	if (host -> flags & HOST_DECL_DYNAMIC) {
		errno = 0;
		fprintf (db_file, "\n  dynamic;");
		if (errno)
			++errors;
	}

	if (host -> flags & HOST_DECL_DELETED) {
		errno = 0;
		fprintf (db_file, "\n  deleted;");
		if (errno)
			++errors;
	} else {
		if (host -> interface.hlen) {
			errno = 0;
			fprintf (db_file, "\n  hardware %s %s;",
				 hardware_types [host -> interface.hbuf [0]],
				 print_hw_addr (host -> interface.hbuf [0],
						host -> interface.hlen - 1,
						&host -> interface.hbuf [1]));
			if (errno) {
				++errors;
			}
		}
		if (host -> client_identifier.len) {
			int i;
			errno = 0;
			if (db_printable_len (host -> client_identifier.data,
					      host -> client_identifier.len)) {
				fprintf (db_file, "\n  uid \"%.*s\";",
					 (int)host -> client_identifier.len,
					 host -> client_identifier.data);
			} else {
				fprintf (db_file,
					 "\n  uid %2.2x",
					 host -> client_identifier.data [0]);
				if (errno) {
					++errors;
				}
				for (i = 1;
				     i < host -> client_identifier.len; i++) {
					errno = 0;
					fprintf (db_file, ":%2.2x",
						 host ->
						 client_identifier.data [i]);
					if (errno) {
						++errors;
					}
				}
				putc (';', db_file);
			}
		}
		
		memset (&ip_addrs, 0, sizeof ip_addrs);
		if (host -> fixed_addr &&
		    evaluate_option_cache (&ip_addrs, (struct packet *)0,
					   (struct lease *)0,
					   (struct client_state *)0,
					   (struct option_state *)0,
					   (struct option_state *)0,
					   &global_scope,
					   host -> fixed_addr, MDL)) {
		
			errno = 0;
			fprintf (db_file, "\n  fixed-address ");
			if (errno) {
				++errors;
			}
			for (i = 0; i < ip_addrs.len - 3; i += 4) {
				errno = 0;
				fprintf (db_file, "%d.%d.%d.%d%s",
					 ip_addrs.data [i],
					 ip_addrs.data [i + 1],
					 ip_addrs.data [i + 2],
					 ip_addrs.data [i + 3],
					 i + 7 < ip_addrs.len ? "," : "");
				if (errno) {
					++errors;
				}
			}
			errno = 0;
			fputc (';', db_file);
			if (errno) {
				++errors;
			}
		}

		if (host -> named_group) {
			errno = 0;
			fprintf (db_file, "\n  group \"%s\";",
				 host -> named_group -> name);
			if (errno) {
				++errors;
			}
		}

		if (host -> group &&
		    (!host -> named_group ||
		     host -> group != host -> named_group -> group) &&
		    host -> group != root_group) {
			errno = 0;
			write_statements (db_file,
					  host -> group -> statements, 8);
			if (errno) {
				++errors;
			}
		}
	}

	errno = 0;
	fputs ("\n}\n", db_file);
	if (errno) {
		++errors;
	}
	if (errors) {
		log_info ("write_host: unable to write host %s",
			  host -> name);
		lease_file_is_corrupt = 1;
	}
	return !errors;
}

int write_group (group)
	struct group_object *group;
{
	int errors = 0;
	int i;

	/* If the lease file is corrupt, don't try to write any more leases
	   until we've written a good lease file. */
	if (lease_file_is_corrupt)
		if (!new_lease_file ())
			return 0;

	if (!db_printable (group -> name))
		return 0;

	if (counting)
		++count;
	errno = 0;

	fprintf (db_file, "group %s {", group -> name);
	if (errno) {
		++errors;
	}

	if (group -> flags & GROUP_OBJECT_DYNAMIC) {
		errno = 0;
		fprintf (db_file, "\n  dynamic;");
		if (errno)
			++errors;
	}

	if (group -> flags & GROUP_OBJECT_STATIC) {
		errno = 0;
		fprintf (db_file, "\n  static;");
		if (errno)
			++errors;
	}

	if (group -> flags & GROUP_OBJECT_DELETED) {
		errno = 0;
		fprintf (db_file, "\n  deleted;");
		if (errno)
			++errors;
	} else {
		if (group -> group) {
			errno = 0;
			write_statements (db_file,
					  group -> group -> statements, 8);
			if (errno) {
				++errors;
			}
		}
	}

	errno = 0;
	fputs ("\n}\n", db_file);
	if (errno) {
		++errors;
	}
	if (errors) {
		log_info ("write_group: unable to write group %s",
			  group -> name);
		lease_file_is_corrupt = 1;
	}
	return !errors;
}

#if defined (FAILOVER_PROTOCOL)
int write_failover_state (dhcp_failover_state_t *state)
{
	struct tm *t;
	int errors = 0;

	if (lease_file_is_corrupt)
		if (!new_lease_file ())
			return 0;

	errno = 0;
	fprintf (db_file, "\nfailover peer \"%s\" state {", state -> name);
	if (errno)
		++errors;

	t = gmtime (&state -> me.stos);
	errno = 0;
	fprintf (db_file, "\n  my state %s at %d %d/%02d/%02d %02d:%02d:%02d;",
		 /* Never record our state as "startup"! */
		 (state -> me.state == startup
		  ? dhcp_failover_state_name_print (state -> saved_state)
		  : dhcp_failover_state_name_print (state -> me.state)),
		 t -> tm_wday, t -> tm_year + 1900,
		 t -> tm_mon + 1, t -> tm_mday,
		 t -> tm_hour, t -> tm_min, t -> tm_sec);
	if (errno)
		++errors;

	t = gmtime (&state -> partner.stos);
	errno = 0;
	fprintf (db_file,
		 "\n  partner state %s at %d %d/%02d/%02d %02d:%02d:%02d;",
		 dhcp_failover_state_name_print (state -> partner.state),
		 t -> tm_wday, t -> tm_year + 1900,
		 t -> tm_mon + 1, t -> tm_mday,
		 t -> tm_hour, t -> tm_min, t -> tm_sec);
	if (errno)
		++errors;

	if (state -> i_am == secondary) {
		errno = 0;
		fprintf (db_file, "\n  mclt %ld;",
			 (unsigned long)state -> mclt);
		if (errno)
			++errors;
	}
	fprintf (db_file, "\n}\n");
	if (errno)
		++errors;

	if (errors) {
		log_info ("write_failover_state: unable to write state %s",
			  state -> name);
		lease_file_is_corrupt = 1;
		return 0;
	}
	return 1;

}
#endif

int db_printable (s)
	const char *s;
{
	int i;
	for (i = 0; s [i]; i++)
		if (!isascii (s [i]) || !isprint (s [i])
		    || s [i] == '"' || s [i] == '\\')
			return 0;
	return 1;
}

int db_printable_len (s, len)
	const unsigned char *s;
	unsigned len;
{
	int i;
	for (i = 0; i < len; i++)
		if (!isascii (s [i]) || !isprint (s [i]) ||
		    s [i] == '"' || s [i] == '\\')
			return 0;
	return 1;
}

void write_named_billing_class (const char *name, unsigned len,
				struct class *class)
{
	/* XXX billing classes that are modified by OMAPI need
	   XXX to be detected and written out here. */
}

void write_billing_classes ()
{
	struct collection *lp;
	struct class *cp;
	struct hash_bucket *bp;
	int i;

	for (lp = collections; lp; lp = lp -> next) {
	    for (cp = lp -> classes; cp; cp = cp -> nic) {
		if (cp -> spawning && cp -> hash) {
		    class_hash_foreach (cp -> hash, write_named_billing_class);
		}
	    }
	}
}

/* Write a spawned class to the database file. */

int write_billing_class (class)
	struct class *class;
{
	int errors = 0;
	int i;

	if (lease_file_is_corrupt)
		if (!new_lease_file ())
			return 0;

	if (!class -> superclass) {
		errno = 0;
		fprintf (db_file, "\n  billing class \"%s\";", class -> name);
		return !errno;
	}

	errno = 0;
	fprintf (db_file, "\n  billing subclass \"%s\"",
		 class -> superclass -> name);
	if (errno)
		++errors;

	for (i = 0; i < class -> hash_string.len; i++)
		if (!isascii (class -> hash_string.data [i]) ||
		    !isprint (class -> hash_string.data [i]))
			break;
	if (i == class -> hash_string.len) {
		errno = 0;
		fprintf (db_file, " \"%.*s\";",
			 (int)class -> hash_string.len,
			 class -> hash_string.data);
		if (errno)
			++errors;
	} else {
		errno = 0;
		fprintf (db_file, " %2.2x", class -> hash_string.data [0]);
		if (errno)
			++errors;
		for (i = 1; i < class -> hash_string.len; i++) {
			errno = 0;
			fprintf (db_file, ":%2.2x",
				 class -> hash_string.data [i]);
			if (errno)
				++errors;
		}
		errno = 0;
		fprintf (db_file, ";");
		if (errno)
			++errors;
	}

	class -> dirty = !errors;
	if (errors)
		lease_file_is_corrupt = 1;
	return !errors;
}

/* Commit any leases that have been written out... */

int commit_leases ()
{
	/* Commit any outstanding writes to the lease database file.
	   We need to do this even if we're rewriting the file below,
	   just in case the rewrite fails. */
	if (fflush (db_file) == EOF) {
		log_info ("commit_leases: unable to commit: %m");
		return 0;
	}
	if (fsync (fileno (db_file)) < 0) {
		log_info ("commit_leases: unable to commit: %m");
		return 0;
	}

	/* If we haven't rewritten the lease database in over an
	   hour, rewrite it now.  (The length of time should probably
	   be configurable. */
	if (count && cur_time - write_time > 3600) {
		count = 0;
		write_time = cur_time;
		new_lease_file ();
	}
	return 1;
}

void db_startup (testp)
	int testp;
{
	isc_result_t status;

#if defined (TRACING)
	if (!trace_playback ()) {
#endif
		/* Read in the existing lease file... */
		status = read_conf_file (path_dhcpd_db,
					 (struct group *)0, 0, 1);
		/* XXX ignore status? */
#if defined (TRACING)
	}
#endif

#if defined (TRACING)
	/* If we're playing back, there is no lease file, so we can't
	   append it, so we create one immediately (maybe this isn't
	   the best solution... */
	if (trace_playback ()) {
		new_lease_file ();
	}
#endif
	if (!testp) {
		db_file = fopen (path_dhcpd_db, "a");
		if (!db_file)
			log_fatal ("Can't open %s for append.", path_dhcpd_db);
		expire_all_pools ();
#if defined (TRACING)
		if (trace_playback ())
			write_time = cur_time;
		else
#endif
			GET_TIME (&write_time);
		new_lease_file ();
	}
}

int new_lease_file ()
{
	char newfname [512];
	char backfname [512];
	TIME t;
	int db_fd;

	/* If we already have an open database, close it. */
	if (db_file) {
		fclose (db_file);
		db_file = (FILE *)0;
	}

	/* Make a temporary lease file... */
	GET_TIME (&t);
	sprintf (newfname, "%s.%d", path_dhcpd_db, (int)t);
	db_fd = open (newfname, O_WRONLY | O_TRUNC | O_CREAT, 0664);
	if (db_fd < 0) {
		log_error ("Can't create new lease file: %m");
		return 0;
	}
	if ((db_file = fdopen (db_fd, "w")) == NULL) {
		log_error ("Can't fdopen new lease file!");
		goto fail;
	}

	/* Write an introduction so people don't complain about time
	   being off. */
	errno = 0;
	fprintf (db_file, "# All times in this file are in UTC (GMT), not %s",
		 "your local timezone.   This is\n");
	if (errno != 0)
		goto fail;
	fprintf (db_file, "# not a bug, so please don't ask about it.   %s",
		 "There is no portable way to\n");
	if (errno != 0)
		goto fail;
	fprintf (db_file, "# store leases in the local timezone, so please %s",
		 "don't request this as a\n");
	if (errno != 0)
		goto fail;
	fprintf (db_file, "# feature.   If this is inconvenient or %s",
		 "confusing to you, we sincerely\n");
	if (errno != 0)
		goto fail;
	fprintf (db_file, "# apologize.   Seriously, though - don't ask.\n");
	if (errno != 0)
		goto fail;
	fprintf (db_file, "# The format of this file is documented in the %s",
		 "dhcpd.leases(5) manual page.\n");
	if (errno != 0)
		goto fail;
	fprintf (db_file, "# This lease file was written by isc-dhcp-%s\n\n",
		 DHCP_VERSION);
	if (errno != 0)
		goto fail;

	/* Write out all the leases that we know of... */
	counting = 0;
	if (!write_leases ())
		goto fail;

#if defined (TRACING)
	if (!trace_playback ()) {
#endif
	    /* Get the old database out of the way... */
	    sprintf (backfname, "%s~", path_dhcpd_db);
	    if (unlink (backfname) < 0 && errno != ENOENT) {
		log_error ("Can't remove old lease database backup %s: %m",
			   backfname);
		goto fail;
	    }
	    if (link (path_dhcpd_db, backfname) < 0) {
		log_error ("Can't backup lease database %s to %s: %m",
			   path_dhcpd_db, backfname);
		goto fail;
	    }
#if defined (TRACING)
	}
#endif
	
	/* Move in the new file... */
	if (rename (newfname, path_dhcpd_db) < 0) {
		log_error ("Can't install new lease database %s to %s: %m",
			   newfname, path_dhcpd_db);
		goto fail;
	}

	counting = 1;
	lease_file_is_corrupt = 0;
	return 1;

      fail:
	unlink (newfname);
	lease_file_is_corrupt = 1;
	return 0;
}

int group_writer (struct group_object *group)
{
	if (!write_group (group))
		return 0;
	if (!commit_leases ())
		return 0;
	return 1;
}
