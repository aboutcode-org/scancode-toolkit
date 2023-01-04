#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from commoncode.testcase import FileBasedTesting

from licensedcode import index
from licensedcode import match_seq
from licensedcode.legalese import build_dictionary_from_iterable
from licensedcode.models import load_rules
from licensedcode.tracing import get_texts

from licensedcode_test_utils import mini_legalese  # NOQA
from licensedcode_test_utils import create_rule_from_text_and_expression

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestMatchSeq(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_template_with_few_tokens_around_gaps_is_wholly_seq_matched(self):
        # was failing when a gapped token (from a template) starts at a
        # beginning of an index doc. We may still skip that, but capture a large match anyway.

        rule_text = u'''
            Copyright
            THIS IS FROM [[THE OLD CODEHAUS]] AND CONTRIBUTORS
            IN NO EVENT SHALL [[THE OLD CODEHAUS]] OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE [[POSSIBILITY OF NEW SUCH]] DAMAGE
        '''

        rule = create_rule_from_text_and_expression(text=rule_text, license_expression='test')

        legalese = build_dictionary_from_iterable(
            set(mini_legalese) |
            set(['copyright', 'reserved', 'advised', 'liable', 'damage',
                 'contributors', 'alternately', 'possibility'])
        )
        idx = index.LicenseIndex([rule], _legalese=legalese)

        querys = u'''
            Copyright 2003 (C) James. All Rights Reserved.
            THIS IS FROM THE CODEHAUS AND CONTRIBUTORS
            IN NO EVENT SHALL THE CODEHAUS OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
        '''
        result = idx.match(query_string=querys)
        assert len(result) == 1
        match = result[0]
        assert match.matcher == match_seq.MATCH_SEQ

        exp_qtext = u"""
            Copyright [2003] ([C]) [James]. [All] [Rights] [Reserved].
            [THIS] [IS] [FROM] [THE] CODEHAUS AND CONTRIBUTORS
            IN NO EVENT SHALL THE CODEHAUS OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
        """.split()

        exp_itext = u"""
            Copyright
            <THIS> <IS> <FROM> <THE> <OLD> CODEHAUS AND CONTRIBUTORS
            IN NO EVENT SHALL THE <OLD> CODEHAUS OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE POSSIBILITY OF <NEW> SUCH DAMAGE
        """.lower().split()
        qtext, itext = get_texts(match)
        assert qtext.split() == exp_qtext
        assert qtext.split() == exp_qtext
        assert itext.split() == exp_itext
        assert match.coverage() >= 70

    def test_match_seq_are_correct_on_apache(self):
        rule_dir = self.get_test_loc('match_seq/rules')

        legalese = build_dictionary_from_iterable(
            set(mini_legalese) |
            set(['redistributions', 'written', 'registered', 'derived',
                 'damage', 'due', 'alternately', 'nor'])
        )
        idx = index.LicenseIndex(load_rules(rule_dir), _legalese=legalese)

        query_loc = self.get_test_loc('match_seq/query')
        matches = idx.match(location=query_loc)
        assert len(matches) == 1
        match = matches[0]
        assert match.matcher == match_seq.MATCH_SEQ
        qtext, _itext = get_texts(match)
        expected = u'''
            The OpenSymphony Group. All rights reserved.

            Redistribution and use in source and binary forms, with or without modification,
            are permitted provided that the following conditions are met:

            1. Redistributions of source code must retain the above copyright notice, this
            list of conditions and the following disclaimer.

            2. Redistributions in binary form must reproduce the above copyright notice,
            this list of conditions and the following disclaimer in the documentation and/or
            other materials provided with the distribution.

            3. The end-user documentation included with the redistribution, if any, must
            include the following acknowledgment:

            [4]. "[This] [product] [includes] [software] [developed] [by] [the] [OpenSymphony] [Group]
            ([http]://[www].[opensymphony].[com]/)."

            [5]. Alternately, this acknowledgment may appear in the software itself, if and
            wherever such third-party acknowledgments normally appear.

            The names "OpenSymphony" and "The OpenSymphony Group" must not be used to
            endorse or promote products derived from this software without prior written
            permission. For written permission, please contact license@opensymphony.com .

            Products derived from this software may not be called "OpenSymphony" or
            "[OsCore]", nor may "OpenSymphony" or "[OsCore]" appear in their name, without prior
            written permission of the OpenSymphony Group.

            THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED WARRANTIES,
            INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
            FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE APACHE
            SOFTWARE FOUNDATION OR ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
            INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
            LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
            PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
            LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
            OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
            ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
        '''
        assert qtext.split() == expected.split()
