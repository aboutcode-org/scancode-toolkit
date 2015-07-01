
#ifdef SYSV
#define VersionStr "Gif library module,\t\tEric S. Raymond\n\
                    (C) Copyright 1997 Eric S. Raymond\n"
#else
#define VersionStr PROGRAM_NAME "    IBMPC " GIF_LIB_VERSION \
                    "    Eric S. Raymond,    " __DATE__ ",   " \
                    __TIME__ "\n" "(C) Copyright 1997 Eric S. Raymond\n"
#endif /* SYSV */
