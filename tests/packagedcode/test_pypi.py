#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
from unittest.case import skipIf

import pytest
from commoncode.resource import VirtualCodebase
from commoncode.system import on_windows

from packagedcode import pypi
from packages_test_utils import check_result_equals_expected_json
from packages_test_utils import PackageTester
from scancode_config import REGEN_TEST_FIXTURES
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click


class TestPyPiEndtoEnd(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_package_scan_pypi_end_to_end_full(self):
        test_dir = self.get_test_loc('pypi/source-package/pip-22.0.4/')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('pypi/source-package/pip-22.0.4-pypi-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_scan_pypi_end_to_end_full_with_license(self):
        test_dir = self.get_test_loc('pypi/source-package/pip-22.0.4/')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('pypi/source-package/pip-22.0.4-pypi-package-with-license-expected.json')
        run_scan_click(['--package', '--license', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_scan_pypi_setup_py_end_to_end(self):
        test_dir = self.get_test_loc('pypi/source-package/pip-22.0.4/setup.py')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('pypi/source-package/pip-22.0.4-pypi-package-setup-expected.json', must_exist=False)
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_scan_pypi_end_to_end_skip_site_packages(self):
        test_dir = self.get_test_loc('pypi/site-packages/codebase')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('pypi/site-packages/site-packages-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_scan_pypi_end_to_end_can_handle_solo_setup_py(self):
        test_dir = self.get_test_loc('pypi/solo-setup/setup.py')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('pypi/solo-setup/expected.json')
        run_scan_click(['--package', '--processes', '-1', test_dir, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_detect_version_attribute_setup_py(self):
        test_loc = self.get_test_loc('pypi/source-package/pip-22.0.4/setup.py')
        result = pypi.detect_version_attribute(test_loc)
        assert result == '22.0.4'

    def test_package_scan_pypi_end_to_end_extracted_wheel(self):
        test_dir = self.get_test_loc('pypi/unpacked_wheel/daglib_wheel_extracted/')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('pypi/unpacked_wheel/daglib_wheel_extracted-expected.json')
        run_scan_click(['--package', '--processes', '-1', test_dir, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)


class TestPyPiDevelopEggInfoPkgInfo(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_python_pkg_info_is_package_data_file(self):
        test_file = self.get_test_loc('pypi/develop/scancode_toolkit.egg-info/PKG-INFO')
        assert pypi.PythonEditableInstallationPkgInfoFile.is_datafile(test_file)

    def test_develop_with_parse_metadata(self):
        test_file = self.get_test_loc('pypi/develop/scancode_toolkit.egg-info/PKG-INFO')
        package = pypi.PythonEditableInstallationPkgInfoFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/develop/scancode_toolkit.egg-info-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_develop_with_parse(self):
        test_file = self.get_test_loc('pypi/develop/scancode_toolkit.egg-info/PKG-INFO')
        package = pypi.PythonEditableInstallationPkgInfoFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/develop/scancode_toolkit.egg-info-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)


class TestPyPiPkgInfoAndMetadata(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_sdist_pkg_infometadata_format_v10(self):
        test_file = self.get_test_loc('pypi/metadata/v10/PKG-INFO')
        package = pypi.PythonSdistPkgInfoFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/metadata/v10/PKG-INFO-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_sdist_pkg_infometadata_format_v11(self):
        test_file = self.get_test_loc('pypi/metadata/v11/PKG-INFO')
        package = pypi.PythonSdistPkgInfoFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/metadata/v11/PKG-INFO-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_sdist_pkg_infometadata_format_v12(self):
        test_file = self.get_test_loc('pypi/metadata/v12/PKG-INFO')
        package = pypi.PythonSdistPkgInfoFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/metadata/v12/PKG-INFO-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_sdist_pkg_infometadata_format_v20(self):
        test_file = self.get_test_loc('pypi/metadata/v20/PKG-INFO')
        package = pypi.PythonSdistPkgInfoFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/metadata/v20/PKG-INFO-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_sdist_pkg_infometadata_format_v21(self):
        test_file = self.get_test_loc('pypi/metadata/v21/PKG-INFO')
        package = pypi.PythonSdistPkgInfoFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/metadata/v21/PKG-INFO-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_sdist_pkg_info_basic(self):
        test_file = self.get_test_loc('pypi/metadata/PKG-INFO')
        package = pypi.PythonSdistPkgInfoFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/metadata/PKG-INFO-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_python_metadata_is_package_data_file(self):
        test_file = self.get_test_loc('pypi/dist-info-metadata/scan/.dist-info/METADATA')
        assert pypi.PythonInstalledWheelMetadataFile.is_datafile(test_file)

    def test_parse_metadata_basic(self):
        test_file = self.get_test_loc('pypi/dist-info-metadata/scan/.dist-info/METADATA')
        package = pypi.PythonInstalledWheelMetadataFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/dist-info-metadata/METADATA-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)


class TestPypiWheelAndEggArchive(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_python_bdist_whl_is_package_data_file(self):
        test_file = self.get_test_loc('pypi/archive/atomicwrites-1.2.1-py2.py3-none-any.whl')
        assert pypi.PypiWheelHandler.is_datafile(test_file)

    def test_python_bdist_egg_is_package_data_file(self):
        test_file = self.get_test_loc('pypi/archive/commoncode-21.5.12-py3.9.egg')
        assert pypi.PypiEggHandler.is_datafile(test_file)

    def test_parse_archive_with_wheelfile(self):
        test_file = self.get_test_loc('pypi/archive/atomicwrites-1.2.1-py2.py3-none-any.whl')
        package = pypi.PypiWheelHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/archive/atomicwrites-1.2.1-py2.py3-none-any.whl-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_with_wheelfile(self):
        test_file = self.get_test_loc('pypi/archive/atomicwrites-1.2.1-py2.py3-none-any.whl')
        package = pypi.PypiWheelHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/archive/atomicwrites-1.2.1-py2.py3-none-any.whl-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_with_eggfile(self):
        test_file = self.get_test_loc('pypi/archive/commoncode-21.5.12-py3.9.egg')
        package = pypi.PypiEggHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/archive/commoncode-21.5.12-py3.9.egg-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)


class TestPypiInstalledWheel(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_with_unpacked_wheel_meta_v20_1(self):
        test_file = self.get_test_loc('pypi/unpacked_wheel/metadata-2.0/Jinja2-2.10.dist-info/METADATA')
        package = pypi.PythonInstalledWheelMetadataFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_wheel/metadata-2.0/Jinja2-2.10.dist-info-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_with_unpacked_wheel_meta_v20_2(self):
        test_file = self.get_test_loc('pypi/unpacked_wheel/metadata-2.0/python_mimeparse-1.6.0.dist-info/METADATA')
        package = pypi.PythonInstalledWheelMetadataFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_wheel/metadata-2.0/python_mimeparse-1.6.0.dist-info-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_with_unpacked_wheel_meta_v20_3(self):
        test_file = self.get_test_loc('pypi/unpacked_wheel/metadata-2.0/toml-0.10.1.dist-info/METADATA')
        package = pypi.PythonInstalledWheelMetadataFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_wheel/metadata-2.0/toml-0.10.1.dist-info-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_with_unpacked_wheel_meta_v20_4(self):
        test_file = self.get_test_loc('pypi/unpacked_wheel/metadata-2.0/urllib3-1.26.4.dist-info/METADATA')
        package = pypi.PythonInstalledWheelMetadataFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_wheel/metadata-2.0/urllib3-1.26.4.dist-info-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_with_unpacked_wheel_meta_v21_1(self):
        test_file = self.get_test_loc('pypi/unpacked_wheel/metadata-2.1/haruka_bot-1.2.3.dist-info/METADATA')
        package = pypi.PythonInstalledWheelMetadataFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_wheel/metadata-2.1/haruka_bot-1.2.3.dist-info-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_with_unpacked_wheel_meta_v21_2(self):
        test_file = self.get_test_loc('pypi/unpacked_wheel/metadata-2.1/pip-20.2.2.dist-info/METADATA')
        package = pypi.PythonInstalledWheelMetadataFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_wheel/metadata-2.1/pip-20.2.2.dist-info-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_with_unpacked_wheel_meta_v21_3(self):
        test_file = self.get_test_loc('pypi/unpacked_wheel/metadata-2.1/plugincode-21.1.21.dist-info/METADATA')
        package = pypi.PythonInstalledWheelMetadataFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_wheel/metadata-2.1/plugincode-21.1.21.dist-info-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_with_unpacked_wheel_meta_v21__with_sources(self):
        test_file = self.get_test_loc('pypi/unpacked_wheel/metadata-2.1/with_sources/anonapi-0.0.19.dist-info/METADATA')
        package = pypi.PythonInstalledWheelMetadataFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_wheel/metadata-2.1/with_sources/anonapi-0.0.19.dist-info-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)


class TestPypiUnpackedSdist(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_metadata_unpacked_sdist_metadata_v10(self):
        test_file = self.get_test_loc('pypi/unpacked_sdist/metadata-1.0/PyJPString-0.0.3/PKG-INFO')
        package = pypi.PythonSdistPkgInfoFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_sdist/metadata-1.0/PyJPString-0.0.3-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_metadata_unpacked_sdist_metadata_v10_subdir(self):
        test_file = self.get_test_loc('pypi/unpacked_sdist/metadata-1.0/PyJPString-0.0.3/PyJPString.egg-info/PKG-INFO')
        package = pypi.PythonEditableInstallationPkgInfoFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_sdist/metadata-1.0/PyJPString-0.0.3-subdir-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_metadata_unpacked_sdist_metadata_v11_1(self):
        test_file = self.get_test_loc('pypi/unpacked_sdist/metadata-1.1/python-mimeparse-1.6.0/PKG-INFO')
        package = pypi.PythonSdistPkgInfoFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_sdist/metadata-1.1/python-mimeparse-1.6.0-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_metadata_unpacked_sdist_metadata_v11_2(self):
        test_file = self.get_test_loc('pypi/unpacked_sdist/metadata-1.1/pyup-django-0.4.0/PKG-INFO')
        package = pypi.PythonSdistPkgInfoFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_sdist/metadata-1.1/pyup-django-0.4.0-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_metadata_unpacked_sdist_metadata_v12(self):
        test_file = self.get_test_loc('pypi/unpacked_sdist/metadata-1.2/anonapi-0.0.19/PKG-INFO')
        package = pypi.PythonSdistPkgInfoFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_sdist/metadata-1.2/anonapi-0.0.19-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_metadata_unpacked_sdist_metadata_v21(self):
        test_file = self.get_test_loc('pypi/unpacked_sdist/metadata-2.1/commoncode-21.5.12/PKG-INFO')
        package = pypi.PythonSdistPkgInfoFile.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_sdist/metadata-2.1/commoncode-21.5.12-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_can_parse_solo_metadata_from_command_line(self):
        test_file = self.get_test_loc('pypi/solo-metadata/PKG-INFO')
        expected_file = self.get_test_loc('pypi/solo-metadata/expected.json', must_exist=False)
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_parse_metadata_prefer_pkg_info_from_egg_info_from_command_line(self):
        test_file = self.get_test_loc('pypi/unpacked_sdist/prefer-egg-info-pkg-info/celery')
        expected_file = self.get_test_loc('pypi/unpacked_sdist/prefer-egg-info-pkg-info/celery-expected.json', must_exist=False)
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

        # Really check to see that we are only using the PKG-INFO from
        # `celery/celery.egg-info/PKG-INFO`
        vc = VirtualCodebase(location=result_file)
        for dep in vc.attributes.dependencies:
            self.assertEqual(dep['datafile_path'], 'celery/celery.egg-info/PKG-INFO')
        for pkg in vc.attributes.packages:
            for path in pkg['datafile_paths']:
                self.assertEqual(path, 'celery/celery.egg-info/PKG-INFO')


class TestPipRequirementsFileHandler(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_python_requirements_is_package_data_file(self):
        test_file = self.get_test_loc('pypi/requirements_txt/basic/requirements.txt')
        assert pypi.PipRequirementsFileHandler.is_datafile(test_file)

    def test_get_requirements_txt_dependencies(self):
        test_file = self.get_test_loc('pypi/requirements_txt/simple/requirements.txt')
        dependencies, extra_data = pypi.get_requirements_txt_dependencies(location=test_file)
        dependencies = [d.to_dict() for d in dependencies]
        results = dependencies, extra_data
        expected_loc = self.get_test_loc('pypi/requirements_txt/simple/output.expected.json')
        check_result_equals_expected_json(results, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_dependency_file_basic(self):
        test_file = self.get_test_loc('pypi/requirements_txt/basic/requirements.txt')
        package = pypi.PipRequirementsFileHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/basic/output.expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_dependency_file_pinned(self):
        test_file = self.get_test_loc('pypi/requirements_txt/pinned/sample-requirements.txt')
        package = pypi.PipRequirementsFileHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/pinned/output.expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_dependency_file_dev(self):
        test_file = self.get_test_loc('pypi/requirements_txt/dev/requirements-dev.txt')
        package = pypi.PipRequirementsFileHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/dev/output.expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_dependency_file_requirements_in(self):
        test_file = self.get_test_loc('pypi/requirements_txt/requirements_in/requirements.in')
        package = pypi.PipRequirementsFileHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/requirements_in/output.expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_dependency_file_eol_comment(self):
        test_file = self.get_test_loc('pypi/requirements_txt/eol_comment/requirements.txt')
        package = pypi.PipRequirementsFileHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/eol_comment/output.expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_dependency_file_complex(self):
        test_file = self.get_test_loc('pypi/requirements_txt/complex/requirements.txt')
        package = pypi.PipRequirementsFileHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/complex/output.expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_dependency_file_editable(self):
        test_file = self.get_test_loc('pypi/requirements_txt/editable/requirements.txt')
        package = pypi.PipRequirementsFileHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/editable/output.expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_dependency_file_double_extras(self):
        test_file = self.get_test_loc('pypi/requirements_txt/double_extras/requirements.txt')
        package = pypi.PipRequirementsFileHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/double_extras/output.expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_dependency_file_repeated(self):
        test_file = self.get_test_loc('pypi/requirements_txt/repeated/requirements.txt')
        package = pypi.PipRequirementsFileHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/repeated/output.expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_dependency_file_vcs_eggs(self):
        test_file = self.get_test_loc('pypi/requirements_txt/vcs_eggs/requirements.txt')
        package = pypi.PipRequirementsFileHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/vcs_eggs/output.expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_dependency_file_local_paths_and_files(self):
        test_file = self.get_test_loc('pypi/requirements_txt/local_paths_and_files/requirements.txt')
        package = pypi.PipRequirementsFileHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/local_paths_and_files/output.expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_dependency_file_urls_wth_checksums(self):
        test_file = self.get_test_loc('pypi/requirements_txt/urls_wth_checksums/requirements.txt')
        package = pypi.PipRequirementsFileHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/urls_wth_checksums/output.expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_dependency_file_mixed(self):
        test_file = self.get_test_loc('pypi/requirements_txt/mixed/requirements.txt')
        package = pypi.PipRequirementsFileHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/mixed/output.expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_dependency_file_comments_and_empties(self):
        test_file = self.get_test_loc('pypi/requirements_txt/comments_and_empties/requirements.txt')
        package = pypi.PipRequirementsFileHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/comments_and_empties/output.expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_dependency_file_many_specs(self):
        test_file = self.get_test_loc('pypi/requirements_txt/many_specs/requirements.txt')
        package = pypi.PipRequirementsFileHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/many_specs/output.expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_dependency_file_vcs_editable(self):
        test_file = self.get_test_loc('pypi/requirements_txt/vcs_editable/requirements.txt')
        package = pypi.PipRequirementsFileHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/vcs_editable/output.expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_dependency_file_vcs_extras_require(self):
        test_file = self.get_test_loc('pypi/requirements_txt/vcs_extras_require/requirements.txt')
        package = pypi.PipRequirementsFileHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/vcs_extras_require/output.expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_dependency_file_vcs_git(self):
        test_file = self.get_test_loc('pypi/requirements_txt/vcs-git/requirements.txt')
        package = pypi.PipRequirementsFileHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/vcs-git/output.expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_dependency_file_with_invalid_does_not_fail(self):
        test_file = self.get_test_loc('pypi/requirements_txt/invalid_spec/requirements.txt')
        package = pypi.PipRequirementsFileHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/invalid_spec/output.expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_PipRequirementsFileHandler_is_datafile(self):
        self.assertEqual(
            pypi.PipRequirementsFileHandler.is_datafile('dev-requirements.txt', _bare_filename=True),
            True
        )
        self.assertEqual(
            pypi.PipRequirementsFileHandler.is_datafile('requirements.txt', _bare_filename=True),
            True
        )
        self.assertEqual(
            pypi.PipRequirementsFileHandler.is_datafile('requirement.txt', _bare_filename=True),
            True
        )
        self.assertEqual(
            pypi.PipRequirementsFileHandler.is_datafile('requirements.in', _bare_filename=True),
            True
        )
        self.assertEqual(
            pypi.PipRequirementsFileHandler.is_datafile('requirements.pip', _bare_filename=True),
            True
        )
        self.assertEqual(
            pypi.PipRequirementsFileHandler.is_datafile('requirements-dev.txt', _bare_filename=True),
            True
        )
        self.assertEqual(
            pypi.PipRequirementsFileHandler.is_datafile('some-requirements-dev.txt', _bare_filename=True),
            True
        )
        self.assertEqual(
            pypi.PipRequirementsFileHandler.is_datafile('requires.txt', _bare_filename=True),
            True
        )
        self.assertEqual(
            pypi.PipRequirementsFileHandler.is_datafile('requirements/base.txt', _bare_filename=True),
            True
        )
        self.assertEqual(
            pypi.PipRequirementsFileHandler.is_datafile('reqs.txt', _bare_filename=True),
            True
        )


class TestPyPiPipfile(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_pipfile_lock_sample1(self):
        test_file = self.get_test_loc('pypi/pipfile.lock/sample1/Pipfile.lock')
        package = pypi.PipfileLockHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/pipfile.lock/sample1/Pipfile.lock-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_pipfile_lock_sample2(self):
        test_file = self.get_test_loc('pypi/pipfile.lock/sample2/Pipfile.lock')
        package = pypi.PipfileLockHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/pipfile.lock/sample2/Pipfile.lock-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_pipfile_lock_sample3(self):
        test_file = self.get_test_loc('pypi/pipfile.lock/sample3/Pipfile.lock')
        package = pypi.PipfileLockHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/pipfile.lock/sample3/Pipfile.lock-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_pipfile_lock_sample4(self):
        test_file = self.get_test_loc('pypi/pipfile.lock/sample4/Pipfile.lock')
        package = pypi.PipfileLockHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/pipfile.lock/sample4/Pipfile.lock-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_pipfile_lock_sample5(self):
        test_file = self.get_test_loc('pypi/pipfile.lock/sample5/Pipfile.lock')
        package = pypi.PipfileLockHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/pipfile.lock/sample5/Pipfile.lock-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_file_type(self):
        filename = pypi.get_dparse2_supported_file_name('Pipfile.lock')
        assert filename == 'Pipfile.lock'


class TestIsPipRequirementsFileHandler(object):

    requirement_location = [
        'requirements.txt',
        'requirement.txt',
        'sample-requirements.txt',
        'requirements-test.txt',
        'sample-requirements-test.txt',
        'requirements-dev.txt',
        'sample-requirements-dev.txt',
        'requirements.in',
        'requirement.in',
        'sample-requirements.in',
        'requirements-test.in',
        'sample-requirements-test.in',
        'requirements-dev.in',
        'sample-requirements-dev.in',
        'requirements/dev.pip',
        'requirements/test.txt',
        'requirements/dev.in',
    ]

    @pytest.mark.parametrize('location', requirement_location)
    def test_is_requirements_file(self, location, monkeypatch):
        # monkey patch filetype.is_file to pretend this is a real file
        from commoncode import filetype
        monkeypatch.setattr(filetype, "is_file", lambda f: True)
        assert pypi.PipRequirementsFileHandler.is_datafile(location)

    def test_is_not_requirements_file(self, monkeypatch):
        # monkey patch filetype.is_file to pretend this is a real file
        from commoncode import filetype
        monkeypatch.setattr(filetype, "is_file", lambda f: True)

        assert not pypi.PipRequirementsFileHandler.is_datafile('req.txt')
        assert not pypi.PipRequirementsFileHandler.is_datafile('requiremenst.py')


class TestPyPiSetupPyNotWin(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    @skipIf(on_windows, 'Somehow this fails on Windows')
    def test_parse_setup_py_arpy(self):
        test_file = self.get_test_loc('pypi/setup.py-not-win/arpy_setup.py')
        package = pypi.PythonSetupPyHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py-not-win/arpy_setup.py-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)


class TestPyPiSetupCfg(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_setup_cfg(self):
        test_file = self.get_test_loc('pypi/setup.cfg/wheel-0.34.2/setup.cfg')
        package = pypi.SetupCfgHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/setup.cfg/wheel-0.34.2/setup.cfg-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)


class TestPyPiSetupPyNames(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_setup_py_with_name(self):
        test_file = self.get_test_loc('pypi/setup.py-name-or-no-name/with_name-setup.py')
        package = pypi.PythonSetupPyHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py-name-or-no-name/with_name-setup.py.expected.json', must_exist=False)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_setup_py_without_name(self):
        test_file = self.get_test_loc('pypi/setup.py-name-or-no-name/without_name-setup.py')
        package = pypi.PythonSetupPyHandler.parse(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py-name-or-no-name/without_name-setup.py.expected.json', must_exist=False)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_get_setup_py_args_with_name(self):
        test_file = self.get_test_loc('pypi/setup.py-name-or-no-name/with_name-setup.py')
        kwargs = pypi.get_setup_py_args(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py-name-or-no-name/with_name-setup.py.args.expected.json', must_exist=False)
        check_result_equals_expected_json(kwargs, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_get_setup_py_args_without_name(self):
        test_file = self.get_test_loc('pypi/setup.py-name-or-no-name/without_name-setup.py')
        kwargs = pypi.get_setup_py_args(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py-name-or-no-name/without_name-setup.py.args.expected.json', must_exist=False)
        check_result_equals_expected_json(kwargs, expected_loc, regen=REGEN_TEST_FIXTURES)


def get_setup_py_test_files(test_dir):
    """
    Yield setup.py file from a `test_dir` test data directory.
    """
    print(test_dir)
    for top, _, files in os.walk(test_dir):
        for tfile in files:
            if tfile.endswith('setup.py'):
                yield os.path.join(top, tfile)


def check_setup_py_parsing(test_loc):
    expected_loc1 = f'{test_loc}-expected-args.json'
    parsed_kwargs = pypi.get_setup_py_args(test_loc, include_not_parsable=False)
    check_result_equals_expected_json(
        result=parsed_kwargs,
        expected_loc=expected_loc1,
        regen=REGEN_TEST_FIXTURES,
    )

    expected_loc2 = f'{test_loc}-expected.json'
    packages_data = pypi.PythonSetupPyHandler.parse(test_loc)
    test_envt.check_packages_data(
        packages_data=packages_data,
        expected_loc=expected_loc2,
        regen=REGEN_TEST_FIXTURES,
        must_exist=False,
    )


test_envt = PackageTester()


@pytest.mark.parametrize(
    'test_loc',
    get_setup_py_test_files(os.path.abspath(os.path.join(test_envt.test_data_dir, 'pypi', 'setup.py-versions'))),
)
def test_parse_setup_py_with_computed_versions(test_loc):
    check_setup_py_parsing(test_loc)


@pytest.mark.parametrize(
    'test_loc',
    get_setup_py_test_files(os.path.abspath(os.path.join(test_envt.test_data_dir, 'pypi', 'setup.py')))
)
def test_parse_setup_py(test_loc):
    check_setup_py_parsing(test_loc)


@pytest.mark.parametrize(
    'test_loc',
    get_setup_py_test_files(os.path.abspath(os.path.join(test_envt.test_data_dir, 'pypi', 'more_setup.py'))),
)
def test_parse_more_setup_py(test_loc):
    check_setup_py_parsing(test_loc)

