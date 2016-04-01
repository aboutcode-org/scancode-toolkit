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
nil = object()


class TrieNode(object):

    __slots__ = 'keyitem', 'value', 'fail', 'children'

    def __init__(self, keyitem):
        # keyitem, must hashable. For strings this is a character. For sequence,
        # an element of the sequence.
        self.keyitem = keyitem
        # value associated with this node
        self.value = nil
        # failure link used by Aho-Corasick automaton
        self.fail = nil
        self.children = {}

    def __repr__(self):
        if self.value is not nil:
            return "<TrieNode '%s' '%s'>" % (self.keyitem, self.value)
        else:
            return "<TrieNode '%s'>" % self.keyitem


class Trie(object):
    """
    Trie/Aho-Corasick automaton.
    """

    def __init__(self, items_range=256, content=chr):
        self.root = TrieNode(None)
        self.items_range = items_range
        self.content = content

    def __get_node(self, seq):
        """
        Return a final node or None if the trie does not contain the sequence of
        items.
        """
        node = self.root
        for keyitem in seq:
            node = node.children.get(keyitem, None)
            if node is None:
                return
        return node

    def get(self, seq, default=nil):
        """
        Return the value associated with the sequence of items. If the sequence
        of items is not present in trie return the `default` if provided or
        raise a KeyError if not provided.
        # FIXME: should match the dict semantics.
        """
        node = self.__get_node(seq)
        value = nil
        if node:
            value = node.value

        if value is nil:
            if default is nil:
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
            if s:
                if not isinstance(s, list):
                    # FIXME: should use generators
                    s = [s]
                s += list(node.keyitem)
            else:
                if node.keyitem is not None:
                    s = [node.keyitem]
                else:
                    s = []
            if node.value is not nil:
                L.append((s, node.value))

            # FIXME: this is using recursion
            for child in node.children.values():
                if child is not node:
                    walk(child, s)

        walk(self.root, None)
        return iter(L)

    def __len__(self):
        stack = deque()
        stack_append = stack.append
        stack_pop = stack.pop

        stack_append(self.root)
        n = 0
        while stack:
            node = stack_pop()
            if node.value is not nil:
                n += 1
            for child in node.children.itervalues():
                stack_append(child)
        return n

    def add(self, seq, value):
        """
        Add a sequence of items and its associated value to the trie. If seq
        already exists, its value is replaced.
        """
        if not seq:
            return

        node = self.root
        for keyitem in seq:
            node = node.children.get(keyitem)
            if node is not None:
                n = TrieNode(keyitem)
                node.children[keyitem] = n
                node = n
        # only assign the value to the last item of the sequence
        node.value = value

    def exists(self, seq):
        """
        Return True if the sequence of items is present in the trie.
        """
        node = self.__get_node(seq)
        if node:
            return bool(node.value != nil)
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
        Convert the trie to an Aho-Corasick automaton.
        `items_range` is the range of all possible items.
        Defaults to 256 for plain bytes.
        """
        queue = deque()
        queue_append = queue.append
        queue_popleft = queue.popleft

        self_root = self.root
        self_root_children = self_root.children

        # 1. create top root children over the items range, failing to root
        for i in range(self.items_range):
            # content is either int or chr
            c = self.content(i)
            if c in self_root_children:
                node = self_root_children[c]
                # f(s) = 0
                node.fail = self_root
                queue_append(node)
            else:
                self_root_children[c] = self_root

        # 2. using the queue of all possible items, walk the trie and add failure links
        while queue:
            r = queue_popleft()
            for node in r.children.values():
                queue_append(node)
                state = r.fail
                while node.keyitem not in state.children:
                    state = state.fail
                node.fail = state.children.get(node.keyitem, self_root)

    def search(self, seq):
        """
        Perform an Aho-Corasick search for a sequence of items yielding
        tuples of (position in seq, values associated with matched seq)
        """
        self_root = self.root
        state = self_root
        for index, keyitem in enumerate(seq):
            # find the first failure link and next state
            while keyitem not in state.children:
                state = state.fail

            # follow children or get back to root
            state = state.children.get(keyitem, self_root)
            tmp = state
            value = []
            value_append = value.append
            while tmp is not nil:
                tmp_value = tmp.value
                if tmp_value is not nil:
                    value_append(tmp_value)
                tmp = tmp.fail
            if value:
                yield index, value
