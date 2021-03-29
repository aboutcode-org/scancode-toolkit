#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json
import os
from unittest.case import expectedFailure
from unittest.case import skipIf

import pytest

from commoncode.system import on_windows
from packagedcode import pypi

from packages_test_utils import check_result_equals_expected_json
from packages_test_utils import PackageTester


class TestPyPiDevelop(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_develop_with_parse_metadata(self):
        test_file = self.get_test_loc('pypi/develop/scancode_toolkit.egg-info/PKG-INFO')
        package = pypi.parse_metadata(test_file)
        expected_loc = self.get_test_loc('pypi/develop/scancode_toolkit.egg-info-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_develop_with_parse(self):
        test_file = self.get_test_loc('pypi/develop/scancode_toolkit.egg-info/PKG-INFO')
        package = pypi.parse(test_file)
        expected_loc = self.get_test_loc('pypi/develop/scancode_toolkit.egg-info-expected.json')
        self.check_package(package, expected_loc, regen=False)


class TestPyPiMetadata(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_metadata_format_v10(self):
        test_file = self.get_test_loc('pypi/metadata/v10/PKG-INFO')
        package = pypi.parse_metadata(test_file)
        expected_loc = self.get_test_loc('pypi/metadata/v10/PKG-INFO-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_metadata_format_v11(self):
        test_file = self.get_test_loc('pypi/metadata/v11/PKG-INFO')
        package = pypi.parse_metadata(test_file)
        expected_loc = self.get_test_loc('pypi/metadata/v11/PKG-INFO-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_metadata_format_v12(self):
        test_file = self.get_test_loc('pypi/metadata/v12/PKG-INFO')
        package = pypi.parse_metadata(test_file)
        expected_loc = self.get_test_loc('pypi/metadata/v12/PKG-INFO-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_metadata_format_v20(self):
        test_file = self.get_test_loc('pypi/metadata/v20/PKG-INFO')
        package = pypi.parse_metadata(test_file)
        expected_loc = self.get_test_loc('pypi/metadata/v20/PKG-INFO-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_metadata_format_v21(self):
        test_file = self.get_test_loc('pypi/metadata/v21/PKG-INFO')
        package = pypi.parse_metadata(test_file)
        expected_loc = self.get_test_loc('pypi/metadata/v21/PKG-INFO-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_pkg_dash_info_basic(self):
        test_file = self.get_test_loc('pypi/metadata/PKG-INFO')
        package = pypi.parse_metadata(test_file)
        expected_loc = self.get_test_loc('pypi/metadata/PKG-INFO-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_metadata_basic(self):
        test_file = self.get_test_loc('pypi/metadata/METADATA')
        package = pypi.parse_metadata(test_file)
        expected_loc = self.get_test_loc('pypi/metadata/METADATA-expected.json')
        self.check_package(package, expected_loc, regen=False)


class TestPypiArchive(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_archive_with_wheelfile(self):
        test_file = self.get_test_loc('pypi/archive/atomicwrites-1.2.1-py2.py3-none-any.whl')
        package = pypi.parse_archive(test_file)
        expected_loc = self.get_test_loc('pypi/archive/atomicwrites-1.2.1-py2.py3-none-any.whl-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_with_wheelfile(self):
        test_file = self.get_test_loc('pypi/archive/atomicwrites-1.2.1-py2.py3-none-any.whl')
        package = pypi.parse(test_file)
        expected_loc = self.get_test_loc('pypi/archive/atomicwrites-1.2.1-py2.py3-none-any.whl-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_with_eggfile(self):
        test_file = self.get_test_loc('pypi/archive/commoncode-21.5.12-py3.9.egg')
        package = pypi.parse(test_file)
        expected_loc = self.get_test_loc('pypi/archive/commoncode-21.5.12-py3.9.egg-expected.json')
        self.check_package(package, expected_loc, regen=False)


class TestPypiUnpackedWheel(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_with_unpacked_wheel_meta_v20_1(self):
        test_file = self.get_test_loc('pypi/unpacked_wheel/metadata-2.0/Jinja2-2.10.dist-info/METADATA')
        package = pypi.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_wheel/metadata-2.0/Jinja2-2.10.dist-info-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_with_unpacked_wheel_meta_v20_2(self):
        test_file = self.get_test_loc('pypi/unpacked_wheel/metadata-2.0/python_mimeparse-1.6.0.dist-info/METADATA')
        package = pypi.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_wheel/metadata-2.0/python_mimeparse-1.6.0.dist-info-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_with_unpacked_wheel_meta_v20_3(self):
        test_file = self.get_test_loc('pypi/unpacked_wheel/metadata-2.0/toml-0.10.1.dist-info/METADATA')
        package = pypi.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_wheel/metadata-2.0/toml-0.10.1.dist-info-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_with_unpacked_wheel_meta_v20_4(self):
        test_file = self.get_test_loc('pypi/unpacked_wheel/metadata-2.0/urllib3-1.26.4.dist-info/METADATA')
        package = pypi.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_wheel/metadata-2.0/urllib3-1.26.4.dist-info-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_with_unpacked_wheel_meta_v21_1(self):
        test_file = self.get_test_loc('pypi/unpacked_wheel/metadata-2.1/haruka_bot-1.2.3.dist-info/METADATA')
        package = pypi.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_wheel/metadata-2.1/haruka_bot-1.2.3.dist-info-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_with_unpacked_wheel_meta_v21_2(self):
        test_file = self.get_test_loc('pypi/unpacked_wheel/metadata-2.1/pip-20.2.2.dist-info/METADATA')
        package = pypi.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_wheel/metadata-2.1/pip-20.2.2.dist-info-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_with_unpacked_wheel_meta_v21_3(self):
        test_file = self.get_test_loc('pypi/unpacked_wheel/metadata-2.1/plugincode-21.1.21.dist-info/METADATA')
        package = pypi.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_wheel/metadata-2.1/plugincode-21.1.21.dist-info-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_with_unpacked_wheel_meta_v21__with_sources(self):
        test_file = self.get_test_loc('pypi/unpacked_wheel/metadata-2.1/with_sources/anonapi-0.0.19.dist-info/METADATA')
        package = pypi.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_wheel/metadata-2.1/with_sources/anonapi-0.0.19.dist-info-expected.json')
        self.check_package(package, expected_loc, regen=False)


class TestPypiUnpackedSdist(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_metadata_unpacked_sdist_metadata_v10(self):
        test_file = self.get_test_loc('pypi/unpacked_sdist/metadata-1.0/PyJPString-0.0.3/PKG-INFO')
        package = pypi.parse_metadata(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_sdist/metadata-1.0/PyJPString-0.0.3-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_metadata_unpacked_sdist_metadata_v10_subdir(self):
        test_file = self.get_test_loc('pypi/unpacked_sdist/metadata-1.0/PyJPString-0.0.3/PyJPString.egg-info/PKG-INFO')
        package = pypi.parse_metadata(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_sdist/metadata-1.0/PyJPString-0.0.3-subdir-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_with_name(self):
        test_file = self.get_test_loc('pypi/setup.py/with_name.py')
        packages = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/with_name.py.expected')
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_setup_py_without_name(self):
        test_file = self.get_test_loc('pypi/setup.py/without_name.py')
        try:
            pypi.parse_setup_py(test_file)
        except AttributeError as e:
            assert "'NoneType' object has no attribute 'to_dict'" in str(e)

    def test_parse_metadata_unpacked_sdist_metadata_v11_1(self):
        test_file = self.get_test_loc('pypi/unpacked_sdist/metadata-1.1/python-mimeparse-1.6.0/PKG-INFO')
        package = pypi.parse_metadata(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_sdist/metadata-1.1/python-mimeparse-1.6.0-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_metadata_unpacked_sdist_metadata_v11_2(self):
        test_file = self.get_test_loc('pypi/unpacked_sdist/metadata-1.1/pyup-django-0.4.0/PKG-INFO')
        package = pypi.parse_metadata(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_sdist/metadata-1.1/pyup-django-0.4.0-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_metadata_unpacked_sdist_metadata_v12(self):
        test_file = self.get_test_loc('pypi/unpacked_sdist/metadata-1.2/anonapi-0.0.19/PKG-INFO')
        package = pypi.parse_metadata(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_sdist/metadata-1.2/anonapi-0.0.19-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_metadata_unpacked_sdist_metadata_v21(self):
        test_file = self.get_test_loc('pypi/unpacked_sdist/metadata-2.1/commoncode-21.5.12/PKG-INFO')
        package = pypi.parse_metadata(test_file)
        expected_loc = self.get_test_loc('pypi/unpacked_sdist/metadata-2.1/commoncode-21.5.12-expected.json')
        self.check_package(package, expected_loc, regen=False)


class TestPyPiRequirements(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_with_dparse_requirements(self):
        test_file = self.get_test_loc('pypi/requirements_txt/simple/requirements.txt')
        dependencies = [d.to_dict() for d in pypi.parse_with_dparse(test_file)]
        expected_loc = self.get_test_loc('pypi/requirements_txt/simple/output.expected.json')
        check_result_equals_expected_json(dependencies, expected_loc, regen=False)

    def test_parse_dependency_file_basic(self):
        test_file = self.get_test_loc('pypi/requirements_txt/basic/requirements.txt')
        package = pypi.parse_dependency_file(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/basic/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_dependency_file_pinned(self):
        test_file = self.get_test_loc('pypi/requirements_txt/pinned/sample-requirements.txt')
        package = pypi.parse_dependency_file(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/pinned/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_dependency_file_dev(self):
        test_file = self.get_test_loc('pypi/requirements_txt/dev/requirements-dev.txt')
        package = pypi.parse_dependency_file(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/dev/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_dependency_file_requirements_in(self):
        test_file = self.get_test_loc('pypi/requirements_txt/requirements_in/requirements.in')
        package = pypi.parse_dependency_file(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/requirements_in/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_dependency_file_eol_comment(self):
        test_file = self.get_test_loc('pypi/requirements_txt/eol_comment/requirements.txt')
        package = pypi.parse_dependency_file(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/eol_comment/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_dependency_file_complex(self):
        test_file = self.get_test_loc('pypi/requirements_txt/complex/requirements.txt')
        package = pypi.parse_dependency_file(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/complex/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_dependency_file_editable(self):
        test_file = self.get_test_loc('pypi/requirements_txt/editable/requirements.txt')
        package = pypi.parse_dependency_file(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/editable/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_dependency_file_double_extras(self):
        test_file = self.get_test_loc('pypi/requirements_txt/double_extras/requirements.txt')
        package = pypi.parse_dependency_file(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/double_extras/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    @expectedFailure
    def test_parse_dependency_file_repeated(self):
        # FAILURE: dparse library wrongly detect the first of two repeated
        # dependencies we should return only a single value which should be the
        # last one
        test_file = self.get_test_loc('pypi/requirements_txt/repeated/requirements.txt')
        package = pypi.parse_dependency_file(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/repeated/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_dependency_file_vcs_eggs(self):
        test_file = self.get_test_loc('pypi/requirements_txt/vcs_eggs/requirements.txt')
        package = pypi.parse_dependency_file(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/vcs_eggs/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_dependency_file_local_paths_and_files(self):
        test_file = self.get_test_loc('pypi/requirements_txt/local_paths_and_files/requirements.txt')
        package = pypi.parse_dependency_file(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/local_paths_and_files/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_dependency_file_urls_wth_checksums(self):
        test_file = self.get_test_loc('pypi/requirements_txt/urls_wth_checksums/requirements.txt')
        package = pypi.parse_dependency_file(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/urls_wth_checksums/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_dependency_file_mixed(self):
        test_file = self.get_test_loc('pypi/requirements_txt/mixed/requirements.txt')
        package = pypi.parse_dependency_file(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/mixed/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_dependency_file_comments_and_empties(self):
        test_file = self.get_test_loc('pypi/requirements_txt/comments_and_empties/requirements.txt')
        package = pypi.parse_dependency_file(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/comments_and_empties/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_dependency_file_many_specs(self):
        test_file = self.get_test_loc('pypi/requirements_txt/many_specs/requirements.txt')
        package = pypi.parse_dependency_file(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/many_specs/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_dependency_file_vcs_editable(self):
        test_file = self.get_test_loc('pypi/requirements_txt/vcs_editable/requirements.txt')
        package = pypi.parse_dependency_file(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/vcs_editable/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_dependency_file_vcs_extras_require(self):
        test_file = self.get_test_loc('pypi/requirements_txt/vcs_extras_require/requirements.txt')
        package = pypi.parse_dependency_file(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/vcs_extras_require/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_dependency_file_vcs_git(self):
        test_file = self.get_test_loc('pypi/requirements_txt/vcs-git/requirements.txt')
        package = pypi.parse_dependency_file(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/vcs-git/output.expected.json')
        self.check_package(package, expected_loc, regen=False)


class TestPyPiPipfile(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_pipfile_lock_sample1(self):
        test_file = self.get_test_loc('pypi/pipfile.lock/sample1/Pipfile.lock')
        package = pypi.parse_pipfile_lock(test_file)
        expected_loc = self.get_test_loc('pypi/pipfile.lock/sample1/Pipfile.lock-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_pipfile_lock_sample2(self):
        test_file = self.get_test_loc('pypi/pipfile.lock/sample2/Pipfile.lock')
        package = pypi.parse_pipfile_lock(test_file)
        expected_loc = self.get_test_loc('pypi/pipfile.lock/sample2/Pipfile.lock-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_pipfile_lock_sample3(self):
        test_file = self.get_test_loc('pypi/pipfile.lock/sample3/Pipfile.lock')
        package = pypi.parse_pipfile_lock(test_file)
        expected_loc = self.get_test_loc('pypi/pipfile.lock/sample3/Pipfile.lock-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_pipfile_lock_sample4(self):
        test_file = self.get_test_loc('pypi/pipfile.lock/sample4/Pipfile.lock')
        package = pypi.parse_pipfile_lock(test_file)
        expected_loc = self.get_test_loc('pypi/pipfile.lock/sample4/Pipfile.lock-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_pipfile_lock_sample5(self):
        test_file = self.get_test_loc('pypi/pipfile.lock/sample5/Pipfile.lock')
        package = pypi.parse_pipfile_lock(test_file)
        expected_loc = self.get_test_loc('pypi/pipfile.lock/sample5/Pipfile.lock-expected.json')
        self.check_package(package, expected_loc, regen=False)


class TestRequirementsFiletype(object):

    requirement_files = [
        ('requirements.txt', 'requirements.txt'),
        ('sample-requirements.txt', 'requirements.txt'),
        ('requirements-test.txt', 'requirements.txt'),
        ('sample-requirements-test.txt', 'requirements.txt'),
        ('requirements-dev.txt', 'requirements.txt'),
        ('sample-requirements-dev.txt', 'requirements.txt'),
        ('requirements.in', 'requirements.txt'),
        ('sample-requirements.in', 'requirements.txt'),
        ('requirements-test.in', 'requirements.txt'),
        ('sample-requirements-test.in', 'requirements.txt'),
        ('requirements-dev.in', 'requirements.txt'),
        ('sample-requirements-dev.in', 'requirements.txt'),
        ('Pipfile.lock', 'Pipfile.lock')
    ]

    @pytest.mark.parametrize('filename, expected_filename', requirement_files)
    def test_file_type(self, filename, expected_filename):
        filename = pypi.get_dparse_dependency_type(filename)
        assert filename == expected_filename


def get_setup_py_test_files(test_dir):
    """
    Yield tuples of (setup.py file, expected JSON file) from a `test_dir` test
    data directory.
    """
    for top, _, files in os.walk(test_dir):
        for tfile in files:
            if tfile.endswith('setup.py'):
                continue
            test_loc = os.path.join(top, tfile)
            expected_loc = test_loc + '-expected.json'
            yield test_loc, expected_loc


class TestSetupPyVersions(object):
    test_data_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        'data',
        'setup.py-versions',
    ))

    @pytest.mark.parametrize('test_loc, expected_loc', list(get_setup_py_test_files(test_data_dir)))
    def test_parse_setup_py_with_computed_versions(self, test_loc, expected_loc, regen=False):
        package = pypi.parse_setup_py(test_loc)
        if package:
            results = package.to_dict()
        else:
            results = {}

        if regen:
            with open(expected_loc, 'w') as ex:
                json.dump(results, ex, indent=2, separators=(',', ': '))

        with open(expected_loc) as ex:
            expected = json.load(ex)

        try:
            assert results == expected
        except AssertionError:
            assert json.dumps(results, indent=2) == json.dumps(expected, indent=2)


class TestPyPiSetupPy(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    @skipIf(on_windows, 'Somehow this fails on Windows')
    def test_parse_setup_py_arpy(self):
        test_file = self.get_test_loc('pypi/setup.py/arpy_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/arpy_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    @expectedFailure
    def test_parse_setup_py_pluggy(self):
        test_file = self.get_test_loc('pypi/setup.py/pluggy_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/pluggy_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    @expectedFailure
    def test_parse_setup_py_pygtrie(self):
        # this uses a kwargs dict
        test_file = self.get_test_loc('pypi/setup.py/pygtrie_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/pygtrie_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_basic(self):
        test_file = self.get_test_loc('pypi/setup.py/simple-setup.py')
        package = pypi.parse(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_boolean2_py(self):
        test_file = self.get_test_loc('pypi/setup.py/boolean2_py_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/boolean2_py_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_container_check(self):
        test_file = self.get_test_loc('pypi/setup.py/container_check_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/container_check_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_fb303_py(self):
        test_file = self.get_test_loc('pypi/setup.py/fb303_py_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/fb303_py_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_frell_src(self):
        # setup.py is a temaplte with @vars
        test_file = self.get_test_loc('pypi/setup.py/frell_src_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/frell_src_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_gyp(self):
        test_file = self.get_test_loc('pypi/setup.py/gyp_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/gyp_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_interlap(self):
        test_file = self.get_test_loc('pypi/setup.py/interlap_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/interlap_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_mb(self):
        test_file = self.get_test_loc('pypi/setup.py/mb_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/mb_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_ntfs(self):
        test_file = self.get_test_loc('pypi/setup.py/ntfs_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/ntfs_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_nvchecker(self):
        test_file = self.get_test_loc('pypi/setup.py/nvchecker_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/nvchecker_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_oi_agents_common_code(self):
        test_file = self.get_test_loc('pypi/setup.py/oi_agents_common_code_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/oi_agents_common_code_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_packageurl_python(self):
        test_file = self.get_test_loc('pypi/setup.py/packageurl_python_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/packageurl_python_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_pipdeptree(self):
        test_file = self.get_test_loc('pypi/setup.py/pipdeptree_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/pipdeptree_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_pydep(self):
        test_file = self.get_test_loc('pypi/setup.py/pydep_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/pydep_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_pyrpm_2(self):
        test_file = self.get_test_loc('pypi/setup.py/pyrpm_2_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/pyrpm_2_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_python_publicsuffix(self):
        test_file = self.get_test_loc('pypi/setup.py/python_publicsuffix_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/python_publicsuffix_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_repology_py_libversion(self):
        test_file = self.get_test_loc('pypi/setup.py/repology_py_libversion_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/repology_py_libversion_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_saneyaml(self):
        test_file = self.get_test_loc('pypi/setup.py/saneyaml_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/saneyaml_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_setuppycheck(self):
        test_file = self.get_test_loc('pypi/setup.py/setuppycheck_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/setuppycheck_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_url_py(self):
        test_file = self.get_test_loc('pypi/setup.py/url_py_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/url_py_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_venv(self):
        test_file = self.get_test_loc('pypi/setup.py/venv_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/venv_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_xmltodict(self):
        test_file = self.get_test_loc('pypi/setup.py/xmltodict_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/xmltodict_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

