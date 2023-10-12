#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from commoncode.testcase import FileBasedTesting

from packagedcode import models
from packagedcode.recognize import recognize_package_data

# TODO: this needs to be updated to use either a full scan of to use parse and assemble


class TestRecognize(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_recognize_package_data_deb(self):
        test_file = self.get_test_loc('archives/adduser_3.112ubuntu1_all.deb')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_package_data_rpm(self):
        test_file = self.get_test_loc('archives/alfandega-2.2-2.rh80.src.rpm')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_package_data_cab(self):
        test_file = self.get_test_loc('archives/basic.cab')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_package_data_rar(self):
        test_file = self.get_test_loc('archives/basic.rar')
        packages = recognize_package_data(test_file)
        assert not packages

    def test_recognize_package_data_zip(self):
        test_file = self.get_test_loc('archives/myarch-2.3.0.7z')
        packages = recognize_package_data(test_file)
        assert not packages

    def test_recognize_package_data_gem(self):
        test_file = self.get_test_loc('archives/mysmallidea-address_standardization-0.4.1.gem')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_package_data_jar(self):
        test_file = self.get_test_loc('archives/simple.jar')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_package_data_iso(self):
        test_file = self.get_test_loc('archives/small.iso')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_package_data_does_not_recognize_plain_tarball(self):
        test_file = self.get_test_loc('archives/tarred_bzipped.tar.bz2')
        packages = recognize_package_data(test_file)
        assert not packages

    def test_recognize_maven_dot_pom(self):
        test_file = self.get_test_loc('m2/aspectj/aspectjrt/1.5.3/aspectjrt-1.5.3.pom')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_maven_pom_xml(self):
        test_file = self.get_test_loc('maven2/pom-generic/pom.xml')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_npm(self):
        test_file = self.get_test_loc('recon/package.json')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_cargo(self):
        test_file = self.get_test_loc('recon/Cargo.toml')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_opam(self):
        test_file = self.get_test_loc('recon/opam')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_opam1(self):
        test_file = self.get_test_loc('recon/base.opam')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_composer(self):
        test_file = self.get_test_loc('recon/composer.json')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_haxe(self):
        test_file = self.get_test_loc('recon/haxelib.json')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_freebsd(self):
        test_file = self.get_test_loc('freebsd/multi_license/+COMPACT_MANIFEST')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_nuget(self):
        test_file = self.get_test_loc('recon/bootstrap.nuspec')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_winexe(self):
        test_file = self.get_test_loc('win_pe/tre4.dll')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_bower(self):
        test_file = self.get_test_loc('bower/basic/bower.json')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_cpan(self):
        test_file = self.get_test_loc('cpan/MANIFEST')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_python2(self):
        test_file = self.get_test_loc('recon/pypi/atomicwrites/atomicwrites-1.2.1-py2.py3-none-any.whl')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_python3(self):
        test_file = self.get_test_loc('recon/pypi/Six/Six.dist-info/METADATA')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_python5(self):
        test_file = self.get_test_loc('recon/pypi/TicketImport/PKG-INFO')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_python6(self):
        test_file = self.get_test_loc('recon/pypi/arpy/setup.py')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_python7(self):
        test_file = self.get_test_loc('recon/pypi/atomicwrites/Pipfile.lock')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_python8(self):
        test_file = self.get_test_loc('recon/pypi/requirements/requirements.txt')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_go_mod(self):
        test_file = self.get_test_loc('golang/gomod/kingpin/go.mod')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_go_sum(self):
        test_file = self.get_test_loc('golang/gosum/sample1/go.sum')
        packages = recognize_package_data(test_file)
        assert packages
        assert isinstance(packages[0], models.PackageData)

    def test_recognize_rpmdb_sqlite(self):
        test_file = self.get_test_loc('rpm/rpmdb.sqlite')
        packages = recognize_package_data(test_file, system=True)
        assert packages
        assert isinstance(packages[0], models.PackageData)
