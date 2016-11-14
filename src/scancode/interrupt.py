
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

from functools import partial
import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool
import random
from time import sleep


MAX_TIMEOUT = 600


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
        pool.terminate()
        return False, 'Processing interrupted after timeout of %(timeout)d seconds.' % locals()
    except KeyboardInterrupt:
        pool.terminate()
        return False, 'Processing interrupted with Ctrl-C.'


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
