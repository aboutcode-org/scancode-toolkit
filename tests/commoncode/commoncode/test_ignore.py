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

from __future__ import absolute_import
from __future__ import print_function

import os
from unittest.case import skipIf

import commoncode.testcase
from commoncode import fileutils
from commoncode import ignore
from commoncode.system import on_mac


class IgnoreTest(commoncode.testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    @skipIf(on_mac, 'Return different result on Mac for reasons to investigate')
    def test_is_ignored_default_ignores_eclipse1(self):
        test_dir = self.extract_test_tar('ignore/excludes/eclipse.tgz')
        test_base = os.path.join(test_dir, 'eclipse')

        test = os.path.join(test_base, '.settings')
        result = ignore.is_ignored(test, ignore.default_ignores, {})
        assert 'Default ignore: Eclipse IDE artifact' == result

    def test_is_ignored_default_ignores_eclipse2(self):
        test_dir = self.extract_test_tar('ignore/excludes/eclipse.tgz')
        test_base = os.path.join(test_dir, 'eclipse')

        test = os.path.join(test_base, '.settings/somefile')
        result = ignore.is_ignored(test, ignore.default_ignores, {})
        assert 'Default ignore: Eclipse IDE artifact' == result

    def test_is_ignored_default_ignores_eclipse3(self):
        test_dir = self.extract_test_tar('ignore/excludes/eclipse.tgz')
        test_base = os.path.join(test_dir, 'eclipse')

        test = os.path.join(test_base, '.project')
        result = ignore.is_ignored(test, ignore.default_ignores, {})
        assert 'Default ignore: Eclipse IDE artifact' == result

    def test_is_ignored_default_ignores_eclipse4(self):
        test_dir = self.extract_test_tar('ignore/excludes/eclipse.tgz')
        test_base = os.path.join(test_dir, 'eclipse')

        test = os.path.join(test_base, '.pydevproject')
        result = ignore.is_ignored(test, ignore.default_ignores, {})
        assert 'Default ignore: Eclipse IDE artifact' == result

    def test_is_ignored_default_ignores_mac1(self):
        test_dir = self.extract_test_tar('ignore/excludes/mac.tgz')
        test_base = os.path.join(test_dir, 'mac')

        test = os.path.join(test_base, '__MACOSX')
        result = ignore.is_ignored(test, ignore.default_ignores, {})
        assert 'Default ignore: MacOSX artifact' == result

    def test_is_ignored_default_ignores_mac2(self):
        test_dir = self.extract_test_tar('ignore/excludes/mac.tgz')
        test_base = os.path.join(test_dir, 'mac')

        test = os.path.join(test_base, '__MACOSX/comp_match/smallrepo/._jetty_1.0_index.csv')
        result = ignore.is_ignored(test, ignore.default_ignores, {})
        assert 'Default ignore: MacOSX artifact' == result

    def test_is_ignored_default_ignores_mac3(self):
        test_dir = self.extract_test_tar('ignore/excludes/mac.tgz')
        test_base = os.path.join(test_dir, 'mac')

        test = os.path.join(test_base, '.DS_Store')
        result = ignore.is_ignored(test, ignore.default_ignores, {})
        assert 'Default ignore: MacOSX artifact' == result

    def test_is_ignored_default_ignores_mac4(self):
        test_dir = self.extract_test_tar('ignore/excludes/mac.tgz')
        test_base = os.path.join(test_dir, 'mac')

        test = os.path.join(test_base, '.DS_Store/a')
        result = ignore.is_ignored(test, ignore.default_ignores, {})
        assert 'Default ignore: MacOSX artifact' == result

    @skipIf(on_mac, 'Return different result on Mac for reasons to investigate')
    def test_is_ignored_default_ignores_mac5(self):
        test_dir = self.extract_test_tar('ignore/excludes/mac.tgz')
        test_base = os.path.join(test_dir, 'mac')

        test = os.path.join(test_base, '._.DS_Store')
        result = ignore.is_ignored(test, ignore.default_ignores, {})
        # this is really weird as a behavior
        assert 'Default ignore: MacOSX artifact' == result

    @skipIf(on_mac, 'Return different result on Mac for reasons to investigate')
    def test_is_ignored_default_ignores_msft(self):
        test_dir = self.extract_test_tar('ignore/excludes/msft-vs.tgz')
        test = os.path.join(test_dir, 'msft-vs/tst.sluo')
        result = ignore.is_ignored(test, ignore.default_ignores, {})
        assert 'Default ignore: Microsoft VS project artifact' == result

    @skipIf(on_mac, 'Return different result on Mac for reasons to investigate')
    def test_is_ignored_skip_vcs_files_and_dirs(self):
        test_dir = self.extract_test_tar('ignore/vcs.tgz')
        result = []
        for top, dirs, files in os.walk(test_dir, topdown=True):
            not_ignored = []
            for d in dirs:
                p = os.path.join(top, d)
                ign = ignore.is_ignored(p, ignore.default_ignores, {})
                tp = fileutils.as_posixpath(p.replace(test_dir, ''))
                result.append((tp, ign,))
                if not ign:
                    not_ignored.append(d)

            # skip ignored things
            dirs[:] = not_ignored

            for f in files:
                p = os.path.join(top, f)
                ign = ignore.is_ignored(p, ignore.default_ignores, {})
                tp = fileutils.as_posixpath(p.replace(test_dir, ''))
                result.append((tp, ign,))

        expected = [
            ('/vcs', False),
            ('/vcs/.bzr', u'Default ignore: Bazaar artifact'),
            ('/vcs/.git', u'Default ignore: Git artifact'),
            ('/vcs/.hg', u'Default ignore: Mercurial artifact'),
            ('/vcs/.svn', u'Default ignore: SVN artifact'),
            ('/vcs/CVS', u'Default ignore: CVS artifact'),
            ('/vcs/_darcs', u'Default ignore: Darcs artifact'),
            ('/vcs/_MTN', u'Default ignore: Monotone artifact'),
            ('/vcs/.bzrignore', u'Default ignore: Bazaar config artifact'),
            ('/vcs/.cvsignore', u'Default ignore: CVS config artifact'),
            ('/vcs/.gitignore', u'Default ignore: Git config artifact'),
            ('/vcs/.hgignore', u'Default ignore: Mercurial config artifact'),
            ('/vcs/.repo', False),
            ('/vcs/.repo/repo', False),
            ('/vcs/.repo/repo/.git', u'Default ignore: Git artifact'),
            ('/vcs/.repo/repo/.gitattributes', u'Default ignore: Git config artifact'),
            ('/vcs/.repo/repo/.gitignore', u'Default ignore: Git config artifact'),
            ('/vcs/.repo/repo/color.py', False),
            ('/vcs/.repo/repo/docs', False),
            ('/vcs/.repo/repo/docs/manifest-format.txt', False),
            ('/vcs/.repo/repo/hooks', False),
            ('/vcs/.repo/repo/hooks/commit-msg', False),
            ('/vcs/.repo/repo/hooks/pre-auto-gc', False),
            ('/vcs/.repo/repo/subcmds', False),
            ('/vcs/.repo/repo/subcmds/abandon.py', False),
            ('/vcs/.repo/repo/tests', False),
            ('/vcs/.repo/repo/tests/fixtures', False),
            ('/vcs/.repo/repo/tests/fixtures/gitc_config', False),
            ('/vcs/.repo/repo/tests/fixtures/test.gitconfig', False),
            ('/vcs/.repo/repo/tests/test_git_config.py', False),
            ('/vcs/.svnignore', u'Default ignore: SVN config artifact'),
            ('/vcs/vssver.scc', u'Default ignore: Visual Source Safe artifact'),
        ]
        assert sorted(expected) == sorted(result)

    def test_fileset_match_default_ignore_does_not_skip_one_char_names(self):
        # use fileset directly to work on strings not locations
        from commoncode import fileset
        tests = [c for c in 'HFS+ Private Data'] + 'HFS+ Private Data'.split()
        for test in tests:
            assert False == fileset.match(test, includes=ignore.default_ignores, excludes={})
