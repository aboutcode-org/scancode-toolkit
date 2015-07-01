 * project 2000.
 */
/* ====================================================================
 * Copyright (c) 2000-2005 The OpenSSL Project.  All rights reserved.
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

/* Macro to initialize and invalidate the cache */

#define asn1_tlc_clear(c)	if (c) (c)->valid = 0
/* Version to avoid compiler warning about 'c' always non-NULL */
#define asn1_tlc_clear_nc(c)	(c)->valid = 0

/* Decode an ASN1 item, this currently behaves just 