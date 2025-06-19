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

_MANIFEST_ENDS = {
    '.about': 'ABOUT file',
    '/bower.json': 'bower',
    '/project.clj': 'clojure',
    '.podspec': 'cocoapod',
    '/composer.json': 'composer',
    '/description': 'cran',
    '/elm-package.json': 'elm',
    '/+compact_manifest': 'freebsd',
    '+manifest': 'freebsd',
    '.gemspec': 'gem',
    '/metadata': 'gem',
    # the extracted metadata of a gem archive
    '/metadata.gz-extract': 'gem',
    '/build.gradle': 'gradle',
    '/project.clj': 'clojure',
    '.pom': 'maven',
    '/pom.xml': 'maven',

    '.cabal': 'haskell',
    '/haxelib.json': 'haxe',
    '/package.json': 'npm',
    '.nuspec': 'nuget',
    '.pod': 'perl',
    '/meta.yml': 'perl',
    '/dist.ini': 'perl',

    '/pipfile': 'pypi',
    '/setup.cfg': 'pypi',
    '/setup.py': 'pypi',
    '/PKG-INFO': 'pypi',
    '/pyproject.toml': 'pypi',
    '.spec': 'rpm',
    '/cargo.toml': 'rust',
    '.spdx': 'spdx',
    '/dependencies': 'generic',

    # note that these two cannot be top-level for now
    'debian/copyright': 'deb',
    'meta-inf/manifest.mf': 'maven',

    # TODO: Maven also has sometimes a pom under META-INF/
    # 'META-INF/manifest.mf': 'JAR and OSGI',

}

MANIFEST_ENDS = tuple(_MANIFEST_ENDS)

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
    _MANIF=MANIFEST_ENDS,
    _README=README_STARTS_ENDS,
):
    """
    Set classification flags on the `resource` Resource.
    """
    path = resource.path.lower()

    resource.is_legal = is_legal = check_resource_name_start_and_end(resource, _LEGAL)
    resource.is_readme = is_readme = check_resource_name_start_and_end(resource, _README)
    resource.is_community = check_is_resource_community_file(resource)
    # FIXME: this will never be picked up as this is NOT available in a pre-scan plugin
    has_package_data = bool(getattr(resource, 'package_data', False))
    resource.is_manifest = is_manifest = path.endswith(_MANIF) or has_package_data
    resource.is_key_file = (resource.is_top_level and (is_readme or is_legal or is_manifest))
    return resource
