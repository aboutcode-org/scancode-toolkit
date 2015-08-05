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

import logging
import os
from os.path import join

from commoncode import filetype
import typecode.contenttype

from packagedcode import models


logger = logging.getLogger(__name__)


"""
Package recognizers are used to recognize one or more packages in a directory.

A recognizer is a class with a "recon" method:
 - accepting a directory location as an input.
 - returning an iterable of Package objects.

The contract for this method is that the location can be walked down or up
reasonably, if and only if there is some clues found immediately in the provided
directory location that can be confirmed by navigating up or down the tree.
The location is always an absolute path that includes the root of the scanned
codebase.
"""


class ArchiveRecognizer(object):
    """
    A package recognizer for archive-based packages.
    """
    def recon(self, location):
        for f in  os.listdir(location):
            loc = join(location, f)
            parch = packaged_archive(loc)
            if parch:
                yield parch


def packaged_archive(location):
    """
    Return a Package object if one wass recognized or None for this `location`.
    """
    if not filetype.is_file(location):
        return

    T = typecode.contenttype.get_type(location)
    ftype = T.filetype_file.lower()
    mtype = T.mimetype_file

    for package in models.PACKAGE_TYPES:
        if not package.packaging == models.Package.as_archive:
            continue

        # we default to True if there is nothing to match against
        if package.filetypes:
            type_matched = any(t in ftype for t in package.filetypes)
        else:
            type_matched = True

        # we default to True if there is nothing to match against
        if package.mimetypes:
            mime_matched = any(m in mtype for m in package.mimetypes)
        else:
            mime_matched = True

        # we default to True if there is nothing to match against
        if package.extensions:
            extension_matched = location.lower().endswith(package.extensions)
        else:
            extension_matched = True

        if type_matched and mime_matched and extension_matched:
            # we return the first match in the sequence:
            # the order of PACKAGE_TYPES matters
            return package(location)
