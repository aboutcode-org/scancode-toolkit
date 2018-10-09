#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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
from __future__ import division
from __future__ import unicode_literals

from os.path import abspath
from os.path import basename
from os.path import dirname
from os.path import isdir
from os.path import isfile
from os.path import join
import sys

from spdx.checksum import Algorithm
from spdx.creationinfo import Tool
from spdx.document import Document
from spdx.document import License
from spdx.document import ExtractedLicense
from spdx.file import File
from spdx.package import Package
from spdx.utils import NoAssert
from spdx.utils import SPDXNone
from spdx.version import Version

from formattedcode.utils import get_headings
from plugincode.output import output_impl
from plugincode.output import OutputPlugin
from scancode import CommandLineOption
from scancode import FileOptionType
from scancode import OUTPUT_GROUP

# Python 2 and 3 support
try:
    # Python 2
    unicode
    str_orig = str
    bytes = str  # NOQA
    str = unicode  # NOQA
except NameError:
    # Python 3
    unicode = str  # NOQA

# Tracing flags
TRACE = False
TRACE_DEEP = False


def logger_debug(*args):
    pass


if TRACE or TRACE_DEEP:
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, unicode)
                                     and a or repr(a) for a in args))

"""
Output plugins to write scan results in SPDX format.
"""

_spdx_list_is_patched = False


def _patch_license_list():
    """
    Patch the SPDX library license list to match the list of ScanCode known SPDX
    licenses.
    """
    global _spdx_list_is_patched
    if not _spdx_list_is_patched:
        from spdx.config import LICENSE_MAP
        from licensedcode.models import load_licenses
        licenses = load_licenses(with_deprecated=True)
        spdx_licenses = get_by_spdx(licenses.values())
        LICENSE_MAP.update(spdx_licenses)
        _spdx_list_is_patched = True


def get_by_spdx(licenses):
    """
    Return a mapping of {spdx_key: license object} given a sequence of License
    objects.
    """
    spdx_licenses = {}
    for lic in licenses:
        if not (lic.spdx_license_key or lic.other_spdx_license_keys):
            continue

        if lic.spdx_license_key:
            name = lic.name
            slk = lic.spdx_license_key
            spdx_licenses[slk] = name
            spdx_licenses[name] = slk

            for other_spdx in lic.other_spdx_license_keys:
                if not (other_spdx and other_spdx.strip()):
                    continue
                slk = other_spdx
                spdx_licenses[slk] = name
                spdx_licenses[name] = slk

    return spdx_licenses


@output_impl
class SpdxTvOutput(OutputPlugin):

    options = [
        CommandLineOption(('--spdx-tv',),
            type=FileOptionType(mode='wb', lazy=False),
            metavar='FILE',
            requires=['info'],
            help='Write scan output as SPDX Tag/Value to FILE.',
            help_group=OUTPUT_GROUP)
    ]

    def is_enabled(self, spdx_tv, info, **kwargs):
        return spdx_tv and info

    def process_codebase(self, codebase, spdx_tv, **kwargs):
        input = kwargs.get('input', '')  # NOQA
        results = self.get_results(codebase, **kwargs)
        _files_count, version, notice, _scan_start, _options = get_headings(codebase)
        write_spdx(spdx_tv, results, version, notice, input, as_tagvalue=True)


@output_impl
class SpdxRdfOutput(OutputPlugin):

    options = [
        CommandLineOption(('--spdx-rdf',),
            type=FileOptionType(mode='wb', lazy=False),
            metavar='FILE',
            requires=['info'],
            help='Write scan output as SPDX RDF to FILE.',
            help_group=OUTPUT_GROUP)
    ]

    def is_enabled(self, spdx_rdf, info, **kwargs):
        return spdx_rdf and info

    def process_codebase(self, codebase, spdx_rdf, **kwargs):
        input = kwargs.get('input', '')  # NOQA
        results = self.get_results(codebase, **kwargs)
        _files_count, version, notice, _scan_start, _options = get_headings(codebase)
        write_spdx(spdx_rdf, results, version, notice, input, as_tagvalue=False)


def write_spdx(output_file, results, scancode_version, scancode_notice,
               input_file, as_tagvalue=True):
    """
    Write scan output as SPDX Tag/value or RDF.
    """
    _patch_license_list()

    absinput = abspath(input_file)

    if isdir(absinput):
        input_path = absinput
    else:
        input_path = dirname(absinput)

    doc = Document(Version(2, 1), License.from_identifier('CC0-1.0'))
    doc.comment = scancode_notice

    doc.creation_info.add_creator(Tool('ScanCode ' + scancode_version))
    doc.creation_info.set_created_now()

    package = doc.package = Package(
        name=basename(input_path),
        download_location=NoAssert()
    )

    # Use a set of unique copyrights for the package.
    package.cr_text = set()

    all_files_have_no_license = True
    all_files_have_no_copyright = True

    # FIXME: this should walk the codebase instead!!!
    for file_data in results:
        # Construct the absolute path in case we need to access the file
        # to calculate its SHA1.
        file_entry = File(join(input_path, file_data.get('path')))

        file_sha1 = file_data.get('sha1')
        if not file_sha1:
            if isfile(file_entry.name):
                # Calculate the SHA1 in case it is missing, e.g. for empty files.
                file_sha1 = file_entry.calc_chksum()
            else:
                # Skip directories.
                continue

        # Restore the relative file name as that is what we want in
        # SPDX output (with explicit leading './').
        file_entry.name = './' + file_data.get('path')
        file_entry.chk_sum = Algorithm('SHA1', file_sha1)

        file_licenses = file_data.get('licenses')
        if file_licenses:
            all_files_have_no_license = False
            for file_license in file_licenses:
                spdx_id = file_license.get('spdx_license_key')
                if spdx_id:
                    # spdx_id = spdx_id.rstrip('+')
                    spdx_license = License.from_identifier(spdx_id)
                else:
                    license_key = file_license.get('key')
                    # FIXME: we should prefix this with ScanCode-
                    licenseref_id = 'LicenseRef-' + license_key
                    spdx_license = ExtractedLicense(licenseref_id)
                    spdx_license.name = file_license.get('short_name')
                    comment = ('See details at https://github.com/nexB/scancode-toolkit'
                               '/blob/develop/src/licensedcode/data/licenses/%s.yml\n' % license_key)
                    spdx_license.comment = comment
                    text = file_license.get('matched_text')
                    # always set some text, even if we did not extract the matched text
                    if not text:
                        text = comment
                    spdx_license.text = text
                    doc.add_extr_lic(spdx_license)

                # Add licenses in the order they appear in the file. Maintaining the order
                # might be useful for provenance purposes.
                file_entry.add_lics(spdx_license)
                package.add_lics_from_file(spdx_license)

        elif file_licenses is None:
            all_files_have_no_license = False
            file_entry.add_lics(NoAssert())

        else:
            file_entry.add_lics(SPDXNone())

        file_entry.conc_lics = NoAssert()

        file_copyrights = file_data.get('copyrights')
        if file_copyrights:
            all_files_have_no_copyright = False
            file_entry.copyright = []
            for file_copyright in file_copyrights:
                file_entry.copyright.append(file_copyright.get('value'))

            package.cr_text.update(file_entry.copyright)

            # Create a text of copyright statements in the order they appear in the file.
            # Maintaining the order might be useful for provenance purposes.
            file_entry.copyright = '\n'.join(file_entry.copyright) + '\n'

        elif file_copyrights is None:
            all_files_have_no_copyright = False
            file_entry.copyright = NoAssert()

        else:
            file_entry.copyright = SPDXNone()

        package.add_file(file_entry)

    if len(package.files) == 0:
        if as_tagvalue:
            output_file.write("# No results for package '{}'.\n".format(package.name))
        else:
            output_file.write("<!-- No results for package '{}'. -->\n".format(package.name))

    # Remove duplicate licenses from the list for the package.
    unique_licenses = set(package.licenses_from_files)
    if not len(package.licenses_from_files):
        if all_files_have_no_license:
            package.licenses_from_files = [SPDXNone()]
        else:
            package.licenses_from_files = [NoAssert()]
    else:
        # List license identifiers alphabetically for the package.
        package.licenses_from_files = sorted(unique_licenses, key=lambda x: x.identifier)

    if len(package.cr_text) == 0:
        if all_files_have_no_copyright:
            package.cr_text = SPDXNone()
        else:
            package.cr_text = NoAssert()
    else:
        # Create a text of alphabetically sorted copyright
        # statements for the package.
        package.cr_text = '\n'.join(sorted(package.cr_text)) + '\n'

    package.verif_code = doc.package.calc_verif_code()
    package.license_declared = NoAssert()
    package.conc_lics = NoAssert()

    if as_tagvalue:
        from spdx.writers.tagvalue import write_document  # NOQA
    else:
        from spdx.writers.rdf import write_document  # NOQA

    # The spdx-tools write_document returns either:
    # - unicode for tag values
    # - UTF8-encoded bytes for rdf because somehow the rdf and xml
    #   libraries do the encoding
    # The file passed by ScanCode for output is always opened in binary
    # mode and needs to receive UTF8-encoded bytes.
    # Therefore in one case we do nothing (rdf) and in the other case we
    # encode to UTF8 bytes.

    if package.files:
        from StringIO import StringIO
        spdx_output = StringIO()
        write_document(doc, spdx_output, validate=False)
        result = spdx_output.getvalue()
        if as_tagvalue:
            result = result.encode('utf-8')
        output_file.write(result)
