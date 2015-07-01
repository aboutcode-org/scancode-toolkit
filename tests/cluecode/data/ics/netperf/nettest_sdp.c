#ifndef lint
char	nettest_sdp[]="\
@(#)nettest_sdp.c (c) Copyright 2007 Hewlett-Packard Co. Version 2.4.4";
#else
#define DIRTY
  /* first, use the form "first," (see the routine break_args.. */
  
  while ((c= getopt(argc, argv, SOCKETS_ARGS)) != EOF) {
    switch (c) {
    case '?':	
    case '4':