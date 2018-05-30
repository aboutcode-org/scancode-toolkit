#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import, print_function

import functools
from types import ListType, TupleType, GeneratorType
from array import array


def flatten(seq):
    """
    Flatten recursively a sequence and all its sub-sequences that can be tuples,
    lists or generators (generators will be consumed): all are converted to a
    flat list of elements.

    For example::

    >>> flatten([7, (6, [5, [4, ['a'], 3]], 3), 2, 1])
    [7, 6, 5, 4, 'a', 3, 3, 2, 1]
    >>> def gen():
    ...     for i in range(2):
    ...         yield range(5)
    ...
    >>> flatten(gen())
    [0, 1, 2, 3, 4, 0, 1, 2, 3, 4]

    Originally derived from http://www.andreasen.org/misc/util.py
    2002-2005 by Erwin S. Andreasen -- http://www.andreasen.org/misc.shtml
    This file is in the Public Domain
    Version: Id: util.py,v 1.22 2005/12/16 00:08:21 erwin Exp erwin
    """
    r = []
    for x in seq:
        if isinstance(x, (ListType, TupleType)):
            r.extend(flatten(x))
        elif isinstance(x, GeneratorType):
            r.extend(flatten(list(x)))
        else:
            r.append(x)
    return r


def memoize(fun):
    """
    Decorate `fun` function and cache return values. Arguments must be hashable.
    Only args are supported, kwargs are not handled. Used to speed up some often
    executed functions.

    For example::

    >>> @memoize
    ... def expensive(*args, **kwargs):
    ...     print('Calling expensive with', args, kwargs)
    ...     return 'value expensive to compute' + repr(args)
    >>> expensive(1, 2)
    Calling expensive with (1, 2) {}
    'value expensive to compute(1, 2)'
    >>> expensive(1, 2)
    'value expensive to compute(1, 2)'
    >>> expensive(1, 2, a=0)
    Calling expensive with (1, 2) {'a': 0}
    'value expensive to compute(1, 2)'
    >>> expensive(1, 2, a=0)
    Calling expensive with (1, 2) {'a': 0}
    'value expensive to compute(1, 2)'
    >>> expensive(1, 2)
    'value expensive to compute(1, 2)'
    >>> expensive(1, 2, 5)
    Calling expensive with (1, 2, 5) {}
    'value expensive to compute(1, 2, 5)'

    The expensive function returned value will be cached based for each args
    values and computed only once in its life. Call with kwargs are not cached
    """
    memos = {}

    @functools.wraps(fun)
    def memoized(*args, **kwargs):
        # calls with kwargs are not handled and not cached
        if kwargs:
            return fun(*args, **kwargs)
        # convert any list args to a tuple
        args = tuple(tuple(arg) if isinstance(arg, (ListType, tuple, array)) else arg
                     for arg in args)
        try:
            return memos[args]
        except KeyError:
            memos[args] = fun(*args)
            return memos[args]

    return functools.update_wrapper(memoized, fun)


def partial(func, *args, **kwargs):
    """
    Return a partial function. Same as functools.partial but keeping the __doc__
    and __name__ of the warpper function.
    """
    return functools.update_wrapper(functools.partial(func, *args, **kwargs), func)
