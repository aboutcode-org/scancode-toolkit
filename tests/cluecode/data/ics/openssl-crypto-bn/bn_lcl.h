/* crypto/bn/bn_lcl.h */
/* Copyright (C) 1995-1998 Eric Young (eay@cryptsoft.com)
 * All rights reserved.
 *
 * the following conditions are aheared to.  The following conditions
 * apply to all code found in this distribution, be it the RC4, RSA,
 * lhash, DES, etc., code; not just the SSL code.  The SSL documentation
 * included with this distribution is covered by the same copyright terms
 * except that the holder is Tim Hudson (tjh@cryptsoft.com).
 * 
 * Copyright remains Eric Young's, and as such any Copyright notices in
 * the code are not to be removed.
 * If this package is used in a product, Eric Young should be given attribution
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * [including the GNU Public Licence.]
 */
/* ====================================================================
 * Copyright (c) 1998-2000 The OpenSSL Project.  All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer. 
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
#ifdef BN_LLONG
#define mul_add(r,a,w,c) { \
	BN_ULLONG t; \
	t=(BN_ULLONG)w * (a) + (r) + (c); \
	(r)= Lw(t); \
	(c)= Hw(t); \
	}

#define mul(r,a,w,c) { \
	BN_ULLONG t; \
	t=(BN_ULLONG)w * (a) + (c); \
	(r)= Lw(t); \
	(c)= Hw(t); \
	}

	BN_ULONG high,low,ret,tmp=(a);	\
	ret =  (r);			\
	BN_UMULT_LOHI(low,high,w,tmp);	\
	ret += (c);			\
	(c) =  (ret<(c))?1:0;		\
	(c) += high;			\
	ret += low;			\
	(c) += (ret<low)?1:0;		\
	(r) =  ret;			\
	}
#define mul(r,a,w,c)	{		\
	BN_ULONG high,low,ret,ta=(a);	\
	BN_UMULT_LOHI(low,high,w,ta);	\
	ret =  low + (c);		\
	(c) =  high;			\
	(c) += (ret<low)?1:0;		\
	(r) =  ret;			\
	}
	BN_ULONG high,low,ret,tmp=(a);	\
	ret =  (r);			\
	high=  BN_UMULT_HIGH(w,tmp);	\
	ret += (c);			\
	low =  (w) * tmp;		\
	(c) =  (ret<(c))?1:0;		\
	(c) += high;			\
	ret += low;			\
	(c) += (ret<low)?1:0;		\
	(r) =  ret;			\
	}
	BN_ULONG high,low,ret,ta=(a);	\
	low =  (w) * ta;		\
	high=  BN_UMULT_HIGH(w,ta);	\
	ret =  low + (c);		\
	(c) =  high;			\
	(c) += (ret<low)?1:0;		\
	(r) =  ret;			\
	}
	mul64(l,h,(bl),(bh)); \
 \
	/* non-multiply part */ \
	l=(l+(c))&BN_MASK2; if (l < (c)) h++; \
	(c)=(r); \
	l=(l+(c))&BN_MASK2; if (l < (c)) h++; \
	(c)=h&BN_MASK2; \
	(r)=l; \
	}
	mul64(l,h,(bl),(bh)); \
 \
	/* non-multiply part */ \
	l+=(c); if ((l&BN_MASK2) < (c)) h++; \
	(c)=h&BN_MASK2; \
	(r)=l&BN_MASK2; \
	}