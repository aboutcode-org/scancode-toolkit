/*	Id: racoonctl.c,v 1.11 2006/04/06 17:06:25 manubsd Exp */

/*
 * Copyright (C) 1995, 1996, 1997, and 1998 WIDE Project.
 * Copyright (C) 2008 Timo Teras.
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
	setenv("POSIXLY_CORRECT", "1", 0);
#endif
	while ((c = getopt(ac, av, "lds:")) != -1) {
		switch(c) {
		case 'l':
			long_format++;