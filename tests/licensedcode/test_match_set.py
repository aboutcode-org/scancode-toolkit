#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from licensedcode import index
from licensedcode import match_set
from licensedcode.match_set import ScoresVector
from licensedcode.match_set import truncate_candidates_on_score_boundary
from licensedcode.query import build_query

from licensedcode_test_utils import create_rule_from_text_and_expression
from licensedcode_test_utils import mini_legalese


def MiniLicenseIndex(*args, **kwargs):
    return index.LicenseIndex(*args, _legalese=mini_legalese, **kwargs)


def scores(containment=0.8, resemblance=0.0, matched_length=0.8):
    return ScoresVector(
        is_highly_resemblant=False,
        containment=containment,
        resemblance=resemblance,
        matched_length=matched_length,
    )


def candidate(rounded_scores, identifier='a.RULE'):
    """
    Return a minimal candidate tuple with the same shape as the items returned
    by match_set.compute_candidates().
    """
    return ((rounded_scores, rounded_scores), 0, identifier, None)


def test_truncate_candidates_on_score_boundary_returns_all_candidates_below_top():
    candidates = [candidate(scores())]
    assert truncate_candidates_on_score_boundary(candidates, top=10) == candidates


def test_truncate_candidates_on_score_boundary_truncates_between_different_scores():
    candidates = [
        candidate(scores(containment=1.0), 'first.RULE'),
        candidate(scores(containment=0.9), 'second.RULE'),
        candidate(scores(containment=0.8), 'third.RULE'),
    ]
    truncated = truncate_candidates_on_score_boundary(candidates, top=2)
    assert [c[2] for c in truncated] == ['first.RULE', 'second.RULE']


def test_truncate_candidates_on_score_boundary_does_not_truncate_equal_rounded_scores():
    # The third and fourth candidates have the same rounded scores as the
    # second one: they are ranked equally well and must not be cut arbitrarily.
    candidates = [
        candidate(scores(containment=1.0), 'first.RULE'),
        candidate(scores(containment=0.8, resemblance=0.1), 'second.RULE'),
        candidate(scores(containment=0.8, resemblance=0.1), 'third.RULE'),
        candidate(scores(containment=0.8, resemblance=0.1), 'fourth.RULE'),
        candidate(scores(containment=0.7), 'fifth.RULE'),
    ]
    truncated = truncate_candidates_on_score_boundary(candidates, top=2)
    assert [c[2] for c in truncated] == ['first.RULE', 'second.RULE', 'third.RULE', 'fourth.RULE']


def test_truncate_candidates_on_score_boundary_returns_no_candidate_for_zero_top():
    candidates = [candidate(scores())]
    assert truncate_candidates_on_score_boundary(candidates, top=0) == []


def test_compute_candidates_keeps_all_candidates_with_equal_rounded_scores_at_cutoff():
    # Two rules with the same length and the same match scores are equally
    # ranked candidates. With a `top` of 1, the second one must not be
    # discarded because it has the same rounded scores as the last kept one.
    rules = [
        create_rule_from_text_and_expression(
            text='A one. A license two. A three.',
            license_expression='abc',
            identifier='abc_1.RULE',
        ),
        create_rule_from_text_and_expression(
            text='A four. A license five. A six.',
            license_expression='xyz',
            identifier='xyz_1.RULE',
        ),
    ]
    idx = MiniLicenseIndex(rules)

    query = 'A one. A license two. A three. A four. A license five. A six.'
    qry = build_query(query_string=query, idx=idx)
    assert qry is not None
    query_run = qry.whole_query_run()

    def compute_candidates():
        return match_set.compute_candidates(query_run, idx, idx.approx_matchable_rids, top=1)

    assert len(compute_candidates()) == 1

    qry.has_long_lines = True
    candidates = compute_candidates()
    assert len(candidates) == 2
    assert sorted(c[2].identifier for c in candidates) == ['abc_1.RULE', 'xyz_1.RULE']
