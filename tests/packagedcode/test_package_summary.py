import os

from packages_test_utils import PackageTester

from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


class TestPackageSummary(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), "data")

    def test_if_package_summary_plugin_working(self):
        test_dir = self.get_test_loc("package_summary/plugin_package_summary")
        result_file = self.get_temp_file("json")
        expected_file = self.get_test_loc(
            "package_summary/plugin_package_summary-expected.json"
        )

        run_scan_click(
            [
                "--package",
                "--classify",
                "--package-summary",
                test_dir,
                "--json",
                result_file,
            ]
        )
        check_json_scan(
            expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES
        )

    def test_package_summary_for_python_whl(self):
        test_dir = self.get_test_loc("package_summary/python_whl")
        result_file = self.get_temp_file("json")
        expected_file = self.get_test_loc("package_summary/python_whl-expected.json")

        run_scan_click(
            [
                "--package",
                "--license",
                "--copyright",
                "--strip-root",
                "--processes",
                "-1",
                "--package-summary",
                "--summary",
                "--classify",
                "--json-pp",
                result_file,
                test_dir,
            ]
        )
        check_json_scan(
            expected_file,
            result_file,
            remove_uuid=True,
            remove_file_date=True,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_package_summary_for_npm(self):
        test_dir = self.get_test_loc("package_summary/npm")
        result_file = self.get_temp_file("json")
        expected_file = self.get_test_loc("package_summary/npm-expected.json")

        run_scan_click(
            [
                "--package",
                "--license",
                "--copyright",
                "--strip-root",
                "--processes",
                "-1",
                "--package-summary",
                "--summary",
                "--classify",
                "--json-pp",
                result_file,
                test_dir,
            ]
        )
        check_json_scan(
            expected_file,
            result_file,
            remove_uuid=True,
            remove_file_date=True,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_package_summary_for_rubygems(self):
        test_dir = self.get_test_loc("package_summary/rubygems")
        result_file = self.get_temp_file("json")
        expected_file = self.get_test_loc("package_summary/rubygems-expected.json")

        run_scan_click(
            [
                "--package",
                "--license",
                "--copyright",
                "--strip-root",
                "--processes",
                "-1",
                "--package-summary",
                "--summary",
                "--classify",
                "--json-pp",
                result_file,
                test_dir,
            ]
        )
        check_json_scan(
            expected_file,
            result_file,
            remove_uuid=True,
            remove_file_date=True,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_package_summary_for_rust(self):
        test_dir = self.get_test_loc("package_summary/rust")
        result_file = self.get_temp_file("json")
        expected_file = self.get_test_loc("package_summary/rust-expected.json")

        run_scan_click(
            [
                "--package",
                "--license",
                "--copyright",
                "--strip-root",
                "--processes",
                "-1",
                "--package-summary",
                "--summary",
                "--classify",
                "--json-pp",
                result_file,
                test_dir,
            ]
        )
        check_json_scan(
            expected_file,
            result_file,
            remove_uuid=True,
            remove_file_date=True,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_package_summary_for_copyright(self):
        test_dir = self.get_test_loc("package_summary/package_attributes/copyright")
        result_file = self.get_temp_file("json")
        expected_file = self.get_test_loc(
            "package_summary/package_attributes/copyright-expected.json"
        )

        run_scan_click(
            [
                "--package",
                "--license",
                "--copyright",
                "--strip-root",
                "--processes",
                "-1",
                "--package-summary",
                "--classify",
                "--json-pp",
                result_file,
                test_dir,
            ]
        )
        check_json_scan(
            expected_file,
            result_file,
            remove_uuid=True,
            remove_file_date=True,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_package_to_dict_license_clarity_score(self):
        from packagedcode.models import Package

        pkg = Package(type="npm", name="test-pkg")
        pkg.license_clarity_score = {"score": 80}

        # By default (package_summary=False), license_clarity_score is excluded
        data_default = pkg.to_dict()
        assert "license_clarity_score" not in data_default

        data_false = pkg.to_dict(package_summary=False)
        assert "license_clarity_score" not in data_false

        # When package_summary=True, license_clarity_score is included
        data_true = pkg.to_dict(package_summary=True)
        assert "license_clarity_score" in data_true
        assert data_true["license_clarity_score"] == {"score": 80}

    def test_compute_package_summary_attributes(self):
        from unittest.mock import Mock

        from packagedcode.plugin_package import compute_package_summary_attributes

        key_res = Mock()
        key_res.is_key_file = True
        key_res.detected_license_expression = "mit"
        key_res.detected_license_expression_spdx = "MIT"
        key_res.copyrights = [{"copyright": "Copyright (c) 2024 Test Corp"}]
        key_res.holders = [{"holder": "Test Corp"}]
        key_res.notice_text = [{"notice_text": "All rights reserved"}]

        non_key_res = Mock()
        non_key_res.is_key_file = False
        non_key_res.detected_license_expression = "apache-2.0"
        non_key_res.detected_license_expression_spdx = "Apache-2.0"
        non_key_res.copyrights = []
        non_key_res.holders = []
        non_key_res.notice_text = []

        attrs = compute_package_summary_attributes([key_res, non_key_res])
        assert attrs["copyright"] == "Copyright (c) 2024 Test Corp"
        assert attrs["holder"] == "Test Corp"
        assert attrs["notice_text"] == "All rights reserved"
        assert attrs["other_license_expression"] == "apache-2.0"
        assert attrs["other_license_expression_spdx"] == "Apache-2.0"
