/* -*- mode: C; c-file-style: "gnu"; indent-tabs-mode: nil; -*- */
/* dbus-internals.h  random utility stuff (internal to D-Bus implementation)
 *
 * Copyright (C) 2002, 2003  Red Hat, Inc.
 *
 * Licensed under the Academic Free License version 2.1
#undef	ABS
#define ABS(a)	   (((a) < 0) ? -(a) : (a))

#define _DBUS_ISASCII(c) ((c) != '\0' && (((c) & ~0x7f) == 0))

typedef void (* DBusForeachFunction) (void *element,