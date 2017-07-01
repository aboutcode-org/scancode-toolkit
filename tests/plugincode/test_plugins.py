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
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download..

from os import path

from unittest import TestCase

from plugincode.formats import validate_plugins
from plugincode.formats import is_template


class TestIgnoreFiles(TestCase):

    def test_error_on_loading_duplicate_format(self):
        test = (
                ('--foo'),
                'duplicate_format'
            )
        with self.assertRaises(Exception) as context:
            validate_plugins([test, test])
        assert 'Invalid plugin found' in context.exception.message

    def test_error_on_invalid_plugin(self):
        test = (
                ('--foo'),
                'invalid_plugin',
                'extra_arg'
            )
        with self.assertRaises(ValueError) as context:
            validate_plugins([test, test])
        assert 'Invalid plugin found' in context.exception.message
