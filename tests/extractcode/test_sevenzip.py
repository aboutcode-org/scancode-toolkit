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

from __future__ import absolute_import, print_function

import os

from commoncode.testcase import FileBasedTesting
from extractcode import sevenzip


class TestSevenZip(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_get_7z_errors_password_protected(self):
            test = '''
7-Zip 9.04 beta  Copyright (c) 1999-2009 Igor Pavlov  2009-05-30

Processing archive: c:\w421\scripts\testfiles\archive\zip\zip_password_nexb.zip

Extracting  a.txt     CRC Failed in encrypted file. Wrong password?

Sub items Errors: 1
'''
            result = sevenzip.get_7z_errors(test)
            expected = 'Password protected archive, unable to extract'
            assert expected == result

    def test__list_extracted_7z_files_empty(self):
        assert  [] == sevenzip.list_extracted_7z_files('')

    def test__list_extracted_7z_files_2(self):
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

    def test__list_extracted_7z_files_3(self):
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

    def test_list_sevenzip_on_tar(self):
        test_file = self.get_test_loc('archive/tar/special.tar')
        expected = [
            dict(path=u'0-REGTYPE', size=u'3765', is_file=True, is_dir=False, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False),
            dict(path=u'0-REGTYPE-TEXT', size=u'19941', is_file=True, is_dir=False, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False),
            dict(path=u'0-REGTYPE-VEEEERY_LONG_NAME_____________________________________________________________________________________________________________________155', size=u'3765', is_file=True, is_dir=False, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False),
            dict(path=u'1-LNKTYPE', size=u'0', is_file=True, is_dir=False, is_hardlink=True, is_symlink=False, link_target=u'0-REGTYPE', is_broken_link=False, is_special=False),
            dict(path=u'2-SYMTYPE', size=u'17', is_file=True, is_dir=False, is_hardlink=False, is_symlink=True, link_target=u'testtar/0-REGTYPE', is_broken_link=False, is_special=False),
            dict(path=u'3-CHRTYPE', size=u'0', is_file=True, is_dir=False, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False),
            dict(path=u'5-DIRTYPE', size=u'0', is_file=False, is_dir=True, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False),
            dict(path=u'6-FIFOTYPE', size=u'0', is_file=True, is_dir=False, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False),
            dict(path=u'S-SPARSE', size=u'49152', is_file=True, is_dir=False, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False),
            dict(path=u'S-SPARSE-WITH-NULLS', size=u'49152', is_file=True, is_dir=False, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False)
        ]
        result = [e.to_dict() for e in sevenzip.list_entries(test_file)]
        assert expected == result

    def test_parse_7z_listing_linux(self):
        test_file = self.get_test_loc('archive/7z/listings/cpio_relative.cpio.linux')
        expected = [
            dict(path='../..', size='0', is_file=False, is_dir=True, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False),
            dict(path='../../2folder', size='0', is_file=False, is_dir=True, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False),
            dict(path='../../2folder/3folder', size='0', is_file=False, is_dir=True, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False),
            dict(path='../../2folder/3folder/cpio_relative.cpio', size='0', is_file=True, is_dir=False, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False),
            dict(path='../../2folder/3folder/relative_file', size='14', is_file=True, is_dir=False, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False),
            dict(path='../../2folder/3folder/relative_file~', size='14', is_file=True, is_dir=False, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False),
            dict(path='../../2folder/relative_file', size='14', is_file=True, is_dir=False, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False),
            dict(path='../../relative_file', size='14', is_file=True, is_dir=False, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False)
        ]
        result = [e.to_dict() for e in sevenzip.parse_7z_listing(test_file, False)]
        assert expected == result

    def test_parse_7z_listing_win(self):
        test_file = self.get_test_loc('archive/7z/listings/cpio_relative.cpio.win')
        expected = [
            dict(path=u'..\\..', size=u'0', is_file=False, is_dir=True, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False),
            dict(path=u'..\\..\\2folder', size=u'0', is_file=False, is_dir=True, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False),
            dict(path=u'..\\..\\2folder\\3folder', size=u'0', is_file=False, is_dir=True, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False),
            dict(path=u'..\\..\\2folder\\3folder\\cpio_relative.cpio', size=u'0', is_file=True, is_dir=False, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False),
            dict(path=u'..\\..\\2folder\\3folder\\relative_file', size=u'14', is_file=True, is_dir=False, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False),
            dict(path=u'..\\..\\2folder\\3folder\\relative_file~', size=u'14', is_file=True, is_dir=False, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False),
            dict(path=u'..\\..\\2folder\\relative_file', size=u'14', is_file=True, is_dir=False, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False),
            dict(path=u'..\\..\\relative_file', size=u'14', is_file=True, is_dir=False, is_hardlink=False, is_symlink=False, link_target=None, is_broken_link=False, is_special=False)
        ]
        result = [e.to_dict() for e in sevenzip.parse_7z_listing(test_file, True)]
        assert expected == result
