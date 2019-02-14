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

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from commoncode import fileutils

"""
Recognition of typical "legal" files such as "LICENSE", "COPYING", etc.
"""

special_names = (
    'COPYING', 'COPYRIGHT', 'NOTICE', 'LICENSE', 'LICENCE',
    'LEGAL', 'EULA', 'AGREEMENT', 'ABOUT', 'COPYLEFT', 'LICENSING')

special_names_lower = tuple(x.lower() for x in special_names)


def is_special_legal_file(location):
    """
    Return an indication that a file may be a "special" legal-like file.
    """
    file_base_name = fileutils.file_base_name(location).lower()
    file_extension = fileutils.file_extension(location).lower()

    if (any(special_name == file_base_name
            or special_name == file_extension
            for special_name in special_names_lower)
     or any(special_name in file_base_name
            or special_name in file_extension
            for special_name in special_names)):
        return 'yes'

    elif any(special_name in file_base_name
             or special_name in file_extension
            for special_name in special_names_lower):
        return 'maybe'
    else:
        # return False for now?
        pass
