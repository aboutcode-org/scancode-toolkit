#
# Copyright (c) nexB Inc. and others. All rights reserved.
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

import os
import json
import posixpath
from unittest.case import skipIf

from commoncode.testcase import FileBasedTesting
from commoncode.system import py2
from commoncode.system import py3
from commoncode.system import on_windows
from commoncode import fileutils
from extractcode import sevenzip
from extractcode import ExtractErrorFailedToExtract


class TestSevenZip(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_results_with_expected_json(self, results, expected_loc, clean_dates=False, regen=False):
        if regen:
            if py2:
                wmode = 'wb'
            if py3:
                wmode = 'w'
            with open(expected_loc, wmode) as ex:
                json.dump(results, ex, indent=2, separators=(',', ':'))

        with open(expected_loc, 'rb') as ex:
            expected = json.load(ex, encoding='utf-8')
        if clean_dates:
            if isinstance(results, list):
                self.clean_dates(results)
                self.clean_dates(expected)

        assert expected == results

    def clean_dates(self, results):
        if isinstance(results, list):
            for res in results:
                # remove time from date/time stamp
                if 'date' in res:
                    res['date'] = res['date'].partition(' ')[0]

    def test_get_7z_errors_password_protected(self):
            test = '''
7-Zip 9.04 beta  Copyright (c) 1999-2009 Igor Pavlov  2009-05-30

Processing archive: c:\\w421\\scripts\\testfiles\\archive\\zip\\zip_password_nexb.zip

Extracting  a.txt     CRC Failed in encrypted file. Wrong password?

Sub items Errors: 1
'''
            result = sevenzip.get_7z_errors(test, test)
            expected = 'Password protected archive, unable to extract'
            assert expected == result

    def test_list_extracted_7z_files_empty(self):
        assert  [] == sevenzip.list_extracted_7z_files('')

    def test_list_extracted_7z_files_2(self):
        test = '''
7-Zip 9.04 beta  Copyright (c) 1999-2009 Igor Pavlov  2009-05-30'
p7zip Version 9.04 (locale=utf8,Utf16=on,HugeFiles=on,2 CPUs)

Processing archive: /tmp/a.rpm

Extracting  a.cpio

Everything is Ok

Size:       6536
Compressed: 7674
'''
        expected = ['a.cpio']
        result = sevenzip.list_extracted_7z_files(test)
        assert expected == result

    def test_list_extracted_7z_files_3(self):
        test = '''
7-Zip 9.04 beta  Copyright (c) 1999-2009 Igor Pavlov  2009-05-30
p7zip Version 9.04 (locale=utf8,Utf16=on,HugeFiles=on,2 CPUs)

Processing archive: /tmp/a.rpm

Extracting  a.cpio
Extracting  b.cpio

Everything is Ok

Size:       6536
Compressed: 7674
'''
        expected = ['a.cpio', 'b.cpio']
        result = sevenzip.list_extracted_7z_files(test)
        assert expected == result

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

    def test_extract_of_tar_with_aboslute_path(self):
        test_loc = self.get_test_loc('sevenzip/absolute_path.tar')
        target_dir = self.get_temp_dir()
        sevenzip.extract(test_loc, target_dir, file_by_file=False, log=False)
        expected_loc = test_loc + '-extract-expected.json'
        results = self.collect_extracted_path(target_dir)
        self.check_results_with_expected_json(results, expected_loc, regen=False)


class TestSevenZipListEntries(TestSevenZip):

    @skipIf(on_windows, 'Windows file-by-file extracton is not working well')
    def test_list_entries_of_special_tar(self):
        test_loc = self.get_test_loc('sevenzip/special.tar')
        expected_loc = test_loc + '-entries-expected.json'
        entries, errors = sevenzip.list_entries(test_loc)
        entries = [e.to_dict(full=True) for e in entries]
        errors = errors or []
        results = entries + errors
        self.check_results_with_expected_json(results, expected_loc, regen=False)

    @skipIf(not on_windows, 'Windows file-by-file extracton is not working well')
    def test_list_entries_of_special_tar_win(self):
        test_loc = self.get_test_loc('sevenzip/special.tar')
        expected_loc = test_loc + '-entries-expected-win.json'
        entries, errors = sevenzip.list_entries(test_loc)
        entries = [e.to_dict(full=True) for e in entries]
        errors = errors or []
        results = entries + errors
        self.check_results_with_expected_json(results, expected_loc, clean_dates=True, regen=False)

    @skipIf(on_windows, 'Windows file-by-file extracton is not working well')
    def test_list_entries_with_weird_names_7z(self):
        test_loc = self.get_test_loc('sevenzip/weird_names.7z')
        expected_loc = test_loc + '-entries-expected.json'
        entries, errors = sevenzip.list_entries(test_loc)
        entries = [e.to_dict(full=True) for e in entries]
        errors = errors or []
        results = entries + errors
        self.check_results_with_expected_json(results, expected_loc, regen=False)

    @skipIf(not on_windows, 'Windows file-by-file extracton is not working well')
    def test_list_entries_with_weird_names_7z_win(self):
        test_loc = self.get_test_loc('sevenzip/weird_names.7z')
        expected_loc = test_loc + '-entries-expected-win.json'
        entries, errors = sevenzip.list_entries(test_loc)
        entries = [e.to_dict(full=True) for e in entries]
        errors = errors or []
        results = entries + errors
        self.check_results_with_expected_json(results, expected_loc, clean_dates=True, regen=False)


class TestSevenParseListing(TestSevenZip):

    def check_parse_7z_listing(self, test_loc, regen=False):
        test_loc = self.get_test_loc(test_loc)
        results = [e.to_dict(full=True) for e in sevenzip.parse_7z_listing(location=test_loc, utf=True)]
        expected_loc = test_loc + '-expected.json'
        self.check_results_with_expected_json(
            results=results, expected_loc=expected_loc, regen=regen)

    def test_parse_7z_listing_01(self):
        self.check_parse_7z_listing('sevenzip/listings/cpio_relative.cpio.linux', regen=False)

    def test_parse_7z_listing_02(self):
        self.check_parse_7z_listing('sevenzip/listings/cpio_relative.cpio.win', regen=False)

    def test_parse_7z_listing_03(self):
        self.check_parse_7z_listing('sevenzip/listings/weird_names.7z_7zip_linux_listing.data', regen=False)

    def test_parse_7z_listing_04(self):
        self.check_parse_7z_listing('sevenzip/listings/weird_names.ar_7zip_linux_listing.data', regen=False)

    def test_parse_7z_listing_05(self):
        self.check_parse_7z_listing('sevenzip/listings/weird_names.cpio_7zip_linux_listing.data', regen=False)

    def test_parse_7z_listing_06(self):
        self.check_parse_7z_listing('sevenzip/listings/weird_names.iso_7zip_linux_listing.data', regen=False)

    def test_parse_7z_listing_07(self):
        self.check_parse_7z_listing('sevenzip/listings/weird_names.rar_7zip_linux_listing.data', regen=False)

    def test_parse_7z_listing_08(self):
        self.check_parse_7z_listing('sevenzip/listings/weird_names.tar_7zip_linux_listing.data', regen=False)

    def test_parse_7z_listing_09(self):
        self.check_parse_7z_listing('sevenzip/listings/weird_names.zip_7zip_linux_listing.data', regen=False)


class TestSevenZipFileByFile(TestSevenZip):

    def check_extract_file_by_file(self, test_file):
        """
        This test uses a different expected JSON file on Linux
        """
        test_loc = self.get_test_loc(test_file)
        target_dir = self.get_temp_dir()
        suffix = '-win' if on_windows else ''
        try:
            sevenzip.extract_file_by_file(test_loc, target_dir, log=False)
        except ExtractErrorFailedToExtract as e:
            expected_err_loc = test_loc + '-extract-errors-expected' + suffix + '.json'

            self.check_results_with_expected_json(e.args[0], expected_err_loc, regen=False)

        expected_loc = test_loc + '-extract-expected' + suffix + '.json'
        results = self.collect_extracted_path(target_dir)
        self.check_results_with_expected_json(results, expected_loc, regen=False)

    def test_extract_file_by_file_of_tar_with_absolute_path(self):
        self.check_extract_file_by_file('sevenzip/absolute_path.tar')

    def test_extract_file_by_file_of_nested_zip(self):
        self.check_extract_file_by_file('sevenzip/relative_nested.zip')

    def test_extract_file_by_file_of_special_tar(self):
        self.check_extract_file_by_file('sevenzip/special.tar')

    def test_extract_file_by_file_with_weird_names_7z(self):
        self.check_extract_file_by_file('sevenzip/weird_names.7z')

    def test_extract_file_by_file_weird_names_zip(self):
        self.check_extract_file_by_file('sevenzip/weird_names.zip')

    def test_extract_file_by_file_weird_names_ar(self):
        self.check_extract_file_by_file('sevenzip/weird_names.ar')

    def test_extract_file_by_file_weird_names_cpio(self):
        self.check_extract_file_by_file('sevenzip/weird_names.cpio')

    def test_extract_file_by_file_weird_names_tar(self):
        self.check_extract_file_by_file('sevenzip/weird_names.tar')
