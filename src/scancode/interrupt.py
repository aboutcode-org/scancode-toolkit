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

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from traceback import format_exc as traceback_format_exc

from commoncode.system import on_windows

"""
This modules povides an interruptible() function to run a callable and stop it
after a timeout with a windows and POSIX implementation.

interruptible() calls the `func` function with `args` and `kwargs` arguments and
return a tuple of (error, value). `func` is invoked through an OS- specific
wrapper and will be interrupted if it does not return within `timeout` seconds.

`func` returned results must be pickable.
`timeout` in seconds defaults to DEFAULT_TIMEOUT.
`args` and `kwargs` are passed to `func` as *args and **kwargs.

In the returned tuple of (`error`, `value`), `error` is an error string or None.
The error message is verbose with a full traceback.
`value` is the returned value of `func` or None.

If `error` is not None, the call did not complete within `timeout`
seconds and was interrupted. In this case, the returned `value` is None.
"""


class TimeoutError(Exception):
    pass


DEFAULT_TIMEOUT = 120  # seconds

TIMEOUT_MSG = 'ERROR: Processing interrupted: timeout after %(timeout)d seconds.'
ERROR_MSG = 'ERROR: Unknown error:\n'
NO_ERROR = None
NO_VALUE = None

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

    from signal import ITIMER_REAL
    from signal import SIGALRM
    from signal import setitimer
    from signal import signal as create_signal

    def interruptible(func, args=None, kwargs=None, timeout=DEFAULT_TIMEOUT):
        """
        POSIX, signals-based interruptible runner.
        """

        def handler(signum, frame):
            raise TimeoutError

        try:
            create_signal(SIGALRM, handler)
            setitimer(ITIMER_REAL, timeout)
            return NO_ERROR, func(*(args or ()), **(kwargs or {}))

        except TimeoutError:
            return TIMEOUT_MSG % locals(), NO_VALUE

        except Exception:
            return ERROR_MSG + traceback_format_exc(), NO_VALUE

        finally:
            setitimer(ITIMER_REAL, 0)

else:
    """
    Run a function in an interruptible thread with a timeout.
    Based on an idea of dano "Dan O'Reilly"
    http://stackoverflow.com/users/2073595/dano
    But not code has been reused from this post.
    """

    from ctypes import c_long
    from ctypes import py_object
    from ctypes import pythonapi
    from multiprocessing import TimeoutError as MpTimeoutError
    from Queue import Empty as Queue_Empty
    from Queue import Queue
    try:
        from thread import start_new_thread
    except ImportError:
        from _thread import start_new_thread

    def interruptible(func, args=None, kwargs=None, timeout=DEFAULT_TIMEOUT):
        """
        Windows, threads-based interruptible runner. It can work also on
        POSIX, but is not reliable and works only if everything is pickable.
        """
        # We run `func` in a thread and block on a queue until timeout
        results = Queue()

        def runner():
            try:
                _res = func(*(args or ()), **(kwargs or {}))
                results.put((NO_ERROR, _res,))
            except Exception:
                results.put((ERROR_MSG + traceback_format_exc(), NO_VALUE,))

        tid = start_new_thread(runner, ())

        try:
            err_res = results.get(timeout=timeout)

            if not err_res:
                return ERROR_MSG, NO_VALUE

            return err_res

        except (Queue_Empty, MpTimeoutError):
            return TIMEOUT_MSG % locals(), NO_VALUE

        except Exception:
            return ERROR_MSG + traceback_format_exc(), NO_VALUE

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

        tid = c_long(tid)
        exception = py_object(Exception)
        res = pythonapi.PyThreadState_SetAsyncExc(tid, exception)
        if res == 0:
            raise ValueError('Invalid thread id.')
        elif res != 1:
            # if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect
            pythonapi.PyThreadState_SetAsyncExc(tid, 0)
            raise SystemError('PyThreadState_SetAsyncExc failed.')


def fake_interruptible(func, args=None, kwargs=None, timeout=DEFAULT_TIMEOUT):
    """
    Fake, non-interruptible, using no threads and no signals
    implementation used for debugging. This ignores the timeout and just
    the function as-is.
    """

    try:
        return NO_ERROR, func(*(args or ()), **(kwargs or {}))
    except Exception:
        return ERROR_MSG + traceback_format_exc(), NO_VALUE
