#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict
import os
from unittest.case import skipIf
from unittest.case import expectedFailure

from commoncode.system import on_windows
from packagedcode.models import DependentPackage
from packagedcode import pypi
from packages_test_utils import PackageTester


class TestPyPi(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse(self):
        test_file = self.get_test_loc('pypi/setup.py/setup.py')
        package = pypi.parse(test_file)
        assert 'scancode-toolkit' == package.name
        assert '1.5.0' == package.version
        assert 'ScanCode' == package.parties[0].name
        assert ('ScanCode is a tool to scan code for license, '
                'copyright and other interesting facts.') == package.description
        assert 'https://github.com/nexB/scancode-toolkit' == package.homepage_url

    def test_parse_metadata(self):
        test_folder = self.get_test_loc('pypi')
        test_file = os.path.join(test_folder, 'metadata.json')
        package = pypi.parse_metadata(test_file)
        assert 'six' == package.name
        assert '1.10.0' == package.version
        assert 'Python 2 and 3 compatibility utilities' == package.description
        assert 'MIT' in package.declared_license['license']
        assert ['License :: OSI Approved :: MIT License'] == package.declared_license['classifiers']
        expected_classifiers = [
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Intended Audience :: Developers",
            "Topic :: Software Development :: Libraries",
            "Topic :: Utilities"
        ]
        assert expected_classifiers == package.keywords
        expected = [
            OrderedDict([
                ('type', u'person'), ('role', u'contact'),
                ('name', u'Benjamin Peterson'), ('email', None), ('url', None)])
        ]
        assert expected == [p.to_dict() for p in package.parties]
        assert 'http://pypi.python.org/pypi/six/' == package.homepage_url

    def test_parse_pkg_info(self):
        test_file = self.get_test_loc('pypi/PKG-INFO')
        package = pypi.parse_pkg_info(test_file)
        assert 'TicketImport' == package.name
        assert '0.7a' == package.version
        assert 'Import CSV and Excel files' == package.description
        assert 'BSD' in package.declared_license
        assert 'http://nexb.com' == package.homepage_url
        expected = [OrderedDict([('type', u'person'), ('role', u''), ('name', u'Francois Granade'), ('email', None), ('url', None)])]
        assert expected == [p.to_dict() for p in package.parties]

    @skipIf(on_windows, 'somehow this fails on Windows')
    def test_parse_setup_py_arpy(self):
        test_file = self.get_test_loc('pypi/setup.py/arpy_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/arpy_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_boolean2_py(self):
        test_file = self.get_test_loc('pypi/setup.py/boolean2_py_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/boolean2_py_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_container_check(self):
        test_file = self.get_test_loc('pypi/setup.py/container_check_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/container_check_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_fb303_py(self):
        test_file = self.get_test_loc('pypi/setup.py/fb303_py_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/fb303_py_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_frell_src(self):
        # setup.py is a temaplte with @vars
        test_file = self.get_test_loc('pypi/setup.py/frell_src_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/frell_src_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_gyp(self):
        test_file = self.get_test_loc('pypi/setup.py/gyp_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/gyp_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_interlap(self):
        test_file = self.get_test_loc('pypi/setup.py/interlap_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/interlap_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_mb(self):
        test_file = self.get_test_loc('pypi/setup.py/mb_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/mb_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_ntfs(self):
        test_file = self.get_test_loc('pypi/setup.py/ntfs_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/ntfs_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_nvchecker(self):
        test_file = self.get_test_loc('pypi/setup.py/nvchecker_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/nvchecker_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_oi_agents_common_code(self):
        test_file = self.get_test_loc('pypi/setup.py/oi_agents_common_code_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/oi_agents_common_code_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_packageurl_python(self):
        test_file = self.get_test_loc('pypi/setup.py/packageurl_python_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/packageurl_python_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_pipdeptree(self):
        test_file = self.get_test_loc('pypi/setup.py/pipdeptree_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/pipdeptree_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    @expectedFailure
    def test_parse_setup_py_pluggy(self):
        test_file = self.get_test_loc('pypi/setup.py/pluggy_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/pluggy_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_pydep(self):
        test_file = self.get_test_loc('pypi/setup.py/pydep_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/pydep_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    @expectedFailure
    def test_parse_setup_py_pygtrie(self):
        # this uses a kwargs dict
        test_file = self.get_test_loc('pypi/setup.py/pygtrie_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/pygtrie_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_pyrpm_2(self):
        test_file = self.get_test_loc('pypi/setup.py/pyrpm_2_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/pyrpm_2_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_python_publicsuffix(self):
        test_file = self.get_test_loc('pypi/setup.py/python_publicsuffix_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/python_publicsuffix_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_repology_py_libversion(self):
        test_file = self.get_test_loc('pypi/setup.py/repology_py_libversion_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/repology_py_libversion_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_saneyaml(self):
        test_file = self.get_test_loc('pypi/setup.py/saneyaml_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/saneyaml_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py(self):
        test_file = self.get_test_loc('pypi/setup.py/setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_setuppycheck(self):
        test_file = self.get_test_loc('pypi/setup.py/setuppycheck_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/setuppycheck_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_url_py(self):
        test_file = self.get_test_loc('pypi/setup.py/url_py_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/url_py_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_venv(self):
        test_file = self.get_test_loc('pypi/setup.py/venv_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/venv_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_xmltodict(self):
        test_file = self.get_test_loc('pypi/setup.py/xmltodict_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/xmltodict_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_pkginfo_parse_with_unpackaged_source(self):
        test_file = self.get_test_loc('pypi')
        package = pypi.parse_unpackaged_source(test_file)
        expected_loc = self.get_test_loc('pypi/unpackage_source_parser-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_pkginfo_parse_with_unpackaged_source_with_parse_function(self):
        test_file = self.get_test_loc('pypi')
        package = pypi.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpackage_source_parser-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_pkginfo_parse_with_wheelfile(self):
        test_file = self.get_test_loc('pypi/wheel/atomicwrites-1.2.1-py2.py3-none-any.whl')
        package = pypi.parse_wheel(test_file)
        expected_loc = self.get_test_loc('pypi/wheel/parse-wheel-expected.json')
        self.check_package(package, expected_loc, regen=False)


    def test_pkginfo_parse_with_wheelfile_with_parse_function(self):
        test_file = self.get_test_loc('pypi/wheel/atomicwrites-1.2.1-py2.py3-none-any.whl')
        package = pypi.parse(test_file)
        expected_loc = self.get_test_loc('pypi/wheel/parse-wheel-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_with_dparse(self):
        test_file = self.get_test_loc('pypi/dparse/requirements.txt')
        dependencies = pypi.parse_with_dparse(test_file)
        assert [DependentPackage(purl=u'pkg:pypi/lxml', requirement='==3.4.4', scope='dependencies'),
                DependentPackage(purl=u'pkg:pypi/requests', requirement='==2.7.0', scope='dependencies')] == dependencies
