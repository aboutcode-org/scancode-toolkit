/*
 * -- <linux/cdrom.h>
 * General header file for linux CD-ROM drivers 
 * Copyright (C) 1992         David Giller, rafetmad@oxy.edu
 *               1994, 1995   Eberhard Moenkeberg, emoenke@gwdg.de
 *               1996         David van Leeuwen, david@tm.tno.nl

/* DVD struct types */
#define DVD_STRUCT_PHYSICAL	0x00
#define DVD_STRUCT_COPYRIGHT	0x01
#define DVD_STRUCT_DISCKEY	0x02
#define DVD_STRUCT_BCA		0x03
	struct dvd_layer layer[DVD_LAYERS];
};

struct dvd_copyright {
	__u8 type;

	__u8 type;

	struct dvd_physical	physical;
	struct dvd_copyright	copyright;
	struct dvd_disckey	disckey;
	struct dvd_bca		bca;
	dvd_challenge chal;
};

#define DVD_CPM_NO_COPYRIGHT	0
#define DVD_CPM_COPYRIGHTED	1

#define DVD_CP_SEC_NONE		0