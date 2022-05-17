#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

import pytest

from commoncode.system import on_linux

from packagedcode import models
from packagedcode.models import Party
from packagedcode.msi import create_package_data_from_msiinfo_results
from packagedcode.msi import parse_msiinfo_suminfo_output
from packagedcode.msi import MsiInstallerHandler
from packages_test_utils import PackageTester


@pytest.mark.skipif(not on_linux, reason='msiinfo only runs on Linux')
class TestMsi(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    python_3_9_5_add_to_path_results = {
        'Title': 'Installation Database',
        'Subject': 'Python 3.9.5 Add to Path (64-bit)',
        'Author': 'Python Software Foundation',
        'Keywords': 'Installer',
        'Comments': 'This installer database contains the logic and data required to install Python 3.9.5 Add to Path (64-bit).',
        'Template': 'x64;1033',
        'Revision number (UUID)': '{33F421A1-6B08-4919-A6AB-62A429A0E739}',
        'Created': 'Mon May  3 10:41:02 2021',
        'Last saved': 'Mon May  3 10:41:02 2021',
        'Version': '300 (12c)',
        'Source': '10 (a)',
        'Application': 'Windows Installer XML Toolset (3.11.1.2318)',
        'Security': '2 (2)'
    }

    def test_msi_parse_msiinfo_suminfo_output(self):
        test_file = self.get_test_loc('msi/python-add-to-path-msiinfo-results.txt')
        with open(test_file) as f:
            msiinfo_results = f.read()
        result = parse_msiinfo_suminfo_output(msiinfo_results)

        assert result == self.python_3_9_5_add_to_path_results

    def test_msi_create_package_data_from_msiinfo_results(self):
        result = create_package_data_from_msiinfo_results(
            self.python_3_9_5_add_to_path_results.copy()
        ).to_dict()
        expected = models.PackageData(
            type=MsiInstallerHandler.default_package_type,
            datasource_id=MsiInstallerHandler.datasource_id,
            name='Python 3.9.5 Add to Path (64-bit)',
            version='v 3.9.5',
            description='This installer database contains the logic and data required to install Python 3.9.5 Add to Path (64-bit).',
            parties=[
                Party(
                    type=None,
                    role='author',
                    name='Python Software Foundation'
                )
            ],
            keywords='Installer',
        ).to_dict()
        result['extra_data'] = {}
        assert result == expected
