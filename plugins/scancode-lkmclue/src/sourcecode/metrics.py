#
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
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


import typecode
from commoncode.filetype import counter
from commoncode.functional import memoize
from commoncode import filetype


@memoize
def file_lines_count(location):
    """
    Return a tuple of (code, comment) line counts in a source text file at
    `location`. Memoization guarantees that we do only one pass on a file.
    """

    code = 0
    comment = 0

    T = typecode.contenttype.get_type(location)
    if not T.is_source:
        return code, comment

    with open(location, 'rb') as lines:
        for line in lines:
            ls = line.strip()
            if ls:
                # TODO implement a better comment function
                if ls.startswith(('/', '#', '@rem', ';', '*',)):
                    comment += 1
                else:
                    code += 1
    return code, comment


def code_lines_count(location):
    code, _comment = file_lines_count(location)
    return code


def comment_lines_count(location):
    _code, comment = file_lines_count(location)
    return comment


filetype.counting_functions.update({
    'code_lines': code_lines_count,
    'comment_lines': comment_lines_count
})


def get_code_lines_count(location):
    """
    Return the cumulative number of lines of code in the whole directory tree
    at `location`. Use 0 if `location` is not a source file.
    """
    return counter(location, 'code_lines')


def get_comment_lines_count(location):
    """
    Return the cumulative number of lines of comments in the whole directory
    tree at `location`. Use 0 if `location` is not a source file.
    """
    return counter(location, 'comment_lines')
