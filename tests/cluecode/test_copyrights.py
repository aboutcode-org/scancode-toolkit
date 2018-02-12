
# -*- coding: utf-8 -*-
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

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os.path
from unittest.case import expectedFailure

from commoncode.testcase import FileBasedTesting
from cluecode_assert_utils import check_detection
import cluecode.copyrights


class TestTextPreparation(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_strip_numbers(self):
        a = 'Python 2.6.6 (r266:84297, Aug 24 2010, 18:46:32) [MSC v.1500 32 bit (Intel)] on win32'
        expected = 'Python 2.6.6 (r266:84297, Aug 2010, 18:46:32) [MSC v.1500 bit (Intel)] on win32'
        assert expected == cluecode.copyrights.strip_numbers(a)

    def test_prepare_text(self):
        cp = ''' test (C) all rights reserved'''
        result = cluecode.copyrights.prepare_text_line(cp)
        assert 'test (c) all rights reserved' == result

    def test_is_all_rights_reserved(self):
        line = '''          "All rights reserved\\n"'''
        assert cluecode.copyrights.is_all_rights_reserved(line)

    def test_candidate_lines_simple(self):
        lines = ''' test (C) all rights reserved'''.splitlines(False)
        result = list(cluecode.copyrights.candidate_lines(lines))
        expected = [[(1, ' test (C) all rights reserved')]]
        assert expected == result

    def test_candidate_lines_complex(self):
        lines = '''
           Apache Xalan (Xalan XSLT processor)
           Copyright 1999-2006 The Apache Software Foundation

           Apache Xalan (Xalan serializer)

           This product includes software developed at
           The Apache Software Foundation (http://www.apache.org/).


           =========================================================================
           Portions of this software was originally based on the following:
             - software copyright (c) 1999-2002, Lotus Development Corporation.,
               http://www.lotus.com.
             - software copyright (c) 2001-2002, Sun Microsystems.,
               http://www.sun.com.
             - software copyright (c) 2003, IBM Corporation.,
               http://www.ibm.com.

           =========================================================================
           The binary distribution package (ie. jars, samples and documentation) of
           this product includes software developed by the following:
        '''.splitlines(False)

        expected = [
            [(2, '           Apache Xalan (Xalan XSLT processor)'),
             (3, '           Copyright 1999-2006 The Apache Software Foundation')],

            [(7, '           This product includes software developed at'),
             (8, '           The Apache Software Foundation (http://www.apache.org/).')],

            [(12, '           Portions of this software was originally based on the following:'),
             (13, '             - software copyright (c) 1999-2002, Lotus Development Corporation.,'),
             (14, '               http://www.lotus.com.'),
             (15, '             - software copyright (c) 2001-2002, Sun Microsystems.,'),
             (16, '               http://www.sun.com.'),
             (17, '             - software copyright (c) 2003, IBM Corporation.,'),
             (18, '               http://www.ibm.com.')],

            [(21, '           The binary distribution package (ie. jars, samples and documentation) of'),
             (22, '           this product includes software developed by the following:')]
        ]

        result = list(cluecode.copyrights.candidate_lines(lines))
        assert expected == result

    def test_is_candidates_should_not_select_line_with_bare_full_year(self):
        line = '2012'
        assert not cluecode.copyrights.is_candidate(line)

    def test_is_candidates_should_not_select_line_with_full_year_before_160_and_after_2018(self):
        line = '1959 2019'
        assert not cluecode.copyrights.is_candidate(line)

    def test_is_candidate_should_not_select_line_with_only_two_digit_numbers(self):
        line = 'template<class V> struct v_iter<V, mpl::int_<10> > { typedef typename V::item10 type; typedef v_iter<V, mpl::int_<10 + 1> > next; };'
        assert not cluecode.copyrights.is_candidate(line)

    def test_is_candidate_should_select_line_with_sign(self):
        line = 'template<class V> struct v_iter<V, mpl::int_<10> (c) { typedef typename V::item10 type; typedef v_iter<V, mpl::int_<10 + 1> > next; };'
        assert cluecode.copyrights.is_candidate(line)

    def test_is_candidate_should_not_select_line_with_junk_hex(self):
        line = '01061C3F5280CD4AC504152B81E452BD82015442014'
        assert not cluecode.copyrights.is_candidate(line)

    def test_is_candidate_should_not_select_line_with_trailing_years(self):
        line = '01061C3F5280CD4AC504152B81E452BD820154 2014\n'
        assert not cluecode.copyrights.is_candidate(line)

    def test_is_candidate_should_select_line_with_proper_years(self):
        line = '01061C3F5280CD4AC504152B81E452BD820154 2014-'
        assert cluecode.copyrights.is_candidate(line)

        line = '01061C3F5280CD4,2016 152B81E452BD820154'
        assert cluecode.copyrights.is_candidate(line)

    def test_is_candidate_should_select_line_with_dashed_year(self):
        line = 'pub   1024D/CCD6F801 2006-11-15'
        assert cluecode.copyrights.is_candidate(line)

    def test_is_candidate_should_select_line_with_iso_date_year(self):
        line = 'sig 3 ccd6f801 2006-11-15 nathan mittler <nathan.mittler@gmail.com>'
        assert cluecode.copyrights.is_candidate(line)


class TestCopyrightDetector(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_detect(self):
        location = self.get_test_loc('copyrights/essential_smoke-ibm_c.c')
        expected = [
            'Copyright IBM and others (c) 2008',
            'Copyright Eclipse, IBM and others (c) 2008'
        ]
        copyrights, _, _, _ = cluecode.copyrights.detect(location)
        assert expected == copyrights


class TestCopyrightDetection(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_company_name_in_java(self):
        test_file = self.get_test_loc('copyrights/company_name_in_java-9_java.java')
        expected = [
            'Copyright (c) 2008-2011 Company Name Incorporated',
        ]
        check_detection(expected, test_file)

    def test_03e16f6c_0(self):
        test_file = self.get_test_loc('copyrights/03e16f6c_0-e_f_c.0')
        expected = [
            'Copyright (c) 1997 Microsoft Corp.',
            'Copyright (c) 1997 Microsoft Corp.',
            '(c) 1997 Microsoft',
        ]
        check_detection(expected, test_file,
                        expected_in_results=True,
                        results_in_expected=False)

    def test_3a3b02ce_0(self):
        # this is a certificate and the actual copyright holder is not clear:
        # could be either Wisekey or OISTE Foundation.
        test_file = self.get_test_loc('copyrights/3a3b02ce_0-a_b_ce.0')
        expected = [
            'Copyright (c) 2005, OU OISTE Foundation Endorsed, CN OISTE WISeKey Global Root',
            'Copyright (c) 2005, OU OISTE Foundation Endorsed, CN OISTE WISeKey Global Root',
        ]
        check_detection(expected, test_file)

    def test_ABC_cpp(self):
        test_file = self.get_test_loc('copyrights/ABC_cpp-Case_cpp.cpp')
        expected = [
            'Copyright (c) ABC Company',
        ]
        check_detection(expected, test_file)

    def test_ABC_file_cpp(self):
        test_file = self.get_test_loc('copyrights/ABC_file_cpp-File_cpp.cpp')
        expected = [
            'Copyright (c) ABC Company',
        ]
        check_detection(expected, test_file)

    def test_false_positive_in_c(self):
        test_file = self.get_test_loc('copyrights/false_positive_in_c-false_positives_c.c')
        expected = []
        check_detection(expected, test_file)

    def test_false_positive_in_js(self):
        test_file = self.get_test_loc('copyrights/false_positive_in_js-editor_beta_de_js.js')
        expected = []
        check_detection(expected, test_file)

    def test_false_positive_in_license(self):
        test_file = self.get_test_loc('copyrights/false_positive_in_license-LICENSE')
        expected = []
        check_detection(expected, test_file)

    def test_heunrich_c(self):
        test_file = self.get_test_loc('copyrights/heunrich_c-c.c')
        expected = [
            'Copyright (c) 2000 HEUNRICH HERTZ INSTITUTE',
        ]
        check_detection(expected, test_file)

    def test_isc(self):
        test_file = self.get_test_loc('copyrights/isc-c.c')
        expected = [
            'Copyright (c) 1998-2000 The Internet Software Consortium.',
        ]
        check_detection(expected, test_file)

    def test_no_class_file_1(self):
        test_file = self.get_test_loc('copyrights/no_class_file_1-PersistentArrayHolder_class.class')
        expected = []
        check_detection(expected, test_file)

    def test_sample_py(self):
        test_file = self.get_test_loc('copyrights/sample_py-py.py')
        expected = [
            'COPYRIGHT 2006 ABC ABC',
        ]
        check_detection(expected, test_file)

    def test_abc(self):
        test_file = self.get_test_loc('copyrights/abc')
        expected = [
            'Copyright (c) 2006 abc.org',
        ]
        check_detection(expected, test_file)

    def test_abc_loss_of_holder_c(self):
        test_file = self.get_test_loc('copyrights/abc_loss_of_holder_c-c.c')
        expected = [
            'copyright abc 2001',
        ]
        check_detection(expected, test_file)

    def test_abiword_common(self):
        test_file = self.get_test_loc('copyrights/abiword_common.copyright')
        expected = [
            'Copyright (c) 1998- AbiSource, Inc. & Co.',
            'Copyright (c) 2009 Masayuki Hatta',
            'Copyright (c) 2009 Patrik Fimml <patrik@fimml.at>',
        ]
        check_detection(expected, test_file)

    def test_acme_c(self):
        test_file = self.get_test_loc('copyrights/acme_c-c.c')
        expected = [
            'Copyright (c) 2000 ACME, Inc.',
        ]
        check_detection(expected, test_file)

    def test_activefieldattribute_cs(self):
        test_file = self.get_test_loc('copyrights/activefieldattribute_cs-ActiveFieldAttribute_cs.cs')
        expected = [
            'Web Applications Copyright 2009 - Thomas Hansen thomas@ra-ajax.org.',
        ]
        check_detection(expected, test_file)

    def test_addr_c(self):
        test_file = self.get_test_loc('copyrights/addr_c-addr_c.c')
        expected = [
            'Copyright 1999 Cornell University.',
            'Copyright 2000 Jon Doe.',
        ]
        check_detection(expected, test_file)

    def test_apostrophe_in_name(self):
        test_file = self.get_test_loc('copyrights/with_apos.txt')
        expected = [
            "Copyright Marco d'Itri <md@Linux.IT>",
            "Copyright Marco d'Itri",
        ]
        check_detection(expected, test_file)

    def test_adler_inflate_c(self):
        test_file = self.get_test_loc('copyrights/adler_inflate_c-inflate_c.c')
        expected = [
            'Not copyrighted 1992 by Mark Adler',
        ]
        check_detection(expected, test_file)

    def test_adobe_flashplugin(self):
        test_file = self.get_test_loc('copyrights/adobe_flashplugin-adobe_flashplugin.label')
        expected = [
            'Copyright (c) 1996 - 2008. Adobe Systems Incorporated',
            '(c) 2001-2009, Takuo KITAME, Bart Martens, and Canonical, LTD',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_aleal(self):
        test_file = self.get_test_loc('copyrights/aleal-c.c')
        expected = [
            'copyright (c) 2006 by aleal',
        ]
        check_detection(expected, test_file)

    def test_andre_darcy(self):
        test_file = self.get_test_loc('copyrights/andre_darcy-c.c')
        expected = [
            'Copyright (c) 1995, Pascal Andre (andre@via.ecp.fr).',
            "copyright 1997, 1998, 1999 by D'Arcy J.M. Cain (darcy@druid.net)",
        ]
        check_detection(expected, test_file)

    def test_android_c(self):
        test_file = self.get_test_loc('copyrights/android_c-c.c')
        expected = [
            'Copyright (c) 2009 The Android Open Source Project',
            'Copyright 2003-2005 Colin Percival',
        ]
        check_detection(expected, test_file)

    def test_apache2_debian_trailing_name_missed(self):
        test_file = self.get_test_loc('copyrights/apache2_debian_trailing_name_missed-apache.label')
        expected = [
            'copyright Steinar H. Gunderson <sgunderson@bigfoot.com> and Knut Auvor Grythe <knut@auvor.no>',
            'Copyright (c) 1996-1997 Cisco Systems, Inc.',
            'Copyright (c) Ian F. Darwin',
            'Copyright (c) Ian F. Darwin 1986, 1987, 1989, 1990, 1991, 1992, 1994, 1995.',
            'copyright 1992 by Eric Haines, erich@eye.com',
            'Copyright (c) 1995, Board of Trustees of the University of Illinois',
            'Copyright (c) 1994, Jeff Hostetler, Spyglass, Inc.',
            'Copyright (c) 1993, 1994 by Carnegie Mellon University',
            'Copyright (c) 1991 Bell Communications Research, Inc.',
            '(c) Copyright 1993,1994 by Carnegie Mellon University',
            'Copyright (c) 1991 Bell Communications Research, Inc.',
            'Copyright RSA Data Security, Inc.',
            'Copyright (c) 1991-2, RSA Data Security, Inc.',
            'Copyright RSA Data Security, Inc.',
            'Copyright (c) 1991-2, RSA Data Security, Inc.',
            'copyright RSA Data Security, Inc.',
            'Copyright (c) 1991-2, RSA Data Security, Inc.',
            'copyright RSA Data Security, Inc.',
            'Copyright (c) 1991-2, RSA Data Security, Inc.',
            'Copyright (c) 2000-2002 The Apache Software Foundation',
            'copyright RSA Data Security, Inc.',
            'Copyright (c) 1990-2, RSA Data Security, Inc.',
            'Copyright 1991 by the Massachusetts Institute of Technology',
            'Copyright 1991 by the Massachusetts Institute of Technology',
            'Copyright (c) 1997-2001 University of Cambridge',
            'copyright by the University of Cambridge, England.',
            'Copyright (c) Zeus Technology Limited 1996.',
            'Copyright (c) 1998, 1999, 2000 Thai Open Source Software Center Ltd and Clark Cooper',
            'copyright of Pete Harlow'
        ]
        check_detection(expected, test_file)

    def test_apache_notice(self):
        test_file = self.get_test_loc('copyrights/apache_notice-NOTICE')
        expected = [
            'Copyright 1999-2006 The Apache Software Foundation',
            'Copyright 1999-2006 The Apache Software Foundation',
            'Copyright 2001-2003,2006 The Apache Software Foundation.',
            'copyright (c) 2000 World Wide Web Consortium, http://www.w3.org',
        ]
        check_detection(expected, test_file)

    def test_aptitude(self):
        test_file = self.get_test_loc('copyrights/aptitude-aptitude.label')
        expected = [
            'Copyright 1999-2005 Daniel Burrows <dburrows@debian.org>',
        ]
        check_detection(expected, test_file)

    def test_atheros_spanning_lines(self):
        test_file = self.get_test_loc('copyrights/atheros_spanning_lines-py.py')
        expected = [
            'Copyright (c) 2000 Atheros Communications, Inc.',
            'Copyright (c) 2001 Atheros Communications, Inc.',
            'Copyright (c) 1994-1997 by Intel Corporation.',
        ]
        check_detection(expected, test_file)

    def test_att_in_c(self):
        test_file = self.get_test_loc('copyrights/att_in_c-9_c.c')
        expected = [
            'Copyright (c) 1991 by AT&T.',
        ]
        check_detection(expected, test_file)

    def test_audio_c(self):
        test_file = self.get_test_loc('copyrights/audio_c-c.c')
        expected = [
            'copyright (c) 1995, AudioCodes, DSP Group, France Telecom, Universite de Sherbrooke.',
        ]
        check_detection(expected, test_file)

    def test_babkin_txt(self):
        test_file = self.get_test_loc('copyrights/babkin_txt.txt')
        expected = [
            'Copyright (c) North',
            'Copyright (c) South',
            'Copyright (c) 2001 by the TTF2PT1 project',
            'Copyright (c) 2001 by Sergey Babkin',
        ]
        check_detection(expected, test_file)

    def test_blender_debian(self):
        test_file = self.get_test_loc('copyrights/blender_debian-blender.copyright')
        expected = [
            'Copyright (c) 2002-2008 Blender Foundation',
            'Copyright (c) 2004-2005 Masayuki Hatta <mhatta@debian.org>',
            '(c) 2005-2007 Florian Ernst <florian@debian.org>',
            '(c) 2007-2008 Cyril Brulebois <kibi@debian.org>',
        ]
        check_detection(expected, test_file)

    def test_blue_sky_dash_in_name(self):
        test_file = self.get_test_loc('copyrights/blue_sky_dash_in_name-c.c')
        expected = [
            'Copyright (c) 1995, 1996 - Blue Sky Software Corp. -',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_bouncy_license(self):
        test_file = self.get_test_loc('copyrights/bouncy_license-LICENSE')
        expected = [
            'Copyright (c) 2000-2005 The Legion Of The Bouncy Castle (http://www.bouncycastle.org)',
        ]
        check_detection(expected, test_file)

    def test_bouncy_notice(self):
        test_file = self.get_test_loc('copyrights/bouncy_notice-9_NOTICE')
        expected = [
            'Copyright (c) 2000-2005 The Legion Of The Bouncy Castle (http://www.bouncycastle.org)',
        ]
        check_detection(expected, test_file)

    def test_btt_plot1_py(self):
        test_file = self.get_test_loc('copyrights/btt_plot1_py-btt_plot_py.py')
        expected = [
            '(c) Copyright 2009 Hewlett-Packard Development Company, L.P.',
        ]
        check_detection(expected, test_file)

    def test_camelcase_bug_br_fcc_thread_psipstack_c(self):
        test_file = self.get_test_loc('copyrights/camelcase_bug_br_fcc_thread_psipstack_c-br_fcc_thread_psipstack_c.c')
        expected = [
            'Copyright 2010-2011 by BitRouter',
        ]
        check_detection(expected, test_file)

    def test_ccube_txt(self):
        test_file = self.get_test_loc('copyrights/ccube_txt.txt')
        expected = [
            'Copyright (c) 2001 C-Cube Microsystems.',
        ]
        check_detection(expected, test_file)

    def test_cedrik_java(self):
        test_file = self.get_test_loc('copyrights/cedrik_java-java.java')
        expected = [
            'copyright (c) 2005-2006 Cedrik LIME',
        ]
        check_detection(expected, test_file,
                        expected_in_results=True,
                        results_in_expected=False)

    def test_cern(self):
        test_file = self.get_test_loc('copyrights/cern-TestMatrix_D_java.java')
        expected = [
            'Copyright 1999 CERN - European Organization for Nuclear Research.',
        ]
        check_detection(expected, test_file)

    def test_cern_matrix2d_java(self):
        test_file = self.get_test_loc('copyrights/cern_matrix2d_java-TestMatrix_D_java.java')
        expected = [
            'Copyright 1999 CERN - European Organization for Nuclear Research.',
            'Copyright (c) 1998 <p> Company PIERSOL Engineering Inc.',
            'Copyright (c) 1998 <p> Company PIERSOL Engineering Inc.',
        ]
        check_detection(expected, test_file)

    def test_chameleon_assembly(self):
        test_file = self.get_test_loc('copyrights/chameleon_assembly-9_9_setjmp_S.S')
        expected = [
            'Copyright Chameleon Systems, 1999',
        ]
        check_detection(expected, test_file)

    def test_co_cust(self):
        test_file = self.get_test_loc('copyrights/co_cust-java.java')
        expected = [
            'Copyright (c) 2009 <p> Company Customer Identity Hidden',
        ]
        check_detection(expected, test_file)

    def test_colin_android(self):
        test_file = self.get_test_loc('copyrights/colin_android-bsdiff_c.c')
        expected = [
            'Copyright (c) 2009 The Android Open Source Project',
            'Copyright 2003-2005 Colin Percival',
        ]
        check_detection(expected, test_file)

    def test_company_in_txt(self):
        test_file = self.get_test_loc('copyrights/company_in_txt-9.txt')
        expected = [
            'Copyright (c) 2008-2011 Company Name Incorporated',
        ]
        check_detection(expected, test_file)

    def test_complex_4_line_statement_in_text(self):
        test_file = self.get_test_loc('copyrights/complex_4_line_statement_in_text-9.txt')
        expected = [
            'Copyright 2002 Jonas Borgstrom <jonas@codefactory.se> 2002 Daniel Lundin <daniel@codefactory.se> 2002 CodeFactory AB',
            'Copyright (c) 1994 The Regents of the University of California',
        ]
        check_detection(expected, test_file)

    def test_complex_notice(self):
        test_file = self.get_test_loc('copyrights/complex_notice-NOTICE')
        expected = [
            'Copyright (c) 2003, Steven G. Kargl',
            'Copyright (c) 2003 Mike Barcroft <mike@FreeBSD.org>',
            'Copyright (c) 2002, 2003 David Schultz <das@FreeBSD.ORG>',
            'Copyright (c) 2003 David Schultz <das@FreeBSD.ORG>',
            'Copyright (c) 2004 David Schultz <das@FreeBSD.ORG>',
            'Copyright (c) 2004-2005 David Schultz <das@FreeBSD.ORG>',
            'Copyright (c) 2005 David Schultz <das@FreeBSD.ORG>',
            'Copyright (c) 2002 David Schultz <das@FreeBSD.ORG>',
            'Copyright (c) 2004 Stefan Farfeleder',
            'Copyright (c) 2003 Dag-Erling Coidan Smrgrav',
            'Copyright (c) 1996 The NetBSD Foundation, Inc.',
            'Copyright (c) 1985, 1993',
            'Copyright (c) 1988, 1993',
            'Copyright (c) 1992, 1993 The Regents of the University of California.',
            'Copyright (c) 1993,94 Winning Strategies, Inc.',
            'Copyright (c) 1994 Winning Strategies, Inc.',
            'Copyright (c) 1993 by Sun Microsystems, Inc.',
            'Copyright (c) 1993 by Sun Microsystems, Inc.',
            'Copyright (c) 1993 by Sun Microsystems, Inc.',
            'Copyright (c) 2004 by Sun Microsystems, Inc.',
            'Copyright (c) 2004 Stefan Farfeleder',
            'Copyright (c) 2004 David Schultz <das@FreeBSD.org>',
            'Copyright (c) 2004, 2005 David Schultz <das@FreeBSD.org>',
            'Copyright (c) 2003 Mike Barcroft <mike@FreeBSD.org>',
            'Copyright (c) 2005 David Schultz <das@FreeBSD.org>',
            'Copyright (c) 2003, Steven G. Kargl',
            'Copyright (c) 1991 The Regents of the University of California.',
        ]
        check_detection(expected, test_file)

    def test_complex_notice_sun_microsystems_on_multiple_lines(self):
        test_file = self.get_test_loc('copyrights/complex_notice_sun_microsystems_on_multiple_lines-NOTICE')
        expected = [
            'Copyright 1999-2006 The Apache Software Foundation',
            'copyright (c) 1999-2002, Lotus Development Corporation., http://www.lotus.com.',
            'copyright (c) 2001-2002, Sun Microsystems., http://www.sun.com.',
            'copyright (c) 2003, IBM Corporation., http://www.ibm.com.',
            'copyright (c) 1999, IBM Corporation., http://www.ibm.com.',
            'copyright (c) 1999, Sun Microsystems., http://www.sun.com.',
            'copyright (c) 1999, IBM Corporation., http://www.ibm.com.',
            'copyright (c) 1999, Sun Microsystems., http://www.sun.com.',
        ]
        check_detection(expected, test_file)

    def test_config(self):
        test_file = self.get_test_loc('copyrights/config-config_guess.guess')
        expected = [
            'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_config1_guess(self):
        test_file = self.get_test_loc('copyrights/config1_guess-config_guess.guess')
        expected = [
            'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_camelcase_br_diagnostics_h(self):
        test_file = self.get_test_loc('copyrights/camelcase_br_diagnostics_h-br_diagnostics_h.h')
        expected = [
            'Copyright 2011 by BitRouter',
        ]
        check_detection(expected, test_file)

    def test_coreutils_debian(self):
        test_file = self.get_test_loc('copyrights/coreutils_debian-coreutils.copyright')
        expected = [
            'Copyright (c) 2004, 2005, 2006, 2007, 2008 Free Software Foundation, Inc.',
            'Copyright (c) 1990, 1993, 1994 The Regents of the University of California',
            'Copyright (c) 2004, 2005, 2006, 2007 Free Software Foundation, Inc.',
            'Copyright (c) 1989, 1993 The Regents of the University of California',
            'Copyright (c) 1999-2006 Free Software Foundation, Inc.',
            'Copyright (c) 1997, 1998, 1999 Colin Plumb',
            'Copyright (c) 2005, 2006 Free Software Foundation, Inc.',
            'Copyright (c) 1996-1999 by Internet Software Consortium',
            'Copyright (c) 2004, 2006, 2007 Free Software Foundation, Inc.',
            'Copyright (c) 1997-2007 Free Software Foundation, Inc.',
            'Copyright (c) 1984 David M. Ihnat',
            'Copyright (c) 1996-2007 Free Software Foundation, Inc.',
            'Copyright (c) 1994, 1995, 1997, 1998, 1999, 2000 H. Peter Anvin',
            'Copyright (c) 1997-2005 Free Software Foundation, Inc.',
            'Copyright (c) 1984 David M. Ihnat',
            'Copyright (c) 1999-2007 Free Software Foundation, Inc.',
            'Copyright (c) 1997, 1998, 1999 Colin Plumb',
            'Copyright 1994-1996, 2000-2008 Free Software Foundation, Inc.',
            'Copyright (c) 1984-2008 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_dag_c(self):
        test_file = self.get_test_loc('copyrights/dag_c-s_fabsl_c.c')
        expected = [
            'Copyright (c) 2003 Dag-Erling Coidan Smrgrav',
        ]
        check_detection(expected, test_file)

    def test_dag_elring_notice(self):
        test_file = self.get_test_loc('copyrights/dag_elring_notice-NOTICE')
        expected = [
            'Copyright (c) 2003 Dag-Erling Codan Smrgrav',
        ]
        check_detection(expected, test_file)

    def test_dash_in_name(self):
        test_file = self.get_test_loc('copyrights/dash_in_name-Makefile')
        expected = [
            '(c) 2011 - Anycompany, LLC',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_dasher(self):
        test_file = self.get_test_loc('copyrights/dasher-dasher.label')
        expected = [
            'Copyright (c) 1998-2008 The Dasher Project',
        ]
        check_detection(expected, test_file)

    def test_date_range_dahua_in_c(self):
        test_file = self.get_test_loc('copyrights/date_range_dahua_in_c-c.c')
        expected = [
            '(c) Copyright 2006 to 2007 Dahua Digital.',
        ]
        check_detection(expected, test_file)

    def test_date_range_in_c(self):
        test_file = self.get_test_loc('copyrights/date_range_in_c-c.c')
        expected = [
            'Copyright (c) ImageSilicon Tech. (2006 - 2007)',
        ]
        check_detection(expected, test_file)

    def test_date_range_in_c_2(self):
        test_file = self.get_test_loc('copyrights/date_range_in_c_2-c.c')
        expected = [
            '(c) Copyright 2005 to 2007 ImageSilicon? Tech.,ltd',
        ]
        check_detection(expected, test_file)

    def test_debian_archive_keyring(self):
        test_file = self.get_test_loc('copyrights/debian_archive_keyring-debian_archive_keyring.copyright')
        expected = [
            'Copyright (c) 2006 Michael Vogt <mvo@debian.org>',
        ]
        check_detection(expected, test_file)

    def test_debian_lib_1(self):
        test_file = self.get_test_loc('copyrights/debian_lib_1-libmono_cairo_cil.label')
        expected = [
            'Copyright 2004 The Apache Software Foundation',
            'Copyright (c) 2001-2005 Novell',
            'Copyright (c) Microsoft Corporation',
            'Copyright (c) 2007 James Newton-King',
            'Copyright (c) 2002-2004 James W. Newkirk , Michael C. Two , Alexei A. Vorontsov , Charlie Poole',
            'Copyright (c) 2000-2004 Philip A. Craig',
            'Portions Copyright (c) 2002-2004 James W. Newkirk , Michael C. Two , Alexei A. Vorontsov , Charlie Poole',
            'Copyright (c) 2000-2004 Philip A. Craig',
            'Copyright (c) 2007, 2008 LShift Ltd.',
            'Copyright (c) 2007, 2008 Cohesive Financial Technologies LLC.',
            'Copyright (c) 2007, 2008 Rabbit Technologies Ltd.',
            'Copyright (c) 2007, 2008 LShift Ltd. , Cohesive Financial Technologies LLC., and Rabbit Technologies Ltd.',
            'Copyright (c) 2007, 2008 LShift Ltd. , Cohesive Financial Technologies LLC.',  # , and Rabbit Technologies Ltd.',
            'Copyright (c) 2007 LShift Ltd. , Cohesive Financial Technologies LLC.',  # , and Rabbit Technologies Ltd.',
            'Copyright (c) ???? Simon Mourier <simonm@microsoft.com>',
        ]
        check_detection(expected, test_file)

    def test_debian_lib_2(self):
        test_file = self.get_test_loc('copyrights/debian_lib_2-libmono_cairo_cil.copyright')
        expected = [
            'Copyright 2004 The Apache Software Foundation',
            'Copyright (c) 2001-2005 Novell',
            'Copyright (c) Microsoft Corporation',
            'Copyright (c) 2007 James Newton-King',
            'Copyright (c) 2002-2004 James W. Newkirk , Michael C. Two , Alexei A. Vorontsov , Charlie Poole',
            'Copyright (c) 2000-2004 Philip A. Craig',
            'Portions Copyright (c) 2002-2004 James W. Newkirk , Michael C. Two , Alexei A. Vorontsov , Charlie Poole',
            'Copyright (c) 2000-2004 Philip A. Craig',
            'Copyright (c) 2007, 2008 LShift Ltd.',
            'Copyright (c) 2007, 2008 Cohesive Financial Technologies LLC.',
            'Copyright (c) 2007, 2008 Rabbit Technologies Ltd.',
            'Copyright (c) 2007, 2008 LShift Ltd., Cohesive Financial Technologies LLC.',
            'Copyright (c) 2007, 2008 LShift Ltd. , Cohesive Financial Technologies LLC.',
            'Copyright (c) 2007 LShift Ltd. , Cohesive Financial Technologies LLC.',
            'Copyright (c) ???? Simon Mourier <simonm@microsoft.com>',
        ]
        check_detection(expected, test_file)

    def test_debian_lib_3(self):
        test_file = self.get_test_loc('copyrights/debian_lib_3-libmono_security_cil.copyright')
        expected = [
            'Copyright 2004 The Apache Software Foundation',
            'Copyright (c) 2001-2005 Novell',
            'Copyright (c) Microsoft Corporation',
            'Copyright (c) 2007 James Newton-King',
            'Copyright (c) 2002-2004 James W. Newkirk , Michael C. Two , Alexei A. Vorontsov , Charlie Poole',
            'Copyright (c) 2000-2004 Philip A. Craig',
            'Portions Copyright (c) 2002-2004 James W. Newkirk , Michael C. Two , Alexei A. Vorontsov , Charlie Poole',
            'Copyright (c) 2000-2004 Philip A. Craig',
            'Copyright (c) 2007, 2008 LShift Ltd.',
            'Copyright (c) 2007, 2008 Cohesive Financial Technologies LLC.',
            'Copyright (c) 2007, 2008 Rabbit Technologies Ltd.',
            'Copyright (c) 2007, 2008 LShift Ltd. , Cohesive Financial Technologies LLC.',
            'Copyright (c) 2007, 2008 LShift Ltd. , Cohesive Financial Technologies LLC.',
            'Copyright (c) 2007 LShift Ltd., Cohesive Financial Technologies LLC., and Rabbit Technologies Ltd.',
            'Copyright (c) ???? Simon Mourier <simonm@microsoft.com>',
        ]
        check_detection(expected, test_file)

    def test_debian_multi_names_on_one_line(self):
        test_file = self.get_test_loc('copyrights/debian_multi_names_on_one_line-libgdata.copyright')
        expected = [
            'Copyright 1999-2004 Ximian, Inc. 1999-2005 Novell, Inc.',
            'copyright 2000-2003 Ximian, Inc. , 2003 Gergo Erdi',
            'copyright 2000 Eskil Heyn Olsen , 2000 Ximian, Inc.',
            'copyright 1998 The Free Software Foundation , 2000 Ximian, Inc.',
            'copyright 1998-2005 The OpenLDAP Foundation',
            'Copyright 1999-2003 The OpenLDAP Foundation , Redwood City, California',
            'Copyright 1999-2000 Eric Busboom , The Software Studio (http://www.softwarestudio.org) 2001 Critical Path',
            '(c) Copyright 1996 Apple Computer , Inc., AT&T Corp. , International Business Machines Corporation and Siemens Rolm Communications Inc.',
            'Copyright (c) 1997 Theo de Raadt',
            'copyright 2000 Andrea Campi',
            'copyright 2002 Andrea Campi',
            'copyright 2003 Andrea Campi',
            'Copyright 2002 Jonas Borgstrom <jonas@codefactory.se> 2002 Daniel Lundin <daniel@codefactory.se> 2002 CodeFactory AB',
            'copyright 1996 Apple Computer, Inc. , AT&T Corp. , International Business Machines Corporation and Siemens Rolm Communications Inc.',
            'copyright 1986-2000 Hiram Clawson',
            'copyright 1997 Theo de Raadt',
            'Copyright (c) 1996-2002 Sleepycat Software',
            'Copyright (c) 1990, 1993, 1994, 1995, 1996 Keith Bostic',
            'Copyright (c) 1990, 1993, 1994, 1995 The Regents of the University of California',
        ]
        check_detection(expected, test_file)  # ,
#                         expected_in_results=False,
#                         results_in_expected=True)

    def test_dionysos_c(self):
        test_file = self.get_test_loc('copyrights/dionysos_c-c.c')
        expected = [
            'COPYRIGHT (c) 2006 - 2009 DIONYSOS',
            'COPYRIGHT (c) ADIONYSOS 2006 - 2009',
            'COPYRIGHT (c) ADIONYSOS2 2006',
            'COPYRIGHT (c) MyCompany 2006 - 2009',
            'COPYRIGHT (c) 2006 MyCompany2',
            'copyright (c) 2006 - 2009 DIONYSOS',
            'copyright (c) ADIONYSOS 2006 - 2009',
            'copyright (c) ADIONYSOS2 2006',
            'copyright (c) MyCompany 2006 - 2009',
            'copyright (c) 2006 MyCompany2',
        ]
        check_detection(expected, test_file)

    def test_disclaimed(self):
        test_file = self.get_test_loc('copyrights/disclaimed-c.c')
        expected = [
            'Copyright disclaimed 2003 by Andrew Clarke',
        ]
        check_detection(expected, test_file)

    def test_djvulibre_desktop(self):
        test_file = self.get_test_loc('copyrights/djvulibre_desktop-djvulibre_desktop.copyright')
        expected = [
            'Copyright (c) 2002 Leon Bottou and Yann Le Cun',
            'Copyright (c) 2001 AT&T',
            'Copyright (c) 1999-2001 LizardTech, Inc.',
        ]
        check_detection(expected, test_file)

    def test_docbook_xsl_doc_html(self):
        test_file = self.get_test_loc('copyrights/docbook_xsl_doc_html-docbook_xsl_doc_html.copyright')
        expected = [
            'Copyright (c) 1999-2007 Norman Walsh',
            'Copyright (c) 2003 Jiri Kosek',
            'Copyright (c) 2004-2007 Steve Ball',
            'Copyright (c) 2005-2008 The DocBook Project',
        ]
        check_detection(expected, test_file)

    def test_drand48_c(self):
        test_file = self.get_test_loc('copyrights/drand48_c-drand_c.c')
        expected = [
            'Copyright (c) 1993 Martin Birgmeier',
        ]
        check_detection(expected, test_file)

    def test_ed(self):
        test_file = self.get_test_loc('copyrights/ed-ed.copyright')
        expected = [
            'Copyright (c) 1993, 1994 Andrew Moore , Talke Studio',
            'Copyright (c) 2006, 2007 Antonio Diaz Diaz',
            'Copyright (c) 1997-2007 James Troup',
            'Copyright (c) 1993, 2006, 2007 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_epiphany_browser_data(self):
        test_file = self.get_test_loc('copyrights/epiphany_browser_data-epiphany_browser_data.label')
        expected = [
            'Copyright (c) 2004 the Initial Developer.',
            '(c) 2003-2007, the Debian GNOME team <pkg-gnome-maintainers@lists.alioth.debian.org>',
        ]
        check_detection(expected, test_file)

    def test_eric_young_c(self):
        test_file = self.get_test_loc('copyrights/eric_young_c-c.c')
        expected = [
            'Copyright (c) 1995-1997 Eric Young (eay@mincom.oz.au)',
        ]
        check_detection(expected, test_file)

    def test_errno_atheros(self):
        test_file = self.get_test_loc('copyrights/errno_atheros-c.c')
        expected = [
            'Copyright (c) 2002-2006 Sam Leffler, Errno Consulting, Atheros Communications, Inc.',
        ]
        check_detection(expected, test_file)

    def test_errno_atheros_ah_h(self):
        test_file = self.get_test_loc('copyrights/errno_atheros_ah_h-ah_h.h')
        expected = [
            'Copyright (c) 2002-2006 Sam Leffler, Errno Consulting, Atheros Communications, Inc.',
        ]
        check_detection(expected, test_file)

    def test_errno_c(self):
        test_file = self.get_test_loc('copyrights/errno_c-c.c')
        expected = [
            'Copyright (c) 2002-2006 Sam Leffler, Errno Consulting, Atheros Communications, Inc.',
        ]
        check_detection(expected, test_file)

    def test_esmertec_java(self):
        test_file = self.get_test_loc('copyrights/esmertec_java-java.java')
        expected = [
            'Copyright (c) 2008 Esmertec AG',
            'Copyright (c) 2008 The Android Open Source Project',
        ]
        check_detection(expected, test_file)

    def test_essential_smoke(self):
        test_file = self.get_test_loc('copyrights/essential_smoke-ibm_c.c')
        expected = [
            'Copyright IBM and others (c) 2008',
            'Copyright Eclipse, IBM and others (c) 2008',
        ]
        check_detection(expected, test_file)

    def test_expat_h(self):
        test_file = self.get_test_loc('copyrights/expat_h-expat_h.h')
        expected = [
            'Copyright (c) 1998, 1999, 2000 Thai Open Source Software Center Ltd',
        ]
        check_detection(expected, test_file)

    def test_ext_all_js(self):
        test_file = self.get_test_loc('copyrights/ext_all_js-ext_all_js.js')
        expected = [
            'Copyright (c) 2006-2009 Ext JS, LLC',
        ]
        check_detection(expected, test_file)

    def test_extjs_c(self):
        test_file = self.get_test_loc('copyrights/extjs_c-c.c')
        expected = [
            'Copyright (c) 2006-2007, Ext JS, LLC.',
        ]
        check_detection(expected, test_file)

    def test_fsf_py(self):
        test_file = self.get_test_loc('copyrights/fsf_py-999_py.py')
        expected = [
            'Copyright 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_gailly(self):
        test_file = self.get_test_loc('copyrights/gailly-c.c')
        expected = [
            'Copyright (c) 1992-1993 Jean-loup Gailly.',
            'Copyright (c) 1992-1993 Jean-loup Gailly',
            'Copyright (c) 1992-1993 Jean-loup Gailly',
        ]
        check_detection(expected, test_file)

    def test_geoff_js(self):
        test_file = self.get_test_loc('copyrights/geoff_js-js.js')
        expected = [
            'Copyright (c) 2007-2008 Geoff Stearns, Michael Williams, and Bobby van der Sluis',
        ]
        check_detection(expected, test_file)

    def test_gnome_session(self):
        test_file = self.get_test_loc('copyrights/gnome_session-gnome_session.copyright')
        expected = [
            'Copyright (c) 1999-2009 Red Hat, Inc.',
            'Copyright (c) 1999-2007 Novell, Inc.',
            'Copyright (c) 2001-2003 George Lebl',
            'Copyright (c) 2001 Queen of England',
            'Copyright (c) 2007-2008 William Jon McCann',
            'Copyright (c) 2006 Ray Strode',
            'Copyright (c) 2008 Lucas Rocha',
            'Copyright (c) 2005 Raffaele Sandrini',
            'Copyright (c) 2006-2007 Vincent Untz',
            'Copyright (c) 1998 Tom Tromey',
            'Copyright (c) 1999 Free Software Foundation, Inc.',
            'Copyright (c) 2003 Sun Microsystems, Inc.',
        ]
        check_detection(expected, test_file)

    def test_gnome_system_monitor(self):
        test_file = self.get_test_loc('copyrights/gnome_system_monitor-gnome_system_monitor.copyright')
        expected = [
            'Copyright Holders: Kevin Vandersloot <kfv101@psu.edu> Erik Johnsson <zaphod@linux.nu>',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_gnome_system_monitor_label(self):
        test_file = self.get_test_loc('copyrights/gnome_system_monitor-gnome_system_monitor.label')
        expected = [
            'Copyright Holders: Kevin Vandersloot <kfv101@psu.edu> Erik Johnsson <zaphod@linux.nu>',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_gobjc_4_3(self):
        test_file = self.get_test_loc('copyrights/gobjc_4_3-gobjc.copyright')
        expected = [
            'Copyright (c) 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008 Free Software Foundation, Inc.',
            'copyright Free Software Foundation',
            'Copyright (c) 2004-2005 by Digital Mars , www.digitalmars.com',
            'Copyright (c) 1996-2003 Red Hat, Inc.',
        ]
        check_detection(expected, test_file)

    def test_google_closure_templates_java_html(self):
        test_file = self.get_test_loc('copyrights/google_closure_templates_java_html-html.html')
        expected = [
            '(c) 2009 Google',
        ]
        check_detection(expected, test_file)

    def test_google_view_layout1_xml(self):
        test_file = self.get_test_loc('copyrights/google_view_layout1_xml-view_layout_xml.xml')
        expected = [
            'Copyright (c) 2008 Google Inc.',
        ]
        check_detection(expected, test_file)

    def test_group(self):
        test_file = self.get_test_loc('copyrights/group-c.c')
        expected = [
            'Copyright (c) 2014 ARRis Group, Inc.',
            'Copyright (c) 2013 ARRIS Group, Inc.',
        ]
        check_detection(expected, test_file)

    def test_gsoap(self):
        test_file = self.get_test_loc('copyrights/gsoap-gSOAP')
        expected = [
            'Copyright (c) 2001-2004 Robert A. van Engelen, Genivia inc.',
            'Copyright (c) 2001-2004 Robert A. van Engelen, Genivia inc.',
        ]
        check_detection(expected, test_file)

    def test_gstreamer0_fluendo_mp3(self):
        test_file = self.get_test_loc('copyrights/gstreamer0_fluendo_mp3-gstreamer_fluendo_mp.copyright')
        expected = [
            'Copyright (c) 2005,2006 Fluendo',
            'Copyright 2005 Fluendo',
        ]
        check_detection(expected, test_file)

    def test_hall(self):
        test_file = self.get_test_loc('copyrights/hall-copyright.txt')
        expected = [
            'Copyright (c) 2004, Richard S. Hall',
            'Copyright (c) 2004, Didier Donsez',
            'Copyright (c) 2002,2003, Stefan Haustein, Oberhausen',
        ]
        check_detection(expected, test_file)

    def test_hans_jurgen_htm(self):
        test_file = self.get_test_loc('copyrights/hans_jurgen_htm-9_html.html')
        expected = [
            'Copyright (c) 2006 by Hans-Jurgen Koch.',
        ]
        check_detection(expected, test_file,
                        expected_in_results=True,
                        results_in_expected=False)

    def test_hansen_cs(self):
        test_file = self.get_test_loc('copyrights/hansen_cs-cs.cs')
        expected = [
            'Web Applications Copyright 2009 - Thomas Hansen thomas@ra-ajax.org.',
        ]
        check_detection(expected, test_file)

    def test_hciattach_qualcomm1_c(self):
        test_file = self.get_test_loc('copyrights/hciattach_qualcomm1_c-hciattach_qualcomm_c.c')
        expected = [
            'Copyright (c) 2005-2010 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, test_file)

    def test_hibernate(self):
        test_file = self.get_test_loc('copyrights/hibernate-hibernate.label')
        expected = [
            'Copyright (c) 2004-2006 Bernard Blackham <bernard@blackham.com.au>',
            'copyright (c) 2004-2006 Cameron Patrick <cameron@patrick.wattle.id.au>',
            'copyright (c) 2006- Martin F. Krafft <madduck@debian.org>',
        ]
        check_detection(expected, test_file)

    def test_holtmann(self):
        test_file = self.get_test_loc('copyrights/holtmann-hciattach_qualcomm_c.c')
        expected = [
            'Copyright (c) 2005-2010 Marcel Holtmann <marcel@holtmann.org>',
            'Copyright (c) 2010, Code Aurora Forum.',
        ]
        check_detection(expected, test_file)

    def test_hostapd_cli_c(self):
        test_file = self.get_test_loc('copyrights/hostapd_cli_c-hostapd_cli_c.c')
        expected = [
            'Copyright (c) 2004-2005, Jouni Malinen <jkmaline@cc.hut.fi>',
            'Copyright (c) 2004-2005, Jouni Malinen <jkmaline@cc.hut.fi>',
        ]
        check_detection(expected, test_file)

    def test_hp_notice(self):
        test_file = self.get_test_loc('copyrights/hp_notice-NOTICE')
        expected = [
            '(c) Copyright 2007 Hewlett-Packard Development Company, L.P.',
            '(c) Copyright 2008 Hewlett-Packard Development Company, L.P.',
            'Copyright (c) 2006 Alan D. Brunelle <Alan.Brunelle@hp.com>',
            'Copyright (c) 2007 Alan D. Brunelle <Alan.Brunelle@hp.com>',
            '(c) Copyright 2008 Hewlett-Packard Development Company, L.P.',
            '(c) Copyright 2009 Hewlett-Packard Development Company, L.P.',
            'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, test_file)

    def test_hpijs_ppds(self):
        test_file = self.get_test_loc('copyrights/hpijs_ppds-hpijs_ppds.label')
        expected = [
            'Copyright (c) 2003-2004 by Torsten Landschoff <torsten@debian.org>',
            'Copyright (c) 2004-2006 by Henrique de Moraes Holschuh <hmh@debian.org>',
            'Copyright (c) 2001-2006 Hewlett-Packard Company',
            'Copyright (c) 2001-2006 Hewlett-Packard Development Company, L.P.',
        ]
        check_detection(expected, test_file)

    def test_ibm_c(self):
        test_file = self.get_test_loc('copyrights/ibm_c-ibm_c.c')
        expected = [
            'Copyright (c) ibm technologies 2008',
            'Copyright (c) IBM Corporation 2008',
            'Copyright (c) Ibm Corp. 2008',
            'Copyright (c) ibm.com 2008',
            'Copyright (c) IBM technology 2008',
            'Copyright (c) IBM company 2008',
        ]
        check_detection(expected, test_file)

    def test_icedax(self):
        test_file = self.get_test_loc('copyrights/icedax-icedax.label')
        expected = [
            'Copyright 1998-2003 Heiko Eissfeldt',
            '(c) Peter Widow',
            '(c) Thomas Niederreiter',
            '(c) RSA Data Security, Inc.',
            'Copyright 1993 Yggdrasil Computing, Incorporated',
            'Copyright (c) 1999,2000-2004 J. Schilling',
            '(c) 1998-2002 by Heiko Eissfeldt, heiko@colossus.escape.de',
            '(c) 2002 by Joerg Schilling',
            '(c) 1996, 1997 Robert Leslie',
            'Copyright (c) 2002 J. Schilling',
            'Copyright (c) 1987, 1995-2003 J. Schilling',
            'Copyright 2001 H. Peter Anvin',
        ]
        check_detection(expected, test_file)

    def test_ifrename_c(self):
        test_file = self.get_test_loc('copyrights/ifrename_c-ifrename_c.c')
        expected = [
            'Copyright (c) 2004 Jean Tourrilhes <jt@hpl.hp.com>',
        ]
        check_detection(expected, test_file)

    def test_illinois_html(self):
        test_file = self.get_test_loc('copyrights/illinois_html-9_html.html')
        expected = [
            'Copyright 1999,2000,2001,2002,2003,2004 The Board of Trustees of the University of Illinois',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_COPYING_gpl(self):
        test_file = self.get_test_loc('copyrights/COPYING_gpl-COPYING_gpl.gpl')
        expected = [
            'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, test_file)

    def test_COPYRIGHT_madwifi(self):
        test_file = self.get_test_loc('copyrights/COPYRIGHT_madwifi-COPYRIGHT_madwifi.madwifi')
        expected = [
            'Copyright (c) 2002-2006 Sam Leffler, Errno Consulting, Atheros Communications, Inc.',
        ]
        check_detection(expected, test_file)

    def test_README(self):
        test_file = self.get_test_loc('copyrights/README-README')
        expected = [
            'Copyright (c) 2002-2006, Jouni Malinen <jkmaline@cc.hut.fi>',
        ]
        check_detection(expected, test_file)

    def test_bash(self):
        test_file = self.get_test_loc('copyrights/bash-shell_sh.sh')
        expected = [
            'Copyright (c) 2008 Hewlett-Packard Development Company, L.P.',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_binary_file_with_metadata(self):
        test_file = self.get_test_loc('copyrights/mp4_with_metadata.mp4')
        expected = [
            'copyright (c) 2016 Philippe',
            'copyright (c) 2016 Philippe http://nexb.com joe@nexb.com',
        ]
        check_detection(expected, test_file)

    @expectedFailure
    def test_windows_binary_lib(self):
        test_file = self.get_test_loc('copyrights/binary_lib-php_embed_lib.lib')
        expected = [
            'Copyright nexB and others (c) 2012',
        ]
        check_detection(expected, test_file)

    def test_windows_binary_dll_ignore_leading_junk(self):
        test_file = self.get_test_loc('copyrights/windows.dll')
        expected = [
            'Copyright nexB and others (c) 2012'
        ]
        check_detection(expected, test_file)

    def test_elf_binary_treats_new_lines_as_spaces(self):
        test_file = self.get_test_loc('copyrights/tor.bin')
        expected = [
            u'Copyright (c) 2001-2004, Roger Dingledine',
            u'Copyright (c) 2004-2006, Roger Dingledine, Nick Mathewson',
            u'Copyright (c) 2007-2015, The Tor Project, Inc.'
        ]
        check_detection(expected, test_file, what='copyrights')

    def test_c(self):
        test_file = self.get_test_loc('copyrights/c-c.c')
        expected = [
            'COPYRIGHT (c) STMicroelectronics 2005.',
        ]
        check_detection(expected, test_file)

    def test_c_include(self):
        test_file = self.get_test_loc('copyrights/c_include-h.h')
        expected = [
            'COPYRIGHT (c) ST-Microelectronics 1998.',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_dll_approximate(self):
        test_file = self.get_test_loc('copyrights/dll-9_msvci_dll.dll')
        expected = [
            'Copyright Myself and Me, Inc QjT F4P',
        ]
        check_detection(expected, test_file)

    @expectedFailure
    def test_dll_exact(self):
        test_file = self.get_test_loc('copyrights/dll-9_msvci_dll.dll')
        expected = [
            'Copyright Myself and Me, Inc',
        ]
        check_detection(expected, test_file)

    def test_h(self):
        test_file = self.get_test_loc('copyrights/h-h.h')
        expected = [
            'COPYRIGHT (c) ST-Microelectronics 1998.',
        ]
        check_detection(expected, test_file)

    @expectedFailure
    def test_html_comments(self):
        test_file = self.get_test_loc('copyrights/html_comments-html.html')
        expected = [
            'Copyright 2008 ABCD, LLC.',
        ]
        check_detection(expected, test_file)

    @expectedFailure
    def test_html_incorrect(self):
        test_file = self.get_test_loc('copyrights/html_incorrect-detail_9_html.html')
        expected = [
            'A12 Oe (c) 2004-2009',
        ]
        check_detection(expected, test_file)

    def test_maven_pom_xstream(self):
        test_file = self.get_test_loc('copyrights/maven_pom_xstream-pom_xml.xml')
        expected = [
            'Copyright (c) 2006 Joe Walnes.',
            'Copyright (c) 2006, 2007, 2008 XStream committers.',
        ]
        check_detection(expected, test_file)

    def test_media(self):
        test_file = self.get_test_loc('copyrights/media-a_png.png')
        expected = [
            'Copyright nexB and others (c) 2012',
        ]
        check_detection(expected, test_file)

    def test_phps(self):
        test_file = self.get_test_loc('copyrights/phps-phps.phps')
        expected = [
            'copyright 2005 Michal Migurski',
        ]
        check_detection(expected, test_file)

    def test_postcript(self):
        test_file = self.get_test_loc('copyrights/postcript-9_ps.ps')
        expected = [
            'Copyright 1999 Radical Eye Software',
        ]
        check_detection(expected, test_file)

    def test_txt(self):
        test_file = self.get_test_loc('copyrights/txt.txt')
        expected = [
            'Copyright ?2004-2006 Company',
        ]
        check_detection(expected, test_file)

    def test_visio_doc(self):
        test_file = self.get_test_loc('copyrights/visio_doc-Glitch_ERD_vsd.vsd')
        expected = []
        check_detection(expected, test_file)

    def test_inria_loss_of_holder_c(self):
        test_file = self.get_test_loc('copyrights/inria_loss_of_holder_c-c.c')
        expected = [
            'Copyright (c) 2000,2002,2003 INRIA, France Telecom',
        ]
        check_detection(expected, test_file)

    @expectedFailure
    def test_java(self):
        test_file = self.get_test_loc('copyrights/java-java.java')
        expected = [
            'Copyright (c) 1992-2002 by P.J. Plauger.',
        ]
        check_detection(expected, test_file)

    def test_java_passing(self):
        test_file = self.get_test_loc('copyrights/java-java.java')
        expected = [
            'Copyright (c) 1992-2002 by P.J.',
        ]
        check_detection(expected, test_file)

    def test_jdoe(self):
        test_file = self.get_test_loc('copyrights/jdoe-c.c')
        expected = [
            'Copyright 2009 J-Doe.',
        ]
        check_detection(expected, test_file)

    @expectedFailure
    def test_json_in_phps(self):
        test_file = self.get_test_loc('copyrights/json_in_phps-JSON_phps.phps')
        expected = [
            'copyright 2005 Michal Migurski',
        ]
        check_detection(expected, test_file)

    def test_json_in_phps_incorrect(self):
        test_file = self.get_test_loc('copyrights/json_in_phps_incorrect-JSON_phps.phps')
        expected = []
        check_detection(expected, test_file)

    def test_json_phps_html_incorrect(self):
        test_file = self.get_test_loc('copyrights/json_phps_html_incorrect-JSON_phps_html.html')
        expected = []
        check_detection(expected, test_file)

    @expectedFailure
    def test_json_phps_html(self):
        test_file = self.get_test_loc('copyrights/json_phps_html-JSON_phps_html.html')
        expected = [
            'copyright 2005 Michal Migurski',
        ]
        check_detection(expected, test_file)

    def test_jsp_all_CAPS(self):
        test_file = self.get_test_loc('copyrights/jsp_all_CAPS-jsp.jsp')
        expected = [
            'copyright 2005-2006 Cedrik LIME',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_kaboom(self):
        test_file = self.get_test_loc('copyrights/kaboom-kaboom.copyright')
        expected = [
            'Copyright (c) 2009 Sune Vuorela <sune@vuorela.dk>',
            'Copyright (c) 2007-2009 George Kiagiadakis <gkiagiad@csd.uoc.gr>',
            'Copyright (c) 2009 Modestas Vainius <modestas@vainius.eu>',
            'Copyright (c) 2009, Debian Qt/KDE Maintainers <debian-qt-kde@lists.debian.org>',
        ]
        check_detection(expected, test_file)

    def test_kbuild(self):
        test_file = self.get_test_loc('copyrights/kbuild-kbuild.copyright')
        expected = [
            'Copyright (c) 2005-2009 Knut St. Osmundsen <bird-kBuild-spam@anduin.net>',
            'Copyright (c) 1991-1993 The Regents of the University of California',
            'Copyright (c) 1988-2009 Free Software Foundation, Inc.',
            'Copyright (c) 2003 Free Software Foundation, Inc.',
            'Copyright (c) 2007-2009 Torsten Werner <twerner@debian.org>',
            '(c) 2009 Daniel Baumann <daniel@debian.org>',
        ]
        check_detection(expected, test_file)

    def test_kde_l10n_zhcn(self):
        test_file = self.get_test_loc('copyrights/kde_l10n_zhcn-kde_l_n_zhcn.copyright')
        expected = [
            'Copyright (c) 1996-2009 The KDE Translation teams <kde-i18n-doc@kde.org>',
            '(c) 2007-2009, Debian Qt/KDE Maintainers',
        ]
        check_detection(expected, test_file)

    def test_leonardo_c(self):
        test_file = self.get_test_loc('copyrights/leonardo_c-c.c')
        expected = [
            'Copyright (c) 1994 by Leonardo DaVinci Societe',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_libadns1(self):
        test_file = self.get_test_loc('copyrights/libadns1-libadns.copyright')
        expected = [
            'Copyright 1997-2000 Ian Jackson',
            'Copyright 1999 Tony Finch',
            'Copyright (c) 1991 Massachusetts Institute of Technology',
        ]
        check_detection(expected, test_file)

    def test_libc6_i686(self):
        test_file = self.get_test_loc('copyrights/libc6_i686-libc_i.copyright')
        expected = [
            'Copyright (c) 1991,92,93,94,95,96,97,98,99,2000,2001,2002,2003,2004,2005, 2006,2007,2008 Free Software Foundation, Inc.',
            'Copyright (c) 1991,92,93,94,95,96,97,98,99,2000,2001,2002,2003,2004,2005, 2006,2007,2008 Free Software Foundation, Inc.',
            'Copyright (c) 1991 Regents of the University of California',
            'Portions Copyright (c) 1993 by Digital Equipment Corporation',
            'Copyright (c) 1984, Sun Microsystems, Inc.',
            'Copyright (c) 1991,1990,1989 Carnegie Mellon University',
            'Copyright (c) 2000, Intel Corporation',
            'copyright (c) by Craig Metz',
        ]
        check_detection(expected, test_file)

    def test_libcdio10(self):
        test_file = self.get_test_loc('copyrights/libcdio10-libcdio.label')
        expected = [
            'Copyright (c) 1999, 2002, 2003, 2004, 2005, 2006, 2007, 2008 Rocky Bernstein <rocky@gnu.org>',
            'Copyright (c) 2000, 2001, 2003, 2004, 2005, 2008 Herbert Valerio Riedel',
            'Copyright (c) 1996, 1997, 1998 Gerd Knorr <kraxel@bytesex.org>',
            'Copyright (c) 2001 Xiph.org',
            'Copyright (c) 1994, 1995, 1996, 1997, 1998, 2001 Heiko Eifeldt <heiko@escape.colossus.de>',
            'Copyright (c) 1998, 1999, 2001 Monty',
            'Copyright (c) 2008 Robert W. Fuller <hydrologiccycle@gmail.com>',
            'Copyright (c) 2006, 2008 Burkhard Plaum <plaum@ipf.uni-stuttgart.de>',
            'Copyright (c) 2001, 2002 Ben Fennema <bfennema@falcon.csc.calpoly.edu>',
            'Copyright (c) 2001, 2002 Scott Long <scottl@freebsd.org>',
            'Copyright (c) 1993 Yggdrasil Computing, Incorporated',
            'Copyright (c) 1999, 2000 J. Schilling',
            'Copyright (c) 2001 Sven Ottemann <ac-logic@freenet.de>',
            'Copyright (c) 2003 Svend Sanjay Sorensen <ssorensen@fastmail.fm>',
            'Copyright (c) 1985, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1996, 1997, 1998, 1999, 2000 Free Software Foundation, Inc.',
            'Copyright (c) 2003 Matthias Drochner',
            'Copyright (c) 1998-2001 VideoLAN Johan Bilien <jobi@via.ecp.fr> and Gildas Bazin <gbazin@netcourrier.com>',
            'Copyright (c) 1992, 1993 Eric Youngdale',
            'Copyright (c) 2003, 2004, 2005, 2006, 2007, 2008 Rocky Bernstein and Herbert Valerio Riedel',
        ]
        check_detection(expected, test_file)

    def test_libcelt0(self):
        test_file = self.get_test_loc('copyrights/libcelt0-libcelt.copyright')
        expected = [
            'Copyright 2005-2007 Christopher Montgomery , Jean-Marc Valin , Timothy Terriberry',
            '(c) 2008, Ron',
        ]
        check_detection(expected, test_file)

    def test_libcompress_raw_zlib_perl(self):
        test_file = self.get_test_loc('copyrights/libcompress_raw_zlib_perl-libcompress_raw_zlib_perl.copyright')
        expected = [
            'Copyright 2005-2009, Paul Marquess <pmqs@cpan.org>',
            'Copyright 1995-2005, Jean-loup Gailly <jloup@gzip.org>',
            'Copyright 1995-2005, Mark Adler <madler@alumni.caltech.edu>',
            'Copyright 2004-2009, Marcus Holland-Moritz <mhx-cpan@gmx.net> 2001, Paul Marquess <pmqs@cpan.org>',
            'Copyright 2007-2009, Krzysztof Krzyzaniak <eloy@debian.org>',
        ]
        check_detection(expected, test_file)

    def test_libcpufreq0(self):
        test_file = self.get_test_loc('copyrights/libcpufreq0-libcpufreq.copyright')
        expected = [
            'Copyright 2004-2006 Dominik Brodowski',
        ]
        check_detection(expected, test_file)

    def test_libcrypt_ssleay_perl(self):
        test_file = self.get_test_loc('copyrights/libcrypt_ssleay_perl-libcrypt_ssleay_perl.copyright')
        expected = [
            'Copyright (c) 1999-2003 Joshua Chamas',
            'Copyright (c) 1998 Gisle Aas',
            'copyright (c) 2003 Stephen Zander <gibreel@debian.org>',
        ]
        check_detection(expected, test_file)

    def test_libepc_ui_1_0_1(self):
        test_file = self.get_test_loc('copyrights/libepc_ui_1_0_1-libepc_ui.copyright')
        expected = [
            'Copyright (c) 2007, 2008 Openismus GmbH',
        ]
        check_detection(expected, test_file)

    def test_libepc_ui_1_0_2(self):
        test_file = self.get_test_loc('copyrights/libepc_ui_1_0_2-libepc_ui.label')
        expected = [
            'Copyright (c) 2007, 2008 Openismus GmbH',
        ]
        check_detection(expected, test_file)

    def test_libfltk1_1(self):
        test_file = self.get_test_loc('copyrights/libfltk1_1-libfltk.copyright')
        expected = [
            'Copyright (c) 1998-2009 Bill Spitzak spitzak@users.sourceforge.net',
        ]
        check_detection(expected, test_file)

    def test_libgail18(self):
        test_file = self.get_test_loc('copyrights/libgail18-libgail.label')
        expected = []
        check_detection(expected, test_file)

    def test_libggiwmh0_target_x(self):
        test_file = self.get_test_loc('copyrights/libggiwmh0_target_x-libggiwmh_target_x.copyright')
        expected = [
            'Copyright (c) 2005 Eric Faurot eric.faurot@gmail.com',
            'Copyright (c) 2004 Peter Ekberg peda@lysator.liu.se',
            'Copyright (c) 2004 Christoph Egger',
            'Copyright (c) 1999 Marcus Sundberg marcus@ggi-project.org',
            'Copyright (c) 1998, 1999 Andreas Beck becka@ggi-project.org',
            'Copyright (c) 2008 Bradley Smith <brad@brad-smith.co.uk>',
        ]
        check_detection(expected, test_file)

    def test_libgnome_desktop_2(self):
        test_file = self.get_test_loc('copyrights/libgnome_desktop_2-libgnome_desktop.copyright')
        expected = [
            'Copyright (c) 1999, 2000 Red Hat Inc.',
            'Copyright (c) 2001 Sid Vicious',
            'Copyright (c) 1999 Free Software Foundation',
            'Copyright (c) 2002, Sun Microsystems, Inc.',
            'Copyright (c) 2003, Kristian Rietveld',
        ]
        check_detection(expected, test_file)

    def test_libgnome_media0(self):
        test_file = self.get_test_loc('copyrights/libgnome_media0-libgnome_media.copyright')
        expected = []
        check_detection(expected, test_file)

    def test_libgoffice_0_8(self):
        test_file = self.get_test_loc('copyrights/libgoffice_0_8-libgoffice.label')
        expected = [
            'Copyright (c) 2003-2008 Jody Goldberg (jody@gnome.org) and others.',
        ]
        check_detection(expected, test_file)

    def test_libgtkhtml2_0(self):
        test_file = self.get_test_loc('copyrights/libgtkhtml2_0-libgtkhtml.copyright')
        expected = [
            'Copyright 1999,2000,2001 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_libisc44(self):
        test_file = self.get_test_loc('copyrights/libisc44-libisc.copyright')
        expected = [
            'Copyright (c) 1996-2001 Internet Software Consortium.',
        ]
        check_detection(expected, test_file)

    def test_libisccfg30(self):
        test_file = self.get_test_loc('copyrights/libisccfg30-libisccfg.copyright')
        expected = [
            'Copyright (c) 1996-2001 Internet Software Consortium',
        ]
        check_detection(expected, test_file)

    def test_libisccfg40(self):
        test_file = self.get_test_loc('copyrights/libisccfg40-libisccfg.copyright')
        expected = [
            'Copyright (c) 1996-2001 Internet Software Consortium',
        ]
        check_detection(expected, test_file)

    def test_libjpeg62(self):
        test_file = self.get_test_loc('copyrights/libjpeg62-libjpeg.copyright')
        expected = [
            'copyright (c) 1991-1998, Thomas G. Lane',
            'copyright by the Free Software Foundation',
        ]
        check_detection(expected, test_file)

    def test_libkeyutils1(self):
        test_file = self.get_test_loc('copyrights/libkeyutils1-libkeyutils.label')
        expected = [
            'Copyright (c) 2005 Red Hat',
            'Copyright (c) 2005 Red Hat',
            'Copyright (c) 2006-2009 Daniel Baumann <daniel@debian.org>',
        ]
        check_detection(expected, test_file)

    def test_liblocale_gettext_perl(self):
        test_file = self.get_test_loc('copyrights/liblocale_gettext_perl-liblocale_get_perl.label')
        expected = [
            'Copyright 1996..2005 by Phillip Vandry <vandry@TZoNE.ORG>',
        ]
        check_detection(expected, test_file)

    def test_libopenraw1(self):
        test_file = self.get_test_loc('copyrights/libopenraw1-libopenraw.label')
        expected = [
            'Copyright (c) 2007, David Paleino <d.paleino@gmail.com>',
            'Copyright (c) 2005-2009, Hubert Figuiere <hub@figuiere.net>',
            'Copyright (c) 2006, Hubert Figuiere <hub@figuiere.net>',
            '(c) 2001, Lutz Muller <lutz@users.sourceforge.net>',
            'Copyright (c) 2007, Hubert Figuiere <hub@figuiere.net>',
            '(c) 1994, Kongji Huang and Brian C. Smith , Cornell University',
            '(c) 1993, Brian C. Smith , The Regents of the University of California',
            "(c) 1991-1992, Thomas G. Lane , Part of the Independent JPEG Group's",
            'Copyright (c) 2005, Hubert Figuiere <hub@figuiere.net>',
            'Copyright (c) 2007, Hubert Figuiere <hub@figuiere.net>',
        ]
        check_detection(expected, test_file)

    def test_libopenthreads12(self):
        test_file = self.get_test_loc('copyrights/libopenthreads12-libopenthreads.copyright')
        expected = [
            'Copyright (c) 2002 Robert Osfield',
            'Copyright (c) 1998 Julian Smart , Robert Roebling',
        ]
        check_detection(expected, test_file)

    def test_libpam_ck_connector(self):
        test_file = self.get_test_loc('copyrights/libpam_ck_connector-libpam_ck_connector.copyright')
        expected = [
            'Copyright (c) 2006 William Jon McCann <mccann@jhu.edu>',
            'Copyright (c) 2007 David Zeuthen <davidz@redhat.com>',
            'Copyright (c) 2007 William Jon McCann <mccann@jhu.edu>',
            '(c) 2007, Michael Biebl <biebl@debian.org>',
        ]
        check_detection(expected, test_file)

    def test_libpoppler3(self):
        test_file = self.get_test_loc('copyrights/libpoppler3-libpoppler.copyright')
        expected = [
            'Copyright (c) 1996-2003 Glyph & Cog, LLC',
        ]
        check_detection(expected, test_file)

    def test_libqt4_scripttools(self):
        test_file = self.get_test_loc('copyrights/libqt4_scripttools-libqt_scripttools.copyright')
        expected = [
            '(c) 2008-2009 Nokia Corporation and/or its subsidiary(-ies)',
            '(c) 1994-2008 Trolltech ASA',
        ]
        check_detection(expected, test_file)

    def test_libqtscript4_gui(self):
        test_file = self.get_test_loc('copyrights/libqtscript4_gui-libqtscript_gui.copyright')
        expected = [
            'Copyright (c) 2009 Modestas Vainius <modestas@vainius.eu>',
            'Copyright (c) Trolltech ASA',
            'Copyright (c) Roberto Raggi <roberto@kdevelop.org>',
            'Copyright (c) Harald Fernengel <harry@kdevelop.org>',
        ]
        check_detection(expected, test_file)

    def test_libsocks4(self):
        test_file = self.get_test_loc('copyrights/libsocks4-libsocks.copyright')
        expected = [
            'Copyright (c) 1989 Regents of the University of California.',
            'Portions Copyright (c) 1993, 1994, 1995 by NEC Systems Laboratory',
        ]
        check_detection(expected, test_file)

    def test_libsox_fmt_alsa(self):
        test_file = self.get_test_loc('copyrights/libsox_fmt_alsa-libsox_fmt_alsa.copyright')
        expected = [
            'Copyright 1991 Lance Norskog And Sundry Contributors',
        ]
        check_detection(expected, test_file)

    def test_libspeex1(self):
        test_file = self.get_test_loc('copyrights/libspeex1-libspeex.copyright')
        expected = [
            'Copyright 2002-2007 Xiph.org Foundation',
            'Copyright 2002-2007 Jean-Marc Valin',
            'Copyright 2005-2007 Analog Devices Inc.',
            'Copyright 2005-2007 Commonwealth Scientific and Industrial Research Organisation (CSIRO)',
            'Copyright 1993, 2002, 2006 David Rowe',
            'Copyright 2003 EpicGames',
            'Copyright 1992-1994 Jutta Degener , Carsten Bormann',
        ]
        check_detection(expected, test_file)

    def test_libstlport4_6ldbl(self):
        test_file = self.get_test_loc('copyrights/libstlport4_6ldbl-libstlport_ldbl.label')
        expected = [
            'Copyright (c) 1994 Hewlett-Packard Company',
            'Copyright (c) 1996-1999 Silicon Graphics Computer Systems, Inc.',
            'Copyright (c) 1997 Moscow Center for SPARC Technology',
            'Copyright (c) 1999, 2000, 2001 Boris Fomitchev',
        ]
        check_detection(expected, test_file)

    def test_libtdb1(self):
        test_file = self.get_test_loc('copyrights/libtdb1-libtdb.copyright')
        expected = [
            'Copyright (c) Andrew Tridgell 1999-2004',
            'Copyright (c) Paul Rusty Russell 2000',
            'Copyright (c) Jeremy Allison 2000-2003',
        ]
        check_detection(expected, test_file)

    def test_libuim6(self):
        test_file = self.get_test_loc('copyrights/libuim6-libuim.copyright')
        expected = [
            'Copyright (c) 2003-2007 uim Project http://uim.freedesktop.org/',
            'COPYRIGHT (c) 1988-1994 BY PARADIGM ASSOCIATES INCORPORATED',
            'Copyright (c) 2006, SHIMODA Hiroshi <piro@p.club.ne.jp>',
            'Copyright (c) 2006, FUJITA Yuji <yuji@webmasters.gr.jp>',
            'Copyright (c) 2006, Jun Mukai <mukai@jmuk.org>',
            'Copyright (c) 2006, Teppei Tamra <tam-t@par.odn.ne.jp>',
            'Copyright (c) 2005 UTUMI Hirosi <utuhiro78@yahoo.co.jp>',
            'Copyright (c) 2006 YAMAMOTO Kengo <yamaken@bp.iij4u.or.jp>',
            'Copyright (c) 2006 Jae-hyeon Park <jhyeon@gmail.com>',
            'Copyright (c) 2006 Etsushi Kato <ek.kato@gmail.com>',
        ]
        check_detection(expected, test_file)

    def test_libxext6(self):
        test_file = self.get_test_loc('copyrights/libxext6-libxext.copyright')
        expected = [
            'Copyright 1986, 1987, 1988, 1989, 1994, 1998 The Open Group',
            'Copyright (c) 1996 Digital Equipment Corporation, Maynard, Massachusetts',
            'Copyright (c) 1997 by Silicon Graphics Computer Systems, Inc.',
            'Copyright 1992 Network Computing Devices',
            'Copyright 1991,1993 by Digital Equipment Corporation, Maynard, Massachusetts , and Olivetti Research Limited, Cambridge, England.',
            'Copyright 1986, 1987, 1988 by Hewlett-Packard Corporation',
            'Copyright (c) 1994, 1995 Hewlett-Packard Company',
            'Copyright Digital Equipment Corporation',
            'Copyright 1999, 2005, 2006 Sun Microsystems, Inc.',
        ]
        check_detection(expected, test_file)

    def test_libxmlrpc_c3(self):
        test_file = self.get_test_loc('copyrights/libxmlrpc_c3-libxmlrpc_c.copyright')
        expected = [
            'Copyright (c) 2001 by First Peer, Inc.',
            'Copyright (c) 2001 by Eric Kidd.',
            'Copyright (c) 1998, 1999, 2000 Thai Open Source Software Center Ltd',
            'Copyright (c) 2000 by Moez Mahfoudh <mmoez@bigfoot.com>',
            'Copyright 1991, 1992, 1993, 1994 by Stichting Mathematisch Centrum, Amsterdam',
        ]
        check_detection(expected, test_file)

    def test_libxt6(self):
        test_file = self.get_test_loc('copyrights/libxt6-libxt.label')
        expected = [
            'Copyright 1987, 1988 by Digital Equipment Corporation , Maynard, Massachusetts',
            'Copyright 1993 by Sun Microsystems, Inc. Mountain View',
            'Copyright 1985, 1986, 1987, 1988, 1989, 1994, 1998, 2001 The Open Group',
            '(c) COPYRIGHT International Business Machines Corp. 1992,1997',
        ]
        check_detection(expected, test_file)

    @expectedFailure
    def test_license_qpl_v1_0_perfect(self):
        test_file = self.get_test_loc('copyrights/license_qpl_v1_0_perfect-QPL_v.0')
        expected = [
            'Copyright (c) 1999 Trolltech AS, Norway.',
        ]
        check_detection(expected, test_file)

    def test_adaptive_v1_0(self):
        test_file = self.get_test_loc('copyrights/adaptive_v1_0-Adaptive v.0')
        expected = [
            '(c) Any Recipient',
            '(c) Each Recipient',
        ]
        check_detection(expected, test_file)

    def test_adobe(self):
        test_file = self.get_test_loc('copyrights/adobe-Adobe')
        expected = [
            'Copyright (c) 2006 Adobe Systems Incorporated.',
        ]
        check_detection(expected, test_file)

    def test_adobeflex2sdk(self):
        test_file = self.get_test_loc('copyrights/adobeflex2sdk-Adobeflex_sdk')
        expected = [
            '(c) Adobe AIR',
            '(c) Material Improvement',
        ]
        check_detection(expected, test_file)

    def test_afferogplv1(self):
        test_file = self.get_test_loc('copyrights/afferogplv1-AfferoGPLv')
        expected = [
            'Copyright (c) 2002 Affero Inc.',
            'copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            'copyrighted by Affero, Inc.',
        ]
        check_detection(expected, test_file)

    def test_afferogplv2(self):
        test_file = self.get_test_loc('copyrights/afferogplv2-AfferoGPLv')
        expected = [
            'Copyright (c) 2007 Affero Inc.',
        ]
        check_detection(expected, test_file)

    def test_afferogplv3(self):
        test_file = self.get_test_loc('copyrights/afferogplv3-AfferoGPLv')
        expected = [
            'Copyright (c) 2007 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_afl_v3_0(self):
        test_file = self.get_test_loc('copyrights/afl_v3_0-AFL_v.0')
        expected = [
            'Copyright (c) 2005 Lawrence Rosen.',
        ]
        check_detection(expected, test_file)

    def test_aladdin_free_public_license(self):
        test_file = self.get_test_loc('copyrights/aladdin_free_public_license-Aladdin Free Public License')
        expected = [
            'Copyright (c) 1994, 1995, 1997, 1998, 1999, 2000 Aladdin Enterprises, Menlo Park, California, U.S.A.',
        ]
        check_detection(expected, test_file)

    def test_amazondsb(self):
        test_file = self.get_test_loc('copyrights/amazondsb-AmazonDSb')
        expected = [
            '(c) 2006 Amazon Digital Services, Inc.',
        ]
        check_detection(expected, test_file)

    def test_ampasbsd(self):
        test_file = self.get_test_loc('copyrights/ampasbsd-AMPASBSD')
        expected = [
            'Copyright (c) 2006 Academy of Motion Picture Arts and Sciences',
        ]
        check_detection(expected, test_file)

    def test_apachev1_0(self):
        test_file = self.get_test_loc('copyrights/apachev1_0-Apachev.0')
        expected = [
            'Copyright (c) 1995-1999 The Apache Group.',
        ]
        check_detection(expected, test_file)

    def test_apachev1_1(self):
        test_file = self.get_test_loc('copyrights/apachev1_1-Apachev.1')
        expected = [
            'Copyright (c) 2000 The Apache Software Foundation.',
        ]
        check_detection(expected, test_file)

    def test_apachev2_0b(self):
        test_file = self.get_test_loc('copyrights/apachev2_0b-Apachev_b.0b')
        expected = [
            'Copyright 2000',
        ]
        check_detection(expected, test_file)

    def test_apple_common_documentation_license_v1_0(self):
        test_file = self.get_test_loc('copyrights/apple_common_documentation_license_v1_0-Apple Common Documentation License v.0')
        expected = [
            'Copyright (c) 2001 Apple Computer, Inc.',
        ]
        check_detection(expected, test_file)

    def test_apple_public_source_license_v1_0(self):
        test_file = self.get_test_loc('copyrights/apple_public_source_license_v1_0-Apple Public Source License v.0')
        expected = [
            'Portions Copyright (c) 1999 Apple Computer, Inc.',
        ]
        check_detection(expected, test_file)

    def test_apple_public_source_license_v1_1(self):
        test_file = self.get_test_loc('copyrights/apple_public_source_license_v1_1-Apple Public Source License v.1')
        expected = [
            'Portions Copyright (c) 1999-2000 Apple Computer, Inc.',
        ]
        check_detection(expected, test_file)

    def test_apple_public_source_license_v1_2(self):
        test_file = self.get_test_loc('copyrights/apple_public_source_license_v1_2-Apple Public Source License v.2')
        expected = [
            'Portions Copyright (c) 1999-2003 Apple Computer, Inc.',
        ]
        check_detection(expected, test_file)

    def test_apslv2_0(self):
        test_file = self.get_test_loc('copyrights/apslv2_0-APSLv.0')
        expected = [
            'Portions Copyright (c) 1999-2007 Apple Inc.',
        ]
        check_detection(expected, test_file)

    def test_artistic_v1_0(self):
        test_file = self.get_test_loc('copyrights/artistic_v1_0-Artistic v.0')
        expected = []
        check_detection(expected, test_file)

    def test_artistic_v1_0_short(self):
        test_file = self.get_test_loc('copyrights/artistic_v1_0_short-Artistic v_ short.0 short')
        expected = []
        check_detection(expected, test_file)

    def test_artistic_v2_0beta4(self):
        test_file = self.get_test_loc('copyrights/artistic_v2_0beta4-Artistic v_beta.0beta4')
        expected = [
            'Copyright (c) 2000, Larry Wall.',
        ]
        check_detection(expected, test_file)

    def test_artisticv2_0(self):
        test_file = self.get_test_loc('copyrights/artisticv2_0-Artisticv.0')
        expected = [
            'Copyright (c) 2000-2006, The Perl Foundation.',
        ]
        check_detection(expected, test_file)

    def test_attributionassurancelicense(self):
        test_file = self.get_test_loc('copyrights/attributionassurancelicense-AttributionAssuranceLicense')
        expected = [
            'Copyright (c) 2002 by AUTHOR',
        ]
        check_detection(expected, test_file)

    def test_bigelow_holmes(self):
        test_file = self.get_test_loc('copyrights/bigelow_holmes-Bigelow&Holmes')
        expected = [
            '(c) Copyright 1989 Sun Microsystems, Inc.',
            '(c) Copyright Bigelow & Holmes 1986, 1985.',
        ]
        check_detection(expected, test_file)

    def test_bitstream(self):
        test_file = self.get_test_loc('copyrights/bitstream-Bi_ream')
        expected = [
            'Copyright (c) 2003 by Bitstream, Inc.',
        ]
        check_detection(expected, test_file)

    def test_bsdnrl(self):
        test_file = self.get_test_loc('copyrights/bsdnrl-BSDNRL')
        expected = [
            'copyright by The Regents of the University of California.',
        ]
        check_detection(expected, test_file)

    def test_cnri(self):
        test_file = self.get_test_loc('copyrights/cnri-CNRI')
        expected = [
            'Copyright (c) 1995-2000 Corporation for National Research Initiatives',
        ]
        check_detection(expected, test_file)

    def test_condor_extra_For(self):
        test_file = self.get_test_loc('copyrights/condor_extra_For-Condor')
        expected = [
            'Copyright 1990-2006 Condor Team, Computer Sciences Department, University of Wisconsin-Madison, Madison',
        ]
        check_detection(expected, test_file)

    @expectedFailure
    def test_doc(self):
        test_file = self.get_test_loc('copyrights/doc-DOC')
        expected = [
            'copyrighted by Douglas C. Schmidt and his research group at Washington University, University of California, Irvine, and Vanderbilt University',
            'Copyright (c) 1993-2008'
        ]
        check_detection(expected, test_file)

    def test_dual_mpl_gpl(self):
        test_file = self.get_test_loc('copyrights/dual_mpl_gpl-Dual MPL GPL')
        expected = [
            'Copyright (c) 2002 the Initial Developer.',
        ]
        check_detection(expected, test_file)

    def test_dualmpl_mit(self):
        test_file = self.get_test_loc('copyrights/dualmpl_mit-DualMPL_MIT')
        expected = [
            'Copyright (c) 1998-2001, Daniel Stenberg, <daniel@haxx.se>',
        ]
        check_detection(expected, test_file)

    def test_eclv1_0(self):
        test_file = self.get_test_loc('copyrights/eclv1_0-ECLv.0')
        expected = [
            'Copyright (c) YeAr Name',
        ]
        check_detection(expected, test_file)

    def test_ecosv2_0(self):
        test_file = self.get_test_loc('copyrights/ecosv2_0-eCosv.0')
        expected = [
            'Copyright (c) 1998, 1999, 2000, 2001, 2002 Red Hat, Inc.',
        ]
        check_detection(expected, test_file)

    def test_entessa(self):
        test_file = self.get_test_loc('copyrights/entessa-Entessa')
        expected = [
            'Copyright (c) 2003 Entessa, LLC.',
        ]
        check_detection(expected, test_file)

    def test_eplv1_0b(self):
        test_file = self.get_test_loc('copyrights/eplv1_0b-EPLv_b.0b')
        expected = [
            'Copyright (c) 2003, 2005 IBM Corporation and others.',
        ]
        check_detection(expected, test_file)

    def test_eudatagrid(self):
        test_file = self.get_test_loc('copyrights/eudatagrid-EUDatagrid')
        expected = [
            'Copyright (c) 2001 EU DataGrid.',
        ]
        check_detection(expected, test_file)

    def test_eurosym_v2(self):
        test_file = self.get_test_loc('copyrights/eurosym_v2-Eurosym_v.v2')
        expected = [
            'Copyright (c) 1999-2002 Henrik Theiling',
        ]
        check_detection(expected, test_file)

    def test_frameworxv1_0(self):
        test_file = self.get_test_loc('copyrights/frameworxv1_0-Frameworxv.0')
        expected = [
            '(c) Source Code',
            '(c) THE FRAMEWORX COMPANY 2003',
        ]
        check_detection(expected, test_file)

    def test_freebsd(self):
        test_file = self.get_test_loc('copyrights/freebsd-FreeBSD')
        expected = [
            'Copyright 1994-2006 The FreeBSD Project.',
        ]
        check_detection(expected, test_file)

    def test_freetype(self):
        test_file = self.get_test_loc('copyrights/freetype-FreeType')
        expected = [
            'Copyright 1996-2002, 2006 by David Turner, Robert Wilhelm, and Werner Lemberg',
            'copyright (c) The FreeType Project (www.freetype.org).',
            'copyright (c) 1996-2000 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, test_file)

    def test_gfdlv1_2(self):
        test_file = self.get_test_loc('copyrights/gfdlv1_2-GFDLv.2')
        expected = [
            'Copyright (c) 2000,2001,2002 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_gfdlv1_3(self):
        test_file = self.get_test_loc('copyrights/gfdlv1_3-GFDLv.3')
        expected = [
            'Copyright (c) 2000, 2001, 2002, 2007, 2008 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_glide(self):
        test_file = self.get_test_loc('copyrights/glide-Glide')
        expected = [
            'copyright notice (3dfx Interactive, Inc. 1999)',
            'COPYRIGHT 3DFX INTERACTIVE, INC. 1999',
            'COPYRIGHT 3DFX INTERACTIVE, INC. 1999',
        ]
        check_detection(expected, test_file)

    def test_gnuplot(self):
        test_file = self.get_test_loc('copyrights/gnuplot-gnuplot')
        expected = [
            'Copyright 1986 - 1993, 1998, 2004 Thomas Williams, Colin Kelley',
        ]
        check_detection(expected, test_file)

    def test_gpl_v1(self):
        test_file = self.get_test_loc('copyrights/gpl_v1-GPL_v')
        expected = [
            'Copyright (c) 1989 Free Software Foundation, Inc.',
            'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, test_file)

    def test_gpl_v2(self):
        test_file = self.get_test_loc('copyrights/gpl_v2-GPL_v')
        expected = [
            'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, test_file)

    def test_gpl_v3(self):
        test_file = self.get_test_loc('copyrights/gpl_v3-GPL_v')
        expected = [
            'Copyright (c) 2007 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_helix(self):
        test_file = self.get_test_loc('copyrights/helix-Helix')
        expected = [
            'Copyright (c) 1995-2002 RealNetworks, Inc.',
        ]
        check_detection(expected, test_file)

    def test_hewlett_packard(self):
        test_file = self.get_test_loc('copyrights/hewlett_packard-Hewlett_Packard')
        expected = [
            '(c) HEWLETT-PACKARD COMPANY, 2004.',
        ]
        check_detection(expected, test_file)

    def test_ibmpl_v1_0(self):
        test_file = self.get_test_loc('copyrights/ibmpl_v1_0-IBMPL_v.0')
        expected = [
            'Copyright (c) 1996, 1999 International Business Machines Corporation and others.',
        ]
        check_detection(expected, test_file)

    def test_ietf(self):
        test_file = self.get_test_loc('copyrights/ietf-IETF')
        expected = [
            'Copyright (c) The Internet Society (2003).',
        ]
        check_detection(expected, test_file)

    def test_ijg(self):
        test_file = self.get_test_loc('copyrights/ijg-IJG')
        expected = [
            'copyright (c) 1991-1998, Thomas G. Lane.',
            'copyright by the Free Software Foundation',
        ]
        check_detection(expected, test_file)

    def test_imatix(self):
        test_file = self.get_test_loc('copyrights/imatix-iMatix')
        expected = [
            'Copyright 1991-2000 iMatix Corporation.',
            'Copyright 1991-2000 iMatix Corporation',
            'Copyright 1991-2000 iMatix Corporation',
            'Parts copyright (c) 1991-2000 iMatix Corporation.',
            'Copyright 1996-2000 iMatix Corporation',
        ]
        check_detection(expected, test_file)

    def test_imlib2(self):
        test_file = self.get_test_loc('copyrights/imlib2-Imlib')
        expected = [
            'Copyright (c) 2000 Carsten Haitzler',
        ]
        check_detection(expected, test_file)

    def test_intel(self):
        test_file = self.get_test_loc('copyrights/intel-Intel')
        expected = [
            'Copyright (c) 2006, Intel Corporation.',
        ]
        check_detection(expected, test_file)

    def test_jabber(self):
        test_file = self.get_test_loc('copyrights/jabber-Jabber')
        expected = [
            'Copyright (c) 1999-2000 Jabber.com, Inc.',
            'Portions Copyright (c) 1998-1999 Jeremie Miller.',
        ]
        check_detection(expected, test_file)

    def test_jpython(self):
        test_file = self.get_test_loc('copyrights/jpython-JPython')
        expected = [
            'Copyright 1996-1999 Corporation for National Research Initiatives',
        ]
        check_detection(expected, test_file)

    def test_larryrosen(self):
        test_file = self.get_test_loc('copyrights/larryrosen-LarryRosen')
        expected = [
            'Copyright (c) 2002 Lawrence E. Rosen.',
        ]
        check_detection(expected, test_file)

    def test_latex_v1_0(self):
        test_file = self.get_test_loc('copyrights/latex_v1_0-LaTeX_v.0')
        expected = [
            'Copyright 1999 LaTeX3 Project',
            'Copyright 2001 M. Y. Name',
        ]
        check_detection(expected, test_file)

    def test_latex_v1_1(self):
        test_file = self.get_test_loc('copyrights/latex_v1_1-LaTeX_v.1')
        expected = [
            'Copyright 1999 LaTeX3 Project',
            'Copyright 2001 M. Y. Name',
        ]
        check_detection(expected, test_file)

    def test_latex_v1_2(self):
        test_file = self.get_test_loc('copyrights/latex_v1_2-LaTeX_v.2')
        expected = [
            'Copyright 1999 LaTeX3 Project',
            'Copyright 2001 M. Y. Name',
        ]
        check_detection(expected, test_file)

    def test_latex_v1_3a(self):
        test_file = self.get_test_loc('copyrights/latex_v1_3a-LaTeX_v_a.3a')
        expected = [
            'Copyright 1999 2002-04 LaTeX3 Project',
            'Copyright 2003 M. Y. Name',
        ]
        check_detection(expected, test_file)

    def test_latex_v1_3a_ref(self):
        test_file = self.get_test_loc('copyrights/latex_v1_3a_ref-LaTeX_v_a_ref.3a_ref')
        expected = [
            'Copyright 2003 Name',
        ]
        check_detection(expected, test_file)

    def test_latex_v1_3c(self):
        test_file = self.get_test_loc('copyrights/latex_v1_3c-LaTeX_v_c.3c')
        expected = [
            'Copyright 1999 2002-2008 LaTeX3 Project',
            'Copyright 2005 M. Y. Name',
        ]
        check_detection(expected, test_file)

    def test_lgpl_v2_0(self):
        test_file = self.get_test_loc('copyrights/lgpl_v2_0-LGPL_v.0')
        expected = [
            'Copyright (c) 1991 Free Software Foundation, Inc.',
            'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, test_file)

    def test_lgpl_v2_1(self):
        test_file = self.get_test_loc('copyrights/lgpl_v2_1-LGPL_v.1')
        expected = [
            'Copyright (c) 1991, 1999 Free Software Foundation, Inc.',
            'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, test_file)

    def test_lgpl_v3(self):
        test_file = self.get_test_loc('copyrights/lgpl_v3-LGPL_v')
        expected = [
            'Copyright (c) 2007 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_lgpl_wxwindows_library_licence_v3_0_variant(self):
        test_file = self.get_test_loc('copyrights/wxWindows Library .0 variant')
        expected = [
            'Copyright (c) 1998 Julian Smart, Robert Roebling',
        ]
        check_detection(expected, test_file)

    def test_logica_v1_0(self):
        test_file = self.get_test_loc('copyrights/logica_v1_0-Logica_v.0')
        expected = [
            'Copyright (c) 1996-2001 Logica Mobile Networks Limited',
            'Copyright (c) 1996-2001 Logica Mobile Networks Limited',
        ]
        check_detection(expected, test_file)

    def test_luxi_fonts(self):
        test_file = self.get_test_loc('copyrights/luxi_fonts-Luxi_fonts')
        expected = [
            'copyright (c) 2001 by Bigelow & Holmes Inc.',
            'copyright (c) 2001 by URW++ GmbH.',
        ]
        check_detection(expected, test_file)

    def test_maia(self):
        test_file = self.get_test_loc('copyrights/maia-Maia')
        expected = [
            'Copyright 2004 by Robert LeBlanc',
        ]
        check_detection(expected, test_file)

    def test_mit_adobeglyph(self):
        test_file = self.get_test_loc('copyrights/mit_adobeglyph-MIT_AdobeGlyph')
        expected = [
            'Copyright (c) 1997,1998,2002,2007 Adobe Systems Incorporated',
        ]
        check_detection(expected, test_file)

    def test_mit_cmu(self):
        test_file = self.get_test_loc('copyrights/mit_cmu-MIT_CMU')
        expected = [
            'Copyright 1989, 1991, 1992 by Carnegie Mellon University',
            'Copyright 1996, 1998-2000 The Regents of the University of California',
        ]
        check_detection(expected, test_file)

    def test_mit_enna(self):
        test_file = self.get_test_loc('copyrights/mit_enna-MIT_enna')
        expected = [
            'Copyright (c) 2000 Carsten Haitzler',
        ]
        check_detection(expected, test_file)

    def test_mit_hylafax(self):
        test_file = self.get_test_loc('copyrights/mit_hylafax-MIT_hylafax')
        expected = [
            'Copyright (c) 1990-1996 Sam Leffler',
            'Copyright (c) 1991-1996 Silicon Graphics, Inc.',
        ]
        check_detection(expected, test_file)

    def test_mit_icu(self):
        test_file = self.get_test_loc('copyrights/mit_icu-MIT_ICU')
        expected = [
            'Copyright (c) 1995-2006 International Business Machines Corporation and others',
        ]
        check_detection(expected, test_file)

    def test_mit_lucent(self):
        test_file = self.get_test_loc('copyrights/mit_lucent-MIT_Lucent')
        expected = [
            'Copyright (c) 1989-1998 by Lucent Technologies',
        ]
        check_detection(expected, test_file)

    def test_mit_mlton(self):
        test_file = self.get_test_loc('copyrights/mit_mlton-MIT_MLton')
        expected = [
            'Copyright (c) 1999-2006 Henry Cejtin, Matthew Fluet, Suresh Jagannathan, and Stephen Weeks.',
            'Copyright (c) 1997-2000 by the NEC Research',
        ]
        check_detection(expected, test_file)

    def test_mit_oldstyle_disclaimer4(self):
        test_file = self.get_test_loc('copyrights/mit_oldstyle_disclaimer4-MIT_OldStyle_disclaimer')
        expected = [
            'Copyright (c) 2001, 2002, 2003, 2004, 2005 by The Regents of the University of California.',
        ]
        check_detection(expected, test_file)

    def test_mit_unicode(self):
        test_file = self.get_test_loc('copyrights/mit_unicode-MIT_unicode')
        expected = [
            'Copyright (c) 1991-2005 Unicode, Inc.',
        ]
        check_detection(expected, test_file)

    def test_mit_wordnet(self):
        test_file = self.get_test_loc('copyrights/mit_wordnet-MIT_WordNet')
        expected = [
            'Copyright 2006 by Princeton University.',
        ]
        check_detection(expected, test_file)

    def test_mitre(self):
        test_file = self.get_test_loc('copyrights/mitre-MITRE')
        expected = [
            'Copyright (c) 1994-1999. The MITRE Corporation',
        ]
        check_detection(expected, test_file)

    def test_ms_pl(self):
        test_file = self.get_test_loc('copyrights/ms_pl-Ms_PL')
        expected = []
        check_detection(expected, test_file)

    def test_ms_rl(self):
        test_file = self.get_test_loc('copyrights/ms_rl-Ms_RL')
        expected = []
        check_detection(expected, test_file)

    def test_ms_rsl(self):
        test_file = self.get_test_loc('copyrights/ms_rsl-Ms_RSL')
        expected = []
        check_detection(expected, test_file)

    def test_msntp(self):
        test_file = self.get_test_loc('copyrights/msntp-MSNTP')
        expected = [
            '(c) Copyright, University of Cambridge, 1996, 1997, 2000',
            '(c) Copyright University of Cambridge.',
        ]
        check_detection(expected, test_file)

    def test_mysql_gplexception(self):
        test_file = self.get_test_loc('copyrights/mysql_gplexception-MySQL_gplexception')
        expected = []
        check_detection(expected, test_file)

    def test_naumen(self):
        test_file = self.get_test_loc('copyrights/naumen-Naumen')
        expected = [
            'Copyright (c) NAUMEN (tm) and Contributors.',
        ]
        check_detection(expected, test_file)

    def test_netcomponents(self):
        test_file = self.get_test_loc('copyrights/netcomponents-NetComponents')
        expected = [
            'Copyright (c) 1996-1999 Daniel F. Savarese.',
        ]
        check_detection(expected, test_file)

    def test_nethack(self):
        test_file = self.get_test_loc('copyrights/nethack-Nethack')
        expected = [
            'Copyright (c) 1989 M. Stephenson',
            'copyright 1988 Richard M. Stallman',
        ]
        check_detection(expected, test_file)

    def test_nokia(self):
        test_file = self.get_test_loc('copyrights/nokia-Nokia')
        expected = [
            'Copyright (c) Nokia and others.',
        ]
        check_detection(expected, test_file)

    def test_npl_v1_0(self):
        test_file = self.get_test_loc('copyrights/npl_v1_0-NPL_v.0')
        expected = [
            'Copyright (c) 1998 Netscape Communications Corporation.',
        ]
        check_detection(expected, test_file)

    def test_nvidia_source(self):
        test_file = self.get_test_loc('copyrights/nvidia_source-Nvidia_source')
        expected = [
            'Copyright (c) 1996-1998 NVIDIA, Corp.',
            'Copyright (c) 1996-1998 NVIDIA, Corp.',
        ]
        check_detection(expected, test_file)

    def test_oclc_v1_0(self):
        test_file = self.get_test_loc('copyrights/oclc_v1_0-OCLC_v.0')
        expected = [
            'Copyright (c) 2000. OCLC Research.',
            'Copyright (c) 2000- (insert then current year) OCLC OCLC Research and others.',
        ]
        check_detection(expected, test_file)

    def test_oclc_v2_0(self):
        test_file = self.get_test_loc('copyrights/oclc_v2_0-OCLC_v.0')
        expected = [
            'Copyright (c) 2002. OCLC Research.',
            'Copyright (c) 2000- (insert then current year) OCLC Online Computer Library Center, Inc. and other contributors.',
            'Copyright (c) 2000- (insert then current year) OCLC Online Computer Library Center, Inc. and other contributors.',
        ]
        check_detection(expected, test_file)

    def test_openldap(self):
        test_file = self.get_test_loc('copyrights/openldap-OpenLDAP')
        expected = [
            'Copyright 1999-2003 The OpenLDAP Foundation, Redwood City, California',
        ]
        check_detection(expected, test_file)

    def test_openmotif(self):
        test_file = self.get_test_loc('copyrights/openmotif-OpenMotif')
        expected = [
            'Copyright (c) date here, The Open Group Ltd. and others.',
        ]
        check_detection(expected, test_file)

    def test_openpbs(self):
        test_file = self.get_test_loc('copyrights/openpbs-OpenPBS')
        expected = [
            'Copyright (c) 1999-2000 Veridian Information Solutions, Inc.',
        ]
        check_detection(expected, test_file)

    def test_openpublicationref(self):
        test_file = self.get_test_loc('copyrights/openpublicationref-OpenPublicationref')
        expected = [
            'Copyright (c) 2000 by ThisOldHouse.',
        ]
        check_detection(expected, test_file)

    def test_openssl_c(self):
        test_file = self.get_test_loc('copyrights/openssl-c.c')
        expected = [
            'Copyright (c) 1995-1997 Eric Young (eay@mincom.oz.au)',
        ]
        check_detection(expected, test_file)

    def test_openssl(self):
        test_file = self.get_test_loc('copyrights/openssl-OpenSSL')
        expected = [
            'Copyright (c) 1998-2000 The OpenSSL Project.',
        ]
        check_detection(expected, test_file)

    def test_osl_v3_0(self):
        test_file = self.get_test_loc('copyrights/osl_v3_0-OSL_v.0')
        expected = [
            'Copyright (c) 2005 Lawrence Rosen.',
        ]
        check_detection(expected, test_file)

    def test_phorum(self):
        test_file = self.get_test_loc('copyrights/phorum-Phorum')
        expected = [
            'Copyright (c) 2001 The Phorum Development Team.',
        ]
        check_detection(expected, test_file)

    def test_pine(self):
        test_file = self.get_test_loc('copyrights/pine-Pine')
        expected = [
            'Copyright 1989-2007 by the University of Washington.',
        ]
        check_detection(expected, test_file)

    def test_python_v1_6(self):
        test_file = self.get_test_loc('copyrights/python_v1_6-Python_v.6')
        expected = [
            'Copyright (c) 1995-2000 Corporation for National Research Initiatives',
        ]
        check_detection(expected, test_file)

    def test_python_v1_6_1(self):
        test_file = self.get_test_loc('copyrights/python_v1_6_1-Python_v.1')
        expected = [
            'Copyright 1995-2001 Corporation for National Research Initiatives',
        ]
        check_detection(expected, test_file)

    def test_python_v2(self):
        test_file = self.get_test_loc('copyrights/python_v2-Python_v')
        expected = [
            'Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006 Python Software Foundation',
            'Copyright (c) 1995-2001 Corporation for National Research Initiatives',
        ]
        check_detection(expected, test_file)

    def test_qpl_v1_0(self):
        test_file = self.get_test_loc('copyrights/qpl_v1_0-QPL_v.0')
        expected = [
            'Copyright (c) 1999 Trolltech AS',
        ]
        check_detection(expected, test_file)

    def test_realcsl_v2_0(self):
        test_file = self.get_test_loc('copyrights/realcsl_v2_0-RealCSL_v.0')
        expected = []
        check_detection(expected, test_file)

    def test_realpsl_v1_0(self):
        test_file = self.get_test_loc('copyrights/realpsl_v1_0-RealPSL_v.0')
        expected = [
            'Copyright (c) 1995-2002 RealNetworks, Inc.',
        ]
        check_detection(expected, test_file)

    def test_realpsl_v1_0ref(self):
        test_file = self.get_test_loc('copyrights/realpsl_v1_0ref-RealPSL_v_ref.0ref')
        expected = [
            'Copyright (c) 1995-2004 RealNetworks, Inc.',
        ]
        check_detection(expected, test_file)

    def test_reciprocal_v1_5(self):
        test_file = self.get_test_loc('copyrights/reciprocal_v1_5-Reciprocal_v.5')
        expected = [
            'Copyright (c) 2001-2007 Technical Pursuit Inc.',
        ]
        check_detection(expected, test_file)

    def test_redhateula(self):
        test_file = self.get_test_loc('copyrights/redhateula-RedHatEULA')
        expected = []
        check_detection(expected, test_file)

    def test_redhatref(self):
        test_file = self.get_test_loc('copyrights/redhatref-RedHatref')
        expected = [
            'Copyright (c) 2005 Red Hat, Inc.',
            'Copyright (c) 1995-2005 Red Hat, Inc. and others.',
            'copyrighted by Red Hat, Inc.',
        ]
        check_detection(expected, test_file)

    def test_ricoh_v1_0(self):
        test_file = self.get_test_loc('copyrights/ricoh_v1_0-Ricoh_v.0')
        expected = [
            'Ricoh Silicon Valley, Inc. are Copyright (c) 1995-1999.',
        ]
        check_detection(expected, test_file)

    @expectedFailure
    def test_scilab(self):
        test_file = self.get_test_loc('copyrights/scilab-Scilab')
        expected = [
            'Scilab (c) INRIA-ENPC.',
            'Scilab (c) INRIA-ENPC.',
            'Scilab (c) INRIA-ENPC.',
            'Scilab (c) INRIA-ENPC.',
            'Scilab inside (c) INRIA-ENPC',
            'Scilab (c) INRIA-ENPC',
            'Scilab (c) INRIA-ENPC',
        ]
        check_detection(expected, test_file)

    def test_sgi_cid_v1_0(self):
        test_file = self.get_test_loc('copyrights/sgi_cid_v1_0-SGI_CID_v.0')
        expected = [
            'Copyright (c) 1994-1999 Silicon Graphics, Inc.',
            'Copyright (c) 1994-1999 Silicon Graphics, Inc.',
        ]
        check_detection(expected, test_file)

    def test_sgi_glx_v1_0(self):
        test_file = self.get_test_loc('copyrights/sgi_glx_v1_0-SGI_GLX_v.0')
        expected = [
            '(c) 1991-9 Silicon Graphics, Inc.',
        ]
        check_detection(expected, test_file)

    def test_sissl_v1_1refa(self):
        test_file = self.get_test_loc('copyrights/sissl_v1_1refa-SISSL_v_refa.1refa')
        expected = [
            'Copyright 2000 by Sun Microsystems, Inc.',
        ]
        check_detection(expected, test_file)

    def test_sleepycat(self):
        test_file = self.get_test_loc('copyrights/sleepycat-Sleepycat')
        expected = [
            'Copyright (c) 1990-1999 Sleepycat Software.',
        ]
        check_detection(expected, test_file)

    def test_sybaseopenwatcom_v1_0(self):
        test_file = self.get_test_loc('copyrights/sybaseopenwatcom_v1_0-SybaseOpenWatcom_v.0')
        expected = [
            'Portions Copyright (c) 1983-2002 Sybase, Inc.',
        ]
        check_detection(expected, test_file)

    def test_uofu_rfpl(self):
        test_file = self.get_test_loc('copyrights/uofu_rfpl-UofU_RFPL')
        expected = [
            'Copyright (c) 2001, 1998 University of Utah.',
        ]
        check_detection(expected, test_file)

    def test_vovida_v1_0(self):
        test_file = self.get_test_loc('copyrights/vovida_v1_0-Vovida_v.0')
        expected = [
            'Copyright (c) 2000 Vovida Networks, Inc.',
        ]
        check_detection(expected, test_file)

    def test_wtfpl(self):
        test_file = self.get_test_loc('copyrights/wtfpl-WTFPL')
        expected = [
            'Copyright (c) 2004 Sam Hocevar',
        ]
        check_detection(expected, test_file)

    def test_x_net(self):
        test_file = self.get_test_loc('copyrights/x_net-X_Net.Net')
        expected = [
            'Copyright (c) 2000-2001 X.Net, Inc. Lafayette, California',
        ]
        check_detection(expected, test_file)

    def test_zend(self):
        test_file = self.get_test_loc('copyrights/zend-Zend')
        expected = [
            'Copyright (c) 1999-2002 Zend Technologies Ltd.',
        ]
        check_detection(expected, test_file)

    def test_zliback(self):
        test_file = self.get_test_loc('copyrights/zliback-zLibAck')
        expected = [
            'Portions Copyright (c) 2002-2007 Charlie Poole',
            'Copyright (c) 2002-2004 James W. Newkirk, Michael C. Two, Alexei A. Vorontsov',
            'Copyright (c) 2000-2002 Philip A. Craig',
        ]
        check_detection(expected, test_file)

    def test_zope_v1_0(self):
        test_file = self.get_test_loc('copyrights/zope_v1_0-Zope_v.0')
        expected = [
            'Copyright (c) Digital Creations.',
        ]
        check_detection(expected, test_file)

    def test_zope_v2_0(self):
        test_file = self.get_test_loc('copyrights/zope_v2_0-Zope_v.0')
        expected = [
            'Copyright (c) Zope Corporation (tm) and Contributors.',
        ]
        check_detection(expected, test_file)

    def test_linux_source_2_6(self):
        test_file = self.get_test_loc('copyrights/linux_source_2_6-linux_source.copyright')
        expected = [
            'copyrighted by Linus Torvalds and others.',
        ]
        check_detection(expected, test_file)

    def test_loss_of_holder_c(self):
        test_file = self.get_test_loc('copyrights/loss_of_holder_c-c.c')
        expected = [
            'COPYRIGHT (c) DIONYSOS 2006 - 2009',
        ]
        check_detection(expected, test_file)

    def test_matroska_demux1_c(self):
        test_file = self.get_test_loc('copyrights/matroska_demux1_c-matroska_demux_c.c')
        expected = [
            '(c) 2003 Ronald Bultje <rbultje@ronald.bitfreak.net>',
            '(c) 2011 Debarshi Ray <rishi@gnu.org>',
        ]
        check_detection(expected, test_file)

    def test_matroska_demux_c(self):
        test_file = self.get_test_loc('copyrights/matroska_demux_c-matroska_demux_c.c')
        expected = [
            '(c) 2006 Tim-Philipp Muller',
            '(c) 2008 Sebastian Droge <slomo@circular-chaos.org>',
        ]
        check_detection(expected, test_file)

    def test_matroska_demux_muller_c(self):
        test_file = self.get_test_loc('copyrights/matroska_demux_muller_c-matroska_demux_c.c')
        expected = [
            '(c) 2006 Tim-Philipp Muller',
            '(c) 2008 Sebastian Droge <slomo@circular-chaos.org>',
        ]
        check_detection(expected, test_file)

    def test_memcmp_assembly(self):
        test_file = self.get_test_loc('copyrights/memcmp_assembly-9_9_memcmp_S.S')
        expected = [
            'Copyright (c) 2007 ARC International (UK) LTD',
        ]
        check_detection(expected, test_file)

    def test_mergesort_java(self):
        test_file = self.get_test_loc('copyrights/mergesort_java-MergeSort_java.java')
        expected = [
            'Copyright (c) 1998 Sun Microsystems, Inc.',
        ]
        check_detection(expected, test_file)

    def test_michal_txt(self):
        test_file = self.get_test_loc('copyrights/michal_txt.txt')
        expected = [
            'copyright 2005 Michal Migurski',
        ]
        check_detection(expected, test_file)

    def test_mips1_be_elf_hal_o_uu(self):
        test_file = self.get_test_loc('copyrights/mips1_be_elf_hal_o_uu-mips_be_elf_hal_o_uu.uu')
        expected = [
            'Copyright (c) 2002-2006 Sam Leffler, Errno Consulting, Atheros Communications, Inc.',
        ]
        check_detection(expected, test_file)

    def test_missing_statement_file_txt(self):
        test_file = self.get_test_loc('copyrights/missing_statement_file_txt-file.txt')
        expected = [
            'Copyright 2003-2009 The Apache Geronimo development community',
            'Copyright (c) 2000-2005 The Legion Of The Bouncy Castle (http://www.bouncycastle.org)',
        ]
        check_detection(expected, test_file)

    def test_mit(self):
        test_file = self.get_test_loc('copyrights/mit.txt')
        expected = [
            'Copyright 2010-2011 by MitSomething',
        ]
        check_detection(expected, test_file)

    def test_mit_danse(self):
        test_file = self.get_test_loc('copyrights/mit_danse')
        expected = [
            'Copyright (c) 2009 California Institute of Technology.',
        ]
        check_detection(expected, test_file)

    def test_mit_danse_mojibake(self):
        test_file = self.get_test_loc('copyrights/mit_danse-mojibake')
        expected = [
            'Copyright (c) 2009 California Institute of Technology.',
        ]
        check_detection(expected, test_file)

    def test_mixedcaps_c(self):
        test_file = self.get_test_loc('copyrights/mixedcaps_c-mixedcaps_c.c')
        expected = [
            'COPYRIGHT (c) 2006 MyCompany2 MYCOP',
            'copyright (c) 2006 MyCompany2 MYCOP',
            'COPYRIGHT (c) 2006 MYCOP MyCompany3',
            'copyright (c) 2006 MYCOP MyCompany3',
            'Copyright (c) 1993-95 NEC Systems Laboratory',
            'COPYRIGHT (c) 1988-1994 PARADIGM BY CAMBRIDGE asSOCIATES INCORPORATED',
            'Copyright (c) 2006, SHIMODA Hiroshi',
            'Copyright (c) 2006, FUJITA Yuji',
            'Copyright (c) 2007 GNOME i18n Project',
            'Copyright 1996-2007 Glyph & Cog, LLC.',
            'Copyright (c) 2002 Juan Carlos Arevalo-Baeza',
            'Copyright (c) 2000 INRIA, France Telecom',
            'Copyright (c) NEC Systems Laboratory 1993',
            'Copyright (c) 1984 NEC Systems Laboratory',
            'Copyright (c) 1996-2003 Glyph & Cog, LLC',
            'Copyright (c) 1996. Zeus Technology Limited',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_mixedcase_company_name_in_c(self):
        test_file = self.get_test_loc('copyrights/mixedcase_company_name_in_c-lowercase_company_c.c')
        expected = [
            'Copyright (c) 2001 nexB',
        ]
        check_detection(expected, test_file)

    def test_mkisofs(self):
        test_file = self.get_test_loc('copyrights/mkisofs-mkisofs.copyright')
        expected = [
            'Copyright 1998-2003 Heiko Eissfeldt',
            '(c) Peter Widow',
            '(c) Thomas Niederreiter',
            '(c) RSA Data Security, Inc.',
            'Copyright 1993 Yggdrasil Computing, Incorporated',
            'Copyright (c) 1999,2000-2004 J. Schilling',
            '(c) 1998-2002 by Heiko Eissfeldt, heiko@colossus.escape.de',
            '(c) 2002 by Joerg Schilling',
            '(c) 1996, 1997 Robert Leslie',
            'Copyright (c) 2002 J. Schilling',
            'Copyright (c) 1987, 1995-2003 J. Schilling',
            'Copyright 2001 H. Peter Anvin',
        ]
        check_detection(expected, test_file)

    def test_moto_broad(self):
        test_file = self.get_test_loc('copyrights/moto_broad-c.c')
        expected = [
            'COPYRIGHT (c) 2005 MOTOROLA, BROADBAND COMMUNICATIONS SECTOR',
        ]
        check_detection(expected, test_file)

    def test_motorola_c(self):
        test_file = self.get_test_loc('copyrights/motorola_c-c.c')
        expected = [
            'Copyright (c) 2003, 2010 Motorola, Inc.',
        ]
        check_detection(expected, test_file)

    def test_motorola_mobility_c(self):
        test_file = self.get_test_loc('copyrights/motorola_mobility_c-c.c')
        expected = [
            'Copyright (c) 2009 Motorola, Inc.',
            'Copyright (c) 2011 Motorola Mobility, Inc.',
        ]
        check_detection(expected, test_file)

    def test_mplayer_skin_blue(self):
        test_file = self.get_test_loc('copyrights/mplayer_skin_blue-mplayer_skin_blue.copyright')
        expected = [
            'Copyright (c) 2005-06 Franciszek Wilamowski, xenomorph@irc.pl',
        ]
        check_detection(expected, test_file)

    def test_muller(self):
        test_file = self.get_test_loc('copyrights/muller-c.c')
        expected = [
            '(c) 2003 Ronald Bultje <rbultje@ronald.bitfreak.net>',
            '(c) 2006 Tim-Philipp Muller',
            '(c) 2008 Sebastian Droge <slomo@circular-chaos.org>',
            '(c) 2011 Debarshi Ray <rishi@gnu.org>',
        ]
        check_detection(expected, test_file)

    def test_multiline(self):
        test_file = self.get_test_loc('copyrights/multiline-Historical.txt')
        expected = [
            'COPYRIGHT (c) 1990-1994 BY GEORGE J. CARRETTE, CONCORD, MASSACHUSETTS.',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_multiline_george(self):
        test_file = self.get_test_loc('copyrights/multiline_george-Historical.txt')
        expected = [
            'COPYRIGHT (c) 1990-1994 BY GEORGE',
        ]
        check_detection(expected, test_file)

    def test_mycorp_c(self):
        test_file = self.get_test_loc('copyrights/mycorp_c-c.c')
        expected = [
            'Copyright (c) 2012 MyCorp Inc.',
        ]
        check_detection(expected, test_file)

    def test_name_before_c(self):
        test_file = self.get_test_loc('copyrights/name_before_c-c.c')
        expected = [
            'Russ Dill <Russ.Dill@asu.edu> 2001-2003',
            'Vladimir Oleynik <dzo@simtreas.ru> (c) 2003'
        ]
        check_detection(expected, test_file)

    def test_name_sign_year(self):
        test_file = self.get_test_loc('copyrights/name_sign_year_correct-c.c')
        expected = [
            'Copyright (c) 2008 Daisy Ltd. http://www.daisy.com',
            'Daisy (c) 1997 - 2008',
        ]
        check_detection(expected, test_file)

    def test_naumen_txt(self):
        test_file = self.get_test_loc('copyrights/naumen_txt.txt')
        expected = [
            'Copyright (c) NAUMEN (tm) and Contributors.',
        ]
        check_detection(expected, test_file)

    def test_ncurses_bin(self):
        test_file = self.get_test_loc('copyrights/ncurses_bin-ncurses_bin.copyright')
        expected = [
            'Copyright (c) 1998 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_nederlof(self):
        test_file = self.get_test_loc('copyrights/nederlof.txt')
        expected = [
            '(c) 2005 - Peter Nederlof',
        ]
        check_detection(expected, test_file)

    def test_trailing_copyleft(self):
        test_file = self.get_test_loc('copyrights/trailing_copyleft.txt')
        expected = [
            'Copyright (c) 1992 Ronald S. Karr',
        ]
        check_detection(expected, test_file)

    def test_no_c(self):
        test_file = self.get_test_loc('copyrights/no_c-c.c')
        expected = []
        check_detection(expected, test_file)

    def test_no_class_file_2(self):
        test_file = self.get_test_loc('copyrights/no_class_file_2-PersistentElementHolder_class.class')
        expected = []
        check_detection(expected, test_file)

    def test_no_class_file_3(self):
        test_file = self.get_test_loc('copyrights/no_class_file_3-PersistentIndexedElementHolder_class.class')
        expected = []
        check_detection(expected, test_file)

    def test_no_class_file_4(self):
        test_file = self.get_test_loc('copyrights/no_class_file_4-PersistentListElementHolder_class.class')
        expected = []
        check_detection(expected, test_file)

    def test_no_holder_java(self):
        test_file = self.get_test_loc('copyrights/no_holder_java-java.java')
        expected = [
            'Copyright (c) 2005',
        ]
        check_detection(expected, test_file)

    def test_nokia_cpp(self):
        test_file = self.get_test_loc('copyrights/nokia_cpp-cpp.cpp')
        expected = [
            'Copyright (c) 2002, Nokia Mobile Phones.',
        ]
        check_detection(expected, test_file)

    def test_north_c(self):
        test_file = self.get_test_loc('copyrights/north_c-99_c.c')
        expected = [
            'Copyright (c) 2010 42North Inc.',
        ]
        check_detection(expected, test_file)

    def test_notice2(self):
        test_file = self.get_test_loc('copyrights/notice2-9_NOTICE')
        expected = [
            'Copyright 2003-2009 The Apache Geronimo development community',
        ]
        check_detection(expected, test_file)

    def test_notice2_txt(self):
        test_file = self.get_test_loc('copyrights/notice2_txt-NOTICE.txt')
        expected = [
            'Copyright (c) 2004, Richard S. Hall',
            'Copyright (c) 2002,2003, Stefan Haustein, Oberhausen',
            'Copyright (c) 2002,2004, Stefan Haustein, Oberhausen',
            'Copyright (c) 2002,2003, Stefan Haustein, Oberhausen',
        ]
        check_detection(expected, test_file)

    def test_notice_name_before_statement(self):
        test_file = self.get_test_loc('copyrights/notice_name_before_statement-NOTICE')
        expected = [
            'at iClick, Inc., software copyright (c) 1999.',
        ]
        check_detection(expected, test_file)

    def test_notice_txt(self):
        test_file = self.get_test_loc('copyrights/notice_txt-NOTICE.txt')
        expected = [
            'Copyright 2003-2010 The Knopflerfish Project http://www.knopflerfish.org',
            'Copyright (c) OSGi Alliance (2000, 2009).',
            'Copyright (c) 2000-2005 INRIA, France Telecom',
            '(c) 1999-2003.',
            '(c) 2001-2004',
            'Copyright (c) 2004, Didier Donsez',
            '(c) 2001-2004 http://commons.apache.org/logging',
            '(c) 1999-2003. http://xml.apache.org/dist/LICENSE.txt',
            '(c) 2001-2004',
            'Copyright (c) 2004, Richard S. Hall',
            '(c) 2001-2004 http://xml.apache.org/xalan-j',
            '(c) 2001-2004 http://xerces.apache.org',
        ]
        check_detection(expected, test_file)

    def test_o_brien_style_name(self):
        test_file = self.get_test_loc('copyrights/o_brien_style_name.txt')
        expected = [
            "Copyright (c) 2001-2003, Patrick K. O'Brien",
        ]
        check_detection(expected, test_file)

    def test_oberhummer_c_code(self):
        test_file = self.get_test_loc('copyrights/oberhummer_c_code-c.c')
        expected = [
            'Copyright (c) 2005 Markus Franz Xaver Johannes Oberhumer',
            'Copyright (c) 2004 Markus Franz Xaver Johannes Oberhumer',
            'Copyright (c) 2003 Markus Franz Xaver Johannes Oberhumer',
            'Copyright (c) 2002 Markus Franz Xaver Johannes Oberhumer',
            'Copyright (c) 2001 Markus Franz Xaver Johannes Oberhumer',
            'Copyright (c) 2000 Markus Franz Xaver Johannes Oberhumer',
            'Copyright (c) 1999 Markus Franz Xaver Johannes Oberhumer',
            'Copyright (c) 1998 Markus Franz Xaver Johannes Oberhumer',
            'Copyright (c) 1997 Markus Franz Xaver Johannes Oberhumer',
            'Copyright (c) 1996 Markus Franz Xaver Johannes Oberhumer',
        ]
        check_detection(expected, test_file)

    def test_oberhummer_text(self):
        test_file = self.get_test_loc('copyrights/oberhummer_text.txt')
        expected = [
            'Copyright (c) 2005 Markus Franz Xaver Johannes Oberhumer',
            'Copyright (c) 2004 Markus Franz Xaver Johannes Oberhumer',
            'Copyright (c) 2003 Markus Franz Xaver Johannes Oberhumer',
            'Copyright (c) 2002 Markus Franz Xaver Johannes Oberhumer',
            'Copyright (c) 2001 Markus Franz Xaver Johannes Oberhumer',
            'Copyright (c) 2000 Markus Franz Xaver Johannes Oberhumer',
            'Copyright (c) 1999 Markus Franz Xaver Johannes Oberhumer',
            'Copyright (c) 1998 Markus Franz Xaver Johannes Oberhumer',
            'Copyright (c) 1997 Markus Franz Xaver Johannes Oberhumer',
            'Copyright (c) 1996 Markus Franz Xaver Johannes Oberhumer',
        ]
        check_detection(expected, test_file)

    def test_objectivec(self):
        test_file = self.get_test_loc('copyrights/objectivec-objectiveC_m.m')
        expected = [
            'Copyright (c) 2009 ABC',
        ]
        check_detection(expected, test_file)

    def test_openhackware(self):
        test_file = self.get_test_loc('copyrights/openhackware-openhackware.label')
        expected = [
            'Copyright (c) 2004-2005 Jocelyn Mayer <l_indien@magic.fr>',
            'Copyright (c) 2004-2005 Fabrice Bellard',
        ]
        check_detection(expected, test_file)

    def test_openoffice_org_report_builder_bin(self):
        test_file = self.get_test_loc('copyrights/openoffice_org_report_builder_bin.copyright')
        expected = [
            'Copyright (c) 2002-2009 Software in the Public Interest, Inc.',
            'Copyright (c) 2002-2009 ooo-build/Go-OO Team',
            '(c) Sun Microsystems.',
            'Copyright 2002-2009 Sun Microsystems, Inc.',
            'Copyright 2002-2009 Sun Microsystems, Inc.',
            'Copyright (c) 2002-2005 Maxim Shemanarev',
            'Copyright 2001-2004 The Apache Software Foundation.',
            'Copyright 2003-2007 The Apache Software Foundation',
            'Copyright 2001-2007 The Apache Software Foundation',
            'Copyright 1999-2007 The Apache Software Foundation',
            'Copyright (c) 2000 Pat Niemeyer',
            'Copyright (c) 2000 INRIA , France Telecom',
            'Copyright (c) 2002 France Telecom',
            'Copyright (c) 1990-2003 Sleepycat Software',
            'Copyright (c) 1990, 1993, 1994, 1995 The Regents of the University of California',
            'Copyright (c) 2003 by Bitstream, Inc.',
            'Cppyright Copyright (c) 2006 by Tavmjong Bah',
            'Copyright (c) 2007 Red Hat, Inc',
            'Copyright (c) 2007 Red Hat, Inc.',
            'Copyright 2000-2003 Beman Dawes',
            'Copyright (c) 1998-2003 Joel de Guzman',
            'Copyright (c) 2001-2003 Daniel Nuffer',
            'Copyright (c) 2001-2003 Hartmut Kaiser',
            'Copyright (c) 2002-2003 Martin Wille',
            'Copyright (c) 2002 Juan Carlos Arevalo-Baeza',
            'Copyright (c) 2002 Raghavendra Satish',
            'Copyright (c) 2002 Jeff Westfahl',
            'Copyright (c) 2001 Bruce Florman',
            'Copyright 1999 Tom Tromey',
            'Copyright 2002, 2003 University of Southern California, Information Sciences Institute',
            'Copyright 2004 David Reveman',
            'Copyright 2000, 2002, 2004, 2005 Keith Packard',
            'Copyright 2004 Calum Robinson',
            'Copyright 2004 Richard D. Worth',
            'Copyright 2004, 2005 Red Hat, Inc.',
            'Copyright 2004 David Reveman',
            '(c) Copyright 2000, Baptiste Lepilleur',
            'Copyright (c) 1996 - 2004, Daniel Stenberg',
            'Copyright (c) 1992,1994 by Dennis Vadura',
            'Copyright (c) 1996 by WTI Corp.',
            'Copyright 1999-2003 by Easy Software Products',
            'Copyright (c) 1998, 1999 Thai Open Source Software Center Ltd',
            'Copyright (c) 1987, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 2000 Free Software Foundation, Inc.',
            'Copyright (c) 2000,2001,2002,2003 by George William',
            'Copyright (c) 2001-2008, The HSQL Development Group',
            'Copyright (c) 1995, 1997, 2000, 2001, 2002 Free Software Foundation, Inc.',
            'Copyright (c) Kevin Hendricks',
            'Copyright (c) 2002-2008 Laszlo Nemeth',
            'Copyright (c) 2000 Bjoern Jacke',
            'Copyright 2000 by Sun Microsystems, Inc.',
            'Copyright (c) 1998 Raph Levien',
            'Copyright (c) 2001 ALTLinux, Moscow',
            'Copyright (c) 2006, 2007, 2008 Laszlo Nemeth',
            'Copyright (c) 2003-2006 The International Color Consortiu',
            'Copyright (c) 1995-2008 International Business Machines Corporation and others',
            'Copyright 2000-2005, by Object Refinery Limited',
            'Copyright 2005-2007, by Pentaho Corporation',
            'Copyright 1994-2002 World Wide Web Consortium',
            'Copyright (c) 1991-1998, Thomas G. Lane',
            'Copyright 1994-2002 World Wide Web Consortium',
            'Copyright (c) 2002 Anders Carlsson <andersca@gnu.org>',
            'Copyright (c) 2003, WiseGuys Internet B.V.',
            'Copyright (c) 2003, WiseGuys Internet B.V.',
            'Copyright 1997-1999 World Wide Web Consortium',
            'Copyright (c) 2002-2003 Aleksey Sanin',
            'Copyright (c) 2003 America Online, Inc.',
            'Copyright (c) 2001-2002 Daniel Veillard',
            'Copyright (c) 1998-2001 by the University of Florida',
            'Copyright (c) 1991, 2007 Free Software Foundation, Inc',
            'Copyright 2004 The Apache Software Foundation',
            'Copyright 2005 The Apache Software Foundation',
            'Copyright 2007 The Apache Software Foundation',
            'Copyright (c) 1999-2007 Brian Paul',
            'Copyright (c) 2007 The Khronos Group Inc.',
            'Copyright (c) 2003 Stuart Caie <kyzer@4u.net>',
            'Copyright (c) 1999-2006 Joe Orton <joe@manyfish.co.uk>',
            'Copyright (c) 1999-2000 Tommi Komulainen <Tommi.Komulainen@iki.fi>',
            'Copyright (c) 1999-2000 Peter Boos <pedib@colorfullife.com>',
            'Copyright (c) 1991, 1995, 1996, 1997 Free Software Foundation, Inc.',
            'Copyright (c) 2004 Aleix Conchillo Flaque <aleix@member.fsf.org>',
            'Copyright (c) 2004 Jiang Lei <tristone@deluxe.ocn.ne.jp>',
            'Copyright (c) 2004-2005 Vladimir Berezniker http://public.xdi.org',
            'Copyright (c) 1998 Netscape Communications Corporation',
            'Copyright (c) 1998-2007 The OpenSSL Project',
            'Copyright (c) 1998-2007 The OpenSSL Project',
            'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            'Copyright (c) 2001, 2002, 2003, 2004 Python Software Foundation',
            'Copyright (c) 2000 BeOpen.com',
            'Copyright (c) 1995-2001 Corporation for National Research Initiatives',
            'Copyright (c) 1991-1995 Stichting Mathematisch Centrum',
            'Copyright (c) 2000-2007 David Beckett',
            'Copyright (c) 2000-2005 University of Bristol',
            'Copyright (c) 1993, 94, 95, 96, 97, 98, 99 Free Software Foundation, Inc',
            'Copyright (c) 1997-2000 Netscape Communications Corporation',
            'Copyright (c) 2000 see Beyond Communications Corporation',
            'Copyright (c) 1997 David Mosberger-Tang and Andreas Beck',
            'Copyright (c) 1998, 1999 James Clark',
            'Copyright ? 1999 CERN - European Organization for Nuclear Research',
            'Copyright (c) 2002-2003 Aleksey Sanin',
            'Copyright (c) 2003 America Online, Inc.',
            'Copyright (c) 2001-2002 Daniel Veillard',
            'Copyright (c) 1998-2001 by the University of Florida',
            'Copyright (c) 1991, 2007 Free Software Foundation, Inc',
            'Copyright 2004 The Apache Software Foundation',
            'Copyright 2005 The Apache Software Foundation',
            'Copyright 2007 The Apache Software Foundation',
            'Copyright (c) 1999-2007 Brian Paul',
            'Copyright (c) 2007 The Khronos Group Inc.',
            'Copyright (c) 2003 Stuart Caie <kyzer@4u.net>',
            'Copyright (c) 1999-2006 Joe Orton <joe@manyfish.co.uk>',
            'Copyright (c) 1999-2000 Tommi Komulainen <Tommi.Komulainen@iki.fi>',
            'Copyright (c) 1999-2000 Peter Boos <pedib@colorfullife.com>',
            'Copyright (c) 1991, 1995, 1996, 1997 Free Software Foundation, Inc.',
            'Copyright (c) 2004 Aleix Conchillo Flaque <aleix@member.fsf.org>',
            'Copyright (c) 2004 Jiang Lei <tristone@deluxe.ocn.ne.jp>',
            'Copyright (c) 2004-2005 Vladimir Berezniker http://public.xdi.org',
            'Copyright (c) 1998 Netscape Communications Corporation',
            'Copyright (c) 1998-2007 The OpenSSL Project',
            'Copyright (c) 1998-2007 The OpenSSL Project',
            'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            'Copyright (c) 2001, 2002, 2003, 2004 Python Software Foundation',
            'Copyright (c) 2000 BeOpen.com',
            'Copyright (c) 1995-2001 Corporation for National Research Initiatives',
            'Copyright (c) 1991-1995 Stichting Mathematisch Centrum',
            'Copyright (c) 2000-2007 David Beckett',
            'Copyright (c) 2000-2005 University of Bristol',
            'Copyright (c) 1993, 94, 95, 96, 97, 98, 99 Free Software Foundation, Inc',
            'Copyright (c) 1997-2000 Netscape Communications Corporation',
            'Copyright (c) 2000 see Beyond Communications Corporation',
            'Copyright (c) 1997 David Mosberger-Tang and Andreas Beck',
            'Copyright (c) 1998, 1999 James Clark',
            'Copyright ? 1999 CERN - European Organization for Nuclear Research',
            'Copyright (c) 1994 Hewlett-Packard Company',
            'Copyright (c) 1996-1999 Silicon Graphics Computer Systems, Inc.',
            'Copyright (c) 1997 Moscow Center for SPARC Technology',
            'Copyright (c) 1999, 2000, 2001 Boris Fomitchev',
            'Copyright 1999-2002,2004 The Apache Software Foundation',
            'Copyright (c) 1991, 1992 TWAIN Working Group',
            'Copyright (c) 1997 TWAIN Working Group',
            'Copyright (c) 1998 TWAIN Working Group',
            'Copyright (c) 2000 TWAIN Working Group',
            'Copyright 1998-2001 by Ullrich Koethe',
            'Copyright 2004 by Urban Widmark',
            'Copyright 2002-2007 by Henrik Just',
            'Copyright (c) 2000, Compaq Computer Corporation',
            'Copyright (c) 2002, Hewlett Packard, Inc',
            'Copyright (c) 2000 SuSE, Inc.',
            'Copyright 1996-2007 Glyph & Cog, LLC.',
            'Copyright (c) 1995-2002 Jean-loup Gailly and Mark Adler',
        ]
        check_detection(expected, test_file)

    def test_openoffice_org_report_builder_bin_2(self):
        test_file = self.get_test_loc('copyrights/openoffice_org_report_builder_bin_2-openoffice_org_report_builder_bin.copyright2')
        expected = [
            'Copyright (c) 1990, 1993, 1994, 1995 The Regents of the University of California',
            'Copyright (c) 1995, 1996 The President and Fellows of Harvard University',
        ]
        check_detection(expected, test_file)

    def test_partial_detection(self):
        test_file = self.get_test_loc('copyrights/partial_detection.txt')
        expected = [
            'Copyright 1991 by the Massachusetts Institute of Technology',
            'Copyright (c) 2001 AT&T',
            'Copyright (c) 2004-2006 by Henrique de Moraes Holschuh <hmh@debian.org>',
            'Copyright 2005-2007 Christopher Montgomery , Jean-Marc Valin , Timothy Terriberry',
            'Copyright (c) 2007 James Newton-King',
            'Copyright (c) 2006, SHIMODA Hiroshi <piro@p.club.ne.jp>',
            'Copyright (c) 2006, FUJITA Yuji <yuji@webmasters.gr.jp>',
            'Copyright (c) 2002-2009 ooo-build/Go-OO Team',
            'Copyright (c) 2002-2009 Software in the Public Interest, Inc.',
            'Copyright (c) 2004 by the Perl 5 Porters',
            'Copyright (c) 2006 Academy of Motion Picture Arts and Sciences',
            'Copyright (c) 1995-2000 Corporation for National Research Initiatives',
            'Copyright (c) 2001 EU DataGrid',
            'Copyright (c) 2000. OCLC Research',
            'Copyright (c) 1999 Trolltech AS',
        ]
        check_detection(expected, test_file)

    def test_partial_detection_mit(self):
        test_file = self.get_test_loc('copyrights/partial_detection_mit.txt')
        expected = [
            'Copyright 1991 by the Massachusetts Institute of Technology',
            'Copyright (c) 2001 AT&T',
            'Copyright (c) 2004-2006 by Henrique de Moraes Holschuh <hmh@debian.org>',
            'Copyright 2005-2007 Christopher Montgomery , Jean-Marc Valin , Timothy Terriberry',
            'Copyright (c) 2007 James Newton-King',
            'Copyright (c) 2006, SHIMODA Hiroshi <piro@p.club.ne.jp>',
            'Copyright (c) 2006, FUJITA Yuji <yuji@webmasters.gr.jp>',
            'Copyright (c) 2002-2009 ooo-build/Go-OO Team',
            'Copyright (c) 2002-2009 Software in the Public Interest, Inc.',
            'Copyright (c) 2004 by the Perl 5 Porters',
            'Copyright (c) 2006 Academy of Motion Picture Arts and Sciences',
            'Copyright (c) 1995-2000 Corporation for National Research Initiatives',
            'Copyright (c) 2001 EU DataGrid',
            'Copyright (c) 2000. OCLC Research',
            'Copyright (c) 1999 Trolltech AS',
        ]
        check_detection(expected, test_file)

    def test_perl_base(self):
        test_file = self.get_test_loc('copyrights/perl_base-perl_base.copyright')
        expected = [
            'Copyright 1989-2001, Larry Wall',
            'Copyright (c) 1995-2005 Jean-loup Gailly and Mark Adler',
            'Copyright (c) 1991-2006 Unicode, Inc.',
            'Copyright (c) 1991-2008 Unicode, Inc.',
            'Copyright (c) 2004 by the Perl 5 Porters',
            'copyright (c) 1994 by the Regents of the University of California',
            'Copyright (c) 1994 The Regents of the University of California',
            'Copyright (c) 1989, 1993 The Regents of the University of California',
            'copyright (c) 1996-2007 Julian R Seward',
        ]
        check_detection(expected, test_file)

    def test_perl_module(self):
        test_file = self.get_test_loc('copyrights/perl_module-pm.pm')
        expected = [
            'Copyright (c) 1995-2000 Name Surname',
        ]
        check_detection(expected, test_file)

    def test_peter_c(self):
        test_file = self.get_test_loc('copyrights/peter_c-c.c')
        expected = [
            '(c) 2005 - Peter Nederlof',
        ]
        check_detection(expected, test_file)

    @expectedFailure
    def test_piersol(self):
        test_file = self.get_test_loc('copyrights/piersol-TestMatrix_D_java.java')
        expected = [
            'Copyright (c) 1998 Company PIERSOL Engineering Inc.',
            'Copyright (c) 1998 Company PIERSOL Engineering Inc.',
        ]
        check_detection(expected, test_file)

    def test_piersol_ok(self):
        test_file = self.get_test_loc('copyrights/piersol-TestMatrix_D_java.java')
        expected = [
            'Copyright (c) 1998 <p> Company PIERSOL Engineering Inc.',
            'Copyright (c) 1998 <p> Company PIERSOL Engineering Inc.',
        ]
        check_detection(expected, test_file)

    def test_postgresql_8_3(self):
        test_file = self.get_test_loc('copyrights/postgresql_8_3-postgresql.label')
        expected = [
            'Portions Copyright (c) 1996-2003, The PostgreSQL Global Development Group',
            'Portions Copyright (c) 1994, The Regents of the University of California',
            'Copyright (c) 1998, 1999 Henry Spencer',
            'copyrighted by the Regents of the University of California, Sun Microsystems, Inc., Scriptics Corporation, ActiveState Corporation'
        ]
        check_detection(expected, test_file)

    def test_prof_informatics(self):
        test_file = self.get_test_loc('copyrights/prof_informatics.txt')
        expected = [
            'Professional Informatics (c) 1994',
        ]
        check_detection(expected, test_file)

    def test_professional_txt(self):
        test_file = self.get_test_loc('copyrights/professional_txt-copyright.txt')
        expected = [
            'Professional Informatics (c) 1994',
        ]
        check_detection(expected, test_file)

    def test_properties(self):
        test_file = self.get_test_loc('copyrights/properties-properties.properties')
        expected = [
            '(c) 2004-2007 Restaurant.',
        ]
        check_detection(expected, test_file)

    def test_psf_in_python(self):
        test_file = self.get_test_loc('copyrights/psf_in_python-BitVector_py.py')
        expected = [
            'copyright (c) 2008 Avinash Kak. Python Software Foundation.',
        ]
        check_detection(expected, test_file)

    def test_python_dateutil(self):
        test_file = self.get_test_loc('copyrights/python_dateutil-python_dateutil.copyright')
        expected = [
            'Copyright (c) 2001, 2002 Python Software Foundation',
            'Copyright (c) 1995-2001 Corporation for National Research Initiatives',
            'Copyright (c) 1991 - 1995, Stichting Mathematisch Centrum Amsterdam',
        ]
        check_detection(expected, test_file)

    def test_python_psyco(self):
        test_file = self.get_test_loc('copyrights/python_psyco-python_psyco.copyright')
        expected = [
            'Copyright (c) 2001-2003 Armin Rigo',
        ]
        check_detection(expected, test_file)

    def test_python_reportbug(self):
        test_file = self.get_test_loc('copyrights/python_reportbug-python_report.label')
        expected = [
            'Copyright (c) 1999-2006 Chris Lawrence',
            'Copyright (c) 2008-2009 Sandro Tosi <morph@debian.org>',
            'Copyright (c) 1996-2000 Christoph Lameter <clameter@debian.org>',
            '(c) 1996-2000 Nicolas Lichtmaier <nick@debian.org>',
            '(c) 2000 Chris Lawrence <lawrencc@debian.org>',
            'Copyright (c) 2008 Ben Finney <ben+debian@benfinney.id.au>',
            'Copyright (c) 2008 Ben Finney <ben+debian@benfinney.id.au>',
            'Copyright (c) 2008 Sandro Tosi <morph@debian.org>',
            'Copyright (c) 2006 Philipp Kern <pkern@debian.org>',
            'Copyright (c) 2008-2009 Luca Bruno <lethalman88@gmail.com>',
        ]
        check_detection(expected, test_file)

    def test_python_software_properties(self):
        test_file = self.get_test_loc('copyrights/python_software_properties-python_software_properties.copyright')
        expected = [
            'Copyright 2004-2007 Canonical Ltd. 2004-2005 Michiel Sikkes 2006',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_red_hat_openoffice_org_report_builder_bin(self):
        test_file = self.get_test_loc('copyrights/red_hat_openoffice_org_report_builder_bin-openoffice_org_report_builder_bin.copyright')
        expected = [
            'Copyright (c) 2007 Red Hat, Inc',
            'Copyright (c) 2007 Red Hat, Inc.',
        ]
        check_detection(expected, test_file)

    def test_regents_complex(self):
        test_file = self.get_test_loc('copyrights/regents_complex-strtol_c.c')
        expected = [
            'Copyright (c) 1990 The Regents of the University of California.',
        ]
        check_detection(expected, test_file)

    # #@expectedFailure
    def test_regents_license(self):
        test_file = self.get_test_loc('copyrights/regents_license-LICENSE')
        expected = [
            'copyrighted by The Regents of the University of California.',
            'Copyright 1979, 1980, 1983, 1986, 1988, 1989, 1991, 1992, 1993, 1994 The Regents of the University of California.',
            'copyright C 1988 by the Institute of Electrical and Electronics Engineers, Inc.',
        ]
        check_detection(expected, test_file)

    def test_resig_js(self):
        test_file = self.get_test_loc('copyrights/resig_js-js.js')
        expected = [
            'Copyright (c) 2009 John Resig',
        ]
        check_detection(expected, test_file)

    def test_rusty(self):
        test_file = self.get_test_loc('copyrights/rusty.txt')
        expected = [
            '(c) Rusty Russell, IBM 2002',
        ]
        check_detection(expected, test_file)

    def test_rusty_c(self):
        test_file = self.get_test_loc('copyrights/rusty_c-c.c')
        expected = [
            '(c) Rusty Russell, IBM 2002',
        ]
        check_detection(expected, test_file)

    def test_s_fabsl_c(self):
        test_file = self.get_test_loc('copyrights/s_fabsl_c-s_fabsl_c.c')
        expected = [
            'Copyright (c) 2003 Dag-Erling Coidan Smrgrav',
        ]
        check_detection(expected, test_file)

    def test_sample_java(self):
        test_file = self.get_test_loc('copyrights/sample_java-java.java')
        expected = [
            'Copyright (c) 2000-2007, Sample ABC Inc.',
        ]
        check_detection(expected, test_file)

    def test_sample_no(self):
        test_file = self.get_test_loc('copyrights/sample_no-c.c')
        expected = []
        check_detection(expected, test_file)

    def test_seahorse_plugins(self):
        test_file = self.get_test_loc('copyrights/seahorse_plugins-seahorse_plugins.copyright')
        expected = [
            'Copyright (c) 2004-2007 Stefan Walter',
            'Copyright (c) 2004-2006 Adam Schreiber',
            'Copyright (c) 2001-2003 Jose Carlos Garcia Sogo',
            'Copyright (c) 2002, 2003 Jacob Perkins',
            'Copyright (c) 2004, 2006 Nate Nielsen',
            'Copyright (c) 2000-2004 Marco Pesenti Gritti',
            'Copyright (c) 2003-2006 Christian Persch',
            'Copyright (c) 2004, 2006 Jean-Francois Rameau',
            'Copyright (c) 2000, 2001 Eazel, Inc.',
            'Copyright (c) 2007, 2008 Jorge Gonzalez',
            'Copyright (c) 2007, 2008 Daniel Nylander',
            'Copyright (c) 2004-2005 Shaun McCance',
            'Copyright (c) 2007 Milo Casagrande',
            'Copyright (c) 2007-2008 Claude Paroz',
            'Copyright (c) 2007 GNOME i18n Project',
            # Copyright © 2008 <s>Василий Фаронов</s>
            'Vietnamese Copyright (c) 2008',  # i18n Project for Vietnamese Copyright (c) 2008
            'Copyright (c) 1992-2008 Free Software Foundation, Inc.',
            'Copyright (c) 1999 Dave Camp',
            'Copyright (c) 2005 Tecsidel S.A.',
            'Copyright (c) 2004-2005 Adam Weinberger and the GNOME Foundation',
            'Copyright (c) 2007, 2008 The GNOME Project',
            'Copyright (c) 2007 Swecha Telugu Localisation Team',
            'Copyright (c) 1995-1997 Ulrich Drepper',
            'Copyright (c) 2004-2008 Rodney Dawes',
            'Copyright (c) 1999, 2000 Anthony Mulcahy',
            'Copyright (c) 2007 Ihar Hrachyshka',
            'Copyright (c) 2004, 2005 Miloslav Trmac',
            'Copyright (c) 2003 Peter Mato',
            'Copyright (c) 2004, 2005 Danijel Studen , Denis Lackovic , Ivan Jankovic',
            'Copyright (c) 1994 X Consortium',
            'Copyright (c) 2006 Alexander Larsson',
            'Copyright (c) 2000-2003 Ximian Inc.',
            'Copyright (c) 1995-1997 Peter Mattis , Spencer Kimball and Josh MacDonald',
            'Copyright (c) 1999, 2000 Robert Bihlmeyer',
            'Copyright (c) Crispin Flowerday',
            'Copyright (c) 2008 Frederic Peters',
            'Copyright (c) 2008 Lucas Lommer',
            'Copyright (c) 2008 Mario Blattermann',
            'Copyright (c) 2001-2004 Red Hat, Inc.',
            'Copyright (c) 2004 Scott James Remnant',
            # note this is not correct and severaly truncated
            'Copyright (c) 1998-2006 by the',  # following: Dave Ahlswede, Manuel Amador, Matt Amato, Daniel Atallah, Paul Aurich, Patrick Aussems, Anibal Avelar, Alex Badea, John Bailey, Chris Banal, Luca Barbato, Levi Bard, Kevin Barry, Derek Battams, Martin Bayard, Curtis Beattie, Dave Bell, Igor Belyi, Brian Bernas, Paul Betts, Jonas Birme, Eric Blade, Ethan Blanton, Joshua Blanton, Rainer Blessing, Herman Bloggs, David Blue, Jason Boerner, Graham Booker, Paolo Borelli, Julien Bossart, Craig Boston, Chris Boyle, Derrick J Brashear, Matt Brenneke, Jeremy Brooks, Philip Brown, Sean Burke, Thomas Butter, Andrea Canciani, Damien Carbery, Michael Carlson, Keegan Carruthers-Smith, Steve Cavilia, Julien Cegarra, Cerulean Studios, LLC',
            'Copyright (c) 2008 Sebastien Bacher , Andreas Moog , Emilio Pozuelo Monfort and Josselin Mouette',
        ]
        check_detection(expected, test_file)

    def test_simgear1_0_0(self):
        test_file = self.get_test_loc('copyrights/simgear1_0_0-simgear.copyright')
        expected = [
            'Copyright (c) 1999-2000 Curtis L. Olson <curt@flightgear.org>',
            'Copyright (c) 2002-2004 Mark J. Harris',
        ]
        check_detection(expected, test_file)

    def test_snippet_no(self):
        test_file = self.get_test_loc('copyrights/snippet_no')
        expected = []
        check_detection(expected, test_file)

    def test_snmptrapd_c(self):
        test_file = self.get_test_loc('copyrights/snmptrapd_c-snmptrapd_c.c')
        expected = [
            'Copyright 1989, 1991, 1992 by Carnegie Mellon University',
        ]
        check_detection(expected, test_file)

    def test_some_co(self):
        test_file = self.get_test_loc('copyrights/some_co-9_h.h')
        expected = [
            'Copyright Some Company, inc.',
        ]
        check_detection(expected, test_file)

    def test_somefile_cpp(self):
        test_file = self.get_test_loc('copyrights/somefile_cpp-somefile_cpp.cpp')
        expected = [
            '(c) 2005',
            'Copyright Private Company (PC) Property of Private Company',
            'Copyright (2003) Private Company',
        ]
        check_detection(expected, test_file)

    def test_source_auditor_projectinfo_java(self):
        test_file = self.get_test_loc('copyrights/source_auditor_projectinfo_java-ProjectInfo_java.java')
        expected = [
            'Copyright (c) 2009 Source Auditor Inc.',
        ]
        check_detection(expected, test_file)

    def test_stacktrace_cpp(self):
        test_file = self.get_test_loc('copyrights/stacktrace_cpp-stacktrace_cpp.cpp')
        expected = [
            'Copyright 2003, 2004 Rickard E. Faith (faith@dict.org)',
        ]
        check_detection(expected, test_file)

    def test_stmicro_in_h(self):
        test_file = self.get_test_loc('copyrights/stmicro_in_h-h.h')
        expected = [
            'COPYRIGHT (c) ST-Microelectronics 1998.',
        ]
        check_detection(expected, test_file)

    def test_stmicro_in_txt(self):
        test_file = self.get_test_loc('copyrights/stmicro_in_txt.txt')
        expected = [
            'COPYRIGHT (c) STMicroelectronics 2005.',
            'COPYRIGHT (c) ST-Microelectronics 1998.',
        ]
        check_detection(expected, test_file)

    def test_strchr_assembly(self):
        test_file = self.get_test_loc('copyrights/strchr_assembly-9_9_strchr_S.S')
        expected = [
            'Copyright (c) 2007 ARC International (UK) LTD',
        ]
        check_detection(expected, test_file)

    def test_super_tech_c(self):
        test_file = self.get_test_loc('copyrights/super_tech_c-c.c')
        expected = [
            'Copyright (c) $LastChangedDate$ Super Technologies Corporation, Cedar Rapids, Iowa, U.S.A.',
            'Copyright (c) 2004 Benjamin Herrenschmuidt (benh@kernel.crashing.org), IBM Corp.',
        ]
        check_detection(expected, test_file)

    def test_tcl(self):
        test_file = self.get_test_loc('copyrights/tcl-tcl.copyright')
        expected = [
            'copyrighted by the Regents of the University of California , Sun Microsystems, Inc. , Scriptics Corporation',  # not found, rather complex
            'Copyright (c) 2007 Software in the Public Interest',
        ]
        check_detection(expected, test_file)

    def test_tech_sys(self):
        test_file = self.get_test_loc('copyrights/tech_sys.txt')
        expected = [
            '(c) Copyright 1985-1999 SOME TECHNOLOGY SYSTEMS',
        ]
        check_detection(expected, test_file)

    def test_texinfo_tex(self):
        test_file = self.get_test_loc('copyrights/texinfo_tex-texinfo_tex.tex')
        expected = [
            'Copyright (c) 1985, 1986, 1988, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_texlive_lang_greek(self):
        test_file = self.get_test_loc('copyrights/texlive_lang_greek-texlive_lang_greek.copyright')
        expected = [
            'Copyright 1999 2002-2006 LaTeX3 Project',
            'Copyright 2005 M. Y. Name',
        ]
        check_detection(expected, test_file)

    def test_texlive_lang_spanish(self):
        test_file = self.get_test_loc('copyrights/texlive_lang_spanish-texlive_lang_spanish.copyright')
        expected = [
            'Copyright 1999 2002-2006 LaTeX3 Project',
            'Copyright 2005 M. Y. Name',
        ]
        check_detection(expected, test_file)

    def test_texlive_lang_vietnamese(self):
        test_file = self.get_test_loc('copyrights/texlive_lang_vietnamese-texlive_lang_vietnamese.label')
        expected = [
            'Copyright 1999 2002-2006 LaTeX3 Project',
            'Copyright 2005 M. Y. Name',
        ]
        check_detection(expected, test_file)

    def test_tfc_c(self):
        test_file = self.get_test_loc('copyrights/tfc_c-c.c')
        expected = [
            'Copyright 1991, 1992, 1993, 1994, 1995, 1996, 1998, 1999, 2000, 2001 Traditional Food Consortium, Inc.',
            'Copyright 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007 Traditional Food Consortium, Inc.',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_thirdpartyproject_prop(self):
        test_file = self.get_test_loc('copyrights/thirdpartyproject_prop-ThirdPartyProject_prop.prop')
        expected = [
            'Copyright 2010 Google Inc.',
        ]
        check_detection(expected, test_file)

    def test_trailing_For(self):
        test_file = self.get_test_loc('copyrights/trailing_For-c.c')
        expected = [
            'Copyright . 2008 Mycom Pany, inc.',
            'Copyright (c) 1995-2003 Jean-loup Gailly.',
        ]
        check_detection(expected, test_file)

    def test_trailing_name(self):
        test_file = self.get_test_loc('copyrights/trailing_name-copyright.txt')
        expected = [
            'Copyright (c) 1998, 1999, 2000 Thai Open Source Software Center Ltd and Clark Cooper',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_trailing_redistribution(self):
        test_file = self.get_test_loc('copyrights/trailing_redistribution-bspatch_c.c')
        expected = [
            'Copyright (c) 2008 The Android Open Source Project',
            'Copyright 2003-2005 Colin Percival',
        ]
        check_detection(expected, test_file)

    def test_transcode_doc(self):
        test_file = self.get_test_loc('copyrights/transcode_doc-transcode_doc.copyright')
        expected = [
            'Copyright (c) 2001 Thomas Ostreich',
        ]
        check_detection(expected, test_file)

    def test_transfig_with_parts(self):
        test_file = self.get_test_loc('copyrights/transfig_with_parts-transfig.copyright')
        expected = [
            'Copyright (c) 1985-1988 Supoj Sutantavibul',
            'Copyright (c) 1991-1999 Micah Beck',
            'Copyright (c) 1989-2002 by Brian V. Smith',
            'Copyright (c) 1991 by Paul King',
            'Copyright (c) 1995 C. Blanc and C. Schlick',
            'Copyright (c) 1993 Anthony Starks',
            'Copyright (c) 1992 Uri Blumenthal, I BM',
            'Copyright (c) 1992 by Brian Boyter',
            'Copyright (c) 1995 Dane Dwyer',
            'Copyright (c) 1999 by Philippe Bekaert',
            'Copyright (c) 1999 by T. Sato',
            'Copyright (c) 1998 by Mike Markowski',
            'Copyright (c) 1994-2002 by Thomas Merz',
            'Copyright (c) 2002-2006 by Martin Kroeker',
            'Copyright 1990, David Koblas',
            'Copyright, 1987, Massachusetts Institute of Technology',
            'Copyright (c) 2006 Michael Pfeiffer p3fff@web.de',
        ]
        check_detection(expected, test_file)

    def test_treetablemodeladapter_java(self):
        test_file = self.get_test_loc('copyrights/treetablemodeladapter_java-TreeTableModelAdapter_java.java')
        expected = [
            'Copyright 1997, 1998 by Sun Microsystems, Inc.',
        ]
        check_detection(expected, test_file)

    def test_truncated_dmv_c(self):
        test_file = self.get_test_loc('copyrights/truncated_dmv_c-9_c.c')
        expected = [
            'Copyright (c) 1995 DMV - DigiMedia Vision',
        ]
        check_detection(expected, test_file)

    def test_truncated_doe(self):
        test_file = self.get_test_loc('copyrights/truncated_doe-c.c')
        expected = [
            'Copyright (c) 2008 by John Doe',
        ]
        check_detection(expected, test_file)

    def test_truncated_inria(self):
        test_file = self.get_test_loc('copyrights/truncated_inria.txt')
        expected = [
            '(c) 1998-2000 (W3C) MIT, INRIA, Keio University',
        ]
        check_detection(expected, test_file)

    def test_truncated_rusty(self):
        test_file = self.get_test_loc('copyrights/truncated_rusty-c.c')
        expected = [
            '(c) 1999-2001 Paul Rusty Russell',
        ]
        check_detection(expected, test_file)

    def test_truncated_swfobject_js(self):
        test_file = self.get_test_loc('copyrights/truncated_swfobject_js-swfobject_js.js')
        expected = [
            'Copyright (c) 2007-2008 Geoff Stearns, Michael Williams, and Bobby van der Sluis',
        ]
        check_detection(expected, test_file)

    def test_ttf_malayalam_fonts(self):
        test_file = self.get_test_loc('copyrights/ttf_malayalam_fonts-ttf_malayalam_fonts.copyright')
        expected = [
            'Copyright (c) Jeroen Hellingman <jehe@kabelfoon.nl> , N.V Shaji <nvshaji@yahoo.com>',
            'Copyright (c) 2004 Kevin & Siji',
            'Copyright (c) Suresh',
            'Copyright (c) 2007 Hiran Venugopalan',
            'Copyright (c) 2007 Hussain',
            'Copyright (c) 2005 Rachana Akshara Vedi',
            'Copyright (c) CDAC, Mumbai Font Design',
            'Copyright (c) 2003 Modular Infotech, Pune',
            'Copyright (c) 2006 Modular Infotech Pvt Ltd.',
            'Copyright (c) 2009 Red Hat, Inc.',
        ]
        check_detection(expected, test_file)

    def test_tunnel_h(self):
        test_file = self.get_test_loc('copyrights/tunnel_h-tunnel_h.h')
        expected = [
            'Copyright (c) 2000 Frank Strauss <strauss@ibr.cs.tu-bs.de>',
        ]
        check_detection(expected, test_file)

    def test_two_digits_years(self):
        test_file = self.get_test_loc('copyrights/two_digits_years-digits_c.c')
        expected = [
            'Copyright (c) 1987,88,89,90,91,92,93,94,96,97 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    @expectedFailure
    def test_url_in_html(self):
        test_file = self.get_test_loc('copyrights/url_in_html-detail_9_html.html')
        expected = [
            '(c) 2004-2009 pudn.com',
        ]
        check_detection(expected, test_file)

    def test_utilities_js(self):
        test_file = self.get_test_loc('copyrights/utilities_js-utilities_js.js')
        expected = [
            'Copyright (c) 2009, Yahoo! Inc.',
            'Copyright 2001 Robert Penner',
        ]
        check_detection(expected, test_file)

    def test_var_route_c(self):
        test_file = self.get_test_loc('copyrights/var_route_c-var_route_c.c')
        expected = [
            'Copyright 1988, 1989 by Carnegie Mellon University',
            'Copyright 1989 TGV, Incorporated',
            'Erik Schoenfelder (schoenfr@ibr.cs.tu-bs.de) 1994/1995.',
            'Simon Leinen (simon@switch.ch) 1997',
        ]
        check_detection(expected, test_file)

    def test_view_layout2_xml(self):
        test_file = self.get_test_loc('copyrights/view_layout2_xml-view_layout_xml.xml')
        expected = [
            'Copyright (c) 2008 Esmertec AG.',
        ]
        check_detection(expected, test_file)

    def test_warning_parsing_empty_text(self):
        test_file = self.get_test_loc('copyrights/warning_parsing_empty_text-controlpanel_anjuta.anjuta')
        expected = []
        check_detection(expected, test_file)

    def test_web_app_dtd_b_sun(self):
        test_file = self.get_test_loc('copyrights/web_app_dtd_b_sun-web_app_dtd.dtd')
        expected = [
            'Copyright 2000-2007 Sun Microsystems, Inc.',
        ]
        check_detection(expected, test_file)

    def test_web_app_dtd_sun_twice(self):
        test_file = self.get_test_loc('copyrights/web_app_dtd_sun_twice-web_app_b_dtd.dtd')
        expected = [
            'Copyright (c) 2000 Sun Microsystems, Inc.',
            'Copyright (c) 2000 Sun Microsystems, Inc.',
        ]
        check_detection(expected, test_file)

    def test_wide_c(self):
        test_file = self.get_test_loc('copyrights/wide_c-c.c')
        expected = [
            'Copyright (c) 1995, 1996, 1997, and 1998 WIDE Project.',
        ]
        check_detection(expected, test_file)

    def test_wide_txt(self):
        test_file = self.get_test_loc('copyrights/wide_txt.txt')
        expected = [
            'Copyright (c) 1995, 1996, 1997, and 1998 WIDE Project.',
        ]
        check_detection(expected, test_file)

    def test_with_verbatim_lf(self):
        test_file = self.get_test_loc('copyrights/with_verbatim_lf-verbatim_lf_c.c')
        expected = [
            'Copyright 2003-2005 Colin Percival',
        ]
        check_detection(expected, test_file)

    def test_xconsortium_sh(self):
        test_file = self.get_test_loc('copyrights/xconsortium_sh-9_sh.sh')
        expected = [
            'Copyright (c) 1994 X Consortium',
        ]
        check_detection(expected, test_file)

    def test_xfonts_utils(self):
        test_file = self.get_test_loc('copyrights/xfonts_utils-xfonts_utils.copyright')
        expected = [
            'Copyright 1991, 1993, 1998 The Open Group',
            'Copyright 2005 Red Hat, Inc.',
            'Copyright 2005 Red Hat, Inc',
            'Copyright (c) 1991-2003 Unicode, Inc.',
            'Copyright (c) 2003 The NetBSD Foundation, Inc.',
            'Copyright (c) 2006 Martin Husemann.',
            'Copyright (c) 2007 Joerg Sonnenberger.',
            'Copyright (c) 2002-2008 by Juliusz Chroboczek',
            'Copyright (c) 1987, 1993 The Regents of the University of California.',
            'Copyright 1993, 1994, 1998 The Open Group',
            'Copyright (c) 2002-2008 by Juliusz Chroboczek',
            'Copyright 1999, 2001, 2002, 2004 Branden Robinson',
            'Copyright 2006 Steve Langasek',
            'Copyright 1999, 2001, 2002, 2004 Branden Robinson',
            'Copyright 1999-2002, 2004 Branden Robinson',
            'Copyright 2006 Steve Langasek',
        ]
        check_detection(expected, test_file)

    def test_xresprobe(self):
        test_file = self.get_test_loc('copyrights/xresprobe-xresprobe.label')
        expected = [
            'copyright (c) 2004 Canonical Software',
            'Copyright (c) 2002 Terra Soft Solutions, Inc.',
            'Copyright (c) 1998 by Josh Vanderhoof',
            'Copyright (c) 1996-1999 SciTech Software, Inc.',
            'copyright (c) David Mosberger-Tang',
            'Copyright (c) 1999 Egbert Eich',
        ]
        check_detection(expected, test_file)

    def test_xsane(self):
        test_file = self.get_test_loc('copyrights/xsane-xsane.label')
        expected = [
            'Copyright (c) 1998-2005 Oliver Rauch',
        ]
        check_detection(expected, test_file)

    def test_does_not_return_junk_in_pdf(self):
        # from https://github.com/ttgurney/yocto-spdx/blob/master/doc/Yocto-SPDX_Manual_Install_Walkthrough.pdf
        test_file = self.get_test_loc('copyrights/Yocto-SPDX.pdf')
        expected = [
        ]
        check_detection(expected, test_file)

    def test_name_and_co(self):
        test_file = self.get_test_loc('copyrights/nnp_and_co.txt')
        expected = [
            'Copyright (c) 2001, Sandra and Klaus Rennecke.',
        ]
        check_detection(expected, test_file)

    def test_with_ascii_art(self):
        test_file = self.get_test_loc('copyrights/with_ascii_art.txt')
        expected = [
            'Copyright (c) 1996. The Regents of the University of California.',
        ]
        check_detection(expected, test_file)

    def test_should_not_be_detected_in_pixel_data_stream(self):
        test_file = self.get_test_loc('copyrights/pixelstream.rgb')
        expected = []
        check_detection(expected, test_file)

    def test_should_not_contain_leading_or_trailing_colon(self):
        test_file = self.get_test_loc('copyrights/with_colon')
        expected = ['copyright (c) 2013 by Armin Ronacher.']
        check_detection(expected, test_file)

    def test_markup_should_not_be_truncated(self):
        test_file = self.get_test_loc('copyrights/html.html')
        expected = ["(c) Copyright 2010 by the <a href http://wtforms.simplecodes.com'> WTForms Team"]
        check_detection(expected, test_file)

    def test_should_not_have_trailing_garbage(self):
        test_file = self.get_test_loc('copyrights/with_trailing_words.js')
        expected = [
            'Copyright 2012-2015 The Dojo Foundation',
            'Copyright 2009-2015 Jeremy Ashkenas, DocumentCloud and Investigative Reporters',
            'Copyright 2009-2015 Jeremy Ashkenas, DocumentCloud and Investigative Reporters',
            'Copyright 2009-2015 Jeremy Ashkenas, DocumentCloud and Investigative Reporters',
            '(c) Varun Malhotra 2013 Source Code',
            'Copyright 2015, MYCO',
            'Copyright 2015, MYCO',
            'Copyright 2013, MYCO',
        ]
        check_detection(expected, test_file)

    def test_should_not_have_trailing_available(self):
        test_file = self.get_test_loc('copyrights/hostapd_trailing_available.c')
        expected = ['Copyright (c) 2004-2005, Jouni Malinen <jkmaline@cc.hut.fi>']
        check_detection(expected, test_file)

    def test_with_dots_and_all_lowercase_on_multilines(self):
        test_lines = ['Copyright . 2008 company name, inc.',
                      '  Change: Add functions', ]
        expected = ['Copyright . 2008 company name, inc.']
        check_detection(expected, test_lines)

    def test_with_dots_and_all_lowercase_on_single_line(self):
        test_lines = ['Copyright . 2008 foo name, inc.']
        expected = ['Copyright . 2008 foo name, inc.']
        check_detection(expected, test_lines)

    def test_copy_copy_by_name3(self):
        test_lines = ['Copyright (c) by 2007  Joachim Foerster <JOFT@gmx.de>']
        expected = ['Copyright (c) by 2007 Joachim Foerster <JOFT@gmx.de>']
        check_detection(expected, test_lines)

    def test_rimini(self):
        test_file = self.get_test_loc('copyrights/rimini.c')
        expected = ['(c) Copyright 2000 Paolo Scaffardi, AIRVENT SAM s.p.a - RIMINI(ITALY), arsenio@tin.it']
        check_detection(expected, test_file)

    def test_should_not_be_detected_in_apache_html(self):
        test_file = self.get_test_loc('copyrights/apache_in_html.html')
        expected = []
        check_detection(expected, test_file)

    def test_bv_legal_entity(self):
        test_file = self.get_test_loc('copyrights/bv.txt')
        expected = ['Copyright (c) 2016 HERE Europe B.V.', '(c) HERE 2016']
        check_detection(expected, test_file)

    def test_with_dash_and_dotted_name(self):
        test_lines = ['Copyright 1999, 2000 - D.T.Shield.']
        expected = ['Copyright 1999, 2000 - D.T.Shield.']
        check_detection(expected, test_lines)

    def test_with_sign_dash_and_dotted_name(self):
        test_lines = ['Copyright (c) 1999, 2000 - D.T.Shield.']
        expected = ['Copyright (c) 1999, 2000 - D.T.Shield.']
        check_detection(expected, test_lines)

    def test_with_sign_year_comp_and_auth(self):
        test_lines = ['Copyright (c) 2012-2016, Project contributors']
        expected = ['Copyright (c) 2012-2016, Project contributors']
        check_detection(expected, test_lines)

    def test_with_year_comp_and_auth(self):
        test_lines = ['Copyright 2012-2016, Project contributors']
        expected = ['Copyright 2012-2016, Project contributors']
        check_detection(expected, test_lines)

    def test_with_year_noun_junk_auth_noun_and_auth(self):
        test_lines = ['Copyright 2007-2010 the original author or authors.']
        expected = ['Copyright 2007-2010 the original author or authors.']
        check_detection(expected, test_lines)

    def test_with_sign_year_noun_junk_auth_noun_and_auth(self):
        test_lines = ['Copyright (c) 2007-2010 the original author or authors.']
        expected = ['Copyright (c) 2007-2010 the original author or authors.']
        check_detection(expected, test_lines)

    def test_byten_c_exactly(self):
        test_lines = ['... don’t fit into your fixed-size buffer.\nByten ( c )\nExactly n bytes. If the']
        expected = []
        check_detection(expected, test_lines)

    def test_should_not_be_detected_in_junk_strings_with_year_prefix(self):
        test_file = self.get_test_loc('copyrights/access_strings.txt')
        expected = []
        check_detection(expected, test_file)

    def test_chromium_authors(self):
        test_lines = ['© 2017 The Chromium Authors']
        expected = ['(c) 2017 The Chromium Authors']
        check_detection(expected, test_lines)

    def test_rim(self):
        test_lines = ['Copyright (C) Research In Motion Limited 2010. All rights reserved.']
        expected = ['Copyright (c) Research In Motion Limited 2010.']
        check_detection(expected, test_lines)

    def test_sinica(self):
        test_lines = '''
            #  Copyright (c) 1999 Computer Systems and Communication Lab,
            #                    Institute of Information Science, Academia Sinica.

            some junk
        '''.splitlines()
        expected = ['Copyright (c) 1999 Computer Systems and Communication Lab, Institute of Information Science, Academia Sinica.']

        check_detection(expected, test_lines)

    def test_copr1(self):
        test_lines = ['Copyright or Copr. CNRS']
        expected = ['Copyright or Copr. CNRS']
        check_detection(expected, test_lines)

    def test_copr2(self):
        test_lines = ['Copyright  or Copr. 2006 INRIA - CIRAD - INRA']
        expected = ['Copr. 2006 INRIA - CIRAD - INRA']
        check_detection(expected, test_lines)

    @expectedFailure
    def test_copr2_correct(self):
        test_lines = ['Copyright  or Copr. 2006 INRIA - CIRAD - INRA']
        expected = ['Copyright or Copr. 2006 INRIA - CIRAD - INRA']
        check_detection(expected, test_lines)

    def test_copr3(self):
        test_lines = ['Copyright or © or Copr. SSD Research Team 2011']
        expected = ['Copr. SSD Research Team 2011']
        check_detection(expected, test_lines)

    @expectedFailure
    def test_copr3_correct(self):
        test_lines = ['Copyright or © or Copr. SSD Research Team 2011']
        expected = ['Copyright or (c) or Copr. SSD Research Team 2011']
        check_detection(expected, test_lines)

    def test_copr4(self):
        test_lines = ["(C) Copr. 1986-92 Numerical Recipes Software i9k''3"]
        expected = ['(c) Copr. 1986-92 Numerical Recipes Software']
        check_detection(expected, test_lines)

    def test_copr5(self):
        test_lines = ['Copyright or Copr. Mines Paristech, France - Mark NOBLE, Alexandrine GESRET']
        expected = ['Copr. Mines Paristech, France - Mark NOBLE']
        check_detection(expected, test_lines)

    @expectedFailure
    def test_copr5_correct(self):
        test_lines = ['Copyright or Copr. Mines Paristech, France - Mark NOBLE, Alexandrine GESRET']
        expected = ['Copyright or Copr. Mines Paristech, France - Mark NOBLE, Alexandrine GESRET']
        check_detection(expected, test_lines)

    def test_oracle(self):
        test_lines = ['Copyright (c) 1997-2015 Oracle and/or its affiliates. All rights reserved.']
        expected = ['Copyright (c) 1997-2015 Oracle and/or its affiliates.']
        check_detection(expected, test_lines)

    def test_windows(self):
        test_lines = ['This release supports NT-based Windows releases like Windows 2000 SP4, Windows XP, and Windows 2003.']
        expected = []
        check_detection(expected, test_lines)

    def test_binary_sql_server(self):
        test_lines = ['2005charchar? 7 DDLSQL Server 2005smalldatetimedatetimeLDDDDDD7']
        expected = []
        check_detection(expected, test_lines)

    def test_with_example_com_url(self):
        test_lines = ['"domain": function(c) { assert.equal(c.domain, "example.com") },']
        expected = []
        check_detection(expected, test_lines)

    def test_various(self):
        test_lines = '''
            libwmf (<libwmf/api.h>): library for wmf conversion
            Copyright (C) 2000 - various; see CREDITS, ChangeLog, and sources
            The libwmf Library is free software; you can redistribute it and/or
        '''.splitlines(False)
        expected = ['Copyright (c) 2000 - various']  # ; see CREDITS, ChangeLog, and sources
        check_detection(expected, test_lines)

    def test_natural_docs(self):
        test_lines = '''
            // Search script generated by doxygen
            // Copyright (C) 2009 by Dimitri van Heesch.

            // The code in this file is loosly based on main.js, part of Natural Docs,
            // which is Copyright (C) 2003-2008 Greg Valure
            // Natural Docs is licensed under the GPL.
        '''.splitlines(False)
        expected = [
            u'Copyright (c) 2009 by Dimitri van Heesch.',
            u'Copyright (c) 2003-2008 Greg Valure'
        ]
        check_detection(expected, test_lines)

    def test_and_authors_mixed(self):
        test_lines = '''
             * Copyright (c) 1998 Softweyr LLC.  All rights reserved.
             *
             * strtok_r, from Berkeley strtok
             * Oct 13, 1998 by Wes Peters <wes@softweyr.com>
             *
             * Copyright (c) 1988, 1993
             *  The Regents of the University of California.  All rights reserved.
        '''.splitlines(False)
        expected = [
            u'Copyright (c) 1998 Softweyr LLC.',
            u'Copyright (c) 1988, 1993 The Regents of the University of California.'
        ]
        check_detection(expected, test_lines)

    def test_word_in_html(self):
        test_lines = '''
            <td width="40%" align="left">Copyright &copy; 2010 Nokia Corporation and/or its subsidiary(-ies)</td>
        '''.splitlines(False)
        expected = [
            u'Copyright (c) 2010 Nokia Corporation and/or its subsidiary(-ies)',
        ]
        check_detection(expected, test_lines)

    def test_with_date_in_angle_brackets(self):
        test_lines = '''
         * Copyright (C) <2013>, GENIVI Alliance, Inc.
         * Author: bj@open-rnd.pl
        '''.splitlines(False)
        expected = [
            u'Copyright (c) <2013> , GENIVI Alliance, Inc.',
        ]
        check_detection(expected, test_lines, what='copyrights')
        expected = [
            u'bj@open-rnd.pl',
        ]
        check_detection(expected, test_lines, what='authors')

    def test_with_zoo(self):
        test_lines = '''
             *  Download Upload Messaging Manager
             *
             *  Copyright (C) 2012-2013  Open-RnD Sp. z o.o. All rights reserved.
             * @verbatim
        '''.splitlines(False)
        expected = [
            u'Copyright (c) 2012-2013 Open-RnD Sp.',
        ]
        check_detection(expected, test_lines, what='copyrights')

    def test_man_page(self):
        test_lines = '''COPYRIGHT
        Copyright \(co 2001-2017 Free Software Foundation, Inc., and others.
            print "Copyright \\(co ". $args{'copyright'} . ".\n";
        '''.splitlines(False)
        expected = [
            'Copyright 2001-2017 Free Software Foundation, Inc., and others.'
        ]
        check_detection(expected, test_lines, what='copyrights')

        expected = [
            'Free Software Foundation, Inc., and others.'
        ]
        check_detection(expected, test_lines, what='holders')

    def test_is_not_mixed_with_authors(self):
        test_lines = '''
         * Copyright (C) 2000-2012 Free Software Foundation, Inc.
         * Author: Nikos Mavrogiannopoulos
        '''.splitlines(False)
        expected = [
            'Copyright (c) 2000-2012 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_lines, what='copyrights')

        expected = [
            'Nikos Mavrogiannopoulos'
        ]
        check_detection(expected, test_lines, what='authors')

    def test_ibm_and_authors_are_detected(self):
        test_lines = '''
         * Copyright IBM, Corp. 2007
         *
         * Authors:
         *  Anthony Liguori   <aliguori@us.ibm.com>
        '''.splitlines(False)
        expected = [
            'Copyright IBM, Corp. 2007',
        ]
        check_detection(expected, test_lines, what='copyrights')

        expected = [
            'Anthony Liguori <aliguori@us.ibm.com>'
        ]
        check_detection(expected, test_lines, what='authors')

        expected = [
            'IBM, Corp.'
        ]
        check_detection(expected, test_lines, what='holders')

    def test_germany(self):
        test_lines = '''
         * Copyright (C) 2011
         * Bardenheuer GmbH, Munich and Bundesdruckerei GmbH, Berlin
        '''.splitlines(False)
        expected = [
            u'Bardenheuer GmbH, Munich and Bundesdruckerei GmbH',
        ]
        check_detection(expected, test_lines, what='holders')

    @expectedFailure
    def test_germany_should_detect_trailing_city(self):
        test_lines = '''
         * Copyright (C) 2011
         * Bardenheuer GmbH, Munich and Bundesdruckerei GmbH, Berlin
        '''.splitlines(False)
        expected = [
            u'Bardenheuer GmbH, Munich and Bundesdruckerei GmbH, Berlin',
        ]
        check_detection(expected, test_lines, what='holders')

    def test_does_not_detect_junk_in_texinfo(self):
        test_lines = '''
          \DeclareUnicodeCharacter{00A8}{\"{ }}
          \DeclareUnicodeCharacter{00A9}{\copyright}
          \DeclareUnicodeCharacter{00AA}{\ordf}
        '''.splitlines(False)
        expected = [
        ]
        check_detection(expected, test_lines, what='copyrights')

    def test_author_does_not_report_trailing_coma(self):
        test_lines = '''
            # Written by Gordon Matzigkeit, 1996
        '''.splitlines(False)
        expected = [
            u'Gordon Matzigkeit'
        ]
        check_detection(expected, test_lines, what='authors')

    def test_author_does_not_report_trailing_junk_and_incorrect_authors(self):
        test_lines = '''
            # Original author: Mohit Agarwal.
            # Send bug reports and any other correspondence to bug-gnulib@gnu.org.

            This is an 128-bit block cipher developed by Mitsubishi and NTT. It
            is one of the approved ciphers of the European NESSIE and Japanese

            "PO-Revision-Date: 2013-06-13 19:56+0200\n"
            "Last-Translator: Benno Schulenberg <benno@vertaalt.nl>\n"
            "Language-Team: Dutch <vertaling@vrijschrift.org>\n"
            "Language: nl\n"

        /* Need to cast, because on Solaris 11 2011-10, Mac OS X 10.5, IRIX 6.5
           and FreeBSD 6.4 the second parameter is int.  On Solaris 11
           2011-10, the first parameter is not const.  */

        '''.splitlines(False)
        expected = [
            'Mohit Agarwal.',
            'Mitsubishi and NTT.'
        ]
        check_detection(expected, test_lines, what='authors')

    def test_assembly_data(self):
        test_lines = '''
        [assembly: AssemblyProduct("")]
        [assembly: AssemblyCopyright("(c) 2004 by Henrik Ravn")]
        [assembly: AssemblyTrademark("")]
        [assembly: AssemblyCulture("")]
        '''.splitlines(False)
        expected = [
            '(c) 2004 by Henrik Ravn'
        ]
        check_detection(expected, test_lines, what='copyrights')

    def test_author_does_not_report_incorrect_junk(self):
        test_lines = '''
        by the Contributor ("Commercial Contributor")
        by an Indemnified Contributor
        '''.splitlines(False)
        expected = [
        ]
        check_detection(expected, test_lines, what='authors')

    def test_does_not_truncate_last_name(self):
        test_lines = '''
            /* Copyright 2014, Kenneth MacKay. Licensed under the BSD 2-clause license. */
        '''.splitlines(False)
        expected = [
            'Copyright 2014, Kenneth MacKay.'
        ]
        check_detection(expected, test_lines, what='copyrights')

    @expectedFailure
    def test_with_leading_date_andtrailing_plus(self):
        test_lines = '''
        * 2004+ Copyright (c) Evgeniy Polyakov <zbr@ioremap.net>
          * All rights reserved.
        '''.splitlines(False)
        expected = [
            '2004+ Copyright (c) Evgeniy Polyakov <zbr@ioremap.net>'
        ]
        check_detection(expected, test_lines, what='copyrights')

