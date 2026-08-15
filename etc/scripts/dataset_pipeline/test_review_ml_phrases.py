# tests for review_ml_phrases.py
# no model and no network, the tagger is stubbed and the crf is built here
# etc is in pytest's norecursedirs so these do not run in CI, run them by path:
#   pytest etc/scripts/dataset_pipeline/test_review_ml_phrases.py
import itertools
import json
import os
import sys
from pathlib import Path

import click
import pytest
from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parent))
import review_ml_phrases
from review_ml_phrases import accepted_phrases
from review_ml_phrases import APPROVED
from review_ml_phrases import AUTO
from review_ml_phrases import check_thresholds
from review_ml_phrases import cli
from review_ml_phrases import DROPPED
from review_ml_phrases import is_injectable
from review_ml_phrases import LOW
from review_ml_phrases import new_phrase
from review_ml_phrases import new_predict_counts
from review_ml_phrases import new_record
from review_ml_phrases import PENDING
from review_ml_phrases import phrase_sort_key
from review_ml_phrases import preview_injection
from review_ml_phrases import read_review_file
from review_ml_phrases import REJECTED
from review_ml_phrases import REVIEW
from review_ml_phrases import span_confidence
from review_ml_phrases import tag_and_score
from review_ml_phrases import tier_for
from review_ml_phrases import write_review_file
from train_model import LABEL2ID
from train_model import LABELS

import licensedcode.required_phrases as required_phrases
from licensedcode.models import Rule

TEXT = 'Granted under the MIT License to do things with this software'


class FakeEncoding(dict):

    def __init__(self, word_ids):
        super().__init__()
        self._word_ids = word_ids
        self['input_ids'] = [[0] * len(word_ids)]
        self['attention_mask'] = [[1] * len(word_ids)]

    def word_ids(self):
        return self._word_ids


class FakeTokenizer:
    """CLS, one subword per word, SEP, cut off at max_length"""

    def __call__(self, words, max_length=512, **kwargs):
        word_ids = [None] + list(range(len(words))) + [None]
        return FakeEncoding(word_ids[:max_length])


class StubTagger:
    """Puts the given labels on the given word offsets

    The crf is real but zeroed, so decoding is a plain argmax over the emissions
    and the tags a test asks for are the tags it gets
    """

    def __init__(self, tagged):
        import torch
        from torchcrf import CRF

        self.tagged = tagged
        self.crf = CRF(len(LABELS), batch_first=True)
        with torch.no_grad():
            for param in self.crf.parameters():
                param.zero_()

    def emissions(self, input_ids, attention_mask):
        import torch

        width = len(input_ids[0])
        scores = torch.zeros((1, width, len(LABELS)))
        for offset, label in self.tagged.items():
            # subword offset + 1 because of the leading CLS
            scores[0, offset + 1, LABEL2ID[label]] = 9.0
        return scores


def make_rule(text=TEXT, identifier='mit_1.RULE'):
    rule = Rule(
        license_expression='mit',
        identifier=identifier,
        text=text,
        is_license_reference=True,
        relevance=100,
    )
    rule.source = None
    return rule


def use_tmp_rules(monkeypatch, tmp_path):
    """Point both rules_data_dir bindings at tmp_path

    review_ml_phrases reads its own in load_rule, and required_phrases keeps a
    separate one that add_required_phrase_to_rule writes through, so patching
    only the first would send real writes into the repo
    """
    monkeypatch.setattr(review_ml_phrases, 'rules_data_dir', str(tmp_path))
    monkeypatch.setattr(required_phrases, 'rules_data_dir', str(tmp_path))


def write_rule(tmp_path, text=TEXT, identifier='mit_1.RULE'):
    rule = make_rule(text=text, identifier=identifier)
    rule.dump(str(tmp_path))
    return rule


def rule_digests(tmp_path):
    return {
        path.name: path.read_bytes()
        for path in sorted(Path(tmp_path).glob('*.RULE'))
    }


def make_review_file(tmp_path, phrases, identifier='mit_1.RULE', text=TEXT):
    """A rule on disk and a review file naming it"""
    rule = write_rule(tmp_path, text=text, identifier=identifier)
    path = tmp_path / 'review.jsonl'
    write_review_file(str(path), [new_record(rule, phrases, False)])
    return str(path)


def decisions(path):
    return [
        (phrase['text'], phrase['decision'])
        for record in read_review_file(path)
        for phrase in record['phrases']
    ]


def build_crf(num_tags, seed=7):
    """A small crf with real transitions, in float64 so the maths is exact"""
    import torch
    from torchcrf import CRF

    torch.manual_seed(seed)
    crf = CRF(num_tags, batch_first=True).to(torch.float64)
    with torch.no_grad():
        crf.transitions.copy_(torch.randn(num_tags, num_tags).to(torch.float64))
        crf.start_transitions.copy_(torch.randn(num_tags).to(torch.float64))
        crf.end_transitions.copy_(torch.randn(num_tags).to(torch.float64))
    return crf


def decode_once(crf, emissions):
    """The best path, its mask and its log likelihood"""
    import torch

    mask = torch.ones(emissions.shape[:2], dtype=torch.bool)
    tags = torch.tensor([crf.decode(emissions, mask=mask)[0]])
    free = crf(emissions, tags, mask=mask, reduction='none')
    return tags, mask, free


class TestPhraseSortKey:

    def test_longest_first(self):
        phrases = ['mit', 'mit license', 'a']
        assert sorted(phrases, key=phrase_sort_key) == ['mit license', 'mit', 'a']

    def test_equal_length_goes_alphabetical(self):
        assert sorted(['bbb', 'aaa'], key=phrase_sort_key) == ['aaa', 'bbb']


class TestReviewFile:

    def test_round_trip_is_the_identity(self, tmp_path):
        # Feature: ml-phrase-review-cli, Property 3: review file round trip is the identity
        path = str(tmp_path / 'review.jsonl')
        # two phrases of equal length, the case an unstable sort would break
        records = [new_record(make_rule(), [
            new_phrase('bbb', 0.5, LOW, DROPPED),
            new_phrase('aaa', 0.4, LOW, DROPPED),
            new_phrase('MIT License', 0.98, AUTO, AUTO),
            new_phrase('do things', 0.8, REVIEW, PENDING),
        ], False)]

        write_review_file(path, records)
        first = Path(path).read_bytes()
        write_review_file(path, read_review_file(path))

        assert Path(path).read_bytes() == first

    def test_phrases_are_stored_longest_first(self, tmp_path):
        path = str(tmp_path / 'review.jsonl')
        write_review_file(path, [new_record(make_rule(), [
            new_phrase('mit', 0.7, REVIEW, PENDING),
            new_phrase('mit license', 0.9, REVIEW, PENDING),
        ], False)])

        texts = [phrase['text'] for phrase in read_review_file(path)[0]['phrases']]
        assert texts == ['mit license', 'mit']

    def test_a_record_carries_the_rule_and_the_truncated_flag(self):
        record = new_record(make_rule(), [new_phrase('mit license', 0.9, AUTO, AUTO)], True)
        assert record['identifier'] == 'mit_1.RULE'
        assert record['license_expression'] == 'mit'
        assert record['truncated'] is True

    def test_an_edit_keeps_the_predicted_text(self):
        phrase = new_phrase('MIT License', 0.9, REVIEW, PENDING)
        phrase['text'] = 'MIT License to'
        assert phrase['predicted_text'] == 'MIT License'

    def test_blank_lines_are_skipped(self, tmp_path):
        path = tmp_path / 'review.jsonl'
        record = new_record(make_rule(), [new_phrase('mit license', 0.9, AUTO, AUTO)], False)
        path.write_text(json.dumps(record) + '\n\n', encoding='utf-8')
        assert len(read_review_file(str(path))) == 1

    def test_a_bad_line_names_its_number(self, tmp_path):
        path = tmp_path / 'review.jsonl'
        path.write_text('{}\nnot json\n', encoding='utf-8')
        with pytest.raises(click.ClickException) as caught:
            read_review_file(str(path))
        assert 'line 1' in str(caught.value)

    def test_a_missing_phrase_field_names_its_number(self, tmp_path):
        path = tmp_path / 'review.jsonl'
        record = new_record(make_rule(), [new_phrase('mit license', 0.9, AUTO, AUTO)], False)
        del record['phrases'][0]['confidence']
        path.write_text(json.dumps(record) + '\n', encoding='utf-8')
        with pytest.raises(click.ClickException) as caught:
            read_review_file(str(path))
        assert "line 1" in str(caught.value) and 'confidence' in str(caught.value)

    def test_a_failed_write_keeps_the_previous_file(self, tmp_path, monkeypatch):
        path = str(tmp_path / 'review.jsonl')
        records = [new_record(make_rule(), [new_phrase('mit license', 0.9, AUTO, AUTO)], False)]
        write_review_file(path, records)
        before = Path(path).read_bytes()

        def failing_replace(src, dst):
            raise OSError('no')

        monkeypatch.setattr(os, 'replace', failing_replace)
        with pytest.raises(OSError):
            write_review_file(path, records)

        assert Path(path).read_bytes() == before
        assert list(tmp_path.glob('*.tmp')) == []


class TestSpanConfidence:

    def test_matches_the_brute_force_marginal(self):
        # Feature: ml-phrase-review-cli, Property 1: the span marginal is the true marginal
        import torch

        num_tags = len(LABELS)
        length = 5
        crf = build_crf(num_tags)
        torch.manual_seed(3)
        emissions = torch.randn(1, length, num_tags).to(torch.float64)
        tags, mask, free = decode_once(crf, emissions)

        # every possible path, scored in one call
        paths = torch.tensor(list(itertools.product(range(num_tags), repeat=length)))
        probabilities = crf(
            emissions.expand(len(paths), -1, -1),
            paths,
            mask=mask.expand(len(paths), -1),
            reduction='none',
        ).detach().exp()

        for span in [(0, 0), (2, 2), (1, 3), (3, 4), (0, length - 1)]:
            start, end = span
            matching = (paths[:, start:end + 1] == tags[0, start:end + 1]).all(dim=1)
            expected = float(probabilities[matching].sum() / probabilities.sum())
            got = span_confidence(crf, emissions, tags, mask, free, span)
            assert abs(got - expected) < 1e-12
            assert 0.0 <= got <= 1.0

    def test_scoring_one_span_does_not_disturb_another(self):
        # Feature: ml-phrase-review-cli, Property 2: scoring one span does not disturb another
        import torch

        num_tags = len(LABELS)
        crf = build_crf(num_tags)
        torch.manual_seed(11)
        emissions = torch.randn(1, 6, num_tags).to(torch.float64)
        tags, mask, free = decode_once(crf, emissions)
        spans = [(0, 1), (2, 2), (4, 5)]

        forwards = [span_confidence(crf, emissions, tags, mask, free, s) for s in spans]
        backwards = [
            span_confidence(crf, emissions, tags, mask, free, s)
            for s in reversed(spans)
        ]

        assert forwards == list(reversed(backwards))

    def test_the_emissions_are_left_alone(self):
        import torch

        crf = build_crf(len(LABELS))
        emissions = torch.randn(1, 4, len(LABELS)).to(torch.float64)
        original = emissions.clone()
        tags, mask, free = decode_once(crf, emissions)

        span_confidence(crf, emissions, tags, mask, free, (1, 2))

        assert torch.equal(emissions, original)

    def test_large_negative_emissions_do_not_give_nan(self):
        import torch

        crf = build_crf(len(LABELS))
        emissions = torch.full((1, 4, len(LABELS)), -1e4, dtype=torch.float64)
        tags, mask, free = decode_once(crf, emissions)

        confidence = span_confidence(crf, emissions, tags, mask, free, (0, 3))

        assert confidence == confidence
        assert 0.0 <= confidence <= 1.0


class TestCheckThresholds:

    def test_the_defaults_are_fine(self):
        check_thresholds(0.95, 0.60)

    def test_review_above_auto_is_refused(self):
        with pytest.raises(click.ClickException):
            check_thresholds(0.5, 0.9)

    @pytest.mark.parametrize('auto, review', [(1.5, 0.6), (0.95, -0.1)])
    def test_out_of_range_is_refused(self, auto, review):
        with pytest.raises(click.ClickException):
            check_thresholds(auto, review)


class TestTierFor:

    @pytest.mark.parametrize('confidence, expected', [
        (1.0, (AUTO, AUTO)),
        (0.95, (AUTO, AUTO)),
        (0.9499, (REVIEW, PENDING)),
        (0.60, (REVIEW, PENDING)),
        (0.5999, (LOW, DROPPED)),
        (0.0, (LOW, DROPPED)),
    ])
    def test_the_boundaries(self, confidence, expected):
        assert tier_for(confidence, 0.95, 0.60) == expected


class TestTagAndScore:

    def test_one_phrase(self):
        tagger = StubTagger({3: 'B-REQ', 4: 'E-REQ'})
        scored, truncated = tag_and_score(tagger, FakeTokenizer(), 512, TEXT.split())
        assert [text for text, _ in scored] == ['MIT License']
        assert not truncated

    def test_two_phrases(self):
        tagger = StubTagger({0: 'S-REQ', 3: 'B-REQ', 4: 'E-REQ'})
        scored, _ = tag_and_score(tagger, FakeTokenizer(), 512, TEXT.split())
        assert sorted(text for text, _ in scored) == ['Granted', 'MIT License']

    def test_the_same_text_twice_is_deduped(self):
        tagger = StubTagger({0: 'S-REQ', 2: 'S-REQ'})
        scored, _ = tag_and_score(tagger, FakeTokenizer(), 512, ['MIT', 'x', 'MIT'])
        assert [text for text, _ in scored] == ['MIT']

    def test_a_span_cut_by_truncation_is_dropped(self):
        tagger = StubTagger({2: 'B-REQ', 3: 'I-REQ'})
        scored, truncated = tag_and_score(tagger, FakeTokenizer(), 5, TEXT.split())
        assert scored == []
        assert truncated

    def test_nothing_tagged(self):
        tagger = StubTagger({})
        assert tag_and_score(tagger, FakeTokenizer(), 512, TEXT.split()) == ([], False)

    def test_no_words_never_reaches_the_backbone(self):
        class Exploding(StubTagger):
            def emissions(self, input_ids, attention_mask):
                raise AssertionError('there is nothing to tag')

        assert tag_and_score(Exploding({}), FakeTokenizer(), 512, []) == ([], False)


class TestIsInjectable:

    def test_a_good_phrase(self):
        counts = new_predict_counts()
        assert is_injectable(make_rule(), 'MIT License', counts)
        assert counts['rejected'] == 0 and counts['not_found'] == 0

    def test_is_good_refuses_a_short_phrase(self):
        counts = new_predict_counts()
        assert not is_injectable(make_rule(), 'is', counts)
        assert counts['rejected'] == 1

    def test_is_good_refuses_text_with_no_tokens(self):
        # find_phrase_spans_in_text would raise on this, is_good has to run first
        counts = new_predict_counts()
        assert not is_injectable(make_rule(), '///', counts)
        assert counts['rejected'] == 1
        assert counts['not_found'] == 0

    def test_a_phrase_that_is_not_in_the_rule(self):
        counts = new_predict_counts()
        assert not is_injectable(make_rule(), 'Apache License', counts)
        assert counts['not_found'] == 1


class TestPreviewInjection:

    @pytest.mark.parametrize('text, phrase, expected', [
        (
            'Granted under the MIT License to do things',
            'MIT License',
            'Granted under the {{MIT License}} to do things',
        ),
        (
            # marked at both places, which a one span preview would miss
            'The MIT License applies. See the MIT License text.',
            'MIT License',
            'The {{MIT License}} applies. See the {{MIT License}} text.',
        ),
    ])
    def test_the_preview_is_what_apply_writes(self, tmp_path, monkeypatch, text, phrase, expected):
        # Feature: ml-phrase-review-cli, Property 4: the preview is what apply writes
        use_tmp_rules(monkeypatch, tmp_path)
        rule = write_rule(tmp_path, text=text)

        changed, preview = preview_injection(rule, phrase)
        assert changed
        assert preview == expected
        # and the rule object is as it was
        assert rule.text == text
        assert rule.source is None

        # what really gets written matches
        from licensedcode.required_phrases import add_required_phrase_to_rule
        fresh = review_ml_phrases.load_rule('mit_1.RULE')
        add_required_phrase_to_rule(fresh, phrase, source='ml_model', dry_run=False)
        assert review_ml_phrases.load_rule('mit_1.RULE').text == preview

    def test_a_phrase_that_cannot_be_marked(self, tmp_path, monkeypatch):
        use_tmp_rules(monkeypatch, tmp_path)
        rule = write_rule(tmp_path)
        changed, preview = preview_injection(rule, 'Apache License')
        assert not changed
        assert preview == rule.text

    def test_a_missing_rule_file(self, tmp_path, monkeypatch):
        use_tmp_rules(monkeypatch, tmp_path)
        assert review_ml_phrases.load_rule('gone_1.RULE') is None


def run_predict(monkeypatch, tmp_path, tagger, rules, *extra):
    """Drive predict with a stubbed model and a fixed set of rules"""
    monkeypatch.setattr(
        review_ml_phrases, 'load_model',
        lambda model, hf_token=None: (tagger, FakeTokenizer(), 512),
    )
    monkeypatch.setattr(
        review_ml_phrases, 'select_rules',
        lambda license_expression=None: {'mit': rules},
    )
    path = str(tmp_path / 'review.jsonl')
    result = CliRunner().invoke(cli, [
        'predict', '--model', 'stub', '--review-file', path,
    ] + list(extra))
    return result, path


class TestPredict:

    def test_writes_a_record_per_rule_with_phrases(self, tmp_path, monkeypatch):
        tagger = StubTagger({3: 'B-REQ', 4: 'E-REQ'})
        rules = [make_rule(identifier='mit_1.RULE'), make_rule(identifier='mit_2.RULE')]
        result, path = run_predict(monkeypatch, tmp_path, tagger, rules)

        assert result.exit_code == 0
        records = read_review_file(path)
        assert [record['identifier'] for record in records] == ['mit_1.RULE', 'mit_2.RULE']
        assert records[0]['phrases'][0]['text'] == 'MIT License'
        assert records[0]['phrases'][0]['decision'] == AUTO

    def test_a_rule_with_nothing_to_file_gets_no_record(self, tmp_path, monkeypatch):
        result, path = run_predict(
            monkeypatch, tmp_path, StubTagger({}), [make_rule()],
        )
        assert result.exit_code == 0
        assert read_review_file(path) == []

    def test_the_tiers_follow_the_thresholds(self, tmp_path, monkeypatch):
        tagger = StubTagger({3: 'B-REQ', 4: 'E-REQ'})
        # every confidence lands under an auto threshold of 1.0
        result, path = run_predict(
            monkeypatch, tmp_path, tagger, [make_rule()], '--auto-threshold', '1.0',
        )
        assert result.exit_code == 0
        phrase = read_review_file(path)[0]['phrases'][0]
        assert phrase['tier'] == REVIEW
        assert phrase['decision'] == PENDING

    def test_limit_stops_early(self, tmp_path, monkeypatch):
        tagger = StubTagger({3: 'B-REQ', 4: 'E-REQ'})
        rules = [make_rule(identifier=f'mit_{n}.RULE') for n in range(5)]
        result, path = run_predict(monkeypatch, tmp_path, tagger, rules, '--limit', '2')

        assert result.exit_code == 0
        assert len(read_review_file(path)) == 2

    def test_the_counts_add_up(self, tmp_path, monkeypatch):
        # Feature: ml-phrase-review-cli, Property 6: predict counts conserve
        # one phrase is good, one is a single short token is_good will refuse
        tagger = StubTagger({3: 'B-REQ', 4: 'E-REQ', 0: 'S-REQ'})
        result, path = run_predict(monkeypatch, tmp_path, tagger, [make_rule()])

        filed = sum(len(record['phrases']) for record in read_review_file(path))
        rejected = int(result.output.split('rejected       : ')[1].split('\n')[0])
        not_found = int(result.output.split('not found      : ')[1].split('\n')[0])
        assert filed + rejected + not_found == 2

    def test_the_histogram_is_left_out_when_nothing_was_filed(self, tmp_path, monkeypatch):
        result, _ = run_predict(monkeypatch, tmp_path, StubTagger({}), [make_rule()])
        assert 'confidence spread' not in result.output

    def test_a_review_file_that_exists_is_refused(self, tmp_path, monkeypatch):
        def exploding_load(model, hf_token=None):
            raise AssertionError('the model must not be loaded')

        monkeypatch.setattr(review_ml_phrases, 'load_model', exploding_load)
        path = tmp_path / 'review.jsonl'
        path.write_text('keep me\n', encoding='utf-8')

        result = CliRunner().invoke(cli, [
            'predict', '--model', 'stub', '--review-file', str(path),
        ])

        assert result.exit_code != 0
        assert path.read_text(encoding='utf-8') == 'keep me\n'

    def test_bad_thresholds_never_load_the_model(self, tmp_path, monkeypatch):
        def exploding_load(model, hf_token=None):
            raise AssertionError('the model must not be loaded')

        monkeypatch.setattr(review_ml_phrases, 'load_model', exploding_load)
        path = tmp_path / 'review.jsonl'

        result = CliRunner().invoke(cli, [
            'predict', '--model', 'stub', '--review-file', str(path),
            '--review-threshold', '0.99',
        ])

        assert result.exit_code != 0
        assert not path.exists()

    def test_a_missing_ml_dependency_is_reported(self, tmp_path, monkeypatch):
        def no_safetensors(model, hf_token=None):
            raise ImportError('No module named safetensors')

        monkeypatch.setattr(review_ml_phrases, 'load_model', no_safetensors)
        result = CliRunner().invoke(cli, [
            'predict', '--model', 'stub',
            '--review-file', str(tmp_path / 'review.jsonl'),
        ])

        assert result.exit_code != 0
        assert 'safetensors' in result.output
        assert 'requirements-ml.txt' in result.output


def run_review(path, keys):
    return CliRunner().invoke(cli, ['review', '--review-file', path], input=keys)


class TestReview:

    def two_pending(self, tmp_path):
        return make_review_file(tmp_path, [
            new_phrase('MIT License', 0.82, REVIEW, PENDING),
            new_phrase('do things', 0.71, REVIEW, PENDING),
        ])

    def test_approving_and_rejecting(self, tmp_path, monkeypatch):
        use_tmp_rules(monkeypatch, tmp_path)
        path = self.two_pending(tmp_path)

        result = run_review(path, 'y\nn\n')

        assert result.exit_code == 0
        assert decisions(path) == [('MIT License', APPROVED), ('do things', REJECTED)]

    def test_the_diff_and_the_rule_are_shown(self, tmp_path, monkeypatch):
        use_tmp_rules(monkeypatch, tmp_path)
        path = self.two_pending(tmp_path)

        result = run_review(path, 'y\ny\n')

        assert 'mit_1.RULE  mit' in result.output
        assert '+Granted under the {{MIT License}} to do things' in result.output
        assert '82%' in result.output

    def test_an_unknown_key_asks_again(self, tmp_path, monkeypatch):
        use_tmp_rules(monkeypatch, tmp_path)
        path = self.two_pending(tmp_path)

        result = run_review(path, 'x\ny\ny\n')

        assert 'answer y, n, e or q' in result.output
        assert decisions(path) == [('MIT License', APPROVED), ('do things', APPROVED)]

    def test_quitting_leaves_the_rest_pending(self, tmp_path, monkeypatch):
        use_tmp_rules(monkeypatch, tmp_path)
        path = self.two_pending(tmp_path)

        result = run_review(path, 'y\nq\n')

        assert result.exit_code == 0
        assert decisions(path) == [('MIT License', APPROVED), ('do things', PENDING)]

    def test_a_rerun_carries_on_where_it_stopped(self, tmp_path, monkeypatch):
        use_tmp_rules(monkeypatch, tmp_path)
        path = self.two_pending(tmp_path)
        run_review(path, 'y\nq\n')

        result = run_review(path, 'n\n')

        assert '1 phrases waiting' in result.output
        assert decisions(path) == [('MIT License', APPROVED), ('do things', REJECTED)]

    def test_nothing_pending(self, tmp_path, monkeypatch):
        use_tmp_rules(monkeypatch, tmp_path)
        path = make_review_file(tmp_path, [new_phrase('MIT License', 0.98, AUTO, AUTO)])

        result = run_review(path, '')

        assert result.exit_code == 0
        assert 'nothing left to review' in result.output

    def test_a_stale_record_is_skipped(self, tmp_path, monkeypatch):
        use_tmp_rules(monkeypatch, tmp_path)
        path = self.two_pending(tmp_path)
        os.unlink(str(tmp_path / 'mit_1.RULE'))

        result = run_review(path, '')

        assert result.exit_code == 0
        assert 'stale rules    : 1' in result.output
        assert decisions(path) == [('MIT License', PENDING), ('do things', PENDING)]

    def test_a_phrase_that_cannot_be_marked_is_not_asked_about(self, tmp_path, monkeypatch):
        use_tmp_rules(monkeypatch, tmp_path)
        path = make_review_file(tmp_path, [new_phrase('Apache License', 0.8, REVIEW, PENDING)])

        result = run_review(path, '')

        assert 'nothing to add : 1' in result.output
        assert decisions(path) == [('Apache License', PENDING)]

    def test_an_accepted_edit(self, tmp_path, monkeypatch):
        use_tmp_rules(monkeypatch, tmp_path)
        path = make_review_file(tmp_path, [new_phrase('MIT License', 0.82, REVIEW, PENDING)])

        result = run_review(path, 'e\nMIT License to\n')

        assert result.exit_code == 0
        phrase = read_review_file(path)[0]['phrases'][0]
        assert phrase['text'] == 'MIT License to'
        assert phrase['predicted_text'] == 'MIT License'
        assert phrase['confidence'] == 0.82
        assert phrase['decision'] == APPROVED
        assert 'edited       : 1' in result.output

    def test_an_edit_refused_by_is_good(self, tmp_path, monkeypatch):
        use_tmp_rules(monkeypatch, tmp_path)
        path = make_review_file(tmp_path, [new_phrase('MIT License', 0.82, REVIEW, PENDING)])

        result = run_review(path, 'e\nis\n\ny\n')

        assert 'is_good refused it' in result.output
        assert decisions(path) == [('MIT License', APPROVED)]

    def test_an_edit_that_is_not_in_the_rule(self, tmp_path, monkeypatch):
        use_tmp_rules(monkeypatch, tmp_path)
        path = make_review_file(tmp_path, [new_phrase('MIT License', 0.82, REVIEW, PENDING)])

        result = run_review(path, 'e\nApache License\n\nn\n')

        assert 'not found in the rule text' in result.output
        assert decisions(path) == [('MIT License', REJECTED)]

    def test_an_empty_edit_goes_back_to_the_keys(self, tmp_path, monkeypatch):
        use_tmp_rules(monkeypatch, tmp_path)
        path = make_review_file(tmp_path, [new_phrase('MIT License', 0.82, REVIEW, PENDING)])

        result = run_review(path, 'e\n\ny\n')

        phrase = read_review_file(path)[0]['phrases'][0]
        assert phrase['text'] == 'MIT License'
        assert phrase['decision'] == APPROVED
        assert 'edited       : 0' in result.output


def run_apply(path, *extra):
    return CliRunner().invoke(cli, ['apply', '--review-file', path] + list(extra))


class TestApply:

    def test_dry_run_writes_nothing(self, tmp_path, monkeypatch):
        # Feature: ml-phrase-review-cli, Property 7: nothing is written under dry-run
        use_tmp_rules(monkeypatch, tmp_path)
        path = make_review_file(tmp_path, [new_phrase('MIT License', 0.98, AUTO, AUTO)])
        before = rule_digests(tmp_path)

        result = run_apply(path, '--dry-run')

        assert result.exit_code == 0
        assert rule_digests(tmp_path) == before
        assert 'dry run, no rules were saved' in result.output

    def test_a_real_write_marks_the_rule(self, tmp_path, monkeypatch):
        use_tmp_rules(monkeypatch, tmp_path)
        path = make_review_file(tmp_path, [new_phrase('MIT License', 0.98, AUTO, AUTO)])

        result = run_apply(path)

        assert result.exit_code == 0
        marked = review_ml_phrases.load_rule('mit_1.RULE')
        assert '{{MIT License}}' in marked.text
        assert marked.source == 'ml_model'
        assert 'scancode-reindex-licenses' in result.output

    def test_running_it_twice_changes_nothing(self, tmp_path, monkeypatch):
        # Feature: ml-phrase-review-cli, Property 5: apply is idempotent
        use_tmp_rules(monkeypatch, tmp_path)
        path = make_review_file(tmp_path, [new_phrase('MIT License', 0.98, AUTO, AUTO)])
        run_apply(path)
        after_first = rule_digests(tmp_path)

        result = run_apply(path)

        assert rule_digests(tmp_path) == after_first
        assert 'phrases injected : 0' in result.output

    def test_only_approved_and_auto_go_in(self, tmp_path, monkeypatch):
        use_tmp_rules(monkeypatch, tmp_path)
        path = make_review_file(tmp_path, [
            new_phrase('MIT License', 0.98, AUTO, AUTO),
            new_phrase('do things', 0.80, REVIEW, APPROVED),
            new_phrase('with this software', 0.75, REVIEW, REJECTED),
            new_phrase('under the', 0.70, REVIEW, PENDING),
        ])

        run_apply(path)

        text = review_ml_phrases.load_rule('mit_1.RULE').text
        assert '{{MIT License}}' in text
        assert '{{do things}}' in text
        assert '{{with this software}}' not in text

    def test_nothing_accepted(self, tmp_path, monkeypatch):
        use_tmp_rules(monkeypatch, tmp_path)
        path = make_review_file(tmp_path, [new_phrase('MIT License', 0.4, LOW, DROPPED)])
        before = rule_digests(tmp_path)

        result = run_apply(path)

        assert result.exit_code == 0
        assert 'nothing accepted to apply' in result.output
        assert rule_digests(tmp_path) == before

    def test_a_stale_record_is_counted(self, tmp_path, monkeypatch):
        use_tmp_rules(monkeypatch, tmp_path)
        path = make_review_file(tmp_path, [new_phrase('MIT License', 0.98, AUTO, AUTO)])
        os.unlink(str(tmp_path / 'mit_1.RULE'))

        result = run_apply(path)

        assert result.exit_code == 0
        assert 'stale rules      : 1' in result.output

    def test_a_rule_that_already_has_a_marker_takes_the_next_phrase(self, tmp_path, monkeypatch):
        use_tmp_rules(monkeypatch, tmp_path)
        path = make_review_file(tmp_path, [new_phrase('MIT License', 0.98, AUTO, AUTO)])
        run_apply(path)

        # a second review file for the same rule, which now carries a marker
        second = str(tmp_path / 'second.jsonl')
        write_review_file(second, [new_record(
            review_ml_phrases.load_rule('mit_1.RULE'),
            [new_phrase('do things', 0.80, REVIEW, APPROVED)],
            False,
        )])
        run_apply(second)

        text = review_ml_phrases.load_rule('mit_1.RULE').text
        assert '{{MIT License}}' in text
        assert '{{do things}}' in text

    def test_the_phrases_go_in_longest_first(self):
        record = new_record(make_rule(), [
            new_phrase('MIT', 0.9, AUTO, AUTO),
            new_phrase('MIT License', 0.9, REVIEW, APPROVED),
            new_phrase('skipped', 0.9, REVIEW, REJECTED),
        ], False)
        assert accepted_phrases(record) == ['MIT License', 'MIT']
