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

from datetime import datetime
import email
import io
import os
from os import path
import posixpath
import re
import xmltodict

import attr
from license_expression import Licensing
from packageurl import PackageURL

from commoncode.datautils import List
from packagedcode import models
from packagedcode import licensing
from textcode.analysis import as_unicode


@attr.s()
class RpmBasePackage(models.Package):
    # FIXME
    # Please review if the extensions and default_type are correct
    extensions = ('.rpm',)
    default_type = 'rpm'

    installed_files = List(
        item_type=models.PackageFile,
        label='installed files',
        help='List of files installed by this package.')

    def compute_normalized_license(self):
        _declared, detected = detect_declared_license(self.declared_license)
        return detected

    def to_dict(self, _detailed=False, **kwargs):
        data = models.Package.to_dict(self, **kwargs)
        if _detailed:
            #################################################
            data['installed_files'] = [istf.to_dict() for istf in (self.installed_files or [])]
            #################################################
        else:
            #################################################
            # remove temporary fields
            data.pop('installed_files', None)
            #################################################
        return data


def get_installed_packages(root_dir, **kwargs):
    """
    Given a directory to a rootfs, yield a RpmBasePackage and a list of `installed_files`
    (path, md5sum) tuples.
    """
    installed_file_loc = path.join(root_dir, 'var/lib/rpm/Packages')
    if not path.exists(installed_file_loc):
        return
    # FIXME
    # This code will not work as we need to parse/convert the "Packages" with
    # the rpm command.
    # i.e.
    # rpm --query --all --qf '[%{*:xml}\n]' --dbpath=<path to RPM DB directory 
    #                                typically some /var/lib/rpm/> > ~/rpm.xml.txt
    # See https://github.com/nexB/scancode.io/issues/6
    for package in parse_rpm_db(installed_file_loc):
        yield package


def parse_rpm_db(location):
    """
    Yield RpmBasePackage objects from an installed database file at `location`
    or None. Typically found at '/var/lib/rpm/Packages' in an RPM
    installation.
    """
    if not path.exists(location):
        return

    with open(location, 'rb') as f:
        installed = as_unicode(f.read())

    if installed:
        parsed_result = []
        # each paragraph is separated by <rpmHeader>
        sections = installed.split('<rpmHeader>')
        for section in sections:
            if section:
                result = '<rpmHeader>' + section
                parsed_result.append(xmltodict.parse(result))

        for result in parsed_result:
            content_dict = result['rpmHeader']['rpmTag']
            fields = []
            for dict in content_dict:
                # The keys should be '@name' and "type" (such as string/integer etc)
                # This is the convention from xmltodict
                assert len(dict.keys()) == 2
                values = []
                # The format of the dict.items() is something like
                # ('@name', 'sample'), ('string', 'sample context')
                # We want to extract the "real" value and make it a tuple
                # i.e. ('sample', 'sample context')
                # and therefore we will get the item[1] at the below
                for item in list(dict.items()):
                    values.append(item[1])
                fields.append(tuple(values))
            yield build_package(fields)


# Note handlers MUST accept **kwargs as they also receive the current data
# being processed so far as a processed_data kwarg, but most do not use it


def build_package(package_fields):
    """
    Return an RpmBasePackage object from a `package_fields` list of (name, value)
    tuples.
    """
    # mapping of actual Package field name -> value that have been converted to the expected format
    converted_fields = {}
    for name, value in package_fields:
        handler = package_short_field_handlers.get(name)
        if handler:
            converted = handler(value, **converted_fields)
            converted_fields.update(converted)

    # construct the package: we ignore unknown as we added a few technical fields
    package = RpmBasePackage.create(ignore_unknown=True, **converted_fields)
    return package


def name_value_str_handler(name):
    """
    Return a generic handler for plain string fields.
    """

    def handler(value, **kwargs):
        return {name: value}

    return handler


def license_handler(value, **kwargs):
    """
    Return a normalized declared license and a detected license expression.
    """
    declared, detected = detect_declared_license(value)
    return {
        'declared_license': declared,
        'license_expression': detected,
    }


def size_handler(value, **kwargs):
    return {'size': int(value)}


def arch_handler(value, **kwargs):
    """
    Return a Package URL qualifier for the arch.
    """
    return {'qualifiers': 'arch={}'.format(value)}


def checksum_handler(value, **kwargs):
    """
    Return a list which contains the MD5 hash
    """
    return {'current_file': value}


def dir_index_handler(value, current_file, **kwargs):
    """
    Return a list of tuples with (dirindexes, md5)
    """
    return {'current_file': list(zip(value, current_file))}


def basename_handler(value, current_file, **kwargs):
    """
    Return a list of tuples with (dirindexes, md5, basename)
    """
    data = []
    for index, file in enumerate(current_file):
        basename = (value[index],)
        data.append(file + basename)
    return {'current_file': data}


def dirname_handler(value, current_file, **kwargs):
    """
    Update the current_file with joining the correct dir and basename
    along with the md5 value.
    Add to installed_files
    """
    installed_files = []
    for file in current_file:
        dirindexes, md5, basename = file
        dir = value[int(dirindexes)]
        c_file = models.PackageFile(path=posixpath.join(dir, basename))
        c_file.md5 = md5
        installed_files.append(c_file)
    return {'installed_files': installed_files}

# mapping of:
# - the package field one letter name in the installed db,
# - an handler for that field
package_short_field_handlers = {

    ############################################################################
    # per-package fields
    ############################################################################

    'Name': name_value_str_handler('name'),
    'Version': name_value_str_handler('version'),
    'Description': name_value_str_handler('description'),
    'Sha1header': name_value_str_handler('sha1'),
    'Url': name_value_str_handler('homepage_url'),
    'License': license_handler,
    'Arch':  arch_handler,
    'Size': size_handler,

    ############################################################################
    # ignored per-package fields. from here on, these fields are not used yet
    ############################################################################
    #  '(unknown)'
    #  'Archivesize'
    #  'Buildhost'
    #  'Buildtime'
    #  'Changelogname'
    #  'Changelogtext'
    #  'Changelogtime'
    #  'Classdict'
    #  'Conflictflags'
    #  'Conflictname'
    #  'Conflictversion'
    #  'Cookie'
    #  'Dependsdict'
    #  'Distribution'
    #  'Dsaheader'
    #  'Epoch'
    #  'Fileclass'
    #  'Filecolors'
    #  'Filecontexts'
    #  'Filedependsn'
    #  'Filedependsx'
    #  'Filedevices'
    #  'Fileflags'
    #  'Filegroupname'
    #  'Fileinodes'
    #  'Filelangs'
    #  'Filelinktos'
    #  'Filemodes'
    #  'Filemtimes'
    #  'Filerdevs'
    #  'Filesizes'
    #  'Filestates'
    #  'Fileusername'
    #  'Fileverifyflags'
    #  'Group'
    #  'Installcolor'
    #  'Installtid'
    #  'Installtime'
    #  'Instprefixes'
    #  'Obsoleteflags'
    #  'Obsoletename'
    #  'Obsoleteversion'
    #  'Optflags'
    #  'Os'
    #  'Packager'
    #  'Payloadcompressor'
    #  'Payloadflags'
    #  'Payloadformat'
    #  'Platform'
    #  'Postin'
    #  'Postinprog'
    #  'Postun'
    #  'Postunprog'
    #  'Prefixes'
    #  'Prein'
    #  'Preinprog']
    #  'Preun'
    #  'Preunprog'
    #  'Provideflags'
    #  'Providename'
    #  'Provideversion'
    #  'Release'
    #  'Requireflags'
    #  'Requirename'
    #  'Requireversion'
    #  'Rpmversion'
    #  'Siggpg'
    #  'Sigmd5'
    #  'Sigsize'
    #  'Sourcerpm'
    #  'Summary'
    #  'Triggerflags'
    #  'Triggerindex'
    #  'Triggername'
    #  'Triggerscriptprog'
    #  'Triggerscripts'
    #  'Triggerversion'
    #  'Vendor'
    #  'Headeri18ntable'
    ############################################################################

    ############################################################################
    # per-file fields
    ############################################################################
    'Filedigests': checksum_handler,
    'Dirindexes': dir_index_handler,
    'Basenames': basename_handler,
    'Dirnames': dirname_handler,
    ############################################################################
}

############################################################################
# FIXME: this license detection code is copied from debian_copyright.py
############################################################################


def detect_declared_license(declared):
    """
    Return a tuple of (declared license, detected license expression) from a
    declared license. Both can be None.
    """
    declared = normalize_and_cleanup_declared_license(declared)
    if not declared:
        return None, None

    # apply multiple license detection in sequence
    detected = detect_using_name_mapping(declared)
    if detected:
        return declared, detected

    # cases of using a comma are for an AND
    normalized_declared = declared.replace(',', ' and ')
    detected = models.compute_normalized_license(normalized_declared)
    return declared, detected


def normalize_and_cleanup_declared_license(declared):
    """
    Return a cleaned and normalized declared license.
    """
    declared = declared or ''
    # there are few odd cases of license fileds starting with a colon or #
    declared = declared.strip(': \t#')
    # normalize spaces
    declared = ' '.join(declared.split())
    return declared


def detect_using_name_mapping(declared):
    """
    Return a license expression detected from a `declared` license string.
    """
    declared = declared.lower()
    detected = get_declared_to_detected().get(declared)
    if detected:
        licensing = Licensing()
        return str(licensing.parse(detected, simple=True))


_DECLARED_TO_DETECTED = None


def get_declared_to_detected(data_file=None):
    """
    Return a mapping of declared to detected license expression cached and
    loaded from a tab-separated text file, all lowercase, normalized for spaces.

    This data file is from license keys used in APKINDEX files and has been
    derived from a large collection of most APKINDEX files released by Alpine
    since circa Alpine 2.5.
    """
    global _DECLARED_TO_DETECTED
    if _DECLARED_TO_DETECTED:
        return _DECLARED_TO_DETECTED

    _DECLARED_TO_DETECTED = {}
    if not data_file:
        data_file = path.join(path.dirname(__file__), 'alpine_licenses.txt')
    with io.open(data_file, encoding='utf-8') as df:
        for line in df:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            decl, _, detect = line.partition('\t')
            if detect and detect.strip():
                decl = decl.strip()
                _DECLARED_TO_DETECTED[decl] = detect
    return _DECLARED_TO_DETECTED
