
#ifdef WANT_DLPI
char	nettest_dlpi_id[]="\
@(#)nettest_dlpi.c (c) Copyright 1993,1995,2004 Hewlett-Packard Co. Version 2.4.3";

#include <sys/types.h>
#define DLPI_ARGS "D:hM:m:p:r:s:W:w:"
  
  while ((c= getopt(argc, argv, DLPI_ARGS)) != EOF) {
    switch (c) {
    case '?':	
    case 'h':