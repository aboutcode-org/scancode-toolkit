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
#
# This code was in part derived from the python-magic library:
# The MIT License (MIT)
#
# Copyright (c) 2001-2014 Adam Hupp
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import os.path
import ctypes
import sys

from commoncode import system
from commoncode import command

"""
magic2 is minimal and specialized wrapper around a vendored libmagic file
identification library. This is NOT thread-safe. It is based on python-magic
by Adam Hup and adapted to the specific needs of ScanCode.
"""


data_dir = os.path.join(os.path.dirname(__file__), 'data')
bin_dir = os.path.join(os.path.dirname(__file__), 'bin')


# path to vendored magic DB, possibly OS-specific
basemag = os.path.join(data_dir, 'magic')
# keep the first which is the most specific directory
magdir = command.get_base_dirs(basemag)[0]
magic_db = os.path.join(magdir, 'magic.mgc')

#
# Cached detectors
#
detectors = {}


# libmagic flags
MAGIC_NONE = 0
MAGIC_MIME = 16
MAGIC_MIME_ENCODING = 1024
MAGIC_NO_CHECK_ELF = 65536
MAGIC_NO_CHECK_TEXT = 131072
MAGIC_NO_CHECK_CDF = 262144


DETECT_TYPE = MAGIC_NONE
DETECT_MIME = MAGIC_NONE | MAGIC_MIME
DETECT_ENC = MAGIC_NONE | MAGIC_MIME | MAGIC_MIME_ENCODING


def file_type(location):
    """"
    Return the detected filetype for file at `location` or an empty string if
    nothing found or an error occurred.
    """
    try:
        return _detect(location, DETECT_TYPE)
    except:
        # TODO: log errors
        return ''


def mime_type(location):
    """"
    Return the detected mimetype for file at `location` or an empty string if
    nothing found or an error occurred.
    """
    try:
        return _detect(location, DETECT_MIME)
    except:
        # TODO: log errors
        return ''


def encoding(location):
    """"
    Return the detected encoding for file at `location` or an empty string.
    Raise an exception on errors.
    """
    return _detect(location, DETECT_ENC)


def _detect(location, flags):
    """"
    Return the detected type using `flags` of file at `location` or an empty
    string. Raise an exception on errors.
    """
    try:
        detector = detectors[flags]
    except KeyError:
        detector = Detector(flags=flags)
        detectors[flags] = detector
    val = detector.get(location)
    val = val or ''
    val = val.decode('ascii', 'ignore').strip()
    return ' '.join(val.split())


class MagicException(Exception):
    pass


class Detector(object):
    def __init__(self, flags, magic_file=magic_db):
        """
        Create a new libmagic detector.
        flags - the libmagic flags
        magic_file - use a mime database other than the vendored default
        """
        self.flags = flags
        self.cookie = _magic_open(self.flags)
        _magic_load(self.cookie, magic_file)

    def get(self, location):
        """
        Return the magic type info from a file at `location`. The value
        returned depends on the flags passed to the object. If this fails
        attempt to get it using a UTF-encoded location or from loading the
        first 16K of the file. Raise a MagicException on error.
        """
        assert location
        try:
            # first use the path as is
            return  _magic_file(self.cookie, location)
        except:
            # then try to get a utf-8 encoded path: Rationale:
            # https://docs.python.org/2/library/ctypes.html#ctypes.set_conversion_mode ctypes
            # encode strings to byte as ASCII or MBCS depending on the OS The
            # location string may therefore be mangled and the file not accessible
            # anymore by libmagic in some cases.
            try:
                # FIXME: use filesystem encoding instead
                uloc = location.encode('utf-8')
                return  _magic_file(self.cookie, uloc)
            except:
                # if all fails, read the start of the file instead
                with open(location) as fd:
                    buf = fd.read(16384)
                return _magic_buffer(self.cookie, buf, len(buf))

    def __del__(self):
        """
        During shutdown magic_close may have been cleared already so make sure
        it exists before using it.
        """
        if self.cookie and _magic_close:
            _magic_close(self.cookie)


def load_lib():
    """
    Return the loaded libmagic shared library object from vendored paths.
    """
    root_dir = command.get_base_dirs(bin_dir)[0]
    _bin_dir, lib_dir = command.get_bin_lib_dirs(root_dir)
    magic_so = os.path.join(lib_dir, 'libmagic' + system.lib_ext)

    # add lib path to the front of the PATH env var
    new_path = os.pathsep.join([lib_dir, os.environ['PATH']])
    os.environ['PATH'] = new_path

    if os.path.exists(magic_so):
        if not isinstance(magic_so, bytes):
            # ensure that the path is not Unicode...
            magic_so = magic_so.encode(sys.getfilesystemencoding() or sys.getdefaultencoding())
        lib = ctypes.CDLL(magic_so)
        if lib and lib._name:
            return lib
    raise ImportError('Failed to load libmagic from %(magic_so)r' % locals())


# Main ctypes proxy
libmagic = load_lib()


def check_error(result, func, args):  # @UnusedVariable
    """
    ctypes error handler/checker:  Check for errors and raise an exception or
    return the result otherwise.
    """
    if result is None or result < 0 or str(result).startswith('cannot open'):
        err = _magic_error(args[0])
        raise MagicException(err)
    else:
        return result


# ctypes functions aliases.
_magic_open = libmagic.magic_open
_magic_open.restype = ctypes.c_void_p
_magic_open.argtypes = [ctypes.c_int]

_magic_close = libmagic.magic_close
_magic_close.restype = None
_magic_close.argtypes = [ctypes.c_void_p]

_magic_error = libmagic.magic_error
_magic_error.restype = ctypes.c_char_p
_magic_error.argtypes = [ctypes.c_void_p]

_magic_file = libmagic.magic_file
_magic_file.restype = ctypes.c_char_p
_magic_file.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
_magic_file.errcheck = check_error

_magic_buffer = libmagic.magic_buffer
_magic_buffer.restype = ctypes.c_char_p
_magic_buffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
_magic_buffer.errcheck = check_error

_magic_load = libmagic.magic_load
_magic_load.restype = ctypes.c_int
_magic_load.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
_magic_load.errcheck = check_error
