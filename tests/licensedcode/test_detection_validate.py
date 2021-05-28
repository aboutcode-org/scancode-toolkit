#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import unittest

import pytest
import saneyaml

from commoncode.functional import flatten
from commoncode import text
from licensedcode import cache
from licensedcode import models

"""
Validate that each license and rule text is properly detected with exact
detection and that their ignorable clues are correctly detected.

TODO: to make the license detection test worthy, we should disable hash matching
such that we test everything else including the automaton, sets and
sequence detections.
"""


def make_validation_test(rule, test_name):
    """
    Build and return a test function closing on tests arguments.
    """
    if isinstance(test_name, bytes):
        test_name = test_name.decode('utf-8')

    if rule.is_false_positive:

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
        assert results == expected
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
            if match.rule.is_from_license:
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


def check_ignorable_clues(rule, regen=False):
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

    results = {}
    for what, detections in scan_data.items():
        # remove lines
        for detected in detections:
            detected.pop('start_line', None)
            detected.pop('end_line', None)

        # remove keys and keep only values e.g. a list of detected copyrights,
        # emails, etc
        detections = sorted(set(chain(*(detected.values() for detected in detections))))
        results['ignorable_' + what] = detections

    results = dict([(k, v) for k, v in sorted(results.items()) if v])

    if regen:
        for k, v in results.items():
            setattr(rule, k, v)
        rule.dump()

    # collect ignorables
    expected = dict([
        ('ignorable_copyrights', sorted(rule.ignorable_copyrights or [])),
        ('ignorable_holders', sorted(rule.ignorable_holders or [])),
        ('ignorable_authors', sorted(rule.ignorable_authors or [])),
        ('ignorable_urls', sorted(rule.ignorable_urls or [])),
        ('ignorable_emails', sorted(rule.ignorable_emails or [])),
    ])

    expected = dict([(k, v) for k, v in sorted(expected.items()) if v])

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
        assert saneyaml.dump(results) == saneyaml.dump(expected)


def build_validation_tests(rules, test_classes):
    """
    Dynamically build an individual test method for each rule texts in a `rules`
    iterable of Rule objects then attach the test method to the `class_basic` and `class_extended` test
    classes for basic and extended respectively.
    """
    # TODO: add test to detect the standard notice??

    # we split our rules in chunks, one for each extended classes we have
    # so we can split tests more or less evenly between them
    # the first chunk is an arbitrary 200 length
    chunks = [rules[:200]]
    extended_rules = rules[200:]
    number_of_ext_cls = len(test_classes) - 1
    slice_length = int(len(extended_rules) / number_of_ext_cls)

    for i in range(0, len(extended_rules), slice_length):
        chnk = extended_rules[i:i + slice_length]
        chunks.append(chnk)

    for chunk, cls in zip(chunks, test_classes):
        for rule in chunk:
            if rule.text_file and os.path.exists(rule.text_file):
                test_name = ('test_validate_detect_' + text.python_safe_name(rule.identifier))
                test_method = make_validation_test(rule=rule, test_name=test_name)
                setattr(cls, test_name, test_method)


class TestValidateLicenseBasic(unittest.TestCase):
    # Test functions are attached to this class at import time
    pytestmark = pytest.mark.scanslow


class TestValidateLicenseExtended1(unittest.TestCase):
    # Test functions are attached to this class at import time
    pytestmark = pytest.mark.scanvalidate


class TestValidateLicenseExtended2(unittest.TestCase):
    # Test functions are attached to this class at import time
    pytestmark = pytest.mark.scanvalidate


class TestValidateLicenseExtended3(unittest.TestCase):
    # Test functions are attached to this class at import time
    pytestmark = pytest.mark.scanvalidate


class TestValidateLicenseExtended4(unittest.TestCase):
    # Test functions are attached to this class at import time
    pytestmark = pytest.mark.scanvalidate


class TestValidateLicenseExtended5(unittest.TestCase):
    # Test functions are attached to this class at import time
    pytestmark = pytest.mark.scanvalidate


_rules = sorted(models.get_rules(), key=lambda r: r.identifier)
build_validation_tests(
    _rules,
    test_classes=[
        TestValidateLicenseBasic,
        TestValidateLicenseExtended1,
        TestValidateLicenseExtended2,
        TestValidateLicenseExtended3,
        TestValidateLicenseExtended4,
        TestValidateLicenseExtended5,
     ]
)
del _rules
