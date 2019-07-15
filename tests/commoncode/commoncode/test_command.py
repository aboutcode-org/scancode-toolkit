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

from commoncode import command
from commoncode import compat
from commoncode.testcase import FileBasedTesting
from commoncode.system import on_linux
from commoncode.system import on_mac
from commoncode.system import on_windows
from commoncode import compat

import pytest

class TestCommand(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    @pytest.mark.scanslow
    def test_execute2_non_ascii_output(self):
        # Popen returns a *binary* string with non-ascii chars: skips these
        rc, stdout, stderr = command.execute2(
            b'python', ['-c', "print b'non ascii: \\xe4 just passed it !'"]
        )
        assert rc == 0
        assert stderr == b''

        # converting to Unicode could cause an "ordinal not in range..."
        # exception
        assert stdout == b'non ascii:  just passed it !'
        compat.unicode(stdout)
    
    pytestmark = pytest.mark.scanpy3 #NOQA
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
    
    pytestmark = pytest.mark.scanpy3 #NOQA
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
    
    pytestmark = pytest.mark.scanpy3 #NOQA
    @skipIf(not on_mac, 'Mac only')
    def test_update_path_environment_mac_from_bytes(self):

        class MockOs(object):
            environ = {b'PATH': b'/usr/bin:/usr/local'}
            pathsep = b':'

        bytes_path = b'foo\xb1bar'
        command.update_path_environment(bytes_path, MockOs)
        assert {b'PATH': b'/usr/bin:/usr/local', 'PATH': 'foo\udcb1bar'} == MockOs.environ

        unicode_path = u'/bin/foo\udcb1bar'
        command.update_path_environment(unicode_path, MockOs)
        assert {b'PATH': b'/usr/bin:/usr/local', 'PATH': '/bin/foo\udcb1bar:foo\udcb1bar'} == MockOs.environ

        bytes_path = b'foo\xb1bar'
        command.update_path_environment(bytes_path, MockOs)
        assert {b'PATH': b'/usr/bin:/usr/local', 'PATH': '/bin/foo\udcb1bar:foo\udcb1bar'} == MockOs.environ
    
    pytestmark = pytest.mark.scanpy3 #NOQA
    @skipIf(not on_mac, 'Mac only')
    def test_update_path_environment_mac_from_unicode(self):

        class MockOs(object):
            environ = {b'PATH': b'/usr/bin:/usr/local'}
            pathsep = b':'

        unicode_path = u'foo\udcb1bar'
        command.update_path_environment(unicode_path, MockOs)
        assert {b'PATH': b'/usr/bin:/usr/local', 'PATH': 'foo\udcb1bar'} == MockOs.environ

        bytes_path = b'/bin/foo\xb1bar'
        command.update_path_environment(bytes_path, MockOs)
        assert {b'PATH': b'/usr/bin:/usr/local', 'PATH': '/bin/foo\udcb1bar:foo\udcb1bar'} == MockOs.environ

        unicode_path = u'foo\udcb1bar'
        command.update_path_environment(unicode_path, MockOs)
        assert {b'PATH': b'/usr/bin:/usr/local', 'PATH': '/bin/foo\udcb1bar:foo\udcb1bar'} == MockOs.environ
    
    pytestmark = pytest.mark.scanpy3 #NOQA
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
    
    pytestmark = pytest.mark.scanpy3 #NOQA
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
