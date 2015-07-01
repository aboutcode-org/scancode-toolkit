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
from collections import defaultdict
import logging
import os
import shutil
import time

from commoncode import filetype
from commoncode import fileutils
from commoncode import fileset
from commoncode import ignore

import extractcode
from extractcode import archive
from extractcode import is_extraction_path

logger = logging.getLogger('extractcode.extract')
# import sys
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# logger.setLevel(logging.DEBUG)


"""
Extract archives and compressed files to get the file content available for
further processing. This the high level extraction entry point and includes
recursive extractions an.

This is NOT a general purpose un-archiver. The code tries hard to do the right
thing, BUT the extracted files are not meant to be something that can be
faithfully re-archived to get an equivalent set of files. The purpose here is
to extract the content of the archives as faithfully and safely as possible to
make this content available for scanning.

In particular:

 - Permissions and owners stored in archives are ignored entirely: The
   extracted content is always owned and readable by the user who ran the
   extraction.
 - Special files are never extracted (such as FIFO, character devices, etc)

 - Symlinks may be replaced by plain file copies as if they were regular
   files. Hardlinks are recreated as regular files, not as hardlinks to the
   original file.

 - Files and directories may be renamed when their name is a duplicate. And a
   name may be considered a duplicate ignore upper and lower case mixes even
   on case-sensitive file systems. In particular when an archive contains the
   same file path several times, every paths will be extracted with different
   files names, even though using a regular tool for extraction would have
   overwritten previous paths with the last path.

 - Paths may be converted to a safe ASCII alternative that is portable across OSes.

 - Symlinks, relative paths and absolute paths pointing outside of the archive
   are replaced and renamed in such a way that all the extract content of an
   archive exist under a single target extraction directory. This process
   includes eventually creating "synthetic" or dummy paths that did not exist
   in the original archive.
"""

"""
A job is a unit of work to extract a source file location to a target dir.
"""
ExtractJob = namedtuple('ExtractJob', 'src tgt kinds recurse warnings errors')


def extract(location, kinds=extractcode.all_kinds, recurse=False):
    """
    Extract archives `kinds` at `location` recursively if `recurse`.
    """
    start = time.time()
    logger.debug('extract(%(location)r, %(kinds)r, %(recurse)r\n' % locals())
    results = []
    top_jobs = get_jobs(location, kinds, recurse)
    process(top_jobs, results)
    dur = time.time() - start
    cnt = len(results)
    logger.debug('extract %(location)r: %(dur)ds, %(cnt)d jobs\n' % locals())
    return results


def job_messages(job):
    """
    Return a list of message strings for an ExtractJob.
    """
    src = job.src
    tgt = job.tgt
    recurse = 'recursively ' if job.recurse else 'shallow '

    kinds = []
    for k in job.kinds:
        lab = extractcode.kind_labels[k]
        if lab not in kinds:
            kinds.append(lab)
    kinds = ','.join(kinds)

    warnings = ['Warning: %r: %r' % (k, v,) for k, v in job.warnings.items()]
    errors = job.errors
    msg = 'Extracted %(recurse)s: %(src)r to: %(tgt)r for %(kinds)s' % locals()
    return [msg] + errors + warnings


def get_jobs(location, kinds, recurse):
    """
    Yield `ExtractJob` objects based on `location`, `recurse` and  `kinds`. If
    `location` is a directory, walks the directory and yield `ExtractJob` for
    extractible files. If `location` is a file, yield an `ExtractJob` if
    extractible.
    """
    logger.debug('get_jobs(%(location)r, %(kinds)r, %(recurse)r)\n' % locals())
    if not filetype.is_special(location) and not is_vcs(location):
        if filetype.is_file(location):
            logger.debug('get_jobs: %(location)r is_file.\n' % locals())
            yield get_job(location, kinds, recurse)
        else:
            logger.debug('get_jobs: %(location)r is_dir\n' % locals())
            # NOTE: never recurse in VCS files
            for top, dirs, files in fileutils.walk(location, ignorer=is_vcs):
                logger.debug('get_jobs: top:%(top)s' % locals())
                if not recurse:
                    if is_extraction_path(top):
                        logger.debug('get_jobs: breaking:%(top)s' % locals())
                        break
                    drs = dirs[:]
                    for d in dirs:
                        if is_extraction_path(d):
                            dirs.remove(d)

                for l in dirs + files:
                    loc = os.path.join(top, l)
                    logger.debug('get_jobs: loc:%(loc)s' % locals())
                    for job in get_jobs(loc, kinds, recurse):
                        yield job


def process(jobs, results):
    """
    Process the `jobs` iterable of ExtractJob and put the results in the
    results list. Recurse as needed, proceeding top-down, depth-first.
    """
    for job in jobs:
        if not job:
            continue
        logger.debug('Executing job: %(job)r...\n' % locals())
        if extractcode.is_extracted(job.src):
            logger.debug('Already extracted: %(job)r...\n' % locals())
        else:
            # do not re-extract for now.
            try:
                extractor = archive.get_extractor(job.src, job.kinds)
                tmp_tgt = fileutils.get_temp_dir('extract')
                job.warnings.update(extractor(job.src, tmp_tgt))
                tgt_parent= os.path.dirname(job.tgt)
                fileutils.create_dir(tgt_parent)
                shutil.move(tmp_tgt, job.tgt)
            except Exception, e:
                msg = ('run_job: ERROR: %(job)r.\n' % locals())
                logger.debug(msg)
                job.errors.append(str(e))
                job.errors.append('Extracted files were removed.')
#                 if os.path.exists(tmp_tgt):
#                     fileutils.delete(tmp_tgt)
#                 if os.path.exists(job.tgt):
#                     fileutils.delete(job.tgt)
            finally:
                # we have no errors at this stage.
                logger.debug('run_job: DONE: %(job)r.\n' % locals())
                results.append(job)

        # get and process more jobs if recurse
        if job.recurse:
            logger.debug('run_job: RECURSE: %(job)r.\n' % locals())
            process(get_jobs(job.tgt, job.kinds, job.recurse), results)


def is_vcs(location):
    return fileset.match(location, includes=ignore.ignores_VCS, excludes={})


def get_job(location, kinds, recurse):
    """
    Return an `ExtractJob` if `location` is extractible, or None.
    """
    is_extractible = (filetype.is_file(location)
        and archive.can_extract(location)
        and archive.should_extract(location, kinds)
    )

    if is_extractible and not is_vcs(location):
        target = extractcode.get_extraction_path(location)
        warnings = defaultdict(list)
        errors = []
        job = ExtractJob(location, target, kinds, recurse, warnings, errors)
        logger.debug('get_job: Building: %(job)r.\n' % locals())
        return job
    else:
        logger.debug('get_job: %(location)r is not extractible.\n' % locals())
