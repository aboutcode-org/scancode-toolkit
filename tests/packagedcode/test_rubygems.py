#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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
import io
import json
import os
from unittest.case import expectedFailure

import saneyaml

from commoncode import compat
from commoncode.system import py2
from commoncode.system import py3
from commoncode import text
from commoncode.testcase import FileBasedTesting
from packagedcode import rubygems
from packages_test_utils import PackageTester


# TODO: Add test with https://rubygems.org/gems/pbox2d/versions/1.0.3-java
# this is a multiple personality package (Java  and Ruby)
# see also https://rubygems.org/downloads/jaro_winkler-1.5.1-java.gem

# NOTE: this needs to be implemented first
@expectedFailure
class TestRubyGemspec(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_gemspec(self, test_loc, expected_loc, regen=False):
        test_loc = self.get_test_loc(test_loc)
        expected_loc = self.get_test_loc(expected_loc)
        results = rubygems.get_gemspec_data(test_loc)

        try:
            # fix absolute paths for testing
            rel_path = results['loaded_from']
            rel_path = [p for p in rel_path.split('/') if p]
            rel_path = '/'.join(rel_path[-2:])
            results['loaded_from'] = rel_path
        except:
            pass

        if regen:
            if py2:
                mode = 'wb'
            if py3:
                mode = 'w'
            with open(expected_loc, mode) as ex:
                json.dump(results, ex, indent=2)
        with io.open(expected_loc, encoding='UTF-8') as ex:
            expected = json.load(ex)

        assert sorted(expected.items()) == sorted(results.items())

    def test_rubygems_can_parse_gemspec_address_standardization_gemspec(self):
        self.check_gemspec(
            'rubygems/gemspec/address_standardization.gemspec',
            'rubygems/gemspec/address_standardization.gemspec.expected.json')

    def test_rubygems_can_parse_gemspec_arel_gemspec(self):
        self.check_gemspec(
            'rubygems/gemspec/arel.gemspec',
            'rubygems/gemspec/arel.gemspec.expected.json')

    def test_rubygems_modern_gemspec(self):
        self.check_gemspec(
            'rubygems/gemspec/cat.gemspec',
            'rubygems/gemspec/cat.gemspec.expected.json')

    def test_rubygems_oj_gemspec(self):
        self.check_gemspec(
            'rubygems/gemspec/oj.gemspec',
            'rubygems/gemspec/oj.gemspec.expected.json')

    def test_rubygems_rubocop_gemspec(self):
        self.check_gemspec(
            'rubygems/gemspec/rubocop.gemspec',
            'rubygems/gemspec/rubocop.gemspec.expected.json')

    def test_rubygems_gemspec_with_variables(self):
        self.check_gemspec(
            'rubygems/gemspec/with_variables.gemspec',
            'rubygems/gemspec/with_variables.gemspec.expected.json')


class TestRubyGemMetadata(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_build_rubygem_package_does_not_crash(self):
        test_file = self.get_test_loc('rubygems/metadata/metadata.gz-extract')
        with open(test_file) as tf:
            metadata = saneyaml.load(tf.read())
        rubygems.build_rubygem_package(metadata)


def relative_walk(dir_path, extension='.gem'):
    """
    Walk `dir_path` and yield paths that end with `extension` relative to
    dir_path for.
    """
    for base_dir, _dirs, files in os.walk(dir_path):
        for file_name in files:
            if file_name.endswith(extension):
                file_path = os.path.join(base_dir, file_name)
                file_path = file_path.replace(dir_path, '', 1)
                file_path = file_path.strip(os.path.sep)
                yield file_path


def create_test_function(test_loc, test_name, regen=False):
    """
    Return a test function closed on test arguments.
    """
    # closure on the test params
    def check_rubygem(self):
        loc = self.get_test_loc(test_loc)
        expected_json_loc = loc + '.json'
        package = rubygems.get_gem_package(location=loc)
        package.license_expression = package.compute_normalized_license()
        package = [package.to_dict()]
        if regen:
            if py2:
                wmode = 'wb'
            if py3:
                wmode = 'w'
            with io.open(expected_json_loc, wmode) as ex:
                json.dump(package, ex, indent=2)

        with io.open(expected_json_loc, encoding='utf-8') as ex:
            expected = json.load(ex, object_pairs_hook=OrderedDict)
        assert expected == package

    if py2 and isinstance(test_name, compat.unicode):
        test_name = test_name.encode('utf-8')
    if py3 and isinstance(test_name, bytes):
        test_name = test_name.decode('utf-8')

    check_rubygem.__name__ = test_name

    return check_rubygem


class TestRubyGemsDataDriven(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def build_tests(test_dir, clazz, prefix='test_rubygems_parse_', regen=False):
    """
    Dynamically build test methods for each gem in `test_dir`  and
    attach the test method to the `clazz` class.
    """
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
    test_dir = os.path.join(test_data_dir, test_dir)
    # loop through all items and attach a test method to our test class
    for test_file in relative_walk(test_dir):
        test_name = prefix + text.python_safe_name(test_file)
        test_pom_loc = os.path.join(test_dir, test_file)
        test_method = create_test_function(test_pom_loc, test_name, regen=regen)
        # attach that method to the class
        setattr(clazz, test_name, test_method)


class TestRubyGemfileLock(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_ruby_gemfile_lock_as_dict(self):
        test_file = self.get_test_loc('rubygems/gemfile-lock/Gemfile.lock')
        expected_loc = self.get_test_loc('rubygems/gemfile-lock/Gemfile.lock.expected')
        packages = rubygems.RubyGem.recognize(test_file)
        self.check_packages(packages, expected_loc, regen=False)


build_tests(test_dir='rubygems/gem', clazz=TestRubyGemsDataDriven,
            prefix='test_get_gem_package_', regen=False)
