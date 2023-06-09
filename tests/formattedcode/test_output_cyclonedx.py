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
import json
import os

import saneyaml
from lxml import etree
from commoncode.testcase import FileDrivenTesting

from formattedcode.output_cyclonedx import CycloneDxComponent
from formattedcode.output_cyclonedx import CycloneDxExternalRef
from formattedcode.output_cyclonedx import CycloneDxHashObject
from formattedcode.output_cyclonedx import CycloneDxLicenseExpression
from formattedcode.output_cyclonedx import CycloneDxMetadata
from formattedcode.output_cyclonedx import get_author_from_parties
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def load_and_clean_json(result_file):
    with io.open(result_file, encoding='utf-8') as res:
        result = json.loads(res.read())
    result.pop('metadata', None)
    result.pop('serialNumber', None)
    return result


def check_cyclone_output(expected_file, result_file, regen=REGEN_TEST_FIXTURES):
    """
    Check that expected and result_file are equal. Ignore headers.
    If `regen` is True the expected_file is overwritten with `results_file`.
    """
    result = load_and_clean_json(result_file)

    if regen:
        with open(expected_file, 'w') as reg:
            json.dump(result, reg, indent=2, separators=(',', ': '))

    expected = load_and_clean_json(expected_file)

    # NOTE we redump the JSON as a YAML string for easier display of
    # the failures comparison/diff
    if result != expected:
        expected = saneyaml.dump(expected)
        result = saneyaml.dump(result)
        assert result == expected


def check_cyclone_xml_output(expected_file, result_file, regen=REGEN_TEST_FIXTURES):
    """
    Check that expected and result_file are equal. Ignore headers.
    If `regen` is True the expected_file is overwritten with `results_file`.
    """
    if regen:
        with open(result_file) as rf, open(expected_file, 'w') as ef:
            expected = rf.read()
            ef.write(expected)

    result = load_and_clean_xml(result_file)
    expected = load_and_clean_xml(expected_file)
    assert result == expected


def load_and_clean_xml(location):
    """
    Return plain Python nested data for the CycloneDX file at location
    suitable for comparison. The file content is cleaned from variable
    parts such as dates, generated UUIDs and versions
    """
    with open(location, 'rb') as co:
        xml_text = co.read()
    parser = etree.XMLParser(
        recover=True,
        remove_comments=True,
        remove_pis=True,
        remove_blank_text=True,
        resolve_entities=False
    )
    bom = etree.fromstring(xml_text, parser=parser)
    bom.set('serialNumber', '')

    metadata = bom.find('{http://cyclonedx.org/schema/bom/1.3}metadata')
    bom.remove(metadata)
    return etree.tostring(bom, encoding='unicode', pretty_print=True)


def test_can_encode_component():
    purl = 'pkg:generic/test@1'
    hashes = [CycloneDxHashObject(alg='MD5', content='not-a-hash')]
    licenses = [CycloneDxLicenseExpression(expression='MIT or Apache-2.0')]

    component = CycloneDxComponent(
        name='test',
        version='1',
        purl=purl,
        bom_ref=purl,
        hashes=hashes,
        licenses=licenses,
    )
    expected = {
        'author': None,
        'bom-ref': 'pkg:generic/test@1',
        'copyright': None,
        'description': None,
        'externalReferences': [],
        'group': None,
        'hashes': [{'alg': 'MD5',
                    'content': 'not-a-hash'}],
        'licenses': [{'expression': 'MIT or Apache-2.0'}],
        'name': 'test',
        'properties': [],
        'purl': 'pkg:generic/test@1',
        'scope': 'required',
        'type': 'library',
        'version': '1',
    }
    assert component.to_dict() == expected


def test_get_author_from_parties():
    parties = [
        {'type': 'person', 'role': 'author', 'name': 'author a'},
        {'type': 'person', 'role': 'author', 'name': 'author b'},
        {'type': 'person', 'role': 'maintainer', 'name': 'author b'},
    ]
    author = get_author_from_parties(parties)
    assert author.splitlines() == ["author a", "author b"]


def test_get_author_from_parties_default_none():
    parties = [
        {'type': 'person', 'role': 'maintainer', 'name': 'the maintainer'}
    ]
    assert not get_author_from_parties(parties)


def test_get_licenses_from_package():
    package = {'declared_license_expression': 'mit or gpl-2.0'}
    licenses = [l.to_dict() for l in CycloneDxLicenseExpression.from_package(package)]
    expected = [{'expression': 'MIT OR GPL-2.0-only'}]
    assert licenses == expected


def test_can_get_hashes_from_package():
    package = {
        'md5': 'cc5ea2445954a282f622042252a6eef9',
        'sha1': 'b754cee9a3d3501d32ae200e07f4e518cd8294b8',
        'sha256': '4795dae6518d60e4e5bd7103f50f5f86f8c07cbdc36aa76f410a0d534edc8ec5',
        'sha512': 'f385a335b20e0bd933b3d59abc41e9b05f4333db6cd948b579b2562d617a6fa35e13ffa0c2eceae031afcf73c5fb7e1660fade207ddf2a0e312e006eb115e9b0',
    }
    hashes = [h.to_dict() for h in CycloneDxHashObject.from_package(package=package)]
    expected = [
        {'alg': 'MD5',
         'content': 'cc5ea2445954a282f622042252a6eef9'},
        {'alg': 'SHA-1',
         'content': 'b754cee9a3d3501d32ae200e07f4e518cd8294b8'},
        {'alg': 'SHA-256',
         'content': '4795dae6518d60e4e5bd7103f50f5f86f8c07cbdc36aa76f410a0d534edc8ec5'},
        {'alg': 'SHA-512',
         'content': 'f385a335b20e0bd933b3d59abc41e9b05f4333db6cd948b579b2562d617a6fa35e13ffa0c2eceae031afcf73c5fb7e1660fade207ddf2a0e312e006eb115e9b0'},
    ]
    assert hashes == expected


def test_get_extref_from_license_expression_returns_ref_for_license_refs():
    license_expression = 'mit AND ac3filter'
    refs = CycloneDxExternalRef.from_license_expression(license_expression)
    refs = [r.to_dict() for r in refs]


def test_get_extref_from_license_expression_returns_nothing_for_none():
    assert list(CycloneDxExternalRef.from_license_expression(None)) == []
    assert list(CycloneDxExternalRef.from_license_expression('')) == []


def test_get_extref_from_license_expression_is_empty_for_plain_spdx():
    assert list(CycloneDxExternalRef.from_license_expression('mit')) == []


def test_CycloneDxMetadata_from_headers():
    headers = [{
        'tool_name': 'scancode-toolkit',
        'tool_version': '31.1.1',
        'notice': 'some notice',
        'message': 'some message',
        'errors': ['some error'],
        'warnings': ['some warning'],
        'extra_data': {'spdx_version': '3.1.2'}
    }]
    m = CycloneDxMetadata.from_headers(headers).to_dict()
    m.pop('timestamp')
    expected = {
        'properties': [
            {'name': 'notice', 'value': 'some notice'},
            {'name': 'errors', 'value': ['some error']},
            {'name': 'warnings', 'value': ['some warning']},
            {'name': 'message', 'value': 'some message'},
            {'name': 'spdx_version', 'value': '3.1.2'},
        ],
        'tools': [
            {'name': 'scancode-toolkit', 'vendor': 'AboutCode.org', 'version': '31.1.1'},
        ],
    }
    assert m == expected


def test_cyclonedx_plugin_does_not_fail_without_packages():
    test_dir = test_env.get_test_loc('cyclonedx/simple')
    result_file = test_env.get_temp_file('cyclonedx.json')
    run_scan_click([test_dir, '--cyclonedx', result_file])
    expected_file = test_env.get_test_loc('cyclonedx/expected-without-packages.json')
    check_cyclone_output(expected_file, result_file, regen=REGEN_TEST_FIXTURES)


def test_cyclonedx_plugin_json():
    test_dir = test_env.get_test_loc('cyclonedx/simple')
    result_file = test_env.get_temp_file('cyclonedx.json')
    run_scan_click(['--package', test_dir, '--cyclonedx', result_file])
    expected_file = test_env.get_test_loc('cyclonedx/simple-expected.json')
    check_cyclone_output(expected_file, result_file, regen=REGEN_TEST_FIXTURES)


def test_cyclonedx_plugin_json_simple_package_icu():
    test_dir = test_env.get_test_loc('cyclonedx/simple-icu')
    result_file = test_env.get_temp_file('cyclonedx.json')
    run_scan_click(['--package', '--license', test_dir, '--cyclonedx', result_file])
    expected_file = test_env.get_test_loc('cyclonedx/simple-icu-expected.json')
    check_cyclone_output(expected_file, result_file, regen=REGEN_TEST_FIXTURES)


def test_cyclonedx_plugin_xml_components_and_dependencies_are_serialized_correctly():
    test_dir = test_env.get_test_loc('cyclonedx/simple')
    result_file = test_env.get_temp_file('cyclonedx.xml')
    run_scan_click(['--package', test_dir, '--cyclonedx-xml', result_file])
    expected_file = test_env.get_test_loc('cyclonedx/expected.xml')
    check_cyclone_xml_output(expected_file, result_file, regen=REGEN_TEST_FIXTURES)
