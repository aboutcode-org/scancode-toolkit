/*
 * Copyright (c) 1995 Danny Gasparovski.
 *
 * Please read the file COPYRIGHT for the
 * terms and conditions of the copyright.
 */

			c = *bptr;
			*bptr++ = (char)0;
			argv[i++] = strdup(curarg);
		   } while (c);

                argv[i] = NULL;