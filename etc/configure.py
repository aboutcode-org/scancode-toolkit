#!/usr/bin/python
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

"""
A configuration helper that wraps virtualenv and pip to configure an Python
isolated virtual environment and install requirement there with pip using
bundled packages from a third-party directory. It does some minimal checks on
supported OSes, architectures and Python versions.

To use, create requirements flies and use this way:

* to configure and install::

    ./configure.py [<pip requirement argument>, ...]

* to cleanup everything::

    ./configure.py --clean
"""

import os
import shutil
import subprocess
import sys


def unsupported(platform):
    print('Unsupported Python, OS, platform or architecture: {platform}'.format(platform=platform))
    print('See https://github.com/nexB/scancode-toolkit/ for supported OS/platforms. '
          'Enter a ticket https://github.com/nexB/scancode-toolkit/issues '
          'asking for support of your OS/platform combo.')
    sys.exit(1)

# Supported platforms and arches
# Supported Python versions


sys_platform = str(sys.platform).lower()

if not(
    sys_platform.startswith('linux')
    or 'win32' in sys_platform
    or 'darwin' in sys_platform
    or 'freebsd' in sys_platform
):
    unsupported(sys_platform)

if not (sys.maxsize > 2 ** 32):
    unsupported('32 bits: use a 64 bits OS and Python instead.')

if sys.version_info < (3, 6):
    unsupported('Only Python 64 bits 3.6 and above are supported.')

on_win = 'win32' in sys_platform

if on_win:
    BIN_DIR_NAME = 'Scripts'
else:
    BIN_DIR_NAME = 'bin'


def call(cmd):
    """
    Run the `cmd` command (as a list of args) with all env vars using `root_dir`
    as the current working directory.
    """
    cmd = ' '.join(cmd)
    try:
        subprocess.check_call(
            cmd,
            shell=True,
            env=dict(os.environ),
            cwd=ROOT_DIR,
            stderr=subprocess.STDOUT,
        )
    except Exception as e:
        raise Exception('Failed to run {}\n{}'.format(cmd, str(e)))
            

# list of cleanble directory and file paths
cleanable = '''
    build
    bin
    lib
    lib64
    include
    tcl
    local
    .Python
    .eggs
    pip-selfcheck.json
    src/scancode_toolkit.egg-info
    SCANCODE_DEV_MODE
    man
    Scripts
'''.split()


def find_pycache(root_dir):
    """
    Yield __pycache__ directory paths found in root_dir as paths relative to
    root_dir.
    """
    for top, dirs, _files in os.walk(root_dir):
        for d in dirs:
            if d != '__pycache__':
                continue
            dir_path = os.path.join(top, d)
            dir_path = dir_path.replace(root_dir, '', 1)
            dir_path = dir_path.strip(os.path.sep)
            yield dir_path


def clean(root_dir, cleanable=cleanable):
    """
    Remove `cleanable` directories and files from `root_dir`.
    """
    print('* Cleaning ...')

    # also clean __pycache__ if any
    cleanable.extend(find_pycache(root_dir))

    for d in cleanable:
        loc = os.path.join(root_dir, d)
        if os.path.exists(loc):
            if os.path.isdir(loc):
                shutil.rmtree(loc)
            else:
                os.remove(loc)


def quote(s):
    """
    Return a string s enclosed in double quotes.
    """
    return '"{}"'.format(s)


def create_virtualenv(root_dir, venv_pyz, quiet=False):
    """
    Create a virtualenv in the `root_dir` directory. Use the current Python
    exe.  Use the virtualenv.pyz app in at `venv_pyz`.
    If `quiet` is True, information messages are suppressed.

    Note: we do not use the bundled Python 3 "venv" because its behavior and
    presence is not consistent across Linux distro and sometimes pip is not
    included either by default. The virtualenv.pyz app cures all these issues.
    """
    if not quiet:
        print('* Configuring Python ...')

    if not venv_pyz or not os.path.exists(venv_pyz):
        print('Configuration Error: Unable to find {venv_pyz}... aborting.'.format(venv_pyz=venv_pyz))
        sys.exit(1)

    standard_python = sys.executable

    # once we have a pyz, we do not want to download anything else nor ever update
    vcmd = [
        standard_python, quote(venv_pyz),
        '--wheel', 'embed', '--pip', 'embed', '--setuptools', 'embed',
        '--seeder', 'pip',
        '--never-download',
        '--no-periodic-update',
    ]

    if quiet:
        vcmd += ['-qq']

    # we create the virtualenv in the root_dir
    vcmd += [quote(root_dir)]
    call(vcmd)


def activate_virtualenv():
    """
    Activate the ROOT_DIR virtualenv in the current process.
    """
    activate_this = os.path.join(BIN_DIR, 'activate_this.py')
    exec(open(activate_this).read(), {'__file__': activate_this})


def pip_install(req_args, quiet=False):
    """
    Install a list of `req_args` command line requirement arguments with
    pip, using packages found in THIRDPARTY_DIR_OR_LINKS directory or URL.
    """
    if not quiet:
        print('* Installing packages ...')

    if on_win:
        cmd = [CONFIGURED_PYTHON, '-m', 'pip']
    else:
        cmd = [quote(os.path.join(BIN_DIR, 'pip'))]

    # note: --no-build-isolation means that pip/wheel/setuptools will not
    # be reinstalled a second time and this speeds up the installation.
    # We always have the PEP517 build dependencies installed already.
    cmd += [
        'install', '--upgrade',
        '--no-build-isolation',
        '--no-index',
        '--find-links', THIRDPARTY_DIR_OR_LINKS,
    ]
    if quiet:
        cmd += ['-qq']

    cmd += req_args
    call(cmd)


def pip_cache_wheels(requirement_files, quiet=False):
    """
    Download and cache wheels from a list of `requirement_files` pip requirement
    files using packages found in THIRDPARTY_LINKS and save them in the
    THIRDPARTY_DIR directory.
    """
    if not quiet:
        print('* Downloading packages ...')

    for req_file in requirement_files:
        if on_win:
            cmd = [CONFIGURED_PYTHON, '-m', 'pip']
        else:
            cmd = [quote(os.path.join(BIN_DIR, 'pip'))]

        cmd += [
            'download', '--no-index',
            '--find-links', THIRDPARTY_LINKS,
            '--dest', THIRDPARTY_DIR,
        ]

        if quiet:
            cmd += ['-qq']

        cmd += ['--requirement', req_file]

        call(cmd)


def get_pip_req_files(req_args):
    rfs = [f for f in req_args if f.startswith('requirements') and f.endswith('.txt')]
    return rfs


usage = '\nUsage: configure [--clean] [<pip requirement arguments>]\n'

if __name__ == '__main__':

    # you must create a CONFIGURE_QUIET env var if you want to run quietly
    ##################
    quiet = 'CONFIGURE_QUIET' in os.environ

    # define/setup common directories and locations
    ##################
    current_dir = os.path.abspath(os.path.dirname(__file__))
    ROOT_DIR = os.path.dirname(current_dir)
    sys.path.insert(0, ROOT_DIR)

    BIN_DIR = os.path.join(ROOT_DIR, BIN_DIR_NAME)
    if on_win:
        CONFIGURED_PYTHON = os.path.join(BIN_DIR, 'python.exe')
    else:
        CONFIGURED_PYTHON = os.path.join(BIN_DIR, 'python')

    # THIRDPARTY_DIR is a cache of wheels
    THIRDPARTY_DIR = os.environ.get('THIRDPARTY_DIR', 'thirdparty')
    THIRDPARTY_DIR = os.path.join(ROOT_DIR, THIRDPARTY_DIR)
    os.makedirs(THIRDPARTY_DIR, exist_ok=True)

    THIRDPARTY_LINKS = os.environ.get('THIRDPARTY_LINKS', 'https://thirdparty.aboutcode.org/pypi')

    # no_cache = 'CONFIGURE_NO_CACHE' in os.environ
    # if no_cache:
    #     THIRDPARTY_DIR_OR_LINKS = THIRDPARTY_DIR
    # else:
    # if we have at least one wheel in THIRDPARTY_DIR, we assume we are offline
    # otherwise we are online and use our remote links for pip operations
    has_wheels = any(w.endswith('.whl') for w in os.listdir(THIRDPARTY_DIR))
    THIRDPARTY_DIR_OR_LINKS = THIRDPARTY_DIR if has_wheels else THIRDPARTY_LINKS

    # collect args
    ##################
    requirement_args = ['--requirement', 'requirements.txt']

    args = sys.argv[1:]
    if args:
        arg0 = args[0]
        if arg0 == '--clean':
            clean(ROOT_DIR)
            sys.exit(0)

        # use provided pip args instead of defaults
        requirement_args = args

    # Determine where to get dependencies from
    #################################

    # etc/thirdparty must contain virtualenv.pyz
    etc_thirdparty = os.path.join(os.path.dirname(__file__), 'thirdparty')
    VIRTUALENV_PYZ_APP_LOC = os.path.join(etc_thirdparty, 'virtualenv.pyz')
    if not os.path.exists(VIRTUALENV_PYZ_APP_LOC):
        print((
            '* FAILED to configure: virtualenv application {VIRTUALENV_PYZ_APP_LOC} not found. '
            'The current version needs to be saved in etc/thirdparty. '
            'See https://github.com/pypa/get-virtualenv and '
            'https://virtualenv.pypa.io/en/latest/installation.html#via-zipapp'
            ).format(VIRTUALENV_PYZ_APP_LOC=VIRTUALENV_PYZ_APP_LOC)
        )
        sys.exit(1)

    # Configure proper: create and activate virtualenv
    ###########################
    if not os.path.exists(CONFIGURED_PYTHON):
        create_virtualenv(root_dir=ROOT_DIR, venv_pyz=VIRTUALENV_PYZ_APP_LOC, quiet=quiet)

    activate_virtualenv()

    # cache requirements
    req_files = get_pip_req_files(requirement_args)
    # pip_cache_wheels(requirement_files=req_files, quiet=quiet)

    # ... and installl
    pip_install(requirement_args, quiet=quiet)

    if not quiet:
        print('* Configuration completed.')
        print()
