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
from io import BytesIO
from io import StringIO

from spdx.checksum import Checksum
from spdx.checksum import ChecksumAlgorithm
from spdx.creationinfo import Tool
from spdx.document import ExtractedLicense
from spdx.document import Document
from spdx.license import License
from spdx.file import File
from spdx.package import Package
from spdx.relationship import Relationship
from spdx.utils import calc_verif_code
from spdx.utils import NoAssert
from spdx.utils import SPDXNone
from spdx.version import Version

from license_expression import Licensing
from commoncode.cliutils import OUTPUT_GROUP
from commoncode.cliutils import PluggableCommandLineOption
from commoncode.fileutils import file_name
from commoncode.fileutils import parent_directory
from commoncode.text import python_safe_name
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

_spdx_list_is_patched = False


def _patch_license_list():
    """
    Patch the SPDX Python library license list to match the list of ScanCode
    known SPDX licenses.
    """
    global _spdx_list_is_patched
    if not _spdx_list_is_patched:
        from spdx.config import LICENSE_MAP
        from licensedcode.models import load_licenses
        licenses = load_licenses(with_deprecated=True)
        spdx_licenses = get_licenses_by_spdx_key(licenses.values())
        LICENSE_MAP.update(spdx_licenses)
        _spdx_list_is_patched = True


def get_licenses_by_spdx_key(licenses):
    """
    Return a mapping of {spdx_key: license object} given a ``license`` sequence
    of License objects.
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
        PluggableCommandLineOption(('--spdx-tv',),
            type=FileOptionType(mode='w', encoding='utf-8', lazy=True),
            metavar='FILE',
            help='Write scan output as SPDX Tag/Value to FILE.',
            help_group=OUTPUT_GROUP)
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
            help='Write scan output as SPDX RDF to FILE.',
            help_group=OUTPUT_GROUP)
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
            **kwargs
        )


def _process_codebase(
    spdx_plugin,
    codebase,
    input_path,
    output_file,
    as_tagvalue=True,
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
    download_location=NoAssert(),
    as_tagvalue=True,
    spdx_version = (2, 2),
    with_notice_text=False,
):
    """
    Write scan output as SPDX Tag/value to ``output_file`` file-like
    object using the ``files`` list of scanned file data.
    Write as RDF XML if ``as_tagvalue`` is False.

    Use the ``notice`` string as a notice included in a document comment.
    Include the ``tool_name`` and ``tool_version`` to indicate which tool is
    producing this SPDX document.
    Use ``package_name`` as a Package name and as a namespace prefix base.
    """
    from licensedcode import cache
    licenses = cache.get_licenses_db()
    licensing = Licensing()

    as_rdf = not as_tagvalue
    _patch_license_list()

    ns_prefix = '_'.join(package_name.lower().split())
    comment = notice + f'\nSPDX License List: {scancode_config.spdx_license_list_version}'

    version_major, version_minor = scancode_config.spdx_license_list_version.split(".")
    spdx_license_list_version = Version(major=version_major, minor=version_minor)

    doc = Document(
        version=Version(*spdx_version),
        data_license=License.from_identifier('CC0-1.0'),
        comment=notice,
        namespace=f'http://spdx.org/spdxdocs/{ns_prefix}-{uuid.uuid4()}',
        license_list_version=scancode_config.spdx_license_list_version,
        name='SPDX Document created by ScanCode Toolkit'
    )

    tool_name = tool_name or 'ScanCode'
    doc.creation_info.add_creator(Tool(f'{tool_name} {tool_version}'))
    doc.creation_info.set_created_now()
    doc.creation_info.license_list_version = spdx_license_list_version

    package_id = '001'
    package = doc.package = Package(
        name=package_name,
        download_location=download_location,
        spdx_id=f'SPDXRef-{package_id}',
    )

    # Use a set of unique copyrights for the package.
    package.cr_text = set()

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
        file_entry = File(
            spdx_id=f'SPDXRef-{sid}',
            name=name)
        if file_data.get('file_type') == 'empty':
            file_entry.set_checksum(Checksum(ChecksumAlgorithm.SHA1, "da39a3ee5e6b4b0d3255bfef95601890afd80709"))
        else:
            file_entry.set_checksum(Checksum(ChecksumAlgorithm.SHA1, file_data.get('sha1') or ''))

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

                    if not is_license_ref:
                        spdx_license = License.from_identifier(spdx_id)
                    else:
                        spdx_license = ExtractedLicense(spdx_id)
                        spdx_license.name = file_license.short_name
                        # FIXME: replace this with the licensedb URL
                        comment = (
                            f'See details at https://github.com/nexB/scancode-toolkit'
                            f'/blob/develop/src/licensedcode/data/licenses/{license_key}.yml\n'
                        )
                        spdx_license.comment = comment
                        text = match.get('matched_text')
                        # always set some text, even if we did not extract the
                        # matched text
                        if not text:
                            text = comment
                        spdx_license.text = text
                        doc.add_extr_lic(spdx_license)

                    # Add licenses in the order they appear in the file. Maintaining
                    # the order might be useful for provenance purposes.
                    file_entry.add_lics(spdx_license)
                    package.add_lics_from_file(spdx_license)

        elif license_matches is None:
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
                file_entry.copyright.append(file_copyright.get('copyright'))

            package.cr_text.update(file_entry.copyright)

            # Create a text of copyright statements in the order they appear in
            # the file. Maintaining the order might be useful for provenance
            # purposes.
            file_entry.copyright = '\n'.join(file_entry.copyright) + '\n'

        elif file_copyrights is None:
            all_files_have_no_copyright = False
            file_entry.copyright = NoAssert()

        else:
            file_entry.copyright = SPDXNone()

        doc.add_file(file_entry)
        relationship = Relationship(f'{package.spdx_id} CONTAINS {file_entry.spdx_id}')
        doc.add_relationship(relationship)

    if not doc.files:
        if as_tagvalue:
            msg = "# No results for package '{}'.\n".format(package.name)
        else:
            # rdf
            msg = "<!-- No results for package '{}'. -->\n".format(package.name)
        output_file.write(msg)

    # Remove duplicate licenses from the list for the package.
    unique_licenses = {l.identifier: l for l in package.licenses_from_files}
    unique_licenses = list(unique_licenses.values())
    if not len(package.licenses_from_files):
        if all_files_have_no_license:
            package.licenses_from_files = [SPDXNone()]
        else:
            package.licenses_from_files = [NoAssert()]
    else:
        # List license identifiers alphabetically for the package.
        package.licenses_from_files = sorted(
            unique_licenses,
            key=lambda x: x.identifier,
        )

    if len(package.cr_text) == 0:
        if all_files_have_no_copyright:
            package.cr_text = SPDXNone()
        else:
            package.cr_text = NoAssert()
    else:
        # Create a text of alphabetically sorted copyright
        # statements for the package.
        package.cr_text = '\n'.join(sorted(package.cr_text)) + '\n'

    package.verif_code = calc_verif_code(doc.files)
    package.license_declared = NoAssert()
    package.conc_lics = NoAssert()

    # The spdx-tools write_document returns either:
    # - unicode for tag values
    # - UTF8-encoded bytes for rdf because somehow the rdf and xml
    #   libraries do the encoding and do not return text but bytes
    # The file passed by ScanCode for output is opened in text mode Therefore in
    # one case we do need to deal with bytes and decode before writing (rdf) and
    # in the other case we deal with text all the way.

    if doc.files:

        if as_tagvalue:
            from spdx.writers.tagvalue import write_document  # NOQA
        elif as_rdf:
            from spdx.writers.rdf import write_document  # NOQA

        if as_tagvalue:
            spdx_output = StringIO()
        elif as_rdf:
            # rdf is utf-encoded bytes
            spdx_output = BytesIO()

        write_document(doc, spdx_output, validate=False)
        result = spdx_output.getvalue()

        if as_rdf:
            # rdf is utf-encoded bytes
            result = result.decode('utf-8')

        output_file.write(result)
