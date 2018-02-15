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

from __future__ import absolute_import, print_function

import os.path

from commoncode.testcase import FileBasedTesting
from cluecode import copyrights as copyrights_module


class TestTextPreparation(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_strip_numbers(self):
        a = 'Python 2.6.6 (r266:84297, Aug 24 2010, 18:46:32) [MSC v.1500 32 bit (Intel)] on win32'
        expected = 'Python 2.6.6 (r266:84297, Aug 2010, 18:46:32) [MSC v.1500 bit (Intel)] on win32'
        assert expected == copyrights_module.strip_numbers(a)

    def test_prepare_text(self):
        cp = ''' test (C) all rights reserved'''
        result = copyrights_module.prepare_text_line(cp)
        assert 'test (c) all rights reserved' == result

    def test_is_all_rights_reserved(self):
        line = '''          "All rights reserved\\n"'''
        _line, char_only_line = copyrights_module.prep_line(line)
        assert copyrights_module.is_all_rights_reserved(char_only_line)

    def test_candidate_lines_simple(self):
        lines = ''' test (C) all rights reserved'''.splitlines(False)
        result = list(copyrights_module.candidate_lines(lines))
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

        result = list(copyrights_module.candidate_lines(lines))
        assert expected == result

    def test_is_candidates_should_not_select_line_with_bare_full_year(self):
        line = '2012'
        line, _char_only = copyrights_module.prep_line(line)
        assert not copyrights_module.is_candidate(line)

    def test_is_candidates_should_not_select_line_with_full_year_before_160_and_after_2018(self):
        line = '1959 2019'
        line, _char_only = copyrights_module.prep_line(line)
        assert not copyrights_module.is_candidate(line)

    def test_is_candidate_should_not_select_line_with_only_two_digit_numbers(self):
        line = 'template<class V> struct v_iter<V, mpl::int_<10> > { typedef typename V::item10 type; typedef v_iter<V, mpl::int_<10 + 1> > next; };'
        line, _char_only = copyrights_module.prep_line(line)
        assert not copyrights_module.is_candidate(line)

    def test_is_candidate_should_select_line_with_sign(self):
        line = 'template<class V> struct v_iter<V, mpl::int_<10> (c) { typedef typename V::item10 type; typedef v_iter<V, mpl::int_<10 + 1> > next; };'
        line, _char_only = copyrights_module.prep_line(line)
        assert copyrights_module.is_candidate(line)

    def test_is_candidate_should_not_select_line_with_junk_hex(self):
        line = '01061C3F5280CD4AC504152B81E452BD82015442014'
        line, _char_only = copyrights_module.prep_line(line)
        assert not copyrights_module.is_candidate(line)

    def test_is_candidate_should_not_select_line_with_trailing_years(self):
        line = '01061C3F5280CD4AC504152B81E452BD820154 2014\n'
        line, _char_only = copyrights_module.prep_line(line)
        assert not copyrights_module.is_candidate(line)

    def test_is_candidate_should_select_line_with_proper_years(self):
        line = '01061C3F5280CD4AC504152B81E452BD820154 2014-'
        line, _char_only = copyrights_module.prep_line(line)
        assert copyrights_module.is_candidate(line)

    def test_is_candidate_should_select_line_with_proper_years2(self):
        line = '01061C3F5280CD4,2016 152B81E452BD820154'
        line, _char_only = copyrights_module.prep_line(line)
        assert copyrights_module.is_candidate(line)

    def test_is_candidate_should_select_line_with_dashed_year(self):
        line = 'pub   1024D/CCD6F801 2006-11-15'
        line, _char_only = copyrights_module.prep_line(line)
        assert copyrights_module.is_candidate(line)

    def test_is_candidate_should_select_line_with_iso_date_year(self):
        line = 'sig 3 ccd6f801 2006-11-15 nathan mittler <nathan.mittler@gmail.com>'
        line, _char_only = copyrights_module.prep_line(line)
        assert copyrights_module.is_candidate(line)


class TestCopyrightDetector(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_detect(self):
        location = self.get_test_loc('copyrights_basic/essential_smoke-ibm_c.c')
        expected = [
            'Copyright IBM and others (c) 2008',
            'Copyright Eclipse, IBM and others (c) 2008'
        ]
        copyrights, _, _, _ = copyrights_module.detect(location)
        assert expected == copyrights

    def test_detect_with_lines(self):
        location = self.get_test_loc('copyrights_basic/essential_smoke-ibm_c.c')
        expected = [
            ([u'Copyright IBM and others (c) 2008'], [], [u'2008'], [u'IBM and others'], 6, 6),
            ([u'Copyright Eclipse, IBM and others (c) 2008'], [], [u'2008'], [u'Eclipse, IBM and others'], 8, 8)
            ]
        results = list(copyrights_module.detect_copyrights(location))
        assert expected == results


def check_detection_with_lines(expected, test_file, what='copyrights', with_line_num=True):
    """
    Run detection of copyright on the test_file, checking the results
    match the expected list of values.

    If expected_in_results and results_in_expected are True (the default),
    then expected and test results are tested for equality. To accommodate
    for some level of approximate testing, the check can test only if an
    expected result in a test result, or the opposite. If
    expected_in_results and results_in_expected are both False an
    exception is raised as this is not a case that make sense.
    """
    all_results = []
    for detection in copyrights_module.detect_copyrights(test_file):
        copyrights, authors, years, holders, start_line, end_line = detection
        what_is_detected = locals().get(what)
        if not what_is_detected:
            continue
        if with_line_num:
            results = (what_is_detected, start_line, end_line)
            all_results.append(results)
        else:
            results = what_is_detected
            all_results.extend(results)

    assert expected == all_results


class TestCopyrightLinesDetection(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_company_lines_name_in_java(self):
        test_file = self.get_test_loc('copyrights_basic/company_name_in_java-9_java.java')
        expected = [
            ([u'Copyright (c) 2008-2011 Company Name Incorporated'], 2, 3)
        ]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_03e16f6c_0(self):
        test_file = self.get_test_loc('copyrights_basic/03e16f6c_0-e_f_c.0')
        expected = [
            ([u'Copyright (c) 1997 Microsoft Corp., OU Microsoft Corporation, CN Microsoft Root',
              u'Copyright (c) 1997 Microsoft Corp., OU Microsoft Corporation, CN Microsoft Root'],
              30, 37),
            ([u'(c) 1997 Microsoft'], 60, 63)
        ]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_3a3b02ce_0(self):
        # this is a certificate and the actual copyright holder is not clear:
        # could be either Wisekey or OISTE Foundation.
        test_file = self.get_test_loc('copyrights_basic/3a3b02ce_0-a_b_ce.0')
        expected = [([
                u'Copyright (c) 2005, OU OISTE Foundation Endorsed, CN OISTE WISeKey Global Root',
                u'Copyright (c) 2005, OU OISTE Foundation Endorsed, CN OISTE WISeKey Global Root'
            ],
            30, 37
        )]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_boost_vector(self):
        test_file = self.get_test_loc('copyrights_basic/vector50.hpp')
        expected = [([u'Copyright (c) 2005 Arkadiy Vertleyb', u'Copyright (c) 2005 Peder Holt'], 2, 3)]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_ABC_cpp(self):
        test_file = self.get_test_loc('copyrights_basic/ABC_cpp-Case_cpp.cpp')
        expected = [([u'Copyright (c) ABC Company'], 12, 12)]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_ABC_file_cpp(self):
        test_file = self.get_test_loc('copyrights_basic/ABC_file_cpp-File_cpp.cpp')
        expected = [([u'Copyright (c) ABC Company'], 12, 12)]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_heunrich_c(self):
        test_file = self.get_test_loc('copyrights_basic/heunrich_c-c.c')
        expected = [([u'Copyright (c) 2000 HEUNRICH HERTZ INSTITUTE'], 5, 5)]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_isc(self):
        test_file = self.get_test_loc('copyrights_basic/isc-c.c')
        expected = [([u'Copyright (c) 1998-2000 The Internet Software Consortium.'], 1, 3)]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_sample_py(self):
        test_file = self.get_test_loc('copyrights_basic/sample_py-py.py')
        expected = [([u'COPYRIGHT 2006 ABC ABC'], 6, 7)]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_abc(self):
        test_file = self.get_test_loc('copyrights_basic/abc')
        expected = [([u'Copyright (c) 2006 abc.org'], 1, 2)]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_abc_loss_of_holder_c(self):
        test_file = self.get_test_loc('copyrights_basic/abc_loss_of_holder_c-c.c')
        expected = [([u'copyright abc 2001'], 1, 2)]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_abiword_common_copyright(self):
        test_file = self.get_test_loc('copyrights_basic/abiword_common.copyright')
        expected = [
            ([u'Copyright (c) 1998- AbiSource, Inc. & Co.'], 15, 17),
             ([u'Copyright (c) 2009 Masayuki Hatta',
               u'Copyright (c) 2009 Patrik Fimml <patrik@fimml.at>'],
              41, 42),
        ]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_acme_c(self):
        test_file = self.get_test_loc('copyrights_basic/acme_c-c.c')
        expected = [([u'Copyright (c) 2000 ACME, Inc.'], 1, 1)]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_activefieldattribute_cs(self):
        test_file = self.get_test_loc('copyrights_basic/activefieldattribute_cs-ActiveFieldAttribute_cs.cs')
        expected = [([u'Web Applications Copyright 2009 - Thomas Hansen thomas@ra-ajax.org.'], 2, 5)]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_addr_c(self):
        test_file = self.get_test_loc('copyrights_basic/addr_c-addr_c.c')
        expected = [
            ([u'Copyright 1999 Cornell University.'], 2, 4),
            ([u'Copyright 2000 Jon Doe.'], 5, 5)
        ]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_adler_inflate_c(self):
        test_file = self.get_test_loc('copyrights_basic/adler_inflate_c-inflate_c.c')
        expected = [([u'Not copyrighted 1992 by Mark Adler'], 1, 2)]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_aleal(self):
        test_file = self.get_test_loc('copyrights_basic/aleal-c.c')
        expected = [([u'copyright (c) 2006 by aleal'], 2, 2)]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_andre_darcy(self):
        test_file = self.get_test_loc('copyrights_basic/andre_darcy-c.c')
        expected = [
            ([u'Copyright (c) 1995, Pascal Andre (andre@via.ecp.fr).'], 2, 6),
            ([u"copyright 1997, 1998, 1999 by D'Arcy J.M. Cain (darcy@druid.net)"], 25, 26)
        ]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_android_c(self):
        test_file = self.get_test_loc('copyrights_basic/android_c-c.c')
        expected = [
            ([u'Copyright (c) 2009 The Android Open Source Project'], 2, 2),
            ([u'Copyright 2003-2005 Colin Percival'], 23, 24)
        ]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_apache_notice(self):
        test_file = self.get_test_loc('copyrights_basic/apache_notice-NOTICE')
        expected = [
            ([u'Copyright 1999-2006 The Apache Software Foundation'], 6, 7),
            ([u'Copyright 1999-2006 The Apache Software Foundation'], 16, 17),
            ([u'Copyright 2001-2003,2006 The Apache Software Foundation.'], 27, 28),
            ([u'copyright (c) 2000 World Wide Web Consortium, http://www.w3.org'], 33, 34)
        ]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_aptitude_copyright_label(self):
        test_file = self.get_test_loc('copyrights_basic/aptitude-aptitude.label')
        expected = [([u'Copyright 1999-2005 Daniel Burrows <dburrows@debian.org>'], 1, 1)]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_atheros_spanning_lines(self):
        test_file = self.get_test_loc('copyrights_basic/atheros_spanning_lines-py.py')
        expected = [
            ([u'Copyright (c) 2000 Atheros Communications, Inc.'], 2, 2),
            ([u'Copyright (c) 2001 Atheros Communications, Inc.'], 3, 3),
            ([u'Copyright (c) 1994-1997 by Intel Corporation.'], 8, 11)
        ]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_att_in_c(self):
        test_file = self.get_test_loc('copyrights_basic/att_in_c-9_c.c')
        expected = [([u'Copyright (c) 1991 by AT&T.'], 5, 5)]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_audio_c(self):
        test_file = self.get_test_loc('copyrights_basic/audio_c-c.c')
        expected = [([u'copyright (c) 1995, AudioCodes, DSP Group, France Telecom, Universite de Sherbrooke.'], 2, 4)]

        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_babkin_txt(self):
        test_file = self.get_test_loc('copyrights_basic/babkin_txt.txt')
        expected = [
            ([u'Copyright (c) North',
              u'Copyright (c) South',
              u'Copyright (c) 2001 by the TTF2PT1 project',
              u'Copyright (c) 2001 by Sergey Babkin'
             ], 1, 5)
        ]
        check_detection_with_lines(expected, test_file)

    def test_copyright_lines_blender_debian(self):
        test_file = self.get_test_loc('copyrights_basic/blender_debian-blender.copyright')
        expected = [
            ([u'Copyright (c) 2002-2008 Blender Foundation'], 8, 11),
            ([u'Copyright (c) 2004-2005 Masayuki Hatta <mhatta@debian.org>',
              u'(c) 2005-2007 Florian Ernst <florian@debian.org>',
              u'(c) 2007-2008 Cyril Brulebois <kibi@debian.org>'],
              30, 35)
        ]
        check_detection_with_lines(expected, test_file)
