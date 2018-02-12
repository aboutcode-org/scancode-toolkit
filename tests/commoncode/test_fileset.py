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

import os

import commoncode.testcase
from commoncode import fileset


class FilesetTest(commoncode.testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_load(self):
        irf = self.get_test_loc('fileset/scancodeignore.lst')
        result = fileset.load(irf)
        assert ['/foo/*', '!/foobar/*', 'bar/*', '#comment'] == result

    def test_match_basic(self):
        assert not fileset.match('/common/src/', {}, {})
        assert not fileset.match('/common/src/', None, None)
        assert not fileset.match(None, None, None)

    def test_in_fileset(self):
        incs = {'/common/src/*': '.scanignore'}
        excs = {'/common/src/*.so':'.scanignore'}
        assert not fileset.match(None, incs, excs)
        assert not fileset.match('', incs, excs)
        assert not fileset.match('/', incs, excs)
        assert fileset.match('/common/src/', incs, excs)
        assert not fileset.match('/common/bin/', incs, excs)

    def test_in_fileset_2(self):
        incs = {'src*': '.scanignore'}
        excs = {'src/ab': '.scanignore'}
        assert not fileset.match(None, incs, excs)
        assert not fileset.match('', incs, excs)
        assert not fileset.match('/', incs, excs)
        assert fileset.match('/common/src/', incs, excs)
        assert not fileset.match('src/ab', incs, excs)
        assert fileset.match('src/abbab', incs, excs)

    def test_match_exclusions(self):
        incs = {'/src/*': '.scanignore'}
        excs = {'/src/*.so':'.scanignore'}
        assert not fileset.match('/src/dist/build/mylib.so', incs, excs)

    def test_match_exclusions_2(self):
        incs = {'src': '.scanignore'}
        excs = {'src/*.so':'.scanignore'}
        assert fileset.match('/some/src/this/that', incs, excs)
        assert not fileset.match('/src/dist/build/mylib.so', incs, excs)

    def test_match_empty_exclusions(self):
        incs = {'/src/*': '.scanignore'}
        excs = {'': '.scanignore'}
        assert fileset.match('/src/dist/build/mylib.so', incs, excs)

    def test_match_sources(self):
        incs = {'/home/elf/elf-0.5/*': '.scanignore'}
        excs = {'/home/elf/elf-0.5/src/elf': '.scanignore',
                '/home/elf/elf-0.5/src/elf.o': '.scanignore'}
        assert not fileset.match('/home/elf/elf-0.5/src/elf', incs, excs)

    def test_match_dot_svn(self):
        incs = {'*/.svn/*': '.scanignore'}
        excs = {}
        assert fileset.match('home/common/tools/elf/.svn/', incs, excs)
        assert fileset.match('home/common/tools/.svn/this', incs, excs)
        assert not fileset.match('home/common/tools/this', incs, excs)

    def test_match_dot_svn_with_excludes(self):
        incs = {'*/.svn/*': '.scanignore'}
        excs = {'*/.git/*': '.scanignore'}
        assert fileset.match('home/common/tools/elf/.svn/', incs, excs)
        assert fileset.match('home/common/tools/.svn/this', incs, excs)
        assert not fileset.match('home/common/.git/this', incs, excs)
