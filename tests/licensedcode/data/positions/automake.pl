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

[.... code removed]


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
