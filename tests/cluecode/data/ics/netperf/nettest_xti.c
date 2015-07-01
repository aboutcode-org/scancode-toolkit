#ifdef WANT_XTI
#ifndef lint
char	nettest_xti_id[]="\
@(#)nettest_xti.c (c) Copyright 1995-2007 Hewlett-Packard Co. Version 2.4.3";
#else
#define DIRTY
  /* first, use the form "first," (see the routine break_args.. */
  
  while ((c= getopt(argc, argv, XTI_ARGS)) != EOF) {
    switch (c) {
    case '?':	
    case 'h':