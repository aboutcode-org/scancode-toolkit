/* Copyright (C) 2007 ARC International (UK) LTD */

#include "asm.h"

/* In order to search for a zero in a W, we calculate
   X := (W - 0x01010101) & ~W & 0x80808080;
   In the little endian case:
     If no byte in W is zero, X will be zero; otherwise, the least significant
     byte of X which is nonzero indicates the least significant byte of W that
     is zero.

     W is zero, otherwise that byte of Y is 0.  */

#if !defined(__ARC700__) && !defined(__A4__)
ENTRY(strchr)
	bmsk.f	r2,r0,1
	mov_s	r3,0x01010101
	extb_s	r1,r1
	asl	r5,r1,8
	or	r5,r5,r1
	beq.d	.Laligned
	asl	r4,r5,16
        sub_s   r0,r0,r2
        asl_s   r2,r2,3
#ifdef	__LITTLE_ENDIAN__
        asl     r7,r3,r2
#else
        lsr     r7,r3,r2
#endif
#endif /* !__ARC_700__ */
