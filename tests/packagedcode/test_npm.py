#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import, print_function

import json
import os.path
import shutil

from commoncode.testcase import FileBasedTesting

from packagedcode import npm
from commoncode import fileutils
from collections import OrderedDict


class TestNpm(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_package(self, test_loc, expected_loc, regen=False):
        test_loc = self.get_test_loc(test_loc)
        expected_loc = self.get_test_loc(expected_loc)
        results = npm.parse(location=test_loc)
        if regen:
            regened_exp_loc = self.get_temp_file()

            with open(regened_exp_loc, 'wb') as ex:
                json.dump(results, ex, indent=2)

            expected_dir = os.path.dirname(expected_loc)
            if not os.path.exists(expected_dir):
                os.makedirs(expected_dir)
            shutil.copy(regened_exp_loc, expected_loc)

        with open(expected_loc) as ex:
            expected = json.load(ex)

        assert sorted(expected.items()) == sorted(results.items())

#     def test_parse_basic(self):
#         self.check_package('npm/basic/package.json', 'npm/basic/expected.json')
#
#     def test_parse_no_deps(self):
#         self.check_package('npm/nodep/package.json-no-dep', 'npm/nodep/expected.json')

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
        assert ('Isaac Z. Schlueter', None , None) == npm.parse_person(test)

    def test_parse_person_dict2(self):
        test = {'email': 'me@this.com'}
        assert (None , 'me@this.com', None) == npm.parse_person(test)

    def test_parse_person_dict3(self):
        test = {'url': 'http://example.com'}
        assert (None , None, 'http://example.com') == npm.parse_person(test)

    def test_parse_person_dict4(self):
        test = {'name': 'Isaac Z. Schlueter',
                'email': 'me@this.com',
                'url': 'http://example.com'}
        assert ('Isaac Z. Schlueter', 'me@this.com' , 'http://example.com') == npm.parse_person(test)

    def relative_locations(self, package_dict):
        """
        Helper to transform absolute locations to a simple file name
        """
        for key, value in package_dict.items():
            if not value:
                continue
            if key.endswith('location'):
                package_dict[key] = value and fileutils.file_name(value) or None
            if key.endswith('locations'):
                values = [v and fileutils.file_name(v) or None for v in value]
                package_dict[key] = values
        return package_dict

    def test_parse_from_tarball(self):
        test_file = self.get_test_loc('npm/from_tarball/package.json')
        package = npm.parse(test_file)
        expected = OrderedDict([
            ('type', 'npm'),
            ('packaging', None),
            ('primary_language', 'JavaScript'),
            ('metafile_location', 'package.json'),
            ('id', u'npm'),
            ('name', u'npm'),
            ('qualified_name', u'npm npm'),
            ('version', u'2.13.5'),
            ('summary', u'a package manager for JavaScript'),
            ('asserted_licenses', [OrderedDict([('license', u'Artistic-2.0'),
                                      ('text', None),
                                      ('notice', None),
                                      ('url', None)])]),
            ('author', u'Isaac Z. Schlueter'),
            ('author_email', u'i@izs.me'),
            ('author_url', u'http://blog.izs.me'),
            ('homepage_url', u'https://docs.npmjs.com/'),
            ('download_url', u'https://registry.npmjs.org/npm/-/npm-2.13.5.tgz'),
            ('vcs_tool', u'git'),
            ('vcs_repository', u'https://github.com/npm/npm')
        ])

        assert expected == self.relative_locations(package.get_info())

    def test_parse_basic(self):
        test_file = self.get_test_loc('npm/basic/package.json')
        package = npm.parse(test_file)
        result = self.relative_locations(package.get_info())
        expected = OrderedDict([
            ('type', 'npm'),
            ('packaging', None),
            ('primary_language', 'JavaScript'),
            ('metafile_location', 'package.json'),
            ('id', u'cookie-signature'),
            ('name', u'cookie-signature'),
            ('qualified_name', u'npm cookie-signature'),
            ('version', u'1.0.3'),
            ('summary', u'Sign and unsign cookies'),
            ('asserted_licenses', []),
            ('author', u'TJ Holowaychuk'),
            ('author_email', u'tj@learnboost.com'),
            ('author_url', None),
            ('homepage_url', None),
            ('download_url', u'https://registry.npmjs.org/cookie-signature/-/cookie-signature-1.0.3.tgz'),
            ('vcs_tool', u'git'),
            ('vcs_repository', u'https://github.com/visionmedia/node-cookie-signature.git'),
        ])
        assert expected == result

    def test_parse_from_npmjs(self):
        test_file = self.get_test_loc('npm/from_nmpjs/package.json')
        package = npm.parse(test_file)
        result = self.relative_locations(package.get_info())
        expected = OrderedDict([
            ('type', 'npm'),
            ('packaging', None),
            ('primary_language', 'JavaScript'),
            ('metafile_location', 'package.json'),
            ('id', u'npm'),
            ('name', u'npm'),
            ('qualified_name', u'npm npm'),
            ('version', u'2.13.5'),
            ('summary', u'a package manager for JavaScript'),
            ('asserted_licenses', [OrderedDict([('license', u'Artistic-2.0'), ('text', None), ('notice', None), ('url', None)])]),
            ('author', u'Isaac Z. Schlueter'),
            ('author_email', u'i@izs.me'),
            ('author_url', u'http://blog.izs.me'),
            ('homepage_url', u'https://docs.npmjs.com/'),
            ('download_url', u'http://registry.npmjs.org/npm/-/npm-2.13.5.tgz'),
            ('vcs_tool', u'git'),
            ('vcs_repository', u'git+https://github.com/npm/npm.git'),
        ])
        assert expected == result

    def test_parse_as_installed(self):
        test_file = self.get_test_loc('npm/as_installed/package.json')
        package = npm.parse(test_file)
        result = self.relative_locations(package.get_info())
        expected = OrderedDict([
            ('type', 'npm'),
            ('packaging', None),
            ('primary_language', 'JavaScript'),
            ('metafile_location', 'package.json'),
            ('id', u'npm'),
            ('name', u'npm'),
            ('qualified_name', u'npm npm'),
            ('version', u'2.13.5'),
            ('summary', u'a package manager for JavaScript'),
            ('asserted_licenses', [OrderedDict([('license', u'Artistic-2.0'), ('text', None), ('notice', None), ('url', None)])]),
            ('author', u'Isaac Z. Schlueter'),
            ('author_email', u'i@izs.me'),
            ('author_url', u'http://blog.izs.me'),
            ('homepage_url', u'https://docs.npmjs.com/'),
            ('download_url', u'http://registry.npmjs.org/npm/-/npm-2.13.5.tgz'),
            ('vcs_tool', u'git'),
            ('vcs_repository', u'git+https://github.com/npm/npm.git'),
        ])
        assert expected == result

    def test_parse_subset(self):
        test_file = self.get_test_loc('npm/invalid/package.json')
        try:
            npm.parse(test_file)
        except ValueError, e:
            assert 'No JSON object could be decoded' == e.message
