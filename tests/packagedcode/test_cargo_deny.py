import os

from packages_test_utils import PackageTester
from packagedcode import cargo


class TestCargoDeny(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_cargo_deny_is_datafile(self):
        test_file = self.get_test_loc('cargo/deny_toml/deny.toml')
        assert cargo.CargoDenyHandler.is_datafile(test_file)

    def test_parse_simple_deny_toml(self):
        test_file = self.get_test_loc('cargo/deny_toml/simple-deny.toml')
        packages = list(cargo.CargoDenyHandler.parse(test_file))
        assert len(packages) == 1
        package = packages[0]

        extra = package.extra_data
        assert 'MIT' in extra['allowed_licenses']
        assert 'Apache-2.0' in extra['allowed_licenses']
        assert 'GPL-2.0' in extra['denied_licenses']

        clarifications = extra['license_clarifications']
        ring_clarity = next((c for c in clarifications if c['name'] == 'ring'), None)
        assert ring_clarity is not None
        assert ring_clarity['expression'] == 'MIT AND ISC AND OpenSSL'

        exceptions = extra['license_exceptions']
        special_exc = next((e for e in exceptions if e['name'] == 'special-crate'), None)
        assert special_exc is not None
        assert special_exc['allow'] == ['LicenseRef-special']

        assert 'RUSTSEC-2020-0001' in extra['ignored_advisories']

        deps = package.dependencies
        openssl_dep = next((d for d in deps if d.purl == 'pkg:cargo/openssl'), None)
        assert openssl_dep is not None
        assert openssl_dep.scope == 'deny'
        assert openssl_dep.extracted_requirement == '*'

    def test_parse_real_deny_toml(self):
        test_file = self.get_test_loc('cargo/deny_toml/egui-deny.toml')
        packages = list(cargo.CargoDenyHandler.parse(test_file))
        assert len(packages) == 1
        package = packages[0]

        extra = package.extra_data
        assert 'allowed_licenses' in extra
        assert 'denied_licenses' in extra

    def test_parse_empty_deny_toml(self):
        test_file = self.get_test_loc('cargo/deny_toml/empty-deny.toml')
        packages = list(cargo.CargoDenyHandler.parse(test_file))
        assert len(packages) == 1
        package = packages[0]

        extra = package.extra_data
        assert extra['allowed_licenses'] == []
        assert extra['denied_licenses'] == []
        assert extra['license_clarifications'] == []
        assert extra['license_exceptions'] == []
        assert extra['ignored_advisories'] == []
        assert package.dependencies == []

    def test_parse_missing_sections(self):
        test_file = self.get_temp_file('missing-sections.toml')
        with open(test_file, 'w') as f:
            f.write('[licenses]\nallow = ["MIT"]\n')

        packages = list(cargo.CargoDenyHandler.parse(test_file))
        assert len(packages) == 1
        package = packages[0]

        extra = package.extra_data
        assert extra['allowed_licenses'] == ['MIT']
        assert extra['denied_licenses'] == []
        assert extra['license_clarifications'] == []
        assert extra['license_exceptions'] == []
        assert extra['ignored_advisories'] == []
        assert package.dependencies == []

    def test_parse_invalid_toml_returns_no_package_data(self):
        test_file = self.get_temp_file('invalid-deny.toml')
        with open(test_file, 'w') as f:
            f.write('not toml [')

        packages = list(cargo.CargoDenyHandler.parse(test_file))
        assert packages == []
