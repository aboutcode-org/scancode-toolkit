import os
from packages_test_utils import PackageTester
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES

class TestPackageSummary(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    def test_if_package_summary_plugin_working(self):
        test_dir = self.get_test_loc('package_summary/plugin_package_summary')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('package_summary/plugin_package_summary-expected.json')
        
        run_scan_click(['--package', '--classify', '--package-summary', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)
    #     test_dir = self.get_test_loc('package_summary/change-case-change-case-5.4.4.zip-extract') 
    #     result_file = self.get_temp_file('json')
    #     expected_file = self.get_test_loc('package_summary/expected.json')

    #     run_scan_click(['--package','--license','--copyright', '--strip-root', '--processes', '-1', '--package-summary', '--classify', '--json-pp', result_file, test_dir])
    #     check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)
    
    # def test_py_whl_ecosystem_with_package_summary(self):
    #     test_dir = self.get_test_loc('package_summary/python.whl-extract') 
    #     result_file = self.get_temp_file('json')
    #     expected_file = self.get_test_loc('package_summary/python-whl-expected.json')

    #     run_scan_click(['--package','--license','--copyright', '--strip-root', '--processes', '-1', '--package-summary', '--summary' , '--classify', '--json-pp', result_file, test_dir])
    #     check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)
    
    # # Package Attribute tests
    # def test_package_summary__does_summarize_npm_copyright(self): 
    #     test_dir = self.get_test_loc('package_summary/npm_copyright') 
    #     result_file = self.get_temp_file('json')
    #     expected_file = self.get_test_loc('package_summary/npm_copyrightexpected.json')

    #     run_scan_click(['--package','--license','--copyright', '--strip-root', '--processes', '-1', '--package-summary', '--classify', '--json-pp', result_file, test_dir])
    #     check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)
    