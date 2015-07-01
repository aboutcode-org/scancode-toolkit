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

import commoncode.hash
from commoncode.hash import sha1
from commoncode.hash import md5
from commoncode.hash import b64sha1


class TestHash(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_get_hasher(self):
        h = commoncode.hash.get_hasher(160)
        self.assertEqual('hvfkN_qlp_zhXR3cuerq6jd2Z7g=', h('a').b64digest())
        self.assertEqual('4MkDWJjdUvxlxBRUzsnE0mEb-zc=', h('aa').b64digest())
        self.assertEqual('fiQN50-x7Qj6CNOAY_amqRRiqBU=', h('aaa').b64digest())

    def test_hash_1(self):
        test_file = self.get_test_loc('hash/dir1/a.png')
        assert sha1(test_file) == '34ac5465d48a9b04fc275f09bc2230660df8f4f7'

    def test_hash_2(self):
        test_file = self.get_test_loc('hash/dir1/a.png')
        assert md5(test_file) == '4760fb467f1ebf3b0aeace4a3926f1a4'

    def test_hash_3(self):
        test_file = self.get_test_loc('hash/dir1/a.png')
        assert b64sha1(test_file) == 'NKxUZdSKmwT8J18JvCIwZg349Pc='

    def test_hash_4(self):
        test_file = self.get_test_loc('hash/dir1/a.txt')
        assert sha1(test_file) == '3ca69e8d6c234a469d16ac28a4a658c92267c423'

    def test_hash_5(self):
        test_file = self.get_test_loc('hash/dir1/a.txt')
        assert md5(test_file) == '40c53c58fdafacc83cfff6ee3d2f6d69'

    def test_hash_6(self):
        test_file = self.get_test_loc('hash/dir1/a.txt')
        assert b64sha1(test_file) == 'PKaejWwjSkadFqwopKZYySJnxCM='

    def test_hash_7(self):
        test_file = self.get_test_loc('hash/dir2/a.txt')
        assert sha1(test_file) == '3ca69e8d6c234a469d16ac28a4a658c92267c423'

    def test_hash_8(self):
        test_file = self.get_test_loc('hash/dir2/a.txt')
        assert md5(test_file) == '40c53c58fdafacc83cfff6ee3d2f6d69'

    def test_hash_9(self):
        test_file = self.get_test_loc('hash/dir2/a.txt')
        assert b64sha1(test_file) == 'PKaejWwjSkadFqwopKZYySJnxCM='

    def test_hash_10(self):
        test_file = self.get_test_loc('hash/dir2/dos.txt')
        assert sha1(test_file) == 'a71718fb198630ae8ba32926015d8555a03cb06c'

    def test_hash_11(self):
        test_file = self.get_test_loc('hash/dir2/dos.txt')
        assert md5(test_file) == '095f5068940e41df9add5d4cc396c181'

    def test_hash_12(self):
        test_file = self.get_test_loc('hash/dir2/dos.txt')
        assert b64sha1(test_file) == 'pxcY-xmGMK6LoykmAV2FVaA8sGw='
