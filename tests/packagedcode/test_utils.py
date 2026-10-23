#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from unittest import TestCase

from packagedcode.utils import normalize_vcs_url
from packagedcode.utils import parse_vcs_urls


class TestPackageUtils(TestCase):

    def test_normalize_vcs_url_basic(self):
        url = 'https://pear2.php.net'
        result = normalize_vcs_url(url)
        expected = 'https://pear2.php.net'
        assert result == expected

    def test_normalize_vcs_url_svn(self):
        url = 'http://svn.example.org/projectA/'
        result = normalize_vcs_url(url)
        expected = 'http://svn.example.org/projectA/'
        assert result == expected

    def test_normalize_vcs_url_github(self):
        url = 'https://github.com/igorw/monolog'
        result = normalize_vcs_url(url)
        expected = 'https://github.com/igorw/monolog'
        assert result == expected

    def test_normalize_vcs_url_bitbucket(self):
        url = 'git@bitbucket.org:vendor/my-private-repo.git'
        result = normalize_vcs_url(url)
        expected = 'https://bitbucket.org/vendor/my-private-repo.git'
        assert result == expected

    def test_normalize_vcs_url_does_not_pad_git_plus(self):
        url = 'git+git://bitbucket.org/vendor/my-private-repo.git'
        result = normalize_vcs_url(url)
        assert result == url

    def test_normalize_vcs_url_does_not_pad_git_plus2(self):
        url = 'git+https://github.com/stevepapa/angular2-autosize.git'
        result = normalize_vcs_url(url)
        expected = 'git+https://github.com/stevepapa/angular2-autosize.git'
        assert result == expected

    def test_normalize_vcs_url_0(self):
        test = 'npm/npm'
        expected = 'https://github.com/npm/npm'
        assert normalize_vcs_url(test) == expected

    def test_normalize_vcs_url_1(self):
        test = 'gist:11081aaa281'
        expected = 'https://gist.github.com/11081aaa281'
        assert normalize_vcs_url(test) == expected

    def test_normalize_vcs_url_2(self):
        test = 'bitbucket:example/repo'
        expected = 'https://bitbucket.org/example/repo'
        assert normalize_vcs_url(test) == expected

    def test_normalize_vcs_url_3(self):
        test = 'gitlab:another/repo'
        expected = 'https://gitlab.com/another/repo'
        assert normalize_vcs_url(test) == expected

    def test_normalize_vcs_url_4(self):
        test = 'expressjs/serve-static'
        expected = 'https://github.com/expressjs/serve-static'
        assert normalize_vcs_url(test) == expected

    def test_normalize_vcs_url_5(self):
        test = 'git://github.com/angular/di.js.git'
        expected = 'git://github.com/angular/di.js.git'
        assert normalize_vcs_url(test) == expected

    def test_normalize_vcs_url_6(self):
        test = 'git://github.com/hapijs/boom'
        expected = 'git://github.com/hapijs/boom'
        assert normalize_vcs_url(test) == expected

    def test_normalize_vcs_url_7(self):
        test = 'git@github.com:balderdashy/waterline-criteria.git'
        expected = 'https://github.com/balderdashy/waterline-criteria.git'
        assert normalize_vcs_url(test) == expected

    def test_normalize_vcs_url_8(self):
        test = 'http://github.com/ariya/esprima.git'
        expected = 'http://github.com/ariya/esprima.git'
        assert normalize_vcs_url(test) == expected

    def test_normalize_vcs_url_9(self):
        test = 'http://github.com/isaacs/nopt'
        expected = 'http://github.com/isaacs/nopt'
        assert normalize_vcs_url(test) == expected

    def test_normalize_vcs_url_10(self):
        test = 'https://github.com/chaijs/chai'
        expected = 'https://github.com/chaijs/chai'
        assert normalize_vcs_url(test) == expected

    def test_normalize_vcs_url_11(self):
        test = 'https://github.com/christkv/kerberos.git'
        expected = 'https://github.com/christkv/kerberos.git'
        assert normalize_vcs_url(test) == expected

    def test_normalize_vcs_url_12(self):
        test = 'https://gitlab.com/foo/private.git'
        expected = 'https://gitlab.com/foo/private.git'
        assert normalize_vcs_url(test) == expected

    def test_normalize_vcs_url_13(self):
        test = 'git@gitlab.com:foo/private.git'
        expected = 'https://gitlab.com/foo/private.git'
        assert normalize_vcs_url(test) == expected

    def test_normalize_vcs_url_git_repo_url_without_slash_slash(self):
        test = 'git@github.com/Filirom1/npm2aur.git'
        expected = 'https://github.com/Filirom1/npm2aur.git'
        assert normalize_vcs_url(test) == expected

    def test_normalize_vcs_url_does_not_fail_on_empty(self):
        assert normalize_vcs_url(None) == None
        assert normalize_vcs_url('') == None
        assert normalize_vcs_url(' ') == None

    # parse_vcs_urls tests -- without version (code_view_url should be None)

    def test_parse_vcs_urls_github_no_version(self):
        code, bugs = parse_vcs_urls('https://github.com/owner/repo.git')
        assert code is None
        assert bugs == 'https://github.com/owner/repo/issues'

    def test_parse_vcs_urls_gitlab_no_version(self):
        code, bugs = parse_vcs_urls('git+https://gitlab.com/owner/repo')
        assert code is None
        assert bugs == 'https://gitlab.com/owner/repo/-/issues'

    def test_parse_vcs_urls_bitbucket_no_version(self):
        code, bugs = parse_vcs_urls('git@bitbucket.org:owner/repo')
        assert code is None
        assert bugs == 'https://bitbucket.org/owner/repo/issues'

    def test_parse_vcs_urls_codeberg_no_version(self):
        code, bugs = parse_vcs_urls('https://codeberg.org/owner/repo.git')
        assert code is None
        assert bugs == 'https://codeberg.org/owner/repo/issues'

    def test_parse_vcs_urls_unknown_host(self):
        code, bugs = parse_vcs_urls('https://gitea.example.com/owner/repo.git')
        assert code is None
        assert bugs is None

    def test_parse_vcs_urls_empty(self):
        assert parse_vcs_urls(None) == (None, None)
        assert parse_vcs_urls('') == (None, None)
        assert parse_vcs_urls(' ') == (None, None)

    # parse_vcs_urls tests -- with version

    def test_parse_vcs_urls_github_git_ssh_with_version(self):
        code, bugs = parse_vcs_urls('git@github.com:owner/repo.git', version='1.2.3')
        assert code == 'https://github.com/owner/repo/tree/1.2.3'
        assert bugs == 'https://github.com/owner/repo/issues'

    def test_parse_vcs_urls_github_https_with_version(self):
        code, bugs = parse_vcs_urls('https://github.com/owner/repo.git', version='2.0.0')
        assert code == 'https://github.com/owner/repo/tree/2.0.0'
        assert bugs == 'https://github.com/owner/repo/issues'

    def test_parse_vcs_urls_github_git_plus_https_with_version(self):
        code, bugs = parse_vcs_urls('git+https://github.com/owner/repo.git', version='0.9.1')
        assert code == 'https://github.com/owner/repo/tree/0.9.1'
        assert bugs == 'https://github.com/owner/repo/issues'

    def test_parse_vcs_urls_gitlab_with_version(self):
        code, bugs = parse_vcs_urls('git+https://gitlab.com/owner/repo', version='2.0.0')
        assert code == 'https://gitlab.com/owner/repo/-/tree/2.0.0'
        assert bugs == 'https://gitlab.com/owner/repo/-/issues'

    def test_parse_vcs_urls_bitbucket_with_version(self):
        code, bugs = parse_vcs_urls('git@bitbucket.org:owner/repo', version='3.1.0')
        assert code == 'https://bitbucket.org/owner/repo/src/3.1.0'
        assert bugs == 'https://bitbucket.org/owner/repo/issues'

    def test_parse_vcs_urls_codeberg_with_version(self):
        code, bugs = parse_vcs_urls('https://codeberg.org/owner/repo.git', version='0.5.0')
        assert code == 'https://codeberg.org/owner/repo/src/tag/0.5.0'
        assert bugs == 'https://codeberg.org/owner/repo/issues'

    def test_parse_vcs_urls_unknown_host_with_version(self):
        code, bugs = parse_vcs_urls('https://gitea.example.com/owner/repo.git', version='1.0.0')
        assert code is None
        assert bugs is None
