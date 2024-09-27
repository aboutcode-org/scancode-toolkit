#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import pytest

from packagedcode import ALL_DATAFILE_HANDLERS
from packagedcode import APPLICATION_PACKAGE_DATAFILE_HANDLERS
from packagedcode import SYSTEM_PACKAGE_DATAFILE_HANDLERS
from packagedcode.debian_copyright import DebianCopyrightFileInPackageHandler


@pytest.mark.parametrize('datafile_handler', ALL_DATAFILE_HANDLERS)
def test_validate_datafile_handlers(datafile_handler):
    datafile_handler.validate()


def test_check_datafile_handlers_have_no_duplicate_datasource_id():
    seen_datasource_id = set()

    for dfh in sorted(set(APPLICATION_PACKAGE_DATAFILE_HANDLERS + SYSTEM_PACKAGE_DATAFILE_HANDLERS), key=str):
        assert dfh.datasource_id not in seen_datasource_id
        seen_datasource_id.add(dfh.datasource_id)


def test_check_datafile_handlers_have_no_duplicated_entries():
    app_handlers = set(APPLICATION_PACKAGE_DATAFILE_HANDLERS)
    sys_handlers = set(SYSTEM_PACKAGE_DATAFILE_HANDLERS)

    dupes = app_handlers.intersection(sys_handlers)
    expected = set([DebianCopyrightFileInPackageHandler])
    assert dupes == expected
