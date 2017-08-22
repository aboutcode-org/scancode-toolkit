#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import ctypes
import os
import logging
import signal
import subprocess
import sys

from commoncode import fileutils
from commoncode import text
from commoncode import system
from commoncode.system import current_os_arch
from commoncode.system import current_os_noarch
from commoncode.system import noarch
from commoncode.system import on_windows


"""
Minimal wrapper for executing external commands in sub-processes. The approach
is unconventionally relying on vendoring scripts or pre-built executable
binary command rather than relying on OS-provided binaries.

While this could seem contrived at first this approach ensures that:
 - a distributed scancode package is self-contained
 - a non technical user does not have any extra installation to do, in
   particular there is no compilation needed at installation time.
 - we have few dependencies on the OS.
 - we control closely the version of these executables and how they were
   built to ensure sanity, especially on Linux where several different
   (oftentimes older) version may exist in the path for a given distro.
   For instance this applies to tools such as 7z, binutils and file.
"""

logger = logging.getLogger(__name__)
# import sys
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# logger.setLevel(logging.DEBUG)

# current directory is the root dir of this library
curr_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def execute(cmd, args, root_dir=None, cwd=None, env=None, to_files=False):
    """
    Run a `cmd` external command with the `args` arguments list and return the
    return code, the stdout and stderr.

    To avoid RAM exhaustion, always write stdout and stderr streams to files.

    If `to_files` is False, return the content of stderr and stdout as ASCII
    strings. Otherwise, return the locations to the stderr and stdout
    temporary files.

    Resolve the `cmd` location using os/arch local/vendored location based on
    using `root_dir`. No resolution is done if root_dir is None

    Run the command using the `cwd` current working directory with an
    `env` dict of environment variables.
    """
    assert cmd
    cmd_loc, bin_dir, lib_dir = get_locations(cmd, root_dir)
    full_cmd = [cmd_loc or cmd] + args or []
    env = get_env(env, lib_dir) or None
    cwd = cwd or curr_dir

    # temp files for stderr and stdout
    tmp_dir = fileutils.get_temp_dir(base_dir='cmd')
    sop = os.path.join(tmp_dir, 'stdout')
    sep = os.path.join(tmp_dir, 'stderr')

    # shell==True is DANGEROUS but we are not running arbitrary commands
    # though we can execute command that just happen to be in the path
    shell = True if on_windows else False

    logger.debug('Executing command %(cmd)r as %(full_cmd)r with: env=%(env)r, '
                 'shell=%(shell)r, cwd=%(cwd)r, stdout=%(sop)r, stderr=%(sep)r.'
                 % locals())

    proc = None
    try:
        with open(sop, 'wb') as stdout, open(sep, 'wb') as stderr:
            # -1 defaults bufsize to system bufsize
            pargs = dict(cwd=cwd, env=env, stdout=stdout, stderr=stderr,
                         shell=shell, bufsize=-1, universal_newlines=True)
            proc = subprocess.Popen(full_cmd, **pargs)
            stdout, stderr = proc.communicate()
            rc = proc.returncode if proc else 0
    finally:
        close(proc)

    if not to_files:
        # return output as ASCII string loaded from the output files
        sop = text.toascii(open(sop, 'rb').read().strip())
        sep = text.toascii(open(sep, 'rb').read().strip())
    return rc, sop, sep


def os_arch_dir(root_dir, _os_arch=current_os_arch):
    """
    Return a sub-directory of `root_dir` tailored for the current OS and
    current processor architecture.
    """
    return os.path.join(root_dir, _os_arch)


def os_noarch_dir(root_dir, _os_noarch=current_os_noarch):
    """
    Return a sub-directory of `root_dir` tailored for the current OS and NOT
    specific to a processor architecture.
    """
    return os.path.join(root_dir, _os_noarch)


def noarch_dir(root_dir, _noarch=noarch):
    """
    Return a sub-directory of `root_dir` that is NOT specific to an OS or
    processor architecture.
    """
    return os.path.join(root_dir, _noarch)


def get_base_dirs(root_dir,
                  _os_arch=current_os_arch,
                  _os_noarch=current_os_noarch,
                  _noarch=noarch):
    """
    Return a sequence of existing directories relative to a `root_dir`. Each
    returned directory is an existing local/vendored directory location
    ordered from the most operating system and processor architecture specific
    to the least specific:

    - 1. <root_dir>/<os>-<arch>: a dir specific to the OS and arch.
    - 2. <root_dir>/<os>-noarch: a dir specific to the OS for any arch.
    - 3. <root_dir>/noarch: a dir for any OS and any arch

    Return an empty sequence if no local/vendored directory was found.

    Rationale: Pre-built executable command binaries are typically stored for
    convenience side-by-side with code that calls them.  We support multiple
    OSes and architectures and therefore have multiple vendored pre-built
    binary  of any given binary. This function resolves to an actual OS/arch
    location in this context.
    """
    if not root_dir or not os.path.exists(root_dir):
        return []

    dirs = []

    def find_loc(fun, arg):
        loc = fun(root_dir, arg)
        if os.path.exists(loc):
            dirs.append(loc)

    if _os_arch:
        find_loc(os_arch_dir, _os_arch)
    if _os_noarch:
        find_loc(os_noarch_dir, _os_noarch)
    if _noarch:
        find_loc(noarch_dir, _noarch)

    return dirs


def get_bin_lib_dirs(base_dir):
    """
    Return a tuple of bin and lib sub-directories of a `base_dir`. bin and lib
    directories are None if they do not exist.

    On POSIX, all files in these directories are made executable.
    The lib dir defaults to bin dir if lib did is not present.
    """

    if not base_dir:
        return None, None

    bin_dir = os.path.join(base_dir, 'bin')

    if os.path.exists(bin_dir):
        fileutils.chmod(bin_dir, fileutils.RX, recurse=True)
    else:
        bin_dir = None

    lib_dir = os.path.join(base_dir, 'lib')

    if os.path.exists(lib_dir):
        fileutils.chmod(bin_dir, fileutils.RX, recurse=True)
    else:
        # default to bin for lib if it exists
        lib_dir = bin_dir or None

    return bin_dir, lib_dir


def get_env(base_vars=None, lib_dir=None):
    """
    Return a dictionary of environment variables for command execution with
    appropriate LD paths. Use the optional `base_vars` environment variables
    dictionary as a base if provided. Note: if `base_vars`  contains LD
    variables these will be overwritten.
    """
    env_vars = {}
    if base_vars:
        env_vars.update(base_vars)

    # Create and add LD environment variables
    if lib_dir:
        path_var = '%(lib_dir)s' % locals()
        # on Linux/posix
        env_vars['LD_LIBRARY_PATH'] = path_var
        # on Mac
        env_vars['DYLD_LIBRARY_PATH'] = path_var

    # ensure that we use bytes, not unicode
    def to_bytes(s):
        return s if isinstance(s, bytes) else s.encode('utf-8')

    env_vars = {to_bytes(k): to_bytes(v) for k, v in env_vars.items()}
    return env_vars


def get_locations(cmd, root_dir,
                  _os_arch=current_os_arch,
                  _os_noarch=current_os_noarch,
                  _noarch=noarch,
                  must_exist=True):
    """
    Return a tuple of (cmd_loc, bin_dir, lib_dir), where `cmd_loc` is the
    location of an  `cmd` external command, bin_dir and lib_dir are the
    corresponding bin and lib directories. `root_dir` is used to resolve where
    a local/vendored executable `cmd` is stored. Return a tuple of None if no
    local/vendored executable was found or no `root_dir` was provided or
    found.
    If `must_exist` is False, the existence of the cmd is not performed.
    In this case the first existing bin and lib dirs will be returned.

    On POSIX, the command file is made executable when found locally.
    On Windows, an '.exe' extension is added to `cmd`.
    """
    cmd_loc = bin_dir = lib_dir = None
    if not root_dir:
        return cmd_loc, bin_dir, lib_dir

    if must_exist:
        # we do not use on_windows here to support cross OS testing
        if any(x and 'win' in x for x in (_os_arch, _os_noarch, _noarch)):
            cmd = cmd + '.exe'

        for base_dir in get_base_dirs(root_dir, _os_arch, _os_noarch, _noarch):
            bin_dir, lib_dir = get_bin_lib_dirs(base_dir)
            cmd_loc = os.path.join(bin_dir, cmd)
            if os.path.exists(cmd_loc):
                fileutils.chmod(cmd_loc, fileutils.RX, recurse=False)
                return cmd_loc, bin_dir, lib_dir
    else:
        # we just care for getting the dirs and grab the first one
        for base_dir in get_base_dirs(root_dir, _os_arch, _os_noarch, _noarch):
            bin_dir, lib_dir = get_bin_lib_dirs(base_dir)
            return None, bin_dir, lib_dir

    return None, None, None


def close(proc):
    """
    Close a `proc` process opened pipes and kill the process.
    """
    if not proc:
        return

    def close_pipe(p):
        if not p:
            return
        try:
            p.close()
        except IOError:
            pass

    close_pipe(getattr(proc, 'stdin', None))
    close_pipe(getattr(proc, 'stdout', None))
    close_pipe(getattr(proc, 'stderr', None))

    try:
        # Ensure process death otherwise proc.wait may hang in some cases
        # NB: this will run only on POSIX OSes supporting signals
        os.kill(proc.pid, signal.SIGKILL)  # @UndefinedVariable
    except:
        pass

    # This may slow things down a tad on non-POSIX Oses but is safe:
    # this calls os.waitpid() to make sure the process is dead
    proc.wait()


def load_lib(libname, root_dir):
    """
    Return the loaded `libname` shared library object from vendored paths.
    """
    os_dir = get_base_dirs(root_dir)[0]
    _bin_dir, lib_dir = get_bin_lib_dirs(os_dir)
    so = os.path.join(lib_dir, libname + system.lib_ext)

    # add lib path to the front of the PATH env var
    new_path = os.pathsep.join([lib_dir, os.environ['PATH']])
    os.environ['PATH'] = new_path

    if os.path.exists(so):
        if not isinstance(so, bytes):
            # ensure that the path is not Unicode...
            so = so.encode(sys.getfilesystemencoding() or sys.getdefaultencoding())
        lib = ctypes.CDLL(so)
        if lib and lib._name:
            return lib
    raise ImportError('Failed to load %(libname)s from %(so)r' % locals())
