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

from __future__ import absolute_import, division, print_function

from array import array
import cPickle
from collections import Counter
from collections import defaultdict
from copy import copy
from itertools import chain
from itertools import izip
from time import time

from bitarray import bitarray

from commoncode.dict_utils import sparsify

from licensedcode import NGRAM_LENGTH
from licensedcode.frequent_tokens import global_tokens_by_ranks

from licensedcode.match import refine_matches

from licensedcode.match_inv import match_inverted
from licensedcode.match_inv import reinject_hits

from licensedcode.match_chunk import index_starters
from licensedcode.match_chunk import match_chunks

from licensedcode.query import Query

from licensedcode.tokenize import ngrams
from licensedcode.prefilter import get_candidates
from licensedcode.prefilter import get_query_candidates
from licensedcode.prefilter import compute_candidates
"""
Main license index construction, query processing and matching entry points.
Actual matching is delegated to modules that implement a matching strategy. 
"""

# debug flags
DEBUG = True
DEBUG_DEEP = False
DEBUG_PERF = False


def logger_debug(*args): pass


def logger_debug_deep(*args): pass


if DEBUG or DEBUG_DEEP:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))

    if DEBUG_DEEP:
        def logger_debug_deep(*args):
            return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))


# if 4, ~ 1/4 of all tokens will be treated as junk
PROPORTION_OF_JUNK = 3

def get_license_matches(location=None, min_score=100):
    """
    Yield detected license matches in the file at `location`.

    min_score is a minimum score threshold for a license match from 0 to 100
    percent. The default is 100 meaning only exact match. With any value below
    100, approximate license matches are included.
    
    # FIXME: is this really?? what about short rules?
    Note that the  minimum length for an approximate match is four words .
    """
    return get_index().match(location, min_score=min_score)


def detect_license(location=None, min_score=100):
    """
    DEPRECATED: legacy API
    Yield detected licenses in the file at `location`. This is a
    wrapper to IndexLicense.match working on the full license index and
    returning only strings as opposed to objects

    An exception may be raised on error.
    Directories yield nothing and are not walked for their containing files.
    Use commoncode.fileutils.walk for walking a directory tree..

    Note that for testing purposes, location can be a list of lines too.

    min_score is the minimum score threshold from 0 to 100.
    """
    for match in get_license_matches(location, min_score=min_score):
        # TODO: return one result per match with a license
        # yielding the default license if provided
        for detected_license in match.rule.licenses:
            yield (detected_license,
                   match.lines.start, match.lines.end,
                   match.qspan.start, match.qspan.end,
                   match.rule.identifier(),
                   match.normalized_score(),)


# global in-memory cache of the license index
_LICENSES_INDEX = None


def get_index():
    """
    Return and eventually cache an index built from an iterable of rules.
    Build the index from the built-in rules dataset.
    """
    global _LICENSES_INDEX
    if not _LICENSES_INDEX:
        from licensedcode.cache import get_or_build_index_from_cache
        _LICENSES_INDEX = get_or_build_index_from_cache()
    return _LICENSES_INDEX


# maximum number of unique tokens we can handle: 16 bits signed integer ~ 32K.
# MAX_TOKENS = 2 ** 15



class LicenseIndex(object):
    """
    A license detection index. An index is queried for license matches found in a query file.
    The index support multiple strategies for finding exact and approximate matches.
    """

    def __init__(self, rules=None, _ngram_length=NGRAM_LENGTH):
        """
        Initialize the index with an iterable of Rule objects.
        """
        # largest token ID for a "junk" token. A token with a smaller id than
        # len_junk is considered a "junk" very common token
        self.len_junk = -1
        self.len_good = -1

        # total number of known tokens
        self.len_tokens = -1

        # mapping of token string > token id
        self.dictionary = {}

        # mapping of token id -> token string as a list where the index is the
        # token id and the value the actual token string
        self.tokens_by_tid = []

        # mapping of token id -> token frequency as a list where the index is
        # the token id and the value the count of occurrences of this token in
        # all rules: Note the most frequent token is 'the' with +100K occurrences

        # TODO: Remove. this is used only during indexing and never afterwards, except for testing
        self.frequencies_by_tid = []

        # mapping of rule id->(mapping of (token_id->list of positions in the rule)
        #
        # The top level mapping is a list where the index is the rule id; and
        # the value a dictionary of lists where the key is a token id and the
        # final value is an array of sorted absolute positions of this token in
        # the rule.
        self.postings_by_rid = []

        # mapping of rule id->(mapping of starter ngrams->[start position, ...])
        #
        # Starter ngrams are either the first ngram of a rule text or first
        # ngram after a rule {{}} gap. Only kept for ngrams of at least
        # ngram_length.

        # For instance for a rule without template, the starter ngram will be
        # the first ngram; start=0.
        #
        # For a rule with templates, there will be one starter ngram and
        # start pos for each run of tokens separated by a gap. In this case
        # a starter ngram is either the first ngram or the ngram following a
        # gap. The start is the position of the first token of the run.

        # ngram_length for starters
        self._ngram_length = _ngram_length
        # mapping of ngram -> [(start, rid, ), ...]
        self.start_ngrams = defaultdict(list)

        # These are mappings of rid-> data as lists of data where the list index
        # is the rule id.
        #
        # rule objects proper
        self.rules_by_rid = []
        # token_id sequence
        self.tokens_by_rid = []

        # template bitvector
        self.bv_template = None
        # bitvector for high tokens
        self.high_bitvectors_by_rid = []
        # bitvector for low tokens
        self.low_bitvectors_by_rid = []
        # Counters of tokens
        # TODO: remove combined frequencies_by_rid
        self.frequencies_by_rid = []
        self.high_frequencies_by_rid = []
        self.low_frequencies_by_rid = []

        # disjunctive sets of regular and negative rule ids
        self.regular_rids = set()
        self.negative_rids = set()

        # if True the index has been optimized and becomes read only:
        # no new rules can be added
        self.optimized = False

        if rules:
            if DEBUG_PERF:
                start = time()
                print('LicenseIndex: building index.')

            # index all and optimize
            self._add_rules(rules, self._ngram_length)
            # self.optimize(

            if DEBUG_PERF:
                duration = time() - start
                len_rules = len(self.rules_by_rid)
                print('LicenseIndex: built index with %(len_rules)d rules in %(duration)f seconds.' % locals())
                self._print_index_stats()

    def _add_rules(self, rules, optimize=True, _ngram_length=NGRAM_LENGTH):
        """
        Add an iterable of Rule objects to the index as an optimized batch
        operation. This replaces any existing indexed rules_by_rid previously added.
        """
        if self.optimized:
            raise Exception('Index has been optimized and cannot be updated.')

        rules_by_rid = list(rules)
        len_rules = len(rules_by_rid)

        # template reused for rule_id "list" mappings
        rules_list_template = [0 for _r in range(len_rules)]

        # First pass: collect tokens, count frequencies and find unique tokens
        ######################################################################
        # compute the unique tokens and frequency at once
        unique_tokens = Counter()
        unique_tokens_update = unique_tokens.update

        # accumulate all rule tokens at once. Also assign the rule ids implicitly
        token_strings_by_rid = rules_list_template[:]

        regular_rids = set()
        regular_rids_add = regular_rids.add

        negative_rids = set()
        negative_rids_add = negative_rids.add

        for rid, rule in enumerate(rules_by_rid):
            rule.rid = rid
            if rule.negative():
                negative_rids_add(rid)
            else:
                regular_rids_add(rid)
            rule_tokens = list(rule.tokens())
            token_strings_by_rid[rid] = rule_tokens
            unique_tokens_update(rule_tokens)

        # Create the tokens lookup structure at once. Note that tokens ids are
        # assigned randomly at first by unzipping: we get the frequencies and
        # tokens->id at once.
        tokens_by_tid, frequencies_by_tid = izip(*unique_tokens.items())
        dictionary = {ts: tid for tid, ts in enumerate(tokens_by_tid)}
        len_tokens = len(tokens_by_tid)

        # for speed
        sparsify(dictionary)

        # replace strings with token ids
        tokens_by_rid = [[dictionary[tok] for tok in rule_tok] for rule_tok in token_strings_by_rid]

        # Second pass: Optimize token ids based on frequencies and common words
        #######################################################################

        # renumber tokens ids
        if optimize:
            renumbered = renumber_token_ids(tokens_by_rid, dictionary, tokens_by_tid, frequencies_by_tid)
            old_to_new, len_junk, dictionary, tokens_by_tid, frequencies_by_tid = renumbered
        else:
            # for testing only
            len_junk = 0
            # this becomes a noop mapping existing id to themselves
            old_to_new = range(len_tokens)

        # mapping of rule_id->new token_ids array
        new_tokens_by_rid = rules_list_template[:]
        # renumber old token ids to new
        for rid, rule_tokens in enumerate(tokens_by_rid):
            new_tokens_by_rid[rid] = array('h', (old_to_new[tid] for tid in rule_tokens))

        # Third pass: build index structures
        ####################################
        # lists of bitvectors for high and low tokens, one per rule
        # ALTERNATIVE: bv_template = bitarray([0 for _t in tokens_by_tid])
        bv_template = bitarray('0') * len_tokens
        high_bitvectors_by_rid = [bv_template.copy() for _r in range(len_rules)]
        low_bitvectors_by_rid = [bv_template.copy() for _r in range(len_rules)]

        frequencies_by_rid = [Counter() for _r in range(len_rules)]
        high_frequencies_by_rid = [Counter() for _r in range(len_rules)]
        low_frequencies_by_rid = [Counter() for _r in range(len_rules)]

        # nested inverted index by rule_id->token_id->[postings array]
        postings_by_rid = [defaultdict(list) for _r in rules_by_rid]

        # mapping of rule_id -> mapping of starter ngrams -> [(start, end,), ...]
        start_ngrams_by_rid = [defaultdict(list) for _r in rules_by_rid]

        # build posting lists and other index structures
        for rid, new_rule_token_ids in enumerate(new_tokens_by_rid):
            rule_postings = postings_by_rid[rid]

            rule_frequencies = frequencies_by_rid[rid]
            rule_high_frequencies = high_frequencies_by_rid[rid]
            rule_low_frequencies = low_frequencies_by_rid[rid]
            high_length = 0
            low_length = 0

            # rule bitvector: index is the token id, 1 means token is present, and 0 absent
            rule_bv = bv_template.copy()

            for pos, new_tid in enumerate(new_rule_token_ids):
                rule_postings[new_tid].append(pos)

                # TODO: optimize: slice assignments could be faster?
                rule_bv[new_tid] = 1
                if new_tid >= len_junk:
                    high_length += 1
                    rule_high_frequencies[new_tid] += 1
                    rule_frequencies[new_tid] += 1
                else:
                    low_length += 1
                    rule_low_frequencies[new_tid] += 1
                    rule_frequencies[new_tid] += 1

            # update rule token ids lengths
            rule = rules_by_rid[rid]
            rule.high_length = high_length
            rule.low_length = low_length

            # build high and low bitvectors
            hbv = rule_bv[len_junk:]
            lbv = rule_bv[:len_junk]
            # all rule should have at least one high tokens
            assert hbv.any()
            high_bitvectors_by_rid[rid] = hbv
            low_bitvectors_by_rid[rid] = lbv

            # collect starters
            start_ngrams = start_ngrams_by_rid[rid]
            for start_ngram, start in index_starters(new_rule_token_ids, rule.gaps, _ngram_length):
                start_ngrams[start_ngram].append(start)

            # for speed
            sparsify(start_ngrams)

            # OPTIMIZED: for speed and memory: convert postings to arrays
            rule_postings = {key: array('h', value) for key, value in rule_postings.items()}
            # for speed
            sparsify(rule_postings)
            postings_by_rid[rid] = rule_postings

        # finally assign back new index structure to self
        self.rules_by_rid = rules_by_rid
        self.postings_by_rid = postings_by_rid
        self.tokens_by_rid = new_tokens_by_rid
        self.start_ngrams_by_rid = start_ngrams_by_rid
        self.negative_rids = negative_rids
        self.regular_rids = regular_rids

        self.len_junk = len_junk
        self.len_good = len_tokens - len_junk
        self.len_tokens = len_tokens

        self.dictionary = dictionary
        self.tokens_by_tid = tokens_by_tid

        # TODO: remove: only used for testing
        self.frequencies_by_tid = frequencies_by_tid

        # TODO: remove combined frequencies_by_rid
        self.frequencies_by_rid = frequencies_by_rid
        self.high_frequencies_by_rid = high_frequencies_by_rid
        self.low_frequencies_by_rid = low_frequencies_by_rid

        self.high_bitvectors_by_rid = high_bitvectors_by_rid
        self.low_bitvectors_by_rid = low_bitvectors_by_rid
        self.bv_template = bv_template

        if optimize:
            self.optimized = True
        else:
            # for testing
            return tokens_by_rid

    def match(self, location=None, query_string=None, min_score=100, min_length=4, _ngram_length=NGRAM_LENGTH, _detect_negative=True):
        """
        Return a sequence of LicenseMatch by matching the file at `location` or
        the `query_string` text against the index. Only include matches with
        scores greater or equal to `min_score`.
        """
        # TODO: OPTIMIZE: Compute hash based on runs, broken on first ngram and
        # last ngrams index for super fast exact match of a full text at once
        # TODO: match whole rules exactly using a hash on whole vector

        # TODO: OPTIMIZE: LRU cache matches for a query: intuition: several
        # files in the same project will have a quasi identical header comment
        # notice

        # TODO: OPTIMIZE: we should LRU cache query vectors-> found matches because
        # there is often a repeated pattern of identical license headers in the code
        # files of a project. Another common pattern is for multiple copies of a
        # full (and possibly long) license text. by caching and returning the cache
        # right away, we can avoid doing the same matching over and over entirely.

        # TODO: OPTIMIZE: combined with caching above, and if we reuse query runs
        # again here, we could normalize the cached vector for a run, such that the
        # query positions in a cached run vector are starting at 0. This would speed
        # up matching when a run vector may not start at the same absolute position,
        # but is the same when considering run-relative zero-base positions. This
        # would be the case for instance in a long composite license notice where
        # the same license text may occur several times (For instance Android or
        # iOS).

        assert 0 <= min_score <= 100
        logger_debug('match start....')

        if not location and not query_string:
            return []

        matches = []
        discarded = []

        qry = Query(location, query_string, self)
        query_candidates = None
        query_runs = qry.query_runs()

        # TODO: compute query-wide candidates and hashes
        if False:
            query_runs = list(qry.query_runs())
            # TODO consider using from_iterable
            # query_tokens = chain.from_iterable(qr.tokens for qr in query_runs)
            query_tokens = chain(*(qr.tokens for qr in query_runs))
            query_candidates = get_query_candidates(query_tokens, self)
            if not query_candidates:
                return []

        for query_run in query_runs:
            run_matches = []
            logger_debug()
            logger_debug('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            logger_debug('#match: processing query run:', query_run)

            if not query_run.matchable():
                logger_debug('#match: query run not matchable')
                continue

            # note: _detect_negative may be false for tests only, to test negative rules detection
            if _detect_negative:
                # remove the negative rules matches from the query stream
                negative_matches = self._negative_match(query_run, _ngram_length=_ngram_length)
                if negative_matches:
                    query_run.substract(negative_matches)
                if DEBUG: logger_debug('###match: Found negative matches#:', len(negative_matches))

            # first pass with chunk matching top 10
            #######################################################
            if DEBUG: logger_debug('#match: Candidates1...')
            candidates1, all_candidates = compute_candidates(query_run, self, rules_subset=self.regular_rids)
            if DEBUG: logger_debug('##match: Collected candidates1 #:', len(candidates1), len(all_candidates))

            if DEBUG: logger_debug('#match: CHUNK1 MATCHING....')

            chunk_matches = match_chunks(self, candidates1, query_run, _ngram_length=_ngram_length)

            if DEBUG: logger_debug('##match: CHUNK1: Found matches #:', len(chunk_matches))
            if DEBUG: map(logger_debug, chunk_matches)

            chunk_matches = reinject_hits(chunk_matches, query_run, self.rules_by_rid, self.postings_by_rid, len_junk=self.len_junk, dilate=5, high_tokens=True)
            chunk_matches = reinject_hits(chunk_matches, query_run, self.rules_by_rid, self.postings_by_rid, len_junk=0, dilate=0, high_tokens=False)

            if DEBUG: logger_debug('###match: CHUNK1: high tokens re-injected')
            if DEBUG: map(logger_debug, chunk_matches)

            run_matches.extend(chunk_matches)
            # keep only subset of unmatched query
            query_run.substract(chunk_matches)

            # second pass with chunk matching top 10 again
            #######################################################

            # stop early if we have consumed all the query.
            if not query_run.matchable():
                matches.extend(chunk_matches)
                continue

            if DEBUG: logger_debug('#match: Candidates2...')
            candidates2, all_candidates = compute_candidates(query_run, self, rules_subset=all_candidates)
            if DEBUG: logger_debug('##match: Collected candidates2 #:', len(candidates2), len(all_candidates))

            if DEBUG: logger_debug('#match: CHUNK MATCHING2....')

            chunk_matches = match_chunks(self, candidates2, query_run, _ngram_length=_ngram_length)

            if DEBUG: logger_debug('##match: CHUNK2: Found matches #:', len(chunk_matches))
            if DEBUG: map(logger_debug, chunk_matches)

            chunk_matches = reinject_hits(chunk_matches, query_run, self.rules_by_rid, self.postings_by_rid, len_junk=self.len_junk, dilate=5, high_tokens=True)
            chunk_matches = reinject_hits(chunk_matches, query_run, self.rules_by_rid, self.postings_by_rid, len_junk=0, dilate=0, high_tokens=False)

            if DEBUG: logger_debug('###match: CHUNK2: high tokens re-injected')
            if DEBUG: map(logger_debug, chunk_matches)

            run_matches.extend(chunk_matches)
            # keep only subset of unmatched query
            query_run.substract(chunk_matches)

            # stop early if we have consumed all the query.
            if not query_run.matchable():
                matches.extend(chunk_matches)
                continue

            # third pass with chunk matching top 10 again
            #######################################################

            if DEBUG: logger_debug('#match: Candidates3...')
            candidates3, all_candidates = compute_candidates(query_run, self, rules_subset=all_candidates)
            if DEBUG: logger_debug('##match: Collected candidates3 #:', len(candidates3), len(all_candidates))

            if DEBUG: logger_debug('#match: CHUNK MATCHING3....')

            chunk_matches = match_chunks(self, candidates3, query_run, _ngram_length=_ngram_length)

            if DEBUG: logger_debug('##match: CHUNK3: Found matches #:', len(chunk_matches))
            if DEBUG: map(logger_debug, chunk_matches)

            chunk_matches = reinject_hits(chunk_matches, query_run, self.rules_by_rid, self.postings_by_rid, len_junk=self.len_junk, dilate=5, high_tokens=True)
            chunk_matches = reinject_hits(chunk_matches, query_run, self.rules_by_rid, self.postings_by_rid, len_junk=0, dilate=0, high_tokens=False)

            if DEBUG: logger_debug('###match: CHUNK3: high tokens re-injected')
            if DEBUG: map(logger_debug, chunk_matches)

            run_matches.extend(chunk_matches)
            # keep only subset of unmatched query
            query_run.substract(chunk_matches)

            # stop early if we have consumed all the query.
            if not query_run.matchable():
                matches.extend(chunk_matches)
                continue

            # inverted matches pass 1
            #######################################################
            if DEBUG: logger_debug('#match: Candidates4...')
            candidates4, all_candidates = compute_candidates(query_run, self, all_candidates)
            if DEBUG: logger_debug('##match: Collected candidates4 #:', len(candidates4))

            inv_matches = match_inverted(self, candidates4, query_run, max_dist=5, dilate=5)

            if DEBUG: logger_debug('#match: INVERTED:', len(inv_matches))
            if DEBUG: map(logger_debug, inv_matches)

            run_matches.extend(inv_matches)
            query_run.substract(inv_matches)

            # stop early if we have consumed all the query.
            if not query_run.matchable():
                matches.extend(inv_matches)
                continue

            # inverted matches pass 2
            #######################################################
            if DEBUG: logger_debug('#match: Candidates5...')
            candidates5, all_candidates = compute_candidates(query_run, self, all_candidates)
            if DEBUG: logger_debug('##match: Collected candidates4 #:', len(candidates5))

            inv_matches = match_inverted(self, candidates5, query_run, max_dist=5, dilate=5)

            if DEBUG: logger_debug('#match: INVERTED:', len(inv_matches))
            if DEBUG: map(logger_debug, inv_matches)

            run_matches.extend(inv_matches)
            query_run.substract(inv_matches)

            # stop early if we have consumed all the query.
            if not query_run.matchable():
                matches.extend(inv_matches)
                continue


            if DEBUG: logger_debug('#match: query run matches before filtering:', len(matches))
            if DEBUG: map(logger_debug, run_matches)

            if DEBUG: logger_debug('###match: FILTERING...')
            refined_matches, refined_discarded = refine_matches(run_matches, max_dist=15, min_length=min_length, min_density=0.3, min_score=0)

            if DEBUG: logger_debug('#match: query run matches after filtering:', len(refined_matches))
            if DEBUG: map(logger_debug, refined_matches)
            if DEBUG: logger_debug('#match: query run discarded matches after filtering:', len(refined_discarded))
            if DEBUG: map(logger_debug, refined_discarded)

            matches.extend(refined_matches)
            discarded.extend(refined_discarded)

        if DEBUG: logger_debug('#match: matches :', len(matches))
        if DEBUG_DEEP: map(logger_debug, matches)
        if DEBUG: logger_debug('#match: discarded :', len(discarded))
        if DEBUG_DEEP: map(logger_debug, discarded)

        # finally refine once more across all matches
        all_matches, all_discarded = refine_matches(matches + discarded, max_dist=15, min_length=min_length, min_density=0.3, min_score=min_score)

        if DEBUG: logger_debug('#match: whole query matches   :', len(all_matches))
        if DEBUG: map(logger_debug, all_matches)
        if DEBUG: logger_debug('#match: whole query discarded :', len(all_discarded))
        if DEBUG: map(logger_debug, all_discarded)

        all_matches.sort()
        return all_matches

    def _negative_match(self, query_run, _ngram_length=NGRAM_LENGTH):
        """
        Match a query run against negative, license-less rules.
        """
        logger_debug(' ##_negative_match: NEGATIVE MATCHING....')

        candidates1 = get_candidates(query_run, self, self.negative_rids, min_score=100)
        chunk_matches = match_chunks(self, candidates1, query_run, _ngram_length)
        # note: we trick the re-injection of both junk and good at once
        negative_matches = reinject_hits(chunk_matches, query_run, self.rules_by_rid, self.postings_by_rid, len_junk=0, dilate=3, high_tokens=False)

        # keep only subset of unmatched query at this step, working on a copy of the query run
        new_query_run = copy(query_run)
        new_query_run.substract(chunk_matches)

        if new_query_run.matchable():
            candidates2 = get_candidates(new_query_run, self, set(rid for _, rid in candidates1), min_score=100)
            negative_matches += match_inverted(self, candidates2, query_run, max_dist=2, dilate=3)

        negative_matches, _discarded = refine_matches(negative_matches, max_dist=3, min_length=4, min_density=0.8, min_score=100)
        return negative_matches

    def _print_index_stats(self):
        """
        Print internal Index structures stats. Used for debugging and testing.
        """
        try:
            from pympler.asizeof import asizeof as size_of
        except ImportError:
            print('Index statistics will be approximate: `pip install pympler` for correct structure sizes')
            from sys import getsizeof as size_of

        internal_structures = [
            'postings_by_rid    ',
            'dictionary         ',
            'tokens_by_tid      ',
            'frequencies_by_tid ',
            'rules_by_rid       ',
            'frequencies_by_rid ',
        ]

        print('Index statistics:')
        total_size = 0
        for struct_name in internal_structures:
            struct = getattr(self, struct_name.strip())
            print('  ', struct_name, ':', 'length    :', len(struct))
            siz = size_of(struct)
            total_size += siz
            print('  ', struct_name, ':', 'size in MB:', round(siz / (1024 * 1024), 2))
        print('    TOTAL internals in MB:', round(total_size / (1024 * 1024), 2))
        print('    TOTAL real size in MB:', round(size_of(self) / (1024 * 1024), 2))

    def _as_dict(self):
        """
        Return a human readable dictionary representing the index replacing
        token ids and rule ids with their string values and the postings by
        lists. Used for debugging and testing.
        """
        as_dict = {}
        for rid, tok2pos in enumerate(self.postings_by_rid):
            as_dict[self.rules_by_rid[rid].identifier()] = [(self.tokens_by_tid[tokid], list(posts),) for tokid, posts in sorted(tok2pos.items())]
        return as_dict

    @staticmethod
    def loads(saved):
        """
        Return a LicenseIndex from a pickled string.
        """
        idx = cPickle.loads(saved)

        # perform some optimizations on dictionaries
        sparsify(idx.dictionary)
        for post in idx.postings_by_rid:
            sparsify(post)
        for start in idx.start_ngrams_by_rid:
            sparsify(start)

        return idx

    def dumps(self):
        """
        Return a pickled string of self.
        """
        return cPickle.dumps(self, protocol=cPickle.HIGHEST_PROTOCOL)


def renumber_token_ids(rules_tokens_ids, dictionary, tokens_by_tid, frequencies_by_tid, length=9, with_checks=True):
    """
    Return updated index structures with new token ids such that the most common
    aka. 'junk' tokens have the lowest ids. 

    `rules_tokens_ids` is a mapping of rule_id->sequence of token ids
    
    These common tokens are based on a curated list of frequent words and
    further refined such that:
     - no rule text sequence is composed entirely of these common tokens.
     - no or only a few rule text sub-sequence of `length` tokens (aka.
     ngrams) is not composed entirely of these common tokens.

    The returned structures are:
    - old_to_new: mapping of (old token id->new token id)
    - len_junk: the highest id of a junk token
    - dictionary (token string->token id)
    - tokens_by_tid (token id->token string)
    - frequencies_by_tid (token id->frequency)
    """
    # keep track of very common junk tokens: digits and single letters
    very_common = set()
    very_common_add = very_common.add
    string_lowercase = u'abcdefghijklmnopqrstuvwxyz'
    for tid, token in enumerate(tokens_by_tid):
        # DIGIT TOKENS: Treat tokens composed only of digits as common junk
        # SINGLE ASCII LETTER TOKENS: Treat single ASCII letter tokens as common junk

        # TODO: ensure common numbers as strings are always there (one, two, and first, second, etc.)
        if token.isdigit() or (len(token) == 1 and token in string_lowercase):
            very_common_add(tid)

    # keep track of good, "not junk" tokens
    good = set()
    good_update = good.update

    # Classify rules tokens as smaller or equal to `length` or regular.
    regular_rules = []
    regular_rules_append = regular_rules.append
    small_rules = []
    small_rules_append = small_rules.append

    for rid, rule_toks_ids in enumerate(rules_tokens_ids):
        len_toks = len(rule_toks_ids)
        if len_toks == 1:
            # RULES of ONE TOKEN: their token cannot be junk
            good_update(rule_toks_ids)
        if len_toks <= length:
            small_rules_append((rid, rule_toks_ids))
        else:
            regular_rules_append((rid, rule_toks_ids))

    # Build a candidate junk set with a defined proportion of junk tokens the
    # size of of tokens set: we use a curated list of common words as a base.

    proportion_of_junk = PROPORTION_OF_JUNK
    junk_max = abs((len(tokens_by_tid) / proportion_of_junk) - len(very_common))

    junk = set()
    junk_add = junk.add
    dictionary_get = dictionary.get
    junk_count = 0

    for token in global_tokens_by_ranks():
        tid = dictionary_get(token)
        if tid is None:
            continue

        if tid not in very_common and tid not in good:
            junk_add(tid)
            junk_count += 1

        if junk_count == junk_max:
            break

    # Assemble our final junk and not junk sets
    final_junk = (very_common | junk) - good
    good = set(range(len(tokens_by_tid))) - final_junk

    if with_checks:
        # Now do a few sanity checks...
        def tokens_str(_tks):
            return u' '.join(tokens_by_tid[_tk] for _tk in _tks)

        # Check that no small rule is made entirely of junk
        for rid, tokens in small_rules:
            try:
                assert not all([jt in final_junk for jt in tokens])
            except AssertionError:
                # this is a serious index issue
                print('!!!LicenseIndex: FATAL ERROR: small rule: ', rid , 'is all made of junk:', tokens_str(tokens))
                raise

        # Check that not too many ngrams are made entirely of junk
        # we build a set of ngrams for `length` over tokens of rules at equal or
        # bigger than length and check them all

        all_junk_ngrams_count = 0
        for rid, tokens in regular_rules:
            for ngram in ngrams(tokens, length):
                # skip ngrams composed only of common junk as not significant
                if all(nt in very_common for nt in ngram):
                    continue
                try:
                    # note: we check only against junk, not final_junk
                    assert not all(nt in junk for nt in ngram)
                except AssertionError:
                    all_junk_ngrams_count += 1

        # TODO: test that the junk choice is correct: for instance using some
        # stats based on standard deviation or markov chains or similar
        # conditional probabilities such that we verify that we CANNOT create a
        # distinctive meaningful license string made entirely from junk tokens

        # TODO: ?check that we do not have too many ngrams made entirely of junk

    # Sort each set of old token IDs by decreasing original frequencies
    # FIXME: should use a key function not a schwartzian sort
    decorated = ((frequencies_by_tid[old_id], old_id) for old_id in final_junk)
    final_junk = [t for _f, t in sorted(decorated, reverse=True)]

    # FIXME: should use a key function not a schwartzian sort
    decorated = ((frequencies_by_tid[old_id], old_id) for old_id in good)
    good = [t for _f, t in sorted(decorated, reverse=True)]

    # create the new ids -> tokens value mapping
    new_tokens_by_tid = [tokens_by_tid[t] for t in final_junk + good]

    # sanity check: by construction this should always be true
    assert set(new_tokens_by_tid) == set(tokens_by_tid)

    # create new structures based on new ids and a mapping from old to new id
    len_tokens = len(new_tokens_by_tid)
    old_to_new = array('h', [0] * len_tokens)
    new_frequencies_by_tid = [None] * len_tokens
    new_dictionary = {}

    # assign new ids, re build dictionary, frequency
    for new_id, token in enumerate(new_tokens_by_tid):
        old_id = dictionary[token]
        old_to_new[old_id] = new_id

        new_dictionary[token] = new_id

        old_freq = frequencies_by_tid[old_id]
        new_frequencies_by_tid[new_id] = old_freq

    sparsify(new_dictionary)
    return old_to_new, len(final_junk), new_dictionary, new_tokens_by_tid, new_frequencies_by_tid
