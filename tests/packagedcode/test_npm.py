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

import os.path

from packagedcode import npm

from packages_test_utils import PackageTester
import schematics


class TestNpm(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_person(self):
        test = 'Isaac Z. Schlueter <i@izs.me> (http://blog.izs.me)'
        assert ('Isaac Z. Schlueter', 'i@izs.me' , 'http://blog.izs.me') == npm.parse_person(test)

    def test_parse_person2(self):
        test = 'Isaac Z. Schlueter <i@izs.me>'
        assert ('Isaac Z. Schlueter', 'i@izs.me' , None) == npm.parse_person(test)

    def test_parse_person3(self):
        test = 'Isaac Z. Schlueter  (http://blog.izs.me)'
        assert ('Isaac Z. Schlueter', None , 'http://blog.izs.me') == npm.parse_person(test)

    def test_parse_person4(self):
        test = 'Isaac Z. Schlueter'
        assert ('Isaac Z. Schlueter', None , None) == npm.parse_person(test)

    def test_parse_person5(self):
        test = '<i@izs.me> (http://blog.izs.me)'
        assert ('<i@izs.me> (http://blog.izs.me)', None, None) == npm.parse_person(test)

    def test_parse_person_dict(self):
        test = {'name': 'Isaac Z. Schlueter'}
        assert ('Isaac Z. Schlueter', None, None) == npm.parse_person(test)

    def test_parse_person_dict2(self):
        test = {'email': 'me@this.com'}
        assert (None, 'me@this.com', None) == npm.parse_person(test)

    def test_parse_person_dict3(self):
        test = {'url': 'http://example.com'}
        assert (None, None, 'http://example.com') == npm.parse_person(test)

    def test_parse_person_dict4(self):
        test = {'name': 'Isaac Z. Schlueter',
                'email': 'me@this.com',
                'url': 'http://example.com'}
        assert ('Isaac Z. Schlueter', 'me@this.com' , 'http://example.com') == npm.parse_person(test)

    def test_parse_package_json_from_tarball_with_deps(self):
        test_file = self.get_test_loc('npm/from_tarball/package.json')
        expected_loc = self.get_test_loc('npm/from_tarball/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False, fix_locations=False)
        package.validate()

    def test_parse_basic(self):
        test_file = self.get_test_loc('npm/basic/package.json')
        expected_loc = self.get_test_loc('npm/basic/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False, fix_locations=False)
        package.validate()

    def test_parse_invalid_json(self):
        test_file = self.get_test_loc('npm/invalid/package.json')
        try:
            npm.parse(test_file)
        except ValueError, e:
            assert 'No JSON object could be decoded' in str(e)

    def test_parse_as_installed(self):
        test_file = self.get_test_loc('npm/as_installed/package.json')
        expected_loc = self.get_test_loc('npm/as_installed/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False, fix_locations=False)
        try:
            package.validate()
        except schematics.models.ModelValidationError:
            pass

    def test_parse_nodep(self):
        test_file = self.get_test_loc('npm/nodep/package.json')
        expected_loc = self.get_test_loc('npm/nodep/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False, fix_locations=False)
        package.validate()

    def test_parse_from_npmjs(self):
        test_file = self.get_test_loc('npm/from_npmjs/package.json')
        expected_loc = self.get_test_loc('npm/from_npmjs/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False, fix_locations=False)
        try:
            package.validate()
        except schematics.models.ModelValidationError:
            pass

    def test_parse_from_uri_vcs(self):
        test_file = self.get_test_loc('npm/uri_vcs/package.json')
        expected_loc = self.get_test_loc('npm/uri_vcs/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False, fix_locations=False)
        package.validate()

    def test_parse_from_urls_dict_legacy_is_ignored(self):
        test_file = self.get_test_loc('npm/urls_dict/package.json')
        expected_loc = self.get_test_loc('npm/urls_dict/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False, fix_locations=False)
        package.validate()

    def test_parse_does_not_crash_if_partial_repo_url(self):
        test_file = self.get_test_loc('npm/repo_url/package.json')
        expected_loc = self.get_test_loc('npm/repo_url/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False, fix_locations=False)
        package.validate()

    def test_parse_scoped_package_1(self):
        test_file = self.get_test_loc('npm/scoped1/package.json')
        expected_loc = self.get_test_loc('npm/scoped1/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False, fix_locations=False)
        package.validate()

    def test_parse_scoped_package_2(self):
        test_file = self.get_test_loc('npm/scoped2/package.json')
        expected_loc = self.get_test_loc('npm/scoped2/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False, fix_locations=False)
        package.validate()
