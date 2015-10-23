# -*- coding: utf-8 -*-
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

import os.path
from unittest.case import expectedFailure

from commoncode.testcase import FileBasedTesting
from cluecode_assert_utils import check_detection
import cluecode.copyrights


class TestTextPreparation(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_strip_numbers(self):
        a = 'Python 2.6.6 (r266:84297, Aug 24 2010, 18:46:32) [MSC v.1500 32 bit (Intel)] on win32'
        expected = u'Python 2.6.6 (r266:84297, Aug 2010, 18:46:32) [MSC v.1500 bit (Intel)] on win32'
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


class TestCopyrightDetector(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_copyright_detect(self):
        location = self.get_test_loc('copyrights/copyright_essential_smoke-ibm_c.c')
        expected = [
            u'Copyright IBM and others (c) 2008',
            u'Copyright Eclipse, IBM and others (c) 2008'
        ]
        copyrights, _, _, _ = cluecode.copyrights.detect(location)
        assert expected == copyrights


class TestCopyrightDetection(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_company_name_in_java(self):
        test_file = self.get_test_loc('copyrights/company_name_in_java-9_java.java')
        expected = [
            u'Copyright (c) 2008-2011 Company Name Incorporated',
        ]
        check_detection(expected, test_file)

    def test_copyright_03e16f6c_0(self):
        test_file = self.get_test_loc('copyrights/copyright_03e16f6c_0-e_f_c.0')
        expected = [
            u'Copyright (c) 1997 Microsoft Corp.',
            u'Copyright (c) 1997 Microsoft Corp.',
            u'(c) 1997 Microsoft',
        ]
        check_detection(expected, test_file,
                        expected_in_results=True,
                        results_in_expected=False)

    def test_copyright_3a3b02ce_0(self):
        # this is a certificate and the actual copyright holder is not clear:
        # could be either Wisekey or OISTE Foundation.
        test_file = self.get_test_loc('copyrights/copyright_3a3b02ce_0-a_b_ce.0')
        expected = [
            u'Copyright (c) 2005',
            u'Copyright (c) 2005',
        ]
        check_detection(expected, test_file,
                        expected_in_results=True,
                        results_in_expected=False)

    def test_copyright_ABC_cpp(self):
        test_file = self.get_test_loc('copyrights/copyright_ABC_cpp-Case_cpp.cpp')
        expected = [
            u'Copyright (c) ABC Company',
        ]
        check_detection(expected, test_file)

    def test_copyright_ABC_file_cpp(self):
        test_file = self.get_test_loc('copyrights/copyright_ABC_file_cpp-File_cpp.cpp')
        expected = [
            u'Copyright (c) ABC Company',
        ]
        check_detection(expected, test_file)

    def test_copyright_false_positive_in_c(self):
        test_file = self.get_test_loc('copyrights/copyright_false_positive_in_c-false_positives_c.c')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_false_positive_in_js(self):
        test_file = self.get_test_loc('copyrights/copyright_false_positive_in_js-editor_beta_de_js.js')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_false_positive_in_license(self):
        test_file = self.get_test_loc('copyrights/copyright_false_positive_in_license-LICENSE')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_heunrich_c(self):
        test_file = self.get_test_loc('copyrights/copyright_heunrich_c-c.c')
        expected = [
            u'Copyright (c) 2000 HEUNRICH HERTZ INSTITUTE',
        ]
        check_detection(expected, test_file)

    def test_copyright_isc(self):
        test_file = self.get_test_loc('copyrights/copyright_isc-c.c')
        expected = [
            u'Copyright (c) 1998-2000 The Internet Software Consortium.',
        ]
        check_detection(expected, test_file)

    def test_copyright_json_phps_html_incorrect(self):
        test_file = self.get_test_loc('copyrights/copyright_json_phps_html_incorrect-JSON_phps_html.html')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_no_copyright_in_class_file_1(self):
        test_file = self.get_test_loc('copyrights/copyright_no_copyright_in_class_file_1-PersistentArrayHolder_class.class')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_sample_py(self):
        test_file = self.get_test_loc('copyrights/copyright_sample_py-py.py')
        expected = [
            u'COPYRIGHT 2006',
        ]
        check_detection(expected, test_file)

    def test_copyright_abc(self):
        test_file = self.get_test_loc('copyrights/copyright_abc')
        expected = [
            u'Copyright (c) 2006 abc.org',
        ]
        check_detection(expected, test_file)

    def test_copyright_abc_loss_of_holder_c(self):
        test_file = self.get_test_loc('copyrights/copyright_abc_loss_of_holder_c-c.c')
        expected = [
            u'copyright abc 2001',
        ]
        check_detection(expected, test_file)

    def test_copyright_abiword_common_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_abiword_common_copyright-abiword_common_copyright.copyright')
        expected = [
            u'Copyright (c) 1998- AbiSource, Inc.',
            u'Copyright (c) 2009 Masayuki Hatta',
            u'Copyright (c) 2009 Patrik Fimml <patrik@fimml.at>',
        ]
        check_detection(expected, test_file)

    def test_copyright_acme_c(self):
        test_file = self.get_test_loc('copyrights/copyright_acme_c-c.c')
        expected = [
            u'Copyright (c) 2000 ACME, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_activefieldattribute_cs(self):
        test_file = self.get_test_loc('copyrights/copyright_activefieldattribute_cs-ActiveFieldAttribute_cs.cs')
        expected = [
            u'Web Applications Copyright 2009 - Thomas Hansen thomas@ra-ajax.org.',
        ]
        check_detection(expected, test_file)

    def test_copyright_addr_c(self):
        test_file = self.get_test_loc('copyrights/copyright_addr_c-addr_c.c')
        expected = [
            u'Copyright 1999 Cornell University.',
            u'Copyright 2000 Jon Doe.',
        ]
        check_detection(expected, test_file)

    def test_copyright_apostrophe_in_name(self):
        test_file = self.get_test_loc('copyrights/copyright_with_apos.txt')
        expected = [
            u"Copyright Marco d'Itri <md@Linux.IT>",
            u"Copyright Marco d'Itri",
        ]
        check_detection(expected, test_file)

    def test_copyright_adler_inflate_c(self):
        test_file = self.get_test_loc('copyrights/copyright_adler_inflate_c-inflate_c.c')
        expected = [
            u'Not copyrighted 1992 by Mark Adler',
        ]
        check_detection(expected, test_file)

    def test_copyright_adobe_flashplugin_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_adobe_flashplugin_copyright_label-adobe_flashplugin_copyright_label.label')
        expected = [
            u'Copyright (c) 1996 - 2008. Adobe Systems Incorporated',
            u'(c) 2001-2009, Takuo KITAME, Bart Martens, and Canonical, LTD',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_copyright_aleal(self):
        test_file = self.get_test_loc('copyrights/copyright_aleal-c.c')
        expected = [
            u'copyright (c) 2006 by aleal',
        ]
        check_detection(expected, test_file)

    def test_copyright_andre_darcy(self):
        test_file = self.get_test_loc('copyrights/copyright_andre_darcy-c.c')
        expected = [
            u'Copyright (c) 1995, Pascal Andre (andre@via.ecp.fr).',
            u"copyright 1997, 1998, 1999 by D'Arcy J.M. Cain (darcy@druid.net)",
        ]
        check_detection(expected, test_file)

    def test_copyright_android_c(self):
        test_file = self.get_test_loc('copyrights/copyright_android_c-c.c')
        expected = [
            u'Copyright (c) 2009 The Android Open Source Project',
            u'Copyright 2003-2005 Colin Percival',
        ]
        check_detection(expected, test_file)

    def test_copyright_apache2_debian_trailing_name_missed(self):
        test_file = self.get_test_loc('copyrights/copyright_apache2_debian_trailing_name_missed-apache_copyright_label.label')
        expected = [
            u'copyright Steinar H. Gunderson <sgunderson@bigfoot.com> and Knut Auvor Grythe <knut@auvor.no>',
            u'Copyright (c) 1996-1997 Cisco Systems, Inc.',
            u'Copyright (c) Ian F. Darwin',
            u'Copyright (c) Ian F. Darwin 1986, 1987, 1989, 1990, 1991, 1992, 1994, 1995.',
            u'copyright 1992 by Eric Haines, erich@eye.com',
            u'Copyright (c) 1995, Board of Trustees of the University of Illinois',
            u'Copyright (c) 1994, Jeff Hostetler, Spyglass, Inc.',
            u'Copyright (c) 1993, 1994 by Carnegie Mellon University',
            u'Copyright (c) 1991 Bell Communications Research, Inc.',
            u'(c) Copyright 1993,1994 by Carnegie Mellon University',
            u'Copyright (c) 1991 Bell Communications Research, Inc.',
            u'Copyright RSA Data Security, Inc.',
            u'Copyright (c) 1991-2, RSA Data Security, Inc.',
            u'Copyright RSA Data Security, Inc.',
            u'Copyright (c) 1991-2, RSA Data Security, Inc.',
            u'copyright RSA Data Security, Inc.',
            u'Copyright (c) 1991-2, RSA Data Security, Inc.',
            u'copyright RSA Data Security, Inc.',
            u'Copyright (c) 1991-2, RSA Data Security, Inc.',
            u'Copyright (c) 2000-2002 The Apache Software Foundation',
            u'copyright RSA Data Security, Inc.',
            u'Copyright (c) 1990-2, RSA Data Security, Inc.',
            u'Copyright 1991 by the Massachusetts Institute of Technology',
            u'Copyright 1991 by the Massachusetts Institute of Technology',
            u'Copyright (c) 1997-2001 University of Cambridge',
            u'copyright by the University of Cambridge, England.',
            u'Copyright (c) Zeus Technology Limited 1996.',
            u'Copyright (c) 1998, 1999, 2000 Thai Open Source Software Center Ltd and Clark Cooper',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_copyright_apache_notice(self):
        test_file = self.get_test_loc('copyrights/copyright_apache_notice-NOTICE')
        expected = [
            u'Copyright 1999-2006 The Apache Software Foundation',
            u'Copyright 1999-2006 The Apache Software Foundation',
            u'Copyright 2001-2003,2006 The Apache Software Foundation.',
            u'copyright (c) 2000 World Wide Web Consortium',
        ]
        check_detection(expected, test_file)

    def test_copyright_aptitude_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_aptitude_copyright_label-aptitude_copyright_label.label')
        expected = [
            u'Copyright 1999-2005 Daniel Burrows <dburrows@debian.org>',
        ]
        check_detection(expected, test_file)

    def test_copyright_atheros_spanning_lines(self):
        test_file = self.get_test_loc('copyrights/copyright_atheros_spanning_lines-py.py')
        expected = [
            u'Copyright (c) 2000 Atheros Communications, Inc.',
            u'Copyright (c) 2001 Atheros Communications, Inc.',
            u'Copyright (c) 1994-1997 by Intel Corporation.',
        ]
        check_detection(expected, test_file)

    def test_copyright_att_in_c(self):
        test_file = self.get_test_loc('copyrights/copyright_att_in_c-9_c.c')
        expected = [
            u'Copyright (c) 1991 by AT&T.',
        ]
        check_detection(expected, test_file)

    def test_copyright_audio_c(self):
        test_file = self.get_test_loc('copyrights/copyright_audio_c-c.c')
        expected = [
            u'copyright (c) 1995, AudioCodes, DSP Group, France Telecom, Universite de Sherbrooke.',
        ]
        check_detection(expected, test_file)

    def test_copyright_babkin_txt(self):
        test_file = self.get_test_loc('copyrights/copyright_babkin_txt.txt')
        expected = [
            u'Copyright (c) North',
            u'Copyright (c) South',
            u'Copyright (c) 2001 by the TTF2PT1 project',
            u'Copyright (c) 2001 by Sergey Babkin',
        ]
        check_detection(expected, test_file)

    def test_copyright_blender_debian(self):
        test_file = self.get_test_loc('copyrights/copyright_blender_debian-blender_copyright.copyright')
        expected = [
            u'Copyright (c) 2002-2008 Blender Foundation',
            u'Copyright (c) 2004-2005 Masayuki Hatta <mhatta@debian.org>',
            u'(c) 2005-2007 Florian Ernst <florian@debian.org>',
            u'(c) 2007-2008 Cyril Brulebois <kibi@debian.org>',
        ]
        check_detection(expected, test_file)

    def test_copyright_blue_sky_dash_in_name(self):
        test_file = self.get_test_loc('copyrights/copyright_blue_sky_dash_in_name-c.c')
        expected = [
            u'Copyright (c) 1995, 1996 - Blue Sky Software Corp. -',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_copyright_bouncy_license(self):
        test_file = self.get_test_loc('copyrights/copyright_bouncy_license-LICENSE')
        expected = [
            u'Copyright (c) 2000-2005 The Legion Of The Bouncy Castle',
        ]
        check_detection(expected, test_file)

    def test_copyright_bouncy_notice(self):
        test_file = self.get_test_loc('copyrights/copyright_bouncy_notice-9_NOTICE')
        expected = [
            u'Copyright (c) 2000-2005 The Legion Of The Bouncy Castle',
        ]
        check_detection(expected, test_file)

    def test_copyright_btt_plot1_py(self):
        test_file = self.get_test_loc('copyrights/copyright_btt_plot1_py-btt_plot_py.py')
        expected = [
            u'(c) Copyright 2009 Hewlett-Packard Development Company',
        ]
        check_detection(expected, test_file)

    def test_copyright_camelcase_bug_br_fcc_thread_psipstack_c(self):
        test_file = self.get_test_loc('copyrights/copyright_camelcase_bug_br_fcc_thread_psipstack_c-br_fcc_thread_psipstack_c.c')
        expected = [
            u'Copyright 2010-2011 by BitRouter',
        ]
        check_detection(expected, test_file)

    def test_copyright_ccube_txt(self):
        test_file = self.get_test_loc('copyrights/copyright_ccube_txt.txt')
        expected = [
            u'Copyright (c) 2001 C-Cube Microsystems.',
        ]
        check_detection(expected, test_file)

    def test_copyright_cedrik_java(self):
        test_file = self.get_test_loc('copyrights/copyright_cedrik_java-java.java')
        expected = [
            u'copyright (c) 2005-2006 Cedrik LIME',
        ]
        check_detection(expected, test_file,
                        expected_in_results=True,
                        results_in_expected=False)

    def test_copyright_cern(self):
        test_file = self.get_test_loc('copyrights/copyright_cern-TestMatrix_D_java.java')
        expected = [
            u'Copyright 1999 CERN - European Organization for Nuclear Research.',
        ]
        check_detection(expected, test_file)

    def test_copyright_cern_matrix2d_java(self):
        test_file = self.get_test_loc('copyrights/copyright_cern_matrix2d_java-TestMatrix_D_java.java')
        expected = [
            u'Copyright 1999 CERN - European Organization for Nuclear Research.',
            u'Copyright (c) 1998 Company PIERSOL Engineering Inc.',
            u'Copyright (c) 1998 Company PIERSOL Engineering Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_chameleon_assembly(self):
        test_file = self.get_test_loc('copyrights/copyright_chameleon_assembly-9_9_setjmp_S.S')
        expected = [
            u'Copyright Chameleon Systems, 1999',
        ]
        check_detection(expected, test_file)

    def test_copyright_co_cust(self):
        test_file = self.get_test_loc('copyrights/copyright_co_cust-copyright_java.java')
        expected = [
            u'Copyright (c) 2009 Company Customer Identity Hidden',
        ]
        check_detection(expected, test_file)

    def test_copyright_colin_android(self):
        test_file = self.get_test_loc('copyrights/copyright_colin_android-bsdiff_c.c')
        expected = [
            u'Copyright (c) 2009 The Android Open Source Project',
            u'Copyright 2003-2005 Colin Percival',
        ]
        check_detection(expected, test_file)

    def test_copyright_company_in_txt(self):
        test_file = self.get_test_loc('copyrights/copyright_company_in_txt-9.txt')
        expected = [
            u'Copyright (c) 2008-2011 Company Name Incorporated',
        ]
        check_detection(expected, test_file)

    def test_copyright_complex_4_line_statement_in_text(self):
        test_file = self.get_test_loc('copyrights/copyright_complex_4_line_statement_in_text-9.txt')
        expected = [
            u'Copyright 2002 Jonas Borgstrom <jonas@codefactory.se> 2002 Daniel Lundin <daniel@codefactory.se> 2002 CodeFactory AB',
            u'Copyright (c) 1994 The Regents of the University of California',
        ]
        check_detection(expected, test_file)

    def test_copyright_complex_notice(self):
        test_file = self.get_test_loc('copyrights/copyright_complex_notice-NOTICE')
        expected = [
            u'Copyright (c) 2003, Steven G. Kargl',
            u'Copyright (c) 2003 Mike Barcroft <mike@FreeBSD.org>',
            u'Copyright (c) 2002, 2003 David Schultz <das@FreeBSD.ORG>',
            u'Copyright (c) 2003 David Schultz <das@FreeBSD.ORG>',
            u'Copyright (c) 2004 David Schultz <das@FreeBSD.ORG>',
            u'Copyright (c) 2004-2005 David Schultz <das@FreeBSD.ORG>',
            u'Copyright (c) 2005 David Schultz <das@FreeBSD.ORG>',
            u'Copyright (c) 2002 David Schultz <das@FreeBSD.ORG>',
            u'Copyright (c) 2004 Stefan Farfeleder',
            u'Copyright (c) 2003 Dag-Erling Coidan Smrgrav',
            u'Copyright (c) 1996 The NetBSD Foundation, Inc.',
            u'Copyright (c) 1985, 1993',
            u'Copyright (c) 1988, 1993',
            u'Copyright (c) 1992, 1993 The Regents of the University of California.',
            u'Copyright (c) 1993,94 Winning Strategies, Inc.',
            u'Copyright (c) 1994 Winning Strategies, Inc.',
            u'Copyright (c) 1993 by Sun Microsystems, Inc.',
            u'Copyright (c) 1993 by Sun Microsystems, Inc.',
            u'Copyright (c) 1993 by Sun Microsystems, Inc.',
            u'Copyright (c) 2004 by Sun Microsystems, Inc.',
            u'Copyright (c) 2004 Stefan Farfeleder',
            u'Copyright (c) 2004 David Schultz <das@FreeBSD.org>',
            u'Copyright (c) 2004, 2005 David Schultz <das@FreeBSD.org>',
            u'Copyright (c) 2003 Mike Barcroft <mike@FreeBSD.org>',
            u'Copyright (c) 2005 David Schultz <das@FreeBSD.org>',
            u'Copyright (c) 2003, Steven G. Kargl',
            u'Copyright (c) 1991 The Regents of the University of California.',
        ]
        check_detection(expected, test_file)

    def test_copyright_complex_notice_sun_microsystems_on_multiple_lines(self):
        test_file = self.get_test_loc('copyrights/copyright_complex_notice_sun_microsystems_on_multiple_lines-NOTICE')
        expected = [
            u'Copyright 1999-2006 The Apache Software Foundation',
            u'copyright (c) 1999-2002, Lotus Development',
            u'copyright (c) 2001-2002, Sun Microsystems.',
            u'copyright (c) 2003, IBM Corporation., http://www.ibm.com.',
            u'copyright (c) 1999, IBM Corporation., http://www.ibm.com.',
            u'copyright (c) 1999, Sun Microsystems.',
            u'copyright (c) 1999, IBM Corporation., http://www.ibm.com.',
            u'copyright (c) 1999, Sun Microsystems.',
        ]
        check_detection(expected, test_file)

    def test_copyright_config(self):
        test_file = self.get_test_loc('copyrights/copyright_config-config_guess.guess')
        expected = [
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_config1_guess(self):
        test_file = self.get_test_loc('copyrights/copyright_config1_guess-config_guess.guess')
        expected = [
            u'Copyright (c) 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_copyright_camelcase_br_diagnostics_h(self):
        test_file = self.get_test_loc('copyrights/copyright_copyright_camelcase_br_diagnostics_h-br_diagnostics_h.h')
        expected = [
            u'Copyright 2011 by BitRouter',
        ]
        check_detection(expected, test_file)

    def test_copyright_coreutils_debian(self):
        test_file = self.get_test_loc('copyrights/copyright_coreutils_debian-coreutils_copyright.copyright')
        expected = [
            u'Copyright (c) 2004, 2005, 2006, 2007, 2008 Free Software Foundation, Inc.',
            u'Copyright (c) 1990, 1993, 1994 The Regents of the University of California',
            u'Copyright (c) 2004, 2005, 2006, 2007 Free Software Foundation, Inc.',
            u'Copyright (c) 1989, 1993 The Regents of the University of California',
            u'Copyright (c) 1999-2006 Free Software Foundation, Inc.',
            u'Copyright (c) 1997, 1998, 1999 Colin Plumb',
            u'Copyright (c) 2005, 2006 Free Software Foundation, Inc.',
            u'Copyright (c) 1996-1999 by Internet Software Consortium',
            u'Copyright (c) 2004, 2006, 2007 Free Software Foundation, Inc.',
            u'Copyright (c) 1997-2007 Free Software Foundation, Inc.',
            u'Copyright (c) 1984 David M. Ihnat',
            u'Copyright (c) 1996-2007 Free Software Foundation, Inc.',
            u'Copyright (c) 1994, 1995, 1997, 1998, 1999, 2000 H. Peter Anvin',
            u'Copyright (c) 1997-2005 Free Software Foundation, Inc.',
            u'Copyright (c) 1984 David M. Ihnat',
            u'Copyright (c) 1999-2007 Free Software Foundation, Inc.',
            u'Copyright (c) 1997, 1998, 1999 Colin Plumb',
            u'Copyright 1994-1996, 2000-2008 Free Software Foundation, Inc.',
            u'Copyright (c) 1984-2008 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_dag_c(self):
        test_file = self.get_test_loc('copyrights/copyright_dag_c-s_fabsl_c.c')
        expected = [
            u'Copyright (c) 2003 Dag-Erling Coidan Smrgrav',
        ]
        check_detection(expected, test_file)

    def test_copyright_dag_elring_notice(self):
        test_file = self.get_test_loc('copyrights/copyright_dag_elring_notice-NOTICE')
        expected = [
            u'Copyright (c) 2003 Dag-Erling Codan Smrgrav',
        ]
        check_detection(expected, test_file)

    def test_copyright_dash_in_name(self):
        test_file = self.get_test_loc('copyrights/copyright_dash_in_name-Makefile')
        expected = [
            u'(c) 2011 - Anycompany, LLC',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_copyright_dasher_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_dasher_copyright_label-dasher_copyright_label.label')
        expected = [
            u'Copyright (c) 1998-2008 The Dasher Project',
        ]
        check_detection(expected, test_file)

    def test_copyright_date_range_dahua_in_c(self):
        test_file = self.get_test_loc('copyrights/copyright_date_range_dahua_in_c-c.c')
        expected = [
            u'(c) Copyright 2006 to 2007 Dahua Digital.',
        ]
        check_detection(expected, test_file)

    def test_copyright_date_range_in_c(self):
        test_file = self.get_test_loc('copyrights/copyright_date_range_in_c-c.c')
        expected = [
            u'Copyright (c) ImageSilicon Tech. (2006 - 2007)',
        ]
        check_detection(expected, test_file)

    def test_copyright_date_range_in_c_2(self):
        test_file = self.get_test_loc('copyrights/copyright_date_range_in_c_2-c.c')
        expected = [
            u'(c) Copyright 2005 to 2007 ImageSilicon? Tech.,ltd',
        ]
        check_detection(expected, test_file)

    def test_copyright_debian_archive_keyring_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_debian_archive_keyring_copyright-debian_archive_keyring_copyright.copyright')
        expected = [
            u'Copyright (c) 2006 Michael Vogt <mvo@debian.org>',
        ]
        check_detection(expected, test_file)

    def test_copyright_debian_lib_1(self):
        test_file = self.get_test_loc('copyrights/copyright_debian_lib_1-libmono_cairo_cil_copyright_label.label')
        expected = [
            u'Copyright 2004 The Apache Software Foundation',
            u'Copyright (c) 2001-2005 Novell',
            u'Copyright (c) Microsoft Corporation',
            u'Copyright (c) 2007 James Newton-King',
            u'Copyright (c) 2002-2004 James W. Newkirk , Michael C. Two , Alexei A. Vorontsov , Charlie Poole',
            u'Copyright (c) 2000-2004 Philip A. Craig',
            u'Copyright (c) 2002-2004 James W. Newkirk , Michael C. Two , Alexei A. Vorontsov , Charlie Poole',
            u'Copyright (c) 2000-2004 Philip A. Craig',
            u'Copyright (c) 2007, 2008 LShift Ltd.',
            u'Copyright (c) 2007, 2008 Cohesive Financial Technologies LLC.',
            u'Copyright (c) 2007, 2008 Rabbit Technologies Ltd.',
            u'Copyright (c) 2007, 2008 LShift Ltd. , Cohesive Financial Technologies',  # LLC., and Rabbit Technologies Ltd.',
            u'Copyright (c) 2007, 2008 LShift Ltd. , Cohesive Financial Technologies',  # LLC., and Rabbit Technologies Ltd.',
             u'Copyright (c) 2007 LShift Ltd. , Cohesive Financial Technologies',  # LLC., and Rabbit Technologies Ltd.',
            u'Copyright (c) ???? Simon Mourier <simonm@microsoft.com>',
        ]
        check_detection(expected, test_file)

    def test_copyright_debian_lib_2(self):
        test_file = self.get_test_loc('copyrights/copyright_debian_lib_2-libmono_cairo_cil_copyright.copyright')
        expected = [
            u'Copyright 2004 The Apache Software Foundation',
            u'Copyright (c) 2001-2005 Novell',
            u'Copyright (c) Microsoft Corporation',
            u'Copyright (c) 2007 James Newton-King',
            u'Copyright (c) 2002-2004 James W. Newkirk , Michael C. Two , Alexei A. Vorontsov , Charlie Poole',
            u'Copyright (c) 2000-2004 Philip A. Craig',
            u'Copyright (c) 2002-2004 James W. Newkirk , Michael C. Two , Alexei A. Vorontsov , Charlie Poole',
            u'Copyright (c) 2000-2004 Philip A. Craig',
            u'Copyright (c) 2007, 2008 LShift Ltd.',
            u'Copyright (c) 2007, 2008 Cohesive Financial Technologies LLC.',
            u'Copyright (c) 2007, 2008 Rabbit Technologies Ltd.',
            u'Copyright (c) 2007, 2008 LShift Ltd., Cohesive Financial Technologies LLC.',
            u'Copyright (c) 2007, 2008 LShift Ltd. , Cohesive Financial Technologies',
            u'Copyright (c) 2007 LShift Ltd. , Cohesive Financial Technologies',
            u'Copyright (c) ???? Simon Mourier <simonm@microsoft.com>',
        ]
        check_detection(expected, test_file)

    def test_copyright_debian_lib_3(self):
        test_file = self.get_test_loc('copyrights/copyright_debian_lib_3-libmono_security_cil_copyright.copyright')
        expected = [
            u'Copyright 2004 The Apache Software Foundation',
            u'Copyright (c) 2001-2005 Novell',
            u'Copyright (c) Microsoft Corporation',
            u'Copyright (c) 2007 James Newton-King',
            u'Copyright (c) 2002-2004 James W. Newkirk , Michael C. Two , Alexei A. Vorontsov , Charlie Poole',
            u'Copyright (c) 2000-2004 Philip A. Craig',
            u'Copyright (c) 2002-2004 James W. Newkirk , Michael C. Two , Alexei A. Vorontsov , Charlie Poole',
            u'Copyright (c) 2000-2004 Philip A. Craig',
            u'Copyright (c) 2007, 2008 LShift Ltd.',
            u'Copyright (c) 2007, 2008 Cohesive Financial Technologies LLC.',
            u'Copyright (c) 2007, 2008 Rabbit Technologies Ltd.',
            u'Copyright (c) 2007, 2008 LShift Ltd. , Cohesive Financial Technologies',
            u'Copyright (c) 2007, 2008 LShift Ltd. , Cohesive Financial Technologies',
            u'Copyright (c) 2007 LShift Ltd., Cohesive Financial Technologies LLC., and Rabbit Technologies Ltd.',
            u'Copyright (c) ???? Simon Mourier <simonm@microsoft.com>',
        ]
        check_detection(expected, test_file)

    def test_copyright_debian_multi_names_on_one_line(self):
        test_file = self.get_test_loc('copyrights/copyright_debian_multi_names_on_one_line-libgdata__copyright.copyright')
        expected = [
            u'Copyright 1999-2004 Ximian, Inc. 1999-2005 Novell, Inc.',
            u'copyright 2000-2003 Ximian, Inc. , 2003 Gergo Erdi',
            u'copyright 2000 Eskil Heyn Olsen , 2000 Ximian, Inc.',
            u'copyright 1998 The Free Software Foundation , 2000 Ximian, Inc.',
            u'copyright 1998-2005 The OpenLDAP Foundation',
            u'Copyright 1999-2003 The OpenLDAP Foundation , Redwood City, California',
            u'Copyright 1999-2000 Eric Busboom , The Software Studio (http://www.softwarestudio.org) 2001 Critical Path Authors',
            u'(c) Copyright 1996 Apple Computer, Inc. , AT&T Corp., International Business Machines Corporation and Siemens Rolm Communications Inc.',
            u'Copyright (c) 1997 Theo de Raadt',
            u'copyright 2000 Andrea Campi',
            u'copyright 2002 Andrea Campi',
            u'copyright 2003 Andrea Campi',
            u'Copyright 2002 Jonas Borgstrom <jonas@codefactory.se> 2002 Daniel Lundin <daniel@codefactory.se> 2002 CodeFactory AB',
            u'copyright 1996 Apple Computer, Inc. , AT&T Corp. , International Business Machines Corporation and Siemens Rolm Communications Inc.',
            u'copyright 1986-2000 Hiram Clawson',
            u'copyright 1997 Theo de Raadt',
            u'Copyright (c) 1996-2002 Sleepycat Software',
            u'Copyright (c) 1990, 1993, 1994, 1995, 1996 Keith Bostic',
            u'Copyright (c) 1990, 1993, 1994, 1995 The Regents of the University of California',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_copyright_dionysos_c(self):
        test_file = self.get_test_loc('copyrights/copyright_dionysos_c-c.c')
        expected = [
            u'COPYRIGHT (c) 2006 - 2009 DIONYSOS',
            u'COPYRIGHT (c) ADIONYSOS 2006 - 2009',
            u'COPYRIGHT (c) ADIONYSOS2 2006',
            u'COPYRIGHT (c) MyCompany 2006 - 2009',
            u'COPYRIGHT (c) 2006 MyCompany2',
            u'COPYRIGHT (c) 2024 DIONYSOS2',
            u'copyright (c) 2006 - 2009 DIONYSOS',
            u'copyright (c) ADIONYSOS 2006 - 2009',
            u'copyright (c) ADIONYSOS2 2006',
            u'copyright (c) MyCompany 2006 - 2009',
            u'copyright (c) 2006 MyCompany2',
            u'copyright (c) 2024 DIONYSOS2',
        ]
        check_detection(expected, test_file)

    def test_copyright_disclaimed(self):
        test_file = self.get_test_loc('copyrights/copyright_disclaimed-c.c')
        expected = [
            u'Copyright disclaimed 2003 by Andrew Clarke',
        ]
        check_detection(expected, test_file)

    def test_copyright_djvulibre_desktop_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_djvulibre_desktop_copyright-djvulibre_desktop_copyright.copyright')
        expected = [
            u'Copyright (c) 2002 Leon Bottou and Yann Le Cun',
            u'Copyright (c) 2001 AT&T',
            u'Copyright (c) 1999-2001 LizardTech, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_docbook_xsl_doc_html_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_docbook_xsl_doc_html_copyright-docbook_xsl_doc_html_copyright.copyright')
        expected = [
            u'Copyright (c) 1999-2007 Norman Walsh',
            u'Copyright (c) 2003 Jiri Kosek',
            u'Copyright (c) 2004-2007 Steve Ball',
            u'Copyright (c) 2005-2008 The DocBook Project',
        ]
        check_detection(expected, test_file)

    def test_copyright_drand48_c(self):
        test_file = self.get_test_loc('copyrights/copyright_drand48_c-drand_c.c')
        expected = [
            u'Copyright (c) 1993 Martin Birgmeier',
        ]
        check_detection(expected, test_file)

    def test_copyright_ed_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_ed_copyright-ed_copyright.copyright')
        expected = [
            u'Copyright (c) 1993, 1994 Andrew Moore , Talke Studio',
            u'Copyright (c) 2006, 2007 Antonio Diaz Diaz',
            u'Copyright (c) 1997-2007 James Troup',
            u'Copyright (c) 1993, 2006, 2007 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_epiphany_browser_data_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_epiphany_browser_data_copyright_label-epiphany_browser_data_copyright_label.label')
        expected = [
            u'Copyright (c) 2004 the Initial Developer.',
            u'(c) 2003-2007, the Debian GNOME team <pkg-gnome-maintainers@lists.alioth.debian.org>',
        ]
        check_detection(expected, test_file)

    def test_copyright_eric_young_c(self):
        test_file = self.get_test_loc('copyrights/copyright_eric_young_c-c.c')
        expected = [
            u'Copyright (c) 1995-1997 Eric Young (eay@mincom.oz.au)',
        ]
        check_detection(expected, test_file)

    def test_copyright_errno_atheros(self):
        test_file = self.get_test_loc('copyrights/copyright_errno_atheros-c.c')
        expected = [
            'Copyright (c) 2002-2006 Sam Leffler, Errno Consulting, Atheros Communications, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_errno_atheros_ah_h(self):
        test_file = self.get_test_loc('copyrights/copyright_errno_atheros_ah_h-ah_h.h')
        expected = [
            u'Copyright (c) 2002-2006 Sam Leffler, Errno Consulting, Atheros Communications, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_errno_c(self):
        test_file = self.get_test_loc('copyrights/copyright_errno_c-c.c')
        expected = [
            u'Copyright (c) 2002-2006 Sam Leffler, Errno Consulting, Atheros Communications, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_esmertec_java(self):
        test_file = self.get_test_loc('copyrights/copyright_esmertec_java-java.java')
        expected = [
            u'Copyright (c) 2008 Esmertec AG',
            u'Copyright (c) 2008 The Android Open Source Project',
        ]
        check_detection(expected, test_file)

    def test_copyright_essential_smoke(self):
        test_file = self.get_test_loc('copyrights/copyright_essential_smoke-ibm_c.c')
        expected = [
            u'Copyright IBM and others (c) 2008',
            u'Copyright Eclipse, IBM and others (c) 2008',
        ]
        check_detection(expected, test_file)

    def test_copyright_expat_h(self):
        test_file = self.get_test_loc('copyrights/copyright_expat_h-expat_h.h')
        expected = [
            u'Copyright (c) 1998, 1999, 2000 Thai Open Source Software Center Ltd',
        ]
        check_detection(expected, test_file)

    def test_copyright_ext_all_js(self):
        test_file = self.get_test_loc('copyrights/copyright_ext_all_js-ext_all_js.js')
        expected = [
            u'Copyright (c) 2006-2009 Ext JS, LLC',
        ]
        check_detection(expected, test_file)

    def test_copyright_extjs_c(self):
        test_file = self.get_test_loc('copyrights/copyright_extjs_c-c.c')
        expected = [
            u'Copyright (c) 2006-2007, Ext JS, LLC.',
        ]
        check_detection(expected, test_file)

    def test_copyright_fsf_py(self):
        test_file = self.get_test_loc('copyrights/copyright_fsf_py-999_py.py')
        expected = [
            u'Copyright 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_gailly(self):
        test_file = self.get_test_loc('copyrights/copyright_gailly-c.c')
        expected = [
            u'Copyright (c) 1992-1993 Jean-loup Gailly.',
            u'Copyright (c) 1992-1993 Jean-loup Gailly',
            u'Copyright (c) 1992-1993 Jean-loup Gailly',
        ]
        check_detection(expected, test_file)

    def test_copyright_geoff_js(self):
        test_file = self.get_test_loc('copyrights/copyright_geoff_js-js.js')
        expected = [
            u'Copyright (c) 2007-2008 Geoff Stearns, Michael Williams, and Bobby van der Sluis',
        ]
        check_detection(expected, test_file)

    def test_copyright_gnome_session_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_gnome_session_copyright-gnome_session_copyright.copyright')
        expected = [
            u'Copyright (c) 1999-2009 Red Hat, Inc.',
            u'Copyright (c) 1999-2007 Novell, Inc.',
            u'Copyright (c) 2001-2003 George Lebl',
            u'Copyright (c) 2001 Queen of England',
            u'Copyright (c) 2007-2008 William Jon McCann',
            u'Copyright (c) 2006 Ray Strode',
            u'Copyright (c) 2008 Lucas Rocha',
            u'Copyright (c) 2005 Raffaele Sandrini',
            u'Copyright (c) 2006-2007 Vincent Untz',
            u'Copyright (c) 1998 Tom Tromey',
            u'Copyright (c) 1999 Free Software Foundation, Inc.',
            u'Copyright (c) 2003 Sun Microsystems, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_gnome_system_monitor_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_gnome_system_monitor_copyright-gnome_system_monitor_copyright.copyright')
        expected = [
            u'Copyright Holders: Kevin Vandersloot <kfv101@psu.edu> Erik Johnsson <zaphod@linux.nu>',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_copyright_gnome_system_monitor_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_gnome_system_monitor_copyright_label-gnome_system_monitor_copyright_label.label')
        expected = [
            u'Copyright Holders: Kevin Vandersloot <kfv101@psu.edu> Erik Johnsson <zaphod@linux.nu>',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_copyright_gobjc_4_3_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_gobjc_4_3_copyright-gobjc__copyright.copyright')
        expected = [
            u'Copyright (c) 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008 Free Software Foundation, Inc.',
            u'copyright Free Software Foundation',
            u'Copyright (c) 2004-2005 by Digital Mars , www.digitalmars.com',
            u'Copyright (c) 1996-2003 Red Hat, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_google_closure_templates_java_html(self):
        test_file = self.get_test_loc('copyrights/copyright_google_closure_templates_java_html-html.html')
        expected = [
            u'(c) 2009 Google',
        ]
        check_detection(expected, test_file)

    def test_copyright_google_view_layout1_xml(self):
        test_file = self.get_test_loc('copyrights/copyright_google_view_layout1_xml-view_layout_xml.xml')
        expected = [
            u'Copyright (c) 2008 Google Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_group(self):
        test_file = self.get_test_loc('copyrights/copyright_group-c.c')
        expected = [
            u'Copyright (c) 2014 ARRis Group, Inc.',
            u'Copyright (c) 2013 ARRIS Group, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_gsoap(self):
        test_file = self.get_test_loc('copyrights/copyright_gsoap-gSOAP')
        expected = [
            u'Copyright (c) 2001-2004 Robert A. van Engelen, Genivia inc.',
            u'Copyright (c) 2001-2004 Robert A. van Engelen, Genivia inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_gstreamer0_fluendo_mp3_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_gstreamer0_fluendo_mp3_copyright-gstreamer__fluendo_mp_copyright.copyright')
        expected = [
            u'Copyright (c) 2005,2006 Fluendo',
            u'Copyright 2005 Fluendo',
        ]
        check_detection(expected, test_file)

    def test_copyright_hall(self):
        test_file = self.get_test_loc('copyrights/copyright_hall-copyright.txt')
        expected = [
            u'Copyright (c) 2004, Richard S. Hall',
            u'Copyright (c) 2004, Didier Donsez',
            u'Copyright (c) 2002,2003, Stefan Haustein, Oberhausen',
        ]
        check_detection(expected, test_file)

    def test_copyright_hans_jurgen_htm(self):
        test_file = self.get_test_loc('copyrights/copyright_hans_jurgen_htm-9_html.html')
        expected = [
            u'Copyright (c) 2006 by Hans-Jurgen Koch.',
        ]
        check_detection(expected, test_file,
                        expected_in_results=True,
                        results_in_expected=False)

    def test_copyright_hansen_cs(self):
        test_file = self.get_test_loc('copyrights/copyright_hansen_cs-cs.cs')
        expected = [
            u'Web Applications Copyright 2009 - Thomas Hansen thomas@ra-ajax.org.',
        ]
        check_detection(expected, test_file)

    def test_copyright_hciattach_qualcomm1_c(self):
        test_file = self.get_test_loc('copyrights/copyright_hciattach_qualcomm1_c-hciattach_qualcomm_c.c')
        expected = [
            u'Copyright (c) 2005-2010 Marcel Holtmann <marcel@holtmann.org>',
        ]
        check_detection(expected, test_file)

    def test_copyright_hibernate_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_hibernate_copyright_label-hibernate_copyright_label.label')
        expected = [
            u'Copyright (c) 2004-2006 Bernard Blackham <bernard@blackham.com.au>',
            u'copyright (c) 2004-2006 Cameron Patrick <cameron@patrick.wattle.id.au>',
            u'copyright (c) 2006- Martin F. Krafft <madduck@debian.org>',
        ]
        check_detection(expected, test_file)

    def test_copyright_holtmann(self):
        test_file = self.get_test_loc('copyrights/copyright_holtmann-hciattach_qualcomm_c.c')
        expected = [
            u'Copyright (c) 2005-2010 Marcel Holtmann <marcel@holtmann.org>',
            u'Copyright (c) 2010, Code Aurora Forum.',
        ]
        check_detection(expected, test_file)

    def test_copyright_hostapd_cli_c(self):
        test_file = self.get_test_loc('copyrights/copyright_hostapd_cli_c-hostapd_cli_c.c')
        expected = [
            u'Copyright (c) 2004-2005, Jouni Malinen <jkmaline@cc.hut.fi>',
            u'Copyright (c) 2004-2005, Jouni Malinen <jkmaline@cc.hut.fi>',
        ]
        check_detection(expected, test_file)

    def test_copyright_hp_notice(self):
        test_file = self.get_test_loc('copyrights/copyright_hp_notice-NOTICE')
        expected = [
            u'(c) Copyright 2007 Hewlett-Packard Development Company',
            u'(c) Copyright 2008 Hewlett-Packard Development Company',
            u'Copyright (c) 2006 Alan D. Brunelle <Alan.Brunelle@hp.com>',
            u'Copyright (c) 2007 Alan D. Brunelle <Alan.Brunelle@hp.com>',
            u'(c) Copyright 2008 Hewlett-Packard Development Company',
            u'(c) Copyright 2009 Hewlett-Packard Development Company',
            u'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, test_file)

    def test_copyright_hpijs_ppds_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_hpijs_ppds_copyright_label-hpijs_ppds_copyright_label.label')
        expected = [
            u'Copyright (c) 2003-2004 by Torsten Landschoff <torsten@debian.org>',
            u'Copyright (c) 2004-2006 by Henrique de Moraes Holschuh <hmh@debian.org>',
            u'Copyright (c) 2001-2006 Hewlett-Packard Company',
            u'Copyright (c) 2001-2006 Hewlett-Packard Development Company',
        ]
        check_detection(expected, test_file)

    def test_copyright_ibm_c(self):
        test_file = self.get_test_loc('copyrights/copyright_ibm_c-ibm_c.c')
        expected = [
            u'Copyright (c) ibm technologies 2008',
            u'Copyright (c) IBM Corporation 2008',
            u'Copyright (c) Ibm Corp. 2008',
            u'Copyright (c) ibm.com 2008',
            u'Copyright (c) IBM technology 2008',
            u'Copyright (c) IBM company 2008',
        ]
        check_detection(expected, test_file)

    def test_copyright_icedax_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_icedax_copyright_label-icedax_copyright_label.label')
        expected = [
            u'Copyright 1998-2003 Heiko Eissfeldt',
            u'(c) Peter Widow',
            u'(c) Thomas Niederreiter',
            u'(c) RSA Data Security, Inc.',
            u'Copyright 1993 Yggdrasil Computing, Incorporated',
            u'Copyright (c) 1999,2000-2004 J. Schilling',
            u'(c) 1998-2002 by Heiko Eissfeldt, heiko@colossus.escape.de',
            u'(c) 2002 by Joerg Schilling',
            u'(c) 1996, 1997 Robert Leslie',
            u'Copyright (c) 2002 J. Schilling',
            u'Copyright (c) 1987, 1995-2003 J. Schilling',
            u'Copyright 2001 H. Peter Anvin',
        ]
        check_detection(expected, test_file)

    def test_copyright_ifrename_c(self):
        test_file = self.get_test_loc('copyrights/copyright_ifrename_c-ifrename_c.c')
        expected = [
            u'Copyright (c) 2004 Jean Tourrilhes <jt@hpl.hp.com>',
        ]
        check_detection(expected, test_file)

    def test_copyright_illinois_html(self):
        test_file = self.get_test_loc('copyrights/copyright_illinois_html-9_html.html')
        expected = [
            u'Copyright 1999,2000,2001,2002,2003,2004 The Board of Trustees of the University of Illinois',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_copyright_in_COPYING_gpl(self):
        test_file = self.get_test_loc('copyrights/copyright_in_COPYING_gpl-COPYING_gpl.gpl')
        expected = [
            u'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, test_file)

    def test_copyright_in_COPYRIGHT_madwifi(self):
        test_file = self.get_test_loc('copyrights/copyright_in_COPYRIGHT_madwifi-COPYRIGHT_madwifi.madwifi')
        expected = [
            u'Copyright (c) 2002-2006 Sam Leffler, Errno Consulting, Atheros Communications, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_in_README(self):
        test_file = self.get_test_loc('copyrights/copyright_in_README-README')
        expected = [
            u'Copyright (c) 2002-2006, Jouni Malinen <jkmaline@cc.hut.fi>',
        ]
        check_detection(expected, test_file)

    def test_copyright_in_bash(self):
        test_file = self.get_test_loc('copyrights/copyright_in_bash-shell_sh.sh')
        expected = [
            u'Copyright (c) 2008 Hewlett-Packard Development Company, L.P.',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_copyright_in_binary_lib(self):
        test_file = self.get_test_loc('copyrights/copyright_in_binary_lib-php_embed_lib.lib')
        expected = [
            'Copyright nexB and others (c) 2012',
        ]
        check_detection(expected, test_file)

    def test_copyright_in_c(self):
        test_file = self.get_test_loc('copyrights/copyright_in_c-c.c')
        expected = [
            u'COPYRIGHT (c) STMicroelectronics 2005.',
        ]
        check_detection(expected, test_file)

    def test_copyright_in_c_include(self):
        test_file = self.get_test_loc('copyrights/copyright_in_c_include-h.h')
        expected = [
            u'COPYRIGHT (c) ST-Microelectronics 1998.',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_copyright_in_dll(self):
        test_file = self.get_test_loc('copyrights/copyright_in_dll-9_msvci_dll.dll')
        expected = [
            'Copyright Myself and Me, Inc',
        ]
        check_detection(expected, test_file)

    def test_copyright_in_h(self):
        test_file = self.get_test_loc('copyrights/copyright_in_h-h.h')
        expected = [
            u'COPYRIGHT (c) ST-Microelectronics 1998.',
        ]
        check_detection(expected, test_file)

    @expectedFailure
    def test_copyright_in_html_comments(self):
        test_file = self.get_test_loc('copyrights/copyright_in_html_comments-html.html')
        expected = [
            u'Copyright 2008 ABCD, LLC.',
        ]
        check_detection(expected, test_file)

    def test_copyright_in_html_incorrect(self):
        test_file = self.get_test_loc('copyrights/copyright_in_html_incorrect-detail_9_html.html')
        expected = [
            'A12 Oe (c) 2004-2009',
        ]
        check_detection(expected, test_file)

    def test_copyright_in_maven_pom_xstream(self):
        test_file = self.get_test_loc('copyrights/copyright_in_maven_pom_xstream-pom_xml.xml')
        expected = [
            u'Copyright (c) 2006 Joe Walnes.',
            u'Copyright (c) 2006, 2007, 2008 XStream committers.',
        ]
        check_detection(expected, test_file)

    def test_copyright_in_media(self):
        test_file = self.get_test_loc('copyrights/copyright_in_media-a_png.png')
        expected = [
            'Copyright nexB and others (c) 2012',
        ]
        check_detection(expected, test_file)

    def test_copyright_in_phps(self):
        test_file = self.get_test_loc('copyrights/copyright_in_phps-phps.phps')
        expected = [
            u'copyright 2005 Michal Migurski',
        ]
        check_detection(expected, test_file)

    def test_copyright_in_postcript(self):
        test_file = self.get_test_loc('copyrights/copyright_in_postcript-9__ps.ps')
        expected = [
            'Copyright 1999 Radical Eye Software',
        ]
        check_detection(expected, test_file)

    def test_copyright_in_txt(self):
        test_file = self.get_test_loc('copyrights/copyright_in_txt.txt')
        expected = [
            u'Copyright ?2004-2006 Company',
        ]
        check_detection(expected, test_file)

    def test_copyright_in_visio_doc(self):
        test_file = self.get_test_loc('copyrights/copyright_in_visio_doc-Glitch_ERD_vsd.vsd')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_inria_loss_of_holder_c(self):
        test_file = self.get_test_loc('copyrights/copyright_inria_loss_of_holder_c-c.c')
        expected = [
            u'Copyright (c) 2000,2002,2003 INRIA, France Telecom',
        ]
        check_detection(expected, test_file)

    @expectedFailure
    def test_copyright_java(self):
        test_file = self.get_test_loc('copyrights/copyright_java-java.java')
        expected = [
            u'Copyright (c) 1992-2002 by P.J. Plauger.',
        ]
        check_detection(expected, test_file)

    @expectedFailure
    def test_copyright_java_passing(self):
        test_file = self.get_test_loc('copyrights/copyright_java-java.java')
        expected = [
            u'Copyright (c) 1992-2002 by P.J.',
        ]
        check_detection(expected, test_file) 

    def test_copyright_jdoe(self):
        test_file = self.get_test_loc('copyrights/copyright_jdoe-copyright_c.c')
        expected = [
            u'Copyright 2009 J-Doe.',
        ]
        check_detection(expected, test_file)

    @expectedFailure
    def test_copyright_json_in_phps(self):
        test_file = self.get_test_loc('copyrights/copyright_json_in_phps-JSON_phps.phps')
        expected = [
            u'copyright 2005 Michal Migurski',
        ]
        check_detection(expected, test_file)

    def test_copyright_json_in_phps_incorrect(self):
        test_file = self.get_test_loc('copyrights/copyright_json_in_phps_incorrect-JSON_phps.phps')
        expected = []
        check_detection(expected, test_file)

    @expectedFailure
    def test_copyright_json_phps_html(self):
        test_file = self.get_test_loc('copyrights/copyright_json_phps_html-JSON_phps_html.html')
        expected = [
            u'copyright 2005 Michal Migurski',
        ]
        check_detection(expected, test_file)

    def test_copyright_jsp_all_CAPS(self):
        test_file = self.get_test_loc('copyrights/copyright_jsp_all_CAPS-jsp.jsp')
        expected = [
            u'copyright 2005-2006 Cedrik LIME',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_copyright_kaboom_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_kaboom_copyright-kaboom_copyright.copyright')
        expected = [
            u'Copyright (c) 2009 Sune Vuorela <sune@vuorela.dk>',
            u'Copyright (c) 2007-2009 George Kiagiadakis <gkiagiad@csd.uoc.gr>',
            u'Copyright (c) 2009 Modestas Vainius <modestas@vainius.eu>',
            u'Copyright (c) 2009, Debian Qt/KDE Maintainers <debian-qt-kde@lists.debian.org>',
        ]
        check_detection(expected, test_file)

    def test_copyright_kbuild_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_kbuild_copyright-kbuild_copyright.copyright')
        expected = [
            u'Copyright (c) 2005-2009 Knut St. Osmundsen <bird-kBuild-spam@anduin.net>',
            u'Copyright (c) 1991-1993 The Regents of the University of California',
            u'Copyright (c) 1988-2009 Free Software Foundation, Inc.',
            u'Copyright (c) 2003 Free Software Foundation, Inc.',
            u'Copyright (c) 2007-2009 Torsten Werner <twerner@debian.org>',
            u'(c) 2009 Daniel Baumann <daniel@debian.org>',
        ]
        check_detection(expected, test_file)

    def test_copyright_kde_l10n_zhcn_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_kde_l10n_zhcn_copyright-kde_l_n_zhcn_copyright.copyright')
        expected = [
            u'Copyright (c) 1996-2009 The KDE Translation teams <kde-i18n-doc@kde.org>',
            u'(c) 2007-2009, Debian Qt/KDE Maintainers',
        ]
        check_detection(expected, test_file)

    def test_copyright_leonardo_c(self):
        test_file = self.get_test_loc('copyrights/copyright_leonardo_c-c.c')
        expected = [
            u'Copyright (c) 1994 by Leonardo DaVinci Societe',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_copyright_libadns1_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libadns1_copyright-libadns_copyright.copyright')
        expected = [
            u'Copyright 1997-2000 Ian Jackson',
            u'Copyright 1999 Tony Finch',
            u'Copyright (c) 1991 Massachusetts Institute of Technology',
        ]
        check_detection(expected, test_file)

    def test_copyright_libc6_i686_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libc6_i686_copyright-libc_i_copyright.copyright')
        expected = [
            u'Copyright (c) 1991,92,93,94,95,96,97,98,99,2000,2001,2002,2003,2004,2005, 2006,2007,2008 Free Software Foundation, Inc.',
            u'Copyright (c) 1991,92,93,94,95,96,97,98,99,2000,2001,2002,2003,2004,2005, 2006,2007,2008 Free Software Foundation, Inc.',
            u'Copyright (c) 1991 Regents of the University of California',
            u'Portions Copyright (c) 1993 by Digital Equipment Corporation',
            u'Copyright (c) 1984, Sun Microsystems, Inc.',
            u'Copyright (c) 1991,1990,1989 Carnegie Mellon University',
            u'Copyright (c) 2000, Intel Corporation',
            u'copyright (c) by Craig Metz',
        ]
        check_detection(expected, test_file)

    def test_copyright_libcdio10_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_libcdio10_copyright_label-libcdio_copyright_label.label')
        expected = [
            u'Copyright (c) 1999, 2002, 2003, 2004, 2005, 2006, 2007, 2008 Rocky Bernstein <rocky@gnu.org>',
            u'Copyright (c) 2000, 2001, 2003, 2004, 2005, 2008 Herbert Valerio Riedel',
            u'Copyright (c) 1996, 1997, 1998 Gerd Knorr <kraxel@bytesex.org>',
            u'Copyright (c) 2001 Xiph.org',
            u'Copyright (c) 1994, 1995, 1996, 1997, 1998, 2001 Heiko Eifeldt <heiko@escape.colossus.de>',
            u'Copyright (c) 1998, 1999, 2001 Monty',
            u'Copyright (c) 2008 Robert W. Fuller <hydrologiccycle@gmail.com>',
            u'Copyright (c) 2006, 2008 Burkhard Plaum <plaum@ipf.uni-stuttgart.de>',
            u'Copyright (c) 2001, 2002 Ben Fennema <bfennema@falcon.csc.calpoly.edu>',
            u'Copyright (c) 2001, 2002 Scott Long <scottl@freebsd.org>',
            u'Copyright (c) 1993 Yggdrasil Computing, Incorporated',
            u'Copyright (c) 1999, 2000 J. Schilling',
            u'Copyright (c) 2001 Sven Ottemann <ac-logic@freenet.de>',
            u'Copyright (c) 2003 Svend Sanjay Sorensen <ssorensen@fastmail.fm>',
            u'Copyright (c) 1985, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1996, 1997, 1998, 1999, 2000 Free Software Foundation, Inc.',
            u'Copyright (c) 2003 Matthias Drochner',
            u'Copyright (c) 1998-2001 VideoLAN Johan Bilien <jobi@via.ecp.fr> and Gildas Bazin <gbazin@netcourrier.com>',
            u'Copyright (c) 1992, 1993 Eric Youngdale',
            u'Copyright (c) 2003, 2004, 2005, 2006, 2007, 2008 Rocky Bernstein and Herbert Valerio Riedel',
        ]
        check_detection(expected, test_file)

    def test_copyright_libcelt0_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libcelt0_copyright-libcelt_copyright.copyright')
        expected = [
            u'Copyright 2005-2007 Christopher Montgomery , Jean-Marc Valin , Timothy Terriberry',
            u'(c) 2008, Ron',
        ]
        check_detection(expected, test_file)

    def test_copyright_libcompress_raw_zlib_perl_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libcompress_raw_zlib_perl_copyright-libcompress_raw_zlib_perl_copyright.copyright')
        expected = [
            u'Copyright 2005-2009, Paul Marquess <pmqs@cpan.org>',
            u'Copyright 1995-2005, Jean-loup Gailly <jloup@gzip.org>',
            u'Copyright 1995-2005, Mark Adler <madler@alumni.caltech.edu>',
            u'Copyright 2004-2009, Marcus Holland-Moritz <mhx-cpan@gmx.net> 2001, Paul Marquess <pmqs@cpan.org>',
            u'Copyright 2007-2009, Krzysztof Krzyzaniak <eloy@debian.org>',
        ]
        check_detection(expected, test_file)

    def test_copyright_libcpufreq0_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libcpufreq0_copyright-libcpufreq_copyright.copyright')
        expected = [
            u'Copyright 2004-2006 Dominik Brodowski',
        ]
        check_detection(expected, test_file)

    def test_copyright_libcrypt_ssleay_perl_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libcrypt_ssleay_perl_copyright-libcrypt_ssleay_perl_copyright.copyright')
        expected = [
            u'Copyright (c) 1999-2003 Joshua Chamas',
            u'Copyright (c) 1998 Gisle Aas',
            u'copyright (c) 2003 Stephen Zander <gibreel@debian.org>',
        ]
        check_detection(expected, test_file)

    def test_copyright_libepc_ui_1_0_1_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libepc_ui_1_0_1_copyright-libepc_ui__copyright.copyright')
        expected = [
            u'Copyright (c) 2007, 2008 Openismus GmbH',
        ]
        check_detection(expected, test_file)

    def test_copyright_libepc_ui_1_0_2_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_libepc_ui_1_0_2_copyright_label-libepc_ui__copyright_label.label')
        expected = [
            u'Copyright (c) 2007, 2008 Openismus GmbH',
        ]
        check_detection(expected, test_file)

    def test_copyright_libfltk1_1_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libfltk1_1_copyright-libfltk_copyright.copyright')
        expected = [
            u'Copyright (c) 1998-2009 Bill Spitzak spitzak@users.sourceforge.net',
        ]
        check_detection(expected, test_file)

    def test_copyright_libgail18_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_libgail18_copyright_label-libgail_copyright_label.label')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_libggiwmh0_target_x_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libggiwmh0_target_x_copyright-libggiwmh_target_x_copyright.copyright')
        expected = [
            u'Copyright (c) 2005 Eric Faurot eric.faurot@gmail.com',
            u'Copyright (c) 2004 Peter Ekberg peda@lysator.liu.se',
            u'Copyright (c) 2004 Christoph Egger',
            u'Copyright (c) 1999 Marcus Sundberg marcus@ggi-project.org',
            u'Copyright (c) 1998, 1999 Andreas Beck becka@ggi-project.org',
            u'Copyright (c) 2008 Bradley Smith <brad@brad-smith.co.uk>',
        ]
        check_detection(expected, test_file)

    def test_copyright_libgnome_desktop_2_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libgnome_desktop_2_copyright-libgnome_desktop__copyright.copyright')
        expected = [
            u'Copyright (c) 1999, 2000 Red Hat Inc.',
            u'Copyright (c) 2001 Sid Vicious',
            u'Copyright (c) 1999 Free Software Foundation',
            u'Copyright (c) 2002, Sun Microsystems, Inc.',
            u'Copyright (c) 2003, Kristian Rietveld',
        ]
        check_detection(expected, test_file)

    def test_copyright_libgnome_media0_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libgnome_media0_copyright-libgnome_media_copyright.copyright')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_libgoffice_0_8_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_libgoffice_0_8_copyright_label-libgoffice__copyright_label.label')
        expected = [
            u'Copyright (c) 2003-2008 Jody Goldberg (jody@gnome.org)',
        ]
        check_detection(expected, test_file)

    def test_copyright_libgtkhtml2_0_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libgtkhtml2_0_copyright-libgtkhtml_copyright.copyright')
        expected = [
            u'Copyright 1999,2000,2001 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_libisc44_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libisc44_copyright-libisc_copyright.copyright')
        expected = [
            u'Copyright (c) 1996-2001 Internet Software Consortium.',
        ]
        check_detection(expected, test_file)

    def test_copyright_libisccfg30_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libisccfg30_copyright-libisccfg_copyright.copyright')
        expected = [
            u'Copyright (c) 1996-2001 Internet Software Consortium',
        ]
        check_detection(expected, test_file)

    def test_copyright_libisccfg40_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libisccfg40_copyright-libisccfg_copyright.copyright')
        expected = [
            u'Copyright (c) 1996-2001 Internet Software Consortium',
        ]
        check_detection(expected, test_file)

    def test_copyright_libjpeg62_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libjpeg62_copyright-libjpeg_copyright.copyright')
        expected = [
            u'copyright (c) 1991-1998, Thomas G. Lane',
            u'copyright by the Free Software Foundation',
        ]
        check_detection(expected, test_file)

    def test_copyright_libkeyutils1_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_libkeyutils1_copyright_label-libkeyutils_copyright_label.label')
        expected = [
            u'Copyright (c) 2005 Red Hat',
            u'Copyright (c) 2005 Red Hat',
            u'Copyright (c) 2006-2009 Daniel Baumann <daniel@debian.org>',
        ]
        check_detection(expected, test_file)

    def test_copyright_liblocale_gettext_perl_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_liblocale_gettext_perl_copyright_label-liblocale_get_perl_copyright_label.label')
        expected = [
            u'Copyright 1996..2005 by Phillip Vandry <vandry@TZoNE.ORG>',
        ]
        check_detection(expected, test_file)

    def test_copyright_libopenraw1_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_libopenraw1_copyright_label-libopenraw_copyright_label.label')
        expected = [
            u'Copyright (c) 2007, David Paleino <d.paleino@gmail.com>',
            u'Copyright (c) 2005-2009, Hubert Figuiere <hub@figuiere.net>',
            u'Copyright (c) 2006, Hubert Figuiere <hub@figuiere.net>',
            u'(c) 2001, Lutz Muller <lutz@users.sourceforge.net>',
            u'Copyright (c) 2007, Hubert Figuiere <hub@figuiere.net>',
            u'(c) 1994, Kongji Huang and Brian C. Smith , Cornell University',
            u'(c) 1993, Brian C. Smith , The Regents',
            u"(c) 1991-1992, Thomas G. Lane , Part of the Independent JPEG Group's",
            u'Copyright (c) 2005, Hubert Figuiere <hub@figuiere.net>',
            u'Copyright (c) 2007, Hubert Figuiere <hub@figuiere.net>',
        ]
        check_detection(expected, test_file)

    def test_copyright_libopenthreads12_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libopenthreads12_copyright-libopenthreads_copyright.copyright')
        expected = [
            u'Copyright (c) 2002 Robert Osfield',
            u'Copyright (c) 1998 Julian Smart , Robert Roebling',
        ]
        check_detection(expected, test_file)

    def test_copyright_libpam_ck_connector_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libpam_ck_connector_copyright-libpam_ck_connector_copyright.copyright')
        expected = [
            u'Copyright (c) 2006 William Jon McCann <mccann@jhu.edu>',
            u'Copyright (c) 2007 David Zeuthen <davidz@redhat.com>',
            u'Copyright (c) 2007 William Jon McCann <mccann@jhu.edu>',
            u'(c) 2007, Michael Biebl <biebl@debian.org>',
        ]
        check_detection(expected, test_file)

    def test_copyright_libpoppler3_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libpoppler3_copyright-libpoppler_copyright.copyright')
        expected = [
            u'Copyright (c) 1996-2003 Glyph & Cog, LLC',
        ]
        check_detection(expected, test_file)

    def test_copyright_libqt4_scripttools_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libqt4_scripttools_copyright-libqt_scripttools_copyright.copyright')
        expected = [
            u'(c) 2008-2009 Nokia Corporation',
            u'(c) 1994-2008 Trolltech ASA',
        ]
        check_detection(expected, test_file)

    def test_copyright_libqtscript4_gui_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libqtscript4_gui_copyright-libqtscript_gui_copyright.copyright')
        expected = [
            u'Copyright (c) 2009 Modestas Vainius <modestas@vainius.eu>',
            u'Copyright (c) Trolltech ASA',
            u'Copyright (c) Roberto Raggi <roberto@kdevelop.org>',
            u'Copyright (c) Harald Fernengel <harry@kdevelop.org>',
        ]
        check_detection(expected, test_file)

    def test_copyright_libsocks4_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libsocks4_copyright-libsocks_copyright.copyright')
        expected = [
            u'Copyright (c) 1989 Regents of the University of California.',
            u'Portions Copyright (c) 1993, 1994, 1995 by NEC Systems Laboratory',
        ]
        check_detection(expected, test_file)

    def test_copyright_libsox_fmt_alsa_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libsox_fmt_alsa_copyright-libsox_fmt_alsa_copyright.copyright')
        expected = [
            u'Copyright 1991 Lance Norskog And Sundry Contributors',
        ]
        check_detection(expected, test_file)

    def test_copyright_libspeex1_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libspeex1_copyright-libspeex_copyright.copyright')
        expected = [
            u'Copyright 2002-2007 Xiph.org',
            u'Copyright 2002-2007 Jean-Marc Valin',
            u'Copyright 2005-2007 Analog Devices Inc.',
            u'Copyright 2005-2007 Commonwealth',
            u'Copyright 1993, 2002, 2006 David Rowe',
            u'Copyright 2003 EpicGames',
            u'Copyright 1992-1994 Jutta Degener , Carsten Bormann',
        ]
        check_detection(expected, test_file)

    def test_copyright_libstlport4_6ldbl_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_libstlport4_6ldbl_copyright_label-libstlport_ldbl_copyright_label.label')
        expected = [
            u'Copyright (c) 1994 Hewlett-Packard Company',
            u'Copyright (c) 1996-1999 Silicon Graphics Computer Systems, Inc.',
            u'Copyright (c) 1997 Moscow Center for SPARC Technology',
            u'Copyright (c) 1999, 2000, 2001 Boris Fomitchev',
        ]
        check_detection(expected, test_file)

    def test_copyright_libtdb1_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libtdb1_copyright-libtdb_copyright.copyright')
        expected = [
            u'Copyright (c) Andrew Tridgell 1999-2004',
            u'Copyright (c) Paul Rusty Russell 2000',
            u'Copyright (c) Jeremy Allison 2000-2003',
        ]
        check_detection(expected, test_file)

    def test_copyright_libuim6_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libuim6_copyright-libuim_copyright.copyright')
        expected = [
            u'Copyright (c) 2003-2007 uim Project',
            u'COPYRIGHT (c) 1988-1994 BY PARADIGM ASSOCIATES INCORPORATED',
            u'Copyright (c) 2006, SHIMODA Hiroshi <piro@p.club.ne.jp>',
            u'Copyright (c) 2006, FUJITA Yuji <yuji@webmasters.gr.jp>',
            u'Copyright (c) 2006, Jun Mukai <mukai@jmuk.org>',
            u'Copyright (c) 2006, Teppei Tamra <tam-t@par.odn.ne.jp>',
            u'Copyright (c) 2005 UTUMI Hirosi <utuhiro78@yahoo.co.jp>',
            u'Copyright (c) 2006 YAMAMOTO Kengo <yamaken@bp.iij4u.or.jp>',
            u'Copyright (c) 2006 Jae-hyeon Park <jhyeon@gmail.com>',
            u'Copyright (c) 2006 Etsushi Kato <ek.kato@gmail.com>',
        ]
        check_detection(expected, test_file)

    def test_copyright_libxext6_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libxext6_copyright-libxext_copyright.copyright')
        expected = [
            u'Copyright 1986, 1987, 1988, 1989, 1994, 1998 The Open Group',
            u'Copyright (c) 1996 Digital Equipment Corporation, Maynard, Massachusetts',
            u'Copyright (c) 1997 by Silicon Graphics Computer Systems, Inc.',
            u'Copyright 1992 Network Computing Devices',
            u'Copyright 1991,1993 by Digital Equipment Corporation, Maynard, Massachusetts',
            u'Copyright 1986, 1987, 1988 by Hewlett-Packard Corporation',
            u'Copyright (c) 1994, 1995 Hewlett-Packard Company',
            u'Copyright Digital Equipment Corporation',
            u'Copyright 1999, 2005, 2006 Sun Microsystems, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_libxmlrpc_c3_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_libxmlrpc_c3_copyright-libxmlrpc_c_copyright.copyright')
        expected = [
            u'Copyright (c) 2001 by First Peer, Inc.',
            u'Copyright (c) 2001 by Eric Kidd.',
            u'Copyright (c) 1998, 1999, 2000 Thai Open Source Software Center Ltd',
            u'Copyright (c) 2000 by Moez Mahfoudh <mmoez@bigfoot.com>',
            u'Copyright 1991, 1992, 1993, 1994 by Stichting Mathematisch Centrum, Amsterdam',
        ]
        check_detection(expected, test_file)

    def test_copyright_libxt6_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_libxt6_copyright_label-libxt_copyright_label.label')
        expected = [
            u'Copyright 1987, 1988 by Digital Equipment Corporation , Maynard, Massachusetts',
            u'Copyright 1993 by Sun Microsystems, Inc. Mountain View',
            u'Copyright 1985, 1986, 1987, 1988, 1989, 1994, 1998, 2001 The Open Group',
            u'(c) COPYRIGHT International Business Machines Corp. 1992,1997',
        ]
        check_detection(expected, test_file)

    @expectedFailure
    def test_copyright_license__qpl_v1_0_perfect(self):
        test_file = self.get_test_loc('copyrights/copyright_license_qpl_v1_0_perfect-QPL_v.0')
        expected = [
            u'Copyright (c) 1999 Trolltech AS, Norway.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_adaptive_v1_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_adaptive_v1_0-Adaptive v.0')
        expected = [
            u'(c) Any Recipient',
            u'(c) Each Recipient',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_adobe(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_adobe-Adobe')
        expected = [
            u'Copyright (c) 2006 Adobe Systems Incorporated.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_adobeflex2sdk(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_adobeflex2sdk-Adobeflex_sdk')
        expected = [
            u'(c) Adobe AIR',
            u'(c) Material Improvement',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_afferogplv1(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_afferogplv1-AfferoGPLv')
        expected = [
            u'Copyright (c) 2002 Affero Inc.',
            u'copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            u'copyrighted by Affero, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_afferogplv2(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_afferogplv2-AfferoGPLv')
        expected = [
            u'Copyright (c) 2007 Affero Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_afferogplv3(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_afferogplv3-AfferoGPLv')
        expected = [
            u'Copyright (c) 2007 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_afl_v3_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_afl_v3_0-AFL_v.0')
        expected = [
            u'Copyright (c) 2005 Lawrence Rosen.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_aladdin_free_public_license(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_aladdin_free_public_license-Aladdin Free Public License')
        expected = [
            u'Copyright (c) 1994, 1995, 1997, 1998, 1999, 2000 Aladdin Enterprises, Menlo Park, California',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_amazondsb(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_amazondsb-AmazonDSb')
        expected = [
            u'(c) 2006 Amazon Digital Services, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_ampasbsd(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_ampasbsd-AMPASBSD')
        expected = [
            u'Copyright (c) 2006 Academy of Motion Picture Arts and Sciences',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_apachev1_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_apachev1_0-Apachev.0')
        expected = [
            u'Copyright (c) 1995-1999 The Apache Group.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_apachev1_1(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_apachev1_1-Apachev.1')
        expected = [
            u'Copyright (c) 2000 The Apache Software Foundation.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_apachev2_0b(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_apachev2_0b-Apachev_b.0b')
        expected = [
            u'Copyright 2000',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_apple_common_documentation_license_v1_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_apple_common_documentation_license_v1_0-Apple Common Documentation License v.0')
        expected = [
            u'Copyright (c) 2001 Apple Computer, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_apple_public_source_license_v1_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_apple_public_source_license_v1_0-Apple Public Source License v.0')
        expected = [
            u'Copyright (c) 1999 Apple Computer, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_apple_public_source_license_v1_1(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_apple_public_source_license_v1_1-Apple Public Source License v.1')
        expected = [
            u'Copyright (c) 1999-2000 Apple Computer, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_apple_public_source_license_v1_2(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_apple_public_source_license_v1_2-Apple Public Source License v.2')
        expected = [
            u'Copyright (c) 1999-2003 Apple Computer, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_apslv2_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_apslv2_0-APSLv.0')
        expected = [
            u'Copyright (c) 1999-2007 Apple Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_artistic_v1_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_artistic_v1_0-Artistic v.0')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_license_text_artistic_v1_0_short(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_artistic_v1_0_short-Artistic v_ short.0 short')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_license_text_artistic_v2_0beta4(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_artistic_v2_0beta4-Artistic v_beta.0beta4')
        expected = [
            u'Copyright (c) 2000, Larry Wall.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_artisticv2_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_artisticv2_0-Artisticv.0')
        expected = [
            u'Copyright (c) 2000-2006, The Perl Foundation.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_attributionassurancelicense(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_attributionassurancelicense-AttributionAssuranceLicense')
        expected = [
            u'Copyright (c) 2002 by AUTHOR',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_bigelow_holmes(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_bigelow_holmes-Bigelow&Holmes')
        expected = [
            u'(c) Copyright 1989 Sun Microsystems, Inc.',
            u'(c) Copyright Bigelow',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_bitstream(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_bitstream-Bi_ream')
        expected = [
            u'Copyright (c) 2003 by Bitstream, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_bsdnrl(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_bsdnrl-BSDNRL')
        expected = [
            u'copyright by The Regents of the University of California.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_cnri(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_cnri-CNRI')
        expected = [
            u'Copyright (c) 1995-2000 Corporation for National Research Initiatives',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_condor_extra_For(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_condor_extra_For-Condor')
        expected = [
            u'Copyright 1990-2006 Condor Team, Computer Sciences Department, University of Wisconsin-Madison, Madison',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_doc(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_doc-DOC')
        expected = [u'copyrighted by Douglas C. Schmidt',
                    # and his research group at Washington University, University of California, Irvine, and Vanderbilt University',
                    u'research group at Washington University, University of California, Irvine, and Vanderbilt University, Copyright (c) 1993-2008']
        check_detection(expected, test_file)

    def test_copyright_license_text_dual_mpl_gpl(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_dual_mpl_gpl-Dual MPL GPL')
        expected = [
            u'Copyright (c) 2002 the Initial Developer.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_dualmpl_mit(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_dualmpl_mit-DualMPL_MIT')
        expected = [
            u'Copyright (c) 1998-2001, Daniel Stenberg, <daniel@haxx.se>',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_eclv1_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_eclv1_0-ECLv.0')
        expected = [
            u'Copyright (c) YeAr Name',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_ecosv2_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_ecosv2_0-eCosv.0')
        expected = [
            u'Copyright (c) 1998, 1999, 2000, 2001, 2002 Red Hat, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_entessa(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_entessa-Entessa')
        expected = [
            u'Copyright (c) 2003 Entessa, LLC.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_eplv1_0b(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_eplv1_0b-EPLv_b.0b')
        expected = [
            u'Copyright (c) 2003, 2005 IBM Corporation',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_eudatagrid(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_eudatagrid-EUDatagrid')
        expected = [
            u'Copyright (c) 2001 EU DataGrid.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_eurosym_v2(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_eurosym_v2-Eurosym_v.v2')
        expected = [
            u'Copyright (c) 1999-2002 Henrik Theiling',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_frameworxv1_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_frameworxv1_0-Frameworxv.0')
        expected = [
            u'(c) Source Code',
            u'(c) THE FRAMEWORX COMPANY 2003',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_freebsd(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_freebsd-FreeBSD')
        expected = [
            u'Copyright 1994-2006 The FreeBSD Project.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_freetype(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_freetype-FreeType')
        expected = [
            u'Copyright 1996-2002, 2006 by David Turner, Robert Wilhelm, and Werner Lemberg',
            u'copyright (c) The FreeType Project (www.freetype.org).',
            u'copyright (c) 1996-2000 by David Turner, Robert Wilhelm, and Werner Lemberg.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_gfdlv1_2(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_gfdlv1_2-GFDLv.2')
        expected = [
            u'Copyright (c) 2000,2001,2002 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_gfdlv1_3(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_gfdlv1_3-GFDLv.3')
        expected = [
            u'Copyright (c) 2000, 2001, 2002, 2007, 2008 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_glide(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_glide-Glide')
        expected = [
            u'copyright notice (3dfx Interactive, Inc. 1999)',
            u'COPYRIGHT 3DFX INTERACTIVE, INC. 1999',
            u'COPYRIGHT 3DFX INTERACTIVE, INC. 1999',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_gnuplot(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_gnuplot-gnuplot')
        expected = [
            u'Copyright 1986 - 1993, 1998, 2004 Thomas Williams, Colin Kelley',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_gpl_v1(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_gpl_v1-GPL_v')
        expected = [
            u'Copyright (c) 1989 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_gpl_v2(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_gpl_v2-GPL_v')
        expected = [
            u'Copyright (c) 1989, 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_gpl_v3(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_gpl_v3-GPL_v')
        expected = [
            u'Copyright (c) 2007 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_gsoap(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_gsoap-gSOAP')
        expected = [
            u'Copyright (c) 2001-2004 Robert A. van Engelen, Genivia inc.',
            u'Copyright (c) 2001-2004 Robert A. van Engelen, Genivia inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_helix(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_helix-Helix')
        expected = [
            u'Copyright (c) 1995-2002 RealNetworks, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_hewlett_packard(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_hewlett_packard-Hewlett_Packard')
        expected = [
            u'(c) HEWLETT-PACKARD COMPANY, 2004.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_ibmpl_v1_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_ibmpl_v1_0-IBMPL_v.0')
        expected = [
            u'Copyright (c) 1996, 1999 International Business Machines Corporation',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_ietf(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_ietf-IETF')
        expected = [
            u'Copyright (c) The Internet Society (2003).',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_ijg(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_ijg-IJG')
        expected = [
            u'copyright (c) 1991-1998, Thomas G. Lane.',
            u'copyright by the Free Software Foundation',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_imatix(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_imatix-iMatix')
        expected = [
            u'Copyright 1991-2000 iMatix Corporation.',
            u'Copyright 1991-2000 iMatix Corporation',
            u'Copyright 1991-2000 iMatix Corporation',
            u'Parts copyright (c) 1991-2000 iMatix Corporation.',
            u'Copyright 1996-2000 iMatix Corporation',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_imlib2(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_imlib2-Imlib')
        expected = [
            u'Copyright (c) 2000 Carsten Haitzler',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_intel(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_intel-Intel')
        expected = [
            u'Copyright (c) 2006, Intel Corporation.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_jabber(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_jabber-Jabber')
        expected = [
            u'Copyright (c) 1999-2000 Jabber.com',
            u'Copyright (c) 1998-1999 Jeremie Miller.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_jpython(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_jpython-JPython')
        expected = [
            u'Copyright 1996-1999 Corporation for National Research Initiatives',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_larryrosen(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_larryrosen-LarryRosen')
        expected = [
            u'Copyright (c) 2002 Lawrence E. Rosen.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_latex_v1_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_latex_v1_0-LaTeX_v.0')
        expected = [
            u'Copyright 1999 LaTeX3 Project',
            u'Copyright 2001 M. Y. Name',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_latex_v1_1(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_latex_v1_1-LaTeX_v.1')
        expected = [
            u'Copyright 1999 LaTeX3 Project',
            u'Copyright 2001 M. Y. Name',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_latex_v1_2(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_latex_v1_2-LaTeX_v.2')
        expected = [
            u'Copyright 1999 LaTeX3 Project',
            u'Copyright 2001 M. Y. Name',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_latex_v1_3a(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_latex_v1_3a-LaTeX_v_a.3a')
        expected = [
            u'Copyright 1999 2002-04 LaTeX3 Project',
            u'Copyright 2003 M. Y. Name',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_latex_v1_3a_ref(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_latex_v1_3a_ref-LaTeX_v_a_ref.3a_ref')
        expected = [
            u'Copyright 2003 Name',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_latex_v1_3c(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_latex_v1_3c-LaTeX_v_c.3c')
        expected = [
            u'Copyright 1999 2002-2008 LaTeX3 Project',
            u'Copyright 2005 M. Y. Name',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_lgpl_v2_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_lgpl_v2_0-LGPL_v.0')
        expected = [
            u'Copyright (c) 1991 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_lgpl_v2_1(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_lgpl_v2_1-LGPL_v.1')
        expected = [
            u'Copyright (c) 1991, 1999 Free Software Foundation, Inc.',
            u'copyrighted by the Free Software Foundation',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_lgpl_v3(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_lgpl_v3-LGPL_v')
        expected = [
            u'Copyright (c) 2007 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_lgpl_wxwindows_library_licence_v3_0_variant(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_lgpl_wxwindows_library_licence_v3_0_variant-LGPL wxWindows Library Licence v_ variant.0 variant')
        expected = [
            u'Copyright (c) 1998 Julian Smart, Robert Roebling',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_logica_v1_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_logica_v1_0-Logica_v.0')
        expected = [
            u'Copyright (c) 1996-2001 Logica Mobile Networks Limited',
            u'Copyright (c) 1996-2001 Logica Mobile Networks Limited',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_luxi_fonts(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_luxi_fonts-Luxi_fonts')
        expected = [
            u'copyright (c) 2001 by Bigelow & Holmes Inc.',
            u'copyright (c) 2001 by URW++ GmbH.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_maia(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_maia-Maia')
        expected = [
            u'Copyright 2004 by Robert LeBlanc',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_mit_adobeglyph(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_mit_adobeglyph-MIT_AdobeGlyph')
        expected = [
            u'Copyright (c) 1997,1998,2002,2007 Adobe Systems Incorporated',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_mit_cmu(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_mit_cmu-MIT_CMU')
        expected = [
            u'Copyright 1989, 1991, 1992 by Carnegie Mellon University',
            u'Copyright 1996, 1998-2000 The Regents of the University of California',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_mit_danse(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_mit_danse-MIT_danse')
        expected = [
            u'Copyright (c) 2009 California Institute of Technology.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_mit_enna(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_mit_enna-MIT_enna')
        expected = [
            u'Copyright (c) 2000 Carsten Haitzler',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_mit_hylafax(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_mit_hylafax-MIT_hylafax')
        expected = [
            u'Copyright (c) 1990-1996 Sam Leffler',
            u'Copyright (c) 1991-1996 Silicon Graphics, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_mit_icu(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_mit_icu-MIT_ICU')
        expected = [
            u'Copyright (c) 1995-2006 International Business Machines Corporation',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_mit_lucent(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_mit_lucent-MIT_Lucent')
        expected = [
            u'Copyright (c) 1989-1998 by Lucent Technologies',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_mit_mlton(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_mit_mlton-MIT_MLton')
        expected = [
            u'Copyright (c) 1999-2006 Henry Cejtin, Matthew Fluet, Suresh Jagannathan, and Stephen Weeks.',
            u'Copyright (c) 1997-2000 by the NEC Research',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_mit_oldstyle_disclaimer4(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_mit_oldstyle_disclaimer4-MIT_OldStyle_disclaimer')
        expected = [
            u'Copyright (c) 2001, 2002, 2003, 2004, 2005 by The Regents of the University of California.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_mit_unicode(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_mit_unicode-MIT_unicode')
        expected = [
            u'Copyright (c) 1991-2005 Unicode, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_mit_wordnet(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_mit_wordnet-MIT_WordNet')
        expected = [
            u'Copyright 2006 by Princeton University.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_mitre(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_mitre-MITRE')
        expected = [
            u'Copyright (c) 1994-1999. The MITRE Corporation',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_ms_pl(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_ms_pl-Ms_PL')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_license_text_ms_rl(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_ms_rl-Ms_RL')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_license_text_ms_rsl(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_ms_rsl-Ms_RSL')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_license_text_msntp(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_msntp-MSNTP')
        expected = [
            u'(c) Copyright, University of Cambridge, 1996, 1997, 2000',
            u'(c) Copyright University of Cambridge.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_mysql_gplexception(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_mysql_gplexception-MySQL_gplexception')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_license_text_naumen(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_naumen-Naumen')
        expected = [
            u'Copyright (c) NAUMEN (tm) and Contributors.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_netcomponents(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_netcomponents-NetComponents')
        expected = [
            u'Copyright (c) 1996-1999 Daniel F. Savarese.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_nethack(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_nethack-Nethack')
        expected = [
            u'Copyright (c) 1989 M. Stephenson',
            u'copyright 1988 Richard M. Stallman',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_nokia(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_nokia-Nokia')
        expected = [
            u'Copyright (c) Nokia',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_npl_v1_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_npl_v1_0-NPL_v.0')
        expected = [
            u'Copyright (c) 1998 Netscape Communications Corporation.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_nvidia_source(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_nvidia_source-Nvidia_source')
        expected = [
            u'Copyright (c) 1996-1998 NVIDIA, Corp.',
            u'Copyright (c) 1996-1998 NVIDIA, Corp.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_oclc_v1_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_oclc_v1_0-OCLC_v.0')
        expected = [
            u'Copyright (c) 2000. OCLC Research.',
            u'Copyright (c) 2000- (insert then current year)',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_oclc_v2_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_oclc_v2_0-OCLC_v.0')
        expected = [
            u'Copyright (c) 2002. OCLC Research.',
            u'Copyright (c) 2000- (insert then current year)',
            u'Copyright (c) 2000- (insert then current year)',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_openldap(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_openldap-OpenLDAP')
        expected = [
            u'Copyright 1999-2003 The OpenLDAP Foundation, Redwood City, California',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_openmotif(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_openmotif-OpenMotif')
        expected = [
            u'Copyright (c) date here, The Open Group Ltd.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_openpbs(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_openpbs-OpenPBS')
        expected = [
            u'Copyright (c) 1999-2000 Veridian Information Solutions, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_openpublicationref(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_openpublicationref-OpenPublicationref')
        expected = [
            u'Copyright (c) 2000 by ThisOldHouse.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_openssl(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_openssl-OpenSSL')
        expected = [
            u'Copyright (c) 1998-2000 The OpenSSL Project.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_osl_v3_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_osl_v3_0-OSL_v.0')
        expected = [
            u'Copyright (c) 2005 Lawrence Rosen.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_phorum(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_phorum-Phorum')
        expected = [
            u'Copyright (c) 2001 The Phorum Development Team.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_pine(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_pine-Pine')
        expected = [
            u'Copyright 1989-2007 by the University of Washington.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_python_v1_6(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_python_v1_6-Python_v.6')
        expected = [
            u'Copyright (c) 1995-2000 Corporation for National Research Initiatives',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_python_v1_6_1(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_python_v1_6_1-Python_v.1')
        expected = [
            u'Copyright 1995-2001 Corporation for National Research Initiatives',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_python_v2(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_python_v2-Python_v')
        expected = [
            u'Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006 Python Software Foundation',
            u'Copyright (c) 1995-2001 Corporation for National Research Initiatives',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_qpl_v1_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_qpl_v1_0-QPL_v.0')
        expected = [
            u'Copyright (c) 1999 Trolltech AS',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_realcsl_v2_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_realcsl_v2_0-RealCSL_v.0')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_license_text_realpsl_v1_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_realpsl_v1_0-RealPSL_v.0')
        expected = [
            u'Copyright (c) 1995-2002 RealNetworks, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_realpsl_v1_0ref(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_realpsl_v1_0ref-RealPSL_v_ref.0ref')
        expected = [
            u'Copyright (c) 1995-2004 RealNetworks, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_reciprocal_v1_5(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_reciprocal_v1_5-Reciprocal_v.5')
        expected = [
            u'Copyright (c) 2001-2007 Technical Pursuit Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_redhateula(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_redhateula-RedHatEULA')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_license_text_redhatref(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_redhatref-RedHatref')
        expected = [
            u'Copyright (c) 2005 Red Hat, Inc.',
            u'Copyright (c) 1995-2005 Red Hat, Inc.',
            u'copyrighted by Red Hat, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_ricoh_v1_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_ricoh_v1_0-Ricoh_v.0')
        expected = [
            u'Ricoh Silicon Valley, Inc. are Copyright (c) 1995-1999.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_scilab(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_scilab-Scilab')
        expected = [
            u'Scilab (c) INRIA-ENPC.',
            u'Scilab (c) INRIA-ENPC.',
            u'Scilab (c) INRIA-ENPC.',
            u'Scilab (c) INRIA-ENPC.',
            u'Scilab inside (c) INRIA-ENPC',
            u'Scilab (c) INRIA-ENPC',
            u'Scilab (c) INRIA-ENPC',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_sgi_cid_v1_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_sgi_cid_v1_0-SGI_CID_v.0')
        expected = [
            u'Copyright (c) 1994-1999 Silicon Graphics, Inc.',
            u'Copyright (c) 1994-1999 Silicon Graphics, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_sgi_glx_v1_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_sgi_glx_v1_0-SGI_GLX_v.0')
        expected = [
            u'(c) 1991-9 Silicon Graphics, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_sissl_v1_1refa(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_sissl_v1_1refa-SISSL_v_refa.1refa')
        expected = [
            u'Copyright 2000 by Sun Microsystems, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_sleepycat(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_sleepycat-Sleepycat')
        expected = [
            u'Copyright (c) 1990-1999 Sleepycat Software.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_sybaseopenwatcom_v1_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_sybaseopenwatcom_v1_0-SybaseOpenWatcom_v.0')
        expected = [
            u'Copyright (c) 1983-2002 Sybase, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_uofu_rfpl(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_uofu_rfpl-UofU_RFPL')
        expected = [
            u'Copyright (c) 2001, 1998 University of Utah.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_vovida_v1_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_vovida_v1_0-Vovida_v.0')
        expected = [
            u'Copyright (c) 2000 Vovida Networks, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_wtfpl(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_wtfpl-WTFPL')
        expected = [
            u'Copyright (c) 2004 Sam Hocevar',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_x_net(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_x_net-X_Net.Net')
        expected = [
            u'Copyright (c) 2000-2001 X.Net, Inc. Lafayette, California',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_zend(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_zend-Zend')
        expected = [
            u'Copyright (c) 1999-2002 Zend Technologies Ltd.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_zliback(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_zliback-zLibAck')
        expected = [
            u'Copyright (c) 2002-2007 Charlie Poole',
            u'Copyright (c) 2002-2004 James W. Newkirk, Michael C. Two, Alexei A. Vorontsov',
            u'Copyright (c) 2000-2002 Philip A. Craig',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_zope_v1_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_zope_v1_0-Zope_v.0')
        expected = [
            u'Copyright (c) Digital Creations.',
        ]
        check_detection(expected, test_file)

    def test_copyright_license_text_zope_v2_0(self):
        test_file = self.get_test_loc('copyrights/copyright_license_text_zope_v2_0-Zope_v.0')
        expected = [
            u'Copyright (c) Zope Corporation (tm) and Contributors.',
        ]
        check_detection(expected, test_file)

    def test_copyright_linux_source_2_6_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_linux_source_2_6_copyright-linux_source__copyright.copyright')
        expected = [
            u'copyrighted by Linus Torvalds',
        ]
        check_detection(expected, test_file)

    def test_copyright_loss_of_holder_c(self):
        test_file = self.get_test_loc('copyrights/copyright_loss_of_holder_c-c.c')
        expected = [
            u'COPYRIGHT (c) DIONYSOS 2006 - 2009',
        ]
        check_detection(expected, test_file)

    def test_copyright_matroska_demux1_c(self):
        test_file = self.get_test_loc('copyrights/copyright_matroska_demux1_c-matroska_demux_c.c')
        expected = [
            u'(c) 2003 Ronald Bultje <rbultje@ronald.bitfreak.net>',
            u'(c) 2011 Debarshi Ray <rishi@gnu.org>',
        ]
        check_detection(expected, test_file)

    def test_copyright_matroska_demux_c(self):
        test_file = self.get_test_loc('copyrights/copyright_matroska_demux_c-matroska_demux_c.c')
        expected = [
            u'(c) 2006 Tim-Philipp Muller',
            u'(c) 2008 Sebastian Droge <slomo@circular-chaos.org>',
        ]
        check_detection(expected, test_file)

    def test_copyright_matroska_demux_muller_c(self):
        test_file = self.get_test_loc('copyrights/copyright_matroska_demux_muller_c-matroska_demux_c.c')
        expected = [
            u'(c) 2006 Tim-Philipp Muller',
            u'(c) 2008 Sebastian Droge <slomo@circular-chaos.org>',
        ]
        check_detection(expected, test_file)

    def test_copyright_memcmp_assembly(self):
        test_file = self.get_test_loc('copyrights/copyright_memcmp_assembly-9_9_memcmp_S.S')
        expected = [
            u'Copyright (c) 2007 ARC International (UK) LTD',
        ]
        check_detection(expected, test_file)

    def test_copyright_mergesort_java(self):
        test_file = self.get_test_loc('copyrights/copyright_mergesort_java-MergeSort_java.java')
        expected = [
            u'Copyright (c) 1998 Sun Microsystems, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_michal_txt(self):
        test_file = self.get_test_loc('copyrights/copyright_michal_txt.txt')
        expected = [
            u'copyright 2005 Michal Migurski',
        ]
        check_detection(expected, test_file)

    def test_copyright_mips1_be_elf_hal_o_uu(self):
        test_file = self.get_test_loc('copyrights/copyright_mips1_be_elf_hal_o_uu-mips_be_elf_hal_o_uu.uu')
        expected = [
            u'Copyright (c) 2002-2006 Sam Leffler, Errno Consulting, Atheros Communications, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_missing_statement_file_txt(self):
        test_file = self.get_test_loc('copyrights/copyright_missing_statement_file_txt-file.txt')
        expected = [
            u'Copyright 2003-2009 The Apache Geronimo development community',
            u'Copyright (c) 2000-2005 The Legion Of The Bouncy Castle',
        ]
        check_detection(expected, test_file)

    def test_copyright_mit(self):
        test_file = self.get_test_loc('copyrights/copyright_mit.txt')
        expected = [
            u'Copyright 2010-2011 by MitSomething',
        ]
        check_detection(expected, test_file)

    def test_copyright_mit_danse(self):
        test_file = self.get_test_loc('copyrights/copyright_mit_danse-MIT_Danse')
        expected = [
            u'Copyright (c) 2009 California Institute of Technology.',
        ]
        check_detection(expected, test_file)

    def test_copyright_mixedcaps_c(self):
        test_file = self.get_test_loc('copyrights/copyright_mixedcaps_c-mixedcaps_c.c')
        expected = [
            u'COPYRIGHT (c) 2006 MyCompany2 MYCOP',
            u'copyright (c) 2006 MyCompany2 MYCOP',
            u'COPYRIGHT (c) 2006 MYCOP MyCompany3',
            u'copyright (c) 2006 MYCOP MyCompany3',
            u'Copyright (c) 1993-95 NEC Systems Laboratory',
            u'COPYRIGHT (c) 1988-1994 PARADIGM BY CAMBRIDGE asSOCIATES INCORPORATED',
            u'Copyright (c) 2006, SHIMODA Hiroshi',
            u'Copyright (c) 2006, FUJITA Yuji',
            u'Copyright (c) 2007 GNOME i18n Project',
            u'Copyright 1996-2007 Glyph & Cog, LLC.',
            u'Copyright (c) 2002 Juan Carlos Arevalo-Baeza',
            u'Copyright (c) 2000 INRIA, France Telecom',
            u'Copyright (c) NEC Systems Laboratory 1993',
            u'Copyright (c) 1984 NEC Systems Laboratory',
            u'Copyright (c) 1996-2003 Glyph & Cog, LLC',
            u'Copyright (c) 1996. Zeus Technology Limited',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_copyright_mixedcase_company_name_in_c(self):
        test_file = self.get_test_loc('copyrights/copyright_mixedcase_company_name_in_c-lowercase_company_c.c')
        expected = [
            u'Copyright (c) 2001 nexB',
        ]
        check_detection(expected, test_file)

    def test_copyright_mkisofs_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_mkisofs_copyright-mkisofs_copyright.copyright')
        expected = [
            u'Copyright 1998-2003 Heiko Eissfeldt',
            u'(c) Peter Widow',
            u'(c) Thomas Niederreiter',
            u'(c) RSA Data Security, Inc.',
            u'Copyright 1993 Yggdrasil Computing, Incorporated',
            u'Copyright (c) 1999,2000-2004 J. Schilling',
            u'(c) 1998-2002 by Heiko Eissfeldt, heiko@colossus.escape.de',
            u'(c) 2002 by Joerg Schilling',
            u'(c) 1996, 1997 Robert Leslie',
            u'Copyright (c) 2002 J. Schilling',
            u'Copyright (c) 1987, 1995-2003 J. Schilling',
            u'Copyright 2001 H. Peter Anvin',
        ]
        check_detection(expected, test_file)

    def test_copyright_moto_broad(self):
        test_file = self.get_test_loc('copyrights/copyright_moto_broad-c.c')
        expected = [
            u'COPYRIGHT (c) 2005 MOTOROLA, BROADBAND COMMUNICATIONS SECTOR',
        ]
        check_detection(expected, test_file)

    def test_copyright_motorola_c(self):
        test_file = self.get_test_loc('copyrights/copyright_motorola_c-c.c')
        expected = [
            u'Copyright (c) 2003, 2010 Motorola, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_motorola_mobility_c(self):
        test_file = self.get_test_loc('copyrights/copyright_motorola_mobility_c-c.c')
        expected = [
            u'Copyright (c) 2009 Motorola, Inc.',
            u'Copyright (c) 2011 Motorola Mobility, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_mplayer_skin_blue_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_mplayer_skin_blue_copyright-mplayer_skin_blue_copyright.copyright')
        expected = [
            u'Copyright (c) 2005-06 Franciszek Wilamowski, xenomorph@irc.pl',
        ]
        check_detection(expected, test_file)

    def test_copyright_muller(self):
        test_file = self.get_test_loc('copyrights/copyright_muller-c.c')
        expected = [
            u'(c) 2003 Ronald Bultje <rbultje@ronald.bitfreak.net>',
            u'(c) 2006 Tim-Philipp Muller',
            u'(c) 2008 Sebastian Droge <slomo@circular-chaos.org>',
            u'(c) 2011 Debarshi Ray <rishi@gnu.org>',
        ]
        check_detection(expected, test_file)

    def test_copyright_multiline(self):
        test_file = self.get_test_loc('copyrights/copyright_multiline-Historical.txt')
        expected = [
            u'COPYRIGHT (c) 1990-1994 BY GEORGE J. CARRETTE, CONCORD, MASSACHUSETTS.',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_copyright_multiline_george(self):
        test_file = self.get_test_loc('copyrights/copyright_multiline_george-Historical.txt')
        expected = [
            u'COPYRIGHT (c) 1990-1994 BY GEORGE',
        ]
        check_detection(expected, test_file)

    def test_copyright_mycorp_c(self):
        test_file = self.get_test_loc('copyrights/copyright_mycorp_c-c.c')
        expected = [
            u'Copyright (c) 2012 MyCorp Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_name_before_copyright_c(self):
        test_file = self.get_test_loc('copyrights/copyright_name_before_copyright_c-c.c')
        expected = [
            u'Russ Dill <Russ.Dill@asu.edu> 2001-2003',
            u'Vladimir Oleynik <dzo@simtreas.ru> (c) 2003'
        ]
        check_detection(expected, test_file)

    def test_copyright_name_sign_year(self):
        test_file = self.get_test_loc('copyrights/copyright_name_sign_year_correct-c.c')
        expected = [
            'Copyright (c) 2008 Daisy Ltd.',
            'Daisy (c) 1997 - 2008',
        ]
        check_detection(expected, test_file)

    def test_copyright_naumen_txt(self):
        test_file = self.get_test_loc('copyrights/copyright_naumen_txt.txt')
        expected = [
            u'Copyright (c) NAUMEN (tm) and Contributors.',
        ]
        check_detection(expected, test_file)

    def test_copyright_ncurses_bin_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_ncurses_bin_copyright-ncurses_bin_copyright.copyright')
        expected = [
            u'Copyright (c) 1998 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_nederlof(self):
        test_file = self.get_test_loc('copyrights/copyright_nederlof.txt')
        expected = [
            u'(c) 2005 - Peter Nederlof',
        ]
        check_detection(expected, test_file)

    def test_copyright_trailing_copyleft(self):
        test_file = self.get_test_loc('copyrights/copyright_trailing_copyleft.txt')
        expected = [
            u'Copyright (c) 1992 Ronald S. Karr',
        ]
        check_detection(expected, test_file)

    def test_copyright_no_copyright_in_c(self):
        test_file = self.get_test_loc('copyrights/copyright_no_copyright_in_c-c.c')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_no_copyright_in_class_file_2(self):
        test_file = self.get_test_loc('copyrights/copyright_no_copyright_in_class_file_2-PersistentElementHolder_class.class')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_no_copyright_in_class_file_3(self):
        test_file = self.get_test_loc('copyrights/copyright_no_copyright_in_class_file_3-PersistentIndexedElementHolder_class.class')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_no_copyright_in_class_file_4(self):
        test_file = self.get_test_loc('copyrights/copyright_no_copyright_in_class_file_4-PersistentListElementHolder_class.class')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_no_holder_java(self):
        test_file = self.get_test_loc('copyrights/copyright_no_holder_java-java.java')
        expected = [
            u'Copyright (c) 2005',
        ]
        check_detection(expected, test_file)

    def test_copyright_nokia_cpp(self):
        test_file = self.get_test_loc('copyrights/copyright_nokia_cpp-cpp.cpp')
        expected = [
            u'Copyright (c) 2002, Nokia Mobile Phones.',
        ]
        check_detection(expected, test_file)

    def test_copyright_north_c(self):
        test_file = self.get_test_loc('copyrights/copyright_north_c-99_c.c')
        expected = [
            u'Copyright (c) 2010 42North Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_notice2(self):
        test_file = self.get_test_loc('copyrights/copyright_notice2-9_NOTICE')
        expected = [
            u'Copyright 2003-2009 The Apache Geronimo development community',
        ]
        check_detection(expected, test_file)

    def test_copyright_notice2_txt(self):
        test_file = self.get_test_loc('copyrights/copyright_notice2_txt-NOTICE.txt')
        expected = [
            u'Copyright (c) 2004, Richard S. Hall',
            u'Copyright (c) 2002,2003, Stefan Haustein, Oberhausen',
            u'Copyright (c) 2002,2004, Stefan Haustein, Oberhausen',
            u'Copyright (c) 2002,2003, Stefan Haustein, Oberhausen',
        ]
        check_detection(expected, test_file)

    def test_copyright_notice_name_before_statement(self):
        test_file = self.get_test_loc('copyrights/copyright_notice_name_before_statement-NOTICE')
        expected = [
            u'iClick, Inc., software copyright (c) 1999.',
        ]
        check_detection(expected, test_file)

    def test_copyright_notice_txt(self):
        test_file = self.get_test_loc('copyrights/copyright_notice_txt-NOTICE.txt')
        expected = [
            u'Copyright 2003-2010 The Knopflerfish Project',
            u'Copyright (c) OSGi Alliance (2000, 2009).',
            u'Copyright (c) 2000-2005 INRIA, France Telecom',
            u'(c) 1999-2003.',
            u'(c) 2001-2004',
            u'Copyright (c) 2004, Didier Donsez',
            u'(c) 2001-2004 http://commons.apache.org/logging',
            u'(c) 1999-2003. http://xml.apache.org/dist/LICENSE.txt',
            u'(c) 2001-2004',
            u'Copyright (c) 2004, Richard S. Hall',
            u'(c) 2001-2004 http://xml.apache.org/xalan-j',
            u'(c) 2001-2004 http://xerces.apache.org',
        ]
        check_detection(expected, test_file)

    def test_copyright_o_brien_style_name(self):
        test_file = self.get_test_loc('copyrights/copyright_o_brien_style_name.txt')
        expected = [
            u"Copyright (c) 2001-2003, Patrick K. O'Brien",
        ]
        check_detection(expected, test_file)

    def test_copyright_oberhummer_c_code(self):
        test_file = self.get_test_loc('copyrights/copyright_oberhummer_c_code-c.c')
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

    def test_copyright_oberhummer_text(self):
        test_file = self.get_test_loc('copyrights/copyright_oberhummer_text.txt')
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

    def test_copyright_objectivec(self):
        test_file = self.get_test_loc('copyrights/copyright_objectivec-objectiveC_m.m')
        expected = [
            u'Copyright (c) 2009',
        ]
        check_detection(expected, test_file)

    def test_copyright_openhackware_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_openhackware_copyright_label-openhackware_copyright_label.label')
        expected = [
            u'Copyright (c) 2004-2005 Jocelyn Mayer <l_indien@magic.fr>',
            u'Copyright (c) 2004-2005 Fabrice Bellard',
        ]
        check_detection(expected, test_file)

    def test_copyright_openoffice_org_report_builder_bin_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_openoffice_org_report_builder_bin_copyright-openoffice_org_report_builder_bin_copyright.copyright')
        expected = [
            u'Copyright (c) 2002-2009 Software in the Public Interest, Inc.',
            u'Copyright (c) 2002-2009 ooo-build/Go-OO Team',
            u'(c) Sun Microsystems.',
            u'Copyright 2002-2009 Sun Microsystems, Inc.',
            u'Copyright 2002-2009 Sun Microsystems, Inc.',
            u'Copyright (c) 2002-2005 Maxim Shemanarev',
            u'Copyright 2001-2004 The Apache Software Foundation.',
            u'Copyright 2003-2007 The Apache Software Foundation',
            u'Copyright 2001-2007 The Apache Software Foundation',
            u'Copyright 1999-2007 The Apache Software Foundation',
            u'Copyright (c) 2000 Pat Niemeyer',
            u'Copyright (c) 2000',
            u'Copyright (c) 2002 France Telecom',
            u'Copyright (c) 1990-2003 Sleepycat Software',
            u'Copyright (c) 1990, 1993, 1994, 1995 The Regents of the University of California',
            u'Copyright (c) 2003 by Bitstream, Inc.',
            u'Cppyright Copyright (c) 2006 by Tavmjong Bah',
            u'Copyright (c) 2007 Red Hat, Inc',
            u'Copyright (c) 2007 Red Hat, Inc.',
            u'Copyright 2000-2003 Beman Dawes',
            u'Copyright (c) 1998-2003 Joel de Guzman',
            u'Copyright (c) 2001-2003 Daniel Nuffer',
            u'Copyright (c) 2001-2003 Hartmut Kaiser',
            u'Copyright (c) 2002-2003 Martin Wille',
            u'Copyright (c) 2002 Juan Carlos Arevalo-Baeza',
            u'Copyright (c) 2002 Raghavendra Satish',
            u'Copyright (c) 2002 Jeff Westfahl',
            u'Copyright (c) 2001 Bruce Florman',
            u'Copyright 1999 Tom Tromey',
            u'Copyright 2002, 2003 University of Southern California, Information Sciences Institute',
            u'Copyright 2004 David Reveman',
            u'Copyright 2000, 2002, 2004, 2005 Keith Packard',
            u'Copyright 2004 Calum Robinson',
            u'Copyright 2004 Richard D. Worth',
            u'Copyright 2004, 2005 Red Hat, Inc.',
            u'Copyright 2004 David Reveman',
            u'(c) Copyright 2000, Baptiste Lepilleur',
            u'Copyright (c) 1996 - 2004, Daniel Stenberg',
            u'Copyright (c) 1992,1994 by Dennis Vadura',
            u'Copyright (c) 1996 by WTI Corp.',
            u'Copyright 1999-2003 by Easy Software Products',
            u'Copyright (c) 1998, 1999 Thai Open Source Software Center Ltd',
            u'Copyright (c) 1987, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 2000 Free Software Foundation, Inc.',
            u'Copyright (c) 2000,2001,2002,2003 by George William',
            u'Copyright (c) 2001-2008, The HSQL Development Group',
            u'Copyright (c) 1995, 1997, 2000, 2001, 2002 Free Software Foundation, Inc.',
            u'Copyright (c) Kevin Hendricks',
            u'Copyright (c) 2002-2008 Laszlo Nemeth',
            u'Copyright (c) 2000 Bjoern Jacke',
            u'Copyright 2000 by Sun Microsystems, Inc.',
            u'Copyright (c) 1998 Raph Levien',
            u'Copyright (c) 2001 ALTLinux, Moscow',
            u'Copyright (c) 2006, 2007, 2008 Laszlo Nemeth',
            u'Copyright (c) 2003-2006 The International Color Consortiu',
            u'Copyright (c) 1995-2008 International Business Machines Corporation',
            u'Copyright 2000-2005, by Object Refinery Limited',
            u'Copyright 2005-2007, by Pentaho Corporation',
            u'Copyright 1994-2002 World Wide Web Consortium',
            u'Copyright (c) 1991-1998, Thomas G. Lane',
            u'Copyright 1994-2002 World Wide Web Consortium',
            u'Copyright (c) 2002 Anders Carlsson <andersca@gnu.org>',
            u'Copyright (c) 2003, WiseGuys Internet',
            u'Copyright (c) 2003, WiseGuys Internet',
            u'Copyright 1997-1999 World Wide Web Consortium',
            u'Copyright (c) 2002-2003 Aleksey Sanin',
            u'Copyright (c) 2003 America Online, Inc.',
            u'Copyright (c) 2001-2002 Daniel Veillard',
            u'Copyright (c) 1998-2001 by the University of Florida',
            u'Copyright (c) 1991, 2007 Free Software Foundation, Inc',
            u'Copyright 2004 The Apache Software Foundation',
            u'Copyright 2005 The Apache Software Foundation',
            u'Copyright 2007 The Apache Software Foundation',
            u'Copyright (c) 1999-2007 Brian Paul',
            u'Copyright (c) 2007 The Khronos Group Inc.',
            u'Copyright (c) 2003 Stuart Caie <kyzer@4u.net>',
            u'Copyright (c) 1999-2006 Joe Orton <joe@manyfish.co.uk>',
            u'Copyright (c) 1999-2000 Tommi Komulainen <Tommi.Komulainen@iki.fi>',
            u'Copyright (c) 1999-2000 Peter Boos <pedib@colorfullife.com>',
            u'Copyright (c) 1991, 1995, 1996, 1997 Free Software Foundation, Inc.',
            u'Copyright (c) 2004 Aleix Conchillo Flaque <aleix@member.fsf.org>',
            u'Copyright (c) 2004 Jiang Lei <tristone@deluxe.ocn.ne.jp>',
            u'Copyright (c) 2004-2005 Vladimir Berezniker',
            u'Copyright (c) 1998 Netscape Communications Corporation',
            u'Copyright (c) 1998-2007 The OpenSSL Project',
            u'Copyright (c) 1998-2007 The OpenSSL Project',
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 2001, 2002, 2003, 2004 Python Software Foundation',
            u'Copyright (c) 2000 BeOpen.com',
            u'Copyright (c) 1995-2001 Corporation for National Research Initiatives',
            u'Copyright (c) 1991-1995 Stichting Mathematisch Centrum',
            u'Copyright (c) 2000-2007 David Beckett',
            u'Copyright (c) 2000-2005 University of Bristol',
            u'Copyright (c) 1993, 94, 95, 96, 97, 98, 99 Free Software Foundation, Inc',
            u'Copyright (c) 1997-2000 Netscape Communications Corporation',
            u'Copyright (c) 2000 see Beyond Communications Corporation',
            u'Copyright (c) 1997 David Mosberger-Tang and Andreas Beck',
            u'Copyright (c) 1998, 1999 James Clark',
            u'Copyright ? 1999',
            u'Copyright (c) 2002-2003 Aleksey Sanin',
            u'Copyright (c) 2003 America Online, Inc.',
            u'Copyright (c) 2001-2002 Daniel Veillard',
            u'Copyright (c) 1998-2001 by the University of Florida',
            u'Copyright (c) 1991, 2007 Free Software Foundation, Inc',
            u'Copyright 2004 The Apache Software Foundation',
            u'Copyright 2005 The Apache Software Foundation',
            u'Copyright 2007 The Apache Software Foundation',
            u'Copyright (c) 1999-2007 Brian Paul',
            u'Copyright (c) 2007 The Khronos Group Inc.',
            u'Copyright (c) 2003 Stuart Caie <kyzer@4u.net>',
            u'Copyright (c) 1999-2006 Joe Orton <joe@manyfish.co.uk>',
            u'Copyright (c) 1999-2000 Tommi Komulainen <Tommi.Komulainen@iki.fi>',
            u'Copyright (c) 1999-2000 Peter Boos <pedib@colorfullife.com>',
            u'Copyright (c) 1991, 1995, 1996, 1997 Free Software Foundation, Inc.',
            u'Copyright (c) 2004 Aleix Conchillo Flaque <aleix@member.fsf.org>',
            u'Copyright (c) 2004 Jiang Lei <tristone@deluxe.ocn.ne.jp>',
            u'Copyright (c) 2004-2005 Vladimir Berezniker',
            u'Copyright (c) 1998 Netscape Communications Corporation',
            u'Copyright (c) 1998-2007 The OpenSSL Project',
            u'Copyright (c) 1998-2007 The OpenSSL Project',
            u'Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com)',
            u'Copyright (c) 2001, 2002, 2003, 2004 Python Software Foundation',
            u'Copyright (c) 2000 BeOpen.com',
            u'Copyright (c) 1995-2001 Corporation for National Research Initiatives',
            u'Copyright (c) 1991-1995 Stichting Mathematisch Centrum',
            u'Copyright (c) 2000-2007 David Beckett',
            u'Copyright (c) 2000-2005 University of Bristol',
            u'Copyright (c) 1993, 94, 95, 96, 97, 98, 99 Free Software Foundation, Inc',
            u'Copyright (c) 1997-2000 Netscape Communications Corporation',
            u'Copyright (c) 2000 see Beyond Communications Corporation',
            u'Copyright (c) 1997 David Mosberger-Tang and Andreas Beck',
            u'Copyright (c) 1998, 1999 James Clark',
            u'Copyright ? 1999',
            u'Copyright (c) 1994 Hewlett-Packard Company',
            u'Copyright (c) 1996-1999 Silicon Graphics Computer Systems, Inc.',
            u'Copyright (c) 1997 Moscow Center for SPARC Technology',
            u'Copyright (c) 1999, 2000, 2001 Boris Fomitchev',
            u'Copyright 1999-2002,2004 The Apache Software Foundation',
            u'Copyright (c) 1991, 1992 TWAIN Working Group',
            u'Copyright (c) 1997 TWAIN Working Group',
            u'Copyright (c) 1998 TWAIN Working Group',
            u'Copyright (c) 2000 TWAIN Working Group',
            u'Copyright 1998-2001 by Ullrich Koethe',
            u'Copyright 2004 by Urban Widmark',
            u'Copyright 2002-2007 by Henrik Just',
            u'Copyright (c) 2000, Compaq Computer Corporation',
            u'Copyright (c) 2002, Hewlett Packard, Inc',
            u'Copyright (c) 2000 SuSE, Inc.',
            u'Copyright 1996-2007 Glyph & Cog, LLC.',
            u'Copyright (c) 1995-2002 Jean-loup Gailly and Mark Adler',
        ]
        check_detection(expected, test_file)

    def test_copyright_openoffice_org_report_builder_bin_copyright2(self):
        test_file = self.get_test_loc('copyrights/copyright_openoffice_org_report_builder_bin_copyright2-openoffice_org_report_builder_bin_copyright.copyright2')
        expected = [
            u'Copyright (c) 1990, 1993, 1994, 1995 The Regents of the University of California',
            u'Copyright (c) 1995, 1996 The President and Fellows of Harvard University',
        ]
        check_detection(expected, test_file)

    def test_copyright_openssl(self):
        test_file = self.get_test_loc('copyrights/copyright_openssl-c.c')
        expected = [
            'Copyright (c) 1995-1997 Eric Young (eay@mincom.oz.au)',
        ]
        check_detection(expected, test_file)

    def test_copyright_partial_detection(self):
        test_file = self.get_test_loc('copyrights/copyright_partial_detection.txt')
        expected = [
            u'Copyright 1991 by the Massachusetts Institute of Technology',
            u'Copyright (c) 2001 AT&T',
            u'Copyright (c) 2004-2006 by Henrique de Moraes Holschuh <hmh@debian.org>',
            u'Copyright 2005-2007 Christopher Montgomery , Jean-Marc Valin , Timothy Terriberry',
            u'Copyright (c) 2007 James Newton-King',
            u'Copyright (c) 2006, SHIMODA Hiroshi <piro@p.club.ne.jp>',
            u'Copyright (c) 2006, FUJITA Yuji <yuji@webmasters.gr.jp>',
            u'Copyright (c) 2002-2009 ooo-build/Go-OO Team',
            u'Copyright (c) 2002-2009 Software in the Public Interest, Inc.',
            u'Copyright (c) 2004 by the Perl 5 Porters',
            u'Copyright (c) 2006 Academy of Motion Picture Arts and Sciences',
            u'Copyright (c) 1995-2000 Corporation for National Research Initiatives',
            u'Copyright (c) 2001 EU DataGrid',
            u'Copyright (c) 2000. OCLC Research',
            u'Copyright (c) 1999 Trolltech AS',
        ]
        check_detection(expected, test_file)

    def test_copyright_partial_detection_mit(self):
        test_file = self.get_test_loc('copyrights/copyright_partial_detection_mit.txt')
        expected = [
            u'Copyright 1991 by the Massachusetts Institute of Technology',
            u'Copyright (c) 2001 AT&T',
            u'Copyright (c) 2004-2006 by Henrique de Moraes Holschuh <hmh@debian.org>',
            u'Copyright 2005-2007 Christopher Montgomery , Jean-Marc Valin , Timothy Terriberry',
            u'Copyright (c) 2007 James Newton-King',
            u'Copyright (c) 2006, SHIMODA Hiroshi <piro@p.club.ne.jp>',
            u'Copyright (c) 2006, FUJITA Yuji <yuji@webmasters.gr.jp>',
            u'Copyright (c) 2002-2009 ooo-build/Go-OO Team',
            u'Copyright (c) 2002-2009 Software in the Public Interest, Inc.',
            u'Copyright (c) 2004 by the Perl 5 Porters',
            u'Copyright (c) 2006 Academy of Motion Picture Arts and Sciences',
            u'Copyright (c) 1995-2000 Corporation for National Research Initiatives',
            u'Copyright (c) 2001 EU DataGrid',
            u'Copyright (c) 2000. OCLC Research',
            u'Copyright (c) 1999 Trolltech AS',
        ]
        check_detection(expected, test_file)

    def test_copyright_perl_base_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_perl_base_copyright-perl_base_copyright.copyright')
        expected = [
            u'Copyright 1989-2001, Larry Wall',
            u'Copyright (c) 1995-2005 Jean-loup Gailly and Mark Adler',
            u'Copyright (c) 1991-2006 Unicode, Inc.',
            u'Copyright (c) 1991-2008 Unicode, Inc.',
            u'Copyright (c) 2004 by the Perl 5 Porters',
            u'copyright (c) 1994 by the Regents of the University of California',
            u'Copyright (c) 1994 The Regents of the University of California',
            u'Copyright (c) 1989, 1993 The Regents of the University of California',
            u'copyright (c) 1996-2007 Julian R Seward',
        ]
        check_detection(expected, test_file)

    def test_copyright_perl_module(self):
        test_file = self.get_test_loc('copyrights/copyright_perl_module-pm.pm')
        expected = [
            u'Copyright (c) 1995-2000 Name Surname',
        ]
        check_detection(expected, test_file)

    def test_copyright_peter_c(self):
        test_file = self.get_test_loc('copyrights/copyright_peter_c-c.c')
        expected = [
            u'(c) 2005 - Peter Nederlof',
        ]
        check_detection(expected, test_file)

    def test_copyright_php_lib(self):
        test_file = self.get_test_loc('copyrights/copyright_php_lib-php_embed_lib.lib')
        expected = [
            u'Copyright nexB and others (c) 2012',
        ]
        check_detection(expected, test_file)

    def test_copyright_piersol(self):
        test_file = self.get_test_loc('copyrights/copyright_piersol-TestMatrix_D_java.java')
        expected = [
            u'Copyright (c) 1998 Company PIERSOL Engineering Inc.',
            u'Copyright (c) 1998 Company PIERSOL Engineering Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_postgresql_8_3_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_postgresql_8_3_copyright_label-postgresql__copyright_label.label')
        expected = [
            u'Portions Copyright (c) 1996-2003, The PostgreSQL Global Development Group',
            u'Portions Copyright (c) 1994, The Regents of the University of California',
            u'Copyright (c) 1998, 1999 Henry Spencer',
        ]
        check_detection(expected, test_file)

    def test_copyright_prof_informatics(self):
        test_file = self.get_test_loc('copyrights/copyright_prof_informatics.txt')
        expected = [
            u'Professional Informatics (c) 1994',
        ]
        check_detection(expected, test_file)

    def test_copyright_professional_txt(self):
        test_file = self.get_test_loc('copyrights/copyright_professional_txt-copyright.txt')
        expected = [
            u'Professional Informatics (c) 1994',
        ]
        check_detection(expected, test_file)

    def test_copyright_properties(self):
        test_file = self.get_test_loc('copyrights/copyright_properties-properties.properties')
        expected = [
            u'(c) 2004-2007 Restaurant.',
        ]
        check_detection(expected, test_file)

    def test_copyright_psf_in_python(self):
        test_file = self.get_test_loc('copyrights/copyright_psf_in_python-BitVector_py.py')
        expected = [
            u'copyright (c) 2008 Avinash Kak. Python Software Foundation.',
        ]
        check_detection(expected, test_file)

    def test_copyright_python_dateutil_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_python_dateutil_copyright-python_dateutil_copyright.copyright')
        expected = [
            u'Copyright (c) 2001, 2002 Python Software Foundation',
            u'Copyright (c) 1995-2001 Corporation for National Research Initiatives',
            u'Copyright (c) 1991 - 1995, Stichting Mathematisch Centrum Amsterdam',
        ]
        check_detection(expected, test_file)

    def test_copyright_python_psyco_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_python_psyco_copyright-python_psyco_copyright.copyright')
        expected = [
            u'Copyright (c) 2001-2003 Armin Rigo',
        ]
        check_detection(expected, test_file)

    def test_copyright_python_reportbug_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_python_reportbug_copyright_label-python_report_copyright_label.label')
        expected = [
            u'Copyright (c) 1999-2006 Chris Lawrence',
            u'Copyright (c) 2008-2009 Sandro Tosi <morph@debian.org>',
            u'Copyright (c) 1996-2000 Christoph Lameter <clameter@debian.org>',
            u'(c) 1996-2000 Nicolas Lichtmaier <nick@debian.org>',
            u'(c) 2000 Chris Lawrence <lawrencc@debian.org>',
            u'Copyright (c) 2008 Ben Finney <ben+debian@benfinney.id.au>',
            u'Copyright (c) 2008 Ben Finney <ben+debian@benfinney.id.au>',
            u'Copyright (c) 2008 Sandro Tosi <morph@debian.org>',
            u'Copyright (c) 2006 Philipp Kern <pkern@debian.org>',
            u'Copyright (c) 2008-2009 Luca Bruno <lethalman88@gmail.com>',
        ]
        check_detection(expected, test_file)

    def test_copyright_python_software_properties_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_python_software_properties_copyright-python_software_properties_copyright.copyright')
        expected = [
            u'Copyright 2004-2007 Canonical Ltd. 2004-2005 Michiel Sikkes 2006',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_copyright_red_hat_openoffice_org_report_builder_bin_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_red_hat_openoffice_org_report_builder_bin_copyright-openoffice_org_report_builder_bin_copyright.copyright')
        expected = [
            u'Copyright (c) 2007 Red Hat, Inc',
            u'Copyright (c) 2007 Red Hat, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_regents_complex(self):
        test_file = self.get_test_loc('copyrights/copyright_regents_complex-strtol_c.c')
        expected = [
            'Copyright (c) 1990 The Regents of the University of California.',
        ]
        check_detection(expected, test_file)

    @expectedFailure
    def test_copyright_regents_license(self):
        test_file = self.get_test_loc('copyrights/copyright_regents_license-LICENSE')
        expected = [
            u'copyrighted by The Regents of the University of California.',
            u'Copyright 1979, 1980, 1983, 1986, 1988, 1989, 1991, 1992, 1993, 1994 The Regents of the University of California.',
            u'copyright C 1988 by the Institute of Electrical and Electronics Engineers, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_resig_js(self):
        test_file = self.get_test_loc('copyrights/copyright_resig_js-js.js')
        expected = [
            u'Copyright (c) 2009 John Resig',
        ]
        check_detection(expected, test_file)

    def test_copyright_rusty(self):
        test_file = self.get_test_loc('copyrights/copyright_rusty.txt')
        expected = [
            u'(c) Rusty Russell, IBM 2002',
        ]
        check_detection(expected, test_file)

    def test_copyright_rusty_c(self):
        test_file = self.get_test_loc('copyrights/copyright_rusty_c-c.c')
        expected = [
            u'(c) Rusty Russell, IBM 2002',
        ]
        check_detection(expected, test_file)

    def test_copyright_s_fabsl_c(self):
        test_file = self.get_test_loc('copyrights/copyright_s_fabsl_c-s_fabsl_c.c')
        expected = [
            u'Copyright (c) 2003 Dag-Erling Coidan Smrgrav',
        ]
        check_detection(expected, test_file)

    def test_copyright_sample_java(self):
        test_file = self.get_test_loc('copyrights/copyright_sample_java-java.java')
        expected = [
            u'Copyright (c) 2000-2007, Sample ABC Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_sample_no_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_sample_no_copyright-c.c')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_seahorse_plugins(self):
        test_file = self.get_test_loc('copyrights/copyright_seahorse_plugins-seahorse_plugins_copyright.copyright')
        expected = [
            u'Copyright (c) 2004-2007 Stefan Walter',
            u'Copyright (c) 2004-2006 Adam Schreiber',
            u'Copyright (c) 2001-2003 Jose Carlos Garcia Sogo',
            u'Copyright (c) 2002, 2003 Jacob Perkins',
            u'Copyright (c) 2004, 2006 Nate Nielsen',
            u'Copyright (c) 2000-2004 Marco Pesenti Gritti',
            u'Copyright (c) 2003-2006 Christian Persch',
            u'Copyright (c) 2004, 2006 Jean-Francois Rameau',
            u'Copyright (c) 2000, 2001 Eazel, Inc.',
            u'Copyright (c) 2007, 2008 Jorge Gonzalez',
            u'Copyright (c) 2007, 2008 Daniel Nylander',
            u'Copyright (c) 2004-2005 Shaun McCance',
            u'Copyright (c) 2007 Milo Casagrande',
            u'Copyright (c) 2007-2008 Claude Paroz',
            u'Copyright (c) 2007 GNOME',
            # Copyright © 2008 <s>Василий Фаронов</s>
            u'i18n Project for Vietnamese Copyright (c) 2008',
            u'Copyright (c) 1992-2008 Free Software Foundation, Inc.',
            u'Copyright (c) 1999 Dave Camp',
            u'Copyright (c) 2005 Tecsidel S.A.',
            u'Copyright (c) 2004-2005 Adam Weinberger',
            u'Copyright (c) 2007, 2008 The GNOME Project',
            u'Copyright (c) 2007 Swecha Telugu Localisation Team',
            u'Copyright (c) 1995-1997 Ulrich Drepper',
            u'Copyright (c) 2004-2008 Rodney Dawes',
            u'Copyright (c) 1999, 2000 Anthony Mulcahy',
            u'Copyright (c) 2007 Ihar Hrachyshka',
            u'Copyright (c) 2004, 2005 Miloslav Trmac',
            u'Copyright (c) 2003 Peter Mato',
            u'Copyright (c) 2004, 2005 Danijel Studen , Denis Lackovic , Ivan Jankovic',
            u'Copyright (c) 1994 X Consortium',
            u'Copyright (c) 2006 Alexander Larsson',
            u'Copyright (c) 2000-2003 Ximian Inc.',
            u'Copyright (c) 1995-1997 Peter Mattis , Spencer Kimball and Josh MacDonald',
            u'Copyright (c) 1999, 2000 Robert Bihlmeyer',
            u'Copyright (c) Crispin Flowerday',
            u'Copyright (c) 2008 Frederic Peters',
            u'Copyright (c) 2008 Lucas Lommer',
            u'Copyright (c) 2008 Mario Blattermann',
            u'Copyright (c) 2001-2004 Red Hat, Inc.',
            u'Copyright (c) 2004 Scott James Remnant',
            # note this is not correct and severaly truncated
            u'Copyright (c) 1998-2006 by the following: Dave Ahlswede, Manuel Amador, Matt Amato, Daniel Atallah, Paul Aurich, Patrick Aussems, Anibal Avelar, Alex Badea, John Bailey, Chris Banal, Luca Barbato, Levi Bard, Kevin Barry, Derek Battams, Martin Bayard, Curtis Beattie, Dave Bell, Igor Belyi, Brian Bernas, Paul Betts, Jonas Birme, Eric Blade, Ethan Blanton, Joshua Blanton, Rainer Blessing, Herman Bloggs, David Blue, Jason Boerner, Graham Booker, Paolo Borelli, Julien Bossart, Craig Boston, Chris Boyle, Derrick J Brashear, Matt Brenneke, Jeremy Brooks, Philip Brown, Sean Burke, Thomas Butter, Andrea Canciani, Damien Carbery, Michael Carlson, Keegan Carruthers-Smith, Steve Cavilia, Julien Cegarra, Cerulean Studios, LLC',
            u'Copyright (c) 2008 Sebastien Bacher , Andreas Moog , Emilio Pozuelo Monfort and Josselin Mouette',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_copyright_simgear1_0_0_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_simgear1_0_0_copyright-simgear__copyright.copyright')
        expected = [
            u'Copyright (c) 1999-2000 Curtis L. Olson <curt@flightgear.org>',
            u'Copyright (c) 2002-2004 Mark J. Harris',
        ]
        check_detection(expected, test_file)

    def test_copyright_snippet_no_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_snippet_no_copyright')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_snmptrapd_c(self):
        test_file = self.get_test_loc('copyrights/copyright_snmptrapd_c-snmptrapd_c.c')
        expected = [
            u'Copyright 1989, 1991, 1992 by Carnegie Mellon University',
        ]
        check_detection(expected, test_file)

    def test_copyright_some_co(self):
        test_file = self.get_test_loc('copyrights/copyright_some_co-9_h.h')
        expected = [
            u'Copyright Some Company, inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_somefile_cpp(self):
        test_file = self.get_test_loc('copyrights/copyright_somefile_cpp-somefile_cpp.cpp')
        expected = [
            u'(c) 2005',
            u'Copyright Private Company (PC) Property of Private Company',
            u'Copyright (2003) Private Company',
        ]
        check_detection(expected, test_file)

    def test_copyright_source_auditor_projectinfo_java(self):
        test_file = self.get_test_loc('copyrights/copyright_source_auditor_projectinfo_java-ProjectInfo_java.java')
        expected = [
            u'Copyright (c) 2009 Source Auditor Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_stacktrace_cpp(self):
        test_file = self.get_test_loc('copyrights/copyright_stacktrace_cpp-stacktrace_cpp.cpp')
        expected = [
            u'Copyright 2003, 2004 Rickard E. Faith (faith@dict.org)',
        ]
        check_detection(expected, test_file)

    def test_copyright_stmicro_in_h(self):
        test_file = self.get_test_loc('copyrights/copyright_stmicro_in_h-h.h')
        expected = [
            u'COPYRIGHT (c) ST-Microelectronics 1998.',
        ]
        check_detection(expected, test_file)

    def test_copyright_stmicro_in_txt(self):
        test_file = self.get_test_loc('copyrights/copyright_stmicro_in_txt.txt')
        expected = [
            u'COPYRIGHT (c) STMicroelectronics 2005.',
            u'COPYRIGHT (c) ST-Microelectronics 1998.',
        ]
        check_detection(expected, test_file)

    def test_copyright_strchr_assembly(self):
        test_file = self.get_test_loc('copyrights/copyright_strchr_assembly-9_9_strchr_S.S')
        expected = [
            u'Copyright (c) 2007 ARC International (UK) LTD',
        ]
        check_detection(expected, test_file)

    def test_copyright_super_tech_c(self):
        test_file = self.get_test_loc('copyrights/copyright_super_tech_c-c.c')
        expected = [
            u'Copyright (c) $LastChangedDate$ Super Technologies Corporation, Cedar Rapids, Iowa',
            u'Copyright (c) 2004 Benjamin Herrenschmuidt (benh@kernel.crashing.org), IBM Corp.',
        ]
        check_detection(expected, test_file)

    @expectedFailure
    def test_copyright_tcl_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_tcl_copyright-tcl_copyright.copyright')
        expected = [
            u'copyrighted by the Regents of the University of California , Sun Microsystems, Inc. , Scriptics Corporation',  # not found, rather complex
            u'Copyright (c) 2007 Software in the Public Interest',
        ]
        check_detection(expected, test_file)

    def test_copyright_tech_sys(self):
        test_file = self.get_test_loc('copyrights/copyright_tech_sys.txt')
        expected = [
            u'(c) Copyright 1985-1999 SOME TECHNOLOGY SYSTEMS',
        ]
        check_detection(expected, test_file)

    def test_copyright_texinfo_tex(self):
        test_file = self.get_test_loc('copyrights/copyright_texinfo_tex-texinfo_tex.tex')
        expected = [
            u'Copyright (c) 1985, 1986, 1988, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_copyright_texlive_lang_greek_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_texlive_lang_greek_copyright-texlive_lang_greek_copyright.copyright')
        expected = [
            u'Copyright 1999 2002-2006 LaTeX3 Project',
            u'Copyright 2005 M. Y. Name',
        ]
        check_detection(expected, test_file)

    def test_copyright_texlive_lang_spanish_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_texlive_lang_spanish_copyright-texlive_lang_spanish_copyright.copyright')
        expected = [
            u'Copyright 1999 2002-2006 LaTeX3 Project',
            u'Copyright 2005 M. Y. Name',
        ]
        check_detection(expected, test_file)

    def test_copyright_texlive_lang_vietnamese_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_texlive_lang_vietnamese_copyright_label-texlive_lang_vietnamese_copyright_label.label')
        expected = [
            u'Copyright 1999 2002-2006 LaTeX3 Project',
            u'Copyright 2005 M. Y. Name',
        ]
        check_detection(expected, test_file)

    def test_copyright_tfc_c(self):
        test_file = self.get_test_loc('copyrights/copyright_tfc_c-c.c')
        expected = [
            u'Copyright 1991, 1992, 1993, 1994, 1995, 1996, 1998, 1999, 2000, 2001 Traditional Food Consortium, Inc.',
            u'Copyright 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007 Traditional Food Consortium, Inc.',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_copyright_thirdpartyproject_prop(self):
        test_file = self.get_test_loc('copyrights/copyright_thirdpartyproject_prop-ThirdPartyProject_prop.prop')
        expected = [
            u'Copyright 2010 Google Inc.',
        ]
        check_detection(expected, test_file)

    @expectedFailure
    def test_copyright_trailing_For(self):
        test_file = self.get_test_loc('copyrights/copyright_trailing_For-copyright_c.c')
        expected = [
            u'Copyright . 2008 Mycom Pany, inc.',
            u'Copyright (c) 1995-2003 Jean-loup Gailly.',
        ]
        check_detection(expected, test_file,
                        expected_in_results=True,
                        results_in_expected=False)

    def test_copyright_trailing_name(self):
        test_file = self.get_test_loc('copyrights/copyright_trailing_name-copyright.txt')
        expected = [
            u'Copyright (c) 1998, 1999, 2000 Thai Open Source Software Center Ltd and Clark Cooper',
        ]
        check_detection(expected, test_file,
                        expected_in_results=False,
                        results_in_expected=True)

    def test_copyright_trailing_redistribution(self):
        test_file = self.get_test_loc('copyrights/copyright_trailing_redistribution-bspatch_c.c')
        expected = [
            u'Copyright (c) 2008 The Android Open Source Project',
            u'Copyright 2003-2005 Colin Percival',
        ]
        check_detection(expected, test_file)

    def test_copyright_transcode_doc_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_transcode_doc_copyright-transcode_doc_copyright.copyright')
        expected = [
            u'Copyright (c) 2001 Thomas Ostreich',
        ]
        check_detection(expected, test_file)

    def test_copyright_transfig_copyright_with_parts(self):
        test_file = self.get_test_loc('copyrights/copyright_transfig_copyright_with_parts-transfig_copyright.copyright')
        expected = [
            u'Copyright (c) 1985-1988 Supoj Sutantavibul',
            u'Copyright (c) 1991-1999 Micah Beck',
            u'Copyright (c) 1989-2002 by Brian V. Smith',
            u'Copyright (c) 1991 by Paul King',
            u'Copyright (c) 1995 C. Blanc and C. Schlick',
            u'Copyright (c) 1993 Anthony Starks',
            u'Copyright (c) 1992 Uri Blumenthal',
            u'Copyright (c) 1992 by Brian Boyter',
            u'Copyright (c) 1995 Dane Dwyer',
            u'Copyright (c) 1999 by Philippe Bekaert',
            u'Copyright (c) 1999 by T. Sato',
            u'Copyright (c) 1998 by Mike Markowski',
            u'Copyright (c) 1994-2002 by Thomas Merz',
            u'Copyright (c) 2002-2006 by Martin Kroeker',
            u'Copyright 1990, David Koblas',
            u'Copyright, 1987, Massachusetts Institute of Technology',
            u'Copyright (c) 2006 Michael Pfeiffer p3fff@web.de',
        ]
        check_detection(expected, test_file)

    def test_copyright_treetablemodeladapter_java(self):
        test_file = self.get_test_loc('copyrights/copyright_treetablemodeladapter_java-TreeTableModelAdapter_java.java')
        expected = [
            u'Copyright 1997, 1998 by Sun Microsystems, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_truncated_dmv_c(self):
        test_file = self.get_test_loc('copyrights/copyright_truncated_dmv_c-9_c.c')
        expected = [
            u'Copyright (c) 1995 DMV - DigiMedia Vision',
        ]
        check_detection(expected, test_file)

    def test_copyright_truncated_doe(self):
        test_file = self.get_test_loc('copyrights/copyright_truncated_doe-c.c')
        expected = [
            u'Copyright (c) 2008 by John Doe',
        ]
        check_detection(expected, test_file)

    def test_copyright_truncated_inria(self):
        test_file = self.get_test_loc('copyrights/copyright_truncated_inria.txt')
        expected = [
            u'(c) 1998-2000 (W3C) MIT, INRIA, Keio University',
        ]
        check_detection(expected, test_file)

    def test_copyright_truncated_rusty(self):
        test_file = self.get_test_loc('copyrights/copyright_truncated_rusty-c.c')
        expected = [
            u'(c) 1999-2001 Paul Rusty Russell',
        ]
        check_detection(expected, test_file)

    def test_copyright_truncated_swfobject_js(self):
        test_file = self.get_test_loc('copyrights/copyright_truncated_swfobject_js-swfobject_js.js')
        expected = [
            u'Copyright (c) 2007-2008 Geoff Stearns, Michael Williams, and Bobby van der Sluis',
        ]
        check_detection(expected, test_file)

    def test_copyright_ttf_malayalam_fonts_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_ttf_malayalam_fonts_copyright-ttf_malayalam_fonts_copyright.copyright')
        expected = [
            u'Copyright (c) Jeroen Hellingman <jehe@kabelfoon.nl> , N.V Shaji <nvshaji@yahoo.com>',
            u'Copyright (c) 2004 Kevin',
            u'Copyright (c) Suresh',
            u'Copyright (c) 2007 Hiran Venugopalan',
            u'Copyright (c) 2007 Hussain',
            u'Copyright (c) 2005 Rachana Akshara Vedi',
            u'Copyright (c) CDAC, Mumbai Font Design',
            u'Copyright (c) 2003 Modular Infotech, Pune',
            u'Copyright (c) 2006 Modular Infotech Pvt Ltd.',
            u'Copyright (c) 2009 Red Hat, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_tunnel_h(self):
        test_file = self.get_test_loc('copyrights/copyright_tunnel_h-tunnel_h.h')
        expected = [
            u'Copyright (c) 2000 Frank Strauss <strauss@ibr.cs.tu-bs.de>',
        ]
        check_detection(expected, test_file)

    def test_copyright_two_digits_years(self):
        test_file = self.get_test_loc('copyrights/copyright_two_digits_years-digits_c.c')
        expected = [
            'Copyright (c) 1987,88,89,90,91,92,93,94,96,97 Free Software Foundation, Inc.',
        ]
        check_detection(expected, test_file)

    @expectedFailure
    def test_copyright_url_in_html(self):
        test_file = self.get_test_loc('copyrights/copyright_url_in_html-detail_9_html.html')
        expected = [
            '(c) 2004-2009 pudn.com',
        ]
        check_detection(expected, test_file)

    def test_copyright_utilities_js(self):
        test_file = self.get_test_loc('copyrights/copyright_utilities_js-utilities_js.js')
        expected = [
            u'Copyright (c) 2009, Yahoo! Inc.',
            u'Copyright 2001 Robert Penner',
        ]
        check_detection(expected, test_file)

    def test_copyright_var_route_c(self):
        test_file = self.get_test_loc('copyrights/copyright_var_route_c-var_route_c.c')
        expected = [
            u'Copyright 1988, 1989 by Carnegie Mellon University',
            u'Copyright 1989 TGV, Incorporated',
            u'Erik Schoenfelder (schoenfr@ibr.cs.tu-bs.de) 1994/1995.',
            u'Simon Leinen (simon@switch.ch) 1997',
        ]
        check_detection(expected, test_file)

    def test_copyright_view_layout2_xml(self):
        test_file = self.get_test_loc('copyrights/copyright_view_layout2_xml-view_layout_xml.xml')
        expected = [
            u'Copyright (c) 2008 Esmertec AG.',
        ]
        check_detection(expected, test_file)

    def test_copyright_warning_parsing_empty_text(self):
        test_file = self.get_test_loc('copyrights/copyright_warning_parsing_empty_text-controlpanel_anjuta.anjuta')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_web_app_dtd__b_sun(self):
        test_file = self.get_test_loc('copyrights/copyright_web_app_dtd_b_sun-web_app__dtd.dtd')
        expected = [
            u'Copyright 2000-2007 Sun Microsystems, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_web_app_dtd_sun_twice(self):
        test_file = self.get_test_loc('copyrights/copyright_web_app_dtd_sun_twice-web_app__b_dtd.dtd')
        expected = [
            u'Copyright (c) 2000 Sun Microsystems, Inc.',
            u'Copyright (c) 2000 Sun Microsystems, Inc.',
        ]
        check_detection(expected, test_file)

    def test_copyright_wide_c(self):
        test_file = self.get_test_loc('copyrights/copyright_wide_c-c.c')
        expected = [
            u'Copyright (c) 1995, 1996, 1997, and 1998 WIDE Project.',
        ]
        check_detection(expected, test_file)

    def test_copyright_wide_txt(self):
        test_file = self.get_test_loc('copyrights/copyright_wide_txt.txt')
        expected = [
            u'Copyright (c) 1995, 1996, 1997, and 1998 WIDE Project.',
        ]
        check_detection(expected, test_file)

    def test_copyright_with_verbatim_lf(self):
        test_file = self.get_test_loc('copyrights/copyright_with_verbatim_lf-verbatim_lf_c.c')
        expected = [
            u'Copyright 2003-2005 Colin Percival',
        ]
        check_detection(expected, test_file)

    def test_copyright_xconsortium_sh(self):
        test_file = self.get_test_loc('copyrights/copyright_xconsortium_sh-9_sh.sh')
        expected = [
            u'Copyright (c) 1994 X Consortium',
        ]
        check_detection(expected, test_file)

    def test_copyright_xfonts_utils_copyright(self):
        test_file = self.get_test_loc('copyrights/copyright_xfonts_utils_copyright-xfonts_utils_copyright.copyright')
        expected = [
            u'Copyright 1991, 1993, 1998 The Open Group',
            u'Copyright 2005 Red Hat, Inc.',
            u'Copyright 2005 Red Hat, Inc',
            u'Copyright (c) 1991-2003 Unicode, Inc.',
            u'Copyright (c) 2003 The NetBSD Foundation, Inc.',
            u'Copyright (c) 2006 Martin Husemann.',
            u'Copyright (c) 2007 Joerg Sonnenberger.',
            u'Copyright (c) 2002-2008 by Juliusz Chroboczek',
            u'Copyright (c) 1987, 1993 The Regents of the University of California.',
            u'Copyright 1993, 1994, 1998 The Open Group',
            u'Copyright (c) 2002-2008 by Juliusz Chroboczek',
            u'Copyright 1999, 2001, 2002, 2004 Branden Robinson',
            u'Copyright 2006 Steve Langasek',
            u'Copyright 1999, 2001, 2002, 2004 Branden Robinson',
            u'Copyright 1999-2002, 2004 Branden Robinson',
            u'Copyright 2006 Steve Langasek',
        ]
        check_detection(expected, test_file)

    def test_copyright_xresprobe_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_xresprobe_copyright_label-xresprobe_copyright_label.label')
        expected = [
            u'copyright (c) 2004 Canonical Software',
            u'Copyright (c) 2002 Terra Soft Solutions, Inc.',
            u'Copyright (c) 1998 by Josh Vanderhoof',
            u'Copyright (c) 1996-1999 SciTech Software, Inc.',
            u'copyright (c) David Mosberger-Tang',
            u'Copyright (c) 1999 Egbert Eich',
        ]
        check_detection(expected, test_file)

    def test_copyright_xsane_copyright_label(self):
        test_file = self.get_test_loc('copyrights/copyright_xsane_copyright_label-xsane_copyright_label.label')
        expected = [
            u'Copyright (c) 1998-2005 Oliver Rauch',
        ]
        check_detection(expected, test_file)

    def test_copyright_does_not_return_junk_in_pdf(self):
        # from https://github.com/ttgurney/yocto-spdx/blob/master/doc/Yocto-SPDX_Manual_Install_Walkthrough.pdf
        test_file = self.get_test_loc('copyrights/copyright_Yocto-SPDX.pdf')
        expected = [
        ]
        check_detection(expected, test_file)

    def test_copyright_name_and_co(self):
        test_file = self.get_test_loc('copyrights/copyright_nnp_and_co.txt')
        expected = [
            u'Copyright (c) 2001, Sandra and Klaus Rennecke.',
        ]
        check_detection(expected, test_file)

    def test_copyright_with_ascii_art(self):
        test_file = self.get_test_loc('copyrights/copyright_with_ascii_art.txt')
        expected = [
            u'Copyright (c) 1996. The Regents of the University of California.',
        ]
        check_detection(expected, test_file)

    def test_copyright_should_not_be_detected_in_pixel_data_stream(self):
        test_file = self.get_test_loc('copyrights/copyright_pixelstream.rgb')
        expected = []
        check_detection(expected, test_file)

    def test_copyright_should_not_contain_leading_or_trailing_colon(self):
        test_file = self.get_test_loc('copyrights/copyright_with_colon')
        expected = ['copyright (c) 2013 by Armin Ronacher.']
        check_detection(expected, test_file)

    @expectedFailure
    def test_copyright_in_markup_should_not_be_truncated(self):
        test_file = self.get_test_loc('copyrights/copyright_in_html.html')
        expected = [u'(c) Copyright 2010 by the WTForms Team']
        check_detection(expected, test_file)

    def test_copyright_should_not_have_trailing_garbage(self):
        test_file = self.get_test_loc('copyrights/copyright_with_trailing_words.js')
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

    def test_copyright_should_not_have_trailing_available(self):
        test_file = self.get_test_loc('copyrights/copyright_hostapd_trailing_available.c')
        expected = [u'Copyright (c) 2004-2005, Jouni Malinen <jkmaline@cc.hut.fi>']
        check_detection(expected, test_file)
