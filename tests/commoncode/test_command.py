# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/commoncode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import sys

from unittest.case import skipIf

from commoncode import command
from commoncode.testcase import FileBasedTesting
from commoncode.system import on_linux
from commoncode.system import on_mac
from commoncode.system import on_windows
from commoncode.system import py36


class TestCommand(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    @skipIf(py36, 'This fails on Python 3.6 https://bugs.python.org/issue26919')
    def test_execute_can_handle_non_ascii_output(self):
        # Popen returns a *binary* string with non-ascii chars: skips these
        python = sys.executable
        rc, stdout, stderr = command.execute(
            python, ['-c', 'print("non ascii: été just passed it !")']
        )
        assert stderr == ''
        assert stdout == 'non ascii: ete just passed it !'
        assert rc == 0
        # do not throw exception
        stdout.encode('ascii')

    def test_execute_(self):
        python = sys.executable
        rc, stdout, stderr = command.execute(
            python, ['-c', 'print("foobar")']
        )
        assert stderr == ''
        assert stdout == 'foobar'
        assert rc == 0
        # do not throw exception
        stdout.encode('ascii')

    def test_execute2(self):
        python = sys.executable
        rc, stdout, stderr = command.execute2(
            python, ['-c', 'print("foobar")']
        )
        assert stderr == ''
        assert stdout == 'foobar'
        assert rc == 0
        # do not throw exception
        stdout.encode('ascii')

    @skipIf(not on_linux, 'Linux only')
    def test_update_path_var_on_linux(self):
        existing_path_var = '/usr/bin:/usr/local'

        new_path = b'foo\xb1bar'
        updated_path = command.update_path_var(existing_path_var, new_path)
        assert updated_path == 'foo\udcb1bar:/usr/bin:/usr/local'

        new_path = u'/bin/foo\udcb1bar'
        updated_path = command.update_path_var(updated_path, new_path)
        assert updated_path == '/bin/foo\udcb1bar:foo\udcb1bar:/usr/bin:/usr/local'

        new_path = b'/bin/foo\xb1bar'
        updated_path = command.update_path_var(updated_path, new_path)
        assert updated_path == '/bin/foo\udcb1bar:foo\udcb1bar:/usr/bin:/usr/local'

        new_path = u'foo\udcb1bar'
        updated_path = command.update_path_var(updated_path, new_path)
        assert updated_path == '/bin/foo\udcb1bar:foo\udcb1bar:/usr/bin:/usr/local'

        new_path = b'foo\xb1bar'
        updated_path = command.update_path_var(updated_path, new_path)
        assert updated_path == '/bin/foo\udcb1bar:foo\udcb1bar:/usr/bin:/usr/local'

    @skipIf(not on_mac, 'Mac only')
    def test_update_path_var_on_mac(self):
        existing_path_var = '/usr/bin:/usr/local'

        new_path = u'foo\udcb1bar'
        updated_path = command.update_path_var(existing_path_var, new_path)
        assert updated_path == 'foo\udcb1bar:/usr/bin:/usr/local'

        new_path = b'/bin/foo\xb1bar'
        updated_path = command.update_path_var(updated_path, new_path)
        assert updated_path == '/bin/foo\udcb1bar:foo\udcb1bar:/usr/bin:/usr/local'

        new_path = u'foo\udcb1bar'
        updated_path = command.update_path_var(updated_path, new_path)
        assert updated_path == '/bin/foo\udcb1bar:foo\udcb1bar:/usr/bin:/usr/local'

    @skipIf(not on_windows, 'Windows only')
    def test_update_path_var_on_windows(self):
        existing_path_var = u'c:\\windows;C:Program Files'

        new_path = u'foo\udcb1bar'
        updated_path = command.update_path_var(existing_path_var, new_path)
        assert updated_path == u'foo\udcb1bar;c:\\windows;C:Program Files'

        new_path = u'foo\udcb1bar'
        updated_path = command.update_path_var(updated_path, new_path)
        assert updated_path == u'foo\udcb1bar;c:\\windows;C:Program Files'

    def test_searchable_paths(self):
        d1 = self.get_temp_dir('foo')
        d2 = self.get_temp_dir('bar')
        ps = os.pathsep
        os.environ['FOO_SCANCODE_TEST1'] = f'{ps}{d1}{ps}{ps}{d2}{ps}'
        os.environ['FOO_SCANCODE_TEST2'] = f'{ps}{d2}{ps}{ps}{d1}{ps}/NOTADIR'

        env_vars = 'FOO_SCANCODE_TEST1', 'FOO_SCANCODE_TEST2'
        expected = d1, d2, d2, d1

        results = command.searchable_paths(env_vars=env_vars)
        if on_windows:
            for res, exp in zip(results, expected):
                _, _, r = res.rpartition('\\')
                _, _, e = exp.rpartition('\\')
                assert r == e

        elif on_mac:
            # macOS somehow adds a /private to the paths in the CI as a side-
            # effect of calling "realpath" and likely resolving links
            expected = f'/private{d1}', f'/private{d2}', f'/private{d2}', f'/private{d1}'
            assert expected == results
        else:
            assert expected == results

    def test_find_in_path(self):
        d1 = self.get_temp_dir('foo')
        d2 = self.get_temp_dir('bar')
        filename = 'baz'

        assert None == command.find_in_path(filename, searchable_paths=(d1, d2,))

        f2 = os.path.join(d2, filename)
        with open(f2, 'w') as o:
            o.write('some')

        assert f2 == command.find_in_path(filename, searchable_paths=(d1, d2,))
        assert f2 == command.find_in_path(filename, searchable_paths=(d2, d1,))

        f1 = os.path.join(d1, filename)
        with open(f1, 'w') as o:
            o.write('some')

        assert f1 == command.find_in_path(filename, searchable_paths=(d1, d2,))
        assert f2 == command.find_in_path(filename, searchable_paths=(d2, d1,))
