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
from packagedcode import APPLICATION_PACKAGE_DATAFILE_HANDLERS
from packagedcode import SYSTEM_PACKAGE_DATAFILE_HANDLERS
from packagedcode import ALL_DATAFILE_HANDLERS
from packagedcode import models

TRACE = False or os.environ.get('SCANCODE_DEBUG_PACKAGE_API', False)


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


def recognize_package_data(
    location,
    application=True,
    system=False,
):
    """
    Return a list of Package objects if any package_data were recognized for
    this `location`, or None if there were no Packages found. Raises Exceptions
    on errors.
    Include ``application`` packages (such as pypi) and/or ``system`` packages.
    Default to use application packages
    """
    if not filetype.is_file(location):
        return []

    assert application or system
    if application and system:
        datafile_handlers = ALL_DATAFILE_HANDLERS
    elif application:
        datafile_handlers = APPLICATION_PACKAGE_DATAFILE_HANDLERS
    elif system:
        datafile_handlers = SYSTEM_PACKAGE_DATAFILE_HANDLERS

    return list(_parse(location, datafile_handlers=datafile_handlers))


def _parse(
    location,
    datafile_handlers=APPLICATION_PACKAGE_DATAFILE_HANDLERS,
):
    """
    Yield parsed PackageData objects from ``location``. Raises Exceptions on errors.

    Use the provided ``datafile_handlers`` list of DatafileHandler classes.
    Default to use application packages
    """

    for handler in datafile_handlers:
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
                logger_debug('_parse: NotImplementedError: handler', handler)

            yield pkg

            if TRACE:
                raise
