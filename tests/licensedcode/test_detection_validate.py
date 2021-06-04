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
from pprint import pprint

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
            check_special_rule_cannot_be_detected(rule)

    else:

        def closure_test_function(*args, **kwargs):
            check_rule_or_license_can_be_self_detected_exactly(rule)
            check_ignorable_clues(rule)

    closure_test_function.__name__ = test_name
    closure_test_function.funcname = test_name

    return closure_test_function


def check_special_rule_cannot_be_detected(rule):
    idx = cache.get_index()
    results = idx.match(location=rule.text_file)
    if results:
        data_file = rule.data_file
        if not data_file:
            data_file = rule.text_file.replace('.LICENSE', '.yml')
        # On failure, we compare againto get additional failure details such as
        # a clickable text_file path
        results = (results, f'file://{data_file}', f'file://{rule.text_file}')
        # this assert will always fail and provide a more detailed failure trace
        assert  results == []


def check_rule_or_license_can_be_self_detected_exactly(rule):
    idx = cache.get_index()
    matches = idx.match(
        location=rule.text_file,
        _skip_hash_match=True,
        deadline=10,
    )
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
            f'file://{data_file}',
            f'file://{text_file}',
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
                f'======= MATCH {i} ====',
                repr(match),
                f'file://{m_data_file}',
                f'file://{m_text_file}',
                '======= Matched Query Text:', '', qtext, ''
                '======= Matched Rule Text:', '', itext
            ])

        # this assert will always fail and provide a detailed failure trace
        assert '\n'.join(failure_trace) == '\n'.join(expected)


def check_ignorable_clues(licensish, regen=False, verbose=True):
    """
    Validate that all current ignorable clues declared in a `licensish` License
    or Rule object are properly detected in that rule text file. Optionally
    regen the new_ignorables and updates the .yml files.
    """
    new_ignorables = models.get_ignorables(
        text_file=licensish.text_file,
    )
    if verbose:
        print()
        print('new_ignorables')
        pprint(new_ignorables)

    if regen:
        models.set_ignorables(licensish, new_ignorables , verbose=verbose)
        licensish.dump()

    current = dict(
        ignorable_copyrights=sorted(licensish.ignorable_copyrights or []),
        ignorable_holders=sorted(licensish.ignorable_holders or []),
        ignorable_authors=sorted(licensish.ignorable_authors or []),
        ignorable_urls=sorted(licensish.ignorable_urls or []),
        ignorable_emails=sorted(licensish.ignorable_emails or []),
    )

    current = dict([(k, v) for k, v in sorted(current.items()) if v])

    if verbose:
        print('current')
        pprint(current)

    try:
        assert current == new_ignorables
    except:
        # On failure, we compare again to get additional failure details such as
        # a clickable text_file path.

        data_file = licensish.data_file
        if not data_file:
            data_file = licensish.text_file.replace('.LICENSE', '.yml')

        new_ignorables['files'] = [
            f'file://{data_file}',
            f'file://{licensish.text_file}',
        ]

        # This assert will always fail and provide a more detailed failure trace
        assert saneyaml.dump(new_ignorables) == saneyaml.dump(current)


def build_validation_tests(rules, test_classes):
    """
    Dynamically build an individual test method for each rule texts in a
    ``rules`` iterable of Rule objects then attach the test methods to the
    ``test_classes`` lits of test classes.
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
                test_name = (
                    'test_validate_detect_' +
                    text.python_safe_name(rule.identifier)
                )
                test_method = make_validation_test(
                    rule=rule,
                    test_name=test_name,
                )
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
