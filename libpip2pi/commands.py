import os
import sys
import cgi
import shutil
import atexit
import zipfile
import tempfile
import textwrap
from subprocess import check_call

def dedent(text):
    return textwrap.dedent(text.lstrip("\n"))

def file_to_package(file, basedir=None):
    """ Returns the package name for a given file.

        >>> file_to_package("foo-1.2.3_rc1.tar.gz")
        ('foo', '1.2.3-rc1.tar.gz')
        >>> file_to_package("foo-bar-1.2.tgz")
        ('foo-bar', '1.2.tgz')
        >>> """
    split = file.rsplit("-", 1)
    if len(split) != 2:
        msg = "unexpected file name: %r " %(file, )
        msg += "(not in 'pkg-name-version.xxx' format"
        if basedir:
            msg += "; found in directory: %r" %(basedir)
        msg += ")"
        raise ValueError(msg)
    # Note: for various reasions (which I don't 100% remember right now) we
    # need to replace '-' in the version string with '_'. I think this has to
    # do with the way we export the list of files from the PIP manifest, then
    # read them back in somewhere else. It would be cool to fix this at some
    # point.
    return (split[0], split[1].replace("_", "-"))

def dir2pi(argv=sys.argv):
    if len(argv) != 2:
        print dedent("""
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
        """)
        sys.exit(1)
    pkgdir = argv[1]
    if not os.path.isdir(pkgdir):
        raise ValueError("no such directory: %r" %(pkgdir, ))
    pkgdirpath = lambda *x: os.path.join(pkgdir, *x)

    shutil.rmtree(pkgdirpath("simple"), ignore_errors=True)
    os.mkdir(pkgdirpath("simple"))

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
        os.symlink(symlink_source, symlink_target)
        with open(os.path.join(pkg_dir, "index.html"), "a") as fp:
            pkg_new_basename_html = cgi.escape(pkg_new_basename)
            fp.write("<a href='%s'>%s</a><br />\n"
                     %(pkg_new_basename_html, pkg_new_basename_html))


def pip2tgz(argv=sys.argv):
    if len(argv) < 3:
        print dedent("""
            usage: pip2tgz OUTPUT_DIRECTORY PACKAGE_NAME ...

            Where PACKAGE_NAMES are any names accepted by pip (ex, `foo`,
            `foo==1.2`, `-r requirements.txt`).
            
            pip2tgz will download all packages required to install PACKAGE_NAMES and
            save them to sanely-named tarballs in OUTPUT_DIRECTORY.

            For example:
                
                $ pip2tgz /var/www/packages/ -r requirements.txt foo==1.2 baz/
        """)
        sys.exit(1)

    outdir = os.path.abspath(argv[1])
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    tempdir = os.path.join(outdir, "_pip2tgz_temp")
    if os.path.exists(tempdir):
        shutil.rmtree(tempdir)
    os.mkdir(tempdir)

    bundle_zip = os.path.join(tempdir, "bundle.zip")
    build_dir = os.path.join(tempdir, "build")
    check_call(["pip", "bundle", "-b", build_dir, bundle_zip] + argv[2:])

    os.chdir(tempdir)
    if os.path.exists(build_dir):
        zipfile.ZipFile("bundle.zip").extract("pip-manifest.txt")
    else:
        # Older versions of pip delete the "build" directory after they
        # are done with it... So extract the entire bundle.zip
        zipfile.ZipFile("bundle.zip").extractall()

    num_pakages = 0
    for line in open("pip-manifest.txt"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        pkg_version = line.split("==")
        if len(pkg_version) != 2:
            bundle_file = os.path.abspath("pip-manifest.txt")
            raise ValueError("surprising line in %r: %r"
                             %(bundle_file, line, ))
        pkg, version = pkg_version
        version = version.replace("-", "_")
        old_input_dir = os.path.join("build/", pkg)
        new_input_dir = "%s-%s" %(pkg, version)
        os.rename(old_input_dir, new_input_dir)
        output_name = os.path.join("..", new_input_dir + ".tar.gz")
        check_call(["tar", "-czf", output_name, new_input_dir])
        num_pakages += 1

    os.chdir(outdir)
    shutil.rmtree(tempdir)
    print "%s .tar.gz saved to %r" %(num_pakages, argv[1])

def pip2pi(argv=sys.argv):
    if len(argv) < 3:
        print dedent("""
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
        """)
        sys.exit(1)

    target = argv[1]
    pip_packages = argv[2:]
    if ":" in target:
        is_remote = True
        working_dir = tempfile.mkdtemp(prefix="pip2pi-working-dir") 
        atexit.register(lambda: shutil.rmtree(working_dir))
    else:
        is_remote = False
        working_dir = os.path.abspath(target)

    pip2tgz([argv[0], working_dir] + pip_packages)
    dir2pi([argv[0], working_dir])

    if is_remote:
        print "copying temporary index at %r to %r..." %(working_dir, target)
        check_call([
            "rsync",
            "--recursive", "--progress", "--links",
            working_dir + "/", target + "/",
        ])
