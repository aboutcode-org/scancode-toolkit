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

from unittest import TestCase

from packagedcode.utils import combine_expressions
from packagedcode.utils import normalize_vcs_url


class TestPackageUtils(TestCase):

    def test_normalize_vcs_url_basic(self):
        url = 'https://pear2.php.net'
        result = normalize_vcs_url(url)
        expected = 'https://pear2.php.net'
        assert expected == result

    def test_normalize_vcs_url_svn(self):
        url = 'http://svn.example.org/projectA/'
        result = normalize_vcs_url(url)
        expected = 'http://svn.example.org/projectA/'
        assert expected == result

    def test_normalize_vcs_url_github(self):
        url = 'https://github.com/igorw/monolog'
        result = normalize_vcs_url(url)
        expected = 'https://github.com/igorw/monolog'
        assert expected == result

    def test_normalize_vcs_url_bitbucket(self):
        url = 'git@bitbucket.org:vendor/my-private-repo.git'
        result = normalize_vcs_url(url)
        expected = 'https://bitbucket.org/vendor/my-private-repo.git'
        assert expected == result

    def test_normalize_vcs_url_does_not_pad_git_plus(self):
        url = 'git+git://bitbucket.org/vendor/my-private-repo.git'
        result = normalize_vcs_url(url)
        assert url== result

    def test_normalize_vcs_url_does_not_pad_git_plus2(self):
        url = 'git+https://github.com/stevepapa/angular2-autosize.git'
        result = normalize_vcs_url(url)
        expected = 'git+https://github.com/stevepapa/angular2-autosize.git'
        assert expected == result

    def test_normalize_vcs_url_0(self):
        test = 'npm/npm'
        expected = 'https://github.com/npm/npm'
        assert expected == normalize_vcs_url(test)

    def test_normalize_vcs_url_1(self):
        test = 'gist:11081aaa281'
        expected = 'https://gist.github.com/11081aaa281'
        assert expected == normalize_vcs_url(test)

    def test_normalize_vcs_url_2(self):
        test = 'bitbucket:example/repo'
        expected = 'https://bitbucket.org/example/repo'
        assert expected == normalize_vcs_url(test)

    def test_normalize_vcs_url_3(self):
        test = 'gitlab:another/repo'
        expected = 'https://gitlab.com/another/repo'
        assert expected == normalize_vcs_url(test)

    def test_normalize_vcs_url_4(self):
        test = 'expressjs/serve-static'
        expected = 'https://github.com/expressjs/serve-static'
        assert expected == normalize_vcs_url(test)

    def test_normalize_vcs_url_5(self):
        test = 'git://github.com/angular/di.js.git'
        expected = 'git://github.com/angular/di.js.git'
        assert expected == normalize_vcs_url(test)

    def test_normalize_vcs_url_6(self):
        test = 'git://github.com/hapijs/boom'
        expected = 'git://github.com/hapijs/boom'
        assert expected == normalize_vcs_url(test)

    def test_normalize_vcs_url_7(self):
        test = 'git@github.com:balderdashy/waterline-criteria.git'
        expected = 'https://github.com/balderdashy/waterline-criteria.git'
        assert expected == normalize_vcs_url(test)

    def test_normalize_vcs_url_8(self):
        test = 'http://github.com/ariya/esprima.git'
        expected = 'http://github.com/ariya/esprima.git'
        assert expected == normalize_vcs_url(test)

    def test_normalize_vcs_url_9(self):
        test = 'http://github.com/isaacs/nopt'
        expected = 'http://github.com/isaacs/nopt'
        assert expected == normalize_vcs_url(test)

    def test_normalize_vcs_url_10(self):
        test = 'https://github.com/chaijs/chai'
        expected = 'https://github.com/chaijs/chai'
        assert expected == normalize_vcs_url(test)

    def test_normalize_vcs_url_11(self):
        test = 'https://github.com/christkv/kerberos.git'
        expected = 'https://github.com/christkv/kerberos.git'
        assert expected == normalize_vcs_url(test)

    def test_normalize_vcs_url_12(self):
        test = 'https://gitlab.com/foo/private.git'
        expected = 'https://gitlab.com/foo/private.git'
        assert expected == normalize_vcs_url(test)

    def test_normalize_vcs_url_13(self):
        test = 'git@gitlab.com:foo/private.git'
        expected = 'https://gitlab.com/foo/private.git'
        assert expected == normalize_vcs_url(test)

    def test_normalize_vcs_url_git_repo_url_without_slash_slash(self):
        test = 'git@github.com/Filirom1/npm2aur.git'
        expected = 'https://github.com/Filirom1/npm2aur.git'
        assert expected == normalize_vcs_url(test)

    def test_normalize_vcs_url_does_not_fail_on_empty(self):
        assert None == normalize_vcs_url(None)
        assert None == normalize_vcs_url('')
        assert None == normalize_vcs_url(' ')

    def test_combine_expressions_with_empty_input(self):
        assert None == combine_expressions(None)
        assert None == combine_expressions([])

    def test_combine_expressions_with_regular(self):
        assert 'mit AND apache-2.0' == combine_expressions(
            ['mit', 'apache-2.0'])

    def test_combine_expressions_with_duplicated_elements(self):
        assert 'mit AND apache-2.0' == combine_expressions(
            ['mit', 'apache-2.0', 'mit'])

    def test_combine_expressions_with_or_relationship(self):
        assert 'mit OR apache-2.0' == combine_expressions(
            ['mit', 'apache-2.0'], 'OR')
