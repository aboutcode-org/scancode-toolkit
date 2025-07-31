#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from unittest.case import TestCase

from licensedcode import seq

"""
This is testing the sequence matching internals using sequences of integers. The
texts are there for reference and sanity and are not use directly in the tests.
"""


class TestSeq(TestCase):

    def test_find_longest_match_seq(self):

        # true len = 409
        a = [
        33, 747, 1551, 119, 33, 1205, 2175, 2837, 119, 84, 3, 21, 54, 5801,
        4, 5789, 5, 11, 13, 9, 69, 18, 2, 42, 5867, 12, 5824, 5802, 46, 14, 0,
        74, 33, 53, 4, 5, 84, 53, 265, 7, 39, 94, 5813, 4, 5856, 7, 38, 4, 140,
        296, 12, 120, 46, 14, 474, 5974, 12, 338, 3, 0, 167, 4, 0, 2837, 349,
        13, 970, 15, 2953, 5, 33, 53, 6040, 0, 11, 12, 46, 17, 12, 4, 0, 167,
        5938, 39, 5797, 18, 6090, 3, 5, 11, 44, 39, 67, 5797, 1, 5810, 4, 5808,
        7, 52, 133, 50, 0, 167, 19, 5820, 13, 9, 128, 186, 168, 2, 5822, 5796,
        2, 9, 5796, 5953, 292, 40, 5833, 1, 21, 92, 2, 5862, 105, 7, 56, 213, 1,
        5827, 5852, 2, 28, 6325, 213, 5819, 136, 1, 2, 7, 5876, 18, 0, 21, 2,
        5872, 1, 5, 11, 5, 20, 12, 173, 40, 71, 822, 37, 1, 6352, 8427, 2177,
        6250, 58, 6380, 10, 1006, 12155, 7799, 492, 18, 1317, 1161, 7809, 12155,
        0, 964, 486, 1, 58, 12, 10, 5944, 6503, 0, 209, 1835, 12, 100, 17, 10,
        1006, 12155, 479, 7, 3186, 3907, 49, 2573, 175, 376, 0, 1006, 12155, 99,
        147, 110, 751, 3, 116, 0, 132, 181, 0, 340, 14, 278, 30, 6516, 3, 2251,
        0, 209, 1916, 2857, 3864, 113, 5, 97, 567, 19, 100, 13, 1873, 64, 55,
        1448, 997, 1916, 1875, 7809, 12, 10, 6125, 5869, 1, 1317, 2294, 5, 20,
        7390, 0, 2184, 1215, 2564, 1835, 0, 1835, 12, 474, 3, 5, 20, 337, 115,
        15, 2838, 11441, 7, 1742, 52, 33, 12, 7182, 5, 20, 12, 7, 0, 41, 430,
        76, 18, 30, 415, 8, 383, 402, 20, 12, 93, 40, 1317, 92, 831, 154, 5, 20,
        99, 147, 6952, 229, 14, 4, 12, 402, 117, 14, 8, 954, 567, 458, 3, 116,
        436, 1093, 1, 9940, 18, 380, 54, 3, 1350, 0, 1215, 2564, 1, 10, 1, 1991,
        9516, 56, 592, 1112, 30, 3, 1409, 17, 723, 34, 301, 1, 1991, 4, 159,
        1409, 58, 55, 3805, 10, 478, 790, 2121, 18, 0, 2564,

            0, 2567, 2298, 6, 6670, 2103, 10248, 2179, 4107, 910,
            5, 72, 17, 412, 17, 8, 5878, 5, 53, 8,
            97, 76, 6165, 8, 438, 18, 5, 7770, 26, 162,
            555, 230, 936, 4, 8, 1537, 5, 7770, 12, 3479,
            30, 8, 97, 8176, 947, 10, 2567, 7, 755, 3670,
            3723, 3716
        ]

        a_357 = [
            0, 2567, 2298, 6, 6670, 2103, 10248, 2179, 4107, 910,
            5, 72, 17, 412, 17, 8, 5878, 5, 53, 8,
            97, 76, 6165, 8, 438, 18, 5, 7770, 26, 162,
            555, 230, 936, 4, 8, 1537, 5, 7770, 12, 3479,
            30, 8, 97, 8176, 947, 10, 2567, 7, 755, 3670,
            3723, 3716
        ]

        ato = '''
        copyright 1996 david org copyright 2008 miller openbsd org permission to
        use copy modify and distribute this software for any purpose with or
        without fee is hereby granted provided that the above copyright notice
        and this permission notice appear in all copies modification and
        redistribution in source and binary forms is permitted provided that due
        credit is given to the author and the openbsd project for instance by
        leaving this copyright notice intact the software is provided as is and
        the author disclaims all warranties with regard to this software
        including all implied warranties of merchantability and fitness in no
        event shall the author be liable for any special direct indirect or
        consequential damages or any damages whatsoever resulting from loss of
        use data or profits whether in an action of contract negligence or other
        tortious action arising out of or in connection with the use or
        performance of this software this code is derived from section 17 1 of
        applied cryptography second edition which describes a stream cipher
        allegedly compatible with rsa labs rc4 cipher the actual description of
        which is a trade secret the same algorithm is used as a stream cipher
        called in tatu ylonen s ssh package here the stream cipher has been
        modified always to include the time when the state that makes it
        impossible to regenerate the same random sequence twice so this can t be
        used for encryption but will generate good random numbers rc4 is a
        registered trademark of rsa laboratories this code implements the md5
        message digest algorithm the algorithm is due to this code was written
        by colin plumb in 1993 no copyright is claimed this code is in the
        public domain do with it what you wish equivalent code is available from
        rsa data security inc this code has been tested against that and is
        equivalent except that you don t need to include two pages of legalese
        with every copy to compute the message digest of a of bytes declare an
        structure pass it to call as needed on full of bytes and then call which
        will fill a supplied 16 byte with the digest

        the beer ware license revision 42
        phk login dk wrote this file
        as long as you retain this notice you can do whatever you want with this
        stuff if we meet some day and you think this stuff is worth it you can
        buy me a beer in return poul henning kamp'''

        assert len(a) == len(ato.split())

        ato_357 = [
        'the', 'beer', 'ware', 'license', 'revision', '42', 'phk', 'login',
        'dk', 'wrote', 'this', 'file', 'as', 'long', 'as', 'you', 'retain',
        'this', 'notice', 'you', 'can', 'do', 'whatever', 'you', 'want', 'with',
        'this', 'stuff', 'if', 'we', 'meet', 'some', 'day', 'and', 'you',
        'think', 'this', 'stuff', 'is', 'worth', 'it', 'you', 'can', 'buy',
        'me', 'a', 'beer', 'in', 'return', 'poul', 'henning', 'kamp'
        ]

        # this is contiguous from qpos 357 to the end. and same length as a_357
        # and ato_357
        matchables = set([
            357, 358, 359, 360, 361, 362, 363, 364, 365, 366,
            367, 368, 369, 370, 371, 372, 373, 374, 375, 376,
            377, 378, 379, 380, 381, 382, 383, 384, 385, 386,
            387, 388, 389, 390, 391, 392, 393, 394, 395, 396,
            397, 398, 399, 400, 401, 402, 403, 404, 405, 406,
            407, 408]
        )

        assert len(matchables) == len(a_357) == len(ato_357) == 52

        b = [
            0, 2567, 2298, 6, 6670, 2103, 10248, 2179,

            # this is an extra token in b only (not in a), at bpos: 9=8
            13406,

            4107, 910,

            5, 72, 17, 412, 17, 8, 5878, 5, 53, 8,
            97, 76, 6165, 8, 438, 18, 5, 7770, 26, 162,
            555, 230, 936, 4, 8, 1537, 5, 7770, 12, 3479,
            30, 8, 97, 8176, 947, 10, 2567, 7, 755, 3670,
            3723, 3716,
        ]

        # this is mapping of high token ids in b to a list of positions
        # for instance, 10248 is the 'phk' token and is found at position 6 in b
        # and 7770 is stuff and found in two places
        b2j = {
            10248: [6],
            6670: [4],
            8176: [44],
            6165: [23],
            5878: [17],
            7770: [28, 38],
            13406: [8]
        }

        len_good = 20000

        a_start = 357
        b_start = 0
        b_end = 53

        tests = seq.find_longest_match(
            a=a,
            b=b,
            alo=a_start,
            ahi=len(a),
            blo=b_start,
            bhi=b_end,
            b2j=b2j,
            len_good=len_good,
            matchables=matchables,
        )
        assert tests == seq.Match(a=357, b=0, size=8)
