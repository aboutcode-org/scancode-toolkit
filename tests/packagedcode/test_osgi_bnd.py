import io
import json
import os

from commoncode.testcase import FileBasedTesting
from packagedcode.maven import OsgiBndHandler
from scancode_config import REGEN_TEST_FIXTURES


class TestOsgiBnd(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_parse_bnd(self, test_bnd, regen=REGEN_TEST_FIXTURES):
        test_loc = self.get_test_loc(test_bnd)
        expected_loc = test_loc + '.json'
        packages = list(OsgiBndHandler.parse(test_loc))
        assert len(packages) == 1
        package = packages[0].to_dict()

        if regen:
            with open(expected_loc, 'w') as ex:
                json.dump(package, ex, indent=2)

        with io.open(expected_loc, encoding='utf-8') as ex:
            expected = json.load(ex)

        assert json.dumps(package) == json.dumps(expected)

    def test_parse_bnd_basic(self):
        self.check_parse_bnd('osgi/basic.bnd', regen=True)
