#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
import os
import sys
import uuid
from datetime import datetime
from io import BytesIO
from io import StringIO


from license_expression import Licensing
from commoncode.cliutils import OUTPUT_GROUP
from commoncode.cliutils import PluggableCommandLineOption
from commoncode.fileutils import file_name
from commoncode.fileutils import parent_directory
from commoncode.text import python_safe_name
from spdx_tools.spdx.model import SpdxNoAssertion
from spdx_tools.spdx.model import Version
from spdx_tools.spdx.model import CreationInfo
from spdx_tools.spdx.model import Actor
from spdx_tools.spdx.model import ActorType
from spdx_tools.spdx.model import Document
from spdx_tools.spdx.model import Package
from spdx_tools.spdx.model import File
from spdx_tools.spdx.model import Checksum
from spdx_tools.spdx.model import ChecksumAlgorithm
from spdx_tools.spdx.model import ExtractedLicensingInfo
from spdx_tools.spdx.model import SpdxNone
from spdx_tools.spdx.model import Relationship
from spdx_tools.spdx.model import RelationshipType
from spdx_tools.spdx.spdx_element_utils import calculate_package_verification_code

from formattedcode import FileOptionType
from licensedcode.detection import get_matches_from_detection_mappings
from plugincode.output import output_impl
from plugincode.output import OutputPlugin
import scancode_config

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
        return logger.debug(
            ' '.join(isinstance(a, str) and a or repr(a) for a in args)
        )

"""
Output plugins to write scan results in SPDX format.
"""

@output_impl
class SpdxTvOutput(OutputPlugin):

    options = [
        PluggableCommandLineOption(('--spdx-tv',),
            type=FileOptionType(mode='w', encoding='utf-8', lazy=True),
            metavar='FILE',
            default=None,
            help='Write scan output as SPDX Tag/Value to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order=70,
        )
    ]

    def is_enabled(self, spdx_tv, **kwargs):
        return spdx_tv

    def process_codebase(self, codebase, spdx_tv, **kwargs):
        _process_codebase(
            spdx_plugin=self,
            codebase=codebase,
            input_path=kwargs.get('input', ''),
            output_file=spdx_tv,
            as_tagvalue=True,
            **kwargs
        )


@output_impl
class SpdxRdfOutput(OutputPlugin):

    options = [
        PluggableCommandLineOption(('--spdx-rdf',),
            type=FileOptionType(mode='w', encoding='utf-8', lazy=True),
            metavar='FILE',
            default=None,
            help='Write scan output as SPDX RDF to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order=70,
        )
    ]

    def is_enabled(self, spdx_rdf, **kwargs):
        return spdx_rdf

    def process_codebase(self, codebase, spdx_rdf, **kwargs):
        _process_codebase(
            spdx_plugin=self,
            codebase=codebase,
            input_path=kwargs.get('input', ''),
            output_file=spdx_rdf,
            as_tagvalue=False,
            output_format='rdf',
            **kwargs
        )


@output_impl
class SpdxJsonOutput(OutputPlugin):

    options = [
        PluggableCommandLineOption(('--spdx-json',),
            type=FileOptionType(mode='w', encoding='utf-8', lazy=True),
            metavar='FILE',
            default=None,
            help='Write scan output as SPDX 2.3 JSON to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order=70,
        )
    ]

    def is_enabled(self, spdx_json, **kwargs):
        return spdx_json

    def process_codebase(self, codebase, spdx_json, **kwargs):
        _process_codebase(
            spdx_plugin=self,
            codebase=codebase,
            input_path=kwargs.get('input', ''),
            output_file=spdx_json,
            as_tagvalue=False,
            output_format='json',
            spdx_version=(2, 3),
            **kwargs
        )


@output_impl
class SpdxYamlOutput(OutputPlugin):

    options = [
        PluggableCommandLineOption(('--spdx-yaml',),
            type=FileOptionType(mode='w', encoding='utf-8', lazy=True),
            metavar='FILE',
            default=None,
            help='Write scan output as SPDX 2.3 YAML to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order=70,
        )
    ]

    def is_enabled(self, spdx_yaml, **kwargs):
        return spdx_yaml

    def process_codebase(self, codebase, spdx_yaml, **kwargs):
        _process_codebase(
            spdx_plugin=self,
            codebase=codebase,
            input_path=kwargs.get('input', ''),
            output_file=spdx_yaml,
            as_tagvalue=False,
            output_format='yaml',
            spdx_version=(2, 3),
            **kwargs
        )


@output_impl
class SpdxXmlOutput(OutputPlugin):

    options = [
        PluggableCommandLineOption(('--spdx-xml',),
            type=FileOptionType(mode='w', encoding='utf-8', lazy=True),
            metavar='FILE',
            default=None,
            help='Write scan output as SPDX 2.3 XML to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order=70,
        )
    ]

    def is_enabled(self, spdx_xml, **kwargs):
        return spdx_xml

    def process_codebase(self, codebase, spdx_xml, **kwargs):
        _process_codebase(
            spdx_plugin=self,
            codebase=codebase,
            input_path=kwargs.get('input', ''),
            output_file=spdx_xml,
            as_tagvalue=False,
            output_format='xml',
            spdx_version=(2, 3),
            **kwargs
        )


def _process_codebase(
    spdx_plugin,
    codebase,
    input_path,
    output_file,
    as_tagvalue=True,
    output_format=None,
    spdx_version=(2, 2),
    **kwargs,
):
    check_sha1(codebase)
    files = spdx_plugin.get_files(codebase, **kwargs)
    header = codebase.get_or_create_current_header()
    tool_name = header.tool_name
    tool_version = header.tool_version
    notice = header.notice
    package_name = build_package_name(input_path)

    write_spdx(
        codebase=codebase,
        output_file=output_file,
        files=files,
        tool_name=tool_name,
        tool_version=tool_version,
        notice=notice,
        package_name=package_name,
        as_tagvalue=as_tagvalue,
        output_format=output_format,
        spdx_version=spdx_version,
    )


def build_package_name(input_path):
    """
    Return a package name built from an ``input_path`` path.

    """
    if input_path:
        absinput = absinput = os.path.abspath(input_path)
        if  os.path.isfile(absinput):
            input_path = parent_directory(absinput)
        return python_safe_name(file_name(input_path))

    return 'scancode-toolkit-analyzed-package'


def check_sha1(codebase):
    has_sha1 = hasattr(codebase.root, 'sha1')
    if not has_sha1:
        import click

        click.secho(
            'WARNING: Files are missing a SHA1 attribute. '
            'Incomplete SPDX document created.',
            err=True,
            fg='red',
        )


def write_spdx(
    codebase,
    output_file,
    files,
    tool_name,
    tool_version,
    notice,
    package_name='',
    download_location=SpdxNoAssertion(),
    as_tagvalue=True,
    spdx_version=(2, 2),
    with_notice_text=False,
    output_format=None,
):
    """
    Write scan output as SPDX to ``output_file`` file-like object using the
    ``files`` list of scanned file data.
    ``output_format`` may be one of ``'tv'``, ``'rdf'``, ``'json'``, ``'yaml'``,
    or ``'xml'``. When omitted, writes Tag/Value if ``as_tagvalue`` is True or
    RDF XML otherwise.

    Use the ``notice`` string as a notice included in a document comment.
    Include the ``tool_name`` and ``tool_version`` to indicate which tool is
    producing this SPDX document.
    Use ``package_name`` as a Package name and as a namespace prefix base.
    """
    from licensedcode import cache
    licenses = cache.get_licenses_db()
    licensing = Licensing()

    if output_format is None:
        output_format = 'tv' if as_tagvalue else 'rdf'
    as_tagvalue = output_format == 'tv'
    as_rdf = output_format == 'rdf'

    ns_prefix = '_'.join(package_name.lower().split())
    comment = notice + f'\nSPDX License List: {scancode_config.spdx_license_list_version}'

    version_major, version_minor = scancode_config.spdx_license_list_version.split(".")
    spdx_license_list_version = Version(major=version_major, minor=version_minor)

    tool_name = tool_name or 'ScanCode'
    creator = Actor(ActorType.TOOL, f'{tool_name} {tool_version}')

    creation_info = CreationInfo(
        spdx_id="SPDXRef-DOCUMENT",
        spdx_version=f"SPDX-{spdx_version[0]}.{spdx_version[1]}",
        data_license='CC0-1.0',
        document_comment=comment,
        document_namespace=f'http://spdx.org/spdxdocs/{ns_prefix}-{uuid.uuid4()}',
        license_list_version=spdx_license_list_version,
        name='SPDX Document created by ScanCode Toolkit',
        creators=[creator],
        created=datetime.now(),
    )


    package_id = '001'
    package = Package(
        name=package_name,
        download_location=download_location,
        spdx_id=f'SPDXRef-{package_id}',
    )

    doc = Document(
        creation_info=creation_info,
        packages=[package],
    )

    # Use a set of unique copyrights for the package.
    package_copyright_texts = set()

    all_files_have_no_license = True
    all_files_have_no_copyright = True

    # FIXME: this should walk the codebase instead!!!
    for sid, file_data in enumerate(files, 1):

        # Skip directories.
        if file_data.get('type') != 'file':
            continue

        # Set a relative file name as that is what we want in
        # SPDX output (with explicit leading './').
        name = './' + file_data.get('path')

        if file_data.get('file_type') == 'empty':
            checksum = Checksum(ChecksumAlgorithm.SHA1, "da39a3ee5e6b4b0d3255bfef95601890afd80709")
        else:
            # FIXME: this sets the checksum of a file to the empty string hash if unknown; tracked in https://github.com/nexB/scancode-toolkit/issues/3453
            checksum = Checksum(ChecksumAlgorithm.SHA1, file_data.get('sha1') or 'da39a3ee5e6b4b0d3255bfef95601890afd80709')

        file_entry = File(
            spdx_id=f'SPDXRef-{sid}',
            name=name,
            checksums=[checksum]
        )

        file_license_detections = file_data.get('license_detections')
        license_matches = get_matches_from_detection_mappings(file_license_detections)
        if license_matches:
            all_files_have_no_license = False
            for match in license_matches:
                file_license_expression = match["license_expression"]
                file_license_keys = licensing.license_keys(
                    expression=file_license_expression,
                    unique=True
                )
                for license_key in file_license_keys:
                    file_license = licenses.get(license_key)
                    license_key = file_license.key

                    spdx_id = file_license.spdx_license_key
                    if not spdx_id:
                        spdx_id = f'LicenseRef-scancode-{license_key}'
                    is_license_ref = spdx_id.lower().startswith('licenseref-')

                    spdx_license = licensing.parse(spdx_id)

                    if is_license_ref:
                        text = match.get('matched_text')
                        # FIXME: replace this with the licensedb URL
                        comment = (
                            f'See details at https://github.com/nexB/scancode-toolkit'
                            f'/blob/develop/src/licensedcode/data/licenses/{license_key}.LICENSE\n'
                        )
                        extracted_license = ExtractedLicensingInfo(
                            license_id=spdx_id,
                            # always set some text, even if we did not extract the
                            # matched text
                            extracted_text=text if text else comment,
                            license_name=file_license.short_name,
                            comment=comment,
                        )
                        doc.extracted_licensing_info.append(extracted_license)

                    # Add licenses in the order they appear in the file. Maintaining
                    # the order might be useful for provenance purposes.
                    file_entry.license_info_in_file.append(spdx_license)
                    package.license_info_from_files.append(spdx_license)

        elif license_matches is None:
            all_files_have_no_license = False
            file_entry.license_info_in_file.append(SpdxNoAssertion())

        else:
            file_entry.license_info_in_file.append(SpdxNone())

        file_entry.license_concluded = SpdxNoAssertion()

        file_copyrights = file_data.get('copyrights')
        if file_copyrights:
            all_files_have_no_copyright = False
            copyrights = []
            for file_copyright in file_copyrights:
                copyrights.append(file_copyright.get('copyright'))

            package_copyright_texts.update(copyrights)

            # Create a text of copyright statements in the order they appear in
            # the file. Maintaining the order might be useful for provenance
            # purposes.
            file_entry.copyright_text = '\n'.join(copyrights) + '\n'

        elif file_copyrights is None:
            all_files_have_no_copyright = False
            file_entry.copyright_text = SpdxNoAssertion()

        else:
            file_entry.copyright_text = SpdxNone()

        doc.files.append(file_entry)
        relationship = Relationship(package.spdx_id, RelationshipType.CONTAINS, file_entry.spdx_id)
        doc.relationships.append(relationship)

    if not doc.files:
        if as_tagvalue:
            msg = "# No results for package '{}'.\n".format(package.name)
            output_file.write(msg)
        elif as_rdf:
            msg = "<!-- No results for package '{}'. -->\n".format(package.name)
            output_file.write(msg)

    # Remove duplicate licenses from the list for the package.
    package.license_info_from_files = list(set(package.license_info_from_files))
    if not package.license_info_from_files:
        if all_files_have_no_license:
            package.license_info_from_files = [SpdxNone()]
        else:
            package.license_info_from_files = [SpdxNoAssertion()]
    else:
        # List license identifiers alphabetically for the package.
        package.license_info_from_files = sorted(package.license_info_from_files)

    if not package_copyright_texts:
        if all_files_have_no_copyright:
            package.copyright_text = SpdxNone()
        else:
            package.copyright_text = SpdxNoAssertion()
    else:
        # Create a text of alphabetically sorted copyright
        # statements for the package.
        package.copyright_text = '\n'.join(sorted(package_copyright_texts)) + '\n'

    package.verification_code = calculate_package_verification_code(doc.files)
    package.license_declared = SpdxNoAssertion()
    package.license_concluded = SpdxNoAssertion()

    # The spdx-tools write_document returns either:
    # - unicode for tag values
    # - UTF8-encoded bytes for rdf because somehow the rdf and xml
    #   libraries do the encoding and do not return text but bytes
    # The file passed by ScanCode for output is opened in text mode Therefore in
    # one case we do need to deal with bytes and decode before writing (rdf) and
    # in the other case we deal with text all the way.

    if doc.files or output_format in ('json', 'yaml', 'xml'):
        import importlib
        writers = {
            'tv': ('spdx_tools.spdx.writer.tagvalue.tagvalue_writer', False),
            'rdf': ('spdx_tools.spdx.writer.rdf.rdf_writer', True),
            'json': ('spdx_tools.spdx.writer.json.json_writer', False),
            'yaml': ('spdx_tools.spdx.writer.yaml.yaml_writer', False),
            'xml': ('spdx_tools.spdx.writer.xml.xml_writer', False),
        }
        if output_format not in writers:
            raise ValueError(f'Unsupported SPDX output format: {output_format!r}')

        writer_module, is_bytes = writers[output_format]
        write_document_to_stream = importlib.import_module(writer_module).write_document_to_stream
        spdx_output = BytesIO() if is_bytes else StringIO()

        write_document_to_stream(doc, spdx_output, validate=False)
        result = spdx_output.getvalue()

        if is_bytes:
            # rdf is utf-encoded bytes
            result = result.decode('utf-8')

        output_file.write(result)
