# -*- coding: utf-8 -*-
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
import sys
from unittest.case import skipIf

from commoncode import command
from commoncode import compat
from commoncode.testcase import FileBasedTesting
from commoncode.system import on_linux
from commoncode.system import on_mac
from commoncode.system import on_windows
from commoncode.system import py2
from commoncode.system import py3


class TestCommand(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    @skipIf(not py2, 'Behaviour of console encodings changed in Python3')
    def test_execute2_non_ascii_output_py2(self):
        # Popen returns a *binary* string with non-ascii chars: skips these
        python = sys.executable
        rc, stdout, stderr = command.execute2(
            python, ['-c', "print b'non ascii: \\xe4 just passed it !'"]
        )
        assert b'' == stderr
        assert b'non ascii: a just passed it !' == stdout
        assert rc == 0
        # do not throw exception
        compat.unicode(stdout)

    @skipIf(not py3, 'Behaviour of console encodings changed in Python3')
    def test_execute2_non_ascii_output_py3(self):
        # Popen returns a *binary* string with non-ascii chars: skips these
        python = sys.executable
        rc, stdout, stderr = command.execute2(
            python, ['-c', 'print("non ascii: été just passed it !")']
        )
        assert '' == stderr
        assert 'non ascii: ete just passed it !' == stdout
        assert 0 == rc
        # do not throw exception
        stdout.encode('ascii')

    @skipIf(not (on_linux and py2), 'Linux py2 only')
    def test_update_path_var_linux_py2(self):
        existing_path_var = b'/usr/bin:/usr/local'
        pathsep = b':'

        new_path = b'foo\xb1bar'
        updated_path = command.update_path_var(existing_path_var, new_path, pathsep)
        assert b'foo\xb1bar:/usr/bin:/usr/local' == updated_path

        new_path = u'/bin/foo\udcb1bar'
        updated_path = command.update_path_var(updated_path, new_path, pathsep)
        assert b'/bin/foo\xb1bar:foo\xb1bar:/usr/bin:/usr/local' == updated_path

        new_path = b'foo\xb1bar'
        updated_path = command.update_path_var(updated_path, new_path, pathsep)
        assert b'/bin/foo\xb1bar:foo\xb1bar:/usr/bin:/usr/local' == updated_path

    @skipIf(not (on_linux and py3), 'Linux py3 only')
    def test_update_path_var_linux_from_bytes(self):
        existing_path_var = '/usr/bin:/usr/local'
        pathsep = ':'

        new_path = b'foo\xb1bar'
        updated_path = command.update_path_var(existing_path_var, new_path, pathsep)
        assert 'foo\udcb1bar:/usr/bin:/usr/local' == updated_path

        new_path = u'/bin/foo\udcb1bar'
        updated_path = command.update_path_var(updated_path, new_path, pathsep)
        assert '/bin/foo\udcb1bar:foo\udcb1bar:/usr/bin:/usr/local' == updated_path

        new_path = b'/bin/foo\xb1bar'
        updated_path = command.update_path_var(updated_path, new_path, pathsep)
        assert '/bin/foo\udcb1bar:foo\udcb1bar:/usr/bin:/usr/local' == updated_path

        new_path = u'foo\udcb1bar'
        updated_path = command.update_path_var(updated_path, new_path, pathsep)
        assert '/bin/foo\udcb1bar:foo\udcb1bar:/usr/bin:/usr/local' == updated_path

        new_path = b'foo\xb1bar'
        updated_path = command.update_path_var(updated_path, new_path, pathsep)
        assert '/bin/foo\udcb1bar:foo\udcb1bar:/usr/bin:/usr/local' == updated_path

    @skipIf(not (on_mac and py2), 'Mac only py2')
    def test_update_path_var_mac_from_bytes(self):
        existing_path_var = '/usr/bin:/usr/local'
        pathsep = ':'

        new_path = b'foo\xb1bar'
        updated_path = command.update_path_var(existing_path_var, new_path, pathsep)
        assert 'foo\xb1bar:/usr/bin:/usr/local' == updated_path

        new_path = u'/bin/foo\udcb1bar'
        updated_path = command.update_path_var(updated_path, new_path, pathsep)
        assert '/bin/foo\xb1bar:foo\xb1bar:/usr/bin:/usr/local' == updated_path

        new_path = b'foo\xb1bar'
        updated_path = command.update_path_var(updated_path, new_path, pathsep)
        assert '/bin/foo\xb1bar:foo\xb1bar:/usr/bin:/usr/local' == updated_path

    @skipIf(not (on_mac and py3), 'Mac only py3')
    def test_update_path_var_mac_from_unicode(self):
        existing_path_var = '/usr/bin:/usr/local'
        pathsep = ':'

        new_path = u'foo\udcb1bar'
        updated_path = command.update_path_var(existing_path_var, new_path, pathsep)
        assert 'foo\udcb1bar:/usr/bin:/usr/local' == updated_path

        new_path = b'/bin/foo\xb1bar'
        updated_path = command.update_path_var(updated_path, new_path, pathsep)
        assert '/bin/foo\udcb1bar:foo\udcb1bar:/usr/bin:/usr/local' == updated_path

        new_path = u'foo\udcb1bar'
        updated_path = command.update_path_var(updated_path, new_path, pathsep)
        assert '/bin/foo\udcb1bar:foo\udcb1bar:/usr/bin:/usr/local' == updated_path

    @skipIf(not (on_mac and py2), 'Mac py2 only')
    def test_update_path_var_mac_from_unicode_py2(self):
        existing_path_var = '/usr/bin:/usr/local'
        pathsep = ':'

        new_path = u'foo\udcb1bar'
        updated_path = command.update_path_var(existing_path_var, new_path, pathsep)
        assert 'foo\xb1bar:/usr/bin:/usr/local' == updated_path

        new_path = b'/bin/foo\xb1bar'
        updated_path = command.update_path_var(updated_path, new_path, pathsep)
        assert '/bin/foo\xb1bar:foo\xb1bar:/usr/bin:/usr/local' == updated_path

        new_path = u'foo\udcb1bar'
        updated_path = command.update_path_var(updated_path, new_path, pathsep)
        assert '/bin/foo\xb1bar:foo\xb1bar:/usr/bin:/usr/local' == updated_path

    @skipIf(not (on_windows and py2), 'Windows only on Py2')
    def test_update_path_var_windows_py2(self):
        existing_path_var = b'c:\\windows;C:Program Files'
        pathsep = ';'

        new_path = u'c:\\bin\\foo\udcb1bar'
        updated_path = command.update_path_var(existing_path_var, new_path, pathsep)
        assert 'c:\\bin\\foo?bar;c:\\windows;C:Program Files' == updated_path

    @skipIf(not (on_windows and py3), 'Windows only on Py3')
    def test_update_path_var_windows_from_unicode(self):
        existing_path_var = u'c:\\windows;C:Program Files'
        pathsep = u';'

        new_path = u'foo\udcb1bar'
        updated_path = command.update_path_var(existing_path_var, new_path, pathsep)
        assert u'foo\udcb1bar;c:\\windows;C:Program Files' == updated_path

        new_path = u'foo\udcb1bar'
        updated_path = command.update_path_var(updated_path, new_path, pathsep)
        assert u'foo\udcb1bar;c:\\windows;C:Program Files' == updated_path
