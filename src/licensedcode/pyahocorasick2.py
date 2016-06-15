# -*- coding: utf-8 -*-

# Copyright (c) 2011-2014 Wojciech Mula
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above
#   copyright notice, this list of conditions and the following
#   disclaimer in the documentation and/or other materials
#   provided with the distribution.
# * Neither the name of the Wojciech Mula nor the names of its
#   contributors may be used to endorse or promote products
#   derived from this software without specific prior written
#   permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

"""
Aho-Corasick string search algorithm.

Author    : Wojciech Mula, wojciech_mula@poczta.onet.pl
WWW       : http://0x80.pl
License   : public domain
"""

from __future__ import print_function, absolute_import

from collections import deque


# used to distinguish from None
NIL = -1

def TrieNode(key):
    """
    Build a new node as a simple list: [key, value, fail, kids]
    # keyitem, must hashable. For strings this is a character. For sequence,
    # an element of the sequence.
    # value associated with this node
    # failure link used by Aho-Corasick automaton
    """
    # [keyitem:0, value:1, fail:2, _kids:3]
    return [key, -1, -1, {}]

# attributes index in the node
_key = 0
_val = 1
_fail = 2
_kids = 3


class Trie(object):
    """
    Trie/Aho-Corasick automaton.
    """

    def __init__(self, items_range):
        """
        Initialize a Trie for up to `items_range` number of tokens.
        """
        self.root = TrieNode([])
        self.items_range = items_range

    def __get_node(self, seq):
        """
        Return a final node or None if the trie does not contain the sequence of
        items.
        """
        node = self.root
        for key in seq:
            try:
                # note: kids may be None
                node = node[_kids][key]
            except KeyError:
                return None
        return node

    def get(self, seq, default=-1):
        """
        Return the value associated with the sequence of items. If the sequence
        of items is not present in trie return the `default` if provided or
        raise a KeyError if not provided.
        # FIXME: should match the dict semantics.
        """
        node = self.__get_node(seq)
        value = -1
        if node:
            value = node[_val]

        if value == -1:
            if default == -1:
                raise KeyError()
            else:
                return default
        else:
            return value

    def iterkeys(self):
        return (k for k, _v in self.iteritems())

    def itervalues(self):
        return (v for _k, v in self.iteritems())

    def iteritems(self):
        L = []

        def walk(node, s):
            s = s + [node[_key]]
            if node[_val] != -1:
                L.append((s, node[_val]))

            # FIXME: this is using recursion
            for child in node[_kids].values():
                if child is not node:
                    walk(child, s)

        walk(self.root, [])
        return iter(L)

    def __len__(self):
        stack = deque()
        stack.append(self.root)
        n = 0
        while stack:
            node = stack.pop()
            if node[_val] != -1:
                n += 1
            for child in node[_kids].itervalues():
                stack.append(child)
        return n

    def add(self, seq, value):
        """
        Add a sequence of items and its associated value to the trie. If seq
        already exists, its value is replaced.
        """
        if not seq:
            return

        node = self.root
        for key in seq:
            try:
                # note: kids may be None
                node = node[_kids][key]
            except KeyError:
                n = TrieNode(key)
                node[_kids][key] = n
                node = n

        # only assign the value to the last item of the sequence
        node[_val] = value

    def clear(self):
        """
        Clears trie.
        """
        self.root = TrieNode([])


    def exists(self, seq):
        """
        Return True if the sequence of items is present in the trie.
        """
        node = self.__get_node(seq)
        if node:
            return bool(node[_val] != -1)
        else:
            return False

    def match(self, seq):
        """
        Return True if the sequence of items is a prefix of any existing
        sequence of items in the trie.
        """
        return self.__get_node(seq) is not None

    def make_automaton(self):
        """
        Convert the trie to an Aho-Corasick automaton adding the failure links.
        `self.items_range` is the range of all possible items.
        """
        queue = deque()

        # 1. create top root kids over the items range, failing to root
        for item in range(self.items_range):
            # self.content is either int or chr
            # item = self.content(i)
            if item in self.root[_kids]:
                node = self.root[_kids][item]
                # f(s) = 0
                node[_fail] = self.root
                queue.append(node)
            else:
                self.root[_kids][item] = self.root

        # 2. using the queue of all possible items, walk the trie and add failure links
        while queue:
            current = queue.popleft()
            for node in current[_kids].values():
                queue.append(node)
                state = current[_fail]
                while node[_key] not in state[_kids]:
                    state = state[_fail]
                node[_fail] = state[_kids].get(node[_key], self.root)

    def search(self, seq):
        """
        Yield all matches of `seq` in the automaton performing an Aho-Corasick
        search. This includes overlapping matches.

        The returned tuples are: (matched end index in seq, [associated values, ...])
        such that the actual matched sub-sequence is: seq[end_index - n + 1:end_index + 1]
        """
        state = self.root
        for index, key in enumerate(seq):
            # find the first failure link and next state
            while key not in state[_kids]:
                state = state[_fail]

            # follow kids or get back to root
            state = state[_kids].get(key, self.root)
            tmp = state
            value = []
            while tmp != -1:
                if tmp == -1:
                    break
                if tmp[_val] != -1:
                    value.append(tmp[_val])
                tmp = tmp[_fail]
            if value:
                yield index, value

    def search_long(self, seq):
        """
        Yield all loguest non-verlapping matches of `seq` in the automaton
        performing an Aho-Corasick search such that when matches overlap, only
        the longuest is returned.

        Note that because of the original index construction, two matches cannot
        be the same as not two rules are identical.

        The returned tuples are: (matched end index in seq, [associated values, ...])
        such that the actual matched sub-sequence is: seq[end_index - n + 1:end_index + 1]
        """
        state = self.root
        last = None

        index = 0
        while index < len(seq):
            item = seq[index]

            if item in state[_kids]:
                state = state[_kids][item]
                if state[_val] != -1:
                    # save the last node on the path
                    last = index, [state[_val]]
                index += 1
            else:
                if last:
                    # return the saved match
                    yield last
                    # and start over since we do not want overlapping results
                    # Note: this leads to quadratic complexity in the worst case
                    index = last[1] + 1
                    state = self.root
                    last = None
                else:
                    # if no output, perform classic Aho-Corasick algorithm
                    while item not in state[_kids]:
                        state = state[_fail]
        # last match if any
        if last:
            yield last
