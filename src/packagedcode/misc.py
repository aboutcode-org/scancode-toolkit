#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import logging
import os
import sys

import attr

from packagedcode.models import PackageData
from packagedcode.models import PackageDataFile

"""
Miscellaneous package data file formats.
"""

SCANCODE_DEBUG_PACKAGE_API = os.environ.get('SCANCODE_DEBUG_PACKAGE_API', False)

TRACE = False or SCANCODE_DEBUG_PACKAGE_API
TRACE_MERGING = False or SCANCODE_DEBUG_PACKAGE_API


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE or TRACE_MERGING:

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))

    logger_debug = print

# Package types
# NOTE: this is somewhat redundant with extractcode archive handlers
# yet the purpose and semantics are rather different here


@attr.s()
class JavaJar(PackageData, PackageDataFile):
    filename_patterns = ('META-INF/MANIFEST.MF',)
    extensions = ('.jar',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip',)
    default_type = 'jar'
    default_primary_language = 'Java'


@attr.s()
class JavaWar(PackageData, PackageDataFile):
    filename_patterns = ('WEB-INF/web.xml',)
    extensions = ('.war',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    default_type = 'war'
    default_primary_language = 'Java'


@attr.s()
class JavaEar(PackageData, PackageDataFile):
    filename_patterns = ('META-INF/application.xml', 'META-INF/ejb-jar.xml')
    extensions = ('.ear',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    default_type = 'ear'
    default_primary_language = 'Java'


@attr.s()
class Axis2Mar(PackageData, PackageDataFile):
    """Apache Axis2 module"""
    filename_patterns = ('META-INF/module.xml',)
    extensions = ('.mar',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    default_type = 'axis2'
    default_primary_language = 'Java'


@attr.s()
class JBossSar(PackageData, PackageDataFile):
    filename_patterns = ('META-INF/jboss-service.xml',)
    extensions = ('.sar',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    default_type = 'jboss'
    default_primary_language = 'Java'


@attr.s()
class MeteorPackage(PackageData, PackageDataFile):
    filename_patterns = ('package.js',)
    default_type = 'meteor'
    default_primary_language = 'JavaScript'


@attr.s()
class CpanModule(PackageData, PackageDataFile):
    filename_patterns = (
        '*.pod',
        # TODO: .pm is not a package manifest
        '*.pm',
        'MANIFEST',
        'Makefile.PL',
        'META.yml',
        'META.json',
        '*.meta',
        'dist.ini',)
    # TODO: refine me
    extensions = ('.tar.gz',)
    default_type = 'cpan'
    default_primary_language = 'Perl'


# TODO: refine me: Go packages are a mess but something is emerging
# TODO: move to and use godeps.py
@attr.s()
class Godep(PackageData, PackageDataFile):
    filename_patterns = ('Godeps',)
    default_type = 'golang'
    default_primary_language = 'Go'


@attr.s()
class AndroidApp(PackageData, PackageDataFile):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.apk',)
    default_type = 'android'
    default_primary_language = 'Java'


# see http://tools.android.com/tech-docs/new-build-system/aar-formats
@attr.s()
class AndroidLibrary(PackageData, PackageDataFile):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    # note: Apache Axis also uses AAR extensions for plain Jars.
    # this could be decided based on internal structure
    extensions = ('.aar',)
    default_type = 'android-lib'
    default_primary_language = 'Java'


@attr.s()
class MozillaExtension(PackageData, PackageDataFile):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.xpi',)
    default_type = 'mozilla'
    default_primary_language = 'JavaScript'


@attr.s()
class ChromeExtension(PackageData, PackageDataFile):
    filetypes = ('data',)
    mimetypes = ('application/octet-stream',)
    extensions = ('.crx',)
    default_type = 'chrome'
    default_primary_language = 'JavaScript'


@attr.s()
class IOSApp(PackageData, PackageDataFile):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.ipa',)
    default_type = 'ios'
    default_primary_language = 'Objective-C'


@attr.s()
class CabPackage(PackageData, PackageDataFile):
    filetypes = ('microsoft cabinet',)
    mimetypes = ('application/vnd.ms-cab-compressed',)
    extensions = ('.cab',)
    default_type = 'cab'


@attr.s()
class InstallShieldPackage(PackageData, PackageDataFile):
    filetypes = ('installshield',)
    mimetypes = ('application/x-dosexec',)
    extensions = ('.exe',)
    default_type = 'installshield'


@attr.s()
class NSISInstallerPackage(PackageData, PackageDataFile):
    filetypes = ('nullsoft installer',)
    mimetypes = ('application/x-dosexec',)
    extensions = ('.exe',)
    default_type = 'nsis'


@attr.s()
class SharPackage(PackageData, PackageDataFile):
    filetypes = ('posix shell script',)
    mimetypes = ('text/x-shellscript',)
    extensions = ('.sha', '.shar', '.bin',)
    default_type = 'shar'


@attr.s()
class AppleDmgPackage(PackageData, PackageDataFile):
    filetypes = ('zlib compressed',)
    mimetypes = ('application/zlib',)
    extensions = ('.dmg', '.sparseimage',)
    default_type = 'dmg'


@attr.s()
class IsoImagePackage(PackageData, PackageDataFile):
    filetypes = ('iso 9660 cd-rom', 'high sierra cd-rom',)
    mimetypes = ('application/x-iso9660-image',)
    extensions = ('.iso', '.udf', '.img',)
    default_type = 'iso'


@attr.s()
class SquashfsPackage(PackageData, PackageDataFile):
    filetypes = ('squashfs',)
    default_type = 'squashfs'

# TODO: Add VM images formats(VMDK, OVA, OVF, VDI, etc) and Docker/other containers
