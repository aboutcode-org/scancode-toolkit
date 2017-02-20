

"""
Based on Killable Threads By Tomer Filiba
from http://tomerfiliba.com/recipes/Thread2/
public domain.
"""

from __future__ import absolute_import
import ctypes


def async_raise(tid, exctype):
    """
    Raise the exception `exctype` in the Thread with id `tid`. Perform cleanup if
    needed
    """
    assert isinstance(tid, int), 'Invalid  thread id: must an integer'
    assert isinstance(exctype, type), 'Only types can be raised (not instances)'

    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid),
                                                     ctypes.py_object(exctype))
    if res == 0:
        raise ValueError('Invalid thread id.')
    elif res != 1:
        # if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), 0)
        raise SystemError('PyThreadState_SetAsyncExc failed.')
