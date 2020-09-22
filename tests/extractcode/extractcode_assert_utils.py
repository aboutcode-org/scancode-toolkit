#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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

from collections import OrderedDict
import json
import os
import ntpath
import posixpath

from commoncode import compat
from commoncode import filetype
from commoncode import fileutils
from commoncode.testcase import FileBasedTesting
from commoncode.system import on_windows
from commoncode.system import py2
from commoncode.system import py3

"""
Shared archiving test utils.
"""


def check_size(expected_size, location):
    assert expected_size == os.stat(location).st_size


def check_results_with_expected_json(results, expected_loc, regen=False):
    if regen:
        if py2:
            wmode = 'wb'
        if py3:
            wmode = 'w'
        with open(expected_loc, wmode) as ex:
            json.dump(results, ex, indent=2, separators=(',', ':'))
    with open(expected_loc, 'rb') as ex:
        expected = json.load(ex, encoding='utf-8', object_pairs_hook=OrderedDict)
    try:
        assert expected == results
    except AssertionError:
        assert json.dumps(expected, indent=2) == json.dumps(results, indent=2)


def check_files(test_dir, expected, regen=False):
    """
    Walk test_dir.
    Check that all dirs are readable.
    Check that all files are:
     * non-special,
     * readable,
     * have a posix path that ends with one of the expected tuple paths.
    """
    result = []
    locs = []
    if filetype.is_file(test_dir):
        test_dir = fileutils.parent_directory(test_dir)

    test_dir_path = fileutils.as_posixpath(test_dir)
    for top, _, files in os.walk(test_dir):
        for f in files:
            location = os.path.join(top, f)
            locs.append(location)
            path = fileutils.as_posixpath(location)
            path = path.replace(test_dir_path, '').strip('/')
            result.append(path)

    expected_is_json_file = False
    if not isinstance(expected, (list, tuple)) and expected.endswith('.json'):
        expected_is_json_file = True
        # this is a path to a JSON file
        if regen:
            wmode = 'wb' if py2 else 'w'
            with open(expected, wmode) as ex:
                json.dump(result, ex, indent=2, separators=(',', ':'))
            expected_content = result
        else:
            with open(expected, 'rb') as ex:
                expected_content = json.load(ex, encoding='utf-8', object_pairs_hook=OrderedDict)
    else:
        expected_content = expected

    expected_content = sorted(expected_content)
    result = sorted(result)

    try:
        assert expected_content == result
    except AssertionError:
        files = [
            'test_dir: file://{}'.format(test_dir),
            'expected: file://{}'.format(expected if expected_is_json_file else ''),
        ]
        assert files + expected_content == result

    for location in locs:
        assert filetype.is_file(location)
        assert not filetype.is_special(location)
        assert filetype.is_readable(location)


def check_no_error(result):
    """
    Check that every ExtractEvent in the `result` list has no error or warning.
    """
    for r in result:
        assert not r.errors
        assert not r.warnings


def is_posixpath(location):
    """
    Return True if the `location` path is likely a POSIX-like path using POSIX path
    separators (slash or "/")or has no path separator.

    Return False if the `location` path is likely a Windows-like path using backslash
    as path separators (e.g. "\").
    """
    has_slashes = '/' in location
    has_backslashes = '\\' in location
    # windows paths with drive
    if location:
        drive, _ = ntpath.splitdrive(location)
        if drive:
            return False

    # a path is always POSIX unless it contains ONLY backslahes
    # which is a rough approximation (it could still be posix)
    is_posix = True
    if has_backslashes and not has_slashes:
        is_posix = False
    return is_posix


def to_posix(path):
    """
    Return a path using the posix path separator given a path that may contain posix
    or windows separators, converting \\ to /. NB: this path will still be valid in
    the windows explorer (except as a UNC or share name). It will be a valid path
    everywhere in Python. It will not be valid for windows command line operations.
    """
    is_unicode = isinstance(path, compat.unicode)
    ntpath_sep = is_unicode and u'\\' or '\\'
    posixpath_sep = is_unicode and u'/' or '/'
    if is_posixpath(path):
        if on_windows:
            return path.replace(ntpath_sep, posixpath_sep)
        else:
            return path
    return path.replace(ntpath_sep, posixpath_sep)


class BaseArchiveTestCase(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_get_extractors(self, test_file, expected, kinds=()):
        from extractcode import archive

        test_loc = self.get_test_loc(test_file)
        if kinds:
            extractors = archive.get_extractors(test_loc, kinds)
        else:
            extractors = archive.get_extractors(test_loc)

        fe = fileutils.file_extension(test_loc).lower()
        em = ', '.join(e.__module__ + '.' + e.__name__ for e in extractors)

        msg = ('%(expected)r == %(extractors)r for %(test_file)s\n'
               'with fe:%(fe)r, em:%(em)s' % locals())
        assert expected == extractors, msg

    def assertRaisesInstance(self, excInstance, callableObj, *args, **kwargs):
        """
        This assertion accepts an instance instead of a class for refined
        exception testing.
        """
        kwargs = kwargs or {}
        excClass = excInstance.__class__
        try:
            callableObj(*args, **kwargs)
        except excClass as e:
            assert str(e).startswith(str(excInstance))
        else:
            if hasattr(excClass, '__name__'):
                excName = excClass.__name__
            else:
                excName = str(excClass)
            raise self.failureException('%s not raised' % excName)

    def check_extract(self, test_function, test_file, expected, expected_warnings=None, check_all=False):
        """
        Run the extraction `test_function` on `test_file` checking that a map of
        expected paths --> size exist in the extracted target directory.
        Does not test the presence of all files unless `check_all` is True.
        """
        from extractcode import archive

        test_file = self.get_test_loc(test_file)
        test_dir = self.get_temp_dir()
        warnings = test_function(test_file, test_dir)
        if expected_warnings is not None:
            assert expected_warnings == warnings

        if check_all:
            len_test_dir = len(test_dir)
            extracted = {path[len_test_dir:]: filetype.get_size(path) for path in fileutils.resource_iter(test_dir, with_dirs=False)}
            expected = {os.path.join(test_dir, exp_path): exp_size for exp_path, exp_size in expected.items()}
            assert sorted(expected.items()) == sorted(extracted.items())
        else:
            for exp_path, exp_size in expected.items():
                exp_loc = os.path.join(test_dir, exp_path)
                msg = '''When extracting: %(test_file)s
                    With function: %(test_function)r
                    Failed to find expected path: %(exp_loc)s'''
                assert os.path.exists(exp_loc), msg % locals()
                if exp_size is not None:
                    res_size = os.stat(exp_loc).st_size
                    msg = '''When extracting: %(test_file)s
                        With function: %(test_function)r
                        Failed to assert the correct size %(exp_size)d
                        Got instead: %(res_size)d
                        for expected path: %(exp_loc)s'''
                    assert exp_size == res_size, msg % locals()

    def collect_extracted_path(self, test_dir):
        result = []
        td = fileutils.as_posixpath(test_dir)
        for t, dirs, files in os.walk(test_dir):
            t = fileutils.as_posixpath(t)
            for d in dirs:
                nd = posixpath.join(t, d).replace(td, '') + '/'
                result.append(nd)
            for f in files:
                nf = posixpath.join(t, f).replace(td, '')
                result.append(nf)
        result = sorted(result)
        return result

    def assertExceptionContains(self, text, callableObj, *args, **kwargs):
        try:
            callableObj(*args, **kwargs)
        except Exception as e:
            if text not in str(e):
                raise self.failureException(
                       'Exception %(e)r raised, '
                       'it should contain the text %(text)r '
                       'and does not' % locals())
        else:
            raise self.failureException(
                   'Exception containing %(text)r not raised' % locals())
