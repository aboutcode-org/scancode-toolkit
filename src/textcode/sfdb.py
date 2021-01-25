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

"""
Specialized processing for Spline Font Database files from Fontforge
https://fontforge.github.io/en-US/documentation/developers/sfdformat/
"""


def get_text_lines(location):
    """
    Return a list of unicode text lines extracted from a spline font DB file at
    `location`.
    """
    interesting_lines = (
        b'Copyright:', b'LangName:',
        b'FontName:', b'FullName:',
        b'FamilyName:', b'Version:',
    )
    with open(location, 'rb') as sfdb_file:
        for line in sfdb_file:
            if line.startswith(interesting_lines):
                yield line
