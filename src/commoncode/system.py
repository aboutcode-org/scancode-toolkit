#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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

from __future__ import print_function, absolute_import, unicode_literals

import sys
import os
import getpass
import subprocess


def os_arch():
    """
    Return a tuple for the current the OS and architecture.
    """
    if sys.maxsize > 2 ** 32:
        arch = '64'
    else:
        arch = '32'

    sys_platform = str(sys.platform).lower()
    if sys_platform.startswith('linux'):
        os = 'linux'
    elif 'win32' in sys_platform:
        os = 'win'
    elif 'darwin' in sys_platform:
        os = 'mac'
    elif 'freebsd' in sys_platform:
        os = 'freebsd'
    else:
        raise Exception('Unsupported OS/platform %r' % sys_platform)
    return os, arch

#
# OS/Arch
#
current_os, current_arch = os_arch()
on_windows = current_os == 'win'
on_mac = current_os == 'mac'
on_linux = current_os == 'linux'
on_freebsd = current_os == 'freebsd'
on_posix = not on_windows and (on_mac or on_linux or on_freebsd)

current_os_arch = '%(current_os)s-%(current_arch)s' % locals()
noarch = 'noarch'
current_os_noarch = '%(current_os)s-%(noarch)s' % locals()

del os_arch


def is_on_macos_14_or_higher():
    """
    Return True if the current OS is macPS 14 or higher.
    It uses APFS by default and has a different behavior wrt. unicode and
    filesystem encodings.
    """
    import platform
    macos_ver = platform.mac_ver()
    macos_ver = macos_ver[0]
    macos_ver = macos_ver.split('.')
    return macos_ver > ['10', '14']

on_macos_14_or_higher = is_on_macos_14_or_higher()

del is_on_macos_14_or_higher

#
# Shared library file extensions
#
if on_windows:
    lib_ext = '.dll'
if on_mac:
    lib_ext = '.dylib'
if on_linux or on_freebsd:
    lib_ext = '.so'

#
# Python versions
#
_sys_v0 = sys.version_info[0]
py2 = _sys_v0 == 2
py3 = _sys_v0 == 3

_sys_v1 = sys.version_info[1]
py27 = py2 and _sys_v1 == 7
py34 = py3 and _sys_v1 == 4
py35 = py3 and _sys_v1 == 5
py36 = py3 and _sys_v1 == 6
py37 = py3 and _sys_v1 == 7

#these are used together in many places
py2_with_linux = py2 and on_linux

# Do not let Windows error pop up messages with default SetErrorMode
# See http://msdn.microsoft.com/en-us/library/ms680621(VS100).aspx
#
# SEM_FAILCRITICALERRORS:
# The system does not display the critical-error-handler message box.
# Instead, the system sends the error to the calling process.
#
# SEM_NOGPFAULTERRORBOX:
# The system does not display the Windows Error Reporting dialog.
if on_windows:
    import ctypes
    # 3 is SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX
    ctypes.windll.kernel32.SetErrorMode(3)  # @UndefinedVariable
