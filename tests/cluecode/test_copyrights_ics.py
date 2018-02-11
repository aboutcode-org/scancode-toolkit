# -*- coding: utf-8 -*-
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

import os.path

from commoncode.testcase import FileBasedTesting
from cluecode_assert_utils import check_detection
from cluecode_assert_utils import expectedFailure

"""
This test suite is based a rather large subset of Android ICS, providing a
rather diversified sample of a typical Linux-based user space environment.
"""


class TestCopyrights(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_ics_bison_build_aux_config_rpath_authors(self):
        expected = [
            u'Gordon Matzigkeit <gord@gnu.ai.mit.edu>',
        ]
        check_detection(expected, 'authors/author-config.rpath', what='authors')

    def test_ics_bison_lib_strverscmp_c_authors(self):
        expected = [
            u'Jean-Francois Bignolles <bignolle@ecoledoc.ibp.fr>'
        ]
        check_detection(expected, 'authors/strverscmp2.c', what='authors')

    def test_ics_blktrace_strverscmp_c_authors(self):
        expected = [
            u'Jean-Francois Bignolles <bignolle@ecoledoc.ibp.fr>'
        ]
        check_detection(expected, 'authors/strverscmp.c', what='authors')

    def test_ics_bluetooth_bluez_health_hdp_c_authors(self):
        expected = [
            u'Santiago Carot Nemesio',
        ]
        check_detection(expected, 'authors/hdp.c', what='authors')

    def test_ics_bluetooth_glib_gio_tests_memory_input_stream_c_authors(self):
        expected = [
            u'Tim Janik',
        ]
        check_detection(expected, 'authors/memory-input-stream.c', what='authors')

    def test_ics_chromium_sdch_open_vcdiff_ltmain_sh_authors(self):
        expected = [
            u'Gordon Matzigkeit <gord@gnu.ai.mit.edu>',
        ]
        check_detection(expected, 'authors/vcdiff-ltmain.sh', what='authors')

    def test_ics_expat_configure_authors(self):
        expected = [
            u'Gordon Matzigkeit <gord@gnu.ai.mit.edu>',
        ]
        check_detection(expected, 'authors/configure', what='authors')

    def test_ics_expat_conftools_libtool_m4_authors(self):
        expected = [
            u'Gordon Matzigkeit <gord@gnu.ai.mit.edu>',
        ]
        check_detection(expected, 'authors/libtool.m4', what='authors')

    def test_ics_expat_conftools_ltmain_sh_authors(self):
        expected = [
            u'Gordon Matzigkeit <gord@gnu.ai.mit.edu>',
        ]
        check_detection(expected, 'authors/expat-ltmain.sh', what='authors')

    def test_ics_kernel_headers_original_asm_arm_arch_mcbsp_h_authors(self):
        expected = [
            u'Steve Johnson',
        ]
        check_detection(expected, 'authors/mcbsp.h', what='authors')

    def test_ics_libffi_ltcf_c_sh_authors(self):
        expected = [
            u'Gordon Matzigkeit <gord@gnu.ai.mit.edu>',
        ]
        check_detection(expected, 'authors/ltcf-c.sh', what='authors')

    def test_ics_libffi_ltcf_cxx_sh_authors(self):
        expected = [
            u'Gordon Matzigkeit <gord@gnu.ai.mit.edu>',
        ]
        check_detection(expected, 'authors/ltcf-cxx.sh', what='authors')

    def test_ics_libffi_ltconfig_authors(self):
        expected = [
            u'Gordon Matzigkeit <gord@gnu.ai.mit.edu>',
            u'Gordon Matzigkeit <gord@gnu.ai.mit.edu>',
        ]
        check_detection(expected, 'authors/ltconfig', what='authors')

    def test_ics_libffi_ltmain_sh_authors(self):
        expected = [
            u'Gordon Matzigkeit <gord@gnu.ai.mit.edu>',
        ]
        check_detection(expected, 'authors/ltmain.sh', what='authors')

    def test_ics_qemu_device_tree_c_authors(self):
        expected = [
            u'Jerone Young <jyoung5@us.ibm.com> Hollis Blanchard <hollisb@us.ibm.com>',
        ]
        check_detection(expected, 'authors/device_tree.c', what='authors')

    def test_ics_speex_libspeex_fixed_bfin_h_authors(self):
        expected = [
            u'Jean-Marc Valin'
        ]
        check_detection(expected, 'authors/fixed_bfin.h', what='authors')

    def test_ics_android_mock_android_mk(self):
        expected = [
            u'Copyright (c) 2010 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/android-mock/Android.mk')

    def test_ics_android_mock_notice(self):
        expected = [
            u'Copyright (c) 2005-2008, The Android Open Source Project',
        ]
        check_detection(expected, 'ics/android-mock/NOTICE')

    def test_ics_android_mock_regenerate_from_source_sh(self):
        expected = [
            u'Copyright (c) 2011 The Android Open Source Project.',
        ]
        check_detection(expected, 'ics/android-mock/regenerate_from_source.sh')

    def test_ics_android_mock_livetests_com_google_android_testing_mocking_test_androidmanifest_xml(self):
        expected = [
            u'Copyright 2010 Google Inc.',
        ]
        check_detection(expected, 'ics/android-mock-livetests-com-google-android-testing-mocking-test/AndroidManifest.xml')

    def test_ics_android_mock_src_com_google_android_testing_mocking_androidmock_java(self):
        expected = [
            u'Copyright 2010 Google Inc.',
        ]
        check_detection(expected, 'ics/android-mock-src-com-google-android-testing-mocking/AndroidMock.java')

    def test_ics_android_mock_src_com_google_android_testing_mocking_generatedmockjar_readme(self):
        expected = [
            u'Copyright 2010 Google Inc.',
        ]
        check_detection(expected, 'ics/android-mock-src-com-google-android-testing-mocking/GeneratedMockJar.readme')

    def test_ics_antlr_android_mk(self):
        expected = [
            u'Copyright (c) 2011 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/antlr/Android.mk')

    def test_ics_antlr_src_org_antlr_runtime_antlrfilestream_java(self):
        expected = [
            u'Copyright (c) 2005-2009 Terence Parr',
        ]
        check_detection(expected, 'ics/antlr-src-org-antlr-runtime/ANTLRFileStream.java')

    def test_ics_apache_harmony_notice(self):
        expected = [
            u'Copyright 2001-2004 The Apache Software Foundation.',
            u'Copyright 2001-2006 The Apache Software Foundation.',
            u'Copyright 2003-2004 The Apache Software Foundation.',
            u'Copyright 2004 The Apache Software Foundation.',
        ]
        check_detection(expected, 'ics/apache-harmony/NOTICE')

    def test_ics_apache_http_cleanspec_mk(self):
        expected = [
            u'Copyright (c) 2007 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/apache-http/CleanSpec.mk')

    def test_ics_apache_http_thirdpartyproject_prop(self):
        expected = [
            u'Copyright 2010 Google Inc.',
        ]
        check_detection(expected, 'ics/apache-http/ThirdPartyProject.prop')

    def test_ics_apache_http_src_org_apache_commons_codec_binarydecoder_java(self):
        expected = [
            u'Copyright 2001-2004 The Apache Software Foundation.',
        ]
        check_detection(expected, 'ics/apache-http-src-org-apache-commons-codec/BinaryDecoder.java')

    def test_ics_apache_http_src_org_apache_commons_codec_overview_html(self):
        expected = [
            u'Copyright 2003-2004 The Apache Software Foundation.',
        ]
        check_detection(expected, 'ics/apache-http-src-org-apache-commons-codec/overview.html')

    def test_ics_apache_http_src_org_apache_commons_logging_logfactory_java(self):
        expected = [
            u'Copyright 2001-2006 The Apache Software Foundation.',
        ]
        check_detection(expected, 'ics/apache-http-src-org-apache-commons-logging/LogFactory.java')

    def test_ics_apache_http_src_org_apache_commons_logging_package_html(self):
        expected = [
            u'Copyright 2001-2004 The Apache Software Foundation.',
        ]
        check_detection(expected, 'ics/apache-http-src-org-apache-commons-logging/package.html')

    def test_ics_apache_http_src_org_apache_commons_logging_impl_weakhashtable_java(self):
        expected = [
            u'Copyright 2004 The Apache Software Foundation.',
        ]
        check_detection(expected, 'ics/apache-http-src-org-apache-commons-logging-impl/WeakHashtable.java')

    def test_ics_apache_xml_notice(self):
        expected = [
            u'Copyright 1999-2006 The Apache Software Foundation',
            u'Copyright 1999-2006 The Apache Software Foundation',
            u'copyright (c) 1999-2002, Lotus Development Corporation., http://www.lotus.com.',
            u'copyright (c) 2001-2002, Sun Microsystems., http://www.sun.com.',
            u'copyright (c) 2003, IBM Corporation., http://www.ibm.com.',
            u'Copyright 1999-2006 The Apache Software Foundation',
            u'copyright (c) 1999, IBM Corporation., http://www.ibm.com.',
            u'copyright (c) 1999, Sun Microsystems., http://www.sun.com.',
            u'at iClick, Inc., software copyright (c) 1999.',
            u'Copyright 2001-2003,2006 The Apache Software Foundation.',
            u'copyright (c) 1999, IBM Corporation., http://www.ibm.com.',
            u'copyright (c) 1999, Sun Microsystems., http://www.sun.com.',
            u'copyright (c) 2000 World Wide Web Consortium, http://www.w3.org',
        ]
        check_detection(expected, 'ics/apache-xml/NOTICE')

    def test_ics_apache_xml_src_main_java_org_apache_xpath_domapi_xpathstylesheetdom3exception_java(self):
        expected = [
            u'Copyright (c) 2002 World Wide Web Consortium, '
            u'(Massachusetts Institute of Technology, '
            u'Institut National de Recherche en Informatique et en Automatique, '
            u'Keio University).',
        ]
        check_detection(expected, 'ics/apache-xml-src-main-java-org-apache-xpath-domapi/XPathStylesheetDOM3Exception.java')

    def test_ics_astl_android_mk(self):
        expected = [
            u'Copyright (c) 2009 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/astl/Android.mk')

    def test_ics_astl_notice(self):
        expected = [
            u'Copyright (c) 2009 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/astl/NOTICE')

    def test_ics_astl_include_algorithm(self):
        expected = [
            u'Copyright (c) 2009 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/astl-include/algorithm')

    def test_ics_astl_include_basic_ios_h(self):
        expected = [
            u'Copyright (c) 2010 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/astl-include/basic_ios.h')

    def test_ics_astl_include_streambuf(self):
        expected = [
            u'Copyright (c) 2010 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/astl-include/streambuf')

    def test_ics_astl_include_string(self):
        expected = [
            u'Copyright (c) 2009 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/astl-include/string')

    def test_ics_astl_src_ostream_cpp(self):
        expected = [
            u'Copyright (c) 2010 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/astl-src/ostream.cpp')

    def test_ics_astl_tests_test_vector_cpp(self):
        expected = [
            u'Copyright (c) 2009 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/astl-tests/test_vector.cpp')

    def test_ics_bison_aclocal_m4(self):
        expected = [
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2002, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 1999, 2000, 2001, 2002, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1997, 2000, 2001, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2002, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1997, 1999, 2000, 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2002, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 2000, 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison/aclocal.m4')

    def test_ics_bison_android_mk(self):
        expected = [
            u'Copyright 2006 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/bison/Android.mk')

    def test_ics_bison_changelog(self):
        expected = [
            u'Copyright (c) 1987, 1988, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison/ChangeLog')

    def test_ics_bison_config_log(self):
        expected = [
            u'Copyright (c) 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison/config.log')

    def test_ics_bison_config_status(self):
        expected = [
            u'Copyright (c) 2003 Free Software Foundation, Inc.',
            u'Copyright (c) 2000, 2001, 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison/config.status')

    def test_ics_bison_configure(self):
        expected = [
            u'Copyright (c) 2003 Free Software Foundation, Inc.',
            u'Copyright (c) 2003 Free Software Foundation, Inc.',
            u'Copyright (c) 2003 Free Software Foundation, Inc.',
            u'Copyright (c) 2000, 2001, 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison/configure')

    def test_ics_bison_configure_ac(self):
        expected = [
            u'Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison/configure.ac')

    def test_ics_bison_copying(self):
        expected = [
            u'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, 'ics/bison/COPYING')

    def test_ics_bison_gnumakefile(self):
        expected = [
            u'Copyright (c) 2001, 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison/GNUmakefile')

    def test_ics_bison_install(self):
        expected = [
            u'Copyright (c) 1994, 1995, 1996, 1999, 2000, 2001, 2002, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison/INSTALL')

    def test_ics_bison_makefile(self):
        expected = [
            u'Copyright (c) 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison/Makefile')

    def test_ics_bison_makefile_am(self):
        expected = [
            u'Copyright (c) 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison/Makefile.am')

    def test_ics_bison_makefile_cfg(self):
        expected = [
            u'Copyright (c) 2003, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison/Makefile.cfg')

    def test_ics_bison_makefile_maint(self):
        expected = [
            u'Copyright (c) 2001-2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison/Makefile.maint')

    def test_ics_bison_news(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison/NEWS')

    def test_ics_bison_notice(self):
        expected = [
            u'Copyright (c) 1992-2006 Free Software Foundation, Inc.',
            u'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, 'ics/bison/NOTICE')

    def test_ics_bison_packaging(self):
        expected = [
            u'Copyright (c) 2002, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison/PACKAGING')

    def test_ics_bison_readme(self):
        expected = [
            u'Copyright (c) 1992, 1998, 1999, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison/README')

    def test_ics_bison_todo(self):
        expected = [
            u'Copyright (c) 2001, 2002, 2003, 2004, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison/TODO')

    def test_ics_bison_build_aux_config_guess(self):
        expected = [
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-build-aux/config.guess')

    def test_ics_bison_build_aux_config_rpath(self):
        expected = [
            u'Copyright 1996-2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-build-aux/config.rpath')

    def test_ics_bison_build_aux_depcomp(self):
        expected = [
            u'Copyright (c) 1999, 2000, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-build-aux/depcomp')

    def test_ics_bison_build_aux_install_sh(self):
        expected = [
            u'Copyright (c) 1994 X Consortium',
        ]
        check_detection(expected, 'ics/bison-build-aux/install-sh')

    def test_ics_bison_build_aux_mdate_sh(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-build-aux/mdate-sh')

    def test_ics_bison_build_aux_missing(self):
        expected = [
            u'Copyright (c) 1996, 1997, 1999, 2000, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-build-aux/missing')

    def test_ics_bison_build_aux_texinfo_tex(self):
        expected = [
            u'Copyright (c) 1985, 1986, 1988, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-build-aux/texinfo.tex')

    def test_ics_bison_build_aux_ylwrap(self):
        expected = [
            u'Copyright (c) 1996, 1997, 1998, 1999, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-build-aux/ylwrap')

    def test_ics_bison_data_c_m4(self):
        expected = [
            u'Copyright (c) 2002, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) $2 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-data/c.m4')

    def test_ics_bison_data_c_m4_2(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-data/c++.m4')

    def test_ics_bison_data_makefile_am(self):
        expected = [
            u'Copyright (c) 2002, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-data/Makefile.am')

    def test_ics_bison_data_readme(self):
        expected = [
            u'Copyright (c) 2002 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-data/README')

    def test_ics_bison_data_m4sugar_m4sugar_m4(self):
        expected = [
            u'Copyright (c) 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-data-m4sugar/m4sugar.m4')

    def test_ics_bison_djgpp_config_bat(self):
        expected = [
            u'Copyright (c) 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-djgpp/config.bat')

    def test_ics_bison_djgpp_config_sed(self):
        expected = [
            u'Copyright (c) 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-djgpp/config.sed')

    def test_ics_bison_djgpp_makefile_maint(self):
        expected = [
            u'Copyright (c) 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-djgpp/Makefile.maint')

    def test_ics_bison_djgpp_readme_in(self):
        expected = [
            u'Copyright (c) 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-djgpp/README.in')

    def test_ics_bison_djgpp_subpipe_h(self):
        expected = [
            u'Copyright (c) 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-djgpp/subpipe.h')

    def test_ics_bison_doc_bison_texinfo(self):
        expected = [
            u'Copyright 1988, 1989, 1990, 1991, 1992, 1993, 1995, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-doc/bison.texinfo')

    def test_ics_bison_doc_fdl_texi(self):
        expected = [
            u'Copyright 2000,2001,2002 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-doc/fdl.texi')

    def test_ics_bison_doc_gpl_texi(self):
        expected = [
            u'Copyright 1989, 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, 'ics/bison-doc/gpl.texi')

    def test_ics_bison_doc_makefile_am(self):
        expected = [
            u'Copyright (c) 2001, 2002, 2003, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-doc/Makefile.am')

    def test_ics_bison_doc_refcard_tex(self):
        expected = [
            u'Copyright (c) 1998, 2001 Free Software Foundation, Inc.',
            u'Copyright year Free Software Foundation, Inc.',
            u'Copyright year Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-doc/refcard.tex')

    def test_ics_bison_examples_extexi(self):
        expected = [
            u'Copyright 1992, 2000, 2001, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-examples/extexi')

    def test_ics_bison_examples_makefile_am(self):
        expected = [
            u'Copyright (c) 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-examples/Makefile.am')

    def test_ics_bison_lib_abitset_c(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/abitset.c')

    def test_ics_bison_lib_abitset_h(self):
        expected = [
            u'Copyright (c) 2002, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/abitset.h')

    def test_ics_bison_lib_argmatch_c(self):
        expected = [
            u'Copyright (c) 1990, 1998, 1999, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/argmatch.c')

    def test_ics_bison_lib_argmatch_h(self):
        expected = [
            u'Copyright (c) 1990, 1998, 1999, 2001, 2002, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/argmatch.h')

    def test_ics_bison_lib_basename_c(self):
        expected = [
            u'Copyright (c) 1990, 1998, 1999, 2000, 2001, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/basename.c')

    def test_ics_bison_lib_bbitset_h(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/bbitset.h')

    def test_ics_bison_lib_bitset_c(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/bitset.c')

    def test_ics_bison_lib_bitset_h(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/bitset.h')

    def test_ics_bison_lib_bitsetv_c(self):
        expected = [
            u'Copyright (c) 2001, 2002, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/bitsetv.c')

    def test_ics_bison_lib_bitsetv_print_c(self):
        expected = [
            u'Copyright (c) 2001, 2002, 2004, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/bitsetv-print.c')

    def test_ics_bison_lib_dirname_c(self):
        expected = [
            u'Copyright (c) 1990, 1998, 2000, 2001, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/dirname.c')

    def test_ics_bison_lib_dirname_h(self):
        expected = [
            u'Copyright (c) 1998, 2001, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/dirname.h')

    def test_ics_bison_lib_dup_safer_c(self):
        expected = [
            u'Copyright (c) 2001, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/dup-safer.c')

    def test_ics_bison_lib_error_c(self):
        expected = [
            u'Copyright (c) 1990-1998, 2000-2003, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/error.c')

    def test_ics_bison_lib_error_h(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997, 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/error.h')

    def test_ics_bison_lib_exit_h(self):
        expected = [
            u'Copyright (c) 1995, 2001 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/exit.h')

    def test_ics_bison_lib_exitfail_c(self):
        expected = [
            u'Copyright (c) 2002, 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/exitfail.c')

    def test_ics_bison_lib_get_errno_c(self):
        expected = [
            u'Copyright (c) 2002, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/get-errno.c')

    def test_ics_bison_lib_getopt_c(self):
        expected = [
            u'Copyright (c) 1987,88,89,90,91,92,93,94,95,96,98,99,2000,2001,2002,2003,2004,2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/getopt.c')

    def test_ics_bison_lib_getopt_h(self):
        expected = [
            u'Copyright (c) 1989-1994,1996-1999,2001,2003,2004,2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/getopt_.h')

    def test_ics_bison_lib_getopt_int_h(self):
        expected = [
            u'Copyright (c) 1989-1994,1996-1999,2001,2003,2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/getopt_int.h')

    def test_ics_bison_lib_getopt1_c(self):
        expected = [
            u'Copyright (c) 1987,88,89,90,91,92,93,94,96,97,98,2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/getopt1.c')

    def test_ics_bison_lib_gettext_h(self):
        expected = [
            u'Copyright (c) 1995-1998, 2000-2002, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/gettext.h')

    def test_ics_bison_lib_hard_locale_c(self):
        expected = [
            u'Copyright (c) 1997, 1998, 1999, 2002, 2003, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/hard-locale.c')

    def test_ics_bison_lib_hard_locale_h(self):
        expected = [
            u'Copyright (c) 1999, 2003, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/hard-locale.h')

    def test_ics_bison_lib_hash_c(self):
        expected = [
            u'Copyright (c) 1998, 1999, 2000, 2001, 2002, 2003, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/hash.c')

    def test_ics_bison_lib_hash_h(self):
        expected = [
            u'Copyright (c) 1998, 1999, 2001, 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/hash.h')

    def test_ics_bison_lib_makefile_am(self):
        expected = [
            u'Copyright (c) 2001, 2002, 2003, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/Makefile.am')

    def test_ics_bison_lib_malloc_c(self):
        expected = [
            u'Copyright (c) 1997, 1998 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/malloc.c')

    def test_ics_bison_lib_mbswidth_c(self):
        expected = [
            u'Copyright (c) 2000-2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/mbswidth.c')

    def test_ics_bison_lib_mbswidth_h(self):
        expected = [
            u'Copyright (c) 2000-2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/mbswidth.h')

    def test_ics_bison_lib_obstack_c(self):
        expected = [
            u'Copyright (c) 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/obstack.c')

    def test_ics_bison_lib_obstack_h(self):
        expected = [
            u'Copyright (c) 1988-1994,1996-1999,2003,2004,2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/obstack.h')

    def test_ics_bison_lib_quote_c(self):
        expected = [
            u'Copyright (c) 1998, 1999, 2000, 2001, 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/quote.c')

    def test_ics_bison_lib_quote_h(self):
        expected = [
            u'Copyright (c) 1998, 1999, 2000, 2001, 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/quote.h')

    def test_ics_bison_lib_quotearg_c(self):
        expected = [
            u'Copyright (c) 1998, 1999, 2000, 2001, 2002, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/quotearg.c')

    def test_ics_bison_lib_quotearg_h(self):
        expected = [
            u'Copyright (c) 1998, 1999, 2000, 2001, 2002, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/quotearg.h')

    def test_ics_bison_lib_stdbool_h(self):
        expected = [
            u'Copyright (c) 2001, 2002, 2003, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/stdbool_.h')

    def test_ics_bison_lib_stdio_safer_h(self):
        expected = [
            u'Copyright (c) 2001, 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/stdio-safer.h')

    def test_ics_bison_lib_stpcpy_c(self):
        expected = [
            u'Copyright (c) 1992, 1995, 1997, 1998 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/stpcpy.c')

    def test_ics_bison_lib_stpcpy_h(self):
        expected = [
            u'Copyright (c) 1995, 2001, 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/stpcpy.h')

    def test_ics_bison_lib_strdup_c(self):
        expected = [
            u'Copyright (c) 1991, 1996, 1997, 1998, 2002, 2003, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/strdup.c')

    def test_ics_bison_lib_strdup_h(self):
        expected = [
            u'Copyright (c) 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/strdup.h')

    def test_ics_bison_lib_strerror_c(self):
        expected = [
            u'Copyright (c) 1986, 1988, 1989, 1991, 2002, 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/strerror.c')

    def test_ics_bison_lib_stripslash_c(self):
        expected = [
            u'Copyright (c) 1990, 2001, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/stripslash.c')

    def test_ics_bison_lib_strndup_c(self):
        expected = [
            u'Copyright (c) 1996, 1997, 1998, 2001, 2002, 2003, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/strndup.c')

    def test_ics_bison_lib_strndup_h(self):
        expected = [
            u'Copyright (c) 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/strndup.h')

    def test_ics_bison_lib_strtol_c(self):
        expected = [
            u'Copyright (c) 1991, 1992, 1994, 1995, 1996, 1997, 1998, 1999, 2003, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/strtol.c')

    def test_ics_bison_lib_strtoul_c(self):
        expected = [
            u'Copyright (c) 1991, 1997 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/strtoul.c')

    def test_ics_bison_lib_strverscmp_c(self):
        expected = [
            u'Copyright (c) 1997, 2000, 2002, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/strverscmp.c')

    def test_ics_bison_lib_strverscmp_h(self):
        expected = [
            u'Copyright (c) 1997, 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/strverscmp.h')

    def test_ics_bison_lib_subpipe_c(self):
        expected = [
            u'Copyright (c) 2002, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/subpipe.c')

    def test_ics_bison_lib_subpipe_h(self):
        expected = [
            u'Copyright (c) 2002, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/subpipe.h')

    def test_ics_bison_lib_timevar_c(self):
        expected = [
            u'Copyright (c) 2000, 2002, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/timevar.c')

    def test_ics_bison_lib_timevar_h(self):
        expected = [
            u'Copyright (c) 2000, 2002, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/timevar.h')

    def test_ics_bison_lib_unistd_safer_h(self):
        expected = [
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/unistd-safer.h')

    def test_ics_bison_lib_unlocked_io_h(self):
        expected = [
            u'Copyright (c) 2001, 2002, 2003, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/unlocked-io.h')

    def test_ics_bison_lib_xalloc_h(self):
        expected = [
            u'Copyright (c) 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2003, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/xalloc.h')

    def test_ics_bison_lib_xalloc_die_c(self):
        expected = [
            u'Copyright (c) 1997, 1998, 1999, 2000, 2002, 2003, 2004, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-lib/xalloc-die.c')

    def test_ics_bison_m4_bison_i18n_m4(self):
        expected = [
            u'Copyright (c) 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/bison-i18n.m4')

    def test_ics_bison_m4_c_working_m4(self):
        expected = [
            u'Copyright (c) 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/c-working.m4')

    def test_ics_bison_m4_cxx_m4(self):
        expected = [
            u'Copyright (c) 2004, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/cxx.m4')

    def test_ics_bison_m4_dirname_m4(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/dirname.m4')

    def test_ics_bison_m4_dos_m4(self):
        expected = [
            u'Copyright (c) 2000, 2001, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/dos.m4')

    def test_ics_bison_m4_error_m4(self):
        expected = [
            u'Copyright (c) 1996, 1997, 1998, 2001, 2002, 2003, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/error.m4')

    def test_ics_bison_m4_exitfail_m4(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/exitfail.m4')

    def test_ics_bison_m4_extensions_m4(self):
        expected = [
            u'Copyright (c) 2003, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/extensions.m4')

    def test_ics_bison_m4_gettext_gl_m4(self):
        expected = [
            u'Copyright (c) 1995-2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/gettext_gl.m4')

    def test_ics_bison_m4_iconv_m4(self):
        expected = [
            u'Copyright (c) 2000-2002 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/iconv.m4')

    def test_ics_bison_m4_inttypes_h_gl_m4(self):
        expected = [
            u'Copyright (c) 1997-2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/inttypes_h_gl.m4')

    def test_ics_bison_m4_lib_ld_gl_m4(self):
        expected = [
            u'Copyright (c) 1996-2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/lib-ld_gl.m4')

    def test_ics_bison_m4_lib_link_m4(self):
        expected = [
            u'Copyright (c) 2001-2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/lib-link.m4')

    def test_ics_bison_m4_m4_m4(self):
        expected = [
            u'Copyright 2000 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/m4.m4')

    def test_ics_bison_m4_mbrtowc_m4(self):
        expected = [
            u'Copyright (c) 2001-2002, 2004-2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/mbrtowc.m4')

    def test_ics_bison_m4_mbstate_t_m4(self):
        expected = [
            u'Copyright (c) 2000, 2001, 2002 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/mbstate_t.m4')

    def test_ics_bison_m4_mbswidth_m4(self):
        expected = [
            u'Copyright (c) 2000-2002, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/mbswidth.m4')

    def test_ics_bison_m4_nls_m4(self):
        expected = [
            u'Copyright (c) 1995-2003, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/nls.m4')

    def test_ics_bison_m4_obstack_m4(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/obstack.m4')

    def test_ics_bison_m4_onceonly_m4(self):
        expected = [
            u'Copyright (c) 2002-2003, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/onceonly.m4')

    def test_ics_bison_m4_progtest_m4(self):
        expected = [
            u'Copyright (c) 1996-2003, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/progtest.m4')

    def test_ics_bison_m4_quotearg_m4(self):
        expected = [
            u'Copyright (c) 2002, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/quotearg.m4')

    def test_ics_bison_m4_stdbool_m4(self):
        expected = [
            u'Copyright (c) 2002-2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/stdbool.m4')

    def test_ics_bison_m4_stdio_safer_m4(self):
        expected = [
            u'Copyright (c) 2002, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/stdio-safer.m4')

    def test_ics_bison_m4_stpcpy_m4(self):
        expected = [
            u'Copyright (c) 2002 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/stpcpy.m4')

    def test_ics_bison_m4_strndup_m4(self):
        expected = [
            u'Copyright (c) 2002-2003, 2005-2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/strndup.m4')

    def test_ics_bison_m4_strtol_m4(self):
        expected = [
            u'Copyright (c) 2002, 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/strtol.m4')

    def test_ics_bison_m4_ulonglong_gl_m4(self):
        expected = [
            u'Copyright (c) 1999-2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/ulonglong_gl.m4')

    def test_ics_bison_m4_unlocked_io_m4(self):
        expected = [
            u'Copyright (c) 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/unlocked-io.m4')

    def test_ics_bison_m4_warning_m4(self):
        expected = [
            u'Copyright (c) 2001, 2002 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/warning.m4')

    def test_ics_bison_m4_xstrndup_m4(self):
        expected = [
            u'Copyright (c) 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-m4/xstrndup.m4')

    def test_ics_bison_src_assoc_c(self):
        expected = [
            u'Copyright (c) 2002, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/assoc.c')

    def test_ics_bison_src_closure_c(self):
        expected = [
            u'Copyright (c) 1984, 1989, 2000, 2001, 2002, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/closure.c')

    def test_ics_bison_src_closure_h(self):
        expected = [
            u'Copyright (c) 1984, 1989, 2000, 2001, 2002 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/closure.h')

    def test_ics_bison_src_complain_c(self):
        expected = [
            u'Copyright (c) 2000, 2001, 2002, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/complain.c')

    def test_ics_bison_src_complain_h(self):
        expected = [
            u'Copyright (c) 2000, 2001, 2002 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/complain.h')

    def test_ics_bison_src_conflicts_c(self):
        expected = [
            u'Copyright (c) 1984, 1989, 1992, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/conflicts.c')

    def test_ics_bison_src_conflicts_h(self):
        expected = [
            u'Copyright (c) 2000, 2001, 2002, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/conflicts.h')

    def test_ics_bison_src_derives_c(self):
        expected = [
            u'Copyright (c) 1984, 1989, 2000, 2001, 2002, 2003, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/derives.c')

    def test_ics_bison_src_files_c(self):
        expected = [
            u'Copyright (c) 1984, 1986, 1989, 1992, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/files.c')

    def test_ics_bison_src_getargs_c_lead_copy(self):
        expected = [
            u'Copyright (c) 1984, 1986, 1989, 1992, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) d Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/getargs.c')

    def test_ics_bison_src_getargs_h(self):
        expected = [
            u'Copyright (c) 1984, 1986, 1989, 1992, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/getargs.h')

    def test_ics_bison_src_gram_c(self):
        expected = [
            u'Copyright (c) 1984, 1986, 1989, 2001, 2002, 2003, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/gram.c')

    def test_ics_bison_src_gram_h(self):
        expected = [
            u'Copyright (c) 1984, 1986, 1989, 1992, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/gram.h')

    def test_ics_bison_src_lalr_c(self):
        expected = [
            u'Copyright (c) 1984, 1986, 1989, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/lalr.c')

    def test_ics_bison_src_lalr_h(self):
        expected = [
            u'Copyright (c) 1984, 1986, 1989, 2000, 2002, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/lalr.h')

    def test_ics_bison_src_lr0_c(self):
        expected = [
            u'Copyright (c) 1984, 1986, 1989, 2000, 2001, 2002, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/LR0.c')

    def test_ics_bison_src_lr0_h(self):
        expected = [
            u'Copyright 1984, 1986, 1989, 2000, 2001, 2002 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/LR0.h')

    def test_ics_bison_src_main_c(self):
        expected = [
            u'Copyright (c) 1984, 1986, 1989, 1992, 1995, 2000, 2001, 2002, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/main.c')

    def test_ics_bison_src_muscle_tab_c(self):
        expected = [
            u'Copyright (c) 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/muscle_tab.c')

    def test_ics_bison_src_muscle_tab_h(self):
        expected = [
            u'Copyright (c) 2001, 2002, 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/muscle_tab.h')

    def test_ics_bison_src_nullable_c(self):
        expected = [
            u'Copyright (c) 1984, 1989, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/nullable.c')

    def test_ics_bison_src_nullable_h(self):
        expected = [
            u'Copyright (c) 2000, 2002 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/nullable.h')

    def test_ics_bison_src_output_c(self):
        expected = [
            u'Copyright (c) 1984, 1986, 1989, 1992, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/output.c')

    def test_ics_bison_src_output_h(self):
        expected = [
            u'Copyright (c) 2000, 2001, 2002, 2003, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/output.h')

    def test_ics_bison_src_parse_gram_c(self):
        expected = [
            u'Copyright (c) 1984, 1989, 1990, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/parse-gram.c')

    def test_ics_bison_src_parse_gram_h(self):
        expected = [
            u'Copyright (c) 1984, 1989, 1990, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/parse-gram.h')

    def test_ics_bison_src_print_c(self):
        expected = [
            u'Copyright (c) 1984, 1986, 1989, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/print.c')

    def test_ics_bison_src_print_h(self):
        expected = [
            u'Copyright 2000 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/print.h')

    def test_ics_bison_src_reader_c(self):
        expected = [
            u'Copyright (c) 1984, 1986, 1989, 1992, 1998, 2000, 2001, 2002, 2003, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/reader.c')

    def test_ics_bison_src_reader_h(self):
        expected = [
            u'Copyright (c) 2000, 2001, 2002, 2003, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/reader.h')

    def test_ics_bison_src_reduce_c(self):
        expected = [
            u'Copyright (c) 1988, 1989, 2000, 2001, 2002, 2003, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/reduce.c')

    def test_ics_bison_src_scan_skel_c(self):
        expected = [
            u'Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/scan-skel.c')

    def test_ics_bison_src_scan_skel_l(self):
        expected = [
            u'Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/scan-skel.l')

    def test_ics_bison_src_state_h(self):
        expected = [
            u'Copyright (c) 1984, 1989, 2000, 2001, 2002, 2003, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/state.h')

    def test_ics_bison_src_symtab_c(self):
        expected = [
            u'Copyright (c) 1984, 1989, 2000, 2001, 2002, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/symtab.c')

    def test_ics_bison_src_symtab_h(self):
        expected = [
            u'Copyright (c) 1984, 1989, 1992, 2000, 2001, 2002, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/symtab.h')

    def test_ics_bison_src_system_h(self):
        expected = [
            u'Copyright (c) 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/system.h')

    def test_ics_bison_src_uniqstr_c(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/uniqstr.c')

    def test_ics_bison_src_vcg_h(self):
        expected = [
            u'Copyright (c) 2001, 2002, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-src/vcg.h')

    def test_ics_bison_tests_actions_at(self):
        expected = [
            u'Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-tests/actions.at')

    def test_ics_bison_tests_atconfig(self):
        expected = [
            u'Copyright (c) 2000, 2001, 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-tests/atconfig')

    def test_ics_bison_tests_atlocal(self):
        expected = [
            u'Copyright (c) 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-tests/atlocal')

    def test_ics_bison_tests_c_at(self):
        expected = [
            u'Copyright (c) 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-tests/c++.at')

    def test_ics_bison_tests_calc_at(self):
        expected = [
            u'Copyright (c) 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-tests/calc.at')

    def test_ics_bison_tests_conflicts_at(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-tests/conflicts.at')

    def test_ics_bison_tests_cxx_type_at(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-tests/cxx-type.at')

    def test_ics_bison_tests_existing_at(self):
        expected = [
            u'Copyright (c) 1989, 1990, 1991, 1992, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-tests/existing.at')

    def test_ics_bison_tests_glr_regression_at(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-tests/glr-regression.at')

    def test_ics_bison_tests_headers_at(self):
        expected = [
            u'Copyright (c) 2001, 2002, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-tests/headers.at')

    def test_ics_bison_tests_local_at(self):
        expected = [
            u'Copyright (c) 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-tests/local.at')

    def test_ics_bison_tests_makefile_am(self):
        expected = [
            u'Copyright (c) 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-tests/Makefile.am')

    def test_ics_bison_tests_output_at(self):
        expected = [
            u'Copyright (c) 2000, 2001, 2002, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-tests/output.at')

    def test_ics_bison_tests_sets_at(self):
        expected = [
            u'Copyright (c) 2001, 2002, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-tests/sets.at')

    def test_ics_bison_tests_synclines_at(self):
        expected = [
            u'Copyright (c) 2002, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-tests/synclines.at')

    def test_ics_bison_tests_testsuite_at(self):
        expected = [
            u'Copyright (c) 2000, 2001, 2002, 2003, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-tests/testsuite.at')

    def test_ics_bison_tests_torture_at(self):
        expected = [
            u'Copyright (c) 2001, 2002, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bison-tests/torture.at')

    def test_ics_blktrace_blkiomon_c(self):
        expected = [
            u'Copyright IBM Corp. 2008',
        ]
        check_detection(expected, 'ics/blktrace/blkiomon.c')

    def test_ics_blktrace_blkiomon_h(self):
        expected = [
            u'Copyright IBM Corp. 2008',
        ]
        check_detection(expected, 'ics/blktrace/blkiomon.h')

    def test_ics_blktrace_blkparse_c(self):
        expected = [
            u'Copyright (c) 2005 Jens Axboe <axboe@suse.de>',
            u'Copyright (c) 2006 Jens Axboe <axboe@kernel.dk>',
        ]
        check_detection(expected, 'ics/blktrace/blkparse.c')

    def test_ics_blktrace_blkrawverify_c(self):
        expected = [
            u'Copyright (c) 2006 Alan D. Brunelle <Alan.Brunelle@hp.com>',
        ]
        check_detection(expected, 'ics/blktrace/blkrawverify.c')

    def test_ics_blktrace_btrace(self):
        expected = [
            u'Copyright (c) 2005 Silicon Graphics, Inc.',
        ]
        check_detection(expected, 'ics/blktrace/btrace')

    def test_ics_blktrace_btrace_spec(self):
        expected = [
            u'Copyright (c) 2005 SUSE LINUX Products GmbH, Nuernberg, Germany.',
        ]
        check_detection(expected, 'ics/blktrace/btrace.spec')

    def test_ics_blktrace_jhash_h(self):
        expected = [
            u'Copyright (c) 2006. Bob Jenkins (bob_jenkins@burtleburtle.net)',
            u'Copyright (c) 2009 Jozsef Kadlecsik (kadlec@blackhole.kfki.hu)',
        ]
        check_detection(expected, 'ics/blktrace/jhash.h')

    def test_ics_blktrace_notice(self):
        expected = [
            u'Copyright (c) 1997, 2002, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2005 Jens Axboe <axboe@suse.de>',
            u'Copyright (c) 2006 Alan D. Brunelle <Alan.Brunelle@hp.com>',
            u'Copyright (c) 2006 Jens Axboe <axboe@kernel.dk>',
            u'Copyright (c) 2006. Bob Jenkins (bob_jenkins@burtleburtle.net)',
            u'Copyright (c) 2009 Jozsef Kadlecsik (kadlec@blackhole.kfki.hu)',
            u'Copyright IBM Corp. 2008',
            u'Copyright (c) 2005 SUSE LINUX Products GmbH, Nuernberg, Germany.',
            u'Copyright (c) 2005 Silicon Graphics, Inc.',
            u'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, 'ics/blktrace/NOTICE')

    def test_ics_blktrace_rbtree_c(self):
        expected = [
            u'(c) 1999 Andrea Arcangeli <andrea@suse.de>',
            u'(c) 2002 David Woodhouse <dwmw2@infradead.org>',
        ]
        check_detection(expected, 'ics/blktrace/rbtree.c')

    def test_ics_blktrace_rbtree_h(self):
        expected = [
            u'(c) 1999 Andrea Arcangeli <andrea@suse.de>',
        ]
        check_detection(expected, 'ics/blktrace/rbtree.h')

    def test_ics_blktrace_strverscmp_c(self):
        expected = [
            u'Copyright (c) 1997, 2002, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/blktrace/strverscmp.c')

    def test_ics_blktrace_btreplay_btrecord_c(self):
        expected = [
            u'Copyright (c) 2007 Alan D. Brunelle <Alan.Brunelle@hp.com>',
        ]
        check_detection(expected, 'ics/blktrace-btreplay/btrecord.c')

    def test_ics_blktrace_btreplay_btrecord_h(self):
        expected = [
            u'Copyright (c) 2007 Alan D. Brunelle <Alan.Brunelle@hp.com>',
        ]
        check_detection(expected, 'ics/blktrace-btreplay/btrecord.h')

    def test_ics_blktrace_btreplay_doc_abstract_tex(self):
        expected = [
            u'Copyright (c) 2007 Alan D. Brunelle <Alan.Brunelle@hp.com>',
        ]
        check_detection(expected, 'ics/blktrace-btreplay-doc/abstract.tex')

    def test_ics_blktrace_btt_bno_plot_py(self):
        expected = [
            u'(c) Copyright 2008 Hewlett-Packard Development Company, L.P.',
        ]
        check_detection(expected, 'ics/blktrace-btt/bno_plot.py')

    def test_ics_blktrace_btt_btt_plot_py(self):
        expected = [
            u'(c) Copyright 2009 Hewlett-Packard Development Company, L.P.',
        ]
        check_detection(expected, 'ics/blktrace-btt/btt_plot.py')

    def test_ics_blktrace_btt_notice(self):
        expected = [
            u'(c) Copyright 2007 Hewlett-Packard Development Company, L.P.',
            u'(c) Copyright 2008 Hewlett-Packard Development Company, L.P.',
            u'Copyright (c) 2006 Alan D. Brunelle <Alan.Brunelle@hp.com>',
            u'Copyright (c) 2007 Alan D. Brunelle <Alan.Brunelle@hp.com>',
            u'(c) Copyright 2008 Hewlett-Packard Development Company, L.P.',
            u'(c) Copyright 2009 Hewlett-Packard Development Company, L.P.',
            u'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, 'ics/blktrace-btt/NOTICE')

    def test_ics_blktrace_btt_plat_c(self):
        expected = [
            u'(c) Copyright 2008 Hewlett-Packard Development Company, L.P. Alan D. Brunelle <alan.brunelle@hp.com>',
        ]
        check_detection(expected, 'ics/blktrace-btt/plat.c')

    def test_ics_blktrace_btt_q2d_c(self):
        expected = [
            u'(c) Copyright 2007 Hewlett-Packard Development Company, L.P.',
        ]
        check_detection(expected, 'ics/blktrace-btt/q2d.c')

    def test_ics_blktrace_doc_blktrace_tex(self):
        expected = [
            u'Copyright (c) 2005, 2006 Alan D. Brunelle <Alan.Brunelle@hp.com>',
        ]
        check_detection(expected, 'ics/blktrace-doc/blktrace.tex')

    def test_ics_bluetooth_bluez_android_mk(self):
        expected = [
            u'Copyright (c) 2008 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/bluetooth-bluez/Android.mk')

    def test_ics_bluetooth_bluez_copying_lib(self):
        expected = [
            u'Copyright (c) 1991, 1999 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, 'ics/bluetooth-bluez/COPYING.LIB')

    def test_ics_bluetooth_bluez_notice(self):
        expected = [
            u'Copyright (c) 2004-2008 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2004-2009 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2006-2007 Nokia Corporation',
            u'Copyright (c) 2006-2009 Nokia Corporation',
            u'Copyright (c) 2008 Joao Paulo Rechi Vita',
            u'Copyright (c) 2008-2009 Leonid Movshovich <event.riga@gmail.org>',
            u'Copyright (c) 2008-2009 Nokia Corporation',
            u'Copyright (c) 2009 Lennart Poettering',
            u'Copyright (c) 2009 Intel Corporation',
            u'Copyright (c) 2009 Joao Paulo Rechi Vita',
            u'Copyright (c) 2009-2010 Motorola Inc.',
            u'Copyright (c) 2004-2005 Henryk Ploetz <henryk@ploetzli.ch>',
            u'Copyright (c) 2004-2008 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2004-2009 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2005-2006 Brad Midgley <bmidgley@xmission.com>',
            u'Copyright (c) 2005-2008 Brad Midgley <bmidgley@xmission.com>',
            u'Copyright (c) 2006-2007 Nokia Corporation',
            u'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
            u'Copyright (c) 1991, 1999 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, 'ics/bluetooth-bluez/NOTICE')

    def test_ics_bluetooth_bluez_readme(self):
        expected = [
            u'Copyright (c) 2000-2001 Qualcomm Incorporated',
            u'Copyright (c) 2002-2003 Maxim Krasnyansky <maxk@qualcomm.com>',
            u'Copyright (c) 2002-2010 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez/README')

    def test_ics_bluetooth_bluez_attrib_att_c(self):
        expected = [
            u'Copyright (c) 2010 Nokia Corporation',
            u'Copyright (c) 2010 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-attrib/att.c')

    def test_ics_bluetooth_bluez_attrib_gatttool_h(self):
        expected = [
            u'Copyright (c) 2011 Nokia Corporation',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-attrib/gatttool.h')

    def test_ics_bluetooth_bluez_audio_a2dp_codecs_h(self):
        expected = [
            u'Copyright (c) 2006-2010 Nokia Corporation',
            u'Copyright (c) 2004-2010 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-audio/a2dp-codecs.h')

    def test_ics_bluetooth_bluez_audio_android_audio_hw_c(self):
        expected = [
            u'Copyright (c) 2008-2011 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-audio/android_audio_hw.c')

    def test_ics_bluetooth_bluez_audio_ctl_bluetooth_c(self):
        expected = [
            u'Copyright (c) 2004-2010 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-audio/ctl_bluetooth.c')

    def test_ics_bluetooth_bluez_audio_gateway_c(self):
        expected = [
            u'Copyright (c) 2006-2010 Nokia Corporation',
            u'Copyright (c) 2004-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2008-2009 Leonid Movshovich <event.riga@gmail.org>',
            u'Copyright (c) 2010 ProFUSION',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-audio/gateway.c')

    @expectedFailure
    def test_ics_bluetooth_bluez_audio_gateway_c_trail_name(self):
        expected = [
            u'Copyright (c) 2006-2010 Nokia Corporation',
            u'Copyright (c) 2004-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2008-2009 Leonid Movshovich <event.riga@gmail.org>',
            u'Copyright (c) 2010  ProFUSION embedded systems',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-audio/gateway.c')

    def test_ics_bluetooth_bluez_audio_liba2dp_c(self):
        expected = [
            u'Copyright (c) 2006-2007 Nokia Corporation',
            u'Copyright (c) 2004-2008 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-audio/liba2dp.c')

    def test_ics_bluetooth_bluez_audio_media_c(self):
        expected = [
            u'Copyright (c) 2006-2007 Nokia Corporation',
            u'Copyright (c) 2004-2009 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-audio/media.c')

    def test_ics_bluetooth_bluez_audio_sink_c(self):
        expected = [
            u'Copyright (c) 2006-2007 Nokia Corporation',
            u'Copyright (c) 2004-2009 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2009-2010 Motorola Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-audio/sink.c')

    def test_ics_bluetooth_bluez_audio_source_c(self):
        expected = [
            u'Copyright (c) 2006-2010 Nokia Corporation',
            u'Copyright (c) 2004-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2009 Joao Paulo Rechi Vita',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-audio/source.c')

    def test_ics_bluetooth_bluez_audio_telephony_maemo5_c(self):
        expected = [
            u'Copyright (c) 2008-2010 Nokia Corporation',
            u'Copyright (c) 2004-2010 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-audio/telephony-maemo5.c')

    def test_ics_bluetooth_bluez_audio_telephony_ofono_c(self):
        expected = [
            u'Copyright (c) 2009-2010 Intel Corporation',
            u'Copyright (c) 2006-2009 Nokia Corporation',
            u'Copyright (c) 2004-2010 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-audio/telephony-ofono.c')

    def test_ics_bluetooth_bluez_btio_btio_c(self):
        expected = [
            u'Copyright (c) 2009-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2009-2010 Nokia Corporation',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-btio/btio.c')

    def test_ics_bluetooth_bluez_common_android_bluez_c(self):
        expected = [
            u'Copyright (c) 2004-2009 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2009 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-common/android_bluez.c')

    def test_ics_bluetooth_bluez_compat_bnep_c(self):
        expected = [
            u'Copyright (c) 2002-2003 Maxim Krasnyansky <maxk@qualcomm.com>',
            u'Copyright (c) 2002-2010 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-compat/bnep.c')

    def test_ics_bluetooth_bluez_compat_fakehid_c(self):
        expected = [
            u'Copyright (c) 2003-2010 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-compat/fakehid.c')

    def test_ics_bluetooth_bluez_doc_adapter_api_txt(self):
        expected = [
            u'Copyright (c) 2004-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2005-2006 Johan Hedberg <johan.hedberg@nokia.com>',
            u'Copyright (c) 2005-2006 Claudio Takahasi <claudio.takahasi@indt.org.br>',
            u'Copyright (c) 2006-2007 Luiz von Dentz',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-doc/adapter-api.txt')

    def test_ics_bluetooth_bluez_doc_agent_api_txt(self):
        expected = [
            u'Copyright (c) 2004-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2005-2006 Johan Hedberg <johan.hedberg@nokia.com>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-doc/agent-api.txt')

    def test_ics_bluetooth_bluez_doc_attribute_api_txt(self):
        expected = [
            u'Copyright (c) 2004-2010 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-doc/attribute-api.txt')

    def test_ics_bluetooth_bluez_doc_audio_api_txt(self):
        expected = [
            u'Copyright (c) 2004-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2005-2007 Johan Hedberg <johan.hedberg@nokia.com>',
            u'Copyright (c) 2005-2006 Brad Midgley <bmidgley@xmission.com>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-doc/audio-api.txt')

    def test_ics_bluetooth_bluez_doc_control_api_txt(self):
        expected = [
            u'Copyright (c) 2004-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2007-2008 David Stockwell <dstockwell@frequency-one.com>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-doc/control-api.txt')

    def test_ics_bluetooth_bluez_doc_mgmt_api_txt(self):
        expected = [
            u'Copyright (c) 2008-2009 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-doc/mgmt-api.txt')

    def test_ics_bluetooth_bluez_doc_oob_api_txt(self):
        expected = [
            u'Copyright (c) 2011 Szymon Janc <szymon.janc@tieto.com>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-doc/oob-api.txt')

    def test_ics_bluetooth_bluez_doc_sap_api_txt(self):
        expected = [
            u'Copyright (c) 2010 ST-Ericsson SA',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-doc/sap-api.txt')

    def test_ics_bluetooth_bluez_gdbus_gdbus_h(self):
        expected = [
            u'Copyright (c) 2004-2011 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-gdbus/gdbus.h')

    def test_ics_bluetooth_bluez_gdbus_notice(self):
        expected = [
            u'Copyright (c) 2004-2009 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-gdbus/NOTICE')

    def test_ics_bluetooth_bluez_health_hdp_c(self):
        expected = [
            u'Copyright (c) 2010 GSyC/LibreSoft, Universidad Rey Juan Carlos.'
        ]
        check_detection(expected, 'ics/bluetooth-bluez-health/hdp.c')

    def test_ics_bluetooth_bluez_health_mcap_c(self):
        expected = [
            u'Copyright (c) 2010 GSyC/LibreSoft, Universidad Rey Juan Carlos.',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-health/mcap.c')

    def test_ics_bluetooth_bluez_health_mcap_h(self):
        expected = [
            u'Copyright (c) 2010 GSyC/LibreSoft, Universidad Rey Juan Carlos.',
            u'Copyright (c) 2010 Signove',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-health/mcap.h')

    def test_ics_bluetooth_bluez_lib_bluetooth_c(self):
        expected = [
            u'Copyright (c) 2000-2001 Qualcomm Incorporated',
            u'Copyright (c) 2002-2003 Maxim Krasnyansky <maxk@qualcomm.com>',
            u'Copyright (c) 2002-2010 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-lib/bluetooth.c')

    def test_ics_bluetooth_bluez_lib_notice(self):
        expected = [
            u'Copyright (c) 2000-2001 Qualcomm Incorporated',
            u'Copyright (c) 2001-2002 Nokia Corporation',
            u'Copyright (c) 2002-2003 Maxim Krasnyansky <maxk@qualcomm.com>',
            u'Copyright (c) 2002-2003 Stephen Crane <steve.crane@rococosoft.com>',
            u'Copyright (c) 2002-2009 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2001-2002 Nokia Corporation',
            u'Copyright (c) 2002-2003 Maxim Krasnyansky <maxk@qualcomm.com>',
            u'Copyright (c) 2002-2009 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2002-2003 Stephen Crane <steve.crane@rococosoft.com>',
            u'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-lib/NOTICE')

    def test_ics_bluetooth_bluez_lib_sdp_c(self):
        expected = [
            u'Copyright (c) 2001-2002 Nokia Corporation',
            u'Copyright (c) 2002-2003 Maxim Krasnyansky <maxk@qualcomm.com>',
            u'Copyright (c) 2002-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2002-2003 Stephen Crane <steve.crane@rococosoft.com>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-lib/sdp.c')

    def test_ics_bluetooth_bluez_lib_uuid_c(self):
        expected = [
            u'Copyright (c) 2011 Nokia Corporation',
            u'Copyright (c) 2011 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-lib/uuid.c')

    def test_ics_bluetooth_bluez_lib_bluetooth_cmtp_h(self):
        expected = [
            u'Copyright (c) 2002-2010 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-lib-bluetooth/cmtp.h')

    def test_ics_bluetooth_bluez_plugins_builtin_h(self):
        expected = [
            u'Copyright (c) 2004-2009 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-plugins/builtin.h')

    def test_ics_bluetooth_bluez_plugins_dbusoob_c(self):
        expected = [
            u'Copyright (c) 2011 ST-Ericsson SA',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-plugins/dbusoob.c')

    def test_ics_bluetooth_bluez_sap_main_c_trail_institut(self):
        expected = [
            u'Copyright (c) 2010 Instituto Nokia de Tecnologia - INdT',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-sap/main.c')

    def test_ics_bluetooth_bluez_sap_sap_h_trail_institut(self):
        expected = [
            u'Copyright (c) 2010 Instituto Nokia de Tecnologia - INdT',
            u'Copyright (c) 2010 ST-Ericsson SA',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-sap/sap.h')

    def test_ics_bluetooth_bluez_sap_sap_dummy_c(self):
        expected = [
            u'Copyright (c) 2010 ST-Ericsson SA',
            u'Copyright (c) 2011 Tieto Poland',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-sap/sap-dummy.c')

    def test_ics_bluetooth_bluez_sap_server_c_trail_institut(self):
        expected = [
            u'Copyright (c) 2010 Instituto Nokia de Tecnologia - INdT',
            u'Copyright (c) 2010 ST-Ericsson SA',
            u'Copyright (c) 2011 Tieto Poland',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-sap/server.c')

    def test_ics_bluetooth_bluez_sap_server_h(self):
        expected = [
            u'Copyright (c) 2010 ST-Ericsson SA',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-sap/server.h')

    def test_ics_bluetooth_bluez_sbc_formats_h(self):
        expected = [
            u'Copyright (c) 2004-2010 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-sbc/formats.h')

    def test_ics_bluetooth_bluez_sbc_sbc_c(self):
        expected = [
            u'Copyright (c) 2008-2010 Nokia Corporation',
            u'Copyright (c) 2004-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2004-2005 Henryk Ploetz <henryk@ploetzli.ch>',
            u'Copyright (c) 2005-2008 Brad Midgley <bmidgley@xmission.com>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-sbc/sbc.c')

    def test_ics_bluetooth_bluez_sbc_sbc_h(self):
        expected = [
            u'Copyright (c) 2008-2010 Nokia Corporation',
            u'Copyright (c) 2004-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2004-2005 Henryk Ploetz <henryk@ploetzli.ch>',
            u'Copyright (c) 2005-2006 Brad Midgley <bmidgley@xmission.com>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-sbc/sbc.h')

    def test_ics_bluetooth_bluez_sbc_sbc_primitives_iwmmxt_c(self):
        expected = [
            u'Copyright (c) 2010 Keith Mok <ek9852@gmail.com>',
            u'Copyright (c) 2008-2010 Nokia Corporation',
            u'Copyright (c) 2004-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2004-2005 Henryk Ploetz <henryk@ploetzli.ch>',
            u'Copyright (c) 2005-2006 Brad Midgley <bmidgley@xmission.com>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-sbc/sbc_primitives_iwmmxt.c')

    def test_ics_bluetooth_bluez_sbc_sbcdec_c_lead_copy(self):
        expected = [
            u'Copyright (c) 2008-2010 Nokia Corporation',
            u'Copyright (c) 2004-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2004-2010 Marcel Holtmann',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-sbc/sbcdec.c')

    def test_ics_bluetooth_bluez_sbc_sbctester_c(self):
        expected = [
            u'Copyright (c) 2008-2010 Nokia Corporation',
            u'Copyright (c) 2007-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2007-2008 Frederic Dalleau <fdalleau@free.fr>',
            u'Copyright (c) 2007-2010 Marcel Holtmann',
            u'Copyright (c) 2007-2008 Frederic Dalleau',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-sbc/sbctester.c')

    def test_ics_bluetooth_bluez_src_dbus_common_c(self):
        expected = [
            u'Copyright (c) 2006-2010 Nokia Corporation',
            u'Copyright (c) 2004-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2005-2007 Johan Hedberg <johan.hedberg@nokia.com>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-src/dbus-common.c')

    def test_ics_bluetooth_bluez_src_error_c(self):
        expected = [
            u'Copyright (c) 2006-2010 Nokia Corporation',
            u'Copyright (c) 2004-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2007-2008 Fabien Chevalier <fabchevalier@free.fr>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-src/error.c')

    def test_ics_bluetooth_bluez_src_notice(self):
        expected = [
            u'Copyright (c) 2000-2001 Qualcomm Incorporated',
            u'Copyright (c) 2002-2003 Maxim Krasnyansky <maxk@qualcomm.com>',
            u'Copyright (c) 2002-2009 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-src/NOTICE')

    def test_ics_bluetooth_bluez_src_sdp_xml_c(self):
        expected = [
            u'Copyright (c) 2005-2010 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-src/sdp-xml.c')

    def test_ics_bluetooth_bluez_test_attest_c(self):
        expected = [
            u'Copyright (c) 2001-2010 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-test/attest.c')

    def test_ics_bluetooth_bluez_test_avtest_c(self):
        expected = [
            u'Copyright (c) 2007-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2009-2010 Nokia Corporation',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-test/avtest.c')

    def test_ics_bluetooth_bluez_test_gaptest_c(self):
        expected = [
            u'Copyright (c) 2007-2010 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-test/gaptest.c')

    def test_ics_bluetooth_bluez_test_hciemu_c(self):
        expected = [
            u'Copyright (c) 2000-2002 Maxim Krasnyansky <maxk@qualcomm.com>',
            u'Copyright (c) 2003-2010 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-test/hciemu.c')

    def test_ics_bluetooth_bluez_test_ipctest_c(self):
        expected = [
            u'Copyright (c) 2006-2010 Nokia Corporation',
            u'Copyright (c) 2004-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2009 Lennart Poettering',
            u'Copyright (c) 2008 Joao Paulo Rechi Vita',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-test/ipctest.c')

    def test_ics_bluetooth_bluez_test_notice(self):
        expected = [
            u'Copyright (c) 2000-2001 Qualcomm Incorporated',
            u'Copyright (c) 2000-2002 Maxim Krasnyansky <maxk@qualcomm.com>',
            u'Copyright (c) 2001-2009 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2002-2003 Maxim Krasnyansky <maxk@qualcomm.com>',
            u'Copyright (c) 2002-2009 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2003-2009 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2004-2009 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2005-2009 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2007-2009 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2009 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2009 Nokia Corporation',
            u'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-test/NOTICE')

    def test_ics_bluetooth_bluez_tools_hciattach_ath3k_c(self):
        expected = [
            u'Copyright (c) 2009-2010 Atheros Communications Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-tools/hciattach_ath3k.c')

    def test_ics_bluetooth_bluez_tools_hciattach_qualcomm_c(self):
        expected = [
            u'Copyright (c) 2005-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2010, Code Aurora Forum.',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-tools/hciattach_qualcomm.c')

    def test_ics_bluetooth_bluez_tools_hciattach_ti_c(self):
        expected = [
            u'Copyright (c) 2007-2008 Texas Instruments, Inc.',
            u'Copyright (c) 2005-2010 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-tools/hciattach_ti.c')

    def test_ics_bluetooth_bluez_tools_hid2hci_c(self):
        expected = [
            u'Copyright (c) 2003-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2008-2009 Mario Limonciello <mario_limonciello@dell.com>',
            u'Copyright (c) 2009-2011 Kay Sievers <kay.sievers@vrfy.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-tools/hid2hci.c')

    def test_ics_bluetooth_bluez_tools_lexer_c(self):
        expected = [
            u'Copyright (c) 2002-2008 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-tools/lexer.c')

    def test_ics_bluetooth_bluez_tools_notice(self):
        expected = [
            u'Copyright (c) 2000-2001 Qualcomm Incorporated',
            u'Copyright (c) 2001-2002 Nokia Corporation',
            u'Copyright (c) 2002-2003 Jean Tourrilhes <jt@hpl.hp.com>',
            u'Copyright (c) 2002-2003 Maxim Krasnyansky <maxk@qualcomm.com>',
            u'Copyright (c) 2002-2003 Stephen Crane <steve.crane@rococosoft.com>',
            u'Copyright (c) 2002-2009 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2003-2009 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2004-2009 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2005-2009 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2006-2007 Nokia Corporation',
            u'Copyright (c) 2007-2008 Texas Instruments, Inc.',
            u'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-tools/NOTICE')

    def test_ics_bluetooth_bluez_tools_sdptool_c(self):
        expected = [
            u'Copyright (c) 2001-2002 Nokia Corporation',
            u'Copyright (c) 2002-2003 Maxim Krasnyansky <maxk@qualcomm.com>',
            u'Copyright (c) 2002-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2002-2003 Stephen Crane <steve.crane@rococosoft.com>',
            u'Copyright (c) 2002-2003 Jean Tourrilhes <jt@hpl.hp.com>',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-tools/sdptool.c')

    def test_ics_bluetooth_bluez_tools_ubcsp_c(self):
        expected = [
            u'Copyright (c) 2000-2005 CSR Ltd.',
        ]
        check_detection(expected, 'ics/bluetooth-bluez-tools/ubcsp.c')

    def test_ics_bluetooth_glib_acinclude_m4(self):
        expected = [
            u'Copyright (c) 2001-2002 Free Software Foundation, Inc.',
            u'Copyright (c) 1999-2003 Free Software Foundation, Inc.',
            u'Copyright (c) 2002 Free Software Foundation, Inc.',
            u'Copyright (c) 2002 Free Software Foundation, Inc.',
            u'Copyright (c) 2003 Free Software Foundation, Inc.',
            u'Copyright (c) 1997-2002 Free Software Foundation, Inc.',
            u'Copyright (c) 1997-2002 Free Software Foundation, Inc.',
            u'Copyright (c) 1997-2002 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib/acinclude.m4')

    def test_ics_bluetooth_glib_copying(self):
        expected = [
            u'Copyright (c) 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, 'ics/bluetooth-glib/COPYING')

    def test_ics_bluetooth_glib_glib_h(self):
        expected = [
            u'Copyright (c) 1995-1997 Peter Mattis, Spencer Kimball and Josh MacDonald',
        ]
        check_detection(expected, 'ics/bluetooth-glib/glib.h')

    def test_ics_bluetooth_glib_glib_gettextize_in(self):
        expected = [
            u'Copyright (c) 1995-1998, 2000, 2001 Free Software Foundation, Inc.',
            u'Copyright (c) 1995-1998, 2000, 2001 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib/glib-gettextize.in')

    def test_ics_bluetooth_glib_docs_reference_glib_regex_syntax_sgml(self):
        expected = [
            u'Copyright (c) 1997-2006 University of Cambridge.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-docs-reference-glib/regex-syntax.sgml')

    def test_ics_bluetooth_glib_gio_gappinfo_c(self):
        expected = [
            u'Copyright (c) 2006-2007 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio/gappinfo.c')

    def test_ics_bluetooth_glib_gio_gbufferedinputstream_c(self):
        expected = [
            u'Copyright (c) 2006-2007 Red Hat, Inc.',
            u'Copyright (c) 2007 Jurg Billeter',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio/gbufferedinputstream.c')

    def test_ics_bluetooth_glib_gio_gdatainputstream_c(self):
        expected = [
            u'Copyright (c) 2006-2007 Red Hat, Inc.',
            u'Copyright (c) 2007 Jurg Billeter',
            u'Copyright (c) 2009 Codethink Limited',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio/gdatainputstream.c')

    def test_ics_bluetooth_glib_gio_gdesktopappinfo_c(self):
        expected = [
            u'Copyright (c) 2006-2007 Red Hat, Inc.',
            u'Copyright (c) 2007 Ryan Lortie',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio/gdesktopappinfo.c')

    def test_ics_bluetooth_glib_gio_gemblem_c(self):
        expected = [
            u'Copyright (c) 2008 Clemens N. Buss <cebuzz@gmail.com>',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio/gemblem.c')

    def test_ics_bluetooth_glib_gio_gmount_c(self):
        expected = [
            u'Copyright (c) 2006-2008 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio/gmount.c')

    def test_ics_bluetooth_glib_gio_gwin32mount_c(self):
        expected = [
            u'Copyright (c) 2006-2007 Red Hat, Inc.',
            u'Copyright (c) 2008 Hans Breuer',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio/gwin32mount.c')

    def test_ics_bluetooth_glib_gio_fam_fam_module_c(self):
        expected = [
            u'Copyright (c) 2006-2007 Red Hat, Inc.',
            u'Copyright (c) 2007 Sebastian Droge.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio-fam/fam-module.c')

    def test_ics_bluetooth_glib_gio_fen_fen_data_c(self):
        expected = [
            u'Copyright (c) 2008 Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio-fen/fen-data.c')

    def test_ics_bluetooth_glib_gio_fen_gfendirectorymonitor_c(self):
        expected = [
            u'Copyright (c) 2006-2007 Red Hat, Inc.',
            u'Copyright (c) 2007 Sebastian Droge.',
            u'Copyright (c) 2008 Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio-fen/gfendirectorymonitor.c')

    def test_ics_bluetooth_glib_gio_inotify_inotify_diag_c(self):
        expected = [
            u'Copyright (c) 2005 John McCutchan',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio-inotify/inotify-diag.c')

    def test_ics_bluetooth_glib_gio_inotify_inotify_diag_h(self):
        expected = [
            u'Copyright (c) 2006 John McCutchan <john@johnmccutchan.com>',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio-inotify/inotify-diag.h')

    def test_ics_bluetooth_glib_gio_inotify_inotify_helper_c(self):
        expected = [
            u'Copyright (c) 2007 John McCutchan',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio-inotify/inotify-helper.c')

    def test_ics_bluetooth_glib_gio_inotify_inotify_path_c(self):
        expected = [
            u'Copyright (c) 2006 John McCutchan',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio-inotify/inotify-path.c')

    def test_ics_bluetooth_glib_gio_tests_buffered_input_stream_c(self):
        expected = [
            u'Copyright (c) 2008 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio-tests/buffered-input-stream.c')

    def test_ics_bluetooth_glib_gio_tests_desktop_app_info_c(self):
        expected = [
            u'Copyright (c) 2008 Red Hat, Inc',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio-tests/desktop-app-info.c')

    def test_ics_bluetooth_glib_gio_tests_filter_streams_c(self):
        expected = [
            u'Copyright (c) 2009 Codethink Limited',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio-tests/filter-streams.c')

    def test_ics_bluetooth_glib_gio_tests_memory_input_stream_c(self):
        expected = [
            u'Copyright (c) 2007 Imendio AB',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio-tests/memory-input-stream.c')

    def test_ics_bluetooth_glib_gio_tests_simple_async_result_c(self):
        expected = [
            u'Copyright (c) 2009 Ryan Lortie',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio-tests/simple-async-result.c')

    def test_ics_bluetooth_glib_gio_win32_gwinhttpfile_c(self):
        expected = [
            u'Copyright (c) 2006-2007 Red Hat, Inc.',
            u'Copyright (c) 2008 Novell, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio-win32/gwinhttpfile.c')

    def test_ics_bluetooth_glib_gio_win32_winhttp_h(self):
        expected = [
            u'Copyright (c) 2007 Francois Gouget',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio-win32/winhttp.h')

    def test_ics_bluetooth_glib_gio_xdgmime_test_mime_c(self):
        expected = [
            u'Copyright (c) 2003,2004 Red Hat, Inc.',
            u'Copyright (c) 2003,2004 Jonathan Blandford <jrb@alum.mit.edu>',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio-xdgmime/test-mime.c')

    def test_ics_bluetooth_glib_gio_xdgmime_xdgmime_h(self):
        expected = [
            u'Copyright (c) 2003 Red Hat, Inc.',
            u'Copyright (c) 2003 Jonathan Blandford <jrb@alum.mit.edu>',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio-xdgmime/xdgmime.h')

    def test_ics_bluetooth_glib_gio_xdgmime_xdgmimealias_c(self):
        expected = [
            u'Copyright (c) 2004 Red Hat, Inc.',
            u'Copyright (c) 2004 Matthias Clasen <mclasen@redhat.com>',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio-xdgmime/xdgmimealias.c')

    def test_ics_bluetooth_glib_gio_xdgmime_xdgmimealias_h(self):
        expected = [
            u'Copyright (c) 2004 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio-xdgmime/xdgmimealias.h')

    def test_ics_bluetooth_glib_gio_xdgmime_xdgmimecache_c(self):
        expected = [
            u'Copyright (c) 2005 Matthias Clasen <mclasen@redhat.com>',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio-xdgmime/xdgmimecache.c')

    def test_ics_bluetooth_glib_gio_xdgmime_xdgmimeicon_c(self):
        expected = [
            u'Copyright (c) 2008 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio-xdgmime/xdgmimeicon.c')

    def test_ics_bluetooth_glib_gio_xdgmime_xdgmimemagic_c(self):
        expected = [
            u'Copyright (c) 2003 Red Hat, Inc.',
            u'Copyright (c) 2003 Jonathan Blandford <jrb@alum.mit.edu>',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gio-xdgmime/xdgmimemagic.c')

    def test_ics_bluetooth_glib_glib_gatomic_c(self):
        expected = [
            u'Copyright (c) 1995-1997 Peter Mattis, Spencer Kimball and Josh MacDonald',
            u'Copyright (c) 2003 Sebastian Wilhelmi',
            u'Copyright (c) 2007 Nokia Corporation',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gatomic.c')

    def test_ics_bluetooth_glib_glib_gatomic_h(self):
        expected = [
            u'Copyright (c) 1995-1997 Peter Mattis, Spencer Kimball and Josh MacDonald',
            u'Copyright (c) 2003 Sebastian Wilhelmi',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gatomic.h')

    def test_ics_bluetooth_glib_glib_gbase64_h(self):
        expected = [
            u'Copyright (c) 2005 Alexander Larsson <alexl@redhat.com>',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gbase64.h')

    def test_ics_bluetooth_glib_glib_gbookmarkfile_h(self):
        expected = [
            u'Copyright (c) 2005-2006 Emmanuele Bassi',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gbookmarkfile.h')

    def test_ics_bluetooth_glib_glib_gbsearcharray_h(self):
        expected = [
            u'Copyright (c) 2000-2003 Tim Janik',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gbsearcharray.h')

    def test_ics_bluetooth_glib_glib_gchecksum_h(self):
        expected = [
            u'Copyright (c) 2007 Emmanuele Bassi <ebassi@gnome.org>',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gchecksum.h')

    def test_ics_bluetooth_glib_glib_gconvert_c(self):
        expected = [
            u'Copyright Red Hat Inc., 2000',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gconvert.c')

    def test_ics_bluetooth_glib_glib_gdataset_c(self):
        expected = [
            u'Copyright (c) 1995-1997 Peter Mattis, Spencer Kimball and Josh MacDonald',
            u'Copyright (c) 1998 Tim Janik',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gdataset.c')

    def test_ics_bluetooth_glib_glib_gdatasetprivate_h(self):
        expected = [
            u'Copyright (c) 2005 Red Hat',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gdatasetprivate.h')

    def test_ics_bluetooth_glib_glib_gdir_c(self):
        expected = [
            u'Copyright (c) 1995-1997 Peter Mattis, Spencer Kimball and Josh MacDonald',
            u'Copyright 2001 Hans Breuer',
            u'Copyright 2004 Tor Lillqvist',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gdir.c')

    def test_ics_bluetooth_glib_glib_gdir_h(self):
        expected = [
            u'Copyright (c) 1995-1997 Peter Mattis, Spencer Kimball and Josh MacDonald',
            u'Copyright 2001 Hans Breuer',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gdir.h')

    def test_ics_bluetooth_glib_glib_gerror_h(self):
        expected = [
            u'Copyright 2000 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gerror.h')

    def test_ics_bluetooth_glib_glib_gfileutils_c(self):
        expected = [
            u'Copyright 2000 Red Hat, Inc.',
            u'Copyright (c) 1991,92,93,94,95,96,97,98,99 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gfileutils.c')

    def test_ics_bluetooth_glib_glib_gi18n_lib_h(self):
        expected = [
            u'Copyright (c) 1995-1997, 2002 Peter Mattis, Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gi18n-lib.h')

    def test_ics_bluetooth_glib_glib_giochannel_c(self):
        expected = [
            u'Copyright (c) 1995-1997 Peter Mattis, Spencer Kimball and Josh MacDonald',
            u'Copyright 1998 Owen Taylor',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/giochannel.c')

    def test_ics_bluetooth_glib_glib_gkeyfile_c(self):
        expected = [
            u'Copyright 2004 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gkeyfile.c')

    def test_ics_bluetooth_glib_glib_gkeyfile_h(self):
        expected = [
            u'Copyright 2004 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gkeyfile.h')

    def test_ics_bluetooth_glib_glib_glib_object_h(self):
        expected = [
            u'Copyright (c) 1998, 1999, 2000 Tim Janik and Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/glib-object.h')

    def test_ics_bluetooth_glib_glib_gmain_h(self):
        expected = [
            u'Copyright (c) 1998-2000 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gmain.h')

    def test_ics_bluetooth_glib_glib_gmappedfile_h(self):
        expected = [
            u'Copyright 2005 Matthias Clasen',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gmappedfile.h')

    def test_ics_bluetooth_glib_glib_goption_c(self):
        expected = [
            u'Copyright (c) 1999, 2003 Red Hat Software',
            u'Copyright (c) 2004 Anders Carlsson <andersca@gnome.org>',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/goption.c')

    def test_ics_bluetooth_glib_glib_goption_h(self):
        expected = [
            u'Copyright (c) 2004 Anders Carlsson <andersca@gnome.org>',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/goption.h')

    def test_ics_bluetooth_glib_glib_gpattern_c(self):
        expected = [
            u'Copyright (c) 1995-1997, 1999 Peter Mattis, Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gpattern.c')

    def test_ics_bluetooth_glib_glib_gpoll_c(self):
        expected = [
            u'Copyright (c) 1995-1997 Peter Mattis, Spencer Kimball and Josh MacDonald',
            u'Copyright 1998 Owen Taylor',
            u'Copyright 2008 Red Hat, Inc.',
            u'Copyright (c) 1994, 1996, 1997 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gpoll.c')

    def test_ics_bluetooth_glib_glib_gqsort_c(self):
        expected = [
            u'Copyright (c) 1991, 1992, 1996, 1997,1999,2004 Free Software Foundation, Inc.',
            u'Copyright (c) 2000 Eazel, Inc.',
            u'Copyright (c) 1995-1997 Peter Mattis, Spencer Kimball and Josh MacDonald',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gqsort.c')

    def test_ics_bluetooth_glib_glib_gregex_h(self):
        expected = [
            u'Copyright (c) 1999, 2000 Scott Wimer',
            u'Copyright (c) 2004, Matthias Clasen <mclasen@redhat.com>',
            u'Copyright (c) 2005 - 2007, Marco Barisione <marco@barisione.org>',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gregex.h')

    def test_ics_bluetooth_glib_glib_gsequence_h(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007 Soeren Sandmann (sandmann@daimi.au.dk)',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gsequence.h')

    def test_ics_bluetooth_glib_glib_gslice_c(self):
        expected = [
            u'Copyright (c) 2005 Tim Janik',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gslice.c')

    def test_ics_bluetooth_glib_glib_gstdio_c(self):
        expected = [
            u'Copyright 2004 Tor Lillqvist',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gstdio.c')

    def test_ics_bluetooth_glib_glib_gstrfuncs_c(self):
        expected = [
            u'Copyright (c) 1995-1997 Peter Mattis, Spencer Kimball and Josh MacDonald',
            u'Copyright (c) 1991,92,94,95,96,97,98,99,2000,01,02 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gstrfuncs.c')

    def test_ics_bluetooth_glib_glib_gstring_c(self):
        expected = [
            u'Copyright (c) 1995-1997 Peter Mattis, Spencer Kimball and Josh MacDonald',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gstring.c')

    def test_ics_bluetooth_glib_glib_gtestutils_c(self):
        expected = [
            u'Copyright (c) 2007 Imendio AB',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gtestutils.c')

    def test_ics_bluetooth_glib_glib_gthread_c(self):
        expected = [
            u'Copyright (c) 1995-1997 Peter Mattis, Spencer Kimball and Josh MacDonald',
            u'Copyright 1998 Sebastian Wilhelmi University of Karlsruhe Owen Taylor',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gthread.c')

    def test_ics_bluetooth_glib_glib_gthreadprivate_h(self):
        expected = [
            u'Copyright (c) 2003 Sebastian Wilhelmi',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gthreadprivate.h')

    def test_ics_bluetooth_glib_glib_gunicode_h(self):
        expected = [
            u'Copyright (c) 1999, 2000 Tom Tromey',
            u'Copyright 2000, 2005 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gunicode.h')

    def test_ics_bluetooth_glib_glib_gunicodeprivate_h(self):
        expected = [
            u'Copyright (c) 2003 Noah Levitt',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gunicodeprivate.h')

    def test_ics_bluetooth_glib_glib_gunidecomp_c(self):
        expected = [
            u'Copyright (c) 1999, 2000 Tom Tromey',
            u'Copyright 2000 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gunidecomp.c')

    def test_ics_bluetooth_glib_glib_guniprop_c(self):
        expected = [
            u'Copyright (c) 1999 Tom Tromey',
            u'Copyright (c) 2000 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/guniprop.c')

    def test_ics_bluetooth_glib_glib_gutils_c(self):
        expected = [
            u'Copyright (c) 1995-1998 Peter Mattis, Spencer Kimball and Josh MacDonald',
            u'Copyright (c) 2007 Red Hat Inc.',
            u'Copyright (c) 1995, 1996, 1997, 1998 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib/gutils.c')

    def test_ics_bluetooth_glib_glib_gnulib_asnprintf_c(self):
        expected = [
            u'Copyright (c) 1999, 2002 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib-gnulib/asnprintf.c')

    def test_ics_bluetooth_glib_glib_gnulib_g_gnulib_h(self):
        expected = [
            u'Copyright (c) 2003 Matthias Clasen',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib-gnulib/g-gnulib.h')

    def test_ics_bluetooth_glib_glib_gnulib_printf_c(self):
        expected = [
            u'Copyright (c) 2003 Matthias Clasen',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib-gnulib/printf.c')

    def test_ics_bluetooth_glib_glib_gnulib_printf_args_c(self):
        expected = [
            u'Copyright (c) 1999, 2002-2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib-gnulib/printf-args.c')

    def test_ics_bluetooth_glib_glib_gnulib_printf_parse_c(self):
        expected = [
            u'Copyright (c) 1999-2000, 2002-2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib-gnulib/printf-parse.c')

    def test_ics_bluetooth_glib_glib_gnulib_vasnprintf_h(self):
        expected = [
            u'Copyright (c) 2002-2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-glib-gnulib/vasnprintf.h')

    def test_ics_bluetooth_glib_gmodule_gmodule_c(self):
        expected = [
            u'Copyright (c) 1998 Tim Janik',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gmodule/gmodule.c')

    def test_ics_bluetooth_glib_gmodule_gmodule_rc_in(self):
        expected = [
            u'Copyright (c) 1998-2000 Tim Janik.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gmodule/gmodule.rc.in')

    def test_ics_bluetooth_glib_gmodule_gmodule_ar_c(self):
        expected = [
            u'Copyright (c) 1998, 2000 Tim Janik',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gmodule/gmodule-ar.c')

    def test_ics_bluetooth_glib_gmodule_gmodule_beos_c_trail_name(self):
        expected = [
            u'Copyright (c) 1998, 2000 Tim Janik',
            u'Copyright (c) 1999 Richard Offer and Shawn T. Amundson (amundson@gtk.org)',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gmodule/gmodule-beos.c')

    def test_ics_bluetooth_glib_gmodule_gmodule_dyld_c(self):
        expected = [
            u'Copyright (c) 1998, 2000 Tim Janik',
            u'Copyright (c) 2001 Dan Winship',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gmodule/gmodule-dyld.c')

    def test_ics_bluetooth_glib_gmodule_gmodule_win32_c(self):
        expected = [
            u'Copyright (c) 1998, 2000 Tim Janik',
            u'Copyright (c) 1998 Tor Lillqvist',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gmodule/gmodule-win32.c')

    def test_ics_bluetooth_glib_gobject_gboxed_c(self):
        expected = [
            u'Copyright (c) 2000-2001 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gobject/gboxed.c')

    def test_ics_bluetooth_glib_gobject_gclosure_c(self):
        expected = [
            u'Copyright (c) 2000-2001 Red Hat, Inc.',
            u'Copyright (c) 2005 Imendio AB',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gobject/gclosure.c')

    def test_ics_bluetooth_glib_gobject_genums_c(self):
        expected = [
            u'Copyright (c) 1998-1999, 2000-2001 Tim Janik and Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gobject/genums.c')

    def test_ics_bluetooth_glib_gobject_gobject_rc_in(self):
        expected = [
            u'Copyright (c) 1998-2004 Tim Janik and Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gobject/gobject.rc.in')

    def test_ics_bluetooth_glib_gobject_gparam_c(self):
        expected = [
            u'Copyright (c) 1997-1999, 2000-2001 Tim Janik and Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gobject/gparam.c')

    def test_ics_bluetooth_glib_gobject_gsourceclosure_c(self):
        expected = [
            u'Copyright (c) 2001 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gobject/gsourceclosure.c')

    def test_ics_bluetooth_glib_gobject_gtypemodule_c(self):
        expected = [
            u'Copyright (c) 2000 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gobject/gtypemodule.c')

    def test_ics_bluetooth_glib_gobject_makefile_am(self):
        expected = [
            u'Copyright (c) 1997,98,99,2000 Tim Janik and Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gobject/Makefile.am')

    def test_ics_bluetooth_glib_gobject_tests_threadtests_c(self):
        expected = [
            u'Copyright (c) 2008 Imendio AB',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gobject-tests/threadtests.c')

    def test_ics_bluetooth_glib_gthread_gthread_rc_in(self):
        expected = [
            u'Copyright (c) 1995-1997 Peter Mattis, Spencer Kimball and Josh MacDonald.',
            u'Copyright (c) 1998 Sebastian Wilhelmi.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gthread/gthread.rc.in')

    def test_ics_bluetooth_glib_gthread_gthread_win32_c(self):
        expected = [
            u'Copyright (c) 1995-1997 Peter Mattis, Spencer Kimball and Josh MacDonald',
            u'Copyright 1998-2001 Sebastian Wilhelmi University of Karlsruhe',
            u'Copyright 2001 Hans Breuer',
        ]
        check_detection(expected, 'ics/bluetooth-glib-gthread/gthread-win32.c')

    def test_ics_bluetooth_glib_m4macros_glib_gettext_m4(self):
        expected = [
            u'Copyright (c) 1995-2002 Free Software Foundation, Inc.',
            u'Copyright (c) 2001-2003,2004 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-m4macros/glib-gettext.m4')

    def test_ics_bluetooth_glib_po_makefile_in_in(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997 by Ulrich Drepper <drepper@gnu.ai.mit.edu>',
        ]
        check_detection(expected, 'ics/bluetooth-glib-po/Makefile.in.in')

    def test_ics_bluetooth_glib_po_po2tbl_sed_in(self):
        expected = [
            u'Copyright (c) 1995 Free Software Foundation, Inc. Ulrich Drepper <drepper@gnu.ai.mit.edu>',
        ]
        check_detection(expected, 'ics/bluetooth-glib-po/po2tbl.sed.in')

    def test_ics_bluetooth_glib_tests_gio_test_c(self):
        expected = [
            u'Copyright (c) 2000 Tor Lillqvist',
        ]
        check_detection(expected, 'ics/bluetooth-glib-tests/gio-test.c')

    def test_ics_bluetooth_glib_tests_hash_test_c(self):
        expected = [
            u'Copyright (c) 1995-1997 Peter Mattis, Spencer Kimball and Josh MacDonald',
            u'Copyright (c) 1999 The Free Software Foundation',
        ]
        check_detection(expected, 'ics/bluetooth-glib-tests/hash-test.c')

    def test_ics_bluetooth_glib_tests_mapping_test_c(self):
        expected = [
            u'Copyright (c) 2005 Matthias Clasen',
        ]
        check_detection(expected, 'ics/bluetooth-glib-tests/mapping-test.c')

    def test_ics_bluetooth_glib_tests_markup_collect_c(self):
        expected = [
            u'Copyright (c) 2007 Ryan Lortie',
        ]
        check_detection(expected, 'ics/bluetooth-glib-tests/markup-collect.c')

    def test_ics_bluetooth_glib_tests_onceinit_c(self):
        expected = [
            u'Copyright (c) 2007 Tim Janik',
        ]
        check_detection(expected, 'ics/bluetooth-glib-tests/onceinit.c')

    def test_ics_bluetooth_glib_tests_patterntest_c(self):
        expected = [
            u'Copyright (c) 2001 Matthias Clasen <matthiasc@poet.de>',
        ]
        check_detection(expected, 'ics/bluetooth-glib-tests/patterntest.c')

    def test_ics_bluetooth_glib_tests_regex_test_c(self):
        expected = [
            u'Copyright (c) 2005 - 2006, Marco Barisione <marco@barisione.org>',
        ]
        check_detection(expected, 'ics/bluetooth-glib-tests/regex-test.c')

    def test_ics_bluetooth_glib_tests_scannerapi_c(self):
        expected = [
            u'Copyright (c) 2007 Patrick Hulin',
            u'Copyright (c) 2007 Imendio AB',
        ]
        check_detection(expected, 'ics/bluetooth-glib-tests/scannerapi.c')

    def test_ics_bluetooth_glib_tests_slice_concurrent_c(self):
        expected = [
            u'Copyright (c) 2006 Stefan Westerfeld',
            u'Copyright (c) 2007 Tim Janik',
        ]
        check_detection(expected, 'ics/bluetooth-glib-tests/slice-concurrent.c')

    def test_ics_bluetooth_glib_tests_testingbase64_c(self):
        expected = [
            u'Copyright (c) 2008 Asbjoern Pettersen',
        ]
        check_detection(expected, 'ics/bluetooth-glib-tests/testingbase64.c')

    def test_ics_bluetooth_glib_tests_gobject_accumulator_c(self):
        expected = [
            u'Copyright (c) 2001, 2003 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-tests-gobject/accumulator.c')

    def test_ics_bluetooth_glib_tests_gobject_deftype_c(self):
        expected = [
            u'Copyright (c) 2006 Behdad Esfahbod',
        ]
        check_detection(expected, 'ics/bluetooth-glib-tests-gobject/deftype.c')

    def test_ics_bluetooth_glib_tests_gobject_override_c(self):
        expected = [
            u'Copyright (c) 2001, James Henstridge',
            u'Copyright (c) 2003, Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-tests-gobject/override.c')

    def test_ics_bluetooth_glib_tests_gobject_references_c(self):
        expected = [
            u'Copyright (c) 2005 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-tests-gobject/references.c')

    def test_ics_bluetooth_glib_tests_gobject_singleton_c(self):
        expected = [
            u'Copyright (c) 2006 Imendio AB',
        ]
        check_detection(expected, 'ics/bluetooth-glib-tests-gobject/singleton.c')

    def test_ics_bluetooth_glib_tests_gobject_testcommon_h(self):
        expected = [
            u'Copyright (c) 2003 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/bluetooth-glib-tests-gobject/testcommon.h')

    def test_ics_bluetooth_glib_tests_refcount_closures_c(self):
        expected = [
            u'Copyright (c) 2005 Imendio AB',
        ]
        check_detection(expected, 'ics/bluetooth-glib-tests-refcount/closures.c')

    def test_ics_bluetooth_hcidump_readme(self):
        expected = [
            u'Copyright (c) 2000-2002 Maxim Krasnyansky <maxk@qualcomm.com>',
            u'Copyright (c) 2003-2011 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-hcidump/README')

    def test_ics_bluetooth_hcidump_parser_att_c(self):
        expected = [
            u'Copyright (c) 2011 Andre Dieb Martins <andre.dieb@gmail.com>',
        ]
        check_detection(expected, 'ics/bluetooth-hcidump-parser/att.c')

    def test_ics_bluetooth_hcidump_parser_bnep_c(self):
        expected = [
            u'Copyright (c) 2002-2003 Takashi Sasai <sasai@sm.sony.co.jp>',
            u'Copyright (c) 2003-2011 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-hcidump-parser/bnep.c')

    def test_ics_bluetooth_hcidump_parser_cmtp_c(self):
        expected = [
            u'Copyright (c) 2002-2011 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-hcidump-parser/cmtp.c')

    def test_ics_bluetooth_hcidump_parser_hci_c(self):
        expected = [
            u'Copyright (c) 2000-2002 Maxim Krasnyansky <maxk@qualcomm.com>',
            u'Copyright (c) 2003-2011 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-hcidump-parser/hci.c')

    def test_ics_bluetooth_hcidump_parser_hidp_c(self):
        expected = [
            u'Copyright (c) 2003-2011 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-hcidump-parser/hidp.c')

    def test_ics_bluetooth_hcidump_parser_rfcomm_c(self):
        expected = [
            u'Copyright (c) 2001-2002 Wayne Lee <waynelee@qualcomm.com>',
            u'Copyright (c) 2003-2011 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-hcidump-parser/rfcomm.c')

    def test_ics_bluetooth_hcidump_parser_sdp_c(self):
        expected = [
            u'Copyright (c) 2001-2002 Ricky Yuen <ryuen@qualcomm.com>',
            u'Copyright (c) 2003-2011 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/bluetooth-hcidump-parser/sdp.c')

    def test_ics_bouncycastle_notice(self):
        expected = [
            u'Copyright (c) 2000-2010 The Legion Of The Bouncy Castle (http://www.bouncycastle.org)',
        ]
        check_detection(expected, 'ics/bouncycastle/NOTICE')

    def test_ics_bouncycastle_src_main_java_org_bouncycastle_crypto_digests_openssldigest_java(self):
        expected = [
            u'Copyright (c) 2008 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/bouncycastle-src-main-java-org-bouncycastle-crypto-digests/OpenSSLDigest.java')

    def test_ics_bsdiff_bsdiff_1(self):
        expected = [
            u'Copyright 2003-2005 Colin Percival',
        ]
        check_detection(expected, 'ics/bsdiff/bsdiff.1')

    def test_ics_bsdiff_bsdiff_c(self):
        expected = [
            u'Copyright 2003-2005 Colin Percival',
        ]
        check_detection(expected, 'ics/bsdiff/bsdiff.c')

    def test_ics_bzip2_blocksort_c(self):
        expected = [
            u'Copyright (c) 1996-2010 Julian Seward <jseward@bzip.org>',
        ]
        check_detection(expected, 'ics/bzip2/blocksort.c')

    def test_ics_bzip2_bzip2_c(self):
        expected = [
            u'Copyright (c) 1996-2010 Julian Seward <jseward@bzip.org>',
            u'Copyright (c) 1996-2010 by Julian Seward.',
        ]
        check_detection(expected, 'ics/bzip2/bzip2.c')

    def test_ics_bzip2_license(self):
        expected = [
            u'copyright (c) 1996-2010 Julian R Seward.',
        ]
        check_detection(expected, 'ics/bzip2/LICENSE')

    def test_ics_bzip2_makefile(self):
        expected = [
            u'Copyright (c) 1996-2010 Julian Seward <jseward@bzip.org>',
        ]
        check_detection(expected, 'ics/bzip2/Makefile')

    def test_ics_bzip2_manual_html(self):
        expected = [
            u'Copyright (c) 1996-2010 Julian Seward',
            u'copyright (c) 1996-2010 Julian Seward.',
        ]
        check_detection(expected, 'ics/bzip2/manual.html')

    def test_ics_bzip2_xmlproc_sh(self):
        expected = [
            u'Copyright (c) 1996-2010 Julian Seward <jseward@bzip.org>',
        ]
        check_detection(expected, 'ics/bzip2/xmlproc.sh')

    def test_ics_chromium_license(self):
        expected = [
            u'Copyright (c) 2010 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium/LICENSE')

    def test_ics_chromium_android_execinfo_cc(self):
        expected = [
            u'Copyright (c) 2011 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-android/execinfo.cc')

    def test_ics_chromium_android_prefix_h(self):
        expected = [
            u'Copyright 2010, The Android Open Source Project',
        ]
        check_detection(expected, 'ics/chromium-android/prefix.h')

    def test_ics_chromium_android_jni_jni_utils_cc(self):
        expected = [
            u'Copyright (c) 2010 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-android-jni/jni_utils.cc')

    def test_ics_chromium_android_ui_base_l10n_l10n_util_cc(self):
        expected = [
            u'Copyright 2010, The Android Open Source Project',
        ]
        check_detection(expected, 'ics/chromium-android-ui-base-l10n/l10n_util.cc')

    def test_ics_chromium_app_sql_init_status_h(self):
        expected = [
            u'Copyright (c) 2009 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-app-sql/init_status.h')

    def test_ics_chromium_base_atomicops_internals_x86_gcc_cc(self):
        expected = [
            u'Copyright (c) 2006-2008 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-base/atomicops_internals_x86_gcc.cc')

    def test_ics_chromium_base_atomicops_internals_x86_gcc_h(self):
        expected = [
            u'Copyright (c) 2006-2008 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-base/atomicops_internals_x86_gcc.h')

    def test_ics_chromium_base_base_gyp(self):
        expected = [
            u'Copyright (c) 2011 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-base/base.gyp')

    def test_ics_chromium_base_compat_execinfo_h(self):
        expected = [
            u'Copyright (c) 2006-2009 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-base/compat_execinfo.h')

    def test_ics_chromium_base_file_version_info_h(self):
        expected = [
            u'Copyright (c) 2011 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-base/file_version_info.h')

    def test_ics_chromium_base_file_version_info_mac_mm(self):
        expected = [
            u'Copyright (c) 2011 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-base/file_version_info_mac.mm')

    def test_ics_chromium_base_foundation_utils_mac_h(self):
        expected = [
            u'Copyright (c) 2008 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-base/foundation_utils_mac.h')

    def test_ics_chromium_base_md5_cc(self):
        expected = [
            u'Copyright 2006 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-base/md5.cc')

    def test_ics_chromium_base_string_tokenizer_h(self):
        expected = [
            u'Copyright (c) 2010 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-base/string_tokenizer.h')

    def test_ics_chromium_base_allocator_allocator_gyp(self):
        expected = [
            u'Copyright (c) 2009 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-base-allocator/allocator.gyp')

    def test_ics_chromium_base_i18n_icu_string_conversions_cc(self):
        expected = [
            u'Copyright (c) 2009 The Chromium Authors.',
            u'Copyright (c) 1995-2006 International Business Machines Corporation and others',
        ]
        check_detection(expected, 'ics/chromium-base-i18n/icu_string_conversions.cc')

    def test_ics_chromium_base_third_party_dmg_fp_dtoa_cc(self):
        expected = [
            u'Copyright (c) 1991, 2000, 2001 by Lucent Technologies.',
        ]
        check_detection(expected, 'ics/chromium-base-third_party-dmg_fp/dtoa.cc')

    def test_ics_chromium_base_third_party_dmg_fp_g_fmt_cc(self):
        expected = [
            u'Copyright (c) 1991, 1996 by Lucent Technologies.',
        ]
        check_detection(expected, 'ics/chromium-base-third_party-dmg_fp/g_fmt.cc')

    def test_ics_chromium_base_third_party_dmg_fp_license(self):
        expected = [
            u'Copyright (c) 1991, 2000, 2001 by Lucent Technologies.',
        ]
        check_detection(expected, 'ics/chromium-base-third_party-dmg_fp/LICENSE')

    def test_ics_chromium_base_third_party_dmg_fp_thirdpartyproject_prop(self):
        expected = [
            u'Copyright 2011 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-base-third_party-dmg_fp/ThirdPartyProject.prop')

    def test_ics_chromium_base_third_party_dynamic_annotations_dynamic_annotations_c(self):
        expected = [
            u'Copyright (c) 2008-2009, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-base-third_party-dynamic_annotations/dynamic_annotations.c')

    def test_ics_chromium_base_third_party_dynamic_annotations_dynamic_annotations_gyp(self):
        expected = [
            u'Copyright (c) 2010 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-base-third_party-dynamic_annotations/dynamic_annotations.gyp')

    def test_ics_chromium_base_third_party_icu_icu_utf_cc_trail_other(self):
        expected = [
            u'Copyright (c) 1999-2006, International Business Machines Corporation and others.',
        ]
        check_detection(expected, 'ics/chromium-base-third_party-icu/icu_utf.cc')

    def test_ics_chromium_base_third_party_icu_icu_utf_h(self):
        expected = [
            u'Copyright (c) 1999-2004, International Business Machines Corporation and others.',
        ]
        check_detection(expected, 'ics/chromium-base-third_party-icu/icu_utf.h')

    def test_ics_chromium_base_third_party_icu_license_trail_other(self):
        expected = [
            u'Copyright (c) 1995-2009 International Business Machines Corporation and others',
        ]
        check_detection(expected, 'ics/chromium-base-third_party-icu/LICENSE')

    def test_ics_chromium_base_third_party_nspr_license(self):
        expected = [
            u'Copyright (c) 1998-2000 the Initial Developer.',
        ]
        check_detection(expected, 'ics/chromium-base-third_party-nspr/LICENSE')

    def test_ics_chromium_base_third_party_nspr_prcpucfg_h(self):
        expected = [
            u'Copyright 2008, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-base-third_party-nspr/prcpucfg.h')

    def test_ics_chromium_base_third_party_nspr_prtime_cc(self):
        expected = [
            u'Copyright (c) 2011 Google Inc',
            u'Copyright (c) 1998-2000 the Initial Developer.',
        ]
        check_detection(expected, 'ics/chromium-base-third_party-nspr/prtime.cc')

    def test_ics_chromium_build_branding_value_sh(self):
        expected = [
            u'Copyright (c) 2008 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-build/branding_value.sh')

    def test_ics_chromium_build_install_build_deps_sh(self):
        expected = [
            u'Copyright (c) 2011 The Chromium Authors.',
            u'Copyright 2006, 2007, 2008, 2009, 2010 Free Software Foundation, Inc.',
            u'Copyright 2006, 2007, 2008, 2009, 2010, 2011 Free Software Foundation, Inc.',
            u'Copyright 2006, 2007, 2008, 2009, 2010 Free Software Foundation, Inc.',
            u'Copyright 2006, 2007, 2008, 2009, 2010, 2011 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/chromium-build/install-build-deps.sh')

    def test_ics_chromium_build_whitespace_file_txt(self):
        expected = [
            u'Copyright (c) 2011 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-build/whitespace_file.txt')

    def test_ics_chromium_build_mac_strip_from_xcode(self):
        expected = [
            u'Copyright (c) 2008 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-build-mac/strip_from_xcode')

    def test_ics_chromium_chrome_browser_nacl_loader_sb(self):
        expected = [
            u'Copyright (c) 2011 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser/nacl_loader.sb')

    def test_ics_chromium_chrome_browser_chromeos_panels_panel_scroller_container_cc(self):
        expected = [
            u'Copyright (c) 2009 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-chromeos-panels/panel_scroller_container.cc')

    def test_ics_chromium_chrome_browser_cocoa_authorization_util_mm(self):
        expected = [
            u'Copyright (c) 2009 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-cocoa/authorization_util.mm')

    def test_ics_chromium_chrome_browser_download_download_extensions_cc(self):
        expected = [
            u'Copyright (c) 2010 The Chromium Authors.',
            u'Copyright (c) 1998-1999 the Initial Developer.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-download/download_extensions.cc')

    def test_ics_chromium_chrome_browser_importer_firefox_profile_lock_cc(self):
        expected = [
            u'Copyright (c) 2010 The Chromium Authors.',
            u'Copyright (c) 2002 the Initial Developer.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-importer/firefox_profile_lock.cc')

    def test_ics_chromium_chrome_browser_importer_firefox_profile_lock_posix_cc(self):
        expected = [
            u'Copyright (c) 2009 The Chromium Authors.',
            u'Copyright (c) 2002 the Initial Developer.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-importer/firefox_profile_lock_posix.cc')

    def test_ics_chromium_chrome_browser_importer_firefox_profile_lock_win_cc(self):
        expected = [
            u'Copyright (c) 2008 The Chromium Authors.',
            u'Copyright (c) 2002 the Initial Developer.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-importer/firefox_profile_lock_win.cc')

    def test_ics_chromium_chrome_browser_importer_mork_reader_cc(self):
        expected = [
            u'Copyright (c) 2006 the Initial Developer.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-importer/mork_reader.cc')

    def test_ics_chromium_chrome_browser_importer_nss_decryptor_cc(self):
        expected = [
            u'Copyright (c) 2011 The Chromium Authors.',
            u'Copyright (c) 1994-2000 the Initial Developer.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-importer/nss_decryptor.cc')

    def test_ics_chromium_chrome_browser_importer_nss_decryptor_mac_h(self):
        expected = [
            u'Copyright (c) 2010 The Chromium Authors.',
            u'Copyright (c) 1994-2000 the Initial Developer.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-importer/nss_decryptor_mac.h')

    def test_ics_chromium_chrome_browser_importer_nss_decryptor_win_h(self):
        expected = [
            u'Copyright (c) 2009 The Chromium Authors.',
            u'Copyright (c) 1994-2000 the Initial Developer.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-importer/nss_decryptor_win.h')

    def test_ics_chromium_chrome_browser_metrics_system_metrics_proto(self):
        expected = [
            u'Copyright (c) 2009 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-metrics/system_metrics.proto')

    def test_ics_chromium_chrome_browser_renderer_host_render_widget_host_view_mac_mm(self):
        expected = [
            u'Copyright (c) 2011 The Chromium Authors.',
            u'Copyright (c) 2005, 2006, 2007, 2008, 2009 Apple Inc.',
            u'(c) 2006, 2007 Graham Dennis (graham.dennis@gmail.com)',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-renderer_host/render_widget_host_view_mac.mm')

    def test_ics_chromium_chrome_browser_resources_about_credits_html(self):
        expected = [
            u'Copyright (c) 1991, 2000, 2001 by Lucent Technologies.',
            u'Copyright (c) 2008-2009, Google Inc.',
            u'Copyright (c) 1998-2000 the Initial Developer.',
            u'Copyright (c) 1994-2000 the Initial Developer.',
            u'(c) Copyright IBM Corporation. 2006, 2006.',
            u'Copyright (c) 2006, Google Inc.',
            u'Copyright (c) 2000-2008 Julian Seward.',
            u'Copyright (c) 2007 Red Hat, inc',
            u'Copyright 2003-2005 Colin Percival',
            u'Copyright (c) 2000 the Initial Developer.',
            u'Copyright 1993 by OpenVision Technologies, Inc.',
            u'Copyright 2007 Google Inc.',
            u'Copyright (c) 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007 Alexander Kellett, Alexey Proskuryakov, Alex Mathews, Allan Sandfeld Jensen, Alp Toker, Anders Carlsson, Andrew Wellington, Antti',
            u'Copyright (c) 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
            u'Copyright (c) 1991, 1999 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
            u'Copyright (c) 2002-2010 The ANGLE Project',
            u'Copyright (c) 2009 Apple Inc.',
            u'Portions Copyright (c) 1999-2007 Apple Inc.',
            u'copyright (c) 1996-2010 Julian R Seward.',
            u'Copyright (c) 2010 The Chromium Authors.',
            u'Copyright (c) 1998-1999 Netscape Communications Corporation.',
            u'Copyright (c) 1998, 1999, 2000 Thai Open Source Software Center Ltd and Clark Cooper',
            u'Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006 Expat maintainers.',
            u'Copyright (c) 2008 The Khronos Group Inc.',
            u'Copyright (c) 1997, 1998, 1999, 2000, 2001, 2002 by Remco Treffkorn, and others',
            u'Copyright (c) 2005 by Eric S. Raymond.',
            u'Copyright (c) 2007, 2010 Linux Foundation',
            u'Copyright (c) 2006 IBM Corporation',
            u'Copyright (c) 2000, 2006 Sun Microsystems, Inc.',
            u'copyright (c) 1991-1998, Thomas G. Lane.',
            u'Copyright (c) 1995-2009 International Business Machines Corporation and others',
            u'(c) 1999 TaBE Project.',
            u'Copyright (c) 1999 Pai-Hsiang Hsiao.',
            u'Copyright (c) 1999 Computer Systems and Communication Lab, Institute of Information Science, Academia Sinica.',
            u'Copyright 1996 Chih-Hao Tsai Beckman Institute, University of Illinois',
            u'Copyright 2000, 2001, 2002, 2003 Nara Institute of Science and Technology.',
            u'Copyright (c) 2002 the Initial Developer.',
            u'Copyright (c) 2006-2008 Jason Evans',
            u'Copyright (c) International Business Machines Corp., 2002,2007',
            u'Copyright 2000-2007 Niels Provos',
            u'Copyright 2007-2009 Niels Provos and Nick Mathewson',
            u'Copyright (c) 2004 2005, Google Inc.',
            u'copyright (c) 1991-1998, Thomas G. Lane.',
            u'copyright by the Free Software Foundation',
            u'Copyright (c) 1998-2005 Julian Smart, Robert Roebling',
            u'Copyright (c) 2004, 2006-2009 Glenn Randers-Pehrson',
            u'Copyright (c) 2000-2002 Glenn Randers-Pehrson',
            u'Copyright (c) 1998, 1999 Glenn Randers-Pehrson',
            u'Copyright (c) 1996, 1997 Andreas Dilger',
            u'Copyright (c) 1995, 1996 Guy Eric Schalnat, Group 42, Inc.',
            u'Copyright (c) 2001-2006 Cisco Systems, Inc.',
            u'Copyright (c) 2010, Google Inc.',
            u'Copyright (c) 2010, Google Inc.',
            u'Copyright (c) 1998-2003 Daniel Veillard.',
            u'Copyright (c) 2001-2002 Daniel Veillard.',
            u'Copyright (c) 2001-2002 Thomas Broyer, Charlie Bozeman and Daniel Veillard.',
            u'Copyright (c) 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
            u'Copyright (c) 2005, 2006 Nick Galbreath',
            u'Copyright 2008 MolokoCacao',
            u'Copyright (c) 2004-2009 Sergey Lyubka',
            u'Portions Copyright (c) 2009 Gilbert Wellisch',
            u'Copyright (c) 2002 the Initial Developer.',
            u'Copyright (c) 1998 the Initial Developer.',
            u'Copyright (c) 2004-2009 by Mulle Kybernetik.',
            u'Copyright (c) 2008 The Khronos Group Inc.',
            u'Copyright (c) 1998-2008 The OpenSSL Project.',
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 2009 The Chromium Authors.',
            u'Copyright 2007 Google Inc.',
            u'Copyright (c) 2010 The Chromium Authors.',
            u'Copyright 2008, Google Inc.',
            u'Copyright (c) 2007 Giampaolo Rodola',
            u'Copyright 2009, Google Inc.',
            u'Copyright (c) 2009 Mozilla Corporation',
            u'Copyright (c) 1998-2007 Marti Maria',
            u'Copyright (c) 1994-1996 SunSoft, Inc.',
            u'Copyright 2009 Google Inc.',
            u'Copyright (c) 2006 Bob Ippolito',
            u'Copyright 2002-2008 Xiph.org Foundation',
            u'Copyright 2002-2008 Jean-Marc Valin',
            u'Copyright 2005-2007 Analog Devices Inc.',
            u'Copyright 2005-2008 Commonwealth Scientific and Industrial Research Organisation (CSIRO)',
            u'Copyright 1993, 2002, 2006 David Rowe',
            u'Copyright 2003 EpicGames',
            u'Copyright 1992-1994 Jutta Degener, Carsten Bormann',
            u'Copyright (c) 1995-1998 The University of Utah and the Regents of the University of California',
            u'Copyright (c) 1998-2005 University of Chicago.',
            u'Copyright (c) 2005-2006 Arizona Board of Regents (University of Arizona).',
            u'Copyright (c) Andrew Tridgell 2004-2005',
            u'Copyright (c) Stefan Metzmacher 2006',
            u'Copyright (c) 2005, Google Inc.',
            u'Copyright (c) 2007 Free Software Foundation, Inc.',
            u'Copyright (c) 1998-1999 Netscape Communications Corporation.',
            u'Copyright (c) 2001-2010 Peter Johnson and other Yasm developers.',
            u'Copyright (c) 1995-2010 Jean-loup Gailly and Mark Adler',
            u'Copyright (c) 1994-2006 Sun Microsystems Inc.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-resources/about_credits.html')

    def test_ics_chromium_chrome_browser_resources_gpu_internals_html(self):
        expected = [
            u'Copyright (c) 2010 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-resources/gpu_internals.html')

    def test_ics_chromium_chrome_browser_resources_keyboard_overlay_js(self):
        expected = [
            u'Copyright (c) 2011 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-resources/keyboard_overlay.js')

    def test_ics_chromium_chrome_browser_resources_file_manager_harness_html(self):
        expected = [
            u'Copyright (c) 2011 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-resources-file_manager/harness.html')

    def test_ics_chromium_chrome_browser_resources_file_manager_css_file_manager_css(self):
        expected = [
            u'Copyright (c) 2011 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-resources-file_manager-css/file_manager.css')

    def test_ics_chromium_chrome_browser_sync_engine_change_reorder_buffer_cc(self):
        expected = [
            u'Copyright (c) 2006-2009 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-sync-engine/change_reorder_buffer.cc')

    def test_ics_chromium_chrome_browser_sync_engine_clear_data_command_h(self):
        expected = [
            u'Copyright (c) 2006-2010 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-sync-engine/clear_data_command.h')

    def test_ics_chromium_chrome_browser_ui_cocoa_applescript_examples_advanced_tab_manipulation_applescript(self):
        expected = [
            u'Copyright (c) 2010 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-ui-cocoa-applescript-examples/advanced_tab_manipulation.applescript')

    def test_ics_chromium_chrome_browser_userfeedback_proto_annotations_proto(self):
        expected = [
            u'Copyright 2009 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-userfeedback-proto/annotations.proto')

    def test_ics_chromium_chrome_browser_userfeedback_proto_chrome_proto(self):
        expected = [
            u'Copyright 2010 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-chrome-browser-userfeedback-proto/chrome.proto')

    def test_ics_chromium_chrome_common_extensions_docs_examples_api_i18n_cld_background_html(self):
        expected = [
            u'Copyright (c) 2009 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-chrome-common-extensions-docs-examples-api-i18n-cld/background.html')

    def test_ics_chromium_chrome_common_extensions_docs_examples_api_notifications_background_html(self):
        expected = [
            u'Copyright 2010 the Chromium Authors',
        ]
        check_detection(expected, 'ics/chromium-chrome-common-extensions-docs-examples-api-notifications/background.html')

    def test_ics_chromium_chrome_common_extensions_docs_examples_apps_hello_java_hellolicenseservlet_java(self):
        expected = [
            u'Copyright 2010 the Chromium Authors',
        ]
        check_detection(expected, 'ics/chromium-chrome-common-extensions-docs-examples-apps-hello-java/HelloLicenseServlet.java')

    def test_ics_chromium_chrome_common_extensions_docs_examples_apps_hello_php_notice(self):
        expected = [
            u'Copyright 2009 Google Inc.',
            u'Copyright (c) 2010 John Resig',
            u'Copyright (c) 2007 Andy Smith',
            u'Copyright (c) 2010, Mewp',
        ]
        check_detection(expected, 'ics/chromium-chrome-common-extensions-docs-examples-apps-hello-php/NOTICE')

    def test_ics_chromium_chrome_common_extensions_docs_examples_apps_hello_php_popuplib_js(self):
        expected = [
            u'Copyright 2009 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-chrome-common-extensions-docs-examples-apps-hello-php/popuplib.js')

    def test_ics_chromium_chrome_common_extensions_docs_examples_apps_hello_php_lib_oauth_license_txt(self):
        expected = [
            u'Copyright (c) 2007 Andy Smith',
        ]
        check_detection(expected, 'ics/chromium-chrome-common-extensions-docs-examples-apps-hello-php-lib-oauth/LICENSE.txt')

    def test_ics_chromium_chrome_common_extensions_docs_examples_apps_hello_python_notice(self):
        expected = [
            u'Copyright (c) 2007 Leah Culver',
        ]
        check_detection(expected, 'ics/chromium-chrome-common-extensions-docs-examples-apps-hello-python/NOTICE')

    def test_ics_chromium_chrome_common_extensions_docs_examples_apps_hello_python_httplib2_init_py(self):
        expected = [
            u'Copyright 2006, Joe Gregorio contributors',
        ]
        check_detection(expected, 'ics/chromium-chrome-common-extensions-docs-examples-apps-hello-python-httplib2/__init__.py')

    @expectedFailure
    def test_ics_chromium_chrome_common_extensions_docs_examples_apps_hello_python_httplib2_init_py_extra_contributors(self):
        expected = [
            u'Copyright 2006, Joe Gregorio',
        ]
        check_detection(expected, 'ics/chromium-chrome-common-extensions-docs-examples-apps-hello-python-httplib2/__init__.py')

    def test_ics_chromium_chrome_common_extensions_docs_examples_apps_hello_python_oauth2_init_py(self):
        expected = [
            u'Copyright (c) 2007-2010 Leah Culver, Joe Stump, Mark Paschal, Vic Fryzel',
        ]
        check_detection(expected, 'ics/chromium-chrome-common-extensions-docs-examples-apps-hello-python-oauth2/__init__.py')

    def test_ics_chromium_chrome_common_extensions_docs_examples_extensions_benchmark_jquery_jquery_1_4_2_min_js(self):
        expected = [
            u'Copyright 2010, John Resig',
            u'Copyright 2010, The Dojo Foundation',
        ]
        check_detection(expected, 'ics/chromium-chrome-common-extensions-docs-examples-extensions-benchmark-jquery/jquery-1.4.2.min.js')

    def test_ics_chromium_chrome_common_extensions_docs_examples_extensions_benchmark_jst_jsevalcontext_js(self):
        expected = [
            u'Copyright 2006 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-chrome-common-extensions-docs-examples-extensions-benchmark-jst/jsevalcontext.js')

    def test_ics_chromium_chrome_common_extensions_docs_examples_extensions_benchmark_util_sorttable_js(self):
        expected = [
            u'Copyright 2006, Dean Edwards',
        ]
        check_detection(expected, 'ics/chromium-chrome-common-extensions-docs-examples-extensions-benchmark-util/sorttable.js')

    def test_ics_chromium_chrome_common_extensions_docs_examples_extensions_gdocs_chrome_ex_oauthsimple_js(self):
        expected = [
            u'copyright unitedHeroes.net',
            u'Copyright (c) 2009, unitedHeroes.net',
        ]
        check_detection(expected, 'ics/chromium-chrome-common-extensions-docs-examples-extensions-gdocs/chrome_ex_oauthsimple.js')

    def test_ics_chromium_chrome_common_extensions_docs_examples_extensions_imageinfo_notice(self):
        expected = [
            u'Copyright (c) 2008 Jacob Seidelin, jseidelin@nihilogic.dk, http://blog.nihilogic.dk',
        ]
        check_detection(expected, 'ics/chromium-chrome-common-extensions-docs-examples-extensions-imageinfo/NOTICE')

    def test_ics_chromium_chrome_common_extensions_docs_examples_extensions_imageinfo_imageinfo_binaryajax_js(self):
        expected = [
            u'Copyright (c) 2008 Jacob Seidelin, cupboy@gmail.com, http://blog.nihilogic.dk',
        ]
        check_detection(expected, 'ics/chromium-chrome-common-extensions-docs-examples-extensions-imageinfo-imageinfo/binaryajax.js')

    def test_ics_chromium_chrome_common_extensions_docs_examples_extensions_imageinfo_imageinfo_imageinfo_js(self):
        expected = [
            u'Copyright (c) 2008 Jacob Seidelin, jseidelin@nihilogic.dk, http://blog.nihilogic.dk',
        ]
        check_detection(expected, 'ics/chromium-chrome-common-extensions-docs-examples-extensions-imageinfo-imageinfo/imageinfo.js')

    def test_ics_chromium_chrome_common_extensions_docs_examples_extensions_oauth_contacts_notice(self):
        expected = [
            u'copyright unitedHeroes.net',
            u'Copyright (c) 2009, unitedHeroes.net',
            u'Copyright Paul Johnston 2000 - 2002.',
        ]
        check_detection(expected, 'ics/chromium-chrome-common-extensions-docs-examples-extensions-oauth_contacts/NOTICE')

    def test_ics_chromium_chrome_common_extensions_docs_examples_extensions_proxy_configuration_test_jsunittest_js(self):
        expected = [
            u'(c) 2008 Dr Nic Williams',
        ]
        check_detection(expected, 'ics/chromium-chrome-common-extensions-docs-examples-extensions-proxy_configuration-test/jsunittest.js')

    def test_ics_chromium_chrome_common_extensions_docs_examples_extensions_wave_background_html(self):
        expected = [
            u'Copyright 2010 Google',
        ]
        check_detection(expected, 'ics/chromium-chrome-common-extensions-docs-examples-extensions-wave/background.html')

    def test_ics_chromium_crypto_third_party_nss_blapi_h(self):
        expected = [
            u'Copyright (c) 1994-2000 the Initial Developer.',
        ]
        check_detection(expected, 'ics/chromium-crypto-third_party-nss/blapi.h')

    def test_ics_chromium_crypto_third_party_nss_sha256_h(self):
        expected = [
            u'Copyright (c) 2002 the Initial Developer.',
        ]
        check_detection(expected, 'ics/chromium-crypto-third_party-nss/sha256.h')

    def test_ics_chromium_googleurl_license_txt(self):
        expected = [
            u'Copyright 2007, Google Inc.',
            u'Copyright (c) 1998 the Initial Developer.',
        ]
        check_detection(expected, 'ics/chromium-googleurl/LICENSE.txt')

    def test_ics_chromium_googleurl_base_basictypes_h(self):
        expected = [
            u'Copyright 2001 - 2003 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-googleurl-base/basictypes.h')

    def test_ics_chromium_googleurl_base_logging_cc(self):
        expected = [
            u'Copyright 2007, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-googleurl-base/logging.cc')

    def test_ics_chromium_googleurl_base_logging_h(self):
        expected = [
            u'Copyright 2006 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-googleurl-base/logging.h')

    def test_ics_chromium_googleurl_base_scoped_ptr_h(self):
        expected = [
            u'(c) Copyright Greg Colvin and Beman Dawes 1998, 1999.',
            u'Copyright (c) 2001, 2002 Peter Dimov',
        ]
        check_detection(expected, 'ics/chromium-googleurl-base/scoped_ptr.h')

    def test_ics_chromium_googleurl_src_gurl_unittest_cc(self):
        expected = [
            u'Copyright 2007 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-googleurl-src/gurl_unittest.cc')

    def test_ics_chromium_googleurl_src_url_canon_ip_cc(self):
        expected = [
            u'Copyright 2009, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-googleurl-src/url_canon_ip.cc')

    def test_ics_chromium_googleurl_src_url_common_h(self):
        expected = [
            u'Copyright 2010, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-googleurl-src/url_common.h')

    def test_ics_chromium_googleurl_src_url_parse_cc(self):
        expected = [
            u'Copyright (c) 1998 the Initial Developer.',
        ]
        check_detection(expected, 'ics/chromium-googleurl-src/url_parse.cc')

    def test_ics_chromium_googleurl_src_url_test_utils_h(self):
        expected = [
            u'Copyright 2007 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-googleurl-src/url_test_utils.h')

    def test_ics_chromium_net_base_cookie_monster_cc(self):
        expected = [
            u'Copyright (c) 2011 The Chromium Authors.',
            u'Copyright (c) 2003 the Initial Developer.',
        ]
        check_detection(expected, 'ics/chromium-net-base/cookie_monster.cc')

    def test_ics_chromium_net_base_effective_tld_names_dat(self):
        expected = [
            u'Copyright (c) 2007 the Initial Developer.',
        ]
        check_detection(expected, 'ics/chromium-net-base/effective_tld_names.dat')

    def test_ics_chromium_net_base_ssl_false_start_blacklist_process_cc(self):
        expected = [
            u'Copyright (c) 2010 The Chromium Authors.',
            u'Copyright (c) 2010 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-net-base/ssl_false_start_blacklist_process.cc')

    def test_ics_chromium_net_base_x509_cert_types_mac_unittest_cc(self):
        expected = [
            u'Copyright (c) 2010 The Chromium Authors.',
            u'(c) Kasm 2005',
            u'(c) 1999 Entrust.net Limited',
            u'(c) Kasm 2005',
            u"(c) 1999 Entrust.net Limited",
        ]
        check_detection(expected, 'ics/chromium-net-base/x509_cert_types_mac_unittest.cc')

    def test_ics_chromium_net_base_x509_certificate_unittest_cc(self):
        expected = [
            u'Copyright (c) 2011 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-net-base/x509_certificate_unittest.cc')

    def test_ics_chromium_net_data_proxy_resolver_perftest_no_ads_pac_trail_name(self):
        expected = [
            u'Copyright 1996-2004, John LoVerso.',
        ]
        check_detection(expected, 'ics/chromium-net-data-proxy_resolver_perftest/no-ads.pac')

    def test_ics_chromium_net_disk_cache_sparse_control_cc(self):
        expected = [
            u'Copyright (c) 2009-2010 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-net-disk_cache/sparse_control.cc')

    def test_ics_chromium_net_ftp_ftp_network_layer_cc(self):
        expected = [
            u'Copyright (c) 2008 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-net-ftp/ftp_network_layer.cc')

    def test_ics_chromium_net_http_des_cc(self):
        expected = [
            u'Copyright (c) 2011 The Chromium Authors.',
            u'Copyright (c) 2003 IBM Corporation.',
        ]
        check_detection(expected, 'ics/chromium-net-http/des.cc')

    def test_ics_chromium_net_http_http_auth_handler_ntlm_portable_cc(self):
        expected = [
            u'Copyright (c) 2010 The Chromium Authors.',
            u'Copyright (c) 2003 IBM Corporation.',
        ]
        check_detection(expected, 'ics/chromium-net-http/http_auth_handler_ntlm_portable.cc')

    def test_ics_chromium_net_http_http_chunked_decoder_cc(self):
        expected = [
            u'Copyright (c) 2010 The Chromium Authors.',
            u'Copyright (c) 2001 the Initial Developer.',
        ]
        check_detection(expected, 'ics/chromium-net-http/http_chunked_decoder.cc')

    def test_ics_chromium_net_http_md4_cc(self):
        expected = [
            u'Copyright (c) 2003 IBM Corporation.',
        ]
        check_detection(expected, 'ics/chromium-net-http/md4.cc')

    def test_ics_chromium_net_socket_ssl_client_socket_nss_cc(self):
        expected = [
            u'Copyright (c) 2011 The Chromium Authors.',
            u'Copyright (c) 2000 the Initial Developer.',
        ]
        check_detection(expected, 'ics/chromium-net-socket/ssl_client_socket_nss.cc')

    def test_ics_chromium_net_third_party_gssapi_gssapi_h(self):
        expected = [
            u'Copyright 1993 by OpenVision Technologies, Inc.',
        ]
        check_detection(expected, 'ics/chromium-net-third_party-gssapi/gssapi.h')

    def test_ics_chromium_net_third_party_gssapi_license(self):
        expected = [
            u'Copyright 1993 by OpenVision Technologies, Inc.',
        ]
        check_detection(expected, 'ics/chromium-net-third_party-gssapi/LICENSE')

    def test_ics_chromium_net_tools_spdyshark_makefile_am(self):
        expected = [
            u'Copyright 1998 Gerald Combs',
        ]
        check_detection(expected, 'ics/chromium-net-tools-spdyshark/Makefile.am')

    def test_ics_chromium_net_tools_spdyshark_packet_spdy_c(self):
        expected = [
            u'Copyright 2010, Google Inc. Eric Shienbrood <ers@google.com>',
            u'Copyright 1998 Gerald Combs',
        ]
        check_detection(expected, 'ics/chromium-net-tools-spdyshark/packet-spdy.c')

    def test_ics_chromium_net_tools_spdyshark_plugin_rc_in(self):
        expected = [
            u'Copyright (c) 1998 Gerald Combs <gerald@wireshark.org> , Gilbert Ramirez <gram@alumni.rice.edu> and others',
        ]
        check_detection(expected, 'ics/chromium-net-tools-spdyshark/plugin.rc.in')

    def test_ics_chromium_net_tools_testserver_chromiumsync_py(self):
        expected = [
            u'Copyright (c) 2010 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-net-tools-testserver/chromiumsync.py')

    def test_ics_chromium_net_tools_tld_cleanup_tld_cleanup_cc(self):
        expected = [
            u'Copyright (c) 2006-2008 The Chromium Authors.',
            u'Copyright (c) 2009 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-net-tools-tld_cleanup/tld_cleanup.cc')

    def test_ics_chromium_sdch_open_vcdiff_aclocal_m4(self):
        expected = [
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008 Free Software Foundation, Inc.',
            u'Copyright (c) 2002, 2003, 2005, 2006, 2007 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1997, 2000, 2001, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 2000, 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2008 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2002, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1997, 1999, 2000, 2001, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2002, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 2000, 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff/aclocal.m4')

    def test_ics_chromium_sdch_open_vcdiff_compile(self):
        expected = [
            u'Copyright 1999, 2000 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff/compile')

    def test_ics_chromium_sdch_open_vcdiff_configure(self):
        expected = [
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008 Free Software Foundation, Inc.',
            u'Copyright (c) 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff/configure')

    def test_ics_chromium_sdch_open_vcdiff_copying(self):
        expected = [
            u'Copyright (c) 2008, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff/COPYING')

    def test_ics_chromium_sdch_open_vcdiff_depcomp(self):
        expected = [
            u'Copyright (c) 1999, 2000, 2003, 2004, 2005, 2006, 2007 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff/depcomp')

    def test_ics_chromium_sdch_open_vcdiff_install(self):
        expected = [
            u'Copyright (c) 1994, 1995, 1996, 1999, 2000, 2001, 2002, 2004, 2005, 2006, 2007 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff/INSTALL')

    def test_ics_chromium_sdch_open_vcdiff_ltmain_sh(self):
        expected = [
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2003, 2004, 2005, 2006, 2007, 2008 Free Software Foundation, Inc.',
            u'Copyright (c) 2008 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff/ltmain.sh')

    def test_ics_chromium_sdch_open_vcdiff_missing(self):
        expected = [
            u'Copyright (c) 1996, 1997, 1999, 2000, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff/missing')

    def test_ics_chromium_sdch_open_vcdiff_man_vcdiff_1(self):
        expected = [
            u'Copyright (c) 2008, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff-man/vcdiff.1')

    def test_ics_chromium_sdch_open_vcdiff_src_addrcache_cc(self):
        expected = [
            u'Copyright 2007 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff-src/addrcache.cc')

    def test_ics_chromium_sdch_open_vcdiff_src_adler32_c(self):
        expected = [
            u'Copyright (c) 1995-2004 Mark Adler',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff-src/adler32.c')

    def test_ics_chromium_sdch_open_vcdiff_src_blockhash_cc(self):
        expected = [
            u'Copyright 2006, 2008 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff-src/blockhash.cc')

    def test_ics_chromium_sdch_open_vcdiff_src_blockhash_test_cc(self):
        expected = [
            u'Copyright 2008 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff-src/blockhash_test.cc')

    def test_ics_chromium_sdch_open_vcdiff_src_codetablewriter_interface_h(self):
        expected = [
            u'Copyright 2008 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff-src/codetablewriter_interface.h')

    def test_ics_chromium_sdch_open_vcdiff_src_gflags_cc(self):
        expected = [
            u'Copyright (c) 2006, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff-src/gflags.cc')

    def test_ics_chromium_sdch_open_vcdiff_src_mutex_h(self):
        expected = [
            u'Copyright (c) 2007, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff-src/mutex.h')

    def test_ics_chromium_sdch_open_vcdiff_src_rolling_hash_h(self):
        expected = [
            u'Copyright 2007, 2008 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff-src/rolling_hash.h')

    def test_ics_chromium_sdch_open_vcdiff_src_vcdiff_test_sh(self):
        expected = [
            u'Copyright 2008 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff-src/vcdiff_test.sh')

    def test_ics_chromium_sdch_open_vcdiff_src_zconf_h(self):
        expected = [
            u'Copyright (c) 1995-2005 Jean-loup Gailly.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff-src/zconf.h')

    def test_ics_chromium_sdch_open_vcdiff_src_zlib_h(self):
        expected = [
            u'Copyright (c) 1995-2005 Jean-loup Gailly and Mark Adler',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff-src/zlib.h')

    def test_ics_chromium_sdch_open_vcdiff_src_google_output_string_h(self):
        expected = [
            u'Copyright 2008 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff-src-google/output_string.h')

    def test_ics_chromium_sdch_open_vcdiff_src_gtest_gtest_cc(self):
        expected = [
            u'Copyright 2005, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff-src-gtest/gtest.cc')

    def test_ics_chromium_sdch_open_vcdiff_src_gtest_gtest_main_cc(self):
        expected = [
            u'Copyright 2006, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff-src-gtest/gtest_main.cc')

    def test_ics_chromium_sdch_open_vcdiff_vsprojects_vcdiff_test_bat(self):
        expected = [
            u'Copyright 2008 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-sdch-open-vcdiff-vsprojects/vcdiff_test.bat')

    def test_ics_chromium_testing_generate_gmock_mutant_py(self):
        expected = [
            u'Copyright (c) 2009 The Chromium Authors.',
            u'Copyright (c) 2009 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/chromium-testing/generate_gmock_mutant.py')

    def test_ics_chromium_testing_gmock_copying(self):
        expected = [
            u'Copyright 2008, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-testing-gmock/COPYING')

    def test_ics_chromium_testing_gmock_include_gmock_gmock_cardinalities_h(self):
        expected = [
            u'Copyright 2007, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-testing-gmock-include-gmock/gmock-cardinalities.h')

    def test_ics_chromium_testing_gmock_scripts_fuse_gmock_files_py(self):
        expected = [
            u'Copyright 2009, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-testing-gmock-scripts/fuse_gmock_files.py')

    def test_ics_chromium_testing_gmock_scripts_gmock_doctor_py(self):
        expected = [
            u'Copyright 2008, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-testing-gmock-scripts/gmock_doctor.py')

    def test_ics_chromium_testing_gmock_scripts_upload_py(self):
        expected = [
            u'Copyright 2007 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-testing-gmock-scripts/upload.py')

    def test_ics_chromium_testing_gmock_scripts_generator_gmock_gen_py(self):
        expected = [
            u'Copyright 2008 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-testing-gmock-scripts-generator/gmock_gen.py')

    def test_ics_chromium_testing_gmock_scripts_generator_cpp_ast_py(self):
        expected = [
            u'Copyright 2007 Neal Norwitz',
            u'Portions Copyright 2007 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-testing-gmock-scripts-generator-cpp/ast.py')

    def test_ics_chromium_testing_gmock_scripts_generator_cpp_gmock_class_test_py(self):
        expected = [
            u'Copyright 2009 Neal Norwitz',
            u'Portions Copyright 2009 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-testing-gmock-scripts-generator-cpp/gmock_class_test.py')

    def test_ics_chromium_testing_gmock_test_gmock_test_utils_py(self):
        expected = [
            u'Copyright 2006, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-testing-gmock-test/gmock_test_utils.py')

    def test_ics_chromium_testing_gtest_include_gtest_internal_gtest_linked_ptr_h(self):
        expected = [
            u'Copyright 2003 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-testing-gtest-include-gtest-internal/gtest-linked_ptr.h')

    def test_ics_chromium_testing_gtest_include_gtest_internal_gtest_tuple_h(self):
        expected = [
            u'Copyright 2009 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-testing-gtest-include-gtest-internal/gtest-tuple.h')

    def test_ics_chromium_testing_gtest_samples_sample10_unittest_cc(self):
        expected = [
            u'Copyright 2009 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-testing-gtest-samples/sample10_unittest.cc')

    def test_ics_chromium_testing_gtest_scripts_gen_gtest_pred_impl_py(self):
        expected = [
            u'Copyright 2006, Google Inc.',
            u'Copyright 2006, Google Inc.',
            u'Copyright 2006, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-testing-gtest-scripts/gen_gtest_pred_impl.py')

    def test_ics_chromium_testing_gtest_src_gtest_port_cc(self):
        expected = [
            u'Copyright 2008, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-testing-gtest-src/gtest-port.cc')

    def test_ics_chromium_testing_gtest_test_gtest_catch_exceptions_test_py(self):
        expected = [
            u'Copyright 2010 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-testing-gtest-test/gtest_catch_exceptions_test.py')

    def test_ics_chromium_testing_gtest_test_gtest_filter_unittest_py(self):
        expected = [
            u'Copyright 2005 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-testing-gtest-test/gtest_filter_unittest.py')

    def test_ics_chromium_testing_gtest_test_gtest_shuffle_test_py(self):
        expected = [
            u'Copyright 2009 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-testing-gtest-test/gtest_shuffle_test.py')

    def test_ics_chromium_testing_gtest_test_gtest_linked_ptr_test_cc(self):
        expected = [
            u'Copyright 2003, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-testing-gtest-test/gtest-linked_ptr_test.cc')

    def test_ics_chromium_third_party_libevent_buffer_c(self):
        expected = [
            u'Copyright (c) 2002, 2003 Niels Provos <provos@citi.umich.edu>',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/buffer.c')

    def test_ics_chromium_third_party_libevent_config_guess(self):
        expected = [
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008 Free Software Foundation, Inc.',
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/config.guess')

    def test_ics_chromium_third_party_libevent_configure(self):
        expected = [
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008 Free Software Foundation, Inc.',
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008 Free Software Foundation, Inc.',
            u'Copyright (c) 2008 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/configure')

    def test_ics_chromium_third_party_libevent_devpoll_c(self):
        expected = [
            u'Copyright 2000-2004 Niels Provos <provos@citi.umich.edu>',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/devpoll.c')

    def test_ics_chromium_third_party_libevent_epoll_c(self):
        expected = [
            u'Copyright 2000-2003 Niels Provos <provos@citi.umich.edu>',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/epoll.c')

    def test_ics_chromium_third_party_libevent_epoll_sub_c(self):
        expected = [
            u'Copyright 2003 Niels Provos <provos@citi.umich.edu>',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/epoll_sub.c')

    def test_ics_chromium_third_party_libevent_evbuffer_c(self):
        expected = [
            u'Copyright (c) 2002-2004 Niels Provos <provos@citi.umich.edu>',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/evbuffer.c')

    def test_ics_chromium_third_party_libevent_evdns_3(self):
        expected = [
            u'Copyright (c) 2006 Niels Provos <provos@citi.umich.edu>',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/evdns.3')

    def test_ics_chromium_third_party_libevent_evdns_h(self):
        expected = [
            u'Copyright (c) 2006 Niels Provos <provos@citi.umich.edu>',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/evdns.h')

    def test_ics_chromium_third_party_libevent_event_3(self):
        expected = [
            u'Copyright (c) 2000 Artur Grabowski <art@openbsd.org>',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/event.3')

    def test_ics_chromium_third_party_libevent_event_h(self):
        expected = [
            u'Copyright (c) 2000-2007 Niels Provos <provos@citi.umich.edu>',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/event.h')

    def test_ics_chromium_third_party_libevent_event_rpcgen_py(self):
        expected = [
            u'Copyright (c) 2005 Niels Provos <provos@citi.umich.edu>',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/event_rpcgen.py')

    def test_ics_chromium_third_party_libevent_event_tagging_c(self):
        expected = [
            u'Copyright (c) 2003, 2004 Niels Provos <provos@citi.umich.edu>',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/event_tagging.c')

    def test_ics_chromium_third_party_libevent_event_internal_h(self):
        expected = [
            u'Copyright (c) 2000-2004 Niels Provos <provos@citi.umich.edu>',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/event-internal.h')

    def test_ics_chromium_third_party_libevent_evport_c(self):
        expected = [
            u'Copyright (c) 2007 Sun Microsystems.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/evport.c')

    def test_ics_chromium_third_party_libevent_evsignal_h(self):
        expected = [
            u'Copyright 2000-2002 Niels Provos <provos@citi.umich.edu>',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/evsignal.h')

    def test_ics_chromium_third_party_libevent_evutil_c(self):
        expected = [
            u'Copyright (c) 2007 Niels Provos <provos@citi.umich.edu>',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/evutil.c')

    def test_ics_chromium_third_party_libevent_http_c(self):
        expected = [
            u'Copyright (c) 2002-2006 Niels Provos <provos@citi.umich.edu>',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/http.c')

    def test_ics_chromium_third_party_libevent_http_internal_h(self):
        expected = [
            u'Copyright 2001 Niels Provos <provos@citi.umich.edu>',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/http-internal.h')

    def test_ics_chromium_third_party_libevent_license(self):
        expected = [
            u'Copyright 2000-2007 Niels Provos <provos@citi.umich.edu>',
            u'Copyright 2007-2009 Niels Provos and Nick Mathewson',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/LICENSE')

    def test_ics_chromium_third_party_libevent_log_c(self):
        expected = [
            u'Copyright (c) 2005 Nick Mathewson <nickm@freehaven.net>',
            u'Copyright (c) 2000 Dug Song <dugsong@monkey.org>',
            u'Copyright (c) 1993 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/log.c')

    def test_ics_chromium_third_party_libevent_min_heap_h(self):
        expected = [
            u'Copyright (c) 2006 Maxim Yegorushkin <maxim.yegorushkin@gmail.com>',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/min_heap.h')

    def test_ics_chromium_third_party_libevent_missing(self):
        expected = [
            u'Copyright (c) 1996, 1997, 1999, 2000, 2002, 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/missing')

    def test_ics_chromium_third_party_libevent_strlcpy_c(self):
        expected = [
            u'Copyright (c) 1998 Todd C. Miller <Todd.Miller@courtesan.com>',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent/strlcpy.c')

    def test_ics_chromium_third_party_libevent_compat_sys_libevent_time_h(self):
        expected = [
            u'Copyright (c) 1982, 1986, 1993 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent-compat-sys/_libevent_time.h')

    def test_ics_chromium_third_party_libevent_compat_sys_queue_h(self):
        expected = [
            u'Copyright (c) 1991, 1993 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent-compat-sys/queue.h')

    def test_ics_chromium_third_party_libevent_test_regress_dns_c(self):
        expected = [
            u'Copyright (c) 2003-2006 Niels Provos <provos@citi.umich.edu>',
        ]
        check_detection(expected, 'ics/chromium-third_party-libevent-test/regress_dns.c')

    def test_ics_chromium_third_party_libjingle_overrides_talk_base_logging_h(self):
        expected = [
            u'Copyright 2004 2005, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-overrides-talk-base/logging.h')

    def test_ics_chromium_third_party_libjingle_source_copying(self):
        expected = [
            u'Copyright (c) 2004 2005, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source/COPYING')

    def test_ics_chromium_third_party_libjingle_source_talk_base_asyncfile_cc(self):
        expected = [
            u'Copyright 2010, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source-talk-base/asyncfile.cc')

    def test_ics_chromium_third_party_libjingle_source_talk_base_asyncfile_h(self):
        expected = [
            u'Copyright 2004 2010, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source-talk-base/asyncfile.h')

    def test_ics_chromium_third_party_libjingle_source_talk_base_base64_cc(self):
        expected = [
            u'Copyright (c) 1999, Bob Withers',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source-talk-base/base64.cc')

    def test_ics_chromium_third_party_libjingle_source_talk_base_base64_h(self):
        expected = [
            u'Copyright (c) 1999, Bob Withers',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source-talk-base/base64.h')

    def test_ics_chromium_third_party_libjingle_source_talk_base_basicpacketsocketfactory_cc(self):
        expected = [
            u'Copyright 2011, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source-talk-base/basicpacketsocketfactory.cc')

    def test_ics_chromium_third_party_libjingle_source_talk_base_buffer_h(self):
        expected = [
            u'Copyright 2004-2010, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source-talk-base/buffer.h')

    def test_ics_chromium_third_party_libjingle_source_talk_base_event_cc(self):
        expected = [
            u'Copyright 2004 2008, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source-talk-base/event.cc')

    def test_ics_chromium_third_party_libjingle_source_talk_base_fileutils_cc(self):
        expected = [
            u'Copyright 2004 2006, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source-talk-base/fileutils.cc')

    def test_ics_chromium_third_party_libjingle_source_talk_base_httpbase_cc(self):
        expected = [
            u'Copyright 2004 2005, Google Inc.',
            u'Copyright 2005 Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source-talk-base/httpbase.cc')

    def test_ics_chromium_third_party_libjingle_source_talk_base_macconversion_cc(self):
        expected = [
            u'Copyright 2004 2009, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source-talk-base/macconversion.cc')

    def test_ics_chromium_third_party_libjingle_source_talk_base_macutils_cc(self):
        expected = [
            u'Copyright 2007 2009, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source-talk-base/macutils.cc')

    def test_ics_chromium_third_party_libjingle_source_talk_base_socketstream_h(self):
        expected = [
            u'Copyright 2005 2010, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source-talk-base/socketstream.h')

    def test_ics_chromium_third_party_libjingle_source_talk_base_stringutils_cc(self):
        expected = [
            u'Copyright 2004 2005, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source-talk-base/stringutils.cc')

    def test_ics_chromium_third_party_libjingle_source_talk_session_phone_call_cc(self):
        expected = [
            u'Copyright 2004 2007, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source-talk-session-phone/call.cc')

    def test_ics_chromium_third_party_libjingle_source_talk_session_phone_codec_h(self):
        expected = [
            u'Copyright 2004 2007, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source-talk-session-phone/codec.h')

    def test_ics_chromium_third_party_libjingle_source_talk_session_phone_mediamonitor_cc(self):
        expected = [
            u'Copyright 2005 2007, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source-talk-session-phone/mediamonitor.cc')

    def test_ics_chromium_third_party_libjingle_source_talk_session_phone_mediamonitor_h(self):
        expected = [
            u'Copyright 2005 2008, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source-talk-session-phone/mediamonitor.h')

    def test_ics_chromium_third_party_libjingle_source_talk_session_phone_srtpfilter_h(self):
        expected = [
            u'Copyright 2009, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source-talk-session-phone/srtpfilter.h')

    def test_ics_chromium_third_party_libjingle_source_talk_session_phone_v4llookup_cc(self):
        expected = [
            u'Copyright 2009, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source-talk-session-phone/v4llookup.cc')

    def test_ics_chromium_third_party_libjingle_source_talk_session_phone_videocommon_h(self):
        expected = [
            u'Copyright 2011, Google Inc.',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source-talk-session-phone/videocommon.h')

    def test_ics_chromium_third_party_libjingle_source_talk_third_party_libudev_libudev_h(self):
        expected = [
            u'Copyright (c) 2008-2010 Kay Sievers <kay.sievers@vrfy.org>',
        ]
        check_detection(expected, 'ics/chromium-third_party-libjingle-source-talk-third_party-libudev/libudev.h')

    def test_ics_chromium_third_party_modp_b64_license(self):
        expected = [
            u'Copyright (c) 2005, 2006 Nick Galbreath',
        ]
        check_detection(expected, 'ics/chromium-third_party-modp_b64/LICENSE')

    def test_ics_chromium_third_party_modp_b64_modp_b64_cc(self):
        expected = [
            u'Copyright (c) 2005, 2006 Nick Galbreath',
        ]
        check_detection(expected, 'ics/chromium-third_party-modp_b64/modp_b64.cc')

    def test_ics_chromium_third_party_modp_b64_modp_b64_h(self):
        expected = [
            u'Copyright (c) 2005, 2006, Nick Galbreath',
        ]
        check_detection(expected, 'ics/chromium-third_party-modp_b64/modp_b64.h')

    def test_ics_chromium_webkit_glue_inspector_strings_grd(self):
        expected = [
            u'Copyright (c) 2007, 2008 Apple Inc.',
        ]
        check_detection(expected, 'ics/chromium-webkit-glue/inspector_strings.grd')

    def test_ics_chromium_webkit_glue_multipart_response_delegate_h(self):
        expected = [
            u'Copyright (c) 2006-2009 The Chromium Authors.',
            u'Copyright (c) 1998 the Initial Developer.',
        ]
        check_detection(expected, 'ics/chromium-webkit-glue/multipart_response_delegate.h')

    def test_ics_chromium_webkit_glue_webcursor_gtk_data_h(self):
        expected = [
            u'Copyright (c) 2001 Tim Copperfield <timecop@network.email.ne.jp>',
            u'Copyright (c) 2007 Christian Dywan <christian@twotoasts.de>',
        ]
        check_detection(expected, 'ics/chromium-webkit-glue/webcursor_gtk_data.h')

    def test_ics_chromium_webkit_glue_webkit_strings_grd(self):
        expected = [
            u'Copyright (c) 2007 Apple Inc.',
            u'Copyright (c) 2001 the Initial Developer.',
        ]
        check_detection(expected, 'ics/chromium-webkit-glue/webkit_strings.grd')

    def test_ics_chromium_webkit_glue_resources_readme_txt(self):
        expected = [
            u'Copyright (c) 1998 the Initial Developer.',
            u'Copyright (c) 2005 Apple Computer, Inc.',
        ]
        check_detection(expected, 'ics/chromium-webkit-glue-resources/README.txt')

    def test_ics_clang_notice_trail_place(self):
        expected = [
            u'Copyright (c) 2007-2011 University of Illinois at Urbana-Champaign.',
        ]
        check_detection(expected, 'ics/clang/NOTICE')

    def test_ics_clang_docs_block_abi_apple_txt(self):
        expected = [
            u'Copyright 2008-2010 Apple, Inc.',
        ]
        check_detection(expected, 'ics/clang-docs/Block-ABI-Apple.txt')

    def test_ics_clang_docs_blocklanguagespec_txt(self):
        expected = [
            u'Copyright 2008-2009 Apple, Inc.',
        ]
        check_detection(expected, 'ics/clang-docs/BlockLanguageSpec.txt')

    def test_ics_clang_include_clang_basic_convertutf_h(self):
        expected = [
            u'Copyright 2001-2004 Unicode, Inc.',
        ]
        check_detection(expected, 'ics/clang-include-clang-Basic/ConvertUTF.h')

    def test_ics_clang_lib_headers_iso646_h(self):
        expected = [
            u'Copyright (c) 2008 Eli Friedman',
        ]
        check_detection(expected, 'ics/clang-lib-Headers/iso646.h')

    def test_ics_clang_lib_headers_limits_h(self):
        expected = [
            u'Copyright (c) 2009 Chris Lattner',
        ]
        check_detection(expected, 'ics/clang-lib-Headers/limits.h')

    def test_ics_clang_lib_headers_tgmath_h(self):
        expected = [
            u'Copyright (c) 2009 Howard Hinnant',
        ]
        check_detection(expected, 'ics/clang-lib-Headers/tgmath.h')

    def test_ics_collada_license_txt(self):
        expected = [
            u'Copyright 2006 Sony Computer Entertainment Inc.',
        ]
        check_detection(expected, 'ics/collada/license.txt')

    def test_ics_collada_include_dae_h(self):
        expected = [
            u'Copyright 2006 Sony Computer Entertainment Inc.',
        ]
        check_detection(expected, 'ics/collada-include/dae.h')

    def test_ics_collada_include_dae_daezaeuncompresshandler_h(self):
        expected = [
            u'Copyright 2008 Netallied Systems GmbH.',
        ]
        check_detection(expected, 'ics/collada-include-dae/daeZAEUncompressHandler.h')

    def test_ics_collada_src_1_4_dom_domasset_cpp(self):
        expected = [
            u'Copyright 2006 Sony Computer Entertainment Inc.',
        ]
        check_detection(expected, 'ics/collada-src-1.4-dom/domAsset.cpp')

    def test_ics_dbus_acinclude_m4(self):
        expected = [
            u'Copyright (c) 2004 Scott James Remnant <scott@netsplit.com>',
            u'(c) 2003, 2004, 2005 Thomas Vander Stichele',
        ]
        check_detection(expected, 'ics/dbus/acinclude.m4')

    def test_ics_dbus_configure_in(self):
        expected = [
            u'Copyright (c) 2000-2002, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/dbus/configure.in')

    def test_ics_dbus_copying(self):
        expected = [
            u'Copyright (c) 2003-2004 Lawrence E. Rosen.',
            u'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, 'ics/dbus/COPYING')

    def test_ics_dbus_bus_activation_c(self):
        expected = [
            u'Copyright (c) 2003 CodeFactory AB',
            u'Copyright (c) 2003 Red Hat, Inc.',
            u'Copyright (c) 2004 Imendio HB',
        ]
        check_detection(expected, 'ics/dbus-bus/activation.c')

    def test_ics_dbus_bus_activation_h(self):
        expected = [
            u'Copyright (c) 2003 CodeFactory AB',
        ]
        check_detection(expected, 'ics/dbus-bus/activation.h')

    def test_ics_dbus_bus_activation_exit_codes_h(self):
        expected = [
            u'Copyright (c) 2007 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-bus/activation-exit-codes.h')

    def test_ics_dbus_bus_bus_c(self):
        expected = [
            u'Copyright (c) 2003, 2004 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-bus/bus.c')

    def test_ics_dbus_bus_config_parser_trivial_c(self):
        expected = [
            u'Copyright (c) 2003, 2004, 2007 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-bus/config-parser-trivial.c')

    def test_ics_dbus_bus_connection_c(self):
        expected = [
            u'Copyright (c) 2003 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-bus/connection.c')

    def test_ics_dbus_bus_connection_h(self):
        expected = [
            u'Copyright (c) 2003, 2004 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-bus/connection.h')

    def test_ics_dbus_bus_dbus_daemon_1_in(self):
        expected = [
            u'Copyright (c) 2003,2008 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-bus/dbus-daemon.1.in')

    def test_ics_dbus_bus_desktop_file_c(self):
        expected = [
            u'Copyright (c) 2003 CodeFactory AB',
            u'Copyright (c) 2003 Red Hat Inc.',
        ]
        check_detection(expected, 'ics/dbus-bus/desktop-file.c')

    def test_ics_dbus_bus_dir_watch_inotify_c(self):
        expected = [
            u'Copyright (c) 2003 Red Hat, Inc.',
            u'(c) 2006 Mandriva',
        ]
        check_detection(expected, 'ics/dbus-bus/dir-watch-inotify.c')

    def test_ics_dbus_bus_dispatch_c(self):
        expected = [
            u'Copyright (c) 2003 CodeFactory AB',
            u'Copyright (c) 2003, 2004, 2005 Red Hat, Inc.',
            u'Copyright (c) 2004 Imendio HB',
        ]
        check_detection(expected, 'ics/dbus-bus/dispatch.c')

    def test_ics_dbus_bus_driver_c(self):
        expected = [
            u'Copyright (c) 2003 CodeFactory AB',
            u'Copyright (c) 2003, 2004, 2005 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-bus/driver.c')

    def test_ics_dbus_bus_main_c(self):
        expected = [
            u'Copyright (c) 2003 Red Hat, Inc.',
            u'Copyright (c) 2002, 2003 Red Hat, Inc., CodeFactory AB, and others',
        ]
        check_detection(expected, 'ics/dbus-bus/main.c')

    def test_ics_dbus_bus_messagebus_config_in(self):
        expected = [
            u'Copyright 2009 Yaakov Selkowitz',
        ]
        check_detection(expected, 'ics/dbus-bus/messagebus-config.in')

    def test_ics_dbus_bus_services_c(self):
        expected = [
            u'Copyright (c) 2003 Red Hat, Inc.',
            u'Copyright (c) 2003 CodeFactory AB',
        ]
        check_detection(expected, 'ics/dbus-bus/services.c')

    def test_ics_dbus_bus_signals_c(self):
        expected = [
            u'Copyright (c) 2003, 2005 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-bus/signals.c')

    def test_ics_dbus_bus_utils_c(self):
        expected = [
            u'Copyright (c) 2003 CodeFactory AB',
            u'Copyright (c) 2003 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-bus/utils.c')

    def test_ics_dbus_cmake_bus_dbus_daemon_xml(self):
        expected = [
            u'Copyright (c) 2003 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-cmake-bus/dbus-daemon.xml')

    def test_ics_dbus_cmake_modules_win32macros_cmake(self):
        expected = [
            u'Copyright (c) 2006-2007, Ralf Habacker',
        ]
        check_detection(expected, 'ics/dbus-cmake-modules/Win32Macros.cmake')

    def test_ics_dbus_dbus_dbus_address_c(self):
        expected = [
            u'Copyright (c) 2003 CodeFactory AB',
            u'Copyright (c) 2004,2005 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-address.c')

    def test_ics_dbus_dbus_dbus_auth_h(self):
        expected = [
            u'Copyright (c) 2002 Red Hat Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-auth.h')

    def test_ics_dbus_dbus_dbus_auth_util_c(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004 Red Hat Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-auth-util.c')

    def test_ics_dbus_dbus_dbus_connection_c(self):
        expected = [
            u'Copyright (c) 2002-2006 Red Hat Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-connection.c')

    def test_ics_dbus_dbus_dbus_connection_h(self):
        expected = [
            u'Copyright (c) 2002, 2003 Red Hat Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-connection.h')

    def test_ics_dbus_dbus_dbus_credentials_util_c(self):
        expected = [
            u'Copyright (c) 2007 Red Hat Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-credentials-util.c')

    def test_ics_dbus_dbus_dbus_errors_c(self):
        expected = [
            u'Copyright (c) 2002, 2004 Red Hat Inc.',
            u'Copyright (c) 2003 CodeFactory AB',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-errors.c')

    def test_ics_dbus_dbus_dbus_errors_h(self):
        expected = [
            u'Copyright (c) 2002 Red Hat Inc.',
            u'Copyright (c) 2003 CodeFactory AB',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-errors.h')

    def test_ics_dbus_dbus_dbus_file_h(self):
        expected = [
            u'Copyright (c) 2002, 2003 Red Hat, Inc.',
            u'Copyright (c) 2003 CodeFactory AB',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-file.h')

    def test_ics_dbus_dbus_dbus_file_unix_c(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2006 Red Hat, Inc.',
            u'Copyright (c) 2003 CodeFactory AB',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-file-unix.c')

    def test_ics_dbus_dbus_dbus_hash_c(self):
        expected = [
            u'Copyright (c) 2002 Red Hat, Inc.',
            u'Copyright (c) 1991-1993 The Regents of the University of California.',
            u'Copyright (c) 1994 Sun Microsystems, Inc.',
            u'Copyright (c) 1991-1993 The Regents of the University of California.',
            u'Copyright (c) 1994 Sun Microsystems, Inc.',
            u'copyrighted by the Regents of the University of California, Sun Microsystems, Inc., Scriptics Corporation'
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-hash.c')

    def test_ics_dbus_dbus_dbus_hash_h(self):
        expected = [
            u'Copyright (c) 2002 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-hash.h')

    def test_ics_dbus_dbus_dbus_internals_c(self):
        expected = [
            u'Copyright (c) 2002, 2003 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-internals.c')

    def test_ics_dbus_dbus_dbus_internals_h(self):
        expected = [
            u'Copyright (c) 2002, 2003 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-internals.h')

    def test_ics_dbus_dbus_dbus_keyring_c(self):
        expected = [
            u'Copyright (c) 2003, 2004 Red Hat Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-keyring.c')

    def test_ics_dbus_dbus_dbus_keyring_h(self):
        expected = [
            u'Copyright (c) 2003 Red Hat Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-keyring.h')

    def test_ics_dbus_dbus_dbus_marshal_basic_c(self):
        expected = [
            u'Copyright (c) 2002 CodeFactory AB',
            u'Copyright (c) 2003, 2004, 2005 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-marshal-basic.c')

    def test_ics_dbus_dbus_dbus_marshal_basic_h(self):
        expected = [
            u'Copyright (c) 2002 CodeFactory AB',
            u'Copyright (c) 2004, 2005 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-marshal-basic.h')

    def test_ics_dbus_dbus_dbus_marshal_recursive_util_c(self):
        expected = [
            u'Copyright (c) 2004, 2005 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-marshal-recursive-util.c')

    def test_ics_dbus_dbus_dbus_md5_c(self):
        expected = [
            u'Copyright (c) 2003 Red Hat Inc.',
            u'Copyright (c) 1999, 2000 Aladdin Enterprises.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-md5.c')

    def test_ics_dbus_dbus_dbus_memory_c(self):
        expected = [
            u'Copyright (c) 2002, 2003 Red Hat Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-memory.c')

    def test_ics_dbus_dbus_dbus_message_h(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2005 Red Hat Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-message.h')

    def test_ics_dbus_dbus_dbus_message_factory_c(self):
        expected = [
            u'Copyright (c) 2005 Red Hat Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-message-factory.c')

    def test_ics_dbus_dbus_dbus_message_private_h(self):
        expected = [
            u'Copyright (c) 2005 Red Hat Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-message-private.h')

    def test_ics_dbus_dbus_dbus_message_util_c(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004, 2005 Red Hat Inc.',
            u'Copyright (c) 2002, 2003 CodeFactory AB',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-message-util.c')

    def test_ics_dbus_dbus_dbus_misc_c(self):
        expected = [
            u'Copyright (c) 2006 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-misc.c')

    def test_ics_dbus_dbus_dbus_nonce_c(self):
        expected = [
            u'Copyright (c) 2009 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.net',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-nonce.c')

    def test_ics_dbus_dbus_dbus_nonce_h(self):
        expected = [
            u'Copyright (c) 2009 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.net',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-nonce.h')

    def test_ics_dbus_dbus_dbus_object_tree_c(self):
        expected = [
            u'Copyright (c) 2003, 2005 Red Hat Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-object-tree.c')

    def test_ics_dbus_dbus_dbus_protocol_h(self):
        expected = [
            u'Copyright (c) 2002, 2003 CodeFactory AB',
            u'Copyright (c) 2004, 2005 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-protocol.h')

    def test_ics_dbus_dbus_dbus_server_c(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004, 2005 Red Hat Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-server.c')

    def test_ics_dbus_dbus_dbus_server_debug_pipe_c(self):
        expected = [
            u'Copyright (c) 2003 CodeFactory AB',
            u'Copyright (c) 2003, 2004 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-server-debug-pipe.c')

    def test_ics_dbus_dbus_dbus_server_socket_c(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004, 2006 Red Hat Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-server-socket.c')

    def test_ics_dbus_dbus_dbus_server_socket_h(self):
        expected = [
            u'Copyright (c) 2002, 2006 Red Hat Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-server-socket.h')

    def test_ics_dbus_dbus_dbus_server_win_c(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004 Red Hat Inc.',
            u'Copyright (c) 2007 Ralf Habacker <ralf.habacker@freenet.de>',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-server-win.c')

    def test_ics_dbus_dbus_dbus_server_win_h(self):
        expected = [
            u'Copyright (c) 2002 Red Hat Inc.',
            u'Copyright (c) 2007 Ralf Habacker <ralf.habacker@freenet.de>',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-server-win.h')

    def test_ics_dbus_dbus_dbus_sha_c(self):
        expected = [
            u'Copyright (c) 2003 Red Hat Inc.',
            u'Copyright (c) 1995 A. M. Kuchling',
            u'Copyright (c) 1995, A.M.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-sha.c')

    @expectedFailure
    def test_ics_dbus_dbus_dbus_sha_c_trail_name(self):
        expected = [
            u'Copyright (c) 2003 Red Hat Inc.',
            u'Copyright (c) 1995 A. M. Kuchling',
            u'Copyright (c) 1995 A. M. Kuchling',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-sha.c')

    def test_ics_dbus_dbus_dbus_sockets_win_h(self):
        expected = [
            u'Copyright (c) 2005 Novell, Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-sockets-win.h')

    def test_ics_dbus_dbus_dbus_spawn_c(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004 Red Hat, Inc.',
            u'Copyright (c) 2003 CodeFactory AB',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-spawn.c')

    def test_ics_dbus_dbus_dbus_spawn_win_c(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004 Red Hat, Inc.',
            u'Copyright (c) 2003 CodeFactory AB',
            u'Copyright (c) 2005 Novell, Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-spawn-win.c')

    def test_ics_dbus_dbus_dbus_string_h(self):
        expected = [
            u'Copyright (c) 2002, 2003 Red Hat, Inc.',
            u'Copyright (c) 2006 Ralf Habacker <ralf.habacker@freenet.de>',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-string.h')

    def test_ics_dbus_dbus_dbus_string_util_c(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004, 2005 Red Hat, Inc.',
            u'Copyright (c) 2006 Ralf Habacker <ralf.habacker@freenet.de>',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-string-util.c')

    def test_ics_dbus_dbus_dbus_sysdeps_pthread_c(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2006 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-sysdeps-pthread.c')

    def test_ics_dbus_dbus_dbus_sysdeps_util_unix_c(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004, 2005 Red Hat, Inc.',
            u'Copyright (c) 2003 CodeFactory AB',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-sysdeps-util-unix.c')

    def test_ics_dbus_dbus_dbus_sysdeps_util_win_c(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004, 2005 Red Hat, Inc.',
            u'Copyright (c) 2003 CodeFactory AB',
            u'Copyright (c) 2000 Werner Almesberger',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-sysdeps-util-win.c')

    def test_ics_dbus_dbus_dbus_sysdeps_win_c(self):
        expected = [
            u'Copyright (c) 2002, 2003 Red Hat, Inc.',
            u'Copyright (c) 2003 CodeFactory AB',
            u'Copyright (c) 2005 Novell, Inc.',
            u'Copyright (c) 2006 Ralf Habacker <ralf.habacker@freenet.de>',
            u'Copyright (c) 2006 Peter Kummel <syntheticpp@gmx.net>',
            u'Copyright (c) 2006 Christian Ehrlicher <ch.ehrlicher@gmx.de>',
            u'Copyright (c) 2002, 2003 Red Hat, Inc.',
            u'Copyright (c) 2003 CodeFactory AB',
            u'Copyright (c) 2005 Novell, Inc.',
            u'Copyright 2004 Eric Poech',
            u'Copyright 2004 Robert Shearman',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-sysdeps-win.c')

    def test_ics_dbus_dbus_dbus_sysdeps_win_h(self):
        expected = [
            u'Copyright (c) 2002, 2003 Red Hat, Inc.',
            u'Copyright (c) 2003 CodeFactory AB',
            u'Copyright (c) 2005 Novell, Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-sysdeps-win.h')

    def test_ics_dbus_dbus_dbus_sysdeps_wince_glue_c(self):
        expected = [
            u'Copyright (c) 2002, 2003 Red Hat, Inc.',
            u'Copyright (c) 2003 CodeFactory AB',
            u'Copyright (c) 2005 Novell, Inc.',
            u'Copyright (c) 2006 Ralf Habacker <ralf.habacker@freenet.de>',
            u'Copyright (c) 2006 Peter Kummel <syntheticpp@gmx.net>',
            u'Copyright (c) 2006 Christian Ehrlicher <ch.ehrlicher@gmx.de>',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-sysdeps-wince-glue.c')

    def test_ics_dbus_dbus_dbus_threads_c(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2006 Red Hat Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-threads.c')

    def test_ics_dbus_dbus_dbus_threads_internal_h(self):
        expected = [
            u'Copyright (c) 2002, 2005 Red Hat Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-threads-internal.h')

    def test_ics_dbus_dbus_dbus_transport_protected_h(self):
        expected = [
            u'Copyright (c) 2002, 2004 Red Hat Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-transport-protected.h')

    def test_ics_dbus_dbus_dbus_userdb_util_c(self):
        expected = [
            u'Copyright (c) 2003, 2004, 2005 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-dbus/dbus-userdb-util.c')

    def test_ics_dbus_dbus_sd_daemon_c(self):
        expected = [
            u'Copyright 2010 Lennart Poettering',
        ]
        check_detection(expected, 'ics/dbus-dbus/sd-daemon.c')

    def test_ics_dbus_dbus_versioninfo_rc_in(self):
        expected = [
            u'Copyright (c) 2005 g10 Code GmbH',
            u'Copyright (c) 2009 FreeDesktop.org',
        ]
        check_detection(expected, 'ics/dbus-dbus/versioninfo.rc.in')

    def test_ics_dbus_doc_introspect_dtd(self):
        expected = [
            u'(c) 2005-02-02 David A. Wheeler',
        ]
        check_detection(expected, 'ics/dbus-doc/introspect.dtd')

    def test_ics_dbus_doc_introspect_xsl(self):
        expected = [
            u'Copyright (c) 2005 Lennart Poettering.',
        ]
        check_detection(expected, 'ics/dbus-doc/introspect.xsl')

    def test_ics_dbus_test_decode_gcov_c(self):
        expected = [
            u'Copyright (c) 2003 Red Hat Inc.',
            u'Copyright (c) 1990, 1991, 1992, 1993, 1994, 1996, 1997, 1998, 1999, 2000, 2001, 2002 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/dbus-test/decode-gcov.c')

    def test_ics_dbus_tools_dbus_cleanup_sockets_1(self):
        expected = [
            u'Copyright (c) 2003 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-tools/dbus-cleanup-sockets.1')

    def test_ics_dbus_tools_dbus_cleanup_sockets_c(self):
        expected = [
            u'Copyright (c) 2003 Red Hat, Inc.',
            u'Copyright (c) 2002 Michael Meeks',
            u'Copyright (c) 2003 Red Hat, Inc.',
            u'Copyright (c) 2002 Michael Meeks',
        ]
        check_detection(expected, 'ics/dbus-tools/dbus-cleanup-sockets.c')

    def test_ics_dbus_tools_dbus_launch_c(self):
        expected = [
            u'Copyright (c) 2003, 2006 Red Hat, Inc.',
            u'Copyright (c) 2006 Thiago Macieira <thiago@kde.org>',
            u'Copyright (c) 2003 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-tools/dbus-launch.c')

    def test_ics_dbus_tools_dbus_launch_win_c(self):
        expected = [
            u'Copyright (c) 2007 Ralf Habacker <ralf.habacker@freenet.de>',
        ]
        check_detection(expected, 'ics/dbus-tools/dbus-launch-win.c')

    def test_ics_dbus_tools_dbus_launch_x11_c(self):
        expected = [
            u'Copyright (c) 2006 Thiago Macieira <thiago@kde.org>',
        ]
        check_detection(expected, 'ics/dbus-tools/dbus-launch-x11.c')

    def test_ics_dbus_tools_dbus_monitor_c(self):
        expected = [
            u'Copyright (c) 2003 Philip Blundell <philb@gnu.org>',
        ]
        check_detection(expected, 'ics/dbus-tools/dbus-monitor.c')

    def test_ics_dbus_tools_dbus_print_message_c(self):
        expected = [
            u'Copyright (c) 2003 Philip Blundell <philb@gnu.org>',
            u'Copyright (c) 2003 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-tools/dbus-print-message.c')

    def test_ics_dbus_tools_dbus_uuidgen_1(self):
        expected = [
            u'Copyright (c) 2006 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-tools/dbus-uuidgen.1')

    def test_ics_dbus_tools_dbus_uuidgen_c(self):
        expected = [
            u'Copyright (c) 2006 Red Hat, Inc.',
            u'Copyright (c) 2006 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-tools/dbus-uuidgen.c')

    def test_ics_dbus_tools_dbus_viewer_c(self):
        expected = [
            u'Copyright (c) 2003 Red Hat, Inc.',
            u'Copyright (c) 2003 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/dbus-tools/dbus-viewer.c')

    def test_ics_dbus_tools_strtoll_c(self):
        expected = [
            u'Copyright (c) 1992, 1993 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/dbus-tools/strtoll.c')

    def test_ics_dhcpcd_arp_c(self):
        expected = [
            u'Copyright (c) 2006-2008 Roy Marples <roy@marples.name>',
        ]
        check_detection(expected, 'ics/dhcpcd/arp.c')

    def test_ics_dhcpcd_bind_c(self):
        expected = [
            u'Copyright (c) 2006-2010 Roy Marples <roy@marples.name>',
        ]
        check_detection(expected, 'ics/dhcpcd/bind.c')

    def test_ics_dhcpcd_bpf_filter_h(self):
        expected = [
            u'Copyright (c) 2006-2008 Roy Marples <roy@marples.name>',
            u'Copyright (c) 2004,2007 by Internet Systems Consortium, Inc.',
            u'Copyright (c) 1996-2003 by Internet Software Consortium',
        ]
        check_detection(expected, 'ics/dhcpcd/bpf-filter.h')

    def test_ics_dhcpcd_client_c(self):
        expected = [
            u'Copyright 2006-2008 Roy Marples <roy@marples.name>',
        ]
        check_detection(expected, 'ics/dhcpcd/client.c')

    def test_ics_dhcpcd_common_c(self):
        expected = [
            u'Copyright (c) 2006-2009 Roy Marples <roy@marples.name>',
        ]
        check_detection(expected, 'ics/dhcpcd/common.c')

    def test_ics_dhcpcd_dhcpcd_8(self):
        expected = [
            u'Copyright (c) 2006-2010 Roy Marples',
        ]
        check_detection(expected, 'ics/dhcpcd/dhcpcd.8')

    def test_ics_dhcpcd_dhcpcd_c(self):
        expected = [
            u'Copyright (c) 2006-2010 Roy Marples <roy@marples.name>',
            u'Copyright (c) 2006-2010 Roy Marples',
        ]
        check_detection(expected, 'ics/dhcpcd/dhcpcd.c')

    def test_ics_dhcpcd_ifaddrs_c(self):
        expected = [
            u'Copyright 2011, The Android Open Source Project',
        ]
        check_detection(expected, 'ics/dhcpcd/ifaddrs.c')

    def test_ics_dhcpcd_if_linux_wireless_c(self):
        expected = [
            u'Copyright (c) 2009-2010 Roy Marples <roy@marples.name>',
        ]
        check_detection(expected, 'ics/dhcpcd/if-linux-wireless.c')

    def test_ics_dhcpcd_notice(self):
        expected = [
            u'Copyright 2006-2008 Roy Marples <roy@marples.name>',
            u'Copyright (c) 2004,2007 by Internet Systems Consortium, Inc.',
            u'Copyright (c) 1996-2003 by Internet Software Consortium',
        ]
        check_detection(expected, 'ics/dhcpcd/NOTICE')

    def test_ics_dhcpcd_readme(self):
        expected = [
            u'Copyright (c) 2006-2010 Roy Marples <roy@marples.name>',
        ]
        check_detection(expected, 'ics/dhcpcd/README')

    def test_ics_dhcpcd_compat_arc4random_c(self):
        expected = [
            u'Copyright 1996 David Mazieres <dm@lcs.mit.edu>',
        ]
        check_detection(expected, 'ics/dhcpcd-compat/arc4random.c')

    def test_ics_dhcpcd_compat_linkaddr_c(self):
        expected = [
            u'Copyright (c) 1990, 1993 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/dhcpcd-compat/linkaddr.c')

    def test_ics_dhcpcd_mk_cc_mk(self):
        expected = [
            u'Copyright 2008 Roy Marples <roy@marples.name>',
        ]
        check_detection(expected, 'ics/dhcpcd-mk/cc.mk')

    def test_ics_dhcpcd_mk_dist_mk(self):
        expected = [
            u'Copyright 2008-2009 Roy Marples <roy@marples.name>',
        ]
        check_detection(expected, 'ics/dhcpcd-mk/dist.mk')

    def test_ics_dnsmasq_copying_v3(self):
        expected = [
            u'Copyright (c) 2007 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/dnsmasq/COPYING-v3')

    def test_ics_dnsmasq_makefile(self):
        expected = [
            u'Copyright (c) 2000-2009 Simon Kelley',
        ]
        check_detection(expected, 'ics/dnsmasq/Makefile')

    def test_ics_dnsmasq_contrib_suse_dnsmasq_suse_spec(self):
        expected = [
            u'Copyright GPL Group',
        ]
        check_detection(expected, 'ics/dnsmasq-contrib-Suse/dnsmasq-suse.spec')

    def test_ics_dnsmasq_contrib_wrt_dhcp_lease_time_c(self):
        expected = [
            u'Copyright (c) 2007 Simon Kelley',
        ]
        check_detection(expected, 'ics/dnsmasq-contrib-wrt/dhcp_lease_time.c')

    def test_ics_dnsmasq_contrib_wrt_dhcp_release_c(self):
        expected = [
            u'Copyright (c) 2006 Simon Kelley',
        ]
        check_detection(expected, 'ics/dnsmasq-contrib-wrt/dhcp_release.c')

    def test_ics_dnsmasq_contrib_wrt_lease_update_sh(self):
        expected = [
            u'Copyright (c) 2006 Simon Kelley',
        ]
        check_detection(expected, 'ics/dnsmasq-contrib-wrt/lease_update.sh')

    def test_ics_dnsmasq_src_bpf_c(self):
        expected = [
            u'Copyright (c) 2000-2009 Simon Kelley',
        ]
        check_detection(expected, 'ics/dnsmasq-src/bpf.c')

    def test_ics_dnsmasq_src_dnsmasq_h(self):
        expected = [
            u'Copyright (c) 2000-2009 Simon Kelley',
            u'Copyright (c) 2000-2009 Simon Kelley',
        ]
        check_detection(expected, 'ics/dnsmasq-src/dnsmasq.h')

    def test_ics_dnsmasq_src_nameser_h(self):
        expected = [
            u'Copyright (c) 1983, 1989, 1993 The Regents of the University of California.',
            u'Portions Copyright (c) 1993 by Digital Equipment Corporation.',
            u'Portions Copyright (c) 1995 by International Business Machines, Inc.',
        ]
        check_detection(expected, 'ics/dnsmasq-src/nameser.h')

    def test_ics_doclava_notice(self):
        expected = [
            u'Copyright (c) 2010 Google Inc.',
            u'Copyright (c) 2008 John Resig (jquery.com)',
            u'Copyright (c) 2009 John Resig, http://jquery.com',
        ]
        check_detection(expected, 'ics/doclava/NOTICE')

    def test_ics_doclava_res_assets_templates_assets_jquery_history_js(self):
        expected = [
            u'Copyright (c) 2008 Tom Rodenberg',
        ]
        check_detection(expected, 'ics/doclava-res-assets-templates-assets/jquery-history.js')

    def test_ics_doclava_res_assets_templates_assets_jquery_resizable_min_js(self):
        expected = [
            u'Copyright (c) 2009 John Resig',
            u'Copyright 2009, The Dojo Foundation',
            u'Copyright (c) 2009 AUTHORS.txt (http://jqueryui.com/about)',
            u'Copyright (c) 2009 AUTHORS.txt (http://jqueryui.com/about)',
        ]
        check_detection(expected, 'ics/doclava-res-assets-templates-assets/jquery-resizable.min.js')

    def test_ics_doclava_src_com_google_doclava_annotationinstanceinfo_java(self):
        expected = [
            u'Copyright (c) 2010 Google Inc.',
        ]
        check_detection(expected, 'ics/doclava-src-com-google-doclava/AnnotationInstanceInfo.java')

    def test_ics_doclava_src_com_google_doclava_doclava2_java(self):
        expected = [
            u'Copyright (c) 2011 Google Inc.',
        ]
        check_detection(expected, 'ics/doclava-src-com-google-doclava/Doclava2.java')

    def test_ics_doclava_src_com_google_doclava_parser_java_g(self):
        expected = [
            u'Copyright (c) 2007-2008 Terence Parr',
        ]
        check_detection(expected, 'ics/doclava-src-com-google-doclava-parser/Java.g')

    def test_ics_dropbear_agentfwd_h(self):
        expected = [
            u'Copyright (c) 2002,2003 Matt Johnston',
        ]
        check_detection(expected, 'ics/dropbear/agentfwd.h')

    def test_ics_dropbear_atomicio_c(self):
        expected = [
            u'Copyright (c) 1995,1999 Theo de Raadt.',
        ]
        check_detection(expected, 'ics/dropbear/atomicio.c')

    def test_ics_dropbear_circbuffer_c(self):
        expected = [
            u'Copyright (c) 2002-2004 Matt Johnston',
        ]
        check_detection(expected, 'ics/dropbear/circbuffer.c')

    def test_ics_dropbear_cli_algo_c(self):
        expected = [
            u'Copyright (c) 2002,2003 Matt Johnston',
            u'Copyright (c) 2004 by Mihnea Stoenescu',
        ]
        check_detection(expected, 'ics/dropbear/cli-algo.c')

    def test_ics_dropbear_cli_authinteract_c(self):
        expected = [
            u'Copyright (c) 2005 Matt Johnston',
        ]
        check_detection(expected, 'ics/dropbear/cli-authinteract.c')

    def test_ics_dropbear_cli_kex_c(self):
        expected = [
            u'Copyright (c) 2002-2004 Matt Johnston',
            u'Copyright (c) 2004 by Mihnea Stoenescu',
        ]
        check_detection(expected, 'ics/dropbear/cli-kex.c')

    def test_ics_dropbear_common_kex_c(self):
        expected = [
            u'Copyright (c) 2002-2004 Matt Johnston',
            u'Portions Copyright (c) 2004 by Mihnea Stoenescu',
        ]
        check_detection(expected, 'ics/dropbear/common-kex.c')

    def test_ics_dropbear_compat_c(self):
        expected = [
            u'Copyright (c) 2002,2003 Matt Johnston',
            u'Copyright (c) 1998 Todd C. Miller <Todd.Miller@courtesan.com>',
            u'Copyright (c) 1990, 1993 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/dropbear/compat.c')

    def test_ics_dropbear_configure(self):
        expected = [
            u'Copyright (c) 2003 Free Software Foundation, Inc.',
            u'Copyright (c) 2003 Free Software Foundation, Inc.',
            u'Copyright (c) 2003 Free Software Foundation, Inc.',
            u'Copyright (c) 2003 Free Software Foundation, Inc.',
            u'Copyright (c) 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/dropbear/configure')

    def test_ics_dropbear_dbutil_c(self):
        expected = [
            u'Copyright (c) 2002,2003 Matt Johnston',
            u'Copyright (c) 1998 Todd C. Miller <Todd.Miller@courtesan.com>',
        ]
        check_detection(expected, 'ics/dropbear/dbutil.c')

    def test_ics_dropbear_fake_rfc2553_c(self):
        expected = [
            u'Copyright (c) 2000-2003 Damien Miller.',
            u'Copyright (c) 1999 WIDE Project.',
        ]
        check_detection(expected, 'ics/dropbear/fake-rfc2553.c')

    def test_ics_dropbear_install_sh(self):
        expected = [
            u'Copyright 1991 by the Massachusetts Institute of Technology',
        ]
        check_detection(expected, 'ics/dropbear/install-sh')

    def test_ics_dropbear_keyimport_c_trail_name(self):
        expected = [
            u'copyright 2003 Matt Johnston',
            u'copyright 1997-2003 Simon Tatham.',
            u'Portions copyright Robert de Bath, Joris van Rantwijk, Delian Delchev, Andreas Schultz, Jeroen Massar, Wez Furlong, Nicolas Barry, Justin Bradford, and CORE SDI S.A.',
        ]
        check_detection(expected, 'ics/dropbear/keyimport.c')

    def test_ics_dropbear_license_extra_portion_trail_name(self):
        expected = [
            u'(c) 2004 Mihnea Stoenescu',
            u'Copyright (c) 2002-2006 Matt Johnston',
            u'Portions copyright (c) 2004 Mihnea Stoenescu',
            u'Copyright (c) 1995 Tatu Ylonen <ylo@cs.hut.fi> , Espoo, Finland',
            u'(c) Todd C. Miller',
            u'copyright 1997-2003 Simon Tatham.',
            u'Portions copyright Robert de Bath, Joris van Rantwijk, Delian Delchev, Andreas Schultz, Jeroen Massar, Wez Furlong, Nicolas Barry, Justin Bradford, and CORE SDI S.A.',
        ]
        check_detection(expected, 'ics/dropbear/LICENSE')

    def test_ics_dropbear_loginrec_c_extra_portion_extra_portion(self):
        expected = [
            u'Copyright (c) 2000 Andre Lucas.',
            u'Portions copyright (c) 1998 Todd C. Miller',
            u'Portions copyright (c) 1996 Jason Downs',
            u'Portions copyright (c) 1996 Theo de Raadt',
        ]
        check_detection(expected, 'ics/dropbear/loginrec.c')

    def test_ics_dropbear_loginrec_h(self):
        expected = [
            u'Copyright (c) 2000 Andre Lucas.',
        ]
        check_detection(expected, 'ics/dropbear/loginrec.h')

    def test_ics_dropbear_netbsd_getpass_c(self):
        expected = [
            u'Copyright (c) 1988, 1993 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/dropbear/netbsd_getpass.c')

    def test_ics_dropbear_progressmeter_c(self):
        expected = [
            u'Copyright (c) 2003 Nils Nordman.',
        ]
        check_detection(expected, 'ics/dropbear/progressmeter.c')

    def test_ics_dropbear_progressmeter_h(self):
        expected = [
            u'Copyright (c) 2002 Nils Nordman.',
        ]
        check_detection(expected, 'ics/dropbear/progressmeter.h')

    def test_ics_dropbear_scp_c(self):
        expected = [
            u'Copyright (c) 1999 Theo de Raadt.',
            u'Copyright (c) 1999 Aaron Campbell.',
            u'Copyright (c) 1983, 1990, 1992, 1993, 1995 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/dropbear/scp.c')

    def test_ics_dropbear_scpmisc_c(self):
        expected = [
            u'Copyright (c) 2000 Markus Friedl.',
            u'Copyright (c) 1995 Tatu Ylonen <ylo@cs.hut.fi> , Espoo, Finland',
        ]
        check_detection(expected, 'ics/dropbear/scpmisc.c')

    def test_ics_dropbear_scpmisc_h(self):
        expected = [
            u'Copyright (c) 1995 Tatu Ylonen <ylo@cs.hut.fi> , Espoo, Finland',
        ]
        check_detection(expected, 'ics/dropbear/scpmisc.h')

    def test_ics_dropbear_svr_authpam_c(self):
        expected = [
            u'Copyright (c) 2004 Martin Carlsson',
            u'Portions (c) 2004 Matt Johnston',
        ]
        check_detection(expected, 'ics/dropbear/svr-authpam.c')

    def test_ics_dropbear_svr_main_c(self):
        expected = [
            u'Copyright (c) 2002-2006 Matt Johnston',
        ]
        check_detection(expected, 'ics/dropbear/svr-main.c')

    def test_ics_dropbear_libtommath_mtest_mpi_c(self):
        expected = [
            u'Copyright (c) 1998 Michael J. Fromberger',
        ]
        check_detection(expected, 'ics/dropbear-libtommath-mtest/mpi.c')

    def test_ics_dropbear_libtommath_mtest_mpi_h(self):
        expected = [
            u'Copyright (c) 1998 Michael J. Fromberger',
        ]
        check_detection(expected, 'ics/dropbear-libtommath-mtest/mpi.h')

    def test_ics_easymock_src_org_easymock_abstractmatcher_java_trail_name(self):
        expected = [
            u'Copyright 2001-2009 OFFIS, Tammo Freese',
        ]
        check_detection(expected, 'ics/easymock-src-org-easymock/AbstractMatcher.java')

    def test_ics_easymock_src_org_easymock_capture_java_trail_name(self):
        expected = [
            u'Copyright 2003-2009 OFFIS, Henri Tremblay',
        ]
        check_detection(expected, 'ics/easymock-src-org-easymock/Capture.java')

    def test_ics_easymock_src_org_easymock_iargumentmatcher_java_trail_name(self):
        expected = [
            u'Copyright 2001-2006 OFFIS, Tammo Freese',
        ]
        check_detection(expected, 'ics/easymock-src-org-easymock/IArgumentMatcher.java')

    def test_ics_embunit_inc_assertimpl_h(self):
        expected = [
            u'Copyright (c) 2003 Embedded Unit Project',
        ]
        check_detection(expected, 'ics/embunit-inc/AssertImpl.h')

    def test_ics_embunit_src_stdimpl_c(self):
        expected = [
            u'Copyright (c) 2003 Embedded Unit Project',
        ]
        check_detection(expected, 'ics/embunit-src/stdImpl.c')

    def test_ics_emma_android_mk(self):
        expected = [
            u'Copyright 2008 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/emma/Android.mk')

    def test_ics_emma_build_txt(self):
        expected = [
            u'Copyright (c) 2003-2004 Vlad Roubtsov.',
        ]
        check_detection(expected, 'ics/emma/BUILD.txt')

    def test_ics_emma_test_sh(self):
        expected = [
            u'Copyright 2009 Google Inc.',
        ]
        check_detection(expected, 'ics/emma/test.sh')

    def test_ics_emma_ant_ant14_com_vladium_emma_antmain_java(self):
        expected = [
            u'Copyright (c) 2003 Vladimir Roubtsov.',
            u'Vlad Roubtsov, (c) 2004',
        ]
        check_detection(expected, 'ics/emma-ant-ant14-com-vladium-emma/ANTMain.java')

    def test_ics_emma_ant_ant14_com_vladium_emma_emmajavatask_java(self):
        expected = [
            u'Copyright (c) 2003 Vladimir Roubtsov.',
            u'Vlad Roubtsov, (c) 2003',
        ]
        check_detection(expected, 'ics/emma-ant-ant14-com-vladium-emma/emmajavaTask.java')

    def test_ics_emma_core_data_manifest_mf_extra_implementation(self):
        expected = [
            u'(c) Vladimir Roubtsov',
        ]
        check_detection(expected, 'ics/emma-core-data/MANIFEST.MF')

    def test_ics_emma_core_java12_com_vladium_emma_iappconstants_java_extra_string(self):
        expected = [
            u'Copyright (c) 2003 Vladimir Roubtsov.',
            u'Vlad Roubtsov, (c) 2003',
            u'(c) Vladimir Roubtsov',
        ]
        check_detection(expected, 'ics/emma-core-java12-com-vladium-emma/IAppConstants.java')

    def test_ics_emma_core_java12_com_vladium_emma_processor_java(self):
        expected = [
            u'Copyright (c) 2004 Vladimir Roubtsov.',
            u'Vlad Roubtsov, (c) 2004',
        ]
        check_detection(expected, 'ics/emma-core-java12-com-vladium-emma/Processor.java')

    def test_ics_emma_core_java12_com_vladium_emma_data_imetadataconstants_java(self):
        expected = [
            u'Copyright (c) 2003 Vladimir Roubtsov.',
        ]
        check_detection(expected, 'ics/emma-core-java12-com-vladium-emma-data/IMetadataConstants.java')

    def test_ics_emma_core_java12_com_vladium_emma_report_lcov_reportgenerator_java(self):
        expected = [
            u'Copyright 2009 Google Inc.',
            u'Copyright (c) 2003 Vladimir Roubtsov.',
            u'Vlad Roubtsov, (c) 2003',
            u'Tim Baverstock, (c) 2009',
        ]
        check_detection(expected, 'ics/emma-core-java12-com-vladium-emma-report-lcov/ReportGenerator.java')

    def test_ics_emma_core_java12_com_vladium_jcd_cls_abstractclassdefvisitor_java(self):
        expected = [
            u'Copyright (c) 2003 Vladimir Roubtsov.',
            u'(c) 2001, Vlad Roubtsov',
        ]
        check_detection(expected, 'ics/emma-core-java12-com-vladium-jcd-cls/AbstractClassDefVisitor.java')

    def test_ics_emma_core_java12_com_vladium_jcd_cls_constantcollection_java(self):
        expected = [
            u'Copyright (c) 2003 Vladimir Roubtsov.',
            u'(c) 2001, Vladimir Roubtsov',
        ]
        check_detection(expected, 'ics/emma-core-java12-com-vladium-jcd-cls/ConstantCollection.java')

    def test_ics_emma_core_java12_com_vladium_logging_iloglevels_java(self):
        expected = [
            u'Copyright (c) 2003 Vladimir Roubtsov.',
            u'Vlad Roubtsov, (c) 2001',
        ]
        check_detection(expected, 'ics/emma-core-java12-com-vladium-logging/ILogLevels.java')

    def test_ics_emma_core_java12_com_vladium_util_softvaluemap_java(self):
        expected = [
            u'Copyright (c) 2003 Vladimir Roubtsov.',
            u'(c) 2002, Vlad Roubtsov',
        ]
        check_detection(expected, 'ics/emma-core-java12-com-vladium-util/SoftValueMap.java')

    def test_ics_emma_core_java12_com_vladium_util_wcmatcher_java(self):
        expected = [
            u'Copyright (c) 2003 Vladimir Roubtsov.',
            u'Vlad Roubtsov, (c) 2002',
        ]
        check_detection(expected, 'ics/emma-core-java12-com-vladium-util/WCMatcher.java')

    def test_ics_esd_include_audiofile_h(self):
        expected = [
            u'Copyright (c) 1998-2000, Michael Pruett <michael@68k.org>',
        ]
        check_detection(expected, 'ics/esd-include/audiofile.h')

    def test_ics_expat_configure(self):
        expected = [
            u'Copyright (c) 2003 Free Software Foundation, Inc.',
            u'Copyright (c) 2003 Free Software Foundation, Inc.',
            u'Copyright 1996, 1997, 1998, 1999, 2000, 2001, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001 Free Software Foundation, Inc.',
            u'Copyright (c) 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/expat/configure')

    def test_ics_expat_configure_in(self):
        expected = [
            u'Copyright 2000 Clark Cooper',
        ]
        check_detection(expected, 'ics/expat/configure.in')

    def test_ics_expat_notice(self):
        expected = [
            u'Copyright (c) 1998, 1999, 2000 Thai Open Source Software Center Ltd and Clark Cooper',
            u'Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006 Expat maintainers.'
        ]
        check_detection(expected, 'ics/expat/NOTICE')

    def test_ics_expat_amiga_expat_lib_c_trail_maint(self):
        expected = [
            u'Copyright (c) 2001-2007 Expat maintainers.',
        ]
        check_detection(expected, 'ics/expat-amiga/expat_lib.c')

    def test_ics_expat_conftools_libtool_m4(self):
        expected = [
            u'Copyright 1996, 1997, 1998, 1999, 2000, 2001, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/expat-conftools/libtool.m4')

    def test_ics_expat_conftools_ltmain_sh(self):
        expected = [
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/expat-conftools/ltmain.sh')

    def test_ics_expat_doc_reference_html(self):
        expected = [
            u'Copyright 1999,2000 Clark Cooper <coopercc@netheaven.com>',
        ]
        check_detection(expected, 'ics/expat-doc/reference.html')

    def test_ics_expat_examples_outline_c(self):
        expected = [
            u'Copyright 1999, Clark Cooper',
        ]
        check_detection(expected, 'ics/expat-examples/outline.c')

    def test_ics_expat_lib_ascii_h(self):
        expected = [
            u'Copyright (c) 1998, 1999 Thai Open Source Software Center Ltd',
        ]
        check_detection(expected, 'ics/expat-lib/ascii.h')

    def test_ics_expat_lib_expat_h(self):
        expected = [
            u'Copyright (c) 1998, 1999, 2000 Thai Open Source Software Center Ltd',
        ]
        check_detection(expected, 'ics/expat-lib/expat.h')

    def test_ics_expat_lib_macconfig_h(self):
        expected = [
            u'Copyright 2000, Clark Cooper',
        ]
        check_detection(expected, 'ics/expat-lib/macconfig.h')

    def test_ics_expat_lib_makefile_mpw_extra_portion(self):
        expected = [
            u'Copyright (c) 2002 Daryle Walker',
            u'Portions Copyright (c) 2002 Thomas Wegner see the COPYING',
        ]
        check_detection(expected, 'ics/expat-lib/Makefile.MPW')

    def test_ics_expat_lib_xmlparse_c(self):
        expected = [
            u'Copyright (c) 1998, 1999, 2000 Thai Open Source Software Center Ltd',
        ]
        check_detection(expected, 'ics/expat-lib/xmlparse.c')

    def test_ics_expat_lib_xmltok_c(self):
        expected = [
            u'Copyright (c) 1998, 1999 Thai Open Source Software Center Ltd',
        ]
        check_detection(expected, 'ics/expat-lib/xmltok.c')

    def test_ics_expat_tests_chardata_c(self):
        expected = [
            u'Copyright (c) 1998-2003 Thai Open Source Software Center Ltd',
        ]
        check_detection(expected, 'ics/expat-tests/chardata.c')

    def test_ics_expat_win32_expat_iss(self):
        expected = [
            u'Copyright (c) 1998-2006 Thai Open Source Software Center, Clark Cooper, and the Expat maintainers',
        ]
        check_detection(expected, 'ics/expat-win32/expat.iss')

    def test_ics_eyes_free_notice(self):
        expected = [
            u'Copyright 2010 Google Inc.',
        ]
        check_detection(expected, 'ics/eyes-free/NOTICE')

    def test_ics_fdlibm_configure(self):
        expected = [
            u'Copyright (c) 2003 Free Software Foundation, Inc.',
            u'Copyright (c) 2003 Free Software Foundation, Inc.',
            u'Copyright (c) 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/fdlibm/configure')

    def test_ics_fdlibm_e_acos_c(self):
        expected = [
            u'Copyright (c) 1993 by Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/fdlibm/e_acos.c')

    def test_ics_fdlibm_e_exp_c(self):
        expected = [
            u'Copyright (c) 2004 by Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/fdlibm/e_exp.c')

    def test_ics_fdlibm_k_tan_c(self):
        expected = [
            u'Copyright 2004 Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/fdlibm/k_tan.c')

    def test_ics_fdlibm_makefile_in(self):
        expected = [
            u'Copyright (c) 1993 by Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/fdlibm/makefile.in')

    def test_ics_fdlibm_notice(self):
        expected = [
            u'Copyright (c) 1993 by Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/fdlibm/NOTICE')

    def test_ics_flac_notice(self):
        expected = [
            u'Copyright (c) 2000,2001,2002,2003,2004,2005,2006,2007 Josh Coalson',
        ]
        check_detection(expected, 'ics/flac/NOTICE')

    def test_ics_flac_include_flac_all_h(self):
        expected = [
            u'Copyright (c) 2000,2001,2002,2003,2004,2005,2006,2007 Josh Coalson',
        ]
        check_detection(expected, 'ics/flac-include-FLAC/all.h')

    def test_ics_flac_include_flac_assert_h(self):
        expected = [
            u'Copyright (c) 2001,2002,2003,2004,2005,2006,2007 Josh Coalson',
        ]
        check_detection(expected, 'ics/flac-include-FLAC/assert.h')

    def test_ics_flac_include_flac_callback_h(self):
        expected = [
            u'Copyright (c) 2004,2005,2006,2007 Josh Coalson',
        ]
        check_detection(expected, 'ics/flac-include-FLAC/callback.h')

    def test_ics_flac_include_share_alloc_h(self):
        expected = [
            u'Copyright (c) 2011 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/flac-include-share/alloc.h')

    def test_ics_flac_libflac_makefile_am(self):
        expected = [
            u'Copyright (c) 2001,2002,2003,2004,2005,2006,2007 Josh Coalson',
        ]
        check_detection(expected, 'ics/flac-libFLAC/Makefile.am')

    def test_ics_flac_libflac_makefile_in(self):
        expected = [
            u'Copyright 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003 Free Software Foundation, Inc.',
            u'Copyright (c) 2001,2002,2003,2004,2005,2006,2007 Josh Coalson',
        ]
        check_detection(expected, 'ics/flac-libFLAC/Makefile.in')

    def test_ics_flac_libflac_ogg_decoder_aspect_c(self):
        expected = [
            u'Copyright (c) 2002,2003,2004,2005,2006,2007 Josh Coalson',
        ]
        check_detection(expected, 'ics/flac-libFLAC/ogg_decoder_aspect.c')

    def test_ics_flac_libflac_window_c(self):
        expected = [
            u'Copyright (c) 2006,2007 Josh Coalson',
        ]
        check_detection(expected, 'ics/flac-libFLAC/window.c')

    def test_ics_flac_libflac_ia32_bitreader_asm_nasm(self):
        expected = [
            u'Copyright (c) 2001,2002,2003,2004,2005,2006,2007 Josh Coalson',
        ]
        check_detection(expected, 'ics/flac-libFLAC-ia32/bitreader_asm.nasm')

    def test_ics_flac_libflac_ppc_makefile_am(self):
        expected = [
            u'Copyright (c) 2004,2005,2006,2007 Josh Coalson',
        ]
        check_detection(expected, 'ics/flac-libFLAC-ppc/Makefile.am')

    def test_ics_flac_libflac_ppc_makefile_in(self):
        expected = [
            u'Copyright 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003 Free Software Foundation, Inc.',
            u'Copyright (c) 2004,2005,2006,2007 Josh Coalson',
        ]
        check_detection(expected, 'ics/flac-libFLAC-ppc/Makefile.in')

    def test_ics_freetype_notice(self):
        expected = [
            u'Copyright 1996-2002, 2006 by David Turner, Robert Wilhelm, and Werner Lemberg',
            u'copyright (c) The FreeType Project (www.freetype.org).',
            u'copyright (c) 1996-2000 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype/NOTICE')

    def test_ics_freetype_builds_ft2unix_h(self):
        expected = [
            u'Copyright 1996-2001, 2003, 2006 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-builds/ft2unix.h')

    def test_ics_freetype_include_ft2build_h(self):
        expected = [
            u'Copyright 1996-2001, 2006 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include/ft2build.h')

    def test_ics_freetype_include_freetype_freetype_h(self):
        expected = [
            u'Copyright 1996-2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/freetype.h')

    def test_ics_freetype_include_freetype_ftadvanc_h(self):
        expected = [
            u'Copyright 2008 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftadvanc.h')

    def test_ics_freetype_include_freetype_ftbbox_h(self):
        expected = [
            u'Copyright 1996-2001, 2003, 2007, 2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftbbox.h')

    def test_ics_freetype_include_freetype_ftbdf_h(self):
        expected = [
            u'Copyright 2002, 2003, 2004, 2006, 2009 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftbdf.h')

    def test_ics_freetype_include_freetype_ftbitmap_h(self):
        expected = [
            u'Copyright 2004, 2005, 2006, 2008 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftbitmap.h')

    def test_ics_freetype_include_freetype_ftcache_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftcache.h')

    def test_ics_freetype_include_freetype_ftcid_h(self):
        expected = [
            u'Copyright 2007, 2009 by Dereg Clegg, Michael Toftdal.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftcid.h')

    def test_ics_freetype_include_freetype_fterrdef_h(self):
        expected = [
            u'Copyright 2002, 2004, 2006, 2007, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/fterrdef.h')

    def test_ics_freetype_include_freetype_fterrors_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2004, 2007 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/fterrors.h')

    def test_ics_freetype_include_freetype_ftgasp_h(self):
        expected = [
            u'Copyright 2007, 2008, 2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftgasp.h')

    def test_ics_freetype_include_freetype_ftglyph_h(self):
        expected = [
            u'Copyright 1996-2003, 2006, 2008, 2009, 2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftglyph.h')

    def test_ics_freetype_include_freetype_ftgxval_h_trail_name(self):
        expected = [
            u'Copyright 2004, 2005, 2006 by Masatake YAMATO, Redhat K.K, David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftgxval.h')

    def test_ics_freetype_include_freetype_ftgzip_h(self):
        expected = [
            u'Copyright 2002, 2003, 2004, 2006 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftgzip.h')

    def test_ics_freetype_include_freetype_ftimage_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftimage.h')

    def test_ics_freetype_include_freetype_ftincrem_h(self):
        expected = [
            u'Copyright 2002, 2003, 2006, 2007, 2008, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftincrem.h')

    def test_ics_freetype_include_freetype_ftlcdfil_h(self):
        expected = [
            u'Copyright 2006, 2007, 2008, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftlcdfil.h')

    def test_ics_freetype_include_freetype_ftlist_h(self):
        expected = [
            u'Copyright 1996-2001, 2003, 2007, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftlist.h')

    def test_ics_freetype_include_freetype_ftlzw_h(self):
        expected = [
            u'Copyright 2004, 2006 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftlzw.h')

    def test_ics_freetype_include_freetype_ftmac_h(self):
        expected = [
            u'Copyright 1996-2001, 2004, 2006, 2007 by Just van Rossum, David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftmac.h')

    def test_ics_freetype_include_freetype_ftmm_h(self):
        expected = [
            u'Copyright 1996-2001, 2003, 2004, 2006, 2009 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftmm.h')

    def test_ics_freetype_include_freetype_ftmodapi_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2006, 2008, 2009, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftmodapi.h')

    def test_ics_freetype_include_freetype_ftmoderr_h(self):
        expected = [
            u'Copyright 2001, 2002, 2003, 2004, 2005, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftmoderr.h')

    def test_ics_freetype_include_freetype_ftotval_h(self):
        expected = [
            u'Copyright 2004, 2005, 2006, 2007 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftotval.h')

    def test_ics_freetype_include_freetype_ftoutln_h(self):
        expected = [
            u'Copyright 1996-2003, 2005-2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftoutln.h')

    def test_ics_freetype_include_freetype_ftpfr_h(self):
        expected = [
            u'Copyright 2002, 2003, 2004, 2006, 2008, 2009 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftpfr.h')

    def test_ics_freetype_include_freetype_ftrender_h(self):
        expected = [
            u'Copyright 1996-2001, 2005, 2006, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftrender.h')

    def test_ics_freetype_include_freetype_ftsnames_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2006, 2009, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftsnames.h')

    def test_ics_freetype_include_freetype_ftstroke_h(self):
        expected = [
            u'Copyright 2002-2006, 2008, 2009, 2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftstroke.h')

    def test_ics_freetype_include_freetype_ftsynth_h(self):
        expected = [
            u'Copyright 2000-2001, 2003, 2006, 2008 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftsynth.h')

    def test_ics_freetype_include_freetype_ftsystem_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2005, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftsystem.h')

    def test_ics_freetype_include_freetype_fttrigon_h(self):
        expected = [
            u'Copyright 2001, 2003, 2005, 2007 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/fttrigon.h')

    def test_ics_freetype_include_freetype_fttypes_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2004, 2006, 2007, 2008 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/fttypes.h')

    def test_ics_freetype_include_freetype_ftwinfnt_h(self):
        expected = [
            u'Copyright 2003, 2004, 2008 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftwinfnt.h')

    def test_ics_freetype_include_freetype_ftxf86_h(self):
        expected = [
            u'Copyright 2002, 2003, 2004, 2006, 2007 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ftxf86.h')

    def test_ics_freetype_include_freetype_t1tables_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2004, 2006, 2008, 2009 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/t1tables.h')

    def test_ics_freetype_include_freetype_ttnameid_h(self):
        expected = [
            u'Copyright 1996-2002, 2003, 2004, 2006, 2007, 2008 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ttnameid.h')

    def test_ics_freetype_include_freetype_tttables_h(self):
        expected = [
            u'Copyright 1996-2005, 2008-2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/tttables.h')

    def test_ics_freetype_include_freetype_tttags_h(self):
        expected = [
            u'Copyright 1996-2001, 2004, 2005, 2007, 2008 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/tttags.h')

    def test_ics_freetype_include_freetype_ttunpat_h(self):
        expected = [
            u'Copyright 2003, 2006 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype/ttunpat.h')

    def test_ics_freetype_include_freetype_config_ftconfig_h(self):
        expected = [
            u'Copyright 1996-2004, 2006-2008, 2010-2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-config/ftconfig.h')

    def test_ics_freetype_include_freetype_config_ftstdlib_h(self):
        expected = [
            u'Copyright 2002, 2003, 2004, 2005, 2006, 2007, 2009 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-config/ftstdlib.h')

    def test_ics_freetype_include_freetype_internal_autohint_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2007 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal/autohint.h')

    def test_ics_freetype_include_freetype_internal_ftcalc_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2004, 2005, 2006, 2008, 2009 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal/ftcalc.h')

    def test_ics_freetype_include_freetype_internal_ftdebug_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2004, 2006, 2007, 2008, 2009 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal/ftdebug.h')

    def test_ics_freetype_include_freetype_internal_ftdriver_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2006, 2008 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal/ftdriver.h')

    def test_ics_freetype_include_freetype_internal_ftgloadr_h(self):
        expected = [
            u'Copyright 2002, 2003, 2005, 2006 by David Turner, Robert Wilhelm, and Werner Lemberg',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal/ftgloadr.h')

    def test_ics_freetype_include_freetype_internal_ftmemory_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2004, 2005, 2006, 2007, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal/ftmemory.h')

    def test_ics_freetype_include_freetype_internal_ftobjs_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2004, 2005, 2006, 2008, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal/ftobjs.h')

    def test_ics_freetype_include_freetype_internal_ftpic_h(self):
        expected = [
            u'Copyright 2009 by Oran Agra and Mickey Gabel.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal/ftpic.h')

    def test_ics_freetype_include_freetype_internal_ftrfork_h_trail_name(self):
        expected = [
            u'Copyright 2004, 2006, 2007 by Masatake YAMATO and Redhat K.K.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal/ftrfork.h')

    def test_ics_freetype_include_freetype_internal_ftserv_h(self):
        expected = [
            u'Copyright 2003, 2004, 2005, 2006, 2007 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal/ftserv.h')

    def test_ics_freetype_include_freetype_internal_ftstream_h(self):
        expected = [
            u'Copyright 1996-2002, 2004-2006, 2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal/ftstream.h')

    def test_ics_freetype_include_freetype_internal_fttrace_h(self):
        expected = [
            u'Copyright 2002, 2004-2007, 2009, 2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal/fttrace.h')

    def test_ics_freetype_include_freetype_internal_ftvalid_h(self):
        expected = [
            u'Copyright 2004 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal/ftvalid.h')

    def test_ics_freetype_include_freetype_internal_internal_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2004 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal/internal.h')

    def test_ics_freetype_include_freetype_internal_pcftypes_h(self):
        expected = [
            u'Copyright (c) 2000, 2001, 2002 by Francesco Zappa Nardelli',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal/pcftypes.h')

    def test_ics_freetype_include_freetype_internal_pshints_h(self):
        expected = [
            u'Copyright 2001, 2002, 2003, 2005, 2006, 2007, 2009 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal/pshints.h')

    def test_ics_freetype_include_freetype_internal_sfnt_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2004, 2005, 2006 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal/sfnt.h')

    def test_ics_freetype_include_freetype_internal_tttypes_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2004, 2005, 2006, 2007, 2008 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal/tttypes.h')

    def test_ics_freetype_include_freetype_internal_services_svbdf_h(self):
        expected = [
            u'Copyright 2003 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal-services/svbdf.h')

    def test_ics_freetype_include_freetype_internal_services_svcid_h(self):
        expected = [
            u'Copyright 2007, 2009 by Derek Clegg, Michael Toftdal.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal-services/svcid.h')

    def test_ics_freetype_include_freetype_internal_services_svgxval_h(self):
        expected = [
            u'Copyright 2004, 2005 by Masatake YAMATO, Red Hat K.K., David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal-services/svgxval.h')

    def test_ics_freetype_include_freetype_internal_services_svkern_h(self):
        expected = [
            u'Copyright 2006 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal-services/svkern.h')

    def test_ics_freetype_include_freetype_internal_services_svmm_h(self):
        expected = [
            u'Copyright 2003, 2004 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal-services/svmm.h')

    def test_ics_freetype_include_freetype_internal_services_svpostnm_h(self):
        expected = [
            u'Copyright 2003, 2007 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal-services/svpostnm.h')

    def test_ics_freetype_include_freetype_internal_services_svpsinfo_h(self):
        expected = [
            u'Copyright 2003, 2004, 2009 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal-services/svpsinfo.h')

    def test_ics_freetype_include_freetype_internal_services_svttcmap_h_trail_name(self):
        expected = [
            u'Copyright 2003 by Masatake YAMATO, Redhat K.K.',
            u'Copyright 2003, 2008 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal-services/svttcmap.h')

    def test_ics_freetype_include_freetype_internal_services_svttglyf_h(self):
        expected = [
            u'Copyright 2007 by David Turner.',
        ]
        check_detection(expected, 'ics/freetype-include-freetype-internal-services/svttglyf.h')

    def test_ics_freetype_src_autofit_afangles_c(self):
        expected = [
            u'Copyright 2003-2006, 2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-autofit/afangles.c')

    def test_ics_freetype_src_autofit_afcjk_c(self):
        expected = [
            u'Copyright 2006-2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-autofit/afcjk.c')

    def test_ics_freetype_src_autofit_afcjk_h(self):
        expected = [
            u'Copyright 2006, 2007, 2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-autofit/afcjk.h')

    def test_ics_freetype_src_autofit_afdummy_c(self):
        expected = [
            u'Copyright 2003-2005, 2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-autofit/afdummy.c')

    def test_ics_freetype_src_autofit_aferrors_h(self):
        expected = [
            u'Copyright 2005 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-autofit/aferrors.h')

    def test_ics_freetype_src_autofit_afglobal_c(self):
        expected = [
            u'Copyright 2003-2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-autofit/afglobal.c')

    def test_ics_freetype_src_autofit_afglobal_h(self):
        expected = [
            u'Copyright 2003-2005, 2007, 2009, 2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-autofit/afglobal.h')

    def test_ics_freetype_src_autofit_afhints_c(self):
        expected = [
            u'Copyright 2003-2007, 2009-2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-autofit/afhints.c')

    def test_ics_freetype_src_autofit_afhints_h(self):
        expected = [
            u'Copyright 2003-2008, 2010-2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-autofit/afhints.h')

    def test_ics_freetype_src_autofit_afindic_c(self):
        expected = [
            u'Copyright 2007, 2011 by Rahul Bhalerao <rahul.bhalerao@redhat.com>',
        ]
        check_detection(expected, 'ics/freetype-src-autofit/afindic.c')

    def test_ics_freetype_src_autofit_afindic_h(self):
        expected = [
            u'Copyright 2007 by Rahul Bhalerao <rahul.bhalerao@redhat.com>',
        ]
        check_detection(expected, 'ics/freetype-src-autofit/afindic.h')

    def test_ics_freetype_src_autofit_aflatin_h(self):
        expected = [
            u'Copyright 2003-2007, 2009, 2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-autofit/aflatin.h')

    def test_ics_freetype_src_autofit_afloader_c(self):
        expected = [
            u'Copyright 2003-2009, 2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-autofit/afloader.c')

    def test_ics_freetype_src_autofit_afmodule_c(self):
        expected = [
            u'Copyright 2003-2006, 2009, 2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-autofit/afmodule.c')

    def test_ics_freetype_src_autofit_afmodule_h(self):
        expected = [
            u'Copyright 2003, 2004, 2005 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-autofit/afmodule.h')

    def test_ics_freetype_src_autofit_afpic_c(self):
        expected = [
            u'Copyright 2009, 2010, 2011 by Oran Agra and Mickey Gabel.',
        ]
        check_detection(expected, 'ics/freetype-src-autofit/afpic.c')

    def test_ics_freetype_src_autofit_afpic_h(self):
        expected = [
            u'Copyright 2009, 2011 by Oran Agra and Mickey Gabel.',
        ]
        check_detection(expected, 'ics/freetype-src-autofit/afpic.h')

    def test_ics_freetype_src_autofit_afwarp_h(self):
        expected = [
            u'Copyright 2006, 2007 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-autofit/afwarp.h')

    def test_ics_freetype_src_autofit_autofit_c(self):
        expected = [
            u'Copyright 2003-2007, 2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-autofit/autofit.c')

    def test_ics_freetype_src_base_ftadvanc_c(self):
        expected = [
            u'Copyright 2008, 2009 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftadvanc.c')

    def test_ics_freetype_src_base_ftapi_c(self):
        expected = [
            u'Copyright 2002 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftapi.c')

    def test_ics_freetype_src_base_ftbase_c(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2004, 2006, 2007, 2008, 2009 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftbase.c')

    def test_ics_freetype_src_base_ftbase_h(self):
        expected = [
            u'Copyright 2008, 2010 by David Turner, Robert Wilhelm, Werner Lemberg',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftbase.h')

    @expectedFailure
    def test_ics_freetype_src_base_ftbase_h_trail_name(self):
        expected = [
            u'Copyright 2008, 2010 by David Turner, Robert Wilhelm, Werner Lemberg and suzuki toshiya.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftbase.h')

    def test_ics_freetype_src_base_ftbbox_c(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2004, 2006, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftbbox.c')

    def test_ics_freetype_src_base_ftbitmap_c(self):
        expected = [
            u'Copyright 2004, 2005, 2006, 2007, 2008, 2009 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftbitmap.c')

    def test_ics_freetype_src_base_ftcalc_c(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2004, 2005, 2006, 2008 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftcalc.c')

    def test_ics_freetype_src_base_ftdbgmem_c(self):
        expected = [
            u'Copyright 2001, 2002, 2003, 2004, 2005, 2006, 2009 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftdbgmem.c')

    def test_ics_freetype_src_base_ftdebug_c(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2004, 2008 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftdebug.c')

    def test_ics_freetype_src_base_ftgloadr_c(self):
        expected = [
            u'Copyright 2002, 2003, 2004, 2005, 2006, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftgloadr.c')

    def test_ics_freetype_src_base_ftglyph_c(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2004, 2005, 2007, 2008, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftglyph.c')

    def test_ics_freetype_src_base_ftinit_c(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2005, 2007, 2009 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftinit.c')

    def test_ics_freetype_src_base_ftlcdfil_c(self):
        expected = [
            u'Copyright 2006, 2008, 2009, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftlcdfil.c')

    def test_ics_freetype_src_base_ftmm_c(self):
        expected = [
            u'Copyright 1996-2001, 2003, 2004, 2009 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftmm.c')

    def test_ics_freetype_src_base_ftobjs_c(self):
        expected = [
            u'Copyright 1996-2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftobjs.c')

    def test_ics_freetype_src_base_ftpatent_c(self):
        expected = [
            u'Copyright 2007, 2008, 2010 by David Turner.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftpatent.c')

    def test_ics_freetype_src_base_ftrfork_c_trail_name(self):
        expected = [
            u'Copyright 2004, 2005, 2006, 2007, 2008, 2009, 2010 by Masatake YAMATO and Redhat K.K.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftrfork.c')

    def test_ics_freetype_src_base_ftsnames_c(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2009 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftsnames.c')

    def test_ics_freetype_src_base_ftstream_c(self):
        expected = [
            u'Copyright 2000-2002, 2004-2006, 2008-2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftstream.c')

    def test_ics_freetype_src_base_ftstroke_c(self):
        expected = [
            u'Copyright 2002-2006, 2008-2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftstroke.c')

    def test_ics_freetype_src_base_ftsynth_c(self):
        expected = [
            u'Copyright 2000-2001, 2002, 2003, 2004, 2005, 2006, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftsynth.c')

    def test_ics_freetype_src_base_ftsystem_c(self):
        expected = [
            u'Copyright 1996-2002, 2006, 2008-2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftsystem.c')

    def test_ics_freetype_src_base_fttrigon_c(self):
        expected = [
            u'Copyright 2001, 2002, 2003, 2004, 2005 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-base/fttrigon.c')

    def test_ics_freetype_src_base_ftutil_c(self):
        expected = [
            u'Copyright 2002, 2004, 2005, 2006, 2007 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftutil.c')

    def test_ics_freetype_src_base_ftxf86_c(self):
        expected = [
            u'Copyright 2002, 2003, 2004 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-base/ftxf86.c')

    def test_ics_freetype_src_cff_cff_c(self):
        expected = [
            u'Copyright 1996-2001, 2002 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-cff/cff.c')

    def test_ics_freetype_src_cff_cffcmap_c(self):
        expected = [
            u'Copyright 2002, 2003, 2004, 2005, 2006, 2007, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-cff/cffcmap.c')

    def test_ics_freetype_src_cff_cffcmap_h(self):
        expected = [
            u'Copyright 2002, 2003, 2006 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-cff/cffcmap.h')

    def test_ics_freetype_src_cff_cfferrs_h(self):
        expected = [
            u'Copyright 2001 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-cff/cfferrs.h')

    def test_ics_freetype_src_cff_cffload_c(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-cff/cffload.c')

    def test_ics_freetype_src_cff_cffload_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2007, 2008, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-cff/cffload.h')

    def test_ics_freetype_src_cff_cffobjs_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2004, 2006, 2007, 2008 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-cff/cffobjs.h')

    def test_ics_freetype_src_cff_cffparse_c(self):
        expected = [
            u'Copyright 1996-2004, 2007-2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-cff/cffparse.c')

    def test_ics_freetype_src_cff_cffparse_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-cff/cffparse.h')

    def test_ics_freetype_src_cff_cffpic_c(self):
        expected = [
            u'Copyright 2009, 2010 by Oran Agra and Mickey Gabel.',
        ]
        check_detection(expected, 'ics/freetype-src-cff/cffpic.c')

    def test_ics_freetype_src_cff_cfftypes_h(self):
        expected = [
            u'Copyright 1996-2003, 2006-2008, 2010-2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-cff/cfftypes.h')

    def test_ics_freetype_src_psaux_afmparse_c(self):
        expected = [
            u'Copyright 2006, 2007, 2008, 2009, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-psaux/afmparse.c')

    def test_ics_freetype_src_psaux_psaux_c(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2006 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-psaux/psaux.c')

    def test_ics_freetype_src_psaux_psauxmod_c(self):
        expected = [
            u'Copyright 2000-2001, 2002, 2003, 2006 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-psaux/psauxmod.c')

    def test_ics_freetype_src_psaux_psauxmod_h(self):
        expected = [
            u'Copyright 2000-2001 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-psaux/psauxmod.h')

    def test_ics_freetype_src_psaux_psconv_c(self):
        expected = [
            u'Copyright 2006, 2008, 2009 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-psaux/psconv.c')

    def test_ics_freetype_src_psaux_t1cmap_c(self):
        expected = [
            u'Copyright 2002, 2003, 2006, 2007 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-psaux/t1cmap.c')

    def test_ics_freetype_src_psaux_t1decode_c(self):
        expected = [
            u'Copyright 2000-2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-psaux/t1decode.c')

    def test_ics_freetype_src_psaux_t1decode_h(self):
        expected = [
            u'Copyright 2000-2001, 2002, 2003 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-psaux/t1decode.h')

    def test_ics_freetype_src_pshinter_pshalgo_c(self):
        expected = [
            u'Copyright 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-pshinter/pshalgo.c')

    def test_ics_freetype_src_pshinter_pshalgo_h(self):
        expected = [
            u'Copyright 2001, 2002, 2003, 2008 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-pshinter/pshalgo.h')

    def test_ics_freetype_src_pshinter_pshglob_c(self):
        expected = [
            u'Copyright 2001, 2002, 2003, 2004, 2006, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-pshinter/pshglob.c')

    def test_ics_freetype_src_pshinter_pshglob_h(self):
        expected = [
            u'Copyright 2001, 2002, 2003 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-pshinter/pshglob.h')

    def test_ics_freetype_src_pshinter_pshinter_c(self):
        expected = [
            u'Copyright 2001, 2003 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-pshinter/pshinter.c')

    def test_ics_freetype_src_pshinter_pshmod_c(self):
        expected = [
            u'Copyright 2001, 2002, 2007 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-pshinter/pshmod.c')

    def test_ics_freetype_src_pshinter_pshrec_c(self):
        expected = [
            u'Copyright 2001, 2002, 2003, 2004, 2007, 2009 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-pshinter/pshrec.c')

    def test_ics_freetype_src_pshinter_pshrec_h(self):
        expected = [
            u'Copyright 2001, 2002, 2003, 2006, 2008 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-pshinter/pshrec.h')

    def test_ics_freetype_src_psnames_psmodule_c(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2005, 2006, 2007, 2008 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-psnames/psmodule.c')

    def test_ics_freetype_src_psnames_psmodule_h(self):
        expected = [
            u'Copyright 1996-2001 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-psnames/psmodule.h')

    def test_ics_freetype_src_psnames_pstables_h(self):
        expected = [
            u'Copyright 2005, 2008 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-psnames/pstables.h')

    def test_ics_freetype_src_raster_ftmisc_h(self):
        expected = [
            u'Copyright 2005, 2009, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-raster/ftmisc.h')

    def test_ics_freetype_src_raster_ftraster_c(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2005, 2007, 2008, 2009, 2010, 2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-raster/ftraster.c')

    def test_ics_freetype_src_raster_ftrend1_c(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2005, 2006 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-raster/ftrend1.c')

    def test_ics_freetype_src_sfnt_sfdriver_c(self):
        expected = [
            u'Copyright 1996-2007, 2009-2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-sfnt/sfdriver.c')

    def test_ics_freetype_src_sfnt_sferrors_h(self):
        expected = [
            u'Copyright 2001, 2004 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-sfnt/sferrors.h')

    def test_ics_freetype_src_sfnt_sfobjs_c(self):
        expected = [
            u'Copyright 1996-2008, 2010-2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-sfnt/sfobjs.c')

    def test_ics_freetype_src_sfnt_ttbdf_c(self):
        expected = [
            u'Copyright 2005, 2006, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-sfnt/ttbdf.c')

    def test_ics_freetype_src_sfnt_ttcmap_c(self):
        expected = [
            u'Copyright 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-sfnt/ttcmap.c')

    def test_ics_freetype_src_sfnt_ttcmap_h(self):
        expected = [
            u'Copyright 2002, 2003, 2004, 2005 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-sfnt/ttcmap.h')

    def test_ics_freetype_src_sfnt_ttkern_c(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2004, 2005, 2006, 2007, 2009, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-sfnt/ttkern.c')

    def test_ics_freetype_src_sfnt_ttkern_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2005, 2007 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-sfnt/ttkern.h')

    def test_ics_freetype_src_sfnt_ttload_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2005, 2006 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-sfnt/ttload.h')

    def test_ics_freetype_src_sfnt_ttmtx_c(self):
        expected = [
            u'Copyright 2006-2009, 2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-sfnt/ttmtx.c')

    def test_ics_freetype_src_sfnt_ttpost_c(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2006, 2007, 2008, 2009, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-sfnt/ttpost.c')

    def test_ics_freetype_src_sfnt_ttsbit_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-sfnt/ttsbit.h')

    def test_ics_freetype_src_sfnt_ttsbit0_c(self):
        expected = [
            u'Copyright 2005, 2006, 2007, 2008, 2009 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-sfnt/ttsbit0.c')

    def test_ics_freetype_src_smooth_ftgrays_c(self):
        expected = [
            u'Copyright 2000-2003, 2005-2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-smooth/ftgrays.c')

    def test_ics_freetype_src_smooth_ftsmooth_c(self):
        expected = [
            u'Copyright 2000-2006, 2009-2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-smooth/ftsmooth.c')

    def test_ics_freetype_src_truetype_truetype_c(self):
        expected = [
            u'Copyright 1996-2001, 2004, 2006 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-truetype/truetype.c')

    def test_ics_freetype_src_truetype_ttgload_c(self):
        expected = [
            u'Copyright 1996-2011 David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-truetype/ttgload.c')

    def test_ics_freetype_src_truetype_ttgload_h(self):
        expected = [
            u'Copyright 1996-2006, 2008, 2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-truetype/ttgload.h')

    def test_ics_freetype_src_truetype_ttinterp_h(self):
        expected = [
            u'Copyright 1996-2001, 2002, 2003, 2004, 2005, 2006, 2007, 2010 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-truetype/ttinterp.h')

    def test_ics_freetype_src_truetype_ttobjs_h(self):
        expected = [
            u'Copyright 1996-2009, 2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-truetype/ttobjs.h')

    def test_ics_freetype_src_truetype_ttpload_c(self):
        expected = [
            u'Copyright 1996-2002, 2004-2011 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, 'ics/freetype-src-truetype/ttpload.c')

    def test_ics_fsck_msdos_boot_c(self):
        expected = [
            u'Copyright (c) 1995, 1997 Wolfgang Solfrank',
            u'Copyright (c) 1995 Martin Husemann',
        ]
        check_detection(expected, 'ics/fsck_msdos/boot.c')

    def test_ics_fsck_msdos_check_c(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997 Wolfgang Solfrank',
            u'Copyright (c) 1995 Martin Husemann',
        ]
        check_detection(expected, 'ics/fsck_msdos/check.c')

    def test_ics_fsck_msdos_main_c(self):
        expected = [
            u'Copyright (c) 1995 Wolfgang Solfrank',
            u'Copyright (c) 1995 Martin Husemann',
        ]
        check_detection(expected, 'ics/fsck_msdos/main.c')

    def test_ics_fsck_msdos_notice(self):
        expected = [
            u'Copyright (c) 1995, 1997 Wolfgang Solfrank',
            u'Copyright (c) 1995 Martin Husemann',
            u'Copyright (c) 1995, 1996, 1997 Wolfgang Solfrank',
            u'Copyright (c) 1995 Martin Husemann',
            u'Copyright (c) 1995 Wolfgang Solfrank',
            u'Copyright (c) 1995 Martin Husemann',
        ]
        check_detection(expected, 'ics/fsck_msdos/NOTICE')

    def test_ics_genext2fs_aclocal_m4(self):
        expected = [
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2002, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1997, 2000, 2001, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2002, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1997, 1999, 2000, 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2002, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 2000, 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/genext2fs/aclocal.m4')

    def test_ics_genext2fs_configure(self):
        expected = [
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/genext2fs/configure')

    def test_ics_genext2fs_genext2fs_c_trail_name_trail_name_trail_name_trail_name(self):
        expected = [
            u'Copyright (c) 2000 Xavier Bestel <xavier.bestel@free.fr>',
            u'Copyright (c) 1999,2000 by Lineo, inc. and John Beppu',
            u'Copyright (c) 1999,2000,2001 by John Beppu <beppu@codepoet.org>',
            u'Copyright (c) 2002 Edward Betts <edward@debian.org>',
            u'Copyright (c) 2002 Ixia communications',
            u'Copyright (c) 2002 Ixia communications',
            u'Copyright (c) 2002 Ixia communications',
        ]
        check_detection(expected, 'ics/genext2fs/genext2fs.c')

    def test_ics_genext2fs_m4_ac_func_scanf_can_malloc_m4(self):
        expected = [
            u'(c) Finn Thain 2006',
        ]
        check_detection(expected, 'ics/genext2fs-m4/ac_func_scanf_can_malloc.m4')

    def test_ics_giflib_gif_lib_private_h(self):
        expected = [
            u'(c) Copyright 1997 Eric S. Raymond',
            u'(c) Copyright 1997 Eric S. Raymond',
        ]
        check_detection(expected, 'ics/giflib/gif_lib_private.h')

    def test_ics_giflib_notice(self):
        expected = [
            u'Copyright (c) 1997 Eric S. Raymond',
        ]
        check_detection(expected, 'ics/giflib/NOTICE')

    def test_ics_google_diff_match_patch_name_fraser_neil_plaintext_diff_match_patch_java(self):
        expected = [
            u'Copyright 2006 Google Inc.',
        ]
        check_detection(expected, 'ics/google-diff-match-patch-name-fraser-neil-plaintext/diff_match_patch.java')

    def test_ics_gtest_test_gtest_filter_unittest_py(self):
        expected = [
            u'Copyright 2005, Google Inc.',
        ]
        check_detection(expected, 'ics/gtest-test/gtest_filter_unittest.py')

    def test_ics_gtest_test_gtest_nc_test_py(self):
        expected = [
            u'Copyright 2007, Google Inc.',
        ]
        check_detection(expected, 'ics/gtest-test/gtest_nc_test.py')

    def test_ics_guava_guava_ipr(self):
        expected = [u'(c) &amp 36 today.year Google Inc.']
        check_detection(expected, 'ics/guava/guava.ipr')

    @expectedFailure
    def test_ics_guava_guava_ipr_markup(self):
        expected = [
            u'Copyright (c) Google Inc.',
        ]
        check_detection(expected, 'ics/guava/guava.ipr')

    def test_ics_guava_src_com_google_common_annotations_gwtcompatible_java(self):
        expected = [
            u'Copyright (c) 2009 Google Inc.',
        ]
        check_detection(expected, 'ics/guava-src-com-google-common-annotations/GwtCompatible.java')

    def test_ics_guava_src_com_google_common_annotations_visiblefortesting_java(self):
        expected = [
            u'Copyright (c) 2006 Google Inc.',
        ]
        check_detection(expected, 'ics/guava-src-com-google-common-annotations/VisibleForTesting.java')

    def test_ics_guava_src_com_google_common_base_charmatcher_java(self):
        expected = [
            u'Copyright (c) 2008 Google Inc.',
        ]
        check_detection(expected, 'ics/guava-src-com-google-common-base/CharMatcher.java')

    def test_ics_guava_src_com_google_common_base_charsets_java(self):
        expected = [
            u'Copyright (c) 2007 Google Inc.',
        ]
        check_detection(expected, 'ics/guava-src-com-google-common-base/Charsets.java')

    def test_ics_guava_src_com_google_common_io_nulloutputstream_java(self):
        expected = [
            u'Copyright (c) 2004 Google Inc.',
        ]
        check_detection(expected, 'ics/guava-src-com-google-common-io/NullOutputStream.java')

    def test_ics_harfbuzz_contrib_harfbuzz_unicode_icu_c(self):
        expected = [
            u'Copyright 2010, The Android Open Source Project',
            u'Copyright 2010, Google Inc.',
        ]
        check_detection(expected, 'ics/harfbuzz-contrib/harfbuzz-unicode-icu.c')

    def test_ics_harfbuzz_contrib_tables_bidimirroring_txt(self):
        expected = [
            u'Copyright (c) 1991-2008 Unicode, Inc.',
        ]
        check_detection(expected, 'ics/harfbuzz-contrib-tables/BidiMirroring.txt')

    def test_ics_harfbuzz_src_harfbuzz_arabic_c(self):
        expected = [
            u'Copyright (c) 2008 Nokia Corporation and/or its subsidiary(-ies)',
        ]
        check_detection(expected, 'ics/harfbuzz-src/harfbuzz-arabic.c')

    def test_ics_harfbuzz_src_harfbuzz_buffer_private_h(self):
        expected = [
            u'Copyright (c) 1998-2004 David Turner and Werner Lemberg',
            u'Copyright (c) 2004,2007 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/harfbuzz-src/harfbuzz-buffer-private.h')

    def test_ics_harfbuzz_src_harfbuzz_dump_c(self):
        expected = [
            u'Copyright (c) 2000, 2007 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/harfbuzz-src/harfbuzz-dump.c')

    def test_ics_harfbuzz_src_harfbuzz_external_h(self):
        expected = [
            u'Copyright (c) 2008 Nokia Corporation and/or its subsidiary(-ies)',
        ]
        check_detection(expected, 'ics/harfbuzz-src/harfbuzz-external.h')

    def test_ics_harfbuzz_src_harfbuzz_gdef_private_h(self):
        expected = [
            u'Copyright (c) 1998-2004 David Turner and Werner Lemberg',
            u'Copyright (c) 2006 Behdad Esfahbod',
        ]
        check_detection(expected, 'ics/harfbuzz-src/harfbuzz-gdef-private.h')

    def test_ics_harfbuzz_src_harfbuzz_global_h(self):
        expected = [
            u'Copyright (c) 2008 Nokia Corporation and/or its subsidiary(-ies)',
            u'Copyright (c) 2007 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/harfbuzz-src/harfbuzz-global.h')

    def test_ics_harfbuzz_src_harfbuzz_gpos_c(self):
        expected = [
            u'Copyright (c) 1998-2004 David Turner and Werner Lemberg',
            u'Copyright (c) 2006 Behdad Esfahbod',
            u'Copyright (c) 2007 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/harfbuzz-src/harfbuzz-gpos.c')

    def test_ics_harfbuzz_src_harfbuzz_greek_c(self):
        expected = [
            u'Copyright (c) 2010 Nokia Corporation and/or its subsidiary(-ies)',
        ]
        check_detection(expected, 'ics/harfbuzz-src/harfbuzz-greek.c')

    def test_ics_harfbuzz_src_harfbuzz_impl_c(self):
        expected = [
            u'Copyright (c) 1998-2004 David Turner and Werner Lemberg',
            u'Copyright (c) 2008 Nokia Corporation and/or its subsidiary(-ies)',
            u'Copyright (c) 2007 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/harfbuzz-src/harfbuzz-impl.c')

    def test_ics_harfbuzz_src_harfbuzz_shape_h(self):
        expected = [
            u'Copyright (c) 2006 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/harfbuzz-src/harfbuzz-shape.h')

    def test_ics_harfbuzz_src_harfbuzz_stream_c(self):
        expected = [
            u'Copyright (c) 2005 David Turner',
            u'Copyright (c) 2008 Nokia Corporation and/or its subsidiary(-ies)',
            u'Copyright (c) 2007 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/harfbuzz-src/harfbuzz-stream.c')

    def test_ics_harfbuzz_src_harfbuzz_stream_h(self):
        expected = [
            u'Copyright (c) 2005 David Turner',
            u'Copyright (c) 2008 Nokia Corporation and/or its subsidiary(-ies)',
        ]
        check_detection(expected, 'ics/harfbuzz-src/harfbuzz-stream.h')

    def test_ics_hyphenation_hnjalloc_c(self):
        expected = [
            u'Copyright (c) 1998 Raph Levien',
            u'(c) 2001 ALTLinux, Moscow',
        ]
        check_detection(expected, 'ics/hyphenation/hnjalloc.c')

    def test_ics_hyphenation_hnjalloc_h(self):
        expected = [
            u'Copyright (c) 1998 Raph Levien',
        ]
        check_detection(expected, 'ics/hyphenation/hnjalloc.h')

    def test_ics_hyphenation_hyphen_c(self):
        expected = [
            u'Copyright (c) 1998 Raph Levien',
            u'(c) 2001 ALTLinux, Moscow',
            u'(c) 2001 Peter Novodvorsky (nidd@cs.msu.su)',
            u'(c) 2006, 2007, 2008 Laszlo Nemeth',
        ]
        check_detection(expected, 'ics/hyphenation/hyphen.c')

    def test_ics_hyphenation_hyphen_h(self):
        expected = [
            u'(c) 1998 Raph Levien',
            u'(c) 2001 ALTLinux, Moscow',
            u'(c) 2006, 2007, 2008 Laszlo Nemeth',
            u'Copyright (c) 1998 Raph Levien',
        ]
        check_detection(expected, 'ics/hyphenation/hyphen.h')

    def test_ics_hyphenation_readme(self):
        expected = [
            u'(c) 1998 Raph Levien',
            u'(c) 2001 ALTLinux, Moscow',
            u'(c) 2006, 2007, 2008 Laszlo Nemeth',
        ]
        check_detection(expected, 'ics/hyphenation/README')

    def test_ics_iproute2_readme_lnstat(self):
        expected = [
            u'(c) 2004 Harald Welte laforge@gnumonks.org',
        ]
        check_detection(expected, 'ics/iproute2/README.lnstat')

    def test_ics_iproute2_include_linux_if_addrlabel_h(self):
        expected = [
            u'Copyright (c) 2007 USAGI/WIDE Project',
        ]
        check_detection(expected, 'ics/iproute2-include-linux/if_addrlabel.h')

    def test_ics_iproute2_include_linux_if_arp_h(self):
        expected = [
            u'(c) UCB 1986-1988',
        ]
        check_detection(expected, 'ics/iproute2-include-linux/if_arp.h')

    def test_ics_iproute2_include_linux_if_tun_h(self):
        expected = [
            u'Copyright (c) 1999-2000 Maxim Krasnyansky <max_mk@yahoo.com>',
        ]
        check_detection(expected, 'ics/iproute2-include-linux/if_tun.h')

    def test_ics_iproute2_include_linux_netfilter_ipv4_h(self):
        expected = [
            u'(c) 1998 Rusty Russell',
        ]
        check_detection(expected, 'ics/iproute2-include-linux/netfilter_ipv4.h')

    def test_ics_iproute2_include_linux_can_netlink_h(self):
        expected = [
            u'Copyright (c) 2009 Wolfgang Grandegger <wg@grandegger.com>',
        ]
        check_detection(expected, 'ics/iproute2-include-linux-can/netlink.h')

    def test_ics_iproute2_include_linux_tc_act_tc_skbedit_h(self):
        expected = [
            u'Copyright (c) 2008, Intel Corporation.',
        ]
        check_detection(expected, 'ics/iproute2-include-linux-tc_act/tc_skbedit.h')

    def test_ics_iproute2_include_netinet_icmp6_h(self):
        expected = [
            u'Copyright (c) 1991-1997,2000,2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/iproute2-include-netinet/icmp6.h')

    def test_ics_iproute2_ip_ip6tunnel_c(self):
        expected = [
            u'Copyright (c) 2006 USAGI/WIDE Project',
        ]
        check_detection(expected, 'ics/iproute2-ip/ip6tunnel.c')

    def test_ics_iproute2_ip_ipaddrlabel_c(self):
        expected = [
            u'Copyright (c) 2007 USAGI/WIDE Project',
        ]
        check_detection(expected, 'ics/iproute2-ip/ipaddrlabel.c')

    def test_ics_iproute2_ip_ipprefix_c(self):
        expected = [
            u'Copyright (c) 2005 USAGI/WIDE Project',
        ]
        check_detection(expected, 'ics/iproute2-ip/ipprefix.c')

    def test_ics_iproute2_ip_ipxfrm_c(self):
        expected = [
            u'Copyright (c) 2004 USAGI/WIDE Project',
        ]
        check_detection(expected, 'ics/iproute2-ip/ipxfrm.c')

    def test_ics_iproute2_misc_lnstat_c(self):
        expected = [
            u'Copyright (c) 2004 by Harald Welte <laforge@gnumonks.org>',
            u'Copyright 2001 by Robert Olsson <robert.olsson@its.uu.se> Uppsala University, Sweden',
            u'Copyright (c) 2004 by Harald Welte <laforge@gnumonks.org>',
        ]
        check_detection(expected, 'ics/iproute2-misc/lnstat.c')

    def test_ics_iproute2_misc_lnstat_util_c(self):
        expected = [
            u'Copyright (c) 2004 by Harald Welte <laforge@gnumonks.org>',
            u'Copyright 2001 by Robert Olsson <robert.olsson@its.uu.se> Uppsala University, Sweden',
        ]
        check_detection(expected, 'ics/iproute2-misc/lnstat_util.c')

    def test_ics_ipsec_tools_notice_extra_contributed(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997, and 1998 WIDE Project.',
            u'Copyright (c) 2004 Emmanuel Dreyfus',
            u'Copyright (c) 2004-2006 Emmanuel Dreyfus',
            u'Copyright (c) 2000 WIDE Project.',
            u'Copyright (c) 2004-2005 Emmanuel Dreyfus',
            u'Copyright (c) 2000, 2001 WIDE Project.',
            u'Copyright (c) 2004 SuSE Linux AG, Nuernberg, Germany.',
            u'Copyright (c) 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002 and 2003 WIDE Project.',
            u'Copyright 2000 Wasabi Systems, Inc.',
            u'Copyright (c) 2005 International Business Machines Corporation',
            u'Copyright (c) 2005 by Trusted Computer Solutions, Inc.',
            u'Copyright 2000 Aaron D. Gifford.',
            u'Copyright (c) 1995, 1996, 1997, 1998, and 1999 WIDE Project.',
            u'Copyright (c) 1995, 1996, 1997, and 1998 WIDE Project.',
            u'Copyright (c) 1991, 1993 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/ipsec-tools/NOTICE')

    def test_ics_ipsec_tools_src_include_glibc_notice(self):
        expected = [
            u'Copyright (c) 1991, 1993 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-include-glibc/NOTICE')

    def test_ics_ipsec_tools_src_libipsec_ipsec_dump_policy_c(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997, 1998, and 1999 WIDE Project.',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-libipsec/ipsec_dump_policy.c')

    def test_ics_ipsec_tools_src_libipsec_ipsec_set_policy_3(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997, 1998, and 1999 WIDE Project.',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-libipsec/ipsec_set_policy.3')

    def test_ics_ipsec_tools_src_libipsec_key_debug_c(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997, and 1998 WIDE Project.',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-libipsec/key_debug.c')

    def test_ics_ipsec_tools_src_libipsec_notice(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997, 1998, and 1999 WIDE Project.',
            u'Copyright (c) 1995, 1996, 1997, and 1998 WIDE Project.',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-libipsec/NOTICE')

    def test_ics_ipsec_tools_src_libipsec_policy_parse_y(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997, 1998, and 1999 WIDE Project.',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-libipsec/policy_parse.y')

    def test_ics_ipsec_tools_src_racoon_cfparse_y(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002 and 2003 WIDE Project.',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-racoon/cfparse.y')

    def test_ics_ipsec_tools_src_racoon_dump_h(self):
        expected = [
            u'Copyright (c) 2000 WIDE Project.',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-racoon/dump.h')

    def test_ics_ipsec_tools_src_racoon_evt_c(self):
        expected = [
            u'Copyright (c) 2004 Emmanuel Dreyfus',
            u'Copyright (c) 2008 Timo Teras',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-racoon/evt.c')

    def test_ics_ipsec_tools_src_racoon_gcmalloc_h(self):
        expected = [
            u'Copyright (c) 2000, 2001 WIDE Project.',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-racoon/gcmalloc.h')

    def test_ics_ipsec_tools_src_racoon_genlist_c_extra_contributed(self):
        expected = [
            u'Copyright (c) 2004 SuSE Linux AG, Nuernberg, Germany.',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-racoon/genlist.c')

    def test_ics_ipsec_tools_src_racoon_grabmyaddr_c(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997, and 1998 WIDE Project.',
            u'Copyright (c) 2008 Timo Teras <timo.teras@iki.fi>',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-racoon/grabmyaddr.c')

    def test_ics_ipsec_tools_src_racoon_gssapi_c(self):
        expected = [
            u'Copyright 2000 Wasabi Systems, Inc.',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-racoon/gssapi.c')

    def test_ics_ipsec_tools_src_racoon_handler_h(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997, and 1998 WIDE Project.',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-racoon/handler.h')

    def test_ics_ipsec_tools_src_racoon_isakmp_cfg_c(self):
        expected = [
            u'Copyright (c) 2004-2006 Emmanuel Dreyfus',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-racoon/isakmp_cfg.c')

    def test_ics_ipsec_tools_src_racoon_isakmp_cfg_h(self):
        expected = [
            u'Copyright (c) 2004 Emmanuel Dreyfus',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-racoon/isakmp_cfg.h')

    def test_ics_ipsec_tools_src_racoon_isakmp_xauth_c(self):
        expected = [
            u'Copyright (c) 2004-2005 Emmanuel Dreyfus',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-racoon/isakmp_xauth.c')

    def test_ics_ipsec_tools_src_racoon_notice_extra_contributed(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997, and 1998 WIDE Project.',
            u'Copyright (c) 2004 Emmanuel Dreyfus',
            u'Copyright (c) 2004-2006 Emmanuel Dreyfus',
            u'Copyright (c) 2000 WIDE Project.',
            u'Copyright (c) 2004-2005 Emmanuel Dreyfus',
            u'Copyright (c) 2000, 2001 WIDE Project.',
            u'Copyright (c) 2004 SuSE Linux AG, Nuernberg, Germany.',
            u'Copyright (c) 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002 and 2003 WIDE Project.',
            u'Copyright 2000 Wasabi Systems, Inc.',
            u'Copyright (c) 2005 International Business Machines Corporation',
            u'Copyright (c) 2005 by Trusted Computer Solutions, Inc.',
            u'Copyright 2000 Aaron D. Gifford.',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-racoon/NOTICE')

    def test_ics_ipsec_tools_src_racoon_plainrsa_gen_8(self):
        expected = [
            u'Copyright (c) 2004 SuSE Linux AG, Nuernberg, Germany.',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-racoon/plainrsa-gen.8')

    def test_ics_ipsec_tools_src_racoon_racoon_8(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997, and 1998 WIDE Project.',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-racoon/racoon.8')

    def test_ics_ipsec_tools_src_racoon_racoonctl_8(self):
        expected = [
            u'Copyright (c) 2004 Emmanuel Dreyfus',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-racoon/racoonctl.8')

    def test_ics_ipsec_tools_src_racoon_racoonctl_c(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997, and 1998 WIDE Project.',
            u'Copyright (c) 2008 Timo Teras.',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-racoon/racoonctl.c')

    def test_ics_ipsec_tools_src_racoon_security_c(self):
        expected = [
            u'Copyright (c) 2005 International Business Machines Corporation',
            u'Copyright (c) 2005 by Trusted Computer Solutions, Inc.',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-racoon/security.c')

    def test_ics_ipsec_tools_src_racoon_missing_crypto_sha2_sha2_c(self):
        expected = [
            u'Copyright 2000 Aaron D. Gifford.',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-racoon-missing-crypto-sha2/sha2.c')

    def test_ics_ipsec_tools_src_racoon_missing_crypto_sha2_sha2_h(self):
        expected = [
            u'Copyright 2000 Aaron D. Gifford.',
        ]
        check_detection(expected, 'ics/ipsec-tools-src-racoon-missing-crypto-sha2/sha2.h')

    def test_ics_iptables_extensions_libip6t_reject_c(self):
        expected = [
            u'(c) 2000 Jozsef Kadlecsik <kadlec@blackhole.kfki.hu>',
        ]
        check_detection(expected, 'ics/iptables-extensions/libip6t_REJECT.c')

    def test_ics_iptables_extensions_libipt_clusterip_c(self):
        expected = [
            u'(c) 2003 by Harald Welte <laforge@gnumonks.org>',
        ]
        check_detection(expected, 'ics/iptables-extensions/libipt_CLUSTERIP.c')

    def test_ics_iptables_extensions_libipt_ecn_c(self):
        expected = [
            u'(c) 2002 by Harald Welte <laforge@gnumonks.org>',
        ]
        check_detection(expected, 'ics/iptables-extensions/libipt_ECN.c')

    def test_ics_iptables_extensions_libipt_ttl_c(self):
        expected = [
            u'(c) 2000 by Harald Welte <laforge@gnumonks.org>',
        ]
        check_detection(expected, 'ics/iptables-extensions/libipt_TTL.c')

    def test_ics_iptables_extensions_libxt_audit_c(self):
        expected = [
            u'(c) 2010-2011, Thomas Graf <tgraf@redhat.com>',
            u'(c) 2010-2011, Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/iptables-extensions/libxt_AUDIT.c')

    def test_ics_iptables_extensions_libxt_checksum_c(self):
        expected = [
            u'(c) 2002 by Harald Welte <laforge@gnumonks.org>',
            u'(c) 2010 by Red Hat, Inc',
        ]
        check_detection(expected, 'ics/iptables-extensions/libxt_CHECKSUM.c')

    def test_ics_iptables_extensions_libxt_cluster_c(self):
        expected = [
            u'(c) 2009 by Pablo Neira Ayuso <pablo@netfilter.org>',
        ]
        check_detection(expected, 'ics/iptables-extensions/libxt_cluster.c')

    def test_ics_iptables_extensions_libxt_connmark_c(self):
        expected = [
            u'(c) 2002,2004 MARA Systems AB',
        ]
        check_detection(expected, 'ics/iptables-extensions/libxt_connmark.c')

    def test_ics_iptables_extensions_libxt_connsecmark_c(self):
        expected = [
            u'Copyright (c) 2006 Red Hat, Inc., James Morris <jmorris@redhat.com>',
        ]
        check_detection(expected, 'ics/iptables-extensions/libxt_CONNSECMARK.c')

    def test_ics_iptables_extensions_libxt_conntrack_c(self):
        expected = [
            u'(c) 2001 Marc Boucher (marc@mbsi.ca).',
            u'Copyright (c) CC Computer Consultants GmbH, 2007 - 2008 Jan Engelhardt <jengelh@computergmbh.de>',
        ]
        check_detection(expected, 'ics/iptables-extensions/libxt_conntrack.c')

    def test_ics_iptables_extensions_libxt_dccp_c(self):
        expected = [
            u'(c) 2005 by Harald Welte <laforge@netfilter.org>',
        ]
        check_detection(expected, 'ics/iptables-extensions/libxt_dccp.c')

    def test_ics_iptables_extensions_libxt_devgroup_c(self):
        expected = [
            u'Copyright (c) 2011 Patrick McHardy <kaber@trash.net>',
        ]
        check_detection(expected, 'ics/iptables-extensions/libxt_devgroup.c')

    def test_ics_iptables_extensions_libxt_hashlimit_c(self):
        expected = [
            u'(c) 2003-2004 by Harald Welte <laforge@netfilter.org>',
        ]
        check_detection(expected, 'ics/iptables-extensions/libxt_hashlimit.c')

    def test_ics_iptables_extensions_libxt_idletimer_c(self):
        expected = [
            u'Copyright (c) 2010 Nokia Corporation.',
        ]
        check_detection(expected, 'ics/iptables-extensions/libxt_IDLETIMER.c')

    def test_ics_iptables_extensions_libxt_led_c(self):
        expected = [
            u'(c) 2008 Adam Nielsen <a.nielsen@shikadi.net>',
        ]
        check_detection(expected, 'ics/iptables-extensions/libxt_LED.c')

    def test_ics_iptables_extensions_libxt_osf_c(self):
        expected = [
            u'Copyright (c) 2003+ Evgeniy Polyakov <zbr@ioremap.net>',
        ]
        check_detection(expected, 'ics/iptables-extensions/libxt_osf.c')

    def test_ics_iptables_extensions_libxt_owner_c(self):
        expected = [
            u'Copyright (c) CC Computer Consultants GmbH, 2007 - 2008 Jan Engelhardt <jengelh@computergmbh.de>'
        ]
        check_detection(expected, 'ics/iptables-extensions/libxt_owner.c')

    def test_ics_iptables_extensions_libxt_set_c(self):
        expected = [
            u'Copyright (c) 2000-2002 Joakim Axelsson <gozem@linux.nu> Patrick Schaaf <bof@bof.de> Martin Josefsson <gandalf@wlug.westbo.se>',
            u'Copyright (c) 2003-2010 Jozsef Kadlecsik <kadlec@blackhole.kfki.hu>',
        ]
        check_detection(expected, 'ics/iptables-extensions/libxt_SET.c')

    def test_ics_iptables_extensions_libxt_socket_c(self):
        expected = [
            u'Copyright (c) 2007 BalaBit IT Ltd.',
        ]
        check_detection(expected, 'ics/iptables-extensions/libxt_socket.c')

    def test_ics_iptables_extensions_libxt_string_c(self):
        expected = [
            u'Copyright (c) 2000 Emmanuel Roger <winfield@freegates.be>',
        ]
        check_detection(expected, 'ics/iptables-extensions/libxt_string.c')

    def test_ics_iptables_extensions_libxt_tcpoptstrip_c(self):
        expected = [
            u'Copyright (c) 2007 Sven Schnelle <svens@bitebene.org>',
            u'Copyright (c) CC Computer Consultants GmbH, 2007 Jan Engelhardt <jengelh@computergmbh.de>',
        ]
        check_detection(expected, 'ics/iptables-extensions/libxt_TCPOPTSTRIP.c')

    def test_ics_iptables_extensions_libxt_tee_c(self):
        expected = [
            u'Copyright (c) Sebastian Claen , 2007 Jan Engelhardt',
        ]
        check_detection(expected, 'ics/iptables-extensions/libxt_TEE.c')

    def test_ics_iptables_extensions_libxt_time_c(self):
        expected = [
            u'Copyright (c) CC Computer Consultants GmbH, 2007',
        ]
        check_detection(expected, 'ics/iptables-extensions/libxt_time.c')

    def test_ics_iptables_extensions_libxt_tproxy_c(self):
        expected = [
            u'Copyright (c) 2002-2008 BalaBit IT Ltd.',
        ]
        check_detection(expected, 'ics/iptables-extensions/libxt_TPROXY.c')

    def test_ics_iptables_extensions_libxt_u32_c(self):
        expected = [
            u'(c) 2002 by Don Cohen <don-netf@isis.cs3-inc.com>',
            u'Copyright (c) CC Computer Consultants GmbH, 2007',
        ]
        check_detection(expected, 'ics/iptables-extensions/libxt_u32.c')

    def test_ics_iptables_include_libipq_libipq_h(self):
        expected = [
            u'Copyright (c) 2000-2001 Netfilter Core Team',
        ]
        check_detection(expected, 'ics/iptables-include-libipq/libipq.h')

    def test_ics_iptables_include_linux_netfilter_ipv6_h(self):
        expected = [
            u'(c) 1998 Rusty Russell',
            u'(c) 1999 David Jeffery',
        ]
        check_detection(expected, 'ics/iptables-include-linux/netfilter_ipv6.h')

    def test_ics_iptables_include_linux_netfilter_xt_audit_h(self):
        expected = [
            u'(c) 2010-2011 Thomas Graf <tgraf@redhat.com>',
            u'(c) 2010-2011 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/iptables-include-linux-netfilter/xt_AUDIT.h')

    def test_ics_iptables_include_linux_netfilter_xt_checksum_h(self):
        expected = [
            u'(c) 2002 by Harald Welte <laforge@gnumonks.org>',
            u'(c) 2010 Red Hat Inc',
        ]
        check_detection(expected, 'ics/iptables-include-linux-netfilter/xt_CHECKSUM.h')

    def test_ics_iptables_include_linux_netfilter_xt_conntrack_h(self):
        expected = [
            u'(c) 2001 Marc Boucher (marc@mbsi.ca).',
        ]
        check_detection(expected, 'ics/iptables-include-linux-netfilter/xt_conntrack.h')

    def test_ics_iptables_include_linux_netfilter_xt_dscp_h(self):
        expected = [
            u'(c) 2002 Harald Welte <laforge@gnumonks.org>',
        ]
        check_detection(expected, 'ics/iptables-include-linux-netfilter/xt_DSCP.h')

    def test_ics_iptables_include_linux_netfilter_xt_idletimer_h(self):
        expected = [
            u'Copyright (c) 2004, 2010 Nokia Corporation',
        ]
        check_detection(expected, 'ics/iptables-include-linux-netfilter/xt_IDLETIMER.h')

    def test_ics_iptables_include_linux_netfilter_xt_nfqueue_h(self):
        expected = [
            u'(c) 2005 Harald Welte <laforge@netfilter.org>',
        ]
        check_detection(expected, 'ics/iptables-include-linux-netfilter/xt_NFQUEUE.h')

    def test_ics_iptables_include_linux_netfilter_xt_osf_h(self):
        expected = [
            u'Copyright (c) 2003+ Evgeniy Polyakov <johnpol@2ka.mxt.ru>',
        ]
        check_detection(expected, 'ics/iptables-include-linux-netfilter/xt_osf.h')

    def test_ics_iptables_include_linux_netfilter_ipv4_ipt_ttl_h(self):
        expected = [
            u'(c) 2000 by Harald Welte <laforge@gnumonks.org>',
        ]
        check_detection(expected, 'ics/iptables-include-linux-netfilter_ipv4/ipt_ttl.h')

    def test_ics_iptables_include_linux_netfilter_ipv4_ipt_ulog_h(self):
        expected = [
            u'(c) 2000-2002 by Harald Welte <laforge@gnumonks.org>',
        ]
        check_detection(expected, 'ics/iptables-include-linux-netfilter_ipv4/ipt_ULOG.h')

    def test_ics_iptables_iptables_ip6tables_standalone_c(self):
        expected = [
            u'(c) 2000-2002 by the netfilter coreteam <coreteam@netfilter.org> Paul Rusty Russell <rusty@rustcorp.com.au> Marc Boucher <marc+nf@mbsi.ca>',
        ]
        check_detection(expected, 'ics/iptables-iptables/ip6tables-standalone.c')

    def test_ics_iptables_iptables_iptables_xslt_extra_author(self):
        expected = [
            u'Copyright 2006 UfoMechanic',
        ]
        check_detection(expected, 'ics/iptables-iptables/iptables.xslt')

    def test_ics_iptables_iptables_iptables_apply(self):
        expected = [
            u'Copyright (c) Martin F. Krafft <madduck@madduck.net>',
        ]
        check_detection(expected, 'ics/iptables-iptables/iptables-apply')

    def test_ics_iptables_iptables_iptables_apply_8(self):
        expected = [
            u'copyright by Martin F. Krafft.',
        ]
        check_detection(expected, 'ics/iptables-iptables/iptables-apply.8')

    def test_ics_iptables_iptables_iptables_restore_c(self):
        expected = [
            u'(c) 2000-2002 by Harald Welte <laforge@gnumonks.org>',
        ]
        check_detection(expected, 'ics/iptables-iptables/iptables-restore.c')

    def test_ics_iptables_iptables_iptables_save_c(self):
        expected = [
            u'(c) 1999 by Paul Rusty Russell <rusty@rustcorp.com.au>',
            u'(c) 2000-2002 by Harald Welte <laforge@gnumonks.org>',
        ]
        check_detection(expected, 'ics/iptables-iptables/iptables-save.c')

    def test_ics_iptables_iptables_iptables_xml_c(self):
        expected = [
            u'(c) 2006 Ufo Mechanic <azez@ufomechanic.net>',
            u'(c) 2000-2002 by Harald Welte <laforge@gnumonks.org>',
        ]
        check_detection(expected, 'ics/iptables-iptables/iptables-xml.c')

    def test_ics_iptables_iptables_xtables_c_trail_name(self):
        expected = [
            u'(c) 2000-2006 by the netfilter coreteam <coreteam@netfilter.org>',
        ]
        check_detection(expected, 'ics/iptables-iptables/xtables.c')

    def test_ics_iptables_iptables_xtoptions_c(self):
        expected = [
            u'Copyright (c) Jan Engelhardt, 2011',
        ]
        check_detection(expected, 'ics/iptables-iptables/xtoptions.c')

    def test_ics_iptables_libipq_ipq_create_handle_3(self):
        expected = [
            u'Copyright (c) 2000-2001 Netfilter Core Team',
            u'Copyright (c) 2000-2001 Netfilter Core Team.',
        ]
        check_detection(expected, 'ics/iptables-libipq/ipq_create_handle.3')

    def test_ics_iptables_libipq_ipq_errstr_3(self):
        expected = [
            u'Copyright (c) 2000 Netfilter Core Team',
            u'Copyright (c) 2000-2001 Netfilter Core Team.',
        ]
        check_detection(expected, 'ics/iptables-libipq/ipq_errstr.3')

    def test_ics_iptables_libiptc_libip4tc_c(self):
        expected = [
            u'(c) 1999 Paul Rusty Russell',
        ]
        check_detection(expected, 'ics/iptables-libiptc/libip4tc.c')

    def test_ics_iptables_libiptc_libiptc_c(self):
        expected = [
            u'(c) 1999 Paul Rusty Russell',
            u'(c) 2000-2004 by the Netfilter Core Team <coreteam@netfilter.org>',
        ]
        check_detection(expected, 'ics/iptables-libiptc/libiptc.c')

    def test_ics_iptables_m4_ax_check_linker_flags_m4(self):
        expected = [
            u'Copyright (c) 2009 Mike Frysinger <vapier@gentoo.org>',
            u'Copyright (c) 2009 Steven G. Johnson <stevenj@alum.mit.edu>',
            u'Copyright (c) 2009 Matteo Frigo',
        ]
        check_detection(expected, 'ics/iptables-m4/ax_check_linker_flags.m4')

    def test_ics_iptables_utils_nfnl_osf_c(self):
        expected = [
            u'Copyright (c) 2005 Evgeniy Polyakov <johnpol@2ka.mxt.ru>',
        ]
        check_detection(expected, 'ics/iptables-utils/nfnl_osf.c')

    def test_ics_iptables_utils_pf_os(self):
        expected = [
            u'(c) Copyright 2000-2003 by Michal Zalewski <lcamtuf@coredump.cx>',
            u'(c) Copyright 2003 by Mike Frantzen <frantzen@w4g.org>',
        ]
        check_detection(expected, 'ics/iptables-utils/pf.os')

    def test_ics_javasqlite_src_main_native_sqlite_jni_defs_h(self):
        expected = [
            u'Copyright 2007, The Android Open Source Project',
        ]
        check_detection(expected, 'ics/javasqlite-src-main-native/sqlite_jni_defs.h')

    def test_ics_javassist_license_html(self):
        expected = [
            u'Copyright (c) 1999-2010 Shigeru Chiba.',
        ]
        check_detection(expected, 'ics/javassist/License.html')

    def test_ics_javassist_notice(self):
        expected = [
            u'Copyright (c) 1999-2010 Shigeru Chiba.',
        ]
        check_detection(expected, 'ics/javassist/NOTICE')

    def test_ics_javassist_readme_html(self):
        expected = [
            u'Copyright (c) 1999-2010 by Shigeru Chiba',
            u'Copyright (c) 1999-2010 Shigeru Chiba.',
            u'Copyright (c) 1999-2010 Shigeru Chiba.',
        ]
        check_detection(expected, 'ics/javassist/Readme.html')

    def test_ics_javassist_sample_preproc_assistant_java(self):
        expected = [
            u'Copyright (c) 1999-2005 Shigeru Chiba.',
        ]
        check_detection(expected, 'ics/javassist-sample-preproc/Assistant.java')

    def test_ics_javassist_src_main_javassist_bytearrayclasspath_java(self):
        expected = [
            u'Copyright (c) 1999-2007 Shigeru Chiba.',
        ]
        check_detection(expected, 'ics/javassist-src-main-javassist/ByteArrayClassPath.java')

    def test_ics_javassist_src_main_javassist_ctclass_java(self):
        expected = [
            u'Copyright (c) 1999-2007 Shigeru Chiba.',
            u'Copyright (c) 1999-2010 Shigeru Chiba.',
        ]
        check_detection(expected, 'ics/javassist-src-main-javassist/CtClass.java')

    def test_ics_javassist_src_main_javassist_ctclass_java_lead_copy(self):
        expected = [
            u'Copyright (c) 1999-2007 Shigeru Chiba.',
            u'Copyright (c) 1999-2010 Shigeru Chiba.',
        ]
        check_detection(expected, 'ics/javassist-src-main-javassist/CtClass.java')

    def test_ics_javassist_src_main_javassist_bytecode_bytestream_java(self):
        expected = [
            u'Copyright (c) 1999-2010 Shigeru Chiba.',
        ]
        check_detection(expected, 'ics/javassist-src-main-javassist-bytecode/ByteStream.java')

    def test_ics_javassist_src_main_javassist_bytecode_instructionprinter_java(self):
        expected = [
            u'Copyright (c) 1999-2007 Shigeru Chiba, and others.',
        ]
        check_detection(expected, 'ics/javassist-src-main-javassist-bytecode/InstructionPrinter.java')

    def test_ics_javassist_src_main_javassist_bytecode_annotation_annotation_java(self):
        expected = [
            u'Copyright (c) 2004 Bill Burke.',
        ]
        check_detection(expected, 'ics/javassist-src-main-javassist-bytecode-annotation/Annotation.java')

    def test_ics_javassist_src_main_javassist_bytecode_annotation_nosuchclasserror_java(self):
        expected = [
            u'Copyright (c) 1999-2009 Shigeru Chiba.',
        ]
        check_detection(expected, 'ics/javassist-src-main-javassist-bytecode-annotation/NoSuchClassError.java')

    def test_ics_javassist_tutorial_tutorial_html(self):
        expected = [
            u'Copyright (c) 2000-2010 by Shigeru Chiba',
        ]
        check_detection(expected, 'ics/javassist-tutorial/tutorial.html')

    def test_ics_jdiff_src_jdiff_diffmyers_java(self):
        expected = [
            u'Copyright (c) 2000 Business Management Systems, Inc.',
        ]
        check_detection(expected, 'ics/jdiff-src-jdiff/DiffMyers.java')

    def test_ics_jhead_main_c(self):
        expected = [
            u'Copyright (c) 2008, The Android Open Source Project',
        ]
        check_detection(expected, 'ics/jhead/main.c')

    def test_ics_jpeg_ansi2knr_c(self):
        expected = [
            u'Copyright (c) 1988 Richard M. Stallman',
            u'Copyright (c) 1989 Aladdin Enterprises.',
        ]
        check_detection(expected, 'ics/jpeg/ansi2knr.c')

    def test_ics_jpeg_cderror_h(self):
        expected = [
            u'Copyright (c) 1994-1997, Thomas G. Lane.',
        ]
        check_detection(expected, 'ics/jpeg/cderror.h')

    def test_ics_jpeg_cdjpeg_c(self):
        expected = [
            u'Copyright (c) 1991-1997, Thomas G. Lane.',
        ]
        check_detection(expected, 'ics/jpeg/cdjpeg.c')

    def test_ics_jpeg_cjpeg_c(self):
        expected = [
            u'Copyright (c) 1991-1998, Thomas G. Lane.',
        ]
        check_detection(expected, 'ics/jpeg/cjpeg.c')

    def test_ics_jpeg_ckconfig_c(self):
        expected = [
            u'Copyright (c) 1991-1994, Thomas G. Lane.',
        ]
        check_detection(expected, 'ics/jpeg/ckconfig.c')

    def test_ics_jpeg_coderules_doc(self):
        expected = [
            u'Copyright (c) 1991-1996, Thomas G. Lane.',
        ]
        check_detection(expected, 'ics/jpeg/coderules.doc')

    def test_ics_jpeg_config_guess(self):
        expected = [
            u'Copyright (c) 1992, 93, 94, 95, 96, 1997 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/jpeg/config.guess')

    def test_ics_jpeg_config_sub(self):
        expected = [
            u'Copyright (c) 1991, 92, 93, 94, 95, 96, 1997 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/jpeg/config.sub')

    def test_ics_jpeg_configure(self):
        expected = [
            u'Copyright (c) 1992, 93, 94, 95, 96 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/jpeg/configure')

    def test_ics_jpeg_filelist_doc(self):
        expected = [
            u'Copyright (c) 1994-1998, Thomas G. Lane.',
        ]
        check_detection(expected, 'ics/jpeg/filelist.doc')

    def test_ics_jpeg_install_doc(self):
        expected = [
            u'Copyright (c) 1991-1998, Thomas G. Lane.',
        ]
        check_detection(expected, 'ics/jpeg/install.doc')

    def test_ics_jpeg_jcapimin_c(self):
        expected = [
            u'Copyright (c) 1994-1998, Thomas G. Lane.',
        ]
        check_detection(expected, 'ics/jpeg/jcapimin.c')

    def test_ics_jpeg_jcapistd_c(self):
        expected = [
            u'Copyright (c) 1994-1996, Thomas G. Lane.',
        ]
        check_detection(expected, 'ics/jpeg/jcapistd.c')

    def test_ics_jpeg_jccolor_c(self):
        expected = [
            u'Copyright (c) 1991-1996, Thomas G. Lane.',
        ]
        check_detection(expected, 'ics/jpeg/jccolor.c')

    def test_ics_jpeg_jcphuff_c(self):
        expected = [
            u'Copyright (c) 1995-1997, Thomas G. Lane.',
        ]
        check_detection(expected, 'ics/jpeg/jcphuff.c')

    def test_ics_jpeg_jctrans_c(self):
        expected = [
            u'Copyright (c) 1995-1998, Thomas G. Lane.',
        ]
        check_detection(expected, 'ics/jpeg/jctrans.c')

    def test_ics_jpeg_jmem_android_c(self):
        expected = [
            u'Copyright (c) 2007-2008 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/jpeg/jmem-android.c')

    def test_ics_jpeg_jmemansi_c(self):
        expected = [
            u'Copyright (c) 1992-1996, Thomas G. Lane.',
        ]
        check_detection(expected, 'ics/jpeg/jmemansi.c')

    def test_ics_jpeg_jmemdos_c(self):
        expected = [
            u'Copyright (c) 1992-1997, Thomas G. Lane.',
        ]
        check_detection(expected, 'ics/jpeg/jmemdos.c')

    def test_ics_jpeg_jversion_h(self):
        expected = [
            u'Copyright (c) 1991-1998, Thomas G. Lane.',
            u'Copyright (c) 1998, Thomas G. Lane',
        ]
        check_detection(expected, 'ics/jpeg/jversion.h')

    def test_ics_jpeg_ltconfig(self):
        expected = [
            u'Copyright (c) 1996-1998 Free Software Foundation, Inc. Gordon Matzigkeit <gord@gnu.ai.mit.edu>',
            u'Copyright (c) 1996-1998 Free Software Foundation, Inc. Gordon Matzigkeit <gord@gnu.ai.mit.edu>'
        ]
        check_detection(expected, 'ics/jpeg/ltconfig')

    def test_ics_jpeg_ltmain_sh(self):
        expected = [
            u'Copyright (c) 1996-1998 Free Software Foundation, Inc. Gordon Matzigkeit <gord@gnu.ai.mit.edu>'
        ]
        check_detection(expected, 'ics/jpeg/ltmain.sh')

    def test_ics_jpeg_notice(self):
        expected = [
            u'copyright (c) 1991-1998, Thomas G. Lane.',
        ]
        check_detection(expected, 'ics/jpeg/NOTICE')

    def test_ics_jpeg_rdcolmap_c(self):
        expected = [
            u'Copyright (c) 1994-1996, Thomas G. Lane.',
            u'Copyright (c) 1988 by Jef Poskanzer.',
        ]
        check_detection(expected, 'ics/jpeg/rdcolmap.c')

    def test_ics_jpeg_rdppm_c(self):
        expected = [
            u'Copyright (c) 1991-1997, Thomas G. Lane.',
            u'Copyright (c) 1988 by Jef Poskanzer.',
        ]
        check_detection(expected, 'ics/jpeg/rdppm.c')

    def test_ics_jpeg_readme(self):
        expected = [
            u'copyright (c) 1991-1998, Thomas G. Lane.',
            u'copyright by the Free Software Foundation',
        ]
        check_detection(expected, 'ics/jpeg/README')

    def test_ics_jpeg_structure_doc(self):
        expected = [
            u'Copyright (c) 1991-1995, Thomas G. Lane.',
        ]
        check_detection(expected, 'ics/jpeg/structure.doc')

    def test_ics_jpeg_transupp_c(self):
        expected = [
            u'Copyright (c) 1997, Thomas G. Lane.',
        ]
        check_detection(expected, 'ics/jpeg/transupp.c')

    def test_ics_jpeg_wrgif_c(self):
        expected = [
            u'Copyright (c) 1991-1997, Thomas G. Lane.',
            u'Copyright (c) 1989 by Jef Poskanzer.',
        ]
        check_detection(expected, 'ics/jpeg/wrgif.c')

    def test_ics_jpeg_wrjpgcom_c(self):
        expected = [
            u'Copyright (c) 1994-1997, Thomas G. Lane.',
        ]
        check_detection(expected, 'ics/jpeg/wrjpgcom.c')

    def test_ics_jsr305_notice_trail_name(self):
        expected = [
            u'Copyright (c) 2007-2009, JSR305 expert group',
        ]
        check_detection(expected, 'ics/jsr305/NOTICE')

    def test_ics_jsr305_ri_src_main_java_javax_annotation_concurrent_guardedby_java(self):
        expected = [
            u'Copyright (c) 2005 Brian Goetz',
        ]
        check_detection(expected, 'ics/jsr305-ri-src-main-java-javax-annotation-concurrent/GuardedBy.java')

    def test_ics_kernel_headers_original_asm_arm_atomic_h(self):
        expected = [
            u'Copyright (c) 1996 Russell King.',
            u'Copyright (c) 2002 Deep Blue Solutions Ltd.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/atomic.h')

    def test_ics_kernel_headers_original_asm_arm_bitops_h(self):
        expected = [
            u'Copyright 1995, Russell King.',
            u'Copyright 2001, Nicolas Pitre',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/bitops.h')

    def test_ics_kernel_headers_original_asm_arm_bitops_h_extra_various(self):
        expected = [
            u'Copyright 1995, Russell King.',
            u'Copyright 2001, Nicolas Pitre',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/bitops.h')

    def test_ics_kernel_headers_original_asm_arm_cacheflush_h(self):
        expected = [
            u'Copyright (c) 1999-2002 Russell King',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/cacheflush.h')

    def test_ics_kernel_headers_original_asm_arm_delay_h(self):
        expected = [
            u'Copyright (c) 1995-2004 Russell King',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/delay.h')

    def test_ics_kernel_headers_original_asm_arm_domain_h(self):
        expected = [
            u'Copyright (c) 1999 Russell King.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/domain.h')

    def test_ics_kernel_headers_original_asm_arm_fpstate_h(self):
        expected = [
            u'Copyright (c) 1995 Russell King',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/fpstate.h')

    def test_ics_kernel_headers_original_asm_arm_glue_h(self):
        expected = [
            u'Copyright (c) 1997-1999 Russell King',
            u'Copyright (c) 2000-2002 Deep Blue Solutions Ltd.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/glue.h')

    def test_ics_kernel_headers_original_asm_arm_hardware_h(self):
        expected = [
            u'Copyright (c) 1996 Russell King',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/hardware.h')

    def test_ics_kernel_headers_original_asm_arm_ide_h(self):
        expected = [
            u'Copyright (c) 1994-1996 Linus Torvalds',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/ide.h')

    def test_ics_kernel_headers_original_asm_arm_io_h(self):
        expected = [
            u'Copyright (c) 1996-2000 Russell King',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/io.h')

    def test_ics_kernel_headers_original_asm_arm_locks_h(self):
        expected = [
            u'Copyright (c) 2000 Russell King',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/locks.h')

    def test_ics_kernel_headers_original_asm_arm_memory_h(self):
        expected = [
            u'Copyright (c) 2000-2002 Russell King',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/memory.h')

    def test_ics_kernel_headers_original_asm_arm_mtd_xip_h(self):
        expected = [
            u'Copyright (c) 2004 MontaVista Software, Inc.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/mtd-xip.h')

    def test_ics_kernel_headers_original_asm_arm_page_h(self):
        expected = [
            u'Copyright (c) 1995-2003 Russell King',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/page.h')

    def test_ics_kernel_headers_original_asm_arm_param_h(self):
        expected = [
            u'Copyright (c) 1995-1999 Russell King',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/param.h')

    def test_ics_kernel_headers_original_asm_arm_pgalloc_h(self):
        expected = [
            u'Copyright (c) 2000-2001 Russell King',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/pgalloc.h')

    def test_ics_kernel_headers_original_asm_arm_pgtable_hwdef_h(self):
        expected = [
            u'Copyright (c) 1995-2002 Russell King',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/pgtable-hwdef.h')

    def test_ics_kernel_headers_original_asm_arm_posix_types_h(self):
        expected = [
            u'Copyright (c) 1996-1998 Russell King.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/posix_types.h')

    def test_ics_kernel_headers_original_asm_arm_proc_fns_h(self):
        expected = [
            u'Copyright (c) 1997-1999 Russell King',
            u'Copyright (c) 2000 Deep Blue Solutions Ltd',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/proc-fns.h')

    def test_ics_kernel_headers_original_asm_arm_procinfo_h(self):
        expected = [
            u'Copyright (c) 1996-1999 Russell King',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/procinfo.h')

    def test_ics_kernel_headers_original_asm_arm_ptrace_h(self):
        expected = [
            u'Copyright (c) 1996-2003 Russell King',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/ptrace.h')

    def test_ics_kernel_headers_original_asm_arm_sizes_h(self):
        expected = [
            u'Copyright (c) ARM Limited 1998.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/sizes.h')

    def test_ics_kernel_headers_original_asm_arm_smp_h(self):
        expected = [
            u'Copyright (c) 2004-2005 ARM Ltd.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/smp.h')

    def test_ics_kernel_headers_original_asm_arm_thread_info_h(self):
        expected = [
            u'Copyright (c) 2002 Russell King.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/thread_info.h')

    def test_ics_kernel_headers_original_asm_arm_timex_h(self):
        expected = [
            u'Copyright (c) 1997,1998 Russell King',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/timex.h')

    def test_ics_kernel_headers_original_asm_arm_tlbflush_h(self):
        expected = [
            u'Copyright (c) 1999-2003 Russell King',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/tlbflush.h')

    def test_ics_kernel_headers_original_asm_arm_unistd_h(self):
        expected = [
            u'Copyright (c) 2001-2005 Russell King',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm/unistd.h')

    def test_ics_kernel_headers_original_asm_arm_arch_board_h(self):
        expected = [
            u'Copyright (c) 2004 Nokia Corporation',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm-arch/board.h')

    def test_ics_kernel_headers_original_asm_arm_arch_board_perseus2_h(self):
        expected = [
            u'Copyright 2003 by Texas Instruments Incorporated',
            u'Copyright (c) 2001 RidgeRun, Inc. (http://www.ridgerun.com)',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm-arch/board-perseus2.h')

    def test_ics_kernel_headers_original_asm_arm_arch_board_perseus2_h_extra_name(self):
        expected = [
            u'Copyright 2003 by Texas Instruments Incorporated',
            u'Copyright (c) 2001 RidgeRun, Inc. (http://www.ridgerun.com)',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm-arch/board-perseus2.h')

    def test_ics_kernel_headers_original_asm_arm_arch_dma_h(self):
        expected = [
            u'Copyright (c) 2003 Nokia Corporation',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm-arch/dma.h')

    def test_ics_kernel_headers_original_asm_arm_arch_fpga_h(self):
        expected = [
            u'Copyright (c) 2001 RidgeRun, Inc.',
            u'Copyright (c) 2002 MontaVista Software, Inc.',
            u'Copyright (c) 2004 Nokia Corporation',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm-arch/fpga.h')

    def test_ics_kernel_headers_original_asm_arm_arch_gpio_h(self):
        expected = [
            u'Copyright (c) 2003-2005 Nokia Corporation',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm-arch/gpio.h')

    def test_ics_kernel_headers_original_asm_arm_arch_gpio_switch_h(self):
        expected = [
            u'Copyright (c) 2006 Nokia Corporation',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm-arch/gpio-switch.h')

    def test_ics_kernel_headers_original_asm_arm_arch_hardware_h(self):
        expected = [
            u'Copyright (c) 2001 RidgeRun, Inc.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm-arch/hardware.h')

    def test_ics_kernel_headers_original_asm_arm_arch_io_h(self):
        expected = [
            u'Copyright (c) 1997-1999 Russell King',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm-arch/io.h')

    def test_ics_kernel_headers_original_asm_arm_arch_irqs_h(self):
        expected = [
            u'Copyright (c) Greg Lonnon 2001',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm-arch/irqs.h')

    def test_ics_kernel_headers_original_asm_arm_arch_mcbsp_h(self):
        expected = [
            u'Copyright (c) 2002 RidgeRun, Inc.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm-arch/mcbsp.h')

    def test_ics_kernel_headers_original_asm_arm_arch_memory_h(self):
        expected = [
            u'Copyright (c) 2000 RidgeRun, Inc.',
            u'Copyright (c) 1999 ARM Limited',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm-arch/memory.h')

    def test_ics_kernel_headers_original_asm_arm_arch_mtd_xip_h(self):
        expected = [
            u'(c) 2005 MontaVista Software, Inc.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm-arch/mtd-xip.h')

    def test_ics_kernel_headers_original_asm_arm_arch_mux_h(self):
        expected = [
            u'Copyright (c) 2003 - 2005 Nokia Corporation',
            u'Copyright (c) 2004 Texas Instruments',
            u'Copyright (c) 2004 Texas Instruments',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm-arch/mux.h')

    def test_ics_kernel_headers_original_asm_arm_arch_timex_h(self):
        expected = [
            u'Copyright (c) 2000 RidgeRun, Inc.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm-arch/timex.h')

    def test_ics_kernel_headers_original_asm_arm_arch_vmalloc_h(self):
        expected = [
            u'Copyright (c) 2000 Russell King.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-arm-arch/vmalloc.h')

    def test_ics_kernel_headers_original_asm_generic_tlb_h_trail_other(self):
        expected = [
            u'Copyright 2001 Red Hat, Inc.',
            u'Copyright Linus Torvalds and others.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-generic/tlb.h')

    def test_ics_kernel_headers_original_asm_generic_topology_h(self):
        expected = [
            u'Copyright (c) 2002, IBM Corp.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-generic/topology.h')

    def test_ics_kernel_headers_original_asm_x86_acpi_32_h(self):
        expected = [
            u'Copyright (c) 2001 Paul Diefenbaugh <paul.s.diefenbaugh@intel.com>',
            u'Copyright (c) 2001 Patrick Mochel <mochel@osdl.org>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-x86/acpi_32.h')

    def test_ics_kernel_headers_original_asm_x86_bitops_32_h(self):
        expected = [
            u'Copyright 1992, Linus Torvalds.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-x86/bitops_32.h')

    def test_ics_kernel_headers_original_asm_x86_delay_h(self):
        expected = [
            u'Copyright (c) 1993 Linus Torvalds',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-x86/delay.h')

    def test_ics_kernel_headers_original_asm_x86_fixmap_32_h(self):
        expected = [
            u'Copyright (c) 1998 Ingo Molnar',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-x86/fixmap_32.h')

    def test_ics_kernel_headers_original_asm_x86_genapic_32_h(self):
        expected = [
            u'Copyright 2003 Andi Kleen, SuSE Labs.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-x86/genapic_32.h')

    def test_ics_kernel_headers_original_asm_x86_highmem_h(self):
        expected = [
            u'Copyright (c) 1999 Gerhard Wichert, Siemens AG',
            u'Copyright (c) 1999 Ingo Molnar <mingo@redhat.com>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-x86/highmem.h')

    def test_ics_kernel_headers_original_asm_x86_hw_irq_32_h(self):
        expected = [
            u'(c) 1992, 1993 Linus Torvalds',
            u'(c) 1997 Ingo Molnar',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-x86/hw_irq_32.h')

    def test_ics_kernel_headers_original_asm_x86_i387_32_h(self):
        expected = [
            u'Copyright (c) 1994 Linus Torvalds',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-x86/i387_32.h')

    def test_ics_kernel_headers_original_asm_x86_io_apic_32_h(self):
        expected = [
            u'Copyright (c) 1997, 1998, 1999, 2000 Ingo Molnar',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-x86/io_apic_32.h')

    def test_ics_kernel_headers_original_asm_x86_ist_h(self):
        expected = [
            u'Copyright 2002 Andy Grover <andrew.grover@intel.com>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-x86/ist.h')

    def test_ics_kernel_headers_original_asm_x86_semaphore_32_h(self):
        expected = [
            u'(c) Copyright 1996 Linus Torvalds',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-x86/semaphore_32.h')

    def test_ics_kernel_headers_original_asm_x86_thread_info_32_h(self):
        expected = [
            u'Copyright (c) 2002 David Howells (dhowells@redhat.com)',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-x86/thread_info_32.h')

    def test_ics_kernel_headers_original_asm_x86_voyager_h(self):
        expected = [
            u'Copyright (c) 1999,2001',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-x86/voyager.h')

    def test_ics_kernel_headers_original_asm_x86_xen_hypercall_h(self):
        expected = [
            u'Copyright (c) 2002-2004, K A Fraser',
        ]
        check_detection(expected, 'ics/kernel-headers-original-asm-x86-xen/hypercall.h')

    def test_ics_kernel_headers_original_linux_a1026_h(self):
        expected = [
            u'Copyright (c) 2009 HTC Corporation.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/a1026.h')

    def test_ics_kernel_headers_original_linux_aio_abi_h(self):
        expected = [
            u'Copyright 2000,2001,2002 Red Hat.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/aio_abi.h')

    def test_ics_kernel_headers_original_linux_android_alarm_h(self):
        expected = [
            u'Copyright 2006, The Android Open Source Project',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/android_alarm.h')

    def test_ics_kernel_headers_original_linux_android_pmem_h(self):
        expected = [
            u'Copyright (c) 2007 Google, Inc.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/android_pmem.h')

    def test_ics_kernel_headers_original_linux_android_power_h(self):
        expected = [
            u'Copyright 2005-2006, The Android Open Source Project',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/android_power.h')

    def test_ics_kernel_headers_original_linux_apm_bios_h(self):
        expected = [
            u'Copyright 1994-2001 Stephen Rothwell (sfr@canb.auug.org.au)',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/apm_bios.h')

    def test_ics_kernel_headers_original_linux_ashmem_h(self):
        expected = [
            u'Copyright 2008 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/ashmem.h')

    def test_ics_kernel_headers_original_linux_ata_h(self):
        expected = [
            u'Copyright 2003-2004 Red Hat, Inc.',
            u'Copyright 2003-2004 Jeff Garzik',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/ata.h')

    def test_ics_kernel_headers_original_linux_attribute_container_h(self):
        expected = [
            u'Copyright (c) 2005 - James Bottomley <James.Bottomley@steeleye.com>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/attribute_container.h')

    def test_ics_kernel_headers_original_linux_auto_fs_h(self):
        expected = [
            u'Copyright 1997 Transmeta Corporation',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/auto_fs.h')

    def test_ics_kernel_headers_original_linux_binder_h(self):
        expected = [
            u'Copyright (c) 2008 The Android Open Source Project',
            u'Copyright (c) 2005 Palmsource, Inc.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/binder.h')

    def test_ics_kernel_headers_original_linux_bio_h(self):
        expected = [
            u'Copyright (c) 2001 Jens Axboe <axboe@suse.de>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/bio.h')

    def test_ics_kernel_headers_original_linux_bmp085_h(self):
        expected = [
            u'Copyright (c) 2010 Motorola, Inc.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/bmp085.h')

    def test_ics_kernel_headers_original_linux_capella_cm3602_h(self):
        expected = [
            u'Copyright (c) 2009 Google, Inc.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/capella_cm3602.h')

    def test_ics_kernel_headers_original_linux_capi_h(self):
        expected = [
            u'Copyright 1997 by Carsten Paeth (calle@calle.in-berlin.de)',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/capi.h')

    def test_ics_kernel_headers_original_linux_cdrom_h(self):
        expected = [
            u'Copyright (c) 1992 David Giller, rafetmad@oxy.edu 1994, 1995 Eberhard Moenkeberg, emoenke@gwdg.de 1996 David van Leeuwen',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/cdrom.h')

    @expectedFailure
    def test_ics_kernel_headers_original_linux_cdrom_h_trail_email(self):
        expected = [
            u'Copyright (c) 1992 David Giller, rafetmad@oxy.edu 1994, 1995 Eberhard Moenkeberg, emoenke@gwdg.de 1996 David van Leeuwen, david@tm.tno.nl',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/cdrom.h')

    def test_ics_kernel_headers_original_linux_clk_h(self):
        expected = [
            u'Copyright (c) 2004 ARM Limited.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/clk.h')

    def test_ics_kernel_headers_original_linux_coda_h(self):
        expected = [
            u'Copyright (c) 1987-1999 Carnegie Mellon University',
            u'Copyright (c) 1987-1999 Carnegie Mellon University',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/coda.h')

    def test_ics_kernel_headers_original_linux_coda_fs_i_h(self):
        expected = [
            u'Copyright (c) 1998 Carnegie Mellon University',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/coda_fs_i.h')

    def test_ics_kernel_headers_original_linux_completion_h(self):
        expected = [
            u'(c) Copyright 2001 Linus Torvalds',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/completion.h')

    def test_ics_kernel_headers_original_linux_cpcap_audio_h(self):
        expected = [
            u'Copyright (c) 2010 Google, Inc.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/cpcap_audio.h')

    def test_ics_kernel_headers_original_linux_device_h(self):
        expected = [
            u'Copyright (c) 2001-2003 Patrick Mochel <mochel@osdl.org>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/device.h')

    def test_ics_kernel_headers_original_linux_dmaengine_h(self):
        expected = [
            u'Copyright (c) 2004 - 2006 Intel Corporation.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/dmaengine.h')

    def test_ics_kernel_headers_original_linux_dm_ioctl_h_trail_name(self):
        expected = [
            u'Copyright (c) 2001 - 2003 Sistina Software (UK) Limited.',
            u'Copyright (c) 2004 - 2005 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/dm-ioctl.h')

    def test_ics_kernel_headers_original_linux_efs_dir_h(self):
        expected = [
            u'Copyright (c) 1999 Al Smith',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/efs_dir.h')

    def test_ics_kernel_headers_original_linux_efs_fs_i_h(self):
        expected = [
            u'Copyright (c) 1999 Al Smith',
            u'(c) 1988 Silicon Graphics',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/efs_fs_i.h')

    def test_ics_kernel_headers_original_linux_ethtool_h(self):
        expected = [
            u'Copyright (c) 1998 David S. Miller (davem@redhat.com)',
            u'Copyright 2001 Jeff Garzik <jgarzik@pobox.com>',
            u'Portions Copyright 2001 Sun Microsystems (thockin@sun.com)',
            u'Portions Copyright 2002 Intel',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/ethtool.h')

    def test_ics_kernel_headers_original_linux_ext2_fs_h_trail_name(self):
        expected = [
            u'Copyright (c) 1992, 1993, 1994, 1995 Remy Card (card@masi.ibp.fr) Laboratoire MASI - Institut Blaise Pascal',
            u'Copyright (c) 1991, 1992 Linus Torvalds',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/ext2_fs.h')

    def test_ics_kernel_headers_original_linux_ext3_fs_h_trail_name(self):
        expected = [
            u'Copyright (c) 1992, 1993, 1994, 1995 Remy Card (card@masi.ibp.fr) Laboratoire MASI - Institut Blaise Pascal',
            u'Copyright (c) 1991, 1992 Linus Torvalds',
            u'(c) Daniel Phillips, 2001',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/ext3_fs.h')

    def test_ics_kernel_headers_original_linux_ftape_h(self):
        expected = [
            u'Copyright (c) 1994-1996 Bas Laarhoven',
            u'(c) 1996-1997 Claus-Justus Heine.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/ftape.h')

    def test_ics_kernel_headers_original_linux_genhd_h_extra_generic(self):
        expected = [
            u'Copyright (c) 1992 Drew Eckhardt',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/genhd.h')

    def test_ics_kernel_headers_original_linux_hdsmart_h(self):
        expected = [
            u'Copyright (c) 1999-2000 Michael Cornwell <cornwell@acm.org>',
            u'Copyright (c) 2000 Andre Hedrick <andre@linux-ide.org>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/hdsmart.h')

    def test_ics_kernel_headers_original_linux_hid_h(self):
        expected = [
            u'Copyright (c) 1999 Andreas Gal',
            u'Copyright (c) 2000-2001 Vojtech Pavlik',
            u'Copyright (c) 2006-2007 Jiri Kosina',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/hid.h')

    def test_ics_kernel_headers_original_linux_hidraw_h(self):
        expected = [
            u'Copyright (c) 2007 Jiri Kosina',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/hidraw.h')

    def test_ics_kernel_headers_original_linux_hil_h(self):
        expected = [
            u'Copyright (c) 2001 Brian S. Julin',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/hil.h')

    def test_ics_kernel_headers_original_linux_i2c_h(self):
        expected = [
            u'Copyright (c) 1995-2000 Simon G. Vogl',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/i2c.h')

    def test_ics_kernel_headers_original_linux_if_ppp_h(self):
        expected = [
            u'Copyright (c) 1989 Carnegie Mellon University.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/if_ppp.h')

    def test_ics_kernel_headers_original_linux_inotify_h(self):
        expected = [
            u'Copyright (c) 2005 John McCutchan',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/inotify.h')

    def test_ics_kernel_headers_original_linux_input_h(self):
        expected = [
            u'Copyright (c) 1999-2002 Vojtech Pavlik',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/input.h')

    def test_ics_kernel_headers_original_linux_ion_h(self):
        expected = [
            u'Copyright (c) 2011 Google, Inc.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/ion.h')

    def test_ics_kernel_headers_original_linux_ipmi_msgdefs_h(self):
        expected = [
            u'Copyright 2002 MontaVista Software Inc.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/ipmi_msgdefs.h')

    def test_ics_kernel_headers_original_linux_jbd_h(self):
        expected = [
            u'Copyright 1998-2000 Red Hat, Inc',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/jbd.h')

    def test_ics_kernel_headers_original_linux_kernelcapi_h(self):
        expected = [
            u'(c) Copyright 1997 by Carsten Paeth (calle@calle.in-berlin.de)',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/kernelcapi.h')

    def test_ics_kernel_headers_original_linux_keychord_h(self):
        expected = [
            u'Copyright (c) 2008 Google, Inc.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/keychord.h')

    def test_ics_kernel_headers_original_linux_klist_h(self):
        expected = [
            u'Copyright (c) 2005 Patrick Mochel',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/klist.h')

    def test_ics_kernel_headers_original_linux_kobject_h(self):
        expected = [
            u'Copyright (c) 2002-2003 Patrick Mochel',
            u'Copyright (c) 2002-2003 Open Source Development Labs',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/kobject.h')

    def test_ics_kernel_headers_original_linux_kref_h(self):
        expected = [
            u'Copyright (c) 2004 Greg Kroah-Hartman <greg@kroah.com>',
            u'Copyright (c) 2004 IBM Corp.',
            u'Copyright (c) 2002-2003 Patrick Mochel <mochel@osdl.org>',
            u'Copyright (c) 2002-2003 Open Source Development Labs',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/kref.h')

    def test_ics_kernel_headers_original_linux_ktime_h(self):
        expected = [
            u'Copyright (c) 2005, Thomas Gleixner <tglx@linutronix.de>',
            u'Copyright (c) 2005, Red Hat, Inc., Ingo Molnar',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/ktime.h')

    def test_ics_kernel_headers_original_linux_kxtf9_h(self):
        expected = [
            u'Copyright (c) 2008-2009, Kionix, Inc.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/kxtf9.h')

    def test_ics_kernel_headers_original_linux_leds_an30259a_h(self):
        expected = [
            u'Copyright (c) 2011 Samsung Electronics Co. Ltd.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/leds-an30259a.h')

    def test_ics_kernel_headers_original_linux_lis331dlh_h(self):
        expected = [
            u'Copyright (c) 2008-2009, Motorola',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/lis331dlh.h')

    def test_ics_kernel_headers_original_linux_lockdep_h(self):
        expected = [
            u'Copyright (c) 2006 Red Hat, Inc., Ingo Molnar <mingo@redhat.com>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/lockdep.h')

    def test_ics_kernel_headers_original_linux_loop_h_trail_name(self):
        expected = [
            u"Copyright 1993 by Theodore Ts'o.",
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/loop.h')

    def test_ics_kernel_headers_original_linux_mc146818rtc_h(self):
        expected = [
            u'Copyright Torsten Duwe <duwe@informatik.uni-erlangen.de> 1993',
            u'Copyright Motorola 1984',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/mc146818rtc.h')

    def test_ics_kernel_headers_original_linux_mempolicy_h(self):
        expected = [
            u'Copyright 2003,2004 Andi Kleen SuSE Labs',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/mempolicy.h')

    def test_ics_kernel_headers_original_linux_moduleparam_h(self):
        expected = [
            u'(c) Copyright 2001, 2002 Rusty Russell IBM Corporation',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/moduleparam.h')

    def test_ics_kernel_headers_original_linux_msm_kgsl_h(self):
        expected = [
            u'(c) Copyright Advanced Micro Devices, Inc. 2002, 2007',
            u'Copyright (c) 2008-2009 QUALCOMM USA, INC.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/msm_kgsl.h')

    def test_ics_kernel_headers_original_linux_msm_mdp_h(self):
        expected = [
            u'Copyright (c) 2007 Google Incorporated',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/msm_mdp.h')

    def test_ics_kernel_headers_original_linux_msm_q6vdec_h(self):
        expected = [
            u'Copyright (c) 2008-2009, Code Aurora Forum.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/msm_q6vdec.h')

    def test_ics_kernel_headers_original_linux_msm_vidc_dec_h(self):
        expected = [
            u'Copyright (c) 2010, Code Aurora Forum.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/msm_vidc_dec.h')

    def test_ics_kernel_headers_original_linux_msm_vidc_enc_h(self):
        expected = [
            u'Copyright (c) 2009, Code Aurora Forum.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/msm_vidc_enc.h')

    def test_ics_kernel_headers_original_linux_mt9t013_h(self):
        expected = [
            u'Copyright (c) 2007, 2008 HTC, Inc',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/mt9t013.h')

    def test_ics_kernel_headers_original_linux_mutex_h(self):
        expected = [
            u'Copyright (c) 2004, 2005, 2006 Red Hat, Inc., Ingo Molnar <mingo@redhat.com>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/mutex.h')

    def test_ics_kernel_headers_original_linux_ncp_h(self):
        expected = [
            u'Copyright (c) 1995 by Volker Lendecke',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/ncp.h')

    def test_ics_kernel_headers_original_linux_ncp_mount_h(self):
        expected = [
            u'Copyright (c) 1995, 1996 by Volker Lendecke',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/ncp_mount.h')

    def test_ics_kernel_headers_original_linux_netfilter_arp_h(self):
        expected = [
            u'(c) 2002 Rusty Russell',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/netfilter_arp.h')

    def test_ics_kernel_headers_original_linux_nfs4_h(self):
        expected = [
            u'Copyright (c) 2002 The Regents of the University of Michigan.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/nfs4.h')

    def test_ics_kernel_headers_original_linux_nfsacl_h(self):
        expected = [
            u'(c) 2003 Andreas Gruenbacher <agruen@suse.de>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/nfsacl.h')

    def test_ics_kernel_headers_original_linux_nvhdcp_h(self):
        expected = [
            u'Copyright (c) 2010-2011, NVIDIA Corporation.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/nvhdcp.h')

    def test_ics_kernel_headers_original_linux_pagemap_h(self):
        expected = [
            u'Copyright 1995 Linus Torvalds',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/pagemap.h')

    def test_ics_kernel_headers_original_linux_patchkey_h(self):
        expected = [
            u'Copyright (c) 2005 Stuart Brady',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/patchkey.h')

    def test_ics_kernel_headers_original_linux_pci_h(self):
        expected = [
            u'Copyright 1994, Drew Eckhardt',
            u'Copyright 1997 1999 Martin Mares <mj@ucw.cz>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/pci.h')

    def test_ics_kernel_headers_original_linux_perf_event_h(self):
        expected = [
            u'Copyright (c) 2008-2009, Thomas Gleixner <tglx@linutronix.de>',
            u'Copyright (c) 2008-2009, Red Hat, Inc., Ingo Molnar',
            u'Copyright (c) 2008-2009, Red Hat, Inc., Peter Zijlstra',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/perf_event.h')

    def test_ics_kernel_headers_original_linux_plist_h(self):
        expected = [
            u'(c) 2002-2003 Intel Corp Inaky Perez-Gonzalez <inaky.perez-gonzalez@intel.com>',
            u'(c) MontaVista Software, Inc.',
            u'(c) 2005 Thomas Gleixner <tglx@linutronix.de>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/plist.h')

    def test_ics_kernel_headers_original_linux_pm_h(self):
        expected = [
            u'Copyright (c) 2000 Andrew Henroid',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/pm.h')

    def test_ics_kernel_headers_original_linux_pn544_h(self):
        expected = [
            u'Copyright (c) 2010 Trusted Logic S.A.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/pn544.h')

    def test_ics_kernel_headers_original_linux_posix_acl_h(self):
        expected = [
            u'(c) 2002 Andreas Gruenbacher, <a.gruenbacher@computer.org>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/posix_acl.h')

    def test_ics_kernel_headers_original_linux_ppdev_h(self):
        expected = [
            u'Copyright (c) 1998-9 Tim Waugh <tim@cyberelk.demon.co.uk>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/ppdev.h')

    def test_ics_kernel_headers_original_linux_ppp_defs_h(self):
        expected = [
            u'Copyright (c) 1994 The Australian National University.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/ppp_defs.h')

    def test_ics_kernel_headers_original_linux_qic117_h(self):
        expected = [
            u'Copyright (c) 1993-1996 Bas Laarhoven',
            u'(c) 1997 Claus-Justus Heine.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/qic117.h')

    def test_ics_kernel_headers_original_linux_quota_h(self):
        expected = [
            u'Copyright (c) 1982, 1986 Regents of the University of California.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/quota.h')

    def test_ics_kernel_headers_original_linux_rcupdate_h(self):
        expected = [
            u'Copyright (c) IBM Corporation, 2001',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/rcupdate.h')

    def test_ics_kernel_headers_original_linux_relay_h(self):
        expected = [
            u'Copyright (c) 2002, 2003 - Tom Zanussi (zanussi@us.ibm.com), IBM Corp',
            u'Copyright (c) 1999, 2000, 2001, 2002 - Karim Yaghmour (karim@opersys.com)',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/relay.h')

    def test_ics_kernel_headers_original_linux_rpmsg_omx_h(self):
        expected = [
            u'Copyright (c) 2011 Texas Instruments.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/rpmsg_omx.h')

    def test_ics_kernel_headers_original_linux_rtc_h(self):
        expected = [
            u'Copyright (c) 1999 Hewlett-Packard Co.',
            u'Copyright (c) 1999 Stephane Eranian <eranian@hpl.hp.com>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/rtc.h')

    def test_ics_kernel_headers_original_linux_serial_core_h(self):
        expected = [
            u'Copyright (c) 2000 Deep Blue Solutions Ltd.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/serial_core.h')

    def test_ics_kernel_headers_original_linux_serial_reg_h_trail_name(self):
        expected = [
            u"Copyright (c) 1992, 1994 by Theodore Ts'o.",
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/serial_reg.h')

    def test_ics_kernel_headers_original_linux_sfh7743_h(self):
        expected = [
            u'Copyright (c) 2009 Motorola, Inc.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/sfh7743.h')

    def test_ics_kernel_headers_original_linux_smb_h(self):
        expected = [
            u'Copyright (c) 1995, 1996 by Paal-Kr. Engstad and Volker Lendecke',
            u'Copyright (c) 1997 by Volker Lendecke',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/smb.h')

    def test_ics_kernel_headers_original_linux_soundcard_h(self):
        expected = [
            u'Copyright by Hannu Savolainen 1993-1997',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/soundcard.h')

    def test_ics_kernel_headers_original_linux_spinlock_api_smp_h(self):
        expected = [
            u'portions Copyright 2005, Red Hat, Inc., Ingo Molnar',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/spinlock_api_smp.h')

    def test_ics_kernel_headers_original_linux_sysfs_h(self):
        expected = [
            u'Copyright (c) 2001,2002 Patrick Mochel',
            u'Copyright (c) 2004 Silicon Graphics, Inc.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/sysfs.h')

    def test_ics_kernel_headers_original_linux_taskstats_h(self):
        expected = [
            u'Copyright (c) Shailabh Nagar, IBM Corp. 2006',
            u'(c) Balbir Singh, IBM Corp. 2006',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/taskstats.h')

    def test_ics_kernel_headers_original_linux_telephony_h(self):
        expected = [
            u'(c) Copyright 1999-2001 Quicknet Technologies, Inc.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/telephony.h')

    def test_ics_kernel_headers_original_linux_timex_h(self):
        expected = [
            u'Copyright (c) David L. Mills 1993',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/timex.h')

    def test_ics_kernel_headers_original_linux_ufs_fs_i_h(self):
        expected = [
            u'Copyright (c) 1996 Adrian Rodriguez (adrian@franklins-tower.rutgers.edu) Laboratory for Computer Science Research Computing Facility',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/ufs_fs_i.h')

    def test_ics_kernel_headers_original_linux_usbdevice_fs_h(self):
        expected = [
            u'Copyright (c) 2000 Thomas Sailer (sailer@ife.ee.ethz.ch)',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/usbdevice_fs.h')

    def test_ics_kernel_headers_original_linux_videodev2_h(self):
        expected = [
            u'Copyright (c) 1999-2007 the contributors',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/videodev2.h')

    def test_ics_kernel_headers_original_linux_vt_buffer_h(self):
        expected = [
            u'(c) 1998 Martin Mares <mj@ucw.cz>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/vt_buffer.h')

    def test_ics_kernel_headers_original_linux_wanrouter_h(self):
        expected = [
            u'Copyright (c) 1995-2000 Sangoma Technologies Inc.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/wanrouter.h')

    def test_ics_kernel_headers_original_linux_wireless_h(self):
        expected = [
            u'Copyright (c) 1997-2006 Jean Tourrilhes',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/wireless.h')

    def test_ics_kernel_headers_original_linux_xattr_h(self):
        expected = [
            u'Copyright (c) 2001 by Andreas Gruenbacher <a.gruenbacher@computer.org>',
            u'Copyright (c) 2001-2002 Silicon Graphics, Inc.',
            u'Copyright (c) 2004 Red Hat, Inc., James Morris <jmorris@redhat.com>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/xattr.h')

    def test_ics_kernel_headers_original_linux_zconf_h(self):
        expected = [
            u'Copyright (c) 1995-1998 Jean-loup Gailly.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux/zconf.h')

    def test_ics_kernel_headers_original_linux_lockd_nlm_h(self):
        expected = [
            u'Copyright (c) 1996, Olaf Kirch <okir@monad.swb.de>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-lockd/nlm.h')

    def test_ics_kernel_headers_original_linux_lockd_xdr_h(self):
        expected = [
            u'Copyright (c) 1996 Olaf Kirch <okir@monad.swb.de>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-lockd/xdr.h')

    def test_ics_kernel_headers_original_linux_mtd_bbm_h(self):
        expected = [
            u'Copyright (c) 2005 Samsung Electronics Kyungmin Park <kyungmin.park@samsung.com>',
            u'Copyright (c) 2000-2005 Thomas Gleixner <tglx@linuxtronix.de>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-mtd/bbm.h')

    def test_ics_kernel_headers_original_linux_mtd_blktrans_h(self):
        expected = [
            u'(c) 2003 David Woodhouse <dwmw2@infradead.org>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-mtd/blktrans.h')

    def test_ics_kernel_headers_original_linux_mtd_flashchip_h(self):
        expected = [
            u'(c) 2000 Red Hat.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-mtd/flashchip.h')

    def test_ics_kernel_headers_original_linux_mtd_mtd_h(self):
        expected = [
            u'Copyright (c) 1999-2003 David Woodhouse <dwmw2@infradead.org>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-mtd/mtd.h')

    def test_ics_kernel_headers_original_linux_mtd_nand_h(self):
        expected = [
            u'Copyright (c) 2000 David Woodhouse <dwmw2@mvhi.com> Steven J. Hill <sjhill@realitydiluted.com> Thomas Gleixner <tglx@linutronix.de>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-mtd/nand.h')

    def test_ics_kernel_headers_original_linux_mtd_nand_ecc_h(self):
        expected = [
            u'Copyright (c) 2000 Steven J. Hill (sjhill@realitydiluted.com)',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-mtd/nand_ecc.h')

    def test_ics_kernel_headers_original_linux_mtd_nftl_h(self):
        expected = [
            u'(c) 1999-2003 David Woodhouse <dwmw2@infradead.org>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-mtd/nftl.h')

    def test_ics_kernel_headers_original_linux_mtd_onenand_regs_h(self):
        expected = [
            u'Copyright (c) 2005 Samsung Electronics',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-mtd/onenand_regs.h')

    def test_ics_kernel_headers_original_linux_mtd_partitions_h(self):
        expected = [
            u'(c) 2000 Nicolas Pitre <nico@cam.org>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-mtd/partitions.h')

    def test_ics_kernel_headers_original_linux_netfilter_xt_connmark_h(self):
        expected = [
            u'Copyright (c) 2002,2004 MARA Systems AB',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-netfilter/xt_CONNMARK.h')

    @expectedFailure
    def test_ics_kernel_headers_original_linux_netfilter_xt_connmark_h_trail_url(self):
        expected = [
            u'Copyright (c) 2002,2004 MARA Systems AB <http://www.marasystems.com>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-netfilter/xt_CONNMARK.h')

    def test_ics_kernel_headers_original_linux_netfilter_ipv4_ip_queue_h(self):
        expected = [
            u'(c) 2000 James Morris',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-netfilter_ipv4/ip_queue.h')

    def test_ics_kernel_headers_original_linux_netfilter_ipv4_ipt_dscp_h(self):
        expected = [
            u'(c) 2002 Harald Welte <laforge@gnumonks.org>',
            u'(c) 2000 by Matthew G. Marsh <mgm@paktronix.com>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-netfilter_ipv4/ipt_DSCP.h')

    def test_ics_kernel_headers_original_linux_netfilter_ipv4_ipt_ttl_h(self):
        expected = [
            u'(c) 2000 by Harald Welte <laforge@netfilter.org>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-netfilter_ipv4/ipt_TTL.h')

    def test_ics_kernel_headers_original_linux_nfsd_auth_h(self):
        expected = [
            u'Copyright (c) 1995, 1996 Olaf Kirch <okir@monad.swb.de>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-nfsd/auth.h')

    def test_ics_kernel_headers_original_linux_nfsd_const_h(self):
        expected = [
            u'Copyright (c) 1995-1997 Olaf Kirch <okir@monad.swb.de>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-nfsd/const.h')

    def test_ics_kernel_headers_original_linux_nfsd_debug_h(self):
        expected = [
            u'Copyright (c) 1995 Olaf Kirch <okir@monad.swb.de>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-nfsd/debug.h')

    def test_ics_kernel_headers_original_linux_nfsd_interface_h(self):
        expected = [
            u'Copyright (c) 2000 Neil Brown <neilb@cse.unsw.edu.au>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-nfsd/interface.h')

    def test_ics_kernel_headers_original_linux_nfsd_nfsfh_h(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997 Olaf Kirch <okir@monad.swb.de>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-nfsd/nfsfh.h')

    def test_ics_kernel_headers_original_linux_raid_md_h(self):
        expected = [
            u'Copyright (c) 1996-98 Ingo Molnar, Gadi Oxman',
            u'Copyright (c) 1994-96 Marc ZYNGIER <zyngier@ufr-info-p7.ibp.fr>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-raid/md.h')

    def test_ics_kernel_headers_original_linux_raid_md_k_h(self):
        expected = [
            u'Copyright (c) 1996-98 Ingo Molnar, Gadi Oxman',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-raid/md_k.h')

    def test_ics_kernel_headers_original_linux_sunrpc_auth_gss_h(self):
        expected = [
            u'Copyright (c) 2000 The Regents of the University of Michigan',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-sunrpc/auth_gss.h')

    def test_ics_kernel_headers_original_linux_sunrpc_clnt_h(self):
        expected = [
            u'Copyright (c) 1995, 1996, Olaf Kirch <okir@monad.swb.de>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-sunrpc/clnt.h')

    def test_ics_kernel_headers_original_linux_sunrpc_gss_asn1_h(self):
        expected = [
            u'Copyright (c) 2000 The Regents of the University of Michigan.',
            u'Copyright 1995 by the Massachusetts Institute of Technology.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-sunrpc/gss_asn1.h')

    def test_ics_kernel_headers_original_linux_sunrpc_gss_err_h(self):
        expected = [
            u'Copyright (c) 2002 The Regents of the University of Michigan.',
            u'Copyright 1993 by OpenVision Technologies, Inc.',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-sunrpc/gss_err.h')

    def test_ics_kernel_headers_original_linux_sunrpc_timer_h(self):
        expected = [
            u'Copyright (c) 2002 Trond Myklebust <trond.myklebust@fys.uio.no>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-linux-sunrpc/timer.h')

    def test_ics_kernel_headers_original_sound_asound_h(self):
        expected = [
            u'Copyright (c) 1994-2003 by Jaroslav Kysela <perex@perex.cz> , Abramo Bagnara <abramo@alsa-project.org>',
        ]
        check_detection(expected, 'ics/kernel-headers-original-sound/asound.h')

    def test_ics_libffi_aclocal_m4(self):
        expected = [
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007 Free Software Foundation, Inc.',
            u'Copyright (c) 2002, 2003, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1997, 2000, 2001, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1998, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2002, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1999, 2000, 2001, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1997, 1999, 2000, 2001, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2002, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 2000, 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/libffi/aclocal.m4')

    def test_ics_libffi_android_mk(self):
        expected = [
            u'Copyright 2007 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/libffi/Android.mk')

    def test_ics_libffi_configure(self):
        expected = [
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007 Free Software Foundation, Inc.',
            u'Copyright (c) 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/libffi/configure')

    def test_ics_libffi_depcomp(self):
        expected = [
            u'Copyright (c) 1999, 2000, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/libffi/depcomp')

    def test_ics_libffi_license(self):
        expected = [
            u'Copyright (c) 1996-2008 Red Hat, Inc and others.',
        ]
        check_detection(expected, 'ics/libffi/LICENSE')

    def test_ics_libffi_ltcf_c_sh(self):
        expected = [
            u'Copyright (c) 1996-2000, 2001 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/libffi/ltcf-c.sh')

    def test_ics_libffi_ltcf_cxx_sh(self):
        expected = [
            u'Copyright (c) 1996-1999, 2000, 2001, 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/libffi/ltcf-cxx.sh')

    def test_ics_libffi_ltconfig(self):
        expected = [
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001 Free Software Foundation, Inc.',
            u'Copyright (c) 1996-2000 Free Software Foundation, Inc.',
            u'Copyright (c) 1999-2000 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/libffi/ltconfig')

    def test_ics_libffi_ltmain_sh(self):
        expected = [
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2003, 2004, 2005, 2006, 2007 Free Software Foundation, Inc.',
            u'Copyright (c) 2007 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/libffi/ltmain.sh')

    def test_ics_libffi_missing(self):
        expected = [
            u'Copyright (c) 1996, 1997, 1999, 2000, 2002, 2003, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/libffi/missing')

    def test_ics_libffi_darwin_x86_ffi_h(self):
        expected = [
            u'Copyright (c) 1996-2003, 2007, 2008 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/libffi-darwin-x86/ffi.h')

    def test_ics_libffi_darwin_x86_ffitarget_h(self):
        expected = [
            u'Copyright (c) 1996-2003 Red Hat, Inc.',
            u'Copyright (c) 2008 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/libffi-darwin-x86/ffitarget.h')

    def test_ics_libffi_doc_libffi_texi(self):
        expected = [
            u'Copyright 2008 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/libffi-doc/libffi.texi')

    def test_ics_libffi_include_ffi_h_in(self):
        expected = [
            u'Copyright (c) 1996-2003, 2007, 2008 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/libffi-include/ffi.h.in')

    def test_ics_libffi_include_ffi_common_h(self):
        expected = [
            u'Copyright (c) 1996 Red Hat, Inc.',
            u'Copyright (c) 2007 Free Software Foundation, Inc',
        ]
        check_detection(expected, 'ics/libffi-include/ffi_common.h')

    def test_ics_libffi_src_closures_c(self):
        expected = [
            u'Copyright (c) 2007 Red Hat, Inc.',
            u'Copyright (c) 2007 Free Software Foundation, Inc',
        ]
        check_detection(expected, 'ics/libffi-src/closures.c')

    def test_ics_libffi_src_debug_c(self):
        expected = [
            u'Copyright (c) 1996 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/libffi-src/debug.c')

    def test_ics_libffi_src_java_raw_api_c(self):
        expected = [
            u'Copyright (c) 1999, 2007, 2008 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/libffi-src/java_raw_api.c')

    def test_ics_libffi_src_prep_cif_c(self):
        expected = [
            u'Copyright (c) 1996, 1998, 2007 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/libffi-src/prep_cif.c')

    def test_ics_libffi_src_raw_api_c(self):
        expected = [
            u'Copyright (c) 1999, 2008 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/libffi-src/raw_api.c')

    def test_ics_libffi_src_types_c(self):
        expected = [
            u'Copyright (c) 1996, 1998 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/libffi-src/types.c')

    def test_ics_libffi_src_alpha_ffi_c(self):
        expected = [
            u'Copyright (c) 1998, 2001, 2007, 2008 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/libffi-src-alpha/ffi.c')

    def test_ics_libffi_src_alpha_ffitarget_h(self):
        expected = [
            u'Copyright (c) 1996-2003 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/libffi-src-alpha/ffitarget.h')

    def test_ics_libffi_src_arm_ffi_c(self):
        expected = [
            u'Copyright (c) 1998, 2008 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/libffi-src-arm/ffi.c')

    def test_ics_libffi_src_cris_ffi_c(self):
        expected = [
            u'Copyright (c) 1998 Cygnus Solutions',
            u'Copyright (c) 2004 Simon Posnjak',
            u'Copyright (c) 2005 Axis Communications AB',
            u'Copyright (c) 2007 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/libffi-src-cris/ffi.c')

    def test_ics_libffi_src_frv_ffi_c(self):
        expected = [
            u'Copyright (c) 2004 Anthony Green',
            u'Copyright (c) 2007 Free Software Foundation, Inc.',
            u'Copyright (c) 2008 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/libffi-src-frv/ffi.c')

    def test_ics_libffi_src_frv_ffitarget_h(self):
        expected = [
            u'Copyright (c) 1996-2004 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/libffi-src-frv/ffitarget.h')

    def test_ics_libffi_src_ia64_ffi_c(self):
        expected = [
            u'Copyright (c) 1998, 2007, 2008 Red Hat, Inc.',
            u'Copyright (c) 2000 Hewlett Packard Company',
        ]
        check_detection(expected, 'ics/libffi-src-ia64/ffi.c')

    def test_ics_libffi_src_ia64_ia64_flags_h(self):
        expected = [
            u'Copyright (c) 2000 Hewlett Packard Company',
        ]
        check_detection(expected, 'ics/libffi-src-ia64/ia64_flags.h')

    def test_ics_libffi_src_m32r_ffi_c(self):
        expected = [
            u'Copyright (c) 2004 Renesas Technology',
            u'Copyright (c) 2008 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/libffi-src-m32r/ffi.c')

    def test_ics_libffi_src_m32r_ffitarget_h(self):
        expected = [
            u'Copyright (c) 2004 Renesas Technology.',
        ]
        check_detection(expected, 'ics/libffi-src-m32r/ffitarget.h')

    def test_ics_libffi_src_mips_ffi_c(self):
        expected = [
            u'Copyright (c) 1996, 2007, 2008 Red Hat, Inc.',
            u'Copyright (c) 2008 David Daney',
        ]
        check_detection(expected, 'ics/libffi-src-mips/ffi.c')

    def test_ics_libffi_src_pa_ffi_c(self):
        expected = [
            u'(c) 2003-2004 Randolph Chung <tausq@debian.org>',
            u'(c) 2008 Red Hat, Inc.',
            u'(c) 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/libffi-src-pa/ffi.c')

    def test_ics_libffi_src_powerpc_asm_h(self):
        expected = [
            u'Copyright (c) 1998 Geoffrey Keating',
        ]
        check_detection(expected, 'ics/libffi-src-powerpc/asm.h')

    def test_ics_libffi_src_powerpc_ffi_c(self):
        expected = [
            u'Copyright (c) 1998 Geoffrey Keating',
            u'Copyright (c) 2007 Free Software Foundation, Inc',
            u'Copyright (c) 2008 Red Hat, Inc',
        ]
        check_detection(expected, 'ics/libffi-src-powerpc/ffi.c')

    def test_ics_libffi_src_powerpc_ffi_darwin_c(self):
        expected = [
            u'Copyright (c) 1998 Geoffrey Keating',
            u'Copyright (c) 2001 John Hornkvist',
            u'Copyright (c) 2002, 2006, 2007 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/libffi-src-powerpc/ffi_darwin.c')

    def test_ics_libffi_src_powerpc_ffitarget_h(self):
        expected = [
            u'Copyright (c) 1996-2003 Red Hat, Inc.',
            u'Copyright (c) 2007 Free Software Foundation, Inc',
        ]
        check_detection(expected, 'ics/libffi-src-powerpc/ffitarget.h')

    def test_ics_libffi_src_s390_ffi_c(self):
        expected = [
            u'Copyright (c) 2000, 2007 Software AG',
            u'Copyright (c) 2008 Red Hat, Inc',
        ]
        check_detection(expected, 'ics/libffi-src-s390/ffi.c')

    def test_ics_libffi_src_sh_ffi_c(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007, 2008 Kaz Kojima',
            u'Copyright (c) 2008 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/libffi-src-sh/ffi.c')

    def test_ics_libffi_src_sh64_ffi_c(self):
        expected = [
            u'Copyright (c) 2003, 2004 Kaz Kojima',
            u'Copyright (c) 2008 Anthony Green',
        ]
        check_detection(expected, 'ics/libffi-src-sh64/ffi.c')

    def test_ics_libffi_src_sparc_ffi_c(self):
        expected = [
            u'Copyright (c) 1996, 2003, 2004, 2007, 2008 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/libffi-src-sparc/ffi.c')

    def test_ics_libffi_src_x86_ffi_c(self):
        expected = [
            u'Copyright (c) 1996, 1998, 1999, 2001, 2007, 2008 Red Hat, Inc.',
            u'Copyright (c) 2002 Ranjit Mathew',
            u'Copyright (c) 2002 Bo Thorsen',
            u'Copyright (c) 2002 Roger Sayle',
            u'Copyright (c) 2008 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/libffi-src-x86/ffi.c')

    def test_ics_libffi_src_x86_ffi64_c(self):
        expected = [
            u'Copyright (c) 2002, 2007 Bo Thorsen <bo@suse.de>',
            u'Copyright (c) 2008 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/libffi-src-x86/ffi64.c')

    def test_ics_libffi_testsuite_run_all_tests(self):
        expected = [
            u'Copyright 2009 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/libffi-testsuite/run-all-tests')

    def test_ics_libffi_testsuite_lib_libffi_dg_exp(self):
        expected = [
            u'Copyright (c) 2003, 2005, 2008 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/libffi-testsuite-lib/libffi-dg.exp')

    def test_ics_libffi_testsuite_lib_target_libpath_exp(self):
        expected = [
            u'Copyright (c) 2004, 2005, 2007 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/libffi-testsuite-lib/target-libpath.exp')

    def test_ics_libffi_testsuite_lib_wrapper_exp(self):
        expected = [
            u'Copyright (c) 2004, 2007 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/libffi-testsuite-lib/wrapper.exp')

    def test_ics_libgsm_changelog(self):
        expected = [
            u'Copyright 1992 by Jutta Degener and Carsten Bormann, Technische Universitaet Berlin.',
        ]
        check_detection(expected, 'ics/libgsm/ChangeLog')

    def test_ics_libgsm_notice(self):
        expected = [
            u'Copyright 1992, 1993, 1994 by Jutta Degener and Carsten Bormann, Technische Universitaet Berlin',
        ]
        check_detection(expected, 'ics/libgsm/NOTICE')

    def test_ics_libgsm_readme(self):
        expected = [
            u'Copyright 1992 by Jutta Degener and Carsten Bormann, Technische Universitaet Berlin.',
        ]
        check_detection(expected, 'ics/libgsm/README')

    def test_ics_libgsm_inc_config_h(self):
        expected = [
            u'Copyright 1992 by Jutta Degener and Carsten Bormann, Technische Universitaet Berlin.',
        ]
        check_detection(expected, 'ics/libgsm-inc/config.h')

    def test_ics_libgsm_man_gsm_3(self):
        expected = [
            u'Copyright 1992 by Jutta Degener and Carsten Bormann, Technische Universitaet Berlin.',
        ]
        check_detection(expected, 'ics/libgsm-man/gsm.3')

    def test_ics_libgsm_man_gsm_option_3(self):
        expected = [
            u'Copyright 1992-1995 by Jutta Degener and Carsten Bormann, Technische Universitaet Berlin.',
        ]
        check_detection(expected, 'ics/libgsm-man/gsm_option.3')

    def test_ics_liblzf_license(self):
        expected = [
            u'Copyright (c) 2000-2009 Marc Alexander Lehmann <schmorp@schmorp.de>',
        ]
        check_detection(expected, 'ics/liblzf/LICENSE')

    def test_ics_liblzf_lzf_c(self):
        expected = [
            u'Copyright (c) 2006 Stefan Traby <stefan@hello-penguin.com>',
        ]
        check_detection(expected, 'ics/liblzf/lzf.c')

    def test_ics_liblzf_lzf_h(self):
        expected = [
            u'Copyright (c) 2000-2008 Marc Alexander Lehmann <schmorp@schmorp.de>',
        ]
        check_detection(expected, 'ics/liblzf/lzf.h')

    def test_ics_liblzf_lzf_c_c(self):
        expected = [
            u'Copyright (c) 2000-2010 Marc Alexander Lehmann <schmorp@schmorp.de>',
        ]
        check_detection(expected, 'ics/liblzf/lzf_c.c')

    def test_ics_liblzf_lzfp_h(self):
        expected = [
            u'Copyright (c) 2000-2007 Marc Alexander Lehmann <schmorp@schmorp.de>',
        ]
        check_detection(expected, 'ics/liblzf/lzfP.h')

    def test_ics_liblzf_cs_clzf_cs(self):
        expected = [
            u'Copyright (c) 2005 Oren J. Maurice <oymaurice@hazorea.org.il>',
        ]
        check_detection(expected, 'ics/liblzf-cs/CLZF.cs')

    def test_ics_libnfc_nxp_inc_nfc_custom_config_h(self):
        expected = [
            u'Copyright (c) 2010 NXP Semiconductors',
        ]
        check_detection(expected, 'ics/libnfc-nxp-inc/nfc_custom_config.h')

    def test_ics_libnl_headers_netlink_generic_h(self):
        expected = [
            u'Copyright (c) 2003-2006 Thomas Graf <tgraf@suug.ch>',
        ]
        check_detection(expected, 'ics/libnl-headers/netlink-generic.h')

    def test_ics_libnl_headers_netlink_local_h(self):
        expected = [
            u'Copyright (c) 2003-2008 Thomas Graf <tgraf@suug.ch>',
        ]
        check_detection(expected, 'ics/libnl-headers/netlink-local.h')

    def test_ics_libnl_headers_netlink_errno_h(self):
        expected = [
            u'Copyright (c) 2008 Thomas Graf <tgraf@suug.ch>',
        ]
        check_detection(expected, 'ics/libnl-headers-netlink/errno.h')

    def test_ics_libnl_headers_netlink_object_api_h(self):
        expected = [
            u'Copyright (c) 2003-2007 Thomas Graf <tgraf@suug.ch>',
        ]
        check_detection(expected, 'ics/libnl-headers-netlink/object-api.h')

    def test_ics_libnl_headers_netlink_cli_utils_h(self):
        expected = [
            u'Copyright (c) 2003-2009 Thomas Graf <tgraf@suug.ch>',
        ]
        check_detection(expected, 'ics/libnl-headers-netlink-cli/utils.h')

    def test_ics_libnl_headers_netlink_netfilter_ct_h(self):
        expected = [
            u'Copyright (c) 2003-2008 Thomas Graf <tgraf@suug.ch>',
            u'Copyright (c) 2007 Philip Craig <philipc@snapgear.com>',
            u'Copyright (c) 2007 Secure Computing Corporation',
        ]
        check_detection(expected, 'ics/libnl-headers-netlink-netfilter/ct.h')

    def test_ics_libnl_headers_netlink_route_addr_h(self):
        expected = [
            u'Copyright (c) 2003-2008 Thomas Graf <tgraf@suug.ch>',
            u'Copyright (c) 2003-2006 Baruch Even <baruch@ev-en.org> , Mediatrix Telecom, inc. <ericb@mediatrix.com>',
        ]
        check_detection(expected, 'ics/libnl-headers-netlink-route/addr.h')

    def test_ics_libpcap_aclocal_m4_trail_name(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997, 1998 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/aclocal.m4')

    def test_ics_libpcap_atmuni31_h(self):
        expected = [
            u'Copyright (c) 1997 Yen Yen Lim and North Dakota State University',
        ]
        check_detection(expected, 'ics/libpcap/atmuni31.h')

    def test_ics_libpcap_bpf_dump_c(self):
        expected = [
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/bpf_dump.c')

    def test_ics_libpcap_bpf_image_c(self):
        expected = [
            u'Copyright (c) 1990, 1991, 1992, 1994, 1995, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/bpf_image.c')

    def test_ics_libpcap_config_guess(self):
        expected = [
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003 Free Software Foundation, Inc.',
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/libpcap/config.guess')

    def test_ics_libpcap_configure_in_trail_name(self):
        expected = [
            u'Copyright (c) 1994, 1995, 1996, 1997 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/configure.in')

    def test_ics_libpcap_etherent_c(self):
        expected = [
            u'Copyright (c) 1990, 1993, 1994, 1995, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/etherent.c')

    def test_ics_libpcap_ethertype_h(self):
        expected = [
            u'Copyright (c) 1993, 1994, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/ethertype.h')

    def test_ics_libpcap_fad_getad_c(self):
        expected = [
            u'Copyright (c) 1994, 1995, 1996, 1997, 1998 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/fad-getad.c')

    def test_ics_libpcap_fad_win32_c(self):
        expected = [
            u'Copyright (c) 2002 - 2005 NetGroup, Politecnico di Torino (Italy)',
            u'Copyright (c) 2005 - 2006 CACE Technologies, Davis (California)',
        ]
        check_detection(expected, 'ics/libpcap/fad-win32.c')

    def test_ics_libpcap_gencode_c(self):
        expected = [
            u'Copyright (c) 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/gencode.c')

    def test_ics_libpcap_gencode_h(self):
        expected = [
            u'Copyright (c) 1990, 1991, 1992, 1993, 1994, 1995, 1996 The Regents of the University of California.',
            u'Copyright (c) 1997 Yen Yen Lim and North Dakota State University',
        ]
        check_detection(expected, 'ics/libpcap/gencode.h')

    def test_ics_libpcap_grammar_c(self):
        expected = [
            u'Copyright (c) 1984, 1989, 1990, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/grammar.c')

    def test_ics_libpcap_llc_h(self):
        expected = [
            u'Copyright (c) 1993, 1994, 1997 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/llc.h')

    def test_ics_libpcap_makefile_in(self):
        expected = [
            u'Copyright (c) 1993, 1994, 1995, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/Makefile.in')

    def test_ics_libpcap_mkdep(self):
        expected = [
            u'Copyright (c) 1994, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/mkdep')

    def test_ics_libpcap_nlpid_h(self):
        expected = [
            u'Copyright (c) 1996 Juniper Networks, Inc.',
        ]
        check_detection(expected, 'ics/libpcap/nlpid.h')

    def test_ics_libpcap_optimize_c(self):
        expected = [
            u'Copyright (c) 1988, 1989, 1990, 1991, 1993, 1994, 1995, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/optimize.c')

    def test_ics_libpcap_pcap_3_trail_name(self):
        expected = [
            u'Copyright (c) 1994, 1996, 1997 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/pcap.3')

    def test_ics_libpcap_pcap_c(self):
        expected = [
            u'Copyright (c) 1993, 1994, 1995, 1996, 1997, 1998 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/pcap.c')

    def test_ics_libpcap_pcap_h(self):
        expected = [
            u'Copyright (c) 1993, 1994, 1995, 1996, 1997 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/pcap.h')

    def test_ics_libpcap_pcap_bpf_c(self):
        expected = [
            u'Copyright (c) 1993, 1994, 1995, 1996, 1998 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/pcap-bpf.c')

    def test_ics_libpcap_pcap_bpf_h(self):
        expected = [
            u'Copyright (c) 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/pcap-bpf.h')

    def test_ics_libpcap_pcap_dlpi_c(self):
        expected = [
            u'Copyright (c) 1993, 1994, 1995, 1996, 1997 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/pcap-dlpi.c')

    def test_ics_libpcap_pcap_int_h(self):
        expected = [
            u'Copyright (c) 1994, 1995, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/pcap-int.h')

    def test_ics_libpcap_pcap_linux_c(self):
        expected = [
            u'Copyright (c) 2000 Torsten Landschoff <torsten@debian.org> Sebastian Krahmer <krahmer@cs.uni-potsdam.de>',
        ]
        check_detection(expected, 'ics/libpcap/pcap-linux.c')

    def test_ics_libpcap_pcap_namedb_h(self):
        expected = [
            u'Copyright (c) 1994, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/pcap-namedb.h')

    def test_ics_libpcap_pcap_nit_c(self):
        expected = [
            u'Copyright (c) 1990, 1991, 1992, 1993, 1994, 1995, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/pcap-nit.c')

    def test_ics_libpcap_pcap_nit_h(self):
        expected = [
            u'Copyright (c) 1990, 1994 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/pcap-nit.h')

    def test_ics_libpcap_pcap_null_c(self):
        expected = [
            u'Copyright (c) 1994, 1995, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/pcap-null.c')

    def test_ics_libpcap_pcap_stdinc_h_trail_name(self):
        expected = [
            u'Copyright (c) 2002 - 2003 NetGroup, Politecnico di Torino (Italy)',
        ]
        check_detection(expected, 'ics/libpcap/pcap-stdinc.h')

    def test_ics_libpcap_pcap_win32_c(self):
        expected = [
            u'Copyright (c) 1999 - 2005 NetGroup, Politecnico di Torino (Italy)',
            u'Copyright (c) 2005 - 2007 CACE Technologies, Davis (California)',
        ]
        check_detection(expected, 'ics/libpcap/pcap-win32.c')

    def test_ics_libpcap_ppp_h(self):
        expected = [
            u'Copyright 1989 by Carnegie Mellon.',
        ]
        check_detection(expected, 'ics/libpcap/ppp.h')

    def test_ics_libpcap_scanner_c(self):
        expected = [
            u'Copyright (c) 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap/scanner.c')

    def test_ics_libpcap_tokdefs_h(self):
        expected = [
            u'Copyright (c) 1984, 1989, 1990, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/libpcap/tokdefs.h')

    def test_ics_libpcap_doc_pcap_html(self):
        expected = [
            u'Copyright (c) The Internet Society (2004).',
            u'Copyright (c) The Internet Society (2004).',
        ]
        check_detection(expected, 'ics/libpcap-doc/pcap.html')

    def test_ics_libpcap_doc_pcap_txt(self):
        expected = [
            u'Copyright (c) The Internet Society (2004).',
            u'Full Copyright Statement',
            u'Copyright (c) The Internet Society (2004).',
        ]
        check_detection(expected, 'ics/libpcap-doc/pcap.txt')

    def test_ics_libpcap_lbl_os_sunos4_h(self):
        expected = [
            u'Copyright (c) 1989, 1990, 1993, 1994, 1995, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap-lbl/os-sunos4.h')

    def test_ics_libpcap_lbl_os_ultrix4_h(self):
        expected = [
            u'Copyright (c) 1990, 1993, 1994, 1995, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/libpcap-lbl/os-ultrix4.h')

    def test_ics_libpcap_missing_snprintf_c(self):
        expected = [
            u'Copyright (c) 1995-1999 Kungliga Tekniska Hogskolan (Royal Institute of Technology, Stockholm, Sweden).',
        ]
        check_detection(expected, 'ics/libpcap-missing/snprintf.c')

    def test_ics_libvpx_args_c(self):
        expected = [
            u'Copyright (c) 2010 The WebM project',
        ]
        check_detection(expected, 'ics/libvpx/args.c')

    def test_ics_libvpx_docs_mk(self):
        expected = [
            u'Copyright (c) 2010 The WebM project',
        ]
        check_detection(expected, 'ics/libvpx/docs.mk')

    def test_ics_libvpx_license(self):
        expected = [
            u'Copyright (c) 2010, Google Inc.',
        ]
        check_detection(expected, 'ics/libvpx/LICENSE')

    def test_ics_libvpx_y4minput_c(self):
        expected = [
            u'Copyright (c) 2010 The WebM project',
            u'Copyright (c) 2002-2010 The Xiph.Org Foundation and contributors.',
        ]
        check_detection(expected, 'ics/libvpx/y4minput.c')

    def test_ics_libvpx_build_x86_msvs_obj_int_extract_bat(self):
        expected = [
            u'Copyright (c) 2011 The WebM project',
        ]
        check_detection(expected, 'ics/libvpx-build-x86-msvs/obj_int_extract.bat')

    def test_ics_libvpx_examples_includes_asciimathphp_2_0_htmlmathml_js(self):
        expected = [
            u'(c) Peter Jipsen',
        ]
        check_detection(expected, 'ics/libvpx-examples-includes-ASCIIMathPHP-2.0/htmlMathML.js')

    def test_ics_libvpx_examples_includes_geshi_docs_geshi_doc_html(self):
        expected = [
            u'(c) 2004 - 2007 Nigel McNie, 2007 - 2008 Benny Baumann (http://qbnz.com/highlighter/ and http://geshi.org/)',
            u'(c) 2004 - 2007 Nigel McNie, 2007 - 2008 Benny Baumann (http://qbnz.com/highlighter/ and http://geshi.org/)',
            u'(c) 2004 - 2007 Nigel McNie, 2007 - 2008 Benny Baumann (http://qbnz.com/highlighter/ and http://geshi.org/)',
            u'(c) 2004 - 2007 Nigel McNie, 2007 - 2008 Benny Baumann (http://qbnz.com/highlighter/ and http://geshi.org/)',
            u'(c) 2004 - 2007 Nigel McNie, 2007 - 2008 Benny Baumann (http://qbnz.com/highlighter/ and http://geshi.org/)',
            u'Copyright (c) 2004 Nigel McNie',
            u"Copyright (c) 2008 &lt name&gt (&lt website URL&gt ) <span class coMULTI'> &nbsp",
        ]
        check_detection(expected, 'ics/libvpx-examples-includes-geshi-docs/geshi-doc.html')

    def test_ics_libvpx_examples_includes_geshi_docs_geshi_doc_txt(self):
        expected = [
            u'Copyright (c) 2004 - 2007 Nigel McNie, 2007 - 2008 Benny Baumann Email nigel@geshi.org',
            u'Copyright (c) 2004 Nigel McNie',
            u'Copyright (c) 2004 ( )',
        ]
        check_detection(expected, 'ics/libvpx-examples-includes-geshi-docs/geshi-doc.txt')

    @expectedFailure
    def test_ics_libvpx_examples_includes_geshi_docs_geshi_doc_txt_trail_email_trail_url_misc(self):
        expected = [
            u'Copyright (c) 2004 - 2007 Nigel McNie, 2007 - 2008 Benny Baumann Email nigel@geshi.org, BenBE@omorphia.de',
            u'Copyright: (c) 2004 Nigel McNie (http://qbnz.com/highlighter/)',
            u'Copyright: (c) 2004 <name> (<website URL>)',
        ]
        check_detection(expected, 'ics/libvpx-examples-includes-geshi-docs/geshi-doc.txt')

    def test_ics_libvpx_examples_includes_geshi_docs_phpdoc_ini(self):
        expected = [
            u'Copyright 2002, Greg Beaver <cellog@users.sourceforge.net>',
        ]
        check_detection(expected, 'ics/libvpx-examples-includes-geshi-docs/phpdoc.ini')

    def test_ics_libvpx_examples_includes_html_toc_0_91_toc_pod(self):
        expected = [
            u'Copyright (c) 2001 Freddy Vulto.',
        ]
        check_detection(expected, 'ics/libvpx-examples-includes-HTML-Toc-0.91/Toc.pod')

    def test_ics_libvpx_examples_includes_php_markdown_extra_1_2_3_license_text(self):
        expected = [
            u'Copyright (c) 2004-2008 Michel Fortin',
            u'Copyright (c) 2003-2006 John Gruber',
        ]
        check_detection(expected, 'ics/libvpx-examples-includes-PHP-Markdown-Extra-1.2.3/License.text')

    def test_ics_libvpx_examples_includes_php_markdown_extra_1_2_3_markdown_php(self):
        expected = [
            u'Copyright (c) 2004-2008 Michel Fortin',
            u'Copyright (c) 2004-2006 John Gruber',
            u'Copyright (c) 2004-2008 Michel Fortin',
            u'Copyright (c) 2003-2006 John Gruber',
        ]
        check_detection(expected, 'ics/libvpx-examples-includes-PHP-Markdown-Extra-1.2.3/markdown.php')

    def test_ics_libvpx_examples_includes_php_markdown_extra_1_2_3_php_markdown_extra_readme_text(self):
        expected = [
            u'Copyright (c) 2004-2005 Michel Fortin',
            u'Copyright (c) 2003-2005 John Gruber',
        ]
        check_detection(expected, 'ics/libvpx-examples-includes-PHP-Markdown-Extra-1.2.3/PHP Markdown Extra Readme.text')

    def test_ics_libvpx_examples_includes_php_smartypants_1_5_1e_php_smartypants_readme_txt(self):
        expected = [
            u'Copyright (c) 2005 Michel Fortin',
            u'Copyright (c) 2003-2004 John Gruber',
        ]
        check_detection(expected, 'ics/libvpx-examples-includes-PHP-SmartyPants-1.5.1e/PHP SmartyPants Readme.txt')

    def test_ics_libvpx_examples_includes_php_smartypants_1_5_1e_smartypants_php(self):
        expected = [
            u'Copyright (c) 2003-2004 John Gruber',
            u'Copyright (c) 2004-2005 Michel Fortin',
            u'Copyright (c) 2003 John Gruber',
            u'Copyright (c) 2004-2005 Michel Fortin',
        ]
        check_detection(expected, 'ics/libvpx-examples-includes-PHP-SmartyPants-1.5.1e/smartypants.php')

    def test_ics_libvpx_libmkv_ebmlids_h(self):
        expected = [
            u'Copyright (c) 2010 The WebM project',
        ]
        check_detection(expected, 'ics/libvpx-libmkv/EbmlIDs.h')

    def test_ics_libvpx_nestegg_license(self):
        expected = [
            u'Copyright (c) 2010 Mozilla Foundation',
        ]
        check_detection(expected, 'ics/libvpx-nestegg/LICENSE')

    def test_ics_libvpx_nestegg_halloc_halloc_h(self):
        expected = [
            u'Copyright (c) 2004-2010 Alex Pankratov.',
        ]
        check_detection(expected, 'ics/libvpx-nestegg-halloc/halloc.h')

    def test_ics_libvpx_nestegg_halloc_readme(self):
        expected = [
            u'Copyright (c) 2004-2010, Alex Pankratov (ap@swapped.cc).',
        ]
        check_detection(expected, 'ics/libvpx-nestegg-halloc/README')

    def test_ics_libvpx_nestegg_halloc_src_halloc_c(self):
        expected = [
            u'Copyright (c) 2004i-2010 Alex Pankratov.',
        ]
        check_detection(expected, 'ics/libvpx-nestegg-halloc-src/halloc.c')

    def test_ics_libvpx_nestegg_include_nestegg_nestegg_h(self):
        expected = [
            u'Copyright (c) 2010 Mozilla Foundation',
        ]
        check_detection(expected, 'ics/libvpx-nestegg-include-nestegg/nestegg.h')

    def test_ics_libvpx_nestegg_m4_pkg_m4(self):
        expected = [
            u'Copyright (c) 2004 Scott James Remnant <scott@netsplit.com>',
        ]
        check_detection(expected, 'ics/libvpx-nestegg-m4/pkg.m4')

    def test_ics_libvpx_vp8_common_asm_com_offsets_c(self):
        expected = [
            u'Copyright (c) 2011 The WebM project',
        ]
        check_detection(expected, 'ics/libvpx-vp8-common/asm_com_offsets.c')

    def test_ics_libxml2_dict_c(self):
        expected = [
            u'Copyright (c) 2003 Daniel Veillard.',
        ]
        check_detection(expected, 'ics/libxml2/dict.c')

    def test_ics_libxml2_hash_c(self):
        expected = [
            u'Copyright (c) 2000 Bjorn Reese and Daniel Veillard.',
        ]
        check_detection(expected, 'ics/libxml2/hash.c')

    def test_ics_libxml2_list_c(self):
        expected = [
            u'Copyright (c) 2000 Gary Pennington and Daniel Veillard.',
        ]
        check_detection(expected, 'ics/libxml2/list.c')

    def test_ics_libxml2_notice(self):
        expected = [
            u'Copyright (c) 1998-2003 Daniel Veillard.',
        ]
        check_detection(expected, 'ics/libxml2/NOTICE')

    def test_ics_libxml2_trio_c(self):
        expected = [
            u'Copyright (c) 1998 Bjorn Reese and Daniel Stenberg.',
        ]
        check_detection(expected, 'ics/libxml2/trio.c')

    def test_ics_libxml2_triodef_h(self):
        expected = [
            u'Copyright (c) 2001 Bjorn Reese <breese@users.sourceforge.net>',
        ]
        check_detection(expected, 'ics/libxml2/triodef.h')

    def test_ics_libxml2_triop_h(self):
        expected = [
            u'Copyright (c) 2000 Bjorn Reese and Daniel Stenberg.',
        ]
        check_detection(expected, 'ics/libxml2/triop.h')

    def test_ics_libxml2_triostr_c(self):
        expected = [
            u'Copyright (c) 2001 Bjorn Reese and Daniel Stenberg.',
        ]
        check_detection(expected, 'ics/libxml2/triostr.c')

    def test_ics_libxslt_copyright(self):
        expected = [
            u'Copyright (c) 2001-2002 Daniel Veillard.',
            u'Copyright (c) 2001-2002 Thomas Broyer, Charlie Bozeman and Daniel Veillard.',
        ]
        check_detection(expected, 'ics/libxslt/Copyright')

    def test_ics_lohit_fonts_notice(self):
        expected = [
            u'Copyright 2011 Lohit Fonts Project contributors',
        ]
        check_detection(expected, 'ics/lohit-fonts/NOTICE')

    @expectedFailure
    def test_ics_lohit_fonts_notice_trail_url(self):
        expected = [
            u'Copyright 2011 Lohit Fonts Project contributors <http://fedorahosted.org/lohit>',
        ]
        check_detection(expected, 'ics/lohit-fonts/NOTICE')

    def test_ics_lohit_fonts_lohit_bengali_ttf_copyright(self):
        expected = [
            u'Copyright 2011 Lohit Fonts Project contributors.',
        ]
        check_detection(expected, 'ics/lohit-fonts-lohit-bengali-ttf/COPYRIGHT')

    @expectedFailure
    def test_ics_lohit_fonts_lohit_bengali_ttf_copyright_trail_url(self):
        expected = [
            u'Copyright 2011 Lohit Fonts Project contributors. <http://fedorahosted.org/lohit>',
        ]
        check_detection(expected, 'ics/lohit-fonts-lohit-bengali-ttf/COPYRIGHT')

    def test_ics_markdown_notice(self):
        expected = [
            u'Copyright 2007, 2008 The Python Markdown Project',
            u'Copyright 2004, 2005, 2006 Yuri Takhteyev',
            u'Copyright 2004 Manfred Stienstra',
        ]
        check_detection(expected, 'ics/markdown/NOTICE')

    def test_ics_markdown_bin_markdown(self):
        expected = [
            u'Copyright 2007, 2008 The Python Markdown Project',
            u'Copyright 2004, 2005, 2006 Yuri Takhteyev',
            u'Copyright 2004 Manfred Stienstra',
        ]
        check_detection(expected, 'ics/markdown-bin/markdown')

    def test_ics_markdown_markdown_html4_py(self):
        expected = [
            u'Copyright (c) 1999-2007 by Fredrik Lundh.',
            u'Copyright (c) 1999-2007 by Fredrik Lundh',
        ]
        check_detection(expected, 'ics/markdown-markdown/html4.py')

    def test_ics_markdown_markdown_extensions_abbr_py(self):
        expected = [
            u'Copyright 2007-2008 Waylan Limberg (http://achinghead.com/) Seemant Kulleen (http://www.kulleen.org/)',
        ]
        check_detection(expected, 'ics/markdown-markdown-extensions/abbr.py')

    def test_ics_markdown_markdown_extensions_codehilite_py_trail_url(self):
        expected = [
            u'Copyright 2006-2008 Waylan Limberg',
        ]
        check_detection(expected, 'ics/markdown-markdown-extensions/codehilite.py')

    def test_ics_markdown_markdown_extensions_def_list_py_trail_url(self):
        expected = [
            u'Copyright 2008 - Waylan Limberg (http://achinghead.com)',
        ]
        check_detection(expected, 'ics/markdown-markdown-extensions/def_list.py')

    def test_ics_markdown_markdown_extensions_html_tidy_py_trail_url(self):
        expected = [
            u'Copyright (c) 2008 Waylan Limberg (http://achinghead.com)',
        ]
        check_detection(expected, 'ics/markdown-markdown-extensions/html_tidy.py')

    def test_ics_markdown_markdown_extensions_tables_py_trail_url(self):
        expected = [
            u'Copyright 2009 - Waylan Limberg (http://achinghead.com)',
        ]
        check_detection(expected, 'ics/markdown-markdown-extensions/tables.py')

    def test_ics_markdown_markdown_extensions_toc_py(self):
        expected = [
            u'(c) 2008 Jack Miller (http://codezen.org)',
        ]
        check_detection(expected, 'ics/markdown-markdown-extensions/toc.py')

    def test_ics_mesa3d_notice(self):
        expected = [
            u'Copyright (c) 1999-2008 Brian Paul',
            u'Copyright (c) 2008-1010 Intel Corporation',
            u'Copyright (c) 2007-2010 VMware, Inc.',
            u'Copyright (c) 2010 Luca Barbieri',
            u'Copyright (c) 2006 Alexander Chemeris',
            u'Copyright 2007,2010,2011 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/mesa3d/NOTICE')

    def test_ics_mesa3d_docs_license_html(self):
        expected = [
            u'copyrighted by Mark Kilgard',
            u'Copyright (c) 1999-2007 Brian Paul',
        ]
        check_detection(expected, 'ics/mesa3d-docs/license.html')

    def test_ics_mesa3d_docs_subset_a_html(self):
        expected = [
            u'Copyright (c) 2002-2003 by Tungsten Graphics, Inc., Cedar Park, Texas.',
        ]
        check_detection(expected, 'ics/mesa3d-docs/subset-A.html')

    def test_ics_mesa3d_include_c99_inttypes_h(self):
        expected = [
            u'Copyright (c) 2006 Alexander Chemeris',
        ]
        check_detection(expected, 'ics/mesa3d-include-c99/inttypes.h')

    def test_ics_mesa3d_include_c99_stdbool_h(self):
        expected = [
            u'Copyright 2007-2010 VMware, Inc.',
        ]
        check_detection(expected, 'ics/mesa3d-include-c99/stdbool.h')

    def test_ics_mesa3d_include_c99_stdint_h(self):
        expected = [
            u'Copyright (c) 2006-2008 Alexander Chemeris',
        ]
        check_detection(expected, 'ics/mesa3d-include-c99/stdint.h')

    def test_ics_mesa3d_include_pixelflinger2_pixelflinger2_interface_h(self):
        expected = [
            u'Copyright 2010, The Android Open Source Project',
        ]
        check_detection(expected, 'ics/mesa3d-include-pixelflinger2/pixelflinger2_interface.h')

    def test_ics_mesa3d_src_glsl_ast_h(self):
        expected = [
            u'Copyright (c) 2009 Intel Corporation',
        ]
        check_detection(expected, 'ics/mesa3d-src-glsl/ast.h')

    def test_ics_mesa3d_src_glsl_ast_expr_cpp(self):
        expected = [
            u'Copyright (c) 2010 Intel Corporation',
        ]
        check_detection(expected, 'ics/mesa3d-src-glsl/ast_expr.cpp')

    def test_ics_mesa3d_src_glsl_glsl_compiler_cpp(self):
        expected = [
            u'Copyright (c) 2008, 2009 Intel Corporation',
        ]
        check_detection(expected, 'ics/mesa3d-src-glsl/glsl_compiler.cpp')

    def test_ics_mesa3d_src_glsl_glsl_parser_cpp(self):
        expected = [
            u'Copyright (c) 1984, 1989, 1990, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2009, 2010 Free Software Foundation, Inc.',
            u'Copyright (c) 2008, 2009 Intel Corporation',
        ]
        check_detection(expected, 'ics/mesa3d-src-glsl/glsl_parser.cpp')

    def test_ics_mesa3d_src_glsl_glsl_parser_h(self):
        expected = [
            u'Copyright (c) 1984, 1989, 1990, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2009, 2010 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/mesa3d-src-glsl/glsl_parser.h')

    def test_ics_mesa3d_src_glsl_ir_to_llvm_cpp(self):
        expected = [
            u'Copyright (c) 2005-2007 Brian Paul',
            u'Copyright (c) 2008 VMware, Inc.',
            u'Copyright (c) 2010 Intel Corporation',
            u'Copyright (c) 2010 Luca Barbieri',
        ]
        check_detection(expected, 'ics/mesa3d-src-glsl/ir_to_llvm.cpp')

    def test_ics_mesa3d_src_glsl_list_h(self):
        expected = [
            u'Copyright (c) 2008, 2010 Intel Corporation',
        ]
        check_detection(expected, 'ics/mesa3d-src-glsl/list.h')

    def test_ics_mesa3d_src_glsl_lower_jumps_cpp(self):
        expected = [
            u'Copyright (c) 2010 Luca Barbieri',
        ]
        check_detection(expected, 'ics/mesa3d-src-glsl/lower_jumps.cpp')

    def test_ics_mesa3d_src_glsl_program_h(self):
        expected = [
            u'Copyright (c) 1999-2008 Brian Paul',
            u'Copyright (c) 2009 VMware, Inc.',
            u'Copyright (c) 2010 Intel Corporation',
        ]
        check_detection(expected, 'ics/mesa3d-src-glsl/program.h')

    def test_ics_mesa3d_src_glsl_strtod_c(self):
        expected = [
            u'Copyright 2010 VMware, Inc.',
        ]
        check_detection(expected, 'ics/mesa3d-src-glsl/strtod.c')

    def test_ics_mesa3d_src_glsl_glcpp_glcpp_lex_c(self):
        expected = [
            u'Copyright (c) 2010 Intel Corporation',
        ]
        check_detection(expected, 'ics/mesa3d-src-glsl-glcpp/glcpp-lex.c')

    def test_ics_mesa3d_src_glsl_glcpp_glcpp_parse_c(self):
        expected = [
            u'Copyright (c) 1984, 1989, 1990, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2009, 2010 Free Software Foundation, Inc.',
            u'Copyright (c) 2010 Intel Corporation',
        ]
        check_detection(expected, 'ics/mesa3d-src-glsl-glcpp/glcpp-parse.c')

    def test_ics_mesa3d_src_glsl_glcpp_makefile_am(self):
        expected = [
            u'Copyright (c) 2010 Intel Corporation',
        ]
        check_detection(expected, 'ics/mesa3d-src-glsl-glcpp/Makefile.am')

    def test_ics_mesa3d_src_mesa_main_compiler_h(self):
        expected = [
            u'Copyright (c) 1999-2008 Brian Paul',
            u'Copyright (c) 2009 VMware, Inc.',
        ]
        check_detection(expected, 'ics/mesa3d-src-mesa-main/compiler.h')

    def test_ics_mesa3d_src_mesa_main_config_h(self):
        expected = [
            u'Copyright (c) 1999-2007 Brian Paul',
            u'Copyright (c) 2008 VMware, Inc.',
        ]
        check_detection(expected, 'ics/mesa3d-src-mesa-main/config.h')

    def test_ics_mesa3d_src_mesa_main_core_h(self):
        expected = [
            u'Copyright (c) 2010 LunarG Inc.',
        ]
        check_detection(expected, 'ics/mesa3d-src-mesa-main/core.h')

    def test_ics_mesa3d_src_mesa_main_debug_h(self):
        expected = [
            u'Copyright (c) 1999-2004 Brian Paul',
        ]
        check_detection(expected, 'ics/mesa3d-src-mesa-main/debug.h')

    def test_ics_mesa3d_src_mesa_main_get_h(self):
        expected = [
            u'Copyright (c) 1999-2001 Brian Paul',
        ]
        check_detection(expected, 'ics/mesa3d-src-mesa-main/get.h')

    def test_ics_mesa3d_src_mesa_main_glheader_h(self):
        expected = [
            u'Copyright (c) 1999-2008 Brian Paul',
        ]
        check_detection(expected, 'ics/mesa3d-src-mesa-main/glheader.h')

    def test_ics_mesa3d_src_mesa_main_hash_h(self):
        expected = [
            u'Copyright (c) 1999-2006 Brian Paul',
        ]
        check_detection(expected, 'ics/mesa3d-src-mesa-main/hash.h')

    def test_ics_mesa3d_src_mesa_main_shaderobj_h(self):
        expected = [
            u'Copyright (c) 2004-2007 Brian Paul',
        ]
        check_detection(expected, 'ics/mesa3d-src-mesa-main/shaderobj.h')

    def test_ics_mesa3d_src_mesa_main_simple_list_h(self):
        expected = [
            u'(c) 1997, Keith Whitwell',
            u'Copyright (c) 1999-2001 Brian Paul',
        ]
        check_detection(expected, 'ics/mesa3d-src-mesa-main/simple_list.h')

    def test_ics_mesa3d_src_mesa_program_hash_table_c(self):
        expected = [
            u'Copyright (c) 2008 Intel Corporation',
        ]
        check_detection(expected, 'ics/mesa3d-src-mesa-program/hash_table.c')

    def test_ics_mesa3d_src_mesa_program_prog_statevars_h(self):
        expected = [
            u'Copyright (c) 1999-2007 Brian Paul',
        ]
        check_detection(expected, 'ics/mesa3d-src-mesa-program/prog_statevars.h')

    def test_ics_mesa3d_src_pixelflinger2_pixelflinger2_cpp(self):
        expected = [
            u'Copyright 2010, The Android Open Source Project',
        ]
        check_detection(expected, 'ics/mesa3d-src-pixelflinger2/pixelflinger2.cpp')

    def test_ics_mesa3d_test_egl_cpp(self):
        expected = [
            u'Copyright 2007 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/mesa3d-test/egl.cpp')

    def test_ics_mesa3d_test_m_matrix_c(self):
        expected = [
            u'Copyright (c) 1999-2005 Brian Paul',
        ]
        check_detection(expected, 'ics/mesa3d-test/m_matrix.c')

    def test_ics_mesa3d_test_m_matrix_h(self):
        expected = [
            u'Copyright (c) 1999-2005 Brian Paul',
        ]
        check_detection(expected, 'ics/mesa3d-test/m_matrix.h')

    def test_ics_mksh_android_mk(self):
        expected = [
            u'Copyright (c) 2010 Thorsten Glaser <t.glaser@tarent.de>',
        ]
        check_detection(expected, 'ics/mksh/Android.mk')

    def test_ics_mksh_mkshrc(self):
        expected = [
            u'Copyright (c) 2010 Thorsten Glaser <t.glaser@tarent.de>',
        ]
        check_detection(expected, 'ics/mksh/mkshrc')

    def test_ics_mksh_notice(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010 Thorsten Glaser <tg@mirbsd.org>',
        ]
        check_detection(expected, 'ics/mksh/NOTICE')

    def test_ics_mksh_src_build_sh(self):
        expected = [
            u'Copyright (c) 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010 Thorsten Glaser <tg@mirbsd.org>',
        ]
        check_detection(expected, 'ics/mksh-src/Build.sh')

    def test_ics_mksh_src_edit_c(self):
        expected = [
            u'Copyright (c) 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010 Thorsten Glaser <tg@mirbsd.org>',
        ]
        check_detection(expected, 'ics/mksh-src/edit.c')

    def test_ics_mksh_src_funcs_c(self):
        expected = [
            u'Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010 Thorsten Glaser <tg@mirbsd.org>',
        ]
        check_detection(expected, 'ics/mksh-src/funcs.c')

    def test_ics_mksh_src_jobs_c(self):
        expected = [
            u'Copyright (c) 2003, 2004, 2005, 2006, 2007, 2008, 2009 Thorsten Glaser <tg@mirbsd.org>',
        ]
        check_detection(expected, 'ics/mksh-src/jobs.c')

    def test_ics_mksh_src_lalloc_c(self):
        expected = [
            u'Copyright (c) 2009 Thorsten Glaser <tg@mirbsd.org>',
        ]
        check_detection(expected, 'ics/mksh-src/lalloc.c')

    def test_ics_mksh_src_sh_h(self):
        expected = [
            u'Copyright (c) 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010 Thorsten Glaser <tg@mirbsd.org>',
        ]
        check_detection(expected, 'ics/mksh-src/sh.h')

    def test_ics_mtpd_l2tp_c(self):
        expected = [
            u'Copyright (c) 2009 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/mtpd/l2tp.c')

    def test_ics_mtpd_notice(self):
        expected = [
            u'Copyright (c) 2009, The Android Open Source Project',
        ]
        check_detection(expected, 'ics/mtpd/NOTICE')

    def test_ics_netperf_module_license_hp(self):
        expected = [
            u'Copyright (c) 1993 Hewlett-Packard Company',
        ]
        check_detection(expected, 'ics/netperf/MODULE_LICENSE_HP')

    def test_ics_netperf_netcpu_kstat10_c(self):
        expected = [
            u'(c) Copyright 2005-2007, Hewlett-Packard Company',
        ]
        check_detection(expected, 'ics/netperf/netcpu_kstat10.c')

    def test_ics_netperf_netcpu_looper_c(self):
        expected = [
            u'(c) Copyright 2005-2007. version 2.4.3',
        ]
        check_detection(expected, 'ics/netperf/netcpu_looper.c')

    def test_ics_netperf_netcpu_none_c(self):
        expected = [
            u'(c) Copyright 2005, Hewlett-Packard Company',
        ]
        check_detection(expected, 'ics/netperf/netcpu_none.c')

    def test_ics_netperf_netcpu_procstat_c(self):
        expected = [
            u'(c) Copyright 2005-2007 version 2.4.3',
        ]
        check_detection(expected, 'ics/netperf/netcpu_procstat.c')

    def test_ics_netperf_netlib_c(self):
        expected = [
            u'(c) Copyright 1993-2007 Hewlett-Packard Company.',
        ]
        check_detection(expected, 'ics/netperf/netlib.c')

    def test_ics_netperf_netlib_h(self):
        expected = [
            u'Copyright (c) 1993-2005 Hewlett-Packard Company',
        ]
        check_detection(expected, 'ics/netperf/netlib.h')

    def test_ics_netperf_netperf_c(self):
        expected = [
            u'Copyright (c) 1993-2007 Hewlett-Packard Company',
            u'(c) Copyright 1993-2007 Hewlett-Packard Company.',
        ]
        check_detection(expected, 'ics/netperf/netperf.c')

    def test_ics_netperf_netserver_c(self):
        expected = [
            u'Copyright (c) 1993-2007 Hewlett-Packard Company',
            u'(c) Copyright 1993-2007 Hewlett-Packard Co.',
        ]
        check_detection(expected, 'ics/netperf/netserver.c')

    def test_ics_netperf_netsh_h(self):
        expected = [
            u'Copyright (c) 1993,1995 Hewlett-Packard Company',
        ]
        check_detection(expected, 'ics/netperf/netsh.h')

    def test_ics_netperf_nettest_bsd_c(self):
        expected = [
            u'(c) Copyright 1993-2004 Hewlett-Packard Co.',
        ]
        check_detection(expected, 'ics/netperf/nettest_bsd.c')

    def test_ics_netperf_nettest_bsd_h(self):
        expected = [
            u'Copyright (c) 1993-2004 Hewlett-Packard Company',
        ]
        check_detection(expected, 'ics/netperf/nettest_bsd.h')

    def test_ics_netperf_nettest_dlpi_c(self):
        expected = [
            u'(c) Copyright 1993,1995,2004 Hewlett-Packard Co.',
        ]
        check_detection(expected, 'ics/netperf/nettest_dlpi.c')

    def test_ics_netperf_nettest_dlpi_h(self):
        expected = [
            u'Copyright (c) 1993, Hewlett-Packard Company',
        ]
        check_detection(expected, 'ics/netperf/nettest_dlpi.h')

    def test_ics_netperf_nettest_sctp_c(self):
        expected = [
            u'(c) Copyright 2005-2007 Hewlett-Packard Co.',
        ]
        check_detection(expected, 'ics/netperf/nettest_sctp.c')

    def test_ics_netperf_nettest_sctp_h(self):
        expected = [
            u'Copyright (c) 1993-2003 Hewlett-Packard Company',
        ]
        check_detection(expected, 'ics/netperf/nettest_sctp.h')

    def test_ics_netperf_nettest_sdp_c(self):
        expected = [
            u'(c) Copyright 2007 Hewlett-Packard Co.',
        ]
        check_detection(expected, 'ics/netperf/nettest_sdp.c')

    def test_ics_netperf_nettest_sdp_h(self):
        expected = [
            u'Copyright (c) 2007 Hewlett-Packard Company',
        ]
        check_detection(expected, 'ics/netperf/nettest_sdp.h')

    def test_ics_netperf_nettest_unix_c(self):
        expected = [
            u'(c) Copyright 1994-2007 Hewlett-Packard Co.',
        ]
        check_detection(expected, 'ics/netperf/nettest_unix.c')

    def test_ics_netperf_nettest_xti_c(self):
        expected = [
            u'(c) Copyright 1995-2007 Hewlett-Packard Co.',
        ]
        check_detection(expected, 'ics/netperf/nettest_xti.c')

    def test_ics_netperf_nettest_xti_h(self):
        expected = [
            u'Copyright (c) 1995,2004 Hewlett-Packard Company',
        ]
        check_detection(expected, 'ics/netperf/nettest_xti.h')

    def test_ics_neven_facedetector_jni_cpp(self):
        expected = [
            u'Copyright (c) 2006 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/neven/FaceDetector_jni.cpp')

    def test_ics_neven_notice(self):
        expected = [
            u'Copyright (c) 2008 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/neven/NOTICE')

    def test_ics_nist_sip_java_gov_nist_core_multimap_java(self):
        expected = [
            u'Copyright 1999-2004 The Apache Software Foundation',
        ]
        check_detection(expected, 'ics/nist-sip-java-gov-nist-core/MultiMap.java')

    def test_ics_oauth_core_src_main_java_net_oauth_consumerproperties_java(self):
        expected = [
            u'Copyright 2007 Netflix, Inc.',
        ]
        check_detection(expected, 'ics/oauth-core-src-main-java-net-oauth/ConsumerProperties.java')

    def test_ics_oauth_core_src_main_java_net_oauth_oauthexception_java(self):
        expected = [
            u'Copyright 2008 Google, Inc.',
        ]
        check_detection(expected, 'ics/oauth-core-src-main-java-net-oauth/OAuthException.java')

    def test_ics_oauth_core_src_main_java_net_oauth_oauthmessage_java(self):
        expected = [
            u'Copyright 2007, 2008 Netflix, Inc.',
        ]
        check_detection(expected, 'ics/oauth-core-src-main-java-net-oauth/OAuthMessage.java')

    def test_ics_oauth_core_src_main_java_net_oauth_client_oauthresponsemessage_java(self):
        expected = [
            u'Copyright 2008 Netflix, Inc.',
        ]
        check_detection(expected, 'ics/oauth-core-src-main-java-net-oauth-client/OAuthResponseMessage.java')

    def test_ics_oauth_core_src_main_java_net_oauth_client_httpclient4_httpclient4_java(self):
        expected = [
            u'Copyright 2008 Sean Sullivan',
        ]
        check_detection(expected, 'ics/oauth-core-src-main-java-net-oauth-client-httpclient4/HttpClient4.java')

    def test_ics_oauth_core_src_main_java_net_oauth_signature_rsa_sha1_java(self):
        expected = [
            u'Copyright 2007 Google, Inc.',
        ]
        check_detection(expected, 'ics/oauth-core-src-main-java-net-oauth-signature/RSA_SHA1.java')

    def test_ics_opencv_cvjni_cpp(self):
        expected = [
            u'Copyright (c) 2006-2009 SIProp Project http://www.siprop.org',
        ]
        check_detection(expected, 'ics/opencv/cvjni.cpp')

    def test_ics_opencv_license_opencv(self):
        expected = [
            u'Copyright (c) 2000-2006, Intel Corporation',
        ]
        check_detection(expected, 'ics/opencv/LICENSE_OpenCV')

    def test_ics_opencv_notice(self):
        expected = [
            u'Copyright (c) 2000-2006, Intel Corporation',
            u'Copyright (c) 2006-2009 SIProp Project http://www.siprop.org',
            u'Copyright (c) 1992, 1993 The Regents of the University of California.',
            u'Copyright (c) 2008, Liu Liu',
            u'Copyright (c) 2008, Google',
            u'Copyright (c) 1992, 1993 The Regents of the University of California.',
            u'Copyright (c) 2002, MD-Mathematische Dienste GmbH Im Defdahl',
            u'Copyright (c) 2000-2003 Chih-Chung Chang and Chih-Jen Lin',
            u'Copyright (c) 2000, Intel Corporation',
            u'Copyright (c) 2000, Intel Corporation',
            u'Copyright (c) 2002, Intel Corporation',
            u'Copyright( C) 2000, Intel Corporation',
            u'Copyright (c) 2008, Xavier Delacour',
            u'Copyright( C) 2000, Intel Corporation',
            u'Copyright (c) 2000, Intel Corporation',
            u'Copyright (c) 2008, Nils Hasler',
            u'Copyright (c) 2000, Intel Corporation',
            u'Copyright (c) 2000, Intel Corporation',
            u'Copyright (c) 2000, Intel Corporation',
            u'Copyright (c) 2000, Intel Corporation',
            u'Copyright (c) 1978-1999 Ken Turkowski. <turk@computer.org>',
            u'Copyright (c) 1981-1999 Ken Turkowski. <turk@computer.org>',
            u'Copyright (c) 1998 Yossi Rubner Computer Science Department, Stanford University',
            u'Copyright (c) 2006 Simon Perreault',
            u'Copyright (c) 1995 Intel Corporation.',
        ]
        check_detection(expected, 'ics/opencv/NOTICE')

    def test_ics_opencv_cvaux_src_cv3dtracker_cpp(self):
        expected = [
            u'Copyright (c) 2002, Intel Corporation',
        ]
        check_detection(expected, 'ics/opencv-cvaux-src/cv3dtracker.cpp')

    def test_ics_opencv_cvaux_src_cvdpstereo_cpp(self):
        expected = [
            u'Copyright (c) 2000, Intel Corporation',
        ]
        check_detection(expected, 'ics/opencv-cvaux-src/cvdpstereo.cpp')

    def test_ics_opencv_cv_include_cv_h(self):
        expected = [
            u'Copyright (c) 2000, Intel Corporation',
        ]
        check_detection(expected, 'ics/opencv-cv-include/cv.h')

    def test_ics_opencv_cv_src_cvkdtree_hpp(self):
        expected = [
            u'Copyright (c) 2008, Xavier Delacour',
        ]
        check_detection(expected, 'ics/opencv-cv-src/_cvkdtree.hpp')

    def test_ics_opencv_cv_src_cvcolor_cpp(self):
        expected = [
            u'Copyright (c) 2000, Intel Corporation',
            u'Copyright (c) 2002, MD-Mathematische Dienste GmbH Im Defdahl',
        ]
        check_detection(expected, 'ics/opencv-cv-src/cvcolor.cpp')

    def test_ics_opencv_cv_src_cvdistransform_cpp(self):
        expected = [
            u'Copyright (c) 2000, Intel Corporation',
            u'(c) 2006 by Jay Stavinzky.',
        ]
        check_detection(expected, 'ics/opencv-cv-src/cvdistransform.cpp')

    def test_ics_opencv_cv_src_cvemd_cpp(self):
        expected = [
            u'Copyright (c) 2000, Intel Corporation',
            u'Copyright (c) 1998 Yossi Rubner Computer Science Department, Stanford University',
        ]
        check_detection(expected, 'ics/opencv-cv-src/cvemd.cpp')

    def test_ics_opencv_cv_src_cvkdtree_cpp(self):
        expected = [
            u'Copyright (c) 2008, Xavier Delacour',
        ]
        check_detection(expected, 'ics/opencv-cv-src/cvkdtree.cpp')

    def test_ics_opencv_cv_src_cvsmooth_cpp(self):
        expected = [
            u'Copyright (c) 2000, Intel Corporation',
            u'Copyright (c) 2006 Simon Perreault',
        ]
        check_detection(expected, 'ics/opencv-cv-src/cvsmooth.cpp')

    def test_ics_opencv_cv_src_cvsurf_cpp(self):
        expected = [
            u'Copyright (c) 2008, Liu Liu',
        ]
        check_detection(expected, 'ics/opencv-cv-src/cvsurf.cpp')

    def test_ics_opencv_cxcore_include_cvwimage_h(self):
        expected = [
            u'Copyright (c) 2008, Google',
        ]
        check_detection(expected, 'ics/opencv-cxcore-include/cvwimage.h')

    def test_ics_opencv_cxcore_include_cxmisc_h(self):
        expected = [
            u'Copyright (c) 2000, Intel Corporation',
            u'Copyright (c) 1992, 1993 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/opencv-cxcore-include/cxmisc.h')

    def test_ics_opencv_cxcore_include_cxtypes_h(self):
        expected = [
            u'Copyright (c) 2000, Intel Corporation',
            u'Copyright (c) 1995 Intel Corporation.',
        ]
        check_detection(expected, 'ics/opencv-cxcore-include/cxtypes.h')

    def test_ics_opencv_cxcore_src_cxdatastructs_cpp(self):
        expected = [
            u'Copyright (c) 2000, Intel Corporation',
            u'Copyright (c) 1992, 1993 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/opencv-cxcore-src/cxdatastructs.cpp')

    def test_ics_opencv_cxcore_src_cxutils_cpp(self):
        expected = [
            u'Copyright (c) 2000, Intel Corporation',
            u'Copyright (c) 1978-1999 Ken Turkowski. <turk@computer.org>',
            u'Copyright (c) 1981-1999 Ken Turkowski. <turk@computer.org>',
        ]
        check_detection(expected, 'ics/opencv-cxcore-src/cxutils.cpp')

    def test_ics_opencv_ml_src_mlsvm_cpp(self):
        expected = [
            u'Copyright (c) 2000, Intel Corporation',
            u'Copyright (c) 2000-2003 Chih-Chung Chang and Chih-Jen Lin',
        ]
        check_detection(expected, 'ics/opencv-ml-src/mlsvm.cpp')

    def test_ics_opencv_otherlibs_highgui_cvcap_socket_cpp(self):
        expected = [
            u'Copyright (c) 2008, Nils Hasler',
        ]
        check_detection(expected, 'ics/opencv-otherlibs-highgui/cvcap_socket.cpp')

    def test_ics_opencv_otherlibs_highgui_grfmt_png_cpp(self):
        expected = [
            u'Copyright (c) 2000, Intel Corporation',
            u'(Copyright (c) 1999-2001 MIYASAKA Masaru)',
        ]
        check_detection(expected, 'ics/opencv-otherlibs-highgui/grfmt_png.cpp')

    def test_ics_openssl_e_os_h(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
        ]
        check_detection(expected, 'ics/openssl/e_os.h')

    def test_ics_openssl_e_os2_h(self):
        expected = [
            u'Copyright (c) 1998-2000 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl/e_os2.h')

    def test_ics_openssl_notice(self):
        expected = [
            u'Copyright (c) 1998-2011 The OpenSSL Project.',
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
        ]
        check_detection(expected, 'ics/openssl/NOTICE')

    def test_ics_openssl_apps_app_rand_c(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1998-2000 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-apps/app_rand.c')

    def test_ics_openssl_apps_apps_c(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1998-2001 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-apps/apps.c')

    def test_ics_openssl_apps_apps_h(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1998-2001 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-apps/apps.h')

    def test_ics_openssl_apps_asn1pars_c(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
        ]
        check_detection(expected, 'ics/openssl-apps/asn1pars.c')

    def test_ics_openssl_apps_cms_c(self):
        expected = [
            u'Copyright (c) 2008 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-apps/cms.c')

    def test_ics_openssl_apps_ec_c(self):
        expected = [
            u'Copyright (c) 1998-2005 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-apps/ec.c')

    def test_ics_openssl_apps_ecparam_c(self):
        expected = [
            u'Copyright (c) 1998-2005 The OpenSSL Project.',
            u'Copyright 2002 Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/openssl-apps/ecparam.c')

    def test_ics_openssl_apps_engine_c(self):
        expected = [
            u'Copyright (c) 2000 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-apps/engine.c')

    def test_ics_openssl_apps_genpkey_c(self):
        expected = [
            u'Copyright (c) 2006 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-apps/genpkey.c')

    def test_ics_openssl_apps_nseq_c(self):
        expected = [
            u'Copyright (c) 1999 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-apps/nseq.c')

    def test_ics_openssl_apps_openssl_c(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1998-2006 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-apps/openssl.c')

    def test_ics_openssl_apps_pkcs12_c(self):
        expected = [
            u'Copyright (c) 1999-2006 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-apps/pkcs12.c')

    def test_ics_openssl_apps_prime_c(self):
        expected = [
            u'Copyright (c) 2004 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-apps/prime.c')

    def test_ics_openssl_apps_rand_c(self):
        expected = [
            u'Copyright (c) 1998-2001 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-apps/rand.c')

    def test_ics_openssl_apps_s_client_c(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1998-2006 The OpenSSL Project.',
            u'Copyright 2005 Nokia.',
        ]
        check_detection(expected, 'ics/openssl-apps/s_client.c')

    def test_ics_openssl_apps_s_server_c(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1998-2006 The OpenSSL Project.',
            u'Copyright 2002 Sun Microsystems, Inc.',
            u'Copyright 2005 Nokia.',
        ]
        check_detection(expected, 'ics/openssl-apps/s_server.c')

    def test_ics_openssl_apps_smime_c(self):
        expected = [
            u'Copyright (c) 1999-2004 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-apps/smime.c')

    def test_ics_openssl_apps_speed_c(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright 2002 Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/openssl-apps/speed.c')

    def test_ics_openssl_apps_timeouts_h(self):
        expected = [
            u'Copyright (c) 1999-2005 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-apps/timeouts.h')

    def test_ics_openssl_crypto_cryptlib_c(self):
        expected = [
            u'Copyright (c) 1998-2006 The OpenSSL Project.',
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright 2002 Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/openssl-crypto/cryptlib.c')

    def test_ics_openssl_crypto_lpdir_nyi_c(self):
        expected = [
            u'Copyright (c) 2004, Richard Levitte <richard@levitte.org>',
        ]
        check_detection(expected, 'ics/openssl-crypto/LPdir_nyi.c')

    def test_ics_openssl_crypto_md32_common_h(self):
        expected = [
            u'Copyright (c) 1999-2007 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto/md32_common.h')

    def test_ics_openssl_crypto_mem_clr_c(self):
        expected = [
            u'Copyright (c) 2001 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto/mem_clr.c')

    def test_ics_openssl_crypto_o_str_c(self):
        expected = [
            u'Copyright (c) 2003 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto/o_str.c')

    def test_ics_openssl_crypto_aes_aes_h(self):
        expected = [
            u'Copyright (c) 1998-2002 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-aes/aes.h')

    def test_ics_openssl_crypto_aes_aes_cfb_c(self):
        expected = [
            u'Copyright (c) 2002-2006 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-aes/aes_cfb.c')

    def test_ics_openssl_crypto_asn1_a_sign_c(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1998-2003 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-asn1/a_sign.c')

    def test_ics_openssl_crypto_asn1_asn_mime_c(self):
        expected = [
            u'Copyright (c) 1999-2008 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-asn1/asn_mime.c')

    def test_ics_openssl_crypto_asn1_asn_moid_c(self):
        expected = [
            u'Copyright (c) 2001-2004 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-asn1/asn_moid.c')

    def test_ics_openssl_crypto_asn1_asn1_err_c(self):
        expected = [
            u'Copyright (c) 1999-2009 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-asn1/asn1_err.c')

    def test_ics_openssl_crypto_asn1_asn1_gen_c(self):
        expected = [
            u'Copyright (c) 2002 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-asn1/asn1_gen.c')

    def test_ics_openssl_crypto_asn1_asn1t_h(self):
        expected = [
            u'Copyright (c) 2000-2005 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-asn1/asn1t.h')

    def test_ics_openssl_crypto_asn1_tasn_dec_c(self):
        expected = [
            u'Copyright (c) 2000-2005 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-asn1/tasn_dec.c')

    def test_ics_openssl_crypto_asn1_tasn_enc_c(self):
        expected = [
            u'Copyright (c) 2000-2004 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-asn1/tasn_enc.c')

    def test_ics_openssl_crypto_asn1_tasn_prn_c(self):
        expected = [
            u'Copyright (c) 2000,2005 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-asn1/tasn_prn.c')

    def test_ics_openssl_crypto_asn1_x_nx509_c(self):
        expected = [
            u'Copyright (c) 2005 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-asn1/x_nx509.c')

    def test_ics_openssl_crypto_bf_bf_locl_h(self):
        expected = [
            u'Copyright (c) 1995-1997 Eric Young (eay@cryptsoft.com)',
        ]
        check_detection(expected, 'ics/openssl-crypto-bf/bf_locl.h')

    def test_ics_openssl_crypto_bf_copyright(self):
        expected = [
            u'Copyright (c) 1995-1997 Eric Young (eay@cryptsoft.com)',
        ]
        check_detection(expected, 'ics/openssl-crypto-bf/COPYRIGHT')

    def test_ics_openssl_crypto_bio_b_print_c(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright Patrick Powell 1995',
        ]
        check_detection(expected, 'ics/openssl-crypto-bio/b_print.c')

    def test_ics_openssl_crypto_bio_bss_bio_c(self):
        expected = [
            u'Copyright (c) 1998-2003 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-bio/bss_bio.c')

    def test_ics_openssl_crypto_bn_bn_h(self):
        expected = [
            u'Copyright (c) 1995-1997 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1998-2006 The OpenSSL Project.',
            u'Copyright 2002 Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/openssl-crypto-bn/bn.h')

    def test_ics_openssl_crypto_bn_bn_blind_c(self):
        expected = [
            u'Copyright (c) 1998-2006 The OpenSSL Project.',
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
        ]
        check_detection(expected, 'ics/openssl-crypto-bn/bn_blind.c')

    def test_ics_openssl_crypto_bn_bn_ctx_c(self):
        expected = [
            u'Copyright (c) 1998-2004 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-bn/bn_ctx.c')

    def test_ics_openssl_crypto_bn_bn_err_c(self):
        expected = [
            u'Copyright (c) 1999-2007 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-bn/bn_err.c')

    def test_ics_openssl_crypto_bn_bn_exp_c(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1998-2005 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-bn/bn_exp.c')

    def test_ics_openssl_crypto_bn_bn_gf2m_c(self):
        expected = [
            u'Copyright 2002 Sun Microsystems, Inc.',
            u'Copyright (c) 1998-2002 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-bn/bn_gf2m.c')

    def test_ics_openssl_crypto_bn_bn_lcl_h(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1998-2000 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-bn/bn_lcl.h')

    def test_ics_openssl_crypto_bn_bn_mod_c(self):
        expected = [
            u'Copyright (c) 1998-2000 The OpenSSL Project.',
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
        ]
        check_detection(expected, 'ics/openssl-crypto-bn/bn_mod.c')

    def test_ics_openssl_crypto_des_read2pwd_c(self):
        expected = [
            u'Copyright (c) 2001-2002 The OpenSSL Project.',
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
        ]
        check_detection(expected, 'ics/openssl-crypto-des/read2pwd.c')

    def test_ics_openssl_crypto_des_readme(self):
        expected = [
            u'Copyright (c) 1997, Eric Young',
        ]
        check_detection(expected, 'ics/openssl-crypto-des/README')

    def test_ics_openssl_crypto_des_rpc_des_h(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1986 by Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/openssl-crypto-des/rpc_des.h')

    def test_ics_openssl_crypto_des_asm_des_enc_m4(self):
        expected = [
            u'Copyright Svend Olaf Mikkelsen.',
            u'Copyright Eric A. Young.',
        ]
        check_detection(expected, 'ics/openssl-crypto-des-asm/des_enc.m4')

    def test_ics_openssl_crypto_dsa_dsa_locl_h(self):
        expected = [
            u'Copyright (c) 2007 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-dsa/dsa_locl.h')

    def test_ics_openssl_crypto_ec_ec_h(self):
        expected = [
            u'Copyright (c) 1998-2005 The OpenSSL Project.',
            u'Copyright 2002 Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/openssl-crypto-ec/ec.h')

    def test_ics_openssl_crypto_ec_ec_asn1_c(self):
        expected = [
            u'Copyright (c) 2000-2003 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-ec/ec_asn1.c')

    def test_ics_openssl_crypto_ec_ec_curve_c(self):
        expected = [
            u'Copyright (c) 1998-2004 The OpenSSL Project.',
            u'Copyright 2002 Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/openssl-crypto-ec/ec_curve.c')

    def test_ics_openssl_crypto_ec_ec_mult_c(self):
        expected = [
            u'Copyright (c) 1998-2007 The OpenSSL Project.',
            u'Copyright 2002 Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/openssl-crypto-ec/ec_mult.c')

    def test_ics_openssl_crypto_ec_ec2_mult_c(self):
        expected = [
            u'Copyright 2002 Sun Microsystems, Inc.',
            u'Copyright (c) 1998-2003 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-ec/ec2_mult.c')

    def test_ics_openssl_crypto_ec_ec2_smpl_c(self):
        expected = [
            u'Copyright 2002 Sun Microsystems, Inc.',
            u'Copyright (c) 1998-2005 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-ec/ec2_smpl.c')

    def test_ics_openssl_crypto_ec_ecp_mont_c(self):
        expected = [
            u'Copyright (c) 1998-2001 The OpenSSL Project.',
            u'Copyright 2002 Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/openssl-crypto-ec/ecp_mont.c')

    def test_ics_openssl_crypto_ec_ecp_nist_c(self):
        expected = [
            u'Copyright (c) 1998-2003 The OpenSSL Project.',
            u'Copyright 2002 Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/openssl-crypto-ec/ecp_nist.c')

    def test_ics_openssl_crypto_ec_ecp_smpl_c(self):
        expected = [
            u'Copyright (c) 1998-2002 The OpenSSL Project.',
            u'Copyright 2002 Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/openssl-crypto-ec/ecp_smpl.c')

    def test_ics_openssl_crypto_ecdh_ecdh_h(self):
        expected = [
            u'Copyright 2002 Sun Microsystems, Inc.',
            u'Copyright (c) 2000-2002 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-ecdh/ecdh.h')

    def test_ics_openssl_crypto_ecdsa_ecdsatest_c(self):
        expected = [
            u'Copyright (c) 2000-2005 The OpenSSL Project.',
            u'Copyright 2002 Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/openssl-crypto-ecdsa/ecdsatest.c')

    def test_ics_openssl_crypto_ecdsa_ecs_asn1_c(self):
        expected = [
            u'Copyright (c) 2000-2002 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-ecdsa/ecs_asn1.c')

    def test_ics_openssl_crypto_engine_eng_all_c(self):
        expected = [
            u'Copyright (c) 2000-2001 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-engine/eng_all.c')

    def test_ics_openssl_crypto_engine_eng_cryptodev_c(self):
        expected = [
            u'Copyright (c) 2002 Bob Beck <beck@openbsd.org>',
            u'Copyright (c) 2002 Theo de Raadt',
            u'Copyright (c) 2002 Markus Friedl',
        ]
        check_detection(expected, 'ics/openssl-crypto-engine/eng_cryptodev.c')

    def test_ics_openssl_crypto_engine_eng_dyn_c(self):
        expected = [
            u'Copyright (c) 1999-2001 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-engine/eng_dyn.c')

    def test_ics_openssl_crypto_engine_eng_err_c(self):
        expected = [
            u'Copyright (c) 1999-2010 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-engine/eng_err.c')

    def test_ics_openssl_crypto_engine_eng_fat_c(self):
        expected = [
            u'Copyright (c) 1999-2001 The OpenSSL Project.',
            u'Copyright 2002 Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/openssl-crypto-engine/eng_fat.c')

    def test_ics_openssl_crypto_engine_engine_h(self):
        expected = [
            u'Copyright (c) 1999-2004 The OpenSSL Project.',
            u'Copyright 2002 Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/openssl-crypto-engine/engine.h')

    def test_ics_openssl_crypto_evp_m_ecdsa_c(self):
        expected = [
            u'Copyright (c) 1998-2002 The OpenSSL Project.',
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
        ]
        check_detection(expected, 'ics/openssl-crypto-evp/m_ecdsa.c')

    def test_ics_openssl_crypto_evp_m_sigver_c(self):
        expected = [
            u'Copyright (c) 2006,2007 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-evp/m_sigver.c')

    def test_ics_openssl_crypto_pem_pem_all_c(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1998-2002 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-pem/pem_all.c')

    def test_ics_openssl_crypto_pkcs12_p12_crt_c(self):
        expected = [
            u'Copyright (c) 1999-2002 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-pkcs12/p12_crt.c')

    def test_ics_openssl_crypto_rand_rand_win_c(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1998-2000 The OpenSSL Project.',
            u'(c) Copyright Microsoft Corp. 1993.',
        ]
        check_detection(expected, 'ics/openssl-crypto-rand/rand_win.c')

    def test_ics_openssl_crypto_rc4_asm_rc4_ia64_pl(self):
        expected = [
            u'Copyright (c) 2005 Hewlett-Packard Development Company, L.P.',
            u'Copyright (c) 2005 Hewlett-Packard Development Company, L.P.',
        ]
        check_detection(expected, 'ics/openssl-crypto-rc4-asm/rc4-ia64.pl')

    def test_ics_openssl_crypto_ui_ui_compat_c(self):
        expected = [
            u'Copyright (c) 2001-2002 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-ui/ui_compat.c')

    def test_ics_openssl_crypto_ui_ui_openssl_c(self):
        expected = [
            u'Copyright (c) 2001 The OpenSSL Project.',
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
        ]
        check_detection(expected, 'ics/openssl-crypto-ui/ui_openssl.c')

    def test_ics_openssl_crypto_x509_x509_h(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright 2002 Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/openssl-crypto-x509/x509.h')

    def test_ics_openssl_crypto_x509v3_v3_alt_c(self):
        expected = [
            u'Copyright (c) 1999-2003 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-crypto-x509v3/v3_alt.c')

    def test_ics_openssl_crypto_x509v3_v3_pci_c(self):
        expected = [
            u'Copyright (c) 2004 Kungliga Tekniska Hogskolan (Royal Institute of Technology, Stockholm, Sweden).',
        ]
        check_detection(expected, 'ics/openssl-crypto-x509v3/v3_pci.c')

    def test_ics_openssl_include_openssl_modes_h(self):
        expected = [
            u'Copyright (c) 2008 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-include-openssl/modes.h')

    def test_ics_openssl_include_openssl_ssl_h(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1998-2007 The OpenSSL Project.',
            u'Copyright 2002 Sun Microsystems, Inc.',
            u'Copyright 2005 Nokia.',
        ]
        check_detection(expected, 'ics/openssl-include-openssl/ssl.h')

    def test_ics_openssl_include_openssl_ssl3_h(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1998-2002 The OpenSSL Project.',
            u'Copyright 2002 Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/openssl-include-openssl/ssl3.h')

    def test_ics_openssl_include_openssl_tls1_h(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1998-2006 The OpenSSL Project.',
            u'Copyright 2002 Sun Microsystems, Inc.',
            u'Copyright 2005 Nokia.',
        ]
        check_detection(expected, 'ics/openssl-include-openssl/tls1.h')

    def test_ics_openssl_ssl_d1_both_c(self):
        expected = [
            u'Copyright (c) 1998-2005 The OpenSSL Project.',
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
        ]
        check_detection(expected, 'ics/openssl-ssl/d1_both.c')

    def test_ics_openssl_ssl_d1_clnt_c(self):
        expected = [
            u'Copyright (c) 1999-2007 The OpenSSL Project.',
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
        ]
        check_detection(expected, 'ics/openssl-ssl/d1_clnt.c')

    def test_ics_openssl_ssl_s2_lib_c(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1998-2007 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-ssl/s2_lib.c')

    def test_ics_openssl_ssl_s3_enc_c(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1998-2007 The OpenSSL Project.',
            u'Copyright 2005 Nokia.',
        ]
        check_detection(expected, 'ics/openssl-ssl/s3_enc.c')

    def test_ics_openssl_ssl_s3_lib_c(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1998-2007 The OpenSSL Project.',
            u'Copyright 2002 Sun Microsystems, Inc.',
            u'Copyright 2005 Nokia.',
        ]
        check_detection(expected, 'ics/openssl-ssl/s3_lib.c')

    def test_ics_openssl_ssl_ssl_asn1_c(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright 2005 Nokia.',
        ]
        check_detection(expected, 'ics/openssl-ssl/ssl_asn1.c')

    def test_ics_openssl_ssl_ssl_cert_c(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1998-2007 The OpenSSL Project.',
            u'Copyright 2002 Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/openssl-ssl/ssl_cert.c')

    def test_ics_openssl_ssl_ssltest_c(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1998-2000 The OpenSSL Project.',
            u'Copyright 2002 Sun Microsystems, Inc.',
            u'Copyright 2005 Nokia.',
        ]
        check_detection(expected, 'ics/openssl-ssl/ssltest.c')

    def test_ics_openssl_ssl_t1_reneg_c(self):
        expected = [
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 1998-2009 The OpenSSL Project.',
        ]
        check_detection(expected, 'ics/openssl-ssl/t1_reneg.c')

    def test_ics_oprofile_changelog_2002(self):
        expected = [
            u'copyright for 2002',
        ]
        check_detection(expected, 'ics/oprofile/ChangeLog-2002')

    def test_ics_oprofile_configure_in(self):
        expected = [
            u'Copyright 1999 Olaf Titz <olaf@bigred.inka.de>',
        ]
        check_detection(expected, 'ics/oprofile/configure.in')

    def test_ics_oprofile_popt_h(self):
        expected = [
            u'(c) 1998-2000 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/oprofile/popt.h')

    def test_ics_oprofile_agents_jvmpi_jvmpi_oprofile_cpp(self):
        expected = [
            u'Copyright 2007 OProfile authors',
            u'Copyright IBM Corporation 2007',
        ]
        check_detection(expected, 'ics/oprofile-agents-jvmpi/jvmpi_oprofile.cpp')

    def test_ics_oprofile_daemon_init_c(self):
        expected = [
            u'Copyright 2002 OProfile authors',
            u'Copyright (c) 2005 Hewlett-Packard Co.',
        ]
        check_detection(expected, 'ics/oprofile-daemon/init.c')

    def test_ics_oprofile_daemon_opd_anon_c(self):
        expected = [
            u'Copyright 2005 OProfile authors',
        ]
        check_detection(expected, 'ics/oprofile-daemon/opd_anon.c')

    def test_ics_oprofile_daemon_opd_cookie_c(self):
        expected = [
            u'Copyright 2002, 2005 OProfile authors',
        ]
        check_detection(expected, 'ics/oprofile-daemon/opd_cookie.c')

    def test_ics_oprofile_daemon_opd_events_c(self):
        expected = [
            u'Copyright 2002, 2003 OProfile authors',
        ]
        check_detection(expected, 'ics/oprofile-daemon/opd_events.c')

    def test_ics_oprofile_daemon_opd_extended_c(self):
        expected = [
            u'Copyright 2007-2009 OProfile authors',
            u'Copyright (c) 2009 Advanced Micro Devices, Inc.',
        ]
        check_detection(expected, 'ics/oprofile-daemon/opd_extended.c')

    def test_ics_oprofile_daemon_opd_ibs_c(self):
        expected = [
            u'Copyright 2007-2010 OProfile authors',
            u'Copyright (c) 2008 Advanced Micro Devices, Inc.',
        ]
        check_detection(expected, 'ics/oprofile-daemon/opd_ibs.c')

    def test_ics_oprofile_daemon_opd_ibs_h(self):
        expected = [
            u'Copyright 2008-2010 OProfile authors',
            u'Copyright (c) 2008 Advanced Micro Devices, Inc.',
        ]
        check_detection(expected, 'ics/oprofile-daemon/opd_ibs.h')

    def test_ics_oprofile_daemon_opd_ibs_trans_c(self):
        expected = [
            u'Copyright 2008 - 2010 OProfile authors',
            u'Copyright (c) 2008 Advanced Micro Devices, Inc.',
        ]
        check_detection(expected, 'ics/oprofile-daemon/opd_ibs_trans.c')

    def test_ics_oprofile_daemon_opd_ibs_trans_h(self):
        expected = [
            u'Copyright 2008 OProfile authors',
            u'Copyright (c) 2008 Advanced Micro Devices, Inc.',
        ]
        check_detection(expected, 'ics/oprofile-daemon/opd_ibs_trans.h')

    def test_ics_oprofile_daemon_opd_mangling_c(self):
        expected = [
            u'Copyright 2002 OProfile authors',
        ]
        check_detection(expected, 'ics/oprofile-daemon/opd_mangling.c')

    def test_ics_oprofile_daemon_opd_perfmon_c(self):
        expected = [
            u'Copyright 2003 OProfile authors',
        ]
        check_detection(expected, 'ics/oprofile-daemon/opd_perfmon.c')

    def test_ics_oprofile_daemon_opd_pipe_c(self):
        expected = [
            u'Copyright 2008 OProfile authors',
        ]
        check_detection(expected, 'ics/oprofile-daemon/opd_pipe.c')

    def test_ics_oprofile_daemon_opd_spu_c(self):
        expected = [
            u'Copyright 2007 OProfile authors',
            u'(c) Copyright IBM Corporation 2007',
        ]
        check_detection(expected, 'ics/oprofile-daemon/opd_spu.c')

    def test_ics_oprofile_daemon_opd_trans_c(self):
        expected = [
            u'Copyright 2002 OProfile authors',
            u'Copyright (c) 2005 Hewlett-Packard Co.',
            u'(c) Copyright IBM Corporation 2007',
        ]
        check_detection(expected, 'ics/oprofile-daemon/opd_trans.c')

    def test_ics_oprofile_daemon_opd_trans_h(self):
        expected = [
            u'Copyright 2002 OProfile authors',
            u'(c) Copyright IBM Corporation 2007',
        ]
        check_detection(expected, 'ics/oprofile-daemon/opd_trans.h')

    def test_ics_oprofile_daemon_oprofiled_c(self):
        expected = [
            u'Copyright 2002, 2003 OProfile authors',
            u'Copyright (c) 2005 Hewlett-Packard Co.',
        ]
        check_detection(expected, 'ics/oprofile-daemon/oprofiled.c')

    def test_ics_oprofile_daemon_liblegacy_p_module_h(self):
        expected = [
            u'Copyright 1996, 1997 Linux International.',
        ]
        check_detection(expected, 'ics/oprofile-daemon-liblegacy/p_module.h')

    def test_ics_oprofile_doc_oprofile_1_in(self):
        expected = [
            u'Copyright (c) 1998-2004 University of Manchester, UK, John Levon, and others.',
        ]
        check_detection(expected, 'ics/oprofile-doc/oprofile.1.in')

    def test_ics_oprofile_events_ppc64_970mp_events(self):
        expected = [
            u'Copyright OProfile authors',
            u'Copyright (c) International Business Machines, 2007.',
        ]
        check_detection(expected, 'ics/oprofile-events-ppc64-970MP/events')

    def test_ics_oprofile_events_ppc64_970mp_unit_masks(self):
        expected = [
            u'Copyright OProfile authors',
            u'Copyright (c) International Business Machines, 2006.',
        ]
        check_detection(expected, 'ics/oprofile-events-ppc64-970MP/unit_masks')

    def test_ics_oprofile_events_ppc64_cell_be_events(self):
        expected = [
            u'Copyright OProfile authors',
            u'(c) COPYRIGHT International Business Machines Corp. 2006',
        ]
        check_detection(expected, 'ics/oprofile-events-ppc64-cell-be/events')

    def test_ics_oprofile_events_ppc64_ibm_compat_v1_events(self):
        expected = [
            u'Copyright OProfile authors',
            u'Copyright (c) International Business Machines, 2009.',
        ]
        check_detection(expected, 'ics/oprofile-events-ppc64-ibm-compat-v1/events')

    def test_ics_oprofile_events_x86_64_family10_events_extra_contributed(self):
        expected = [
            u'Copyright OProfile authors',
            u'Copyright (c) 2006-2008 Advanced Micro Devices',
        ]
        check_detection(expected, 'ics/oprofile-events-x86-64-family10/events')

    def test_ics_oprofile_events_x86_64_family11h_unit_masks(self):
        expected = [
            u'Copyright OProfile authors',
            u'Copyright (c) Advanced Micro Devices, 2006-2008',
        ]
        check_detection(expected, 'ics/oprofile-events-x86-64-family11h/unit_masks')

    def test_ics_oprofile_events_x86_64_family12h_events_extra_contributed(self):
        expected = [
            u'Copyright OProfile authors',
            u'Copyright (c) 2006-2010 Advanced Micro Devices',
        ]
        check_detection(expected, 'ics/oprofile-events-x86-64-family12h/events')

    def test_ics_oprofile_include_sstream(self):
        expected = [
            u'Copyright (c) 2000 Free Software Foundation',
        ]
        check_detection(expected, 'ics/oprofile-include/sstream')

    def test_ics_oprofile_libop_op_hw_specific_h(self):
        expected = [
            u'Copyright 2008 Intel Corporation',
        ]
        check_detection(expected, 'ics/oprofile-libop/op_hw_specific.h')

    def test_ics_oprofile_libpopt_findme_c(self):
        expected = [
            u'(c) 1998-2002 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/oprofile-libpopt/findme.c')

    def test_ics_oprofile_libpp_callgraph_container_cpp(self):
        expected = [
            u'Copyright 2004 OProfile authors',
        ]
        check_detection(expected, 'ics/oprofile-libpp/callgraph_container.cpp')

    def test_ics_oprofile_libpp_format_output_h(self):
        expected = [
            u'Copyright 2002 OProfile authors',
        ]
        check_detection(expected, 'ics/oprofile-libpp/format_output.h')

    def test_ics_oprofile_libpp_populate_cpp(self):
        expected = [
            u'Copyright 2003 OProfile authors',
            u'(c) Copyright IBM Corporation 2007',
        ]
        check_detection(expected, 'ics/oprofile-libpp/populate.cpp')

    def test_ics_oprofile_libpp_symbol_cpp(self):
        expected = [
            u'Copyright 2002, 2004 OProfile authors',
        ]
        check_detection(expected, 'ics/oprofile-libpp/symbol.cpp')

    def test_ics_oprofile_libpp_xml_utils_cpp(self):
        expected = [
            u'Copyright 2006 OProfile authors',
        ]
        check_detection(expected, 'ics/oprofile-libpp/xml_utils.cpp')

    def test_ics_oprofile_libregex_demangle_java_symbol_cpp(self):
        expected = [
            u'Copyright 2007 OProfile authors',
        ]
        check_detection(expected, 'ics/oprofile-libregex/demangle_java_symbol.cpp')

    def test_ics_oprofile_libutil_sparse_array_h(self):
        expected = [
            u'Copyright 2007 OProfile authors',
            u'Copyright (c) International Business Machines, 2007.',
        ]
        check_detection(expected, 'ics/oprofile-libutil++/sparse_array.h')

    def test_ics_oprofile_libutil_string_manip_cpp(self):
        expected = [
            u'Copyright 2002 OProfile authors',
        ]
        check_detection(expected, 'ics/oprofile-libutil++/string_manip.cpp')

    def test_ics_oprofile_libutil_utility_h(self):
        expected = [
            u'Copyright 2002 OProfile authors',
            u'(c) Copyright boost.org 1999.',
        ]
        check_detection(expected, 'ics/oprofile-libutil++/utility.h')

    def test_ics_oprofile_module_ia64_op_pmu_c(self):
        expected = [
            u'Copyright 2002 OProfile authors',
            u'Copyright (c) 1999 Ganesh Venkitachalam <venkitac@us.ibm.com>',
            u'Copyright (c) 1999-2002 Hewlett Packard Co Stephane Eranian <eranian@hpl.hp.com> David Mosberger-Tang <davidm@hpl.hp.com>',
        ]
        check_detection(expected, 'ics/oprofile-module-ia64/op_pmu.c')

    def test_ics_oprofile_opcontrol_opcontrol_cpp(self):
        expected = [
            u'Copyright 2008, The Android Open Source Project',
        ]
        check_detection(expected, 'ics/oprofile-opcontrol/opcontrol.cpp')

    def test_ics_oprofile_opjitconv_conversion_c(self):
        expected = [
            u'Copyright 2008 OProfile authors',
            u'Copyright IBM Corporation 2008',
        ]
        check_detection(expected, 'ics/oprofile-opjitconv/conversion.c')

    def test_ics_oprofile_pp_oparchive_cpp(self):
        expected = [
            u'Copyright 2003, 2004 OProfile authors',
        ]
        check_detection(expected, 'ics/oprofile-pp/oparchive.cpp')

    def test_ics_oprofile_pp_oparchive_options_cpp(self):
        expected = [
            u'Copyright 2002, 2003, 2004 OProfile authors',
        ]
        check_detection(expected, 'ics/oprofile-pp/oparchive_options.cpp')

    def test_ics_oprofile_utils_opcontrol_misc(self):
        expected = [
            u'Copyright 2002 Read the file COPYING',
            u'Copyright IBM Corporation 2007',
        ]
        check_detection(expected, 'ics/oprofile-utils/opcontrol')

    def test_ics_ping_notice(self):
        expected = [
            u'Copyright (c) 1989 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/ping/NOTICE')

    def test_ics_ping_ping_c(self):
        expected = [
            u'Copyright (c) 1989 The Regents of the University of California.',
            u'Copyright (c) 1989 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/ping/ping.c')

    def test_ics_ping6_notice(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997, and 1998 WIDE Project.',
            u'Copyright (c) 1989, 1993 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/ping6/NOTICE')

    def test_ics_ping6_ping6_c(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997, and 1998 WIDE Project.',
            u'Copyright (c) 1989, 1993 The Regents of the University of California.',
            u'Copyright (c) 1989, 1993 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/ping6/ping6.c')

    def test_ics_ppp_pppd_auth_c(self):
        expected = [
            u'Copyright (c) 1993-2002 Paul Mackerras.',
            u'Copyright (c) 1984-2000 Carnegie Mellon University.',
        ]
        check_detection(expected, 'ics/ppp-pppd/auth.c')

    def test_ics_ppp_pppd_cbcp_c(self):
        expected = [
            u'Copyright (c) 1995 Pedro Roque Marques.',
        ]
        check_detection(expected, 'ics/ppp-pppd/cbcp.c')

    def test_ics_ppp_pppd_ccp_c(self):
        expected = [
            u'Copyright (c) 1994-2002 Paul Mackerras.',
        ]
        check_detection(expected, 'ics/ppp-pppd/ccp.c')

    def test_ics_ppp_pppd_chap_ms_c(self):
        expected = [
            u'Copyright (c) 1995 Eric Rosenquist.',
            u'Copyright (c) 2002 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/ppp-pppd/chap_ms.c')

    def test_ics_ppp_pppd_chap_ms_h(self):
        expected = [
            u'Copyright (c) 1995 Eric Rosenquist.',
        ]
        check_detection(expected, 'ics/ppp-pppd/chap_ms.h')

    def test_ics_ppp_pppd_chap_md5_c(self):
        expected = [
            u'Copyright (c) 2003 Paul Mackerras.',
        ]
        check_detection(expected, 'ics/ppp-pppd/chap-md5.c')

    def test_ics_ppp_pppd_demand_c(self):
        expected = [
            u'Copyright (c) 1996-2002 Paul Mackerras.',
        ]
        check_detection(expected, 'ics/ppp-pppd/demand.c')

    def test_ics_ppp_pppd_eap_c(self):
        expected = [
            u'Copyright (c) 2001 by Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/ppp-pppd/eap.c')

    def test_ics_ppp_pppd_ecp_c(self):
        expected = [
            u'Copyright (c) 2002 The Android Open Source Project',
            u'Copyright (c) 1994-2002 Paul Mackerras.',
        ]
        check_detection(expected, 'ics/ppp-pppd/ecp.c')

    def test_ics_ppp_pppd_ecp_h(self):
        expected = [
            u'Copyright (c) 2002 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/ppp-pppd/ecp.h')

    def test_ics_ppp_pppd_eui64_c(self):
        expected = [
            u'Copyright (c) 1999 Tommi Komulainen.',
        ]
        check_detection(expected, 'ics/ppp-pppd/eui64.c')

    def test_ics_ppp_pppd_fsm_c(self):
        expected = [
            u'Copyright (c) 1984-2000 Carnegie Mellon University.',
        ]
        check_detection(expected, 'ics/ppp-pppd/fsm.c')

    def test_ics_ppp_pppd_ipv6cp_c(self):
        expected = [
            u'Copyright (c) 1999 Tommi Komulainen.',
            u'Copyright (c) 1995, 1996, 1997 Francis.Dupont@inria.fr, INRIA',
            u'Copyright (c) 1998, 1999 Francis.Dupont@inria.fr',
            u'Copyright (c) 1984-2000 Carnegie Mellon University.',
        ]
        check_detection(expected, 'ics/ppp-pppd/ipv6cp.c')

    def test_ics_ppp_pppd_main_c(self):
        expected = [
            u'Copyright (c) 1984-2000 Carnegie Mellon University.',
            u'Copyright (c) 1999-2004 Paul Mackerras.',
        ]
        check_detection(expected, 'ics/ppp-pppd/main.c')

    def test_ics_ppp_pppd_md4_c(self):
        expected = [
            u'(c) 1990 RSA Data Security, Inc.',
        ]
        check_detection(expected, 'ics/ppp-pppd/md4.c')

    def test_ics_ppp_pppd_md5_c(self):
        expected = [
            u'Copyright (c) 1990, RSA Data Security, Inc.',
        ]
        check_detection(expected, 'ics/ppp-pppd/md5.c')

    def test_ics_ppp_pppd_md5_h(self):
        expected = [
            u'Copyright (c) 1990, RSA Data Security, Inc.',
        ]
        check_detection(expected, 'ics/ppp-pppd/md5.h')

    def test_ics_ppp_pppd_notice(self):
        expected = [
            u'Copyright (c) 1984-2000 Carnegie Mellon University.',
            u'Copyright (c) 1995 Pedro Roque Marques.',
            u'Copyright (c) 2000-2004 Paul Mackerras.',
            u'Copyright (c) 1994-2002 Paul Mackerras.',
            u'Copyright (c) 2003 Paul Mackerras.',
            u'Copyright (c) 1996-2002 Paul Mackerras.',
            u'Copyright (c) 1999-2004 Paul Mackerras.',
            u'Copyright (c) 2000-2002 Paul Mackerras.',
            u'Copyright (c) 1999-2002 Paul Mackerras.',
            u'Copyright (c) 1995 Eric Rosenquist.',
            u'Copyright (c) 2002 The Android Open Source Project',
            u'Copyright (c) 1990, RSA Data Security, Inc.',
            u'Copyright (c) 2001 by Sun Microsystems, Inc.',
            u'Copyright (c) 1999 Tommi Komulainen.',
            u'Copyright (c) 1995, 1996, 1997 Francis.Dupont@inria.fr, INRIA',
            u'Copyright (c) 1998, 1999 Francis.Dupont@inria.fr',
        ]
        check_detection(expected, 'ics/ppp-pppd/NOTICE')

    def test_ics_ppp_pppd_pppd_8(self):
        expected = [
            u'Copyright (c) 1993-2003 Paul Mackerras <paulus@samba.org>',
            u'Copyright (c) 1984-2000 Carnegie Mellon University.',
            u'Copyright (c) 1993-2004 Paul Mackerras.',
            u'Copyright (c) 1995 Pedro Roque Marques.',
            u'Copyright (c) 1995 Eric Rosenquist.',
            u'Copyright (c) 1999 Tommi Komulainen.',
            u'Copyright (c) Andrew Tridgell 1999',
            u'Copyright (c) 2000 by Sun Microsystems, Inc.',
            u'Copyright (c) 2001 by Sun Microsystems, Inc.',
            u'Copyright (c) 2002 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/ppp-pppd/pppd.8')

    def test_ics_ppp_pppd_pppd_h(self):
        expected = [
            u'Copyright (c) 1984-2000 Carnegie Mellon University.',
        ]
        check_detection(expected, 'ics/ppp-pppd/pppd.h')

    def test_ics_ppp_pppd_sys_linux_c(self):
        expected = [
            u'Copyright (c) 1994-2004 Paul Mackerras.',
            u'Copyright (c) 1984-2000 Carnegie Mellon University.',
        ]
        check_detection(expected, 'ics/ppp-pppd/sys-linux.c')

    def test_ics_ppp_pppd_sys_solaris_c(self):
        expected = [
            u'Copyright (c) 2000 by Sun Microsystems, Inc.',
            u'Copyright (c) 1995-2002 Paul Mackerras.',
            u'Copyright (c) 1984-2000 Carnegie Mellon University.',
        ]
        check_detection(expected, 'ics/ppp-pppd/sys-solaris.c')

    def test_ics_ppp_pppd_tty_c(self):
        expected = [
            u'Copyright (c) 2000-2004 Paul Mackerras.',
            u'Copyright (c) 1984-2000 Carnegie Mellon University.',
        ]
        check_detection(expected, 'ics/ppp-pppd/tty.c')

    def test_ics_ppp_pppd_utils_c(self):
        expected = [
            u'Copyright (c) 1999-2002 Paul Mackerras.',
        ]
        check_detection(expected, 'ics/ppp-pppd/utils.c')

    def test_ics_ppp_pppd_include_net_ppp_defs_h(self):
        expected = [
            u'Copyright (c) 1984 Paul Mackerras.',
        ]
        check_detection(expected, 'ics/ppp-pppd-include-net/ppp_defs.h')

    def test_ics_ppp_pppd_include_net_pppio_h(self):
        expected = [
            u'Copyright (c) 1994 Paul Mackerras.',
        ]
        check_detection(expected, 'ics/ppp-pppd-include-net/pppio.h')

    def test_ics_ppp_pppd_include_net_slcompress_h(self):
        expected = [
            u'Copyright (c) 1989 Regents of the University of California.',
        ]
        check_detection(expected, 'ics/ppp-pppd-include-net/slcompress.h')

    def test_ics_ppp_pppd_plugins_minconn_c(self):
        expected = [
            u'Copyright (c) 1999 Paul Mackerras.',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins/minconn.c')

    def test_ics_ppp_pppd_plugins_passprompt_c(self):
        expected = [
            u'Copyright 1999 Paul Mackerras, Alan Curry.',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins/passprompt.c')

    def test_ics_ppp_pppd_plugins_winbind_c(self):
        expected = [
            u'Copyright (c) 2003 Andrew Bartlet <abartlet@samba.org>',
            u'Copyright 1999 Paul Mackerras, Alan Curry.',
            u'Copyright (c) 2002 Roaring Penguin Software Inc.',
            u'Copyright (c) 1996, Matjaz Godec <gody@elgo.si>',
            u'Copyright (c) 1996, Lars Fenneberg <in5y050@public.uni-hamburg.de>',
            u'Copyright (c) 1997, Miguel A.L. Paraz <map@iphil.net>',
            u'Copyright (c) 1995,1996,1997,1998 Lars Fenneberg <lf@elemental.net>',
            u'Copyright (c) 2002 Roaring Penguin Software Inc.',
            u'Copyright (c) 2003, Sean E. Millichamp',
            u'Copyright (c) Andrew Tridgell 1992-2001',
            u'Copyright (c) Simo Sorce 2001-2002',
            u'Copyright (c) Martin Pool 2003',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins/winbind.c')

    def test_ics_ppp_pppd_plugins_pppoatm_copying(self):
        expected = [
            u'Copyright 1995-2000 EPFL-LRC/ICA',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-pppoatm/COPYING')

    def test_ics_ppp_pppd_plugins_pppoatm_pppoatm_c(self):
        expected = [
            u'Copyright 2000 Mitchell Blank Jr.',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-pppoatm/pppoatm.c')

    def test_ics_ppp_pppd_plugins_radius_avpair_c(self):
        expected = [
            u'Copyright (c) 1995 Lars Fenneberg',
            u'Copyright 1992 Livingston Enterprises, Inc.',
            u'Copyright 1992,1993, 1994,1995 The Regents of the University of Michigan and Merit Network, Inc.',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-radius/avpair.c')

    def test_ics_ppp_pppd_plugins_radius_buildreq_c(self):
        expected = [
            u'Copyright (c) 1995,1997 Lars Fenneberg',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-radius/buildreq.c')

    def test_ics_ppp_pppd_plugins_radius_clientid_c(self):
        expected = [
            u'Copyright (c) 1995,1996,1997 Lars Fenneberg',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-radius/clientid.c')

    def test_ics_ppp_pppd_plugins_radius_config_c(self):
        expected = [
            u'Copyright (c) 1995,1996,1997 Lars Fenneberg',
            u'Copyright 1992 Livingston Enterprises, Inc.',
            u'Copyright 1992,1993, 1994,1995 The Regents of the University of Michigan and Merit Network, Inc.',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-radius/config.c')

    def test_ics_ppp_pppd_plugins_radius_copyright(self):
        expected = [
            u'Copyright (c) 2002 Roaring Penguin Software Inc.',
            u'Copyright (c) 1995,1996,1997,1998 Lars Fenneberg <lf@elemental.net>',
            u'Copyright 1992 Livingston Enterprises, Inc. Livingston Enterprises, Inc.',
            u'Copyright (c) 1991-2, RSA Data Security, Inc.',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-radius/COPYRIGHT')

    def test_ics_ppp_pppd_plugins_radius_dict_c(self):
        expected = [
            u'Copyright (c) 2002 Roaring Penguin Software Inc.',
            u'Copyright (c) 1995,1996,1997 Lars Fenneberg',
            u'Copyright 1992 Livingston Enterprises, Inc.',
            u'Copyright 1992,1993, 1994,1995 The Regents of the University of Michigan and Merit Network, Inc.',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-radius/dict.c')

    def test_ics_ppp_pppd_plugins_radius_includes_h(self):
        expected = [
            u'Copyright (c) 1997 Lars Fenneberg',
            u'Copyright 1992 Livingston Enterprises, Inc.',
            u'Copyright 1992,1993, 1994,1995 The Regents of the University of Michigan and Merit Network, Inc.',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-radius/includes.h')

    def test_ics_ppp_pppd_plugins_radius_lock_c(self):
        expected = [
            u'Copyright (c) 1997 Lars Fenneberg',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-radius/lock.c')

    def test_ics_ppp_pppd_plugins_radius_makefile_linux(self):
        expected = [
            u'Copyright 2002 Roaring Penguin Software Inc.',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-radius/Makefile.linux')

    def test_ics_ppp_pppd_plugins_radius_options_h(self):
        expected = [
            u'Copyright (c) 1996 Lars Fenneberg',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-radius/options.h')

    def test_ics_ppp_pppd_plugins_radius_pathnames_h(self):
        expected = [
            u'Copyright (c) 1995,1996 Lars Fenneberg',
            u'Copyright 1992 Livingston Enterprises, Inc.',
            u'Copyright 1992,1993, 1994,1995 The Regents of the University of Michigan and Merit Network, Inc.',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-radius/pathnames.h')

    def test_ics_ppp_pppd_plugins_radius_radattr_c(self):
        expected = [
            u'Copyright (c) 2002 Roaring Penguin Software Inc.',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-radius/radattr.c')

    def test_ics_ppp_pppd_plugins_radius_radius_c(self):
        expected = [
            u'Copyright (c) 2002 Roaring Penguin Software Inc.',
            u'Copyright (c) 1996, Matjaz Godec <gody@elgo.si>',
            u'Copyright (c) 1996, Lars Fenneberg <in5y050@public.uni-hamburg.de>',
            u'Copyright (c) 1997, Miguel A.L. Paraz <map@iphil.net>',
            u'Copyright (c) 1995,1996,1997,1998 Lars Fenneberg <lf@elemental.net>',
            u'Copyright (c) 2002 Roaring Penguin Software Inc.',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-radius/radius.c')

    def test_ics_ppp_pppd_plugins_radius_radiusclient_h(self):
        expected = [
            u'Copyright (c) 1995,1996,1997,1998 Lars Fenneberg',
            u'Copyright 1992 Livingston Enterprises, Inc.',
            u'Copyright 1992,1993, 1994,1995 The Regents of the University of Michigan and Merit Network, Inc.',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-radius/radiusclient.h')

    def test_ics_ppp_pppd_plugins_radius_radrealms_c(self):
        expected = [
            u'Copyright (c) 2002 Netservers',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-radius/radrealms.c')

    def test_ics_ppp_pppd_plugins_rp_pppoe_common_c(self):
        expected = [
            u'Copyright (c) 2000 by Roaring Penguin Software Inc.',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-rp-pppoe/common.c')

    def test_ics_ppp_pppd_plugins_rp_pppoe_discovery_c(self):
        expected = [
            u'Copyright (c) 1999 by Roaring Penguin Software Inc.',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-rp-pppoe/discovery.c')

    def test_ics_ppp_pppd_plugins_rp_pppoe_makefile_linux(self):
        expected = [
            u'Copyright (c) 2001 Roaring Penguin Software Inc.',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-rp-pppoe/Makefile.linux')

    def test_ics_ppp_pppd_plugins_rp_pppoe_plugin_c(self):
        expected = [
            u'Copyright (c) 2001 by Roaring Penguin Software Inc., Michal Ostrowski and Jamal Hadi Salim.',
            u'Copyright 2000 Michal Ostrowski <mostrows@styx.uwaterloo.ca> , Jamal Hadi Salim <hadi@cyberus.ca>',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-rp-pppoe/plugin.c')

    def test_ics_ppp_pppd_plugins_rp_pppoe_pppoe_h(self):
        expected = [
            u'Copyright (c) 2000 Roaring Penguin Software Inc.',
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-rp-pppoe/pppoe.h')

    def test_ics_ppp_pppd_plugins_rp_pppoe_pppoe_discovery_c_trail_name(self):
        expected = [
            u'Copyright (c) 2000-2001 by Roaring Penguin Software Inc.',
            u"Copyright (c) 2004 Marco d'Itri <md@linux.it>",
        ]
        check_detection(expected, 'ics/ppp-pppd-plugins-rp-pppoe/pppoe-discovery.c')

    def test_ics_proguard_notice(self):
        expected = [
            u'Copyright (c) 2002-2009 Eric Lafortune.',
            u'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, 'ics/proguard/NOTICE')

    def test_ics_proguard_readme(self):
        expected = [
            u'Copyright (c) 2002-2009 Eric Lafortune (eric@graphics.cornell.edu)',
        ]
        check_detection(expected, 'ics/proguard/README')

    def test_ics_proguard_docs_acknowledgements_html(self):
        expected = [
            u"Copyright (c) 2002-2009 <a href http://www.graphics.cornell.edu/~eric/'> Eric Lafortune",
        ]
        check_detection(expected, 'ics/proguard-docs/acknowledgements.html')

    def test_ics_proguard_docs_gpl_html(self):
        expected = [
            u'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, 'ics/proguard-docs/GPL.html')

    def test_ics_proguard_docs_gpl_exception_html(self):
        expected = [
            u'Copyright (c) 2002-2009 Eric Lafortune',
        ]
        check_detection(expected, 'ics/proguard-docs/GPL_exception.html')

    def test_ics_proguard_examples_annotations_src_proguard_annotation_keep_java(self):
        expected = [
            u'Copyright (c) 2002-2007 Eric Lafortune (eric@graphics.cornell.edu)',
        ]
        check_detection(expected, 'ics/proguard-examples-annotations-src-proguard-annotation/Keep.java')

    def test_ics_proguard_src_proguard_argumentwordreader_java(self):
        expected = [
            u'Copyright (c) 2002-2009 Eric Lafortune (eric@graphics.cornell.edu)',
        ]
        check_detection(expected, 'ics/proguard-src-proguard/ArgumentWordReader.java')

    def test_ics_proguard_src_proguard_gui_guiresources_properties(self):
        expected = [
            u'Copyright (c) 2002-2009 Eric Lafortune (eric@graphics.cornell.edu)',
            u'Copyright (c) 2002-2009.',
        ]
        check_detection(expected, 'ics/proguard-src-proguard-gui/GUIResources.properties')

    def test_ics_protobuf_aclocal_m4(self):
        expected = [
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008 Free Software Foundation, Inc.',
            u'Copyright (c) 2002, 2003, 2005, 2006, 2007 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1997, 2000, 2001, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2008 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2002, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1997, 1999, 2000, 2001, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2002, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 2000, 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/protobuf/aclocal.m4')

    def test_ics_protobuf_configure(self):
        expected = [
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2003, 2004, 2005, 2006, 2007, 2008 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/protobuf/configure')

    def test_ics_protobuf_install_txt(self):
        expected = [
            u'Copyright 1994, 1995, 1996, 1999, 2000, 2001, 2002 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/protobuf/INSTALL.txt')

    def test_ics_protobuf_ltmain_sh(self):
        expected = [
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2003, 2004, 2005, 2006, 2007 2008 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/protobuf/ltmain.sh')

    def test_ics_protobuf_readme_txt(self):
        expected = [
            u'Copyright 2008 Google Inc.',
        ]
        check_detection(expected, 'ics/protobuf/README.txt')

    def test_ics_protobuf_editors_proto_vim(self):
        expected = [
            u'Copyright 2008 Google Inc.',
        ]
        check_detection(expected, 'ics/protobuf-editors/proto.vim')

    def test_ics_protobuf_gtest_aclocal_m4(self):
        expected = [
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2003, 2004, 2005, 2006, 2007, 2008 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2003, 2004, 2005, 2006, 2007, 2008 Free Software Foundation, Inc.',
            u'Copyright (c) 2008 Free Software Foundation, Inc.',
            u'Copyright (c) 2004, 2005, 2007, 2008 Free Software Foundation, Inc.',
            u'Copyright (c) 2004, 2005, 2007 Free Software Foundation, Inc.',
            u'Copyright (c) 2004 Free Software Foundation, Inc.',
            u'Copyright (c) 2004, 2005, 2007 Free Software Foundation, Inc.',
            u'Copyright (c) 2002, 2003, 2005, 2006, 2007 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1997, 2000, 2001, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2008 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2002, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1997, 1999, 2000, 2001, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2002, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 2000, 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/protobuf-gtest/aclocal.m4')

    def test_ics_protobuf_gtest_scons_sconscript(self):
        expected = [
            u'Copyright 2008 Google Inc.',
        ]
        check_detection(expected, 'ics/protobuf-gtest-scons/SConscript')

    def test_ics_protobuf_java_src_main_java_com_google_protobuf_abstractmessage_java(self):
        expected = [
            u'Copyright 2008 Google Inc.',
        ]
        check_detection(expected, 'ics/protobuf-java-src-main-java-com-google-protobuf/AbstractMessage.java')

    def test_ics_protobuf_m4_libtool_m4(self):
        expected = [
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2003, 2004, 2005, 2006, 2007, 2008 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2003, 2004, 2005, 2006, 2007, 2008 Free Software Foundation, Inc.',
            u'Copyright (c) 2008 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/protobuf-m4/libtool.m4')

    def test_ics_protobuf_m4_ltoptions_m4(self):
        expected = [
            u'Copyright (c) 2004, 2005, 2007, 2008 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/protobuf-m4/ltoptions.m4')

    def test_ics_protobuf_m4_ltsugar_m4(self):
        expected = [
            u'Copyright (c) 2004, 2005, 2007 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/protobuf-m4/ltsugar.m4')

    def test_ics_protobuf_m4_ltversion_m4(self):
        expected = [
            u'Copyright (c) 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/protobuf-m4/ltversion.m4')

    def test_ics_protobuf_src_google_protobuf_compiler_javamicro_javamicro_params_h(self):
        expected = [
            u'Copyright 2010 Google Inc.',
        ]
        check_detection(expected, 'ics/protobuf-src-google-protobuf-compiler-javamicro/javamicro_params.h')

    def test_ics_protobuf_src_google_protobuf_io_tokenizer_cc(self):
        expected = [
            u'Copyright 2008 Google Inc.',
        ]
        check_detection(expected, 'ics/protobuf-src-google-protobuf-io/tokenizer.cc')

    def test_ics_protobuf_src_google_protobuf_stubs_structurally_valid_cc(self):
        expected = [
            u'Copyright 2005-2008 Google Inc.',
        ]
        check_detection(expected, 'ics/protobuf-src-google-protobuf-stubs/structurally_valid.cc')

    def test_ics_qemu_a_out_h(self):
        expected = [
            u'Copyright 1997, 1998, 1999, 2001 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/qemu/a.out.h')

    def test_ics_qemu_acl_c(self):
        expected = [
            u'Copyright (c) 2009 Red Hat, Inc',
        ]
        check_detection(expected, 'ics/qemu/acl.c')

    def test_ics_qemu_aio_android_c(self):
        expected = [
            u'Copyright IBM, Corp. 2008',
        ]
        check_detection(expected, 'ics/qemu/aio-android.c')

    def test_ics_qemu_android_trace_h(self):
        expected = [
            u'Copyright (c) 2006-2007 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/qemu/android-trace.h')

    def test_ics_qemu_arch_init_c(self):
        expected = [
            u'Copyright (c) 2003-2008 Fabrice Bellard',
        ]
        check_detection(expected, 'ics/qemu/arch_init.c')

    def test_ics_qemu_arm_dis_c(self):
        expected = [
            u'Copyright 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004 2007, Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/qemu/arm-dis.c')

    def test_ics_qemu_arm_semi_c(self):
        expected = [
            u'Copyright (c) 2005, 2007 CodeSourcery.',
        ]
        check_detection(expected, 'ics/qemu/arm-semi.c')

    def test_ics_qemu_block_c(self):
        expected = [
            u'Copyright (c) 2003 Fabrice Bellard',
        ]
        check_detection(expected, 'ics/qemu/block.c')

    def test_ics_qemu_bt_host_c(self):
        expected = [
            u'Copyright (c) 2008 Andrzej Zaborowski <balrog@zabor.org>',
        ]
        check_detection(expected, 'ics/qemu/bt-host.c')

    def test_ics_qemu_console_c(self):
        expected = [
            u'Copyright (c) 2004 Fabrice Bellard',
        ]
        check_detection(expected, 'ics/qemu/console.c')

    def test_ics_qemu_cpu_all_h(self):
        expected = [
            u'Copyright (c) 2003 Fabrice Bellard',
        ]
        check_detection(expected, 'ics/qemu/cpu-all.h')

    def test_ics_qemu_cpu_exec_c(self):
        expected = [
            u'Copyright (c) 2003-2005 Fabrice Bellard',
        ]
        check_detection(expected, 'ics/qemu/cpu-exec.c')

    def test_ics_qemu_curses_c(self):
        expected = [
            u'Copyright (c) 2005 Andrzej Zaborowski <balrog@zabor.org>',
        ]
        check_detection(expected, 'ics/qemu/curses.c')

    def test_ics_qemu_curses_keys_h(self):
        expected = [
            u'Copyright (c) 2005 Andrzej Zaborowski <balrog@zabor.org>',
        ]
        check_detection(expected, 'ics/qemu/curses_keys.h')

    def test_ics_qemu_cutils_c(self):
        expected = [
            u'Copyright (c) 2006 Fabrice Bellard',
        ]
        check_detection(expected, 'ics/qemu/cutils.c')

    def test_ics_qemu_d3des_c(self):
        expected = [
            u'Copyright (c) 1999 AT&T Laboratories Cambridge.',
            u'Copyright (c) 1988,1989,1990,1991,1992 by Richard Outerbridge.',
        ]
        check_detection(expected, 'ics/qemu/d3des.c')

    def test_ics_qemu_d3des_h(self):
        expected = [
            u'Copyright (c) 1999 AT&T Laboratories Cambridge.',
            u'Copyright (c) 1988,1989,1990,1991,1992 by Richard Outerbridge',
        ]
        check_detection(expected, 'ics/qemu/d3des.h')

    def test_ics_qemu_device_tree_c(self):
        expected = [
            u'Copyright 2008 IBM Corporation.',
        ]
        check_detection(expected, 'ics/qemu/device_tree.c')

    def test_ics_qemu_dma_helpers_c(self):
        expected = [
            u'Copyright (c) 2009 Red Hat',
        ]
        check_detection(expected, 'ics/qemu/dma-helpers.c')

    def test_ics_qemu_dynlink_h(self):
        expected = [
            u'Copyright (c) 2008 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/qemu/dynlink.h')

    def test_ics_qemu_dynlink_static_c(self):
        expected = [
            u'Copyright (c) 2010 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/qemu/dynlink-static.c')

    def test_ics_qemu_feature_to_c_sh(self):
        expected = [
            u'Copyright (c) 2007 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/qemu/feature_to_c.sh')

    def test_ics_qemu_hostregs_helper_h(self):
        expected = [
            u'Copyright (c) 2007 CodeSourcery',
        ]
        check_detection(expected, 'ics/qemu/hostregs_helper.h')

    def test_ics_qemu_host_utils_c(self):
        expected = [
            u'Copyright (c) 2003 Fabrice Bellard',
            u'Copyright (c) 2007 Aurelien Jarno',
        ]
        check_detection(expected, 'ics/qemu/host-utils.c')

    def test_ics_qemu_host_utils_h(self):
        expected = [
            u'Copyright (c) 2007 Thiemo Seufer',
            u'Copyright (c) 2007 Jocelyn Mayer',
        ]
        check_detection(expected, 'ics/qemu/host-utils.h')

    def test_ics_qemu_i386_dis_c(self):
        expected = [
            u'Copyright 1988, 1989, 1991, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright 1989, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/qemu/i386-dis.c')

    def test_ics_qemu_json_lexer_c(self):
        expected = [
            u'Copyright IBM, Corp. 2009',
        ]
        check_detection(expected, 'ics/qemu/json-lexer.c')

    def test_ics_qemu_keymaps_c(self):
        expected = [
            u'Copyright (c) 2004 Johannes Schindelin',
        ]
        check_detection(expected, 'ics/qemu/keymaps.c')

    def test_ics_qemu_kqemu_c(self):
        expected = [
            u'Copyright (c) 2005-2008 Fabrice Bellard',
        ]
        check_detection(expected, 'ics/qemu/kqemu.c')

    def test_ics_qemu_kqemu_h(self):
        expected = [
            u'Copyright (c) 2004-2008 Fabrice Bellard',
        ]
        check_detection(expected, 'ics/qemu/kqemu.h')

    def test_ics_qemu_loader_c(self):
        expected = [
            u'Copyright (c) 2006 Fabrice Bellard',
            u'(c) Copyright 2008 Semihalf',
            u'(c) Copyright 2000-2005 Wolfgang Denk, DENX Software Engineering, wd@denx.de.',
        ]
        check_detection(expected, 'ics/qemu/loader.c')

    def test_ics_qemu_migration_exec_c(self):
        expected = [
            u'Copyright IBM, Corp. 2008',
            u'Copyright Dell MessageOne 2008',
        ]
        check_detection(expected, 'ics/qemu/migration-exec.c')

    def test_ics_qemu_monitor_c(self):
        expected = [
            u'Copyright (c) 2003-2004 Fabrice Bellard',
        ]
        check_detection(expected, 'ics/qemu/monitor.c')

    def test_ics_qemu_net_checksum_c(self):
        expected = [
            u'(c) 2008 Gerd Hoffmann <kraxel@redhat.com>',
        ]
        check_detection(expected, 'ics/qemu/net-checksum.c')

    def test_ics_qemu_notify_c(self):
        expected = [
            u'Copyright IBM, Corp. 2010',
        ]
        check_detection(expected, 'ics/qemu/notify.c')

    def test_ics_qemu_os_posix_c(self):
        expected = [
            u'Copyright (c) 2003-2008 Fabrice Bellard',
            u'Copyright (c) 2010 Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/qemu/os-posix.c')

    def test_ics_qemu_ppc_dis_c(self):
        expected = [
            u'Copyright 1994, 1995, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007 Free Software Foundation, Inc.',
            u'Copyright 1994, 1995, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007 Free Software Foundation, Inc.',
            u'Copyright 1994, 1995, 1996, 1997, 1998, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/qemu/ppc-dis.c')

    def test_ics_qemu_qdict_c(self):
        expected = [
            u'Copyright (c) 2009 Red Hat Inc.',
        ]
        check_detection(expected, 'ics/qemu/qdict.c')

    def test_ics_qemu_qemu_error_c(self):
        expected = [
            u'Copyright (c) 2010 Red Hat Inc.',
        ]
        check_detection(expected, 'ics/qemu/qemu-error.c')

    def test_ics_qemu_qemu_io_c(self):
        expected = [
            u'Copyright (c) 2009 Red Hat, Inc.',
            u'Copyright (c) 2003-2005 Silicon Graphics, Inc.',
        ]
        check_detection(expected, 'ics/qemu/qemu-io.c')

    def test_ics_qemu_qemu_option_c(self):
        expected = [
            u'Copyright (c) 2003-2008 Fabrice Bellard',
            u'Copyright (c) 2009 Kevin Wolf <kwolf@redhat.com>',
        ]
        check_detection(expected, 'ics/qemu/qemu-option.c')

    def test_ics_qemu_qemu_options_h(self):
        expected = [
            u'Copyright (c) 2003-2008 Fabrice Bellard',
            u'Copyright (c) 2010 Jes Sorensen <Jes.Sorensen@redhat.com>',
        ]
        check_detection(expected, 'ics/qemu/qemu-options.h')

    def test_ics_qemu_qemu_thread_c(self):
        expected = [
            u'Copyright Red Hat, Inc. 2009',
        ]
        check_detection(expected, 'ics/qemu/qemu-thread.c')

    def test_ics_qemu_softmmu_outside_jit_c(self):
        expected = [
            u'Copyright (c) 2007-2009 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/qemu/softmmu_outside_jit.c')

    def test_ics_qemu_softmmu_semi_h(self):
        expected = [
            u'Copyright (c) 2007 CodeSourcery.',
        ]
        check_detection(expected, 'ics/qemu/softmmu-semi.h')

    def test_ics_qemu_sys_tree_h(self):
        expected = [
            u'Copyright 2002 Niels Provos <provos@citi.umich.edu>',
        ]
        check_detection(expected, 'ics/qemu/sys-tree.h')

    def test_ics_qemu_tap_win32_c(self):
        expected = [
            u'Copyright (c) Damion K. Wilson, 2003',
            u'Copyright (c) James Yonan, 2003-2004',
        ]
        check_detection(expected, 'ics/qemu/tap-win32.c')

    def test_ics_qemu_tcpdump_c(self):
        expected = [
            u'Copyright (c) 2008 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/qemu/tcpdump.c')

    def test_ics_qemu_uboot_image_h(self):
        expected = [
            u'(c) Copyright 2000-2005 Wolfgang Denk, DENX Software Engineering, wd@denx.de.',
        ]
        check_detection(expected, 'ics/qemu/uboot_image.h')

    def test_ics_qemu_usb_linux_c(self):
        expected = [
            u'Copyright (c) 2005 Fabrice Bellard',
            u'Copyright (c) 2008 Max Krasnyansky',
            u'Copyright 2008 TJ <linux@tjworld.net>',
        ]
        check_detection(expected, 'ics/qemu/usb-linux.c')

    def test_ics_qemu_vl_android_c(self):
        expected = [
            u'Copyright (c) 2003-2008 Fabrice Bellard',
            u'Copyright (c) 2003-2008 Fabrice Bellard',
        ]
        check_detection(expected, 'ics/qemu/vl-android.c')

    def test_ics_qemu_vnc_android_c(self):
        expected = [
            u'Copyright (c) 2006 Anthony Liguori <anthony@codemonkey.ws>',
            u'Copyright (c) 2006 Fabrice Bellard',
            u'Copyright (c) 2009 Red Hat, Inc',
        ]
        check_detection(expected, 'ics/qemu/vnc-android.c')

    def test_ics_qemu_android_android_h(self):
        expected = [
            u'Copyright (c) 2007 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/qemu-android/android.h')

    def test_ics_qemu_android_main_c(self):
        expected = [
            u'Copyright (c) 2006-2008 The Android Open Source Project',
            u'Copyright (c) 2006-2011 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/qemu-android/main.c')

    def test_ics_qemu_android_main_common_c(self):
        expected = [
            u'Copyright (c) 2011 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/qemu-android/main-common.c')

    def test_ics_qemu_android_qemu_setup_c(self):
        expected = [
            u'Copyright (c) 2006-2010 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/qemu-android/qemu-setup.c')

    def test_ics_qemu_android_snapshot_c(self):
        expected = [
            u'Copyright (c) 2010 The Android Open Source Project',
            u'copyright (c) 2003 Fabrice Bellard',
        ]
        check_detection(expected, 'ics/qemu-android/snapshot.c')

    def test_ics_qemu_android_utils_mapfile_c(self):
        expected = [
            u'Copyright (c) 2007-2010 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/qemu-android-utils/mapfile.c')

    def test_ics_qemu_audio_alsaaudio_c(self):
        expected = [
            u'Copyright (c) 2008-2010 The Android Open Source Project',
            u'Copyright (c) 2005 Vassili Karpov',
        ]
        check_detection(expected, 'ics/qemu-audio/alsaaudio.c')

    def test_ics_qemu_audio_audio_c(self):
        expected = [
            u'Copyright (c) 2007-2008 The Android Open Source Project',
            u'Copyright (c) 2003-2005 Vassili Karpov',
        ]
        check_detection(expected, 'ics/qemu-audio/audio.c')

    def test_ics_qemu_audio_audio_h(self):
        expected = [
            u'Copyright (c) 2003-2005 Vassili Karpov',
        ]
        check_detection(expected, 'ics/qemu-audio/audio.h')

    def test_ics_qemu_audio_audio_template_h(self):
        expected = [
            u'Copyright (c) 2005 Vassili Karpov',
        ]
        check_detection(expected, 'ics/qemu-audio/audio_template.h')

    def test_ics_qemu_audio_coreaudio_c(self):
        expected = [
            u'Copyright (c) 2008 The Android Open Source Project',
            u'Copyright (c) 2005 Mike Kronenberg',
        ]
        check_detection(expected, 'ics/qemu-audio/coreaudio.c')

    def test_ics_qemu_audio_esdaudio_c(self):
        expected = [
            u'Copyright (c) 2008-2009 The Android Open Source Project',
            u'Copyright (c) 2006 Frederick Reeve',
        ]
        check_detection(expected, 'ics/qemu-audio/esdaudio.c')

    def test_ics_qemu_audio_fmodaudio_c(self):
        expected = [
            u'Copyright (c) 2004-2005 Vassili Karpov',
        ]
        check_detection(expected, 'ics/qemu-audio/fmodaudio.c')

    def test_ics_qemu_audio_mixeng_c(self):
        expected = [
            u'Copyright (c) 2004-2005 Vassili Karpov',
            u'Copyright (c) 1998 Fabrice Bellard',
            u'Copyright 1998 Fabrice Bellard.',
        ]
        check_detection(expected, 'ics/qemu-audio/mixeng.c')

    def test_ics_qemu_audio_rate_template_h(self):
        expected = [
            u'Copyright (c) 2004-2005 Vassili Karpov',
            u'Copyright (c) 1998 Fabrice Bellard',
        ]
        check_detection(expected, 'ics/qemu-audio/rate_template.h')

    def test_ics_qemu_audio_wavaudio_c(self):
        expected = [
            u'Copyright (c) 2007 The Android Open Source Project',
            u'Copyright (c) 2004-2005 Vassili Karpov',
        ]
        check_detection(expected, 'ics/qemu-audio/wavaudio.c')

    def test_ics_qemu_audio_winaudio_c(self):
        expected = [
            u'Copyright (c) 2007 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/qemu-audio/winaudio.c')

    def test_ics_qemu_block_bochs_c(self):
        expected = [
            u'Copyright (c) 2005 Alex Beregszaszi',
        ]
        check_detection(expected, 'ics/qemu-block/bochs.c')

    def test_ics_qemu_block_cloop_c(self):
        expected = [
            u'Copyright (c) 2004 Johannes E. Schindelin',
        ]
        check_detection(expected, 'ics/qemu-block/cloop.c')

    def test_ics_qemu_block_nbd_c(self):
        expected = [
            u'Copyright (c) 2008 Bull S.A.S.',
            u'Copyright (c) 2007 Anthony Liguori <anthony@codemonkey.ws>',
        ]
        check_detection(expected, 'ics/qemu-block/nbd.c')

    def test_ics_qemu_block_parallels_c(self):
        expected = [
            u'Copyright (c) 2007 Alex Beregszaszi',
        ]
        check_detection(expected, 'ics/qemu-block/parallels.c')

    def test_ics_qemu_block_qcow_c(self):
        expected = [
            u'Copyright (c) 2004-2006 Fabrice Bellard',
        ]
        check_detection(expected, 'ics/qemu-block/qcow.c')

    def test_ics_qemu_block_vmdk_c(self):
        expected = [
            u'Copyright (c) 2004 Fabrice Bellard',
            u'Copyright (c) 2005 Filip Navara',
        ]
        check_detection(expected, 'ics/qemu-block/vmdk.c')

    def test_ics_qemu_block_vpc_c(self):
        expected = [
            u'Copyright (c) 2005 Alex Beregszaszi',
            u'Copyright (c) 2009 Kevin Wolf <kwolf@suse.de>',
        ]
        check_detection(expected, 'ics/qemu-block/vpc.c')

    def test_ics_qemu_block_vvfat_c(self):
        expected = [
            u'Copyright (c) 2004,2005 Johannes E. Schindelin',
        ]
        check_detection(expected, 'ics/qemu-block/vvfat.c')

    def test_ics_qemu_distrib_libpng_1_2_19_png_c(self):
        expected = [
            u'Copyright (c) 1998-2007 Glenn Randers-Pehrson',
            u'Copyright (c) 1996, 1997 Andreas Dilger',
            u'Copyright (c) 1995, 1996 Guy Eric Schalnat, Group 42, Inc.',
            u'Copyright (c) 1998-2007 Glenn Randers-Pehrson',
            u'Copyright (c) 1996-1997 Andreas Dilger',
            u'Copyright (c) 1995-1996 Guy Eric Schalnat, Group 42, Inc.',
        ]
        check_detection(expected, 'ics/qemu-distrib-libpng-1.2.19/png.c')

    def test_ics_qemu_distrib_libpng_1_2_19_png_h(self):
        expected = [
            u'Copyright (c) 1998-2007 Glenn Randers-Pehrson',
            u'Copyright (c) 1996, 1997 Andreas Dilger',
            u'Copyright (c) 1995, 1996 Guy Eric Schalnat, Group 42, Inc.',
            u'Copyright (c) 2004, 2006-2007 Glenn Randers-Pehrson',
            u'Copyright (c) 2000-2002 Glenn Randers-Pehrson',
            u'Copyright (c) 1998, 1999, 2000 Glenn Randers-Pehrson',
            u'Copyright (c) 1996, 1997 Andreas Dilger',
            u'Copyright (c) 1995, 1996 Guy Eric Schalnat, Group 42, Inc.',
        ]
        check_detection(expected, 'ics/qemu-distrib-libpng-1.2.19/png.h')

    def test_ics_qemu_distrib_libpng_1_2_19_pngconf_h(self):
        expected = [
            u'Copyright (c) 1998-2007 Glenn Randers-Pehrson',
            u'Copyright (c) 1996, 1997 Andreas Dilger',
            u'Copyright (c) 1995, 1996 Guy Eric Schalnat, Group 42, Inc.',
        ]
        check_detection(expected, 'ics/qemu-distrib-libpng-1.2.19/pngconf.h')

    def test_ics_qemu_distrib_libpng_1_2_19_pngerror_c(self):
        expected = [
            u'Copyright (c) 1998-2007 Glenn Randers-Pehrson',
            u'Copyright (c) 1996, 1997 Andreas Dilger',
            u'Copyright (c) 1995, 1996 Guy Eric Schalnat, Group 42, Inc.',
        ]
        check_detection(expected, 'ics/qemu-distrib-libpng-1.2.19/pngerror.c')

    def test_ics_qemu_distrib_libpng_1_2_19_pnggccrd_c(self):
        expected = [
            u'Copyright (c) 1998 Intel Corporation',
            u'Copyright (c) 1999-2002,2007 Greg Roelofs',
            u'Copyright (c) 1998-2007 Glenn Randers-Pehrson',
        ]
        check_detection(expected, 'ics/qemu-distrib-libpng-1.2.19/pnggccrd.c')

    def test_ics_qemu_distrib_libpng_1_2_19_pngmem_c(self):
        expected = [
            u'Copyright (c) 1998-2006 Glenn Randers-Pehrson',
            u'Copyright (c) 1996, 1997 Andreas Dilger',
            u'Copyright (c) 1995, 1996 Guy Eric Schalnat, Group 42, Inc.',
        ]
        check_detection(expected, 'ics/qemu-distrib-libpng-1.2.19/pngmem.c')

    def test_ics_qemu_distrib_libpng_1_2_19_pngrtran_c(self):
        expected = [
            u'Copyright (c) 1998-2007 Glenn Randers-Pehrson',
            u'Copyright (c) 1996, 1997 Andreas Dilger',
            u'Copyright (c) 1995, 1996 Guy Eric Schalnat, Group 42, Inc.',
            u'Copyright (c) 1998-01-04 Charles Poynton poynton at inforamp.net',
        ]
        check_detection(expected, 'ics/qemu-distrib-libpng-1.2.19/pngrtran.c')

    def test_ics_qemu_distrib_libpng_1_2_19_pngvcrd_c(self):
        expected = [
            u'Copyright (c) 1998-2007 Glenn Randers-Pehrson',
            u'Copyright (c) 1998, Intel Corporation',
        ]
        check_detection(expected, 'ics/qemu-distrib-libpng-1.2.19/pngvcrd.c')

    def test_ics_qemu_distrib_sdl_1_2_12_copying(self):
        expected = [
            u'Copyright (c) 1991, 1999 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12/COPYING')

    def test_ics_qemu_distrib_sdl_1_2_12_include_begin_code_h(self):
        expected = [
            u'Copyright (c) 1997-2004 Sam Lantinga',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-include/begin_code.h')

    def test_ics_qemu_distrib_sdl_1_2_12_include_sdl_h(self):
        expected = [
            u'Copyright (c) 1997-2006 Sam Lantinga',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-include/SDL.h')

    def test_ics_qemu_distrib_sdl_1_2_12_include_sdl_opengl_h(self):
        expected = [
            u'Copyright (c) 1997-2006 Sam Lantinga',
            u'Copyright (c) 1991-2004 Silicon Graphics, Inc.',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-include/SDL_opengl.h')

    def test_ics_qemu_distrib_sdl_1_2_12_src_audio_sdl_mixer_mmx_c(self):
        expected = [
            u'Copyright (c) 1997-2006 Sam Lantinga',
            u'Copyright 2002 Stephane Marchesin (stephane.marchesin@wanadoo.fr)',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-audio/SDL_mixer_MMX.c')

    def test_ics_qemu_distrib_sdl_1_2_12_src_audio_sdl_mixer_mmx_h(self):
        expected = [
            u'Copyright 2002 Stephane Marchesin (stephane.marchesin@wanadoo.fr)',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-audio/SDL_mixer_MMX.h')

    def test_ics_qemu_distrib_sdl_1_2_12_src_audio_dc_aica_c(self):
        expected = [
            u'(c) 2000 Dan Potter',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-audio-dc/aica.c')

    def test_ics_qemu_distrib_sdl_1_2_12_src_audio_sun_sdl_sunaudio_c_trail_name(self):
        expected = [
            u'Copyright (c) 1997-2006 Sam Lantinga',
            u'Copyright 1989 by Rich Gopstein and Harris Corporation',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-audio-sun/SDL_sunaudio.c')

    def test_ics_qemu_distrib_sdl_1_2_12_src_cdrom_macosx_audiofileplayer_c(self):
        expected = [
            u'Copyright (c) 1997, 1998, 1999, 2000, 2001, 2002 Sam Lantinga',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-cdrom-macosx/AudioFilePlayer.c')

    def test_ics_qemu_distrib_sdl_1_2_12_src_cdrom_macosx_sdlosxcaguard_c(self):
        expected = [
            u'Copyright (c) 1997, 1998, 1999, 2000, 2001, 2002 Sam Lantinga',
            u'(c) Copyright 2002 Apple Computer, Inc.',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-cdrom-macosx/SDLOSXCAGuard.c')

    def test_ics_qemu_distrib_sdl_1_2_12_src_cdrom_macosx_sdlosxcaguard_h(self):
        expected = [
            u'Copyright (c) 1997-2004 Sam Lantinga',
            u'(c) Copyright 2002 Apple Computer, Inc.',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-cdrom-macosx/SDLOSXCAGuard.h')

    def test_ics_qemu_distrib_sdl_1_2_12_src_cdrom_osf_sdl_syscdrom_c(self):
        expected = [
            u'DirectMedia Layer Copyright (c) 2003',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-cdrom-osf/SDL_syscdrom.c')

    def test_ics_qemu_distrib_sdl_1_2_12_src_hermes_copying_lib(self):
        expected = [
            u'Copyright (c) 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-hermes/COPYING.LIB')

    def test_ics_qemu_distrib_sdl_1_2_12_src_hermes_headmmx_h(self):
        expected = [
            u'Copyright (c) 1998 Christian Nentwich (c.nentwich@cs.ucl.ac.uk)',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-hermes/HeadMMX.h')

    def test_ics_qemu_distrib_sdl_1_2_12_src_hermes_headx86_h(self):
        expected = [
            u'Copyright (c) 1998 Christian Nentwich (brn@eleet.mcb.at)',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-hermes/HeadX86.h')

    def test_ics_qemu_distrib_sdl_1_2_12_src_hermes_readme(self):
        expected = [
            u'(c) 1998 Christian Nentwich',
            u'(c) Glenn Fielder (gaffer@gaffer.org)',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-hermes/README')

    def test_ics_qemu_distrib_sdl_1_2_12_src_joystick_os2_joyos2_h(self):
        expected = [
            u'Copyright (c) 1995 IBM Corporation',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-joystick-os2/joyos2.h')

    def test_ics_qemu_distrib_sdl_1_2_12_src_loadso_macosx_sdl_dlcompat_c(self):
        expected = [
            u'Copyright (c) 1997-2006 Sam Lantinga',
            u"Copyright (c) 2002 Jorge Acereda <jacereda@users.sourceforge.net> & Peter O'Gorman <ogorman@users.sourceforge.net>",
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-loadso-macosx/SDL_dlcompat.c')

    def test_ics_qemu_distrib_sdl_1_2_12_src_main_win32_version_rc(self):
        expected = [
            u'Copyright (c) 2007 Sam Lantinga',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-main-win32/version.rc')

    def test_ics_qemu_distrib_sdl_1_2_12_src_stdlib_sdl_qsort_c(self):
        expected = [
            u'(c) 1998 Gareth McCaughan',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-stdlib/SDL_qsort.c')

    def test_ics_qemu_distrib_sdl_1_2_12_src_thread_win32_win_ce_semaphore_c(self):
        expected = [
            u'Copyright (c) 1998, Johnson M. Hart',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-thread-win32/win_ce_semaphore.c')

    def test_ics_qemu_distrib_sdl_1_2_12_src_timer_macos_fasttimes_c(self):
        expected = [
            u'Copyright (c) Matt Slot, 1999-2000.',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-timer-macos/FastTimes.c')

    def test_ics_qemu_distrib_sdl_1_2_12_src_video_sdl_yuv_sw_c(self):
        expected = [
            u'Copyright (c) 1997-2006 Sam Lantinga',
            u'Copyright (c) 1995 The Regents of the University of California.',
            u'Copyright (c) 1995 Erik Corry',
            u'Copyright (c) 1995 Brown University.',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-video/SDL_yuv_sw.c')

    def test_ics_qemu_distrib_sdl_1_2_12_src_video_fbcon_matrox_regs_h(self):
        expected = [
            u'Copyright 1996 The XFree86 Project, Inc.',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-video-fbcon/matrox_regs.h')

    def test_ics_qemu_distrib_sdl_1_2_12_src_video_fbcon_riva_mmio_h(self):
        expected = [
            u'Copyright 1993-1999 NVIDIA, Corporation.',
            u'Copyright 1993-1999 NVIDIA, Corporation.',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-video-fbcon/riva_mmio.h')

    def test_ics_qemu_distrib_sdl_1_2_12_src_video_maccommon_sdl_macwm_c(self):
        expected = [
            u'Copyright (c) 1997-2006 Sam Lantinga',
            u'Copyright (c) 1999 Apple Computer, Inc.',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-video-maccommon/SDL_macwm.c')

    def test_ics_qemu_distrib_sdl_1_2_12_src_video_nanox_sdl_nxevents_c(self):
        expected = [
            u'Copyright (c) 1997-2004 Sam Lantinga',
            u'Copyright (c) 2001 Hsieh-Fu Tsai',
            u'Copyright (c) 2002 Greg Haerr <greg@censoft.com>',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-video-nanox/SDL_nxevents.c')

    def test_ics_qemu_distrib_sdl_1_2_12_src_video_nanox_sdl_nxevents_c_h(self):
        expected = [
            u'Copyright (c) 1997-2004 Sam Lantinga',
            u'Copyright (c) 2001 Hsieh-Fu Tsai',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-video-nanox/SDL_nxevents_c.h')

    def test_ics_qemu_distrib_sdl_1_2_12_src_video_quartz_cgs_h(self):
        expected = [
            u'Copyright (c) 1997-2003 Sam Lantinga',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-video-quartz/CGS.h')

    def test_ics_qemu_distrib_sdl_1_2_12_src_video_xext_extensions_extutil_h(self):
        expected = [
            u'Copyright 1989, 1998 The Open Group',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-video-Xext-extensions/extutil.h')

    def test_ics_qemu_distrib_sdl_1_2_12_src_video_xext_extensions_panoramixext_h(self):
        expected = [
            u'Copyright (c) 1991, 1997 Digital Equipment Corporation, Maynard, Massachusetts.',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-video-Xext-extensions/panoramiXext.h')

    def test_ics_qemu_distrib_sdl_1_2_12_src_video_xext_extensions_xf86dga_h(self):
        expected = [
            u'Copyright (c) 1999 XFree86 Inc',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-video-Xext-extensions/xf86dga.h')

    def test_ics_qemu_distrib_sdl_1_2_12_src_video_xext_extensions_xf86dga1_h(self):
        expected = [
            u'Copyright (c) 1995 Jon Tombs',
            u'Copyright (c) 1995 XFree86 Inc',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-video-Xext-extensions/xf86dga1.h')

    def test_ics_qemu_distrib_sdl_1_2_12_src_video_xext_extensions_xf86dga1str_h(self):
        expected = [
            u'Copyright (c) 1995 Jon Tombs',
            u'Copyright (c) 1995 XFree86 Inc.',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-video-Xext-extensions/xf86dga1str.h')

    def test_ics_qemu_distrib_sdl_1_2_12_src_video_xext_extensions_xf86vmode_h_trail_caps(self):
        expected = [
            u'Copyright 1995 Kaleb S. KEITHLEY',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-video-Xext-extensions/xf86vmode.h')

    def test_ics_qemu_distrib_sdl_1_2_12_src_video_xext_extensions_xme_h(self):
        expected = [
            u'Copyright 1993-2001 by Xi Graphics, Inc.',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-video-Xext-extensions/xme.h')

    def test_ics_qemu_distrib_sdl_1_2_12_src_video_xext_extensions_xv_h_trail_name(self):
        expected = [
            u'Copyright 1991 by Digital Equipment Corporation, Maynard, Massachusetts, and the Massachusetts Institute of Technology, Cambridge, Massachusetts.',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-video-Xext-extensions/Xv.h')

    def test_ics_qemu_distrib_sdl_1_2_12_src_video_xext_xv_xvlibint_h(self):
        expected = [
            u'Copyright 1987 by Digital Equipment Corporation, Maynard, Massachusetts, and the Massachusetts Institute of Technology, Cambridge, Massachusetts.',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-video-Xext-Xv/Xvlibint.h')

    def test_ics_qemu_distrib_sdl_1_2_12_src_video_xext_xxf86dga_xf86dga_c(self):
        expected = [
            u'Copyright (c) 1995 Jon Tombs',
            u'Copyright (c) 1995,1996 The XFree86 Project, Inc',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-video-Xext-Xxf86dga/XF86DGA.c')

    def test_ics_qemu_distrib_sdl_1_2_12_src_video_xext_xxf86vm_xf86vmode_c_trail_caps(self):
        expected = [
            u'Copyright (c) 1995 Kaleb S. KEITHLEY',
        ]
        check_detection(expected, 'ics/qemu-distrib-sdl-1.2.12-src-video-Xext-Xxf86vm/XF86VMode.c')

    def test_ics_qemu_distrib_zlib_1_2_3_compress_c(self):
        expected = [
            u'Copyright (c) 1995-2003 Jean-loup Gailly.',
        ]
        check_detection(expected, 'ics/qemu-distrib-zlib-1.2.3/compress.c')

    def test_ics_qemu_distrib_zlib_1_2_3_crc32_c(self):
        expected = [
            u'Copyright (c) 1995-2005 Mark Adler',
        ]
        check_detection(expected, 'ics/qemu-distrib-zlib-1.2.3/crc32.c')

    def test_ics_qemu_distrib_zlib_1_2_3_deflate_c(self):
        expected = [
            u'Copyright (c) 1995-2005 Jean-loup Gailly.',
            u'Copyright 1995-2005 Jean-loup Gailly',
        ]
        check_detection(expected, 'ics/qemu-distrib-zlib-1.2.3/deflate.c')

    def test_ics_qemu_distrib_zlib_1_2_3_deflate_h(self):
        expected = [
            u'Copyright (c) 1995-2004 Jean-loup Gailly',
        ]
        check_detection(expected, 'ics/qemu-distrib-zlib-1.2.3/deflate.h')

    def test_ics_qemu_distrib_zlib_1_2_3_gzio_c(self):
        expected = [
            u'Copyright (c) 1995-2005 Jean-loup Gailly.',
        ]
        check_detection(expected, 'ics/qemu-distrib-zlib-1.2.3/gzio.c')

    def test_ics_qemu_distrib_zlib_1_2_3_inffast_h(self):
        expected = [
            u'Copyright (c) 1995-2003 Mark Adler',
        ]
        check_detection(expected, 'ics/qemu-distrib-zlib-1.2.3/inffast.h')

    def test_ics_qemu_distrib_zlib_1_2_3_inftrees_c(self):
        expected = [
            u'Copyright (c) 1995-2005 Mark Adler',
            u'Copyright 1995-2005 Mark Adler',
        ]
        check_detection(expected, 'ics/qemu-distrib-zlib-1.2.3/inftrees.c')

    def test_ics_qemu_distrib_zlib_1_2_3_trees_c(self):
        expected = [
            u'Copyright (c) 1995-2005 Jean-loup Gailly',
        ]
        check_detection(expected, 'ics/qemu-distrib-zlib-1.2.3/trees.c')

    def test_ics_qemu_elff_dwarf_h(self):
        expected = [
            u'Copyright (c) 2000,2001,2003,2004,2005,2006 Silicon Graphics, Inc.',
            u'Portions Copyright 2002,2007 Sun Microsystems, Inc.',
            u'Portions Copyright 2007-2009 David Anderson.',
        ]
        check_detection(expected, 'ics/qemu-elff/dwarf.h')

    def test_ics_qemu_gdb_xml_arm_core_xml(self):
        expected = [
            u'Copyright (c) 2008 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/qemu-gdb-xml/arm-core.xml')

    def test_ics_qemu_gdb_xml_power_altivec_xml(self):
        expected = [
            u'Copyright (c) 2007, 2008 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/qemu-gdb-xml/power-altivec.xml')

    def test_ics_qemu_hw_apic_c(self):
        expected = [
            u'Copyright (c) 2004-2005 Fabrice Bellard',
        ]
        check_detection(expected, 'ics/qemu-hw/apic.c')

    def test_ics_qemu_hw_arm_misc_h(self):
        expected = [
            u'Copyright (c) 2006 CodeSourcery.',
        ]
        check_detection(expected, 'ics/qemu-hw/arm-misc.h')

    def test_ics_qemu_hw_armv7m_c(self):
        expected = [
            u'Copyright (c) 2006-2007 CodeSourcery.',
        ]
        check_detection(expected, 'ics/qemu-hw/armv7m.c')

    def test_ics_qemu_hw_baum_h(self):
        expected = [
            u'Copyright (c) 2008 Samuel Thibault',
        ]
        check_detection(expected, 'ics/qemu-hw/baum.h')

    def test_ics_qemu_hw_bt_h(self):
        expected = [
            u'Copyright (c) 2007 OpenMoko, Inc.',
            u'Copyright (c) 2000-2001 Qualcomm Incorporated',
            u'Copyright (c) 2002-2003 Maxim Krasnyansky <maxk@qualcomm.com>',
            u'Copyright (c) 2002-2006 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, 'ics/qemu-hw/bt.h')

    def test_ics_qemu_hw_bt_hci_c(self):
        expected = [
            u'Copyright (c) 2007 OpenMoko, Inc.',
            u'Copyright (c) 2008 Andrzej Zaborowski <balrog@zabor.org>',
        ]
        check_detection(expected, 'ics/qemu-hw/bt-hci.c')

    def test_ics_qemu_hw_bt_hid_c(self):
        expected = [
            u'Copyright (c) 2007-2008 OpenMoko, Inc.',
        ]
        check_detection(expected, 'ics/qemu-hw/bt-hid.c')

    def test_ics_qemu_hw_dma_c(self):
        expected = [
            u'Copyright (c) 2003-2004 Vassili Karpov',
        ]
        check_detection(expected, 'ics/qemu-hw/dma.c')

    def test_ics_qemu_hw_fw_cfg_c(self):
        expected = [
            u'Copyright (c) 2008 Gleb Natapov',
        ]
        check_detection(expected, 'ics/qemu-hw/fw_cfg.c')

    def test_ics_qemu_hw_irq_c(self):
        expected = [
            u'Copyright (c) 2007 CodeSourcery.',
        ]
        check_detection(expected, 'ics/qemu-hw/irq.c')

    def test_ics_qemu_hw_mmc_h(self):
        expected = [
            u'Copyright 2002 Hewlett-Packard Company',
        ]
        check_detection(expected, 'ics/qemu-hw/mmc.h')

    def test_ics_qemu_hw_msmouse_c(self):
        expected = [
            u'Copyright (c) 2008 Lubomir Rintel',
        ]
        check_detection(expected, 'ics/qemu-hw/msmouse.c')

    def test_ics_qemu_hw_power_supply_h(self):
        expected = [
            u'Copyright (c) 2007 Anton Vorontsov <cbou@mail.ru>',
            u'Copyright (c) 2004 Szabolcs Gyurko',
            u'Copyright (c) 2003 Ian Molton <spyro@f2s.com>',
        ]
        check_detection(expected, 'ics/qemu-hw/power_supply.h')

    def test_ics_qemu_hw_pxa_h(self):
        expected = [
            u'Copyright (c) 2006 Openedhand Ltd.',
        ]
        check_detection(expected, 'ics/qemu-hw/pxa.h')

    def test_ics_qemu_hw_qdev_c(self):
        expected = [
            u'Copyright (c) 2009 CodeSourcery',
        ]
        check_detection(expected, 'ics/qemu-hw/qdev.c')

    def test_ics_qemu_hw_sd_h(self):
        expected = [
            u'Copyright (c) 2005-2007 Pierre Ossman',
        ]
        check_detection(expected, 'ics/qemu-hw/sd.h')

    def test_ics_qemu_hw_smbios_c(self):
        expected = [
            u'Copyright (c) 2009 Hewlett-Packard Development Company, L.P.',
        ]
        check_detection(expected, 'ics/qemu-hw/smbios.c')

    def test_ics_qemu_hw_smc91c111_c(self):
        expected = [
            u'Copyright (c) 2005 CodeSourcery, LLC.',
        ]
        check_detection(expected, 'ics/qemu-hw/smc91c111.c')

    def test_ics_qemu_hw_usb_hid_c(self):
        expected = [
            u'Copyright (c) 2005 Fabrice Bellard',
            u'Copyright (c) 2007 OpenMoko, Inc.',
        ]
        check_detection(expected, 'ics/qemu-hw/usb-hid.c')

    def test_ics_qemu_hw_usb_hub_c(self):
        expected = [
            u'Copyright (c) 2005 Fabrice Bellard',
        ]
        check_detection(expected, 'ics/qemu-hw/usb-hub.c')

    def test_ics_qemu_hw_usb_ohci_c(self):
        expected = [
            u'Copyright (c) 2004 Gianni Tedesco',
            u'Copyright (c) 2006 CodeSourcery',
            u'Copyright (c) 2006 Openedhand Ltd.',
        ]
        check_detection(expected, 'ics/qemu-hw/usb-ohci.c')

    def test_ics_qemu_pc_bios_bochs_bochs_h(self):
        expected = [
            u'Copyright (c) 2002 MandrakeSoft S.A.',
        ]
        check_detection(expected, 'ics/qemu-pc-bios-bochs/bochs.h')

    def test_ics_qemu_pc_bios_bochs_config_h_in(self):
        expected = [
            u'Copyright (c) 2001 MandrakeSoft S.A.',
        ]
        check_detection(expected, 'ics/qemu-pc-bios-bochs/config.h.in')

    def test_ics_qemu_pc_bios_bochs_configure(self):
        expected = [
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001 Free Software Foundation, Inc.',
            u'Copyright (c) 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/qemu-pc-bios-bochs/configure')

    def test_ics_qemu_pc_bios_bochs_makefile_in(self):
        expected = [
            u'Copyright (c) 2002 MandrakeSoft S.A.',
        ]
        check_detection(expected, 'ics/qemu-pc-bios-bochs/Makefile.in')

    def test_ics_qemu_pc_bios_bochs_bios_acpi_dsdt_dsl(self):
        expected = [
            u'Copyright (c) 2006 Fabrice Bellard',
        ]
        check_detection(expected, 'ics/qemu-pc-bios-bochs-bios/acpi-dsdt.dsl')

    def test_ics_qemu_pc_bios_bochs_bios_acpi_dsdt_hex_extra_support(self):
        expected = [
            u'Copyright (c) 2000 - 2006 Intel Corporation',
        ]
        check_detection(expected, 'ics/qemu-pc-bios-bochs-bios/acpi-dsdt.hex')

    def test_ics_qemu_pc_bios_bochs_bios_rombios_c(self):
        expected = [
            u'Copyright (c) 2002 MandrakeSoft S.A.',
            u'(c) 2002 MandrakeSoft S.A.',
            u'(c) by Joseph Gil',
        ]
        check_detection(expected, 'ics/qemu-pc-bios-bochs-bios/rombios.c')

    def test_ics_qemu_pc_bios_bochs_bios_rombios_h(self):
        expected = [
            u'Copyright (c) 2006 Volker Ruppert',
        ]
        check_detection(expected, 'ics/qemu-pc-bios-bochs-bios/rombios.h')

    def test_ics_qemu_pc_bios_vgabios_clext_c(self):
        expected = [
            u'Copyright (c) 2004 Makoto Suzuki',
        ]
        check_detection(expected, 'ics/qemu-pc-bios-vgabios/clext.c')

    def test_ics_qemu_pc_bios_vgabios_readme(self):
        expected = [
            u'(c) by Joseph Gil',
        ]
        check_detection(expected, 'ics/qemu-pc-bios-vgabios/README')

    def test_ics_qemu_pc_bios_vgabios_vbe_c_extra_byte(self):
        expected = [
            u'Copyright (c) 2002 Jeroen Janssen',
            u'(c) 2003 http://savannah.nongnu.org/projects/vgabios/',
        ]
        check_detection(expected, 'ics/qemu-pc-bios-vgabios/vbe.c')

    def test_ics_qemu_pc_bios_vgabios_vgabios_c(self):
        expected = [
            u'Copyright (c) 2001-2008 the LGPL VGABios developers Team',
            u'(c) by Joseph Gil',
            u'(c) 2008 the LGPL VGABios developers Team',
        ]
        check_detection(expected, 'ics/qemu-pc-bios-vgabios/vgabios.c')

    def test_ics_qemu_pc_bios_vgabios_vgafonts_h(self):
        expected = [
            u'(c) by Joseph Gil',
        ]
        check_detection(expected, 'ics/qemu-pc-bios-vgabios/vgafonts.h')

    def test_ics_qemu_slirp_cksum_c(self):
        expected = [
            u'Copyright (c) 1988, 1992, 1993 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/qemu-slirp/cksum.c')

    def test_ics_qemu_slirp_copyright(self):
        expected = [
            u'Danny Gasparovski. Copyright (c), 1995,1996',
            u'Copyright (c) 1995,1996 Danny Gasparovski.'
        ]
        check_detection(expected, 'ics/qemu-slirp/COPYRIGHT')

    def test_ics_qemu_slirp_debug_c(self):
        expected = [
            u'Copyright (c) 1995 Danny Gasparovski.',
            u'Portions copyright (c) 2000 Kelly Price.',
        ]
        check_detection(expected, 'ics/qemu-slirp/debug.c')

    def test_ics_qemu_slirp_debug_h(self):
        expected = [
            u'Copyright (c) 1995 Danny Gasparovski.',
        ]
        check_detection(expected, 'ics/qemu-slirp/debug.h')

    def test_ics_qemu_slirp_ip_icmp_c(self):
        expected = [
            u'Copyright (c) 1982, 1986, 1988, 1993 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/qemu-slirp/ip_icmp.c')

    def test_ics_qemu_slirp_ip_input_c(self):
        expected = [
            u'Copyright (c) 1982, 1986, 1988, 1993 The Regents of the University of California.',
            u'Copyright (c) 1995 Danny Gasparovski.',
        ]
        check_detection(expected, 'ics/qemu-slirp/ip_input.c')

    def test_ics_qemu_slirp_ip_output_c(self):
        expected = [
            u'Copyright (c) 1982, 1986, 1988, 1990, 1993 The Regents of the University of California.',
            u'Copyright (c) 1995 Danny Gasparovski.',
        ]
        check_detection(expected, 'ics/qemu-slirp/ip_output.c')

    def test_ics_qemu_slirp_mbuf_c(self):
        expected = [
            u'Copyright (c) 1995 Danny Gasparovski',
        ]
        check_detection(expected, 'ics/qemu-slirp/mbuf.c')

    def test_ics_qemu_slirp_misc_c(self):
        expected = [
            u'Copyright (c) 1995 Danny Gasparovski.',
        ]
        check_detection(expected, 'ics/qemu-slirp/misc.c')

    def test_ics_qemu_slirp_tcp_input_c(self):
        expected = [
            u'Copyright (c) 1982, 1986, 1988, 1990, 1993, 1994 The Regents of the University of California.',
            u'Copyright (c) 1995 Danny Gasparovski.',
        ]
        check_detection(expected, 'ics/qemu-slirp/tcp_input.c')

    def test_ics_qemu_slirp_tcp_timer_c(self):
        expected = [
            u'Copyright (c) 1982, 1986, 1988, 1990, 1993 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/qemu-slirp/tcp_timer.c')

    def test_ics_qemu_slirp_tcp_var_h(self):
        expected = [
            u'Copyright (c) 1982, 1986, 1993, 1994 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/qemu-slirp/tcp_var.h')

    def test_ics_qemu_slirp_tftp_c(self):
        expected = [
            u'Copyright (c) 2004 Magnus Damm <damm@opensource.se>',
        ]
        check_detection(expected, 'ics/qemu-slirp/tftp.c')

    def test_ics_qemu_slirp_android_helper_h(self):
        expected = [
            u'Copyright (c) 2009 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/qemu-slirp-android/helper.h')

    def test_ics_qemu_target_arm_iwmmxt_helper_c(self):
        expected = [
            u'Copyright (c) 2007 OpenedHand, Ltd.',
            u'Copyright (c) 2008 CodeSourcery',
        ]
        check_detection(expected, 'ics/qemu-target-arm/iwmmxt_helper.c')

    def test_ics_qemu_target_arm_neon_helper_c(self):
        expected = [
            u'Copyright (c) 2007, 2008 CodeSourcery.',
        ]
        check_detection(expected, 'ics/qemu-target-arm/neon_helper.c')

    def test_ics_qemu_target_arm_op_helper_c(self):
        expected = [
            u'Copyright (c) 2005-2007 CodeSourcery, LLC',
        ]
        check_detection(expected, 'ics/qemu-target-arm/op_helper.c')

    def test_ics_qemu_target_arm_translate_c(self):
        expected = [
            u'Copyright (c) 2003 Fabrice Bellard',
            u'Copyright (c) 2005-2007 CodeSourcery',
            u'Copyright (c) 2007 OpenedHand, Ltd.',
        ]
        check_detection(expected, 'ics/qemu-target-arm/translate.c')

    def test_ics_qemu_target_i386_helper_template_h(self):
        expected = [
            u'Copyright (c) 2008 Fabrice Bellard',
        ]
        check_detection(expected, 'ics/qemu-target-i386/helper_template.h')

    def test_ics_qemu_target_i386_kvm_c(self):
        expected = [
            u'Copyright (c) 2006-2008 Qumranet Technologies',
            u'Copyright IBM, Corp. 2008',
        ]
        check_detection(expected, 'ics/qemu-target-i386/kvm.c')

    def test_ics_qemu_target_i386_ops_sse_h(self):
        expected = [
            u'Copyright (c) 2005 Fabrice Bellard',
            u'Copyright (c) 2008 Intel Corporation',
        ]
        check_detection(expected, 'ics/qemu-target-i386/ops_sse.h')

    def test_ics_qemu_target_i386_ops_sse_header_h(self):
        expected = [
            u'Copyright (c) 2005 Fabrice Bellard',
        ]
        check_detection(expected, 'ics/qemu-target-i386/ops_sse_header.h')

    def test_ics_qemu_tcg_tcg_c(self):
        expected = [
            u'Copyright (c) 2008 Fabrice Bellard',
        ]
        check_detection(expected, 'ics/qemu-tcg/tcg.c')

    def test_ics_qemu_tcg_arm_tcg_target_c(self):
        expected = [
            u'Copyright (c) 2008 Andrzej Zaborowski',
        ]
        check_detection(expected, 'ics/qemu-tcg-arm/tcg-target.c')

    def test_ics_qemu_tcg_arm_tcg_target_h(self):
        expected = [
            u'Copyright (c) 2008 Fabrice Bellard',
            u'Copyright (c) 2008 Andrzej Zaborowski',
        ]
        check_detection(expected, 'ics/qemu-tcg-arm/tcg-target.h')

    def test_ics_quake_androidmanifest_xml(self):
        expected = [
            u'Copyright 2007, The Android Open Source Project',
        ]
        check_detection(expected, 'ics/quake/AndroidManifest.xml')

    def test_ics_quake_notice(self):
        expected = [
            u'Copyright (c) 1996-2000 Id Software Inc.',
            u'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
            u'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, 'ics/quake/NOTICE')

    def test_ics_quake_quake_src_gnu_txt(self):
        expected = [
            u'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, 'ics/quake-quake-src/gnu.txt')

    def test_ics_quake_quake_src_qw_glqwcl_spec_sh(self):
        expected = [
            u'Copyright Restricted Icon',
        ]
        check_detection(expected, 'ics/quake-quake-src-QW/glqwcl.spec.sh')

    def test_ics_quake_quake_src_qw_client_adivtab_h(self):
        expected = [
            u'Copyright (c) 1999, 2000 Id Software Inc.',
        ]
        check_detection(expected, 'ics/quake-quake-src-QW-client/adivtab.h')

    def test_ics_quake_quake_src_qw_client_anorms_h(self):
        expected = [
            u'Copyright (c) 1996-1997 Id Software, Inc.',
        ]
        check_detection(expected, 'ics/quake-quake-src-QW-client/anorms.h')

    def test_ics_quake_quake_src_qw_client_cd_linux_c(self):
        expected = [
            u'Copyright (c) 1996-1997 Id Software, Inc.',
            u'(c) 1996 Id Software, Inc.',
        ]
        check_detection(expected, 'ics/quake-quake-src-QW-client/cd_linux.c')

    def test_ics_quake_quake_src_qw_client_cl_demo_c(self):
        expected = [
            u'Copyright (c) 1996-1997 Id Software, Inc.',
        ]
        check_detection(expected, 'ics/quake-quake-src-QW-client/cl_demo.c')

    def test_ics_quake_quake_src_qw_client_exitscrn_txt(self):
        expected = [
            u'(c) 1996, 1997 Id Software, inc.',
        ]
        check_detection(expected, 'ics/quake-quake-src-QW-client/exitscrn.txt')

    def test_ics_quake_quake_src_qw_client_keys_h(self):
        expected = [
            u'Copyright (c) 1996-1997 Id Software, Inc.',
        ]
        check_detection(expected, 'ics/quake-quake-src-QW-client/keys.h')

    def test_ics_quake_quake_src_qw_client_md4_c(self):
        expected = [
            u'Copyright (c) 1996-1997 Id Software, Inc.',
            u'Copyright (c) 1991-2, RSA Data Security, Inc.',
            u'Copyright (c) 1990-2, RSA Data Security, Inc.',
        ]
        check_detection(expected, 'ics/quake-quake-src-QW-client/md4.c')

    def test_ics_quake_quake_src_qw_client_menu_c(self):
        expected = [
            u'Copyright (c) 1996-1997 Id Software, Inc.',
            u"(c) 1996 Id Software,', 0Inc.",
        ]
        check_detection(expected, 'ics/quake-quake-src-QW-client/menu.c')

    @expectedFailure
    def test_ics_quake_quake_src_qw_client_menu_c_trail_name(self):
        expected = [
            u'Copyright (c) 1996-1997 Id Software, Inc.',
            u'(c) 1996 Id Software',
        ]
        check_detection(expected, 'ics/quake-quake-src-QW-client/menu.c')

    def test_ics_quake_quake_src_qw_client_qwcl_plg(self):
        expected = [
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
        ]
        check_detection(expected, 'ics/quake-quake-src-QW-client/qwcl.plg')

    def test_ics_quake_quake_src_qw_dxsdk_sdk_inc_d3d_h(self):
        expected = [
            u'Copyright (c) 1995-1996 Microsoft Corporation.',
        ]
        check_detection(expected, 'ics/quake-quake-src-QW-dxsdk-sdk-inc/d3d.h')

    def test_ics_quake_quake_src_qw_dxsdk_sdk_inc_ddraw_h(self):
        expected = [
            u'Copyright (c) 1994-1996 Microsoft Corporation.',
        ]
        check_detection(expected, 'ics/quake-quake-src-QW-dxsdk-sdk-inc/ddraw.h')

    def test_ics_quake_quake_src_qw_dxsdk_sdk_inc_dinput_h(self):
        expected = [
            u'Copyright (c) 1996 Microsoft Corporation.',
        ]
        check_detection(expected, 'ics/quake-quake-src-QW-dxsdk-sdk-inc/dinput.h')

    def test_ics_quake_quake_src_qw_dxsdk_sdk_inc_dplay_h(self):
        expected = [
            u'Copyright (c) 1994-1995 Microsoft Corporation.',
        ]
        check_detection(expected, 'ics/quake-quake-src-QW-dxsdk-sdk-inc/dplay.h')

    def test_ics_quake_quake_src_qw_dxsdk_sdk_inc_dsound_h(self):
        expected = [
            u'Copyright (c) 1995,1996 Microsoft Corporation.',
        ]
        check_detection(expected, 'ics/quake-quake-src-QW-dxsdk-sdk-inc/dsound.h')

    def test_ics_quake_quake_src_qw_scitech_include_debug_h(self):
        expected = [
            u'Copyright (c) 1996 SciTech Software',
        ]
        check_detection(expected, 'ics/quake-quake-src-QW-scitech-include/debug.h')

    def test_ics_quake_quake_src_qw_scitech_include_mgldos_h(self):
        expected = [
            u'Copyright (c) 1996 SciTech Software.',
        ]
        check_detection(expected, 'ics/quake-quake-src-QW-scitech-include/mgldos.h')

    def test_ics_quake_quake_src_winquake_3dfx_txt_trail_name(self):
        expected = [
            u'Copyright 1997 3Dfx Interactive, Inc.',
        ]
        check_detection(expected, 'ics/quake-quake-src-WinQuake/3dfx.txt')

    def test_ics_quake_quake_src_winquake_cl_input_cpp(self):
        expected = [
            u'Copyright (c) 1996-1997 Id Software, Inc.',
            u'(c) 1996 Id Software, Inc.',
        ]
        check_detection(expected, 'ics/quake-quake-src-WinQuake/cl_input.cpp')

    def test_ics_quake_quake_src_winquake_conproc_cpp(self):
        expected = [
            u'Copyright (c) 1996-1997 Id Software, Inc.',
        ]
        check_detection(expected, 'ics/quake-quake-src-WinQuake/conproc.cpp')

    def test_ics_quake_quake_src_winquake_menu_cpp(self):
        expected = [
            u'Copyright (c) 1996-1997 Id Software, Inc.',
            u'(c) 1996 Id Software, inc.',
        ]
        check_detection(expected, 'ics/quake-quake-src-WinQuake/menu.cpp')

    def test_ics_quake_quake_src_winquake_mpdosock_h(self):
        expected = [
            u'Copyright (c) 1993-1995, Microsoft Corp.',
            u'Copyright (c) 1982-1986 Regents of the University of California.',
        ]
        check_detection(expected, 'ics/quake-quake-src-WinQuake/mpdosock.h')

    def test_ics_quake_quake_src_winquake_sys_linux_cpp(self):
        expected = [
            u'(c) 1996 Id Software, inc.',
            u'(c) 1996 Id Software, inc.',
        ]
        check_detection(expected, 'ics/quake-quake-src-WinQuake/sys_linux.cpp')

    def test_ics_quake_quake_src_winquake_winquake_plg(self):
        expected = [
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
            u'Copyright (c) Microsoft Corp 1984-1998.',
            u'Copyright (c) Microsoft Corp 1981-1993.',
        ]
        check_detection(expected, 'ics/quake-quake-src-WinQuake/WinQuake.plg')

    def test_ics_quake_src_com_android_quake_quakeactivity_java(self):
        expected = [
            u'Copyright (c) 2007 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/quake-src-com-android-quake/QuakeActivity.java')

    def test_ics_quake_src_com_android_quake_quakelib_java(self):
        expected = [
            u'Copyright (c) 2007 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/quake-src-com-android-quake/QuakeLib.java')

    def test_ics_quake_src_com_android_quake_quakeview_java(self):
        expected = [
            u'Copyright (c) 2007 The Android Open Source Project',
            u'Copyright (c) 2008 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/quake-src-com-android-quake/QuakeView.java')

    def test_ics_safe_iop_notice(self):
        expected = [
            u'Copyright (c) 2007,2008 Will Drewry <redpig@dataspill.org>',
        ]
        check_detection(expected, 'ics/safe-iop/NOTICE')

    def test_ics_safe_iop_include_safe_iop_h_lead_portion(self):
        expected = [
            u'Copyright 2007,2008 redpig@dataspill.org',
            u'portions copyright The Android Open Source Project',
        ]
        check_detection(expected, 'ics/safe-iop-include/safe_iop.h')

    def test_ics_safe_iop_src_safe_iop_c_lead_portion(self):
        expected = [
            u'Copyright 2007,2008 redpig@dataspill.org',
            u'portions copyright The Android Open Source Project',
        ]
        check_detection(expected, 'ics/safe-iop-src/safe_iop.c')

    def test_ics_skia_android_sample_sampleapp_androidmanifest_xml(self):
        expected = [
            u'Copyright (c) 2011 Skia',
        ]
        check_detection(expected, 'ics/skia-android_sample-SampleApp/AndroidManifest.xml')

    def test_ics_skia_android_sample_sampleapp_jni_sample_jni_cpp(self):
        expected = [
            u'Copyright (c) 2011 Skia',
        ]
        check_detection(expected, 'ics/skia-android_sample-SampleApp-jni/sample-jni.cpp')

    def test_ics_skia_emoji_emojifont_cpp(self):
        expected = [
            u'Copyright 2009, The Android Open Source Project',
        ]
        check_detection(expected, 'ics/skia-emoji/EmojiFont.cpp')

    def test_ics_skia_gm_strokerects_cpp(self):
        expected = [
            u'Copyright 2011 Google Inc.',
        ]
        check_detection(expected, 'ics/skia-gm/strokerects.cpp')

    def test_ics_skia_gpu_src_grgpu_cpp(self):
        expected = [
            u'Copyright 2010 Google Inc.',
        ]
        check_detection(expected, 'ics/skia-gpu-src/GrGpu.cpp')

    def test_ics_skia_include_core_skbitmap_h(self):
        expected = [
            u'Copyright (c) 2006 The Android Open Source Project',
            u'SkColorGetR (c), SkColorGetG',
        ]
        check_detection(expected, 'ics/skia-include-core/SkBitmap.h')

    def test_ics_skia_include_core_skcolorpriv_h(self):
        expected = [
            u'Copyright (c) 2006 The Android Open Source Project',
            u'SkGetPackedG32 (c), SkGetPackedB32',
            u'SkGetPackedG32 (c), SkGetPackedB32',
        ]
        check_detection(expected, 'ics/skia-include-core/SkColorPriv.h')

    def test_ics_skia_include_core_skregion_h(self):
        expected = [
            u'Copyright (c) 2005 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/skia-include-core/SkRegion.h')

    def test_ics_skia_include_core_skscalar_h(self):
        expected = [
            u'Copyright (c) 2006 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/skia-include-core/SkScalar.h')

    def test_ics_skia_include_core_sktregistry_h(self):
        expected = [
            u'Copyright 2009, The Android Open Source Project',
        ]
        check_detection(expected, 'ics/skia-include-core/SkTRegistry.h')

    def test_ics_skia_include_ports_skharfbuzzfont_h(self):
        expected = [
            u'Copyright (c) 2009, Google Inc.',
        ]
        check_detection(expected, 'ics/skia-include-ports/SkHarfBuzzFont.h')

    def test_ics_skia_include_views_skoswindow_wxwidgets_h(self):
        expected = [
            u'Copyright (c) 2006 The Android Open Source Project',
            u'Copyright 2005 MyCompanyName',
        ]
        check_detection(expected, 'ics/skia-include-views/SkOSWindow_wxwidgets.h')

    def test_ics_skia_src_animator_skoperanditerpolator_cpp(self):
        expected = [
            u'Copyright 2006, The Android Open Source Project',
        ]
        check_detection(expected, 'ics/skia-src-animator/SkOperandIterpolator.cpp')

    def test_ics_skia_src_core_skbitmap_cpp(self):
        expected = [
            u'Copyright (c) 2006-2008 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/skia-src-core/SkBitmap.cpp')

    def test_ics_skia_src_core_skbitmapprocstate_matrixprocs_cpp(self):
        expected = [
            u'(c) COPYRIGHT 2009 Motorola',
        ]
        check_detection(expected, 'ics/skia-src-core/SkBitmapProcState_matrixProcs.cpp')

    def test_ics_skia_src_core_skblitter_4444_cpp(self):
        expected = [
            u'Copyright 2006, The Android Open Source Project',
            u'SkColorGetG (c), SkColorGetB',
        ]
        check_detection(expected, 'ics/skia-src-core/SkBlitter_4444.cpp')

    def test_ics_skia_src_core_skcolortable_cpp(self):
        expected = [
            u'Copyright (c) 2006-2009 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/skia-src-core/SkColorTable.cpp')

    def test_ics_skia_src_core_skfilterproc_h(self):
        expected = [
            u'Copyright (c) 2006-2008 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/skia-src-core/SkFilterProc.h')

    def test_ics_skia_src_images_skimagedecoder_libjpeg_cpp(self):
        expected = [
            u'Copyright 2007, The Android Open Source Project',
        ]
        check_detection(expected, 'ics/skia-src-images/SkImageDecoder_libjpeg.cpp')

    def test_ics_skia_src_opts_opts_check_arm_cpp(self):
        expected = [
            u'Copyright (c) 2010, Code Aurora Forum.',
            u'Copyright 2006-2010, The Android Open Source Project',
        ]
        check_detection(expected, 'ics/skia-src-opts/opts_check_arm.cpp')

    def test_ics_skia_src_pdf_skpdffont_cpp(self):
        expected = [
            u'Copyright (c) 2011 Google Inc.',
        ]
        check_detection(expected, 'ics/skia-src-pdf/SkPDFFont.cpp')

    def test_ics_skia_src_ports_skdebug_brew_cpp(self):
        expected = [
            u'Copyright 2009, The Android Open Source Project',
            u'Copyright 2009, Company 100, Inc.',
        ]
        check_detection(expected, 'ics/skia-src-ports/SkDebug_brew.cpp')

    def test_ics_skia_src_ports_skfonthost_fontconfig_cpp(self):
        expected = [
            u'Copyright 2008, Google Inc.',
        ]
        check_detection(expected, 'ics/skia-src-ports/SkFontHost_fontconfig.cpp')

    def test_ics_skia_src_ports_skfonthost_none_cpp(self):
        expected = [
            u'Copyright 2006-2008, The Android Open Source Project',
        ]
        check_detection(expected, 'ics/skia-src-ports/SkFontHost_none.cpp')

    def test_ics_skia_src_ports_skosfile_brew_cpp(self):
        expected = [
            u'Copyright 2006, The Android Open Source Project',
            u'Copyright 2009, Company 100, Inc.',
        ]
        check_detection(expected, 'ics/skia-src-ports/SkOSFile_brew.cpp')

    def test_ics_skia_src_ports_skxmlparser_empty_cpp(self):
        expected = [
            u'Copyright 2006, The Android Open Source Project',
            u'Copyright Skia Inc. 2004 - 2005',
        ]
        check_detection(expected, 'ics/skia-src-ports/SkXMLParser_empty.cpp')

    def test_ics_skia_tests_fillpathtest_cpp(self):
        expected = [
            u'Copyright (c) 2010 The Chromium Authors.',
        ]
        check_detection(expected, 'ics/skia-tests/FillPathTest.cpp')

    def test_ics_sonivox_notice(self):
        expected = [
            u'Copyright (c) 2004-2006 Sonic Network Inc.',
        ]
        check_detection(expected, 'ics/sonivox/NOTICE')

    def test_ics_sonivox_arm_fm_22k_host_src_eas_h(self):
        expected = [
            u'Copyright Sonic Network Inc. 2005, 2006',
        ]
        check_detection(expected, 'ics/sonivox-arm-fm-22k-host_src/eas.h')

    def test_ics_sonivox_arm_fm_22k_host_src_eas_build_h(self):
        expected = [
            u'Copyright Sonic Network Inc. 2006',
        ]
        check_detection(expected, 'ics/sonivox-arm-fm-22k-host_src/eas_build.h')

    def test_ics_sonivox_arm_fm_22k_host_src_eas_config_c(self):
        expected = [
            u'Copyright Sonic Network Inc. 2004-2006',
        ]
        check_detection(expected, 'ics/sonivox-arm-fm-22k-host_src/eas_config.c')

    def test_ics_sonivox_arm_fm_22k_host_src_eas_config_h(self):
        expected = [
            u'Copyright 2005 Sonic Network Inc.',
        ]
        check_detection(expected, 'ics/sonivox-arm-fm-22k-host_src/eas_config.h')

    def test_ics_sonivox_arm_fm_22k_host_src_eas_main_c(self):
        expected = [
            u'Copyright Sonic Network Inc. 2004',
        ]
        check_detection(expected, 'ics/sonivox-arm-fm-22k-host_src/eas_main.c')

    def test_ics_sonivox_arm_fm_22k_host_src_eas_types_h(self):
        expected = [
            u'Copyright Sonic Network Inc. 2004',
        ]
        check_detection(expected, 'ics/sonivox-arm-fm-22k-host_src/eas_types.h')

    def test_ics_sonivox_arm_fm_22k_host_src_eas_wave_c(self):
        expected = [
            u'Copyright Sonic Network Inc. 2005',
        ]
        check_detection(expected, 'ics/sonivox-arm-fm-22k-host_src/eas_wave.c')

    def test_ics_sonivox_arm_fm_22k_lib_src_eas_ctype_h(self):
        expected = [
            u'Copyright (c) 2005 Sonic Network Inc.',
        ]
        check_detection(expected, 'ics/sonivox-arm-fm-22k-lib_src/eas_ctype.h')

    def test_ics_sonivox_arm_fm_22k_lib_src_eas_data_h(self):
        expected = [
            u'Copyright 2004 Sonic Network Inc.',
        ]
        check_detection(expected, 'ics/sonivox-arm-fm-22k-lib_src/eas_data.h')

    def test_ics_sonivox_arm_fm_22k_lib_src_eas_fmengine_c(self):
        expected = [
            u'Copyright Sonic Network Inc. 2004, 2005',
        ]
        check_detection(expected, 'ics/sonivox-arm-fm-22k-lib_src/eas_fmengine.c')

    def test_ics_sonivox_arm_fm_22k_lib_src_eas_fmsndlib_c(self):
        expected = [
            u'(c) Copyright 2005 Sonic Network, Inc.',
        ]
        check_detection(expected, 'ics/sonivox-arm-fm-22k-lib_src/eas_fmsndlib.c')

    def test_ics_sonivox_arm_fm_22k_lib_src_eas_smfdata_h(self):
        expected = [
            u'Copyright Sonic Network Inc. 2005',
        ]
        check_detection(expected, 'ics/sonivox-arm-fm-22k-lib_src/eas_smfdata.h')

    def test_ics_sonivox_arm_hybrid_22k_lib_src_eas_wtengine_c(self):
        expected = [
            u'Copyright Sonic Network Inc. 2004-2005',
        ]
        check_detection(expected, 'ics/sonivox-arm-hybrid-22k-lib_src/eas_wtengine.c')

    def test_ics_sonivox_arm_hybrid_22k_lib_src_hybrid_22khz_mcu_c(self):
        expected = [
            u'Copyright (c) 2006 Sonic Network Inc.',
        ]
        check_detection(expected, 'ics/sonivox-arm-hybrid-22k-lib_src/hybrid_22khz_mcu.c')

    def test_ics_sonivox_arm_wt_22k_lib_src_dls_h(self):
        expected = [
            u'Copyright (c) 1996 Sonic Foundry',
        ]
        check_detection(expected, 'ics/sonivox-arm-wt-22k-lib_src/dls.h')

    def test_ics_sonivox_arm_wt_22k_lib_src_jet_data_h(self):
        expected = [
            u'Copyright (c) 2006 Sonic Network Inc.',
        ]
        check_detection(expected, 'ics/sonivox-arm-wt-22k-lib_src/jet_data.h')

    def test_ics_sonivox_arm_wt_22k_lib_src_wt_22khz_c(self):
        expected = [
            u'Copyright (c) 2009 Sonic Network Inc.',
        ]
        check_detection(expected, 'ics/sonivox-arm-wt-22k-lib_src/wt_22khz.c')

    def test_ics_sonivox_docs_jet_authoring_guidelines_html(self):
        expected = [
            u'Copyright 2009 techdoc.dot Jennifer Hruska',
            u'Copyright (c) 2009 The Android Open Source Project',
            u'Copyright 2009 Sonic Network, Inc.'
        ]
        check_detection(expected, 'ics/sonivox-docs/JET_Authoring_Guidelines.html')

    def test_ics_sonivox_docs_jet_creator_user_manual_html(self):
        expected = [
            u'Jennifer Hruska Copyright 2009',
            u'Copyright (c) 2009 The Android Open Source Project',
            u'Copyright 2009 Sonic Network, Inc.'
        ]
        check_detection(expected, 'ics/sonivox-docs/JET_Creator_User_Manual.html')

    def test_ics_sonivox_docs_jet_programming_manual_html(self):
        expected = [
            u'Copyright (c) 2009 The Android Open Source Project',
            u'Copyright 2009 Sonic Network, Inc.'
        ]
        check_detection(expected, 'ics/sonivox-docs/JET_Programming_Manual.html')

    def test_ics_sonivox_jet_tools_jetcreator_jetaudition_py(self):
        expected = [
            u'Copyright (c) 2008 Android Open Source Project',
        ]
        check_detection(expected, 'ics/sonivox-jet_tools-JetCreator/JetAudition.py')

    def test_ics_speex_notice(self):
        expected = [
            u'Copyright (c) 2002-2008 Jean-Marc Valin',
            u'Copyright (c) 2002 Jean-Marc Valin & David Rowe',
            u'Copyright (c) 2003 Epic Games',
            u'Copyright (c) 2003 Epic Games',
            u'Copyright (c) 2004-2006 Epic Games',
            u'Copyright (c) 2005 Analog Devices',
            u'Copyright (c) 2005 Jean-Marc Valin, CSIRO, Christopher Montgomery',
            u'Copyright (c) 2006 David Rowe',
            u'Copyright (c) 2006-2008 CSIRO, Jean-Marc Valin, Xiph.Org Foundation',
            u'Copyright (c) 2008 Thorvald Natvig',
            u'Copyright (c) 2003-2004, Mark Borgerding',
            u'Copyright (c) 2005-2007, Jean-Marc Valin',
            u'Copyright (c) 2011 Jyri Sarha, Texas Instruments',
            u'Copyright 1992, 1993, 1994 by Jutta Degener and Carsten Bormann, Technische Universitaet Berlin',
        ]
        check_detection(expected, 'ics/speex/NOTICE')

    def test_ics_speex_include_speex_speex_h(self):
        expected = [
            u'Copyright (c) 2002-2006 Jean-Marc Valin',
        ]
        check_detection(expected, 'ics/speex-include-speex/speex.h')

    def test_ics_speex_include_speex_speex_bits_h(self):
        expected = [
            u'Copyright (c) 2002 Jean-Marc Valin',
        ]
        check_detection(expected, 'ics/speex-include-speex/speex_bits.h')

    def test_ics_speex_include_speex_speex_buffer_h(self):
        expected = [
            u'Copyright (c) 2007 Jean-Marc Valin',
        ]
        check_detection(expected, 'ics/speex-include-speex/speex_buffer.h')

    def test_ics_speex_include_speex_speex_echo_h(self):
        expected = [
            u'Copyright (c) Jean-Marc Valin',
        ]
        check_detection(expected, 'ics/speex-include-speex/speex_echo.h')

    def test_ics_speex_include_speex_speex_preprocess_h(self):
        expected = [
            u'Copyright (c) 2003 Epic Games',
        ]
        check_detection(expected, 'ics/speex-include-speex/speex_preprocess.h')

    def test_ics_speex_include_speex_speex_types_h(self):
        expected = [
            u'(c) COPYRIGHT 1994-2002 by the Xiph.Org Foundation http://www.xiph.org/',
        ]
        check_detection(expected, 'ics/speex-include-speex/speex_types.h')

    def test_ics_speex_libspeex_kiss_fft_guts_h(self):
        expected = [
            u'Copyright (c) 2003-2004, Mark Borgerding',
        ]
        check_detection(expected, 'ics/speex-libspeex/_kiss_fft_guts.h')

    def test_ics_speex_libspeex_arch_h(self):
        expected = [
            u'Copyright (c) 2003 Jean-Marc Valin',
        ]
        check_detection(expected, 'ics/speex-libspeex/arch.h')

    def test_ics_speex_libspeex_bits_c(self):
        expected = [
            u'Copyright (c) 2002 Jean-Marc Valin',
        ]
        check_detection(expected, 'ics/speex-libspeex/bits.c')

    def test_ics_speex_libspeex_cb_search_c(self):
        expected = [
            u'Copyright (c) 2002-2006 Jean-Marc Valin',
        ]
        check_detection(expected, 'ics/speex-libspeex/cb_search.c')

    def test_ics_speex_libspeex_cb_search_h(self):
        expected = [
            u'Copyright (c) 2002 Jean-Marc Valin & David Rowe',
        ]
        check_detection(expected, 'ics/speex-libspeex/cb_search.h')

    def test_ics_speex_libspeex_cb_search_arm4_h(self):
        expected = [
            u'Copyright (c) 2004 Jean-Marc Valin',
        ]
        check_detection(expected, 'ics/speex-libspeex/cb_search_arm4.h')

    def test_ics_speex_libspeex_cb_search_bfin_h(self):
        expected = [
            u'Copyright (c) 2005 Analog Devices',
        ]
        check_detection(expected, 'ics/speex-libspeex/cb_search_bfin.h')

    def test_ics_speex_libspeex_fftwrap_c(self):
        expected = [
            u'Copyright (c) 2005-2006 Jean-Marc Valin',
        ]
        check_detection(expected, 'ics/speex-libspeex/fftwrap.c')

    def test_ics_speex_libspeex_fftwrap_h(self):
        expected = [
            u'Copyright (c) 2005 Jean-Marc Valin',
        ]
        check_detection(expected, 'ics/speex-libspeex/fftwrap.h')

    def test_ics_speex_libspeex_filterbank_c(self):
        expected = [
            u'Copyright (c) 2006 Jean-Marc Valin',
        ]
        check_detection(expected, 'ics/speex-libspeex/filterbank.c')

    def test_ics_speex_libspeex_fixed_bfin_h(self):
        expected = [
            u'Copyright (c) 2005 Analog Devices',
        ]
        check_detection(expected, 'ics/speex-libspeex/fixed_bfin.h')

    def test_ics_speex_libspeex_kiss_fft_c(self):
        expected = [
            u'Copyright (c) 2003-2004, Mark Borgerding',
            u'Copyright (c) 2005-2007, Jean-Marc Valin',
        ]
        check_detection(expected, 'ics/speex-libspeex/kiss_fft.c')

    def test_ics_speex_libspeex_kiss_fftr_c(self):
        expected = [
            u'Copyright (c) 2003-2004, Mark Borgerding',
        ]
        check_detection(expected, 'ics/speex-libspeex/kiss_fftr.c')

    def test_ics_speex_libspeex_lpc_c(self):
        expected = [
            u'Copyright 1992, 1993, 1994 by Jutta Degener and Carsten Bormann, Technische Universitaet Berlin',
        ]
        check_detection(expected, 'ics/speex-libspeex/lpc.c')

    def test_ics_speex_libspeex_lsp_c(self):
        expected = [
            u'Jean-Marc Valin (c) 2002-2006',
        ]
        check_detection(expected, 'ics/speex-libspeex/lsp.c')

    def test_ics_speex_libspeex_lsp_bfin_h(self):
        expected = [
            u'Copyright (c) 2006 David Rowe',
        ]
        check_detection(expected, 'ics/speex-libspeex/lsp_bfin.h')

    def test_ics_speex_libspeex_mdf_c(self):
        expected = [
            u'Copyright (c) 2003-2008 Jean-Marc Valin',
        ]
        check_detection(expected, 'ics/speex-libspeex/mdf.c')

    def test_ics_speex_libspeex_modes_wb_c(self):
        expected = [
            u'Copyright (c) 2002-2007 Jean-Marc Valin',
        ]
        check_detection(expected, 'ics/speex-libspeex/modes_wb.c')

    def test_ics_speex_libspeex_preprocess_c(self):
        expected = [
            u'Copyright (c) 2003 Epic Games',
            u'Copyright (c) 2004-2006 Epic Games',
        ]
        check_detection(expected, 'ics/speex-libspeex/preprocess.c')

    def test_ics_speex_libspeex_pseudofloat_h(self):
        expected = [
            u'Copyright (c) 2005 Jean-Marc Valin',
        ]
        check_detection(expected, 'ics/speex-libspeex/pseudofloat.h')

    def test_ics_speex_libspeex_resample_c(self):
        expected = [
            u'Copyright (c) 2007-2008 Jean-Marc Valin',
            u'Copyright (c) 2008 Thorvald Natvig',
        ]
        check_detection(expected, 'ics/speex-libspeex/resample.c')

    def test_ics_speex_libspeex_resample_neon_h(self):
        expected = [
            u'Copyright (c) 2007-2008 Jean-Marc Valin',
            u'Copyright (c) 2008 Thorvald Natvig',
            u'Copyright (c) 2011 Jyri Sarha, Texas Instruments',
        ]
        check_detection(expected, 'ics/speex-libspeex/resample_neon.h')

    def test_ics_speex_libspeex_resample_sse_h(self):
        expected = [
            u'Copyright (c) 2007-2008 Jean-Marc Valin',
            u'Copyright (c) 2008 Thorvald Natvig',
        ]
        check_detection(expected, 'ics/speex-libspeex/resample_sse.h')

    def test_ics_speex_libspeex_scal_c(self):
        expected = [
            u'Copyright (c) 2006-2008 CSIRO, Jean-Marc Valin, Xiph.Org Foundation',
        ]
        check_detection(expected, 'ics/speex-libspeex/scal.c')

    def test_ics_speex_libspeex_smallft_c(self):
        expected = [
            u'(c) COPYRIGHT 1994-2001 by the XIPHOPHORUS Company http://www.xiph.org/',
        ]
        check_detection(expected, 'ics/speex-libspeex/smallft.c')

    def test_ics_speex_libspeex_vorbis_psy_h(self):
        expected = [
            u'Copyright (c) 2005 Jean-Marc Valin, CSIRO, Christopher Montgomery',
        ]
        check_detection(expected, 'ics/speex-libspeex/vorbis_psy.h')

    def test_ics_speex_libspeex_window_c(self):
        expected = [
            u'Copyright (c) 2006 Jean-Marc Valin',
        ]
        check_detection(expected, 'ics/speex-libspeex/window.c')

    def test_ics_srec_notice(self):
        expected = [
            u'Copyright 2007, 2008 Nuance Communications',
        ]
        check_detection(expected, 'ics/srec/NOTICE')

    def test_ics_srec_audio_audioin_unix_include_audioin_h(self):
        expected = [
            u'Copyright 2007, 2008 Nuance Communciations, Inc.',
        ]
        check_detection(expected, 'ics/srec-audio-AudioIn-UNIX-include/audioin.h')

    def test_ics_srec_audio_audioin_unix_src_audioinwrapper_cpp(self):
        expected = [
            u'Copyright 2007, 2008 Nuance Communciations, Inc.',
        ]
        check_detection(expected, 'ics/srec-audio-AudioIn-UNIX-src/audioinwrapper.cpp')

    def test_ics_srec_audio_audioin_unix_src_filter_c(self):
        expected = [
            u'Copyright 2007, 2008 Nuance Communciations, Inc.',
        ]
        check_detection(expected, 'ics/srec-audio-AudioIn-UNIX-src/filter.c')

    def test_ics_srec_doc_srec_doxygen(self):
        expected = [
            u'(c) Copyright 2003-2007 Nuance',
        ]
        check_detection(expected, 'ics/srec-doc/srec.doxygen')

    def test_ics_srec_srec_srec_doxygen(self):
        expected = [
            u'(c) Copyright 2003 Speechworks International',
        ]
        check_detection(expected, 'ics/srec-srec/srec.doxygen')

    def test_ics_srec_srec_jni_android_speech_srec_microphoneinputstream_cpp(self):
        expected = [
            u'Copyright 2007 Nuance Communciations, Inc.',
        ]
        check_detection(expected, 'ics/srec-srec_jni/android_speech_srec_MicrophoneInputStream.cpp')

    @expectedFailure
    def test_ics_srec_tools_grxmlcompile_grxmlcompile_cpp(self):
        expected = [
            u'Copyright 2007, 2008 Nuance Communciations, Inc.',
            u'Copyright (c) 2007 Project Admins leethomason',
        ]
        check_detection(expected, 'ics/srec-tools-grxmlcompile/grxmlcompile.cpp')

    def test_ics_srec_tools_grxmlcompile_grxmlcompile_cpp_current(self):
        expected = [
            u'Copyright 2007, 2008 Nuance Communciations, Inc.',
            u'Copyright (c) 2007 Project',
        ]
        check_detection(expected, 'ics/srec-tools-grxmlcompile/grxmlcompile.cpp')

    def test_ics_srtp_config_guess(self):
        expected = [
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004 Free Software Foundation, Inc.',
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/srtp/config.guess')

    def test_ics_srtp_config_log(self):
        expected = [
            u'Copyright (c) 2007 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/srtp/config.log')

    def test_ics_srtp_license(self):
        expected = [
            u'Copyright (c) 2001-2006 Cisco Systems, Inc.',
        ]
        check_detection(expected, 'ics/srtp/LICENSE')

    def test_ics_srtp_crypto_cipher_aes_c(self):
        expected = [
            u'Copyright (c) 2001-2006, Cisco Systems, Inc.',
        ]
        check_detection(expected, 'ics/srtp-crypto-cipher/aes.c')

    def test_ics_srtp_crypto_hash_hmac_c(self):
        expected = [
            u'Copyright (c) 2001-2006 Cisco Systems, Inc.',
        ]
        check_detection(expected, 'ics/srtp-crypto-hash/hmac.c')

    def test_ics_srtp_crypto_include_auth_h(self):
        expected = [
            u'Copyright (c) 2001-2006, Cisco Systems, Inc.',
        ]
        check_detection(expected, 'ics/srtp-crypto-include/auth.h')

    def test_ics_srtp_crypto_include_kernel_compat_h(self):
        expected = [
            u'Copyright (c) 2005 Ingate Systems AB',
        ]
        check_detection(expected, 'ics/srtp-crypto-include/kernel_compat.h')

    def test_ics_srtp_doc_header_template(self):
        expected = [
            u'copyright 2001-2005 by David A. McGrew, Cisco Systems, Inc.',
        ]
        check_detection(expected, 'ics/srtp-doc/header.template')

    def test_ics_srtp_doc_intro_txt(self):
        expected = [
            u'Copyright (c) 2001-2005 Cisco Systems, Inc.',
        ]
        check_detection(expected, 'ics/srtp-doc/intro.txt')

    def test_ics_srtp_doc_rfc3711_txt(self):
        expected = [
            u'Copyright (c) The Internet Society (2004).',
            u'Full Copyright Statement',
            u'Full Copyright Statement',
            u'Copyright (c) The Internet Society (2004).',
        ]
        check_detection(expected, 'ics/srtp-doc/rfc3711.txt')

    def test_ics_srtp_include_ekt_h(self):
        expected = [
            u'Copyright (c) 2001-2005 Cisco Systems, Inc.',
        ]
        check_detection(expected, 'ics/srtp-include/ekt.h')

    def test_ics_stlport_configure_bat(self):
        expected = [
            u'Copyright (c) 2004,2005 Michael Fink',
        ]
        check_detection(expected, 'ics/stlport/configure.bat')

    def test_ics_stlport_license(self):
        expected = [
            u'Copyright 1999,2000 Boris Fomitchev',
            u'Copyright 1994 Hewlett-Packard Company',
            u'Copyright 1996,97 Silicon Graphics Computer Systems, Inc.',
            u'Copyright 1997 Moscow Center for SPARC Technology.',
        ]
        check_detection(expected, 'ics/stlport/LICENSE')

    def test_ics_stlport_makefile(self):
        expected = [
            u'Copyright (c) 2004-2008 Petr Ovtchenkov',
        ]
        check_detection(expected, 'ics/stlport/Makefile')

    def test_ics_stlport_readme(self):
        expected = [
            u'Copyright (c) 1994 Hewlett-Packard Company',
            u'Copyright (c) 1996-1999 Silicon Graphics Computer Systems, Inc.',
            u'Copyright (c) 1997 Moscow Center for SPARC Technology',
            u'Copyright (c) 1999-2003 Boris Fomitchev',
        ]
        check_detection(expected, 'ics/stlport/README')

    def test_ics_stlport_src_acquire_release_h(self):
        expected = [
            u'Copyright (c) 1999 Silicon Graphics Computer Systems, Inc.',
            u'Copyright (c) 1999 Boris Fomitchev',
        ]
        check_detection(expected, 'ics/stlport-src/acquire_release.h')

    def test_ics_stlport_src_allocators_cpp(self):
        expected = [
            u'Copyright (c) 1996,1997 Silicon Graphics Computer Systems, Inc.',
            u'Copyright (c) 1997 Moscow Center for SPARC Technology',
            u'Copyright (c) 1999 Boris Fomitchev',
        ]
        check_detection(expected, 'ics/stlport-src/allocators.cpp')

    def test_ics_stlport_src_bitset_cpp(self):
        expected = [
            u'Copyright (c) 1998 Silicon Graphics Computer Systems, Inc.',
            u'Copyright (c) 1999 Boris Fomitchev',
        ]
        check_detection(expected, 'ics/stlport-src/bitset.cpp')

    def test_ics_stlport_src_ctype_cpp(self):
        expected = [
            u'Copyright (c) 1999 Silicon Graphics Computer Systems, Inc.',
            u'Copyright (c) 1999 Boris Fomitchev',
        ]
        check_detection(expected, 'ics/stlport-src/ctype.cpp')

    def test_ics_stlport_src_dll_main_cpp(self):
        expected = [
            u'Copyright (c) 1994 Hewlett-Packard Company',
            u'Copyright (c) 1996,1997 Silicon Graphics Computer Systems, Inc.',
            u'Copyright (c) 1997 Moscow Center for SPARC Technology',
            u'Copyright (c) 1999 Boris Fomitchev',
        ]
        check_detection(expected, 'ics/stlport-src/dll_main.cpp')

    def test_ics_stlport_src_lock_free_slist_h(self):
        expected = [
            u'Copyright (c) 1997-1999 Silicon Graphics Computer Systems, Inc.',
            u'Copyright (c) 1999 Boris Fomitchev',
        ]
        check_detection(expected, 'ics/stlport-src/lock_free_slist.h')

    def test_ics_stlport_src_stlport_rc(self):
        expected = [
            u'Copyright (c) Boris Fomitchev',
        ]
        check_detection(expected, 'ics/stlport-src/stlport.rc')

    def test_ics_stlport_src_c_locale_dummy_c_locale_dummy_c(self):
        expected = [
            u'Copyright (c) 1999 Silicon Graphics Computer Systems, Inc.',
            u'Copyright (c) 1999 Boris Fomitchev',
        ]
        check_detection(expected, 'ics/stlport-src-c_locale_dummy/c_locale_dummy.c')

    def test_ics_stlport_src_c_locale_win32_c_wlocale_win32_c(self):
        expected = [
            u'Copyright (c) 2007 2008 Francois Dumont',
        ]
        check_detection(expected, 'ics/stlport-src-c_locale_win32/c_wlocale_win32.c')

    def test_ics_stlport_stlport_assert_h(self):
        expected = [
            u'Copyright (c) 1999 Boris Fomitchev',
        ]
        check_detection(expected, 'ics/stlport-stlport/assert.h')

    def test_ics_stlport_stlport_exception(self):
        expected = [
            u'Copyright (c) 1996,1997 Silicon Graphics Computer Systems, Inc.',
            u'Copyright (c) 1999 Boris Fomitchev',
        ]
        check_detection(expected, 'ics/stlport-stlport/exception')

    def test_ics_stlport_stlport_limits(self):
        expected = [
            u'Copyright (c) 1997 Silicon Graphics Computer Systems, Inc.',
            u'Copyright (c) 1999 Boris Fomitchev',
        ]
        check_detection(expected, 'ics/stlport-stlport/limits')

    def test_ics_stlport_stlport_locale(self):
        expected = [
            u'Copyright (c) 1999 Silicon Graphics Computer Systems, Inc.',
            u'Copyright (c) 1999 Boris Fomitchev',
        ]
        check_detection(expected, 'ics/stlport-stlport/locale')

    def test_ics_stlport_stlport_numeric(self):
        expected = [
            u'Copyright (c) 1994 Hewlett-Packard Company',
            u'Copyright (c) 1996,1997 Silicon Graphics Computer Systems, Inc.',
            u'Copyright (c) 1999 Boris Fomitchev',
        ]
        check_detection(expected, 'ics/stlport-stlport/numeric')

    def test_ics_stlport_stlport_rope(self):
        expected = [
            u'Copyright (c) 1997 Silicon Graphics Computer Systems, Inc.',
        ]
        check_detection(expected, 'ics/stlport-stlport/rope')

    def test_ics_stlport_stlport_type_traits(self):
        expected = [
            u'Copyright (c) 2007, 2008 Petr Ovtchenkov',
        ]
        check_detection(expected, 'ics/stlport-stlport/type_traits')

    def test_ics_stlport_stlport_unordered_map(self):
        expected = [
            u'Copyright (c) 2004,2005 Francois Dumont',
        ]
        check_detection(expected, 'ics/stlport-stlport/unordered_map')

    def test_ics_stlport_stlport_stl_carray_h(self):
        expected = [
            u'Copyright (c) 2005 Francois Dumont',
        ]
        check_detection(expected, 'ics/stlport-stlport-stl/_carray.h')

    def test_ics_stlport_stlport_stl_function_h(self):
        expected = [
            u'Copyright (c) 1994 Hewlett-Packard Company',
            u'Copyright (c) 1996-1998 Silicon Graphics Computer Systems, Inc.',
            u'Copyright (c) 1997 Moscow Center for SPARC Technology',
            u'Copyright (c) 1999 Boris Fomitchev',
        ]
        check_detection(expected, 'ics/stlport-stlport-stl/_function.h')

    def test_ics_stlport_stlport_stl_function_adaptors_h(self):
        expected = [
            u'Copyright (c) 1994 Hewlett-Packard Company',
            u'Copyright (c) 1996-1998 Silicon Graphics Computer Systems, Inc.',
            u'Copyright (c) 1997 Moscow Center for SPARC Technology',
            u'Copyright (c) 1999 Boris Fomitchev',
            u'Copyright (c) 2000 Pavel Kuznetsov',
            u"Copyright (c) 2001 Meridian'93",
        ]
        check_detection(expected, 'ics/stlport-stlport-stl/_function_adaptors.h')

    def test_ics_stlport_stlport_stl_hash_fun_h(self):
        expected = [
            u'Copyright (c) 1996-1998 Silicon Graphics Computer Systems, Inc.',
            u'Copyright (c) 1994 Hewlett-Packard Company',
        ]
        check_detection(expected, 'ics/stlport-stlport-stl/_hash_fun.h')

    def test_ics_stlport_stlport_stl_heap_h(self):
        expected = [
            u'Copyright (c) 1994 Hewlett-Packard Company',
            u'Copyright (c) 1997 Silicon Graphics Computer Systems, Inc.',
        ]
        check_detection(expected, 'ics/stlport-stlport-stl/_heap.h')

    def test_ics_stlport_stlport_stl_limits_c(self):
        expected = [
            u'Copyright (c) 1998,1999 Silicon Graphics Computer Systems, Inc.',
            u'Copyright (c) 1999 Boris Fomitchev',
        ]
        check_detection(expected, 'ics/stlport-stlport-stl/_limits.c')

    def test_ics_stlport_stlport_stl_string_base_h(self):
        expected = [
            u'Copyright (c) 1997-1999 Silicon Graphics Computer Systems, Inc.',
            u'Copyright (c) 1999 Boris Fomitchev',
            u'Copyright (c) 2003 Francois Dumont',
        ]
        check_detection(expected, 'ics/stlport-stlport-stl/_string_base.h')

    def test_ics_stlport_stlport_stl_boost_type_traits_h(self):
        expected = [
            u'Copyright (c) 2004 Francois Dumont',
        ]
        check_detection(expected, 'ics/stlport-stlport-stl/boost_type_traits.h')

    def test_ics_stlport_stlport_stl_concept_checks_h(self):
        expected = [
            u'Copyright (c) 1999 Silicon Graphics Computer Systems, Inc.',
        ]
        check_detection(expected, 'ics/stlport-stlport-stl/concept_checks.h')

    def test_ics_stlport_stlport_stl_msl_string_h_trail_inc(self):
        expected = [
            u'Copyright (c) 1998 Mark of the Unicorn, Inc.',
        ]
        check_detection(expected, 'ics/stlport-stlport-stl/msl_string.h')

    def test_ics_stlport_stlport_stl_type_manips_h(self):
        expected = [
            u'Copyright (c) 2003 Francois Dumont',
        ]
        check_detection(expected, 'ics/stlport-stlport-stl/type_manips.h')

    def test_ics_stlport_stlport_stl_type_traits_h(self):
        expected = [
            u'Copyright (c) 1996,1997 Silicon Graphics Computer Systems, Inc.',
            u'Copyright (c) 1997 Moscow Center for SPARC Technology',
            u'Copyright (c) 1999 Boris Fomitchev',
            u'Copyright 2000 Adobe Systems Incorporated and others.',
        ]
        check_detection(expected, 'ics/stlport-stlport-stl/type_traits.h')

    def test_ics_stlport_stlport_stl_config_native_headers_h(self):
        expected = [
            u'Copyright (c) 2006 Francois Dumont',
        ]
        check_detection(expected, 'ics/stlport-stlport-stl-config/_native_headers.h')

    def test_ics_stlport_test_eh_main_cpp_trail_inc(self):
        expected = [
            u'Copyright (c) 1997 Mark of the Unicorn, Inc.',
            u'Copyright (c) 1997 Moscow Center for SPARC Technology',
        ]
        check_detection(expected, 'ics/stlport-test-eh/main.cpp')

    def test_ics_stlport_test_eh_mwerks_console_os_x_c(self):
        expected = [
            u'Copyright (c) 1995-2002 Metrowerks Corporation.',
        ]
        check_detection(expected, 'ics/stlport-test-eh/mwerks_console_OS_X.c')

    def test_ics_stlport_test_eh_random_number_h_trail_inc(self):
        expected = [
            u'Copyright (c) 1997-1998 Mark of the Unicorn, Inc.',
        ]
        check_detection(expected, 'ics/stlport-test-eh/random_number.h')

    def test_ics_stlport_test_eh_test_insert_h_trail_inc(self):
        expected = [
            u'Copyright (c) 1997 Mark of the Unicorn, Inc.',
        ]
        check_detection(expected, 'ics/stlport-test-eh/test_insert.h')

    def test_ics_stlport_test_unit_limits_test_cpp(self):
        expected = [
            u'Copyright Jens Maurer 2000',
        ]
        check_detection(expected, 'ics/stlport-test-unit/limits_test.cpp')

    def test_ics_stlport_test_unit_cppunit_cppunit_mini_h(self):
        expected = [
            u'Copyright (c) 2003, 2004 Zdenek Nemec',
        ]
        check_detection(expected, 'ics/stlport-test-unit-cppunit/cppunit_mini.h')

    def test_ics_strace_aclocal_m4(self):
        expected = [
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2002, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1997, 2000, 2001, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 2000, 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1998, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2002, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1997, 1999, 2000, 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2003, 2004, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2002, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1996, 1997, 2000, 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2001, 2003, 2005 Free Software Foundation, Inc.',
            u'Copyright (c) 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/strace/aclocal.m4')

    def test_ics_strace_bjm_c(self):
        expected = [
            u'Copyright (c) 1991, 1992 Paul Kranenburg <pk@cs.few.eur.nl>',
            u'Copyright (c) 1993 Branko Lankester <branko@hacktic.nl>',
            u'Copyright (c) 1993, 1994, 1995, 1996 Rick Sladkey <jrs@world.std.com>',
            u'Copyright (c) 1996-1999 Wichert Akkerman <wichert@cistron.nl>',
        ]
        check_detection(expected, 'ics/strace/bjm.c')

    def test_ics_strace_config_log(self):
        expected = [
            u'Copyright (c) 2006 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/strace/config.log')

    def test_ics_strace_copyright(self):
        notes = '''this is redundant and rare junk except in BSD and is not detected
        COPYRIGHT,v 1.3 2002/03/31 18:43:00 wichert'''
        expected = [
            u'Copyright (c) 1991, 1992 Paul Kranenburg <pk@cs.few.eur.nl>',
            u'Copyright (c) 1993 Branko Lankester <branko@hacktic.nl>',
            u'Copyright (c) 1993 Ulrich Pegelow <pegelow@moorea.uni-muenster.de>',
            u'Copyright (c) 1995, 1996 Michael Elizabeth Chastain <mec@duracef.shout.net>',
            u'Copyright (c) 1993, 1994, 1995, 1996 Rick Sladkey <jrs@world.std.com>',
            u'Copyright (c) 1998-2001 Wichert Akkerman <wakkerma@deephackmode.org>',
        ]
        check_detection(expected, 'ics/strace/COPYRIGHT', notes=notes)

    def test_ics_strace_defs_h(self):
        expected = [
            u'Copyright (c) 1991, 1992 Paul Kranenburg <pk@cs.few.eur.nl>',
            u'Copyright (c) 1993 Branko Lankester <branko@hacktic.nl>',
            u'Copyright (c) 1993, 1994, 1995, 1996 Rick Sladkey <jrs@world.std.com>',
        ]
        check_detection(expected, 'ics/strace/defs.h')

    def test_ics_strace_depcomp(self):
        expected = [
            u'Copyright (c) 1999, 2000, 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/strace/depcomp')

    def test_ics_strace_errnoent_sh(self):
        expected = [
            u'Copyright (c) 1993, 1994, 1995 Rick Sladkey <jrs@world.std.com>',
        ]
        check_detection(expected, 'ics/strace/errnoent.sh')

    def test_ics_strace_ioctl_c(self):
        expected = [
            u'Copyright (c) 1991, 1992 Paul Kranenburg <pk@cs.few.eur.nl>',
            u'Copyright (c) 1993 Branko Lankester <branko@hacktic.nl>',
            u'Copyright (c) 1993, 1994, 1995, 1996 Rick Sladkey <jrs@world.std.com>',
            u'Copyright (c) 1996-2001 Wichert Akkerman <wichert@cistron.nl>',
        ]
        check_detection(expected, 'ics/strace/ioctl.c')

    def test_ics_strace_ioctlsort_c(self):
        expected = [
            u'Copyright (c) 1991, 1992 Paul Kranenburg <pk@cs.few.eur.nl>',
            u'Copyright (c) 1993, 1994, 1995 Rick Sladkey <jrs@world.std.com>',
        ]
        check_detection(expected, 'ics/strace/ioctlsort.c')

    def test_ics_strace_ipc_c(self):
        expected = [
            u'Copyright (c) 1993 Ulrich Pegelow <pegelow@moorea.uni-muenster.de>',
            u'Copyright (c) 1993 Branko Lankester <branko@hacktic.nl>',
            u'Copyright (c) 1993, 1994, 1995, 1996 Rick Sladkey <jrs@world.std.com>',
            u'Copyright (c) 1996-1999 Wichert Akkerman <wichert@cistron.nl>',
        ]
        check_detection(expected, 'ics/strace/ipc.c')

    def test_ics_strace_makefile_in(self):
        expected = [
            u'Copyright (c) 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, 'ics/strace/Makefile.in')

    def test_ics_strace_mem_c(self):
        expected = [
            u'Copyright (c) 1991, 1992 Paul Kranenburg <pk@cs.few.eur.nl>',
            u'Copyright (c) 1993 Branko Lankester <branko@hacktic.nl>',
            u'Copyright (c) 1993, 1994, 1995, 1996 Rick Sladkey <jrs@world.std.com>',
            u'Copyright (c) 1996-1999 Wichert Akkerman <wichert@cistron.nl>',
            u'Copyright (c) 2000 PocketPenguins Inc.',
        ]
        check_detection(expected, 'ics/strace/mem.c')

    def test_ics_strace_net_c(self):
        expected = [
            u'Copyright (c) 1991, 1992 Paul Kranenburg <pk@cs.few.eur.nl>',
            u'Copyright (c) 1993 Branko Lankester <branko@hacktic.nl>',
            u'Copyright (c) 1993, 1994, 1995, 1996 Rick Sladkey <jrs@world.std.com>',
            u'Copyright (c) 1996-2000 Wichert Akkerman <wichert@cistron.nl>',
        ]
        check_detection(expected, 'ics/strace/net.c')

    def test_ics_strace_proc_c(self):
        expected = [
            u'Copyright (c) 1993, 1994, 1995 Rick Sladkey <jrs@world.std.com>',
        ]
        check_detection(expected, 'ics/strace/proc.c')

    def test_ics_strace_process_c(self):
        expected = [
            u'Copyright (c) 1991, 1992 Paul Kranenburg <pk@cs.few.eur.nl>',
            u'Copyright (c) 1993 Branko Lankester <branko@hacktic.nl>',
            u'Copyright (c) 1993, 1994, 1995, 1996 Rick Sladkey <jrs@world.std.com>',
            u'Copyright (c) 1996-1999 Wichert Akkerman <wichert@cistron.nl>',
            u'Copyright (c) 1999 IBM Deutschland Entwicklung GmbH, IBM Corporation',
            u'Copyright (c) 2000 PocketPenguins Inc.',
        ]
        check_detection(expected, 'ics/strace/process.c')

    def test_ics_strace_signal_c(self):
        expected = [
            u'Copyright (c) 1991, 1992 Paul Kranenburg <pk@cs.few.eur.nl>',
            u'Copyright (c) 1993 Branko Lankester <branko@hacktic.nl>',
            u'Copyright (c) 1993, 1994, 1995, 1996 Rick Sladkey <jrs@world.std.com>',
            u'Copyright (c) 1996-1999 Wichert Akkerman <wichert@cistron.nl>',
            u'Copyright (c) 1999 IBM Deutschland Entwicklung GmbH, IBM Corporation',
        ]
        check_detection(expected, 'ics/strace/signal.c')

    def test_ics_strace_signalent_sh(self):
        expected = [
            u'Copyright (c) 1996 Rick Sladkey <jrs@world.std.com>',
        ]
        check_detection(expected, 'ics/strace/signalent.sh')

    def test_ics_strace_sock_c(self):
        expected = [
            u'Copyright (c) 1993, 1994, 1995, 1996 Rick Sladkey <jrs@world.std.com>',
        ]
        check_detection(expected, 'ics/strace/sock.c')

    def test_ics_strace_strace_1(self):
        expected = [
            u'Copyright (c) 1991, 1992 Paul Kranenburg <pk@cs.few.eur.nl>',
            u'Copyright (c) 1993 Branko Lankester <branko@hacktic.nl>',
            u'Copyright (c) 1993, 1994, 1995, 1996 Rick Sladkey <jrs@world.std.com>',
        ]
        check_detection(expected, 'ics/strace/strace.1')

    def test_ics_strace_strace_graph(self):
        expected = [
            u'Copyright (c) 1998 by Richard Braakman <dark@xs4all.nl>',
        ]
        check_detection(expected, 'ics/strace/strace-graph')

    def test_ics_strace_stream_c(self):
        expected = [
            u'Copyright (c) 1993, 1994, 1995, 1996 Rick Sladkey <jrs@world.std.com>',
            u'Copyright (c) 1996-1999 Wichert Akkerman <wichert@cistron.nl>',
        ]
        check_detection(expected, 'ics/strace/stream.c')

    def test_ics_strace_syscallent_sh(self):
        expected = [
            u'Copyright (c) 1993, 1994, 1995, 1996 Rick Sladkey <jrs@world.std.com>',
        ]
        check_detection(expected, 'ics/strace/syscallent.sh')

    def test_ics_strace_linux_dummy_h(self):
        expected = [
            u'Copyright (c) 1993 Branko Lankester <branko@hacktic.nl>',
            u'Copyright (c) 1993, 1994, 1995 Rick Sladkey <jrs@world.std.com>',
        ]
        check_detection(expected, 'ics/strace-linux/dummy.h')

    def test_ics_strace_linux_ioctlent_sh(self):
        expected = [
            u'Copyright (c) 2001 Wichert Akkerman <wichert@cistron.nl>',
        ]
        check_detection(expected, 'ics/strace-linux/ioctlent.sh')

    def test_ics_strace_strace_linux_hppa_syscallent_h(self):
        expected = [
            u'Copyright (c) 2001 Hewlett-Packard, Matthew Wilcox',
        ]
        check_detection(expected, 'ics/strace-strace-linux-hppa/syscallent.h')

    def test_ics_strace_strace_linux_ia64_syscallent_h(self):
        expected = [
            u'Copyright (c) 1999, 2001 Hewlett-Packard Co David Mosberger-Tang <davidm@hpl.hp.com>',
        ]
        check_detection(expected, 'ics/strace-strace-linux-ia64/syscallent.h')

    def test_ics_strace_strace_linux_mips_ioctlent_sh(self):
        expected = [
            u'Copyright (c) 1993, 1994, 1995 Rick Sladkey <jrs@world.std.com>',
            u'Copyright (c) 1995, 1996 Michael Elizabeth Chastain <mec@duracef.shout.net>',
        ]
        check_detection(expected, 'ics/strace-strace-linux-mips/ioctlent.sh')

    def test_ics_strace_strace_linux_s390_syscallent_h(self):
        expected = [
            u'Copyright (c) 2000 IBM Deutschland Entwicklung GmbH, IBM Coporation',
        ]
        check_detection(expected, 'ics/strace-strace-linux-s390/syscallent.h')

    def test_ics_strace_strace_linux_sh_syscallent_h(self):
        expected = [
            u'Copyright (c) 1993 Branko Lankester <branko@hacktic.nl>',
            u'Copyright (c) 1993, 1994, 1995 Rick Sladkey <jrs@world.std.com>',
            u'Copyright (c) 2000 PocketPenguins Inc.',
        ]
        check_detection(expected, 'ics/strace-strace-linux-sh/syscallent.h')

    def test_ics_strace_strace_linux_sparc_syscall_h(self):
        expected = [
            u'Copyright (c) 1991, 1992 Paul Kranenburg <pk@cs.few.eur.nl>',
            u'Copyright (c) 1993, 1994, 1995, 1996 Rick Sladkey <jrs@world.std.com>',
        ]
        check_detection(expected, 'ics/strace-strace-linux-sparc/syscall.h')

    def test_ics_svox_pico_androidmanifest_xml(self):
        expected = [
            u'Copyright 2009, The Android Open Source Project',
        ]
        check_detection(expected, 'ics/svox-pico/AndroidManifest.xml')

    def test_ics_svox_pico_resources_tools_lingwarebuilding_readme_txt(self):
        expected = [
            u'Copyright (c) 2008-2009 SVOX AG',
        ]
        check_detection(expected, 'ics/svox-pico_resources-tools-LingwareBuilding/Readme.txt')

    def test_ics_svox_pico_resources_tools_lingwarebuilding_picolingware_source_files_textana_en_gb_en_gb_lexpos_utf(self):
        expected = [
            u'Copyright (c) 2008-2009 SVOX AG',
        ]
        check_detection(expected, 'ics/svox-pico_resources-tools-LingwareBuilding-PicoLingware_source_files-textana-en-GB/en-GB_lexpos.utf')

    def test_ics_svox_pico_resources_tools_lingwarebuilding_picolingware_tools_windows_tools_buildbin_sh(self):
        expected = [
            u'Copyright (c) 2009 SVOX AG.',
        ]
        check_detection(expected, 'ics/svox-pico_resources-tools-LingwareBuilding-PicoLingware_tools_windows-tools/buildbin.sh')

    def test_ics_svox_pico_compat_jni_com_android_tts_compat_synthproxy_cpp(self):
        expected = [
            u'Copyright (c) 2009-2010 Google Inc.',
        ]
        check_detection(expected, 'ics/svox-pico-compat-jni/com_android_tts_compat_SynthProxy.cpp')

    def test_ics_svox_pico_lib_notice(self):
        expected = [
            u'Copyright (c) 2008-2009 SVOX AG',
        ]
        check_detection(expected, 'ics/svox-pico-lib/NOTICE')

    def test_ics_svox_pico_lib_picoacph_c(self):
        expected = [
            u'Copyright (c) 2008-2009 SVOX AG',
            u'Copyright (c) 2008-2009 SVOX AG',
        ]
        check_detection(expected, 'ics/svox-pico-lib/picoacph.c')

    def test_ics_svox_pico_lib_picofftsg_c(self):
        expected = [
            u'Copyright (c) 2008-2009 SVOX AG',
            u'Copyright (c) 2008-2009 SVOX AG',
            u'(Copyright Takuya OOURA, 1996-2001)',
        ]
        check_detection(expected, 'ics/svox-pico-lib/picofftsg.c')

    def test_ics_svox_pico_lib_picoos_c(self):
        expected = [
            u'Copyright (c) 2008-2009 SVOX AG',
            u'Copyright (c) 2008-2009 SVOX AG',
            u'(c) SVOX AG',
        ]
        check_detection(expected, 'ics/svox-pico-lib/picoos.c')

    def test_ics_svox_pico_res_xml_tts_engine_xml(self):
        expected = [
            u'Copyright (c) 2011 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/svox-pico-res-xml/tts_engine.xml')

    def test_ics_svox_pico_res_xml_voices_list_xml(self):
        expected = [
            u'Copyright (c) 2009 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/svox-pico-res-xml/voices_list.xml')

    def test_ics_svox_pico_tts_com_svox_picottsengine_cpp(self):
        expected = [
            u'Copyright (c) 2008-2009 SVOX AG',
        ]
        check_detection(expected, 'ics/svox-pico-tts/com_svox_picottsengine.cpp')

    def test_ics_tagsoup_src_org_ccil_cowan_tagsoup_autodetector_java(self):
        expected = [
            u'Copyright 2002-2008 by John Cowan.',
        ]
        check_detection(expected, 'ics/tagsoup-src-org-ccil-cowan-tagsoup/AutoDetector.java')

    def test_ics_tcpdump_aclocal_m4_trail_name_m4_dnl_comment(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997, 1998 The Regents of the University of California.',
            u'Copyright (c) 1999 WIDE Project.',
        ]
        check_detection(expected, 'ics/tcpdump/aclocal.m4')

    def test_ics_tcpdump_addrtoname_c(self):
        expected = [
            u'Copyright (c) 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/addrtoname.c')

    def test_ics_tcpdump_addrtoname_h(self):
        expected = [
            u'Copyright (c) 1990, 1992, 1993, 1994, 1995, 1996, 1997 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/addrtoname.h')

    def test_ics_tcpdump_af_c(self):
        expected = [
            u'Copyright (c) 1998-2006 The TCPDUMP project',
        ]
        check_detection(expected, 'ics/tcpdump/af.c')

    def test_ics_tcpdump_aodv_h(self):
        expected = [
            u'Copyright (c) 2003 Bruce M. Simpson <bms@spc.org>',
        ]
        check_detection(expected, 'ics/tcpdump/aodv.h')

    def test_ics_tcpdump_appletalk_h(self):
        expected = [
            u'Copyright (c) 1988, 1989, 1990, 1993, 1994, 1995, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/appletalk.h')

    def test_ics_tcpdump_atm_h(self):
        expected = [
            u'Copyright (c) 2002 Guy Harris.',
        ]
        check_detection(expected, 'ics/tcpdump/atm.h')

    def test_ics_tcpdump_bootp_h(self):
        expected = [
            u'Copyright 1988 by Carnegie Mellon.',
        ]
        check_detection(expected, 'ics/tcpdump/bootp.h')

    def test_ics_tcpdump_chdlc_h(self):
        expected = [
            u'Copyright (c) 1990, 1991, 1993, 1994, 1995, 1996, 1997 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/chdlc.h')

    def test_ics_tcpdump_cpack_c(self):
        expected = [
            u'Copyright (c) 2003, 2004 David Young.',
        ]
        check_detection(expected, 'ics/tcpdump/cpack.c')

    def test_ics_tcpdump_dccp_h(self):
        expected = [
            u'Copyright (c) Arnaldo Carvalho de Melo 2004',
            u'Copyright (c) Ian McDonald 2005 <iam4@cs.waikato.ac.nz>',
            u'Copyright (c) Yoshifumi Nishida 2005',
        ]
        check_detection(expected, 'ics/tcpdump/dccp.h')

    def test_ics_tcpdump_decnet_h(self):
        expected = [
            u'Copyright (c) 1992, 1994, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/decnet.h')

    def test_ics_tcpdump_decode_prefix_h(self):
        expected = [
            u'Copyright (c) 1999 WIDE Project.',
        ]
        check_detection(expected, 'ics/tcpdump/decode_prefix.h')

    def test_ics_tcpdump_enc_h(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997, 1998 by John Ioannidis, Angelos D. Keromytis and Niels Provos.',
            u'Copyright (c) 2001, Angelos D. Keromytis.',
        ]
        check_detection(expected, 'ics/tcpdump/enc.h')

    def test_ics_tcpdump_gmt2local_c(self):
        expected = [
            u'Copyright (c) 1997 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/gmt2local.c')

    def test_ics_tcpdump_icmp6_h(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997, and 1998 WIDE Project.',
            u'Copyright (c) 1982, 1986, 1993 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/icmp6.h')

    def test_ics_tcpdump_ieee802_11_h(self):
        expected = [
            u'Copyright (c) 2001 Fortress Technologies Charlie Lenahan',
        ]
        check_detection(expected, 'ics/tcpdump/ieee802_11.h')

    @expectedFailure
    def test_ics_tcpdump_ieee802_11_h_trail_email(self):
        expected = [
            u'Copyright (c) 2001 Fortress Technologies Charlie Lenahan ( clenahan@fortresstech.com )',
        ]
        check_detection(expected, 'ics/tcpdump/ieee802_11.h')

    def test_ics_tcpdump_interface_h(self):
        expected = [
            u'Copyright (c) 1988-2002 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/interface.h')

    def test_ics_tcpdump_ipproto_h(self):
        expected = [
            u'Copyright (c) 1982, 1986, 1990, 1993 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/ipproto.h')

    def test_ics_tcpdump_l2tp_h(self):
        expected = [
            u'Copyright (c) 1991, 1993, 1994, 1995, 1996, 1997 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/l2tp.h')

    def test_ics_tcpdump_machdep_c(self):
        expected = [
            u'Copyright (c) 1996, 1997 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/machdep.c')

    def test_ics_tcpdump_makefile_in(self):
        expected = [
            u'Copyright (c) 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/Makefile.in')

    def test_ics_tcpdump_makemib(self):
        expected = [
            u'Copyright (c) 1990, 1996 John Robert LoVerso.',
            u'copyright (c) 1999 William C. Fenner.',
        ]
        check_detection(expected, 'ics/tcpdump/makemib')

    def test_ics_tcpdump_mpls_h(self):
        expected = [
            u'Copyright (c) 2001 WIDE Project.',
        ]
        check_detection(expected, 'ics/tcpdump/mpls.h')

    def test_ics_tcpdump_nameser_h(self):
        expected = [
            u'Copyright (c) 1983, 1989, 1993 The Regents of the University of California.',
            u'Portions Copyright (c) 1993 by Digital Equipment Corporation.',
        ]
        check_detection(expected, 'ics/tcpdump/nameser.h')

    def test_ics_tcpdump_netdissect_h(self):
        expected = [
            u'Copyright (c) 1988-1997 The Regents of the University of California.',
            u'Copyright (c) 1998-2004 Michael Richardson <mcr@tcpdump.org> The TCPDUMP project',
        ]
        check_detection(expected, 'ics/tcpdump/netdissect.h')

    def test_ics_tcpdump_nfs_h(self):
        expected = [
            u'Copyright (c) 1989, 1993 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/nfs.h')

    def test_ics_tcpdump_nfsfh_h_trail_name(self):
        expected = [
            u'Copyright (c) 1993, 1994 Jeffrey C. Mogul, Digital Equipment Corporation, Western Research Laboratory.',
            u'Copyright (c) 2001 Compaq Computer Corporation.',
        ]
        check_detection(expected, 'ics/tcpdump/nfsfh.h')

    def test_ics_tcpdump_parsenfsfh_c(self):
        expected = [
            u'Copyright (c) 1993, 1994 Jeffrey C. Mogul, Digital Equipment Corporation, Western Research Laboratory.',
            u'Copyright (c) 2001 Compaq Computer Corporation.',
        ]
        check_detection(expected, 'ics/tcpdump/parsenfsfh.c')

    def test_ics_tcpdump_pmap_prot_h(self):
        expected = [
            u'Copyright (c) 1984, Sun Microsystems, Inc.',
        ]
        check_detection(expected, 'ics/tcpdump/pmap_prot.h')

    def test_ics_tcpdump_print_ah_c(self):
        expected = [
            u'Copyright (c) 1988, 1989, 1990, 1991, 1992, 1993, 1994 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/print-ah.c')

    def test_ics_tcpdump_print_ap1394_c(self):
        expected = [
            u'Copyright (c) 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 2000 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/print-ap1394.c')

    def test_ics_tcpdump_print_ascii_c(self):
        expected = [
            u'Copyright (c) 1997, 1998 The NetBSD Foundation, Inc.',
        ]
        check_detection(expected, 'ics/tcpdump/print-ascii.c')

    def test_ics_tcpdump_print_atm_c(self):
        expected = [
            u'Copyright (c) 1994, 1995, 1996, 1997 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/print-atm.c')

    def test_ics_tcpdump_print_beep_c(self):
        expected = [
            u'Copyright (c) 2000, Richard Sharpe',
        ]
        check_detection(expected, 'ics/tcpdump/print-beep.c')

    def test_ics_tcpdump_print_bootp_c(self):
        expected = [
            u'Copyright (c) 1990, 1991, 1993, 1994, 1995, 1996, 1997 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/print-bootp.c')

    def test_ics_tcpdump_print_cdp_c(self):
        expected = [
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1997 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/print-cdp.c')

    def test_ics_tcpdump_print_cnfp_c(self):
        expected = [
            u'Copyright (c) 1998 Michael Shalayeff',
        ]
        check_detection(expected, 'ics/tcpdump/print-cnfp.c')

    def test_ics_tcpdump_print_dccp_c(self):
        expected = [
            u'Copyright (c) Arnaldo Carvalho de Melo 2004',
            u'Copyright (c) Ian McDonald 2005',
            u'Copyright (c) Yoshifumi Nishida 2005',
        ]
        check_detection(expected, 'ics/tcpdump/print-dccp.c')

    def test_ics_tcpdump_print_dhcp6_c(self):
        expected = [
            u'Copyright (c) 1998 and 1999 WIDE Project.',
        ]
        check_detection(expected, 'ics/tcpdump/print-dhcp6.c')

    def test_ics_tcpdump_print_dvmrp_c(self):
        expected = [
            u'Copyright (c) 1995, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/print-dvmrp.c')

    def test_ics_tcpdump_print_eap_c(self):
        expected = [
            u'Copyright (c) 2004 - Michael Richardson <mcr@xelerance.com>',
        ]
        check_detection(expected, 'ics/tcpdump/print-eap.c')

    def test_ics_tcpdump_print_egp_c(self):
        expected = [
            u'Copyright (c) 1991, 1992, 1993, 1994, 1995, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/print-egp.c')

    def test_ics_tcpdump_print_eigrp_c(self):
        expected = [
            u'Copyright (c) 1998-2004 Hannes Gredler <hannes@tcpdump.org> The TCPDUMP project',
        ]
        check_detection(expected, 'ics/tcpdump/print-eigrp.c')

    def test_ics_tcpdump_print_enc_c(self):
        expected = [
            u'Copyright (c) 1990, 1991, 1993, 1994, 1995, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/print-enc.c')

    def test_ics_tcpdump_print_fddi_c(self):
        expected = [
            u'Copyright (c) 1991, 1992, 1993, 1994, 1995, 1996, 1997 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/print-fddi.c')

    def test_ics_tcpdump_print_frag6_c(self):
        expected = [
            u'Copyright (c) 1988, 1989, 1990, 1991, 1993, 1994 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/print-frag6.c')

    def test_ics_tcpdump_print_gre_c(self):
        expected = [
            u'Copyright (c) 2002 Jason L. Wright (jason@thought.net)',
        ]
        check_detection(expected, 'ics/tcpdump/print-gre.c')

    def test_ics_tcpdump_print_hsrp_c(self):
        expected = [
            u'Copyright (c) 2001 Julian Cowley',
        ]
        check_detection(expected, 'ics/tcpdump/print-hsrp.c')

    def test_ics_tcpdump_print_ip6opts_c(self):
        expected = [
            u'Copyright (c) 1998 WIDE Project.',
        ]
        check_detection(expected, 'ics/tcpdump/print-ip6opts.c')

    def test_ics_tcpdump_print_krb_c(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/print-krb.c')

    def test_ics_tcpdump_print_lwres_c(self):
        expected = [
            u'Copyright (c) 2001 WIDE Project.',
        ]
        check_detection(expected, 'ics/tcpdump/print-lwres.c')

    def test_ics_tcpdump_print_mobile_c(self):
        expected = [
            u'(c) 1998 The NetBSD Foundation, Inc.',
        ]
        check_detection(expected, 'ics/tcpdump/print-mobile.c')

    def test_ics_tcpdump_print_mobility_c(self):
        expected = [
            u'Copyright (c) 2002 WIDE Project.',
        ]
        check_detection(expected, 'ics/tcpdump/print-mobility.c')

    def test_ics_tcpdump_print_msdp_c(self):
        expected = [
            u'Copyright (c) 2001 William C. Fenner.',
        ]
        check_detection(expected, 'ics/tcpdump/print-msdp.c')

    def test_ics_tcpdump_print_olsr_c(self):
        expected = [
            u'Copyright (c) 1998-2007 The TCPDUMP project',
        ]
        check_detection(expected, 'ics/tcpdump/print-olsr.c')

    def test_ics_tcpdump_print_radius_c(self):
        expected = [
            u'Copyright (c) 2000 Alfredo Andres Omella.',
        ]
        check_detection(expected, 'ics/tcpdump/print-radius.c')

    def test_ics_tcpdump_print_rip_c(self):
        expected = [
            u'Copyright (c) 1989, 1990, 1991, 1993, 1994, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/print-rip.c')

    def test_ics_tcpdump_print_ripng_c(self):
        expected = [
            u'Copyright (c) 1989, 1990, 1991, 1993, 1994 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/print-ripng.c')

    def test_ics_tcpdump_print_rx_c(self):
        expected = [
            u'Copyright (c) 2000 United States Government',
        ]
        check_detection(expected, 'ics/tcpdump/print-rx.c')

    @expectedFailure
    def test_ics_tcpdump_print_rx_c_trail_name(self):
        expected = [
            u'Copyright: (c) 2000 United States Government as represented by the Secretary of the Navy.',
        ]
        check_detection(expected, 'ics/tcpdump/print-rx.c')

    def test_ics_tcpdump_print_sctp_c_trail_name(self):
        expected = [
            u'Copyright (c) 2001 NETLAB, Temple University',
            u'Copyright (c) 2001 Protocol Engineering Lab, University of Delaware',
        ]
        check_detection(expected, 'ics/tcpdump/print-sctp.c')

    def test_ics_tcpdump_print_sl_c(self):
        expected = [
            u'Copyright (c) 1989, 1990, 1991, 1993, 1994, 1995, 1996, 1997 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/print-sl.c')

    def test_ics_tcpdump_print_slow_c(self):
        expected = [
            u'Copyright (c) 1998-2005 The TCPDUMP project',
        ]
        check_detection(expected, 'ics/tcpdump/print-slow.c')

    def test_ics_tcpdump_print_smb_c(self):
        expected = [
            u'Copyright (c) Andrew Tridgell 1995-1999',
        ]
        check_detection(expected, 'ics/tcpdump/print-smb.c')

    def test_ics_tcpdump_print_snmp_c(self):
        expected = [
            u'Copyright (c) 1990, 1991, 1993, 1994, 1995, 1996, 1997 John Robert LoVerso.',
            u'J. Schoenwaelder, Copyright (c) 1999.',
            u'Copyright (c) 1990, 1991, 1993, 1994, 1995, 1996, 1997 this software was produced',
        ]
        check_detection(expected, 'ics/tcpdump/print-snmp.c')

    @expectedFailure
    def test_ics_tcpdump_print_snmp_c_trail_name_lead_name_trail_name_complex(self):
        expected = [
            u'Copyright (c) 1990, 1991, 1993, 1994, 1995, 1996, 1997 John Robert LoVerso.',
            u'J. Schoenwaelder, Copyright (c) 1999.',
            u'Los Alamos National Laboratory Copyright (c) 1990, 1991, 1993, 1994, 1995, 1996, 1997',
        ]
        check_detection(expected, 'ics/tcpdump/print-snmp.c')

    def test_ics_tcpdump_print_stp_c(self):
        expected = [
            u'Copyright (c) 2000 Lennert Buytenhek',
        ]
        check_detection(expected, 'ics/tcpdump/print-stp.c')

    def test_ics_tcpdump_print_tcp_c(self):
        expected = [
            u'Copyright (c) 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997 The Regents of the University of California.',
            u'Copyright (c) 1999-2004 The tcpdump.org project',
        ]
        check_detection(expected, 'ics/tcpdump/print-tcp.c')

    def test_ics_tcpdump_print_telnet_c(self):
        expected = [
            u'Copyright (c) 1997, 1998 The NetBSD Foundation, Inc.',
            u'Copyright (c) 1994, Simon J. Gerraty.',
        ]
        check_detection(expected, 'ics/tcpdump/print-telnet.c')

    def test_ics_tcpdump_print_timed_c(self):
        expected = [
            u'Copyright (c) 2000 Ben Smithurst <ben@scientia.demon.co.uk>',
        ]
        check_detection(expected, 'ics/tcpdump/print-timed.c')

    def test_ics_tcpdump_print_token_c(self):
        expected = [
            u'Copyright (c) 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/print-token.c')

    def test_ics_tcpdump_print_vrrp_c(self):
        expected = [
            u'Copyright (c) 2000 William C. Fenner.',
        ]
        check_detection(expected, 'ics/tcpdump/print-vrrp.c')

    def test_ics_tcpdump_print_wb_c(self):
        expected = [
            u'Copyright (c) 1993, 1994, 1995, 1996 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/print-wb.c')

    def test_ics_tcpdump_print_zephyr_c(self):
        expected = [
            u'Copyright (c) 2001 Nickolai Zeldovich <kolya@MIT.EDU>',
        ]
        check_detection(expected, 'ics/tcpdump/print-zephyr.c')

    def test_ics_tcpdump_route6d_h(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997 and 1998 WIDE Project.',
        ]
        check_detection(expected, 'ics/tcpdump/route6d.h')

    def test_ics_tcpdump_sctpconstants_h_trail_name(self):
        expected = [
            u'Implementation Copyright (c) 1999 Cisco And Motorola',
        ]
        check_detection(expected, 'ics/tcpdump/sctpConstants.h')

    def test_ics_tcpdump_slcompress_h(self):
        expected = [
            u'Copyright (c) 1989, 1990, 1992, 1993 Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/slcompress.h')

    def test_ics_tcpdump_slip_h(self):
        expected = [
            u'Copyright (c) 1990 Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/slip.h')

    def test_ics_tcpdump_strcasecmp_c(self):
        expected = [
            u'Copyright (c) 1987 Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/strcasecmp.c')

    def test_ics_tcpdump_tcpdump_1_trail_name(self):
        expected = [
            u'Copyright (c) 1987, 1988, 1989, 1990, 1991, 1992, 1994, 1995, 1996, 1997 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/tcpdump.1')

    def test_ics_tcpdump_tcpdump_c(self):
        expected = [
            u'Copyright (c) 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 2000 The Regents of the University of California.',
            u'Copyright (c) 2001 Seth Webster <swebster@sst.ll.mit.edu>',
            u'Copyright (c) 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 2000 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/tcpdump.c')

    def test_ics_tcpdump_telnet_h(self):
        expected = [
            u'Copyright (c) 1983, 1993 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/telnet.h')

    def test_ics_tcpdump_token_h(self):
        expected = [
            u'Copyright (c) 1998, Larry Lile',
        ]
        check_detection(expected, 'ics/tcpdump/token.h')

    def test_ics_tcpdump_vfprintf_c(self):
        expected = [
            u'Copyright (c) 1995 The Regents of the University of California.',
        ]
        check_detection(expected, 'ics/tcpdump/vfprintf.c')

    def test_ics_tcpdump_missing_inet_aton_c_trail_place(self):
        expected = [
            u'Copyright (c) 1995, 1996, 1997 Kungliga Tekniska Hogskolan (Royal Institute of Technology, Stockholm, Sweden).',
        ]
        check_detection(expected, 'ics/tcpdump-missing/inet_aton.c')

    def test_ics_tcpdump_missing_inet_ntop_c_trail_place(self):
        expected = [
            u'Copyright (c) 1999 Kungliga Tekniska Hogskolan (Royal Institute of Technology, Stockholm, Sweden).',
        ]
        check_detection(expected, 'ics/tcpdump-missing/inet_ntop.c')

    def test_ics_tinyxml_android_mk(self):
        expected = [
            u'Copyright 2005 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/tinyxml/Android.mk')

    def test_ics_tinyxml_tinyxml_cpp(self):
        expected = [
            u'copyright (c) 2000-2002 Lee Thomason (www.grinninglizard.com)',
        ]
        check_detection(expected, 'ics/tinyxml/tinyxml.cpp')

    def test_ics_tinyxml_tinyxml_h(self):
        expected = [
            u'copyright (c) 2000-2002 Lee Thomason (www.grinninglizard.com)',
        ]
        check_detection(expected, 'ics/tinyxml/tinyxml.h')

    def test_ics_tremolo_notice(self):
        expected = [
            u'Copyright (c) 2002-2009, Xiph.org Foundation',
            u'Copyright (c) 2010, Robin Watts for Pinknoise Productions Ltd',
        ]
        check_detection(expected, 'ics/tremolo/NOTICE')

    def test_ics_tremolo_tremolo_asm_arm_h(self):
        expected = [
            u'Copyright (c) 2002-2009, Xiph.org Foundation',
            u'Copyright (c) 2010, Robin Watts for Pinknoise Productions Ltd',
        ]
        check_detection(expected, 'ics/tremolo-Tremolo/asm_arm.h')

    def test_ics_webp_examples_dwebp_c(self):
        expected = [
            u'Copyright 2010 Google Inc.',
        ]
        check_detection(expected, 'ics/webp-examples/dwebp.c')

    def test_ics_webp_include_webp_encode_h(self):
        expected = [
            u'Copyright 2011 Google Inc.',
        ]
        check_detection(expected, 'ics/webp-include-webp/encode.h')

    def test_ics_webp_src_dec_android_mk(self):
        expected = [
            u'Copyright 2010 The Android Open Source Project',
        ]
        check_detection(expected, 'ics/webp-src-dec/Android.mk')

    def test_ics_webp_src_enc_dsp_c(self):
        expected = [
            u'Copyright 2011 Google Inc.',
        ]
        check_detection(expected, 'ics/webp-src-enc/dsp.c')

    def test_ics_webrtc_android_webrtc_mk(self):
        expected = [
            u'Copyright (c) 2011 The WebRTC project',
        ]
        check_detection(expected, 'ics/webrtc/android-webrtc.mk')

    def test_ics_webrtc_notice(self):
        expected = [
            u'Copyright (c) 2011 The WebRTC project',
            u'Copyright (c) 2010 The Android Open Source Project',
            u'Copyright Takuya OOURA, 1996-2001',
            u'Copyright Takuya OOURA, 1996-2001',
            u'Copyright Steven J. Ross 2001 - 2009.',
        ]
        check_detection(expected, 'ics/webrtc/NOTICE')

    def test_ics_webrtc_src_common_types_h(self):
        expected = [
            u'Copyright (c) 2011 The WebRTC project',
        ]
        check_detection(expected, 'ics/webrtc-src/common_types.h')

    def test_ics_webrtc_src_modules_audio_processing_aec_main_source_aec_rdft_c(self):
        expected = [
            u'Copyright Takuya OOURA, 1996-2001',
        ]
        check_detection(expected, 'ics/webrtc-src-modules-audio_processing-aec-main-source/aec_rdft.c')

    def test_ics_webrtc_src_system_wrappers_source_spreadsortlib_spreadsort_hpp(self):
        expected = [
            u'Copyright Steven J. Ross 2001 - 2009.',
        ]
        check_detection(expected, 'ics/webrtc-src-system_wrappers-source-spreadsortlib/spreadsort.hpp')

    def test_ics_wpa_supplicant_aes_c(self):
        expected = [
            u'Copyright (c) 2003-2005, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/aes.c')

    def test_ics_wpa_supplicant_aes_h(self):
        expected = [
            u'Copyright (c) 2003-2006, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/aes.h')

    def test_ics_wpa_supplicant_aes_wrap_c(self):
        expected = [
            u'Copyright (c) 2003-2007, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/aes_wrap.c')

    def test_ics_wpa_supplicant_asn1_c(self):
        expected = [
            u'Copyright (c) 2006, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/asn1.c')

    def test_ics_wpa_supplicant_base64_c(self):
        expected = [
            u'Copyright (c) 2005, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/base64.c')

    def test_ics_wpa_supplicant_build_config_h(self):
        expected = [
            u'Copyright (c) 2005-2006, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/build_config.h')

    def test_ics_wpa_supplicant_common_c(self):
        expected = [
            u'Copyright (c) 2002-2006, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/common.c')

    def test_ics_wpa_supplicant_config_h(self):
        expected = [
            u'Copyright (c) 2003-2005, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/config.h')

    def test_ics_wpa_supplicant_crypto_c(self):
        expected = [
            u'Copyright (c) 2004-2005, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/crypto.c')

    def test_ics_wpa_supplicant_ctrl_iface_c(self):
        expected = [
            u'Copyright (c) 2004-2006, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/ctrl_iface.c')

    def test_ics_wpa_supplicant_ctrl_iface_dbus_c(self):
        expected = [
            u'Copyright (c) 2006, Dan Williams <dcbw@redhat.com> and Red Hat, Inc.',
        ]
        check_detection(expected, 'ics/wpa_supplicant/ctrl_iface_dbus.c')

    def test_ics_wpa_supplicant_driver_atmel_c(self):
        expected = [
            u'Copyright (c) 2000-2005, ATMEL Corporation',
            u'Copyright (c) 2004-2007, Jouni Malinen <j@w1.fi>',
            u'Copyright 2000-2001 ATMEL Corporation.',
        ]
        check_detection(expected, 'ics/wpa_supplicant/driver_atmel.c')

    def test_ics_wpa_supplicant_driver_broadcom_c(self):
        expected = [
            u'Copyright (c) 2004, Nikki Chumkov <nikki@gattaca.ru>',
            u'Copyright (c) 2004, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/driver_broadcom.c')

    def test_ics_wpa_supplicant_driver_bsd_c(self):
        expected = [
            u'Copyright (c) 2004, Sam Leffler <sam@errno.com>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/driver_bsd.c')

    def test_ics_wpa_supplicant_driver_ipw_c(self):
        expected = [
            u'Copyright (c) 2005 Zhu Yi <yi.zhu@intel.com>',
            u'Copyright (c) 2004 Lubomir Gelo <lgelo@cnc.sk>',
            u'Copyright (c) 2003-2004, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/driver_ipw.c')

    def test_ics_wpa_supplicant_driver_madwifi_c(self):
        expected = [
            u'Copyright (c) 2004, Sam Leffler <sam@errno.com>',
            u'Copyright (c) 2004-2005, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/driver_madwifi.c')

    def test_ics_wpa_supplicant_driver_ndiswrapper_c(self):
        expected = [
            u'Copyright (c) 2004-2006, Giridhar Pemmasani <giri@lmc.cs.sunysb.edu>',
            u'Copyright (c) 2004-2006, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/driver_ndiswrapper.c')

    def test_ics_wpa_supplicant_driver_prism54_c(self):
        expected = [
            u'Copyright (c) 2003-2005, Jouni Malinen <j@w1.fi>',
            u'Copyright (c) 2004, Luis R. Rodriguez <mcgrof@ruslug.rutgers.edu>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/driver_prism54.c')

    def test_ics_wpa_supplicant_driver_wired_c(self):
        expected = [
            u'Copyright (c) 2005-2007, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/driver_wired.c')

    def test_ics_wpa_supplicant_eap_gpsk_c(self):
        expected = [
            u'Copyright (c) 2006-2007, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/eap_gpsk.c')

    def test_ics_wpa_supplicant_eap_psk_c(self):
        expected = [
            u'Copyright (c) 2004-2007, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/eap_psk.c')

    def test_ics_wpa_supplicant_eap_sim_common_c(self):
        expected = [
            u'Copyright (c) 2004-2008, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/eap_sim_common.c')

    def test_ics_wpa_supplicant_eapol_test_c(self):
        expected = [
            u'Copyright (c) 2003-2006, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/eapol_test.c')

    def test_ics_wpa_supplicant_eloop_c(self):
        expected = [
            u'Copyright (c) 2002-2005, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/eloop.c')

    def test_ics_wpa_supplicant_l2_packet_freebsd_c(self):
        expected = [
            u'Copyright (c) 2003-2005, Jouni Malinen <j@w1.fi>',
            u'Copyright (c) 2005, Sam Leffler <sam@errno.com>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/l2_packet_freebsd.c')

    def test_ics_wpa_supplicant_mlme_c(self):
        expected = [
            u'Copyright (c) 2003-2006, Jouni Malinen <j@w1.fi>',
            u'Copyright (c) 2004, Instant802 Networks, Inc.',
            u'Copyright (c) 2005-2006, Devicescape Software, Inc.',
        ]
        check_detection(expected, 'ics/wpa_supplicant/mlme.c')

    def test_ics_wpa_supplicant_notice(self):
        expected = [
            u'Copyright (c) 2003-2008, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/NOTICE')

    def test_ics_wpa_supplicant_radius_c(self):
        expected = [
            u'Copyright (c) 2002-2008, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/radius.c')

    def test_ics_wpa_supplicant_tls_none_c(self):
        expected = [
            u'Copyright (c) 2004, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/tls_none.c')

    def test_ics_wpa_supplicant_wireless_copy_h(self):
        expected = [
            u'Copyright (c) 1997-2007 Jean Tourrilhes',
        ]
        check_detection(expected, 'ics/wpa_supplicant/wireless_copy.h')

    def test_ics_wpa_supplicant_wpa_cli_c(self):
        expected = [
            u'Copyright (c) 2004-2008, Jouni Malinen <j@w1.fi>',
            u'Copyright (c) 2004-2008, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/wpa_cli.c')

    def test_ics_wpa_supplicant_wpa_supplicant_c(self):
        expected = [
            u'Copyright (c) 2003-2008, Jouni Malinen <j@w1.fi>',
            u'Copyright (c) 2003-2008, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant/wpa_supplicant.c')

    def test_ics_wpa_supplicant_wpa_gui_wpagui_ui_h(self):
        expected = [
            u'Copyright (c) 2003-2008, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant-wpa_gui/wpagui.ui.h')

    def test_ics_wpa_supplicant_wpa_gui_qt4_wpagui_cpp(self):
        expected = [
            u'Copyright (c) 2005-2008, Jouni Malinen <j@w1.fi>',
            u'Copyright (c) 2003-2008, Jouni Malinen <j@w1.fi>',
        ]
        check_detection(expected, 'ics/wpa_supplicant-wpa_gui-qt4/wpagui.cpp')

    def test_ics_xmlwriter_src_org_jheer_xmlwriter_java(self):
        expected = [
            u'Copyright (c) 2004-2006 Regents of the University of California.',
        ]
        check_detection(expected, 'ics/xmlwriter-src-org-jheer/XMLWriter.java')

    def test_ics_yaffs2_yaffs2_devextras_h(self):
        expected = [
            u'Copyright (c) 2002 Aleph One Ltd. for Toby Churchill Ltd and Brightstar Engineering',
        ]
        check_detection(expected, 'ics/yaffs2-yaffs2/devextras.h')

    def test_ics_yaffs2_yaffs2_patch_ker_sh(self):
        expected = [
            u'Copyright (c) 2002 Aleph One Ltd.',
        ]
        check_detection(expected, 'ics/yaffs2-yaffs2/patch-ker.sh')

    def test_ics_yaffs2_yaffs2_yaffs_qsort_h(self):
        expected = [
            u'Copyright (c) 2000-2002 Silicon Graphics, Inc.',
        ]
        check_detection(expected, 'ics/yaffs2-yaffs2/yaffs_qsort.h')

    def test_ics_yaffs2_yaffs2_direct_makefile(self):
        expected = [
            u'Copyright (c) 2003 Aleph One Ltd.',
        ]
        check_detection(expected, 'ics/yaffs2-yaffs2-direct/Makefile')

    def test_ics_zlib_adler32_c(self):
        expected = [
            u'Copyright (c) 1995-2007 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib/adler32.c')

    def test_ics_zlib_crc32_c(self):
        expected = [
            u'Copyright (c) 1995-2006, 2010 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib/crc32.c')

    def test_ics_zlib_deflate_c(self):
        expected = [
            u'Copyright (c) 1995-2010 Jean-loup Gailly and Mark Adler',
            u'Copyright 1995-2010 Jean-loup Gailly and Mark Adler',
        ]
        check_detection(expected, 'ics/zlib/deflate.c')

    def test_ics_zlib_deflate_h(self):
        expected = [
            u'Copyright (c) 1995-2010 Jean-loup Gailly',
        ]
        check_detection(expected, 'ics/zlib/deflate.h')

    def test_ics_zlib_example_c(self):
        expected = [
            u'Copyright (c) 1995-2006 Jean-loup Gailly.',
        ]
        check_detection(expected, 'ics/zlib/example.c')

    def test_ics_zlib_gzclose_c(self):
        expected = [
            u'Copyright (c) 2004, 2010 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib/gzclose.c')

    def test_ics_zlib_gzguts_h(self):
        expected = [
            u'Copyright (c) 2004, 2005, 2010 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib/gzguts.h')

    def test_ics_zlib_infback_c(self):
        expected = [
            u'Copyright (c) 1995-2009 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib/infback.c')

    def test_ics_zlib_inffast_c(self):
        expected = [
            u'Copyright (c) 1995-2008, 2010 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib/inffast.c')

    def test_ics_zlib_inffast_h(self):
        expected = [
            u'Copyright (c) 1995-2003, 2010 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib/inffast.h')

    def test_ics_zlib_inflate_c(self):
        expected = [
            u'Copyright (c) 1995-2010 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib/inflate.c')

    def test_ics_zlib_inftrees_c(self):
        expected = [
            u'Copyright (c) 1995-2010 Mark Adler',
            u'Copyright 1995-2010 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib/inftrees.c')

    def test_ics_zlib_inftrees_h(self):
        expected = [
            u'Copyright (c) 1995-2005, 2010 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib/inftrees.h')

    def test_ics_zlib_makefile_in(self):
        expected = [
            u'Copyright (c) 1995-2010 Jean-loup Gailly.',
        ]
        check_detection(expected, 'ics/zlib/Makefile.in')

    def test_ics_zlib_minigzip_c(self):
        expected = [
            u'Copyright (c) 1995-2006, 2010 Jean-loup Gailly.',
        ]
        check_detection(expected, 'ics/zlib/minigzip.c')

    def test_ics_zlib_notice(self):
        expected = [
            u'(c) 1995-2004 Jean-loup Gailly and Mark Adler',
        ]
        check_detection(expected, 'ics/zlib/NOTICE')

    def test_ics_zlib_readme(self):
        expected = [
            u'(c) 1995-2010 Jean-loup Gailly and Mark Adler',
        ]
        check_detection(expected, 'ics/zlib/README')

    def test_ics_zlib_trees_c(self):
        expected = [
            u'Copyright (c) 1995-2010 Jean-loup Gailly',
        ]
        check_detection(expected, 'ics/zlib/trees.c')

    def test_ics_zlib_uncompr_c(self):
        expected = [
            u'Copyright (c) 1995-2003, 2010 Jean-loup Gailly.',
        ]
        check_detection(expected, 'ics/zlib/uncompr.c')

    def test_ics_zlib_zconf_h(self):
        expected = [
            u'Copyright (c) 1995-2010 Jean-loup Gailly.',
        ]
        check_detection(expected, 'ics/zlib/zconf.h')

    def test_ics_zlib_zlib_h(self):
        expected = [
            u'Copyright (c) 1995-2010 Jean-loup Gailly and Mark Adler',
        ]
        check_detection(expected, 'ics/zlib/zlib.h')

    def test_ics_zlib_zutil_c(self):
        expected = [
            u'Copyright (c) 1995-2005, 2010 Jean-loup Gailly.',
        ]
        check_detection(expected, 'ics/zlib/zutil.c')

    def test_ics_zlib_amiga_makefile_pup(self):
        expected = [
            u'Copyright (c) 1998 by Andreas R. Kleinert',
        ]
        check_detection(expected, 'ics/zlib-amiga/Makefile.pup')

    def test_ics_zlib_contrib_ada_buffer_demo_adb(self):
        expected = [
            u'Copyright (c) 2002-2004 Dmitriy Anisimkov',
        ]
        check_detection(expected, 'ics/zlib-contrib-ada/buffer_demo.adb')

    def test_ics_zlib_contrib_ada_mtest_adb(self):
        expected = [
            u'Copyright (c) 2002-2003 Dmitriy Anisimkov',
        ]
        check_detection(expected, 'ics/zlib-contrib-ada/mtest.adb')

    def test_ics_zlib_contrib_ada_zlib_ads(self):
        expected = [
            u'Copyright (c) 2002-2004 Dmitriy Anisimkov',
        ]
        check_detection(expected, 'ics/zlib-contrib-ada/zlib.ads')

    def test_ics_zlib_contrib_blast_blast_c(self):
        expected = [
            u'Copyright (c) 2003 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib-contrib-blast/blast.c')

    def test_ics_zlib_contrib_blast_blast_h(self):
        expected = [
            u'Copyright (c) 2003 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib-contrib-blast/blast.h')

    def test_ics_zlib_contrib_delphi_readme_txt(self):
        expected = [
            u'Copyright (c) 1997,99 Borland Corp.',
        ]
        check_detection(expected, 'ics/zlib-contrib-delphi/readme.txt')

    def test_ics_zlib_contrib_dotzlib_readme_txt(self):
        expected = [
            u'Copyright (c) Henrik Ravn 2004',
        ]
        check_detection(expected, 'ics/zlib-contrib-dotzlib/readme.txt')

    def test_ics_zlib_contrib_dotzlib_dotzlib_checksumimpl_cs(self):
        expected = [
            u'(c) Copyright Henrik Ravn 2004',
        ]
        check_detection(expected, 'ics/zlib-contrib-dotzlib-DotZLib/ChecksumImpl.cs')

    def test_ics_zlib_contrib_dotzlib_dotzlib_assemblyinfo_cs(self):
        expected = [
            u'(c) 2004 by Henrik Ravn',
        ]
        check_detection(expected, 'ics/zlib-contrib-dotzlib-DotZLib/AssemblyInfo.cs')

    def test_ics_zlib_contrib_infback9_infback9_c(self):
        expected = [
            u'Copyright (c) 1995-2008 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib-contrib-infback9/infback9.c')

    def test_ics_zlib_contrib_infback9_infback9_h(self):
        expected = [
            u'Copyright (c) 2003 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib-contrib-infback9/infback9.h')

    def test_ics_zlib_contrib_inflate86_inffas86_c(self):
        expected = [
            u'Copyright (c) 1995-2003 Mark Adler',
            u'Copyright (c) 2003 Chris Anderson <christop@charm.net>',
        ]
        check_detection(expected, 'ics/zlib-contrib-inflate86/inffas86.c')

    def test_ics_zlib_contrib_masmx86_gvmat32c_c(self):
        expected = [
            u'Copyright (c) 1995-1996 Jean-loup Gailly and Gilles Vollant.',
        ]
        check_detection(expected, 'ics/zlib-contrib-masmx86/gvmat32c.c')

    def test_ics_zlib_contrib_minizip_crypt_h(self):
        expected = [
            u'Copyright (c) 1998-2005 Gilles Vollant',
        ]
        check_detection(expected, 'ics/zlib-contrib-minizip/crypt.h')

    def test_ics_zlib_contrib_minizip_ioapi_c(self):
        expected = [
            u'Copyright (c) 1998-2010 Gilles Vollant',
            u'Copyright (c) 2009-2010 Mathias Svensson http://result42.com',
        ]
        check_detection(expected, 'ics/zlib-contrib-minizip/ioapi.c')

    def test_ics_zlib_contrib_minizip_miniunz_c(self):
        expected = [
            u'Copyright (c) 1998-2010 Gilles Vollant',
            u'Copyright (c) 2007-2008 Even Rouault',
            u'Copyright (c) 2009-2010 Mathias Svensson http://result42.com',
        ]
        check_detection(expected, 'ics/zlib-contrib-minizip/miniunz.c')

    def test_ics_zlib_contrib_minizip_minizip64_info_txt(self):
        expected = [
            u'Copyright (c) 1998-2010 - by Gilles Vollant',
        ]
        check_detection(expected, 'ics/zlib-contrib-minizip/MiniZip64_info.txt')

    def test_ics_zlib_contrib_minizip_unzip_c(self):
        expected = [
            u'Copyright (c) 1998-2010 Gilles Vollant',
            u'Copyright (c) 2007-2008 Even Rouault',
            u'Copyright (c) 2009-2010 Mathias Svensson http://result42.com',
            u'Copyright (c) 1990-2000 Info-ZIP.',
            u'Copyright (c) 2007-2008 Even Rouault',
            u'Copyright (c) 1998 - 2010 Gilles Vollant, Even Rouault, Mathias Svensson',
            u'Copyright 1998-2004 Gilles Vollant',
        ]
        check_detection(expected, 'ics/zlib-contrib-minizip/unzip.c')

    def test_ics_zlib_contrib_minizip_zip_c(self):
        expected = [
            u'Copyright (c) 1998-2010 Gilles Vollant',
            u'Copyright (c) 2009-2010 Mathias Svensson http://result42.com',
            u'Copyright 1998-2004 Gilles Vollant',
        ]
        check_detection(expected, 'ics/zlib-contrib-minizip/zip.c')

    def test_ics_zlib_contrib_pascal_readme_txt(self):
        expected = [
            u'Copyright (c) 1995-2003 Jean-loup Gailly and Mark Adler.',
            u'Copyright (c) 1998 by Bob Dellaca.',
            u'Copyright (c) 2003 by Cosmin Truta.',
            u'Copyright (c) 1995-2003 by Jean-loup Gailly.',
            u'Copyright (c) 1998,1999,2000 by Jacques Nomssi Nzali.',
            u'Copyright (c) 2003 by Cosmin Truta.',
        ]
        check_detection(expected, 'ics/zlib-contrib-pascal/readme.txt')

    def test_ics_zlib_contrib_puff_puff_c(self):
        expected = [
            u'Copyright (c) 2002-2010 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib-contrib-puff/puff.c')

    def test_ics_zlib_contrib_puff_puff_h(self):
        expected = [
            u'Copyright (c) 2002-2010 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib-contrib-puff/puff.h')

    def test_ics_zlib_contrib_vstudio_vc10_zlib_rc(self):
        expected = [
            u'(c) 1995-2010 Jean-loup Gailly & Mark Adler',
        ]
        check_detection(expected, 'ics/zlib-contrib-vstudio-vc10/zlib.rc')

    def test_ics_zlib_contrib_vstudio_vc7_zlib_rc(self):
        expected = [
            u'(c) 1995-2003 Jean-loup Gailly & Mark Adler',
        ]
        check_detection(expected, 'ics/zlib-contrib-vstudio-vc7/zlib.rc')

    def test_ics_zlib_doc_rfc1950_txt(self):
        expected = [
            u'Copyright (c) 1996 L. Peter Deutsch and Jean-Loup Gailly',
        ]
        check_detection(expected, 'ics/zlib-doc/rfc1950.txt')

    def test_ics_zlib_doc_rfc1951_txt(self):
        expected = [
            u'Copyright (c) 1996 L. Peter Deutsch',
        ]
        check_detection(expected, 'ics/zlib-doc/rfc1951.txt')

    def test_ics_zlib_examples_enough_c(self):
        expected = [
            u'Copyright (c) 2007, 2008 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib-examples/enough.c')

    def test_ics_zlib_examples_gun_c(self):
        expected = [
            u'Copyright (c) 2003, 2005, 2008, 2010 Mark Adler',
            u'Copyright (c) 2003-2010 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib-examples/gun.c')

    def test_ics_zlib_examples_gzappend_c(self):
        expected = [
            u'Copyright (c) 2003 Mark Adler',
            u'Copyright (c) 2003 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib-examples/gzappend.c')

    def test_ics_zlib_examples_gzjoin_c(self):
        expected = [
            u'Copyright (c) 2004 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib-examples/gzjoin.c')

    def test_ics_zlib_examples_gzlog_c(self):
        expected = [
            u'Copyright (c) 2004, 2008 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib-examples/gzlog.c')

    def test_ics_zlib_examples_gzlog_h(self):
        expected = [
            u'Copyright (c) 2004, 2008 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib-examples/gzlog.h')

    def test_ics_zlib_examples_zlib_how_html(self):
        expected = [
            u'Copyright (c) 2004, 2005 Mark Adler.',
            u'Copyright (c) 2004, 2005 by Mark Adler',
        ]
        check_detection(expected, 'ics/zlib-examples/zlib_how.html')

    def test_ics_zlib_examples_zran_c(self):
        expected = [
            u'Copyright (c) 2005 Mark Adler',
        ]
        check_detection(expected, 'ics/zlib-examples/zran.c')

    def test_ics_zlib_msdos_makefile_dj2(self):
        expected = [
            u'Copyright (c) 1995-1998 Jean-loup Gailly.',
        ]
        check_detection(expected, 'ics/zlib-msdos/Makefile.dj2')

    def test_ics_zlib_old_zlib_html(self):
        expected = [
            u'Copyright (c) 1995-2002 Jean-loup Gailly and Mark Adler',
        ]
        check_detection(expected, 'ics/zlib-old/zlib.html')

    def test_ics_zlib_old_visualc6_readme_txt(self):
        expected = [
            u'Copyright (c) 2000-2004 Simon-Pierre Cadieux.',
            u'Copyright (c) 2004 Cosmin Truta.',
        ]
        check_detection(expected, 'ics/zlib-old-visualc6/README.txt')

    def test_ics_zlib_win32_makefile_gcc(self):
        expected = [
            u'Copyright (c) 1995-2003 Jean-loup Gailly.',
        ]
        check_detection(expected, 'ics/zlib-win32/Makefile.gcc')

    def test_ics_zlib_win32_makefile_msc(self):
        expected = [
            u'copyright (c) 1995-2006 Jean-loup Gailly and Mark Adler',
        ]
        check_detection(expected, 'ics/zlib-win32/Makefile.msc')

    def test_ics_zlib_win32_zlib1_rc(self):
        expected = [
            u'(c) 1995-2006 Jean-loup Gailly & Mark Adler',
        ]
        check_detection(expected, 'ics/zlib-win32/zlib1.rc')
