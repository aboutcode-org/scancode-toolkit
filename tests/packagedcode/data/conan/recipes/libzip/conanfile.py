from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class LibZipConan(ConanFile):
    name = "libzip"
    description = "A C library for reading, creating, and modifying zip archives"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nih-at/libzip"
    license = "BSD-3-Clause"
    topics = ("zip", "zip-archives", "zip-editing")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_bzip2": [True, False],
        "with_lzma": [True, False],
        "with_zstd": [True, False],
        "crypto": [False, "win32", "openssl", "mbedtls"],
        "tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_bzip2": True,
        "with_lzma": True,
        "with_zstd": True,
        "crypto": "openssl",
        "tools": True,
    }

    @property
    def _has_zstd_support(self):
        return Version(self.version) >= "1.8.0"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_zstd_support:
            del self.options.with_zstd
        # Default crypto backend on windows
        if self.settings.os == "Windows":
            self.options.crypto = "win32"

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")

        if self.options.with_bzip2:
            self.requires("bzip2/1.0.8")

        if self.options.with_lzma:
            self.requires("xz_utils/5.4.5")

        if self.options.get_safe("with_zstd"):
            self.requires("zstd/1.5.5")

        if self.options.crypto == "openssl":
            self.requires("openssl/[>=1.1 <4]")
        elif self.options.crypto == "mbedtls":
            self.requires("mbedtls/3.5.0")

    def validate(self):
        if self.options.crypto == "win32" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("Windows is required to use win32 crypto libraries")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TOOLS"] = self.options.tools
        tc.variables["BUILD_REGRESS"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_DOC"] = False
        tc.variables["ENABLE_LZMA"] = self.options.with_lzma
        tc.variables["ENABLE_BZIP2"] = self.options.with_bzip2
        if self._has_zstd_support:
            tc.variables["ENABLE_ZSTD"] = self.options.with_zstd
        tc.variables["ENABLE_COMMONCRYPTO"] = False  # TODO: We need CommonCrypto package
        tc.variables["ENABLE_GNUTLS"] = False  # TODO: We need GnuTLS package
        tc.variables["ENABLE_MBEDTLS"] = self.options.crypto == "mbedtls"
        tc.variables["ENABLE_OPENSSL"] = self.options.crypto == "openssl"
        tc.variables["ENABLE_WINDOWS_CRYPTO"] = self.options.crypto == "win32"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libzip")
        self.cpp_info.set_property("cmake_target_name", "libzip::zip")
        self.cpp_info.set_property("pkg_config_name", "libzip")

        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["_libzip"].libs = ["zip"]
        if self.settings.os == "Windows":
            self.cpp_info.components["_libzip"].system_libs = ["advapi32"]
            if self.options.crypto == "win32":
                self.cpp_info.components["_libzip"].system_libs.append("bcrypt")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "libzip"
        self.cpp_info.names["cmake_find_package_multi"] = "libzip"
        self.cpp_info.components["_libzip"].names["cmake_find_package"] = "zip"
        self.cpp_info.components["_libzip"].names["cmake_find_package_multi"] = "zip"
        self.cpp_info.components["_libzip"].set_property("cmake_target_name", "libzip::zip")
        self.cpp_info.components["_libzip"].set_property("pkg_config_name", "libzip")
        self.cpp_info.components["_libzip"].requires = ["zlib::zlib"]
        if self.options.with_bzip2:
            self.cpp_info.components["_libzip"].requires.append("bzip2::bzip2")
        if self.options.with_lzma:
            self.cpp_info.components["_libzip"].requires.append("xz_utils::xz_utils")
        if self.options.get_safe("with_zstd"):
            self.cpp_info.components["_libzip"].requires.append("zstd::zstd")
        if self.options.crypto == "openssl":
            self.cpp_info.components["_libzip"].requires.append("openssl::crypto")
        elif self.options.crypto == "mbedtls":
            self.cpp_info.components["_libzip"].requires.append("mbedtls::mbedtls")
        if self.options.tools:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
