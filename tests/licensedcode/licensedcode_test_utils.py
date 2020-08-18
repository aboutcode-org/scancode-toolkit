#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict
import io
import os
import traceback

import attr
from license_expression import Licensing
import pytest

from commoncode import compat
from commoncode import saneyaml
from commoncode.system import py2
from commoncode.system import py3
from commoncode import text
from commoncode.testcase import get_test_file_pairs


"""
Data-driven tests using expectations stored in YAML files.
"""

@attr.attrs(slots=True)
class LicenseTest(object):
    """
    A license detection test is used to verify that license detection works
    correctly

    It consists of two files with the same base name: a .yml file with test data
    and a test file with any other extension that needs to be tested for
    detection

    The following data are loaded from the .yml file:
     - a test file to scan for licenses,
     - a list of expected licenses expressions to detect
     - optional notes.
     - a boolean flag expected_failure set to True if a test is expected to fail
       for now.

    If the list of license expressions is empty, then this test should not
    detect any license in the test file.
    """
    data_file = attr.attrib(default=None)
    test_file = attr.attrib(default=None)
    test_file_name = attr.attrib(default=None)
    license_expressions = attr.attrib(default=attr.Factory(list))
    notes = attr.attrib(default=None)
    expected_failure = attr.attrib(default=False)

    licensing = Licensing()

    def __attrs_post_init__(self, *args, **kwargs):
        if self.test_file:
            _, _, self.test_file_name = self.test_file.partition(
                os.path.join('licensedcode', 'data') + os.sep)

        data = {}
        if self.data_file:
            try:
                with io.open(self.data_file, encoding='utf-8') as df:
                    data = saneyaml.load(df.read()) or {}
            except Exception as e:
                raise Exception('Failed to read:', 'file://' + self.data_file, e)

            self.license_expressions = data.pop('license_expressions', [])
            self.notes = data.pop('notes', None)
            # True if the test is expected to fail
            self.expected_failure = data.pop('expected_failure', False)

        if data:
            raise Exception(
                'Unknown data elements: ' + repr(data) +
                ' for: file://' + self.data_file)

        if self.license_expressions:
            for i, exp in enumerate(self.license_expressions[:]):
                try:
                    expression = self.licensing.parse(exp)
                except:
                    raise Exception(
                        'Unable to parse License rule expression: '
                        +repr(exp) + ' for: file://' + self.data_file +
                        '\n' + traceback.format_exc()
                )
                if expression is None:
                    raise Exception(
                        'Unable to parse License rule expression: '
                        +repr(exp) + ' for:' + repr(self.data_file))

                new_exp = expression.render()
                self.license_expressions[i] = new_exp

        else:
            if not self.notes:
                raise Exception(
                    'A license test without expected license_expressions should '
                    'have explanatory notes:  for: file://' + self.data_file)

    def to_dict(self):
        dct = OrderedDict()
        if self.license_expressions:
            dct['license_expressions'] = self.license_expressions
        if self.expected_failure:
            dct['expected_failure'] = self.expected_failure
        if self.notes:
            dct['notes'] = self.notes
        return dct

    def dump(self):
        """
        Dump a representation of self to its YAML data file
        """
        as_yaml = saneyaml.dump(self.to_dict())
        with io.open(self.data_file, 'w', encoding='utf-8') as df:
            df.write(as_yaml)

    def get_content(self):
        """
        Return a byte strings of the test file content.
        """
        with open(self.test_file, 'rb') as df:
            d = df.read()
        return d

    def get_test_method_name(self, prefix='test_detection_'):
        test_file_name = self.test_file_name
        test_name = '{prefix}{test_file_name}'.format(**locals())
        test_name = text.python_safe_name(test_name)
        if py2 and not isinstance(test_name, bytes):
            test_name = test_name.encode('utf-8')
        if py3 and not isinstance(test_name, compat.unicode):
            test_name = test_name.decode('utf-8')
        return test_name

    @staticmethod
    def load_from(test_dir):
        """
        Return an iterable of LicenseTest objects loaded from `test_dir`
        """
        return [LicenseTest(data_file, test_file)
                 for data_file, test_file in get_test_file_pairs(test_dir)]


def build_tests(test_dir, clazz, regen=False):
    """
    Dynamically build license_test methods from a sequence of LicenseTest and
    attach these method to the clazz license test class.
    """

    license_tests = LicenseTest.load_from(test_dir)

    # TODO: check that we do not have duplicated tests with same data and text

    for license_test in license_tests:
        test_name = license_test.get_test_method_name()
        test_file = license_test.test_file

        # closure on the license_test params
        test_method = make_test(license_test, regen=regen)

        # avoid duplicated test method
        if hasattr(clazz, test_name):
            msg = ('Duplicated test method name: {test_name}: file://{test_file}'
            ).format(**locals())
            raise Exception(msg)

        # attach that method to our license_test class
        setattr(clazz, test_name, test_method)


def make_test(license_test, regen=False):
    """
    Build and return a test function closing on tests arguments for a
    license_test LicenseTest object.
    """
    test_name = license_test.get_test_method_name()

    from licensedcode import cache
    from licensedcode.tracing import get_texts

    expected_expressions = license_test.license_expressions or []

    test_file = license_test.test_file
    test_data_file = license_test.data_file
    expected_failure = license_test.expected_failure

    def closure_test_function(*args, **kwargs):
        idx = cache.get_index()
        matches = idx.match(location=test_file, min_score=0)
        if not matches:
            matches = []

        detected_expressions = [match.rule.license_expression for match in matches]

        # use detection as expected and dump test back
        if regen:
            if not expected_failure:
                license_test.license_expressions = detected_expressions
            license_test.dump()
            return

        if expected_expressions != detected_expressions:
            # On failure, we compare against more result data to get additional
            # failure details, including the test_file and full match details
            results = expected_expressions + ['======================', '']
            failure_trace = detected_expressions[:] + ['======================', '']
            for match in matches:
                qtext, itext = get_texts(match)
                rule_text_file = match.rule.text_file
                if match.rule.is_license:
                    rule_data_file = rule_text_file.replace('LICENSE', 'yml')
                else:
                    rule_data_file = match.rule.data_file
                failure_trace.extend(['',
                    '======= MATCH ====', repr(match),
                    '======= Matched Query Text for:',
                    'file://{test_file}'.format(**locals())
                ])
                if test_data_file:
                    failure_trace.append('file://{test_data_file}'.format(**locals()))

                failure_trace.append('')
                failure_trace.append(qtext)
                failure_trace.extend(['',
                    '======= Matched Rule Text for:',
                    'file://{rule_text_file}'.format(**locals()),
                    'file://{rule_data_file}'.format(**locals()),
                    '',
                    itext,
                ])
            if not matches:
                failure_trace.extend(['',
                    '======= NO MATCH ====',
                    '======= Not Matched Query Text for:',
                    'file://{test_file}'.format(**locals())
                ])
                if test_data_file:
                    failure_trace.append('file://{test_data_file}'.format(**locals()))

            # this assert will always fail and provide a detailed failure trace
            assert '\n'.join(results) == '\n'.join(failure_trace)

    closure_test_function.__name__ = test_name

    if expected_failure:
        closure_test_function = pytest.mark.xfail(closure_test_function)

    return closure_test_function


# a small test set of legalese to use in tests
mini_legalese = frozenset([
'accordance',
'alternatively',
'according',
'acknowledgement',
'enforcement',
'admission',
'alleged',
'accused',
'determines',
'exceeding',
'assessment',
'exceeds',
'literal',
'existed',
'ignored',
'complementary',
'responded',
'observed',
'assessments',
'volunteer',
'admitted',
'ultimately',
'choices',
'complications',
'allowance',
'fragments',
'plaintiff',
'license',
'agreement',
'gnu',
'general',
'warranty',
'distribute',
'distribution',
'licensed',
'covered',
'warranties',
'damages',
'liability',
'means',
])
