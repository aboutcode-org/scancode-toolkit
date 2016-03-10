#
# Copyright (c) 2010 Matt Chaput. All rights reserved.
# Modifications by nexB Copyright 2016 nexB Inc. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY MATT CHAPUT ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL MATT CHAPUT OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Matt Chaput.

from __future__ import absolute_import

from functools import total_ordering
from itertools import count
from itertools import groupby
from itertools import izip


@total_ordering
class Span(object):
    """
    Represent a span from start to end where start and end are positive integers. A
    span includes both items represented by start and end. 

    A span is neither a slice nor an interval. 
    Instead a span represents the start and end indexes (inclusive) of a
    sequence slice. Slices do not include the end index.
    
    Typically used to represent a range of contiguous tokens positions.

    Originally derived and modified from Whoosh.
    """
    __slots__ = 'start', 'end'

    def __init__(self, start, end=None):
        """
        Create a new Span from start to end. end defaults to start if not
        provided.
        """
        self.start = start
        self.end = end is not None and end or start

    def __repr__(self):
        return 'Span(%d, %d)' % (self.start, self.end)

    def __eq__(self, other):
        return isinstance(other, Span) and self.start == other.start and self.end == other.end

    def __lt__(self, other):
        # FIXME: we should consider the length and end too for deciding on ordering
        return self.start < other.start

    def __hash__(self):
        return hash((self.start, self.end))

    def __len__(self):
        """
        >>> len(Span(1, 2))
        2
        >>> len(Span(0, 0))
        1
        >>> len(Span(0, 10))
        11
        >>> len(Span(4, 6))
        3
        """
        return (self.end - self.start) + 1

    def __iter__(self):
        """
        Return an iterator on start and end. 
        >>> [x for x in Span(1, 8)]
        [1, 8]
        >>> it = iter(Span(1, 8))
        >>> it.next()
        1
        >>> it.next()
        8
        >>> try:
        ...    it.next()
        ... except StopIteration:
        ...    pass
        """
        yield self.start
        yield self.end

    def __contains__(self, other):
        """
        Return True if self contains other span (span can also be a single int).

        >>> Span(5, 7) in Span(5, 7)
        True
        >>> Span(5, 8) in Span(5, 7)
        False
        >>> 6 in Span(4, 8)
        True
        >>> 2 in Span(4, 8)
        False
        >>> 8 in Span(4, 8)
        True
        >>> 9 in Span(4, 8)
        False
        """
        if isinstance(other, int):
            return self.start <= other <= self.end
        return isinstance(other, Span) and self.start <= other.start and other.end <= self.end

    @staticmethod
    def from_ints(ints):
        """
        Return a iterator of spans from an iterable of ints. Contiguous ints are
        grouped in a single span.
        >>> list(Span.from_ints([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]))
        [Span(1, 12)]
        >>> list(Span.from_ints([1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12]))
        [Span(1, 3), Span(5, 12)]
        >>> list(Span.from_ints([0, 2, 3, 5, 6, 7, 8, 9, 10, 11, 13]))
        [Span(0, 0), Span(2, 3), Span(5, 11), Span(13, 13)]
        """
        ints = sorted(set(ints))
        groups = (list(group) for _, group in groupby(ints, lambda group, c=count(): next(c) - group))
        return (Span(group[0], group[-1]) for group in groups)

    @staticmethod
    def merge(spans):
        """
        Merge overlapping and touching spans in the given iterable of spans.
        Return a new list of merged spans if they can be merged. Spans that
        cannot be merged are returned as-is.

        The maximal merge is always returned, eventually resulting in a single
        span if all spans could be merged.

        >>> spans = [Span(1, 2), Span(3, 5), Span(3, 6), Span(8, 10)]
        >>> Span.merge(spans)
        [Span(1, 6), Span(8, 10)]

        >>> spans = [Span(1, 2), Span(4, 5), Span(7, 8), Span(11, 12)]
        >>> Span.merge(spans)
        [Span(1, 2), Span(4, 5), Span(7, 8), Span(11, 12)]

        >>> spans = [Span(1, 2), Span(5, 6), Span(7, 8), Span(12, 13)]
        >>> Span.merge(spans)
        [Span(1, 2), Span(5, 8), Span(12, 13)]
        """
        return list(Span.from_ints(Span.ranges(spans)))

    @staticmethod
    def merge_two(span1, span2):
        """
        Return a merged Span covering span1 and span2 if they are mergeable or None otherwise.

        `bridge` is a integer to merge (aka. "bridge") two non-touching non-
        overlapping spans that are separated by up to `bridge` distance.

        >>> Span.merge_two(Span(1, 2), Span(3, 5))
        Span(1, 5)

        >>> Span.merge_two(Span(1, 4), Span(3, 5))
        Span(1, 5)

        >>> Span.merge_two(Span(5, 6), Span(3, 5))
        Span(3, 6)

        >>> Span.merge_two(Span(3, 6), Span(8, 10))
        """
        merged = Span.merge([span1, span2])
        if len(merged) == 2:
            return
        else:
            return merged[0]

    @staticmethod
    def fuse(spans):
        """
        Return a new span covering all the spans in the given list of spans.
        The new Span is based on the smallest start and the biggest end.

        >>> spans = [Span(1, 2), Span(3, 5), Span(3, 6), Span(8, 10)]
        >>> Span.fuse(spans)
        Span(1, 10)

        >>> spans = [Span(1, 2), Span(4, 5), Span(7, 8), Span(11, 12)]
        >>> Span.fuse(spans)
        Span(1, 12)

        >>> spans = [Span(1), Span(4), Span(7), Span(11, 12)]
        >>> Span.fuse(spans)
        Span(1, 12)
        """
        starts, ends = izip(*((s.start, s.end) for s in spans))
        return Span(min(starts), max(ends))

    def to(self, span):
        """
        Return a new span covering self and other span.

        >>> Span(1, 2).to(Span(5))
        Span(1, 5)
        >>> Span(1, 2).to(Span(5, 7))
        Span(1, 7)
        >>> Span(12, 14).to(Span(5, 7))
        Span(5, 14)
        """
        return Span(min(self.start, span.start), max(self.end, span.end))

    def overlap(self, span):
        """
        Return True if self overlaps with other span.

        >>> Span(1, 2).overlap(Span(5, 6))
        False
        >>> Span(5, 6).overlap(Span(5, 6))
        True
        >>> Span(4, 7).overlap(Span(5, 6))
        True
        >>> Span(4, 6).overlap(Span(5, 7))
        True
        >>> Span(4, 5).overlap(Span(6, 7))
        False
        """
        # FIXME: this test is obscure
        return ((self.start >= span.start and self.start <= span.end)
             or (self.end >= span.start and self.end <= span.end)
             or (span.start >= self.start and span.start <= self.end)
             or (span.end >= self.start and span.end <= self.end))

    def surround(self, span):
        """
        Return True if self surrounds (without touching) other span.

        >>> Span(4, 8).surround(Span(4, 8))
        False
        >>> Span(4, 8).surround(Span(5, 7))
        True
        """
        return self.start < span.start and self.end > span.end

    def is_before(self, span):
        return self.end < span.start

    def is_before_or_touch(self, span):
        return self.end <= span.start

    def is_after(self, span):
        return self.start > span.end

    def is_after_or_touch(self, span):
        return self.start >= span.end

    def touch(self, span):
        """
        Return True if self is contiguous with other span without overlap.

        >>> Span(5, 7).touch(Span(5))
        False
        >>> Span(5, 7).touch(Span(5, 8))
        False
        >>> Span(5, 7).touch(Span(7, 8))
        False
        >>> Span(5, 7).touch(Span(8, 9))
        True
        >>> Span(8, 9).touch(Span(5, 7))
        True
        """
        return self.start == span.end + 1 or self.end == span.start - 1

    def distance_to(self, span):
        """
        Return the absolute positive distance from self to other span.
        Touching and overlapping spans have a zero distance.

        >>> Span(8, 9).distance_to(Span(5, 7))
        0
        >>> Span(5, 7).distance_to(Span(8, 9))
        0
        >>> Span(5, 6).distance_to(Span(8, 9))
        2
        >>> Span(5, 7).distance_to(Span(5, 7))
        0
        >>> Span(4, 6).distance_to(Span(5, 7))
        0
        >>> Span(5, 7).distance_to(Span(10, 12))
        3
        >>> Span(1, 2).distance_to(Span(4, 52))
        2
        """
        if self.overlap(span) or self.touch(span):
            return 0
        elif self.is_before(span):
            return span.start - self.end
        else:
            return self.start - span.end

    def dilate(self, count=0):
        """
        Return a new "dilated" Span by extending it left and right with the
        provided positive count int. Add count to end and subtract count from
        start. start is never less than zero.

        >>> Span(8, 9).dilate(3)
        Span(5, 12)
        >>> Span(5, 6).dilate(6)
        Span(0, 12)
        """
        if not count:
            return Span(self.start, self.end)
        return Span(max([0, self.start - count]), self.end + count)


    def range(self):
        """
        Return a range of integers representing this span.

        >>> Span(8, 9).range()
        [8, 9]
        >>> Span(0, 4).range()
        [0, 1, 2, 3, 4]
        >>> Span(1, 1).range()
        [1]
        """
        return range(self.start, self.end + 1)

    @staticmethod
    def ranges(spans):
        """
        Return a set of integers representing the ranges of a spans sequence.
        """
        spans_range = set()
        for span in spans:
            spans_range.update(span.range())
        return spans_range


def contained(spans1, spans2):
    """
    Return True if all spans from spans2 list are contained in some span of
    spans1 list.
    """
    for span2 in spans2:
        if not any(span2 in span for span in spans1):
            return False
    return True
