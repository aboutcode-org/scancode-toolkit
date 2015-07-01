# Define some macros required for proper operation of code in lib/*.c
# on MSDOS/Windows systems.

# Copyright (C) 2000, 2001, 2004 Free Software Foundation, Inc.
# This file is free software; the Free Software Foundation
# gives unlimited permission to copy and/or distribute it,

    AH_VERBATIM(ISSLASH,
    [#if FILE_SYSTEM_BACKSLASH_IS_FILE_NAME_SEPARATOR
# define ISSLASH(C) ((C) == '/' || (C) == '\\')
#else
# define ISSLASH(C) ((C) == '/')
#endif])
