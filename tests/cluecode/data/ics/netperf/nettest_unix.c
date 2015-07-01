
#ifdef WANT_UNIX
char	nettest_unix_id[]="\
@(#)nettest_unix.c (c) Copyright 1994-2007 Hewlett-Packard Co. Version 2.4.3";
     
/****************************************************************/
  /* first, use the form "first," (see the routine break_args.. */
  
  while ((c= getopt(argc, argv, UNIX_ARGS)) != EOF) {
    switch (c) {
    case '?':	
    case 'h':