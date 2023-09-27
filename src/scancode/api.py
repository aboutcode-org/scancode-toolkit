#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
from itertools import islice
from os.path import getsize
import logging
import os
import sys

from commoncode.filetype import get_last_modified_date
from commoncode.hash import multi_checksums
from scancode import ScancodeError
from typecode.contenttype import get_type


TRACE = os.environ.get('SCANCODE_DEBUG_API', False)


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(
            ' '.join(isinstance(a, str) and a or repr(a) for a in args)
        )

"""
Main scanning functions.

Each scanner is a function that accepts a location and returns a sequence of
mappings as results.

Note: this API is unstable and still evolving.
"""


def get_copyrights(
    location,
    deadline=sys.maxsize,
    **kwargs,
):
    """
    Return a mapping with a single 'copyrights' key with a value that is a list
    of mappings for copyright detected in the file at `location`.
    """
    from cluecode.copyrights import detect_copyrights
    from cluecode.copyrights import Detection

    detections = detect_copyrights(
        location,
        include_copyrights=True,
        include_holders=True,
        include_authors=True,
        include_copyright_years=True,
        include_copyright_allrights=False,
        deadline=deadline,
    )

    copyrights, holders, authors = Detection.split(detections, to_dict=True)

    results = dict([
        ('copyrights', copyrights),
        ('holders', holders),
        ('authors', authors),
    ])

    # TODO: do something if we missed the deadline
    return results


def get_emails(
    location,
    threshold=50,
    test_slow_mode=False,
    test_error_mode=False,
    **kwargs,
):
    """
    Return a mapping with a single 'emails' key with a value that is a list of
    mappings for emails detected in the file at `location`.
    Return only up to `threshold` values. Return all values if `threshold` is 0.

    If test_mode is True, the scan will be slow for testing purpose and pause
    for one second.
    """
    if test_error_mode:
        raise ScancodeError('Triggered email failure')

    if test_slow_mode:
        import time
        time.sleep(1)

    from cluecode.finder import find_emails
    results = []

    found_emails = ((em, ln) for (em, ln) in find_emails(location) if em)
    if threshold:
        found_emails = islice(found_emails, threshold)

    for email, line_num in found_emails:
        result = {}
        results.append(result)
        result['email'] = email
        result['start_line'] = line_num
        result['end_line'] = line_num
    return dict(emails=results)


def get_urls(location, threshold=50, **kwargs):
    """
    Return a mapping with a single 'urls' key with a value that is a list of
    mappings for urls detected in the file at `location`.
    Return only up to `threshold` values. Return all values if `threshold` is 0.
    """
    from cluecode.finder import find_urls
    results = []

    found_urls = ((u, ln) for (u, ln) in find_urls(location) if u)
    if threshold:
        found_urls = islice(found_urls, threshold)

    for urls, line_num in found_urls:
        result = {}
        results.append(result)
        result['url'] = urls
        result['start_line'] = line_num
        result['end_line'] = line_num
    return dict(urls=results)


SPDX_LICENSE_URL = 'https://spdx.org/licenses/{}'
DEJACODE_LICENSE_URL = 'https://enterprise.dejacode.com/urn/urn:dje:license:{}'
SCANCODE_LICENSEDB_URL = 'https://scancode-licensedb.aboutcode.org/{}'
SCANCODE_DATA_BASE_URL = 'https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data'
SCANCODE_LICENSE_URL = f'{SCANCODE_DATA_BASE_URL}/licenses/{{}}.LICENSE'
SCANCODE_RULE_URL = f'{SCANCODE_DATA_BASE_URL}/rules/{{}}'

def get_licenses(
    location,
    min_score=0,
    include_text=False,
    license_text_diagnostics=False,
    license_diagnostics=False,
    deadline=sys.maxsize,
    unknown_licenses=False,
    **kwargs,
):
    """
    Return a mapping or license_detections for licenses detected in the file at
    `location`

    This mapping contains two keys:
     - 'license_detections' with a value that is list of mappings of license information.
     - 'detected_license_expression' with a value that is a license expression string.

    `min_score` is a minimum score threshold from 0 to 100. The default is 0,
    meaning that all license matches are returned. If specified, matches with a
    score lower than `minimum_score` are not returned.

    If `include_text` is True, matched text is included in the returned
    `licenses` data as well as a file-level `percentage_of_license_text` 
    as the percentage of file words detected as license text or notice.
    This is used to determine if a file contains mostly licensing.

    If ``unknown_licenses`` is True, also detect unknown licenses.
    """
    from licensedcode.cache import build_spdx_license_expression
    from licensedcode.cache import get_cache
    from licensedcode.detection import detect_licenses
    from packagedcode.utils import combine_expressions

    license_clues = []
    license_detections = []
    detected_expressions = []
    detected_license_expression = None
    detected_license_expression_spdx = None

    detections = detect_licenses(
        location=location,
        min_score=min_score,
        deadline=deadline,
        unknown_licenses=unknown_licenses,
        **kwargs,
    )

    all_qspans = []
    detection = None
    for detection in detections:
        all_qspans.extend(detection.qspans)

        if detection.license_expression is None:
            detection_mapping = detection.to_dict(
                include_text=include_text,
                license_text_diagnostics=license_text_diagnostics,
                license_diagnostics=license_diagnostics,
            )
            license_clues.extend(detection_mapping["matches"])
        else:
            detected_expressions.append(detection.license_expression)
            license_detections.append(
                detection.to_dict(
                    include_text=include_text,
                    license_text_diagnostics=license_text_diagnostics,
                    license_diagnostics=license_diagnostics,
                )
            )

    if TRACE:
        logger_debug(f"api: get_licenses: license_detections: {license_detections}")
        logger_debug(f"api: get_licenses: license_clues: {license_clues}")

    if detected_expressions:
        detected_license_expression = combine_expressions(
            expressions=detected_expressions,
            relation='AND',
            unique=True,
        )
        detected_license_expression_spdx = str(build_spdx_license_expression(
            detected_license_expression,
            licensing=get_cache().licensing
        ))

    percentage_of_license_text = 0
    if detection:
        percentage_of_license_text = detection.percentage_license_text_of_file(all_qspans)

    return dict([
        ('detected_license_expression', detected_license_expression),
        ('detected_license_expression_spdx', detected_license_expression_spdx),
        ('license_detections', license_detections),
        ('license_clues', license_clues),
        ('percentage_of_license_text', percentage_of_license_text),
    ])


SCANCODE_DEBUG_PACKAGE_API = os.environ.get('SCANCODE_DEBUG_PACKAGE_API', False)


def _get_package_data(
        location,
        application=True,
        system=False,
        purl_only=False,
        **kwargs
    ):
    """
    Return a mapping of package manifest information detected in the file at ``location``.
    Include ``application`` packages (such as pypi) and/or ``system`` packages.
    Note that all exceptions are caught if there are any errors while parsing a
    package manifest.
    """
    assert application or system
    from packagedcode.recognize import recognize_package_data
    try:
        return recognize_package_data(
            location=location,
            application=application,
            system=system,
            purl_only=purl_only,
        ) or []

    except Exception as e:
        if TRACE:
            logger.error(f'_get_package_data: location: {location!r}: Exception: {e}')

        if SCANCODE_DEBUG_PACKAGE_API:
            raise
        else:
            # attention: we are swallowing ALL exceptions here!
            pass


def get_package_info(location, **kwargs):
    """
    Return a mapping of package information detected in the file at `location`.
    This API function is DEPRECATED, use `get_package_data` instead.
    """
    import warnings
    warnings.warn(
        "`get_package_info` is deprecated. Use `get_package_data` instead.",
        DeprecationWarning,
        stacklevel=1
    )

    packages = _get_package_data(location, **kwargs) or []
    return dict(packages=[p.to_dict() for p in packages])


def get_package_data(
        location,
        application=True,
        system=False,
        purl_only=False,
        **kwargs
    ):
    """
    Return a mapping of package manifest information detected in the file at
    `location`.
    Include ``application`` packages (such as pypi) and/or ``system`` packages.
    """
    if TRACE:
        print('  scancode.api.get_package_data: kwargs', kwargs)

    package_datas = _get_package_data(
        location=location,
        application=application,
        system=system,
        purl_only=purl_only,
        **kwargs,
    ) or []

    return dict(package_data=[pd.to_dict() for pd in package_datas])


def get_file_info(location, **kwargs):
    """
    Return a mapping of file information collected for the file at `location`.
    """
    result = {}

    # TODO: move date and size these to the inventory collection step???
    result['date'] = get_last_modified_date(location) or None
    result['size'] = getsize(location) or 0

    sha1, md5, sha256 = multi_checksums(location, ('sha1', 'md5', 'sha256')).values()
    result['sha1'] = sha1
    result['md5'] = md5
    result['sha256'] = sha256

    collector = get_type(location)
    result['mime_type'] = collector.mimetype_file or None
    result['file_type'] = collector.filetype_file or None
    result['programming_language'] = collector.programming_language or None
    result['is_binary'] = bool(collector.is_binary)
    result['is_text'] = bool(collector.is_text)
    result['is_archive'] = bool(collector.is_archive)
    result['is_media'] = bool(collector.is_media)
    result['is_source'] = bool(collector.is_source)
    result['is_script'] = bool(collector.is_script)
    return result
