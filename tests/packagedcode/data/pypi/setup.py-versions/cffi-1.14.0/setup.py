import sys, os
import subprocess
import errno

# on Windows we give up and always import setuptools early to fix things for us
if sys.platform == "win32":
    import setuptools


sources = ['c/_cffi_backend.c']
libraries = ['ffi']
include_dirs = ['/usr/include/ffi',
                '/usr/include/libffi']    # may be changed by pkg-config
define_macros = []
library_dirs = []
extra_compile_args = []
extra_link_args = []


def _ask_pkg_config(resultlist, option, result_prefix='', sysroot=False):
    pkg_config = os.environ.get('PKG_CONFIG','pkg-config')
    try:
        p = subprocess.Popen([pkg_config, option, 'libffi'],
                             stdout=subprocess.PIPE)
    except OSError as e:
        if e.errno not in [errno.ENOENT, errno.EACCES]:
            raise
    else:
        t = p.stdout.read().decode().strip()
        p.stdout.close()
        if p.wait() == 0:
            res = t.split()
            # '-I/usr/...' -> '/usr/...'
            for x in res:
                assert x.startswith(result_prefix)
            res = [x[len(result_prefix):] for x in res]
            #print 'PKG_CONFIG:', option, res
            #
            sysroot = sysroot and os.environ.get('PKG_CONFIG_SYSROOT_DIR', '')
            if sysroot:
                # old versions of pkg-config don't support this env var,
                # so here we emulate its effect if needed
                res = [path if path.startswith(sysroot)
                            else sysroot + path
                         for path in res]
            #
            resultlist[:] = res

no_compiler_found = False
def no_working_compiler_found():
    sys.stderr.write("""
    No working compiler found, or bogus compiler options passed to
    the compiler from Python's standard "distutils" module.  See
    the error messages above.  Likely, the problem is not related
    to CFFI but generic to the setup.py of any Python package that
    tries to compile C code.  (Hints: on OS/X 10.8, for errors about
    -mno-fused-madd see http://stackoverflow.com/questions/22313407/
    Otherwise, see https://wiki.python.org/moin/CompLangPython or
    the IRC channel #python on irc.freenode.net.)

    Trying to continue anyway.  If you are trying to install CFFI from
    a build done in a different context, you can ignore this warning.
    \n""")
    global no_compiler_found
    no_compiler_found = True

def get_config():
    from distutils.core import Distribution
    from distutils.sysconfig import get_config_vars
    get_config_vars()      # workaround for a bug of distutils, e.g. on OS/X
    config = Distribution().get_command_obj('config')
    return config

def ask_supports_thread():
    config = get_config()
    ok = (sys.platform != 'win32' and
          config.try_compile('__thread int some_threadlocal_variable_42;'))
    if ok:
        define_macros.append(('USE__THREAD', None))
    else:
        ok1 = config.try_compile('int some_regular_variable_42;')
        if not ok1:
            no_working_compiler_found()
        else:
            sys.stderr.write("Note: will not use '__thread' in the C code\n")
            _safe_to_ignore()

def ask_supports_sync_synchronize():
    if sys.platform == 'win32' or no_compiler_found:
        return
    config = get_config()
    ok = config.try_link('int main(void) { __sync_synchronize(); return 0; }')
    if ok:
        define_macros.append(('HAVE_SYNC_SYNCHRONIZE', None))
    else:
        sys.stderr.write("Note: will not use '__sync_synchronize()'"
                         " in the C code\n")
        _safe_to_ignore()

def _safe_to_ignore():
    sys.stderr.write("***** The above error message can be safely ignored.\n\n")

def uses_msvc():
    config = get_config()
    return config.try_compile('#ifndef _MSC_VER\n#error "not MSVC"\n#endif')

def use_pkg_config():
    if sys.platform == 'darwin' and os.path.exists('/usr/local/bin/brew'):
        use_homebrew_for_libffi()

    _ask_pkg_config(include_dirs,       '--cflags-only-I', '-I', sysroot=True)
    _ask_pkg_config(extra_compile_args, '--cflags-only-other')
    _ask_pkg_config(library_dirs,       '--libs-only-L', '-L', sysroot=True)
    _ask_pkg_config(extra_link_args,    '--libs-only-other')
    _ask_pkg_config(libraries,          '--libs-only-l', '-l')

def use_homebrew_for_libffi():
    # We can build by setting:
    # PKG_CONFIG_PATH = $(brew --prefix libffi)/lib/pkgconfig
    with os.popen('brew --prefix libffi') as brew_prefix_cmd:
        prefix = brew_prefix_cmd.read().strip()
    pkgconfig = os.path.join(prefix, 'lib', 'pkgconfig')
    os.environ['PKG_CONFIG_PATH'] = (
        os.environ.get('PKG_CONFIG_PATH', '') + ':' + pkgconfig)


if sys.platform == 'win32' and uses_msvc():
    COMPILE_LIBFFI = 'c/libffi_msvc'    # from the CPython distribution
else:
    COMPILE_LIBFFI = None

if COMPILE_LIBFFI:
    assert os.path.isdir(COMPILE_LIBFFI), "directory not found!"
    include_dirs[:] = [COMPILE_LIBFFI]
    libraries[:] = []
    _filenames = [filename.lower() for filename in os.listdir(COMPILE_LIBFFI)]
    _filenames = [filename for filename in _filenames
                           if filename.endswith('.c')]
    if sys.maxsize > 2**32:
        # 64-bit: unlist win32.c, and add instead win64.obj.  If the obj
        # happens to get outdated at some point in the future, you need to
        # rebuild it manually from win64.asm.
        _filenames.remove('win32.c')
        extra_link_args.append(os.path.join(COMPILE_LIBFFI, 'win64.obj'))
    sources.extend(os.path.join(COMPILE_LIBFFI, filename)
                   for filename in _filenames)
else:
    use_pkg_config()
    ask_supports_thread()
    ask_supports_sync_synchronize()

if 'freebsd' in sys.platform:
    include_dirs.append('/usr/local/include')
    library_dirs.append('/usr/local/lib')

if 'darwin' in sys.platform:
    try:
        p = subprocess.Popen(['xcrun', '--show-sdk-path'],
                             stdout=subprocess.PIPE)
    except OSError as e:
        if e.errno not in [errno.ENOENT, errno.EACCES]:
            raise
    else:
        t = p.stdout.read().decode().strip()
        p.stdout.close()
        if p.wait() == 0:
            include_dirs.append(t + '/usr/include/ffi')



if __name__ == '__main__':
    from setuptools import setup, Distribution, Extension

    class CFFIDistribution(Distribution):
        def has_ext_modules(self):
            # Event if we don't have extension modules (e.g. on PyPy) we want to
            # claim that we do so that wheels get properly tagged as Python
            # specific.  (thanks dstufft!)
            return True

    # On PyPy, cffi is preinstalled and it is not possible, at least for now,
    # to install a different version.  We work around it by making the setup()
    # arguments mostly empty in this case.
    cpython = ('_cffi_backend' not in sys.builtin_module_names)

    setup(
        name='cffi',
        description='Foreign Function Interface for Python calling C code.',
        long_description="""
CFFI
====

Foreign Function Interface for Python calling C code.
Please see the `Documentation <http://cffi.readthedocs.org/>`_.

Contact
-------

`Mailing list <https://groups.google.com/forum/#!forum/python-cffi>`_
""",
        version='1.14.0',
        packages=['cffi'] if cpython else [],
        package_data={'cffi': ['_cffi_include.h', 'parse_c_type.h', 
                               '_embedding.h', '_cffi_errors.h']}
                     if cpython else {},
        zip_safe=False,

        url='http://cffi.readthedocs.org',
        author='Armin Rigo, Maciej Fijalkowski',
        author_email='python-cffi@googlegroups.com',

        license='MIT',

        distclass=CFFIDistribution,
        ext_modules=[Extension(
            name='_cffi_backend',
            include_dirs=include_dirs,
            sources=sources,
            libraries=libraries,
            define_macros=define_macros,
            library_dirs=library_dirs,
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
        )] if cpython else [],

        install_requires=[
            'pycparser' if sys.version_info >= (2, 7) else 'pycparser<2.19',
        ] if cpython else [],

        entry_points = {
            "distutils.setup_keywords": [
                "cffi_modules = cffi.setuptools_ext:cffi_modules",
            ],
        },

        classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'License :: OSI Approved :: MIT License',
        ],
    )
