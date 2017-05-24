#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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

from collections import OrderedDict
import os

from commoncode.testcase import FileBasedTesting

from commoncode.hash import checksum
from commoncode.hash import get_hasher
from commoncode.hash import b64sha1
from commoncode.hash import md5
from commoncode.hash import sha1
from commoncode.hash import sha256
from commoncode.hash import sha512
from commoncode.hash import sha1_git
from commoncode.hash import multi_checksums


class TestHash(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_get_hasher(self):
        h = get_hasher(160)
        assert 'hvfkN_qlp_zhXR3cuerq6jd2Z7g=' == h('a').b64digest()
        assert '4MkDWJjdUvxlxBRUzsnE0mEb-zc=' == h('aa').b64digest()
        assert 'fiQN50-x7Qj6CNOAY_amqRRiqBU=' == h('aaa').b64digest()

    def test_short_hashes(self):
        h = get_hasher(32)
        assert '0cc175b9' == h('a').hexdigest()
        assert '4124bc0a' == h('aa').hexdigest()
        h = get_hasher(64)
        assert '4124bc0a9335c27f' == h('aa').hexdigest()

    def test_sha1_checksum_on_text(self):
        test_file = self.get_test_loc('hash/dir1/a.txt')
        assert sha1(test_file) == '3ca69e8d6c234a469d16ac28a4a658c92267c423'

    def test_sha1_checksum_on_text2(self):
        test_file = self.get_test_loc('hash/dir2/a.txt')
        assert sha1(test_file) == '3ca69e8d6c234a469d16ac28a4a658c92267c423'

    def test_sha1_checksum_on_dos_text(self):
        test_file = self.get_test_loc('hash/dir2/dos.txt')
        assert sha1(test_file) == 'a71718fb198630ae8ba32926015d8555a03cb06c'

    def test_sha1_checksum_base64(self):
        test_file = self.get_test_loc('hash/dir1/a.png')
        assert b64sha1(test_file) == 'NKxUZdSKmwT8J18JvCIwZg349Pc='

    def test_md5_checksum_on_text(self):
        test_file = self.get_test_loc('hash/dir1/a.txt')
        assert md5(test_file) == '40c53c58fdafacc83cfff6ee3d2f6d69'

    def test_md5_checksum_on_text2(self):
        test_file = self.get_test_loc('hash/dir2/a.txt')
        assert md5(test_file) == '40c53c58fdafacc83cfff6ee3d2f6d69'

    def test_md5_checksum_on_dos_text(self):
        test_file = self.get_test_loc('hash/dir2/dos.txt')
        assert md5(test_file) == '095f5068940e41df9add5d4cc396c181'

    def test_md5_checksum(self):
        test_file = self.get_test_loc('hash/dir1/a.png')
        assert md5(test_file) == '4760fb467f1ebf3b0aeace4a3926f1a4'

    def test_sha1_checksum(self):
        test_file = self.get_test_loc('hash/dir1/a.png')
        assert sha1(test_file) == '34ac5465d48a9b04fc275f09bc2230660df8f4f7'

    def test_sha256_checksum(self):
        test_file = self.get_test_loc('hash/dir1/a.png')
        assert sha256(test_file) == '1b598db6fee8f1ec7bb919c0adf68956f3d20af8c9934a9cf2db52e1347efd35'

    def test_sha512_checksum(self):
        test_file = self.get_test_loc('hash/dir1/a.png')
        assert sha512(test_file) == '5be9e01cd20ff288fd3c3fc46be5c2747eaa2c526197125330947a95cdb418222176b182a4680f0e435ba8f114363c45a67b30eed9a9222407e63ccbde46d3b4'

    def test_checksum_sha1(self):
        test_file = self.get_test_loc('hash/dir1/a.txt')
        assert checksum(test_file, 'sha1') == '3ca69e8d6c234a469d16ac28a4a658c92267c423'

    def test_checksum_md5(self):
        test_file = self.get_test_loc('hash/dir1/a.txt')
        assert checksum(test_file, 'md5') == '40c53c58fdafacc83cfff6ee3d2f6d69'

    def test_multi_checksums(self):
        test_file = self.get_test_loc('hash/dir1/a.png')
        expected = OrderedDict([
            ('md5', '4760fb467f1ebf3b0aeace4a3926f1a4'),
            ('sha1', '34ac5465d48a9b04fc275f09bc2230660df8f4f7'),
            ('sha256', '1b598db6fee8f1ec7bb919c0adf68956f3d20af8c9934a9cf2db52e1347efd35'),
        ])
        result = multi_checksums(test_file, 'md5 sha1 sha256'.split())
        assert expected == result

    def test_multi_checksums_custom(self):
        test_file = self.get_test_loc('hash/dir1/a.png')
        result = multi_checksums(test_file, ('sha512',))
        expected = OrderedDict([
            ('sha512', '5be9e01cd20ff288fd3c3fc46be5c2747eaa2c526197125330947a95cdb418222176b182a4680f0e435ba8f114363c45a67b30eed9a9222407e63ccbde46d3b4'),
        ])
        assert expected == result

    def test_multi_checksums_shattered1(self):
        test_file = self.get_test_loc('hash/sha1-collision/shattered-1.pdf')
        expected = OrderedDict([
            ('md5', 'ee4aa52b139d925f8d8884402b0a750c'),
            ('sha1', '38762cf7f55934b34d179ae6a4c80cadccbb7f0a'),
            ('sha256', '2bb787a73e37352f92383abe7e2902936d1059ad9f1ba6daaa9c1e58ee6970d0'),
            ('sha512', '3c19b2cbcf72f7f5b252ea31677b8f2323d6119e49bcc0fb55931d00132385f1e749bb24cbd68c04ac826ae8421802825d3587fe185abf709669bb9693f6b416'),
            ('sha1_git', 'ba9aaa145ccd24ef760cf31c74d8f7ca1a2e47b0'),
        ])
        result = multi_checksums(test_file)
        assert expected == result

    def test_multi_checksums_shattered2(self):
        test_file = self.get_test_loc('hash/sha1-collision/shattered-2.pdf')
        expected = OrderedDict([
            ('md5', '5bd9d8cabc46041579a311230539b8d1'),
            ('sha1', '38762cf7f55934b34d179ae6a4c80cadccbb7f0a'),
            ('sha256', 'd4488775d29bdef7993367d541064dbdda50d383f89f0aa13a6ff2e0894ba5ff'),
            ('sha512', 'f39a04842e4b28e04558496beb7cb84654ded9c00b2f873c3ef64f9dfdbc760cd0273b816858ba5b203c0dd71af8b65d6a0c1032e00e48ace0b4705eedcc1bab'),
            # Note: this is not the same as the sha1_git for shattered-1.pdf ;)
            ('sha1_git', 'b621eeccd5c7edac9b7dcba35a8d5afd075e24f2'),
        ])
        result = multi_checksums(test_file)
        assert expected == result

    def test_sha1_git_checksum(self):
        test_file = self.get_test_loc('hash/dir1/a.png')
        # test that we match the git hash-object
        # tests/commoncode/data/hash/dir1/a.png ouput as of git 1.9.1
        assert sha1_git(test_file) == '5f212358671a3ada8794cb14fb5227f596447a8c'
