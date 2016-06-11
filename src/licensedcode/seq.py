"""
Based on Python's difflib.py from the 3.X tip:
https://hg.python.org/cpython/raw-file/0a69b1e8b7fe/Lib/difflib.py

Module difflib -- helpers for computing deltas between objects.

Class SequenceMatcher:
    A flexible class for comparing pairs of sequences of any type.
"""
from __future__ import absolute_import
from __future__ import print_function


from collections import namedtuple as _namedtuple

Match = _namedtuple('Match', 'a b size')

class SequenceMatcher:

    """
    SequenceMatcher is a flexible class for comparing pairs of sequences of any
    type, so long as the sequence elements are hashable.  The basic algorithm
    predates, and is a little fancier than, an algorithm published in the late
    1980's by Ratcliff and Obershelp under the hyperbolic name "gestalt pattern
    matching".  The basic idea is to find the longest contiguous matching
    subsequence that contains no "junk" elements.  The same idea is then applied
    recursively to the pieces of the sequences to the left and to the right of
    the matching subsequence.  This does not yield minimal edit sequences, but
    does tend to yield matches that "look right" to people.

    SequenceMatcher tries to compute a diff between two sequences. The
    fundamental notion is the longest *contiguous* & junk- free matching
    subsequence.  That's what catches peoples' eyes.

    Note that the last tuple returned by .get_matching_blocks() is always a
    dummy, (len(a), len(b), 0), and this is the only case in which the last
    tuple element (number of elements matched) is 0.

    Timing:  Basic R-O is cubic time worst case and quadratic time expected
    case.  SequenceMatcher is quadratic time for the worst case and has
    expected-case behavior dependent in a complicated way on how many
    elements the sequences have in common; best case time is linear.

    Methods:

    __init__(b='', len_junk=0)
        Construct a SequenceMatcher.

    find_longest_match(a, alo, ahi, blo, bhi)
        Find longest matching block in a[alo:ahi] and b[blo:bhi].

    get_matching_blocks(a)
        Return list of triples describing matching subsequences.
    """

    def __init__(self, b, len_junk=0):
        """
        Construct a SequenceMatcher.
        arg b is the second of two sequences to be compared.
        """

        # Members:
        # b
        #      second sequence; differences are computed as "what do
        #      we need to do to 'a' to change it into 'b'?"
        # b2j
        #      for x in b, b2j[x] is a list of the indices (into b)
        #      at which x appears; junk elements do not appear
        # len_junk
        #      The value that defines junk elements: elements less than len_junk
        #      are junk non-junk elements are greater than or equal tolen_junk

        self.b = b
        self.len_b = len(self.b)
        self.len_junk = len_junk

        # For each non-junk element x in b, set b2j[x] to a list of the indices
        # in b where x appears; the indices are in increasing order; Since junk
        # elements don't show up in this map, this stops the central
        # find_longest_match method from starting any matching block at a junk
        # element ...

        self.b2j = b2j = {}

        for i, elt in enumerate(b):
            if elt < self.len_junk:
                continue
            # FIXME: would a default dict be faster?
            indices = b2j.setdefault(elt, [])
            indices.append(i)

    def find_longest_match(self, a, alo, ahi, blo, bhi, matchables):
        """
        Find longest matching block of and self.b in a[alo:ahi] and b[blo:bhi].

        matchables is a set of matchable positions.

        Return (i,j,k) such that a[i:i+k] is equal to b[j:j+k], where
            alo <= i <= i+k <= ahi
            blo <= j <= j+k <= bhi
        and for all (i',j',k') meeting those conditions,
            k >= k'
            i <= i'
            and if i == i', j <= j'

        In other words, of all maximal matching blocks, return one that
        starts earliest in a, and of all those maximal matching blocks that
        start earliest in a, return the one that starts earliest in b.

        >>> s = SequenceMatcher(" abcd abcd")
        >>> s.find_longest_match(" abcd", 0, 5, 0, 9, range(len(" abcd")))
        Match(a=0, b=0, size=5)
        >>> s.find_longest_match("abcd", 0, 4, 0, 9, range(len(" abcd")))
        Match(a=0, b=1, size=4)

        First the longest matching block is determined as above where no junk
        element appears in the block.  Then that block is extended as far as
        possible by matching (only) junk elements on both sides.  So the
        resulting block never matches on junk except as identical junk happens
        to be adjacent to an "interesting" match.

        If no blocks match, return (alo, blo, 0).

        >>> s = SequenceMatcher("c")
        >>> s.find_longest_match("ab", 0, 2, 0, 1, range(len("ab")))
        Match(a=0, b=0, size=0)
        """

        # CAUTION:  stripping common prefix or suffix would be incorrect.
        # E.g.,
        #    ab
        #    acab
        # Longest matching block is "ab", but if common prefix is
        # stripped, it's "a" (tied with "b").  UNIX(tm) diff does so
        # strip, so ends up claiming that ab is changed to acab by
        # inserting "ca" in the middle.  That's minimal but unintuitive:
        # "it's obvious" that someone inserted "ac" at the front.
        # Windiff ends up at the same place as diff, but by pairing up
        # the unique 'b's and then matching the first two 'a's.

        len_junk = self.len_junk
        b, b2j = self.b, self.b2j
        besti, bestj, bestsize = alo, blo, 0
        b2j_get = b2j.get

        # find longest junk-free match
        # during an iteration of the loop, j2len[j] = length of longest
        # junk-free match ending with a[i-1] and b[j]
        j2len = {}
        nothing = []
        for i in range(alo, ahi):
            if not i in matchables:
                continue
            # look at all instances of a[i] in b; note that because
            # b2j has no junk keys, the loop is skipped if a[i] is junk
            j2lenget = j2len.get
            newj2len = {}
            for j in b2j_get(a[i], nothing):
                # a[i] matches b[j]
                if j < blo:
                    continue
                if j >= bhi:
                    break
                k = newj2len[j] = j2lenget(j - 1, 0) + 1
                if k > bestsize:
                    besti, bestj, bestsize = i - k + 1, j - k + 1, k
            j2len = newj2len

        
        # Extend the best by non-junk elements on each end.
        while (besti > alo and bestj > blo and
               b[bestj - 1] >= len_junk and
               (besti - 1) in matchables and
               a[besti - 1] == b[bestj - 1]):
            besti, bestj, bestsize = besti - 1, bestj - 1, bestsize + 1

        while (besti + bestsize < ahi and bestj + bestsize < bhi and
               b[bestj + bestsize] >= len_junk and
              (besti + bestsize) in matchables and
              a[besti + bestsize] == b[bestj + bestsize]):
            bestsize += 1

        if bestsize:
            # if have a non-empty interesting match, append any matching on each side.
            while (besti > alo and bestj > blo and
                  #b[bestj - 1] < len_junk and
                  (besti - 1) in matchables and
                  a[besti - 1] == b[bestj - 1]):
                besti, bestj, bestsize = besti - 1, bestj - 1, bestsize + 1
      
            while (besti + bestsize < ahi and bestj + bestsize < bhi and
                  #b[bestj + bestsize] < len_junk and
                  (besti + bestsize) in matchables and
                  a[besti + bestsize] == b[bestj + bestsize]):
                bestsize = bestsize + 1

        return Match(besti, bestj, bestsize)

    def get_matching_blocks(self, a, starta=0, matchables=()):
        """
        Return list of triples describing matching subsequences of a in self.b
        starting at starta index.

        matchables is a set of matchable positions in a and indexed matched in a
        must exists in matchables.

        Each triple is of the form (i, j, n), and means that
        a[i:i+n] == b[j:j+n].  The triples are monotonically increasing in
        i and in j.  New in Python 2.5, it's also guaranteed that if
        (i, j, n) and (i', j', n') are adjacent triples in the list, and
        the second is not the last triple in the list, then i+n != i' or
        j+n != j'.  IOW, adjacent triples never describe adjacent equal
        blocks.

        >>> s = SequenceMatcher("abcd")
        >>> list(s.get_matching_blocks("abxcd"))
        [Match(a=0, b=0, size=2), Match(a=3, b=2, size=2)]
        """
        la = len(a)
        lb = self.len_b

        # find the first matchable index in a
        _starta=-1
        for _starta, _atok in enumerate(a, starta):
            if starta in matchables:
                break
        if _starta < 0:
            return []
        starta = _starta

        # This is most naturally expressed as a recursive algorithm, but
        # at least one user bumped into extreme use cases that exceeded
        # the recursion limit on their box.  So, now we maintain a list
        # ('queue`) of blocks we still need to look at, and append partial
        # results to `matching_blocks` in a loop; the matches are sorted
        # at the end.

        startb = 0
        queue = [(starta, la, startb, lb)]
        queue_append = queue.append
        queue_pop = queue.pop
        matching_blocks = []
        matching_blocks_append = matching_blocks.append
        find_longest_match = self.find_longest_match
        while queue:
            alo, ahi, blo, bhi = queue_pop()
            i, j, k = x = find_longest_match(a, alo, ahi, blo, bhi, matchables)
            # a[alo:i] vs b[blo:j] unknown
            # a[i:i+k] same as b[j:j+k]
            # a[i+k:ahi] vs b[j+k:bhi] unknown
            if k:  # if k is 0, there was no matching block
                matching_blocks_append(x)
                if alo < i and blo < j:
                    queue_append((alo, i, blo, j))
                if i + k < ahi and j + k < bhi:
                    queue_append((i + k, ahi, j + k, bhi))

        matching_blocks.sort()
        # FIXME: do we care for adjacent equal blocks?
 
        # It's possible that we have adjacent equal blocks in the
        # matching_blocks list now.  Starting with 2.5, this code was added
        # to collapse them.
#         i1 = j1 = k1 = 0
#         non_adjacent = []
#         non_adjacent_append = non_adjacent.append
#         for i2, j2, k2 in matching_blocks:
#             # Is this block adjacent to i1, j1, k1?
#             if i1 + k1 == i2 and j1 + k1 == j2:
#                 # Yes, so collapse them -- this just increases the length of
#                 # the first block by the length of the second, and the first
#                 # block so lengthened remains the block to compare against.
#                 k1 += k2
#             else:
#                 # Not adjacent.  Remember the first block (k1==0 means it's
#                 # the dummy we started with), and make the second block the
#                 # new block to compare against.
#                 if k1:
#                     non_adjacent_append((i1, j1, k1))
#                 i1, j1, k1 = i2, j2, k2
#         if k1:
#             non_adjacent.append((i1, j1, k1))

        return map(Match._make, matching_blocks)