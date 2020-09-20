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
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


"""
Note: this API is unstable and still evolving.
"""


def extract_archives(location, recurse=True, replace_originals=False, ignore_pattern=()):
    """
    Yield ExtractEvent while extracting archive(s) and compressed files at
    `location`. If `recurse` is True, extract nested archives-in-archives
    recursively.
    Archives and compressed files are extracted in a directory named
    "<file_name>-extract" created in the same directory as the archive.
    Note: this API is returning an iterable and NOT a sequence.
    """
    from extractcode.extract import extract
    from extractcode import default_kinds
    for xevent in extract(
        location=location,
        kinds=default_kinds,
        recurse=recurse,
        replace_originals=replace_originals,
        ignore_pattern=ignore_pattern
    ):
        yield xevent
