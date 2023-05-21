# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

import cluecode_test_utils  # NOQA
from commoncode.testcase import FileBasedTesting
from cluecode import copyrights


class TestTextPreparation(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_strip_leading_numbers(self):
        a = '2.6.6 (r266:84297, Aug 24 2010, 18:46:32) [MSC v.1500 32 bit (Intel)] on win32'
        assert copyrights.strip_leading_numbers(a) == a

        a = '26 6 24 2010, 18:46:32) [MSC v.1500 32 bit (Intel)] on 12'
        expected = '2010, 18:46:32) [MSC v.1500 32 bit (Intel)] on 12'
        assert copyrights.strip_leading_numbers(a) == expected

    def test_prepare_text_line(self):
        cp = 'test (C) all rights reserved'
        result = copyrights.prepare_text_line(cp)
        assert result == 'test (c) all rights reserved'

    def test_prepare_text_line_debian(self):
        cp = 'Parts Copyright (c) 1992 <s>Uri Blumentha<s>l, I</s>BM</s>'
        result = copyrights.prepare_text_line(cp)
        assert result == 'Parts Copyright (c) 1992 Uri Blumenthal, IBM'

    def test_prepare_text_line_does_not_truncate_transliterable_unicode(self):
        cp = 'Muła'
        result = copyrights.prepare_text_line(cp)
        assert result == 'Mula'

    def test_strip_markup(self):
        cp = 'Parts Copyright (c) 1992 <s>Uri Blumentha<s>l, I</s>BM</s>'
        result = copyrights.strip_markup(cp)
        assert result == 'Parts Copyright (c) 1992 Uri Blumenthal, IBM'

    def test_prepare_text_line_removes_C_comments(self):
        cp = '/*  Copyright 1996-2005, 2008-2011 by   */'
        result = copyrights.prepare_text_line(cp)
        assert result == 'Copyright 1996-2005, 2008-2011 by'

    def test_prepare_text_line_removes_C_comments2(self):
        cp = '/*  David Turner, Robert Wilhelm, and Werner Lemberg. */'
        result = copyrights.prepare_text_line(cp)
        assert result == 'David Turner, Robert Wilhelm, and Werner Lemberg.'

    def test_prepare_text_line_removes_Cpp_comments(self):
        cp = '//  David Turner, Robert Wilhelm, and Werner Lemberg. */'
        result = copyrights.prepare_text_line(cp)
        assert result == 'David Turner, Robert Wilhelm, and Werner Lemberg.'

    def test_prepare_text_line_does_not_damage_urls(self):
        cp = 'copyright (c) 2000 World Wide Web Consortium, http://www.w3.org'
        result = copyrights.prepare_text_line(cp)
        assert result == 'copyright (c) 2000 World Wide Web Consortium, http://www.w3.org'

    def test_is_end_of_statement(self):
        line = '''          "All rights reserved\\n"'''
        _line, char_only_line = copyrights.prep_line(line)
        assert copyrights.is_end_of_statement(char_only_line)

    def test_candidate_lines_simple(self):
        lines = [(1, ' test (C) all rights reserved')]
        result = list(copyrights.candidate_lines(lines))
        expected = [[(1, ' test (C) all rights reserved')]]
        assert result == expected

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
            [(3, '           Copyright 1999-2006 The Apache Software Foundation')],

            [(7, '           This product includes software developed at'),
             (8, '           The Apache Software Foundation (http://www.apache.org/).')],

            [(13, '             - software copyright (c) 1999-2002, Lotus Development Corporation.,'),
             (14, '               http://www.lotus.com.'),
             (15, '             - software copyright (c) 2001-2002, Sun Microsystems.,'),
             (16, '               http://www.sun.com.'),
             (17, '             - software copyright (c) 2003, IBM Corporation.,'),
             (18, '               http://www.ibm.com.')],

            [(22, '           this product includes software developed by the following:')]
        ]

        result = list(copyrights.candidate_lines(enumerate(lines, 1)))
        assert result == expected

    def test_is_candidates_should_not_select_line_with_bare_full_year(self):
        line = '2012'
        line, _char_only = copyrights.prep_line(line)
        assert not copyrights.is_candidate(line)

    def test_is_candidates_should_not_select_line_with_full_year_before_160_and_after_2018(self):
        line = '1959 2019'
        line, _char_only = copyrights.prep_line(line)
        assert not copyrights.is_candidate(line)

    def test_is_candidate_should_not_select_line_with_only_two_digit_numbers(self):
        line = 'template<class V> struct v_iter<V, mpl::int_<10> > { typedef typename V::item10 type; typedef v_iter<V, mpl::int_<10 + 1> > next; };'
        line, _char_only = copyrights.prep_line(line)
        assert not copyrights.is_candidate(line)

    def test_is_candidate_should_select_line_with_sign(self):
        line = 'template<class V> struct v_iter<V, mpl::int_<10> (c) { typedef typename V::item10 type; typedef v_iter<V, mpl::int_<10 + 1> > next; };'
        line, _char_only = copyrights.prep_line(line)
        assert copyrights.is_candidate(line)

    def test_is_candidate_should_not_select_line_with_junk_hex(self):
        line = '01061C3F5280CD4AC504152B81E452BD82015442014'
        line, _char_only = copyrights.prep_line(line)
        assert not copyrights.is_candidate(line)

    def test_is_candidate_should_select_line_with_a_trailing_years(self):
        line = '01061C3F5280CD4AC504152B81E452BD820154 2014\n'
        line, _char_only = copyrights.prep_line(line)
        assert copyrights.is_candidate(line)

    def test_is_candidate_should_select_line_with_proper_years(self):
        line = '01061C3F5280CD4AC504152B81E452BD820154 2014-'
        line, _char_only = copyrights.prep_line(line)
        assert copyrights.is_candidate(line)

    def test_is_candidate_should_select_line_with_proper_years2(self):
        line = '01061C3F5280CD4,2016 152B81E452BD820154'
        line, _char_only = copyrights.prep_line(line)
        assert copyrights.is_candidate(line)

    def test_is_candidate_should_select_line_with_dashed_year(self):
        line = 'pub   1024D/CCD6F801 2006-11-15'
        line, _char_only = copyrights.prep_line(line)
        assert copyrights.is_candidate(line)

    def test_is_candidate_should_select_line_with_iso_date_year(self):
        line = 'sig 3 ccd6f801 2006-11-15 nathan mittler <nathan.mittler@gmail.com>'
        line, _char_only = copyrights.prep_line(line)
        assert copyrights.is_candidate(line)

    def test_is_candidate_should_not_select_lines_made_only_of_punct_and_digits(self):
        lines = '''
              25  17   1   -80.00000      .25000    37.00000      .25000
            0: 5107 -2502 -700 496 -656 468 -587 418 -481 347 -325 256 -111 152 166 50
            493 -37 854 -96 1221 -118 1568 -125 1953 -143 2433 -195 2464 -281 2529 -395
            1987 -729 447 -916 -3011 -1181 -5559 -406 -6094 541 -5714 1110 -5247 1289
            -4993 1254 -4960 1151
            1: 4757 -1695 -644 429 -627 411 -602 368 -555 299 -470 206 -328 96 -125 -15
            126 -105 391 -146 634 -120 762 -58 911 -13 1583 -8 1049 -28 1451 123 1377 -464
            907 -603 -4056 -1955 -6769 -485 -5797 929 -4254 1413 -3251 1295 -2871 993
            -2899 724
            2: 4413 -932 -563 355 -566 354 -582 322 -597 258 -579 164 -499 45 -341 -84
            -127 -192 93 -234 288 -157 190 -25 -145 65 1065 74 -1087 -40 -877 1058 -994 18
            1208 694 -5540 -3840 -7658 -332 -4130 1732 -1668 1786 -634 1127 -525 501
            -856 110
            '''.splitlines()

        for line in lines:
            line, _ = copyrights.prep_line(line)
            assert not copyrights.is_candidate(line)


class TestCopyrightDetector(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_detect(self):
        location = self.get_test_loc('copyrights_basic/essential_smoke-ibm_c.c')
        expected = [
            copyrights.CopyrightDetection('Copyright IBM and others (c) 2008', 6, 6),
            copyrights.CopyrightDetection('Copyright Eclipse, IBM and others', 8, 8),
            copyrights.CopyrightDetection('(c) 2008', 8, 8),
        ]
        results = list(copyrights.detect_copyrights(
            location,
            include_holders=False,
            include_authors=False,
        ))
        assert results == expected

    def test_detect_with_lines(self):
        location = self.get_test_loc('copyrights_basic/essential_smoke-ibm_c.c')
        expected = [
            copyrights.CopyrightDetection('Copyright IBM and others (c) 2008', 6, 6),
            copyrights.HolderDetection('IBM and others', 6, 6),
            copyrights.CopyrightDetection('Copyright Eclipse, IBM and others', 8, 8),
            copyrights.HolderDetection('Eclipse, IBM and others', 8, 8),
            copyrights.CopyrightDetection('(c) 2008', 8, 8)
        ]
        results = list(copyrights.detect_copyrights(location))
        assert results == expected

    def test_detect_with_lines_only_holders(self):
        location = self.get_test_loc('copyrights_basic/essential_smoke-ibm_c.c')
        expected = [
            copyrights.HolderDetection('IBM and others', 6, 6),
            copyrights.HolderDetection('Eclipse, IBM and others', 8, 8)
        ]
        results = list(copyrights.detect_copyrights(
            location,
            include_copyrights=False,
            include_holders=True,
            include_authors=False,
        ))
        assert results == expected


def check_full_detections(expected, test_file):
    """
    Run detection of copyright on the test_file, checking the results
    match the expected list of values.
    """
    results = list(copyrights.detect_copyrights(
        test_file,
        include_copyrights=True,
        include_authors=False,
        include_holders=False
    ))
    assert results == expected


class TestCopyrightLinesDetection(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_company_lines_name_in_java(self):
        test_file = self.get_test_loc('copyrights_basic/company_name_in_java-9_java.java')
        expected = [
            copyrights.CopyrightDetection('Copyright (c) 2008-2011 Company Name Incorporated', 2, 2)
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_03e16f6c_0(self):
        test_file = self.get_test_loc('copyrights_basic/03e16f6c_0-e_f_c.0')
        expected = [
            copyrights.CopyrightDetection('Copyright (c) 1997 Microsoft Corp.', 31, 31),
            copyrights.CopyrightDetection('Copyright (c) 1997 Microsoft Corp.', 35, 35),
            copyrights.CopyrightDetection('Copyright (c) 1997 Microsoft', 61, 61)
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_3a3b02ce_0(self):
        # this is a certificate and the actual copyright holder is not clear:
        # could be either Wisekey or OISTE Foundation.
        test_file = self.get_test_loc('copyrights_basic/3a3b02ce_0-a_b_ce.0')
        expected = [
            copyrights.CopyrightDetection('Copyright (c) 2005, OU OISTE Foundation', 31, 31),
            copyrights.CopyrightDetection('Copyright (c) 2005, OU OISTE Foundation', 35, 35),
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_boost_vector(self):
        test_file = self.get_test_loc('copyrights_basic/vector50.hpp')
        expected = [
            copyrights.CopyrightDetection('Copyright (c) 2005 Arkadiy Vertleyb', 2, 2),
            copyrights.CopyrightDetection('Copyright (c) 2005 Peder Holt', 3, 3),
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_ABC_cpp(self):
        test_file = self.get_test_loc('copyrights_basic/ABC_cpp-Case_cpp.cpp')
        expected = [
            copyrights.CopyrightDetection('Copyright (c) ABC Company', 12, 12),
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_ABC_file_cpp(self):
        test_file = self.get_test_loc('copyrights_basic/ABC_file_cpp-File_cpp.cpp')
        expected = [
            copyrights.CopyrightDetection('Copyright (c) ABC Company', 12, 12)
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_heunrich_c(self):
        test_file = self.get_test_loc('copyrights_basic/heunrich_c-c.c')
        expected = [
            copyrights.CopyrightDetection('Copyright (c) 2000 HEUNRICH HERTZ INSTITUTE', 5, 5)
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_isc(self):
        test_file = self.get_test_loc('copyrights_basic/isc-c.c')
        expected = [
            copyrights.CopyrightDetection('Copyright (c) 1998-2000 The Internet Software Consortium', 3, 3)
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_sample_py(self):
        test_file = self.get_test_loc('copyrights_basic/sample_py-py.py')
        expected = [
            copyrights.CopyrightDetection('COPYRIGHT 2006 ABC', 6, 6)
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_abc(self):
        test_file = self.get_test_loc('copyrights_basic/abc')
        expected = [
            copyrights.CopyrightDetection('Copyright (c) 2006 abc.org', 2, 2)
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_abc_loss_of_holder_c(self):
        test_file = self.get_test_loc('copyrights_basic/abc_loss_of_holder_c-c.c')
        expected = [
            copyrights.CopyrightDetection('copyright abc 2001', 1, 1)
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_abiword_common_copyright(self):
        test_file = self.get_test_loc('copyrights_basic/abiword_common.copyright')
        expected = [
            copyrights.CopyrightDetection('Copyright (c) 1998- AbiSource, Inc. & Co.', 15, 17),
            copyrights.CopyrightDetection('Copyright (c) 2009 Masayuki Hatta (mhatta) <mhatta@debian.org>', 41, 41),
            copyrights.CopyrightDetection('Copyright (c) 2009 Patrik Fimml <patrik@fimml.at>', 42, 42),
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_acme_c(self):
        test_file = self.get_test_loc('copyrights_basic/acme_c-c.c')
        expected = [
            copyrights.CopyrightDetection('Copyright (c) 2000 ACME, Inc.', 1, 1)
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_activefieldattribute_cs(self):
        test_file = self.get_test_loc('copyrights_basic/activefieldattribute_cs-ActiveFieldAttribute_cs.cs')
        expected = [
            copyrights.CopyrightDetection('Copyright 2009 - Thomas Hansen thomas@ra-ajax.org', 3, 4)
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_addr_c(self):
        test_file = self.get_test_loc('copyrights_basic/addr_c-addr_c.c')
        expected = [
            copyrights.CopyrightDetection('Copyright 1999 Cornell University', 4, 4),
            copyrights.CopyrightDetection('Copyright 2000 Jon Doe', 5, 5)
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_adler_inflate_c(self):
        test_file = self.get_test_loc('copyrights_basic/adler_inflate_c-inflate_c.c')
        expected = [
            copyrights.CopyrightDetection('Not copyrighted 1992 by Mark Adler', 1, 1)
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_aleal(self):
        test_file = self.get_test_loc('copyrights_basic/aleal-c.c')
        expected = [
            copyrights.CopyrightDetection('copyright (c) 2006 by aleal', 2, 2)
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_andre_darcy(self):
        test_file = self.get_test_loc('copyrights_basic/andre_darcy-c.c')
        expected = [
            copyrights.CopyrightDetection('Copyright (c) 1995, Pascal Andre (andre@via.ecp.fr)', 5, 6),
            copyrights.CopyrightDetection(u"copyright 1997, 1998, 1999 by D'Arcy J.M. Cain (darcy@druid.net)", 25, 26)
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_android_c(self):
        test_file = self.get_test_loc('copyrights_basic/android_c-c.c')
        expected = [
            copyrights.CopyrightDetection('Copyright (c) 2009 The Android Open Source Project', 2, 2),
            copyrights.CopyrightDetection('Copyright 2003-2005 Colin Percival', 23, 23)
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_apache_notice(self):
        test_file = self.get_test_loc('copyrights_basic/apache_notice-NOTICE')
        expected = [
            copyrights.CopyrightDetection('Copyright 1999-2006 The Apache Software Foundation', 7, 7),
            copyrights.CopyrightDetection('Copyright 1999-2006 The Apache Software Foundation', 17, 17),
            copyrights.CopyrightDetection('Copyright 2001-2003,2006 The Apache Software Foundation', 28, 28),
            copyrights.CopyrightDetection('copyright (c) 2000 World Wide Web Consortium, http://www.w3.org', 34, 34)
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_aptitude_copyright_label(self):
        test_file = self.get_test_loc('copyrights_basic/aptitude-aptitude.label')
        expected = [
            copyrights.CopyrightDetection('Copyright 1999-2005 Daniel Burrows <dburrows@debian.org>', 1, 1)
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_atheros_spanning_lines(self):
        test_file = self.get_test_loc('copyrights_basic/atheros_spanning_lines-py.py')
        expected = [
            copyrights.CopyrightDetection('Copyright (c) 2000 Atheros Communications, Inc.', 2, 2),
            copyrights.CopyrightDetection('Copyright (c) 2001 Atheros Communications, Inc.', 3, 3),
            copyrights.CopyrightDetection('Copyright (c) 1994-1997 by Intel Corporation', 10, 11)
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_att_in_c(self):
        test_file = self.get_test_loc('copyrights_basic/att_in_c-9_c.c')
        expected = [
            copyrights.CopyrightDetection('Copyright (c) 1991 by AT&T.', 5, 5),
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_audio_c(self):
        test_file = self.get_test_loc('copyrights_basic/audio_c-c.c')
        expected = [
            copyrights.CopyrightDetection('copyright (c) 1995, AudioCodes, DSP Group, France Telecom, Universite de Sherbrooke', 3, 4)
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_babkin_txt(self):
        test_file = self.get_test_loc('copyrights_basic/babkin_txt.txt')
        expected = [
            copyrights.CopyrightDetection('Copyright (c) North', 1, 1),
            copyrights.CopyrightDetection('Copyright (c) South', 2, 3),
            copyrights.CopyrightDetection('Copyright (c) 2001 by the TTF2PT1 project', 4, 4),
            copyrights.CopyrightDetection('Copyright (c) 2001 by Sergey Babkin', 5, 5),
        ]
        check_full_detections(expected, test_file)

    def test_copyright_lines_blender_debian(self):
        test_file = self.get_test_loc('copyrights_basic/blender_debian-blender.copyright')
        expected = [
            copyrights.CopyrightDetection('Copyright (c) 2002-2008 Blender Foundation', 9, 9),
            copyrights.CopyrightDetection('Copyright (c) 2004-2005 Masayuki Hatta <mhatta@debian.org>', 31, 31),
            copyrights.CopyrightDetection('(c) 2005-2007 Florian Ernst <florian@debian.org>', 32, 32),
            copyrights.CopyrightDetection('(c) 2007-2008 Cyril Brulebois <kibi@debian.org>', 33, 33),
        ]
        check_full_detections(expected, test_file)
