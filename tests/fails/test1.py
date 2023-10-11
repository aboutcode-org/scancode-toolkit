import os

from commoncode.testcase import FileBasedTesting

from licensedcode import index
from licensedcode.index import LicenseIndex
from licensedcode.match_unknown import match_unknowns
from licensedcode.models import get_all_spdx_key_tokens, load_licenses, get_license_tokens, get_rules
from licensedcode.query import build_query
from licensedcode_test_utils import mini_legalese


def MiniLicenseIndex(*args, **kwargs):
    return index.LicenseIndex(*args, _legalese=mini_legalese, **kwargs)


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestFailed(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_stable_firmwar_realtek_copyright_detailed_expected_yml(self):
        rule_dir = self.get_test_loc('rules/')
        license_dir = self.get_test_loc('licenses/')
        licenses_db = load_licenses(license_dir)
        rules = list(get_rules(licenses_db=licenses_db, rules_data_dir=rule_dir))
        spdx_tokens = set(get_all_spdx_key_tokens(licenses_db))
        license_tokens = set(get_license_tokens())
        idx = LicenseIndex(
            rules=rules,
            _spdx_tokens=spdx_tokens,
            _license_tokens=license_tokens,
        )

        query_loc = self.get_test_loc('debian/stable_firmware-realtek.copyright')
        qry_string = open(query_loc, 'r').read()
        m = idx.match(query_string=qry_string)
        print(m)
