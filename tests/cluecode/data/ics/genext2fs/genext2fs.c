// genext2fs.c
//
// ext2 filesystem generator for embedded systems
// Copyright (C) 2000 Xavier Bestel <xavier.bestel@free.fr>
//
// Please direct support requests to genext2fs-devel@lists.sourceforge.net
//
// 'du' portions taken from coreutils/du.c in busybox:
//	Copyright (C) 1999,2000 by Lineo, inc. and John Beppu
//	Copyright (C) 1999,2000,2001 by John Beppu <beppu@codepoet.org>
//	Copyright (C) 2002  Edward Betts <edward@debian.org>
//
// This program is free software; you can redistribute it and/or
// 	23 Mar 2002	Bugfix: test for IFCHR or IFBLK was flawed
// 	10 Oct 2002	Added comments,makefile targets,	vsundar@ixiacom.com    
// 			endianess swap assert check.  
// 			Copyright (C) 2002 Ixia communications
// 	12 Oct 2002	Added support for triple indirection	vsundar@ixiacom.com
// 			Copyright (C) 2002 Ixia communications
// 	14 Oct 2002	Added support for groups		vsundar@ixiacom.com
// 			Copyright (C) 2002 Ixia communications
// 	 5 Jan 2003	Bugfixes: reserved inodes should be set vsundar@usc.edu
// 			only in the first group; directory names

	while((c = getopt(argc, argv,      "x:d:D:b:i:N:m:g:e:zfqUPahVv")) != EOF) {
#endif /* HAVE_GETOPT_LONG */
		switch(c)
		{
			case 'x':