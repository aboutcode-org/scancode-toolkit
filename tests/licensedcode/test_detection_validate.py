#
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
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

from collections import OrderedDict
import os
import unittest

import pytest
import saneyaml

from commoncode import compat
from commoncode.functional import flatten
from commoncode import text
from commoncode.system import py2
from commoncode.system import py3
from licensedcode import cache
from licensedcode import models


"""
Validate that each license and rule text is properly detected with exact
detection and that their ignorable clues are correctly detected.

TODO: to make the license detection test worthy, we should disable hash matching
such that we test everything else including the negative, automaton, sets and
seq detections.
"""


def make_validation_test(rule, test_name):
    """
    Build and return a test function closing on tests arguments.
    """
    if py2 and isinstance(test_name, compat.unicode):
        test_name = test_name.encode('utf-8')
    if py3 and isinstance(test_name, bytes):
        test_name = test_name.decode('utf-8')

    if rule.is_negative or rule.is_false_positive:
        def closure_test_function(*args, **kwargs):
            check_special_rule_can_be_detected(rule)
    else:
        def closure_test_function(*args, **kwargs):
            check_rule_or_license_can_be_self_detected_exactly(rule)
            check_ignorable_clues(rule)

    closure_test_function.__name__ = test_name
    closure_test_function.funcname = test_name

    return closure_test_function


def check_special_rule_can_be_detected(rule):
    idx = cache.get_index()
    results = idx.match(location=rule.text_file)
    try:
        assert not results
    except:
        data_file = rule.data_file
        if not data_file:
            data_file = rule.text_file.replace('.LICENSE', '.yml')
        # On failure, we compare againto get additional failure details such as
        # a clickable text_file path
        results = (
            results,
            'file://{data_file}'.format(**locals()),
            'file://{text_file}'.format(**locals()),
        )
        # this assert will always fail and provide a more detailed failure trace
        assert not results


def check_rule_or_license_can_be_self_detected_exactly(rule):
    idx = cache.get_index()
    matches = idx.match(location=rule.text_file, _skip_hash_match=True)
    expected = [rule.identifier, '100']
    results = flatten((m.rule.identifier, str(int(m.coverage()))) for m in matches)

    try:
        assert expected == results
    except:

        from licensedcode.tracing import get_texts
        data_file = rule.data_file
        if not data_file:
            data_file = rule.text_file.replace('.LICENSE', '.yml')
        text_file = rule.text_file
        # On failure, we compare againto get additional failure details such as
        # a clickable text_file path
        failure_trace = ['======= TEST ====']
        failure_trace.extend(results)
        failure_trace.extend(['',
            'file://{data_file}'.format(**locals()),
            'file://{text_file}'.format(**locals()),
            '======================',
        ])

        for i, match in enumerate(matches):
            qtext, itext = get_texts(match)
            m_text_file = match.rule.text_file
            if match.rule.is_license:
                m_data_file = m_text_file.replace('LICENSE', '.yml')
            else:
                m_data_file = match.rule.data_file

            failure_trace.extend(['',
                '======= MATCH {} ===='.format(i), repr(match),
                'file://{m_data_file}'.format(**locals()),
                'file://{m_text_file}'.format(**locals()),
                '======= Matched Query Text:', '', qtext, ''
                '======= Matched Rule Text:', '', itext
            ])

        # this assert will always fail and provide a detailed failure trace
        assert '\n'.join(expected) == '\n'.join(failure_trace)


def check_ignorable_clues(rule):
    """
    Validate that all ignorable clues defined in a `rule` Rule object are
    properly detected in that rule text file.
    """
    from itertools import chain
    from scancode import api

    text_file = rule.text_file

    # scan clues
    scan_data = {}
    scan_data.update(api.get_copyrights(text_file))
    scan_data.update(api.get_urls(text_file, threshold=0))
    scan_data.update(api.get_emails(text_file, threshold=0))

    results = OrderedDict()
    for what, detections in scan_data.items():
        # remove lines
        for detected in detections:
            detected.pop('start_line', None)
            detected.pop('end_line', None)

        # remove keys and keep only values e.g. a list of detected copyrights,
        # emails, etc
        detections = sorted(set(chain(*(detected.values() for detected in detections))))
        results['ignorable_' + what] = detections

    # collect ignorables
    expected = OrderedDict([
        ('ignorable_copyrights', rule.ignorable_copyrights or []),
        ('ignorable_holders', rule.ignorable_holders or []),
        ('ignorable_authors', rule.ignorable_authors or []),
        ('ignorable_urls', rule.ignorable_urls or []),
        ('ignorable_emails', rule.ignorable_emails or []),
    ])

    results = OrderedDict([(k, v) for k, v in sorted(results.items()) if v])
    expected = OrderedDict([(k, v) for k, v in sorted(expected.items()) if v])

    try:
        assert expected == results
    except:
        # On failure, we compare againto get additional failure details such as
        # a clickable text_file path

        data_file = rule.data_file
        if not data_file:
            data_file = text_file.replace('.LICENSE', '.yml')
        results['files'] = [
            'file://{data_file}'.format(**locals()),
            'file://{text_file}'.format(**locals()),
        ]
        # this assert will always fail and provide a more detailed failure trace
        assert saneyaml.dump(expected) == saneyaml.dump(results)


def build_validation_tests(rules, class_basic, class_extended):
    """
    Dynamically build an individual test method for each rule texts in a `rules`
    iterable of Rule objects then attach the test method to the `class_basic` and `class_extended` test
    classes for basic and extended respectively.
    """
    # TODO: add test to detect the standard notice??

    cls = class_basic
    for i, rule in enumerate(rules):
        # only push 20 rules in the basic set
        if i > 20:
            cls = class_extended
        if rule.text_file and os.path.exists(rule.text_file):
            test_name = ('test_validate_detect_' + text.python_safe_name(rule.identifier))
            test_method = make_validation_test(rule=rule, test_name=test_name)
            setattr(cls, test_name, test_method)


class TestValidateLicenseBasic(unittest.TestCase):
    # Test functions are attached to this class at import time
    pytestmark = pytest.mark.scanslow


class TestValidateLicenseExtended(unittest.TestCase):
    # Test functions are attached to this class at import time
    pytestmark = pytest.mark.scanvalidate


_rules = sorted(models.get_rules(), key=lambda r: r.identifier)
build_validation_tests(_rules, TestValidateLicenseBasic, TestValidateLicenseExtended)
del _rules
