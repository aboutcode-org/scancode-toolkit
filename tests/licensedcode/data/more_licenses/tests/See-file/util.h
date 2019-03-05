/*
** JNetLib
** Copyright (C) 2000-2001 Nullsoft, Inc.
** Author: Justin Frankel
** File: util.h - JNL interface for basic network utilities
** License: see License.txt
**
** routines you may be interested in:
**   JNL::open_socketlib(); 
**    opens the socket library. Call this once before using any network
**    code. If you create a new thread, call this again. Only really an
**    issue for Win32 support, but use it anyway for portability/
**
**   JNL::close_Socketlib();
**    closes the socketlib. Call this when you're done with the network,
**    after all your JNetLib objects have been destroyed.
**
**   unsigned long JNL::ipstr_to_addr(const char *cp); 
**    gives you the integer representation of a ip address in dotted 
**    decimal form.
**
**  JNL::addr_to_ipstr(unsigned long addr, char *host, int maxhostlen);
**    gives you the dotted decimal notation of an integer ip address.
**
*/

#ifndef _UTIL_H_
#define _UTIL_H_

int my_atoi(char *p);
__int64 myatoi64(char *s);
void myitoa64(__int64 i, char *buffer);
void mini_memset(void *,char,int);
void mini_memcpy(void *,void*,int);

#endif //_UTIL_H_
