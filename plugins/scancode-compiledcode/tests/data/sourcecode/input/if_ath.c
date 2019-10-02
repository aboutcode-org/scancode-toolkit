/*-
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
 * $Id: if_ath.c 3354 2008-02-13 05:13:10Z mrenzmann $
 */

/*
 * Driver for the Atheros Wireless LAN controller.
 *
 * This software is derived from work of Atsushi Onoe; his contribution
 * is greatly appreciated.
 */
#include "opt_ah.h"

#ifndef AUTOCONF_INCLUDED
#include <linux/config.h>
#endif
#include <linux/version.h>
#include <linux/module.h>
#include <linux/init.h>
#include <linux/skbuff.h>
#include <linux/netdevice.h>
#include <linux/etherdevice.h>
#include <linux/random.h>
#include <linux/delay.h>
#include <linux/cache.h>
#include <linux/sysctl.h>
#include <linux/proc_fs.h>
#include <linux/if_arp.h>
#include <linux/rtnetlink.h>
#include <asm/uaccess.h>

#include "if_ethersubr.h"		/* for ETHER_IS_MULTICAST */
#include "if_media.h"
#include "if_llc.h"

#include <net80211/ieee80211_radiotap.h>
#include <net80211/ieee80211_var.h>
#include <net80211/ieee80211_monitor.h>
#include <net80211/ieee80211_rate.h>

#ifdef USE_HEADERLEN_RESV
#include <net80211/if_llc.h>
#endif

#define	AR_DEBUG

#include "net80211/if_athproto.h"
#include "if_athvar.h"
#include "ah_desc.h"
#include "ah_devid.h"			/* XXX to identify chipset */

#ifdef ATH_PCI		/* PCI BUS */
#include "if_ath_pci.h"
#endif			/* PCI BUS */
#ifdef ATH_AHB		/* AHB BUS */
#include "if_ath_ahb.h"
#endif			/* AHB BUS */

#ifdef ATH_TX99_DIAG
#include "ath_tx99.h"
#endif

/* unaligned little endian access */
#define LE_READ_2(p)							\
	((u_int16_t)							\
	 ((((u_int8_t *)(p))[0]      ) | (((u_int8_t *)(p))[1] <<  8)))
#define LE_READ_4(p)							\
	((u_int32_t)							\
	 ((((u_int8_t *)(p))[0]      ) | (((u_int8_t *)(p))[1] <<  8) |	\
	  (((u_int8_t *)(p))[2] << 16) | (((u_int8_t *)(p))[3] << 24)))

/* Default rate control algorithm */
#ifdef CONFIG_ATHEROS_RATE_DEFAULT
#define DEF_RATE_CTL CONFIG_ATHEROS_RATE_DEFAULT
#else
#define DEF_RATE_CTL "sample"
#endif

enum {
	ATH_LED_TX,
	ATH_LED_RX,
	ATH_LED_POLL,
};

static struct ieee80211vap *ath_vap_create(struct ieee80211com *,
	const char *, int, int, int, struct net_device *);
static void ath_vap_delete(struct ieee80211vap *);
static int ath_init(struct net_device *);
static int ath_set_ack_bitrate(struct ath_softc *, int);
static int ath_reset(struct net_device *);
static void ath_fatal_tasklet(TQUEUE_ARG);
static void ath_rxorn_tasklet(TQUEUE_ARG);
static void ath_bmiss_tasklet(TQUEUE_ARG);
static void ath_bstuck_tasklet(TQUEUE_ARG);
static void ath_radar_task(struct work_struct *);
static void ath_dfs_test_return(unsigned long);

static int ath_stop_locked(struct net_device *);
static int ath_stop(struct net_device *);
#if 0
static void ath_initkeytable(struct ath_softc *);
#endif
static int ath_key_alloc(struct ieee80211vap *, const struct ieee80211_key *);
static int ath_key_delete(struct ieee80211vap *, const struct ieee80211_key *,
	struct ieee80211_node *);
static int ath_key_set(struct ieee80211vap *, const struct ieee80211_key *,
	const u_int8_t mac[IEEE80211_ADDR_LEN]);
static void ath_key_update_begin(struct ieee80211vap *);
static void ath_key_update_end(struct ieee80211vap *);
static void ath_mode_init(struct net_device *);
static void ath_setslottime(struct ath_softc *);
static void ath_updateslot(struct net_device *);
static int ath_beaconq_setup(struct ath_hal *);
static int ath_beacon_alloc(struct ath_softc *, struct ieee80211_node *);
#ifdef ATH_SUPERG_DYNTURBO
static void ath_beacon_dturbo_update(struct ieee80211vap *, int *, u_int8_t);
static void ath_beacon_dturbo_config(struct ieee80211vap *, u_int32_t);
static void ath_turbo_switch_mode(unsigned long);
static int ath_check_beacon_done(struct ath_softc *);
#endif
static void ath_beacon_send(struct ath_softc *, int *);
static void ath_beacon_start_adhoc(struct ath_softc *, struct ieee80211vap *);
static void ath_beacon_return(struct ath_softc *, struct ath_buf *);
static void ath_beacon_free(struct ath_softc *);
static void ath_beacon_config(struct ath_softc *, struct ieee80211vap *);
static int ath_desc_alloc(struct ath_softc *);
static void ath_desc_free(struct ath_softc *);
static void ath_desc_swap(struct ath_desc *);
static struct ieee80211_node *ath_node_alloc(struct ieee80211_node_table *,
	struct ieee80211vap *);
static void ath_node_cleanup(struct ieee80211_node *);
static void ath_node_free(struct ieee80211_node *);
static u_int8_t ath_node_getrssi(const struct ieee80211_node *);
static int ath_rxbuf_init(struct ath_softc *, struct ath_buf *);
static void ath_recv_mgmt(struct ieee80211_node *, struct sk_buff *, int,
	int, u_int32_t);
static void ath_setdefantenna(struct ath_softc *, u_int);
static struct ath_txq *ath_txq_setup(struct ath_softc *, int, int);
static void ath_rx_tasklet(TQUEUE_ARG);
static int ath_hardstart(struct sk_buff *, struct net_device *);
static int ath_mgtstart(struct ieee80211com *, struct sk_buff *);
#ifdef ATH_SUPERG_COMP
static u_int32_t ath_get_icvlen(struct ieee80211_key *);
static u_int32_t ath_get_ivlen(struct ieee80211_key *);
static void ath_setup_comp(struct ieee80211_node *, int);
static void ath_comp_set(struct ieee80211vap *, struct ieee80211_node *, int);	
#endif
static int ath_tx_setup(struct ath_softc *, int, int);
static int ath_wme_update(struct ieee80211com *);
static void ath_uapsd_flush(struct ieee80211_node *);
static void ath_tx_cleanupq(struct ath_softc *, struct ath_txq *);
static void ath_tx_cleanup(struct ath_softc *);
static void ath_tx_uapsdqueue(struct ath_softc *, struct ath_node *,
	struct ath_buf *);

static int ath_tx_start(struct net_device *, struct ieee80211_node *,
	struct ath_buf *, struct sk_buff *, int);
static void ath_tx_tasklet_q0(TQUEUE_ARG);
static void ath_tx_tasklet_q0123(TQUEUE_ARG);
static void ath_tx_tasklet(TQUEUE_ARG);
static void ath_tx_timeout(struct net_device *);
static void ath_tx_draintxq(struct ath_softc *, struct ath_txq *);
static int ath_chan_set(struct ath_softc *, struct ieee80211_channel *);
static void ath_draintxq(struct ath_softc *);
static __inline void ath_tx_txqaddbuf(struct ath_softc *, struct ieee80211_node *,
	struct ath_txq *, struct ath_buf *, struct ath_desc *, int);
static void ath_stoprecv(struct ath_softc *);
static int ath_startrecv(struct ath_softc *);
static void ath_flushrecv(struct ath_softc *);
static void ath_chan_change(struct ath_softc *, struct ieee80211_channel *);
static void ath_calibrate(unsigned long);
static int ath_newstate(struct ieee80211vap *, enum ieee80211_state, int);

static void ath_scan_start(struct ieee80211com *);
static void ath_scan_end(struct ieee80211com *);
static void ath_set_channel(struct ieee80211com *);
static void ath_set_coverageclass(struct ieee80211com *);
static u_int ath_mhz2ieee(struct ieee80211com *, u_int, u_int);
#ifdef ATH_SUPERG_FF
static int athff_can_aggregate(struct ath_softc *, struct ether_header *,
	struct ath_node *, struct sk_buff *, u_int16_t, int *);
#endif
static struct net_device_stats *ath_getstats(struct net_device *);
static void ath_setup_stationkey(struct ieee80211_node *);
static void ath_setup_stationwepkey(struct ieee80211_node *);
static void ath_setup_keycacheslot(struct ath_softc *, struct ieee80211_node *);
static void ath_newassoc(struct ieee80211_node *, int);
static int ath_getchannels(struct net_device *, u_int, HAL_BOOL, HAL_BOOL);
static void ath_led_event(struct ath_softc *, int);
static void ath_update_txpow(struct ath_softc *);

static int ath_set_mac_address(struct net_device *, void *);
static int ath_change_mtu(struct net_device *, int);
static int ath_ioctl(struct net_device *, struct ifreq *, int);

static int ath_rate_setup(struct net_device *, u_int);
static void ath_setup_subrates(struct net_device *);
#ifdef ATH_SUPERG_XR
static int ath_xr_rate_setup(struct net_device *);
static void ath_grppoll_txq_setup(struct ath_softc *, int, int);
static void ath_grppoll_start(struct ieee80211vap *, int);
static void ath_grppoll_stop(struct ieee80211vap *);
static u_int8_t ath_node_move_data(const struct ieee80211_node *);
static void ath_grppoll_txq_update(struct ath_softc *, int);
static void ath_grppoll_period_update(struct ath_softc *);
#endif
static void ath_setcurmode(struct ath_softc *, enum ieee80211_phymode);

static void ath_dynamic_sysctl_register(struct ath_softc *);
static void ath_dynamic_sysctl_unregister(struct ath_softc *);
static void ath_announce(struct net_device *);
static int ath_descdma_setup(struct ath_softc *, struct ath_descdma *,
	ath_bufhead *, const char *, int, int);
static void ath_descdma_cleanup(struct ath_softc *, struct ath_descdma *,
	ath_bufhead *, int);
static void ath_check_dfs_clear(unsigned long);
static const char *ath_get_hal_status_desc(HAL_STATUS status);
static int ath_rcv_dev_event(struct notifier_block *, unsigned long, void *);
	
static int ath_calinterval = ATH_SHORT_CALINTERVAL;		/*
								 * calibrate every 30 secs in steady state
								 * but check every second at first.
								 */
static int ath_countrycode = CTRY_DEFAULT;	/* country code */
static int ath_outdoor = AH_FALSE;		/* enable outdoor use */
static int ath_xchanmode = AH_TRUE;		/* enable extended channels */
static int ath_maxvaps = ATH_MAXVAPS_DEFAULT;	/* set default maximum vaps */
static char *autocreate = NULL;
static char *ratectl = DEF_RATE_CTL;
static int rfkill = -1;
static int countrycode = -1;
static int maxvaps = -1;
static int outdoor = -1;
static int xchanmode = -1;

static const char *hal_status_desc[] = {
	"No error",
	"No hardware present or device not yet supported",
	"Memory allocation failed",
	"Hardware didn't respond as expected",
	"EEPROM magic number invalid",
	"EEPROM version invalid",
	"EEPROM unreadable",
	"EEPROM checksum invalid",
	"EEPROM read problem",
	"EEPROM mac address invalid",
	"EEPROM size not supported",
	"Attempt to change write-locked EEPROM",
	"Invalid parameter to function",
	"Hardware revision not supported",
	"Hardware self-test failed",
	"Operation incomplete"
};

static struct notifier_block ath_event_block = {
        .notifier_call = ath_rcv_dev_event
};

#if (LINUX_VERSION_CODE < KERNEL_VERSION(2,5,52))
MODULE_PARM(countrycode, "i");
MODULE_PARM(maxvaps, "i");
MODULE_PARM(outdoor, "i");
MODULE_PARM(xchanmode, "i");
MODULE_PARM(rfkill, "i");
MODULE_PARM(autocreate, "s");
MODULE_PARM(ratectl, "s");
#else
#include <linux/moduleparam.h>
module_param(countrycode, int, 0600);
module_param(maxvaps, int, 0600);
module_param(outdoor, int, 0600);
module_param(xchanmode, int, 0600);
module_param(rfkill, int, 0600);
module_param(autocreate, charp, 0600);
module_param(ratectl, charp, 0600);
#endif
MODULE_PARM_DESC(countrycode, "Override default country code");
MODULE_PARM_DESC(maxvaps, "Maximum VAPs");
MODULE_PARM_DESC(outdoor, "Enable/disable outdoor use");
MODULE_PARM_DESC(xchanmode, "Enable/disable extended channel mode");
MODULE_PARM_DESC(rfkill, "Enable/disable RFKILL capability");
MODULE_PARM_DESC(autocreate, "Create ath device in [sta|ap|wds|adhoc|ahdemo|monitor] mode. defaults to sta, use 'none' to disable");
MODULE_PARM_DESC(ratectl, "Rate control algorithm [amrr|minstrel|onoe|sample], defaults to '" DEF_RATE_CTL "'");

static int	ath_debug = 0;
#ifdef AR_DEBUG
#if (LINUX_VERSION_CODE < KERNEL_VERSION(2,5,52))
MODULE_PARM(ath_debug, "i");
#else
module_param(ath_debug, int, 0600);
#endif
MODULE_PARM_DESC(ath_debug, "Load-time debug output enable");

#define	IFF_DUMPPKTS(sc, _m) \
	((sc->sc_debug & _m))
static void ath_printrxbuf(struct ath_buf *, int);
static void ath_printtxbuf(struct ath_buf *, int);
enum {
	ATH_DEBUG_XMIT		= 0x00000001,	/* basic xmit operation */
	ATH_DEBUG_XMIT_DESC	= 0x00000002,	/* xmit descriptors */
	ATH_DEBUG_RECV		= 0x00000004,	/* basic recv operation */
	ATH_DEBUG_RECV_DESC	= 0x00000008,	/* recv descriptors */
	ATH_DEBUG_RATE		= 0x00000010,	/* rate control */
	ATH_DEBUG_RESET		= 0x00000020,	/* reset processing */
	/* 0x00000040 was ATH_DEBUG_MODE */
	ATH_DEBUG_BEACON 	= 0x00000080,	/* beacon handling */
	ATH_DEBUG_WATCHDOG 	= 0x00000100,	/* watchdog timeout */
	ATH_DEBUG_INTR		= 0x00001000,	/* ISR */
	ATH_DEBUG_TX_PROC	= 0x00002000,	/* tx ISR proc */
	ATH_DEBUG_RX_PROC	= 0x00004000,	/* rx ISR proc */
	ATH_DEBUG_BEACON_PROC	= 0x00008000,	/* beacon ISR proc */
	ATH_DEBUG_CALIBRATE	= 0x00010000,	/* periodic calibration */
	ATH_DEBUG_KEYCACHE	= 0x00020000,	/* key cache management */
	ATH_DEBUG_STATE		= 0x00040000,	/* 802.11 state transitions */
	ATH_DEBUG_NODE		= 0x00080000,	/* node management */
	ATH_DEBUG_LED		= 0x00100000,	/* led management */
	ATH_DEBUG_FF		= 0x00200000,	/* fast frames */
	ATH_DEBUG_TURBO		= 0x00400000,	/* turbo/dynamic turbo */
	ATH_DEBUG_UAPSD		= 0x00800000,	/* uapsd */
	ATH_DEBUG_DOTH		= 0x01000000,	/* 11.h */
	ATH_DEBUG_FATAL		= 0x80000000,	/* fatal errors */
	ATH_DEBUG_ANY		= 0xffffffff
};
#define	DPRINTF(sc, _m, _fmt, ...) do {				\
	if (sc->sc_debug & (_m))				\
		printk(_fmt, __VA_ARGS__);			\
} while (0)
#define	KEYPRINTF(sc, ix, hk, mac) do {				\
	if (sc->sc_debug & ATH_DEBUG_KEYCACHE)			\
		ath_keyprint(sc, __func__, ix, hk, mac);	\
} while (0)
#else /* defined(AR_DEBUG) */
#define	IFF_DUMPPKTS(sc, _m)	netif_msg_dumppkts(&sc->sc_ic)
#define	DPRINTF(sc, _m, _fmt, ...)
#define	KEYPRINTF(sc, k, ix, mac)
#endif /* defined(AR_DEBUG) */

#define ATH_SETUP_XR_VAP(sc,vap,rfilt) \
	do { \
		if (sc->sc_curchan.privFlags & CHANNEL_4MS_LIMIT) \
			vap->iv_fragthreshold = XR_4MS_FRAG_THRESHOLD; \
		else \
			vap->iv_fragthreshold = vap->iv_xrvap->iv_fragthreshold; \
		if (!sc->sc_xrgrppoll) { \
			ath_grppoll_txq_setup(sc, HAL_TX_QUEUE_DATA, GRP_POLL_PERIOD_NO_XR_STA(sc)); \
			ath_grppoll_start(vap, sc->sc_xrpollcount); \
			ath_hal_setrxfilter(sc->sc_ah, rfilt|HAL_RX_FILTER_XRPOLL); \
		} \
   	} while(0)

/*
 * Define the scheme that we select MAC address for multiple BSS on the same radio.
 * The very first VAP will just use the MAC address from the EEPROM.
 * For the next 3 VAPs, we set the U/L bit (bit 1) in MAC address,
 * and use the next two bits as the index of the VAP.
 */
#define ATH_SET_VAP_BSSID_MASK(bssid_mask)				\
	((bssid_mask)[0] &= ~(((ath_maxvaps-1) << 2) | 0x02))
#define ATH_GET_VAP_ID(bssid)                   ((bssid)[0] >> 2)
#define ATH_SET_VAP_BSSID(bssid, id)            			\
    	do {                                    			\
		if (id)                            			\
            		(bssid)[0] |= (((id) << 2) | 0x02); 		\
	} while(0)

int
ath_attach(u_int16_t devid, struct net_device *dev, HAL_BUS_TAG tag)
{
	struct ath_softc *sc = dev->priv;
	struct ieee80211com *ic = &sc->sc_ic;
	struct ath_hal *ah;
	HAL_STATUS status;
	int error = 0, i;
	int autocreatemode = IEEE80211_M_STA;
	u_int8_t csz;

	sc->devid = devid;
	sc->sc_debug = ath_debug;
	DPRINTF(sc, ATH_DEBUG_ANY, "%s: devid 0x%x\n", __func__, devid);

	/* Allocate space for dynamically determined maximum VAP count */
	sc->sc_bslot = kmalloc(ath_maxvaps * sizeof(struct ieee80211vap), GFP_KERNEL);
	memset(sc->sc_bslot, 0, ath_maxvaps * sizeof(struct ieee80211vap));

	/*
	 * Cache line size is used to size and align various
	 * structures used to communicate with the hardware.
	 */
	bus_read_cachesize(sc, &csz);
	/* XXX assert csz is non-zero */
	sc->sc_cachelsz = csz << 2;		/* convert to bytes */

	ATH_LOCK_INIT(sc);
	ATH_TXBUF_LOCK_INIT(sc);
	ATH_RXBUF_LOCK_INIT(sc);

	ATH_INIT_TQUEUE(&sc->sc_rxtq,	 ath_rx_tasklet,	dev);
	ATH_INIT_TQUEUE(&sc->sc_txtq,	 ath_tx_tasklet,	dev);
	ATH_INIT_TQUEUE(&sc->sc_bmisstq, ath_bmiss_tasklet,	dev);
	ATH_INIT_TQUEUE(&sc->sc_bstucktq,ath_bstuck_tasklet,	dev);
	ATH_INIT_TQUEUE(&sc->sc_rxorntq, ath_rxorn_tasklet,	dev);
	ATH_INIT_TQUEUE(&sc->sc_fataltq, ath_fatal_tasklet,	dev);
	ATH_INIT_WORK(&sc->sc_radartask, ath_radar_task);

	/*
	 * Attach the HAL and verify ABI compatibility by checking
	 * the HAL's ABI signature against the one the driver was
	 * compiled with.  A mismatch indicates the driver was
	 * built with an ah.h that does not correspond to the HAL
	 * module loaded in the kernel.
	 */
	ah = _ath_hal_attach(devid, sc, tag, sc->sc_iobase, &status);
	if (ah == NULL) {
		printk(KERN_ERR "%s: unable to attach hardware: '%s' (HAL status %u)\n",
			dev->name, ath_get_hal_status_desc(status), status);
		error = ENXIO;
		goto bad;
	}
	if (ah->ah_abi != HAL_ABI_VERSION) {
		printk(KERN_ERR "%s: HAL ABI mismatch; "
			"driver expects 0x%x, HAL reports 0x%x\n",
			dev->name, HAL_ABI_VERSION, ah->ah_abi);
		error = ENXIO;		/* XXX */
		goto bad;
	}
	sc->sc_ah = ah;

	/*
	 * Check if the MAC has multi-rate retry support.
	 * We do this by trying to setup a fake extended
	 * descriptor.  MAC's that don't have support will
	 * return false w/o doing anything.  MAC's that do
	 * support it will return true w/o doing anything.
	 */
	sc->sc_mrretry = ath_hal_setupxtxdesc(ah, NULL, 0,0, 0,0, 0,0);

	/*
	 * Check if the device has hardware counters for PHY
	 * errors.  If so we need to enable the MIB interrupt
	 * so we can act on stat triggers.
	 */
	if (ath_hal_hwphycounters(ah))
		sc->sc_needmib = 1;

	/*
	 * Get the hardware key cache size.
	 */
	sc->sc_keymax = ath_hal_keycachesize(ah);
	if (sc->sc_keymax > ATH_KEYMAX) {
		printk("%s: Warning, using only %u entries in %u key cache\n",
			dev->name, ATH_KEYMAX, sc->sc_keymax);
		sc->sc_keymax = ATH_KEYMAX;
	}
	/*
	 * Reset the key cache since some parts do not
	 * reset the contents on initial power up.
	 */
	for (i = 0; i < sc->sc_keymax; i++)
		ath_hal_keyreset(ah, i);

	/*
	 * Collect the channel list using the default country
	 * code and including outdoor channels.  The 802.11 layer
	 * is responsible for filtering this list based on settings
	 * like the phy mode.
	 */
	if (countrycode != -1)
		ath_countrycode = countrycode;
	if (maxvaps != -1) {
		ath_maxvaps = maxvaps;
		if (ath_maxvaps < ATH_MAXVAPS_MIN)
			ath_maxvaps = ATH_MAXVAPS_MIN;
		if (ath_maxvaps > ATH_MAXVAPS_MAX)
			ath_maxvaps = ATH_MAXVAPS_MAX;
	}
	if (outdoor != -1)
		ath_outdoor = outdoor;
	if (xchanmode != -1)
		ath_xchanmode = xchanmode;
	error = ath_getchannels(dev, ath_countrycode,
			ath_outdoor, ath_xchanmode);
	if (error != 0)
		goto bad;

	ic->ic_country_code = ath_countrycode;
	ic->ic_country_outdoor = ath_outdoor;

	if (rfkill != -1) {
		printk(KERN_INFO "ath_pci: switching rfkill capability %s\n",
			rfkill ? "on" : "off");	
		ath_hal_setrfsilent(ah, rfkill);
	}

	/*
	 * Setup rate tables for all potential media types.
	 */
	ath_rate_setup(dev, IEEE80211_MODE_11A);
	ath_rate_setup(dev, IEEE80211_MODE_11B);
	ath_rate_setup(dev, IEEE80211_MODE_11G);
	ath_rate_setup(dev, IEEE80211_MODE_TURBO_A);
	ath_rate_setup(dev, IEEE80211_MODE_TURBO_G);

	/* Setup for half/quarter rates */
	ath_setup_subrates(dev);

	/* NB: setup here so ath_rate_update is happy */
	ath_setcurmode(sc, IEEE80211_MODE_11A);

	/*
	 * Allocate tx+rx descriptors and populate the lists.
	 */
	error = ath_desc_alloc(sc);
	if (error != 0) {
		printk(KERN_ERR "%s: failed to allocate descriptors: %d\n",
			dev->name, error);
		goto bad;
	}

	/*
	 * Init ic_caps prior to queue init, since WME cap setting
	 * depends on queue setup.
	 */
	ic->ic_caps = 0;

	/*
	 * Allocate hardware transmit queues: one queue for
	 * beacon frames and one data queue for each QoS
	 * priority.  Note that the HAL handles resetting
	 * these queues at the needed time.
	 *
	 * XXX PS-Poll
	 */
	sc->sc_bhalq = ath_beaconq_setup(ah);
	if (sc->sc_bhalq == (u_int) -1) {
		printk(KERN_ERR "%s: unable to setup a beacon xmit queue!\n",
			dev->name);
		error = EIO;
		goto bad2;
	}
	sc->sc_cabq = ath_txq_setup(sc, HAL_TX_QUEUE_CAB, 0);
	if (sc->sc_cabq == NULL) {
		printk(KERN_ERR "%s: unable to setup CAB xmit queue!\n",
			dev->name);
		error = EIO;
		goto bad2;
	}
	/* NB: ensure BK queue is the lowest priority h/w queue */
	if (!ath_tx_setup(sc, WME_AC_BK, HAL_WME_AC_BK)) {
		printk(KERN_ERR "%s: unable to setup xmit queue for %s traffic!\n",
			dev->name, ieee80211_wme_acnames[WME_AC_BK]);
		error = EIO;
		goto bad2;
	}
	if (!ath_tx_setup(sc, WME_AC_BE, HAL_WME_AC_BE) ||
	    !ath_tx_setup(sc, WME_AC_VI, HAL_WME_AC_VI) ||
	    !ath_tx_setup(sc, WME_AC_VO, HAL_WME_AC_VO)) {
		/*
		 * Not enough hardware tx queues to properly do WME;
		 * just punt and assign them all to the same h/w queue.
		 * We could do a better job of this if, for example,
		 * we allocate queues when we switch from station to
		 * AP mode.
		 */
		if (sc->sc_ac2q[WME_AC_VI] != NULL)
			ath_tx_cleanupq(sc, sc->sc_ac2q[WME_AC_VI]);
		if (sc->sc_ac2q[WME_AC_BE] != NULL)
			ath_tx_cleanupq(sc, sc->sc_ac2q[WME_AC_BE]);
		sc->sc_ac2q[WME_AC_BE] = sc->sc_ac2q[WME_AC_BK];
		sc->sc_ac2q[WME_AC_VI] = sc->sc_ac2q[WME_AC_BK];
		sc->sc_ac2q[WME_AC_VO] = sc->sc_ac2q[WME_AC_BK];
	} else {
		/*
		 * Mark WME capability since we have sufficient
		 * hardware queues to do proper priority scheduling.
		 */
		ic->ic_caps |= IEEE80211_C_WME;
		sc->sc_uapsdq = ath_txq_setup(sc, HAL_TX_QUEUE_UAPSD, 0);
		if (sc->sc_uapsdq == NULL)
			DPRINTF(sc, ATH_DEBUG_UAPSD, "%s: unable to setup UAPSD xmit queue!\n",
				__func__);
		else {
			ic->ic_caps |= IEEE80211_C_UAPSD;
			/*
			 * default UAPSD on if HW capable
			 */
			IEEE80211_COM_UAPSD_ENABLE(ic);
		}
	}
#ifdef ATH_SUPERG_XR
	ath_xr_rate_setup(dev);
	sc->sc_xrpollint = XR_DEFAULT_POLL_INTERVAL;
	sc->sc_xrpollcount = XR_DEFAULT_POLL_COUNT;
	strcpy(sc->sc_grppoll_str, XR_DEFAULT_GRPPOLL_RATE_STR);
	sc->sc_grpplq.axq_qnum = -1;
	sc->sc_xrtxq = ath_txq_setup(sc, HAL_TX_QUEUE_DATA, HAL_XR_DATA);
#endif

	/*
	 * Special case certain configurations.  Note the
	 * CAB queue is handled by these specially so don't
	 * include them when checking the txq setup mask.
	 */
	switch (sc->sc_txqsetup &~ ((1<<sc->sc_cabq->axq_qnum) |
				(sc->sc_uapsdq ? (1<<sc->sc_uapsdq->axq_qnum) : 0))) {
	case 0x01:
		ATH_INIT_TQUEUE(&sc->sc_txtq, ath_tx_tasklet_q0, dev);
		break;
	case 0x0f:
		ATH_INIT_TQUEUE(&sc->sc_txtq, ath_tx_tasklet_q0123, dev);
		break;
	}

	sc->sc_setdefantenna = ath_setdefantenna;
	sc->sc_rc = ieee80211_rate_attach(sc, ratectl);
	if (sc->sc_rc == NULL) {
		error = EIO;
		goto bad2;
	}

	init_timer(&sc->sc_cal_ch);
	sc->sc_cal_ch.function = ath_calibrate;
	sc->sc_cal_ch.data = (unsigned long) dev;

#ifdef ATH_SUPERG_DYNTURBO
	init_timer(&sc->sc_dturbo_switch_mode);
	sc->sc_dturbo_switch_mode.function = ath_turbo_switch_mode;
	sc->sc_dturbo_switch_mode.data = (unsigned long) dev;
#endif

	sc->sc_blinking = 0;
	sc->sc_ledstate = 1;
	sc->sc_ledon = 0;			/* low true */
	sc->sc_ledidle = msecs_to_jiffies(2700);	/* 2.7 sec */
	sc->sc_dfstesttime = ATH_DFS_TEST_RETURN_PERIOD;
	init_timer(&sc->sc_ledtimer);
	init_timer(&sc->sc_dfswaittimer);
	init_timer(&sc->sc_dfstesttimer);
	sc->sc_ledtimer.data = (unsigned long) sc;
	if (sc->sc_softled) {
		ath_hal_gpioCfgOutput(ah, sc->sc_ledpin);
		ath_hal_gpioset(ah, sc->sc_ledpin, !sc->sc_ledon);
	}

	/* NB: ether_setup is done by bus-specific code */
	dev->open = ath_init;
	dev->stop = ath_stop;
	dev->hard_start_xmit = ath_hardstart;
	dev->tx_timeout = ath_tx_timeout;
	dev->watchdog_timeo = 5 * HZ;			/* XXX */
	dev->set_multicast_list = ath_mode_init;
	dev->do_ioctl = ath_ioctl;
	dev->get_stats = ath_getstats;
	dev->set_mac_address = ath_set_mac_address;
 	dev->change_mtu = ath_change_mtu;
	dev->tx_queue_len = ATH_TXBUF - 1;		/* 1 for mgmt frame */
#ifdef USE_HEADERLEN_RESV
	dev->hard_header_len += sizeof(struct ieee80211_qosframe) +
				sizeof(struct llc) +
				IEEE80211_ADDR_LEN +
				IEEE80211_WEP_IVLEN +
				IEEE80211_WEP_KIDLEN;
#ifdef ATH_SUPERG_FF
	dev->hard_header_len += ATH_FF_MAX_HDR;
#endif
#endif
	ic->ic_dev = dev;
	ic->ic_mgtstart = ath_mgtstart;
	ic->ic_init = ath_init;
	ic->ic_reset = ath_reset;
	ic->ic_newassoc = ath_newassoc;
	ic->ic_updateslot = ath_updateslot;

	ic->ic_wme.wme_update = ath_wme_update;
	ic->ic_uapsd_flush = ath_uapsd_flush;

	/* XXX not right but it's not used anywhere important */
	ic->ic_phytype = IEEE80211_T_OFDM;
	ic->ic_opmode = IEEE80211_M_STA;
	sc->sc_opmode = HAL_M_STA;
	/* 
	 * Set the Atheros Advanced Capabilities from station config before 
	 * starting 802.11 state machine.  Currently, set only fast-frames 
	 * capability.
	 */
	ic->ic_ath_cap = 0;
	sc->sc_fftxqmin = ATH_FF_TXQMIN;
#ifdef ATH_SUPERG_FF
	ic->ic_ath_cap |= (ath_hal_fastframesupported(ah) ? IEEE80211_ATHC_FF : 0);
#endif
	ic->ic_ath_cap |= (ath_hal_burstsupported(ah) ? IEEE80211_ATHC_BURST : 0);

#ifdef ATH_SUPERG_COMP
	ic->ic_ath_cap |= (ath_hal_compressionsupported(ah) ? IEEE80211_ATHC_COMP : 0); 
#endif

#ifdef ATH_SUPERG_DYNTURBO
	ic->ic_ath_cap |= (ath_hal_turboagsupported(ah) ? (IEEE80211_ATHC_TURBOP |
							IEEE80211_ATHC_AR) : 0);
#endif
#ifdef ATH_SUPERG_XR
	ic->ic_ath_cap |= (ath_hal_xrsupported(ah) ? IEEE80211_ATHC_XR : 0);
#endif

	ic->ic_caps |=
		  IEEE80211_C_IBSS		/* ibss, nee adhoc, mode */
		| IEEE80211_C_HOSTAP		/* hostap mode */
		| IEEE80211_C_MONITOR		/* monitor mode */
		| IEEE80211_C_AHDEMO		/* adhoc demo mode */
		| IEEE80211_C_SHPREAMBLE	/* short preamble supported */
		| IEEE80211_C_SHSLOT		/* short slot time supported */
		| IEEE80211_C_WPA		/* capable of WPA1+WPA2 */
		| IEEE80211_C_BGSCAN		/* capable of bg scanning */
		;
	/*
	 * Query the HAL to figure out h/w crypto support.
	 */
	if (ath_hal_ciphersupported(ah, HAL_CIPHER_WEP))
		ic->ic_caps |= IEEE80211_C_WEP;
	if (ath_hal_ciphersupported(ah, HAL_CIPHER_AES_OCB))
		ic->ic_caps |= IEEE80211_C_AES;
	if (ath_hal_ciphersupported(ah, HAL_CIPHER_AES_CCM))
		ic->ic_caps |= IEEE80211_C_AES_CCM;
	if (ath_hal_ciphersupported(ah, HAL_CIPHER_CKIP))
		ic->ic_caps |= IEEE80211_C_CKIP;
	if (ath_hal_ciphersupported(ah, HAL_CIPHER_TKIP)) {
		ic->ic_caps |= IEEE80211_C_TKIP;
		/*
		 * Check if h/w does the MIC and/or whether the
		 * separate key cache entries are required to
		 * handle both tx+rx MIC keys.
		 */
		if (ath_hal_ciphersupported(ah, HAL_CIPHER_MIC)) {
			ic->ic_caps |= IEEE80211_C_TKIPMIC;
			/*
			 * Check if h/w does MIC correctly when
			 * WMM is turned on.
			 */
			if (ath_hal_wmetkipmic(ah))
				ic->ic_caps |= IEEE80211_C_WME_TKIPMIC;
		}

		/*
		 * If the h/w supports storing tx+rx MIC keys
		 * in one cache slot automatically enable use.
		 */
		if (ath_hal_hastkipsplit(ah) ||
		    !ath_hal_settkipsplit(ah, AH_FALSE))
			sc->sc_splitmic = 1;
	}
	sc->sc_hasclrkey = ath_hal_ciphersupported(ah, HAL_CIPHER_CLR);
#if 0
	sc->sc_mcastkey = ath_hal_getmcastkeysearch(ah);
#endif
	/*
	 * Mark key cache slots associated with global keys
	 * as in use.  If we knew TKIP was not to be used we
	 * could leave the +32, +64, and +32+64 slots free.
	 */
	for (i = 0; i < IEEE80211_WEP_NKID; i++) {
		setbit(sc->sc_keymap, i);
		setbit(sc->sc_keymap, i+64);
		if (sc->sc_splitmic) {
			setbit(sc->sc_keymap, i+32);
			setbit(sc->sc_keymap, i+32+64);
		}
	}
	/*
	 * TPC support can be done either with a global cap or
	 * per-packet support.  The latter is not available on
	 * all parts.  We're a bit pedantic here as all parts
	 * support a global cap.
	 */
	sc->sc_hastpc = ath_hal_hastpc(ah);
	if (sc->sc_hastpc || ath_hal_hastxpowlimit(ah))
		ic->ic_caps |= IEEE80211_C_TXPMGT;

	/*
	 * Default 11.h to start enabled.
	 */
	ic->ic_flags |= IEEE80211_F_DOTH;
	
	/*
	 * Check for misc other capabilities.
	 */
	if (ath_hal_hasbursting(ah))
		ic->ic_caps |= IEEE80211_C_BURST;
	sc->sc_hasbmask = ath_hal_hasbssidmask(ah);
	sc->sc_hastsfadd = ath_hal_hastsfadjust(ah);
	/*
	 * Indicate we need the 802.11 header padded to a
	 * 32-bit boundary for 4-address and QoS frames.
	 */
	ic->ic_flags |= IEEE80211_F_DATAPAD;

	/*
	 * Query the HAL about antenna support
	 * Enable rx fast diversity if HAL has support
	 */
	if (ath_hal_hasdiversity(ah)) {
		sc->sc_hasdiversity = 1;
		ath_hal_setdiversity(ah, AH_TRUE);
		sc->sc_diversity = 1;
	} else {
		sc->sc_hasdiversity = 0;
		sc->sc_diversity = 0;
		ath_hal_setdiversity(ah, AH_FALSE);
	}
	sc->sc_defant = ath_hal_getdefantenna(ah);

	/*
	 * Not all chips have the VEOL support we want to
	 * use with IBSS beacons; check here for it.
	 */
	sc->sc_hasveol = ath_hal_hasveol(ah);

       /* Interference Mitigation causes problems with recevive sensitivity
        * for OFDM rates when we are in non-STA modes. We will turn this
        * capability off in non-STA VAPs
        */
	sc->sc_hasintmit = ath_hal_hasintmit(ah);
	sc->sc_useintmit = 1;

	/* get mac address from hardware */
	ath_hal_getmac(ah, ic->ic_myaddr);
	if (sc->sc_hasbmask) {
		ath_hal_getbssidmask(ah, sc->sc_bssidmask);
		ATH_SET_VAP_BSSID_MASK(sc->sc_bssidmask);
		ath_hal_setbssidmask(ah, sc->sc_bssidmask);
	}
	IEEE80211_ADDR_COPY(dev->dev_addr, ic->ic_myaddr);

	/* call MI attach routine. */
	ieee80211_ifattach(ic);
	/* override default methods */
	ic->ic_node_alloc = ath_node_alloc;
	sc->sc_node_free = ic->ic_node_free;
	ic->ic_node_free = ath_node_free;
	ic->ic_node_getrssi = ath_node_getrssi;
#ifdef ATH_SUPERG_XR
	ic->ic_node_move_data = ath_node_move_data;
#endif
	sc->sc_node_cleanup = ic->ic_node_cleanup;
	ic->ic_node_cleanup = ath_node_cleanup;
	sc->sc_recv_mgmt = ic->ic_recv_mgmt;
	ic->ic_recv_mgmt = ath_recv_mgmt;

	ic->ic_vap_create = ath_vap_create;
	ic->ic_vap_delete = ath_vap_delete;

	ic->ic_scan_start = ath_scan_start;
	ic->ic_scan_end = ath_scan_end;
	ic->ic_set_channel = ath_set_channel;

	ic->ic_set_coverageclass = ath_set_coverageclass;
	ic->ic_mhz2ieee = ath_mhz2ieee;

	if (register_netdev(dev)) {
		printk(KERN_ERR "%s: unable to register device\n", dev->name);
		goto bad3;
	}
	/*
	 * Attach dynamic MIB vars and announce support
	 * now that we have a device name with unit number.
	 */
	ath_dynamic_sysctl_register(sc);
	ieee80211_announce(ic);
	ath_announce(dev);
#ifdef ATH_TX99_DIAG
	printk("%s: TX99 support enabled\n", dev->name);
#endif
	sc->sc_invalid = 0;

	if (autocreate) {
		if (!strcmp(autocreate, "none"))
			autocreatemode = -1;
		else if (!strcmp(autocreate, "sta"))
			autocreatemode = IEEE80211_M_STA;
		else if (!strcmp(autocreate, "ap"))
			autocreatemode = IEEE80211_M_HOSTAP;
		else if (!strcmp(autocreate, "adhoc"))
			autocreatemode = IEEE80211_M_IBSS;
		else if (!strcmp(autocreate, "ahdemo"))
			autocreatemode = IEEE80211_M_AHDEMO;
		else if (!strcmp(autocreate, "wds"))
			autocreatemode = IEEE80211_M_WDS;
		else if (!strcmp(autocreate, "monitor"))
			autocreatemode = IEEE80211_M_MONITOR;
		else {
			printk(KERN_INFO "Unknown autocreate mode: %s\n",
				autocreate);
			autocreatemode = -1;
		}
	}
	
	if (autocreatemode != -1) {
		rtnl_lock();
		error = ieee80211_create_vap(ic, "ath%d", dev,
				autocreatemode, IEEE80211_CLONE_BSSID);
		rtnl_unlock();
		if (error)
			printk(KERN_ERR "%s: autocreation of VAP failed: %d\n",
				dev->name, error);
	}

	return 0;
bad3:
	ieee80211_ifdetach(ic);
	ieee80211_rate_detach(sc->sc_rc);
bad2:
	ath_tx_cleanup(sc);
	ath_desc_free(sc);
bad:
	if (ah)
		ath_hal_detach(ah);
	ATH_TXBUF_LOCK_DESTROY(sc);
	ATH_LOCK_DESTROY(sc);
	sc->sc_invalid = 1;

	return error;
}

int
ath_detach(struct net_device *dev)
{
	struct ath_softc *sc = dev->priv;
	struct ath_hal *ah = sc->sc_ah;

	HAL_INT tmp;
	DPRINTF(sc, ATH_DEBUG_ANY, "%s: flags %x\n", __func__, dev->flags);
	ath_stop(dev);

	ath_hal_setpower(sc->sc_ah, HAL_PM_AWAKE);
	/* Flush the radar task if it's scheduled */
	if (sc->sc_rtasksched == 1)
		flush_scheduled_work();

	sc->sc_invalid = 1;

	/*
	 * NB: the order of these is important:
	 * o call the 802.11 layer before detaching the HAL to
	 *   ensure callbacks into the driver to delete global
	 *   key cache entries can be handled
	 * o reclaim the tx queue data structures after calling
	 *   the 802.11 layer as we'll get called back to reclaim
	 *   node state and potentially want to use them
	 * o to cleanup the tx queues the HAL is called, so detach
	 *   it last
	 * Other than that, it's straightforward...
	 */
	ieee80211_ifdetach(&sc->sc_ic);

	ath_hal_intrset(ah, 0);		/* disable further intr's */
	ath_hal_getisr(ah, &tmp);	/* clear ISR */
	if(dev->irq) {
		free_irq(dev->irq, dev);
		dev->irq = 0;
	}
#ifdef ATH_TX99_DIAG
	if (sc->sc_tx99 != NULL)
		sc->sc_tx99->detach(sc->sc_tx99);
#endif
	ieee80211_rate_detach(sc->sc_rc);
	ath_desc_free(sc);
	ath_tx_cleanup(sc);
	ath_hal_detach(ah);
	kfree(sc->sc_bslot);
	sc->sc_bslot = NULL;

	ath_dynamic_sysctl_unregister(sc);
	ATH_LOCK_DESTROY(sc);
	dev->stop = NULL; /* prevent calling ath_stop again */
	unregister_netdev(dev);
	return 0;
}

static struct ieee80211vap *
ath_vap_create(struct ieee80211com *ic, const char *name, int unit,
	int opmode, int flags, struct net_device *mdev)
{
	struct ath_softc *sc = ic->ic_dev->priv;
	struct ath_hal *ah = sc->sc_ah;
	struct net_device *dev;
	struct ath_vap *avp;
	struct ieee80211vap *vap;
	int ic_opmode;

	if (ic->ic_dev->flags & IFF_RUNNING) {
		/* needs to disable hardware too */
		ath_hal_intrset(ah, 0);		/* disable interrupts */
		ath_draintxq(sc);		/* stop xmit side */
		ath_stoprecv(sc);		/* stop recv side */
	}
	/* XXX ic unlocked and race against add */
	switch (opmode) {
	case IEEE80211_M_STA:	/* ap+sta for repeater application */
		if (sc->sc_nstavaps != 0)  /* only one sta regardless */
			return NULL;
		if ((sc->sc_nvaps != 0) && (!(flags & IEEE80211_NO_STABEACONS)))
			return NULL;   /* If using station beacons, must first up */
		if (flags & IEEE80211_NO_STABEACONS) {
			sc->sc_nostabeacons = 1;
			ic_opmode = IEEE80211_M_HOSTAP;	/* Run with chip in AP mode */
		} else 
			ic_opmode = opmode;
		break;
	case IEEE80211_M_IBSS:
		if (sc->sc_nvaps != 0)		/* only one */
			return NULL;
		ic_opmode = opmode;
		break;
	case IEEE80211_M_AHDEMO:
	case IEEE80211_M_MONITOR:
		if (sc->sc_nvaps != 0 && ic->ic_opmode != opmode) {
			/* preserve existing mode */
			ic_opmode = ic->ic_opmode;
		} else
			ic_opmode = opmode;
		break;
	case IEEE80211_M_HOSTAP:
	case IEEE80211_M_WDS:
		/* permit multiple ap's and/or wds links */
		/* XXX sta+ap for repeater/bridge application */
		if ((sc->sc_nvaps != 0) && (ic->ic_opmode == IEEE80211_M_STA))
			return NULL;
		/* XXX not right, beacon buffer is allocated on RUN trans */
		if (opmode == IEEE80211_M_HOSTAP && STAILQ_EMPTY(&sc->sc_bbuf))
			return NULL;
		/*
		 * XXX Not sure if this is correct when operating only
		 * with WDS links.
		 */
		ic_opmode = IEEE80211_M_HOSTAP;

		break;
	default:
		return NULL;
	}

	if (sc->sc_nvaps >= ath_maxvaps) {
		printk(KERN_WARNING "too many virtual ap's (already got %d)\n", sc->sc_nvaps);
		return NULL;
	}

	dev = alloc_etherdev(sizeof(struct ath_vap) + sc->sc_rc->arc_vap_space);
	if (dev == NULL) {
		/* XXX msg */
		return NULL;
	}
	
	avp = dev->priv;
	ieee80211_vap_setup(ic, dev, name, unit, opmode, flags);
	/* override with driver methods */
	vap = &avp->av_vap;
	avp->av_newstate = vap->iv_newstate;
	vap->iv_newstate = ath_newstate;
	vap->iv_key_alloc = ath_key_alloc;
	vap->iv_key_delete = ath_key_delete;
	vap->iv_key_set = ath_key_set;
	vap->iv_key_update_begin = ath_key_update_begin;
	vap->iv_key_update_end = ath_key_update_end;
#ifdef ATH_SUPERG_COMP
	vap->iv_comp_set = ath_comp_set;
#endif

	/* Let rate control register proc entries for the VAP */
	if (sc->sc_rc->ops->dynamic_proc_register)
		sc->sc_rc->ops->dynamic_proc_register(vap);

	/*
	 * Change the interface type for monitor mode.
	 */
	if (opmode == IEEE80211_M_MONITOR)
		dev->type = ARPHRD_IEEE80211_RADIOTAP;
	if ((flags & IEEE80211_CLONE_BSSID) &&
	    sc->sc_nvaps != 0 && opmode != IEEE80211_M_WDS && sc->sc_hasbmask) {
		struct ieee80211vap *v;
		uint64_t id_mask;
		unsigned int id;
		
		/*
		 * Hardware supports the bssid mask and a unique
		 * bssid was requested.  Assign a new mac address
		 * and expand our bssid mask to cover the active
		 * virtual ap's with distinct addresses.
		 */
		
		/* do a full search to mark all the allocated VAPs */
		id_mask = 0;
		TAILQ_FOREACH(v, &ic->ic_vaps, iv_next)
			id_mask |= (1 << ATH_GET_VAP_ID(v->iv_myaddr));
		
		for (id = 0; id < ath_maxvaps; id++) {
			/* get the first available slot */
			if ((id_mask & (1 << id)) == 0) {
				ATH_SET_VAP_BSSID(vap->iv_myaddr, id);
				break;
			}
		}
	}
	avp->av_bslot = -1;
	STAILQ_INIT(&avp->av_mcastq.axq_q);
	ATH_TXQ_LOCK_INIT(&avp->av_mcastq);
	if (opmode == IEEE80211_M_HOSTAP || opmode == IEEE80211_M_IBSS) {
		/*
		 * Allocate beacon state for hostap/ibss.  We know
		 * a buffer is available because of the check above.
		 */
		avp->av_bcbuf = STAILQ_FIRST(&sc->sc_bbuf);
		STAILQ_REMOVE_HEAD(&sc->sc_bbuf, bf_list);
		if (opmode == IEEE80211_M_HOSTAP || !sc->sc_hasveol) {
			int slot;
			/*
			 * Assign the VAP to a beacon xmit slot.  As
			 * above, this cannot fail to find one.
			 */
			avp->av_bslot = 0;
			for (slot = 0; slot < ath_maxvaps; slot++)
				if (sc->sc_bslot[slot] == NULL) {
					/*
					 * XXX hack, space out slots to better
					 * deal with misses
					 */
					if (slot + 1 < ath_maxvaps &&
					    sc->sc_bslot[slot+1] == NULL) {
						avp->av_bslot = slot + 1;
						break;
					}
					avp->av_bslot = slot;
					/* NB: keep looking for a double slot */
				}
			KASSERT(sc->sc_bslot[avp->av_bslot] == NULL,
				("beacon slot %u not empty?", avp->av_bslot));
			sc->sc_bslot[avp->av_bslot] = vap;
			sc->sc_nbcnvaps++;
		}
		if ((opmode == IEEE80211_M_HOSTAP) && (sc->sc_hastsfadd)) {
			/*
			 * Multiple VAPs are to transmit beacons and we
			 * have h/w support for TSF adjusting; enable use
			 * of staggered beacons.
			 */
			/* XXX check for beacon interval too small */
			if (ath_maxvaps > 4) {
				DPRINTF(sc, ATH_DEBUG_BEACON,
					"Staggered beacons are not possible "
					"with maxvaps set to %d.\n",
					ath_maxvaps);
				sc->sc_stagbeacons = 0;
			} else {
				sc->sc_stagbeacons = 1;
			}
		}
		DPRINTF(sc, ATH_DEBUG_BEACON, "sc->stagbeacons %sabled\n",
			(sc->sc_stagbeacons ? "en" : "dis"));
	}
	if (sc->sc_hastsfadd)
		ath_hal_settsfadjust(sc->sc_ah, sc->sc_stagbeacons);
	SET_NETDEV_DEV(dev, ATH_GET_NETDEV_DEV(mdev));
	/* complete setup */
	(void) ieee80211_vap_attach(vap,
		ieee80211_media_change, ieee80211_media_status);

	ic->ic_opmode = ic_opmode;
	
	if (opmode != IEEE80211_M_WDS)
		sc->sc_nvaps++;
		
	if (opmode == IEEE80211_M_STA)
		sc->sc_nstavaps++;
	else if (opmode == IEEE80211_M_MONITOR)
		sc->sc_nmonvaps++;
	/*
	 * Adhoc demo mode is a pseudo mode; to the HAL it's
	 * just ibss mode and the driver doesn't use management
	 * frames.  Other modes carry over directly to the HAL.
	 */
	if (ic->ic_opmode == IEEE80211_M_AHDEMO)
		sc->sc_opmode = HAL_M_IBSS;
	else
		sc->sc_opmode = (HAL_OPMODE) ic->ic_opmode;	/* NB: compatible */

#ifdef ATH_SUPERG_XR
	if ( vap->iv_flags & IEEE80211_F_XR ) {
		if (ath_descdma_setup(sc, &sc->sc_grppolldma, &sc->sc_grppollbuf,
			"grppoll", (sc->sc_xrpollcount+1) * HAL_ANTENNA_MAX_MODE, 1) != 0)
			printk("%s:grppoll Buf allocation failed \n",__func__);
		if (!sc->sc_xrtxq)
			sc->sc_xrtxq = ath_txq_setup(sc, HAL_TX_QUEUE_DATA, HAL_XR_DATA);
		if (sc->sc_hasdiversity) {
			/* Save current diversity state if user destroys XR VAP */
			sc->sc_olddiversity = sc->sc_diversity;
			ath_hal_setdiversity(sc->sc_ah, 0);
			sc->sc_diversity = 0;
		}
	}
#endif
	if (ic->ic_dev->flags & IFF_RUNNING) {
		/* restart hardware */
		if (ath_startrecv(sc) != 0)	/* restart recv */
			printk("%s: %s: unable to start recv logic\n",
				dev->name, __func__);
		if (sc->sc_beacons)
			ath_beacon_config(sc, NULL);	/* restart beacons */
		ath_hal_intrset(ah, sc->sc_imask);
	}

	return vap;
}

static void
ath_vap_delete(struct ieee80211vap *vap)
{
	struct net_device *dev = vap->iv_ic->ic_dev;
	struct ath_softc *sc = dev->priv;
	struct ath_hal *ah = sc->sc_ah;
	struct ath_vap *avp = ATH_VAP(vap);
	int decrease = 1;
	int i;
	KASSERT(vap->iv_state == IEEE80211_S_INIT, ("VAP not stopped"));

	if (dev->flags & IFF_RUNNING) {
		/*
		 * Quiesce the hardware while we remove the VAP.  In
		 * particular we need to reclaim all references to the
		 * VAP state by any frames pending on the tx queues.
		 *
		 * XXX can we do this w/o affecting other VAPs?
		 */
		ath_hal_intrset(ah, 0);		/* disable interrupts */
		ath_draintxq(sc);		/* stop xmit side */
		ath_stoprecv(sc);		/* stop recv side */
	}

	/*
	 * Reclaim any pending mcast bufs on the VAP.
	 */
	ath_tx_draintxq(sc, &avp->av_mcastq);
	ATH_TXQ_LOCK_DESTROY(&avp->av_mcastq);

	/*
	 * Reclaim beacon state.  Note this must be done before
	 * VAP instance is reclaimed as we may have a reference
	 * to it in the buffer for the beacon frame.
	 */
	if (avp->av_bcbuf != NULL) {
		if (avp->av_bslot != -1) {
			sc->sc_bslot[avp->av_bslot] = NULL;
			sc->sc_nbcnvaps--;
		}
		ath_beacon_return(sc, avp->av_bcbuf);
		avp->av_bcbuf = NULL;
		if (sc->sc_nbcnvaps == 0)
			sc->sc_stagbeacons = 0;
	}
	if (vap->iv_opmode == IEEE80211_M_STA) {
		sc->sc_nstavaps--;
		if (sc->sc_nostabeacons)
			sc->sc_nostabeacons = 0;
	} else if (vap->iv_opmode == IEEE80211_M_MONITOR) {
		sc->sc_nmonvaps--;
	} else if (vap->iv_opmode == IEEE80211_M_WDS) {
		decrease = 0;
	}
	ieee80211_vap_detach(vap);
	/* NB: memory is reclaimed through dev->destructor callback */
	if (decrease)
		sc->sc_nvaps--;

#ifdef ATH_SUPERG_XR 
	/*
	 * If it's an XR VAP, free the memory allocated explicitly.
	 * Since the XR VAP is not registered, OS cannot free the memory.
	 */
	if (vap->iv_flags & IEEE80211_F_XR) {
		ath_grppoll_stop(vap);
		ath_descdma_cleanup(sc, &sc->sc_grppolldma, &sc->sc_grppollbuf, BUS_DMA_FROMDEVICE);
		memset(&sc->sc_grppollbuf, 0, sizeof(sc->sc_grppollbuf));
		memset(&sc->sc_grppolldma, 0, sizeof(sc->sc_grppolldma));
		if (vap->iv_xrvap)
			vap->iv_xrvap->iv_xrvap = NULL;
		kfree(vap->iv_dev);
		ath_tx_cleanupq(sc,sc->sc_xrtxq);
		sc->sc_xrtxq = NULL;
		if (sc->sc_hasdiversity) {
			/* Restore diversity setting to old diversity setting */
			ath_hal_setdiversity(ah, sc->sc_olddiversity);
			sc->sc_diversity = sc->sc_olddiversity;
		}
	}
#endif

	for (i = 0; i < IEEE80211_APPIE_NUM_OF_FRAME; i++) {
		if (vap->app_ie[i].ie != NULL) {
			FREE(vap->app_ie[i].ie, M_DEVBUF);
			vap->app_ie[i].ie = NULL;
			vap->app_ie[i].length = 0;
		}
	}

	if (dev->flags & IFF_RUNNING) {
		/*
		 * Restart rx+tx machines if device is still running.
		 */
		if (ath_startrecv(sc) != 0)	/* restart recv */
			printk("%s: %s: unable to start recv logic\n",
				dev->name, __func__);
		if (sc->sc_beacons)
			ath_beacon_config(sc, NULL);	/* restart beacons */
		ath_hal_intrset(ah, sc->sc_imask);
	}
}

void
ath_suspend(struct net_device *dev)
{
	struct ath_softc *sc = dev->priv;

	DPRINTF(sc, ATH_DEBUG_ANY, "%s: flags %x\n", __func__, dev->flags);
	ath_stop(dev);
}

void
ath_resume(struct net_device *dev)
{
	struct ath_softc *sc = dev->priv;

	DPRINTF(sc, ATH_DEBUG_ANY, "%s: flags %x\n", __func__, dev->flags);
	ath_init(dev);
}

static void
ath_uapsd_processtriggers(struct ath_softc *sc)
{
	struct ath_hal *ah = sc->sc_ah;
	struct ath_buf *bf;
	struct ath_desc *ds;
	struct sk_buff *skb;
	struct ieee80211_node *ni;
	struct ath_node *an;
	struct ieee80211_qosframe *qwh;
	struct ath_txq *uapsd_xmit_q = sc->sc_uapsdq;
	struct ieee80211com *ic = &sc->sc_ic;
	int ac, retval;
	u_int8_t tid;
	u_int16_t frame_seq;
	u_int64_t tsf;
#define	PA2DESC(_sc, _pa) \
	((struct ath_desc *)((caddr_t)(_sc)->sc_rxdma.dd_desc + \
		((_pa) - (_sc)->sc_rxdma.dd_desc_paddr)))

	/* XXXAPSD: build in check against max triggers we could see
	 *          based on ic->ic_uapsdmaxtriggers.
	 */

	tsf = ath_hal_gettsf64(ah);
	ATH_RXBUF_LOCK(sc);
	if (sc->sc_rxbufcur == NULL)
		sc->sc_rxbufcur = STAILQ_FIRST(&sc->sc_rxbuf);
	for (bf = sc->sc_rxbufcur; bf; bf = STAILQ_NEXT(bf, bf_list)) {
		ds = bf->bf_desc;
		if (ds->ds_link == bf->bf_daddr) {
			/* NB: never process the self-linked entry at the end */
			break;
		}
		if (bf->bf_status & ATH_BUFSTATUS_DONE) {
			/* 
			 * already processed this buffer (shouldn't occur if
			 * we change code to always process descriptors in
			 * rx intr handler - as opposed to sometimes processing
			 * in the rx tasklet).
			 */
			continue;
		}
		skb = bf->bf_skb;
		if (skb == NULL) {		/* XXX ??? can this happen */
			printk("%s: no skbuff\n", __func__);
			continue;
		}

		/*
		 * XXXAPSD: consider new HAL call that does only the subset
		 *          of ath_hal_rxprocdesc we require for trigger search.
		 */

		/* 
		 * NB: descriptor memory doesn't need to be sync'd
		 *     due to the way it was allocated. 
		 */

		/*
		 * Must provide the virtual address of the current
		 * descriptor, the physical address, and the virtual
		 * address of the next descriptor in the h/w chain.
		 * This allows the HAL to look ahead to see if the
		 * hardware is done with a descriptor by checking the
		 * done bit in the following descriptor and the address
		 * of the current descriptor the DMA engine is working
		 * on.  All this is necessary because of our use of
		 * a self-linked list to avoid rx overruns.
		 */
		retval = ath_hal_rxprocdesc(ah, ds, bf->bf_daddr, PA2DESC(sc, ds->ds_link), tsf);
		if (HAL_EINPROGRESS == retval)
			break;

		/* XXX: we do not support frames spanning multiple descriptors */
		bf->bf_status |= ATH_BUFSTATUS_DONE;

		/* errors? */
		if (ds->ds_rxstat.rs_status)
			continue;

		/* prepare wireless header for examination */
		bus_dma_sync_single(sc->sc_bdev, bf->bf_skbaddr, 
							sizeof(struct ieee80211_qosframe), 
							BUS_DMA_FROMDEVICE);
		qwh = (struct ieee80211_qosframe *) skb->data;

		/* find the node. it MUST be in the keycache. */
		if (ds->ds_rxstat.rs_keyix == HAL_RXKEYIX_INVALID ||
		    (ni = sc->sc_keyixmap[ds->ds_rxstat.rs_keyix]) == NULL) {
			/* 
			 * XXX: this can occur if WEP mode is used for non-Atheros clients
			 *      (since we do not know which of the 4 WEP keys will be used
			 *      at association time, so cannot setup a key-cache entry.
			 *      The Atheros client can convey this in the Atheros IE.)
			 *
			 * TODO: The fix is to use the hash lookup on the node here.
			 */
#if 0
			/*
			 * This print is very chatty, so removing for now.
			 */
			DPRINTF(sc, ATH_DEBUG_UAPSD, "%s: U-APSD node (%s) has invalid keycache entry\n",
				__func__, ether_sprintf(qwh->i_addr2));
#endif
			continue;
		}
		
		if (!(ni->ni_flags & IEEE80211_NODE_UAPSD))
			continue;
		
		/*
		 * Must deal with change of state here, since otherwise there would
		 * be a race (on two quick frames from STA) between this code and the
		 * tasklet where we would:
		 *   - miss a trigger on entry to PS if we're already trigger hunting
		 *   - generate spurious SP on exit (due to frame following exit frame)
		 */
		if (((qwh->i_fc[1] & IEEE80211_FC1_PWR_MGT) ^
		     (ni->ni_flags & IEEE80211_NODE_PWR_MGT))) {
			/*
			 * NB: do not require lock here since this runs at intr
			 * "proper" time and cannot be interrupted by rx tasklet
			 * (code there has lock). May want to place a macro here
			 * (that does nothing) to make this more clear.
			 */
			ni->ni_flags |= IEEE80211_NODE_PS_CHANGED;
			ni->ni_pschangeseq = *(__le16 *)(&qwh->i_seq[0]);
			ni->ni_flags &= ~IEEE80211_NODE_UAPSD_SP;
			ni->ni_flags ^= IEEE80211_NODE_PWR_MGT;
			if (qwh->i_fc[1] & IEEE80211_FC1_PWR_MGT) {
				ni->ni_flags |= IEEE80211_NODE_UAPSD_TRIG;
				ic->ic_uapsdmaxtriggers++;
				WME_UAPSD_NODE_TRIGSEQINIT(ni);
				DPRINTF(sc, ATH_DEBUG_UAPSD,
					"%s: Node (%s) became U-APSD triggerable (%d)\n", 
					__func__, ether_sprintf(qwh->i_addr2),
					ic->ic_uapsdmaxtriggers);
			} else {
				ni->ni_flags &= ~IEEE80211_NODE_UAPSD_TRIG;
				ic->ic_uapsdmaxtriggers--;
				DPRINTF(sc, ATH_DEBUG_UAPSD,
					"%s: Node (%s) no longer U-APSD triggerable (%d)\n", 
					__func__, ether_sprintf(qwh->i_addr2),
					ic->ic_uapsdmaxtriggers);
				/* 
				 * XXX: rapidly thrashing sta could get 
				 * out-of-order frames due this flush placing
				 * frames on backlogged regular AC queue and
				 * re-entry to PS having fresh arrivals onto
				 * faster UPSD delivery queue. if this is a
				 * big problem we may need to drop these.
				 */
				ath_uapsd_flush(ni);
			}
			
			continue;
		}

		if (ic->ic_uapsdmaxtriggers == 0)
			continue;
		
		/* make sure the frame is QoS data/null */
		/* NB: with current sub-type definitions, the 
		 * IEEE80211_FC0_SUBTYPE_QOS check, below, covers the 
		 * QoS null case too.
		 */
		if (((qwh->i_fc[0] & IEEE80211_FC0_TYPE_MASK) != IEEE80211_FC0_TYPE_DATA) ||
		     !(qwh->i_fc[0] & IEEE80211_FC0_SUBTYPE_QOS))
			continue;
		
		/*
		 * To be a trigger:
		 *   - node is in triggerable state
		 *   - QoS data/null frame with triggerable AC
		 */
		tid = qwh->i_qos[0] & IEEE80211_QOS_TID;
		ac = TID_TO_WME_AC(tid);
		if (!WME_UAPSD_AC_CAN_TRIGGER(ac, ni))
			continue;
		
		DPRINTF(sc, ATH_DEBUG_UAPSD, 
			"%s: U-APSD trigger detected for node (%s) on AC %d\n",
			__func__, ether_sprintf(ni->ni_macaddr), ac);
		if (ni->ni_flags & IEEE80211_NODE_UAPSD_SP) {
			/* have trigger, but SP in progress, so ignore */
			DPRINTF(sc, ATH_DEBUG_UAPSD,
				"%s:   SP already in progress - ignoring\n",
				__func__);
			continue;
		}

		/*
		 * Detect duplicate triggers and drop if so.
		 */
		frame_seq = le16toh(*(__le16 *)qwh->i_seq);
		if ((qwh->i_fc[1] & IEEE80211_FC1_RETRY) &&
		    frame_seq == ni->ni_uapsd_trigseq[ac]) {
			DPRINTF(sc, ATH_DEBUG_UAPSD, "%s: dropped dup trigger, ac %d, seq %d\n",
				__func__, ac, frame_seq);
			continue;
		}

		an = ATH_NODE(ni);

		/* start the SP */
		ATH_NODE_UAPSD_LOCK(an);
		ni->ni_stats.ns_uapsd_triggers++;
		ni->ni_flags |= IEEE80211_NODE_UAPSD_SP;
		ni->ni_uapsd_trigseq[ac] = frame_seq;
		ATH_NODE_UAPSD_UNLOCK(an);

		ATH_TXQ_LOCK(uapsd_xmit_q);
		if (STAILQ_EMPTY(&an->an_uapsd_q)) {
			DPRINTF(sc, ATH_DEBUG_UAPSD,
				"%s: Queue empty, generating QoS NULL to send\n",
				__func__);
			/* 
			 * Empty queue, so need to send QoS null on this ac. Make a
			 * call that will dump a QoS null onto the node's queue, then
			 * we can proceed as normal.
			 */
			ieee80211_send_qosnulldata(ni, ac);
		}

		if (STAILQ_FIRST(&an->an_uapsd_q)) {
			struct ath_buf *last_buf = STAILQ_LAST(&an->an_uapsd_q, ath_buf, bf_list);
			struct ath_desc *last_desc = last_buf->bf_desc;
			struct ieee80211_qosframe *qwhl = (struct ieee80211_qosframe *)last_buf->bf_skb->data;
			/* 
			 * NB: flip the bit to cause intr on the EOSP desc,
			 * which is the last one
			 */
			ath_hal_txreqintrdesc(sc->sc_ah, last_desc);
			qwhl->i_qos[0] |= IEEE80211_QOS_EOSP;

			if (IEEE80211_VAP_EOSPDROP_ENABLED(ni->ni_vap)) {
				/* simulate lost EOSP */
				qwhl->i_addr1[0] |= 0x40;
			}
			
			/* more data bit only for EOSP frame */
			if (an->an_uapsd_overflowqdepth)
				qwhl->i_fc[1] |= IEEE80211_FC1_MORE_DATA;
			else if (IEEE80211_NODE_UAPSD_USETIM(ni))
				ni->ni_vap->iv_set_tim(ni, 0);

			ni->ni_stats.ns_tx_uapsd += an->an_uapsd_qdepth;

			bus_dma_sync_single(sc->sc_bdev, last_buf->bf_skbaddr,
				sizeof(*qwhl), BUS_DMA_TODEVICE);
			
			if (uapsd_xmit_q->axq_link) {
#ifdef AH_NEED_DESC_SWAP
				*uapsd_xmit_q->axq_link = cpu_to_le32(STAILQ_FIRST(&an->an_uapsd_q)->bf_daddr);
#else
				*uapsd_xmit_q->axq_link = STAILQ_FIRST(&an->an_uapsd_q)->bf_daddr;
#endif
			}
			/* below leaves an_uapsd_q NULL */
			STAILQ_CONCAT(&uapsd_xmit_q->axq_q, &an->an_uapsd_q);
			uapsd_xmit_q->axq_link = &last_desc->ds_link;
			ath_hal_puttxbuf(sc->sc_ah, 
				uapsd_xmit_q->axq_qnum, 
				(STAILQ_FIRST(&uapsd_xmit_q->axq_q))->bf_daddr);
			ath_hal_txstart(sc->sc_ah, uapsd_xmit_q->axq_qnum);
		}
		an->an_uapsd_qdepth = 0;

		ATH_TXQ_UNLOCK(uapsd_xmit_q);
	}
	sc->sc_rxbufcur = bf;
	ATH_RXBUF_UNLOCK(sc);
#undef PA2DESC
}

/*
 * Interrupt handler.  Most of the actual processing is deferred.
 */
irqreturn_t
#if LINUX_VERSION_CODE >= KERNEL_VERSION(2,6,19)
ath_intr(int irq, void *dev_id)
#else
ath_intr(int irq, void *dev_id, struct pt_regs *regs)
#endif
{
	struct net_device *dev = dev_id;
	struct ath_softc *sc = dev->priv;
	struct ath_hal *ah = sc->sc_ah;
	HAL_INT status;
	int needmark;

	if (sc->sc_invalid) {
		/*
		 * The hardware is not ready/present, don't touch anything.
		 * Note this can happen early on if the IRQ is shared.
		 */
		return IRQ_NONE;
	}
	if (!ath_hal_intrpend(ah))		/* shared irq, not for us */
		return IRQ_NONE;
	if ((dev->flags & (IFF_RUNNING | IFF_UP)) != (IFF_RUNNING | IFF_UP)) {
		DPRINTF(sc, ATH_DEBUG_INTR, "%s: flags 0x%x\n",
			__func__, dev->flags);
		ath_hal_getisr(ah, &status);	/* clear ISR */
		ath_hal_intrset(ah, 0);		/* disable further intr's */
		return IRQ_HANDLED;
	}
	needmark = 0;
	/*
	 * Figure out the reason(s) for the interrupt.  Note
	 * that the HAL returns a pseudo-ISR that may include
	 * bits we haven't explicitly enabled so we mask the
	 * value to ensure we only process bits we requested.
	 */
	ath_hal_getisr(ah, &status);		/* NB: clears ISR too */
	DPRINTF(sc, ATH_DEBUG_INTR, "%s: status 0x%x\n", __func__, status);
	status &= sc->sc_imask;			/* discard unasked for bits */
	if (status & HAL_INT_FATAL) {
		sc->sc_stats.ast_hardware++;
		ath_hal_intrset(ah, 0);		/* disable intr's until reset */
		ATH_SCHEDULE_TQUEUE(&sc->sc_fataltq, &needmark);
	} else if (status & HAL_INT_RXORN) {
		sc->sc_stats.ast_rxorn++;
		ath_hal_intrset(ah, 0);		/* disable intr's until reset */
		ATH_SCHEDULE_TQUEUE(&sc->sc_rxorntq, &needmark);
	} else {
		if (status & HAL_INT_SWBA) {
			/*
			 * Software beacon alert--time to send a beacon.
			 * Handle beacon transmission directly; deferring
			 * this is too slow to meet timing constraints
			 * under load.
			 */
			ath_beacon_send(sc, &needmark);
		}
		if (status & HAL_INT_RXEOL) {
			/*
			 * NB: the hardware should re-read the link when
			 *     RXE bit is written, but it doesn't work at
			 *     least on older hardware revs.
			 */
			sc->sc_stats.ast_rxeol++;
		}
		if (status & HAL_INT_TXURN) {
			sc->sc_stats.ast_txurn++;
			/* bump tx trigger level */
			ath_hal_updatetxtriglevel(ah, AH_TRUE);
		}
		if (status & HAL_INT_RX) {
			ath_uapsd_processtriggers(sc);
			/* Get the noise floor data in interrupt context as we can't get it
			 * per frame, so we need to get it as soon as possible (i.e. the tasklet
			 * might take too long to fire */
			ath_hal_process_noisefloor(ah);
			sc->sc_channoise = ath_hal_get_channel_noise(ah, &(sc->sc_curchan));
			ATH_SCHEDULE_TQUEUE(&sc->sc_rxtq, &needmark);
		}
		if (status & HAL_INT_TX) {
#ifdef ATH_SUPERG_DYNTURBO
			/*
			 * Check if the beacon queue caused the interrupt 
			 * when a dynamic turbo switch
			 * is pending so we can initiate the change. 
			 * XXX must wait for all VAPs' beacons
			 */

			if (sc->sc_dturbo_switch) {
				u_int32_t txqs = (1 << sc->sc_bhalq);
				ath_hal_gettxintrtxqs(ah, &txqs);
				if(txqs & (1 << sc->sc_bhalq)) {
					sc->sc_dturbo_switch = 0;
					/*
					 * Hack: defer switch for 10ms to permit slow
					 * clients time to track us.  This especially
					 * noticeable with Windows clients.
					 */
					mod_timer(&sc->sc_dturbo_switch_mode,
							  jiffies + msecs_to_jiffies(10));
				}
			} 
#endif
			ATH_SCHEDULE_TQUEUE(&sc->sc_txtq, &needmark);
		}
		if (status & HAL_INT_BMISS) {
			sc->sc_stats.ast_bmiss++;
			ATH_SCHEDULE_TQUEUE(&sc->sc_bmisstq, &needmark);
		}
		if (status & HAL_INT_MIB) {
			sc->sc_stats.ast_mib++;
			/*
			 * Disable interrupts until we service the MIB
			 * interrupt; otherwise it will continue to fire.
			 */
			ath_hal_intrset(ah, 0);
			/*
			 * Let the HAL handle the event.  We assume it will
			 * clear whatever condition caused the interrupt.
			 */
			ath_hal_mibevent(ah, &sc->sc_halstats);
			ath_hal_intrset(ah, sc->sc_imask);
		}
	}
	if (needmark)
		mark_bh(IMMEDIATE_BH);
	return IRQ_HANDLED;
}

static void
ath_radar_task(struct work_struct *thr)
{
	struct ath_softc *sc = container_of(thr, struct ath_softc, sc_radartask);
	struct ath_hal *ah = sc->sc_ah;
	struct ieee80211com *ic = &sc->sc_ic;
	struct ieee80211_channel ichan;
	HAL_CHANNEL hchan;

	sc->sc_rtasksched = 0;
	if (ath_hal_procdfs(ah, &hchan)) {
		/*
		 * DFS was found, initiate channel change
		 */
		ichan.ic_ieee = ath_hal_mhz2ieee(ah, hchan.channel, hchan.channelFlags);
		ichan.ic_freq = hchan.channel;
		ichan.ic_flags = hchan.channelFlags;

		if ((sc->sc_curchan.channel == hchan.channel) &&
		    (sc->sc_curchan.channelFlags == hchan.channel)) {
			if (hchan.privFlags & CHANNEL_INTERFERENCE)
				sc->sc_curchan.privFlags |= CHANNEL_INTERFERENCE;
		}
		ieee80211_mark_dfs(ic, &ichan);
		if (((ic->ic_flags_ext & IEEE80211_FEXT_MARKDFS) == 0) &&
		    (ic->ic_opmode == IEEE80211_M_HOSTAP)) {
			sc->sc_dfstest_ieeechan = ic->ic_curchan->ic_ieee;
			sc->sc_dfstesttimer.function = ath_dfs_test_return;
			sc->sc_dfstesttimer.expires = jiffies + (sc->sc_dfstesttime * HZ);
			sc->sc_dfstesttimer.data = (unsigned long)sc;
			if (sc->sc_dfstest == 0) {
				sc->sc_dfstest = 1;
				add_timer(&sc->sc_dfstesttimer);
			}
		}
	}
}

static void
ath_dfs_test_return(unsigned long data)
{
	struct ath_softc *sc = (struct ath_softc *)data; 
	struct ieee80211com *ic = &sc->sc_ic;

	sc->sc_dfstest = 0;
	ieee80211_dfs_test_return(ic, sc->sc_dfstest_ieeechan);
}

static void
ath_fatal_tasklet(TQUEUE_ARG data)
{
	struct net_device *dev = (struct net_device *)data;

	printk("%s: hardware error; resetting\n", dev->name);
	ath_reset(dev);
}

static void
ath_rxorn_tasklet(TQUEUE_ARG data)
{
	struct net_device *dev = (struct net_device *)data;

	printk("%s: rx FIFO overrun; resetting\n", dev->name);
	ath_reset(dev);
}

static void
ath_bmiss_tasklet(TQUEUE_ARG data)
{
	struct net_device *dev = (struct net_device *)data;
	struct ath_softc *sc = dev->priv;

	if (time_before(jiffies, sc->sc_ic.ic_bmiss_guard)) {
		/* Beacon miss interrupt occured too short after last beacon
		 * timer configuration. Ignore it as it could be spurious. */
		DPRINTF(sc, ATH_DEBUG_ANY, "%s: ignored\n", __func__);
	} else {
		DPRINTF(sc, ATH_DEBUG_ANY, "%s\n", __func__);
		ieee80211_beacon_miss(&sc->sc_ic);
	}
}

static u_int
ath_chan2flags(struct ieee80211_channel *chan)
{
	u_int flags;
	static const u_int modeflags[] = {
		0,		/* IEEE80211_MODE_AUTO    */
		CHANNEL_A,	/* IEEE80211_MODE_11A     */
		CHANNEL_B,	/* IEEE80211_MODE_11B     */
		CHANNEL_PUREG,	/* IEEE80211_MODE_11G     */
		0,		/* IEEE80211_MODE_FH      */
		CHANNEL_108A,	/* IEEE80211_MODE_TURBO_A */
		CHANNEL_108G,	/* IEEE80211_MODE_TURBO_G */
	};

	flags = modeflags[ieee80211_chan2mode(chan)];

	if (IEEE80211_IS_CHAN_HALF(chan))
		flags |= CHANNEL_HALF;
	else if (IEEE80211_IS_CHAN_QUARTER(chan))
		flags |= CHANNEL_QUARTER;

	return flags;
}

/*
 * Context: process context
 */

static int
ath_init(struct net_device *dev)
{
	struct ath_softc *sc = dev->priv;
	struct ieee80211com *ic = &sc->sc_ic;
	struct ath_hal *ah = sc->sc_ah;
	HAL_STATUS status;
	int error = 0;

	ATH_LOCK(sc);

	DPRINTF(sc, ATH_DEBUG_RESET, "%s: mode %d\n", __func__, ic->ic_opmode);

	/*
	 * Stop anything previously setup.  This is safe
	 * whether this is the first time through or not.
	 */
	ath_stop_locked(dev);

#ifdef ATH_CAP_TPC
	ath_hal_setcapability(sc->sc_ah, HAL_CAP_TPC, 0, 1, NULL);
#endif

	/* Whether we should enable h/w TKIP MIC */
	if ((ic->ic_caps & IEEE80211_C_WME) == 0)
		ath_hal_setcapability(sc->sc_ah, HAL_CAP_TKIP_MIC, 0, 0, NULL);
	else {
		if (((ic->ic_caps & IEEE80211_C_WME_TKIPMIC) == 0) &&
		    (ic->ic_flags & IEEE80211_F_WME))
			ath_hal_setcapability(sc->sc_ah, HAL_CAP_TKIP_MIC, 0, 0, NULL);
		else
			ath_hal_setcapability(sc->sc_ah, HAL_CAP_TKIP_MIC, 0, 1, NULL);
	}
		
	/*
	 * Flush the skb's allocated for receive in case the rx
	 * buffer size changes.  This could be optimized but for
	 * now we do it each time under the assumption it does
	 * not happen often.
	 */
	ath_flushrecv(sc);

	/*
	 * The basic interface to setting the hardware in a good
	 * state is ``reset''.  On return the hardware is known to
	 * be powered up and with interrupts disabled.  This must
	 * be followed by initialization of the appropriate bits
	 * and then setup of the interrupt mask.
	 */
	sc->sc_curchan.channel = ic->ic_curchan->ic_freq;
	sc->sc_curchan.channelFlags = ath_chan2flags(ic->ic_curchan);
	if (!ath_hal_reset(ah, sc->sc_opmode, &sc->sc_curchan, AH_FALSE, &status)) {
		printk("%s: unable to reset hardware: '%s' (HAL status %u) "
			"(freq %u flags 0x%x)\n", dev->name,
			ath_get_hal_status_desc(status), status,
			sc->sc_curchan.channel, sc->sc_curchan.channelFlags);
		error = -EIO;
		goto done;
	}

	if (sc->sc_softled)
		ath_hal_gpioCfgOutput(ah, sc->sc_ledpin);

	/* Turn off Interference Mitigation in non-STA modes */
	if ((sc->sc_opmode != HAL_M_STA) && sc->sc_hasintmit && !sc->sc_useintmit) {
		DPRINTF(sc, ATH_DEBUG_RESET,
			"%s: disabling interference mitigation (ANI)\n", __func__);
		ath_hal_setintmit(ah, 0);
	}

	/*
	 * This is needed only to setup initial state
	 * but it's best done after a reset.
	 */
	ath_update_txpow(sc);

	/* Set the default RX antenna; it may get lost on reset. */
	ath_setdefantenna(sc, sc->sc_defant);

	/*
	 * Setup the hardware after reset: the key cache
	 * is filled as needed and the receive engine is
	 * set going.  Frame transmit is handled entirely
	 * in the frame output path; there's nothing to do
	 * here except setup the interrupt mask.
	 */
#if 0
	ath_initkeytable(sc);		/* XXX still needed? */
#endif
	if (ath_startrecv(sc) != 0) {
		printk("%s: unable to start recv logic\n", dev->name);
		error = -EIO;
		goto done;
	}
	/* Enable interrupts. */
	sc->sc_imask = HAL_INT_RX | HAL_INT_TX
		  | HAL_INT_RXEOL | HAL_INT_RXORN
		  | HAL_INT_FATAL | HAL_INT_GLOBAL;
	/*
	 * Enable MIB interrupts when there are hardware phy counters.
	 * Note we only do this (at the moment) for station mode.
	 */
	if (sc->sc_needmib && ic->ic_opmode == IEEE80211_M_STA)
		sc->sc_imask |= HAL_INT_MIB;
	ath_hal_intrset(ah, sc->sc_imask);

	/*
	 * The hardware should be ready to go now so it's safe
	 * to kick the 802.11 state machine as it's likely to
	 * immediately call back to us to send mgmt frames.
	 */
	ath_chan_change(sc, ic->ic_curchan);
	ath_set_ack_bitrate(sc, sc->sc_ackrate);
	dev->flags |= IFF_RUNNING;		/* we are ready to go */
	ieee80211_start_running(ic);		/* start all VAPs */
#ifdef ATH_TX99_DIAG
	if (sc->sc_tx99 != NULL)
		sc->sc_tx99->start(sc->sc_tx99);
#endif
done:
	ATH_UNLOCK(sc);
	return error;
}

/* Caller must lock ATH_LOCK 
 *
 * Context: softIRQ
 */ 
static int
ath_stop_locked(struct net_device *dev)
{
	struct ath_softc *sc = dev->priv;
	struct ieee80211com *ic = &sc->sc_ic;
	struct ath_hal *ah = sc->sc_ah;

	DPRINTF(sc, ATH_DEBUG_RESET, "%s: invalid %u flags 0x%x\n",
		__func__, sc->sc_invalid, dev->flags);

	if (dev->flags & IFF_RUNNING) {
		/*
		 * Shutdown the hardware and driver:
		 *    stop output from above
		 *    reset 802.11 state machine
		 *	(sends station deassoc/deauth frames)
		 *    turn off timers
		 *    disable interrupts
		 *    clear transmit machinery
		 *    clear receive machinery
		 *    turn off the radio
		 *    reclaim beacon resources
		 *
		 * Note that some of this work is not possible if the
		 * hardware is gone (invalid).
		 */
#ifdef ATH_TX99_DIAG
		if (sc->sc_tx99 != NULL)
			sc->sc_tx99->stop(sc->sc_tx99);
#endif
		netif_stop_queue(dev);		/* XXX re-enabled by ath_newstate */
		dev->flags &= ~IFF_RUNNING;	/* NB: avoid recursion */
		ieee80211_stop_running(ic);	/* stop all VAPs */
		if (!sc->sc_invalid) {
			ath_hal_intrset(ah, 0);
			if (sc->sc_softled) {
				del_timer(&sc->sc_ledtimer);
				ath_hal_gpioset(ah, sc->sc_ledpin, !sc->sc_ledon);
				sc->sc_blinking = 0;
				sc->sc_ledstate = 1;
			}
		}
		ath_draintxq(sc);
		if (!sc->sc_invalid) {
			ath_stoprecv(sc);
			ath_hal_phydisable(ah);
		} else
			sc->sc_rxlink = NULL;
		ath_beacon_free(sc);		/* XXX needed? */
	} else
		ieee80211_stop_running(ic);	/* stop other VAPs */

	if (sc->sc_softled)
		ath_hal_gpioset(ah, sc->sc_ledpin, !sc->sc_ledon);
	
	return 0;
}

/*
 * Stop the device, grabbing the top-level lock to protect
 * against concurrent entry through ath_init (which can happen
 * if another thread does a system call and the thread doing the
 * stop is preempted).
 */
static int
ath_stop(struct net_device *dev)
{
	struct ath_softc *sc = dev->priv;
	int error;

	ATH_LOCK(sc);

	if (!sc->sc_invalid)
		ath_hal_setpower(sc->sc_ah, HAL_PM_AWAKE);

	error = ath_stop_locked(dev);
#if 0
	if (error == 0 && !sc->sc_invalid) {
		/*
		 * Set the chip in full sleep mode.  Note that we are
		 * careful to do this only when bringing the interface
		 * completely to a stop.  When the chip is in this state
		 * it must be carefully woken up or references to
		 * registers in the PCI clock domain may freeze the bus
		 * (and system).  This varies by chip and is mostly an
		 * issue with newer parts that go to sleep more quickly.
		 */
		ath_hal_setpower(sc->sc_ah, HAL_PM_FULL_SLEEP);
	}
#endif
	ATH_UNLOCK(sc);

	return error;
}

static int 
ar_device(int devid)
{
	switch (devid) {
	case AR5210_DEFAULT:
	case AR5210_PROD:
	case AR5210_AP:
		return 5210;
	case AR5211_DEFAULT:
	case AR5311_DEVID:
	case AR5211_LEGACY:
	case AR5211_FPGA11B:
		return 5211;
	case AR5212_DEFAULT:
	case AR5212_DEVID:
	case AR5212_FPGA:
	case AR5212_DEVID_IBM:
	case AR5212_AR5312_REV2:
	case AR5212_AR5312_REV7:
	case AR5212_AR2313_REV8:
	case AR5212_AR2315_REV6:
	case AR5212_AR2315_REV7:
	case AR5212_AR2317_REV1:
	case AR5212_DEVID_0014:
	case AR5212_DEVID_0015:
	case AR5212_DEVID_0016:
	case AR5212_DEVID_0017:
	case AR5212_DEVID_0018:
	case AR5212_DEVID_0019:
	case AR5212_AR2413:
	case AR5212_AR5413:
	case AR5212_AR5424:
	case AR5212_DEVID_FF19:
		return 5212;
	case AR5213_SREV_1_0:
	case AR5213_SREV_REG:
	case AR_SUBVENDOR_ID_NOG:
	case AR_SUBVENDOR_ID_NEW_A:
		return 5213;
	default: 
		return 0; /* unknown */
	}
}


static int 
ath_set_ack_bitrate(struct ath_softc *sc, int high) 
{
	struct ath_hal *ah = sc->sc_ah;
	if (ar_device(sc->devid) == 5212 || ar_device(sc->devid) == 5213) {
		/* set ack to be sent at low bit-rate */
		/* registers taken from the OpenBSD 5212 HAL */
#define AR5K_AR5212_STA_ID1                     0x8004
#define AR5K_AR5212_STA_ID1_ACKCTS_6MB          0x01000000
#define AR5K_AR5212_STA_ID1_BASE_RATE_11B       0x02000000
		u_int32_t v = AR5K_AR5212_STA_ID1_BASE_RATE_11B | AR5K_AR5212_STA_ID1_ACKCTS_6MB;
		if (high) {
			OS_REG_WRITE(ah, AR5K_AR5212_STA_ID1, OS_REG_READ(ah, AR5K_AR5212_STA_ID1) & ~v);
		} else {
			OS_REG_WRITE(ah, AR5K_AR5212_STA_ID1, OS_REG_READ(ah, AR5K_AR5212_STA_ID1) | v);
		}
		return 0;
	}
	return 1;
}

/*
 * Reset the hardware w/o losing operational state.  This is
 * basically a more efficient way of doing ath_stop, ath_init,
 * followed by state transitions to the current 802.11
 * operational state.  Used to recover from errors rx overrun
 * and to reset the hardware when rf gain settings must be reset.
 */
static int
ath_reset(struct net_device *dev)
{
	struct ath_softc *sc = dev->priv;
	struct ieee80211com *ic = &sc->sc_ic;
	struct ath_hal *ah = sc->sc_ah;
	struct ieee80211_channel *c;
	HAL_STATUS status;

	/*
	 * Convert to a HAL channel description with the flags
	 * constrained to reflect the current operating mode.
	 */
	c = ic->ic_curchan;
	sc->sc_curchan.channel = c->ic_freq;
	sc->sc_curchan.channelFlags = ath_chan2flags(c);

	ath_hal_intrset(ah, 0);		/* disable interrupts */
	ath_draintxq(sc);		/* stop xmit side */
	ath_stoprecv(sc);		/* stop recv side */
	/* NB: indicate channel change so we do a full reset */
	if (!ath_hal_reset(ah, sc->sc_opmode, &sc->sc_curchan, AH_TRUE, &status))
		printk("%s: %s: unable to reset hardware: '%s' (HAL status %u)\n",
			dev->name, __func__, ath_get_hal_status_desc(status), status);

	/* Turn off Interference Mitigation in non-STA modes */
	if ((sc->sc_opmode != HAL_M_STA) && sc->sc_hasintmit && !sc->sc_useintmit) {
		DPRINTF(sc, ATH_DEBUG_RESET,
			"%s: disabling interference mitigation (ANI)\n", __func__);
		ath_hal_setintmit(ah, 0);
	}

	ath_update_txpow(sc);		/* update tx power state */
	if (ath_startrecv(sc) != 0)	/* restart recv */
		printk("%s: %s: unable to start recv logic\n",
			dev->name, __func__);
	if (sc->sc_softled)
		ath_hal_gpioCfgOutput(ah, sc->sc_ledpin);

	/*
	 * We may be doing a reset in response to an ioctl
	 * that changes the channel so update any state that
	 * might change as a result.
	 */
	ath_chan_change(sc, c);
	if (sc->sc_beacons)
		ath_beacon_config(sc, NULL);	/* restart beacons */
	ath_hal_intrset(ah, sc->sc_imask);
	ath_set_ack_bitrate(sc, sc->sc_ackrate);
	netif_wake_queue(dev);		/* restart xmit */
#ifdef ATH_SUPERG_XR
	/*
	 * restart the group polls.
	 */
	if (sc->sc_xrgrppoll) {
		struct ieee80211vap *vap;
		TAILQ_FOREACH(vap, &ic->ic_vaps, iv_next)
			if (vap && (vap->iv_flags & IEEE80211_F_XR))
				break;
		ath_grppoll_stop(vap);
		ath_grppoll_start(vap, sc->sc_xrpollcount);
	}
#endif
	return 0;
}


/* Swap transmit descriptor.
 * if AH_NEED_DESC_SWAP flag is not defined this becomes a "null"
 * function.
 */
static __inline void
ath_desc_swap(struct ath_desc *ds)
{
#ifdef AH_NEED_DESC_SWAP
	ds->ds_link = cpu_to_le32(ds->ds_link);
	ds->ds_data = cpu_to_le32(ds->ds_data);
	ds->ds_ctl0 = cpu_to_le32(ds->ds_ctl0);
	ds->ds_ctl1 = cpu_to_le32(ds->ds_ctl1);
	ds->ds_hw[0] = cpu_to_le32(ds->ds_hw[0]);
	ds->ds_hw[1] = cpu_to_le32(ds->ds_hw[1]);
#endif
}

/*
 * Insert a buffer on a txq 
 * 
 */
static __inline void
ath_tx_txqaddbuf(struct ath_softc *sc, struct ieee80211_node *ni, 
	struct ath_txq *txq, struct ath_buf *bf, 
	struct ath_desc *lastds, int framelen)
{
	struct ath_hal *ah = sc->sc_ah;

	/*
	 * Insert the frame on the outbound list and
	 * pass it on to the hardware.
	 */
	ATH_TXQ_LOCK(txq);
	if (ni && ni->ni_vap && txq == &ATH_VAP(ni->ni_vap)->av_mcastq) {
		/*
		 * The CAB queue is started from the SWBA handler since
		 * frames only go out on DTIM and to avoid possible races.
		 */
		ath_hal_intrset(ah, sc->sc_imask & ~HAL_INT_SWBA);
		ATH_TXQ_INSERT_TAIL(txq, bf, bf_list);
		DPRINTF(sc, ATH_DEBUG_TX_PROC, "%s: txq depth = %d\n", __func__, txq->axq_depth);
		if (txq->axq_link != NULL) {
#ifdef AH_NEED_DESC_SWAP
			*txq->axq_link = cpu_to_le32(bf->bf_daddr);
#else
			*txq->axq_link = bf->bf_daddr;
#endif
			DPRINTF(sc, ATH_DEBUG_XMIT, "%s: link[%u](%p)=%llx (%p)\n",
				__func__,
				txq->axq_qnum, txq->axq_link,
				ito64(bf->bf_daddr), bf->bf_desc);
		}
		txq->axq_link = &lastds->ds_link;
		ath_hal_intrset(ah, sc->sc_imask);
	} else {
		ATH_TXQ_INSERT_TAIL(txq, bf, bf_list);
		DPRINTF(sc, ATH_DEBUG_TX_PROC, "%s: txq depth = %d\n", __func__, txq->axq_depth);
		if (txq->axq_link == NULL) {
			ath_hal_puttxbuf(ah, txq->axq_qnum, bf->bf_daddr);
			DPRINTF(sc, ATH_DEBUG_XMIT, "%s: TXDP[%u] = %llx (%p)\n",
				__func__,
				txq->axq_qnum, ito64(bf->bf_daddr), bf->bf_desc);
		} else {
#ifdef AH_NEED_DESC_SWAP
			*txq->axq_link = cpu_to_le32(bf->bf_daddr);
#else
			*txq->axq_link = bf->bf_daddr;
#endif
			DPRINTF(sc, ATH_DEBUG_XMIT, "%s: link[%u] (%p)=%llx (%p)\n",
				__func__,
				txq->axq_qnum, txq->axq_link,
				ito64(bf->bf_daddr), bf->bf_desc);
		}
		txq->axq_link = &lastds->ds_link;
		ath_hal_txstart(ah, txq->axq_qnum);
		sc->sc_dev->trans_start = jiffies;
	}
	ATH_TXQ_UNLOCK(txq);

	sc->sc_devstats.tx_packets++;
	sc->sc_devstats.tx_bytes += framelen;
}

static int 
dot11_to_ratecode(struct ath_softc *sc, const HAL_RATE_TABLE *rt, int dot11)
{
	int index = sc->sc_rixmap[dot11 & IEEE80211_RATE_VAL];
	if (index >= 0 && index < rt->rateCount)
		return rt->info[index].rateCode;
	
	return rt->info[sc->sc_minrateix].rateCode;
}


static int 
ath_tx_startraw(struct net_device *dev, struct ath_buf *bf, struct sk_buff *skb) 
{
	struct ath_softc *sc = dev->priv;
	struct ath_hal *ah = sc->sc_ah;
	struct ieee80211_phy_params *ph = (struct ieee80211_phy_params *) (skb->cb + sizeof(struct ieee80211_cb));
	const HAL_RATE_TABLE *rt;
	int pktlen;
	int hdrlen;
	HAL_PKT_TYPE atype;
	u_int flags;
	int keyix;
	int try0;
	int power;
	u_int8_t antenna, txrate;
	struct ath_txq *txq=NULL;
	struct ath_desc *ds=NULL;
	struct ieee80211_frame *wh; 
	
	wh = (struct ieee80211_frame *) skb->data;
	try0 = ph->try0;
	rt = sc->sc_currates;
	txrate = dot11_to_ratecode(sc, rt, ph->rate0);
	power = ph->power > 60 ? 60 : ph->power;
	hdrlen = ieee80211_anyhdrsize(wh);
	pktlen = skb->len + IEEE80211_CRC_LEN;
	
	keyix = HAL_TXKEYIX_INVALID;
	flags = HAL_TXDESC_INTREQ | HAL_TXDESC_CLRDMASK; /* XXX needed for crypto errs */
	
	bf->bf_skbaddr = bus_map_single(sc->sc_bdev,
					skb->data, pktlen, BUS_DMA_TODEVICE);
	DPRINTF(sc, ATH_DEBUG_XMIT, "%s: skb %p [data %p len %u] skbaddr %llx\n",
		__func__, skb, skb->data, skb->len, ito64(bf->bf_skbaddr));
	
	
	bf->bf_skb = skb;
	bf->bf_node = NULL;
	
#ifdef ATH_SUPERG_FF
	bf->bf_numdesc = 1;
#endif
	
	/* setup descriptors */
	ds = bf->bf_desc;
	rt = sc->sc_currates;
	KASSERT(rt != NULL, ("no rate table, mode %u", sc->sc_curmode));
	
	
	if (IEEE80211_IS_MULTICAST(wh->i_addr1)) {
		flags |= HAL_TXDESC_NOACK;	/* no ack on broad/multicast */
		sc->sc_stats.ast_tx_noack++;
		try0 = 1;
	}
	atype = HAL_PKT_TYPE_NORMAL;		/* default */
	txq = sc->sc_ac2q[skb->priority & 0x3];
	
	
	flags |= HAL_TXDESC_INTREQ;
	antenna = sc->sc_txantenna;
	
	/* XXX check return value? */
	ath_hal_setuptxdesc(ah, ds
			    , pktlen	/* packet length */
			    , hdrlen	/* header length */
			    , atype	/* Atheros packet type */
			    , power	/* txpower */
			    , txrate, try0 /* series 0 rate/tries */
			    , keyix	/* key cache index */
			    , antenna	/* antenna mode */
			    , flags	/* flags */
			    , 0		/* rts/cts rate */
			    , 0		/* rts/cts duration */
			    , 0		/* comp icv len */
			    , 0		/* comp iv len */
			    , ATH_COMP_PROC_NO_COMP_NO_CCS /* comp scheme */
			   );

	if (ph->try1) {
		ath_hal_setupxtxdesc(sc->sc_ah, ds
			, dot11_to_ratecode(sc, rt, ph->rate1), ph->try1 /* series 1 */
			, dot11_to_ratecode(sc, rt, ph->rate2), ph->try2 /* series 2 */
			, dot11_to_ratecode(sc, rt, ph->rate3), ph->try3 /* series 3 */
			);	
	}
	bf->bf_flags = flags;			/* record for post-processing */

	ds->ds_link = 0;
	ds->ds_data = bf->bf_skbaddr;
	
	ath_hal_filltxdesc(ah, ds
			   , skb->len	/* segment length */
			   , AH_TRUE	/* first segment */
			   , AH_TRUE	/* last segment */
			   , ds		/* first descriptor */
			   );
	
	/* NB: The desc swap function becomes void, 
	 * if descriptor swapping is not enabled
	 */
	ath_desc_swap(ds);
	
	DPRINTF(sc, ATH_DEBUG_XMIT, "%s: Q%d: %08x %08x %08x %08x %08x %08x\n",
		__func__, M_FLAG_GET(skb, M_UAPSD) ? 0 : txq->axq_qnum, ds->ds_link, ds->ds_data,
		ds->ds_ctl0, ds->ds_ctl1, ds->ds_hw[0], ds->ds_hw[1]);
		
	ath_tx_txqaddbuf(sc, NULL, txq, bf, ds, pktlen);
	return 0;
}

#ifdef ATH_SUPERG_FF
/*
 * Flush FF staging queue.
 */
static int
ath_ff_neverflushtestdone(struct ath_txq *txq, struct ath_buf *bf)
{
	return 0;
}

static int
ath_ff_ageflushtestdone(struct ath_txq *txq, struct ath_buf *bf)
{
	if ( (txq->axq_totalqueued - bf->bf_queueage) < ATH_FF_STAGEQAGEMAX )
		return 1;

	return 0;
}

/* Caller must not hold ATH_TXQ_LOCK and ATH_TXBUF_LOCK
 *
 * Context: softIRQ
 */
static void
ath_ffstageq_flush(struct ath_softc *sc, struct ath_txq *txq,
	int (*ath_ff_flushdonetest)(struct ath_txq *txq, struct ath_buf *bf))
{
	struct ath_buf *bf_ff = NULL;
	struct ieee80211_node *ni = NULL;
	int pktlen;
	int framecnt;

	for (;;) {
		ATH_TXQ_LOCK(txq);

		bf_ff = TAILQ_LAST(&txq->axq_stageq, axq_headtype);
		if ((!bf_ff) || ath_ff_flushdonetest(txq, bf_ff))
		{
			ATH_TXQ_UNLOCK(txq);
			break;
		}

		ni = bf_ff->bf_node;
		KASSERT(ATH_NODE(ni)->an_tx_ffbuf[bf_ff->bf_skb->priority],
			("no bf_ff on staging queue %p", bf_ff));
		ATH_NODE(ni)->an_tx_ffbuf[bf_ff->bf_skb->priority] = NULL;
		TAILQ_REMOVE(&txq->axq_stageq, bf_ff, bf_stagelist);

		ATH_TXQ_UNLOCK(txq);

		/* encap and xmit */
		bf_ff->bf_skb = ieee80211_encap(ni, bf_ff->bf_skb, &framecnt);
		if (bf_ff->bf_skb == NULL) {
			DPRINTF(sc, ATH_DEBUG_XMIT | ATH_DEBUG_FF,
				"%s: discard, encapsulation failure\n", __func__);
			sc->sc_stats.ast_tx_encap++;
			goto bad;
		}
		pktlen = bf_ff->bf_skb->len;	/* NB: don't reference skb below */
		if (ath_tx_start(sc->sc_dev, ni, bf_ff, bf_ff->bf_skb, 0) == 0)
			continue;
	bad:
		ieee80211_free_node(ni);
		if (bf_ff->bf_skb != NULL) {
			dev_kfree_skb(bf_ff->bf_skb);
			bf_ff->bf_skb = NULL;
		}
		bf_ff->bf_node = NULL;

		ATH_TXBUF_LOCK_IRQ(sc);
		STAILQ_INSERT_TAIL(&sc->sc_txbuf, bf_ff, bf_list);
		ATH_TXBUF_UNLOCK_IRQ(sc);
	}
}
#endif

#define ATH_HARDSTART_GET_TX_BUF_WITH_LOCK				\
	ATH_TXBUF_LOCK_IRQ(sc);						\
	bf = STAILQ_FIRST(&sc->sc_txbuf);				\
	if (bf != NULL) {						\
		STAILQ_REMOVE_HEAD(&sc->sc_txbuf, bf_list);		\
		STAILQ_INSERT_TAIL(&bf_head, bf, bf_list);              \
	}                                                               \
	/* XXX use a counter and leave at least one for mgmt frames */	\
	if (STAILQ_EMPTY(&sc->sc_txbuf)) {				\
		DPRINTF(sc, ATH_DEBUG_XMIT,				\
			"%s: stop queue\n", __func__);			\
		sc->sc_stats.ast_tx_qstop++;				\
		netif_stop_queue(dev); 					\
		sc->sc_devstopped = 1;					\
		ATH_SCHEDULE_TQUEUE(&sc->sc_txtq, NULL); 		\
	}								\
	ATH_TXBUF_UNLOCK_IRQ(sc);					\
	if (bf == NULL) {		/* NB: should not happen */	\
		DPRINTF(sc,ATH_DEBUG_XMIT,				\
			"%s: discard, no xmit buf\n", __func__);	\
		sc->sc_stats.ast_tx_nobuf++;				\
	}

/*
 * Transmit a data packet.  On failure caller is
 * assumed to reclaim the resources.
 *
 * Context: process context with BH's disabled
 */
static int
ath_hardstart(struct sk_buff *skb, struct net_device *dev)
{
	struct ath_softc *sc = dev->priv;
	struct ieee80211_node *ni = NULL;
	struct ath_buf *bf = NULL;
	struct ieee80211_cb *cb = (struct ieee80211_cb *) skb->cb;
	struct ether_header *eh;
	STAILQ_HEAD(tmp_bf_head, ath_buf) bf_head;
	struct ath_buf *tbf, *tempbf;
	struct sk_buff *tskb;
	struct ieee80211vap *vap;
	int framecnt;
	int requeue = 0;
#ifdef ATH_SUPERG_FF
	int pktlen;
	struct ieee80211com *ic = &sc->sc_ic;
	struct ath_node *an;
	struct ath_txq *txq = NULL;
	int ff_flush;
#endif

	if ((dev->flags & IFF_RUNNING) == 0 || sc->sc_invalid) {
		DPRINTF(sc, ATH_DEBUG_XMIT,
			"%s: discard, invalid %d flags %x\n",
			__func__, sc->sc_invalid, dev->flags);
		sc->sc_stats.ast_tx_invalid++;
		return -ENETDOWN;
	}

	STAILQ_INIT(&bf_head);

	if (cb->flags & M_RAW) {
		ATH_HARDSTART_GET_TX_BUF_WITH_LOCK;
		if (bf == NULL)
			goto hardstart_fail;
		ath_tx_startraw(dev, bf,skb);
		return NETDEV_TX_OK;
	}

	eh = (struct ether_header *)skb->data;
	ni = cb->ni;		/* NB: always passed down by 802.11 layer */
	if (ni == NULL) {
		/* NB: this happens if someone marks the underlying device up */
		DPRINTF(sc, ATH_DEBUG_XMIT,
			"%s: discard, no node in cb\n", __func__);
		goto hardstart_fail;
	}

	vap = ni->ni_vap;

#ifdef ATH_SUPERG_FF
	if (M_FLAG_GET(skb, M_UAPSD)) {
		/* bypass FF handling */
		ATH_HARDSTART_GET_TX_BUF_WITH_LOCK;
		if (bf == NULL)
			goto hardstart_fail;
		goto ff_bypass;
	}

	/*
	 * Fast frames check.
	 */
	ATH_FF_MAGIC_CLR(skb);
	an = ATH_NODE(ni);

	txq = sc->sc_ac2q[skb->priority];

	if (txq->axq_depth > TAIL_DROP_COUNT) {
		sc->sc_stats.ast_tx_discard++;
		/* queue is full, let the kernel backlog the skb */
		requeue = 1;
		goto hardstart_fail;
	}

	/* NB: use this lock to protect an->an_ff_txbuf in athff_can_aggregate()
	 *     call too.
	 */
	ATH_TXQ_LOCK(txq);
	if (athff_can_aggregate(sc, eh, an, skb, vap->iv_fragthreshold, &ff_flush)) {

		if (an->an_tx_ffbuf[skb->priority]) { /* i.e., frame on the staging queue */
			bf = an->an_tx_ffbuf[skb->priority];

			/* get (and remove) the frame from staging queue */
			TAILQ_REMOVE(&txq->axq_stageq, bf, bf_stagelist);
			an->an_tx_ffbuf[skb->priority] = NULL;

			ATH_TXQ_UNLOCK(txq);

			/*
			 * chain skbs and add FF magic
			 *
			 * NB: the arriving skb should not be on a list (skb->list),
			 *     so "re-using" the skb next field should be OK.
			 */
			bf->bf_skb->next = skb;
			skb->next = NULL;
			skb = bf->bf_skb;
			ATH_FF_MAGIC_PUT(skb);

			/* decrement extra node reference made when an_tx_ffbuf[] was set */
			//ieee80211_free_node(ni); /* XXX where was it set ? */

			DPRINTF(sc, ATH_DEBUG_XMIT | ATH_DEBUG_FF,
				"%s: aggregating fast-frame\n", __func__);
		} else {
			/* NB: careful grabbing the TX_BUF lock since still holding the txq lock.
			 *     this could be avoided by always obtaining the txbuf earlier,
			 *     but the "if" portion of this "if/else" clause would then need
			 *     to give the buffer back.
			 */
			ATH_HARDSTART_GET_TX_BUF_WITH_LOCK;
			if (bf == NULL) {
				ATH_TXQ_UNLOCK(txq);
				goto hardstart_fail;
			}
			DPRINTF(sc, ATH_DEBUG_XMIT | ATH_DEBUG_FF,
				"%s: adding to fast-frame stage Q\n", __func__);

			bf->bf_skb = skb;
			bf->bf_node = ni;
			bf->bf_queueage = txq->axq_totalqueued;
			an->an_tx_ffbuf[skb->priority] = bf;

			TAILQ_INSERT_HEAD(&txq->axq_stageq, bf, bf_stagelist);

			ATH_TXQ_UNLOCK(txq);

			return NETDEV_TX_OK;
		}
	} else {
		if (ff_flush) {
			struct ath_buf *bf_ff = an->an_tx_ffbuf[skb->priority];

			TAILQ_REMOVE(&txq->axq_stageq, bf_ff, bf_stagelist);
			an->an_tx_ffbuf[skb->priority] = NULL;

			ATH_TXQ_UNLOCK(txq);

			/* encap and xmit */
			bf_ff->bf_skb = ieee80211_encap(ni, bf_ff->bf_skb, &framecnt);

			if (bf_ff->bf_skb == NULL) {
				DPRINTF(sc, ATH_DEBUG_XMIT,
					"%s: discard, ff flush encap failure\n",
					__func__);
				sc->sc_stats.ast_tx_encap++;
				goto ff_flushbad;
			}
			pktlen = bf_ff->bf_skb->len;	/* NB: don't reference skb below */
			/* NB: ath_tx_start() will use ATH_TXBUF_LOCK_BH(). The _BH
			 *     portion is not needed here since we're running at
			 *     interrupt time, but should be harmless.
			 */
			if (ath_tx_start(dev, ni, bf_ff, bf_ff->bf_skb, 0))
				goto ff_flushbad;
			goto ff_flushdone;
		ff_flushbad:
			DPRINTF(sc, ATH_DEBUG_XMIT | ATH_DEBUG_FF,
				"%s: ff stageq flush failure\n", __func__);
			ieee80211_free_node(ni);
			if (bf_ff->bf_skb) {
				dev_kfree_skb(bf_ff->bf_skb);
				bf_ff->bf_skb = NULL;
			}
			bf_ff->bf_node = NULL;

			ATH_TXBUF_LOCK(sc);
			STAILQ_INSERT_TAIL(&sc->sc_txbuf, bf_ff, bf_list);
			ATH_TXBUF_UNLOCK(sc);
			goto ff_flushdone;
		}
		/*
		 * XXX: out-of-order condition only occurs for AP mode and multicast.
		 *      But, there may be no valid way to get this condition.
		 */
		else if (an->an_tx_ffbuf[skb->priority]) {
			DPRINTF(sc, ATH_DEBUG_XMIT | ATH_DEBUG_FF,
				"%s: Out-Of-Order fast-frame\n", __func__);
			ATH_TXQ_UNLOCK(txq);
		} else
			ATH_TXQ_UNLOCK(txq);

	ff_flushdone:
		ATH_HARDSTART_GET_TX_BUF_WITH_LOCK;
		if (bf == NULL)
			goto hardstart_fail;
	}

ff_bypass:

#else /* ATH_SUPERG_FF */

	ATH_HARDSTART_GET_TX_BUF_WITH_LOCK;

#endif /* ATH_SUPERG_FF */

	/*
	 * Encapsulate the packet for transmission.
	 */
	skb = ieee80211_encap(ni, skb, &framecnt);
	if (skb == NULL) {
		DPRINTF(sc, ATH_DEBUG_XMIT,
			"%s: discard, encapsulation failure\n", __func__);
		sc->sc_stats.ast_tx_encap++;
		goto hardstart_fail;
	}

	if (framecnt > 1) {
		int bfcnt;

		/*
		**  Allocate 1 ath_buf for each frame given 1 was 
		**  already alloc'd
		*/
		ATH_TXBUF_LOCK(sc);
		for (bfcnt = 1; bfcnt < framecnt; ++bfcnt) {
			if ((tbf = STAILQ_FIRST(&sc->sc_txbuf)) != NULL) {
				STAILQ_REMOVE_HEAD(&sc->sc_txbuf, bf_list);
				STAILQ_INSERT_TAIL(&bf_head, tbf, bf_list);
			}
			else
				break;
			
			ieee80211_ref_node(ni);
		}

		if (bfcnt != framecnt) {
			if (!STAILQ_EMPTY(&bf_head)) {
				/*
				**  Failed to alloc enough ath_bufs;
				**  return to sc_txbuf list
				*/
				STAILQ_FOREACH_SAFE(tbf, &bf_head, bf_list, tempbf) {
					STAILQ_INSERT_TAIL(&sc->sc_txbuf, tbf, bf_list);
				}
			}
			ATH_TXBUF_UNLOCK(sc);
			STAILQ_INIT(&bf_head);
			goto hardstart_fail;
		}
		ATH_TXBUF_UNLOCK(sc);

		while ((bf = STAILQ_FIRST(&bf_head)) != NULL && skb != NULL) {
			int nextfraglen = 0;

			STAILQ_REMOVE_HEAD(&bf_head, bf_list);
			tskb = skb->next;
			skb->next = NULL;
			if (tskb)
				nextfraglen = tskb->len;

			if (ath_tx_start(dev, ni, bf, skb, nextfraglen) != 0) {
				STAILQ_INSERT_TAIL(&bf_head, bf, bf_list);
				skb->next = tskb;
				goto hardstart_fail;
			}
			skb = tskb;
		}
	} else {
		if (ath_tx_start(dev, ni, bf, skb, 0) != 0) {
			STAILQ_INSERT_TAIL(&bf_head, bf, bf_list);
			goto hardstart_fail;
		}
	}

#ifdef ATH_SUPERG_FF
	/*
	 * flush out stale FF from staging Q for applicable operational modes.
	 */
	/* XXX: ADHOC mode too? */
	if (txq && ic->ic_opmode == IEEE80211_M_HOSTAP)
		ath_ffstageq_flush(sc, txq, ath_ff_ageflushtestdone);
#endif

	return NETDEV_TX_OK;

hardstart_fail:
	if (!STAILQ_EMPTY(&bf_head)) {
		ATH_TXBUF_LOCK(sc);
		STAILQ_FOREACH_SAFE(tbf, &bf_head, bf_list, tempbf) {
			tbf->bf_skb = NULL;
			tbf->bf_node = NULL;
			
			if (ni != NULL) 
				ieee80211_free_node(ni);

			STAILQ_INSERT_TAIL(&sc->sc_txbuf, tbf, bf_list);
		}
		ATH_TXBUF_UNLOCK(sc);
	}
	
	/* let the kernel requeue the skb (don't free it!) */
	if (requeue)
		return NETDEV_TX_BUSY;

	/* free sk_buffs */
	while (skb) {
		tskb = skb->next;
		skb->next = NULL;
		dev_kfree_skb(skb);
		skb = tskb;
	}
	return NETDEV_TX_OK;
}
#undef ATH_HARDSTART_GET_TX_BUF_WITH_LOCK

/*
 * Transmit a management frame.  On failure we reclaim the skbuff.
 * Note that management frames come directly from the 802.11 layer
 * and do not honor the send queue flow control.  Need to investigate
 * using priority queuing so management frames can bypass data.
 *
 * Context: hwIRQ and softIRQ
 */
static int
ath_mgtstart(struct ieee80211com *ic, struct sk_buff *skb)
{
	struct net_device *dev = ic->ic_dev;
	struct ath_softc *sc = dev->priv;
	struct ieee80211_node *ni = NULL;
	struct ath_buf *bf = NULL;
	struct ieee80211_cb *cb;
	int error;

	if ((dev->flags & IFF_RUNNING) == 0 || sc->sc_invalid) {
		DPRINTF(sc, ATH_DEBUG_XMIT,
			"%s: discard, invalid %d flags %x\n",
			__func__, sc->sc_invalid, dev->flags);
		sc->sc_stats.ast_tx_invalid++;
		error = -ENETDOWN;
		goto bad;
	}
	/*
	 * Grab a TX buffer and associated resources.
	 */
	ATH_TXBUF_LOCK_IRQ(sc);
	bf = STAILQ_FIRST(&sc->sc_txbuf);
	if (bf != NULL)
		STAILQ_REMOVE_HEAD(&sc->sc_txbuf, bf_list);
	if (STAILQ_EMPTY(&sc->sc_txbuf)) {
		DPRINTF(sc, ATH_DEBUG_XMIT, "%s: stop queue\n", __func__);
		sc->sc_stats.ast_tx_qstop++;
		netif_stop_queue(dev);
		sc->sc_devstopped=1;
		ATH_SCHEDULE_TQUEUE(&sc->sc_txtq, NULL);
	}
	ATH_TXBUF_UNLOCK_IRQ(sc);
	if (bf == NULL) {
		printk("ath_mgtstart: discard, no xmit buf\n");
		sc->sc_stats.ast_tx_nobufmgt++;
		error = -ENOBUFS;
		goto bad;
	}

	/*
	 * NB: the referenced node pointer is in the
	 * control block of the sk_buff.  This is
	 * placed there by ieee80211_mgmt_output because
	 * we need to hold the reference with the frame.
	 */
	cb = (struct ieee80211_cb *)skb->cb;
	ni = cb->ni;
	error = ath_tx_start(dev, ni, bf, skb, 0);
	if (error == 0) {
		sc->sc_stats.ast_tx_mgmt++;
		return 0;
	}
	/* fall thru... */
bad:
	if (ni != NULL)
		ieee80211_free_node(ni);
	if (bf != NULL) {
		bf->bf_skb = NULL;
		bf->bf_node = NULL;

		ATH_TXBUF_LOCK_IRQ(sc);
		STAILQ_INSERT_TAIL(&sc->sc_txbuf, bf, bf_list);
		ATH_TXBUF_UNLOCK_IRQ(sc);
	}
	dev_kfree_skb_any(skb);
	skb = NULL;
	return error;
}

#ifdef AR_DEBUG
static void
ath_keyprint(struct ath_softc *sc, const char *tag, u_int ix,
	const HAL_KEYVAL *hk, const u_int8_t mac[IEEE80211_ADDR_LEN])
{
	static const char *ciphers[] = {
		"WEP",
		"AES-OCB",
		"AES-CCM",
		"CKIP",
		"TKIP",
		"CLR",
	};
	int i, n;

	printk("%s: [%02u] %-7s ", tag, ix, ciphers[hk->kv_type]);
	for (i = 0, n = hk->kv_len; i < n; i++)
		printk("%02x", hk->kv_val[i]);
	printk(" mac %s", ether_sprintf(mac));
	if (hk->kv_type == HAL_CIPHER_TKIP) {
		printk(" %s ", sc->sc_splitmic ? "mic" : "rxmic");
		for (i = 0; i < sizeof(hk->kv_mic); i++)
			printk("%02x", hk->kv_mic[i]);
#if HAL_ABI_VERSION > 0x06052200
		if (!sc->sc_splitmic) {
			printk(" txmic ");
			for (i = 0; i < sizeof(hk->kv_txmic); i++)
				printk("%02x", hk->kv_txmic[i]);
		}
#endif
	}
	printk("\n");
}
#endif

/*
 * Set a TKIP key into the hardware.  This handles the
 * potential distribution of key state to multiple key
 * cache slots for TKIP.
 */
static int
ath_keyset_tkip(struct ath_softc *sc, const struct ieee80211_key *k,
	HAL_KEYVAL *hk, const u_int8_t mac[IEEE80211_ADDR_LEN])
{
#define	IEEE80211_KEY_XR	(IEEE80211_KEY_XMIT | IEEE80211_KEY_RECV)
	static const u_int8_t zerobssid[IEEE80211_ADDR_LEN];
	struct ath_hal *ah = sc->sc_ah;

	KASSERT(k->wk_cipher->ic_cipher == IEEE80211_CIPHER_TKIP,
		("got a non-TKIP key, cipher %u", k->wk_cipher->ic_cipher));
	if ((k->wk_flags & IEEE80211_KEY_XR) == IEEE80211_KEY_XR) {
		if (sc->sc_splitmic) {
			/*
			 * TX key goes at first index, RX key at the rx index.
			 * The HAL handles the MIC keys at index+64.
			 */
			memcpy(hk->kv_mic, k->wk_txmic, sizeof(hk->kv_mic));
			KEYPRINTF(sc, k->wk_keyix, hk, zerobssid);
			if (!ath_hal_keyset(ah, k->wk_keyix, hk, zerobssid))
				return 0;

			memcpy(hk->kv_mic, k->wk_rxmic, sizeof(hk->kv_mic));
			KEYPRINTF(sc, k->wk_keyix+32, hk, mac);
			/* XXX delete tx key on failure? */
			return ath_hal_keyset(ah, k->wk_keyix+32, hk, mac);
		} else {
			/*
			 * Room for both TX+RX MIC keys in one key cache
			 * slot, just set key at the first index; the HAL
			 * will handle the reset.
			 */
			memcpy(hk->kv_mic, k->wk_rxmic, sizeof(hk->kv_mic));
#if HAL_ABI_VERSION > 0x06052200
			memcpy(hk->kv_txmic, k->wk_txmic, sizeof(hk->kv_txmic));
#endif
			KEYPRINTF(sc, k->wk_keyix, hk, mac);
			return ath_hal_keyset(ah, k->wk_keyix, hk, mac);
		}
	} else if (k->wk_flags & IEEE80211_KEY_XR) {
		/*
		 * TX/RX key goes at first index.
		 * The HAL handles the MIC keys are index+64.
		 */
		memcpy(hk->kv_mic, k->wk_flags & IEEE80211_KEY_XMIT ?
			k->wk_txmic : k->wk_rxmic, sizeof(hk->kv_mic));
		KEYPRINTF(sc, k->wk_keyix, hk, mac);
		return ath_hal_keyset(ah, k->wk_keyix, hk, mac);
	}
	return 0;
#undef IEEE80211_KEY_XR
}

/*
 * Set a net80211 key into the hardware.  This handles the
 * potential distribution of key state to multiple key
 * cache slots for TKIP with hardware MIC support.
 */
static int
ath_keyset(struct ath_softc *sc, const struct ieee80211_key *k,
	const u_int8_t mac0[IEEE80211_ADDR_LEN],
	struct ieee80211_node *bss)
{
#define	N(a)	((int)(sizeof(a)/sizeof(a[0])))
	static const u_int8_t ciphermap[] = {
		HAL_CIPHER_WEP,		/* IEEE80211_CIPHER_WEP */
		HAL_CIPHER_TKIP,	/* IEEE80211_CIPHER_TKIP */
		HAL_CIPHER_AES_OCB,	/* IEEE80211_CIPHER_AES_OCB */
		HAL_CIPHER_AES_CCM,	/* IEEE80211_CIPHER_AES_CCM */
		(u_int8_t) -1,		/* 4 is not allocated */
		HAL_CIPHER_CKIP,	/* IEEE80211_CIPHER_CKIP */
		HAL_CIPHER_CLR,		/* IEEE80211_CIPHER_NONE */
	};
	struct ath_hal *ah = sc->sc_ah;
	const struct ieee80211_cipher *cip = k->wk_cipher;
	u_int8_t gmac[IEEE80211_ADDR_LEN];
	const u_int8_t *mac;
	HAL_KEYVAL hk;

	memset(&hk, 0, sizeof(hk));
	/*
	 * Software crypto uses a "clear key" so non-crypto
	 * state kept in the key cache are maintained and
	 * so that rx frames have an entry to match.
	 */
	if ((k->wk_flags & IEEE80211_KEY_SWCRYPT) == 0) {
		KASSERT(cip->ic_cipher < N(ciphermap),
			("invalid cipher type %u", cip->ic_cipher));
		hk.kv_type = ciphermap[cip->ic_cipher];
		hk.kv_len = k->wk_keylen;
		memcpy(hk.kv_val, k->wk_key, k->wk_keylen);
	} else
		hk.kv_type = HAL_CIPHER_CLR;

	if ((k->wk_flags & IEEE80211_KEY_GROUP) && sc->sc_mcastkey) {
		/*
		 * Group keys on hardware that supports multicast frame
		 * key search use a mac that is the sender's address with
		 * the high bit set instead of the app-specified address.
		 */
		IEEE80211_ADDR_COPY(gmac, bss->ni_macaddr);
		gmac[0] |= 0x80;
		mac = gmac;
	} else
		mac = mac0;

	if (hk.kv_type == HAL_CIPHER_TKIP &&
	    (k->wk_flags & IEEE80211_KEY_SWMIC) == 0) {
		return ath_keyset_tkip(sc, k, &hk, mac);
	} else {
		KEYPRINTF(sc, k->wk_keyix, &hk, mac);
		return ath_hal_keyset(ah, k->wk_keyix, &hk, mac);
	}
#undef N
}

/*
 * Allocate tx/rx key slots for TKIP.  We allocate two slots for
 * each key, one for decrypt/encrypt and the other for the MIC.
 */
static u_int16_t
key_alloc_2pair(struct ath_softc *sc)
{
#define	N(a)	((int)(sizeof(a)/sizeof(a[0])))
	u_int i, keyix;

	KASSERT(sc->sc_splitmic, ("key cache !split"));
	/* XXX could optimize */
	for (i = 0; i < N(sc->sc_keymap) / 4; i++) {
		u_int8_t b = sc->sc_keymap[i];
		if (b != 0xff) {
			/*
			 * One or more slots in this byte are free.
			 */
			keyix = i * NBBY;
			while (b & 1) {
		again:
				keyix++;
				b >>= 1;
			}
			/* XXX IEEE80211_KEY_XMIT | IEEE80211_KEY_RECV */
			if (isset(sc->sc_keymap, keyix + 32) ||
			    isset(sc->sc_keymap, keyix + 64) ||
			    isset(sc->sc_keymap, keyix + 32 + 64)) {
				/* full pair unavailable */
				/* XXX statistic */
				if (keyix == (i + 1) * NBBY) {
					/* no slots were appropriate, advance */
					continue;
				}
				goto again;
			}
			setbit(sc->sc_keymap, keyix);
			setbit(sc->sc_keymap, keyix + 64);
			setbit(sc->sc_keymap, keyix + 32);
			setbit(sc->sc_keymap, keyix + 32 + 64);
			DPRINTF(sc, ATH_DEBUG_KEYCACHE,
				"%s: key pair %u,%u %u,%u\n",
				__func__, keyix, keyix + 64,
				keyix + 32, keyix + 32 + 64);
			return keyix;
		}
	}
	DPRINTF(sc, ATH_DEBUG_KEYCACHE, "%s: out of pair space\n", __func__);
	return IEEE80211_KEYIX_NONE;
#undef N
}

/*
 * Allocate tx/rx key slots for TKIP.  We allocate two slots for
 * each key, one for decrypt/encrypt and the other for the MIC.
 */
static u_int16_t
key_alloc_pair(struct ath_softc *sc)
{
#define	N(a)	(sizeof(a)/sizeof(a[0]))
	u_int i, keyix;

	KASSERT(!sc->sc_splitmic, ("key cache split"));
	/* XXX could optimize */
	for (i = 0; i < N(sc->sc_keymap)/4; i++) {
		u_int8_t b = sc->sc_keymap[i];
		if (b != 0xff) {
			/*
			 * One or more slots in this byte are free.
			 */
			keyix = i*NBBY;
			while (b & 1) {
		again:
				keyix++;
				b >>= 1;
			}
			if (isset(sc->sc_keymap, keyix+64)) {
				/* full pair unavailable */
				/* XXX statistic */
				if (keyix == (i+1)*NBBY) {
					/* no slots were appropriate, advance */
					continue;
				}
				goto again;
			}
			setbit(sc->sc_keymap, keyix);
			setbit(sc->sc_keymap, keyix+64);
			DPRINTF(sc, ATH_DEBUG_KEYCACHE,
				"%s: key pair %u,%u\n",
				__func__, keyix, keyix+64);
			return keyix;
		}
	}
	DPRINTF(sc, ATH_DEBUG_KEYCACHE, "%s: out of pair space\n", __func__);
	return IEEE80211_KEYIX_NONE;
#undef N
}

/*
 * Allocate a single key cache slot.
 */
static u_int16_t
key_alloc_single(struct ath_softc *sc)
{
#define	N(a)	((int)(sizeof(a)/sizeof(a[0])))
	u_int i, keyix;

	/* XXX try i,i+32,i+64,i+32+64 to minimize key pair conflicts */
	for (i = 0; i < N(sc->sc_keymap); i++) {
		u_int8_t b = sc->sc_keymap[i];
		if (b != 0xff) {
			/*
			 * One or more slots are free.
			 */
			keyix = i * NBBY;
			while (b & 1)
				keyix++, b >>= 1;
			setbit(sc->sc_keymap, keyix);
			DPRINTF(sc, ATH_DEBUG_KEYCACHE, "%s: key %u\n",
				__func__, keyix);
			return keyix;
		}
	}
	DPRINTF(sc, ATH_DEBUG_KEYCACHE, "%s: out of space\n", __func__);
	return IEEE80211_KEYIX_NONE;
#undef N
}

/*
 * Allocate one or more key cache slots for a unicast key.  The
 * key itself is needed only to identify the cipher.  For hardware
 * TKIP with split cipher+MIC keys we allocate two key cache slot
 * pairs so that we can setup separate TX and RX MIC keys.  Note
 * that the MIC key for a TKIP key at slot i is assumed by the
 * hardware to be at slot i+64.  This limits TKIP keys to the first
 * 64 entries.
 */
static int
ath_key_alloc(struct ieee80211vap *vap, const struct ieee80211_key *k)
{
	struct net_device *dev = vap->iv_ic->ic_dev;
	struct ath_softc *sc = dev->priv;

	/*
	 * Group key allocation must be handled specially for
	 * parts that do not support multicast key cache search
	 * functionality.  For those parts the key id must match
	 * the h/w key index so lookups find the right key.  On
	 * parts w/ the key search facility we install the sender's
	 * mac address (with the high bit set) and let the hardware
	 * find the key w/o using the key id.  This is preferred as
	 * it permits us to support multiple users for adhoc and/or
	 * multi-station operation.
	 */
	if ((k->wk_flags & IEEE80211_KEY_GROUP) && !sc->sc_mcastkey) {
		int i;
		u_int keyix = IEEE80211_KEYIX_NONE;

		for (i = 0; i < IEEE80211_WEP_NKID; i++) {
			if (k == &vap->iv_nw_keys[i]) {
				keyix = i;
				break;
			}
		}
		if (keyix == IEEE80211_KEYIX_NONE) {
			/* should not happen */
			DPRINTF(sc, ATH_DEBUG_KEYCACHE,
				"%s: bogus group key\n", __func__);
			return IEEE80211_KEYIX_NONE;
		}

		/*
		 * XXX we pre-allocate the global keys so
		 * have no way to check if they've already been allocated.
		 */
		return keyix;
	}
	/*
	 * We allocate two pair for TKIP when using the h/w to do
	 * the MIC.  For everything else, including software crypto,
	 * we allocate a single entry.  Note that s/w crypto requires
	 * a pass-through slot on the 5211 and 5212.  The 5210 does
	 * not support pass-through cache entries and we map all
	 * those requests to slot 0.
	 *
	 * Allocate 1 pair of keys for WEP case. Make sure the key
	 * is not a shared-key.
	 */
	if (k->wk_flags & IEEE80211_KEY_SWCRYPT)
		return key_alloc_single(sc);
	else if (k->wk_cipher->ic_cipher == IEEE80211_CIPHER_TKIP &&
		(k->wk_flags & IEEE80211_KEY_SWMIC) == 0) {
		if (sc->sc_splitmic)
			return key_alloc_2pair(sc);
		else
			return key_alloc_pair(sc);
	} else
		return key_alloc_single(sc);
}

/*
 * Delete an entry in the key cache allocated by ath_key_alloc.
 */
static int
ath_key_delete(struct ieee80211vap *vap, const struct ieee80211_key *k,
				struct ieee80211_node *ninfo)
{
	struct net_device *dev = vap->iv_ic->ic_dev;
	struct ath_softc *sc = dev->priv;
	struct ath_hal *ah = sc->sc_ah;
	const struct ieee80211_cipher *cip = k->wk_cipher;
	struct ieee80211_node *ni;
	u_int keyix = k->wk_keyix;
	int rxkeyoff = 0;

	DPRINTF(sc, ATH_DEBUG_KEYCACHE, "%s: delete key %u\n", __func__, keyix);

	ath_hal_keyreset(ah, keyix);
	/*
	 * Check the key->node map and flush any ref.
	 */
	ni = sc->sc_keyixmap[keyix];
	if (ni != NULL) {
		ieee80211_free_node(ni);
		sc->sc_keyixmap[keyix] = NULL;
	}
	/*
	 * Handle split tx/rx keying required for TKIP with h/w MIC.
	 */
	if (cip->ic_cipher == IEEE80211_CIPHER_TKIP &&
	    (k->wk_flags & IEEE80211_KEY_SWMIC) == 0 && sc->sc_splitmic) {
		ath_hal_keyreset(ah, keyix + 32);	/* RX key */
		ni = sc->sc_keyixmap[keyix + 32];
		if (ni != NULL) {			/* as above... */
			ieee80211_free_node(ni);
			sc->sc_keyixmap[keyix + 32] = NULL;
		}
	}

	/* Remove receive key entry if one exists for static WEP case */
	if (ninfo != NULL) {
		rxkeyoff = ninfo->ni_rxkeyoff;
		if (rxkeyoff != 0) {
			ninfo->ni_rxkeyoff = 0;
			ath_hal_keyreset(ah, keyix + rxkeyoff);
			ni = sc->sc_keyixmap[keyix + rxkeyoff];
			if (ni != NULL) {	/* as above... */
				ieee80211_free_node(ni);
				sc->sc_keyixmap[keyix + rxkeyoff] = NULL;
			}
		}
	}

	if (keyix >= IEEE80211_WEP_NKID) {
		/*
		 * Don't touch keymap entries for global keys so
		 * they are never considered for dynamic allocation.
		 */
		clrbit(sc->sc_keymap, keyix);
		if (cip->ic_cipher == IEEE80211_CIPHER_TKIP &&
		    (k->wk_flags & IEEE80211_KEY_SWMIC) == 0) {
			clrbit(sc->sc_keymap, keyix + 64);	/* TX key MIC */
			if (sc->sc_splitmic) {
				/* +32 for RX key, +32+64 for RX key MIC */
				clrbit(sc->sc_keymap, keyix+32);
				clrbit(sc->sc_keymap, keyix+32+64);
			}
		}

		if (rxkeyoff != 0)
			clrbit(sc->sc_keymap, keyix + rxkeyoff);/*RX Key */
	}
	return 1;
}

/*
 * Set the key cache contents for the specified key.  Key cache
 * slot(s) must already have been allocated by ath_key_alloc.
 */
static int
ath_key_set(struct ieee80211vap *vap, const struct ieee80211_key *k,
	const u_int8_t mac[IEEE80211_ADDR_LEN])
{
	struct net_device *dev = vap->iv_ic->ic_dev;
	struct ath_softc *sc = dev->priv;

	return ath_keyset(sc, k, mac, vap->iv_bss);
}

/*
 * Block/unblock tx+rx processing while a key change is done.
 * We assume the caller serializes key management operations
 * so we only need to worry about synchronization with other
 * uses that originate in the driver.
 */
static void
ath_key_update_begin(struct ieee80211vap *vap)
{
	struct net_device *dev = vap->iv_ic->ic_dev;
	struct ath_softc *sc = dev->priv;

	DPRINTF(sc, ATH_DEBUG_KEYCACHE, "%s:\n", __func__);
	/*
	 * When called from the rx tasklet we cannot use
	 * tasklet_disable because it will block waiting
	 * for us to complete execution.
	 *
	 * XXX Using in_softirq is not right since we might
	 * be called from other soft irq contexts than
	 * ath_rx_tasklet.
	 */
	if (!in_softirq())
		tasklet_disable(&sc->sc_rxtq);
	netif_stop_queue(dev);
}

static void
ath_key_update_end(struct ieee80211vap *vap)
{
	struct net_device *dev = vap->iv_ic->ic_dev;
	struct ath_softc *sc = dev->priv;

	DPRINTF(sc, ATH_DEBUG_KEYCACHE, "%s:\n", __func__);
	netif_start_queue(dev);
	if (!in_softirq())		/* NB: see above */
		tasklet_enable(&sc->sc_rxtq);
}

/*
 * Calculate the receive filter according to the
 * operating mode and state:
 *
 * o always accept unicast, broadcast, and multicast traffic
 * o maintain current state of phy error reception (the HAL
 *   may enable phy error frames for noise immunity work)
 * o probe request frames are accepted only when operating in
 *   hostap, adhoc, or monitor modes
 * o enable promiscuous mode according to the interface state
 * o accept beacons:
 *   - when operating in adhoc mode so the 802.11 layer creates
 *     node table entries for peers,
 *   - when operating in station mode for collecting rssi data when
 *     the station is otherwise quiet, or
 *   - when operating as a repeater so we see repeater-sta beacons
 *   - when scanning
 */
static u_int32_t
ath_calcrxfilter(struct ath_softc *sc)
{
#define	RX_FILTER_PRESERVE	(HAL_RX_FILTER_PHYERR | HAL_RX_FILTER_PHYRADAR)
	struct ieee80211com *ic = &sc->sc_ic;
	struct net_device *dev = ic->ic_dev;
	struct ath_hal *ah = sc->sc_ah;
	u_int32_t rfilt;

	rfilt = (ath_hal_getrxfilter(ah) & RX_FILTER_PRESERVE) |
		 HAL_RX_FILTER_UCAST | HAL_RX_FILTER_BCAST |
		 HAL_RX_FILTER_MCAST;
	if (ic->ic_opmode != IEEE80211_M_STA)
		rfilt |= HAL_RX_FILTER_PROBEREQ;
	if (ic->ic_opmode != IEEE80211_M_HOSTAP && (dev->flags & IFF_PROMISC))
		rfilt |= HAL_RX_FILTER_PROM;
	if (ic->ic_opmode == IEEE80211_M_STA ||
	    sc->sc_opmode == HAL_M_IBSS ||	/* NB: AHDEMO too */
	    (sc->sc_nostabeacons) || sc->sc_scanning)
		rfilt |= HAL_RX_FILTER_BEACON;
	if (sc->sc_nmonvaps > 0) 
		rfilt |= (HAL_RX_FILTER_CONTROL | HAL_RX_FILTER_BEACON | 
			  HAL_RX_FILTER_PROBEREQ | HAL_RX_FILTER_PROM);
	return rfilt;
#undef RX_FILTER_PRESERVE
}

/*
 * Merge multicast addresses from all VAPs to form the
 * hardware filter.  Ideally we should only inspect our
 * own list and the 802.11 layer would merge for us but
 * that's a bit difficult so for now we put the onus on
 * the driver.
 */
static void
ath_merge_mcast(struct ath_softc *sc, u_int32_t mfilt[2])
{
	struct ieee80211com *ic = &sc->sc_ic;
	struct ieee80211vap *vap;
	struct dev_mc_list *mc;
	u_int32_t val;
	u_int8_t pos;

	mfilt[0] = mfilt[1] = 0;
	/* XXX locking */
	TAILQ_FOREACH(vap, &ic->ic_vaps, iv_next) {
		struct net_device *dev = vap->iv_dev;
		for (mc = dev->mc_list; mc; mc = mc->next) {
			/* calculate XOR of eight 6-bit values */
			val = LE_READ_4(mc->dmi_addr + 0);
			pos = (val >> 18) ^ (val >> 12) ^ (val >> 6) ^ val;
			val = LE_READ_4(mc->dmi_addr + 3);
			pos ^= (val >> 18) ^ (val >> 12) ^ (val >> 6) ^ val;
			pos &= 0x3f;
			mfilt[pos / 32] |= (1 << (pos % 32));
		}
	}
}

static void
ath_mode_init(struct net_device *dev)
{
	struct ath_softc *sc = dev->priv;
	struct ath_hal *ah = sc->sc_ah;
	u_int32_t rfilt, mfilt[2];

	/* configure rx filter */
	rfilt = ath_calcrxfilter(sc);
	ath_hal_setrxfilter(ah, rfilt);

	/* configure bssid mask */
	if (sc->sc_hasbmask)
		ath_hal_setbssidmask(ah, sc->sc_bssidmask);

	/* configure operational mode */
	ath_hal_setopmode(ah);

	/* calculate and install multicast filter */
	if ((dev->flags & IFF_ALLMULTI) == 0)
		ath_merge_mcast(sc, mfilt);
	else
		mfilt[0] = mfilt[1] = ~0;
	ath_hal_setmcastfilter(ah, mfilt[0], mfilt[1]);
	DPRINTF(sc, ATH_DEBUG_STATE,
	     "%s: RX filter 0x%x, MC filter %08x:%08x\n",
	     __func__, rfilt, mfilt[0], mfilt[1]);
}

/*
 * Set the slot time based on the current setting.
 */
static void
ath_setslottime(struct ath_softc *sc)
{
	struct ieee80211com *ic = &sc->sc_ic;
	struct ath_hal *ah = sc->sc_ah;

	if (sc->sc_slottimeconf > 0) /* manual override */
		ath_hal_setslottime(ah, sc->sc_slottimeconf);
	else if (ic->ic_flags & IEEE80211_F_SHSLOT)
		ath_hal_setslottime(ah, HAL_SLOT_TIME_9);
	else
		ath_hal_setslottime(ah, HAL_SLOT_TIME_20);
	sc->sc_updateslot = OK;
}

/*
 * Callback from the 802.11 layer to update the
 * slot time based on the current setting.
 */
static void
ath_updateslot(struct net_device *dev)
{
	struct ath_softc *sc = dev->priv;
	struct ieee80211com *ic = &sc->sc_ic;

	/*
	 * When not coordinating the BSS, change the hardware
	 * immediately.  For other operation we defer the change
	 * until beacon updates have propagated to the stations.
	 */
	if (ic->ic_opmode == IEEE80211_M_HOSTAP)
		sc->sc_updateslot = UPDATE;
	else if (dev->flags & IFF_RUNNING)
		ath_setslottime(sc);
}

#ifdef ATH_SUPERG_DYNTURBO
/*
 * Dynamic turbo support.
 * XXX much of this could be moved up to the net80211 layer.
 */

/*
 * Configure dynamic turbo state on beacon setup.
 */
static void
ath_beacon_dturbo_config(struct ieee80211vap *vap, u_int32_t intval)
{
#define	IS_CAPABLE(vap) \
	(vap->iv_bss && (vap->iv_bss->ni_ath_flags & (IEEE80211_ATHC_TURBOP )) == \
		(IEEE80211_ATHC_TURBOP))
	struct ieee80211com *ic = vap->iv_ic;
	struct ath_softc *sc = ic->ic_dev->priv;

	if (ic->ic_opmode == IEEE80211_M_HOSTAP && IS_CAPABLE(vap)) {

		/* Dynamic Turbo is supported on this channel. */
		sc->sc_dturbo = 1;
		sc->sc_dturbo_tcount = 0;
		sc->sc_dturbo_switch = 0;
		sc->sc_ignore_ar = 0;

		/* Set the initial ATHC_BOOST capability. */
		if (ic->ic_bsschan->ic_flags & CHANNEL_TURBO)
			ic->ic_ath_cap |=  IEEE80211_ATHC_BOOST;
		else
			ic->ic_ath_cap &= ~IEEE80211_ATHC_BOOST;

		/*
		 * Calculate time & bandwidth thresholds
		 *
		 * sc_dturbo_base_tmin  :  ~70 seconds
		 * sc_dturbo_turbo_tmax : ~120 seconds
		 *
		 * NB: scale calculated values to account for staggered
		 *     beacon handling
		 */
		sc->sc_dturbo_base_tmin  = 70  * 1024 / ic->ic_lintval;
		sc->sc_dturbo_turbo_tmax = 120 * 1024 / ic->ic_lintval;
		sc->sc_dturbo_turbo_tmin = 5 * 1024 / ic->ic_lintval;
		/* convert the thresholds from BW/sec to BW/beacon period */
		sc->sc_dturbo_bw_base    = ATH_TURBO_DN_THRESH/(1024/ic->ic_lintval);  
		sc->sc_dturbo_bw_turbo   = ATH_TURBO_UP_THRESH/(1024/ic->ic_lintval); 
		/* time in hold state in number of beacon */
		sc->sc_dturbo_hold_max   = (ATH_TURBO_PERIOD_HOLD * 1024)/ic->ic_lintval;
	} else {
		sc->sc_dturbo = 0;
		ic->ic_ath_cap &= ~IEEE80211_ATHC_BOOST;
	}
#undef IS_CAPABLE
}

/*
 * Update dynamic turbo state at SWBA.  We assume we care
 * called only if dynamic turbo has been enabled (sc_turbo).
 */
static void
ath_beacon_dturbo_update(struct ieee80211vap *vap, int *needmark,u_int8_t dtim)
{
	struct ieee80211com *ic = vap->iv_ic;
	struct ath_softc *sc = ic->ic_dev->priv;
	u_int32_t bss_traffic;

	/* TBD: Age out CHANNEL_INTERFERENCE */
	if (sc->sc_ignore_ar) {
		/* 
		 * Ignore AR for this beacon; a dynamic turbo
		 * switch just happened and the information
		 * is invalid.  Notify AR support of the channel
		 * change.
		 */
		sc->sc_ignore_ar = 0;
		ath_hal_ar_enable(sc->sc_ah);
	}
	sc->sc_dturbo_tcount++;
	/*
	 * Calculate BSS traffic over the previous interval.
	 */
	bss_traffic = (sc->sc_devstats.tx_bytes + sc->sc_devstats.rx_bytes)
		    - sc->sc_dturbo_bytes;
	sc->sc_dturbo_bytes = sc->sc_devstats.tx_bytes
			    + sc->sc_devstats.rx_bytes;
	if (ic->ic_ath_cap & IEEE80211_ATHC_BOOST) {
 		/* 
  		* before switching to base mode,
  		* make sure that the conditions( low rssi, low bw) to switch mode 
  		* hold for some time and time in turbo exceeds minimum turbo time.
  		*/
 
		if (sc->sc_dturbo_tcount >= sc->sc_dturbo_turbo_tmin && 
		   sc->sc_dturbo_hold ==0 &&
		   (bss_traffic < sc->sc_dturbo_bw_base || !sc->sc_rate_recn_state)) {
			sc->sc_dturbo_hold = 1;
		} else {
			if (sc->sc_dturbo_hold &&
			   bss_traffic >= sc->sc_dturbo_bw_turbo && sc->sc_rate_recn_state) {
				/* out of hold state */
				sc->sc_dturbo_hold = 0;
				sc->sc_dturbo_hold_count = sc->sc_dturbo_hold_max;
			}
		}
		if (sc->sc_dturbo_hold && sc->sc_dturbo_hold_count)
			sc->sc_dturbo_hold_count--;
		/*
		 * Current Mode: Turbo (i.e. BOOST)
		 *
		 * Transition to base occurs when one of the following
		 * is true:
		 *    1. its a DTIM beacon. 
		 *    2. Maximum time in BOOST has elapsed (120 secs).
		 *    3. Channel is marked with interference
		 *    4. Average BSS traffic falls below 4Mbps 
		 *    5. RSSI cannot support at least 18 Mbps rate 
		 * XXX do bw checks at true beacon interval?
		 */
		if (dtim && 
			(sc->sc_dturbo_tcount >= sc->sc_dturbo_turbo_tmax ||
			 ((vap->iv_bss->ni_ath_flags & IEEE80211_ATHC_AR) && 
			  (sc->sc_curchan.privFlags & CHANNEL_INTERFERENCE) &&
			  IEEE80211_IS_CHAN_2GHZ(ic->ic_curchan)) || 
			 !sc->sc_dturbo_hold_count)) {
			DPRINTF(sc, ATH_DEBUG_TURBO, "%s: Leaving turbo\n",
					sc->sc_dev->name);
			ic->ic_ath_cap &= ~IEEE80211_ATHC_BOOST;
			vap->iv_bss->ni_ath_flags &= ~IEEE80211_ATHC_BOOST;
			sc->sc_dturbo_tcount = 0;
			sc->sc_dturbo_switch = 1;
		}
	} else {
		/*
		 * Current Mode: BASE
		 *
		 * Transition to Turbo (i.e. BOOST) when all of the
		 * following are true:
		 *
		 * 1. its a DTIM beacon. 
		 * 2. Dwell time at base has exceeded minimum (70 secs)
		 * 3. Only DT-capable stations are associated
		 * 4. Channel is marked interference-free.
		 * 5. BSS data traffic averages at least 6Mbps 
		 * 6. RSSI is good enough to support 36Mbps 
		 * XXX do bw+rssi checks at true beacon interval?
		 */
		if (dtim && 
			(sc->sc_dturbo_tcount >= sc->sc_dturbo_base_tmin &&
			 (ic->ic_dt_sta_assoc != 0 &&
			  ic->ic_sta_assoc == ic->ic_dt_sta_assoc) &&
			 ((vap->iv_bss->ni_ath_flags & IEEE80211_ATHC_AR) == 0 || 
			  (sc->sc_curchan.privFlags & CHANNEL_INTERFERENCE) == 0) &&
			 bss_traffic >= sc->sc_dturbo_bw_turbo && 
			 sc->sc_rate_recn_state)) {
			DPRINTF(sc, ATH_DEBUG_TURBO, "%s: Entering turbo\n",
					sc->sc_dev->name);
			ic->ic_ath_cap |= IEEE80211_ATHC_BOOST;
			vap->iv_bss->ni_ath_flags |= IEEE80211_ATHC_BOOST;
			sc->sc_dturbo_tcount = 0;
			sc->sc_dturbo_switch = 1;
			sc->sc_dturbo_hold = 0;
			sc->sc_dturbo_hold_count = sc->sc_dturbo_hold_max;
		}
	}
}


static int 
ath_check_beacon_done(struct ath_softc *sc)
{
	struct ieee80211vap *vap=NULL;
	struct ath_vap *avp;
	struct ath_buf *bf;
	struct sk_buff *skb;
	struct ath_desc *ds;
	struct ath_hal *ah = sc->sc_ah;
	int slot;

	/*
	 * check if the last beacon went out with the mode change flag set.
	 */
	for (slot = 0; slot < ath_maxvaps; slot++) {
		if(sc->sc_bslot[slot]) { 
			vap = sc->sc_bslot[slot];
			break;
		}
	}
	if (!vap)
		 return 0;
	avp = ATH_VAP(vap);
	bf = avp->av_bcbuf;
	skb = bf->bf_skb;
	ds = bf->bf_desc;

	return (ath_hal_txprocdesc(ah, ds) != HAL_EINPROGRESS);

}

/*
 * Effect a turbo mode switch when operating in dynamic
 * turbo mode. wait for beacon to go out before switching.
 */
static void
ath_turbo_switch_mode(unsigned long data)
{
	struct net_device *dev = (struct net_device *)data;
	struct ath_softc *sc = dev->priv;
	struct ieee80211com *ic = &sc->sc_ic;
	int newflags;

	KASSERT(ic->ic_opmode == IEEE80211_M_HOSTAP,
		("unexpected operating mode %d", ic->ic_opmode));

	DPRINTF(sc, ATH_DEBUG_STATE, "%s: dynamic turbo switch to %s mode\n",
		dev->name,
		ic->ic_ath_cap & IEEE80211_ATHC_BOOST ? "turbo" : "base");

	if (!ath_check_beacon_done(sc)) {
		/* 
		 * beacon did not go out. reschedule tasklet.
		 */
		mod_timer(&sc->sc_dturbo_switch_mode, jiffies + msecs_to_jiffies(2));
		return;
	}

	/* TBD: DTIM adjustments, delay CAB queue tx until after transmit */
	newflags = ic->ic_bsschan->ic_flags;
	if (ic->ic_ath_cap & IEEE80211_ATHC_BOOST) {
		if (IEEE80211_IS_CHAN_2GHZ(ic->ic_bsschan)) {
			/*
			 * Ignore AR next beacon. the AR detection
			 * code detects the traffic in normal channel
			 * from stations during transition delays
			 * between AP and station.
			 */
			sc->sc_ignore_ar = 1;
			ath_hal_ar_disable(sc->sc_ah);
		}
		newflags |= IEEE80211_CHAN_TURBO;
	} else
		newflags &= ~IEEE80211_CHAN_TURBO;
	ieee80211_dturbo_switch(ic, newflags);
	/* XXX ieee80211_reset_erp? */
}
#endif /* ATH_SUPERG_DYNTURBO */

/*
 * Setup a h/w transmit queue for beacons.
 */
static int
ath_beaconq_setup(struct ath_hal *ah)
{
	HAL_TXQ_INFO qi;

	memset(&qi, 0, sizeof(qi));
	qi.tqi_aifs = 1;
	qi.tqi_cwmin = 0;
	qi.tqi_cwmax = 0;
#ifdef ATH_SUPERG_DYNTURBO
	qi.tqi_qflags = HAL_TXQ_TXDESCINT_ENABLE;
#endif
	/* NB: don't enable any interrupts */
	return ath_hal_setuptxqueue(ah, HAL_TX_QUEUE_BEACON, &qi);
}

/*
 * Configure IFS parameter for the beacon queue.
 */
static int
ath_beaconq_config(struct ath_softc *sc)
{
#define	ATH_EXPONENT_TO_VALUE(v)	((1<<v)-1)
	struct ieee80211com *ic = &sc->sc_ic;
	struct ath_hal *ah = sc->sc_ah;
	HAL_TXQ_INFO qi;

	ath_hal_gettxqueueprops(ah, sc->sc_bhalq, &qi);
	if (ic->ic_opmode == IEEE80211_M_HOSTAP) {
		/*
		 * Always burst out beacon and CAB traffic.
		 */
		qi.tqi_aifs = 1;
		qi.tqi_cwmin = 0;
		qi.tqi_cwmax = 0;
	} else {
		struct wmeParams *wmep =
			&ic->ic_wme.wme_chanParams.cap_wmeParams[WME_AC_BE];
		/*
		 * Adhoc mode; important thing is to use 2x cwmin.
		 */
		qi.tqi_aifs = wmep->wmep_aifsn;
		qi.tqi_cwmin = 2 * ATH_EXPONENT_TO_VALUE(wmep->wmep_logcwmin);
		qi.tqi_cwmax = ATH_EXPONENT_TO_VALUE(wmep->wmep_logcwmax);
	}

	if (!ath_hal_settxqueueprops(ah, sc->sc_bhalq, &qi)) {
		printk("%s: unable to update h/w beacon queue parameters\n",
			sc->sc_dev->name);
		return 0;
	} else {
		ath_hal_resettxqueue(ah, sc->sc_bhalq);	/* push to h/w */
		return 1;
	}
#undef ATH_EXPONENT_TO_VALUE
}

/*
 * Allocate and setup an initial beacon frame.
 *
 * Context: softIRQ
 */
static int
ath_beacon_alloc(struct ath_softc *sc, struct ieee80211_node *ni)
{
	struct ath_vap *avp = ATH_VAP(ni->ni_vap);
	struct ieee80211_frame *wh;
	struct ath_buf *bf;
	struct sk_buff *skb;

	/*
	 * release the previous beacon's skb if it already exists.
	 */
	bf = avp->av_bcbuf;
	if (bf->bf_skb != NULL) {
		bus_unmap_single(sc->sc_bdev,
		    bf->bf_skbaddr, bf->bf_skb->len, BUS_DMA_TODEVICE);
		dev_kfree_skb(bf->bf_skb);
		bf->bf_skb = NULL;
	}
	if (bf->bf_node != NULL) {
		ieee80211_free_node(bf->bf_node);
		bf->bf_node = NULL;
	}

	/*
	 * NB: the beacon data buffer must be 32-bit aligned;
	 * we assume the mbuf routines will return us something
	 * with this alignment (perhaps should assert).
	 */
	skb = ieee80211_beacon_alloc(ni, &avp->av_boff);
	if (skb == NULL) {
		DPRINTF(sc, ATH_DEBUG_BEACON, "%s: cannot get sk_buff\n",
			__func__);
		sc->sc_stats.ast_be_nobuf++;
		return -ENOMEM;
	}

	/*
	 * Calculate a TSF adjustment factor required for
	 * staggered beacons.  Note that we assume the format
	 * of the beacon frame leaves the tstamp field immediately
	 * following the header.
	 */
	if (sc->sc_stagbeacons && avp->av_bslot > 0) {
		uint64_t tuadjust;
		__le64 tsfadjust;
		/*
		 * The beacon interval is in TU's; the TSF in usecs.
		 * We figure out how many TU's to add to align the
		 * timestamp then convert to TSF units and handle
		 * byte swapping before writing it in the frame.
		 * The hardware will then add this each time a beacon
		 * frame is sent.  Note that we align VAPs 1..N
		 * and leave VAP 0 untouched.  This means VAP 0
		 * has a timestamp in one beacon interval while the
		 * others get a timestamp aligned to the next interval.
		 */
		tuadjust = (ni->ni_intval * (ath_maxvaps - avp->av_bslot)) / ath_maxvaps;
		tsfadjust = cpu_to_le64(tuadjust << 10);	/* TU->TSF */

		DPRINTF(sc, ATH_DEBUG_BEACON,
			"%s: %s beacons, bslot %d intval %u tsfadjust(Kus) %llu\n",
			__func__, sc->sc_stagbeacons ? "stagger" : "burst",
			avp->av_bslot, ni->ni_intval, (long long) tuadjust);

		wh = (struct ieee80211_frame *) skb->data;
		memcpy(&wh[1], &tsfadjust, sizeof(tsfadjust));
	}

	bf->bf_node = ieee80211_ref_node(ni);
	bf->bf_skbaddr = bus_map_single(sc->sc_bdev,
		skb->data, skb->len, BUS_DMA_TODEVICE);
	bf->bf_skb = skb;

	return 0;
}

/*
 * Setup the beacon frame for transmit.
 */
static void
ath_beacon_setup(struct ath_softc *sc, struct ath_buf *bf)
{
#define	USE_SHPREAMBLE(_ic) \
	(((_ic)->ic_flags & (IEEE80211_F_SHPREAMBLE | IEEE80211_F_USEBARKER))\
		== IEEE80211_F_SHPREAMBLE)
	struct ieee80211_node *ni = bf->bf_node;
	struct ieee80211com *ic = ni->ni_ic;
	struct sk_buff *skb = bf->bf_skb;
	struct ath_hal *ah = sc->sc_ah;
	struct ath_desc *ds;
	int flags;
	int antenna = sc->sc_txantenna;
	const HAL_RATE_TABLE *rt;
	u_int8_t rix, rate;
	int ctsrate = 0;
	int ctsduration = 0;

	DPRINTF(sc, ATH_DEBUG_BEACON_PROC, "%s: m %p len %u\n",
		__func__, skb, skb->len);

	/* setup descriptors */
	ds = bf->bf_desc;

	flags = HAL_TXDESC_NOACK;
#ifdef ATH_SUPERG_DYNTURBO
	if (sc->sc_dturbo_switch)
		flags |= HAL_TXDESC_INTREQ;
#endif

	if (ic->ic_opmode == IEEE80211_M_IBSS && sc->sc_hasveol) {
		ds->ds_link = bf->bf_daddr;	/* self-linked */
		flags |= HAL_TXDESC_VEOL;
		/*
		 * Let hardware handle antenna switching if txantenna is not set
		 */
	} else {
		ds->ds_link = 0;
		/*
		 * Switch antenna every beacon if txantenna is not set
		 * Should only switch every beacon period, not for every
		 * SWBA's
		 * XXX assumes two antenna
		 */
		if (antenna == 0) {
			if (sc->sc_stagbeacons)
				antenna = ((sc->sc_stats.ast_be_xmit / sc->sc_nbcnvaps) & 1 ? 2 : 1);
			else
				antenna = (sc->sc_stats.ast_be_xmit & 1 ? 2 : 1);
		}
	}

	ds->ds_data = bf->bf_skbaddr;
	/*
	 * Calculate rate code.
	 * XXX everything at min xmit rate
	 */
	rix = sc->sc_minrateix;
	rt = sc->sc_currates;
	rate = rt->info[rix].rateCode;
	if (USE_SHPREAMBLE(ic))
		rate |= rt->info[rix].shortPreamble;
#ifdef ATH_SUPERG_XR
	if (bf->bf_node->ni_vap->iv_flags & IEEE80211_F_XR) {
		u_int8_t cix;
		int pktlen;
		pktlen = skb->len + IEEE80211_CRC_LEN;
		cix = rt->info[sc->sc_protrix].controlRate;
		/* for XR VAP use different RTSCTS rates and calculate duration */
		ctsrate = rt->info[cix].rateCode;
		if (USE_SHPREAMBLE(ic))
			ctsrate |= rt->info[cix].shortPreamble;
		flags |= HAL_TXDESC_CTSENA;
		rt = sc->sc_xr_rates;
		ctsduration = ath_hal_computetxtime(ah,rt, pktlen,
			IEEE80211_XR_DEFAULT_RATE_INDEX, AH_FALSE);
		rate = rt->info[IEEE80211_XR_DEFAULT_RATE_INDEX].rateCode;
	}
#endif
	ath_hal_setuptxdesc(ah, ds
		, skb->len + IEEE80211_CRC_LEN	/* frame length */
		, sizeof(struct ieee80211_frame)	/* header length */
		, HAL_PKT_TYPE_BEACON		/* Atheros packet type */
		, ni->ni_txpower		/* txpower XXX */
		, rate, 1			/* series 0 rate/tries */
		, HAL_TXKEYIX_INVALID		/* no encryption */
		, antenna			/* antenna mode */
		, flags				/* no ack, veol for beacons */
		, ctsrate			/* rts/cts rate */
		, ctsduration			/* rts/cts duration */
		, 0				/* comp icv len */
		, 0				/* comp iv len */
		, ATH_COMP_PROC_NO_COMP_NO_CCS	/* comp scheme */
	);

	/* NB: beacon's BufLen must be a multiple of 4 bytes */
	ath_hal_filltxdesc(ah, ds
		, roundup(skb->len, 4)	/* buffer length */
		, AH_TRUE		/* first segment */
		, AH_TRUE		/* last segment */
		, ds			/* first descriptor */
	);

	/* NB: The desc swap function becomes void, 
	 * if descriptor swapping is not enabled
	 */
	ath_desc_swap(ds);
#undef USE_SHPREAMBLE
}

/*
 * Generate beacon frame and queue cab data for a VAP.
 */
static struct ath_buf *
ath_beacon_generate(struct ath_softc *sc, struct ieee80211vap *vap, int *needmark)
{
	struct ath_hal *ah = sc->sc_ah;
	struct ath_buf *bf;
	struct ieee80211_node *ni;
	struct ath_vap *avp;
	struct sk_buff *skb;
	int ncabq;
	unsigned int curlen;

	if (vap->iv_state != IEEE80211_S_RUN) {
		DPRINTF(sc, ATH_DEBUG_BEACON_PROC, "%s: skip VAP in %s state\n",
			__func__, ieee80211_state_name[vap->iv_state]);
		return NULL;
	}
#ifdef ATH_SUPERG_XR
	if (vap->iv_flags & IEEE80211_F_XR) {
		vap->iv_xrbcnwait++;
		/* wait for XR_BEACON_FACTOR times before sending the beacon */
		if (vap->iv_xrbcnwait < IEEE80211_XR_BEACON_FACTOR)
			return NULL;
		vap->iv_xrbcnwait = 0;
	}
#endif
	avp = ATH_VAP(vap);
	if (avp->av_bcbuf == NULL) {
		DPRINTF(sc, ATH_DEBUG_ANY, "%s: avp=%p av_bcbuf=%p\n",
			 __func__, avp, avp->av_bcbuf);
		return NULL;
	}
	bf = avp->av_bcbuf;
	ni = bf->bf_node;

#ifdef ATH_SUPERG_DYNTURBO
	/* 
	 * If we are using dynamic turbo, update the
	 * capability info and arrange for a mode change
	 * if needed.
	 */
	if (sc->sc_dturbo) {
		u_int8_t dtim;
		dtim = ((avp->av_boff.bo_tim[2] == 1) ||
			(avp->av_boff.bo_tim[3] == 1));
		ath_beacon_dturbo_update(vap, needmark, dtim);
	}
#endif
	/*
	 * Update dynamic beacon contents.  If this returns
	 * non-zero then we need to remap the memory because
	 * the beacon frame changed size (probably because
	 * of the TIM bitmap).
	 */
	skb = bf->bf_skb;
	curlen = skb->len;
	ncabq = avp->av_mcastq.axq_depth;
	if (ieee80211_beacon_update(ni, &avp->av_boff, skb, ncabq)) {
		bus_unmap_single(sc->sc_bdev,
			bf->bf_skbaddr, curlen, BUS_DMA_TODEVICE);
		bf->bf_skbaddr = bus_map_single(sc->sc_bdev,
			skb->data, skb->len, BUS_DMA_TODEVICE);
	}

	/*
	 * if the CABQ traffic from previous DTIM is pending and the current
	 * beacon is also a DTIM. 
	 *  1) if there is only one VAP let the cab traffic continue. 
	 *  2) if there are more than one VAP and we are using staggered
	 *     beacons, then drain the cabq by dropping all the frames in
	 *     the cabq so that the current VAP's cab traffic can be scheduled.
	 * XXX: Need to handle the last MORE_DATA bit here.
	 */
	if (ncabq && (avp->av_boff.bo_tim[4] & 1) && sc->sc_cabq->axq_depth) {
		if (sc->sc_nvaps > 1 && sc->sc_stagbeacons) {
			ath_tx_draintxq(sc, sc->sc_cabq);
			DPRINTF(sc, ATH_DEBUG_BEACON,
				"%s: flush previous cabq traffic\n", __func__);
		}
	}

	/*
	 * Construct tx descriptor.
	 */
	ath_beacon_setup(sc, bf);

	bus_dma_sync_single(sc->sc_bdev,
		bf->bf_skbaddr, bf->bf_skb->len, BUS_DMA_TODEVICE);

	/*
	 * Enable the CAB queue before the beacon queue to
	 * ensure cab frames are triggered by this beacon.
	 */
	if (avp->av_boff.bo_tim[4] & 1)	{	/* NB: only at DTIM */
		struct ath_txq *cabq = sc->sc_cabq;
		struct ath_buf *bfmcast;
		/*
		 * Move everything from the VAP's mcast queue 
		 * to the hardware cab queue.
		 */
		ATH_TXQ_LOCK(&avp->av_mcastq);
		ATH_TXQ_LOCK(cabq);
		bfmcast = STAILQ_FIRST(&avp->av_mcastq.axq_q);
		/* link the descriptors */
		if (cabq->axq_link == NULL)
			ath_hal_puttxbuf(ah, cabq->axq_qnum, bfmcast->bf_daddr);
		else {
#ifdef AH_NEED_DESC_SWAP
			*cabq->axq_link = cpu_to_le32(bfmcast->bf_daddr);
#else
			*cabq->axq_link = bfmcast->bf_daddr;
#endif
		}

		/* Set the MORE_DATA bit for each packet except the last one */
		STAILQ_FOREACH(bfmcast, &avp->av_mcastq.axq_q, bf_list) {
			if (bfmcast != STAILQ_LAST(&avp->av_mcastq.axq_q, ath_buf, bf_list))
				((struct ieee80211_frame *)bfmcast->bf_skb->data)->i_fc[1] |= IEEE80211_FC1_MORE_DATA;
		}

		/* append the private VAP mcast list to the cabq */
		ATH_TXQ_MOVE_MCASTQ(&avp->av_mcastq, cabq);
		/* NB: gated by beacon so safe to start here */
		ath_hal_txstart(ah, cabq->axq_qnum);
		ATH_TXQ_UNLOCK(cabq);
		ATH_TXQ_UNLOCK(&avp->av_mcastq);
	}

	return bf;
}

/*
 * Transmit one or more beacon frames at SWBA.  Dynamic
 * updates to the frame contents are done as needed and
 * the slot time is also adjusted based on current state.
 */
static void
ath_beacon_send(struct ath_softc *sc, int *needmark)
{
#define	TSF_TO_TU(_h,_l) \
	((((u_int32_t)(_h)) << 22) | (((u_int32_t)(_l)) >> 10))
	struct ath_hal *ah = sc->sc_ah;
	struct ieee80211vap *vap;
	struct ath_buf *bf;
	int slot;
	u_int32_t bfaddr;

	/*
	 * Check if the previous beacon has gone out.  If
	 * not don't try to post another, skip this period
	 * and wait for the next.  Missed beacons indicate
	 * a problem and should not occur.  If we miss too
	 * many consecutive beacons reset the device.
	 */
	if (ath_hal_numtxpending(ah, sc->sc_bhalq) != 0) {
		sc->sc_bmisscount++;
		/* XXX: 802.11h needs the chanchange IE countdown decremented.
		 *      We should consider adding a net80211 call to indicate
		 *      a beacon miss so appropriate action could be taken
		 *      (in that layer).
		 */
		DPRINTF(sc, ATH_DEBUG_BEACON_PROC,
			"%s: missed %u consecutive beacons\n",
			__func__, sc->sc_bmisscount);
		if (sc->sc_bmisscount > BSTUCK_THRESH)
			ATH_SCHEDULE_TQUEUE(&sc->sc_bstucktq, needmark);
		return;
	}
	if (sc->sc_bmisscount != 0) {
		DPRINTF(sc, ATH_DEBUG_BEACON_PROC,
			"%s: resume beacon xmit after %u misses\n",
			__func__, sc->sc_bmisscount);
		sc->sc_bmisscount = 0;
	}

	/*
	 * Generate beacon frames.  If we are sending frames
	 * staggered then calculate the slot for this frame based
	 * on the tsf to safeguard against missing an swba.
	 * Otherwise we are bursting all frames together and need
	 * to generate a frame for each VAP that is up and running.
	 */
	if (sc->sc_stagbeacons) {		/* staggered beacons */
		struct ieee80211com *ic = &sc->sc_ic;
		u_int64_t tsf;
		u_int32_t tsftu;

		tsf = ath_hal_gettsf64(ah);
		tsftu = TSF_TO_TU(tsf >> 32, tsf);
		slot = ((tsftu % ic->ic_lintval) * ath_maxvaps) / ic->ic_lintval;
		vap = sc->sc_bslot[(slot + 1) % ath_maxvaps];
		DPRINTF(sc, ATH_DEBUG_BEACON_PROC,
			"%s: slot %d [tsf %llu tsftu %u intval %u] vap %p\n",
			__func__, slot, (long long) tsf, tsftu, ic->ic_lintval, vap);
		bfaddr = 0;
		if (vap != NULL) {
			bf = ath_beacon_generate(sc, vap, needmark);
			if (bf != NULL)
				bfaddr = bf->bf_daddr;
		}
	} else {				/* burst'd beacons */
		u_int32_t *bflink;

		bflink = &bfaddr;
		/* XXX rotate/randomize order? */
		for (slot = 0; slot < ath_maxvaps; slot++) {
			vap = sc->sc_bslot[slot];
			if (vap != NULL) {
				bf = ath_beacon_generate(sc, vap, needmark);
				if (bf != NULL) {
#ifdef AH_NEED_DESC_SWAP
					if (bflink != &bfaddr)
						*bflink = cpu_to_le32(bf->bf_daddr);
					else
						*bflink = bf->bf_daddr;
#else
					*bflink = bf->bf_daddr;
#endif
					bflink = &bf->bf_desc->ds_link;
				}
			}
		}
		*bflink = 0;			/* link of last frame */
	}

	/*
	 * Handle slot time change when a non-ERP station joins/leaves
	 * an 11g network.  The 802.11 layer notifies us via callback,
	 * we mark updateslot, then wait one beacon before effecting
	 * the change.  This gives associated stations at least one
	 * beacon interval to note the state change.
	 *
	 * NB: The slot time change state machine is clocked according
	 *     to whether we are bursting or staggering beacons.  We
	 *     recognize the request to update and record the current
	 *     slot then don't transition until that slot is reached
	 *     again.  If we miss a beacon for that slot then we'll be
	 *     slow to transition but we'll be sure at least one beacon
	 *     interval has passed.  When bursting slot is always left
	 *     set to ath_maxvaps so this check is a no-op.
	 */
	/* XXX locking */
	if (sc->sc_updateslot == UPDATE) {
		sc->sc_updateslot = COMMIT;	/* commit next beacon */
		sc->sc_slotupdate = slot;
	} else if (sc->sc_updateslot == COMMIT && sc->sc_slotupdate == slot)
		ath_setslottime(sc);		/* commit change to hardware */

	if ((!sc->sc_stagbeacons || slot == 0) && (!sc->sc_diversity)) {
		int otherant;
		/*
		 * Check recent per-antenna transmit statistics and flip
		 * the default rx antenna if noticeably more frames went out
		 * on the non-default antenna.  Only do this if rx diversity
		 * is off.
		 * XXX assumes 2 antennae
		 */
		otherant = sc->sc_defant & 1 ? 2 : 1;
		if (sc->sc_ant_tx[otherant] > sc->sc_ant_tx[sc->sc_defant] + ATH_ANTENNA_DIFF) {
			DPRINTF(sc, ATH_DEBUG_BEACON,
				"%s: flip defant to %u, %u > %u\n",
				__func__, otherant, sc->sc_ant_tx[otherant],
				sc->sc_ant_tx[sc->sc_defant]);
			ath_setdefantenna(sc, otherant);
		}
		sc->sc_ant_tx[1] = sc->sc_ant_tx[2] = 0;
	}

	if (bfaddr != 0) {
		/*
		 * Stop any current DMA and put the new frame(s) on the queue.
		 * This should never fail since we check above that no frames
		 * are still pending on the queue.
		 */
		if (!ath_hal_stoptxdma(ah, sc->sc_bhalq)) {
			DPRINTF(sc, ATH_DEBUG_ANY,
				"%s: beacon queue %u did not stop?\n",
				__func__, sc->sc_bhalq);
			/* NB: the HAL still stops DMA, so proceed */
		}
		/* NB: cabq traffic should already be queued and primed */
		ath_hal_puttxbuf(ah, sc->sc_bhalq, bfaddr);
		ath_hal_txstart(ah, sc->sc_bhalq);

		sc->sc_stats.ast_be_xmit++;		/* XXX per-VAP? */
	}
#undef TSF_TO_TU
}

/*
 * Reset the hardware after detecting beacons have stopped.
 */
static void
ath_bstuck_tasklet(TQUEUE_ARG data)
{
	struct net_device *dev = (struct net_device *)data;
	struct ath_softc *sc = dev->priv;
	/*
	 * XXX:if the bmisscount is cleared while the 
	 *     tasklet execution is pending, the following
	 *     check will be true, in which case return 
	 *     without resetting the driver.
	 */
	if (sc->sc_bmisscount <= BSTUCK_THRESH) 
		return;
	printk("%s: stuck beacon; resetting (bmiss count %u)\n",
		dev->name, sc->sc_bmisscount);
	ath_reset(dev);
}

/*
 * Startup beacon transmission for adhoc mode when
 * they are sent entirely by the hardware using the
 * self-linked descriptor + veol trick.
 */
static void
ath_beacon_start_adhoc(struct ath_softc *sc, struct ieee80211vap *vap)
{
	struct ath_hal *ah = sc->sc_ah;
	struct ath_buf *bf;
	struct ieee80211_node *ni;
	struct ath_vap *avp;
	struct sk_buff *skb;

	avp = ATH_VAP(vap);
	if (avp->av_bcbuf == NULL) {
		DPRINTF(sc, ATH_DEBUG_ANY, "%s: avp=%p av_bcbuf=%p\n",
			 __func__, avp, avp != NULL ? avp->av_bcbuf : NULL);
		return;
	}
	bf = avp->av_bcbuf;
	ni = bf->bf_node;

	/*
	 * Update dynamic beacon contents.  If this returns
	 * non-zero then we need to remap the memory because
	 * the beacon frame changed size (probably because
	 * of the TIM bitmap).
	 */
	skb = bf->bf_skb;
	if (ieee80211_beacon_update(ni, &avp->av_boff, skb, 0)) {
		bus_unmap_single(sc->sc_bdev,
			bf->bf_skbaddr, bf->bf_skb->len, BUS_DMA_TODEVICE);
		bf->bf_skbaddr = bus_map_single(sc->sc_bdev,
			skb->data, skb->len, BUS_DMA_TODEVICE);
	}

	/*
	 * Construct tx descriptor.
	 */
	ath_beacon_setup(sc, bf);

	bus_dma_sync_single(sc->sc_bdev,
		bf->bf_skbaddr, bf->bf_skb->len, BUS_DMA_TODEVICE);

	/* NB: caller is known to have already stopped tx DMA */
	ath_hal_puttxbuf(ah, sc->sc_bhalq, bf->bf_daddr);
	ath_hal_txstart(ah, sc->sc_bhalq);
	DPRINTF(sc, ATH_DEBUG_BEACON_PROC, "%s: TXDP%u = %llx (%p)\n", __func__,
		sc->sc_bhalq, ito64(bf->bf_daddr), bf->bf_desc);
}

/*
 * Reclaim beacon resources and return buffer to the pool.
 */
static void
ath_beacon_return(struct ath_softc *sc, struct ath_buf *bf)
{
	if (bf->bf_skb != NULL) {
		bus_unmap_single(sc->sc_bdev,
		    bf->bf_skbaddr, bf->bf_skb->len, BUS_DMA_TODEVICE);
		dev_kfree_skb(bf->bf_skb);
		bf->bf_skb = NULL;
	}
	if (bf->bf_node != NULL) {
		ieee80211_free_node(bf->bf_node);
		bf->bf_node = NULL;
	}
	STAILQ_INSERT_TAIL(&sc->sc_bbuf, bf, bf_list);
}

/*
 * Reclaim all beacon resources.
 */
static void
ath_beacon_free(struct ath_softc *sc)
{
	struct ath_buf *bf;

	STAILQ_FOREACH(bf, &sc->sc_bbuf, bf_list) {
		if (bf->bf_skb != NULL) {
			bus_unmap_single(sc->sc_bdev,
				bf->bf_skbaddr, bf->bf_skb->len, BUS_DMA_TODEVICE);
			dev_kfree_skb(bf->bf_skb);
			bf->bf_skb = NULL;
		}
		if (bf->bf_node != NULL) {
			ieee80211_free_node(bf->bf_node);
			bf->bf_node = NULL;
		}
	}
}

/*
 * Configure the beacon and sleep timers.
 *
 * When operating as an AP this resets the TSF and sets
 * up the hardware to notify us when we need to issue beacons.
 *
 * When operating in station mode this sets up the beacon
 * timers according to the timestamp of the last received
 * beacon and the current TSF, configures PCF and DTIM
 * handling, programs the sleep registers so the hardware
 * will wake up in time to receive beacons, and configures
 * the beacon miss handling so we'll receive a BMISS
 * interrupt when we stop seeing beacons from the AP
 * we've associated with.
 */
static void
ath_beacon_config(struct ath_softc *sc, struct ieee80211vap *vap)
{
#define	TSF_TO_TU(_h,_l) \
	((((u_int32_t)(_h)) << 22) | (((u_int32_t)(_l)) >> 10))
	struct ieee80211com *ic = &sc->sc_ic;
	struct ath_hal *ah = sc->sc_ah;
	struct ieee80211_node *ni;
	u_int32_t nexttbtt, intval;

	if (vap == NULL)
		vap = TAILQ_FIRST(&ic->ic_vaps);   /* XXX */

	ni = vap->iv_bss;

	/* extract tstamp from last beacon and convert to TU */
	nexttbtt = TSF_TO_TU(LE_READ_4(ni->ni_tstamp.data + 4),
			     LE_READ_4(ni->ni_tstamp.data));
	/* XXX conditionalize multi-bss support? */
	if (ic->ic_opmode == IEEE80211_M_HOSTAP) {
		/*
		 * For multi-bss ap support beacons are either staggered
		 * evenly over N slots or burst together.  For the former
		 * arrange for the SWBA to be delivered for each slot.
		 * Slots that are not occupied will generate nothing. 
		 */
		/* NB: the beacon interval is kept internally in TU's */
		intval = ic->ic_lintval & HAL_BEACON_PERIOD;
		if (sc->sc_stagbeacons)
			intval /= ath_maxvaps;	/* for staggered beacons */
		if ((sc->sc_nostabeacons) &&
		    (vap->iv_opmode == IEEE80211_M_HOSTAP))
			nexttbtt = 0;
	} else
		intval = ni->ni_intval & HAL_BEACON_PERIOD;
	if (nexttbtt == 0)		/* e.g. for ap mode */
		nexttbtt = intval;
	else if (intval)		/* NB: can be 0 for monitor mode */
		nexttbtt = roundup(nexttbtt, intval);
	DPRINTF(sc, ATH_DEBUG_BEACON, "%s: nexttbtt %u intval %u (%u)\n",
		__func__, nexttbtt, intval, ni->ni_intval);
	if (ic->ic_opmode == IEEE80211_M_STA &&	!(sc->sc_nostabeacons)) {
		HAL_BEACON_STATE bs;
		u_int64_t tsf;
		u_int32_t tsftu;
		int dtimperiod, dtimcount;
		int cfpperiod, cfpcount;

		/*
		 * Setup dtim and cfp parameters according to
		 * last beacon we received (which may be none).
		 */
		dtimperiod = vap->iv_dtim_period;
		if (dtimperiod <= 0)		/* NB: 0 if not known */
			dtimperiod = 1;
		dtimcount = vap->iv_dtim_count;
		if (dtimcount >= dtimperiod)	/* NB: sanity check */
			dtimcount = 0;		/* XXX? */
		cfpperiod = 1;			/* NB: no PCF support yet */
		cfpcount = 0;
#define	FUDGE	2
		/*
		 * Pull nexttbtt forward to reflect the current
		 * TSF and calculate dtim+cfp state for the result.
		 */
		tsf = ath_hal_gettsf64(ah);
		tsftu = TSF_TO_TU(tsf>>32, tsf) + FUDGE;
		do {
			nexttbtt += intval;
			if (--dtimcount < 0) {
				dtimcount = dtimperiod - 1;
				if (--cfpcount < 0)
					cfpcount = cfpperiod - 1;
			}
		} while (nexttbtt < tsftu);
#undef FUDGE
		memset(&bs, 0, sizeof(bs));
		bs.bs_intval = intval;
		bs.bs_nexttbtt = nexttbtt;
		bs.bs_dtimperiod = dtimperiod * intval;
		bs.bs_nextdtim = bs.bs_nexttbtt + dtimcount * intval;
		bs.bs_cfpperiod = cfpperiod * bs.bs_dtimperiod;
		bs.bs_cfpnext = bs.bs_nextdtim + cfpcount * bs.bs_dtimperiod;
		bs.bs_cfpmaxduration = 0;
#if 0
		/*
		 * The 802.11 layer records the offset to the DTIM
		 * bitmap while receiving beacons; use it here to
		 * enable h/w detection of our AID being marked in
		 * the bitmap vector (to indicate frames for us are
		 * pending at the AP).
		 * XXX do DTIM handling in s/w to WAR old h/w bugs
		 * XXX enable based on h/w rev for newer chips
		 */
		bs.bs_timoffset = ni->ni_timoff;
#endif
		/*
		 * Calculate the number of consecutive beacons to miss
		 * before taking a BMISS interrupt.  The configuration
		 * is specified in TU so we only need calculate based
		 * on the beacon interval.  Note that we clamp the
		 * result to at most 10 beacons.
		 */
		bs.bs_bmissthreshold = howmany(ic->ic_bmisstimeout, intval);
		if (bs.bs_bmissthreshold > 10)
			bs.bs_bmissthreshold = 10;
		else if (bs.bs_bmissthreshold < 2)
			bs.bs_bmissthreshold = 2;

		/*
		 * Calculate sleep duration.  The configuration is
		 * given in ms.  We ensure a multiple of the beacon
		 * period is used.  Also, if the sleep duration is
		 * greater than the DTIM period then it makes senses
		 * to make it a multiple of that.
		 *
		 * XXX fixed at 100ms
		 */
		bs.bs_sleepduration =
			roundup(IEEE80211_MS_TO_TU(100), bs.bs_intval);
		if (bs.bs_sleepduration > bs.bs_dtimperiod)
			bs.bs_sleepduration = roundup(bs.bs_sleepduration, bs.bs_dtimperiod);

		DPRINTF(sc, ATH_DEBUG_BEACON, 
			"%s: tsf %llu tsf:tu %u intval %u nexttbtt %u dtim %u nextdtim %u bmiss %u sleep %u cfp:period %u maxdur %u next %u timoffset %u\n"
			, __func__
			, (long long) tsf, tsftu
			, bs.bs_intval
			, bs.bs_nexttbtt
			, bs.bs_dtimperiod
			, bs.bs_nextdtim
			, bs.bs_bmissthreshold
			, bs.bs_sleepduration
			, bs.bs_cfpperiod
			, bs.bs_cfpmaxduration
			, bs.bs_cfpnext
			, bs.bs_timoffset
		);

		ic->ic_bmiss_guard = jiffies +
			IEEE80211_TU_TO_JIFFIES(bs.bs_intval * bs.bs_bmissthreshold);

		ath_hal_intrset(ah, 0);
		ath_hal_beacontimers(ah, &bs);
		sc->sc_imask |= HAL_INT_BMISS;
		ath_hal_intrset(ah, sc->sc_imask);
	} else {
		ath_hal_intrset(ah, 0);
		if (nexttbtt == intval)
			intval |= HAL_BEACON_RESET_TSF;
		if (ic->ic_opmode == IEEE80211_M_IBSS) {
			/*
			 * In IBSS mode enable the beacon timers but only
			 * enable SWBA interrupts if we need to manually
			 * prepare beacon frames.  Otherwise we use a
			 * self-linked tx descriptor and let the hardware
			 * deal with things.
			 */
			intval |= HAL_BEACON_ENA;
			if (!sc->sc_hasveol)
				sc->sc_imask |= HAL_INT_SWBA;
			ath_beaconq_config(sc);
		} else if (ic->ic_opmode == IEEE80211_M_HOSTAP) {
			/*
			 * In AP mode we enable the beacon timers and
			 * SWBA interrupts to prepare beacon frames.
			 */
			intval |= HAL_BEACON_ENA;
			sc->sc_imask |= HAL_INT_SWBA;	/* beacon prepare */
			ath_beaconq_config(sc);
		}
#ifdef ATH_SUPERG_DYNTURBO
		ath_beacon_dturbo_config(vap, intval & 
				~(HAL_BEACON_RESET_TSF | HAL_BEACON_ENA));
#endif
		ath_hal_beaconinit(ah, nexttbtt, intval);
		sc->sc_bmisscount = 0;
		ath_hal_intrset(ah, sc->sc_imask);
		/*
		 * When using a self-linked beacon descriptor in
		 * ibss mode load it once here.
		 */
		if (ic->ic_opmode == IEEE80211_M_IBSS && sc->sc_hasveol)
			ath_beacon_start_adhoc(sc, vap);
	}
	sc->sc_syncbeacon = 0;
#undef TSF_TO_TU
}

static int
ath_descdma_setup(struct ath_softc *sc,
	struct ath_descdma *dd, ath_bufhead *head,
	const char *name, int nbuf, int ndesc)
{
#define	DS2PHYS(_dd, _ds) \
	((_dd)->dd_desc_paddr + ((caddr_t)(_ds) - (caddr_t)(_dd)->dd_desc))
	struct ath_desc *ds;
	struct ath_buf *bf;
	int i, bsize, error;

	DPRINTF(sc, ATH_DEBUG_RESET, "%s: %s DMA: %u buffers %u desc/buf\n",
		__func__, name, nbuf, ndesc);

	dd->dd_name = name;
	dd->dd_desc_len = sizeof(struct ath_desc) * nbuf * ndesc;

	/* allocate descriptors */
	dd->dd_desc = bus_alloc_consistent(sc->sc_bdev,
		dd->dd_desc_len, &dd->dd_desc_paddr);
	if (dd->dd_desc == NULL) {
		error = -ENOMEM;
		goto fail;
	}
	ds = dd->dd_desc;
	DPRINTF(sc, ATH_DEBUG_RESET, "%s: %s DMA map: %p (%lu) -> %llx (%lu)\n",
		__func__, dd->dd_name, ds, (u_long) dd->dd_desc_len,
		ito64(dd->dd_desc_paddr), /*XXX*/ (u_long) dd->dd_desc_len);

	/* allocate buffers */
	bsize = sizeof(struct ath_buf) * nbuf;
	bf = kmalloc(bsize, GFP_KERNEL);
	if (bf == NULL) {
		error = -ENOMEM;		/* XXX different code */
		goto fail2;
	}
	memset(bf, 0, bsize);
	dd->dd_bufptr = bf;

	STAILQ_INIT(head);
	for (i = 0; i < nbuf; i++, bf++, ds += ndesc) {
		bf->bf_desc = ds;
		bf->bf_daddr = DS2PHYS(dd, ds);
		STAILQ_INSERT_TAIL(head, bf, bf_list);
	}
	return 0;
fail2:
	bus_free_consistent(sc->sc_bdev, dd->dd_desc_len,
		dd->dd_desc, dd->dd_desc_paddr);
fail:
	memset(dd, 0, sizeof(*dd));
	return error;
#undef DS2PHYS
}

static void
ath_descdma_cleanup(struct ath_softc *sc,
	struct ath_descdma *dd, ath_bufhead *head, int dir)
{
	struct ath_buf *bf;
	struct ieee80211_node *ni;

	STAILQ_FOREACH(bf, head, bf_list) {
		if (bf->bf_skb != NULL) {
			/* XXX skb->len is not good enough for rxbuf */
			if (dd == &sc->sc_rxdma)
				bus_unmap_single(sc->sc_bdev,
					bf->bf_skbaddr, sc->sc_rxbufsize, dir);
			else
				bus_unmap_single(sc->sc_bdev,
					bf->bf_skbaddr, bf->bf_skb->len, dir);
			dev_kfree_skb(bf->bf_skb);
			bf->bf_skb = NULL;
		}
		ni = bf->bf_node;
		bf->bf_node = NULL;
		if (ni != NULL) {
			/*
			 * Reclaim node reference.
			 */
			ieee80211_free_node(ni);
		}
	}

	/* Free memory associated with descriptors */
	bus_free_consistent(sc->sc_bdev, dd->dd_desc_len,
		dd->dd_desc, dd->dd_desc_paddr);

	STAILQ_INIT(head);
	kfree(dd->dd_bufptr);
	memset(dd, 0, sizeof(*dd));
}

static int
ath_desc_alloc(struct ath_softc *sc)
{
	int error;

	error = ath_descdma_setup(sc, &sc->sc_rxdma, &sc->sc_rxbuf,
			"rx", ATH_RXBUF, 1);
	if (error != 0)
		return error;

	error = ath_descdma_setup(sc, &sc->sc_txdma, &sc->sc_txbuf,
			"tx", ATH_TXBUF, ATH_TXDESC);
	if (error != 0) {
		ath_descdma_cleanup(sc, &sc->sc_rxdma, &sc->sc_rxbuf,
			BUS_DMA_FROMDEVICE);
		return error;
	}

	/* XXX allocate beacon state together with VAP */
	error = ath_descdma_setup(sc, &sc->sc_bdma, &sc->sc_bbuf,
			"beacon", ath_maxvaps, 1);
	if (error != 0) {
		ath_descdma_cleanup(sc, &sc->sc_txdma, &sc->sc_txbuf,
			BUS_DMA_TODEVICE);
		ath_descdma_cleanup(sc, &sc->sc_rxdma, &sc->sc_rxbuf,
			BUS_DMA_FROMDEVICE);
		return error;
	}
	return 0;
}

static void
ath_desc_free(struct ath_softc *sc)
{
	if (sc->sc_bdma.dd_desc_len != 0)
		ath_descdma_cleanup(sc, &sc->sc_bdma, &sc->sc_bbuf,
			BUS_DMA_TODEVICE);
	if (sc->sc_txdma.dd_desc_len != 0)
		ath_descdma_cleanup(sc, &sc->sc_txdma, &sc->sc_txbuf,
			BUS_DMA_TODEVICE);
	if (sc->sc_rxdma.dd_desc_len != 0)
		ath_descdma_cleanup(sc, &sc->sc_rxdma, &sc->sc_rxbuf,
			BUS_DMA_FROMDEVICE);
}

static struct ieee80211_node *
ath_node_alloc(struct ieee80211_node_table *nt,struct ieee80211vap *vap)
{
	struct ath_softc *sc = nt->nt_ic->ic_dev->priv;
	const size_t space = sizeof(struct ath_node) + sc->sc_rc->arc_space;
	struct ath_node *an;

	an = kmalloc(space, GFP_ATOMIC);
	if (an == NULL)
		return NULL;
	memset(an, 0, space);
	an->an_decomp_index = INVALID_DECOMP_INDEX;
	an->an_avgrssi = ATH_RSSI_DUMMY_MARKER;
	an->an_halstats.ns_avgbrssi = ATH_RSSI_DUMMY_MARKER;
	an->an_halstats.ns_avgrssi = ATH_RSSI_DUMMY_MARKER;
	an->an_halstats.ns_avgtxrssi = ATH_RSSI_DUMMY_MARKER;
	/*
	 * ath_rate_node_init needs a VAP pointer in node
	 * to decide which mgt rate to use
	 */
	an->an_node.ni_vap = vap;
	sc->sc_rc->ops->node_init(sc, an);

	/* U-APSD init */
	STAILQ_INIT(&an->an_uapsd_q);
	an->an_uapsd_qdepth = 0;
	STAILQ_INIT(&an->an_uapsd_overflowq);
	an->an_uapsd_overflowqdepth = 0;
	ATH_NODE_UAPSD_LOCK_INIT(an);

	DPRINTF(sc, ATH_DEBUG_NODE, "%s: an %p\n", __func__, an);
	return &an->an_node;
}

static void
ath_node_cleanup(struct ieee80211_node *ni)
{
	struct ieee80211com *ic = ni->ni_ic;
	struct ath_softc *sc = ni->ni_ic->ic_dev->priv;
	struct ath_node *an = ATH_NODE(ni);
	struct ath_buf *bf;
	
	/*
	 * U-APSD cleanup
	 */
	ATH_NODE_UAPSD_LOCK_IRQ(an);
	if (ni->ni_flags & IEEE80211_NODE_UAPSD_TRIG) {
		ni->ni_flags &= ~IEEE80211_NODE_UAPSD_TRIG;
		ic->ic_uapsdmaxtriggers--;
		ni->ni_flags &= ~IEEE80211_NODE_UAPSD_SP;
	}
	ATH_NODE_UAPSD_UNLOCK_IRQ(an);
	while (an->an_uapsd_qdepth) {
		bf = STAILQ_FIRST(&an->an_uapsd_q);
		STAILQ_REMOVE_HEAD(&an->an_uapsd_q, bf_list);
		bf->bf_desc->ds_link = 0;

		dev_kfree_skb_any(bf->bf_skb);
		bf->bf_skb = NULL;
		bf->bf_node = NULL;
		ATH_TXBUF_LOCK_IRQ(sc);
		STAILQ_INSERT_TAIL(&sc->sc_txbuf, bf, bf_list);
		ATH_TXBUF_UNLOCK_IRQ(sc);
		ieee80211_free_node(ni);

		an->an_uapsd_qdepth--;
	}

	while (an->an_uapsd_overflowqdepth) {
		bf = STAILQ_FIRST(&an->an_uapsd_overflowq);
		STAILQ_REMOVE_HEAD(&an->an_uapsd_overflowq, bf_list);
		bf->bf_desc->ds_link = 0;

		dev_kfree_skb_any(bf->bf_skb);
		bf->bf_skb = NULL;
		bf->bf_node = NULL;
		ATH_TXBUF_LOCK_IRQ(sc);
		STAILQ_INSERT_TAIL(&sc->sc_txbuf, bf, bf_list);
		ATH_TXBUF_UNLOCK_IRQ(sc);
		ieee80211_free_node(ni);

		an->an_uapsd_overflowqdepth--;
	}

	ATH_NODE_UAPSD_LOCK_IRQ(an);
	sc->sc_node_cleanup(ni);
	ATH_NODE_UAPSD_UNLOCK_IRQ(an);
}

static void
ath_node_free(struct ieee80211_node *ni)
{
	struct ath_softc *sc = ni->ni_ic->ic_dev->priv;

	sc->sc_rc->ops->node_cleanup(sc, ATH_NODE(ni));
	sc->sc_node_free(ni);
#ifdef ATH_SUPERG_XR
	ath_grppoll_period_update(sc);
#endif
}

static u_int8_t
ath_node_getrssi(const struct ieee80211_node *ni)
{
#define	HAL_EP_RND(x, mul) \
	((((x)%(mul)) >= ((mul)/2)) ? ((x) + ((mul) - 1)) / (mul) : (x)/(mul))
	u_int32_t avgrssi = ATH_NODE_CONST(ni)->an_avgrssi;
	int32_t rssi;

	/*
	 * When only one frame is received there will be no state in
	 * avgrssi so fallback on the value recorded by the 802.11 layer.
	 */
	if (avgrssi != ATH_RSSI_DUMMY_MARKER)
		rssi = HAL_EP_RND(avgrssi, HAL_RSSI_EP_MULTIPLIER);
	else
		rssi = ni->ni_rssi;
	/* NB: theoretically we shouldn't need this, but be paranoid */
	return rssi < 0 ? 0 : rssi > 127 ? 127 : rssi;
#undef HAL_EP_RND
}


#ifdef ATH_SUPERG_XR
/*
 * Stops the txqs and moves data between XR and Normal queues.
 * Also adjusts the rate info in the descriptors.
 */

static u_int8_t
ath_node_move_data(const struct ieee80211_node *ni)
{
#ifdef NOT_YET
	struct ath_txq *txq = NULL; 
	struct ieee80211com *ic = ni->ni_ic;
	struct ath_softc *sc = ic->ic_dev->priv;
	struct ath_buf *bf, *prev, *bf_tmp, *bf_tmp1;
	struct ath_hal *ah = sc->sc_ah;
	struct sk_buff *skb = NULL;
	struct ath_desc *ds;
	HAL_STATUS status;
	int index;

	if (ni->ni_vap->iv_flags & IEEE80211_F_XR) {
		struct ath_txq tmp_q; 
		memset(&tmp_q, 0, sizeof(tmp_q));
		STAILQ_INIT(&tmp_q.axq_q);
		/*
		 * move data from Normal txqs to XR queue.
		 */
		printk("move data from NORMAL to XR\n");
		/*
		 * collect all the data towards the node
		 * in to the tmp_q.
		 */
		index = WME_AC_VO;
		while (index >= WME_AC_BE && txq != sc->sc_ac2q[index]) { 
			txq = sc->sc_ac2q[index]; 
			ATH_TXQ_LOCK(txq);
			ath_hal_stoptxdma(ah, txq->axq_qnum);
			bf = prev = STAILQ_FIRST(&txq->axq_q);
			/*
			 * skip all the buffers that are done
			 * until the first one that is in progress
			 */
			while (bf) {
#ifdef ATH_SUPERG_FF
				ds = &bf->bf_desc[bf->bf_numdesc - 1];
#else
				ds = bf->bf_desc;		/* NB: last descriptor */
#endif
				status = ath_hal_txprocdesc(ah, ds);
				if (status == HAL_EINPROGRESS)
					break; 
				prev = bf;
				bf = STAILQ_NEXT(bf,bf_list);
			}
			/* 
			 * save the pointer to the last buf that's
			 * done
			 */
			if (prev == bf)
				bf_tmp = NULL;  
			else
				bf_tmp=prev;
			while (bf) {
				if (ni == bf->bf_node) {
					if (prev == bf) {
						ATH_TXQ_REMOVE_HEAD(txq, bf_list);
						STAILQ_INSERT_TAIL(&tmp_q.axq_q, bf, bf_list);
						bf = STAILQ_FIRST(&txq->axq_q);
						prev = bf;
					} else {
						STAILQ_REMOVE_AFTER(&(txq->axq_q), prev, bf_list);
						txq->axq_depth--;
						STAILQ_INSERT_TAIL(&tmp_q.axq_q, bf, bf_list);
						bf = STAILQ_NEXT(prev, bf_list);
						/*
						 * after deleting the node
						 * link the descriptors
						 */
#ifdef ATH_SUPERG_FF
						ds = &prev->bf_desc[prev->bf_numdesc - 1];
#else
						ds = prev->bf_desc;	/* NB: last descriptor */
#endif
#ifdef AH_NEED_DESC_SWAP
						ds->ds_link = cpu_to_le32(bf->bf_daddr);
#else
						ds->ds_link = bf->bf_daddr;
#endif
					}
				} else {
					prev = bf;
					bf = STAILQ_NEXT(bf, bf_list);
				}
			}
			/*
			 * if the last buf was deleted.
			 * set the pointer to the last descriptor.
			 */
			bf = STAILQ_FIRST(&txq->axq_q);
			if (bf) {
				if (prev) {
					bf = STAILQ_NEXT(prev, bf_list);
					if (!bf) { /* prev is the last one on the list */
#ifdef ATH_SUPERG_FF
						ds = &prev->bf_desc[prev->bf_numdesc - 1];
#else
						ds = prev->bf_desc;	/* NB: last descriptor */
#endif
						status = ath_hal_txprocdesc(ah, ds);
						if (status == HAL_EINPROGRESS) 
							txq->axq_link = &ds->ds_link;
						else
							txq->axq_link = NULL;	
					}
				} 
			} else
				txq->axq_link = NULL;

			ATH_TXQ_UNLOCK(txq);
			/*
			 * restart the DMA from the first 
			 * buffer that was not DMA'd.
			 */
			if (bf_tmp)
				bf = STAILQ_NEXT(bf_tmp, bf_list);
			else
				bf = STAILQ_FIRST(&txq->axq_q);
			if (bf) {	
				ath_hal_puttxbuf(ah, txq->axq_qnum, bf->bf_daddr);
				ath_hal_txstart(ah, txq->axq_qnum);
			}
		}
		/* 
		 * queue them on to the XR txqueue. 
		 * can not directly put them on to the XR txq. since the
		 * skb data size may be greater than the XR fragmentation
		 * threshold size.
		 */
		bf  = STAILQ_FIRST(&tmp_q.axq_q);
		index = 0;
		while (bf) {
			skb = bf->bf_skb;
			bf->bf_skb = NULL;
			bf->bf_node = NULL;
			ATH_TXBUF_LOCK(sc);
			STAILQ_INSERT_TAIL(&sc->sc_txbuf, bf, bf_list);
			ATH_TXBUF_UNLOCK(sc);
			ath_hardstart(skb,sc->sc_dev);
			ATH_TXQ_REMOVE_HEAD(&tmp_q, bf_list);
			bf = STAILQ_FIRST(&tmp_q.axq_q);
			index++;
		}
		printk("moved %d buffers from NORMAL to XR\n", index);
	} else {
		struct ath_txq wme_tmp_qs[WME_AC_VO+1]; 
		struct ath_txq *wmeq = NULL, *prevq; 
		struct ieee80211_frame *wh;
		struct ath_desc *ds = NULL;
		int count = 0;

		/*
		 * move data from XR txq to Normal txqs.
		 */
		printk("move buffers from XR to NORMAL\n");
		memset(&wme_tmp_qs, 0, sizeof(wme_tmp_qs));
		for (index = 0; index <= WME_AC_VO; index++)
			STAILQ_INIT(&wme_tmp_qs[index].axq_q);
		txq = sc->sc_xrtxq; 
		ATH_TXQ_LOCK(txq);
		ath_hal_stoptxdma(ah, txq->axq_qnum);
		bf = prev = STAILQ_FIRST(&txq->axq_q);
		/*
		 * skip all the buffers that are done
		 * until the first one that is in progress
		 */
		while (bf) {
#ifdef ATH_SUPERG_FF
			ds = &bf->bf_desc[bf->bf_numdesc - 1];
#else
			ds = bf->bf_desc;		/* NB: last descriptor */
#endif
			status = ath_hal_txprocdesc(ah, ds);
			if (status == HAL_EINPROGRESS)
				break;
			prev= bf;
			bf = STAILQ_NEXT(bf,bf_list);
		}
		/* 
		 * save the pointer to the last buf that's
		 * done
		 */
		if (prev == bf)
			bf_tmp1 = NULL;  
		else
			bf_tmp1 = prev;
		/*
		 * collect all the data in to four temp SW queues.
		 */
		while (bf) {
			if (ni == bf->bf_node) {
				if (prev == bf) {
					STAILQ_REMOVE_HEAD(&txq->axq_q,bf_list);
					bf_tmp=bf;
					bf = STAILQ_FIRST(&txq->axq_q);
					prev = bf;
				} else {
					STAILQ_REMOVE_AFTER(&(txq->axq_q),prev,bf_list);
					bf_tmp=bf;
					bf = STAILQ_NEXT(prev,bf_list);
				}
				count++;
				skb = bf_tmp->bf_skb;
				wh = (struct ieee80211_frame *) skb->data;
				if (wh->i_fc[0] & IEEE80211_FC0_SUBTYPE_QOS) {
					/* XXX validate skb->priority, remove mask */
					wmeq = &wme_tmp_qs[skb->priority & 0x3];
				} else
					wmeq = &wme_tmp_qs[WME_AC_BE];
				STAILQ_INSERT_TAIL(&wmeq->axq_q, bf_tmp, bf_list);
				ds = bf_tmp->bf_desc;
				/* 
				 * link the descriptors
				 */
				if (wmeq->axq_link != NULL) {
#ifdef AH_NEED_DESC_SWAP
					*wmeq->axq_link = cpu_to_le32(bf_tmp->bf_daddr);
#else
					*wmeq->axq_link = bf_tmp->bf_daddr;
#endif
					DPRINTF(sc, ATH_DEBUG_XMIT, "%s: link[%u](%p)=%p (%p)\n",
							__func__,
							wmeq->axq_qnum, wmeq->axq_link,
							(caddr_t)bf_tmp->bf_daddr, bf_tmp->bf_desc);
				}
				wmeq->axq_link = &ds->ds_link;
				/* 
				 * update the rate information  
				 */
			} else {
				prev = bf;
				bf = STAILQ_NEXT(bf, bf_list);
			}
		}
		/*
		 * reset the axq_link pointer to the last descriptor.
		 */
		bf = STAILQ_FIRST(&txq->axq_q);
		if (bf) {
			if (prev) {
				bf = STAILQ_NEXT(prev, bf_list);
				if (!bf) { /* prev is the last one on the list */
#ifdef ATH_SUPERG_FF
					ds = &prev->bf_desc[prev->bf_numdesc - 1];
#else
					ds = prev->bf_desc;	/* NB: last descriptor */
#endif
					status = ath_hal_txprocdesc(ah, ds);
					if (status == HAL_EINPROGRESS) 
						txq->axq_link = &ds->ds_link;
					else
						txq->axq_link = NULL;
				} 
			} 
		} else {
			/*
			 * if the list is empty reset the pointer.
			 */
			txq->axq_link = NULL;
		}
		ATH_TXQ_UNLOCK(txq);
		/*
		 * restart the DMA from the first 
		 * buffer that was not DMA'd.
		 */
		if (bf_tmp1)
			bf = STAILQ_NEXT(bf_tmp1,bf_list);
		else
			bf = STAILQ_FIRST(&txq->axq_q);
		if (bf) {	
			ath_hal_puttxbuf(ah, txq->axq_qnum, bf->bf_daddr);
			ath_hal_txstart(ah, txq->axq_qnum);
		}

		/* 
		 * move (concant) the lists from the temp sw queues in to
		 * WME queues.
		 */
		index = WME_AC_VO;
		txq = NULL;
		while (index >= WME_AC_BE ) { 
			prevq = txq;
			txq = sc->sc_ac2q[index];
			if (txq != prevq) {
				ATH_TXQ_LOCK(txq);
				ath_hal_stoptxdma(ah, txq->axq_qnum);
			}
			
			wmeq = &wme_tmp_qs[index];
			bf = STAILQ_FIRST(&wmeq->axq_q);
			if (bf) {
				ATH_TXQ_MOVE_Q(wmeq,txq);
				if (txq->axq_link != NULL) {
#ifdef AH_NEED_DESC_SWAP
					*(txq->axq_link) = cpu_to_le32(bf->bf_daddr);
#else
					*(txq->axq_link) = bf->bf_daddr;
#endif
				} 
			}
			if (index == WME_AC_BE || txq != prevq) {
				/* 
				 * find the first buffer to be DMA'd.
				 */
				bf = STAILQ_FIRST(&txq->axq_q);
				while (bf) {
#ifdef ATH_SUPERG_FF
					ds = &bf->bf_desc[bf->bf_numdesc - 1];
#else
					ds = bf->bf_desc;	/* NB: last descriptor */
#endif
					status = ath_hal_txprocdesc(ah, ds);
					if (status == HAL_EINPROGRESS)
						break; 
					bf = STAILQ_NEXT(bf,bf_list);
				}
				if (bf) {
					ath_hal_puttxbuf(ah, txq->axq_qnum, bf->bf_daddr);
					ath_hal_txstart(ah, txq->axq_qnum);
				}
				ATH_TXQ_UNLOCK(txq);
			}
			index--;
		}
		printk("moved %d buffers from XR to NORMAL\n", count);
	}
#endif
	return 0;
}
#endif

static struct sk_buff *
ath_alloc_skb(u_int size, u_int align)
{
	struct sk_buff *skb;
	u_int off;

	skb = dev_alloc_skb(size + align - 1);
	if (skb != NULL) {
		off = ((unsigned long) skb->data) % align;
		if (off != 0)
			skb_reserve(skb, align - off);
	}
	return skb;
}

static int
ath_rxbuf_init(struct ath_softc *sc, struct ath_buf *bf)
{
	struct ath_hal *ah = sc->sc_ah;
	struct sk_buff *skb;
	struct ath_desc *ds;

	skb = bf->bf_skb;
	if (skb == NULL) {
 		if (sc->sc_nmonvaps > 0) {
 			u_int off;
			int extra = A_MAX(sizeof(struct ath_rx_radiotap_header), 
					  A_MAX(sizeof(wlan_ng_prism2_header), ATHDESC_HEADER_SIZE));
						
 			/*
 			 * Allocate buffer for monitor mode with space for the
			 * wlan-ng style physical layer header at the start.
 			 */
 			skb = dev_alloc_skb(sc->sc_rxbufsize + extra + sc->sc_cachelsz - 1);
 			if (skb == NULL) {
 				DPRINTF(sc, ATH_DEBUG_ANY,
					"%s: skbuff alloc of size %u failed\n",
					__func__,
					sc->sc_rxbufsize + extra + sc->sc_cachelsz - 1);
 				sc->sc_stats.ast_rx_nobuf++;
 				return -ENOMEM;
 			}
 			/*
			 * Reserve space for the Prism header.
 			 */
 			skb_reserve(skb, sizeof(wlan_ng_prism2_header));
			/*
 			 * Align to cache line.
			 */
 			off = ((unsigned long) skb->data) % sc->sc_cachelsz;
 			if (off != 0)
 				skb_reserve(skb, sc->sc_cachelsz - off);
		} else {
			/*
			 * Cache-line-align.  This is important (for the
			 * 5210 at least) as not doing so causes bogus data
			 * in rx'd frames.
			 */
			skb = ath_alloc_skb(sc->sc_rxbufsize, sc->sc_cachelsz);
			if (skb == NULL) {
				DPRINTF(sc, ATH_DEBUG_ANY,
					"%s: skbuff alloc of size %u failed\n",
					__func__, sc->sc_rxbufsize);
				sc->sc_stats.ast_rx_nobuf++;
				return -ENOMEM;
			}
		}
		skb->dev = sc->sc_dev;
		bf->bf_skb = skb;
		bf->bf_skbaddr = bus_map_single(sc->sc_bdev,
			skb->data, sc->sc_rxbufsize, BUS_DMA_FROMDEVICE);
	}

	/*
	 * Setup descriptors.  For receive we always terminate
	 * the descriptor list with a self-linked entry so we'll
	 * not get overrun under high load (as can happen with a
	 * 5212 when ANI processing enables PHY error frames).
	 *
	 * To ensure the last descriptor is self-linked we create
	 * each descriptor as self-linked and add it to the end.  As
	 * each additional descriptor is added the previous self-linked
	 * entry is ``fixed'' naturally.  This should be safe even
	 * if DMA is happening.  When processing RX interrupts we
	 * never remove/process the last, self-linked, entry on the
	 * descriptor list.  This ensures the hardware always has
	 * someplace to write a new frame.
	 */
	ds = bf->bf_desc;
	ds->ds_link = bf->bf_daddr;		/* link to self */
	ds->ds_data = bf->bf_skbaddr;
	ds->ds_vdata = (void *) skb->data;	/* virt addr of buffer */
	ath_hal_setuprxdesc(ah, ds
		, skb_tailroom(skb)		/* buffer size */
		, 0
	);
	if (sc->sc_rxlink != NULL)
		*sc->sc_rxlink = bf->bf_daddr;
	sc->sc_rxlink = &ds->ds_link;
	return 0;
}

/*
 * Extend 15-bit time stamp from rx descriptor to
 * a full 64-bit TSF using the current h/w TSF.
 */
static __inline u_int64_t
ath_extend_tsf(struct ath_hal *ah, u_int32_t rstamp)
{
	u_int64_t tsf;

	tsf = ath_hal_gettsf64(ah);
	if ((tsf & 0x7fff) < rstamp)
		tsf -= 0x8000;
	return ((tsf &~ 0x7fff) | rstamp);
}

/*
 * Add a prism2 header to a received frame and
 * dispatch it to capture tools like kismet.
 */
static void
ath_rx_capture(struct net_device *dev, struct ath_desc *ds, struct sk_buff *skb)
{
	struct ath_softc *sc = dev->priv;
	struct ieee80211com *ic = &sc->sc_ic;
	struct ieee80211_frame *wh = (struct ieee80211_frame *) skb->data;
	unsigned int headersize = ieee80211_anyhdrsize(wh);
	int padbytes = roundup(headersize, 4) - headersize;
	u_int64_t tsf;

	/* Pass up tsf clock in mactime
	 * Rx descriptor has the low 15 bits of the tsf at
	 * the time the frame was received.  Use the current
	 * tsf to extend this to 64 bits.
	 */
	tsf = ath_extend_tsf(sc->sc_ah, ds->ds_rxstat.rs_tstamp);

	KASSERT(ic->ic_flags & IEEE80211_F_DATAPAD,
		("data padding not enabled?"));

	if (padbytes > 0) {
		/* Remove hw pad bytes */
		struct sk_buff *skb1 = skb_copy(skb, GFP_ATOMIC);
		memmove(skb1->data + padbytes, skb1->data, headersize);
		skb_pull(skb1, padbytes);
		ieee80211_input_monitor(ic, skb1, ds, 0, tsf, sc);
		dev_kfree_skb(skb1);
	} else {
		ieee80211_input_monitor(ic, skb, ds, 0, tsf, sc);
	}
}


static void
ath_tx_capture(struct net_device *dev, struct ath_desc *ds, struct sk_buff *skb)
{
	struct ath_softc *sc = dev->priv;
	struct ieee80211com *ic = &sc->sc_ic;
	struct ieee80211_frame *wh;
	int extra = A_MAX(sizeof(struct ath_tx_radiotap_header), 
			  A_MAX(sizeof(wlan_ng_prism2_header), ATHDESC_HEADER_SIZE));
	u_int64_t tsf;
	u_int32_t tstamp;
	unsigned int headersize;
	int padbytes;
	
	/* Pass up tsf clock in mactime
	 * TX descriptor contains the transmit time in TU's,
	 * (bits 25-10 of the TSF).
	 */
	tsf = ath_hal_gettsf64(sc->sc_ah);
	tstamp = ds->ds_txstat.ts_tstamp << 10;
	
	if ((tsf & 0x3ffffff) < tstamp)
		tsf -= 0x4000000;
	tsf = ((tsf &~ 0x3ffffff) | tstamp);

	/*                                                                      
	 * release the owner of this skb since we're basically                  
	 * recycling it                                                         
	 */
	if (atomic_read(&skb->users) != 1) {
		struct sk_buff *skb2 = skb;
		skb = skb_copy(skb, GFP_ATOMIC);
		if (skb == NULL) {
			printk("%s:%d %s\n", __FILE__, __LINE__, __func__);
			dev_kfree_skb(skb2);
			return;
		}
		dev_kfree_skb(skb2);
	} else
		skb_orphan(skb);

	wh = (struct ieee80211_frame *) skb->data;
	headersize = ieee80211_anyhdrsize(wh);
	padbytes = roundup(headersize, 4) - headersize;
	if (padbytes > 0) {
		/* Unlike in rx_capture, we're freeing the skb at the end
		 * anyway, so we don't need to worry about using a copy */
		memmove(skb->data + padbytes, skb->data, headersize);
		skb_pull(skb, padbytes);
	}
	
	if (skb_headroom(skb) < extra &&
	    pskb_expand_head(skb, extra, 0, GFP_ATOMIC)) {
		printk("%s:%d %s\n", __FILE__, __LINE__, __func__);
		goto done;
	}
	ieee80211_input_monitor(ic, skb, ds, 1, tsf, sc);
 done:
	dev_kfree_skb(skb);
}

/*
 * Intercept management frames to collect beacon rssi data
 * and to do ibss merges.
 */
static void
ath_recv_mgmt(struct ieee80211_node *ni, struct sk_buff *skb,
	int subtype, int rssi, u_int32_t rstamp)
{
	struct ath_softc *sc = ni->ni_ic->ic_dev->priv;
	struct ieee80211vap *vap = ni->ni_vap;

	/*
	 * Call up first so subsequent work can use information
	 * potentially stored in the node (e.g. for ibss merge).
	 */
	sc->sc_recv_mgmt(ni, skb, subtype, rssi, rstamp);
	switch (subtype) {
	case IEEE80211_FC0_SUBTYPE_BEACON:
		/* update rssi statistics for use by the HAL */
		ATH_RSSI_LPF(ATH_NODE(ni)->an_halstats.ns_avgbrssi, rssi);
		if ((sc->sc_syncbeacon || (vap->iv_flags_ext & IEEE80211_FEXT_APPIE_UPDATE)) &&
		    ni == vap->iv_bss && vap->iv_state == IEEE80211_S_RUN) {
			/*
			 * Resync beacon timers using the tsf of the
			 * beacon frame we just received.
			 */
			vap->iv_flags_ext &= ~IEEE80211_FEXT_APPIE_UPDATE;
			ath_beacon_config(sc, vap);
		}
		/* fall thru... */
	case IEEE80211_FC0_SUBTYPE_PROBE_RESP:
		if (vap->iv_opmode == IEEE80211_M_IBSS &&
		    vap->iv_state == IEEE80211_S_RUN) {
			u_int64_t tsf = ath_extend_tsf(sc->sc_ah, rstamp);
			/*
			 * Handle ibss merge as needed; check the tsf on the
			 * frame before attempting the merge.  The 802.11 spec
			 * says the station should change it's bssid to match
			 * the oldest station with the same ssid, where oldest
			 * is determined by the tsf.  Note that hardware
			 * reconfiguration happens through callback to
			 * ath_newstate as the state machine will go from
			 * RUN -> RUN when this happens.
			 */
			/* jal: added: don't merge if we have a desired
			   BSSID */
			if (!(vap->iv_flags & IEEE80211_F_DESBSSID) &&
				le64_to_cpu(ni->ni_tstamp.tsf) >= tsf) {
				DPRINTF(sc, ATH_DEBUG_STATE,
					"ibss merge, rstamp %u tsf %llu "
					"tstamp %llu\n", rstamp, (long long) tsf,
					(long long) le64_to_cpu(ni->ni_tstamp.tsf));
				(void) ieee80211_ibss_merge(ni);
			}
		}
		break;
	}
}

static void
ath_setdefantenna(struct ath_softc *sc, u_int antenna)
{
	struct ath_hal *ah = sc->sc_ah;

	/* XXX block beacon interrupts */
	ath_hal_setdefantenna(ah, antenna);
	if (sc->sc_defant != antenna)
		sc->sc_stats.ast_ant_defswitch++;
	sc->sc_defant = antenna;
	sc->sc_rxotherant = 0;
}

static void
ath_rx_tasklet(TQUEUE_ARG data)
{
#define	PA2DESC(_sc, _pa) \
	((struct ath_desc *)((caddr_t)(_sc)->sc_rxdma.dd_desc + \
		((_pa) - (_sc)->sc_rxdma.dd_desc_paddr)))
	struct net_device *dev = (struct net_device *)data;
	struct ath_buf *bf;
	struct ath_softc *sc = dev->priv;
	struct ieee80211com *ic = &sc->sc_ic;
	struct ath_hal *ah = sc->sc_ah;
	struct ath_desc *ds;
	struct sk_buff *skb;
	struct ieee80211_node *ni;
	int len, type;
	u_int phyerr;

	/* Let the 802.11 layer know about the new noise floor */
	ic->ic_channoise = sc->sc_channoise;
	
	DPRINTF(sc, ATH_DEBUG_RX_PROC, "%s\n", __func__);
	do {
		bf = STAILQ_FIRST(&sc->sc_rxbuf);
		if (bf == NULL) {		/* XXX ??? can this happen */
			printk("%s: no buffer (%s)\n", dev->name, __func__);
			break;
		}

		/*
		 * Descriptors are now processed at in the first-level
		 * interrupt handler to support U-APSD trigger search.
		 * This must also be done even when U-APSD is not active to support
		 * other error handling that requires immediate attention.
		 * We check bf_status to find out if the bf's descriptors have 
		 * been processed by the HAL.
		 */
		if (!(bf->bf_status & ATH_BUFSTATUS_DONE))
			break;
		
		ds = bf->bf_desc;
		if (ds->ds_link == bf->bf_daddr) {
			/* NB: never process the self-linked entry at the end */
			break;
		}
		skb = bf->bf_skb;
		if (skb == NULL) {		/* XXX ??? can this happen */
			printk("%s: no skbuff (%s)\n", dev->name, __func__);
			continue;
		}

#ifdef AR_DEBUG
		if (sc->sc_debug & ATH_DEBUG_RECV_DESC)
			ath_printrxbuf(bf, 1);
#endif

		if (ds->ds_rxstat.rs_more) {
			/*
			 * Frame spans multiple descriptors; this
			 * cannot happen yet as we don't support
			 * jumbograms.  If not in monitor mode,
			 * discard the frame.
			 */
#ifndef ERROR_FRAMES
			/*
			 * Enable this if you want to see
			 * error frames in Monitor mode.
			 */
			if (ic->ic_opmode != IEEE80211_M_MONITOR) {
				sc->sc_stats.ast_rx_toobig++;
				goto rx_next;
			}
#endif
			/* fall thru for monitor mode handling... */
		} else if (ds->ds_rxstat.rs_status != 0) {
			if (ds->ds_rxstat.rs_status & HAL_RXERR_CRC)
				sc->sc_stats.ast_rx_crcerr++;
			if (ds->ds_rxstat.rs_status & HAL_RXERR_FIFO)
				sc->sc_stats.ast_rx_fifoerr++;
			if (ds->ds_rxstat.rs_status & HAL_RXERR_PHY) {
				sc->sc_stats.ast_rx_phyerr++;
				phyerr = ds->ds_rxstat.rs_phyerr & 0x1f;
				sc->sc_stats.ast_rx_phy[phyerr]++;
			}
			if (ds->ds_rxstat.rs_status & HAL_RXERR_DECRYPT) {
				/*
				 * Decrypt error.  If the error occurred
				 * because there was no hardware key, then
				 * let the frame through so the upper layers
				 * can process it.  This is necessary for 5210
				 * parts which have no way to setup a ``clear''
				 * key cache entry.
				 *
				 * XXX do key cache faulting
				 */
				if (ds->ds_rxstat.rs_keyix == HAL_RXKEYIX_INVALID)
					goto rx_accept;
				sc->sc_stats.ast_rx_badcrypt++;
			}
			if (ds->ds_rxstat.rs_status & HAL_RXERR_MIC) {
				sc->sc_stats.ast_rx_badmic++;
				/*
				 * Do minimal work required to hand off
				 * the 802.11 header for notification.
				 */
				/* XXX frag's and QoS frames */
				len = ds->ds_rxstat.rs_datalen;
				if (len >= sizeof (struct ieee80211_frame)) {
					bus_dma_sync_single(sc->sc_bdev,
					    bf->bf_skbaddr, len,
					    BUS_DMA_FROMDEVICE);
#if 0
/* XXX revalidate MIC, lookup ni to find VAP */
					ieee80211_notify_michael_failure(ic,
					    (struct ieee80211_frame *) skb->data,
					    sc->sc_splitmic ?
					        ds->ds_rxstat.rs_keyix - 32 :
					        ds->ds_rxstat.rs_keyix
					);
#endif
				}
			}
			/*
			 * Reject error frames if we have no vaps that 
			 * are operating in monitor mode.
			 */
			if(sc->sc_nmonvaps == 0) goto rx_next;
		}
rx_accept:
		/*
		 * Sync and unmap the frame.  At this point we're
		 * committed to passing the sk_buff somewhere so
		 * clear buf_skb; this means a new sk_buff must be
		 * allocated when the rx descriptor is setup again
		 * to receive another frame.
		 */
		len = ds->ds_rxstat.rs_datalen;
		bus_dma_sync_single(sc->sc_bdev,
			bf->bf_skbaddr, len, BUS_DMA_FROMDEVICE);
		bus_unmap_single(sc->sc_bdev, bf->bf_skbaddr,
			sc->sc_rxbufsize, BUS_DMA_FROMDEVICE);
		bf->bf_skb = NULL;

		sc->sc_stats.ast_ant_rx[ds->ds_rxstat.rs_antenna]++;
		sc->sc_devstats.rx_packets++;
		sc->sc_devstats.rx_bytes += len;

		skb_put(skb, len);
		skb->protocol = __constant_htons(ETH_P_CONTROL);

		if (sc->sc_nmonvaps > 0) {
			/* 
			 * Some vap is in monitor mode, so send to
			 * ath_rx_capture for monitor encapsulation
			 */
#if 0
			if (len < IEEE80211_ACK_LEN) {
				DPRINTF(sc, ATH_DEBUG_RECV,
					"%s: runt packet %d\n", __func__, len);
				sc->sc_stats.ast_rx_tooshort++;
				dev_kfree_skb(skb);
				skb = NULL;
				goto rx_next;
			}
#endif
			ath_rx_capture(dev, ds, skb);
			if (sc->sc_ic.ic_opmode == IEEE80211_M_MONITOR) {
				/* no other VAPs need the packet */
				dev_kfree_skb(skb);
				skb = NULL;
				goto rx_next;
			}
		}

		/*
		 * Finished monitor mode handling, now reject
		 * error frames before passing to other vaps
		 */
		if (ds->ds_rxstat.rs_status != 0) {
			dev_kfree_skb(skb);
			skb = NULL;
			goto rx_next;
		}
		
		/* remove the CRC */
		skb_trim(skb, skb->len - IEEE80211_CRC_LEN);

		/*
		 * From this point on we assume the frame is at least
		 * as large as ieee80211_frame_min; verify that.
		 */
		if (len < IEEE80211_MIN_LEN) {
			DPRINTF(sc, ATH_DEBUG_RECV, "%s: short packet %d\n",
				__func__, len);
			sc->sc_stats.ast_rx_tooshort++;
			dev_kfree_skb(skb);
			skb = NULL;
			goto rx_next;
		}

		/*
		 * Normal receive.
		 */

		if (IFF_DUMPPKTS(sc, ATH_DEBUG_RECV)) {
			ieee80211_dump_pkt(ic, skb->data, skb->len,
				   sc->sc_hwmap[ds->ds_rxstat.rs_rate].ieeerate,
				   ds->ds_rxstat.rs_rssi);
		}

		/*
		 * Locate the node for sender, track state, and then
		 * pass the (referenced) node up to the 802.11 layer
		 * for its use.  If the sender is unknown spam the
		 * frame; it'll be dropped where it's not wanted.
		 */
		if (ds->ds_rxstat.rs_keyix != HAL_RXKEYIX_INVALID &&
		    (ni = sc->sc_keyixmap[ds->ds_rxstat.rs_keyix]) != NULL) {
			struct ath_node *an;
			/*
			 * Fast path: node is present in the key map;
			 * grab a reference for processing the frame.
			 */
			an = ATH_NODE(ieee80211_ref_node(ni));
			ATH_RSSI_LPF(an->an_avgrssi, ds->ds_rxstat.rs_rssi);
			type = ieee80211_input(ni, skb,
				ds->ds_rxstat.rs_rssi, ds->ds_rxstat.rs_tstamp);
			ieee80211_free_node(ni);
		} else {
			/*
			 * No key index or no entry, do a lookup and
			 * add the node to the mapping table if possible.
			 */
			ni = ieee80211_find_rxnode(ic, 
				(const struct ieee80211_frame_min *) skb->data);
			if (ni != NULL) {
				struct ath_node *an = ATH_NODE(ni);
				u_int16_t keyix;

				ATH_RSSI_LPF(an->an_avgrssi,
					ds->ds_rxstat.rs_rssi);
				type = ieee80211_input(ni, skb,
					ds->ds_rxstat.rs_rssi,
					ds->ds_rxstat.rs_tstamp);
				/*
				 * If the station has a key cache slot assigned
				 * update the key->node mapping table.
				 */
				keyix = ni->ni_ucastkey.wk_keyix;
				if (keyix != IEEE80211_KEYIX_NONE &&
				    sc->sc_keyixmap[keyix] == NULL)
					sc->sc_keyixmap[keyix] = ieee80211_ref_node(ni);
				ieee80211_free_node(ni); 
			} else
				type = ieee80211_input_all(ic, skb,
					ds->ds_rxstat.rs_rssi,
					ds->ds_rxstat.rs_tstamp);
		}

		if (sc->sc_diversity) {
			/*
			 * When using hardware fast diversity, change the default rx
			 * antenna if rx diversity chooses the other antenna 3
			 * times in a row.
			 */
			if (sc->sc_defant != ds->ds_rxstat.rs_antenna) {
				if (++sc->sc_rxotherant >= 3)
					ath_setdefantenna(sc, ds->ds_rxstat.rs_antenna);
			} else
				sc->sc_rxotherant = 0;
		}
		if (sc->sc_softled) {
			/*
			 * Blink for any data frame.  Otherwise do a
			 * heartbeat-style blink when idle.  The latter
			 * is mainly for station mode where we depend on
			 * periodic beacon frames to trigger the poll event.
			 */
			if (type == IEEE80211_FC0_TYPE_DATA) {
				sc->sc_rxrate = ds->ds_rxstat.rs_rate;
				ath_led_event(sc, ATH_LED_RX);
			} else if (jiffies - sc->sc_ledevent >= sc->sc_ledidle)
				ath_led_event(sc, ATH_LED_POLL);
		}
rx_next:
		ATH_RXBUF_LOCK_IRQ(sc);
		STAILQ_REMOVE_HEAD(&sc->sc_rxbuf, bf_list);
		bf->bf_status &= ~ATH_BUFSTATUS_DONE;
		STAILQ_INSERT_TAIL(&sc->sc_rxbuf, bf, bf_list);
		ATH_RXBUF_UNLOCK_IRQ(sc);
	} while (ath_rxbuf_init(sc, bf) == 0);
	
	/* rx signal state monitoring */
	ath_hal_rxmonitor(ah, &sc->sc_halstats, &sc->sc_curchan);
	if (ath_hal_radar_event(ah)) {
		sc->sc_rtasksched = 1;
		schedule_work(&sc->sc_radartask);
	}
#undef PA2DESC
}

#ifdef ATH_SUPERG_XR

static void 
ath_grppoll_period_update(struct ath_softc *sc)
{
	struct ieee80211com *ic = &sc->sc_ic;
	u_int16_t interval;
	u_int16_t xrsta;
	u_int16_t normalsta;
	u_int16_t allsta;

	xrsta = ic->ic_xr_sta_assoc;

	/*
	 * if no stations are in XR mode.
	 * use default poll interval.
	 */
	if (xrsta == 0) { 
		if (sc->sc_xrpollint != XR_DEFAULT_POLL_INTERVAL) {
			sc->sc_xrpollint = XR_DEFAULT_POLL_INTERVAL;
			ath_grppoll_txq_update(sc,XR_DEFAULT_POLL_INTERVAL);
		}
		return;
	}

	allsta = ic->ic_sta_assoc;
	/*
	 * if all the stations are in XR mode.
	 * use minimum poll interval.
	 */
	if (allsta == xrsta) { 
		if (sc->sc_xrpollint != XR_MIN_POLL_INTERVAL) {
			sc->sc_xrpollint = XR_MIN_POLL_INTERVAL;
			ath_grppoll_txq_update(sc,XR_MIN_POLL_INTERVAL);
		}
		return;
	}

	normalsta = allsta-xrsta;
	/*
	 * if stations are in both XR and normal mode. 
	 * use some fudge factor.
	 */
	interval = XR_DEFAULT_POLL_INTERVAL -
          ((XR_DEFAULT_POLL_INTERVAL - XR_MIN_POLL_INTERVAL) * xrsta)/(normalsta * XR_GRPPOLL_PERIOD_FACTOR);
	if (interval < XR_MIN_POLL_INTERVAL)
		interval = XR_MIN_POLL_INTERVAL;
	
	if (sc->sc_xrpollint != interval) {
		sc->sc_xrpollint = interval;
		ath_grppoll_txq_update(sc,interval);
	}

	/*
	 * XXX: what if stations go to sleep?
	 * ideally the interval should be adjusted dynamically based on
	 * xr and normal upstream traffic.
	 */
}

/*
 * update grppoll period.
 */
static void 
ath_grppoll_txq_update(struct ath_softc *sc, int period)
{
	struct ath_hal *ah = sc->sc_ah;
	HAL_TXQ_INFO qi;
	struct ath_txq *txq = &sc->sc_grpplq;

	if (sc->sc_grpplq.axq_qnum == -1)
		return; 

	memset(&qi, 0, sizeof(qi));
	qi.tqi_subtype = 0;
	qi.tqi_aifs = XR_AIFS;
	qi.tqi_cwmin = XR_CWMIN_CWMAX;
	qi.tqi_cwmax = XR_CWMIN_CWMAX;
	qi.tqi_compBuf = 0;
	qi.tqi_cbrPeriod = IEEE80211_TU_TO_MS(period) * 1000; /* usec */
	qi.tqi_cbrOverflowLimit = 2;
	ath_hal_settxqueueprops(ah, txq->axq_qnum,&qi);
	ath_hal_resettxqueue(ah, txq->axq_qnum); /* push to h/w */
}

/*
 * Setup grppoll  h/w transmit queue.
 */
static void 
ath_grppoll_txq_setup(struct ath_softc *sc, int qtype, int period)
{
#define	N(a)	((int)(sizeof(a)/sizeof(a[0])))
	struct ath_hal *ah = sc->sc_ah;
	HAL_TXQ_INFO qi;
	int qnum;
	u_int compbufsz = 0;
	char *compbuf = NULL;
	dma_addr_t compbufp = 0;
	struct ath_txq *txq = &sc->sc_grpplq;

	memset(&qi, 0, sizeof(qi));
	qi.tqi_subtype = 0;
	qi.tqi_aifs = XR_AIFS;
	qi.tqi_cwmin = XR_CWMIN_CWMAX;
	qi.tqi_cwmax = XR_CWMIN_CWMAX;
	qi.tqi_compBuf = 0;
	qi.tqi_cbrPeriod = IEEE80211_TU_TO_MS(period) * 1000; /* usec */
	qi.tqi_cbrOverflowLimit = 2;

	if (sc->sc_grpplq.axq_qnum == -1) {
		qnum = ath_hal_setuptxqueue(ah, qtype, &qi);
		if (qnum == -1)
			return ;
		if (qnum >= N(sc->sc_txq)) {
			printk("%s: HAL qnum %u out of range, max %u!\n",
				   sc->sc_dev->name, qnum, N(sc->sc_txq));
			ath_hal_releasetxqueue(ah, qnum);
			return;
		}

		txq->axq_qnum = qnum;
	}
	txq->axq_link = NULL;
	STAILQ_INIT(&txq->axq_q);
	ATH_TXQ_LOCK_INIT(txq);
	txq->axq_depth = 0;
	txq->axq_totalqueued = 0;
	txq->axq_intrcnt = 0;
	TAILQ_INIT(&txq->axq_stageq);
	txq->axq_compbuf = compbuf;
	txq->axq_compbufsz = compbufsz;
	txq->axq_compbufp = compbufp;
	ath_hal_resettxqueue(ah, txq->axq_qnum); /* push to h/w */
#undef N

}

/*
 * Setup group poll frames on the group poll queue.
 */
static void ath_grppoll_start(struct ieee80211vap *vap,int pollcount)
{
	int i, amode;
	int flags;
	struct sk_buff *skb = NULL;
	struct ath_buf *bf, *head = NULL;
	struct ieee80211com *ic = vap->iv_ic;
	struct ath_softc *sc = ic->ic_dev->priv;
	struct ath_hal *ah = sc->sc_ah;
	u_int8_t rate;
	int ctsrate = 0;
	int ctsduration = 0;
	const HAL_RATE_TABLE *rt;
	u_int8_t cix, rtindex = 0;
	u_int type;
	struct ath_txq *txq = &sc->sc_grpplq;
	struct ath_desc *ds = NULL;
	int pktlen = 0, keyix = 0;
	int pollsperrate, pos;
	int rates[XR_NUM_RATES];
	u_int8_t ratestr[16], numpollstr[16];
	typedef struct rate_to_str_map {
		u_int8_t str[4];
		int ratekbps;
	} RATE_TO_STR_MAP;

	static const RATE_TO_STR_MAP ratestrmap[] = {
		{"0.25",    250},
		{ ".25",    250},
		{"0.5",     500},
		{ ".5",     500},
		{  "1",    1000},
		{  "3",    3000},
		{  "6",    6000},
		{  "?",       0},
	};

#define MAX_GRPPOLL_RATE 5
#define	USE_SHPREAMBLE(_ic) \
	(((_ic)->ic_flags & (IEEE80211_F_SHPREAMBLE | IEEE80211_F_USEBARKER)) \
		== IEEE80211_F_SHPREAMBLE)

	if (sc->sc_xrgrppoll)
		return; 

	memset(&rates, 0, sizeof(rates));
	pos = 0;
	while (sscanf(&(sc->sc_grppoll_str[pos]), "%s %s", ratestr, numpollstr) == 2) {
		int rtx = 0;
		while (ratestrmap[rtx].ratekbps != 0) {
			if (strcmp(ratestrmap[rtx].str, ratestr) == 0)
				break;
			rtx++;
		}
		sscanf(numpollstr, "%d", &(rates[rtx]));
		pos += strlen(ratestr) + strlen(numpollstr) + 2;
	}
	if (!sc->sc_grppolldma.dd_bufptr) {
		printk("grppoll_start: grppoll Buf allocation failed\n");
		return;
	}
	rt = sc->sc_currates;
	cix = rt->info[sc->sc_protrix].controlRate;
	ctsrate = rt->info[cix].rateCode;
	if (USE_SHPREAMBLE(ic))
			ctsrate |= rt->info[cix].shortPreamble;
	rt = sc->sc_xr_rates;
	/*
	 * queue the group polls for each antenna mode. set the right keycache index for the
	 * broadcast packets. this will ensure that if the first poll
	 * does not elicit a single chirp from any XR station, hardware will
	 * not send the subsequent polls
	 */
	pollsperrate = 0;
	for (amode = HAL_ANTENNA_FIXED_A; amode < HAL_ANTENNA_MAX_MODE ; amode++) {
		for (i = 0; i < (pollcount + 1); i++) {

			flags = HAL_TXDESC_NOACK;
			rate = rt->info[rtindex].rateCode;
			/* 
			 * except for the last one every thing else is a CF poll.
			 * last one is  the CF End frame.
			 */

			if (i == pollcount) {
				skb = ieee80211_getcfframe(vap,IEEE80211_FC0_SUBTYPE_CF_END);
				rate = ctsrate;
				ctsduration = ath_hal_computetxtime(ah,
					sc->sc_currates, pktlen, sc->sc_protrix, AH_FALSE);
			} else {
				skb = ieee80211_getcfframe(vap, IEEE80211_FC0_SUBTYPE_CFPOLL);
				pktlen = skb->len + IEEE80211_CRC_LEN;
				/*
				 * the very first group poll ctsduration  should be enough to allow
				 * an auth frame from station. This is to pass the wifi testing (as 
				 * some stations in testing do not honor CF_END and rely on CTS duration)
				 */
				if (i == 0 && amode == HAL_ANTENNA_FIXED_A) {
					ctsduration = ath_hal_computetxtime(ah,	rt,
							pktlen,	rtindex,
							AH_FALSE) /*cf-poll time */
						+ (XR_AIFS + (XR_CWMIN_CWMAX * XR_SLOT_DELAY))  
						+ ath_hal_computetxtime(ah, rt,
							2 * (sizeof(struct ieee80211_frame_min) + 6),
							IEEE80211_XR_DEFAULT_RATE_INDEX,
							AH_FALSE) /*auth packet time */
						+ ath_hal_computetxtime(ah, rt,
							IEEE80211_ACK_LEN,
							IEEE80211_XR_DEFAULT_RATE_INDEX,
							AH_FALSE); /*ack frame time */ 
				} else {
					ctsduration = ath_hal_computetxtime(ah, rt,
							pktlen, rtindex,
							AH_FALSE) /*cf-poll time */
						+ (XR_AIFS + (XR_CWMIN_CWMAX * XR_SLOT_DELAY))  
						+ ath_hal_computetxtime(ah,rt,
							XR_FRAGMENTATION_THRESHOLD,
							IEEE80211_XR_DEFAULT_RATE_INDEX,
							AH_FALSE) /*data packet time */
						+ ath_hal_computetxtime(ah,rt,
							IEEE80211_ACK_LEN,
							IEEE80211_XR_DEFAULT_RATE_INDEX,
							AH_FALSE); /*ack frame time */ 
				}
				if ((vap->iv_flags & IEEE80211_F_PRIVACY) && keyix == 0) {
					struct ieee80211_key *k;
					k = ieee80211_crypto_encap(vap->iv_bss, skb);
					if (k)
						keyix = k->wk_keyix;
				}
			}
			ATH_TXBUF_LOCK_IRQ(sc);					
			bf = STAILQ_FIRST(&sc->sc_grppollbuf);
			if (bf != NULL)
				STAILQ_REMOVE_HEAD(&sc->sc_grppollbuf, bf_list);
			else {
				DPRINTF(sc, ATH_DEBUG_XMIT, "%s: No more TxBufs\n", __func__);
				ATH_TXBUF_UNLOCK_IRQ_EARLY(sc);
				return;
			}
			/* XXX use a counter and leave at least one for mgmt frames */
			if (STAILQ_EMPTY(&sc->sc_grppollbuf)) {				
				DPRINTF(sc, ATH_DEBUG_XMIT, "%s: No more TxBufs left\n", __func__);
				ATH_TXBUF_UNLOCK_IRQ_EARLY(sc);
				return;
			}					
			ATH_TXBUF_UNLOCK_IRQ(sc);
			bf->bf_skbaddr = bus_map_single(sc->sc_bdev,
				skb->data, skb->len, BUS_DMA_TODEVICE);
			bf->bf_skb = skb;
			ATH_TXQ_INSERT_TAIL(txq, bf, bf_list);
			ds = bf->bf_desc;
			ds->ds_data = bf->bf_skbaddr;
			if (i == pollcount && amode == (HAL_ANTENNA_MAX_MODE -1)) {
				type = HAL_PKT_TYPE_NORMAL;
				flags |= (HAL_TXDESC_CLRDMASK | HAL_TXDESC_VEOL);
			} else {
				flags |= HAL_TXDESC_CTSENA;
				type = HAL_PKT_TYPE_GRP_POLL;
			}
			if (i == 0 && amode == HAL_ANTENNA_FIXED_A ) {
				flags |= HAL_TXDESC_CLRDMASK;  
				head = bf;
			}
			ath_hal_setuptxdesc(ah, ds
				, skb->len + IEEE80211_CRC_LEN	/* frame length */
				, sizeof(struct ieee80211_frame)	/* header length */
				, type			/* Atheros packet type */
				, ic->ic_txpowlimit	/* max txpower */
				, rate, 0		/* series 0 rate/tries */
				, keyix /* HAL_TXKEYIX_INVALID */		/* use key index */
				, amode			/* antenna mode */
				, flags				
				, ctsrate		/* rts/cts rate */
				, ctsduration		/* rts/cts duration */
				, 0			/* comp icv len */
				, 0			/* comp iv len */
				, ATH_COMP_PROC_NO_COMP_NO_CCS	/* comp scheme */
				);
			ath_hal_filltxdesc(ah, ds
				, roundup(skb->len, 4)	/* buffer length */
				, AH_TRUE		/* first segment */
				, AH_TRUE		/* last segment */
				, ds			/* first descriptor */
				);
			/* NB: The desc swap function becomes void, 
	 		* if descriptor swapping is not enabled
	 		*/
			ath_desc_swap(ds);
			if (txq->axq_link) {
#ifdef AH_NEED_DESC_SWAP
				*txq->axq_link = cpu_to_le32(bf->bf_daddr);
#else
				*txq->axq_link = bf->bf_daddr;
#endif
			}
			txq->axq_link = &ds->ds_link;
			pollsperrate++;
			if (pollsperrate > rates[rtindex]) {
				rtindex = (rtindex + 1) % MAX_GRPPOLL_RATE;
				pollsperrate = 0;
			}
		}
	}
	/* make it circular */
#ifdef AH_NEED_DESC_SWAP
	ds->ds_link = cpu_to_le32(head->bf_daddr);
#else
	ds->ds_link = head->bf_daddr;
#endif
	/* start the queue */
	ath_hal_puttxbuf(ah, txq->axq_qnum, head->bf_daddr);
	ath_hal_txstart(ah, txq->axq_qnum);
	sc->sc_xrgrppoll = 1;
#undef USE_SHPREAMBLE
}

static void ath_grppoll_stop(struct ieee80211vap *vap)
{
	struct ieee80211com *ic = vap->iv_ic;
	struct ath_softc *sc = ic->ic_dev->priv;
	struct ath_hal *ah = sc->sc_ah;
	struct ath_txq *txq = &sc->sc_grpplq;
	struct ath_buf *bf;
	
	
	if (!sc->sc_xrgrppoll)
		return; 
	ath_hal_stoptxdma(ah, txq->axq_qnum);

	/* move the grppool bufs back to the grppollbuf */
	for (;;) {
		ATH_TXQ_LOCK(txq);
		bf = STAILQ_FIRST(&txq->axq_q);
		if (bf == NULL) {
			txq->axq_link = NULL;
			ATH_TXQ_UNLOCK(txq);
			break;
		}
		ATH_TXQ_REMOVE_HEAD(txq, bf_list);
		ATH_TXQ_UNLOCK(txq);
		bus_unmap_single(sc->sc_bdev,
			bf->bf_skbaddr, bf->bf_skb->len, BUS_DMA_TODEVICE);
		dev_kfree_skb(bf->bf_skb);
		bf->bf_skb = NULL;
		bf->bf_node = NULL;

		ATH_TXBUF_LOCK(sc);
		STAILQ_INSERT_TAIL(&sc->sc_grppollbuf, bf, bf_list);
		ATH_TXBUF_UNLOCK(sc);
	}
	STAILQ_INIT(&txq->axq_q);
	ATH_TXQ_LOCK_INIT(txq);
	txq->axq_depth = 0;
	txq->axq_totalqueued = 0;
	txq->axq_intrcnt = 0;
	TAILQ_INIT(&txq->axq_stageq);
	sc->sc_xrgrppoll = 0;
}
#endif

/*
 * Setup a h/w transmit queue.
 */
static struct ath_txq *
ath_txq_setup(struct ath_softc *sc, int qtype, int subtype)
{
#define	N(a)	((int)(sizeof(a)/sizeof(a[0])))
	struct ath_hal *ah = sc->sc_ah;
	HAL_TXQ_INFO qi;
	int qnum;
	u_int compbufsz = 0;
	char *compbuf = NULL;
	dma_addr_t compbufp = 0;

	memset(&qi, 0, sizeof(qi));
	qi.tqi_subtype = subtype;
	qi.tqi_aifs = HAL_TXQ_USEDEFAULT;
	qi.tqi_cwmin = HAL_TXQ_USEDEFAULT;
	qi.tqi_cwmax = HAL_TXQ_USEDEFAULT;
	qi.tqi_compBuf = 0;
#ifdef ATH_SUPERG_XR
	if (subtype == HAL_XR_DATA) {
		qi.tqi_aifs  = XR_DATA_AIFS;
		qi.tqi_cwmin = XR_DATA_CWMIN;
		qi.tqi_cwmax = XR_DATA_CWMAX;
	}
#endif

#ifdef ATH_SUPERG_COMP
	/* allocate compression scratch buffer for data queues */
	if (((qtype == HAL_TX_QUEUE_DATA)|| (qtype == HAL_TX_QUEUE_UAPSD)) 
	    && ath_hal_compressionsupported(ah)) {
		compbufsz = roundup(HAL_COMP_BUF_MAX_SIZE, 
			HAL_COMP_BUF_ALIGN_SIZE) + HAL_COMP_BUF_ALIGN_SIZE;
		compbuf = (char *)bus_alloc_consistent(sc->sc_bdev,
			compbufsz, &compbufp);
		if (compbuf == NULL)
			sc->sc_ic.ic_ath_cap &= ~IEEE80211_ATHC_COMP;	
		else
			qi.tqi_compBuf = (u_int32_t)compbufp;
	} 
#endif
	/*
	 * Enable interrupts only for EOL and DESC conditions.
	 * We mark tx descriptors to receive a DESC interrupt
	 * when a tx queue gets deep; otherwise waiting for the
	 * EOL to reap descriptors.  Note that this is done to
	 * reduce interrupt load and this only defers reaping
	 * descriptors, never transmitting frames.  Aside from
	 * reducing interrupts this also permits more concurrency.
	 * The only potential downside is if the tx queue backs
	 * up in which case the top half of the kernel may backup
	 * due to a lack of tx descriptors.
	 *
	 * The UAPSD queue is an exception, since we take a desc-
	 * based intr on the EOSP frames.
	 */
	if (qtype == HAL_TX_QUEUE_UAPSD)
		qi.tqi_qflags = HAL_TXQ_TXDESCINT_ENABLE;
	else
		qi.tqi_qflags = HAL_TXQ_TXEOLINT_ENABLE | HAL_TXQ_TXDESCINT_ENABLE;
	qnum = ath_hal_setuptxqueue(ah, qtype, &qi);
	if (qnum == -1) {
		/*
		 * NB: don't print a message, this happens
		 * normally on parts with too few tx queues
		 */
#ifdef ATH_SUPERG_COMP
		if (compbuf) {
			bus_free_consistent(sc->sc_bdev, compbufsz,
				compbuf, compbufp);
		}
#endif
		return NULL;
	}
	if (qnum >= N(sc->sc_txq)) {
		printk("%s: HAL qnum %u out of range, max %u!\n",
			sc->sc_dev->name, qnum, N(sc->sc_txq));
#ifdef ATH_SUPERG_COMP
		if (compbuf) {
			bus_free_consistent(sc->sc_bdev, compbufsz,
				compbuf, compbufp);
		}
#endif
		ath_hal_releasetxqueue(ah, qnum);
		return NULL;
	}
	if (!ATH_TXQ_SETUP(sc, qnum)) {
		struct ath_txq *txq = &sc->sc_txq[qnum];

		txq->axq_qnum = qnum;
		txq->axq_link = NULL;
		STAILQ_INIT(&txq->axq_q);
		ATH_TXQ_LOCK_INIT(txq);
		txq->axq_depth = 0;
		txq->axq_totalqueued = 0;
		txq->axq_intrcnt = 0;
		TAILQ_INIT(&txq->axq_stageq);
		txq->axq_compbuf = compbuf;
		txq->axq_compbufsz = compbufsz;
		txq->axq_compbufp = compbufp;
		sc->sc_txqsetup |= 1 << qnum;
	}
	return &sc->sc_txq[qnum];
#undef N
}

/*
 * Setup a hardware data transmit queue for the specified
 * access control.  The HAL may not support all requested
 * queues in which case it will return a reference to a
 * previously setup queue.  We record the mapping from ac's
 * to h/w queues for use by ath_tx_start and also track
 * the set of h/w queues being used to optimize work in the
 * transmit interrupt handler and related routines.
 */
static int
ath_tx_setup(struct ath_softc *sc, int ac, int haltype)
{
#define	N(a)	((int)(sizeof(a)/sizeof(a[0])))
	struct ath_txq *txq;

	if (ac >= N(sc->sc_ac2q)) {
		printk("%s: AC %u out of range, max %u!\n",
		       sc->sc_dev->name, ac, (unsigned)N(sc->sc_ac2q));
		return 0;
	}
	txq = ath_txq_setup(sc, HAL_TX_QUEUE_DATA, haltype);
	if (txq != NULL) {
		sc->sc_ac2q[ac] = txq;
		return 1;
	} else
		return 0;
#undef N
}

/*
 * Update WME parameters for a transmit queue.
 */
static int
ath_txq_update(struct ath_softc *sc, struct ath_txq *txq, int ac)
{
#define	ATH_EXPONENT_TO_VALUE(v)	((1<<v)-1)
#define	ATH_TXOP_TO_US(v)		(v<<5)
	struct ieee80211com *ic = &sc->sc_ic;
	struct wmeParams *wmep = &ic->ic_wme.wme_chanParams.cap_wmeParams[ac];
	struct ath_hal *ah = sc->sc_ah;
	HAL_TXQ_INFO qi;

	ath_hal_gettxqueueprops(ah, txq->axq_qnum, &qi);
	qi.tqi_aifs = wmep->wmep_aifsn;
	qi.tqi_cwmin = ATH_EXPONENT_TO_VALUE(wmep->wmep_logcwmin);
	qi.tqi_cwmax = ATH_EXPONENT_TO_VALUE(wmep->wmep_logcwmax);
	qi.tqi_burstTime = ATH_TXOP_TO_US(wmep->wmep_txopLimit);

	if (!ath_hal_settxqueueprops(ah, txq->axq_qnum, &qi)) {
		printk("%s: unable to update hardware queue "
			"parameters for %s traffic!\n",
			sc->sc_dev->name, ieee80211_wme_acnames[ac]);
		return 0;
	} else {
		ath_hal_resettxqueue(ah, txq->axq_qnum); /* push to h/w */
		return 1;
	}
#undef ATH_TXOP_TO_US
#undef ATH_EXPONENT_TO_VALUE
}

/*
 * Callback from the 802.11 layer to update WME parameters.
 */
static int
ath_wme_update(struct ieee80211com *ic)
{
	struct ath_softc *sc = ic->ic_dev->priv;

	if (sc->sc_uapsdq)
		ath_txq_update(sc, sc->sc_uapsdq, WME_AC_VO);

	return !ath_txq_update(sc, sc->sc_ac2q[WME_AC_BE], WME_AC_BE) ||
	    !ath_txq_update(sc, sc->sc_ac2q[WME_AC_BK], WME_AC_BK) ||
	    !ath_txq_update(sc, sc->sc_ac2q[WME_AC_VI], WME_AC_VI) ||
	    !ath_txq_update(sc, sc->sc_ac2q[WME_AC_VO], WME_AC_VO) ? EIO : 0;
}

/*
 * Callback from 802.11 layer to flush a node's U-APSD queues
 */
static void	
ath_uapsd_flush(struct ieee80211_node *ni)
{
	struct ath_node *an = ATH_NODE(ni);
	struct ath_buf *bf;
	struct ath_softc *sc = ni->ni_ic->ic_dev->priv;
	struct ath_txq *txq;

	ATH_NODE_UAPSD_LOCK_IRQ(an);
	/*
	 * NB: could optimize for successive runs from the same AC
	 *     if we can assume that is the most frequent case.
	 */
	while (an->an_uapsd_qdepth) {
		bf = STAILQ_FIRST(&an->an_uapsd_q);
		STAILQ_REMOVE_HEAD(&an->an_uapsd_q, bf_list);
		bf->bf_desc->ds_link = 0;
		txq = sc->sc_ac2q[bf->bf_skb->priority & 0x3];
		ath_tx_txqaddbuf(sc, ni, txq, bf, bf->bf_desc, bf->bf_skb->len);
		an->an_uapsd_qdepth--;
	}

	while (an->an_uapsd_overflowqdepth) {
		bf = STAILQ_FIRST(&an->an_uapsd_overflowq);
		STAILQ_REMOVE_HEAD(&an->an_uapsd_overflowq, bf_list);
		bf->bf_desc->ds_link = 0;
		txq = sc->sc_ac2q[bf->bf_skb->priority & 0x3];
		ath_tx_txqaddbuf(sc, ni, txq, bf, bf->bf_desc, bf->bf_skb->len);
		an->an_uapsd_overflowqdepth--;
	}
	if (IEEE80211_NODE_UAPSD_USETIM(ni))
		ni->ni_vap->iv_set_tim(ni, 0);
	ATH_NODE_UAPSD_UNLOCK_IRQ(an);
}

/*
 * Reclaim resources for a setup queue.
 */
static void
ath_tx_cleanupq(struct ath_softc *sc, struct ath_txq *txq)
{

#ifdef ATH_SUPERG_COMP
	/* Release compression buffer */
	if (txq->axq_compbuf) {
		bus_free_consistent(sc->sc_bdev, txq->axq_compbufsz,
			txq->axq_compbuf, txq->axq_compbufp);
		txq->axq_compbuf = NULL;
	}
#endif
	ath_hal_releasetxqueue(sc->sc_ah, txq->axq_qnum);
	ATH_TXQ_LOCK_DESTROY(txq);
	sc->sc_txqsetup &= ~(1 << txq->axq_qnum);
}

/*
 * Reclaim all tx queue resources.
 */
static void
ath_tx_cleanup(struct ath_softc *sc)
{
	int i;

	ATH_TXBUF_LOCK_DESTROY(sc);
	for (i = 0; i < HAL_NUM_TX_QUEUES; i++)
		if (ATH_TXQ_SETUP(sc, i))
			ath_tx_cleanupq(sc, &sc->sc_txq[i]);
}

#ifdef ATH_SUPERG_COMP
static u_int32_t
ath_get_icvlen(struct ieee80211_key *k)
{
	const struct ieee80211_cipher *cip = k->wk_cipher;

	if (cip->ic_cipher == IEEE80211_CIPHER_AES_CCM ||
		cip->ic_cipher == IEEE80211_CIPHER_AES_OCB)
		return AES_ICV_FIELD_SIZE;

	return WEP_ICV_FIELD_SIZE;
}

static u_int32_t
ath_get_ivlen(struct ieee80211_key *k)
{
	const struct ieee80211_cipher *cip = k->wk_cipher;
	u_int32_t ivlen;

	ivlen = WEP_IV_FIELD_SIZE;

	if (cip->ic_cipher == IEEE80211_CIPHER_AES_CCM ||
		cip->ic_cipher == IEEE80211_CIPHER_AES_OCB)
		ivlen += EXT_IV_FIELD_SIZE;
	
	return ivlen;
}
#endif

/*
 * Get transmit rate index using rate in Kbps
 */
static __inline int
ath_tx_findindex(const HAL_RATE_TABLE *rt, int rate)
{
	int i;
	int ndx = 0;

	for (i = 0; i < rt->rateCount; i++) {
		if (rt->info[i].rateKbps == rate) {
			ndx = i;
			break;
		}
	}

	return ndx;
}

/*
 * Needs external locking!
 */
static void
ath_tx_uapsdqueue(struct ath_softc *sc, struct ath_node *an, struct ath_buf *bf)
{
	struct ath_buf *lastbuf;

	/* case the delivery queue just sent and can move overflow q over */
	if (an->an_uapsd_qdepth == 0 && an->an_uapsd_overflowqdepth != 0) {
		DPRINTF(sc, ATH_DEBUG_UAPSD,
			"%s: delivery Q empty, replacing with overflow Q\n",
			__func__);
		STAILQ_CONCAT(&an->an_uapsd_q, &an->an_uapsd_overflowq);
		an->an_uapsd_qdepth = an->an_uapsd_overflowqdepth;
		an->an_uapsd_overflowqdepth = 0;
	}

	/* most common case - room on delivery q */
	if (an->an_uapsd_qdepth < an->an_node.ni_uapsd_maxsp) {
		/* add to delivery q */
		if ((lastbuf = STAILQ_LAST(&an->an_uapsd_q, ath_buf, bf_list))) {
#ifdef AH_NEED_DESC_SWAP
			lastbuf->bf_desc->ds_link = cpu_to_le32(bf->bf_daddr);
#else
			lastbuf->bf_desc->ds_link = bf->bf_daddr;
#endif
		}
		STAILQ_INSERT_TAIL(&an->an_uapsd_q, bf, bf_list);
		an->an_uapsd_qdepth++;
		DPRINTF(sc, ATH_DEBUG_UAPSD,
				"%s: added AC %d frame to delivery Q, new depth = %d\n", 
				__func__, bf->bf_skb->priority, an->an_uapsd_qdepth);
		return;
	}
	
	/* check if need to make room on overflow queue */
	if (an->an_uapsd_overflowqdepth == an->an_node.ni_uapsd_maxsp) {
		/* 
		 *  pop oldest from delivery queue and cleanup
		 */ 
		lastbuf = STAILQ_FIRST(&an->an_uapsd_q);
		STAILQ_REMOVE_HEAD(&an->an_uapsd_q, bf_list);
		dev_kfree_skb(lastbuf->bf_skb);
		lastbuf->bf_skb = NULL;
		ieee80211_free_node(lastbuf->bf_node);
		lastbuf->bf_node = NULL;
		ATH_TXBUF_LOCK_IRQ(sc);
		STAILQ_INSERT_TAIL(&sc->sc_txbuf, lastbuf, bf_list);
		ATH_TXBUF_UNLOCK_IRQ(sc);
		
		/*
		 *  move oldest from overflow to delivery
		 */
		lastbuf = STAILQ_FIRST(&an->an_uapsd_overflowq);
		STAILQ_REMOVE_HEAD(&an->an_uapsd_overflowq, bf_list);
		an->an_uapsd_overflowqdepth--;
		STAILQ_INSERT_TAIL(&an->an_uapsd_q, lastbuf, bf_list);
		DPRINTF(sc, ATH_DEBUG_UAPSD,
			"%s: delivery and overflow Qs full, dropped oldest\n",
			__func__);
	}

	/* add to overflow q */
	if ((lastbuf = STAILQ_LAST(&an->an_uapsd_overflowq, ath_buf, bf_list))) {
#ifdef AH_NEED_DESC_SWAP
		lastbuf->bf_desc->ds_link = cpu_to_le32(bf->bf_daddr);
#else
		lastbuf->bf_desc->ds_link = bf->bf_daddr;
#endif
	}
	STAILQ_INSERT_TAIL(&an->an_uapsd_overflowq, bf, bf_list);
	an->an_uapsd_overflowqdepth++;
	DPRINTF(sc, ATH_DEBUG_UAPSD, "%s: added AC %d to overflow Q, new depth = %d\n",
		__func__, bf->bf_skb->priority, an->an_uapsd_overflowqdepth);

	return;
}

static int
ath_tx_start(struct net_device *dev, struct ieee80211_node *ni, struct ath_buf *bf, struct sk_buff *skb, int nextfraglen)
{
#define	MIN(a,b)	((a) < (b) ? (a) : (b))
	struct ath_softc *sc = dev->priv;
	struct ieee80211com *ic = ni->ni_ic;
	struct ieee80211vap *vap = ni->ni_vap;
	struct ath_hal *ah = sc->sc_ah;
	int isprot, ismcast, keyix, hdrlen, pktlen, try0;
	u_int8_t rix, txrate, ctsrate;
	u_int32_t ivlen = 0, icvlen = 0;
	int comp = ATH_COMP_PROC_NO_COMP_NO_CCS;
	u_int8_t cix = 0xff;		/* NB: silence compiler */
	struct ath_desc *ds = NULL;
	struct ath_txq *txq = NULL;
	struct ieee80211_frame *wh;
	u_int subtype, flags, ctsduration;
	HAL_PKT_TYPE atype;
	const HAL_RATE_TABLE *rt;
	HAL_BOOL shortPreamble;
	struct ath_node *an;
	struct ath_vap *avp = ATH_VAP(vap);
	int istxfrag;
	u_int8_t antenna;

	wh = (struct ieee80211_frame *) skb->data;
	isprot = wh->i_fc[1] & IEEE80211_FC1_PROT;
	ismcast = IEEE80211_IS_MULTICAST(wh->i_addr1);
	hdrlen = ieee80211_anyhdrsize(wh);
	istxfrag = (wh->i_fc[1] & IEEE80211_FC1_MORE_FRAG) || 
		(((le16toh(*(__le16 *) &wh->i_seq[0]) >> 
		IEEE80211_SEQ_FRAG_SHIFT) & IEEE80211_SEQ_FRAG_MASK) > 0);

	pktlen = skb->len;
#ifdef ATH_SUPERG_FF
	{
		struct sk_buff *skbtmp = skb;
		while ((skbtmp = skbtmp->next))
			pktlen += skbtmp->len;
	}
#endif
	/*
	 * Packet length must not include any
	 * pad bytes; deduct them here.
	 */
	pktlen -= (hdrlen & 3);

	if (isprot) {
		const struct ieee80211_cipher *cip;
		struct ieee80211_key *k;

		/*
		 * Construct the 802.11 header+trailer for an encrypted
		 * frame. The only reason this can fail is because of an
		 * unknown or unsupported cipher/key type.
		 */

		/* FFXXX: change to handle linked skbs */
		k = ieee80211_crypto_encap(ni, skb);
		if (k == NULL) {
			/*
			 * This can happen when the key is yanked after the
			 * frame was queued.  Just discard the frame; the
			 * 802.11 layer counts failures and provides
			 * debugging/diagnostics.
			 */
			return -EIO;
		}
		/*
		 * Adjust the packet + header lengths for the crypto
		 * additions and calculate the h/w key index.  When
		 * a s/w mic is done the frame will have had any mic
		 * added to it prior to entry so skb->len above will
		 * account for it. Otherwise we need to add it to the
		 * packet length.
		 */
		cip = k->wk_cipher;
		hdrlen += cip->ic_header;
		pktlen += cip->ic_header + cip->ic_trailer;
		if ((k->wk_flags & IEEE80211_KEY_SWMIC) == 0) {
			if (!istxfrag)
				pktlen += cip->ic_miclen;
			else
				if (cip->ic_cipher != IEEE80211_CIPHER_TKIP)
					pktlen += cip->ic_miclen;
		}
		keyix = k->wk_keyix;

#ifdef ATH_SUPERG_COMP
		icvlen = ath_get_icvlen(k) / 4;
		ivlen = ath_get_ivlen(k) / 4;
#endif
		/* packet header may have moved, reset our local pointer */
		wh = (struct ieee80211_frame *) skb->data;
	} else if (ni->ni_ucastkey.wk_cipher == &ieee80211_cipher_none) {
		/*
		 * Use station key cache slot, if assigned.
		 */
		keyix = ni->ni_ucastkey.wk_keyix;
		if (keyix == IEEE80211_KEYIX_NONE)
			keyix = HAL_TXKEYIX_INVALID;
	} else
		keyix = HAL_TXKEYIX_INVALID;

	pktlen += IEEE80211_CRC_LEN;

	/*
	 * Load the DMA map so any coalescing is done.  This
	 * also calculates the number of descriptors we need.
	 */
#ifndef ATH_SUPERG_FF
	bf->bf_skbaddr = bus_map_single(sc->sc_bdev,
		skb->data, pktlen, BUS_DMA_TODEVICE);
	DPRINTF(sc, ATH_DEBUG_XMIT, "%s: skb %p [data %p len %u] skbaddr %llx\n",
		__func__, skb, skb->data, skb->len, ito64(bf->bf_skbaddr));
#else /* ATH_SUPERG_FF case */
	/* NB: ensure skb->len had been updated for each skb so we don't need pktlen */
	{
		struct sk_buff *skbtmp = skb;
		int i = 0;

		bf->bf_skbaddr = bus_map_single(sc->sc_bdev,
			skb->data, skb->len, BUS_DMA_TODEVICE);
 		DPRINTF(sc, ATH_DEBUG_XMIT, "%s: skb%d %p [data %p len %u] skbaddr %llx\n",
			__func__, i, skb, skb->data, skb->len, ito64(bf->bf_skbaddr));
		while ((skbtmp = skbtmp->next)) {
			bf->bf_skbaddrff[i++] = bus_map_single(sc->sc_bdev,
				skbtmp->data, skbtmp->len, BUS_DMA_TODEVICE);
			DPRINTF(sc, ATH_DEBUG_XMIT, "%s: skb%d %p [data %p len %u] skbaddr %llx\n",
				__func__, i, skbtmp, skbtmp->data, skbtmp->len,
				ito64(bf->bf_skbaddrff[i-1]));
		}
		bf->bf_numdesc = i + 1;
	}
#endif /* ATH_SUPERG_FF */
	bf->bf_skb = skb;
	bf->bf_node = ni;

	/* setup descriptors */
	ds = bf->bf_desc;
#ifdef ATH_SUPERG_XR
	if(vap->iv_flags & IEEE80211_F_XR ) 
		rt = sc->sc_xr_rates;
	else
		rt = sc->sc_currates;
#else
	rt = sc->sc_currates;
#endif
	KASSERT(rt != NULL, ("no rate table, mode %u", sc->sc_curmode));

	/*
	 * NB: the 802.11 layer marks whether or not we should
	 * use short preamble based on the current mode and
	 * negotiated parameters.
	 */
	if ((ic->ic_flags & IEEE80211_F_SHPREAMBLE) &&
	    (ni->ni_capinfo & IEEE80211_CAPINFO_SHORT_PREAMBLE)) {
		shortPreamble = AH_TRUE;
		sc->sc_stats.ast_tx_shortpre++;
	} else
		shortPreamble = AH_FALSE;

	an = ATH_NODE(ni);
	flags = HAL_TXDESC_CLRDMASK;		/* XXX needed for crypto errs */
	/*
	 * Calculate Atheros packet type from IEEE80211 packet header,
	 * setup for rate calculations, and select h/w transmit queue.
	 */
	switch (wh->i_fc[0] & IEEE80211_FC0_TYPE_MASK) {
	case IEEE80211_FC0_TYPE_MGT:
		subtype = wh->i_fc[0] & IEEE80211_FC0_SUBTYPE_MASK;
		if (subtype == IEEE80211_FC0_SUBTYPE_BEACON)
			atype = HAL_PKT_TYPE_BEACON;
		else if (subtype == IEEE80211_FC0_SUBTYPE_PROBE_RESP)
			atype = HAL_PKT_TYPE_PROBE_RESP;
		else if (subtype == IEEE80211_FC0_SUBTYPE_ATIM)
			atype = HAL_PKT_TYPE_ATIM;
		else
			atype = HAL_PKT_TYPE_NORMAL;	/* XXX */
		rix = sc->sc_minrateix;
		txrate = rt->info[rix].rateCode;
		if (shortPreamble)
			txrate |= rt->info[rix].shortPreamble;
		try0 = ATH_TXMAXTRY;

		if (ni->ni_flags & IEEE80211_NODE_QOS) {
			/* NB: force all management frames to highest queue */
			txq = sc->sc_ac2q[WME_AC_VO];
		} else
			txq = sc->sc_ac2q[WME_AC_BE];
		break;
	case IEEE80211_FC0_TYPE_CTL:
		atype = HAL_PKT_TYPE_PSPOLL;	/* stop setting of duration */
		rix = sc->sc_minrateix;
		txrate = rt->info[rix].rateCode;
		if (shortPreamble)
			txrate |= rt->info[rix].shortPreamble;
		try0 = ATH_TXMAXTRY;

		if (ni->ni_flags & IEEE80211_NODE_QOS) {
			/* NB: force all ctl frames to highest queue */
			txq = sc->sc_ac2q[WME_AC_VO];
		} else
			txq = sc->sc_ac2q[WME_AC_BE];
		break;
	case IEEE80211_FC0_TYPE_DATA:
		atype = HAL_PKT_TYPE_NORMAL;		/* default */
		
		if (ismcast) {
			rix = ath_tx_findindex(rt, vap->iv_mcast_rate);
			txrate = rt->info[rix].rateCode;
			if (shortPreamble)
				txrate |= rt->info[rix].shortPreamble;
			/* 
			 * ATH_TXMAXTRY disables Multi-rate retries, which
			 * isn't applicable to mcast packets and overrides
			 * the desired transmission rate for mcast traffic.
			 */
			try0 = ATH_TXMAXTRY;
		} else {
			/*
			 * Data frames; consult the rate control module.
			 */
			sc->sc_rc->ops->findrate(sc, an, shortPreamble, skb->len,
				&rix, &try0, &txrate);

			/* Ratecontrol sometimes returns invalid rate index */
			if (rix != 0xff)
				an->an_prevdatarix = rix;
			else
				rix = an->an_prevdatarix;
		}

		if (M_FLAG_GET(skb, M_UAPSD)) {
			/* U-APSD frame, handle txq later */
			break;
		}

		/*
		 * Default all non-QoS traffic to the best-effort queue.
		 */
		if (wh->i_fc[0] & IEEE80211_FC0_SUBTYPE_QOS) {
			/* XXX validate skb->priority, remove mask */
			txq = sc->sc_ac2q[skb->priority & 0x3];
			if (ic->ic_wme.wme_wmeChanParams.cap_wmeParams[skb->priority].wmep_noackPolicy) {
				flags |= HAL_TXDESC_NOACK;
				sc->sc_stats.ast_tx_noack++;
			}
		} else
			txq = sc->sc_ac2q[WME_AC_BE];
		break;
	default:
		printk("%s: bogus frame type 0x%x (%s)\n", dev->name,
			wh->i_fc[0] & IEEE80211_FC0_TYPE_MASK, __func__);
		/* XXX statistic */
		return -EIO;
	}

#ifdef ATH_SUPERG_XR 
	if (vap->iv_flags & IEEE80211_F_XR ) {
		txq = sc->sc_xrtxq;
		if (!txq)
			txq = sc->sc_ac2q[WME_AC_BK];
		flags |= HAL_TXDESC_CTSENA;
		cix = rt->info[sc->sc_protrix].controlRate;
	}
#endif
	/*
	 * When servicing one or more stations in power-save mode (or)
	 * if there is some mcast data waiting on mcast queue
	 * (to prevent out of order delivery of mcast,bcast packets)
	 * multicast frames must be buffered until after the beacon.
	 * We use the private mcast queue for that.
	 */
	if (ismcast && (vap->iv_ps_sta || avp->av_mcastq.axq_depth)) {
		txq = &avp->av_mcastq;
		/* XXX? more bit in 802.11 frame header */
	}

	/*
	 * Calculate miscellaneous flags.
	 */
	if (ismcast) {
		flags |= HAL_TXDESC_NOACK;	/* no ack on broad/multicast */
		sc->sc_stats.ast_tx_noack++;
		try0 = ATH_TXMAXTRY;    /* turn off multi-rate retry for multicast traffic */
	 } else if (pktlen > vap->iv_rtsthreshold) { 
#ifdef ATH_SUPERG_FF
		/* we could refine to only check that the frame of interest
		 * is a FF, but this seems inconsistent.
		 */
		if (!(vap->iv_ath_cap & ni->ni_ath_flags & IEEE80211_ATHC_FF)) {
#endif
			flags |= HAL_TXDESC_RTSENA;	/* RTS based on frame length */
			cix = rt->info[rix].controlRate;
			sc->sc_stats.ast_tx_rts++;
#ifdef ATH_SUPERG_FF
		}
#endif
	}

	/*
	 * If 802.11g protection is enabled, determine whether
	 * to use RTS/CTS or just CTS.  Note that this is only
	 * done for OFDM unicast frames.
	 */
	if ((ic->ic_flags & IEEE80211_F_USEPROT) &&
	    rt->info[rix].phy == IEEE80211_T_OFDM &&
	    (flags & HAL_TXDESC_NOACK) == 0) {
		/* XXX fragments must use CCK rates w/ protection */
		if (ic->ic_protmode == IEEE80211_PROT_RTSCTS)
			flags |= HAL_TXDESC_RTSENA;
		else if (ic->ic_protmode == IEEE80211_PROT_CTSONLY)
			flags |= HAL_TXDESC_CTSENA;

		if (istxfrag)
			/*
			**  if Tx fragment, it would be desirable to 
			**  use highest CCK rate for RTS/CTS.
			**  However, stations farther away may detect it
			**  at a lower CCK rate. Therefore, use the 
			**  configured protect rate, which is 2 Mbps
			**  for 11G.
			*/
			cix = rt->info[sc->sc_protrix].controlRate;
		else
			cix = rt->info[sc->sc_protrix].controlRate;
		sc->sc_stats.ast_tx_protect++;
	}

	/*
	 * Calculate duration.  This logically belongs in the 802.11
	 * layer but it lacks sufficient information to calculate it.
	 */
	if ((flags & HAL_TXDESC_NOACK) == 0 &&
	    (wh->i_fc[0] & IEEE80211_FC0_TYPE_MASK) != IEEE80211_FC0_TYPE_CTL) {
		u_int16_t dur;
		/*
		 * XXX not right with fragmentation.
		 */
		if (shortPreamble)
			dur = rt->info[rix].spAckDuration;
		else
			dur = rt->info[rix].lpAckDuration;

		if (wh->i_fc[1] & IEEE80211_FC1_MORE_FRAG) {
			dur += dur;  /* Add additional 'SIFS + ACK' */

			/*
			** Compute size of next fragment in order to compute
			** durations needed to update NAV.
			** The last fragment uses the ACK duration only.
			** Add time for next fragment.
			*/
			dur += ath_hal_computetxtime(ah, rt, nextfraglen, 
				rix, shortPreamble);
		}

		if (istxfrag) {
			/*
			**  Force hardware to use computed duration for next
			**  fragment by disabling multi-rate retry, which
			**  updates duration based on the multi-rate
			**  duration table.
			*/
			try0 = ATH_TXMAXTRY;
		}

		wh->i_dur = cpu_to_le16(dur);
	}

	/*
	 * Calculate RTS/CTS rate and duration if needed.
	 */
	ctsduration = 0;
	if (flags & (HAL_TXDESC_RTSENA|HAL_TXDESC_CTSENA)) {
		/*
		 * CTS transmit rate is derived from the transmit rate
		 * by looking in the h/w rate table.  We must also factor
		 * in whether or not a short preamble is to be used.
		 */
		/* NB: cix is set above where RTS/CTS is enabled */
		KASSERT(cix != 0xff, ("cix not setup"));
		ctsrate = rt->info[cix].rateCode;
		/*
		 * Compute the transmit duration based on the frame
		 * size and the size of an ACK frame.  We call into the
		 * HAL to do the computation since it depends on the
		 * characteristics of the actual PHY being used.
		 *
		 * NB: CTS is assumed the same size as an ACK so we can
		 *     use the precalculated ACK durations.
		 */
		if (shortPreamble) {
			ctsrate |= rt->info[cix].shortPreamble;
			if (flags & HAL_TXDESC_RTSENA)		/* SIFS + CTS */
				ctsduration += rt->info[cix].spAckDuration;
			ctsduration += ath_hal_computetxtime(ah,
				rt, pktlen, rix, AH_TRUE);
			if ((flags & HAL_TXDESC_NOACK) == 0)	/* SIFS + ACK */
				ctsduration += rt->info[rix].spAckDuration;
		} else {
			if (flags & HAL_TXDESC_RTSENA)		/* SIFS + CTS */
				ctsduration += rt->info[cix].lpAckDuration;
			ctsduration += ath_hal_computetxtime(ah,
				rt, pktlen, rix, AH_FALSE);
			if ((flags & HAL_TXDESC_NOACK) == 0)	/* SIFS + ACK */
				ctsduration += rt->info[rix].lpAckDuration;
		}
		/*
		 * Must disable multi-rate retry when using RTS/CTS.
		 */
		try0 = ATH_TXMAXTRY;
	} else 
		ctsrate = 0;

	if (IFF_DUMPPKTS(sc, ATH_DEBUG_XMIT))
		/* FFXXX: need multi-skb version to dump entire FF */
		ieee80211_dump_pkt(ic, skb->data, skb->len,
			sc->sc_hwmap[txrate].ieeerate, -1);

	/*
	 * Determine if a tx interrupt should be generated for
	 * this descriptor.  We take a tx interrupt to reap
	 * descriptors when the h/w hits an EOL condition or
	 * when the descriptor is specifically marked to generate
	 * an interrupt.  We periodically mark descriptors in this
	 * way to ensure timely replenishing of the supply needed
	 * for sending frames.  Deferring interrupts reduces system
	 * load and potentially allows more concurrent work to be
	 * done, but if done too aggressively, it can cause senders
	 * to backup.
	 *
	 * NB: use >= to deal with sc_txintrperiod changing
	 *     dynamically through sysctl.
	 */
	if (!M_FLAG_GET(skb, M_UAPSD) &&
		++txq->axq_intrcnt >= sc->sc_txintrperiod) {
		flags |= HAL_TXDESC_INTREQ;
		txq->axq_intrcnt = 0;
	}

#ifdef ATH_SUPERG_COMP
	if (ATH_NODE(ni)->an_decomp_index != INVALID_DECOMP_INDEX && 
	    !ismcast &&
	    ((wh->i_fc[0] & IEEE80211_FC0_TYPE_MASK) == IEEE80211_FC0_TYPE_DATA) &&
	    ((wh->i_fc[0] & IEEE80211_FC0_SUBTYPE_MASK) != IEEE80211_FC0_SUBTYPE_NODATA)) {
		if (pktlen > ATH_COMP_THRESHOLD)
			comp = ATH_COMP_PROC_COMP_OPTIMAL;
		else
			comp = ATH_COMP_PROC_NO_COMP_ADD_CCS;
	} 
#endif

	/*
	 * sc_txantenna == 0 means transmit diversity mode.
	 * sc_txantenna == 1 or sc_txantenna == 2 means the user has selected
	 * the first or second antenna port.
	 * If the user has set the txantenna, use it for multicast frames too.
	 */
	if (ismcast && !sc->sc_txantenna) {
		antenna = sc->sc_mcastantenna + 1;
		sc->sc_mcastantenna = (sc->sc_mcastantenna + 1) & 0x1;
	} else
		antenna = sc->sc_txantenna;

	if (txrate == 0) {
		/* Drop frame, if the rate is 0.
		 * Otherwise this may lead to the continuous transmission of
		 * noise. */
		printk("%s: invalid TX rate %u (%s: %u)\n", dev->name,
			txrate, __func__, __LINE__);
		return -EIO;
	}

	DPRINTF(sc, ATH_DEBUG_XMIT, "%s: set up txdesc: pktlen %d hdrlen %d "
		"atype %d txpower %d txrate %d try0 %d keyix %d ant %d flags %x "
		"ctsrate %d ctsdur %d icvlen %d ivlen %d comp %d\n",
		__func__, pktlen, hdrlen, atype, MIN(ni->ni_txpower, 60), txrate,
		try0, keyix, antenna, flags, ctsrate, ctsduration, icvlen, ivlen,
		comp);

	/*
	 * Formulate first tx descriptor with tx controls.
	 */
	/* XXX check return value? */
	ath_hal_setuptxdesc(ah, ds
			    , pktlen		/* packet length */
			    , hdrlen		/* header length */
			    , atype		/* Atheros packet type */
			    , MIN(ni->ni_txpower, 60)/* txpower */
			    , txrate, try0	/* series 0 rate/tries */
			    , keyix		/* key cache index */
			    , antenna		/* antenna mode */
			    , flags		/* flags */
			    , ctsrate		/* rts/cts rate */
			    , ctsduration	/* rts/cts duration */
			    , icvlen		/* comp icv len */
			    , ivlen		/* comp iv len */
			    , comp		/* comp scheme */
		);
	bf->bf_flags = flags;			/* record for post-processing */

	/*
	 * Setup the multi-rate retry state only when we're
	 * going to use it.  This assumes ath_hal_setuptxdesc
	 * initializes the descriptors (so we don't have to)
	 * when the hardware supports multi-rate retry and
	 * we don't use it.
	 */
	if (try0 != ATH_TXMAXTRY)
		sc->sc_rc->ops->setupxtxdesc(sc, an, ds, shortPreamble,
					     skb->len, rix);

#ifndef ATH_SUPERG_FF
	ds->ds_link = 0;
	ds->ds_data = bf->bf_skbaddr;

	ath_hal_filltxdesc(ah, ds
			   , skb->len	/* segment length */
			   , AH_TRUE	/* first segment */
			   , AH_TRUE	/* last segment */
			   , ds		/* first descriptor */
		);

	/* NB: The desc swap function becomes void, 
	 * if descriptor swapping is not enabled
	 */
	ath_desc_swap(ds);

	DPRINTF(sc, ATH_DEBUG_XMIT, "%s: Q%d: %08x %08x %08x %08x %08x %08x\n",
	    __func__, M_FLAG_GET(skb, M_UAPSD) ? 0 : txq->axq_qnum, ds->ds_link, ds->ds_data,
	    ds->ds_ctl0, ds->ds_ctl1, ds->ds_hw[0], ds->ds_hw[1]);
#else /* ATH_SUPERG_FF */
	{
		struct sk_buff *skbtmp = skb;
		struct ath_desc *ds0 = ds;
		int i;

		ds->ds_data = bf->bf_skbaddr;
		ds->ds_link = (skb->next == NULL) ? 0 : bf->bf_daddr + sizeof(*ds);

		ath_hal_filltxdesc(ah, ds
			, skbtmp->len		/* segment length */
			, AH_TRUE		/* first segment */
			, skbtmp->next == NULL	/* last segment */
			, ds			/* first descriptor */
		);

		/* NB: The desc swap function becomes void, 
		 * if descriptor swapping is not enabled
		 */
		ath_desc_swap(ds);

		DPRINTF(sc, ATH_DEBUG_XMIT, "%s: Q%d: (ds)%p (lk)%08x (d)%08x (c0)%08x (c1)%08x %08x %08x\n",
			__func__, M_FLAG_GET(skb, M_UAPSD) ? 0 : txq->axq_qnum,
			ds, ds->ds_link, ds->ds_data, ds->ds_ctl0, ds->ds_ctl1,
			ds->ds_hw[0], ds->ds_hw[1]);
		for (i= 0, skbtmp = skbtmp->next; i < bf->bf_numdesc - 1; i++, skbtmp = skbtmp->next) {
			ds++;
			ds->ds_link = skbtmp->next == NULL ? 0 : bf->bf_daddr + sizeof(*ds) * (i + 2);
			ds->ds_data = bf->bf_skbaddrff[i];
			ath_hal_filltxdesc(ah, ds
				, skbtmp->len		/* segment length */
				, AH_FALSE		/* first segment */
				, skbtmp->next == NULL	/* last segment */
				, ds0			/* first descriptor */
			);

			/* NB: The desc swap function becomes void, 
		 	 * if descriptor swapping is not enabled
		 	 */
			ath_desc_swap(ds);

			DPRINTF(sc, ATH_DEBUG_XMIT, "%s: Q%d: %08x %08x %08x %08x %08x %08x\n",
				__func__, M_FLAG_GET(skb, M_UAPSD) ? 0 : txq->axq_qnum,
				ds->ds_link, ds->ds_data, ds->ds_ctl0,
				ds->ds_ctl1, ds->ds_hw[0], ds->ds_hw[1]);
		}
	}
#endif

	if (M_FLAG_GET(skb, M_UAPSD)) {
		/* must lock against interrupt-time processing (i.e., not just tasklet) */
		ATH_NODE_UAPSD_LOCK_IRQ(an);
		DPRINTF(sc, ATH_DEBUG_UAPSD, "%s: Qing U-APSD data frame for node %s \n", 
			__func__, ether_sprintf(an->an_node.ni_macaddr));
		ath_tx_uapsdqueue(sc, an, bf);
		if (IEEE80211_NODE_UAPSD_USETIM(ni) && (an->an_uapsd_qdepth == 1))
			vap->iv_set_tim(ni, 1);
		ATH_NODE_UAPSD_UNLOCK_IRQ(an);

		return 0;
	}
	
	
	IEEE80211_DPRINTF(vap, IEEE80211_MSG_NODE, "%s: %p<%s> refcnt %d\n",
		__func__, vap->iv_bss, ether_sprintf(vap->iv_bss->ni_macaddr),
		ieee80211_node_refcnt(vap->iv_bss));


	ath_tx_txqaddbuf(sc, ni, txq, bf, ds, pktlen);
	return 0;
#undef MIN
}

/*
 * Process completed xmit descriptors from the specified queue.
 * Should only be called from tasklet context
 */
static void
ath_tx_processq(struct ath_softc *sc, struct ath_txq *txq)
{
	struct ath_hal *ah = sc->sc_ah;
	struct ath_buf *bf = NULL;
	struct ath_desc *ds = NULL;
	struct ieee80211_node *ni = NULL;
	struct ath_node *an = NULL;
	int sr, lr;
	HAL_STATUS status;
	int uapsdq = 0;
	unsigned long uapsdq_lockflags = 0;

	DPRINTF(sc, ATH_DEBUG_TX_PROC, "%s: tx queue %d (0x%x), link %p\n", __func__,
		txq->axq_qnum, ath_hal_gettxbuf(sc->sc_ah, txq->axq_qnum),
		txq->axq_link);

	if (txq == sc->sc_uapsdq) {
		DPRINTF(sc, ATH_DEBUG_UAPSD, "%s: reaping U-APSD txq\n", __func__);
		uapsdq = 1;
	}

	for (;;) {
		if (uapsdq)
			ATH_TXQ_UAPSDQ_LOCK_IRQ(txq);
		else
			ATH_TXQ_LOCK(txq);
		txq->axq_intrcnt = 0; /* reset periodic desc intr count */
		bf = STAILQ_FIRST(&txq->axq_q);
		if (bf == NULL) {
			txq->axq_link = NULL;
			if (uapsdq)
				ATH_TXQ_UAPSDQ_UNLOCK_IRQ(txq);
			else
				ATH_TXQ_UNLOCK(txq);
			break;
		}

#ifdef ATH_SUPERG_FF
		ds = &bf->bf_desc[bf->bf_numdesc - 1];
		DPRINTF(sc, ATH_DEBUG_TX_PROC, "%s: frame's last desc: %p\n",
			__func__, ds);
#else
		ds = bf->bf_desc;		/* NB: last descriptor */
#endif
		status = ath_hal_txprocdesc(ah, ds);
#ifdef AR_DEBUG
		if (sc->sc_debug & ATH_DEBUG_XMIT_DESC)
			ath_printtxbuf(bf, status == HAL_OK);
#endif
		if (status == HAL_EINPROGRESS) {
			if (uapsdq)
				ATH_TXQ_UAPSDQ_UNLOCK_IRQ(txq);
			else
				ATH_TXQ_UNLOCK(txq);
			break;
		}

		ATH_TXQ_REMOVE_HEAD(txq, bf_list);
		if (uapsdq)
			ATH_TXQ_UAPSDQ_UNLOCK_IRQ(txq);
		else
			ATH_TXQ_UNLOCK(txq);

		ni = bf->bf_node;
		if (ni != NULL) {
			an = ATH_NODE(ni);
			if (ds->ds_txstat.ts_status == 0) {
				u_int8_t txant = ds->ds_txstat.ts_antenna;
				sc->sc_stats.ast_ant_tx[txant]++;
				sc->sc_ant_tx[txant]++;
#ifdef ATH_SUPERG_FF
				if (bf->bf_numdesc > 1)
					ni->ni_vap->iv_stats.is_tx_ffokcnt++;
#endif
				if (ds->ds_txstat.ts_rate & HAL_TXSTAT_ALTRATE)
					sc->sc_stats.ast_tx_altrate++;
				sc->sc_stats.ast_tx_rssi =
					ds->ds_txstat.ts_rssi;
				ATH_RSSI_LPF(an->an_halstats.ns_avgtxrssi,
					ds->ds_txstat.ts_rssi);
				if (bf->bf_skb->priority == WME_AC_VO ||
				    bf->bf_skb->priority == WME_AC_VI)
					ni->ni_ic->ic_wme.wme_hipri_traffic++;
				ni->ni_inact = ni->ni_inact_reload;
			} else {
#ifdef ATH_SUPERG_FF
				if (bf->bf_numdesc > 1)
					ni->ni_vap->iv_stats.is_tx_fferrcnt++;
#endif
				if (ds->ds_txstat.ts_status & HAL_TXERR_XRETRY) {
					sc->sc_stats.ast_tx_xretries++;
					if (ni->ni_flags & IEEE80211_NODE_UAPSD_TRIG) {
						ni->ni_stats.ns_tx_eosplost++;
						DPRINTF(sc, ATH_DEBUG_UAPSD,
							"%s: frame in SP retried out, possible EOSP stranded!!!\n",
							__func__);
					}
				}
				if (ds->ds_txstat.ts_status & HAL_TXERR_FIFO)
					sc->sc_stats.ast_tx_fifoerr++;
				if (ds->ds_txstat.ts_status & HAL_TXERR_FILT)
					sc->sc_stats.ast_tx_filtered++;
			}
			sr = ds->ds_txstat.ts_shortretry;
			lr = ds->ds_txstat.ts_longretry;
			sc->sc_stats.ast_tx_shortretry += sr;
			sc->sc_stats.ast_tx_longretry += lr;
			/*
			 * Hand the descriptor to the rate control algorithm
			 * if the frame wasn't dropped for filtering or sent
			 * w/o waiting for an ack.  In those cases the rssi
			 * and retry counts will be meaningless.
			 */
			if ((ds->ds_txstat.ts_status & HAL_TXERR_FILT) == 0 &&
			    (bf->bf_flags & HAL_TXDESC_NOACK) == 0)
				sc->sc_rc->ops->tx_complete(sc, an, ds);
			/*
			 * Reclaim reference to node.
			 *
			 * NB: the node may be reclaimed here if, for example
			 *     this is a DEAUTH message that was sent and the
			 *     node was timed out due to inactivity.
			 */
			 ieee80211_free_node(ni); 
		}

		bus_unmap_single(sc->sc_bdev, bf->bf_skbaddr, 
                                 bf->bf_skb->len, BUS_DMA_TODEVICE);
		if (ni && uapsdq) {
			/* detect EOSP for this node */
			struct ieee80211_qosframe *qwh = (struct ieee80211_qosframe *)bf->bf_skb->data;
			an = ATH_NODE(ni);
			KASSERT(ni != NULL, ("Processing U-APSD txq for ath_buf with no node!\n"));
			if (qwh->i_qos[0] & IEEE80211_QOS_EOSP) {
				DPRINTF(sc, ATH_DEBUG_UAPSD, "%s: EOSP detected for node (%s) on desc %p\n", 
					__func__, ether_sprintf(ni->ni_macaddr), ds);
				ATH_NODE_UAPSD_LOCK_IRQ(an);
				ni->ni_flags &= ~IEEE80211_NODE_UAPSD_SP;
				if (an->an_uapsd_qdepth == 0 && an->an_uapsd_overflowqdepth != 0) {
					STAILQ_CONCAT(&an->an_uapsd_q, &an->an_uapsd_overflowq);
					an->an_uapsd_qdepth = an->an_uapsd_overflowqdepth;
					an->an_uapsd_overflowqdepth = 0;
				}
				ATH_NODE_UAPSD_UNLOCK_IRQ(an);
			}
		}

		{
			struct ieee80211_frame *wh = (struct ieee80211_frame *)bf->bf_skb->data;
			if ((ds->ds_txstat.ts_seqnum << IEEE80211_SEQ_SEQ_SHIFT) & ~IEEE80211_SEQ_SEQ_MASK) {
				DPRINTF(sc, ATH_DEBUG_TX_PROC, "%s: h/w assigned sequence number is not sane (%d), ignoring it\n", __func__,
				        ds->ds_txstat.ts_seqnum);
			} else {
				DPRINTF(sc, ATH_DEBUG_TX_PROC, "%s: updating frame's sequence number from %d to %d\n", __func__, 
				        (le16toh(*(__le16 *)&wh->i_seq[0]) & IEEE80211_SEQ_SEQ_MASK) >> IEEE80211_SEQ_SEQ_SHIFT,
				        ds->ds_txstat.ts_seqnum);

				*(__le16 *)&wh->i_seq[0] = htole16(
					ds->ds_txstat.ts_seqnum << IEEE80211_SEQ_SEQ_SHIFT |
					(le16toh(*(__le16 *)&wh->i_seq[0]) & ~IEEE80211_SEQ_SEQ_MASK));
			}
		}

#ifdef ATH_SUPERG_FF
		{
			struct sk_buff *skbfree, *skb = bf->bf_skb;
			int i;

			skbfree = skb;
			skb = skb->next;
			DPRINTF(sc, ATH_DEBUG_TX_PROC, "%s: free skb %p\n",
				__func__, skbfree);
			ath_tx_capture(sc->sc_dev, ds, skbfree);
			for (i = 1; i < bf->bf_numdesc; i++) {
				bus_unmap_single(sc->sc_bdev, bf->bf_skbaddrff[i-1],
					bf->bf_skb->len, BUS_DMA_TODEVICE);
				skbfree = skb;
				skb = skb->next;
				DPRINTF(sc, ATH_DEBUG_TX_PROC, "%s: free skb %p\n",
					__func__, skbfree);
				ath_tx_capture(sc->sc_dev, ds, skbfree);
			}
		}
		bf->bf_numdesc = 0;
#else
		DPRINTF(sc, ATH_DEBUG_TX_PROC, "%s: free skb %p\n", __func__, bf->bf_skb);
		ath_tx_capture(sc->sc_dev, ds, bf->bf_skb);
#endif
		bf->bf_skb = NULL;
		bf->bf_node = NULL;

		ATH_TXBUF_LOCK_IRQ(sc);
		STAILQ_INSERT_TAIL(&sc->sc_txbuf, bf, bf_list);
		if (sc->sc_devstopped) {
			++sc->sc_reapcount;
			if (sc->sc_reapcount > ATH_TXBUF_FREE_THRESHOLD) {
				if (!sc->sc_dfswait)
					netif_start_queue(sc->sc_dev);
				DPRINTF(sc, ATH_DEBUG_TX_PROC,
					"%s: tx tasklet restart the queue\n",
					__func__);
				sc->sc_reapcount = 0;
				sc->sc_devstopped = 0;
			} else
				ATH_SCHEDULE_TQUEUE(&sc->sc_txtq, NULL);
		}
		ATH_TXBUF_UNLOCK_IRQ(sc);
	}
#ifdef ATH_SUPERG_FF
	/* flush ff staging queue if buffer low */
	if (txq->axq_depth <= sc->sc_fftxqmin - 1) {
		/* NB: consider only flushing a preset number based on age. */
		ath_ffstageq_flush(sc, txq, ath_ff_neverflushtestdone);
	}
#endif /* ATH_SUPERG_FF */
}

static __inline int
txqactive(struct ath_hal *ah, int qnum)
{
	u_int32_t txqs = 1 << qnum;
	ath_hal_gettxintrtxqs(ah, &txqs);
	return (txqs & (1 << qnum));
}

/*
 * Deferred processing of transmit interrupt; special-cased
 * for a single hardware transmit queue (e.g. 5210 and 5211).
 */
static void
ath_tx_tasklet_q0(TQUEUE_ARG data)
{
	struct net_device *dev = (struct net_device *)data;
	struct ath_softc *sc = dev->priv;

	if (txqactive(sc->sc_ah, 0))
		ath_tx_processq(sc, &sc->sc_txq[0]);
	if (txqactive(sc->sc_ah, sc->sc_cabq->axq_qnum))
		ath_tx_processq(sc, sc->sc_cabq);

	netif_wake_queue(dev);

	if (sc->sc_softled)
		ath_led_event(sc, ATH_LED_TX);
}

/*
 * Deferred processing of transmit interrupt; special-cased
 * for four hardware queues, 0-3 (e.g. 5212 w/ WME support).
 */
static void
ath_tx_tasklet_q0123(TQUEUE_ARG data)
{
	struct net_device *dev = (struct net_device *)data;
	struct ath_softc *sc = dev->priv;

	/*
	 * Process each active queue.
	 */
	if (txqactive(sc->sc_ah, 0))
		ath_tx_processq(sc, &sc->sc_txq[0]);
	if (txqactive(sc->sc_ah, 1))
		ath_tx_processq(sc, &sc->sc_txq[1]);
	if (txqactive(sc->sc_ah, 2))
		ath_tx_processq(sc, &sc->sc_txq[2]);
	if (txqactive(sc->sc_ah, 3))
		ath_tx_processq(sc, &sc->sc_txq[3]);
	if (txqactive(sc->sc_ah, sc->sc_cabq->axq_qnum))
		ath_tx_processq(sc, sc->sc_cabq);
#ifdef ATH_SUPERG_XR
	if (sc->sc_xrtxq && txqactive(sc->sc_ah, sc->sc_xrtxq->axq_qnum))
		ath_tx_processq(sc, sc->sc_xrtxq);
#endif
	if (sc->sc_uapsdq && txqactive(sc->sc_ah, sc->sc_uapsdq->axq_qnum))
		ath_tx_processq(sc, sc->sc_uapsdq);

	netif_wake_queue(dev);

	if (sc->sc_softled)
		ath_led_event(sc, ATH_LED_TX);
}

/*
 * Deferred processing of transmit interrupt.
 */
static void
ath_tx_tasklet(TQUEUE_ARG data)
{
	struct net_device *dev = (struct net_device *)data;
	struct ath_softc *sc = dev->priv;
	int i;

	/*
	 * Process each active queue.
	 */
	for (i = 0; i < HAL_NUM_TX_QUEUES; i++)
		if (ATH_TXQ_SETUP(sc, i) && txqactive(sc->sc_ah, i))
			ath_tx_processq(sc, &sc->sc_txq[i]);
#ifdef ATH_SUPERG_XR
	if (sc->sc_xrtxq && txqactive(sc->sc_ah, sc->sc_xrtxq->axq_qnum))
		ath_tx_processq(sc, sc->sc_xrtxq);
#endif

	netif_wake_queue(dev);

	if (sc->sc_softled)
		ath_led_event(sc, ATH_LED_TX);
}

static void
ath_tx_timeout(struct net_device *dev)
{
	struct ath_softc *sc = dev->priv;

	DPRINTF(sc, ATH_DEBUG_WATCHDOG, "%s: %sRUNNING %svalid\n",
		__func__, (dev->flags & IFF_RUNNING) ? "" : "!",
		sc->sc_invalid ? "in" : "");

	if ((dev->flags & IFF_RUNNING) && !sc->sc_invalid) {
		sc->sc_stats.ast_watchdog++;
		ath_reset(dev);	/* Avoid taking a semaphore in ath_init */
	}
}

/* 
 * Context: softIRQ and hwIRQ
 */
static void
ath_tx_draintxq(struct ath_softc *sc, struct ath_txq *txq)
{
	struct ath_hal *ah = sc->sc_ah;
	struct ath_buf *bf;
	struct sk_buff *skb;
#ifdef ATH_SUPERG_FF
	struct sk_buff *tskb;
#endif
	int i;

	/*
	 * NB: this assumes output has been stopped and
	 *     we do not need to block ath_tx_tasklet
	 */
	for (;;) {
		ATH_TXQ_LOCK(txq);
		bf = STAILQ_FIRST(&txq->axq_q);
		if (bf == NULL) {
			txq->axq_link = NULL;
			ATH_TXQ_UNLOCK(txq);
			break;
		}
		ATH_TXQ_REMOVE_HEAD(txq, bf_list);
		ATH_TXQ_UNLOCK(txq);
#ifdef AR_DEBUG
		if (sc->sc_debug & ATH_DEBUG_RESET)
			ath_printtxbuf(bf, ath_hal_txprocdesc(ah, bf->bf_desc) == HAL_OK);
#endif /* AR_DEBUG */
		skb = bf->bf_skb->next;
		bus_unmap_single(sc->sc_bdev,
			bf->bf_skbaddr, bf->bf_skb->len, BUS_DMA_TODEVICE);
		dev_kfree_skb_any(bf->bf_skb);
		i = 0;
#ifdef ATH_SUPERG_FF
		while (skb) {
			tskb = skb->next;
			bus_unmap_single(sc->sc_bdev,
				 bf->bf_skbaddrff[i++], skb->len, BUS_DMA_TODEVICE);
			dev_kfree_skb_any(skb);
			skb = tskb;
		}
#endif /* ATH_SUPERG_FF */
		if (bf->bf_node)
			ieee80211_free_node(bf->bf_node);

		bf->bf_skb = NULL;
		bf->bf_node = NULL;

		ATH_TXBUF_LOCK(sc);
		STAILQ_INSERT_TAIL(&sc->sc_txbuf, bf, bf_list);
		ATH_TXBUF_UNLOCK(sc);
	}
}

static void
ath_tx_stopdma(struct ath_softc *sc, struct ath_txq *txq)
{
	struct ath_hal *ah = sc->sc_ah;

	(void) ath_hal_stoptxdma(ah, txq->axq_qnum);
	DPRINTF(sc, ATH_DEBUG_RESET, "%s: tx queue [%u] 0x%x, link %p\n",
		__func__, txq->axq_qnum,
		ath_hal_gettxbuf(ah, txq->axq_qnum), txq->axq_link);
}

/*
 * Drain the transmit queues and reclaim resources.
 */
static void
ath_draintxq(struct ath_softc *sc)
{
	struct ath_hal *ah = sc->sc_ah;
	int i;

	/* XXX return value */
	if (!sc->sc_invalid) {
		(void) ath_hal_stoptxdma(ah, sc->sc_bhalq);
		DPRINTF(sc, ATH_DEBUG_RESET, "%s: beacon queue 0x%x\n",
			__func__, ath_hal_gettxbuf(ah, sc->sc_bhalq));
		for (i = 0; i < HAL_NUM_TX_QUEUES; i++)
			if (ATH_TXQ_SETUP(sc, i))
				ath_tx_stopdma(sc, &sc->sc_txq[i]);
	}
	sc->sc_dev->trans_start = jiffies;
	netif_start_queue(sc->sc_dev);		/* XXX move to callers */
	for (i = 0; i < HAL_NUM_TX_QUEUES; i++)
		if (ATH_TXQ_SETUP(sc, i))
			ath_tx_draintxq(sc, &sc->sc_txq[i]);
}

/*
 * Disable the receive h/w in preparation for a reset.
 */
static void
ath_stoprecv(struct ath_softc *sc)
{
#define	PA2DESC(_sc, _pa) \
	((struct ath_desc *)((caddr_t)(_sc)->sc_rxdma.dd_desc + \
		((_pa) - (_sc)->sc_rxdma.dd_desc_paddr)))
	struct ath_hal *ah = sc->sc_ah;
	u_int64_t tsf;

	ath_hal_stoppcurecv(ah);	/* disable PCU */
	ath_hal_setrxfilter(ah, 0);	/* clear recv filter */
	ath_hal_stopdmarecv(ah);	/* disable DMA engine */
	mdelay(3);			/* 3 ms is long enough for 1 frame */
	tsf = ath_hal_gettsf64(ah);
#ifdef AR_DEBUG
	if (sc->sc_debug & (ATH_DEBUG_RESET | ATH_DEBUG_FATAL)) {
		struct ath_buf *bf;

		printk("ath_stoprecv: rx queue 0x%x, link %p\n",
			ath_hal_getrxbuf(ah), sc->sc_rxlink);
		STAILQ_FOREACH(bf, &sc->sc_rxbuf, bf_list) {
			struct ath_desc *ds = bf->bf_desc;
			HAL_STATUS status = ath_hal_rxprocdesc(ah, ds,
				bf->bf_daddr, PA2DESC(sc, ds->ds_link), tsf);
			if (status == HAL_OK || (sc->sc_debug & ATH_DEBUG_FATAL))
				ath_printrxbuf(bf, status == HAL_OK);
		}
	}
#endif
	sc->sc_rxlink = NULL;		/* just in case */
#undef PA2DESC
}

/*
 * Enable the receive h/w following a reset.
 */
static int
ath_startrecv(struct ath_softc *sc)
{
	struct ath_hal *ah = sc->sc_ah;
	struct net_device *dev = sc->sc_dev;
	struct ath_buf *bf;

	/*
	 * Cisco's VPN software requires that drivers be able to
	 * receive encapsulated frames that are larger than the MTU.
	 * Since we can't be sure how large a frame we'll get, setup
	 * to handle the larges on possible.
	 */
#ifdef ATH_SUPERG_FF
	sc->sc_rxbufsize = roundup(ATH_FF_MAX_LEN, sc->sc_cachelsz);
#else
	sc->sc_rxbufsize = roundup(IEEE80211_MAX_LEN, sc->sc_cachelsz);
#endif
	DPRINTF(sc,ATH_DEBUG_RESET, "%s: mtu %u cachelsz %u rxbufsize %u\n",
		__func__, dev->mtu, sc->sc_cachelsz, sc->sc_rxbufsize);

	sc->sc_rxlink = NULL;
	STAILQ_FOREACH(bf, &sc->sc_rxbuf, bf_list) {
		int error = ath_rxbuf_init(sc, bf);
		ATH_RXBUF_RESET(bf);
		if (error < 0)
			return error;
	}

	sc->sc_rxbufcur = NULL;

	bf = STAILQ_FIRST(&sc->sc_rxbuf);
	ath_hal_putrxbuf(ah, bf->bf_daddr);
	ath_hal_rxena(ah);		/* enable recv descriptors */
	ath_mode_init(dev);		/* set filters, etc. */
	ath_hal_startpcurecv(ah);	/* re-enable PCU/DMA engine */
	return 0;
}

/*
 * Flush skb's allocate for receive.
 */
static void
ath_flushrecv(struct ath_softc *sc)
{
	struct ath_buf *bf;

	STAILQ_FOREACH(bf, &sc->sc_rxbuf, bf_list)
		if (bf->bf_skb != NULL) {
			bus_unmap_single(sc->sc_bdev,
				bf->bf_skbaddr, sc->sc_rxbufsize,
				BUS_DMA_FROMDEVICE);
			dev_kfree_skb(bf->bf_skb);
			bf->bf_skb = NULL;
		}
}

/*
 * Update internal state after a channel change.
 */
static void
ath_chan_change(struct ath_softc *sc, struct ieee80211_channel *chan)
{
	struct ieee80211com *ic = &sc->sc_ic;
	struct net_device *dev = sc->sc_dev;
	enum ieee80211_phymode mode;

	mode = ieee80211_chan2mode(chan);

	ath_rate_setup(dev, mode);
	ath_setcurmode(sc, mode);

#ifdef notyet
	/*
	 * Update BPF state.
	 */
	sc->sc_tx_th.wt_chan_freq = sc->sc_rx_th.wr_chan_freq =
		htole16(chan->ic_freq);
	sc->sc_tx_th.wt_chan_flags = sc->sc_rx_th.wr_chan_flags =
		htole16(chan->ic_flags);
#endif
	if (ic->ic_curchanmaxpwr == 0)
		ic->ic_curchanmaxpwr = chan->ic_maxregpower;
}

/*
 * Set/change channels.  If the channel is really being changed,
 * it's done by resetting the chip.  To accomplish this we must
 * first cleanup any pending DMA, then restart stuff after a la
 * ath_init.
 */
static int
ath_chan_set(struct ath_softc *sc, struct ieee80211_channel *chan)
{
	struct ath_hal *ah = sc->sc_ah;
	struct ieee80211com *ic = &sc->sc_ic;
	struct net_device *dev = sc->sc_dev;
	HAL_CHANNEL hchan;
	u_int8_t tswitch = 0;

	/*
	 * Convert to a HAL channel description with
	 * the flags constrained to reflect the current
	 * operating mode.
	 */
	hchan.channel = chan->ic_freq;
	hchan.channelFlags = ath_chan2flags(chan);
	KASSERT(hchan.channel != 0,
		("bogus channel %u/0x%x", hchan.channel, hchan.channelFlags));

	DPRINTF(sc, ATH_DEBUG_RESET, "%s: %u (%u MHz) -> %u (%u MHz)\n",
		__func__, ath_hal_mhz2ieee(ah, sc->sc_curchan.channel,
		sc->sc_curchan.channelFlags), sc->sc_curchan.channel,
		ath_hal_mhz2ieee(ah, hchan.channel, hchan.channelFlags),
		hchan.channel);
	/* check if it is turbo mode switch */
	if (hchan.channel == sc->sc_curchan.channel &&
	   (hchan.channelFlags & IEEE80211_CHAN_TURBO) != (sc->sc_curchan.channelFlags & IEEE80211_CHAN_TURBO)) 
		tswitch = 1;
	if (hchan.channel != sc->sc_curchan.channel ||
	    hchan.channelFlags != sc->sc_curchan.channelFlags) {
		HAL_STATUS status;

		/*
		 * To switch channels clear any pending DMA operations;
		 * wait long enough for the RX fifo to drain, reset the
		 * hardware at the new frequency, and then re-enable
		 * the relevant bits of the h/w.
		 */
		ath_hal_intrset(ah, 0);	/* disable interrupts */
		ath_draintxq(sc);	/* clear pending tx frames */
		ath_stoprecv(sc);	/* turn off frame recv */
		
		/* Set coverage class */
		if (sc->sc_scanning || !IEEE80211_IS_CHAN_A(chan))
			ath_hal_setcoverageclass(sc->sc_ah, 0, 0);
		else
			ath_hal_setcoverageclass(sc->sc_ah, ic->ic_coverageclass, 0);

		if (!ath_hal_reset(ah, sc->sc_opmode, &hchan, AH_TRUE, &status)) {
			printk("%s: %s: unable to reset channel %u (%u MHz) "
				"flags 0x%x '%s' (HAL status %u)\n",
				dev->name, __func__,
				ieee80211_chan2ieee(ic, chan), chan->ic_freq,
			        hchan.channelFlags,
				ath_get_hal_status_desc(status), status);
			return -EIO;
		}

		if (sc->sc_softled)
			ath_hal_gpioCfgOutput(ah, sc->sc_ledpin);
		
		/* Turn off Interference Mitigation in non-STA modes */
		if ((sc->sc_opmode != HAL_M_STA) && sc->sc_hasintmit && !sc->sc_useintmit) {
			DPRINTF(sc, ATH_DEBUG_RESET,
				"%s: disabling interference mitigation (ANI)\n", __func__);
			ath_hal_setintmit(ah, 0);
		}
		sc->sc_curchan = hchan;
		ath_update_txpow(sc);		/* update tx power state */

		/*
		 * Re-enable rx framework.
		 */
		if (ath_startrecv(sc) != 0) {
			printk("%s: %s: unable to restart recv logic\n",
				dev->name, __func__);
			return -EIO;
		}

		/*
		 * Change channels and update the h/w rate map
		 * if we're switching; e.g. 11a to 11b/g.
		 */
		ath_chan_change(sc, chan);
		if (ic->ic_opmode == IEEE80211_M_HOSTAP) {
			if (sc->sc_curchan.privFlags & CHANNEL_DFS) {
				if (!(sc->sc_curchan.privFlags & CHANNEL_DFS_CLEAR)) { 
					dev->watchdog_timeo = 120 * HZ;	/* set the timeout to normal */
					netif_stop_queue(dev);			
					if (sc->sc_dfswait)
						del_timer_sync(&sc->sc_dfswaittimer);
					DPRINTF(sc, ATH_DEBUG_STATE, "%s: %s: start dfs wait period\n",
						__func__, dev->name);
					sc->sc_dfswait = 1;
					sc->sc_dfswaittimer.function = ath_check_dfs_clear;
					sc->sc_dfswaittimer.expires = 
						jiffies + (ATH_DFS_WAIT_POLL_PERIOD * HZ);
					sc->sc_dfswaittimer.data = (unsigned long)sc;
					add_timer(&sc->sc_dfswaittimer);
				}
			} else
				if (sc->sc_dfswait == 1)
					mod_timer(&sc->sc_dfswaittimer, jiffies + 2);
		}
		/*
		 * re configure beacons when it is a turbo mode switch.
		 * HW seems to turn off beacons during turbo mode switch.
		 */
		if (sc->sc_beacons && tswitch) 
			ath_beacon_config(sc, NULL);	

		/*
		 * Re-enable interrupts.
		 */
		ath_hal_intrset(ah, sc->sc_imask);
	}
	return 0;
}

/*
 * Periodically recalibrate the PHY to account
 * for temperature/environment changes.
 */
static void
ath_calibrate(unsigned long arg)
{
	struct net_device *dev = (struct net_device *) arg;
	struct ath_softc *sc = dev->priv;
	struct ath_hal *ah = sc->sc_ah;
	struct ieee80211com *ic = &sc->sc_ic;
	HAL_CHANNEL *chans;
	u_int32_t nchans;
	HAL_BOOL isIQdone = AH_FALSE;

	sc->sc_stats.ast_per_cal++;

	DPRINTF(sc, ATH_DEBUG_CALIBRATE, "%s: channel %u/%x\n",
		__func__, sc->sc_curchan.channel, sc->sc_curchan.channelFlags);

	if (ath_hal_getrfgain(ah) == HAL_RFGAIN_NEED_CHANGE) {
		/*
		 * Rfgain is out of bounds, reset the chip
		 * to load new gain values.
		 */
		sc->sc_stats.ast_per_rfgain++;
		ath_reset(dev);
	}
	if (!ath_hal_calibrate(ah, &sc->sc_curchan, &isIQdone)) {
		DPRINTF(sc, ATH_DEBUG_ANY,
			"%s: calibration of channel %u failed\n",
			__func__, sc->sc_curchan.channel);
		sc->sc_stats.ast_per_calfail++;
	}
	if (ic->ic_opmode == IEEE80211_M_HOSTAP) {
		chans = kmalloc(IEEE80211_CHAN_MAX * sizeof(HAL_CHANNEL), GFP_ATOMIC);
		if (chans == NULL) {
			printk("%s: unable to allocate channel table\n", dev->name);
			return;
		}
		nchans = ath_hal_checknol(ah, chans, IEEE80211_CHAN_MAX);
		if (nchans > 0) {
			u_int32_t i, j;
			struct ieee80211_channel *ichan;
			
			for (i = 0; i < nchans; i++) {
				for (j = 0; j < ic->ic_nchans; j++) {
					ichan = &ic->ic_channels[j];
					if (chans[i].channel == ichan->ic_freq)
						ichan->ic_flags &= ~IEEE80211_CHAN_RADAR;
				}

				ichan = ieee80211_find_channel(ic, chans[i].channel,
					chans[i].channelFlags);
				if (ichan != NULL)
					ichan->ic_flags &= ~IEEE80211_CHAN_RADAR;
			}
		}
		kfree(chans);
	}

	if (isIQdone == AH_TRUE)
		ath_calinterval = ATH_LONG_CALINTERVAL;
	else
		ath_calinterval = ATH_SHORT_CALINTERVAL;

	sc->sc_cal_ch.expires = jiffies + (ath_calinterval * HZ);
	add_timer(&sc->sc_cal_ch);
}

static void
ath_scan_start(struct ieee80211com *ic)
{
	struct net_device *dev = ic->ic_dev;
	struct ath_softc *sc = dev->priv;
	struct ath_hal *ah = sc->sc_ah;
	u_int32_t rfilt;

	/* XXX calibration timer? */

	sc->sc_scanning = 1;
	sc->sc_syncbeacon = 0;
	rfilt = ath_calcrxfilter(sc);
	ath_hal_setrxfilter(ah, rfilt);
	ath_hal_setassocid(ah, dev->broadcast, 0);

	DPRINTF(sc, ATH_DEBUG_STATE, "%s: RX filter 0x%x bssid %s aid 0\n",
		 __func__, rfilt, ether_sprintf(dev->broadcast));
}

static void
ath_scan_end(struct ieee80211com *ic)
{
	struct net_device *dev = ic->ic_dev;
	struct ath_softc *sc = dev->priv;
	struct ath_hal *ah = sc->sc_ah;
	u_int32_t rfilt;

	sc->sc_scanning = 0;
	rfilt = ath_calcrxfilter(sc);
	ath_hal_setrxfilter(ah, rfilt);
	ath_hal_setassocid(ah, sc->sc_curbssid, sc->sc_curaid);

	DPRINTF(sc, ATH_DEBUG_STATE, "%s: RX filter 0x%x bssid %s aid 0x%x\n",
		 __func__, rfilt, ether_sprintf(sc->sc_curbssid),
		 sc->sc_curaid);
}

static void
ath_set_channel(struct ieee80211com *ic)
{
	struct net_device *dev = ic->ic_dev;
	struct ath_softc *sc = dev->priv;

	(void) ath_chan_set(sc, ic->ic_curchan);
	/*
	 * If we are returning to our bss channel then mark state
	 * so the next recv'd beacon's tsf will be used to sync the
	 * beacon timers.  Note that since we only hear beacons in
	 * sta/ibss mode this has no effect in other operating modes.
	 */
	if (!sc->sc_scanning && ic->ic_curchan == ic->ic_bsschan)
		sc->sc_syncbeacon = 1;
}

static void
ath_set_coverageclass(struct ieee80211com *ic) 
{
	struct ath_softc *sc = ic->ic_dev->priv;

	ath_hal_setcoverageclass(sc->sc_ah, ic->ic_coverageclass, 0);
	
	return;
}

static u_int
ath_mhz2ieee(struct ieee80211com *ic, u_int freq, u_int flags)
{
	struct ath_softc *sc = ic->ic_dev->priv;

 	return (ath_hal_mhz2ieee(sc->sc_ah, freq, flags));
}


/*
 * Context: softIRQ and process context
 */
static int
ath_newstate(struct ieee80211vap *vap, enum ieee80211_state nstate, int arg)
{
	struct ath_vap *avp = ATH_VAP(vap);
	struct ieee80211com *ic = vap->iv_ic;
	struct net_device *dev = ic->ic_dev;
	struct ath_softc *sc = dev->priv;
	struct ath_hal *ah = sc->sc_ah;
	struct ieee80211_node *ni, *wds_ni;
	int i, error, stamode;
	u_int32_t rfilt = 0;
	struct ieee80211vap *tmpvap;
	static const HAL_LED_STATE leds[] = {
		HAL_LED_INIT,	/* IEEE80211_S_INIT */
		HAL_LED_SCAN,	/* IEEE80211_S_SCAN */
		HAL_LED_AUTH,	/* IEEE80211_S_AUTH */
		HAL_LED_ASSOC, 	/* IEEE80211_S_ASSOC */
		HAL_LED_RUN, 	/* IEEE80211_S_RUN */
	};

	DPRINTF(sc, ATH_DEBUG_STATE, "%s: %s: %s -> %s\n", __func__, dev->name,
		ieee80211_state_name[vap->iv_state],
		ieee80211_state_name[nstate]);

	del_timer(&sc->sc_cal_ch);		/* periodic calibration timer */
	ath_hal_setledstate(ah, leds[nstate]);	/* set LED */
	netif_stop_queue(dev);			/* before we do anything else */

	if (nstate == IEEE80211_S_INIT) {
		/*
		 * if there is no VAP left in RUN state
		 * disable beacon interrupts.
		 */
		TAILQ_FOREACH(tmpvap, &ic->ic_vaps, iv_next) {
			if (tmpvap != vap && tmpvap->iv_state == IEEE80211_S_RUN )
				break;
		}
		if (!tmpvap) {
			sc->sc_imask &= ~(HAL_INT_SWBA | HAL_INT_BMISS);
			/*
			 * Disable interrupts.
			 */
			ath_hal_intrset(ah, sc->sc_imask &~ HAL_INT_GLOBAL);
			sc->sc_beacons = 0;
		}
		/*
		 * Notify the rate control algorithm.
		 */
		sc->sc_rc->ops->newstate(vap, nstate);
		goto done;
	}
	ni = vap->iv_bss;

	rfilt = ath_calcrxfilter(sc);
	stamode = (vap->iv_opmode == IEEE80211_M_STA ||
		   vap->iv_opmode == IEEE80211_M_IBSS ||
		   vap->iv_opmode == IEEE80211_M_AHDEMO);
	if (stamode && nstate == IEEE80211_S_RUN) {
		sc->sc_curaid = ni->ni_associd;
		IEEE80211_ADDR_COPY(sc->sc_curbssid, ni->ni_bssid);
	} else
		sc->sc_curaid = 0;

	DPRINTF(sc, ATH_DEBUG_STATE, "%s: RX filter 0x%x bssid %s aid 0x%x\n",
		 __func__, rfilt, ether_sprintf(sc->sc_curbssid),
		 sc->sc_curaid);

	ath_hal_setrxfilter(ah, rfilt);
	if (stamode)
		ath_hal_setassocid(ah, sc->sc_curbssid, sc->sc_curaid);

	if ((vap->iv_opmode != IEEE80211_M_STA) &&
		 (vap->iv_flags & IEEE80211_F_PRIVACY)) {
		for (i = 0; i < IEEE80211_WEP_NKID; i++)
			if (ath_hal_keyisvalid(ah, i))
				ath_hal_keysetmac(ah, i, ni->ni_bssid);
	}

	/*
	 * Notify the rate control algorithm so rates
	 * are setup should ath_beacon_alloc be called.
	 */
	sc->sc_rc->ops->newstate(vap, nstate);

	if (vap->iv_opmode == IEEE80211_M_MONITOR) {
		/* nothing to do */;
	} else if (nstate == IEEE80211_S_RUN) {
		DPRINTF(sc, ATH_DEBUG_STATE,
			"%s(RUN): ic_flags=0x%08x iv=%d bssid=%s "
			"capinfo=0x%04x chan=%d\n"
			 , __func__
			 , vap->iv_flags
			 , ni->ni_intval
			 , ether_sprintf(ni->ni_bssid)
			 , ni->ni_capinfo
			 , ieee80211_chan2ieee(ic, ni->ni_chan));

		switch (vap->iv_opmode) {
		case IEEE80211_M_HOSTAP:
		case IEEE80211_M_IBSS:
			/*
			 * Allocate and setup the beacon frame.
			 *
			 * Stop any previous beacon DMA.  This may be
			 * necessary, for example, when an ibss merge
			 * causes reconfiguration; there will be a state
			 * transition from RUN->RUN that means we may
			 * be called with beacon transmission active.
			 */
			ath_hal_stoptxdma(ah, sc->sc_bhalq);

        		/* Set default key index for static wep case */
			ni->ni_ath_defkeyindex = IEEE80211_INVAL_DEFKEY;
			if (((vap->iv_flags & IEEE80211_F_WPA) == 0) &&
			    (ni->ni_authmode != IEEE80211_AUTH_8021X) &&
			    (vap->iv_def_txkey != IEEE80211_KEYIX_NONE)) {
                       		ni->ni_ath_defkeyindex = vap->iv_def_txkey;
			}

			error = ath_beacon_alloc(sc, ni);
			if (error < 0)
				goto bad;
			/* 
			 * if the turbo flags have changed, then beacon and turbo
			 * need to be reconfigured.
			 */
			if ((sc->sc_dturbo && !(vap->iv_ath_cap & IEEE80211_ATHC_TURBOP)) || 
				(!sc->sc_dturbo && (vap->iv_ath_cap & IEEE80211_ATHC_TURBOP))) 
				sc->sc_beacons = 0;
			/* 
			 * if it is the first AP VAP moving to RUN state then beacon 
			 * needs to be reconfigured.
			 */
			TAILQ_FOREACH(tmpvap, &ic->ic_vaps, iv_next) {
				if (tmpvap != vap && tmpvap->iv_state == IEEE80211_S_RUN &&
					tmpvap->iv_opmode == IEEE80211_M_HOSTAP)
					break;
			}
			if (!tmpvap) 
				sc->sc_beacons = 0;
			break;
		case IEEE80211_M_STA:
#ifdef ATH_SUPERG_COMP
			/* have we negotiated compression? */
			if (!(vap->iv_ath_cap & ni->ni_ath_flags & IEEE80211_NODE_COMP))
				ni->ni_ath_flags &= ~IEEE80211_NODE_COMP;
#endif
			/*
			 * Allocate a key cache slot to the station.
			 */
			ath_setup_keycacheslot(sc, ni);
			/*
			 * Record negotiated dynamic turbo state for
			 * use by rate control modules.
			 */
			sc->sc_dturbo =
				(ni->ni_ath_flags & IEEE80211_ATHC_TURBOP) != 0;
			break;
		case IEEE80211_M_WDS:
			wds_ni = ieee80211_find_txnode(vap, vap->wds_mac);
			if (wds_ni) {
				/* XXX no rate negotiation; just dup */
				wds_ni->ni_rates = vap->iv_bss->ni_rates;
				/* Depending on the sequence of bringing up devices
				 * it's possible the rates of the root bss isn't
				 * filled yet. 
				 */
				if (vap->iv_ic->ic_newassoc != NULL && 
				    wds_ni->ni_rates.rs_nrates != 0) {
					/* Fill in the rates based on our own rates
					 * we rely on the rate selection mechanism
					 * to find out which rates actually work!
					 */
					vap->iv_ic->ic_newassoc(wds_ni, 1);
				}
			}
			break;
		default:
			break;
		}


		/*
		 * Configure the beacon and sleep timers.
		 */
		if (!sc->sc_beacons && vap->iv_opmode!=IEEE80211_M_WDS) {
			ath_beacon_config(sc, vap);
			sc->sc_beacons = 1;
		}

		/*
		 * Reset rssi stats; maybe not the best place...
		 */
		sc->sc_halstats.ns_avgbrssi = ATH_RSSI_DUMMY_MARKER;
		sc->sc_halstats.ns_avgrssi = ATH_RSSI_DUMMY_MARKER;
		sc->sc_halstats.ns_avgtxrssi = ATH_RSSI_DUMMY_MARKER;
		/* 
		 * if it is a DFS channel and has not been checked for radar 
		 * do not let the 80211 state machine to go to RUN state.
		 *
		 */
		if (sc->sc_dfswait && vap->iv_opmode == IEEE80211_M_HOSTAP ) {
			/* push the VAP to RUN state once DFS is cleared */
			DPRINTF(sc, ATH_DEBUG_STATE, "%s: %s: VAP  -> DFS_WAIT\n",
				__func__, dev->name);
			avp->av_dfswait_run = 1; 
			return 0;
		}
	} else {
		if (sc->sc_dfswait &&
			vap->iv_opmode == IEEE80211_M_HOSTAP &&
			sc->sc_dfswaittimer.data == (unsigned long)vap) {
			del_timer_sync(&sc->sc_dfswaittimer);
			sc->sc_dfswait = 0;
			DPRINTF(sc, ATH_DEBUG_STATE, "%s: %s: VAP  out of DFS_WAIT\n",
				__func__, dev->name);
		}
		/*
		 *  XXXX
		 * if it is SCAN state, disable beacons. 
		 */
		if (nstate == IEEE80211_S_SCAN) {
			ath_hal_intrset(ah,sc->sc_imask &~ (HAL_INT_SWBA | HAL_INT_BMISS));
			sc->sc_imask &= ~(HAL_INT_SWBA | HAL_INT_BMISS);
			/* need to reconfigure the beacons when it moves to RUN */
			sc->sc_beacons = 0; 
		}
		avp->av_dfswait_run = 0; /* reset the dfs wait flag */ 
	}
done:
	/*
	 * Invoke the parent method to complete the work.
	 */
	error = avp->av_newstate(vap, nstate, arg);

	/*
	 * Finally, start any timers.
	 */
	if (nstate == IEEE80211_S_RUN) {
		/* start periodic recalibration timer */
		mod_timer(&sc->sc_cal_ch, jiffies + (ath_calinterval * HZ));
	}

#ifdef ATH_SUPERG_XR
	if (vap->iv_flags & IEEE80211_F_XR &&
		nstate == IEEE80211_S_RUN)
		ATH_SETUP_XR_VAP(sc,vap,rfilt);
	if (vap->iv_flags & IEEE80211_F_XR &&
		nstate == IEEE80211_S_INIT && sc->sc_xrgrppoll)
		ath_grppoll_stop(vap);
#endif
bad:
	netif_start_queue(dev);
	dev->watchdog_timeo = 5 * HZ;		/* set the timeout to normal */
	return error;
}

/*
 * periodically checks for the HAL to set
 * CHANNEL_DFS_CLEAR flag on current channel.
 * if the flag is set and a VAP is waiting for it, push 
 * transition the VAP to RUN state.
 *
 * Context: Timer (softIRQ)
 */
static void 
ath_check_dfs_clear(unsigned long data ) 
{
	struct ath_softc *sc = (struct ath_softc *)data; 
	struct ieee80211com *ic = &sc->sc_ic;
	struct net_device *dev = sc->sc_dev;
	struct ieee80211vap *vap ;
	HAL_CHANNEL hchan;

	if(!sc->sc_dfswait) return;

	/* if still need to wait */
	ath_hal_radar_wait(sc->sc_ah, &hchan);

	if (hchan.privFlags & CHANNEL_INTERFERENCE)
		return; 

	if ((hchan.privFlags & CHANNEL_DFS_CLEAR) ||
	    (!(hchan.privFlags & CHANNEL_DFS))) { 
		sc->sc_curchan.privFlags |= CHANNEL_DFS_CLEAR;
		sc->sc_dfswait = 0;
		TAILQ_FOREACH(vap, &ic->ic_vaps, iv_next) {
			struct ath_vap *avp = ATH_VAP(vap);
			if (avp->av_dfswait_run) {
				/* re alloc beacons to update new channel info */
				int error;
				error = ath_beacon_alloc(sc, vap->iv_bss);
				if(error < 0) {
					/* XXX */
					return;
				}
				DPRINTF(sc, ATH_DEBUG_STATE, "%s: %s: VAP DFS_WAIT -> RUN\n",
					__func__, dev->name);
				avp->av_newstate(vap, IEEE80211_S_RUN, 0);
				/* start calibration timer */
				mod_timer(&sc->sc_cal_ch, jiffies + (ath_calinterval * HZ));
#ifdef ATH_SUPERG_XR
				if (vap->iv_flags & IEEE80211_F_XR ) {
					u_int32_t rfilt = 0;
					rfilt = ath_calcrxfilter(sc);
					ATH_SETUP_XR_VAP(sc, vap, rfilt);
				}
#endif
				avp->av_dfswait_run = 0;
			}
		}
		/* start the device */
		netif_start_queue(dev);
		dev->watchdog_timeo = 5 * HZ;	/* set the timeout to normal */
	} else {
		/* fire the timer again */
		sc->sc_dfswaittimer.expires = jiffies + (ATH_DFS_WAIT_POLL_PERIOD * HZ);
		sc->sc_dfswaittimer.data = (unsigned long)sc;
		add_timer(&sc->sc_dfswaittimer);
	}

}

#ifdef ATH_SUPERG_COMP
/* Enable/Disable de-compression mask for given node.
 * The routine is invoked after addition or deletion of the
 * key.
 */
static void
ath_comp_set(struct ieee80211vap *vap, struct ieee80211_node *ni, int en)
{
	ath_setup_comp(ni, en);
	return;
}

/* Set up decompression engine for this node. */
static void
ath_setup_comp(struct ieee80211_node *ni, int enable)
{
#define	IEEE80211_KEY_XR	(IEEE80211_KEY_XMIT | IEEE80211_KEY_RECV)
	struct ieee80211vap *vap = ni->ni_vap;
	struct ath_softc *sc = vap->iv_ic->ic_dev->priv;
	struct ath_node *an = ATH_NODE(ni);
	u_int16_t keyindex;

	if (enable) {
		/* Have we negotiated compression? */
		if (!(ni->ni_ath_flags & IEEE80211_NODE_COMP))
			return;

		/* No valid key? */
		if (ni->ni_ucastkey.wk_keyix == IEEE80211_KEYIX_NONE)
			return;

		/* Setup decompression mask.
		 * For TKIP and split MIC case, recv. keyindex is at 32 offset
		 * from tx key.
		 */
		if ((ni->ni_wpa_ie != NULL) &&
		    (ni->ni_rsn.rsn_ucastcipher == IEEE80211_CIPHER_TKIP) &&
		    sc->sc_splitmic) {
			if ((ni->ni_ucastkey.wk_flags & IEEE80211_KEY_XR) 
							== IEEE80211_KEY_XR)
				keyindex = ni->ni_ucastkey.wk_keyix + 32;
			else
				keyindex = ni->ni_ucastkey.wk_keyix;
		} else
			keyindex = ni->ni_ucastkey.wk_keyix + ni->ni_rxkeyoff;

		ath_hal_setdecompmask(sc->sc_ah, keyindex, 1);
		an->an_decomp_index = keyindex;
	} else {
		if (an->an_decomp_index != INVALID_DECOMP_INDEX) {
			ath_hal_setdecompmask(sc->sc_ah, an->an_decomp_index, 0);
			an->an_decomp_index = INVALID_DECOMP_INDEX;
		}
	}

	return;
#undef IEEE80211_KEY_XR
}
#endif

/*
 * Allocate a key cache slot to the station so we can
 * setup a mapping from key index to node. The key cache
 * slot is needed for managing antenna state and for
 * compression when stations do not use crypto.  We do
 * it unilaterally here; if crypto is employed this slot
 * will be reassigned.
 */
static void
ath_setup_stationkey(struct ieee80211_node *ni)
{
	struct ieee80211vap *vap = ni->ni_vap;
	struct ath_softc *sc = vap->iv_ic->ic_dev->priv;
	u_int16_t keyix;

	keyix = ath_key_alloc(vap, &ni->ni_ucastkey);
	if (keyix == IEEE80211_KEYIX_NONE) {
		/*
		 * Key cache is full; we'll fall back to doing
		 * the more expensive lookup in software.  Note
		 * this also means no h/w compression.
		 */
		/* XXX msg+statistic */
		return;
	} else {
		ni->ni_ucastkey.wk_keyix = keyix;
		/* NB: this will create a pass-thru key entry */
		ath_keyset(sc, &ni->ni_ucastkey, ni->ni_macaddr, vap->iv_bss);

#ifdef ATH_SUPERG_COMP
		/* Enable de-compression logic */
		ath_setup_comp(ni, 1);
#endif
	}
	
	return;
}

/* Setup WEP key for the station if compression is negotiated.
 * When station and AP are using same default key index, use single key
 * cache entry for receive and transmit, else two key cache entries are
 * created. One for receive with MAC address of station and one for transmit
 * with NULL mac address. On receive key cache entry de-compression mask
 * is enabled.
 */
static void
ath_setup_stationwepkey(struct ieee80211_node *ni)
{
	struct ieee80211vap *vap = ni->ni_vap;
	struct ieee80211_key *ni_key;
	struct ieee80211_key tmpkey;
	struct ieee80211_key *rcv_key, *xmit_key;
	int txkeyidx, rxkeyidx = IEEE80211_KEYIX_NONE, i;
	u_int8_t null_macaddr[IEEE80211_ADDR_LEN] = {0, 0, 0, 0, 0, 0};

	KASSERT(ni->ni_ath_defkeyindex < IEEE80211_WEP_NKID,
		("got invalid node key index 0x%x", ni->ni_ath_defkeyindex));
	KASSERT(vap->iv_def_txkey < IEEE80211_WEP_NKID,
		("got invalid vap def key index 0x%x", vap->iv_def_txkey));

	/* Allocate a key slot first */
	if (!ieee80211_crypto_newkey(vap, 
		IEEE80211_CIPHER_WEP, 
		IEEE80211_KEY_XMIT|IEEE80211_KEY_RECV, 
		&ni->ni_ucastkey))
		goto error;

	txkeyidx = ni->ni_ucastkey.wk_keyix;
	xmit_key = &vap->iv_nw_keys[vap->iv_def_txkey];

	/* Do we need separate rx key? */
	if (ni->ni_ath_defkeyindex != vap->iv_def_txkey) {
		ni->ni_ucastkey.wk_keyix = IEEE80211_KEYIX_NONE;
		if (!ieee80211_crypto_newkey(vap, 
			IEEE80211_CIPHER_WEP, 
			IEEE80211_KEY_XMIT|IEEE80211_KEY_RECV,
			&ni->ni_ucastkey)) {
			ni->ni_ucastkey.wk_keyix = txkeyidx;
			ieee80211_crypto_delkey(vap, &ni->ni_ucastkey, ni);
			goto error;
		}
		rxkeyidx = ni->ni_ucastkey.wk_keyix;
		ni->ni_ucastkey.wk_keyix = txkeyidx;

		rcv_key = &vap->iv_nw_keys[ni->ni_ath_defkeyindex];
	} else {
		rcv_key = xmit_key;
		rxkeyidx = txkeyidx;
	}

	/* Remember receive key offset */
	ni->ni_rxkeyoff = rxkeyidx - txkeyidx;

	/* Setup xmit key */
	ni_key = &ni->ni_ucastkey;
	if (rxkeyidx != txkeyidx)
		ni_key->wk_flags = IEEE80211_KEY_XMIT;
	else
		ni_key->wk_flags = IEEE80211_KEY_XMIT|IEEE80211_KEY_RECV;

	ni_key->wk_keylen = xmit_key->wk_keylen;
	for (i = 0; i < IEEE80211_TID_SIZE; i++)
		ni_key->wk_keyrsc[i] = xmit_key->wk_keyrsc[i];
	ni_key->wk_keytsc = 0; 
	memset(ni_key->wk_key, 0, sizeof(ni_key->wk_key));
	memcpy(ni_key->wk_key, xmit_key->wk_key, xmit_key->wk_keylen);
	ieee80211_crypto_setkey(vap, &ni->ni_ucastkey, 
		(rxkeyidx == txkeyidx) ? ni->ni_macaddr:null_macaddr, ni);

	if (rxkeyidx != txkeyidx) {
		/* Setup recv key */
		ni_key = &tmpkey;
		ni_key->wk_keyix = rxkeyidx;
		ni_key->wk_flags = IEEE80211_KEY_RECV;
		ni_key->wk_keylen = rcv_key->wk_keylen;
		for(i = 0; i < IEEE80211_TID_SIZE; i++)
			ni_key->wk_keyrsc[i] = rcv_key->wk_keyrsc[i];
		ni_key->wk_keytsc = 0; 
		ni_key->wk_cipher = rcv_key->wk_cipher; 
		ni_key->wk_private = rcv_key->wk_private; 
		memset(ni_key->wk_key, 0, sizeof(ni_key->wk_key));
		memcpy(ni_key->wk_key, rcv_key->wk_key, rcv_key->wk_keylen);
		ieee80211_crypto_setkey(vap, &tmpkey, ni->ni_macaddr, ni);
	}

	return;

error:
	ni->ni_ath_flags &= ~IEEE80211_NODE_COMP;
	return;
}

/* Create a keycache entry for given node in clearcase as well as static wep.
 * Handle compression state if required.
 * For non clearcase/static wep case, the key is plumbed by hostapd.
 */
static void
ath_setup_keycacheslot(struct ath_softc *sc, struct ieee80211_node *ni)
{
	struct ieee80211vap *vap = ni->ni_vap;

	if (ni->ni_ucastkey.wk_keyix != IEEE80211_KEYIX_NONE)
		ieee80211_crypto_delkey(vap, &ni->ni_ucastkey, ni);

	/* Only for clearcase and WEP case */
	if ((vap->iv_flags & IEEE80211_F_PRIVACY) == 0 ||
		(ni->ni_ath_defkeyindex != IEEE80211_INVAL_DEFKEY)) {

		if ((vap->iv_flags & IEEE80211_F_PRIVACY) == 0) {
			KASSERT(ni->ni_ucastkey.wk_keyix == IEEE80211_KEYIX_NONE,
		    		("new node with a ucast key already setup (keyix %u)",
		    		  ni->ni_ucastkey.wk_keyix));
			/* NB: 5210 has no passthru/clr key support */
			if (sc->sc_hasclrkey)
				ath_setup_stationkey(ni);
		} else
			ath_setup_stationwepkey(ni);
	}

	return;
}

/*
 * Setup driver-specific state for a newly associated node.
 * Note that we're called also on a re-associate, the isnew
 * param tells us if this is the first time or not.
 */
static void
ath_newassoc(struct ieee80211_node *ni, int isnew)
{
	struct ieee80211com *ic = ni->ni_ic;
	struct ieee80211vap *vap = ni->ni_vap;
	struct ath_softc *sc = ic->ic_dev->priv;

	sc->sc_rc->ops->newassoc(sc, ATH_NODE(ni), isnew);

	/* are we supporting compression? */
	if (!(vap->iv_ath_cap & ni->ni_ath_flags & IEEE80211_NODE_COMP))
		ni->ni_ath_flags &= ~IEEE80211_NODE_COMP;

	/* disable compression for TKIP */
	if ((ni->ni_ath_flags & IEEE80211_NODE_COMP) &&
		(ni->ni_wpa_ie != NULL) &&
		(ni->ni_rsn.rsn_ucastcipher == IEEE80211_CIPHER_TKIP))
		ni->ni_ath_flags &= ~IEEE80211_NODE_COMP;

	ath_setup_keycacheslot(sc, ni);
#ifdef ATH_SUPERG_XR
	if (1) {
		struct ath_node *an = ATH_NODE(ni);
		if (ic->ic_ath_cap & an->an_node.ni_ath_flags & IEEE80211_ATHC_XR)
			an->an_minffrate = ATH_MIN_FF_RATE;
		else
			an->an_minffrate = 0;
		ath_grppoll_period_update(sc);
	}
#endif
}

static int
ath_getchannels(struct net_device *dev, u_int cc,
	HAL_BOOL outdoor, HAL_BOOL xchanmode)
{
	struct ath_softc *sc = dev->priv;
	struct ieee80211com *ic = &sc->sc_ic;
	struct ath_hal *ah = sc->sc_ah;
	HAL_CHANNEL *chans;
	int i;
	u_int nchan;

	chans = kmalloc(IEEE80211_CHAN_MAX * sizeof(HAL_CHANNEL), GFP_KERNEL);
	if (chans == NULL) {
		printk("%s: unable to allocate channel table\n", dev->name);
		return -ENOMEM;
	}
	if (!ath_hal_init_channels(ah, chans, IEEE80211_CHAN_MAX, &nchan,
	    ic->ic_regclassids, IEEE80211_REGCLASSIDS_MAX, &ic->ic_nregclass,
	    cc, HAL_MODE_ALL, outdoor, xchanmode)) {
		u_int32_t rd;

		ath_hal_getregdomain(ah, &rd);
		printk("%s: unable to collect channel list from HAL; "
			"regdomain likely %u country code %u\n",
			dev->name, rd, cc);
		kfree(chans);
		return -EINVAL;
	}
	/*
	 * Convert HAL channels to ieee80211 ones.
	 */
	for (i = 0; i < nchan; i++) {
		HAL_CHANNEL *c = &chans[i];
		struct ieee80211_channel *ichan = &ic->ic_channels[i];

		ichan->ic_ieee = ath_hal_mhz2ieee(ah, c->channel, c->channelFlags);
		ichan->ic_freq = c->channel;
		ichan->ic_flags = c->channelFlags;
		ichan->ic_maxregpower = c->maxRegTxPower;	/* dBm */
		ichan->ic_maxpower = c->maxTxPower;		    /* 1/4 dBm */
		ichan->ic_minpower = c->minTxPower;		    /* 1/4 dBm */
	}
	ic->ic_nchans = nchan;
	kfree(chans);
	return 0;
}

static void
ath_led_done(unsigned long arg)
{
	struct ath_softc *sc = (struct ath_softc *) arg;

	sc->sc_blinking = 0;
}

/*
 * Turn the LED off: flip the pin and then set a timer so no
 * update will happen for the specified duration.
 */
static void
ath_led_off(unsigned long arg)
{
	struct ath_softc *sc = (struct ath_softc *) arg;

	ath_hal_gpioset(sc->sc_ah, sc->sc_ledpin, !sc->sc_ledon);
	sc->sc_ledtimer.function = ath_led_done;
	sc->sc_ledtimer.expires = jiffies + sc->sc_ledoff;
	add_timer(&sc->sc_ledtimer);
}

/*
 * Blink the LED according to the specified on/off times.
 */
static void
ath_led_blink(struct ath_softc *sc, int on, int off)
{
	DPRINTF(sc, ATH_DEBUG_LED, "%s: on %u off %u\n", __func__, on, off);
	ath_hal_gpioset(sc->sc_ah, sc->sc_ledpin, sc->sc_ledon);
	sc->sc_blinking = 1;
	sc->sc_ledoff = off;
	sc->sc_ledtimer.function = ath_led_off;
	sc->sc_ledtimer.expires = jiffies + on;
	add_timer(&sc->sc_ledtimer);
}

static void
ath_led_event(struct ath_softc *sc, int event)
{

	sc->sc_ledevent = jiffies;	/* time of last event */
	if (sc->sc_blinking)		/* don't interrupt active blink */
		return;
	switch (event) {
	case ATH_LED_POLL:
		ath_led_blink(sc, sc->sc_hwmap[0].ledon,
			sc->sc_hwmap[0].ledoff);
		break;
	case ATH_LED_TX:
		ath_led_blink(sc, sc->sc_hwmap[sc->sc_txrate].ledon,
			sc->sc_hwmap[sc->sc_txrate].ledoff);
		break;
	case ATH_LED_RX:
		ath_led_blink(sc, sc->sc_hwmap[sc->sc_rxrate].ledon,
			sc->sc_hwmap[sc->sc_rxrate].ledoff);
		break;
	}
}

static void
set_node_txpower(void *arg, struct ieee80211_node *ni)
{
	int *value = (int *)arg;
	ni->ni_txpower = *value;
}

/* XXX: this function needs some locking to avoid being called twice/interrupted */
static void
ath_update_txpow(struct ath_softc *sc)
{
	struct ieee80211com *ic = &sc->sc_ic;
	struct ieee80211vap *vap = NULL;
	struct ath_hal *ah = sc->sc_ah;
	u_int32_t txpowlimit = 0;
	u_int32_t maxtxpowlimit = 9999;
	u_int32_t clamped_txpow = 0;

	/*
	 * Find the maxtxpow of the card and regulatory constraints
	 */
	(void)ath_hal_getmaxtxpow(ah, &txpowlimit);
	ath_hal_settxpowlimit(ah, maxtxpowlimit);
	(void)ath_hal_getmaxtxpow(ah, &maxtxpowlimit);
	ic->ic_txpowlimit = maxtxpowlimit;
	ath_hal_settxpowlimit(ah, txpowlimit);
 	
 	/*
	 * Make sure the VAP's change is within limits, clamp it otherwise
 	 */
	if (ic->ic_newtxpowlimit > ic->ic_txpowlimit)
		clamped_txpow = ic->ic_txpowlimit;
	else
		clamped_txpow = ic->ic_newtxpowlimit;
	
	/*
	 * Search for the VAP that needs a txpow change, if any
	 */
	TAILQ_FOREACH(vap, &ic->ic_vaps, iv_next) {
#ifdef ATH_CAP_TPC
		if (ic->ic_newtxpowlimit == vap->iv_bss->ni_txpower) {
			vap->iv_bss->ni_txpower = clamped_txpow;
			ieee80211_iterate_nodes(&vap->iv_ic->ic_sta, set_node_txpower, &clamped_txpow);
		}
#else
		vap->iv_bss->ni_txpower = clamped_txpow;
		ieee80211_iterate_nodes(&vap->iv_ic->ic_sta, set_node_txpower, &clamped_txpow);
#endif
	}
 	
	ic->ic_newtxpowlimit = sc->sc_curtxpow = clamped_txpow;

#ifdef ATH_CAP_TPC
	if (ic->ic_newtxpowlimit >= txpowlimit)
		ath_hal_settxpowlimit(ah, ic->ic_newtxpowlimit);
#else
	if (ic->ic_newtxpowlimit != txpowlimit)
		ath_hal_settxpowlimit(ah, ic->ic_newtxpowlimit);
#endif
}
 

#ifdef ATH_SUPERG_XR
static int
ath_xr_rate_setup(struct net_device *dev)
{
	struct ath_softc *sc = dev->priv;
	struct ath_hal *ah = sc->sc_ah;
	struct ieee80211com *ic = &sc->sc_ic;
	const HAL_RATE_TABLE *rt;
	struct ieee80211_rateset *rs;
	int i, maxrates;
	sc->sc_xr_rates = ath_hal_getratetable(ah, HAL_MODE_XR);
	rt = sc->sc_xr_rates;
	if (rt == NULL)
		return 0;
	if (rt->rateCount > XR_NUM_SUP_RATES) {
		DPRINTF(sc, ATH_DEBUG_ANY,
			"%s: rate table too small (%u > %u)\n",
			__func__, rt->rateCount, IEEE80211_RATE_MAXSIZE);
		maxrates = IEEE80211_RATE_MAXSIZE;
	} else
		maxrates = rt->rateCount;
	rs = &ic->ic_sup_xr_rates;
	for (i = 0; i < maxrates; i++)
		rs->rs_rates[i] = rt->info[i].dot11Rate;
	rs->rs_nrates = maxrates;
	return 1;
}
#endif

/* Setup half/quarter rate table support */
static void
ath_setup_subrates(struct net_device *dev)
{
	struct ath_softc *sc = dev->priv;
	struct ath_hal *ah = sc->sc_ah;
	struct ieee80211com *ic = &sc->sc_ic;
	const HAL_RATE_TABLE *rt;
	struct ieee80211_rateset *rs;
	int i, maxrates;

	sc->sc_half_rates = ath_hal_getratetable(ah, HAL_MODE_11A_HALF_RATE);
	rt = sc->sc_half_rates;
	if (rt != NULL) {
		if (rt->rateCount > IEEE80211_RATE_MAXSIZE) {
			DPRINTF(sc, ATH_DEBUG_ANY,
				"%s: rate table too small (%u > %u)\n",
			       __func__, rt->rateCount, IEEE80211_RATE_MAXSIZE);
			maxrates = IEEE80211_RATE_MAXSIZE;
		} else
			maxrates = rt->rateCount;
		rs = &ic->ic_sup_half_rates;
		for (i = 0; i < maxrates; i++)
			rs->rs_rates[i] = rt->info[i].dot11Rate;
		rs->rs_nrates = maxrates;
	}

	sc->sc_quarter_rates = ath_hal_getratetable(ah, HAL_MODE_11A_QUARTER_RATE);
	rt = sc->sc_quarter_rates;
	if (rt != NULL) {
		if (rt->rateCount > IEEE80211_RATE_MAXSIZE) {
			DPRINTF(sc, ATH_DEBUG_ANY,
				"%s: rate table too small (%u > %u)\n",
			       __func__, rt->rateCount, IEEE80211_RATE_MAXSIZE);
			maxrates = IEEE80211_RATE_MAXSIZE;
		} else
			maxrates = rt->rateCount;
		rs = &ic->ic_sup_quarter_rates;
		for (i = 0; i < maxrates; i++)
			rs->rs_rates[i] = rt->info[i].dot11Rate;
		rs->rs_nrates = maxrates;
	}
}

static int
ath_rate_setup(struct net_device *dev, u_int mode)
{
	struct ath_softc *sc = dev->priv;
	struct ath_hal *ah = sc->sc_ah;
	struct ieee80211com *ic = &sc->sc_ic;
	const HAL_RATE_TABLE *rt;
	struct ieee80211_rateset *rs;
	int i, maxrates;

	switch (mode) {
	case IEEE80211_MODE_11A:
		sc->sc_rates[mode] = ath_hal_getratetable(ah, HAL_MODE_11A);
		break;
	case IEEE80211_MODE_11B:
		sc->sc_rates[mode] = ath_hal_getratetable(ah, HAL_MODE_11B);
		break;
	case IEEE80211_MODE_11G:
		sc->sc_rates[mode] = ath_hal_getratetable(ah, HAL_MODE_11G);
		break;
	case IEEE80211_MODE_TURBO_A:
		sc->sc_rates[mode] = ath_hal_getratetable(ah, HAL_MODE_TURBO);
		break;
	case IEEE80211_MODE_TURBO_G:
		sc->sc_rates[mode] = ath_hal_getratetable(ah, HAL_MODE_108G);
		break;
	default:
		DPRINTF(sc, ATH_DEBUG_ANY, "%s: invalid mode %u\n",
			__func__, mode);
		return 0;
	}
	rt = sc->sc_rates[mode];
	if (rt == NULL)
		return 0;
	if (rt->rateCount > IEEE80211_RATE_MAXSIZE) {
		DPRINTF(sc, ATH_DEBUG_ANY,
			"%s: rate table too small (%u > %u)\n",
			__func__, rt->rateCount, IEEE80211_RATE_MAXSIZE);
		maxrates = IEEE80211_RATE_MAXSIZE;
	} else
		maxrates = rt->rateCount;
	rs = &ic->ic_sup_rates[mode];
	for (i = 0; i < maxrates; i++)
		rs->rs_rates[i] = rt->info[i].dot11Rate;
	rs->rs_nrates = maxrates;
	return 1;
}

static void
ath_setcurmode(struct ath_softc *sc, enum ieee80211_phymode mode)
{
#define	N(a)	((int)(sizeof(a)/sizeof(a[0])))
	/* NB: on/off times from the Atheros NDIS driver, w/ permission */
	static const struct {
		u_int		rate;		/* tx/rx 802.11 rate */
		u_int16_t	timeOn;		/* LED on time (ms) */
		u_int16_t	timeOff;	/* LED off time (ms) */
	} blinkrates[] = {
		{ 108,  40,  10 },
		{  96,  44,  11 },
		{  72,  50,  13 },
		{  48,  57,  14 },
		{  36,  67,  16 },
		{  24,  80,  20 },
		{  22, 100,  25 },
		{  18, 133,  34 },
		{  12, 160,  40 },
		{  10, 200,  50 },
		{   6, 240,  58 },
		{   4, 267,  66 },
		{   2, 400, 100 },
		{   0, 500, 130 },
	};
	const HAL_RATE_TABLE *rt;
	int i, j;

	memset(sc->sc_rixmap, 0xff, sizeof(sc->sc_rixmap));
	rt = sc->sc_rates[mode];
	KASSERT(rt != NULL, ("no h/w rate set for phy mode %u", mode));
	for (i = 0; i < rt->rateCount; i++)
		sc->sc_rixmap[rt->info[i].dot11Rate & IEEE80211_RATE_VAL] = i;
	memset(sc->sc_hwmap, 0, sizeof(sc->sc_hwmap));
	for (i = 0; i < 32; i++) {
		u_int8_t ix = rt->rateCodeToIndex[i];
		if (ix == 0xff) {
			sc->sc_hwmap[i].ledon = msecs_to_jiffies(500);
			sc->sc_hwmap[i].ledoff = msecs_to_jiffies(130);
			continue;
		}
		sc->sc_hwmap[i].ieeerate =
			rt->info[ix].dot11Rate & IEEE80211_RATE_VAL;
		if (rt->info[ix].shortPreamble ||
		    rt->info[ix].phy == IEEE80211_T_OFDM)
			sc->sc_hwmap[i].flags |= IEEE80211_RADIOTAP_F_SHORTPRE;
		/* setup blink rate table to avoid per-packet lookup */
		for (j = 0; j < N(blinkrates) - 1; j++)
			if (blinkrates[j].rate == sc->sc_hwmap[i].ieeerate)
				break;
		/* NB: this uses the last entry if the rate isn't found */
		/* XXX beware of overflow */
		sc->sc_hwmap[i].ledon = msecs_to_jiffies(blinkrates[j].timeOn);
		sc->sc_hwmap[i].ledoff = msecs_to_jiffies(blinkrates[j].timeOff);
	}
	sc->sc_currates = rt;
	sc->sc_curmode = mode;
	/*
	 * All protection frames are transmitted at 2Mb/s for
	 * 11g, otherwise at 1Mb/s.
	 * XXX select protection rate index from rate table.
	 */
	sc->sc_protrix = (mode == IEEE80211_MODE_11G ? 1 : 0);
	/* rate index used to send mgt frames */
	sc->sc_minrateix = 0;
#undef N
}

#ifdef ATH_SUPERG_FF
static u_int32_t
athff_approx_txtime(struct ath_softc *sc, struct ath_node *an, struct sk_buff *skb)
{
	u_int32_t txtime;
	u_int32_t framelen;

	/*
	 * Approximate the frame length to be transmitted. A swag to add
	 * the following maximal values to the skb payload:
	 *   - 32: 802.11 encap + CRC
	 *   - 24: encryption overhead (if wep bit)
	 *   - 4 + 6: fast-frame header and padding
	 *   - 16: 2 LLC FF tunnel headers
	 *   - 14: 1 802.3 FF tunnel header (skb already accounts for 2nd)
	 */
	framelen = skb->len + 32 + 4 + 6 + 16 + 14;
	if (sc->sc_ic.ic_flags & IEEE80211_F_PRIVACY)
		framelen += 24;
	if (an->an_tx_ffbuf[skb->priority])
		framelen += an->an_tx_ffbuf[skb->priority]->bf_skb->len;

	txtime = ath_hal_computetxtime(sc->sc_ah, sc->sc_currates, framelen,
		an->an_prevdatarix, AH_FALSE);

	return txtime;
}
/*
 * Determine if a data frame may be aggregated via ff tunneling.
 *
 *  NB: allowing EAPOL frames to be aggregated with other unicast traffic.
 *      Do 802.1x EAPOL frames proceed in the clear? Then they couldn't
 *      be aggregated with other types of frames when encryption is on?
 *
 *  NB: assumes lock on an_tx_ffbuf effectively held by txq lock mechanism.
 */
static int
athff_can_aggregate(struct ath_softc *sc, struct ether_header *eh,
		    struct ath_node *an, struct sk_buff *skb, u_int16_t fragthreshold, int *flushq)
{
	struct ieee80211com *ic = &sc->sc_ic;
	struct ath_txq *txq = sc->sc_ac2q[skb->priority];
	struct ath_buf *ffbuf = an->an_tx_ffbuf[skb->priority];
	u_int32_t txoplimit;

#define US_PER_4MS 4000
#define	MIN(a,b)	((a) < (b) ? (a) : (b))

	*flushq = AH_FALSE;

	if (fragthreshold < 2346)
	    return AH_FALSE;

	if ((!ffbuf) && (txq->axq_depth < sc->sc_fftxqmin))
		return AH_FALSE;
	if (!(ic->ic_ath_cap & an->an_node.ni_ath_flags & IEEE80211_ATHC_FF))
		return AH_FALSE;
	if (!(ic->ic_opmode == IEEE80211_M_STA ||
		  ic->ic_opmode == IEEE80211_M_HOSTAP))
		return AH_FALSE;
	if ((ic->ic_opmode == IEEE80211_M_HOSTAP) &&
		  ETHER_IS_MULTICAST(eh->ether_dhost))
		return AH_FALSE;

#ifdef ATH_SUPERG_XR
	if (sc->sc_currates->info[an->an_prevdatarix].rateKbps < an->an_minffrate)
		return AH_FALSE;
#endif
	txoplimit = IEEE80211_TXOP_TO_US(
		ic->ic_wme.wme_chanParams.cap_wmeParams[skb->priority].wmep_txopLimit);

	/* if the 4 msec limit is set on the channel, take it into account */
	if (sc->sc_curchan.privFlags & CHANNEL_4MS_LIMIT)
		txoplimit = MIN(txoplimit, US_PER_4MS); 

	if (txoplimit != 0 && athff_approx_txtime(sc, an, skb) > txoplimit) {
		DPRINTF(sc, ATH_DEBUG_XMIT | ATH_DEBUG_FF,
			"%s: FF TxOp violation\n", __func__);
		if (ffbuf)
			*flushq = AH_TRUE;
		return AH_FALSE;
	}

	return AH_TRUE;

#undef US_PER_4MS
#undef MIN
}
#endif

#ifdef AR_DEBUG
static void
ath_printrxbuf(struct ath_buf *bf, int done)
{
	struct ath_desc *ds = bf->bf_desc;

	printk("R (%p %llx) %08x %08x %08x %08x %08x %08x %c\n",
	    ds, ito64(bf->bf_daddr),
	    ds->ds_link, ds->ds_data,
	    ds->ds_ctl0, ds->ds_ctl1,
	    ds->ds_hw[0], ds->ds_hw[1],
	    !done ? ' ' : (ds->ds_rxstat.rs_status == 0) ? '*' : '!');
}

static void
ath_printtxbuf(struct ath_buf *bf, int done)
{
	struct ath_desc *ds = bf->bf_desc;

	printk("T (%p %llx) %08x %08x %08x %08x %08x %08x %08x %08x %c\n",
	    ds, ito64(bf->bf_daddr),
	    ds->ds_link, ds->ds_data,
	    ds->ds_ctl0, ds->ds_ctl1,
	    ds->ds_hw[0], ds->ds_hw[1], ds->ds_hw[2], ds->ds_hw[3],
	    !done ? ' ' : (ds->ds_txstat.ts_status == 0) ? '*' : '!');
}
#endif /* AR_DEBUG */

/*
 * Return netdevice statistics.
 */
static struct net_device_stats *
ath_getstats(struct net_device *dev)
{
	struct ath_softc *sc = dev->priv;
	struct net_device_stats *stats = &sc->sc_devstats;

	/* update according to private statistics */
	stats->tx_errors = sc->sc_stats.ast_tx_xretries
			 + sc->sc_stats.ast_tx_fifoerr
			 + sc->sc_stats.ast_tx_filtered;
	stats->tx_dropped = sc->sc_stats.ast_tx_nobuf
			+ sc->sc_stats.ast_tx_encap
			+ sc->sc_stats.ast_tx_nonode
			+ sc->sc_stats.ast_tx_nobufmgt;
	stats->rx_errors = sc->sc_stats.ast_rx_fifoerr
			+ sc->sc_stats.ast_rx_badcrypt
			+ sc->sc_stats.ast_rx_badmic;
	stats->rx_dropped = sc->sc_stats.ast_rx_tooshort;
	stats->rx_crc_errors = sc->sc_stats.ast_rx_crcerr;

	return stats;
}

static int
ath_set_mac_address(struct net_device *dev, void *addr)
{
	struct ath_softc *sc = dev->priv;
	struct ieee80211com *ic = &sc->sc_ic;
	struct ath_hal *ah = sc->sc_ah;
	struct sockaddr *mac = addr;
	int error = 0;

	if (netif_running(dev)) {
		DPRINTF(sc, ATH_DEBUG_ANY,
			"%s: cannot set address; device running\n", __func__);
		return -EBUSY;
	}
	DPRINTF(sc, ATH_DEBUG_ANY, "%s: %.2x:%.2x:%.2x:%.2x:%.2x:%.2x\n",
		__func__,
		mac->sa_data[0], mac->sa_data[1], mac->sa_data[2],
		mac->sa_data[3], mac->sa_data[4], mac->sa_data[5]);

	ATH_LOCK(sc);
	/* XXX not right for multiple VAPs */
	IEEE80211_ADDR_COPY(ic->ic_myaddr, mac->sa_data);
	IEEE80211_ADDR_COPY(dev->dev_addr, mac->sa_data);
	ath_hal_setmac(ah, dev->dev_addr);
	if ((dev->flags & IFF_RUNNING) && !sc->sc_invalid) {
		error = ath_reset(dev);
	}
	ATH_UNLOCK(sc);

	return error;
}

static int
ath_change_mtu(struct net_device *dev, int mtu)
{
	struct ath_softc *sc = dev->priv;
	int error = 0;

	if (!(ATH_MIN_MTU < mtu && mtu <= ATH_MAX_MTU)) {
		DPRINTF(sc, ATH_DEBUG_ANY, "%s: invalid %d, min %u, max %u\n",
			__func__, mtu, ATH_MIN_MTU, ATH_MAX_MTU);
		return -EINVAL;
	}
	DPRINTF(sc, ATH_DEBUG_ANY, "%s: %d\n", __func__, mtu);

	ATH_LOCK(sc);
	dev->mtu = mtu;
	if ((dev->flags & IFF_RUNNING) && !sc->sc_invalid) {
		/* NB: the rx buffers may need to be reallocated */
		tasklet_disable(&sc->sc_rxtq);
		error = ath_reset(dev);
		tasklet_enable(&sc->sc_rxtq);
	}
	ATH_UNLOCK(sc);

	return error;
}

/*
 * Diagnostic interface to the HAL.  This is used by various
 * tools to do things like retrieve register contents for
 * debugging.  The mechanism is intentionally opaque so that
 * it can change frequently w/o concern for compatibility.
 */
static int
ath_ioctl_diag(struct ath_softc *sc, struct ath_diag *ad)
{
	struct ath_hal *ah = sc->sc_ah;
	u_int id = ad->ad_id & ATH_DIAG_ID;
	void *indata = NULL;
	void *outdata = NULL;
	u_int32_t insize = ad->ad_in_size;
	u_int32_t outsize = ad->ad_out_size;
	int error = 0;

	if (ad->ad_id & ATH_DIAG_IN) {
		/*
		 * Copy in data.
		 */
		indata = kmalloc(insize, GFP_KERNEL);
		if (indata == NULL) {
			error = -ENOMEM;
			goto bad;
		}
		if (copy_from_user(indata, ad->ad_in_data, insize)) {
			error = -EFAULT;
			goto bad;
		}
	}
	if (ad->ad_id & ATH_DIAG_DYN) {
		/*
		 * Allocate a buffer for the results (otherwise the HAL
		 * returns a pointer to a buffer where we can read the
		 * results).  Note that we depend on the HAL leaving this
		 * pointer for us to use below in reclaiming the buffer;
		 * may want to be more defensive.
		 */
		outdata = kmalloc(outsize, GFP_KERNEL);
		if (outdata == NULL) {
			error = -ENOMEM;
			goto bad;
		}
	}
	if (ath_hal_getdiagstate(ah, id, indata, insize, &outdata, &outsize)) {
		if (outsize < ad->ad_out_size)
			ad->ad_out_size = outsize;
		if (outdata &&
		    copy_to_user(ad->ad_out_data, outdata, ad->ad_out_size))
			error = -EFAULT;
	} else
		error = -EINVAL;
bad:
	if ((ad->ad_id & ATH_DIAG_IN) && indata != NULL)
		kfree(indata);
	if ((ad->ad_id & ATH_DIAG_DYN) && outdata != NULL)
		kfree(outdata);
	return error;
}

static int
ath_ioctl(struct net_device *dev, struct ifreq *ifr, int cmd)
{
	struct ath_softc *sc = dev->priv;
	struct ieee80211com *ic = &sc->sc_ic;
	int error;

	ATH_LOCK(sc);
	switch (cmd) {
	case SIOCGATHSTATS:
		sc->sc_stats.ast_tx_packets = sc->sc_devstats.tx_packets;
		sc->sc_stats.ast_rx_packets = sc->sc_devstats.rx_packets;
		sc->sc_stats.ast_rx_rssi = ieee80211_getrssi(ic);
		if (copy_to_user(ifr->ifr_data, &sc->sc_stats, sizeof (sc->sc_stats)))
			error = -EFAULT;
		else
			error = 0;
		break;
	case SIOCGATHDIAG:
		if (!capable(CAP_NET_ADMIN))
			error = -EPERM;
		else
			error = ath_ioctl_diag(sc, (struct ath_diag *) ifr);
		break;
	case SIOCETHTOOL:
		if (copy_from_user(&cmd, ifr->ifr_data, sizeof(cmd)))
			error = -EFAULT;
		else
			error = ath_ioctl_ethtool(sc, cmd, ifr->ifr_data);
		break;
	case SIOC80211IFCREATE:
		error = ieee80211_ioctl_create_vap(ic, ifr, dev); 
		break;
	default:
		error = -EINVAL;
		break;
	}
	ATH_UNLOCK(sc);
	return error;
}

/*
 * Sysctls are split into ``static'' and ``dynamic'' tables.
 * The former are defined at module load time and are used
 * control parameters common to all devices.  The latter are
 * tied to particular device instances and come and go with
 * each device.  The split is currently a bit tenuous; many of
 * the static ones probably should be dynamic but having them
 * static (e.g. debug) means they can be set after a module is
 * loaded and before bringing up a device.  The alternative
 * is to add module parameters.
 */

/*
 * Dynamic (i.e. per-device) sysctls.  These are automatically
 * mirrored in /proc/sys.
 */
enum {
	ATH_SLOTTIME		= 1,
	ATH_ACKTIMEOUT		= 2,
	ATH_CTSTIMEOUT		= 3,
	ATH_SOFTLED		= 4,
	ATH_LEDPIN		= 5,
	ATH_COUNTRYCODE		= 6,
	ATH_REGDOMAIN		= 7,
	ATH_DEBUG		= 8,
	ATH_TXANTENNA		= 9,
	ATH_RXANTENNA		= 10,
	ATH_DIVERSITY		= 11,
	ATH_TXINTRPERIOD 	= 12,
	ATH_FFTXQMIN		= 18,
	ATH_TKIPMIC		= 19,
	ATH_XR_POLL_PERIOD 	= 20,
	ATH_XR_POLL_COUNT 	= 21,
	ATH_ACKRATE		= 22,
	ATH_INTMIT		= 23,
	ATH_MAXVAPS		= 26,
};

static int
ATH_SYSCTL_DECL(ath_sysctl_halparam, ctl, write, filp, buffer, lenp, ppos)
{
	struct ath_softc *sc = ctl->extra1;
	struct ath_hal *ah = sc->sc_ah;
	u_int val;
	int ret;

	ctl->data = &val;
	ctl->maxlen = sizeof(val);
	if (write) {
		ret = ATH_SYSCTL_PROC_DOINTVEC(ctl, write, filp, buffer, lenp, ppos);
		if (ret == 0) {
			switch ((long)ctl->extra2) {
			case ATH_SLOTTIME:
				if (val > 0) {
					if (!ath_hal_setslottime(ah, val))
						ret = -EINVAL;
					else
						sc->sc_slottimeconf = val;
				} else {
					/* disable manual override */
					sc->sc_slottimeconf = 0;
					ath_setslottime(sc);
				}
				break;
			case ATH_ACKTIMEOUT:
				if (!ath_hal_setacktimeout(ah, val))
					ret = -EINVAL;
				break;
			case ATH_CTSTIMEOUT:
				if (!ath_hal_setctstimeout(ah, val))
					ret = -EINVAL;
				break;
			case ATH_SOFTLED:
				if (val != sc->sc_softled) {
					if (val)
						ath_hal_gpioCfgOutput(ah, sc->sc_ledpin);
					ath_hal_gpioset(ah, sc->sc_ledpin,!sc->sc_ledon);
					sc->sc_softled = val;
				}
				break;
			case ATH_LEDPIN:
				/* XXX validate? */
				sc->sc_ledpin = val;
				break;
			case ATH_DEBUG:
				sc->sc_debug = val;
				break;
			case ATH_TXANTENNA:
				/*
				 * antenna can be:
				 * 0 = transmit diversity
				 * 1 = antenna port 1
				 * 2 = antenna port 2
				 */
				if (val < 0 || val > 2)
					return -EINVAL;
				else
					sc->sc_txantenna = val;
				break;
			case ATH_RXANTENNA:
				/*
				 * antenna can be:
				 * 0 = receive diversity
				 * 1 = antenna port 1
				 * 2 = antenna port 2
				 */
				if (val < 0 || val > 2)
					return -EINVAL;
				else
					ath_setdefantenna(sc, val);
				break;
			case ATH_DIVERSITY:
				/*
				 * 0 = disallow use of diversity
				 * 1 = allow use of diversity
				 */
				if (val < 0 || val > 1)
					return -EINVAL;
				/* Don't enable diversity if XR is enabled */
				if (((!sc->sc_hasdiversity) || (sc->sc_xrtxq != NULL)) && val)
					return -EINVAL;
				sc->sc_diversity = val;
				ath_hal_setdiversity(ah, val);
				break;
			case ATH_TXINTRPERIOD:
				/* XXX: validate? */
				sc->sc_txintrperiod = val;
				break;
			case ATH_FFTXQMIN:
				/* XXX validate? */
				sc->sc_fftxqmin = val;
				break;
			case ATH_TKIPMIC: {
				struct ieee80211com *ic = &sc->sc_ic;

				if (!ath_hal_hastkipmic(ah))
					return -EINVAL;
				ath_hal_settkipmic(ah, val);
				if (val)
					ic->ic_caps |= IEEE80211_C_TKIPMIC;
				else
					ic->ic_caps &= ~IEEE80211_C_TKIPMIC;
				break;
			}
#ifdef ATH_SUPERG_XR
			case ATH_XR_POLL_PERIOD: 
				if (val > XR_MAX_POLL_INTERVAL)
					val = XR_MAX_POLL_INTERVAL;
				else if (val < XR_MIN_POLL_INTERVAL)
					val = XR_MIN_POLL_INTERVAL;
				sc->sc_xrpollint = val;
				break;

			case ATH_XR_POLL_COUNT: 
				if (val > XR_MAX_POLL_COUNT)
					val = XR_MAX_POLL_COUNT;
				else if (val < XR_MIN_POLL_COUNT)
					val = XR_MIN_POLL_COUNT;
				sc->sc_xrpollcount = val;
				break;
#endif
			case ATH_ACKRATE:
				sc->sc_ackrate = val;
				ath_set_ack_bitrate(sc, sc->sc_ackrate);
				break;
			case ATH_INTMIT:
				sc->sc_useintmit = val;
				ath_hal_setintmit(ah, val ? 1 : 0);
				if (sc->sc_dev != NULL &&
				    sc->sc_dev->flags & IFF_RUNNING &&
				    !sc->sc_invalid)
					ath_reset(sc->sc_dev);
				break;
			default:
				return -EINVAL;
			}
		}
	} else {
		switch ((long)ctl->extra2) {
		case ATH_SLOTTIME:
			val = ath_hal_getslottime(ah);
			break;
		case ATH_ACKTIMEOUT:
			val = ath_hal_getacktimeout(ah);
			break;
		case ATH_CTSTIMEOUT:
			val = ath_hal_getctstimeout(ah);
			break;
		case ATH_SOFTLED:
			val = sc->sc_softled;
			break;
		case ATH_LEDPIN:
			val = sc->sc_ledpin;
			break;
		case ATH_COUNTRYCODE:
			ath_hal_getcountrycode(ah, &val);
			break;
		case ATH_MAXVAPS:
			val = ath_maxvaps;
			break;
		case ATH_REGDOMAIN:
			ath_hal_getregdomain(ah, &val);
			break;
		case ATH_DEBUG:
			val = sc->sc_debug;
			break;
		case ATH_TXANTENNA:
			val = sc->sc_txantenna;
			break;
		case ATH_RXANTENNA:
			val = ath_hal_getdefantenna(ah);
			break;
		case ATH_DIVERSITY:
			val = sc->sc_diversity;
			break;
		case ATH_TXINTRPERIOD:
			val = sc->sc_txintrperiod;
			break;
		case ATH_FFTXQMIN:
			val = sc->sc_fftxqmin;
			break;
		case ATH_TKIPMIC:
			val = ath_hal_gettkipmic(ah);
			break;
#ifdef ATH_SUPERG_XR
		case ATH_XR_POLL_PERIOD: 
			val=sc->sc_xrpollint;
			break;
		case ATH_XR_POLL_COUNT: 
			val=sc->sc_xrpollcount;
			break;
#endif
		case ATH_ACKRATE:
			val = sc->sc_ackrate;
			break;
		case ATH_INTMIT:
			val = sc->sc_useintmit;
			break;
		default:
			return -EINVAL;
		}
		ret = ATH_SYSCTL_PROC_DOINTVEC(ctl, write, filp, buffer, lenp, ppos);
	}
	return ret;
}

static int mincalibrate = 1;			/* once a second */
static int maxint = 0x7fffffff;		/* 32-bit big */

static const ctl_table ath_sysctl_template[] = {
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "slottime",
	  .mode		= 0644,
	  .proc_handler	= ath_sysctl_halparam,
	  .extra2	= (void *)ATH_SLOTTIME,
	},
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "acktimeout",
	  .mode		= 0644,
	  .proc_handler	= ath_sysctl_halparam,
	  .extra2	= (void *)ATH_ACKTIMEOUT,
	},
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "ctstimeout",
	  .mode		= 0644,
	  .proc_handler	= ath_sysctl_halparam,
	  .extra2	= (void *)ATH_CTSTIMEOUT,
	},
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "softled",
	  .mode		= 0644,
	  .proc_handler	= ath_sysctl_halparam,
	  .extra2	= (void *)ATH_SOFTLED,
	},
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "ledpin",
	  .mode		= 0644,
	  .proc_handler	= ath_sysctl_halparam,
	  .extra2	= (void *)ATH_LEDPIN,
	},
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "countrycode",
	  .mode		= 0444,
	  .proc_handler	= ath_sysctl_halparam,
	  .extra2	= (void *)ATH_COUNTRYCODE,
	},
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "maxvaps",
	  .mode		= 0444,
	  .proc_handler	= ath_sysctl_halparam,
	  .extra2	= (void *)ATH_MAXVAPS,
	},
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "regdomain",
	  .mode		= 0444,
	  .proc_handler	= ath_sysctl_halparam,
	  .extra2	= (void *)ATH_REGDOMAIN,
	},
#ifdef AR_DEBUG
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "debug",
	  .mode		= 0644,
	  .proc_handler	= ath_sysctl_halparam,
	  .extra2	= (void *)ATH_DEBUG,
	},
#endif
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "txantenna",
	  .mode		= 0644,
	  .proc_handler	= ath_sysctl_halparam,
	  .extra2	= (void *)ATH_TXANTENNA,
	},
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "rxantenna",
	  .mode		= 0644,
	  .proc_handler	= ath_sysctl_halparam,
	  .extra2	= (void *)ATH_RXANTENNA,
	},
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "diversity",
	  .mode		= 0644,
	  .proc_handler	= ath_sysctl_halparam,
	  .extra2	= (void *)ATH_DIVERSITY,
	},
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "txintrperiod",
	  .mode		= 0644,
	  .proc_handler	= ath_sysctl_halparam,
	  .extra2	= (void *)ATH_TXINTRPERIOD,
	},
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "fftxqmin",
	  .mode		= 0644,
	  .proc_handler	= ath_sysctl_halparam,
	  .extra2	= (void *)ATH_FFTXQMIN,
	},
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "tkipmic",
	  .mode		= 0644,
	  .proc_handler	= ath_sysctl_halparam,
	  .extra2	= (void *)ATH_TKIPMIC,
	},
#ifdef ATH_SUPERG_XR
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "xrpollperiod",
	  .mode		= 0644,
	  .proc_handler	= ath_sysctl_halparam,
	  .extra2	= (void *)ATH_XR_POLL_PERIOD,
	},
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "xrpollcount",
	  .mode		= 0644,
	  .proc_handler	= ath_sysctl_halparam,
	  .extra2	= (void *)ATH_XR_POLL_COUNT,
	},
#endif
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "ackrate",
	  .mode		= 0644,
	  .proc_handler	= ath_sysctl_halparam,
	  .extra2	= (void *)ATH_ACKRATE,
	},
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "intmit",
	  .mode		= 0644,
	  .proc_handler	= ath_sysctl_halparam,
	  .extra2	= (void *)ATH_INTMIT,
	},
	{ 0 }
};

static void
ath_dynamic_sysctl_register(struct ath_softc *sc)
{
	int i, space;
	char *dev_name = NULL;
	
	space = 5 * sizeof(struct ctl_table) + sizeof(ath_sysctl_template);
	sc->sc_sysctls = kmalloc(space, GFP_KERNEL);
	if (sc->sc_sysctls == NULL) {
		printk("%s: no memory for sysctl table!\n", __func__);
		return;
	}
	
	/* 
	 * We want to reserve space for the name of the device separate
	 * from the net_device structure, because when the name is changed
	 * it is changed in the net_device structure and the message given
	 * out.  Thus we won't know what the name it used to be if we rely
	 * on it.
	 */
	dev_name = kmalloc((strlen(sc->sc_dev->name) + 1) * sizeof(char), GFP_KERNEL);
	if (dev_name == NULL) {
		printk("%s: no memory for device name storage!\n", __func__);
		return;
	}
	strncpy(dev_name, sc->sc_dev->name, strlen(sc->sc_dev->name) + 1);

	/* setup the table */
	memset(sc->sc_sysctls, 0, space);
	sc->sc_sysctls[0].ctl_name = CTL_DEV;
	sc->sc_sysctls[0].procname = "dev";
	sc->sc_sysctls[0].mode = 0555;
	sc->sc_sysctls[0].child = &sc->sc_sysctls[2];
	/* [1] is NULL terminator */
	sc->sc_sysctls[2].ctl_name = CTL_AUTO;
	sc->sc_sysctls[2].procname = dev_name;
	sc->sc_sysctls[2].mode = 0555;
	sc->sc_sysctls[2].child = &sc->sc_sysctls[4];
	/* [3] is NULL terminator */
	/* copy in pre-defined data */
	memcpy(&sc->sc_sysctls[4], ath_sysctl_template,
		sizeof(ath_sysctl_template));

	/* add in dynamic data references */
	for (i = 4; sc->sc_sysctls[i].procname; i++)
		if (sc->sc_sysctls[i].extra1 == NULL)
			sc->sc_sysctls[i].extra1 = sc;

	/* and register everything */
	sc->sc_sysctl_header = ATH_REGISTER_SYSCTL_TABLE(sc->sc_sysctls);
	if (!sc->sc_sysctl_header) {
		printk("%s: failed to register sysctls!\n", sc->sc_dev->name);
		kfree(dev_name);
		kfree(sc->sc_sysctls);
		sc->sc_sysctls = NULL;
	}

	/* initialize values */
	sc->sc_debug = ath_debug;
	sc->sc_txantenna = 0;		/* default to auto-selection */
	sc->sc_txintrperiod = ATH_TXQ_INTR_PERIOD;
}

static void
ath_dynamic_sysctl_unregister(struct ath_softc *sc)
{
	if (sc->sc_sysctl_header) {
		unregister_sysctl_table(sc->sc_sysctl_header);
		sc->sc_sysctl_header = NULL;
	}
	if (sc->sc_sysctls && sc->sc_sysctls[2].procname) {
		kfree(sc->sc_sysctls[2].procname);
		sc->sc_sysctls[2].procname = NULL;
	}
	if (sc->sc_sysctls) {
		kfree(sc->sc_sysctls);
		sc->sc_sysctls = NULL;
	}
}

/*
 * Announce various information on device/driver attach.
 */
static void
ath_announce(struct net_device *dev)
{
#define	HAL_MODE_DUALBAND	(HAL_MODE_11A|HAL_MODE_11B)
	struct ath_softc *sc = dev->priv;
	struct ath_hal *ah = sc->sc_ah;
	u_int modes, cc;

	printk("%s: mac %d.%d phy %d.%d", dev->name,
		ah->ah_macVersion, ah->ah_macRev,
		ah->ah_phyRev >> 4, ah->ah_phyRev & 0xf);
	/*
	 * Print radio revision(s).  We check the wireless modes
	 * to avoid falsely printing revs for inoperable parts.
	 * Dual-band radio revs are returned in the 5 GHz rev number.
	 */
	ath_hal_getcountrycode(ah, &cc);
	modes = ath_hal_getwirelessmodes(ah, cc);
	if ((modes & HAL_MODE_DUALBAND) == HAL_MODE_DUALBAND) {
		if (ah->ah_analog5GhzRev && ah->ah_analog2GhzRev)
			printk(" 5 GHz radio %d.%d 2 GHz radio %d.%d",
				ah->ah_analog5GhzRev >> 4,
				ah->ah_analog5GhzRev & 0xf,
				ah->ah_analog2GhzRev >> 4,
				ah->ah_analog2GhzRev & 0xf);
		else
			printk(" radio %d.%d", ah->ah_analog5GhzRev >> 4,
				ah->ah_analog5GhzRev & 0xf);
	} else
		printk(" radio %d.%d", ah->ah_analog5GhzRev >> 4,
			ah->ah_analog5GhzRev & 0xf);
	printk("\n");
	if (1/*bootverbose*/) {
		int i;
		for (i = 0; i <= WME_AC_VO; i++) {
			struct ath_txq *txq = sc->sc_ac2q[i];
			printk("%s: Use hw queue %u for %s traffic\n",
				dev->name, txq->axq_qnum,
				ieee80211_wme_acnames[i]);
		}
		printk("%s: Use hw queue %u for CAB traffic\n", dev->name,
			sc->sc_cabq->axq_qnum);
		printk("%s: Use hw queue %u for beacons\n", dev->name,
			sc->sc_bhalq);
	}
#undef HAL_MODE_DUALBAND
}

/*
 * Static (i.e. global) sysctls.  Note that the HAL sysctls
 * are located under ours by sharing the setting for DEV_ATH.
 */
static ctl_table ath_static_sysctls[] = {
#ifdef AR_DEBUG
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "debug",
	  .mode		= 0644,
	  .data		= &ath_debug,
	  .maxlen	= sizeof(ath_debug),
	  .proc_handler	= proc_dointvec
	},
#endif
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "countrycode",
	  .mode		= 0444,
	  .data		= &ath_countrycode,
	  .maxlen	= sizeof(ath_countrycode),
	  .proc_handler	= proc_dointvec
	},
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "maxvaps",
	  .mode		= 0444,
	  .data		= &ath_maxvaps,
	  .maxlen	= sizeof(ath_maxvaps),
	  .proc_handler	= proc_dointvec
	},
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "outdoor",
	  .mode		= 0444,
	  .data		= &ath_outdoor,
	  .maxlen	= sizeof(ath_outdoor),
	  .proc_handler	= proc_dointvec
	},
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "xchanmode",
	  .mode		= 0444,
	  .data		= &ath_xchanmode,
	  .maxlen	= sizeof(ath_xchanmode),
	  .proc_handler	= proc_dointvec
	},
	{ .ctl_name	= CTL_AUTO,
	  .procname	= "calibrate",
	  .mode		= 0644,
	  .data		= &ath_calinterval,
	  .maxlen	= sizeof(ath_calinterval),
	  .extra1	= &mincalibrate,
	  .extra2	= &maxint,
	  .proc_handler	= proc_dointvec_minmax
	},
	{ 0 }
};
static ctl_table ath_ath_table[] = {
	{ .ctl_name	= DEV_ATH,
	  .procname	= "ath",
	  .mode		= 0555,
	  .child	= ath_static_sysctls
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

void
ath_sysctl_register(void)
{
	static int initialized = 0;

	if (!initialized) {
	        register_netdevice_notifier(&ath_event_block);
		ath_sysctl_header = ATH_REGISTER_SYSCTL_TABLE(ath_root_table);
		initialized = 1;
	}
}

void
ath_sysctl_unregister(void)
{
	unregister_netdevice_notifier(&ath_event_block);
	if (ath_sysctl_header)
		unregister_sysctl_table(ath_sysctl_header);
}

static const char* 
ath_get_hal_status_desc(HAL_STATUS status)
{
	if (status > 0 && status < sizeof(hal_status_desc)/sizeof(char *))
		return hal_status_desc[status];
	else
		return "";
}

static int
ath_rcv_dev_event(struct notifier_block *this, unsigned long event,
	void *ptr)
{
	struct net_device *dev = (struct net_device *) ptr;
	struct ath_softc *sc = (struct ath_softc *) dev->priv;

	if (!dev || !sc || dev->open != &ath_init)
		return 0;

        switch (event) {
        case NETDEV_CHANGENAME:
		ath_dynamic_sysctl_unregister(sc);
		ath_dynamic_sysctl_register(sc);
		return NOTIFY_DONE;
        default:
	        break;
        }
        return 0;
}
