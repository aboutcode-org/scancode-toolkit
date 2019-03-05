/*
 
	   Copyright (C) 1993-2007 Hewlett-Packard Company
                         ALL RIGHTS RESERVED.
 
  The enclosed software and documentation includes copyrighted works
  of Hewlett-Packard Co. For as long as you comply with the following
  limitations, you are hereby authorized to (i) use, reproduce, and
  modify the software and documentation, and to (ii) distribute the
  software and documentation, including modifications, for
  non-commercial purposes only.
      
  1.  The enclosed software and documentation is made available at no
      charge in order to advance the general development of
      high-performance networking products.
 
  2.  You may not delete any copyright notices contained in the
      software or documentation. All hard copies, and copies in
      source code or object code form, of the software or
      documentation (including modifications) must contain at least
      one of the copyright notices.
 
  3.  The enclosed software and documentation has not been subjected
      to testing and quality control and is not a Hewlett-Packard Co.
      product. At a future time, Hewlett-Packard Co. may or may not
      offer a version of the software and documentation as a product.
  
  4.  THE SOFTWARE AND DOCUMENTATION IS PROVIDED "AS IS".
      HEWLETT-PACKARD COMPANY DOES NOT WARRANT THAT THE USE,
      REPRODUCTION, MODIFICATION OR DISTRIBUTION OF THE SOFTWARE OR
      DOCUMENTATION WILL NOT INFRINGE A THIRD PARTY'S INTELLECTUAL
      PROPERTY RIGHTS. HP DOES NOT WARRANT THAT THE SOFTWARE OR
      DOCUMENTATION IS ERROR FREE. HP DISCLAIMS ALL WARRANTIES,
      EXPRESS AND IMPLIED, WITH REGARD TO THE SOFTWARE AND THE
      DOCUMENTATION. HP SPECIFICALLY DISCLAIMS ALL WARRANTIES OF
      MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
  
  5.  HEWLETT-PACKARD COMPANY WILL NOT IN ANY EVENT BE LIABLE FOR ANY
      DIRECT, INDIRECT, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES
      (INCLUDING LOST PROFITS) RELATED TO ANY USE, REPRODUCTION,
      MODIFICATION, OR DISTRIBUTION OF THE SOFTWARE OR DOCUMENTATION.
 
*/

#include "netperf_version.h"

char	netserver_id[]="\
@(#)netserver.c (c) Copyright 1993-2007 Hewlett-Packard Co. Version 2.4.3";

 /***********************************************************************/
 /*									*/
 /*	netserver.c							*/
 /*									*/
 /*	This is the server side code for the netperf test package. It	*/
 /* will operate either stand-alone, or as a child of inetd. In this	*/
 /* way, we insure that it can be installed on systems with or without	*/
 /* root permissions (editing inetd.conf). Essentially, this code is	*/
 /* the analog to the netsh.c code.					*/
 /*									*/
 /***********************************************************************/


/************************************************************************/
/*									*/
/*	Global include files						*/
/*									*/
/************************************************************************/
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#if HAVE_STRING_H
# if !STDC_HEADERS && HAVE_MEMORY_H
#  include <memory.h>
# endif
# include <string.h>
#endif
#if HAVE_STRINGS_H
# include <strings.h>
#endif
#if HAVE_LIMITS_H
# include <limits.h>
#endif
#include <sys/types.h>
#include <stdio.h>
#ifndef WIN32
#include <errno.h>
#include <signal.h>
#endif
#if !defined(WIN32) && !defined(__VMS)
#include <sys/ipc.h>
#endif /* !defined(WIN32) && !defined(__VMS) */
#include <fcntl.h>
#ifdef WIN32
#include <time.h>
#include <winsock2.h>
#define netperf_socklen_t socklen_t
/* we need to find some other way to decide to include ws2 */
/* if you are trying to compile on Windows 2000 or NT 4 you will */
/* probably have to define DONT_IPV6 */
#ifndef DONT_IPV6
#include <ws2tcpip.h>
#endif  /* DONT_IPV6 */
#include <windows.h>
#define sleep(x) Sleep((x)*1000)
#else
#ifndef MPE
#include <sys/time.h>
#endif /* MPE */
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <netinet/in.h>
#include <netdb.h>
#include <unistd.h>
#ifndef DONT_WAIT
#include <sys/wait.h>
#endif /* DONT_WAIT */
#endif /* WIN32 */
#include <stdlib.h>
#ifdef __VMS
#include <tcpip$inetdef.h> 
#include <unixio.h> 
#endif /* __VMS */
#include "netlib.h"
#include "nettest_bsd.h"

#ifdef WANT_UNIX
#include "nettest_unix.h"
#endif /* WANT_UNIX */

#ifdef WANT_DLPI
#include "nettest_dlpi.h"
#endif /* WANT_DLPI */

#ifdef WANT_SCTP
#include "nettest_sctp.h"
#endif

#include "netsh.h"

#ifndef DEBUG_LOG_FILE
#ifndef WIN32
#define DEBUG_LOG_FILE "/tmp/netperf.debug"
#else
#define DEBUG_LOG_FILE "c:\\temp\\netperf.debug"
#endif  /* WIN32 */
#endif /* DEBUG_LOG_FILE */

 /* some global variables */

FILE	*afp;
char    listen_port[10];
extern	char	*optarg;
extern	int	optind, opterr;

#ifndef WIN32
#define SERVER_ARGS "dL:n:p:v:V46"
#else
#define SERVER_ARGS "dL:n:p:v:V46I:i:"
#endif

/* perhaps one day we will use this as part of only opening a debug
   log file if debug is set, of course we have to be wary of the base
   use of "where" and so probably always need "where" pointing
   "somewhere" or other. */
void
open_debug_file() 
{
#ifndef WIN32
#ifndef PATH_MAX
#define PATH_MAX MAX_PATH
#endif
  char FileName[PATH_MAX];   /* for opening the debug log file */
  strcpy(FileName, DEBUG_LOG_FILE);

  if (where != NULL) fflush(where);

  snprintf(&FileName[strlen(FileName)], sizeof(FileName) - strlen(FileName), "_%d", getpid());
  if ((where = fopen(FileName, "w")) == NULL) {
    perror("netserver: debug file");
    exit(1);
  }

  chmod(FileName,0644);
#endif

}
 /* This routine implements the "main event loop" of the netperf	*/
 /* server code. Code above it will have set-up the control connection	*/
 /* so it can just merrily go about its business, which is to		*/
 /* "schedule" performance tests on the server.				*/

void 
process_requests()
{
  
  float	temp_rate;
  
  if (debug)    open_debug_file();


  while (1) {
    recv_request();

    switch (netperf_request.content.request_type) {
      
    case DEBUG_ON:
      netperf_response.content.response_type = DEBUG_OK;
      /*  dump_request already present in recv_request; redundant? */
      if (!debug) {
	debug++;
	open_debug_file();
	dump_request();
      }
      send_response();
      break;
      
    case DEBUG_OFF:
      if (debug)
	debug--;
      netperf_response.content.response_type = DEBUG_OK;
      send_response();
      /* +SAF why??? */
      if (!debug) 
      {
	fclose(where);
#if !defined(WIN32) && !defined(MPE) && !defined(__VMS)
	/* For Unix: reopen the debug write file descriptor to "/dev/null" */
	/* and redirect stdout to it.					   */
	fflush (stdout);
	where = fopen ("/dev/null", "w");
	if (where == NULL)
	{
	  perror ("netserver: reopening debug fp for writing: /dev/null");
	  exit   (1);
	}
	if (close (STDOUT_FILENO) == -1)
	{
	  perror ("netserver: closing stdout file descriptor");
	  exit   (1);
	}
	if (dup (fileno (where))  == -1)
	{
	  perror ("netserver: duplicate /dev/null write file descr. to stdout");
	  exit   (1);
	}
#endif /* !WIN32 !MPE !__VMS */
      }
      break;
      
    case CPU_CALIBRATE:
      netperf_response.content.response_type = CPU_CALIBRATE;
      temp_rate = calibrate_local_cpu(0.0);
      bcopy((char *)&temp_rate,
	    (char *)netperf_response.content.test_specific_data,
	    sizeof(temp_rate));
      bcopy((char *)&lib_num_loc_cpus,
	    (char *)netperf_response.content.test_specific_data + sizeof(temp_rate),
	    sizeof(lib_num_loc_cpus));
      if (debug) {
	fprintf(where,"netserver: sending CPU information:");
	fprintf(where,"rate is %g num cpu %d\n",temp_rate,lib_num_loc_cpus);
	fflush(where);
      }
      
      /* we need the cpu_start, cpu_stop in the looper case to kill the */
      /* child proceses raj 7/95 */
      
#ifdef USE_LOOPER
      cpu_start(1);
      cpu_stop(1,&temp_rate);
#endif /* USE_LOOPER */
      
      send_response();
      break;
      
    case DO_TCP_STREAM:
      recv_tcp_stream();
      break;
      
    case DO_TCP_MAERTS:
      recv_tcp_maerts();
      break;
      
    case DO_TCP_RR:
      recv_tcp_rr();
      break;
      
    case DO_TCP_CRR:
      recv_tcp_conn_rr();
      break;
      
    case DO_TCP_CC:
      recv_tcp_cc();
      break;
      
#ifdef DO_1644
    case DO_TCP_TRR:
      recv_tcp_tran_rr();
      break;
#endif /* DO_1644 */
      
#ifdef DO_NBRR
    case DO_TCP_NBRR:
      recv_tcp_nbrr();
      break;
#endif /* DO_NBRR */
      
    case DO_UDP_STREAM:
      recv_udp_stream();
      break;
      
    case DO_UDP_RR:
      recv_udp_rr();
      break;
      
#ifdef WANT_DLPI

    case DO_DLPI_CO_RR:
      recv_dlpi_co_rr();
      break;
      
    case DO_DLPI_CL_RR:
      recv_dlpi_cl_rr();
      break;

    case DO_DLPI_CO_STREAM:
      recv_dlpi_co_stream();
      break;

    case DO_DLPI_CL_STREAM:
      recv_dlpi_cl_stream();
      break;

#endif /* WANT_DLPI */

#ifdef WANT_UNIX

    case DO_STREAM_STREAM:
      recv_stream_stream();
      break;
      
    case DO_STREAM_RR:
      recv_stream_rr();
      break;
      
    case DO_DG_STREAM:
      recv_dg_stream();
      break;
      
    case DO_DG_RR:
      recv_dg_rr();
      break;
      
#endif /* WANT_UNIX */

#ifdef WANT_XTI
    case DO_XTI_TCP_STREAM:
      recv_xti_tcp_stream();
      break;
      
    case DO_XTI_TCP_RR:
      recv_xti_tcp_rr();
      break;
      
    case DO_XTI_UDP_STREAM:
      recv_xti_udp_stream();
      break;
      
    case DO_XTI_UDP_RR:
      recv_xti_udp_rr();
      break;

#endif /* WANT_XTI */

#ifdef WANT_SCTP
    case DO_SCTP_STREAM:
      recv_sctp_stream();
      break;
      
    case DO_SCTP_STREAM_MANY:
      recv_sctp_stream_1toMany();
      break;

    case DO_SCTP_RR:
      recv_sctp_rr();
      break;

    case DO_SCTP_RR_MANY:
      recv_sctp_rr_1toMany();
      break;
#endif

#ifdef WANT_SDP
    case DO_SDP_STREAM:
      recv_sdp_stream();
      break;

    case DO_SDP_MAERTS:
      recv_sdp_maerts();
      break;

    case DO_SDP_RR:
      recv_sdp_rr();
      break;
#endif 

    default:
      fprintf(where,"unknown test number %d\n",
	      netperf_request.content.request_type);
      fflush(where);
      netperf_response.content.serv_errno=998;
      send_response();
      break;
      
    }
  }
}

/*	
 set_up_server()

 set-up the server listen socket. we only call this routine if the 
 user has specified a port number on the command line or we believe we
 are not a child of inetd or its platform-specific equivalent */

/*KC*/

void 
set_up_server(char hostname[], char port[], int af)
{ 

  struct addrinfo     hints;
  struct addrinfo     *local_res;
  struct addrinfo     *local_res_temp;

  struct sockaddr_storage     peeraddr;
  netperf_socklen_t                 peeraddr_len = sizeof(peeraddr);
  
  SOCKET server_control;
  int on=1;
  int count;
  int error;
  int not_listening;

#if !defined(WIN32) && !defined(MPE) && !defined(__VMS)
  FILE *rd_null_fp;    /* Used to redirect from "/dev/null". */
  FILE *wr_null_fp;    /* Used to redirect to   "/dev/null". */
#endif /* !WIN32 !MPE !__VMS */

  if (debug) {
    fprintf(stderr,
            "set_up_server called with host '%s' port '%s' remfam %d\n",
            hostname,
	    port,
            af);
    fflush(stderr);
  }

  memset(&hints,0,sizeof(hints));
  hints.ai_family = af;
  hints.ai_socktype = SOCK_STREAM;
  hints.ai_protocol = IPPROTO_TCP;
  hints.ai_flags = AI_PASSIVE;

  count = 0;
  do {
    error = getaddrinfo((char *)hostname,
                        (char *)port,
                        &hints,
                        &local_res);
    count += 1;
    if (error == EAI_AGAIN) {
      if (debug) {
        fprintf(stderr,"Sleeping on getaddrinfo EAI_AGAIN\n");
        fflush(stderr);
      }
      sleep(1);
    }
  } while ((error == EAI_AGAIN) && (count <= 5));

  if (error) {
    fprintf(stderr,
	    "set_up_server: could not resolve remote '%s' port '%s' af %d",
	    hostname,
	    port,
	    af);
    fprintf(stderr,"\n\tgetaddrinfo returned %d %s\n",
	    error,
	    gai_strerror(error));
    exit(-1);
  }

  if (debug) {
    dump_addrinfo(stderr, local_res, hostname, port, af);
  }

  not_listening = 1;
  local_res_temp = local_res;

  while((local_res_temp != NULL) && (not_listening)) {

    fprintf(stderr,
	    "Starting netserver at port %s\n",
	    port);

    server_control = socket(local_res_temp->ai_family,SOCK_STREAM,0);

    if (server_control == INVALID_SOCKET) {
      perror("set_up_server could not allocate a socket");
      exit(-1);
    }

    /* happiness and joy, keep going */
    if (setsockopt(server_control, 
		   SOL_SOCKET, 
		   SO_REUSEADDR, 
		   (char *)&on , 
		   sizeof(on)) == SOCKET_ERROR) {
      if (debug) {
	perror("warning: set_up_server could not set SO_REUSEADDR");
      }
    }
    /* still happy and joyful */

    if ((bind (server_control, 
	       local_res_temp->ai_addr, 
	       local_res_temp->ai_addrlen) != SOCKET_ERROR) &&
	(listen (server_control,5) != SOCKET_ERROR))  {
      not_listening = 0;
      break;
    }
    else {
      /* we consider a bind() or listen() failure a transient and try
	 the next address */
      if (debug) {
	perror("warning: set_up_server failed a bind or listen call\n");
      }
      local_res_temp = local_res_temp->ai_next;
      continue;
    }
  }

  if (not_listening) {
    fprintf(stderr,
	    "set_up_server could not establish a listen endpoint for %s port %s with family %s\n",
	    host_name,
	    port,
	    inet_ftos(af));
    fflush(stderr);
    exit(-1);
  }
  else {
    printf("Starting netserver at hostname %s port %s and family %s\n",
	   hostname,
	   port,
	   inet_ftos(af));
  }

  /*
    setpgrp();
    */

#if !defined(WIN32) && !defined(MPE) && !defined(__VMS)
  /* Flush the standard I/O file descriptors before forking. */
  fflush (stdin);
  fflush (stdout);
  fflush (stderr);
  switch (fork())
    {
    case -1:  	
      perror("netperf server error");
      exit(1);
      
    case 0:	
      /* Redirect stdin from "/dev/null". */
      rd_null_fp = fopen ("/dev/null", "r");
      if (rd_null_fp == NULL)
      {
	perror ("netserver: opening for reading: /dev/null");
	exit   (1);
      }
      if (close (STDIN_FILENO) == -1)
      {
	perror ("netserver: closing stdin file descriptor");
	exit   (1);
      }
      if (dup (fileno (rd_null_fp)) == -1)
      {
	perror ("netserver: duplicate /dev/null read file descr. to stdin");
	exit   (1);
      }

      /* Redirect stdout to the debug write file descriptor. */
      if (close (STDOUT_FILENO) == -1)
      {
	perror ("netserver: closing stdout file descriptor");
	exit   (1);
      }
      if (dup (fileno (where))  == -1)
      {
	perror ("netserver: duplicate the debug write file descr. to stdout");
	exit   (1);
      }

      /* Redirect stderr to "/dev/null". */
      wr_null_fp = fopen ("/dev/null", "w");
      if (wr_null_fp == NULL)
      {
	perror ("netserver: opening for writing: /dev/null");
	exit   (1);
      }
      if (close (STDERR_FILENO) == -1)
      {
	perror ("netserver: closing stderr file descriptor");
	exit   (1);
      }
      if (dup (fileno (wr_null_fp))  == -1)
      {
	perror ("netserver: dupicate /dev/null write file descr. to stderr");
	exit   (1);
      }
 
#ifndef NO_SETSID
      setsid();
#else
      setpgrp();
#endif /* NO_SETSID */

 /* some OS's have SIGCLD defined as SIGCHLD */
#ifndef SIGCLD
#define SIGCLD SIGCHLD
#endif /* SIGCLD */

      signal(SIGCLD, SIG_IGN);
      
#endif /* !WIN32 !MPE !__VMS */

      for (;;)
	{
	  if ((server_sock=accept(server_control,
				  (struct sockaddr *)&peeraddr,
				  &peeraddr_len)) == INVALID_SOCKET)
	    {
	      printf("server_control: accept failed errno %d\n",errno);
	      exit(1);
	    }
#if defined(MPE) || defined(__VMS)
	  /*
	   * Since we cannot fork this process , we cant fire any threads
	   * as they all share the same global data . So we better allow
	   * one request at at time 
	   */
	  process_requests() ;
#elif WIN32
		{
			BOOL b;
			char cmdline[80];
			PROCESS_INFORMATION pi;
			STARTUPINFO si;
			int i;

			memset(&si, 0 , sizeof(STARTUPINFO));
			si.cb = sizeof(STARTUPINFO);

			/* Pass the server_sock as stdin for the new process. */
			/* Hopefully this will continue to be created with the OBJ_INHERIT attribute. */
			si.hStdInput = (HANDLE)server_sock;
			si.hStdOutput = GetStdHandle(STD_OUTPUT_HANDLE);
			si.hStdError = GetStdHandle(STD_ERROR_HANDLE);
			si.dwFlags = STARTF_USESTDHANDLES;

			/* Build cmdline for child process */
			strcpy(cmdline, program);
			if (verbosity > 1) {
				snprintf(&cmdline[strlen(cmdline)], sizeof(cmdline) - strlen(cmdline), " -v %d", verbosity);
			}
			for (i=0; i < debug; i++) {
				snprintf(&cmdline[strlen(cmdline)], sizeof(cmdline) - strlen(cmdline), " -d");
			}
			snprintf(&cmdline[strlen(cmdline)], sizeof(cmdline) - strlen(cmdline), " -I %x", (int)(UINT_PTR)server_sock);
			snprintf(&cmdline[strlen(cmdline)], sizeof(cmdline) - strlen(cmdline), " -i %x", (int)(UINT_PTR)server_control);
			snprintf(&cmdline[strlen(cmdline)], sizeof(cmdline) - strlen(cmdline), " -i %x", (int)(UINT_PTR)where);

			b = CreateProcess(NULL,	 /* Application Name */
					cmdline,
					NULL,    /* Process security attributes */
					NULL,    /* Thread security attributes */
					TRUE,    /* Inherit handles */
					0,	   /* Creation flags  PROCESS_QUERY_INFORMATION,  */
					NULL,    /* Enviornment */
					NULL,    /* Current directory */
					&si,	   /* StartupInfo */
					&pi);
			if (!b)
			{
				perror("CreateProcessfailure: ");
				exit(1);
			}

			/* We don't need the thread or process handles any more; let them */
			/* go away on their own timeframe. */

			CloseHandle(pi.hThread);
			CloseHandle(pi.hProcess);

			/* And close the server_sock since the child will own it. */

			close(server_sock);
		}
#else
      signal(SIGCLD, SIG_IGN);
	  
	  switch (fork())
	    {
	    case -1:
	      /* something went wrong */
	      exit(1);
	    case 0:
	      /* we are the child process */
	      close(server_control);
	      process_requests();
	      exit(0);
	      break;
	    default:
	      /* we are the parent process */
	      close(server_sock);
	      /* we should try to "reap" some of our children. on some */
	      /* systems they are being left as defunct processes. we */
	      /* will call waitpid, looking for any child process, */
	      /* with the WNOHANG feature. when waitpid return a zero, */
	      /* we have reaped all the children there are to reap at */
	      /* the moment, so it is time to move on. raj 12/94 */
#ifndef DONT_WAIT
#ifdef NO_SETSID
	      /* Only call "waitpid()" if "setsid()" is not used. */
	      while(waitpid(-1, NULL, WNOHANG) > 0) { }
#endif /* NO_SETSID */
#endif /* DONT_WAIT */
	      break;
	    }
#endif /* !WIN32 !MPE !__VMS */  
	} /*for*/
#if !defined(WIN32) && !defined(MPE) && !defined(__VMS)
      break; /*case 0*/
      
    default: 
      exit (0);
      
    }
#endif /* !WIN32 !MPE !__VMS */  
}

#ifdef WIN32

  /* With Win2003, WinNT's POSIX subsystem is gone and hence so is */
  /* fork. */

  /* But hopefully the kernel support will continue to exist for some */
  /* time. */

  /* We are not counting on the child address space copy_on_write */
  /* support, since it isn't exposed except through the NT native APIs */
  /* (which is not public). */

  /* We will try to use the InheritHandles flag in CreateProcess.  It */
  /* is in the public API, though it is documented as "must be FALSE". */

  /* So where we would have forked, we will now create a new process. */
  /* I have added a set of command line switches to specify a list of */
  /* handles that the child should close since they shouldn't have */
  /* been inherited ("-i#"), and a single switch to specify the handle */
  /* for the server_sock ("I#"). */

  /* A better alternative would be to re-write NetPerf to be */
  /* multi-threaded; i.e., move all of the various NetPerf global */
  /* variables in to thread specific structures.  But this is a bigger */
  /* effort than I want to tackle at this time.  (And I doubt that the */
  /* HP-UX author sees value in this effort). */

#endif

int _cdecl
main(int argc, char *argv[])
{

  int	c;
  int   not_inetd = 0;
#ifdef WIN32
  BOOL  child = FALSE;
#endif
  char arg1[BUFSIZ], arg2[BUFSIZ];
#ifndef PATH_MAX
#define PATH_MAX MAX_PATH
#endif
  char FileName[PATH_MAX];   /* for opening the debug log file */

  struct sockaddr name;
  netperf_socklen_t namelen = sizeof(name);
  

#ifdef WIN32
	WSADATA	wsa_data ;

	/* Initialize the winsock lib ( version 2.2 ) */
	if ( WSAStartup(MAKEWORD(2,2), &wsa_data) == SOCKET_ERROR ){
		printf("WSAStartup() failed : %d\n", GetLastError()) ;
		return 1 ;
	}
#endif /* WIN32 */

	/* Save away the program name */
	program = (char *)malloc(strlen(argv[0]) + 1);
	if (program == NULL) {
		printf("malloc(%d) failed!\n", strlen(argv[0]) + 1);
		return 1 ;
	}
	strcpy(program, argv[0]);

  netlib_init();
  
  /* Scan the command line to see if we are supposed to set-up our own */
  /* listen socket instead of relying on inetd. */

  /* first set a copy of initial values */
  strncpy(local_host_name,"0.0.0.0",sizeof(local_host_name));
  local_address_family = AF_UNSPEC;
  strncpy(listen_port,TEST_PORT,sizeof(listen_port));

  while ((c = getopt(argc, argv, SERVER_ARGS)) != EOF) {
    switch (c) {
    case '?':
    case 'h':
      print_netserver_usage();
      exit(1);
    case 'd':
      /* we want to set the debug file name sometime */
      debug++;
      break;
    case 'L':
      not_inetd = 1;
      break_args_explicit(optarg,arg1,arg2);
      if (arg1[0]) {
	strncpy(local_host_name,arg1,sizeof(local_host_name));
      }
      if (arg2[0]) {
	local_address_family = parse_address_family(arg2);
	/* if only the address family was set, we may need to set the
	   local_host_name accordingly. since our defaults are IPv4
	   this should only be necessary if we have IPv6 support raj
	   2005-02-07 */  
#if defined (AF_INET6)
	if (!arg1[0]) {
	  strncpy(local_host_name,"::0",sizeof(local_host_name));
	}
#endif
      }
      break;
    case 'n':
      shell_num_cpus = atoi(optarg);
      if (shell_num_cpus > MAXCPUS) {
	fprintf(stderr,
		"netserver: This version can only support %d CPUs. Please",
		MAXCPUS);
	fprintf(stderr,
		"           increase MAXCPUS in netlib.h and recompile.\n");
	fflush(stderr);
	exit(1);
      }
      break;
    case 'p':
      /* we want to open a listen socket at a */
      /* specified port number */
      strncpy(listen_port,optarg,sizeof(listen_port));
      not_inetd = 1;
      break;
    case '4':
      local_address_family = AF_INET;
      break;
    case '6':
#if defined(AF_INET6)
      local_address_family = AF_INET6;
      strncpy(local_host_name,"::0",sizeof(local_host_name));
#else
      local_address_family = AF_UNSPEC;
#endif
      break;
    case 'v':
      /* say how much to say */
      verbosity = atoi(optarg);
      break;
    case 'V':
      printf("Netperf version %s\n",NETPERF_VERSION);
      exit(0);
      break;
#ifdef WIN32
/*+*+SAF */
	case 'I':
		child = TRUE;
		/* This is the handle we expect to inherit. */
		/*+*+SAF server_sock = (HANDLE)atoi(optarg); */
		break;
	case 'i':
		/* This is a handle we should NOT inherit. */
		/*+*+SAF CloseHandle((HANDLE)atoi(optarg)); */
		break;
#endif

    }
  }

  /* +*+SAF I need a better way to find inherited handles I should close! */
  /* +*+SAF Use DuplicateHandle to force inheritable attribute (or reset it)? */

/*  unlink(DEBUG_LOG_FILE); */

  strcpy(FileName, DEBUG_LOG_FILE);
    
#ifndef WIN32
  snprintf(&FileName[strlen(FileName)], sizeof(FileName) - strlen(FileName), "_%d", getpid());
  if ((where = fopen(FileName, "w")) == NULL) {
    perror("netserver: debug file");
    exit(1);
  }
#else
  {
    
    if (child) {
      snprintf(&FileName[strlen(FileName)], sizeof(FileName) - strlen(FileName), "_%x", getpid());
    }
    
    /* Hopefully, by closing stdout & stderr, the subsequent
       fopen calls will get mapped to the correct std handles. */
    fclose(stdout);
    
    if ((where = fopen(FileName, "w")) == NULL) {
      perror("netserver: fopen of debug file as new stdout failed!");
      exit(1);
    }
    
    fclose(stderr);
    
    if ((where = fopen(FileName, "w")) == NULL) {
      fprintf(stdout, "fopen of debug file as new stderr failed!\n");
      exit(1);
    }
  }
#endif
 
#ifndef WIN32 
  chmod(DEBUG_LOG_FILE,0644);
#endif
  
#if WIN32
  if (child) {
	  server_sock = (SOCKET)GetStdHandle(STD_INPUT_HANDLE);
  }
#endif

  /* if we are not a child of an inetd or the like, then we should
   open a socket and hang listens off of it. otherwise, we should go
   straight into processing requests. the do_listen() routine will sit
   in an infinite loop accepting connections and forking child
   processes. the child processes will call process_requests */
  
  /* If fd 0 is not a socket then assume we're not being called */
  /* from inetd and start server socket on the default port. */
  /* this enhancement comes from vwelch@ncsa.uiuc.edu (Von Welch) */
  if (not_inetd) {
    /* the user specified a port number on the command line */
    set_up_server(local_host_name,listen_port,local_address_family);
  }
#ifdef WIN32
  /* OK, with Win2003 WinNT's POSIX subsystem is gone, and hence so is */
  /* fork.  But hopefully the kernel support will continue to exist */
  /* for some time.  We are not counting on the address space */
  /* copy_on_write support, since it isn't exposed except through the */
  /* NT native APIs (which are not public).  We will try to use the */
  /* InheritHandles flag in CreateProcess though since this is public */
  /* and is used for more than just POSIX so hopefully it won't go */
  /* away. */
  else if (TRUE) {
    if (child) {
      process_requests();
    } else {
      strncpy(listen_port,TEST_PORT,sizeof(listen_port));
      set_up_server(local_host_name,listen_port,local_address_family);
    }
  }
#endif
#if !defined(__VMS)
  else if (getsockname(0, &name, &namelen) == SOCKET_ERROR) {
    /* we may not be a child of inetd */
    if (errno == ENOTSOCK) {
      strncpy(listen_port,TEST_PORT,sizeof(listen_port));
      set_up_server(local_host_name,listen_port,local_address_family);
    }
  }
#endif /* !defined(__VMS) */
  else {
    /* we are probably a child of inetd, or are being invoked via the
       VMS auxilliarly server mechanism */
#if !defined(__VMS)
    server_sock = 0;
#else
    if ( (server_sock = socket(TCPIP$C_AUXS, SOCK_STREAM, 0)) == INVALID_SOCKET ) 
    { 
      perror("Failed to grab aux server socket" ); 
      exit(1); 
    } 
  
#endif /* !defined(__VMS) */
    process_requests();
  }
#ifdef WIN32
	/* Cleanup the winsock lib */
	WSACleanup();
#endif

  return(0);
}
