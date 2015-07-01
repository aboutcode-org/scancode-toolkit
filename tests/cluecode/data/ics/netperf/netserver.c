/*
 
	   Copyright (C) 1993-2007 Hewlett-Packard Company
                         ALL RIGHTS RESERVED.
 
  The enclosed software and documentation includes copyrighted works
  of Hewlett-Packard Co. For as long as you comply with the following
  limitations, you are hereby authorized to (i) use, reproduce, and
      charge in order to advance the general development of
      high-performance networking products.
 
  2.  You may not delete any copyright notices contained in the
      software or documentation. All hard copies, and copies in
      source code or object code form, of the software or
      documentation (including modifications) must contain at least
      one of the copyright notices.
 
  3.  The enclosed software and documentation has not been subjected
#include "netperf_version.h"

char	netserver_id[]="\
@(#)netserver.c (c) Copyright 1993-2007 Hewlett-Packard Co. Version 2.4.3";

 /***********************************************************************/
  strncpy(listen_port,TEST_PORT,sizeof(listen_port));

  while ((c = getopt(argc, argv, SERVER_ARGS)) != EOF) {
    switch (c) {
    case '?':
    case 'h':