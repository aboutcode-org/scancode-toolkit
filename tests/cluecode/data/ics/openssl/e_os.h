/* e_os.h */
/* Copyright (C) 1995-1998 Eric Young (eay@cryptsoft.com)
 * All rights reserved.
 *
 * the following conditions are aheared to.  The following conditions
 * apply to all code found in this distribution, be it the RC4, RSA,
 * lhash, DES, etc., code; not just the SSL code.  The SSL documentation
 * included with this distribution is covered by the same copyright terms
 * except that the holder is Tim Hudson (tjh@cryptsoft.com).
 * 
 * Copyright remains Eric Young's, and as such any Copyright notices in
 * the code are not to be removed.
 * If this package is used in a product, Eric Young should be given attribution
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
#elif defined(OPENSSL_SYS_VXWORKS)
#define get_last_socket_error()	errno
#define clear_socket_error()	errno=0
#define ioctlsocket(a,b,c)	    ioctl((a),(b),(int)(c))
#define closesocket(s)		    close(s)
#define readsocket(s,b,n)	    read((s),(b),(n))
#define get_last_socket_error() errno
#define clear_socket_error()    errno=0
#define FIONBIO SO_NONBLOCK
#define ioctlsocket(a,b,c)		  setsockopt((a),SOL_SOCKET,(b),(c),sizeof(*(c)))
#define readsocket(s,b,n)       recv((s),(b),(n),0)
#define writesocket(s,b,n)      send((s),(b),(n),0)
#        define socket(d,t,p)	((int)socket(d,t,p))
#        define accept(s,f,l)	((int)accept(s,f,l))
#      endif
#      define SSLeay_Write(a,b,c)	send((a),(b),(c),0)
#      define SSLeay_Read(a,b,c)	recv((a),(b),(c),0)
#      define SHUTDOWN(fd)		{ shutdown((fd),0); closesocket(fd); }
#      define SHUTDOWN2(fd)		{ shutdown((fd),2); closesocket(fd); }
#  elif defined(MAC_OS_pre_X)

#    include "MacSocket.h"
#    define SSLeay_Write(a,b,c)		MacSocket_send((a),(b),(c))
#    define SSLeay_Read(a,b,c)		MacSocket_recv((a),(b),(c),true)
#    define SHUTDOWN(fd)		MacSocket_close(fd)
#    define SHUTDOWN2(fd)		MacSocket_close(fd)
#      else
#        include <novsock2.h>
#      endif
#      define SSLeay_Write(a,b,c)   send((a),(b),(c),0)
#      define SSLeay_Read(a,b,c) recv((a),(b),(c),0)
#      define SHUTDOWN(fd)    { shutdown((fd),0); closesocket(fd); }
#      define SHUTDOWN2(fd)      { shutdown((fd),2); closesocket(fd); }
#      endif
#    endif

#    define SSLeay_Read(a,b,c)     read((a),(b),(c))
#    define SSLeay_Write(a,b,c)    write((a),(b),(c))
#    define SHUTDOWN(fd)    { shutdown((fd),0); closesocket((fd)); }
#    define SHUTDOWN2(fd)   { shutdown((fd),2); closesocket((fd)); }