# -*- coding: utf-8 -*-
###############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
###############################################################################
import ws
import unittest

class TestCollapse(unittest.TestCase):
    def test_collapse(self):
        result = ws.collapse("   ")
        self.assertEqual(result, "")

        result = ws.collapse("  foo")
        self.assertEqual(result, "foo")

        result = ws.collapse("foo   ")
        self.assertEqual(result, "foo")

        result = ws.collapse("  foo    bar  ")
        self.assertEqual(result, "foo bar")

        result = ws.collapse("foo\t\nbar\r")
        self.assertEqual(result, "foo bar")


if __name__ == '__main__':
    unittest.main()
