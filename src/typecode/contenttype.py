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

import contextlib
import io
import os
import fnmatch
import mimetypes as mimetype_python

import attr
from binaryornot.helpers import get_starting_chunk
from binaryornot.helpers import is_binary_string
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFSyntaxError
from pdfminer.psparser import PSSyntaxError
from pdfminer.pdfdocument import PDFEncryptionError
from pdfminer.pdftypes import PDFException
from six import string_types

from commoncode import filetype
from commoncode import fileutils
from commoncode.datautils import Boolean
from commoncode.datautils import List
from commoncode.datautils import String
from commoncode.system import on_linux
from commoncode.system import py2
from commoncode import text
from typecode import entropy
from typecode import extractible
from typecode import magic2
from typecode.pygments_lexers import ClassNotFound as LexerClassNotFound
from typecode.pygments_lexers import get_lexer_for_filename
from typecode.pygments_lexers import guess_lexer


"""
Utilities to detect and report the type of a file or path based on its name,
extension and mostly its content.
"""

# Tracing flag
TRACE = False


def logger_debug(*args):
    pass


if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, string_types) and a or repr(a) for a in args))


data_dir = os.path.join(os.path.dirname(__file__), 'data')

# Python mimetypes path setup using Apache mimetypes DB
os.environ['XDG_DATA_DIRS'] = os.path.join(data_dir, 'apache')
os.environ['XDG_DATA_HOME'] = os.environ['XDG_DATA_DIRS']
APACHE_MIME_TYPES = os.path.join(data_dir, 'apache', 'mime.types')


# Ensure that all dates are UTC, especially for fine free file.
os.environ['TZ'] = 'UTC'


def as_bytes(items):
    """
    Return a tuple of bytes items from a sequence of string items.
    """
    return tuple(e.encode('utf-8') for e in items)


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
# FIXME: can this be a memroy hog for very large scans?
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
        '_is_text_with_long_lines',
        '_is_compact_js',
        '_is_js_map',
        '_is_binary',
        '_is_data',
        '_is_archive',
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
        self._is_text_with_long_lines = None
        self._is_compact_js = None
        self._is_js_map = None
        self._is_binary = None
        self._is_data = None
        self._is_archive = None
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
            if self.is_text and not self.is_media:
                lexer = get_pygments_lexer(self.location)
                if lexer and not lexer.name.startswith('JSON'):
                    self._filetype_pygments = lexer.name or ''
                else:
                    self._filetype_pygments = ''
        return self._filetype_pygments

    # FIXME: we way we use tri booleans is a tad ugly

    @property
    def is_binary(self):
        """
        Return True is the file at location is likely to be a binary file.
        """
        if self._is_binary is None:
            self._is_binary = False
            if self.is_file is True:
                self._is_binary = is_binary(self.location)
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
    def is_text_with_long_lines(self):
        """
        Return True is the file at location is likely to be a text file.
        """
        if self._is_text_with_long_lines is None:
            self._is_text_with_long_lines = (
                self.is_text is True
                and 'long lines' in self.filetype_file.lower()
            )
        return self._is_text_with_long_lines

    @property
    def is_compact_js(self):
        """
        Return True is the file at location is likely to be a compact JavaScript
        (e.g. map or minified) or JSON file.
        """
        if self._is_compact_js is None:
            # FIXME: when moving to Python 3
            if on_linux and py2:
                extensions = (b'.min.js', b'.typeface.json',)
                json_ext = b'.json'
            else:
                extensions = (u'.min.js', u'.typeface.json',)
                json_ext = u'.json'

            self._is_compact_js = (
                self.is_js_map
                or (self.is_text is True and self.location.endswith(extensions))
                or (self.filetype_file.lower() == 'data'
                    and (self.programming_language == 'JavaScript'
                         or self.location.endswith(json_ext)
                         )
                    )
            )
        return self._is_compact_js

    @property
    def is_js_map(self):
        """
        Return True is the file at location is likely to be a CSS or JavaScript
        map file.
        """
        if self._is_js_map is None:
            # FIXME: when moving to Python 3
            extensions = '.js.map', '.css.map',
            if on_linux and py2:
                extensions = as_bytes(extensions)

            self._is_js_map = (
                self.is_text is True
                and self.location.endswith(extensions)
            )
        return self._is_js_map

    @property
    def is_archive(self):
        """
        Return True if the file is some kind of archive or compressed file.
        """
        if self._is_archive is not None:
            return self._is_archive
        self._is_archive = False


        ft = self.filetype_file.lower()
        if on_linux and py2:
            docx_ext = b'x'
        else:
            docx_ext = u'x'

        if self.is_text:
            self._is_archive = False

        elif self.filetype_file.lower().startswith('gem image data'):
            self._is_archive = False

        elif (self.is_compressed
            or 'archive' in ft
            or self.is_package
            or self.is_filesystem
            or (self.is_office_doc and self.location.endswith(docx_ext))
            or extractible.can_extract(self.location)
            # FIXME: is this really correct???
            or '(zip)' in ft):
                self._is_archive = True

        return self._is_archive

    @property
    def is_office_doc(self):
        loc = self.location.lower()
        # FIXME: add open office extensions

        msoffice_exts = u'.doc', u'.docx', u'.xlsx', u'.xlsx', u'.ppt', u'.pptx'
        if on_linux and py2:
            msoffice_exts = as_bytes(msoffice_exts)
        if loc.endswith(msoffice_exts):
            return True
        else:
            return False

    @property
    def is_package(self):
        """
        Return True if the file is some kind of packaged archive.
        """
        # FIXME: this should beased on proper package recognition, not this simplistic check
        ft = self.filetype_file.lower()
        loc = self.location.lower()
        package_archive_extensions = u'.jar', u'.war', u'.ear', u'.zip', '.whl', '.egg'
        if on_linux and py2:
            package_archive_extensions = as_bytes(package_archive_extensions)
        if on_linux and py2:
            gem_extension = b'.gem'
        else:
            gem_extension = u'.gem'

        # FIXME: this is grossly under specified and is missing many packages
        if ('debian binary package' in ft
        or ft.startswith('rpm ')
        or (ft == 'posix tar archive' and loc.endswith(gem_extension))
        or (ft.startswith(('zip archive', 'java archive'))
            and loc.endswith(package_archive_extensions))):
            return True
        else:
            return False

    @property
    def is_compressed(self):
        """
        Return True if the file is some kind of compressed file.
        """
        ft = self.filetype_file.lower()

        if on_linux and py2:
            docx_ext = b'x'
        else:
            docx_ext = u'x'

        if (not self.is_text
        and (
            '(zip)' in ft
            or ft.startswith(('zip archive', 'java archive'))
            or self.is_package
            or any(x in ft for x in ('squashfs filesystem', 'compressed'))
            or (self.is_office_doc and self.location.endswith(docx_ext))
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
            'pc bitmap', 'image data', 'netpbm'
        )

        if any(m in mt for m in mimes) or any(t in ft for t in types):
            return True

        if on_linux and py2:
            tga_ext = b'.tga'
        else:
            tga_ext = u'.tga'

        if ft == 'data' and mt=='application/octet-stream' and self.location.lower().endswith(tga_ext):
            # there is a regression in libmagic 5.38 https://bugs.astron.com/view.php?id=161
            # this is a targe image
            return True

        return False

    @property
    def is_media_with_meta(self):
        """
        Return True if the file is a media file that may contain text metadata.
        """
        # For now we only exclude PNGs, JEPG and Gifs, though there are likely
        # several other. mp(1,2,3,4), jpeg, gif all have support for metadata
        # but we exclude some.

        # FIXME: only include types that are known to have metadata
        if (self.is_media and self.filetype_file.lower().startswith(
                ('gif image', 'png image', 'jpeg image', 'netpbm', 'mpeg'))):
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
                    except (PDFSyntaxError, PSSyntaxError, PDFException, PDFEncryptionError):
                        self._is_pdf_with_text = False
        return self._is_pdf_with_text

    @property
    def contains_text(self):
        """
        Return True if a file possibly contains some text.
        """
        if self._contains_text is None:
            if on_linux and py2:
                svg_ext = b'.svg'
            else:
                svg_ext = u'.svg'

            if not self.is_file:
                self._contains_text = False

            elif self.is_media and not self.location.lower().endswith(svg_ext):
                # and not self.is_media_with_meta:
                self._contains_text = False

            elif self.is_text:
                self._contains_text = True

            elif self.is_pdf and not self.is_pdf_with_text:
                self._contains_text = False

            elif self.is_compressed:
                self._contains_text = False

            elif self.is_archive and not self.is_compressed:
                self._contains_text = True

            # TODO: exclude all binaries??
            # elif self.is_binary:
            #     self._contains_text = False

            else:
                self._contains_text = True
        return self._contains_text

    @property
    def is_data(self):
        """
        Return True if the file is some kind of data file.
        """
        if self._is_data is None:
            if not self.is_file:
                self._is_data = False

            large_file = 5 * 1000 * 1000
            large_text_file = 2 * 1000 * 1000

            ft = self.filetype_file.lower()

            size = self.size
            max_entropy = 1.3

            if (ft == 'data'
            or is_data(self.location)
            or ('data' in ft and size > large_file)
            or (self.is_text and size > large_text_file)
            or (self.is_text and size > large_text_file)
            or (entropy.entropy(self.location, length=5000) < max_entropy)):

                self._is_data = True
            else:
                self._is_data = False
        return self._is_data

    @property
    def is_script(self):
        """
        Return True if the file is script-like.
        """
        ft = self.filetype_file.lower()
        if self.is_text is True and 'script' in ft and not 'makefile' in ft:
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
        PLAIN_TEXT_EXTENSIONS = (
            '.rst', '.rest', '.txt', '.md',
            # This one is actually not handled by Pygments. There are probably more.
            '.log')
        if on_linux and py2:
            PLAIN_TEXT_EXTENSIONS = as_bytes(PLAIN_TEXT_EXTENSIONS)

        if self.location.endswith(PLAIN_TEXT_EXTENSIONS):
            return False

        if self.filetype_pygment or self.is_script is True:
            return True
        else:
            return False

    @property
    def programming_language(self):
        """
        Return the programming language if the file is source code or an empty
        string.
        """
        return self.filetype_pygment or ''

    @property
    def is_c_source(self):
        C_EXTENSIONS = set(
            ['.c', '.cc', '.cp', '.cpp', '.cxx', '.c++', '.h', '.hh',
            '.s', '.asm', '.hpp', '.hxx', '.h++', '.i', '.ii', '.m'])
        if on_linux and py2:
            C_EXTENSIONS = set(as_bytes(C_EXTENSIONS))

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
          or ELF_RELOC in ft)
        ):
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

            if (fnmatch.fnmatch(name, b'*.java' if on_linux and py2 else u'*.java')
             or fnmatch.fnmatch(name, b'*.aj' if on_linux and py2 else u'*.aj')
             or fnmatch.fnmatch(name, b'*.ajt' if on_linux and py2 else u'*.ajt')):
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
            if fnmatch.fnmatch(name, b'*?.class' if on_linux and py2 else u'*?.class'):
                return True
            else:
                return False
        else:
            return False


@attr.attributes
class TypeDefinition(object):
    name = String(repr=True)
    filetypes = List(repr=True)
    mimetypes = List(repr=True)
    extensions = List(repr=True)
    strict = Boolean(repr=True,
        help=' if True, all criteria must be matched to select this detector.')


DATA_TYPE_DEFINITIONS = tuple([
    TypeDefinition(
        name='MySQL ARCHIVE Storage Engine data files',
        filetypes=('mysql table definition file',),
        extensions=
            (b'.arm', b'.arz', b'.arn',) if on_linux and py2
            else (u'.arm', u'.arz', u'.arn',),
    ),
])


def is_data(location, definitions=DATA_TYPE_DEFINITIONS):
    """
    Return True isthe file at `location` is a data file.
    """
    if on_linux and py2:
        location = fileutils.fsencode(location)

    if not filetype.is_file(location):
        return False

    T = get_type(location)
    ftype = T.filetype_file.lower()
    mtype = T.mimetype_file.lower()

    for ddef in definitions:
        type_matched = ddef.filetypes and any(t in ftype for t in ddef.filetypes)
        mime_matched = ddef.mimetypes and any(m in mtype for m in ddef.mimetypes)

        exts = ddef.extensions
        if exts:
            extension_matched = exts and location.lower().endswith(exts)

        if TRACE:
            logger_debug('is_data: considering def: %(ddef)r for %(location)s' % locals())
            logger_debug('matched type: %(type_matched)s, mime: %(mime_matched)s, ext: %(extension_matched)s' % locals())

        if ddef.strict and not all([type_matched, mime_matched, extension_matched]):
            continue

        if type_matched or mime_matched or extension_matched:
            if TRACE:
                logger_debug('is_data: True: %(location)s: ' % locals())
            return True

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
        if is_binary(location):
            return
    try:
        # FIXME: Latest Pygments versions should work fine
        # win32_bug_on_s_files = dejacode.on_windows and location.endswith('.s')

        # NOTE: we use only the location for its file name here, we could use
        # lowercase location may be
        lexer = get_lexer_for_filename(location, stripnl=False, stripall=False)
        return lexer

    except LexerClassNotFound:
        try:
            # if Pygments does not guess we should not carry forward
            # read the first 4K of the file
            try:
                with io.open(location, 'r') as f:
                    content = f.read(4096)
            except:
                # try again as bytes and force unicode
                with open(location, 'rb') as f:
                    content = text.as_unicode(f.read(4096))

            guessed = guess_lexer(content)
            return guessed
        except LexerClassNotFound:
            return


def get_filetype(location):
    """
    LEGACY: Return the best filetype for location using multiple tools.
    """
    T = get_type(location)
    return T.filetype_file.lower()


def is_standard_include(location):
    """
    Return True if the `location` file path refers to something that looks like
    a standard C/C++ include.
    """
    STD_INCLUDES = (
        '/usr/lib/gcc', '/usr/lib', '/usr/include',
        '<built-in>', '/tmp/glibc-',
    )

    if (location.startswith(STD_INCLUDES) or location.endswith(STD_INCLUDES)):
        return True
    else:
        return False


def is_binary(location):
    """
    Retrun True if the file at `location` is a binary file.
    """
    known_extensions = (
        '.pyc', '.pgm', '.mp3', '.mp4', '.mpeg', '.mpg', '.emf',
        '.pgm', '.pbm', '.ppm')
    if on_linux and py2:
        known_extensions = as_bytes(known_extensions)

    if location.endswith(known_extensions):
        return True
    return is_binary_string(get_starting_chunk(location))
