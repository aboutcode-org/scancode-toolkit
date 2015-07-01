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
import string
import re

from commoncode.text import toascii


"""
Extract ASCII strings from a (possibly) binary string.

Use character translations tables for this, replacing all non-printable
characters by a newline char.
Then split on lines, yield these lines filtering out junk strings.
This is similar to what GNU Binutils strings does.
TODO: Add support for some additional and common strings-inbinary encodings
such ass UTC-16 in Windows binary executables.
"""


"""
Definition of non printable text: Remove digit,letters, punctuation and white
spaces, all the rest is junk.

Note: we replace also \r and \f with a newline. Since \r will be replaced by a
new line, some empty lines are possible, which is not a problem.

The fact that strings could be null-terminated is handled since the null is
also replaced by a newline.

The translation table is:
    0123456789abcdefghijklmnopqrstuvwxyz
    ABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \n
"""
allchars = string.maketrans('', '')
non_printable = string.translate(allchars, allchars,
                                 string.digits
                                 + string.letters
                                 + string.punctuation
                                 + ' \t\n')


"""
This create a translation table to replace junk chars with a newline char
"""
printable = string.maketrans(non_printable, '\n' * len(non_printable))


# this is heart of the code... a one liner
def strings(binary_string):
    """
    Return a list of strings extracted from a binary string.
    """
    return lines(remove_non_printable(binary_string))


def lines(s):
    for x in s.splitlines():
        yield x


def remove_non_printable(binary_string):
    """
    Returns an ASCII printable string for a binary string, removing all non
    printable characters.
    """
    return binary_string.translate(printable)


def file_strings(location, buff_size=1024 * 1024):
    """
    Process (eventually large) files in chunks and yield ASCII strings found
    in file as location, encoded as Unicode.
    """
    file_size = os.path.getsize(location)
    count = 0
    with open(location, 'rb') as f:
        while True:
            start = f.tell()
            buf = f.read(buff_size)
            count += 1
            if not buf or not buf.strip():
                break
            s = remove_non_printable(buf)

            if file_size >= buff_size * count:
                # if the last char is not a '\n' we need to backtrack to avoid
                # truncating lines in the middle
                last_ln_end = s.rfind('\n')
                # what if we did not find any??
                # in this case we likely need to read forward instead of
                # backward since this is a very unlikely event, we are just
                # yielding what we have
                if last_ln_end != -1:
                    to_truncate = len(s) - last_ln_end
                    back_pos = start - to_truncate
                    f.seek(back_pos, os.SEEK_CUR)
                    s = s[:last_ln_end + 1]

            for l in s.splitlines():
                ls = l.strip()
                if ls:
                    yield ls

#
# Junk strings filtering
#

# Filters accept or reject a string: a filtering function returns True if the
# strings needs to be filtered out

non_chars = string.translate(allchars, allchars, string.letters)
letters = string.maketrans(non_chars, ' ' * len(non_chars))


def filter_string(S, min_length=2):
    """
    Filters strings composed of :
     * only one repeated character
     * only short tokens
    """
    tok = del_special(S)
    tok = tok.translate(letters)
    tok = tok.strip().lower().split()

    if S:
        repeat = S[0]
    else:
        repeat = ' '
    return (all(len(x) <= min_length for x in tok)
            or all(x == repeat for x in list(S)))


def filter_strict(S):
    return filter_string (S, min_length=4)


# Ensure certain short strings are not filtered out
token_to_keep = set(
    (
     # elf related
     'gnu',
     'gnu as',
     'elf',
     'rel',
     'dyn',
     'jcr',
     'dot',
     'jss',
     'plt',
     'bss',
     'jcr',
     'end',
     'die',
     # license related
     'gpl',
     'mit',
     'bsd',
     '(c)',
     )
)


def to_keep(S):
    """
    Keeps strings that are in a reference set.
    """
    return S.lower() in token_to_keep


def is_good(S, filt=filter_string):
    """
    Returns True if if string is a keeper or False if filtered.
    """
    if not S:
        return False
    return to_keep(S) or not filt(S)

#
# transformers change the content of strings
#

# TODO: add c++ demangling, etc)
def del_special(S):
    """
    Replace verbatim white space lien endings and tabs (\\n, \\r, \\t) that
    may exist as-is as literals in the extracted string by a space.
    """
    return S.replace('\\r', ' ').replace('\\n', ' ').replace('\\t', ' ')


def is_mangled_ccp(S):  # @UnusedVariable
    return False


def demangle_cpp(S):
    return S


def is_mangled_java(S):  # @UnusedVariable
    return False


def demangle_java(S):
    return S


def strings_in_file(location, filt=filter_string):
    """
    Yield ASCCI strings encoded as Unicode extracted from a file at location.
    """
    for s in file_strings(location):
        if is_good(s, filt):
            s = s.strip()
            if s:
                yield toascii(s)


# http://code.activestate.com/recipes/466293-efficient-character-escapes-decoding/?in=user-2382677
# classifiers detect specific patterns in the strings
# TODO: add path detection, etc
# Detect paths and file names

def FILE_RE():
    return re.compile('^[\w_\-]+\.\w{1,4}$', re.IGNORECASE)


def is_file(S):
    """
    Return True is S looks like a file name.
    Exmaple: dsdsd.dll
    """
    return 'file-name' if re.match(FILE_RE(), S) else None


def SO_RE():
    return re.compile('^[\w_\-]+\.so\.[0-9]+\.*.[0-9]*$', re.IGNORECASE)

def is_shared_object(S):
    """
    Return True is S looks like a shared object file.
    Example: librt.so.1
    """
    return 'elf-shared-object' if re.match(SO_RE(), S) else None


def POSIXPATH_RE():
    return re.compile('^[\w_\-]+\.so\.[0-9]+\.*.[0-9]*$', re.IGNORECASE)

def is_posix_path(S):
    """
    Return True is S looks like a posix path.
    Example: /usr/lib/librt.so.1 or usr/lib
    """
    return re.match(POSIXPATH_RE(), S)


def RELATIVE_RE():
    return re.compile('^[\w_\-]+\.so\.[0-9]+\.*.[0-9]*$', re.IGNORECASE)

def is_relative_path(S):
    """
    Return True is S looks like a relative posix path.
    Example: usr/lib/librt.so.1 or ../usr/lib
    """
    return re.match(POSIXPATH_RE(), S)


def WINPATH_RE():
    return re.compile('^[\w_\-]+\.so\.[0-9]+\.*.[0-9]*$', re.IGNORECASE)

def is_win_path(S):
    """
    Return True is S looks like a win path.
    Example: c:\usr\lib\librt.so.1.
    """
    return re.match(WINPATH_RE(), S)


def is_c_source(S):
    """
    Return True is S looks like a C source path.
    Example: this.c 
    FIXME: should get actual algo from contenttype.
    """
    return S.endswith(('.c', '.cpp', '.hpp', '.h',))


def is_java_source(S):
    """
    Return True is S looks like a Java source path.
    Example: this.java
    FIXME: should get actual algo from contenttype.
    """
    return S.endswith(('.java', '.jsp', '.aj',))


def is_GLIBC_ref(S):
    """
    Return True is S looks like a reference to GLIBC as typically found in
    Elfs.
    """
    return '@@GLIBC' in S


def JAVAREF_RE():
    return re.compile('^.*$', re.IGNORECASE)


def is_java_ref(S):  # @UnusedVariable
    """
    Return True is S looks like a reference to a java class or package in a
    class file.
    """
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

