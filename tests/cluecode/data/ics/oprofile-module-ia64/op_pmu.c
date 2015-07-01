 * @file op_pmu.c
 * Setup and handling of IA64 Performance Monitoring Unit (PMU)
 *
 * @remark Copyright 2002 OProfile authors
 * @remark Read the file COPYING
 *

/* performance counters are in pairs: pmcN and pmdN.  The pmc register acts
 * as the event selection; the pmd register is the counter. */
#define perf_reg(c)	((c)+4)

#define IA64_1_PMD_MASK_VAL	((1UL << 32) - 1)
/* The appropriate value is selected in pmu_init() */
unsigned long pmd_mask = IA64_2_PMD_MASK_VAL;

#define pmd_overflowed(r, c) ((r) & (1 << perf_reg(c)))
#define set_pmd_neg(v, c) do { \
	ia64_set_pmd(perf_reg(c), -(ulong)(v) & pmd_mask); \
	ia64_srlz_d(); } while (0)
#define set_pmd(v, c) do { \
	ia64_set_pmd(perf_reg(c), (v) & pmd_mask); \
	ia64_srlz_d(); } while (0)
#define set_pmc(v, c) do { ia64_set_pmc(perf_reg(c), (v)); ia64_srlz_d(); } while (0)
#define get_pmd(c) ia64_get_pmd(perf_reg(c))
#define get_pmc(c) ia64_get_pmc(perf_reg(c))

/* ---------------- IRQ handler ------------------ */
/* from linux/arch/ia64/kernel/perfmon.c */
/*
 * Originaly Written by Ganesh Venkitachalam, IBM Corp.
 * Copyright (C) 1999 Ganesh Venkitachalam <venkitac@us.ibm.com>
 *
 * Modifications by Stephane Eranian, Hewlett-Packard Co.
 * Modifications by David Mosberger-Tang, Hewlett-Packard Co.
 *
 * Copyright (C) 1999-2002  Hewlett Packard Co
 *               Stephane Eranian <eranian@hpl.hp.com>
 *               David Mosberger-Tang <davidm@hpl.hp.com>