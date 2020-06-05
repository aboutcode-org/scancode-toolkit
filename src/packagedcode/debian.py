#
# Copyright (c) nexB Inc. and others. All rights reserved.
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
from __future__ import unicode_literals

from collections import OrderedDict
import logging
import os

import attr
from six import string_types
from debut import debcon
from packageurl import PackageURL

from commoncode import filetype
from commoncode import fileutils
from commoncode.datautils import String
from packagedcode import models

"""
Handle Debian packages.
"""

TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


@attr.s()
class DebianPackage(models.Package):
    metafiles = ('*.control',)
    extensions = ('.deb',)
    filetypes = ('debian binary package',)
    mimetypes = ('application/x-archive', 'application/vnd.debian.binary-package',)
    default_type = 'deb'

    multi_arch = String(
        label='Multi-Arch',
        help='Multi-Arch value from status file')

    def to_dict(self, **kwargs):
        data = models.Package.to_dict(self, **kwargs)
        if 'multi_arch' in data:
            data.pop('multi_arch')

        return data


    def get_list_of_installed_files(self, info_dir):
        """
        Given a info_dir path, yeild a list of tuples of path + md5 values.
        """
        # Multi-Arch can be: foreign, same, allowed or empty
        # We only need to adjust the md5sum path in the case of `same`
        if self.multi_arch == 'same':
            arch = ':{}'.format(self.qualifiers.get('arch'))
        else:
            arch = ''

        package_md5sum = '{}{}.md5sums'.format(self.name, arch)
        with open(os.path.join(info_dir, package_md5sum)) as info_file:
            for line in info_file:
                line = line.strip()
                if not line:
                    continue

                md5sum, _, path = line.partition(' ')
                yield path.strip(), md5sum.strip()


    def get_copyright_file_path(self, root_dir):
        """
        Given a root_dir path to a filesystem root, return the path to a copyright file
        for this Package
        """
        # We start by looking for a copyright file stored in a directory named after the
        # package name. Otherwise we look for a copyright file stored in a source package
        # name.
        candidate_names = [self.name]
        candidate_names.extend(PackageURL.from_string(sp).name for sp in self.source_packages)
    
        copyright_file = os.path.join(root_dir, 'usr/share/doc/{}/copyright')

        for name in candidate_names:
            copyright_loc = copyright_file.format(name)
            if os.path.exists(copyright_loc):
                return copyright_loc


def get_installed_packages(root_dir, distro='debian'):
    """
    Given a directory to a rootfs, yield a DebianPackage and a list of `installed_files` 
    (path, md5sum) tuples.
    """
    base_status_file_loc = os.path.join(root_dir, 'var/lib/dpkg/status')
    base_info_dir = os.path.join(root_dir, 'var/lib/dpkg/info/')
    
    for package in parse_status_file(base_status_file_loc, distro=distro):
            yield package, list(package.get_list_of_installed_files(base_info_dir))


def is_debian_status_file(location):
    return (filetype.is_file(location)
            and fileutils.file_name(location).lower() == 'status')


def parse_status_file(location, distro='debian'):
    """
    Yield Debian Package objects from a dpkg `status` file or None.
    """
    if not is_debian_status_file(location):
        return

    for debian_pkg_data in debcon.get_paragraphs_data_from_file(location):
        yield build_package(debian_pkg_data, distro)


def build_package(package_data, distro='debian'):
    """
    Return a Package object from a package_data mapping (from a dpkg status file) 
    or None.
    """
    # construct the package
    package = DebianPackage()
    package.namespace = distro

    # add debian-specific package 'qualifiers'
    qualifiers = OrderedDict([
        ('arch', package_data.get('architecture')),
    ])
    package.qualifiers = qualifiers

    # mapping of top level `status` file items to the Package object field name
    plain_fields = [
        ('description', 'description'),
        ('homepage', 'homepage_url'),
        ('installed-size', 'size'),
        ('package', 'name'),
        ('version', 'version'),
        ('maintainer', 'maintainer'),
        ('multi-arch', 'multi_arch'),
    ]

    for source, target in plain_fields:
        value = package_data.get(source)
        if value:
            if isinstance(value, string_types):
                value = value.strip()
            if value:
                setattr(package, target, value)

    # mapping of top level `status` file items to a function accepting as
    # arguments the package.json element value and returning an iterable of key,
    # values Package Object to update
    field_mappers = [
        ('section', keywords_mapper),
        ('source', source_packages_mapper),
        #('depends', dependency_mapper),
    ]


    for source, func in field_mappers:
        logger.debug('parse: %(source)r, %(func)r' % locals())
        value = package_data.get(source) or None
        if value:
            func(value, package)
    
    # parties_mapper() need mutiple fields:
    parties_mapper(package_data, package)

    return package


def keywords_mapper(keyword, package):
    """
    Add `section` info as a list of keywords to a DebianPackage.
    """
    package.keywords = [keyword]
    return package


def source_packages_mapper(source, package):
    """
    Add `source` info as a list of `purl`s to a DebianPackage.
    """
    source_pkg_purl = PackageURL(
        type=package.type,
        name=source,
        namespace=package.namespace
    ).to_string()

    package.source_packages = [source_pkg_purl]

    return package

def parties_mapper(package_data, package):
    """
    add
    """
    parties = []

    maintainer = package_data.get('maintainer')
    orig_maintainer = package_data.get('original_maintainer')

    if maintainer:
        parties.append(models.Party(role='maintainer', name=maintainer))
    
    if orig_maintainer:
        parties.append(models.Party(role='original_maintainer', name=orig_maintainer))

    package.parties = parties

    return package
