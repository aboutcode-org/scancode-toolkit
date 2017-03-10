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

import multiprocessing
import Queue
import thread

from scancode.thread2 import async_raise

DEFAULT_TIMEOUT = 120  # seconds

"""
Run a function in an interruptible thread with a timeout..
Based on an idea of dano "Dan O'Reilly"  http://stackoverflow.com/users/2073595/dano
But not code has been reused from this post.
"""


def interruptible(func, args=(), kwargs={}, timeout=DEFAULT_TIMEOUT):
    """
    Call `func` function with `args` and `kwargs` arguments and return a tuple of
    (success, return value). `func` is invoked through a wrapper in a thread and
    will be interrupted if it does not return within `timeout` seconds.

    `func` returned results must be pickable.
    `timeout` in seconds defaults to DEFAULT_TIMEOUT.

    `args` and `kwargs` are passed to `func` as *args and **kwargs.

    In the returned tuple of (success, value), success is True or False.
    If success is True, the call was successful and the second item in the tuple is
    the returned value of `func`.
    
    If success is False, the call did not complete within `timeout`
    seconds and was interrupted. In this case, the second item in the
    tuple is an error message string.
    """
    # We run `func` in a thread and run a loop until timeout
    results = Queue.Queue()

    def _runner():
        results.put(func(*args, **kwargs))

    tid = thread.start_new_thread(_runner, ())

    try:
        res = results.get(timeout=timeout)
        return True, res
    except (Queue.Empty, multiprocessing.TimeoutError):
        return False, ('ERROR: Processing interrupted: timeout after '
                       '%(timeout)d seconds.' % locals())
    finally:
        try:
            async_raise(tid, Exception)
        except (SystemExit, ValueError):
            pass
