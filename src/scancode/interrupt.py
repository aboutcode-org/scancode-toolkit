
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

We use a pool of three threads that will race against each other to finish first:
- one will run the requested function proper
- one will sleep until a timeout and then return
- one will run a loop to check for memory usage and return when it exceeds max_memory

The first thread to complete will return its result and win. e.g if the function
completes within timeout and does not exceeds RAM, it will return first. Otherwise if
the memory check or the timeout thread completes first, the main function will be
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

from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing

from time import sleep

import psutil


MIN_TIMEOUT = 60  # seconds
MAX_TIMEOUT = 600  # seconds
RUNTIME_EXCEEDED = 1

MIN_MEMORY = 1024 * 1024 * 1024  # 1GB
MAX_MEMORY = 2 * 1024 * 1024 * 1024  # 2GB
MEMORY_EXCEEDED = 2


def interruptible(func, *args, **kwargs):
    """
    Call `func` function with `args` arguments and return a tuple of (success, return
    value). `func` is invoked through a wrapper and will be interrupted if it does
    not return within `timeout` seconds of execution or uses more than 'max_memory`
    bytes of memory.

    `timeout` in seconds should be provided as a keyword argument.
    MAX_TIMEOUT is always enforced even if no timeout keyword is present.

    `max_memory` in bytes should be provided as a keyword argument.
    If not present maximum memory quota is not enforced.

    Only `args` are passed to `func`, not any `kwargs`.

    In the returned tuple of (success, value), success is True or False. If success
    is True, the call was successful and the second item in the tuple is the returned
    value of func.
    If success is False, the call did not complete within timeout seconds or exceeded
    max_memory and was interrupted. The second item in the tuple is an error message
    string.
    """

    # We use a pool of three threads that will race to finish against each other:
    # - one will run the func proper
    # - one will sleep until a timeout and return
    # - one will run a loop to check for memory usage and return when it exceeds max_memory
    # The first thread that completes will return a result and win.
    # Other threads will be terminated.

    pool = ThreadPool(3)

    # our execution units contain at least the the function to run proper
    execution_units = [(func, args,)]

    # add timeout only if present
    if 'timeout' in kwargs:
        timeout = kwargs.pop('timeout', MIN_TIMEOUT)
        execution_units.append((time_guard, [timeout],))

    # add memory quota only if present
    if 'max_memory' in kwargs:
        max_memory = kwargs.pop('max_memory', MIN_MEMORY)
        execution_units.append((memory_guard, [max_memory],))

    # submit our three threads: whichever finishes first thanks to imap_unordered
    # will be returned by the call to next()
    threads = pool.imap_unordered(runner, execution_units, chunksize=1)

    try:
        # always use MAX_TIMEOUT
        result = threads.next(MAX_TIMEOUT)
        if result == MEMORY_EXCEEDED:
            max_mb = megabytes(max_memory)
            return False, 'Processing interrupted: excessive memory usage of more than %(max_mb)s.' % locals()
        elif result == RUNTIME_EXCEEDED:
            return False, 'Processing interrupted: timeout after %(timeout)d seconds.' % locals()
        else:
            # we succeeded with quotas: return expected results
            return True, result

    except multiprocessing.TimeoutError:
        return False, 'Processing interrupted: timeout after %(timeout)d seconds.' % locals()

    except KeyboardInterrupt:
        return False, 'Processing interrupted with Ctrl-C.'
    finally:
        # stop processing
        pool.terminate()


def runner(arg):
    """
    Run func with args and return its returned value where arg is tuple of (func, args).
    This is a wrapper to allow using an imap-like call.
    """
    func, args = arg
    return func(*args)


def time_guard(timeout):
    """
    Return when a timeout has expired.
    """
    sleep(timeout)
    return RUNTIME_EXCEEDED


def compute_timeout(size, extra_sec_per_mb=30):
    """
    Return a scan timeout in seconds computed based on a file size.
    """
    # add extra seconds for each megabyte
    timeout = MIN_TIMEOUT + ((size // (1024 * 1024)) * extra_sec_per_mb)
    return min([timeout, MAX_TIMEOUT])


def memory_guard(max_memory, interval=5):
    """
    Run forever unless memory usage in the current process exceeds `max_memory`.
    If it does, return `MEMORY_EXCEEDED`
    Check memory usage every `interval` seconds.
    """
    process = psutil.Process()
    memory_info = process.memory_info
    while True:
        try:
            if memory_info().rss > max_memory:
                return MEMORY_EXCEEDED
            sleep(interval)
        except:
            # How could this happen? Some psutil issue??
            return MEMORY_EXCEEDED


def compute_memory_quota(size, extra_ram_per_mb=5):
    """
    Return a not-to-exceed maximum memory_quota in bytes computed based on a file size.
    """
    # add extra quota for each byte of a file bigger than 1MB
    memory_quota = MIN_MEMORY + (size * extra_ram_per_mb)
    return min([memory_quota, MAX_MEMORY])


def megabytes(n):
    """
    Return a string representation of a bytes number as megabytes.
    """
    mega = 1024 * 1024
    return '%dMB' % (n // mega)
