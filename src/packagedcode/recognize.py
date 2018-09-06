#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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

import fnmatch
import logging
import sys

from commoncode import filetype
from commoncode.fileutils import file_name
from commoncode.fileutils import fsencode
from commoncode.fileutils import splitext_name
from commoncode.system import on_linux
from packagedcode import PACKAGE_TYPES
from typecode import contenttype

TRACE = False

logger = logging.getLogger(__name__)


def logger_debug(*args):
    pass


if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))

"""
Recognize package manifests in files.
"""


def recognize_package(location):
    """
    Return a Package object if one was recognized for this `location` or None.
    Raises Exceptions on errors.
    """

    if not filetype.is_file(location):
        return

    T = contenttype.get_type(location)
    ftype = T.filetype_file.lower()
    mtype = T.mimetype_file

    _base_name, extension = splitext_name(location, is_file=True)
    filename = file_name(location)
    extension = extension.lower()

    if TRACE:
        logger_debug('recognize_package: ftype:', ftype, 'mtype:', mtype,
                     'pygtype:', T.filetype_pygment,
                     'fname:', filename, 'ext:', extension)

    for package_type in PACKAGE_TYPES:
        # Note: default to True if there is nothing to match against
        metafiles = package_type.metafiles
        if on_linux:
            metafiles = (fsencode(m) for m in metafiles)

        if any(fnmatch.fnmatchcase(filename, metaf) for metaf in metafiles):
            recognized = package_type.recognize(location)
            if TRACE:
                logger_debug('recognize_package: metafile matching: '
                             'package is of type:', package_type,
                             'recognized as:', repr(recognized))
            return recognized

        type_matched = False
        if package_type.filetypes:
            type_matched = any(t in ftype for t in package_type.filetypes)

        mime_matched = False
        if package_type.mimetypes:
            mime_matched = any(m in mtype for m in package_type.mimetypes)

        extension_matched = False
        extensions = package_type.extensions
        if extensions:
            if on_linux:
                extensions = (fsencode(e) for e in extensions)
            extensions = (e.lower() for e in extensions)
            extension_matched = any(
                fnmatch.fnmatchcase(extension, ext_pat) for ext_pat in extensions)

        if type_matched and mime_matched and extension_matched:
            if TRACE:
                logger_debug('recognize_package: all matching')
            # we return the first match in the order of PACKAGE_TYPES
            try:
                recognized = package_type.recognize(location)
            except NotImplementedError:
                # build a plain package if recognize is not yet implemented
                recognized = package_type()
            if TRACE:
                logger_debug(
                    'recognize_package:'
                    'package is of type:', package_type,
                    'recognized as:', repr(recognized))
            return recognized

        if TRACE:
            logger_debug('recognize_package: no match for type:', package_type)
