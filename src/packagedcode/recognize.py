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

from commoncode import filetype
from commoncode.fileutils import file_name
from commoncode.fileutils import splitext_name
from packagedcode import PACKAGE_MANIFEST_TYPES
from typecode import contenttype

SCANCODE_DEBUG_PACKAGE_API = os.environ.get('SCANCODE_DEBUG_PACKAGE_API', False)

TRACE = False or SCANCODE_DEBUG_PACKAGE_API


def logger_debug(*args):
    pass


if TRACE:
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))

    logger_debug = print

"""
Recognize package manifests in files.
"""


def recognize_package_manifests(location):
    """
    Return a list of Package objects if any package_manifests were recognized for this
    `location`, or None if there were no Packages found. Raises Exceptions on errors.
    """

    if not filetype.is_file(location):
        return

    recognized_package_manifests = []
    for package_manifest_type in PACKAGE_MANIFEST_TYPES:
        if not package_manifest_type.is_manifest(location):
            continue

        try:
            for recognized in package_manifest_type.recognize(location):
                if TRACE:
                    logger_debug(
                        'recognize_package_manifests: metafile matching: recognized:',
                        recognized,
                    )
                if recognized and not recognized.license_expression:
                    # compute and set a normalized license expression
                    try:
                        recognized.license_expression = recognized.compute_normalized_license()
                    except Exception:
                        if SCANCODE_DEBUG_PACKAGE_API:
                            raise
                        recognized.license_expression = 'unknown'

                    if TRACE:
                        logger_debug(
                            'recognize_package_manifests: recognized.license_expression:',
                            recognized.license_expression
                        )
                recognized_package_manifests.append(recognized)
            return recognized_package_manifests

        except NotImplementedError:
            # build a plain package if recognize is not yet implemented
            recognized = package_manifest_type()
            if TRACE:
                logger_debug(
                    'recognize_package_manifests: NotImplementedError: recognized', recognized
                )

            recognized_package_manifests.append(recognized)

            if SCANCODE_DEBUG_PACKAGE_API:
                raise

        return recognized_package_manifests

        if TRACE: logger_debug(
            'recognize_package_manifests: no match for type:', package_manifest_type
        )
