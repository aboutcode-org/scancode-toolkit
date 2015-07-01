/* Copyright (C) 2007 ARC International (UK) LTD */

#include "asm.h"

#ifdef __LITTLE_ENDIAN__
#define WORD2 r2
#define SHIFT r3
#else /* BIG ENDIAN */
#define WORD2 r3
#define SHIFT r2
#endif

ENTRY(memcmp)
	or	r12,r0,r1
	asl_s	r12,r12,30
#ifdef __ARC700__
	sub_l	r3,r2,1
	brls	r2,r12,.Lbytewise
#else
	brls.d	r2,r12,.Lbytewise
	sub_s	r3,r2,1
#endif
	ld	r4,[r0,0]
	ld	r5,[r1,0]
	lsr.f	lp_count,r3,3
	lpne	.Loop_end
	ld_s	WORD2,[r0,4]
	ld_s	r12,[r1,4]
	brne	r4,r5,.Leven
	ld.a	r4,[r0,8]
	ld.a	r5,[r1,8]
	brne	WORD2,r12,.Lodd
