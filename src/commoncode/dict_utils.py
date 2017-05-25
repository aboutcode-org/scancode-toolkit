
# Copyright (c) 2003-2012 Raymond Hettinger
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
#     The above copyright notice and this permission notice shall be
#     included in all copies or substantial portions of the Software.
#
#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#     EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#     OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#     NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#     HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#     WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#     FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#     OTHER DEALINGS IN THE SOFTWARE.
#
# http://code.activestate.com/recipes/578375-proof-of-concept-for-a-more-space-efficient-faster/
# Created by Raymond Hettinger on Mon, 10 Dec 2012 (MIT)
# Proof-of-concept for a more space-efficient, faster-looping dictionary (Python
# recipe) Save space and improve iteration speed by moving the hash/key/value
# entries to a densely packed array keeping only a sparse array of indices. This
# eliminates wasted space without requiring any algorithmic changes.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import array
import collections
import itertools


# Placeholder constants
FREE = -1
DUMMY = -2



class Dict(collections.MutableMapping):
    """
    Space efficient dictionary with fast iteration and cheap resizes.
    """

    @staticmethod
    def _gen_probes(hashvalue, mask):
        """
        Same sequence of probes used in the current dictionary design.
        """
        PERTURB_SHIFT = 5
        if hashvalue < 0:
            hashvalue = -hashvalue
        i = hashvalue & mask
        yield i
        perturb = hashvalue
        while True:
            i = (5 * i + perturb + 1) & 0xFFFFFFFFFFFFFFFF
            yield i & mask
            perturb >>= PERTURB_SHIFT

    def _lookup(self, key, hashvalue):
        """
        Same lookup logic as currently used in real dicts.
        """
        assert self.filled < len(self.indices)  # At least one open slot
        freeslot = None
        for i in self._gen_probes(hashvalue, len(self.indices) - 1):
            index = self.indices[i]
            if index == FREE:
                return (FREE, i) if freeslot is None else (DUMMY, freeslot)
            elif index == DUMMY:
                if freeslot is None:
                    freeslot = i
            elif (self.keylist[index] is key or
                  self.hashlist[index] == hashvalue
                  and self.keylist[index] == key):
                    return (index, i)

    @staticmethod
    def _make_index(n):
        """
        New sequence of indices using the smallest possible datatype.
        """
        if n <= 2 ** 7: return array.array('b', [FREE]) * n  # signed char
        if n <= 2 ** 15: return array.array('h', [FREE]) * n  # signed short
        if n <= 2 ** 31: return array.array('l', [FREE]) * n  # signed long
        return [FREE] * n  # python integers

    def _resize(self, n):
        """
        Reindex the existing hash/key/value entries.
        Entries do not get moved, they only get new indices.
        No calls are made to hash() or __eq__().
        """
        # round-up to power-of-two
        n = 2 ** n.bit_length()
        self.indices = self._make_index(n)
        for index, hashvalue in enumerate(self.hashlist):
            for i in Dict._gen_probes(hashvalue, n - 1):
                if self.indices[i] == FREE:
                    break
            self.indices[i] = index
        self.filled = self.used

    def clear(self):
        self.indices = self._make_index(8)
        self.hashlist = []
        self.keylist = []
        self.valuelist = []
        self.used = 0
        # used + dummies
        self.filled = 0

    def __getitem__(self, key):
        hashvalue = hash(key)
        index, _i = self._lookup(key, hashvalue)
        if index < 0:
            raise KeyError(key)
        return self.valuelist[index]

    def __setitem__(self, key, value):
        hashvalue = hash(key)
        index, i = self._lookup(key, hashvalue)
        if index < 0:
            self.indices[i] = self.used
            self.hashlist.append(hashvalue)
            self.keylist.append(key)
            self.valuelist.append(value)
            self.used += 1
            if index == FREE:
                self.filled += 1
                if self.filled * 3 > len(self.indices) * 2:
                    self._resize(4 * len(self))
        else:
            self.valuelist[index] = value

    def __delitem__(self, key):
        hashvalue = hash(key)
        index, i = self._lookup(key, hashvalue)
        if index < 0:
            raise KeyError(key)
        self.indices[i] = DUMMY
        self.used -= 1
        # If needed, swap with the last-most entry to avoid leaving a "hole"
        if index != self.used:
            lasthash = self.hashlist[-1]
            lastkey = self.keylist[-1]
            lastvalue = self.valuelist[-1]
            lastindex, j = self._lookup(lastkey, lasthash)
            assert lastindex >= 0 and i != j
            self.indices[j] = index
            self.hashlist[index] = lasthash
            self.keylist[index] = lastkey
            self.valuelist[index] = lastvalue
        # Remove the lastmost entry
        self.hashlist.pop()
        self.keylist.pop()
        self.valuelist.pop()

    def __init__(self, *args, **kwds):
        if not hasattr(self, 'keylist'):
            self.clear()
        self.update(*args, **kwds)

    def __len__(self):
        return self.used

    def __iter__(self):
        return iter(self.keylist)

    def iterkeys(self):
        return iter(self.keylist)

    def keys(self):
        return list(self.keylist)

    def itervalues(self):
        return iter(self.valuelist)

    def values(self):
        return list(self.valuelist)

    def iteritems(self):
        return itertools.izip(self.keylist, self.valuelist)

    def items(self):
        return zip(self.keylist, self.valuelist)

    def __contains__(self, key):
        index, _i = self._lookup(key, hash(key))
        return index >= 0

    def get(self, key, default=None):
        index, _i = self._lookup(key, hash(key))
        return self.valuelist[index] if index >= 0 else default

    def popitem(self):
        if not self.keylist:
            raise KeyError('popitem(): dictionary is empty')
        key = self.keylist[-1]
        value = self.valuelist[-1]
        del self[key]
        return key, value

    def __repr__(self):
        return 'Dict(%r)' % self.items()

    def show_structure(self):
        """
        Diagnostic method.  Not part of the API.
        """
        print('=' * 50)
        print(self)
        print('Indices:', self.indices)
        for i, row in enumerate(zip(self.hashlist, self.keylist, self.valuelist)):
            print(i, row)
        print('-' * 50)


def sparsify(d):
    """
    http://code.activestate.com/recipes/198157-improve-dictionary-lookup-performance/
    Created by Raymond Hettinger on Sun, 4 May 2003 (PSF)
    Reduce average dictionary lookup time by making the internal tables more sparse.
    Improve dictionary sparsity.

    The dict.update() method makes space for non-overlapping keys.
    Giving it a dictionary with 100% overlap will build the same
    dictionary in the larger space.  The resulting dictionary will
    be no more that 1/3 full.  As a result, lookups require less
    than 1.5 probes on average.

    Example:
    >>> sparsify({1: 3, 4: 5})
    {1: 3, 4: 5}
    """
    e = d.copy()
    d.update(e)
    return d


if __name__ == '__main__':
    d = Dict([('timmy', 'red'), ('barry', 'green'), ('guido', 'blue')])
    d.show_structure()
