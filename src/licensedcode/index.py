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

from __future__ import print_function, absolute_import

from array import array
import cPickle
from collections import Counter
from collections import defaultdict
from itertools import izip
from time import time

from bitarray import bitarray

from commoncode.dict_utils import sparsify

from licensedcode import NGRAM_LENGTH
from licensedcode.frequent_tokens import global_tokens_by_ranks

from licensedcode.match import filter_matches
from licensedcode.match import filter_sparse_matches
from licensedcode.match import filter_low_scoring_matches
from licensedcode.match import filter_short_matches
from licensedcode.match import LicenseMatch

from licensedcode.match_inv import match_inverted
from licensedcode.match_inv import reinject_hits

from licensedcode.match_chunk import index_starters
from licensedcode.match_chunk import match_chunks

from licensedcode.prefilter import bit_candidates
from licensedcode.prefilter import freq_candidates

from licensedcode.query import filtered_query_data
from licensedcode.query import query_data

from licensedcode.tokenize import ngrams

"""
Main license index construction, query processing and matching entry points.
Actual matching is delegated to modules that implement a matching strategy. 
"""

# debug flags
DEBUG = False
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
                   match.qregion.start, match.qregion.end,
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
        # this is equivalent to a defaultdict(defaultdict(list))
        self.start_ngrams_by_rid = []

        # These are mappings of rid-> data as lists of data where the list index is the
        # rule id.
        #
        # rule objects proper
        self.rules_by_rid = []
        # token_ids sequence
        self.tokens_by_rid = []
        # bitvector for high tokens
        self.high_bitvectors_by_rid = []
        # bitvector for low tokens
        self.low_bitvectors_by_rid = []
        # Counters of tokens
        self.frequencies_by_rid = []

        # Lenghts
        self.high_lengths_by_rid = []
        self.lengths_by_rid = []
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
        operation. This replaces any existing indexed rules previously added.
        """
        if self.optimized:
            raise Exception('Index has been optimized and cannot be updated.')

        rules = list(rules)

        # First pass: collect tokens, count frequencies and find unique tokens
        ######################################################################
        # compute the unique tokens and frequency at once
        unique_tokens = Counter()

        # accumulate all rule tokens at once. Also assign the rule ids
        tokens_by_rid = []

        regular_rids = set()
        regular_rids_add = regular_rids.add
        negative_rids = set()
        negative_rids_add = negative_rids.add

        for rid, rule in enumerate(rules):
            rule.rid = rid
            if rule.negative():
                negative_rids_add(rid)
            else:
                regular_rids_add(rid)
            rule_tokens = list(rule.tokens())
            tokens_by_rid.append(rule_tokens)
            unique_tokens.update(rule_tokens)

        # Create the tokens lookup structure at once.
        # Note that tokens ids are assigned randomly at first by unzipping we
        # get the frequencies and tokens->id at once.
        tokens_by_tid, frequencies_by_tid = izip(*sorted(unique_tokens.most_common()))
        dictionary = {ts: tid for tid, ts in enumerate(tokens_by_tid)}

        # for speed
        sparsify(dictionary)

        # replace strings with token ids
        rules_tokens_ids = [[dictionary[tok] for tok in rule_tok] for rule_tok in tokens_by_rid]
        len_tokens = len(tokens_by_tid)

        # Second pass: Optimize token ids based on frequencies and common words
        #######################################################################

        # renumber tokens ids
        if optimize:
            renumbered = renumber_token_ids(rules_tokens_ids, dictionary, tokens_by_tid, frequencies_by_tid)
            old_to_new, len_junk, dictionary, tokens_by_tid, frequencies_by_tid = renumbered
        else:
            # for testing only
            len_junk = 0
            # this becomes a noop mapping existing id to themselves
            old_to_new = range(len_tokens)

        # mapping of rule_id->new token_ids array
        new_rules_tokens_ids = []
        # renumber old token ids to new
        for rule_token_ids in rules_tokens_ids:
            new_rules_tokens_ids.append(array('h', (old_to_new[tid] for tid in rule_token_ids)))

        # Third pass: build index structures
        ####################################
        # lists of bitvectors for high and low tokens, one per rule
        high_bitvectors_by_rid = [0 for _r in rules]
        low_bitvectors_by_rid = [0 for _r in rules]

        frequencies_by_rid = [0 for _r in rules]
        lengths_by_rid = array('h', [0 for _r in rules])

        # nested inverted index by rule_id->token_id->[postings array]
        postings_by_rid = [defaultdict(list) for _r in rules]

        # mapping of rule_id -> mapping of starter ngrams -> [(start, end,), ...]
        start_ngrams_by_rid = [defaultdict(list) for _r in rules]

        bv_template = bitarray([0 for _t in tokens_by_tid])

        # build posting lists and other index structures
        for rid, new_rule_token_ids in enumerate(new_rules_tokens_ids):
            rid_postings = postings_by_rid[rid]

            tokens_frequency = Counter()
            # rule bitvector: index is the token id, 1 means token is present, and 0 absent
            tokens_occurrence = bv_template.copy()

            # loop through rules token (new) ids
            for pos, new_tid in enumerate(new_rule_token_ids):
                # append posting
                rid_postings[new_tid].append(pos)
                # set bit to one in bitvector for the token id
                # TODO: optimize: slice assignments could be faster?
                tokens_frequency[new_tid] += 1
                tokens_occurrence[new_tid] = 1

            sparsify(rid_postings)

            # build a  high and low bitvector for the rule
            high_bitvectors_by_rid[rid] = tokens_occurrence[len_junk:]
            # build a  high and low bitvector for the rule
            low_bitvectors_by_rid[rid] = tokens_occurrence[:len_junk]

            frequencies_by_rid[rid] = tokens_frequency
            lengths_by_rid[rid] = len(new_rule_token_ids)

            # collect starters
            rid_starters = start_ngrams_by_rid[rid]
            gaps = rules[rid].gaps
            for starter_ngram, start in index_starters(new_rule_token_ids, gaps, _ngram_length):
                rid_starters[starter_ngram].append(start)

            sparsify(rid_starters)

            # OPTIMIZED: for faster access to index: convert postings to arrays
            postings_by_rid[rid] = {key: array('h', value) for key, value in rid_postings.items()}

        # assign back the created index structure to self attributes
        self.postings_by_rid = postings_by_rid
        self.len_junk = len_junk
        self.len_tokens = len_tokens
        self.tokens_by_tid = tokens_by_tid
        self.frequencies_by_tid = frequencies_by_tid
        self.lengths_by_rid = lengths_by_rid
        self.dictionary = dictionary
        self.rules_by_rid = rules
        self.high_bitvectors_by_rid = high_bitvectors_by_rid
        self.low_bitvectors_by_rid = low_bitvectors_by_rid
        self.frequencies_by_rid = frequencies_by_rid
        self.tokens_by_rid = new_rules_tokens_ids
        self.start_ngrams_by_rid = start_ngrams_by_rid
        self.negative_rids = negative_rids
        self.regular_rids = regular_rids
        if optimize:
            self.optimized = True
        else:
            # for testing
            return rules_tokens_ids

    def match(self, location=None, query=None, min_score=100, min_length=4, _ngram_length=NGRAM_LENGTH, _check_negative=True):
        """
        Return a sequence of LicenseMatch by matching the file at `location` or
        the `query` text string against the index. Only include matches with
        scores greater or equal to `min_score`.
        """
        # TODO: consider new match procedure breaking query in runs
        # TODO: consider returning all matches of all scores always:
        #  after exact matching, match stepwise by 5 or 10% decrements performing approximate matching.

        # TODO: OPTIMIZE: LRU cache matches for a query: intuition: several
        # files in the same project will have a quasi identical header comment
        # notice

        # TODO: OPTIMIZE: we should LRU cache query vectors-> found matches because
        # there is often a repeated pattern of identical license headers in the code
        # files of a project. Another common pattern is for multiple copies of a
        # full (and possibly long) license text. by caching and returning the cache
        # right away, we can avoid doing the same matching over and over entirely.

        # TODO: OPTIMIZE: Compute hash based on runs, broken on first ngram and
        # last ngrams index for super fast exact match of a full text at once
        # TODO: match whole rules exactly using a hash on whole vector

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

        line_by_pos, qvector1, qtokens1 = query_data(location, query, self.dictionary)

        if _check_negative:
            logger_debug('##################match: NEGATIVE MATCHING....')
            # Match 100% against negative rules if any first
            negative_matches = self._match(qtokens1, qvector1, line_by_pos, min_score=100, min_density=0.8, min_length=4, max_dist1=0, max_dist2=2, match_negative=True, _ngram_length=_ngram_length)
            logger_debug('==>match:negative_matches:', len(negative_matches))
            if DEBUG: map(logger_debug, sorted(negative_matches, key=lambda m: m.qregion))
        else:
            negative_matches = []

        qtokens2, qvector2 = qtokens1, qvector1
        # then remove the negative matches from the query data
        if negative_matches:
            # keep only subset of unmatched query at this step
            qtokens2, qvector2 = filtered_query_data(qtokens1, negative_matches, self.len_tokens)

        logger_debug('##################match: EXACT MATCHING....')
        # Match 100% always
        exact_matches = self._match(qtokens2, qvector2, line_by_pos, min_score=100, min_density=0.5, min_length=min_length, max_dist1=5, max_dist2=15, dilate1=0, dilate2=5, match_negative=False, _ngram_length=_ngram_length)
        logger_debug('==>match:exact_matches:', len(exact_matches))

        approx_matches = []
        # If min score is not 100, match approx
        if min_score != 100:
            qtokens3, qvector3 = qtokens2, qvector2
            # first remove the 100% matches from the query data
            if exact_matches:
                qtokens3, qvector3 = filtered_query_data(qtokens2, exact_matches, self.len_tokens)

            logger_debug('##################match: APPROX MATCHING....')

            # then match approx
            approx_matches = self._match(qtokens3, qvector3, line_by_pos, min_score=min_score, min_density=0.4, min_length=min_length, max_dist1=5, max_dist2=15, dilate1=1, dilate2=5, match_negative=False, _ngram_length=_ngram_length)

        logger_debug('==>match:approx_matches:', len(approx_matches))

        return sorted(exact_matches + approx_matches)

    def _match(self, qtokens, qvector, line_by_pos, min_score=100, min_density=0.3, min_length=4, max_dist1=11, max_dist2=15, dilate1=1, dilate2=6, match_negative=False, _ngram_length=NGRAM_LENGTH):
        """
        Return a sequence of LicenseMatch by matching the file at `location` or
        the `query` text string against the index. Only include matches with
        scores greater or equal to `min_score`.
        If match_negative is True, only match against negative rules.
        Otherwise do not match against negative rules and only consider "regular" rules.
        """

        assert 0 <= min_score <= 100
        logger_debug('_match start....')


        # Collect candidate rules using bitvectors of good tokens
        # ##############################################################
        logger_debug('   #############_match: PREFILTER....\n')
        logger_debug('  _match: candidates1: start: filter rules with bitvector distance')
        if match_negative:
            rules_subset = self.negative_rids
        else:
            rules_subset = self.regular_rids

        candidates1 = bit_candidates(qvector, self.high_bitvectors_by_rid, self.low_bitvectors_by_rid, self.len_junk, rules_subset=rules_subset, min_score=min_score)
        if not candidates1:
            logger_debug('  _match: candidates1: all junk from bitvector. No match')
            return []
        logger_debug('  _match: candidates1:', len(candidates1), 'candidates rules from bitvector.')

        # Refine candidate rules using freqs and min score
        # ##############################################################
        logger_debug('  _match: candidates2: start: filter rules with freqs')

        candidates2 = freq_candidates(qvector, self.frequencies_by_rid, self.lengths_by_rid, rules_subset=set(rid for (_, rid) in candidates1), min_score=min_score)

        if not candidates2:
            logger_debug('  _match: candidates2: No match')
            return []
        logger_debug('  _match: candidates2:', len(candidates2), 'candidates rules from freq.')

        # Chunks matching using starters index
        # ####################################################################
        logger_debug('   #############_match: CHUNK MATCHING....\n')
        matches1 = match_chunks(self, candidates2, qtokens, line_by_pos, _ngram_length=_ngram_length)
        if DEBUG: map(logger_debug, sorted(matches1, key=lambda m: m.qregion))

        if matches1:
            logger_debug('   _match: matches1: Found matches #', len(matches1))
            if DEBUG: map(logger_debug, sorted(matches1, key=lambda m: m.qregion))
            matches1 = reinject_hits(matches1, qvector, self.rules_by_rid, self.postings_by_rid, len_junk=self.len_junk, line_by_pos=line_by_pos, dilate=dilate1, junk=False)
            for m in matches1:
                m.simplify()

            logger_debug('   ##### _match: matches1: reinjected', len(matches1))
            if DEBUG:
                m = matches1[0]
                logger_debug('qspans')
                for span in m.qspans:
                    logger_debug(span);
                logger_debug('ispans')
                for span in m.ispans:
                    logger_debug(span);

            # keep only subset of unmatched query at this step
            qtokens2, qvector2 = filtered_query_data(qtokens, matches1, self.len_tokens)
            if DEBUG:
                logger_debug('   _match:  len qtokens1,qtokens2', len(qtokens), len([q for q in qtokens2 if q is not None]))

            # TODO: OPTIMIZE: we do not need to re-match against every rule, but only against the previous candidates
            # recollect remainder candidate rules using bitvectors of good tokens
            candidates3 = bit_candidates(qvector2, self.high_bitvectors_by_rid, self.low_bitvectors_by_rid, self.len_junk, set(rid for _, rid in candidates2), min_score=min_score)

            if not candidates3:
                logger_debug('   _match: candidates3: all junk from bitvector. No more matches')
            else:
                logger_debug('   _match: candidates3:', len(candidates3), 'candidates rules from bitvector.')

            # Refine candidate rules using freqs and min score
            # ##############################################################
            logger_debug('   _match: candidates4: start: filter rules with freqs')

            candidates4 = freq_candidates(qvector2, self.frequencies_by_rid, self.lengths_by_rid, rules_subset=set(rid for _, rid in candidates3), min_score=min_score)

            logger_debug('   _match: candidates4:', len(candidates4), 'candidates rules from freq.')
        else:
            logger_debug('   _match: matches1: No match Found')
            qvector2 = qvector
            qtokens2 = qtokens
            candidates4 = candidates2

        # Match against the inverted index
        # ####################################################################
        # We proceed in order of higher scored rule in the filtering steps one rule at a time
        matches2 = []
        logger_debug('   #############_match: INVERTED MATCHING....\n')
        if any(tid is not None for tid in qtokens2):
            # TODO: stop early if we have consumed all the query.
            matches2 = match_inverted(self, candidates4, qvector2, line_by_pos, min_score=min_score, max_dist=max_dist1, min_density=min_density, dilate=dilate2, min_length=min_length)
            if DEBUG: logger_debug();map(logger_debug, sorted(matches2, key=lambda m: m.qregion))

            logger_debug('  _match: matches inverted:', len(matches2))

        all_matches = matches1 + matches2

        logger_debug('   #############_match: MERGING and FILTERING....\n')
        logger_debug('  _match: matches: ALL matches#', len(all_matches))
        if DEBUG_DEEP: logger_debug();map(logger_debug, sorted(all_matches, key=lambda m: m.qregion))

        for m in all_matches:
            m.simplify()
        logger_debug('  _match: matches: ALL matches simplified#', len(all_matches))
        if DEBUG_DEEP: logger_debug();map(logger_debug, sorted(all_matches, key=lambda m: m.qregion))

        if not all_matches:
            logger_debug('  _match: NO matches')
            return []

        all_matches = LicenseMatch.merge(all_matches, merge_spans=True, max_dist=max_dist2)

        logger_debug('  _match: ##merged_matches#:', len(all_matches))
        if DEBUG_DEEP: map(logger_debug, sorted(all_matches, key=lambda m: m.qregion))

        all_matches = filter_sparse_matches(all_matches, min_density=min_density)

        logger_debug('  _match: after sparse filter#', len(all_matches))
        if DEBUG: map(print, sorted(all_matches, key=lambda m: m.qregion))

        all_matches = filter_short_matches(all_matches, min_length=min_length)

        logger_debug('  _match: after filter_short_matches#', len(all_matches))
        if DEBUG_DEEP: map(print, sorted(all_matches, key=lambda m: m.qregion))

        all_matches = filter_low_scoring_matches(all_matches, min_score=min_score)

        logger_debug('  _match: after filter_low_scoring_matches#', len(all_matches))
        if DEBUG_DEEP: map(print, sorted(all_matches, key=lambda m: m.qregion))

        all_matches = filter_matches(all_matches)

        logger_debug('  _match: filtered_matches#:', len(all_matches))
        if DEBUG_DEEP: map(print, sorted(all_matches, key=lambda m: m.qregion))

        all_matches = filter_low_scoring_matches(all_matches, min_score=min_score)

        logger_debug('  _match: final matches#:', len(all_matches))
        if DEBUG_DEEP: map(print, sorted(all_matches, key=lambda m: m.qregion))

        return sorted(all_matches)

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
            print('  ', struct_name, ':', 'size in MB:', round(siz / (1024 * 1024.0), 2))
        print('    TOTAL internals in MB:', round(total_size / (1024 * 1024.0), 2))
        print('    TOTAL real size in MB:', round(size_of(self) / (1024 * 1024.0), 2))

    def _as_dict(self):
        """
        Return a human readable dictionary representing the index replacing
        token ids and rule ids with their string values and the postings by
        lists. Used for debugging and testing.
        """
        as_dict = {}
        for rid, tok2pos in enumerate(self.postings_by_rid):
            as_dict[self.rules_by_rid[rid].identifier()] = {self.tokens_by_tid[tokid]: list(posts) for tokid, posts in tok2pos.items()}
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

    # Build a candidate junk set of roughly ~ 1/10th the size of of tokens set:
    # we use a curated list of common words as a base. The final length (and
    # also biggest token id) of junk tokens set typically ~ 1200 for about 12K
    # tokens

    junk_max = abs((len(tokens_by_tid) / 11) - len(very_common))

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
                print('!!!License Index FATAL ERROR: small rule: ', rid , 'is all made of junk:', tokens_str(tokens))
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
        # conditional probabilities such that we verify that CANNOT create a
        # distinctive meaningful license string made entirely from junk tokens


        # check that we do not have too many ngrams made entirely of junk
        assert all_junk_ngrams_count < (length * 20)

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
