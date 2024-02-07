import glob
import os

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv, Environment
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    rename
)
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class GetTextConan(ConanFile):
    name = "libgettext"
    description = "An internationalization and localization system for multilingual programs"
    topics = ("gettext", "intl", "libintl", "i18n")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/gettext"
    # Some parts of the project are GPL-3.0-or-later and some are LGPL-2.1-or-later.
    # At this time, only libintl is packaged, which is licensed under the LGPL-2.1-or-later.
    # If you modify this package to include other portions of the library, please configure the license accordingly.
    # The licensing of the project is documented here: https://www.gnu.org/software/gettext/manual/gettext.html#Licenses
    license = "LGPL-2.1-or-later"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threads": ["posix", "solaris", "pth", "windows", "disabled"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        # Handle default value for `threads` in `config_options` method
    }

    @property
    def _is_clang_cl(self):
        return self.settings.os == "Windows" and self.settings.compiler == "clang" and \
               self.settings.compiler.get_safe("runtime")

    @property
    def _gettext_folder(self):
        return "gettext-tools"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

        self.options.threads = {"Solaris": "solaris", "Windows": "windows"}.get(str(self.settings.os), "posix")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libiconv/1.17")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self) or self._is_clang_cl:
            self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

        if not cross_building(self):
            VirtualRunEnv(self).generate(scope="build")

        tc = AutotoolsToolchain(self)
        tc.configure_args += [
            "HELP2MAN=/bin/true",
            "EMACS=no",
            "--disable-nls",
            "--disable-dependency-tracking",
            "--enable-relocatable",
            "--disable-c++",
            "--disable-java",
            "--disable-csharp",
            "--disable-libasprintf",
            "--disable-curses",
            "--disable-threads" if self.options.threads == "disabled" else ("--enable-threads=" + str(self.options.threads)),
            f"--with-libiconv-prefix={unix_path(self, self.dependencies['libiconv'].package_folder)}",
        ]
        if is_msvc(self) or self._is_clang_cl:
            target = None
            if self.settings.arch == "x86_64":
                target = "x86_64-w64-mingw32"
            elif self.settings.arch == "x86":
                target = "i686-w64-mingw32"

            if target is not None:
                tc.configure_args += [f"--host={target}", f"--build={target}"]

            if (str(self.settings.compiler) == "Visual Studio" and Version(self.settings.compiler.version) >= "12") or \
               (str(self.settings.compiler) == "msvc" and Version(self.settings.compiler.version) >= "180"):
                tc.extra_cflags += ["-FS"]
        tc.make_args += ["-C", "intl"]
        env = tc.environment()
        if is_msvc(self) or self._is_clang_cl:
            def programs():
                rc = None
                if self.settings.arch == "x86_64":
                    rc = "windres --target=pe-x86-64"
                elif self.settings.arch == "x86":
                    rc = "windres --target=pe-i386"
                if self._is_clang_cl:
                    return os.environ.get("CC", "clang-cl"), os.environ.get("AR", "llvm-lib"), os.environ.get("LD", "lld-link"), rc
                if is_msvc(self):
                    return "cl -nologo", "lib", "link", rc

            compile_wrapper = unix_path(self, self.conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, self.conf.get("user.automake:lib-wrapper", check_type=str))
            cc, ar, link, rc = programs()
            env.define("CC", f"{compile_wrapper} {cc}")
            env.define("CXX", f"{compile_wrapper} {cc}")
            env.define("LD", link)
            env.define("AR", f"{ar_wrapper} {ar}")
            env.define("NM", "dumpbin -symbols")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            if rc is not None:
                env.define("RC", rc)
                env.define("WINDRES", rc)
        tc.generate(env)

        if is_msvc(self) or self._is_clang_cl:
            # Custom AutotoolsDeps for cl like compilers
            # workaround for https://github.com/conan-io/conan/issues/12784
            includedirs = []
            defines = []
            libs = []
            libdirs = []
            linkflags = []
            cxxflags = []
            cflags = []
            for dependency in self.dependencies.values():
                deps_cpp_info = dependency.cpp_info.aggregated_components()
                includedirs.extend(deps_cpp_info.includedirs)
                defines.extend(deps_cpp_info.defines)
                libs.extend(deps_cpp_info.libs + deps_cpp_info.system_libs)
                libdirs.extend(deps_cpp_info.libdirs)
                linkflags.extend(deps_cpp_info.sharedlinkflags + deps_cpp_info.exelinkflags)
                cxxflags.extend(deps_cpp_info.cxxflags)
                cflags.extend(deps_cpp_info.cflags)

            env = Environment()
            env.append("CPPFLAGS", [f"-I{unix_path(self, p)}" for p in includedirs] + [f"-D{d}" for d in defines])
            env.append("_LINK_", [lib if lib.endswith(".lib") else f"{lib}.lib" for lib in libs])
            env.append("LDFLAGS", [f"-L{unix_path(self, p)}" for p in libdirs] + linkflags)
            env.append("CXXFLAGS", cxxflags)
            env.append("CFLAGS", cflags)
            env.vars(self).save_script("conanautotoolsdeps_cl_workaround")
        else:
            deps = AutotoolsDeps(self)
            deps.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure("gettext-runtime")
        autotools.make()

    def package(self):
        dest_lib_dir = os.path.join(self.package_folder, "lib")
        dest_runtime_dir = os.path.join(self.package_folder, "bin")
        dest_include_dir = os.path.join(self.package_folder, "include")
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*gnuintl*.dll", self.build_folder, dest_runtime_dir, keep_path=False)
        copy(self, "*gnuintl*.lib", self.build_folder, dest_lib_dir, keep_path=False)
        copy(self, "*gnuintl*.a", self.build_folder, dest_lib_dir, keep_path=False)
        copy(self, "*gnuintl*.so*", self.build_folder, dest_lib_dir, keep_path=False)
        copy(self, "*gnuintl*.dylib", self.build_folder, dest_lib_dir, keep_path=False)
        copy(self, "*libgnuintl.h", self.build_folder, dest_include_dir, keep_path=False)
        rename(self, os.path.join(dest_include_dir, "libgnuintl.h"), os.path.join(dest_include_dir, "libintl.h"))
        fix_msvc_libname(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "Intl")
        self.cpp_info.set_property("cmake_target_name", "Intl::Intl")
        self.cpp_info.libs = ["gnuintl"]
        if is_apple_os(self):
            self.cpp_info.frameworks.append("CoreFoundation")

        self.cpp_info.names["cmake_find_package"] = "Intl"
        self.cpp_info.names["cmake_find_package_multi"] = "Intl"

def fix_msvc_libname(conanfile, remove_lib_prefix=True):
    """remove lib prefix & change extension to .lib in case of cl like compiler"""
    if not conanfile.settings.get_safe("compiler.runtime"):
        return
    libdirs = getattr(conanfile.cpp.package, "libdirs")
    for libdir in libdirs:
        for ext in [".dll.a", ".dll.lib", ".a"]:
            full_folder = os.path.join(conanfile.package_folder, libdir)
            for filepath in glob.glob(os.path.join(full_folder, f"*{ext}")):
                libname = os.path.basename(filepath)[0:-len(ext)]
                if remove_lib_prefix and libname[0:3] == "lib":
                    libname = libname[3:]
                rename(conanfile, filepath, os.path.join(os.path.dirname(filepath), f"{libname}.lib"))
