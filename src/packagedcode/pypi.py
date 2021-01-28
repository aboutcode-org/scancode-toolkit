#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import ast
import io
import json
import logging
import os
import re
import sys

import attr
import dparse
from dparse import filetypes
from pkginfo import BDist
from pkginfo import Develop
from pkginfo import SDist
from pkginfo import UnpackedSDist
from pkginfo import Wheel
from packageurl import PackageURL
import saneyaml

from commoncode import filetype
from commoncode import fileutils
from packagedcode import models
from packagedcode.utils import build_description
from packagedcode.utils import combine_expressions


"""
Detect and collect Python packages information.

"""

TRACE = False


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))

# FIXME: this whole module is a mess


@attr.s()
class PythonPackage(models.Package):
    metafiles = (
        'metadata.json',
        '*setup.py',
        'PKG-INFO',
        '*.whl',
        '*.egg',
        '*requirements*.txt',
        '*requirements*.in',
        '*Pipfile.lock',
    )
    extensions = ('.egg', '.whl', '.pyz', '.pex',)
    default_type = 'pypi'
    default_primary_language = 'Python'
    default_web_baseurl = 'https://pypi.org'
    default_download_baseurl = 'https://pypi.io/packages/source'
    default_api_baseurl = 'http://pypi.python.org/pypi'

    @classmethod
    def recognize(cls, location):
        yield parse(location)

    def compute_normalized_license(self):
        return compute_normalized_license(self.declared_license)

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        if not self.name:
            return
        return '{}/project/{}'.format(baseurl, self.name)

    def repository_download_url(self, baseurl=default_download_baseurl):
        if not self.name or not self.version:
            return
        return '{baseurl}/{name[0]}/{name}/{name}-{version}.tar.gz'.format(baseurl=baseurl, name=self.name, version=self.version)

    def api_data_url(self, baseurl=default_api_baseurl):
        if not self.name:
            return
        if not self.version:
            return '{}/{}/json'.format(baseurl, self.name)
        return '{}/{}/{}/json'.format(baseurl, self.name, self.version)


def parse(location):
    """
    Return a Package built from parsing a file or directory at 'location'
    """
    if filetype.is_dir(location):
        package = parse_unpackaged_source(location)
        if package:
            parse_dependencies(location, package)
            return package
    else:
        file_name = fileutils.file_name(location)
        parsers = {
            'setup.py': parse_setup_py,
            'requirements.txt': parse_requirements_txt,
            'requirements.in': parse_requirements_txt,
            'Pipfile.lock': parse_pipfile_lock,
            'metadata.json': parse_metadata,
            'PKG-INFO': parse_unpackaged_source,
            '.whl': parse_wheel,
            '.egg': parse_egg_binary,
            '.tar.gz': parse_source_distribution,
            '.zip': parse_source_distribution,
        }
        for name, parser in parsers.items():
            if file_name.endswith(name):
                package = parser(location)
                if package:
                    parent_directory = fileutils.parent_directory(location)
                    parse_dependencies(parent_directory, package)
                    return package


def parse_unpackaged_source(location):
    """
    Passing it the path to the unpacked package, or by passing it the setup.py at the top level.
    """
    unpackaged_dist = None
    try:
        unpackaged_dist = UnpackedSDist(location)
    except ValueError:
        try:
            unpackaged_dist = Develop(location)
        except ValueError:
            pass

    return parse_with_pkginfo(unpackaged_dist)


def parse_with_pkginfo(pkginfo):
    if pkginfo and pkginfo.name:
        description = pkginfo.description
        if not description:
            description = pkginfo.summary
        common_data = dict(
            name=pkginfo.name,
            version=pkginfo.version,
            description=description,
            download_url=pkginfo.download_url,
            homepage_url=pkginfo.home_page,
        )
        package = PythonPackage(**common_data)
        declared_license = {}
        if pkginfo.license:
            # TODO: We should make the declared license as it is, this should be updated in scancode to parse a pure string
            declared_license['license'] = pkginfo.license
        if pkginfo.classifiers:
            license_classifiers = []
            other_classifiers = []
            for classifier in pkginfo.classifiers:
                if classifier.startswith('License'):
                    license_classifiers.append(classifier)
                else:
                    other_classifiers.append(classifier)
            declared_license['classifiers'] = license_classifiers
            package.keywords = other_classifiers
        if declared_license:
            package.declared_license = declared_license
        if pkginfo.author_email:
            parties = []
            parties.append(models.Party(
                type=models.party_person, name=pkginfo.author, role='author', email=pkginfo.author_email))
            package.parties = parties
        return package


def parse_dependencies(location, package):
    """
    Loop all resources from the passing folder location, get the dependencies from the resources and set it to the passing package object.
    """
    for resource_location in os.listdir(location):
        dependencies = parse_with_dparse(resource_location)
        if dependencies:
            package.dependencies = dependencies


dependency_type_by_extensions = {
    ('.txt', '.in'): 'requirements.txt',
    ('Pipfile.lock'): 'Pipfile.lock',
}


def get_dependency_type(file_name, dependency_type_by_extensions=dependency_type_by_extensions):
    """
    Return the type of a dependency as a string or None given a `file_name` string.
    """
    for extensions, dependency_type in dependency_type_by_extensions.items():
        if file_name.endswith(extensions):
            return dependency_type


def parse_with_dparse(location):
    is_dir = filetype.is_dir(location)
    if is_dir:
        return
    file_name = fileutils.file_name(location)

    dependency_type = get_dependency_type(file_name)

    if dependency_type not in (filetypes.requirements_txt,
                         filetypes.conda_yml,
                         filetypes.tox_ini,
                         filetypes.pipfile,
                         filetypes.pipfile_lock):
        return
    with open(location) as f:
        content = f.read()

    df = dparse.parse(content, file_type=dependency_type)
    df_dependencies = df.dependencies

    if not df_dependencies:
        return

    package_dependencies = []
    for df_dependency in df_dependencies:
        specs = list(df_dependency.specs._specs)
        is_resolved = False
        requirement = None
        purl = PackageURL(
            type='pypi',
            name=df_dependency.name
        ).to_string()
        if specs:
            requirement = str(df_dependency.specs)
            for spec in specs:
                operator = spec.operator
                version = spec.version
                if any(operator == element for element in ('==', '===')):
                    is_resolved = True
                    purl = PackageURL(
                        type='pypi',
                        name=df_dependency.name,
                        version=version
                    ).to_string()
        package_dependencies.append(
            models.DependentPackage(
                purl=purl,
                scope='dependencies',
                is_runtime=True,
                is_optional=False,
                is_resolved=is_resolved,
                requirement=requirement
            )
        )

    return package_dependencies


def parse_requirements_txt(location):
    """
    Return a PythonPackage built from a Python requirements.txt files at location.
    """
    package_dependencies = parse_with_dparse(location)
    return PythonPackage(dependencies=package_dependencies)


def parse_pipfile_lock(location):
    """
    Return a PythonPackage built from a Python Pipfile.lock file at location.
    """
    with open(location) as f:
        content = f.read()

    data = json.loads(content)

    sha256 = None
    if '_meta' in data:
        for name, meta in data['_meta'].items():
            if name == 'hash':
                sha256 = meta.get('sha256')

    package_dependencies = parse_with_dparse(location)
    return PythonPackage(
        sha256=sha256,
        dependencies=package_dependencies
    )


def parse_setup_py(location):
    """
    Return a PythonPackage built from setup.py data.
    """
    if not location or not location.endswith('setup.py'):
        return

    with open(location) as inp:
        setup_text = inp.read()

    setup_args = {}

    # Parse setup.py file and traverse the AST
    tree = ast.parse(setup_text)
    for statement in tree.body:
        # We only care about function calls or assignments to functions named
        # `setup` or `main`
        if (isinstance(statement, (ast.Expr, ast.Call, ast.Assign))
            and isinstance(statement.value, ast.Call)
            and isinstance(statement.value.func, ast.Name)
            # we also look for main as sometimes this is used instead of setup()
            and statement.value.func.id in ('setup', 'main')
        ):

            # Process the arguments to the setup function
            for kw in getattr(statement.value, 'keywords', []):
                arg_name = kw.arg

                if isinstance(kw.value, ast.Str):
                    setup_args[arg_name] = kw.value.s

                elif isinstance(kw.value, (ast.List, ast.Tuple, ast.Set,)):
                    # We collect the elements of a list if the element
                    # and tag function calls
                    value = [
                        elt.s for elt in kw.value.elts
                        if not isinstance(elt, ast.Call)
                    ]
                    setup_args[arg_name] = value

                # TODO:  what if isinstance(kw.value, ast.Dict)
                # or an expression like a call to version=get_version or version__version__

    package_name = setup_args.get('name')
    if not package_name:
        return

    description = build_description(
        setup_args.get('summary', ''),
        setup_args.get('description', ''),
    )

    parties = []
    author = setup_args.get('author')
    author_email = setup_args.get('author_email')
    homepage_url = setup_args.get('url')
    if author:
        parties.append(
            models.Party(
                type=models.party_person,
                name=author,
                email=author_email,
                role='author',
                url=homepage_url
            )
        )
    elif author_email:
        parties.append(
            models.Party(
                type=models.party_person,
                email=author_email,
                role='author',
                url=homepage_url
            )
        )

    declared_license = {}
    license_setuptext = setup_args.get('license')
    declared_license['license'] = license_setuptext

    classifiers = setup_args.get('classifiers', [])
    license_classifiers = [c for c in classifiers if c.startswith('License')]
    declared_license['classifiers'] = license_classifiers

    other_classifiers = [c for c in classifiers if not c.startswith('License')]

    detected_version = setup_args.get('version')
    if not detected_version:
        # search for possible dunder versions here and elsewhere
        detected_version = detect_version_attribute(location)

    return PythonPackage(
        name=package_name,
        version=detected_version,
        description=description or None,
        homepage_url=setup_args.get('url') or None,
        parties=parties,
        declared_license=declared_license,
        keywords=other_classifiers,
    )


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
    with io.open(location, encoding='utf8') as fp:
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
    would return six.__version__.

    Code inspired and heavily modified from:
    https://github.com/pyserial/pyserial/blob/d867871e6aa333014a77498b4ac96fdd1d3bf1d8/setup.py#L34
    SPDX-License-Identifier: BSD-3-Clause
    (C) 2001-2020 Chris Liechti <cliechti@gmx.net>
    """
    pattern = re.compile(r"^\s*version\s*=\s*(.*__version__)", re.MULTILINE)
    match = find_pattern(location, pattern)
    if TRACE: logger_debug('find_setup_py_dunder_version:', 'location:', location, 'match:', match)
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
        logger_debug('    detect_dunder_version:', 'setup_location:', setup_location)
        logger_debug('    setup_version_arg:', repr(setup_version_arg),)
        logger_debug('    setup_py__version:', repr(setup_py__version),)
    if setup_version_arg == '__version__' and setup_py__version:
        version = setup_py__version or None
        if TRACE: logger_debug('    detect_dunder_version: A:', version)
        return version

    # here we have a more complex __version__ location
    # we start by adding the possible paths and file name
    # and we look at these in sequence

    candidate_locs = []

    if setup_version_arg and '.' in setup_version_arg:
        segments = setup_version_arg.split('.')[:-1]
    else:
        segments = []

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

    candidate_locs = [os.path.join(setup_py_dir, *cand_loc_segs) for cand_loc_segs in candidate_locs]

    for fl in get_module_scripts(
        location=setup_py_dir,
        max_depth=4,
        interesting_names=special_names,
    ):
        candidate_locs.append(fl)

    if TRACE:
        for loc in candidate_locs:
            logger_debug('    can loc:', loc)

    version = detect_version_in_locations(
        candidate_locs=candidate_locs,
        detector=find_dunder_version
    )

    if version:
        return version

    return detect_version_in_locations(
        candidate_locs=candidate_locs,
        detector=find_plain_version,
    )


def detect_version_in_locations(candidate_locs, detector=find_plain_version):
    """
    Return the first version found in a location from `candidate_locs` using the
    `detector` callable. Or None.
    """
    for loc in candidate_locs:
        if os.path.exists(loc):
            if TRACE: logger_debug('detect_version_in_locations:', 'loc:', loc)
            # here the file exists try to get a dunder version
            version = detector(loc)
            if TRACE: logger_debug('detect_version_in_locations:', 'detector', detector, 'version:', version)
            if version:
                return version


def get_module_scripts(location, max_depth=1, interesting_names=()):
    """
    Yield interesting Python script paths that have a name in
    `interesting_names` by walking the `location` directory recursively up to
    `max_depth` path segments extending from the root `location`.
    """

    location = location.rstrip(os.path.sep)
    current_depth = max_depth
    for top, _dirs, files in os.walk(location):
        if current_depth == 0:
            break
        for f in files:
            if f in interesting_names:
                path = os.path.join(top, f)
                if TRACE: logger_debug('get_module_scripts:', 'path', path)
                yield path

        current_depth -= 1


# FIXME: use proper library for parsing these
def parse_metadata(location):
    """
    Return a Package object from the Python wheel 'metadata.json' file
    at 'location' or None. Check if the parent directory of 'location'
    contains both a 'METADATA' and a 'DESCRIPTION.rst' file to ensure
    this is a proper metadata.json file.
    """
    if not location or not location.endswith('metadata.json'):
        if TRACE: logger_debug('parse_metadata: not metadata.json:', location)
        return
    parent_dir = fileutils.parent_directory(location)
    # FIXME: is the absence of these two files a show stopper?
    paths = [os.path.join(parent_dir, n) for n in ('METADATA', 'DESCRIPTION.rst')]
    if not all(os.path.exists(p) for p in paths):
        if TRACE: logger_debug('parse_metadata: not extra paths', paths)
        return

    with open(location, 'rb') as infs:
        infos = json.load(infs)

    extensions = infos.get('extensions')
    if TRACE: logger_debug('parse_metadata: extensions:', extensions)
    details = extensions and extensions.get('python.details')
    urls = details and details.get('project_urls')
    homepage_url = urls and urls.get('Home')

    parties = []
    if TRACE: logger_debug('parse_metadata: contacts:', details.get('contacts'))
    contacts = details and details.get('contacts') or []
    for contact in contacts:
        if TRACE: logger_debug('parse_metadata: contact:', contact)
        name = contact and contact.get('name')
        if not name:
            if TRACE: logger_debug('parse_metadata: no name:', contact)
            continue
        parties.append(models.Party(type=models.party_person, name=name, role='contact'))

    description = build_description(
        infos.get('summary'),
        infos.get('description')
    )

    classifiers = infos.get('classifiers')
    license_classifiers = []
    other_classifiers = []
    if classifiers:
        for classifier in classifiers:
            if classifier.startswith('License'):
                license_classifiers.append(classifier)
            else:
                other_classifiers.append(classifier)

    declared_license = {}
    lic = infos.get('license')
    if lic:
        declared_license['license'] = lic
    if license_classifiers:
        declared_license['classifiers'] = license_classifiers

    package = PythonPackage(
        name=infos.get('name'),
        version=infos.get('version'),
        description=description or None,
        declared_license=declared_license or None,
        homepage_url=homepage_url or None,
        parties=parties,
        keywords=other_classifiers,
    )
    return package


def parse_pkg_info(location):
    """
    Return a PythonPackage from a a 'PKG-INFO' file at 'location' or None.
    """
    if not location:
        return

    if not location.endswith('PKG-INFO'):
        return

    with io.open(location, encoding='utf-8') as loc:
        infos = saneyaml.load(loc.read())

    logger.error(logger)
    if not infos.get('Name'):
        return

    parties = []
    author = infos.get('Author')
    if author:
        parties.append(models.Party(type=models.party_person, name=author, role=''))

    package = PythonPackage(
        name=infos.get('Name'),
        version=infos.get('Version'),
        description=infos.get('Summary') or infos.get('Description'),
        homepage_url=infos.get('Home-page') or None,
        # FIXME: this is NOT correct as classifiers can be used for this too
        declared_license=infos.get('License') or None,
        # FIXME: what about email?
        # FIXME: what about maintainers?
        parties=parties,
    )
    return package


def parse_wheel(location):
    """
    Passing wheel file location which is generated via setup.py bdist_wheel.
    """
    wheel = Wheel(location)
    return parse_with_pkginfo(wheel)


def parse_egg_binary(location):
    """
    Passing wheel file location which is generated via setup.py bdist_wheel.
    """
    binary_dist = BDist(location)
    return parse_with_pkginfo(binary_dist)


def parse_source_distribution(location):
    """
    SDist objects are created from a filesystem path to the corresponding archive. Such as Zip or .tar.gz files
    """
    sdist = SDist(location)
    if sdist:
        common_data = dict(
            name=sdist.name,
            version=sdist.version,
        )
        package = PythonPackage(**common_data)
        return package


def compute_normalized_license(declared_license):
    """
    Return a normalized license expression string detected from a mapping or list of
    declared license items.
    """
    if not declared_license:
        return

    if isinstance(declared_license, dict):
        values = list(declared_license.values())
    elif isinstance(declared_license, list):
        values = list(declared_license)
    elif isinstance(declared_license, str):
        values = [declared_license]
    else:
        return

    detected_licenses = []

    for value in values:
        if not value:
            continue
        # The value could be a string or a list
        if isinstance(value, str):
            detected_license = models.compute_normalized_license(value)
            if detected_license:
                detected_licenses.append(detected_license)
        else:
            # this is a list
            for declared in value:
                detected_license = models.compute_normalized_license(declared)
                if detected_license:
                    detected_licenses.append(detected_license)

    if detected_licenses:
        return combine_expressions(detected_licenses)
