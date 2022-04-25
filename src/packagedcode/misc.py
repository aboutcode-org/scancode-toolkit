#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from packagedcode import models

"""
Various package data file formats to implment.
"""

# Package types
# NOTE: this is somewhat redundant with extractcode archive handlers
# yet the purpose and semantics are rather different here

# TODO: parse me!!!
# TODO: add missing URLs and descriptions


class JavaJarHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'java_jar'
    # NOTE: there are a few rare cases where a .zip can be a JAR.
    path_patterns = ('*.jar',)
    filetypes = ('zip archive', 'java archive',)
    description = 'JAR Java Archive'
    documentation_url = 'https://en.wikipedia.org/wiki/JAR_(file_format)'


class IvyXmlHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'ant_ivy_xml'
    path_patterns = ('*/ivy.xml',)
    default_package_type = 'ivy'
    default_primary_language = 'Java'
    description = 'Ant IVY dependency file'
    documentation_url = 'https://ant.apache.org/ivy/history/latest-milestone/ivyfile.html'


class JavaWarHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'java_war_archive'
    path_patterns = ('*.war',)
    filetypes = ('zip archive',)
    default_package_type = 'war'
    default_primary_language = 'Java'
    description = 'Java Web Application Archive'
    documentation_url = 'https://en.wikipedia.org/wiki/WAR_(file_format)'


class JavaWarWebXmlHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'java_war_web_xml'
    path_patterns = ('*/WEB-INF/web.xml',)
    filetypes = ('zip archive',)
    default_package_type = 'war'
    default_primary_language = 'Java'
    description = 'Java WAR web/xml'
    documentation_url = 'https://en.wikipedia.org/wiki/WAR_(file_format)'


class JavaEarHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'java_ear_archive'
    default_package_type = 'ear'
    default_primary_language = 'Java'
    path_patterns = ('*.ear',)
    filetypes = ('zip archive',)
    description = 'Java EAR Enterprise application archive'
    documentation_url = 'https://en.wikipedia.org/wiki/EAR_(file_format)'


class JavaEarAppXmlHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'java_ear_application_xml'
    default_package_type = 'ear'
    default_primary_language = 'Java'
    path_patterns = ('*/META-INF/application.xml',)
    description = 'Java EAR application.xml'
    documentation_url = 'https://en.wikipedia.org/wiki/EAR_(file_format)'


class Axis2MarModuleXmlHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'axis2_module_xml'
    path_patterns = ('*/meta-inf/module.xml',)
    default_package_type = 'axis2'
    default_primary_language = 'Java'
    description = 'Apache Axis2 module.xml'
    documentation_url = 'https://axis.apache.org/axis2/java/core/docs/modules.html'


class Axis2MarArchiveHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'axis2_mar'
    path_patterns = ('*.mar',)
    filetypes = ('zip archive',)
    default_package_type = 'axis2'
    default_primary_language = 'Java'
    description = 'Apache Axis2 module archive'
    documentation_url = 'https://axis.apache.org/axis2/java/core/docs/modules.html'


class JBossSarHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'jboss_sar'
    path_patterns = ('*.sar',)
    filetypes = ('zip archive',)
    default_package_type = 'jboss-service'
    default_primary_language = 'Java'
    description = 'JBOSS service archive'
    documentation_url = 'https://docs.jboss.org/jbossas/docs/Server_Configuration_Guide/4/html/ch02s01.html'


class JBossServiceXmlHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'jboss_service_xml'
    path_patterns = ('*/meta-inf/jboss-service.xml',)
    default_package_type = 'jboss-service'
    default_primary_language = 'Java'
    description = 'JBOSS service.xml'
    documentation_url = 'https://docs.jboss.org/jbossas/docs/Server_Configuration_Guide/4/html/ch02s01.html'


class MeteorPackageHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'meteor_package'
    path_patterns = ('*/package.js',)
    default_package_type = 'meteor'
    default_primary_language = 'JavaScript'
    description = 'Meteor package.js'
    documentation_url = 'https://docs.meteor.com/api/packagejs.html'


class CpanManifestHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'cpan_manifest'
    path_patterns = ('*/MANIFEST',)
    default_package_type = 'cpan'
    default_primary_language = 'Perl'
    description = 'CPAN Perl module MANIFEST'
    documentation_url = 'https://metacpan.org/pod/Module::Manifest'


class CpanMakefilePlHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'cpan_makefile'
    path_patterns = ('*/Makefile.PL',)
    default_package_type = 'cpan'
    default_primary_language = 'Perl'
    description = 'CPAN Perl Makefile.PL'
    documentation_url = 'https://www.perlmonks.org/?node_id=128077'

# http://blogs.perl.org/users/neilb/2017/04/an-introduction-to-distribution-metadata.html
#     Version 2+ data is what you’ll find in META.json
#     Version 1.4 data is what you’ll find in META.yml


class CpanMetaYmlHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'cpan_meta_yml'
    path_patterns = ('*/META.yml',)
    default_package_type = 'cpan'
    default_primary_language = 'Perl'
    description = 'CPAN Perl META.yml'
    documentation_url = 'https://metacpan.org/pod/CPAN::Meta::YAML'


class CpanMetaJsonHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'cpan_meta_json'
    path_patterns = ('*/META.json',)
    default_package_type = 'cpan'
    default_primary_language = 'Perl'
    description = 'CPAN Perl META.json'
    documentation_url = 'https://metacpan.org/pod/Parse::CPAN::Meta'


class CpanDistIniHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'cpan_dist_ini'
    path_patterns = ('*/dist.ini',)
    default_package_type = 'cpan'
    default_primary_language = 'Perl'
    description = 'CPAN Perl dist.ini'
    documentation_url = 'https://metacpan.org/pod/Dist::Zilla::Tutorial'


class AndroidAppArchiveHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'android_apk'
    default_package_type = 'android'
    default_primary_language = 'Java'
    path_patterns = ('*.apk',)
    filetypes = ('zip archive',)
    description = 'Android application package'
    documentation_url = 'https://en.wikipedia.org/wiki/Apk_(file_format)'


# see http://tools.android.com/tech-docs/new-build-system/aar-formats
class AndroidLibraryHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'android_aar_library'
    default_package_type = 'android_lib'
    default_primary_language = 'Java'

    # note: Apache Axis also uses AAR path_patterns for plain Jars.
    # this could be decided based on internal structure
    path_patterns = ('*.aar',)
    filetypes = ('zip archive',)

    description = 'Android library archive'
    documentation_url = 'https://developer.android.com/studio/projects/android-library'


class MozillaExtensionHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'mozilla_xpi'
    path_patterns = ('*.xpi',)
    filetypes = ('zip archive',)
    default_package_type = 'mozilla'
    default_primary_language = 'JavaScript'
    description = 'Mozilla XPI extension'
    documentation_url = 'https://en.wikipedia.org/wiki/XPInstall'


class ChromeExtensionHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'chrome_crx'
    path_patterns = ('*.crx',)
    filetypes = ('zip archive',)
    default_package_type = 'chrome'
    default_primary_language = 'JavaScript'
    description = 'Chrome extension'
    documentation_url = 'https://chrome.google.com/extensions'


class IosAppIpaHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'ios_ipa'
    default_package_type = 'ios'
    default_primary_language = 'Objective-C'
    path_patterns = ('*.ipa',)
    filetypes = ('microsoft cabinet',)
    description = 'iOS package archive'
    documentation_url = 'https://en.wikipedia.org/wiki/.ipa'


class CabArchiveHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'microsoft_cabinet'
    default_package_type = 'cab'
    default_primary_language = 'C'
    path_patterns = ('*.cab',)
    filetypes = ('microsoft cabinet',)
    description = 'Microsoft cabinet archive'
    documentation_url = 'https://docs.microsoft.com/en-us/windows/win32/msi/cabinet-files'


class InstallShieldPackageHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'installshield_installer'
    default_package_type = 'installshield'
    path_patterns = ('*.exe',)
    filetypes = ('zip installshield',)
    description = 'InstallShield installer'
    documentation_url = 'https://www.revenera.com/install/products/installshield'


class NsisInstallerHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'nsis_installer'
    default_package_type = 'nsis'
    path_patterns = ('*.exe',)
    filetypes = ('nullsoft installer',)
    description = 'NSIS installer'
    documentation_url = 'https://nsis.sourceforge.io/Main_Page'


class SharArchiveHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'shar_shell_archive'
    default_package_type = 'shar'
    path_patterns = ('*.shar',)
    filetypes = ('posix shell script',)
    description = 'shell archive'
    documentation_url = 'https://en.wikipedia.org/wiki/Shar'


class AppleDmgHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'apple_dmg'
    default_package_type = 'dmg'
    path_patterns = ('*.dmg', '*.sparseimage',)
    description = ''
    documentation_url = ''


class IsoImageHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'iso_disk_image'
    default_package_type = 'iso'
    path_patterns = ('*.iso', '*.udf', '*.img',)
    filetypes = ('iso 9660 cd-rom', 'high sierra cd-rom',)
    description = 'ISO disk image'
    documentation_url = 'https://en.wikipedia.org/wiki/ISO_9660'


class SquashfsImageHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'squashfs_disk_image'
    default_package_type = 'squashfs'
    filetypes = ('squashfs',)
    description = 'Squashfs disk image'
    documentation_url = 'https://en.wikipedia.org/wiki/SquashFS'

# TODO: Add VM images formats(VMDK, OVA, OVF, VDI, etc) and Docker/other containers
