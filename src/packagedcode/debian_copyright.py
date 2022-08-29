#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
import fnmatch
import os
import sys
from collections import defaultdict
from itertools import chain
from pathlib import Path

import attr
from debian_inspector.copyright import CatchAllParagraph
from debian_inspector.copyright import CopyrightFilesParagraph
from debian_inspector.copyright import CopyrightLicenseParagraph
from debian_inspector.copyright import CopyrightHeaderParagraph
from debian_inspector.copyright import DebianCopyright
from license_expression import ExpressionError
from license_expression import LicenseSymbolLike
from license_expression import Licensing

from licensedcode.cache import get_index
from licensedcode.query import Query
from licensedcode.match import LicenseMatch
from licensedcode.match import set_matched_lines
from licensedcode.models import Rule
from licensedcode.spans import Span
from packagedcode import models
from packagedcode.licensing import get_license_expression_from_matches
from packagedcode.licensing import get_license_matches
from packagedcode.licensing import get_license_matches_from_query_string
from packagedcode.utils import combine_expressions
from textcode.analysis import unicode_text

"""
Detect licenses and copyright in Debian copyright files. Can handle dep-5
machine-readable copyright files, pre-dep-5 mostly machine-readable copyright
files and unstructured non-dep5 copyright files.

The machine-readable files are often messy and not always correctly structured.

License texts can be scattered in various paragraphs in license, comments or
extra data.

The license symbols used in these files are local to a single file and therefore
require full detection to assign some meaning to them

See https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
"""

TRACE = os.environ.get('SCANCODE_DEBUG_PACKAGE', False)



def logger_debug(*args):
    pass


if TRACE:
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(
            ' '.join(isinstance(a, str) and a or repr(a) for a in args)
        )

MATCHER_UNKNOWN = '5-unknown'

class BaseDebianCopyrightFileHandler(models.DatafileHandler):
    default_package_type = 'deb'
    documentation_url = 'https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/'

    @classmethod
    def is_datafile(cls, location, filetypes=tuple(), strict=False):
        isdc = (
            super().is_datafile(location, filetypes=filetypes)
            # we want the filename to be lowercase
            and location.endswith('copyright')
        )
        if isdc:
            if strict:
                text = unicode_text(location)
                return EnhancedDebianCopyright.is_machine_readable_copyright(text)
            else:
                return True

    @classmethod
    def compute_normalized_license(cls, package):
        return

    @classmethod
    def parse(cls, location):
        dc = parse_copyright_file(location)
        # TODO: collect the upstream source package details

        # find a name... TODO: this should be pushed down to each handler
        if fnmatch.fnmatch(name=location, pat='*usr/share/doc/*/copyright'):
            path = Path(location)
            name = path.parent.name
        else:
            # no name otherwise for now
            name = None

        yield models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            declared_license=dc.get_declared_license(),
            license_expression=dc.get_license_expression(),
            copyright=dc.get_copyright(),
        )


class DebianCopyrightFileInSourceHandler(BaseDebianCopyrightFileHandler):
    datasource_id = 'debian_copyright_in_source'
    description = 'Debian machine readable file in source'

    path_patterns = (
        # Seen in a source repo or in *.debian.tar.xz tarball
        # See https://github.com/Debian/dcs/blob/c88c75b9fb776b9d3075698716af8c0fd8d7558f/debian/copyright ]
        # See http://deb.debian.org/debian/pool/main/p/python-docutils/python-docutils_0.16+dfsg-4.debian.tar.xz
        '*/debian/copyright',
    )

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        # two levels up
        root = resource.parent(codebase).parent(codebase)
        if root:
            return cls.assign_package_to_resources(package, root, codebase, package_adder)


# TODO: distiguish the cased of an installed package vs. the case of an extracted .deb
class DebianCopyrightFileInPackageHandler(BaseDebianCopyrightFileHandler):
    datasource_id = 'debian_copyright_in_package'
    description = 'Debian machine readable file in source'

    path_patterns = (
        # Standard form when seen in an installed form in /usr/share/doc/
        # and in the same place in the data.tar.xz inner archive of a .deb archive
        # See http://ftp.us.debian.org/debian/pool/main/p/python-docutils/python3-docutils_0.16+dfsg-4_all.deb
        '*usr/share/doc/*/copyright',
    )

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        # DO NOTHING: let other handler reuse this
        return []


class StandaloneDebianCopyrightFileHandler(BaseDebianCopyrightFileHandler):
    datasource_id = 'debian_copyright_standalone'
    description = 'Debian machine readable file standalone'

    path_patterns = (
        # other places... may be we should treat this strictly wrt. being a structure file only?
        '*/copyright',
        # Seen in http://metadata.ftp-master.debian.org/changelogs/main/d/dtrx/dtrx_8.2.2-1_copyright
        '*_copyright',
    )

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        # assemble is the default
        yield from super().assemble(package_data, resource, codebase, package_adder)


class NotReallyStructuredCopyrightFile(Exception):
    """
    Raised when a file has a dep5, machine readable copyrigh file format
    declared, but is not strictly structured.
    """


def parse_copyright_file(location, check_consistency=False):
    """
    Return a DebianDetector Object containing copyright and license detections
    extracted from the debian copyright file at ``location``.

    If ``check_consistency`` is True, check if debian copyright file is
    consistently structured according to the guidelines specified at
    https://www.debian.org/doc/packaging-manuals/copyright-format/1.0
    """
    if not location or not location.endswith('copyright'):
        return

    # FIXME: we should not read the whole files here and then discard it!
    text = unicode_text(location)
    if EnhancedDebianCopyright.is_machine_readable_copyright(text):
        try:
            dc = StructuredCopyrightProcessor.from_file(
                location=location,
                check_consistency=check_consistency,
            )
        except NotReallyStructuredCopyrightFile:
            if TRACE:
                logger_debug(
                    'StructuredCopyrightProcessor.from_file: '
                    'file is not really structured:',
                    location
                )
            dc = UnstructuredCopyrightProcessor.from_file(
                location=location,
                check_consistency=check_consistency,
            )
    else:
        dc = UnstructuredCopyrightProcessor.from_file(
            location=location,
            check_consistency=check_consistency,
        )

    if check_consistency and dc.consistency_errors:
        msg = (
            f'Debian Copyright file in not consistent, because of the following:'
            f' {dc.consistency_errors}'
        )
        raise DebianCopyrightStructureError(msg)

    if TRACE:
        logger_debug(f'parse_copyright_file: {type(dc)}')
        if isinstance(dc, StructuredCopyrightProcessor):
            for det in dc.license_detections:
                print()
                print(type(det.paragraph))
                for f in det.paragraph.get_field_names():
                    print(f' {f}: {getattr(det.paragraph, f)}')
                    print()
                for m in det.license_matches:
                    print(m)
                    print()

    return dc


@attr.s
class DebianDetector:
    """
    Base class for `UnstructuredCopyrightProcessor` and
    `StructuredCopyrightProcessor` classes, defining the common functions and
    attributes.

    An instance can scan ONLY one copyright file; it cannot be reused.
    """
    # Absolute location of this copyright file
    location = attr.ib()

    # List of consistency error messages if the debian copyright file is not
    # consistent. This is populated if the `check_consistency` flag in
    # `parse_copyright_file` is set to True.
    consistency_errors = attr.ib(default=attr.Factory(list))

    @classmethod
    def from_file(cls, *args, **kwargs):
        """
        Return a DebianDetector object with License and Copyright detections.
        """
        raise NotImplementedError

    def get_copyright(self, *args, **kwargs):
        """
        Return a copyright string (found in Copyright: structured fields or in
        plain text).
        """
        raise NotImplementedError

    def get_license_expression(self, *args, **kwargs):
        """
        Return a license expression string suitable to use as a
        PackageData.license_expression.
        """
        raise NotImplementedError

    def get_declared_license(self, *args, **kwargs):
        """
        Return a list of declared license string suitable to use as a
        PackageData.declared_license.
        """
        raise NotImplementedError


@attr.s
class UnstructuredCopyrightProcessor(DebianDetector):
    # List of LicenseMatches in an unstructured file
    license_matches = attr.ib(default=attr.Factory(list))

    # List of detected copyrights in an unstructured file
    detected_copyrights = attr.ib(default=attr.Factory(list))

    @classmethod
    def from_file(cls, location, check_consistency=False):
        """
        Return a UnstructuredCopyrightProcessor object created from a
        unstructured debian copyright file, after detecting license and
        copyrights.

        If `check_consistency` is True, will always add a consistency error as
        unstructured copyright files are not consistent.
        """
        dc = cls(location=location)

        if check_consistency:
            dc.consistency_errors.append('Debian Copyright File is unstructured')

        dc.detected_copyrights = copyright_detector(location)
        dc.detect_license(location=location)

        return dc

    @property
    def primary_license(self):
        """
        Return None as primary license cannot be detected in an unstructured
        debian copyright file.
        """
        return None

    def get_declared_license(self, *args, **kwargs):
        """
        Return None as there is no declared licenses in an unstructured debian
        copyright file.
        """
        return None

    def get_license_expression(
        self,
        simplify_licenses=False,
        *args, **kwargs
    ):
        """
        Return a license expression string for the corresponding debian
        copyright file.

        If simplify_licenses is True, uses Licensing.dedup() to simplify the
        license expression.
        """
        detected_expressions = [
            match.rule.license_expression for match in self.license_matches
        ]
        license_expression = combine_expressions(
            expressions=detected_expressions,
            relation='AND',
            unique=False,
        )

        if simplify_licenses:
            return dedup_expression(license_expression=license_expression)
        else:
            return license_expression

    def get_copyright(self, *args, **kwargs):
        """
        Return a copyright string with one copyright statement per line.
        """
        return '\n'.join(self.detected_copyrights)

    def detect_license(self, location):
        """
        Return a list of LicenseMatch objects detected in the file at
        ``location``. Return a list with a single match to an UnknownRule if no
        license is detected since we must detect some license in this text.
        """
        # note that we are passing a file location so we have proper line numbers
        license_matches = get_license_matches(location=location)
        if TRACE:
            logger_debug('UnstructuredCopyrightProcessor.detect_license: matches:', license_matches)

        license_matches = remove_known_license_intros(
            license_matches=license_matches
        )

        if TRACE:
            logger_debug('UnstructuredCopyrightProcessor.detect_license: matches2:', license_matches)

        if not license_matches:
            text = unicode_text(location)
            # We have no match: return unknown as there must be some license
            # FIXME: we should track line numbers
            license_matches = add_unknown_matches(name=None, text=text)

        self.license_matches = license_matches
        return license_matches


def is_really_structured(dc):
    """
    Return False if a `dc` debian_inspector DebianCopyright is not really a
    structured file based on its paragraph types makeup.
    Return True otherwise.
    """

    # With only CatchAllParagraph paras we are not structured
    if all(type(p) == CatchAllParagraph for p in dc.paragraphs):
        return False

    # With over 4 catchall paras, we have too many catchalls.
    # A catchall is a sign of recovery from parsing invalid constructions.
    para_type_counts = defaultdict(int)
    for p in dc.paragraphs:
        para_type_counts[type(p)] = para_type_counts[type(p)] + 1
    if para_type_counts.get(CatchAllParagraph, 0) > 4:
        return False

    return True


@attr.s
class StructuredCopyrightProcessor(DebianDetector):

    # FIXME: we should also return the plain License paragraphs

    # List of LicenseDetection objects from detection in files and header
    # paragraphs
    license_detections = attr.ib(default=attr.Factory(list))

    # List of CopyrightDetection from copyright statements found in files and
    # header paragraphs
    copyright_detections = attr.ib(default=attr.Factory(list))

    # A DebianCopyright object built from the copyright file
    debian_copyright = attr.ib(default=None)

    # primary license as a license expression. This is the license present in
    # header or 'files: *' paragraph for a structured debian copyright file
    primary_license = attr.ib(default=None)

    @classmethod
    def from_file(cls, location, check_consistency=False):
        """
        Return a DebianCopyrightFileProcessor object built from debian copyright
        file at ``location``, or None if this is not a debian copyright file.

        If `check_consistency` is True, check if debian copyright file is
        consistently structured according to debian guidelines.
        """
        if not location or not location.endswith('copyright'):
            return

        debian_copyright = DebianCopyright.from_file(location)

        if not is_really_structured(debian_copyright):
            # we bail out and this will be treated as unstructured
            raise NotReallyStructuredCopyrightFile(location)

        edc = EnhancedDebianCopyright(debian_copyright=debian_copyright)
        dc = cls(location=location, debian_copyright=debian_copyright)
        dc.detect_license()
        dc.detect_copyrights()
        dc.set_primary_license()

        if check_consistency:
            dc.consistentcy_errors = edc.get_consistentcy_errors()

        return dc

    @property
    def license_matches(self):
        """
        Get a list of all LicenseMatch objects which are detected in the
        copyright file.
        """
        matches = (
            ld.license_matches
            for ld in self.license_detections
            if ld.license_matches
        )
        return chain.from_iterable(matches)

    def set_primary_license(self):
        """
        Compute and set the primary license expression of this
        debian copyright file to`primary_license`.

        A primary license in a debian copyright file is the license in the
        Header paragraph or the `Files: *` paragraph.
        """
        expressions = []
        has_header_license = False
        has_primary_license = False

        for ld in self.license_detections:
            if ld.license_expression_object != None:
                if not has_header_license and isinstance(
                    ld.paragraph, CopyrightHeaderParagraph
                ):
                    expressions.append(ld.license_expression_object)
                    has_header_license = True

                if not has_primary_license and is_paragraph_primary_license(
                    ld.paragraph
                ):
                    expressions.append(ld.license_expression_object)
                    has_primary_license = True

        self.primary_license = dedup_expression(
            license_expression=str(combine_expressions(expressions))
        )

    def get_declared_license(
        self,
        filter_duplicates=False,
        skip_debian_packaging=False,
        *args, **kwargs,
    ):
        """
        Return a list of declared license strings (`License: <string>`) from the
        all paragraphs.

        If `filter_duplicates` is True, only unique declared licenses are
        returned. If `skip_debian_packaging` is True, skips the declared license
        for `Files: debian/*` paragraph.
        """
        declarable_paragraphs = [
            para
            for para in self.debian_copyright.paragraphs
            if hasattr(para, 'license') and para.license.name
        ]

        if skip_debian_packaging:
            declarable_paragraphs = [
                para
                for para in declarable_paragraphs
                if not is_paragraph_debian_packaging(para)
            ]

        declared_licenses = [
            paragraph.license.name for paragraph in declarable_paragraphs
        ]

        if filter_duplicates:
            return filter_duplicate_strings(declared_licenses)
        else:
            return declared_licenses

    def get_copyright(
        self,
        skip_debian_packaging=False,
        unique_copyrights=False,
        *args,
        **kwarg,
    ):
        """
        Return a copyright string from copyright statements collected in this
        structured copyright file.

        If `unique_copyrights` is True, only unique copyrights are returned.
        If `skip_debian_packaging` is True, skips the declared license for
        `Files: debian/*` paragraph.
        """
        declarable_copyrights = []
        seen_copyrights = set()
        # TODO: Only Unique Holders (copyright without years) should be reported
        # TODO: Report line numbers

        for copyright_detection in self.copyright_detections:
            if (
                skip_debian_packaging
                and is_paragraph_debian_packaging(copyright_detection.paragraph)
            ):
                continue

            if not isinstance(
                copyright_detection.paragraph,
                (CopyrightHeaderParagraph, CopyrightFilesParagraph)
            ):
                continue

            if unique_copyrights:
                for copyrght in copyright_detection.copyrights:
                    if copyrght not in seen_copyrights:
                        if any(x in copyrght for x in ('unknown', 'none',)):
                            continue
                        seen_copyrights.add(copyrght)

                        declarable_copyrights.append(copyrght)
                continue

            declarable_copyrights.extend(copyright_detection.copyrights)

        return '\n'.join(declarable_copyrights)

    def detect_copyrights(self):
        """
        Return a list of CopyrightDetection objects found in paragraphs.
        """
        # TODO: We should also track line numbers in the file where a license was found
        copyright_detections = []

        for paragraph in self.debian_copyright.paragraphs:
            copyrights = []

            if isinstance(paragraph, (CopyrightHeaderParagraph, CopyrightFilesParagraph)):
                pcs = paragraph.copyright.statements or []
                for p in pcs:
                    p = p.dumps()
                    copyrights.append(p)

            copyright_detections.append(
                CopyrightDetection(paragraph=paragraph, copyrights=copyrights)
            )

        # We detect plain copyrights if we didn't find any
        if not copyrights:
            copyrights = copyright_detector(self.location)
            copyright_detections.append(
                CopyrightDetection(paragraph=None, copyrights=copyrights)
            )

        self.copyright_detections = copyright_detections

    def get_license_expression(
        self,
        skip_debian_packaging=False,
        simplify_licenses=False,
        *args,
        **kwargs,
    ):
        """
        Return a license expression string built from the this object
        ``license_detections``.

        If `skip_debian_packaging` is True, skips the declared license for
        `Files: debian/*` paragraph.

            If `simplify_licenses` is True, license expressions are deduplicated by
        Licensing.dedup() and then returned.
        """
        if not self.license_detections:
            raise_no_license_found_error(location=self.location)

        license_detections = [
            license_detection
            for license_detection in self.license_detections
            if license_detection.is_detection_reportable()
        ]

        if skip_debian_packaging:
            license_detections = [
                license_detection
                for license_detection in license_detections
                if not is_paragraph_debian_packaging(license_detection.paragraph)
            ]

        expressions = [
            license_detection.license_expression_object
            for license_detection in license_detections
            if license_detection.license_expression_object != None
        ]

        if expressions:
            license_expression = str(combine_expressions(expressions, unique=False))
        else:
            license_matches = list(self.license_matches)
            if license_matches:
                license_expression = get_license_expression_from_matches(license_matches)
            else:
                raise_no_license_found_error(location=self.location)

        if simplify_licenses:
            return dedup_expression(license_expression=license_expression)
        else:
            return license_expression

    def detect_license(self):
        """
        Return a list of LicenseDetection objects found in paragraphs.
        """
        # TODO: We should also track line numbers in the file where a license was found
        license_detections = []
        edebian_copyright = EnhancedDebianCopyright(debian_copyright=self.debian_copyright)

        debian_licensing = DebianLicensing.from_license_paragraphs(
            paras_with_license=edebian_copyright.paragraphs_with_license_text
        )

        license_detections.extend(debian_licensing.license_detections)

        header_paragraph = edebian_copyright.header_paragraph
        if header_paragraph.license.name:
            header_license_detections = self.get_license_detections(
                paragraph=header_paragraph,
                debian_licensing=debian_licensing,
            )
            license_detections.extend(header_license_detections)

        for file_paragraph in edebian_copyright.file_paragraphs:
            files_license_detections = self.get_license_detections(
                paragraph=file_paragraph,
                debian_licensing=debian_licensing,
            )
            license_detections.extend(files_license_detections)

        license_detections.extend(
            self.detect_license_in_other_paras(
                other_paras=edebian_copyright.other_paragraphs
            )
        )

        self.license_detections = license_detections

    @staticmethod
    def get_license_detections(paragraph, debian_licensing):
        """
        Return a LicenseDetection object from header and files paragraphs.

        `debian_licensing` is a DebianLicensing object used to drive detection
        such that it is aware of license symbols and references.
        """
        license_detections = []

        name = paragraph.license.name

        if not name:
            license_detections.append(
                get_license_detection_from_nameless_paragraph(paragraph=paragraph)
            )
            return license_detections

        license_field_detection = debian_licensing.get_license_detection_from_license_field(paragraph)
        license_detections.append(license_field_detection)

        other_field_detections = get_license_detections_from_other_fields(paragraph) or []
        license_detections.extend(other_field_detections)

        return license_detections

    @staticmethod
    def detect_license_in_other_paras(other_paras):
        """
        Run license Detection on the entire paragraph text and return result in a
        License Detection object.

        `other_paras` is a list of CatchAllParagraph paragraphs.
        """
        license_detections = []

        for paragraph in other_paras:
            for field_name, field_value in paragraph.to_dict().items():
                start_line, _ = paragraph.get_field_line_numbers(field_name)

                matches = get_license_matches_from_query_string(
                    query_string=field_value,
                    start_line=start_line,
                )
                if not matches:
                    continue

                normalized_expression = get_license_expression_from_matches(
                    license_matches=matches,
                )

                license_detections.append(
                    LicenseDetection(
                        paragraph=paragraph,
                        license_expression_object=normalized_expression,
                        license_matches=matches,
                    )
                )

        return license_detections


class NoLicenseFoundError(Exception):
    """
    Raised when there is no license detected in a debian copyright file.
    """


def raise_no_license_found_error(location):
    msg = f'Debian Copyright file does not have any licenses detected in it. Location: {location}'
    raise NoLicenseFoundError(msg)


class DebianCopyrightStructureError(Exception):
    """
    Raised when a structured debian copyright file has discrepancies.
    """


# These are based on `/usr/share/common-licenses/`
# this is a lower case mapping of debian license symbol -> scancode license key
common_licenses = {
    'apache-2.0': 'apache-2.0',
    'apache-2.0+': 'apache-2.0',
    'artistic': 'artistic-perl-1.0',
    'bsd': 'bsd-new',

    'gpl': 'gpl-1.0-plus',
    'gpl+': 'gpl-1.0-plus',
    'gpl-1': 'gpl-1.0',
    'gpl-1+': 'gpl-1.0-plus',
    'gpl-2': 'gpl-2.0',
    'gpl-2+': 'gpl-2.0-plus',
    'gpl-3': 'gpl-3.0',
    'gpl-3+': 'gpl-3.0-plus',

    'lgpl': 'lgpl-2.0-plus',
    'lgpl+': 'lgpl-2.0-plus',
    'lgpl-2': 'lgpl-2.0',
    'lgpl-2+': 'lgpl-2.0-plus',
    'lgpl-2.1': 'lgpl-2.1',
    'lgpl-2.1+': 'lgpl-2.1-plus',
    'lgpl-3': 'lgpl-3.0',
    'lgpl-3+': 'lgpl-3.0-plus',

    'gfdl': 'gfdl-1.1-plus',
    'gfdl+': 'gfdl-1.1-plus',
    'gfdl-1.2': 'gfdl-1.2',
    'gfdl-1.2+': 'gfdl-1.2-plus',
    'gfdl-1.3': 'gfdl-1.3',
    'gfdl-1.3+': 'gfdl-1.3-plus',

    'cc0-1.0': 'cc0-1.0',
    'mpl-1.1': 'mpl-1.1',
    'mpl-2.0': 'mpl-2.0',
    'mpl-1.1+': 'mpl-1.1',
    'mpl-2.0+': 'mpl-2.0',
}


@attr.s
class DebianLicenseSymbol:
    """
    This represents a license key as found in a License: field of a
    Debian Copyright File and the corresponding list of LicenseMatch objects.
    This object is suitable to be used as a license_expression.LicenseSymbolLike object.
    """
    key = attr.ib()
    is_exception = attr.ib(default=False)
    matches = attr.ib(default=attr.Factory(list))

    def get_matched_expression(self, licensing=Licensing()):
        """
        Return a single license_expression.LicenseExpression object crafted
        from the list of LicenseMatch objects.
        """
        assert self.matches, f'Cannot build expression from empty matches: {self}'
        if len(self.matches) > 1:
            expression = licensing.AND(
                *[match.rule.license_expression_object for match in self.matches]
            )
        else:
            expression = self.matches[0].rule.license_expression_object

        return expression


@attr.s
class CopyrightDetection:
    """
    Represent copyright detections for a single paragraph in a debian copyright file.
    """
    paragraph = attr.ib()
    copyrights = attr.ib()


@attr.s
class LicenseDetection:
    """
    Represent license detections for a single paragraph in a debian copyright file.
    """
    paragraph = attr.ib()
    license_expression_object = attr.ib()
    license_matches = attr.ib(default=attr.Factory(list))

    def is_detection_reportable(self):
        """
        Return True if this detection is reportable. LicenseDetection contain
        both license texts detection in license paragraphs and in file/other
        paragraphs. We want to only report license detections that are in
        files/other paragraph with an existing `license_expression_object`.

        Also, for "declared licenses" other paragraphs are not reported.
        """
        # FIXME: this is problematic: we should report solo license paragraphs
        # FIXME: handle the "declared license" separately

        if isinstance(self.paragraph, CopyrightLicenseParagraph):
            # FIXME: we should always report!
            return False
        elif isinstance(self.paragraph, CatchAllParagraph):
            return True

        elif self.paragraph.license.text:
            # FIXME: we should always report!
            if self.license_expression_object is None:
                # FIXME: a paragraph with a license text MUST have a license...
                # if anything an unknown license

                return False

        return True


@attr.s
class DebianLicensing:
    """
    This object exposes license expression parsing that is aware of the specific context
    of a copyright file.
    Within a copyright file we have a set of custom license symbols; in general
    we also have common debian licenses. These two combined form the set of symbols
    we can use to parse the license declaration in each of the paragraphs.
    """
    licensing = attr.ib()

    # A mapping of License key to list of LicenseMatch objects
    license_matches_by_symbol = attr.ib()

    # A mapping of LicenseSymbols to LicenseExpression objects
    # LicenseSymbol.key is the license name for the and the LicenseExpression is created
    # by combining LicenseMatch objects for license detections on the license text
    substitutions = attr.ib()

    # List of license name strings that could not be parsed
    unparsable_expressions = attr.ib()

    # List of LicenseDetection objects
    license_detections = attr.ib()

    @classmethod
    def from_license_paragraphs(cls, paras_with_license):
        """
        Return a DebianLicensing object built from a list of DebianCopyright paragraph
        objects.
        """
        # FIXME: we should also detect licenses in comments
        # rename to plural in case  list
        result = DebianLicensing.parse_paras_with_license_text(
            paras_with_license=paras_with_license
        )
        license_matches_by_symbol, license_detections = result

        expression_symbols, unparsable_expressions = DebianLicensing.build_symbols(
            license_matches_by_symbol=license_matches_by_symbol
        )

        substitutions = {}
        for sym in expression_symbols:
            ds = sym.wrapped
            dse = ds.get_matched_expression()
            substitutions[sym] = dse

        licensing = Licensing(symbols=expression_symbols)

        return cls(
            licensing=licensing,
            license_matches_by_symbol=license_matches_by_symbol,
            substitutions=substitutions,
            unparsable_expressions=unparsable_expressions,
            license_detections=license_detections,
        )

    def get_license_detection_from_license_field(self, paragraph):
        """
        Return a LicenseDetection object built from a license or file
        `paragraph` (e.g. with a "license" field).
        """
        exp = paragraph.license.name
        cleaned = clean_expression(exp)
        normalized_expression = None
        matches = []

        start_line, end_line = paragraph.get_field_line_numbers('license')
        if TRACE:
            logger_debug(
                'get_license_detection_from_license_field:',
                'start_line, end_line:', start_line, end_line,
            )

        try:
            debian_expression = self.licensing.parse(cleaned)
            if self.debian_expression_can_be_substituted(debian_expression):
                normalized_expression = debian_expression.subs(self.substitutions)
            else:
                text = f'License: {cleaned}'
                matches = get_license_matches_from_query_string(
                    query_string=text,
                    start_line=start_line,
                )
                if matches:
                    normalized_expression = get_license_expression_from_matches(
                        license_matches=matches,
                    )

        except ExpressionError:
            # If Expression fails to parse we lookup exact string matches in License paras
            # which also failed to parse
            if cleaned in self.unparsable_expressions:
                matches_unparsable_expression = (
                    # FIXME: add line number trackinhg... there is an offset to apply there
                    self.license_matches_by_symbol.get(cleaned)
                )
                normalized_expression = get_license_expression_from_matches(
                    license_matches=matches_unparsable_expression,
                )

        if normalized_expression == None:
            # Case where expression is not parsable and the same expression is not present in
            # the license paragraphs
            matches = add_unknown_matches(name=exp, text=None)
            normalized_expression = get_license_expression_from_matches(
                license_matches=matches
            )

        return LicenseDetection(
            paragraph=paragraph,
            license_expression_object=normalized_expression,
            license_matches=matches,
        )

    @staticmethod
    def parse_paras_with_license_text(paras_with_license):
        """
        Return a dictionary `license_matches_by_symbol` with declared licenses
        as keys and a list of License Detections from parsing
        ``paras_with_license`` paragraphs that contain a license text.
        """
        license_detections = []
        license_matches_by_symbol = {}

        for license_paragraph in paras_with_license:
            name = license_paragraph.license.name.lower()
            start_line, _ = license_paragraph.get_field_line_numbers('license')

            text = license_paragraph.license.text
            text_matches = get_license_matches_from_query_string(
                query_string=text,
                # we use +1 on line since we are not detecting in the name, but in the text
                start_line=start_line + 1,
            )

            matches = []

            common_license = common_licenses.get(name)
            if common_license:
                # For common license the name has a meaning, so create a
                # synthetic match on that
                common_license_tag = f'License: {name}'

                common_license_matches = get_license_matches_from_query_string(
                    query_string=common_license_tag,
                    start_line=start_line,
                )
                if len(common_license_matches) != 1:
                    raise Exception(
                        'Rules for common License is missing: {common_license_tag}'
                    )

                common_license_match = common_license_matches[0]
                matches.append(common_license_match)

                # Raise Exception when all the license expressions of the
                # matches are not consistent with the common_license_match
                if not have_consistent_licenses_with_match(
                    matches=text_matches, reference_match=common_license_match
                ):
                    # TODO: Add unknown matches if matches are not consistent
                    # raise Exception(f'Inconsistent Licenses: {common_license_match} {matches}')
                    pass

                # TODO: Add unknown matches if matches are weak
                matches.extend(text_matches)
            else:
                # TODO: Add unknown matches if matches are weak
                if text_matches:
                    matches.extend(text_matches)
                else:
                    matches.extend(add_unknown_matches(name=name, text=text))

            if license_paragraph.comment:
                comment = license_paragraph.comment.text
                if comment and comment.strip():
                    start_line, _ = license_paragraph.get_field_line_numbers('comment')
                    comment_matches = get_license_matches_from_query_string(
                        query_string=comment,
                        start_line=start_line,
                    )

                    # If license detected in the comments are not consistent with
                    # the license detected in text, add the license matches detected
                    # in the comment to be reported

                    if comment_matches:
                        if not have_consistent_licenses(
                            matches=text_matches, reference_matches=comment_matches
                        ):
                            matches.extend(comment_matches)

            # Clean should also lower
            cleaned = clean_expression(name)
            license_matches_by_symbol[cleaned] = matches

            license_detections.append(
                LicenseDetection(
                    paragraph=license_paragraph,
                    license_expression_object=None,
                    license_matches=matches,
                )
            )

        return license_matches_by_symbol, license_detections

    @staticmethod
    def build_symbols(
        license_matches_by_symbol,
        common_licenses=common_licenses,
    ):
        """
        Return a list of LicenseSymbolLike objects, built from known and common
        licenses. It is expected that license_matches_by_symbol keys are in
        lowercase. Also return a list of unparsable expressions.
        """
        symbols = []
        unparsable_expressions = []
        seen_keys = set()
        for key, matches in license_matches_by_symbol.items():
            sym = DebianLicenseSymbol(key=key, matches=matches)
            try:
                lsym = LicenseSymbolLike(symbol_like=sym)
                symbols.append(lsym)
            except ExpressionError:
                unparsable_expressions.append(key)
            seen_keys.add(key)

        for debian_key, _scancode_key in common_licenses.items():
            if debian_key in seen_keys:
                continue

            common_license_tag = f'License: {debian_key}'
            # TODO: track line numbers??
            matches = get_license_matches_from_query_string(
                query_string=common_license_tag,
            )
            sym = DebianLicenseSymbol(key=debian_key, matches=matches)
            lsym = LicenseSymbolLike(symbol_like=sym)
            symbols.append(lsym)

        return symbols, unparsable_expressions

    def debian_expression_can_be_substituted(self, debian_expression):
        """
        Return True if all the license keys in the debian_expression are either:
        1. present in one of the License paragraphs, OR
        2. are common debian license keys, e.g. one of the common_licenses.
        """
        all_keys = []
        all_keys.extend(list(self.license_matches_by_symbol.keys()))
        all_keys.extend(list(common_licenses.keys()))

        expression_keys = self.licensing.license_keys(debian_expression)

        for key in expression_keys:
            if key in all_keys:
                continue

            return False

        return True


@attr.s
class EnhancedDebianCopyright:
    debian_copyright = attr.ib()

    @staticmethod
    def is_machine_readable_copyright(text):
        """
        Return True if a text is for a machine-readable copyright format.

        This extends debian_inspector.copyright.is_machine_readable_copyright to
        support more cases.
        """
        return text and text[:100].lower().startswith((
            'format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0',
            'format: http://www.debian.org/doc/packaging-manuals/copyright-format/1.0',
            'format: http://anonscm.debian.org/viewvc/dep/web/deps/dep5',
            'format: http://svn.debian.org/wsvn/dep/web/deps/dep5',
            'format: http://dep.debian.net/deps/dep5',
        ))

    def get_paragraphs_by_type(self, paragraph_type):
        return [
            paragraph
            for paragraph in self.debian_copyright.paragraphs
            if isinstance(paragraph, paragraph_type)
        ]

    @property
    def header_paragraph(self):
        """
        Return the header paragraph or None. Raise an Exception if there is
        more than one header paragraph.
        """
        header_paras = self.get_paragraphs_by_type(CopyrightHeaderParagraph)

        if not header_paras:
            return

        if len(header_paras) != 1:
            raise Exception(
                f'Multiple Header paragraphs in copyright file', *header_paras
            )

        return header_paras[0]

    @property
    def file_paragraphs(self):
        return self.get_paragraphs_by_type(CopyrightFilesParagraph)

    @property
    def license_paragraphs(self):
        return self.get_paragraphs_by_type(CopyrightLicenseParagraph)

    @property
    def paragraphs_with_license_text(self):
        text_paragraphs = self.get_paragraphs_by_type(
            paragraph_type=(
                CopyrightHeaderParagraph,
                CopyrightFilesParagraph,
                CopyrightLicenseParagraph,
            )
        )

        return [p for p in text_paragraphs if p.license.text]

    @property
    def other_paragraphs(self):
        other_paras = [
            p  for p in self.get_paragraphs_by_type(CopyrightLicenseParagraph)
            if not p.license.name
        ]
        other_paras.extend(self.get_paragraphs_by_type(CatchAllParagraph))
        return other_paras

    @property
    def duplicate_license_paragraphs(self):

        seen_license_names = set()
        duplicate_license_paras = []

        paragraphs = self.get_paragraphs_by_type(CopyrightLicenseParagraph)
        for paragraph in paragraphs:

            lic_name = paragraph.license.name
            if not lic_name:
                continue

            if lic_name not in seen_license_names:
                seen_license_names.add(lic_name)
            else:
                duplicate_license_paras.append(paragraph)

        return duplicate_license_paras

    @property
    def license_nameless_paragraphs(self):
        paragraphs = self.get_paragraphs_by_type(
            paragraph_type=(CopyrightFilesParagraph, CopyrightLicenseParagraph,)
        )
        return [p for p in paragraphs if p.license and not p.license.name]

    @property
    def is_all_licenses_used(self):
        # FIXME: If `lgpl` isn't used but there is `lgpl+` somwhere this
        # wouldn't detect correctly. Could be parsed, normalized and the
        # individual components could be matched exactly.

        expressions_with_text = []
        expressions_without_text = []

        for paragraph in self.license_paragraphs:
            if paragraph.license.name:
                expressions_with_text.append(paragraph.license.name)

        for paragraph in self.file_paragraphs:
            if paragraph.license.name and not paragraph.license.text:
                expressions_without_text.append(paragraph.license.name)

        header_paragraph = self.header_paragraph
        if header_paragraph.license.name and not header_paragraph.license.text:
            expressions_without_text.append(header_paragraph.license.name)

        for expression_with_text in expressions_with_text:
            expression_used = False

            for expression_without_text in expressions_without_text:

                if expression_with_text in expression_without_text:
                    expression_used = True

            if not expression_used:
                return False

        return True

    @property
    def is_all_licenses_expressions_parsable(self):
        licensing = Licensing()
        license_expressions = self.get_all_license_expressions()

        for expression in license_expressions:
            if ',' in expression:
                expression = clean_debian_comma_logic(expression)

            try:
                licensing.parse(expression)
            except ExpressionError:
                return False

        return True

    def get_all_license_expressions(self):
        """
        Return a list of all the license expressions detected in this copyright
        file.
        """
        license_expressions = []

        for paragraph in self.debian_copyright.paragraphs:
            if isinstance(
                paragraph,
                (CopyrightHeaderParagraph, CopyrightLicenseParagraph, CopyrightLicenseParagraph)
            ) and paragraph.license.name:
                license_expressions.append(paragraph.license.name)

        return license_expressions

    def get_consistentcy_errors(self):

        consistency_errors = []

        if self.other_paragraphs:
            consistency_errors.append((
                'Paragraphs other than Header/File/License paragraphs present in structured'
                'debian copyright or there is a formatting issue in a paragraph'
            ))

        if not self.license_paragraphs:
            consistency_errors.append(
                'No License paragraphs are present in structured debian copyright file'
            )

        if not self.file_paragraphs:
            consistency_errors.append(
                'No Files paragraphs are present in structured debian copyright file'
            )

        if self.duplicate_license_paragraphs:
            consistency_errors.append((
                'Two License Paragraphs having the same License Name present in'
                'debian copyright file'
            ))

        if self.license_nameless_paragraphs:
            consistency_errors.append(
                'Paragraphs without license names present in debian copyright file'
            )

        if not self.is_all_licenses_used:
            consistency_errors.append(
                'Some of the License Paragraphs are not referenced in Files/Header paragraphs'
            )

        if not self.is_all_licenses_expressions_parsable:
            consistency_errors.append(
                 'Some license expressions present in paragraphs are not valid'
            )

        return consistency_errors


def copyright_detector(location):
    """
    Return lists of detected copyrights, authors & holders in file at location.
    """
    if location:
        from cluecode.copyrights import detect_copyrights

        copyrights = []

        for detection in detect_copyrights(
            location,
            include_copyrights=True,
            include_holders=False,
            include_authors=False,
        ):
            copyrights.append(detection.copyright)
        return copyrights


def filter_duplicate_strings(strings):
    """
    Given a list of strings, return only the unique strings, preserving order.
    """
    seen = set()
    filtered = []

    for string in strings:
        if string not in seen:
            seen.add(string)
            filtered.append(string)

    return filtered


def dedup_expression(license_expression, licensing=Licensing()):
    """
    Deduplicate license expressions from `license_expression` string.
    """
    return str(licensing.dedup(license_expression))


def clean_debian_comma_logic(exp):
    """
    Convert an ``exp`` expression with Debian specific logic regarding comma to
    a parsable license expression.

    For example:
    >>> clean_debian_comma_logic('lgpl-3 or gpl-2, and apache-2.0')
    '(lgpl-3 or gpl-2) and (apache-2.0)'
    """
    subexps = []
    while ', and' in exp:
        exp, _and_op, right = exp.rpartition(', and')
        subexps.insert(0, right)
    subexps.insert(0, exp)
    wrapped = [f'({i.strip()})' for i in subexps]
    cleaned = ' and '.join(wrapped)
    return cleaned


def clean_expression(text):
    """
    Return a cleaned license expression text by normalizing the syntax so it can
    be parsed. Also apply specific string-level substitutions using a table.

    This substitution table has been derived from a large collection of most
    copyright files from Debian (about 320K files from circa 2019-11) and Ubuntu
    (about 200K files from circa 2020-06)
    """
    if not text:
        return text

    text = text.lower()
    text = ' '.join(text.split())
    if ',' in text:
        text = clean_debian_comma_logic(text)

    substitutions = {
        "at&t": "at_and_t",
        "ruby's": "rubys",
        "vixie's": "vixie",
        "bsd-3-clause~o'brien": "bsd-3-clause_o_brien",
        "core security technologies-pysmb": "core-security-technologies-pysmb",
        "|": " or ",
        "{fonts-open-sans}": "fonts-open-sans",
        "{texlive-fonts-extra}": "texlive-fonts-extra",
        " [ref": "_ref",
        "]": "_",
        "zpl 2.1": "zpl-2.1",
        "public domain": "public-domain",
        "gpl-2 (with openssl and foss license exception)": "(gpl-2 with openssl) and (gpl-2 with foss_license_exception)",
        "font embedding": "font_embedding",
        "special exception for compressed executables": "special_exception_for_compressed_executables",
        "exception, origin admission": "exception_origin_admission",
        "gcc runtime library exception": "gcc_runtime_library_exception",
        "special font exception": "special_font_exception",
        "the qt company gpl exception 1.0": "the_qt_company_gpl_exception_1.0",
        "section 7 exception": "section_7_exception",
        "g++ use exception": "g_use_exception",
        "gstreamer link exception": "gstreamer_link_exception",
        "additional permission": "additional_permission",
        "autoconf ": "autoconf_",
        "(lgpl-2.1 or lgpl-3) with qt exception": "lgpl-2.1 with qt_exception or lgpl-3 with qt_exception",
        "font exception (musescore)": "font_exception_musescore",
        "font exception (freefont)": "font_exception_freefont",
        "font exception (lilypond)": "font_exception_lilypond",
        "warranty disclaimer": "warranty_disclaimer",
        "bison exception 2.2": "bison_exception_2.2",
        "zlib/libpng": "zlib_libpng",
        "zlib/png": "zlib_png",
        "mit/x11": "mit_x11",
        "x/mit": "x_mit",
        "mit/x": "mit_x",
        "x11/mit": "x11_mit",
        "-clause/": "-clause_",
        "bsd/superlu": "bsd_superlu",
        "expat/mit": "expat_mit",
        "mit/expat": "mit_expat",
        "openssl/ssleay": "openssl_ssleay",
        "cc0/publicdomain": "cc0_publicdomain",
        "univillinois/ncsa": "univillinois_ncsa",
        " linking exception": "_linking_exception",
        " qt ": "_qt_",
        " exception": "_exception",
    }

    for source, target in substitutions.items():
        cleaned_text = text.replace(source, target)

    return cleaned_text


def remove_known_license_intros(license_matches):
    """
    Return a filtered ``license_matches`` list of LicenseMatch objects removing
    spurious matches to license introduction statements (e.g.
    `is_license_intro` Rules.)

    A common source of false positive license detections in unstructured files
    are license introduction statements that are immediately followed by a
    license notice. In these cases, the license introduction can be discarded as
    this is for the license match that follows it.
    """

    return [match for match in license_matches if not is_known_license_intro(match)]


def is_known_license_intro(license_match):
    """
    Return True if `license_match` LicenseMatch object is matched completely to
    a unknown license intro present as a Rule.
    """
    from licensedcode.match_aho import MATCH_AHO_EXACT

    return (
        license_match.rule.is_license_intro
        and (
            license_match.matcher == MATCH_AHO_EXACT
            or license_match.coverage() == 100
        )
    )


def add_unknown_matches(name, text):
    """
    Return a list of LicenseMatch (with a single match) created for an unknown
    license match with the ``name`` license and license ``text``.

    Return an empty list if both name and text are empty.
    """
    name = name or ''
    text = text or ''
    if not name and not text:
        return []

    # FIXME: track lines
    license_text = f'{name}\n{text}'.strip()
    expression_str = 'unknown-license-reference'

    idx = get_index()
    query = Query(query_string=license_text, idx=idx)

    query_run = query.whole_query_run()

    match_len = len(query_run)
    match_start = query_run.start
    matched_tokens = query_run.tokens

    qspan = Span(range(match_start, query_run.end + 1))
    ispan = Span(range(0, match_len))
    len_legalese = idx.len_legalese
    hispan = Span(p for p, t in enumerate(matched_tokens) if t < len_legalese)

    unknown_rule = UnknownRule(
        license_expression=expression_str,
        text=license_text,
        length=match_len,
    )

    match = LicenseMatch(
        rule=unknown_rule,
        qspan=qspan,
        ispan=ispan,
        hispan=hispan,
        query_run_start=match_start,
        matcher=MATCHER_UNKNOWN,
        query=query_run.query,
    )

    matches = [match]
    set_matched_lines(matches, query.line_by_pos)
    return matches


@attr.s(slots=True, repr=False)
class UnknownRule(Rule):
    """
    A specialized rule object that is used for the special case of unknown
    matches in debian copyright files.

    Since there can be a lot of unknown licenses in a debian copyright file, the
    rule and the LicenseMatch objects for these are built at matching time.
    """

    def __attrs_post_init__(self, *args, **kwargs):
        self.identifier = 'debian-' + self.license_expression
        expression = self.licensing.parse(self.license_expression)
        self.license_expression = expression.render()
        self.license_expression_object = expression
        self.is_license_tag = True
        self.is_small = False
        self.relevance = 100
        self.has_stored_relevance = True

    def load(self):
        raise NotImplementedError

    def dump(self):
        raise NotImplementedError


def get_license_detections_from_other_fields(paragraph):
    """
    Return a list of LicenseDetection found in a ``paragraph`` comment,
    disclaimer or extra_data fields, e.g. all but the "license" field
    """

    def detect_license_and_save(fname, fvalue):
        if fvalue and fvalue.strip():
            fstart_line, fend_line = paragraph.get_field_line_numbers(fname)
            if TRACE:
                logger_debug('get_license_detections_from_other_fields: detect_license_and_save: matches', fstart_line, fend_line)

            fdetection = get_license_detection_from_extra_data(
                query_string=fvalue,
                paragraph=paragraph,
                start_line=fstart_line,
            )

            if fdetection:
                license_detections.append(fdetection)

    license_detections = []
    for field_name in ('comment', 'disclaimer',):
        field = getattr(paragraph, field_name, None)
        if not field:
            continue
        detect_license_and_save(fname=field_name, fvalue=field.text)

    if paragraph.extra_data:
        for field_name, field_value in paragraph.extra_data.items():
            detect_license_and_save(fname=field_name, fvalue=field_value)

    return license_detections


def get_license_detection_from_extra_data(query_string, paragraph, start_line):
    """
    Return a LicenseDetection from a ``query_string`` starting at ``start_line``
    found in ``paragraph``.
    """
    matches = get_license_matches_from_query_string(
        query_string=query_string,
        start_line=start_line,
    )
    matches = remove_known_license_intros(matches)
    if matches:
        normalized_expression = get_license_expression_from_matches(
            license_matches=matches
        )
        return LicenseDetection(
            paragraph=paragraph,
            license_expression_object=normalized_expression,
            license_matches=matches,
        )


def get_license_detection_from_nameless_paragraph(paragraph):
    """
    Return a LicenseDetection object built from any paragraph without a license
    name.
    """
    assert not paragraph.license.name
    start_line, _ = paragraph.get_field_line_numbers('license')
    matches = get_license_matches_from_query_string(
        query_string=paragraph.license.text,
        start_line=start_line,
    )
    if TRACE:
        logger_debug('get_license_detection_from_nameless_paragraph: matches', matches)

    if not matches:
        matches = add_unknown_matches(name=None, text=paragraph.license.text)
        normalized_expression = get_license_expression_from_matches(
            license_matches=matches
        )
    else:
        # TODO: Add unknown matches if matches are weak
        normalized_expression = get_license_expression_from_matches(
            license_matches=matches
        )

    return LicenseDetection(
        paragraph=paragraph,
        license_expression_object=normalized_expression,
        license_matches=matches,
    )


def have_consistent_licenses(matches, reference_matches):
    """
    Return true if all the license of the matches list of LicenseMatch have the
    same license as all the licenses of the reference_matches list of
    LicenseMatch.
    """
    for reference_match in reference_matches:
        if not have_consistent_licenses_with_match(
            matches=matches,
            reference_match=reference_match,
        ):
            return False
    return True


def have_consistent_licenses_with_match(matches, reference_match):
    """
    Return true if all the license of the matches list of LicenseMatch have the
    same license as the reference_match LicenseMatch.
    """
    for match in matches:
        if not reference_match.same_licensing(match):
            return False
    return True


def is_paragraph_debian_packaging(paragraph):
    """
    Return True if the `paragraph` is a CopyrightFilesParagraph that applies
    only to the Debian packaging
    """
    return isinstance(
        paragraph, CopyrightFilesParagraph
    ) and paragraph.files.values == ['debian/*']


def is_paragraph_primary_license(paragraph):
    """
    Return True if the `paragraph` is a CopyrightFilesParagraph that contains
    the primary license.
    """
    return isinstance(
        paragraph, CopyrightFilesParagraph
    ) and paragraph.files.values == ['*']
