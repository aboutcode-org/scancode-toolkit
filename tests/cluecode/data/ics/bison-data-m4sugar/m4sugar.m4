# Base M4 layer.
# Requires GNU M4.
#
# Copyright (C) 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software
# Foundation, Inc.
#
#
# - BODY-TO-EXPAND == m4_indir([NAME-TO-CHECK])
#   In the case of macros with irregular names.  For instance:
#     m4_require([AC_LANG_COMPILER(C)], [indir([AC_LANG_COMPILER(C)])])
#   which means `if the macro named `AC_LANG_COMPILER(C)' (the parens are
#   part of the name, it is not an argument) has not been run, then
#   call it.'
#   Had you used
#     m4_require([AC_LANG_COMPILER(C)], [AC_LANG_COMPILER(C)])
#   then m4_require would have tried to expand `AC_LANG_COMPILER(C)', i.e.,
#   call the macro `AC_LANG_COMPILER' with `C' as argument.
#
#   You could argue that `AC_LANG_COMPILER', when it receives an argument
#   such as `C' should dispatch the call to `AC_LANG_COMPILER(C)'.  But this
#   `extension' prevents `AC_LANG_COMPILER' from having actual arguments that
#   it passes to `AC_LANG_COMPILER(C)'.
m4_define([m4_require],
[m4_ifdef([_m4_expanding($1)],