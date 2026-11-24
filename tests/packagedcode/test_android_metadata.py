#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from packages_test_utils import PackageTester
from packages_test_utils import compare_package_results

from packagedcode import android_metadata
from packagedcode import models

handler = android_metadata.AndroidMetadataHandler


class TestAndroidMetadata(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), "data/build")

    def test_android_metadata_parse(self):
        test_file = self.get_test_loc("android_metadata/METADATA")
        result_packages = handler.parse(test_file, package_only=True)
        package_data = dict(
            datasource_id=handler.datasource_id,
            type="generic",
            name="exfatprogs",
            description="Userspace utilities for creating, fixing and debugging exfat filesystems.",
            version="1.1.0",
            homepage_url="https://github.com/exfatprogs/exfatprogs",
            vcs_url="https://github.com/exfatprogs/exfatprogs/",
            extra_data=dict(license_type="RESTRICTED", last_upgrade_date="2021-04-09"),
        )
        expected_packages = [
            models.PackageData.from_data(package_data, package_only=True)
        ]
        compare_package_results(expected_packages, list(result_packages))

    def test_android_metadata_parse_by_exception_only(self):
        test_file = self.get_test_loc("android_metadata/by-exception/METADATA")
        result_packages = handler.parse(test_file, package_only=True)
        package_data = dict(
            datasource_id=handler.datasource_id,
            type="generic",
            extra_data=dict(license_type="BY_EXCEPTION_ONLY"),
        )
        expected_packages = [
            models.PackageData.from_data(package_data, package_only=True)
        ]
        compare_package_results(expected_packages, list(result_packages))

    def test_is_datafile(self):
        assert handler.is_datafile(self.get_test_loc("android_metadata/METADATA"))
        assert handler.is_datafile(
            self.get_test_loc("android_metadata/by-exception/METADATA")
        )
