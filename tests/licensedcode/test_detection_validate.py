#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import unittest
from pprint import pprint

import pytest
import saneyaml
from commoncode.functional import flatten
from commoncode import text

from licensedcode import cache
from licensedcode import models
from licensedcode.models import licenses_data_dir
from licensedcode.models import rules_data_dir
from scancode_config import REGEN_TEST_FIXTURES

"""
Validate that each license and rule text is properly detected with exact
detection and that their ignorable clues are correctly detected.

TODO: to make the license detection test worthy, we should disable hash matching
such that we test everything else including the automaton, sets and
sequence detections.
"""


def make_validation_test(rule, test_name, regen=REGEN_TEST_FIXTURES):
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
            check_ignorable_clues(rule, regen=regen)

    closure_test_function.__name__ = test_name
    closure_test_function.funcname = test_name

    return closure_test_function


def check_special_rule_cannot_be_detected(rule):
    idx = cache.get_index()

    results = idx.match(query_string=rule.text)

    if results:
        rule_file = rule.rule_file()
        # On failure, we compare again to get additional failure details such as
        # a clickable text_file path
        results = (results, f'file://{rule_file}')
        # this assert will always fail and provide a more detailed failure trace
        assert results == []


def check_rule_or_license_can_be_self_detected_exactly(rule):
    idx = cache.get_index()
    matches = idx.match(
        query_string=rule.text,
        _skip_hash_match=True,
        deadline=10,
    )
    expected = [rule.identifier, '100']
    results = flatten((m.rule.identifier, str(int(m.coverage()))) for m in matches)

    try:
        assert results == expected
    except:

        from licensedcode.tracing import get_texts
        rule_file = rule.rule_file()
        # On failure, we compare again to get additional failure details such as
        # a clickable text_file path
        failure_trace = ['======= TEST ====']
        failure_trace.extend(results)
        failure_trace.extend(['',
            f'file://{rule_file}',
            '======================',
        ])

        for i, match in enumerate(matches):
            qtext, itext = get_texts(match)
            m_rule_file = match.rule.rule_file()

            failure_trace.extend(['',
                f'======= MATCH {i} ====',
                repr(match),
                f'file://{m_rule_file}',
                '======= Matched Query Text:', '', qtext, ''
                '======= Matched Rule Text:', '', itext
            ])

        # this assert will always fail and provide a detailed failure trace
        assert '\n'.join(failure_trace) == '\n'.join(expected)


def check_ignorable_clues(licensish, regen=REGEN_TEST_FIXTURES, verbose=False):
    """
    Validate that all expected ignorable clues declared in a `licensish` License
    or Rule object are properly detected in that rule text file. Optionally
    ``regen`` the ignorables to update the License or Rule .yml data file.
    """
    result = models.get_ignorables(text=licensish.text)

    if verbose:
        print()
        print('result')
        pprint(result)

    if regen:
        is_from_license = licensish.is_from_license
        if is_from_license:
            db = cache.get_licenses_db()
            licish = db[licensish.license_expression]
        else:
            licish = licensish

        models.set_ignorables(licish, result , verbose=verbose)

        if is_from_license:
            licish.dump(licenses_data_dir=licenses_data_dir)
            licensish = models.build_rule_from_license(licish)
        else:
            licish.dump(rules_data_dir=rules_data_dir)

    expected = models.get_normalized_ignorables(licensish)

    if verbose:
        print('expected')
        pprint(expected)

    try:
        assert result == expected
    except:
        # On failure, we compare again to get additional failure details such as
        # a clickable text_file path.

        result['file'] = f'file://{licensish.rule_file()}'

        # This assert will always fail and provide a more detailed failure trace
        assert saneyaml.dump(result) == saneyaml.dump(expected)


def build_validation_tests(rules, test_classes, regen=REGEN_TEST_FIXTURES):
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
            # we exclude the non-english rules from validation
            # as they are not included in the standard indexing
            if rule.language != 'en':
                continue
            test_name = (
                'test_validate_detect_' +
                text.python_safe_name(rule.identifier)
            )
            test_method = make_validation_test(
                rule=rule,
                test_name=test_name,
                regen=regen,
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
     ],
    regen=REGEN_TEST_FIXTURES,
)

del _rules
