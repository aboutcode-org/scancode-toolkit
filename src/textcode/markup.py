# -*- coding: utf-8 -*-
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
import os
import logging

import chardet
import codecs

from commoncode import fileutils
from typecode import contenttype

"""
Extracts plain text from HTML and related files.
"""

logger = logging.getLogger(__name__)

bin_dir = os.path.join(os.path.dirname(__file__), 'bin')


extensions = set(['.html', '.htm', '.php', '.phps', '.jsp', '.jspx'])



def is_markup(location):
    return fileutils.file_extension(location) in extensions


def is_html(location):
    """
    Return True if a file contains html markup.  Used to handle multiple level
    of markup is markup, such as html code highlighted in pygments, that would
    require another pass to extract the actual text. This is really specific
    to code and driven by the fact that code highlighting in HTML is rather
    common such as on Github.
    """
    raise NotImplementedError()


def convert_to_utf8(location):
    """
    Convert the file at location to UTF-8 text.
    Return the location of the converted file or None.
    """
    if not contenttype.get_type(location).is_text:
        return location
    start = open(location, 'rb').read(4096)
    encoding = chardet.detect(start)
    if encoding:
        encoding = encoding.get('encoding', None)
        if encoding:
            target = os.path.join(fileutils.get_temp_dir('markup'),
                                  fileutils.file_name(location))
            with codecs.open(location, 'rb', encoding=encoding,
                             errors='replace', buffering=16384) as inf:
                with codecs.open(target, 'wb', encoding='utf-8') as outf:
                    outf.write(inf.read())
            return target
        else:
            # chardet failed somehow to detect an encoding
            return location


def convert_to_text(location, _retrying=False):
    """
    Convert the markup file at location to plain text.
    Return the location of the converted plain text file or None.
    """
    if not is_markup(location):
        return

    temp_file = os.path.join(fileutils.get_temp_dir('markup'), 'text')
    from bs4 import BeautifulSoup
    with open(location, 'rb') as input_text:
        soup = BeautifulSoup(input_text.read(), 'html5lib')
    with codecs.open(temp_file, mode='wb', encoding='utf-8') as output_text:
        output_text.write(soup.get_text())
    return temp_file
