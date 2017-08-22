
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

"""
Utilities and patches to create multiprocessing Process pools.
Apply proper monkeypatch to work around some bugs or limitations.
"""


"""
Monkeypatch Pool iterators so that Ctrl-C interrupts everything properly
derived from https://gist.github.com/aljungberg/626518

Copyright (c) Alexander Ljungberg. All rights reserved.
Modifications Copyright (c) 2017 nexB Inc. and others. All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from multiprocessing import pool

def wrapped(func):
    # ensure that we do not double wrap
    if func.func_name != 'wrap':
        def wrap(self, timeout=None):
            return func(self, timeout=timeout or 1e10)
        return wrap
    else:
        return func

pool.IMapIterator.next = wrapped(pool.IMapIterator.next)
pool.IMapIterator.__next__ = pool.IMapIterator.next
pool.IMapUnorderedIterator.next = wrapped(pool.IMapUnorderedIterator.next)
pool.IMapUnorderedIterator.__next__ = pool.IMapUnorderedIterator.next


def get_pool(processes=None, initializer=None, initargs=(), maxtasksperchild=None):
    return pool.Pool(processes, initializer, initargs, maxtasksperchild)
