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
from unittest.case import expectedFailure
import json

import pytest

from commoncode.system import on_windows
from packagedcode.models import DependentPackage
from packagedcode import pypi
from packages_test_utils import PackageTester


class TestPyPi(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse(self):
        test_file = self.get_test_loc('pypi/setup.py/setup.py')
        package = pypi.parse(test_file)
        assert package.name == 'scancode-toolkit'
        assert package.version == '1.5.0'
        assert package.parties[0].name == 'ScanCode'
        assert package.description == ('ScanCode is a tool to scan code for license, '
                'copyright and other interesting facts.')
        assert package.homepage_url == 'https://github.com/nexB/scancode-toolkit'

    def test_parse_metadata(self):
        test_folder = self.get_test_loc('pypi')
        test_file = os.path.join(test_folder, 'metadata.json')
        package = pypi.parse_metadata(test_file)
        assert package.name == 'six'
        assert package.version == '1.10.0'
        assert package.description == 'Python 2 and 3 compatibility utilities'
        assert 'MIT' in package.declared_license['license']
        assert package.declared_license['classifiers'] == ['License :: OSI Approved :: MIT License']
        expected_classifiers = [
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Intended Audience :: Developers",
            "Topic :: Software Development :: Libraries",
            "Topic :: Utilities"
        ]
        assert package.keywords == expected_classifiers
        expected = [
            dict([
                ('type', u'person'), ('role', u'contact'),
                ('name', u'Benjamin Peterson'), ('email', None), ('url', None)])
        ]
        assert [p.to_dict() for p in package.parties] == expected
        assert package.homepage_url == 'http://pypi.python.org/pypi/six/'

    def test_parse_pkg_info(self):
        test_file = self.get_test_loc('pypi/PKG-INFO')
        package = pypi.parse_pkg_info(test_file)
        assert package.name == 'TicketImport'
        assert package.version == '0.7a'
        assert package.description == 'Import CSV and Excel files'
        assert 'BSD' in package.declared_license
        assert package.homepage_url == 'http://nexb.com'
        expected = [dict([('type', u'person'), ('role', u''), ('name', u'Francois Granade'), ('email', None), ('url', None)])]
        assert [p.to_dict() for p in package.parties] == expected

    @skipIf(on_windows, 'Somehow this fails on Windows')
    def test_parse_setup_py_arpy(self):
        test_file = self.get_test_loc('pypi/setup.py/arpy_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/arpy_setup.py-expected.json')
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

    @expectedFailure
    def test_parse_setup_py_pluggy(self):
        test_file = self.get_test_loc('pypi/setup.py/pluggy_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/pluggy_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_setup_py_pydep(self):
        test_file = self.get_test_loc('pypi/setup.py/pydep_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/pydep_setup.py-expected.json')
        self.check_package(package, expected_loc, regen=False)

    @expectedFailure
    def test_parse_setup_py_pygtrie(self):
        # this uses a kwargs dict
        test_file = self.get_test_loc('pypi/setup.py/pygtrie_setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/pygtrie_setup.py-expected.json')
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

    def test_parse_setup_py(self):
        test_file = self.get_test_loc('pypi/setup.py/setup.py')
        package = pypi.parse_setup_py(test_file)
        expected_loc = self.get_test_loc('pypi/setup.py/setup.py-expected.json')
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

    def test_pkginfo_parse_with_unpackaged_source(self):
        test_file = self.get_test_loc('pypi')
        package = pypi.parse_unpackaged_source(test_file)
        expected_loc = self.get_test_loc('pypi/unpackage_source_parser-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_pkginfo_parse_with_unpackaged_source_with_parse_function(self):
        test_file = self.get_test_loc('pypi')
        package = pypi.parse(test_file)
        expected_loc = self.get_test_loc('pypi/unpackage_source_parser-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_pkginfo_parse_with_wheelfile(self):
        test_file = self.get_test_loc('pypi/wheel/atomicwrites-1.2.1-py2.py3-none-any.whl')
        package = pypi.parse_wheel(test_file)
        expected_loc = self.get_test_loc('pypi/wheel/parse-wheel-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_pkginfo_parse_with_wheelfile_with_parse_function(self):
        test_file = self.get_test_loc('pypi/wheel/atomicwrites-1.2.1-py2.py3-none-any.whl')
        package = pypi.parse(test_file)
        expected_loc = self.get_test_loc('pypi/wheel/parse-wheel-expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_requirements_txt_sample1(self):
        test_file = self.get_test_loc('pypi/requirements_txt/sample1/requirements.txt')
        package = pypi.parse_requirements_txt(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/sample1/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_requirements_txt_sample2(self):
        test_file = self.get_test_loc('pypi/requirements_txt/sample2/sample-requirements.txt')
        package = pypi.parse_requirements_txt(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/sample2/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_requirements_txt_sample3(self):
        test_file = self.get_test_loc('pypi/requirements_txt/sample3/requirements-dev.txt')
        package = pypi.parse_requirements_txt(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/sample3/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_requirements_txt_sample4(self):
        test_file = self.get_test_loc('pypi/requirements_txt/sample4/requirements.in')
        package = pypi.parse_requirements_txt(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/sample4/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_requirements_txt_sample5(self):
        test_file = self.get_test_loc('pypi/requirements_txt/sample5/requirements-test.txt')
        package = pypi.parse_requirements_txt(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/sample5/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_requirements_txt_sample6(self):
        test_file = self.get_test_loc('pypi/requirements_txt/sample6/requirements-dev.in')
        package = pypi.parse_requirements_txt(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/sample6/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_requirements_txt_sample7(self):
        test_file = self.get_test_loc('pypi/requirements_txt/sample7/requirements-test.in')
        package = pypi.parse_requirements_txt(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/sample7/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_requirements_txt_sample8(self):
        test_file = self.get_test_loc('pypi/requirements_txt/sample8/requirements.txt')
        package = pypi.parse_requirements_txt(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/sample8/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_requirements_txt_sample9(self):
        test_file = self.get_test_loc('pypi/requirements_txt/sample9/requirements.txt')
        package = pypi.parse_requirements_txt(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/sample9/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_requirements_txt_sample10(self):
        test_file = self.get_test_loc('pypi/requirements_txt/sample10/requirements.txt')
        package = pypi.parse_requirements_txt(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/sample10/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_requirements_txt_sample11(self):
        test_file = self.get_test_loc('pypi/requirements_txt/sample11/requirements.txt')
        package = pypi.parse_requirements_txt(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/sample11/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    @expectedFailure
    def test_requirements_txt_sample12(self):
        # FAILURE: dparse library wrongly detect the dependencies
        # we should return only a single value which should be the latest one
        test_file = self.get_test_loc('pypi/requirements_txt/sample12/requirements.txt')
        package = pypi.parse_requirements_txt(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/sample12/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_requirements_txt_sample13(self):
        test_file = self.get_test_loc('pypi/requirements_txt/sample13/requirements.txt')
        package = pypi.parse_requirements_txt(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/sample13/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_requirements_txt_sample14(self):
        test_file = self.get_test_loc('pypi/requirements_txt/sample14/requirements.txt')
        package = pypi.parse_requirements_txt(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/sample14/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_requirements_txt_sample15(self):
        test_file = self.get_test_loc('pypi/requirements_txt/sample15/requirements.txt')
        package = pypi.parse_requirements_txt(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/sample15/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_requirements_txt_sample16(self):
        test_file = self.get_test_loc('pypi/requirements_txt/sample16/requirements.txt')
        package = pypi.parse_requirements_txt(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/sample16/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_requirements_txt_sample17(self):
        test_file = self.get_test_loc('pypi/requirements_txt/sample17/requirements.txt')
        package = pypi.parse_requirements_txt(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/sample17/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_requirements_txt_sample18(self):
        test_file = self.get_test_loc('pypi/requirements_txt/sample18/requirements.txt')
        package = pypi.parse_requirements_txt(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/sample18/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_requirements_txt_sample19(self):
        test_file = self.get_test_loc('pypi/requirements_txt/sample19/requirements.txt')
        package = pypi.parse_requirements_txt(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/sample19/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_requirements_txt_sample20(self):
        test_file = self.get_test_loc('pypi/requirements_txt/sample20/vcs_git_extras_require_requirements.txt')
        package = pypi.parse_requirements_txt(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/sample20/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_requirements_txt_sample21(self):
        test_file = self.get_test_loc('pypi/requirements_txt/sample21/vcs_git_requirements.txt')
        package = pypi.parse_requirements_txt(test_file)
        expected_loc = self.get_test_loc('pypi/requirements_txt/sample21/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_pipfile_lock_sample1(self):
        test_file = self.get_test_loc('pypi/pipfile.lock/sample1/Pipfile.lock')
        package = pypi.parse_pipfile_lock(test_file)
        expected_loc = self.get_test_loc('pypi/pipfile.lock/sample1/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_pipfile_lock_sample2(self):
        test_file = self.get_test_loc('pypi/pipfile.lock/sample2/Pipfile.lock')
        package = pypi.parse_pipfile_lock(test_file)
        expected_loc = self.get_test_loc('pypi/pipfile.lock/sample2/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_pipfile_lock_sample3(self):
        test_file = self.get_test_loc('pypi/pipfile.lock/sample3/Pipfile.lock')
        package = pypi.parse_pipfile_lock(test_file)
        expected_loc = self.get_test_loc('pypi/pipfile.lock/sample3/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_pipfile_lock_sample4(self):
        test_file = self.get_test_loc('pypi/pipfile.lock/sample4/Pipfile.lock')
        package = pypi.parse_pipfile_lock(test_file)
        expected_loc = self.get_test_loc('pypi/pipfile.lock/sample4/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_pipfile_lock_sample5(self):
        test_file = self.get_test_loc('pypi/pipfile.lock/sample5/Pipfile.lock')
        package = pypi.parse_pipfile_lock(test_file)
        expected_loc = self.get_test_loc('pypi/pipfile.lock/sample5/output.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_with_dparse(self):
        test_file = self.get_test_loc('pypi/dparse/requirements.txt')
        dependencies = pypi.parse_with_dparse(test_file)
        assert dependencies == [DependentPackage(purl='pkg:pypi/lxml@3.4.4', requirement='==3.4.4', scope='dependencies', is_resolved=True),
                DependentPackage(purl='pkg:pypi/requests@2.7.0', requirement='==2.7.0', scope='dependencies', is_resolved=True)]


FILENAME_LIST = [
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


class TestFiletype(object):

    @pytest.mark.parametrize('filename, expected_filename', FILENAME_LIST)
    def test_file_type(self, filename, expected_filename):
        filename = pypi.get_dependency_type(filename)
        assert filename == expected_filename


def get_setup_test_files(test_dir):
    """
    Yield tuples of (setup.py file, expected JSON file) from a test data
    `test_dir` directory.
    """
    for top, _, files in os.walk(test_dir):
        for tfile in files:
            if tfile != 'setup.py':
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

    @pytest.mark.parametrize('test_loc, expected_loc', list(get_setup_test_files(test_data_dir)))
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
