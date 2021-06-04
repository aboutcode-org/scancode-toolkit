//==========================================================================
//
//      src/sys-ecos.c
//
//==========================================================================
//####ECOSGPLCOPYRIGHTBEGIN####
// -------------------------------------------
// This file is part of eCos, the Embedded Configurable Operating System.
// Portions created by Nick Garnett are
// Copyright (C) 2003, 2004 eCosCentric Ltd.
//
// eCos is free software; you can redistribute it and/or modify it under
// the terms of the GNU General Public License as published by the Free
// Software Foundation; either version 2 or (at your option) any later version.
//
// eCos is distributed in the hope that it will be useful, but WITHOUT ANY
// WARRANTY; without even the implied warranty of MERCHANTABILITY or
// FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
// for more details.
//
// You should have received a copy of the GNU General Public License along
// with eCos; if not, write to the Free Software Foundation, Inc.,
// 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA.
//
// As a special exception, if other files instantiate templates or use macros
// or inline functions from this file, or you compile this file and link it
// with other works to produce a work based on this file, this file does not
// by itself cause the resulting work to be covered by the GNU General Public
// License. However the source code for this file must still be made available
// in accordance with section (3) of the GNU General Public License.
//
// This exception does not invalidate any other reasons why a work based on
// this file might be covered by the GNU General Public License.
//
// -------------------------------------------
//####ECOSGPLCOPYRIGHTEND####
//####BSDCOPYRIGHTBEGIN####
//
// -------------------------------------------
//
// Portions of this software may have been derived from OpenBSD, 
// FreeBSD or other sources, and are covered by the appropriate
// copyright disclaimers included herein.
//
// -------------------------------------------
//
//####BSDCOPYRIGHTEND####
//==========================================================================

/*
 * sys-bsd.c - System-dependent procedures for setting up
 * PPP interfaces on bsd-4.4-ish systems (including 386BSD, NetBSD, etc.)
 *
 * Copyright (c) 1989 Carnegie Mellon University.
 * Copyright (c) 1995 The Australian National University.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms are permitted
 * provided that the above copyright notice and this paragraph are
 * duplicated in all such forms and that any documentation,
 * advertising materials, and other materials related to such
 * distribution and use acknowledge that the software was developed
 * by Carnegie Mellon University and The Australian National University.
 * The names of the Universities may not be used to endorse or promote
 * products derived from this software without specific prior written
 * permission.
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR
 * IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED
 * WARRANTIES OF MERCHANTIBILITY AND FITNESS FOR A PARTICULAR PURPOSE.
 */

#ifndef lint
//static char rcsid[] = "$FreeBSD: src/usr.sbin/pppd/sys-bsd.c,v 1.17 1999/08/28 01:19:08 peter Exp $";
#endif
/*	$NetBSD: sys-bsd.c,v 1.1.1.3 1997/09/26 18:53:04 christos Exp $	*/

/*
 * TODO:
 */

//==========================================================================

#include <pkgconf/system.h>
#include <pkgconf/net.h>
#include <pkgconf/ppp.h>

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <termios.h>
#include <signal.h>
#define _KERNEL 1
#include <sys/param.h>
#undef _KERNEL
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/stat.h>
#ifdef NetBSD1_2
#include <util.h>
#endif
#ifdef PPP_FILTER
#include <net/bpf.h>
#endif

#include <cyg/ppp/syslog.h>

#include <net/if.h>
#include <cyg/ppp/net/ppp_defs.h>
#include <cyg/ppp/net/if_ppp.h>
#include <net/route.h>
#include <net/if_dl.h>
#include <netinet/in.h>

#ifdef IPX_CHANGE
#include <netipx/ipx.h>
#endif

#if RTM_VERSION >= 3
#include <sys/param.h>
#if defined(NetBSD) && (NetBSD >= 199703)
#include <netinet/if_inarp.h>
#else	/* NetBSD 1.2D or later */
#include <netinet/if_ether.h>
#endif
#endif

#include "cyg/ppp/pppd.h"
#include "cyg/ppp/fsm.h"
#include "cyg/ppp/ipcp.h"

#include "cyg/ppp/ppp_io.h"

#include <cyg/ppp/ppp.h>

//==========================================================================

static int rtm_seq;

static cyg_io_handle_t ppp_handle; /* IO subsystem handle to PPP stream */
struct tty ppp_tty;             /* dummy TTY structure */

static cyg_handle_t ppp_rtc;
static cyg_resolution_t ppp_rtc_resolution;

static int loop_slave = -1;
static int loop_master;

static unsigned char inbuf[PPP_MTU + PPP_HDRLEN + 100]; /* buffer for chars read from input */

static int sockfd = -1;		/* socket for doing interface ioctls */

static int if_is_up;		/* the interface is currently up */
static u_int32_t ifaddrs[2];	/* local and remote addresses we set */
static u_int32_t default_route_gateway;	/* gateway addr for default route */
static u_int32_t proxy_arp_addr;	/* remote addr for proxy arp */

/* Prototypes for procedures local to this file. */
static int dodefaultroute __P((u_int32_t, int));
static int get_ether_addr __P((u_int32_t, struct sockaddr_dl *));

static void wait_input_alarm(cyg_handle_t alarm, cyg_addrword_t data);
#ifdef CYGOPT_IO_SERIAL_SUPPORT_LINE_STATUS
void cyg_ppp_serial_callback( cyg_serial_line_status_t *s,
                                     CYG_ADDRWORD priv );
#endif

extern u_int32_t netmask;	/* IP netmask to set on interface */

//==========================================================================
/*
 * sys_init - System-dependent initialization.
 */
void
sys_init()
{
    if( sockfd == -1 )
    {
        /* Get an internet socket for doing socket ioctl's on. */
        if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
            syslog(LOG_ERR, "Couldn't create IP socket: %d",errno);
            die(1);
        }
    }

    ppp_tty.pppd_wakeup = 0;
    ppp_tty.pppd_thread_running = true;
    
    ppp_rtc = cyg_real_time_clock();
    ppp_rtc_resolution = cyg_clock_get_resolution( ppp_rtc );

    cyg_alarm_create( ppp_rtc,
                      wait_input_alarm,
                      (cyg_addrword_t)&ppp_tty,
                      &ppp_tty.alarm,
                      &ppp_tty.alarm_obj);
}

//==========================================================================
/*
 * sys_cleanup - restore any system state we modified before exiting:
 * mark the interface down, delete default route and/or proxy arp entry.
 * This should call die() because it's called from die().
 */
void
sys_cleanup()
{
    struct ifreq ifr;

db_printf("%s called\n", __PRETTY_FUNCTION__);
    if (if_is_up) {
	strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name));
	if (ioctl(sockfd, SIOCGIFFLAGS, &ifr) >= 0
	    && ((ifr.ifr_flags & IFF_UP) != 0)) {
	    ifr.ifr_flags &= ~IFF_UP;
	    ioctl(sockfd, SIOCSIFFLAGS, &ifr);
	}
    }
    if (ifaddrs[0] != 0)
	cifaddr(0, ifaddrs[0], ifaddrs[1]);
    if (default_route_gateway)
	cifdefaultroute(0, 0, default_route_gateway);
    if (proxy_arp_addr)
	cifproxyarp(0, proxy_arp_addr);

    if( sockfd != -1 )
    {
        close(sockfd);
        sockfd = -1;
    }
}

//==========================================================================

#ifdef __ECOS

void
sys_exit(void)
{
db_printf("%s called\n", __PRETTY_FUNCTION__);    
    phase = PHASE_DEAD;
    while( ppp_tty.tx_thread_running )
    {
        db_printf("kick tx thread\n");        
        cyg_semaphore_post( &ppp_tty.tx_sem );
        cyg_thread_delay(100);
    }
    ppp_tty.pppd_thread_running = false;
    cyg_thread_exit();
}
#endif

//==========================================================================
/*
 * sys_close - Clean up in a child process before execing.
 */
void
sys_close()
{
db_printf("%s called\n", __PRETTY_FUNCTION__);
    if (loop_slave >= 0) {
	close(loop_slave);
	close(loop_master);
    }
}

//==========================================================================
/*
 * sys_check_options - check the options that the user specified
 */
void
sys_check_options()
{
//db_printf("%s called\n", __PRETTY_FUNCTION__);
}

//==========================================================================
/*
 * ppp_available - check whether the system has any ppp interfaces
 * (in fact we check whether we can do an ioctl on ppp0).
 */
int
ppp_available()
{
    int s, ok;
    struct ifreq ifr;
    extern char *no_ppp_msg;

    if ((s = socket(AF_INET, SOCK_DGRAM, 0)) < 0)
	return 1;		/* can't tell */

    strncpy(ifr.ifr_name, "ppp0", sizeof (ifr.ifr_name));
    ok = ioctl(s, SIOCGIFFLAGS, (caddr_t) &ifr) >= 0;
    close(s);

    no_ppp_msg = "\
This system lacks kernel support for PPP.  To include PPP support\n\
in the kernel, please follow the steps detailed in the README.bsd\n\
file in the ppp-2.2 distribution.\n";
    return ok;
}

//==========================================================================
/*
 * establish_ppp - Turn the serial port into a ppp interface.
 */
void
establish_ppp(cyg_io_handle_t handle)
{
    int s;
    int x;
    int err;
    
//db_printf("%s called\n", __PRETTY_FUNCTION__);

    ppp_handle = ppp_tty.t_handle = handle;
    ppp_tty.t_sc = NULL;

    s = splsoftnet();

    err = cyg_ppp_pppopen( &ppp_tty );
    
    if( err != 0 )
        syslog( LOG_ERR, "Couldn't establish PPP interface: %d", err );

    /*
     * Enable debug in the driver if requested.
     */
    if (kdebugflag) {
	if ((err = cyg_ppp_ppptioctl(&ppp_tty, PPPIOCGFLAGS, (caddr_t) &x, 0)) < 0) {
	    syslog(LOG_WARNING, "ioctl (PPPIOCGFLAGS): %d",err);
	} else {
	    x |= (kdebugflag & 0xFF) * SC_DEBUG;
	    if ((err = cyg_ppp_ppptioctl(&ppp_tty, PPPIOCSFLAGS, (caddr_t) &x, 0)) < 0)
		syslog(LOG_WARNING, "ioctl(PPPIOCSFLAGS): %d",err);
	}
    }

    splx(s);
}

//==========================================================================
/*
 * restore_loop - reattach the ppp unit to the loopback.
 */
void
restore_loop()
{
db_printf("%s called\n", __PRETTY_FUNCTION__);
}


//==========================================================================
/*
 * disestablish_ppp - Restore the serial port to normal operation.
 * This shouldn't call die() because it's called from die().
 */
void
disestablish_ppp(cyg_io_handle_t handle)
{
    db_printf("%s called\n", __PRETTY_FUNCTION__);
}

//==========================================================================
/*
 * Check whether the link seems not to be 8-bit clean.
 */
void
clean_check()
{
db_printf("%s called\n", __PRETTY_FUNCTION__);
}

//==========================================================================
/*
 * set_up_tty: Set up the serial port on `fd' for 8 bits, no parity,
 * at the requested speed, etc.  If `local' is true, set CLOCAL
 * regardless of whether the modem option was specified.
 *
 * For *BSD, we assume that speed_t values numerically equal bits/second.
 */
void
set_up_tty(cyg_io_handle_t handle, int local)
{
    cyg_serial_info_t   cfg;
    int                 err;
    cyg_uint32          len = sizeof(cfg);

    err = cyg_io_get_config( handle,
                             CYG_IO_GET_CONFIG_SERIAL_INFO,
                             &cfg,
                             &len);

    if( err != 0 ) {
	syslog(LOG_ERR, "cyg_io_get_config: %d",err);
	die(1);
    }

    switch ( flowctl )
    {
    case CYG_PPP_FLOWCTL_DEFAULT:
        break;
        
    case CYG_PPP_FLOWCTL_NONE:
        cfg.flags &= ~(CYGNUM_SERIAL_FLOW_RTSCTS_RX|CYGNUM_SERIAL_FLOW_RTSCTS_TX|
                       CYGNUM_SERIAL_FLOW_XONXOFF_RX|CYGNUM_SERIAL_FLOW_XONXOFF_TX);
        break;
        
    case CYG_PPP_FLOWCTL_HARDWARE:
        cfg.flags &= ~(CYGNUM_SERIAL_FLOW_XONXOFF_RX|CYGNUM_SERIAL_FLOW_XONXOFF_TX);
        cfg.flags |= CYGNUM_SERIAL_FLOW_RTSCTS_RX|CYGNUM_SERIAL_FLOW_RTSCTS_TX;
        break;
        
    case CYG_PPP_FLOWCTL_SOFTWARE:
        cfg.flags &= ~(CYGNUM_SERIAL_FLOW_RTSCTS_RX|CYGNUM_SERIAL_FLOW_RTSCTS_TX);
        cfg.flags |= CYGNUM_SERIAL_FLOW_XONXOFF_RX|CYGNUM_SERIAL_FLOW_XONXOFF_TX;
        break;
    }

    if( inspeed != 0 )
        cfg.baud = inspeed;
    
    err = cyg_io_set_config( handle,
                             CYG_IO_SET_CONFIG_SERIAL_INFO,
                             &cfg,
                             &len);

    if( err != 0 ) {
	syslog(LOG_ERR, "cyg_io_set_config: %d",err);
	die(1);
    }
}

//==========================================================================
/*
 * restore_tty - restore the terminal to the saved settings.
 */
void
restore_tty(cyg_io_handle_t handle)
{
#ifdef CYGOPT_IO_SERIAL_SUPPORT_LINE_STATUS
    if( modem )
    {
        // Restore callback handler if it was set.
        
        Cyg_ErrNo err;
        cyg_uint32 len = sizeof(ppp_tty.serial_callbacks);

        db_printf("%s called\n", __PRETTY_FUNCTION__);
                
        err = cyg_io_set_config( handle,
                                 CYG_IO_SET_CONFIG_SERIAL_STATUS_CALLBACK,
                                 &ppp_tty.serial_callbacks,
                                 &len);

        if( err != 0 ) {
            syslog(LOG_ERR, "cyg_io_set_config(restore serial callbacks): %d",err);
            die(1);
        }
    }
#endif
}

//==========================================================================
/*
 * setdtr - control the DTR line on the serial port.
 * This is called from die(), so it shouldn't call die().
 */
void
setdtr(fd, on)
int fd, on;
{
db_printf("%s called\n", __PRETTY_FUNCTION__);
}

//==========================================================================
/*
 * output - Output PPP packet.
 */
void
output(unit, p, len)
    int unit;
    u_char *p;
    int len;
{
    Cyg_ErrNo err;
    struct uio uio;
    struct iovec iov;
    int s;
    
    if (debug)
	log_packet(p, len, "sent ", LOG_DEBUG);


    iov.iov_base    = p;
    iov.iov_len     = len;
    uio.uio_iov     = &iov;
    uio.uio_iovcnt  = 1;
    uio.uio_resid   = len;
    uio.uio_segflg  = UIO_USERSPACE;
    uio.uio_rw      = UIO_WRITE;

    s = splsoftnet();
    
    err = cyg_ppp_pppwrite( &ppp_tty, &uio, 0 );

    splx(s);
    
    if( err != 0 )
        syslog(LOG_ERR, "write: %d",err);

}

//==========================================================================

#ifdef __ECOS

static void wait_input_alarm(cyg_handle_t alarm, cyg_addrword_t data)
{
    cyg_thread_release( ppp_tty.pppd_thread );
    ppp_tty.pppd_wakeup = 1;
}

#ifdef CYGOPT_IO_SERIAL_SUPPORT_LINE_STATUS
void cyg_ppp_serial_callback( cyg_serial_line_status_t *s,
                                     CYG_ADDRWORD priv )
{
    externC int kill_link;

//    db_printf("serial callback %d %x\n",s->which, s->value );

    if( s->which == CYGNUM_SERIAL_STATUS_CARRIERDETECT )
    {
        if( s->value == 0 )
        {
            // CD lost
            ppp_tty.carrier_detected = 0;
            kill_link = 1;
            cyg_thread_release( ppp_tty.pppd_thread );
            ppp_tty.pppd_wakeup = 1;
        }
        else
        {
            // CD up
            ppp_tty.carrier_detected = 1;
        }
    }
}
#endif

static void cyg_ppp_tx_thread(CYG_ADDRWORD arg)
{
    ppp_tty.tx_thread_running = true;

    // Wait for the PPPD thread to get going and start the PPP
    // initialization phase.
    while(phase == PHASE_DEAD )
        cyg_thread_delay(100);

    // Now loop until the link goes back down.
    while( phase != PHASE_DEAD )
    {
        cyg_semaphore_wait( &ppp_tty.tx_sem );

        if( phase == PHASE_DEAD )
            break;
        
        // Call into PPP driver to get transmissions going. This is
        // only called if some other thread has failed to transmit all
        // of a packet due to a full buffer, or flow control.

        cyg_ppp_pppstart( &ppp_tty );
    }

db_printf("%s exiting\n", __PRETTY_FUNCTION__);        
    ppp_tty.tx_thread_running = false;
    cyg_thread_exit();
}

#endif


//==========================================================================
/*
 * wait_input - wait until there is data available on ttyfd,
 * for the length of time specified by *timo (indefinite
 * if timo is NULL).
 */
void
wait_input(timo)
    struct timeval *timo;
{
    // If there are any packets still waiting on the input queue then
    // return immediately to let the PPPD handle them.
    if (cyg_ppp_pppcheck(&ppp_tty) != 0)
        return;

    if( timo != NULL )
    {
        cyg_tick_count_t trigger = timo->tv_sec*ppp_rtc_resolution.divisor;

        // If the timeval has a microseconds value, just add another
        // second on to the trigger time. These are after all just
        // timeouts, not accurate timings, so a bit of imprecision
        // will not hurt.
        if( timo->tv_usec != 0 )
            trigger += ppp_rtc_resolution.divisor;            

        trigger += cyg_current_time();

        // We set the alarm to retrigger after a second. This is in
        // case it catches cyg_io_read() at an uninterruptible
        // point. The alarm is disabled as soon as the read returns,
        // so the retrigger will usually not happen.
        cyg_alarm_initialize( ppp_tty.alarm,
                              trigger,
                              ppp_rtc_resolution.divisor );
    }
    
    for(;;)
    {
        int s;
        cyg_uint32 len = 1;
        Cyg_ErrNo err;
        cyg_serial_buf_info_t info;
        cyg_uint32 ilen = sizeof(info);

#if 1
        // Work out how many bytes are waiting in the serial device
        // buffer and read them all at once. If there are none, we
        // just wait for a single character to arrive.
       
        if( cyg_io_get_config( ppp_tty.t_handle, CYG_IO_GET_CONFIG_SERIAL_BUFFER_INFO,
                               &info, &ilen ) == 0 && info.rx_count > 1 )
        {
            len = info.rx_count-1;
            if( len > sizeof(inbuf) )
                len = sizeof(inbuf);
        }
#endif
        
        if( timo != NULL )
            cyg_alarm_enable( ppp_tty.alarm );

        err = cyg_io_read( ppp_handle, &inbuf, &len );

        if( timo != NULL )
            cyg_alarm_disable( ppp_tty.alarm );
        
//        db_printf("read: err %d len %d byte %02x\n",err,len,inbuf[0]);
        
        if( err == 0 )
        {
            int i;
            
            // Pass all input data to PPP driver for analysis. If this
            // turns out to be for the PPPD, it will call
            // pppasyncctlp() which in turn will set
            // ppp_tty.pppd_wakeup. We detect that on return from
            // pppinput() and return to the caller to do pppd
            // processing.

            s = splsoftnet();
            
            for( i = 0; i < len; i++ )
            {
                err = cyg_ppp_pppinput( inbuf[i], &ppp_tty );
                
                if( err != 0 )
                    syslog( LOG_ERR, "pppinput error: %d", err);

            }

            splx(s);
            
        }
        else if( err != -EINTR )
            syslog( LOG_ERR, "Read error: %d",err);

        if( ppp_tty.pppd_wakeup )
        {
            ppp_tty.pppd_wakeup = 0;
            break;
        }
    }
}

//==========================================================================
/*
 * wait_time - wait for a given length of time or until a
 * signal is received.
 */
void
wait_time(timo)
    struct timeval *timo;
{
db_printf("%s called\n", __PRETTY_FUNCTION__);
}


//==========================================================================
/*
 * read_packet - get a PPP packet from the serial device.
 */
int
read_packet(buf)
    u_char *buf;
{
    int err;
    struct uio uio;
    struct iovec iov;
    int len = PPP_MTU + PPP_HDRLEN;
    int s;
    
//db_printf("%s called\n", __PRETTY_FUNCTION__);
    
    iov.iov_base        = buf;
    iov.iov_len         = len;
    uio.uio_iov         = &iov;
    uio.uio_iovcnt      = 1;
    uio.uio_resid       = len;
    uio.uio_segflg      = UIO_USERSPACE;
    uio.uio_rw          = UIO_READ;

    s = splsoftnet();
    
    err = cyg_ppp_pppread( &ppp_tty, &uio, 0 );

    splx(s);
    
    if( err == EWOULDBLOCK )
        return -1;
    
    if( err != 0 )
    {
        syslog(LOG_ERR, "pppread: %d",err);
        die(1);
    }

    len -= uio.uio_resid;

    return len;
}

//==========================================================================
/*
 * ppp_send_config - configure the transmit characteristics of
 * the ppp interface.
 */
void
ppp_send_config(unit, mtu, asyncmap, pcomp, accomp)
    int unit, mtu;
    u_int32_t asyncmap;
    int pcomp, accomp;
{
    u_int x;
    struct ifreq ifr;
    int err;
    int s;
    
//    db_printf("%s: unit %d mtu %d asyncmap %08x pcomp %08x accomp %08x\n", __PRETTY_FUNCTION__,
//              unit,mtu,asyncmap,pcomp,accomp);
    
    strncpy(ifr.ifr_name, ifname, sizeof (ifr.ifr_name));
    ifr.ifr_mtu = mtu;
    if (ioctl(sockfd, SIOCSIFMTU, (caddr_t) &ifr) < 0) {
	syslog(LOG_ERR, "ioctl(SIOCSIFMTU): %d",errno);
	quit();
    }


    s = splsoftnet();
    
    if ((err = cyg_ppp_ppptioctl(&ppp_tty, PPPIOCSASYNCMAP, (caddr_t) &asyncmap, 0)) < 0) {
	syslog(LOG_ERR, "ioctl(PPPIOCSASYNCMAP): %d",err);
    }

    if ((err = cyg_ppp_ppptioctl(&ppp_tty, PPPIOCGFLAGS, (caddr_t) &x, 0)) < 0) {
	syslog(LOG_ERR, "ioctl (PPPIOCGFLAGS): %d",err);
    }
    x = pcomp? x | SC_COMP_PROT: x &~ SC_COMP_PROT;
    x = accomp? x | SC_COMP_AC: x &~ SC_COMP_AC;
    if ((err = cyg_ppp_ppptioctl(&ppp_tty, PPPIOCSFLAGS, (caddr_t) &x, 0)) < 0) {
	syslog(LOG_ERR, "ioctl(PPPIOCSFLAGS): %d",err);
    }

    splx(s);
}


//==========================================================================
/*
 * ppp_set_xaccm - set the extended transmit ACCM for the interface.
 */
void
ppp_set_xaccm(unit, accm)
    int unit;
    ext_accm accm;
{
    int error;
    int s;
    
//db_printf("%s called\n", __PRETTY_FUNCTION__);

    s = splsoftnet();
        
    error = cyg_ppp_ppptioctl( &ppp_tty, PPPIOCSXASYNCMAP, (caddr_t)accm, 0 );

    splx(s);
    
    if( error != 0 )
	syslog(LOG_WARNING, "ioctl(set extended ACCM): %d",error);
}


//==========================================================================
/*
 * ppp_recv_config - configure the receive-side characteristics of
 * the ppp interface.
 */
void
ppp_recv_config(unit, mru, asyncmap, pcomp, accomp)
    int unit, mru;
    u_int32_t asyncmap;
    int pcomp, accomp;
{
    int x;
    int err;
    int s;

    s = splsoftnet();
    
    if ((err = cyg_ppp_ppptioctl(&ppp_tty, PPPIOCSMRU, (caddr_t) &mru, 0)) < 0) {
	syslog(LOG_ERR, "ioctl(PPPIOCSMRU): %d",err);
    }
    if ((err = cyg_ppp_ppptioctl(&ppp_tty, PPPIOCSRASYNCMAP, (caddr_t) &asyncmap, 0)) < 0) {
	syslog(LOG_ERR, "ioctl(PPPIOCSRASYNCMAP): %d",err);
    }
    if ((err = cyg_ppp_ppptioctl(&ppp_tty, PPPIOCGFLAGS, (caddr_t) &x, 0)) < 0) {
	syslog(LOG_ERR, "ioctl (PPPIOCGFLAGS): %d",err);
    }
    x = !accomp? x | SC_REJ_COMP_AC: x &~ SC_REJ_COMP_AC;
    if ((err = cyg_ppp_ppptioctl(&ppp_tty, PPPIOCSFLAGS, (caddr_t) &x, 0)) < 0) {
	syslog(LOG_ERR, "ioctl(PPPIOCSFLAGS): %d",err);
    }

    splx(s);
}

//==========================================================================
/*
 * ccp_test - ask kernel whether a given compression method
 * is acceptable for use.  Returns 1 if the method and parameters
 * are OK, 0 if the method is known but the parameters are not OK
 * (e.g. code size should be reduced), or -1 if the method is unknown.
 */
int
ccp_test(unit, opt_ptr, opt_len, for_transmit)
    int unit, opt_len, for_transmit;
    u_char *opt_ptr;
{
    struct ppp_option_data data;
    int s;
    
    data.ptr = opt_ptr;
    data.length = opt_len;
    data.transmit = for_transmit;
//db_printf("%s called\n", __PRETTY_FUNCTION__);

    s = splsoftnet();
        
    errno = cyg_ppp_ppptioctl(&ppp_tty, PPPIOCSCOMPRESS, (caddr_t) &data, 0 );

    splx(s);
    
    if (errno == 0)        
	return 1;
    else return (errno == ENOBUFS)? 0: -1;
    
}

//==========================================================================
/*
 * ccp_flags_set - inform kernel about the current state of CCP.
 */
void
ccp_flags_set(unit, isopen, isup)
    int unit, isopen, isup;
{
    int x;

    int err;
//db_printf("%s called\n", __PRETTY_FUNCTION__);
    if ((err = cyg_ppp_ppptioctl(&ppp_tty, PPPIOCGFLAGS, (caddr_t) &x, 0)) != 0) {
	syslog(LOG_ERR, "ioctl (PPPIOCGFLAGS): %d",err);
	return;
    }
    x = isopen? x | SC_CCP_OPEN: x &~ SC_CCP_OPEN;
    x = isup? x | SC_CCP_UP: x &~ SC_CCP_UP;
    if ((err = cyg_ppp_ppptioctl(&ppp_tty, PPPIOCSFLAGS, (caddr_t) &x,0)) != 0)
	syslog(LOG_ERR, "ioctl(PPPIOCSFLAGS): %d",err);
}

//==========================================================================
/*
 * ccp_fatal_error - returns 1 if decompression was disabled as a
 * result of an error detected after decompression of a packet,
 * 0 otherwise.  This is necessary because of patent nonsense.
 */
int
ccp_fatal_error(unit)
    int unit;
{
    int x;
    int err;
    
db_printf("%s called\n", __PRETTY_FUNCTION__);
    if ((err = cyg_ppp_ppptioctl(&ppp_tty, PPPIOCGFLAGS, (caddr_t) &x, 0)) != 0) {
	syslog(LOG_ERR, "ioctl(PPPIOCGFLAGS): %d",err);
	return 0;
    }
    return x & SC_DC_FERROR;
}

//==========================================================================
/*
 * get_idle_time - return how long the link has been idle.
 */
int
get_idle_time(u, ip)
    int u;
    struct ppp_idle *ip;
{
    return cyg_ppp_ppptioctl(&ppp_tty, PPPIOCGIDLE, (caddr_t)ip, 0) == 0;
}


//==========================================================================

#ifdef PPP_FILTER
/*
 * set_filters - transfer the pass and active filters to the kernel.
 */
int
set_filters(pass, active)
    struct bpf_program *pass, *active;
{
    int ret = 1;

db_printf("%s called\n", __PRETTY_FUNCTION__);
    if (pass->bf_len > 0) {
	if (ioctl(ppp_fd, PPPIOCSPASS, pass) < 0) {
	    syslog(LOG_ERR, "Couldn't set pass-filter in kernel: %m");
	    ret = 0;
	}
    }
    if (active->bf_len > 0) {
	if (ioctl(ppp_fd, PPPIOCSACTIVE, active) < 0) {
	    syslog(LOG_ERR, "Couldn't set active-filter in kernel: %m");
	    ret = 0;
	}
    }
    return ret;
}
#endif

//==========================================================================
/*
 * sifvjcomp - config tcp header compression
 */
int
sifvjcomp(u, vjcomp, cidcomp, maxcid)
    int u, vjcomp, cidcomp, maxcid;
{
    u_int x;
    int err;
    
    if ((err = cyg_ppp_ppptioctl(&ppp_tty, PPPIOCGFLAGS, (caddr_t) &x, 0)) != 0) {
	syslog(LOG_ERR, "ioctl (PPPIOCGFLAGS): %d",err);
	return 0;
    }
    x = vjcomp ? x | SC_COMP_TCP: x &~ SC_COMP_TCP;
    x = cidcomp? x & ~SC_NO_TCP_CCID: x | SC_NO_TCP_CCID;
    if ((err = cyg_ppp_ppptioctl(&ppp_tty, PPPIOCSFLAGS, (caddr_t) &x, 0)) != 0) {
	syslog(LOG_ERR, "ioctl(PPPIOCSFLAGS): %d",err);
	return 0;
    }
    if (vjcomp && ((err=cyg_ppp_ppptioctl(&ppp_tty, PPPIOCSMAXCID, (caddr_t) &maxcid, 0)) != 0)) {
	syslog(LOG_ERR, "ioctl(PPPIOCSMAXCID): %d",err);
	return 0;
    }
    return 1;
}

//==========================================================================
/*
 * sifup - Config the interface up and enable IP packets to pass.
 */
int
sifup(u)
    int u;
{
    struct ifreq ifr;

//db_printf("%s called\n", __PRETTY_FUNCTION__);
    strncpy(ifr.ifr_name, ifname, sizeof (ifr.ifr_name));
    if (ioctl(sockfd, SIOCGIFFLAGS, (caddr_t) &ifr) < 0) {
	syslog(LOG_ERR, "ioctl (SIOCGIFFLAGS): %m");
	return 0;
    }
    ifr.ifr_flags |= IFF_UP;
    if (ioctl(sockfd, SIOCSIFFLAGS, (caddr_t) &ifr) < 0) {
	syslog(LOG_ERR, "ioctl(SIOCSIFFLAGS): %m");
	return 0;
    }
    if_is_up = 1;
    return 1;
}

//==========================================================================
/*
 * sifnpmode - Set the mode for handling packets for a given NP.
 */
int
sifnpmode(u, proto, mode)
    int u;
    int proto;
    enum NPmode mode;
{
    struct npioctl npi;

//db_printf("%s called\n", __PRETTY_FUNCTION__);
    npi.protocol = proto;
    npi.mode = mode;
    {
        int err;
    
        if ((err = cyg_ppp_ppptioctl(&ppp_tty, PPPIOCSNPMODE, (caddr_t)&npi, 0)) < 0) {
            syslog(LOG_ERR, "ioctl(set NP %d mode to %d): %d", proto, mode,err);
            return 0;
        }
    }
    
    return 1;
}

//==========================================================================
/*
 * sifdown - Config the interface down and disable IP.
 */
int
sifdown(u)
    int u;
{
    struct ifreq ifr;
    int rv;
    struct npioctl npi;

db_printf("%s called\n", __PRETTY_FUNCTION__);
    rv = 1;
    npi.protocol = PPP_IP;
    npi.mode = NPMODE_ERROR;
    {
        int err = cyg_ppp_ppptioctl(&ppp_tty, PPPIOCSNPMODE, (caddr_t) &npi, 0);
        if( err < 0 )
            syslog(LOG_WARNING, "ioctl(PPPIOCSNPMODE): %d",err);
    }
    strncpy(ifr.ifr_name, ifname, sizeof (ifr.ifr_name));
    if (ioctl(sockfd, SIOCGIFFLAGS, (caddr_t) &ifr) < 0) {
	syslog(LOG_ERR, "ioctl (SIOCGIFFLAGS): %m");
	rv = 0;
    } else {
	ifr.ifr_flags &= ~IFF_UP;
	if (ioctl(sockfd, SIOCSIFFLAGS, (caddr_t) &ifr) < 0) {
	    syslog(LOG_ERR, "ioctl(SIOCSIFFLAGS): %m");
	    rv = 0;
	} else
	    if_is_up = 0;
    }
    return rv;
    return 0;
}

//==========================================================================
/*
 * SET_SA_FAMILY - set the sa_family field of a struct sockaddr,
 * if it exists.
 */
#define SET_SA_FAMILY(addr, family)		\
    BZERO((char *) &(addr), sizeof(addr));	\
    addr.sa_family = (family); 			\
    addr.sa_len = sizeof(addr);

//==========================================================================
/*
 * sifaddr - Config the interface IP addresses and netmask.
 */
int
sifaddr(u, o, h, m)
    int u;
    u_int32_t o, h, m;
{
    struct ifaliasreq ifra;
    struct ifreq ifr;

//db_printf("%s called\n", __PRETTY_FUNCTION__);
    strncpy(ifra.ifra_name, ifname, sizeof(ifra.ifra_name));
    SET_SA_FAMILY(ifra.ifra_addr, AF_INET);
    ((struct sockaddr_in *) &ifra.ifra_addr)->sin_addr.s_addr = o;
    SET_SA_FAMILY(ifra.ifra_broadaddr, AF_INET);
    ((struct sockaddr_in *) &ifra.ifra_broadaddr)->sin_addr.s_addr = h;
    if (m != 0) {
	SET_SA_FAMILY(ifra.ifra_mask, AF_INET);
	((struct sockaddr_in *) &ifra.ifra_mask)->sin_addr.s_addr = m;
    } else
	BZERO(&ifra.ifra_mask, sizeof(ifra.ifra_mask));
    BZERO(&ifr, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name));
    if (ioctl(sockfd, SIOCDIFADDR, (caddr_t) &ifr) < 0) {
	if (errno != EADDRNOTAVAIL)
	    syslog(LOG_WARNING, "Couldn't remove interface address: %d",errno);
    }
    if (ioctl(sockfd, SIOCAIFADDR, (caddr_t) &ifra) < 0) {
	if (errno != EEXIST) {
	    syslog(LOG_ERR, "Couldn't set interface address: %d",errno);
	    return 0;
	}
	syslog(LOG_WARNING,
	       "Couldn't set interface address: Address %s already exists",
		ip_ntoa(o));
    }
    ifaddrs[0] = o;
    ifaddrs[1] = h;
    return 1;
}

//==========================================================================
/*
 * cifaddr - Clear the interface IP addresses, and delete routes
 * through the interface if possible.
 */
int
cifaddr(u, o, h)
    int u;
    u_int32_t o, h;
{
    struct ifaliasreq ifra;

db_printf("%s called\n", __PRETTY_FUNCTION__);
    ifaddrs[0] = 0;
    strncpy(ifra.ifra_name, ifname, sizeof(ifra.ifra_name));
    SET_SA_FAMILY(ifra.ifra_addr, AF_INET);
    ((struct sockaddr_in *) &ifra.ifra_addr)->sin_addr.s_addr = o;
    SET_SA_FAMILY(ifra.ifra_broadaddr, AF_INET);
    ((struct sockaddr_in *) &ifra.ifra_broadaddr)->sin_addr.s_addr = h;
    BZERO(&ifra.ifra_mask, sizeof(ifra.ifra_mask));
    if (ioctl(sockfd, SIOCDIFADDR, (caddr_t) &ifra) < 0) {
	if (errno != EADDRNOTAVAIL)
	    syslog(LOG_WARNING, "Couldn't delete interface address: %m");
	return 0;
    }
    return 1;
}

//==========================================================================
/*
 * sifdefaultroute - assign a default route through the address given.
 */
int
sifdefaultroute(u, l, g)
    int u;
    u_int32_t l, g;
{
db_printf("%s called\n", __PRETTY_FUNCTION__);
    return dodefaultroute(g, 's');
}

//==========================================================================
/*
 * cifdefaultroute - delete a default route through the address given.
 */
int
cifdefaultroute(u, l, g)
    int u;
    u_int32_t l, g;
{
db_printf("%s called\n", __PRETTY_FUNCTION__);
    return dodefaultroute(g, 'c');
}

//==========================================================================
/*
 * dodefaultroute - talk to a routing socket to add/delete a default route.
 */
static int
dodefaultroute(g, cmd)
    u_int32_t g;
    int cmd;
{
    int routes;
    struct {
	struct rt_msghdr	hdr;
	struct sockaddr_in	dst;
	struct sockaddr_in	gway;
	struct sockaddr_in	mask;
    } rtmsg;

db_printf("%s %08x %c\n", __PRETTY_FUNCTION__,g,cmd);
    if ((routes = socket(PF_ROUTE, SOCK_RAW, AF_INET)) < 0) {
	syslog(LOG_ERR, "Couldn't %s default route: socket: %d",
	       cmd=='s'? "add": "delete",errno);
	return 0;
    }

    memset(&rtmsg, 0, sizeof(rtmsg));
    rtmsg.hdr.rtm_type = cmd == 's'? RTM_ADD: RTM_DELETE;
    rtmsg.hdr.rtm_flags = RTF_UP | RTF_GATEWAY | RTF_STATIC;
    rtmsg.hdr.rtm_version = RTM_VERSION;
    rtmsg.hdr.rtm_seq = ++rtm_seq;
    rtmsg.hdr.rtm_addrs = RTA_DST | RTA_GATEWAY | RTA_NETMASK;
    rtmsg.dst.sin_len = sizeof(rtmsg.dst);
    rtmsg.dst.sin_family = AF_INET;
    rtmsg.gway.sin_len = sizeof(rtmsg.gway);
    rtmsg.gway.sin_family = AF_INET;
    rtmsg.gway.sin_addr.s_addr = g;
    rtmsg.mask.sin_len = sizeof(rtmsg.dst);
    rtmsg.mask.sin_family = AF_INET;

    rtmsg.hdr.rtm_msglen = sizeof(rtmsg);
    if (write(routes, &rtmsg, sizeof(rtmsg)) < 0) {
	syslog(LOG_ERR, "Couldn't %s default route: %d",
	       cmd=='s'? "add": "delete",errno);
	close(routes);
	return 0;
    }

    close(routes);
    default_route_gateway = (cmd == 's')? g: 0;
    return 1;
}

//==========================================================================

#if RTM_VERSION >= 3

/*
 * sifproxyarp - Make a proxy ARP entry for the peer.
 */
static struct {
    struct rt_msghdr		hdr;
    struct sockaddr_inarp	dst;
    struct sockaddr_dl		hwa;
    char			extra[128];
} arpmsg;

static int arpmsg_valid;

int
sifproxyarp(unit, hisaddr)
    int unit;
    u_int32_t hisaddr;
{
    int routes;

db_printf("%s called\n", __PRETTY_FUNCTION__);
    /*
     * Get the hardware address of an interface on the same subnet
     * as our local address.
     */
    memset(&arpmsg, 0, sizeof(arpmsg));
    if (!get_ether_addr(hisaddr, &arpmsg.hwa)) {
	syslog(LOG_ERR, "Cannot determine ethernet address for proxy ARP");
	return 0;
    }

    if ((routes = socket(PF_ROUTE, SOCK_RAW, AF_INET)) < 0) {
	syslog(LOG_ERR, "Couldn't add proxy arp entry: socket: %m");
	return 0;
    }

    arpmsg.hdr.rtm_type = RTM_ADD;
    arpmsg.hdr.rtm_flags = RTF_ANNOUNCE | RTF_HOST | RTF_STATIC;
    arpmsg.hdr.rtm_version = RTM_VERSION;
    arpmsg.hdr.rtm_seq = ++rtm_seq;
    arpmsg.hdr.rtm_addrs = RTA_DST | RTA_GATEWAY;
    arpmsg.hdr.rtm_inits = RTV_EXPIRE;
    arpmsg.dst.sin_len = sizeof(struct sockaddr_inarp);
    arpmsg.dst.sin_family = AF_INET;
    arpmsg.dst.sin_addr.s_addr = hisaddr;
    arpmsg.dst.sin_other = SIN_PROXY;

    arpmsg.hdr.rtm_msglen = (char *) &arpmsg.hwa - (char *) &arpmsg
	+ arpmsg.hwa.sdl_len;
    if (write(routes, &arpmsg, arpmsg.hdr.rtm_msglen) < 0) {
	syslog(LOG_ERR, "Couldn't add proxy arp entry: %m");
	close(routes);
	return 0;
    }

    close(routes);
    arpmsg_valid = 1;
    proxy_arp_addr = hisaddr;
    return 1;
}

/*
 * cifproxyarp - Delete the proxy ARP entry for the peer.
 */
int
cifproxyarp(unit, hisaddr)
    int unit;
    u_int32_t hisaddr;
{
    int routes;

db_printf("%s called\n", __PRETTY_FUNCTION__);
    if (!arpmsg_valid)
	return 0;
    arpmsg_valid = 0;

    arpmsg.hdr.rtm_type = RTM_DELETE;
    arpmsg.hdr.rtm_seq = ++rtm_seq;

    if ((routes = socket(PF_ROUTE, SOCK_RAW, AF_INET)) < 0) {
	syslog(LOG_ERR, "Couldn't delete proxy arp entry: socket: %m");
	return 0;
    }

    if (write(routes, &arpmsg, arpmsg.hdr.rtm_msglen) < 0) {
	syslog(LOG_ERR, "Couldn't delete proxy arp entry: %m");
	close(routes);
	return 0;
    }

    close(routes);
    proxy_arp_addr = 0;
    return 1;
}

//==========================================================================

#else	/* RTM_VERSION */

/*
 * sifproxyarp - Make a proxy ARP entry for the peer.
 */
int
sifproxyarp(unit, hisaddr)
    int unit;
    u_int32_t hisaddr;
{
    struct arpreq arpreq;
    struct {
	struct sockaddr_dl	sdl;
	char			space[128];
    } dls;

db_printf("%s called\n", __PRETTY_FUNCTION__);
    BZERO(&arpreq, sizeof(arpreq));

    /*
     * Get the hardware address of an interface on the same subnet
     * as our local address.
     */
    if (!get_ether_addr(hisaddr, &dls.sdl)) {
	syslog(LOG_ERR, "Cannot determine ethernet address for proxy ARP");
	return 0;
    }

    arpreq.arp_ha.sa_len = sizeof(struct sockaddr);
    arpreq.arp_ha.sa_family = AF_UNSPEC;
    BCOPY(LLADDR(&dls.sdl), arpreq.arp_ha.sa_data, dls.sdl.sdl_alen);
    SET_SA_FAMILY(arpreq.arp_pa, AF_INET);
    ((struct sockaddr_in *) &arpreq.arp_pa)->sin_addr.s_addr = hisaddr;
    arpreq.arp_flags = ATF_PERM | ATF_PUBL;
    if (ioctl(sockfd, SIOCSARP, (caddr_t)&arpreq) < 0) {
	syslog(LOG_ERR, "Couldn't add proxy arp entry: %m");
	return 0;
    }

    proxy_arp_addr = hisaddr;
    return 1;
}

/*
 * cifproxyarp - Delete the proxy ARP entry for the peer.
 */
int
cifproxyarp(unit, hisaddr)
    int unit;
    u_int32_t hisaddr;
{
    struct arpreq arpreq;

db_printf("%s called\n", __PRETTY_FUNCTION__);
    BZERO(&arpreq, sizeof(arpreq));
    SET_SA_FAMILY(arpreq.arp_pa, AF_INET);
    ((struct sockaddr_in *) &arpreq.arp_pa)->sin_addr.s_addr = hisaddr;
    if (ioctl(sockfd, SIOCDARP, (caddr_t)&arpreq) < 0) {
	syslog(LOG_WARNING, "Couldn't delete proxy arp entry: %m");
	return 0;
    }
    proxy_arp_addr = 0;
    return 1;
}
#endif	/* RTM_VERSION */


//==========================================================================
/*
 * get_ether_addr - get the hardware address of an interface on the
 * the same subnet as ipaddr.
 */
#define MAX_IFS		32

static int
get_ether_addr(ipaddr, hwaddr)
    u_int32_t ipaddr;
    struct sockaddr_dl *hwaddr;
{
    struct ifreq *ifr, *ifend, *ifp;
    u_int32_t ina, mask;
    struct sockaddr_dl *dla;
    struct ifreq ifreq;
    struct ifconf ifc;
    struct ifreq ifs[MAX_IFS];

db_printf("%s called\n", __PRETTY_FUNCTION__);
    ifc.ifc_len = sizeof(ifs);
    ifc.ifc_req = ifs;
    if (ioctl(sockfd, SIOCGIFCONF, &ifc) < 0) {
	syslog(LOG_ERR, "ioctl(SIOCGIFCONF): %m");
	return 0;
    }

    /*
     * Scan through looking for an interface with an Internet
     * address on the same subnet as `ipaddr'.
     */
    ifend = (struct ifreq *) (ifc.ifc_buf + ifc.ifc_len);
    for (ifr = ifc.ifc_req; ifr < ifend;
		ifr = (struct ifreq *) ((char *)&ifr->ifr_addr
		    + MAX(ifr->ifr_addr.sa_len, sizeof(ifr->ifr_addr)))) {
	if (ifr->ifr_addr.sa_family == AF_INET) {
	    ina = ((struct sockaddr_in *) &ifr->ifr_addr)->sin_addr.s_addr;
	    strncpy(ifreq.ifr_name, ifr->ifr_name, sizeof(ifreq.ifr_name));
	    /*
	     * Check that the interface is up, and not point-to-point
	     * or loopback.
	     */
	    if (ioctl(sockfd, SIOCGIFFLAGS, &ifreq) < 0)
		continue;
	    if ((ifreq.ifr_flags &
		 (IFF_UP|IFF_BROADCAST|IFF_POINTOPOINT|IFF_LOOPBACK|IFF_NOARP))
		 != (IFF_UP|IFF_BROADCAST))
		continue;
	    /*
	     * Get its netmask and check that it's on the right subnet.
	     */
	    if (ioctl(sockfd, SIOCGIFNETMASK, &ifreq) < 0)
		continue;
	    mask = ((struct sockaddr_in *) &ifreq.ifr_addr)->sin_addr.s_addr;
	    if ((ipaddr & mask) != (ina & mask))
		continue;

	    break;
	}
    }

    if (ifr >= ifend)
	return 0;
    syslog(LOG_INFO, "found interface %s for proxy arp", ifr->ifr_name);

    /*
     * Now scan through again looking for a link-level address
     * for this interface.
     */
    ifp = ifr;
    for (ifr = ifc.ifc_req; ifr < ifend; ) {
	if (strcmp(ifp->ifr_name, ifr->ifr_name) == 0
	    && ifr->ifr_addr.sa_family == AF_LINK) {
	    /*
	     * Found the link-level address - copy it out
	     */
	    dla = (struct sockaddr_dl *) &ifr->ifr_addr;
	    BCOPY(dla, hwaddr, dla->sdl_len);
	    return 1;
	}
	ifr = (struct ifreq *) ((char *)&ifr->ifr_addr
	    + MAX(ifr->ifr_addr.sa_len, sizeof(ifr->ifr_addr)));
    }

    return 0;
}

//==========================================================================
/*
 * Return user specified netmask, modified by any mask we might determine
 * for address `addr' (in network byte order).
 * Here we scan through the system's list of interfaces, looking for
 * any non-point-to-point interfaces which might appear to be on the same
 * network as `addr'.  If we find any, we OR in their netmask to the
 * user-specified netmask.
 */
u_int32_t
GetMask(addr)
    u_int32_t addr;
{
    u_int32_t mask, nmask, ina;
    struct ifreq *ifr, *ifend, ifreq;
    struct ifconf ifc;
    struct ifreq ifs[MAX_IFS];

    addr = ntohl(addr);
    if (IN_CLASSA(addr))	/* determine network mask for address class */
	nmask = IN_CLASSA_NET;
    else if (IN_CLASSB(addr))
	nmask = IN_CLASSB_NET;
    else
	nmask = IN_CLASSC_NET;
    /* class D nets are disallowed by bad_ip_adrs */
    mask = netmask | htonl(nmask);

    /*
     * Scan through the system's network interfaces.
     */
    ifc.ifc_len = sizeof(ifs);
    ifc.ifc_req = ifs;
    if (ioctl(sockfd, SIOCGIFCONF, &ifc) < 0) {
	syslog(LOG_WARNING, "ioctl(SIOCGIFCONF): %m");
	return mask;
    }
    ifend = (struct ifreq *) (ifc.ifc_buf + ifc.ifc_len);
    for (ifr = ifc.ifc_req; ifr < ifend;
		ifr = (struct ifreq *) ((char *)&ifr->ifr_addr
		    + MAX(ifr->ifr_addr.sa_len, sizeof(ifr->ifr_addr)))) {
	/*
	 * Check the interface's internet address.
	 */
	if (ifr->ifr_addr.sa_family != AF_INET)
	    continue;
	ina = ((struct sockaddr_in *) &ifr->ifr_addr)->sin_addr.s_addr;
	if ((ntohl(ina) & nmask) != (addr & nmask))
	    continue;
	/*
	 * Check that the interface is up, and not point-to-point or loopback.
	 */
	strncpy(ifreq.ifr_name, ifr->ifr_name, sizeof(ifreq.ifr_name));
	if (ioctl(sockfd, SIOCGIFFLAGS, &ifreq) < 0)
	    continue;
	if ((ifreq.ifr_flags & (IFF_UP|IFF_POINTOPOINT|IFF_LOOPBACK))
	    != IFF_UP)
	    continue;
	/*
	 * Get its netmask and OR it into our mask.
	 */
	if (ioctl(sockfd, SIOCGIFNETMASK, &ifreq) < 0)
	    continue;
	mask |= ((struct sockaddr_in *)&ifreq.ifr_addr)->sin_addr.s_addr;
    }

    return mask;
}

//==========================================================================
/*
 * Use the hostid as part of the random number seed.
 */
int
get_host_seed()
{
//db_printf("%s called\n", __PRETTY_FUNCTION__);
#ifndef __ECOS
    return gethostid();
#endif
    return 0;
}

//=====================================================================
// PAP stubs
//
// When omitting PAP, these fill in the dangling references from auth.c
//

#ifndef CYGPKG_PPP_PAP

void
upap_authwithpeer(unit, user, password)
    int unit;
    char *user, *password;
{
    unit=unit;
    user=user;
    password=password;
}

void
upap_authpeer(unit)
    int unit;
{
    unit=unit;
}

#endif

//=====================================================================
// CHAP stubs
//
// When omitting CHAP, these fill in the dangling references from auth.c
//

#ifndef CYGPKG_PPP_CHAP

void
ChapAuthWithPeer(unit, our_name, digest)
    int unit;
    char *our_name;
    int digest;
{
    unit=unit;
    our_name=our_name;
    digest=digest;
}

void
ChapAuthPeer(unit, our_name, digest)
    int unit;
    char *our_name;
    int digest;
{
    unit=unit;
    our_name=our_name;
    digest=digest;
}

#endif

//=====================================================================
// eCos API

externC cyg_int32 cyg_ppp_options_init( cyg_ppp_options_t *options )
{
    if( options == NULL )
        return -1;
    
    options->debug              = 0;
    options->kdebugflag         = 0;
    options->default_route      = 1;
    options->modem              = 0;
    options->flowctl            = CYG_PPP_FLOWCTL_HARDWARE;
    options->refuse_pap         = 0;
    options->refuse_chap        = 0;
    options->neg_accm           = 0;
    options->conf_accm          = 0;

    options->baud               = CYGNUM_SERIAL_BAUD_115200;
    
    options->idle_time_limit    = 1*60;
    options->maxconnect         = 0;

    options->our_address        = 0;
    options->his_address        = 0;

    options->script             = NULL;
    
    strncpy( options->user, CYGPKG_PPP_AUTH_DEFAULT_USER, MAXNAMELEN );
    strncpy( options->passwd, CYGPKG_PPP_AUTH_DEFAULT_PASSWD, MAXSECRETLEN );

    return 0;
}

// -------------------------------------------------------------------------


#define CYGNUM_PPP_PPPD_THREAD_STACK_SIZE (CYGNUM_HAL_STACK_SIZE_TYPICAL+0x1000)

static char cyg_pppd_stack[CYGNUM_PPP_PPPD_THREAD_STACK_SIZE];
static cyg_thread cyg_pppd_thread_obj;

static char cyg_ppp_tx_thread_stack[CYGNUM_HAL_STACK_SIZE_TYPICAL];
static cyg_thread cyg_ppp_tx_thread_obj;


externC void cyg_pppd_main(CYG_ADDRWORD arg);


externC cyg_ppp_handle_t cyg_ppp_up( const char *devnam_arg,
                                     const cyg_ppp_options_t *options )
{

    if( options == NULL || phase != PHASE_DEAD )
        return 0;
    
    // Initialize control block    
   	memset(&ppp_tty, 0, sizeof(struct tty));

    strncpy( devnam, devnam_arg, PATH_MAX );

    ppp_tty.options = options;

    // Start the PPPD thread
    cyg_thread_create(CYGNUM_PPP_PPPD_THREAD_PRIORITY,
                      cyg_pppd_main,
                      (CYG_ADDRWORD)&ppp_tty,
                      "PPPD",
                      &cyg_pppd_stack[0],
                      CYGNUM_PPP_PPPD_THREAD_STACK_SIZE,
                      &ppp_tty.pppd_thread,
                      &cyg_pppd_thread_obj
            );
    cyg_thread_resume(ppp_tty.pppd_thread);

    // Start the TX thread
    cyg_semaphore_init( &ppp_tty.tx_sem,  0 );
    
    cyg_thread_create(CYGNUM_PPP_PPPD_THREAD_PRIORITY+1,
                      cyg_ppp_tx_thread,
                      (CYG_ADDRWORD)&ppp_tty,
                      "PPP Tx Thread",
                      &cyg_ppp_tx_thread_stack[0],
                      sizeof(cyg_ppp_tx_thread_stack),
                      &ppp_tty.tx_thread,
                      &cyg_ppp_tx_thread_obj
            );
    cyg_thread_resume(ppp_tty.tx_thread);

    // Wait for the PPPD thread to get going and start the PPP
    // initialization phase.
    while(phase == PHASE_DEAD )
        cyg_thread_delay(100);
    
    return (cyg_ppp_handle_t)&ppp_tty;
}

// -------------------------------------------------------------------------

externC char **script;

externC void cyg_ppp_options_install( const cyg_ppp_options_t *options )
{
    debug               = options->debug;
    kdebugflag          = options->kdebugflag;
    
    modem               = options->modem;
    flowctl             = options->flowctl;
    refuse_pap          = options->refuse_pap;
    refuse_chap         = options->refuse_chap;
    neg_accm            = options->neg_accm;
    conf_accm           = options->conf_accm;

    inspeed             = options->baud;
    
    idle_time_limit     = options->idle_time_limit;
    maxconnect          = options->maxconnect;

    script              = options->script;
    
    strncpy( user, &options->user[0], MAXNAMELEN );
    strncpy( passwd, &options->passwd[0], MAXSECRETLEN );
    
}

// -------------------------------------------------------------------------

externC cyg_int32 cyg_ppp_down( const cyg_ppp_handle_t handle )
{
    if( phase != PHASE_DEAD )
    {
        externC int kill_link;
        kill_link = 1;
        cyg_thread_release( ppp_tty.pppd_thread );
        ppp_tty.pppd_wakeup = 1;    
        return 0;
    }
    else
        return -1;
}

// -------------------------------------------------------------------------

externC cyg_int32 cyg_ppp_wait_up( cyg_ppp_handle_t handle )
{
    while(!( (phase == PHASE_NETWORK && ifaddrs[0] != 0) ||
             phase == PHASE_DEAD ) )
        cyg_thread_delay(100);

    return phase == PHASE_NETWORK ? 0 : -1;
}

// -------------------------------------------------------------------------

externC void cyg_ppp_wait_down( cyg_ppp_handle_t handle )
{
    while( ppp_tty.tx_thread_running || ppp_tty.pppd_thread_running )
        cyg_thread_delay(100);
    
    cyg_thread_delete( ppp_tty.tx_thread );
    cyg_thread_delete( ppp_tty.pppd_thread );
}

// -------------------------------------------------------------------------
#ifdef CYGOPT_PPP_NS_NEGOTIATE
externC u_int32_t cyg_ppp_get_neg_addrs(cyg_ppp_neg_addrs_t *addrs)
{
	if (phase == PHASE_NETWORK && ifaddrs[0] != 0)
	{
		addrs->local_ip = ipcp_gotoptions[0].ouraddr;
		addrs->peer_ip = ipcp_hisoptions[0].hisaddr;
		addrs->pri_dns = ipcp_gotoptions[0].dnsaddr[0];
		addrs->alt_dns = ipcp_gotoptions[0].dnsaddr[1];
		addrs->pri_wins = ipcp_gotoptions[0].winsaddr[0];
		addrs->alt_wins = ipcp_gotoptions[0].winsaddr[1];
		return(1);
	}
	else
	{
		return(0);
	}
}
#endif
//=====================================================================
// eCos extras

void syslog( int level, char *fmt, ... )
{
    va_list ap;
    int ret;

#ifdef CYGPKG_PPP_DEBUG_WARN_ONLY
    if(!( level == LOG_ERR ||
          level == LOG_WARNING ))
        return;
#endif
    
    va_start(ap, fmt);
    diag_printf("SYSLOG %02x: ",level);
    ret = diag_vprintf(fmt, ap);
    diag_printf("\n");
    va_end(ap);
}

//=====================================================================

char *crypt (const char *key, const char *salt)
{
    static char res[13];

    db_printf("%s called\n", __PRETTY_FUNCTION__);
    
    return res;
}


//=====================================================================
/*
 * Substitute procedures for those systems which don't have
 * drand48 et al.
 */

double
drand48(void)
{
    return (double)rand() / (double)0x7fffffffL; /* 2**31-1 */
}

long
mrand48(void)
{
    return rand();
}

void
srand48(long seedval)
{
    srand(seedval);
}


//=====================================================================

#if 0

#undef MD5Init
#undef MD5Update
#undef MD5Final

#include <sys/types.h>

#include <sys/md5.h>


void   cyg_MD5Init( MD5_CTX *ctx );
void   cyg_MD5Update (MD5_CTX *ctx, const unsigned char *buf, unsigned int size);
void   cyg_MD5Final (unsigned char hash[16], MD5_CTX *ctx);
  

void   cyg_ppp_MD5Init( MD5_CTX *ctx )
{
    db_printf("%s called\n", __PRETTY_FUNCTION__);
    cyg_MD5Init( ctx );
    return;
}

void   cyg_ppp_MD5Update (MD5_CTX *ctx, const unsigned char *buf, unsigned int size)
{
    db_printf("%s called\n", __PRETTY_FUNCTION__);
    cyg_MD5Update( ctx, buf, size );
    return;
}

void   cyg_ppp_MD5Final (unsigned char hash[16], MD5_CTX *ctx)
{
    db_printf("%s called\n", __PRETTY_FUNCTION__);
    cyg_MD5Final( hash, ctx );
    return;
}

#endif

//=====================================================================
// End of sys-ecos.c


