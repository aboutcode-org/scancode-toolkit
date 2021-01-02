#!/usr/bin/python

# Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.

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
    print(f'Unsupported Python, OS, platform or architecture: {platform}')
    print('See https://github.com/nexB/scancode-toolkit/ for supported OS/platforms.')
    print('Enter a ticket https://github.com/nexB/scancode-toolkit/issues '
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
    unsupported('32 bits: use a 64 bits OS instead.')

if sys.version_info < (3, 6):
    unsupported('Only Python 3.6 and above are supported')

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
        raise Exception(f'Failed to run {cmd}') from e


# list of cleanble directory and file paths
cleanable = '''
    build
    bin
    lib
    lib64
    Lib
    Lib64
    include
    Include
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


def create_virtualenv(root_dir, quiet=False):
    """
    Create a virtualenv in the `root_dir` directory. Use the current Python
    exe.  Use the virtualenv.pyz app in THIRDPARTY_LOC directory.
    If `quiet` is True, information messages are suppressed.

    Note: we do not use the bundled Python 3 "venv" because its behavior and
    presence is not consistent across Linux distro and sometimes pip is not
    included either by default. The virtualenv.pyz app cures all these issues.
    """
    if not quiet:
        print('* Configuring Python ...')

    venv_pyz = os.path.join(THIRDPARTY_LOC, 'virtualenv.pyz')
    if not os.path.exists(venv_pyz):
        print(f'Configuration Error: Unable to find {venv_pyz}... aborting.')
        exit(1)

    standard_python = sys.executable

    # once we have a pyz, we do not want to download anything else
    vcmd = [standard_python, quote(venv_pyz), '--never-download']

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


STANDARD_REQUIREMENTS = ['pip', 'setuptools', 'wheel']

def pip_install(requirement_args, quiet=False):
    """
    Install a list of `args` command line requirement arguments with pip,
    using exclusively the bundled packages found in TPP_LOC directory.
    Run pip in `root_dir` in root dir.
    """
    if not quiet:
        print('* Installing components ...')

    if on_win:
        cmd = [CONFIGURED_PYTHON, '-m', 'pip']
    else:
        cmd = [quote(os.path.join(BIN_DIR, 'pip'))]

    cmd += ['install', '--upgrade', '--no-index', '--find-links', THIRDPARTY_LOC]
    if quiet:
        cmd += ['-qq']

    cmd += STANDARD_REQUIREMENTS
    cmd += requirement_args
    call(cmd)


usage = '\nUsage: configure [--clean] <pip requirements arguments>\n'

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
    THIRDPARTY_LOC = os.environ.get('THIRDPARTY_LOC', 'thirdparty')
    THIRDPARTY_LOC = os.path.join(ROOT_DIR, THIRDPARTY_LOC)

    if on_win:
        CONFIGURED_PYTHON = os.path.join(BIN_DIR, 'python.exe')
    else:
        CONFIGURED_PYTHON = os.path.join(BIN_DIR, 'python')

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

    # Finally configure proper: create virtualenv and install there
    ##################
    if not os.path.exists(CONFIGURED_PYTHON):
        create_virtualenv(root_dir=ROOT_DIR, quiet=quiet)

    activate_virtualenv()

    pip_install(requirement_args, quiet=quiet)

    if not quiet:
        print('* Configuration completed.')
        print()
