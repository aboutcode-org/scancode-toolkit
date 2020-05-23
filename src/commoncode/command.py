#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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
import contextlib
import io
import os
from os import path

import logging
import signal
import subprocess

from commoncode import compat
from commoncode.fileutils import EMPTY_STRING
from commoncode.fileutils import PATH_ENV_VAR
from commoncode.fileutils import PATH_ENV_SEP
from commoncode.fileutils import fsdecode
from commoncode.fileutils import fsencode
from commoncode.fileutils import get_temp_dir
from commoncode.system import on_linux
from commoncode.system import on_posix
from commoncode.system import on_windows
from commoncode.system import py2
from commoncode.system import py3
from commoncode import text


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

TRACE = False

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


# current directory is the root dir of this library
curr_dir = path.dirname(path.dirname(path.abspath(__file__)))


if py2:
    PATH_ENV_VAR = b'PATH'
    LD_LIBRARY_PATH = b'LD_LIBRARY_PATH'
    DYLD_LIBRARY_PATH = b'DYLD_LIBRARY_PATH'
else:
    PATH_ENV_VAR = 'PATH'
    LD_LIBRARY_PATH = 'LD_LIBRARY_PATH'
    DYLD_LIBRARY_PATH = 'DYLD_LIBRARY_PATH'


def execute2(cmd_loc, args, lib_dir=None, cwd=None, env=None, to_files=False, log=TRACE):
    """
    Run a `cmd_loc` command with the `args` arguments list and return the return
    code, the stdout and stderr.

    To avoid RAM exhaustion, always write stdout and stderr streams to files.

    If `to_files` is False, return the content of stderr and stdout as ASCII
    strings. Otherwise, return the locations to the stderr and stdout
    temporary files.

    Run the command using the `cwd` current working directory with an
    `env` dict of environment variables.
    """
    assert cmd_loc
    full_cmd = [cmd_loc] + (args or [])

    env = get_env(env, lib_dir) or None
    cwd = cwd or curr_dir

    # temp files for stderr and stdout
    tmp_dir = get_temp_dir(prefix='cmd-')

    if on_linux and py2:
        stdout = b'stdout'
        stderr = b'stderr'
    else:
        stdout = 'stdout'
        stderr = 'stderr'

    sop = path.join(tmp_dir, stdout)
    sep = path.join(tmp_dir, stderr)

    # shell==True is DANGEROUS but we are not running arbitrary commands
    # though we can execute commands that just happen to be in the path
    shell = True if on_windows else False

    if log:
        printer = logger.debug if TRACE else lambda x: print(x)
        printer(
            'Executing command %(cmd_loc)r as:\n%(full_cmd)r\nwith: env=%(env)r\n'
            'shell=%(shell)r\ncwd=%(cwd)r\nstdout=%(sop)r\nstderr=%(sep)r'
            % locals())

    proc = None
    rc = 100

    if py2:
        okwargs = dict(mode='wb')
    if py3:
        okwargs = dict(mode='w', encoding='utf-8')

    try:
        with io.open(sop, **okwargs) as stdout, io.open(sep, **okwargs) as stderr:
            with pushd(lib_dir):
                popen_args = dict(
                    cwd=cwd,
                    env=env,
                    stdout=stdout,
                    stderr=stderr,
                    shell=shell,
                    # -1 defaults bufsize to system bufsize
                    bufsize=-1,
                    universal_newlines=True
                )

                proc = subprocess.Popen(full_cmd, **popen_args)
                stdout, stderr = proc.communicate()
                rc = proc.returncode if proc else 0

    finally:
        close(proc)

    if not to_files:
        # return output as ASCII string loaded from the output files
        sop = text.toascii(open(sop, 'rb').read().strip())
        sep = text.toascii(open(sep, 'rb').read().strip())
    return rc, sop, sep


def get_env(base_vars=None, lib_dir=None):
    """
    Return a dictionary of environment variables for command execution with
    appropriate LD paths. Use the optional `base_vars` environment variables
    dictionary as a base if provided. Note: if `base_vars`  contains LD
    variables these will be overwritten.
    Add `lib_dir` as a proper "LD_LIBRARY_PATH"-like path if provided.
    """
    env_vars = {}
    if base_vars:
        env_vars.update(base_vars)

    # Create and add LD environment variables
    if lib_dir and on_posix:
        new_path = '%(lib_dir)s' % locals()
        # on Linux/posix
        ld_lib_path = os.environ.get(LD_LIBRARY_PATH)
        env_vars.update(
            {LD_LIBRARY_PATH: update_path_var(ld_lib_path, new_path)})
        # on Mac, though LD_LIBRARY_PATH should work too
        dyld_lib_path = os.environ.get(DYLD_LIBRARY_PATH)
        env_vars.update(
            {DYLD_LIBRARY_PATH: update_path_var(dyld_lib_path, new_path)})

    if py2:
        # ensure that we use bytes on py2 and unicode on py3
        def to_bytes(s):
            return s if isinstance(s, bytes) else s.encode('utf-8')
        env_vars = {to_bytes(k): to_bytes(v) for k, v in env_vars.items()}
    else:
        env_vars = {text.as_unicode(k): text.as_unicode(v) for k, v in env_vars.items()}

    return env_vars


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
        os.kill(proc.pid, signal.SIGKILL)  # NOQA
    except:
        pass

    # This may slow things down a tad on non-POSIX Oses but is safe:
    # this calls os.waitpid() to make sure the process is dead
    proc.wait()


def load_shared_library(dll_path, lib_dir):
    """
    Return the loaded shared library object from the dll_path and adding `lib_dir` to the path.
    """

    if not path.exists(dll_path):
        raise ImportError('Shared library does not exists: %(dll_path)r' % locals())

    if lib_dir and not path.exists(lib_dir):
        raise ImportError('Shared library "lib_dir" does not exists: %(lib_dir)r' % locals())

    if on_linux and py2:
        # bytes only there ...
        if not isinstance(dll_path, bytes):
            dll_path = fsencode(dll_path)

    else:
        # ... unicode everywhere else
        if not isinstance(dll_path, compat.unicode):
            dll_path = fsdecode(dll_path)

    try:
        with pushd(lib_dir):
            lib = ctypes.CDLL(dll_path)
    except OSError as e:
        from pprint import pformat
        msgs = tuple([
            'ctypes.CDLL(dll_path): {}'.format(dll_path),
            'os.environ:\n{}'.format(pformat(dict(os.environ))),
        ])
        e.args = tuple(e.args + msgs)
        raise

    if lib and lib._name:
        return lib

    raise ImportError('Failed to load shared library with ctypes: %(dll_path)r and lib_dir:  %(lib_dir)r' % locals())


@contextlib.contextmanager
def pushd(path):
    """
    Context manager to change the current working directory to `path`.
    """
    original_cwd = os.getcwd()
    if not path:
        path = original_cwd
    try:
        os.chdir(path)
        yield os.getcwd()
    finally:
        os.chdir(original_cwd)


def update_path_var(existing_path_var, new_path, pathsep=PATH_ENV_SEP):
    """
    Return an updated value for the `existing_path_var` PATH-like environment
    variable value  by adding `new_path` to the front of that variable if
    `new_path` is not already part of this PATH-like variable.
    """
    if not new_path:
        return existing_path_var

    existing_path_var = existing_path_var or EMPTY_STRING

    # ensure we use unicode or bytes depending on OSes
    # TODO: deal also with Python versions
    if on_linux and py2:
        # bytes ...
        existing_path_var = fsencode(existing_path_var)
        new_path = fsencode(new_path)
        pathsep = fsencode(pathsep)
    else:
        # ... and unicode otherwise
        existing_path_var = fsdecode(existing_path_var)
        new_path = fsdecode(new_path)
        pathsep = fsdecode(pathsep)

    path_elements = existing_path_var.split(pathsep)

    if not path_elements:
        updated_path_var = new_path

    elif new_path not in path_elements:
        # add new path to the front of the PATH env var
        path_elements.insert(0, new_path)
        updated_path_var = pathsep.join(path_elements)

    else:
        # new path is already in PATH, change nothing
        updated_path_var = existing_path_var

    if py2:
        # always use bytes for env vars...
        if isinstance(updated_path_var, compat.unicode):
            updated_path_var = fsencode(updated_path_var)
    else:
        # ... else use unicode
        if not isinstance(updated_path_var, compat.unicode):
            updated_path_var = fsdecode(updated_path_var)

    # at this stage new_path_env is unicode on all OSes on Py3
    # and on Py2 it is bytes on Linux and unicode elsewhere
    return updated_path_var

