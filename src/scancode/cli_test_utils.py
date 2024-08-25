#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import json
import os
import time

import saneyaml
from commoncode.system import on_windows
from packageurl import PackageURL

from scancode_config import scancode_root_dir
from scancode_config import REGEN_TEST_FIXTURES


def run_scan_plain(
    options,
    cwd=None,
    test_mode=True,
    expected_rc=0,
    env=None,
    retry=True,
):
    """
    Run a scan as a plain subprocess. Return rc, stdout, stderr.
    """

    from commoncode.command import execute

    options = add_windows_extra_timeout(options)

    if test_mode and '--test-mode' not in options:
        options.append('--test-mode')

    if not env:
        env = dict(os.environ)

    scmd = 'scancode'
    scan_cmd = os.path.join(scancode_root_dir, scmd)
    rc, stdout, stderr = execute(
        cmd_loc=scan_cmd,
        args=options,
        cwd=cwd,
        env=env,
    )

    if retry and rc != expected_rc:
        # wait and rerun in verbose mode to get more in the output
        time.sleep(1)
        if '--verbose' not in options:
            options.append('--verbose')
        result = rc, stdout, stderr = execute(
            cmd_loc=scan_cmd,
            args=options,
            cwd=cwd,
            env=env,
        )

    if rc != expected_rc:
        opts = get_opts(options)
        error = f'''
Failure to run:
rc: {rc}
scancode {opts}
stdout:
{stdout}

stderr:
{stderr}
''' % locals()
        assert rc == expected_rc, error

    return rc, stdout, stderr


def run_scan_click(
    options,
    monkeypatch=None,
    test_mode=True,
    expected_rc=0,
    env=None,
    retry=True,
):
    """
    Run a scan as a Click-controlled subprocess
    If monkeypatch is provided, a tty with a size (80, 43) is mocked.
    Return a click.testing.Result object.
    If retry is True, wait 10 seconds after a failure and retry once
    """
    import click
    import shutil
    from click.testing import CliRunner
    from scancode import cli

    options = add_windows_extra_timeout(options)

    if test_mode and '--test-mode' not in options:
        options.append('--test-mode')

    if monkeypatch:
        monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
        monkeypatch.setattr(shutil , 'get_terminal_size', lambda: (80, 43,))

    if not env:
        env = dict(os.environ)

    runner = CliRunner()

    result = runner.invoke(cli.scancode, options, catch_exceptions=False, env=env)
    if retry and result.exit_code != expected_rc:
        if on_windows:
            # wait and rerun in verbose mode to get more in the output
            time.sleep(1)
        if '--verbose' not in options:
            options.append('--verbose')
        result = runner.invoke(cli.scancode, options, catch_exceptions=False, env=env)

    if result.exit_code != expected_rc:
        output = result.output
        opts = get_opts(options)
        error = f'''
Failure to run:
rc: {result.exit_code}
scancode {opts}
output:
{output}
'''
        assert result.exit_code == expected_rc, error
    return result


def get_opts(options):
    opts = [o if isinstance(o, str) else repr(o) for o in options]
    return ' '.join(opts)


WINDOWS_CI_TIMEOUT = '222.2'


def add_windows_extra_timeout(options, timeout=WINDOWS_CI_TIMEOUT):
    """
    Add a timeout to an options list if on Windows.
    """
    if on_windows and '--timeout' not in options:
        # somehow the Appevyor windows CI is now much slower and timeouts at 120 secs
        options += ['--timeout', timeout]
    return options


def remove_windows_extra_timeout(scancode_options, timeout=WINDOWS_CI_TIMEOUT):
    """
    Strip a test timeout from a pretty scancode_options mapping if on Windows.
    """
    if on_windows:
        if scancode_options and scancode_options.get('--timeout') == timeout:
            del scancode_options['--timeout']


def check_json_scan(
    expected_file,
    result_file,
    regen=False,
    remove_file_date=False,
    check_headers=False,
    remove_uuid=True,
):
    """
    Check the scan `result_file` JSON results against the `expected_file`
    expected JSON results.

    If `regen` is True the expected_file WILL BE overwritten with the new scan
    results from `results_file`. This is convenient for updating tests
    expectations. But use with caution.

    If `remove_file_date` is True, the file.date attribute is removed.
    If `check_headers` is True, the scan headers attribute is not removed.
    If `remove_uuid` is True, removes UUID from Package and Dependency.
    and if also `regen` is True then regenerate expected file with old UUIDs present already.
    """
    results = load_json_result(location=result_file, remove_file_date=remove_file_date)
    if remove_uuid:
        results = remove_uuid_from_scan(results)

    if not check_headers:
        results.pop('headers', None)

    if regen:
        with open(expected_file, 'w') as reg:
            json.dump(results, reg, indent=2, separators=(',', ': '))
        expected = results
    else:
        expected = load_json_result(location=expected_file, remove_file_date=remove_file_date)
        if remove_uuid:
            expected = remove_uuid_from_scan(expected)
        if not check_headers:
            expected.pop('headers', None)

    # NOTE we redump the JSON as a YAML string for easier display of
    # the failures comparison/diff
    if results != expected:
        expected = saneyaml.dump(expected)
        results = saneyaml.dump(results)
        assert results == expected


def remove_uuid_from_scan(results):
    """
    Remove Package and Dependency UUIDs from a ``results` mapping of scan data .
   UUID fields are generated uniquely and would cause test failures
    when comparing results and expected.
    """
    for package in (results.get('packages') or []):
        package_uid = package.get('package_uid')
        if package_uid:
            package['package_uid'] = purl_with_fake_uuid(package_uid)

    for dependency in (results.get('dependencies') or []):
        dependency_uid = dependency.get('dependency_uid')
        if dependency_uid:
            dependency['dependency_uid'] = purl_with_fake_uuid(dependency_uid)

        for_package_uid = dependency.get('for_package_uid')
        if for_package_uid:
            dependency['for_package_uid'] = purl_with_fake_uuid(for_package_uid)

    for resource in (results.get('files') or []):
        for_packages = []
        has_packages = False
        for fpkg in (resource.get('for_packages') or []):
            has_packages = True
            for_packages.append(purl_with_fake_uuid(fpkg))

        if has_packages:
            resource['for_packages'] = for_packages

    return results


def purl_with_fake_uuid(purl):
    purl = PackageURL.from_string(purl)
    purl.qualifiers['uuid'] = 'fixed-uid-done-for-testing-5642512d1758'
    return purl.to_string()


def load_json_result(location, remove_file_date=False):
    """
    Load the JSON scan results file at `location` location as UTF-8 JSON.

    To help with test resilience against small changes some attributes are
    removed or streamlined such as the  "tool_version" and scan "errors".

    To optionally also remove date attributes from "files" and "headers"
    entries, set the `remove_file_date` argument to True.
    """
    with io.open(location, encoding='utf-8') as res:
        scan_results = res.read()
    return load_json_result_from_string(scan_results, remove_file_date)


def load_json_result_from_string(string, remove_file_date=False):
    """
    Load the JSON scan results `string` as UTF-8 JSON.
    """
    scan_results = json.loads(string)
    # clean new headers attributes
    streamline_headers(scan_results.get('headers', []))
    # clean file_level attributes
    for scanned_file in scan_results['files']:
        streamline_scanned_file(scanned_file, remove_file_date)

    # TODO: remove sort, this should no longer be needed
    scan_results['files'].sort(key=lambda x: x['path'])
    return scan_results


def cleanup_scan(scan_results, remove_file_date=False):
    """
    Cleanup in place the ``scan_results`` mapping for dates, headers and
    other variable data that break tests otherwise.
    """
    # clean new headers attributes
    streamline_headers(scan_results.get('headers', []))
    # clean file_level attributes
    for scanned_file in scan_results['files']:
        streamline_scanned_file(scanned_file, remove_file_date)

    # TODO: remove sort, this should no longer be needed
    scan_results['files'].sort(key=lambda x: x['path'])
    return scan_results


def streamline_errors(errors):
    """
    Modify the `errors` list in place to make it easier to test
    """
    for i, error in enumerate(errors[:]):
        error_lines = error.splitlines(True)
        if len(error_lines) <= 1:
            continue
        # keep only first and last line
        cleaned_error = ''.join([error_lines[0] + error_lines[-1]])
        errors[i] = cleaned_error


def streamline_headers(headers):
    """
    Modify the `headers` list of mappings in place to make it easier to test.
    """
    for hle in headers:
        hle.pop('tool_version', None)
        remove_windows_extra_timeout(hle.get('options', {}))
        hle.pop('start_timestamp', None)
        hle.pop('end_timestamp', None)
        hle.pop('duration', None)
        header = hle.get('options', {})
        header.pop('--verbose', None)
        streamline_errors(hle['errors'])


def streamline_scanned_file(scanned_file, remove_file_date=False, normalize_file_type=True):
    """
    Modify the `scanned_file` mapping for a file in scan results in place to
    make it easier to test.
    """
    streamline_errors(scanned_file.get('scan_errors', []))
    if remove_file_date:
        scanned_file.pop('date', None)
    if normalize_file_type and (file_type := scanned_file.get('file_type')):
        file_type_segments = file_type.split()
        normalized_file_type = file_type_segments[0]
        scanned_file['file_type'] = normalized_file_type


def check_jsonlines_scan(
    expected_file,
    result_file,
    regen=False,
    remove_file_date=False,
    check_headers=False,
    remove_uuid=True,
):
    """
    Check the scan result_file JSON Lines results against the expected_file
    expected JSON results, which is a list of mappings, one per line. If regen
    is True the expected_file WILL BE overwritten with the results. This is
    convenient for updating tests expectations. But use with caution.

    If `remove_file_date` is True, the file.date attribute is removed.
    """
    with io.open(result_file, encoding='utf-8') as res:
        results = [json.loads(line) for line in res]

    if remove_uuid:
        for result in results:
            result = remove_uuid_from_scan(result)
    streamline_jsonlines_scan(results, remove_file_date)

    if regen:
        with open(expected_file, 'w') as reg:
            json.dump(results, reg, indent=2, separators=(',', ': '))

    with io.open(expected_file, encoding='utf-8') as res:
        expected = json.load(res)
        if remove_uuid:
            for result in results:
                result = remove_uuid_from_scan(result)

    streamline_jsonlines_scan(expected, remove_file_date)

    if not check_headers:
        results[0].pop('headers', None)
        expected[0].pop('headers', None)

    expected = json.dumps(expected, indent=2, separators=(',', ': '))
    results = json.dumps(results, indent=2, separators=(',', ': '))
    assert results == expected


def streamline_jsonlines_scan(scan_result, remove_file_date=False):
    """
    Remove or update variable fields from `scan_result`such as version and
    errors to ensure that the test data is stable.

    If `remove_file_date` is True, the file.date attribute is removed.
    """
    for result_line in scan_result:
        headers = result_line.get('headers', {})
        if headers:
            streamline_headers(headers)

        for scanned_file in result_line.get('files', []):
            streamline_scanned_file(scanned_file, remove_file_date)


def check_json(expected, results, regen=REGEN_TEST_FIXTURES):
    """
    Assert if the results JSON file is the same as the expected JSON file.
    """
    if regen:
        with open(expected, 'w') as ex:
            json.dump(results, ex, indent=2, separators=(',', ': '))
    with open(expected) as ex:
        expected = json.load(ex)

    if results != expected:
        expected = saneyaml.dump(expected)
        results = saneyaml.dump(results)
        assert results == expected


def load_both_and_check_json(expected, results, regen=REGEN_TEST_FIXTURES):
    """
    Assert if the results JSON file is the same as the expected JSON file.
    """
    with open(results) as res:
        results = json.load(res)

    if regen:
        mode = 'w'
        with open(expected, mode) as ex:
            json.dump(results, ex, indent=2, separators=(',', ': '))
    with open(expected) as ex:
        expected = json.load(ex)
    assert results == expected
