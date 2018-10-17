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
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import deque
from collections import OrderedDict
from functools import partial
import json
import os
from os import walk as os_walk
from os.path import abspath
from os.path import exists
from os.path import expanduser
from os.path import join
from os.path import normpath
import posixpath
import traceback
import sys

import attr
from intbitset import intbitset

from scancode_config import scancode_temp_dir

from commoncode.datautils import List
from commoncode.datautils import Mapping
from commoncode.datautils import String

from commoncode.filetype import is_file as filetype_is_file
from commoncode.filetype import is_special

from commoncode.fileutils import POSIX_PATH_SEP
from commoncode.fileutils import WIN_PATH_SEP
from commoncode.fileutils import as_posixpath
from commoncode.fileutils import create_dir
from commoncode.fileutils import delete
from commoncode.fileutils import file_name
from commoncode.fileutils import fsdecode
from commoncode.fileutils import fsencode
from commoncode.fileutils import parent_directory
from commoncode.fileutils import splitext_name

from commoncode import ignore
from commoncode.system import on_linux

# Python 2 and 3 support
try:
    # Python 2
    unicode
    str_orig = str
    bytes = str  # NOQA
    str = unicode  # NOQA
except NameError:
    # Python 3
    unicode = str  # NOQA

"""
This module provides Codebase and Resource objects as an abstraction for files
and directories used throughout ScanCode. ScanCode deals with a lot of these as
they are the basic unit of processing.

A Codebase is a tree of Resource. A Resource represents a file or directory and
holds essential file information as attributes. At runtime, scan data is added
as attributes to a Resource. Resource are kept in memory or saved on disk.

This module handles all the details of walking files, path handling and caching.
"""

# Tracing flags
TRACE = False
TRACE_DEEP = False


def logger_debug(*args):
    pass


if TRACE or TRACE_DEEP:
    import logging

    logger = logging.getLogger(__name__)
    # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(
            ' '.join(isinstance(a, unicode) and a or repr(a) for a in args))


class ResourceNotInCache(Exception):
    pass


class UnknownResource(Exception):
    pass


@attr.s(slots=True)
class LogEntry(object):
    """
    Represent a codebase log entry. Each tool that transforms the codebase
    should create a LogEntry and append it to the codebase logentries list.
    """
    tool = String(help='Tool used such as scancode-toolkit.')
    tool_version = String(default='', help='Tool version used such as v1.2.3.')
    options = Mapping(help='Mapping of key/values describing the options used with this tool.')
    notice = String(default='', help='Notice text for this tool.')
    start_timestamp = String(help='Start timestamp for this log entry.')
    end_timestamp = String(help='End timestamp for this log entry.')
    message = String(help='Message text.')
    errors = List(help='List of error messages.')

    def to_dict(self):
        return attr.asdict(self, dict_factory=OrderedDict)


class Codebase(object):
    """
    Represent a codebase being scanned. A Codebase is a tree of Resources.
    """

    # we do not really need slots but this is a way to ensure we have tight
    # control on object attributes
    __slots__ = (
        'original_location',
        'full_root',
        'strip_root',
        'location',
        'has_single_resource',
        'resource_attributes',
        'resource_class',
        'resource_ids',
        'root',
        'is_file',

        'temp_dir',

        'resources',
        'max_in_memory',
        'all_in_memory',
        'all_on_disk',
        'cache_dir',

        'log_entries',
        'current_log_entry',

        'codebase_attributes',
        'attributes',

        'counters',
        'timings',
        'errors',
    )

    def __init__(self, location, resource_attributes=None,
                 codebase_attributes=None,
                 full_root=False, strip_root=False,
                 temp_dir=scancode_temp_dir,
                 max_in_memory=10000):
        """
        Initialize a new codebase rooted at the `location` existing file or
        directory.

        `resource_attributes` is an ordered mapping of attr Resource attributes
        such as plugin-provided attributes: these will be added to a Resource
        sub-class crafted for this codebase.

        `strip_root` and `full_root`: boolean flags: these control the values
        of the path attribute of the codebase Resources. These are mutually
        exclusive.
        If `strip_root` is True, strip the first `path` segment of a Resource
        unless the codebase contains a single root Resource.
        If `full_root` is True the path is an an absolute path.

        `temp_dir` is the base temporary directory to use to cache resources on
        disk and other temporary files.

        `max_in_memory` is the maximum number of Resource instances to keep in
        memory. Beyond this number, Resource are saved on disk instead. -1 means
        no memory is used and 0 means unlimited memory is used.
        """
        self.original_location = location
        self.full_root = full_root
        self.strip_root = strip_root

        # Resource sub-class to use: Configured with attributes in _populate
        self.resource_class = Resource

        self.resource_attributes = resource_attributes or OrderedDict()
        self.codebase_attributes = codebase_attributes or OrderedDict()

        # setup location
        ########################################################################
        if on_linux:
            location = fsencode(location)
        else:
            location = fsdecode(location)

        location = abspath(normpath(expanduser(location)))
        location = location.rstrip(POSIX_PATH_SEP).rstrip(WIN_PATH_SEP)

        # TODO: we should also accept to create "virtual" codebase without a
        # backing filesystem location
        assert exists(location)
        # FIXME: what if is_special(location)???
        self.location = location
        self.is_file = filetype_is_file(location)

        # True if this codebase root is a file or an empty directory.
        self.has_single_resource = bool(self.is_file or not os.listdir(location))

        # Set up caching, summary, timing, and error info
        self._setup_essentials(temp_dir, max_in_memory)

        # finally walk the location and populate
        ########################################################################
        self._populate()

    def _setup_essentials(self, temp_dir=scancode_temp_dir, max_in_memory=10000):
        """
        Set the remaining Codebase attributes

        `temp_dir` is the base temporary directory to use to cache resources on
        disk and other temporary files.

        `max_in_memory` is the maximum number of Resource instances to keep in
        memory. Beyond this number, Resource are saved on disk instead. -1 means
        no memory is used and 0 means unlimited memory is used.
        """

        # setup Resources
        ########################################################################
        # root resource, never cached on disk
        self.root = None

        # set index of existing resource ids ints, initially allocated with
        # 10000 positions (this will grow as needed)
        self.resource_ids = intbitset(10000)

        # setup caching
        ########################################################################
        # dir used for caching and other temp files
        self.temp_dir = temp_dir

        # maximmum number of Resource objects kept in memory cached in this
        # Codebase. When the number of in-memory Resources exceed this number,
        # the next Resource instances are saved to disk instead and re-loaded
        # from disk when used/needed.
        self.max_in_memory = max_in_memory

        # map of {rid: resource} for resources that are kept in memory
        self.resources = {}
        # use only memory
        self.all_in_memory = max_in_memory == 0
        # use only disk
        self.all_on_disk = max_in_memory == -1
        # dir where the on-disk cache is stored
        self.cache_dir = None
        if not self.all_in_memory:
            # this is unique to this codebase instance
            self.cache_dir = get_codebase_cache_dir(temp_dir=temp_dir)

        # setup extra and misc attributes
        ########################################################################

        # stores a list of LogEntry records for this codebase
        self.log_entries = []
        self.current_log_entry = None

        # mapping of scan counters at the codebase level such
        # as the number of files and directories, etc
        self.counters = OrderedDict()

        # mapping of timings for scan stage as {stage: time in seconds as float}
        # This is populated automatically.
        self.timings = OrderedDict()

        # list of errors from collecting the codebase details (such as
        # unreadable file, etc).
        self.errors = []

    def _get_next_rid(self):
        """
        Return the next available resource id.
        """
        return len(self.resource_ids)

    def _get_resource_cache_location(self, rid, create=False):
        """
        Return the location where to get/put a Resource in the cache given a
        Resource `rid`. Create the directories if requested.
        """
        if not self.cache_dir:
            return
        resid = (b'%08x'if on_linux else '%08x') % rid
        cache_sub_dir, cache_file_name = resid[-2:], resid
        parent = join(self.cache_dir, cache_sub_dir)
        if create and not exists(parent):
            create_dir(parent)
        return join(parent, cache_file_name)

    # TODO: add populate progress manager!!!
    def _populate(self):
        """
        Populate this codebase with Resource objects.

        Population is done by walking its `location` topdown, breadth-first,
        first creating first file then directory Resources both sorted in case-
        insensitive name order.

        Special files, links and VCS files are ignored.
        """

        # Codebase attributes to use. Configured with plugin attributes if present.
        cbac = get_codebase_attributes_class(self.codebase_attributes)
        self.attributes = cbac()

        # Resource sub-class to use. Configured with plugin attributes if present
        self.resource_class = attr.make_class(
            name=b'ScannedResource',
            attrs=self.resource_attributes or {},
            slots=True,
            # frozen=True,
            bases=(Resource,))

        def err(_error):
            """os.walk error handler"""
            self.errors.append(
                ('ERROR: cannot populate codebase: %(_error)r\n' % _error)
                +traceback.format_exc())

        def skip_ignored(_loc):
            """Always ignore VCS and some special filetypes."""
            ignored = partial(ignore.is_ignored, ignores=ignore.ignores_VCS)

            if TRACE_DEEP:
                logger_debug()
                logger_debug('Codebase.populate: walk: ignored loc:', _loc,
                             'ignored:', ignored(_loc),
                             'is_special:', is_special(_loc))

            return is_special(_loc) or ignored(_loc)

        def create_resources(_seq, _top, _parent, _is_file):
            """Create Resources of parent from a seq of files or directories."""
            _seq.sort(key=lambda p: (p.lower(), p))
            for name in _seq:
                location = join(_top, name)
                if skip_ignored(location):
                    continue
                res = self._create_resource(name, parent=_parent, is_file=_is_file)
                if not _is_file:
                    # on the plain, bare FS, files cannot be parents
                    parent_by_loc[location] = res
                if TRACE: logger_debug('Codebase.populate:', res)

        root = self._create_root_resource()
        if TRACE: logger_debug('Codebase.populate: root:', root)

        if self.has_single_resource:
            # there is nothing else to do for a single file or a single
            # childless directory
            return

        # track resources parents by location during construction.
        # NOTE: this cannot exhaust memory on a large codebase, because we do
        # not keep parents already walked and we walk topdown.
        parent_by_loc = {root.location: root}

        # walk proper
        for top, dirs, files in os_walk(root.location, topdown=True, onerror=err):
            if skip_ignored(top):
                continue
            # the parent reference is needed only once in a top-down walk, hence
            # the pop
            parent = parent_by_loc.pop(top)
            create_resources(files, top, parent, _is_file=True)
            create_resources(dirs, top, parent, _is_file=False)

    def _create_root_resource(self):
        """
        Create and return the root Resource of this codebase.
        """
        # we cannot recreate a root if it exists!!
        if self.root:
            raise TypeError('Root resource already exists and cannot be recreated')

        location = self.location
        name = file_name(location)

        # do not strip root for codebase with a single Resource.
        if self.strip_root:
            if self.has_single_resource:
                path = fsdecode(name)
            else:
                # NOTE: this may seem weird but the root path will be an empty
                # string for a codebase root with strip_root=True if not
                # single_resource
                path = ''
        else:
            path = get_path(location, location, full_root=self.full_root,
                            strip_root=self.strip_root)
        if TRACE:
            logger_debug('  Codebase._create_root_resource:', path)
            logger_debug()

        root = self.resource_class(name=name, location=location, path=path,
                                   rid=0, pid=None, is_file=self.is_file)

        self.resource_ids.add(0)
        self.resources[0] = root
        self.root = root
        return root

    def _create_resource(self, name, parent, is_file=False, path=None, resource_data=None):
        """
        Create and return a new Resource in this codebase with `name` as a child
        of the `parent` Resource.
        `name` is always in native OS-preferred encoding (e.g. byte on Linux,
        unicode elsewhere).
        """
        if parent is None:
            raise TypeError('Cannot create resource without parent.')

        rid = self._get_next_rid()

        if self._use_disk_cache_for_resource(rid):
            cache_location = self._get_resource_cache_location(rid, create=True)
        else:
            cache_location = None

        # If the codebase is virtual, then there is no location
        parent_location = parent.location
        if parent_location:
            location = join(parent_location, name)
        else:
            location = None

        # If the codebase is virtual, we provide the path
        if not path:
            path = posixpath.join(parent.path, fsdecode(name))

        if TRACE:
            logger_debug('  Codebase._create_resource: parent.path:', parent.path, 'path:', path)

        resource_data = resource_data or {}
        if resource_data:
            resource_data = remove_properties_and_basics(resource_data)
        child = self.resource_class(
            name=name,
            location=location,
            path=path,
            cache_location=cache_location,
            rid=rid,
            pid=parent.rid,
            is_file=is_file,
            **resource_data
        )

        self.resource_ids.add(rid)
        parent.children_rids.append(rid)
        # TODO: fixme, this is not great to save also the parent :|
        self.save_resource(parent)
        self.save_resource(child)
        return child

    def get_current_log_entry(self):
        """
        Return the current LogEntry. Create it if it does not exists.
        """
        if not self.current_log_entry:
            self.current_log_entry = LogEntry()
            self.log_entries.append(self.current_log_entry)
        return self.current_log_entry

    def exists(self, resource):
        """
        Return True if the Resource with `rid` exists in the codebase.
        """
        return resource.rid in self.resource_ids

    def _use_disk_cache_for_resource(self, rid):
        """
        Return True if Resource `rid` should be cached on-disk or False if it
        should be cached in-memory.
        """
        if TRACE:
            msg = ['    Codebase._use_disk_cache_for_resource:, rid:', rid, 'mode:']
            if rid == 0:
                msg.append('root')
            elif self.all_on_disk:
                msg.append('all_on_disk')
            elif self.all_in_memory:
                msg.append('all_in_memory')
            else:
                msg.extend(['mixed:', 'self.max_in_memory:', self.max_in_memory])
                if rid < self.max_in_memory:
                    msg.append('from memory')
                else:
                    msg.append('from disk')
            logger_debug(*msg)

        if rid == 0:
            return False
        elif self.all_on_disk:
            return True
        elif self.all_in_memory:
            return False
        # mixed case where some are in memory and some on disk
        elif  rid < self.max_in_memory:
            return False
        else:
            return True

    def _exists_in_memory(self, rid):
        """
        Return True if Resource `rid` exists in the codebase memory cache.
        """
        return rid in self.resources

    def _exists_on_disk(self, rid):
        """
        Return True if Resource `rid` exists in the codebase disk cache.
        """
        cache_location = self._get_resource_cache_location(rid)
        if cache_location:
            return exists(cache_location)

    def get_resource(self, rid):
        """
        Return the Resource with `rid` or None if it does not exists.
        """
        if TRACE:
            msg = ['  Codebase.get_resource:', 'rid:', rid]
            if rid == 0:
                msg.append('root')
            elif not rid or rid not in self.resource_ids:
                msg.append('not in resources!')
            elif self._use_disk_cache_for_resource(rid):
                msg.extend(['from disk', 'exists:', self._exists_on_disk(rid)])
            else:
                msg.extend(['from memory', 'exists:', self._exists_in_memory(rid)])
            logger_debug(*msg)

        if rid == 0:
            res = attr.evolve(self.root)
        elif not rid or rid not in self.resource_ids:
            res = None
        elif self._use_disk_cache_for_resource(rid):
            res = self._load_resource(rid)
        else:
            res = self.resources.get(rid)
            res = attr.evolve(res)
        if TRACE:
            logger_debug('    Resource:', res)
        return res

    def save_resource(self, resource):
        """
        Save the `resource` Resource to cache (in memory or disk).
        """
        if TRACE:
            msg = ['  Codebase.save_resource:', resource]
            rid = resource.rid
            if resource.is_root:
                msg.append('root')
            elif rid not in self.resource_ids:
                msg.append('missing resource')
            elif self._use_disk_cache_for_resource(rid):
                msg.extend(['to disk:', 'exists:', self._exists_on_disk(rid)])
            else:
                msg.extend(['to memory:', 'exists:', self._exists_in_memory(rid)])
            logger_debug(*msg)

        if not resource:
            return

        rid = resource.rid
        if rid not in self.resource_ids:
            raise UnknownResource('Not part of codebase: %(resource)r' % locals())

        if resource.is_root:
            # this can possibly damage things badly
            self.root = resource

        if self._use_disk_cache_for_resource(rid):
            self._dump_resource(resource)
        else:
            self.resources[rid] = resource

    def _dump_resource(self, resource):
        """
        Dump a Resource to the disk cache.
        """
        cache_location = resource.cache_location

        if not cache_location:
            raise TypeError('Resource cannot be dumped to disk and is used only'
                            'in memory: %(resource)r' % resource)

        # TODO: consider messagepack or protobuf for compact/faster processing?
        with open(cache_location , 'wb') as cached:
            cached.write(json.dumps(resource.serialize(), check_circular=False))

    # TODO: consider adding a small LRU cache in front of this for perf?
    def _load_resource(self, rid):
        """
        Return a Resource with `rid` loaded from the disk cache.
        """
        cache_location = self._get_resource_cache_location(rid, create=False)

        if TRACE:
            logger_debug('    Codebase._load_resource: exists:', exists(cache_location), 'cache_location:', cache_location)

        if not exists(cache_location):
            raise ResourceNotInCache(
                'Failed to load Resource: %(rid)d from %(cache_location)r' % locals())

        # TODO: consider messagepack or protobuf for compact/faster processing
        try:
            with open(cache_location, 'rb') as cached:
                data = json.load(cached, object_pairs_hook=OrderedDict, encoding='utf-8')
                return self.resource_class(**data)
        except Exception:
            with open(cache_location, 'rb') as cached:
                cached_data = cached.read()
            msg = ('ERROR: failed to load resource from cached location: {cache_location} with content:\n\n'.format(**locals())
                +repr(cached_data)
                +'\n\n'
                +traceback.format_exc())
            raise Exception(msg)

    def _remove_resource(self, resource):
        """
        Remove the `resource` Resource object from the resource tree.
        Does not remove children.
        """
        if resource.is_root:
            raise TypeError('Cannot remove the root resource from '
                            'codebase:', repr(resource))
        rid = resource.rid
        # remove from index.
        self.resource_ids.discard(rid)
        # remove from in-memory cache. The disk cache is cleared on exit.
        self.resources.pop(rid, None)
        if TRACE:
            logger_debug('Codebase._remove_resource:', resource)

    def remove_resource(self, resource):
        """
        Remove the `resource` Resource object and all its children from the
        resource tree. Return a set of removed Resource ids.
        """
        if TRACE:
            logger_debug('Codebase.remove_resource')
            logger_debug('  resource', resource)

        if resource.is_root:
            raise TypeError('Cannot remove the root resource from '
                            'codebase:', repr(resource))

        removed_rids = set()

        # remove all descendants bottom up to avoid out-of-order access to
        # removed resources
        for descendant in resource.walk(self, topdown=False):
            self._remove_resource(descendant)
            removed_rids.add(descendant.rid)

        # remove resource from parent
        parent = resource.parent(self)
        if TRACE: logger_debug('    parent', parent)
        parent.children_rids.remove(resource.rid)
        parent.save(self)

        # remove resource proper
        self._remove_resource(resource)
        removed_rids.add(resource.rid)

        return removed_rids

    def walk(self, topdown=True, skip_root=False):
        """
        Yield all resources for this Codebase walking its resource tree.
        Walk the tree top-down, depth-first if `topdown` is True, otherwise walk
        bottom-up.

        Each level is sorted by children sort order (e.g. without-children, then
        with-children and each group by case-insensitive name)

        If `skip_root` is True, the root resource is not returned unless this is
        a codebase with a single resource.
        """
        root = self.root
        # include root if no children (e.g. codebase with a single resource)
        if skip_root and not root.has_children():
            skip_root = False

        root = attr.evolve(root)
        if topdown and not skip_root:
            yield root

        for res in root.walk(self, topdown):
            yield res

        if not topdown and not skip_root:
            yield root

    def walk_filtered(self, topdown=True, skip_root=False):
        """
        Walk this Codebase as with walk() but doe not return Resources with
        `is_filtered` flag set to True.
        """
        for resource in self.walk(topdown, skip_root):
            if resource.is_filtered:
                continue
            yield resource

    def compute_counts(self, skip_root=False, skip_filtered=False):
        """
        Compute and update the counts of every resource.
        Return a tuple of top level counters (files_count, dirs_count,
        size_count) for this codebase.

        The counts are computed differently based on these falsg:
        - If `skip_root` is True, the root resource is not included in counts.
        - If `skip_filtered` is True, resources with `is_filtered` set to True
          are not included in counts.
        """
        self.update_counts(skip_filtered=skip_filtered)

        root = self.root
        files_count = root.files_count
        dirs_count = root.dirs_count
        size_count = root.size_count

        if (skip_root and not root.is_file) or (skip_filtered and root.is_filtered):
            return files_count, dirs_count, size_count

        if root.is_file:
            files_count += 1
        else:
            dirs_count += 1
        size_count += root.size

        return files_count, dirs_count, size_count

    def update_counts(self, skip_filtered=False):
        """
        Update files_count, dirs_count and size_count attributes of each
        Resource in this codebase based on the current state.

        If `skip_filtered` is True, resources with `is_filtered` set to True are
        not included in counts.
        """
        # note: we walk bottom up to update things in the proper order
        # and the walk MUST NOT skip filtered, only the compute
        for resource in self.walk(topdown=False):
            try:
                resource._compute_children_counts(self, skip_filtered)
            except Exception:
                path = resource.path
                msg = ('ERROR: cannot compute children counts for: {path}:\n'.format(**locals())
                +traceback.format_exc())
                raise Exception(msg)

    def clear(self):
        """
        Purge the codebase cache(s).
        """
        delete(self.cache_dir)

    def lowest_common_parent(self):
        """
        Return a Resource that is the lowest common parent of all the files (and
        not directories) of this codebase.
        Derived from Python genericpath.commonprefix().
        """
        # only consider files and ignore directories
        paths = [res.path.split('/') for res in self.walk() if res.is_file]
        # We leverage the fact that resources are sorted and walked sorted too
        first = paths[0]  # could be min(paths)
        last = paths[-1]  # could be max(paths)
        lcp = first
        for i, segment in enumerate(first):
            if segment != last[i]:
                lcp = first[:i]
                break
        # walk again to get the resource object back
        lcp_path = '/'.join(lcp)
        for res in self.walk():
            if res.path == lcp_path:
                return res


def to_native_path(path):
    """
    Return `path` using the preferred OS encoding (bytes on Linux,
    Unicode elsewhere) given a unicode or bytes path string.
    """
    if not path:
        return path
    if on_linux:
        return fsencode(path)
    else:
        return fsdecode(path)


def to_decoded_posix_path(path):
    """
    Return `path` as a Unicode POSIX path given a unicode or bytes path string.
    """
    return fsdecode(as_posixpath(path))


@attr.attributes(slots=True)
class Resource(object):
    """
    A resource represent a file or directory with essential "file information"
    and the scanned data details.

    A Resource is a tree that models the fileystem tree structure.

    In order to support lightweight and smaller objects that can be serialized
    and deserialized (such as pickled in multiprocessing) without pulling in a
    whole object tree, a Resource does not store its related objects directly:
    the Codebase it belongs to, its parent Resource and its Resource children
    objects are stored only as integer ids. Querying the Resource relationships
    and walking the Resources tree requires to lookup the corresponding object
    by id in the codebase object.
    """
    # the file or directory name in the OS preferred representation (either
    # bytes on Linux and Unicode elsewhere)
    name = attr.attrib(converter=to_native_path)

    # the file or directory absolute location in the OS preferred representation
    # (either bytes on Linux and Unicode elsewhere) using the OS native path
    # separators.
    location = attr.attrib(converter=to_native_path, repr=False)

    # the file or directory POSIX path decoded as unicode using the filesystem
    # encoding. This is the path that will be reported in output and can be
    # either one of these:
    # - if the codebase was created with strip_root==True, this is a path
    #   relative to the root, stripped from its root segment unless the codebase
    #   contains a single file.
    # - if the codebase was created with full_root==True, this is an absolute
    #   path
    path = attr.attrib(converter=to_decoded_posix_path)

    # resource id as an integer
    # the root of a Resource tree has a pid==0 by convention
    rid = attr.ib()

    # parent resource id of this resource as an integer
    # the root of a Resource tree has a pid==None by convention
    pid = attr.ib()

    # location of the file where this resource can be chached on disk in the OS
    # preferred representation (either bytes on Linux and Unicode elsewhere)
    cache_location = attr.attrib(default=None, converter=to_native_path, repr=False)

    # True for file, False for directory
    is_file = attr.ib(default=False)

    # True if this Resource should be filtered out, e.g. skipped from the
    # returned list of resources
    is_filtered = attr.ib(default=False)

    # a list of rids
    children_rids = attr.ib(default=attr.Factory(list), repr=TRACE)

    # external data to serialize
    size = attr.ib(default=0, type=int, repr=TRACE)

    # These attributes are re/computed for directories and files with children
    # they represent are the for the full descendants of a Resource
    size_count = attr.ib(default=0, type=int, repr=False)
    files_count = attr.ib(default=0, type=int, repr=False)
    dirs_count = attr.ib(default=0, type=int, repr=False)

    # list of scan error strings
    scan_errors = attr.ib(default=attr.Factory(list), repr=False)

    # Duration in seconds as float to run all scans for this resource
    scan_time = attr.ib(default=0, repr=False)

    # mapping of timings for each scan as {scan_key: duration in seconds as a float}
    scan_timings = attr.ib(default=attr.Factory(OrderedDict), repr=False)

    # stores a mapping of extra data for this Resource this data is
    # never returned in a to_dict() and not meant to be saved in the
    # final scan results. Instead it can be used to store extra data
    # attributes that may be useful during a scan processing but are not
    # usefuol afterwards. Be careful when using this not to override
    # keys/valoues that may have been created by some other plugin or
    # process
    extra_data = attr.ib(default=attr.Factory(dict), repr=False)

    @property
    def is_root(self):
        return self.rid == 0

    @property
    def type(self):
        return 'file' if self.is_file else 'directory'

    @type.setter
    def type(self, value):
        if value == 'file':
            self.is_file = True
        else:
            self.is_file = False

    @property
    def base_name(self):
        # FIXME: we should call the function only once
        base_name, _extension = splitext_name(self.name, is_file=self.is_file)
        return base_name

    @base_name.setter
    def base_name(self, value):
        pass

    @property
    def extension(self):
        # FIXME: we should call the function only once
        _base_name, extension = splitext_name(self.name, is_file=self.is_file)
        return extension

    @extension.setter
    def extension(self, value):
        pass

    @classmethod
    def get(cls, codebase, rid):
        """
        Return the Resource with `rid` in `codebase` or None if it does not
        exists.
        """
        return codebase.get_resource(rid)

    def save(self, codebase):
        """
        Save this resource in `codebase` (in memory or disk).
        """
        return codebase.save_resource(self)

    def remove(self, codebase):
        """
        Remove this resource and all its children from the codebase.
        Return a set of removed Resource ids.
        """
        return codebase.remove_resource(self)

    def create_child(self, codebase, name, is_file=False):
        """
        Create and return a new child Resource of this resource in `codebase`
        with `name`. `name` is always in native OS-preferred encoding (e.g. byte
        on Linux, unicode elsewhere).
        """
        return codebase._create_resource(name, self, is_file)

    def _compute_children_counts(self, codebase, skip_filtered=False):
        """
        Compute counts and update self with these counts from direct children.
        Return a tuple of counters (files_count, dirs_count, size_count) for the
        direct children of this Resource.

        If `skip_filtered` is True, skip resources with the `is_filtered` flag
        set to True.

        Note: because certain files such as archives can have children, they may
        have a files and dirs counts. The size of a directory is aggregated size
        of its files (including the count of files inside archives).
        """
        files_count = dirs_count = size_count = 0
        for child in self.children(codebase):
            files_count += child.files_count
            dirs_count += child.dirs_count
            size_count += child.size_count

            if skip_filtered and child.is_filtered:
                continue

            if child.is_file:
                files_count += 1
            else:
                dirs_count += 1
            size_count += child.size

        self.files_count = files_count
        self.dirs_count = dirs_count
        self.size_count = size_count
        self.save(codebase)

        return files_count, dirs_count, size_count

    def walk(self, codebase, topdown=True,):
        """
        Yield all descendant Resources of this Resource. Does not include self.

        Walk the tree top-down, depth-first if `topdown` is True, otherwise walk
        bottom-up.

        Each level is sorted by children sort order (e.g. without-children, then
        with-children and each group by case-insensitive name)
        """

        for child in self.children(codebase):
            child = attr.evolve(child)
            if topdown:
                yield child
            for subchild in child.walk(codebase, topdown):
                yield subchild
            if not topdown:
                yield child

    def has_children(self):
        """
        Return True is this Resource has children.
        """
        return bool(self.children_rids)

    def children(self, codebase):
        """
        Return a sorted sequence of direct children Resource objects for this Resource
        or an empty sequence.
        Sorting is by resources without children, then resource with children
        (e.g. directories or files with children), then case-insentive name.
        """
        _sorter = lambda r: (r.has_children(), r.name.lower(), r.name)
        get_resource = codebase.get_resource
        return sorted((get_resource(rid) for rid in self.children_rids), key=_sorter)

    def has_parent(self):
        """
        Return True is this Resource has children.
        """
        return not self.is_root

    def parent(self, codebase):
        """
        Return the parent Resource object for this Resource or None.
        """
        return codebase.get_resource(self.pid)

    def has_siblings(self, codebase):
        """
        Return True is this Resource has siblings.
        """
        return self.has_parent() and self.parent(codebase).has_children()

    def siblings(self, codebase):
        """
        Return a sequence of sibling Resource objects for this Resource
        or an empty sequence.
        """
        if self.has_parent():
            return self.parent(codebase).children(codebase)
        return []

    def ancestors(self, codebase):
        """
        Return a sequence of ancestor Resource objects from self to root
        (includes self).
        """
        if self.is_root:
            return [self]

        ancestors = deque()
        ancestors_appendleft = ancestors.appendleft
        codebase_get_resource = codebase.get_resource
        current = self
        # walk up the parent tree up to the root
        while not current.is_root:
            ancestors_appendleft(current)
            current = codebase_get_resource(current.pid)
        # append root too
        ancestors_appendleft(current)
        return list(ancestors)

    def distance(self, codebase):
        """
        Return the distance as the number of path segments separating this
        Resource from the `codebase` root Resource.

        The codebase root has a distance of zero ot itself. Its direct children
        have a distance of one, and so on.
        """
        if self.is_root:
            return 0
        return len(self.ancestors(codebase)) - 1

    def to_dict(self, with_timing=False, with_info=False):
        """
        Return a mapping of representing this Resource and its scans.
        """
        res = OrderedDict()
        res['path'] = self.path
        res['type'] = self.type

        if with_info:
            res['name'] = fsdecode(self.name)
            res['base_name'] = fsdecode(self.base_name)
            res['extension'] = fsdecode(self.extension)
            res['size'] = self.size

        # exclude by default all of the "standard", default Resource fields
        self_fields_filter = attr.filters.exclude(*attr.fields(Resource))

        # this will catch every attribute that has been added dynamically, such
        # as scan-provided resource_attributes
        other_data = attr.asdict(
            self, filter=self_fields_filter, dict_factory=OrderedDict)

        # FIXME: make a deep copy of the data first!!!!
        # see https://github.com/nexB/scancode-toolkit/issues/1199
        res.update(other_data)

        if with_timing:
            res['scan_time'] = self.scan_time or 0
            res['scan_timings'] = self.scan_timings or {}

        if with_info:
            res['files_count'] = self.files_count
            res['dirs_count'] = self.dirs_count
            res['size_count'] = self.size_count

        res['scan_errors'] = self.scan_errors
        if TRACE:
            logger_debug('Resource.to_dict:', res)
        return res

    def serialize(self):
        """
        Return a mapping of representing this Resource and its scans in a form
        that is fully serializable and can be used to reconstruct a Resource.
        All path-derived OS-native strings are decoded to Unicode for ulterior
        JSON serialization.
        """
        # we save all fields, not just the one in .to_dict()
        saveable = attr.asdict(self, dict_factory=OrderedDict)
        saveable['name'] = fsdecode(self.name)
        if self.location:
            saveable['location'] = fsdecode(self.location)
        if self.cache_location:
            saveable['cache_location'] = fsdecode(self.cache_location)
        return saveable


def get_path(root_location, location, full_root=False, strip_root=False):
    """
    Return a Unicode POSIX `path` (using "/"  separators) derived from
    `root_location` and `location` (both absolute native locations
    respectively the root location of the codebase and to the Resource).

    - If `full_root` is True, return an absolute path. Otherwise return a
      relative path where the first segment is the root name.

    - If `strip_root` is True, return a relative path without the first root
      segment. Ignored if `full_root` is True.
    """

    posix_loc = fsdecode(as_posixpath(location))
    if full_root:
        return posix_loc

    if not strip_root:
        # keep the root directory name by default
        root_loc = parent_directory(root_location)
    else:
        root_loc = root_location

    posix_root_loc = fsdecode(as_posixpath(root_loc)).rstrip('/') + '/'

    return posix_loc.replace(posix_root_loc, '', 1)


def get_codebase_cache_dir(temp_dir=scancode_temp_dir):
    """
    Return a new, created and unique per-run cache storage directory path rooted
    at the `temp_dir` base temp directory in the OS-preferred representation
    (either bytes on Linux and Unicode elsewhere).
    """
    from commoncode.fileutils import get_temp_dir
    from commoncode.timeutils import time2tstamp

    prefix = 'scancode-scans-' + time2tstamp() + '-'
    cache_dir = get_temp_dir(base_dir=temp_dir, prefix=prefix)
    if on_linux:
        cache_dir = fsencode(cache_dir)
    else:
        cache_dir = fsdecode(cache_dir)
    return cache_dir


@attr.s(slots=True)
class _CodebaseAttributes(object):
    def to_dict(self):
        return attr.asdict(self, dict_factory=OrderedDict)


def get_codebase_attributes_class(attributes):
    return attr.make_class(
        name=b'CodebaseAttributes',
        attrs=attributes or {},
        slots=True,
        bases=(_CodebaseAttributes,)
    )


def build_attributes_defs(mapping, ignored_keys=()):
    """
    Given a mapping, return an ordered mapping of attributes built from the
    mapping keys and values.
    """
    attributes = OrderedDict()

    # We add the attributes that are not in standard_res_attributes already
    # FIXME: we should not have to infer the schema may be?
    for key, value in mapping.items():
        if key in ignored_keys or key in attributes:
            continue
        if isinstance(value, (list, tuple)):
            attributes[key] = attr.ib(default=attr.Factory(list))
        elif isinstance(value, dict):
            attributes[key] = attr.ib(default=attr.Factory(OrderedDict))
        else:
            attributes[key] = attr.ib(default=None)

    return attributes


class VirtualCodebase(Codebase):

    __slots__ = (
        # TRUE iff the loaded virtual codebase has file information
        'with_info',
        'scan_location',
    )

    def __init__(self, location,
                 resource_attributes=None,
                 codebase_attributes=None,
                 full_root=False, strip_root=False,
                 temp_dir=scancode_temp_dir,
                 max_in_memory=10000):
        """
        Initialize a new virtual codebase from JSON scan file at `location`.
        See the Codebase parent class for other arguments
        """
        self.scan_location = abspath(normpath(expanduser(location)))

        # Resource sub-class to use
        self.resource_class = None

        self._setup_essentials(temp_dir, max_in_memory)


        self.resource_attributes = resource_attributes or OrderedDict()
        self.resource_class = Resource

        self.codebase_attributes = codebase_attributes or OrderedDict()

        self._populate()

    def _get_top_level_attributes(self, scan_data):
        """
        Populate this codebase log entries and other top-level data from `scan_data`.
        """

    def _populate(self):
        """
        Populate this codebase with Resource objects.

        Population is done by loading JSON scan results and creating new
        Resources for each result.

        This assumes that the input JSON scan results are in top-down order.
        """

        # Load scan data at once TODO: since we load it all does it make sense
        # to have support for caching at all?
        with open(self.scan_location, 'rb') as f:
            scan_data = json.load(f, object_pairs_hook=OrderedDict)

        # Collect codebase-level attributes and build a class, then load
        ##########################################################
        standard_cb_attrs = set(['scancode_notice', 'scancode_version',
            'scancode_options', 'scan_start', 'files_count', 'files'])
        all_cb_attributes = build_attributes_defs(scan_data, standard_cb_attrs)
        # We add in the attributes that we collected from the plugins. They come
        # last for now.
        for name, plugin_attribute in self.codebase_attributes.items():
            if name not in all_cb_attributes:
                all_cb_attributes[name] = plugin_attribute

        cbac = get_codebase_attributes_class(all_cb_attributes or {})
        self.attributes = cbac()

        # now populate top level codebase attributes
        for attr_name in all_cb_attributes:
            value = scan_data.get(attr_name)
            if value:
                setattr(self.attributes, attr_name, value)

        # Collect resources: build attributes attach to Resource
        ##########################################################
        resources_data = scan_data['files']
        if not resources_data:
            raise Exception('Input has no file-level scan results: {}'.format(
                self.json_scan_location))
        resources_data = iter(resources_data)

        # The root MUST be the first resource. We use it as a template for
        # actual Resource attributes
        root_data = resources_data.next()

        # Collect the existing attributes of the standard Resource class
        standard_res_attributes = set(f.name for f in attr.fields(Resource))
        # add these properties since they are fields but are serialized
        properties = set(['type', 'base_name', 'extension'])
        standard_res_attributes.update(properties)

        # We collect attributes that are not in standard_res_attributes already
        # FIXME: we should not have to infer the schema may be?
        all_res_attributes = build_attributes_defs(root_data, standard_res_attributes)
        # We add the attributes that we collected from the plugins. They come
        # last for now.
        for name, plugin_attribute in self.resource_attributes.items():
            if name not in all_res_attributes:
                all_res_attributes[name] = plugin_attribute

        # Create the Resource class with the desired attributes
        self.resource_class = attr.make_class(
            name=b'ScannedResource',
            attrs=all_res_attributes or {},
            slots=True,
            # frozen=True,
            bases=(Resource,))

        # do we have file information attributes in this codebase data?
        self.with_info = any(a in root_data for a in (
            'name',
            'base_name',
            'extension',
            'size',
            'files_count',
            'dirs_count',
            'size_count',)
        )

        def get_resource_basic_attributes(_resource_data):
            """
            Return name, path, is_file attributes (e.g. "basic" attributes) given a
            `_resource_data` mapping of resource attributes.
            """
            _path = _resource_data.get('path')
            _name = _resource_data.get('name', None)
            if not _name:
                _name = file_name(_path)
            _file_type = _resource_data.get('type', 'file')
            _is_file = _file_type == 'file'
            return _name, _path, _is_file

        # Create root resource
        root_name, root_path, root_is_file = get_resource_basic_attributes(root_data)
        root_resource = self._create_root_resource(root_name, root_path, root_is_file, root_data)

        # To help recreate the resource tree we keep a mapping by path of any
        # parent resource
        parent_by_path = {root_path: root_resource}

        # resources data MUST be in top-down order
        for resource_data in resources_data:
            name, path, is_file = get_resource_basic_attributes(resource_data)
            parent_path = parent_directory(path).rstrip('/')
            # this must succeed since we must be in the proper sort order
            parent = parent_by_path[parent_path]
            resource = self._create_resource(name, parent, is_file, path, resource_data)

            # Files are not parents (for now), so we do not need to add this
            # to the parent_by_path mapping
            if not is_file:
                parent_by_path[path] = resource
            self.save_resource(resource)

    def _create_root_resource(self, name, path, is_file, root_data):
        """
        Create and return the root Resource of this codebase.
        """
        # we cannot recreate a root if it exists!!
        if self.root:
            raise TypeError('Root resource already exists and cannot be recreated')
        if root_data:
            root_data = remove_properties_and_basics(root_data)
        root = self.resource_class(
            name=name, location=None, path=path, rid=0, pid=None, is_file=is_file, **root_data)

        self.resource_ids.add(0)
        self.resources[0] = root
        self.root = root
        return root


def remove_properties_and_basics(resource_data):
    """
    Given a mapping of resource_data attributes to use as "kwargs", return a new
    mapping with the known properties removed.
    """
    return {k: v for k, v in resource_data.items()
            if k not in ('type', 'base_name', 'extension', 'path', 'name')}
