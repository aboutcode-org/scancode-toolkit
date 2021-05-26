#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

import pytest

from packagedcode import npm
from commoncode.resource import Codebase
from packages_test_utils import PackageTester


class TestNpm(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_person(self):
        test = 'Isaac Z. Schlueter <i@izs.me> (http://blog.izs.me)'
        assert npm.parse_person(test) == ('Isaac Z. Schlueter', 'i@izs.me' , 'http://blog.izs.me')

    def test_parse_person2(self):
        test = 'Isaac Z. Schlueter <i@izs.me>'
        assert npm.parse_person(test) == ('Isaac Z. Schlueter', 'i@izs.me' , None)

    def test_parse_person3(self):
        test = 'Isaac Z. Schlueter  (http://blog.izs.me)'
        assert npm.parse_person(test) == ('Isaac Z. Schlueter', None , 'http://blog.izs.me')

    def test_parse_person4(self):
        test = 'Isaac Z. Schlueter'
        assert npm.parse_person(test) == ('Isaac Z. Schlueter', None , None)

    def test_parse_person5(self):
        test = '<i@izs.me> (http://blog.izs.me)'
        assert npm.parse_person(test) == (None, u'i@izs.me', u'http://blog.izs.me')

    def test_parse_person_dict(self):
        test = {'name': 'Isaac Z. Schlueter'}
        assert npm.parse_person(test) == ('Isaac Z. Schlueter', None, None)

    def test_parse_person_dict2(self):
        test = {'email': 'me@this.com'}
        assert npm.parse_person(test) == (None, 'me@this.com', None)

    def test_parse_person_dict3(self):
        test = {'url': 'http://example.com'}
        assert npm.parse_person(test) == (None, None, 'http://example.com')

    def test_parse_person_dict4(self):
        test = {'name': 'Isaac Z. Schlueter',
                'email': 'me@this.com',
                'url': 'http://example.com'}
        assert npm.parse_person(test) == ('Isaac Z. Schlueter', 'me@this.com' , 'http://example.com')

    def test_parse_dist_with_string_values(self):
        test_file = self.get_test_loc('npm/dist/package.json')
        expected_loc = self.get_test_loc('npm/dist/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_as_installed(self):
        test_file = self.get_test_loc('npm/as_installed/package.json')
        expected_loc = self.get_test_loc('npm/as_installed/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_authors_list_dicts(self):
        # See: https://github.com/csscomb/grunt-csscomb/blob/master/package.json
        test_file = self.get_test_loc('npm/authors_list_dicts/package.json')
        expected_loc = self.get_test_loc('npm/authors_list_dicts/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_authors_list_strings(self):
        # See: https://github.com/chenglou/react-motion/blob/master/package.json
        test_file = self.get_test_loc('npm/authors_list_strings/package.json')
        expected_loc = self.get_test_loc('npm/authors_list_strings/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_authors_list_strings2(self):
        # See: https://github.com/gomfunkel/node-exif/blob/master/package.json
        test_file = self.get_test_loc('npm/authors_list_strings2/package.json')
        expected_loc = self.get_test_loc('npm/authors_list_strings2/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_basic(self):
        test_file = self.get_test_loc('npm/basic/package.json')
        expected_loc = self.get_test_loc('npm/basic/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_bundleddeps(self):
        test_file = self.get_test_loc('npm/bundledDeps/package.json')
        expected_loc = self.get_test_loc('npm/bundledDeps/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_faulty_npm(self):
        test_file = self.get_test_loc('npm/casepath/package.json')
        expected_loc = self.get_test_loc('npm/casepath/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_legacy_licenses(self):
        test_file = self.get_test_loc('npm/chartist/package.json')
        expected_loc = self.get_test_loc('npm/chartist/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_from_npmjs(self):
        test_file = self.get_test_loc('npm/from_npmjs/package.json')
        expected_loc = self.get_test_loc('npm/from_npmjs/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_package_json_from_tarball_with_deps(self):
        test_file = self.get_test_loc('npm/from_tarball/package.json')
        expected_loc = self.get_test_loc('npm/from_tarball/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_invalid_json(self):
        test_file = self.get_test_loc('npm/invalid/package.json')
        try:
            npm.parse(test_file)
        except ValueError as e:
            assert 'Expecting value: line 60 column 3' in str(e)

    def test_parse_keywords(self):
        test_file = self.get_test_loc('npm/keywords/package.json')
        expected_loc = self.get_test_loc('npm/keywords/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_legacy_licenses_as_dict(self):
        test_file = self.get_test_loc('npm/legacy_license_dict/package.json')
        expected_loc = self.get_test_loc('npm/legacy_license_dict/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_double_legacy_licenses_as_dict(self):
        test_file = self.get_test_loc('npm/double_license/package.json')
        expected_loc = self.get_test_loc('npm/double_license/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_nodep(self):
        test_file = self.get_test_loc('npm/nodep/package.json')
        expected_loc = self.get_test_loc('npm/nodep/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_does_not_crash_if_partial_repo_url(self):
        test_file = self.get_test_loc('npm/repo_url/package.json')
        expected_loc = self.get_test_loc('npm/repo_url/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_scoped_package_1(self):
        test_file = self.get_test_loc('npm/scoped1/package.json')
        expected_loc = self.get_test_loc('npm/scoped1/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_scoped_package_2(self):
        test_file = self.get_test_loc('npm/scoped2/package.json')
        expected_loc = self.get_test_loc('npm/scoped2/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_from_npm_authors_with_email_list(self):
        # See: sequelize
        test_file = self.get_test_loc('npm/sequelize/package.json')
        expected_loc = self.get_test_loc('npm/sequelize/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_from_urls_dict_legacy_is_ignored(self):
        test_file = self.get_test_loc('npm/urls_dict/package.json')
        expected_loc = self.get_test_loc('npm/urls_dict/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_from_uri_vcs(self):
        test_file = self.get_test_loc('npm/uri_vcs/package.json')
        expected_loc = self.get_test_loc('npm/uri_vcs/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_registry_old_format(self):
        test_file = self.get_test_loc('npm/old_registry/package.json')
        expected_loc = self.get_test_loc('npm/old_registry/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_with_homepage_as_list(self):
        test_file = self.get_test_loc('npm/homepage-as-list/package.json')
        expected_loc = self.get_test_loc('npm/homepage-as-list/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_with_invalid_dep(self):
        test_file = self.get_test_loc('npm/invalid-dep/package.json')
        expected_loc = self.get_test_loc('npm/invalid-dep/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_utils_merge_1_0_0(self):
        test_file = self.get_test_loc('npm/utils-merge-1.0.0/package.json')
        expected_loc = self.get_test_loc(
            'npm/utils-merge-1.0.0/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_mime_1_3_4(self):
        test_file = self.get_test_loc('npm/mime-1.3.4/package.json')
        expected_loc = self.get_test_loc(
            'npm/mime-1.3.4/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_express_jwt_3_4_0(self):
        test_file = self.get_test_loc('npm/express-jwt-3.4.0/package.json')
        expected_loc = self.get_test_loc(
            'npm/express-jwt-3.4.0/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_package_lock(self):
        test_file = self.get_test_loc('npm/package-lock/package-lock.json')
        expected_loc = self.get_test_loc(
            'npm/package-lock/package-lock.json-expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_npm_shrinkwrap(self):
        test_file = self.get_test_loc('npm/npm-shrinkwrap/npm-shrinkwrap.json')
        expected_loc = self.get_test_loc(
            'npm/npm-shrinkwrap/npm-shrinkwrap.json-expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_with_name(self):
        test_file = self.get_test_loc('npm/with_name/package.json')
        expected_loc = self.get_test_loc('npm/with_name/package.json.expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_without_name(self):
        test_file = self.get_test_loc('npm/without_name/package.json')
        try:
            npm.parse(test_file)
        except AttributeError as e:
            assert "'NoneType' object has no attribute 'to_dict'" in str(e)

    def test_parse_yarn_lock(self):
        test_file = self.get_test_loc('npm/yarn-lock/yarn.lock')
        expected_loc = self.get_test_loc(
            'npm/yarn-lock/yarn.lock-expected')
        packages = npm.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_vcs_repository_mapper(self):
        package = MockPackage()
        repo = 'git+git://bitbucket.org/vendor/my-private-repo.git'
        result = npm.vcs_repository_mapper(repo, package)
        assert result.vcs_url == repo

    def test_vcs_repository_mapper_handles_version(self):
        package = MockPackage()
        repo = 'git@bitbucket.org/vendor/my-private-repo.git'
        rev = '213123aefd'
        expected = 'https://bitbucket.org/vendor/my-private-repo.git@213123aefd'
        result = npm.vcs_repository_mapper(repo, package, rev)
        assert result.vcs_url == expected

    def test_vcs_repository_mapper_handles_version_on_gh(self):
        package = MockPackage()
        repo = 'git@github.com/vendor/my-private-repo'
        rev = '213123aefd'
        expected = 'https://github.com/vendor/my-private-repo@213123aefd'
        result = npm.vcs_repository_mapper(repo, package, rev)
        assert result.vcs_url == expected

    def test_npm_get_package_resources(self):
        test_loc = self.get_test_loc('npm/get_package_resources')
        codebase = Codebase(test_loc)
        root = codebase.root
        expected = [
            'get_package_resources',
            'get_package_resources/package.json',
            'get_package_resources/this-should-be-returned'
        ]
        results = [r.path for r in npm.NpmPackage.get_package_resources(root, codebase)]
        assert results == expected


test_data = [
    (['MIT'], 'mit'),
    (['(MIT OR Apache-2.0)'], 'mit OR apache-2.0'),
    (['SEE LICENSE IN LICENSE'], 'unknown-license-reference'),
    (['For licensing, see LICENSE.md or https://ckeditor.com/legal/ckeditor-oss-license.'], 'unknown-license-reference AND unknown'),
    (['See License in ./LICENSE file'], 'unknown-license-reference AND unknown'),
    # FIXME: Apache2 is a valid license
    (['MIT', 'Apache2'], 'mit AND unknown'),
    ([{'type': 'MIT', 'url': 'https://github.com/jonschlinkert/repeat-element/blob/master/LICENSE'}], 'mit'),
    ([{'type': 'Freeware', 'url': 'https://github.com/foor/bar'}], 'unknown-license-reference'),
    ([{'type': 'patent grant', 'url': 'Freeware'}], 'unknown'),
    ([{'type': 'GPLv2', 'url': 'https://example.com/licenses/GPLv2'}, {'type': 'MIT', 'url': 'https://example.com/licenses/MIT'}, ],
     '(gpl-2.0 AND (gpl-2.0 AND unknown)) AND mit'),
]


@pytest.mark.parametrize('declared_license,expected_expression', test_data)
def test_compute_normalized_license_from_declared(declared_license, expected_expression):
    result = npm.compute_normalized_license(declared_license)
    assert result == expected_expression


class MockPackage(object):
    pass
