#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#


from commoncode.fileutils import file_name
from commoncode.fileutils import file_base_name

def get_relative_path(root_path, path):
    """
    Return a path relativefrom the posix 'path' relative to a
    base path of `len_base_path` length where the base is a directory if
    `base_is_dir` True or a file otherwise.
    """
    return path[len(root_path):].lstrip('/')


LEGAL_STARTS_ENDS = (
    'copying',
    'copyright',
    'copyrights',

    'copyleft',
    'notice',
    'license',
    'licenses',
    'licence',
    'licences',
    'licensing',
    'licencing',

    'legal',
    'eula',
    'agreement',
    'copyleft',
    'patent',
    'patents',
)

import os

_MANIFEST_ENDS = {
    '.about': 'ABOUT file',
    '/bower.json': 'bower',
    '/.bower.json': 'bower',
    '.podspec': 'cocoapod',
    '.podspec.json': 'cocoapod',
    '/composer.json': 'composer',
    '/composer.lock': 'composer',
    '/description': 'cran',
    '/elm-package.json': 'elm',
    '/+compact_manifest': 'freebsd',
    '+manifest': 'freebsd',
    '.gemspec': 'gem',
    '/metadata': 'gem',
    # the extracted metadata of a gem archive
    '/metadata.gz-extract': 'gem',
    '/build.gradle': 'gradle',
    '/build.gradle.kts': 'gradle',
    '/project.clj': 'clojure',
    '.pom': 'maven',
    '/pom.xml': 'maven',
    '/pom.properties': 'maven',

    '.cabal': 'haskell',
    '/haxelib.json': 'haxe',
    '/package.json': 'npm',
    '/package-lock.json': 'npm',
    '/.package-lock.json': 'npm',
    '/npm-shrinkwrap.json': 'npm',
    '/yarn.lock': 'npm',
    '/pnpm-lock.yaml': 'npm',
    '/pnpm-workspace.yaml': 'npm',
    '/shrinkwrap.yaml': 'npm',
    '.nuspec': 'nuget',
    '/packages.lock.json': 'nuget',
    '.pod': 'perl',
    '/meta.yml': 'perl',
    '/dist.ini': 'perl',

    '/pipfile': 'pypi',
    '/pipfile.lock': 'pypi',
    '/poetry.lock': 'pypi',
    '/uv.lock': 'pypi',
    '/setup.cfg': 'pypi',
    '/setup.py': 'pypi',
    '/PKG-INFO': 'pypi',
    '/pyproject.toml': 'pypi',
    '/requirements.txt': 'pypi',
    '.spec': 'rpm',
    '/cargo.toml': 'rust',
    '/cargo.lock': 'rust',
    '.spdx': 'spdx',
    '/dependencies': 'generic',

    '/go.mod': 'golang',
    '/go.sum': 'golang',
    '/godeps.json': 'golang',

    '/pubspec.yaml': 'pubspec',
    '/pubspec.lock': 'pubspec',

    '/conanfile.py': 'conan',
    '/conandata.yml': 'conan',

    '/gemfile': 'gem',
    '/gemfile.lock': 'gem',

    '/podfile': 'cocoapods',
    '/podfile.lock': 'cocoapods',

    '/package.resolved': 'swift',
    '/.package.resolved': 'swift',
    '/package.swift.json': 'swift',

    '/opam': 'opam',
    '/apkbuild': 'alpine',
    '/configure': 'autotools',
    '/configure.ac': 'autotools',
    '/build': 'bazel',
    '/buck': 'buck',
    '/metadata.bzl': 'buck',

    # note that these two cannot be top-level for now
    'debian/copyright': 'deb',
    'meta-inf/manifest.mf': 'maven',

    # TODO: Maven also has sometimes a pom under META-INF/
    # 'META-INF/manifest.mf': 'JAR and OSGI',

}

ARCHIVE_EXTENSIONS = (
    '.apk', '.aar', '.jar', '.war', '.ear', '.sar', '.mar',
    '.whl', '.egg', '.gem', '.rpm', '.deb', '.msi', '.exe',
    '.dll', '.dmg', '.iso', '.udf', '.img', '.cab', '.xpi',
    '.crx', '.ipa', '.shar', '.tgz', '.tar.gz', '.tar.bz2',
    '.zip', '.tar.xz', '.sparseimage', '.mum'
)

_MANIFEST_ENDS_CACHE = None


def get_manifest_ends():
    """
    Return a tuple of path suffixes/ends that indicate a package manifest file,
    dynamically computed from all active DatafileHandler classes in ``packagedcode``.
    """
    global _MANIFEST_ENDS_CACHE
    if _MANIFEST_ENDS_CACHE is not None:
        return _MANIFEST_ENDS_CACHE

    manifest_ends = dict(_MANIFEST_ENDS)

    try:
        from packagedcode import APPLICATION_PACKAGE_DATAFILE_HANDLERS

        for handler in APPLICATION_PACKAGE_DATAFILE_HANDLERS:
            # Skip binary and archive handlers based on filetypes
            filetypes = getattr(handler, 'filetypes', ())
            if any('archive' in ft or 'compressed' in ft or 'executable' in ft for ft in filetypes):
                continue

            pkg_type = getattr(handler, 'default_package_type', None) or 'generic'
            for pat in getattr(handler, 'path_patterns', ()):
                pat_lower = pat.lower()
                ext = os.path.splitext(pat_lower)[1]
                if ext in ARCHIVE_EXTENSIONS:
                    continue

                # Normalize glob patterns into endswith matchers
                if pat_lower.startswith('*/'):
                    manifest_ends[pat_lower[1:]] = pkg_type
                elif pat_lower.startswith('*.'):
                    manifest_ends[pat_lower[1:]] = pkg_type
                elif pat_lower.startswith('*'):
                    suffix = '/' + pat_lower.lstrip('*')
                    manifest_ends[suffix] = pkg_type
                    bare = pat_lower.lstrip('*')
                    if bare and not bare.startswith('/'):
                        manifest_ends[bare] = pkg_type
                elif pat_lower.startswith('/'):
                    manifest_ends[pat_lower] = pkg_type
                else:
                    manifest_ends['/' + pat_lower] = pkg_type
                    manifest_ends[pat_lower] = pkg_type
    except Exception:
        # Fallback to base list if packagedcode is not importable
        pass

    _MANIFEST_ENDS_CACHE = tuple(manifest_ends)
    return _MANIFEST_ENDS_CACHE


MANIFEST_ENDS = get_manifest_ends()

README_STARTS_ENDS = (
    'readme',
)

# Community files are usually files used for FOSS project and community
# maintainence purposes. We want to detect these as in the context of
# licenses as these files don't have interesting license detections, or
# license detection issues are not important to review for these files.
# this is similar to `key` files, which also has a lot of community info
# but there the license declarations are extremely important as they have
# information on the primary (or even secondary) licenses for the package
COMMUNITY_FILES = (
    'CHANGELOG',
    'ROADMAP',
    'CONTRIBUTING',
    'CODE_OF_CONDUCT',
    'AUTHORS',
    'SECURITY',
    'FUNDING',
)


def clean_underscore_dash(filename):
    return filename.replace('_', '').replace('-', '')


def check_is_community_file(filename):
    """
    Return True if the resource is a known community filename,
    return False otherwise.
    """
    community_files_cleaned = [
        clean_underscore_dash(filename.lower())
        for filename in COMMUNITY_FILES
    ]
    name = clean_underscore_dash(filename.lower())
    if any(
        name.startswith(comm_name) or name.endswith(comm_name)
        for comm_name in community_files_cleaned
    ):
        return True

    return False


def check_is_resource_community_file(resource):
    """
    Return True if the `resource` is a community file.
    """
    return check_is_community_file(resource.name) or check_is_community_file(resource.base_name)


def check_is_path_community_file(path):
    """
    Return True if the file at `path` is a community file.
    """
    name = file_name(path, force_posix=True)
    base_name = file_base_name(path, force_posix=True)
    return check_is_community_file(name) or check_is_community_file(base_name)


def check_resource_name_start_and_end(resource, STARTS_ENDS):
    """
    Return True if `resource.name` or `resource.base_name` begins or ends with
    an element of `STARTS_ENDS`.
    """
    name = resource.name.lower()
    base_name = resource.base_name.lower()
    return (
        name.startswith(STARTS_ENDS)
        or name.endswith(STARTS_ENDS)
        or base_name.startswith(STARTS_ENDS)
        or base_name.endswith(STARTS_ENDS)
    )


def set_classification_flags(resource,
    _LEGAL=LEGAL_STARTS_ENDS,
    _MANIF=None,
    _README=README_STARTS_ENDS,
):
    """
    Set classification flags on the `resource` Resource.
    """
    if _MANIF is None:
        _MANIF = get_manifest_ends()

    path = resource.path.lower()

    resource.is_legal = is_legal = check_resource_name_start_and_end(resource, _LEGAL)
    resource.is_readme = is_readme = check_resource_name_start_and_end(resource, _README)
    resource.is_community = check_is_resource_community_file(resource)
    # FIXME: this will never be picked up as this is NOT available in a pre-scan plugin
    has_package_data = bool(getattr(resource, 'package_data', False))
    resource.is_manifest = is_manifest = (
        path.endswith(_MANIF)
        or ('/' + path).endswith(_MANIF)
        or has_package_data
    )
    resource.is_key_file = (resource.is_top_level and (is_readme or is_legal or is_manifest))
    return resource
