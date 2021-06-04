/*-
 * Copyright (c) 2004 INRIA
 * Copyright (c) 2002-2005 Sam Leffler, Errno Consulting
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer,
 *    without modification.
 * 2. Redistributions in binary form must reproduce at minimum a disclaimer
 *    similar to the "NO WARRANTY" disclaimer below ("Disclaimer") and any
 *    redistribution must be conditioned upon including a substantially
 *    similar Disclaimer requirement for further binary redistribution.
 * 3. Neither the names of the above-listed copyright holders nor the names
 *    of any contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * Alternatively, this software may be distributed under the terms of the
 * GNU General Public License ("GPL") version 2 as published by the Free
 * Software Foundation.
 *
 * NO WARRANTY
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF NONINFRINGEMENT, MERCHANTIBILITY
 * AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
 * THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE FOR SPECIAL, EXEMPLARY,
 * OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
 * IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
 * THE POSSIBILITY OF SUCH DAMAGES.
 *
 * $Id: amrr.c 2815 2007-10-31 05:46:45Z proski $
 */

/*
 * AMRR rate control. See:
 * http://www-sop.inria.fr/rapports/sophia/RR-5208.html
 * "IEEE 802.11 Rate Adaptation: A Practical Approach" by
 *    Mathieu Lacage, Hossein Manshaei, Thierry Turletti
 */
#ifndef AUTOCONF_INCLUDED
#include <linux/config.h>
#endif
#include <linux/version.h>
#include <linux/module.h>
#include <linux/init.h>
#include <linux/skbuff.h>
#include <linux/netdevice.h>
#include <linux/random.h>
#include <linux/delay.h>
#include <linux/cache.h>
#include <linux/sysctl.h>
#include <linux/proc_fs.h>
#include <linux/if_arp.h>

#include <asm/uaccess.h>

#include <net80211/if_media.h>
#include <net80211/ieee80211_var.h>
#include <net80211/ieee80211_rate.h>

#include "if_athvar.h"
#include "ah_desc.h"

#include "amrr.h"

#define	AMRR_DEBUG
#ifdef AMRR_DEBUG
#define	DPRINTF(sc, _fmt, ...) do {					\
	if (sc->sc_debug & 0x10)					\
		printk(_fmt, __VA_ARGS__);				\
} while (0)
#else
#define	DPRINTF(sc, _fmt, ...)
#endif

static int ath_rateinterval = 1000;		/* rate ctl interval (ms)  */
static int ath_rate_max_success_threshold = 10;
static int ath_rate_min_success_threshold = 1;

static void ath_ratectl(unsigned long);
static void ath_rate_update(struct ath_softc *, struct ieee80211_node *, int);
static void ath_rate_ctl_start(struct ath_softc *, struct ieee80211_node *);
static void ath_rate_ctl(void *, struct ieee80211_node *);

static void
ath_rate_node_init(struct ath_softc *sc, struct ath_node *an)
{
	/* NB: assumed to be zero'd by caller */
	ath_rate_update(sc, &an->an_node, 0);
}

static void
ath_rate_node_cleanup(struct ath_softc *sc, struct ath_node *an)
{
}

static void
ath_rate_findrate(struct ath_softc *sc, struct ath_node *an,
	int shortPreamble, size_t frameLen,
	u_int8_t *rix, int *try0, u_int8_t *txrate)
{
	struct amrr_node *amn = ATH_NODE_AMRR(an);

	*rix = amn->amn_tx_rix0;
	*try0 = amn->amn_tx_try0;
	if (shortPreamble)
		*txrate = amn->amn_tx_rate0sp;
	else
		*txrate = amn->amn_tx_rate0;
}

static void
ath_rate_setupxtxdesc(struct ath_softc *sc, struct ath_node *an,
	struct ath_desc *ds, int shortPreamble, size_t frame_size, u_int8_t rix)
{
	struct amrr_node *amn = ATH_NODE_AMRR(an);

	ath_hal_setupxtxdesc(sc->sc_ah, ds
		, amn->amn_tx_rate1sp, amn->amn_tx_try1	/* series 1 */
		, amn->amn_tx_rate2sp, amn->amn_tx_try2	/* series 2 */
		, amn->amn_tx_rate3sp, amn->amn_tx_try3	/* series 3 */
	);
}

static void
ath_rate_tx_complete(struct ath_softc *sc,
	struct ath_node *an, const struct ath_desc *ds)
{
	struct amrr_node *amn = ATH_NODE_AMRR(an);
	int sr = ds->ds_txstat.ts_shortretry;
	int lr = ds->ds_txstat.ts_longretry;
	int retry_count = sr + lr;

	amn->amn_tx_try0_cnt++;
	if (retry_count == 1) {
		amn->amn_tx_try1_cnt++;
	} else if (retry_count == 2) {
		amn->amn_tx_try1_cnt++;
		amn->amn_tx_try2_cnt++;
	} else if (retry_count == 3) {
		amn->amn_tx_try1_cnt++;
		amn->amn_tx_try2_cnt++;
		amn->amn_tx_try3_cnt++;
	} else if (retry_count > 3) {
		amn->amn_tx_try1_cnt++;
		amn->amn_tx_try2_cnt++;
		amn->amn_tx_try3_cnt++;
		amn->amn_tx_failure_cnt++;
	}
}

static void
ath_rate_newassoc(struct ath_softc *sc, struct ath_node *an, int isnew)
{
	if (isnew)
		ath_rate_ctl_start(sc, &an->an_node);
}

static void 
node_reset (struct amrr_node *amn)
{
	amn->amn_tx_try0_cnt = 0;
	amn->amn_tx_try1_cnt = 0;
	amn->amn_tx_try2_cnt = 0;
	amn->amn_tx_try3_cnt = 0;
	amn->amn_tx_failure_cnt = 0;
  	amn->amn_success = 0;
  	amn->amn_recovery = 0;
  	amn->amn_success_threshold = ath_rate_min_success_threshold;
}


/**
 * The code below assumes that we are dealing with hardware multi rate retry
 * I have no idea what will happen if you try to use this module with another
 * type of hardware. Your machine might catch fire or it might work with
 * horrible performance...
 */
static void
ath_rate_update(struct ath_softc *sc, struct ieee80211_node *ni, int rate)
{
	struct ath_node *an = ATH_NODE(ni);
	struct amrr_node *amn = ATH_NODE_AMRR(an);
	const HAL_RATE_TABLE *rt = sc->sc_currates;
	u_int8_t rix;

	KASSERT(rt != NULL, ("no rate table, mode %u", sc->sc_curmode));

	DPRINTF(sc, "%s: set xmit rate for %s to %dM\n",
		__func__, ether_sprintf(ni->ni_macaddr),
		ni->ni_rates.rs_nrates > 0 ?
			(ni->ni_rates.rs_rates[rate] & IEEE80211_RATE_VAL) / 2 : 0);

	ni->ni_txrate = rate;
	/*
	 * Before associating a node has no rate set setup
	 * so we can't calculate any transmit codes to use.
	 * This is ok since we should never be sending anything
	 * but management frames and those always go at the
	 * lowest hardware rate.
	 */
	if (ni->ni_rates.rs_nrates > 0) {
		amn->amn_tx_rix0 =
			sc->sc_rixmap[ni->ni_rates.rs_rates[rate] & IEEE80211_RATE_VAL];
		amn->amn_tx_rate0 = rt->info[amn->amn_tx_rix0].rateCode;
		amn->amn_tx_rate0sp = amn->amn_tx_rate0 |
			rt->info[amn->amn_tx_rix0].shortPreamble;
		if (sc->sc_mrretry) {
			amn->amn_tx_try0 = 1;
			amn->amn_tx_try1 = 1;
			amn->amn_tx_try2 = 1;
			amn->amn_tx_try3 = 1;
			if (--rate >= 0) {
				rix = sc->sc_rixmap[ni->ni_rates.rs_rates[rate]&IEEE80211_RATE_VAL];
				amn->amn_tx_rate1 = rt->info[rix].rateCode;
				amn->amn_tx_rate1sp = amn->amn_tx_rate1 |
					rt->info[rix].shortPreamble;
			} else {
				amn->amn_tx_rate1 = amn->amn_tx_rate1sp = 0;
			}
			if (--rate >= 0) {
				rix = sc->sc_rixmap[ni->ni_rates.rs_rates[rate]&IEEE80211_RATE_VAL];
				amn->amn_tx_rate2 = rt->info[rix].rateCode;
				amn->amn_tx_rate2sp = amn->amn_tx_rate2 |
					rt->info[rix].shortPreamble;
			} else {
				amn->amn_tx_rate2 = amn->amn_tx_rate2sp = 0;
			}
			if (rate > 0) {
				/* NB: only do this if we didn't already do it above */
				amn->amn_tx_rate3 = rt->info[0].rateCode;
				amn->amn_tx_rate3sp = amn->amn_tx_rate3 |
					rt->info[0].shortPreamble;
			} else {
				amn->amn_tx_rate3 = amn->amn_tx_rate3sp = 0;
			}
		} else {
			amn->amn_tx_try0 = ATH_TXMAXTRY;
			/* theorically, these statements are useless because
			 *  the code which uses them tests for an_tx_try0 == ATH_TXMAXTRY
			 */
			amn->amn_tx_try1 = 0;
			amn->amn_tx_try2 = 0;
			amn->amn_tx_try3 = 0;
			amn->amn_tx_rate1 = amn->amn_tx_rate1sp = 0;
			amn->amn_tx_rate2 = amn->amn_tx_rate2sp = 0;
			amn->amn_tx_rate3 = amn->amn_tx_rate3sp = 0;
		}
	}
	node_reset(amn);
}

/*
 * Set the starting transmit rate for a node.
 */
static void
ath_rate_ctl_start(struct ath_softc *sc, struct ieee80211_node *ni)
{
#define	RATE(_ix)	(ni->ni_rates.rs_rates[(_ix)] & IEEE80211_RATE_VAL)
	struct ieee80211vap *vap = ni->ni_vap;
	int srate;

	KASSERT(ni->ni_rates.rs_nrates > 0, ("no rates"));
	if (vap->iv_fixed_rate == -1) {
		/*
		 * No fixed rate is requested. For 11b start with
		 * the highest negotiated rate; otherwise, for 11g
		 * and 11a, we start "in the middle" at 24Mb or 36Mb.
		 */
		srate = ni->ni_rates.rs_nrates - 1;
		if (sc->sc_curmode != IEEE80211_MODE_11B) {
			/*
			 * Scan the negotiated rate set to find the
			 * closest rate.
			 */
			/* NB: the rate set is assumed sorted */
			for (; srate >= 0 && RATE(srate) > 72; srate--);
			KASSERT(srate >= 0, ("bogus rate set"));
		}
	} else {
		/*
		 * A fixed rate is to be used; ic_fixed_rate is an
		 * index into the supported rate set.  Convert this
		 * to the index into the negotiated rate set for
		 * the node.  We know the rate is there because the
		 * rate set is checked when the station associates.
		 */
		srate = ni->ni_rates.rs_nrates - 1;
		for (; srate >= 0 && RATE(srate) != vap->iv_fixed_rate; srate--);
		KASSERT(srate >= 0,
			("fixed rate %d not in rate set", vap->iv_fixed_rate));
	}
	ath_rate_update(sc, ni, srate);
#undef RATE
}

static void
ath_rate_cb(void *arg, struct ieee80211_node *ni)
{
	ath_rate_update(ni->ni_ic->ic_dev->priv, ni, (long) arg);
}

/*
 * Reset the rate control state for each 802.11 state transition.
 */
static void
ath_rate_newstate(struct ieee80211vap *vap, enum ieee80211_state state)
{
	struct ieee80211com *ic = vap->iv_ic;
	struct ath_softc *sc = ic->ic_dev->priv;
	struct amrr_softc *asc = (struct amrr_softc *) sc->sc_rc;
	struct ieee80211_node *ni;

	if (state == IEEE80211_S_INIT) {
		del_timer(&asc->timer);
		return;
	}
	if (ic->ic_opmode == IEEE80211_M_STA) {
		/*
		 * Reset local xmit state; this is really only
		 * meaningful when operating in station mode.
		 */
		ni = vap->iv_bss;
		if (state == IEEE80211_S_RUN)
			ath_rate_ctl_start(sc, ni);
		else
			ath_rate_update(sc, ni, 0);
	} else {
		/*
		 * When operating as a station the node table holds
		 * the AP's that were discovered during scanning.
		 * For any other operating mode we want to reset the
		 * tx rate state of each node.
		 */
		ieee80211_iterate_nodes(&ic->ic_sta, ath_rate_cb, NULL);
		ath_rate_update(sc, vap->iv_bss, 0);
	}
	if (vap->iv_fixed_rate == -1 && state == IEEE80211_S_RUN) {
		int interval;
		/*
		 * Start the background rate control thread if we
		 * are not configured to use a fixed xmit rate.
		 */
		interval = ath_rateinterval;
		if (ic->ic_opmode == IEEE80211_M_STA)
			interval /= 2;
		mod_timer(&asc->timer, jiffies + ((HZ * interval) / 1000));
	}
}

/* 
 * Examine and potentially adjust the transmit rate.
 */
static void
ath_rate_ctl(void *arg, struct ieee80211_node *ni)
{
	struct ath_softc *sc = arg;
	struct amrr_node *amn = ATH_NODE_AMRR(ATH_NODE (ni));
	int old_rate;

#define is_success(amn) (amn->amn_tx_try1_cnt  < (amn->amn_tx_try0_cnt / 10))
#define is_enough(amn)  (amn->amn_tx_try0_cnt > 10)
#define is_failure(amn) (amn->amn_tx_try1_cnt > (amn->amn_tx_try0_cnt / 3))
#define is_max_rate(ni) ((ni->ni_txrate + 1) >= ni->ni_rates.rs_nrates)
#define is_min_rate(ni) (ni->ni_txrate == 0)

	old_rate = ni->ni_txrate;
  
  	DPRINTF (sc, "cnt0: %d cnt1: %d cnt2: %d cnt3: %d -- threshold: %d\n",
		 amn->amn_tx_try0_cnt,
		 amn->amn_tx_try1_cnt,
		 amn->amn_tx_try2_cnt,
		 amn->amn_tx_try3_cnt,
		 amn->amn_success_threshold);
  	if (is_success(amn) && is_enough(amn)) {
		amn->amn_success++;
		if (amn->amn_success == amn->amn_success_threshold &&
  		    !is_max_rate(ni)) {
  			amn->amn_recovery = 1;
  			amn->amn_success = 0;
  			ni->ni_txrate++;
			DPRINTF(sc, "increase rate to %d\n", ni->ni_txrate);
  		} else
			amn->amn_recovery = 0;
  	} else if (is_failure(amn)) {
  		amn->amn_success = 0;
  		if (!is_min_rate(ni)) {
  			if (amn->amn_recovery) {
  				/* recovery failure. */
  				amn->amn_success_threshold *= 2;
  				amn->amn_success_threshold = min(amn->amn_success_threshold,
								  (u_int)ath_rate_max_success_threshold);
 				DPRINTF(sc, "decrease rate recovery thr: %d\n",
					amn->amn_success_threshold);
  			} else {
  				/* simple failure. */
 				amn->amn_success_threshold = ath_rate_min_success_threshold;
 				DPRINTF(sc, "decrease rate normal thr: %d\n",
					amn->amn_success_threshold);
  			}
			amn->amn_recovery = 0;
  			ni->ni_txrate--;
   		} else
			amn->amn_recovery = 0;
   	}
	if (is_enough(amn) || old_rate != ni->ni_txrate) {
		/* reset counters. */
		amn->amn_tx_try0_cnt = 0;
		amn->amn_tx_try1_cnt = 0;
		amn->amn_tx_try2_cnt = 0;
		amn->amn_tx_try3_cnt = 0;
		amn->amn_tx_failure_cnt = 0;
	}
	if (old_rate != ni->ni_txrate)
		ath_rate_update(sc, ni, ni->ni_txrate);
}

static void
ath_ratectl(unsigned long data)
{
	struct net_device *dev = (struct net_device *)data;
	struct ath_softc *sc = dev->priv;
	struct amrr_softc *asc = (struct amrr_softc *)sc->sc_rc;
	struct ieee80211com *ic = &sc->sc_ic;
	int interval;

	if (dev->flags & IFF_RUNNING) {
		sc->sc_stats.ast_rate_calls++;

		if (ic->ic_opmode == IEEE80211_M_STA) {
			struct ieee80211vap *tmpvap;
			TAILQ_FOREACH(tmpvap, &ic->ic_vaps, iv_next) {
				ath_rate_ctl(sc, tmpvap->iv_bss);	/* NB: no reference */
			}
		} else
			ieee80211_iterate_nodes(&ic->ic_sta, ath_rate_ctl, sc);
	}
	interval = ath_rateinterval;
	if (ic->ic_opmode == IEEE80211_M_STA)
		interval /= 2;
	asc->timer.expires = jiffies + ((HZ * interval) / 1000);
	add_timer(&asc->timer);
}

static struct ath_ratectrl *
ath_rate_attach(struct ath_softc *sc)
{
	struct amrr_softc *asc;

	_MOD_INC_USE(THIS_MODULE, return NULL);
	asc = kmalloc(sizeof(struct amrr_softc), GFP_ATOMIC);
	if (asc == NULL) {
		_MOD_DEC_USE(THIS_MODULE);
		return NULL;
	}
	asc->arc.arc_space = sizeof(struct amrr_node);
	asc->arc.arc_vap_space = 0;
	init_timer(&asc->timer);
	asc->timer.data = (unsigned long) sc->sc_dev;
	asc->timer.function = ath_ratectl;

	return &asc->arc;
}

static void
ath_rate_detach(struct ath_ratectrl *arc)
{
	struct amrr_softc *asc = (struct amrr_softc *) arc;

	del_timer(&asc->timer);
	kfree(asc);
	_MOD_DEC_USE(THIS_MODULE);
}

static int minrateinterval = 500;	/* 500ms */
static int maxint = 0x7fffffff;		/* 32-bit big */
static int min_threshold = 1;

/*
 * Static (i.e. global) sysctls.
 */

static ctl_table ath_rate_static_sysctls[] = {
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "interval",
	  .mode		= 0644,
	  .data		= &ath_rateinterval,
	  .maxlen	= sizeof(ath_rateinterval),
	  .extra1	= &minrateinterval,
	  .extra2	= &maxint,
	  .proc_handler	= proc_dointvec_minmax
	},
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "max_success_threshold",
	  .mode		= 0644,
	  .data		= &ath_rate_max_success_threshold,
	  .maxlen	= sizeof(ath_rate_max_success_threshold),
	  .extra1	= &min_threshold,
	  .extra2	= &maxint,
	  .proc_handler	= proc_dointvec_minmax
	},
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "min_success_threshold",
	  .mode		= 0644,
	  .data		= &ath_rate_min_success_threshold,
	  .maxlen	= sizeof(ath_rate_min_success_threshold),
	  .extra1	= &min_threshold,
	  .extra2	= &maxint,
	  .proc_handler	= proc_dointvec_minmax
	},
	{ 0 }
};
static ctl_table ath_rate_table[] = {
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "rate",
	  .mode		= 0555,
	  .child	= ath_rate_static_sysctls
	}, { 0 }
};
static ctl_table ath_ath_table[] = {
	{ .ctl_name	= DEV_ATH,
	  .procname	= "ath",
	  .mode		= 0555,
	  .child	= ath_rate_table
	}, { 0 }
};
static ctl_table ath_root_table[] = {
	{ .ctl_name	= CTL_DEV,
	  .procname	= "dev",
	  .mode		= 0555,
	  .child	= ath_ath_table
	}, { 0 }
};
static struct ctl_table_header *ath_sysctl_header;

static struct ieee80211_rate_ops ath_rate_ops = {
	.ratectl_id = IEEE80211_RATE_AMRR,
	.node_init = ath_rate_node_init,
	.node_cleanup = ath_rate_node_cleanup,
	.findrate = ath_rate_findrate,
	.setupxtxdesc = ath_rate_setupxtxdesc,
	.tx_complete = ath_rate_tx_complete,
	.newassoc = ath_rate_newassoc,
	.newstate = ath_rate_newstate,
	.attach = ath_rate_attach,
	.detach = ath_rate_detach,
};

#include "release.h"
static char *version = "0.1 (" RELEASE_VERSION ")";
static char *dev_info = "ath_rate_amrr";

MODULE_AUTHOR("INRIA, Mathieu Lacage");
MODULE_DESCRIPTION("AMRR Rate control algorithm");
#ifdef MODULE_VERSION
MODULE_VERSION(RELEASE_VERSION);
#endif
#ifdef MODULE_LICENSE
MODULE_LICENSE("Dual BSD/GPL");
#endif

static int __init
init_ath_rate_amrr(void)
{
	int ret;
	printk(KERN_INFO "%s: %s\n", dev_info, version);

	ret = ieee80211_rate_register(&ath_rate_ops);
	if (ret)
		return ret;

	ath_sysctl_header = ATH_REGISTER_SYSCTL_TABLE(ath_root_table);
	return (0);
}
module_init(init_ath_rate_amrr);

static void __exit
exit_ath_rate_amrr(void)
{
	if (ath_sysctl_header != NULL)
		unregister_sysctl_table(ath_sysctl_header);
	ieee80211_rate_unregister(&ath_rate_ops);

	printk(KERN_INFO "%s: unloaded\n", dev_info);
}
module_exit(exit_ath_rate_amrr);
