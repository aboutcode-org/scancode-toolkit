# -*- coding: utf-8 -*-

#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import json
import os.path

from commoncode.fileutils import resource_iter
from commoncode.testcase import FileBasedTesting

from scancode_config import REGEN_TEST_FIXTURES
from textcode.analysis import as_unicode
from textcode.analysis import numbered_text_lines
from textcode.analysis import unicode_text_lines


def check_text_lines(result, expected_file, regen=REGEN_TEST_FIXTURES):
        if regen:
            with open(expected_file, 'w') as tf:
                json.dump(result, tf, indent=2)
        with open(expected_file, 'rb') as tf:
            expected = json.load(tf)
        assert result == expected


class TestAnalysis(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_numbered_text_lines_from_list_or_location_yield_same_results(self):
        test_file = self.get_test_loc('analysis/bsd-new')
        with io.open(test_file, encoding='utf-8') as inf:
            test_strings_list = inf.read().splitlines(True)

        # test when we are passing a location or a list
        from_loc = list(numbered_text_lines(location=test_file))
        from_list = list(numbered_text_lines(location=test_strings_list))
        assert from_loc != from_list
        assert len(from_loc) > len(from_list)
        assert ''.join(l for _, l in from_loc) == ''.join(l for _, l in from_list)

    def test_unicode_text_lines_handles_weird_xml_encodings(self):
        test_file = self.get_test_loc('analysis/weird_encoding/easyconf-0.9.0.pom')
        result = list(unicode_text_lines(test_file))
        expected_file = self.get_test_loc('analysis/weird_encoding/easyconf-0.9.0.pom.expected')
        check_text_lines(result, expected_file)

    def test_archives_do_not_yield_numbered_text_lines(self):
        test_file = self.get_test_loc('archive/simple.jar')
        result = list(numbered_text_lines(test_file))
        assert result == []

    def test_mpg_media_do_not_yield_numbered_text_lines(self):
        test_dir = self.get_test_loc('media_with_text')
        for test_file in resource_iter(test_dir, with_dirs=False):
            result = list(numbered_text_lines(test_file))
            assert not result

    def test_image_media_do_not_yield_numbered_text_lines(self):
        test_dir = self.get_test_loc('media_without_text')
        for test_file in resource_iter(test_dir, with_dirs=False):
            result = list(numbered_text_lines(test_file))
            assert result == [], 'Should not return text lines:' + test_file

    def test_numbered_text_lines_handles_sfdb(self):
        test_file = self.get_test_loc('analysis/splinefonts/Ambrosia.sfd')
        result = list(l for _, l in numbered_text_lines(test_file))
        expected_file = test_file + '.expected'
        expected = open(expected_file, 'r').read().splitlines(True)
        assert list(result) == expected

    def test_numbered_text_lines_handles_jsmap1(self):
        test_file = self.get_test_loc('analysis/jsmap/angular-sanitize.min.js.map')
        result = list(l for _, l in numbered_text_lines(test_file))
        expected_file = test_file + '.expected'
        check_text_lines(result, expected_file)

    def test_numbered_text_lines_handles_jsmap2(self):
        test_file = self.get_test_loc('analysis/jsmap/types.js.map')
        result = list(l for _, l in numbered_text_lines(test_file))
        expected_file = test_file + '.expected'
        check_text_lines(result, expected_file)

    def test_numbered_text_lines_handles_jsmap3(self):
        test_file = self.get_test_loc('analysis/jsmap/ar-ER.js.map')
        result = list(l for _, l in numbered_text_lines(test_file))
        expected_file = test_file + '.expected'
        check_text_lines(result, expected_file)

    def test_numbered_text_lines_handles_jsmap4(self):
        test_file = self.get_test_loc('analysis/jsmap/button.js.map')
        result = list(l for _, l in numbered_text_lines(test_file))
        expected_file = test_file + '.expected'
        check_text_lines(result, expected_file)

    def test_numbered_text_lines_handles_broken_jsmap_as_plain_text(self):
        test_file = self.get_test_loc('analysis/jsmap/broken.js.map')
        result = list(l for _, l in numbered_text_lines(test_file))
        expected_file = test_file + '.expected'
        check_text_lines(result, expected_file, regen=REGEN_TEST_FIXTURES)

    def test_numbered_text_lines_strips_verbatim_cr_lf_from_jsmap(self):
        test_file = self.get_test_loc('analysis/jsmap/crlf.js.map')
        result = list(numbered_text_lines(test_file))
        result = [l for _, l in result]
        expected_file = test_file + '.expected'
        check_text_lines(result, expected_file, regen=REGEN_TEST_FIXTURES)

    def test_numbered_text_lines_return_correct_number_of_lines(self):
        test_file = self.get_test_loc('analysis/correct_lines')
        result = list(numbered_text_lines(test_file))
        expected = [
            (1,
            'Permission is hereby granted, free of charge, to any person obtaining '
            'a copy of this software and associated documentation files (the "Software"), '
            'to deal in the Software without restriction, including without limitation '
            'the rights to use, copy, modify, merge, , , sublicense, and/or  Software, ,'),
            (1, u' subject')
        ]
        assert result == expected
        assert len(result) == 2

    def test_as_unicode_converts_bytes_to_unicode(self):
        test_line = '    // as defined in https://tools.ietf.org/html/rfc2821#section-4.1.2.'.encode()
        result = as_unicode(test_line)
        assert type(result) == str

    def test_numbered_text_lines_return_unicode(self):
        test_file = self.get_test_loc('analysis/verify.go')
        for _lineno, line in numbered_text_lines(test_file):
            assert type(line) == str

    def test_unicode_text_lines_replaces_null_bytes_with_space(self):
        test_file = self.get_test_loc('analysis/text-with-trailing-null-bytes.txt')
        result = list(unicode_text_lines(test_file))
        expected_file = self.get_test_loc('analysis/text-with-trailing-null-bytes.txt.expected')
        check_text_lines(result, expected_file, regen=REGEN_TEST_FIXTURES)

    def test_as_unicode_from_bytes_replaces_null_bytes_with_space(self):
        test = b'\x00is designed to give them, \x00BEFORE the\x00\x00\x00\x00\x00\x00'
        result = as_unicode(test)
        expected = ' is designed to give them,  BEFORE the      '
        assert result == expected

    def test_as_unicode_from_unicode_replaces_null_bytes_with_space(self):
        test = '\x00is designed to give them, \x00BEFORE the\x00\x00\x00\x00\x00\x00'
        result = as_unicode(test)
        expected = ' is designed to give them,  BEFORE the      '
        assert result == expected

    def test_numbered_text_lines_returns_same_text_from_file_and_from_strings(self):
        test_file = self.get_test_loc('analysis/gpl-2.0-freertos.RULE')
        from_file = list(numbered_text_lines(location=test_file))
        with io.open(test_file, encoding='utf-8') as tf:
            text = tf.read()
        from_string = list(numbered_text_lines(location=text.splitlines(True)))
        assert from_string == from_file

