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

import multiregex

from commoncode import filetype
from commoncode.fileutils import as_posixpath

from packagedcode import HANDLER_BY_DATASOURCE_ID
from packagedcode import BINARY_HANDLERS_PRESENT
from packagedcode import BINARY_PACKAGE_DATAFILE_HANDLERS
from packagedcode import models
from packagedcode.cache import get_cache

TRACE = os.environ.get('SCANCODE_DEBUG_PACKAGE_API', False)


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
    package_only=False,
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

    return list(_parse(
        location=location,
        package_only=package_only,
        application=application,
        system=system,
    ))


def _parse(
    location,
    application=True,
    system=False,
    package_only=False,
):
    """
    Yield parsed PackageData objects from ``location``. Raises Exceptions on errors.

    Use the provided ``datafile_handlers`` list of DatafileHandler classes.
    Default to use application packages
    """

    package_path = as_posixpath(location)
    package_patterns = get_cache()

    assert application or system or package_only
    if package_only or (application and system):
        multiregex_patterns = package_patterns.all_multiregex_patterns
    elif application:
        multiregex_patterns = package_patterns.application_multiregex_patterns
    elif system:
        multiregex_patterns = package_patterns.system_multiregex_patterns

    package_matcher = multiregex.RegexMatcher(multiregex_patterns)
    matched_patterns = package_matcher.match(package_path)

    datafile_handlers = []
    for matched_pattern in matched_patterns:
        regex, _match = matched_pattern
        handler_ids = package_patterns.handler_by_regex.get(regex.pattern)
        if TRACE:
            logger_debug(f'_parse:.handler_ids: {handler_ids}')

        datafile_handlers = [
            HANDLER_BY_DATASOURCE_ID.get(handler_id)
            for handler_id in handler_ids
        ]

    if not datafile_handlers:
        if BINARY_HANDLERS_PRESENT:
            datafile_handlers = BINARY_PACKAGE_DATAFILE_HANDLERS
        else:
            if TRACE:
                logger_debug(f'_parse: no package datafile detected at {package_path}')

            return

    for handler in datafile_handlers:
        if TRACE:
            logger_debug(f'_parse:.is_datafile: {handler}')

        if not handler.is_datafile(location):
            continue

        if TRACE:
            logger_debug(f'_parse:.is_datafile: {location}')

        try:
            for parsed in handler.parse(location=location, package_only=package_only):
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

        except Exception as e:
            # We should continue when an Exception has occured when trying to
            # recognize a package
            if TRACE:
                import traceback
                logger_debug(f'_parse: Exception: {str(e)} : {traceback.format_exc()}')
                raise Exception(f'_parse: error') from e

            continue
