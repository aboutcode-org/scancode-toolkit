#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import ast
import base64
import copy
import json
import logging
import os
import re
import sys
import tempfile
import zipfile
from configparser import ConfigParser
from pathlib import Path
from typing import NamedTuple

import dparse2
# NOTE: we always want to use the external library rather than the built-in for now
import importlib_metadata
import packvers as packaging
import pip_requirements_parser
import pkginfo2
from commoncode import fileutils
from commoncode.fileutils import as_posixpath
from commoncode.resource import Resource
from packageurl import PackageURL
from packvers.specifiers import SpecifierSet
from packvers import markers
from packvers.requirements import Requirement
from packvers.utils import canonicalize_name

from packagedcode import models
from packagedcode.utils import build_description
from packagedcode.utils import yield_dependencies_from_package_data
from packagedcode.utils import yield_dependencies_from_package_resource

try:
    from zipfile import Path as ZipPath
except ImportError:
    from zipp import Path as ZipPath

"""
Detect and collect Python packages information.
"""
# TODO: add support for poetry and setup.cfg and metadata.json
# TODO: add support for pex, pyz, etc.
# TODO: Add missing ABOUT file for Pyserial code

TRACE = os.environ.get('SCANCODE_DEBUG_PACKAGE', False)


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))


class PythonEggPkgInfoFile(models.DatafileHandler):
    datasource_id = 'pypi_egg_pkginfo'
    default_package_type = 'pypi'
    default_primary_language = 'Python'
    path_patterns = ('*/EGG-INFO/PKG-INFO',)
    description = 'PyPI extracted egg PKG-INFO'
    documentation_url = 'https://peps.python.org/pep-0376/'

    @classmethod
    def parse(cls, location, purl_only=False):
        yield parse_metadata(
            location=location,
            datasource_id=cls.datasource_id,
            package_type=cls.default_package_type,
            purl_only=purl_only,
        )

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        # two levels up
        root = resource.parent(codebase).parent(codebase)
        if root:
            return models.DatafileHandler.assign_package_to_resources(package, root, codebase, package_adder)


class PythonEditableInstallationPkgInfoFile(models.DatafileHandler):
    datasource_id = 'pypi_editable_egg_pkginfo'
    default_package_type = 'pypi'
    default_primary_language = 'Python'
    path_patterns = ('*.egg-info/PKG-INFO',)
    description = 'PyPI editable local installation PKG-INFO'
    documentation_url = 'https://peps.python.org/pep-0376/'

    @classmethod
    def parse(cls, location, purl_only=False):
        yield parse_metadata(
            location=location,
            datasource_id=cls.datasource_id,
            package_type=cls.default_package_type,
            purl_only=purl_only,
        )

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        # only the parent for now... though it can be more complex
        return models.DatafileHandler.assign_package_to_parent_tree(package, resource, codebase, package_adder)


def create_package_from_package_data(package_data, datafile_path):
    package = models.Package.from_package_data(
        package_data=package_data,
        datafile_path=datafile_path,
    )
    package.populate_license_fields()
    return package


def is_egg_info_directory(resource):
    """
    Return True if `resource` is a Python .egg-info directory
    """
    return (
        isinstance(resource, Resource)
        and resource.path.endswith('.egg-info')
    )


class BaseExtractedPythonLayout(models.DatafileHandler):
    """
    Base class for development repos, sdist tarballs and other related extracted
    layourt for Python packages that can use and mix multiple datafiles.
    """

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        # a source distribution can have many manifests
        datafile_name_patterns = (
            'Pipfile.lock',
            'Pipfile',
        ) + PipRequirementsFileHandler.path_patterns

        # TODO: we want PKG-INFO first, then (setup.py, setup.cfg), then pyproject.toml for poetry
        # then we have the rest of the lock files (pipfile, pipfile.lock, etc.)

        package_resource = None
        if resource.name == 'PKG-INFO':
            # Initially use current Resource as `package_resource`.
            # We'll want update `package_resource` with the Resource of a
            # PKG-INFO file that's in an .egg-info Directory.
            package_resource = resource
            # We want to use the PKG-INFO file from an .egg-info directory, as
            # the package info collected from a *.egg_info/PKG-INFO file has
            # dependency information that a PKG-INFO from the root of a Python
            # project lacks.
            parent_resource = resource.parent(codebase)
            if not is_egg_info_directory(parent_resource):
                # If we are not in an .egg-info directory, we assume we are at
                # the root of a Python codebase and we want to find the
                # .egg_info dir
                egg_info_dir = None
                for sibling in resource.siblings(codebase):
                    if sibling.path.endswith('.egg-info'):
                        egg_info_dir = sibling
                        break

                # If we find the .egg_info dir, then we look for the PKG-INFO
                # file in it and use that as our package_resource
                if egg_info_dir:
                    for child in egg_info_dir.children(codebase):
                        if not child.name == 'PKG-INFO':
                            continue
                        package_resource = child
                        break
        elif resource.name in datafile_name_patterns:
            if resource.has_parent():
                siblings = resource.siblings(codebase)
                package_resource = [r for r in siblings if r.name == 'PKG-INFO']
                if package_resource:
                    package_resource = package_resource[0]

        package = None
        if package_resource:
            pkg_data = package_resource.package_data[0]
            pkg_data = models.PackageData.from_dict(pkg_data)
            if pkg_data.purl:
                package = create_package_from_package_data(
                    package_data=pkg_data,
                    datafile_path=package_resource.path
                )
                yield package

                package_adder(package.package_uid, package_resource, codebase)
                yield package_resource

                yield from yield_dependencies_from_package_data(
                    package_data=pkg_data,
                    datafile_path=package_resource.path,
                    package_uid=package.package_uid
                )
        else:
            setup_resources = []
            if resource.has_parent():
                siblings = resource.siblings(codebase)
                setup_resources = [
                    r for r in siblings
                    if r.name in ('setup.py', 'setup.cfg')
                    and r.package_data
                ]

                setup_package_data = [
                    (setup_resource, models.PackageData.from_dict(setup_resource.package_data[0]))
                    for setup_resource in setup_resources
                ]
                setup_package_data = sorted(setup_package_data, key=lambda s: bool(s[1].purl), reverse=True)
                for setup_resource, setup_pkg_data in setup_package_data:
                    if setup_pkg_data.purl:
                        if not package:
                            package = create_package_from_package_data(
                                package_data=setup_pkg_data,
                                datafile_path=setup_resource.path,
                            )
                            yield package
                            package_resource = setup_resource
                        else:
                            package.update(setup_pkg_data, setup_resource.path)
                if package:
                    for setup_resource, setup_pkg_data in setup_package_data:
                        package_adder(package.package_uid, setup_resource, codebase)
                        yield setup_resource

                        yield from yield_dependencies_from_package_data(
                            package_data=setup_pkg_data,
                            datafile_path=setup_resource.path,
                            package_uid=package.package_uid
                        )

        if package:
            package.populate_license_fields()
            package_uid = package.package_uid

            package_resource_parent = package_resource.parent(codebase)
            if is_egg_info_directory(package_resource_parent):
                root = package_resource_parent.parent(codebase)
            else:
                # We're assuming that our package resource is already at the
                # root
                root = package_resource_parent

            if root:
                for py_res in cls.walk_pypi(resource=root, codebase=codebase):
                    if py_res.is_dir:
                        continue
                    if package_uid and package_uid not in py_res.for_packages:
                        package_adder(package_uid, py_res, codebase)
                    yield py_res
            elif codebase.has_single_resource:
                if package_uid and package_uid not in package_resource.for_packages:
                    package_adder(package_uid, package_resource, codebase)

        else:
            package_uid = None

        if package_resource:
            for sibling in package_resource.siblings(codebase):
                if sibling and sibling.name in datafile_name_patterns:
                    yield from yield_dependencies_from_package_resource(
                        resource=sibling,
                        package_uid=package_uid
                    )

                    if package_uid and package_uid not in sibling.for_packages:
                        package_adder(package_uid, sibling, codebase)
                    yield sibling

    @classmethod
    def walk_pypi(cls, resource, codebase):
        """
        Walk the ``codebase`` Codebase top-down, breadth-first starting from the
        ``resource`` Resource.

        Skip the directory named "site-packages": this avoids
        reporting nested vendored packages as being part of their parent.
        Instead they will be reported on their own.
        """
        for child in resource.children(codebase):
            if child.name == 'site-packages':
                continue

            yield child

            if child.is_dir:
                for subchild in cls.walk_pypi(child, codebase):
                    yield subchild


class PythonSdistPkgInfoFile(BaseExtractedPythonLayout):
    datasource_id = 'pypi_sdist_pkginfo'
    default_package_type = 'pypi'
    default_primary_language = 'Python'
    path_patterns = ('*/PKG-INFO',)
    description = 'PyPI extracted sdist PKG-INFO'
    documentation_url = 'https://peps.python.org/pep-0314/'

    @classmethod
    def is_datafile(cls, location):
        return (
            super().is_datafile(location) and
            not PythonEggPkgInfoFile.is_datafile(location) and
            not PythonEditableInstallationPkgInfoFile.is_datafile(location)
        )

    @classmethod
    def parse(cls, location, purl_only=False):
        yield parse_metadata(
            location=location,
            datasource_id=cls.datasource_id,
            package_type=cls.default_package_type,
            purl_only=purl_only,
        )


class PythonInstalledWheelMetadataFile(models.DatafileHandler):
    datasource_id = 'pypi_wheel_metadata'
    path_patterns = ('*.dist-info/METADATA',)
    default_package_type = 'pypi'
    default_primary_language = 'Python'
    description = 'PyPI installed wheel METADATA'
    documentation_url = 'https://packaging.python.org/en/latest/specifications/core-metadata/'

    @classmethod
    def parse(cls, location, purl_only=False):
        yield parse_metadata(
            location=location,
            datasource_id=cls.datasource_id,
            package_type=cls.default_package_type,
            purl_only=purl_only,
        )

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        """
        Assign files to package for an installed wheel. This requires a bit
        of navigation around as the files can be in multiple places.
        """
        site_packages = resource.parent(codebase).parent(codebase)
        if not site_packages:
            return
        package_data = resource.package_data
        assert len(resource.package_data) == 1, (
            f'Unsupported Pypi METADATA wheel structure: {resource.path!r} '
            f'with multiple {package_data!r}'
        )

        package_data = models.PackageData.from_dict(package_data[0])

        package_uid = package.package_uid

        if package_uid:
            # save thyself!
            package_adder(package_uid, resource, codebase)

        # collect actual paths based on the file references
        for file_ref in package_data.file_references:
            path_ref = file_ref.path
            if path_ref.startswith('..'):
                # relative paths need special treatment
                # most of thense are references to bin ../../../bin/wheel
                cannot_resolve = False
                ref_resource = None
                while path_ref.startswith('..'):
                    _, _, path_ref = path_ref.partition('../')
                    ref_resource = site_packages.parent(codebase)
                    if not ref_resource:
                        cannot_resolve = True
                        break
                if cannot_resolve or not ref_resource:
                    # TODO:w e should log these kind of things
                    continue
                else:
                    if package_uid:
                        package_adder(package_uid, ref_resource, codebase)
            else:
                ref_resource = get_resource_for_path(
                    path=path_ref,
                    root=site_packages,
                    codebase=codebase,
                )
                if ref_resource and package_uid:
                    package_adder(package_uid, ref_resource, codebase)


def get_resource_for_path(path, root, codebase):
    """
    Return a resource in ``codebase`` that has a ``path`` relative to the
    ``root` Resource

    For example, say we start from this:
        path: this/is/that therefore segments [this, is, that]
        root: /usr/foo

    We would have these iterations:
    iteration1
        root = /usr/foo
        segments = [this, is, that]
        seg  this
        segments = [is, that]
        children = [/usr/foo/this]
        root = /usr/foo/this

    iteration2
        root = /usr/foo/this
        segments = [is, that]
        seg  is
        segments = [that]
        children = [/usr/foo/this/is]
        root = /usr/foo/this/is

    iteration3
        root = /usr/foo/this/is
        segments = [that]
        seg  that
        segments = []
        children = [/usr/foo/this/is/that]
        root = /usr/foo/this/is/that

    finally return root as /usr/foo/this/is/that
    """
    segments = path.strip('/').split('/')
    while segments:
        seg = segments.pop(0)
        children = [c for c in root.children(codebase) if c.name == seg]
        if len(children) != 1:
            return
        else:
            root = children[0]
    return root


# FIXME: Implement me
class PyprojectTomlHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'pypi_pyproject_toml'
    path_patterns = ('*pyproject.toml',)
    default_package_type = 'pypi'
    default_primary_language = 'Python'
    description = 'Python pyproject.toml'
    documentation_url = 'https://peps.python.org/pep-0621/'


META_DIR_SUFFIXES = '.dist-info', '.egg-info', 'EGG-INFO',


def parse_metadata(location, datasource_id, package_type, purl_only=False):
    """
    Return a PackageData object from a PKG-INFO or METADATA file at ``location``
    which is a path string or pathlib.Path-like object (including a possible zip
    file ZipPath for a wheel)

    Looks in neighboring files as needed when an installed layout is found.
    """
    path = location
    if not isinstance(location, (Path, ZipPath)):
        path = Path(location)

    # build from dir if we are an installed distro
    parent = path.parent
    if parent.name.endswith(META_DIR_SUFFIXES):
        path = parent

    dist = importlib_metadata.PathDistribution(path)

    meta = dist.metadata

    name = get_attribute(meta, 'Name')
    version = get_attribute(meta, 'Version')
    dependencies = get_dist_dependencies(dist)

    if purl_only:
        return models.PackageData(
            datasource_id=datasource_id,
            type=package_type,
            name=name,
            version=version,
            dependencies=dependencies,
        )
    else:
        urls, extra_data = get_urls(metainfo=meta, name=name, version=version)
        file_references = list(get_file_references(dist))
        return models.PackageData(
            datasource_id=datasource_id,
            type=package_type,
            primary_language='Python',
            name=name,
            version=version,
            dependencies=dependencies,
            extracted_license_statement=get_declared_license(meta),
            description=get_description(metainfo=meta, location=str(location)),
            keywords=get_keywords(meta),
            parties=get_parties(meta),
            file_references=file_references,
            extra_data=extra_data,
            **urls,
        )


def urlsafe_b64decode(data):
    """
    urlsafe_b64decode without padding
    SPDX-License-Identifier: MIT
    Copyright (c) 2012-2014 Daniel Holth <dholth@fastmail.fm> and contributors.
    From: https://github.com/pypa/wheel/blob/66208910ab51f4008b034ef4833acfdc920f7606/src/wheel/util.py#L23
    """
    pad = b'=' * (4 - (len(data) & 3))
    return base64.urlsafe_b64decode(data.encode('ASCII') + pad)


def get_file_references(dist):
    """
    Yield FileReference found in a ``dist`` importlib_metadata.Distribution.
    """
    if not dist.files:
        return

    for filepath in dist.files or []:
        # FIXME: the path is relative to the "site-packages" directory or the
        # root of a wheel but this should be a scan path
        ref = models.FileReference(
            path=as_posixpath(str(filepath)),
            size=filepath.size,
        )

        filehash = filepath.hash
        if filehash:
            algo = filehash.mode
            value = filehash.value
            if algo in ('sha256', 'sha512'):
                # convert back to hex as this is a base64 without padding otherwise
                value = urlsafe_b64decode(value).hex()
            setattr(ref, algo, value)
        yield ref


class PypiWheelHandler(models.DatafileHandler):
    datasource_id = 'pypi_wheel'
    path_patterns = ('*.whl',)
    filetypes = ('zip archive',)
    default_package_type = 'pypi'
    default_primary_language = 'Python'
    description = 'PyPI wheel'
    documentation_url = 'https://peps.python.org/pep-0427/'

    @classmethod
    def parse(cls, location, purl_only=False):
        with zipfile.ZipFile(location) as zf:
            for path in ZipPath(zf).iterdir():
                if not path.name.endswith(META_DIR_SUFFIXES):
                    continue
                for metapath in path.iterdir():
                    if not metapath.name.endswith('METADATA'):
                        continue

                    yield parse_metadata(
                        location=metapath,
                        datasource_id=cls.datasource_id,
                        package_type=cls.default_package_type,
                        purl_only=purl_only,
                    )


class PypiEggHandler(models.DatafileHandler):
    datasource_id = 'pypi_egg'
    path_patterns = ('*.egg',)
    filetypes = ('zip archive',)
    default_package_type = 'pypi'
    default_primary_language = 'Python'
    description = 'PyPI egg'
    documentation_url = 'https://web.archive.org/web/20210604075235/http://peak.telecommunity.com/DevCenter/PythonEggs'

    @classmethod
    def parse(cls, location, purl_only=False):
        with zipfile.ZipFile(location) as zf:
            for path in ZipPath(zf).iterdir():
                if not path.name.endswith(META_DIR_SUFFIXES):
                    continue

                for metapath in path.iterdir():
                    if not metapath.name.endswith('PKG-INFO'):
                        continue

                    yield parse_metadata(
                        location=metapath,
                        datasource_id=cls.datasource_id,
                        package_type=cls.default_package_type,
                        purl_only=purl_only,
                    )


class PypiSdistArchiveHandler(models.DatafileHandler):
    datasource_id = 'pypi_sdist'
    path_patterns = ('*.tar.gz', '*.tar.bz2', '*.zip',)
    default_package_type = 'pypi'
    default_primary_language = 'Python'
    description = 'Python source distribution'
    documentation_url = 'https://peps.python.org/pep-0643/'

    @classmethod
    def is_datafile(cls, location, filetypes=tuple()):
        if super().is_datafile(location, filetypes=filetypes):
            # TODO: there is a structure to an sdists name: aboutcode-toolkit-7.0.0.tar.gz
            # TODO: there is more to it than this... based on actual listing of files inside
            return True

    @classmethod
    def parse(cls, location, purl_only=False):
        # FIXME: add dependencies

        try:
            sdist = pkginfo2.SDist(location)
        except ValueError:
            return

        name = sdist.name
        version = sdist.version
        urls, extra_data = get_urls(metainfo=sdist, name=name, version=version)

        if purl_only:
            yield models.PackageData(
                datasource_id=cls.datasource_id,
                type=cls.default_package_type,
                name=name,
                version=version,
            )
        else:
            yield models.PackageData(
                datasource_id=cls.datasource_id,
                type=cls.default_package_type,
                primary_language=cls.default_primary_language,
                name=name,
                version=version,
                description=get_description(sdist, location=location),
                extracted_license_statement=get_declared_license(sdist),
                keywords=get_keywords(sdist),
                parties=get_parties(sdist),
                extra_data=extra_data,
                **urls,
            )


class PythonSetupPyHandler(BaseExtractedPythonLayout):
    datasource_id = 'pypi_setup_py'
    path_patterns = ('*setup.py',)
    default_package_type = 'pypi'
    default_primary_language = 'Python'
    description = 'Python setup.py'
    documentation_url = 'https://docs.python.org/3/distutils/setupscript.html'

    @classmethod
    def parse(cls, location, purl_only=False):
        setup_args = get_setup_py_args(location)

        # it may be legit to have a name-less package?
        # in anycase we do not want to fail because of that
        name = setup_args.get('name')
        version = setup_args.get('version')
        if not version:
            # search for possible dunder versions here and elsewhere
            version = detect_version_attribute(location)

        dependencies = get_setup_py_dependencies(setup_args)

        if purl_only:
            yield models.PackageData(
                datasource_id=cls.datasource_id,
                type=cls.default_package_type,
                name=name,
                version=version,
                dependencies=dependencies,
            )
        else:
            urls, extra_data = get_urls(metainfo=setup_args, name=name, version=version)
            python_requires = get_setup_py_python_requires(setup_args)
            extra_data.update(python_requires)

            yield models.PackageData(
                datasource_id=cls.datasource_id,
                type=cls.default_package_type,
                primary_language=cls.default_primary_language,
                name=name,
                version=version,
                description=get_description(setup_args),
                parties=get_setup_parties(setup_args),
                extracted_license_statement=get_declared_license(setup_args),
                dependencies=dependencies,
                keywords=get_keywords(setup_args),
                extra_data=extra_data,
                **urls,
            )


class ResolvedPurl(NamedTuple):
    """
    A resolved PURL
    """
    purl: PackageURL
    is_resolved: bool


class BaseDependencyFileHandler(models.DatafileHandler):
    """
    Base class for a dependency files parsed with the same library
    """

    @classmethod
    def parse(cls, location, purl_only=False):
        file_name = fileutils.file_name(location)

        dependency_type = get_dparse2_supported_file_name(file_name)
        if not dependency_type:
            return

        dependencies = parse_with_dparse2(
            location=location,
            file_name=dependency_type,
        )
        if purl_only:
            yield models.PackageData(
                datasource_id=cls.datasource_id,
                type=cls.default_package_type,
                dependencies=dependencies,
            )
        else:
            yield models.PackageData(
                datasource_id=cls.datasource_id,
                type=cls.default_package_type,
                primary_language=cls.default_primary_language,
                dependencies=dependencies,
            )


class SetupCfgHandler(BaseExtractedPythonLayout):
    datasource_id = 'pypi_setup_cfg'
    path_patterns = ('*setup.cfg',)
    default_package_type = 'pypi'
    default_primary_language = 'Python'
    description = 'Python setup.cfg'
    documentation_url = 'https://peps.python.org/pep-0390/'

    @classmethod
    def parse(cls, location, purl_only=False):

        metadata = {}
        parser = ConfigParser()
        dependent_packages = []
        with open(location) as f:
            parser.read_file(f)

        for section in parser.values():
            if section.name == 'options':
                scope_by_sub_section = {
                    "install_requires": "install",
                    "tests_require": "test",
                    "setup_requires": "setup",
                    "python_requires": "python",
                }
                for sub_section, scope in scope_by_sub_section.items():
                    if sub_section not in section:
                        continue
                    if scope != "python":
                        reqs = list(get_requirement_from_section(section=section, sub_section=sub_section))
                        dependent_packages.extend(cls.parse_reqs(reqs, scope))
                        continue
                    python_requires_specifier = section[sub_section]
                    purl = PackageURL(
                        type="generic",
                        name="python",
                    )
                    resolved_purl = get_resolved_purl(purl=purl, specifiers=SpecifierSet(python_requires_specifier))
                    dependent_packages.append(
                        models.DependentPackage(
                            purl=str(resolved_purl.purl),
                            scope=scope,
                            is_runtime=True,
                            is_optional=False,
                            is_resolved=resolved_purl.is_resolved,
                            extracted_requirement=f"python_requires{python_requires_specifier}",
                        )
                    )

            if section.name == "options.extras_require":
                for sub_section in section:
                    reqs = list(get_requirement_from_section(section=section, sub_section=sub_section))
                    dependent_packages.extend(cls.parse_reqs(reqs, sub_section))
            if section.name == 'metadata':
                options = (
                    'name',
                    'version',
                    'license',
                    'license_files',
                    'url',
                    'author',
                    'author_email',
                )
                for name in options:
                    content = section.get(name)
                    if not content:
                        continue
                    metadata[name] = content

        package = models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=metadata.get('name'),
            version=metadata.get('version'),
            dependencies=dependent_packages,
        )
        if purl_only:
            yield package
        else:
            parties = []
            author = metadata.get('author')
            if author:
                parties = [
                    models.Party(
                        type=models.party_person,
                        name=author,
                        role='author',
                        email=metadata.get('author_email'),
                    )
                ]

            extracted_license_statement = metadata.get('license')
            license_file_references = metadata.get('license_files')
            if license_file_references:
                if not extracted_license_statement:
                    extracted_license_statement = ''
                extracted_license_statement += f" license_files: {license_file_references}"

            yield models.PackageData(
                datasource_id=cls.datasource_id,
                type=cls.default_package_type,
                name=metadata.get('name'),
                version=metadata.get('version'),
                parties=parties,
                homepage_url=metadata.get('url'),
                primary_language=cls.default_primary_language,
                dependencies=dependent_packages,
                extracted_license_statement=extracted_license_statement,
            )

    @classmethod
    def parse_reqs(cls, reqs, scope):
        """
        Parse a list of requirements and return a list of dependencies
        """
        dependent_packages = []
        for req in reqs:
            req_parsed = packaging.requirements.Requirement(str(req))
            name = canonicalize_name(req_parsed.name)
            purl = PackageURL(type="pypi", name=name)
            specifiers = req_parsed.specifier._specs
            resolved_purl = get_resolved_purl(purl=purl, specifiers=specifiers)
            dependent_packages.append(
                        models.DependentPackage(
                        purl=str(resolved_purl.purl),
                        scope=scope,
                        is_runtime=True,
                        is_optional=False,
                        is_resolved=resolved_purl.is_resolved,
                        extracted_requirement=req
                    )
                )
        return dependent_packages


def get_resolved_purl(purl: PackageURL, specifiers: SpecifierSet):
    """
    Check if the purl is resolved and return a ResolvedPurl.
    If the purl is resolved, update its version to the pinned version
    """
    is_resolved = False
    if len(specifiers) == 1:
        specifier = list(specifiers)[0]
        if specifier.operator in ('==', '==='):
            is_resolved = True
            purl = purl._replace(version=specifier.version)
    return ResolvedPurl(
        purl=purl,
        is_resolved=is_resolved,
    )


class PipfileHandler(BaseDependencyFileHandler):
    datasource_id = 'pipfile'
    path_patterns = ('*Pipfile',)
    default_package_type = 'pypi'
    default_primary_language = 'Python'
    description = 'Pipfile'
    documentation_url = 'https://github.com/pypa/pipfile'


class PipfileLockHandler(BaseDependencyFileHandler):
    datasource_id = 'pipfile_lock'
    path_patterns = ('*Pipfile.lock',)
    default_package_type = 'pypi'
    default_primary_language = 'Python'
    description = 'Pipfile.lock'
    documentation_url = 'https://github.com/pypa/pipfile'

    @classmethod
    def parse(cls, location, purl_only=False):
        with open(location) as f:
            content = f.read()

        data = json.loads(content)

        sha256 = None
        if '_meta' in data:
            for name, meta in data['_meta'].items():
                if name == 'hash':
                    sha256 = meta.get('sha256')

        dependent_packages = parse_with_dparse2(
            location=location,
            file_name='Pipfile.lock',
        )

        package = models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            dependencies=dependent_packages,
        )
        if purl_only:
            yield package
        else:
            package.primary_language = cls.default_primary_language
            package.sha256 = sha256
            yield package


class PipRequirementsFileHandler(BaseDependencyFileHandler):
    datasource_id = 'pip_requirements'

    path_patterns = (
        '*requirement*.txt',
        '*requirement*.pip',
        '*requirement*.in',
        '*requires.txt',
        '*requirements/*.txt',
        '*requirements/*.pip',
        '*requirements/*.in',
        '*reqs.txt',
    )

    default_package_type = 'pypi'
    default_primary_language = 'Python'
    description = 'pip requirements file'
    documentation_url = 'https://pip.pypa.io/en/latest/reference/requirements-file-format/'

    @classmethod
    def parse(cls, location, purl_only=False):
        dependencies, extra_data = get_requirements_txt_dependencies(location=location)
        package = models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            dependencies=dependencies,
        )
        if purl_only:
            yield package
        else:
            package.primary_language = cls.default_primary_language
            package.extra_data = extra_data
            yield package

# TODO: enable nested load


def get_requirements_txt_dependencies(location, include_nested=False):
    """
    Return a two-tuple of (list of deps, mapping of extra data) list of
    DependentPackage found in a requirements file at ``location`` or tuple of
    ([], {})
    """
    req_file = pip_requirements_parser.RequirementsFile.from_file(
        filename=location,
        include_nested=include_nested,
    )
    if not req_file or not req_file.requirements:
        return [], {}

    # for now we ignore errors
    extra_data = {}
    for opt in req_file.options:
        for name, value in opt.options.items():
            if name not in extra_data:
                extra_data[name] = value
            else:
                if isinstance(value, list):
                    extra_data[name].extend(value)
                else:
                    extra_data[name] = value
    dependent_packages = []
    for req in req_file.requirements:

        if req.name:
            # will be None if not pinned
            version = req.get_pinned_version
            purl = PackageURL(type='pypi', name=canonicalize_name(req.name), version=version)

        else:
            # this is odd, but this can be null
            purl = None

        purl = purl and purl.to_string() or None
        requirement = req.dumps()

        if location.endswith(
            (
                'dev.txt',
                'test.txt',
                'tests.txt',
            )
        ):
            scope = 'development'
            is_runtime = False
            is_optional = True
        else:
            scope = 'install'
            is_runtime = True
            is_optional = False

        dependent_packages.append(
            models.DependentPackage(
                purl=purl,
                scope=scope,
                is_runtime=is_runtime,
                is_optional=is_optional,
                is_resolved=req.is_pinned or False,
                extracted_requirement=requirement,
                extra_data=dict(
                    is_editable=req.is_editable,
                    link=req.link and req.link.url or None,
                    hash_options=req.hash_options or [],
                    is_constraint=req.is_constraint,
                    is_archive=req.is_archive,
                    is_wheel=req.is_wheel,
                    is_url=req.is_url,
                    is_vcs_url=req.is_vcs_url,
                    is_name_at_url=req.is_name_at_url,
                    is_local_path=req.is_local_path,
                ),
            )
        )

    return dependent_packages, extra_data


def can_process_dependent_package(dep: models.DependentPackage):
    """
    Return True if we can process the dependent package
    typically anything that's not a plain standard specifier
    can not be processed such as an editable requirement
    """
    # copying dep.extra_data to avoid mutating the original
    requirement_flags = copy.copy(dep.extra_data or {})
    requirement_flags.pop("hash_options", None)
    if not requirement_flags:
        return True
    # we can not process the requirement if it has any flag set
    # because this means it is not a standard specifier
    # but rather some pip specific option of sorts
    return not any(requirement_flags.values())


def get_attribute(metainfo, name, multiple=False):
    """
    Return the value for the attribute ``name`` in the ``metainfo`` mapping,
    pkginfo object or email object. Treat the value as a list of multiple values
    if ``multiple`` is True. Return None or an empty list (if multiple is True)
    if no value is found or the attribute ``name`` does not exist.
    Ignore case (but returns the value for the original case if present.
    """

    # note: the approach for this function is to be used with the various
    # metainfo objects and dictionsaries we use that can be a
    # pkginfo.Distribution, an email.message.EmailMessage or a dict.

    # Because of that, the key can be obtained as a plain named attribute,
    # either as-is or lowercased (and with dash replaced by dunder) or we
    # can use a get on dicts of emails.

    def attr_getter(_aname, default):
        _aname = _aname.replace('-', '_')
        return (
            getattr(metainfo, _aname, default)
            or getattr(metainfo, _aname.lower(), default)
        )

    def item_getter(_iname, getter, default):
        getter = getattr(metainfo, getter, None)
        if getter:
            return getter(_iname, default) or getter(_iname.lower(), default)
        return default

    if multiple:
        return (
            attr_getter(name, [])
            or item_getter(name, 'get_all', [])
            or item_getter(name, 'get', [])
            or []
        )
    else:
        return (
            attr_getter(name, None)
            or item_getter(name, 'get', None)
            or None
        )


def get_description(metainfo, location=None):
    """
    Return a list of keywords found in a ``metainfo`` object or mapping.
    """
    description = None
    # newer metadata versions use the payload for the description
    if hasattr(metainfo, 'get_payload'):
        description = metainfo.get_payload()
    description = description and description.strip() or None
    if not description:
        # legacymetadata versions use the Description for the description
        description = get_attribute(metainfo, 'Description')
        if not description and location:
            # older metadata versions can use a DESCRIPTION.rst file
            description = get_legacy_description(location=fileutils.parent_directory(location))

    summary = get_attribute(metainfo, 'Summary')
    description = clean_description(description)
    return build_description(summary, description)


def clean_description(description):
    """
    Return a cleaned description text, removing extra leading whitespaces if
    needed. Some metadata formats padd each description line with 8 spaces. Some
    do not. We check first and cleanup if needed.
    """
    # TODO: verify what is the impact of Description-Content-Type: if any
    description = description or ''
    description = description.strip()
    lines = description.splitlines(False)

    space_padding = ' ' * 8

    # we need cleaning if any of the first two lines starts with 8 spaces
    need_cleaning = any(l.startswith(space_padding) for l in lines[:2])
    if not need_cleaning:
        return description

    cleaned_lines = [
        line[8:] if line.startswith(space_padding) else line
        for line in lines
    ]

    return '\n'.join(cleaned_lines)


def get_legacy_description(location):
    """
    Return the text of a legacy DESCRIPTION.rst file.
    """
    location = os.path.join(location, 'DESCRIPTION.rst')
    if os.path.exists(location):
        with open(location) as i:
            return i.read()


def get_declared_license(metainfo):
    """
    Return a mapping of declared license information found in a ``metainfo``
    object or mapping.
    """
    declared_license = {}
    # TODO: We should make the declared license as it is, this should be
    # updated in scancode to parse a pure string
    lic = get_attribute(metainfo, 'License')
    if lic and not lic == 'UNKNOWN':
        declared_license['license'] = lic

    license_classifiers, _ = get_classifiers(metainfo)
    if license_classifiers:
        declared_license['classifiers'] = license_classifiers

    if not declared_license:
        declared_license = None

    return declared_license


def get_classifiers(metainfo):
    """
    Return a two tuple of lists of (license_classifiers, other_classifiers)
    found in a ``metainfo`` object or mapping.
    """

    classifiers = (
        get_attribute(metainfo, 'Classifier', multiple=True)
        or get_attribute(metainfo, 'Classifiers', multiple=True)
    )
    if not classifiers:
        return [], []

    license_classifiers = []
    other_classifiers = []
    for classifier in classifiers:
        if classifier:
            if classifier.startswith('License'):
                license_classifiers.append(classifier)
            else:
                other_classifiers.append(classifier)
    return license_classifiers, other_classifiers


def get_keywords(metainfo):
    """
    Return a list of keywords found in a ``metainfo`` object or mapping.
    """
    keywords = []
    kws = get_attribute(metainfo, 'Keywords') or []
    if kws:
        if isinstance(kws, str):
            kws = kws.split(',')
        elif isinstance(kws, (list, tuple)):
            pass
        else:
            kws = [repr(kws)]
        kws = [k.strip() for k in kws if k and k.strip()]
        keywords.extend(kws)

    # we are calling this again and ignoring licenses
    _, other_classifiers = get_classifiers(metainfo)
    keywords.extend(other_classifiers)
    return keywords


def get_parties(
    metainfo,
    author_key='Author',
    author_email_key='Author-email',
    maintainer_key='Maintainer',
    maintainer_email_key='Maintainer-email',

):
    """
    Return a list of parties found in a ``metainfo`` object or mapping.
    Uses the provided keys with a default to key names used in METADATA.
    setup.py and setup.cfg use lower case valid Python identifiers instead.
    """
    parties = []

    author = get_attribute(metainfo, author_key)

    author_email = get_attribute(metainfo, author_email_key)
    if author or author_email:
        parties.append(models.Party(
            type=models.party_person,
            name=author or None,
            role='author',
            email=author_email or None,
        ))

    maintainer = get_attribute(metainfo, maintainer_key)
    maintainer_email = get_attribute(metainfo, maintainer_email_key)
    if maintainer or maintainer_email:
        parties.append(models.Party(
            type=models.party_person,
            name=maintainer or None,
            role='maintainer',
            email=maintainer_email or None,
        ))

    return parties


def get_setup_parties(setup_kwargs):
    """
    Return a list of parties found in a ``setup_kwargs`` mapping of data found
    in setup.py or setup.cfg.
    """
    return get_parties(
        metainfo=setup_kwargs,
        author_key='author',
        author_email_key='author_email',
        maintainer_key='maintainer',
        maintainer_email_key='maintainer_email',
    )


def get_setup_py_python_requires(setup_args):
    """
    Return a mapping of {python_requires: value} or an empty mapping found in a
    ``setup_args`` mapping of setup.py arguments.
    """
    python_requires = setup_args.get('python_requires')
    if python_requires:
        return dict(python_requires=python_requires)
    else:
        return {}


def get_setup_py_dependencies(setup_args):
    """
    Return a list of DependentPackage found in a ``setup_args`` mapping of
    setup.py arguments or an empty list.
    """
    dependencies = []

    install_requires = setup_args.get('install_requires')
    dependencies.extend(get_requires_dependencies(install_requires, default_scope='install'))

    tests_requires = setup_args.get('tests_requires')
    dependencies.extend(
        get_requires_dependencies(tests_requires, default_scope='tests')
    )

    setup_requires = setup_args.get('setup_requires')
    dependencies.extend(
        get_requires_dependencies(setup_requires, default_scope='setup')
    )

    extras_require = setup_args.get('extras_require') or {}
    for scope, requires in extras_require.items():
        dependencies.extend(
            get_requires_dependencies(requires, default_scope=scope)
        )

    return dependencies


def is_simple_requires(requires):
    """
    Return True if ``requires`` is a sequence of strings.
    """
    return (
        requires
        and isinstance(requires, list)
        and all(isinstance(i, str) for i in requires)
    )


def get_dist_dependencies(dist):
    """
    Return a list of DependentPackage found in a ``dist`` Distribution object or
    an empty list.
    """
    # we treat extras as scopes
    # TODO: use these for verification?
    scopes = dist.metadata.get_all('Provides-Extra') or []
    return get_requires_dependencies(requires=dist.requires)


def get_requires_dependencies(requires, default_scope='install'):
    """
    Return a list of DependentPackage found in a ``requires`` list of
    requirement strings or an empty list.
    """
    if not is_simple_requires(requires):
        # FIXME: when does this happen? should we log this?
        return []
    dependent_packages = []
    for req in (requires or []):
        req = Requirement(req)
        name = canonicalize_name(req.name)
        is_resolved = False
        purl = PackageURL(type='pypi', name=name)
        # note: packaging.requirements.Requirement.specifier is a
        # packaging.specifiers.SpecifierSet object and a SpecifierSet._specs is
        # a set of either: packaging.specifiers.Specifier or
        # packaging.specifiers.LegacySpecifier and each of these have a
        # .operator and .version property
        # a packaging.specifiers.SpecifierSet
        specifiers_set = req.specifier  # a list of packaging.specifiers.Specifier
        specifiers = specifiers_set._specs
        requirement = None
        if specifiers:
            # SpecifierSet stringifies to comma-separated sorted Specifiers
            requirement = str(specifiers_set)
            # are we pinned e.g. resolved? this is true if we have a single
            # equality specifier
            if len(specifiers) == 1:
                specifier = list(specifiers)[0]
                if specifier.operator in ('==', '==='):
                    is_resolved = True
                    purl = purl._replace(version=specifier.version)

        # we use the extra as scope if available
        extra = get_extra(req.marker)
        scope = extra or default_scope

        dependent_packages.append(
            models.DependentPackage(
                purl=purl.to_string(),
                scope=scope,
                is_runtime=True,
                is_optional=True if bool(extra) else False,
                is_resolved=is_resolved,
                extracted_requirement=str(req),
        ))

    return dependent_packages


def get_extra(marker):
    """
    Return the "extra" value of a ``marker`` requirement Marker or None.
    """
    if not marker or not isinstance(marker, markers.Marker):
        return

    marks = getattr(marker, '_markers', [])

    for mark in marks:
        # filter for variable(extra) == value tuples of (Variable, Op, Value)
        if not isinstance(mark, tuple) and not len(mark) == 3:
            continue

        variable, operator, value = mark

        if (
            isinstance(variable, markers.Variable)
            and variable.value == 'extra'
            and isinstance(operator, markers.Op)
            and operator.value == '=='
            and isinstance(value, markers.Value)
        ):
            return value.value


def get_dparse2_supported_file_name(file_name):
    """
    Return the file_name if this is supported or None given a `file_name`
    string.
    """
    # this is kludgy but the upstream data structure and API needs this
    dfile_names = (
        'Pipfile.lock',
        'Pipfile',
        'conda.yml',
    )

    for dfile_name in dfile_names:
        if file_name.endswith(dfile_name):
            return file_name


def parse_with_dparse2(location, file_name=None):
    """
    Return a list of DependentPackage built from a dparse2-supported dependency
    manifest such as Conda manifest or Pipfile.lock files, or return an empty
    list.
    """
    with open(location) as f:
        content = f.read()

    dep_file = dparse2.parse(content, file_name=file_name)
    if not dep_file:
        return []

    dependent_packages = []

    for dependency in dep_file.dependencies:
        requirement = dependency.name
        is_resolved = False
        purl = PackageURL(type='pypi', name=dependency.name)

        # note: dparse2.dependencies.Dependency.specs comes from
        # packaging.requirements.Requirement.specifier
        # which in turn is a packaging.specifiers.SpecifierSet objects
        # and a SpecifierSet._specs is a set of either:
        # packaging.specifiers.Specifier or packaging.specifiers.LegacySpecifier
        # and each of these have a .operator and .version property

        # a packaging.specifiers.SpecifierSet
        specifiers_set = dependency.specs
        # a list of packaging.specifiers.Specifier
        specifiers = specifiers_set._specs

        if specifiers:
            # SpecifierSet stringifies to comma-separated sorted Specifiers
            requirement = str(specifiers_set)
            # are we pinned e.g. resolved?
            if len(specifiers) == 1:
                specifier = list(specifiers)[0]
                if specifier.operator in ('==', '==='):
                    is_resolved = True
                    purl = purl._replace(version=specifier.version)

        dependent_packages.append(
            models.DependentPackage(
                purl=purl.to_string(),
                # are we always this scope? what if we have requirements-dev.txt?
                scope='install',
                is_runtime=True,
                is_optional=False,
                is_resolved=is_resolved,
                extracted_requirement=requirement
            )
        )

    return dependent_packages


def is_setup_call(statement):
    """
    Return if the AST ``statement`` is a call to the setup() function.
    """
    return (
        isinstance(statement, (ast.Expr, ast.Call, ast.Assign))
        and isinstance(statement.value, ast.Call)
        and (
            # we look for setup and main as this is used sometimes instead of setup()
            (
                isinstance(statement.value.func, ast.Name)
                and statement.value.func.id in ('setup', 'main')
            )
            or
            # we also look for setuptools.setup when used instead of setup()
            (
                isinstance(statement.value.func, ast.Attribute)
                and statement.value.func.attr == 'setup'
                and isinstance(statement.value.func.value, ast.Name)
                and statement.value.func.value.id == 'setuptools'
            )
        )
    )


def get_setup_py_args_legacy(location, include_not_parsable=False):
    """
    Return a mapping of arguments passed to a setup.py setup() function. Also
    include not parsable identifiers values such as variable name and attribute
    references if ``include_not_parsable`` is True
    """
    with open(location) as inp:
        setup_text = inp.read()

    setup_args = {}

    # Parse setup.py file and traverse the AST
    tree = ast.parse(setup_text)
    for statement in tree.body:
        # We only care about function calls or assignments to functions named
        # `setup` or `main`

        # TODO: also collect top level variables assigned later as arguments values
        if not is_setup_call(statement):
            continue

        # Process the arguments to the setup function
        for kw in getattr(statement.value, 'keywords', []):
            arg_name = kw.arg
            arg_value = kw.value

            # FIXME: use a recursive function to extract structured data

            if isinstance(arg_value, (ast.List, ast.Tuple, ast.Set,)):
                # We collect the elements of a list if the element
                # and tag function calls
                val = [
                    elt.s for elt in arg_value.elts
                    if not isinstance(elt, ast.Call)
                ]
                setup_args[arg_name] = val

            elif isinstance(arg_value, ast.Dict):
                # we only collect simple name/value and name/[values] constructs
                keys = [elt.value for elt in arg_value.keys]
                values = []
                for val in arg_value.values:

                    if isinstance(val, (ast.List, ast.Tuple, ast.Set,)):
                        val = [
                            elt.s for elt in val.elts
                            if not isinstance(elt, ast.Call)
                        ]
                        values.append(val)

                    elif isinstance(val, (ast.Str, ast.Constant,)):
                        values.append(val.s)

                    else:
                        if include_not_parsable:
                            if isinstance(val, ast.Attribute):
                                values.append(val.attr)

                            elif isinstance(val, ast.Name):
                                values.append(val.id)

                            elif not isinstance(val, (ast.Call, ast.ListComp, ast.Subscript)):
                                # we used to consider only isinstance(val, ast.Str):
                                # instead use literal_eval and ignore failures, skipping
                                # only function calls this way we can get more things such
                                # as boolean and numbers
                                try:
                                    values.append(ast.literal_eval(val.value))
                                except Exception as e:
                                    if TRACE:
                                        logger_debug('get_setup_py_args: failed:', e)
                                    values.append(str(val.value))

                mapping = dict(zip(keys, values))
                setup_args[arg_name] = mapping

            elif isinstance(arg_value, (ast.Str, ast.Constant,)):
                setup_args[arg_name] = arg_value.s
            else:
                if include_not_parsable:
                    if isinstance(arg_value, ast.Attribute):
                        setup_args[arg_name] = arg_value.attr

                    elif isinstance(arg_value, ast.Name):
                        if arg_name:
                            setup_args[arg_name] = arg_value.id

                    elif not isinstance(arg_value, (ast.Call, ast.ListComp, ast.Subscript,)):
                        # we used to consider only isinstance(kw.value, ast.Str):
                        # instead use literal_eval and ignore failures, skipping only
                        # function calls this way we can get more things such as boolean
                        # and numbers
                        try:
                            setup_args[arg_name] = ast.literal_eval(arg_value)
                        except Exception as e:
                            if TRACE:
                                logger_debug('get_setup_py_args: failed:', e)
                            setup_args[arg_name] = str(arg_value)

            # TODO:  an expression like a call to version=get_version or version__version__

    return setup_args


def get_setup_py_args(location, include_not_parsable=False):
    """
    Return a mapping of arguments passed to a setup.py setup() function. Also
    include not parsable identifiers values such as variable name and attribute
    references if ``include_not_parsable`` is True
    """
    from packagedcode.pypi_setup_py import parse_setup_py
    return parse_setup_py(location)


def get_pypi_urls(name, version, **kwargs):
    """
    Return a mapping of computed Pypi URLs for this package
    """
    api_data_url = None
    if name and version:
        api_data_url = f'https://pypi.org/pypi/{name}/{version}/json'
    else:
        api_data_url = name and f'https://pypi.org/pypi/{name}/json'

    repository_download_url = (
        name
        and version
        and f'https://pypi.org/packages/source/{name[0]}/{name}/{name}-{version}.tar.gz'
    )

    repository_homepage_url = name and f'https://pypi.org/project/{name}'

    return dict(
        repository_homepage_url=repository_homepage_url,
        repository_download_url=repository_download_url,
        api_data_url=api_data_url,
    )


def get_urls(metainfo, name, version):
    """
    Return a mapping of standard URLs and a mapping of extra-data URls for URLs
    of this package:
    - standard URLs are for URL attributes known in PackageData
    - extra_data for other URLs (possibly updating extra_data if provided).
    """
    # Misc URLs to possibly track
    # Project-URL: Release notes
    # Project-URL: Release Notes
    # Project-URL: Changelog
    # Project-URL: Changes
    #
    # Project-URL: Further Documentation
    # Project-URL: Packaging tutorial
    # Project-URL: Docs
    # Project-URL: Docs: RTD
    # Project-URL: Documentation
    # Project-URL: Documentation (dev)
    # Project-URL: Wiki
    #
    # Project-URL: Chat
    # Project-URL: Chat: Gitter
    # Project-URL: Mailing lists
    # Project-URL: Twitter
    #
    # Project-URL: Travis CI
    # Project-URL: Coverage: codecov
    # Project-URL: CI
    # Project-URL: CI: Azure Pipelines
    # Project-URL: CI: Shippable
    #
    # Project-URL: Tidelift
    # Project-URL: Code of Conduct
    # Project-URL: Donate
    # Project-URL: Funding
    # Project-URL: Ko-fi
    # Project-URL: Twine documentation
    # Project-URL: Twine source
    # Project-URL: Say Thanks!

    extra_data = {}
    urls = get_pypi_urls(name, version)

    def add_url(_url, _utype=None, _attribute=None):
        """
        Add ``_url`` to ``urls`` as _``_attribute`` or to ``extra_data`` as
        ``_utype`` if already defined or no ``_attribute`` is provided.
        """
        if _url:
            if _attribute and _attribute not in urls:
                urls[_attribute] = _url
            elif _utype:
                extra_data[_utype] = _url

    # get first as this is the most common one
    homepage_url = (
        get_attribute(metainfo, 'Home-page')
        or get_attribute(metainfo, 'url')
        or get_attribute(metainfo, 'home')
    )
    add_url(homepage_url, _attribute='homepage_url')

    project_urls = (
        get_attribute(metainfo, 'Project-URL', multiple=True)
        or get_attribute(metainfo, 'project_urls')
        or []
    )

    if isinstance(project_urls, list):
        # these come from METADATA and we convert them back to a mapping
        project_urls = [url.partition(', ') for url in project_urls]
        project_urls = {
            utype.strip(): uvalue.strip()
            for utype, _, uvalue in project_urls
        }
    if isinstance(project_urls, dict):
        for utype, url in project_urls.items():
            utypel = utype.lower()
            if utypel in (
                'tracker',
                'bug reports',
                'github: issues',
                'bug tracker',
                'issues',
                'issue tracker',
            ):
                add_url(url, _utype=utype, _attribute='bug_tracking_url')

            elif utypel in (
                'source',
                'source code',
                'code',
            ):
                add_url(url, _utype=utype, _attribute='code_view_url')

            elif utypel in ('github', 'gitlab', 'github: repo', 'repository'):
                add_url(url, _utype=utype, _attribute='vcs_url')

            elif utypel in ('website', 'homepage', 'home',):
                add_url(url, _utype=utype, _attribute='homepage_url')

            else:
                add_url(url, _utype=utype)

    # FIXME: this may not be the actual correct package download URL, so we keep this as an extra URL
    download_url = get_attribute(metainfo, 'Download-URL')
    if not download_url:
        download_url = get_attribute(metainfo, 'download_url')
    add_url(download_url, _utype='Download-URL')

    return urls, extra_data


def find_pattern(location, pattern):
    """
    Search the file at `location` for a patern regex on a single line and return
    this or None if not found. Reads the supplied location as text without
    importing it.

    Code inspired and heavily modified from:
    https://github.com/pyserial/pyserial/blob/d867871e6aa333014a77498b4ac96fdd1d3bf1d8/setup.py#L34
    SPDX-License-Identifier: BSD-3-Clause
    (C) 2001-2020 Chris Liechti <cliechti@gmx.net>
    """
    with open(location) as fp:
        content = fp.read()

    match = re.search(pattern, content)
    if match:
        return match.group(1).strip()


def find_dunder_version(location):
    """
    Return a "dunder" __version__ string or None from searching the module file
    at `location`.

    Code inspired and heavily modified from:
    https://github.com/pyserial/pyserial/blob/d867871e6aa333014a77498b4ac96fdd1d3bf1d8/setup.py#L34
    SPDX-License-Identifier: BSD-3-Clause
    (C) 2001-2020 Chris Liechti <cliechti@gmx.net>
    """
    pattern = re.compile(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", re.MULTILINE)
    match = find_pattern(location, pattern)
    if TRACE: logger_debug('find_dunder_version:', 'location:', location, 'match:', match)
    return match


def find_plain_version(location):
    """
    Return a plain version attribute string or None from searching the module
    file at `location`.
    """
    pattern = re.compile(r"^version\s*=\s*['\"]([^'\"]*)['\"]", re.MULTILINE)
    match = find_pattern(location, pattern)
    if TRACE: logger_debug('find_plain_version:', 'location:', location, 'match:', match)
    return match


def find_setup_py_dunder_version(location):
    """
    Return a "dunder" __version__ expression string used as a setup(version)
    argument or None from searching the setup.py file at `location`.

    For instance:
        setup(
            version=six.__version__,
        ...
    would return six.__version__

    Code inspired and heavily modified from:
    https://github.com/pyserial/pyserial/blob/d867871e6aa333014a77498b4ac96fdd1d3bf1d8/setup.py#L34
    SPDX-License-Identifier: BSD-3-Clause
    (C) 2001-2020 Chris Liechti <cliechti@gmx.net>
    """
    pattern = re.compile(r"^\s*version\s*=\s*(.*__version__)", re.MULTILINE)
    match = find_pattern(location, pattern)
    if TRACE:
        logger_debug('find_setup_py_dunder_version:', 'location:', location, 'match:', match)
    return match


def detect_version_attribute(setup_location):
    """
    Return a detected version from a setup.py file at `location` if used as in
    a version argument of the setup() function.
    Also search for neighbor files for __version__ and common patterns.
    """
    # search for possible dunder versions here and elsewhere
    setup_version_arg = find_setup_py_dunder_version(setup_location)
    setup_py__version = find_dunder_version(setup_location)
    if TRACE:
        logger_debug('    detect_version_attribute():', 'setup_location:', setup_location)
        logger_debug('      find_setup_py_dunder_version(): setup_version_arg:', repr(setup_version_arg),)
        logger_debug('      find_dunder_version(): setup_py__version:', repr(setup_py__version),)

    if setup_version_arg == '__version__' and setup_py__version:
        version = setup_py__version or None
        if TRACE:
            logger_debug(
                '     detect_dunder_version:',
                "setup_version_arg == '__version__' and setup_py__version:", version)
        return version

    # here we have a more complex __version__ location
    # we start by adding the possible paths and file name
    # and we look at these in sequence

    if setup_version_arg and '.' in setup_version_arg:
        segments = setup_version_arg.split('.')[:-1]
    else:
        segments = []

    if TRACE:
        logger_debug('    detect_version_attribute():', 'segments:', segments)

    special_names = (
        '__init__.py',
        '__main__.py',
        '__version__.py',
        '__about__.py',
        '__version.py',
        '_version.py',
        'version.py',
        'VERSION.py',
        'package_data.py',
    )

    setup_py_dir = fileutils.parent_directory(setup_location)
    src_dir = os.path.join(setup_py_dir, 'src')
    has_src = os.path.exists(src_dir)
    if TRACE:
        logger_debug('    detect_version_attribute():', 'src_dir:', src_dir)
        logger_debug('    detect_version_attribute():', 'has_src:', has_src)

    candidate_locs = []

    if segments:
        for n in special_names:
            candidate_locs.append(segments + [n])
        if has_src:
            for n in special_names:
                candidate_locs.append(['src'] + segments + [n])

        if len(segments) > 1:
            heads = segments[:-1]
            tail = segments[-1]
            candidate_locs.append(heads + [tail + '.py'])
            if has_src:
                candidate_locs.append(['src'] + heads + [tail + '.py'])

        else:
            seg = segments[0]
            candidate_locs.append([seg + '.py'])
            if has_src:
                candidate_locs.append(['src', seg + '.py'])

    candidate_locs = [
        os.path.join(setup_py_dir, *cand_loc_segs)
        for cand_loc_segs in candidate_locs
    ]
    if TRACE:
        logger_debug('    detect_version_attribute():', 'candidate_locs1:', candidate_locs)

    for fl in get_module_scripts(
        location=setup_py_dir,
        max_depth=4,
        interesting_names=special_names,
    ):
        candidate_locs.append(fl)

    if TRACE:
        logger_debug('    detect_version_attribute():', 'candidate_locs2:')
        for loc in candidate_locs:
            logger_debug('        loc:', loc)

    version = detect_version_in_locations(
        candidate_locs=candidate_locs,
        detector=find_dunder_version
    )
    if TRACE:
        logger_debug('    detect_version_attribute():', 'version2:', version)

    if version:
        return version

    version = detect_version_in_locations(
        candidate_locs=candidate_locs,
        detector=find_plain_version,
    )
    if TRACE:
        logger_debug('    detect_version_attribute():', 'version3:', version)

    return version


def detect_version_in_locations(candidate_locs, detector=find_plain_version):
    """
    Return the first version found in a location from the `candidate_locs` list
    using the `detector` callable. Return None if no version is found.
    """
    if TRACE:
        logger_debug('      detect_version_in_locations():', 'candidate_locs:', candidate_locs)

    for loc in candidate_locs:
        if not os.path.exists(loc):
            continue

        if TRACE: logger_debug('        detect_version_in_locations:', 'loc:', loc)

        # here the file exists try to get a dunder version
        version = detector(loc)

        if TRACE:
            logger_debug(
                '        detect_version_in_locations:',
                'detector', detector,
                'version:', version,
            )

        if version:
            return version


def get_module_scripts(location, max_depth=1, interesting_names=()):
    """
    Yield interesting Python script paths that have a name in
    `interesting_names` by walking the `location` directory recursively up to
    `max_depth` path segments extending from the root `location`.
    """
    if TRACE:
        logger_debug(
            '        get_module_scripts():',
            'location:', location,
            'max_depth:', max_depth,
            'interesting_names:', interesting_names
        )

    location = location.rstrip(os.path.sep)
    if TRACE: logger_debug('        get_module_scripts:', 'location:', location)

    for top, _dirs, files in os.walk(location):
        current_depth = compute_path_depth(location, top)
        if TRACE:
            logger_debug('           get_module_scripts:', 'current_depth:', current_depth)
            logger_debug('           get_module_scripts:', 'top:', top, '_dirs:', _dirs, 'files:', files)
        if current_depth >= max_depth:
            break
        for f in files:
            if TRACE: logger_debug('              get_module_scripts:', 'file:', f)

            if f in interesting_names:
                path = os.path.join(top, f)
                if TRACE: logger_debug('                  get_module_scripts:', 'path:', path)
                yield path


def compute_path_depth(base, path):
    """
    Return the depth of ``path`` below ``base`` as the number of path segments
    that ``path`` extends below ``base``.
    For example:
    >>> base = '/home/foo/bar'
    >>> compute_path_depth(base, '/home/foo/bar/baz')
    1
    >>> compute_path_depth(base, base)
    0
    """
    base = base.strip(os.path.sep)
    path = path.strip(os.path.sep)

    assert path.startswith(base)
    subpath = path[len(base):].strip(os.path.sep)
    segments = [s for s in subpath.split(os.path.sep) if s]
    depth = len(segments)
    if TRACE:
        logger_debug(
            '    compute_path_depth:',
            'base:', base, 'path:', path, 'subpath:', subpath,
            'segments:', segments, 'depth:', depth,)
    return depth


def get_requirement_from_section(section, sub_section):
    """
    Yield extracted requirement from the ``sub_section`` key of of a ``section``
    mapping (from a setup.cfg)
    """
    content = section.get(sub_section, "")
    temp = tempfile.NamedTemporaryFile(delete=False)
    location = temp.name
    with open(location, "w") as f:
        f.write(content)
    packages, _ = get_requirements_txt_dependencies(location=location)
    for req in packages:
        yield req.extracted_requirement
