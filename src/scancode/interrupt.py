#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from commoncode.system import on_windows

DEFAULT_TIMEOUT = 120  # seconds


"""
This modules povides an interruptible() function to run a callable and
stop it after a timeout with a windows and POSIX implementation.

Call `func` function with `args` and `kwargs` arguments and return a
tuple of (success, return value). `func` is invoked through an OS-
specific wrapper and will be interrupted if it does not return within
`timeout` seconds.

`func` returned results must be pickable.
`timeout` in seconds defaults to DEFAULT_TIMEOUT.

`args` and `kwargs` are passed to `func` as *args and **kwargs.

In the returned tuple of (success, value), success is True or False. If
success is True, the call was successful and the second item in the
tuple is the returned value of `func`.

If success is False, the call did not complete within `timeout`
seconds and was interrupted. In this case, the second item in the
tuple is an error message string.
"""

class TimeoutError(Exception):
    pass


if not on_windows:
    """
    Some code based in part and inspired from the RobotFramework and
    heavily modified.

    Copyright 2008-2015 Nokia Networks
    Copyright 2016-     Robot Framework Foundation

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
    implied. See the License for the specific language governing
    permissions and limitations under the License.
    """

    import signal

    def interruptible(func, args=None, kwargs=None, timeout=DEFAULT_TIMEOUT):
        """
        POSIX, signals-based interruptible runner.
        """

        def handler(signum, frame):
            raise TimeoutError

        try:
            signal.signal(signal.SIGALRM, handler)
            signal.setitimer(signal.ITIMER_REAL, timeout)
            return True, func(*(args or ()), **(kwargs or {}))
        except TimeoutError:
            return False, ('ERROR: Processing interrupted: timeout after '
                           '%(timeout)d seconds.' % locals())
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)

else:
    """
    Run a function in an interruptible thread with a timeout.
    Based on an idea of dano "Dan O'Reilly"
    http://stackoverflow.com/users/2073595/dano
    But not code has been reused from this post.
    """

    import ctypes
    import multiprocessing
    import Queue
    try:
        import thread
    except ImportError:
        import _thread as thread


    def interruptible(func, args=None, kwargs=None, timeout=DEFAULT_TIMEOUT):
        """
        Windows, threads-based interruptible runner. It can work also on
        POSIX, but is not reliable and works only if everything is pickable.
        """
        # We run `func` in a thread and run a loop until timeout
        results = Queue.Queue()

        def runner():
            results.put(func(*(args or ()), **(kwargs or {})))

        tid = thread.start_new_thread(runner, ())

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


    def async_raise(tid, exctype=Exception):
        """
        Raise an Exception in the Thread with id `tid`. Perform cleanup if
        needed.

        Based on Killable Threads By Tomer Filiba
        from http://tomerfiliba.com/recipes/Thread2/
        license: public domain.
        """
        assert isinstance(tid, int), 'Invalid  thread id: must an integer'

        tid = ctypes.c_long(tid)
        exception = ctypes.py_object(Exception)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, exception)
        if res == 0:
            raise ValueError('Invalid thread id.')
        elif res != 1:
            # if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
            raise SystemError('PyThreadState_SetAsyncExc failed.')
