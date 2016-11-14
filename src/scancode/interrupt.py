
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

Original comments:

Here's a way you can do this without needing to change your worker function. The idea
is to wrap the worker in another function, which will call worker in a background
thread, and then wait for a result for for timeout seconds. If the timeout expires,
it raises an exception, which will abruptly terminate the thread worker is executing
in. Any function that timeouts will raise multiprocessing.TimeoutError. Note that
this means your callback won't execute when a timeout occurs. If this isn't
acceptable, just change the except block of abortable_worker to return something
instead of calling raise.

When you pass N to the Pool constructor, N processes are immediately launched, and
those exact N processes continue to run for the entire lifetime of the pool. No
additional processes get added, and no processes get removed. Any work items you pass
to the Pool via apply/map get distributed to those N workers. If all the workers are
busy, the work item get queued until a worker frees up and is able to execute it.
"""

from __future__ import print_function, absolute_import

#
# ###########################################################################
# # Monkeypatch Pool iterators so that Ctrl-C interrupts everything properly
# # based from https://gist.github.com/aljungberg/626518
# # FIXME: unknown license
# ###########################################################################
# from multiprocessing.pool import IMapIterator, IMapUnorderedIterator
#
# def wrapped(func):
#     def wrap(self, timeout=None):
#         return func(self, timeout=timeout or 1e10)
#     return wrap
#
# IMapIterator.next = wrapped(IMapIterator.next)
# IMapIterator.__next__ = IMapIterator.next
# IMapUnorderedIterator.next = wrapped(IMapUnorderedIterator.next)
# IMapUnorderedIterator.__next__ = IMapUnorderedIterator.next
#
# ###########################################################################

from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing

from functools import partial
import random
from time import sleep

import psutil


MAX_TIMEOUT = 600  # seconds
MAX_MEMORY = 640 * 1024 * 1024 * 1024  # 640MB


def interruptible(func, *args, **kwargs):
    """
    Call `func` function with `args` arguments and return a tuple of (success, return
    value). `func` is invoked through a wrapper and will be interrupted if it does
    not return within `timeout` seconds of execution. `timeout` defaults to
    MAX_TIMEOUT seconds and must be provided as a keyword argument. Only args are
    passed to func, not kwargs.

    In the returned tuple of (success, value), success is True or False. If success
    is True, the call was successful and the second item in the tuple is the returned
    value of func.
    If success is False, the call did not complete within timeout seconds and was
    interrupted. The second item in the tuple is an error message string.
    """
    timeout = kwargs.pop('timeout', MAX_TIMEOUT)
    pool = ThreadPool(1)
    runner = pool.apply_async(func, args=args)
    try:
        # Wait timeout seconds for func to complete.
        result = runner.get(timeout)
        return True, result
    except multiprocessing.TimeoutError:
        return False, 'Processing interrupted after timeout of %(timeout)d seconds.' % locals()
    except KeyboardInterrupt:
        return False, 'Processing interrupted with Ctrl-C.'
    finally:
        pool.terminate()
        pool.close()


MEMORY_EXCEEDED = 1
RUNTIME_EXCEEDED = 2

def time_and_ram_interruptible(func, *args, **kwargs):
    """
    Call `func` function with `args` arguments and return a tuple of (success, return
    value). `func` is invoked through a wrapper and will be interrupted if it does
    not return within `timeout` seconds of execution or uses more than 'max_memory`
    bytes of memory.

    `timeout` defaults to MAX_TIMEOUT seconds and must be provided as a keyword
    argument.

    `max_memory` defaults to MAX_MEMORY bytes and must be provided as a keyword
    argument.

    Only `args` are passed to `func`, not any `kwargs`.

    In the returned tuple of (success, value), success is True or False. If success
    is True, the call was successful and the second item in the tuple is the returned
    value of func.
    If success is False, the call did not complete within timeout seconds or exceeded
    max_memory and was interrupted. The second item in the tuple is an error message
    string.
    """
    timeout = kwargs.pop('timeout', MAX_TIMEOUT)
    max_memory = kwargs.pop('max_memory', MAX_MEMORY)

    # we use a pool of three threads:
    # - one will run the func
    # - one will sleep until timeout
    # - one will run a loop to check for memory usage
    # The first thread that completes will return a result and stop the pool. e.g if
    # the func completes within timeout and does not exceed RAM, it will return first
    # otherwise it will be killed and some error will be returned instead
    pool = ThreadPool(3)

    execution_units = [
        (func, args),
        (memory_guard, [max_memory]),
        (time_guard, [timeout]),
    ]

    # submit our three threads: whichever finishes first will be returned by the call to next()
    threads = pool.imap_unordered(runner, execution_units, chunksize=1)

    try:
        result = threads.next(MAX_TIMEOUT)
        if result == MEMORY_EXCEEDED:
            max_mb = megabytes(max_memory)
            return False, 'Processing interrupted: excessive memory usage over %(max_mb)s.' % locals()
        elif result == RUNTIME_EXCEEDED:
            return False, 'Processing interrupted: did not complete within timeout of %(timeout)d seconds.' % locals()
        else:
            # we succeeded with quotas: return results and stop processing
            return True, result

    except multiprocessing.TimeoutError:
        return False, 'Processing interrupted after timeout of %(timeout)d seconds.' % locals()

    except KeyboardInterrupt:
        return False, 'Processing interrupted with Ctrl-C.'
    finally:
        pool.terminate()
        pool.close()


def runner(arg):
    """
    Run func with args and return its returned value.
    """
    func, args = arg
    return func(*args)


def memory_guard(max_memory, interval=1):
    """
    Run forever and return if memory usage in the current process exceeds max_memory.
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
            # How could this happen? this is really bad???
            return MEMORY_EXCEEDED


def time_guard(timeout):
    """
    Return when a timeout has expired.
    """
    sleep(timeout)
    return RUNTIME_EXCEEDED


def megabytes(n):
    """
    Return a string representation of a bytes number as megabytes.
    """
    mega = 1024 * 1024 * 1024
    return '%dMB' % (n // mega)


if __name__ == '__main__':
    """
    Example.
    """
    def worker(*args):
        sleep(random.randint(1, 4))
        return 'OK'

    # list of arguments
    features = [[1000, k, 1] for k in range(20)]
    inter = partial(interruptible, worker, timeout=2)

    pool = multiprocessing.Pool(4)
    results = pool.imap_unordered(inter, features)
    while True:
        try:
            success, result = results.next(1000)
            print('success, result:', success, result)
        except StopIteration:
            break
        except KeyboardInterrupt:
            print('\nKeyboard interrupt!')
            pool.terminate()
            break
