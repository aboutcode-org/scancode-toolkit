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
from __future__ import division
from __future__ import unicode_literals

import os
from os.path import abspath

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

from plugincode.output import scan_output_writer


"""
Output plugins to write scan results in SPDX format.
"""

@scan_output_writer
def write_spdx_tag_value(files_count, version, notice, scanned_files, input, output_file, *args, **kwargs):
    """
    Write scan output formatted as SPDX Tag/Value.
    """
    write_spdx(version, notice, scanned_files, input, output_file, as_tagvalue=True)


@scan_output_writer
def write_spdx_rdf(files_count, version, notice, scanned_files, input, output_file, *args, **kwargs):
    """
    Write scan output formatted as SPDX RDF.
    """
    write_spdx(version, notice, scanned_files, input, output_file, as_tagvalue=False)


def write_spdx(version, notice, scanned_files, input, output_file, as_tagvalue=True):
    """
    Write scan output formatted as SPDX Tag/value or RDF.
    """
    absinput = abspath(input)

    if os.path.isdir(absinput):
        input_path = absinput
    else:
        input_path = os.path.dirname(absinput)

    doc = Document(Version(2, 1), License.from_identifier('CC0-1.0'))
    doc.comment = notice

    doc.creation_info.add_creator(Tool('ScanCode ' + version))
    doc.creation_info.set_created_now()

    package = doc.package = Package(
        name=os.path.basename(input_path),
        download_location=NoAssert()
    )

    # Use a set of unique copyrights for the package.
    package.cr_text = set()

    all_files_have_no_license = True
    all_files_have_no_copyright = True

    for file_data in scanned_files:
        # Construct the absolute path in case we need to access the file
        # to calculate its SHA1.
        file_entry = File(os.path.join(input_path, file_data.get('path')))

        file_sha1 = file_data.get('sha1')
        if not file_sha1:
            if os.path.isfile(file_entry.name):
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
                    comment = 'See details at https://github.com/nexB/scancode-toolkit/blob/develop/src/licensedcode/data/licenses/%s.yml\n' % license_key
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
                file_entry.copyright.extend(file_copyright.get('statements'))

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
        from spdx.writers.tagvalue import write_document
    else:
        from spdx.writers.rdf import write_document

    # The spdx-tools write_document returns either:
    # - unicode for tag values
    # - UTF8-encoded bytes for rdf because somehow the rd and xml
    #   libraries do the encoding
    # The file passed by ScanCode for output is alwasy opened in binary
    # mode and needs to receive UTF8-encoded bytes.
    # Therefore in one case we do nothing (rdf) and in the other case we
    # encode to UTF8 bytes.

    from StringIO import StringIO
    spdx_output = StringIO()
    write_document(doc, spdx_output, validate=True)
    result = spdx_output.getvalue()
    if as_tagvalue:
        result = result.encode('utf-8')
    output_file.write(result)
