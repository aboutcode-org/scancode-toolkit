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

# Contains code derived from Python tarfile.extractall.
#
# Copyright (C) 2002 Lars Gustabel <lars@gustaebel.de>
# All rights reserved.
#
# Permission  is  hereby granted,  free  of charge,  to  any person
# obtaining a  copy of  this software  and associated documentation
# files  (the  "Software"),  to   deal  in  the  Software   without
# restriction,  including  without limitation  the  rights to  use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies  of  the  Software,  and to  permit  persons  to  whom the
# Software  is  furnished  to  do  so,  subject  to  the  following
# conditions:
#
# The above copyright  notice and this  permission notice shall  be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS  IS", WITHOUT WARRANTY OF ANY  KIND,
# EXPRESS OR IMPLIED, INCLUDING  BUT NOT LIMITED TO  THE WARRANTIES
# OF  MERCHANTABILITY,  FITNESS   FOR  A  PARTICULAR   PURPOSE  AND
# NONINFRINGEMENT.  IN  NO  EVENT SHALL  THE  AUTHORS  OR COPYRIGHT
# HOLDERS  BE LIABLE  FOR ANY  CLAIM, DAMAGES  OR OTHER  LIABILITY,
# WHETHER  IN AN  ACTION OF  CONTRACT, TORT  OR OTHERWISE,  ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# Credits: Gustavo Niemeyer, Niels Gustabel, Richard Townsend.


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import copy
import logging
from collections import defaultdict
from contextlib import closing

# This import adds support for multistream BZ2 files
# This is a patched tarfile using a Python2 backport for bz2file from Python3
# Because of http://bugs.python.org/issue20781
from extractcode.tarfile_patch import tarfile
from commoncode.paths import resolve
from extractcode import ExtractError

logger = logging.getLogger('extractcode')
# logging.basicConfig(level=logging.DEBUG)


"""
Low level support for tar-based archive extraction using Python built-in tar
support.
"""


def list_entries(location):
    """
    Yield entries from the archive file at location.
    """
    raise NotImplementedError()


def extract(location, target_dir):
    """
    Extract all files from the tar archive file at `location` in the
    `target_dir`. Plain tars and tars compressed with gzip and bzip2 are
    supported transparently. Other compressions such as xz or lzma are handled
    in two steps. Return a list of warnings messages. Raise Exceptions on errors.

    Skip special files. Contains code derived from Python tarfile.extractall.

    Copyright (C) 2002 Lars Gustabel <lars@gustaebel.de>
    All rights reserved.

    Permission  is  hereby granted,  free  of charge,  to  any person
    obtaining a  copy of  this software  and associated documentation
    files  (the  "Software"),  to   deal  in  the  Software   without
    restriction,  including  without limitation  the  rights to  use,
    copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies  of  the  Software,  and to  permit  persons  to  whom the
    Software  is  furnished  to  do  so,  subject  to  the  following
    conditions:

    The above copyright  notice and this  permission notice shall  be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS  IS", WITHOUT WARRANTY OF ANY  KIND,
    EXPRESS OR IMPLIED, INCLUDING  BUT NOT LIMITED TO  THE WARRANTIES
    OF  MERCHANTABILITY,  FITNESS   FOR  A  PARTICULAR   PURPOSE  AND
    NONINFRINGEMENT.  IN  NO  EVENT SHALL  THE  AUTHORS  OR COPYRIGHT
    HOLDERS  BE LIABLE  FOR ANY  CLAIM, DAMAGES  OR OTHER  LIABILITY,
    WHETHER  IN AN  ACTION OF  CONTRACT, TORT  OR OTHERWISE,  ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.

    Credits: Gustavo Niemeyer, Niels Gustabel, Richard Townsend.
    """
    assert location
    assert target_dir

    warnings = defaultdict(list)

    # track directories to fixup modification times at the end
    directories = []

    with closing(tarfile.open(location)) as tar:
        tar.errorlevel = 1
        names = set()
        for tinfo in tar.getmembers():
            is_special = not any((tinfo.isfile(), tinfo.isdir(), tinfo.islnk(), tinfo.issym()))
            if is_special:
                # FIXME: we should not report a warning?
                warnings[tinfo.name].append('Skipping special file.')
                continue

            # hardlinks and symlinks are treated as regular files
            if tinfo.islnk() or tinfo.issym():
                if tinfo.issym():
                    # Always search the entire archive.
                    linkname = '/'.join(filter(None,
                               (os.path.dirname(tinfo.name), tinfo.linkname)))
                    limit = None
                else:
                    # Search the archive before the link, because a hard link
                    # is just a reference to an already archived file.
                    linkname = tinfo.linkname
                    limit = tinfo

                realfile = tar._getmember(linkname, tarinfo=limit, normalize=True)
                if realfile is None:
                    warnings[tinfo.name].append('Skipping broken link to: %(linkname)s' % locals())
                    continue

                if not (realfile.isfile() or realfile.isdir()):
                    warnings[tinfo.name].append('Skipping link to special file: %(linkname)s' % locals())
                    continue

                if realfile.islnk() or realfile.issym():
                    # FIXME: Check tarbomb
                    warnings[tinfo.name].append('Skipping multi-level link to: %(linkname)s' % locals())
                    continue

                # replace the tarinfo with the linked-to file info
                # but keep the link name
                lname = tinfo.name
                tinfo = copy.copy(realfile)
                tinfo.name = lname

            # FIXME: we skip duplicates, this can happen and will fail if the
            # location is read-only, we should instead rename duplicates
            # using extractcode.new_name
            if tinfo.name.lower() in names:
                warnings[tinfo.name].append('Skipping duplicate file name.')
            names.add(tinfo.name.lower())

            tinfo = copy.copy(tinfo)
            # ensure we do stay always under the target dir
            tinfo.name = resolve(tinfo.name)
            # Extract all files with a safe mode
            # FIXME: use the current user mask
            tinfo.mode = 0700
            # keep a list of dirs to fix mtime once they are all created
            if tinfo.isdir():
                directories.append(tinfo)
            try:
                tar.extract(tinfo, target_dir)
            except Exception, e:
                # FIXME: we must keep the traceback for diagnostics
                raise ExtractError()

    # Set correct mtime on directories, starting from the bottom of the tree
    def dir_sorter(a, b):
        return cmp(a.name, b.name)

    for tinfo in sorted(directories, cmp=dir_sorter, reverse=True):
        dir_loc = os.path.join(target_dir, tinfo.name)
        try:
            # NOTE: this may not work at all on Windows
            tar.utime(tinfo, dir_loc)
        except Exception, e:
            warnings[tinfo.name].append(str(e))

    # collect warnings
    warning_messages = []
    for pathname, messages in warnings.items():
        msg = pathname + ': ' + '\n'.join(messages).replace(target_dir, '.')
        if msg not in warning_messages:
            warning_messages.append(msg)

    return warning_messages

