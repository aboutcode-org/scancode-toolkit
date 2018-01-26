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

from unittest import TestCase

from packagedcode.utils import parse_repo_url


class TestPackageUtils(TestCase):

    def test_parse_repo_url_0(self):
        test = 'npm/npm'
        expected = 'https://github.com/npm/npm'
        assert expected == parse_repo_url(test)

    def test_parse_repo_url_1(self):
        test = 'gist:11081aaa281'
        expected = 'https://gist.github.com/11081aaa281'
        assert expected == parse_repo_url(test)

    def test_parse_repo_url_2(self):
        test = 'bitbucket:example/repo'
        expected = 'https://bitbucket.org/example/repo'
        assert expected == parse_repo_url(test)

    def test_parse_repo_url_3(self):
        test = 'gitlab:another/repo'
        expected = 'https://gitlab.com/another/repo'
        assert expected == parse_repo_url(test)

    def test_parse_repo_url_4(self):
        test = 'expressjs/serve-static'
        expected = 'https://github.com/expressjs/serve-static'
        assert expected == parse_repo_url(test)

    def test_parse_repo_url_5(self):
        test = 'git://github.com/angular/di.js.git'
        expected = 'git://github.com/angular/di.js.git'
        assert expected == parse_repo_url(test)

    def test_parse_repo_url_6(self):
        test = 'git://github.com/hapijs/boom'
        expected = 'git://github.com/hapijs/boom'
        assert expected == parse_repo_url(test)

    def test_parse_repo_url_7(self):
        test = 'git@github.com:balderdashy/waterline-criteria.git'
        expected = 'https://github.com/balderdashy/waterline-criteria.git'
        assert expected == parse_repo_url(test)

    def test_parse_repo_url_8(self):
        test = 'http://github.com/ariya/esprima.git'
        expected = 'http://github.com/ariya/esprima.git'
        assert expected == parse_repo_url(test)

    def test_parse_repo_url_9(self):
        test = 'http://github.com/isaacs/nopt'
        expected = 'http://github.com/isaacs/nopt'
        assert expected == parse_repo_url(test)

    def test_parse_repo_url_10(self):
        test = 'https://github.com/chaijs/chai'
        expected = 'https://github.com/chaijs/chai'
        assert expected == parse_repo_url(test)

    def test_parse_repo_url_11(self):
        test = 'https://github.com/christkv/kerberos.git'
        expected = 'https://github.com/christkv/kerberos.git'
        assert expected == parse_repo_url(test)

    def test_parse_repo_url_12(self):
        test = 'https://gitlab.com/foo/private.git'
        expected = 'https://gitlab.com/foo/private.git'
        assert expected == parse_repo_url(test)

    def test_parse_repo_url_13(self):
        test = 'git@gitlab.com:foo/private.git'
        expected = 'https://gitlab.com/foo/private.git'
        assert expected == parse_repo_url(test)

    def test_parse_git_repo_url_without_slash_slash(self):
        test = 'git@github.com/Filirom1/npm2aur.git'
        expected = 'https://github.com/Filirom1/npm2aur.git'
        assert expected == parse_repo_url(test)

    def test_parse_repo_url_does_not_fail_on_empty(self):
        assert None == parse_repo_url(None)
        assert None == parse_repo_url('')
        assert None == parse_repo_url(' ')
