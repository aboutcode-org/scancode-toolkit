# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import os

import pytest

from commoncode.testcase import FileDrivenTesting


pytestmark = pytest.mark.scanslow


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def check_plugin(plugin_class, test_file='reuse/vb.json', force_text=False):
    # this is the result of this scan:
    # ./scancode -clip --summary --license-clarity-score --tallies --tallies-key-files
    # --classify  samples/ --json-pp tests/formattedcode/data/reuse/vb.json

    test_file = test_env.get_test_loc(test_file)
    from commoncode.resource import VirtualCodebase

    cb = VirtualCodebase(test_file)

    result_file = test_env.get_temp_file('reuse')
    op = plugin_class()
    if force_text:
        with io.open(result_file, 'w', encoding='utf-8') as out:
            op.process_codebase(cb, out)
    else:
        with io.open(result_file, 'w') as out:
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
