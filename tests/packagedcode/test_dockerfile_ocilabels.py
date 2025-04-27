#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import pytest
import json
import os
from commoncode.testcase import FileDrivenTesting
from scancode.cli_test_utils import run_scan_click
from packagedcode.dockerfile_ocilabels import DockerOCILabelsHandler

class TestDockerOCILabelsHandler(FileDrivenTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    @pytest.mark.parametrize('test_file, expected', [
        ('docker/test.dockerfile', True),
        ('docker/test.containerfile', True),
    ])
    def test_is_datafile(self, test_file, expected):
        test_file_path = self.get_test_loc(test_file)
        assert DockerOCILabelsHandler.is_datafile(test_file_path) == expected

    def test_parse_dockerfile(self):
        test_files = [
            ('test.dockerfile', 'test.dockerfile-package.expected.json'),
            ('test.containerfile', 'test.containerfile-package.expected.json'),
        ]
        for dockerfile, expected in test_files:
            test_file = self.get_test_loc(f'docker/{dockerfile}')
            expected_loc = self.get_test_loc(f'docker/{expected}')
            packages = list(DockerOCILabelsHandler.parse(test_file))
            expected_packages = self.load_expected(expected_loc)
            assert packages == expected_packages

    def test_extract_oci_labels_from_dockerfile(self):
        test_files = [
            ('test.dockerfile', 'test.dockerfile-expected.json'),
            ('test.containerfile', 'test.containerfile-expected.json'),
        ]
        for dockerfile, expected in test_files:
            dockerfile_path = self.get_test_loc(f'docker/{dockerfile}')
            labels = DockerOCILabelsHandler.extract_oci_labels_from_dockerfile(dockerfile_path)
            expected_loc = self.get_test_loc(f'docker/{expected}')
            expected_labels = self.load_expected(expected_loc)
            assert labels == expected_labels

    def test_full_scan_docker_oci_labels_containerfile(self):
        test_file = self.get_test_loc('docker/test.containerfile')
        result_file = self.get_temp_file('json')
        run_scan_click(['--package', test_file, '--json-pp', result_file])
        result = json.load(open(result_file))
        expected_loc = self.get_test_loc('docker/test.containerfile-scan.expected.json')
        expected_package_data = json.load(open(expected_loc))
        package_data = result.get('package_data', [])
        assert len(package_data) == 1
        assert package_data == expected_package_data

    def load_expected(self, expected_file):
        with open(expected_file) as f:
            return json.load(f)