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
import hashlib
import os
import re

import pytest
import xmltodict

from commoncode.testcase import FileDrivenTesting

from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import run_scan_plain
from scancode_config import REGEN_TEST_FIXTURES


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def write_spdx_for_checksum_test(file_data, as_tagvalue, monkeypatch):
    from formattedcode.output_spdx import write_spdx
    from licensedcode import cache

    # These inputs contain no license detections and need no license database.
    monkeypatch.setattr(cache, 'get_licenses_db', lambda: {})
    output = io.StringIO()
    write_spdx(
        codebase=None,
        output_file=output,
        files=[file_data],
        tool_name='ScanCode',
        tool_version='test',
        notice='test',
        package_name='sample',
        as_tagvalue=as_tagvalue,
    )
    return output.getvalue()


@pytest.mark.parametrize('as_tagvalue', [True, False], ids=['tagvalue', 'rdf'])
@pytest.mark.parametrize('checksum_data', [{}, {'sha1': None}, {'sha1': ''}])
def test_spdx_missing_sha1_rejected(as_tagvalue, checksum_data, monkeypatch):
    file_data = {'type': 'file', 'path': 'sample.txt', 'file_type': 'ASCII text'}
    file_data.update(checksum_data)
    with pytest.raises(ValueError, match='missing SHA1.*sample.txt'):
        write_spdx_for_checksum_test(file_data, as_tagvalue, monkeypatch)


@pytest.mark.parametrize('as_tagvalue', [True, False], ids=['tagvalue', 'rdf'])
def test_spdx_file_checksum_preserves_known_sha1(as_tagvalue, monkeypatch):
    checksum = hashlib.sha1(b'non-empty contents').hexdigest()
    result = write_spdx_for_checksum_test(
        {'type': 'file', 'path': 'sample.txt', 'sha1': checksum},
        as_tagvalue,
        monkeypatch,
    )
    assert checksum in result
    assert hashlib.sha1(b'').hexdigest() not in result


@pytest.mark.parametrize('as_tagvalue', [True, False], ids=['tagvalue', 'rdf'])
def test_spdx_file_checksum_preserves_empty_file_hash(as_tagvalue, monkeypatch):
    result = write_spdx_for_checksum_test(
        {'type': 'file', 'path': 'empty.txt', 'file_type': 'empty'},
        as_tagvalue,
        monkeypatch,
    )
    assert hashlib.sha1(b'').hexdigest() in result


@pytest.mark.parametrize('as_tagvalue', [True, False], ids=['tagvalue', 'rdf'])
def test_spdx_file_checksum_does_not_require_directory_hash(as_tagvalue, monkeypatch):
    result = write_spdx_for_checksum_test(
        {'type': 'directory', 'path': 'directory'},
        as_tagvalue,
        monkeypatch,
    )
    assert "No results for package 'sample'." in result


@pytest.mark.parametrize('output_option', ['--spdx-tv', '--spdx-rdf'])
def test_spdx_missing_sha1_cli_error(output_option, tmp_path, monkeypatch):
    from licensedcode import cache

    monkeypatch.setattr(cache, 'get_licenses_db', lambda: {})
    source = tmp_path / 'sample.txt'
    source.write_text('non-empty contents', encoding='utf-8')
    output = tmp_path / 'output.spdx'
    result = run_scan_click(
        ['--email', str(source), output_option, str(output)],
        expected_rc=1,
        retry=False,
    )
    assert 'missing SHA1' in result.output
    assert 'sample.txt' in result.output
    assert '--info' in result.output
    if output.exists():
        assert not output.read_text(encoding='utf-8')


@pytest.mark.parametrize('output_option', ['--spdx-tv', '--spdx-rdf'])
@pytest.mark.parametrize('content', [b'non-empty contents', b''])
def test_spdx_file_checksum_cli_with_info(output_option, content, tmp_path, monkeypatch):
    from licensedcode import cache

    monkeypatch.setattr(cache, 'get_licenses_db', lambda: {})
    source = tmp_path / 'sample.txt'
    source.write_bytes(content)
    output = tmp_path / 'output.spdx'
    run_scan_click(['--info', str(source), output_option, str(output)])
    assert hashlib.sha1(content).hexdigest() in output.read_text(encoding='utf-8')


def strip_variable_text(rdf_text):
    """
    Return rdf_text stripped from variable parts such as rdf nodeids
    """

    namespace_regex = re.compile('SpdxDocument rdf:about="(.+)#SPDXRef-DOCUMENT"')
    namespace = namespace_regex.search(rdf_text).group(1)
    rdf_text = re.compile(namespace).sub('', rdf_text)

    replace_nid = re.compile('rdf:nodeID="[^\\"]*"').sub
    rdf_text = replace_nid('', rdf_text)

    replace_creation = re.compile('<spdx:creationInfo>.*</spdx:creationInfo>', re.DOTALL).sub  # NOQA
    rdf_text = replace_creation('', rdf_text)

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
    with io.open(location, encoding='utf-8') as co:
        content = co.read()
    content = strip_variable_text(content)
    data = xmltodict.parse(content, dict_constructor=dict)
    return sort_nested(data)


def sort_nested(data):
    """
    Return a new ordered and sorted mapping or sequence from a `data` mapping or
    sequence with any nested sequences or mappings sorted recursively.
    """
    seqtypes = list, tuple
    maptypes = dict, dict
    coltypes = seqtypes + maptypes

    if isinstance(data, maptypes):
        new_data = []
        for k, v in data.items():
            if isinstance(v, coltypes):
                v = sort_nested(v)
            new_data.append((k, v))
        return dict(sorted(new_data, key=_sorter))

    elif isinstance(data, seqtypes):
        new_data = []
        for v in data:
            if isinstance(v, coltypes):
                v = sort_nested(v)
            new_data.append(v)
        return sorted(new_data, key=_sorter)


def _sorter(data):
    """
    Return a tree of tuples (type, items sequence) for each items in a nested
    data structure composed of mappings and sequences. Used as a sorting key.
    """
    seqtypes = list, tuple
    maptypes = dict, dict
    coltypes = seqtypes + maptypes

    if isinstance(data, maptypes):
        new_data = []
        for k, v in data.items():
            if isinstance(v, coltypes):
                v = _sorter(v)
            new_data.append((k, v))
        return repr(tuple(sorted(new_data)))

    elif isinstance(data, seqtypes):
        new_data = []
        for v in data:
            if isinstance(v, coltypes):
                v = _sorter(v)
            new_data.append(v)
        return repr(tuple(sorted(new_data)))
    else:
        return repr(data)


def check_rdf_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES):
    """
    Check that expected and result_file are equal.
    Both are paths to SPDX RDF XML files, UTF-8 encoded.
    """
    import json
    result = load_and_clean_rdf(result_file)
    if regen:
        expected = result
        with io.open(expected_file, 'w', encoding='utf-8') as o:
            json.dump(result, o, indent=2)
    else:
        with io.open(expected_file, encoding='utf-8') as i:
            expected = json.load(i)

    assert json.dumps(result, indent=2) == json.dumps(expected, indent=2)


def load_and_clean_tv(location):
    """
    Return a mapping for the SPDX TV file at location suitable for
    comparison. The file content is cleaned from variable parts such as
    dates, generated UUIDs and versions
    """
    with io.open(location, encoding='utf-8') as co:
        content = co.read()
    lines = []
    lines_append = lines.append

    dns = 'DocumentNamespace: http://spdx.org/spdxdocs/'

    for line in content.splitlines(False):
        line = line.strip()
        if not line:
            continue
        if line.startswith('LicenseListVersion'):
            continue
        if line.startswith(('Creator: ', 'Created: ',)):
            continue
        if line.startswith(dns):
            # only keep the left side of
            # DocumentNamespace: http://spdx.org/spdxdocs/unicode-ea31be0f-16de-4eab-9fc7-4e3bafb753d3
            line, _, _ = line.partition('-')
    
        lines_append(line)

    return '\n'.join(lines)


def check_tv_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES):
    """
    Check that expected and result_file are equal.
    Both are paths to plain spdx tv text files, UTF-8 encoded.
    """
    result = load_and_clean_tv(result_file)
    if regen:
        with io.open(expected_file, 'w', encoding='utf-8') as o:
            o.write(result)

    expected = load_and_clean_tv(expected_file)
    assert result == expected


def test_spdx_rdf_basic():
    test_file = test_env.get_test_loc('spdx/simple/test.txt')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('spdx/simple/expected.rdf')
    run_scan_click([test_file, '-clip', '--spdx-rdf', result_file])
    check_rdf_scan(expected_file, result_file)


def test_spdx_tv_basic():
    test_dir = test_env.get_test_loc('spdx/simple/test.txt')
    result_file = test_env.get_temp_file('tv')
    expected_file = test_env.get_test_loc('spdx/simple/expected.tv')
    run_scan_click([test_dir, '-clip', '--spdx-tv', result_file])
    check_tv_scan(expected_file, result_file)


@pytest.mark.scanslow
def test_spdx_rdf_with_known_licenses():
    test_dir = test_env.get_test_loc('spdx/license_known/scan')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('spdx/license_known/expected.rdf')
    run_scan_click([test_dir, '-clip', '--spdx-rdf', result_file])
    check_rdf_scan(expected_file, result_file)


@pytest.mark.scanslow
def test_spdx_rdf_with_license_ref():
    test_dir = test_env.get_test_loc('spdx/license_ref/scan')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('spdx/license_ref/expected.rdf')
    run_scan_click([test_dir, '-clip', '--spdx-rdf', result_file])
    check_rdf_scan(expected_file, result_file)


@pytest.mark.scanslow
def test_spdx_tv_with_known_licenses():
    test_dir = test_env.get_test_loc('spdx/license_known/scan')
    result_file = test_env.get_temp_file('tv')
    expected_file = test_env.get_test_loc('spdx/license_known/expected.tv')
    run_scan_click([test_dir, '-clip', '--spdx-tv', result_file])
    check_tv_scan(expected_file, result_file)


@pytest.mark.scanslow
def test_spdx_tv_with_license_ref():
    test_dir = test_env.get_test_loc('spdx/license_ref/scan')
    result_file = test_env.get_temp_file('tv')
    expected_file = test_env.get_test_loc('spdx/license_ref/expected.tv')
    run_scan_click([test_dir, '-clip', '--spdx-tv', result_file])
    check_tv_scan(expected_file, result_file)


@pytest.mark.scanslow
def test_spdx_rdf_with_known_licenses_with_text():
    test_dir = test_env.get_test_loc('spdx/license_known/scan')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('spdx/license_known/expected_with_text.rdf')
    run_scan_click([ '-clip', '--license-text', test_dir, '--spdx-rdf', result_file])
    check_rdf_scan(expected_file, result_file)


@pytest.mark.scanslow
def test_spdx_rdf_with_license_ref_with_text():
    test_dir = test_env.get_test_loc('spdx/license_ref/scan')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('spdx/license_ref/expected_with_text.rdf')
    run_scan_click(['-clip', '--license-text', test_dir, '--spdx-rdf', result_file])
    check_rdf_scan(expected_file, result_file)


@pytest.mark.scanslow
def test_spdx_tv_with_known_licenses_with_text():
    test_dir = test_env.get_test_loc('spdx/license_known/scan')
    result_file = test_env.get_temp_file('tv')
    expected_file = test_env.get_test_loc('spdx/license_known/expected_with_text.tv')
    run_scan_click(['-clip', '--license-text', test_dir, '--spdx-tv', result_file])
    check_tv_scan(expected_file, result_file)


@pytest.mark.scanslow
def test_spdx_tv_with_license_ref_with_text():
    test_dir = test_env.get_test_loc('spdx/license_ref/scan')
    result_file = test_env.get_temp_file('tv')
    expected_file = test_env.get_test_loc('spdx/license_ref/expected_with_text.tv')
    run_scan_click(['-clip', '--license-text', test_dir, '--spdx-tv', result_file])
    check_tv_scan(expected_file, result_file)


@pytest.mark.scanslow
def test_spdx_tv_tree():
    test_dir = test_env.get_test_loc('spdx/tree/scan')
    result_file = test_env.get_temp_file('tv')
    expected_file = test_env.get_test_loc('spdx/tree/expected.tv')
    run_scan_click(['-clip', test_dir, '--spdx-tv', result_file])
    check_tv_scan(expected_file, result_file)


@pytest.mark.scanslow
def test_spdx_rdf_tree():
    test_dir = test_env.get_test_loc('spdx/tree/scan')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('spdx/tree/expected.rdf')
    run_scan_click(['-clip', test_dir, '--spdx-rdf', result_file])
    check_rdf_scan(expected_file, result_file)


@pytest.mark.scanslow
def test_spdx_tv_with_unicode_license_text_does_not_fail():
    test_file = test_env.get_test_loc('spdx/unicode/et131x.h')
    result_file = test_env.get_temp_file('tv')
    expected_file = test_env.get_test_loc('spdx/unicode/expected.tv')
    args = ['--license', '--copyright', '--info', '--strip-root', '--license-text',
            test_file, '--spdx-tv', result_file]
    run_scan_plain(args)
    check_tv_scan(expected_file, result_file)


@pytest.mark.scanslow
def test_spdx_rdf_with_unicode_license_text_does_not_fail():
    test_file = test_env.get_test_loc('spdx/unicode/et131x.h')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('spdx/unicode/expected.rdf')
    args = ['--license', '--copyright', '--info', '--strip-root',
            '--license-text', test_file, '--spdx-rdf', result_file]
    run_scan_plain(args)
    check_rdf_scan(expected_file, result_file)


@pytest.mark.scanslow
def test_spdx_rdf_with_or_later_license_does_not_fail():
    test_file = test_env.get_test_loc('spdx/or_later/test.java')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('spdx/or_later/expected.rdf')
    args = ['--license', '--copyright', '--info', '--strip-root',
            '--license-text', test_file, '--spdx-rdf', result_file]
    run_scan_plain(args)
    check_rdf_scan(expected_file, result_file)


@pytest.mark.scanslow
def test_spdx_tv_with_empty_scan():
    test_file = test_env.get_test_loc('spdx/empty/scan')
    result_file = test_env.get_temp_file('spdx.tv')
    expected_file = test_env.get_test_loc('spdx/empty/expected.tv')
    args = ['--license', '--strip-root', '--info', '--only-findings', test_file, '--spdx-tv', result_file]
    run_scan_plain(args)
    check_tv_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)


@pytest.mark.scanslow
def test_spdx_rdf_with_empty_scan():
    test_file = test_env.get_test_loc('spdx/empty/scan')
    result_file = test_env.get_temp_file('spdx.rdf')
    args = ['--license', '--strip-root', '--info', '--only-findings', test_file, '--spdx-rdf', result_file]
    run_scan_plain(args)
    expected = "<!-- No results for package 'scan'. -->\n"
    results = open(result_file).read()
    assert results == expected


@pytest.mark.scanslow
def test_output_spdx_rdf_can_handle_non_ascii_paths(monkeypatch):
    from licensedcode import cache

    monkeypatch.setattr(cache, 'get_licenses_db', lambda: {})
    test_file = test_env.get_test_loc('spdx/unicode.json')
    result_file = test_env.get_temp_file(extension='spdx', file_name='test_spdx')
    run_scan_click(['--from-json', test_file, '--spdx-rdf', result_file])
    with io.open(result_file, encoding='utf-8') as res:
        results = res.read()
    assert 'han/据.svg' in results

def test_output_spdx_tv_can_handle_non_ascii_paths(monkeypatch):
    from licensedcode import cache

    monkeypatch.setattr(cache, 'get_licenses_db', lambda: {})
    test_file = test_env.get_test_loc('spdx/unicode.json')
    result_file = test_env.get_temp_file(extension='spdx', file_name='test_spdx')
    run_scan_click(['--from-json', test_file, '--spdx-tv', result_file])
    with io.open(result_file, encoding='utf-8') as res:
        results = res.read()
    assert 'han/据.svg' in results

def test_output_spdx_tv_sh1_of_empty_file():
    test_dir = test_env.get_test_loc('spdx/empty/scan/somefile')
    result_file = test_env.get_temp_file(extension='spdx', file_name='test_spdx')
    run_scan_click([test_dir, '-clip', '--spdx-tv', result_file])
    with io.open(result_file, encoding='utf-8') as res:
        results = res.read()
    assert 'FileChecksum: SHA1: da39a3ee5e6b4b0d3255bfef95601890afd80709' in results
