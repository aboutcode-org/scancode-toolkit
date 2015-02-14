import os
import re
import sys
import cgi
import shutil
import atexit
import tempfile
import warnings
import textwrap
import functools
from subprocess import check_call
import pkg_resources
import glob
import optparse

try:
    import wheel as _; _
    has_wheel = True
except ImportError:
    has_wheel = False

try:
    import pip
except ImportError:
    pip = None

class PipError(Exception):
    pass

def warn_wheel():
    print(
        "ERROR: .whl packages were downloaded but the wheel package "
        "is not installed, so they cannot be correctly processed.\n"
        "Install it with:\n"
        "    pip install wheel"
    )
    try:
        import setuptools
        setuptools_version = setuptools.__version__
    except ImportError:
        setuptools_version = ''
    if setuptools_version < '1.0.0':
        print(
            "WARNING: your setuptools package is out of date. This "
            "could lead to bad things.\n"
            "You should likely update it:\n"
            "    pip install -U setuptools"
        )

def dedent(text):
    return textwrap.dedent(text.lstrip("\n")).rstrip()

def maintain_cwd(f):
    @functools.wraps(f)
    def maintain_cwd_helper(*args, **kwargs):
        orig_dir = os.getcwd()
        try:
            return f(*args, **kwargs)
        finally:
            os.chdir(orig_dir)
    return maintain_cwd_helper

class InvalidFilePackageName(ValueError):
    def __init__(self, file, basedir=None):
        msg = "unexpected file name: %r " %(file, )
        msg += "(not in 'pkg-name-version.xxx' format"
        if basedir:
            msg += "; found in directory: %r" %(basedir)
        msg += ")"
        super(InvalidFilePackageName, self).__init__(msg)

def egg_to_package(file):
    warnings.warn("egg_to_package is deprecated; use file_to_package.",
                  stacklevel=1)
    return file_to_package(file)

def file_to_package(file, basedir=None):
    """ Returns the package name for a given file, or raises an
        ``InvalidFilePackageName`` exception if the file name is
        not valid::

        >>> file_to_package("foo-1.2.3_rc1.tar.gz")
        ('foo', '1.2.3-rc1.tar.gz')
        >>> file_to_package("foo-bar-1.2.tgz")
        ('foo-bar', '1.2.tgz')
        >>> file_to_package("kafka-quixey-0.8.1-1.tar.gz")
        ('kafka-quixey', '0.8.1-1.tar.gz')
        >>> file_to_package("foo-bar-1.2-py27-none-any.whl")
        ('foo-bar', '1.2-py27-none-any.whl')
        >>> file_to_package("Cython-0.17.2-cp26-none-linux_x86_64.whl")
        ('Cython', '0.17.2-cp26-none-linux_x86_64.whl')
        >>> file_to_package("PyYAML-3.10-py2.7-macosx-10.7-x86_64.egg")
        ('PyYAML', '3.10-py2.7-macosx-10.7-x86_64.egg')
        >>> file_to_package("python_ldap-2.3.9-py2.7-macosx-10.3-fat.egg")
        ('python-ldap', '2.3.9-py2.7-macosx-10.3-fat.egg')
        >>> file_to_package("foo.whl")
        Traceback (most recent call last):
            ...
        InvalidFilePackageName: unexpected file name: 'foo.whl' (not in 'pkg-name-version.xxx' format)
        >>> file_to_package("foo.png")
        Traceback (most recent call last):
            ...
        InvalidFilePackageName: unexpected file name: 'foo.png' (not in 'pkg-name-version.xxx' format)
        """
    file = os.path.basename(file)
    file_ext = os.path.splitext(file)[1].lower()
    if file_ext == ".egg":
        dist = pkg_resources.Distribution.from_location(None, file)
        name = dist.project_name
        split = (name, file[len(name)+1:])
        to_safe_name = lambda x: x
    elif file_ext == ".whl":
        bits = file.rsplit("-", 4)
        split = (bits[0], "-".join(bits[1:]))
        to_safe_name = lambda x: x
    else:
        match = re.search(r"(?P<pkg>.*?)-(?P<rest>\d+.*)", file)
        if not match:
            raise InvalidFilePackageName(file, basedir)
        split = (match.group("pkg"), match.group("rest"))
        to_safe_name = pkg_resources.safe_name

    if len(split) != 2 or not split[1]:
        raise InvalidFilePackageName(file, basedir)

    return (split[0], to_safe_name(split[1]))

def try_int(x):
    try:
        return int(x)
    except ValueError:
        return x

def pip_get_version():
    pip_dist = pkg_resources.get_distribution("pip")
    return tuple(try_int(x) for x in pip_dist.version.split("."))

def pip_run_command(pip_args):
    if pip is None:
        print("===== WARNING =====")
        print("Cannot `import pip` - falling back to the pip executable.")
        print("This will be deprecated in a future release.")
        print("Please open an issue if this will be a problem: "
              "https://github.com/wolever/pip2pi/issues")
        print("===================")
        check_call(["pip"] + pip_args)
        return

    version = pip_get_version()
    if version < (1, 1):
        raise RuntimeError("pip >= 1.1 required, but %s is installed"
                           %(version, ))
    res = pip.main(pip_args)
    if res != 0:
        raise PipError("pip failed with status %s while running: %s"
                       %(res, pip_args))


OS_HAS_SYMLINK = hasattr(os, "symlink")


class Pip2PiOptionParser(optparse.OptionParser):
    def format_description(self, formatter):
        # Parent implementation reformats all the hard line breaks
        return self.get_description() + "\n"

    def add_index_options(self):
        self.add_option(
            '-n', '--normalize-package-names', dest="normalize_package_names",
            default=None, action="store_true",
            help=dedent("""
                Normalize package names in simple index.
                Ex, 'simple/Django/Django-1.7.tar.gz' will be
                normalized to 'simple/django/Django-1.7.tar.gz'.
                Non-normalized package names are deprecated and
                this option will eventually be enabled by default.
                See also: https://github.com/wolever/pip2pi/issues/37
            """))
        self.add_option(
            '-N', '--no-normalize-package-names', dest="normalize_package_names",
            action="store_false")
        self.add_option(
            '-s', '--symlink', dest="use_symlink",
            default=OS_HAS_SYMLINK, action="store_true",
            help=dedent("""
                Use symlinks in PACKAGE_DIR/simple/ rather than copying files.
                Default: %default
            """))
        self.add_option(
            '-S', '--no-symlink', dest="use_symlink", action="store_false")

    def _process_args(self, largs, rargs, values):
        """
        An unknown option pass-through implementation of OptionParser.

        When unknown arguments are encountered, bundle with largs and try again,
        until rargs is depleted.  

        sys.exit(status) will still be called if a known argument is passed
        incorrectly (e.g. missing arguments or bad argument types, etc.)        

        From http://stackoverflow.com/a/9307174/6364
        """
        while rargs:
            try:
                optparse.OptionParser._process_args(self, largs, rargs, values)
            except (optparse.BadOptionError, optparse.AmbiguousOptionError) as e:
                largs.append(e.opt_str)


def dir2pi(argv=sys.argv, use_symlink=None):
    parser = Pip2PiOptionParser(
        usage="usage: %prog PACKAGE_DIR",
        description=dedent("""
            Creates the directory PACKAGE_DIR/simple/ and populates it with the
            directory structure required to use with pip's --index-url.

            Assumes that PACKAGE_DIR contains a bunch of archives named
            'package-name-version.ext' (ex 'foo-2.1.tar.gz' or
            'foo-bar-1.3rc1.bz2').

            This makes the most sense if PACKAGE_DIR is somewhere inside a
            webserver's htdocs directory.

            For example:

                $ ls packages/
                foo-1.2.tar.gz
                $ dir2pi packages/
                $ find packages/
                packages/
                packages/foo-1.2.tar.gz
                packages/simple/
                packages/simple/foo/
                packages/simple/foo/index.html
                packages/simple/foo/foo-1.2.tar.gz
        """))

    if use_symlink is not None:
        warnings.warn("dir2pi(use_symlink=...) is deprecated", stacklevel=1)

    parser.add_index_options()

    option, argv = parser.parse_args(argv)
    if len(argv) != 2:
        parser.print_help()
        parser.exit()
    return _dir2pi(option, argv)

def _dir2pi(option, argv):
    pkgdir = argv[1]
    if not os.path.isdir(pkgdir):
        raise ValueError("no such directory: %r" %(pkgdir, ))
    pkgdirpath = lambda *x: os.path.join(pkgdir, *x)

    shutil.rmtree(pkgdirpath("simple"), ignore_errors=True)
    os.mkdir(pkgdirpath("simple"))
    pkg_index = ("<html><head><title>Simple Index</title>"
                 "<meta name='api-version' value='2' /></head><body>\n")

    warn_normalized_pkg_names = []

    for file in os.listdir(pkgdir):
        pkg_filepath = os.path.join(pkgdir, file)
        if not os.path.isfile(pkg_filepath):
            continue
        pkg_basename = os.path.basename(file)
        if pkg_basename.startswith("."):
            continue
        pkg_name, pkg_rest = file_to_package(pkg_basename, pkgdir)

        pkg_dir_name = pkg_name
        if option.normalize_package_names:
            pkg_dir_name = pkg_dir_name.lower()
        elif pkg_dir_name != pkg_dir_name.lower():
            if option.normalize_package_names is None:
                warn_normalized_pkg_names.append(pkg_name)
        pkg_dir = pkgdirpath("simple", pkg_dir_name)
        if not os.path.exists(pkg_dir):
            os.mkdir(pkg_dir)
        pkg_new_basename = "-".join([pkg_name, pkg_rest])
        symlink_target = os.path.join(pkg_dir, pkg_new_basename)
        symlink_source = os.path.join("../../", pkg_basename)
        if option.use_symlink and OS_HAS_SYMLINK:
            os.symlink(symlink_source, symlink_target)
        else:
            shutil.copy2(pkg_filepath, symlink_target)
        pkg_index += "<a href='%s/'>%s</a><br />\n" %(
            cgi.escape(pkg_dir_name),
            cgi.escape(pkg_name),
        )
        with open(os.path.join(pkg_dir, "index.html"), "a") as fp:
            fp.write("<a href='%(name)s'>%(name)s</a><br />\n" %{
                "name": cgi.escape(pkg_new_basename),
            })
    pkg_index += "</body></html>\n"
    with open(pkgdirpath("simple/index.html"), "w") as fp:
        fp.write(pkg_index)

    if warn_normalized_pkg_names:
        warnings.warn(dedent("""
            \n
            WARNING: Non-normalized packages encountered: %s.\n
            Please consider passing `--normalize-package-names` and verifying
            that your environment does not break, as package names will
            eventually be normalized by default. Silence this warning by
            passing `--no-normalized-package-names`.\n
            See also: https://github.com/wolever/pip2pi/issues/37\n
            _
        """ %(", ".join(warn_normalized_pkg_names), )), stacklevel=0)

    return 0

def globall(globs):
    result = []
    for g in globs:
        result.extend(glob.glob(g))
    return result

@maintain_cwd
def pip2tgz(argv=sys.argv):
    glob_exts = ['*.whl', '*.tgz', '*.gz']
    parser = Pip2PiOptionParser(
        usage="usage: %prog OUTPUT_DIRECTORY [PIP_OPTIONS] PACKAGES ...",
        description=dedent("""
            Where PACKAGES are any names accepted by pip (ex, `foo`,
            `foo==1.2`, `-r requirements.txt`), and [PIP_OPTIONS] can be any
            options accepted by `pip install -d`.

            pip2tgz will download all packages required to install PACKAGES and
            save them to sanely-named tarballs or wheel files in OUTPUT_DIRECTORY.

            For example:

                $ pip2tgz /var/www/packages/ -r requirements.txt foo==1.2 baz/
                $ pip2tgz /var/www/packages/ \\
                    --no-use-wheel \\
                    --index-url https://example.com/simple \\
                    bar==3.1
        """))

    option, argv = parser.parse_args(argv)
    if len(argv) < 3:
        parser.print_help()
        parser.exit()

    outdir = os.path.abspath(argv[1])
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    full_glob_paths = [
        os.path.join(outdir, g) for g in glob_exts
    ]
    pkg_file_set = lambda: set(globall(full_glob_paths))
    old_pkgs = pkg_file_set()

    pip_run_command(['install', '-d', outdir] + argv[2:])

    os.chdir(outdir)
    new_pkgs = pkg_file_set() - old_pkgs
    new_wheels = [ f for f in new_pkgs if f.endswith(".whl") ]
    res = handle_new_wheels(outdir, new_wheels)
    if res:
        return res

    num_pkgs = len(pkg_file_set() - old_pkgs)
    print("\nDone. %s new archives currently saved in %r." %(num_pkgs, argv[1]))
    return 0


def handle_new_wheels(outdir, new_wheels):
    """ Makes sure that, if wheel files are downloaded, their dependencies are
        correctly handled.

        This is necessary because ``pip install -d ...`` was broken
        pre-1.5.3[0].

        [0]: https://github.com/pypa/pip/issues/1617
        """
    if not new_wheels:
        return 0

    pip_version = pip_get_version()
    if pip_version >= (1, 5, 3):
        return 0

    print("")
    print("!" * 80)

    if not has_wheel:
        warn_wheel()
        # Remove the wheel files so that they will be re-downloaded and
        # their dependencies installed next time around
        for f in new_wheels:
            os.unlink(f)
        return 1

    print(dedent("""
        WARNING: Your version of pip (%s) doesn't correctly support wheel
        files. I'll do my best to work around that for now, but if possible
        you should upgrade to at least 1.5.3.
    """)) %(pip_version, )

    print("!" * 80)
    print

    for new_pkg in new_wheels:
        pkg_file_basedir = os.path.abspath(os.path.dirname(new_pkg))
        pkg_name, _ = file_to_package(new_pkg)
        pip_run_command([
            '-q', 'wheel', '-w', outdir,
            '--find-links', pkg_file_basedir,
            pkg_name,
        ])

WINDOWS_PATH_RE = re.compile(r"^[A-Za-z]:\\")

def is_remote_target(target):
    return ":" in target and not WINDOWS_PATH_RE.match(target)


def pip2pi(argv=sys.argv):
    parser = Pip2PiOptionParser(
        usage="usage: %prog TARGET [PIP_OPTIONS] PACKAGES ...",
        description=dedent("""
            Adds packages PACKAGES to PyPI-compatible package index at TARGET.

            If TARGET contains ':' it will be treated as a remote path. The
            package index will be built locally and rsync will be used to copy
            it to the remote host.

            PIP_OPTIONS can be any options accepted by `pip install -d`, like
            `--index-url` or `--no-use-wheel`.

            For example, to create a remote index:

                $ pip2pi example.com:/var/www/packages/ -r requirements.txt

            To create a local index:

                $ pip2pi ~/Sites/packages/ foo==1.2

            To pass arguments to pip:

                $ pip2pi ~/Sites/packages/ \\
                    --no-use-wheel \\
                    --index-url https://example.com/simple \\
                    -r requirements-base.txt \\
                    -r requirements-dev.txt \\
                    bar==3.1

        """))
    parser.add_index_options()

    option, argv = parser.parse_args(argv)
    if len(argv) < 3:
        parser.print_help()
        parser.exit()

    target = argv[1]
    pip_argv = argv[2:]
    if is_remote_target(target):
        is_remote = True
        working_dir = tempfile.mkdtemp(prefix="pip2pi-working-dir")
        atexit.register(lambda: shutil.rmtree(working_dir))
    else:
        is_remote = False
        working_dir = os.path.abspath(target)

    subcmd_argv = [argv[0], working_dir] + pip_argv
    res = pip2tgz(subcmd_argv)
    if res:
        print("pip2tgz returned an error; aborting.")
        return res

    res = _dir2pi(option, subcmd_argv)
    if res:
        print("dir2pi returned an error; aborting.")
        return res

    if is_remote:
        print("copying temporary index at %r to %r..." %(working_dir, target))
        check_call([
            "rsync",
            "--recursive", "--progress", "--links",
            working_dir + "/", target + "/",
        ])
    return 0
