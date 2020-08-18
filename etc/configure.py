#!/usr/bin/python

# Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.

"""
This script is a configuration helper to configure a Python environment and
select which pip requirement files to install and which python or shell scripts
to execute based on provided configuration directories paths arguments and the
operating system platform. Everything is done inside in a virtual isolated
environment.

To use, create a configuration directory tree that contains any of these:

* Requirements files named with this convention:
 - requirements_base.txt contains common requirements installed on all platforms.
 - requirements_win.txt, requirements_linux.txt, requirements_mac.txt and
   requirements_posix.txt are os-specific requirements.

* Python scripts files named with this convention:
 - base.py is a common script executed on all os before os-specific scripts.
 - win.py, linux.py, mac.py, posix.py are os-specific scripts to execute.

* Shell or Windows CMD scripts files named with this convention:
 - win.bat is a windows bat file to execute
 - posix.sh, linux.sh, mac.sh are os-specific scripts to execute.

The config directory structure contains one or more directories paths. This
way you can have a main configuration (that is always used) and additional
sub-configurations of a product such as for prod, test, ci, dev, or anything
else.

All Python scripts, system scripts and requirements are optional and only used
if present. Scripts are executed in sequence, one after the other after all
requirements are installed, so they may import from any installed requirement.

The execution order is:
 - requirements installation
 - python scripts execution
 - shell scripts execution

On a POSIX OS, posix Python and shell scripts are executed before mac or linux
scripts.

The base scripts or packages are always installed first before platform-
specific ones.

For example a tree could be looking like this:
    etc/conf
        requirements_base.txt : base pip requirements for all platforms
        requirements_linux.txt : linux-only pip requirements
        base.py : base config script for all platforms
        win.py : windows-only config script
        posix.sh: posix-only shell script

    etc/conf/prod
        requirements_base.txt : base pip requirements for all platforms
        requirements_win.txt : Windows-only pip requirements
        linux.sh : linux-only script
        base.py : base config script for all platforms
        mac.py : mac-only config script

A call using etc/conf/prod would results in these steps if on linux:
1. Create a virtualenv
2. Run pip install with
    etc/conf/requirements_base.txt
    etc/conf/requirements_linux.txt
    etc/conf/prod/requirements_base.txt
    (etc/conf/prod/requirements_win.txt is skipped on linux)
3. Run these Python scripts:
    etc/conf/base.py
    (etc/conf/win.py is skipped on linux)
    etc/conf/prod/base.py
    (etc/conf/prod/mac.py is skipped on linux)
4. Run these shell scripts:
    etc/conf/posix.sh
    etc/conf/prod/linux.sh
"""

from __future__ import absolute_import
from __future__ import print_function

import io
import os
import shutil
import stat
import subprocess
import sys


# platform-specific file base names
sys_platform = str(sys.platform).lower()
on_win = False
if sys_platform.startswith('linux'):
    platform_names = ('posix', 'linux',)
elif 'win32' in sys_platform:
    platform_names = ('win',)
    on_win = True
elif 'darwin' in sys_platform:
    platform_names = ('posix', 'mac',)
elif 'freebsd' in sys_platform:
    platform_names = ('posix', 'freebsd',)
else:
    raise Exception('Unsupported OS/platform %r' % sys_platform)
    platform_names = tuple()


# Python versions
_sys_v0 = sys.version_info[0]
py2 = _sys_v0 == 2
py3 = _sys_v0 == 3


# common file basenames for requirements and scripts
base = ('base',)

# known full file names with txt extension for requirements
# base is always last
requirement_filenames = tuple('requirements_' + p + '.txt' for p in platform_names + base)

# known full file names with py extensions for scripts
# base is always last
python_scripts = tuple(p + '.py' for p in platform_names + base)

# known full file names of shell scripts
# there is no base for scripts: they cannot work cross OS (cmd vs. sh)
shell_scripts = tuple(p + '.sh' for p in platform_names)
if on_win:
    shell_scripts = ('win.bat',)
    bin_dir_name = 'Scripts'
else:
    bin_dir_name = 'bin'

# set to True to trace command line executaion
TRACE = False


def call(cmd, root_dir):
    """
    Run the `cmd` command (as a list of args) with all env vars using `root_dir`
    as the current working directory.
    """
    cmd = ' '.join(cmd)
    if TRACE:
        print('\n===> About to run command:\n%(cmd)s\n' % locals())
        try:
            subprocess.check_output(
                cmd,
                shell=True,
                env=dict(os.environ),
                cwd=root_dir,
                stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as cpe:
            print('Failed ro run command: {}'.format(cmd))
            print(cpe.output)
            raise
        return

    subprocess.check_call(cmd, shell=True, env=dict(os.environ), cwd=root_dir)


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


def clean(root_dir):
    """
    Remove cleanable directories and files in root_dir.
    """
    print('* Cleaning ...')
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
        .cache
        pip-selfcheck.json
        src/scancode_toolkit.egg-info
        SCANCODE_DEV_MODE
        man
        Scripts
    '''.split()

    # also clean __pycache__ if any
    cleanable.extend(find_pycache(root_dir))

    for d in cleanable:
        loc = os.path.join(root_dir, d)
        if os.path.exists(loc):
            if os.path.isdir(loc):
                shutil.rmtree(loc)
            else:
                os.remove(loc)


def build_pip_dirs_args(paths, root_dir, option='--extra-search-dir='):
    """
    Return an iterable of pip command line options for `option` of pip using a
    list of `paths` to directories.
    """
    for path in paths:
        if path.startswith('https'):
            yield option + '"{}"'.format(path)
        else:        
            if not os.path.isabs(path):
                path = os.path.join(root_dir, path)
            if os.path.exists(path):
                yield option + quote(path)


def create_virtualenv(std_python, root_dir, tpp_dirs=(), quiet=False):
    """
    Create a virtualenv in `root_dir` using the `std_python` Python executable.
    One of the `tpp_dirs` must contain a bundled virtualenv.pyz Python app.

    Note: we do not use the bundled Python 3 "venv" because its behavior
    is not consistent across Linux distro and sometimes pip is not included.

    @std_python: Path or name of the Python executable to use.

    @root_dir: directory in which the virtualenv will be created. This is also
    the root directory for the project and the base directory for vendored
    components directory paths.

    @tpp_dirs: list of directory paths relative to `root_dir` containing
    vendored Python distributions that pip will use to find required
    components.
    """
    if not quiet:
        print("* Configuring Python ...")
    # search the virtualenv.pyz app in the tpp_dirs. keep the first found
    venv_pyz = None
    for tpd in tpp_dirs:
        if tpd.startswith('https'):
            continue
        venv = os.path.join(root_dir, tpd, 'virtualenv.pyz')
        if os.path.exists(venv):
            venv_pyz = venv
            break

    # error out if venv_pyz not found
    if not venv_pyz:
        print("Configuration Error ... aborting.")
        exit(1)

    vcmd = [quote(std_python), quote(venv_pyz), '--never-download']
    if quiet:
        vcmd += ['-qq']
    # third parties may be in more than one directory
    vcmd.extend(build_pip_dirs_args(tpp_dirs, root_dir))
    # Window doesn't support link as extra-search-dir
    if on_win:
        vcmd.pop()
    # we create the virtualenv in the root_dir
    vcmd.append(quote(root_dir))
    call(vcmd, root_dir)


def quote(s):
    """
    Return a string s enclosed in double quotes.
    """
    return '"{}"'.format(s)


def install_3pp(configs, root_dir, tpp_dirs, quiet=False):
    """
    Install requirements from requirement files found in `configs` with pip,
    using the vendored components in `tpp_dirs`.
    """
    requirement_files = get_conf_files(configs, root_dir, requirement_filenames, quiet)
    requirements = []
    for req_file in requirement_files:
        req_loc = os.path.join(root_dir, req_file)
        requirements.extend(['--requirement', quote(req_loc)])
    run_pip(requirements, root_dir, tpp_dirs, quiet)


def install_local_package(root_dir, tpp_dirs, quiet=False):
    """
    Install the current local package with pip,
    using the vendored components in `tpp_dirs`.
    """
    requirements = ['--editable', '.']
    run_pip(requirements, root_dir, tpp_dirs, quiet)


def run_pip(requirements, root_dir, tpp_dirs, quiet=False):
    """
    Install a list of `requirements` with pip,
    using the vendored components in `tpp_dirs`.
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
        '--no-index', '--no-cache-dir',
    ]
    pcmd.extend(build_pip_dirs_args(tpp_dirs, root_dir, '--find-links='))
    if quiet:
        pcmd += ['-qq']

    pcmd.extend(requirements)
    call(pcmd, root_dir)


def run_scripts(configs, root_dir, configured_python, quiet=False):
    """
    Run Python scripts and shell scripts found in `configs`.
    """
    if not quiet:
        print("* Configuring ...")
    # Run Python scripts for each configurations
    for py_script in get_conf_files(configs, root_dir, python_scripts):
        cmd = [quote(configured_python), quote(os.path.join(root_dir, py_script))]
        call(cmd, root_dir)

    # Run sh_script scripts for each configurations
    for sh_script in get_conf_files(configs, root_dir, shell_scripts):
        if on_win:
            cmd = []
        else:
            # we source the scripts on posix
            cmd = ['.']
        cmd.extend([quote(os.path.join(root_dir, sh_script))])
        call(cmd, root_dir)


def get_conf_files(config_dir_paths, root_dir, file_names=requirement_filenames, quiet=False):
    """
    Return a list of collected path-prefixed file paths matching names in a
    file_names tuple, based on config_dir_paths, root_dir and the types of
    file_names requested. Returned paths are posix paths.

    @config_dir_paths: Each config_dir_path is a relative from the project
    root to a config dir. This script should always be called from the project
    root dir.

    @root_dir: The project absolute root dir.

    @file_names: get requirements, python or shell files based on list of
    supported file names provided as a tuple of supported file_names.

    Scripts or requirements are optional and only used if presents. Unknown
    scripts or requirements file_names are ignored (but they could be used
    indirectly by known requirements with -r requirements inclusion, or
    scripts with python imports.)

    Since Python scripts are executed after requirements are installed they
    can import from any requirement-installed component such as Fabric.
    """
    # collect files for each requested dir path
    collected = []
    for config_dir_path in config_dir_paths:
        abs_config_dir_path = os.path.join(root_dir, config_dir_path)
        if not os.path.exists(abs_config_dir_path):
            if not quiet:
                print('Configuration directory %(config_dir_path)s '
                      'does not exists. Skipping.' % locals())
            continue
        # Support args like enterprise or enterprise/dev
        paths = config_dir_path.strip('/').replace('\\', '/').split('/')
        # a tuple of (relative path, location,)
        current = None
        for path in paths:
            if not current:
                current = (path, os.path.join(root_dir, path),)
            else:
                base_path, base_loc = current
                current = (os.path.join(base_path, path),
                           os.path.join(base_loc, path),)
            path, loc = current
            # we iterate on known filenames to ensure the defined precedence
            # is respected (posix over mac, linux), etc
            for n in file_names:
                for f in os.listdir(loc):
                    if f == n:
                        f_loc = os.path.join(loc, f)
                        if f_loc not in collected:
                            collected.append(f_loc)

    return collected


def activate(root_dir):
    """
    Activate a virtualenv in the current process.
    """
    bin_dir = os.path.join(root_dir, bin_dir_name)
    activate_this = os.path.join(bin_dir, 'activate_this.py')
    # TODO: we could use it as is and not write then read from disk?
    activate_this_script = save_activate_this_py_script(activate_this)
    code = compile(activate_this_script, activate_this, 'exec')
    exec(code, dict(__file__=activate_this))


def save_activate_this_py_script(activate_path):
    """
    Python 3 venv does not ship activate_this.py anymore. So we bundle it.
    From https://raw.githubusercontent.com/pypa/virtualenv/28839085ff8a5a770bb4a8c52158d763760c89c1/virtualenv_embedded/activate_this.py

    Copyright (c) 2007 Ian Bicking and Contributors
    Copyright (c) 2009 Ian Bicking, The Open Planning Project
    Copyright (c) 2011-2016 The virtualenv developers

    Permission is hereby granted, free of charge, to any person obtaining
    a copy of this software and associated documentation files (the
    "Software"), to deal in the Software without restriction, including
    without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to
    permit persons to whom the Software is furnished to do so, subject to
    the following conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
    LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
    OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
    WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    """
    activate_this = u'''
"""Activate virtualenv for current interpreter:

Use exec(open(this_file).read(), {'__file__': this_file}).

This can be used when you must use an existing Python interpreter, not the virtualenv bin/python.
"""
import os
import site
import sys

try:
    __file__
except NameError:
    raise AssertionError("You must use exec(open(this_file).read(), {'__file__': this_file}))")

# prepend bin to PATH (this file is inside the bin directory)
bin_dir = os.path.dirname(os.path.abspath(__file__))
os.environ["PATH"] = os.pathsep.join([bin_dir] + os.environ.get("PATH", "").split(os.pathsep))

base = os.path.dirname(bin_dir)

# virtual env is right above bin directory
os.environ["VIRTUAL_ENV"] = base

# add the virtual environments site-package to the host python import mechanism
IS_PYPY = hasattr(sys, "pypy_version_info")
IS_JYTHON = sys.platform.startswith("java")
if IS_JYTHON:
    site_packages = os.path.join(base, "Lib", "site-packages")
elif IS_PYPY:
    site_packages = os.path.join(base, "site-packages")
else:
    IS_WIN = sys.platform == "win32"
    if IS_WIN:
        site_packages = os.path.join(base, "Lib", "site-packages")
    else:
        site_packages = os.path.join(base, "lib", "python{}".format(sys.version[:3]), "site-packages")

prev = set(sys.path)
site.addsitedir(site_packages)
sys.real_prefix = sys.prefix
sys.prefix = base

# Move the added items to the front of the path, in place
new = list(sys.path)
sys.path[:] = [i for i in new if i not in prev] + [i for i in new if i in prev]

'''
    if not os.path.exists(activate_path):
        with io.open(activate_path, 'w', encoding='utf-8') as f:
            f.write(activate_this)
    return activate_this


usage = '\nUsage: configure [--clean] <path/to/configuration/directory>\n'


if __name__ == '__main__':

    # you must create a CONFIGURE_QUIET env var if you want to run quietly
    quiet = 'CONFIGURE_QUIET' in os.environ

    # define/setup common directories
    etc_dir = os.path.abspath(os.path.dirname(__file__))
    root_dir = os.path.dirname(etc_dir)

    args = sys.argv[1:]
    if args:
        arg0 = args[0]
        if arg0 == '--clean':
            clean(root_dir)
            sys.exit(0)
        elif arg0.startswith('-'):
            print()
            print('ERROR: unknown option: %(arg0)s' % locals())
            print(usage)
            sys.exit(1)

    sys.path.insert(0, root_dir)
    bin_dir = os.path.join(root_dir, bin_dir_name)
    standard_python = sys.executable

    if on_win:
        configured_python = os.path.join(bin_dir, 'python.exe')
    else:
        configured_python = os.path.join(bin_dir, 'python')

    # Get requested configuration paths to collect components and scripts later
    configs = []
    for path in args[:]:
        abs_path = path
        if not os.path.isabs(path):
            abs_path = os.path.join(root_dir, path)
        if not os.path.exists(abs_path):
            print()
            print('ERROR: Configuration directory does not exists:\n'
                  '  %(path)s: %(abs_path)r'
                  % locals())
            print(usage)
            sys.exit(1)

        configs.append(path)

    # Collect vendor directories from environment variables: one or more third-
    # party directories may exist as environment variables prefixed with TPP_DIR
    thirdparty_dirs = []
    for envvar, path in os.environ.items():
        if not envvar.startswith('TPP_DIR'):
            continue
        if path.startswith('https'):
            thirdparty_dirs.append(path)
        else:        
            abs_path = path
            if not os.path.isabs(path):
                abs_path = os.path.join(root_dir, path)
            if not os.path.exists(abs_path):
                if not quiet:
                    print()
                    print(
                        'WARNING: Third-party Python libraries directory does not exists:\n'
                        '  %(path)r: %(abs_path)r\n'
                        '  Provided by environment variable:\n'
                        '  set %(envvar)s=%(path)r' % locals())
                    print()
            else:
                thirdparty_dirs.append(path)

    # Finally execute our three steps: venv, install and scripts
    if not os.path.exists(configured_python):
        create_virtualenv(standard_python, root_dir, thirdparty_dirs, quiet=quiet)
    activate(root_dir)
    install_3pp(configs, root_dir, thirdparty_dirs, quiet=quiet)
    install_local_package(root_dir, thirdparty_dirs, quiet=quiet)
    run_scripts(configs, root_dir, configured_python, quiet=quiet)

    if not quiet:
        print("* Configuration completed.")
        print()
