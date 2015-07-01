
# Copyright 2010 Matt Chaput. All rights reserved.
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


class Span(object):
    """
    Represent a Span of tokens or text. Start and end are the offsets that can
    be any measure such as characters, lines or token. 

    Originally derived and modified from Whoosh.
    """

    __slots__ = ('start', 'end')

    def __init__(self, start, end=None):
        if end is None:
            end = start
        assert start <= end
        self.start = start
        self.end = end

    def __repr__(self):
        return 'Span(start=%r, end=%r)' % (self.start, self.end)

    def __eq__(self, span):
        return (self.start == span.start
                and self.end == span.end)

    def __ne__(self, span):
        return self.start != span.start or self.end != span.end

    def __lt__(self, span):
        return self.start < span.start

    def __gt__(self, span):
        return self.start > span.start

    def __hash__(self):
        return hash((self.start, self.end))

    def __len__(self):
        return self.end - self.start

    @staticmethod
    def from_span(span):
        assert all(hasattr(span, attr) for attr in ('start', 'end',))
        return Span(start=span.start, end=span.end)

    @classmethod
    def merge(cls, spans):
        """
        Merge overlapping and touches spans in the given list of spans.
        Return a new list of merged (and possibly unmerged) spans.

        >>> spans = [Span(1,2), Span(3,5), Span(3,6), Span(8,10)]
        >>> new_spans = Span.merge(spans)
        >>> new_spans
        [Span(start=1, end=6), Span(start=8, end=10)]
        """
        spans = spans[:]
        i = 0
        while i < len(spans) - 1:
            here = spans[i]
            j = i + 1
            while j < len(spans):
                there = spans[j]
                if there.start > here.end + 1:
                    break
                if here.touches(there) or here.overlaps(there):
                    here = here.to(there)
                    spans[i] = here
                    del spans[j]
                else:
                    j += 1
            i += 1
        return spans

    def to(self, span):
        """
        Return a new span covering self and other span.

        >>> Span(1,2).to(Span(5))
        Span(start=1, end=5)
        >>> Span(1,2).to(Span(5, 7))
        Span(start=1, end=7)
        >>> Span(12,14).to(Span(5,7))
        Span(start=5, end=14)
        """
        return self.__class__(min(self.start, span.start),
                              max(self.end, span.end))

    def overlaps(self, span):
        """
        Return True if self overlaps with other span.

        >>> Span(1,2).overlaps(Span(5,6))
        False
        >>> Span(5,6).overlaps(Span(5,6))
        True
        >>> Span(4,7).overlaps(Span(5,6))
        True
        >>> Span(4,6).overlaps(Span(5,7))
        True
        """
        return ((self.start >= span.start and self.start <= span.end)
                or (self.end >= span.start and self.end <= span.end)
                or (span.start >= self.start and span.start <= self.end)
                or (span.end >= self.start and span.end <= self.end))

    def surrounds(self, span):
        """
        Return True if self surrounds (without touching) other span.

        >>> Span(4,8).surrounds(Span(4,8))
        False
        >>> Span(4,8).surrounds(Span(5,7))
        True
        """
        return self.start < span.start and self.end > span.end

    def __contains__(self, span):
        return span.is_within(self)

    def is_within(self, span):
        """
        Return True other span is contained in self.

        >>> Span(5,7).is_within(Span(5,7))
        True
        >>> Span(5,7).is_within(Span(4,8))
        True
        >>> Span(3,7).is_within(Span(4,8))
        False
        >>> Span(5,7).is_within(Span(5))
        False
        """
        return self.start >= span.start and self.end <= span.end

    def is_before(self, span):
        return self.end < span.start

    def is_after(self, span):
        return self.start > span.end

    def touches(self, span):
        """
        Return True if self is contiguous with other span.

        >>> Span(5,7).touches(Span(5))
        False
        >>> Span(5,7).touches(Span(5,8))
        False
        >>> Span(5,7).touches(Span(7,8))
        False
        >>> Span(5,7).touches(Span(8,9))
        True
        >>> Span(8,9).touches(Span(5,7))
        True
        """
        return self.start == span.end + 1 or self.end == span.start - 1

    def distance_to(self, span):
        """
        Return the absolute positive distance from self to other span.

        >>> Span(8,9).distance_to(Span(5,7))
        1
        >>> Span(5,7).distance_to(Span(8,9))
        1
        >>> Span(5,7).distance_to(Span(5,7))
        0
        >>> Span(5,7).distance_to(Span(10,12))
        3
        """
        if self.overlaps(span):
            return 0
        elif self.is_before(span):
            return span.start - self.end
        else:
            return self.start - span.end

if __name__ == '__main__':
    import doctest
    doctest.testmod()
