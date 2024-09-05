import os

from commoncode import distro
from commoncode.fileutils import resource_iter
from commoncode.testcase import FileBasedTesting
from commoncode.testcase import check_against_expected_json_file


class TestDistro(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), "data")

    def test_parse_os_release(self):
        test_dir = self.get_test_loc("distro/os-release")

        for test_file in resource_iter(test_dir, with_dirs=False):
            if test_file.endswith("expected.json"):
                continue
            expected = test_file + "-expected.json"
            result = distro.parse_os_release(test_file)
            check_against_expected_json_file(result, expected, regen=False)
