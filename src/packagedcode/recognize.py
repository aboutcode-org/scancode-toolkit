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

import logging

from commoncode import filetype
from typecode import contenttype

from packagedcode import PACKAGE_TYPES


logger = logging.getLogger(__name__)


"""
Recognize packages in files or directories.
"""


def recognize_packaged_archives(location):
    """
    Return a Package object if one was recognized or None for this `location`.
    """
    if not filetype.is_file(location):
        return

    T = contenttype.get_type(location)
    ftype = T.filetype_file.lower()
    mtype = T.mimetype_file

    for package in PACKAGE_TYPES:
        # Note: default to True if there is nothing to match against
        if location.endswith(tuple(package.metafiles)):
            return package.recognize(location)

        if package.filetypes:
            type_matched = any(t in ftype for t in package.filetypes)
        else:
            type_matched = False
        if package.mimetypes:
            mime_matched = any(m in mtype for m in package.mimetypes)
        else:
            mime_matched = False

        if package.extensions:
            extension_matched = location.lower().endswith(package.extensions)
        else:
            extension_matched = False

        if type_matched and mime_matched and extension_matched:
            # we return the first match in the order of PACKAGE_TYPES
            return package(location=location)
