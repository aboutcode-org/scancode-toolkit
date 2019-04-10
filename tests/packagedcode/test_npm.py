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

import os.path

from packagedcode import npm

from packages_test_utils import PackageTester


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
        assert (None, u'i@izs.me', u'http://blog.izs.me') == npm.parse_person(test)

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

    def test_parse_as_installed(self):
        test_file = self.get_test_loc('npm/as_installed/package.json')
        expected_loc = self.get_test_loc('npm/as_installed/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_authors_list_dicts(self):
        # See: https://github.com/csscomb/grunt-csscomb/blob/master/package.json
        test_file = self.get_test_loc('npm/authors_list_dicts/package.json')
        expected_loc = self.get_test_loc('npm/authors_list_dicts/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_authors_list_strings(self):
        # See: https://github.com/chenglou/react-motion/blob/master/package.json
        test_file = self.get_test_loc('npm/authors_list_strings/package.json')
        expected_loc = self.get_test_loc('npm/authors_list_strings/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_authors_list_strings2(self):
        # See: https://github.com/gomfunkel/node-exif/blob/master/package.json
        test_file = self.get_test_loc('npm/authors_list_strings2/package.json')
        expected_loc = self.get_test_loc('npm/authors_list_strings2/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_basic(self):
        test_file = self.get_test_loc('npm/basic/package.json')
        expected_loc = self.get_test_loc('npm/basic/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_bundleddeps(self):
        test_file = self.get_test_loc('npm/bundledDeps/package.json')
        expected_loc = self.get_test_loc('npm/bundledDeps/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_faulty_npm(self):
        test_file = self.get_test_loc('npm/casepath/package.json')
        expected_loc = self.get_test_loc('npm/casepath/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_legacy_licenses(self):
        test_file = self.get_test_loc('npm/chartist/package.json')
        expected_loc = self.get_test_loc('npm/chartist/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_from_npmjs(self):
        test_file = self.get_test_loc('npm/from_npmjs/package.json')
        expected_loc = self.get_test_loc('npm/from_npmjs/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_package_json_from_tarball_with_deps(self):
        test_file = self.get_test_loc('npm/from_tarball/package.json')
        expected_loc = self.get_test_loc('npm/from_tarball/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_invalid_json(self):
        test_file = self.get_test_loc('npm/invalid/package.json')
        try:
            npm.parse(test_file)
        except ValueError as e:
            assert 'No JSON object could be decoded' in str(e)

    def test_parse_keywords(self):
        test_file = self.get_test_loc('npm/keywords/package.json')
        expected_loc = self.get_test_loc('npm/keywords/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_legacy_licenses_as_dict(self):
        test_file = self.get_test_loc('npm/legacy_license_dict/package.json')
        expected_loc = self.get_test_loc('npm/legacy_license_dict/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_nodep(self):
        test_file = self.get_test_loc('npm/nodep/package.json')
        expected_loc = self.get_test_loc('npm/nodep/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_does_not_crash_if_partial_repo_url(self):
        test_file = self.get_test_loc('npm/repo_url/package.json')
        expected_loc = self.get_test_loc('npm/repo_url/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_scoped_package_1(self):
        test_file = self.get_test_loc('npm/scoped1/package.json')
        expected_loc = self.get_test_loc('npm/scoped1/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_scoped_package_2(self):
        test_file = self.get_test_loc('npm/scoped2/package.json')
        expected_loc = self.get_test_loc('npm/scoped2/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_from_npm_authors_with_email_list(self):
        # See: sequelize
        test_file = self.get_test_loc('npm/sequelize/package.json')
        expected_loc = self.get_test_loc('npm/sequelize/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_from_urls_dict_legacy_is_ignored(self):
        test_file = self.get_test_loc('npm/urls_dict/package.json')
        expected_loc = self.get_test_loc('npm/urls_dict/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_from_uri_vcs(self):
        test_file = self.get_test_loc('npm/uri_vcs/package.json')
        expected_loc = self.get_test_loc('npm/uri_vcs/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_registry_old_format(self):
        test_file = self.get_test_loc('npm/old_registry/package.json')
        expected_loc = self.get_test_loc('npm/old_registry/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_with_homepage_as_list(self):
        test_file = self.get_test_loc('npm/homepage-as-list/package.json')
        expected_loc = self.get_test_loc('npm/homepage-as-list/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_with_invalid_dep(self):
        test_file = self.get_test_loc('npm/invalid-dep/package.json')
        expected_loc = self.get_test_loc('npm/invalid-dep/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_utils_merge_1_0_0(self):
        test_file = self.get_test_loc('npm/utils-merge-1.0.0/package.json')
        expected_loc = self.get_test_loc(
            'npm/utils-merge-1.0.0/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_mime_1_3_4(self):
        test_file = self.get_test_loc('npm/mime-1.3.4/package.json')
        expected_loc = self.get_test_loc(
            'npm/mime-1.3.4/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_express_jwt_3_4_0(self):
        test_file = self.get_test_loc('npm/express-jwt-3.4.0/package.json')
        expected_loc = self.get_test_loc(
            'npm/express-jwt-3.4.0/package.json.expected')
        package = npm.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_vcs_repository_mapper(self):
        package = MockPackage()
        repo = 'git+git://bitbucket.org/vendor/my-private-repo.git'
        result = npm.vcs_repository_mapper(repo, package)
        assert repo == result.vcs_url

    def test_vcs_repository_mapper_handles_version(self):
        package = MockPackage()
        repo = 'git@bitbucket.org/vendor/my-private-repo.git'
        rev = '213123aefd'
        expected = 'https://bitbucket.org/vendor/my-private-repo.git@213123aefd'
        result = npm.vcs_repository_mapper(repo, package, rev)
        assert expected == result.vcs_url

    def test_vcs_repository_mapper_handles_version_on_gh(self):
        package = MockPackage()
        repo = 'git@github.com/vendor/my-private-repo'
        rev = '213123aefd'
        expected = 'https://github.com/vendor/my-private-repo@213123aefd'
        result = npm.vcs_repository_mapper(repo, package, rev)
        assert expected == result.vcs_url

class MockPackage(object):
    pass
