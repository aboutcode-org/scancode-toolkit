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


class TestCommand(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    # tuples of supported osarch, osnoarch, noarch
    os_arches_test_matrix = [
        ('linux-32', 'linux-noarch', 'noarch'),
        ('linux-64', 'linux-noarch', 'noarch'),
        ('mac-32', 'mac-noarch', 'noarch'),
        ('mac-64', 'mac-noarch', 'noarch'),
        ('win-32', 'win-noarch', 'noarch'),
        ('win-64', 'win-noarch', 'noarch'),
    ]

    # os_arch -> (bin_dir, lib_dir, (bin_dir files,) (lib_dir files,) ,)
    os_arches_files_test_matrix = {
        'linux-32': (
            'command/bin/linux-32/bin',
            'command/bin/linux-32/lib',
            ('cmd'),
            ('libmagic32.so'),
        ),

        'linux-64': (
            'command/bin/linux-64/bin',
            'command/bin/linux-64/lib',
            ('cmd'),
            ('libmagic64.so'),
        ),

        'linux-noarch': (
            'command/bin/linux-noarch/bin',
            'command/bin/linux-noarch/bin',
            ('cmd'),
            (),
        ),

        'mac-32': (
            'command/bin/mac-32/bin',
            'command/bin/mac-32/lib',
            ('cmd'),
            ('libmagic.dylib'),
        ),

        'mac-64': (
            'command/bin/mac-64/bin',
            'command/bin/mac-64/lib',
            ('cmd'),
            ('libmagic.dylib'),
        ),

        'mac-noarch': (
            'command/bin/mac-noarch/bin',
            'command/bin/mac-noarch/bin',
            ('cmd'),
            (),
        ),

        'win-32': (
            'command/bin/win-32/bin',
            'command/bin/win-32/bin',
            ('cmd.exe',
             'magic1.dll'),
            ('cmd.exe',
             'magic1.dll'),
        ),

        'win-64': (
            'command/bin/win-64/bin',
            'command/bin/win-64/bin',
            ('cmd.exe',
             'magic1.dll'),
            ('cmd.exe',
             'magic1.dll'),
        ),

        'win-noarch': (
            'command/bin/win-noarch/bin',
            'command/bin/win-noarch/bin',
            ('cmd.exe',
             'some.dll'),
            ('cmd.exe',
             'some.dll'),
        ),

        'noarch': (
            'command/bin/noarch/bin',
            'command/bin/noarch/lib',
            ('cmd'),
            ('l'),
        ),

        'junk': (None, None, (), (),),
    }

    os_arches_locations_test_matrix = [
        ('linux-32', 'linux-noarch', 'noarch'),
        ('linux-64', 'linux-noarch', 'noarch'),
        ('linux-32', 'linux-noarch', None),
        ('linux-64', 'linux-noarch', None),
        ('linux-32', None, None),
        ('linux-64', None, None),
        (None, 'linux-noarch', 'noarch'),
        (None, 'linux-noarch', None),

        ('mac-32', 'mac-noarch', 'noarch'),
        ('mac-64', 'mac-noarch', 'noarch'),
        ('mac-32', 'mac-noarch', None),
        ('mac-64', 'mac-noarch', None),
        ('mac-32', None, None),
        ('mac-64', None, None),
        (None, 'mac-noarch', 'noarch'),
        (None, 'mac-noarch', None),

        ('win-32', 'win-noarch', 'noarch'),
        ('win-64', 'win-noarch', 'noarch'),
        ('win-32', 'win-noarch', None),
        ('win-64', 'win-noarch', None),
        ('win-32', None, None),
        ('win-64', None, None),
        (None, 'win-noarch', 'noarch'),
        (None, 'win-noarch', None),

        (None, None, 'noarch'),
    ]

    def test_execute_non_ascii_output(self):
        # Popen returns a *binary* string with non-ascii chars: skips these
        rc, stdout, stderr = command.execute(
            'python', ['-c', "print 'non ascii: \\xe4 just passed it !'"]
        )
        assert rc == 0
        assert stderr == ''

        # converting to Unicode could cause an "ordinal not in range..."
        # exception
        assert stdout == 'non ascii:  just passed it !'
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
                assert pbd.endswith(expected_bin.replace('command/', ''))
                if expected_bin_files:
                    assert all(f in expected_bin_files for f in os.listdir(bin_dir)) == True
            else:
                assert expected_bin == bin_dir

            if expected_lib:
                assert os.path.exists(lib_dir)
                assert os.path.isdir(lib_dir)
                pld = fileutils.as_posixpath(lib_dir)
                assert pld.endswith(expected_lib.replace('command/', ''))
                if expected_lib_files:
                    assert all(f in expected_lib_files for f in os.listdir(lib_dir)) == True
            else:
                assert expected_lib == lib_dir

    def test_get_locations_missing(self):
        assert command.get_locations('ctags', None) == (None, None, None)
        assert command.get_locations('dir', None) == (None, None, None)
        assert command.get_locations('ctags', '.') == (None, None, None)

    def test_get_locations(self):
        root_dir = self.get_test_loc('command/bin', copy=True)
        cmd = 'cmd'
        for  test_matrix in self.os_arches_locations_test_matrix:
            _os_arch, _os_noarch, _noarch = test_matrix
            cmd_loc, _ , _ = command.get_locations(cmd, root_dir, _os_arch, _os_noarch, _noarch)
            extension = ''
            if any(x and 'win' in x for x in (_os_arch, _os_noarch, _noarch)):
                extension = '.exe'
            expected_cmd = cmd + extension
            if cmd_loc:
                assert cmd_loc.endswith(expected_cmd)
                assert os.path.exists(cmd_loc)
                assert os.path.isfile(cmd_loc)
