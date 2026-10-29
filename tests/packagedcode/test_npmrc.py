import os

from packagedcode import npm
from packages_test_utils import PackageTester
from scancode_config import REGEN_TEST_FIXTURES


class TestNpmrc(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_basic_npmrc(self):
        test_file = self.get_test_loc('npm/basic/.npmrc')
        expected_loc = self.get_test_loc('npm/basic/.npmrc.expected')
        packages_data = npm.NpmrcHandler.parse(test_file)
        self.check_packages_data(packages_data, expected_loc, regen=REGEN_TEST_FIXTURES)
