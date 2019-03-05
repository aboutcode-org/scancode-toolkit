#!/bin/sh
#
# install - install a program, script, or datafile
# This comes from X11R5 (mit/util/scripts/install.sh).
#
# Copyright 1991 by the Massachusetts Institute of Technology
#
# Permission to use, copy, modify, distribute, and sell this software and its
# documentation for any purpose is hereby granted without fee, provided that
# the above copyright notice appear in all copies and that both that
# copyright notice and this permission notice appear in supporting
# documentation, and that the name of M.I.T. not be used in advertising or
# publicity pertaining to distribution of the software without specific,
# written prior permission.  M.I.T. makes no representations about the
# suitability of this software for any purpose.  It is provided "as is"
# without express or implied warranty.
#
# Calling this script install-sh is preferred over install.sh, to prevent
# `make' implicit rules from creating a file called install from it
# when there is no Makefile.
#
# This script is compatible with the BSD install script, but was written
# from scratch.  It can only install one file at a time, a restriction
# shared with many OS's install programs.
