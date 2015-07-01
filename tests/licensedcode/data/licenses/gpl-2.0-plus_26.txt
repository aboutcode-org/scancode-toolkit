/*
 *  Mini dpkg implementation for busybox.
 *  This is not meant as a replacemnt for dpkg
 *
 *  Written By Glenn McGrath with the help of others
 *  Copyright (C) 2001 by Glenn McGrath
 *
 *  Started life as a busybox implementation of udpkg
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU Library General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 */

/*
 * Known difference between busybox dpkg and the official dpkg that i dont
 * consider important, its worth keeping a note of differences anyway, just to
 * make it easier to maintain.
 *  - The first value for the Confflile: field isnt placed on a new line.
 *  - When installing a package the Status: field is placed at the end of the
 *      section, rather than just after the Package: field.
 *
 * Bugs that need to be fixed
 *  - (unknown, please let me know when you find any)
 *
 */

#include <fcntl.h>
#include <getopt.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "unarchive.h"
#include "busybox.h"

/* NOTE: If you vary HASH_PRIME sizes be aware,
 * 1) Tweaking these will have a big effect on how much memory this program uses.
 * 2) For computational efficiency these hash tables should be at least 20%
 *    larger than the maximum number of elements stored in it.
 * 3) All _HASH_PRIME's must be a prime number or chaos is assured, if your looking
 *    for a prime, try http://www.utm.edu/research/primes/lists/small/10000.txt
 * 4) If you go bigger than 15 bits you may get into trouble (untested) as its
 *    sometimes cast to an unsigned int, if you go to 16 bit you will overlap
 *    int's and chaos is assured, 16381 is the max prime for 14 bit field
 */

/* NAME_HASH_PRIME, Stores package names and versions,
 * I estimate it should be at least 50% bigger than PACKAGE_HASH_PRIME,
 * as there a lot of duplicate version numbers */
#define NAME_HASH_PRIME 16381
char *name_hashtable[NAME_HASH_PRIME + 1];

/* PACKAGE_HASH_PRIME, Maximum number of unique packages,
 * It must not be smaller than STATUS_HASH_PRIME,
 * Currently only packages from status_hashtable are stored in here, but in
 * future this may be used to store packages not only from a status file,
 * but an available_hashtable, and even multiple packages files.
 * Package can be stored more than once if they have different versions.
 * e.g. The same package may have different versions in the status file
 *      and available file */
#define PACKAGE_HASH_PRIME 10007
typedef struct edge_s {
	unsigned int operator:3;
	unsigned int type:4;
	unsigned int name:14;
	unsigned int version:14;
} edge_t;

typedef struct common_node_s {
	unsigned int name:14;
	unsigned int version:14;
	unsigned int num_of_edges:14;
	edge_t **edge;
} common_node_t;
common_node_t *package_hashtable[PACKAGE_HASH_PRIME + 1];

/* Currently it doesnt store packages that have state-status of not-installed
 * So it only really has to be the size of the maximum number of packages
 * likely to be installed at any one time, so there is a bit of leaway here */
#define STATUS_HASH_PRIME 8191
typedef struct status_node_s {
	unsigned int package:14;	/* has to fit PACKAGE_HASH_PRIME */
	unsigned int status:14;		/* has to fit STATUS_HASH_PRIME */
} status_node_t;
status_node_t *status_hashtable[STATUS_HASH_PRIME + 1];

/* Even numbers are for 'extras', like ored dependecies or null */
enum edge_type_e {
	EDGE_NULL = 0,
	EDGE_PRE_DEPENDS = 1,
	EDGE_OR_PRE_DEPENDS = 2,
	EDGE_DEPENDS = 3,
	EDGE_OR_DEPENDS = 4,
	EDGE_REPLACES = 5,
	EDGE_PROVIDES = 7,
	EDGE_CONFLICTS = 9,
	EDGE_SUGGESTS = 11,
	EDGE_RECOMMENDS = 13,
	EDGE_ENHANCES = 15
};
enum operator_e {
	VER_NULL = 0,
	VER_EQUAL = 1,
	VER_LESS = 2,
	VER_LESS_EQUAL = 3,
	VER_MORE = 4,
	VER_MORE_EQUAL = 5,
	VER_ANY = 6
};

enum dpkg_opt_e {
	dpkg_opt_purge = 1,
	dpkg_opt_remove = 2,
	dpkg_opt_unpack = 4,
	dpkg_opt_configure = 8,
	dpkg_opt_install = 16,
	dpkg_opt_package_name = 32,
	dpkg_opt_filename = 64,
	dpkg_opt_list_installed = 128,
	dpkg_opt_force_ignore_depends = 256
};

typedef struct deb_file_s {
	char *control_file;
	char *filename;
	unsigned int package:14;
} deb_file_t;


void make_hash(const char *key, unsigned int *start, unsigned int *decrement, const int hash_prime)
{
	unsigned long int hash_num = key[0];
	int len = strlen(key);
	int i;

	/* Maybe i should have uses a "proper" hashing algorithm here instead
	 * of making one up myself, seems to be working ok though. */
	for(i = 1; i < len; i++) {
		/* shifts the ascii based value and adds it to previous value
		 * shift amount is mod 24 because long int is 32 bit and data
		 * to be shifted is 8, dont want to shift data to where it has
		 * no effect*/
		hash_num += ((key[i] + key[i-1]) << ((key[i] * i) % 24));
	}
	*start = (unsigned int) hash_num % hash_prime;
	*decrement = (unsigned int) 1 + (hash_num % (hash_prime - 1));
}

/* this adds the key to the hash table */
int search_name_hashtable(const char *key)
{
	unsigned int probe_address = 0;
	unsigned int probe_decrement = 0;
//	char *temp;

	make_hash(key, &probe_address, &probe_decrement, NAME_HASH_PRIME);
	while(name_hashtable[probe_address] != NULL) {
		if (strcmp(name_hashtable[probe_address], key) == 0) {
			return(probe_address);
		} else {
			probe_address -= probe_decrement;
			if ((int)probe_address < 0) {
				probe_address += NAME_HASH_PRIME;
			}
		}
	}
	name_hashtable[probe_address] = bb_xstrdup(key);
	return(probe_address);
}

/* this DOESNT add the key to the hashtable
 * TODO make it consistent with search_name_hashtable
 */
unsigned int search_status_hashtable(const char *key)
{
	unsigned int probe_address = 0;
	unsigned int probe_decrement = 0;

	make_hash(key, &probe_address, &probe_decrement, STATUS_HASH_PRIME);
	while(status_hashtable[probe_address] != NULL) {
		if (strcmp(key, name_hashtable[package_hashtable[status_hashtable[probe_address]->package]->name]) == 0) {
			break;
		} else {
			probe_address -= probe_decrement;
			if ((int)probe_address < 0) {
				probe_address += STATUS_HASH_PRIME;
			}
		}
	}
	return(probe_address);
}

/* Need to rethink version comparison, maybe the official dpkg has something i can use ? */
int version_compare_part(const char *version1, const char *version2)
{
	int upstream_len1 = 0;
	int upstream_len2 = 0;
	char *name1_char;
	char *name2_char;
	int len1 = 0;
	int len2 = 0;
	int tmp_int;
	int ver_num1;
	int ver_num2;
	int ret;

	if (version1 == NULL) {
		version1 = bb_xstrdup("");
	}
	if (version2 == NULL) {
		version2 = bb_xstrdup("");
	}
	upstream_len1 = strlen(version1);
	upstream_len2 = strlen(version2);

	while ((len1 < upstream_len1) || (len2 < upstream_len2)) {
		/* Compare non-digit section */
		tmp_int = strcspn(&version1[len1], "0123456789");
		name1_char = bb_xstrndup(&version1[len1], tmp_int);
		len1 += tmp_int;
		tmp_int = strcspn(&version2[len2], "0123456789");
		name2_char = bb_xstrndup(&version2[len2], tmp_int);
		len2 += tmp_int;
		tmp_int = strcmp(name1_char, name2_char);
		free(name1_char);
		free(name2_char);
		if (tmp_int != 0) {
			ret = tmp_int;
			goto cleanup_version_compare_part;
		}

		/* Compare digits */
		tmp_int = strspn(&version1[len1], "0123456789");
		name1_char = bb_xstrndup(&version1[len1], tmp_int);
		len1 += tmp_int;
		tmp_int = strspn(&version2[len2], "0123456789");
		name2_char = bb_xstrndup(&version2[len2], tmp_int);
		len2 += tmp_int;
		ver_num1 = atoi(name1_char);
		ver_num2 = atoi(name2_char);
		free(name1_char);
		free(name2_char);
		if (ver_num1 < ver_num2) {
			ret = -1;
			goto cleanup_version_compare_part;
		}
		else if (ver_num1 > ver_num2) {
			ret = 1;
			goto cleanup_version_compare_part;
		}
	}
	ret = 0;
cleanup_version_compare_part:
	return(ret);
}

/* if ver1 < ver2 return -1,
 * if ver1 = ver2 return 0,
 * if ver1 > ver2 return 1,
 */
int version_compare(const unsigned int ver1, const unsigned int ver2)
{
	char *ch_ver1 = name_hashtable[ver1];
	char *ch_ver2 = name_hashtable[ver2];

	char epoch1, epoch2;
	char *deb_ver1, *deb_ver2;
	char *ver1_ptr, *ver2_ptr;
	char *upstream_ver1;
	char *upstream_ver2;
	int result;

	/* Compare epoch */
	if (ch_ver1[1] == ':') {
		epoch1 = ch_ver1[0];
		ver1_ptr = strchr(ch_ver1, ':') + 1;
	} else {
		epoch1 = '0';
		ver1_ptr = ch_ver1;
	}
	if (ch_ver2[1] == ':') {
		epoch2 = ch_ver2[0];
		ver2_ptr = strchr(ch_ver2, ':') + 1;
	} else {
		epoch2 = '0';
		ver2_ptr = ch_ver2;
	}
	if (epoch1 < epoch2) {
		return(-1);
	}
	else if (epoch1 > epoch2) {
		return(1);
	}

	/* Compare upstream version */
	upstream_ver1 = bb_xstrdup(ver1_ptr);
	upstream_ver2 = bb_xstrdup(ver2_ptr);

	/* Chop off debian version, and store for later use */
	deb_ver1 = strrchr(upstream_ver1, '-');
	deb_ver2 = strrchr(upstream_ver2, '-');
	if (deb_ver1) {
		deb_ver1[0] = '\0';
		deb_ver1++;
	}
	if (deb_ver2) {
		deb_ver2[0] = '\0';
		deb_ver2++;
	}
	result = version_compare_part(upstream_ver1, upstream_ver2);

	free(upstream_ver1);
	free(upstream_ver2);

	if (result != 0) {
		return(result);
	}

	/* Compare debian versions */
	return(version_compare_part(deb_ver1, deb_ver2));
}

int test_version(const unsigned int version1, const unsigned int version2, const unsigned int operator)
{
	const int version_result = version_compare(version1, version2);
	switch(operator) {
		case (VER_ANY):
			return(TRUE);
		case (VER_EQUAL):
			if (version_result == 0) {
				return(TRUE);
			}
			break;
		case (VER_LESS):
			if (version_result < 0) {
				return(TRUE);
			}
			break;
		case (VER_LESS_EQUAL):
			if (version_result <= 0) {
				return(TRUE);
			}
			break;
		case (VER_MORE):
			if (version_result > 0) {
				return(TRUE);
			}
			break;
		case (VER_MORE_EQUAL):
			if (version_result >= 0) {
				return(TRUE);
			}
			break;
	}
	return(FALSE);
}


int search_package_hashtable(const unsigned int name, const unsigned int version, const unsigned int operator)
{
	unsigned int probe_address = 0;
	unsigned int probe_decrement = 0;

	make_hash(name_hashtable[name], &probe_address, &probe_decrement, PACKAGE_HASH_PRIME);
	while(package_hashtable[probe_address] != NULL) {
		if (package_hashtable[probe_address]->name == name) {
			if (operator == VER_ANY) {
				return(probe_address);
			}
			if (test_version(package_hashtable[probe_address]->version, version, operator)) {
				return(probe_address);
			}
		}
		probe_address -= probe_decrement;
		if ((int)probe_address < 0) {
			probe_address += PACKAGE_HASH_PRIME;
		}
	}
	return(probe_address);
}

/*
 * This function searches through the entire package_hashtable looking
 * for a package which provides "needle". It returns the index into
 * the package_hashtable for the provining package.
 *
 * needle is the index into name_hashtable of the package we are
 * looking for.
 *
 * start_at is the index in the package_hashtable to start looking
 * at. If start_at is -1 then start at the beginning. This is to allow
 * for repeated searches since more than one package might provide
 * needle.
 *
 * FIXME: I don't think this is very efficient, but I thought I'd keep
 * it simple for now until it proves to be a problem.
 */
int search_for_provides(int needle, int start_at) {
	int i, j;
	common_node_t *p;
	for (i = start_at + 1; i < PACKAGE_HASH_PRIME; i++) {
		p = package_hashtable[i];
		if ( p == NULL ) continue;
		for(j = 0; j < p->num_of_edges; j++)
			if ( p->edge[j]->type == EDGE_PROVIDES && p->edge[j]->name == needle )
				return i;
	}
	return -1;
}

/*
 * Add an edge to a node
 */
void add_edge_to_node(common_node_t *node, edge_t *edge)
{
	node->num_of_edges++;
	node->edge = xrealloc(node->edge, sizeof(edge_t) * (node->num_of_edges + 1));
	node->edge[node->num_of_edges - 1] = edge;
}

/*
 * Create one new node and one new edge for every dependency.
 *
 * Dependencies which contain multiple alternatives are represented as
 * an EDGE_OR_PRE_DEPENDS or EDGE_OR_DEPENDS node, followed by a
 * number of EDGE_PRE_DEPENDS or EDGE_DEPENDS nodes. The name field of
 * the OR edge contains the full dependency string while the version
 * field contains the number of EDGE nodes which follow as part of
 * this alternative.
 */
void add_split_dependencies(common_node_t *parent_node, const char *whole_line, unsigned int edge_type)
{
	char *line = bb_xstrdup(whole_line);
	char *line2;
	char *line_ptr1 = NULL;
	char *line_ptr2 = NULL;
	char *field;
	char *field2;
	char *version;
	edge_t *edge;
	edge_t *or_edge;
	int offset_ch;

	field = strtok_r(line, ",", &line_ptr1);
	do {
		/* skip leading spaces */
		field += strspn(field, " ");
		line2 = bb_xstrdup(field);
		field2 = strtok_r(line2, "|", &line_ptr2);
		if ( (edge_type == EDGE_DEPENDS || edge_type == EDGE_PRE_DEPENDS) &&
		     (strcmp(field, field2) != 0)) {
			or_edge = (edge_t *)xmalloc(sizeof(edge_t));
			or_edge->type = edge_type + 1;
		} else {
			or_edge = NULL;
		}

		if ( or_edge ) {
			or_edge->name = search_name_hashtable(field);
			or_edge->version = 0; // tracks the number of altenatives

			add_edge_to_node(parent_node, or_edge);
		}

		do {
			edge = (edge_t *) xmalloc(sizeof(edge_t));
			edge->type = edge_type;

			/* Skip any extra leading spaces */
			field2 += strspn(field2, " ");

			/* Get dependency version info */
			version = strchr(field2, '(');
			if (version == NULL) {
				edge->operator = VER_ANY;
				/* Get the versions hash number, adding it if the number isnt already in there */
				edge->version = search_name_hashtable("ANY");
			} else {
				/* Skip leading ' ' or '(' */
				version += strspn(field2, " ");
				version += strspn(version, "(");
				/* Calculate length of any operator charactors */
				offset_ch = strspn(version, "<=>");
				/* Determine operator */
				if (offset_ch > 0) {
					if (strncmp(version, "=", offset_ch) == 0) {
						edge->operator = VER_EQUAL;
					}
					else if (strncmp(version, "<<", offset_ch) == 0) {
						edge->operator = VER_LESS;
					}
					else if (strncmp(version, "<=", offset_ch) == 0) {
						edge->operator = VER_LESS_EQUAL;
					}
					else if (strncmp(version, ">>", offset_ch) == 0) {
						edge->operator = VER_MORE;
					}
					else if (strncmp(version, ">=", offset_ch) == 0) {
						edge->operator = VER_MORE_EQUAL;
					} else {
						bb_error_msg_and_die("Illegal operator\n");
					}
				}
				/* skip to start of version numbers */
				version += offset_ch;
				version += strspn(version, " ");

				/* Truncate version at trailing ' ' or ')' */
				version[strcspn(version, " )")] = '\0';
				/* Get the versions hash number, adding it if the number isnt already in there */
				edge->version = search_name_hashtable(version);
			}

			/* Get the dependency name */
			field2[strcspn(field2, " (")] = '\0';
			edge->name = search_name_hashtable(field2);

			if ( or_edge )
				or_edge->version++;

			add_edge_to_node(parent_node, edge);
		} while ((field2 = strtok_r(NULL, "|", &line_ptr2)) != NULL);
		free(line2);
	} while ((field = strtok_r(NULL, ",", &line_ptr1)) != NULL);
	free(line);

	return;
}

void free_package(common_node_t *node)
{
	unsigned short i;
	if (node) {
		for (i = 0; i < node->num_of_edges; i++) {
			free(node->edge[i]);
		}
		if ( node->edge )
			free(node->edge);
		free(node);
	}
}

unsigned int fill_package_struct(char *control_buffer)
{
	common_node_t *new_node = (common_node_t *) xcalloc(1, sizeof(common_node_t));
	const char *field_names[] = { "Package", "Version", "Pre-Depends", "Depends",
		"Replaces", "Provides", "Conflicts", "Suggests", "Recommends", "Enhances", 0};
	char *field_name;
	char *field_value;
	int field_start = 0;
	int num = -1;
	int buffer_length = strlen(control_buffer);

	new_node->version = search_name_hashtable("unknown");
	while (field_start < buffer_length) {
		unsigned short field_num;

		field_start += read_package_field(&control_buffer[field_start],
				&field_name, &field_value);

		if (field_name == NULL) {
			goto fill_package_struct_cleanup; /* Oh no, the dreaded goto statement ! */
		}

		field_num = compare_string_array(field_names, field_name);
		switch(field_num) {
			case 0: /* Package */
				new_node->name = search_name_hashtable(field_value);
				break;
			case 1: /* Version */
				new_node->version = search_name_hashtable(field_value);
				break;
			case 2: /* Pre-Depends */
				add_split_dependencies(new_node, field_value, EDGE_PRE_DEPENDS);
				break;
			case 3: /* Depends */
				add_split_dependencies(new_node, field_value, EDGE_DEPENDS);
				break;
			case 4: /* Replaces */
				add_split_dependencies(new_node, field_value, EDGE_REPLACES);
				break;
			case 5: /* Provides */
				add_split_dependencies(new_node, field_value, EDGE_PROVIDES);
				break;
			case 6: /* Conflicts */
				add_split_dependencies(new_node, field_value, EDGE_CONFLICTS);
				break;
			case 7: /* Suggests */
				add_split_dependencies(new_node, field_value, EDGE_SUGGESTS);
				break;
			case 8: /* Recommends */
				add_split_dependencies(new_node, field_value, EDGE_RECOMMENDS);
				break;
			case 9: /* Enhances */
				add_split_dependencies(new_node, field_value, EDGE_ENHANCES);
				break;
		}
fill_package_struct_cleanup:
		free(field_name);
		free(field_value);
	}

	if (new_node->version == search_name_hashtable("unknown")) {
		free_package(new_node);
		return(-1);
	}
	num = search_package_hashtable(new_node->name, new_node->version, VER_EQUAL);
	if (package_hashtable[num] == NULL) {
		package_hashtable[num] = new_node;
	} else {
		free_package(new_node);
	}
	return(num);
}

/* if num = 1, it returns the want status, 2 returns flag, 3 returns status */
unsigned int get_status(const unsigned int status_node, const int num)
{
	char *status_string = name_hashtable[status_hashtable[status_node]->status];
	char *state_sub_string;
	unsigned int state_sub_num;
	int len;
	int i;

	/* set tmp_string to point to the start of the word number */
	for (i = 1; i < num; i++) {
		/* skip past a word */
		status_string += strcspn(status_string, " ");
		/* skip past the seperating spaces */
		status_string += strspn(status_string, " ");
	}
	len = strcspn(status_string, " \n\0");
	state_sub_string = bb_xstrndup(status_string, len);
	state_sub_num = search_name_hashtable(state_sub_string);
	free(state_sub_string);
	return(state_sub_num);
}

void set_status(const unsigned int status_node_num, const char *new_value, const int position)
{
	const unsigned int new_value_len = strlen(new_value);
	const unsigned int new_value_num = search_name_hashtable(new_value);
	unsigned int want = get_status(status_node_num, 1);
	unsigned int flag = get_status(status_node_num, 2);
	unsigned int status = get_status(status_node_num, 3);
	int want_len = strlen(name_hashtable[want]);
	int flag_len = strlen(name_hashtable[flag]);
	int status_len = strlen(name_hashtable[status]);
	char *new_status;

	switch (position) {
		case (1):
			want = new_value_num;
			want_len = new_value_len;
			break;
		case (2):
			flag = new_value_num;
			flag_len = new_value_len;
			break;
		case (3):
			status = new_value_num;
			status_len = new_value_len;
			break;
		default:
			bb_error_msg_and_die("DEBUG ONLY: this shouldnt happen");
	}

	new_status = (char *) xmalloc(want_len + flag_len + status_len + 3);
	sprintf(new_status, "%s %s %s", name_hashtable[want], name_hashtable[flag], name_hashtable[status]);
	status_hashtable[status_node_num]->status = search_name_hashtable(new_status);
	free(new_status);
	return;
}

const char *describe_status(int status_num) {
	int status_want, status_state ;
	if ( status_hashtable[status_num] == NULL || status_hashtable[status_num]->status == 0 )
		return "is not installed or flagged to be installed\n";

	status_want = get_status(status_num, 1);
	status_state = get_status(status_num, 3);

	if ( status_state == search_name_hashtable("installed") ) {
		if ( status_want == search_name_hashtable("install") )
			return "is installed";
		if ( status_want == search_name_hashtable("deinstall") )
			return "is marked to be removed";
		if ( status_want == search_name_hashtable("purge") )
			return "is marked to be purged";
	}
	if ( status_want ==  search_name_hashtable("unknown") )
		return "is in an indeterminate state";
	if ( status_want == search_name_hashtable("install") )
		return "is marked to be installed";

	return "is not installed or flagged to be installed";
}


void index_status_file(const char *filename)
{
	FILE *status_file;
	char *control_buffer;
	char *status_line;
	status_node_t *status_node = NULL;
	unsigned int status_num;

	status_file = bb_xfopen(filename, "r");
	while ((control_buffer = fgets_str(status_file, "\n\n")) != NULL) {
		const unsigned int package_num = fill_package_struct(control_buffer);
		if (package_num != -1) {
			status_node = xmalloc(sizeof(status_node_t));
			/* fill_package_struct doesnt handle the status field */
			status_line = strstr(control_buffer, "Status:");
			if (status_line != NULL) {
				status_line += 7;
				status_line += strspn(status_line, " \n\t");
				status_line = bb_xstrndup(status_line, strcspn(status_line, "\n\0"));
				status_node->status = search_name_hashtable(status_line);
				free(status_line);
			}
			status_node->package = package_num;
			status_num = search_status_hashtable(name_hashtable[package_hashtable[status_node->package]->name]);
			status_hashtable[status_num] = status_node;
		}
		free(control_buffer);
	}
	fclose(status_file);
	return;
}

#if 0 /* this code is no longer used */
char *get_depends_field(common_node_t *package, const int depends_type)
{
	char *depends = NULL;
	char *old_sep = (char *)xcalloc(1, 3);
	char *new_sep = (char *)xcalloc(1, 3);
	int line_size = 0;
	int depends_size;

	int i;

	for (i = 0; i < package->num_of_edges; i++) {
		if ((package->edge[i]->type == EDGE_OR_PRE_DEPENDS) ||
			(package->edge[i]->type == EDGE_OR_DEPENDS)) {
		}

		if ((package->edge[i]->type == depends_type) ||
			(package->edge[i]->type == depends_type + 1)) {
			/* Check if its the first time through */

			depends_size = 8 + strlen(name_hashtable[package->edge[i]->name])
				+ strlen(name_hashtable[package->edge[i]->version]);
			line_size += depends_size;
			depends = (char *) xrealloc(depends, line_size + 1);

			/* Check to see if this dependency is the type we are looking for
			 * +1 to check for 'extra' types, e.g. ored dependecies */
			strcpy(old_sep, new_sep);
			if (package->edge[i]->type == depends_type) {
				strcpy(new_sep, ", ");
			}
			else if (package->edge[i]->type == depends_type + 1) {
				strcpy(new_sep, "| ");
			}

			if (depends_size == line_size) {
				strcpy(depends, "");
			} else {
				if ((strcmp(old_sep, "| ") == 0) && (strcmp(new_sep, "| ") == 0)) {
					strcat(depends, " | ");
				} else {
					strcat(depends, ", ");
				}
			}

			strcat(depends, name_hashtable[package->edge[i]->name]);
			if (strcmp(name_hashtable[package->edge[i]->version], "NULL") != 0) {
				if (package->edge[i]->operator == VER_EQUAL) {
					strcat(depends, " (= ");
				}
				else if (package->edge[i]->operator == VER_LESS) {
					strcat(depends, " (<< ");
				}
				else if (package->edge[i]->operator == VER_LESS_EQUAL) {
					strcat(depends, " (<= ");
				}
				else if (package->edge[i]->operator == VER_MORE) {
					strcat(depends, " (>> ");
				}
				else if (package->edge[i]->operator == VER_MORE_EQUAL) {
					strcat(depends, " (>= ");
				} else {
					strcat(depends, " (");
				}
				strcat(depends, name_hashtable[package->edge[i]->version]);
				strcat(depends, ")");
			}
		}
	}
	return(depends);
}
#endif

void write_buffer_no_status(FILE *new_status_file, const char *control_buffer)
{
	char *name;
	char *value;
	int start = 0;
	while (1) {
		start += read_package_field(&control_buffer[start], &name, &value);
		if (name == NULL) {
			break;
		}
		if (strcmp(name, "Status") != 0) {
			fprintf(new_status_file, "%s: %s\n", name, value);
		}
	}
	return;
}

/* This could do with a cleanup */
void write_status_file(deb_file_t **deb_file)
{
	FILE *old_status_file = bb_xfopen("/var/lib/dpkg/status", "r");
	FILE *new_status_file = bb_xfopen("/var/lib/dpkg/status.udeb", "w");
	char *package_name;
	char *status_from_file;
	char *control_buffer = NULL;
	char *tmp_string;
	int status_num;
	int field_start = 0;
	int write_flag;
	int i = 0;

	/* Update previously known packages */
	while ((control_buffer = fgets_str(old_status_file, "\n\n")) != NULL) {
		if ((tmp_string = strstr(control_buffer, "Package:")) == NULL) {
			continue;
		}

		tmp_string += 8;
 		tmp_string += strspn(tmp_string, " \n\t");
		package_name = bb_xstrndup(tmp_string, strcspn(tmp_string, "\n\0"));
		write_flag = FALSE;
		tmp_string = strstr(control_buffer, "Status:");
		if (tmp_string != NULL) {
			/* Seperate the status value from the control buffer */
			tmp_string += 7;
			tmp_string += strspn(tmp_string, " \n\t");
			status_from_file = bb_xstrndup(tmp_string, strcspn(tmp_string, "\n"));
		} else {
			status_from_file = NULL;
		}

		/* Find this package in the status hashtable */
		status_num = search_status_hashtable(package_name);
		if (status_hashtable[status_num] != NULL) {
			const char *status_from_hashtable = name_hashtable[status_hashtable[status_num]->status];
			if (strcmp(status_from_file, status_from_hashtable) != 0) {
				/* New status isnt exactly the same as old status */
				const int state_status = get_status(status_num, 3);
				if ((strcmp("installed", name_hashtable[state_status]) == 0) ||
					(strcmp("unpacked", name_hashtable[state_status]) == 0)) {
					/* We need to add the control file from the package */
					i = 0;
					while(deb_file[i] != NULL) {
						if (strcmp(package_name, name_hashtable[package_hashtable[deb_file[i]->package]->name]) == 0) {
							/* Write a status file entry with a modified status */
							/* remove trailing \n's */
							write_buffer_no_status(new_status_file, deb_file[i]->control_file);
							set_status(status_num, "ok", 2);
							fprintf(new_status_file, "Status: %s\n\n", name_hashtable[status_hashtable[status_num]->status]);
							write_flag = TRUE;
							break;
						}
						i++;
					}
					/* This is temperary, debugging only */
					if (deb_file[i] == NULL) {
						bb_error_msg_and_die("ALERT: Couldnt find a control file, your status file may be broken, status may be incorrect for %s", package_name);
					}
				}
				else if (strcmp("not-installed", name_hashtable[state_status]) == 0) {
					/* Only write the Package, Status, Priority and Section lines */
					fprintf(new_status_file, "Package: %s\n", package_name);
					fprintf(new_status_file, "Status: %s\n", status_from_hashtable);

					while (1) {
						char *field_name;
						char *field_value;
						field_start += read_package_field(&control_buffer[field_start], &field_name, &field_value);
						if (field_name == NULL) {
							break;
						}
						if ((strcmp(field_name, "Priority") == 0) ||
							(strcmp(field_name, "Section") == 0)) {
							fprintf(new_status_file, "%s: %s\n", field_name, field_value);
						}
					}
					write_flag = TRUE;
					fputs("\n", new_status_file);
				}
				else if	(strcmp("config-files", name_hashtable[state_status]) == 0) {
					/* only change the status line */
					while (1) {
						char *field_name;
						char *field_value;
						field_start += read_package_field(&control_buffer[field_start], &field_name, &field_value);
						if (field_name == NULL) {
							break;
						}
						/* Setup start point for next field */
						if (strcmp(field_name, "Status") == 0) {
							fprintf(new_status_file, "Status: %s\n", status_from_hashtable);
						} else {
							fprintf(new_status_file, "%s: %s\n", field_name, field_value);
						}
					}
					write_flag = TRUE;
					fputs("\n", new_status_file);
				}
			}
		}
		/* If the package from the status file wasnt handle above, do it now*/
		if (! write_flag) {
			fprintf(new_status_file, "%s\n\n", control_buffer);
		}

		free(status_from_file);
		free(package_name);
		free(control_buffer);
	}

	/* Write any new packages */
	for(i = 0; deb_file[i] != NULL; i++) {
		status_num = search_status_hashtable(name_hashtable[package_hashtable[deb_file[i]->package]->name]);
		if (strcmp("reinstreq", name_hashtable[get_status(status_num, 2)]) == 0) {
			write_buffer_no_status(new_status_file, deb_file[i]->control_file);
			set_status(status_num, "ok", 2);
			fprintf(new_status_file, "Status: %s\n\n", name_hashtable[status_hashtable[status_num]->status]);
		}
	}
	fclose(old_status_file);
	fclose(new_status_file);


	/* Create a seperate backfile to dpkg */
	if (rename("/var/lib/dpkg/status", "/var/lib/dpkg/status.udeb.bak") == -1) {
		struct stat stat_buf;
		if (stat("/var/lib/dpkg/status", &stat_buf) == 0) {
			bb_error_msg_and_die("Couldnt create backup status file");
		}
		/* Its ok if renaming the status file fails becasue status
		 * file doesnt exist, maybe we are starting from scratch */
		bb_error_msg("No status file found, creating new one");
	}

	if (rename("/var/lib/dpkg/status.udeb", "/var/lib/dpkg/status") == -1) {
		bb_error_msg_and_die("DANGER: Couldnt create status file, you need to manually repair your status file");
	}
}

/* This function returns TRUE if the given package can statisfy a
 * dependency of type depend_type.
 *
 * A pre-depends is statisfied only if a package is already installed,
 * which a regular depends can be satisfied by a package which we want
 * to install.
 */
int package_satisfies_dependency(int package, int depend_type)
{
	int status_num = search_status_hashtable(name_hashtable[package_hashtable[package]->name]);

	/* status could be unknown if package is a pure virtual
	 * provides which cannot satisfy any dependency by itself.
	 */
	if ( status_hashtable[status_num] == NULL )
		return 0;

	switch (depend_type) {
	case EDGE_PRE_DEPENDS: 	return get_status(status_num, 3) == search_name_hashtable("installed");
	case EDGE_DEPENDS: 	return get_status(status_num, 1) == search_name_hashtable("install");
	}
	return 0;
}

int check_deps(deb_file_t **deb_file, int deb_start, int dep_max_count)
{
	int *conflicts = NULL;
	int conflicts_num = 0;
	int i = deb_start;
	int j;

	/* Check for conflicts
	 * TODO: TEST if conflicts with other packages to be installed
	 *
	 * Add install packages and the packages they provide
	 * to the list of files to check conflicts for
	 */

	/* Create array of package numbers to check against
	 * installed package for conflicts*/
	while (deb_file[i] != NULL) {
		const unsigned int package_num = deb_file[i]->package;
		conflicts = xrealloc(conflicts, sizeof(int) * (conflicts_num + 1));
		conflicts[conflicts_num] = package_num;
		conflicts_num++;
		/* add provides to conflicts list */
		for (j = 0; j <	package_hashtable[package_num]->num_of_edges; j++) {
			if (package_hashtable[package_num]->edge[j]->type == EDGE_PROVIDES) {
				const int conflicts_package_num = search_package_hashtable(
					package_hashtable[package_num]->edge[j]->name,
					package_hashtable[package_num]->edge[j]->version,
					package_hashtable[package_num]->edge[j]->operator);
				if (package_hashtable[conflicts_package_num] == NULL) {
					/* create a new package */
					common_node_t *new_node = (common_node_t *) xmalloc(sizeof(common_node_t));
					new_node->name = package_hashtable[package_num]->edge[j]->name;
					new_node->version = package_hashtable[package_num]->edge[j]->version;
					new_node->num_of_edges = 0;
					new_node->edge = NULL;
					package_hashtable[conflicts_package_num] = new_node;
				}
				conflicts = xrealloc(conflicts, sizeof(int) * (conflicts_num + 1));
				conflicts[conflicts_num] = conflicts_package_num;
				conflicts_num++;
			}
		}
		i++;
	}

	/* Check conflicts */
	i = 0;
	while (deb_file[i] != NULL) {
		const common_node_t *package_node = package_hashtable[deb_file[i]->package];
		int status_num = 0;
		status_num = search_status_hashtable(name_hashtable[package_node->name]);

		if (get_status(status_num, 3) == search_name_hashtable("installed")) {
			i++;
			continue;
		}

		for (j = 0; j < package_node->num_of_edges; j++) {
			const edge_t *package_edge = package_node->edge[j];

			if (package_edge->type == EDGE_CONFLICTS) {
				const unsigned int package_num =
					search_package_hashtable(package_edge->name,
								 package_edge->version,
								 package_edge->operator);
				int result = 0;
				if (package_hashtable[package_num] != NULL) {
					status_num = search_status_hashtable(name_hashtable[package_hashtable[package_num]->name]);

					if (get_status(status_num, 1) == search_name_hashtable("install")) {
						result = test_version(package_hashtable[deb_file[i]->package]->version,
							package_edge->version, package_edge->operator);
					}
				}

				if (result) {
					bb_error_msg_and_die("Package %s conflicts with %s",
						name_hashtable[package_node->name],
						name_hashtable[package_edge->name]);
				}
			}
		}
		i++;
	}	


	/* Check dependendcies */
	for (i = 0; i < PACKAGE_HASH_PRIME; i++) {
		int status_num = 0;
		int number_of_alternatives = 0;
		const edge_t * root_of_alternatives;
		const common_node_t *package_node = package_hashtable[i];

		/* If the package node does not exist then this
		 * package is a virtual one. In which case there are
		 * no dependencies to check.
		 */
		if ( package_node == NULL ) continue;

		status_num = search_status_hashtable(name_hashtable[package_node->name]);

		/* If there is no status then this package is a
		 * virtual one provided by something else. In which
		 * case there are no dependencies to check.
		 */
		if ( status_hashtable[status_num] == NULL ) continue;

		/* If we don't want this package installed then we may
		 * as well ignore it's dependencies.
		 */
		if (get_status(status_num, 1) != search_name_hashtable("install")) {
			continue;
		}

#if 0
		/* This might be needed so we don't complain about
		 * things which are broken but unrelated to the
		 * packages that are currently being installed
		 */
                if (state_status == search_name_hashtable("installed"))
                        continue;
#endif

		/* This code is tested only for EDGE_DEPENDS, sine I
		 * have no suitable pre-depends available. There is no
		 * reason that it shouldn't work though :-)
		 */
		for (j = 0; j < package_node->num_of_edges; j++) {
			const edge_t *package_edge = package_node->edge[j];
			unsigned int package_num;
			
			if ( package_edge->type == EDGE_OR_PRE_DEPENDS ||
			     package_edge->type == EDGE_OR_DEPENDS ) { 	/* start an EDGE_OR_ list */
				number_of_alternatives = package_edge->version;
				root_of_alternatives = package_edge;
				continue;
			} else if ( number_of_alternatives == 0 ) { 	/* not in the middle of an EDGE_OR_ list */
				number_of_alternatives = 1;
				root_of_alternatives = NULL;
			}

			package_num = search_package_hashtable(package_edge->name, package_edge->version, package_edge->operator);

			if (package_edge->type == EDGE_PRE_DEPENDS ||
			    package_edge->type == EDGE_DEPENDS ) {
				int result=1;
				status_num = 0;

				/* If we are inside an alternative then check
				 * this edge is the right type.
				 *
				 * EDGE_DEPENDS == OR_DEPENDS -1
				 * EDGE_PRE_DEPENDS == OR_PRE_DEPENDS -1
				 */
				if ( root_of_alternatives && package_edge->type != root_of_alternatives->type - 1)
					bb_error_msg_and_die("Fatal error. Package dependencies corrupt: %d != %d - 1 \n",
							     package_edge->type, root_of_alternatives->type);

				if (package_hashtable[package_num] != NULL)
					result = !package_satisfies_dependency(package_num, package_edge->type);

				if (result) { /* check for other package which provide what we are looking for */
					int provider = -1;

					while ( (provider = search_for_provides(package_edge->name, provider) ) > -1 ) {
						if ( package_hashtable[provider] == NULL ) {
							printf("Have a provider but no package information for it\n");
							continue;
						}
						result = !package_satisfies_dependency(provider, package_edge->type);

						if ( result == 0 )
							break;
					}
				}

				/* It must be already installed, or to be installed */
				number_of_alternatives--;
				if (result && number_of_alternatives == 0) {
					if ( root_of_alternatives )
						bb_error_msg_and_die(
							"Package %s %sdepends on %s, "
							"which cannot be satisfied",
							name_hashtable[package_node->name],
							package_edge->type == EDGE_PRE_DEPENDS ? "pre-" : "",
							name_hashtable[root_of_alternatives->name]);
					else
						bb_error_msg_and_die(
							"Package %s %sdepends on %s, which %s\n",
							name_hashtable[package_node->name],
							package_edge->type == EDGE_PRE_DEPENDS ? "pre-" : "",
							name_hashtable[package_edge->name],
							describe_status(status_num));
				} else if ( result == 0 && number_of_alternatives ) {
					/* we've found a package which
					 * satisfies the dependency,
					 * so skip over the rest of
					 * the alternatives.
					 */
					j += number_of_alternatives;
					number_of_alternatives = 0;
				}
			}
		}
	}
	free(conflicts);
	return(TRUE);
}

char **create_list(const char *filename)
{
	FILE *list_stream;
	char **file_list = NULL;
	char *line = NULL;
	int count = 0;

	/* dont use [xw]fopen here, handle error ourself */
	list_stream = fopen(filename, "r");
	if (list_stream == NULL) {
		return(NULL);
	}

	while ((line = bb_get_chomped_line_from_file(list_stream)) != NULL) {
		file_list = xrealloc(file_list, sizeof(char *) * (count + 2));
		file_list[count] = line;
		count++;
	}
	fclose(list_stream);

	if (count == 0) {
		return(NULL);
	} else {
		file_list[count] = NULL;
		return(file_list);
	}
}

/* maybe i should try and hook this into remove_file.c somehow */
int remove_file_array(char **remove_names, char **exclude_names)
{
	struct stat path_stat;
	int match_flag;
	int remove_flag = FALSE;
	int i,j;

	if (remove_names == NULL) {
		return(FALSE);
	}
	for (i = 0; remove_names[i] != NULL; i++) {
		match_flag = FALSE;
		if (exclude_names != NULL) {
			for (j = 0; exclude_names[j] != 0; j++) {
				if (strcmp(remove_names[i], exclude_names[j]) == 0) {
					match_flag = TRUE;
					break;
				}
			}
		}
		if (!match_flag) {
			if (lstat(remove_names[i], &path_stat) < 0) {
				continue;
			}
			if (S_ISDIR(path_stat.st_mode)) {
				if (rmdir(remove_names[i]) != -1) {
					remove_flag = TRUE;
				}
			} else {
				if (unlink(remove_names[i]) != -1) {
					remove_flag = TRUE;
				}
			}
		}
	}
	return(remove_flag);
}

int run_package_script(const char *package_name, const char *script_type)
{
	struct stat path_stat;
	char *script_path;
	int result;

	script_path = xmalloc(strlen(package_name) + strlen(script_type) + 21);
	sprintf(script_path, "/var/lib/dpkg/info/%s.%s", package_name, script_type);

	/* If the file doesnt exist is isnt a fatal */
	if (lstat(script_path, &path_stat) < 0) {
		result = EXIT_SUCCESS;
	} else {
		result = system(script_path);
	}
	free(script_path);
	return(result);
}

const char *all_control_files[] = {"preinst", "postinst", "prerm", "postrm",
	"list", "md5sums", "shlibs", "conffiles", "config", "templates", NULL };

char **all_control_list(const char *package_name)
{
	unsigned short i = 0;
	char **remove_files;

	/* Create a list of all /var/lib/dpkg/info/<package> files */
	remove_files = malloc(sizeof(all_control_files));
	while (all_control_files[i]) {
		remove_files[i] = xmalloc(strlen(package_name) + strlen(all_control_files[i]) + 21);
		sprintf(remove_files[i], "/var/lib/dpkg/info/%s.%s", package_name, all_control_files[i]);
		i++;
	}
	remove_files[sizeof(all_control_files)/sizeof(char*) - 1] = NULL;

	return(remove_files);
}

void free_array(char **array)
{

	if (array) {
		unsigned short i = 0;
		while (array[i]) {
			free(array[i]);
			i++;
		}
		free(array);
	}
}

/* This function lists information on the installed packages. It loops through
 * the status_hashtable to retrieve the info. This results in smaller code than
 * scanning the status file. The resulting list, however, is unsorted.
 */
void list_packages(void)
{
        int i;

	printf("    Name           Version\n");
	printf("+++-==============-==============\n");

	/* go through status hash, dereference package hash and finally strings */
	for (i=0; i<STATUS_HASH_PRIME+1; i++) {

	        if (status_hashtable[i]) {
		        const char *stat_str;  /* status string */
			const char *name_str;  /* package name */
			const char *vers_str;  /* version */
			char  s1, s2;          /* status abbreviations */
			int   spccnt;          /* space count */
			int   j;

			stat_str = name_hashtable[status_hashtable[i]->status];
			name_str = name_hashtable[package_hashtable[status_hashtable[i]->package]->name];
			vers_str = name_hashtable[package_hashtable[status_hashtable[i]->package]->version];

			/* get abbreviation for status field 1 */
			s1 = stat_str[0] == 'i' ? 'i' : 'r';

			/* get abbreviation for status field 2 */
			for (j=0, spccnt=0; stat_str[j] && spccnt<2; j++) {
			        if (stat_str[j] == ' ') spccnt++;
			}
			s2 = stat_str[j];

			/* print out the line formatted like Debian dpkg */
			printf("%c%c  %-14s %s\n", s1, s2, name_str, vers_str);
		}
    }
}

void remove_package(const unsigned int package_num, int noisy)
{
	const char *package_name = name_hashtable[package_hashtable[package_num]->name];
	const char *package_version = name_hashtable[package_hashtable[package_num]->version];
	const unsigned int status_num = search_status_hashtable(package_name);
	const int package_name_length = strlen(package_name);
	char **remove_files;
	char **exclude_files;
	char list_name[package_name_length + 25];
	char conffile_name[package_name_length + 30];
	int return_value;

	if ( noisy )
		printf("Removing %s (%s) ...\n", package_name, package_version);

	/* run prerm script */
	return_value = run_package_script(package_name, "prerm");
	if (return_value == -1) {
		bb_error_msg_and_die("script failed, prerm failure");
	}

	/* Create a list of files to remove, and a seperate list of those to keep */
	sprintf(list_name, "/var/lib/dpkg/info/%s.list", package_name);
	remove_files = create_list(list_name);

	sprintf(conffile_name, "/var/lib/dpkg/info/%s.conffiles", package_name);
	exclude_files = create_list(conffile_name);

	/* Some directories cant be removed straight away, so do multiple passes */
	while (remove_file_array(remove_files, exclude_files));
	free_array(exclude_files);
	free_array(remove_files);

	/* Create a list of files in /var/lib/dpkg/info/<package>.* to keep  */
	exclude_files = xmalloc(sizeof(char*) * 3);
	exclude_files[0] = bb_xstrdup(conffile_name);
	exclude_files[1] = xmalloc(package_name_length + 27);
	sprintf(exclude_files[1], "/var/lib/dpkg/info/%s.postrm", package_name);
	exclude_files[2] = NULL;

	/* Create a list of all /var/lib/dpkg/info/<package> files */
	remove_files = all_control_list(package_name);

	remove_file_array(remove_files, exclude_files);
	free_array(remove_files);
	free_array(exclude_files);

	/* rename <package>.conffile to <package>.list */
	rename(conffile_name, list_name);

	/* Change package status */
	set_status(status_num, "config-files", 3);
}

void purge_package(const unsigned int package_num)
{
	const char *package_name = name_hashtable[package_hashtable[package_num]->name];
	const char *package_version = name_hashtable[package_hashtable[package_num]->version];
	const unsigned int status_num = search_status_hashtable(package_name);
	char **remove_files;
	char **exclude_files;
	char list_name[strlen(package_name) + 25];

	printf("Purging %s (%s) ...\n", package_name, package_version);

	/* run prerm script */
	if (run_package_script(package_name, "prerm") != 0) {
		bb_error_msg_and_die("script failed, prerm failure");
	}

	/* Create a list of files to remove */
	sprintf(list_name, "/var/lib/dpkg/info/%s.list", package_name);
	remove_files = create_list(list_name);

	exclude_files = xmalloc(sizeof(char*));
	exclude_files[0] = NULL;

	/* Some directories cant be removed straight away, so do multiple passes */
	while (remove_file_array(remove_files, exclude_files));
	free_array(remove_files);

	/* Create a list of all /var/lib/dpkg/info/<package> files */
	remove_files = all_control_list(package_name);
	remove_file_array(remove_files, exclude_files);
	free_array(remove_files);
	free(exclude_files);

	/* run postrm script */
	if (run_package_script(package_name, "postrm") == -1) {
		bb_error_msg_and_die("postrm fialure.. set status to what?");
	}

	/* Change package status */
	set_status(status_num, "not-installed", 3);
}

static archive_handle_t *init_archive_deb_ar(const char *filename)
{
	archive_handle_t *ar_handle;

	/* Setup an ar archive handle that refers to the gzip sub archive */
	ar_handle = init_handle();
	ar_handle->filter = filter_accept_list_reassign;
	ar_handle->src_fd = bb_xopen(filename, O_RDONLY);

	return(ar_handle);
}

static void init_archive_deb_control(archive_handle_t *ar_handle)
{
	archive_handle_t *tar_handle;

	/* Setup the tar archive handle */
	tar_handle = init_handle();
	tar_handle->src_fd = ar_handle->src_fd;

	/* We dont care about data.tar.* or debian-binary, just control.tar.* */
#ifdef CONFIG_FEATURE_DEB_TAR_GZ
	ar_handle->accept = llist_add_to(NULL, "control.tar.gz");
#endif
#ifdef CONFIG_FEATURE_DEB_TAR_BZ2
	ar_handle->accept = llist_add_to(ar_handle->accept, "control.tar.bz2");
#endif

	/* Assign the tar handle as a subarchive of the ar handle */
	ar_handle->sub_archive = tar_handle;

	return;
}

static void init_archive_deb_data(archive_handle_t *ar_handle)
{
	archive_handle_t *tar_handle;

	/* Setup the tar archive handle */
	tar_handle = init_handle();
	tar_handle->src_fd = ar_handle->src_fd;

	/* We dont care about control.tar.* or debian-binary, just data.tar.* */
#ifdef CONFIG_FEATURE_DEB_TAR_GZ
	ar_handle->accept = llist_add_to(NULL, "data.tar.gz");
#endif
#ifdef CONFIG_FEATURE_DEB_TAR_BZ2
	ar_handle->accept = llist_add_to(ar_handle->accept, "data.tar.bz2");
#endif

	/* Assign the tar handle as a subarchive of the ar handle */
	ar_handle->sub_archive = tar_handle;

	return;
}

static char *deb_extract_control_file_to_buffer(archive_handle_t *ar_handle, llist_t *myaccept)
{
	ar_handle->sub_archive->action_data = data_extract_to_buffer;
	ar_handle->sub_archive->accept = myaccept;

	unpack_ar_archive(ar_handle);
	close(ar_handle->src_fd);

	return(ar_handle->sub_archive->buffer);
}

static void data_extract_all_prefix(archive_handle_t *archive_handle)
{
	char *name_ptr = archive_handle->file_header->name;

	name_ptr += strspn(name_ptr, "./");
	if (name_ptr[0] != '\0') {
		archive_handle->file_header->name = xmalloc(strlen(archive_handle->buffer) + 2 + strlen(name_ptr));
		strcpy(archive_handle->file_header->name, archive_handle->buffer);
		strcat(archive_handle->file_header->name, name_ptr);
		data_extract_all(archive_handle);
	}
	return;
}

static void unpack_package(deb_file_t *deb_file)
{
	const char *package_name = name_hashtable[package_hashtable[deb_file->package]->name];
	const unsigned int status_num = search_status_hashtable(package_name);
	const unsigned int status_package_num = status_hashtable[status_num]->package;
	char *info_prefix;
	archive_handle_t *archive_handle;
	FILE *out_stream;
	llist_t *accept_list = NULL;
	int i = 0;

	/* If existing version, remove it first */
	if (strcmp(name_hashtable[get_status(status_num, 3)], "installed") == 0) {
		/* Package is already installed, remove old version first */
		printf("Preparing to replace %s %s (using %s) ...\n", package_name,
			name_hashtable[package_hashtable[status_package_num]->version],
			deb_file->filename);
		remove_package(status_package_num, 0);
	} else {
		printf("Unpacking %s (from %s) ...\n", package_name, deb_file->filename);
	}

	/* Extract control.tar.gz to /var/lib/dpkg/info/<package>.filename */
	info_prefix = (char *) xmalloc(strlen(package_name) + 20 + 4 + 2);
	sprintf(info_prefix, "/var/lib/dpkg/info/%s.", package_name);
	archive_handle = init_archive_deb_ar(deb_file->filename);
	init_archive_deb_control(archive_handle);

	while(all_control_files[i]) {
		char *c = (char *) xmalloc(3 + bb_strlen(all_control_files[i]));
		sprintf(c, "./%s", all_control_files[i]);
		accept_list= llist_add_to(accept_list, c);
		i++;
	}
	archive_handle->sub_archive->accept = accept_list;
	archive_handle->sub_archive->filter = filter_accept_list;
	archive_handle->sub_archive->action_data = data_extract_all_prefix;
	archive_handle->sub_archive->buffer = info_prefix;
	archive_handle->sub_archive->flags |= ARCHIVE_EXTRACT_UNCONDITIONAL;
	unpack_ar_archive(archive_handle);

	/* Run the preinst prior to extracting */
	if (run_package_script(package_name, "preinst") != 0) {
		/* when preinst returns exit code != 0 then quit installation process */
		bb_error_msg_and_die("subprocess pre-installation script returned error.");
	}

	/* Extract data.tar.gz to the root directory */
	archive_handle = init_archive_deb_ar(deb_file->filename);
	init_archive_deb_data(archive_handle);
	archive_handle->sub_archive->action_data = data_extract_all_prefix;
	archive_handle->sub_archive->buffer = "/";
	archive_handle->sub_archive->flags |= ARCHIVE_EXTRACT_UNCONDITIONAL;
	unpack_ar_archive(archive_handle);

	/* Create the list file */
	strcat(info_prefix, "list");
	out_stream = bb_xfopen(info_prefix, "w");
	while (archive_handle->sub_archive->passed) {
		/* the leading . has been stripped by data_extract_all_prefix already */
		fputs(archive_handle->sub_archive->passed->data, out_stream);
		fputc('\n', out_stream);
		archive_handle->sub_archive->passed = archive_handle->sub_archive->passed->link;
	}
	fclose(out_stream);

	/* change status */
	set_status(status_num, "install", 1);
	set_status(status_num, "unpacked", 3);

	free(info_prefix);
}

void configure_package(deb_file_t *deb_file)
{
	const char *package_name = name_hashtable[package_hashtable[deb_file->package]->name];
	const char *package_version = name_hashtable[package_hashtable[deb_file->package]->version];
	const int status_num = search_status_hashtable(package_name);

	printf("Setting up %s (%s) ...\n", package_name, package_version);

	/* Run the postinst script */
	if (run_package_script(package_name, "postinst") != 0) {
		/* TODO: handle failure gracefully */
		bb_error_msg_and_die("postrm failure.. set status to what?");
	}
	/* Change status to reflect success */
	set_status(status_num, "install", 1);
	set_status(status_num, "installed", 3);
}

int dpkg_main(int argc, char **argv)
{
	deb_file_t **deb_file = NULL;
	status_node_t *status_node;
	int opt;
	int package_num;
	int dpkg_opt = 0;
	int deb_count = 0;
	int state_status;
	int status_num;
	int i;

	while ((opt = getopt(argc, argv, "CF:ilPru")) != -1) {
		switch (opt) {
			case 'C': // equivalent to --configure in official dpkg
				dpkg_opt |= dpkg_opt_configure;
				dpkg_opt |= dpkg_opt_package_name;
				break;
			case 'F': // equivalent to --force in official dpkg
				if (strcmp(optarg, "depends") == 0) {
					dpkg_opt |= dpkg_opt_force_ignore_depends;
				}
				break;
			case 'i':
				dpkg_opt |= dpkg_opt_install;
				dpkg_opt |= dpkg_opt_filename;
				break;
			case 'l':
				dpkg_opt |= dpkg_opt_list_installed;
				break;
			case 'P':
				dpkg_opt |= dpkg_opt_purge;
				dpkg_opt |= dpkg_opt_package_name;
				break;
			case 'r':
				dpkg_opt |= dpkg_opt_remove;
				dpkg_opt |= dpkg_opt_package_name;
				break;
			case 'u':	/* Equivalent to --unpack in official dpkg */
				dpkg_opt |= dpkg_opt_unpack;
				dpkg_opt |= dpkg_opt_filename;
				break;
			default:
				bb_show_usage();
		}
	}
	/* check for non-otion argument if expected  */
	if ((dpkg_opt == 0) || ((argc == optind) && !(dpkg_opt && dpkg_opt_list_installed))) {
		bb_show_usage();
	}

/*	puts("(Reading database ... xxxxx files and directories installed.)"); */
	index_status_file("/var/lib/dpkg/status");

	/* if the list action was given print the installed packages and exit */
	if (dpkg_opt & dpkg_opt_list_installed) {
		list_packages();
		return(EXIT_SUCCESS);
	}

	/* Read arguments and store relevant info in structs */
	while (optind < argc) {
		/* deb_count = nb_elem - 1 and we need nb_elem + 1 to allocate terminal node [NULL pointer] */
		deb_file = xrealloc(deb_file, sizeof(deb_file_t *) * (deb_count + 2));
		deb_file[deb_count] = (deb_file_t *) xmalloc(sizeof(deb_file_t));
		if (dpkg_opt & dpkg_opt_filename) {
			archive_handle_t *archive_handle;
			llist_t *control_list = NULL;

			/* Extract the control file */
			control_list = llist_add_to(NULL, "./control");
			archive_handle = init_archive_deb_ar(argv[optind]);
			init_archive_deb_control(archive_handle);
			deb_file[deb_count]->control_file = deb_extract_control_file_to_buffer(archive_handle, control_list);
			if (deb_file[deb_count]->control_file == NULL) {
				bb_error_msg_and_die("Couldnt extract control file");
			}
			deb_file[deb_count]->filename = bb_xstrdup(argv[optind]);
			package_num = fill_package_struct(deb_file[deb_count]->control_file);

			if (package_num == -1) {
				bb_error_msg("Invalid control file in %s", argv[optind]);
				continue;
			}
			deb_file[deb_count]->package = (unsigned int) package_num;

			/* Add the package to the status hashtable */
			if ((dpkg_opt & dpkg_opt_unpack) || (dpkg_opt & dpkg_opt_install)) {
				/* Try and find a currently installed version of this package */
				status_num = search_status_hashtable(name_hashtable[package_hashtable[deb_file[deb_count]->package]->name]);
				/* If no previous entry was found initialise a new entry */
				if ((status_hashtable[status_num] == NULL) ||
					(status_hashtable[status_num]->status == 0)) {
					status_node = (status_node_t *) xmalloc(sizeof(status_node_t));
					status_node->package = deb_file[deb_count]->package;
					/* reinstreq isnt changed to "ok" until the package control info
					 * is written to the status file*/
					status_node->status = search_name_hashtable("install reinstreq not-installed");
					status_hashtable[status_num] = status_node;
				} else {
					set_status(status_num, "install", 1);
					set_status(status_num, "reinstreq", 2);
				}
			}
		}
		else if (dpkg_opt & dpkg_opt_package_name) {
			deb_file[deb_count]->filename = NULL;
			deb_file[deb_count]->control_file = NULL;
			deb_file[deb_count]->package = search_package_hashtable(
				search_name_hashtable(argv[optind]),
				search_name_hashtable("ANY"), VER_ANY);
			if (package_hashtable[deb_file[deb_count]->package] == NULL) {
				bb_error_msg_and_die("Package %s is uninstalled or unknown\n", argv[optind]);
			}
			package_num = deb_file[deb_count]->package;
			status_num = search_status_hashtable(name_hashtable[package_hashtable[package_num]->name]);
			state_status = get_status(status_num, 3);

			/* check package status is "installed" */
			if (dpkg_opt & dpkg_opt_remove) {
				if ((strcmp(name_hashtable[state_status], "not-installed") == 0) ||
					(strcmp(name_hashtable[state_status], "config-files") == 0)) {
					bb_error_msg_and_die("%s is already removed.", name_hashtable[package_hashtable[package_num]->name]);
				}
				set_status(status_num, "deinstall", 1);
			}
			else if (dpkg_opt & dpkg_opt_purge) {
				/* if package status is "conf-files" then its ok */
				if (strcmp(name_hashtable[state_status], "not-installed") == 0) {
					bb_error_msg_and_die("%s is already purged.", name_hashtable[package_hashtable[package_num]->name]);
				}
				set_status(status_num, "purge", 1);
			}
		}
		deb_count++;
		optind++;
	}
	deb_file[deb_count] = NULL;

	/* Check that the deb file arguments are installable */
	if ((dpkg_opt & dpkg_opt_force_ignore_depends) != dpkg_opt_force_ignore_depends) {
		if (!check_deps(deb_file, 0, deb_count)) {
			bb_error_msg_and_die("Dependency check failed");
		}
	}

	/* TODO: install or remove packages in the correct dependency order */
	for (i = 0; i < deb_count; i++) {
		/* Remove or purge packages */
		if (dpkg_opt & dpkg_opt_remove) {
			remove_package(deb_file[i]->package, 1);
		}
		else if (dpkg_opt & dpkg_opt_purge) {
			purge_package(deb_file[i]->package);
		}
		else if (dpkg_opt & dpkg_opt_unpack) {
			unpack_package(deb_file[i]);
		}
		else if (dpkg_opt & dpkg_opt_install) {
			unpack_package(deb_file[i]);
			/* package is configured in second pass below */
		}
		else if (dpkg_opt & dpkg_opt_configure) {
			configure_package(deb_file[i]);
		}
	}
	/* configure installed packages */
	if (dpkg_opt & dpkg_opt_install) {
		for (i = 0; i < deb_count; i++)
			configure_package(deb_file[i]);
	}

	write_status_file(deb_file);

	for (i = 0; i < deb_count; i++) {
		free(deb_file[i]->control_file);
		free(deb_file[i]->filename);
		free(deb_file[i]);
	}

	free(deb_file);

	for (i = 0; i < NAME_HASH_PRIME; i++) {
		free(name_hashtable[i]);
	}

	for (i = 0; i < PACKAGE_HASH_PRIME; i++) {
		if (package_hashtable[i] != NULL) {
			free_package(package_hashtable[i]);
		}
	}

	for (i = 0; i < STATUS_HASH_PRIME; i++) {
		free(status_hashtable[i]);
	}

	return(EXIT_SUCCESS);
}

