#
# Copyright (c) 2016 nexB Inc. and others. All rights reserved.
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

import contextlib
import os
import fnmatch
import mimetypes as mimetype_python
import logging

import pygments.lexers
import pygments.util

import binaryornot.check

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFSyntaxError
from pdfminer.pdfdocument import PDFEncryptionError
from pdfminer.pdftypes import PDFException

from commoncode import fileutils
from commoncode import filetype

from typecode import magic2

"""
Utilities to detect and report the type of a file or path based on its name,
extension and mostly its content.
"""


LOG = logging.getLogger(__name__)

data_dir = os.path.join(os.path.dirname(__file__), 'data')
bin_dir = os.path.join(os.path.dirname(__file__), 'bin')


# Python mimetypes path setup using Apache mimetypes DB
os.environ['XDG_DATA_DIRS'] = os.path.join(data_dir, 'apache')
os.environ['XDG_DATA_HOME'] = os.environ['XDG_DATA_DIRS']
APACHE_MIME_TYPES = os.path.join(data_dir, 'apache', 'mime.types')

# Ensure that all dates are UTC, especially for fine free file.
os.environ['TZ'] = 'UTC'


PLAIN_TEXT_EXTENSIONS = ('.rst', '.rest', '.txt', '.md',
                        # This one is actually not handled by Pygments. There
                        # are probably more.
                         '.log')


C_EXTENSIONS = set(['.c', '.cc', '.cp', '.cpp', '.cxx', '.c++', '.h', '.hh',
                    '.s', '.asm', '.hpp', '.hxx', '.h++', '.i', '.ii', '.m'])


ELF_EXE = 'executable'
ELF_SHARED = 'shared object'
ELF_RELOC = 'relocatable'
ELF_UNKNOWN = 'unknown'
elf_types = (ELF_EXE, ELF_SHARED, ELF_RELOC,)


# TODO:
# http://svn.zope.org/z3c.mimetype/trunk/?pathrev=103648
# http://svn.zope.org/z3c.sharedmimeinfo/trunk/TODO.txt?revision=103668&view=markup
# https://pypi.python.org/pypi/z3c.sharedmimeinfo/0.1.0
# https://github.com/plone/Products.MimetypesRegistry/


# Global registry of Type objects, keyed by location
# TODO: can this be a memroy hog for very large scans?
_registry = {}


def get_type(location):
    """
    Return a Type object for location.
    """
    abs_loc = os.path.abspath(location)
    try:
        return _registry[abs_loc]
    except KeyError:
        t = Type(abs_loc)
        _registry[abs_loc] = t
        return t


# TODO: simplify code using a cached property decorator

class Type(object):
    """
    Content, media and mime type information about a file.
    All flags and values are tri-booleans. You can test a value state with
    `is`:

     - if the value is None, it has not been computed yet
     - if the value is False or has some true-ish value it has been computed

    Raise an IOError if the location does not exists.
    """
    __slots__ = (
        'location',
        'is_file',
        'is_dir',
        'is_regular',
        'is_special',
        'date',
        'is_link',
        'is_broken_link',
        '_size',
        '_link_target',
        '_mimetype_python',
        '_filetype_file',
        '_mimetype_file',
        '_filetype_pygments',
        '_is_pdf_with_text',
        '_is_text',
        '_is_binary',
        '_contains_text',
    )

    def __init__(self, location):
        if (not location
            or (not os.path.exists(location)
                and not filetype.is_broken_link(location))):
            raise IOError("[Errno 2] No such file or directory: "
                          "'%(location)r'" % locals())
        self.location = location
        # flags and values
        self.is_file = filetype.is_file(location)
        self.is_dir = filetype.is_dir(location)
        self.is_regular = filetype.is_regular(location)
        self.is_special = filetype.is_special(location)

        self.date = filetype.get_last_modified_date(location)

        self.is_link = filetype.is_link(location)
        self.is_broken_link = filetype.is_broken_link(location)

        # FIXME: the way the True and False values are checked in properties is verbose and contrived at best
        # and is due to use None/True/False as different values
        # computed on demand
        self._size = None
        self._link_target = None

        self._mimetype_python = None
        self._filetype_file = None
        self._mimetype_file = None
        self._filetype_pygments = None
        self._is_pdf_with_text = None
        self._is_text = None
        self._is_binary = None
        self._contains_text = None

    def __repr__(self):
        return ('Type(ftf=%r, mtf=%r, ftpyg=%r, mtpy=%r)'
                % (self.filetype_file, self.mimetype_file,
                   self.filetype_pygment, self.mimetype_python))

    @property
    def size(self):
        """
        Return the size of a file or directory
        """
        if self._size is None:
            self._size = 0
            if self.is_file or self.is_dir:
                self._size = filetype.get_size(self.location)
        return self._size

    @property
    def link_target(self):
        """
        Return a link target for symlinks or an empty string otherwise.
        """
        if self._link_target is None:
            self._link_target = ''
            if self.is_link or self.is_broken_link:
                self._link_target = filetype.get_link_target(self.location)
        return self._link_target

    @property
    def mimetype_python(self):
        """
        Return the mimetype using the Python stdlib and the Apache HTTPD
        mimetype definitions.
        """
        if self._mimetype_python is None:
            self._mimetype_python = ''
            if self.is_file is True:
                if not mimetype_python.inited:
                    mimetype_python.init([APACHE_MIME_TYPES])
                    val = mimetype_python.guess_type(self.location)[0]
                    self._mimetype_python = val
        return self._mimetype_python

    @property
    def filetype_file(self):
        """
        Return the filetype using the fine free file library.
        """
        if self._filetype_file is None:
            self._filetype_file = ''
            if self.is_file is True:
                self._filetype_file = magic2.file_type(self.location)
        return self._filetype_file

    @property
    def mimetype_file(self):
        """
        Return the mimetype using the fine free file library.
        """
        if self._mimetype_file is None:
            self._mimetype_file = ''
            if self.is_file is True:
                self._mimetype_file = magic2.mime_type(self.location)
        return self._mimetype_file

    @property
    def filetype_pygment(self):
        """
        Return the filetype guessed using Pygments lexer, mostly for source code.
        """
        if self._filetype_pygments is None:
            self._filetype_pygments = ''
            if self.is_file:
                lexer = get_pygments_lexer(self.location)
                if lexer:
                    self._filetype_pygments = lexer.name or ''
                else:
                    self._filetype_pygments = ''
        return self._filetype_pygments

    # FIXME: we way we use tri boolean is a tad ugly

    @property
    def is_binary(self):
        """
        Return True is the file at location is likely to be a binary file.
        """
        if self._is_binary is None:
            self._is_binary = False
            if self.is_file is True:
                self._is_binary = binaryornot.check.is_binary(self.location)
        return self._is_binary

    @property
    def is_text(self):
        """
        Return True is the file at location is likely to be a text file.
        """
        if self._is_text is None:
            self._is_text = self.is_file is True and self.is_binary is False
        return self._is_text

    @property
    def is_archive(self):
        """
        Return True if the file is some kind of archive or compressed file.
        """
        # FIXME: we should use extracode archive detection
        # TODO: also treat file systems as archives
        ft = self.filetype_file.lower()
        if (not self.is_text
        and (self.is_compressed
          or 'archive' in ft
          or self.is_package
          or self.is_filesystem
          or (self.is_office_doc and self.location.endswith('x'))
          # FIXME: is this really correct???
          or '(zip)' in ft
          )
        ):
            return True
        else:
            return False

    @property
    def is_office_doc(self):
        loc = self.location.lower()
        if loc.endswith(('.doc', '.docx', '.xlsx', '.xlsx', '.ppt', '.pptx',)):
            return True
        else:
            return False

    @property
    def is_package(self):
        """
        Return True if the file is some kind of packaged archive.
        """
        ft = self.filetype_file.lower()
        loc = self.location.lower()
        if ('debian binary package' in ft
         or ft.startswith('rpm ')
         or (ft == 'posix tar archive' and loc.endswith('.gem'))
         or (ft.startswith(('zip archive',)) and loc.endswith(('.jar', '.war', '.ear', '.egg', '.whl',)))
         or (ft.startswith(('java archive',)) and loc.endswith(('.jar', '.war', '.ear', '.zip',)))
         ):
            return True
        else:
            return False

    @property
    def is_compressed(self):
        """
        Return True if the file is some kind of compressed file.
        """
        ft = self.filetype_file.lower()
        if (not self.is_text
        and ('compressed' in ft
          or self.is_package
          or (self.is_office_doc and self.location.endswith('x'))
        )):
            return True
        else:
            return False

    @property
    def is_filesystem(self):
        """
        Return True if the file is some kind of file system or disk image.
        """
        ft = self.filetype_file.lower()
        if ('squashfs filesystem' in ft):
            return True
        else:
            return False

    @property
    def is_media(self):
        """
        Return True if the file is likely to be a media file.
        """
        # TODO: fonts?
        mt = self.mimetype_file
        mimes = ('image', 'picture', 'audio', 'video', 'graphic', 'sound',)

        ft = self.filetype_file.lower()
        types = (
            'image data', 'graphics image', 'ms-windows metafont .wmf',
            'windows enhanced metafile',
            'png image', 'interleaved image', 'microsoft asf', 'image text',
            'photoshop image', 'shop pro image', 'ogg data', 'vorbis', 'mpeg',
            'theora', 'bitmap', 'audio', 'video', 'sound', 'riff', 'icon',
            'pc bitmap', 'image data',
        )

        if any(m in mt for m in mimes) or any(t in ft for t in types):
            return True
        else:
            return False

    @property
    def is_media_with_meta(self):
        """
        Return True if the file is a media file that may contain text metadata.
        """
        # For now we only exclude PNGs, though there are likely several other
        # mp(1,2,3,4), jpeg, gif all have support for metadata
        if self.is_media and 'png image' in self.filetype_file.lower():
            return False
        else:
            return True

    @property
    def is_pdf(self):
        """
        Return True if the file is highly likely to be a pdf file.
        """
        ft = self.mimetype_file
        if 'pdf' in ft:
            return True
        else:
            return False

    @property
    def is_pdf_with_text(self):
        """
        Return True if the file is a pdf file from which we can extract text.
        """
        if self._is_pdf_with_text is None:
            self._is_pdf_with_text = False
            if not self.is_file is True and not self.is_pdf is True:
                self._is_pdf_with_text = False
            else:
                with open(self.location, 'rb') as pf:
                    try:
                        with contextlib.closing(PDFParser(pf)) as parser:
                            doc = PDFDocument(parser)
                            self._is_pdf_with_text = doc.is_extractable
                    except (PDFSyntaxError, PDFException, PDFEncryptionError):
                        self._is_pdf_with_text = False
        return self._is_pdf_with_text

    @property
    def contains_text(self):
        """
        Return True if a file possibly contains some text.
        """
        if self._contains_text is None:
            if not self.is_file:
                self._contains_text = False
            elif self.is_text:
                self._contains_text = True
            elif self.is_pdf and not self.is_pdf_with_text:
                self._contains_text = False
            elif self.is_compressed or self.is_archive:
                self._contains_text = False
            elif self.is_media and not self.is_media_with_meta:
                self._contains_text = False
            else:
                self._contains_text = True
        return self._contains_text

    @property
    def is_script(self):
        """
        Return True if the file is script-like.
        """
        ft = self.filetype_file.lower()
        if self.is_text is True and ('text' in ft and 'script' in ft):
            return True
        else:
            return False

    @property
    def is_source(self):
        """
        Return True if the file is source code.
        """
        if self.is_text is False:
            return False

        if self.location.endswith(PLAIN_TEXT_EXTENSIONS):
            return False

        ft = self.filetype_file.lower()
        pt = self.filetype_pygment

        if not 'xml' in ft and (pt or self.is_script is True):
            return True
        else:
            return False

    @property
    def programming_language(self):
        """
        Return the programming language if the file is source code or an empty
        string.
        """
        return self.is_source and self.filetype_pygment or ''

    @property
    def is_c_source(self):
        ext = fileutils.file_extension(self.location)
        if self.is_text is True and ext.lower() in C_EXTENSIONS:
            return True
        else:
            return False

    @property
    def is_winexe(self):
        """
        Return True if a the file is a windows executable.
        """
        ft = self.filetype_file.lower()
        if 'executable for ms windows' in ft or ft.startswith('pe32'):
            return True
        else:
            return False

    @property
    def is_elf(self):
        ft = self.filetype_file.lower()
        if (ft.startswith('elf')
            and (ELF_EXE in ft
            or ELF_SHARED in ft
            or ELF_RELOC in ft)):
            return True
        else:
            return False

    @property
    def elf_type(self):
        if self.is_elf is True:
            ft = self.filetype_file.lower()
            for t in elf_types:
                if t in ft:
                    return t
            return ELF_UNKNOWN
        else:
            return ''

    @property
    def is_stripped_elf(self):
        if self.is_elf is True:
            if 'not stripped' not in self.filetype_file.lower():
                return True
            else:
                return False
        else:
            return False

    @property
    def is_java_source(self):
        """
        FIXME: Check the filetype.
        """
        if self.is_file is True:
            name = fileutils.file_name(self.location)
            if (fnmatch.fnmatch(name, '*.java')
                or fnmatch.fnmatch(name, '*.aj')
                or fnmatch.fnmatch(name, '*.ajt')
                ):
                return True
            else:
                return False
        else:
            return False

    @property
    def is_java_class(self):
        """
        FIXME: Check the filetype.
        """
        if self.is_file is True:
            name = fileutils.file_name(self.location)
            if fnmatch.fnmatch(name, '*?.class'):
                return True
            else:
                return False
        else:
            return False


def get_pygments_lexer(location):
    """
    Given an input file location, return a Pygments lexer appropriate for
    lexing this file content.
    """
    try:
        T = _registry[location]
        if T.is_binary:
            return
    except KeyError:
        if binaryornot.check.is_binary(location):
            return
    try:
        # FIXME: Latest Pygments versions should work fine
        # win32_bug_on_s_files = dejacode.on_windows and location.endswith('.s')

        # NOTE: we use only the location for its file name here, we could use
        # lowercase location may be
        lexer = pygments.lexers.get_lexer_for_filename(location,
                                                       stripnl=False,
                                                       stripall=False)
        return lexer

    except pygments.util.ClassNotFound:
        try:
            # if Pygments does not guess we should not carry forward
            # read the first 4K of the file
            with open(location, 'rb') as f:
                content = f.read(4096)
            guessed = pygments.lexers.guess_lexer(content)
            return guessed
        except pygments.util.ClassNotFound:
            return


def get_filetype(location):
    """
    LEGACY: Return the best filetype for location using multiple tools.
    """
    T = get_type(location)
    filetype = T.filetype_file.lower()
    filetype_pygment = T.filetype_pygment
    # 'file' is not good at detecting language, if pygment even can't
    # detect it, we can ignore it
    if T.is_text and T.filetype_pygment:
        # Pygment tends to recognize many XML files are Genshi files
        # Genshi is rare and irrelevant, just declare as XML
        ftpl = filetype_pygment.lower()
        if 'genshi' in ftpl or 'xml+evoque' in ftpl:
            return 'xml language text'

        # pygment recognizes elfs as Groff files
        if not ('roff' in filetype_pygment and 'roff' not in filetype):
            if filetype_pygment.lower() != 'text only':
                # FIXME: this 'language text' is ugly
                return filetype_pygment.lower() + ' language text'
    return filetype


STD_INCLUDES = ('/usr/lib/gcc', '/usr/lib', '/usr/include',
                '<built-in>', '/tmp/glibc-',)


def is_standard_include(location):
    """
    Return True if a file path refers to something that looks like a
    standard include.
    """
    if (location.startswith(STD_INCLUDES) or location.endswith(STD_INCLUDES)):
        return True
    else:
        return False
