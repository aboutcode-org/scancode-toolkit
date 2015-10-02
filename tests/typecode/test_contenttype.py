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

from __future__ import absolute_import, print_function, unicode_literals

import os

from unittest.case import skipIf
from unittest.case import expectedFailure

from commoncode.testcase import FileBasedTesting
from commoncode.system import on_windows

from typecode.contenttype import get_filetype
from typecode.contenttype import get_type
from typecode.contenttype import get_pygments_lexer
from typecode.contenttype import is_standard_include


# aliases for testing
get_mimetype_python = lambda l: get_type(l).mimetype_python
get_filetype_pygment = lambda l: get_type(l).filetype_pygment
get_filetype_file = lambda l: get_type(l).filetype_file
get_mimetype_file = lambda l: get_type(l).mimetype_file
is_text = lambda l: get_type(l).is_text
is_archive = lambda l: get_type(l).is_archive
is_media = lambda l: get_type(l).is_media
is_winexe = lambda l: get_type(l).is_winexe
is_source = lambda l: get_type(l).is_source
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
        if on_windows:
            # FIXME: this is a very short png file though
            expected = 'Non-ISO extended-ASCII text'
        assert expected == get_filetype_file(test_file)

        expected = 'image/png'
        if on_windows:
            # FIXME: this is a very short png file though
            expected = 'text/plain'
        assert expected == get_mimetype_file(test_file)

    @expectedFailure
    def test_filetype_file_on_unicode_file_name2(self):
        test_dir = self.get_test_loc('contenttype/unicode/')
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

        assert is_link(os.path.join(test_dir, 'prunedirs/targets/simlink_to_dir'))
        assert is_link(os.path.join(test_dir, 'prunedirs/targets/simlink_to_file'))
        assert not is_broken_link(os.path.join(test_dir, 'prunedirs/targets/simlink_to_dir'))
        assert not is_broken_link(os.path.join(test_dir, 'prunedirs/targets/simlink_to_file'))
        assert '../sources/subdir' == get_link_target(os.path.join(test_dir, 'prunedirs/targets/simlink_to_dir'))
        assert '../sources/a.txt' == get_link_target(os.path.join(test_dir, 'prunedirs/targets/simlink_to_file'))

        assert is_link(os.path.join(test_dir, 'prunedirs/targets/simlink_to_missing_file'))
        assert is_link(os.path.join(test_dir, 'prunedirs/targets/simlink_to_missing_dir'))
        assert is_broken_link(os.path.join(test_dir, 'prunedirs/targets/simlink_to_missing_file'))
        assert is_broken_link(os.path.join(test_dir, 'prunedirs/targets/simlink_to_missing_dir'))
        assert '../sources/temp.txt' == get_link_target(os.path.join(test_dir, 'prunedirs/targets/simlink_to_missing_file'))
        assert '../sources/tempdir' == get_link_target(os.path.join(test_dir, 'prunedirs/targets/simlink_to_missing_dir'))


    @skipIf(not on_windows, 'Hangs for now, for mysterious reasons.')
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
        assert not is_binary(self.get_test_loc('contenttype'))

    def test_archive_gnu_tar(self):
        assert is_binary(self.get_test_loc('contenttype/archive/e.tar'))
        assert is_archive(self.get_test_loc('contenttype/archive/e.tar'))
        assert 'posix tar archive (gnu)' == get_filetype(self.get_test_loc('contenttype/archive/e.tar'))

    def test_archive_gz(self):
        assert is_binary(self.get_test_loc('contenttype/archive/file_4.26-1.diff.gz'))
        assert is_archive(self.get_test_loc('contenttype/archive/file_4.26-1.diff.gz'))
        assert get_filetype(self.get_test_loc('contenttype/archive/file_4.26-1.diff.gz')).startswith('gzip compressed data')

    @skipIf(on_windows, 'fails because of libmagic bug on windows.')
    def test_archive_squashfs_crashing(self):
        test_file = self.get_test_loc('contenttype/archive/crashing-squashfs')
        assert get_filetype_file(test_file).startswith('Squashfs filesystem, little endian, version 4.0')

    @skipIf(on_windows, 'fails because of libmagic bug on windows.')
    def test_archive_squashfs_gz(self):
        test_file = self.get_test_loc('contenttype/archive/sqfs-gz.sqs')
        assert get_filetype_file(test_file).startswith('Squashfs filesystem, little endian, version 4.0')

    @skipIf(on_windows, 'fails because of libmagic bug on windows.')
    def test_archive_squashfs_lzo(self):
        test_file = self.get_test_loc('contenttype/archive/sqfs-lzo.sqs')
        assert get_filetype_file(test_file).startswith('Squashfs filesystem, little endian, version 4.0')

    @skipIf(on_windows, 'fails because of libmagic bug on windows.')
    def test_archive_squashfs_xz(self):
        test_file = self.get_test_loc('contenttype/archive/sqfs-xz.sqs')
        assert get_filetype_file(test_file).startswith('Squashfs filesystem, little endian, version 4.0')

    def test_archive_tar_bz2(self):
        assert is_binary(self.get_test_loc('contenttype/archive/e.tar.bz2'))
        assert is_archive(self.get_test_loc('contenttype/archive/e.tar.bz2'))
        assert 'bzip2 compressed data, block size = 900k' == get_filetype(self.get_test_loc('contenttype/archive/e.tar.bz2'))

    def test_archive_tar_gz_1(self):
        assert not is_source(self.get_test_loc('contenttype/archive/a.tar.gz'))
        assert not is_text(self.get_test_loc('contenttype/archive/a.tar.gz'))
        assert '' == get_filetype_pygment(self.get_test_loc('contenttype/archive/a.tar.gz'))
        assert 'application/x-gzip' == get_mimetype_file(self.get_test_loc('contenttype/archive/a.tar.gz'))
        assert get_filetype(self.get_test_loc('contenttype/archive/a.tar.gz')).startswith('gzip compressed data')

    def test_archive_tar_gz_3(self):
        assert is_binary(self.get_test_loc('contenttype/archive/e.tar.gz'))
        assert is_archive(self.get_test_loc('contenttype/archive/e.tar.gz'))
        assert get_filetype(self.get_test_loc('contenttype/archive/e.tar.gz')).startswith('gzip compressed data')

    def test_archive_tar_posix(self):
        assert is_binary(self.get_test_loc('contenttype/archive/posixnotgnu.tar'))
        assert is_archive(self.get_test_loc('contenttype/archive/posixnotgnu.tar'))
        assert 'posix tar archive' == get_filetype(self.get_test_loc('contenttype/archive/posixnotgnu.tar'))

    def test_config_eclipse_data(self):
        assert is_binary(self.get_test_loc('contenttype/config/eclipse_configuration_3u.cfs'))
        assert 'data' == get_filetype(self.get_test_loc('contenttype/config/eclipse_configuration_3u.cfs'))

    def test_binary_data(self):
        assert is_binary(self.get_test_loc('contenttype/binary/data.fdt'))
        assert 'data' == get_filetype(self.get_test_loc('contenttype/binary/data.fdt'))

    def test_binary_data_2(self):
        assert 'data' == get_filetype(self.get_test_loc('contenttype/binary/dbase.fdt'))

    def test_binary_java_serialized_data(self):
        assert is_binary(self.get_test_loc('contenttype/binary/jruby_time_zone_TimeOfDay.dat'))
        assert 'java serialization data, version 5' == get_filetype(self.get_test_loc('contenttype/binary/jruby_time_zone_TimeOfDay.dat'))

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

    def test_build_ant_build_xml(self):
        assert not is_binary(self.get_test_loc('contenttype/build/build.xml'))
        assert 'xml language text' == get_filetype(self.get_test_loc('contenttype/build/build.xml'))

    def test_build_makefile(self):
        assert is_source(self.get_test_loc('contenttype/build/Makefile'))
        assert is_text(self.get_test_loc('contenttype/build/Makefile'))
        assert 'Makefile' == get_filetype_pygment(self.get_test_loc('contenttype/build/Makefile'))
        assert 'ASCII text' == get_filetype_file(self.get_test_loc('contenttype/build/Makefile'))
        assert 'makefile language text' == get_filetype(self.get_test_loc('contenttype/build/Makefile'))
        assert 'text/plain' == get_mimetype_file(self.get_test_loc('contenttype/build/Makefile'))

    def test_build_makefile_2(self):
        assert is_source(self.get_test_loc('contenttype/build/Makefile.inc'))
        assert is_text(self.get_test_loc('contenttype/build/Makefile.inc'))
        assert 'text/x-makefile' == get_mimetype_file(self.get_test_loc('contenttype/build/Makefile.inc'))
        assert 'ASCII text' == get_filetype_file(self.get_test_loc('contenttype/build/Makefile'))

    @expectedFailure
    def test_build_makefile_inc_is_not_povray(self):
        assert 'Makefile' == get_filetype_pygment(self.get_test_loc('contenttype/build/Makefile.inc'))
        assert 'makefile language text' == get_filetype(self.get_test_loc('contenttype/build/Makefile.inc'))

    def test_build_ide_makefile(self):
        assert 'makefile language text' == get_filetype(self.get_test_loc('contenttype/build/documentation.dsp'))

    def test_build_java_maven_pom(self):
        assert not is_source(self.get_test_loc('contenttype/build/pom.pom'))

        assert is_source(self.get_test_loc('contenttype/build/pom.xml'))
        assert 'xml language text' == get_filetype(self.get_test_loc('contenttype/build/pom.xml'))

    def test_certificate_rsa_eclipse(self):
        assert is_binary(self.get_test_loc('contenttype/certificate/ECLIPSE.RSA'))
        assert 'data' == get_filetype(self.get_test_loc('contenttype/certificate/ECLIPSE.RSA'))

    def test_certificate(self):
        assert is_binary(self.get_test_loc('contenttype/certificate/CERTIFICATE'))
        assert 'data' == get_filetype(self.get_test_loc('contenttype/certificate/CERTIFICATE'))

    def test_code_assembly(self):
        assert 'C source, ASCII text, with CRLF line terminators' == get_filetype_file(self.get_test_loc('contenttype/code/assembly/bcopy.s'))
        assert 'GAS' == get_filetype_pygment(self.get_test_loc('contenttype/code/assembly/bcopy.s'))
        assert 'text/x-c' == get_mimetype_file(self.get_test_loc('contenttype/code/assembly/bcopy.s'))

    def test_code_c_1(self):
        assert 'c language text' == get_filetype(self.get_test_loc('contenttype/code/c/c_code.c'))

    def test_code_c_2(self):
        assert is_source(self.get_test_loc('contenttype/code/c/main.c'))
        assert is_text(self.get_test_loc('contenttype/code/c/main.c'))
        assert 'C' == get_filetype_pygment(self.get_test_loc('contenttype/code/c/main.c'))
        assert 'c language text' == get_filetype(self.get_test_loc('contenttype/code/c/main.c'))
        assert 'C source, ASCII text' == get_filetype_file(self.get_test_loc('contenttype/code/c/main.c'))
        assert 'text/x-c' == get_mimetype_file(self.get_test_loc('contenttype/code/c/main.c'))

    def test_code_c_3(self):
        assert is_source(self.get_test_loc('contenttype/code/c/cpu.c'))
        assert is_text(self.get_test_loc('contenttype/code/c/cpu.c'))
        assert 'C' == get_filetype_pygment(self.get_test_loc('contenttype/code/c/cpu.c'))
        assert 'c language text' == get_filetype(self.get_test_loc('contenttype/code/c/cpu.c'))
        assert 'text/x-c' == get_mimetype_file(self.get_test_loc('contenttype/code/c/cpu.c'))

    def test_code_c_4(self):
        assert is_source(self.get_test_loc('contenttype/code/c/mm.c'))
        assert is_text(self.get_test_loc('contenttype/code/c/mm.c'))
        assert 'C' == get_filetype_pygment(self.get_test_loc('contenttype/code/c/mm.c'))
        assert 'c language text' == get_filetype(self.get_test_loc('contenttype/code/c/mm.c'))
        assert 'text/x-c' == get_mimetype_file(self.get_test_loc('contenttype/code/c/mm.c'))

    def test_code_c_5(self):
        assert is_source(self.get_test_loc('contenttype/code/c/pci.c'))
        assert is_text(self.get_test_loc('contenttype/code/c/pci.c'))
        assert 'C source, ASCII text' == get_filetype_file(self.get_test_loc('contenttype/code/c/pci.c'))
        assert 'C' == get_filetype_pygment(self.get_test_loc('contenttype/code/c/pci.c'))
        assert 'c language text' == get_filetype(self.get_test_loc('contenttype/code/c/pci.c'))
        assert 'text/x-c' == get_mimetype_file(self.get_test_loc('contenttype/code/c/pci.c'))

    def test_code_c_6(self):
        assert is_source(self.get_test_loc('contenttype/code/c/pci_v3.c'))
        assert is_text(self.get_test_loc('contenttype/code/c/pci_v3.c'))
        assert 'C source, ASCII text' == get_filetype_file(self.get_test_loc('contenttype/code/c/pci_v3.c'))
        assert 'C' == get_filetype_pygment(self.get_test_loc('contenttype/code/c/pci_v3.c'))
        assert 'c language text' == get_filetype(self.get_test_loc('contenttype/code/c/pci_v3.c'))
        assert 'text/x-c' == get_mimetype_file(self.get_test_loc('contenttype/code/c/pci_v3.c'))

    def test_code_c_7(self):
        assert 'c language text' == get_filetype(self.get_test_loc('contenttype/code/c/some.c'))

    def test_code_c_include(self):
        assert 'c language text' == get_filetype(self.get_test_loc('contenttype/code/c/resource.h'))

        assert is_source(self.get_test_loc('contenttype/code/c/netdb.h'))

    def test_code_c_include_mixed_case(self):
        assert 'c++ language text' == get_filetype(self.get_test_loc('contenttype/code/c/TEST.H'))
        assert 'c language text' == get_filetype(self.get_test_loc('contenttype/code/c/TEST_LOWERCASE.h'))

    def test_code_c_mixed_case(self):
        assert 'c++ language text' == get_filetype(self.get_test_loc('contenttype/code/c/SIMPLE.C'))

    def test_code_cpp_1(self):
        assert is_source(self.get_test_loc('contenttype/code/cpp/stacktrace.cpp'))
        assert is_text(self.get_test_loc('contenttype/code/cpp/stacktrace.cpp'))
        assert 'C++' == get_filetype_pygment(self.get_test_loc('contenttype/code/cpp/stacktrace.cpp'))
        assert 'c++ language text' == get_filetype(self.get_test_loc('contenttype/code/cpp/stacktrace.cpp'))
        assert 'text/x-c' == get_mimetype_file(self.get_test_loc('contenttype/code/cpp/stacktrace.cpp'))

    def test_code_cpp_non_ascii(self):
        assert is_source(self.get_test_loc('contenttype/code/cpp/non_ascii.cpp'))
        assert is_text(self.get_test_loc('contenttype/code/cpp/non_ascii.cpp'))
        assert 'application/octet-stream' == get_mimetype_file(self.get_test_loc('contenttype/code/cpp/non_ascii.cpp'))
        assert 'C++' == get_filetype_pygment(self.get_test_loc('contenttype/code/cpp/non_ascii.cpp'))
        assert 'c++ language text' == get_filetype(self.get_test_loc('contenttype/code/cpp/non_ascii.cpp'))

    def test_code_cpp_stdafx(self):
        assert 'c++ language text' == get_filetype(self.get_test_loc('contenttype/code/cpp/StdAfx.cpp'))

    def test_code_cpp_mixed_case(self):
        assert 'c++ language text' == get_filetype(self.get_test_loc('contenttype/code/cpp/string.CPP'))
        assert 'c++ language text' == get_filetype(self.get_test_loc('contenttype/code/cpp/string.CPP'))

    def test_code_groff(self):
        assert not is_special(self.get_test_loc(u'contenttype/code/groff/example.ms'))
        assert is_text(self.get_test_loc(u'contenttype/code/groff/example.ms'))
        assert 'Groff' == get_filetype_pygment(self.get_test_loc(u'contenttype/code/groff/example.ms'))
        assert 'groff language text' == get_filetype(self.get_test_loc(u'contenttype/code/groff/example.ms'))
        assert 'text/troff' == get_mimetype_python(self.get_test_loc(u'contenttype/code/groff/example.ms'))
        assert 'text/troff' == get_mimetype_file(self.get_test_loc(u'contenttype/code/groff/example.ms'))
        assert get_filetype_file(self.get_test_loc(u'contenttype/code/groff/example.ms')).startswith('troff or preprocessor input')

    def test_code_java_1(self):
        assert not is_binary(self.get_test_loc('contenttype/code/java/contenttype.java'))
        assert 'Java' == get_pygments_lexer(self.get_test_loc('contenttype/code/java/contenttype.java')).name

    def test_code_java_non_ascii(self):
        assert is_source(self.get_test_loc('contenttype/code/java/ChartTiming1.java'))
        assert is_text(self.get_test_loc('contenttype/code/java/ChartTiming1.java'))
        # FIXME: incorrect
        assert 'application/octet-stream' == get_mimetype_file(self.get_test_loc('contenttype/code/java/ChartTiming1.java'))
        assert 'Java' == get_filetype_pygment(self.get_test_loc('contenttype/code/java/ChartTiming1.java'))
        assert 'java language text' == get_filetype(self.get_test_loc('contenttype/code/java/ChartTiming1.java'))

    def test_code_java_3(self):
        assert 'java language text' == get_filetype(self.get_test_loc('contenttype/code/java/Appender.java'))

    def test_code_java_jad(self):
        # FIXME: should this be Java code?
        assert 'python language text' == get_filetype(self.get_test_loc('contenttype/code/java/CommonViewerSiteFactory.jad'))

    def test_code_java_mixed_case(self):
        # FIXME: incorrect type
        assert 'python language text' == get_filetype(self.get_test_loc('contenttype/code/java/Logger.JAVA'))

    def test_code_js(self):
        assert not is_media(self.get_test_loc('contenttype/code/js/a.js'))

    def test_code_python_1(self):
        assert not is_binary(self.get_test_loc('contenttype/code/python/contenttype.py'))
        assert 'Python' == get_pygments_lexer(self.get_test_loc('contenttype/code/python/contenttype.py')).name

    def test_code_python_2(self):
        assert is_source(self.get_test_loc('contenttype/code/python/extract.py'))
        assert is_text(self.get_test_loc('contenttype/code/python/extract.py'))
        assert 'Python' == get_filetype_pygment(self.get_test_loc('contenttype/code/python/extract.py'))
        assert 'python language text' == get_filetype(self.get_test_loc('contenttype/code/python/extract.py'))
        assert 'text/x-python' == get_mimetype_file(self.get_test_loc('contenttype/code/python/extract.py'))
        assert get_filetype_file(self.get_test_loc('contenttype/code/python/extract.py')).startswith('Python script')

    def test_code_python_3(self):
        assert 'python language text' == get_filetype(self.get_test_loc('contenttype/code/python/__init__.py'))

    def test_code_resource(self):
        assert 'c language text' == get_filetype(self.get_test_loc('contenttype/code/c/CcccDevStudioAddIn.rc2'))

    def test_code_scala(self):
        assert 'scala language text' == get_filetype(self.get_test_loc('contenttype/code/scala/Applicative.scala'))

    def test_compiled_elf_exe(self):
        assert is_binary(self.get_test_loc('contenttype/compiled/linux/i686-shash'))
        assert 'elf 32-bit lsb executable, intel 80386, version 1 (sysv), dynamically linked, interpreter /lib/ld-linux.so.2, for gnu/linux 2.6.4, not stripped' == get_filetype(self.get_test_loc(u'contenttype/compiled/linux/i686-shash'))
        assert is_binary(self.get_test_loc('contenttype/compiled/linux/x86_64-shash'))
        assert 'elf 64-bit lsb executable, x86-64, version 1 (sysv), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for gnu/linux 2.6.9, not stripped' == get_filetype(self.get_test_loc(u'contenttype/compiled/linux/x86_64-shash'))

    def test_compiled_elf_so(self):
        assert not is_special(self.get_test_loc(u'contenttype/compiled/linux/libssl.so.0.9.7'))
        assert not is_text(self.get_test_loc(u'contenttype/compiled/linux/libssl.so.0.9.7'))
        assert '' == get_filetype_pygment(self.get_test_loc(u'contenttype/compiled/linux/libssl.so.0.9.7'))
        assert 'application/x-sharedlib' == get_mimetype_file(self.get_test_loc(u'contenttype/compiled/linux/libssl.so.0.9.7'))
        assert 'elf 32-bit lsb shared object, intel 80386, version 1 (sysv), dynamically linked, stripped' == get_filetype(self.get_test_loc(u'contenttype/compiled/linux/libssl.so.0.9.7'))
        assert 'ELF 32-bit LSB shared object, Intel 80386, version 1 (SYSV), dynamically linked, stripped' == get_filetype_file(self.get_test_loc(u'contenttype/compiled/linux/libssl.so.0.9.7'))

    def test_compiled_elf_so_2(self):
        assert not is_source(self.get_test_loc('contenttype/compiled/linux/libnetsnmpagent.so.5'))

    def test_compiled_flash(self):
        assert is_binary(self.get_test_loc('contenttype/compiled/flash/a.swf'))
        assert is_binary(self.get_test_loc('contenttype/compiled/flash/b.swf'))

    def test_compiled_flash_swc(self):
        assert is_binary(self.get_test_loc('contenttype/compiled/flash/flash-haloclassic.swc.incr'))
        assert 'data' == get_filetype(self.get_test_loc('contenttype/compiled/flash/flash-haloclassic.swc.incr'))

    def test_compiled_java(self):
        assert 'compiled java class data, version 46.0 (java 1.2)' == get_filetype(self.get_test_loc('contenttype/compiled/java/CommonViewerSiteFactory.class'))
        assert is_binary(self.get_test_loc('contenttype/compiled/java/old.class'))
        assert 'compiled java class data, version 46.0 (java 1.2)' == get_filetype(self.get_test_loc('contenttype/compiled/java/old.class'))

    def test_compiled_python_1(self):
        test_dir = self.extract_test_zip('contenttype/compiled/python/compiled.zip')
        assert 'python 2.5 byte-compiled' == get_filetype(os.path.join(test_dir, 'command.pyc'))
        assert not is_source(os.path.join(test_dir, 'command.pyc'))
        assert not is_text(os.path.join(test_dir, 'command.pyc'))
        assert 'application/octet-stream' == get_mimetype_file(os.path.join(test_dir, 'command.pyc'))
        assert '' == get_filetype_pygment(os.path.join(test_dir, 'command.pyc'))

    def test_compiled_python_2(self):
        test_dir = self.extract_test_zip('contenttype/compiled/python/compiled.zip')
        assert is_binary(os.path.join(test_dir, 'contenttype.pyc'))
        assert get_pygments_lexer(os.path.join(test_dir, 'contenttype.pyc')) is None

    def test_compiled_python_3(self):
        test_dir = self.extract_test_zip('contenttype/compiled/python/compiled.zip')
        assert is_binary(os.path.join(test_dir, 'contenttype.pyo'))
        assert get_pygments_lexer(os.path.join(test_dir, 'contenttype.pyo')) is None

    def test_compiled_python_4(self):
        test_dir = self.extract_test_zip('contenttype/compiled/python/compiled.zip')
        assert 'python 2.5 byte-compiled' == get_filetype(os.path.join(test_dir, 'extract.pyc'))
        assert not is_source(os.path.join(test_dir, 'extract.pyc'))
        assert not is_text(os.path.join(test_dir, 'extract.pyc'))
        assert 'application/octet-stream' == get_mimetype_file(os.path.join(test_dir, 'extract.pyc'))
        assert '' == get_filetype_pygment(os.path.join(test_dir, 'extract.pyc'))

    def test_compiled_win_dll(self):
        assert is_winexe(self.get_test_loc(u'contenttype/compiled/win/zlib1.dll'))
        assert is_binary(self.get_test_loc('contenttype/compiled/win/zlib1.dll'))

    def test_compiled_win_exe(self):
        assert is_winexe(self.get_test_loc(u'contenttype/compiled/win/file.exe'))
        assert is_binary(self.get_test_loc('contenttype/compiled/win/file.exe'))

    def test_config_conf(self):
        assert 'ascii text, with crlf line terminators' == get_filetype(self.get_test_loc('contenttype/config/config.conf'))

    def test_config_linux_conf(self):
        assert 'linux make config build file (old)' == get_filetype(self.get_test_loc('contenttype/config/defconfig-ar531x-jffs2'))

    def test_config_linux_conf_2(self):
        assert not is_source(self.get_test_loc('contenttype/config/defconfig-ar531x-jffs2'))
        assert is_text(self.get_test_loc('contenttype/config/defconfig-ar531x-jffs2'))
        assert '' == get_filetype_pygment(self.get_test_loc('contenttype/config/defconfig-ar531x-jffs2'))
        assert 'linux make config build file (old)' == get_filetype(self.get_test_loc('contenttype/config/defconfig-ar531x-jffs2'))
        assert 'text/plain' == get_mimetype_file(self.get_test_loc('contenttype/config/defconfig-ar531x-jffs2'))

    def test_config_text_3(self):
        assert 'ascii text, with crlf line terminators' == get_filetype(self.get_test_loc('contenttype/config/wrapper.conf'))
        assert 'ascii text, with crlf line terminators' == get_filetype(self.get_test_loc('contenttype/config/wrapper.conf'))

    def test_debug_win_pdb(self):
        assert is_binary(self.get_test_loc('contenttype/debug/QTMovieWin.pdb'))
        assert 'msvc program database ver \\004' == get_filetype(self.get_test_loc('contenttype/debug/QTMovieWin.pdb'))

    def test_doc_html(self):
        assert not is_binary(self.get_test_loc('contenttype/doc/html/contenttype.html'))
        assert 'HTML' == get_pygments_lexer(self.get_test_loc('contenttype/doc/html/contenttype.html')).name
        assert not is_binary(self.get_test_loc('contenttype/doc/html/a.htm'))

    def test_doc_html_2(self):
        assert is_source(self.get_test_loc('contenttype/doc/html/allclasses-frame.html'))
        assert is_text(self.get_test_loc('contenttype/doc/html/allclasses-frame.html'))
        assert 'HTML' == get_filetype_pygment(self.get_test_loc('contenttype/doc/html/allclasses-frame.html'))
        assert 'html language text' == get_filetype(self.get_test_loc('contenttype/doc/html/allclasses-frame.html'))
        assert 'text/html' == get_mimetype_file(self.get_test_loc('contenttype/doc/html/allclasses-frame.html'))
        assert 'HTML document, ASCII text' == get_filetype_file(self.get_test_loc('contenttype/doc/html/allclasses-frame.html'))

    def test_doc_html_3(self):
        assert is_source(self.get_test_loc('contenttype/doc/html/Label.html'))
        assert is_text(self.get_test_loc('contenttype/doc/html/Label.html'))
        assert 'HTML' == get_filetype_pygment(self.get_test_loc('contenttype/doc/html/Label.html'))
        assert 'html language text' == get_filetype(self.get_test_loc('contenttype/doc/html/Label.html'))
        assert 'text/html' == get_mimetype_file(self.get_test_loc('contenttype/doc/html/Label.html'))
        assert 'HTML document, ASCII text, with very long lines' == get_filetype_file(self.get_test_loc('contenttype/doc/html/Label.html'))

    @expectedFailure
    def test_doc_office_are_archives(self):
        assert is_archive(self.get_test_loc('contenttype/doc/office/document'))
        assert is_archive(self.get_test_loc('contenttype/doc/office/document.doc'))
        assert is_archive(self.get_test_loc('contenttype/doc/office/word.docx'))
        assert is_archive(self.get_test_loc('contenttype/doc/office/excel.xlsx'))
        assert is_archive(self.get_test_loc('contenttype/doc/office/power.pptx'))

    def test_doc_office_excel(self):
        assert 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' == get_mimetype_file(self.get_test_loc('contenttype/doc/office/excel.xlsx'))
        assert 'application/vnd.ms-excel' == get_mimetype_file(self.get_test_loc('contenttype/doc/office/excel.xls'))

    def test_doc_office_powerpoint(self):
        assert 'application/vnd.openxmlformats-officedocument.presentationml.presentation' == get_mimetype_file(self.get_test_loc('contenttype/doc/office/power.pptx'))
        assert 'application/vnd.ms-powerpoint' == get_mimetype_file(self.get_test_loc('contenttype/doc/office/power.ppt'))

    def test_doc_office_visio(self):
        assert 'application/vnd.ms-office' == get_mimetype_file(self.get_test_loc('contenttype/doc/office/Glitch-ERD.vsd'))
        assert not is_text(self.get_test_loc('contenttype/doc/office/Glitch-ERD.vsd'))
        assert is_binary(self.get_test_loc('contenttype/doc/office/Glitch-ERD.vsd'))

    def test_doc_office_word(self):
        assert 'microsoft word 2007+' == get_filetype(self.get_test_loc('contenttype/doc/office/document'))

        assert 'microsoft word 2007+' == get_filetype(self.get_test_loc('contenttype/doc/office/document.doc'))

        assert not is_special(self.get_test_loc('contenttype/doc/office/word.doc'))
        assert '' == get_filetype_pygment(self.get_test_loc('contenttype/doc/office/word.doc'))
        assert 'application/msword' == get_mimetype_file(self.get_test_loc('contenttype/doc/office/word.doc'))
        assert get_filetype(self.get_test_loc('contenttype/doc/office/word.doc')).startswith('composite document file v2 document')
        assert get_filetype_file(self.get_test_loc('contenttype/doc/office/word.doc')).startswith('Composite Document File V2 Document')

        assert 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' == get_mimetype_file(self.get_test_loc('contenttype/doc/office/word.docx'))

    def test_doc_pdf_1(self):
        assert is_pdf(self.get_test_loc('contenttype/doc/pdf/a.pdf'))
        assert is_pdf_with_text(self.get_test_loc('contenttype/doc/pdf/a.pdf'))
        assert 'pdf document, version 1.2' == get_filetype(self.get_test_loc('contenttype/doc/pdf/a.pdf'))
        assert not is_media(self.get_test_loc('contenttype/doc/pdf/a.pdf'))
        assert is_binary(self.get_test_loc('contenttype/doc/pdf/a.pdf'))

    def test_doc_pdf_2(self):
        assert not is_pdf_with_text(self.get_test_loc('contenttype/doc/pdf/notpdf.pdf'))

    def test_doc_pdf_3(self):
        assert is_pdf(self.get_test_loc('contenttype/doc/pdf/pdf.pdf'))
        assert is_pdf_with_text(self.get_test_loc('contenttype/doc/pdf/pdf.pdf'))
        assert 'pdf document, version 1.4' == get_filetype(self.get_test_loc('contenttype/doc/pdf/pdf.pdf'))

    def test_doc_postscript_1(self):
        assert is_text(self.get_test_loc('contenttype/doc/postscript/doc.ps'))
        assert not is_binary(self.get_test_loc('contenttype/doc/postscript/doc.ps'))

    def test_doc_postscript_2(self):
        assert not is_binary(self.get_test_loc('contenttype/doc/postscript/a.ps'))
        assert not is_media(self.get_test_loc('contenttype/doc/postscript/a.ps'))

    def test_doc_postscript_eps(self):
        assert is_binary(self.get_test_loc('contenttype/doc/postscript/Image1.eps'))
        assert 'application/octet-stream' == get_mimetype_file(self.get_test_loc('contenttype/doc/postscript/Image1.eps'))
        assert get_filetype_file(self.get_test_loc('contenttype/doc/postscript/Image1.eps')).startswith('DOS EPS Binary File Postscript')

    def test_doc_xml(self):
        assert not is_binary(self.get_test_loc('contenttype/doc/xml/simple.xml'))
        assert 'xml language text' == get_filetype(self.get_test_loc('contenttype/doc/xml/simple.xml'))

        assert not is_binary(self.get_test_loc('contenttype/doc/xml/some.xml'))
        assert 'xml language text' == get_filetype(self.get_test_loc('contenttype/doc/xml/some.xml'))

        assert not is_binary(self.get_test_loc('contenttype/doc/xml/somespring.xml'))
        assert 'xml language text' == get_filetype(self.get_test_loc('contenttype/doc/xml/somespring.xml'))

    def test_media_audio_aif(self):
        assert is_media(self.get_test_loc('contenttype/media/a.aif'))
        assert is_binary(self.get_test_loc('contenttype/media/a.aif'))

        assert is_media(self.get_test_loc('contenttype/media/a.aiff'))
        assert is_binary(self.get_test_loc('contenttype/media/a.aiff'))

    def test_media_audio_au(self):
        assert is_media(self.get_test_loc('contenttype/media/a.au'))
        assert is_binary(self.get_test_loc('contenttype/media/a.au'))

    def test_media_audio_flac(self):
        assert is_media(self.get_test_loc('contenttype/media/a.flac'))
        assert is_binary(self.get_test_loc('contenttype/media/a.flac'))

    def test_media_audio_mp3(self):
        assert is_media(self.get_test_loc('contenttype/media/a.mp3'))
        assert is_binary(self.get_test_loc('contenttype/media/a.mp3'))

    def test_media_audio_wav(self):
        assert is_media(self.get_test_loc('contenttype/media/a.wav'))
        assert is_binary(self.get_test_loc('contenttype/media/a.wav'))

    def test_media_image_bmp_1(self):
        assert is_media(self.get_test_loc('contenttype/media/Image1.bmp'))
        assert is_binary(self.get_test_loc('contenttype/media/Image1.bmp'))

    def test_media_image_bmp_2(self):
        assert 'pc bitmap, windows 3.x format, 400 x 32 x 4' == get_filetype(self.get_test_loc('contenttype/media/TBarLrge.bmp'))
        assert 'pc bitmap, windows 3.x format, 210 x 16 x 4' == get_filetype(self.get_test_loc('contenttype/media/TBarMedm.bmp'))

    def test_media_image_dib(self):
        assert is_media(self.get_test_loc('contenttype/media/Image1.dib'))
        assert is_binary(self.get_test_loc('contenttype/media/Image1.dib'))

    def test_media_image_gif(self):
        assert is_media(self.get_test_loc('contenttype/media/Image1.gif'))
        assert is_binary(self.get_test_loc('contenttype/media/Image1.gif'))

    def test_media_image_ico(self):
        assert is_media(self.get_test_loc('contenttype/media/Image1.ico'))
        assert is_binary(self.get_test_loc('contenttype/media/Image1.ico'))

    def test_media_image_iff(self):
        assert is_media(self.get_test_loc('contenttype/media/Image1.iff'))
        assert is_binary(self.get_test_loc('contenttype/media/Image1.iff'))

    def test_media_image_img(self):
        # FIXME: .img files are more complex
        assert is_binary(self.get_test_loc('contenttype/media/Image1.img'))
        assert get_filetype_file(self.get_test_loc('contenttype/media/Image1.img')).startswith('GEM Image data')
        assert 'application/octet-stream' == get_mimetype_file(self.get_test_loc('contenttype/media/Image1.img'))
        assert not get_mimetype_python(self.get_test_loc('contenttype/media/Image1.img'))
        assert is_media(self.get_test_loc('contenttype/media/Image1.img'))

    def test_media_image_jif(self):
        assert is_media(self.get_test_loc('contenttype/media/Image1.jif'))
        assert is_binary(self.get_test_loc('contenttype/media/Image1.jif'))

    def test_media_image_jpeg(self):
        assert is_media(self.get_test_loc('contenttype/media/Image1.jpeg'))
        assert is_binary(self.get_test_loc('contenttype/media/Image1.jpeg'))

        assert is_media(self.get_test_loc('contenttype/media/Image1.jpg'))
        assert is_binary(self.get_test_loc('contenttype/media/Image1.jpg'))

    def test_media_image_pbm_ppm(self):
        assert is_media(self.get_test_loc('contenttype/media/Image1.pbm'))
        assert not is_binary(self.get_test_loc('contenttype/media/Image1.pbm'))
        assert not is_binary(self.get_test_loc('contenttype/media/Image1.ppm'))

        # this is text
        assert is_media(self.get_test_loc('contenttype/media/Image1.ppm'))

    def test_media_image_pcx(self):
        assert is_media(self.get_test_loc('contenttype/media/Image1.pcx'))
        assert is_binary(self.get_test_loc('contenttype/media/Image1.pcx'))

    def test_media_image_photoshop(self):
        assert is_media(self.get_test_loc('contenttype/media/Image1.psd'))
        assert is_binary(self.get_test_loc('contenttype/media/Image1.psd'))

    def test_media_image_png(self):
        assert is_media(self.get_test_loc('contenttype/media/a.png'))
        assert is_binary(self.get_test_loc('contenttype/media/a.png'))

    def test_media_image_psp(self):
        assert is_media(self.get_test_loc('contenttype/media/Image1.psp'))
        assert is_binary(self.get_test_loc('contenttype/media/Image1.psp'))

    def test_media_image_ras(self):
        assert is_media(self.get_test_loc('contenttype/media/Image1.ras'))
        assert is_binary(self.get_test_loc('contenttype/media/Image1.ras'))

    def test_media_image_svg(self):
        assert not is_binary(self.get_test_loc('contenttype/media/drawing.svg'))
        assert is_media(self.get_test_loc('contenttype/media/drawing.svg'))
        assert is_media(self.get_test_loc('contenttype/media/drawing.svg'))

    def test_media_image_tgg(self):
        assert is_media(self.get_test_loc('contenttype/media/Image1.tga'))
        assert is_binary(self.get_test_loc('contenttype/media/Image1.tga'))

    def test_media_image_tif(self):
        assert is_media(self.get_test_loc('contenttype/media/Image1.tif'))
        assert is_binary(self.get_test_loc('contenttype/media/Image1.tif'))

    def test_media_image_windows_metafile(self):
        assert 'application/octet-stream' == get_mimetype_file(self.get_test_loc('contenttype/media/Image1.emf'))
        assert not get_mimetype_python(self.get_test_loc('contenttype/media/Image1.emf'))
        assert get_filetype_file(self.get_test_loc('contenttype/media/Image1.emf')).startswith('Windows Enhanced Metafile')
        assert is_media(self.get_test_loc('contenttype/media/Image1.emf'))
        assert is_binary(self.get_test_loc('contenttype/media/Image1.emf'))

    def test_media_video_mpeg(self):
        assert is_media(self.get_test_loc('contenttype/media/a4.mp4'))
        assert is_binary(self.get_test_loc('contenttype/media/a4.mp4'))

        assert is_media(self.get_test_loc('contenttype/media/a4.mpg'))
        assert is_binary(self.get_test_loc('contenttype/media/a4.mpg'))

        assert is_media(self.get_test_loc('contenttype/media/a.mp2'))
        assert is_binary(self.get_test_loc('contenttype/media/a.mp2'))

    def test_media_video_msft(self):
        assert is_media(self.get_test_loc('contenttype/media/a.avi'))
        assert is_binary(self.get_test_loc('contenttype/media/a.avi'))

        assert is_media(self.get_test_loc('contenttype/media/Image1.wmf'))
        assert is_binary(self.get_test_loc('contenttype/media/Image1.wmf'))

        assert is_media(self.get_test_loc('contenttype/media/mov.wvm.wmv'))
        assert is_binary(self.get_test_loc('contenttype/media/mov.wvm.wmv'))
        assert is_media(self.get_test_loc('contenttype/media/Movie.wmv'))
        assert is_binary(self.get_test_loc('contenttype/media/Movie.wmv'))

        assert is_media(self.get_test_loc('contenttype/media/Movie_0001.wmv'))
        assert is_binary(self.get_test_loc('contenttype/media/Movie_0001.wmv'))
        assert is_media(self.get_test_loc('contenttype/media/Movie_0002.wmv'))
        assert is_binary(self.get_test_loc('contenttype/media/Movie_0002.wmv'))

    def test_media_video_ogg(self):
        assert is_media(self.get_test_loc('contenttype/media/a.ogg'))
        assert is_binary(self.get_test_loc('contenttype/media/a.ogg'))
        assert is_media(self.get_test_loc('contenttype/media/a.theo.ogg'))
        assert is_binary(self.get_test_loc('contenttype/media/a.theo.ogg'))

    def test_package_debian(self):
        assert 'debian binary package (format 2.0)' == get_filetype(self.get_test_loc('contenttype/package/wget-el_0.5.0-8_all.deb'))

    def test_package_java_jar(self):
        assert is_binary(self.get_test_loc('contenttype/package/ant-jsch-1.7.0.jar'))
        assert is_archive(self.get_test_loc('contenttype/package/ant-jsch-1.7.0.jar'))
        assert 'java archive data (jar)' == get_filetype(self.get_test_loc('contenttype/package/ant-jsch-1.7.0.jar'))

    def test_package_java_jar_as_zip(self):
        assert is_binary(self.get_test_loc('contenttype/package/ant.zip'))
        assert is_archive(self.get_test_loc('contenttype/package/ant.zip'))
        assert 'java archive data (jar)' == get_filetype(self.get_test_loc('contenttype/package/ant.zip'))

    def test_package_java_war(self):
        assert is_binary(self.get_test_loc('contenttype/package/c.war'))
        assert is_archive(self.get_test_loc('contenttype/package/c.war'))
        assert 'zip archive data, at least v1.0 to extract' == get_filetype(self.get_test_loc('contenttype/package/c.war'))

    def test_package_python_egg(self):
        assert is_binary(self.get_test_loc('contenttype/package/TicketImport-0.7a-py2.5.egg'))
        assert is_archive(self.get_test_loc('contenttype/package/TicketImport-0.7a-py2.5.egg'))
        assert 'zip archive data, at least v2.0 to extract' == get_filetype(self.get_test_loc('contenttype/package/TicketImport-0.7a-py2.5.egg'))

    def test_package_rpm(self):
        assert 'rpm v3.0 bin i386/x86_64' == get_filetype(self.get_test_loc('contenttype/package/wget-1.11.4-3.fc11.i586.rpm'))

    def test_package_rubygem(self):
        assert 'posix tar archive' == get_filetype(self.get_test_loc('contenttype/package/rubygems-update-1.4.1.gem'))

    def test_script_bash(self):
        assert 'bash language text' == get_filetype(self.get_test_loc('contenttype/script/test.sh'))

    def test_script_bash_makelinks(self):
        assert is_source(self.get_test_loc('contenttype/script/makelinks'))

    def test_script_windows_bat(self):
        assert 'batchfile language text' == get_filetype(self.get_test_loc('contenttype/script/build_w32vc.bat'))
        assert 'batchfile language text' == get_filetype(self.get_test_loc('contenttype/script/zip_src.bat'))

    def test_script_install(self):
        assert 'ascii text' == get_filetype(self.get_test_loc('contenttype/script/install'))

    def test_text_crashing(self):
        assert 'ASCII text' == get_filetype_file(self.get_test_loc('contenttype/text/crashing-a.txt'))
        assert 'ASCII text' == get_filetype_file(self.get_test_loc('contenttype/text/crashing-z.txt'))

    def test_text(self):
        assert not is_binary(self.get_test_loc('contenttype/text/x11-xconsortium_text.txt'))
        assert not is_archive(self.get_test_loc('contenttype/text/x11-xconsortium_text.txt'))

    def test_text_license_copying(self):
        assert 'ascii text' in get_filetype(self.get_test_loc('contenttype/text/COPYING'))
        assert not is_source(self.get_test_loc('contenttype/text/COPYING'))
        assert is_text(self.get_test_loc('contenttype/text/COPYING'))
        assert '' == get_filetype_pygment(self.get_test_loc('contenttype/text/COPYING'))
        assert 'text/plain' == get_mimetype_file(self.get_test_loc('contenttype/text/COPYING'))

    def test_text_license_credits(self):
        # FIXME
        assert 'css+lasso language text' == get_filetype(self.get_test_loc('contenttype/text/CREDITS'))
        assert is_text(self.get_test_loc('contenttype/text/CREDITS'))
        # FIXME: incorrect
        assert is_source(self.get_test_loc('contenttype/text/CREDITS'))
        # FIXME: incorrect
        assert 'CSS+Lasso' == get_filetype_pygment(self.get_test_loc('contenttype/text/CREDITS'))
        assert 'ISO-8859 text' == get_filetype_file(self.get_test_loc('contenttype/text/CREDITS'))
        assert 'text/plain' == get_mimetype_file(self.get_test_loc('contenttype/text/CREDITS'))

    def test_text_license_gpl(self):
        assert not is_source(self.get_test_loc('contenttype/text/GPL.txt'))

    def test_text_log(self):
        assert not is_source(self.get_test_loc('contenttype/text/windowserver.log'))
        assert is_text(self.get_test_loc('contenttype/text/windowserver.log'))
        assert '' == get_filetype_pygment(self.get_test_loc('contenttype/text/windowserver.log'))
        assert 'ascii text' == get_filetype(self.get_test_loc('contenttype/text/windowserver.log'))
        assert 'ASCII text' == get_filetype_file(self.get_test_loc('contenttype/text/windowserver.log'))
        assert 'text/plain' == get_mimetype_file(self.get_test_loc('contenttype/text/windowserver.log'))

    def test_is_standard_include(self):
        assert is_standard_include('<built-in>')
        assert is_standard_include('/usr/lib/this.h')
        assert is_standard_include('/usr/include/this.h')

    def test_text_iso_text_changelog_is_not_iso_cdrom(self):
        assert 'Non-ISO extended-ASCII text' == get_filetype_file(self.get_test_loc('contenttype/text/ChangeLog'))

    @expectedFailure
    def test_text_rsync_file_is_not_octet_stream(self):
        # this is a libmagic bug: http://bugs.gw.com/view.php?id=473
        assert 'data' != get_filetype_file(self.get_test_loc('contenttype/text/wildtest.txt'))
        assert 'octet' not in get_mimetype_file(self.get_test_loc('contenttype/text/wildtest.txt'))

    def test_rgb_stream_is_binary(self):
        # this is a binaryornot bug: https://github.com/audreyr/binaryornot/issues/10
        assert 'data' == get_filetype_file(self.get_test_loc('contenttype/binary/pixelstream.rgb'))
        assert 'application/octet-stream' == get_mimetype_file(self.get_test_loc('contenttype/binary/pixelstream.rgb'))
        assert is_binary(self.get_test_loc('contenttype/binary/pixelstream.rgb'))
