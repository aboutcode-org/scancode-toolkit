
"""
Originally based on:
http://stackoverflow.com/questions/29494001/how-can-i-abort-a-task-in-a-multiprocessing-pool-after-a-timeout/29495039#29495039
By dano "Dan O'Reilly" : http://stackoverflow.com/users/2073595/dano
license: public-domain

On 2016-11-11 the Dan O'Reilly provided this feedback:
@dano what would be the license for this code beside the standard CC-BY-SA?
    -Philippe Ombredanne 1 hour ago
@PhilippeOmbredanne Public Domain, as far as I'm concerned.
- dano 1 hour ago

The code was heavily modified to support both a timeout and memory quota:

We use a pool of two threads that will race against each other to finish first:
- one will run the requested function proper
- one will run a loop until a timeout to check for memory usage and return when it
  exceeds max_memory or timeout expires.

The first thread to complete will return its result and win. e.g if the function
completes within timeout and does not exceeds RAM, it will return first. Otherwise if
the memory check and timeout thread completes first, the main function will be
killed and some error will be returned instead.
"""

from __future__ import print_function, absolute_import

###########################################################################
# Monkeypatch Pool iterators so that Ctrl-C interrupts everything properly
# derived from https://gist.github.com/aljungberg/626518
# FIXME: unknown license
###########################################################################
from multiprocessing.pool import IMapIterator, IMapUnorderedIterator

def wrapped(func):
    # ensure that we do not double wrap
    if func.func_name != 'wrap':
        def wrap(self, timeout=None):
            return func(self, timeout=timeout or 1e10)
        return wrap
    else:
        return func

IMapIterator.next = wrapped(IMapIterator.next)
IMapIterator.__next__ = IMapIterator.next
IMapUnorderedIterator.next = wrapped(IMapUnorderedIterator.next)
IMapUnorderedIterator.__next__ = IMapUnorderedIterator.next
###########################################################################

###########################################################################
# Monkeypatch/subclass multiprocessing Process and ThreadPool to
# apply fix for bug https://bugs.python.org/issue14881
# In Python before 2.7.6 this happens at times. For intance on Ubuntu 12.04
# This is the fix applied in https://www.python.org/ftp/python/2.7.12/Python-2.7.12.tar.xz
# We only apply this fix to Python versions before 2.7.6
###########################################################################

import multiprocessing
import sys

py_before_276 = (sys.version_info[0] == 2 and sys.version_info[1] == 7 and (sys.version_info[2] < 6))

if py_before_276:
    import threading
    from multiprocessing.dummy import Process as StandardProcess
    from multiprocessing.dummy import current_process
    from multiprocessing.pool import ThreadPool as StandardThreadPool

    class PatchedProcess(StandardProcess):
        """
        dummy.Process subclass with patched start method for bug https://bugs.python.org/issue14881
        """
        def start(self):
            assert self._parent is current_process()
            self._start_called = True
            if hasattr(self._parent, '_children'):
                self._parent._children[self] = None
            threading.Thread.start(self)

    class ThreadPool(StandardThreadPool):
        """
        ThreadPool subclass using patched Process
        """
        Process = PatchedProcess

else:
    from multiprocessing.pool import ThreadPool

###########################################################################

from time import sleep

import psutil


DEFAULT_TIMEOUT = 120  # seconds
RUNTIME_EXCEEDED = 1

DEFAULT_MAX_MEMORY = 1000  # megabytes
MEMORY_EXCEEDED = 2


def interruptible(func, *args, **kwargs):
    """
    Call `func` function with `args` arguments and return a tuple of (success, return
    value). `func` is invoked through a wrapper and will be interrupted if it does
    not return within `timeout` seconds of execution or uses more than 'max_memory`
    MEGABYTES of memory. `func` returned results should be pickable.

    `timeout` in seconds should be provided as a keyword argument.
    MIN_TIMEOUT is always enforced even if no timeout keyword is present.

    `max_memory` in megabytes should be provided as a keyword argument.
    If not present a memory quota is not enforced.

    Only `args` are passed to `func`, not any `kwargs`.

    In the returned tuple of (success, value), success is True or False.
    If success is True, the call was successful and the second item in the tuple is
    the returned value of `func`.
    If success is False, the call did not complete within `timeout` seconds or
    exceeded `max_memory` memory usage and was interrupted. In this case, the second
    item in the tuple is an error message string.
    """

    timeout = kwargs.pop('timeout', DEFAULT_TIMEOUT)
    max_memory = kwargs.pop('max_memory', DEFAULT_MAX_MEMORY) * 1024 * 1024

    # We use a pool of two threads that race to finish against each other:
    # - one runs the func proper
    # - one runs a loop until a timeout to check memory usage and return when it
    #   exceeds max_memory or the timeout
    # The first thread to complete return its result. The other thread is terminated.

    pool = ThreadPool(2)
    execution_units = [(func, args,), (time_and_memory_guard, [max_memory, timeout],)]

    # run our threads: whichever finishes first thanks to imap_unordered will be
    # returned by the single call to next()
    threads = pool.imap_unordered(runner, execution_units, chunksize=1)
    pool.close()
    try:
        result = threads.next(timeout)
        if result == MEMORY_EXCEEDED:
            max_mb = megabytes(max_memory)
            return False, 'ERROR: Processing interrupted: excessive memory usage of more than %(max_mb)s.' % locals()
        elif result == RUNTIME_EXCEEDED:
            return False, 'ERROR: Processing interrupted: timeout after %(timeout)d seconds.' % locals()
        else:
            # we succeeded with quotas: return expected results
            return True, result

    except multiprocessing.TimeoutError:
        return False, 'ERROR: Processing interrupted: timeout after %(timeout)d seconds.' % locals()

    except KeyboardInterrupt:
        return False, 'ERROR: Processing interrupted with Ctrl-C.'

    finally:
        # stop processing
        pool.terminate()


def runner(func_args):
    """
    Given a `func_args` tuple of (func, args) run the func callable with args and
    return func's returned value. This is a wrapper to allow using in a map-like
    call.
    """
    func, args = func_args
    return func(*args)


def time_and_memory_guard(max_memory=DEFAULT_MAX_MEMORY, timeout=DEFAULT_TIMEOUT, interval=2):
    """
    Return when max_memory bytes has been used or when a timeout has expired.
    Check memory usage every `interval` seconds during up to `timeout` seconds. Run
    until the memory usage in the current process exceeds `max_memory` bytes. If it
    does, return `MEMORY_EXCEEDED`. If the memory usage does not go over `max_memory`
    bytes within `timeout` seconds, return RUNTIME_EXCEEDED.
    """
    process = psutil.Process()
    memory_info = process.memory_info
    while timeout > 0:
        try:
            if memory_info().rss > max_memory:
                return MEMORY_EXCEEDED
            sleep(interval)
            timeout -= interval
        except:
            # How could this happen? Some psutil error?
            return MEMORY_EXCEEDED
    return RUNTIME_EXCEEDED


def megabytes(n):
    """
    Return a megabytes string representation of an `n` number of bytes.
    """
    mega = 1024 * 1024
    return '%dMB' % (n // mega)
