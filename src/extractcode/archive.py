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

from __future__ import print_function, absolute_import

from collections import namedtuple
import functools
import logging
import os

from commoncode import fileutils
from commoncode import filetype
import typecode

from extractcode import all_kinds
from extractcode import regular
from extractcode import package
from extractcode import docs
from extractcode import regular_nested
from extractcode import file_system
from extractcode import patches
from extractcode import special_package

from extractcode import patch
from extractcode import sevenzip
from extractcode import libarchive2
from extractcode import extracted_files
from extractcode.uncompress import uncompress_gzip
from extractcode.uncompress import uncompress_bzip2


logger = logging.getLogger(__name__)
DEBUG = True
DEBUG_DEEP = False
# import sys
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# logger.setLevel(logging.DEBUG)



"""
Archive formats handling. The purpose of this module is to select an extractor
suitable for the accurate extraction of a given kind of archive. An extractor is
a function that can read an archive and extract it to a directory. Multiple
extractors functions can be called in sequence to handle nested archives such
as tar.gz.

A handler contains selection criteria and a list of extractors.
We select an extraction handler based on these croiteria:
 - file type,
 - mime type,
 - file extension,
 - kind of archive.

Several handlers may be suitable candidates for extraction of a given archive.
Candidates are scored and the best one picked which is typically the most
specific and the one capable of doing the deepest extraction of a given archive.

At the lowest level, archives are processed by standard library code (sometimes
patched) or native code (libarchive, 7zip).

For background on archive and compressed file formats see:
 - http://en.wikipedia.org/wiki/List_of_archive_formats
 - http://en.wikipedia.org/wiki/List_of_file_formats#Archive_and_compressed
"""

# high level aliases to lower level extraction functions
extract_tar = libarchive2.extract
extract_patch = patch.extract

extract_deb = libarchive2.extract
extract_ar = libarchive2.extract
extract_msi = sevenzip.extract
extract_cpio = libarchive2.extract
extract_7z = libarchive2.extract
extract_zip = libarchive2.extract

extract_iso = sevenzip.extract
extract_rar = sevenzip.extract
extract_rpm = sevenzip.extract
extract_xz = sevenzip.extract
extract_lzma = sevenzip.extract
extract_squashfs = sevenzip.extract
extract_cab = sevenzip.extract
extract_nsis = sevenzip.extract
extract_ishield = sevenzip.extract
extract_Z = sevenzip.extract


Handler = namedtuple('Handler', ['name', 'types', 'mimes', 'exts', 'kind', 'extractors'])


def can_extract(location):
    """
    Return True if this location can be extracted by some handler.
    """
    handlers = list(get_handlers(location))
    if handlers:
        return True


def should_extract(location, kinds):
    """
    Return True if this location should be extracted based on the provided
    kinds
    """
    location = os.path.abspath(os.path.expanduser(location))
    if get_extractor(location, kinds):
        return True


def get_extractor(location, kinds=all_kinds):
    """
    Return an extraction callable that can extract the file at location or
    an None if no extract function is found.
    """
    assert location
    location = os.path.abspath(os.path.expanduser(location))
    extractors = get_extractors(location, kinds)
    if not extractors:
        return None

    if len(extractors) == 2:
        extractor1, extractor2 = extractors
        nested_extractor = functools.partial(extract_twice,
                                             extractor1=extractor1,
                                             extractor2=extractor2)
        return nested_extractor
    elif len(extractors) == 1:
        return extractors[0]
    else:
        return None


def get_extractors(location, kinds=all_kinds):
    """
    Return a list of extractors that can extract the file at
    location or an empty list.
    """
    location = os.path.abspath(os.path.expanduser(location))
    if filetype.is_file(location):
        handlers = list(get_handlers(location))
        if handlers:
            candidates = score_handlers(handlers)
            if candidates:
                best = pick_best_handler(candidates, kinds)
                if best:
                    return best.extractors
    return []


def get_handlers(location):
    """
    Return an iterable of (handler, type_matched, mime_matched,
    extension_matched,) for this `location`.
    """
    if filetype.is_file(location):
        T = typecode.contenttype.get_type(location)
        ftype = T.filetype_file.lower()
        mtype = T.mimetype_file

        for handler in archive_handlers:
            if not handler.extractors:
                continue

            extractor_count = len(handler.extractors)
            if extractor_count > 2:
                raise Exception('Maximum level of archive nesting is two.')

            type_matched = None
            if handler.types:
                type_matched = any(t in ftype for t in handler.types)

            mime_matched = None
            if handler.mimes:
                mime_matched = any(m in mtype for m in handler.mimes)

            extension_matched = None
            if handler.exts:
                extension_matched = location.lower().endswith(handler.exts)

            if DEBUG_DEEP:
                logger.debug('get_handlers: %(location)s: ftype: %(ftype)s, mtype: %(mtype)s ' % locals())
                logger.debug('get_handlers: %(location)s: matched type: %(type_matched)s, mime: %(mime_matched)s, ext: %(extension_matched)s' % locals())


            if type_matched or mime_matched or extension_matched:
                if DEBUG_DEEP:
                    logger.debug('get_handlers: %(location)s: matched type: %(type_matched)s, mime: %(mime_matched)s, ext: %(extension_matched)s' % locals())
                    logger.debug('get_handlers: %(location)s: handler: %(handler)r' % locals())
                yield handler, type_matched, mime_matched, extension_matched


def score_handlers(handlers):
    """
    Score candidate handlers. Higher score is better.
    """
    for handler, type_matched, mime_matched, extension_matched in handlers:
        score = 0
        # increment kind value: higher kinds numerical values are more
        # specific by design
        score += handler.kind

        # increment score based on matched criteria
        if type_matched and mime_matched and extension_matched:
            # bump for matching all criteria
            score += 10

        if type_matched:
            # type is more specific than mime
            score += 8

        if mime_matched:
            score += 6

        if extension_matched:
            # extensions have little power
            score += 2

        if extension_matched and not (type_matched or mime_matched):
            # extension matched alone should not be extracted
            score -= 100

        # increment using the number of extractors: higher score means that we
        # have some kind of nested archive that we can extract in one
        # operation, therefore more this is a more specific extraction that we
        # should prefer. For instance we prefer uncompressing and extracting a
        # tgz at once, rather than uncompressing in a first operation then
        # later extracting the plain tar in a second operation
        score += len(handler.extractors)

        if score > 0:
            yield score, handler, extension_matched


def pick_best_handler(candidates, kinds):
    """
    Return the best handler with the highest score.
    In case of ties, look at the top two handlers and keep:
    - the handler with the most extractors (i.e. a handler that does deeper
      nested extractions),
    - OR the handler that has matched extensions,
    - OR finally the first handler in the list.
    """
    # sort by increasing scores
    scored = sorted(candidates, reverse=True)
    if not scored:
        return

    top_score, top, top_ext = scored[0]
    # logger.debug('pick_best_handler: top: %(top)r\n' % locals())
    # single candidate case
    if len(scored) == 1:
        return top if top.kind in kinds else None

    # else: here we have 2 or more candidates: look at the runner up.
    runner_up_score, runner_up, runner_up_ext = scored[1]
    # logger.debug('pick_best_handler: runner_up: %(runner_up)r\n' % locals())

    # return the top scoring if there is score ties.
    if top_score > runner_up_score:
        return top if top.kind in kinds else None

    # else: with sorting top_score == runner_up_score by construction here
    # break ties based on number of extractors
    if len(top.extractors) > len(runner_up.extractors):
        return top if top.kind in kinds else None

    elif len(top.extractors) < len(runner_up.extractors):
        return runner_up if runner_up.kind in kinds else None

    # else: here len(top.extractors) == len(runner_up.extractors)
    # now, break ties based on extensions being matched
    if top_ext and not runner_up_ext:
        return top if top.kind in kinds else None

    elif runner_up_ext and not top_ext:
        return runner_up if runner_up.kind in kinds else None

    # else: we could not break ties. finally return the top
    return top if top.kind in kinds else None


def extract_twice(location, target_dir, extractor1, extractor2):
    """
    Extract a nested compressed archive at `location` to `target_dir` using
    the `extractor1` function to a temporary directory then the `extractor2`
    function on the extracted payload of `extractor1`.

    Return a list of warning messages. Raise exceptions on errors.

    Typical nested archives include compressed tarballs and RPMs (containing a
    compressed cpio).

    Note: it would be easy to support deeper extractor chains, but this gets
    hard to trace and debug very quickly. A depth of two is simple and sane and
    covers most common cases.
    """
    abs_location = os.path.abspath(os.path.expanduser(location))
    abs_target_dir = os.path.abspath(os.path.expanduser(target_dir))
    # extract first the intermediate payload to a temp dir
    temp_target = fileutils.get_temp_dir('extract')
    warnings = extractor1(abs_location, temp_target)
    if DEBUG:
        logger.debug('extract_twice: temp_target: %(temp_target)r' % locals())

    # extract this intermediate payload to the final target_dir
    try:
        inner_archives = list(extracted_files(temp_target))
        if not inner_archives:
            warnings.append(location + ': No files found in archive.')
        else:
            for extracted1_loc in inner_archives:
                if DEBUG:
                    logger.debug('extract_twice: extractor2: %(extracted1_loc)r' % locals())
                warnings.extend(extractor2(extracted1_loc, target_dir))
    finally:
        # cleanup the temporary output from extractor1
        fileutils.delete(temp_target)
    return warnings


"""
List of archive handlers.
"""

archive_handlers = [
    Handler(name='Tar',
        types=('.tar', 'tar archive',),
        mimes=('application/x-tar',),
        exts=('.tar',),
        kind=regular,
        extractors=[extract_tar]
    ),

    Handler(name='Ruby Gem package',
        types=('.tar', 'tar archive',),
        mimes=('application/x-tar',),
        exts=('.gem',),
        kind=package,
        extractors=[extract_tar]
    ),

    Handler(name='Zip',
        types=('zip archive',),
        mimes=('application/zip',),
        exts=('.zip', '.zipx'),
        kind=regular,
        extractors=[extract_zip]
    ),

    Handler(name='Office doc',
        types=('zip archive',),
        mimes=('application/zip', 'application/vnd.openxmlformats',),
        # Extensions of office documents that are zip files too
        exts=(
            # ms doc
            '.docx', '.dotx', '.docm',
            # ms xls
            '.xlsx', '.xltx', '.xlsm', '.xltm',
            # ms ppt
            '.pptx', '.ppsx', '.potx', '.pptm', '.potm', '.ppsm',
            # oo write
            '.odt', '.odf', '.sxw', '.stw',
            # oo calc
            '.ods', '.ots', '.sxc', '.stc',
            # oo pres and draw
            '.odp', '.otp', '.odg', '.otg', '.sxi', '.sti', '.sxd',
            '.sxg', '.std',
            # star office
            '.sdc', '.sda', '.sdd', '.smf', '.sdw', '.sxm', '.stw',
            '.oxt', '.sldx',

            '.epub',
        ),
        kind=docs,
        extractors=[extract_zip]
    ),

    Handler(name='Android app',
        types=('zip archive',),
        mimes=('application/zip',),
        exts=('.apk',),
        kind=package,
        extractors=[extract_zip]
    ),

    # see http://tools.android.com/tech-docs/new-build-system/aar-formats
    Handler(name='Android library',
        types=('zip archive',),
        mimes=('application/zip',),
        # note: Apache Axis also uses AAR extensions for plain Jars
        exts=('.aar',),
        kind=package,
        extractors=[extract_zip]
    ),

    Handler(name='Mozilla extension',
        types=('zip archive',),
        mimes=('application/zip',),
        exts=('.xpi',),
        kind=package,
        extractors=[extract_zip]
    ),

# see https://developer.chrome.com/extensions/crx
#    Handler(name='Chrome extension',
#        types=('data',),
#        mimes=('application/octet-stream',),
#        exts=('.crx',),
#        kind=package,
#        extractors=[extract_7z]
#    ),

    Handler(name='iOS app',
        types=('zip archive',),
        mimes=('application/zip',),
        exts=('.ipa',),
        kind=package,
        extractors=[extract_zip]
    ),

    Handler(name='Java Jar package',
        types=('java archive',),
        mimes=('application/java-archive',),
        exts=('.jar', '.zip',),
        kind=package,
        extractors=[extract_zip]
    ),

    Handler(name='Java Jar package',
        types=('zip archive',),
        mimes=('application/zip',),
        exts=('.jar',),
        kind=package,
        extractors=[extract_zip]
    ),

    Handler(name='Java archive',
        types=('zip archive',),
        mimes=('application/zip', 'application/java-archive',),
        exts=('.war', '.sar', '.ear',),
        kind=regular,
        extractors=[extract_zip]
    ),

    Handler(name='Python package',
        types=('zip archive',),
        mimes=('application/zip',),
        exts=('.egg', '.whl', '.pyz', '.pex',),
        kind=package,
        extractors=[extract_zip]
    ),

    Handler(name='xz',
        types=('xz compressed',),
        mimes=('application/x-xz',) ,
        exts=('.xz',),
        kind=regular,
        extractors=[extract_xz]
    ),

    Handler(name='lzma',
        types=('lzma compressed',),
        mimes=('application/x-xz',) ,
        exts=('.lzma',),
        kind=regular,
        extractors=[extract_lzma]
    ),

    Handler(name='Tar xz',
        types=('xz compressed',),
        mimes=('application/x-xz',) ,
        exts=('.tar.xz', '.txz', '.tarxz',),
        kind=regular_nested,
        extractors=[extract_xz, extract_tar]
    ),

    Handler(name='Tar lzma',
        types=('lzma compressed',),
        mimes=('application/x-lzma',) ,
        exts=('tar.lzma', '.tlz', '.tarlz', '.tarlzma'),
        kind=regular_nested,
        extractors=[extract_lzma, extract_tar]
    ),

    Handler(name='Tar gzip',
        types=('gzip compressed',),
        mimes=('application/x-gzip',),
        exts=('.tgz', '.tar.gz', '.tar.gzip', '.targz',
              '.targzip', '.tgzip',),
        kind=regular_nested,
        extractors=[extract_tar]
    ),

    Handler(name='Gzip',
        types=('gzip compressed',),
        mimes=('application/x-gzip',),
        exts=('.gz', '.gzip',),
        kind=regular,
        extractors=[uncompress_gzip]
    ),

    Handler(name='Dia diagram doc',
        types=('gzip compressed',),
        mimes=('application/x-gzip',),
        exts=('.dia',),
        kind=docs,
        extractors=[uncompress_gzip]
    ),

    Handler(name='bzip2',
        types=('bzip2 compressed',),
        mimes=('application/x-bzip2',),
        exts=('.bz', '.bz2', 'bzip2',),
        kind=regular,
        extractors=[uncompress_bzip2]
    ),

    Handler(name='Tar bzip2',
        types=('bzip2 compressed',),
        mimes=('application/x-bzip2',),
        exts=('.tar.bz2', '.tar.bz', '.tar.bzip', '.tar.bzip2',
              '.tbz', '.tbz2', '.tb2', '.tarbz2',),
        kind=regular_nested,
        extractors=[extract_tar]
    ),

    Handler(name='RAR',
        types=('rar archive',),
        mimes=('application/x-rar',),
        exts=('.rar',),
        kind=regular,
        extractors=[extract_rar]
    ),

    Handler(name='Microsoft cab',
        types=('microsoft cabinet',),
        mimes=('application/vnd.ms-cab-compressed',),
        exts=('.cab',),
        kind=package,
        extractors=[extract_cab]
    ),

    Handler(name='Microsoft MSI Installer',
        types=('msi installer',),
        mimes=('application/x-msi',),
        exts=('.msi',),
        kind=package,
        extractors=[extract_msi]
    ),

    # notes: this catches all  exe and fails often
    Handler(name='InstallShield Installer',
        types=('installshield',),
        mimes=('application/x-dosexec',),
        exts=('.exe',),
        kind=special_package,
        extractors=[extract_ishield]
    ),

    Handler(name='Nullsoft Installer',
        types=('nullsoft installer',),
        mimes=('application/x-dosexec',),
        exts=('.exe',),
        kind=special_package,
        extractors=[extract_nsis]
    ),

    Handler(name='ar archive',
        types=('current ar archive',),
        mimes=('application/x-archive',),
        exts=('.ar',),
        kind=regular,
        extractors=[extract_ar]
    ),

    Handler(name='Static Library',
        types=('current ar archive', 'current ar archive random library',),
        mimes=('application/x-archive',),
        exts=('.a', '.lib', '.out', '.ka'),
        kind=package,
        extractors=[extract_ar]
    ),

    Handler(name='Debian package',
        types=('debian binary package',),
        mimes=('application/x-archive',
               'application/vnd.debian.binary-package',),
        exts=('.deb',),
        kind=package,
        extractors=[extract_deb]
    ),

    Handler(name='RPM package',
        types=('rpm ',),
        mimes=('application/x-rpm',),
        exts=('.rpm', '.srpm', '.mvl', '.vip',),
        kind=package,
        extractors=[extract_rpm, extract_cpio]
    ),

    Handler(name='7zip',
        types=('7-zip archive',),
        mimes=('application/x-7z-compressed',),
        exts=('.7z',),
        kind=regular,
        extractors=[extract_7z]
    ),

    Handler(name='Tar 7zip',
        types=('7-zip archive',),
        mimes=('application/x-7z-compressed',),
        exts=('.tar.7z', '.tar.7zip', '.t7z',),
        kind=regular_nested,
        extractors=[extract_7z, extract_tar]
    ),

    Handler(name='shar shell archive',
        types=('posix shell script',),
        mimes=('text/x-shellscript',),
        exts=('.sha', '.shar', '.bin'),
        kind=special_package,
        extractors=[]
    ),

    Handler(name='cpio',
        types=('cpio archive',),
        mimes=('application/x-cpio',),
        exts=('.cpio',),
        kind=regular,
        extractors=[extract_cpio]
    ),

    Handler(name='Z',
        types=("compress'd data",),
        mimes=('application/x-compress',),
        exts=('.z',),
        kind=regular,
        extractors=[extract_Z]
    ),

    Handler(name='Tar Z',
        types=("compress'd data",),
        mimes=('application/x-compress',),
        exts=('.tz', '.tar.z', '.tarz',),
        kind=regular_nested,
        extractors=[extract_Z, extract_tar]
    ),

    Handler(name='Apple dmg',
        types=('zlib compressed',),
        mimes=('application/zlib',),
        exts=('.dmg', '.sparseimage',),
        kind=package,
        extractors=[extract_iso]
    ),

    Handler(name='ISO CD image',
        types=('iso 9660 cd-rom', 'high sierra cd-rom'),
        mimes=('application/x-iso9660-image',),
        exts=('.iso', '.udf', '.img'),
        kind=file_system,
        extractors=[extract_iso]
    ),

    Handler(name='squashfs FS',
        types=('squashfs',),
        mimes=(),
        exts=(),
        kind=file_system,
        extractors=[extract_squashfs]
    ),

    Handler(name='Patch',
        types=('diff', 'patch',),
        mimes=('text/x-diff',),
        exts=('.diff', '.patch',),
        kind=patches,
        extractors=[extract_patch]
    ),
]
