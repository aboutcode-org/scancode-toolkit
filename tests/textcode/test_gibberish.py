#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/aboutcode-org/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from commoncode.testcase import FileBasedTesting

from textcode import gibberish


class TestGibberish(FileBasedTesting):
    def test_gibberish_basic(self):
        # From https://github.com/rrenaud/Gibberish-Detector/blob/847d95ad706b535199b90b4d44e4e6e80564e379/README.rst#usage
        g = gibberish.Gibberish()
        self.assertFalse(g.detect_gibberish("my name is rob and i like to hack"))
        self.assertFalse(g.detect_gibberish("is this thing working?"))
        self.assertFalse(g.detect_gibberish("i hope so"))
        self.assertTrue(g.detect_gibberish("t2 chhsdfitoixcv"))
        self.assertTrue(g.detect_gibberish("ytjkacvzw"))
        self.assertTrue(g.detect_gibberish("yutthasxcvqer"))
        self.assertFalse(g.detect_gibberish("seems okay"))
        self.assertFalse(g.detect_gibberish("yay!"))
