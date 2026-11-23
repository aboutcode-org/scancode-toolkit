#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from packagedcode import dockerfile
from packagedcode.cache import get_cache
from packagedcode.recognize import recognize_package_data
from packages_test_utils import PackageTester
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


class TestDockerfile(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_is_datafile_dockerfile(self):
        test_file = self.get_test_loc('dockerfile/basic/Dockerfile')
        assert dockerfile.DockerfileHandler.is_datafile(test_file)

    def test_is_datafile_dockerfile_suffix(self):
        test_file = self.get_test_loc('dockerfile/dockerfile-suffix/app/Dockerfile.dev')
        assert dockerfile.DockerfileHandler.is_datafile(test_file)

    def test_is_datafile_containerfile(self):
        test_file = self.get_test_loc('dockerfile/containerfile/Containerfile')
        assert dockerfile.DockerfileHandler.is_datafile(test_file)

    def test_is_datafile_containerfile_suffix(self):
        assert dockerfile.DockerfileHandler.is_datafile(
            'some/dir/Containerfile.cuda', _bare_filename=True
        )

    def test_is_datafile_bare_filename(self):
        assert dockerfile.DockerfileHandler.is_datafile(
            'some/dir/Dockerfile', _bare_filename=True
        )

    def test_is_datafile_dockerfile_txt(self):
        # The '*/Dockerfile.*' pattern also matches a Dockerfile saved with
        # a .txt extension: this is intended behaviour.
        test_file = self.get_test_loc('dockerfile/invalid/Dockerfile.txt')
        assert dockerfile.DockerfileHandler.is_datafile(test_file)

    def test_is_not_datafile_lowercase_dockerfile(self):
        test_file = self.get_test_loc('dockerfile/invalid/dockerfile')
        assert not dockerfile.DockerfileHandler.is_datafile(test_file)

    def test_is_not_datafile_random_file(self):
        test_file = self.get_test_loc('dockerfile/invalid/random_file')
        assert not dockerfile.DockerfileHandler.is_datafile(test_file)

    def test_parse_basic(self):
        test_file = self.get_test_loc('dockerfile/basic/Dockerfile')
        expected_loc = self.get_test_loc('dockerfile/basic/Dockerfile.expected')
        package = dockerfile.DockerfileHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_all_oci_keys(self):
        test_file = self.get_test_loc('dockerfile/all-oci-keys/Dockerfile')
        expected_loc = self.get_test_loc('dockerfile/all-oci-keys/Dockerfile.expected')
        package = dockerfile.DockerfileHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_no_labels(self):
        test_file = self.get_test_loc('dockerfile/no-labels/Dockerfile')
        expected_loc = self.get_test_loc('dockerfile/no-labels/Dockerfile.expected')
        package = dockerfile.DockerfileHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_multi_stage_keeps_last_stage_labels(self):
        # dockerfile-parse only exposes the last stage's labels: labels set
        # in an earlier stage do not survive.
        test_file = self.get_test_loc('dockerfile/multi-stage/Dockerfile')
        expected_loc = self.get_test_loc('dockerfile/multi-stage/Dockerfile.expected')
        package = dockerfile.DockerfileHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_label_schema_labels_are_not_mapped(self):
        # Legacy org.label-schema.* labels are preserved in extra_data but are
        # not mapped onto Package fields: only OCI keys are mapped.
        test_file = self.get_test_loc('dockerfile/label-schema/Dockerfile')
        expected_loc = self.get_test_loc('dockerfile/label-schema/Dockerfile.expected')
        package = dockerfile.DockerfileHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_invalid_yields_nothing(self):
        test_file = self.get_test_loc('dockerfile/invalid/Dockerfile')
        packages = list(dockerfile.DockerfileHandler.parse(test_file))
        assert packages == []

    def test_parse_containerfile(self):
        test_file = self.get_test_loc('dockerfile/containerfile/Containerfile')
        expected_loc = self.get_test_loc('dockerfile/containerfile/Containerfile.expected')
        package = dockerfile.DockerfileHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_dockerfile_suffix(self):
        test_file = self.get_test_loc('dockerfile/dockerfile-suffix/app/Dockerfile.dev')
        expected_loc = self.get_test_loc(
            'dockerfile/dockerfile-suffix/app/Dockerfile.dev.expected'
        )
        package = dockerfile.DockerfileHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_arg_substitution(self):
        test_file = self.get_test_loc('dockerfile/arg-substitution/Dockerfile')
        expected_loc = self.get_test_loc('dockerfile/arg-substitution/Dockerfile.expected')
        package = dockerfile.DockerfileHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_assemble_is_a_noop(self):
        # The core of "non-assembled": the handler never creates a top-level
        # Package or Dependency from a Dockerfile.
        test_file = self.get_test_loc('dockerfile/basic/Dockerfile')
        package_data = next(dockerfile.DockerfileHandler.parse(test_file))
        assert dockerfile.DockerfileHandler.assemble(package_data, None, None, None) == []
        assert not package_data.can_assemble

    def test_recognize_dockerfile(self):
        # Force a rebuild of the on-disk pattern index so the newly
        # registered handler is visible to recognition.
        get_cache(force=True)
        test_file = self.get_test_loc('dockerfile/basic/Dockerfile')
        packages = recognize_package_data(test_file)
        assert packages
        assert packages[0].datasource_id == 'dockerfile'
        assert packages[0].type == 'docker'

    def test_end2end_scan_dockerfile_has_package_data_but_no_package(self):
        test_file = self.get_test_loc('dockerfile/basic/Dockerfile')
        expected_file = self.get_test_loc('dockerfile/basic/Dockerfile-end2end-expected.json')
        result_file = self.get_temp_file()
        run_scan_click(['--package', test_file, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)
