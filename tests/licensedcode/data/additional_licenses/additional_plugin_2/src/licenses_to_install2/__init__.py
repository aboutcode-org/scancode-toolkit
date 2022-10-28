#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
from os.path import abspath
from os.path import dirname

from licensedcode.additional_license_location_provider import AdditionalLicenseLocationProviderPlugin


class LicensesToInstall2Paths(AdditionalLicenseLocationProviderPlugin):
    def get_locations(self):
        curr_dir = dirname(abspath(__file__))
        locations = {
            'licenses_to_install2': curr_dir,
        }
        return locations
