#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from os.path import abspath
from os.path import dirname
from os.path import exists
from os.path import join

import unittest

import attr
import saneyaml
from license_expression import Licensing

from commoncode import text
from commoncode import fileutils

import packages_test_utils
from packagedcode import alpine
from scancode_config import REGEN_TEST_FIXTURES


"""
Data-driven tests using tests and expectations stored in YAML files.
Test functions are attached to test classes at module import time
"""


@attr.attrs(slots=True)
class AlpineLicenseTest(object):
    """
    A license detection test is used to verify that Alpine declared license
    detection works  correctly

    It consists of one YAML file with test data and expectation and a pacakge
    reference.
    """
    declared_license = attr.attrib()
    license_expression = attr.attrib()
    data_file = attr.attrib(default=None)

    licensing = Licensing()

    @classmethod
    def from_file(cls, data_file):
        with open(data_file) as df:
            data = saneyaml.load(df.read())
        data['data_file'] = data_file
        alptest = cls(**data)
        alptest.license_expression = cls.licensing.parse(
            alptest.license_expression).render()
        return alptest

    def to_dict(self):
        dct = attr.asdict(self)
        dct.pop('data_file')
        return dct

    def dump(self):
        parent = fileutils.parent_directory(self.data_file)
        if not exists(parent):
            fileutils.create_dir(parent)
        with open(self.data_file, 'w') as df:
            df.write(saneyaml.dump(self.to_dict()))

    def get_test_method_name(self):
        dfn = fileutils.file_base_name(self.data_file.lower())
        test_name = f'test_alpine_license_detection_{dfn}'
        return text.python_safe_name(test_name)

    @staticmethod
    def from_dir(test_dir):
        """
        Return an iterable of AlpineLicenseTest objects loaded from `test_dir`
        """
        test_files = packages_test_utils.get_test_files(test_dir, '.yml')
        test_files = (join(test_dir, f) for f in test_files)
        return map(AlpineLicenseTest.from_file, test_files)


def build_tests(test_dir, clazz, regen=REGEN_TEST_FIXTURES):
    """
    Dynamically build license_test methods from a ``test_dir`` of AlpineLicenseTest
    and attach these method to the ``clazz ``license test class.
    """
    license_tests = AlpineLicenseTest.from_dir(test_dir)
    for license_test in license_tests:
        test_method = make_test(license_test, regen=regen)
        test_name = license_test.get_test_method_name()

        if hasattr(clazz, test_name):
            msg = f'Duplicated test method name: {test_name}: file://{license_test.data_file}'
            raise Exception(msg)

        test_method.__name__ = test_name
        setattr(clazz, test_name, test_method)


def make_test(license_test, regen=REGEN_TEST_FIXTURES):
    """
    Build and return a test function closing on tests arguments for a
    license_test LicenseTest object.
    """

    def closure_test_function(*args, **kwargs):
        declared = license_test.declared_license
        _cleaned, detected, _license_detections = alpine.detect_declared_license(declared)

        if regen:
            license_test.license_expression = detected
            license_test.dump()
            return

        assert detected  == license_test.license_expression

    return closure_test_function


TEST_DIR = abspath(join(dirname(__file__), 'data/alpine/licenses'))


class TestAlpineLicenseDataDriven(unittest.TestCase):
    pass


build_tests(TEST_DIR, clazz=TestAlpineLicenseDataDriven, regen=REGEN_TEST_FIXTURES)
