#ifndef lint
char	nettest_sctp[]="\
@(#)nettest_sctp.c (c) Copyright 2005-2007 Hewlett-Packard Co. Version 2.4.3";
#else
#define DIRTY
  /* first, use the form "first," (see the routine break_args.. */
  
  while ((c= getopt(argc, argv, SOCKETS_ARGS)) != EOF) {
    switch (c) {
    case '?':	
    case '4':