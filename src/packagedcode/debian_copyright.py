#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import sys
from os import environ
from os import path

import attr

from debian_inspector.copyright import DebianCopyright
from debian_inspector.copyright import CatchAllParagraph
from debian_inspector.copyright import CopyrightFilesParagraph
from debian_inspector.copyright import CopyrightLicenseParagraph
from debian_inspector.copyright import CopyrightHeaderParagraph
from debian_inspector.copyright import is_machine_readable_copyright

from license_expression import Licensing
from license_expression import ExpressionError
from license_expression import LicenseSymbolLike

from packagedcode.debian import DebianPackage
from packagedcode.licensing import get_normalized_expression
from packagedcode.utils import combine_expressions

from textcode.analysis import unicode_text

"""
Detect licenses in Debian copyright files. Can handle dep-5 machine-readable
copyright files, pre-dep-5 mostly machine-readable copyright files and
unstructured copyright files.
"""

TRACE = environ.get('SCANCODE_DEBUG_PACKAGE', False) or False


def logger_debug(*args):
    pass


if TRACE:
    import logging

    logger = logging.getLogger(__name__)
    # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))


def get_and_set_package_licenses_and_copyrights(package, root_dir):
    """
    Return a tuple of (declared license, license_expression, copyrights) strings computed
    from the DebianPackage `package` installed in the `root_dir` root directory.
    The package is also updated in place with declared license and license_expression

    For each copyright file paragraph we treat the "name" as a license declaration.
    The text is used for detection and cross-reference with the declaration.
    """
    assert isinstance(package, DebianPackage)
    location = package.get_copyright_file_path(root_dir)

    results = parse_copyright_file(location)
    declared_license, detected_license, copyrights = results

    package.license_expression = detected_license
    package.declared_license = declared_license
    package.copyright = copyrights

    return declared_license, detected_license, copyrights


def parse_copyright_file(location, with_debian_packaging=False):
    """
    Return a tuple of (declared license, detected license_expression, copyrights) strings computed
    from the debain copyright file at `location`. For each copyright file paragraph we
    treat the "name" as a license declaration. The text is used for detection
    and cross-reference with the declaration.
    """
    if not location:
        return None, None, None
    
    if not location.endswith('copyright'):
        return None, None, None

    dc = DebianStructuredCopyrightFileProcessor.from_file(
        location=location, with_debian_packaging=with_debian_packaging,
    )

    declared_license = None
    copyrights = dc.detected_copyrights_text

    if dc.is_structured:
        declared_license = dc.declared_licenses
        detected_license = dc.license_expressions_from_structured
        
    else:
        detected_license = combine_expressions(dc.license_expressions)

    if TRACE:
        logger_debug(
            f'parse_copyright_file: declared_license: {declared_license}\n'
            f'detected_license: {detected_license}\n'
            f'copyrights: {copyrights}'
        )
        
    # Create filters further for results
    #elif is_debian_packaging(paragraph) and not with_debian_packaging:
    # Skipping packaging license for files in debian/*
    # since they are not relevant to the effective package license

    return declared_license, detected_license, copyrights


@attr.s
class DebianStructuredCopyrightFileProcessor:

    location = attr.ib()

    # DebianCopyrightParagraphs object with different kinds of debian copyright paragraphs
    debian_paras = attr.ib()
    
    is_structured = attr.ib(default=True)

    # List of strings of License: tag values in a structured debian copyright file
    declared_licenses = attr.ib(default=attr.Factory(list))

    # ToDo: Consider returning Line Positions
    # List of strings of Copyright: tag values in a structured debian copyright file
    # or the detected copyrights in an unstructured file
    detected_copyrights = attr.ib(default=attr.Factory(list))
    
    # List of LicenseDetection objects having license matches from files/header paragraphs
    license_detections = attr.ib(default=attr.Factory(list))

    # List of LicenseMatches in unstructured Files
    license_matches = attr.ib(default=attr.Factory(list))

    @property
    def detected_copyrights_text(self):
        return '\n'.join(self.detected_copyrights)

    @classmethod
    def from_file(cls, location, with_copyright=True, with_debian_packaging=False):
        """
        Return a DebianCopyrightDetector object built from debian copyright file at ``location``,
        or None if this is not a debian copyright file.
        Optionally detect copyright statements, if ``with_copyright`` is True.
        """
        if not location:
            return
        
        if not location.endswith('copyright'):
            return

        debian_paras = DebianCopyrightParagraphs.from_file(location=location)
        dc = cls(location=location, debian_paras=debian_paras)

        content = unicode_text(location)
        dc.is_structured = is_machine_readable_copyright(content)

        if with_copyright:
            dc.detected_copyrights = dc.detect_copyrights(
                with_debian_packaging=with_debian_packaging,
            )

        if not dc.is_structured:
            dc.license_matches = get_license_matches(query_string=content)
        else:
            dc.license_detections = dc.get_structured_licenses(debian_paras=debian_paras)
            dc.declared_licenses = dc.get_declared_licenses
        
        return dc
    
    @property
    def get_declared_licenses(self):
        """
        Return a list of Declared License from the license detections.
        """
        declared_licenses = [
            license_detection.paragraph.license.name
            for license_detection in self.license_detections
            if license_detection.is_paragraph_reportable(is_declared_licenses=True)
        ]
        
        return declared_licenses
 
    def detect_copyrights(self, with_debian_packaging=False):
        """
        Return copyrights collected from a structured file or an unstructured file.
        """
        copyrights = []
        if self.is_structured:
            deco = DebianCopyright.from_file(self.location)
            for paragraph in deco.paragraphs:
                if is_debian_packaging(paragraph) and not with_debian_packaging:
                    continue
                if isinstance(paragraph, (CopyrightHeaderParagraph, CopyrightFilesParagraph)):
                    pcs = paragraph.copyright.statements or []
                    for p in pcs:
                        p = p.dumps()
                        copyrights.append(p)
        # We detect plain copyrights in a unstructured file if we didn't find any, or
        # in an structured file
        if not copyrights:
            copyrights = copyright_detector(self.location)
            
        return copyrights
    
    @property
    def license_expressions(self):
        """
        Return a list of license expressions.
        """
        matches = self.license_matches
        if not matches:
            # we have no match: return an unknown key
            return ['unknown']

        detected_expressions = [match.rule.license_expression for match in matches]
        return detected_expressions
    
    @property
    def license_expressions_from_structured(self, licensing = Licensing()):
        """
        Return a list of license expressions.
        """
        license_detections = [
            license_detection
            for license_detection in self.license_detections
            if license_detection.is_paragraph_reportable(is_declared_licenses=False)
        ]

        if not self.license_detections:
            # we have no match: return an unknown key
            return ['unknown']

        if len(license_detections) == 1:
            detected_expressions = license_detections[0].license_expression_object
        else:
            detected_expressions = licensing.AND(
                *[
                    license_detection.license_expression_object
                    for license_detection in license_detections
                ]
            )
        
        return str(detected_expressions)

    def get_structured_licenses(self, debian_paras):
        """
        Return lists of LicenseDetections and LicenseTracing objects after parsing and running
        license detection on Structured Debian Copyright File at location.
        # TODO: We should also track line numbers in the file where a license was found 
        """
        if not debian_paras:
            return [], []

        license_detections = []

        debian_licensing = DebianLicensing.from_license_paragraphs(debian_paras=debian_paras)

        license_detections.extend(debian_licensing.license_detections)
        
        if debian_paras.header_para.license.name:
            license_detections_para = self.parse_header_and_files_paras_for_license(
                paragraph=debian_paras.header_para,
                debian_licensing=debian_licensing,
            )
            license_detections.append(license_detections_para)
        
        for file_paragraph in debian_paras.file_paras:
            license_detections_para = self.parse_header_and_files_paras_for_license(
                paragraph=file_paragraph,
                debian_licensing=debian_licensing,
            )
            license_detections.append(license_detections_para)
            
        license_detections.extend(
            self.detect_license_in_other_paras(other_paras=debian_paras.other_paras)
        )

        return license_detections

    @staticmethod
    def parse_header_and_files_paras_for_license(paragraph, debian_licensing):
        """
        Return LicenseDetections and LicenseTracing objects after parsing and running
        license detection on Header/Files paras in Structured Debian Copyright File.
        """
        normalized_expression = None

        name = paragraph.license.name
        name = name and name.lower()
        cleaned = clean_expression(name)

        if not name:
            return get_license_detection_from_nameless_paragraph(paragraph=paragraph)

        try:
            debian_expression = debian_licensing.licensing.parse(cleaned)
            normalized_expression = debian_expression.subs(debian_licensing.substitutions)

        except ExpressionError:
            # If Expression fails to parse we lookup exact string matches in License paras
            # which also failed to parse
            if cleaned in debian_licensing.unparsable_expressions:
                matches_unparsable_expression = debian_licensing.license_matches_by_symbol.get(cleaned)
                normalized_expression = get_license_expression_from_matches(
                    license_matches=matches_unparsable_expression,
                )
                
            else:
                # Case where expression is not parsable and the same expression is not present in
                # the license paragraphs
                unknown_matches = get_unknown_matches(name=name, text=None)
                normalized_expression = get_license_expression_from_matches(
                    license_matches=unknown_matches
                )   

        return LicenseDetection(
            paragraph=paragraph,
            license_expression_object=normalized_expression,
            license_matches=None,
        )
        
    @staticmethod
    def detect_license_in_other_paras(other_paras):
        
        license_detections = []
        
        for other_para in other_paras:
            
            extra_data = other_para.to_dict()
            
            for _field_name, field_value in extra_data.items():
            
                license_matches = get_license_matches(query_string=field_value)
                normalized_expression = get_license_expression_from_matches(
                        license_matches=license_matches,
                )
                license_detections.append(LicenseDetection(
                    paragraph=other_para,
                    license_expression_object=normalized_expression,
                    license_matches=license_matches,
                ))
        
        return license_detections


class NoLicenseFoundError(Exception):
    """
    Raised when some license is expected to be found, but is not found.
    """


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
    Debian Copyright File and the corresponding LicenseMatch objects. This object is
    suitable to be used a license_expression.LicenseSymbolLike object.
    """
    key = attr.ib()
    is_exception = attr.ib(default=False)
    matches = attr.ib(default=attr.Factory(list))
    
    def get_matched_expression(self, licensing=Licensing()):
        """
        Return a single license_expression.LicenseExpression object crafted
        from combining the LicenseMatches
        """
        assert self.matches, f"Cannot build expression from empty matches: {self}"
        if len(self.matches) > 1:
            expression = licensing.AND(*[
                match.rule.license_expression_object for match in self.matches
            ])
        else:
            expression = self.matches[0].rule.license_expression_object

        return expression   


@attr.s
class LicenseDetection:
    """
    License Detections in a debian copyright file can be license matches from a text,
    or a 
    """
    paragraph = attr.ib()
    license_expression_object = attr.ib()
    license_matches = attr.ib()
    is_expresion_parsable = attr.ib(default=True)
    
    def is_paragraph_reportable(self, is_declared_licenses):
        
        if isinstance(self.paragraph, CopyrightLicenseParagraph):
            return False
        elif isinstance(self.paragraph, CatchAllParagraph):
            if is_declared_licenses:
                return False
            else:
                return True
        elif self.paragraph.license.text:
            if self.license_expression_object is None:
                return False

        return True


@attr.s
class DebianLicensing:
    """
    Within a copyright file we have a set of custom license symbols; in general
    we also have common debian licenses. These two combines form the set of symbols
    we can use to parse the license declaration in each of the paragraphs. This
    object exposes license expression parsing that is aware of the specific context
    of this copyright file.
    """
    licensing = attr.ib()
    license_matches_by_symbol = attr.ib()
    substitutions = attr.ib()
    unparsable_expressions = attr.ib()
    license_detections = attr.ib()

    @classmethod
    def from_license_paragraphs(cls, debian_paras):
        # rename to plural in case  list
        result = DebianLicensing.parse_paras_with_license_text(debian_paras=debian_paras)
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
    
    @staticmethod
    def parse_paras_with_license_text(debian_paras):
        """
        Return a dictionary `license_matches_by_symbol` with declared licenses as keys and a list
        of license matches for the License Paragraph `license_paras`. Also returns a list of
        `LicenseTracing` objects.
        """
        paras_with_license = []
        paras_with_license.extend(debian_paras.license_paras)
        paras_with_license.extend(debian_paras.other_paras_with_license_text)
    
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
                common_license_matches = get_license_matches(query_string=common_license_tag)
                if len(common_license_matches) != 1:
                    raise Exception("Rules for common License is missing: {common_license_tag}")
                
                common_license_match = common_license_matches[0]
                matches.append(common_license_match)
                
                # Raise Exception when all the license expressions of the matches are not
                # consistent with the common_license_match
                if not have_consistent_licenses_with_match(
                    matches=text_matches, reference_match=common_license_match
                ):
                    #raise Exception(f"Inconsistent Licenses: {common_license_match} {matches}")
                    pass
                
                matches.extend(text_matches)
            else:
                if text_matches:
                    matches.extend(text_matches)
                else:
                    matches.extend(get_unknown_matches(name=name, text=text))
                
            if license_paragraph.comment:
                comment = license_paragraph.comment.text
                comment_matches = get_license_matches(query_string=comment)   
                
                # If license detected in the comments are not consistent with the license
                # detected in text, add the license matches detected in the comment to be reported
                if comment_matches:
                    if not have_consistent_licenses(
                        matches=text_matches,
                        reference_matches=comment_matches
                    ):
                        matches.extend(comment_matches)

            license_matches_by_symbol[cleaned] = matches

            license_detections.append(LicenseDetection(
                paragraph=license_paragraph,
                license_expression_object=None,
                license_matches=matches,
            ))
            
        return license_matches_by_symbol, license_detections
    
    @staticmethod
    def build_symbols(license_matches_by_symbol, common_licenses=common_licenses):
        """
        Return a list of LicenseSymbolLike objects, built from known and common licenses.
        It is expected that license_matches_by_symbol keys are in lowercase.
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


@attr.s
class DebianCopyrightParagraphs:
    deco = attr.ib()
    header_para = attr.ib(default=None)
    file_paras = attr.ib(default=attr.Factory(list))

    # File and Header paras with a license text
    other_paras_with_license_text = attr.ib(default=attr.Factory(list))
    license_paras = attr.ib(default=attr.Factory(list))

    # Paragraph which isn't Header/File/License paragraph
    other_paras = attr.ib(default=attr.Factory(list))

    # License Paragraph duplicates
    duplicate_license_paras = attr.ib(default=attr.Factory(list))
    seen_license_names = attr.ib(default=attr.Factory(set))

    @classmethod
    def from_file(cls, location):
        """
        From a structured debian copyright file at location, parse and extract paragraphs.
        """
        deco = DebianCopyright.from_file(location)
        
        dc = cls(deco=deco)
        
        for paragraph in deco.paragraphs:
            if isinstance(paragraph, CopyrightHeaderParagraph):
                if paragraph.license.text:
                    dc.other_paras_with_license_text.append(paragraph)
                dc.header_para = paragraph
            elif isinstance(paragraph, CopyrightFilesParagraph):
                if paragraph.license.text:
                    dc.other_paras_with_license_text.append(paragraph)
                dc.file_paras.append(paragraph)
            elif isinstance(paragraph, CopyrightLicenseParagraph):
                lic_name = paragraph.license.name
                if lic_name:
                    if lic_name not in dc.seen_license_names:
                        dc.license_paras.append(paragraph)
                        dc.seen_license_names.add(lic_name)
                    else:
                        # FIXME: There are two instances of the same key, needs to be fixed
                        dc.duplicate_license_paras.append(paragraph)   
                else:
                    dc.other_paras.append(paragraph)
            elif isinstance(paragraph, CatchAllParagraph):
                dc.other_paras.append(paragraph)
            else:
                raise Exception(
                    f'Unknown paragraph type in copyright file, location:{location}',
                    paragraph
                )
        
        if dc.duplicate_license_paras:
            # Run normal license detection on this
            #raise Exception(
            #    f'Duplicate License paragraphs type in copyright file, location:{location}',
            #    *dc.duplicate_license_paras
            #)
            pass
        
        return dc


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


def get_license_matches(location=None, query_string=None):
    """
    Return a sequence of LicenseMatch objects.
    """
    if not query_string:
        return []
    from licensedcode import cache

    idx = cache.get_index()
    return idx.match(location=location, query_string=query_string)


def clean_debian_comma_logic(exp):
    """
    Convert Debian specific logic regarding comma to parsable license expression.
    Example:   `lgpl-3 or gpl-2, and apache-2.0` -> `(lgpl-3 or gpl-2) and apache-2.0`
    """
    subexps = []
    while ", and" in exp:
        exp, and_op, right = exp.rpartition(", and")
        subexps.insert(0, right)
    subexps.insert(0, exp)
    wrapped = [f"({i.strip()})" for i in subexps]
    cleaned= " and ".join(wrapped)
    return cleaned


def clean_expression(text):
    """
    Return a cleaned license expression text by normalizing the syntax so it can be parsed.
    This substitution table has been derived from a large collection of most copyright files
    from Debian (about 320K files from circa 2019-11) and Ubuntu (about 200K files from circa
    2020-06)
    """
    if not text:
        return text

    text = text.lower()
    text = ' '.join(text.split())
    if "," in text:
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
        "gcc runtime library exception":"gcc_runtime_library_exception",
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


def get_license_expression_from_matches(license_matches, licensing = Licensing()):
    
    license_expression = [
        licensing.parse(match.rule.license_expression)
        for match in license_matches
    ]
    
    if len(license_expression) == 1:
        return license_expression[0]
    else:
        return licensing.AND(*license_expression)


def get_unknown_matches(name, text):
    """
    Return a LicenseMatch object for an unknown license match.
    """
    license_text = f"License: {name} {text}"
    return get_license_matches(query_string=license_text)


def get_license_detection_from_nameless_paragraph(paragraph):
    """
    Return LicenseDetections and LicenseTracing objects after parsing and running
    license detection on Header/Files paras in paragrpahs without name.
    """
    matches = []
    
    if not matches:
        unknown_matches = get_unknown_matches(name=None, text=paragraph.license.text)
        normalized_expression = get_license_expression_from_matches(
            license_matches=unknown_matches
        )
    else:
        normalized_expression = get_license_expression_from_matches(
            license_matches=matches
        )

    license_detection_para = LicenseDetection(
        paragraph=paragraph,
        license_expression_object=normalized_expression,
        license_matches=matches,
    )

    return license_detection_para


def have_consistent_licenses(matches, reference_matches):
    """
    Return true if all the license of the matches list of LicenseMatch have the
    same license as all the licenses of the reference_matches list of LicenseMatch.
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


def parse_structured_copyright_file(
    location,
    with_debian_packaging=False,
):
    """
    Return a tuple of (list of declared license strings, list of detected license matches)
    collected from the debian copyright file at `location`.

    If `with_debian_packaging` is False, the Debian packaging license is skipped if detected.
    
    #TODO: We want to find in a file where in a copyright file a license was found.
    """
    if not location:
        return None, None

    deco = DebianCopyright.from_file(location)

    declared_licenses = []
    detected_licenses = []

    #TODO: Revisit: is this really needed
    deco = refine_debian_copyright(deco)

    licensing = Licensing()
    for paragraph in deco.paragraphs:

        if is_debian_packaging(paragraph) and not with_debian_packaging:
            # Skipping packaging license and copyrights since they are not
            # relevant to the effective package license
            continue

        # rare case where we have not a structured file
        if isinstance(paragraph, CatchAllParagraph):
            text = paragraph.dumps()
            if text:
                detected = get_normalized_expression(
                    text,
                    try_as_expression=False,
                    approximate=False,
                )
                if not detected:
                    detected = 'unknown'
                detected_licenses.append(detected)
        else:
            plicense = paragraph.license
            if not plicense:
                continue

            declared, detected = detect_declared_license(plicense.name)
            if declared:
                declared_licenses.append(declared)
            if detected:
                detected_licenses.append(detected)

            # also detect in text
            text = paragraph.license.text
            if text:
                detected = get_normalized_expression(
                    text,
                    try_as_expression=False,
                    approximate=True,
                )
                if not detected:
                    detected = 'unknown'

                detected_licenses.append(detected)

    declared_license = '\n'.join(declared_licenses)

    if detected_licenses:
        detected_licenses = [licensing.parse(dl, simple=True) for dl in detected_licenses]

        if len(detected_licenses) > 1:
            detected_license = licensing.AND(*detected_licenses)
        else:
            detected_license = detected_licenses[0]

        detected_license = str(detected_license)

    else:
        detected_license = 'unknown'

    return declared_license, detected_license


def detect_declared_license(declared):
    """
    Return a tuple of (declared license, detected license expression) from a
    declared license. Both can be None.
    """
    declared = normalize_and_cleanup_declared_license(declared)

    if TRACE:
        logger_debug(f'detect_declared_license: {declared}')

    if not declared:
        return None, None

    # apply multiple license detection in sequence
    detected = detect_using_name_mapping(declared)
    if detected:
        return declared, detected

    from packagedcode import licensing
    try:
        detected = licensing.get_normalized_expression(
            declared,
            try_as_expression=False,
            approximate=False,
        )
    except Exception:
        # FIXME: add logging
        # we never fail just for this
        return 'unknown'

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
    Return a license expression detected from a declared_license.
    """
    declared = declared.lower()
    detected = get_declared_to_detected().get(declared)
    if detected:
        licensing = Licensing()
        return str(licensing.parse(detected, simple=True))


def is_debian_packaging(paragraph):
    """
    Return True if the `paragraph` is a CopyrightFilesParagraph that applies
    only to the Debian packaging
    """
    return (
        isinstance(paragraph, CopyrightFilesParagraph)
        and paragraph.files == ['debian/*']
    )


def is_primary_license_paragraph(paragraph):
    """
    Return True if the `paragraph` is a CopyrightFilesParagraph that contains
    the primary license.
    """
    return (
        isinstance(paragraph, CopyrightFilesParagraph)
        and paragraph.files == ['*']
    )


def refine_debian_copyright(debian_copyright):
    """
    Update in place the `debian_copyright` DebianCopyright object based on
    issues found in a large collection of Debian copyright files.
    """
    for paragraph in debian_copyright.paragraphs:
        if not hasattr(paragraph, 'license'):
            continue
        plicense = paragraph.license
        if not plicense:
            continue

        license_name = plicense.name
        if not license_name:
            continue

        if license_name.startswith('200'):
            # these are copyrights and not actual licenses, such as:
            # - 2005 Sergio Costas
            # - 2006-2010 by The HDF Group.

            if isinstance(paragraph, (CopyrightHeaderParagraph, CopyrightFilesParagraph)):
                pcs = paragraph.copyright.statements or []
                pcs.append(license_name)
                paragraph.copyright.statements = pcs
                paragraph.license.name = None

        license_name_low = license_name.lower()
        NOT_A_LICENSE_NAME = (
            'according to',
            'by obtaining',
            'distributed under the terms of the gnu',
            'gnu general public license version 2 as published by the free',
            'gnu lesser general public license 2.1 as published by the',
        )
        if license_name_low.startswith(NOT_A_LICENSE_NAME):
            text = plicense.text
            if text:
                text = '\n'.join([license_name, text])
            else:
                text = license_name
            paragraph.license.name = None
            paragraph.license.text = text

    return debian_copyright


_DECLARED_TO_DETECTED = None


def get_declared_to_detected(data_file=None):
    """
    Return a mapping of declared to detected license expression cached and
    loaded from a tab-separated text file, all lowercase.

    Each line has this form:
        some license name<tab>scancode license expression

    For instance:
        2-clause bsd    bsd-simplified

    This data file is about license keys used in copyright files and has been
    derived from a large collection of most copyright files from Debian (about
    320K files from circa 2019-11) and Ubuntu (about 200K files from circa
    2020-06)
    """
    global _DECLARED_TO_DETECTED
    if _DECLARED_TO_DETECTED:
        return _DECLARED_TO_DETECTED

    _DECLARED_TO_DETECTED = {}
    if not data_file:
        data_file = path.join(path.dirname(__file__), 'debian_licenses.txt')
    with io.open(data_file, encoding='utf-8') as df:
        for line in df:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            decl, _, detect = line.strip().partition('\t')
            if detect and detect.strip():
                decl = decl.strip()
                _DECLARED_TO_DETECTED[decl] = detect
    return _DECLARED_TO_DETECTED
