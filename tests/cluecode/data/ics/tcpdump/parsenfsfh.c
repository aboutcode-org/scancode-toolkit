/*
 * Copyright (c) 1993, 1994 Jeffrey C. Mogul, Digital Equipment Corporation,
 * Western Research Laboratory. All rights reserved.
 * Copyright (c) 2001 Compaq Computer Corporation. All rights reserved.
 *
 *  Permission to use, copy, and modify this software and its
 *  documentation is hereby granted only under the following terms and
 *  conditions.  Both the above copyright notice and this permission
 *  notice must appear in all copies of the software, derivative works
 *  or modified versions, and any portions thereof, and both notices
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions
 *  are met:
 *    1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *    2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
#endif

#define	make_uint32(msb,b,c,lsb)\
	(XFF(lsb) + (XFF(c)<<8) + (XFF(b)<<16) + (XFF(msb)<<24))

#define	make_uint24(msb,b, lsb)\
#ifdef	__alpha
	/* or other 64-bit systems */
#define	make_uint48(msb,b,c,d,e,lsb)\
	((lsb) + ((e)<<8) + ((d)<<16) + ((c)<<24) + ((b)<<32) + ((msb)<<40))
#else
	/* on 32-bit systems ignore high-order bits */
#define	make_uint48(msb,b,c,d,e,lsb)\
	((lsb) + ((e)<<8) + ((d)<<16) + ((c)<<24))
#endif
