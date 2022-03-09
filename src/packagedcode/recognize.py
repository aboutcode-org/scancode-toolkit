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

from commoncode import filetype
from packagedcode import PACKAGE_DATA_CLASSES

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
Recognize package data in files.
"""


def recognize_package_data(location):
    """
    Return a list of Package objects if any package_data were recognized for this
    `location`, or None if there were no Packages found. Raises Exceptions on errors.
    """

    if not filetype.is_file(location):
        return

    recognized_package_data = []
    for package_data_type in PACKAGE_DATA_CLASSES:
        if not package_data_type.is_package_data_file(location):
            continue

        try:
            for recognized in package_data_type.recognize(location):
                if TRACE:
                    logger_debug(
                        'recognize_package_data: metafile matching: recognized:',
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
                            'recognize_package_data: recognized.license_expression:',
                            recognized.license_expression
                        )
                recognized_package_data.append(recognized)
            return recognized_package_data

        except NotImplementedError:
            # build a plain package if recognize is not yet implemented
            recognized = package_data_type()
            if TRACE:
                logger_debug(
                    'recognize_package_data: NotImplementedError: recognized', recognized
                )

            recognized_package_data.append(recognized)

            if SCANCODE_DEBUG_PACKAGE_API:
                raise

        if TRACE: 
            logger_debug(
                'recognize_package_data: no match for type:', package_data_type
            )

        return recognized_package_data
