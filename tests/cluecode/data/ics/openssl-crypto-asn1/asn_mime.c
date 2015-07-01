 * project.
 */
/* ====================================================================
 * Copyright (c) 1999-2008 The OpenSSL Project.  All rights reserved.
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
		if(!(tmpname = BUF_strdup(name))) return NULL;
		for(p = tmpname ; *p; p++) {
			c = *p;
			if(isupper(c)) {
				c = tolower(c);
				*p = c;
			}
		if(!(tmpval = BUF_strdup(value))) return NULL;
		for(p = tmpval ; *p; p++) {
			c = *p;
			if(isupper(c)) {
				c = tolower(c);
				*p = c;
			}
		if(!tmpname) return 0;
		for(p = tmpname ; *p; p++) {
			c = *p;
			if(isupper(c)) {
				c = tolower(c);
				*p = c;
			}