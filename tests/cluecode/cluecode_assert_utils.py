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

import codecs
from collections import OrderedDict
import os
from os.path import abspath
from os.path import join

import attr

import cluecode.copyrights
from commoncode.testcase import FileDrivenTesting
from commoncode.text import python_safe_name
from commoncode import fileutils
from commoncode import saneyaml
from commoncode.fileutils import file_extension
from commoncode.fileutils import parent_directory
from commoncode.fileutils import file_name

"""
Data-driven Copyright test utilities.
"""

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def expectedFailure(func):
    from unittest.case import expectedFailure
    wrapper = expectedFailure(func)
    wrapper.__wrapped__ = func
    wrapper.is_expected_failure = True
    return wrapper


def check_detection(expected, test_file,
                    what='copyrights',
                    notes=None,
                    expected_failure=False):
    """
    Run detection of copyright on the `test_file`, checking the
    results match the expected list of values.

    `test_file` is either a path string or an iterable of text lines.
    """
    test_file = test_env.get_test_loc(test_file)
    parent = parent_directory(test_file)
    nm = file_name(test_file)
    data_file = join(parent, nm + '.yml')
    tst = CopyrightTest()
    tst.test_file = test_file
    tst.what = what
    tst.data_file = data_file
    tst.notes = notes
    tst.expected_failure = expected_failure
    tst.dump()


def check_detection_orig(expected, test_file,
                    what='copyrights',
                    notes=None,
                    expected_failure=False):
    """
    Run detection of copyright on the `test_file`, checking the
    results match the expected list of values.

    `test_file` is either a path string or an iterable of text lines.
    """
    test_file = test_env.get_test_loc(test_file)

    copyrights, authors, years, holders = cluecode.copyrights.detect(test_file)
    results = {
        'copyrights': copyrights,
        'authors': authors,
        'years': years,
        'holders': holders
    }

    result = results[what]
    assert expected == result


@attr.s(slots=True)
class CopyrightTest(object):
    """
    A copyright detection test is used to verify that copyright detection works
    correctly

    It consists of two files with the same base name: a .yml file with test data
    and a test file with any other extension that needs to be tested for
    detection.

    The following data are loaded based on or from the .yml file:
     - a test file to scan for copyrights (based on file name convenstions),
     - a list of expected copyrights, authors, holders or years to detect,
     - optional notes.
     - a boolean flag expected_failure set to True if a test is expected to fail
       for now

    If a list of expected data is not provided or empty, then this test should
    not detect any such data in the test file.
    """
    data_file = attr.ib(default=None)
    test_file = attr.ib(default=None)
    what = attr.ib(default=None)
    expectations = attr.ib(default=attr.Factory(list))
    expected_failure = attr.ib(default=False)
    notes = attr.ib(default=None)

    def __attrs_post_init__(self, *args, **kwargs):
        if self.data_file:
            with codecs.open(self.data_file, mode='rb', encoding='utf-8') as df:
                for key, value in saneyaml.load(df.read()).items():
                    if value:
                        setattr(self, key, value)

    def to_dict(self):
        """
        Serialize self to an ordered mapping.
        """
        filtered = [(name, field) for name, field in attr.fields(CopyrightTest)
                    if b'_file' in name]
        fields_filter = attr.filters.exclude(*filtered)
        data = attr.asdict(self, filter=fields_filter, dict_factory=OrderedDict)
        return OrderedDict([(key, value) for key, value in data.items() if value])

    def dump(self):
        """
        Dump a representation of self to a .yml data_file in YAML block format.
        """
        as_yaml = saneyaml.dump(self.to_dict())
        with codecs.open(self.data_file, 'wb', encoding='utf-8') as df:
            df.write(as_yaml)


def load_copyright_tests(test_dir=test_env.test_data_dir):
    """
    Yield an iterable of CopyrightTest loaded from test data files in test_dir.
    """
    # first collect files with .yml extension and files with other extensions
    # in two maps keyed by file base_name
    data_files = {}
    test_files = {}
    for top, _, files in os.walk(test_dir):
        for yfile in files:
            if yfile. endswith('~'):
                continue
            base_name = fileutils.file_base_name(yfile)
            file_path = abspath(join(top, yfile))
            if yfile.endswith('.yml'):
                assert base_name not in data_files
                data_files[base_name] = file_path
            else:
                assert base_name not in test_files
                test_files[base_name] = file_path

    # ensure that each data file has a corresponding test file
    diff = set(data_files.keys()).symmetric_difference(set(test_files.keys()))
    assert not diff, ('Orphaned copyright test file(s) found: '
                      'test file without its YAML test descriptor '
                      'or YAML test descriptor without its test file.')

    # second, create pairs of corresponding (data_file, test file) for files
    # that have the same base_name
    for base_name, data_file in data_files.items():
        test_file = test_files[base_name]
        yield CopyrightTest(data_file, test_file)


def make_copyright_test_function(
        expected, test_file, test_data_file, test_name,
        what='copyrights', expected_failure=False):
    """
    Build and return a test function closing on tests arguments.
    """
    if isinstance(test_name, unicode):
        test_name = test_name.encode('utf-8')

    assert isinstance(expected, list)

    def closure_test_function(*args, **kwargs):
        try:
            copyrights, authors, years, holders = cluecode.copyrights.detect(test_file)
            results = OrderedDict([
                ('copyrights', copyrights),
                ('authors', authors),
                ('years', years),
                ('holders', holders),
            ])

            result = results[what]
            assert expected == result
        except:
            # On failure, we compare against more result data to get additional
            # failure details, including the test_file and full results
            # this assert will always fail and provide a more detailed failure trace
            assert expected == results + [test_name, 'test file: file://' + test_file]

    closure_test_function.__name__ = test_name
    closure_test_function.funcname = test_name

    if expected_failure:
        closure_test_function = expectedFailure(closure_test_function)

    return closure_test_function


def build_tests(copyright_tests, clazz):
    """
    Dynamically build test methods from a sequence of CopyrightTest and attach
    these method to the clazz test class.
    """
    for test in copyright_tests:
        tfn = test.test_file_name
        test_name = 'test_copyright_%(tfn)s' % locals()
        test_name = python_safe_name(test_name)

        # closure on the test params
        test_method = make_copyright_test_function(
            test.expectations, test.test_file, test.data_file,
            test_name=test_name,
            what=test.what,
            expected_failure=test.expected_failure,
        )

        # attach that method to our test class
        setattr(clazz, test_name, test_method)
