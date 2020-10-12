#
# Copyright (c) 2020 nexB Inc. and others. All rights reserved.
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

import logging

import attr

from commoncode import filetype
from packagedcode import models

from oelint_parser.cls_stash import Stash
from oelint_parser.cls_item import Variable

TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

@attr.s()
class BitbakePackage(models.Package):
    metafiles = ('*.bb',)
    default_type = 'bitbake'

    @classmethod
    def recognize(cls, location):
        yield parse(location)

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)


def is_bb_file(location):
    return (filetype.is_file(location)
            and location.lower().endswith(('.bb',)))

def parse(location):
    """
    Return a Package object from an ABOUT file or None.
    """
    if not is_bb_file(location):
        return

    _stash = Stash()
    # add any bitbake like file
    _stash.AddFile(location)
    
    # Resolves proper cross file dependencies
    _stash.Finalize()

    # get all variables of the name PV from all files
    package_dict = {}
    for item in _stash.GetItemsFor():
        try:
            # Create a package dictionary with VarName as the key and
            # VarValueStripped as the value
            name = item.VarName
            value = item.VarValueStripped
            try:
                if package_dict[name]:
                    package_dict[name] += '\n' + value
            except:
                package_dict[name] = value
        except:
            # Continue to see if there is any VarName value until the end of
            # the file
            continue

    return build_package(package_dict)


def build_package(package_dict):
    """
    Return a Package built from `package_dict` obtained from the .bb files.
    """
    # Initialization
    name = None
    version = None
    description = None
    homepage_url = None
    download_url = None
    sha1 = None
    md5 = None
    sha256 = None
    sha512 = None
    declared_license = None
    dependencies = None
    if 'PN' in package_dict:
        name = package_dict['PN']
    if 'PV' in package_dict:
        version = package_dict['PV']
    if 'DESCRIPTION' in package_dict:
        description = package_dict['DESCRIPTION']
    if 'HOMEPAGE' in package_dict:
        homepage_url = package_dict['HOMEPAGE']
    if 'PREMIRRORS' in package_dict:
        download_url = package_dict['PREMIRRORS']
    #The item.VarName for SRC_URI[*] from the parser are SRC_URI
    #Therefore, I cannot differentiate md5,sha1, or src file location reference
    # Entered an issue ticket: https://github.com/priv-kweihmann/oelint-parser/issues/3
    """
    if 'SRC_URI[sha1sum]' in package_dict:
        sha1 = package_dict['SRC_URI[sha1sum]']
    if 'SRC_URI[md5sum]' in package_dict:
        md5 = package_dict['SRC_URI[md5sum]']
    if 'SRC_URI[sha256sum]' in package_dict:
        sha256 = package_dict['SRC_URI[sha256sum]']
    if 'SRC_URI[sha512sum]' in package_dict:
        sha512 = package_dict['SRC_URI[sha512sum]']
    """
    if 'LICENSE' in package_dict:
        declared_license = package_dict['LICENSE']
    if 'DEPENDS' in package_dict:
        if dependencies:
            dependencies += '\n' + package_dict['DEPENDS']
        else:
            dependencies = package_dict['DEPENDS']
    # There are some RDEPENDS_* fields such as "RDEPENDS_${PN}" which I need to
    # check with the substring
    for d in package_dict:
        if 'RDEPENDS' in d:
            if dependencies:
                dependencies += '\n' + package_dict[d]
            else:
                dependencies = package_dict[d]

    return BitbakePackage(
        type='bitbake',
        name=name,
        version=version,
        description=description,
        homepage_url=homepage_url,
        download_url=download_url,
        sha1=sha1,
        md5=md5,
        sha256=sha256,
        sha512=sha512,
        declared_license=declared_license,
        dependencies=dependencies
    )
