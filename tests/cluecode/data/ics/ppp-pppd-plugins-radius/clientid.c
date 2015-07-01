/*
 * $Id: clientid.c,v 1.1 2004/11/14 07:26:26 paulus Exp $
 *
 * Copyright (C) 1995,1996,1997 Lars Fenneberg
 *
 * See the file COPYRIGHT for the respective terms and conditions.
 * If the file is missing contact me at lf@elemental.net
 * and I'll send you a copy.
		if (( c = strchr(q, ' ')) || (c = strchr(q,'\t'))) {

			*c = '\0'; c++;
			SKIP(c);

			name = q;