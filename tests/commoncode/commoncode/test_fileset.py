#
# Copyright (c) nexB Inc. and others.
# SPDX-License-Identifier: Apache-2.0
#
# Visit https://aboutcode.org and https://github.com/nexB/ for support and download.
# ScanCode is a trademark of nexB Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os

import commoncode.testcase
from commoncode import fileset


class FilesetTest(commoncode.testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_load(self):
        irf = self.get_test_loc('fileset/scancodeignore.lst')
        result = fileset.load(irf)
        assert ['/foo/*', '!/foobar/*', 'bar/*', '#comment'] == result

    def test_is_included_basic(self):
        assert fileset.is_included('/common/src/', {}, {})
        assert fileset.is_included('/common/src/', None, None)
        assert not fileset.is_included(None, None, None)

    def test_is_included_in_fileset(self):
        incs = {'/common/src/*': '.scanignore'}
        excs = {'/common/src/*.so':'.scanignore'}
        assert not fileset.is_included(None, incs, excs)
        assert not fileset.is_included('', incs, excs)
        assert not fileset.is_included('/', incs, excs)
        assert fileset.is_included('/common/src/', incs, excs)
        assert not fileset.is_included('/common/bin/', incs, excs)

    def test_is_included_in_fileset_2(self):
        incs = {'src*': '.scanignore'}
        excs = {'src/ab': '.scanignore'}
        assert not fileset.is_included(None, incs, excs)
        assert not fileset.is_included('', incs, excs)
        assert not fileset.is_included('/', incs, excs)
        assert fileset.is_included('/common/src/', incs, excs)
        assert not fileset.is_included('src/ab', incs, excs)
        assert fileset.is_included('src/abbab', incs, excs)

    def test_is_included_is_included_exclusions(self):
        incs = {'/src/*': '.scanignore'}
        excs = {'/src/*.so':'.scanignore'}
        assert not fileset.is_included('/src/dist/build/mylib.so', incs, excs)

    def test_is_included_is_included_exclusions_2(self):
        incs = {'src': '.scanignore'}
        excs = {'src/*.so':'.scanignore'}
        assert fileset.is_included('/some/src/this/that', incs, excs)
        assert not fileset.is_included('/src/dist/build/mylib.so', incs, excs)

    def test_is_included_empty_exclusions(self):
        incs = {'/src/*': '.scanignore'}
        excs = {'': '.scanignore'}
        assert fileset.is_included('/src/dist/build/mylib.so', incs, excs)

    def test_is_included_sources(self):
        incs = {'/home/elf/elf-0.5/*': '.scanignore'}
        excs = {'/home/elf/elf-0.5/src/elf': '.scanignore',
                '/home/elf/elf-0.5/src/elf.o': '.scanignore'}
        assert not fileset.is_included('/home/elf/elf-0.5/src/elf', incs, excs)

    def test_is_included_dot_svn(self):
        incs = {'*/.svn/*': '.scanignore'}
        excs = {}
        assert fileset.is_included('home/common/tools/elf/.svn/', incs, excs)
        assert fileset.is_included('home/common/tools/.svn/this', incs, excs)
        assert not fileset.is_included('home/common/tools/this', incs, excs)

    def test_is_included_dot_svn_with_excludes(self):
        incs = {'*/.svn/*': '.scanignore'}
        excs = {'*/.git/*': '.scanignore'}
        assert fileset.is_included('home/common/tools/elf/.svn/', incs, excs)
        assert fileset.is_included('home/common/tools/.svn/this', incs, excs)
        assert not fileset.is_included('home/common/.git/this', incs, excs)

    def test_get_matches(self):
        patterns = {'*/.svn/*': '.scanignore'}
        assert fileset.get_matches('home/common/tools/elf/.svn/', patterns)
        assert fileset.get_matches('home/common/tools/.svn/this', patterns)
        assert not fileset.get_matches('home/common/.git/this', patterns)

    def test_get_matches_accepts_a_list_or_tuple(self):
        patterns = ['*/.svn/*']
        assert fileset.get_matches('home/common/tools/elf/.svn/', patterns)

        patterns = '*/.svn/*',
        assert fileset.get_matches('home/common/tools/elf/.svn/', patterns)
