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

from __future__ import print_function, absolute_import

import logging
import os
import gzip

# These imports add support for multistream BZ2 files
# This is a Python2 backport for bz2file from Python3
# Because of http://bugs.python.org/issue20781
from bz2file import BZ2File

from extractcode import EXTRACT_SUFFIX

DEBUG = False
logger = logging.getLogger(__name__)
# import sys
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# logger.setLevel(logging.DEBUG)


def uncompress(location, target_dir, decompressor, suffix=EXTRACT_SUFFIX):
    """
    Uncompress a compressed file at location in the target_dir using the
    `decompressor` object. The uncompressed file is named after the original
    archive with a `suffix` added.
    Return a list of warning messages. Raise Exceptions on errors.
    """
    # FIXME: do not create a sub-directory and instead strip the "compression"
    # extension such gz, etc. or introspect the archive header to get the file
    # name when present.
    assert location
    assert target_dir
    assert decompressor

    if DEBUG:
        logger.debug('uncompress: ' + location)
    warnings = []
    target_location = os.path.join(target_dir, os.path.basename(location) + suffix)
    with decompressor(location, 'rb') as compressed:
        with open(target_location, 'wb') as uncompressed:
            chunk = compressed.read()
            uncompressed.write(chunk)
        if getattr(decompressor, 'has_trailing_garbage', False):
            warnings.append(location +': Trailing garbage found and ignored.')
    return warnings


class GzipFileWithTrailing(gzip.GzipFile):
    """
    A subclass of gzip.GzipFile supporting files with trailing garbage. Ignore
    the garbage.
    """
    # TODO: what is first_file??
    first_file = True
    gzip_magic = '\037\213'
    has_trailing_garbage = False

    def _read_gzip_header(self):
        # read the first two bytes
        magic = self.fileobj.read(2)
        # rewind two bytes back
        self.fileobj.seek(-2, os.SEEK_CUR)

        is_gzip = magic != self.gzip_magic

        if is_gzip and not self.first_file:
            self.first_file = False
            self.has_trailing_garbage = True
            raise EOFError, 'Trailing garbage found'

        self.first_file = False
        gzip.GzipFile._read_gzip_header(self)


def uncompress_gzip(location, target_dir):
    """
    Uncompress a gzip compressed file at location in the target_dir.
    Return a warnings mapping of path -> warning.
    """
    return uncompress(location, target_dir, GzipFileWithTrailing)


def uncompress_bzip2(location, target_dir):
    """
    Uncompress a bzip2 compressed file at location in the target_dir.
    Return a warnings mapping of path->warning.
    """
    return uncompress(location, target_dir, BZ2File)
