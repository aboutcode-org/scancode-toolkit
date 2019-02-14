#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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

import re
import string

from commoncode.text import toascii

"""
Extract raw ASCII strings from (possibly) binary strings.
Both plain ASCII and UTF-16-LE-encoded (aka. wide) strings are extracted.
The later is found typically in some Windows PEs.

This is more or less similar to what GNU Binutils strings does.

Does not recognize and extract non-ASCII characters

Some alternative and references:
https://github.com/fireeye/flare-floss (also included)
http://stackoverflow.com/questions/10637055/how-do-i-extract-unicode-character-sequences-from-an-mz-executable-file
http://stackoverflow.com/questions/1324067/how-do-i-get-str-translate-to-work-with-unicode-strings
http://stackoverflow.com/questions/11066400/remove-punctuation-from-unicode-formatted-strings/11066687#11066687
https://github.com/TakahiroHaruyama/openioc_scan/blob/d7e8c5962f77f55f9a5d34dbfd0799f8c57eff7f/openioc_scan.py#L184
"""

# at least four characters are needed to consider some blob as a good string
# this is the same default as GNU strings
MIN_LEN = 4


def strings_from_file(location, buff_size=1024 * 1024, ascii=False, clean=True, min_len=MIN_LEN):
    """
    Yield unicode strings made only of ASCII characters found in file at location.
    Process the file in chunks (to limit memory usage). If ascii is True, strings
    are converted to plain ASCII "str or byte" strings instead of unicode.
    """
    with open(location, 'rb') as f:
        while 1:
            buf = f.read(buff_size)
            if not buf:
                break
            for s in strings_from_string(buf, clean=clean, min_len=min_len):
                if ascii:
                    s = toascii(s)
                s = s.strip()
                if len(s) >= min_len:
                    yield s


# Extracted text is digit, letters, punctuation and white spaces
punctuation = re.escape(string.punctuation)
whitespaces = ' \t\n\r'
printable = 'A-Za-z0-9' + whitespaces + punctuation
null_byte = '\x00'

ascii_strings = re.compile(
    # plain ASCII is a sequence of printable of a minimum length
      '('
    + '[' + printable + ']'
    + '{' + str(MIN_LEN) + ',}'
    + ')'
    # or utf-16-le-encoded ASCII is a sequence of ASCII+null byte
    + '|'
    + '('
    + '(?:' + '[' + printable + ']' + null_byte + ')'
    + '{' + str(MIN_LEN) + ',}'
    + ')'
    ).finditer


def strings_from_string(binary_string, clean=False, min_len=0):
    """
    Yield strings extracted from a (possibly binary) string. The strings are ASCII
    printable characters only. If clean is True, also clean and filter short and
    repeated strings.
    Note: we do not keep the offset of where a string was found (e.g. match.start).
    """
    for match in ascii_strings(binary_string):
        s = decode(match.group())
        if not s:
            continue
        s = s.strip()
        if len(s) < min_len:
            continue
        if clean:
            for ss in clean_string(s, min_len=min_len):
                yield ss
        else:
            yield s


def string_from_string(binary_string, clean=False, min_len=0):
    """
    Return a unicode string string extracted from a (possibly binary) string,
    removing all non printable characters.
    """
    return u' '.join(strings_from_string(binary_string, clean, min_len))


def decode(s):
    """
    Return a decoded unicode string from s or None if the string cannot be decoded.
    """
    if '\x00' in s:
        try:
            return s.decode('utf-16-le')
        except UnicodeDecodeError:
            pass
    else:
        return s.decode('ascii')


remove_junk = re.compile('[' + punctuation + whitespaces + ']').sub

JUNK = frozenset(string.punctuation + string.digits + string.whitespace)

def clean_string(s, min_len=MIN_LEN, junk=JUNK):
    """
    Yield cleaned strings from string s if it passes some validity tests:
     * not made of white spaces
     * with a minimum length ignoring spaces and punctuations
     * not made of only two repeated character
     * not made of only of digits, punctuations and whitespaces
    """
    s = s.strip()

    def valid(st):
        st = remove_junk('', st)
        return (st and len(st) >= min_len
                # ignore character repeats, e.g need more than two unique characters
                and len(set(st.lower())) > 1
                # ignore string made only of digits, spaces or punctuations
                and not all(c in junk for c in st))

    if valid(s):
        yield s.strip()

#####################################################################################
# TODO: Strings classification
# Classify strings, detect junk, detect paths, symbols, demangle symbols, unescape
# http://code.activestate.com/recipes/466293-efficient-character-escapes-decoding/?in=user-2382677


def is_file(s):
    """
    Return True if s looks like a file name.
    Exmaple: dsdsd.dll
    """
    filename = re.compile('^[\w_\-]+\.\w{1,4}$', re.IGNORECASE).match
    return filename(s)


def is_shared_object(s):
    """
    Return True if s looks like a shared object file.
    Example: librt.so.1
    """
    so = re.compile('^[\w_\-]+\.so\.[0-9]+\.*.[0-9]*$', re.IGNORECASE).match
    return so(s)


def is_posix_path(s):
    """
    Return True if s looks like a posix path.
    Example: /usr/lib/librt.so.1 or /usr/lib
    """
    # TODO: implement me
    posix = re.compile('^/[\w_\-].*$', re.IGNORECASE).match
    posix(s)
    return False


def is_relative_path(s):
    """
    Return True if s looks like a relative posix path.
    Example: usr/lib/librt.so.1 or ../usr/lib
    """
    relative = re.compile('^(?:([^/]|\.\.)[\w_\-]+/.*$', re.IGNORECASE).match
    return relative(s)


def is_win_path(s):
    """
    Return True if s looks like a win path.
    Example: c:\usr\lib\librt.so.1.
    """
    winpath = re.compile('^[\w_\-]+\.so\.[0-9]+\.*.[0-9]*$', re.IGNORECASE).match
    return winpath(s)


def is_c_source(s):
    """
    Return True if s looks like a C source path.
    Example: this.c
    FIXME: should get actual algo from contenttype.
    """
    return s.endswith(('.c', '.cpp', '.hpp', '.h'))


def is_java_source(s):
    """
    Return True if s looks like a Java source path.
    Example: this.java
    FIXME: should get actual algo from contenttype.
    """
    return s.endswith(('.java', '.jsp', '.aj',))


def is_glibc_ref(s):
    """
    Return True if s looks like a reference to GLIBC as typically found in
    Elfs.
    """
    return '@@GLIBC' in s


def is_java_ref(s):
    """
    Return True if s looks like a reference to a java class or package in a
    class file.
    """
    jref = re.compile('^.*$', re.IGNORECASE).match
    # TODO: implement me
    jref(s)
    return False


def is_win_guid(s):
    """
    Return True if s looks like a windows GUID/APPID/CLSID.
    """
    guid = re.compile('"\{[A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12}\}"', re.IGNORECASE).match
    # TODO: implement me
    guid(s)
    return False


class BinaryStringsClassifier(object):
    """
    Classify  extracted strings as good or bad/junk.
    The types of strings that are recognized include:
    file
    file_path
    junk
    text
    """
    # TODO: Implement me


# TODO: a new approach to more aggressively filter strings
def filter_strings(strs, nglen=4):
    """
    Filter cluster of short strings.
    If a string two previous and next neighbors and itself have a
    small length less than mlen, discard that string.
    """
    from licensedcode.tokenize import ngrams
    # FIXME: the ngrams function skips things if we have less than ngram_len strings
    strs = list(strs)
    if len(strs) < nglen:
        for s in strs:
            yield s
    else:
        for ngm in ngrams(strs, nglen):
            junk = (all(len(s) <= 5 for s in ngm)
                   or sum(len(s) for s in ngm) <= nglen * 5
                   or len(set(ngm[0])) / float(len(ngm[0])) < 0.01)
            if junk:
                continue
            yield ngm[0]


if __name__ == '__main__':
    # also usable a simple command line script
    import sys
    location = sys.argv[1]
    for s in strings_from_file(location):
        print(s)
