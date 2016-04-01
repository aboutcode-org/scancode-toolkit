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

from __future__ import absolute_import, division, print_function

from itertools import count
from itertools import groupby
from itertools import imap


class Span(set):
    """
    Represent a set of integers with a start and end.
    Typically used to represent a range of contiguous tokens positions.
    Originally derived and heavily modified from Whoosh.
    """
    def __init__(self, *args):
        """
        Create a new Span from a start and end ints or an iterable of ints. 

        First form:
        Span(start int, end int) : the span is initialized with a range(start, end+1)

        Second form:
        Span(iterable of ints) : the span is initialized with the iterable 
        
        Spans are hashable and immutable.

        For example:
        >>> s = Span([1, 2])
        >>> s.start
        1
        >>> s.end
        2
        >>> s
        Span([1, 2])

        >>> s = Span(1, 3)
        >>> s.start
        1
        >>> s.end
        3
        >>> s
        Span([1, 2, 3])

        >>> s = Span([6, 5, 1, 2])
        >>> s.start
        1
        >>> s.end
        6
        >>> s
        Span([1, 2, 5, 6])
        >>> len(s)
        4

        >>> Span([5, 6, 7, 8, 9, 10 ,11, 12]) == Span([5, 6, 7, 8, 9, 10 ,11, 12])
        True
        >>> hash(Span([5, 6, 7, 8, 9, 10 ,11, 12])) == hash(Span([5, 6, 7, 8, 9, 10 ,11, 12]))
        True
        >>> hash(Span([5, 6, 7, 8, 9, 10 ,11, 12])) == hash(Span(5, 12))
        True
        """
        if not args:
            raise TypeError('Excepted at least one argument')
            # super(Span, self).__init__()
        else:

            len_args = len(args)
            if len_args == 2:
                for x in args:
                    assert isinstance(x, int), 'All args %r should be int but was:%r' % (args, x)
                iterable = range(args[0], args[1] + 1)
            elif len_args == 1:
                # assume an iterable
                iterable = list(args[0])
                for x in iterable:
                    assert isinstance(x, int), 'All args %r should be int but was:%r' % (iterable, x)

            super(Span, self).__init__(iterable)

    def __hash__(self):
        return hash(frozenset(self))

    def __repr__(self):
        return 'Span(%r)' % sorted(self)

    def union(self, *args):
        return Span(set.union(self, *args))

    @property
    def start(self):
        return min(self)

    @property
    def end(self):
        return max(self)

    def magnitude(self):
        """
        Return the length of the actual maximal length represented by this span
        ignoring gaps. The magnitude is the same as the length for a contiguous
        span. It is based on the start and end of the span.

        For example:
        >>> Span([4, 8]).magnitude()
        5
        >>> len(Span([4, 8]))
        2
        >>> len(Span([4, 5, 6, 7, 8]))
        5
        >>> Span([4, 5, 6, 7, 8]).magnitude()
        5
        >>> Span([0]).magnitude()
        1
        >>> Span([0]).magnitude()
        1
        """
        return self.end - self.start + 1

    def __contains__(self, other):
        """
        Return True if self contains other (where other is a Span, an int or
        an ints set).

        For example:
        >>> Span([5, 7]) in Span(5, 7)
        True
        >>> Span([5, 8]) in Span([5, 7])
        False
        >>> 6 in Span([4, 5, 6, 7, 8])
        True
        >>> 2 in Span([4, 5, 6, 7, 8])
        False
        >>> 8 in Span([4, 8])
        True
        >>> 5 in Span([4, 8])
        False
        >>> set([4, 5]) in Span([4, 5, 6, 7, 8])
        True
        >>> set([9]) in Span([4, 8])
        False
        """
        if isinstance(other, (Span, set, frozenset,)):
            return self.issuperset(other)

        if isinstance(other, int):
            return super(Span, self).__contains__(other)

    @staticmethod
    def from_ints(ints):
        """
        Return a iterable of Spans from an iterable of ints. Contiguous ints are
        grouped in a single Span.
        >>> list(Span.from_ints([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]))
        [Span([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])]
        >>> list(Span.from_ints([1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12]))
        [Span([1, 2, 3]), Span([5, 6, 7, 8, 9, 10, 11, 12])]
        >>> list(Span.from_ints([0, 2, 3, 5, 6, 7, 8, 9, 10, 11, 13]))
        [Span([0]), Span([2, 3]), Span([5, 6, 7, 8, 9, 10, 11]), Span([13])]
        """
        ints = sorted(set(ints))
        groups = (group for _, group in groupby(ints, lambda group, c=count(): next(c) - group))
        return imap(Span, groups)

    @staticmethod
    def merge(spans):
        """
        Return a list of merged spans from a list of spans merging overlapping
        and touching spans in the given iterable of spans. Spans that cannot be
        merged are returned as-is.

        The maximal merge is always returned, eventually resulting in a single
        span if all spans can merge.

        For example:
        >>> spans = [Span([5, 6, 7, 8, 9, 10]), Span([1, 2]), Span([3, 4, 5]), Span([3, 4, 5, 6]), Span([8, 9, 10])]
        >>> Span.merge(spans)
        [Span([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])]

        >>> spans = [Span([1, 2]), Span([3, 4, 5]), Span([3, 4, 5, 6]), Span([8, 9, 10])]
        >>> Span.merge(spans)
        [Span([1, 2, 3, 4, 5, 6]), Span([8, 9, 10])]

        >>> spans = [Span([1, 2]), Span([4, 5]), Span([7, 8]), Span([11, 12])]
        >>> Span.merge(spans)
        [Span([1, 2]), Span([4, 5]), Span([7, 8]), Span([11, 12])]

        >>> spans = [Span([1, 2]), Span([5, 6]), Span([7, 8]), Span([12, 13])]
        >>> Span.merge(spans)
        [Span([1, 2]), Span([5, 6, 7, 8]), Span([12, 13])]

        # This fails for sparse spans with this implmentation:
        # When spans are not touching they do not merge:
        # >>> Span.merge([Span([63, 64]), Span([58, 58])])
        # [Span([58]), Span([63, 64])]
        # 
        # Overlapping spans are merged:
        # >>> spans = [Span([12, 17, 24]), Span([15, 16, 17, 35]), Span([58, 58]), Span([63, 64])]
        # >>> Span.merge(spans)
        # [Span([12, 15, 16, 17, 24, 35]), Span([58]), Span([63, 64])]
        """
        return list(Span.from_ints(Span.union(*spans)))

    # TODO: check which of merge or merge2 is faster
    @staticmethod
    def merge2(spans, bridge=0):
        """
        Merge overlapping and touches spans in the given list of spans. Return a
        new list of merged mergeable spans and not-merged un-mergeable spans.

        `bridge` is a integer to merge two non-touching non-overlapping spans
        that are separated by up to `bridge` distance.

        For example:
        >>> spans = [Span([1, 2]), Span([3, 4, 5]), Span([3, 4, 5, 6]), Span([8, 10])]
        >>> Span.merge2(spans)
        [Span([1, 2, 3, 4, 5, 6]), Span([8, 10])]
 
        >>> spans = [Span([1, 2]), Span([4, 5]), Span([7,8]), Span([11, 12])]
        >>> Span.merge2(spans, bridge=1)
        [Span([1, 2, 4, 5, 7, 8]), Span([11, 12])]
 
        >>> spans = [Span([1, 2]), Span([5, 6]), Span([7, 8]), Span([12, 13])]
        >>> Span.merge2(spans, bridge=2)
        [Span([1, 2, 5, 6, 7, 8]), Span([12, 13])]

        >>> spans = [Span([5, 6, 7, 8, 9, 10]), Span([1, 2]), Span([3, 4, 5]), Span([3, 4, 5, 6]), Span([8, 9, 10])]
        >>> Span.merge2(spans)
        [Span([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])]

        >>> spans = [Span([1, 2]), Span([3, 4, 5]), Span([3, 4, 5, 6]), Span([8, 9, 10])]
        >>> Span.merge2(spans)
        [Span([1, 2, 3, 4, 5, 6]), Span([8, 9, 10])]

        >>> spans = [Span([1, 2]), Span([4, 5]), Span([7, 8]), Span([11, 12])]
        >>> Span.merge2(spans)
        [Span([1, 2]), Span([4, 5]), Span([7, 8]), Span([11, 12])]

        >>> spans = [Span([1, 2]), Span([5, 6]), Span([7, 8]), Span([12, 13])]
        >>> Span.merge2(spans)
        [Span([1, 2]), Span([5, 6, 7, 8]), Span([12, 13])]

        When spans are not touching they do not merge:
        >>> Span.merge2([Span([63, 64]), Span([58, 58])])
        [Span([58]), Span([63, 64])]

        Overlapping spans are merged:
        >>> spans = [Span([12, 17, 24]), Span([15, 16, 17, 35]), Span([58, 58]), Span([63, 64])]
        >>> Span.merge2(spans)
        [Span([12, 15, 16, 17, 24, 35]), Span([58]), Span([63, 64])]
        """
        spans = Span.sort(spans)
        i = 0
        while i < len(spans) - 1:
            here = spans[i]
            j = i + 1
            while j < len(spans):
                there = spans[j]
                if there.start > here.end + 1 + bridge:
                    break
                if here.touch(there) or here.overlap(there) or here.distance_to(there) <= bridge + 1:
                    here = here.union(there)
                    spans[i] = here
                    del spans[j]
                else:
                    j += 1
            i += 1
        return spans

    def overlap(self, other):
        """
        Return the count of overlapping items between this span and another span.

        For example:
        >>> Span([1, 2]).overlap(Span([5, 6]))
        0
        >>> Span([5, 6]).overlap(Span([5, 6]))
        2
        >>> Span([4, 5, 6, 7]).overlap(Span([5, 6]))
        2
        >>> Span([4, 5, 6]).overlap(Span([5, 6, 7]))
        2
        >>> Span([4, 5, 6]).overlap(Span([6]))
        1
        >>> Span([4, 5]).overlap(Span([6, 7]))
        0
        """
        return len(self & other)

    def surround(self, other):
        """
        Return True if this span surrounds (contains without touching) another span.

        For example:
        >>> Span([4, 8]).surround(Span([4, 8]))
        False
        >>> Span([4, 5, 6, 7, 8]).surround(Span([5, 6, 7]))
        True
        """
        return self.issuperset(other) and self.start < other.start and self.end > other.end

    def is_before(self, other):
        return self.end < other.start

    def is_before_or_touch(self, other):
        return self.end <= other.start

    def is_after(self, other):
        return self.start > other.end

    def is_after_or_touch(self, other):
        return self.start >= other.end

    def touch(self, other):
        """
        Return True if self sequence is contiguous with other span without overlap.

        For example:
        >>> Span([5, 7]).touch(Span([5]))
        False
        >>> Span([5, 7]).touch(Span([5, 8]))
        False
        >>> Span([5, 7]).touch(Span([7, 8]))
        False
        >>> Span([5, 7]).touch(Span([8, 9]))
        True
        >>> Span([8, 9]).touch(Span([5, 7]))
        True
        """
        return self.start == other.end + 1 or self.end == other.start - 1

    def distance_to(self, other):
        """
        Return the absolute positive distance from this span to other span.
        Touching and overlapping spans have a zero distance.

        For example:
        >>> Span([8, 9]).distance_to(Span([5, 7]))
        0
        >>> Span([5, 7]).distance_to(Span([8, 9]))
        0
        >>> Span([5, 6]).distance_to(Span([8, 9]))
        2
        >>> Span([5, 7]).distance_to(Span([5, 7]))
        0
        >>> Span([4, 5, 6]).distance_to(Span([5, 6, 7]))
        0
        >>> Span([5, 7]).distance_to(Span([10, 12]))
        3
        >>> Span([1, 2]).distance_to(Span(range(4, 52)))
        2
        """
        if self.overlap(other) or self.touch(other):
            return 0
        elif self.is_before(other):
            return other.start - self.end
        else:
            return self.start - other.end

    def dilate(self, count=0):
        """
        Return a new "dilated" Span by extending this span left and right with
        the provided positive count int. Add count ints at start and end. start
        is never less than zero.

        For example:
        >>> Span([8, 9]).dilate(3)
        Span([5, 6, 7, 8, 9, 10, 11, 12])

        >>> Span([2, 3]).dilate(6)
        Span([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        """
        if not count:
            return Span(self)

        new_items = set.union(
            self,
            set(range(max([0, self.start - count]), self.start)),
            set(range(self.end + 1, self.end + 1 + count))
        )
        return Span(new_items)

    def range(self, offset=0):
        """
        Return a sorted range of integers representing this span.
        Add offset to each item.

        For example:
        >>> Span([8, 9]).range()
        [8, 9]
        >>> Span(range(5)).range()
        [0, 1, 2, 3, 4]
        >>> Span([1]).range()
        [1]
        >>> Span(range(5)).range(1)
        [1, 2, 3, 4, 5]
        """
        return sorted(i + offset for i in self)

    @staticmethod
    def sort(spans):
        """
        Return a sorted list of spans.
        The primary sort is on start. The secondary sort is on length.
        For two spans with same start positions, the longer span will sort first.

        For example:
        >>> spans = [Span([5, 6, 7, 8, 9, 10]), Span([1, 2]), Span([3, 4, 5]), Span([3, 4, 5, 6]), Span([8, 9, 10])]
        >>> Span.sort(spans)
        [Span([1, 2]), Span([3, 4, 5, 6]), Span([3, 4, 5]), Span([5, 6, 7, 8, 9, 10]), Span([8, 9, 10])]

        >>> spans = [Span([1, 2]), Span([3, 4, 5]), Span([3, 4, 5, 6]), Span([8, 9, 10])]
        >>> Span.sort(spans)
        [Span([1, 2]), Span([3, 4, 5, 6]), Span([3, 4, 5]), Span([8, 9, 10])]
 
        >>> spans = [Span([1, 2]), Span([4, 5]), Span([7, 8]), Span([11, 12])]
        >>> Span.sort(spans)
        [Span([1, 2]), Span([4, 5]), Span([7, 8]), Span([11, 12])]
 
        >>> spans = [Span([1, 2]), Span([7, 8]), Span([5, 6]), Span([12, 13])]
        >>> Span.sort(spans)
        [Span([1, 2]), Span([5, 6]), Span([7, 8]), Span([12, 13])]
            
        """
        key = lambda s: (s.start, -len(s),)
        return sorted(spans, key=key)

    def resemblance(self, other):
        """
        Return a resemblance coefficient as a float between 0 and 1.
        0 means the spans are completely different and 1 identical. 
        The resemblance is the Jaccard coefficient between the two span.

        >>> Span([8, 9]).range()
        [8, 9]
        >>> Span(range(5)).range()
        [0, 1, 2, 3, 4]
        >>> Span([1]).range()
        [1]
        >>> Span(range(5)).range(1)
        [1, 2, 3, 4, 5]
        """
        if self.isdisjoint(other):
            return 0

        if self == other:
            return 1

        intersection = self & other
        union = self | other
        resemblance = len(intersection) / len(union)
        return resemblance

    def containment(self, other):
        """
        Return a containment coefficient as a float between 0 and 1.

        >>> Span([8, 9]).range()
        [8, 9]
        >>> Span(range(5)).range()
        [0, 1, 2, 3, 4]
        >>> Span([1]).range()
        [1]
        >>> Span(range(5)).range(1)
        [1, 2, 3, 4, 5]
        """
        intersection = self & other
        union = self | other
        resemblance = len(intersection) / len(union)
        return resemblance
