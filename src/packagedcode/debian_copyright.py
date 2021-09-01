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
from itertools import chain

import attr
from debian_inspector.copyright import DebianCopyright
from debian_inspector.copyright import CatchAllParagraph
from debian_inspector.copyright import CopyrightFilesParagraph
from debian_inspector.copyright import CopyrightLicenseParagraph
from debian_inspector.copyright import CopyrightHeaderParagraph
from license_expression import Licensing
from license_expression import ExpressionError
from license_expression import LicenseSymbolLike

from licensedcode.models import Rule
from licensedcode.match import LicenseMatch
from licensedcode.query import Query
from licensedcode.spans import Span
from licensedcode.cache import get_index
from licensedcode.match import set_lines
from packagedcode.utils import combine_expressions
from packagedcode.licensing import get_license_matches
from packagedcode.licensing import get_license_expression_from_matches
from textcode.analysis import unicode_text

"""
Detect licenses in Debian copyright files. Can handle dep-5 machine-readable
copyright files, pre-dep-5 mostly machine-readable copyright files and
unstructured copyright files.
"""

TRACE = os.environ.get('SCANCODE_DEBUG_PACKAGE', False) or False

MATCHER_UNKNOWN = '5-unknown'


def logger_debug(*args):
    pass


if TRACE:
    import logging

    logger = logging.getLogger(__name__)
    # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(" ".join(isinstance(a, str) and a or repr(a) for a in args))


def parse_copyright_file(location, check_consistency=False):
    """
    Return a DebianDetector Object containing copyright and license detections
    extracted from the debain copyright file at `location`.

    If `check_consistency` is True, check if debian copyright file is
    consistently structured according to the guidelines specified at
    https://www.debian.org/doc/packaging-manuals/copyright-format/1.0
    """
    if not location or not location.endswith('copyright'):
        return

    if EnhancedDebianCopyright.is_machine_readable_copyright(unicode_text(location)):
        dc = StructuredCopyrightProcessor.from_file(
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
        logger_debug(f'parse_copyright_file: {dc}')

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
        Returns a DebianDetector object with License and Copyright detections.
        """
        return NotImplementedError

    def get_copyright(self, *args, **kwargs):
        """
        Return a copyright string suitable to use as a DebianPackage.copyright.
        """
        return NotImplementedError

    def get_license_expression(self, *args, **kwargs):
        """
        Return a license expression string suitable to use as a
        DebianPackage.license_expression.
        """
        return NotImplementedError

    def get_declared_license(self, *args, **kwargs):
        """
        Return a list of declared license string suitable to use as a
        DebianPackage.declared_license.
        """
        return NotImplementedError


@attr.s
class UnstructuredCopyrightProcessor(DebianDetector):
    # List of LicenseMatches in an unstructured file
    license_matches = attr.ib(default=attr.Factory(list))

    # List of detected copyrights in an unstructured file
    detected_copyrights = attr.ib(default=attr.Factory(list))

    @classmethod
    def from_file(cls, location, check_consistency=False):
        """
        Returns a UnstructuredCopyrightProcessor object created from a
        unstructured debian copyright file, after detecting license and
        copyrights.

        If `check_consistency` is True, will always add a consistency error as
        unstructured copyright files are not consistent.
        """
        dc = cls(location=location)

        if check_consistency:
            dc.consistency_errors.append('Debian Copyright File is unstructured')

        dc.detected_copyrights = copyright_detector(location)

        content = unicode_text(location)
        dc.detect_license(query_string=content)

        return dc

    @property
    def primary_license(self):
        """
        Returns None as primary license cannot be detected in an unstructured
        debian copyright file.
        """
        return None

    def get_declared_license(self, *args, **kwargs):
        """
        Returns None as there is no declared licenses in an unstructured debian
        copyright file.
        """
        return None

    def get_license_expression(
        self,
        simplify_licenses=False,
        *args, **kwargs
    ):
        """
        Returns a license expression string for the corresponding debian
        copyright file.

        If simplify_licenses is True, uses Licensing.dedup() to simplify the
        license expression.
        """
        matches = self.license_matches
        detected_expressions = [match.rule.license_expression for match in matches]
        license_expression = combine_expressions(detected_expressions, unique=False)

        if simplify_licenses:
            return dedup_expression(license_expression=license_expression)
        else:
            return license_expression

    def get_copyright(self, *args, **kwargs):
        """
        Returns a copyright string, each in a line, with all the copyright
        detections in a unstrucutred debian copyright file.
        """
        return '\n'.join(self.detected_copyrights)

    def detect_license(self, query_string):
        """
        Return a list of LicenseMatch objects which has the detected license
        matches in `query_string`, or has an UnknownMatch if no license is
        detected.
        """
        license_matches = remove_known_license_intros(
            license_matches=get_license_matches(query_string=query_string)
        )

        if not license_matches:
            # we have no match: return an unknown key
            license_matches = add_unknown_matches(name=None, text=query_string)

        self.license_matches = license_matches


@attr.s
class StructuredCopyrightProcessor(DebianDetector):
    # List of LicenseDetection objects having license matches from files/header paragraphs
    license_detections = attr.ib(default=attr.Factory(list))

    # List of CopyrightDetection objects having copyrights from files/header paragraphs
    copyright_detections = attr.ib(default=attr.Factory(list))

    # A cached DebianCopyright object built from the copyright file at location
    debian_copyright = attr.ib(default=None)

    # License present in header or 'files: *' paragraph for a structured debian copyright file
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
        edc = EnhancedDebianCopyright(debian_copyright=debian_copyright)
        dc = cls(location=location, debian_copyright=debian_copyright)
        dc.detect_license()
        dc.detect_copyrights()
        dc.get_primary_license()

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

    def get_primary_license(self):
        """
        Returns a license expression string which is the primary license for the
        debian copyright file.

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
        self, filter_duplicates=False, skip_debian_packaging=False, *args, **kwargs
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
        *args, **kwarg,
    ):
        """
        Return copyrights collected from a structured file.

        If `unique_copyrights` is True, only unique copyrights are returned.
        If `skip_debian_packaging` is True, skips the declared license for
        `Files: debian/*` paragraph.
        """
        declarable_copyrights = []
        seen_copyrights = set()
        # TODO: Only Unique Holders (copyright without years) should be reported

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
        Return a list of CopyrightDetection objects from a ``debian_copyright``
        DebianCopyright object.
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

        # We detect plain copyrights  if we didn't find any
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
        *args, **kwargs
    ):
        """
        Return a license expression string as built from available license
        detections.

        If `simplify_licenses` is True, license expressions are deduplicated by
        Licensing.dedup() and then returned.
        If `skip_debian_packaging` is True, skips the declared license for
        `Files: debian/*` paragraph.
        """
        if not self.license_detections:
            raise_no_license_found_error(location=self.location)

        license_detections = [
            license_detection
            for license_detection in self.license_detections
            if license_detection.is_detection_declarable()
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
        Return a list of LicenseDetection objects from a ``debian_copyright``
        DebianCopyright object.
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
            self.detect_license_in_other_paras(other_paras=edebian_copyright.other_paragraphs)
        )

        self.license_detections = license_detections

    @staticmethod
    def get_license_detections(paragraph, debian_licensing):
        """
        Return a LicenseDetection object from header/files paras in structured
        debian copyright file.

        `debian_licensing` is a DebianLicensing object.
        """
        license_detections = []

        name = paragraph.license.name
        if not name:
            license_detections.append(
                get_license_detection_from_nameless_paragraph(paragraph=paragraph)
            )
            return license_detections

        license_detections.append(debian_licensing.get_license_detection(paragraph))
        extra_license_detections = get_license_detections_from_extra_data(paragraph)
        if extra_license_detections:
            license_detections.extend(extra_license_detections)
        return license_detections

    @staticmethod
    def detect_license_in_other_paras(other_paras):
        """
        Run license Detection on the entire paragraph text and return result in a
        License Detection object.

        `other_paras` is a list of CatchAllParagraph objects detected in the debian
        copyright file.
        """
        license_detections = []

        for other_para in other_paras:

            extra_data = other_para.to_dict()

            for _field_name, field_value in extra_data.items():

                license_matches = get_license_matches(query_string=field_value)
                if not license_matches:
                    continue

                normalized_expression = get_license_expression_from_matches(
                    license_matches=license_matches,
                )
                license_detections.append(
                    LicenseDetection(
                        paragraph=other_para,
                        license_expression_object=normalized_expression,
                        license_matches=license_matches,
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


# These are based on `/usr/share/common-license/`
common_licenses = {
    'apache-2.0': 'apache-2.0',
    'apache-2.0+': 'apache-2.0',
    'artistic': 'artistic-perl-1.0',
    'bsd': 'bsd-new',
    'cc0-1.0': 'cc0-1.0',
    'gfdl+': 'gfdl-1.1-plus',
    'gfdl-1.2+': 'gfdl-1.2-plus',
    'gfdl-1.3+': 'gfdl-1.3-plus',
    'gpl+': 'gpl-1.0-plus',
    'gpl-1+': 'gpl-1.0-plus',
    'gpl-2+': 'gpl-2.0-plus',
    'gpl-3+': 'gpl-3.0-plus',
    'lgpl+': 'lgpl-2.0-plus',
    'lgpl-2+': 'lgpl-2.0-plus',
    'lgpl-2.1+': 'lgpl-2.1-plus',
    'lgpl-3+': 'lgpl-3.0-plus',
    'gfdl': 'gfdl-1.1-plus',
    'gfdl-1.2': 'gfdl-1.2',
    'gfdl-1.3': 'gfdl-1.3',
    'gpl': 'gpl-1.0-plus',
    'gpl-1': 'gpl-1.0',
    'gpl-2': 'gpl-2.0',
    'gpl-3': 'gpl-3.0',
    'lgpl': 'lgpl-2.0-plus',
    'lgpl-2': 'lgpl-2.0',
    'lgpl-2.1': 'lgpl-2.1',
    'lgpl-3': 'lgpl-3.0',
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

    def is_detection_declarable(self):
        """
        LicenseDetection objects contain both license texts detection in license/file/other
        paragraphs, and only license detections which are in files paragraph has existing
        `license_expression_object` to report.
        Also, in the case of reporting declared licenses other paragraphs are not reported.
        """
        if isinstance(self.paragraph, CopyrightLicenseParagraph):
            return False
        elif isinstance(self.paragraph, CatchAllParagraph):
            return True

        elif self.paragraph.license.text:
            if self.license_expression_object is None:
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

    def get_license_detection(self, paragraph):
        """
        Return a LicenseDetection object build from a debian copyright file `paragraph`.
        """
        exp = paragraph.license.name
        cleaned = clean_expression(exp)
        normalized_expression = None
        matches = []

        try:
            debian_expression = self.licensing.parse(cleaned)
            if self.debian_expression_can_be_substituted(debian_expression):
                normalized_expression = debian_expression.subs(self.substitutions)
            else:
                text = f'License: {cleaned}'
                matches = get_license_matches(query_string=text)
                if matches:
                    normalized_expression = get_license_expression_from_matches(
                        license_matches=matches,
                    )

        except ExpressionError:
            # If Expression fails to parse we lookup exact string matches in License paras
            # which also failed to parse
            if cleaned in self.unparsable_expressions:
                matches_unparsable_expression = (
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
        Return a dictionary `license_matches_by_symbol` with declared licenses as keys and a list
        of License Detections from parsing paras with license text.
        """
        license_detections = []
        license_matches_by_symbol = {}

        for license_paragraph in paras_with_license:
            name = license_paragraph.license.name.lower()
            # Clean should also lower
            cleaned = clean_expression(name)
            text = license_paragraph.license.text
            text_matches = get_license_matches(query_string=text)
            matches = []

            common_license = common_licenses.get(name)
            if common_license:
                # For common license the name has a meaning, so create a synthetic match on that
                common_license_tag = f'License: {name}'
                common_license_matches = get_license_matches(
                    query_string=common_license_tag
                )
                if len(common_license_matches) != 1:
                    raise Exception(
                        'Rules for common License is missing: {common_license_tag}'
                    )

                common_license_match = common_license_matches[0]
                matches.append(common_license_match)

                # Raise Exception when all the license expressions of the matches are not
                # consistent with the common_license_match
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
                comment_matches = get_license_matches(query_string=comment)

                # If license detected in the comments are not consistent with the license
                # detected in text, add the license matches detected in the comment to be reported
                if comment_matches:
                    if not have_consistent_licenses(
                        matches=text_matches, reference_matches=comment_matches
                    ):
                        matches.extend(comment_matches)

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
    def build_symbols(license_matches_by_symbol, common_licenses=common_licenses):
        """
        Return a list of LicenseSymbolLike objects, built from known and common licenses.
        It is expected that license_matches_by_symbol keys are in lowercase.
        Also return a list of unparsable expressions.
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
            matches = get_license_matches(query_string=common_license_tag)
            sym = DebianLicenseSymbol(key=debian_key, matches=matches)
            lsym = LicenseSymbolLike(symbol_like=sym)
            symbols.append(lsym)

        return symbols, unparsable_expressions

    def debian_expression_can_be_substituted(self, debian_expression):
        """
        Return True if all the license keys in the debian_expression is:
        1. either present in one of the License paragraphs, OR
        2. is a common debian license key. (One of common_licenses)
        Otherwise, return False.
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
            if  not p.license.name
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

        for dtype, value, _start, _end in detect_copyrights(location):
            if dtype == 'copyrights':
                copyrights.append(value)
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
    be parsed. This substitution table has been derived from a large collection
    of most copyright files from Debian (about 320K files from circa 2019-11)
    and Ubuntu (about 200K files from circa 2020-06)
    """
    if not text:
        return text

    text = text.lower()
    text = ' '.join(text.split())
    if ',' in text:
        text = clean_debian_comma_logic(text)

    transforms = {
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

    for source, target in transforms.items():
        cleaned_text = text.replace(source, target)

    return cleaned_text


def remove_known_license_intros(license_matches):
    """
    Returns a list of LicenseMatch objects after removing unknown license intros
    from the `license_matches` list of LicenseMatch objects.

    A common source of unknowns in unstrctured files are many types of license
    intros which are present to introduce a lot of license texts, and as the
    license texts are actually present below and in a different query run, it
    only makes sense to remove known license intros in unstructured license
    files.
    """
    return [
        license_match
        for license_match in license_matches
        if not is_known_license_intro(license_match)
    ]


def is_known_license_intro(license_match):
    """
    Returns True if `license_match` LicenseMatch object is matched completely to
    a unknown license intro present as a Rule.
    """
    from licensedcode.match_aho import MATCH_AHO_EXACT

    if license_match.rule.is_license_intro and (
        license_match.matcher == MATCH_AHO_EXACT or license_match.coverage() == 100
    ):
        return True

    return False


def add_unknown_matches(name, text):
    """
    Return a list of LicenseMatch objects created for an unknown license match.
    Return an empty list if both name and text are empty.
    """
    name = name or ''
    text = text or ''
    license_text = f'License: {name}\n {text}'.strip()
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

    rule = UnknownRule(
        license_expression=expression_str,
        stored_text=license_text,
        length=match_len,
    )

    match = LicenseMatch(
        rule=rule,
        qspan=qspan,
        ispan=ispan,
        hispan=hispan,
        query_run_start=match_start,
        matcher=MATCHER_UNKNOWN,
        query=query_run.query,
    )

    matches = [match]
    set_lines(matches, query.line_by_pos)
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


def get_license_detections_from_extra_data(paragraph):
    license_detections = []
    if paragraph.comment:
        license_detection = get_license_detection_from_extra_data(
            query_string=paragraph.comment.text,
            paragraph=paragraph,
        )
        if license_detection:
            license_detections.append(license_detection)

    if paragraph.extra_data:
        for _field_name, field_value in paragraph.extra_data.items():
            license_detection = get_license_detection_from_extra_data(
                query_string=field_value,
                paragraph=paragraph,
            )
            if license_detection:
                license_detections.append(license_detection)

    return license_detections


def get_license_detection_from_extra_data(query_string, paragraph):
    matches = remove_known_license_intros(
        get_license_matches(query_string=query_string)
    )
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
    matches = get_license_matches(query_string=paragraph.license.text)

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
