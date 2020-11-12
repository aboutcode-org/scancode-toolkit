/*
** JNetLib
** Copyright (C) 2000-2001 Nullsoft, Inc.
** Author: Justin Frankel
** File: util.cpp - JNL implementation of basic network utilities
** License: zlib
*/

#include "netinc.h"

#include "util.h"

int JNL::open_socketlib()
{
#ifdef _WIN32
  WSADATA wsaData;
  if (WSAStartup(MAKEWORD(1, 1), &wsaData)) return 1;
#endif
  return 0;
}
void JNL::close_socketlib()
{
