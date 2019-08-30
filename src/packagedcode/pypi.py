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
import io
import json
import logging
import os
import re
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
    metafiles = ('metadata.json', '*setup.py', 'PKG-INFO', '*.whl', '*.egg')
    extensions = ('.egg', '.whl', '.pyz', '.pex',)
    default_type = 'pypi'
    default_primary_language = 'Python'
    default_web_baseurl = None
    default_download_baseurl = None
    default_api_baseurl = None

    @classmethod
    def recognize(cls, location):
        package = parse(location)
        if not package:
            package = parse2(location)
        return package

    def compute_normalized_license(self):
        return compute_normalized_license(self.declared_license)


def compute_normalized_license(declared_license):
    """
    Return a normalized license expression string detected from a list of
    declared license items.
    """
    if not declared_license:
        return

    detected_licenses = []

    for value in declared_license.values():
        if not value:
            continue
        # The value could be a string or a list
        if isinstance(value, string_types):
            detected_license = models.compute_normalized_license(value)
            if detected_license:
                detected_licenses.append(detected_license)
        else:
            for declared in value:
                detected_license = models.compute_normalized_license(declared)
                if detected_license:
                    detected_licenses.append(detected_license)

    if detected_licenses:
        return combine_expressions(detected_licenses)


PKG_INFO_ATTRIBUTES = [
    'Name',
    'Version',
    'Author',
    'Author-email',
    'License',
    'Description',
    'Platform',
    'Home-page',
    'Summary'
]


def parse_pkg_info(location):
    """
    Return a Package from a a 'PKG-INFO' file at 'location' or None.
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

# FIXME: each attribute require reparsing the setup.py: this is nuts!


def get_setup_attribute(setup_text, attribute):
    """
    Return the the value for an `attribute` if found in the 'setup.py' file at
    `location` or None.

    For example with this setup.py file:
    setup(
        name='requests',
        version='1.0',
        )
    the value 'request' is returned for the attribute 'name'
    """
    if not setup_text:
        return

    # FIXME Use a valid parser for parsing 'setup.py'
    # FIXME: it does not make sense to reread a setup.py once for each attribute

    # FIXME: what are these regex doing?
    values = re.findall('setup\\(.*?' + attribute + '\\s*=\\s*[\"\']{1}.*?\'\\s*,', setup_text.replace('\n', ''))
    if len(values) > 1 or len(values) == 0:
        return
    else:
        values = ''.join(values)
        attr_value = re.sub('setup\(.*?' + attribute + '\\s*=\\s*[\"\']{1}', '', values)
        if attr_value.endswith('\','):
            return attr_value.replace('\',', '')
        else:
            return attr_value


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
        infos.get('summary') ,
        infos.get('description')
    )

    package = PythonPackage(
        name=infos.get('name'),
        version=infos.get('version'),
        description=description or None,
        declared_license=infos.get('license') or None,
        homepage_url=homepage_url or None,
        parties=parties,
    )
    return package


# FIXME: this is not the way to parse a python script
def parse_setup_py(location):
    """
    Return a package built from setup.py data.
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

    description = build_description(
        get_setup_attribute(setup_text, 'summary'),
        get_setup_attribute(setup_text, 'description'))

    parties = []
    author = get_setup_attribute(setup_text, 'author')
    if author:
        parties.append(
            models.Party(
            type=models.party_person,
            name=author, role='author'))

    declared_license = OrderedDict()
    license_setuptext = get_setup_attribute(setup_text, 'license')
    declared_license['license'] = license_setuptext

    classifiers = get_classifiers(setup_text)
    license_classifiers = [c for c in classifiers if c.startswith('License')]
    declared_license['classifiers'] = license_classifiers

    other_classifiers = [c for c in classifiers if not c.startswith('License')]

    package = PythonPackage(
        name=get_setup_attribute(setup_text, 'name'),
        version=get_setup_attribute(setup_text, 'version'),
        description=description or None,
        homepage_url=get_setup_attribute(setup_text, 'url') or None,
        parties=parties,
        declared_license=declared_license,
        keywords=other_classifiers,
    )
    return package


def get_classifiers(setup_text):
    """
    Return a list of classifiers
    """
    # FIXME: we are making grossly incorrect assumptions.
    classifiers = [line for line in setup_text.splitlines(False) if '::' in line]

    # strip spaces/tabs/quotes/commas
    classifiers = [line.strip('\t \'",;') for line in classifiers]
    return classifiers


def parse(location):
    """
    Return a Package built from parsing a file at 'location' The file
    name can be either a 'setup.py', 'metadata.json' or 'PKG-INFO'
    file.
    """
    file_name = fileutils.file_name(location)
    parsers = {
        'setup.py': parse_setup_py,
        'metadata.json': parse_metadata,
        'PKG-INFO': parse_pkg_info
    }
    parser = parsers.get(file_name)
    if parser:
        return parser(location)


def parse2(location):
    """
    Parse using the pkginfo library according the file types and return package.
    """
    is_dir = filetype.is_dir(location)
    if is_dir:
        parser = parse_unpackaged_source
        package = parser(location)
        if package:
            parse_dependencies(location, package)
            return package
    else:
        file_name = fileutils.file_name(location)
        parsers = {
            'setup.py': parse_unpackaged_source,
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


def parse_dependencies(location, package):
    """
    Loop all resources from the passing folder location, get the dependencies from the resources and set it to the passing package object.
    """
    for resource_location in os.listdir(location):
        dependencies = parse_with_dparse(resource_location)
        if dependencies:
            package.dependencies = dependencies


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


def parse_egg_binary(location):
    """
    Passing wheel file location which is generated via setup.py bdist_wheel.
    """
    binary_dist = BDist(location)
    return parse_with_pkginfo(binary_dist)


def parse_wheel(location):
    """
    Passing wheel file location which is generated via setup.py bdist_wheel.
    """
    wheel = Wheel(location)
    return parse_with_pkginfo(wheel)


def parse_with_pkginfo(pkginfo):
    if pkginfo and pkginfo.name:
        common_data = dict(
            name=pkginfo.name,
            version=pkginfo.version,
            description=pkginfo.description,
            download_url=pkginfo.download_url,
            homepage_url=pkginfo.home_page,
        )
        package = PythonPackage(**common_data)
        if pkginfo.license:
            # TODO: We should make the declared license as it is, this should be updated in scancode to parse a pure string
            package.declared_license = {'license': pkginfo.license}

        if pkginfo.maintainer:
            common_data['parties'] = []
            common_data['parties'].append(models.Party(
                type=models.party_person, name=pkginfo.maintainer, role='author', email=pkginfo.maintainer_email))
        return package


def parse_with_dparse(location):
    is_dir = filetype.is_dir(location)
    if is_dir:
        return
    file_name = fileutils.file_name(location)
    if file_name not in (filetypes.requirements_txt,
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
        df = dparse.parse(content, file_type=file_name)
        df_dependencies = df.dependencies
        if not df_dependencies:
            return
        package_dependencies = []
        for df_dependency in df_dependencies:
            specs = df_dependency.specs
            requirement = None
            if specs:
                requirement = str(specs)
            package_dependencies.append(
                models.DependentPackage(
                    purl=PackageURL(
                        type='pypi', name=df_dependency.name).to_string(),
                    scope='dependencies',
                    is_runtime=True,
                    is_optional=False,
                    requirement=requirement,
                )
            )
        return package_dependencies


def build_package(package_data):
    """
    Yield Package object from a package_data mapping json file.
    """
    info = package_data.get('info')
    if not info:
        return
    name = info.get('name')
    if not name:
        return
    short_desc = info.get('summary')
    long_desc = info.get('description')
    descriptions = [d for d in (short_desc, long_desc) if d and d.strip() and d.strip() != 'UNKNOWN']
    description = '\n'.join(descriptions)
    common_data = dict(
        name=name,
        version=info.get('version'),
        description=description,
        homepage_url=info.get('home_page'),
        bug_tracking_url=info.get('bugtrack_url'),
    )

    author = info.get('author')
    email = info.get('author_email')
    if author or email:
        parties = common_data.get('parties')
        if not parties:
            common_data['parties'] = []
        common_data['parties'].append(models.Party(
            type=models.party_person, name=author, role='author', email=email))

    maintainer = info.get('maintainer')
    email = info.get('maintainer_email')
    if maintainer or email:
        parties = common_data.get('parties')
        if not parties:
            common_data['parties'] = []
        common_data['parties'].append(models.Party(
            type=models.party_person, name=maintainer, role='maintainer', email=email))

    declared_license = OrderedDict()
    setuptext_licenses = []
    lic = info.get('license')
    if lic and lic != 'UNKNOWN':
        setuptext_licenses.append(lic)
    declared_license['license'] = setuptext_licenses

    classifiers_licenses = []
    classifiers = info.get('classifiers')
    if classifiers and not classifiers_licenses:
        licenses = [lic for lic in classifiers if lic.lower().startswith('license')]
        for lic in licenses:
            classifiers_licenses.append(lic)
    declared_license['classifiers'] = classifiers_licenses

    common_data['declared_license'] = declared_license

    kw = info.get('keywords')
    if kw:
        common_data['keywords'] = [k.strip() for k in kw.split(',') if k.strip()]

    package = PythonPackage(**common_data)
    return package
