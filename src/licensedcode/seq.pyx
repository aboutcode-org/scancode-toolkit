# Based off of https://github.com/rapidfuzz/CyDifflib/blob/ef0d1cb49abbdd551e9a27065032fc5317c731fd/src/cydifflib/_initialize.pyx

from collections import namedtuple as _namedtuple

cimport cython
from libcpp.vector cimport vector
from libcpp.algorithm cimport fill, sort as cpp_sort


Match = _namedtuple('Match', 'a b size')


ctypedef struct MatchingBlockQueueElem:
    Py_ssize_t alo
    Py_ssize_t ahi
    Py_ssize_t blo
    Py_ssize_t bhi


ctypedef struct CMatch:
    Py_ssize_t a
    Py_ssize_t b
    Py_ssize_t size


cdef int CMatch_sorter(const CMatch& lhs, const CMatch& rhs):
    if lhs.a != rhs.a:
        return lhs.a < rhs.a
    if lhs.b != rhs.b:
        return lhs.b < rhs.b
    return lhs.size < rhs.size


cdef CMatch find_longest_match(a, b, Py_ssize_t alo, Py_ssize_t ahi, Py_ssize_t blo, Py_ssize_t bhi, b2j, Py_ssize_t len_good, matchables) except *:
    """
    Find longest matching block of a and b in a[alo:ahi] and b[blo:bhi].

    `b2j` is a mapping of b high token ids -> list of position in b
    `len_good` is such that token ids smaller than `_good_good` are treated as
    good, non-junk tokens. `matchables` is a set of matchable positions.
    Positions absent from this set are ignored.

    Return (i,j,k) Match tuple where:
        "i" in the start in "a"
        "j" in the start in "b"
        "k" in the size of the match

    and such that a[i:i+k] is equal to b[j:j+k], where
        alo <= i <= i+k <= ahi
        blo <= j <= j+k <= bhi

    and for all (i',j',k') matchable token positions meeting those conditions,
        k >= k'
        i <= i'
        and if i == i', j <= j'

    In other words, of all maximal matching blocks, return one that starts
    earliest in a, and of all those maximal matching blocks that start earliest
    in a, return the one that starts earliest in b.

    First the longest matching block (aka contiguous substring) is determined
    where no junk element appears in the block. Then that block is extended as
    far as possible by matching other tokens including junk on both sides. So
    the resulting block never matches on junk.

    If no blocks match, return (alo, blo, 0).
    """
    cdef Py_ssize_t besti, bestj, bestsize
    cdef Py_ssize_t i, j, k
    cdef vector[Py_ssize_t] j2len
    cdef vector[Py_ssize_t] newj2len

    besti, bestj, bestsize = alo, blo, 0
    a_len = <size_t>len(a)
    b_len = <size_t>len(b)
    bufsize = max(a_len, b_len) + 1
    j2len.resize(bufsize)
    newj2len.resize(bufsize)
    # find longest junk-free match
    # during an iteration of the loop, j2len[j] = length of longest
    # junk-free match ending with a[i-1] and b[j]
    nothing = []
    for i in range(alo, ahi):
         # we cannot do LCS on junk or non matchable
        cura = a[i]
        if cura < len_good and i in matchables:
            # look at all instances of a[i] in b; note that because
            # b2j has no junk keys, the loop is skipped if a[i] is junk
            for j in b2j.get(a[i], nothing):
                # a[i] matches b[j]
                if j < blo:
                    continue
                if j >= bhi:
                    break
                k = j2len[j] + 1
                newj2len[j + 1] = k
                if k > bestsize:
                    besti = i - k + 1
                    bestj = j - k + 1
                    bestsize = k

            j2len.swap(newj2len)
            fill(newj2len.begin() + blo, newj2len.begin() + bhi + 1, 0)

    fill(j2len.begin() + blo, j2len.begin() + bhi + 1, 0)
    return extend_match(besti, bestj, bestsize, a, b, alo, ahi, blo, bhi, matchables)


cdef CMatch extend_match(besti, bestj, bestsize, a, b, alo, ahi, blo, bhi, matchables):
    """
    Extend a match identifier by (besti, bestj, bestsize) with any matching
    tokens on each end. Return a new CMatch.
    """
    if bestsize:
        while (besti > alo and bestj > blo
               and a[besti - 1] == b[bestj - 1]
               and (besti - 1) in matchables):

            besti -= 1
            bestj -= 1
            bestsize += 1

        while (besti + bestsize < ahi and bestj + bestsize < bhi
               and a[besti + bestsize] == b[bestj + bestsize]
               and (besti + bestsize) in matchables):

            bestsize += 1

    return CMatch(besti, bestj, bestsize)


def match_blocks(a, b, Py_ssize_t a_start, Py_ssize_t a_end, b2j, Py_ssize_t len_good, matchables, *args, **kwargs):
    """
    Return a list of matching block Match triples describing matching
    subsequences of `a` in `b` starting from the `a_start` position in `a` up to
    the `a_end` position in `a`.

    `b2j` is a mapping of b "high" token ids -> list of positions in b, e.g. a
    posting list.

    `len_good` is such that token ids smaller than `len_good` are treated as
    important, non-junk tokens.

    `matchables` is a set of matchable positions. Positions absent from this set
    are ignored.

    Each triple is of the form (i, j, n), and means that a[i:i+n] == b[j:j+n].
    The triples are monotonically increasing in i and in j.  It is also
    guaranteed that adjacent triples never describe adjacent equal blocks.
    Instead adjacent blocks are merged and collapsed in a single block.
    """
    cdef Py_ssize_t i, j, k, i1, j1, k1, i2, j2, k2
    cdef Py_ssize_t alo, ahi, blo, bhi
    cdef vector[MatchingBlockQueueElem] queue
    cdef vector[CMatch] matching_blocks

    # This non-recursive algorithm is using a list as a queue of blocks. We
    # still need to look at and append partial results to matching_blocks in a
    # loop. The matches are sorted at the end.
    queue.push_back(MatchingBlockQueueElem(a_start, a_end, 0, len(b)))
    while not queue.empty():
        elem = queue.back()
        alo, ahi, blo, bhi = elem.alo, elem.ahi, elem.blo, elem.bhi
        queue.pop_back()
        x = find_longest_match(a, b, alo, ahi, blo, bhi, b2j, len_good, matchables)
        i, j, k = x.a, x.b, x.size
        # a[alo:i] vs b[blo:j] unknown
        # a[i:i+k] same as b[j:j+k]
        # a[i+k:ahi] vs b[j+k:bhi] unknown
        if k:   # if k is 0, there was no matching block
            matching_blocks.push_back(x)
            if alo < i and blo < j:
                # there is unprocessed things remaining to the left
                queue.push_back(MatchingBlockQueueElem(alo, i, blo, j))
            if i + k < ahi and j + k < bhi:
                # there is unprocessed things remaining to the right
                queue.push_back(MatchingBlockQueueElem(i+k, ahi, j+k, bhi))

    cpp_sort(matching_blocks.begin(), matching_blocks.end(), &CMatch_sorter)

    # collapse adjacent blocks
    i1 = j1 = k1 = 0
    non_adjacent = []
    for match in matching_blocks:
        i2, j2, k2 = match.a, match.b, match.size
        # Is this block adjacent to i1, j1, k1?
        if i1 + k1 == i2 and j1 + k1 == j2:
            # Yes, so collapse them -- this just increases the length of
            # the first block by the length of the second, and the first
            # block so lengthened remains the block to compare against.
            k1 += k2
        else:
            # Not adjacent.  Remember the first block (k1==0 means it's
            # the dummy we started with), and make the second block the
            # new block to compare against.
            if k1:
                non_adjacent.append((i1, j1, k1))
            i1, j1, k1 = i2, j2, k2
    if k1:
        non_adjacent.append((i1, j1, k1))

    return [Match._make(na) for na in non_adjacent]
