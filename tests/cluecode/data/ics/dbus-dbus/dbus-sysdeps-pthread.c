/* -*- mode: C; c-file-style: "gnu"; indent-tabs-mode: nil; -*- */
/* dbus-sysdeps-pthread.c Implements threads using pthreads (internal to libdbus)
 * 
 * Copyright (C) 2002, 2003, 2006  Red Hat, Inc.
 *
 * Licensed under the Academic Free License version 2.1
#define DBUS_MUTEX(m)         ((DBusMutex*) m)
#define DBUS_MUTEX_PTHREAD(m) ((DBusMutexPThread*) m)

#define DBUS_COND_VAR(c)         ((DBusCondVar*) c)
#define DBUS_COND_VAR_PTHREAD(c) ((DBusCondVarPThread*) c)

