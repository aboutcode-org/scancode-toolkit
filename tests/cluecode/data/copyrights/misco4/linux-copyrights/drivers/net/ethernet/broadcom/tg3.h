* Copyright (C) 2001, 2002, 2003, 2004 David S. Miller (davem@redhat.com)
 * Copyright (C) 2001 Jeff Garzik (jgarzik@pobox.com)
 * Copyright (C) 2004 Sun Microsystems Inc.
 * Copyright (C) 2007-2016 Broadcom Corporation.
 * Copyright (C) 2016-2017 Broadcom Limited.
 * Copyright (C) 2018 Broadcom. All Rights Reserved. The term "Broadcom"
 * refers to Broadcom Inc. and/or its subsidiaries.
 */


	/* Statistics maintained by Receive MAC. */
	tg3_stat64_t			rx_octets;
	u64				__reserved1;


	/* Statistics maintained by Transmit MAC. */
	tg3_stat64_t			tx_octets;
	u64				__reserved2;


	/* Statistics maintained by Receive List Placement. */
	tg3_stat64_t			COS_rx_packets[16];
	tg3_stat64_t			COS_rx_filter_dropped;


	/* Statistics maintained by Host Coalescing. */
	tg3_stat64_t			ring_set_send_prod_index;
	tg3_stat64_t			ring_status_update;


	/* Statistics maintained by Receive MAC. */
	u64		rx_octets;
	u64		rx_fragments;


	/* Statistics maintained by Transmit MAC. */
	u64		tx_octets;
	u64		tx_collisions;


	/* Statistics maintained by Receive List Placement. */
	u64		dma_writeq_full;
	u64		dma_write_prioq_full;


	/* Statistics maintained by Host Coalescing. */
	u64		ring_set_send_prod_index;
	u64		ring_status_update;