#!/usr/bin/python

# Copyright (c) 2017 nexB Inc. http://www.nexb.com/ - All rights reserved.

"""
This script a configuration helper to select pip requirement files to install
and python and shell configuration scripts to execute based on provided config
directories paths arguments and the operating system platform. To use, create
a configuration directory tree that contains any of these:

 * Requirements files named with this convention:
 - base.txt contains common requirements installed on all platforms.
 - win.txt, linux.txt, mac.txt, posix.txt are os-specific requirements.

 * Python scripts files named with this convention:
 - base.py is a common script executed on all os before os-specific scripts.
 - win.py, linux.py, mac.py, posix.py are os-specific scripts to execute.

 * Shell or Windows CMD scripts files named with this convention:
 - win.bat is a windows bat file to execute
 - posix.sh, linux.sh, mac.sh are os-specific scripts to execute.

The config directory structure contains one or more directories paths. This
way you can have a main configuration and additional sub-configurations of a
product such as for prod, test, ci, dev, or anything else.

All scripts and requirements are optional and only used if presents. Scripts
are executed in sequence, one after the other after all requirements are
installed, so they may import from any installed requirement.

The execution order is:
 - requirements installation
 - python scripts execution
 - shell scripts execution

On posix, posix Python and shell scripts are executed before mac or linux
scripts.

The base scripts or packages are always installed first before platform-
specific ones.

For example a tree could be looking like this::
    etc/conf
        base.txt : base pip requirements for all platforms
        linux.txt : linux-only pip requirements
        base.py : base config script for all platforms
        win.py : windows-only config script
        posix.sh: posix-only shell script

    etc/conf/prod
            base.txt : base pip requirements for all platforms
            linux.txt : linux-only pip requirements
            linux.sh : linux-only script
            base.py : base config script for all platforms
            mac.py : mac-only config script
"""

from __future__ import print_function

import os
import stat
import sys
import shutil
import subprocess


# platform-specific file base names
sys_platform = str(sys.platform).lower()
on_win = False
if 'linux' in sys_platform:
    platform_names = ('posix', 'linux',)
elif'win32' in sys_platform:
    platform_names = ('win',)
    on_win = True
elif 'darwin' in sys_platform:
    platform_names = ('posix', 'mac',)
else:
    raise Exception('Unsupported OS/platform %r' % sys_platform)
    platform_names = tuple()


# common file basenames for requirements and scripts
base = ('base',)

# known full file names with txt extension for requirements
# base is always last
requirements = tuple(p + '.txt' for p in platform_names + base)

# known full file names with py extensions for scripts
# base is always last
python_scripts = tuple(p + '.py' for p in platform_names + base)

# known full file names of shell scripts
# there is no base for scripts: they cannot work cross OS (cmd vs. sh)
shell_scripts = tuple(p + '.sh' for p in platform_names)
if on_win:
    shell_scripts = ('win.bat',)


def call(cmd, root_dir):
    """ Run a `cmd` command (as a list of args) with all env vars."""
    cmd = ' '.join(cmd)
    if  subprocess.Popen(cmd, shell=True, env=dict(os.environ), cwd=root_dir).wait() != 0:
        print()
        print('Failed to execute command:\n%(cmd)s. Aborting...' % locals())
        sys.exit(1)


def find_pycache(root_dir):
    """
    Yield __pycache__ directory paths found in root_dir as paths relative to
    root_dir.
    """
    for top, dirs, _files in os.walk(root_dir):
        for d in dirs:
            if d == '__pycache__':
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
        Lib
        include
        Include
        Scripts
        local
        .Python
        .eggs
        .cache
        pip-selfcheck.json
        src/scancode_toolkit.egg-info
        SCANCODE_DEV_MODE
    '''.split()

    # also clean __pycache__ if any
    cleanable.extend(find_pycache(root_dir))

    for d in cleanable:
        try:
            loc = os.path.join(root_dir, d)
            if os.path.exists(loc):
                if os.path.isdir(loc):
                    shutil.rmtree(loc)
                else:
                    os.remove(loc)
        except:
            pass


def build_pip_dirs_args(paths, root_dir, option='--extra-search-dir='):
    """
    Return an iterable of pip command line options for `option` of pip using a
    list of `paths` to directories.
    """
    for path in paths:
        if not os.path.isabs(path):
            path = os.path.join(root_dir, path)
        if os.path.exists(path):
            yield option + '"' + path + '"'


def create_virtualenv(std_python, root_dir, tpp_dirs, quiet=False):
    """
    Create a virtualenv in `root_dir` using the `std_python` Python
    executable. One of the `tpp_dirs` must contain a vendored virtualenv.py and
    virtualenv dependencies such as setuptools and pip packages.

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
    # search virtualenv.py in the tpp_dirs. keep the first found
    venv_py = None
    for tpd in tpp_dirs:
        venv = os.path.join(root_dir, tpd, 'virtualenv.py')
        if os.path.exists(venv):
            venv_py = '"' + venv + '"'
            break

    # error out if venv_py not found
    if not venv_py:
        print("Configuration Error ... aborting.")
        exit(1)

    vcmd = [std_python, venv_py, '--never-download']
    if quiet:
        vcmd += ['--quiet']
    # third parties may be in more than one directory
    vcmd.extend(build_pip_dirs_args(tpp_dirs, root_dir))
    # we create the virtualenv in the root_dir
    vcmd.append('"' + root_dir + '"')
    call(vcmd, root_dir)


def activate(root_dir):
    """ Activate a virtualenv in the current process."""
    print("* Activating ...")
    bin_dir = os.path.join(root_dir, 'bin')
    activate_this = os.path.join(bin_dir, 'activate_this.py')
    with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))


def install_3pp(configs, root_dir, tpp_dirs, quiet=False):
    """
    Install requirements from requirement files found in `configs` with pip,
    using the vendored components in `tpp_dirs`.
    """
    if not quiet:
        print("* Installing components ...")
    requirement_files = get_conf_files(configs, root_dir, requirements)
    for req_file in requirement_files:
        pcmd = ['pip', 'install', '--no-allow-external',
                '--use-wheel', '--no-index', '--no-cache-dir']
        if quiet:
            pcmd += ['--quiet']
        pip_dir_args = list(build_pip_dirs_args(tpp_dirs, root_dir, '--find-links='))
        pcmd.extend(pip_dir_args)
        req_loc = os.path.join(root_dir, req_file)
        pcmd.extend(['-r' , '"' + req_loc + '"'])
        call(pcmd, root_dir)


def run_scripts(configs, root_dir, configured_python, quiet=False):
    """
    Run Python scripts and shell scripts found in `configs`.
    """
    if not quiet:
        print("* Configuring ...")
    # Run Python scripts for each configurations
    for py_script in get_conf_files(configs, root_dir, python_scripts):
        cmd = [configured_python, '"' + os.path.join(root_dir, py_script) + '"']
        call(cmd, root_dir)

    # Run sh_script scripts for each configurations
    for sh_script in get_conf_files(configs, root_dir, shell_scripts):
        # we source the scripts on posix
        cmd = ['.']
        if on_win:
            cmd = []
        cmd = cmd + [os.path.join(root_dir, sh_script)]
        call(cmd, root_dir)


def chmod_bin(directory):
    """
    Makes the directory and its children executable recursively.
    """
    rwx = (stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR
           | stat.S_IXGRP | stat.S_IXOTH)
    for path, _, files in os.walk(directory):
        for f in files:
            os.chmod(os.path.join(path, f), rwx)


def get_conf_files(config_dir_paths, root_dir, file_names=requirements):
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


if __name__ == '__main__':
    # define/setup common directories
    etc_dir = os.path.abspath(os.path.dirname(__file__))
    root_dir = os.path.dirname(etc_dir)

    args = sys.argv[1:]
    if args[0] == '--clean':
        clean(root_dir)
        sys.exit(0)

    sys.path.insert(0, root_dir)
    bin_dir = os.path.join(root_dir, 'bin')
    standard_python = sys.executable

    # you must create a CONFIGURE_QUIET env var if you want to run quietly
    run_quiet = 'CONFIGURE_QUIET' in os.environ

    if on_win:
        configured_python = os.path.join(bin_dir, 'python.exe')
        scripts_dir = os.path.join(root_dir, 'Scripts')
        bin_dir = os.path.join(root_dir, 'bin')
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir)
        if not os.path.exists(bin_dir):
            cmd = ('mklink /J "%(bin_dir)s" "%(scripts_dir)s"' % locals()).split()
            call(cmd, root_dir)
    else:
        configured_python = os.path.join(bin_dir, 'python')
        scripts_dir = bin_dir

    # Get requested configuration paths to collect components and scripts later
    configs = []
    for path in args[:]:
        if not os.path.isabs(path):
            abs_path = os.path.join(root_dir, path)
            if os.path.exists(abs_path):
                configs.append(path)
        else:
            print()
            print('WARNING: Skipping missing Configuration directory:\n'
                  '  %(path)s does not exist.' % locals())
            print()

    # Collect vendor directories from environment variables: one or more third-
    # party directories may exist as environment variables prefixed with TPP_DIR
    thirdparty_dirs = []
    for envvar, path in os.environ.items():
        if not envvar.startswith('TPP_DIR'):
            continue
        if not os.path.isabs(path):
            abs_path = os.path.join(root_dir, path)
            if os.path.exists(abs_path):
                thirdparty_dirs.append(path)
        else:
            print()
            print('WARNING: Skipping missing Python thirdparty directory:\n'
                  '  %(path)s does not exist.\n'
                  '  Provided by environment variable:\n'
                  '  set %(envvar)s=%(path)s' % locals())
            print()

    # Finally execute our three steps: venv, install and scripts
    if not os.path.exists(configured_python):
        create_virtualenv(standard_python, root_dir, thirdparty_dirs, quiet=run_quiet)
    activate(root_dir)

    install_3pp(configs, root_dir, thirdparty_dirs, quiet=run_quiet)
    run_scripts(configs, root_dir, configured_python, quiet=run_quiet)
    chmod_bin(bin_dir)
    if not run_quiet:
        print("* Configuration completed.")
        print()
