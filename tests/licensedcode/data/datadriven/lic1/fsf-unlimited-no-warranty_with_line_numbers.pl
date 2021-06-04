#!/usr/bin/perl -w
# -*- perl -*-
# automake.  Generated from automake.in by configure.

eval 'case $# in 0) exec /usr/bin/perl -S "$0";; *) exec /usr/bin/perl -S "$0" "$@";; esac'
    if 0;

# automake - create Makefile.in from Makefile.am
# Copyright (C) 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002
# Free Software Foundation, Inc.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.

# Originally written by David Mackenzie <djm@gnu.ai.mit.edu>.
# Perl reimplementation by Tom Tromey <tromey@redhat.com>.

package Language;

BEGIN
{
  my $prefix = "/usr";
  my $perllibdir = $ENV{'perllibdir'} || "/usr/share/automake-1.6";
  unshift @INC, "$perllibdir";
}

use Automake::Struct;
struct (# Short name of the language (c, f77...).
        'name' => "\$",
        # Nice name of the language (C, Fortran 77...).
        'Name' => "\$",

    # List of configure variables which must be defined.
    'config_vars' => '@',

        'ansi'    => "\$",
    # `pure' is `1' or `'.  A `pure' language is one where, if
    # all the files in a directory are of that language, then we
    # do not require the C compiler or any code to call it.
    'pure'   => "\$",

    'autodep' => "\$",

    # Name of the compiling variable (COMPILE).
        'compiler'  => "\$",
        # Content of the compiling variable.
        'compile'  => "\$",
        # Flag to require compilation without linking (-c).
        'compile_flag' => "\$",
        'extensions'      => '@',
        'flags' => "\$",
    # Should the flag be defined as a configure variable.
    # Defaults to true.  FIXME: this should go away once
    # we move to autoconf tracing.
    'define_flag' => "\$",

    # The file to use when generating rules for this language.
    # The default is 'depend2'.
    'rule_file' => "\$",

        # Name of the linking variable (LINK).
        'linker' => "\$",
        # Content of the linking variable.
        'link' => "\$",

        # Name of the linker variable (LD).
        'lder' => "\$",
        # Content of the linker variable ($(CC)).
        'ld' => "\$",

        # Flag to specify the output file (-o).
        'output_flag' => "\$",
        '_finish' => "\$",

    # This is a subroutine which is called whenever we finally
    # determine the context in which a source file will be
    # compiled.
    '_target_hook' => "\$");


sub finish ($)
{
  my ($self) = @_;
  if (defined $self->_finish)
    {
      &{$self->_finish} ();
    }
}

sub target_hook ($$$$)
{
    my ($self) = @_;
    if (defined $self->_target_hook)
    {
    &{$self->_target_hook} (@_);
    }
}

package Automake;

use strict 'vars', 'subs';
use Automake::General;
use Automake::XFile;
use File::Basename;
use Carp;

## ----------- ##
## Constants.  ##
## ----------- ##

# Parameters set by configure.  Not to be changed.  NOTE: assign
# VERSION as string so that eg version 0.30 will print correctly.
my $VERSION = "1.6.3";
my $PACKAGE = "automake";
my $prefix = "/usr";
my $libdir = "/usr/share/automake-1.6";

# String constants.
my $IGNORE_PATTERN = '^\s*##([^#\n].*)?\n';
my $WHITE_PATTERN = '^\s*$';
my $COMMENT_PATTERN = '^#';
my $TARGET_PATTERN='[$a-zA-Z_.@][-.a-zA-Z0-9_(){}/$+@]*';
# A rule has three parts: a list of targets, a list of dependencies,
# and optionally actions.
my $RULE_PATTERN =
  "^($TARGET_PATTERN(?:(?:\\\\\n|\\s)+$TARGET_PATTERN)*) *:([^=].*|)\$";

my $SUFFIX_RULE_PATTERN = '^(\.[a-zA-Z0-9_(){}$+@]+)(\.[a-zA-Z0-9_(){}$+@]+)$';
# Only recognize leading spaces, not leading tabs.  If we recognize
# leading tabs here then we need to make the reader smarter, because
# otherwise it will think rules like `foo=bar; \' are errors.
my $MACRO_PATTERN = '^[A-Za-z0-9_@]+$';
my $ASSIGNMENT_PATTERN = '^ *([^ \t=:+]*)\s*([:+]?)=\s*(.*)$';
# This pattern recognizes a Gnits version id and sets $1 if the
# release is an alpha release.  We also allow a suffix which can be
# used to extend the version number with a "fork" identifier.
my $GNITS_VERSION_PATTERN = '\d+\.\d+([a-z]|\.\d+)?(-[A-Za-z0-9]+)?';
my $IF_PATTERN =          '^if\s+(!?)\s*([A-Za-z][A-Za-z0-9_]*)\s*(?:#.*)?$';
my $ELSE_PATTERN =   '^else(?:\s+(!?)\s*([A-Za-z][A-Za-z0-9_]*))?\s*(?:#.*)?$';
my $ENDIF_PATTERN = '^endif(?:\s+(!?)\s*([A-Za-z][A-Za-z0-9_]*))?\s*(?:#.*)?$';
my $PATH_PATTERN='(\w|[/.-])+';
# This will pass through anything not of the prescribed form.
my $INCLUDE_PATTERN = ('^include\s+'
               . '((\$\(top_srcdir\)/' . $PATH_PATTERN . ')'
               . '|(\$\(srcdir\)/' . $PATH_PATTERN . ')'
               . '|([^/\$]' . $PATH_PATTERN. '))\s*(#.*)?$');

# Some regular expressions.  One reason to put them here is that it
# makes indentation work better in Emacs.
my $AC_CONFIG_AUX_DIR_PATTERN = 'AC_CONFIG_AUX_DIR\(([^)]+)\)';
my $AM_INIT_AUTOMAKE_PATTERN = 'AM_INIT_AUTOMAKE\([^,]*,([^,)]+)[,)]';
my $AC_INIT_PATTERN = 'AC_INIT\([^,]*,([^,)]+)[,)]';
my $AM_PACKAGE_VERSION_PATTERN = '^\s*\[?([^]\s]+)\]?\s*$';

# This handles substitution references like ${foo:.a=.b}.
my $SUBST_REF_PATTERN = "^([^:]*):([^=]*)=(.*)\$";

# Note that there is no AC_PATH_TOOL.  But we don't really care.
my $AC_CHECK_PATTERN = 'AC_(CHECK|PATH)_(PROG|PROGS|TOOL)\(\[?(\w+)';
my $AM_MISSING_PATTERN = 'AM_MISSING_PROG\(\[?(\w+)';
# Just check for alphanumeric in AC_SUBST.  If you do AC_SUBST(5),
# then too bad.
my $AC_SUBST_PATTERN = 'AC_SUBST\(\[?(\w+)';
my $AM_CONDITIONAL_PATTERN = 'AM_CONDITIONAL\(\[?(\w+)';
# Match `-d' as a command-line argument in a string.
my $DASH_D_PATTERN = "(^|\\s)-d(\\s|\$)";
# Directories installed during 'install-exec' phase.
my $EXEC_DIR_PATTERN =
    '^(?:bin|sbin|libexec|sysconf|localstate|lib|pkglib|.*exec.*)$'; #'

# Constants to define the "strictness" level.
use constant FOREIGN => 0;
use constant GNU     => 1;
use constant GNITS   => 2;

# Values for AC_CANONICAL_*
use constant AC_CANONICAL_HOST   => 1;
use constant AC_CANONICAL_SYSTEM => 2;

# Values indicating when something should be cleaned.  Right now we
# only need to handle `mostly'- and `dist'-clean; add more as
# required.
use constant MOSTLY_CLEAN => 0;
use constant DIST_CLEAN   => 1;

# Libtool files.
my @libtool_files = qw(ltmain.sh config.guess config.sub);
# ltconfig appears here for compatibility with old versions of libtool.
my @libtool_sometimes = qw(ltconfig ltcf-c.sh ltcf-cxx.sh ltcf-gcj.sh);

# Commonly found files we look for and automatically include in
# DISTFILES.
my @common_files =
    (qw(ABOUT-GNU ABOUT-NLS AUTHORS BACKLOG COPYING COPYING.DOC COPYING.LIB
    ChangeLog INSTALL NEWS README THANKS TODO acinclude.m4
    ansi2knr.1 ansi2knr.c compile config.guess config.rpath config.sub
    configure configure.ac configure.in depcomp elisp-comp
    install-sh libversion.in mdate-sh missing mkinstalldirs
    py-compile texinfo.tex ylwrap),
     @libtool_files, @libtool_sometimes);

# Commonly used files we auto-include, but only sometimes.
my @common_sometimes =
    qw(aclocal.m4 acconfig.h config.h.top config.h.bot stamp-vti);

# Standard directories from the GNU Coding Standards, and additional
# pkg* directories from Automake.  Stored in a hash for fast member check.
my %standard_prefix =
    map { $_ => 1 } (qw(bin data exec include info lib libexec lisp
            localstate man man1 man2 man3 man4 man5 man6
            man7 man8 man9 oldinclude pkgdatadir
            pkgincludedir pkglibdir sbin sharedstate
            sysconf));

# Copyright on generated Makefile.ins.
my $gen_copyright = "\
# Copyright 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002
# Free Software Foundation, Inc.
# This Makefile.in is free software; the Free Software Foundation
# gives unlimited permission to copy and/or distribute it,
# with or without modifications, as long as this notice is preserved.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, to the extent permitted by law; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.
";

# These constants are returned by lang_*_rewrite functions.
# LANG_SUBDIR means that the resulting object file should be in a
# subdir if the source file is.  In this case the file name cannot
# have `..' components.
my $LANG_IGNORE = 0;
my $LANG_PROCESS = 1;
my $LANG_SUBDIR = 2;

# These are used when keeping track of whether an object can be built
# by two different paths.
my $COMPILE_LIBTOOL = 1;
my $COMPILE_ORDINARY = 2;

# Map from obsolete macros to hints for new macros.
# If you change this, change the corresponding list in aclocal.in.
# FIXME: should just put this into a single file.
my %obsolete_macros =
    (
     'AC_FEATURE_CTYPE'     => "use `AC_HEADER_STDC'",
     'AC_FEATURE_ERRNO'     => "add `strerror' to `AC_REPLACE_FUNCS(...)'",
     'AC_FEATURE_EXIT'      => '',
     'AC_SYSTEM_HEADER'     => '',

     # Note that we do not handle this one, because it is still run
     # from AM_CONFIG_HEADER.  So we deal with it specially in
     # &scan_autoconf_files.
     # 'AC_CONFIG_HEADER'   => "use `AM_CONFIG_HEADER'",

     'fp_C_PROTOTYPES'      => "use `AM_C_PROTOTYPES'",
     'fp_PROG_CC_STDC'      => "use `AM_PROG_CC_STDC'",
     'fp_PROG_INSTALL'      => "use `AC_PROG_INSTALL'",
     'fp_WITH_DMALLOC'      => "use `AM_WITH_DMALLOC'",
     'fp_WITH_REGEX'        => "use `AM_WITH_REGEX'",
     'gm_PROG_LIBTOOL'      => "use `AM_PROG_LIBTOOL'",
     'jm_MAINTAINER_MODE'   => "use `AM_MAINTAINER_MODE'",
     'md_TYPE_PTRDIFF_T'    => "add `ptrdiff_t' to `AC_CHECK_TYPES(...)'",
     'ud_PATH_LISPDIR'      => "use `AM_PATH_LISPDIR'",
     'ud_GNU_GETTEXT'       => "use `AM_GNU_GETTEXT'",

     # Now part of autoconf proper, under a different name.
     'fp_FUNC_FNMATCH'      => "use `AC_FUNC_FNMATCH'",
     'AM_SANITY_CHECK_CC'   => "automatically done by `AC_PROG_CC'",
     'AM_PROG_INSTALL'      => "use `AC_PROG_INSTALL'",
     'AM_EXEEXT'        => "automatically done by `AC_PROG_(CC|CXX|F77)'",
     'AM_CYGWIN32'      => "use `AC_CYGWIN'",
     'AM_MINGW32'       => "use `AC_MINGW32'",
     'AM_FUNC_MKTIME'       => "use `AC_FUNC_MKTIME'",
     );

# Regexp to match the above macros.
my $obsolete_rx = '\b(' . join ('|', keys %obsolete_macros) . ')\b';



## ---------------------------------- ##
## Variables related to the options.  ##
## ---------------------------------- ##

# TRUE if we should always generate Makefile.in.
my $force_generation = 1;

# Strictness level as set on command line.
my $default_strictness = GNU;

# Name of strictness level, as set on command line.
my $default_strictness_name = 'gnu';

# This is TRUE if automatic dependency generation code should be
# included in generated Makefile.in.
my $cmdline_use_dependencies = 1;

# This holds our (eventual) exit status.  We don't actually exit until
# we have processed all input files.
my $exit_status = 0;

# From the Perl manual.
my $symlink_exists = (eval 'symlink ("", "");', $@ eq '');

# TRUE if missing standard files should be installed.
my $add_missing = 0;

# TRUE if we should copy missing files; otherwise symlink if possible.
my $copy_missing = 0;

# TRUE if we should always update files that we know about.
my $force_missing = 0;


## ---------------------------------------- ##
## Variables filled during files scanning.  ##
## ---------------------------------------- ##

# Name of the top autoconf input: `configure.ac' or `configure.in'.
my $configure_ac = '';

# Files found by scanning configure.ac for LIBOBJS.
my %libsources = ();

# True if AM_C_PROTOTYPES appears in configure.ac.
my $am_c_prototypes = 0;

# Names used in AC_CONFIG_HEADER call.
my @config_headers = ();
# Where AC_CONFIG_HEADER appears.
my $config_header_location;

# Directory where output files go.  Actually, output files are
# relative to this directory.
my $output_directory;

# List of Makefile.am's to process, and their corresponding outputs.
my @input_files = ();
my %output_files = ();

# Complete list of Makefile.am's that exist.
my @configure_input_files = ();

# List of files in AC_CONFIG_FILES/AC_OUTPUT without Makefile.am's,
# and their outputs.
my @other_input_files = ();
# Where the last AC_CONFIG_FILES/AC_OUTPUT appears.
my $ac_config_files_location;

# List of directories to search for configure-required files.  This
# can be set by AC_CONFIG_AUX_DIR.
my @config_aux_path = qw(. .. ../..);
my $config_aux_dir = '';
my $config_aux_dir_set_in_configure_in = 0;

# Whether AM_GNU_GETTEXT has been seen in configure.ac.
my $seen_gettext = 0;
# Whether AM_GNU_GETTEXT([external]) is used.
my $seen_gettext_external = 0;
# Where AM_GNU_GETTEXT appears.
my $ac_gettext_location;

# TRUE if AC_PROG_LEX or AM_PROG_LEX were seen.
my $seen_prog_lex = 0;

# TRUE if we've seen AC_CANONICAL_(HOST|SYSTEM).
my $seen_canonical = 0;
my $canonical_location;

# Where AC_PROG_LIBTOOL appears.
my $seen_libtool;

# Where AM_MAINTAINER_MODE appears.
my $seen_maint_mode;

# Actual version we've seen.
my $package_version = '';

# Where version is defined.
my $package_version_location;

# Where AM_PATH_LISPDIR appears.
my $am_lispdir_location;

# Where AM_PATH_PYTHON appears.
my $pythondir_location;

# TRUE if we've seen AC_ENABLE_MULTILIB.
my $seen_multilib = 0;

# TRUE if we've seen AM_PROG_CC_C_O
my $seen_cc_c_o = 0;

# Where AM_INIT_AUTOMAKE is called;
my $seen_init_automake = 0;

# TRUE if we've seen AM_AUTOMAKE_VERSION.
my $seen_automake_version = 0;

# Hash table of discovered configure substitutions.  Keys are names,
# values are `FILE:LINE' strings which are used by error message
# generation.
my %configure_vars = ();

# This is used to keep track of which variable definitions we are
# scanning.  It is only used in certain limited ways, but it has to be
# global.  It is declared just for documentation purposes.
my %vars_scanned = ();

# TRUE if --cygnus seen.
my $cygnus_mode = 0;

# Hash table of AM_CONDITIONAL variables seen in configure.
my %configure_cond = ();

# This maps extensions onto language names.
my %extension_map = ();

# List of the DIST_COMMON files we discovered while reading
# configure.in
my $configure_dist_common = '';

# This maps languages names onto objects.
my %languages = ();

# List of targets we must always output.
# FIXME: Complete, and remove falsely required targets.
my %required_targets =
  (
   'all'          => 1,
   'dvi'      => 1,
   'info'     => 1,
   'install-info' => 1,
   'install'      => 1,
   'install-data' => 1,
   'install-exec' => 1,
   'uninstall'    => 1,

   # FIXME: Not required, temporary hacks.
   # Well, actually they are sort of required: the -recursive
   # targets will run them anyway...
   'dvi-am'          => 1,
   'info-am'         => 1,
   'install-data-am' => 1,
   'install-exec-am' => 1,
   'installcheck-am' => 1,
   'uninstall-am' => 1,

   'install-man' => 1,
  );

# This is set to 1 when Automake needs to be run again.
# (For instance, this happens when an auxiliary file such as
# depcomp is added after the toplevel Makefile.in -- which
# should distribute depcomp -- has been generated.)
my $automake_needs_to_reprocess_all_files = 0;

# Options set via AM_INIT_AUTOMAKE.
my $global_options = '';

# If a file name appears as a key in this hash, then it has already
# been checked for.  This variable is local to the "require file"
# functions.
my %require_file_found = ();


################################################################

## ------------------------------------------ ##
## Variables reset by &initialize_per_input.  ##
## ------------------------------------------ ##

# Basename and relative dir of the input file.
my $am_file_name;
my $am_relative_dir;

# Same but wrt Makefile.in.
my $in_file_name;
my $relative_dir;

# These two variables are used when generating each Makefile.in.
# They hold the Makefile.in until it is ready to be printed.
my $output_rules;
my $output_vars;
my $output_trailer;
my $output_all;
my $output_header;

# Suffixes found during a run.
my @suffixes;

# Handling the variables.
#
# For a $VAR:
# - $var_value{$VAR}{$COND} is its value associated to $COND,
# - $var_location{$VAR} is where it was defined,
# - $var_comment{$VAR} are the comments associated to it.
# - $var_type{$VAR} is how it has been defined (`', `+', or `:'),
# - $var_is_am{$VAR} is true if the variable is owned by Automake.
my %var_value;
my %var_location;
my %var_comment;
my %var_type;
my %var_is_am;

# This holds a 1 if a particular variable was examined.
my %content_seen;

# This holds the names which are targets.  These also appear in
# %contents.
my %targets;

# Same as %VAR_VALUE, but for targets.
my %target_conditional;

# This is the conditional stack.
my @cond_stack;

# This holds the set of included files.
my @include_stack;

# This holds a list of directories which we must create at `dist'
# time.  This is used in some strange scenarios involving weird
# AC_OUTPUT commands.
my %dist_dirs;

# List of dependencies for the obvious targets.
my @all;
my @check;
my @check_tests;

# Holds the dependencies of targets which dependencies are factored.
# Typically, `.PHONY' will appear in plenty of *.am files, but must
# be output once.  Arguably all pure dependencies could be subject
# to this factorization, but it is not unpleasant to have paragraphs
# in Makefile: keeping related stuff altogether.
my %dependencies;

# Holds the factored actions.  Tied to %DEPENDENCIES, i.e., filled
# only when keys exists in %DEPENDENCIES.
my %actions;

# A list of files deleted by `maintainer-clean'.
my @maintainer_clean_files;

# Keys in this hash table are object files or other files in
# subdirectories which need to be removed.  This only holds files
# which are created by compilations.  The value in the hash indicates
# when the file should be removed.
my %compile_clean_files;

# Keys in this hash table are directories where we expect to build a
# libtool object.  We use this information to decide what directories
# to delete.
my %libtool_clean_directories;

# Value of `$(SOURCES)', used by tags.am.
my @sources;
# Sources which go in the distribution.
my @dist_sources;

# This hash maps object file names onto their corresponding source
# file names.  This is used to ensure that each object is created
# by a single source file.
my %object_map;

# This hash maps object file names onto an integer value representing
# whether this object has been built via ordinary compilation or
# libtool compilation (the COMPILE_* constants).
my %object_compilation_map;


# This keeps track of the directories for which we've already
# created `.dirstamp' code.
my %directory_map;

# All .P files.
my %dep_files;

# Strictness levels.
my $strictness;
my $strictness_name;

# Options from AUTOMAKE_OPTIONS.
my %options;

# Whether or not dependencies are handled.  Can be further changed
# in handle_options.
my $use_dependencies;

# This is a list of all targets to run during "make dist".
my @dist_targets;

# Keys in this hash are the basenames of files which must depend on
# ansi2knr.  Values are either the empty string, or the directory in
# which the ANSI source file appears; the directory must have a
# trailing `/'.
my %de_ansi_files;

# This maps the source extension of a suffix rule to its
# corresponding output extension.
# FIXME: because this hash maps one input extension to one output
# extension, Automake cannot handle two suffix rules with the same
# input extension.
my %suffix_rules;

# This is the name of the redirect `all' target to use.
my $all_target;

# This keeps track of which extensions we've seen (that we care
# about).
my %extension_seen;

# This is random scratch space for the language finish functions.
# Don't randomly overwrite it; examine other uses of keys first.
my %language_scratch;

# We keep track of which objects need special (per-executable)
# handling on a per-language basis.
my %lang_specific_files;

# This is set when `handle_dist' has finished.  Once this happens,
# we should no longer push on dist_common.
my $handle_dist_run;

# Used to store a set of linkers needed to generate the sources currently
# under consideration.
my %linkers_used;

# True if we need `LINK' defined.  This is a hack.
my $need_link;

# This is the list of such variables to output.
# FIXME: Might be useless actually.
my @var_list;

# Was get_object_extension run?
# FIXME: This is a hack. a better switch should be found.
my $get_object_extension_was_run;

# Contains a stack of `from' parts of variable substitutions currently in
# force.
my @substfroms;

# Contains a stack of `to' parts of variable substitutions currently in
# force.
my @substtos;

# This keeps track of all variables defined by subobjname.
# The value stored is the variable names.
# The key has the form "(COND1)VAL1(COND2)VAL2..." where VAL1 and VAL2
# are the values of the variable for condition COND1 and COND2.
my %subobjvar = ();

## --------------------------------- ##
## Forward subroutine declarations.  ##
## --------------------------------- ##
sub register_language (%);
sub file_contents_internal ($$%);
sub define_objects_from_sources ($$$$$$$);


# &initialize_per_input ()
# ------------------------
# (Re)-Initialize per-Makefile.am variables.
sub initialize_per_input ()
{
    $am_file_name = '';
    $am_relative_dir = '';

    $in_file_name = '';
    $relative_dir = '';

    $output_rules = '';
    $output_vars = '';
    $output_trailer = '';
    $output_all = '';
    $output_header = '';

    @suffixes = ();

    %var_value = ();
    %var_location = ();
    %var_comment = ();
    %var_type = ();
    %var_is_am = ();

    %content_seen = ();

    %targets = ();

    %target_conditional = ();

    @cond_stack = ();

    @include_stack = ();

    %dist_dirs = ();

    @all = ();
    @check = ();
    @check_tests = ();

    %dependencies =
      (
       # Texinfoing.
       'dvi'      => [],
       'dvi-am'   => [],
       'info'     => [],
       'info-am'  => [],

       # Installing/uninstalling.
       'install-data-am'      => [],
       'install-exec-am'      => [],
       'uninstall-am'         => [],

       'install-man'          => [],
       'uninstall-man'        => [],

       'install-info'         => [],
       'install-info-am'      => [],
       'uninstall-info'       => [],

       'installcheck-am'      => [],

       # Cleaning.
       'clean-am'             => [],
       'mostlyclean-am'       => [],
       'maintainer-clean-am'  => [],
       'distclean-am'         => [],
       'clean'                => [],
       'mostlyclean'          => [],
       'maintainer-clean'     => [],
       'distclean'            => [],

       # Tarballing.
       'dist-all'             => [],

       # Phoning.
       '.PHONY'               => []
      );
    %actions = ();

    @maintainer_clean_files = ();

    @sources = ();
    @dist_sources = ();

    %object_map = ();
    %object_compilation_map = ();

    %directory_map = ();

    %dep_files = ();

    $strictness = $default_strictness;
    $strictness_name = $default_strictness_name;

    %options = ();

    $use_dependencies = $cmdline_use_dependencies;

    @dist_targets = ();

    %de_ansi_files = ();

    %suffix_rules = ();

    $all_target = '';

    %extension_seen = ();

    %language_scratch = ();

    %lang_specific_files = ();

    $handle_dist_run = 0;

    $need_link = 0;

    @var_list = ();

    $get_object_extension_was_run = 0;

    %compile_clean_files = ();

    # We always include `.'.  This isn't strictly correct.
    %libtool_clean_directories = ('.' => 1);

    %subobjvar = ();
}


################################################################

# Initialize our list of languages that are internally supported.

# C.
register_language ('name' => 'c',
           'Name' => 'C',
           'config_vars' => ['CC'],
           'ansi' => 1,
           'autodep' => '',
           'flags' => 'CFLAGS',
           'compiler' => 'COMPILE',
           'compile' => '$(CC) $(DEFS) $(DEFAULT_INCLUDES) $(INCLUDES) $(AM_CPPFLAGS) $(CPPFLAGS) $(AM_CFLAGS) $(CFLAGS)',
           'lder' => 'CCLD',
           'ld' => '$(CC)',
           'linker' => 'LINK',
           'link' => '$(CCLD) $(AM_CFLAGS) $(CFLAGS) $(AM_LDFLAGS) $(LDFLAGS) -o $@',
           'compile_flag' => '-c',
           'extensions' => ['.c'],
           '_finish' => \&lang_c_finish);

# C++.
register_language ('name' => 'cxx',
           'Name' => 'C++',
           'config_vars' => ['CXX'],
           'linker' => 'CXXLINK',
           'link' => '$(CXXLD) $(AM_CXXFLAGS) $(CXXFLAGS) $(AM_LDFLAGS) $(LDFLAGS) -o $@',
           'autodep' => 'CXX',
           'flags' => 'CXXFLAGS',
           'compile' => '$(CXX) $(DEFS) $(DEFAULT_INCLUDES) $(INCLUDES) $(AM_CPPFLAGS) $(CPPFLAGS) $(AM_CXXFLAGS) $(CXXFLAGS)',
           'compiler' => 'CXXCOMPILE',
           'compile_flag' => '-c',
           'output_flag' => '-o',
           'lder' => 'CXXLD',
           'ld' => '$(CXX)',
           'pure' => 1,
           'extensions' => ['.c++', '.cc', '.cpp', '.cxx', '.C']);

# Objective C.
register_language ('name' => 'objc',
           'Name' => 'Objective C',
           'config_vars' => ['OBJC'],
           'linker' => 'OBJCLINK',,
           'link' => '$(OBJCLD) $(AM_OBJCFLAGS) $(OBJCFLAGS) $(AM_LDFLAGS) $(LDFLAGS) -o $@',
           'autodep' => 'OBJC',
           'flags' => 'OBJCFLAGS',
           'compile' => '$(OBJC) $(DEFS) $(DEFAULT_INCLUDES) $(INCLUDES) $(AM_CPPFLAGS) $(CPPFLAGS) $(AM_OBJCFLAGS) $(OBJCFLAGS)',
           'compiler' => 'OBJCCOMPILE',
           'compile_flag' => '-c',
           'output_flag' => '-o',
           'lder' => 'OBJCLD',
           'ld' => '$(OBJC)',
           'pure' => 1,
           'extensions' => ['.m']);

# Headers.
register_language ('name' => 'header',
           'Name' => 'Header',
           'extensions' => ['.h', '.H', '.hxx', '.h++', '.hh',
                    '.hpp', '.inc'],
           # Nothing to do.
           '_finish' => sub { });

# Yacc (C & C++).
register_language ('name' => 'yacc',
           'Name' => 'Yacc',
           'config_vars' => ['YACC'],
           'flags' => 'YFLAGS',
           'define_flag' => 0,
           'compile' => '$(YACC) $(YFLAGS) $(AM_YFLAGS)',
           'compiler' => 'YACCCOMPILE',
           'extensions' => ['.y'],
           'rule_file' => 'yacc',
           '_finish' => \&lang_yacc_finish,
           '_target_hook' => \&lang_yacc_target_hook);
register_language ('name' => 'yaccxx',
           'Name' => 'Yacc (C++)',
           'config_vars' => ['YACC'],
           'rule_file' => 'yacc',
           'flags' => 'YFLAGS',
           'define_flag' => 0,
           'compiler' => 'YACCCOMPILE',
           'compile' => '$(YACC) $(YFLAGS) $(AM_YFLAGS)',
           'extensions' => ['.y++', '.yy', '.yxx', '.ypp'],
           '_finish' => \&lang_yacc_finish,
           '_target_hook' => \&lang_yacc_target_hook);

# Lex (C & C++).
register_language ('name' => 'lex',
           'Name' => 'Lex',
           'config_vars' => ['LEX'],
           'rule_file' => 'lex',
           'flags' => 'LFLAGS',
           'define_flag' => 0,
           'compile' => '$(LEX) $(LFLAGS) $(AM_LFLAGS)',
           'compiler' => 'LEXCOMPILE',
           'extensions' => ['.l'],
           '_finish' => \&lang_lex_finish,
           '_target_hook' => \&lang_lex_target_hook);
register_language ('name' => 'lexxx',
           'Name' => 'Lex (C++)',
           'config_vars' => ['LEX'],
           'rule_file' => 'lex',
           'flags' => 'LFLAGS',
           'define_flag' => 0,
           'compile' => '$(LEX) $(LFLAGS) $(AM_LFLAGS)',
           'compiler' => 'LEXCOMPILE',
           'extensions' => ['.l++', '.ll', '.lxx', '.lpp'],
           '_finish' => \&lang_lex_finish,
           '_target_hook' => \&lang_lex_target_hook);

# Assembler.
register_language ('name' => 'asm',
           'Name' => 'Assembler',
           'config_vars' => ['CCAS', 'CCASFLAGS'],

           'flags' => 'CCASFLAGS',
           # Users can set AM_ASFLAGS to includes DEFS, INCLUDES,
           # or anything else required.  They can also set AS.
           'compile' => '$(CCAS) $(AM_CCASFLAGS) $(CCASFLAGS)',
           'compiler' => 'CCASCOMPILE',
           'compile_flag' => '-c',
           'extensions' => ['.s', '.S'],

           # With assembly we still use the C linker.
           '_finish' => \&lang_c_finish);

# Fortran 77
register_language ('name' => 'f77',
           'Name' => 'Fortran 77',
           'linker' => 'F77LINK',
           'link' => '$(F77LD) $(AM_FFLAGS) $(FFLAGS) $(AM_LDFLAGS) $(LDFLAGS) -o $@',
           'flags' => 'FFLAGS',
           'compile' => '$(F77) $(AM_FFLAGS) $(FFLAGS)',
           'compiler' => 'F77COMPILE',
           'compile_flag' => '-c',
           'output_flag' => '-o',
           'lder' => 'F77LD',
           'ld' => '$(F77)',
           'pure' => 1,
           'extensions' => ['.f', '.for', '.f90']);

# Preprocessed Fortran 77
#
# The current support for preprocessing Fortran 77 just involves
# passing `$(DEFS) $(DEFAULT_INCLUDES) $(INCLUDES) $(AM_CPPFLAGS)
# $(CPPFLAGS)' as additional flags to the Fortran 77 compiler, since
# this is how GNU Make does it; see the `GNU Make Manual, Edition 0.51
# for `make' Version 3.76 Beta' (specifically, from info file
# `(make)Catalogue of Rules').
#
# A better approach would be to write an Autoconf test
# (i.e. AC_PROG_FPP) for a Fortran 77 preprocessor, because not all
# Fortran 77 compilers know how to do preprocessing.  The Autoconf
# macro AC_PROG_FPP should test the Fortran 77 compiler first for
# preprocessing capabilities, and then fall back on cpp (if cpp were
# available).
register_language ('name' => 'ppf77',
           'Name' => 'Preprocessed Fortran 77',
           'config_vars' => ['F77'],
           'linker' => 'F77LINK',
           'link' => '$(F77LD) $(AM_FFLAGS) $(FFLAGS) $(AM_LDFLAGS) $(LDFLAGS) -o $@',
           'lder' => 'F77LD',
           'ld' => '$(F77)',
           'flags' => 'FFLAGS',
           'compiler' => 'PPF77COMPILE',
           'compile' => '$(F77) $(DEFS) $(DEFAULT_INCLUDES) $(INCLUDES) $(AM_CPPFLAGS) $(CPPFLAGS) $(AM_FFLAGS) $(FFLAGS)',
           'compile_flag' => '-c',
           'output_flag' => '-o',
           'pure' => 1,
           'extensions' => ['.F']);

# Ratfor.
register_language ('name' => 'ratfor',
           'Name' => 'Ratfor',
           'config_vars' => ['F77'],
           'linker' => 'F77LINK',
           'link' => '$(F77LD) $(AM_FFLAGS) $(FFLAGS) $(AM_LDFLAGS) $(LDFLAGS) -o $@',
           'lder' => 'F77LD',
           'ld' => '$(F77)',
           'flags' => 'RFLAGS',
           # FIXME also FFLAGS.
           'compile' => '$(F77) $(AM_FFLAGS) $(FFLAGS) $(AM_RFLAGS) $(RFLAGS)',
           'compiler' => 'RCOMPILE',
           'compile_flag' => '-c',
           'output_flag' => '-o',
           'pure' => 1,
           'extensions' => ['.r']);

# Java via gcj.
register_language ('name' => 'java',
           'Name' => 'Java',
           'config_vars' => ['GCJ'],
           'linker' => 'GCJLINK',
           'link' => '$(GCJLD) $(AM_GCJFLAGS) $(GCJFLAGS) $(AM_LDFLAGS) $(LDFLAGS) -o $@',
           'autodep' => 'GCJ',
           'flags' => 'GCJFLAGS',
           'compile' => '$(GCJ) $(AM_GCJFLAGS) $(GCJFLAGS)',
           'compiler' => 'GCJCOMPILE',
           'compile_flag' => '-c',
           'output_flag' => '-o',
           'lder' => 'GCJLD',
           'ld' => '$(GCJ)',
           'pure' => 1,
           'extensions' => ['.java', '.class', '.zip', '.jar']);

################################################################

# Parse command line.
&parse_arguments;

# Do configure.ac scan only once.
&scan_autoconf_files;

die "$me: no `Makefile.am' found or specified\n"
    if ! @input_files;

my $automake_has_run = 0;

do
{
    if ($automake_has_run)
    {
    verbose "processing Makefiles another time to fix them up.\n";
    &prog_error ("running more than two times should never be needed.")
        if $automake_has_run >= 2;
    }
    $automake_needs_to_reprocess_all_files = 0;

    # Now do all the work on each file.
    # This guy must be local otherwise it's private to the loop.
    use vars '$am_file';
    local $am_file;
    foreach $am_file (@input_files)
    {
    if (! -f ($am_file . '.am'))
    {
        &am_error ("`" . $am_file . ".am' does not exist");
    }
    else
    {
        &generate_makefile ($output_files{$am_file}, $am_file);
    }
    }
    ++$automake_has_run;
}
while ($automake_needs_to_reprocess_all_files);

exit $exit_status;

################################################################

# prog_error (@PRINT-ME)
# ----------------------
# Signal a programming error, display PRINT-ME, and exit 1.
sub prog_error (@)
{
    print STDERR "$me: programming error: @_\n";
    exit 1;
}


# subst ($TEXT)
# -------------
# Return a configure-style substitution using the indicated text.
# We do this to avoid having the substitutions directly in automake.in;
# when we do that they are sometimes removed and this causes confusion
# and bugs.
sub subst ($)
{
    my ($text) = @_;
    return '@' . $text . '@';
}

################################################################


# $BACKPATH
# &backname ($REL-DIR)
# --------------------
# If I `cd $REL-DIR', then to come back, I should `cd $BACKPATH'.
# For instance `src/foo' => `../..'.
# Works with non strictly increasing paths, i.e., `src/../lib' => `..'.
sub backname ($)
{
    my ($file) = @_;
    my @res;
    foreach (split (/\//, $file))
    {
    next if $_ eq '.' || $_ eq '';
    if ($_ eq '..')
    {
        pop @res;
    }
    else
    {
        push (@res, '..');
    }
    }
    return join ('/', @res) || '.';
}

################################################################

# Pattern that matches all know input extensions (i.e. extensions used
# by the languages supported by Automake).  Using this pattern
# (instead of `\..*$') to match extensions allows Automake to support
# dot-less extensions.
my $KNOWN_EXTENSIONS_PATTERN = "";
my @known_extensions_list = ();

# accept_extensions (@EXTS)
# -------------------------
# Update $KNOWN_EXTENSIONS_PATTERN to recognize the extensions
# listed @EXTS.  Extensions should contain a dot if needed.
sub accept_extensions (@)
{
    push @known_extensions_list, @_;
    $KNOWN_EXTENSIONS_PATTERN =
    '(?:' . join ('|', map (quotemeta, @known_extensions_list)) . ')';
}

# var_SUFFIXES_trigger ($TYPE, $VALUE)
# ------------------------------------
# This is called automagically by define_macro() when SUFFIXES
# is defined ($TYPE eq '') or appended ($TYPE eq '+').
# The work here needs to be performed as a side-effect of the
# define_macro() call because SUFFIXES definitions impact
# on $KNOWN_EXTENSIONS_PATTERN, and $KNOWN_EXTENSIONS_PATTERN
# are used when parsing the input am file.
sub var_SUFFIXES_trigger ($$)
{
    my ($type, $value) = @_;
    accept_extensions (split (' ', $value));
}

################################################################

# Parse command line.
sub parse_arguments ()
{
    # Start off as gnu.
    &set_strictness ('gnu');

    use Getopt::Long;
    Getopt::Long::config ("bundling", "pass_through");
    Getopt::Long::GetOptions
      (
       'version'    => \&version,
       'help'       => \&usage,
       'libdir:s'   => \$libdir,
       'gnu'        => sub { &set_strictness ('gnu'); },
       'gnits'      => sub { &set_strictness ('gnits'); },
       'cygnus'     => \$cygnus_mode,
       'foreign'    => sub { &set_strictness ('foreign'); },
       'include-deps'   => sub { $cmdline_use_dependencies = 1; },
       'i|ignore-deps'  => sub { $cmdline_use_dependencies = 0; },
       'no-force'   => sub { $force_generation = 0; },
       'f|force-missing'=> \$force_missing,
       'o|output-dir:s' => \$output_directory,
       'a|add-missing'  => \$add_missing,
       'c|copy'     => \$copy_missing,
       'v|verbose'  => \$verbose,
       'Werror'         => sub { $SIG{"__WARN__"} = sub { die $_[0] } },
       'Wno-error'      => sub { $SIG{"__WARN__"} = 'DEFAULT' }
      )
    or exit 1;

    if (defined $output_directory)
    {
    print STDERR "$0: `--output-dir' is deprecated\n";
    }
    else
    {
    # In the next release we'll remove this entirely.
    $output_directory = '.';
    }

    foreach my $arg (@ARGV)
    {
      if ($arg =~ /^-./)
    {
      print STDERR "$0: unrecognized option `$arg'\n";
      print STDERR "Try `$0 --help' for more information.\n";
      exit (1);
    }

      # Handle $local:$input syntax.  Note that we only examine the
      # first ":" file to see if it is automake input; the rest are
      # just taken verbatim.  We still keep all the files around for
      # dependency checking, however.
      my ($local, $input, @rest) = split (/:/, $arg);
      if (! $input)
    {
      $input = $local;
    }
      else
    {
      # Strip .in; later on .am is tacked on.  That is how the
      # automake input file is found.  Maybe not the best way, but
      # it is easy to explain.
      $input =~ s/\.in$//
        or die "$me: invalid input file name `$arg'\n.";
    }
      push (@input_files, $input);
      $output_files{$input} = join (':', ($local, @rest));
    }

    # Take global strictness from whatever we currently have set.
    $default_strictness = $strictness;
    $default_strictness_name = $strictness_name;
}

################################################################

# Generate a Makefile.in given the name of the corresponding Makefile and
# the name of the file output by config.status.
sub generate_makefile
{
    my ($output, $makefile) = @_;

    # Reset all the Makefile.am related variables.
    &initialize_per_input;

    # Name of input file ("Makefile.am") and output file
    # ("Makefile.in").  These have no directory components.
    $am_file_name = basename ($makefile) . '.am';
    $in_file_name = basename ($makefile) . '.in';

    # $OUTPUT is encoded.  If it contains a ":" then the first element
    # is the real output file, and all remaining elements are input
    # files.  We don't scan or otherwise deal with these input file,
    # other than to mark them as dependencies.  See
    # &scan_autoconf_files for details.
    my (@secondary_inputs);
    ($output, @secondary_inputs) = split (/:/, $output);

    $relative_dir = dirname ($output);
    $am_relative_dir = dirname ($makefile);

    &read_main_am_file ($makefile . '.am');
    if (&handle_options)
    {
    # Fatal error.  Just return, so we can continue with next file.
    return;
    }

    # There are a few install-related variables that you should not define.
    foreach my $var ('PRE_INSTALL', 'POST_INSTALL', 'NORMAL_INSTALL')
    {
    if (variable_defined ($var) && !$var_is_am{$var})
    {
        macro_error ($var, "`$var' should not be defined");
    }
    }

    # At the toplevel directory, we might need config.guess, config.sub
    # or libtool scripts (ltconfig and ltmain.sh).
    if ($relative_dir eq '.')
    {
        # AC_CANONICAL_HOST and AC_CANONICAL_SYSTEM need config.guess and
        # config.sub.
        require_conf_file ($canonical_location, FOREIGN,
               'config.guess', 'config.sub')
      if $seen_canonical;
    }

    # We still need Makefile.in here, because sometimes the `dist'
    # target doesn't re-run automake.
    if ($am_relative_dir eq $relative_dir)
    {
    # Only distribute the files if they are in the same subdir as
    # the generated makefile.
    &push_dist_common ($in_file_name, $am_file_name);
    }

    push (@sources, '$(SOURCES)')
    if variable_defined ('SOURCES');

    # Must do this after reading .am file.  See read_main_am_file to
    # understand weird tricks we play there with variables.
    &define_variable ('subdir', $relative_dir);

    # Check first, because we might modify some state.
    &check_cygnus;
    &check_gnu_standards;
    &check_gnits_standards;

    &handle_configure ($output, $makefile, @secondary_inputs);
    &handle_gettext;
    &handle_libraries;
    &handle_ltlibraries;
    &handle_programs;
    &handle_scripts;

    # This must run first so that the ANSI2KNR definition is generated
    # before it is used by the _.c rules.  We have to do this because
    # a variable which is used in a dependency must be defined before
    # the target, or else make won't properly see it.
    &handle_compile;
    # This must be run after all the sources are scanned.
    &handle_languages;

    # We have to run this after dealing with all the programs.
    &handle_libtool;

    # Re-init SOURCES.  FIXME: other code shouldn't depend on this
    # (but currently does).
    macro_define ('SOURCES', 1, '', 'TRUE', "@sources", 'internal');
    define_pretty_variable ('DIST_SOURCES', '', @dist_sources);

    &handle_multilib;
    &handle_texinfo;
    &handle_emacs_lisp;
    &handle_python;
    &handle_java;
    &handle_man_pages;
    &handle_data;
    &handle_headers;
    &handle_subdirs;
    &handle_tags;
    &handle_minor_options;
    &handle_tests;

    # This must come after most other rules.
    &handle_dist ($makefile);

    &handle_footer;
    &do_check_merge_target;
    &handle_all ($output);

    # FIXME: Gross!
    if (variable_defined ('lib_LTLIBRARIES') &&
    variable_defined ('bin_PROGRAMS'))
    {
    $output_rules .= "install-binPROGRAMS: install-libLTLIBRARIES\n\n";
    }

    &handle_installdirs;
    &handle_clean;
    &handle_factored_dependencies;

    check_typos ();

    if (! -d ($output_directory . '/' . $am_relative_dir))
    {
    mkdir ($output_directory . '/' . $am_relative_dir, 0755);
    }

    my ($out_file) = $output_directory . '/' . $makefile . ".in";
    if (! $force_generation && -e $out_file)
    {
    my ($am_time) = (stat ($makefile . '.am'))[9];
    my ($in_time) = (stat ($out_file))[9];
    # FIXME: should cache these times.
    my ($conf_time) = (stat ($configure_ac))[9];
    # FIXME: how to do unsigned comparison?
    if ($am_time < $in_time || $am_time < $conf_time)
    {
        # No need to update.
        return;
    }
    if (-f 'aclocal.m4')
    {
        my ($acl_time) = (stat _)[9];
        return if ($am_time < $acl_time);
    }
    }

    if (-e "$out_file")
    {
    unlink ($out_file)
        or die "$me: cannot remove $out_file: $!\n";
    }
    my $gm_file = new Automake::XFile "> $out_file";
    verbose "creating ", $makefile, ".in";

    print $gm_file $output_vars;
    # We make sure that `all:' is the first target.
    print $gm_file $output_all;
    print $gm_file $output_header;
    print $gm_file $output_rules;
    print $gm_file $output_trailer;
}

################################################################

# A version is a string that looks like
#   MAJOR.MINOR[.MICRO][ALPHA][-FORK]
# where
#   MAJOR, MINOR, and MICRO are digits, ALPHA is a character, and
# FORK any alphanumeric word.
# Usually, ALPHA is used to label alpha releases or intermediate snapshots,
# FORK is used for CVS branches or patched releases, and MICRO is used
# for bug fixes releases on the MAJOR.MINOR branch.
#
# For the purpose of ordering, 1.4 is the same as 1.4.0, but 1.4g is
# the same as 1.4.99g.  The FORK identifier is ignored in the
# ordering, except when it looks like -pMINOR[ALPHA]: some versions
# were labelled like 1.4-p3a, this is the same as an alpha release
# labelled 1.4.3a.  Yes it's horrible, but Automake did not support
# two-dot versions in the past.

# version_split (VERSION)
# -----------------------
# Split a version string into the corresponding (MAJOR, MINOR, MICRO,
# ALPHA, FORK) tuple.  For instance "1.4g" would be split into
# (1, 4, 99, 'g', '').
# Return () on error.
sub version_split ($)
{
    my ($ver) = @_;

    # Special case for versions like 1.4-p2a.
    if ($ver =~ /^(\d+)\.(\d+)(?:-p(\d+)([a-z]+)?)$/)
    {
    return ($1, $2, $3, $4 || '', '');
    }
    # Common case.
    elsif ($ver =~ /^(\d+)\.(\d+)(?:\.(\d+))?([a-z])?(?:-([A-Za-z0-9]+))?$/)
    {
    return ($1, $2, $3 || (defined $4 ? 99 : 0), $4 || '', $5 || '');
    }
    return ();
}

# version_compare (\@LVERSION, \@RVERSION)
# ----------------------------------------
# Return 1 if LVERSION > RVERSION,
#       -1 if LVERSION < RVERSION,
#        0 if LVERSION = RVERSION.
sub version_compare (\@\@)
{
    my @l = @{$_[0]};
    my @r = @{$_[1]};

    for my $i (0, 1, 2)
    {
    return 1  if ($l[$i] > $r[$i]);
    return -1 if ($l[$i] < $r[$i]);
    }
    for my $i (3, 4)
    {
    return 1  if ($l[$i] gt $r[$i]);
    return -1 if ($l[$i] lt $r[$i]);
    }
    return 0;
}

# Handles the logic of requiring a version number in AUTOMAKE_OPTIONS.
# Return 0 if the required version is satisfied, 1 otherwise.
sub version_check ($)
{
    my ($required) = @_;
    my @version = version_split $VERSION;
    my @required = version_split $required;

    prog_error ("version is incorrect: $VERSION")
    if $#version == -1;

    # This should not happen, because process_option_list and split_version
    # use similar regexes.
    prog_error ("required version is incorrect: $required")
    if $#required == -1;

    # If we require 3.4n-foo then we require something
    # >= 3.4n, with the `foo' fork identifier.
    return 1
    if ($required[4] ne '' && $required[4] ne $version[4]);

    return 0 > version_compare @version, @required;
}

# $BOOL
# process_option_list ($CONFIG, @OPTIONS)
# ------------------------------
# Process a list of options.  Return 1 on error, 0 otherwise.
# This is a helper for handle_options.  CONFIG is true if we're
# handling global options.
sub process_option_list
{
    my ($config, @list) = @_;
    foreach (@list)
    {
    $options{$_} = 1;
    if ($_ eq 'gnits' || $_ eq 'gnu' || $_ eq 'foreign')
    {
        &set_strictness ($_);
    }
    elsif ($_ eq 'cygnus')
    {
        $cygnus_mode = 1;
    }
    elsif (/^(.*\/)?ansi2knr$/)
    {
        # An option like "../lib/ansi2knr" is allowed.  With no
        # path prefix, we assume the required programs are in this
        # directory.  We save the actual option for later.
        $options{'ansi2knr'} = $_;
    }
    elsif ($_ eq 'no-installman' || $_ eq 'no-installinfo'
           || $_ eq 'dist-shar' || $_ eq 'dist-zip'
           || $_ eq 'dist-tarZ' || $_ eq 'dist-bzip2'
           || $_ eq 'dejagnu' || $_ eq 'no-texinfo.tex'
           || $_ eq 'readme-alpha' || $_ eq 'check-news'
           || $_ eq 'subdir-objects' || $_ eq 'nostdinc'
           || $_ eq 'no-exeext' || $_ eq 'no-define')
    {
        # Explicitly recognize these.
    }
    elsif ($_ eq 'no-dependencies')
    {
        $use_dependencies = 0;
    }
    elsif (/^\d+\.\d+(?:\.\d+)?[a-z]?(?:-[A-Za-z0-9]+)?$/)
    {
        # Got a version number.
        if (version_check $&)
        {
        if ($config)
        {
            file_error ($seen_init_automake,
                "require version $_, but have $VERSION");
            # Arrange to process this global option only once, otherwise
            # the error message would be printed for each Makefile.
            $global_options =~ s/(?:^| )$_(?: |$)/ /g;
        }
        else
        {
            macro_error ('AUTOMAKE_OPTIONS',
                 "require version $_, but have $VERSION");
        }
        return 1;
        }
    }
    else
    {
        if ($config)
        {
        file_error ($seen_init_automake,
                "option `" . $_ . "\' not recognized");
        }
        else
        {
        macro_error ('AUTOMAKE_OPTIONS',
                 "option `" . $_ . "\' not recognized");
        }
        return 1;
    }
    }
}

# Handle AUTOMAKE_OPTIONS variable.  Return 1 on error, 0 otherwise.
sub handle_options
{
    # Process global options first so that more specific options can
    # override.
    if (&process_option_list (1, split (' ', $global_options)))
    {
    return 1;
    }

    if (variable_defined ('AUTOMAKE_OPTIONS'))
    {
    if (&process_option_list (0, &variable_value_as_list_recursive ('AUTOMAKE_OPTIONS', '')))
    {
        return 1;
    }
    }

    if ($strictness == GNITS)
    {
    $options{'readme-alpha'} = 1;
    $options{'check-news'} = 1;
    }

    return 0;
}


# get_object_extension ($OUT)
# ---------------------------
# Return object extension.  Just once, put some code into the output.
# OUT is the name of the output file
sub get_object_extension
{
    my ($out) = @_;

    # Maybe require libtool library object files.
    my $extension = '.$(OBJEXT)';
    $extension = '.lo' if ($out =~ /\.la$/);

    # Check for automatic de-ANSI-fication.
    $extension = '$U' . $extension
      if defined $options{'ansi2knr'};

    $get_object_extension_was_run = 1;

    return $extension;
}


# Call finish function for each language that was used.
sub handle_languages
{
    if ($use_dependencies)
    {
    # Include auto-dep code.  Don't include it if DEP_FILES would
    # be empty.
    if (&saw_sources_p (0) && keys %dep_files)
    {
        # Set location of depcomp.
        &define_variable ('depcomp', "\$(SHELL) $config_aux_dir/depcomp");
        &define_variable ('am__depfiles_maybe', 'depfiles');

        require_conf_file ("$am_file.am", FOREIGN, 'depcomp');

        my @deplist = sort keys %dep_files;

        # We define this as a conditional variable because BSD
        # make can't handle backslashes for continuing comments on
        # the following line.
        define_pretty_variable ('DEP_FILES', 'AMDEP_TRUE', @deplist);

        # Generate each `include' individually.  Irix 6 make will
        # not properly include several files resulting from a
        # variable expansion; generating many separate includes
        # seems safest.
        $output_rules .= "\n";
        foreach my $iter (@deplist)
        {
        $output_rules .= (subst ('AMDEP_TRUE')
                  . subst ('am__include')
                  . ' '
                  . subst ('am__quote')
                  . $iter
                  . subst ('am__quote')
                  . "\n");
        }

        # Compute the set of directories to remove in distclean-depend.
        my @depdirs = uniq (map { dirname ($_) } @deplist);
        $output_rules .= &file_contents ('depend',
                         DEPDIRS => "@depdirs");
    }
    }
    else
    {
    &define_variable ('depcomp', '');
    &define_variable ('am__depfiles_maybe', '');
    }

    my %done;

    # Is the c linker needed?
    my $needs_c = 0;
    foreach my $ext (sort keys %extension_seen)
    {
    next unless $extension_map{$ext};

    my $lang = $languages{$extension_map{$ext}};

    my $rule_file = $lang->rule_file || 'depend2';

    # Get information on $LANG.
    my $pfx = $lang->autodep;
    my $fpfx = ($pfx eq '') ? 'CC' : $pfx;

    my $AMDEP = (($use_dependencies && $lang->autodep ne 'no')
             ? 'AMDEP' : 'FALSE');

    my %transform = ('EXT'     => $ext,
             'PFX'     => $pfx,
             'FPFX'    => $fpfx,
             'LIBTOOL' => defined $seen_libtool,
             'AMDEP'   => $AMDEP,
             '-c'      => $lang->compile_flag || '',
             'MORE-THAN-ONE'
                       => (count_files_for_language ($lang->name) > 1));

    # Generate the appropriate rules for this extension.
    if (($use_dependencies && $lang->autodep ne 'no')
        || defined $lang->compile)
    {
        # Some C compilers don't support -c -o.  Use it only if really
        # needed.
        my $output_flag = $lang->output_flag || '';
        $output_flag = '-o'
          if (! $output_flag
          && $lang->flags eq 'CFLAGS'
          && defined $options{'subdir-objects'});

        # FIXME: this is a temporary hack to compute a possible
        # derived extension.  This is not used by depend2.am.
        (my $der_ext = $ext) =~ tr/yl/cc/;

        # Another yacc/lex hack.
        my $destfile = '$*' . $der_ext;

        $output_rules .=
          file_contents ($rule_file,
                 %transform,
                 'GENERIC'   => 1,

                 'DERIVED-EXT' => $der_ext,

                 # In this situation we know that the
                 # object is in this directory, so
                 # $(DEPDIR) is the correct location for
                 # dependencies.
                 'DEPBASE'   => '$(DEPDIR)/$*',
                 'BASE'      => '$*',
                 'SOURCE'    => '$<',
                 'OBJ'       => '$@',
                 'OBJOBJ'    => '$@',
                 'LTOBJ'     => '$@',

                 'COMPILE'   => '$(' . $lang->compiler . ')',
                 'LTCOMPILE' => '$(LT' . $lang->compiler . ')',
                 '-o'        => $output_flag);
    }

    # Now include code for each specially handled object with this
    # language.
    my %seen_files = ();
    foreach my $file (@{$lang_specific_files{$lang->name}})
    {
        my ($derived, $source, $obj, $myext) = split (' ', $file);

        # For any specially-generated object, we must respect the
        # ansi2knr setting so that we don't inadvertently try to
        # use the default rule.
        if ($lang->ansi && defined $options{'ansi2knr'})
        {
        $myext = '$U' . $myext;
        }

        # We might see a given object twice, for instance if it is
        # used under different conditions.
        next if defined $seen_files{$obj};
        $seen_files{$obj} = 1;

        my $flags = $lang->flags || '';
        my $val = "${derived}_${flags}";

        prog_error ("found $lang->name in handle_languages, but compiler not defined")
        unless defined $lang->compile;

        (my $obj_compile = $lang->compile) =~ s/\(AM_$flags/\($val/;
        my $obj_ltcompile = '$(LIBTOOL) --mode=compile ' . $obj_compile;

        # We _need_ `-o' for per object rules.
        my $output_flag = $lang->output_flag || '-o';

        my $depbase = dirname ($obj);
        $depbase = ''
        if $depbase eq '.';
        $depbase .= '/'
        unless $depbase eq '';
        $depbase .= '$(DEPDIR)/' . basename ($obj);

        # Generate a transform which will turn suffix targets in
        # depend2.am into real targets for the particular objects we
        # are building.
        $output_rules .=
          file_contents ($rule_file,
                 (%transform,
                  'GENERIC'   => 0,

                  'DEPBASE'   => $depbase,
                  'BASE'      => $obj,
                  'SOURCE'    => $source,
                  # Use $myext and not `.o' here, in case
                  # we are actually building a new source
                  # file -- e.g. via yacc.
                  'OBJ'       => "$obj$myext",
                  'OBJOBJ'    => "$obj.obj",
                  'LTOBJ'     => "$obj.lo",

                  'COMPILE'   => $obj_compile,
                  'LTCOMPILE' => $obj_ltcompile,
                  '-o'        => $output_flag));
    }

    # The rest of the loop is done once per language.
    next if defined $done{$lang};
    $done{$lang} = 1;

    # Load the language dependent Makefile chunks.
    my %lang = map { uc ($_) => 0 } keys %languages;
    $lang{uc ($lang->name)} = 1;
    $output_rules .= file_contents ('lang-compile', %transform, %lang);

    # If the source to a program consists entirely of code from a
    # `pure' language, for instance C++ for Fortran 77, then we
    # don't need the C compiler code.  However if we run into
    # something unusual then we do generate the C code.  There are
    # probably corner cases here that do not work properly.
    # People linking Java code to Fortran code deserve pain.
    $needs_c ||= ! $lang->pure;

    define_compiler_variable ($lang)
      if ($lang->compile);

    define_linker_variable ($lang)
      if ($lang->link);

    foreach my $var (@{$lang->config_vars})
      {
        am_error ($lang->Name
              . " source seen but `$var' not defined in"
              . " `$configure_ac'")
          if !exists $configure_vars{$var};
      }

    # The compiler's flag must be a configure variable.
    define_configure_variable ($lang->flags)
        if defined $lang->flags && $lang->define_flag;

    # Call the finisher.
    $lang->finish;
    }

    # If the project is entirely C++ or entirely Fortran 77 (i.e., 1
    # suffix rule was learned), don't bother with the C stuff.  But if
    # anything else creeps in, then use it.
    $needs_c = 1
      if $need_link || scalar keys %suffix_rules > 1;

    if ($needs_c)
      {
    if (! defined $done{$languages{'c'}})
      {
        &define_configure_variable ($languages{'c'}->flags);
        &define_compiler_variable ($languages{'c'});
      }
    define_linker_variable ($languages{'c'});
      }
}

# Check to make sure a source defined in LIBOBJS is not explicitly
# mentioned.  This is a separate function (as opposed to being inlined
# in handle_source_transform) because it isn't always appropriate to
# do this check.
sub check_libobjs_sources
{
    my ($one_file, $unxformed) = @_;

    foreach my $prefix ('', 'EXTRA_', 'dist_', 'nodist_',
            'dist_EXTRA_', 'nodist_EXTRA_')
    {
        my @files;
    if (variable_defined ($prefix . $one_file . '_SOURCES'))
    {
        @files = &variable_value_as_list_recursive (
                ($prefix . $one_file . '_SOURCES'),
                'all');
    }
    elsif ($prefix eq '')
    {
        @files = ($unxformed . '.c');
    }
    else
    {
        next;
    }

    foreach my $file (@files)
    {
      macro_error ($prefix . $one_file . '_SOURCES',
               "automatically discovered file `$file' should not be explicitly mentioned")
        if defined $libsources{$file};
    }
    }
}


# @OBJECTS
# handle_single_transform_list ($VAR, $TOPPARENT, $DERIVED, $OBJ, @FILES)
# -----------------------------------------------------------------------
# Does much of the actual work for handle_source_transform.
# Arguments are:
#   $VAR is the name of the variable that the source filenames come from
#   $TOPPARENT is the name of the _SOURCES variable which is being processed
#   $DERIVED is the name of resulting executable or library
#   $OBJ is the object extension (e.g., `$U.lo')
#   @FILES is the list of source files to transform
# Result is a list of the names of objects
# %linkers_used will be updated with any linkers needed
sub handle_single_transform_list ($$$$@)
{
    my ($var, $topparent, $derived, $obj, @files) = @_;
    my @result = ();
    my $nonansi_obj = $obj;
    $nonansi_obj =~ s/\$U//g;

    # Turn sources into objects.  We use a while loop like this
    # because we might add to @files in the loop.
    while (scalar @files > 0)
    {
    $_ = shift @files;

        # Configure substitutions in _SOURCES variables are errors.
        if (/^\@.*\@$/)
        {
            macro_error ($var,
             "`$var' includes configure substitution `$_', and is referred to from `$topparent': configure substitutions not allowed in _SOURCES variables");
            next;
        }

        # If the source file is in a subdirectory then the `.o' is put
        # into the current directory, unless the subdir-objects option
        # is in effect.

        # Split file name into base and extension.
        next if ! /^(?:(.*)\/)?([^\/]*)($KNOWN_EXTENSIONS_PATTERN)$/;
        my $full = $_;
        my $directory = $1 || '';
        my $base = $2;
        my $extension = $3;

        # We must generate a rule for the object if it requires its own flags.
        my $renamed = 0;
        my ($linker, $object);

    # This records whether we've seen a derived source file (eg,
    # yacc output).
    my $derived_source = 0;

    # This holds the `aggregate context' of the file we are
    # currently examining.  If the file is compiled with
    # per-object flags, then it will be the name of the object.
    # Otherwise it will be `AM'.  This is used by the target hook
    # language function.
    my $aggregate = 'AM';

        $extension = &derive_suffix ($extension, $nonansi_obj);
        my $lang;
        if ($extension_map{$extension} &&
            ($lang = $languages{$extension_map{$extension}}))
    {
            # Found the language, so see what it says.
            &saw_extension ($extension);

            # Note: computed subr call.  The language rewrite function
            # should return one of the $LANG_* constants.  It could
            # also return a list whose first value is such a constant
            # and whose second value is a new source extension which
            # should be applied.  This means this particular language
            # generates another source file which we must then process
            # further.
            my $subr = 'lang_' . $lang->name . '_rewrite';
            my ($r, $source_extension)
        = & $subr ($directory, $base, $extension);
            # Skip this entry if we were asked not to process it.
            next if $r == $LANG_IGNORE;

            # Now extract linker and other info.
            $linker = $lang->linker;

            my $this_obj_ext;
        if (defined $source_extension)
        {
        $this_obj_ext = $source_extension;
        $derived_source = 1;
        }
        elsif ($lang->ansi)
        {
        $this_obj_ext = $obj;
        }
        else
        {
        $this_obj_ext = $nonansi_obj;
        }
        $object = $base . $this_obj_ext;

            if (defined $lang->flags
                && variable_defined ($derived . '_' . $lang->flags))
            {
                # We have a per-executable flag in effect for this
                # object.  In this case we rewrite the object's
                # name to ensure it is unique.  We also require
                # the `compile' program to deal with compilers
                # where `-c -o' does not work.

                # We choose the name `DERIVED_OBJECT' to ensure
                # (1) uniqueness, and (2) continuity between
                # invocations.  However, this will result in a
                # name that is too long for losing systems, in
                # some situations.  So we provide _SHORTNAME to
                # override.

                my $dname = $derived;
                if (variable_defined ($derived . '_SHORTNAME'))
                {
                    # FIXME: should use the same conditional as
                    # the _SOURCES variable.  But this is really
                    # silly overkill -- nobody should have
                    # conditional shortnames.
                    $dname = &variable_value ($derived . '_SHORTNAME');
                }
                $object = $dname . '-' . $object;

                require_conf_file ("$am_file.am", FOREIGN, 'compile')
                    if $lang->name eq 'c';

                prog_error ("$lang->name flags defined without compiler")
            if ! defined $lang->compile;

                $renamed = 1;
            }

            # If rewrite said it was ok, put the object into a
            # subdir.
            if ($r == $LANG_SUBDIR && $directory ne '')
            {
                $object = $directory . '/' . $object;
            }

            # If doing dependency tracking, then we can't print
            # the rule.  If we have a subdir object, we need to
            # generate an explicit rule.  Actually, in any case
            # where the object is not in `.' we need a special
            # rule.  The per-object rules in this case are
            # generated later, by handle_languages.
            if ($renamed || $directory ne '')
            {
                my $obj_sans_ext = substr ($object, 0,
                       - length ($this_obj_ext));
        my $val = ("$full $obj_sans_ext "
               # Only use $this_obj_ext in the derived
               # source case because in the other case we
               # *don't* want $(OBJEXT) to appear here.
               . ($derived_source ? $this_obj_ext : '.o'));

        # If we renamed the object then we want to use the
        # per-executable flag name.  But if this is simply a
        # subdir build then we still want to use the AM_ flag
        # name.
        if ($renamed)
        {
            $val = "$derived $val";
            $aggregate = $derived;
        }
        else
        {
            $val = "AM $val";
        }

        # Each item on this list is a string consisting of
        # four space-separated values: the derived flag prefix
        # (eg, for `foo_CFLAGS', it is `foo'), the name of the
        # source file, the base name of the output file, and
        # the extension for the object file.
                push (@{$lang_specific_files{$lang->name}}, $val);
            }
        }
        elsif ($extension eq $nonansi_obj)
        {
            # This is probably the result of a direct suffix rule.
            # In this case we just accept the rewrite.
            $object = "$base$extension";
            $linker = '';
        }
        else
        {
            # No error message here.  Used to have one, but it was
            # very unpopular.
        # FIXME: we could potentially do more processing here,
        # perhaps treating the new extension as though it were a
        # new source extension (as above).  This would require
        # more restructuring than is appropriate right now.
            next;
        }

        if (defined $object_map{$object})
        {
            if ($object_map{$object} ne $full)
            {
                am_error ("object `$object' created by `$full' and `$object_map{$object}'");
            }
        }

    my $comp_val = (($object =~ /\.lo$/)
            ? $COMPILE_LIBTOOL : $COMPILE_ORDINARY);
    (my $comp_obj = $object) =~ s/\.lo$/.\$(OBJEXT)/;
    if (defined $object_compilation_map{$comp_obj}
        && $object_compilation_map{$comp_obj} != 0
        # Only see the error once.
        && ($object_compilation_map{$comp_obj}
        != ($COMPILE_LIBTOOL | $COMPILE_ORDINARY))
        && $object_compilation_map{$comp_obj} != $comp_val)
    {
        am_error ("object `$object' created both with libtool and without");
    }
    $object_compilation_map{$comp_obj} |= $comp_val;

    if (defined $lang)
    {
        # Let the language do some special magic if required.
        $lang->target_hook ($aggregate, $object, $full);
    }

    if ($derived_source)
    {
        prog_error ("$lang->name has automatic dependency tracking")
        if $lang->autodep ne 'no';
        # Make sure this new source file is handled next.  That will
        # make it appear to be at the right place in the list.
        unshift (@files, $object);
        # Distribute derived sources unless the source they are
        # derived from is not.
        &push_dist_common ($object)
        unless ($topparent =~ /^(?:nobase_)?nodist_/);
        next;
    }

        $linkers_used{$linker} = 1;

        push (@result, $object);

        if (! defined $object_map{$object})
        {
            my @dep_list = ();
            $object_map{$object} = $full;

            # If file is in subdirectory, we need explicit
            # dependency.
            if ($directory ne '' || $renamed)
            {
                push (@dep_list, $full);
            }

            # If resulting object is in subdir, we need to make
            # sure the subdir exists at build time.
            if ($object =~ /\//)
            {
                # FIXME: check that $DIRECTORY is somewhere in the
                # project

        # For Java, the way we're handling it right now, a
        # `..' component doesn't make sense.
                if ($lang->name eq 'java' && $object =~ /(\/|^)\.\.\//)
                {
                    am_error ("`$full' contains `..' component but should not");
                }

        # Make sure object is removed by `make mostlyclean'.
        $compile_clean_files{$object} = MOSTLY_CLEAN;
        # If we have a libtool object then we also must remove
        # the ordinary .o.
        if ($object =~ /\.lo$/)
        {
            (my $xobj = $object) =~ s,lo$,\$(OBJEXT),;
            $compile_clean_files{$xobj} = MOSTLY_CLEAN;

            $libtool_clean_directories{$directory} = 1;
        }

                push (@dep_list, require_build_directory ($directory));

                # If we're generating dependencies, we also want
                # to make sure that the appropriate subdir of the
                # .deps directory is created.
        push (@dep_list,
              require_build_directory ($directory . '/$(DEPDIR)'))
            if $use_dependencies;
            }

            &pretty_print_rule ($object . ':', "\t", @dep_list)
                if scalar @dep_list > 0;
        }

        # Transform .o or $o file into .P file (for automatic
        # dependency code).
        if ($lang && $lang->autodep ne 'no')
        {
            my $depfile = $object;
            $depfile =~ s/\.([^.]*)$/.P$1/;
            $depfile =~ s/\$\(OBJEXT\)$/o/;
            $dep_files{dirname ($depfile) . '/$(DEPDIR)/'
               . basename ($depfile)} = 1;
        }
    }

    return @result;
}

# ($LINKER, $OBJVAR)
# define_objects_from_sources ($VAR, $OBJVAR, $NODEFINE, $ONE_FILE,
#                              $OBJ, $PARENT, $TOPPARENT)
# ---------------------------------------------------------------------
# Define an _OBJECTS variable for a _SOURCES variable (or subvariable)
#
# Arguments are:
#   $VAR is the name of the _SOURCES variable
#   $OBJVAR is the name of the _OBJECTS variable if known (otherwise
#     it will be generated and returned).
#   $NODEFINE is a boolean: if true, $OBJVAR will not be defined (but
#     work done to determine the linker will be).
#   $ONE_FILE is the canonical (transformed) name of object to build
#   $OBJ is the object extension (ie either `.o' or `.lo').
#   $PARENT is the variable in which $VAR is used, or $VAR if not applicable.
#   $TOPPARENT is the _SOURCES variable being processed.
#
# Result is a pair ($LINKER, $OBJVAR):
#    $LINKER is a boolean, true if a linker is needed to deal with the objects,
#    $OBJVAR is the name of the variable defined to hold the objects.
#
# %linkers_used, %vars_scanned, @substfroms and @substtos should be cleared
# before use:
#   %linkers_used variable will be set to contain the linkers desired.
#   %vars_scanned will be used to check for recursive definitions.
#   @substfroms and @substtos will be used to keep a stack of variable
#   substitutions to be applied.
#
sub define_objects_from_sources ($$$$$$$)
{
    my ($var, $objvar, $nodefine, $one_file, $obj, $parent, $topparent) = @_;

    if (defined $vars_scanned{$var})
    {
    macro_error ($var, "variable `$var' recursively defined");
    return "";
    }
    $vars_scanned{$var} = 1;

    my $needlinker = "";
    my @allresults = ();
    foreach my $cond (variable_conditions ($var))
    {
    my @result;
    foreach my $val (&variable_value_as_list ($var, $cond, $parent))
    {
        # If $val is a variable (i.e. ${foo} or $(bar), not a filename),
        # handle the sub variable recursively.
        if ($val =~ /^\$\{([^}]*)\}$/ || $val =~ /^\$\(([^)]*)\)$/)
        {
        my $subvar = $1;

        # If the user uses a losing variable name, just ignore it.
        # This isn't ideal, but people have requested it.
        next if ($subvar =~ /\@.*\@/);

        # See if the variable is actually a substitution reference
        my ($from, $to);
        my @temp_list;
        if ($subvar =~ /$SUBST_REF_PATTERN/o)
        {
            $subvar = $1;
            $to = $3;
            $from = quotemeta $2;
        }
        push @substfroms, $from;
        push @substtos, $to;

        my ($temp, $varname)
            = define_objects_from_sources ($subvar, undef,
                           $nodefine, $one_file,
                           $obj, $var, $topparent);

        push (@result, '$('. $varname . ')');
        $needlinker ||= $temp;

        pop @substfroms;
        pop @substtos;
        }
        else # $var is a filename
        {
            my $substnum=$#substfroms;
            while ($substnum >= 0)
        {
            $val =~ s/$substfroms[$substnum]$/$substtos[$substnum]/
            if defined $substfroms[$substnum];
            $substnum -= 1;
        }

        my (@transformed) =
              &handle_single_transform_list ($var, $topparent, $one_file, $obj, $val);
        push (@result, @transformed);
        $needlinker = "true" if @transformed;
        }
    }
    push (@allresults, [$cond, @result]);
    }
    # Find a name for the variable, unless imposed.
    $objvar = subobjname (@allresults) unless defined $objvar;
    # Define _OBJECTS conditionally
    unless ($nodefine)
    {
    foreach my $pair (@allresults)
    {
        my ($cond, @result) = @$pair;
        define_pretty_variable ($objvar, $cond, @result);
    }
    }

    delete $vars_scanned{$var};
    return ($needlinker, $objvar);
}


# $VARNAME
# subobjname (@DEFINITIONS)
# -------------------------
# Return a name for an object variable that with definitions @DEFINITIONS.
# @DEFINITIONS is a list of pair [$COND, @OBJECTS].
#
# If we already have an object variable containing @DEFINITIONS, reuse it.
# This way, we avoid combinatorial explosion of the generated
# variables.  Especially, in a Makefile such as:
#
# | if FOO1
# | A1=1
# | endif
# |
# | if FOO2
# | A2=2
# | endif
# |
# | ...
# |
# | if FOON
# | AN=N
# | endif
# |
# | B=$(A1) $(A2) ... $(AN)
# |
# | c_SOURCES=$(B)
# | d_SOURCES=$(B)
#
# The generated c_OBJECTS and d_OBJECTS will share the same variable
# definitions.
#
# This setup can be the case of a testsuite containing lots (>100) of
# small C programs, all testing the same set of source files.
sub subobjname (@)
{
    my $key = '';
    foreach my $pair (@_)
    {
    my ($cond, @values) = @$pair;
    $key .= "($cond)@values";
    }

    return $subobjvar{$key} if exists $subobjvar{$key};

    my $num = 1 + keys (%subobjvar);
    my $name = "am__objects_${num}";
    $subobjvar{$key} = $name;
    return $name;
}


# Handle SOURCE->OBJECT transform for one program or library.
# Arguments are:
#   canonical (transformed) name of object to build
#   actual name of object to build
#   object extension (ie either `.o' or `$o'.
# Return result is name of linker variable that must be used.
# Empty return means just use `LINK'.
sub handle_source_transform
{
    # one_file is canonical name.  unxformed is given name.  obj is
    # object extension.
    my ($one_file, $unxformed, $obj) = @_;

    my ($linker) = '';

    if (variable_defined ($one_file . "_OBJECTS"))
    {
    macro_error ($one_file . '_OBJECTS',
             $one_file . '_OBJECTS', 'should not be defined');
    # No point in continuing.
    return;
    }

    my %used_pfx = ();
    my $needlinker;
    %linkers_used = ();
    foreach my $prefix ('', 'EXTRA_', 'dist_', 'nodist_',
            'dist_EXTRA_', 'nodist_EXTRA_')
    {
    my $var = $prefix . $one_file . "_SOURCES";
    next
      if !variable_defined ($var);

    # We are going to define _OBJECTS variables using the prefix.
    # Then we glom them all together.  So we can't use the null
    # prefix here as we need it later.
    my $xpfx = ($prefix eq '') ? 'am_' : $prefix;

    # Keep track of which prefixes we saw.
    $used_pfx{$xpfx} = 1
      unless $prefix =~ /EXTRA_/;

    push @sources, "\$($var)";
    push @dist_sources, "\$($var)"
      unless $prefix =~ /^nodist_/;

    @substfroms = ();
    @substtos = ();
    %vars_scanned = ();
    my ($temp, $objvar) =
        define_objects_from_sources ($var,
                     $xpfx . $one_file . '_OBJECTS',
                     $prefix =~ /EXTRA_/,
                     $one_file, $obj, $var, $var);
    $needlinker ||= $temp;
    }
    if ($needlinker)
    {
    $linker ||= &resolve_linker (%linkers_used);
    }

    my @keys = sort keys %used_pfx;
    if (scalar @keys == 0)
    {
    &define_variable ($one_file . "_SOURCES", $unxformed . ".c");
    push (@sources, $unxformed . '.c');
    push (@dist_sources, $unxformed . '.c');

    %linkers_used = ();
    my (@result) =
      &handle_single_transform_list ($one_file . '_SOURCES',
                     $one_file . '_SOURCES',
                     $one_file, $obj,
                     "$unxformed.c");
    $linker ||= &resolve_linker (%linkers_used);
    define_pretty_variable ($one_file . "_OBJECTS", '', @result)
    }
    else
    {
    grep ($_ = '$(' . $_ . $one_file . '_OBJECTS)', @keys);
    define_pretty_variable ($one_file . '_OBJECTS', '', @keys);
    }

    # If we want to use `LINK' we must make sure it is defined.
    if ($linker eq '')
    {
    $need_link = 1;
    }

    return $linker;
}


# handle_lib_objects ($XNAME, $VAR)
# ---------------------------------
# Special-case @ALLOCA@ and @LIBOBJS@ in _LDADD or _LIBADD variables.
# Also, generate _DEPENDENCIES variable if appropriate.
# Arguments are:
#   transformed name of object being built, or empty string if no object
#   name of _LDADD/_LIBADD-type variable to examine
# Returns 1 if LIBOBJS seen, 0 otherwise.
sub handle_lib_objects
{
    my ($xname, $var) = @_;

    prog_error ("handle_lib_objects: $var undefined")
    if ! variable_defined ($var);

    my $ret = 0;
    foreach my $cond (variable_conditions_recursive ($var))
      {
    if (&handle_lib_objects_cond ($xname, $var, $cond))
      {
        $ret = 1;
      }
      }
    return $ret;
}

# Subroutine of handle_lib_objects: handle a particular condition.
sub handle_lib_objects_cond
{
    my ($xname, $var, $cond) = @_;

    # We recognize certain things that are commonly put in LIBADD or
    # LDADD.
    my @dep_list = ();

    my $seen_libobjs = 0;
    my $flagvar = 0;

    foreach my $lsearch (&variable_value_as_list_recursive ($var, $cond))
    {
    # Skip -lfoo and -Ldir; these are explicitly allowed.
    next if $lsearch =~ /^-[lL]/;
    if (! $flagvar && $lsearch =~ /^-/)
    {
        if ($var =~ /^(.*)LDADD$/)
        {
        # Skip -dlopen and -dlpreopen; these are explicitly allowed.
        next if $lsearch =~ /^-dl(pre)?open$/;
        my $prefix = $1 || 'AM_';
        macro_error ($var,
                 "linker flags such as `$lsearch' belong in `${prefix}LDFLAGS");
        }
        else
        {
        $var =~ /^(.*)LIBADD$/;
        # Only get this error once.
        $flagvar = 1;
        macro_error ($var,
                 "linker flags such as `$lsearch' belong in `${1}LDFLAGS");
        }
    }

    # Assume we have a file of some sort, and push it onto the
    # dependency list.  Autoconf substitutions are not pushed;
    # rarely is a new dependency substituted into (eg) foo_LDADD
    # -- but "bad things (eg -lX11) are routinely substituted.
    # Note that LIBOBJS and ALLOCA are exceptions to this rule,
    # and handled specially below.
    push (@dep_list, $lsearch)
        unless $lsearch =~ /^\@.*\@$/;

    # Automatically handle @LIBOBJS@ and @ALLOCA@.  Basically this
    # means adding entries to dep_files.
    if ($lsearch =~ /^\@(LT)?LIBOBJS\@$/)
    {
        my $lt = $1 ? $1 : '';
        my $myobjext = ($1 ? 'l' : '') . 'o';

        push (@dep_list, $lsearch);
        $seen_libobjs = 1;
        if (! keys %libsources
        && ! variable_defined ($lt . 'LIBOBJS'))
        {
        macro_error ($var,
                 "\@$lt" . "LIBOBJS\@ seen but never set in `$configure_ac'");
        }

        foreach my $iter (keys %libsources)
        {
        if ($iter =~ /\.[cly]$/)
        {
            &saw_extension ($&);
            &saw_extension ('.c');
        }

        if ($iter =~ /\.h$/)
        {
            require_file_with_macro ($var, FOREIGN, $iter);
        }
        elsif ($iter ne 'alloca.c')
        {
            my $rewrite = $iter;
            $rewrite =~ s/\.c$/.P$myobjext/;
            $dep_files{'$(DEPDIR)/' . $rewrite} = 1;
            $rewrite = "^" . quotemeta ($iter) . "\$";
            # Only require the file if it is not a built source.
            if (! variable_defined ('BUILT_SOURCES')
            || ! grep (/$rewrite/,
                   &variable_value_as_list_recursive (
                    'BUILT_SOURCES', 'all')))
            {
            require_file_with_macro ($var, FOREIGN, $iter);
            }
        }
        }
    }
    elsif ($lsearch =~ /^\@(LT)?ALLOCA\@$/)
    {
        my $lt = $1 ? $1 : '';
        my $myobjext = ($1 ? 'l' : '') . 'o';

        push (@dep_list, $lsearch);
        macro_error ($var,
             "\@$lt" . "ALLOCA\@ seen but `AC_FUNC_ALLOCA' not in `$configure_ac'")
        if ! defined $libsources{'alloca.c'};
        $dep_files{'$(DEPDIR)/alloca.P' . $myobjext} = 1;
        require_file_with_macro ($var, FOREIGN, 'alloca.c');
        &saw_extension ('c');
    }
    }

    if ($xname ne '')
    {
    if (conditional_ambiguous_p ($xname . '_DEPENDENCIES', $cond) ne '')
    {
        # Note that we've examined this.
        &examine_variable ($xname . '_DEPENDENCIES');
    }
    else
    {
        define_pretty_variable ($xname . '_DEPENDENCIES', $cond,
                    @dep_list);
    }
    }

    return $seen_libobjs;
}

# Canonicalize the input parameter
sub canonicalize
{
    my ($string) = @_;
    $string =~ tr/A-Za-z0-9_\@/_/c;
    return $string;
}

# Canonicalize a name, and check to make sure the non-canonical name
# is never used.  Returns canonical name.  Arguments are name and a
# list of suffixes to check for.
sub check_canonical_spelling
{
    my ($name, @suffixes) = @_;

    my $xname = &canonicalize ($name);
    if ($xname ne $name)
    {
    foreach my $xt (@suffixes)
    {
        macro_error ("$name$xt",
             "invalid variable `$name$xt'; should be `$xname$xt'")
        if variable_defined ("$name$xt");
    }
    }

    return $xname;
}


# handle_compile ()
# -----------------
# Set up the compile suite.
sub handle_compile ()
{
    return
      unless $get_object_extension_was_run;

    # Boilerplate.
    my $default_includes = '';
    if (! defined $options{'nostdinc'})
      {
    $default_includes = ' -I. -I$(srcdir)';

    if (variable_defined ('CONFIG_HEADER'))
      {
        foreach my $hdr (split (' ', &variable_value ('CONFIG_HEADER')))
          {
        $default_includes .= ' -I' . dirname ($hdr);
          }
      }
      }

    my (@mostly_rms, @dist_rms);
    foreach my $item (sort keys %compile_clean_files)
    {
    if ($compile_clean_files{$item} == MOSTLY_CLEAN)
    {
        push (@mostly_rms, "\t-rm -f $item");
    }
    elsif ($compile_clean_files{$item} == DIST_CLEAN)
    {
        push (@dist_rms, "\t-rm -f $item");
    }
    else
    {
        prog_error ("invalid entry in \%compile_clean_files");
    }
    }

    my ($coms, $vars, $rules) =
      &file_contents_internal (1, "$libdir/am/compile.am",
                   ('DEFAULT_INCLUDES' => $default_includes,
                'MOSTLYRMS' => join ("\n", @mostly_rms),
                'DISTRMS' => join ("\n", @dist_rms)));
    $output_vars .= $vars;
    $output_rules .= "$coms$rules";

    # Check for automatic de-ANSI-fication.
    if (defined $options{'ansi2knr'})
      {
    if (! $am_c_prototypes)
      {
        macro_error ('AUTOMAKE_OPTIONS',
             "option `ansi2knr' in use but `AM_C_PROTOTYPES' not in `$configure_ac'");
        &keyed_aclocal_warning ('AM_C_PROTOTYPES');
        # Only give this error once.
        $am_c_prototypes = 1;
      }

    # topdir is where ansi2knr should be.
    if ($options{'ansi2knr'} eq 'ansi2knr')
      {
        # Only require ansi2knr files if they should appear in
        # this directory.
        require_file_with_macro ('AUTOMAKE_OPTIONS', FOREIGN,
                     'ansi2knr.c', 'ansi2knr.1');

        # ansi2knr needs to be built before subdirs, so unshift it.
        unshift (@all, '$(ANSI2KNR)');
      }

    my $ansi2knr_dir = '';
    $ansi2knr_dir = dirname ($options{'ansi2knr'})
      if $options{'ansi2knr'} ne 'ansi2knr';

    $output_rules .= &file_contents ('ansi2knr',
                     ('ANSI2KNR-DIR' => $ansi2knr_dir));

    }
}

# handle_libtool ()
# -----------------
# Handle libtool rules.
sub handle_libtool
{
    return unless $seen_libtool;

    # Libtool requires some files, but only at top level.
    require_conf_file ($seen_libtool, FOREIGN, @libtool_files)
    if $relative_dir eq '.';

    my @libtool_rms;
    foreach my $item (sort keys %libtool_clean_directories)
    {
    my $dir = ($item eq '.') ? '' : "$item/";
    # .libs is for Unix, _libs for DOS.
    push (@libtool_rms, "\t-rm -rf ${dir}.libs ${dir}_libs");
    }

    # Output the libtool compilation rules.
    $output_rules .= &file_contents ('libtool',
                     ('LTRMS' => join ("\n", @libtool_rms)));
}

# handle_programs ()
# ------------------
# Handle C programs.
sub handle_programs
{
    my @proglist = &am_install_var ('progs', 'PROGRAMS',
                    'bin', 'sbin', 'libexec', 'pkglib',
                    'noinst', 'check');
    return if ! @proglist;

    my $seen_libobjs = 0;
    foreach my $one_file (@proglist)
    {
    my $obj = &get_object_extension ($one_file);

    # Canonicalize names and check for misspellings.
    my $xname = &check_canonical_spelling ($one_file, '_LDADD', '_LDFLAGS',
                           '_SOURCES', '_OBJECTS',
                           '_DEPENDENCIES');

    my $linker = &handle_source_transform ($xname, $one_file, $obj);

    my $xt = '';
    if (variable_defined ($xname . "_LDADD"))
    {
        if (&handle_lib_objects ($xname, $xname . '_LDADD'))
        {
        $seen_libobjs = 1;
        }
        $xt = '_LDADD';
    }
    else
    {
        # User didn't define prog_LDADD override.  So do it.
        &define_variable ($xname . '_LDADD', '$(LDADD)');

        # This does a bit too much work.  But we need it to
        # generate _DEPENDENCIES when appropriate.
        if (variable_defined ('LDADD'))
        {
        if (&handle_lib_objects ($xname, 'LDADD'))
        {
            $seen_libobjs = 1;
        }
        }
        elsif (! variable_defined ($xname . '_DEPENDENCIES'))
        {
        &define_variable ($xname . '_DEPENDENCIES', '');
        }
        $xt = '_SOURCES'
    }

    if (variable_defined ($xname . '_LIBADD'))
    {
        macro_error ($xname . '_LIBADD',
             "use `" . $xname . "_LDADD', not `"
             . $xname . "_LIBADD'");
    }

    if (! variable_defined ($xname . '_LDFLAGS'))
    {
        # Define the prog_LDFLAGS variable.
        &define_variable ($xname . '_LDFLAGS', '');
    }

    # Determine program to use for link.
    my $xlink;
    if (variable_defined ($xname . '_LINK'))
    {
        $xlink = $xname . '_LINK';
    }
    else
    {
        $xlink = $linker ? $linker : 'LINK';
    }

    # If the resulting program lies into a subdirectory,
    # make sure this directory will exist.
    my $dirstamp = require_build_directory_maybe ($one_file);

    # Don't add $(EXEEXT) if user already did.
    my $extension = ($one_file !~ /\$\(EXEEXT\)$/
             ? "\$(EXEEXT)"
             : '');

    $output_rules .= &file_contents ('program',
                     ('PROGRAM'  => $one_file,
                      'XPROGRAM' => $xname,
                      'XLINK'    => $xlink,
                      'DIRSTAMP' => $dirstamp,
                      'EXEEXT'   => $extension));
    }

    if (variable_defined ('LDADD') && &handle_lib_objects ('', 'LDADD'))
    {
    $seen_libobjs = 1;
    }

    if ($seen_libobjs)
    {
    foreach my $one_file (@proglist)
    {
        my $xname = &canonicalize ($one_file);

        if (variable_defined ($xname . '_LDADD'))
        {
        &check_libobjs_sources ($xname, $xname . '_LDADD');
        }
        elsif (variable_defined ('LDADD'))
        {
        &check_libobjs_sources ($xname, 'LDADD');
        }
    }
    }
}


# handle_libraries ()
# -------------------
# Handle libraries.
sub handle_libraries
{
    my @liblist = &am_install_var ('libs', 'LIBRARIES',
                   'lib', 'pkglib', 'noinst', 'check');
    return if ! @liblist;

    my @prefix = am_primary_prefixes ('LIBRARIES', 0, 'lib', 'pkglib',
                      'noinst', 'check');
    if (! defined $configure_vars{'RANLIB'}
    && @prefix)
      {
    macro_error ($prefix[0] . '_LIBRARIES',
             "library used but `RANLIB' not defined in `$configure_ac'");
    # Only get this error once.  If this is ever printed, we have
    # a bug.
    $configure_vars{'RANLIB'} = 'BUG';
      }

    my $seen_libobjs = 0;
    foreach my $onelib (@liblist)
    {
    # Check that the library fits the standard naming convention.
    if (basename ($onelib) !~ /^lib.*\.a/)
    {
        # FIXME should put line number here.  That means mapping
        # from library name back to variable name.
        &am_error ("`$onelib' is not a standard library name");
    }

    my $obj = &get_object_extension ($onelib);

    # Canonicalize names and check for misspellings.
    my $xlib = &check_canonical_spelling ($onelib, '_LIBADD', '_SOURCES',
                          '_OBJECTS', '_DEPENDENCIES',
                          '_AR');

    if (! variable_defined ($xlib . '_AR'))
    {
        &define_variable ($xlib . '_AR', '$(AR) cru');
    }

    if (variable_defined ($xlib . '_LIBADD'))
    {
        if (&handle_lib_objects ($xlib, $xlib . '_LIBADD'))
        {
        $seen_libobjs = 1;
        }
    }
    else
    {
        # Generate support for conditional object inclusion in
        # libraries.
        &define_variable ($xlib . "_LIBADD", '');
    }

    if (variable_defined ($xlib . '_LDADD'))
    {
        macro_error ($xlib . '_LDADD',
             "use `" . $xlib . "_LIBADD', not `"
             . $xlib . "_LDADD'");
    }

    # Make sure we at look at this.
    &examine_variable ($xlib . '_DEPENDENCIES');

    &handle_source_transform ($xlib, $onelib, $obj);

    # If the resulting library lies into a subdirectory,
    # make sure this directory will exist.
    my $dirstamp = require_build_directory_maybe ($onelib);

    $output_rules .= &file_contents ('library',
                     ('LIBRARY'  => $onelib,
                      'XLIBRARY' => $xlib,
                      'DIRSTAMP' => $dirstamp));
    }

    if ($seen_libobjs)
    {
    foreach my $onelib (@liblist)
    {
        my $xlib = &canonicalize ($onelib);
        if (variable_defined ($xlib . '_LIBADD'))
        {
        &check_libobjs_sources ($xlib, $xlib . '_LIBADD');
        }
    }
    }
}


# handle_ltlibraries ()
# ---------------------
# Handle shared libraries.
sub handle_ltlibraries
{
    my @liblist = &am_install_var ('ltlib', 'LTLIBRARIES',
                   'noinst', 'lib', 'pkglib', 'check');
    return if ! @liblist;

    my %instdirs;
    my @prefix = am_primary_prefixes ('LTLIBRARIES', 0, 'lib', 'pkglib',
                      'noinst', 'check');

    foreach my $key (@prefix)
      {
    if (!$seen_libtool)
      {
        macro_error ($key . '_LTLIBRARIES',
             "library used but `LIBTOOL' not defined in `$configure_ac'");
        # Only get this error once.  If this is ever printed,
        # we have a bug.
        $configure_vars{'LIBTOOL'} = 'BUG';
        $seen_libtool = $var_location{$key . '_LTLIBRARIES'};
      }

    # Get the installation directory of each library.
    (my $dir = $key) =~ s/^nobase_//;
    for (variable_value_as_list_recursive ($key . '_LTLIBRARIES', 'all'))
      {
        if ($instdirs{$_})
          {
        am_error ("`$_' is already going to be installed in `$instdirs{$_}'");
          }
        else
          {
        $instdirs{$_} = $dir;
          }
      }
      }

    my $seen_libobjs = 0;
    foreach my $onelib (@liblist)
    {
    my $obj = &get_object_extension ($onelib);

    # Canonicalize names and check for misspellings.
    my $xlib = &check_canonical_spelling ($onelib, '_LIBADD', '_LDFLAGS',
                          '_SOURCES', '_OBJECTS',
                          '_DEPENDENCIES');

    if (! variable_defined ($xlib . '_LDFLAGS'))
    {
        # Define the lib_LDFLAGS variable.
        &define_variable ($xlib . '_LDFLAGS', '');
    }

    # Check that the library fits the standard naming convention.
        my $libname_rx = "^lib.*\.la";
    if ((variable_defined ($xlib . '_LDFLAGS')
         && grep (/-module/, &variable_value_as_list_recursive (
                        $xlib . '_LDFLAGS', 'all')))
        || (variable_defined ('LDFLAGS')
        && grep (/-module/, &variable_value_as_list_recursive (
                    'LDFLAGS', 'all'))))
    {
        # Relax name checking for libtool modules.
            $libname_rx = "\.la";
    }
    if (basename ($onelib) !~ /$libname_rx$/)
    {
        # FIXME this should only be a warning for foreign packages
        # FIXME should put line number here.  That means mapping
        # from library name back to variable name.
        &am_error ("`$onelib' is not a standard libtool library name");
    }

    if (variable_defined ($xlib . '_LIBADD'))
    {
        if (&handle_lib_objects ($xlib, $xlib . '_LIBADD'))
        {
        $seen_libobjs = 1;
        }
    }
    else
    {
        # Generate support for conditional object inclusion in
        # libraries.
        &define_variable ($xlib . "_LIBADD", '');
    }

    if (variable_defined ($xlib . '_LDADD'))
    {
        macro_error ($xlib . '_LDADD',
             "use `" . $xlib . "_LIBADD', not `"
             . $xlib . "_LDADD'");
    }

    # Make sure we at look at this.
    &examine_variable ($xlib . '_DEPENDENCIES');

    my $linker = &handle_source_transform ($xlib, $onelib, $obj);

    # Determine program to use for link.
    my $xlink;
    if (variable_defined ($xlib . '_LINK'))
    {
        $xlink = $xlib . '_LINK';
    }
    else
    {
        $xlink = $linker ? $linker : 'LINK';
    }

    my $rpath;
    if ($instdirs{$onelib} eq 'EXTRA'
        || $instdirs{$onelib} eq 'noinst'
        || $instdirs{$onelib} eq 'check')
    {
        # It's an EXTRA_ library, so we can't specify -rpath,
        # because we don't know where the library will end up.
        # The user probably knows, but generally speaking automake
        # doesn't -- and in fact configure could decide
        # dynamically between two different locations.
        $rpath = '';
    }
    else
    {
        $rpath = ('-rpath $(' . $instdirs{$onelib} . 'dir)');
    }

    # If the resulting library lies into a subdirectory,
    # make sure this directory will exist.
    my $dirstamp = require_build_directory_maybe ($onelib);

    $output_rules .= &file_contents ('ltlibrary',
                     ('LTLIBRARY'  => $onelib,
                      'XLTLIBRARY' => $xlib,
                      'RPATH'      => $rpath,
                      'XLINK'      => $xlink,
                      'DIRSTAMP'   => $dirstamp));
    }

    if ($seen_libobjs)
    {
    foreach my $onelib (@liblist)
    {
        my $xlib = &canonicalize ($onelib);
        if (variable_defined ($xlib . '_LIBADD'))
        {
        &check_libobjs_sources ($xlib, $xlib . '_LIBADD');
        }
    }
    }
}

# See if any _SOURCES variable were misspelled.  Also, make sure that
# EXTRA_ variables don't contain configure substitutions.
sub check_typos ()
{
    # It is ok if the user sets this particular variable.
    &examine_variable ('AM_LDFLAGS');

    foreach my $varname (keys %var_value)
    {
    foreach my $primary ('_SOURCES', '_LIBADD', '_LDADD', '_LDFLAGS',
                 '_DEPENDENCIES')
    {
        macro_error ($varname,
             "invalid unused variable name: `$varname'")
        # Note that a configure variable is always legitimate.
        # It is natural to name such variables after the
        # primary, so we explicitly allow it.
        if $varname =~ /$primary$/ && ! $content_seen{$varname}
               && ! exists $configure_vars{$varname};
    }
    }
}


# Handle scripts.
sub handle_scripts
{
    # NOTE we no longer automatically clean SCRIPTS, because it is
    # useful to sometimes distribute scripts verbatim.  This happens
    # eg in Automake itself.
    &am_install_var ('-candist', 'scripts', 'SCRIPTS',
             'bin', 'sbin', 'libexec', 'pkgdata',
             'noinst', 'check');
}


# ($OUTFILE, $VFILE, @CLEAN_FILES)
# &scan_texinfo_file ($FILENAME)
# ------------------------------
# $OUTFILE is the name of the info file produced by $FILENAME.
# $VFILE is the name of the version.texi file used (empty if none).
# @CLEAN_FILES is the list of by products (indexes etc.)
sub scan_texinfo_file
{
    my ($filename) = @_;

    # These are always created, no matter whether indexes are used or not.
    # (Actually tmp is only created if an @macro is used and a certain e-TeX
    # feature is not available.)
    my @clean_suffixes = qw(aux dvi log ps toc tmp
                cp fn ky vr tp pg); # grep new.*index texinfo.tex

    # There are predefined indexes which don't follow the regular rules.
    my %predefined_index = qw(c cps
                  f fns
                  k kys
                  v vrs
                  t tps
                  p pgs);

    # There are commands which include a hidden index command.
    my %hidden_index = (tp => 'tps');
    $hidden_index{$_} = 'fns' foreach qw(fn un typefn typefun max spec
                     op typeop method typemethod);
    $hidden_index{$_} = 'vrs' foreach qw(vr var typevr typevar opt cv
                     ivar typeivar);

    # Indexes stored into another one.  In this case, the *.??s file
    # is not created.
    my @syncodeindexes = ();

    my $texi = new Automake::XFile "< $filename";
    verbose "reading $filename";

    my ($outfile, $vfile);
    while ($_ = $texi->getline)
    {
      if (/^\@setfilename +(\S+)/)
      {
        $outfile = $1;
        if ($outfile =~ /\.(.+)$/ && $1 ne 'info')
          {
            file_error ("$filename:$.",
            "output `$outfile' has unrecognized extension");
            return;
          }
      }
      # A "version.texi" file is actually any file whose name
      # matches "vers*.texi".
      elsif (/^\@include\s+(vers[^.]*\.texi)\s*$/)
      {
        $vfile = $1;
      }

      # Try to find what are the indexes which are used.

      # Creating a new category of index.
      elsif (/^\@def(code)?index (\w+)/)
      {
        push @clean_suffixes, $2;
      }

      # Storing in a predefined index.
      elsif (/^\@([cfkvtp])index /)
      {
        push @clean_suffixes, $predefined_index{$1};
      }
      elsif (/^\@def(\w+) /)
      {
    push @clean_suffixes, $hidden_index{$1}
      if defined $hidden_index{$1};
      }

      # Merging an index into an another.
      elsif (/^\@syn(code)?index (\w+) (\w+)/)
      {
    push @syncodeindexes, "$2s";
    push @clean_suffixes, "$3s";
      }

    }

    if ($outfile eq '')
      {
    &am_error ("`$filename' missing \@setfilename");
    return;
      }

    my $infobase = basename ($filename);
    $infobase =~ s/\.te?xi(nfo)?$//;
    my %clean_files = map { +"$infobase.$_" => 1 } @clean_suffixes;
    grep { delete $clean_files{"$infobase.$_"} } @syncodeindexes;
    return ($outfile, $vfile, (sort keys %clean_files));
}


# ($DO-SOMETHING, $TEXICLEANS)
# handle_texinfo_helper ()
# ------------------------
# Handle all Texinfo source; helper for handle_texinfo
sub handle_texinfo_helper
{
    macro_error ('TEXINFOS',
         "`TEXINFOS' is an anachronism; use `info_TEXINFOS'")
    if variable_defined ('TEXINFOS');
    return (0, '') if (! variable_defined ('info_TEXINFOS')
               && ! variable_defined ('html_TEXINFOS'));

    if (variable_defined ('html_TEXINFOS'))
    {
    macro_error ('html_TEXINFOS',
             "HTML generation not yet supported");
    return (0, '');
    }

    my @texis = &variable_value_as_list_recursive ('info_TEXINFOS', 'all');

    my (@info_deps_list, @dvis_list, @texi_deps);
    my %versions;
    my $done = 0;
    my @texi_cleans;
    my $canonical;

    my %texi_suffixes;
    foreach my $info_cursor (@texis)
    {
        my $infobase = $info_cursor;
        $infobase =~ s/\.(txi|texinfo|texi)$//;

    if ($infobase eq $info_cursor)
    {
        # FIXME: report line number.
        &am_error ("texinfo file `$info_cursor' has unrecognized extension");
        next;
    }
    $texi_suffixes{$1} = 1;

    # If 'version.texi' is referenced by input file, then include
    # automatic versioning capability.
    my ($out_file, $vtexi, @clean_files) =
      &scan_texinfo_file ("$relative_dir/$info_cursor")
        or next;
    push (@texi_cleans, @clean_files);

    if ($vtexi)
    {
        &am_error ("`$vtexi', included in `$info_cursor', also included in `$versions{$vtexi}'")
        if (defined $versions{$vtexi});
        $versions{$vtexi} = $info_cursor;

        # We number the stamp-vti files.  This is doable since the
        # actual names don't matter much.  We only number starting
        # with the second one, so that the common case looks nice.
        my $vti = ($done ? $done : 'vti');
        ++$done;

        # This is ugly, but it is our historical practice.
        if ($config_aux_dir_set_in_configure_in)
        {
        require_conf_file_with_macro ('info_TEXINFOS', FOREIGN,
                          'mdate-sh');
        }
        else
        {
        require_file_with_macro ('info_TEXINFOS', FOREIGN,
                     'mdate-sh');
        }

        my $conf_dir;
        if ($config_aux_dir_set_in_configure_in)
        {
        $conf_dir = $config_aux_dir;
        $conf_dir .= '/' unless $conf_dir =~ /\/$/;
        }
        else
        {
        $conf_dir = '$(srcdir)/';
        }
        $output_rules .= &file_contents ('texi-vers',
                         ('TEXI'  => $info_cursor,
                          'VTI'   => $vti,
                          'VTEXI' => $vtexi,
                          'MDDIR' => $conf_dir));
    }

    # If user specified file_TEXINFOS, then use that as explicit
    # dependency list.
    @texi_deps = ();
    push (@texi_deps, $info_cursor);
    # Prefix with $(srcdir) because some version of make won't
    # work if the target has it and the dependency doesn't.
    push (@texi_deps, '$(srcdir)/' . $vtexi) if $vtexi;

    my $canonical = &canonicalize ($infobase);
    if (variable_defined ($canonical . "_TEXINFOS"))
    {
        push (@texi_deps, '$(' . $canonical . '_TEXINFOS)');
        &push_dist_common ('$(' . $canonical . '_TEXINFOS)');
    }

    $output_rules .= ("\n" . $out_file . ": "
              . "@texi_deps"
              . "\n" . $infobase . ".dvi: "
              . "@texi_deps"
              . "\n");

    push (@info_deps_list, $out_file);
    push (@dvis_list, $infobase . '.dvi');
    }

    # Handle location of texinfo.tex.
    my $need_texi_file = 0;
    my $texinfodir;
    if ($cygnus_mode)
    {
        $texinfodir = '$(top_srcdir)/../texinfo';
    &define_variable ('TEXINFO_TEX', "$texinfodir/texinfo.tex");
    }
    elsif ($config_aux_dir_set_in_configure_in)
    {
        $texinfodir = $config_aux_dir;
    &define_variable ('TEXINFO_TEX', "$texinfodir/texinfo.tex");
    $need_texi_file = 2; # so that we require_conf_file later
    }
    elsif (variable_defined ('TEXINFO_TEX'))
    {
    # The user defined TEXINFO_TEX so assume he knows what he is
    # doing.
        $texinfodir = ('$(srcdir)/'
               . dirname (&variable_value ('TEXINFO_TEX')));
    }
    else
    {
        $texinfodir = '$(srcdir)';
    $need_texi_file = 1;
    }

    foreach my $txsfx (sort keys %texi_suffixes)
    {
    $output_rules .= &file_contents ('texibuild',
                     ('TEXINFODIR' => $texinfodir,
                      'SUFFIX'     => $txsfx));
    }

    # The return value.
    my $texiclean = &pretty_print_internal ("", "\t  ", @texi_cleans);

    push (@dist_targets, 'dist-info');

    if (! defined $options{'no-installinfo'})
    {
    # Make sure documentation is made and installed first.  Use
    # $(INFO_DEPS), not 'info', because otherwise recursive makes
    # get run twice during "make all".
    unshift (@all, '$(INFO_DEPS)');
    }

    &define_variable ("INFO_DEPS", "@info_deps_list");
    &define_variable ("DVIS", "@dvis_list");
    # This next isn't strictly needed now -- the places that look here
    # could easily be changed to look in info_TEXINFOS.  But this is
    # probably better, in case noinst_TEXINFOS is ever supported.
    &define_variable ("TEXINFOS", &variable_value ('info_TEXINFOS'));

    # Do some error checking.  Note that this file is not required
    # when in Cygnus mode; instead we defined TEXINFO_TEX explicitly
    # up above.
    if ($need_texi_file && ! defined $options{'no-texinfo.tex'})
    {
    if ($need_texi_file > 1)
    {
        require_conf_file_with_macro ('info_TEXINFOS', FOREIGN,
                      'texinfo.tex');
    }
    else
    {
        require_file_with_macro ('info_TEXINFOS', FOREIGN, 'texinfo.tex');
    }
    }

    return (1, $texiclean);
}

# handle_texinfo ()
# -----------------
# Handle all Texinfo source.
sub handle_texinfo
{
    my ($do_something, $texiclean) = handle_texinfo_helper ();
    $output_rules .=  &file_contents ('texinfos',
                      ('TEXICLEAN' => $texiclean,
                       'LOCAL-TEXIS' => $do_something));
}

# Handle any man pages.
sub handle_man_pages
{
    macro_error ('MANS', "`MANS' is an anachronism; use `man_MANS'")
    if variable_defined ('MANS');

    # Find all the sections in use.  We do this by first looking for
    # "standard" sections, and then looking for any additional
    # sections used in man_MANS.
    my (%sections, %vlist);
    # We handle nodist_ for uniformity.  man pages aren't distributed
    # by default so it isn't actually very important.
    foreach my $pfx ('', 'dist_', 'nodist_')
    {
    # Add more sections as needed.
    foreach my $section ('0'..'9', 'n', 'l')
    {
        if (variable_defined ($pfx . 'man' . $section . '_MANS'))
        {
        $sections{$section} = 1;
        $vlist{'$(' . $pfx . 'man' . $section . '_MANS)'} = 1;

        &push_dist_common ('$(' . $pfx . 'man' . $section . '_MANS)')
            if $pfx eq 'dist_';
        }
    }

    if (variable_defined ($pfx . 'man_MANS'))
    {
        $vlist{'$(' . $pfx . 'man_MANS)'} = 1;
        foreach (&variable_value_as_list_recursive ($pfx . 'man_MANS', 'all'))
        {
        # A page like `foo.1c' goes into man1dir.
        if (/\.([0-9a-z])([a-z]*)$/)
        {
            $sections{$1} = 1;
        }
        }

        &push_dist_common ('$(' . $pfx . 'man_MANS)')
        if $pfx eq 'dist_';
    }
    }

    return unless %sections;

    # Now for each section, generate an install and unintall rule.
    # Sort sections so output is deterministic.
    foreach my $section (sort keys %sections)
    {
    $output_rules .= &file_contents ('mans', ('SECTION' => $section));
    }

    my @mans = sort keys %vlist;
    $output_vars .= file_contents ('mans-vars',
                   ('MANS' => "@mans"));

    if (! defined $options{'no-installman'})
    {
    push (@all, '$(MANS)');
    }
}

# Handle DATA variables.
sub handle_data
{
    &am_install_var ('-noextra', '-candist', 'data', 'DATA',
             'data', 'sysconf', 'sharedstate', 'localstate',
             'pkgdata', 'noinst', 'check');
}

# Handle TAGS.
sub handle_tags
{
    my @tag_deps = ();
    if (variable_defined ('SUBDIRS'))
    {
    $output_rules .= ("tags-recursive:\n"
              . "\tlist=\'\$(SUBDIRS)\'; for subdir in \$\$list; do \\\n"
              # Never fail here if a subdir fails; it
              # isn't important.
              . "\t  test \"\$\$subdir\" = . || (cd \$\$subdir"
              . " && \$(MAKE) \$(AM_MAKEFLAGS) tags); \\\n"
              . "\tdone\n");
    push (@tag_deps, 'tags-recursive');
    &depend ('.PHONY', 'tags-recursive');
    }

    if (&saw_sources_p (1)
    || variable_defined ('ETAGS_ARGS')
    || @tag_deps)
    {
    my @config;
    foreach my $spec (@config_headers)
    {
        my ($out, @ins) = split_config_file_spec ($spec);
        foreach my $in (@ins)
          {
        # If the config header source is in this directory,
        # require it.
        push @config, basename ($in)
          if $relative_dir eq dirname ($in);
          }
    }
    $output_rules .= &file_contents ('tags',
                     ('CONFIG' => "@config",
                      'DIRS'   => "@tag_deps"));
    &examine_variable ('TAGS_DEPENDENCIES');
    }
    elsif (variable_defined ('TAGS_DEPENDENCIES'))
    {
    macro_error ('TAGS_DEPENDENCIES',
             "doesn't make sense to define `TAGS_DEPENDENCIES' without sources or `ETAGS_ARGS'");
    }
    else
    {
    # Every Makefile must define some sort of TAGS rule.
    # Otherwise, it would be possible for a top-level "make TAGS"
    # to fail because some subdirectory failed.
    $output_rules .= "tags: TAGS\nTAGS:\n\n";
    }
}

# Handle multilib support.
sub handle_multilib
{
    if ($seen_multilib && $relative_dir eq '.')
    {
    $output_rules .= &file_contents ('multilib');
    }
}


# $BOOLEAN
# &for_dist_common ($A, $B)
# -------------------------
# Subroutine for &handle_dist: sort files to dist.
#
# We put README first because it then becomes easier to make a
# Usenet-compliant shar file (in these, README must be first).
#
# FIXME: do more ordering of files here.
sub for_dist_common
{
    return 0
        if $a eq $b;
    return -1
        if $a eq 'README';
    return 1
        if $b eq 'README';
    return $a cmp $b;
}


# handle_dist ($MAKEFILE)
# -----------------------
# Handle 'dist' target.
sub handle_dist
{
    my ($makefile) = @_;

    # `make dist' isn't used in a Cygnus-style tree.
    # Omit the rules so that people don't try to use them.
    return if $cygnus_mode;

    # Look for common files that should be included in distribution.
    # If the aux dir is set, and it does not have a Makefile.am, then
    # we check for these files there as well.
    my $check_aux = 0;
    my $auxdir = '';
    if ($relative_dir eq '.'
    && $config_aux_dir_set_in_configure_in)
    {
    ($auxdir = $config_aux_dir) =~ s,^\$\(top_srcdir\)/,,;
    if (! &is_make_dir ($auxdir))
    {
        $check_aux = 1;
    }
    }
    foreach my $cfile (@common_files)
    {
    if (-f ($relative_dir . "/" . $cfile)
        # The file might be absent, but if it can be built it's ok.
        || exists $targets{$cfile})
    {
        &push_dist_common ($cfile);
    }

    # Don't use `elsif' here because a file might meaningfully
    # appear in both directories.
    if ($check_aux && -f ($auxdir . '/' . $cfile))
    {
        &push_dist_common ($auxdir . '/' . $cfile);
    }
    }

    # We might copy elements from $configure_dist_common to
    # %dist_common if we think we need to.  If the file appears in our
    # directory, we would have discovered it already, so we don't
    # check that.  But if the file is in a subdir without a Makefile,
    # we want to distribute it here if we are doing `.'.  Ugly!
    if ($relative_dir eq '.')
    {
       foreach my $file (split (' ' , $configure_dist_common))
       {
       push_dist_common ($file)
         unless is_make_dir (dirname ($file));
       }
    }



    # Files to distributed.  Don't use &variable_value_as_list_recursive
    # as it recursively expands `$(dist_pkgdata_DATA)' etc.
    check_variable_defined_unconditionally ('DIST_COMMON');
    my @dist_common = split (' ', variable_value ('DIST_COMMON', 'TRUE'));
    @dist_common = uniq (sort for_dist_common (@dist_common));
    pretty_print ('DIST_COMMON = ', "\t", @dist_common);

    # Now that we've processed DIST_COMMON, disallow further attempts
    # to set it.
    $handle_dist_run = 1;

    # Scan EXTRA_DIST to see if we need to distribute anything from a
    # subdir.  If so, add it to the list.  I didn't want to do this
    # originally, but there were so many requests that I finally
    # relented.
    if (variable_defined ('EXTRA_DIST'))
    {
    # FIXME: This should be fixed to work with conditionals.  That
    # will require only making the entries in %dist_dirs under the
    # appropriate condition.  This is meaningful if the nature of
    # the distribution should depend upon the configure options
    # used.
    foreach (&variable_value_as_list_recursive ('EXTRA_DIST', ''))
    {
        next if /^\@.*\@$/;
        next unless s,/+[^/]+$,,;
        $dist_dirs{$_} = 1
        unless $_ eq '.';
    }
    }

    # We have to check DIST_COMMON for extra directories in case the
    # user put a source used in AC_OUTPUT into a subdir.
    foreach (&variable_value_as_list_recursive ('DIST_COMMON', 'all'))
    {
    next if /^\@.*\@$/;
    next unless s,/+[^/]+$,,;
    $dist_dirs{$_} = 1
        unless $_ eq '.';
    }

    # Rule to check whether a distribution is viable.
    my %transform = ('DISTCHECK-HOOK' => &target_defined ('distcheck-hook'),
             'GETTEXT'        => $seen_gettext);

    # Prepend $(distdir) to each directory given.
    my %rewritten = map { '$(distdir)/' . "$_" => 1 } keys %dist_dirs;
    $transform{'DISTDIRS'} = join (' ', sort keys %rewritten);

    # If we have SUBDIRS, create all dist subdirectories and do
    # recursive build.
    if (variable_defined ('SUBDIRS'))
    {
    # If SUBDIRS is conditionally defined, then set DIST_SUBDIRS
    # to all possible directories, and use it.  If DIST_SUBDIRS is
    # defined, just use it.
    my $dist_subdir_name;
    # Note that we check DIST_SUBDIRS first on purpose.  At least
    # one project uses so many conditional subdirectories that
    # calling variable_conditionally_defined on SUBDIRS will cause
    # automake to grow to 150Mb.  Sigh.
    if (variable_defined ('DIST_SUBDIRS')
        || variable_conditionally_defined ('SUBDIRS'))
    {
        $dist_subdir_name = 'DIST_SUBDIRS';
        if (! variable_defined ('DIST_SUBDIRS'))
        {
        define_pretty_variable
          ('DIST_SUBDIRS', '',
           uniq (&variable_value_as_list_recursive ('SUBDIRS', 'all')));
        }
    }
    else
    {
        $dist_subdir_name = 'SUBDIRS';
        # We always define this because that is what `distclean'
        # wants.
        define_pretty_variable ('DIST_SUBDIRS', '', '$(SUBDIRS)');
    }

    $transform{'DIST_SUBDIR_NAME'} = $dist_subdir_name;
    }

    # If the target `dist-hook' exists, make sure it is run.  This
    # allows users to do random weird things to the distribution
    # before it is packaged up.
    push (@dist_targets, 'dist-hook')
      if &target_defined ('dist-hook');
    $transform{'DIST-TARGETS'} = join(' ', @dist_targets);

    # Defining $(DISTDIR).
    $transform{'DISTDIR'} = !variable_defined('distdir');
    $transform{'TOP_DISTDIR'} = backname ($relative_dir);

    $output_rules .= &file_contents ('distdir', %transform);
}


# Handle subdirectories.
sub handle_subdirs
{
    return
      unless variable_defined ('SUBDIRS');

    # Make sure each directory mentioned in SUBDIRS actually exists.
    foreach my $dir (&variable_value_as_list_recursive ('SUBDIRS', 'all'))
    {
    # Skip directories substituted by configure.
    next if $dir =~ /^\@.*\@$/;

    if (! -d $am_relative_dir . '/' . $dir)
    {
        macro_error ('SUBDIRS',
             "required directory $am_relative_dir/$dir does not exist");
        next;
    }

    macro_error ('SUBDIRS', "directory should not contain `/'")
        if $dir =~ /\//;
    }

    $output_rules .= &file_contents ('subdirs');
    variable_pretty_output ('RECURSIVE_TARGETS', 'TRUE');
}


# ($REGEN, @DEPENDENCIES)
# &scan_aclocal_m4
# ----------------
# If aclocal.m4 creation is automated, return the list of its dependencies.
sub scan_aclocal_m4
{
    my $regen_aclocal = 0;

    return (0, ())
      unless $relative_dir eq '.';

    &examine_variable ('CONFIG_STATUS_DEPENDENCIES');
    &examine_variable ('CONFIGURE_DEPENDENCIES');

    if (-f 'aclocal.m4')
    {
    &define_variable ("ACLOCAL_M4", '$(top_srcdir)/aclocal.m4');
    &push_dist_common ('aclocal.m4');

    my $aclocal = new Automake::XFile "< aclocal.m4";
    my $line = $aclocal->getline;
    $regen_aclocal = $line =~ 'generated automatically by aclocal';
    }

    my @ac_deps = ();

    if (-f 'acinclude.m4')
    {
    $regen_aclocal = 1;
    push @ac_deps, 'acinclude.m4';
    }

    if (variable_defined ('ACLOCAL_M4_SOURCES'))
    {
    push (@ac_deps, '$(ACLOCAL_M4_SOURCES)');
    }
    elsif (variable_defined ('ACLOCAL_AMFLAGS'))
    {
    # Scan all -I directories for m4 files.  These are our
    # dependencies.
    my $examine_next = 0;
    foreach my $amdir (&variable_value_as_list_recursive ('ACLOCAL_AMFLAGS', ''))
    {
        if ($examine_next)
        {
        $examine_next = 0;
        if ($amdir !~ /^\// && -d $amdir)
        {
            foreach my $ac_dep (&my_glob ($amdir . '/*.m4'))
            {
            $ac_dep =~ s/^\.\/+//;
            push (@ac_deps, $ac_dep)
              unless $ac_dep eq "aclocal.m4"
                || $ac_dep eq "acinclude.m4";
            }
        }
        }
        elsif ($amdir eq '-I')
        {
        $examine_next = 1;
        }
    }
    }

    # Note that it might be possible that aclocal.m4 doesn't exist but
    # should be auto-generated.  This case probably isn't very
    # important.

    return ($regen_aclocal, @ac_deps);
}


# @DEPENDENCY
# &rewrite_inputs_into_dependencies ($ADD_SRCDIR, @INPUTS)
# --------------------------------------------------------
# Rewrite a list of input files into a form suitable to put on a
# dependency list.  The idea is that if an input file has a directory
# part the same as the current directory, then the directory part is
# simply removed.  But if the directory part is different, then
# $(top_srcdir) is prepended.  Among other things, this is used to
# generate the dependency list for the output files generated by
# AC_OUTPUT.  Consider what the dependencies should look like in this
# case:
#   AC_OUTPUT(src/out:src/in1:lib/in2)
# The first argument, ADD_SRCDIR, is 1 if $(top_srcdir) should be added.
# If 0 then files that require this addition will simply be ignored.
sub rewrite_inputs_into_dependencies ($@)
{
    my ($add_srcdir, @inputs) = @_;
    my @newinputs;

    foreach my $single (@inputs)
    {
    if (dirname ($single) eq $relative_dir)
    {
        push (@newinputs, basename ($single));
    }
    elsif ($add_srcdir)
    {
        push (@newinputs, '$(top_srcdir)/' . $single);
    }
    }

    return @newinputs;
}

# Handle remaking and configure stuff.
# We need the name of the input file, to do proper remaking rules.
sub handle_configure
{
    my ($local, $input, @secondary_inputs) = @_;

    my $input_base = basename ($input);
    my $local_base = basename ($local);

    my $amfile = $input_base . '.am';
    # We know we can always add '.in' because it really should be an
    # error if the .in was missing originally.
    my $infile = '$(srcdir)/' . $input_base . '.in';
    my $colon_infile = '';
    if ($local ne $input || @secondary_inputs)
    {
    $colon_infile = ':' . $input . '.in';
    }
    $colon_infile .= ':' . join (':', @secondary_inputs)
    if @secondary_inputs;

    my @rewritten = rewrite_inputs_into_dependencies (1, @secondary_inputs);

    my ($regen_aclocal_m4, @aclocal_m4_deps) = scan_aclocal_m4 ();

    $output_rules .=
      &file_contents ('configure',
              ('MAKEFILE'
               => $local_base,
               'MAKEFILE-DEPS'
               => "@rewritten",
               'CONFIG-MAKEFILE'
               => ((($relative_dir eq '.') ? '$@' : '$(subdir)/$@')
               . $colon_infile),
               'MAKEFILE-IN'
               => $infile,
               'MAKEFILE-IN-DEPS'
               => "@include_stack",
               'MAKEFILE-AM'
               => $amfile,
               'STRICTNESS'
               => $cygnus_mode ? 'cygnus' : $strictness_name,
               'USE-DEPS'
               => $cmdline_use_dependencies ? '' : ' --ignore-deps',
               'MAKEFILE-AM-SOURCES'
               =>  "$input$colon_infile",
               'REGEN-ACLOCAL-M4'
               => $regen_aclocal_m4,
               'ACLOCAL_M4_DEPS'
               => "@aclocal_m4_deps"));

    if ($relative_dir eq '.')
    {
    &push_dist_common ('acconfig.h')
        if -f 'acconfig.h';
    }

    # If we have a configure header, require it.
    my $hdr_index = 0;
    my @distclean_config;
    foreach my $spec (@config_headers)
      {
    $hdr_index += 1;
    # $CONFIG_H_PATH: config.h from top level.
    my ($config_h_path, @ins) = split_config_file_spec ($spec);
    my $config_h_dir = dirname ($config_h_path);

    # If the header is in the current directory we want to build
    # the header here.  Otherwise, if we're at the topmost
    # directory and the header's directory doesn't have a
    # Makefile, then we also want to build the header.
    if ($relative_dir eq $config_h_dir
        || ($relative_dir eq '.' && ! &is_make_dir ($config_h_dir)))
    {
        my ($cn_sans_dir, $stamp_dir);
        if ($relative_dir eq $config_h_dir)
        {
        $cn_sans_dir = basename ($config_h_path);
        $stamp_dir = '';
        }
        else
        {
        $cn_sans_dir = $config_h_path;
        if ($config_h_dir eq '.')
        {
            $stamp_dir = '';
        }
        else
        {
            $stamp_dir = $config_h_dir . '/';
        }
        }

        # Compute relative path from directory holding output
        # header to directory holding input header.  FIXME:
        # doesn't handle case where we have multiple inputs.
        my $in0_sans_dir;
        if (dirname ($ins[0]) eq $relative_dir)
        {
        $in0_sans_dir = basename ($ins[0]);
        }
        else
        {
            $in0_sans_dir = backname ($relative_dir) . '/' . $ins[0];
        }

        require_file ($config_header_location, FOREIGN, $in0_sans_dir);

        # Header defined and in this directory.
        my @files;
        if (-f $config_h_path . '.top')
        {
        push (@files, "$cn_sans_dir.top");
        }
        if (-f $config_h_path . '.bot')
        {
        push (@files, "$cn_sans_dir.bot");
        }

        push_dist_common (@files);

        # For now, acconfig.h can only appear in the top srcdir.
        if (-f 'acconfig.h')
        {
            push (@files, '$(top_srcdir)/acconfig.h');
        }

        my $stamp = "${stamp_dir}stamp-h${hdr_index}";
            $output_rules .=
          file_contents ('remake-hdr',
                 ('FILES'         => "@files",
                  'CONFIG_H'      => $cn_sans_dir,
                  'CONFIG_HIN'    => $in0_sans_dir,
                  'CONFIG_H_PATH' => $config_h_path,
                  'STAMP'         => "$stamp"));

        push @distclean_config, $cn_sans_dir, $stamp;
    }
    }

    $output_rules .= file_contents ('clean-hdr',
                    ('FILES' => "@distclean_config"))
      if @distclean_config;

    # Set location of mkinstalldirs.
    define_variable ('mkinstalldirs',
             ('$(SHELL) ' . $config_aux_dir . '/mkinstalldirs'));

    macro_error ('CONFIG_HEADER',
         "`CONFIG_HEADER' is an anachronism; now determined from `$configure_ac'")
    if variable_defined ('CONFIG_HEADER');

    my @config_h;
    foreach my $spec (@config_headers)
      {
    my ($out, @ins) = split_config_file_spec ($spec);
    # Generate CONFIG_HEADER define.
    if ($relative_dir eq dirname ($out))
    {
        push @config_h, basename ($out);
    }
    else
    {
        push @config_h, "\$(top_builddir)/$out";
    }
    }
    define_variable ("CONFIG_HEADER", "@config_h")
      if @config_h;

    # Now look for other files in this directory which must be remade
    # by config.status, and generate rules for them.
    my @actual_other_files = ();
    foreach my $lfile (@other_input_files)
    {
        my $file;
    my @inputs;
    if ($lfile =~ /^([^:]*):(.*)$/)
    {
        # This is the ":" syntax of AC_OUTPUT.
        $file = $1;
        @inputs = split (':', $2);
    }
    else
    {
        # Normal usage.
        $file = $lfile;
        @inputs = $file . '.in';
    }

    # Automake files should not be stored in here, but in %MAKE_LIST.
        prog_error ("$lfile in \@other_input_files")
      if -f $file . '.am';

    my $local = basename ($file);

    # Make sure the dist directory for each input file is created.
    # We only have to do this at the topmost level though.  This
    # is a bit ugly but it easier than spreading out the logic,
    # especially in cases like AC_OUTPUT(foo/out:bar/in), where
    # there is no Makefile in bar/.
    if ($relative_dir eq '.')
    {
        foreach (@inputs)
        {
        $dist_dirs{dirname ($_)} = 1;
        }
    }

    # We skip files that aren't in this directory.  However, if
    # the file's directory does not have a Makefile, and we are
    # currently doing `.', then we create a rule to rebuild the
    # file in the subdir.
    my $fd = dirname ($file);
    if ($fd ne $relative_dir)
    {
        if ($relative_dir eq '.' && ! &is_make_dir ($fd))
        {
        $local = $file;
        }
        else
        {
        next;
        }
    }

    my @rewritten_inputs = rewrite_inputs_into_dependencies (1, @inputs);
    $output_rules .= ($local . ': '
              . '$(top_builddir)/config.status '
              . "@rewritten_inputs\n"
              . "\t"
              . 'cd $(top_builddir) && '
              . '$(SHELL) ./config.status '
              . ($relative_dir eq '.' ? '' : '$(subdir)/')
              . '$@'
              . "\n");
    push (@actual_other_files, $local);

    # Require all input files.
    require_file ($ac_config_files_location, FOREIGN,
              rewrite_inputs_into_dependencies (0, @inputs));
    }

    # These files get removed by "make clean".
    define_pretty_variable ('CONFIG_CLEAN_FILES', '', @actual_other_files);
}

# Handle C headers.
sub handle_headers
{
    my @r = &am_install_var ('-defaultdist', 'header', 'HEADERS', 'include',
                 'oldinclude', 'pkginclude',
                 'noinst', 'check');
    foreach (@r)
    {
    next unless /\..*$/;
    &saw_extension ($&);
    }
}

sub handle_gettext
{
    return if ! $seen_gettext || $relative_dir ne '.';

    if (! variable_defined ('SUBDIRS'))
    {
    conf_error ("AM_GNU_GETTEXT used but SUBDIRS not defined");
    return;
    }

    my @subdirs = &variable_value_as_list_recursive ('SUBDIRS', 'all');
    macro_error ('SUBDIRS',
         "AM_GNU_GETTEXT used but `po' not in SUBDIRS")
    if ! grep ($_ eq 'po', @subdirs);

    # intl/ is not required when AM_GNU_GETTEXT is called with
    # the `external' option.
    macro_error ('SUBDIRS',
         "AM_GNU_GETTEXT used but `intl' not in SUBDIRS")
    if (! $seen_gettext_external
        && ! grep ($_ eq 'intl', @subdirs));

    require_file ($ac_gettext_location, GNU, 'ABOUT-NLS');
}

# Handle footer elements.
sub handle_footer
{
    # NOTE don't use define_pretty_variable here, because
    # $contents{...} is already defined.
    $output_vars .= 'SOURCES = ' . variable_value ('SOURCES') . "\n\n"
      if variable_value ('SOURCES');


    target_error ('.SUFFIXES',
          "use variable `SUFFIXES', not target `.SUFFIXES'")
      if target_defined ('.SUFFIXES');

    # Note: AIX 4.1 /bin/make will fail if any suffix rule appears
    # before .SUFFIXES.  So we make sure that .SUFFIXES appears before
    # anything else, by sticking it right after the default: target.
    $output_header .= ".SUFFIXES:\n";
    if (@suffixes || variable_defined ('SUFFIXES'))
    {
    # Make sure suffixes has unique elements.  Sort them to ensure
    # the output remains consistent.  However, $(SUFFIXES) is
    # always at the start of the list, unsorted.  This is done
    # because make will choose rules depending on the ordering of
    # suffixes, and this lets the user have some control.  Push
    # actual suffixes, and not $(SUFFIXES).  Some versions of make
    # do not like variable substitutions on the .SUFFIXES line.
    my @user_suffixes = (variable_defined ('SUFFIXES')
                 ? &variable_value_as_list_recursive ('SUFFIXES', '')
                 : ());

    my %suffixes = map { $_ => 1 } @suffixes;
    delete @suffixes{@user_suffixes};

    $output_header .= (".SUFFIXES: "
               . join (' ', @user_suffixes, sort keys %suffixes)
               . "\n");
    }

    $output_trailer .= file_contents ('footer');
}

# Deal with installdirs target.
sub handle_installdirs ()
{
    $output_rules .=
      &file_contents ('install',
              ('_am_installdirs'
               => variable_value ('_am_installdirs') || '',
               'installdirs-local'
               => (target_defined ('installdirs-local')
               ? ' installdirs-local' : '')));
}


# Deal with all and all-am.
sub handle_all ($)
{
    my ($makefile) = @_;

    # Output `all-am'.

    # Put this at the beginning for the sake of non-GNU makes.  This
    # is still wrong if these makes can run parallel jobs.  But it is
    # right enough.
    unshift (@all, basename ($makefile));

    foreach my $spec (@config_headers)
      {
        my ($out, @ins) = split_config_file_spec ($spec);
    push (@all, basename ($out))
      if dirname ($out) eq $relative_dir;
      }

    # Install `all' hooks.
    if (&target_defined ("all-local"))
    {
      push (@all, "all-local");
      &depend ('.PHONY', "all-local");
    }

    &pretty_print_rule ("all-am:", "\t\t", @all);
    &depend ('.PHONY', 'all-am', 'all');


    # Output `all'.

    my @local_headers = ();
    push @local_headers, '$(BUILT_SOURCES)'
      if variable_defined ('BUILT_SOURCES');
    foreach my $spec (@config_headers)
      {
        my ($out, @ins) = split_config_file_spec ($spec);
    push @local_headers, basename ($out)
      if dirname ($out) eq $relative_dir;
      }

    if (@local_headers)
      {
    # We need to make sure config.h is built before we recurse.
    # We also want to make sure that built sources are built
    # before any ordinary `all' targets are run.  We can't do this
    # by changing the order of dependencies to the "all" because
    # that breaks when using parallel makes.  Instead we handle
    # things explicitly.
    $output_all .= ("all: @local_headers"
            . "\n\t"
            . '$(MAKE) $(AM_MAKEFLAGS) '
            . (variable_defined ('SUBDIRS')
               ? 'all-recursive' : 'all-am')
            . "\n\n");
      }
    else
      {
    $output_all .= "all: " . (variable_defined ('SUBDIRS')
                  ? 'all-recursive' : 'all-am') . "\n\n";
      }
}


# Handle check merge target specially.
sub do_check_merge_target
{
    if (&target_defined ('check-local'))
    {
    # User defined local form of target.  So include it.
    push (@check_tests, 'check-local');
    &depend ('.PHONY', 'check-local');
    }

    # In --cygnus mode, check doesn't depend on all.
    if ($cygnus_mode)
    {
    # Just run the local check rules.
    &pretty_print_rule ('check-am:', "\t\t", @check);
    }
    else
    {
    # The check target must depend on the local equivalent of
    # `all', to ensure all the primary targets are built.  Then it
    # must build the local check rules.
    $output_rules .= "check-am: all-am\n";
    &pretty_print_rule ("\t\$(MAKE) \$(AM_MAKEFLAGS)", "\t  ",
                @check)
        if @check;
    }
    &pretty_print_rule ("\t\$(MAKE) \$(AM_MAKEFLAGS)", "\t  ",
            @check_tests)
    if @check_tests;

    &depend ('.PHONY', 'check', 'check-am');
    $output_rules .= ("check: "
              . (variable_defined ('SUBDIRS')
             ? 'check-recursive' : 'check-am')
              . "\n");
}

# Handle all 'clean' targets.
sub handle_clean
{
    my %transform;

    # Don't include `MAINTAINER'; it is handled specially below.
    foreach my $name ('MOSTLY', '', 'DIST')
    {
      $transform{"${name}CLEAN"} = variable_defined ("${name}CLEANFILES");
    }

    # Built sources are automatically removed by maintainer-clean.
    push (@maintainer_clean_files, '$(BUILT_SOURCES)')
    if variable_defined ('BUILT_SOURCES');
    push (@maintainer_clean_files, '$(MAINTAINERCLEANFILES)')
    if variable_defined ('MAINTAINERCLEANFILES');

    $output_rules .= &file_contents ('clean',
                     (%transform,
                      'MCFILES'
                      # Join with no space to avoid
                      # spurious `test -z' success at
                      # runtime.
                      => join ('', @maintainer_clean_files),
                      'MFILES'
                      # A space is required in the join here.
                      => "@maintainer_clean_files"));
}


# &depend ($CATEGORY, @DEPENDENDEES)
# ----------------------------------
# The target $CATEGORY depends on @DEPENDENDEES.
sub depend
{
    my ($category, @dependendees) = @_;
    {
      push (@{$dependencies{$category}}, @dependendees);
    }
}


# &target_cmp ($A, $B)
# --------------------
# Subroutine for &handle_factored_dependencies to let `.PHONY' be last.
sub target_cmp
{
    return 0
        if $a eq $b;
    return -1
        if $b eq '.PHONY';
    return 1
        if $a eq '.PHONY';
    return $a cmp $b;
}


# &handle_factored_dependencies ()
# --------------------------------
# Handle everything related to gathered targets.
sub handle_factored_dependencies
{
    # Reject bad hooks.
    foreach my $utarg ('uninstall-data-local', 'uninstall-data-hook',
               'uninstall-exec-local', 'uninstall-exec-hook')
    {
    if (&target_defined ($utarg))
    {
        my $x = $utarg;
        $x =~ s/(data|exec)-//;
        target_error ($utarg, "use `$x', not `$utarg'");
    }
    }

    if (&target_defined ('install-local'))
    {
    target_error ('install-local',
              "use `install-data-local' or `install-exec-local', "
              . "not `install-local'");
    }

    if (!defined $options{'no-installinfo'}
    && &target_defined ('install-info-local'))
    {
    target_error ('install-info-local',
              "`install-info-local' target defined but "
              . "`no-installinfo' option not in use");
    }

    # Install the -local hooks.
    foreach (keys %dependencies)
    {
      # Hooks are installed on the -am targets.
      s/-am$// or next;
      if (&target_defined ("$_-local"))
    {
      depend ("$_-am", "$_-local");
      &depend ('.PHONY', "$_-local");
    }
    }

    # Install the -hook hooks.
    # FIXME: Why not be as liberal as we are with -local hooks?
    foreach ('install-exec', 'install-data', 'uninstall')
    {
      if (&target_defined ("$_-hook"))
    {
      $actions{"$_-am"} .=
        ("\t\@\$(NORMAL_INSTALL)\n"
         . "\t" . '$(MAKE) $(AM_MAKEFLAGS) ' . "$_-hook\n");
    }
    }

    # All the required targets are phony.
    depend ('.PHONY', keys %required_targets);

    # Actually output gathered targets.
    foreach (sort target_cmp keys %dependencies)
    {
        # If there is nothing about this guy, skip it.
        next
      unless (@{$dependencies{$_}}
          || $actions{$_}
          || $required_targets{$_});
        &pretty_print_rule ("$_:", "\t",
                uniq (sort @{$dependencies{$_}}));
    $output_rules .= $actions{$_}
      if defined $actions{$_};
        $output_rules .= "\n";
    }
}


# &handle_tests_dejagnu ()
# ------------------------
sub handle_tests_dejagnu
{
    push (@check_tests, 'check-DEJAGNU');
    $output_rules .= file_contents ('dejagnu');
}


# Handle TESTS variable and other checks.
sub handle_tests
{
    if (defined $options{'dejagnu'})
    {
        &handle_tests_dejagnu;
    }
    else
    {
    foreach my $c ('DEJATOOL', 'RUNTEST', 'RUNTESTFLAGS')
    {
        macro_error ($c,
             "`$c' defined but `dejagnu' not in `AUTOMAKE_OPTIONS'")
          if variable_defined ($c);
    }
    }

    if (variable_defined ('TESTS'))
    {
    push (@check_tests, 'check-TESTS');
    $output_rules .= &file_contents ('check');
    }
}

# Handle Emacs Lisp.
sub handle_emacs_lisp
{
    my @elfiles = &am_install_var ('-candist', 'lisp', 'LISP',
                   'lisp', 'noinst');

    return if ! @elfiles;

    # Generate .elc files.
    my @elcfiles = map { $_ . 'c' } @elfiles;
    define_pretty_variable ('ELCFILES', '', @elcfiles);

    push (@all, '$(ELCFILES)');

    &am_error ("`lisp_LISP' defined but `AM_PATH_LISPDIR' not in `$configure_ac'")
      if ! $am_lispdir_location && variable_defined ('lisp_LISP');

    require_conf_file ($am_lispdir_location, FOREIGN, 'elisp-comp');
    &define_variable ('elisp_comp', $config_aux_dir . '/elisp-comp');
}

# Handle Python
sub handle_python
{
    my @pyfiles = &am_install_var ('-defaultdist', 'python', 'PYTHON',
                   'python', 'noinst');
    return if ! @pyfiles;

    # Found some python.
    &am_error ("`python_PYTHON' defined but `AM_PATH_PYTHON' not in `$configure_ac'")
    if ! $pythondir_location && variable_defined ('python_PYTHON');

    require_conf_file ($pythondir_location, FOREIGN, 'py-compile');
    &define_variable ('py_compile', $config_aux_dir . '/py-compile');
}

# Handle Java.
sub handle_java
{
    my @sourcelist = &am_install_var ('-candist',
                      'java', 'JAVA',
                      'java', 'noinst', 'check');
    return if ! @sourcelist;

    my @prefix = am_primary_prefixes ('JAVA', 1,
                      'java', 'noinst', 'check');

    my $dir;
    foreach my $curs (@prefix)
      {
    next
      if $curs eq 'EXTRA';

    macro_error ($curs . '_JAVA',
             "multiple _JAVA primaries in use")
      if defined $dir;
    $dir = $curs;
      }


    push (@all, 'class' . $dir . '.stamp');
}


# Handle some of the minor options.
sub handle_minor_options
{
    if (defined $options{'readme-alpha'})
    {
    if ($relative_dir eq '.')
    {
        if ($package_version !~ /^$GNITS_VERSION_PATTERN$/)
        {
        # FIXME: allow real filename.
        file_error ($package_version_location,
                "version `$package_version' doesn't follow Gnits standards");
        }
        elsif (defined $1 && -f 'README-alpha')
        {
        # This means we have an alpha release.  See
        # GNITS_VERSION_PATTERN for details.
        require_file_with_macro ('AUTOMAKE_OPTIONS',
                     FOREIGN, 'README-alpha');
        }
    }
    }
}

################################################################

# ($OUTPUT, @INPUTS)
# &split_config_file_spec ($SPEC)
# -------------------------------
# Decode the Autoconf syntax for config files (files, headers, links
# etc.).
sub split_config_file_spec ($)
{
  my ($spec) = @_;
  my ($output, @inputs) = split (/:/, $spec);

  push @inputs, "$output.in"
    unless @inputs;

  return ($output, @inputs);
}


my %make_list;

# &scan_autoconf_config_files ($CONFIG-FILES)
# -------------------------------------------
# Study $CONFIG-FILES which is the first argument to AC_CONFIG_FILES
# (or AC_OUTPUT).
sub scan_autoconf_config_files
{
    my ($config_files) = @_;
    # Look at potential Makefile.am's.
    foreach (split ' ', $config_files)
    {
        # Must skip empty string for Perl 4.
        next if $_ eq "\\" || $_ eq '';

        # Handle $local:$input syntax.  Note that we ignore
        # every input file past the first, though we keep
        # those around for later.
        my ($local, $input, @rest) = split (/:/);
        if (! $input)
        {
            $input = $local;
        }
        else
        {
            # FIXME: should be error if .in is missing.
            $input =~ s/\.in$//;
        }

        if (-f $input . '.am')
        {
            # We have a file that automake should generate.
            $make_list{$input} = join (':', ($local, @rest));
        }
        else
        {
            # We have a file that automake should cause to be
            # rebuilt, but shouldn't generate itself.
            push (@other_input_files, $_);
        }
    }
}


# &scan_autoconf_traces ($FILENAME)
# ---------------------------------
# FIXME: For the time being, we don't care about the FILENAME.
sub scan_autoconf_traces ($)
{
  my ($filename) = @_;

  my @traced = qw(AC_CANONICAL_HOST
          AC_CANONICAL_SYSTEM
          AC_CONFIG_AUX_DIR
          AC_CONFIG_FILES
          AC_INIT
          AC_LIBSOURCE
          AC_PROG_LEX
          AC_PROG_LIBTOOL AM_PROG_LIBTOOL
          AC_SUBST
          AM_AUTOMAKE_VERSION
          AM_CONDITIONAL
          AM_CONFIG_HEADER
          AM_C_PROTOTYPES
          AM_GNU_GETTEXT
          AM_INIT_AUTOMAKE
          AM_MAINTAINER_MODE
          AM_PATH_LISPDIR
          AM_PATH_PYTHON
          AM_PROG_CC_C_O);

  my $traces = "$ENV{amtraces} ";

  # Use a separator unlikely to be used, not `:', the default, which
  # has a precise meaning for AC_CONFIG_FILES and so on.
  $traces .= join (' ',
           map { "--trace=$_" . ':\$f:\$l::\$n::\${::}%' } @traced);

  my $tracefh = new Automake::XFile ("$traces |");
  verbose "reading $traces";

  while ($_ = $tracefh->getline)
    {
      chomp;
      my ($here, @args) = split /::/;
      my $macro = $args[0];

      # Alphabetical ordering please.
      if ($macro eq 'AC_CANONICAL_HOST')
    {
      if (! $seen_canonical)
        {
          $seen_canonical = AC_CANONICAL_HOST;
          $canonical_location = $here;
        };
    }
      elsif ($macro eq 'AC_CANONICAL_SYSTEM')
    {
      $seen_canonical = AC_CANONICAL_SYSTEM;
      $canonical_location = $here;
    }
      elsif ($macro eq 'AC_CONFIG_AUX_DIR')
    {
      @config_aux_path = $args[1];
      $config_aux_dir_set_in_configure_in = 1;
    }
      elsif ($macro eq 'AC_CONFIG_FILES')
    {
      # Look at potential Makefile.am's.
      $ac_config_files_location = $here;
      &scan_autoconf_config_files ($args[1]);
    }
      elsif ($macro eq 'AC_INIT')
        {
      if (defined $args[2])
        {
          $package_version = $args[2];
          $package_version_location = $here;
        }
    }
      elsif ($macro eq 'AC_LIBSOURCE')
    {
      $libsources{$args[1]} = $here;
    }
      elsif ($macro =~ /^A(C|M)_PROG_LIBTOOL$/)
    {
      $seen_libtool = $here;
    }
      elsif ($macro eq 'AC_PROG_LEX')
    {
      $seen_prog_lex = $here;
    }
      elsif ($macro eq 'AC_SUBST')
    {
      # Just check for alphanumeric in AC_SUBST.  If you do
      # AC_SUBST(5), then too bad.
      $configure_vars{$args[1]} = $here
        if $args[1] =~ /^\w+$/;
    }
      elsif ($macro eq 'AM_AUTOMAKE_VERSION')
        {
      file_error ($here,
              "version mismatch.  This is Automake $VERSION,\n" .
              "but the definition used by this AM_INIT_AUTOMAKE\n" .
              "comes from Automake $args[1].  You should recreate\n" .
              "aclocal.m4 with aclocal and run automake again.\n")
          if ($VERSION ne $args[1]);

      $seen_automake_version = 1;
        }
      elsif ($macro eq 'AM_CONDITIONAL')
    {
      $configure_cond{$args[1]} = $here;
    }
      elsif ($macro eq 'AM_CONFIG_HEADER')
    {
      $config_header_location = $here;
      push @config_headers, split (' ', $args[1]);
    }
      elsif ($macro eq 'AM_C_PROTOTYPES')
    {
      $am_c_prototypes = $here;
    }
      elsif ($macro eq 'AM_GNU_GETTEXT')
    {
      $seen_gettext = $here;
      $ac_gettext_location = $here;
      $seen_gettext_external = grep ($_ eq 'external', @args);
    }
      elsif ($macro eq 'AM_INIT_AUTOMAKE')
    {
      $seen_init_automake = $here;
      if (defined $args[2])
        {
          $package_version = $args[2];
          $package_version_location = $here;
        }
      elsif (defined $args[1])
        {
          $global_options = $args[1];
        }
    }
      elsif ($macro eq 'AM_MAINTAINER_MODE')
    {
      $seen_maint_mode = $here;
    }
      elsif ($macro eq 'AM_PATH_LISPDIR')
    {
      $am_lispdir_location = $here;
    }
      elsif ($macro eq 'AM_PATH_PYTHON')
    {
      $pythondir_location = $here;
    }
      elsif ($macro eq 'AM_PROG_CC_C_O')
    {
      $seen_cc_c_o = $here;
    }
   }
}


# &scan_one_autoconf_file ($FILENAME)
# -----------------------------------
# Scan one file for interesting things.  Subroutine of
# &scan_autoconf_files.
sub scan_one_autoconf_file
{
    my ($filename) = @_;

    # Some macros already provide the right traces to enable generic
    # code and specific arguments, instead of dedicated code.  But
    # currently we don't handle traces.  Rewrite these dedicated
    # macros handling into the generic macro invocation, and let our
    # generic case handle them.

    my %generalize =
      (
       'AC_FUNC_ALLOCA'           => 'AC_LIBSOURCES([alloca.c])',
       'AC_FUNC_GETLOADAVG'       => 'AC_LIBSOURCES([getloadavg.c])',
       'AC_FUNC_MEMCMP'           => 'AC_LIBSOURCES([memcmp.c])',
       'AC_STRUCT_ST_BLOCKS'      => 'AC_LIBSOURCES([fileblocks.c])',
       'A[CM]_REPLACE_GNU_GETOPT' => 'AC_LIBSOURCES([getopt.c, getopt1.c])',
       'A[CM]_FUNC_STRTOD'        => 'AC_LIBSOURCES([strtod.c])',
       'AM_WITH_REGEX'      => 'AC_LIBSOURCES([rx.c, rx.h, regex.c, regex.h])',
       'AC_FUNC_MKTIME'           => 'AC_LIBSOURCES([mktime.c])',
       'A[CM]_FUNC_ERROR_AT_LINE' => 'AC_LIBSOURCES([error.c, error.h])',
       'A[CM]_FUNC_OBSTACK'       => 'AC_LIBSOURCES([obstack.c, obstack.h])',
      );

    my $configfh = new Automake::XFile ("< $filename");
    verbose "reading $filename";

    my ($in_ac_output, $in_ac_replace) = (0, 0);
    while ($_ = $configfh->getline)
    {
    # Remove comments from current line.
    s/\bdnl\b.*$//;
    s/\#.*$//;

    # Skip macro definitions.  Otherwise we might be confused into
    # thinking that a macro that was only defined was actually
    # used.
    next if /AC_DEFUN/;

    # Follow includes.  This is a weirdness commonly in use at
    # Cygnus and hopefully nowhere else.
    if (/\b(?:m4_)?s?include\((.*)\)/ && -f $1)
    {
        # $_ being local, if we don't preserve it, when coming
        # back we will have $_ undefined, which is bad for the
        # the rest of this routine.
        my $underscore = $_;
        &scan_one_autoconf_file (unquote_m4_arg ($1));
        $_ = $underscore;
    }

    for my $generalize (keys %generalize)
      {
        s/\b$generalize\b/$generalize{$generalize}/g;
      }


    my $here = "$filename:$.";

    # Populate libobjs array.
    if (/LIBOBJS="(.*)\s+\$LIBOBJS"/
           || /LIBOBJS="\$LIBOBJS\s+(.*)"/)
    {
        foreach my $libobj_iter (split (' ', $1))
        {
        if ($libobj_iter =~ /^(.*)\.o(bj)?$/
            || $libobj_iter =~ /^(.*)\.\$ac_objext$/
            || $libobj_iter =~ /^(.*)\.\$\{ac_objext\}$/)
        {
            $libsources{$1 . '.c'} = $here;
        }
        }
    }
    elsif (/AC_LIBOBJ\(([^)]+)\)/)
    {
        $libsources{unquote_m4_arg ($1) . ".c"} = $here;
    }
        elsif (/AC_LIBSOURCE\(([^)]+)\)/)
    {
        $libsources{&unquote_m4_arg ($1)} = $here;
    }
        elsif (/AC_LIBSOURCES\(([^)]+)\)/)
    {
        foreach my $lc_iter (split (/[, ]+/, &unquote_m4_arg ($1)))
        {
        $libsources{$lc_iter} = $here;
        }
    }

    if (! $in_ac_replace && s/AC_REPLACE_FUNCS\s*\(\[?//)
    {
        $in_ac_replace = 1;
    }
    if ($in_ac_replace)
    {
        $in_ac_replace = 0 if s/[\]\)].*$//;
        # Remove trailing backslash.
        s/\\$//;
        foreach (split)
        {
        # Need to skip empty elements for Perl 4.
        next if $_ eq '';
        $libsources{$_ . '.c'} = $here;
        }
    }

    if (/$obsolete_rx/o)
    {
        my $hint = '';
        if ($obsolete_macros{$1} ne '')
        {
        $hint = '; ' . $obsolete_macros{$1};
        }
        file_error ($here, "`$1' is obsolete$hint");
    }

    # Process the AC_OUTPUT and AC_CONFIG_FILES macros.
    if (! $in_ac_output && s/(AC_(OUTPUT|CONFIG_FILES))\s*\(\[?//)
    {
        $in_ac_output = $1;
        $ac_config_files_location = $here;
    }
    if ($in_ac_output)
    {
        my $closing = 0;
        if (s/[\]\),].*$//)
        {
        $in_ac_output = 0;
        $closing = 1;
        }

        # Look at potential Makefile.am's.
        &scan_autoconf_config_files ($_);

        if ($closing
        && scalar keys %make_list == 0
        && @other_input_files == 0)
        {
        file_error ($ac_config_files_location,
                "no files mentioned in `$in_ac_output'");
        exit 1;
        }
    }

    if (/$AC_CONFIG_AUX_DIR_PATTERN/o)
    {
        @config_aux_path = &unquote_m4_arg ($1);
        $config_aux_dir_set_in_configure_in = $here;
    }

    # Check for ansi2knr.
    $am_c_prototypes = $here if /AM_C_PROTOTYPES/;

    # Check for `-c -o' code.
    $seen_cc_c_o = $here if /AM_PROG_CC_C_O/;

    # Check for NLS support.
    if (/\bAM_GNU_GETTEXT\b/)
    {
        $seen_gettext = $here;
        $ac_gettext_location = $here;
        $seen_gettext_external = 1
            if /\bAM_GNU_GETTEXT\([^\)]*\bexternal\b/;
    }

    # Handle configuration headers.  A config header of `[$1]'
    # means we are actually scanning AM_CONFIG_HEADER from
    # aclocal.m4.  Same thing with a leading underscore.
    if (/(?<!_)A([CM])_CONFIG_HEADERS?\s*\((.*)\)/
        && $2 ne '[$1]')
    {
        file_error ($here,
           "`automake requires `AM_CONFIG_HEADER', not `AC_CONFIG_HEADER'")
          if $1 eq 'C';

        $config_header_location = $here;
        push @config_headers, split (' ', unquote_m4_arg ($2));
    }

        # Handle AC_CANONICAL_*.  Always allow upgrading to
        # AC_CANONICAL_SYSTEM, but never downgrading.
    if (/AC_CANONICAL_HOST/ || /AC_CYGWIN/ || /AC_EMXOS2/ || /AC_MINGW32/)
      {
        if (! $seen_canonical)
          {
        $seen_canonical = AC_CANONICAL_HOST;
        $canonical_location = $here;
          }
      }
    if (/AC_CANONICAL_SYSTEM/)
      {
        $seen_canonical = AC_CANONICAL_SYSTEM;
        $canonical_location = $here;
      }

        # If using X, include some extra variable definitions.  NOTE
        # we don't want to force these into CFLAGS or anything,
        # because not all programs will necessarily use X.
    if (/AC_PATH_XTRA/)
      {
        foreach my $var (qw(X_CFLAGS X_LIBS X_EXTRA_LIBS X_PRE_LIBS))
          {
        $configure_vars{$var} = $here;
          }
      }

    # AM_INIT_AUTOMAKE with any number of argument
    if (/AM_INIT_AUTOMAKE/)
    {
        $seen_init_automake = $here;
        }

    # AC_INIT or AM_INIT_AUTOMAKE with two arguments
        if (/$AC_INIT_PATTERN/o || /$AM_INIT_AUTOMAKE_PATTERN/o)
    {
            if ($1 =~ /$AM_PACKAGE_VERSION_PATTERN/o)
            {
        $package_version = $1;
        $package_version_location = $here;
        }
    }

    # AM_INIT_AUTOMAKE with one argument.
    if (/AM_INIT_AUTOMAKE\(([^),]+)\)/)
    {
            $global_options = &unquote_m4_arg ($1);
    }

    if (/AM_AUTOMAKE_VERSION\(([^)]+)\)/)
    {
        my $vers = &unquote_m4_arg ($1);
        file_error ($here,
            "version mismatch.  This is Automake $VERSION, " .
            "but $filename\nwas generated for Automake $vers.  " .
            "You should recreate\n$filename with aclocal and " .
            "run automake again.\n")
            if ($VERSION ne $vers);

        $seen_automake_version = 1;
    }

    if (/AM_PROG_LEX/)
    {
        $configure_vars{'LEX'} = $here;
        $configure_vars{'LEX_OUTPUT_ROOT'} = $here;
        $configure_vars{'LEXLIB'} = $here;
        $seen_prog_lex = $here;
    }
    if (/AC_PROG_LEX/ && $filename =~ /configure\.(ac|in)$/)
    {
        $configure_vars{'LEX'} = $here;
        $configure_vars{'LEX_OUTPUT_ROOT'} = $here;
        $configure_vars{'LEXLIB'} = $here;
        $seen_prog_lex = $here;
        file_warning ($here,
           "automake requires `AM_PROG_LEX', not `AC_PROG_LEX'");
    }

    if (/AC_PROG_(F77|YACC|RANLIB|CC|CXXCPP|CXX|LEX|AWK|CPP|LN_S)/)
    {
        $configure_vars{$1} = $here;
    }
    if (/$AC_CHECK_PATTERN/o)
    {
        $configure_vars{$3} = $here;
    }
    if (/$AM_MISSING_PATTERN/o
        && $1 ne 'ACLOCAL'
        && $1 ne 'AUTOCONF'
        && $1 ne 'AUTOMAKE'
        && $1 ne 'AUTOHEADER'
        # AM_INIT_AUTOMAKE is AM_MISSING_PROG'ing MAKEINFO.  But
        # we handle it elsewhere.
        && $1 ne 'MAKEINFO')
    {
        $configure_vars{$1} = $here;
    }

    # Explicitly avoid ANSI2KNR -- we AC_SUBST that in protos.m4,
    # but later define it elsewhere.  This is pretty hacky.  We
    # also explicitly avoid INSTALL_SCRIPT and some other
    # variables because they are defined in header-vars.am.
    # AMDEPBACKSLASH might be subst'd by `\', which certainly would
    # not be appreciated by Make.
    if (/$AC_SUBST_PATTERN/o
        && $1 ne 'ANSI2KNR'
        && $1 ne 'INSTALL_SCRIPT'
        && $1 ne 'INSTALL_DATA'
        && $1 ne 'AMDEPBACKSLASH')
    {
        $configure_vars{$1} = $here;
    }

    if (/AM_MAINTAINER_MODE/)
    {
        $seen_maint_mode = $here;
        $configure_cond{'MAINTAINER_MODE'} = $here;
    }

        $am_lispdir_location = $here if /AM_PATH_LISPDIR/;

        if (/AM_PATH_PYTHON/)
      {
        $pythondir_location = $here;
        $configure_vars{'pythondir'} = $here;
        $configure_vars{'PYTHON'} = $here;
      }

        if (/A(C|M)_PROG_LIBTOOL/)
    {
        # We're not ready for this yet.  People still use a
        # libtool with no AC_PROG_LIBTOOL.  Once that is the
        # dominant version we can reenable this code -- but next
        # time by mentioning the macro in %obsolete_macros, both
        # here and in aclocal.in.

        # if (/AM_PROG_LIBTOOL/)
        # {
        #   file_warning ($here, "`AM_PROG_LIBTOOL' is obsolete, use `AC_PROG_LIBTOOL' instead");
        # }
        $seen_libtool = $here;
        $configure_vars{'LIBTOOL'} = $here;
        $configure_vars{'RANLIB'} = $here;
        $configure_vars{'CC'} = $here;
        # AC_PROG_LIBTOOL runs AC_CANONICAL_HOST.  Make sure we
        # never downgrade (if we've seen AC_CANONICAL_SYSTEM).
        $seen_canonical = AC_CANONICAL_HOST if ! $seen_canonical;
    }

    $seen_multilib = $here if (/AM_ENABLE_MULTILIB/);

    if (/$AM_CONDITIONAL_PATTERN/o)
    {
        $configure_cond{$1} = $here;
    }

    # Check for Fortran 77 intrinsic and run-time libraries.
    if (/AC_F77_LIBRARY_LDFLAGS/)
    {
        $configure_vars{'FLIBS'} = $here;
    }
    }
}


# &scan_autoconf_files ()
# -----------------------
# Check whether we use `configure.ac' or `configure.in'.
# Scan it (and possibly `aclocal.m4') for interesting things.
# We must scan aclocal.m4 because there might be AC_SUBSTs and such there.
sub scan_autoconf_files
{
    # Reinitialize libsources here.  This isn't really necessary,
    # since we currently assume there is only one configure.ac.  But
    # that won't always be the case.
    %libsources = ();

    $configure_ac = find_configure_ac;
    die "$me: `configure.ac' or `configure.in' is required\n"
        if !$configure_ac;

    if (defined $ENV{'amtraces'})
    {
        print STDERR "$me: Autoconf traces is an experimental feature\n";
        print STDERR "$me: use at your own risks\n";

        scan_autoconf_traces ($configure_ac);
    }
    else
      {
    scan_one_autoconf_file ($configure_ac);
    scan_one_autoconf_file ('aclocal.m4')
      if -f 'aclocal.m4';
      }

    # Set input and output files if not specified by user.
    if (! @input_files)
    {
    @input_files = sort keys %make_list;
    %output_files = %make_list;
    }

    @configure_input_files = sort keys %make_list;

    conf_error ("`AM_INIT_AUTOMAKE' must be used")
    if ! $seen_init_automake;

    if (! $seen_automake_version)
    {
    if (-f 'aclocal.m4')
    {
        file_error ($seen_init_automake || $me,
            "your implementation of AM_INIT_AUTOMAKE comes from " .
            "an\nold Automake version.  You should recreate " .
            "aclocal.m4\nwith aclocal and run automake again.\n");
    }
    else
    {
        file_error ($seen_init_automake || $me,
            "no proper implementation of AM_INIT_AUTOMAKE was " .
            "found,\nprobably because aclocal.m4 is missing...\n" .
            "You should run aclocal to create this file, then\n" .
            "run automake again.\n");
    }
    }

    # Look for some files we need.  Always check for these.  This
    # check must be done for every run, even those where we are only
    # looking at a subdir Makefile.  We must set relative_dir so that
    # the file-finding machinery works.
    # FIXME: Is this broken because it needs dynamic scopes.
    # My tests seems to show it's not the case.
    $relative_dir = '.';
    require_conf_file ($configure_ac, FOREIGN,
               'install-sh', 'mkinstalldirs', 'missing');
    am_error ("`install.sh' is an anachronism; use `install-sh' instead")
        if -f $config_aux_path[0] . '/install.sh';

    require_conf_file ($pythondir_location, FOREIGN, 'py-compile')
      if $pythondir_location;

    # Preserve dist_common for later.
    $configure_dist_common = variable_value ('DIST_COMMON', 'TRUE') || '';
}

################################################################

# Set up for Cygnus mode.
sub check_cygnus
{
    return unless $cygnus_mode;

    &set_strictness ('foreign');
    $options{'no-installinfo'} = 1;
    $options{'no-dependencies'} = 1;
    $use_dependencies = 0;

    conf_error ("`AM_MAINTAINER_MODE' required when --cygnus specified")
      if !$seen_maint_mode;
}

# Do any extra checking for GNU standards.
sub check_gnu_standards
{
    if ($relative_dir eq '.')
    {
    # In top level (or only) directory.
    require_file ("$am_file.am", GNU,
              qw(INSTALL NEWS README COPYING AUTHORS ChangeLog));
    }

    if ($strictness >= GNU
    && defined $options{'no-installman'})
    {
    macro_error ('AUTOMAKE_OPTIONS',
             "option `no-installman' disallowed by GNU standards");
    }

    if ($strictness >= GNU
    && defined $options{'no-installinfo'})
    {
    macro_error ('AUTOMAKE_OPTIONS',
             "option `no-installinfo' disallowed by GNU standards");
    }
}

# Do any extra checking for GNITS standards.
sub check_gnits_standards
{
    if ($relative_dir eq '.')
    {
    # In top level (or only) directory.
    require_file ("$am_file.am", GNITS, 'THANKS');
    }
}

################################################################
#
# Functions to handle files of each language.

# Each `lang_X_rewrite($DIRECTORY, $BASE, $EXT)' function follows a
# simple formula: Return value is $LANG_SUBDIR if the resulting object
# file should be in a subdir if the source file is, $LANG_PROCESS if
# file is to be dealt with, $LANG_IGNORE otherwise.

# Much of the actual processing is handled in
# handle_single_transform_list.  These functions exist so that
# auxiliary information can be recorded for a later cleanup pass.
# Note that the calls to these functions are computed, so don't bother
# searching for their precise names in the source.

# This is just a convenience function that can be used to determine
# when a subdir object should be used.
sub lang_sub_obj
{
    return defined $options{'subdir-objects'} ? $LANG_SUBDIR : $LANG_PROCESS;
}

# Rewrite a single C source file.
sub lang_c_rewrite
{
    my ($directory, $base, $ext) = @_;

    if (defined $options{'ansi2knr'} && $base =~ /_$/)
    {
    # FIXME: include line number in error.
    am_error ("C source file `$base.c' would be deleted by ansi2knr rules");
    }

    my $r = $LANG_PROCESS;
    if (defined $options{'subdir-objects'})
    {
    $r = $LANG_SUBDIR;
    $base = $directory . '/' . $base
        unless $directory eq '.' || $directory eq '';

    if (! $seen_cc_c_o)
    {
        # Only give error once.
        $seen_cc_c_o = 1;
        # FIXME: line number.
        am_error ("C objects in subdir but `AM_PROG_CC_C_O' not in `$configure_ac'");
    }

    require_conf_file ("$am_file.am", FOREIGN, 'compile');

    # In this case we already have the directory information, so
    # don't add it again.
    $de_ansi_files{$base} = '';
    }
    else
    {
    $de_ansi_files{$base} = (($directory eq '.' || $directory eq '')
                 ? ''
                 : "$directory/");
    }

    return $r;
}

# Rewrite a single C++ source file.
sub lang_cxx_rewrite
{
    return &lang_sub_obj;
}

# Rewrite a single header file.
sub lang_header_rewrite
{
    # Header files are simply ignored.
    return $LANG_IGNORE;
}

# Rewrite a single yacc file.
sub lang_yacc_rewrite
{
    my ($directory, $base, $ext) = @_;

    my $r = &lang_sub_obj;
    (my $newext = $ext) =~ tr/y/c/;
    return ($r, $newext);
}

# Rewrite a single yacc++ file.
sub lang_yaccxx_rewrite
{
    my ($directory, $base, $ext) = @_;

    my $r = &lang_sub_obj;
    (my $newext = $ext) =~ tr/y/c/;
    return ($r, $newext);
}

# Rewrite a single lex file.
sub lang_lex_rewrite
{
    my ($directory, $base, $ext) = @_;

    my $r = &lang_sub_obj;
    (my $newext = $ext) =~ tr/l/c/;
    return ($r, $newext);
}

# Rewrite a single lex++ file.
sub lang_lexxx_rewrite
{
    my ($directory, $base, $ext) = @_;

    my $r = &lang_sub_obj;
    (my $newext = $ext) =~ tr/l/c/;
    return ($r, $newext);
}

# Rewrite a single assembly file.
sub lang_asm_rewrite
{
    return &lang_sub_obj;
}

# Rewrite a single Fortran 77 file.
sub lang_f77_rewrite
{
    return $LANG_PROCESS;
}

# Rewrite a single preprocessed Fortran 77 file.
sub lang_ppf77_rewrite
{
    return $LANG_PROCESS;
}

# Rewrite a single ratfor file.
sub lang_ratfor_rewrite
{
    return $LANG_PROCESS;
}

# Rewrite a single Objective C file.
sub lang_objc_rewrite
{
    return &lang_sub_obj;
}

# Rewrite a single Java file.
sub lang_java_rewrite
{
    return $LANG_SUBDIR;
}

# The lang_X_finish functions are called after all source file
# processing is done.  Each should handle defining rules for the
# language, etc.  A finish function is only called if a source file of
# the appropriate type has been seen.

sub lang_c_finish
{
    # Push all libobjs files onto de_ansi_files.  We actually only
    # push files which exist in the current directory, and which are
    # genuine source files.
    foreach my $file (keys %libsources)
    {
    if ($file =~ /^(.*)\.[cly]$/ && -f "$relative_dir/$file")
    {
        $de_ansi_files{$1} = (($relative_dir eq '.' || $relative_dir eq '')
                  ? ''
                  : "$relative_dir/");
    }
    }

    if (defined $options{'ansi2knr'} && keys %de_ansi_files)
    {
    # Make all _.c files depend on their corresponding .c files.
    my @objects;
    foreach my $base (sort keys %de_ansi_files)
    {
        # Each _.c file must depend on ansi2knr; otherwise it
        # might be used in a parallel build before it is built.
        # We need to support files in the srcdir and in the build
        # dir (because these files might be auto-generated.  But
        # we can't use $< -- some makes only define $< during a
        # suffix rule.
        my $ansfile = $de_ansi_files{$base} . $base . '.c';
        $output_rules .= ($base . "_.c: $ansfile \$(ANSI2KNR)\n\t"
                  . '$(CPP) $(DEFS) $(DEFAULT_INCLUDES) $(INCLUDES) $(AM_CPPFLAGS) $(CPPFLAGS) '
                  . '`if test -f $(srcdir)/' . $ansfile
                  . '; then echo $(srcdir)/' . $ansfile
                  . '; else echo ' . $ansfile . '; fi` '
                  . "| sed 's/^# \\([0-9]\\)/#line \\1/' "
                  . '| $(ANSI2KNR) > ' . $base . "_.c"
                  # If ansi2knr fails then we shouldn't
                  # create the _.c file
                  . " || rm -f ${base}_.c\n");
        push (@objects, $base . '_.$(OBJEXT)');
        push (@objects, $base . '_.lo')
          if $seen_libtool;
    }

    # Make all _.o (and _.lo) files depend on ansi2knr.
    # Use a sneaky little hack to make it print nicely.
    &pretty_print_rule ('', '', @objects, ':', '$(ANSI2KNR)');
    }
}

# This is a yacc helper which is called whenever we have decided to
# compile a yacc file.
sub lang_yacc_target_hook
{
    my ($self, $aggregate, $output, $input) = @_;

    my $flag = $aggregate . "_YFLAGS";
    if ((variable_defined ($flag)
     && &variable_value ($flag) =~ /$DASH_D_PATTERN/o)
    || (variable_defined ('YFLAGS')
        && &variable_value ('YFLAGS') =~ /$DASH_D_PATTERN/o))
    {
    (my $output_base = $output) =~ s/$KNOWN_EXTENSIONS_PATTERN$//;
    my $header = $output_base . '.h';

    # Found a `-d' that applies to the compilation of this file.
    # Add a dependency for the generated header file, and arrange
    # for that file to be included in the distribution.
    # FIXME: this fails for `nodist_*_SOURCES'.
    $output_rules .= ("${header}: $output\n"
              # Recover from removal of $header
              . "\t\@if test ! -f \$@; then \\\n"
              . "\t  rm -f $output; \\\n"
              . "\t  \$(MAKE) $output; \\\n"
              . "\telse :; fi\n");
    &push_dist_common ($header);
    # If the files are built in the build directory, then we want
    # to remove them with `make clean'.  If they are in srcdir
    # they shouldn't be touched.  However, we can't determine this
    # statically, and the GNU rules say that yacc/lex output files
    # should be removed by maintainer-clean.  So that's what we
    # do.
    push (@maintainer_clean_files, $header);
    }
    # Erase $OUTPUT on `make maintainer-clean' (by GNU standards).
    # See the comment above for $HEADER.
    push (@maintainer_clean_files, $output);
}

# This is a lex helper which is called whenever we have decided to
# compile a lex file.
sub lang_lex_target_hook
{
    my ($self, $aggregate, $output, $input) = @_;
    # If the files are built in the build directory, then we want to
    # remove them with `make clean'.  If they are in srcdir they
    # shouldn't be touched.  However, we can't determine this
    # statically, and the GNU rules say that yacc/lex output files
    # should be removed by maintainer-clean.  So that's what we do.
    push (@maintainer_clean_files, $output);
}

# This is a helper for both lex and yacc.
sub yacc_lex_finish_helper
{
    return if defined $language_scratch{'lex-yacc-done'};
    $language_scratch{'lex-yacc-done'} = 1;

    # If there is more than one distinct yacc (resp lex) source file
    # in a given directory, then the `ylwrap' program is required to
    # allow parallel builds to work correctly.  FIXME: for now, no
    # line number.
    require_conf_file ($configure_ac, FOREIGN, 'ylwrap');
    if ($config_aux_dir_set_in_configure_in)
    {
    &define_variable ('YLWRAP', $config_aux_dir . "/ylwrap");
    }
    else
    {
    &define_variable ('YLWRAP', '$(top_srcdir)/ylwrap');
    }
}

sub lang_yacc_finish
{
    return if defined $language_scratch{'yacc-done'};
    $language_scratch{'yacc-done'} = 1;

    macro_error ('YACCFLAGS',
         "`YACCFLAGS' obsolete; use `YFLAGS' instead")
      if variable_defined ('YACCFLAGS');

    if (count_files_for_language ('yacc') > 1)
    {
    &yacc_lex_finish_helper;
    }
}


sub lang_lex_finish
{
    return if defined $language_scratch{'lex-done'};
    $language_scratch{'lex-done'} = 1;

    am_error ("lex source seen but `AM_PROG_LEX' not in `$configure_ac'")
      unless $seen_prog_lex;

    if (count_files_for_language ('lex') > 1)
    {
    &yacc_lex_finish_helper;
    }
}


# Given a hash table of linker names, pick the name that has the most
# precedence.  This is lame, but something has to have global
# knowledge in order to eliminate the conflict.  Add more linkers as
# required.
sub resolve_linker
{
    my (%linkers) = @_;

    foreach my $l (qw(GCJLINK CXXLINK F77LINK OBJCLINK))
    {
    return $l if defined $linkers{$l};
    }
    return 'LINK';
}

# Called to indicate that an extension was used.
sub saw_extension
{
    my ($ext) = @_;
    if (! defined $extension_seen{$ext})
    {
    $extension_seen{$ext} = 1;
    }
    else
    {
    ++$extension_seen{$ext};
    }
}

# Return the number of files seen for a given language.  Knows about
# special cases we care about.  FIXME: this is hideous.  We need
# something that involves real language objects.  For instance yacc
# and yaccxx could both derive from a common yacc class which would
# know about the strange ylwrap requirement.  (Or better yet we could
# just not support legacy yacc!)
sub count_files_for_language
{
    my ($name) = @_;

    my @names;
    if ($name eq 'yacc' || $name eq 'yaccxx')
    {
    @names = ('yacc', 'yaccxx');
    }
    elsif ($name eq 'lex' || $name eq 'lexxx')
    {
    @names = ('lex', 'lexxx');
    }
    else
    {
    @names = ($name);
    }

    my $r = 0;
    foreach $name (@names)
    {
    my $lang = $languages{$name};
    foreach my $ext (@{$lang->extensions})
    {
        $r += $extension_seen{$ext}
            if defined $extension_seen{$ext};
    }
    }

    return $r
}

# Called to ask whether source files have been seen . If HEADERS is 1,
# headers can be included.
sub saw_sources_p
{
    my ($headers) = @_;

    # count all the sources
    my $count = 0;
    foreach my $val (values %extension_seen)
    {
    $count += $val;
    }

    if (!$headers)
    {
    $count -= count_files_for_language ('header');
    }

    return $count > 0;
}


# register_language (%ATTRIBUTE)
# ------------------------------
# Register a single language.
# Each %ATTRIBUTE is of the form ATTRIBUTE => VALUE.
sub register_language (%)
{
    my (%option) = @_;

    # Set the defaults.
    $option{'ansi'} = 0
      unless defined $option{'ansi'};
    $option{'autodep'} = 'no'
      unless defined $option{'autodep'};
    $option{'linker'} = ''
      unless defined $option{'linker'};
    $option{'define_flag'} = 1
      unless defined $option{'define_flag'};

    my $lang = new Language (%option);

    # Fill indexes.
    grep ($extension_map{$_} = $lang->name, @{$lang->extensions});
    $languages{$lang->name} = $lang;

    # Update the pattern of known extensions.
    accept_extensions (@{$lang->extensions});
}

# derive_suffix ($EXT, $OBJ)
# --------------------------
# This function is used to find a path from a user-specified suffix $EXT
# to $OBJ or to some other suffix we recognize internally, eg `cc'.
sub derive_suffix ($$)
{
    my ($source_ext, $obj) = @_;

    while (! $extension_map{$source_ext}
       && $source_ext ne $obj
       && defined $suffix_rules{$source_ext})
    {
    $source_ext = $suffix_rules{$source_ext};
    }

    return $source_ext;
}


################################################################

# Pretty-print something.  HEAD is what should be printed at the
# beginning of the first line, FILL is what should be printed at the
# beginning of every subsequent line.
sub pretty_print_internal
{
    my ($head, $fill, @values) = @_;

    my $column = length ($head);
    my $result = $head;

    # Fill length is number of characters.  However, each Tab
    # character counts for eight.  So we count the number of Tabs and
    # multiply by 7.
    my $fill_length = length ($fill);
    $fill_length += 7 * ($fill =~ tr/\t/\t/d);

    foreach (@values)
    {
    # "71" because we also print a space.
    if ($column + length ($_) > 71)
    {
        $result .= " \\\n" . $fill;
        $column = $fill_length;
    }
    $result .= ' ' if $result =~ /\S\z/;
    $result .= $_;
    $column += length ($_) + 1;
    }

    $result .= "\n";
    return $result;
}

# Pretty-print something and append to output_vars.
sub pretty_print
{
    $output_vars .= &pretty_print_internal (@_);
}

# Pretty-print something and append to output_rules.
sub pretty_print_rule
{
    $output_rules .= &pretty_print_internal (@_);
}


################################################################


# $STRING
# &conditional_string(@COND-STACK)
# --------------------------------
# Build a string which denotes the conditional in @COND-STACK.  Some
# simplifications are done: `TRUE' entries are elided, and any `FALSE'
# entry results in a return of `FALSE'.
sub conditional_string
{
  my (@stack) = @_;

  if (grep (/^FALSE$/, @stack))
    {
      return 'FALSE';
    }
  else
    {
      return join (' ', uniq sort grep (!/^TRUE$/, @stack));
    }
}


# $BOOLEAN
# &conditional_true_when ($COND, $WHEN)
# -------------------------------------
# See if a conditional is true.  Both arguments are conditional
# strings.  This returns true if the first conditional is true when
# the second conditional is true.
# For instance with $COND = `BAR FOO', and $WHEN = `BAR BAZ FOO',
# obviously return 1, and 0 when, for instance, $WHEN = `FOO'.
sub conditional_true_when ($$)
{
    my ($cond, $when) = @_;

    # Make a hash holding all the values from $WHEN.
    my %cond_vals = map { $_ => 1 } split (' ', $when);

    # Check each component of $cond, which looks `COND1 COND2'.
    foreach my $comp (split (' ', $cond))
    {
    # TRUE is always true.
    next if $comp eq 'TRUE';
    return 0 if ! defined $cond_vals{$comp};
    }

    return 1;
}


# $BOOLEAN
# &conditional_is_redundant ($COND, @WHENS)
# ----------------------------------------
# Determine whether $COND is redundant with respect to @WHENS.
#
# Returns true if $COND is true for any of the conditions in @WHENS.
#
# If there are no @WHENS, then behave as if @WHENS contained a single empty
# condition.
sub conditional_is_redundant ($@)
{
    my ($cond, @whens) = @_;

    if (@whens == 0)
    {
    return 1 if conditional_true_when ($cond, "");
    }
    else
    {
    foreach my $when (@whens)
    {
        return 1 if conditional_true_when ($cond, $when);
    }
    }

    return 0;
}


# $NEGATION
# condition_negate ($COND)
# ------------------------
sub condition_negate ($)
{
    my ($cond) = @_;

    $cond =~ s/TRUE$/TRUEO/;
    $cond =~ s/FALSE$/TRUE/;
    $cond =~ s/TRUEO$/FALSE/;

    return $cond;
}


# Compare condition names.
# Issue them in alphabetical order, foo_TRUE before foo_FALSE.
sub by_condition
{
    # Be careful we might be comparing `' or `#'.
    $a =~ /^(.*)_(TRUE|FALSE)$/;
    my ($aname, $abool) = ($1 || '', $2 || '');
    $b =~ /^(.*)_(TRUE|FALSE)$/;
    my ($bname, $bbool) = ($1 || '', $2 || '');
    return ($aname cmp $bname
        # Don't bother with IFs, given that TRUE is after FALSE
        # just cmp in the reverse order.
        || $bbool cmp $abool
        # Just in case...
        || $a cmp $b);
}


# &make_condition (@CONDITIONS)
# -----------------------------
# Transform a list of conditions (themselves can be an internal list
# of conditions, e.g., @CONDITIONS = ('cond1 cond2', 'cond3')) into a
# Make conditional (a pattern for AC_SUBST).
# Correctly returns the empty string when there are no conditions.
sub make_condition
{
    my $res = conditional_string (@_);

    # There are no conditions.
    if ($res eq '')
      {
    # Nothing to do.
      }
    # It's impossible.
    elsif ($res eq 'FALSE')
      {
    $res = '#';
      }
    # Build it.
    else
      {
    $res = '@' . $res . '@';
    $res =~ s/ /@@/g;
      }

    return $res;
}



## ------------------------------ ##
## Handling the condition stack.  ##
## ------------------------------ ##


# $COND_STRING
# cond_stack_if ($NEGATE, $COND, $WHERE)
# --------------------------------------
sub cond_stack_if ($$$)
{
  my ($negate, $cond, $where) = @_;

  file_error ($where, "$cond does not appear in AM_CONDITIONAL")
    if ! $configure_cond{$cond} && $cond !~ /^TRUE|FALSE$/;

  $cond = "${cond}_TRUE"
    unless $cond =~ /^TRUE|FALSE$/;
  $cond = condition_negate ($cond)
    if $negate;

  push (@cond_stack, $cond);

  return conditional_string (@cond_stack);
}


# $COND_STRING
# cond_stack_else ($NEGATE, $COND, $WHERE)
# ----------------------------------------
sub cond_stack_else ($$$)
{
  my ($negate, $cond, $where) = @_;

  if (! @cond_stack)
    {
      file_error ($where, "else without if");
      return;
    }

  $cond_stack[$#cond_stack] = condition_negate ($cond_stack[$#cond_stack]);

  # If $COND is given, check against it.
  if (defined $cond)
    {
      $cond = "${cond}_TRUE"
    unless $cond =~ /^TRUE|FALSE$/;
      $cond = condition_negate ($cond)
    if $negate;

      file_error ($where,
          "else reminder ($negate$cond) incompatible with "
          . "current conditional: $cond_stack[$#cond_stack]")
    if $cond_stack[$#cond_stack] ne $cond;
    }

  return conditional_string (@cond_stack);
}


# $COND_STRING
# cond_stack_endif ($NEGATE, $COND, $WHERE)
# -----------------------------------------
sub cond_stack_endif ($$$)
{
  my ($negate, $cond, $where) = @_;
  my $old_cond;

  if (! @cond_stack)
    {
      file_error ($where, "endif without if: $negate$cond");
      return;
    }


  # If $COND is given, check against it.
  if (defined $cond)
    {
      $cond = "${cond}_TRUE"
    unless $cond =~ /^TRUE|FALSE$/;
      $cond = condition_negate ($cond)
    if $negate;

      file_error ($where,
          "endif reminder ($negate$cond) incompatible with "
          . "current conditional: $cond_stack[$#cond_stack]")
    if $cond_stack[$#cond_stack] ne $cond;
    }

  pop @cond_stack;

  return conditional_string (@cond_stack);
}





## ------------------------ ##
## Handling the variables.  ##
## ------------------------ ##


# check_ambiguous_conditional ($VAR, $COND)
# -----------------------------------------
# Check for an ambiguous conditional.  This is called when a variable
# is being defined conditionally.  If we already know about a
# definition that is true under the same conditions, then we have an
# ambiguity.
sub check_ambiguous_conditional ($$)
{
    my ($var, $cond) = @_;
    my $message = conditional_ambiguous_p ($var, $cond);
    if ($message ne '')
    {
    macro_error ($var, $message);
    macro_dump ($var);
    }
}

# $STRING
# conditional_ambiguous_p ($VAR, $COND)
# -------------------------------------
# Check for an ambiguous conditional.  Return an error message if we
# have one, the empty string otherwise.
sub conditional_ambiguous_p ($$)
{
    my ($var, $cond) = @_;
    foreach my $vcond (keys %{$var_value{$var}})
    {
       my $message;
       if ($vcond eq $cond)
       {
       return "$var multiply defined in condition $cond";
       }
       elsif (&conditional_true_when ($vcond, $cond))
       {
     return ("$var was already defined in condition $vcond, "
         . "which implies condition $cond");
       }
       elsif (&conditional_true_when ($cond, $vcond))
       {
       return ("$var was already defined in condition $vcond, "
           . "which is implied by condition $cond");
       }
   }

    return '';
}


# &macro_define($VAR, $VAR_IS_AM, $TYPE, $COND, $VALUE, $WHERE)
# -------------------------------------------------------------
# The $VAR can go from Automake to user, but not the converse.
sub macro_define ($$$$$$)
{
  my ($var, $var_is_am, $type, $cond, $value, $where) = @_;

  file_error ($where, "bad macro name `$var'")
    if $var !~ /$MACRO_PATTERN/o;

  $cond ||= 'TRUE';

  # An Automake variable must be consistently defined with the same
  # sign by Automake.  A user variable must be set by either `=' or
  # `:=', and later promoted to `+='.
  if ($var_is_am)
    {
      if (defined $var_type{$var} && $var_type{$var} ne $type)
    {
      file_error ($where,
              ("$var was set with `$var_type{$var}=' "
               . "and is now set with `$type='"));
    }
    }
  else
    {
      if (!defined $var_type{$var} && $type eq '+')
    {
      file_error ($where, "$var must be set with `=' before using `+='");
    }
    }
  $var_type{$var} = $type;

  # When adding, since we rewrite, don't try to preserve the
  # Automake continuation backslashes.
  $value =~ s/\\$//mg
    if $type eq '+' && $var_is_am;

  # Differentiate the first assignment (including with `+=').
  if ($type eq '+' && defined $var_value{$var}{$cond})
    {
      if (chomp $var_value{$var}{$cond})
    {
      # Insert a backslash before a trailing newline.
      $var_value{$var}{$cond} .= "\\\n";
    }
      elsif ($var_value{$var}{$cond})
    {
      # Insert a separator.
      $var_value{$var}{$cond} .= ' ';
    }
       $var_value{$var}{$cond} .= $value;
    }
  else
    {
      # The first assignment to a macro sets its location.  Ideally I
      # suppose we would associate line numbers with random bits of text.
      # FIXME: We sometimes redefine some variables, but we want to keep
      # the original location.  More subs are needed to handle
      # properly variables.  Once this done, remove this hack.
      $var_location{$var} = $where
    unless defined $var_location{$var};

      # If Automake tries to override a value specified by the user,
      # just don't let it do.
      if (defined $var_value{$var}{$cond} && !$var_is_am{$var} && $var_is_am)
    {
      if ($verbose)
        {
          print STDERR "$me: refusing to override the user definition of:\n";
          macro_dump ($var);
          print STDERR "$me: with `$cond' => `$value'\n";
        }
    }
      else
    {
      # There must be no previous value unless the user is redefining
      # an Automake variable or an AC_SUBST variable for an existing
      # condition.
      check_ambiguous_conditional ($var, $cond)
        unless (($var_is_am{$var} && !$var_is_am
             || exists $configure_vars{$var})
            && exists $var_value{$var}{$cond});

      $var_value{$var}{$cond} = $value;
    }
    }

  # An Automake variable can be given to the user, but not the converse.
  if (! defined $var_is_am{$var} || !$var_is_am)
    {
      $var_is_am{$var} = $var_is_am;
    }

  # Call var_VAR_trigger if it's defined.
  # This hook helps to update some internal state *while*
  # parsing the file.  For instance the handling of SUFFIXES
  # requires this (see var_SUFFIXES_trigger).
  my $var_trigger = "var_${var}_trigger";
  &$var_trigger($type, $value) if defined &$var_trigger;
}


# &macro_delete ($VAR, [@CONDS])
# ------------------------------
# Forget about $VAR under the conditions @CONDS, or completely if
# @CONDS is empty.
sub macro_delete ($@)
{
  my ($var, @conds) = @_;

  if (!@conds)
    {
      delete $var_value{$var};
      delete $var_location{$var};
      delete $var_is_am{$var};
      delete $var_comment{$var};
      delete $var_type{$var};
    }
  else
    {
      foreach my $cond (@conds)
    {
      delete $var_value{$var}{$cond};
    }
    }
}


# &macro_dump ($VAR)
# ------------------
sub macro_dump ($)
{
  my ($var) = @_;

  if (!exists $var_value{$var})
    {
      print STDERR "  $var does not exist\n";
    }
  else
    {
      my $var_is_am = $var_is_am{$var} ? "Automake" : "User";
      my $where = (defined $var_location{$var}
           ? $var_location{$var} : "undefined");
      print STDERR "$var_comment{$var}"
    if defined $var_comment{$var};
      print STDERR "  $var ($var_is_am, where = $where) $var_type{$var}=\n";
      print STDERR "  {\n";
      foreach my $vcond (sort by_condition keys %{$var_value{$var}})
    {
      print STDERR "    $vcond => $var_value{$var}{$vcond}\n";
    }
      print STDERR "  }\n";
    }
}


# &macros_dump ()
# ---------------
sub macros_dump ()
{
  my ($var) = @_;

  print STDERR "%var_value =\n";
  print STDERR "{\n";
  foreach my $var (sort (keys %var_value))
    {
      macro_dump ($var);
    }
  print STDERR "}\n";
}


# $BOOLEAN
# variable_defined ($VAR, [$COND])
# ---------------------------------
# See if a variable exists.  $VAR is the variable name, and $COND is
# the condition which we should check.  If no condition is given, we
# currently return true if the variable is defined under any
# condition.
sub variable_defined ($;$)
{
    my ($var, $cond) = @_;

    # Unfortunately we can't just check for $var_value{VAR}{COND}
    # as this would make perl create $condition{VAR}, which we
    # don't want.
    if (!exists $var_value{$var})
      {
    macro_error ($var, "`$var' is a target; expected a variable")
      if defined $targets{$var};
    # The variable is not defined
    return 0;
      }

    # The variable is not defined for the given condition.
    return 0
      if $cond && !exists $var_value{$var}{$cond};

    # Even a var_value examination is good enough for us.  FIXME:
    # really should maintain examined status on a per-condition basis.
    $content_seen{$var} = 1;
    return 1;
}


# $BOOLEAN
# variable_assert ($VAR, $WHERE)
# ------------------------------
# Make sure a variable exists.  $VAR is the variable name, and $WHERE
# is the name of a macro which refers to $VAR.
sub variable_assert ($$)
{
  my ($var, $where) = @_;

  return 1
    if variable_defined $var;

  macro_error ($where, "variable `$var' not defined");

  return 0;
}


# Mark a variable as examined.
sub examine_variable
{
    my ($var) = @_;
    variable_defined ($var);
}


# &variable_conditions_recursive ($VAR)
# -------------------------------------
# Return the set of conditions for which a variable is defined.

# If the variable is not defined conditionally, and is not defined in
# terms of any variables which are defined conditionally, then this
# returns the empty list.

# If the variable is defined conditionally, but is not defined in
# terms of any variables which are defined conditionally, then this
# returns the list of conditions for which the variable is defined.

# If the variable is defined in terms of any variables which are
# defined conditionally, then this returns a full set of permutations
# of the subvariable conditions.  For example, if the variable is
# defined in terms of a variable which is defined for COND_TRUE,
# then this returns both COND_TRUE and COND_FALSE.  This is
# because we will need to define the variable under both conditions.
sub variable_conditions_recursive ($)
{
    my ($var) = @_;

    %vars_scanned = ();

    my @new_conds = variable_conditions_recursive_sub ($var, '');
    # Now we want to return all permutations of the subvariable
    # conditions.
    my %allconds = ();
    foreach my $item (@new_conds)
    {
    foreach (split (' ', $item))
    {
        s/^(.*)_(TRUE|FALSE)$/$1_TRUE/;
        $allconds{$_} = 1;
    }
    }
    @new_conds = variable_conditions_permutations (sort keys %allconds);

    my %uniqify;
    foreach my $cond (@new_conds)
    {
    my $reduce = variable_conditions_reduce (split (' ', $cond));
        next
        if $reduce eq 'FALSE';
    $uniqify{$cond} = 1;
    }

    # Note we cannot just do `return sort keys %uniqify', because this
    # function is sometimes used in a scalar context.
    my @uniq_list = sort by_condition keys %uniqify;
    return @uniq_list;
}


# @CONDS
# variable_conditions ($VAR)
# --------------------------
# Get the list of conditions that a variable is defined with, without
# recursing through the conditions of any subvariables.
# Argument is $VAR: the variable to get the conditions of.
# Returns the list of conditions.
sub variable_conditions ($)
{
    my ($var) = @_;
    my @conds = keys %{$var_value{$var}};
    return sort by_condition @conds;
}


# $BOOLEAN
# &variable_conditionally_defined ($VAR)
# --------------------------------------
sub variable_conditionally_defined ($)
{
    my ($var) = @_;
    foreach my $cond (variable_conditions_recursive ($var))
      {
    return 1
      unless $cond =~ /^TRUE|FALSE$/;
      }
    return 0;
}



# &variable_conditions_recursive_sub ($VAR, $PARENT)
# -------------------------------------------------------
# A subroutine of variable_conditions_recursive.  This returns all the
# conditions of $VAR, including those of any sub-variables.
sub variable_conditions_recursive_sub
{
    my ($var, $parent) = @_;
    my @new_conds = ();

    if (defined $vars_scanned{$var})
    {
    macro_error ($parent, "variable `$var' recursively defined");
    return ();
    }
    $vars_scanned{$var} = 1;

    my @this_conds = ();
    # Examine every condition under which $VAR is defined.
    foreach my $vcond (keys %{$var_value{$var}})
    {
    push (@this_conds, $vcond);

    # If $VAR references some other variable, then compute the
    # conditions for that subvariable.
    my @subvar_conds = ();
    foreach (split (' ', $var_value{$var}{$vcond}))
    {
        # If a comment seen, just leave.
        last if /^#/;

        # Handle variable substitutions.
        if (/^\$\{(.*)\}$/ || /^\$\((.*)\)$/)
        {
            my $varname = $1;
        if ($varname =~ /$SUBST_REF_PATTERN/o)
        {
            $varname = $1;
        }


        # Here we compute all the conditions under which the
        # subvariable is defined.  Then we go through and add
        # $VCOND to each.
        my @svc = variable_conditions_recursive_sub ($varname, $var);
        foreach my $item (@svc)
        {
            my $val = conditional_string ($vcond, split (' ', $item));
            $val ||= 'TRUE';
            push (@subvar_conds, $val);
        }
        }
    }

    # If there are no conditional subvariables, then we want to
    # return this condition.  Otherwise, we want to return the
    # permutations of the subvariables, taking into account the
    # conditions of $VAR.
    if (! @subvar_conds)
    {
        push (@new_conds, $vcond);
    }
    else
    {
        push (@new_conds, variable_conditions_reduce (@subvar_conds));
    }
    }

    # Unset our entry in vars_scanned.  We only care about recursive
    # definitions.
    delete $vars_scanned{$var};

    # If we are being called on behalf of another variable, we need to
    # return all possible permutations of the conditions.  We have
    # already handled everything in @this_conds along with their
    # subvariables.  We now need to add any permutations that are not
    # in @this_conds.
    foreach my $this_cond (@this_conds)
    {
    my @perms =
        variable_conditions_permutations (split (' ', $this_cond));
    foreach my $perm (@perms)
    {
        my $ok = 1;
        foreach my $scan (@this_conds)
        {
        if (&conditional_true_when ($perm, $scan)
            || &conditional_true_when ($scan, $perm))
        {
            $ok = 0;
            last;
        }
        }
        next if ! $ok;

        # This permutation was not already handled, and is valid
        # for the parents.
        push (@new_conds, $perm);
    }
    }

    return @new_conds;
}


# Filter a list of conditionals so that only the exclusive ones are
# retained.  For example, if both `COND1_TRUE COND2_TRUE' and
# `COND1_TRUE' are in the list, discard the latter.
# If the list is empty, return TRUE
sub variable_conditions_reduce
{
    my (@conds) = @_;
    my @ret = ();
    my $cond;
    while(@conds > 0)
    {
    $cond = shift(@conds);

        # FALSE is absorbent.
    return 'FALSE'
      if $cond eq 'FALSE';

    if (!conditional_is_redundant ($cond, @ret, @conds))
      {
        push (@ret, $cond);
      }
    }

    return "TRUE" if @ret == 0;
    return @ret;
}

# @CONDS
# invert_conditions (@CONDS)
# --------------------------
# Invert a list of conditionals.  Returns a set of conditionals which
# are never true for any of the input conditionals, and when taken
# together with the input conditionals cover all possible cases.
#
# For example: invert_conditions("A_TRUE B_TRUE", "A_FALSE B_FALSE") will
# return ("A_FALSE B_TRUE", "A_TRUE B_FALSE")
sub invert_conditions
{
    my (@conds) = @_;

    my @notconds = ();
    foreach my $cond (@conds)
    {
    foreach my $perm (variable_conditions_permutations (split(' ', $cond)))
    {
        push @notconds, $perm
            if ! conditional_is_redundant ($perm, @conds);
    }
    }
    return variable_conditions_reduce (@notconds);
}

# Return a list of permutations of a conditional string.
sub variable_conditions_permutations
{
    my (@comps) = @_;
    return ()
    if ! @comps;
    my $comp = shift (@comps);
    return variable_conditions_permutations (@comps)
    if $comp eq '';
    my $neg = condition_negate ($comp);

    my @ret;
    foreach my $sub (variable_conditions_permutations (@comps))
    {
    push (@ret, "$comp $sub");
    push (@ret, "$neg $sub");
    }
    if (! @ret)
    {
    push (@ret, $comp);
    push (@ret, $neg);
    }
    return @ret;
}


# $BOOL
# &check_variable_defined_unconditionally($VAR, $PARENT)
# ------------------------------------------------------
# Warn if a variable is conditionally defined.  This is called if we
# are using the value of a variable.
sub check_variable_defined_unconditionally ($$)
{
    my ($var, $parent) = @_;
    foreach my $cond (keys %{$var_value{$var}})
    {
        next
      if $cond =~ /^TRUE|FALSE$/;

    if ($parent)
    {
        macro_error ($parent,
             "warning: automake does not support conditional definition of $var in $parent");
    }
    else
    {
        macro_error ($parent,
             "warning: automake does not support $var being defined conditionally");
    }
    }
}


# Get the TRUE value of a variable, warn if the variable is
# conditionally defined.
sub variable_value
{
    my ($var) = @_;
    &check_variable_defined_unconditionally ($var);
    return $var_value{$var}{'TRUE'};
}


# @VALUES
# &value_to_list ($VAR, $VAL, $COND)
# ----------------------------------
# Convert a variable value to a list, split as whitespace.  This will
# recursively follow $(...) and ${...} inclusions.  It preserves @...@
# substitutions.
#
# If COND is 'all', then all values under all conditions should be
# returned; if COND is a particular condition (all conditions are
# surrounded by @...@) then only the value for that condition should
# be returned; otherwise, warn if VAR is conditionally defined.
# SCANNED is a global hash listing whose keys are all the variables
# already scanned; it is an error to rescan a variable.
sub value_to_list ($$$)
{
    my ($var, $val, $cond) = @_;
    my @result;

    # Strip backslashes
    $val =~ s/\\(\n|$)/ /g;

    foreach (split (' ', $val))
    {
    # If a comment seen, just leave.
    last if /^#/;

    # Handle variable substitutions.
    if (/^\$\{([^}]*)\}$/ || /^\$\(([^)]*)\)$/)
    {
        my $varname = $1;

        # If the user uses a losing variable name, just ignore it.
        # This isn't ideal, but people have requested it.
        next if ($varname =~ /\@.*\@/);

        my ($from, $to);
        my @temp_list;
        if ($varname =~ /$SUBST_REF_PATTERN/o)
        {
        $varname = $1;
        $to = $3;
        $from = quotemeta $2;
        }

        # Find the value.
        @temp_list =
          variable_value_as_list_recursive_worker ($1, $cond, $var);

        # Now rewrite the value if appropriate.
        if (defined $from)
        {
        grep (s/$from$/$to/, @temp_list);
        }

        push (@result, @temp_list);
    }
    else
    {
        push (@result, $_);
    }
    }

    return @result;
}


# @VALUES
# variable_value_as_list ($VAR, $COND, $PARENT)
# ---------------------------------------------
# Get the value of a variable given a specified condition. without
# recursing through any subvariables.
# Arguments are:
#   $VAR    is the variable
#   $COND   is the condition.  If this is not given, the value for the
#           "TRUE" condition will be returned.
#   $PARENT is the variable in which the variable is used: this is used
#           only for error messages.
# Returns the list of conditions.
# For example, if A is defined as "foo $(B) bar", and B is defined as
# "baz", this will return ("foo", "$(B)", "bar")
sub variable_value_as_list
{
    my ($var, $cond, $parent) = @_;
    my @result;

    # Check defined
    return
      unless variable_assert $var, $parent;

    # Get value for given condition
    $cond ||= 'TRUE';
    my $onceflag;
    foreach my $vcond (keys %{$var_value{$var}})
    {
    my $val = $var_value{$var}{$vcond};

    if (&conditional_true_when ($vcond, $cond))
    {
        # Unless variable is not defined conditionally, there should only
        # be one value of $vcond true when $cond.
        &check_variable_defined_unconditionally ($var, $parent)
            if $onceflag;
        $onceflag = 1;

        # Strip backslashes
        $val =~ s/\\(\n|$)/ /g;

        foreach (split (' ', $val))
        {
        # If a comment seen, just leave.
        last if /^#/;

        push (@result, $_);
        }
    }
    }

    return @result;
}


# @VALUE
# &variable_value_as_list_recursive_worker ($VAR, $COND, $PARENT)
# ---------------------------------------------------------------
# Return contents of VAR as a list, split on whitespace.  This will
# recursively follow $(...) and ${...} inclusions.  It preserves @...@
# substitutions.  If COND is 'all', then all values under all
# conditions should be returned; if COND is a particular condition
# (all conditions are surrounded by @...@) then only the value for
# that condition should be returned; otherwise, warn if VAR is
# conditionally defined.  If PARENT is specified, it is the name of
# the including variable; this is only used for error reports.
sub variable_value_as_list_recursive_worker ($$$)
{
    my ($var, $cond, $parent) = @_;
    my @result = ();

    return
      unless variable_assert $var, $parent;

    if (defined $vars_scanned{$var})
    {
    # `vars_scanned' is a global we use to keep track of which
    # variables we've already examined.
    macro_error ($parent, "variable `$var' recursively defined");
    }
    elsif ($cond eq 'all')
    {
    $vars_scanned{$var} = 1;
    foreach my $vcond (keys %{$var_value{$var}})
    {
        my $val = $var_value{$var}{$vcond};
        push (@result, &value_to_list ($var, $val, $cond));
    }
    }
    else
    {
        $cond ||= 'TRUE';
    $vars_scanned{$var} = 1;
    my $onceflag;
    foreach my $vcond (keys %{$var_value{$var}})
    {
        my $val = $var_value{$var}{$vcond};
        if (&conditional_true_when ($vcond, $cond))
        {
        # Warn if we have an ambiguity.  It's hard to know how
        # to handle this case correctly.
        &check_variable_defined_unconditionally ($var, $parent)
            if $onceflag;
        $onceflag = 1;
        push (@result, &value_to_list ($var, $val, $cond));
        }
    }
    }

    # Unset our entry in vars_scanned.  We only care about recursive
    # definitions.
    delete $vars_scanned{$var};

    return @result;
}


# &variable_output ($VAR, [@CONDS])
# ---------------------------------
# Output all the values of $VAR is @COND is not specified, else only
# that corresponding to @COND.
sub variable_output ($@)
{
  my ($var, @conds) = @_;

  @conds = keys %{$var_value{$var}}
    unless @conds;

  $output_vars .= $var_comment{$var}
    if defined $var_comment{$var};

  foreach my $cond (sort by_condition @conds)
    {
      my $val = $var_value{$var}{$cond};
      my $equals = $var_type{$var} eq ':' ? ':=' : '=';
      my $output_var = "$var $equals $val";
      $output_var =~ s/^/make_condition ($cond)/meg;
      $output_vars .= $output_var . "\n";
    }
}


# &variable_pretty_output ($VAR, [@CONDS])
# ----------------------------------------
# Likewise, but pretty, i.e., we *split* the values at spaces.   Use only
# with variables holding filenames.
sub variable_pretty_output ($@)
{
  my ($var, @conds) = @_;

  @conds = keys %{$var_value{$var}}
    unless @conds;

  $output_vars .= $var_comment{$var}
    if defined $var_comment{$var};

  foreach my $cond (sort by_condition @conds)
    {
      my $val = $var_value{$var}{$cond};
      my $equals = $var_type{$var} eq ':' ? ':=' : '=';
      my $make_condition = make_condition ($cond);
      $output_vars .= pretty_print_internal ("$make_condition$var $equals",
                         "$make_condition\t",
                         split (' ' , $val));
    }
}


# &variable_value_as_list_recursive ($VAR, $COND, $PARENT)
# --------------------------------------------------------
# This is just a wrapper for variable_value_as_list_recursive_worker that
# initializes the global hash `vars_scanned'.  This hash is used to
# avoid infinite recursion.
sub variable_value_as_list_recursive ($$@)
{
    my ($var, $cond, $parent) = @_;
    %vars_scanned = ();
    return &variable_value_as_list_recursive_worker ($var, $cond, $parent);
}


# &define_pretty_variable ($VAR, $COND, @VALUE)
# ---------------------------------------------
# Like define_variable, but the value is a list, and the variable may
# be defined conditionally.  The second argument is the conditional
# under which the value should be defined; this should be the empty
# string to define the variable unconditionally.  The third argument
# is a list holding the values to use for the variable.  The value is
# pretty printed in the output file.
sub define_pretty_variable ($$@)
{
    my ($var, $cond, @value) = @_;

    # Beware that an empty $cond has a different semantics for
    # macro_define and variable_pretty_output.
    $cond ||= 'TRUE';

    if (! variable_defined ($var, $cond))
    {
        macro_define ($var, 1, '', $cond, "@value", undef);
    variable_pretty_output ($var, $cond || 'TRUE');
    $content_seen{$var} = 1;
    }
}


# define_variable ($VAR, $VALUE)
# ------------------------------
# Define a new user variable VAR to VALUE, but only if not already defined.
sub define_variable ($$)
{
    my ($var, $value) = @_;
    define_pretty_variable ($var, 'TRUE', $value);
}


# Like define_variable, but define a variable to be the configure
# substitution by the same name.
sub define_configure_variable ($)
{
    my ($var) = @_;
    if (! variable_defined ($var, 'TRUE'))
    {
    # A macro defined via configure is a `user' macro -- we should not
    # override it.
    macro_define ($var, 0, '', 'TRUE', subst $var, $configure_vars{$var});
    variable_pretty_output ($var, 'TRUE');
    }
}


# define_compiler_variable ($LANG)
# --------------------------------
# Define a compiler variable.  We also handle defining the `LT'
# version of the command when using libtool.
sub define_compiler_variable ($)
{
    my ($lang) = @_;

    my ($var, $value) = ($lang->compiler, $lang->compile);
    &define_variable ($var, $value);
    &define_variable ("LT$var", "\$(LIBTOOL) --mode=compile $value")
      if $seen_libtool;
}


# define_linker_variable ($LANG)
# ------------------------------
# Define linker variables.
sub define_linker_variable ($)
{
    my ($lang) = @_;

    my ($var, $value) = ($lang->lder, $lang->ld);
    # CCLD = $(CC).
    &define_variable ($lang->lder, $lang->ld);
    # CCLINK = $(CCLD) blah blah...
    &define_variable ($lang->linker,
              (($seen_libtool ? '$(LIBTOOL) --mode=link ' : '')
               . $lang->link));
}

################################################################

## ---------------- ##
## Handling rules.  ##
## ---------------- ##

# $BOOL
# rule_define ($TARGET, $IS_AM, $COND, $WHERE)
# --------------------------------------------
# Define a new rule.  $TARGET is the rule name.  $IS_AM is a boolean
# which is true if the new rule is defined by the user.  $COND is the
# condition under which the rule is defined.  $WHERE is where the rule
# is defined (file name or line number).  Returns true if it is ok to
# define the rule, false otherwise.
sub rule_define ($$$$)
{
  my ($target, $rule_is_am, $cond, $where) = @_;

  # For now `foo:' will override `foo$(EXEEXT):'.  This is temporary,
  # though, so we emit a warning.
  (my $noexe = $target) =~ s,\$\(EXEEXT\)$,,;
  if ($noexe ne $target && defined $targets{$noexe})
  {
      # The no-exeext option enables this feature.
      if (! defined $options{'no-exeext'})
      {
      macro_error ($noexe,
               "deprecated feature: `$noexe' overrides `$noexe\$(EXEEXT)'\nchange your target to read `$noexe\$(EXEEXT)'");
      }
      # Don't define.
      return 0;
  }

  if (defined $targets{$target}
      && ($cond
      ? ! defined $target_conditional{$target}
      : defined $target_conditional{$target}))
  {
      target_error ($target,
            "$target defined both conditionally and unconditionally");
  }

  # Value here doesn't matter; for targets we only note existence.
  $targets{$target} = $where;
  if ($cond)
  {
      if ($target_conditional{$target})
      {
      &check_ambiguous_conditional ($target, $cond);
      }
      $target_conditional{$target}{$cond} = $where;
  }

  # Check the rule for being a suffix rule. If so, store in a hash.
  # Either it's a rule for two known extensions...
  if ($target =~ /^($KNOWN_EXTENSIONS_PATTERN)($KNOWN_EXTENSIONS_PATTERN)$/
  # ...or it's a rule with unknown extensions (.i.e, the rule looks like
  # `.foo.bar:' but `.foo' or `.bar' are not declared in SUFFIXES
  # and are not known language extensions).
  # Automake will complete SUFFIXES from @suffixes automatically
  # (see handle_footer).
      || ($target =~ /$SUFFIX_RULE_PATTERN/o && accept_extensions($1)))
  {
      my $internal_ext = $2;

      # When tranforming sources to objects, Automake uses the
      # %suffix_rules to move from each source extension to
      # `.$(OBJEXT)', not to `.o' or `.obj'.  However some people
      # define suffix rules for `.o' or `.obj', so internally we will
      # consider these extensions equivalent to `.$(OBJEXT)'.  We
      # CANNOT rewrite the target (i.e., automagically replace `.o'
      # and `.obj' by `.$(OBJEXT)' in the output), or warn the user
      # that (s)he'd better use `.$(OBJEXT)', because Automake itself
      # output suffix rules for `.o' or `.obj'...
      $internal_ext = '.$(OBJEXT)' if ($2 eq '.o' || $2 eq '.obj');

      $suffix_rules{$1} = $internal_ext;
      verbose "Sources ending in $1 become $2";
      push @suffixes, $1, $2;
  }

  return 1;
}


# See if a target exists.
sub target_defined
{
    my ($target) = @_;
    return defined $targets{$target};
}


################################################################

# &append_comments ($VARIABLE, $SPACING, $COMMENT)
# ------------------------------------------------
# Apped $COMMENT to the other comments for $VARIABLE, using
# $SPACING as separator.
sub append_comments ($$$)
{
    my ($var, $spacing, $comment) = @_;
    $var_comment{$var} .= $spacing
    if (!defined $var_comment{$var} || $var_comment{$var} !~ /\n$/o);
    $var_comment{$var} .= $comment;
}


# &read_am_file ($AMFILE)
# -----------------------
# Read Makefile.am and set up %contents.  Simultaneously copy lines
# from Makefile.am into $output_trailer or $output_vars as
# appropriate.  NOTE we put rules in the trailer section.  We want
# user rules to come after our generated stuff.
sub read_am_file ($)
{
    my ($amfile) = @_;

    my $am_file = new Automake::XFile ("< $amfile");
    verbose "reading $amfile";

    my $spacing = '';
    my $comment = '';
    my $blank = 0;
    my $saw_bk = 0;

    use constant IN_VAR_DEF => 0;
    use constant IN_RULE_DEF => 1;
    use constant IN_COMMENT => 2;
    my $prev_state = IN_RULE_DEF;

    while ($_ = $am_file->getline)
    {
    if (/$IGNORE_PATTERN/o)
    {
        # Merely delete comments beginning with two hashes.
    }
    elsif (/$WHITE_PATTERN/o)
    {
        file_error ("$amfile:$.",
            "blank line following trailing backslash")
        if $saw_bk;
        # Stick a single white line before the incoming macro or rule.
        $spacing = "\n";
        $blank = 1;
        # Flush all comments seen so far.
        if ($comment ne '')
        {
        $output_vars .= $comment;
        $comment = '';
        }
    }
    elsif (/$COMMENT_PATTERN/o)
    {
        # Stick comments before the incoming macro or rule.  Make
        # sure a blank line preceeds first block of comments.
        $spacing = "\n" unless $blank;
        $blank = 1;
        $comment .= $spacing . $_;
        $spacing = '';
        $prev_state = IN_COMMENT;
    }
    else
    {
        last;
    }
    $saw_bk = /\\$/ && ! /$IGNORE_PATTERN/o;
    }

    # We save the conditional stack on entry, and then check to make
    # sure it is the same on exit.  This lets us conditonally include
    # other files.
    my @saved_cond_stack = @cond_stack;
    my $cond = conditional_string (@cond_stack);

    my $last_var_name = '';
    my $last_var_type = '';
    my $last_var_value = '';
    # FIXME: shouldn't use $_ in this loop; it is too big.
    while ($_)
    {
        my $here = "$amfile:$.";

    # Make sure the line is \n-terminated.
    chomp;
    $_ .= "\n";

    # Don't look at MAINTAINER_MODE_TRUE here.  That shouldn't be
    # used by users.  @MAINT@ is an anachronism now.
    $_ =~ s/\@MAINT\@//g
        unless $seen_maint_mode;

    my $new_saw_bk = /\\$/ && ! /$IGNORE_PATTERN/o;

    if (/$IGNORE_PATTERN/o)
    {
        # Merely delete comments beginning with two hashes.
    }
    elsif (/$WHITE_PATTERN/o)
    {
        # Stick a single white line before the incoming macro or rule.
        $spacing = "\n";
        file_error ($here, "blank line following trailing backslash")
        if $saw_bk;
    }
    elsif (/$COMMENT_PATTERN/o)
    {
        # Stick comments before the incoming macro or rule.
        $comment .= $spacing . $_;
        $spacing = '';
        file_error ($here, "comment following trailing backslash")
        if $saw_bk && $comment eq '';
        $prev_state = IN_COMMENT;
    }
    elsif ($saw_bk)
    {
        if ($prev_state == IN_RULE_DEF)
        {
            $output_trailer .= &make_condition (@cond_stack);
        $output_trailer .= $_;
        }
        elsif ($prev_state == IN_COMMENT)
        {
        # If the line doesn't start with a `#', add it.
        # We do this because a continuated comment like
        #   # A = foo \
        #         bar \
        #         baz
        # is not portable.  BSD make doesn't honor
        # escaped newlines in comments.
        s/^#?/#/;
        $comment .= $spacing . $_;
        }
        else # $prev_state == IN_VAR_DEF
        {
          $last_var_value .= ' '
        unless $last_var_value =~ /\s$/;
          $last_var_value .= $_;

          if (!/\\$/)
        {
          append_comments $last_var_name, $spacing, $comment;
          $comment = $spacing = '';
          macro_define ($last_var_name, 0,
                $last_var_type, $cond,
                $last_var_value, $here)
            if $cond ne 'FALSE';
          push (@var_list, $last_var_name);
        }
        }
    }

    elsif (/$IF_PATTERN/o)
      {
        $cond = cond_stack_if ($1, $2, $here);
      }
    elsif (/$ELSE_PATTERN/o)
      {
        $cond = cond_stack_else ($1, $2, $here);
      }
    elsif (/$ENDIF_PATTERN/o)
      {
        $cond = cond_stack_endif ($1, $2, $here);
      }

    elsif (/$RULE_PATTERN/o)
    {
        # Found a rule.
        $prev_state = IN_RULE_DEF;

        rule_define ($1, 0, $cond, $here);

        $output_trailer .= $comment . $spacing;
            $output_trailer .= &make_condition (@cond_stack);
            $output_trailer .= $_;
        $comment = $spacing = '';
    }
    elsif (/$ASSIGNMENT_PATTERN/o)
    {
        # Found a macro definition.
        $prev_state = IN_VAR_DEF;
        $last_var_name = $1;
        $last_var_type = $2;
        $last_var_value = $3;
        if ($3 ne '' && substr ($3, -1) eq "\\")
        {
        # We preserve the `\' because otherwise the long lines
        # that are generated will be truncated by broken
        # `sed's.
        $last_var_value = $3 . "\n";
        }

        if (!/\\$/)
          {
        # FIXME: this doesn't always work correctly; it will
        # group all comments for a given variable, no matter
        # where defined.
        # Accumulating variables must not be output.
        append_comments $last_var_name, $spacing, $comment;
        $comment = $spacing = '';

        macro_define ($last_var_name, 0,
                  $last_var_type, $cond,
                  $last_var_value, $here)
          if $cond ne 'FALSE';
        push (@var_list, $last_var_name);
          }
    }
        elsif (/$INCLUDE_PATTERN/o)
        {
            my $path = $1;

            if ($path =~ s/^\$\(top_srcdir\)\///)
            {
                push (@include_stack, "\$\(top_srcdir\)/$path");
            }
            else
            {
                $path =~ s/\$\(srcdir\)\///;
                push (@include_stack, "\$\(srcdir\)/$path");
                $path = $relative_dir . "/" . $path;
            }
            &read_am_file ($path);
        }
    else
        {
        # This isn't an error; it is probably a continued rule.
        # In fact, this is what we assume.
        $prev_state = IN_RULE_DEF;
        $output_trailer .= $comment . $spacing;
        $output_trailer .= &make_condition  (@cond_stack);
        $output_trailer .= $_;
        $comment = $spacing = '';
        file_error ($here, "`#' comment at start of rule is unportable")
        if $_ =~ /^\t\s*\#/;
    }

    $saw_bk = $new_saw_bk;
        $_ = $am_file->getline;
    }

    $output_trailer .= $comment;

    if ("@saved_cond_stack" ne "@cond_stack")
    {
    if (@cond_stack)
    {
        &am_error ("unterminated conditionals: @cond_stack");
    }
    else
    {
        # FIXME: better error message here.
        &am_error ("conditionals not nested in include file");
    }
    }
}


# define_standard_variables ()
# ----------------------------
# A helper for read_main_am_file which initializes configure variables
# and variables from header-vars.am.  This is a subr so we can call it
# twice.
sub define_standard_variables
{
    my $saved_output_vars = $output_vars;
    my ($comments, undef, $rules) =
      file_contents_internal (1, "$libdir/am/header-vars.am");

    # This will output the definitions in $output_vars, which we don't
    # want...
    foreach my $var (sort keys %configure_vars)
    {
        &define_configure_variable ($var);
        push (@var_list, $var);
    }

    # ... hence, we restore $output_vars.
    $output_vars = $saved_output_vars . $comments . $rules;
}

# Read main am file.
sub read_main_am_file
{
    my ($amfile) = @_;

    # This supports the strange variable tricks we are about to play.
    if (scalar keys %var_value > 0)
      {
    macros_dump ();
    prog_error ("variable defined before read_main_am_file");
      }

    # Generate copyright header for generated Makefile.in.
    # We do discard the output of predefined variables, handled below.
    $output_vars = ("# $in_file_name generated by automake "
           . $VERSION . " from $am_file_name.\n");
    $output_vars .= '# ' . subst ('configure_input') . "\n";
    $output_vars .= $gen_copyright;

    # We want to predefine as many variables as possible.  This lets
    # the user set them with `+=' in Makefile.am.  However, we don't
    # want these initial definitions to end up in the output quite
    # yet.  So we just load them, but output them later.
    &define_standard_variables;

    # Read user file, which might override some of our values.
    &read_am_file ($amfile);

    # Output all the Automake variables.  If the user changed one,
    # then it is now marked as owned by the user.
    foreach my $var (uniq @var_list)
    {
    # Don't process user variables.
        variable_output ($var)
      unless !$var_is_am{$var};
    }

    # Now dump the user variables that were defined.  We do it in the same
    # order in which they were defined (skipping duplicates).
    foreach my $var (uniq @var_list)
    {
    # Don't process Automake variables.
        variable_output ($var)
      unless $var_is_am{$var};
    }
}

################################################################

# $FLATTENED
# &flatten ($STRING)
# ------------------
# Flatten the $STRING and return the result.
sub flatten
{
  $_ = shift;

  s/\\\n//somg;
  s/\s+/ /g;
  s/^ //;
  s/ $//;

  return $_;
}


# @PARAGRAPHS
# &make_paragraphs ($MAKEFILE, [%TRANSFORM])
# ------------------------------------------
# Load a $MAKEFILE, apply the %TRANSFORM, and return it as a list of
# paragraphs.
sub make_paragraphs ($%)
{
    my ($file, %transform) = @_;

    # Complete %transform with global options and make it a Perl
    # $command.
    my $command =
      "s/$IGNORE_PATTERN//gm;"
    . transform (%transform,

             'CYGNUS'          => $cygnus_mode,
             'MAINTAINER-MODE'
             => $seen_maint_mode ? subst ('MAINTAINER_MODE_TRUE') : '',

             'SHAR'        => $options{'dist-shar'} || 0,
             'BZIP2'       => $options{'dist-bzip2'} || 0,
             'ZIP'         => $options{'dist-zip'} || 0,
             'COMPRESS'    => $options{'dist-tarZ'} || 0,

             'INSTALL-INFO' => !$options{'no-installinfo'},
             'INSTALL-MAN'  => !$options{'no-installman'},
             'CK-NEWS'      => $options{'check-news'} || 0,

             'SUBDIRS'      => variable_defined ('SUBDIRS'),
             'TOPDIR'       => backname ($relative_dir),
             'TOPDIR_P'     => $relative_dir eq '.',
             'CONFIGURE-AC' => $configure_ac,

             'BUILD'    => $seen_canonical == AC_CANONICAL_SYSTEM,
             'HOST'     => $seen_canonical,
             'TARGET'   => $seen_canonical == AC_CANONICAL_SYSTEM,

             'LIBTOOL'      => defined $configure_vars{'LIBTOOL'})
      # We don't need more than two consecutive new-lines.
      . 's/\n{3,}/\n\n/g';

    # Swallow the file and apply the COMMAND.
    my $fc_file = new Automake::XFile "< $file";
    # Looks stupid?
    verbose "reading $file";
    my $saved_dollar_slash = $/;
    undef $/;
    $_ = $fc_file->getline;
    $/ = $saved_dollar_slash;
    eval $command;
    $fc_file->close;
    my $content = $_;

    # Split at unescaped new lines.
    my @lines = split (/(?<!\\)\n/, $content);
    my @res;

    while (defined ($_ = shift @lines))
      {
    my $paragraph = "$_";
    # If we are a rule, eat as long as we start with a tab.
    if (/$RULE_PATTERN/smo)
      {
        while (defined ($_ = shift @lines) && $_ =~ /^\t/)
          {
        $paragraph .= "\n$_";
          }
        unshift (@lines, $_);
      }

    # If we are a comments, eat as much comments as you can.
    elsif (/$COMMENT_PATTERN/smo)
      {
        while (defined ($_ = shift @lines)
           && $_ =~ /$COMMENT_PATTERN/smo)
          {
        $paragraph .= "\n$_";
          }
        unshift (@lines, $_);
      }

    push @res, $paragraph;
    $paragraph = '';
      }

    return @res;
}



# ($COMMENT, $VARIABLES, $RULES)
# &file_contents_internal ($IS_AM, $FILE, [%TRANSFORM])
# -----------------------------------------------------
# Return contents of a file from $libdir/am, automatically skipping
# macros or rules which are already known. $IS_AM iff the caller is
# reading an Automake file (as opposed to the user's Makefile.am).
sub file_contents_internal ($$%)
{
    my ($is_am, $file, %transform) = @_;

    my $result_vars = '';
    my $result_rules = '';
    my $comment = '';
    my $spacing = '';

    # The following flags are used to track rules spanning across
    # multiple paragraphs.
    my $is_rule = 0;        # 1 if we are processing a rule.
    my $discard_rule = 0;   # 1 if the current rule should not be output.

    # We save the conditional stack on entry, and then check to make
    # sure it is the same on exit.  This lets us conditonally include
    # other files.
    my @saved_cond_stack = @cond_stack;
    my $cond = conditional_string (@cond_stack);

    foreach (make_paragraphs ($file, %transform))
    {
        # Sanity checks.
    file_error ($file, "blank line following trailing backslash:\n$_")
      if /\\$/;
    file_error ($file, "comment following trailing backslash:\n$_")
      if /\\#/;

    if (/^$/)
    {
        $is_rule = 0;
        # Stick empty line before the incoming macro or rule.
        $spacing = "\n";
    }
    elsif (/$COMMENT_PATTERN/mso)
    {
        $is_rule = 0;
        # Stick comments before the incoming macro or rule.
        $comment = "$_\n";
    }

    # Handle inclusion of other files.
        elsif (/$INCLUDE_PATTERN/o)
        {
        if ($cond ne 'FALSE')
          {
        my $file = ($is_am ? "$libdir/am/" : '') . $1;
        # N-ary `.=' fails.
        my ($com, $vars, $rules)
          = file_contents_internal ($is_am, $file, %transform);
        $comment .= $com;
        $result_vars .= $vars;
        $result_rules .= $rules;
          }
        }

        # Handling the conditionals.
        elsif (/$IF_PATTERN/o)
      {
        $cond = cond_stack_if ($1, $2, $file);
      }
    elsif (/$ELSE_PATTERN/o)
      {
        $cond = cond_stack_else ($1, $2, $file);
      }
    elsif (/$ENDIF_PATTERN/o)
      {
        $cond = cond_stack_endif ($1, $2, $file);
      }

        # Handling rules.
    elsif (/$RULE_PATTERN/mso)
    {
      $is_rule = 1;
      $discard_rule = 0;
      # Separate relationship from optional actions: the first
      # `new-line tab" not preceded by backslash (continuation
      # line).
      # I'm quite shoked!  It seems that (\\\n|[^\n]) is not the
      # same as `([^\n]|\\\n)!!!  Don't swap it, it breaks.
      my $paragraph = $_;
      /^((?:\\\n|[^\n])*)(?:\n(\t.*))?$/som;
      my ($relationship, $actions) = ($1, $2 || '');

      # Separate targets from dependencies: the first colon.
      $relationship =~ /^([^:]+\S+) *: *(.*)$/som;
      my ($targets, $dependencies) = ($1, $2);
      # Remove the escaped new lines.
      # I don't know why, but I have to use a tmp $flat_deps.
      my $flat_deps = &flatten ($dependencies);
      my @deps = split (' ', $flat_deps);

      foreach (split (' ' , $targets))
        {
          # FIXME: We are not robust to people defining several targets
          # at once, only some of them being in %dependencies.  The
          # actions from the targets in %dependencies are usually generated
          # from the content of %actions, but if some targets in $targets
          # are not in %dependencies the ELSE branch will output
          # a rule for all $targets (i.e. the targets which are both
          # in %dependencies and $targets will have two rules).

          # FIXME: The logic here is not able to output a
          # multi-paragraph rule several time (e.g. for each conditional
          # it is defined for) because it only knows the first paragraph.

          # Output only if not in FALSE.
          if (defined $dependencies{$_}
          && $cond ne 'FALSE')
        {
          &depend ($_, @deps);
          $actions{$_} .= $actions;
        }
          else
        {
          # Free-lance dependency.  Output the rule for all the
          # targets instead of one by one.

          # Work out all the conditions for which the target hasn't
          # been defined
          my @undefined_conds;
          if (defined $target_conditional{$targets})
            {
              my @defined_conds = keys %{$target_conditional{$targets}};
              @undefined_conds = invert_conditions(@defined_conds);
            }
          else
            {
              if (defined $targets{$targets})
                {
              # No conditions for which target hasn't been defined
              @undefined_conds = ();
                }
              else
            {
              # Target hasn't been defined for any conditions
              @undefined_conds = ("");
            }
            }

          if ($cond ne 'FALSE')
            {
              for my $undefined_cond (@undefined_conds)
              {
              my $condparagraph = $paragraph;
              $condparagraph =~ s/^/make_condition (@cond_stack, $undefined_cond)/gme;
              if (rule_define ($targets, $is_am,
                      "$cond $undefined_cond", $file))
              {
                  $result_rules .=
                  "$spacing$comment$condparagraph\n"
              }
              else
              {
                  # Remember to discard next paragraphs
                  # if they belong to this rule.
                  $discard_rule = 1;
              }
              }
              if ($#undefined_conds == -1)
              {
              # This target has already been defined, the rule
              # has not been defined. Remember to discard next
              # paragraphs if they belong to this rule.
              $discard_rule = 1;
              }
            }
          $comment = $spacing = '';
          last;
        }
        }
    }

    elsif (/$ASSIGNMENT_PATTERN/mso)
    {
        my ($var, $type, $val) = ($1, $2, $3);
        file_error ($file, "macro `$var' with trailing backslash")
          if /\\$/;

        $is_rule = 0;

        # Accumulating variables must not be output.
        append_comments $var, $spacing, $comment;
        macro_define ($var, $is_am, $type, $cond, $val, $file)
          if $cond ne 'FALSE';
        push (@var_list, $var);

        # If the user has set some variables we were in charge
        # of (which is detected by the first reading of
        # `header-vars.am'), we must not output them.
        $result_vars .= "$spacing$comment$_\n"
          if $type ne '+' && $var_is_am{$var} && $cond ne 'FALSE';

        $comment = $spacing = '';
    }
    else
    {
        # This isn't an error; it is probably some tokens which
        # configure is supposed to replace, such as `@SET-MAKE@',
        # or some part of a rule cut by an if/endif.
        if ($cond ne 'FALSE' && ! ($is_rule && $discard_rule))
          {
        s/^/make_condition (@cond_stack)/gme;
        $result_rules .= "$spacing$comment$_\n";
          }
        $comment = $spacing = '';
    }
    }

    if ("@saved_cond_stack" ne "@cond_stack")
    {
    if (@cond_stack)
    {
        &am_error ("unterminated conditionals: @cond_stack");
    }
    else
    {
        # FIXME: better error message here.
        &am_error ("conditionals not nested in include file");
    }
    }

    return ($comment, $result_vars, $result_rules);
}


# $CONTENTS
# &file_contents ($BASENAME, [%TRANSFORM])
# ----------------------------------------
# Return contents of a file from $libdir/am, automatically skipping
# macros or rules which are already known.
sub file_contents ($%)
{
    my ($basename, %transform) = @_;
    my ($comments, $variables, $rules) =
      file_contents_internal (1, "$libdir/am/$basename.am", %transform);
    return "$comments$variables$rules";
}


# $REGEXP
# &transform (%PAIRS)
# -------------------
# Foreach ($TOKEN, $VAL) in %PAIRS produce a replacement expression suitable
# for file_contents which:
#   - replaces %$TOKEN% with $VAL,
#   - enables/disables ?$TOKEN? and ?!$TOKEN?,
#   - replaces %?$TOKEN% with TRUE or FALSE.
sub transform (%)
{
    my (%pairs) = @_;
    my $result = '';

    while (my ($token, $val) = each %pairs)
    {
        $result .= "s/\Q%$token%\E/\Q$val\E/gm;";
    if ($val)
    {
        $result .= "s/\Q?$token?\E//gm;s/^.*\Q?!$token?\E.*\\n//gm;";
        $result .= "s/\Q%?$token%\E/TRUE/gm;";
    }
    else
    {
        $result .= "s/\Q?!$token?\E//gm;s/^.*\Q?$token?\E.*\\n//gm;";
        $result .= "s/\Q%?$token%\E/FALSE/gm;";
    }
    }

    return $result;
}


# &append_exeext ($MACRO)
# -----------------------
# Macro is an Automake magic macro which primary is PROGRAMS, e.g.
# bin_PROGRAMS.  Make sure these programs have $(EXEEXT) appended.
sub append_exeext ($)
{
  my ($macro) = @_;

  prog_error "append_exeext ($macro)"
    unless $macro =~ /_PROGRAMS$/;

  my @conds = variable_conditions_recursive ($macro);

  my @condvals;
  foreach my $cond (@conds)
    {
      my @one_binlist = ();
      my @condval = variable_value_as_list_recursive ($macro, $cond);
      foreach my $rcurs (@condval)
    {
      # Skip autoconf substs.  Also skip if the user
      # already applied $(EXEEXT).
      if ($rcurs =~ /^\@.*\@$/ || $rcurs =~ /\$\(EXEEXT\)$/)
        {
          push (@one_binlist, $rcurs);
        }
      else
        {
          push (@one_binlist, $rcurs . '$(EXEEXT)');
        }
    }

      push (@condvals, $cond);
      push (@condvals, "@one_binlist");
    }

  macro_delete ($macro);
  while (@condvals)
    {
      my $cond = shift (@condvals);
      my @val = split (' ', shift (@condvals));
      define_pretty_variable ($macro, $cond, @val);
    }
 }


# @PREFIX
# &am_primary_prefixes ($PRIMARY, $CAN_DIST, @PREFIXES)
# -----------------------------------------------------
# Find all variable prefixes that are used for install directories.  A
# prefix `zar' qualifies iff:
#
# * `zardir' is a variable.
# * `zar_PRIMARY' is a variable.
#
# As a side effect, it looks for misspellings.  It is an error to have
# a variable ending in a "reserved" suffix whose prefix is unknown, eg
# "bni_PROGRAMS".  However, unusual prefixes are allowed if a variable
# of the same name (with "dir" appended) exists.  For instance, if the
# variable "zardir" is defined, then "zar_PROGRAMS" becomes valid.
# This is to provide a little extra flexibility in those cases which
# need it.
sub am_primary_prefixes ($$@)
{
    my ($primary, $can_dist, @prefixes) = @_;

    local $_;
    my %valid = map { $_ => 0 } @prefixes;
    $valid{'EXTRA'} = 0;
    foreach my $varname (keys %var_value)
    {
        # Automake is allowed to define variables that look like they
        # are magic variables, such as INSTALL_DATA.
        next
      if $var_is_am{$varname};

    if ($varname =~ /^(nobase_)?(dist_|nodist_)?(.*)_$primary$/)
    {
        my ($base, $dist, $X) = ($1 || '', $2 || '', $3 || '');
        if ($dist ne '' && ! $can_dist)
            {
        # Note that a configure variable is always legitimate.
        # It is natural to name such variables after the
        # primary, so we explicitly allow it.
        macro_error ($varname,
                "invalid variable `$varname': `dist' is forbidden")
          if ! exists $configure_vars{$varname};
        }
        # A not-explicitely-allowed prefix X is allowed if Xdir
        # has been defined and X is not a standard prefix.
        elsif (! defined $valid{$X} && (! variable_defined ("${X}dir")
                        || exists $standard_prefix{$X}))
        {
        # Note that a configure variable is always legitimate.
        # It is natural to name such variables after the
        # primary, so we explicitly allow it.
            macro_error ($varname, "invalid variable `$varname'")
          if ! exists $configure_vars{$varname};
        }
        else
        {
        # Ensure all extended prefixes are actually used.
        $valid{"$base$dist$X"} = 1;
        }
    }
    }

    # Return only those which are actually defined.
    return sort grep { variable_defined ($_ . '_' . $primary) } keys %valid;
}


# Handle `where_HOW' variable magic.  Does all lookups, generates
# install code, and possibly generates code to define the primary
# variable.  The first argument is the name of the .am file to munge,
# the second argument is the primary variable (eg HEADERS), and all
# subsequent arguments are possible installation locations.  Returns
# list of all values of all _HOW targets.
#
# FIXME: this should be rewritten to be cleaner.  It should be broken
# up into multiple functions.
#
# Usage is: am_install_var (OPTION..., file, HOW, where...)
sub am_install_var
{
    my (@args) = @_;

    my $do_require = 1;
    my $can_dist = 0;
    my $default_dist = 0;
    while (@args)
    {
    if ($args[0] eq '-noextra')
    {
        $do_require = 0;
    }
    elsif ($args[0] eq '-candist')
    {
        $can_dist = 1;
    }
    elsif ($args[0] eq '-defaultdist')
    {
        $default_dist = 1;
        $can_dist = 1;
    }
    elsif ($args[0] !~ /^-/)
    {
        last;
    }
    shift (@args);
    }

    my ($file, $primary, @prefix) = @args;

    # Now that configure substitutions are allowed in where_HOW
    # variables, it is an error to actually define the primary.  We
    # allow `JAVA', as it is customarily used to mean the Java
    # interpreter.  This is but one of several Java hacks.  Similarly,
    # `PYTHON' is customarily used to mean the Python interpreter.
    macro_error ($primary, "`$primary' is an anachronism")
    if variable_defined ($primary)
        && ($primary ne 'JAVA' && $primary ne 'PYTHON');


    # Get the prefixes which are valid and actually used.
    @prefix = am_primary_prefixes ($primary, $can_dist, @prefix);

    # If a primary includes a configure substitution, then the EXTRA_
    # form is required.  Otherwise we can't properly do our job.
    my $require_extra;
    my $warned_about_extra = 0;

    my @used = ();
    my @result = ();

    # True if the iteration is the first one.  Used for instance to
    # output parts of the associated file only once.
    my $first = 1;
    foreach my $X (@prefix)
    {
    my $nodir_name = $X;
    my $one_name = $X . '_' . $primary;

    my $strip_subdir = 1;
    # If subdir prefix should be preserved, do so.
    if ($nodir_name =~ /^nobase_/)
      {
        $strip_subdir = 0;
        $nodir_name =~ s/^nobase_//;
      }

    # If files should be distributed, do so.
    my $dist_p = 0;
    if ($can_dist)
      {
        $dist_p = (($default_dist && $nodir_name !~ /^nodist_/)
               || (! $default_dist && $nodir_name =~ /^dist_/));
        $nodir_name =~ s/^(dist|nodist)_//;
      }

    # Append actual contents of where_PRIMARY variable to
    # result.
    foreach my $rcurs (&variable_value_as_list_recursive ($one_name, 'all'))
      {
        # Skip configure substitutions.  Possibly bogus.
        if ($rcurs =~ /^\@.*\@$/)
          {
        if ($nodir_name eq 'EXTRA')
          {
            if (! $warned_about_extra)
              {
            $warned_about_extra = 1;
            macro_error ($one_name,
                     "`$one_name' contains configure substitution, but shouldn't");
              }
          }
        # Check here to make sure variables defined in
        # configure.ac do not imply that EXTRA_PRIMARY
        # must be defined.
        elsif (! defined $configure_vars{$one_name})
          {
            $require_extra = $one_name
              if $do_require;
          }

        next;
          }

        push (@result, $rcurs);
      }

    # A blatant hack: we rewrite each _PROGRAMS primary to include
    # EXEEXT.
    append_exeext ($one_name)
      if $primary eq 'PROGRAMS';

    # "EXTRA" shouldn't be used when generating clean targets,
    # all, or install targets.  We used to warn if EXTRA_FOO was
    # defined uselessly, but this was annoying.
    next
      if $nodir_name eq 'EXTRA';

    if ($nodir_name eq 'check')
      {
        push (@check, '$(' . $one_name . ')');
      }
    else
      {
        push (@used, '$(' . $one_name . ')');
      }

    # Is this to be installed?
    my $install_p = $nodir_name ne 'noinst' && $nodir_name ne 'check';

    # If so, with install-exec? (or install-data?).
    my $exec_p = ($nodir_name =~ /$EXEC_DIR_PATTERN/o);

    # Singular form of $PRIMARY.
    (my $one_primary = $primary) =~ s/S$//;
    $output_rules .= &file_contents ($file,
                     ('FIRST' => $first,

                      'PRIMARY'     => $primary,
                      'ONE_PRIMARY' => $one_primary,
                      'DIR'         => $X,
                      'NDIR'        => $nodir_name,
                      'BASE'        => $strip_subdir,

                      'EXEC'    => $exec_p,
                      'INSTALL' => $install_p,
                      'DIST'    => $dist_p));

    $first = 0;
    }

    # The JAVA variable is used as the name of the Java interpreter.
    # The PYTHON variable is used as the name of the Python interpreter.
    if (@used && $primary ne 'JAVA' && $primary ne 'PYTHON')
    {
    # Define it.
    define_pretty_variable ($primary, '', @used);
    $output_vars .= "\n";
    }

    if ($require_extra && ! variable_defined ('EXTRA_' . $primary))
    {
    macro_error ($require_extra,
             "`$require_extra' contains configure substitution, but `EXTRA_$primary' not defined");
    }

    # Push here because PRIMARY might be configure time determined.
    push (@all, '$(' . $primary . ')')
    if @used && $primary ne 'JAVA' && $primary ne 'PYTHON';

    # Make the result unique.  This lets the user use conditionals in
    # a natural way, but still lets us program lazily -- we don't have
    # to worry about handling a particular object more than once.
    return uniq (sort @result);
}


################################################################

# Each key in this hash is the name of a directory holding a
# Makefile.in.  These variables are local to `is_make_dir'.
my %make_dirs = ();
my $make_dirs_set = 0;

sub is_make_dir
{
    my ($dir) = @_;
    if (! $make_dirs_set)
    {
    foreach my $iter (@configure_input_files)
    {
        $make_dirs{dirname ($iter)} = 1;
    }
    # We also want to notice Makefile.in's.
    foreach my $iter (@other_input_files)
    {
        if ($iter =~ /Makefile\.in$/)
        {
        $make_dirs{dirname ($iter)} = 1;
        }
    }
    $make_dirs_set = 1;
    }
    return defined $make_dirs{$dir};
}

################################################################

# This variable is local to the "require file" set of functions.
my @require_file_paths = ();


# &maybe_push_required_file ($DIR, $FILE, $FULLFILE)
# --------------------------------------------------
# See if we want to push this file onto dist_common.  This function
# encodes the rules for deciding when to do so.
sub maybe_push_required_file
{
    my ($dir, $file, $fullfile) = @_;

    if ($dir eq $relative_dir)
    {
    push_dist_common ($file);
    return 1;
    }
    elsif ($relative_dir eq '.' && ! &is_make_dir ($dir))
    {
    # If we are doing the topmost directory, and the file is in a
    # subdir which does not have a Makefile, then we distribute it
    # here.
    push_dist_common ($fullfile);
    return 1;
    }
    return 0;
}


# &require_file_internal ($WHERE, $MYSTRICT, @FILES)
# --------------------------------------------------
# Verify that the file must exist in the current directory.
# $MYSTRICT is the strictness level at which this file becomes required.
#
# Must set require_file_paths before calling this function.
# require_file_paths is set to hold a single directory (the one in
# which the first file was found) before return.
sub require_file_internal ($$@)
{
    my ($where, $mystrict, @files) = @_;

    foreach my $file (@files)
    {
        my $fullfile;
    my $errdir;
    my $errfile;
    my $save_dir;

    my $found_it = 0;
    my $dangling_sym = 0;
    foreach my $dir (@require_file_paths)
    {
        $fullfile = $dir . "/" . $file;
        $errdir = $dir unless $errdir;

        # Use different name for "error filename".  Otherwise on
        # an error the bad file will be reported as eg
        # `../../install-sh' when using the default
        # config_aux_path.
        $errfile = $errdir . '/' . $file;

        if (-l $fullfile && ! -f $fullfile)
        {
        $dangling_sym = 1;
        last;
        }
        elsif (-f $fullfile)
        {
        $found_it = 1;
        maybe_push_required_file ($dir, $file, $fullfile);
        $save_dir = $dir;
        last;
        }
    }

    # `--force-missing' only has an effect if `--add-missing' is
    # specified.
    if ($found_it && (! $add_missing || ! $force_missing))
    {
        # Prune the path list.
        @require_file_paths = $save_dir;
    }
    else
    {
        # If we've already looked for it, we're done.  You might
        # wonder why we don't do this before searching for the
        # file.  If we do that, then something like
        # AC_OUTPUT(subdir/foo foo) will fail to put foo.in into
        # DIST_COMMON.
        if (! $found_it)
        {
        next if defined $require_file_found{$fullfile};
        $require_file_found{$fullfile} = 1;
        }

        if ($strictness >= $mystrict)
        {
        if ($dangling_sym && $add_missing)
        {
            unlink ($fullfile);
        }

        my $trailer = '';
        my $suppress = 0;

        # Only install missing files according to our desired
        # strictness level.
        my $message = "required file `$errfile' not found";
        if ($add_missing)
        {
            $suppress = 1;

            if (-f ("$libdir/$file"))
            {
            # Install the missing file.  Symlink if we
            # can, copy if we must.  Note: delete the file
            # first, in case it is a dangling symlink.
            $message = "installing `$errfile'";
            # Windows Perl will hang if we try to delete a
            # file that doesn't exist.
            unlink ($errfile) if -f $errfile;
            if ($symlink_exists && ! $copy_missing)
            {
                if (! symlink ("$libdir/$file", $errfile))
                {
                $suppress = 0;
                $trailer = "; error while making link: $!";
                }
            }
            elsif (system ('cp', "$libdir/$file", $errfile))
            {
                $suppress = 0;
                $trailer = "\n    error while copying";
            }
            }

            if (! maybe_push_required_file (dirname ($errfile),
                                                    $file, $errfile))
            {
            if (! $found_it)
            {
                # We have added the file but could not push it
                # into DIST_COMMON (probably because this is
                # an auxiliary file and we are not processing
                # the top level Makefile). This is unfortunate,
                # since it means we are using a file which is not
                # distributed!

                # Get Automake to be run again: on the second
                # run the file will be found, and pushed into
                # the toplevel DIST_COMMON automatically.
                $automake_needs_to_reprocess_all_files = 1;
            }
            }

            # Prune the path list.
            @require_file_paths = &dirname ($errfile);
        }

        # If --force-missing was specified, and we have
        # actually found the file, then do nothing.
        next
            if $found_it && $force_missing;

        if ($suppress)
        {
          file_warning ($where, "$message$trailer");
        }
        else
        {
          file_error ($where, "$message$trailer");
        }
        }
    }
    }
}

# &require_file ($WHERE, $MYSTRICT, @FILES)
# -----------------------------------------
sub require_file ($$@)
{
    my ($where, $mystrict, @files) = @_;
    @require_file_paths = $relative_dir;
    require_file_internal ($where, $mystrict, @files);
}

# &require_file_with_macro ($MACRO, $MYSTRICT, @FILES)
# ----------------------------------------------------
sub require_file_with_macro ($$@)
{
    my ($macro, $mystrict, @files) = @_;
    require_file ($var_location{$macro}, $mystrict, @files);
}


# &require_conf_file ($WHERE, $MYSTRICT, @FILES)
# ----------------------------------------------
# Looks in configuration path, as specified by AC_CONFIG_AUX_DIR.
sub require_conf_file ($$@)
{
    my ($where, $mystrict, @files) = @_;
    @require_file_paths = @config_aux_path;
    require_file_internal ($where, $mystrict, @files);
    my $dir = $require_file_paths[0];
    @config_aux_path = @require_file_paths;
     # Avoid unsightly '/.'s.
    $config_aux_dir = '$(top_srcdir)' . ($dir eq '.' ? "" : "/$dir");
}


# &require_conf_file_with_macro ($MACRO, $MYSTRICT, @FILES)
# ---------------------------------------------------------
sub require_conf_file_with_macro ($$@)
{
    my ($macro, $mystrict, @files) = @_;
    require_conf_file ($var_location{$macro}, $mystrict, @files);
}

################################################################

# &require_build_directory ($DIRECTORY)
# ------------------------------------
# Emit rules to create $DIRECTORY if needed, and return
# the file that any target requiring this directory should be made
# dependent upon.
sub require_build_directory ($)
{
    my $directory = shift;
    my $dirstamp = "$directory/.dirstamp";

    # Don't emit the rule twice.
    if (! defined $directory_map{$directory})
    {
    $directory_map{$directory} = 1;

    # Directory must be removed by `make distclean'.
    $compile_clean_files{$dirstamp} = DIST_CLEAN;

    $output_rules .= ("$dirstamp:\n"
              . "\t\@\$(mkinstalldirs) $directory\n"
              . "\t\@: > $dirstamp\n");
    }

    return $dirstamp;
}

# &require_build_directory_maybe ($FILE)
# --------------------------------------
# If $FILE lies in a subdirectory, emit a rule to create this
# directory and return the file that $FILE should be made
# dependent upon.  Otherwise, just return the empty string.
sub require_build_directory_maybe ($)
{
    my $file = shift;
    my $directory = dirname ($file);

    if ($directory ne '.')
    {
    return require_build_directory ($directory);
    }
    else
    {
    return '';
    }
}

################################################################

# Push a list of files onto dist_common.
sub push_dist_common
{
    prog_error ("push_dist_common run after handle_dist")
        if $handle_dist_run;
    macro_define ('DIST_COMMON', 1, '+', '', "@_", '');
}


# Set strictness.
sub set_strictness
{
    $strictness_name = $_[0];
    if ($strictness_name eq 'gnu')
    {
    $strictness = GNU;
    }
    elsif ($strictness_name eq 'gnits')
    {
    $strictness = GNITS;
    }
    elsif ($strictness_name eq 'foreign')
    {
    $strictness = FOREIGN;
    }
    else
    {
    die "$me: level `$strictness_name' not recognized\n";
    }
}


################################################################

# Glob something.  Do this to avoid indentation screwups everywhere we
# want to glob.  Gross!
sub my_glob
{
    my ($pat) = @_;
    return <${pat}>;
}

# Remove one level of brackets and strip leading spaces,
# as does m4 to function arguments.
sub unquote_m4_arg
{
    $_ = shift;
    s/^\s*//;

    my @letters = split //;
    my @result = ();
    my $depth = 0;

    foreach (@letters)
    {
    if ($_ eq '[')
    {
        ++$depth;
        next if $depth == 1;
    }
    elsif ($_ eq ']')
    {
        --$depth;
        next if $depth == 0;
        # don't count orphan right brackets
        $depth = 0 if $depth < 0;
    }
    push @result, $_;
    }
    return join '', @result;
}

################################################################

# print_error ($LEADER, @ARGS)
# ----------------------------
# Do the work of printing the error message.  Join @ARGS with spaces,
# then split at newlines and add $LEADER to each line.  Uses `warn' to
# print message.  Set exit status.
sub print_error
{
    my ($leader, @args) = @_;
    my $text = "@args";
    @args = split ("\n", $text);
    $text = $leader . join ("\n" . $leader, @args) . "\n";
    warn $text;
    $exit_status = 1;
}


# Print an error message and set exit status.
sub am_error (@)
{
    print_error ("$me: ${am_file}.am: ", @_);
}


# &file_error ($FILE, @ARGS)
# --------------------------
sub file_error ($@)
{
    my ($file, @args) = @_;
    print_error ("$file: ", @args);
}


# &macro_error ($MACRO, @ARGS)
# ----------------------------
# Report an error, @ARGS, about $MACRO.
sub macro_error ($@)
{
    my ($macro, @args) = @_;
    file_error ($var_location{$macro}, @args);
}


# &target_error ($TARGET, @ARGS)
# ------------------------------
# Report an error, @ARGS, about the rule $TARGET.
sub target_error ($@)
{
    my ($target, @args) = @_;
    file_error ($targets{$target}, @args);
}


# Like am_error, but while scanning configure.ac.
sub conf_error
{
    # FIXME: can run in subdirs.
    print_error ("$me: $configure_ac: ", @_);
}

# &file_warning ($FILE, @ARGS)
# ----------------------------
# Warning message with line number referring to configure.ac.
# Does not affect exit_status
sub file_warning ($@)
{
    my ($file, @args) = @_;

    my $saved_exit_status = $exit_status;
    my $sig = $SIG{'__WARN__'};
    $SIG{'__WARN__'} = 'DEFAULT';
    file_error ($file, @args);
    $exit_status = $saved_exit_status;
    $SIG{'__WARN__'} = $sig;
}

# Tell user where our aclocal.m4 is, but only once.
sub keyed_aclocal_warning ($)
{
    my ($key) = @_;
    warn "$me: macro `$key' can be generated by `aclocal'\n";
}

# Print usage information.
sub usage ()
{
    print <<EOF;
Usage: $0 [OPTION] ... [Makefile]...

Generate Makefile.in for configure from Makefile.am.

Operation modes:
      --help             print this help, then exit
      --version          print version number, then exit
  -v, --verbose          verbosely list files processed
      --no-force         only update Makefile.in's that are out of date

Dependency tracking:
  -i, --ignore-deps      disable dependency tracking code
      --include-deps     enable dependency tracking code

Flavors:
      --cygnus           assume program is part of Cygnus-style tree
      --foreign          set strictness to foreign
      --gnits            set strictness to gnits
      --gnu              set strictness to gnu

Library files:
  -a, --add-missing      add missing standard files to package
      --libdir=DIR       directory storing library files
  -c, --copy             with -a, copy missing files (default is symlink)
  -f, --force-missing    force update of standard files
EOF

    my ($last, @lcomm);
    $last = '';
    foreach my $iter (sort ((@common_files, @common_sometimes)))
    {
    push (@lcomm, $iter) unless $iter eq $last;
    $last = $iter;
    }

    my @four;
    print "\nFiles which are automatically distributed, if found:\n";
    format USAGE_FORMAT =
  @<<<<<<<<<<<<<<<<   @<<<<<<<<<<<<<<<<   @<<<<<<<<<<<<<<<<   @<<<<<<<<<<<<<<<<
  $four[0],           $four[1],           $four[2],           $four[3]
.
    $~ = "USAGE_FORMAT";

    my $cols = 4;
    my $rows = int(@lcomm / $cols);
    my $rest = @lcomm % $cols;

    if ($rest)
    {
    $rows++;
    }
    else
    {
    $rest = $cols;
    }

    for (my $y = 0; $y < $rows; $y++)
    {
    @four = ("", "", "", "");
    for (my $x = 0; $x < $cols; $x++)
    {
        last if $y + 1 == $rows && $x == $rest;

        my $idx = (($x > $rest)
               ?  ($rows * $rest + ($rows - 1) * ($x - $rest))
               : ($rows * $x));

        $idx += $y;
        $four[$x] = $lcomm[$idx];
    }
    write;
    }

    print "\nReport bugs to <bug-automake\@gnu.org>.\n";

    exit 0;
}


# &version ()
# -----------
# Print version information
sub version ()
{
  print <<EOF;
automake (GNU $PACKAGE) $VERSION
Written by Tom Tromey <tromey\@redhat.com>.

Copyright 2002 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
EOF
  exit 0;
}
