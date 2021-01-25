#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#
# Visit https://aboutcode.org and https://github.com/nexB/scancode-toolkit for
# support and download. ScanCode is a trademark of nexB Inc.
#
# The ScanCode software is licensed under the Apache License version 2.0.
# The ScanCode open data is licensed under CC-BY-4.0.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from unittest import TestCase

from packagedcode.licensing import get_normalized_expression


class TestLicensing(TestCase):
    def test_get_normalized_expression(self):
        assert 'mit' == get_normalized_expression('mit')
        assert 'apache-2.0 AND unknown' == get_normalized_expression('mit or asasa or Apache-2.0')
        assert 'apache-2.0 AND unknown' == get_normalized_expression('mit or asasa or Apache-2.0')
        assert 'mit OR apache-2.0' == get_normalized_expression('mit asasa or Apache-2.0')
        assert get_normalized_expression('') is None
        assert get_normalized_expression(None) is None
