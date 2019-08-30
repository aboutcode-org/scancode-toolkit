# -*- coding: utf-8 -*-
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
from __future__ import division
from __future__ import unicode_literals

import io
import os

import pytest

from commoncode.system import py2
from commoncode.system import py3
from commoncode.testcase import FileDrivenTesting


pytestmark = pytest.mark.scanslow


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def check_plugin(plugin_class, test_file='reuse/vb.json', force_text=False):
    # this is the result of this scan:
    # ./scancode -clip --summary --license-clarity-score --summary-key-files
    # --classify  samples/ --json-pp vb.json -n
    test_file = test_env.get_test_loc(test_file)
    from scancode.resource import VirtualCodebase
    cb = VirtualCodebase(test_file)

    result_file = test_env.get_temp_file('reuse')
    op = plugin_class()
    if force_text:
        with io.open(result_file, 'w', encoding='utf-8') as out:
            op.process_codebase(cb, out)
    else:
        if py2:
            mode = 'wb'
        if py3:
            mode = 'w'
        with io.open(result_file, mode) as out:
            op.process_codebase(cb, out)

    with io.open(result_file, 'r', encoding='utf-8') as inp:
        assert 'zlib' in inp.read()


def test_can_call_json_output_from_regular_code_with_virtualcodebase():
    from formattedcode.output_json import JsonCompactOutput as plug
    check_plugin(plug, 'reuse/vb.json')


def test_can_call_jsonpp_output_from_regular_code_with_virtualcodebase():
    from formattedcode.output_json import JsonPrettyOutput as plug
    check_plugin(plug, 'reuse/vb.json')


def test_can_call_jsonlines_output_from_regular_code_with_virtualcodebase():
    from formattedcode.output_jsonlines import JsonLinesOutput as plug
    check_plugin(plug, 'reuse/vb.json')


def test_can_call_spdxtv_output_from_regular_code_with_virtualcodebase():
    from formattedcode.output_spdx import SpdxTvOutput as plug
    check_plugin(plug, 'reuse/vb.json', force_text=True)


def test_can_call_spdxrdf_output_from_regular_code_with_virtualcodebase():
    from formattedcode.output_spdx import SpdxRdfOutput as plug
    check_plugin(plug, 'reuse/vb.json', force_text=True)


def test_can_call_html_output_from_regular_code_with_virtualcodebase():
    from formattedcode.output_html import  HtmlOutput as plug
    check_plugin(plug, 'reuse/vb.json', force_text=True)
