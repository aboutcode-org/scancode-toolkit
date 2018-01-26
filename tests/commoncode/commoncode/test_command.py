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

import os

from commoncode import command
from commoncode import fileutils
from commoncode.testcase import FileBasedTesting
from unittest.case import skipIf
from commoncode.system import on_linux
from commoncode.system import on_mac
from commoncode.system import on_windows


class TestCommand(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), b'data')

    # tuples of supported osarch, osnoarch, noarch
    os_arches_test_matrix = [
        ('linux-32', b'linux-noarch', b'noarch'),
        ('linux-64', b'linux-noarch', b'noarch'),
        ('mac-32', b'mac-noarch', b'noarch'),
        ('mac-64', b'mac-noarch', b'noarch'),
        ('win-32', b'win-noarch', b'noarch'),
        ('win-64', b'win-noarch', b'noarch'),
    ]

    # os_arch -> (bin_dir, lib_dir, (bin_dir files,) (lib_dir files,) ,)
    os_arches_files_test_matrix = {
        b'linux-32': (
            b'command/bin/linux-32/bin',
            b'command/bin/linux-32/lib',
            ('cmd'),
            ('libmagic32.so'),
        ),

        b'linux-64': (
            b'command/bin/linux-64/bin',
            b'command/bin/linux-64/lib',
            ('cmd'),
            ('libmagic64.so'),
        ),

        b'linux-noarch': (
            b'command/bin/linux-noarch/bin',
            b'command/bin/linux-noarch/bin',
            ('cmd'),
            (),
        ),

        b'mac-32': (
            b'command/bin/mac-32/bin',
            b'command/bin/mac-32/lib',
            ('cmd'),
            ('libmagic.dylib'),
        ),

        b'mac-64': (
            b'command/bin/mac-64/bin',
            b'command/bin/mac-64/lib',
            ('cmd'),
            ('libmagic.dylib'),
        ),

        b'mac-noarch': (
            b'command/bin/mac-noarch/bin',
            b'command/bin/mac-noarch/bin',
            ('cmd'),
            (),
        ),

        b'win-32': (
            b'command/bin/win-32/bin',
            b'command/bin/win-32/bin',
            ('cmd.exe',
             b'magic1.dll'),
            ('cmd.exe',
             b'magic1.dll'),
        ),

        b'win-64': (
            b'command/bin/win-64/bin',
            b'command/bin/win-64/bin',
            ('cmd.exe',
             b'magic1.dll'),
            ('cmd.exe',
             b'magic1.dll'),
        ),

        b'win-noarch': (
            b'command/bin/win-noarch/bin',
            b'command/bin/win-noarch/bin',
            ('cmd.exe',
             b'some.dll'),
            ('cmd.exe',
             b'some.dll'),
        ),

        b'noarch': (
            b'command/bin/noarch/bin',
            b'command/bin/noarch/lib',
            ('cmd'),
            ('l'),
        ),

        b'junk': (None, None, (), (),),
    }

    os_arches_locations_test_matrix = [
        ('linux-32', b'linux-noarch', b'noarch'),
        ('linux-64', b'linux-noarch', b'noarch'),
        ('linux-32', b'linux-noarch', None),
        ('linux-64', b'linux-noarch', None),
        ('linux-32', None, None),
        ('linux-64', None, None),
        (None, b'linux-noarch', b'noarch'),
        (None, b'linux-noarch', None),

        ('mac-32', b'mac-noarch', b'noarch'),
        ('mac-64', b'mac-noarch', b'noarch'),
        ('mac-32', b'mac-noarch', None),
        ('mac-64', b'mac-noarch', None),
        ('mac-32', None, None),
        ('mac-64', None, None),
        (None, b'mac-noarch', b'noarch'),
        (None, b'mac-noarch', None),

        ('win-32', b'win-noarch', b'noarch'),
        ('win-64', b'win-noarch', b'noarch'),
        ('win-32', b'win-noarch', None),
        ('win-64', b'win-noarch', None),
        ('win-32', None, None),
        ('win-64', None, None),
        (None, b'win-noarch', b'noarch'),
        (None, b'win-noarch', None),

        (None, None, b'noarch'),
    ]

    def test_execute_non_ascii_output(self):
        # Popen returns a *binary* string with non-ascii chars: skips these
        rc, stdout, stderr = command.execute(
            b'python', ['-c', "print b'non ascii: \\xe4 just passed it !'"]
        )
        assert rc == 0
        assert stderr == b''

        # converting to Unicode could cause an "ordinal not in range..."
        # exception
        assert stdout == b'non ascii:  just passed it !'
        unicode(stdout)

    def test_os_arch_dir(self):
        root_dir = self.get_test_loc('command/bin', copy=True)
        for  _os_arch, _os_noarch, _noarch in self.os_arches_test_matrix:
            assert command.os_arch_dir(root_dir, _os_arch).endswith(_os_arch)
            assert command.os_noarch_dir(root_dir, _os_noarch).endswith(_os_noarch)
            assert command.noarch_dir(root_dir, _noarch).endswith(_noarch)

    def test_get_base_dirs(self):
        root_dir = self.get_test_loc('command/bin', copy=True)
        for  _os_arch, _os_noarch, _noarch in self.os_arches_test_matrix:
            bds = command.get_base_dirs(root_dir, _os_arch, _os_noarch, _noarch)
            assert bds
            for bd in bds:
                assert os.path.exists(bd)

    def test_get_bin_lib_dirs(self):
        root_dir = self.get_test_loc('command/bin', copy=True)
        for  os_arch, paths in self.os_arches_files_test_matrix.items():
            base_dir = os.path.join(root_dir, os_arch)

            bin_dir, lib_dir = command.get_bin_lib_dirs(base_dir)
            expected_bin, expected_lib, expected_bin_files, expected_lib_files = paths

            def norm(p):
                return os.path.abspath(os.path.normpath(p))

            if expected_bin:
                assert os.path.exists(bin_dir)
                assert os.path.isdir(bin_dir)
                pbd = fileutils.as_posixpath(bin_dir)
                assert pbd.endswith(expected_bin.replace('command/', b''))
                if expected_bin_files:
                    assert all(f in expected_bin_files for f in os.listdir(bin_dir)) == True
            else:
                assert expected_bin == bin_dir

            if expected_lib:
                assert os.path.exists(lib_dir)
                assert os.path.isdir(lib_dir)
                pld = fileutils.as_posixpath(lib_dir)
                assert pld.endswith(expected_lib.replace('command/', b''))
                if expected_lib_files:
                    assert all(f in expected_lib_files for f in os.listdir(lib_dir)) == True
            else:
                assert expected_lib == lib_dir

    def test_get_locations_missing(self):
        assert command.get_locations('ctags', None) == (None, None, None)
        assert command.get_locations('dir', None) == (None, None, None)
        assert command.get_locations('ctags', b'.') == (None, None, None)

    def test_get_locations(self):
        root_dir = self.get_test_loc('command/bin', copy=True)
        cmd = b'cmd'
        for  test_matrix in self.os_arches_locations_test_matrix:
            _os_arch, _os_noarch, _noarch = test_matrix
            cmd_loc, _ , _ = command.get_locations(cmd, root_dir, _os_arch, _os_noarch, _noarch)
            extension = b''
            if any(x and b'win' in x for x in (_os_arch, _os_noarch, _noarch)):
                extension = b'.exe'
            expected_cmd = cmd + extension
            if cmd_loc:
                assert cmd_loc.endswith(expected_cmd)
                assert os.path.exists(cmd_loc)
                assert os.path.isfile(cmd_loc)

    @skipIf(not on_linux, 'Linux only')
    def test_update_path_environment_linux_from_bytes(self):

        class MockOs(object):
            environ = {b'PATH': b'/usr/bin:/usr/local'}
            pathsep = b':'

        bytes_path = b'foo\xb1bar'
        command.update_path_environment(bytes_path, MockOs)
        assert {b'PATH': b'foo\xb1bar:/usr/bin:/usr/local'} == MockOs.environ

        unicode_path = u'/bin/foo\udcb1bar'
        command.update_path_environment(unicode_path, MockOs)
        assert {b'PATH': b'/bin/foo\xb1bar:foo\xb1bar:/usr/bin:/usr/local'} == MockOs.environ

        bytes_path = b'foo\xb1bar'
        command.update_path_environment(bytes_path, MockOs)
        assert {b'PATH': b'/bin/foo\xb1bar:foo\xb1bar:/usr/bin:/usr/local'} == MockOs.environ

    @skipIf(not on_linux, 'Linux only')
    def test_update_path_environment_linux_from_unicode(self):

        class MockOs(object):
            environ = {b'PATH': b'/usr/bin:/usr/local'}
            pathsep = b':'

        unicode_path = u'foo\udcb1bar'
        command.update_path_environment(unicode_path, MockOs)
        assert {b'PATH': b'foo\xb1bar:/usr/bin:/usr/local'} == MockOs.environ

        bytes_path = b'/bin/foo\xb1bar'
        command.update_path_environment(bytes_path, MockOs)
        assert {b'PATH': b'/bin/foo\xb1bar:foo\xb1bar:/usr/bin:/usr/local'} == MockOs.environ

        unicode_path = u'foo\udcb1bar'
        command.update_path_environment(unicode_path, MockOs)
        assert {b'PATH': b'/bin/foo\xb1bar:foo\xb1bar:/usr/bin:/usr/local'} == MockOs.environ

    @skipIf(not on_mac, 'Mac only')
    def test_update_path_environment_mac_from_bytes(self):

        class MockOs(object):
            environ = {b'PATH': b'/usr/bin:/usr/local'}
            pathsep = b':'

        bytes_path = b'foo\xb1bar'
        command.update_path_environment(bytes_path, MockOs)
        assert {'PATH': 'foo\xb1bar:/usr/bin:/usr/local'} == MockOs.environ

        unicode_path = u'/bin/foo\udcb1bar'
        command.update_path_environment(unicode_path, MockOs)
        assert {'PATH': '/bin/foo\xb1bar:foo\xb1bar:/usr/bin:/usr/local'} == MockOs.environ

        bytes_path = b'foo\xb1bar'
        command.update_path_environment(bytes_path, MockOs)
        assert {'PATH': '/bin/foo\xb1bar:foo\xb1bar:/usr/bin:/usr/local'} == MockOs.environ

    @skipIf(not on_mac, 'Mac only')
    def test_update_path_environment_mac_from_unicode(self):

        class MockOs(object):
            environ = {b'PATH': b'/usr/bin:/usr/local'}
            pathsep = b':'

        unicode_path = u'foo\udcb1bar'
        command.update_path_environment(unicode_path, MockOs)
        assert {'PATH': 'foo\xb1bar:/usr/bin:/usr/local'} == MockOs.environ

        bytes_path = b'/bin/foo\xb1bar'
        command.update_path_environment(bytes_path, MockOs)
        assert {'PATH': '/bin/foo\xb1bar:foo\xb1bar:/usr/bin:/usr/local'} == MockOs.environ

        unicode_path = u'foo\udcb1bar'
        command.update_path_environment(unicode_path, MockOs)
        assert {'PATH': '/bin/foo\xb1bar:foo\xb1bar:/usr/bin:/usr/local'} == MockOs.environ

    @skipIf(not on_windows, 'Windows only')
    def test_update_path_environment_windows_from_bytes(self):

        class MockOs(object):
            environ = {b'PATH': b'c:\\windows;C:Program Files'}
            pathsep = b';'

        bytes_path = b'foo\xb1bar'
        command.update_path_environment(bytes_path, MockOs)
        {'PATH': 'foo\xb1bar;c:\\windows;C:Program Files'}

        unicode_path = u'c:\\bin\\foo\udcb1bar'
        command.update_path_environment(unicode_path, MockOs)
        {'PATH': 'c:\\bin\\foo\xb1bar;foo\xb1bar;c:\\windows;C:Program Files'}

        bytes_path = b'foo\xb1bar'
        command.update_path_environment(bytes_path, MockOs)
        {'PATH': 'c:\\bin\\foo\xb1bar;foo\xb1bar;c:\\windows;C:Program Files'}

    @skipIf(not on_windows, 'Windows only')
    def test_update_path_environment_windows_from_unicode(self):

        class MockOs(object):
            environ = {b'PATH': b'c:\\windows;C:Program Files'}
            pathsep = b':'

        unicode_path = u'foo\udcb1bar'
        command.update_path_environment(unicode_path, MockOs)
        {'PATH': 'foo\xb1bar;c:\\windows;C:Program Files'}

        bytes_path = b'c:\\bin\\foo\xb1bar'
        command.update_path_environment(bytes_path, MockOs)
        {'PATH': 'c:\\bin\\foo\xb1bar;foo\xb1bar;c:\\windows;C:Program Files'}

        unicode_path = u'foo\udcb1bar'
        command.update_path_environment(unicode_path, MockOs)
        {'PATH': 'c:\\bin\\foo\xb1bar;foo\xb1bar;c:\\windows;C:Program Files'}
