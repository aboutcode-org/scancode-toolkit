 * Helper routines to provide target memory access for semihosting
 * syscalls in system emulation mode.
 *
 * Copyright (c) 2007 CodeSourcery.
 *
 * This code is licenced under the GPL
        cpu_memory_rw_debug(env, addr, &c, 1, 0);
        addr++;
        *(p++) = c;
    } while (c);
    return s;
}