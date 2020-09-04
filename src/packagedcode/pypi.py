#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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

from collections import OrderedDict
import ast
import io
import json
import logging
import os
import sys

import attr
from six import string_types

from pkginfo import BDist
from pkginfo import Develop
from pkginfo import SDist
from pkginfo import UnpackedSDist
from pkginfo import Wheel

import dparse
from dparse import filetypes

import saneyaml

from commoncode import filetype
from commoncode import fileutils
from commoncode.system import py2
from packagedcode import models
from packagedcode.utils import build_description
from packagedcode.utils import combine_expressions
from packageurl import PackageURL

try:
    # Python 2
    unicode = unicode  # NOQA

except NameError:  # pragma: nocover
    # Python 3
    unicode = str  # NOQA


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
        return logger.debug(' '.join(isinstance(a, string_types) and a or repr(a) for a in args))

# FIXME: this whole module is a mess


@attr.s()
class PythonPackage(models.Package):
    metafiles = ('metadata.json', '*setup.py', 'PKG-INFO', '*.whl', '*.egg', '*requirements*.txt', '*requirements*.in', '*Pipfile.lock')
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
        declared_license = OrderedDict()
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
    if py2:
        mode = 'rb'
    else:
        mode = 'r'
    with open(location, mode) as f:
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

    data = json.loads(content, object_pairs_hook=OrderedDict)

    sha256 = None
    if '_meta' in data:
        for name, meta in data['_meta'].items():
            if name=='hash':
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

    # FIXME: what if this is unicode text?
    if py2:
        mode = 'rb'
    else:
        mode = 'r'
    with open(location, mode) as inp:
        setup_text = inp.read()

    setup_args = OrderedDict()

    # Parse setup.py file and traverse the AST
    tree = ast.parse(setup_text)
    for statement in tree.body:
        # We only care about function calls or assignments to functions named `setup`
        if (isinstance(statement, ast.Expr)
                or isinstance(statement, ast.Call)
                or isinstance(statement, ast.Assign)
                and isinstance(statement.value, ast.Call)
                and isinstance(statement.value.func, ast.Name)
                and statement.value.func.id == 'setup'):
            # Process the arguments to the setup function
            for kw in statement.value.keywords:
                arg_name = kw.arg
                if isinstance(kw.value, ast.Str):
                    setup_args[arg_name] = kw.value.s
                if isinstance(kw.value, ast.List):
                    # We collect the elements of a list if the element is not a function call
                    setup_args[arg_name] = [elt.s for elt in kw.value.elts if not isinstance(elt, ast.Call)]

    package_name = setup_args.get('name')
    if not package_name:
        return

    description = build_description(
        setup_args.get('summary', ''),
        setup_args.get('description', ''))

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

    declared_license = OrderedDict()
    license_setuptext = setup_args.get('license')
    declared_license['license'] = license_setuptext

    classifiers = setup_args.get('classifiers', [])
    license_classifiers = [c for c in classifiers if c.startswith('License')]
    declared_license['classifiers'] = license_classifiers

    other_classifiers = [c for c in classifiers if not c.startswith('License')]

    return PythonPackage(
        name=package_name,
        version=setup_args.get('version'),
        description=description or None,
        homepage_url=setup_args.get('url') or None,
        parties=parties,
        declared_license=declared_license,
        keywords=other_classifiers,
    )


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
        infos = json.load(infs, object_pairs_hook=OrderedDict)

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

    declared_license = OrderedDict()
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
    elif isinstance(declared_license, (str, unicode,)):
        values = [declared_license]
    else:
        return

    detected_licenses = []

    for value in values:
        if not value:
            continue
        # The value could be a string or a list
        if isinstance(value, string_types):
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
