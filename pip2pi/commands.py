import os
import sys
import shutil
import textwrap
from subprocess import check_call

def dedent(text):
    return textwrap.dedent(text)

def file_to_package(file):
    """ Returns the package name for a given file.

        >>> file_to_package("foo-1.2.3_rc1.tar.gz")
        ('foo', '1.2.3-rc1.tar.gz')
        >>> file_to_package("foo-bar-1.2.tgz")
        ('foo-bar', '1.2.tgz')
        >>> """
    split = file.rsplit("-", 1)
    if len(split) != 2:
        msg = ("unexpected file name: %r (not in "
               "'package-name-version.xxx' format)") %(file, )
        raise ValueError(msg)
    return (split[0], split[1].replace("_", "-"))

def dir2pypi():
    if len(sys.argv) != 2:
        print dedent("""
            usage: %s PACKAGE_DIR

            Creates the directory PACKAGE_DIR/simple/ and populates it with the
            directory structure required to use with pip's --index-url.
            
            Assumes that PACKAGE_DIR contains a bunch of archives named
            'package-name-version.ext' (ex 'foo-2.1.tar.gz' or
            'foo-bar-1.3rc1.bz2').
            
            This makes the most sense if PACKAGE_DIR is somewhere inside a
            webserver's inside htdocs directory.
        """ %(sys.argv[0], ) )
        sys.exit(1)
    pkgdir = sys.argv[1]
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
        pkg_name, pkg_rest = file_to_package(pkg_basename)
        pkg_dir = pkgdirpath("simple", pkg_name)
        if not os.path.exists(pkg_dir):
            os.mkdir(pkg_dir)
        pkg_new_basename = "-".join([pkg_name, pkg_rest])
        os.link(pkg_filepath, os.path.join(pkg_dir, pkg_new_basename))


def pip2tgz():
    if len(sys.argv) < 3:
        print dedent("""
            usage: %s OUTPUT_DIRECTORY PACKAGE_NAMES

            Where PACKAGE_NAMES are any names accepted by pip (ex, `foo`,
            `foo==1.2`, `-r requirements.txt`).
            
            %s will download all packages required to install PACKAGE_NAMES and
            save them to sanely-named tarballs in OUTPUT_DIRECTORY.
        """ %(sys.argv[0], sys.argv[0]))
        sys.exit(1)

    outdir = os.path.abspath(sys.argv[1])
    if not os.path.exists(outdir):
        os.path.mkdir(outdir)

    tempdir = os.path.join(outdir, "_pip2tgz_temp")
    if os.path.exists(tempdir):
        shutil.rmtree(tempdir)
    os.mkdir(tempdir)

    bundle_zip = os.path.join(tempdir, "bundle.zip")
    check_call(["pip", "bundle", "-b", tempdir, bundle_zip] + sys.argv[2:])

    os.chdir(tempdir)
    check_call(["unzip", "bundle.zip", "pip-manifest.txt"])

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
        old_input_dir = pkg
        new_input_dir = "%s-%s" %(pkg, version)
        os.rename(old_input_dir, new_input_dir)
        output_name = os.path.join("..", new_input_dir + ".tar.gz")
        check_call(["tar", "-czvf", output_name, new_input_dir])

    os.chdir(outdir)
    shutil.rmtree(tempdir)
