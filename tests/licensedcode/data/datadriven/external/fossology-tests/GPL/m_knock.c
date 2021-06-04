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

Module MOD_HEADER(m_knock) = {
	"m_knock",
	"/KNOCK command",
	6, "$Revision: 1.33.2.2 $"
};

int MOD_LOAD(m_knock)()
{
	if (register_command(&MOD_HEADER(m_knock), &CMD_KNOCK, m_knock) == NULL) {
		return MOD_FAILURE;
	}
	return MOD_SUCCESS;
}

int MOD_UNLOAD(m_knock)()
{
	return MOD_SUCCESS;
}

/*
 * m_knock
 *	parv[0] = sender prefix
 *	parv[1] = channel name
 *	parv[2] = optional channel key
 */
int m_knock(aClient *cptr, aClient *sptr, int parc, char *parv[])
{
	aChannel *chptr;
	char *p, *name, *key;

	if (!GeneralConfig.enable_knock) {
		send_me_numeric(sptr, ERR_FUNCDISABLED, "KNOCK");
		return 0;
	}
	if (parc < 2 || BadPtr(parv[1])) {
		send_me_numeric(sptr, ERR_NEEDMOREPARAMS, "KNOCK");
		return 0;
	}

	name = parv[1];
	key = (parc > 2 && !BadPtr(parv[2])) ? parv[2] : NULL;

	if ((p = strchr(name, ',')) != NULL) {
		*p = '\0';
	}
	if (BadPtr(p)) {
		send_me_numeric(sptr, ERR_NEEDMOREPARAMS, "KNOCK");
		return 0;
	}

	if (!IsChanPrefix(*name)) {
		send_me_numeric(sptr, ERR_NOSUCHCHANNEL, name);
		return 0;
	}
	if (!check_channel_name(sptr, parv[1])) {
		send_me_numeric(sptr, ERR_BADCHANNAME, parv[1]);
		return 0;
	}

	if ((chptr = find_channel(name, NULL)) == NULL) {
		send_me_numeric(sptr, ERR_NOSUCHCHANNEL, name);
		return 0;
	}

	if (IsMember(sptr, chptr)) {
		send_me_numeric(sptr, RPL_KNOCKONCHAN, chptr->chname);
		return 0;
	}

	if (!(chptr->mode.mode & CMODE_INVITEONLY) && ((!chptr->mode.limit || (chptr->mode.limit && chptr->users < chptr->mode.limit))
	  || ((chptr->mode.mode & CMODE_INVITEONLY) && is_invited(sptr, chptr)))) {
		send_me_numeric(sptr, RPL_KNOCKCHANOPEN, chptr->chname);
		return 0;
	}
	if (*chptr->mode.key != '\0' && (key == NULL || irccmp(chptr->mode.key, key))) {
		send_me_numeric(sptr, ERR_BADCHANNELKEY, chptr->chname);
		return 0;
	}
	if (chptr->mode.mode & CMODE_PRIVATE) {
		send_me_numeric(sptr, ERR_CANNOTSENDTOCHAN, chptr->chname, "channel is private");
		return 0;
	}

	if (is_banned(sptr, chptr, NULL)) {
		send_me_numeric(sptr, ERR_BANNEDFROMCHAN, chptr->chname);
		return 0;
	}

	if (FloodConfig.knock_delay && ((chptr->last_knock + FloodConfig.knock_delay) > timeofday)) {
		send_me_numeric(sptr, RPL_KNOCKWAIT, chptr->chname,
			FloodConfig.knock_delay - (timeofday - chptr->last_knock));
		return 0;
	}

	chptr->last_knock = timeofday;

	sendto_channel_local_msg_butone(NULL, &me, chptr, CMODE_HALFOP,
		&CMD_NOTICE, "%%%s :%s!%s@%s has requested an invite into %s", chptr->chname,
		sptr->name, sptr->username, MaskedHost(sptr), chptr->chname);

	send_me_numeric(sptr, RPL_KNOCKDELIVERED, chptr->chname);

	return 0;
}
