/*********************************************************************
 * Universal NetWare library stub.                                   *
 * written by Ulrich Neuman and given to OpenSource copyright-free.  *
 * Extended for CLIB support by Guenter Knauf.                       *
 *********************************************************************
 * $Id: nwlib.c,v 1.1 2007/07/09 22:50:02 gknauf Exp $               *
 *********************************************************************/

#ifdef NETWARE /* Novell NetWare */

#include <stdlib.h>

#ifdef __NOVELL_LIBC__
/* For native LibC-based NLM we need to register as a real lib. */
#include <errno.h>
#include <string.h>
#include <library.h>
#include <netware.h>
#include <screen.h>
#include <nks/thread.h>
#include <nks/synch.h>

