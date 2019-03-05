#!/usr/bin/env python
# Copyright (c) 2002-2005 ActiveState Corp.
# See LICENSE.txt for license details.
# Author:
#   Trent Mick (TrentM@ActiveState.com)
# Home:
#   http://trentm.com/projects/which/

r"""Find the full path to commands.

which(command, path=None, verbose=0, exts=None)
    Return the full path to the first match of the given command on the
    path.

whichall(command, path=None, verbose=0, exts=None)
    Return a list of full paths to all matches of the given command on
    the path.

whichgen(command, path=None, verbose=0, exts=None)
    Return a generator which will yield full paths to all matches of the
    given command on the path.
    
By default the PATH environment variable is searched (as well as, on
Windows, the AppPaths key in the registry), but a specific 'path' list
to search may be specified as well.  On Windows, the PATHEXT environment
variable is applied as appropriate.

If "verbose" is true then a tuple of the form
    (<fullpath>, <matched-where-description>)
is returned for each match. The latter element is a textual description
of where the match was found. For example:
    from PATH element 0
    from HKLM\SOFTWARE\...\perl.exe
"""

_cmdlnUsage = """
    Show the full path of commands.

    Usage:
        which [<options>...] [<command-name>...]

    Options:
        -h, --help      Print this help and exit.
        -V, --version   Print the version info and exit.

        -a, --all       Print *all* matching paths.
        -v, --verbose   Print out how matches were located and
                        show near misses on stderr.
        -q, --quiet     Just print out matches. I.e., do not print out
                        near misses.

        -p <altpath>, --path=<altpath>
                        An alternative path (list of directories) may
                        be specified for searching.
        -e <exts>, --exts=<exts>
                        Specify a list of extensions to consider instead
                        of the usual list (';'-separate list, Windows
                        only).

    Show the full path to the program that would be run for each given
    command name, if any. Which, like GNU's which, returns the number of
    failed arguments, or -1 when no <command-name> was given.

    Near misses include duplicates, non-regular files and (on Un*x)
    files without executable access.
"""

__revision__ = "$Id: which.py 430 2005-08-20 03:11:58Z trentm $"
__version_info__ = (1, 1, 0)
__version__ = '.'.join(map(str, __version_info__))

import os
import sys
import getopt
import stat


#---- exceptions

class WhichError(Exception):
    pass



#---- internal support stuff

def _getRegisteredExecutable(exeName):
    """Windows allow application paths to be registered in the registry."""
    registered = None
    if sys.platform.startswith('win'):
        if os.path.splitext(exeName)[1].lower() != '.exe':
            exeName += '.exe'
        import _winreg
        try:
            key = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\" +\
                  exeName
            value = _winreg.QueryValue(_winreg.HKEY_LOCAL_MACHINE, key)
            registered = (value, "from HKLM\\"+key)
        except _winreg.error:
            pass
        if registered and not os.path.exists(registered[0]):
            registered = None
    return registered

def _samefile(fname1, fname2):
    if sys.platform.startswith('win'):
        return ( os.path.normpath(os.path.normcase(fname1)) ==\
            os.path.normpath(os.path.normcase(fname2)) )
    else:
        return os.path.samefile(fname1, fname2)

def _cull(potential, matches, verbose=0):
    """Cull inappropriate matches. Possible reasons:
        - a duplicate of a previous match
        - not a disk file
        - not executable (non-Windows)
    If 'potential' is approved it is returned and added to 'matches'.
    Otherwise, None is returned.
    """
    for match in matches:  # don't yield duplicates
        if _samefile(potential[0], match[0]):
            if verbose:
                sys.stderr.write("duplicate: %s (%s)\n" % potential)
            return None
    else:
        if not stat.S_ISREG(os.stat(potential[0]).st_mode):
            if verbose:
                sys.stderr.write("not a regular file: %s (%s)\n" % potential)
        elif not os.access(potential[0], os.X_OK):
            if verbose:
                sys.stderr.write("no executable access: %s (%s)\n"\
                                 % potential)
        else:
            matches.append(potential)
            return potential

