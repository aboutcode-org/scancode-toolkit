#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#
# Visit https://aboutcode.org and https://github.com/nexB/scancode-toolkit for
# support and download. ScanCode is a trademark of nexB Inc.
#
# The ScanCode software is licensed under the Apache License version 2.0.
# The ScanCode open data is licensed under CC-BY-4.0.
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
    parse_nevra = re.compile("^(.*)-([^-]*)-([^-]*)\\.([^.]*)$").match
    file_ext = fileutils.file_extension(filename) or None
    if file_ext in ['.rpm', '.srpm']:
        filename = filename[:-len(file_ext)]
    m = parse_nevra(filename)
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
