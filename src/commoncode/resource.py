#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/aboutcode-org/commoncode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json
import os
import sys
import traceback
from collections import deque
from functools import partial
from hashlib import md5
from operator import itemgetter
from os import walk as os_walk
from os.path import abspath
from os.path import exists
from os.path import expanduser
from os.path import isfile
from os.path import join
from os.path import normpath
from posixpath import dirname as posixpath_parent
from posixpath import join as posixpath_join
from posixpath import normpath as posixpath_normpath

import attr

try:
    from scancode_config import scancode_temp_dir as temp_dir
except ImportError:
    # alway have something there.
    import tempfile

    temp_dir = tempfile.mkdtemp(prefix="scancode-resource-cache")

from commoncode import ignore
from commoncode.datautils import List
from commoncode.datautils import Mapping
from commoncode.datautils import String
from commoncode.filetype import is_file as filetype_is_file
from commoncode.filetype import is_special
from commoncode.fileutils import as_posixpath
from commoncode.fileutils import create_dir
from commoncode.fileutils import delete
from commoncode.fileutils import file_name
from commoncode.fileutils import parent_directory
from commoncode.fileutils import splitext_name

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
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(" ".join(isinstance(a, str) and a or repr(a) for a in args))


class ResourceNotInCache(Exception):
    pass


class UnknownResource(Exception):
    pass


def skip_ignored(location):
    """
    Return True if ``location`` should be skipped.
    Always ignore VCS and some special filetypes.
    """
    ignored = partial(ignore.is_ignored, ignores=ignore.ignores_VCS)

    if TRACE_DEEP:
        logger_debug()
        logger_debug(
            "Codebase.populate: walk: ignored loc:",
            location,
            "ignored:",
            ignored(location),
            "is_special:",
            is_special(location),
        )

    return is_special(location) or ignored(location)


def depth_walk(
    root_location,
    max_depth,
    skip_ignored=skip_ignored,
    error_handler=lambda: None,
):
    """
    Yield a (top, dirs, files) tuple at each step of walking the ``root_location``
    directory recursively up to ``max_depth`` path segments extending from the
    ``root_location``. The behaviour is similar of ``os.walk``.

    Arguments:

    - root_location: Absolute, normalized path for the directory to be walked
    - max_depth: positive integer for fixed depth limit. 0 for no limit.
    - skip_ignored: Callback function that takes a location as argument and
      returns a boolean indicating whether to ignore files in that location.
    - error_handler: Error handler callback. No action taken by default.
    """

    if max_depth < 0:
        raise Exception("ERROR: `max_depth` must be a positive integer or 0.")

    # Find root directory depth using path separator's count
    root_dir_depth = root_location.count(os.path.sep)

    for top, dirs, files in os_walk(root_location, topdown=True, onerror=error_handler):
        # If depth is limited (non-zero)
        if max_depth:
            current_depth = top.count(os.path.sep) - root_dir_depth

        if skip_ignored(top) or (max_depth and current_depth >= max_depth):
            # we clear out `dirs` and `files` to prevent `os_walk` from visiting
            # the files and subdirectories of directories we are ignoring or
            # are not in the specified nesting level
            dirs[:] = []
            files[:] = []
            continue
        yield top, dirs, files


@attr.s(slots=True)
class Header(object):
    """
    Represent a Codebase header. Each tool that transforms the codebase
    should create a Header and append it to the Codebase.headers list.
    """

    tool_name = String(help="Name of the tool used such as scancode-toolkit.")
    tool_version = String(default="", help="Tool version used such as v1.2.3.")
    options = Mapping(help="Mapping of key/values describing the options used with this tool.")
    notice = String(default="", help="Notice text for this tool.")
    start_timestamp = String(help="Start timestamp for this header.")
    end_timestamp = String(help="End timestamp for this header.")
    output_format_version = String(help="Version for the output data format, such as v1.1 .")
    duration = String(help="Scan duration in seconds.")
    message = String(help="Message text.")
    errors = List(help="List of error messages.")
    warnings = List(help="List of warning messages.")
    extra_data = Mapping(help="Mapping of extra key/values for this tool.")

    def to_dict(self):
        return attr.asdict(self, dict_factory=dict)

    @classmethod
    def from_dict(cls, **kwargs):
        """
        Return a Header object deserialized from a `kwargs` mapping of
        key/values. Unknown attributes are ignored.
        """
        known_attributes = set(attr.fields_dict(Header))
        kwargs = {k: v for k, v in kwargs.items() if k in known_attributes}
        return cls(**kwargs)


def ignore_nothing(resource, codebase):
    """
    Return True if `resource` should be ignored.

    This function is used as a callable for `ignored` argument in Codebase and
    Resource walk.
    """
    return False


class Codebase:
    """
    Represent a codebase being scanned. A Codebase is a list of Resources.
    """

    # we do not really need slots but this is a way to ensure we have tight
    # control on object attributes
    __slots__ = (
        "max_depth",
        "location",
        "has_single_resource",
        "resource_attributes",
        "resource_class",
        "root",
        "is_file",
        "temp_dir",
        "resources_by_path",
        "resources_count",
        "paths",
        "max_in_memory",
        "all_in_memory",
        "all_on_disk",
        "cache_dir",
        "headers",
        "current_header",
        "codebase_attributes",
        "attributes",
        "counters",
        "timings",
        "errors",
    )

    # the value returned if the resource is cached
    CACHED_RESOURCE = 1

    def __init__(
        self,
        location,
        resource_attributes=None,
        codebase_attributes=None,
        temp_dir=temp_dir,
        max_in_memory=10000,
        max_depth=0,
        paths=tuple(),
        *args,
        **kwargs,
    ):
        """
        Initialize a new codebase rooted at the ``location`` existing file or
        directory.

        Use an optional list of ``paths`` strings that are paths relative to the
        root ``location`` such that joining the root ``location`` and such a
        path is the ``location`` of this path. If these ``paths`` are provided,
        the codebase will only contain these paths and no other path.

        ``resource_attributes`` is an ordered mapping of attr Resource attributes
        such as plugin-provided attributes: these will be added to a Resource
        sub-class crafted for this codebase.

        ``codebase_attributes`` is an ordered mapping of attr Codebase attributes
        such as plugin-provided attributes: these will be added to a
        CodebaseAttributes sub-class crafted for this codebase.

        ``temp_dir`` is the base temporary directory to use to cache resources on
        disk and other temporary files.

        ``max_in_memory`` is the maximum number of Resource instances to keep in
        memory. Beyond this number, Resource are saved on disk instead. -1 means
        no memory is used and 0 means unlimited memory is used.

        ``max_depth`` is the maximum depth of subdirectories to descend below and
        including `location`.

        ``paths`` is an optional list of of path strings that extend from the
        root ``location``. If provided, the codebase will contain only these
        paths.
        """
        self.max_depth = max_depth

        # Resource sub-class to use: Configured with attributes in _populate
        self.resource_class = Resource

        self.resource_attributes = resource_attributes or {}
        self.codebase_attributes = codebase_attributes or {}

        # setup location
        ########################################################################
        location = os.fsdecode(location)
        location = abspath(normpath(expanduser(location)))
        location = location.rstrip("/\\")
        # TODO: what if is_special(location)???
        assert exists(location)
        self.location = location

        self.is_file = filetype_is_file(location)

        # True if this codebase root is a file or an empty directory.
        self.has_single_resource = bool(self.is_file or not os.listdir(location))

        ########################################################################
        # Set up caching, summary, timing, and error info
        self._setup_essentials(temp_dir, max_in_memory)

        # finally populate
        self.paths = self._prepare_clean_paths(paths)
        self._populate()

    def _prepare_clean_paths(self, paths=tuple()):
        """
        Return a new set of cleaned ``paths`` possibly empty.
        We convert to POSIX and ensure we have no slash at both ends.
        """
        paths = (clean_path(p) for p in (paths or []) if p)

        # we sort by path segments (e.g. essentially a topo sort)
        def _sorter(p):
            return p.split("/")

        return sorted(paths, key=_sorter)

    def _setup_essentials(self, temp_dir=temp_dir, max_in_memory=10000):
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

        # mapping of {path: Resource}. This the key data structure of a Codebase.
        # All resources MUST exist there. When cached to disk the value is CACHED_RESOURCE
        self.resources_by_path = {}
        self.resources_count = 0

        # setup caching
        ########################################################################
        # dir used for caching and other temp files
        self.temp_dir = temp_dir

        # maximum number of Resource objects kept in memory cached in this
        # Codebase. When the number of in-memory Resources exceed this number,
        # the next Resource instances are saved to disk instead and re-loaded
        # from disk when used/needed.
        self.max_in_memory = max_in_memory
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

        # stores a list of Header records for this codebase
        self.headers = []
        self.current_header = None

        # mapping of scan counters at the codebase level such
        # as the number of files and directories, etc
        self.counters = dict()

        # mapping of timings for scan stage as {stage: time in seconds as float}
        # This is populated automatically.
        self.timings = dict()

        # list of error strings from collecting the codebase details (such as
        # unreadable file, etc).
        self.errors = []

    def _get_resource_cache_location(self, path, create_dirs=False):
        """
        Return the location where to get/put a Resource in the cache given a
        Resource `path`. Create the directories if requested.
        """
        if not self.cache_dir:
            return

        if isinstance(path, Resource):
            path = path.path

        path = clean_path(path)

        # for the cached file name, we use an md5 of the path to avoid things being too long
        resid = str(md5(path.encode("utf-8")).hexdigest())
        cache_sub_dir, cache_file_name = resid[-2:], resid

        parent = join(self.cache_dir, cache_sub_dir)
        if create_dirs and not exists(parent):
            create_dir(parent)

        return join(parent, cache_file_name)

    def _collect_codebase_attributes(self, *args, **kwargs):
        """
        Return a mapping of CodebaseAttributes fields to use with this Codebase
        """
        return self.codebase_attributes

    def _build_resource_class(self, *args, **kwargs):
        """
        Return a Resource class to use with this Codebase
        """
        # Resource sub-class to use. Configured with plugin attributes if present
        return attr.make_class(
            name="ScannedResource",
            attrs=self.resource_attributes or {},
            slots=True,
            bases=(Resource,),
        )

    # TODO: add populate progress manager!!!
    def _populate(self):
        """
        Populate this codebase with Resource objects.

        The actual subclass of Resource objects used in this codebase will be
        created as a side effect.

        Population is done by walking its `location` topdown, breadth-first,
        first creating first file then directory Resources both sorted in case-
        insensitive name order.

        Special files, links and VCS files are ignored.
        """
        # Collect headers
        ##########################################################
        self.headers = []

        # Collect codebase-level attributes and build a class, then load
        ##########################################################
        # Codebase attributes to use. Configured with plugin attributes if
        # present.
        self.codebase_attributes = self._collect_codebase_attributes()
        cbac = _CodebaseAttributes.from_attributes(attributes=self.codebase_attributes)
        self.attributes = cbac()

        # Resource sub-class to use. Configured with plugin attributes if present
        ##########################################################
        self.resource_class = self._build_resource_class()

        ##########################################################
        # walk and create resources proper

        # Create root first
        ##########################################################
        root = self._create_root_resource()
        if TRACE:
            logger_debug("Codebase.populate: root:", root)

        if self.has_single_resource:
            # there is nothing else to do for a single file or a single
            # childless directory
            return

        if self.paths:
            return self._create_resources_from_paths(root=root, paths=self.paths)
        else:
            return self._create_resources_from_root(root=root)

    def _create_resources_from_paths(self, root, paths):
        # without paths we iterate the provided paths. We report an error
        # if a path is missing on disk.

        # !!!NOTE: WE DO NOT skip_ignored in this case!!!!!

        base_location = parent_directory(root.location)

        # track resources parents by path during construction to avoid
        # recreating all ancestor directories
        parents_by_path = {root.path: root}

        for path in paths:
            res_loc = join(base_location, path)
            if not exists(res_loc):
                msg = f"ERROR: cannot populate codebase: path: {path!r} not found in {res_loc!r}"
                self.errors.append(msg)
                raise Exception(path, join(base_location, path))
                continue

            # create all parents. The last parent is the one we want to use
            parent = root
            if TRACE:
                logger_debug("Codebase._create_resources_from_paths: parent", parent)
            for parent_path in get_ancestor_paths(path, include_self=False):
                if TRACE:
                    logger_debug(
                        f"  Codebase._create_resources_from_paths: parent_path: {parent_path!r}"
                    )
                if not parent_path:
                    continue
                newpar = parents_by_path.get(parent_path)
                if TRACE:
                    logger_debug("  Codebase._create_resources_from_paths: newpar", repr(newpar))

                if not newpar:
                    newpar = self._get_or_create_resource(
                        name=file_name(parent_path),
                        parent=parent,
                        path=parent_path,
                        is_file=False,
                    )
                    if not newpar:
                        raise Exception(
                            f"ERROR: Codebase._create_resources_from_paths: cannot create parent for: {parent_path!r}"
                        )
                    parent = newpar

                    parents_by_path[parent_path] = parent

                    if TRACE:
                        logger_debug(
                            f"  Codebase._create_resources_from_paths:",
                            f"created newpar: {newpar!r}",
                        )

            res = self._get_or_create_resource(
                name=file_name(path),
                parent=parent,
                path=path,
                is_file=isfile(res_loc),
            )
            if TRACE:
                logger_debug("Codebase._create_resources_from_paths: resource", res)

    def _create_resources_from_root(self, root):
        # without paths we walks the root location top-down

        # track resources parents by location during construction.
        # NOTE: this cannot exhaust memory on a large codebase, because we do
        # not keep parents already walked and we walk topdown.
        parents_by_loc = {root.location: root}

        def err(_error):
            """os.walk error handler"""
            self.errors.append(
                f"ERROR: cannot populate codebase: {_error}\n{traceback.format_exc()}"
            )

        # Walk over the directory and build the resource tree
        for top, dirs, files in depth_walk(
            root_location=root.location,
            max_depth=self.max_depth,
            error_handler=err,
        ):
            parent = parents_by_loc.pop(top)
            for created in self._create_resources(
                parent=parent,
                top=top,
                dirs=dirs,
                files=files,
            ):
                # on the plain, bare FS, files cannot be parents
                if not created.is_file:
                    parents_by_loc[created.location] = created

    def _create_resources(self, parent, top, dirs, files, skip_ignored=skip_ignored):
        """
        Create and yield ``files`` and ``dirs`` children Resources of a
        ``parent`` Resource. These are sorted as: directories then files and by
        lowercase name, then name.
        """
        for names, is_file in [(dirs, False), (files, True)]:
            names.sort(key=lambda p: (p.lower(), p))

            for name in names:
                location = join(top, name)
                if skip_ignored(location):
                    continue
                res = self._get_or_create_resource(
                    name=name,
                    parent=parent,
                    is_file=is_file,
                )
                if TRACE:
                    logger_debug("Codebase.create_resources:", res)
                yield res

    def _create_root_resource(self):
        """
        Create and return the root Resource of this codebase.
        """
        # we cannot recreate a root if it exists!!
        if self.root:
            raise TypeError("Root resource already exists and cannot be recreated")

        location = self.location
        name = file_name(location)

        # do not strip root for codebase with a single Resource.
        path = Resource.build_path(root_location=location, location=location)

        if TRACE:
            logger_debug(f"  Codebase._create_root_resource: {path} is_file: {self.is_file}")
            logger_debug()

        root = self.resource_class(
            name=name,
            location=location,
            # never cached
            cache_location=None,
            path=path,
            is_root=True,
            is_file=self.is_file,
        )

        self.resources_by_path[path] = root
        self.resources_count += 1
        self.root = root
        return root

    def _get_or_create_resource(
        self,
        name,
        parent,
        is_file=False,
        path=None,
    ):
        """
        Create and return a new codebase Resource with ``path`` and ``location``.
        """
        if not parent:
            raise TypeError(
                f"Cannot create resource without parent: name: {name!r}, path: {path!r}"
            )

        # If the codebase is virtual, we provide the path
        if not path:
            path = posixpath_join(parent.path, name)
        path = clean_path(path)

        existing = self.get_resource(path)
        if existing:
            if TRACE:
                logger_debug("  Codebase._get_or_create_resource: path  already exists:", path)
            return existing

        if self._use_disk_cache_for_resource():
            cache_location = self._get_resource_cache_location(path=path, create_dirs=True)
        else:
            cache_location = None

        # NOTE: If the codebase is virtual, then there is no location
        parent_location = parent.location
        if parent_location:
            location = join(parent_location, name)
        else:
            location = None

        if TRACE:
            logger_debug(
                f"  Codebase._get_or_create_resource: with path: {path}\n"
                f"  name={name}, is_file={is_file}"
            )

        child = self.resource_class(
            name=name,
            location=location,
            path=path,
            cache_location=cache_location,
            is_file=is_file,
        )
        self.resources_count += 1

        parent.children_names.append(name)
        self.save_resource(parent)
        self.save_resource(child)
        return child

    def get_or_create_current_header(self):
        """
        Return the current Header. Create it if it does not exists and store
        it in the headers.
        """
        if not self.current_header:
            self.current_header = Header()
            self.headers.append(self.current_header)
        return self.current_header

    def get_files_count(self):
        """
        Return the final files counts for the codebase.
        """
        return self.counters.get("final:files_count", 0)

    def add_files_count_to_current_header(self):
        """
        Add the final files counts for the codebase to the current header.
        Return the files_count.
        """
        files_count = self.get_files_count()
        current_header = self.get_or_create_current_header()
        current_header.extra_data["files_count"] = files_count
        return files_count

    def get_headers(self):
        """
        Return a serialized headers composed only of native Python objects
        suitable for use in outputs.
        """
        return [le.to_dict() for le in (self.headers or [])]

    def exists(self, resource):
        """
        Return True if the Resource path exists in the codebase.
        """
        return resource and resource.path in self.resources_by_path

    def _use_disk_cache_for_resource(self):
        """
        Return True if Resource ``res`` should be cached on-disk or False if it
        should be kept in-memory.
        """

        use_disk_cache = False
        if self.all_on_disk:
            use_disk_cache = True
        elif self.all_in_memory:
            use_disk_cache = False
        else:
            # mixed case where some are in memory and some on disk
            if self.resources_count < self.max_in_memory:
                use_disk_cache = False
            else:
                use_disk_cache = True

        if TRACE:
            logger_debug(
                f"    Codebase._use_disk_cache_for_resource mode: {use_disk_cache} "
                f"on_disk: {self.all_on_disk} "
                f"in_mem: {self.all_in_memory} "
                f"max_in_mem: {self.max_in_memory}"
            )
        return use_disk_cache

    def _exists_in_memory(self, path):
        """
        Return True if Resource `path` exists in the codebase memory cache.
        """
        path = clean_path(path)
        return isinstance(self.resources_by_path.get(path), Resource)

    def _exists_on_disk(self, path):
        """
        Return True if Resource `path` exists in the codebase disk cache.
        """
        path = clean_path(path)
        if not self._exists_in_memory(path):
            cache_location = self._get_resource_cache_location(path, create_dirs=False)
            if cache_location:
                return exists(cache_location)

    # FIXME: the PATH SHOULD NOT INCLUDE THE ROOT NAME
    def get_resource(self, path):
        """
        Return the Resource with `path` or None if it does not exists.
        The ``path`` must be relative to the root (and including the root
        name as its first segment).
        """
        assert isinstance(path, str), f"Invalid path: {path!r} is not a string."
        path = clean_path(path)
        if TRACE:
            msg = ["  Codebase.get_resource:", "path:", path]
            if not path or path not in self.resources_by_path:
                msg.append("not in resources!")
            else:
                msg.extend(["exists on disk:", self._exists_on_disk(path)])
                msg.extend(["exists in memo:", self._exists_in_memory(path)])
            logger_debug(*msg)

        # we use Codebase.CACHED_RESOURCE as a semaphore for existing but only
        # on-disk, non-in-memory resource that we need to load from the disk
        # cache to differentiate from None which means missing
        res = self.resources_by_path.get(path)
        if res is Codebase.CACHED_RESOURCE:
            res = self._load_resource(path)

        elif isinstance(res, Resource):
            res = attr.evolve(res)

        elif res is None:
            pass
        else:
            # this should never happen
            raise Exception(f"get_resource: Internal error when getting {path!r}")

        if TRACE:
            logger_debug("    Resource:", res)
        return res

    def save_resource(self, resource):
        """
        Save the `resource` Resource to cache (in memory or disk).
        """
        if not resource:
            return

        path = clean_path(resource.path)

        if TRACE:
            logger_debug("  Codebase.save_resource:", resource)

        if resource.is_root:
            self.root = resource
            self.resources_by_path[path] = resource

        elif resource.cache_location:
            self._dump_resource(resource)
            self.resources_by_path[path] = Codebase.CACHED_RESOURCE

        else:
            self.resources_by_path[path] = resource

    def _dump_resource(self, resource):
        """
        Dump a Resource to the disk cache.
        """
        cache_location = resource.cache_location

        if not cache_location:
            raise TypeError(
                "Resource cannot be dumped to disk and is used only" f"in memory: {resource}"
            )

        # TODO: consider messagepack or protobuf for compact/faster processing?
        with open(cache_location, "w") as cached:
            cached.write(json.dumps(resource.serialize(), check_circular=False))

    # TODO: consider adding a small LRU cache in front of this for perf?
    def _load_resource(self, path):
        """
        Return a Resource with ``path`` loaded from the disk cache.
        """
        path = clean_path(path)
        cache_location = self._get_resource_cache_location(path, create_dirs=False)

        if TRACE:
            logger_debug(
                "    Codebase._load_resource: exists:",
                exists(cache_location),
                "cache_location:",
                cache_location,
            )

        if not exists(cache_location):
            raise ResourceNotInCache(f"Failed to load Resource: {path} from {cache_location!r}")

        # TODO: consider messagepack or protobuf for compact/faster processing
        try:
            with open(cache_location, "rb") as cached:
                # TODO: Use custom json encoder to encode JSON list as a tuple
                # TODO: Consider using simplejson
                data = json.load(cached)
                return self.resource_class(**data)
        except Exception as e:
            with open(cache_location, "rb") as cached:
                cached_data = cached.read()
            msg = (
                f"ERROR: failed to load resource from cached location: {cache_location} "
                "with content:\n\n" + repr(cached_data) + "\n\n" + traceback.format_exc()
            )
            raise Exception(msg) from e

    def _remove_resource(self, resource):
        """
        Remove the ``resource`` Resource object from this codebase.
        Does not remove children.
        """
        if resource.is_root:
            raise TypeError(f"Cannot remove the root resource from codebase: {resource!r}")

        # remove from in-memory cache. The disk cache is cleared on exit.
        self.resources_by_path.pop(resource.path, None)
        if TRACE:
            logger_debug("Codebase._remove_resource:", resource)

    def remove_resource(self, resource):
        """
        Remove the `resource` Resource object and all its children from the
        codebase. Return a set of removed Resource paths.
        """
        if TRACE:
            logger_debug("Codebase.remove_resource")
            logger_debug("  resource", resource)

        if resource.is_root:
            raise TypeError(f"Cannot remove the root resource from codebase: {resource!r}")

        removed_paths = set()

        # remove all descendants bottom up to avoid out-of-order access to
        # removed resources
        for descendant in resource.walk(self, topdown=False):
            self._remove_resource(descendant)
            removed_paths.add(descendant.location)

        # remove resource from parent
        parent = resource.parent(self)
        if TRACE:
            logger_debug("    parent", parent)
        parent.children_names.remove(resource.name)
        parent.save(self)

        # remove resource proper
        self._remove_resource(resource)
        removed_paths.add(resource.location)

        return removed_paths

    def walk(self, topdown=True, skip_root=False, ignored=ignore_nothing):
        """
        Yield all resources for this Codebase walking its resource tree. Walk
        the tree top-down, depth-first if ``topdown`` is True, otherwise walk
        bottom-up.

        Each level is sorted by children woth this sort order: resource without-
        children first, then resource with-children and each group sorted by
        case-insensitive name.

        If ``skip_root`` is True, the root resource is not returned unless this
        is a codebase with a single resource.

        ``ignored`` is a callable that accepts two arguments, ``resource`` and
        ``codebase``, and returns True if ``resource`` should be ignored.
        """
        root = self.root

        if ignored(resource=root, codebase=self):
            return

        # make a copy
        root = attr.evolve(root)

        # include root if no children (e.g. codebase with a single resource)
        if self.has_single_resource or (skip_root and not root.has_children()):
            skip_root = False

        root = attr.evolve(root)
        if topdown and not skip_root:
            yield root

        for res in root.walk(self, topdown=topdown, ignored=ignored):
            yield res

        if not topdown and not skip_root:
            yield root

    def __iter__(self):
        yield from self.walk()

    def walk_filtered(self, topdown=True, skip_root=False):
        """
        Walk this Codebase as with walk() but does not return Resources with
        `is_filtered` flag set to True.
        """
        for resource in self.walk(topdown=topdown, skip_root=skip_root):
            if not resource.is_filtered:
                yield resource

    def compute_counts(self, skip_root=False, skip_filtered=False):
        """
        Compute, update and save the counts of every resource.
        Return a tuple of top level counters for this codebase as:
          (files_count, dirs_count, size_count).

        The counts are computed differently based on these flags:
        - If ``skip_root`` is True, the root resource is not included in counts.
        - If ``skip_filtered`` is True, resources with ``is_filtered`` set to True
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
        size_count += root.size or 0

        return files_count, dirs_count, size_count

    def update_counts(self, skip_filtered=False):
        """
        Update files_count, dirs_count and size_count attributes of each
        Resource in this codebase based on the current Resource data.

        If ``skip_filtered`` is True, resources with ``is_filtered`` set to True are
        not included in counts.
        """
        # note: we walk bottom up to update things in the proper order
        # and the walk MUST NOT skip filtered, only the compute
        for resource in self.walk(topdown=False):
            try:
                resource._compute_children_counts(self, skip_filtered)
            except Exception as e:
                msg = f"ERROR: cannot compute children counts for: {resource.path}"
                raise Exception(msg) from e

    def clear(self):
        """
        Purge the codebase cache(s).
        """
        delete(self.cache_dir)

    def lowest_common_parent(self):
        """
        Return a Resource that is the lowest common parent (aka. lowest common
        ancestor) of all the files of this codebase, skipping root directory
        segments that are "empty" e.g. with a single child. Return None is this
        codebase contains a single resource.
        """
        if self.has_single_resource:
            return self.root

        for res in self.walk(topdown=True):
            if not res.is_file:
                kids = res.children(self)
                if len(kids) == 1 and not kids[0].is_file:
                    # this is an empty dir with a single dir child, therefore
                    # we shall continue the descent walk
                    continue
                else:
                    # the dir starts to branch: we have our lowest common parent
                    # root
                    break
            else:
                # we are in a case that should never happen
                return self.root
        return res

    def to_list(
        self,
        with_timing=False,
        with_info=False,
        skinny=False,
        full_root=False,
        strip_root=False,
    ):
        """
        Return a list of all Resources of this Codebase as mappings.
        """
        if self.has_single_resource:
            return [
                self.root.to_dict(
                    with_timing=with_timing,
                    with_info=with_info,
                    skinny=skinny,
                    # we never strip root for single res codebase
                    full_root=full_root,
                    strip_root=False,
                )
            ]

        td = partial(
            Resource.to_dict,
            with_timing=with_timing,
            with_info=with_info,
            skinny=skinny,
            full_root=full_root,
            strip_root=strip_root,
        )
        return [td(r) for r in self.walk(skip_root=strip_root)]


def to_decoded_posix_path(path):
    """
    Return `path` as a Unicode POSIX path given a unicode or bytes path string.
    """
    return clean_path(os.fsdecode(as_posixpath(path)))


@attr.attributes(slots=True)
class Resource(object):
    """
    A resource represents a file or directory with essential "file information"
    and the scanned data details.

    A Resource is a tree that models the fileystem tree structure.

    In order to support lightweight and smaller objects that can be serialized
    and deserialized (such as pickled in multiprocessing) without pulling in a
    whole object tree, a Resource does not store its related objects directly:
    - the Codebase it belongs to is never stored.
    - its parent Resource and its Resource children objects are queryable by path.

    Querying the Resource relationships and walking the Resources tree typically
    requires to lookup the corresponding object by path in the Codebase object.
    """

    # the file or directory name in the OS preferred representation (either
    # bytes on Linux and Unicode elsewhere)
    name = attr.attrib(repr=False)

    # the file or directory absolute location in the OS preferred representation
    # (either bytes on Linux and Unicode elsewhere) using the OS native path
    # separators.
    location = attr.attrib(repr=False)

    # the file or directory POSIX path decoded as unicode using the filesystem
    # encoding. This is the path that will be reported in output and is always
    # relative to and starting with the root directory.
    path = attr.attrib(converter=to_decoded_posix_path)

    # location of the file where this resource can be chached on disk in the OS
    # preferred representation (either bytes on Linux and Unicode elsewhere)
    cache_location = attr.attrib(default=None, repr=False)

    # True for file, False for directory
    is_file = attr.ib(default=False)

    # True if this Resource should be filtered out, e.g. skipped from the
    # returned list of resources
    is_filtered = attr.ib(default=False)

    # a list of names
    children_names = attr.ib(default=attr.Factory(list), repr=TRACE)

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
    scan_timings = attr.ib(default=attr.Factory(dict), repr=False)

    # stores a mapping of extra data for this Resource this data is never
    # returned in a to_dict() and not meant to be saved in the final scan
    # results. Instead it can be used to store extra data attributes that may be
    # useful during a scan processing but are not usefuol afterwards. Be careful
    # not to override keys/values that may have been created by some other
    # plugin or process
    extra_data = attr.ib(default=attr.Factory(dict), repr=False)

    is_root = attr.ib(default=False, type=bool, repr=False)

    @property
    def type(self):
        return "file" if self.is_file else "directory"

    @type.setter
    def type(self, value):
        if value == "file":
            self.is_file = True
        else:
            self.is_file = False

    @classmethod
    def build_path(cls, root_location, location):
        """
        Return a POSIX path string (using "/"  separators) of ``location`` relative
        to ``root_location`. Both locations are absolute native locations.
        The returned path has no leading and trailing slashes.  The first segment
        of this path is always the last segment of the ``root_location``.
        For example:
        >>> result = Resource.build_path(r'D:\\foo\\bar', r'D:\\foo\\bar\\baz')
        >>> assert result == 'bar/baz', repr(result)
        >>> result = Resource.build_path('/foo/bar/', '/foo/bar/baz')
        >>> assert result == 'bar/baz', result
        >>> result = Resource.build_path('/foo/bar/', '/foo/bar')
        >>> assert result  == 'bar', result
        """
        root_loc = clean_path(root_location)
        loc = clean_path(location)
        assert loc.startswith(root_loc)

        # keep the root directory name by default
        root_loc = posixpath_parent(root_loc).strip("/")
        path = loc.replace(root_loc, "", 1).strip("/")
        if TRACE:
            logger_debug("build_path:", root_loc, loc, path)
        return path

    def get_path(self, full_root=False, strip_root=False):
        """
        Return a POSIX path string (using "/"  separators) for this resource.
        The returned path has no leading and trailing slashes.

        - If ``full_root`` is True, return an absolute path.

        - If ``strip_root`` is True, return a relative path without the first
          root segment. Ignored if ``full_root`` is True.

        - Otherwise return a relative path where the first segment is the
          ``location`` last path segment.
        """
        if full_root:
            return self.full_root_path
        elif strip_root:
            return self.strip_root_path
        else:
            return self.path

    @property
    def full_root_path(self):
        """
        Return a fully rooted POSIX path stripped from leading and trailing slash
        """
        location = self.location
        if location:
            return clean_path(as_posixpath(self.location))
        else:
            return self.path

    @property
    def strip_root_path(self):
        """
        Return a path relative to the root, stripped from its root segment
        unless the codebase contains a single file or there is only one segment
        in the path.
        """
        return strip_first_path_segment(self.path)

    @property
    def is_dir(self):
        # note: we only store is_file
        return not self.is_file

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

    def extracted_to(self, codebase):
        """
        Return the path this Resource archive was extracted to or None.
        """
        extract_path = f"{self.path}-extract"
        return codebase.get_resource(extract_path)

    def extracted_from(self, codebase):
        """
        Return the path to an archive this Resource was extracted from or None.
        """
        path = self.path
        if "-extract" in path:
            archive_path, _, _ = self.path.rpartition("-extract")
            return codebase.get_resource(archive_path)

    @classmethod
    def get(cls, codebase, path):
        """
        Return the Resource with `path` in `codebase` or None if it does not
        exists.
        """
        return codebase.get_resource(path)

    def save(self, codebase):
        """
        Save this resource in `codebase` (in memory or disk).
        """
        return codebase.save_resource(self)

    def remove(self, codebase):
        """
        Remove this resource and all its children from the codebase.
        Return a set of removed Resource paths.
        """
        return codebase.remove_resource(self)

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
            files_count += child.files_count or 0
            dirs_count += child.dirs_count or 0
            size_count += child.size_count or 0

            if skip_filtered and child.is_filtered:
                continue

            if child.is_file:
                files_count += 1
            else:
                dirs_count += 1
            size_count += child.size or 0

        self.files_count = files_count
        self.dirs_count = dirs_count
        self.size_count = size_count
        self.save(codebase)

        return files_count, dirs_count, size_count

    def walk(self, codebase, topdown=True, ignored=ignore_nothing):
        """
        Yield all descendant Resources of this Resource. Does not include self.

        Walk the tree top-down, depth-first if `topdown` is True, otherwise walk
        bottom-up.

        Each level is sorted by children sort order (e.g. without-children, then
        with-children and each group by case-insensitive name)

        `ignored` is a callable that accepts two arguments, `resource` and `codebase`,
        and returns True if `resource` should be ignored.
        """

        for child in self.children(codebase):
            if not ignored(child, codebase):
                child = attr.evolve(child)
                if topdown:
                    yield child

                for subchild in child.walk(
                    codebase=codebase,
                    topdown=topdown,
                    ignored=ignored,
                ):
                    if not ignored(subchild, codebase):
                        yield subchild

                if not topdown:
                    yield child

    def has_children(self):
        """
        Return True is this Resource has children.
        """
        return bool(self.children_names)

    def children(self, codebase, names=()):
        """
        Return a sorted sequence of direct children Resource objects for this
        Resource or an empty sequence.

        Sorting is by resources without children, then resource with children
        (e.g. directories or files with children), then case-insentive name.
        """
        children_names = self.children_names or []
        if not children_names:
            return []

        if names:
            kids = set(children_names)
            children_names = [n for n in names if n in kids]
            if not children_names:
                return []

        child_path = partial(posixpath_join, self.path)
        get_child = codebase.get_resource
        children = [get_child(path=child_path(name)) for name in children_names]

        def _sorter(r):
            return (r.has_children(), r.name.lower(), r.name)

        return sorted((c for c in children if c), key=_sorter)

    def has_parent(self):
        """
        Return True is this Resource has a parent.
        """
        return not self.is_root

    def parent_path(self):
        """
        Return the parent Resource object for this Resource or None.
        """
        return self.has_parent() and parent_directory(self.path, with_trail=False)

    def parent(self, codebase):
        """
        Return the parent Resource object for this Resource or None.
        """
        parent_path = self.parent_path()
        return parent_path and codebase.get_resource(parent_path)

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
        Return a sequence of ancestor Resource objects from root to self
        (includes self).
        """
        if self.is_root:
            return [self]

        ancestors = deque()
        ancestors_appendleft = ancestors.appendleft
        current = self

        # walk up the parent tree up to the root
        while current and not current.is_root:
            ancestors_appendleft(current)
            current = current.parent(codebase)

        # append root too
        if current:
            ancestors_appendleft(current)

        return list(ancestors)

    def descendants(self, codebase):
        """
        Return a sequence of descendant Resource objects
        (does NOT include self).
        """
        return list(self.walk(codebase=codebase, topdown=True))

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

    def to_dict(
        self,
        with_timing=False,
        with_info=False,
        skinny=False,
        full_root=False,
        strip_root=False,
    ):
        """
        Return a mapping of representing this Resource and its data.

        The path is always a POSIX path stripped from leading and trailing
        slashes and can be either one of these exclusive flags:

        - If ``full_root`` is True, this is a full path when available.

        - If ``strip_root`` is True, this is a path relative to the root,
          stripped from its root segment unless the codebase contains a single
          file with a single root segment. Ignored if ``full_root`` is True.
        """
        path = self.get_path(full_root=full_root, strip_root=strip_root)
        res = dict(path=path, type=self.type)
        if skinny:
            return res

        if with_info:
            res["name"] = self.name
            res["base_name"] = self.base_name
            res["extension"] = self.extension
            res["size"] = self.size

        # exclude by default all of the "standard", default Resource fields
        self_fields_filter = attr.filters.exclude(*attr.fields(Resource))

        # this will catch every attribute that has been added dynamically, such
        # as scan-provided resource_attributes
        other_data = attr.asdict(self, filter=self_fields_filter, dict_factory=dict)

        # FIXME: make a deep copy of the data first!!!!
        # see https://github.com/aboutcode-org/scancode-toolkit/issues/1199
        res.update(other_data)

        if with_timing:
            res["scan_time"] = self.scan_time or 0
            res["scan_timings"] = self.scan_timings or dict()

        if with_info:
            res["files_count"] = self.files_count
            res["dirs_count"] = self.dirs_count
            res["size_count"] = self.size_count

        res["scan_errors"] = self.scan_errors
        if TRACE:
            logger_debug("Resource.to_dict:", res)
        return res

    def serialize(self):
        """
        Return a mapping of representing this Resource and its data in a form
        that is fully serializable (to JSON, YAML, pickle, etc.) and can be used
        to reconstruct a Resource.
        """
        # we save all fields, not just the one in .to_dict()
        serializable = attr.asdict(self)
        serializable["name"] = self.name
        if self.location:
            serializable["location"] = self.location
        if self.cache_location:
            serializable["cache_location"] = self.cache_location
        return serializable


def clean_path(path):
    """
    Return a cleaned and normalized POSIX ``path``.
    """
    path = path or ""
    # convert to posix and ensure we have no slash at both ends
    path = posixpath_normpath(path.replace("\\", "/").strip("/"))
    if path == ".":
        path = ""
    return path


def strip_first_path_segment(path):
    """
    Return a POSIX ``path`` stripped from its first path segment unless there is
    only one segment in which case we return this segment. The returned path has
    no leading and trailing slashes.

    For example::
        >>> strip_first_path_segment('')
        ''
        >>> strip_first_path_segment('foo')
        ''
        >>> strip_first_path_segment('foo/bar/baz')
        'bar/baz'
        >>> strip_first_path_segment('/foo/bar/baz/')
        'bar/baz'
        >>> strip_first_path_segment('foo/')
        ''
    """
    path = clean_path(path)
    if "/" in path:
        _root, _, path = path.partition("/")
        return path
    else:
        return ""


def get_codebase_cache_dir(temp_dir):
    """
    Return a new, created and unique per-run cache storage directory path rooted
    at the `temp_dir` base temp directory in the OS-preferred representation
    (either bytes on Linux and Unicode elsewhere).
    """
    from commoncode.fileutils import get_temp_dir
    from commoncode.timeutils import time2tstamp

    prefix = "scancode-codebase-" + time2tstamp() + "-"
    return get_temp_dir(base_dir=temp_dir, prefix=prefix)


@attr.s(slots=True)
class _CodebaseAttributes(object):
    def to_dict(self):
        return attr.asdict(self, dict_factory=dict)

    @classmethod
    def from_attributes(cls, attributes):
        """
        Return a new sub class of _CodebaseAttributes built with the
        ``attributes`` mapping of "attr" attributes.
        """
        return attr.make_class(
            name="CodebaseAttributes",
            attrs=attributes or {},
            slots=True,
            bases=(_CodebaseAttributes,),
        )


def build_attributes_defs(mapping, ignored_keys=()):
    """
    Given a mapping, return an ordered mapping of attributes built from the
    mapping keys and values.
    """
    attributes = {}

    # We add the attributes that are not in standard_res_attributes already
    # FIXME: we should not have to infer the schema may be?
    for key, value in mapping.items():
        if key in ignored_keys or key in attributes:
            continue
        if isinstance(value, (list, tuple)):
            attributes[key] = attr.ib(default=attr.Factory(list), repr=False)
        elif isinstance(value, dict):
            attributes[key] = attr.ib(default=attr.Factory(dict), repr=False)
        elif isinstance(value, bool):
            attributes[key] = attr.ib(default=False, type=bool, repr=False)
        elif isinstance(value, int):
            attributes[key] = attr.ib(default=0, type=bool, repr=False)
        else:
            attributes[key] = attr.ib(default=None, repr=False)

    return attributes


class VirtualCodebase(Codebase):
    __slots__ = (
        # TRUE iff the loaded virtual codebase has file information
        "with_info",
        "has_single_resource",
    )

    def __init__(
        self,
        location,
        resource_attributes=None,
        codebase_attributes=None,
        temp_dir=temp_dir,
        max_in_memory=10000,
        paths=tuple(),
        *args,
        **kwargs,
    ):
        """
        Initialize a new virtual codebase from JSON scan file at `location`.
        See the Codebase parent class for other arguments.

        `max_depth`, if passed, will be ignored as VirtualCodebase will
        be using the depth of the original scan.
        """
        logger_debug(f"VirtualCodebase: new from: {location!r}")

        self._setup_essentials(temp_dir, max_in_memory)

        self.codebase_attributes = codebase_attributes or {}
        self.resource_attributes = resource_attributes or {}
        self.resource_class = None
        self.has_single_resource = False
        self.location = location

        scan_data = self._get_scan_data(location)
        self.paths = self._prepare_clean_paths(paths)
        self._populate(scan_data)

    def _get_scan_data_helper(self, location):
        """
        Return scan data loaded from `location`, which is a path string
        """
        try:
            return json.loads(location)
        except:
            location = abspath(normpath(expanduser(location)))
            with open(location) as f:
                scan_data = json.load(f)
            return scan_data

    def _get_scan_data(self, location):
        """
        Return scan data loaded from `location` that is either:
        - a path string
        - a JSON string
        - a Python mapping
        - a List or Tuple of paths to JSON scans to combine together. In this
          case all paths are prefixed with codebase-1/, codebase-2., etc.
          incremented for each location.
        Loading also cleans the paths as POSIX.
        """
        if isinstance(location, dict):
            return location

        if isinstance(
            location,
            (
                list,
                tuple,
            ),
        ):
            combined_scan_data = dict(headers=[], files=[])
            for idx, loc in enumerate(location, 1):
                scan_data = self._get_scan_data_helper(loc)
                headers = scan_data.get("headers")
                if headers:
                    combined_scan_data["headers"].extend(headers)
                files = scan_data.get("files")
                if files:
                    for f in files:
                        f["path"] = posixpath_join(f"codebase-{idx}", clean_path(f["path"]))
                    combined_scan_data["files"].extend(files)
                else:
                    raise Exception(
                        f'Input file is missing a "files" (aka. resources) section to load: {loc}'
                    )

            combined_scan_data["headers"] = sorted(
                combined_scan_data["headers"],
                key=lambda x: x["start_timestamp"],
            )
            return combined_scan_data

        return self._get_scan_data_helper(location)

    def _create_empty_resource_data(self):
        """
        Return a dictionary of Resource fields and their default values.

        The fields returned are that which are not part of the standard set of
        Resource attributes.
        """
        # Get fields from the base Resource class and the ScannedResource class
        base_fields = attr.fields(Resource)
        resource_fields = attr.fields(self.resource_class)
        # A dict of {field: field_default_value} for the dynamically created fields
        resource_data = {}
        for field in resource_fields:
            if field in base_fields:
                # We only want the fields that are not part of the base set of fields
                continue
            value = field.default
            if isinstance(value, attr.Factory):
                # For fields that have Factories as values, we set their values
                # to be an instance of whatever type the factory makes
                value = value.factory()
            resource_data[field.name] = value
        return resource_data

    def _collect_codebase_attributes(self, scan_data, *args, **kwargs):
        """
        Return a mapping of CodebaseAttributes fields to use with this Codebase
        """
        # collect attributes from scan data
        all_attributes = (
            build_attributes_defs(
                mapping=scan_data,
                ignored_keys=("headers", "files"),
            )
            or {}
        )

        # We add in the attributes that we collected from the plugins. They come
        # last for now.
        for name, plugin_attribute in self.codebase_attributes.items():
            if name not in all_attributes:
                all_attributes[name] = plugin_attribute

        return all_attributes

    def _build_resource_class(self, sample_resource_data, *args, **kwargs):
        """
        Return a Resource class to use with this Codebase
        """
        # Collect the existing attributes of the standard Resource class
        standard_res_attributes = set(f.name for f in attr.fields(Resource))

        # add these properties since they are fields but are serialized
        properties = set(["type", "base_name", "extension"])
        standard_res_attributes.update(properties)

        # We collect attributes that are not in standard_res_attributes already
        # FIXME: we should not have to infer the schema may be?
        all_res_attributes = build_attributes_defs(
            mapping=sample_resource_data,
            ignored_keys=standard_res_attributes,
        )

        # We add the attributes that we collected from the plugins. They come
        # last for now.
        for name, plugin_attribute in self.resource_attributes.items():
            if name not in all_res_attributes:
                all_res_attributes[name] = plugin_attribute

        # Create the Resource class with the desired attributes
        return attr.make_class(
            name="ScannedResource",
            attrs=all_res_attributes or dict(),
            slots=True,
            bases=(Resource,),
        )

    def _populate(self, scan_data):
        """
        Populate this codebase with Resource objects.

        The actual subclass of Resource objects used in this codebase will be
        created as a side effect.

        Population is done by loading JSON scan results and creating new
        Resources for each files mappings.
        """
        # Collect headers
        ##########################################################
        headers = scan_data.get("headers") or []
        headers = [Header.from_dict(**hle) for hle in headers]
        self.headers = headers

        # Collect codebase-level attributes and build a class, then load
        ##########################################################
        # Codebase attributes to use. Configured with scan_data and plugin
        # attributes if present.
        self.codebase_attributes = self._collect_codebase_attributes(scan_data)
        cbac = _CodebaseAttributes.from_attributes(attributes=self.codebase_attributes)
        self.attributes = cbac()

        # now populate top level codebase attributes
        ##########################################################
        for attr_name in self.codebase_attributes:
            value = scan_data.get(attr_name)
            if value == None:
                continue
            setattr(self.attributes, attr_name, value)

        ##########################################################
        files_data = scan_data.get("files")
        if not files_data:
            raise Exception('Input has no "files" top-level scan results.')

        if len(files_data) == 1:
            # we will shortcut to populate the codebase with a single root resource
            self.has_single_resource = True
            root_is_file = files_data[0].get("type") == "file"
        else:
            root_is_file = False

        # Create a virtual root if we are merging multiple input scans together
        location = self.location
        multiple_inputs = (
            isinstance(
                location,
                (
                    list,
                    tuple,
                ),
            )
            and len(location) > 1
        )

        # Iterate through all Resources to collect any attribute in any resource
        # as sample data. The paths were cleaned on loading
        # NOTE: We also:
        # - add a new "segments" attributes with path split in segments
        # - populate a set of unique root names to to check if all scanned
        #   Resources share a common root or need a new virtual root

        root_names = set()
        root_names_add = root_names.add

        sample_resource_data = {}
        sample_resource_data_update = sample_resource_data.update

        for fdata in files_data:
            sample_resource_data_update(fdata)
            segments = fdata["path"].split("/")
            root_names_add(segments[0])
            fdata["path_segments"] = segments

        # Resource sub-class to use. Configured with all known scanned file
        # attributes and plugin attributes if present
        ##########################################################
        self.resource_class = self._build_resource_class(sample_resource_data)

        # do we have file information attributes in this codebase data?
        self.with_info = any(
            a in sample_resource_data
            for a in (
                "name",
                "base_name",
                "extension",
                "size",
                "files_count",
                "dirs_count",
                "size_count",
            )
        )

        # walk and create resources proper
        # Create root resource first
        ##########################################################
        if not root_names:
            raise Exception("Unable to find root for codebase.")

        len_root_names = len(root_names)
        if len_root_names == 1:
            root_path = root_names.pop()
            needs_new_virtual_root = False
        elif len_root_names > 1 or multiple_inputs:
            root_path = "virtual_root"
            needs_new_virtual_root = True

        if needs_new_virtual_root:
            for fdata in files_data:
                rpath = fdata["path"]
                fdata["path"] = posixpath_join(root_path, rpath)
                fdata["path_segments"].insert(0, root_path)

        root_data = self._create_empty_resource_data()

        if self.has_single_resource:
            # single resource with one or more segments
            rdata = files_data[0]
            root_path = rdata["path"]
            rdata = remove_properties_and_basics(rdata)
            root_data.update(rdata)

        # Create root resource
        root = self._create_root_resource(
            name=file_name(root_path),
            path=root_path,
            is_file=root_is_file,
        )

        for name, value in root_data.items():
            # skip known properties
            if name not in KNOW_PROPS:
                setattr(root, name, value)

        if TRACE:
            logger_debug("VirtualCodebase.populate: root:", root)

        # TODO: report error if filtering the root with a paths?
        self.save_resource(root)

        if self.has_single_resource:
            if TRACE:
                logger_debug("VirtualCodebase.populate: with single resource.")
            return

        all_paths = None
        if self.paths:
            # build a set of all all paths and all their ancestors
            all_paths = set()
            for path in self.paths:
                all_paths.update(get_ancestor_paths(path, include_self=True))

        # Create other Resources from scan info

        # Note that we do not know the ordering there.
        # Therefore we sort in place by path segments
        files_data.sort(key=itemgetter("path_segments"))

        # We create directories that exist in the scan or create these that
        # exist only in paths
        duplicated_paths = set()
        last_path = None
        for fdata in files_data:
            path = fdata.get("path")

            # skip the ones we did not request
            if all_paths and path not in all_paths:
                continue

            # these are no longer needed
            path_segments = fdata.pop("path_segments")

            if not last_path:
                last_path = path
            elif last_path == path:
                duplicated_paths.add(path)
            else:
                last_path = path

            name = fdata.get("name", None) or None
            if not name:
                name = file_name(path)

            is_file = fdata.get("type", "file") == "file"

            parent = self._get_parent_directory(path_segments=path_segments)
            resource = self._get_or_create_resource(
                name=name,
                path=path,
                parent=parent,
                is_file=is_file,
            )
            # set data
            for name, value in fdata.items():
                # skip known properties
                if name not in KNOW_PROPS:
                    setattr(resource, name, value)

            self.save_resource(resource)

        if duplicated_paths:
            raise Exception(
                "Illegal combination of VirtualCode multiple inputs: "
                f"duplicated paths: {list(duplicated_paths)}",
            )

    def _get_parent_directory(self, path_segments):
        """
        Ensure that all directories in a sequence of path_segments exist
        and return the last one.
        """
        # TODO: handle single resource codebases
        resources_by_path = self.resources_by_path

        # remove the first which is the root, already created
        # and the last which is the current "child" segment
        path_segments = path_segments[1:-1]

        current = self.root
        for segment in path_segments:
            path = posixpath_join(current.path, segment)
            existing = resources_by_path.get(path)
            if not existing or existing == Codebase.CACHED_RESOURCE:
                existing = self._get_or_create_resource(
                    name=segment,
                    # build the path based on parent
                    path=path,
                    parent=current,
                    is_file=False,
                )
            current = existing
        return current

    def _create_root_resource(self, name, path, is_file):
        """
        Create and return the root Resource of this codebase.
        """
        # we cannot recreate a root if it exists!!
        if self.root:
            raise TypeError("Root resource already exists and cannot be recreated")

        path = clean_path(path)

        if TRACE:
            logger_debug(f"  VirtualCodebase._create_root_resource: {path!r} is_file: {is_file}")

        root = self.resource_class(
            name=name,
            location=None,
            # never cached
            cache_location=None,
            path=path,
            is_root=True,
            is_file=is_file,
        )

        self.resources_by_path[path] = root
        self.resources_count += 1
        self.root = root
        return root


KNOW_PROPS = set(["type", "base_name", "extension", "path", "name", "path_segments"])


def remove_properties_and_basics(resource_data):
    """
    Given a mapping of resource_data attributes to use as "kwargs", return a new
    mapping with the known properties removed.
    """
    return {k: v for k, v in resource_data.items() if k not in KNOW_PROPS}


def get_ancestor_paths(path, include_self=False):
    """
    Yield all subpaths from a POSIX path.

    For example::
    >>> path = 'foo/bar/baz'
    >>> results = list(get_ancestor_paths(path))
    >>> assert results == ['foo', 'foo/bar'], results
    >>> results = list(get_ancestor_paths(path, include_self=True))
    >>> assert results == ['foo', 'foo/bar', 'foo/bar/baz'], results
    >>> results = list(get_ancestor_paths('foo', include_self=False))
    >>> assert results == [], results
    """
    assert path
    segments = path.split("/")
    if not include_self:
        segments = segments[:-1]
    subpath = []
    for segment in segments:
        subpath.append(segment)
        yield "/".join(subpath)
