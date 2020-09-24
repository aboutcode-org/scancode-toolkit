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

import os
from unittest.case import expectedFailure
from unittest.case import skipIf

import pytest

from commoncode.testcase import FileBasedTesting
from commoncode.system import on_linux
from commoncode.system import on_mac
from commoncode.system import on_windows
from commoncode.system import on_windows_64
from commoncode.system import py2

from typecode.contenttype import get_filetype
from typecode.contenttype import get_pygments_lexer
from typecode.contenttype import get_type
from typecode.contenttype import is_data as contenttype_is_data
from typecode.contenttype import is_standard_include


# aliases for testing
get_mimetype_python = lambda l: get_type(l).mimetype_python
get_filetype_pygment = lambda l: get_type(l).filetype_pygment
get_filetype_file = lambda l: get_type(l).filetype_file
get_mimetype_file = lambda l: get_type(l).mimetype_file

is_text = lambda l: get_type(l).is_text
is_archive = lambda l: get_type(l).is_archive
is_compressed = lambda l: get_type(l).is_compressed
is_media = lambda l: get_type(l).is_media
is_winexe = lambda l: get_type(l).is_winexe
is_source = lambda l: get_type(l).is_source
is_script = lambda l: get_type(l).is_script
is_special = lambda l: get_type(l).is_special
is_pdf = lambda l: get_type(l).is_pdf
is_pdf_with_text = lambda l: get_type(l).is_pdf_with_text
is_binary = lambda l: get_type(l).is_binary
is_c_source = lambda l: get_type(l).is_c_source
is_stripped_elf = lambda l: get_type(l).is_stripped_elf
is_elf = lambda l: get_type(l).is_elf

elf_type = lambda l: get_type(l).elf_type
get_link_target = lambda l: get_type(l).link_target
is_link = lambda l: get_type(l).is_link
is_broken_link = lambda l: get_type(l).is_broken_link
size = lambda l: get_type(l).size
contains_text = lambda l: get_type(l).contains_text
is_data = lambda l: get_type(l).is_data
is_js_map = lambda l: get_type(l).is_js_map


class TestContentType(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_size(self):
        test_dir = self.get_test_loc('contenttype/size')
        result = size(test_dir)
        assert 18 == result

    def test_filetype_file_on_unicode_file_name(self):
        test_zip = self.extract_test_zip('contenttype/unicode/unicode.zip')
        test_dir = os.path.join(test_zip, 'a')
        f = os.listdir(test_dir)[0]
        test_file = os.path.join(test_dir, f)
        assert os.path.exists(test_file)

        expected = 'PNG image data, 16 x 12, 8-bit/color RGBA, interlaced'

        assert expected == get_filetype_file(test_file)

        expected = 'image/png'
        assert expected == get_mimetype_file(test_file)

    @skipIf(not on_linux, 'Windows and macOS have some issues with some non-unicode paths')
    def test_filetype_file_on_unicode_file_name2(self):
        zip_file_name = 'contenttype/unicode/unicode2.zip'
        if py2:
            zip_file_name = zip_file_name.encode('utf-8')

        test_zip = self.extract_test_zip(zip_file_name)
        test_dir = os.path.join(test_zip, 'a')
        f = [f for f in os.listdir(test_dir) if f.startswith('g')][0]
        test_file = os.path.join(test_dir, f)
        assert os.path.exists(test_file)

        expected = 'PNG image data, 16 x 12, 8-bit/color RGBA, interlaced'
        if on_windows:
            # FIXME: this is a very short png file though
            expected = 'Non-ISO extended-ASCII text'
        assert expected == get_filetype_file(test_file)

        expected = 'image/png'
        if on_windows:
            # FIXME: this is a very short png file though
            expected = 'text/plain'
        assert expected == get_mimetype_file(test_file)

    @skipIf(on_windows, 'Windows does not have (well supported) links.')
    def test_symbolink_links(self):
        test_dir = self.extract_test_tar('contenttype/links/links.tar.gz', verbatim=True)

        test_file1 = os.path.join(test_dir, 'prunedirs/targets/simlink_to_dir')
        assert is_link(test_file1)
        assert not is_broken_link(test_file1)
        assert '../sources/subdir' == get_link_target(test_file1)

        test_file2 = os.path.join(test_dir, 'prunedirs/targets/simlink_to_file')
        assert is_link(test_file2)
        assert not is_broken_link(test_file2)
        assert '../sources/a.txt' == get_link_target(test_file2)

        test_file3 = os.path.join(test_dir, 'prunedirs/targets/simlink_to_missing_file')
        assert is_link(test_file3)
        assert is_broken_link(test_file3)
        assert '../sources/temp.txt' == get_link_target(test_file3)

        test_file4 = os.path.join(test_dir, 'prunedirs/targets/simlink_to_missing_dir')
        assert is_link(test_file4)
        assert is_broken_link(test_file4)
        assert '../sources/tempdir' == get_link_target(test_file4)

    @skipIf(not on_windows, 'Hangs for now, for lack of proper sudo access on some test servers.')
    @skipIf(on_windows, 'Windows does not have fifos.')
    def test_contenttype_fifo(self):
        test_dir = self.get_temp_dir()
        myfifo = os.path.join(test_dir, 'myfifo')
        import subprocess
        if subprocess.call(['mkfifo', myfifo]) != 0:
            self.fail('Unable to create fifo')
        assert os.path.exists(myfifo)
        assert is_special(myfifo)
        assert 'FIFO pipe' == get_filetype(myfifo)

    def test_directory(self):
        test_file = self.get_test_loc('contenttype')
        assert not is_binary(test_file)
        assert not is_compressed(test_file)
        assert not contains_text(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_archive_gnu_tar(self):
        test_file = self.get_test_loc('contenttype/archive/e.tar')
        assert 'posix tar archive (gnu)' == get_filetype(test_file)
        assert is_binary(test_file)
        assert is_archive(test_file)
        assert not is_compressed(test_file)
        assert contains_text(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_debian_package(self):
        test_file = self.get_test_loc('contenttype/package/libjama-dev_1.2.4-2_all.deb')
        expected = 'debian binary package (format 2.0), with control.tar.gz, data compression gz'
        assert expected == get_filetype(test_file)
        assert is_binary(test_file)
        assert is_archive(test_file)
        assert is_compressed(test_file)
        assert not contains_text(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_package_json(self):
        test_file = self.get_test_loc('contenttype/package/package.json')
        assert 'ascii text, with very long lines' == get_filetype(test_file)
        assert not is_binary(test_file)
        assert '' == get_filetype_pygment(test_file)
        assert not is_source(test_file)

    def test_archive_gz(self):
        test_file = self.get_test_loc('contenttype/archive/file_4.26-1.diff.gz')
        assert get_filetype(test_file).startswith('gzip compressed data')
        assert is_binary(test_file)
        assert is_archive(test_file)
        assert is_compressed(test_file)
        assert not contains_text(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_archive_tar_xz(self):
        test_file = self.get_test_loc('contenttype/archive/test.tar.xz')
        assert get_filetype(test_file).startswith('xz compressed data')
        assert is_binary(test_file)
        assert is_archive(test_file)
        assert is_compressed(test_file)
        assert not contains_text(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_archive_tar_lzma(self):
        test_file = self.get_test_loc('contenttype/archive/test.tar.lzma')
        assert get_filetype(test_file).startswith('lzma compressed data')
        assert is_binary(test_file)
        assert is_archive(test_file)
        assert is_compressed(test_file)
        assert not contains_text(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_archive_zip(self):
        test_file = self.get_test_loc('contenttype/archive/test.zip')
        assert get_filetype(test_file).startswith('zip archive data')
        assert is_binary(test_file)
        assert is_archive(test_file)
        assert is_compressed(test_file)
        assert not contains_text(test_file)
        assert '' == get_filetype_pygment(test_file)

    @skipIf(on_windows, 'fails because of libmagic bug on windows.')
    def test_archive_squashfs_crashing(self):
        test_file = self.get_test_loc('contenttype/archive/crashing-squashfs')
        assert get_filetype_file(test_file).startswith('Squashfs filesystem, little endian, version')
        assert is_archive(test_file)
        assert is_compressed(test_file)
        assert not contains_text(test_file)
        assert '' == get_filetype_pygment(test_file)

    @skipIf(on_windows, 'fails because of libmagic bug on windows.')
    def test_archive_squashfs_gz(self):
        test_file = self.get_test_loc('contenttype/archive/sqfs-gz.sqs')
        assert get_filetype_file(test_file).startswith('Squashfs filesystem, little endian, version')
        assert is_archive(test_file)
        assert is_compressed(test_file)
        assert not contains_text(test_file)
        assert '' == get_filetype_pygment(test_file)

    @skipIf(on_windows, 'fails because of libmagic bug on windows.')
    def test_archive_squashfs_lzo(self):
        test_file = self.get_test_loc('contenttype/archive/sqfs-lzo.sqs')
        assert get_filetype_file(test_file).startswith('Squashfs filesystem, little endian, version')
        assert is_archive(test_file)
        assert is_compressed(test_file)
        assert not contains_text(test_file)
        assert '' == get_filetype_pygment(test_file)

    @skipIf(on_windows, 'fails because of libmagic bug on windows.')
    def test_archive_squashfs_xz(self):
        test_file = self.get_test_loc('contenttype/archive/sqfs-xz.sqs')
        assert get_filetype_file(test_file).startswith('Squashfs filesystem, little endian, version')
        assert is_archive(test_file)
        assert is_compressed(test_file)
        assert not contains_text(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_archive_tar_bz2(self):
        test_file = self.get_test_loc('contenttype/archive/e.tar.bz2')
        assert is_binary(test_file)
        assert is_archive(test_file)
        assert 'bzip2 compressed data, block size = 900k' == get_filetype(test_file)
        assert is_compressed(test_file)
        assert not contains_text(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_archive_tar_gz_1(self):
        test_file = self.get_test_loc('contenttype/archive/a.tar.gz')
        assert not is_source(test_file)
        assert not is_text(test_file)
        assert '' == get_filetype_pygment(test_file)
        assert 'application/gzip' == get_mimetype_file(test_file)
        assert get_filetype(test_file).startswith('gzip compressed data')
        assert is_archive(test_file)
        assert is_compressed(test_file)
        assert not contains_text(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_archive_tar_gz_3(self):
        test_file = self.get_test_loc('contenttype/archive/e.tar.gz')
        assert is_binary(test_file)
        assert is_archive(test_file)
        assert get_filetype(test_file).startswith('gzip compressed data')
        assert is_compressed(test_file)
        assert not contains_text(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_archive_tar_posix_not_compressed(self):
        test_file = self.get_test_loc('contenttype/archive/posixnotgnu.tar')
        assert is_binary(test_file)
        assert is_archive(test_file)
        assert 'posix tar archive' == get_filetype(test_file)
        assert not is_compressed(test_file)
        assert contains_text(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_ar_archive_win_library(self):
        test_file = self.get_test_loc('contenttype/archive/win-archive.lib')
        assert is_binary(test_file)
        assert is_archive(test_file)
        assert 'current ar archive' == get_filetype(test_file)
        assert not is_compressed(test_file)
        assert contains_text(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_win_dll(self):
        test_file = self.get_test_loc('contenttype/binary/windows.dll')
        assert is_binary(test_file)
        assert not is_archive(test_file)
        assert not is_compressed(test_file)
        assert contains_text(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_config_eclipse_data(self):
        test_file = self.get_test_loc('contenttype/config/eclipse_configuration_3u.cfs')
        assert is_binary(test_file)
        assert 'data' == get_filetype(test_file)
        assert contains_text(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_binary_data(self):
        test_file = self.get_test_loc('contenttype/binary/data.fdt')
        assert is_binary(test_file)
        assert 'data' == get_filetype(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_binary_data_2(self):
        test_file = self.get_test_loc('contenttype/binary/dbase.fdt')
        assert 'data' == get_filetype(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_binary_java_serialized_data(self):
        test_file = self.get_test_loc('contenttype/binary/jruby_time_zone_TimeOfDay.dat')
        assert is_binary(test_file)
        assert 'java serialization data, version 5' == get_filetype(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_binary_random_data(self):
        assert 'data' == get_filetype(self.get_test_loc('contenttype/binary-random/binary_random_0'))
        assert 'data' == get_filetype(self.get_test_loc('contenttype/binary-random/binary_random_1'))
        assert 'data' == get_filetype(self.get_test_loc('contenttype/binary-random/binary_random_2'))
        assert 'data' == get_filetype(self.get_test_loc('contenttype/binary-random/binary_random_3'))
        assert 'data' == get_filetype(self.get_test_loc('contenttype/binary-random/binary_random_4'))
        assert 'data' == get_filetype(self.get_test_loc('contenttype/binary-random/binary_random_5'))
        assert 'data' == get_filetype(self.get_test_loc('contenttype/binary-random/binary_random_6'))
        assert 'data' == get_filetype(self.get_test_loc('contenttype/binary-random/binary_random_7'))
        assert 'data' == get_filetype(self.get_test_loc('contenttype/binary-random/binary_random_8'))
        assert '' == get_filetype_pygment(self.get_test_loc('contenttype/binary-random/binary_random_8'))

    def test_build_ant_build_xml(self):
        test_file = self.get_test_loc('contenttype/build/build.xml')
        assert not is_binary(test_file)
        assert 'exported sgml document, ascii text, with crlf line terminators' == get_filetype(test_file)
        assert '' == get_filetype_pygment(test_file)
        assert is_text(test_file)
        assert not is_source(test_file)
        assert not is_script(test_file)

    def test_build_makefile(self):
        test_file = self.get_test_loc('contenttype/build/Makefile')
        assert not is_source(test_file)
        assert not is_script(test_file)
        assert is_text(test_file)
        assert '' == get_filetype_pygment(test_file)
        assert 'ASCII text' == get_filetype_file(test_file)
        assert 'ascii text' == get_filetype(test_file)
        assert 'text/plain' == get_mimetype_file(test_file)

    def test_build_makefile_2(self):
        test_file = self.get_test_loc('contenttype/build/Makefile.inc')
        assert is_text(test_file)
        assert '' == get_filetype_pygment(test_file)
        assert 'makefile script, ascii text, with crlf line terminators' == get_filetype(test_file)
        assert 'text/x-makefile' == get_mimetype_file(test_file)
        assert 'makefile script, ASCII text, with CRLF line terminators' == get_filetype_file(test_file)
        assert not is_source(test_file)

    def test_build_ide_makefile(self):
        test_file = self.get_test_loc('contenttype/build/documentation.dsp')
        assert 'ascii text' == get_filetype(test_file)
        assert '' == get_filetype_pygment(test_file)
        assert not is_source(test_file)

    def test_build_java_maven_pom_pom(self):
        test_file = self.get_test_loc('contenttype/build/pom.pom')
        assert '' == get_filetype_pygment(test_file)
        assert 'xml 1.0 document, ascii text' == get_filetype(test_file)
        assert not is_source(test_file)

    def test_build_java_maven_pom_xml(self):
        test_file = self.get_test_loc('contenttype/build/pom.xml')
        assert not is_source(test_file)
        assert 'exported sgml document, ascii text' == get_filetype(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_certificate_rsa_eclipse(self):
        test_file = self.get_test_loc('contenttype/certificate/ECLIPSE.RSA')
        assert is_binary(test_file)
        assert 'data' == get_filetype(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_certificate(self):
        test_file = self.get_test_loc('contenttype/certificate/CERTIFICATE')
        assert is_binary(test_file)
        assert get_filetype(test_file).startswith('apple diskcopy 4.2 image')
        assert '' == get_filetype_pygment(test_file)

    def test_code_assembly(self):
        test_file = self.get_test_loc('contenttype/code/assembly/bcopy.s')
        assert 'C source, ASCII text, with CRLF line terminators' == get_filetype_file(test_file)
        assert 'GAS' == get_filetype_pygment(test_file)
        assert 'text/x-c' == get_mimetype_file(test_file)
        assert is_source(test_file)
        assert is_text(test_file)

    def test_code_c_1(self):
        test_file = self.get_test_loc('contenttype/code/c/c_code.c')
        assert 'ti-xx graphing calculator (flash)' == get_filetype(test_file)
        assert 'C++' == get_filetype_pygment(test_file)
        assert is_source(test_file)
        assert is_text(test_file)

    def test_code_c_2(self):
        test_file = self.get_test_loc('contenttype/code/c/main.c')
        assert is_source(test_file)
        assert is_text(test_file)
        assert 'C++' == get_filetype_pygment(test_file)
        assert 'c source, ascii text' == get_filetype(test_file)
        assert 'C source, ASCII text' == get_filetype_file(test_file)
        assert 'text/x-c' == get_mimetype_file(test_file)

    def test_code_c_3(self):
        test_file = self.get_test_loc('contenttype/code/c/cpu.c')
        assert is_source(test_file)
        assert is_text(test_file)
        assert 'C++' == get_filetype_pygment(test_file)
        assert 'c source, ascii text' == get_filetype(test_file)
        assert 'text/x-c' == get_mimetype_file(test_file)

    def test_code_c_4(self):
        test_file = self.get_test_loc('contenttype/code/c/mm.c')
        assert is_source(test_file)
        assert is_text(test_file)
        assert 'C++' == get_filetype_pygment(test_file)
        assert 'c source, ascii text' == get_filetype(test_file)
        assert 'text/x-c' == get_mimetype_file(test_file)

    def test_code_c_5(self):
        test_file = self.get_test_loc('contenttype/code/c/pci.c')
        assert is_source(test_file)
        assert is_text(test_file)
        assert 'C source, ASCII text' == get_filetype_file(test_file)
        assert 'C++' == get_filetype_pygment(test_file)
        assert 'c source, ascii text' == get_filetype(test_file)
        assert 'text/x-c' == get_mimetype_file(test_file)

    def test_code_c_6(self):
        test_file = self.get_test_loc('contenttype/code/c/pci_v3.c')
        assert is_source(test_file)
        assert is_text(test_file)
        assert 'C source, ASCII text' == get_filetype_file(test_file)
        assert 'C++' == get_filetype_pygment(test_file)
        assert 'c source, ascii text' == get_filetype(test_file)
        assert 'text/x-c' == get_mimetype_file(test_file)

    def test_code_c_7(self):
        test_file = self.get_test_loc('contenttype/code/c/some.c')
        assert 'ti-xx graphing calculator (flash)' == get_filetype(test_file)
        assert is_source(test_file)
        assert 'C++' == get_filetype_pygment(test_file)

    def test_code_c_include(self):
        test_file = self.get_test_loc('contenttype/code/c/resource.h')
        assert 'ascii text, with crlf line terminators' == get_filetype(test_file)
        assert is_source(test_file)
        assert 'C++' == get_filetype_pygment(test_file)

    def test_code_c_include_2(self):
        test_file = self.get_test_loc('contenttype/code/c/netdb.h')
        assert 'very short file (no magic)' == get_filetype(test_file)
        assert is_source(test_file)
        assert 'C++' == get_filetype_pygment(test_file)

    def test_code_c_include_mixed_case_2(self):
        test_file = self.get_test_loc('contenttype/code/c/TEST_LOWERCASE.h')
        assert 'c source, ascii text' == get_filetype(test_file)
        assert 'C++' == get_filetype_pygment(test_file)

    def test_code_cpp_include_mixed_case(self):
        test_file = self.get_test_loc('contenttype/code/c/TEST.H')
        assert 'c source, ascii text' == get_filetype(test_file)
        assert 'C++' == get_filetype_pygment(test_file)

    def test_code_cpp_mixed_case(self):
        test_file = self.get_test_loc('contenttype/code/c/SIMPLE.C')
        assert 'c source, ascii text' == get_filetype(test_file)
        assert 'C++' == get_filetype_pygment(test_file)

    def test_code_cpp_mixed_case_2(self):
        test_file = self.get_test_loc('contenttype/code/cpp/string.CPP')

        expected = 'c++ source, ascii text'

        assert expected == get_filetype(test_file)
        assert 'C++' == get_filetype_pygment(test_file)

    def test_code_cpp_1(self):
        test_file = self.get_test_loc('contenttype/code/cpp/stacktrace.cpp')
        assert is_source(test_file)
        assert is_text(test_file)
        assert 'C++' == get_filetype_pygment(test_file)
        assert 'c source, ascii text' == get_filetype(test_file)
        assert 'text/x-c' == get_mimetype_file(test_file)

    def test_code_cpp_non_ascii(self):
        test_file = self.get_test_loc('contenttype/code/cpp/non_ascii.cpp')
        assert is_source(test_file)
        assert is_text(test_file)
        assert 'application/octet-stream' == get_mimetype_file(test_file)
        assert 'C++' == get_filetype_pygment(test_file)
        assert 'data' == get_filetype(test_file)

    def test_code_cpp_stdafx(self):
        test_file = self.get_test_loc('contenttype/code/cpp/StdAfx.cpp')
        assert 'c source, ascii text' == get_filetype(test_file)
        assert 'C++' == get_filetype_pygment(test_file)

    def test_code_groff(self):
        test_file = self.get_test_loc(u'contenttype/code/groff/example.ms')
        assert not is_special(test_file)
        assert is_text(test_file)
        assert 'troff or preprocessor input, ascii text' == get_filetype(test_file)
        assert 'GAS' == get_filetype_pygment(test_file)
        # the Apache mimes do not have .ms in their types
        # but the type is still mysteriously returnedd on Windows
        assert 'text/troff' == get_mimetype_python(test_file)
        assert 'text/troff' == get_mimetype_file(test_file)
        assert get_filetype_file(test_file).startswith('troff or preprocessor input')

    def test_code_java_1(self):
        test_file = self.get_test_loc('contenttype/code/java/contenttype.java')
        assert not is_binary(test_file)
        assert 'java source, ascii text' == get_filetype(test_file)
        assert 'Java' == get_filetype_pygment(test_file)

    def test_code_java_non_ascii(self):
        test_file = self.get_test_loc('contenttype/code/java/ChartTiming1.java')
        assert is_source(test_file)
        assert is_text(test_file)
        # FIXME: incorrect
        assert 'application/octet-stream' == get_mimetype_file(test_file)
        assert 'data' == get_filetype(test_file)
        assert 'Java' == get_filetype_pygment(test_file)

    def test_code_java_3(self):
        test_file = self.get_test_loc('contenttype/code/java/Appender.java')
        assert 'java source, ascii text' == get_filetype(test_file)
        assert 'Java' == get_filetype_pygment(test_file)

    def test_code_java_jad(self):
        test_file = self.get_test_loc('contenttype/code/java/CommonViewerSiteFactory.jad')
        assert 'java source, ascii text' == get_filetype(test_file)

    @expectedFailure
    def test_code_java_jad_pygment(self):
        test_file = self.get_test_loc('contenttype/code/java/CommonViewerSiteFactory.jad')
        # This should this be Java code?
        assert 'Java' == get_filetype_pygment(test_file)

    def test_code_java_mixed_case(self):
        test_file = self.get_test_loc('contenttype/code/java/Logger.JAVA')
        assert 'java source, ascii text' == get_filetype(test_file)
        assert 'Java' == get_filetype_pygment(test_file)

    def test_code_js(self):
        test_file = self.get_test_loc('contenttype/code/js/a.js')
        assert not is_media(test_file)
        assert 'ascii text, with crlf line terminators' == get_filetype(test_file)
        assert 'JavaScript' == get_filetype_pygment(test_file)

    def test_code_python_1(self):
        test_file = self.get_test_loc('contenttype/code/python/contenttype.py')
        assert not is_binary(test_file)
        assert 'Python' == get_pygments_lexer(test_file).name
        assert 'Python' == get_filetype_pygment(test_file)

    def test_code_python_2(self):
        test_file = self.get_test_loc('contenttype/code/python/extract.py')
        assert is_source(test_file)
        assert is_text(test_file)
        assert 'Python' == get_filetype_pygment(test_file)
        assert 'python script, ascii text executable' == get_filetype(test_file)
        assert 'text/x-python' == get_mimetype_file(test_file)
        assert get_filetype_file(test_file).startswith('Python script')

    def test_code_python_3(self):
        test_file = self.get_test_loc('contenttype/code/python/__init__.py')
        assert 'python script, ascii text executable' == get_filetype(test_file)
        assert 'Python' == get_filetype_pygment(test_file)

    def test_code_resource(self):
        test_file = self.get_test_loc('contenttype/code/c/CcccDevStudioAddIn.rc2')
        assert 'ascii text' == get_filetype(test_file)
        assert 'C' == get_filetype_pygment(test_file)

    def test_code_scala(self):
        test_file = self.get_test_loc('contenttype/code/scala/Applicative.scala')
        assert 'utf-8 unicode text' == get_filetype(test_file)
        assert 'Scala' == get_filetype_pygment(test_file)

    def test_compiled_elf_exe_32bits(self):
        test_file = self.get_test_loc('contenttype/compiled/linux/i686-shash')
        assert is_binary(test_file)
        expected = (
            'elf 32-bit lsb executable, intel 80386, version 1 (sysv), '
            'dynamically linked, interpreter /lib/ld-linux.so.2, '
            'for gnu/linux 2.6.4, with debug_info, not stripped')
        assert expected == get_filetype(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_compiled_elf_exe_64bits(self):
        test_file = self.get_test_loc('contenttype/compiled/linux/x86_64-shash')
        assert is_binary(test_file)
        assert '' == get_filetype_pygment(test_file)
        assert (
            'elf 64-bit lsb executable, x86-64, version 1 (sysv), '
            'dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, '
            'for gnu/linux 2.6.9, not stripped') == get_filetype(test_file)

    def test_compiled_elf_so(self):
        test_file = self.get_test_loc(u'contenttype/compiled/linux/libssl.so.0.9.7')
        assert not is_special(test_file)
        assert not is_text(test_file)
        assert '' == get_filetype_pygment(test_file)
        assert 'application/x-sharedlib' == get_mimetype_file(test_file)
        assert 'elf 32-bit lsb shared object, intel 80386, version 1 (sysv), statically linked, stripped' == get_filetype(test_file)
        assert 'ELF 32-bit LSB shared object, Intel 80386, version 1 (SYSV), statically linked, stripped' == get_filetype_file(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_compiled_elf_so_2(self):
        test_file = self.get_test_loc('contenttype/compiled/linux/libnetsnmpagent.so.5')
        assert not is_source(test_file)
        expected = 'elf 32-bit lsb shared object, intel 80386, version 1 (sysv), statically linked, with debug_info, not stripped'
        assert expected == get_filetype(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_compiled_flash(self):
        test_file = self.get_test_loc('contenttype/compiled/flash/a.swf')
        assert is_binary(test_file)
        assert 'macromedia flash data, version 7' == get_filetype(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_compiled_flash_2(self):
        test_file = self.get_test_loc('contenttype/compiled/flash/b.swf')
        assert is_binary(test_file)
        assert 'macromedia flash data, version 7' == get_filetype(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_compiled_flash_swc(self):
        test_file = self.get_test_loc('contenttype/compiled/flash/flash-haloclassic.swc.incr')
        assert is_binary(test_file)
        assert 'data' == get_filetype(test_file)
        assert '' == get_filetype_pygment(test_file)

    @pytest.mark.xfail(on_mac, reason='Somehow we get really weird results on macOS with libmagic 5.38: '
       '[64-bit architecture=6893422] [64-bit architecture=6649701] [architecture=1075809] [architecture=3959150] [architecture=768]')
    def test_compiled_java_classfile_1(self):
        test_file = self.get_test_loc('contenttype/compiled/java/CommonViewerSiteFactory.class')
        assert 'compiled java class data, version 46.0 (java 1.2)' == get_filetype(test_file)
        assert '' == get_filetype_pygment(test_file)

    @pytest.mark.xfail(on_mac, reason='Somehow we get really weird results on macOS with libmagic 5.38: '
       '[64-bit architecture=6893422] [64-bit architecture=6649701] [architecture=1075809] [architecture=3959150] [architecture=768]')
    def test_compiled_java_classfile_2(self):
        test_file = self.get_test_loc('contenttype/compiled/java/old.class')
        assert is_binary(test_file)
        assert 'compiled java class data, version 46.0 (java 1.2)' == get_filetype(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_compiled_python_1(self):
        test_dir = self.extract_test_zip('contenttype/compiled/python/compiled.zip')
        test_file = os.path.join(test_dir, 'command.pyc')
        assert 'python 2.5 byte-compiled' == get_filetype(test_file)
        assert not is_source(test_file)
        assert not is_text(test_file)
        assert 'application/octet-stream' == get_mimetype_file(test_file)
        assert '' == get_filetype_pygment(test_file)

        test_file2 = os.path.join(test_dir, 'contenttype.pyc')
        assert is_binary(test_file2)
        assert get_pygments_lexer(test_file2) is None

        test_file3 = os.path.join(test_dir, 'contenttype.pyo')
        assert is_binary(test_file3)
        assert get_pygments_lexer(test_file3) is None

        test_file4 = os.path.join(test_dir, 'extract.pyc')
        assert 'python 2.5 byte-compiled' == get_filetype(test_file4)
        assert not is_source(test_file4)
        assert not is_text(test_file4)
        assert 'application/octet-stream' == get_mimetype_file(test_file4)
        assert '' == get_filetype_pygment(test_file4)

    def test_compiled_win_dll(self):
        test_file = self.get_test_loc(u'contenttype/compiled/win/zlib1.dll')
        assert is_winexe(test_file)
        assert is_binary(self.get_test_loc('contenttype/compiled/win/zlib1.dll'))
        assert '' == get_filetype_pygment(test_file)

    def test_compiled_win_exe(self):
        test_file = self.get_test_loc(u'contenttype/compiled/win/file.exe')
        assert is_winexe(test_file)
        assert is_binary(self.get_test_loc('contenttype/compiled/win/file.exe'))
        assert '' == get_filetype_pygment(test_file)

    def test_config_conf(self):
        test_file = self.get_test_loc('contenttype/config/config.conf')
        assert 'ascii text, with crlf line terminators' == get_filetype(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_config_linux_conf(self):
        test_file = self.get_test_loc('contenttype/config/defconfig-ar531x-jffs2')
        assert 'linux make config build file (old)' == get_filetype(test_file)
        assert not is_source(test_file)
        assert is_text(test_file)
        assert '' == get_filetype_pygment(test_file)
        assert 'linux make config build file (old)' == get_filetype(test_file)
        assert 'text/plain' == get_mimetype_file(test_file)

    def test_config_text_3(self):
        test_file = self.get_test_loc('contenttype/config/wrapper.conf')
        assert 'ascii text, with crlf line terminators' == get_filetype(test_file)
        assert 'ascii text, with crlf line terminators' == get_filetype(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_debug_win_pdb(self):
        test_file = self.get_test_loc('contenttype/debug/QTMovieWin.pdb')
        assert is_binary(test_file)
        assert 'msvc program database ver 7.00, 1024*843 bytes' == get_filetype(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_doc_html(self):
        test_file = self.get_test_loc('contenttype/doc/html/contenttype.html')
        assert not is_binary(test_file)
        assert 'HTML' == get_pygments_lexer(test_file).name

    def test_doc_html_2(self):
        test_file = self.get_test_loc('contenttype/doc/html/allclasses-frame.html')
        assert is_source(test_file)
        assert is_text(test_file)
        assert 'HTML' == get_filetype_pygment(test_file)
        assert 'html document, ascii text' == get_filetype(test_file)
        assert 'text/html' == get_mimetype_file(test_file)
        assert 'HTML document, ASCII text' == get_filetype_file(test_file)

    def test_doc_html_3(self):
        test_file = self.get_test_loc('contenttype/doc/html/Label.html')
        assert is_source(test_file)
        assert is_text(test_file)
        assert 'HTML' == get_filetype_pygment(test_file)
        assert 'html document, ascii text, with very long lines' == get_filetype(test_file)
        assert 'text/html' == get_mimetype_file(test_file)
        assert 'HTML document, ASCII text, with very long lines' == get_filetype_file(test_file)

    def test_doc_html_4(self):
        test_file = self.get_test_loc('contenttype/doc/html/a.htm')
        assert not is_binary(test_file)
        assert not is_binary(test_file)
        assert 'HTML' == get_pygments_lexer(test_file).name

    def test_doc_office_word_docx_2007_without_extension(self):
        test_file = self.get_test_loc('contenttype/doc/office/document')
        assert is_archive(test_file)
        assert 'microsoft word 2007+' == get_filetype(test_file)

    def test_doc_office_word_docx_2007_with_incorrect_extension(self):
        test_file = self.get_test_loc('contenttype/doc/office/document.doc')
        assert is_archive(test_file)
        assert 'microsoft word 2007+' == get_filetype(test_file)

    def test_doc_office_msword_ole(self):
        test_file = self.get_test_loc('contenttype/doc/office/word.doc')
        assert not is_special(test_file)
        assert '' == get_filetype_pygment(test_file)
        assert 'application/msword' == get_mimetype_file(test_file)
        assert get_filetype(test_file).startswith('composite document file v2 document')
        assert get_filetype_file(test_file).startswith('Composite Document File V2 Document')

    def test_doc_office_word_docx_2007(self):
        test_file = self.get_test_loc('contenttype/doc/office/word.docx')
        assert 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' == get_mimetype_file(test_file)
        assert 'microsoft word 2007+' == get_filetype(test_file)
        assert is_archive(test_file)
        assert is_compressed(test_file)
        assert not contains_text(test_file)

    def test_doc_office_excel_xlsx(self):
        test_file = self.get_test_loc('contenttype/doc/office/excel.xlsx')
        assert 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' == get_mimetype_file(test_file)
        assert 'microsoft excel 2007+' == get_filetype(test_file)
        assert is_archive(test_file)
        assert is_compressed(test_file)
        assert not contains_text(test_file)

    def test_doc_office_excel_xls(self):
        test_file = self.get_test_loc('contenttype/doc/office/excel.xls')
        assert 'application/vnd.ms-excel' == get_mimetype_file(test_file)
        ft = get_filetype(test_file)
        assert ft.startswith('composite document file v2 document')
        assert 'microsoft excel' in ft

    def test_doc_office_pptx_is_archive(self):
        test_file = self.get_test_loc('contenttype/doc/office/power.pptx')
        assert 'application/vnd.openxmlformats-officedocument.presentationml.presentation' == get_mimetype_file(test_file)
        assert 'microsoft powerpoint 2007+' == get_filetype(test_file)
        assert is_archive(test_file)
        assert is_compressed(test_file)
        assert not contains_text(test_file)

    def test_doc_office_powerpoint_ppt(self):
        test_file = self.get_test_loc('contenttype/doc/office/power.ppt')
        assert 'application/vnd.ms-powerpoint' == get_mimetype_file(test_file)
        ft = get_filetype(test_file)
        assert ft.startswith('composite document file v2 document')
        assert 'microsoft office powerpoint' in ft

    def test_doc_office_visio(self):
        test_file = self.get_test_loc('contenttype/doc/office/Glitch-ERD.vsd')
        assert 'application/vnd.ms-office' == get_mimetype_file(test_file)
        assert not is_text(test_file)
        assert is_binary(test_file)
        ft = get_filetype(test_file)
        assert ft.startswith('composite document file v2 document')
        assert 'microsoft visio' in ft

    def test_doc_pdf_1(self):
        test_file = self.get_test_loc('contenttype/doc/pdf/a.pdf')
        assert is_pdf(test_file)
        assert is_pdf_with_text(test_file)
        assert 'pdf document, version 1.2' == get_filetype(test_file)
        assert not is_media(test_file)
        assert is_binary(test_file)

    def test_doc_pdf_2(self):
        test_file = self.get_test_loc('contenttype/doc/pdf/notpdf.pdf')
        assert not is_pdf_with_text(test_file)

    def test_doc_pdf_3(self):
        test_file = self.get_test_loc('contenttype/doc/pdf/pdf.pdf')
        assert is_pdf(test_file)
        assert is_pdf_with_text(test_file)
        assert 'pdf document, version 1.4' == get_filetype(test_file)

    def test_doc_postscript_1(self):
        test_file = self.get_test_loc('contenttype/doc/postscript/doc.ps')
        assert is_text(test_file)
        assert not is_binary(test_file)

    def test_doc_postscript_2(self):
        test_file = self.get_test_loc('contenttype/doc/postscript/a.ps')
        assert not is_binary(test_file)
        assert not is_media(test_file)

    # @pytest.mark.xfail(on_windows or on_mac, reason='Somehow we have incorrect results on win63 with libmagic 5.38: '
    #   'application/octet-stream instead of EPS')
    def test_doc_postscript_eps(self):
        test_file = self.get_test_loc('contenttype/doc/postscript/Image1.eps')
        assert is_binary(test_file)

        results = dict(
            get_filetype_file=get_filetype_file(test_file),
            get_mimetype_file=get_mimetype_file(test_file),
        )
        if on_windows:
            expected = dict(
                get_filetype_file='DOS EPS Binary File Postscript starts at byte 32 length 466 TIFF starts at byte 498 length 11890',
                get_mimetype_file='application/octet-stream',
            )
        else:
            expected = dict(
                get_filetype_file='DOS EPS Binary File Postscript starts at byte 32 length 466 TIFF starts at byte 498 length 11890',
                get_mimetype_file='image/x-eps',
            )
        assert expected == results

    def test_doc_xml(self):
        test_file = self.get_test_loc('contenttype/doc/xml/simple.xml')
        assert not is_binary(test_file)
        assert 'ascii text' == get_filetype(test_file)

    def test_doc_xml_2(self):
        test_file = self.get_test_loc('contenttype/doc/xml/some.xml')
        assert not is_binary(test_file)
        assert 'xml 1.0 document, ascii text, with crlf line terminators' == get_filetype(test_file)

    def test_doc_xml_3(self):
        test_file = self.get_test_loc('contenttype/doc/xml/somespring.xml')
        assert not is_binary(test_file)
        assert 'xml xxx document, ascii text, with crlf line terminators' == get_filetype(test_file)

    def test_media_audio_aif(self):
        test_file = self.get_test_loc('contenttype/media/a.aif')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_audio_aif2(self):
        test_file = self.get_test_loc('contenttype/media/a.aiff')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_audio_au(self):
        test_file = self.get_test_loc('contenttype/media/a.au')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_audio_flac(self):
        test_file = self.get_test_loc('contenttype/media/a.flac')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_audio_mp3(self):
        test_file = self.get_test_loc('contenttype/media/a.mp3')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_audio_wav(self):
        test_file = self.get_test_loc('contenttype/media/a.wav')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_image_bmp_1(self):
        test_file = self.get_test_loc('contenttype/media/Image1.bmp')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_image_bmp_2(self):
        test_file = self.get_test_loc('contenttype/media/TBarLrge.bmp')
        expected = 'pc bitmap, windows 3.x format, 400 x 32 x 4'
        assert get_filetype(test_file).startswith(expected)
        assert not contains_text(test_file)

    def test_media_image_bmp_3(self):
        test_file = self.get_test_loc('contenttype/media/TBarMedm.bmp')
        expected = 'pc bitmap, windows 3.x format, 210 x 16 x 4'
        assert get_filetype(test_file).startswith(expected)
        assert not contains_text(test_file)

    def test_media_image_dib(self):
        test_file = self.get_test_loc('contenttype/media/Image1.dib')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_image_gif(self):
        test_file = self.get_test_loc('contenttype/media/Image1.gif')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_image_ico(self):
        test_file = self.get_test_loc('contenttype/media/Image1.ico')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_image_iff(self):
        test_file = self.get_test_loc('contenttype/media/Image1.iff')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_image_img(self):
        # FIXME: .img files are more complex
        test_file = self.get_test_loc('contenttype/media/Image1.img')
        assert is_binary(test_file)
        assert get_filetype_file(test_file).startswith('GEM Image data')
        assert 'image/x-gem' == get_mimetype_file(test_file)
        assert not get_mimetype_python(test_file)
        assert is_media(test_file)
        assert not is_text(test_file)
        assert not is_archive(test_file)
        assert not contains_text(test_file)

    def test_media_image_jif(self):
        test_file = self.get_test_loc('contenttype/media/Image1.jif')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_image_jpeg(self):
        test_file = self.get_test_loc('contenttype/media/Image1.jpeg')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_image_jpg(self):
        test_file = self.get_test_loc('contenttype/media/Image1.jpg')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_image_pbm(self):
        test_file = self.get_test_loc('contenttype/media/Image1.pbm')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_image_ppm(self):
        # this is text-like
        test_file = self.get_test_loc('contenttype/media/Image1.ppm')
        assert is_binary(test_file)
        assert is_media(test_file)
        assert not contains_text(test_file)

    def test_media_image_pcx(self):
        test_file = self.get_test_loc('contenttype/media/Image1.pcx')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_image_photoshop(self):
        test_file = self.get_test_loc('contenttype/media/Image1.psd')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_image_png(self):
        test_file = self.get_test_loc('contenttype/media/a.png')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_image_pgm(self):
        test_file = self.get_test_loc('contenttype/media/Image.pgm')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_image_pgm_ascii(self):
        test_file = self.get_test_loc('contenttype/media/Image-ascii.pgm')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_image_psp(self):
        test_file = self.get_test_loc('contenttype/media/Image1.psp')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_image_ras(self):
        test_file = self.get_test_loc('contenttype/media/Image1.ras')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_image_svg(self):
        test_file = self.get_test_loc('contenttype/media/drawing.svg')
        assert not is_binary(test_file)
        assert is_media(test_file)
        assert '' == get_filetype_pygment(test_file)
        assert 'SVG Scalable Vector Graphics image' == get_filetype_file(test_file)
        assert not is_source(test_file)
        assert contains_text(test_file)

    def test_media_image_tga(self):
        test_file = self.get_test_loc('contenttype/media/Image1.tga')
        assert is_media(test_file), repr(get_type(test_file))
        assert is_binary(test_file), repr(get_type(test_file))
        assert not contains_text(test_file)

    def test_media_image_tif(self):
        test_file = self.get_test_loc('contenttype/media/Image1.tif')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_image_windows_metafile(self):
        test_file = self.get_test_loc('contenttype/media/Image1.emf')
        assert 'application/octet-stream' == get_mimetype_file(test_file)
        assert get_filetype_file(test_file).startswith('Windows Enhanced Metafile')
        assert not get_mimetype_python(test_file)
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_video_mpeg(self):
        test_file = self.get_test_loc('contenttype/media/a4.mp4')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_video_mpg(self):
        test_file = self.get_test_loc('contenttype/media/a4.mpg')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_video_mp2(self):
        test_file = self.get_test_loc('contenttype/media/a.mp2')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_video_msft_avi(self):
        test_file = self.get_test_loc('contenttype/media/a.avi')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_video_msft_wmf(self):
        test_file = self.get_test_loc('contenttype/media/Image1.wmf')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_video_msft_wmv1(self):
        test_file = self.get_test_loc('contenttype/media/mov.wvm.wmv')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_video_msft_wmv2(self):
        test_file = self.get_test_loc('contenttype/media/Movie.wmv')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_video_msft_wmv3(self):
        test_file = self.get_test_loc('contenttype/media/Movie_0001.wmv')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_video_msft_wmv4(self):
        test_file = self.get_test_loc('contenttype/media/Movie_0002.wmv')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_video_ogg(self):
        test_file = self.get_test_loc('contenttype/media/a.ogg')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_media_video_theora_ogg(self):
        test_file = self.get_test_loc('contenttype/media/a.theo.ogg')
        assert is_media(test_file)
        assert is_binary(test_file)
        assert not contains_text(test_file)

    def test_package_debian(self):
        test_file = self.get_test_loc('contenttype/package/wget-el_0.5.0-8_all.deb')
        expected = 'debian binary package (format 2.0), with control.tar.gz, data compression gz'
        assert expected == get_filetype(test_file)
        assert is_binary(test_file)
        assert is_archive(test_file)
        assert not contains_text(test_file)

    def test_package_java_jar(self):
        test_file = self.get_test_loc('contenttype/package/ant-jsch-1.7.0.jar')
        assert 'java archive data (jar)' == get_filetype(test_file)
        assert is_binary(test_file)
        assert is_compressed(test_file)
        assert is_archive(test_file)
        assert not contains_text(test_file)

    def test_package_java_jar_as_zip(self):
        test_file = self.get_test_loc('contenttype/package/ant.zip')
        assert 'java archive data (jar)' == get_filetype(test_file)
        assert is_binary(test_file)
        assert is_compressed(test_file)
        assert is_archive(test_file)
        assert not contains_text(test_file)

    def test_package_java_war(self):
        test_file = self.get_test_loc('contenttype/package/c.war')
        assert 'zip archive data, at least v1.0 to extract' == get_filetype(test_file)
        assert is_binary(test_file)
        assert is_compressed(test_file)
        assert is_archive(test_file)
        assert not contains_text(test_file)

    def test_package_python_egg(self):
        test_file = self.get_test_loc('contenttype/package/TicketImport-0.7a-py2.5.egg')
        assert 'zip archive data, at least v2.0 to extract' == get_filetype(test_file)
        assert is_binary(test_file)
        assert is_compressed(test_file)
        assert is_archive(test_file)
        assert not contains_text(test_file)

    def test_package_rpm(self):
        test_file = self.get_test_loc('contenttype/package/wget-1.11.4-3.fc11.i586.rpm')
        assert 'rpm v3.0 bin i386/x86_64' == get_filetype(test_file)
        assert is_binary(test_file)
        assert is_archive(test_file)
        assert is_compressed(test_file)
        assert not contains_text(test_file)

    def test_package_rubygem(self):
        test_file = self.get_test_loc('contenttype/package/rubygems-update-1.4.1.gem')
        assert 'posix tar archive' == get_filetype(test_file)
        assert is_binary(test_file)
        assert is_compressed(test_file)
        assert is_archive(test_file)
        assert not contains_text(test_file)

    def test_script_bash(self):
        test_file = self.get_test_loc('contenttype/script/test.sh')
        assert 'posix shell script, ascii text executable' == get_filetype(test_file)
        assert 'Bash' == get_filetype_pygment(test_file)

    def test_script_bash_makelinks(self):
        test_file = self.get_test_loc('contenttype/script/makelinks')
        assert is_source(test_file)
        assert 'Bash' == get_filetype_pygment(test_file)

    def test_script_windows_bat(self):
        test_file = self.get_test_loc('contenttype/script/build_w32vc.bat')
        assert 'dos batch file, ascii text' == get_filetype(test_file)
        assert 'Batchfile' == get_filetype_pygment(test_file)

    def test_script_windows_bat_2(self):
        test_file = self.get_test_loc('contenttype/script/zip_src.bat')
        assert 'ascii text, with crlf line terminators' == get_filetype(test_file)
        assert 'Batchfile' == get_filetype_pygment(test_file)

    def test_script_install(self):
        test_file = self.get_test_loc('contenttype/script/install')
        assert 'ascii text' == get_filetype(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_text_crashing(self):
        # these used to make libmagic crash somehow
        test_file = self.get_test_loc('contenttype/text/crashing-a.txt')
        assert 'ASCII text' == get_filetype_file(test_file)
        test_file = self.get_test_loc('contenttype/text/crashing-z.txt')
        assert 'ASCII text' == get_filetype_file(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_text(self):
        test_file = self.get_test_loc('contenttype/text/x11-xconsortium_text.txt')
        assert not is_binary(test_file)
        assert not is_archive(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_text_license_copying(self):
        test_file = self.get_test_loc('contenttype/text/COPYING')
        assert 'ascii text' in get_filetype(test_file)
        assert not is_source(test_file)
        assert is_text(test_file)
        assert '' == get_filetype_pygment(test_file)
        assert 'text/plain' == get_mimetype_file(test_file)

    def test_text_license_credits(self):
        # FIXME
        test_file = self.get_test_loc('contenttype/text/CREDITS')
        assert 'iso-8859 text' == get_filetype(test_file)
        assert is_text(test_file)
        assert not is_source(test_file)
        assert '' == get_filetype_pygment(test_file)
        assert 'ISO-8859 text' == get_filetype_file(test_file)
        assert 'text/plain' == get_mimetype_file(test_file)

    def test_text_license_gpl(self):
        test_file = self.get_test_loc('contenttype/text/GPL.txt')
        assert not is_source(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_text_log(self):
        test_file = self.get_test_loc('contenttype/text/windowserver.log')
        assert not is_source(test_file)
        assert is_text(test_file)
        assert '' == get_filetype_pygment(test_file)
        assert 'ascii text' == get_filetype(test_file)
        assert 'ASCII text' == get_filetype_file(test_file)
        assert 'text/plain' == get_mimetype_file(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_is_standard_include(self):
        assert is_standard_include('<built-in>')
        assert is_standard_include('/usr/lib/this.h')
        assert is_standard_include('/usr/include/this.h')

    def test_text_iso_text_changelog_is_not_iso_cdrom(self):
        test_file = self.get_test_loc('contenttype/text/ChangeLog')
        assert 'Non-ISO extended-ASCII text' == get_filetype_file(test_file)
        assert '' == get_filetype_pygment(test_file)

    @expectedFailure
    def test_text_rsync_file_is_not_octet_stream(self):
        # this is a libmagic bug: http://bugs.gw.com/view.php?id=473
        test_file = self.get_test_loc('contenttype/text/wildtest.txt')
        assert 'data' != get_filetype_file(test_file)
        assert 'octet' not in get_mimetype_file(test_file)

    def test_rgb_stream_is_binary(self):
        # this is a binaryornot bug: https://github.com/audreyr/binaryornot/issues/10
        test_file = self.get_test_loc('contenttype/binary/pixelstream.rgb')
        assert 'data' == get_filetype_file(test_file)
        assert 'application/octet-stream' == get_mimetype_file(test_file)
        assert is_binary(test_file)
        assert is_data(test_file)

    def test_large_text_file_is_data(self):
        test_file = self.get_test_loc('contenttype/data/nulls.txt')
        assert is_data(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_is_data_for_mysql1(self):
        test_file = self.get_test_loc('contenttype/data/mysql-arch')
        assert contenttype_is_data(test_file)
        assert is_data(test_file)

    def test_is_data_for_mysql2(self):
        test_file = self.get_test_loc('contenttype/data/mysql-arch.ARM')
        assert contenttype_is_data(test_file)
        assert is_data(test_file)

    def test_is_data_for_mysql3(self):
        test_file = self.get_test_loc('contenttype/data/mysql-arch.ARN')
        assert contenttype_is_data(test_file)
        assert is_data(test_file)

    def test_is_data_for_mysql4(self):
        test_file = self.get_test_loc('contenttype/data/mysql-arch.ARZ')
        assert contenttype_is_data(test_file)
        assert is_data(test_file)

    def test_is_js_map_for_css(self):
        test_file = self.get_test_loc('contenttype/build/ar-ER.css.map')
        assert is_js_map(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_is_js_map_for_js(self):
        test_file = self.get_test_loc('contenttype/build/ar-ER.js.map')
        assert is_js_map(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_is_js_map_for_binary(self):
        test_file = self.get_test_loc('contenttype/build/binary.js.map')
        assert not is_js_map(test_file)
        assert '' == get_filetype_pygment(test_file)

    def test_is_js_map_for_makefile(self):
        test_file = self.get_test_loc('contenttype/build/Makefile')
        assert not is_js_map(test_file)
        assert '' == get_filetype_pygment(test_file)
