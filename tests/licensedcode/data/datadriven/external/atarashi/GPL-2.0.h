/****************************************************************************
 * ip_conntrack_h323_asn1.h - BER and PER decoding library for H.323
 * 			      conntrack/NAT module.
 *
 * Copyright (c) 2006 by Jing Min Zhao <zhaojingmin@users.sourceforge.net>
 *
 * This source code is licensed under General Public License version 2.
 *
 *
 * This library is based on H.225 version 4, H.235 version 2 and H.245
 * version 7. It is extremely optimized to decode only the absolutely
 * necessary objects in a signal for Linux kernel NAT module use, so don't
 * expect it to be a full ASN.1 library.
 *
 * Features:
 *
 * 1. Small. The total size of code plus data is less than 20 KB (IA32).
 * 2. Fast. Decoding Netmeeting's Setup signal 1 million times on a PIII 866
 *    takes only 3.9 seconds.
 * 3. No memory allocation. It uses a static object. No need to initialize or
 *    cleanup.
 * 4. Thread safe.
 * 5. Support embedded architectures that has no misaligned memory access
 *    support.
 *
 * Limitations:
 *
 * 1. At most 30 faststart entries. Actually this is limited by ethernet's MTU.
 *    If a Setup signal contains more than 30 faststart, the packet size will
 *    very likely exceed the MTU size, then the TPKT will be fragmented. I
 *    don't know how to handle this in a Netfilter module. Anybody can help?
 *    Although I think 30 is enough for most of the cases.
 * 2. IPv4 addresses only.
 *
 ****************************************************************************/

#ifndef _NF_CONNTRACK_HELPER_H323_ASN1_H_
#define _NF_CONNTRACK_HELPER_H323_ASN1_H_

/*****************************************************************************
 * H.323 Types
 ****************************************************************************/
#include <linux/netfilter/nf_conntrack_h323_types.h>

typedef struct
