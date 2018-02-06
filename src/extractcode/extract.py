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
from __future__ import unicode_literals

from collections import namedtuple
from functools import partial
import logging
from os.path import abspath
from os.path import expanduser
from os.path import join
import traceback

from commoncode import fileutils
from commoncode import ignore
import extractcode
from extractcode import archive

logger = logging.getLogger(__name__)
TRACE = False

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

"""
Extract archives and compressed files recursively to get the file content available for
further processing. This the high level extraction entry point.

This is NOT a general purpose un-archiver. The code tries hard to do the right
thing, BUT the extracted files are not meant to be something that can be
faithfully re-archived to get an equivalent archive. The purpose instead is
to extract the content of the archives as faithfully and safely as possible to
make this content available for scanning: some paths may be altered. Some files
may be altered or skipped entirely.

In particular:

 - Permissions and owners stored in archives are ignored entirely: The extracted
   content is always owned and readable by the user who ran the extraction.

 - Special files are never extracted (such as FIFO, character devices, etc)

 - Symlinks may be replaced by plain file copies as if they were regular files.
   Hardlinks may be recreated as regular files, not as hardlinks to the original
   file.

 - Files and directories may be renamed when their name is a duplicate. And a
   name may be considered a duplicate ignore upper and lower case mixes even
   on case-sensitive file systems. In particular when an archive contains the
   same file path several times, every paths will be extracted with different
   files names, even though using a regular tool for extraction would have
   overwritten previous paths with the last path.

 - Paths may be converted to a safe ASCII alternative that is portable across
   OSes.

 - Symlinks, relative paths and absolute paths pointing outside of the archive
   are replaced and renamed in such a way that all the extract content of an
   archive exist under a single target extraction directory. This process
   includes eventually creating "synthetic" or dummy paths that did not exist in
   the original archive.
"""

"""
An ExtractEvent contains data about an archive extraction progress:
 - `source` is the location of the archive being extracted
 - `target` is the target location where things are extracted
 - `done` is a boolean set to True when the extraction is done (even if failed).
 - `warnings` is a mapping of extracted paths to a list of warning messages.
 - `errors` is a list of error messages.
"""
ExtractEvent = namedtuple('ExtractEvent', 'source target done warnings errors')


def extract(location, kinds=extractcode.default_kinds, recurse=False):
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
    ignored = partial(ignore.is_ignored, ignores=ignore.default_ignores, unignores={})
    if TRACE:
        logger.debug('extract:start: %(location)r  recurse: %(recurse)r\n' % locals())
    abs_location = abspath(expanduser(location))
    for top, dirs, files in fileutils.walk(abs_location, ignored):
        if TRACE:
            logger.debug('extract:walk: top:  %(top)r dirs: %(dirs)r files: r(files)r' % locals())

        if not recurse:
            if TRACE:
                drs = set(dirs)
            for d in dirs[:]:
                if extractcode.is_extraction_path(d):
                    dirs.remove(d)
            if TRACE:
                logger.debug('extract:walk: not recurse: removed dirs:' + repr(drs.symmetric_difference(set(dirs))))
        for f in files:
            loc = join(top, f)
            if not recurse and extractcode.is_extraction_path(loc):
                if TRACE:
                    logger.debug('extract:walk not recurse: skipped  file: %(loc)r' % locals())
                continue

            if not archive.should_extract(loc, kinds):
                if TRACE:
                    logger.debug('extract:walk: skipped file: not should_extract: %(loc)r' % locals())
                continue

            target = join(abspath(top), extractcode.get_extraction_path(loc))
            if TRACE:
                logger.debug('extract:target: %(target)r' % locals())
            for xevent in extract_file(loc, target, kinds):
                if TRACE:
                    logger.debug('extract:walk:extraction event: %(xevent)r' % locals())
                yield xevent

            if recurse:
                if TRACE:
                    logger.debug('extract:walk: recursing on target: %(target)r' % locals())
                for xevent in extract(target, kinds, recurse):
                    if TRACE:
                        logger.debug('extract:walk:recurse:extraction event: %(xevent)r' % locals())
                    yield xevent


def extract_file(location, target, kinds=extractcode.default_kinds, verbose=False):
    """
    Extract a single archive at `location` in the `target` directory if it is
    of a kind supported in the `kinds` kind tuple.
    """
    warnings = []
    errors = []
    extractor = archive.get_extractor(location, kinds)
    if TRACE:
        logger.debug('extract_file: extractor: for: %(location)r with kinds: %(kinds)r : ' % locals()
                     + getattr(extractor, '__module__', '')
                     + '.' + getattr(extractor, '__name__', ''))
    if extractor:
        yield ExtractEvent(location, target, done=False, warnings=[], errors=[])
        try:
            # extract first to a temp directory: if there is an error,  the
            # extracted files will not be moved to target
            tmp_tgt = fileutils.get_temp_dir(prefix='scancode-extract-')
            abs_location = abspath(expanduser(location))
            warns = extractor(abs_location, tmp_tgt) or []
            warnings.extend(warns)
            fileutils.copytree(tmp_tgt, target)
            fileutils.delete(tmp_tgt)
        except Exception, e:
            errors = [str(e).strip(' \'"')]
            if verbose:
                errors.append(traceback.format_exc())
            if TRACE:
                tb = traceback.format_exc()
                logger.debug('extract_file: ERROR: %(location)r: %(errors)r\n%(e)r\n%(tb)s' % locals())
            
        finally:
            yield ExtractEvent(location, target, done=True, warnings=warnings, errors=errors)
