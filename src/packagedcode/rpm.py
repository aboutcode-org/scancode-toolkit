#
# Copyright (c) 2016 nexB Inc. and others. All rights reserved.
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
import string

import typecode.contenttype

from packagedcode import models
from packagedcode import nevra
from packagedcode.pyrpm.rpm import RPM

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
    def __new__(self, version, release, epoch=None):
        if epoch and epoch.strip() and not epoch.isdigit():
            raise models.ValidationError('Invalid epoch: must be a number or empty.')

        return super(EVR, self).__new__(EVR, epoch, version, release)


class RPMVersionType(models.BaseType):
    """
    RPM versions are composed of a (mostly) hidden epoch, a version and release.
    The release may be further split in build numbers.
    """

    def __init__(self, **kwargs):
        super(RPMVersionType, self).__init__(**kwargs)

    def validate_version(self, value):
        if value and not isinstance(value, EVR):
            raise models.ValidationError('RPM version must be an EVR tuple')

    def to_primitive(self, value, context=None):
        """
        Return an version string using RPM conventions.
        # FIXME: Handle Epochs
        """
        vr = u'-'.join([value.version, value.release])
        if context and context.get('with_epoch') and value.epoch:
            return u':'.join([value.epoch, vr])
        return vr

    def to_native(self, value):
        return value

    def _mock(self, context=None):
        version = models.random_string(1, string.digits)
        release = models.random_string(1, string.digits)
        return self.to_primitive(EVR(version, release), context)


class RPMRelatedPackage(models.RelatedPackage):
    type = models.StringType(default='RPM')
    version = RPMVersionType()

    class Options:
        fields_order = 'type', 'name', 'version', 'payload_type'


class RpmPackage(models.Package):
    metafiles = ('*.spec',)
    extensions = ('.rpm', '.srpm', '.mvl', '.vip',)
    filetypes = ('rpm ',)
    mimetypes = ('application/x-rpm',)
    repo_types = (models.repo_yum,)

    type = models.StringType(default='RPM')
    version = RPMVersionType()

    packaging = models.StringType(default=models.as_archive)
    related_packages = models.ListType(models.ModelType(RPMRelatedPackage))

    @classmethod
    def recognize(location):
        return parse(location)


def parse(location):
    """
    Return an RpmPackage object for the file at location or None if the file is
    not an RPM.
    """
    infos = info(location, include_desc=True)
    if not infos:
        return

    epoch = int(infos.epoch) if infos.epoch else None

    asserted_licenses = []
    if infos.license:
        asserted_licenses = [models.AssertedLicense(license=infos.license)]

    related_packages = []
    if infos.source_rpm:
        epoch, name, version, release, _arch = nevra.from_name(infos.source_rpm)
        evr = EVR(version, release, epoch)
        related_packages = [RPMRelatedPackage(name=name,
                                              version=evr,
                                              payload_type=models.payload_src)]

    package = RpmPackage(
        summary=infos.summary,
        description=infos.description,
        name=infos.name,
        version=EVR(version=infos.version, release=infos.release, epoch=epoch or None),
        homepage_url=infos.url,
        distributors=[models.Party(name=infos.distribution)],
        vendors=[models.Party(name=infos.vendor)],

        asserted_licenses=asserted_licenses,

        related_packages=related_packages
    )
    return package
