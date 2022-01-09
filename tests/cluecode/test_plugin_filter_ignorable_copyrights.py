import os

from commoncode.testcase import FileDrivenTesting

from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

def test_ignorable_copyrights():
    test_dir = test_env.get_test_loc('plugin_filter_ignorable_copyrights/files')
    result_file = test_env.get_temp_file('json')
    args = ['--copyright', '--license', '--filter-ignorable-copyrights', '--strip-root', test_dir, '--json-pp', result_file]
    run_scan_click(args)
    check_json_scan(test_env.get_test_loc('plugin_filter_ignorable_copyrights/ignorable_copyrights.expected.json'), result_file)
