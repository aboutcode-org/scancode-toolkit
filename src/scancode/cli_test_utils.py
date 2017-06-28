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
import json
import os


def remove_dates(scan_result):
    """
    Remove date fields from scan.
    """
    for scanned_file in scan_result['files']:
        if 'date' in scanned_file:
            del scanned_file['date']


def check_json_scan(expected_file, result_file, regen=False, strip_dates=False):
    """
    Check the scan result_file JSON results against the expected_file expected JSON
    results. Removes references to test_dir for the comparison. If regen is True the
    expected_file WILL BE overwritten with the results. This is convenient for
    updating tests expectations. But use with caution.
    """
    result = _load_json_result(result_file)
    if strip_dates:
        remove_dates(result)
    if regen:
        with open(expected_file, 'wb') as reg:
            json.dump(result, reg, indent=2, separators=(',', ': '))
    expected = _load_json_result(expected_file)
    if strip_dates:
        remove_dates(expected)

    # NOTE we redump the JSON as a string for a more efficient comparison of
    # failures
    expected = json.dumps(expected, indent=2, sort_keys=True, separators=(',', ': '))
    result = json.dumps(result, indent=2, sort_keys=True, separators=(',', ': '))
    assert expected == result


def _load_json_result(result_file):
    """
    Load the result file as utf-8 JSON and strip test_dir prefix from
    locations.
    Sort the results by location.
    """
    with codecs.open(result_file, encoding='utf-8') as res:
        scan_result = json.load(res, object_pairs_hook=OrderedDict)

    if scan_result.get('scancode_version'):
        del scan_result['scancode_version']

    scan_result['files'].sort(key=lambda x: x['path'])
    return scan_result


def run_scan_plain(options, cwd=None):
    """
    Run a scan as a plain subprocess. Return rc, stdout, stderr.
    """
    import scancode
    from commoncode.command import execute
    scan_cmd = os.path.join(scancode.root_dir, 'scancode')
    return execute(scan_cmd, options, cwd=cwd)


def run_scan_click(options, monkeypatch=None, catch_exceptions=False):
    """
    Run a scan as a Clikc-controlled subprocess
    If monkeypatch is provided, a tty with a size (80, 43) is mocked.
    Return a click.testing.Result object.
    """
    import click
    from click.testing import CliRunner
    from scancode import cli

    if monkeypatch:
        monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
        monkeypatch.setattr(click , 'get_terminal_size', lambda : (80, 43,))
    runner = CliRunner()
    return runner.invoke(cli.scancode, options, catch_exceptions=catch_exceptions)
