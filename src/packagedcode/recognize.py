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
from packagedcode import PACKAGE_DATAFILE_HANDLERS
from packagedcode import models

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
Recognize and parse package datafiles, manifests, or lockfiles.
"""


def recognize_package_data(location):
    """
    Return a list of Package objects if any package_data were recognized for
    this `location`, or None if there were no Packages found. Raises Exceptions
    on errors.
    """

    if not filetype.is_file(location):
        return []

    return list(_parse(location))


def _parse(location):
    """
    Yield parsed PackageData objects from ``location``. Raises Exceptions on errors.
    """

    for handler in PACKAGE_DATAFILE_HANDLERS:
        if not handler.is_datafile(location):
            continue

        if TRACE:
            logger_debug(f'_parse:.is_datafile: {location}')

        try:
            for parsed in handler.parse(location):
                if TRACE:
                    logger_debug(f' _parse: parsed: {parsed!r}')
                yield parsed

        except NotImplementedError:
            # build a plain package if parse is not yet implemented
            pkg = models.PackageData(
                datasource_id=handler.datasource_id,
                type=handler.default_package_type,
                primary_language=handler.default_primary_language,
            )
            if TRACE:
                logger_debug('_parse: NotImplementedError: parsed', parsed)

            yield pkg

            if SCANCODE_DEBUG_PACKAGE_API:
                raise
