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

from collections import namedtuple
import logging
import sys

import attr

from packagedcode import models
from packagedcode import nevra
from packagedcode.pyrpm.rpm import RPM
from packagedcode.utils import join_texts
import typecode.contenttype


TRACE = False


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))

# TODO: retrieve dependencies

# TODO: parse spec files see:
#  http://www.faqs.org/docs/artu/ch05s02.html#id2906931%29.)
#  http://code.activestate.com/recipes/436229-record-jar-parser/

RPM_TAGS = (
    'name',
    'epoch',
    'version',
    'release',
    'arch',
    'os',
    'summary',
    # the full description is often a long text
    'description',
    'distribution',
    'vendor',
    'license',
    'packager',
    'group',
    'patch',
    'url',
    'source_rpm',
    'source_package',
    'dist_url',
    'bin_or_src',
)

RPMInfo = namedtuple('RPMInfo', list(RPM_TAGS))


def tags(location, include_desc=False):
    """
    Return a dictionary of RPM tags for the file at location or an empty
    dictionary. Include the long RPM description value if include_desc is True.
    """
    T = typecode.contenttype.get_type(location)
    if 'rpm' not in T.filetype_file.lower():
        return {}

    with open(location, 'rb') as rpmf:
        rpm = RPM(rpmf)
        tags = rpm.tags()

        # this is not a real 'tag' but some header flag, let's treat it as a
        # tag for our purpose
        tags['bin_or_src'] = 'bin' if rpm.binary else 'src'

        # we encode in UTF8 by default and avoid errors with a replacement
        # utf-8 should be the standard for RPMs, though for older rpms mileage
        # may vary
        tag_map = {t: unicode(tags[t], 'UTF8', 'replace') for t in RPM_TAGS}
        if not include_desc:
            tag_map['description'] = u''
        return tag_map


def info(location, include_desc=False):
    """
    Return a namedtuple of RPM tags for the file at location or None. Include
    the long RPM description value if include_desc is True.
    """
    tgs = tags(location, include_desc)
    return tgs and RPMInfo(**tgs) or None


class EVR(namedtuple('EVR', 'epoch version release')):
    """
    The RPM Epoch, Version, Release tuple.
    """

    # note: the order of the named tuple is the sort order.
    # But for creation we put the rarely used epoch last
    def __new__(self, version, release=None, epoch=None):
        if epoch and epoch.strip() and not epoch.isdigit():
            raise ValueError('Invalid epoch: must be a number or empty.')
        if not version:
            raise ValueError('Version is required: {}'.format(repr(version)))

        return super(EVR, self).__new__(EVR, epoch, version, release)

    def __str__(self, *args, **kwargs):
        return self.to_string()

    def to_string(self):
        if self.release:
            vr = '-'.join([self.version, self.release])
        else:
            vr = self.version

        if self.epoch:
            vr = ':'.join([self.epoch, vr])
        return vr


@attr.s()
class RpmPackage(models.Package):
    metafiles = ('*.spec',)
    extensions = ('.rpm', '.srpm', '.mvl', '.vip',)
    filetypes = ('rpm ',)
    mimetypes = ('application/x-rpm',)

    default_type = 'rpm'

    default_web_baseurl = None
    default_download_baseurl = None
    default_api_baseurl = None

    @classmethod
    def recognize(cls, location):
        return parse(location)


def parse(location):
    """
    Return an RpmPackage object for the file at location or None if
    the file is not an RPM.
    """
    infos = info(location, include_desc=True)
    if TRACE: logger_debug('parse: infos', infos)
    if not infos:
        return

    name = infos.name

    try:
        epoch = infos.epoch and int(infos.epoch) or None
    except ValueError:
        epoch = None
    evr = EVR(
        version=infos.version or None,
        release=infos.release or None,
        epoch=epoch).to_string()

    qualifiers = {}
    os = infos.os
    if os and os != 'linux':
        qualifiers['os'] = os

    arch = infos.arch
    if arch:
        qualifiers['arch'] = arch

    source_packages = []
    if infos.source_rpm:
        src_epoch, src_name, src_version, src_release, src_arch = nevra.from_name(infos.source_rpm)
        src_evr = EVR(src_version, src_release, src_epoch).to_string()
        src_qualifiers = {}
        if src_arch:
            src_qualifiers['arch'] = src_arch

        src_purl = models.PackageURL(
            type=RpmPackage.default_type,
            name=src_name,
            version=src_evr,
            qualifiers=src_qualifiers
        ).to_string()

        if TRACE: logger_debug('parse: source_rpm', src_purl)
        source_packages = [src_purl]

    parties = []
    if infos.distribution:
        parties.append(models.Party(name=infos.distribution, role='distributor'))
    if infos.vendor:
        parties.append(models.Party(name=infos.vendor, role='vendor'))

    description = join_texts(infos.summary , infos.description)

    if TRACE: 
        data = dict(
            name=name,
            version=evr,
            description=description or None,
            homepage_url=infos.url or None,
            parties=parties,
            declared_licensing=infos.license or None,
            source_packages=source_packages
        )
        logger_debug('parse: data to create a package:\n', data)

    package = RpmPackage(
        name=name,
        version=evr,
        description=description or None,
        homepage_url=infos.url or None,
        parties=parties,
        declared_licensing=infos.license or None,
        source_packages=source_packages
    )
    if TRACE: 
        logger_debug('parse: created package:\n', package)

    return package
