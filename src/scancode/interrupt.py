#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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

from __future__ import print_function
from __future__ import absolute_import

import os
import Queue
import thread

import psutil

from scancode.thread2 import async_raise


DEFAULT_TIMEOUT = 120  # seconds
DEFAULT_MAX_MEMORY = 1000  # in megabytes. 0 is unlimited.

"""
Run a function in an interruptible thread with a timeout and memory quota.
Based on an idea of dano "Dan O'Reilly"  http://stackoverflow.com/users/2073595/dano
But not code has been reused from this post.
"""

def interruptible(func, args=(), kwargs={},
                  timeout=DEFAULT_TIMEOUT, max_memory=DEFAULT_MAX_MEMORY):

    try:
        return _interruptible(func, args, kwargs, timeout, max_memory)
    except:
        import traceback
        print('#############ERROR##################')
        print(traceback.format_exc())
        print('###################################')
        raise


def _interruptible(func, args=(), kwargs={},
                  timeout=DEFAULT_TIMEOUT, max_memory=DEFAULT_MAX_MEMORY):
    """
    Call `func` function with `args` and `kwargs` arguments and return a tuple of
    (success, return value). `func` is invoked through a wrapper in a thread and
    will be interrupted if it does not return within `timeout` seconds of execution
    or uses more than 'max_memory` MEGABYTES of memory.

    `func` returned results must be pickable.
    `timeout` in seconds defaults to DEFAULT_TIMEOUT.

    `max_memory` is the memory quota in megabytes and defaults to DEFAULT_MAX_MEMORY.
    If zero, then no memory quota is enforced.

    `args` and `kwargs` are passed to `func` as *args and **kwargs.

    In the returned tuple of (success, value), success is True or False.
    If success is True, the call was successful and the second item in the tuple is
    the returned value of `func`.
    If success is False, the call did not complete within `timeout` seconds or
    exceeded `max_memory` memory usage and was interrupted. In this case, the second
    item in the tuple is an error message string.
    """
    # We run `func` in a thread and run a loop until timeout to check memory
    # usage of the runner
    results = Queue.Queue()

    def _runner():
        res = func(*args, **kwargs)
        results.put(res)

    tid = thread.start_new_thread(_runner, ())

    # only check for memory if asked for a quota
    max_bytes = max_memory * 1024 * 1024
    get_memory_in_use = None
    if max_bytes:
        get_memory_in_use = psutil.Process(os.getpid()).memory_info

    interval = 0.2  # second
    try:
        while timeout > 0:
            if max_bytes and get_memory_in_use().rss > max_bytes:
                return False, ('ERROR: Processing interrupted: excessive memory usage '
                               'of more than %(max_memory)dMB.' % locals())

            try:
                # blocking get for interval which is a slice of the timeout
                res = results.get(timeout=interval)
                return True, res
            except Queue.Empty:
                timeout -= interval

        return False, ('ERROR: Processing interrupted: timeout after '
                       '%(timeout)d seconds.' % locals())
    finally:
        try:
            async_raise(tid, Exception)
        except (SystemExit, ValueError, Exception):
            pass
