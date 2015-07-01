 * project 2001.
 */
/* ====================================================================
 * Copyright (c) 1999-2001 The OpenSSL Project.  All rights reserved.
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
	if(!c->dirs)
		{
		ENGINEerr(ENGINE_F_DYNAMIC_SET_DATA_CTX,ERR_R_MALLOC_FAILURE);
		OPENSSL_free(c);
		return 0;
		}
	CRYPTO_w_unlock(CRYPTO_LOCK_ENGINE);
	/* If we lost the race to set the context, c is non-NULL and *ctx is the
	 * context of the thread that won. */
	if(c)
		OPENSSL_free(c);
	return 1;
	}