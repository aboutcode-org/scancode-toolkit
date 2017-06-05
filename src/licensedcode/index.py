# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import, division, print_function

from array import array
import cPickle
from collections import Counter
from collections import defaultdict
from functools import partial
from itertools import izip
from operator import itemgetter
import os
import sys
from time import time

import ahocorasick

from commoncode.dict_utils import sparsify

from licensedcode import MAX_DIST

from licensedcode.cache import get_index

from licensedcode.frequent_tokens import global_tokens_by_ranks

from licensedcode.match import get_texts
from licensedcode.match import merge_matches
from licensedcode.match import refine_matches
from licensedcode.match import set_lines

from licensedcode import match_aho
from licensedcode.match_aho import exact_match
from licensedcode.match_hash import index_hash
from licensedcode.match_hash import match_hash
from licensedcode.match_seq import match_sequence
from licensedcode.match_set import compute_candidates
from licensedcode.match_set import index_token_sets
from licensedcode.match_set import tids_multiset_counter
from licensedcode.match_set import tids_set_counter

from licensedcode import query
from licensedcode.tokenize import ngrams
from licensedcode.tokenize import select_ngrams

"""
Main license index construction, query processing and matching entry points for
license detection. Use the `get_license_matches` function to obtain matches.

The LicenseIndex is the main class and holds the index structures and the
`match` method drives the matching.  Actual matching is delegated to other
modules that implement a matching strategy.
"""

# Tracing flags
TRACE = False

TRACE_QUERY_RUN = False
TRACE_QUERY_RUN_SIMPLE = False

TRACE_MATCHES = False
TRACE_MATCHES_TEXT = False

TRACE_NEGATIVE = False
TRACE_EXACT = False

TRACE_MATCHES_DISCARD = False

TRACE_INDEXING_PERF = False
TRACE_INDEXING_CHECK = False


def logger_debug(*args):
    pass

if TRACE or TRACE_INDEXING_PERF or TRACE_QUERY_RUN_SIMPLE or os.environ.get('SCANCODE_LICENSE_DEBUG'):
    import logging

    logger = logging.getLogger(__name__)
    # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))


def get_license_matches(location=None, query_string=None, min_score=0):
    """
    Yield detected license matches in the file at `location` or the
    `query_string` string.

    `min_score` is a minimum score threshold for a license match from 0 to 100
    percent. 100 is a high confidence match and 0 a low confidence match. A
    `min_score` of 0 means all matches are returned.

    The minimum length for an approximate match is four tokens.
    Spurrious matched are always filtered.
    """
    return get_index().match(location=location, query_string=query_string, min_score=min_score)


# Feature switch to enable or not ngram fragments detection
USE_AHO_FRAGMENTS = False

# length of ngrams used for fragments detection
NGRAM_LEN = 32

# Maximum number of unique tokens we can handle: 16 bits signed integers are up to
# 32767. Since we use internally several arrays of ints for smaller and optimized
# storage we cannot exceed this number of tokens.
MAX_TOKENS = (2 ** 15) - 1

# if 4, ~ 1/4 of all tokens will be treated as junk
PROPORTION_OF_JUNK = 2


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
        'len_junk',
        'len_good',
        'dictionary',
        'tokens_by_tid',

        'rules_by_rid',
        'tids_by_rid',

        'high_postings_by_rid',

        'tids_sets_by_rid',
        'tids_msets_by_rid',

        'rid_by_hash',
        'rules_automaton',
        'negative_automaton',

        'regular_rids',
        'small_rids',
        'negative_rids',
        'false_positive_rids',

        'false_positive_rid_by_hash',
        'largest_false_positive_length',

        'optimized',
    )

    def __init__(self, rules=None, _ranked_tokens=global_tokens_by_ranks):
        """
        Initialize the index with an iterable of Rule objects.
        """
        # total number of unique known tokens
        self.len_tokens = 0

        # largest token ID for a "junk" token. A token with a smaller id than
        # len_junk is considered a "junk" very common token
        self.len_junk = 0
        # corresponding number of non-junk tokens: len_tokens = len_junk + len_good
        self.len_good = 0

        # mapping of token string > token id
        self.dictionary = {}

        # mapping of token id -> token string as a list where the index is the
        # token id and the value the actual token string
        self.tokens_by_tid = []

        # Note: all mappings of rid-> data are lists of data where the index
        # is the rule id.

        # rule objects proper
        self.rules_by_rid = []

        # token_id sequences
        self.tids_by_rid = []

        # mapping of rule id->(mapping of (token_id->[positions, ...])
        # We track only high/good tokens there. This is a "traditional"
        # positional inverted index
        self.high_postings_by_rid = []

        # mapping of rule_id -> tuple of low and high tokens ids sets/multisets
        # (low_tids_set, high_tids_set)
        self.tids_sets_by_rid = []
        # (low_tids_mset, high_tids_mset)
        self.tids_msets_by_rid = []

        # mapping of hash -> single rid : duplicated rules are not allowed
        self.rid_by_hash = {}

        # Aho-Corasick automatons for negative and small rules
        self.rules_automaton = ahocorasick.Automaton(ahocorasick.STORE_ANY)
        self.negative_automaton = ahocorasick.Automaton(ahocorasick.STORE_ANY)

        # disjunctive sets of rule ids: regular, negative, small, false positive
        self.regular_rids = set()
        self.negative_rids = set()
        self.small_rids = set()
        self.false_positive_rids = set()

        # length of the largest false_positive rule
        self.largest_false_positive_length = 0
        # mapping of hash -> rid for false positive rule tokens hashes
        self.false_positive_rid_by_hash = {}

        # if True the index has been optimized and becomes read only:
        # no new rules can be added
        self.optimized = False

        if rules:
            if TRACE_INDEXING_PERF:
                start = time()
                print('LicenseIndex: building index.')

            # index all and optimize
            self._add_rules(rules, _ranked_tokens)

            if TRACE_INDEXING_PERF:
                duration = time() - start
                len_rules = len(self.rules_by_rid)
                print('LicenseIndex: built index with %(len_rules)d rules in %(duration)f seconds.' % locals())
                self._print_index_stats()

    def _add_rules(self, rules, _ranked_tokens=global_tokens_by_ranks):
        """
        Add a list of Rule objects to the index and constructs optimized and
        immutable index structures.
        """
        if self.optimized:
            raise Exception('Index has been optimized and cannot be updated.')

        # this assigns the rule ids implicitly: this is the index in the list
        self.rules_by_rid = list(rules)

        #######################################################################
        # classify rules, collect tokens and frequencies
        #######################################################################
        # accumulate all rule tokens strings. This is used only during indexing
        token_strings_by_rid = []
        # collect the unique token strings and compute their global frequency
        # This is used only during indexing
        frequencies_by_token = Counter()

        for rid, rul in enumerate(self.rules_by_rid):
            rul_tokens = list(rul.tokens())
            token_strings_by_rid.append(rul_tokens)
            frequencies_by_token.update(rul_tokens)
            # assign the rid to the rule object for sanity
            rul.rid = rid

            # classify rules and build disjuncted sets of rids
            rul_len = rul.length
            if rul.false_positive:
                # false positive rules do not participate in the matches at all
                # they are used only in post-matching filtering
                self.false_positive_rids.add(rid)
                if rul_len > self.largest_false_positive_length:
                    self.largest_false_positive_length = rul_len
            elif rul.negative():
                # negative rules are matched early and their exactly matched
                # tokens are removed from the token stream
                self.negative_rids.add(rid)
            elif rul.small():
                # small rules are best matched with a specialized approach
                self.small_rids.add(rid)
            else:
                # regular rules are matched using a common approach
                self.regular_rids.add(rid)

        # Create the tokens lookup structure at once. Note that tokens ids are
        # assigned randomly here at first by unzipping: we get the frequencies
        # and tokens->id at once this way
        tokens_by_tid, frequencies_by_tid = izip(*frequencies_by_token.items())
        self.tokens_by_tid = tokens_by_tid
        self.len_tokens = len_tokens = len(tokens_by_tid)
        assert len_tokens <= MAX_TOKENS, 'Cannot support more than licensedcode.index.MAX_TOKENS: %d' % MAX_TOKENS

        # initial dictionary mapping to old/random token ids
        self.dictionary = dictionary = {ts: tid for tid, ts in enumerate(tokens_by_tid)}
        sparsify(dictionary)

        # replace token strings with arbitrary (and temporary) random integer ids
        self.tids_by_rid = [[dictionary[tok] for tok in rule_tok] for rule_tok in token_strings_by_rid]

        #######################################################################
        # renumber token ids based on frequencies and common words
        #######################################################################
        renumbered = self.renumber_token_ids(frequencies_by_tid, _ranked_tokens)
        self.len_junk, self.dictionary, self.tokens_by_tid, self.tids_by_rid = renumbered
        len_junk, dictionary, tokens_by_tid, tids_by_rid = renumbered
        self.len_good = len_good = len_tokens - len_junk

        #######################################################################
        # build index structures
        #######################################################################

        len_rules = len(self.rules_by_rid)

        # since we only use these for regular rules, these lists may be sparse
        # their index is the rule rid
        self.high_postings_by_rid = [None for _ in range(len_rules)]
        self.tids_sets_by_rid = [None for _ in range(len_rules)]
        self.tids_msets_by_rid = [None for _ in range(len_rules)]

        # track all duplicate rules: fail and report dupes at once at the end
        dupe_rules_by_hash = defaultdict(list)

        # build closures for methods that populate automatons
        negative_automaton_add = partial(match_aho.add_sequence, automaton=self.negative_automaton)
        rules_automaton_add = partial(match_aho.add_sequence, automaton=self.rules_automaton)

        # build by-rule index structures over the token ids seq of each rule
        for rid, rule_token_ids in enumerate(tids_by_rid):
            rule = self.rules_by_rid[rid]

            # build hashes index and check for duplicates rule texts
            rule_hash = index_hash(rule_token_ids)
            dupe_rules_by_hash[rule_hash].append(rule)

            if rule.false_positive:
                # FP rules are not used for any matching
                # there is nothing else for these rules
                self.false_positive_rid_by_hash[rule_hash] = rid
            else:
                # negative, small and regular

                # update hashes index
                self.rid_by_hash[rule_hash] = rid

                # update high postings index: positions by high tids
                # TODO: this could be optimized with a group_by
                postings = defaultdict(list)
                for pos, tid in enumerate(rule_token_ids):
                    if tid >= len_junk:
                        postings[tid].append(pos)
                # OPTIMIZED: for speed and memory: convert postings to arrays
                postings = {tid: array('h', value) for tid, value in postings.items()}
                # OPTIMIZED: for speed, sparsify dict
                sparsify(postings)
                self.high_postings_by_rid[rid] = postings

                # build high and low tids sets and multisets
                rlow_set, rhigh_set, rlow_mset, rhigh_mset = index_token_sets(rule_token_ids, len_junk, len_good)
                self.tids_sets_by_rid[rid] = rlow_set, rhigh_set
                self.tids_msets_by_rid[rid] = rlow_mset, rhigh_mset

                # populate automatons...
                if rule.negative():
                    # ... with only the whole rule tokens sequence
                    negative_automaton_add(tids=rule_token_ids, rid=rid)
                else:
                    # ... or with the whole rule tokens sequence
                    rules_automaton_add(tids=rule_token_ids, rid=rid)
                    # ... and ngrams: compute ngrams and populate the automaton with ngrams
                    if USE_AHO_FRAGMENTS and rule.minimum_coverage < 100 and len(rule_token_ids) > NGRAM_LEN:
                        all_ngrams = ngrams(rule_token_ids, ngram_length=NGRAM_LEN)
                        selected_ngrams = select_ngrams(all_ngrams, with_pos=True)
                        for pos, ngram in selected_ngrams:
                            rules_automaton_add(tids=ngram, rid=rid, start=pos)

                # update rule thresholds
                rule.low_unique = tids_set_counter(rlow_set)
                rule.high_unique = tids_set_counter(rhigh_set)
                rule.length_unique = rule.high_unique + rule.low_unique
                rule.low_length = tids_multiset_counter(rlow_mset)
                rule.high_length = tids_multiset_counter(rhigh_mset)
                assert rule.length == rule.low_length + rule.high_length

        # # finalize automatons
        self.negative_automaton.make_automaton()
        self.rules_automaton.make_automaton()

        # sparser dicts for faster lookup
        sparsify(self.rid_by_hash)
        sparsify(self.false_positive_rid_by_hash)

        dupe_rules = [rules for rules in dupe_rules_by_hash.values() if len(rules) > 1]
        if dupe_rules:
            dupe_rule_paths = [['file://' + rule.text_file for rule in rules] for rules in dupe_rules]
            msg = (u'Duplicate rules: \n' + u'\n'.join(map(repr, dupe_rule_paths)))
            raise AssertionError(msg)

        self.optimized = True

    def debug_matches(self, matches, message, location=None, query_string=None, with_text=False):
        if TRACE or TRACE_NEGATIVE:
            logger_debug(message + ':', len(matches))

            if TRACE_MATCHES or TRACE_NEGATIVE:
                map(logger_debug, matches)

            if (TRACE_MATCHES_TEXT  or TRACE_NEGATIVE) and with_text:
                logger_debug(message + ' MATCHED TEXTS')
                for m in matches:
                    logger_debug(m)
                    qt, it = get_texts(m, location, query_string, self)
                    print('  MATCHED QUERY TEXT')
                    print(qt)
                    print('  MATCHED RULE TEXT')
                    print(it)
                    print()

    def match(self, location=None, query_string=None, min_score=0, detect_negative=True):
        """
        Return a sequence of LicenseMatch by matching the file at `location` or
        the `query_string` text against the index. Only include matches with
        scores greater or equal to `min_score`.

        `detect_negative` is for testing purpose only.
        """
        assert 0 <= min_score <= 100

        if TRACE:
            print()
            logger_debug('match start....')

        if not location and not query_string:
            return []

        qry = query.build_query(location, query_string, self)
        if not qry:
            logger_debug('#match: No query returned for:', location)
            return []

        #######################################################################
        # Whole file matching: hash, negative and exact matching
        #######################################################################
        whole_query_run = qry.whole_query_run()
        if not whole_query_run or not whole_query_run.matchables:
            logger_debug('#match: whole query not matchable')
            return []

        # hash
        hash_matches = match_hash(self, whole_query_run)
        if hash_matches:
            self.debug_matches(hash_matches, '#match FINAL Hash matched', location, query_string)
            set_lines(hash_matches, qry.line_by_pos)
            return hash_matches

        # negative rules exact matching
        negative = []
        # note: detect_negative is false only to test negative rules detection proper
        if detect_negative and self.negative_rids:
            if TRACE: logger_debug('#match: NEGATIVE')
            negative = self.negative_match(whole_query_run)
            for neg in negative:
                if TRACE_NEGATIVE: self.debug_matches(negative, '   ##match: NEGATIVE subtracting #:', location, query_string)
                whole_query_run.subtract(neg.qspan)
            if TRACE_NEGATIVE: logger_debug('     #match: NEGATIVE found', negative)

        # exact matches
        if TRACE_EXACT: logger_debug('#match: EXACT')
        exact_matches = exact_match(self, whole_query_run, self.rules_automaton)
        if TRACE_EXACT: self.debug_matches(exact_matches, '  #match: EXACT matches#:', location, query_string)

        exact_matches, exact_discarded = refine_matches(exact_matches, self, query=qry)

        if TRACE_EXACT: self.debug_matches(exact_matches, '   #match: ===> exact matches refined')
        if TRACE_EXACT: self.debug_matches(exact_discarded, '   #match: ===> exact matches discarded')

        matches = exact_matches
        discarded = exact_discarded

        #######################################################################
        # Per query run matching.
        #######################################################################
        if TRACE: logger_debug('#match: #QUERY RUNS:', len(qry.query_runs))

        # check if we have some matchable left
        # collect qspans matched exactly e.g. with coverage 100%
        # this coverage check is because we have provision to match fragments (unused for now)
        matched_qspans = [m.qspan for m in exact_matches if m.coverage() == 100]
        # do not match futher if we do not need to
        if whole_query_run.is_matchable(include_low=True, qspans=matched_qspans):

            rules_subset = (self.regular_rids | self.small_rids)

            for qrnum, query_run in enumerate(qry.query_runs, 1):
                if TRACE_QUERY_RUN_SIMPLE:
                    logger_debug('#match: ===> processing query run #:', qrnum)
                    logger_debug('  #match:', query_run)

                if not query_run.is_matchable(include_low=True):
                    if TRACE: logger_debug('#match: query_run NOT MATCHABLE')
                    continue

                # hash match
                #########################
                hash_matches = match_hash(self, query_run)
                if hash_matches:
                    if TRACE: self.debug_matches(hash_matches, '  #match Query run matches (hash)', location, query_string)
                    matches.extend(hash_matches)
                    continue

                # query run match proper using sequence matching
                #########################################
                if TRACE: logger_debug('  #match: Query run MATCHING proper....')

                run_matches = []
                candidates = compute_candidates(query_run, self, rules_subset=rules_subset, top=40)

                if TRACE_QUERY_RUN: logger_debug('      #match: query_run: number of candidates for seq match #', len(candidates))

                for candidate_num, candidate in enumerate(candidates):
                    if TRACE_QUERY_RUN: logger_debug('         #match: query_run: seq matching candidate#:', candidate_num, 'candidate:', candidate)
                    start_offset = 0
                    while True:
                        rule_matches = match_sequence(self, candidate, query_run, start_offset=start_offset)
                        if TRACE_QUERY_RUN and rule_matches: self.debug_matches(rule_matches, '           #match: query_run: seq matches for candidate')
                        if not rule_matches:
                            break
                        else:
                            matches_end = max(m.qend for m in rule_matches)
                            run_matches.extend(rule_matches)

                            if matches_end + 1 < query_run.end:
                                start_offset = matches_end + 1
                                continue
                            else:
                                break

                ############################################################################
                if TRACE_QUERY_RUN: self.debug_matches(run_matches, '    #match: ===> Query run matches', location, query_string, with_text=True)

                run_matches = merge_matches(run_matches, max_dist=MAX_DIST)
                matches.extend(run_matches)

                if TRACE: self.debug_matches(run_matches, '     #match: Query run matches merged', location, query_string)

        # final matching merge, refinement and filtering
        ################################################
        if matches:
            logger_debug()
            logger_debug('!!!!!!!!!!!!!!!!!!!!REFINING!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            self.debug_matches(matches, '#match: ALL matches from all query runs', location, query_string)

            matches, whole_discarded = refine_matches(matches, idx=self, query=qry, min_score=min_score, max_dist=MAX_DIST // 2)
            if TRACE_MATCHES_DISCARD:
                discarded.extend(whole_discarded)
            matches.sort()
            set_lines(matches, qry.line_by_pos)
            self.debug_matches(matches, '#match: FINAL MERGED', location, query_string)
            if TRACE_MATCHES_DISCARD: self.debug_matches(discarded, '#match: FINAL DISCARDED', location, query_string)

        self.debug_matches(matches, '#match: FINAL MATCHES', location, query_string, with_text=True)

        return matches

    def negative_match(self, query_run):
        """
        Match a query run exactly against negative, license-less rules.
        Return a list of negative LicenseMatch for a query run, subtract these matches from the query run.
        """
        matches = exact_match(self, query_run, self.negative_automaton)

        if TRACE_NEGATIVE and matches: logger_debug('     ##final _negative_matches:....', len(matches))
        if TRACE_NEGATIVE and matches: map(logger_debug, matches)

        return matches

    def _print_index_stats(self):
        """
        Print internal Index structures stats. Used for debugging and testing.
        """
        try:
            from pympler.asizeof import asizeof as size_of
        except ImportError:
            print('Index statistics will be approximate: `pip install pympler` for correct structure sizes')
            from sys import getsizeof as size_of

        fields = [
        'dictionary',
        'tokens_by_tid',
        'rid_by_hash',
        'rules_by_rid',
        'tids_by_rid',

        'tids_sets_by_rid',
        'tids_msets_by_rid',

        'regular_rids',
        'negative_rids',
        'small_rids',
        'false_positive_rids',

        'false_positive_rid_by_hash',
        ]

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

    def to_dict(self, all_tokens=False):
        """
        Return a human readable dictionary representing the index replacing
        token ids and rule ids with their string values and the postings by
        lists. Used for debugging and testing.
        """
        dct = {}
        # FIXME: this is not representative and used only for test as a sanity check
        # FIXME: we do not have the low postings
        for rid, postings in enumerate(self.high_postings_by_rid):
            ridentifier = self.rules_by_rid[rid].identifier
            ridentifier = ridentifier + '_' + str(rid)
            dct[ridentifier] = {self.tokens_by_tid[tid]: list(positions) for tid, positions in postings.viewitems()}
        return dct

    def _tokens2text(self, tokens):
        """
        Return a text string from a sequence of token ids.
        Used for tracing and debugging.
        """
        return u' '.join('None' if t is None else self.tokens_by_tid[t] for t in tokens)

    @staticmethod
    def loads(saved):
        """
        Return a LicenseIndex from a pickled string.
        """
        idx = cPickle.loads(saved)
        # perform some optimizations on the dictionaries
        sparsify(idx.dictionary)
        return idx

    def dumps(self):
        """
        Return a pickled string of self.
        """
        # here cPickle fails. Pickle is slower but works
        import pickle
        return pickle.dumps(self, protocol=cPickle.HIGHEST_PROTOCOL)

    def renumber_token_ids(self, frequencies_by_old_tid, _ranked_tokens=global_tokens_by_ranks):
        """
        Return updated index structures with new token ids such that the most
        common tokens (aka. 'junk' or 'low' tokens) have the lowest ids.

        Return a tuple of (len_junk, dictionary, tokens_by_tid, tids_by_rid)
        - len_junk: the number of junk_old_tids tokens such that all junk token
        ids are smaller than this number.
        - dictionary: mapping of token string->token id
        - tokens_by_tid: reverse mapping of token id->token string
        - tids_by_rid: mapping of rule id-> array of token ids

        The arguments all relate to old, temporary token ids and are :
        - frequencies_by_old_tid: mapping of token id-> occurences across all rules
        - _ranked_tokens: callable returning a list of common lowercase token
        strings, ranked from most common to least common Used only for testing
        and default to a global list.

        Common tokens are computed based on a curated list of frequent words and
        token frequencies across rules such that:
         - common tokens have lower token ids smaller than len_junk
         - no rule is composed entirely of junk tokens.
        """
        old_dictionary = self.dictionary
        tokens_by_old_tid = self.tokens_by_tid
        old_tids_by_rid = self.tids_by_rid

        # track tokens for rules with a single token: their token is never junk
        # otherwise they can never be detected
        rules_of_one = set(r.rid for r in self.rules_by_rid if r.length == 1)
        never_junk_old_tids = set(rule_tokens[0] for rid, rule_tokens
                                  in enumerate(old_tids_by_rid)
                                  if rid in rules_of_one)

        # creat initial set of junk token ids
        junk_old_tids = set()
        junk_old_tids_add = junk_old_tids.add

        # Treat very common tokens composed only of digits or single chars as junk
        very_common_tids = set(old_tid for old_tid, token in enumerate(tokens_by_old_tid)
                          if token.isdigit() or len(token) == 1)
        junk_old_tids.update(very_common_tids)

        # TODO: ensure common number as words are treated as very common
        # (one, two, and first, second, etc.)?

        # TODO: add and treat person and place names as always being JUNK

        # Build the candidate junk set as an apprixmate proportion of total tokens
        len_tokens = len(tokens_by_old_tid)
        junk_max = len_tokens // PROPORTION_OF_JUNK

        # Use a curated list of common tokens sorted by decreasing frequency as
        # the basis to determine junk status.
        old_dictionary_get = old_dictionary.get
        for token in _ranked_tokens():
            # stop when we reach the maximum junk proportion
            if len(junk_old_tids) == junk_max:
                break
            old_tid = old_dictionary_get(token)
            if old_tid is not None and old_tid not in never_junk_old_tids:
                junk_old_tids_add(old_tid)

        len_junk = len(junk_old_tids)

        # Assemble our final set of good old token id
        good_old_tids = set(range(len_tokens)) - junk_old_tids
        assert len_tokens == len(junk_old_tids) + len(good_old_tids)

        # Sort the list of old token ids: junk before good, then by decreasing
        # frequencies, then old id.
        # This sort does the renumbering proper of old to new token ids
        key = lambda i: (i in good_old_tids, -frequencies_by_old_tid[i], i)
        new_to_old_tids = sorted(range(len_tokens), key=key)

        # keep a mapping from old to new id used for renumbering index structures
        old_to_new_tids = [new_tid for new_tid, _old_tid in sorted(enumerate(new_to_old_tids), key=itemgetter(1))]

        # create the new ids -> tokens string mapping
        tokens_by_new_tid = [tokens_by_old_tid[old_tid]  for _new_tid, old_tid in enumerate(new_to_old_tids)]

        # create the new dcitionary tokens trings -> new id
        new_dictionary = {token: new_tid  for new_tid, token in enumerate(tokens_by_new_tid)}
        sparsify(new_dictionary)
        old_tids_by_rid = self.tids_by_rid
        # mapping of rule_id->new token_ids array
        new_tids_by_rid = [array('h', (old_to_new_tids[tid] for tid in old_tids)) for old_tids in old_tids_by_rid]

        # Now do a few sanity checks...
        # By construction this should always be true
        assert set(tokens_by_new_tid) == set(tokens_by_old_tid)

        fatals = []
        for rid, new_tids in enumerate(new_tids_by_rid):
            # Check that no rule is all junk: this is a fatal indexing error
            if all(t < len_junk for t in new_tids):
                message = (
                    'WARNING: Weak rule, made only of frequent junk tokens. Can only be matched exactly:',
                    self.rules_by_rid[rid].identifier,
                    u' '.join(tokens_by_new_tid[t] for t in new_tids)
                )
                fatals.append(u' '.join(message))
        if TRACE and fatals:
            # raise IndexError(u'\n'.join(fatals))
            print()
            print('############################################')
            map(print, fatals)
            print('############################################')
            print()
        # TODO: Check that the junk count choice is correct: for instance using some
        # stats based on standard deviation or markov chains or similar
        # conditional probabilities such that we verify that we CANNOT create a
        # distinctive meaningful license string made entirely from junk tokens

        return len_junk, new_dictionary, tokens_by_new_tid, new_tids_by_rid

