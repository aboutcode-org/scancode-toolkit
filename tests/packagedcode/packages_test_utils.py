#
# Copyright (c) 2016 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict
import os.path
import json
import shutil

from commoncode import testcase


class PackageTester(testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_package(self, package, expected_loc, regen=False):
        """
        Helper to test a package object against an expected JSON file.
        """
        expected_loc = self.get_test_loc(expected_loc)

        package.license_expression = package.compute_normalized_license()
        results = package.to_dict()

        if regen:
            regened_exp_loc = self.get_temp_file()
            wmode = 'w'
            with open(regened_exp_loc, wmode) as ex:
                json.dump(results, ex, indent=2, separators=(',', ': '))

            expected_dir = os.path.dirname(expected_loc)
            if not os.path.exists(expected_dir):
                os.makedirs(expected_dir)
            shutil.copy(regened_exp_loc, expected_loc)

        with open(expected_loc, 'rb') as ex:
            expected = json.load(ex, encoding='utf-8', object_pairs_hook=OrderedDict)

        try:
            assert expected == results
        except AssertionError:
            assert json.dumps(expected, indent=2) == json.dumps(results, indent=2)

    def check_packages(self, packages, expected_loc, regen=False):
        """
        Helper to test multiple package objects against an expected JSON file.
        """
        expected_loc = self.get_test_loc(expected_loc)

        results = []
        for package in packages:
            package.license_expression = package.compute_normalized_license()
            results.append(package.to_dict())

        if regen:
            regened_exp_loc = self.get_temp_file()
            wmode = 'w'
            with open(regened_exp_loc, wmode) as ex:
                json.dump(results, ex, indent=2, separators=(',', ': '))

            expected_dir = os.path.dirname(expected_loc)
            if not os.path.exists(expected_dir):
                os.makedirs(expected_dir)
            shutil.copy(regened_exp_loc, expected_loc)

        with open(expected_loc, 'rb') as ex:
            expected_packages = json.load(ex, encoding='utf-8', object_pairs_hook=OrderedDict)

        for expected_package, result in zip(expected_packages, results):
            assert expected_package == result
