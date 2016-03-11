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

import unicodedata

import chardet

import typecode.contenttype
from textcode import pdf
from textcode import markup
from textcode import strings
from textcode.strings import remove_non_printable

"""
Utilities to analyze text. Files are the input.
Once a file is read its output are unicode text lines.
All internal processing assumes unicode in and out.
"""


def text_lines(location):
    """
    Return a text lines iterator from file at `location`. Return an empty
    iterator if no text content is extractible. Text extraction is based on
    detected file type.

    Note: For testing or building from strings, location can be a is a list of
    unicode line strings.
    """
    # TODO: add support for "wide" UTF-16-like strings where each char is
    # followed by a zero as is often found in some Windows binaries. Do this for
    # binaries only. This is in direct conflict with "strings" extraction as
    # currently implemented

    if not location:
        return iter([])

    if not isinstance(location, basestring):
        # not a path: wrap an iterator on location which should be a sequence
        # of lines
        return iter(location)

    T = typecode.contenttype.get_type(location)

    if not T.is_file:
        return iter([])

    # Should we read this as some markup, pdf office doc, text or binary?
    if T.is_pdf:
        return unicode_text_lines_from_pdf(location)

# TODO: enable markup stripping support
#     if T.is_doc:
#         return unicode_text_lines_from_markup(location)

#     if markup.is_markup(location):
#         try:
#             new_loc = markup.convert_to_text(location)
#             return unicode_text_lines(new_loc)
#         except:
#             # try again with as plain text
#             pass

    if T.is_text:
        return unicode_text_lines(location)

    if T.is_binary:
        # fall back to binary
        return unicode_text_lines_from_binary(location)

    else:
        # if neither text, text-like nor binary: return empty
        # this should never happen
        return iter([])


def unicode_text_lines_from_binary(location):
    """
    Return an iterable over unicode text lines extracted from a binary file at
    location.
    """
    as_unicodef = as_unicode
    for line in strings.strings_in_file(location, filt=strings.filter_strict):
        yield as_unicodef(line)


def unicode_text_lines_from_pdf(location):
    """
    Return an iterable over unicode text lines extracted from a pdf file at
    location.
    """
    as_unicodef = as_unicode
    for line in pdf.get_text_lines(location):
        yield as_unicodef(line)


def as_unicode(line):
    """
    Return a unicode text line from a text line.
    Try to decode line as Unicode. Try first some default encodings,
    then attempt Unicode trans-literation and finally
    fall-back to ASCII strings extraction.

    TODO: Add file/magic detection, unicodedmanit/BS3/4 and chardet
    """
    unicodedata_normalize = unicodedata.normalize
    chardet_detect = chardet.detect
    try:
        s = unicode(line, 'utf-8')
    except UnicodeDecodeError:
        try:
            # FIXME: latin-1 may never fail
            s = unicode(line, 'latin-1')
        except UnicodeDecodeError:
            try:
                # Convert some byte string to ASCII characters as
                # Unicode including replacing accented characters with
                # their non- accented NFKD equivalent. Non ISO-Latin
                # and non ASCII characters are stripped from the
                # output. Does not preserve the original length
                # offsets. For Unicode NFKD equivalence, see:
                # http://en.wikipedia.org/wiki/Unicode_equivalence
                s = unicodedata_normalize('NFKD', line).encode('ASCII')
            except UnicodeDecodeError:
                try:
                    enc = chardet_detect(line)['encoding']
                    s = unicode(line, enc)
                except UnicodeDecodeError:
                    # fall-back to strings extraction if all else
                    # fails
                    s = unicode(remove_non_printable(s))
    return s


def unicode_text_lines(location):
    """
    Return an iterable over unicode text lines from a text file at location.
    Open the file as binary with universal new lines then try to decode each
    line as Unicode.
    """
    as_unicodef = as_unicode
    with open(location, 'rbU') as f:
        for line in f:
            yield as_unicodef(line)


def unicode_text(location):
    """
    Return a string guaranteed to be unicode from the content of the file at
    location. The whole file content is returned at once, which may be a
    problem for very large files.
    """
    return u''.join(unicode_text_lines(location))
