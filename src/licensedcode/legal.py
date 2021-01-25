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

from commoncode import fileutils

"""
Recognition of typical "legal" files such as "LICENSE", "COPYING", etc.
"""

special_names = (
    'COPYING',
    'COPYRIGHT',
    'COPYRIGHTS',
    'NOTICE',
    'NOTICES',
    'LICENSE',
    'LICENCE',
    'LICENSES',
    'LICENCES',
    'LICENSING',
    'LICENCING',
    'COPYLEFT',
    'LEGAL',
    'EULA',
    'AGREEMENT',
    'AGREEMENTS',
    'ABOUT',
    'UNLICENSE',
    'COMMITMENT'
    'COMMITMENTS'
)


special_names_lower = tuple(x.lower() for x in special_names)


def is_special_legal_file(location):
    """
    Return an indication that a file may be a "special" legal-like file.
    """
    file_base_name = fileutils.file_base_name(location)
    file_base_name_lower = file_base_name.lower()
    file_extension = fileutils.file_extension(location)
    file_extension_lower = file_extension.lower()

    name_contains_special = (
        special_name in file_base_name or
        special_name in file_extension
            for special_name in special_names
    )

    name_lower_is_special = (
        special_name_lower == file_base_name_lower or
        special_name_lower == file_extension_lower
            for special_name_lower in special_names_lower
    )

    name_lower_contains_special = (
        special_name_lower in file_base_name_lower or
        special_name_lower in file_extension_lower
            for special_name_lower in special_names_lower
    )

    if any(name_contains_special) or any(name_lower_is_special):
        return 'yes'

    elif any(name_lower_contains_special):
        return 'maybe'
    else:
        # return False for now?
        pass
