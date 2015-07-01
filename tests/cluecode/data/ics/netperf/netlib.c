char    netlib_id[]="\
@(#)netlib.c (c) Copyright 1993-2007 Hewlett-Packard Company. Version 2.4.3";


 /* these routines for confidence intervals are courtesy of IBM. They */
 /* have been modified slightly for more general usage beyond TCP/UDP */
 /* tests. raj 11/94 I would suspect that this code carries an IBM */
 /* copyright that is much the same as that for the original HP */
 /* netperf code */
int     confidence_iterations; /* for iterations */