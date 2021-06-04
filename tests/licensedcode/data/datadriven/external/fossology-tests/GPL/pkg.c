
/*
* Copyright (C) 2001, 2002 Red Hat Inc.
*
* This program is free software; you can redistribute it and/or
* modify it under the terms of the GNU General Public License as
* published by the Free Software Foundation; either version 2 of the
* License, or (at your option) any later version.
*
* This program is distributed in the hope that it will be useful, but
* WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
* General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program; if not, write to the Free Software
* Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
* 02111-1307, USA.
*/


#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "pkg.h"
#include "parse.h"

#ifdef HAVE_MALLOC_H
# include <malloc.h>
#endif

#include <sys/types.h>
#include <dirent.h>
#include <string.h>
#include <errno.h>
#include <stdio.h>
#ifdef HAVE_UNISTD_H
#include <unistd.h>
#endif
#include <stdlib.h>
#include <ctype.h>

static void verify_package (Package *pkg);

static GHashTable *packages = NULL;
static GHashTable *locations = NULL;
static GHashTable *path_positions = NULL;
static GHashTable *globals = NULL;
static GList *search_dirs = NULL;
static int scanned_dir_count = 0;

gboolean disable_uninstalled = FALSE;
gboolean ignore_requires = FALSE;
gboolean ignore_requires_private = TRUE;
gboolean ignore_private_libs = TRUE;

void
add_search_dir (const char *path)
{
search_dirs = g_list_append (search_dirs, g_strdup (path));
}

void
add_search_dirs (const char *path, const char *separator)
{
char **search_dirs;
char **iter;

search_dirs = g_strsplit (path, separator, -1);

iter = search_dirs;
while (*iter)
{
debug_spew ("Adding directory '%s' from PKG_CONFIG_PATH\n",
*iter);
add_search_dir (*iter);

++iter;
}

g_strfreev (search_dirs);
}

#ifdef G_OS_WIN32
/* Guard against .pc file being installed with UPPER CASE name */
# define FOLD(x) tolower(x)
# define FOLDCMP(a, b) g_ascii_strcasecmp (a, b)
#else
# define FOLD(x) (x)
# define FOLDCMP(a, b) strcmp (a, b)
#endif

#define EXT_LEN 3

static gboolean
ends_in_dotpc (const char *str)
{
int len = strlen (str);

if (len > EXT_LEN &&
str[len - 3] == '.' &&
FOLD (str[len - 2]) == 'p' &&
FOLD (str[len - 1]) == 'c')
return TRUE;
else
return FALSE;
}

/* strlen ("-uninstalled") */
#define UNINSTALLED_LEN 12

gboolean
name_ends_in_uninstalled (const char *str)
{
int len = strlen (str);

if (len > UNINSTALLED_LEN &&
FOLDCMP ((str + len - UNINSTALLED_LEN), "-uninstalled") == 0)
return TRUE;
else
return FALSE;
}


/* Look for .pc files in the given directory and add them into
* locations, ignoring duplicates
*/
static void
scan_dir (const char *dirname)
{
DIR *dir;
struct dirent *dent;
int dirnamelen = strlen (dirname);
/* Use a copy of dirname cause Win32 opendir doesn't like
* superfluous trailing (back)slashes in the directory name.
*/
char *dirname_copy = g_strdup (dirname);

if (dirnamelen > 1 && dirname[dirnamelen-1] == G_DIR_SEPARATOR)
{
dirnamelen--;
dirname_copy[dirnamelen] = '\0';
}
#ifdef G_OS_WIN32
{
gchar *p;
/* Turn backslashes into slashes or
* g_shell_parse_argv() will eat them when ${prefix}
* has been expanded in parse_libs().
*/
p = dirname;
while (*p)
{
if (*p == '\\')
*p = '/';
p++;
}
}
#endif
dir = opendir (dirname_copy);
g_free (dirname_copy);
if (!dir)
{
debug_spew ("Cannot open directory '%s' in package search path: %s\n",
dirname, g_strerror (errno));
return;
}

debug_spew ("Scanning directory '%s'\n", dirname);

scanned_dir_count += 1;

while ((dent = readdir (dir)))
{
int len = strlen (dent->d_name);

if (ends_in_dotpc (dent->d_name))
{
char *pkgname = g_malloc (len - 2);

debug_spew ("File '%s' appears to be a .pc file\n", dent->d_name);

strncpy (pkgname, dent->d_name, len - EXT_LEN);
pkgname[len-EXT_LEN] = '\0';

if (g_hash_table_lookup (locations, pkgname))
{
debug_spew ("File '%s' ignored, we already know about package '%s'\n", dent->d_name, pkgname);
g_free (pkgname);
}
else
{
char *filename = g_malloc (dirnamelen + 1 + len + 1);
strncpy (filename, dirname, dirnamelen);
filename[dirnamelen] = G_DIR_SEPARATOR;
strcpy (filename + dirnamelen + 1, dent->d_name);

if (g_file_test(filename, G_FILE_TEST_IS_REGULAR) == TRUE) {
g_hash_table_insert (locations, pkgname, filename);
g_hash_table_insert (path_positions, pkgname,
GINT_TO_POINTER (scanned_dir_count));
debug_spew ("Will find package '%s' in file '%s'\n",
pkgname, filename);
} else {
debug_spew ("Ignoring '%s' while looking for '%s'; not a "
"regular file.\n", pkgname, filename);
}
}
}
else
{
debug_spew ("Ignoring file '%s' in search directory; not a .pc file\n",
dent->d_name);
}
}
closedir(dir);
}

static Package *
add_virtual_pkgconfig_package (void)
{
Package *pkg = NULL;

pkg = g_new0 (Package, 1);

pkg->key = g_strdup ("pkg-config");
pkg->version = g_strdup (VERSION);
pkg->name = g_strdup ("pkg-config");
pkg->description = g_strdup ("pkg-config is a system for managing "
"compile/link flags for libraries");
pkg->url = g_strdup ("http://pkg-config.freedesktop.org/");

if (pkg->vars == NULL)
pkg->vars = g_hash_table_new (g_str_hash, g_str_equal);
g_hash_table_insert (pkg->vars, "pc_path", pkg_config_pc_path);

debug_spew ("Adding virtual 'pkg-config' package to list of known packages\n");
g_hash_table_insert (packages, pkg->key, pkg);

return pkg;
}

void
package_init ()
{
static gboolean initted = FALSE;

if (!initted)
{
initted = TRUE;

packages = g_hash_table_new (g_str_hash, g_str_equal);
locations = g_hash_table_new (g_str_hash, g_str_equal);
path_positions = g_hash_table_new (g_str_hash, g_str_equal);

add_virtual_pkgconfig_package ();

g_list_foreach (search_dirs, (GFunc)scan_dir, NULL);
}
}

static Package *
internal_get_package (const char *name, gboolean warn)
{
Package *pkg = NULL;
const char *location;
GList *iter;

pkg = g_hash_table_lookup (packages, name);

if (pkg)
return pkg;

debug_spew ("Looking for package '%s'\n", name);

/* treat "name" as a filename if it ends in .pc and exists */
if ( ends_in_dotpc (name) )
{
debug_spew ("Considering '%s' to be a filename rather than a package name\n", name);
location = name;
}
else
{
/* See if we should auto-prefer the uninstalled version */
if (!disable_uninstalled &&
!name_ends_in_uninstalled (name))
{
char *un;

un = g_strconcat (name, "-uninstalled", NULL);

pkg = internal_get_package (un, FALSE);

g_free (un);

if (pkg)
{
debug_spew ("Preferring uninstalled version of package '%s'\n", name);
return pkg;
}
}

location = g_hash_table_lookup (locations, name);
}

if (location == NULL)
{
if (warn)
verbose_error ("Package %s was not found in the pkg-config search path.\n"
"Perhaps you should add the directory containing `%s.pc'\n"
"to the PKG_CONFIG_PATH environment variable\n",
name, name);

return NULL;
}

debug_spew ("Reading '%s' from file '%s'\n", name, location);
pkg = parse_package_file (location, ignore_requires, ignore_private_libs,
ignore_requires_private);

if (pkg == NULL)
{
debug_spew ("Failed to parse '%s'\n", location);
return NULL;
}

if (strstr (location, "uninstalled.pc"))
pkg->uninstalled = TRUE;

if (location != name)
pkg->key = g_strdup (name);
else
{
/* need to strip package name out of the filename */
int len = strlen (name);
const char *end = name + (len - EXT_LEN);
const char *start = end;

while (start != name && *start != G_DIR_SEPARATOR)
--start;

g_assert (end >= start);

pkg->key = g_strndup (start, end - start);
}

pkg->path_position =
GPOINTER_TO_INT (g_hash_table_lookup (path_positions, pkg->key));

debug_spew ("Path position of '%s' is %d\n",
pkg->key, pkg->path_position);

debug_spew ("Adding '%s' to list of known packages\n", pkg->key);
g_hash_table_insert (packages, pkg->key, pkg);

/* pull in Requires packages */
for (iter = pkg->requires_entries; iter != NULL; iter = g_list_next (iter))
{
Package *req;
RequiredVersion *ver = iter->data;

debug_spew ("Searching for '%s' requirement '%s'\n",
pkg->key, ver->name);
req = internal_get_package (ver->name, warn);
if (req == NULL)
{
verbose_error ("Package '%s', required by '%s', not found\n",
ver->name, pkg->key);
exit (1);
}

if (pkg->required_versions == NULL)
pkg->required_versions = g_hash_table_new (g_str_hash, g_str_equal);

g_hash_table_insert (pkg->required_versions, ver->name, ver);
pkg->requires = g_list_prepend (pkg->requires, req);
}

/* pull in Requires.private packages */
for (iter = pkg->requires_private_entries; iter != NULL;
iter = g_list_next (iter))
{
Package *req;
RequiredVersion *ver = iter->data;

debug_spew ("Searching for '%s' private requirement '%s'\n",
pkg->key, ver->name);
req = internal_get_package (ver->name, warn);
if (req == NULL)
{
verbose_error ("Package '%s', required by '%s', not found\n",
ver->name, pkg->key);
exit (1);
}

if (pkg->required_versions == NULL)
pkg->required_versions = g_hash_table_new (g_str_hash, g_str_equal);

g_hash_table_insert (pkg->required_versions, ver->name, ver);
pkg->requires_private = g_list_prepend (pkg->requires_private, req);
}

/* make requires_private include a copy of the public requires too */
pkg->requires_private = g_list_concat (g_list_copy (pkg->requires),
pkg->requires_private);

pkg->requires = g_list_reverse (pkg->requires);
pkg->requires_private = g_list_reverse (pkg->requires_private);

verify_package (pkg);

return pkg;
}

Package *
get_package (const char *name)
{
return internal_get_package (name, TRUE);
}

Package *
get_package_quiet (const char *name)
{
return internal_get_package (name, FALSE);
}

/* Strip consecutive duplicate arguments in the flag list. */
static GList *
flag_list_strip_duplicates (GList *list)
{
GList *tmp;

/* Start at the 2nd element of the list so we don't have to check for an
* existing previous element. */
for (tmp = g_list_next (list); tmp != NULL; tmp = g_list_next (tmp))
{
Flag *cur = tmp->data;
Flag *prev = tmp->prev->data;

if (cur->type == prev->type && g_strcmp0 (cur->arg, prev->arg) == 0)
{
/* Remove the duplicate flag from the list and move to the last
* element to prepare for the next iteration. */
GList *dup = tmp;

debug_spew (" removing duplicate \"%s\"\n", cur->arg);
tmp = g_list_previous (tmp);
list = g_list_remove_link (list, dup);
}
}

return list;
}

static char *
flag_list_to_string (GList *list)
{
GList *tmp;
GString *str = g_string_new ("");
char *retval;

tmp = list;
while (tmp != NULL) {
Flag *flag = tmp->data;
char *tmpstr = flag->arg;

if (pcsysrootdir != NULL && flag->type & (CFLAGS_I | LIBS_L)) {
g_string_append_c (str, '-');
g_string_append_c (str, tmpstr[1]);
g_string_append (str, pcsysrootdir);
g_string_append (str, tmpstr+2);
} else {
g_string_append (str, tmpstr);
}
g_string_append_c (str, ' ');
tmp = g_list_next (tmp);
}

retval = str->str;
g_string_free (str, FALSE);

return retval;
}

static int
pathposcmp (gconstpointer a, gconstpointer b)
{
const Package *pa = a;
const Package *pb = b;

if (pa->path_position < pb->path_position)
return -1;
else if (pa->path_position > pb->path_position)
return 1;
else
return 0;
}

static void
spew_package_list (const char *name,
GList *list)
{
GList *tmp;

debug_spew (" %s:", name);

tmp = list;
while (tmp != NULL)
{
Package *pkg = tmp->data;
debug_spew (" %s", pkg->key);
tmp = tmp->next;
}
debug_spew ("\n");
}


static GList *
packages_sort_by_path_position (GList *list)
{
return g_list_sort (list, pathposcmp);
}

static void
recursive_fill_list (Package *pkg, gboolean include_private, GList **listp)
{
GList *tmp;

/*
* If the package is one of the parents, we can skip it. This allows
* circular requires loops to be broken.
*/
if (pkg->in_requires_chain)
{
debug_spew ("Package %s already in requires chain, skipping\n",
pkg->key);
return;
}

/* record this package in the dependency chain */
pkg->in_requires_chain = TRUE;

/* Start from the end of the required package list to maintain order since
* the recursive list is built by prepending. */
tmp = include_private ? pkg->requires_private : pkg->requires;
for (tmp = g_list_last (tmp); tmp != NULL; tmp = g_list_previous (tmp))
recursive_fill_list (tmp->data, include_private, listp);

*listp = g_list_prepend (*listp, pkg);

/* remove this package from the dependency chain now that we've unwound */
pkg->in_requires_chain = FALSE;
}

/* merge the flags from the individual packages */
static GList *
merge_flag_lists (GList *packages, FlagType type)
{
GList *last = NULL;
GList *merged = NULL;

/* keep track of the last element to avoid traversing the whole list */
for (; packages != NULL; packages = g_list_next (packages))
{
Package *pkg = packages->data;
GList *flags = (type & LIBS_ANY) ? pkg->libs : pkg->cflags;

/* manually copy the elements so we can keep track of the end */
for (; flags != NULL; flags = g_list_next (flags))
{
Flag *flag = flags->data;

if (flag->type & type)
{
if (last == NULL)
{
merged = g_list_prepend (NULL, flags->data);
last = merged;
}
else
last = g_list_next (g_list_append (last, flags->data));
}
}
}

return merged;
}

/* Work backwards from the end of the package list to remove duplicate
* packages. This could happen because the package was specified multiple
* times on the command line, or because multiple packages require the same
* package. When we have duplicate dependencies, starting from the end of the
* list ensures that the dependency shows up later in the package list and
* Libs will come out correctly. */
static GList *
package_list_strip_duplicates (GList *packages)
{
GList *cur;
GHashTable *requires;

requires = g_hash_table_new (g_str_hash, g_str_equal);
for (cur = g_list_last (packages); cur != NULL; cur = g_list_previous (cur))
{
Package *pkg = cur->data;

if (g_hash_table_lookup_extended (requires, pkg->key, NULL, NULL))
{
GList *dup = cur;

/* Remove the duplicate package from the list */
debug_spew ("Removing duplicate package %s\n", pkg->key);
cur = cur->next;
packages = g_list_delete_link (packages, dup);
}
else
{
/* Unique package. Track it and move to the next. */
g_hash_table_replace (requires, pkg->key, pkg->key);
}
}
g_hash_table_destroy (requires);

return packages;
}

static GList *
fill_list (GList *packages, FlagType type,
gboolean in_path_order, gboolean include_private)
{
GList *tmp;
GList *expanded = NULL;
GList *flags;

/* Start from the end of the requested package list to maintain order since
* the recursive list is built by prepending. */
for (tmp = g_list_last (packages); tmp != NULL; tmp = g_list_previous (tmp))
recursive_fill_list (tmp->data, include_private, &expanded);

/* Remove duplicate packages from the recursive list. This should provide a
* serialized package list where all interdependencies are resolved
* consistently. */
spew_package_list (" pre-remove", expanded);
expanded = package_list_strip_duplicates (expanded);
spew_package_list ("post-remove", expanded);

if (in_path_order)
{
spew_package_list ("original", expanded);
expanded = packages_sort_by_path_position (expanded);
spew_package_list (" sorted", expanded);
}

flags = merge_flag_lists (expanded, type);
g_list_free (expanded);

return flags;
}

static GList *
add_env_variable_to_list (GList *list, const gchar *env)
{
gchar **values;
gint i;

values = g_strsplit (env, G_SEARCHPATH_SEPARATOR_S, 0);
for (i = 0; values[i] != NULL; i++)
{
list = g_list_append (list, g_strdup (values[i]));
}
g_strfreev (values);

return list;
}

static void
verify_package (Package *pkg)
{
GList *requires = NULL;
GList *conflicts = NULL;
GList *system_directories = NULL;
GList *iter;
GList *requires_iter;
GList *conflicts_iter;
GList *system_dir_iter = NULL;
int count;
const gchar *search_path;

/* Be sure we have the required fields */

if (pkg->key == NULL)
{
fprintf (stderr,
"Internal pkg-config error, package with no key, please file a bug report\n");
exit (1);
}

if (pkg->name == NULL)
{
verbose_error ("Package '%s' has no Name: field\n",
pkg->key);
exit (1);
}

if (pkg->version == NULL)
{
verbose_error ("Package '%s' has no Version: field\n",
pkg->key);
exit (1);
}

if (pkg->description == NULL)
{
verbose_error ("Package '%s' has no Description: field\n",
pkg->key);
exit (1);
}

/* Make sure we have the right version for all requirements */

iter = pkg->requires_private;

while (iter != NULL)
{
Package *req = iter->data;
RequiredVersion *ver = NULL;

if (pkg->required_versions)
ver = g_hash_table_lookup (pkg->required_versions,
req->key);

if (ver)
{
if (!version_test (ver->comparison, req->version, ver->version))
{
verbose_error ("Package '%s' requires '%s %s %s' but version of %s is %s\n",
pkg->key, req->key,
comparison_to_str (ver->comparison),
ver->version,
req->key,
req->version);
if (req->url)
verbose_error ("You may find new versions of %s at %s\n",
req->name, req->url);

exit (1);
}
}

iter = g_list_next (iter);
}

/* Make sure we didn't drag in any conflicts via Requires
* (inefficient algorithm, who cares)
*/
recursive_fill_list (pkg, TRUE, &requires);
conflicts = pkg->conflicts;

requires_iter = requires;
while (requires_iter != NULL)
{
Package *req = requires_iter->data;

conflicts_iter = conflicts;

while (conflicts_iter != NULL)
{
RequiredVersion *ver = conflicts_iter->data;

if (strcmp (ver->name, req->key) == 0 &&
version_test (ver->comparison,
req->version,
ver->version))
{
verbose_error ("Version %s of %s creates a conflict.\n"
"(%s %s %s conflicts with %s %s)\n",
req->version, req->key,
ver->name,
comparison_to_str (ver->comparison),
ver->version ? ver->version : "(any)",
ver->owner->key,
ver->owner->version);

exit (1);
}

conflicts_iter = g_list_next (conflicts_iter);
}

requires_iter = g_list_next (requires_iter);
}

g_list_free (requires);

/* We make a list of system directories that gcc expects so we can remove
* them.
*/

search_path = g_getenv ("PKG_CONFIG_SYSTEM_INCLUDE_PATH");

if (search_path == NULL)
{
search_path = PKG_CONFIG_SYSTEM_INCLUDE_PATH;
}

system_directories = add_env_variable_to_list (system_directories, search_path);

search_path = g_getenv ("C_INCLUDE_PATH");
if (search_path != NULL)
{
system_directories = add_env_variable_to_list (system_directories, search_path);
}

search_path = g_getenv ("CPLUS_INCLUDE_PATH");
if (search_path != NULL)
{
system_directories = add_env_variable_to_list (system_directories, search_path);
}

count = 0;
for (iter = pkg->cflags; iter != NULL; iter = g_list_next (iter))
{
gint offset = 0;
Flag *flag = iter->data;

if (!(flag->type & CFLAGS_I))
continue;

/* we put things in canonical -I/usr/include (vs. -I /usr/include) format,
* but if someone changes it later we may as well be robust
*/
if (((strncmp (flag->arg, "-I", 2) == 0) && (offset = 2))||
((strncmp (flag->arg, "-I ", 3) == 0) && (offset = 3)))
{
if (offset == 0)
{
iter = iter->next;
continue;
}

system_dir_iter = system_directories;
while (system_dir_iter != NULL)
{
if (strcmp (system_dir_iter->data,
((char*)flag->arg) + offset) == 0)
{
debug_spew ("Package %s has %s in Cflags\n",
pkg->key, (gchar *)flag->arg);
if (g_getenv ("PKG_CONFIG_ALLOW_SYSTEM_CFLAGS") == NULL)
{
debug_spew ("Removing %s from cflags for %s\n",
flag->arg, pkg->key);
++count;
iter->data = NULL;

break;
}
}
system_dir_iter = system_dir_iter->next;
}
}
}

while (count)
{
pkg->cflags = g_list_remove (pkg->cflags, NULL);
--count;
}

g_list_foreach (system_directories, (GFunc) g_free, NULL);
g_list_free (system_directories);

system_directories = NULL;

search_path = g_getenv ("PKG_CONFIG_SYSTEM_LIBRARY_PATH");

if (search_path == NULL)
{
search_path = PKG_CONFIG_SYSTEM_LIBRARY_PATH;
}

system_directories = add_env_variable_to_list (system_directories, search_path);

count = 0;
for (iter = pkg->libs; iter != NULL; iter = g_list_next (iter))
{
GList *system_dir_iter = system_directories;
Flag *flag = iter->data;

if (!(flag->type & LIBS_L))
continue;

while (system_dir_iter != NULL)
{
gboolean is_system = FALSE;
const char *linker_arg = flag->arg;
const char *system_libpath = system_dir_iter->data;

if (strncmp (linker_arg, "-L ", 3) == 0 &&
strcmp (linker_arg + 3, system_libpath) == 0)
is_system = TRUE;
else if (strncmp (linker_arg, "-L", 2) == 0 &&
strcmp (linker_arg + 2, system_libpath) == 0)
is_system = TRUE;
if (is_system)
{
debug_spew ("Package %s has -L %s in Libs\n",
pkg->key, system_libpath);
if (g_getenv ("PKG_CONFIG_ALLOW_SYSTEM_LIBS") == NULL)
{
iter->data = NULL;
++count;
debug_spew ("Removing -L %s from libs for %s\n",
system_libpath, pkg->key);
break;
}
}
system_dir_iter = system_dir_iter->next;
}
}
g_list_free (system_directories);

while (count)
{
pkg->libs = g_list_remove (pkg->libs, NULL);
--count;
}
}

/* Create a merged list of required packages and retrieve the flags from them.
* Strip the duplicates from the flags list. The sorting and stripping can be
* done in one of two ways: packages sorted by position in the pkg-config path
* and stripping done from the beginning of the list, or packages sorted from
* most dependent to least dependent and stripping from the end of the list.
* The former is done for -I/-L flags, and the latter for all others.
*/
static char *
get_multi_merged (GList *pkgs, FlagType type, gboolean in_path_order,
gboolean include_private)
{
GList *list;
char *retval;

list = fill_list (pkgs, type, in_path_order, include_private);
list = flag_list_strip_duplicates (list);
retval = flag_list_to_string (list);
g_list_free (list);

return retval;
}

char *
packages_get_flags (GList *pkgs, FlagType flags)
{
GString *str;
char *cur;

str = g_string_new (NULL);

/* sort packages in path order for -L/-I, dependency order otherwise */
if (flags & CFLAGS_OTHER)
{
cur = get_multi_merged (pkgs, CFLAGS_OTHER, FALSE, TRUE);
debug_spew ("adding CFLAGS_OTHER string \"%s\"\n", cur);
g_string_append (str, cur);
g_free (cur);
}
if (flags & CFLAGS_I)
{
cur = get_multi_merged (pkgs, CFLAGS_I, TRUE, TRUE);
debug_spew ("adding CFLAGS_I string \"%s\"\n", cur);
g_string_append (str, cur);
g_free (cur);
}
if (flags & LIBS_L)
{
cur = get_multi_merged (pkgs, LIBS_L, TRUE, !ignore_private_libs);
debug_spew ("adding LIBS_L string \"%s\"\n", cur);
g_string_append (str, cur);
g_free (cur);
}
if (flags & (LIBS_OTHER | LIBS_l))
{
cur = get_multi_merged (pkgs, flags & (LIBS_OTHER | LIBS_l), FALSE,
!ignore_private_libs);
debug_spew ("adding LIBS_OTHER | LIBS_l string \"%s\"\n", cur);
g_string_append (str, cur);
g_free (cur);
}

debug_spew ("returning flags string \"%s\"\n", str->str);
return g_string_free (str, FALSE);
}

void
define_global_variable (const char *varname,
const char *varval)
{
if (globals == NULL)
globals = g_hash_table_new (g_str_hash, g_str_equal);

if (g_hash_table_lookup (globals, varname))
{
verbose_error ("Variable '%s' defined twice globally\n", varname);
exit (1);
}

g_hash_table_insert (globals, g_strdup (varname), g_strdup (varval));

debug_spew ("Global variable definition '%s' = '%s'\n",
varname, varval);
}

char *
package_get_var (Package *pkg,
const char *var)
{
char *varval = NULL;

if (globals)
varval = g_strdup (g_hash_table_lookup (globals, var));

if (varval == NULL && pkg->vars)
varval = g_strdup (g_hash_table_lookup (pkg->vars, var));

/* Magic "pcfiledir" variable */
if (varval == NULL && pkg->pcfiledir && strcmp (var, "pcfiledir") == 0)
varval = g_strdup (pkg->pcfiledir);

return varval;
}

char *
packages_get_var (GList *pkgs,
const char *varname)
{
GList *tmp;
GString *str;
char *retval;

str = g_string_new ("");

tmp = pkgs;
while (tmp != NULL)
{
Package *pkg = tmp->data;
char *var;

var = package_get_var (pkg, varname);

if (var)
{
g_string_append (str, var);
g_string_append_c (str, ' ');
g_free (var);
}

tmp = g_list_next (tmp);
}

/* chop last space */
if (str->len > 0)
str->str[str->len - 1] = '\0';
retval = str->str;
g_string_free (str, FALSE);

return retval;
}



/* Stolen verbatim from rpm/lib/misc.c
RPM is Copyright (c) 1998 by Red Hat Software, Inc.,
and may be distributed under the terms of the GPL and LGPL.
*/
/* compare alpha and numeric segments of two versions */
/* return 1: a is newer than b */
/* 0: a and b are the same version */
/* -1: b is newer than a */
static int rpmvercmp(const char * a, const char * b) {
char oldch1, oldch2;
char * str1, * str2;
char * one, * two;
int rc;
int isnum;

/* easy comparison to see if versions are identical */
if (!strcmp(a, b)) return 0;

str1 = g_alloca(strlen(a) + 1);
str2 = g_alloca(strlen(b) + 1);

strcpy(str1, a);
strcpy(str2, b);

one = str1;
two = str2;

/* loop through each version segment of str1 and str2 and compare them */
while (*one && *two) {
while (*one && !isalnum((guchar)*one)) one++;
while (*two && !isalnum((guchar)*two)) two++;

/* If we ran to the end of either, we are finished with the loop */
if (!(*one && *two)) break;

str1 = one;
str2 = two;

/* grab first completely alpha or completely numeric segment */
/* leave one and two pointing to the start of the alpha or numeric */
/* segment and walk str1 and str2 to end of segment */
if (isdigit((guchar)*str1)) {
while (*str1 && isdigit((guchar)*str1)) str1++;
while (*str2 && isdigit((guchar)*str2)) str2++;
isnum = 1;
} else {
while (*str1 && isalpha((guchar)*str1)) str1++;
while (*str2 && isalpha((guchar)*str2)) str2++;
isnum = 0;
}

/* save character at the end of the alpha or numeric segment */
/* so that they can be restored after the comparison */
oldch1 = *str1;
*str1 = '\0';
oldch2 = *str2;
*str2 = '\0';

/* take care of the case where the two version segments are */
/* different types: one numeric and one alpha */
if (one == str1) return -1; /* arbitrary */
/* XXX See patch #60884 (and details) from bugzilla #50977. */
if (two == str2) return (isnum ? 1 : -1);

if (isnum) {
/* this used to be done by converting the digit segments */
/* to ints using atoi() - it's changed because long */
/* digit segments can overflow an int - this should fix that. */

/* throw away any leading zeros - it's a number, right? */
while (*one == '0') one++;
while (*two == '0') two++;

/* whichever number has more digits wins */
if (strlen(one) > strlen(two)) return 1;
if (strlen(two) > strlen(one)) return -1;
}

/* strcmp will return which one is greater - even if the two */
/* segments are alpha or if they are numeric. don't return */
/* if they are equal because there might be more segments to */
/* compare */
rc = strcmp(one, two);
if (rc) return rc;

/* restore character that was replaced by null above */
*str1 = oldch1;
one = str1;
*str2 = oldch2;
two = str2;
}

/* this catches the case where all numeric and alpha segments have */
/* compared identically but the segment sepparating characters were */
/* different */
if ((!*one) && (!*two)) return 0;

/* whichever version still has characters left over wins */
if (!*one) return -1; else return 1;
}

int
compare_versions (const char * a, const char *b)
{
return rpmvercmp (a, b);
}

gboolean
version_test (ComparisonType comparison,
const char *a,
const char *b)
{
switch (comparison)
{
case LESS_THAN:
return compare_versions (a, b) < 0;
break;

case GREATER_THAN:
return compare_versions (a, b) > 0;
break;

case LESS_THAN_EQUAL:
return compare_versions (a, b) <= 0;
break;

case GREATER_THAN_EQUAL:
return compare_versions (a, b) >= 0;
break;

case EQUAL:
return compare_versions (a, b) == 0;
break;

case NOT_EQUAL:
return compare_versions (a, b) != 0;
break;

case ALWAYS_MATCH:
return TRUE;
break;

default:
g_assert_not_reached ();
break;
}

return FALSE;
}

const char *
comparison_to_str (ComparisonType comparison)
{
switch (comparison)
{
case LESS_THAN:
return "<";
break;

case GREATER_THAN:
return ">";
break;

case LESS_THAN_EQUAL:
return "<=";
break;

case GREATER_THAN_EQUAL:
return ">=";
break;

case EQUAL:
return "=";
break;

case NOT_EQUAL:
return "!=";
break;

case ALWAYS_MATCH:
return "(any)";
break;

default:
g_assert_not_reached ();
break;
}

return "???";
}

static void
max_len_foreach (gpointer key, gpointer value, gpointer data)
{
int *mlen = data;

*mlen = MAX (*mlen, strlen (key));
}

static void
packages_foreach (gpointer key, gpointer value, gpointer data)
{
Package *pkg = get_package (key);

if (pkg != NULL)
{
char *pad;

pad = g_strnfill (GPOINTER_TO_INT (data) - strlen (pkg->key), ' ');

printf ("%s%s%s - %s\n",
pkg->key, pad, pkg->name, pkg->description);

g_free (pad);
}
}

void
print_package_list (void)
{
int mlen = 0;

ignore_requires = TRUE;
ignore_requires_private = TRUE;

g_hash_table_foreach (locations, max_len_foreach, &mlen);
g_hash_table_foreach (locations, packages_foreach, GINT_TO_POINTER (mlen + 1));
}

void
enable_private_libs(void)
{
ignore_private_libs = FALSE;
}

void
disable_private_libs(void)
{
ignore_private_libs = TRUE;
}

void
enable_requires(void)
{
ignore_requires = FALSE;
}

void
disable_requires(void)
{
ignore_requires = TRUE;
}

void
enable_requires_private(void)
{
ignore_requires_private = FALSE;
}

void
disable_requires_private(void)
{
ignore_requires_private = TRUE;
}