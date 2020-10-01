"""A simple packaging tool for simple packages."""
import argparse
import logging
import os
import pathlib
import shutil
import subprocess
import sys
from typing import Optional

from flit_core import common
from .inifile import ConfigError
from .log import enable_colourful_output

__version__ = '2.3.0'

log = logging.getLogger(__name__)


class PythonNotFoundError(FileNotFoundError): pass


def find_python_executable(python: Optional[str] = None) -> str:
    """Returns an absolute filepath to the executable of Python to use."""
    if not python:
        python = os.environ.get("FLIT_INSTALL_PYTHON")
    if not python:
        return sys.executable
    if os.path.isabs(python):  # sys.executable is absolute too
        return python
    # get absolute filepath of {python}
    # shutil.which may give a different result to the raw subprocess call
    # see https://github.com/takluyver/flit/pull/300 and https://bugs.python.org/issue38905
    resolved_python = shutil.which(python)
    if resolved_python is None:
        raise PythonNotFoundError("Unable to resolve Python executable {!r}".format(python))
    try:
        return subprocess.check_output(
            [resolved_python, "-c", "import sys; print(sys.executable)"],
            universal_newlines=True,
        ).strip()
    except Exception as e:
        raise PythonNotFoundError(
            "{} occurred trying to find the absolute filepath of Python executable {!r} ({!r})".format(
                e.__class__.__name__, python, resolved_python
            )
        ) from e


def add_shared_install_options(parser: argparse.ArgumentParser):
    parser.add_argument('--user', action='store_true', default=None,
        help="Do a user-local install (default if site.ENABLE_USER_SITE is True)"
    )
    parser.add_argument('--env', action='store_false', dest='user',
        help="Install into sys.prefix (default if site.ENABLE_USER_SITE is False, i.e. in virtualenvs)"
    )
    parser.add_argument('--python',
        help="Target Python executable, if different from the one running flit"
    )


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('-f', '--ini-file', type=pathlib.Path, default='pyproject.toml')
    ap.add_argument('-V', '--version', action='version', version='Flit '+__version__)
    # --repository now belongs on 'flit publish' - it's still here for
    # compatibility with scripts passing it before the subcommand.
    ap.add_argument('--repository', dest='deprecated_repository', help=argparse.SUPPRESS)
    ap.add_argument('--debug', action='store_true', help=argparse.SUPPRESS)
    ap.add_argument('--logo', action='store_true', help=argparse.SUPPRESS)
    subparsers = ap.add_subparsers(title='subcommands', dest='subcmd')

    # flit build --------------------------------------------
    parser_build = subparsers.add_parser('build',
        help="Build wheel and sdist",
    )

    parser_build.add_argument('--format', action='append',
        help="Select a format to build. Options: 'wheel', 'sdist'"
    )

    parser_build.add_argument('--no-setup-py', action='store_false', dest='setup_py',
        help=("Don't generate a setup.py file in the sdist. "
              "The sdist will only work with tools that support PEP 517, "
              "but the wheel will still be usable by any compatible tool."
             )
    )

    # flit publish --------------------------------------------
    parser_publish = subparsers.add_parser('publish',
        help="Upload wheel and sdist",
    )

    parser_publish.add_argument('--format', action='append',
        help="Select a format to publish. Options: 'wheel', 'sdist'"
    )

    parser_publish.add_argument('--no-setup-py', action='store_false', dest='setup_py',
        help=("Don't generate a setup.py file in the sdist. "
              "The sdist will only work with tools that support PEP 517, "
              "but the wheel will still be usable by any compatible tool."
             )
    )

    parser_publish.add_argument('--repository',
        help="Name of the repository to upload to (must be in ~/.pypirc)"
    )

    # flit install --------------------------------------------
    parser_install = subparsers.add_parser('install',
        help="Install the package",
    )
    parser_install.add_argument('-s', '--symlink', action='store_true',
        help="Symlink the module/package into site packages instead of copying it"
    )
    parser_install.add_argument('--pth-file', action='store_true',
        help="Add .pth file for the module/package to site packages instead of copying it"
    )
    add_shared_install_options(parser_install)
    parser_install.add_argument('--deps', choices=['all', 'production', 'develop', 'none'], default='all',
        help="Which set of dependencies to install. If --deps=develop, the extras dev, doc, and test are installed"
    )
    parser_install.add_argument('--extras', default=(), type=lambda l: l.split(',') if l else (),
        help="Install the dependencies of these (comma separated) extras additionally to the ones implied by --deps. "
             "--extras=all can be useful in combination with --deps=production, --deps=none precludes using --extras"
    )

    # flit installfrom (deprecated) ---------------------------------------
    parser_installfrom = subparsers.add_parser('installfrom',
       help="Download and install a package using flit from source"
    )
    parser_installfrom.add_argument('location',
        help="A URL to download, or a shorthand like github:takluyver/flit"
    )
    add_shared_install_options(parser_installfrom)

    # flit init --------------------------------------------
    parser_init = subparsers.add_parser('init',
        help="Prepare pyproject.toml for a new package"
    )

    args = ap.parse_args(argv)

    cf = args.ini_file
    if (
        args.subcmd not in {'init', 'installfrom'}
        and cf == pathlib.Path('pyproject.toml')
        and not cf.is_file()
    ):
        # Fallback to flit.ini if it's present
        cf_ini = pathlib.Path('flit.ini')
        if cf_ini.is_file():
            args.ini_file = cf_ini
        else:
            sys.exit('Neither pyproject.toml nor flit.ini found, '
                     'and no other config file path specified')

    enable_colourful_output(logging.DEBUG if args.debug else logging.INFO)

    log.debug("Parsed arguments %r", args)

    if args.logo:
        from .logo import clogo
        print(clogo.format(version=__version__))
        sys.exit(0)

    if args.subcmd == 'build':
        from .build import main
        try:
            main(args.ini_file, formats=set(args.format or []),
                 gen_setup_py=args.setup_py)
        except(common.NoDocstringError, common.VCSError, common.NoVersionError) as e:
            sys.exit(e.args[0])
    elif args.subcmd == 'publish':
        if args.deprecated_repository:
            log.warning("Passing --repository before the 'upload' subcommand is deprecated: pass it after")
        repository = args.repository or args.deprecated_repository
        from .upload import main
        main(args.ini_file, repository, formats=set(args.format or []),
                gen_setup_py=args.setup_py)

    elif args.subcmd == 'install':
        from .install import Installer
        try:
            python = find_python_executable(args.python)
            Installer.from_ini_path(args.ini_file, user=args.user, python=python,
                      symlink=args.symlink, deps=args.deps, extras=args.extras,
                      pth=args.pth_file).install()
        except (ConfigError, PythonNotFoundError, common.NoDocstringError, common.NoVersionError) as e:
            sys.exit(e.args[0])
    elif args.subcmd == 'installfrom':
        log.warning("'flit installfrom' is deprecated: use a recent version of pip instead")
        from .installfrom import installfrom
        try:
            python = find_python_executable(args.python)
        except PythonNotFoundError as e:
            sys.exit(e.args[0])
        sys.exit(installfrom(args.location, user=args.user, python=python))
    elif args.subcmd == 'init':
        from .init import TerminalIniter
        TerminalIniter().initialise()
    else:
        ap.print_help()
        sys.exit(1)
