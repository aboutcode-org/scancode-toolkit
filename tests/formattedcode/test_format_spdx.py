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

import codecs
from collections import OrderedDict
import os
import re

import xmltodict

from commoncode.testcase import FileDrivenTesting
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import run_scan_plain


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def strip_variable_text(rdf_text):
    """
    Return rdf_text stripped from variable parts such as rdf nodeids
    """

    replace_nid = re.compile('rdf:nodeID="[^\"]*"').sub
    rdf_text = replace_nid('', rdf_text)

    replace_creation = re.compile('<ns1:creationInfo>.*</ns1:creationInfo>', re.DOTALL).sub
    rdf_text = replace_creation('', rdf_text)

    replace_pcc = re.compile('<ns1:packageVerificationCode>.*</ns1:packageVerificationCode>', re.DOTALL).sub
    rdf_text = replace_pcc('', rdf_text)
    return rdf_text


def load_and_clean_rdf(location):
    """
    Return plain Python nested data for the SPDX RDF file at location
    suitable for comparison. The file content is cleaned from variable
    parts such as dates, generated UUIDs and versions

    NOTE: we use plain dicts to avoid ordering issues in XML. the SPDX
    tool and lxml do not seem to return a consistent ordering that is
    needed for tests.
    """
    content = codecs.open(location, encoding='utf-8').read()
    content = strip_variable_text(content)
    data = xmltodict.parse(content, dict_constructor=OrderedDict)
    return sort_nested(data)


def sort_nested(data):
    """
    Return a new dict with any nested list sorted recursively.
    """
    if isinstance(data, (OrderedDict, dict)):
        new_data = OrderedDict()
        for k, v in data.items():
            if isinstance(v, list):
                v = sorted(v)
            if isinstance(v, OrderedDict):
                v = sort_nested(v)
            new_data[k] = v
        return new_data
    elif isinstance(data, list):
        new_data = []
        for v in sorted(data):
            if isinstance(v, list):
                v = sort_nested(v)
            if isinstance(v, OrderedDict):
                v = sort_nested(v)
            new_data.append(v)
        return new_data


def check_rdf_scan(expected_file, result_file, regen=False):
    """
    Check that expected and result_file are equal.
    Both are paths to SPDX RDF XML files, UTF-8 encoded.
    """
    import json
    result = load_and_clean_rdf(result_file)
    if regen:
        expected = result
        with codecs.open(expected_file, 'w', encoding='utf-8') as o:
            json.dump(expected, o, indent=2)
    else:
        with codecs.open(expected_file, 'r', encoding='utf-8') as i:
            expected = sort_nested(json.load(i, object_pairs_hook=OrderedDict))
    assert expected == result


def load_and_clean_tv(location):
    """
    Return a mapping for the SPDX TV file at location suitable for
    comparison. The file content is cleaned from variable parts such as
    dates, generated UUIDs and versions
    """
    content = codecs.open(location, encoding='utf-8').read()
    content = [l for l in content.splitlines(False)
        if l and l.strip() and not l.startswith(('Creator: ', 'Created: ',))]
    return '\n'.join(content)


def check_tv_scan(expected_file, result_file, regen=False):
    """
    Check that expected and result_file are equal.
    Both are paths to plain spdx tv text files, UTF-8 encoded.
    """
    result = load_and_clean_tv(result_file)
    if regen:
        with codecs.open(expected_file, 'w', encoding='utf-8') as o:
            o.write(result)

    expected = load_and_clean_tv(expected_file)
    assert expected == result


def test_spdx_rdf_basic():
    test_file = test_env.get_test_loc('spdx/simple/test.txt')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('spdx/simple/expected.rdf')
    result = run_scan_click(['--format', 'spdx-rdf', test_file, result_file])
    assert result.exit_code == 0
    check_rdf_scan(expected_file, result_file)


def test_spdx_tv_basic():
    test_dir = test_env.get_test_loc('spdx/simple/test.txt')
    result_file = test_env.get_temp_file('tv')
    expected_file = test_env.get_test_loc('spdx/simple/expected.tv')
    result = run_scan_click(['--format', 'spdx-tv', test_dir, result_file])
    assert result.exit_code == 0
    check_tv_scan(expected_file, result_file)


def test_spdx_rdf_with_known_licenses():
    test_dir = test_env.get_test_loc('spdx/license_known/scan')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('spdx/license_known/expected.rdf')
    result = run_scan_click(['--format', 'spdx-rdf', test_dir, result_file])
    assert result.exit_code == 0
    check_rdf_scan(expected_file, result_file)


def test_spdx_rdf_with_license_ref():
    test_dir = test_env.get_test_loc('spdx/license_ref/scan')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('spdx/license_ref/expected.rdf')
    result = run_scan_click(['--format', 'spdx-rdf', test_dir, result_file])
    assert result.exit_code == 0
    check_rdf_scan(expected_file, result_file)


def test_spdx_tv_with_known_licenses():
    test_dir = test_env.get_test_loc('spdx/license_known/scan')
    result_file = test_env.get_temp_file('tv')
    expected_file = test_env.get_test_loc('spdx/license_known/expected.tv')
    result = run_scan_click(['--format', 'spdx-tv', test_dir, result_file])
    assert result.exit_code == 0
    check_tv_scan(expected_file, result_file)


def test_spdx_tv_with_license_ref():
    test_dir = test_env.get_test_loc('spdx/license_ref/scan')
    result_file = test_env.get_temp_file('tv')
    expected_file = test_env.get_test_loc('spdx/license_ref/expected.tv')
    result = run_scan_click(['--format', 'spdx-tv', test_dir, result_file])
    assert result.exit_code == 0
    check_tv_scan(expected_file, result_file)


def test_spdx_rdf_with_known_licenses_with_text():
    test_dir = test_env.get_test_loc('spdx/license_known/scan')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('spdx/license_known/expected_with_text.rdf')
    result = run_scan_click(['--format', 'spdx-rdf', '--license-text', test_dir, result_file])
    assert result.exit_code == 0
    check_rdf_scan(expected_file, result_file)


def test_spdx_rdf_with_license_ref_with_text():
    test_dir = test_env.get_test_loc('spdx/license_ref/scan')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('spdx/license_ref/expected_with_text.rdf')
    result = run_scan_click(['--format', 'spdx-rdf', '--license-text', test_dir, result_file])
    assert result.exit_code == 0
    check_rdf_scan(expected_file, result_file)


def test_spdx_tv_with_known_licenses_with_text():
    test_dir = test_env.get_test_loc('spdx/license_known/scan')
    result_file = test_env.get_temp_file('tv')
    expected_file = test_env.get_test_loc('spdx/license_known/expected_with_text.tv')
    result = run_scan_click(['--format', 'spdx-tv', '--license-text', test_dir, result_file])
    assert result.exit_code == 0
    check_tv_scan(expected_file, result_file)


def test_spdx_tv_with_license_ref_with_text():
    test_dir = test_env.get_test_loc('spdx/license_ref/scan')
    result_file = test_env.get_temp_file('tv')
    expected_file = test_env.get_test_loc('spdx/license_ref/expected_with_text.tv')
    result = run_scan_click(['--format', 'spdx-tv', '--license-text', test_dir, result_file])
    assert result.exit_code == 0
    check_tv_scan(expected_file, result_file)


def test_spdx_tv_tree():
    test_dir = test_env.get_test_loc('spdx/tree/scan')
    result_file = test_env.get_temp_file('tv')
    expected_file = test_env.get_test_loc('spdx/tree/expected.tv')
    result = run_scan_click(['--format', 'spdx-tv', test_dir, result_file])
    assert result.exit_code == 0
    check_tv_scan(expected_file, result_file)


def test_spdx_rdf_tree():
    test_dir = test_env.get_test_loc('spdx/tree/scan')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('spdx/tree/expected.rdf')
    result = run_scan_click(['--format', 'spdx-rdf', test_dir, result_file])
    assert result.exit_code == 0
    check_rdf_scan(expected_file, result_file)


def test_spdx_tv_with_unicode_license_text_does_not_fail():
    test_file = test_env.get_test_loc('spdx/unicode/et131x.h')
    result_file = test_env.get_temp_file('tv')
    expected_file = test_env.get_test_loc('spdx/unicode/expected.tv')
    rc, stdout, stderr = run_scan_plain([
        '--license', '--copyright', '--info',
        '--format', 'spdx-tv', '--strip-root', '--license-text',
        '--diag',
         test_file, result_file
    ])
    if rc != 0:
        print('stdout', stdout)
        print('stderr', stderr)
    assert rc == 0
    check_tv_scan(expected_file, result_file, regen=False)


def test_spdx_rdf_with_unicode_license_text_does_not_fail():
    test_file = test_env.get_test_loc('spdx/unicode/et131x.h')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('spdx/unicode/expected.rdf')
    rc, stdout, stderr = run_scan_plain([
        '--license', '--copyright', '--info',
        '--format', 'spdx-rdf', '--strip-root', '--license-text',
        '--diag',
         test_file, result_file
    ])
    if rc != 0:
        print('stdout', stdout)
        print('stderr', stderr)
    assert rc == 0
    check_rdf_scan(expected_file, result_file, regen=False)


def test_spdx_rdf_with_or_later_license_does_not_fail():
    test_file = test_env.get_test_loc('spdx/or_later/test.java')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('spdx/or_later/expected.rdf')
    rc, stdout, stderr = run_scan_plain([
        '--license', '--copyright', '--info',
        '--format', 'spdx-rdf', '--strip-root', '--license-text',
        '--diag',
         test_file, result_file
    ])
    if rc != 0:
        print('stdout', stdout)
        print('stderr', stderr)
    assert rc == 0
    check_rdf_scan(expected_file, result_file, regen=False)
