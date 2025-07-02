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
from time import time

import pytest
import saneyaml
from commoncode import text

from licensedcode import cache
from licensedcode import models
from licensedcode.detection import is_correct_detection
from licensedcode.detection import has_extra_words_spans
from licensedcode.models import licenses_data_dir
from licensedcode.models import rules_data_dir
from licensedcode.models import License
from scancode_config import REGEN_TEST_FIXTURES

"""
Validate that each license and rule text is properly detected with exact
detection and that their ignorable clues are correctly detected.
"""


def make_validation_test(rule, test_name, regen=REGEN_TEST_FIXTURES):
    """
    Build and return a test function closing on tests arguments.
    """
    if isinstance(test_name, bytes):
        test_name = test_name.decode('utf-8')

    if rule.is_false_positive:

        def closure_test_function(*args, **kwargs):
            check_false_positive_rule_cannot_be_detected(rule)

    else:

        def closure_test_function(*args, **kwargs):
            check_rule_or_license_can_be_detected_exactly(rule)

    closure_test_function.__name__ = test_name
    closure_test_function.funcname = test_name

    return closure_test_function


def make_deprecated_validation_test(rule, test_name, regen=REGEN_TEST_FIXTURES):
    """
    Build and return a test function closing on tests arguments.
    """
    if isinstance(test_name, bytes):
        test_name = test_name.decode('utf-8')

    def closure_test_function(*args, **kwargs):
        check_deprecated_rule_or_license_can_be_detected(licensish=rule, regen=regen)

    closure_test_function.__name__ = test_name
    closure_test_function.funcname = test_name

    return closure_test_function


def check_false_positive_rule_cannot_be_detected(rule):
    idx = cache.get_index()

    results = idx.match(query_string=rule.text)

    if results:
        rule_file = rule.rule_file()
        # On failure, we compare again to get additional failure details such as
        # a clickable text_file path
        results = (results, f'file://{rule_file}')
        # this assert will always fail and provide a more detailed failure trace
        assert results == []


def check_rule_or_license_can_be_detected_exactly(licensish):
    """
    Check that a rule or license can be detected exactly, either by thyself (or with an exact match
    to any rule for deprecated rules).
    """
    idx = cache.get_index()
    deadline = time() + 20  # ms
    matches = idx.match(query_string=licensish.text, _skip_hash_match=True, deadline=deadline)
    # ensure we can self-detect exactly
    expected = [licensish.identifier]
    results = [m.rule.identifier for m in matches]

    if results != expected:
        expected.append(f'file://{licensish.rule_file()}')
        assert results == expected

    icm = is_correct_detection(matches)
    if not icm and not has_extra_words_spans(matches):
        expected.append(f'file://{licensish.rule_file()}')
        assert results == expected


def check_deprecated_rule_or_license_can_be_detected(licensish, regen=REGEN_TEST_FIXTURES):
    """
    Check that a deprecated rule or license can still be detected by other rules.
    """
    idx = cache.get_index()

    deadline = time() + 20  # ms
    matches = idx.match(query_string=licensish.text, deadline=deadline)

    if regen:
        detected_expressions = [m.rule.license_expression for m in matches]
        is_from_license = licensish.is_from_license
        if is_from_license:
            licensish = License.from_dir(key=licensish.license_expression)

        licensish.replaced_by = detected_expressions
        if is_from_license:
            licensish.dump(licenses_data_dir=licenses_data_dir)
        else:
            licensish.dump(rules_data_dir=rules_data_dir)
        return

    expected = list(licensish.replaced_by)
    results = [m.rule.license_expression for m in matches]

    if results != expected:
        expected.append(f'file://{licensish.rule_file()}')
        assert results == expected

    icm = is_correct_detection(matches)
    if not icm:
        expected.extend(m.representation(trace_text=True, trace_rule=True) for m in matches)
        expected.append(f'file://{licensish.rule_file()}')
        assert results == expected


def make_ignorable_clues_test(rule, test_name, regen=REGEN_TEST_FIXTURES):
    """
    Build and return a test function closing on tests arguments.
    """
    if isinstance(test_name, bytes):
        test_name = test_name.decode('utf-8')

    def closure_test_function(*args, **kwargs):
        check_ignorable_clues(rule, regen=regen)

    closure_test_function.__name__ = test_name
    closure_test_function.funcname = test_name

    return closure_test_function


def check_ignorable_clues(licensish, regen=REGEN_TEST_FIXTURES, verbose=False):
    """
    Validate that all expected ignorable clues declared in a `licensish` License
    or Rule object are properly detected in that rule text file. Optionally
    ``regen`` the ignorables to update the License or Rule .yml data file.
    """
    if licensish.is_false_positive or licensish.is_deprecated:
        return

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

    if result != expected:
        # On failure, we compare again to get additional failure details such as
        # a clickable text_file path.

        result['file'] = f'file://{licensish.rule_file()}'

        # This assert will always fail and provide a more detailed failure trace
        assert saneyaml.dump(result) == saneyaml.dump(expected)


def build_validation_tests(
    rules,
    test_classes,
    test_func_creator=make_validation_test,
    test_name_prefix="test_validate_detect_",
    regen=REGEN_TEST_FIXTURES,
):
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
            test_name = f"{test_name_prefix }{text.python_safe_name(rule.identifier)}"
            test_method = test_func_creator(
                rule=rule,
                test_name=test_name,
                regen=regen,
            )
            if test_method:
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


# keep deprecated to test we can detect them
_temp_rules = sorted(models.get_rules(with_deprecated=True), key=lambda r: r.identifier)
_deprecated_rules = [r for r in _temp_rules  if not r.is_false_positive and r.is_deprecated and not r.relevance == 0]
_current_rules = [r for r in _temp_rules  if not r.is_deprecated]
del _temp_rules

build_validation_tests(
    _current_rules,
    test_classes=[
        TestValidateLicenseBasic,
        TestValidateLicenseExtended1,
        TestValidateLicenseExtended2,
        TestValidateLicenseExtended3,
        TestValidateLicenseExtended4,
        TestValidateLicenseExtended5,
     ],
    test_func_creator=make_validation_test,
    test_name_prefix="test_validate_detect_",
    regen=REGEN_TEST_FIXTURES,
)

build_validation_tests(
    _deprecated_rules,
    test_classes=[
        TestValidateLicenseBasic,
        TestValidateLicenseExtended5,
     ],
    test_func_creator=make_deprecated_validation_test,
    test_name_prefix="test_validate_detect_deprecated_",
    regen=REGEN_TEST_FIXTURES,
)

del _deprecated_rules


class TestValidateLicenseIgnorableCluesBasic(unittest.TestCase):
    # Test functions are attached to this class at import time
    pytestmark = pytest.mark.scanslow


class TestValidateLicenseIgnorableClues1(unittest.TestCase):
    # Test functions are attached to this class at import time
    pytestmark = pytest.mark.scanvalidate


class TestValidateLicenseIgnorableClues2(unittest.TestCase):
    # Test functions are attached to this class at import time
    pytestmark = pytest.mark.scanvalidate


class TestValidateLicenseIgnorableClues3(unittest.TestCase):
    # Test functions are attached to this class at import time
    pytestmark = pytest.mark.scanvalidate


class TestValidateLicenseIgnorableClues4(unittest.TestCase):
    # Test functions are attached to this class at import time
    pytestmark = pytest.mark.scanvalidate


class TestValidateLicenseIgnorableClues5(unittest.TestCase):
    # Test functions are attached to this class at import time
    pytestmark = pytest.mark.scanvalidate


build_validation_tests(
    _current_rules,
    test_classes=[
        TestValidateLicenseIgnorableCluesBasic,
        TestValidateLicenseIgnorableClues1,
        TestValidateLicenseIgnorableClues2,
        TestValidateLicenseIgnorableClues3,
        TestValidateLicenseIgnorableClues4,
        TestValidateLicenseIgnorableClues5,
     ],
    test_func_creator=make_ignorable_clues_test,
    test_name_prefix="test_ignorables_in_rule_or_license_",
    regen=REGEN_TEST_FIXTURES,
)

del _current_rules
