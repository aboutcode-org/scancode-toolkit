#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/commoncode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
from unittest.case import skipIf

import commoncode.testcase
from commoncode import fileutils
from commoncode import ignore
from commoncode.system import on_mac
from commoncode.system import on_windows


class IgnoreTest(commoncode.testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    @skipIf(on_mac, 'Return different result on Mac for reasons to investigate')
    def test_is_ignored_default_ignores_eclipse1(self):
        test_dir = self.extract_test_tar('ignore/excludes/eclipse.tgz')
        test_base = os.path.join(test_dir, 'eclipse')

        test = os.path.join(test_base, '.settings')
        assert ignore.is_ignored(test, ignore.default_ignores, {})

    def test_is_ignored_default_ignores_eclipse2(self):
        test_dir = self.extract_test_tar('ignore/excludes/eclipse.tgz')
        test_base = os.path.join(test_dir, 'eclipse')

        test = os.path.join(test_base, '.settings/somefile')
        assert ignore.is_ignored(test, ignore.default_ignores, {})

    def test_is_ignored_default_ignores_eclipse3(self):
        test_dir = self.extract_test_tar('ignore/excludes/eclipse.tgz')
        test_base = os.path.join(test_dir, 'eclipse')

        test = os.path.join(test_base, '.project')
        assert ignore.is_ignored(test, ignore.default_ignores, {})

    def test_is_ignored_default_ignores_eclipse4(self):
        test_dir = self.extract_test_tar('ignore/excludes/eclipse.tgz')
        test_base = os.path.join(test_dir, 'eclipse')

        test = os.path.join(test_base, '.pydevproject')
        assert ignore.is_ignored(test, ignore.default_ignores, {})

    def test_is_ignored_default_ignores_mac1(self):
        test_dir = self.extract_test_tar('ignore/excludes/mac.tgz')
        test_base = os.path.join(test_dir, 'mac')

        test = os.path.join(test_base, '__MACOSX')
        assert ignore.is_ignored(test, ignore.default_ignores, {})

    def test_is_ignored_default_ignores_mac2(self):
        test_dir = self.extract_test_tar('ignore/excludes/mac.tgz')
        test_base = os.path.join(test_dir, 'mac')

        test = os.path.join(test_base, '__MACOSX/comp_match/smallrepo/._jetty_1.0_index.csv')
        assert ignore.is_ignored(test, ignore.default_ignores, {})

    def test_is_ignored_default_ignores_mac3(self):
        test_dir = self.extract_test_tar('ignore/excludes/mac.tgz')
        test_base = os.path.join(test_dir, 'mac')

        test = os.path.join(test_base, '.DS_Store')
        assert ignore.is_ignored(test, ignore.default_ignores, {})

    def test_is_ignored_default_ignores_mac4(self):
        test_dir = self.extract_test_tar('ignore/excludes/mac.tgz')
        test_base = os.path.join(test_dir, 'mac')

        test = os.path.join(test_base, '.DS_Store/a')
        assert ignore.is_ignored(test, ignore.default_ignores, {})

    @skipIf(on_mac, 'Return different result on Mac for reasons to investigate')
    def test_is_ignored_default_ignores_mac5(self):
        test_dir = self.extract_test_tar('ignore/excludes/mac.tgz')
        test_base = os.path.join(test_dir, 'mac')

        test = os.path.join(test_base, '._.DS_Store')
        # this is really weird as a behavior
        # 'Default ignore: MacOSX artifact'
        assert ignore.is_ignored(test, ignore.default_ignores, {})

    @skipIf(on_mac, 'Return different result on Mac for reasons to investigate')
    def test_is_ignored_default_ignores_msft(self):
        test_dir = self.extract_test_tar('ignore/excludes/msft-vs.tgz')
        test = os.path.join(test_dir, 'msft-vs/tst.sluo')
        # 'Default ignore: Microsoft VS project artifact' ??
        assert ignore.is_ignored(test, ignore.default_ignores, {})

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
            ('/vcs/.bzr', True),
            ('/vcs/.git', True),
            ('/vcs/.hg', True),
            ('/vcs/.repo', True),
            ('/vcs/.svn', True),
            ('/vcs/CVS', True),
            ('/vcs/_darcs', True),
            ('/vcs/_MTN', True),
            ('/vcs/.bzrignore', True),
            ('/vcs/.cvsignore', True),
            ('/vcs/.gitignore', True),
            ('/vcs/.hgignore', True),
            ('/vcs/.svnignore', True),
            ('/vcs/vssver.scc', True),
        ]
        assert sorted(result) == sorted(expected)

    def test_fileset_is_included_with_default_ignore_does_not_skip_one_char_names(self):
        # use fileset directly to work on strings not locations
        from commoncode import fileset
        tests = [c for c in 'HFS+ Private Data'] + 'HFS+ Private Data'.split()
        result = [(t,
            fileset.is_included(t, excludes=ignore.default_ignores, includes={}))
            for t in tests]
        expected = [
            ('H', True),
            ('F', True),
            ('S', True),
            ('+', True),
            (' ', False),
            ('P', True),
            ('r', True),
            ('i', True),
            ('v', True),
            ('a', True),
            ('t', True),
            ('e', True),
            (' ', False),
            ('D', True),
            ('a', True),
            ('t', True),
            ('a', True),
            ('HFS+', True),
            ('Private', True),
            ('Data', True)
        ]

        assert result == expected

    @skipIf(on_mac or on_windows, 'We are only testing on posix for now')
    def test_is_ignored_path_string_skip_special(self):
        test_path = '/test/path'
        assert ignore.is_ignored(test_path, {'asdf': 'skip'}, {}, skip_special=True)
        assert not ignore.is_ignored(test_path, {'asdf': 'skip'}, {}, skip_special=False)

    @skipIf(on_mac or on_windows, 'We are only testing on posix for now')
    def test_is_ignored_special_files_skip_special(self):
        test_fifo = self.get_temp_file()
        os.mkfifo(test_fifo)
        assert ignore.is_ignored(test_fifo, {'asdf': 'skip'}, {}, skip_special=True)
        assert not ignore.is_ignored(test_fifo, {'asdf': 'skip'}, {}, skip_special=False)

        test_symlink = self.get_temp_file()
        test_file_location = self.get_test_loc('ignore/vcs.tgz')
        os.symlink(test_file_location, test_symlink)
        assert ignore.is_ignored(test_symlink, {'asdf': 'skip'}, {}, skip_special=True)
        assert not ignore.is_ignored(test_symlink, {'asdf': 'skip'}, {}, skip_special=False)

    @skipIf(on_mac or on_windows, 'We are only testing on posix for now')
    def test_is_ignored_real_location_skip_special(self):
        test_file_location = self.get_test_loc('ignore/vcs.tgz')
        assert not ignore.is_ignored(test_file_location, {'asdf': 'skip'}, {}, skip_special=True)
        assert not ignore.is_ignored(test_file_location, {'asdf': 'skip'}, {}, skip_special=False)

        assert not ignore.is_ignored(test_file_location, {'asdf': 'skip'}, {}, skip_special=True)
        assert not ignore.is_ignored(test_file_location, {'asdf': 'skip'}, {}, skip_special=False)
