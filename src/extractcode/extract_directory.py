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

from __future__ import print_function, absolute_import

from collections import namedtuple
from functools import partial
import logging
from os.path import abspath
from os.path import expanduser
from os.path import join

from commoncode import fileutils
from commoncode import ignore
import extractcode
from extractcode import archive
from extractcode import extract
import os

logger = logging.getLogger(__name__)
TRACE = False

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


def extract_directory(resources, kinds=extractcode.default_kinds, recurse=True):
    """
    Walk and extract any archives found at `location` (either a file or
    directory). Extract only archives of a kind listed in the `kinds` kind tuple.

    Return an iterable of ExtractEvent tuples for each extracted archive. This
    can be used to track extraction progress:

     - one event is emitted just before extracting an archive. The ExtractEvent
       warnings and errors are empty. The `done` flag is False.

     - one event is emitted right after extracting an archive. The ExtractEvent
       warnings and errors contains warnings and errors if any. The `done` flag
       is True.

    If `recurse` is True, extract recursively archives nested inside other
    archives If `recurse` is false, then do not extract further an already
    extracted archive identified by the corresponding extract suffix location.

    Note that while the original file system is walked top-down, breadth-first,
    if recurse and a nested archive is found, it is extracted to full depth
    first before resuming the file system walk.
    """
    for file in resources:
        if archive.can_extract(file):
            #TODO : Implement Extraction of Files without printing to the Terminal
            for y in extract(file, kinds=kinds, recurse=recurse):
                pass
