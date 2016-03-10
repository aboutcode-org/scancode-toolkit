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

from unittest.case import TestCase

from licensedcode.whoosh_spans.spans import Span


class TestSpans(TestCase):

    def test_merge_span_with_no_touching_spans(self):
        pos1 = Span(58, 58)
        pos2 = Span(63, 64)
        expected = [Span(58, 58), Span(63, 64)]
        result = Span.merge([pos2, pos1])
        assert expected == result

    def test_merge_span_with_overlap(self):
        pos21 = Span(12, 24)
        pos22 = Span(15, 35)
        pos11 = Span(58, 58)
        pos12 = Span(63, 64)
        expected = [Span(12, 35), Span(58, 58), Span(63, 64)]
        result = Span.merge([pos11, pos21, pos12, pos22])
        assert expected == result
