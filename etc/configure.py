#!/usr/bin/python

# Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.

"""
This script is a configuration helper that wrap pip and virtualenv to configure
a Python virtual environment and install requirement files with pip. It does
some minimal checks on supported OSes, architectures and Python versions.

To use, create requirements flies and use this way:

* to configure and install::

    ./configure.py [<requirement or path to requirements file>, ...]

* to cleanup everything::

    ./configure.py --clean
"""

import io
import os
from os import path
import shutil
import stat
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
    bin_dir_name = 'Scripts'
else:
    bin_dir_name = 'bin'


def call(cmd, root_dir):
    """
    Run the `cmd` command (as a list of args) with all env vars using `root_dir`
    as the current working directory.
    """
    try:
        cmd = ' '.join(cmd)
        subprocess.check_call(
            cmd,
            shell=True,
            env=dict(os.environ),
            cwd=root_dir,
            stderr=subprocess.STDOUT,
        )
    except Exception:
        print(cmd)
        raise


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


def build_pip_dirs_args(paths_or_urls, root_dir, option='--extra-search-dir'):
    """
    Return an iterable of pip command line options for `option` of pip using a
    list of `paths_or_urls` paths to directories or URLs.
    """
    for path_or_url in paths_or_urls:
        if path_or_url.startswith('https'):
            yield '='.join([option, f'"{path_or_url}"'])
        else:
            if not os.path.isabs(path_or_url):
                path_or_url = os.path.join(root_dir, path_or_url)
            if os.path.exists(path_or_url):
                # always = and quoted path
                yield '='.join([option, quote(path_or_url)])


def create_virtualenv(std_python, root_dir, thirdparty_locs=(), quiet=False):
    """
    Create a virtualenv in the `root_dir` directory using the `std_python` path
    to a Python executable. One of the `thirdparty_locs` directory paths must
    contain a bundled virtualenv.pyz Python app and any other thirdparty
    packages. If `quiet` is True, information messages are suppressed.

    Note: we do not use the bundled Python 3 "venv" because its behavior is not
    consistently present across Linux distro and sometimes pip is not included.
    components.
    """
    if not quiet:
        print("* Configuring Python ...")
    # search the virtualenv.pyz app in the tpp_dirs. keep the first found
    venv_pyz = None
    for tpd in thirdparty_locs:
        if tpd.startswith('https'):
            continue
        venv = os.path.join(root_dir, tpd, 'virtualenv.pyz')
        if os.path.exists(venv):
            venv_pyz = venv
            break

    # error out if venv_pyz not found
    if not venv_pyz:
        print("Configuration Error: Unable to find virtualenv.pyz ... aborting.")
        exit(1)

    # once we have a pyz, we do not want to download anything else
    vcmd = [quote(std_python), quote(venv_pyz), '--never-download']
    if quiet:
        vcmd += ['-qq']
    # we create the virtualenv in the root_dir
    vcmd.append(quote(root_dir))
    call(vcmd, root_dir)


def quote(s):
    """
    Return a string s enclosed in double quotes.
    """
    return '"{}"'.format(s)


def run_pip(requirements, root_dir, tpp_locs, quiet=False):
    """
    Install a list of `requirements` with pip,
    using the vendored components in `tpp_locs` directories or find-links URLs.
    """
    if not quiet:
        print("* Installing components ...")

    if on_win:
        configured_python = quote(os.path.join(root_dir, bin_dir_name, 'python.exe'))
        base_cmd = [configured_python, '-m', 'pip']
    else:
        configured_pip = quote(os.path.join(root_dir, bin_dir_name, 'pip'))
        base_cmd = [configured_pip]

    pcmd = base_cmd + [
        'install',
        '--upgrade',
        '--no-index',
    ]
    pcmd.extend(build_pip_dirs_args(tpp_locs, root_dir, '--find-links'))
    if quiet:
        pcmd += ['-qq']

    pcmd.extend(requirements)
    call(pcmd, root_dir)


def activate(root_dir):
    """
    Activate a virtualenv in the current process.
    """
    bin_dir = os.path.join(root_dir, bin_dir_name)
    activate_this = os.path.join(bin_dir, 'activate_this.py')
    exec(open(activate_this).read(), {'__file__': activate_this})


def get_thirdparty_locs():
    """
    Return a list of directories and URLS suitable for use with pip --find-
    links, either local directories with whels or URLs to a PyPI found in
    environment variables prefixed with THIRDPARTY_LOC
    """
    tpp_locs = []
    for envvar, loc_or_url in os.environ.items():
        if not envvar.startswith('THIRDPARTY_LOC'):
            continue

        if loc_or_url.startswith('https'):
            tpp_locs.append(loc_or_url)
            continue

        abs_path = loc_or_url
        if not os.path.isabs(loc_or_url):
            abs_path = os.path.join(root_dir, loc_or_url)

        tpp_locs.append(loc_or_url)

        if not os.path.exists(abs_path):
            raise Exception(
                    'WARNING: Third-party Python libraries directory does not exists:\n'
                    '  %(loc_or_url)r: %(abs_path)r\n'
                    '  Provided by environment variable:\n'
                    '  set %(envvar)s=%(loc_or_url)r' % locals())
    return tpp_locs


usage = '\nUsage: configure [--clean] <path/to/configuration/directory>\n'

if __name__ == '__main__':

    # you must create a CONFIGURE_QUIET env var if you want to run quietly
    quiet = 'CONFIGURE_QUIET' in os.environ

    # define/setup common directories
    etc_dir = os.path.abspath(os.path.dirname(__file__))
    root_dir = os.path.dirname(etc_dir)
    requirements = ['requirements.txt']
    args = sys.argv[1:]
    if args:
        arg0 = args[0]
        if arg0 == '--clean':
            clean(root_dir)
            sys.exit(0)

        if arg0.startswith('-'):
            print()
            print('ERROR: unknown option: %(arg0)s' % locals())
            print(usage)
            sys.exit(1)

        requirements = args

    thirdparty_locs = get_thirdparty_locs()

    sys.path.insert(0, root_dir)
    bin_dir = os.path.join(root_dir, bin_dir_name)
    standard_python = sys.executable

    if on_win:
        configured_python = os.path.join(bin_dir, 'python.exe')
    else:
        configured_python = os.path.join(bin_dir, 'python')

    # Finally execute our three steps: venv, install and scripts
    if not os.path.exists(configured_python):
        create_virtualenv(standard_python, root_dir, thirdparty_locs, quiet=quiet)

    activate(root_dir)

    # upgrade the basics in place before doing anything else
    basic_reqs = ['pip', 'setuptools']
    run_pip(basic_reqs, root_dir, thirdparty_locs, quiet=quiet)

    # install in sequence (and separately to avoid hash/no hash issues) each of
    # the requirements provided: detect if we have a file or a plain requirement
    for req in requirements:
        if os.path.exists(req):
            reqs = ['--requirement', quote(req)]
        else:
            reqs = [req]

        run_pip(reqs, root_dir, thirdparty_locs, quiet=quiet)

    if not quiet:
        print("* Configuration completed.")
        print()
