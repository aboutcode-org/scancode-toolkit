#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from commoncode.testcase import FileBasedTesting

import packagedcode
from packagedcode import freebsd
from packagedcode import maven
from packagedcode import npm
from packagedcode import cargo
from packagedcode import opam
from packagedcode import phpcomposer
from packagedcode import rpm
from packagedcode.recognize import recognize_packages
from packagedcode import nuget


class TestRecognize(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_recognize_packages_deb(self):
        test_file = self.get_test_loc('archives/adduser_3.112ubuntu1_all.deb')
        packages = recognize_packages(test_file)
        assert packages
        assert isinstance(packages[0], packagedcode.debian.DebianPackage)

    def test_recognize_packages_rpm(self):
        test_file = self.get_test_loc('archives/alfandega-2.2-2.rh80.src.rpm')
        packages = recognize_packages(test_file)
        assert packages
        assert isinstance(packages[0], rpm.RpmPackage)

    def test_recognize_packages_cab(self):
        test_file = self.get_test_loc('archives/basic.cab')
        packages = recognize_packages(test_file)
        assert packages
        assert isinstance(packages[0], packagedcode.models.CabPackage)

    def test_recognize_packages_rar(self):
        test_file = self.get_test_loc('archives/basic.rar')
        packages = recognize_packages(test_file)
        assert not packages

    def test_recognize_packages_zip(self):
        test_file = self.get_test_loc('archives/myarch-2.3.0.7z')
        packages = recognize_packages(test_file)
        assert not packages

    def test_recognize_packages_gem(self):
        test_file = self.get_test_loc('archives/mysmallidea-address_standardization-0.4.1.gem')
        packages = recognize_packages(test_file)
        assert packages
        assert isinstance(packages[0], packagedcode.rubygems.RubyGem)

    def test_recognize_packages_jar(self):
        test_file = self.get_test_loc('archives/simple.jar')
        packages = recognize_packages(test_file)
        assert packages
        assert isinstance(packages[0], packagedcode.models.JavaJar)

    def test_recognize_packages_iso(self):
        test_file = self.get_test_loc('archives/small.iso')
        packages = recognize_packages(test_file)
        assert packages
        assert isinstance(packages[0], packagedcode.models.IsoImagePackage)

    def test_recognize_packages_does_not_recognize_plain_tarball(self):
        test_file = self.get_test_loc('archives/tarred_bzipped.tar.bz2')
        packages = recognize_packages(test_file)
        assert not packages

    def test_recognize_cpan_manifest_as_plain_package(self):
        test_file = self.get_test_loc('cpan/MANIFEST')
        try:
            recognize_packages(test_file)
            self.fail('Exception not raised')
        except NotImplementedError:
            pass

    def test_recognize_maven_dot_pom(self):
        test_file = self.get_test_loc('m2/aspectj/aspectjrt/1.5.3/aspectjrt-1.5.3.pom')
        packages = recognize_packages(test_file)
        assert packages
        assert isinstance(packages[0], maven.MavenPomPackage)

    def test_recognize_maven_pom_xml(self):
        test_file = self.get_test_loc('maven2/pom.xml')
        packages = recognize_packages(test_file)
        assert packages
        assert isinstance(packages[0], maven.MavenPomPackage)

    def test_recognize_npm(self):
        test_file = self.get_test_loc('recon/package.json')
        packages = recognize_packages(test_file)
        assert packages
        assert isinstance(packages[0], npm.NpmPackage)

    def test_recognize_cargo(self):
        test_file = self.get_test_loc('recon/Cargo.toml')
        packages = recognize_packages(test_file)
        assert packages
        assert isinstance(packages[0], cargo.RustCargoCrate)

    def test_recognize_opam(self):
        test_file = self.get_test_loc('recon/opam')
        packages = recognize_packages(test_file)
        assert packages
        assert isinstance(packages[0], opam.OpamPackage)

    def test_recognize_opam1(self):
        test_file = self.get_test_loc('recon/base.opam')
        packages = recognize_packages(test_file)
        assert packages
        assert isinstance(packages[0], opam.OpamPackage)

    def test_recognize_composer(self):
        test_file = self.get_test_loc('recon/composer.json')
        packages = recognize_packages(test_file)
        assert packages
        assert isinstance(packages[0], phpcomposer.PHPComposerPackage)

    def test_recognize_freebsd(self):
        test_file = self.get_test_loc('freebsd/multi_license/+COMPACT_MANIFEST')
        packages = recognize_packages(test_file)
        assert packages
        assert isinstance(packages[0], freebsd.FreeBSDPackage)

    def test_recognize_nuget(self):
        test_file = self.get_test_loc('recon/bootstrap.nuspec')
        packages = recognize_packages(test_file)
        assert packages
        assert isinstance(packages[0], nuget.NugetPackage)
