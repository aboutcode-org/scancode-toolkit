/*
* Dynamic function tracing support.
*
* Copyright (C) 2008 Shaohua Li <shaohua.li@intel.com>
*
* For licencing details, see COPYING.
*
* Defines low-level handling of mcount calls when the kernel
* is compiled with the -pg flag. When using dynamic ftrace, the
* mcount call-sites get patched lazily with NOP till they are
* enabled. All code mutation routines here take effect atomically.
*/
