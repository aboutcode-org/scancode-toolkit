#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import datetime
import errno
import os
import tempfile
from os.path import abspath
from os.path import dirname
from os.path import exists
from os.path import expanduser
from os.path import join

"""
Core configuration globals.

Note: this module MUST import ONLY from the standard library.
"""

# this exception is not available on POSIX
try:
    WindowsError  # NOQA
except NameError:

    class WindowsError(Exception):
        pass


def _create_dir(location):
    """
    Create directory and all sub-directories recursively at `location`.
    Raise Exceptions if it fails to create the directory.
    NOTE: this is essentailly a copy of commoncode.fileutils.create_dir()
    """

    if exists(location):
        if not os.path.isdir(location):
            err = ('Cannot create directory: existing file '
                   'in the way ''%(location)s.')
            raise OSError(err % locals())
        return

    # may fail on win if the path is too long
    # FIXME: consider using UNC ?\\ paths
    try:
        os.makedirs(location)

    # avoid multi-process TOCTOU conditions when creating dirs
    # the directory may have been created since the exist check
    except WindowsError as e:
        # [Error 183] Cannot create a file when that file already exists
        if e and e.winerror == 183:
            if not os.path.isdir(location):
                raise
        else:
            raise
    except (IOError, OSError) as o:
        if o.errno == errno.EEXIST:
            if not os.path.isdir(location):
                raise
        else:
            raise

################################################################################
# INVARIABLE INSTALLATION-SPECIFIC, BUILT-IN LOCATIONS AND FLAGS
################################################################################
# These are guaranteed to be there and are entirely based on and relative to the
# current installation location. This is where the source code and static data
# lives.


system_temp_dir = tempfile.gettempdir()
scancode_src_dir = dirname(__file__)
scancode_root_dir = dirname(scancode_src_dir)

# USAGE MODE FLAG. If we have a .git dir, we are a git clone and developing
_SCANCODE_DEV_MODE = os.path.exists(join(scancode_root_dir, '.git'))

# There are multiple cases for versions, depending on where we come from:
__version__ = ''

# 1. - a git clone: we can use git describe which take consider the closest tag
#   "git describe --dirty > SCANCODE_VERSION"
# This is the common case when we develop, including dump the latestlicense db
if _SCANCODE_DEV_MODE:

    from subprocess import check_output
    from subprocess import STDOUT
    from subprocess import CalledProcessError

    # this may fail with exceptions
    cmd = 'git', 'describe',
    try:
        output = check_output(cmd, stderr=STDOUT)
        __version__ = output.decode('utf-8').strip()
    except (Exception, CalledProcessError) as e:
        pass

# 2. - the scancode-tool binary or sources app archives: with a SCANCODE_VERSION
#   file containing the git tag of the release with "git describe --tags > SCANCODE_VERSION"
# - a tarball without an updated .VERSION, we cannot tell anything and we will use importlib metadata
# - a wheel or sdist in which case we use the importlib metadata
# we use importlib metadata in all these cases
if not __version__:
    try:
        from importlib_metadata import version
        __version__ = version('scancode-toolkit')
    except Exception:
        pass

# 3. - a tarball or zip archive from git with a .VERSION file with var substitution:
#   .VERSION will contain:
#      refs=HEAD -> fix-license-dump
#      commit=5ccc92e69cffb503e9bedc7fce5a1dbb0fd851da
#      abbrev_commit=5ccc92e69c
#      committer_date=2023-01-16
#      git_describe=v31.2.3-328-g5ccc92e69c
#    otherwise it contains:
#      refs=$Format:%D$
#      commit=$Format:%H$
#      abbrev_commit=$Format:%h$
#      committer_date=$Format:%cs$
#      git_describe=$Format:%(describe)$
# NOTE: we do not handle this for now

# 4. hardcoded This is the default, fallback version in case package is not installed or we
# do not have a proper version otherwise.
if not __version__:
    __version__ = '32.0.0rc1'

#######################
# used to warn user when the version is out of date
__release_date__ = datetime.datetime(2023, 1, 15)

# See https://github.com/nexB/scancode-toolkit/issues/2653 for more information
# on the data format version
__output_format_version__ = '3.0.0'

#
spdx_license_list_version = '3.19'

################################################################################
# USAGE MODE-, INSTALLATION- and IMPORT- and RUN-SPECIFIC DIRECTORIES
################################################################################
# These vary based on the usage mode: dev or not and based on environamnet
# variables

# - scancode_cache_dir: for long-lived caches which are installation-specific:
# this is for cached data which are infrequently written to and mostly readed,
# such as the license index cache. The same location is used across runs of
# a given version of ScanCode
"""
We set the path to an existing directory where ScanCode can cache files
available across runs from the value of the `SCANCODE_CACHE` environment
variable. If `SCANCODE_CACHE` is not set, a default sub-directory in the user
home directory is used instead.
"""
if _SCANCODE_DEV_MODE:
    # in dev mode the cache and temp files are stored exclusively under the
    # scancode_root_dir
    scancode_cache_dir = join(scancode_root_dir, '.cache')
else:
    # In other usage modes (as a CLI or as a library, regardless of how
    # installed) the cache dir goes to the home directory and is different for
    # each version
    user_home = abspath(expanduser('~'))
    __env_cache_dir = os.getenv('SCANCODE_CACHE')
    std_scancode_cache_dir = join(user_home, '.cache', 'scancode-tk', __version__)
    scancode_cache_dir = (__env_cache_dir or std_scancode_cache_dir)

# we pre-build the index and bundle this with the the deployed release
# therefore we use package data
# .... but we accept this to be overriden with and env variable
std_license_cache_dir = join(scancode_src_dir, 'licensedcode', 'data', 'cache')
__env_license_cache_dir = os.getenv('SCANCODE_LICENSE_INDEX_CACHE')
licensedcode_cache_dir = (__env_license_cache_dir or std_license_cache_dir)

_create_dir(licensedcode_cache_dir)
_create_dir(scancode_cache_dir)

# - scancode_temp_dir: for short-lived temporary files which are import- or run-
# specific that may live for the duration of a function call or for the duration
# of a whole scancode run, such as any temp file and the per-run scan results
# cache. A new unique location is used for each run of ScanCode (e.g. for the
# lifetime of the Python interpreter process)

"""
We set the path to an existing directory where ScanCode can create temporary
files from the value of the `SCANCODE_TMP` environment variable if available. If
`SCANCODE_TMP` is not set, a default sub-directory in the system temp directory
is used instead. Each scan run creates its own tempfile subdirectory.
"""
__scancode_temp_base_dir = os.getenv('SCANCODE_TEMP')

if not __scancode_temp_base_dir:
    if _SCANCODE_DEV_MODE:
        __scancode_temp_base_dir = join(scancode_root_dir, 'tmp')
    else:
        __scancode_temp_base_dir = system_temp_dir

_create_dir(__scancode_temp_base_dir)
_prefix = 'scancode-tk-' + __version__ + '-'
scancode_temp_dir = tempfile.mkdtemp(prefix=_prefix, dir=__scancode_temp_base_dir)

# Used for tests to regenerate fixtures with regen=True
REGEN_TEST_FIXTURES = os.getenv('SCANCODE_REGEN_TEST_FIXTURES', False)
