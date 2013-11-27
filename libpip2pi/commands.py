import os
import sys
import cgi
import shutil
import atexit
import zipfile
import tempfile
import textwrap
import functools
from subprocess import check_call
import pkg_resources
import glob

def dedent(text):
    return textwrap.dedent(text.lstrip("\n"))

def maintain_cwd(f):
    @functools.wraps(f)
    def maintain_cwd_helper(*args, **kwargs):
        orig_dir = os.getcwd()
        try:
            return f(*args, **kwargs)
        finally:
            os.chdir(orig_dir)
    return maintain_cwd_helper

def egg_to_package(file):
    """ Extracts the package name from an egg.

        >>> egg_to_package("PyYAML-3.10-py2.7-macosx-10.7-x86_64.egg")
        ('PyYAML', '3.10-py2.7-macosx-10.7-x86_64.egg')
        >>> egg_to_package("python_ldap-2.3.9-py2.7-macosx-10.3-fat.egg")
        ('python-ldap', '2.3.9-py2.7-macosx-10.3-fat.egg')
    """
    dist = pkg_resources.Distribution.from_location(None, file)
    name = dist.project_name
    return (name, file[len(name)+1:])

def file_to_package(file, basedir=None):
    """ Returns the package name for a given file.

        >>> file_to_package("foo-1.2.3_rc1.tar.gz")
        ('foo', '1.2.3-rc1.tar.gz')
        >>> file_to_package("foo-bar-1.2.tgz")
        ('foo-bar', '1.2.tgz')
        >>> """
    if os.path.splitext(file)[1].lower() == ".egg":
        return egg_to_package(file)
    split = file.rsplit("-", 1)
    if len(split) != 2:
        msg = "unexpected file name: %r " %(file, )
        msg += "(not in 'pkg-name-version.xxx' format"
        if basedir:
            msg += "; found in directory: %r" %(basedir)
        msg += ")"
        raise ValueError(msg)
    return (split[0], pkg_resources.safe_name(split[1]))

def archive_pip_packages(path, package_cmds):
    use_pip_main = False
    try:
        import pip
        pip_dist = pkg_resources.get_distribution('pip')
        version = pip_dist.version

        if version < '1.1':
            raise RuntimeError('pip >= 1.1 required, %s installed' % version)

        use_pip_main = True
    except ImportError:
        print '\n===\nWARNING:\nCannot import `pip` - falling back to using the pip executable.'
        print '(This will be deprecated in a future release.)\n===\n'

    if use_pip_main:
        cmds = ['install', '-d', path]
        cmds.extend(package_cmds)
        pip.main(cmds)
    else:
        check_call(["pip", "install", "-d", path] + package_cmds)

def dir2pi(argv=sys.argv):
    if len(argv) != 2:
        print(dedent("""
            usage: dir2pi PACKAGE_DIR

            Creates the directory PACKAGE_DIR/simple/ and populates it with the
            directory structure required to use with pip's --index-url.

            Assumes that PACKAGE_DIR contains a bunch of archives named
            'package-name-version.ext' (ex 'foo-2.1.tar.gz' or
            'foo-bar-1.3rc1.bz2').

            This makes the most sense if PACKAGE_DIR is somewhere inside a
            webserver's inside htdocs directory.

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
        return 1
    pkgdir = argv[1]
    if not os.path.isdir(pkgdir):
        raise ValueError("no such directory: %r" %(pkgdir, ))
    pkgdirpath = lambda *x: os.path.join(pkgdir, *x)

    shutil.rmtree(pkgdirpath("simple"), ignore_errors=True)
    os.mkdir(pkgdirpath("simple"))
    pkg_index = ("<html><head><title>Simple Index</title>"
                 "<meta name='api-version' value='2' /></head><body>\n")

    for file in os.listdir(pkgdir):
        pkg_filepath = os.path.join(pkgdir, file)
        if not os.path.isfile(pkg_filepath):
            continue
        pkg_basename = os.path.basename(file)
        if pkg_basename.startswith("."):
            continue
        pkg_name, pkg_rest = file_to_package(pkg_basename, pkgdir)
        pkg_dir = pkgdirpath("simple", pkg_name)
        if not os.path.exists(pkg_dir):
            os.mkdir(pkg_dir)
        pkg_new_basename = "-".join([pkg_name, pkg_rest])
        symlink_target = os.path.join(pkg_dir, pkg_new_basename)
        symlink_source = os.path.join("../../", pkg_basename)
        if hasattr(os, "symlink"):
            os.symlink(symlink_source, symlink_target)
        else:
            shutil.copy2(pkg_filepath, symlink_target)
        pkg_name_html = cgi.escape(pkg_name)
        pkg_index += "<a href='{0}/'>{0}</a><br />\n".format(pkg_name_html)
        with open(os.path.join(pkg_dir, "index.html"), "a") as fp:
            pkg_new_basename_html = cgi.escape(pkg_new_basename)
            fp.write("<a href='%s'>%s</a><br />\n"
                     %(pkg_new_basename_html, pkg_new_basename_html))
    pkg_index += "</body></html>\n"
    with open(pkgdirpath("simple/index.html"), "w") as fp:
        fp.write(pkg_index)
    return 0

@maintain_cwd
def pip2tgz(argv=sys.argv):
    if len(argv) < 3:
        print(dedent("""
            usage: pip2tgz OUTPUT_DIRECTORY PACKAGE_NAME ...

            Where PACKAGE_NAMES are any names accepted by pip (ex, `foo`,
            `foo==1.2`, `-r requirements.txt`).

            pip2tgz will download all packages required to install PACKAGE_NAMES and
            save them to sanely-named tarballs in OUTPUT_DIRECTORY.

            For example:

                $ pip2tgz /var/www/packages/ -r requirements.txt foo==1.2 baz/
        """))
        return 1

    outdir = os.path.abspath(argv[1])
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    archive_pip_packages(outdir, argv[2:])
    os.chdir(outdir)
    num_pakages = len(glob.glob('./*.tar.gz'))

    print("%s .tar.gz saved to %r" %(num_pakages, argv[1]))
    return 0

def pip2pi(argv=sys.argv):
    if len(argv) < 3:
        print(dedent("""
            usage: pip2pi TARGET PACKAGE_NAME ...

            Combines pip2tgz and dir2pi, adding PACKAGE_NAME to package index
            TARGET.

            If TARGET contains ':' it will be treated as a remote path. The
            package index will be built locally then rsync will be used to copy
            it to the remote host.

            For example, to create a remote index:

                $ pip2pi example.com:/var/www/packages/ -r requirements.txt

            Or to create a local index:

                $ pip2pi ~/Sites/packages/ foo==1.2
        """))
        return 1

    target = argv[1]
    pip_packages = argv[2:]
    if ":" in target:
        is_remote = True
        working_dir = tempfile.mkdtemp(prefix="pip2pi-working-dir")
        atexit.register(lambda: shutil.rmtree(working_dir))
    else:
        is_remote = False
        working_dir = os.path.abspath(target)

    res = pip2tgz([argv[0], working_dir] + pip_packages)
    if res:
        print("pip2tgz returned an error; aborting.")
        return res

    res = dir2pi([argv[0], working_dir])
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
