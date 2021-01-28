#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from collections import namedtuple
import logging
import sys

import attr

from packagedcode import models
from packagedcode import nevra
from packagedcode.pyrpm import RPM
from packagedcode.utils import build_description
import typecode.contenttype


TRACE = False


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))

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
    'url',
    'source_rpm',
    'dist_url',
    'is_binary',
)

RPMtags = namedtuple('RPMtags', list(RPM_TAGS))


def get_rpm_tags(location, include_desc=False):
    """
    Return an RPMtags object for the file at location or None.
    Include the long RPM description value if `include_desc` is True.
    """
    T = typecode.contenttype.get_type(location)

    if 'rpm' not in T.filetype_file.lower():
        return

    with open(location, 'rb') as rpmf:
        rpm = RPM(rpmf)
        tags = {k: v for k, v in rpm.to_dict().items() if k in RPM_TAGS}
        if not include_desc:
            tags['description'] = None
        return RPMtags(**tags)


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
        yield parse(location)


def parse(location):
    """
    Return an RpmPackage object for the file at location or None if
    the file is not an RPM.
    """
    tags = get_rpm_tags(location, include_desc=True)
    if TRACE: logger_debug('parse: tags', tags)
    if not tags:
        return

    name = tags.name

    try:
        epoch = tags.epoch and int(tags.epoch) or None
    except ValueError:
        epoch = None

    evr = EVR(
        version=tags.version or None,
        release=tags.release or None,
        epoch=epoch).to_string()

    qualifiers = {}
    os = tags.os
    if os and os.lower() != 'linux':
        qualifiers['os'] = os

    arch = tags.arch
    if arch:
        qualifiers['arch'] = arch

    source_packages = []
    if tags.source_rpm:
        src_epoch, src_name, src_version, src_release, src_arch = nevra.from_name(tags.source_rpm)
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
    if tags.distribution:
        parties.append(models.Party(name=tags.distribution, role='distributor'))
    if tags.vendor:
        parties.append(models.Party(name=tags.vendor, role='vendor'))

    description = build_description(tags.summary, tags.description)

    if TRACE:
        data = dict(
            name=name,
            version=evr,
            description=description or None,
            homepage_url=tags.url or None,
            parties=parties,
            declared_license=tags.license or None,
            source_packages=source_packages)
        logger_debug('parse: data to create a package:\n', data)

    package = RpmPackage(
        name=name,
        version=evr,
        description=description or None,
        homepage_url=tags.url or None,
        parties=parties,
        declared_license=tags.license or None,
        source_packages=source_packages)
    if TRACE:
        logger_debug('parse: created package:\n', package)

    return package
