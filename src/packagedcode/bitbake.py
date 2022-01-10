#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import logging

import attr
from oelint_parser.cls_stash import Stash
from oelint_parser.cls_item import Variable

from commoncode import filetype
from packagedcode import models

TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


@attr.s()
class BitbakePacakge(models.Package):
    default_type = 'bitbake'

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)

@attr.s()
class BitbakeBbManifest(BitbakePacakge, models.PackageManifest):
    file_patterns = ('*.bb',)
    extensions = ('.bb', '.bbclass',)

    @classmethod
    def is_manifest(cls, location):
        return (
            filetype.is_file(location)
            and location.lower().endswith(('.bb',))
        )

    @classmethod
    def recognize(cls, location):
        yield parse(location)


def parse(location):
    """
    Return a Package object from an BitBake file or None.
    """
    _stash = Stash()
    # add any bitbake like file
    _stash.AddFile(location)

    # Resolves proper cross file dependencies
    _stash.Finalize()

    # get all variables from all prsed files
    data = {}
    for item in _stash.GetItemsFor():
        try:
            # Create a package dictionary with VarName as the key and
            # VarValueStripped as the value
            name = item.VarName
            value = item.VarValueStripped
            try:
                if data[name]:
                    data[name] += '\n' + value
            except:
                data[name] = value
        except:
            # Continue to see if there is any VarName value until the end of
            # the file
            continue

    return build_package(data)


def build_package(data):
    """
    Return a Package built from Bake `data` mapping.
    """
    name = data.get('PN')
    version = data.get('PV')
    description = data.get('DESCRIPTION')
    homepage_url = data.get('HOMEPAGE')
    download_url = data.get('PREMIRRORS')
    declared_license = data.get('LICENSE')
    dependencies = data.get('DEPENDS', [])

    # The item.VarName for SRC_URI[*] from the parser are SRC_URI
    # Therefore, I cannot differentiate md5, sha1, or src file location reference
    # See: https://github.com/priv-kweihmann/oelint-parser/issues/3
    sha1 = data.get('SRC_URI[sha1sum]')
    md5 = data.get('SRC_URI[md5sum]')
    sha256 = data.get('SRC_URI[sha256sum]')
    sha512 = data.get('SRC_URI[sha512sum]')

    # There are some RDEPENDS_* fields such as "RDEPENDS_${PN}" which I need to
    # check with the substring
    # FIXME: we should create a DependentPackage
    for d in data:
        if d.startswith('RDEPENDS'):
            if dependencies:
                dependencies += '\n' + data[d]
            else:
                dependencies = data[d]

    return BitbakeBbManifest(
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
