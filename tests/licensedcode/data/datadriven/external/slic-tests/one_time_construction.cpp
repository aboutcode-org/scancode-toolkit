/*
 * one_time_construction.cpp
 *
 * Copyright 2006 The Android Open Source Project
 *
 * This file contains C++ ABI support functions for one time
 * constructors as defined in the "Run-time ABI for the ARM Architecture"
 * section 4.4.2
 */

#include <stddef.h>
#include <sys/atomics.h>
#include <bionic_futex.h>
#include <bionic_atomic_inline.h>

extern "C" int __cxa_guard_acquire(int volatile * gv)
{
    // 0 -> 2, return 1
    // 2 -> 6, wait and return 0
    // 6 untouched, wait and return 0
    // 1 untouched, return 0
retry:
    if (__atomic_cmpxchg(0, 0x2, gv) == 0) {
        ANDROID_MEMBAR_FULL();
        return 1;
    }
    __atomic_cmpxchg(0x2, 0x6, gv); // Indicate there is a waiter
    __futex_wait(gv, 0x6, NULL);

    if(*gv != 1) // __cxa_guard_abort was called, let every thread try since there is no return code for this condition
        goto retry;

    ANDROID_MEMBAR_FULL();
    return 0;
}

extern "C" void __cxa_guard_release(int volatile * gv)
{
    // 2 -> 1
    // 6 -> 1, and wake
    ANDROID_MEMBAR_FULL();
    if (__atomic_cmpxchg(0x2, 0x1, gv) == 0) {
        return;
    }

    *gv = 0x1;
    __futex_wake(gv, 0x7fffffff);
}

extern "C" void __cxa_guard_abort(int volatile * gv)
{
    ANDROID_MEMBAR_FULL();
    *gv = 0;
    __futex_wake(gv, 0x7fffffff);
}
