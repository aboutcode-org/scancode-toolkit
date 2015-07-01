/* gzappend -- command to append to a gzip file

  Copyright (C) 2003 Mark Adler, all rights reserved
  version 1.1, 4 Nov 2003

 *
 * 1.0  19 Oct 2003     - First version
 * 1.1   4 Nov 2003     - Expand and clarify some comments and notes
 *                      - Add version and copyright to help
 *                      - Send help to stdout instead of stderr
 *                      - Add some preemptive typecasts

    /* provide usage if no arguments */
    if (*argv == NULL) {
        printf("gzappend 1.1 (4 Nov 2003) Copyright (C) 2003 Mark Adler\n");
        printf(
            "usage: gzappend [-level] file.gz [ addthis [ andthis ... ]]\n");