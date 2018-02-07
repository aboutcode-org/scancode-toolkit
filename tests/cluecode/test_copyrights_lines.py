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

import os.path

from commoncode.testcase import FileBasedTesting
import cluecode.copyrights


class TestCopyrightDetector(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_copyright_detect2_basic(self):
        location = self.get_test_loc('copyright_lines/essential_smoke-ibm_c.c')
        expected = [
            ([u'Copyright IBM and others (c) 2008'], [], [u'2008'], [u'IBM and others'], 6, 6),
            ([u'Copyright Eclipse, IBM and others (c) 2008'], [], [u'2008'], [u'Eclipse, IBM and others'], 8, 8)
            ]
        results = list(cluecode.copyrights.detect_copyrights(location))
        assert expected == results


def check_detection(expected, test_file,
                    what='copyrights', with_line_num=True):
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
    for detection in cluecode.copyrights.detect_copyrights(test_file):
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

    def test_company_name_in_java(self):
        test_file = self.get_test_loc('copyright_lines/company_name_in_java-9_java.java')
        expected = [
            ([u'Copyright (c) 2008-2011 Company Name Incorporated'], 2, 3)
        ]
        check_detection(expected, test_file)

    def test_copyright_03e16f6c_0(self):
        test_file = self.get_test_loc('copyright_lines/03e16f6c_0-e_f_c.0')
        expected = [
            ([u'Copyright (c) 1997 Microsoft Corp., OU Microsoft Corporation, CN Microsoft Root',
              u'Copyright (c) 1997 Microsoft Corp., OU Microsoft Corporation, CN Microsoft Root'],
              30, 37),
            ([u'(c) 1997 Microsoft'], 60, 63)
        ]
        check_detection(expected, test_file)

    def test_copyright_3a3b02ce_0(self):
        # this is a certificate and the actual copyright holder is not clear:
        # could be either Wisekey or OISTE Foundation.
        test_file = self.get_test_loc('copyright_lines/3a3b02ce_0-a_b_ce.0')
        expected = [([
                u'Copyright (c) 2005, OU OISTE Foundation Endorsed, CN OISTE WISeKey Global Root',
                u'Copyright (c) 2005, OU OISTE Foundation Endorsed, CN OISTE WISeKey Global Root'
            ],
            30, 37
        )]
        check_detection(expected, test_file)

    def test_copyright_boost_vector(self):
        test_file = self.get_test_loc('copyright_lines/vector50.hpp')
        expected = [([u'Copyright (c) 2005 Arkadiy Vertleyb', u'Copyright (c) 2005 Peder Holt'], 2, 3)]
        check_detection(expected, test_file)

    def test_copyright_ABC_cpp(self):
        test_file = self.get_test_loc('copyright_lines/ABC_cpp-Case_cpp.cpp')
        expected = [([u'Copyright (c) ABC Company'], 12, 12)]
        check_detection(expected, test_file)

    def test_copyright_ABC_file_cpp(self):
        test_file = self.get_test_loc('copyright_lines/ABC_file_cpp-File_cpp.cpp')
        expected = [([u'Copyright (c) ABC Company'], 12, 12)]
        check_detection(expected, test_file)

    def test_copyright_heunrich_c(self):
        test_file = self.get_test_loc('copyright_lines/heunrich_c-c.c')
        expected = [([u'Copyright (c) 2000 HEUNRICH HERTZ INSTITUTE'], 5, 5)]
        check_detection(expected, test_file)

    def test_copyright_isc(self):
        test_file = self.get_test_loc('copyright_lines/isc-c.c')
        expected = [([u'Copyright (c) 1998-2000 The Internet Software Consortium.'], 1, 3)]
        check_detection(expected, test_file)

    def test_copyright_sample_py(self):
        test_file = self.get_test_loc('copyright_lines/sample_py-py.py')
        expected = [([u'COPYRIGHT 2006 ABC ABC'], 6, 7)]
        check_detection(expected, test_file)

    def test_copyright_abc(self):
        test_file = self.get_test_loc('copyright_lines/abc')
        expected = [([u'Copyright (c) 2006 abc.org'], 1, 2)]
        check_detection(expected, test_file)

    def test_copyright_abc_loss_of_holder_c(self):
        test_file = self.get_test_loc('copyright_lines/abc_loss_of_holder_c-c.c')
        expected = [([u'copyright abc 2001'], 1, 2)]
        check_detection(expected, test_file)

    def test_copyright_abiword_common_copyright(self):
        test_file = self.get_test_loc('copyright_lines/abiword_common.copyright')
        expected = [
            ([u'Copyright (c) 1998- AbiSource, Inc. & Co.'], 17, 17),
             ([u'Copyright (c) 2009 Masayuki Hatta',
               u'Copyright (c) 2009 Patrik Fimml <patrik@fimml.at>'],
              41, 42),
        ]
        check_detection(expected, test_file)

    def test_copyright_acme_c(self):
        test_file = self.get_test_loc('copyright_lines/acme_c-c.c')
        expected = [([u'Copyright (c) 2000 ACME, Inc.'], 1, 1)]
        check_detection(expected, test_file)

    def test_copyright_activefieldattribute_cs(self):
        test_file = self.get_test_loc('copyright_lines/activefieldattribute_cs-ActiveFieldAttribute_cs.cs')
        expected = [([u'Web Applications Copyright 2009 - Thomas Hansen thomas@ra-ajax.org.'], 2, 5)]
        check_detection(expected, test_file)

    def test_copyright_addr_c(self):
        test_file = self.get_test_loc('copyright_lines/addr_c-addr_c.c')
        expected = [
            ([u'Copyright 1999 Cornell University.'], 2, 4),
            ([u'Copyright 2000 Jon Doe.'], 5, 5)
        ]
        check_detection(expected, test_file)

    def test_copyright_adler_inflate_c(self):
        test_file = self.get_test_loc('copyright_lines/adler_inflate_c-inflate_c.c')
        expected = [([u'Not copyrighted 1992 by Mark Adler'], 1, 2)]
        check_detection(expected, test_file)

    def test_copyright_aleal(self):
        test_file = self.get_test_loc('copyright_lines/aleal-c.c')
        expected = [([u'copyright (c) 2006 by aleal'], 2, 2)]
        check_detection(expected, test_file)

    def test_copyright_andre_darcy(self):
        test_file = self.get_test_loc('copyright_lines/andre_darcy-c.c')
        expected = [
            ([u'Copyright (c) 1995, Pascal Andre (andre@via.ecp.fr).'], 2, 6),
            ([u"copyright 1997, 1998, 1999 by D'Arcy J.M. Cain (darcy@druid.net)"], 25, 26)
        ]
        check_detection(expected, test_file)

    def test_copyright_android_c(self):
        test_file = self.get_test_loc('copyright_lines/android_c-c.c')
        expected = [
            ([u'Copyright (c) 2009 The Android Open Source Project'], 2, 2),
            ([u'Copyright 2003-2005 Colin Percival'], 23, 24)
        ]
        check_detection(expected, test_file)

    def test_copyright_apache_notice(self):
        test_file = self.get_test_loc('copyright_lines/apache_notice-NOTICE')
        expected = [
            ([u'Copyright 1999-2006 The Apache Software Foundation'], 6, 7),
            ([u'Copyright 1999-2006 The Apache Software Foundation'], 16, 17),
            ([u'Copyright 2001-2003,2006 The Apache Software Foundation.'], 27, 28),
            ([u'copyright (c) 2000 World Wide Web Consortium, http://www.w3.org'], 33, 34)
        ]
        check_detection(expected, test_file)

    def test_copyright_aptitude_copyright_label(self):
        test_file = self.get_test_loc('copyright_lines/aptitude-aptitude.label')
        expected = [([u'Copyright 1999-2005 Daniel Burrows <dburrows@debian.org>'], 1, 1)]
        check_detection(expected, test_file)

    def test_copyright_atheros_spanning_lines(self):
        test_file = self.get_test_loc('copyright_lines/atheros_spanning_lines-py.py')
        expected = [
            ([u'Copyright (c) 2000 Atheros Communications, Inc.'], 2, 2),
            ([u'Copyright (c) 2001 Atheros Communications, Inc.'], 3, 3),
            ([u'Copyright (c) 1994-1997 by Intel Corporation.'], 8, 11)
        ]
        check_detection(expected, test_file)

    def test_copyright_att_in_c(self):
        test_file = self.get_test_loc('copyright_lines/att_in_c-9_c.c')
        expected = [([u'Copyright (c) 1991 by AT&T.'], 5, 5)]
        check_detection(expected, test_file)

    def test_copyright_audio_c(self):
        test_file = self.get_test_loc('copyright_lines/audio_c-c.c')
        expected = [([u'copyright (c) 1995, AudioCodes, DSP Group, France Telecom, Universite de Sherbrooke.'], 2, 4)]

        check_detection(expected, test_file)

    def test_copyright_babkin_txt(self):
        test_file = self.get_test_loc('copyright_lines/babkin_txt.txt')
        expected = [
            ([u'Copyright (c) North',
              u'Copyright (c) South',
              u'Copyright (c) 2001 by the TTF2PT1 project',
              u'Copyright (c) 2001 by Sergey Babkin'
             ], 1, 5)
        ]
        check_detection(expected, test_file)

    def test_copyright_blender_debian(self):
        test_file = self.get_test_loc('copyright_lines/blender_debian-blender.copyright')
        expected = [
            ([u'Copyright (c) 2002-2008 Blender Foundation'], 8, 11),
            ([u'Copyright (c) 2004-2005 Masayuki Hatta <mhatta@debian.org>',
              u'(c) 2005-2007 Florian Ernst <florian@debian.org>',
              u'(c) 2007-2008 Cyril Brulebois <kibi@debian.org>'],
              30, 35)
        ]
        check_detection(expected, test_file)

