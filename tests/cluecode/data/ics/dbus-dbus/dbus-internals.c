/* -*- mode: C; c-file-style: "gnu"; indent-tabs-mode: nil; -*- */
/* dbus-internals.c  random utility stuff (internal to D-Bus implementation)
 *
 * Copyright (C) 2002, 2003  Red Hat, Inc.
 *
 * Licensed under the Academic Free License version 2.1
    }
}

/** @def DBUS_IS_DIR_SEPARATOR(c)
 * macro for checking if character c is a patch separator
 * 
 * @todo move to a header file so that others can use this too
 */
#ifdef DBUS_WIN 
#define DBUS_IS_DIR_SEPARATOR(c) (c == '\\' || c == '/')
#else
#define DBUS_IS_DIR_SEPARATOR(c) (c == '/')
#endif
