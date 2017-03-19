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

from collections import OrderedDict
import os
from os.path import abspath

from formattedcode.format import as_template
from formattedcode.format import as_html_app
from formattedcode.format import create_html_app_assets
from formattedcode.format import HtmlAppAssetCopyWarning
from formattedcode.format import HtmlAppAssetCopyError


def write_formatted_output(scanners, files_count, version, notice, scanned_files, format, options, input, output_file, _echo):
    """
    Save scan results to file or screen.
    """

    if format == 'html':
        for template_chunk in as_template(scanned_files):
            try:
                output_file.write(template_chunk)
            except Exception as e:
                extra_context = 'ERROR: Failed to write output to HTML for: ' + repr(template_chunk)
                _echo(extra_context, fg='red')
                e.args += (extra_context,)
                raise e

    elif format == 'html-app':
        output_file.write(as_html_app(input, output_file))
        try:
            create_html_app_assets(scanned_files, output_file)
        except HtmlAppAssetCopyWarning:
            _echo('\nHTML app creation skipped when printing to stdout.', fg='yellow')
        except HtmlAppAssetCopyError:
            _echo('\nFailed to create HTML app.', fg='red')

    elif format == 'json' or format == 'json-pp':
        import simplejson as json

        meta = OrderedDict()
        meta['scancode_notice'] = notice
        meta['scancode_version'] = version
        meta['scancode_options'] = options
        meta['files_count'] = files_count
        meta['files'] = scanned_files
        if format == 'json-pp':
            output_file.write(unicode(json.dumps(meta, indent=2 * ' ', iterable_as_array=True, encoding='utf-8')))
        else:
            output_file.write(unicode(json.dumps(meta, separators=(',', ':'), iterable_as_array=True, encoding='utf-8')))
        output_file.write('\n')

    elif format in ('spdx-tv', 'spdx-rdf'):
        from spdx.checksum import Algorithm
        from spdx.creationinfo import Tool
        from spdx.document import Document, License
        from spdx.file import File
        from spdx.package import Package
        from spdx.utils import NoAssert
        from spdx.utils import SPDXNone
        from spdx.version import Version

        input = abspath(input)

        if os.path.isdir(input):
            input_path = input
        else:
            input_path = os.path.dirname(input)

        doc = Document(Version(2, 1), License.from_identifier('CC0-1.0'))

        doc.creation_info.add_creator(Tool('ScanCode ' + version))
        doc.creation_info.set_created_now()

        doc.package = Package(os.path.basename(input_path), NoAssert())

        # Use a set of unique copyrights for the package.
        doc.package.cr_text = set()

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
                        spdx_license = License.from_identifier(spdx_id)
                    else:
                        license_key = 'LicenseRef-' + file_license.get('key')
                        spdx_license = License(file_license.get('short_name'), license_key)

                    # Add licenses in the order they appear in the file. Maintaining the order
                    # might be useful for provenance purposes.
                    file_entry.add_lics(spdx_license)
                    doc.package.add_lics_from_file(spdx_license)
            else:
                if file_licenses == None:
                    all_files_have_no_license = False
                    spdx_license = NoAssert()
                else:
                    spdx_license = SPDXNone()

                file_entry.add_lics(spdx_license)

            file_entry.conc_lics = NoAssert()

            file_copyrights = file_data.get('copyrights')
            if file_copyrights:
                all_files_have_no_copyright = False
                file_entry.copyright = []
                for file_copyright in file_copyrights:
                    file_entry.copyright.extend(file_copyright.get('statements'))

                doc.package.cr_text.update(file_entry.copyright)

                # Create a text of copyright statements in the order they appear in the file.
                # Maintaining the order might be useful for provenance purposes.
                file_entry.copyright = '\n'.join(file_entry.copyright) + '\n'
            else:
                if file_copyrights == None:
                    all_files_have_no_copyright = False
                    spdx_copyright = NoAssert()
                else:
                    spdx_copyright = SPDXNone()

                file_entry.copyright = spdx_copyright

            doc.package.add_file(file_entry)

        if len(doc.package.files) == 0:
            if format == 'spdx-tv':
                output_file.write("# No results for package '{}'.\n".format(doc.package.name))
            else:
                output_file.write("<!-- No results for package '{}'. -->\n".format(doc.package.name))
            return

        # Remove duplicate licenses from the list for the package.
        unique_licenses = set(doc.package.licenses_from_files)
        if len(doc.package.licenses_from_files) == 0:
            if all_files_have_no_license:
                doc.package.licenses_from_files = [SPDXNone()]
            else:
                doc.package.licenses_from_files = [NoAssert()]
        else:
            # List license identifiers alphabetically for the package.
            doc.package.licenses_from_files = sorted(unique_licenses, key=lambda x: x.identifier)

        if len(doc.package.cr_text) == 0:
            if all_files_have_no_copyright:
                doc.package.cr_text = SPDXNone()
            else:
                doc.package.cr_text = NoAssert()
        else:
            # Create a text of alphabetically sorted copyright statements for the package.
            doc.package.cr_text = '\n'.join(sorted(doc.package.cr_text)) + '\n'

        doc.package.verif_code = doc.package.calc_verif_code()
        doc.package.license_declared = NoAssert()
        doc.package.conc_lics = NoAssert()

        # As the spdx-tools package can only write the document to a "str" file but ScanCode provides a "unicode" file,
        # write to a "str" buffer first and then manually write the value to a "unicode" file.
        from StringIO import StringIO

        str_buffer = StringIO()

        if format == 'spdx-tv':
            from spdx.writers.tagvalue import write_document
            write_document(doc, str_buffer)
        else:
            from spdx.writers.rdf import write_document
            write_document(doc, str_buffer)

        output_file.write(str_buffer.getvalue())

    else:
        raise Exception('Unknown format')
