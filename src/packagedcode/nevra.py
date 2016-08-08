#
# Copyright (c) 2016 nexB Inc. and others. All rights reserved.
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

import re

from commoncode import fileutils


"""
Utilities to handle RPM NEVRA (name, epoch, version, release, architecture)
"""

# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# modified and originally from:
# https://raw.githubusercontent.com/sassoftware/conary/c26507001b62b0839539908cc5bf28893c45c0b4/conary/rpmhelper.py

def from_name(filename):
    """
    Return an (E, N, V, R, A) tuple given a file name, by splitting
    [e:]name-version-release.arch into the four possible subcomponents.
    Default epoch, version, release and arch to None if not specified.
    Accepts RPM names with and without extensions
    """
    _re = re.compile("^(.*)-([^-]*)-([^-]*)\.([^.]*)$")
    file_ext = fileutils.file_extension(filename) or None
    if file_ext in ['.rpm', 'srpm']:
        filename = filename[:-len(file_ext)]
    m = _re.match(filename)
    if not m:
        return None
    n, v, r, a = m.groups()
    if file_ext == '.srpm':
        a = 'src'
    if ':' not in v:
        return None, n, v, r, a
    e, v = v.split(':', 1)
    e = int(e)
    return (e, n, v, r, a)
