#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import, print_function

from collections import namedtuple

from packagedcode.models import AssertedLicense
from packagedcode.pyrpm.rpm import RPM
from packagedcode.pyrpm.rpm import RPMError

import typecode.contenttype

# TODO: retrieve dependencies

# TODO: parse spec files see:
#  http://www.faqs.org/docs/artu/ch05s02.html#id2906931%29.)
#  http://code.activestate.com/recipes/436229-record-jar-parser/

RPM_TAGS = ('name',
           'version',
           'release',
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
           'os',
           'arch',
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
    if not 'rpm' in T.filetype_file.lower():
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
    return RPMInfo(**tgs) if tgs else None


def parse(location):
    """
    Return a package object of RPM metadata.
    'location' is the file location.
    """
    from packagedcode.models import RpmPackage
    infos = tags(location, include_desc=True)
    asserted_license = AssertedLicense(license=infos['license'])
    package = RpmPackage(
                summary=infos['summary'],
                description=infos['description'],
                name=infos['name'],
                version=infos['version'],
                release=infos['release'],
                homepage_url=infos['url'],
                source_rpm=infos['source_rpm'],
                distributors=infos['distribution'],
                arch=infos['arch'],
                location=location,
                os=infos['os'],
                vendor=infos['vendor'],
                bin_or_src=infos['bin_or_src'],
                asserted_licenses=[asserted_license],)
    return package
