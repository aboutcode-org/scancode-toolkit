# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from array import array
from collections import Counter
from collections import defaultdict
from functools import partial
from operator import itemgetter
import os
import sys
from time import time

from intbitset import intbitset

from licensedcode import SMALL_RULE
from licensedcode import TINY_RULE
from licensedcode.legalese import common_license_words
from licensedcode import match
from licensedcode import match_aho
from licensedcode import match_hash
from licensedcode import match_seq
from licensedcode import match_set
from licensedcode import match_spdx_lid
from licensedcode import match_unknown
from licensedcode.dmp import match_blocks as match_blocks_dmp
from licensedcode.seq import match_blocks as match_blocks_seq
from licensedcode import query
from licensedcode import tokenize
from licensedcode.spans import Span

"""
Main license index construction, query processing and matching entry points for
license detection.

The LicenseIndex is the main class and holds the index structures. The `match`
method drives the matching using a succession of matching strategies. Actual
matching is delegated to other modules that implement a matching strategy.
"""

# Tracing flags
TRACE = False or os.environ.get('SCANCODE_DEBUG_LICENSE', False)
TRACE_APPROX = False
TRACE_APPROX_CANDIDATES = False
TRACE_APPROX_MATCHES = False
TRACE_INDEXING = False or os.environ.get('SCANCODE_DEBUG_LICENSE_INDEX', False)
TRACE_INDEXING_PERF = False
TRACE_TOKEN_DOC_FREQ = False
TRACE_SPDX_LID = False


def logger_debug(*args):
    pass


if (
    TRACE
    or TRACE_APPROX
    or TRACE_APPROX_CANDIDATES
    or TRACE_APPROX_MATCHES
    or TRACE_INDEXING
    or TRACE_INDEXING_PERF
    or TRACE_SPDX_LID
):

    use_print = True

    if use_print:
        printer = print
    else:
        import logging

        logger = logging.getLogger(__name__)
        # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
        logging.basicConfig(stream=sys.stdout)
        logger.setLevel(logging.DEBUG)
        printer = logger.debug

    def logger_debug(*args):
        return printer(' '.join(isinstance(a, str) and a or repr(a)
                                     for a in args))

############################## Feature SWITCHES ################################
########## Ngram fragments detection
USE_AHO_FRAGMENTS = False
# length of ngrams used for fragments detection
AHO_FRAGMENTS_NGRAM_LEN = 6

########## Query run breaking using rule starts
# Feature switch to enable or not extra query run breaking based on rule starts
USE_RULE_STARTS = False

########## Use Bigrams instead of tokens
# Enable using an bigrams for multisets/bags instead of tokens
USE_BIGRAM_MULTISETS = False

########## Use diff match patch myers diff for approx matching
# Enable using an bigrams for multisets/bags instead of tokens
USE_DMP = False

############################## Feature SWITCHES ################################

# Maximum number of unique tokens we can handle: 16 bits signed integers are up
# to 32767. Since we use internally several arrays of ints for smaller and
# optimized storage we cannot exceed this number of tokens.
MAX_TOKENS = (2 ** 15) - 1


class DuplicateRuleError(Exception):
    pass


class LicenseIndex(object):
    """
    A license detection index. An index is queried for license matches found in
    a query file. The index support multiple strategies for finding exact and
    approximate matches.
    """
    # slots are not really needed but they help with sanity and avoid an
    # unchecked proliferation of new attributes
    __slots__ = (
        'len_tokens',
        'len_legalese',
        'dictionary',
        'digit_only_tids',
        'tokens_by_tid',

        'rules_by_rid',
        'tids_by_rid',

        'high_postings_by_rid',

        'sets_by_rid',
        'msets_by_rid',

        'rid_by_hash',
        'rules_automaton',
        'fragments_automaton',
        'starts_automaton',
        'unknown_automaton',

        'regular_rids',
        'false_positive_rids',
        'approx_matchable_rids',

        'optimized',
        'all_languages',
    )

    def __init__(
        self,
        rules=None,
        _legalese=common_license_words,
        _spdx_tokens=frozenset(),
        _license_tokens=frozenset(),
        _all_languages=False,
    ):
        """
        Initialize the index with an iterable of Rule objects.
        ``_legalese`` is a sorted mapping of common license-specific words aka. legalese as {token: id}
        ``_spdx_tokens`` is a set of tokens used in SPDX license identifiers
        ``_license_tokens`` is a set of "license" tokens used as start or end of a rule
        If ``_all_languages`` is True, use all spoken languages license and rules.
        Otherwise, use only English rules and licenses.
        """
        # total number of unique known tokens
        self.len_tokens = 0

        # largest token ID for a "legalese" token. A token with a larger id than
        # len_legalese is considered a "junk" very common token
        self.len_legalese = 0

        # mapping of token string > token id
        self.dictionary = {}

        # set of token ids made entirely of digits
        self.digit_only_tids = set()

        # mapping-like of token id -> token string as a list where the index is the
        # token id and the value the actual token string.
        # This the reverse of the dictionary.
        self.tokens_by_tid = []

        # Note: all the following are mappings-like (using lists) of
        # rid-> data are lists of data where the index is the rule id.

        # maping-like of rule_id -> rule objects proper
        self.rules_by_rid = []

        # maping-like of rule_id -> sequence of token_ids
        self.tids_by_rid = []

        # mapping-like of rule id->(mapping of (token_id->[positions, ...])
        # We track only high/good tokens there. This is a "traditional"
        # inverted index postings list
        self.high_postings_by_rid = []

        # mapping-like of rule_id -> tokens ids sets/multisets
        self.sets_by_rid = []
        self.msets_by_rid = []

        # mapping of hash -> single rid for hash match: duplicated rules are not allowed
        self.rid_by_hash = {}

        # Aho-Corasick automatons for regular rules and experimental fragments
        self.rules_automaton = match_aho.get_automaton()
        self.fragments_automaton = USE_AHO_FRAGMENTS and match_aho.get_automaton()
        self.starts_automaton = USE_RULE_STARTS and match_aho.get_automaton()
        self.unknown_automaton = match_unknown.get_automaton()

        # disjunctive sets of rule ids: regular and false positive

        # TODO: consider using intbitset instead
        self.regular_rids = set()
        self.false_positive_rids = set()

        # These rule ids are for rules that can be matched with a sequence
        # match. Other rules can only be matched exactly
        self.approx_matchable_rids = set()

        # if True the index has been optimized and becomes read only:
        # no new rules can be added
        self.optimized = False

        # For info only, set to True when the rules used to build this index are
        # in all languages as opposed to be only in English.
        self.all_languages = _all_languages

        if rules:
            if TRACE_INDEXING_PERF:
                start = time()
                logger_debug('LicenseIndex: building index.')
            # index all and optimize
            self._add_rules(
                rules,
                _legalese=_legalese,
                _spdx_tokens=_spdx_tokens,
                _license_tokens=_license_tokens,
            )

            if TRACE_TOKEN_DOC_FREQ:
                logger_debug('LicenseIndex: token, frequency')
                from itertools import chain
                tf = Counter(chain.from_iterable(tids for rid, tids
                        in enumerate(self.tids_by_rid)
                        if rid in self.regular_rids))

            if TRACE_INDEXING_PERF:
                duration = time() - start
                len_rules = len(self.rules_by_rid)
                logger_debug('LicenseIndex: built index with %(len_rules)d rules in '
                      '%(duration)f seconds.' % locals())
                self._print_index_stats()

    def _add_rules(
        self,
        rules,
        _legalese=common_license_words,
        _spdx_tokens=frozenset(),
        _license_tokens=frozenset(),
    ):
        """
        Add a list of Rule objects to the index and constructs optimized and
        immutable index structures.

        ``_legalese`` is a sorted mapping of common license-specific words aka. legalese as {token: id}
        ``_spdx_tokens`` is a set of token strings used in SPDX license identifiers
        ``_license_tokens`` is a set of "license" tokens used as start or end of a rule
        """
        if self.optimized:
            raise Exception('Index has been optimized and cannot be updated.')

        # initial dictionary mapping for known legalese tokens
        ########################################################################

        # FIXME: we should start enumerating at 1 below: token ids then become
        # valid "unichr" values, making it easier downstream when used in
        # automatons

        self.dictionary = dictionary = dict(_legalese)
        dictionary_get = dictionary.get

        self.len_legalese = len_legalese = len(dictionary)
        highest_tid = len_legalese - 1

        # Add SPDX key tokens to the dictionary: these are always treated as
        # non-legalese. This may seem weird but they are detected in expressions
        # alright and some of their tokens exist as rules too (e.g. GPL).
        # Treating their words as legalese by default creates problems as common
        # words such as mit may become legalese words even though we do not want
        # this to happen.
        ########################################################################
        for sts in sorted(_spdx_tokens):
            stid = dictionary_get(sts)
            if stid is None:
                # we have a never yet seen token, so we assign a new tokenid
                highest_tid += 1
                stid = highest_tid
                dictionary[sts] = stid

        self.rules_by_rid = rules_by_rid = list(rules)
        if TRACE_INDEXING:
            for _rid, _rule in enumerate(rules_by_rid):
                logger_debug('rules_by_rid:', _rid, _rule)

        # ensure that rules are sorted
        rules_by_rid.sort()
        len_rules = len(rules_by_rid)

        # create index data structures
        # OPTIMIZATION: bind frequently used methods to the local scope for
        # index structures
        ########################################################################
        tids_by_rid_append = self.tids_by_rid.append

        false_positive_rids_add = self.false_positive_rids.add
        regular_rids_add = self.regular_rids.add
        approx_matchable_rids_add = self.approx_matchable_rids.add

        # since we only use these for regular rules, these lists may be sparse.
        # their index is the rule rid
        self.high_postings_by_rid = high_postings_by_rid = [None] * len_rules
        self.sets_by_rid = sets_by_rid = [None] * len_rules
        self.msets_by_rid = msets_by_rid = [None] * len_rules

        # track all duplicate rules: fail and report dupes at once at the end
        dupe_rules_by_hash = defaultdict(list)

        # create a set of known "license" words used to determine if a rule
        # starts or ends with a "license" word/token
        ########################################################################
        license_tokens = set()
        for t in _license_tokens:
            tid = dictionary_get(t)
            if tid is not None:
                license_tokens.add(tid)

        rules_automaton_add = partial(match_aho.add_sequence,
            automaton=self.rules_automaton, with_duplicates=False)

        if USE_AHO_FRAGMENTS:
            fragments_automaton_add = partial(
                match_aho.add_sequence,
                automaton=self.fragments_automaton,
                with_duplicates=True,
            )

        if USE_RULE_STARTS:
            starts_automaton_add_start = partial(
                match_aho.add_start,
                automaton=self.starts_automaton,
            )

        # OPTIMIZED: bind frequently used objects to local scope
        rid_by_hash = self.rid_by_hash
        match_hash_index_hash = match_hash.index_hash
        match_set_tids_set_counter = match_set.tids_set_counter
        match_set_multiset_counter = match_set.multiset_counter

        len_starts = SMALL_RULE
        min_len_starts = SMALL_RULE * 6

        ngram_len = AHO_FRAGMENTS_NGRAM_LEN

        # Index each rule
        ########################################################################
        for rid, rule in enumerate(rules_by_rid):

            # assign rid
            rule.rid = rid

            rule_token_ids = array('h', [])
            tids_by_rid_append(rule_token_ids)
            rule_token_ids_append = rule_token_ids.append

            rule_tokens = []
            rule_tokens_append = rule_tokens.append

            # A rule is weak if it does not contain at least one legalese word:
            # we consider all rules to be weak until proven otherwise below.
            # "weak" rules can only be matched with an automaton exactly.
            is_weak = True

            for rts in rule.tokens():
                rule_tokens_append(rts)
                rtid = dictionary_get(rts)
                if rtid is None:
                    # we have a never yet seen token, so we assign a new tokenid
                    # note: we could use the length of the dictionary instead
                    highest_tid += 1
                    rtid = highest_tid
                    dictionary[rts] = rtid
                if is_weak and rtid < len_legalese:
                    is_weak = False

                try:
                    rule_token_ids_append(rtid)
                except Exception as e:
                    raise Exception(rtid, rts, rule) from e

            rule_length = rule.length
            is_tiny = rule_length < TINY_RULE

            # build hashes index and check for duplicates rule texts
            rule_hash = match_hash_index_hash(rule_token_ids)
            dupe_rules_by_hash[rule_hash].append(rule)

            ####################
            # populate automaton with the whole rule tokens sequence, for all
            # RULEs, be they "standard"/regular, weak, false positive or small
            ####################
            rules_automaton_add(tids=rule_token_ids, rid=rid)

            if rule.is_false_positive:
                # False positive rules do not participate in the set or sequence
                # matching at all: they are used for exact matching and in post-
                # matching filtering
                false_positive_rids_add(rid)
                continue

            # from now on, we have regular rules
            rid_by_hash[rule_hash] = rid
            regular_rids_add(rid)

            # Does the rule starts or ends with a "license" word? We track this
            # to help disambiguate some overlapping false positive short rules
            # OPTIMIZED: the last rtid above IS the last token id
            if license_tokens:
                if rtid in license_tokens:
                    rule.ends_with_license = True
                if rule_token_ids[0] in license_tokens:
                    rule.starts_with_license = True

            # populate unknown_automaton that only makes sense for rules that
            # are also sequence matchable.
            ####################
            match_unknown.add_ngrams(
                automaton=self.unknown_automaton,
                tids=rule_token_ids,
                tokens=rule_tokens,
                len_legalese=len_legalese,
                rule_length=rule_length,
            )

            # Some rules that cannot be matched as a sequence are "weak" rules
            # or can require to be matched only as a continuous sequence of
            # tokens. This includes, tiny, is_continuous or is_license_reference
            # rules. We skip adding these to the data structures used for
            # sequence matching.
            can_match_as_sequence = not (
                is_weak
                or is_tiny
                or rule.is_continuous
                or (rule.is_small
                    and (rule.is_license_reference or rule.is_license_tag))
            )

            if can_match_as_sequence:
                approx_matchable_rids_add(rid)

                ####################
                # update high postings: positions by high tids used to
                # speed up sequence matching
                ####################
                # no postings for rules that cannot be matched as a sequence (too short and weak)
                # TODO: this could be optimized with a group_by
                postings = defaultdict(list)
                for pos, tid in enumerate(rule_token_ids):
                    if tid < len_legalese:
                        postings[tid].append(pos)
                # OPTIMIZED: for speed and memory: convert postings to arrays
                postings = {tid: array('h', value) for tid, value in postings.items()}
                high_postings_by_rid[rid] = postings

                ####################
                # ... and ngram fragments: compute ngrams and populate an automaton with ngrams
                ####################
                if (USE_AHO_FRAGMENTS
                    and rule.minimum_coverage < 100
                    and rule_length > ngram_len
                ):
                    all_ngrams = tokenize.ngrams(rule_token_ids, ngram_length=ngram_len)
                    all_ngrams_with_pos = tokenize.select_ngrams(all_ngrams, with_pos=True)
                    # all_ngrams_with_pos = enumerate(all_ngrams)
                    for pos, ngram in all_ngrams_with_pos:
                        fragments_automaton_add(tids=ngram, rid=rid, start=pos)

                ####################
                # use the start and end of this rule as a break point for query runs
                ####################
                if USE_RULE_STARTS and rule_length > min_len_starts:
                    starts_automaton_add_start(
                        tids=rule_token_ids[:len_starts],
                        rule_identifier=rule.identifier,
                        rule_length=rule_length,
                    )

            ####################
            # build sets and multisets indexes, for all regular rules as we need
            # the thresholds
            ####################
            tids_set, mset = match_set.build_set_and_mset(
                rule_token_ids, _use_bigrams=USE_BIGRAM_MULTISETS)
            sets_by_rid[rid] = tids_set
            msets_by_rid[rid] = mset

            ####################################################################
            ####################################################################
            # FIXME!!!!!!! we should store them: we need them and we recompute
            # them later at match time
            tids_set_high = match_set.high_tids_set_subset(
                tids_set, len_legalese)
            mset_high = match_set.high_multiset_subset(
                mset, len_legalese, _use_bigrams=USE_BIGRAM_MULTISETS)

            # FIXME!!!!!!!
            ####################################################################
            ####################################################################

            ####################
            # update rule thresholds
            ####################
            rule.length_unique = match_set_tids_set_counter(tids_set)
            rule.high_length_unique = match_set_tids_set_counter(tids_set_high)

            rule.high_length = match_set_multiset_counter(mset_high)
            rule.compute_thresholds()

        ########################################################################
        # Finalize index data structures
        ########################################################################
        # Create the tid -> token string lookup structure.
        ########################################################################
        self.tokens_by_tid = tokens_by_tid = [
            ts for ts, _tid in sorted(dictionary.items(), key=itemgetter(1))]
        self.len_tokens = len_tokens = len(tokens_by_tid)

        # some tokens are made entirely of digits and these can create some
        # worst case behavior when there are long runs on these
        ########################################################################
        self.digit_only_tids = intbitset([
            i for i, s in enumerate(self.tokens_by_tid) if s.isdigit()])

        # Finalize automatons
        ########################################################################
        self.rules_automaton.make_automaton()
        if USE_AHO_FRAGMENTS:
            self.fragments_automaton.make_automaton()
        if USE_RULE_STARTS:
            match_aho.finalize_starts(self.starts_automaton)
        self.unknown_automaton.make_automaton()

        ########################################################################
        # Do some sanity checks
        ########################################################################

        msg = 'Inconsistent structure lengths'
        assert len_tokens == highest_tid + 1 == len(dictionary), msg

        msg = 'Cannot support more than licensedcode.index.MAX_TOKENS: %d' % MAX_TOKENS
        assert len_tokens <= MAX_TOKENS, msg

        dupe_rule_paths = []
        for rules in dupe_rules_by_hash.values():
            if len(rules) == 1:
                continue
            drp = [rule.identifier for rule in rules]
            drp.sort()
            dupe_rule_paths.append('\n'.join(drp))

        if dupe_rule_paths:
            msg = ('Duplicate rules: \n' + '\n\n'.join(dupe_rule_paths))
            raise DuplicateRuleError(msg)

        self.optimized = True

    def debug_matches(
        self,
        matches,
        message,
        location=None,
        query_string=None,
        with_text=False,
        qry=None,
    ):
        """
        Log debug-level data for a list of `matches`.
        """
        logger_debug(message + ':', len(matches))
        if qry:
            # set line early to ease debugging
            match.set_matched_lines(matches, qry.line_by_pos)

        if not with_text:
            for m in matches:
                logger_debug(m)
        else:
            logger_debug(message + ' MATCHED TEXTS')

            from licensedcode.tracing import get_texts

            for m in matches:
                logger_debug(m)
                qt, it = get_texts(m)
                logger_debug('  MATCHED QUERY TEXT:', qt)
                logger_debug('  MATCHED RULE TEXT:', it)

    def get_spdx_id_matches(
        self,
        query,
        from_spdx_id_lines=True,
        expression_symbols=None,
        **kwargs,
    ):
        """
        Matching strategy for SPDX-Licensed-Identifier style of expressions. If
        `from_spdx_id_lines` is True detect only in the SPDX license identifier
        lines found in the query. Otherwise use the whole query for detection.

        Use the ``expression_symbols`` mapping of {lowered key: LicenseSymbol}
        if provided. Otherwise use the standard SPDX license symbols.
        """
        matches = []

        if from_spdx_id_lines:
            qrs_and_texts = query.spdx_lid_query_runs_and_text()
        else:
            # If we are not specifically looking at a single SPDX-Licene-
            # identifier line, then use the whole query run with the whole text.
            # Note this can only work for small texts or this will likely make
            # the expression parser choke if you feed it large texts
            query_lines = tokenize.query_lines(query.location, query.query_string)
            query_lines = [ln for _, ln in query_lines]
            qrs_and_texts = query.whole_query_run(), u'\n'.join(query_lines)
            qrs_and_texts = [qrs_and_texts]

        for query_run, detectable_text in qrs_and_texts:
            if not query_run.matchables:
                continue
            if TRACE_SPDX_LID:
                logger_debug(
                    'get_spdx_id_matches:',
                    'query_run:', query_run,
                    'detectable_text:', detectable_text,
                )

            spdx_match = match_spdx_lid.spdx_id_match(
                idx=self,
                query_run=query_run,
                text=detectable_text,
                expression_symbols=expression_symbols,
            )

            if spdx_match:
                query_run.subtract(spdx_match.qspan)
                matches.append(spdx_match)

        return matches

    def get_exact_matches(self, query, deadline=sys.maxsize, **kwargs):
        """
        Exact matching strategy using an automaton for multimatching many rules
        at once.
        """
        wqr = query.whole_query_run()

        matches = match_aho.exact_match(
            idx=self,
            query_run=wqr,
            automaton=self.rules_automaton,
            deadline=deadline,
        )

        matches, _discarded = match.refine_matches(
            matches=matches,
            query=query,
            filter_false_positive=False,
            merge=False,
        )
        return matches

    def get_fragments_matches(
        self,
        query,
        matched_qspans,
        deadline=sys.maxsize,
        **kwargs,
    ):
        """
        Approximate matching strategy breaking a query in query_runs and using
        fragment matching. Return a list of matches.
        """
        matches = []

        for query_run in query.query_runs:
            # we cannot do a sequence match in query run without some high token left
            if not query_run.is_matchable(include_low=False, qspans=matched_qspans):
                continue
            qrun_matches = match_aho.match_fragments(self, query_run)
            matches.extend(match.merge_matches(qrun_matches))
            # break if deadline has passed
            if time() > deadline:
                break

        return matches

    def get_approximate_matches(self, query, matched_qspans, existing_matches,
                                deadline=sys.maxsize, **kwargs):
        """
        Approximate matching strategy breaking a query in query_runs and using
        multiple local alignments (aka. diff). Return a list of matches.
        """
        matches = []
        matchable_rids = self.approx_matchable_rids

        already_matched_qspans = matched_qspans[:]

        MAX_NEAR_DUPE_CANDIDATES = 10

        # first check if the whole file may be close, near-dupe match
        whole_query_run = query.whole_query_run()
        near_dupe_candidates = match_set.compute_candidates(
            query_run=whole_query_run,
            idx=self,
            matchable_rids=matchable_rids,
            top=MAX_NEAR_DUPE_CANDIDATES,
            high_resemblance=True,
            _use_bigrams=USE_BIGRAM_MULTISETS,
        )

        # if near duplicates, we only match the whole file at once against these
        # candidates
        if near_dupe_candidates:
            if TRACE_APPROX_CANDIDATES:
                logger_debug('get_query_run_approximate_matches: near dupe candidates:')
                for rank, ((sv1, sv2), _rid, can, _inter) in enumerate(near_dupe_candidates, 1):
                    logger_debug(rank, sv1, sv2, can.identifier)

            matched = self.get_query_run_approximate_matches(
                whole_query_run, near_dupe_candidates, already_matched_qspans, deadline)

            matches.extend(matched)

            # subtract these
            for match in matched:
                qspan = match.qspan
                query.subtract(qspan)
                already_matched_qspans.append(qspan)

            # break if deadline has passed
            if time() > deadline:
                return matches

        # otherwise, and in all cases we break things in smaller query runs and
        # match each separately

        if USE_RULE_STARTS:
            query.refine_runs()

        if TRACE_APPROX:
            logger_debug('get_approximate_matches: len(query.query_runs):', len(query.query_runs))

        MAX_CANDIDATES = 70
        for query_run in query.query_runs:
            # inverted index match and ranking, query run-level
            candidates = match_set.compute_candidates(
                query_run=query_run,
                idx=self,
                matchable_rids=matchable_rids,
                top=MAX_CANDIDATES,
                high_resemblance=False,
                _use_bigrams=USE_BIGRAM_MULTISETS,
            )

            if TRACE_APPROX_CANDIDATES:
                logger_debug('get_query_run_approximate_matches: candidates:')
                for rank, ((sv1, sv2), _rid, can, _inter) in enumerate(candidates, 1):
                    logger_debug(rank, sv1, sv2, can.identifier)

            matched = self.get_query_run_approximate_matches(
                query_run, candidates, matched_qspans, deadline)

            matches.extend(matched)

            # break if deadline has passed
            if time() > deadline:
                break

        return matches

    def get_query_run_approximate_matches(
        self,
        query_run,
        candidates,
        matched_qspans,
        deadline=sys.maxsize,
        **kwargs,
    ):
        """
        Return Return a list of approximate matches for a single query run.
        """
        matches = []

        # we cannot do a sequence match in query run without some high token left
        if not query_run.is_matchable(include_low=False, qspans=matched_qspans):
            if TRACE_APPROX:
                logger_debug(
                    'get_query_run_approximate_matches: query_run not matchable:', query_run)

            return matches

        # Perform multiple sequence matching/alignment for each candidate,
        # query run-level for as long as we have more non-overlapping
        # matches returned

        for _score_vecs, rid, candidate_rule, high_intersection in candidates:
            if USE_DMP:
                # Myers diff works best when the difference are small, otherwise
                # it performs rather poorly as it is not aware of legalese
                match_blocks = match_blocks_dmp
                high_postings = None

            else:
                # we prefer to use the high tken aware seq matching only
                # when the matches are not clear. it works best when things
                # are farther apart
                match_blocks = match_blocks_seq
                high_postings = self.high_postings_by_rid[rid]
                high_postings = {
                    tid: postings for tid, postings in high_postings.items()
                        if tid in high_intersection}

            start_offset = 0
            while True:
                rule_matches = match_seq.match_sequence(
                    self, candidate_rule, query_run,
                    high_postings=high_postings,
                    start_offset=start_offset,
                    match_blocks=match_blocks,
                )

                if TRACE_APPROX_MATCHES:
                    self.debug_matches(
                        matches=rule_matches,
                        message='get_query_run_approximate_matches: rule_matches:',
                        with_text=True,
                        qry=query_run.query,
                    )

                if not rule_matches:
                    break

                matches_end = max(m.qend for m in rule_matches)
                matches.extend(rule_matches)

                if matches_end + 1 < query_run.end:
                    start_offset = matches_end + 1
                    continue
                else:
                    break

                # break if deadline has passed
                if time() > deadline:
                    break

            # break if deadline has passed
            if time() > deadline:
                break

        # FIXME: is this really needed here?
        matches = match.merge_matches(matches)

        return matches

    def match(
        self,
        location=None,
        query_string=None,
        min_score=0,
        as_expression=False,
        expression_symbols=None,
        approximate=True,
        unknown_licenses=False,
        deadline=sys.maxsize,
        _skip_hash_match=False,
        **kwargs,
    ):
        """
        This is the main entry point to match licenses.

        Return a sequence of LicenseMatch by matching the file at ``location`` or
        the ``query_string`` string against this index. Only include matches with
        scores greater or equal to ``min_score``.

        If ``as_expression`` is True, treat the whole text as a single SPDX
        license expression and use only expression matching.

        Use the ``expression_symbols`` mapping of {lowered key: LicenseSymbol}
        if provided. Otherwise use the standard SPDX license symbols mapping.

        If ``approximate`` is True, perform approximate matching as a last
        matching step. Otherwise, only do hash, exact and expression matching.

        If ``unknown_licenses`` is True, perform unknown licenses matching after
        all regular matching steps.

        ``deadline`` is a time.time() value in seconds by which the processing
        should stop and return whatever was matched so far.

        ``_skip_hash_match`` is used only for testing.
        """
        assert 0 <= min_score <= 100

        if not location and not query_string:
            return []

        qry = query.build_query(
            location=location,
            query_string=query_string,
            idx=self,
            text_line_threshold=15,
            bin_line_threshold=50,
        )

        if TRACE:
            logger_debug('Index.match: for:', location, 'query:', qry)

        if not qry:
            return []

        return self.match_query(
            qry=qry,
            min_score=min_score,
            as_expression=as_expression,
            expression_symbols=expression_symbols,
            approximate=approximate,
            unknown_licenses=unknown_licenses,
            deadline=deadline,
            _skip_hash_match=_skip_hash_match,
            **kwargs,
        )

    def match_query(
        self,
        qry,
        min_score=0,
        as_expression=False,
        expression_symbols=None,
        approximate=True,
        unknown_licenses=False,
        deadline=sys.maxsize,
        _skip_hash_match=False,
        **kwargs,
    ):
        """
        Return a sequence of LicenseMatch by matching the ``qry`` Query against
        this index. See Index.match() for arguments documentation.
        """

        whole_query_run = qry.whole_query_run()
        if not whole_query_run or not whole_query_run.matchables:
            return []

        if not _skip_hash_match:
            matches = match_hash.hash_match(self, whole_query_run)
            if matches:
                match.set_matched_lines(matches, qry.line_by_pos)
                return matches

        get_spdx_id_matches = partial(
            self.get_spdx_id_matches,
            expression_symbols=expression_symbols,
        )

        if as_expression:
            matches = get_spdx_id_matches(qry, from_spdx_id_lines=False)
            match.set_matched_lines(matches, qry.line_by_pos)
            return matches

        matches = []

        if USE_AHO_FRAGMENTS:
            approx = self.get_fragments_matches
        else:
            approx = self.get_approximate_matches

        matchers = [
            # matcher, include_low in post-matching remaining matchable check
            (self.get_exact_matches, False, 'aho'),
            (get_spdx_id_matches, True, 'spdx_lid'),
        ]

        if approximate:
            matchers += [(approx, False, 'seq'), ]

        already_matched_qspans = []
        for matcher, include_low, matcher_name in matchers:
            if TRACE:
                logger_debug()
                logger_debug('match_query: matching with matcher:', matcher_name)

            matched = matcher(
                qry,
                matched_qspans=already_matched_qspans,
                existing_matches=matches,
                deadline=deadline,
            )

            if TRACE:
                self.debug_matches(
                    matches=matched,
                    message='matched with: ' + matcher_name,
                    location=qry.location,
                    query_string=qry.query_string,
                )

            matched = match.merge_matches(matched)
            matches.extend(matched)

            # Subtract whole text matched if this is long enough
            for m in matched:
                if (m.rule.is_license_text
                    and m.rule.length > 120
                    and m.coverage() > 98
                ):
                    qry.subtract(m.qspan)

            # Check if we have some matchable left: do not match futher if we do
            # not need to collect qspans matched exactly e.g. with coverage 100%
            # this coverage check is because we have provision to match
            # fragments (unused for now).

            already_matched_qspans.extend(
                m.qspan for m in matched if m.coverage() == 100)

            if not whole_query_run.is_matchable(
                include_low=include_low,
                qspans=already_matched_qspans,
            ):
                if TRACE:
                    logger_debug('  match_query: no more matchable ... stop matching after matcher:', matcher_name)
                break

            # break if deadline has passed
            if time() > deadline:
                break

        # refining matches without filtering false positives
        matches, _discarded = match.refine_matches(
            matches=matches,
            query=qry,
            min_score=min_score,
            filter_false_positive=False,
            merge=True,
        )

        if unknown_licenses:
            good_matches, weak_matches = match.split_weak_matches(matches)
            # collect the positions that are "good matches" to exclude from
            # matching for unknown_licenses. Create a Span to check for unknown
            # based on this.
            original_qspan = Span(0, len(qry.tokens) - 1)
            good_qspans = (m.qspan for m in good_matches)
            good_qspan = Span().union(*good_qspans)

            unmatched_qspan = original_qspan.difference(good_qspan)

            # for each subspan, run unknown license detection
            unknown_matches = []
            for unspan in unmatched_qspan.subspans():
                unquery_run = query.QueryRun(
                    query=qry,
                    start=unspan.start,
                    end=unspan.end,
                )

                unknown_match = match_unknown.match_unknowns(
                    idx=self,
                    query_run=unquery_run,
                    automaton=self.unknown_automaton,
                )

                if unknown_match:
                    unknown_matches.append(unknown_match)

            unknown_matches = match.filter_invalid_contained_unknown_matches(
                unknown_matches=unknown_matches,
                good_matches=good_matches,
            )

            matches.extend(unknown_matches)
            # reinject weak matches and let refine matches keep the bests
            matches.extend(weak_matches)

        if not matches:
            return []

        if TRACE:
            logger_debug()
            self.debug_matches(
                matches=matches, message='matches before final merge',
                location=qry.location,
                query_string=qry.query_string,
                with_text=True, qry=qry)

        matches, _discarded = match.refine_matches(
            matches=matches,
            query=qry,
            min_score=min_score,
            filter_false_positive=True,
            merge=True,
        )

        matches.sort()

        if TRACE:
            self.debug_matches(
                matches=matches,
                message='final matches',
                location=qry.location,
                query_string=qry.query_string,
                with_text=True,
                qry=qry,
            )

        return matches

    def _print_index_stats(self):
        """
        Print internal Index structures stats. Used for debugging and testing.
        """
        try:
            from pympler.asizeof import asizeof as size_of
        except ImportError:
            print('Index statistics will be approximate: `pip install pympler` '
                  'for correct structure sizes')
            from sys import getsizeof as size_of

        fields = (
            'dictionary',
            'tokens_by_tid',
            'rid_by_hash',
            'rules_by_rid',
            'tids_by_rid',

            'sets_by_rid',
            'msets_by_rid',

            'regular_rids',
            'approx_matchable_rids',
            'false_positive_rids',
        )

        plen = max(map(len, fields)) + 1
        internal_structures = [s + (' ' * (plen - len(s))) for s in fields]

        print('Index statistics:')
        total_size = 0
        for struct_name in internal_structures:
            struct = getattr(self, struct_name.strip())
            try:
                print('  ', struct_name, ':', 'length    :', len(struct))
            except:
                print('  ', struct_name, ':', 'repr      :', repr(struct))
            siz = size_of(struct)
            total_size += siz
            print('  ', struct_name, ':', 'size in MB:', round(siz / (1024 * 1024), 2))
        print('    TOTAL internals in MB:', round(total_size / (1024 * 1024), 2))
        print('    TOTAL real size in MB:', round(size_of(self) / (1024 * 1024), 2))

    def _tokens2text(self, tokens):
        """
        Return a text string from a sequence of token ids.
        Used for tracing and debugging.
        """
        return u' '.join('None' if t is None else self.tokens_by_tid[t] for t in tokens)


def get_weak_rids(len_legalese, tids_by_rid, _idx):
    """
    Return a set of "weak" rule ids made entirely of junk tokens: they can only
    be matched using an automaton.
    """
    weak_rids = set()
    weak_rids_add = weak_rids.add
    for rid, tids in enumerate(tids_by_rid):
        if any(t < len_legalese for t in tids):
            continue
        weak_rids_add(rid)

    if TRACE :
        for rid in sorted(weak_rids):
            rule = _idx.rules_by_rid[rid]
            message = (
                'WARNING: Weak rule, made only of frequent junk tokens. '
                'Can only be matched exactly:',
                rule.identifier,
                u' '.join(_idx.tokens_by_tid[t] for t in tids))
            logger_debug(u' '.join(message))

    return weak_rids


def get_matched_rule_ids(matches, query_run):
    """
    Yield the subset of matched rule ids from a `matches` LicenseMatch
    sequence that are within the `query_run` query run.
    """
    qstart = query_run.start
    qend = query_run.end

    for match in matches:
        if qstart <= match.qstart and match.qend <= qend:
            yield match.rule.rid
