#
# Copyright (c) 2015-2018 nexB Inc. and others. All rights reserved.
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

import os

from commoncode.testcase import FileBasedTesting

from licensedcode import index
from licensedcode.tracing import get_texts
from licensedcode.models import Rule
from licensedcode.models import load_rules
from licensedcode import match_seq

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestMatchSeq(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_template_with_few_tokens_around_gaps_is_wholly_seq_matched(self):
        # was failing when a gapped token (from a template) starts at a
        # beginning of an index doc. We may still skip that, but capture a large match anyway.

        rule_text = u'''
            Copyright {{some copyright}}
            THIS IS FROM {{THE CODEHAUS}} AND CONTRIBUTORS
            IN NO EVENT SHALL {{THE CODEHAUS}} OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE {{POSSIBILITY OF SUCH}} DAMAGE
        '''

        rule = Rule(_text=rule_text, licenses=['test'],)
        idx = index.LicenseIndex([rule])

        querys = u'''
            Copyright 2003 (C) James. All Rights Reserved.
            THIS IS FROM THE CODEHAUS AND CONTRIBUTORS
            IN NO EVENT SHALL THE CODEHAUS OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
        '''
        result = idx.match(query_string=querys)
        assert 1 == len(result)
        match = result[0]
        assert match_seq.MATCH_SEQ == match.matcher

        exp_qtext = u"""
            Copyright [2003] [C] [James] [All] [Rights] [Reserved]
            THIS IS FROM <THE> [CODEHAUS]
            AND CONTRIBUTORS
            IN NO EVENT SHALL <THE> [CODEHAUS] OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE [POSSIBILITY] <OF> [SUCH] DAMAGE
        """.split()

        exp_itext = u"""
            Copyright
            THIS IS FROM
            AND CONTRIBUTORS
            IN NO EVENT SHALL OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE DAMAGE
        """.split()
        qtext, itext = get_texts(match, query_string=querys, idx=idx)
        assert exp_qtext == qtext.split()
        assert exp_qtext == qtext.split()
        assert exp_itext == itext.split()
        assert 99 <= match.coverage()

    def test_match_seq_are_correct_on_apache(self):
        rule_dir = self.get_test_loc('match_seq/rules')
        idx = index.LicenseIndex(load_rules(rule_dir))

        query_loc = self.get_test_loc('match_seq/query')
        matches = idx.match(location=query_loc)
        assert 1 == len(matches)
        match = matches[0]
        assert match_seq.MATCH_SEQ == match.matcher
        qtext, _itext = get_texts(match, location=query_loc, idx=idx)
        expected = u'''
        The OpenSymphony Group All rights reserved Redistribution and use in source and
        binary forms with or without modification are permitted provided that the following
        conditions are met 1 Redistributions of source code must retain the above copyright
        notice this list of conditions and the following disclaimer 2 Redistributions in
        binary form must reproduce the above copyright notice this list of conditions and the
        following disclaimer in the documentation and or other materials provided with the
        distribution 3 The end user documentation included with the redistribution if any
        must include the following acknowledgment <4> <This> <product> <includes> <software>
        <developed> <by> <the> <OpenSymphony> <Group> <http> <www> <opensymphony> <com> <5>
        Alternately this acknowledgment may appear in the software itself if and wherever
        such third party acknowledgments normally appear The names OpenSymphony and The
        OpenSymphony Group must not be used to endorse or promote products derived from this
        software without prior written permission For written permission please contact
        license opensymphony com Products derived from this software may not be called
        OpenSymphony or [OsCore] nor may OpenSymphony or [OsCore] appear in their name
        without prior written permission of the OpenSymphony Group THIS SOFTWARE IS PROVIDED
        AS IS AND ANY EXPRESSED OR IMPLIED WARRANTIES INCLUDING BUT NOT LIMITED TO THE
        IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
        DISCLAIMED IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR ITS CONTRIBUTORS BE
        LIABLE FOR ANY DIRECT INDIRECT INCIDENTAL SPECIAL EXEMPLARY OR CONSEQUENTIAL DAMAGES
        INCLUDING BUT NOT LIMITED TO PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS OF USE
        DATA OR PROFITS OR BUSINESS INTERRUPTION HOWEVER CAUSED AND ON ANY THEORY OF
        LIABILITY WHETHER IN CONTRACT STRICT LIABILITY OR TORT INCLUDING NEGLIGENCE OR
        OTHERWISE ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE EVEN IF ADVISED OF THE
        POSSIBILITY OF SUCH DAMAGE
        '''
        assert expected.split() == qtext.split()
