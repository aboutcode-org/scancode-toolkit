#ifndef lint
char	nettest_id[]="\
@(#)nettest_bsd.c (c) Copyright 1993-2004 Hewlett-Packard Co. Version 2.4.3";
#endif /* lint */

  /* first, use the form "first," (see the routine break_args.. */
  
  while ((c= getopt(argc, argv, SOCKETS_ARGS)) != EOF) {
    switch (c) {
    case '?':	
    case '4':