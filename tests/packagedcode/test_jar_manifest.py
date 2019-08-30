#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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

import io
from collections import OrderedDict
import json
import os.path

from commoncode import compat
from commoncode.system import py2
from commoncode.system import py3
from commoncode import text
from commoncode import testcase
from packagedcode.jar_manifest import parse_manifest
from packagedcode.jar_manifest import get_normalized_package_data


if py2:
    mode = 'wb'
if py3:
    mode = 'w'


class BaseParseManifestCase(testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_parse_manifest(self, test_manifest, regen=False):
        """
        Test the parsing of MANIFEST.MF at test_manifest against an expected JSON
        from the same name with a .json extension.
        """
        test_manifest_loc = self.get_test_loc(test_manifest)
        expected_manifest_loc = test_manifest_loc + '.json'
        parsed_manifest = parse_manifest(location=test_manifest_loc)

        if regen:
            with open(expected_manifest_loc, mode) as ex:
                json.dump(parsed_manifest, ex, indent=2)

        with io.open(expected_manifest_loc, encoding='utf-8') as ex:
            expected = json.load(ex, object_pairs_hook=OrderedDict)

        assert json.dumps(expected) == json.dumps(parsed_manifest)

    def check_get_normalized_package_data(self, test_manifest, regen=False):
        """
        Test the get_normalized_package_data() function using the MANIFEST  file
        at `test_manifest` against an expected JSON from the same name with a
        .package-data.json extension.
        """
        test_manifest_loc = self.get_test_loc(test_manifest)
        manifest_sections = parse_manifest(test_manifest_loc)
        package = get_normalized_package_data(manifest_sections[0]) or {}

        expected_json_loc = test_manifest_loc + '.package-data.json'

        if regen:
            with open(expected_json_loc, mode) as ex:
                json.dump(package, ex, indent=2)

        with io.open(expected_json_loc, 'rb') as ex:
            expected = json.load(ex, encoding='utf-8', object_pairs_hook=OrderedDict)

        assert json.dumps(expected) == json.dumps(package)


class TestMavenMisc(BaseParseManifestCase):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def relative_walk(dir_path):
    """
    Walk path and yield POM files paths relative to dir_path.
    """
    for base_dir, _dirs, files in os.walk(dir_path):
        for file_name in files:
            if file_name == ('MANIFEST.MF'):
                file_path = os.path.join(base_dir, file_name)
                file_path = file_path.replace(dir_path, '', 1)
                file_path = file_path.strip(os.path.sep)
                yield file_path


def create_test_function(test_manifest_loc, test_name, check_parse=True, regen=False):
    """
    Return a test function closed on test arguments for `test_manifest_loc`
    location and with `test_name` method name..

    If check_parse is True, test the parse_manifest; otherwise, test the package
    data normalization.
    """
    # closure on the test params
    if check_parse:
        def test_manifest(self):
            self.check_parse_manifest(test_manifest_loc, regen)
    else:
        def test_manifest(self):
            self.check_get_normalized_package_data(test_manifest_loc, regen)

    # set a proper function name to display in reports and use in discovery
    # function names are best as bytes
    if py2 and isinstance(test_name, compat.unicode):
        test_name = test_name.encode('utf-8')
    if py3 and isinstance(test_name, bytes):
        test_name = test_name.decode('utf-8')
    test_manifest.__name__ = test_name
    return test_manifest


def build_tests(test_dir, clazz, prefix='test_jar_manifest', check_parse=True, regen=False):
    """
    Dynamically build test methods for each MANIFEST.MF in `test_dir` and
    attach the test method to the `clazz` class.

    If check_parse is True, test the parse_manifest; otherwise, test the package
    data normalization.
    """
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
    test_dir = os.path.join(test_data_dir, test_dir)
    # loop through all items and attach a test method to our test class
    for idx, test_file in enumerate(relative_walk(test_dir)):
        test_name = prefix + text.python_safe_name(test_file + str(idx))
        test_manifest_loc = os.path.join(test_dir, test_file)
        test_method = create_test_function(
            test_manifest_loc, test_name, check_parse=check_parse, regen=regen)
        # attach that method to the class
        setattr(clazz, test_name, test_method)


class TestParseManifestDataDriven(BaseParseManifestCase):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


build_tests(test_dir='maven_misc/manifest', clazz=TestParseManifestDataDriven,
            prefix='test_jar_manifest_parse_manifest_',
            check_parse=True, regen=False)


build_tests(test_dir='maven_misc/manifest', clazz=TestParseManifestDataDriven,
            prefix='test_jar_manifest_get_package_data_',
            check_parse=False, regen=False)
