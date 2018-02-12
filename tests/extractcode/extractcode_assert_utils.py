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
from commoncode import filetype
from commoncode import fileutils

"""
Shared archiving test utils.
"""


def check_size(expected_size, location):
    assert expected_size == os.stat(location).st_size


def check_files(test_dir, expected):
    """
    Walk test_dir.
    Check that all dirs are readable.
    Check that all files are:
     * non-special,
     * readable,
     * have a posix path that ends with one of the expected tuple paths.
    """
    result = []
    locs = []
    if filetype.is_file(test_dir):
        test_dir = fileutils.parent_directory(test_dir)

    test_dir_path = fileutils.as_posixpath(test_dir)
    for top, _, files in os.walk(test_dir):
        for f in files:
            location = os.path.join(top, f)
            locs.append(location)
            path = fileutils.as_posixpath(location)
            path = path.replace(test_dir_path, '').strip('/')
            result.append(path)

    assert sorted(expected) == sorted(result)

    for location in locs:
        assert filetype.is_file(location)
        assert not filetype.is_special(location)
        assert filetype.is_readable(location)


def check_no_error(result):
    """
    Check that every ExtractEvent in the `result` list has no error or warning.
    """
    for r in result:
        assert not r.errors
        assert not r.warnings
