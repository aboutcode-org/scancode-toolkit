
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



from __future__ import absolute_import, print_function


from licensedcode.pyahocorasick import Trie


def test_EmptyTrieShouldNotContainsAnyWords():
    t = Trie()
    assert len(t) ==0


def test_AddedWordShouldBeCountedAndAvailableForRetrieval():
    t = Trie()
    t.add('python', 'value')
    assert len(t)== 1
    assert t.get('python')== 'value'


def test_AddingExistingWordShouldReplaceAssociatedValue():
    t = Trie()
    t.add('python', 'value')
    assert len(t) ==1
    assert t.get('python') =='value'

    t.add('python', 'other')
    assert len(t) ==1
    assert t.get('python') =='other'


def test_GetUnknowWordWithoutDefaultValueShouldRaiseException():
    t = Trie()
    try:
        t.get('python')
    except KeyError:
        pass


def test_GetUnknowWordWithDefaultValueShouldReturnDefault():
    t = Trie()
    assert t.get('python', 'default') =='default'


def test_ExistShouldDetectAddedWords():
    t = Trie()
    t.add('python', 'value')
    t.add('ada', 'value')

    assert t.exists('python')
    assert t.exists('ada')


def test_ExistShouldReturnFailOnUnknownWord():
    t = Trie()
    t.add('python', 'value')

    assert not t.exists('ada')


def test_MatchShouldDetecAllPrefixesIncludingWord():
    t = Trie()
    t.add('python', 'value')
    t.add('ada', 'value')

    assert t.match('a')
    assert t.match('ad')
    assert t.match('ada')

    assert t.match('p')
    assert t.match('py')
    assert t.match('pyt')
    assert t.match('pyth')
    assert t.match('pytho')
    assert t.match('python')
    assert not t.match('yth')


def test_iteritems_ShouldReturnAllItemsAlreadyAddedToTheTrie():
    t = Trie()
    t.add('python', 1)
    t.add('ada', 2)
    t.add('perl', 3)
    t.add('pascal', 4)
    t.add('php', 5)

    result = [(''.join(k), v) for k, v in t.iteritems()]
    assert [('ada', 2), ('python', 1), ('pascal', 4), ('perl', 3), ('php', 5)] == result


def test_iterkeys_ShouldReturnAllKeysAlreadyAddedToTheTrie():
    t = Trie()
    t.add('python', 1)
    t.add('ada', 2)
    t.add('perl', 3)
    t.add('pascal', 4)
    t.add('php', 5)

    result = sorted([''.join(k) for k  in t.iterkeys()])
    assert  ['ada', 'pascal', 'perl', 'php', 'python'] ==result


def test_itervalues_ShouldReturnAllValuesAlreadyAddedToTheTrie():
    t = Trie()
    t.add('python', 1)
    t.add('ada', 2)
    t.add('perl', 3)
    t.add('pascal', 4)
    t.add('php', 5)

    result = sorted(t.itervalues())
    assert [1, 2, 3, 4, 5] == result


def get_test_automaton():
    words = 'he her hers his she hi him man himan'.split()
    t = Trie();
    for w in words:
        t.add(w, w)
    t.make_automaton()
    return t


def test_search_should_match_all_strings():
    words = 'he her hers his she hi him man himan'.split()
    t = Trie();
    for w in words:
        t.add(w, w)
    t.make_automaton()

    test_string = 'he she himan'
    result = list(t.search(test_string))

    # there are 5 matching positions
    expected = [
        (1, ['he']),
        (5, ['she', 'he']),
        (8, ['hi']),
        (9, ['him']),
        (11, ['himan', 'man'])
    ]
    assert expected == result

    # result should have be valid, i.e. returned position and substring
    # must match substring from test string
    for end_index, strings in result:
        for s in strings:
            n = len(s)
            assert s, test_string[end_index - n + 1 : end_index + 1]
