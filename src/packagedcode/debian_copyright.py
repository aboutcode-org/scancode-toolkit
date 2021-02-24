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

from debut.copyright import DebianCopyright
from debut.copyright import CatchAllParagraph
from debut.copyright import CopyrightFilesParagraph
from debut.copyright import CopyrightHeaderParagraph
from license_expression import Licensing

from packagedcode.debian import DebianPackage
from packagedcode import models
from packagedcode.licensing import get_normalized_expression
import textcode

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
    copyright_file = package.get_copyright_file_path(root_dir)

    results = parse_copyright_file(copyright_file)
    declared_license, detected_license, copyrights = results

    package.license_expression = detected_license
    package.declared_license = declared_license
    package.copyright = copyrights

    return declared_license, detected_license, copyrights


def parse_copyright_file(
    copyright_file,
    skip_debian_packaging=True,
    simplify_licenses=True,
    unique=True
):
    """
    Return a tuple of (declared license, detected license_expression, copyrights) strings computed
    from the `copyright_file` location. For each copyright file paragraph we
    treat the "name" as a license declaration. The text is used for detection
    and cross-reference with the declaration.
    """
    if not copyright_file:
        return None, None, None

    # first parse as structured copyright file
    declared_license, detected_license, copyrights = parse_structured_copyright_file(
        copyright_file=copyright_file,
        skip_debian_packaging=skip_debian_packaging,
        simplify_licenses=simplify_licenses,
        unique=unique,
    )
    if TRACE:
        logger_debug(
            f'parse_copyright_file: declared_license: {declared_license}\n'
            f'detected_license: {detected_license}\n'
            f'copyrights: {copyrights}'
        )

    # dive into whole text only if we detected everything as unknown.
    # TODO: this is not right.
    if not detected_license or detected_license == 'unknown':
        text = textcode.analysis.unicode_text(copyright_file)
        detected_license = get_normalized_expression(text, try_as_expression=False)
        if TRACE:
            logger_debug(
                f'parse_copyright_file: using whole text: '
                f'detected_license: {detected_license}'
            )

    # dive into copyright if we did not detect any.
    if not copyrights:
        copyrights = '\n'.join(copyright_detector(copyright_file))
        if TRACE:
            logger_debug(
                f'parse_copyright_file: using whole text: '
                f'copyrights: {copyrights}'
            )

    return declared_license, detected_license, copyrights


def copyright_detector(location):
    """
    Return lists of detected copyrights, authors & holders in file at location.
    """
    if location:
        from cluecode.copyrights import detect_copyrights
        copyrights = []
        copyrights_append = copyrights.append

        for dtype, value, _start, _end in detect_copyrights(location):
            if dtype == 'copyrights':
                copyrights_append(value)
        return copyrights


def parse_structured_copyright_file(
    copyright_file,
    skip_debian_packaging=True,
    simplify_licenses=True,
    unique=True,
):
    """
    Return a tuple of (declared license, detected license_expression,
    copyrights) strings computed from the `copyright_file` location. For each
    copyright file paragraph we treat the "name" as a license declaration. The
    text is used for detection and cross-reference with the declaration.

    If `skip_debian_packaging` is True, the Debian packaging license is skipped
    if detected.

    If `simplify_licenses` is True the license expressions are simplified.

    If `unique` is True, repeated copyrights, detected or declared licenses are
    ignored, and only unique detections are returned.
    """
    if not copyright_file:
        return None, None, None

    deco = DebianCopyright.from_file(copyright_file)

    declared_licenses = []
    detected_licenses = []
    copyrights = []

    deco = fix_copyright(deco)

    licensing = Licensing()
    for paragraph in deco.paragraphs:

        if skip_debian_packaging and is_debian_packaging(paragraph):
            # Skipping packaging license and copyrights since they are not
            # relevant to the effective package license
            continue

        if isinstance(paragraph, (CopyrightHeaderParagraph, CopyrightFilesParagraph)):
            pcs = paragraph.copyright.statements or []
            for p in pcs:
                p = p.dumps()
                # avoid repeats
                if unique:
                    if p not in copyrights:
                        copyrights.append(p)
                else:
                    copyrights.append(p)

        if isinstance(paragraph, CatchAllParagraph):
            text = paragraph.dumps()
            if text:
                detected = get_normalized_expression(text, try_as_expression=False)
                if not detected:
                    detected = 'unknown'
                detected_licenses.append(detected)
        else:
            plicense = paragraph.license
            if not plicense:
                continue

            declared, detected = detect_declared_license(plicense.name)
            # avoid repeats
            if unique:
                if declared and declared not in declared_licenses:
                    declared_licenses.append(declared)
                if detected and detected not in detected_licenses:
                    detected_licenses.append(detected)
            else:
                declared_licenses.append(declared)
                detected_licenses.append(detected)

            # also detect in text
            text = paragraph.license.text
            if text:
                detected = get_normalized_expression(text, try_as_expression=False)
                if not detected:
                    detected = 'unknown'
                # avoid repeats
                if unique:
                    if detected not in detected_licenses:
                        detected_licenses.append(detected)
                else:
                    detected_licenses.append(detected)

    declared_license = '\n'.join(declared_licenses)

    if detected_licenses:
        detected_licenses = [licensing.parse(dl, simple=True) for dl in detected_licenses]

        if len(detected_licenses) > 1:
            detected_license = licensing.AND(*detected_licenses)
        else:
            detected_license = detected_licenses[0]

        if simplify_licenses:
            detected_license = detected_license.simplify()

        detected_license = str(detected_license)

    else:
        detected_license = 'unknown'

    copyrights = '\n'.join(copyrights)
    return declared_license, detected_license, copyrights


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

    detected = models.compute_normalized_license(declared)
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


def fix_copyright(debian_copyright):
    """
    Update in place the `debian_copyright` DebianCopyright object based on
    issues found in a large collection of Debian copyrights such as names that
    rea either copyright staments or license texts.
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

    This data file is about license keys used in copyright files and has been
    derived from a large collection of most copyright files from Debian (about
    320K files from circa 2019-11) and Ubuntu (about 200K files from circa
    202-06)
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
