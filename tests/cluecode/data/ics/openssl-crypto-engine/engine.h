 * project 2000.
 */
/* ====================================================================
 * Copyright (c) 1999-2004 The OpenSSL Project.  All rights reserved.
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
 *
 */
/* ====================================================================
 * Copyright 2002 Sun Microsystems, Inc. ALL RIGHTS RESERVED.
 * ECDH support in OpenSSL originally developed by 
 * SUN MICROSYSTEMS, INC., and contributed to the OpenSSL project.
 * function and command settings. It should not adjust the structural or
 * functional reference counts. If this function returns zero, (a) the load will
 * be aborted, (b) the previous ENGINE state will be memcpy'd back onto the
 * structure, and (c) the shared library will be unloaded. So implementations
 * should do their own internal cleanup in failure circumstances otherwise they
 * could leak. The 'id' parameter, if non-NULL, represents the ENGINE id that