#
# Copyright (c) nexB Inc. and others. All rights reserved.
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

"""
Utilities to detect is a file is extractible.
We prefer using extractcode support if available.
Otherwise we use the standard library available archive and compressed files support.
"""

try:
    from extractcode.archive import can_extract  # NOQA
except ImportError:

    from functools import partial
    import bz2
    import gzip
    import os
    import tarfile
    import zipfile

    def _is_compressed(location, opener):
        if os.path.isfile(location):
            try:
                with opener(location) as comp:
                    comp.read()
                return True
            except Exception:
                return False

    is_gzipfile = partial(_is_compressed, opener=gzip.open)

    is_bz2file = partial(_is_compressed, opener=bz2.open)

    try:
        import lzma
        is_lzmafile = partial(_is_compressed, opener=lzma.open)
    except ImportError:
        is_lzmafile = lambda _: False
        lzma = None

    # Each function accept a single location argument and return True if this is
    # an archive
    archive_handlers = [
        zipfile.is_zipfile,
        tarfile.is_tarfile,
        is_gzipfile,
        is_gzipfile,
        is_lzmafile
    ]

    def can_extract(location):
        """
        Return True if this location is likely to be extractible as some archive
        or compressed file.
        """
        return any(handler(location) for handler in archive_handlers)
