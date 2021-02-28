/*
 * RageIRCd: an advanced Internet Relay Chat daemon (ircd).
 * (C) 2000-2005 the RageIRCd Development Team, all rights reserved.
 *
 * This software is free, licensed under the General Public License.
 * Please refer to doc/LICENSE and doc/README for further details.
 *
 * $Id: m_knock.c,v 1.33.2.2 2005/01/15 23:53:32 amcwilliam Exp $
 */

#include "config.h"
#include "struct.h"
#include "common.h"
#include "sys.h"
#include "numeric.h"
#include "msg.h"
#include "channel.h"
#include "h.h"
#include "memory.h"
#include "modules.h"
#include "xmode.h"
#include <time.h>
#include <sys/stat.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
