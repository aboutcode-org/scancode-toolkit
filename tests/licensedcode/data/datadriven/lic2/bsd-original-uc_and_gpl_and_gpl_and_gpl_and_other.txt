/* fdisk.c -- Partition table manipulator for Linux.
 *
 * Copyright (C) 1992  A. V. Le Blanc (LeBlanc@mcc.ac.uk)
 *
 * This program is free software.  You can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation: either version 1 or
 * (at your option) any later version.
 *
 * Vladimir Oleynik <dzo@simtreas.ru> 2001,2002 Busybox port
 */

#define UTIL_LINUX_VERSION "2.12"

#define PROC_PARTITIONS "/proc/partitions"

#include <sys/types.h>
#include <sys/stat.h>           /* stat */
#include <ctype.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <setjmp.h>
#include <assert.h>             /* assert */
#include <getopt.h>
#include <endian.h>
#include <sys/ioctl.h>
#include <sys/param.h>
#include <sys/sysmacros.h>     /* major */

#include <stdint.h>        /* for uint32_t, uint16_t, uint8_t, int16_t, etc */

/* Copied from linux/major.h */
#define FLOPPY_MAJOR    2

#include <sys/utsname.h>

#include "busybox.h"

#define MAKE_VERSION(p,q,r)     (65536*(p) + 256*(q) + (r))

#define DKTYPENAMES

#define _(Text) Text

#define BLKRRPART  _IO(0x12,95)    /* re-read partition table */
#define BLKGETSIZE _IO(0x12,96)    /* return device size */
#define BLKFLSBUF  _IO(0x12,97)    /* flush buffer cache */
#define BLKSSZGET  _IO(0x12,104)   /* get block device sector size */

/* Avoid conflicts with the 2.6 kernel headers, which define
 * _IOR rather differently */
#undef _IOR
#define _IOR(type,nr,size)      _IOC(_IOC_READ,(type),(nr),sizeof(size))
#define BLKGETSIZE64 _IOR(0x12,114,uint64_t)

/*
   fdisk.h
*/

#define DEFAULT_SECTOR_SIZE     512
#define MAX_SECTOR_SIZE 2048
#define SECTOR_SIZE     512     /* still used in BSD code */
#define MAXIMUM_PARTS   60

#define ACTIVE_FLAG     0x80

#define EXTENDED        0x05
#define WIN98_EXTENDED  0x0f
#define LINUX_PARTITION 0x81
#define LINUX_SWAP      0x82
#define LINUX_NATIVE    0x83
#define LINUX_EXTENDED  0x85
#define LINUX_LVM       0x8e
#define LINUX_RAID      0xfd

#define SUNOS_SWAP 3
#define WHOLE_DISK 5

#define IS_EXTENDED(i) \
	((i) == EXTENDED || (i) == WIN98_EXTENDED || (i) == LINUX_EXTENDED)

#define SIZE(a) (sizeof(a)/sizeof((a)[0]))

#define cround(n)       (display_in_cyl_units ? ((n)/units_per_sector)+1 : (n))
#define scround(x)      (((x)+units_per_sector-1)/units_per_sector)

#ifdef CONFIG_FEATURE_SUN_LABEL
#define SCSI_IOCTL_GET_IDLUN 0x5382
#endif


/* including <linux/hdreg.h> also fails */
struct hd_geometry {
      unsigned char heads;
      unsigned char sectors;
      unsigned short cylinders;
      unsigned long start;
};

#define HDIO_GETGEO             0x0301  /* get device geometry */


struct systypes {
	const unsigned char *name;
};

static uint    sector_size = DEFAULT_SECTOR_SIZE,
	user_set_sector_size,
	sector_offset = 1;

/*
 * Raw disk label. For DOS-type partition tables the MBR,
 * with descriptions of the primary partitions.
 */
static char MBRbuffer[MAX_SECTOR_SIZE];

#ifdef CONFIG_FEATURE_SUN_LABEL
static int     sun_label;                  /* looking at sun disklabel */
#else
#define sun_label 0
#endif
#ifdef CONFIG_FEATURE_SGI_LABEL
static int     sgi_label;                  /* looking at sgi disklabel */
#else
#define sgi_label 0
#endif
#ifdef CONFIG_FEATURE_AIX_LABEL
static int     aix_label;                  /* looking at aix disklabel */
#else
#define aix_label 0
#endif
#ifdef CONFIG_FEATURE_OSF_LABEL
static int     osf_label;                  /* looking at OSF/1 disklabel */
static int     possibly_osf_label;
#else
#define osf_label 0
#endif

#define dos_label (!sun_label && !sgi_label && !aix_label && !osf_label)

static uint heads, sectors, cylinders;
static void update_units(void);


/*
 * return partition name - uses static storage unless buf is supplied
 */
static const char *
partname(const char *dev, int pno, int lth) {
	static char buffer[80];
	const char *p;
	int w, wp;
	int bufsiz;
	char *bufp;

	bufp = buffer;
	bufsiz = sizeof(buffer);

	w = strlen(dev);
	p = "";

	if (isdigit(dev[w-1]))
		p = "p";

	/* devfs kludge - note: fdisk partition names are not supposed
	   to equal kernel names, so there is no reason to do this */
	if (strcmp (dev + w - 4, "disc") == 0) {
		w -= 4;
		p = "part";
	}

	wp = strlen(p);

	if (lth) {
		snprintf(bufp, bufsiz, "%*.*s%s%-2u",
			 lth-wp-2, w, dev, p, pno);
	} else {
		snprintf(bufp, bufsiz, "%.*s%s%-2u", w, dev, p, pno);
	}
	return bufp;
}

struct partition {
	unsigned char boot_ind;         /* 0x80 - active */
	unsigned char head;             /* starting head */
	unsigned char sector;           /* starting sector */
	unsigned char cyl;              /* starting cylinder */
	unsigned char sys_ind;          /* What partition type */
	unsigned char end_head;         /* end head */
	unsigned char end_sector;       /* end sector */
	unsigned char end_cyl;          /* end cylinder */
	unsigned char start4[4];        /* starting sector counting from 0 */
	unsigned char size4[4];         /* nr of sectors in partition */
} __attribute__((__packed__));

enum failure {
	ioctl_error, unable_to_open, unable_to_read, unable_to_seek,
	unable_to_write
};

enum action {fdisk, require, try_only, create_empty_dos, create_empty_sun};

static const char *disk_device;
static int fd;                  /* the disk */
static int partitions = 4;      /* maximum partition + 1 */
static uint display_in_cyl_units = 1;
static uint units_per_sector = 1;
#ifdef CONFIG_FEATURE_FDISK_WRITABLE
static char *line_ptr;
static void change_units(void);
static void reread_partition_table(int leave);
static void delete_partition(int i);
static int  get_partition(int warn, int max);
static void list_types(const struct systypes *sys);
static uint read_int(uint low, uint dflt, uint high, uint base, char *mesg);
#endif
static const char *partition_type(unsigned char type);
static void fdisk_fatal(enum failure why) __attribute__ ((noreturn));
static void get_geometry(void);
static int get_boot(enum action what);

#define PLURAL   0
#define SINGULAR 1

#define hex_val(c)      ({ \
				char _c = (c); \
				isdigit(_c) ? _c - '0' : \
				tolower(_c) + 10 - 'a'; \
			})


#define LINE_LENGTH     800
#define pt_offset(b, n) ((struct partition *)((b) + 0x1be + \
				(n) * sizeof(struct partition)))
#define sector(s)       ((s) & 0x3f)
#define cylinder(s, c)  ((c) | (((s) & 0xc0) << 2))

#define hsc2sector(h,s,c) (sector(s) - 1 + sectors * \
				((h) + heads * cylinder(s,c)))
#define set_hsc(h,s,c,sector) { \
				s = sector % sectors + 1;       \
				sector /= sectors;      \
				h = sector % heads;     \
				sector /= heads;        \
				c = sector & 0xff;      \
				s |= (sector >> 2) & 0xc0;      \
			}


static unsigned int get_start_sect(const struct partition *p);
static unsigned int get_nr_sects(const struct partition *p);

/*
 * per partition table entry data
 *
 * The four primary partitions have the same sectorbuffer (MBRbuffer)
 * and have NULL ext_pointer.
 * Each logical partition table entry has two pointers, one for the
 * partition and one link to the next one.
 */
static struct pte {
	struct partition *part_table;   /* points into sectorbuffer */
	struct partition *ext_pointer;  /* points into sectorbuffer */
#ifdef CONFIG_FEATURE_FDISK_WRITABLE
	char changed;           /* boolean */
#endif
	uint offset;            /* disk sector number */
	char *sectorbuffer;     /* disk sector contents */
} ptes[MAXIMUM_PARTS];


#ifdef CONFIG_FEATURE_FDISK_WRITABLE
static void
set_all_unchanged(void) {
	int i;

	for (i = 0; i < MAXIMUM_PARTS; i++)
		ptes[i].changed = 0;
}

static void
set_changed(int i) {
	ptes[i].changed = 1;
}
#endif /* CONFIG_FEATURE_FDISK_WRITABLE */

#if defined(CONFIG_FEATURE_SGI_LABEL) || defined(CONFIG_FEATURE_OSF_LABEL)
static struct partition *
get_part_table(int i) {
	return ptes[i].part_table;
}
#endif

static const char *
str_units(int n) {      /* n==1: use singular */
	if (n == 1)
		return display_in_cyl_units ? _("cylinder") : _("sector");
	else
		return display_in_cyl_units ? _("cylinders") : _("sectors");
}

static int
valid_part_table_flag(const unsigned char *b) {
	return (b[510] == 0x55 && b[511] == 0xaa);
}

#ifdef CONFIG_FEATURE_FDISK_WRITABLE
static char  line_buffer[LINE_LENGTH];

/* read line; return 0 or first char */
static int
read_line(void)
{
	static int got_eof = 0;

	fflush (stdout);         /* requested by niles@scyld.com */
	line_ptr = line_buffer;
	if (!fgets(line_buffer, LINE_LENGTH, stdin)) {
		if (feof(stdin))
			got_eof++;      /* user typed ^D ? */
		if (got_eof >= 3) {
			fprintf(stderr, _("\ngot EOF thrice - exiting..\n"));
			exit(1);
		}
		return 0;
	}
	while (*line_ptr && !isgraph(*line_ptr))
		line_ptr++;
	return *line_ptr;
}

static char
read_char(const char *mesg)
{
	do {
		fputs(mesg, stdout);
	} while (!read_line());
	return *line_ptr;
}

static char
read_chars(const char *mesg)
{
	fputs(mesg, stdout);
	if (!read_line()) {
		*line_ptr = '\n';
		line_ptr[1] = 0;
	}
	return *line_ptr;
}

static int
read_hex(const struct systypes *sys)
{
	int hex;

	while (1)
	{
	   read_char(_("Hex code (type L to list codes): "));
	   if (*line_ptr == 'l' || *line_ptr == 'L')
	       list_types(sys);
	   else if (isxdigit (*line_ptr))
	   {
	      hex = 0;
	      do
		 hex = hex << 4 | hex_val(*line_ptr++);
	      while (isxdigit(*line_ptr));
	      return hex;
	   }
	}
}
#endif /* CONFIG_FEATURE_FDISK_WRITABLE */

#ifdef CONFIG_FEATURE_AIX_LABEL
/*
 * Copyright (C) Andreas Neuper, Sep 1998.
 *      This file may be redistributed under
 *      the terms of the GNU Public License.
 */

typedef struct {
	unsigned int   magic;        /* expect AIX_LABEL_MAGIC */
	unsigned int   fillbytes1[124];
	unsigned int   physical_volume_id;
	unsigned int   fillbytes2[124];
} aix_partition;

#define AIX_LABEL_MAGIC         0xc9c2d4c1
#define AIX_LABEL_MAGIC_SWAPPED 0xc1d4c2c9
#define AIX_INFO_MAGIC          0x00072959
#define AIX_INFO_MAGIC_SWAPPED  0x59290700

#define aixlabel ((aix_partition *)MBRbuffer)


/*
  Changes:
  * 1999-03-20 Arnaldo Carvalho de Melo <acme@conectiva.com.br>
  *     Internationalization
  *
  * 2003-03-20 Phillip Kesling <pkesling@sgi.com>
  *      Some fixes
*/

static  int     aix_other_endian;
static  short   aix_volumes=1;

/*
 * only dealing with free blocks here
 */

static void
aix_info( void ) {
    puts(
	_("\n\tThere is a valid AIX label on this disk.\n"
	"\tUnfortunately Linux cannot handle these\n"
	"\tdisks at the moment.  Nevertheless some\n"
	"\tadvice:\n"
	"\t1. fdisk will destroy its contents on write.\n"
	"\t2. Be sure that this disk is NOT a still vital\n"
	"\t   part of a volume group. (Otherwise you may\n"
	"\t   erase the other disks as well, if unmirrored.)\n"
	"\t3. Before deleting this physical volume be sure\n"
	"\t   to remove the disk logically from your AIX\n"
	"\t   machine.  (Otherwise you become an AIXpert).")
    );
}

static void
aix_nolabel( void )
{
    aixlabel->magic = 0;
    aix_label = 0;
    partitions = 4;
    memset( MBRbuffer, 0, sizeof(MBRbuffer) );  /* avoid fdisk cores */
    return;
}

static int
check_aix_label( void )
{
    if (aixlabel->magic != AIX_LABEL_MAGIC &&
	aixlabel->magic != AIX_LABEL_MAGIC_SWAPPED) {
	aix_label = 0;
	aix_other_endian = 0;
	return 0;
    }
    aix_other_endian = (aixlabel->magic == AIX_LABEL_MAGIC_SWAPPED);
    update_units();
    aix_label = 1;
    partitions= 1016;
    aix_volumes = 15;
    aix_info();
    aix_nolabel();              /* %% */
    aix_label = 1;              /* %% */
    return 1;
}
#endif  /* AIX_LABEL */

#ifdef CONFIG_FEATURE_OSF_LABEL
/*
 * Copyright (c) 1987, 1988 Regents of the University of California.
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
 * 3. All advertising materials mentioning features or use of this software
 *    must display the following acknowledgement:
 *      This product includes software developed by the University of
 *      California, Berkeley and its contributors.
 * 4. Neither the name of the University nor the names of its contributors
 *    may be used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 */


#ifndef BSD_DISKMAGIC
#define BSD_DISKMAGIC     ((uint32_t) 0x82564557)
#endif

#ifndef BSD_MAXPARTITIONS
#define BSD_MAXPARTITIONS 16
#endif

#define BSD_LINUX_BOOTDIR "/usr/ucb/mdec"

#if defined (i386) || defined (__sparc__) || defined (__arm__) || defined (__mips__) || defined (__s390__) || defined (__sh__) || defined(__x86_64__)
#define BSD_LABELSECTOR   1
#define BSD_LABELOFFSET   0
#elif defined (__alpha__) || defined (__powerpc__) || defined (__ia64__) || defined (__hppa__)
#define BSD_LABELSECTOR   0
#define BSD_LABELOFFSET   64
#elif defined (__s390__) || defined (__s390x__)
#define BSD_LABELSECTOR   1
#define BSD_LABELOFFSET   0
#else
#error unknown architecture
#endif

#define BSD_BBSIZE        8192          /* size of boot area, with label */
#define BSD_SBSIZE        8192          /* max size of fs superblock */

struct xbsd_disklabel {
	uint32_t   d_magic;                /* the magic number */
	int16_t   d_type;                 /* drive type */
	int16_t   d_subtype;              /* controller/d_type specific */
	char    d_typename[16];         /* type name, e.g. "eagle" */
	char    d_packname[16];                 /* pack identifier */
			/* disk geometry: */
	uint32_t   d_secsize;              /* # of bytes per sector */
	uint32_t   d_nsectors;             /* # of data sectors per track */
	uint32_t   d_ntracks;              /* # of tracks per cylinder */
	uint32_t   d_ncylinders;           /* # of data cylinders per unit */
	uint32_t   d_secpercyl;            /* # of data sectors per cylinder */
	uint32_t   d_secperunit;           /* # of data sectors per unit */
	/*
	 * Spares (bad sector replacements) below
	 * are not counted in d_nsectors or d_secpercyl.
	 * Spare sectors are assumed to be physical sectors
	 * which occupy space at the end of each track and/or cylinder.
	 */
	uint16_t   d_sparespertrack;       /* # of spare sectors per track */
	uint16_t   d_sparespercyl;         /* # of spare sectors per cylinder */
	/*
	 * Alternate cylinders include maintenance, replacement,
	 * configuration description areas, etc.
	 */
	uint32_t   d_acylinders;           /* # of alt. cylinders per unit */

			/* hardware characteristics: */
	/*
	 * d_interleave, d_trackskew and d_cylskew describe perturbations
	 * in the media format used to compensate for a slow controller.
	 * Interleave is physical sector interleave, set up by the formatter
	 * or controller when formatting.  When interleaving is in use,
	 * logically adjacent sectors are not physically contiguous,
	 * but instead are separated by some number of sectors.
	 * It is specified as the ratio of physical sectors traversed
	 * per logical sector.  Thus an interleave of 1:1 implies contiguous
	 * layout, while 2:1 implies that logical sector 0 is separated
	 * by one sector from logical sector 1.
	 * d_trackskew is the offset of sector 0 on track N
	 * relative to sector 0 on track N-1 on the same cylinder.
	 * Finally, d_cylskew is the offset of sector 0 on cylinder N
	 * relative to sector 0 on cylinder N-1.
	 */
	uint16_t   d_rpm;                  /* rotational speed */
	uint16_t   d_interleave;           /* hardware sector interleave */
	uint16_t   d_trackskew;            /* sector 0 skew, per track */
	uint16_t   d_cylskew;              /* sector 0 skew, per cylinder */
	uint32_t   d_headswitch;           /* head switch time, usec */
	uint32_t   d_trkseek;              /* track-to-track seek, usec */
	uint32_t   d_flags;                /* generic flags */
#define NDDATA 5
	uint32_t   d_drivedata[NDDATA];    /* drive-type specific information */
#define NSPARE 5
	uint32_t   d_spare[NSPARE];        /* reserved for future use */
	uint32_t   d_magic2;               /* the magic number (again) */
	uint16_t   d_checksum;             /* xor of data incl. partitions */
			/* filesystem and partition information: */
	uint16_t   d_npartitions;          /* number of partitions in following */
	uint32_t   d_bbsize;               /* size of boot area at sn0, bytes */
	uint32_t   d_sbsize;               /* max size of fs superblock, bytes */
	struct xbsd_partition    {      /* the partition table */
		uint32_t   p_size;         /* number of sectors in partition */
		uint32_t   p_offset;       /* starting sector */
		uint32_t   p_fsize;        /* filesystem basic fragment size */
		uint8_t    p_fstype;       /* filesystem type, see below */
		uint8_t    p_frag;         /* filesystem fragments per block */
		uint16_t   p_cpg;          /* filesystem cylinders per group */
	} d_partitions[BSD_MAXPARTITIONS]; /* actually may be more */
};

/* d_type values: */
#define BSD_DTYPE_SMD           1               /* SMD, XSMD; VAX hp/up */
#define BSD_DTYPE_MSCP          2               /* MSCP */
#define BSD_DTYPE_DEC           3               /* other DEC (rk, rl) */
#define BSD_DTYPE_SCSI          4               /* SCSI */
#define BSD_DTYPE_ESDI          5               /* ESDI interface */
#define BSD_DTYPE_ST506         6               /* ST506 etc. */
#define BSD_DTYPE_HPIB          7               /* CS/80 on HP-IB */
#define BSD_DTYPE_HPFL          8               /* HP Fiber-link */
#define BSD_DTYPE_FLOPPY        10              /* floppy */

/* d_subtype values: */
#define BSD_DSTYPE_INDOSPART    0x8             /* is inside dos partition */
#define BSD_DSTYPE_DOSPART(s)   ((s) & 3)       /* dos partition number */
#define BSD_DSTYPE_GEOMETRY     0x10            /* drive params in label */

#ifdef DKTYPENAMES
static const char * const xbsd_dktypenames[] = {
	"unknown",
	"SMD",
	"MSCP",
	"old DEC",
	"SCSI",
	"ESDI",
	"ST506",
	"HP-IB",
	"HP-FL",
	"type 9",
	"floppy",
	0
};
#define BSD_DKMAXTYPES  (sizeof(xbsd_dktypenames) / sizeof(xbsd_dktypenames[0]) - 1)
#endif

/*
 * Filesystem type and version.
 * Used to interpret other filesystem-specific
 * per-partition information.
 */
#define BSD_FS_UNUSED   0               /* unused */
#define BSD_FS_SWAP     1               /* swap */
#define BSD_FS_V6       2               /* Sixth Edition */
#define BSD_FS_V7       3               /* Seventh Edition */
#define BSD_FS_SYSV     4               /* System V */
#define BSD_FS_V71K     5               /* V7 with 1K blocks (4.1, 2.9) */
#define BSD_FS_V8       6               /* Eighth Edition, 4K blocks */
#define BSD_FS_BSDFFS   7               /* 4.2BSD fast file system */
#define BSD_FS_BSDLFS   9               /* 4.4BSD log-structured file system */
#define BSD_FS_OTHER    10              /* in use, but unknown/unsupported */
#define BSD_FS_HPFS     11              /* OS/2 high-performance file system */
#define BSD_FS_ISO9660  12              /* ISO-9660 filesystem (cdrom) */
#define BSD_FS_ISOFS    BSD_FS_ISO9660
#define BSD_FS_BOOT     13              /* partition contains bootstrap */
#define BSD_FS_ADOS     14              /* AmigaDOS fast file system */
#define BSD_FS_HFS      15              /* Macintosh HFS */
#define BSD_FS_ADVFS    16              /* Digital Unix AdvFS */

/* this is annoying, but it's also the way it is :-( */
#ifdef __alpha__
#define BSD_FS_EXT2     8               /* ext2 file system */
#else
#define BSD_FS_MSDOS    8               /* MS-DOS file system */
#endif

#ifdef  DKTYPENAMES
static const struct systypes xbsd_fstypes[] = {
/* BSD_FS_UNUSED  */   {"\x00" "unused"},
/* BSD_FS_SWAP    */   {"\x01" "swap"},
/* BSD_FS_V6      */   {"\x02" "Version 6"},
/* BSD_FS_V7      */   {"\x03" "Version 7"},
/* BSD_FS_SYSV    */   {"\x04" "System V"},
/* BSD_FS_V71K    */   {"\x05" "4.1BSD"},
/* BSD_FS_V8      */   {"\x06" "Eighth Edition"},
/* BSD_FS_BSDFFS  */   {"\x07" "4.2BSD"},
#ifdef __alpha__
/* BSD_FS_EXT2    */   {"\x08" "ext2"},
#else
/* BSD_FS_MSDOS   */   {"\x08" "MS-DOS"},
#endif
/* BSD_FS_BSDLFS  */   {"\x09" "4.4LFS"},
/* BSD_FS_OTHER   */   {"\x0a" "unknown"},
/* BSD_FS_HPFS    */   {"\x0b" "HPFS"},
/* BSD_FS_ISO9660 */   {"\x0c" "ISO-9660"},
/* BSD_FS_BOOT    */   {"\x0d" "boot"},
/* BSD_FS_ADOS    */   {"\x0e" "ADOS"},
/* BSD_FS_HFS     */   {"\x0f" "HFS"},
/* BSD_FS_ADVFS   */   {"\x10" "AdvFS"},
		       { NULL }
};
#define BSD_FSMAXTYPES (SIZE(xbsd_fstypes)-1)

#endif

/*
 * flags shared by various drives:
 */
#define BSD_D_REMOVABLE 0x01            /* removable media */
#define BSD_D_ECC       0x02            /* supports ECC */
#define BSD_D_BADSECT   0x04            /* supports bad sector forw. */
#define BSD_D_RAMDISK   0x08            /* disk emulator */
#define BSD_D_CHAIN     0x10            /* can do back-back transfers */
#define BSD_D_DOSPART   0x20            /* within MSDOS partition */

#endif /* OSF_LABEL */

/*
 * Copyright (C) Andreas Neuper, Sep 1998.
 *      This file may be modified and redistributed under
 *      the terms of the GNU Public License.
 */

struct device_parameter { /* 48 bytes */
	unsigned char  skew;
	unsigned char  gap1;
	unsigned char  gap2;
	unsigned char  sparecyl;
	unsigned short pcylcount;
	unsigned short head_vol0;
	unsigned short ntrks;   /* tracks in cyl 0 or vol 0 */
	unsigned char  cmd_tag_queue_depth;
	unsigned char  unused0;
	unsigned short unused1;
	unsigned short nsect;   /* sectors/tracks in cyl 0 or vol 0 */
	unsigned short bytes;
	unsigned short ilfact;
	unsigned int   flags;           /* controller flags */
	unsigned int   datarate;
	unsigned int   retries_on_error;
	unsigned int   ms_per_word;
	unsigned short xylogics_gap1;
	unsigned short xylogics_syncdelay;
	unsigned short xylogics_readdelay;
	unsigned short xylogics_gap2;
	unsigned short xylogics_readgate;
	unsigned short xylogics_writecont;
};

#define SGI_VOLHDR      0x00
/* 1 and 2 were used for drive types no longer supported by SGI */
#define SGI_SWAP        0x03
/* 4 and 5 were for filesystem types SGI haven't ever supported on MIPS CPUs */
#define SGI_VOLUME      0x06
#define SGI_EFS         0x07
#define SGI_LVOL        0x08
#define SGI_RLVOL       0x09
#define SGI_XFS         0x0a
#define SGI_XFSLOG      0x0b
#define SGI_XLV         0x0c
#define SGI_XVM         0x0d
#define ENTIRE_DISK     SGI_VOLUME
/*
 * controller flags
 */
#define SECTOR_SLIP     0x01
#define SECTOR_FWD      0x02
#define TRACK_FWD       0x04
#define TRACK_MULTIVOL  0x08
#define IGNORE_ERRORS   0x10
#define RESEEK          0x20
#define ENABLE_CMDTAGQ  0x40

typedef struct {
	unsigned int   magic;            /* expect SGI_LABEL_MAGIC */
	unsigned short boot_part;        /* active boot partition */
	unsigned short swap_part;        /* active swap partition */
	unsigned char  boot_file[16];    /* name of the bootfile */
	struct device_parameter devparam;       /*  1 * 48 bytes */
	struct volume_directory {               /* 15 * 16 bytes */
		unsigned char vol_file_name[8]; /* a character array */
		unsigned int  vol_file_start;   /* number of logical block */
		unsigned int  vol_file_size;    /* number of bytes */
	} directory[15];
	struct sgi_partition {                  /* 16 * 12 bytes */
		unsigned int num_sectors;       /* number of blocks */
		unsigned int start_sector;      /* must be cylinder aligned */
		unsigned int id;
	} partitions[16];
	unsigned int   csum;
	unsigned int   fillbytes;
} sgi_partition;

typedef struct {
	unsigned int   magic;           /* looks like a magic number */
	unsigned int   a2;
	unsigned int   a3;
	unsigned int   a4;
	unsigned int   b1;
	unsigned short b2;
	unsigned short b3;
	unsigned int   c[16];
	unsigned short d[3];
	unsigned char  scsi_string[50];
	unsigned char  serial[137];
	unsigned short check1816;
	unsigned char  installer[225];
} sgiinfo;

#define SGI_LABEL_MAGIC         0x0be5a941
#define SGI_LABEL_MAGIC_SWAPPED 0x41a9e50b
#define SGI_INFO_MAGIC          0x00072959
#define SGI_INFO_MAGIC_SWAPPED  0x59290700
#define SGI_SSWAP16(x) (sgi_other_endian ? __swap16(x) \
				 : (uint16_t)(x))
#define SGI_SSWAP32(x) (sgi_other_endian ? __swap32(x) \
				 : (uint32_t)(x))

#define sgilabel ((sgi_partition *)MBRbuffer)
#define sgiparam (sgilabel->devparam)

typedef struct {
	unsigned char info[128];   /* Informative text string */
	unsigned char spare0[14];
	struct sun_info {
		unsigned char spare1;
		unsigned char id;
		unsigned char spare2;
		unsigned char flags;
	} infos[8];
	unsigned char spare1[246]; /* Boot information etc. */
	unsigned short rspeed;     /* Disk rotational speed */
	unsigned short pcylcount;  /* Physical cylinder count */
	unsigned short sparecyl;   /* extra sects per cylinder */
	unsigned char spare2[4];   /* More magic... */
	unsigned short ilfact;     /* Interleave factor */
	unsigned short ncyl;       /* Data cylinder count */
	unsigned short nacyl;      /* Alt. cylinder count */
	unsigned short ntrks;      /* Tracks per cylinder */
	unsigned short nsect;      /* Sectors per track */
	unsigned char spare3[4];   /* Even more magic... */
	struct sun_partition {
		uint32_t start_cylinder;
		uint32_t num_sectors;
	} partitions[8];
	unsigned short magic;      /* Magic number */
	unsigned short csum;       /* Label xor'd checksum */
} sun_partition;


#define SUN_LABEL_MAGIC          0xDABE
#define SUN_LABEL_MAGIC_SWAPPED  0xBEDA
#define sunlabel ((sun_partition *)MBRbuffer)
#define SUN_SSWAP16(x) (sun_other_endian ? __swap16(x) \
				 : (uint16_t)(x))
#define SUN_SSWAP32(x) (sun_other_endian ? __swap32(x) \
				 : (uint32_t)(x))


#ifdef CONFIG_FEATURE_OSF_LABEL
/*
   Changes:
   19990319 - Arnaldo Carvalho de Melo <acme@conectiva.com.br> - i18n/nls

   20000101 - David Huggins-Daines <dhuggins@linuxcare.com> - Better
   support for OSF/1 disklabels on Alpha.
   Also fixed unaligned accesses in alpha_bootblock_checksum()
*/

#define FREEBSD_PARTITION       0xa5
#define NETBSD_PARTITION        0xa9

static void xbsd_delete_part (void);
static void xbsd_new_part (void);
static void xbsd_write_disklabel (void);
static int xbsd_create_disklabel (void);
static void xbsd_edit_disklabel (void);
static void xbsd_write_bootstrap (void);
static void xbsd_change_fstype (void);
static int xbsd_get_part_index (int max);
static int xbsd_check_new_partition (int *i);
static void xbsd_list_types (void);
static u_short xbsd_dkcksum (struct xbsd_disklabel *lp);
static int xbsd_initlabel  (struct partition *p, struct xbsd_disklabel *d,
			    int pindex);
static int xbsd_readlabel  (struct partition *p, struct xbsd_disklabel *d);
static int xbsd_writelabel (struct partition *p, struct xbsd_disklabel *d);

#if defined (__alpha__)
static void alpha_bootblock_checksum (char *boot);
#endif

#if !defined (__alpha__)
static int xbsd_translate_fstype (int linux_type);
static void xbsd_link_part (void);
static struct partition *xbsd_part;
static int xbsd_part_index;
#endif

#if defined (__alpha__)
/* We access this through a uint64_t * when checksumming */
static char disklabelbuffer[BSD_BBSIZE] __attribute__((aligned(8)));
#else
static char disklabelbuffer[BSD_BBSIZE];
#endif

static struct xbsd_disklabel xbsd_dlabel;

#define bsd_cround(n) \
	(display_in_cyl_units ? ((n)/xbsd_dlabel.d_secpercyl) + 1 : (n))

/*
 * Test whether the whole disk has BSD disk label magic.
 *
 * Note: often reformatting with DOS-type label leaves the BSD magic,
 * so this does not mean that there is a BSD disk label.
 */
static int
check_osf_label(void) {
	if (xbsd_readlabel (NULL, &xbsd_dlabel) == 0)
		return 0;
	return 1;
}

static void xbsd_print_disklabel(int);

static int
btrydev (const char * dev) {
	if (xbsd_readlabel (NULL, &xbsd_dlabel) == 0)
		return -1;
	printf(_("\nBSD label for device: %s\n"), dev);
	xbsd_print_disklabel (0);
	return 0;
}

static void
bmenu (void) {
  puts (_("Command action"));
  puts (_("\td\tdelete a BSD partition"));
  puts (_("\te\tedit drive data"));
  puts (_("\ti\tinstall bootstrap"));
  puts (_("\tl\tlist known filesystem types"));
  puts (_("\tm\tprint this menu"));
  puts (_("\tn\tadd a new BSD partition"));
  puts (_("\tp\tprint BSD partition table"));
  puts (_("\tq\tquit without saving changes"));
  puts (_("\tr\treturn to main menu"));
  puts (_("\ts\tshow complete disklabel"));
  puts (_("\tt\tchange a partition's filesystem id"));
  puts (_("\tu\tchange units (cylinders/sectors)"));
  puts (_("\tw\twrite disklabel to disk"));
#if !defined (__alpha__)
  puts (_("\tx\tlink BSD partition to non-BSD partition"));
#endif
}

#if !defined (__alpha__)
static int
hidden(int type) {
	return type ^ 0x10;
}

static int
is_bsd_partition_type(int type) {
	return (type == FREEBSD_PARTITION ||
		type == hidden(FREEBSD_PARTITION) ||
		type == NETBSD_PARTITION ||
		type == hidden(NETBSD_PARTITION));
}
#endif

static void
bselect (void) {
#if !defined (__alpha__)
  int t, ss;
  struct partition *p;

  for (t=0; t<4; t++) {
    p = get_part_table(t);
    if (p && is_bsd_partition_type(p->sys_ind)) {
      xbsd_part = p;
      xbsd_part_index = t;
      ss = get_start_sect(xbsd_part);
      if (ss == 0) {
	fprintf (stderr, _("Partition %s has invalid starting sector 0.\n"),
		 partname(disk_device, t+1, 0));
	return;
      }
      printf (_("Reading disklabel of %s at sector %d.\n"),
	      partname(disk_device, t+1, 0), ss + BSD_LABELSECTOR);
      if (xbsd_readlabel (xbsd_part, &xbsd_dlabel) == 0)
	if (xbsd_create_disklabel () == 0)
	  return;
      break;
    }
  }

  if (t == 4) {
    printf (_("There is no *BSD partition on %s.\n"), disk_device);
    return;
  }

#elif defined (__alpha__)

  if (xbsd_readlabel (NULL, &xbsd_dlabel) == 0)
    if (xbsd_create_disklabel () == 0)
      exit ( EXIT_SUCCESS );

#endif

  while (1) {
    putchar ('\n');
    switch (tolower (read_char (_("BSD disklabel command (m for help): ")))) {
      case 'd':
	xbsd_delete_part ();
	break;
      case 'e':
	xbsd_edit_disklabel ();
	break;
      case 'i':
	xbsd_write_bootstrap ();
	break;
      case 'l':
	xbsd_list_types ();
	break;
      case 'n':
	xbsd_new_part ();
	break;
      case 'p':
	xbsd_print_disklabel (0);
	break;
      case 'q':
	close (fd);
	exit ( EXIT_SUCCESS );
      case 'r':
	return;
      case 's':
	xbsd_print_disklabel (1);
	break;
      case 't':
	xbsd_change_fstype ();
	break;
      case 'u':
	change_units();
	break;
      case 'w':
	xbsd_write_disklabel ();
	break;
#if !defined (__alpha__)
      case 'x':
	xbsd_link_part ();
	break;
#endif
      default:
	bmenu ();
	break;
    }
  }
}

static void
xbsd_delete_part (void)
{
  int i;

  i = xbsd_get_part_index (xbsd_dlabel.d_npartitions);
  xbsd_dlabel.d_partitions[i].p_size   = 0;
  xbsd_dlabel.d_partitions[i].p_offset = 0;
  xbsd_dlabel.d_partitions[i].p_fstype = BSD_FS_UNUSED;
  if (xbsd_dlabel.d_npartitions == i + 1)
    while (xbsd_dlabel.d_partitions[xbsd_dlabel.d_npartitions-1].p_size == 0)
      xbsd_dlabel.d_npartitions--;
}

static void
xbsd_new_part (void)
{
  uint begin, end;
  char mesg[256];
  int i;

  if (!xbsd_check_new_partition (&i))
    return;

#if !defined (__alpha__) && !defined (__powerpc__) && !defined (__hppa__)
  begin = get_start_sect(xbsd_part);
  end = begin + get_nr_sects(xbsd_part) - 1;
#else
  begin = 0;
  end = xbsd_dlabel.d_secperunit - 1;
#endif

  snprintf (mesg, sizeof(mesg), _("First %s"), str_units(SINGULAR));
  begin = read_int (bsd_cround (begin), bsd_cround (begin), bsd_cround (end),
		    0, mesg);

  if (display_in_cyl_units)
    begin = (begin - 1) * xbsd_dlabel.d_secpercyl;

  snprintf (mesg, sizeof(mesg), _("Last %s or +size or +sizeM or +sizeK"),
	   str_units(SINGULAR));
  end = read_int (bsd_cround (begin), bsd_cround (end), bsd_cround (end),
		  bsd_cround (begin), mesg);

  if (display_in_cyl_units)
    end = end * xbsd_dlabel.d_secpercyl - 1;

  xbsd_dlabel.d_partitions[i].p_size   = end - begin + 1;
  xbsd_dlabel.d_partitions[i].p_offset = begin;
  xbsd_dlabel.d_partitions[i].p_fstype = BSD_FS_UNUSED;
}

static void
xbsd_print_disklabel (int show_all) {
  struct xbsd_disklabel *lp = &xbsd_dlabel;
  struct xbsd_partition *pp;
  int i, j;

  if (show_all) {
#if defined (__alpha__)
    printf("# %s:\n", disk_device);
#else
    printf("# %s:\n", partname(disk_device, xbsd_part_index+1, 0));
#endif
    if ((unsigned) lp->d_type < BSD_DKMAXTYPES)
      printf(_("type: %s\n"), xbsd_dktypenames[lp->d_type]);
    else
      printf(_("type: %d\n"), lp->d_type);
    printf(_("disk: %.*s\n"), (int) sizeof(lp->d_typename), lp->d_typename);
    printf(_("label: %.*s\n"), (int) sizeof(lp->d_packname), lp->d_packname);
    printf(_("flags:"));
    if (lp->d_flags & BSD_D_REMOVABLE)
      printf(_(" removable"));
    if (lp->d_flags & BSD_D_ECC)
      printf(_(" ecc"));
    if (lp->d_flags & BSD_D_BADSECT)
      printf(_(" badsect"));
    printf("\n");
    /* On various machines the fields of *lp are short/int/long */
    /* In order to avoid problems, we cast them all to long. */
    printf(_("bytes/sector: %ld\n"), (long) lp->d_secsize);
    printf(_("sectors/track: %ld\n"), (long) lp->d_nsectors);
    printf(_("tracks/cylinder: %ld\n"), (long) lp->d_ntracks);
    printf(_("sectors/cylinder: %ld\n"), (long) lp->d_secpercyl);
    printf(_("cylinders: %ld\n"), (long) lp->d_ncylinders);
    printf(_("rpm: %d\n"), lp->d_rpm);
    printf(_("interleave: %d\n"), lp->d_interleave);
    printf(_("trackskew: %d\n"), lp->d_trackskew);
    printf(_("cylinderskew: %d\n"), lp->d_cylskew);
    printf(_("headswitch: %ld\t\t# milliseconds\n"),
	    (long) lp->d_headswitch);
    printf(_("track-to-track seek: %ld\t# milliseconds\n"),
	    (long) lp->d_trkseek);
    printf(_("drivedata: "));
    for (i = NDDATA - 1; i >= 0; i--)
      if (lp->d_drivedata[i])
	break;
    if (i < 0)
      i = 0;
    for (j = 0; j <= i; j++)
      printf("%ld ", (long) lp->d_drivedata[j]);
  }
  printf(_("\n%d partitions:\n"), lp->d_npartitions);
  printf(_("#       start       end      size     fstype   [fsize bsize   cpg]\n"));
  pp = lp->d_partitions;
  for (i = 0; i < lp->d_npartitions; i++, pp++) {
    if (pp->p_size) {
      if (display_in_cyl_units && lp->d_secpercyl) {
	printf("  %c: %8ld%c %8ld%c %8ld%c  ",
		'a' + i,
		(long) pp->p_offset / lp->d_secpercyl + 1,
		(pp->p_offset % lp->d_secpercyl) ? '*' : ' ',
		(long) (pp->p_offset + pp->p_size + lp->d_secpercyl - 1)
			/ lp->d_secpercyl,
		((pp->p_offset + pp->p_size) % lp->d_secpercyl) ? '*' : ' ',
		(long) pp->p_size / lp->d_secpercyl,
		(pp->p_size % lp->d_secpercyl) ? '*' : ' ');
      } else {
	printf("  %c: %8ld  %8ld  %8ld   ",
		'a' + i,
		(long) pp->p_offset,
		(long) pp->p_offset + pp->p_size - 1,
		(long) pp->p_size);
      }
      if ((unsigned) pp->p_fstype < BSD_FSMAXTYPES)
	printf("%8.8s", xbsd_fstypes[pp->p_fstype].name);
      else
	printf("%8x", pp->p_fstype);
      switch (pp->p_fstype) {
	case BSD_FS_UNUSED:
	  printf("    %5ld %5ld %5.5s ",
		  (long) pp->p_fsize, (long) pp->p_fsize * pp->p_frag, "");
	  break;

	case BSD_FS_BSDFFS:
	  printf("    %5ld %5ld %5d ",
		  (long) pp->p_fsize, (long) pp->p_fsize * pp->p_frag,
		  pp->p_cpg);
	  break;

	default:
	  printf("%22.22s", "");
	  break;
      }
      printf("\n");
    }
  }
}

static void
xbsd_write_disklabel (void) {
#if defined (__alpha__)
	printf (_("Writing disklabel to %s.\n"), disk_device);
	xbsd_writelabel (NULL, &xbsd_dlabel);
#else
	printf (_("Writing disklabel to %s.\n"),
		partname(disk_device, xbsd_part_index+1, 0));
	xbsd_writelabel (xbsd_part, &xbsd_dlabel);
#endif
	reread_partition_table(0);      /* no exit yet */
}

static int
xbsd_create_disklabel (void) {
	char c;

#if defined (__alpha__)
	fprintf (stderr, _("%s contains no disklabel.\n"), disk_device);
#else
	fprintf (stderr, _("%s contains no disklabel.\n"),
		 partname(disk_device, xbsd_part_index+1, 0));
#endif

	while (1) {
		c = read_char (_("Do you want to create a disklabel? (y/n) "));
		if (c == 'y' || c == 'Y') {
			if (xbsd_initlabel (
#if defined (__alpha__) || defined (__powerpc__) || defined (__hppa__) || \
    defined (__s390__) || defined (__s390x__)
				NULL, &xbsd_dlabel, 0
#else
				xbsd_part, &xbsd_dlabel, xbsd_part_index
#endif
				) == 1) {
				xbsd_print_disklabel (1);
				return 1;
			} else
				return 0;
		} else if (c == 'n')
			return 0;
	}
}

static int
edit_int (int def, char *mesg)
{
  do {
    fputs (mesg, stdout);
    printf (" (%d): ", def);
    if (!read_line ())
      return def;
  }
  while (!isdigit (*line_ptr));
  return atoi (line_ptr);
}

static void
xbsd_edit_disklabel (void)
{
  struct xbsd_disklabel *d;

  d = &xbsd_dlabel;

#if defined (__alpha__) || defined (__ia64__)
  d -> d_secsize    = (u_long) edit_int ((u_long) d -> d_secsize     ,_("bytes/sector"));
  d -> d_nsectors   = (u_long) edit_int ((u_long) d -> d_nsectors    ,_("sectors/track"));
  d -> d_ntracks    = (u_long) edit_int ((u_long) d -> d_ntracks     ,_("tracks/cylinder"));
  d -> d_ncylinders = (u_long) edit_int ((u_long) d -> d_ncylinders  ,_("cylinders"));
#endif

  /* d -> d_secpercyl can be != d -> d_nsectors * d -> d_ntracks */
  while (1)
  {
    d -> d_secpercyl = (u_long) edit_int ((u_long) d -> d_nsectors * d -> d_ntracks,
					  _("sectors/cylinder"));
    if (d -> d_secpercyl <= d -> d_nsectors * d -> d_ntracks)
      break;

    printf (_("Must be <= sectors/track * tracks/cylinder (default).\n"));
  }
  d -> d_rpm        = (u_short) edit_int ((u_short) d -> d_rpm       ,_("rpm"));
  d -> d_interleave = (u_short) edit_int ((u_short) d -> d_interleave,_("interleave"));
  d -> d_trackskew  = (u_short) edit_int ((u_short) d -> d_trackskew ,_("trackskew"));
  d -> d_cylskew    = (u_short) edit_int ((u_short) d -> d_cylskew   ,_("cylinderskew"));
  d -> d_headswitch = (u_long) edit_int ((u_long) d -> d_headswitch  ,_("headswitch"));
  d -> d_trkseek    = (u_long) edit_int ((u_long) d -> d_trkseek     ,_("track-to-track seek"));

  d -> d_secperunit = d -> d_secpercyl * d -> d_ncylinders;
}

static int
xbsd_get_bootstrap (char *path, void *ptr, int size)
{
  int fdb;

  if ((fdb = open (path, O_RDONLY)) < 0)
  {
    perror (path);
    return 0;
  }
  if (read (fdb, ptr, size) < 0)
  {
    perror (path);
    close (fdb);
    return 0;
  }
  printf (" ... %s\n", path);
  close (fdb);
  return 1;
}

static void
sync_disks (void)
{
  printf (_("\nSyncing disks.\n"));
  sync ();
  sleep (4);
}

static void
xbsd_write_bootstrap (void)
{
  char *bootdir = BSD_LINUX_BOOTDIR;
  char path[MAXPATHLEN];
  char *dkbasename;
  struct xbsd_disklabel dl;
  char *d, *p, *e;
  int sector;

  if (xbsd_dlabel.d_type == BSD_DTYPE_SCSI)
    dkbasename = "sd";
  else
    dkbasename = "wd";

  printf (_("Bootstrap: %sboot -> boot%s (%s): "),
	  dkbasename, dkbasename, dkbasename);
  if (read_line ()) {
    line_ptr[strlen (line_ptr)-1] = '\0';
    dkbasename = line_ptr;
  }
  snprintf (path, sizeof(path), "%s/%sboot", bootdir, dkbasename);
  if (!xbsd_get_bootstrap (path, disklabelbuffer, (int) xbsd_dlabel.d_secsize))
    return;

  /* We need a backup of the disklabel (xbsd_dlabel might have changed). */
  d = &disklabelbuffer[BSD_LABELSECTOR * SECTOR_SIZE];
  bcopy (d, &dl, sizeof (struct xbsd_disklabel));

  /* The disklabel will be overwritten by 0's from bootxx anyway */
  bzero (d, sizeof (struct xbsd_disklabel));

  snprintf (path, sizeof(path), "%s/boot%s", bootdir, dkbasename);
  if (!xbsd_get_bootstrap (path, &disklabelbuffer[xbsd_dlabel.d_secsize],
			  (int) xbsd_dlabel.d_bbsize - xbsd_dlabel.d_secsize))
    return;

  e = d + sizeof (struct xbsd_disklabel);
  for (p=d; p < e; p++)
    if (*p) {
      fprintf (stderr, _("Bootstrap overlaps with disk label!\n"));
      exit ( EXIT_FAILURE );
    }

  bcopy (&dl, d, sizeof (struct xbsd_disklabel));

#if defined (__powerpc__) || defined (__hppa__)
  sector = 0;
#elif defined (__alpha__)
  sector = 0;
  alpha_bootblock_checksum (disklabelbuffer);
#else
  sector = get_start_sect(xbsd_part);
#endif

  if (lseek (fd, sector * SECTOR_SIZE, SEEK_SET) == -1)
    fdisk_fatal (unable_to_seek);
  if (BSD_BBSIZE != write (fd, disklabelbuffer, BSD_BBSIZE))
    fdisk_fatal (unable_to_write);

#if defined (__alpha__)
  printf (_("Bootstrap installed on %s.\n"), disk_device);
#else
  printf (_("Bootstrap installed on %s.\n"),
    partname (disk_device, xbsd_part_index+1, 0));
#endif

  sync_disks ();
}

static void
xbsd_change_fstype (void)
{
  int i;

  i = xbsd_get_part_index (xbsd_dlabel.d_npartitions);
  xbsd_dlabel.d_partitions[i].p_fstype = read_hex (xbsd_fstypes);
}

static int
xbsd_get_part_index (int max)
{
  char prompt[256];
  char l;

  snprintf (prompt, sizeof(prompt), _("Partition (a-%c): "), 'a' + max - 1);
  do
     l = tolower (read_char (prompt));
  while (l < 'a' || l > 'a' + max - 1);
  return l - 'a';
}

static int
xbsd_check_new_partition (int *i) {

	/* room for more? various BSD flavours have different maxima */
	if (xbsd_dlabel.d_npartitions == BSD_MAXPARTITIONS) {
		int t;

		for (t = 0; t < BSD_MAXPARTITIONS; t++)
			if (xbsd_dlabel.d_partitions[t].p_size == 0)
				break;

		if (t == BSD_MAXPARTITIONS) {
			fprintf (stderr, _("The maximum number of partitions "
					   "has been created\n"));
			return 0;
		}
	}

	*i = xbsd_get_part_index (BSD_MAXPARTITIONS);

	if (*i >= xbsd_dlabel.d_npartitions)
		xbsd_dlabel.d_npartitions = (*i) + 1;

	if (xbsd_dlabel.d_partitions[*i].p_size != 0) {
		fprintf (stderr, _("This partition already exists.\n"));
		return 0;
	}

	return 1;
}

static void
xbsd_list_types (void) {
	list_types (xbsd_fstypes);
}

static u_short
xbsd_dkcksum (struct xbsd_disklabel *lp) {
	u_short *start, *end;
	u_short sum = 0;

	start = (u_short *) lp;
	end = (u_short *) &lp->d_partitions[lp->d_npartitions];
	while (start < end)
		sum ^= *start++;
	return sum;
}

static int
xbsd_initlabel (struct partition *p, struct xbsd_disklabel *d, int pindex) {
	struct xbsd_partition *pp;

	get_geometry ();
	bzero (d, sizeof (struct xbsd_disklabel));

	d -> d_magic = BSD_DISKMAGIC;

	if (strncmp (disk_device, "/dev/sd", 7) == 0)
		d -> d_type = BSD_DTYPE_SCSI;
	else
		d -> d_type = BSD_DTYPE_ST506;

#if 0 /* not used (at least not written to disk) by NetBSD/i386 1.0 */
	d -> d_subtype = BSD_DSTYPE_INDOSPART & pindex;
#endif

#if !defined (__alpha__)
	d -> d_flags = BSD_D_DOSPART;
#else
	d -> d_flags = 0;
#endif
	d -> d_secsize = SECTOR_SIZE;           /* bytes/sector  */
	d -> d_nsectors = sectors;            /* sectors/track */
	d -> d_ntracks = heads;               /* tracks/cylinder (heads) */
	d -> d_ncylinders = cylinders;
	d -> d_secpercyl  = sectors * heads;/* sectors/cylinder */
	if (d -> d_secpercyl == 0)
		d -> d_secpercyl = 1;           /* avoid segfaults */
	d -> d_secperunit = d -> d_secpercyl * d -> d_ncylinders;

	d -> d_rpm = 3600;
	d -> d_interleave = 1;
	d -> d_trackskew = 0;
	d -> d_cylskew = 0;
	d -> d_headswitch = 0;
	d -> d_trkseek = 0;

	d -> d_magic2 = BSD_DISKMAGIC;
	d -> d_bbsize = BSD_BBSIZE;
	d -> d_sbsize = BSD_SBSIZE;

#if !defined (__alpha__)
	d -> d_npartitions = 4;
	pp = &d -> d_partitions[2];             /* Partition C should be
						   the NetBSD partition */
	pp -> p_offset = get_start_sect(p);
	pp -> p_size   = get_nr_sects(p);
	pp -> p_fstype = BSD_FS_UNUSED;
	pp = &d -> d_partitions[3];             /* Partition D should be
						   the whole disk */
	pp -> p_offset = 0;
	pp -> p_size   = d -> d_secperunit;
	pp -> p_fstype = BSD_FS_UNUSED;
#elif defined (__alpha__)
	d -> d_npartitions = 3;
	pp = &d -> d_partitions[2];             /* Partition C should be
						   the whole disk */
	pp -> p_offset = 0;
	pp -> p_size   = d -> d_secperunit;
	pp -> p_fstype = BSD_FS_UNUSED;
#endif

	return 1;
}

/*
 * Read a xbsd_disklabel from sector 0 or from the starting sector of p.
 * If it has the right magic, return 1.
 */
static int
xbsd_readlabel (struct partition *p, struct xbsd_disklabel *d)
{
	int t, sector;

	/* p is used only to get the starting sector */
#if !defined (__alpha__)
	sector = (p ? get_start_sect(p) : 0);
#elif defined (__alpha__)
	sector = 0;
#endif

	if (lseek (fd, sector * SECTOR_SIZE, SEEK_SET) == -1)
		fdisk_fatal (unable_to_seek);
	if (BSD_BBSIZE != read (fd, disklabelbuffer, BSD_BBSIZE))
		fdisk_fatal (unable_to_read);

	bcopy (&disklabelbuffer[BSD_LABELSECTOR * SECTOR_SIZE + BSD_LABELOFFSET],
	       d, sizeof (struct xbsd_disklabel));

	if (d -> d_magic != BSD_DISKMAGIC || d -> d_magic2 != BSD_DISKMAGIC)
		return 0;

	for (t = d -> d_npartitions; t < BSD_MAXPARTITIONS; t++) {
		d -> d_partitions[t].p_size   = 0;
		d -> d_partitions[t].p_offset = 0;
		d -> d_partitions[t].p_fstype = BSD_FS_UNUSED;
	}

	if (d -> d_npartitions > BSD_MAXPARTITIONS)
		fprintf (stderr, _("Warning: too many partitions "
				   "(%d, maximum is %d).\n"),
			 d -> d_npartitions, BSD_MAXPARTITIONS);
	return 1;
}

static int
xbsd_writelabel (struct partition *p, struct xbsd_disklabel *d)
{
  unsigned int sector;

#if !defined (__alpha__) && !defined (__powerpc__) && !defined (__hppa__)
  sector = get_start_sect(p) + BSD_LABELSECTOR;
#else
  sector = BSD_LABELSECTOR;
#endif

  d -> d_checksum = 0;
  d -> d_checksum = xbsd_dkcksum (d);

  /* This is necessary if we want to write the bootstrap later,
     otherwise we'd write the old disklabel with the bootstrap.
  */
  bcopy (d, &disklabelbuffer[BSD_LABELSECTOR * SECTOR_SIZE + BSD_LABELOFFSET],
	 sizeof (struct xbsd_disklabel));

#if defined (__alpha__) && BSD_LABELSECTOR == 0
  alpha_bootblock_checksum (disklabelbuffer);
  if (lseek (fd, 0, SEEK_SET) == -1)
    fdisk_fatal (unable_to_seek);
  if (BSD_BBSIZE != write (fd, disklabelbuffer, BSD_BBSIZE))
    fdisk_fatal (unable_to_write);
#else
  if (lseek (fd, sector * SECTOR_SIZE + BSD_LABELOFFSET,
		   SEEK_SET) == -1)
    fdisk_fatal (unable_to_seek);
  if (sizeof (struct xbsd_disklabel) != write (fd, d, sizeof (struct xbsd_disklabel)))
    fdisk_fatal (unable_to_write);
#endif

  sync_disks ();

  return 1;
}


#if !defined (__alpha__)
static int
xbsd_translate_fstype (int linux_type)
{
  switch (linux_type)
  {
    case 0x01: /* DOS 12-bit FAT   */
    case 0x04: /* DOS 16-bit <32M  */
    case 0x06: /* DOS 16-bit >=32M */
    case 0xe1: /* DOS access       */
    case 0xe3: /* DOS R/O          */
    case 0xf2: /* DOS secondary    */
      return BSD_FS_MSDOS;
    case 0x07: /* OS/2 HPFS        */
      return BSD_FS_HPFS;
    default:
      return BSD_FS_OTHER;
  }
}

static void
xbsd_link_part (void)
{
  int k, i;
  struct partition *p;

  k = get_partition (1, partitions);

  if (!xbsd_check_new_partition (&i))
    return;

  p = get_part_table(k);

  xbsd_dlabel.d_partitions[i].p_size   = get_nr_sects(p);
  xbsd_dlabel.d_partitions[i].p_offset = get_start_sect(p);
  xbsd_dlabel.d_partitions[i].p_fstype = xbsd_translate_fstype(p->sys_ind);
}
#endif

#if defined (__alpha__)

#if !defined(__GLIBC__)
typedef unsigned long long uint64_t;
#endif

static void
alpha_bootblock_checksum (char *boot)
{
  uint64_t *dp, sum;
  int i;

  dp = (uint64_t *)boot;
  sum = 0;
  for (i = 0; i < 63; i++)
    sum += dp[i];
  dp[63] = sum;
}
#endif /* __alpha__ */

#endif /* OSF_LABEL */

#if defined(CONFIG_FEATURE_SGI_LABEL) || defined(CONFIG_FEATURE_SUN_LABEL)
static inline unsigned short
__swap16(unsigned short x) {
	return (((uint16_t)(x) & 0xFF) << 8) | (((uint16_t)(x) & 0xFF00) >> 8);
}

static inline uint32_t
__swap32(uint32_t x) {
	 return (((x & 0xFF) << 24) |
		((x & 0xFF00) << 8) |
		((x & 0xFF0000) >> 8) |
		((x & 0xFF000000) >> 24));
}
#endif

#ifdef CONFIG_FEATURE_SGI_LABEL
/*
 *
 * fdisksgilabel.c
 *
 * Copyright (C) Andreas Neuper, Sep 1998.
 *      This file may be modified and redistributed under
 *      the terms of the GNU Public License.
 *
 * Sat Mar 20 EST 1999 Arnaldo Carvalho de Melo <acme@conectiva.com.br>
 *      Internationalization
 */


static  int     sgi_other_endian;
static  int     debug;
static  short   sgi_volumes=1;

/*
 * only dealing with free blocks here
 */

typedef struct { unsigned int first; unsigned int last; } freeblocks;
static freeblocks freelist[17]; /* 16 partitions can produce 17 vacant slots */

static void
setfreelist(int i, unsigned int f, unsigned int l) {
	freelist[i].first = f;
	freelist[i].last = l;
}

static void
add2freelist(unsigned int f, unsigned int l) {
	int i = 0;
	for ( ; i < 17 ; i++)
		if (freelist[i].last == 0)
			break;
	setfreelist(i, f, l);
}

static void
clearfreelist(void) {
	int i;

	for (i = 0; i < 17 ; i++)
		setfreelist(i, 0, 0);
}

static unsigned int
isinfreelist(unsigned int b) {
	int i;

	for (i = 0; i < 17 ; i++)
		if (freelist[i].first <= b && freelist[i].last >= b)
			return freelist[i].last;
	return 0;
}
	/* return last vacant block of this stride (never 0). */
	/* the '>=' is not quite correct, but simplifies the code */
/*
 * end of free blocks section
 */

static const struct systypes sgi_sys_types[] = {
/* SGI_VOLHDR   */  {"\x00" "SGI volhdr"   },
/* 0x01         */  {"\x01" "SGI trkrepl"  },
/* 0x02         */  {"\x02" "SGI secrepl"  },
/* SGI_SWAP     */  {"\x03" "SGI raw"      },
/* 0x04         */  {"\x04" "SGI bsd"      },
/* 0x05         */  {"\x05" "SGI sysv"     },
/* ENTIRE_DISK  */  {"\x06" "SGI volume"   },
/* SGI_EFS      */  {"\x07" "SGI efs"      },
/* 0x08         */  {"\x08" "SGI lvol"     },
/* 0x09         */  {"\x09" "SGI rlvol"    },
/* SGI_XFS      */  {"\x0a" "SGI xfs"      },
/* SGI_XFSLOG   */  {"\x0b" "SGI xfslog"   },
/* SGI_XLV      */  {"\x0c" "SGI xlv"      },
/* SGI_XVM      */  {"\x0d" "SGI xvm"      },
/* LINUX_SWAP   */  {"\x82" "Linux swap"   },
/* LINUX_NATIVE */  {"\x83" "Linux native" },
/* LINUX_LVM    */  {"\x8d" "Linux LVM"    },
/* LINUX_RAID   */  {"\xfd" "Linux RAID"   },
		    { NULL             }
};


static int
sgi_get_nsect(void) {
    return SGI_SSWAP16(sgilabel->devparam.nsect);
}

static int
sgi_get_ntrks(void) {
    return SGI_SSWAP16(sgilabel->devparam.ntrks);
}

static void
sgi_nolabel(void) {
    sgilabel->magic = 0;
    sgi_label = 0;
    partitions = 4;
}

static unsigned int
two_s_complement_32bit_sum(unsigned int* base, int size /* in bytes */) {
    int i=0;
    unsigned int sum=0;

    size /= sizeof(unsigned int);
    for (i = 0; i < size; i++)
	    sum -= SGI_SSWAP32(base[i]);
    return sum;
}

static int
check_sgi_label(void) {
    if (sizeof(sgilabel) > 512) {
	    fprintf(stderr,
		    _("According to MIPS Computer Systems, Inc the "
		    "Label must not contain more than 512 bytes\n"));
	    exit(1);
    }

    if (sgilabel->magic != SGI_LABEL_MAGIC &&
	sgilabel->magic != SGI_LABEL_MAGIC_SWAPPED) {
	sgi_label = 0;
	sgi_other_endian = 0;
	return 0;
    }

    sgi_other_endian = (sgilabel->magic == SGI_LABEL_MAGIC_SWAPPED);
    /*
     * test for correct checksum
     */
    if (two_s_complement_32bit_sum((unsigned int*)sgilabel,
				       sizeof(*sgilabel))) {
		fprintf(stderr,
			_("Detected sgi disklabel with wrong checksum.\n"));
    }
    update_units();
    sgi_label = 1;
    partitions= 16;
    sgi_volumes = 15;
    return 1;
}

static unsigned int
sgi_get_start_sector(int i) {
    return SGI_SSWAP32(sgilabel->partitions[i].start_sector);
}

static unsigned int
sgi_get_num_sectors(int i) {
    return SGI_SSWAP32(sgilabel->partitions[i].num_sectors);
}

static int
sgi_get_sysid(int i)
{
    return SGI_SSWAP32(sgilabel->partitions[i].id);
}

static int
sgi_get_bootpartition(void)
{
    return SGI_SSWAP16(sgilabel->boot_part);
}

static int
sgi_get_swappartition(void)
{
    return SGI_SSWAP16(sgilabel->swap_part);
}

static void
sgi_list_table(int xtra) {
    int i, w, wd;
    int kpi = 0;                /* kernel partition ID */

    if(xtra) {
	printf(_("\nDisk %s (SGI disk label): %d heads, %d sectors\n"
	       "%d cylinders, %d physical cylinders\n"
	       "%d extra sects/cyl, interleave %d:1\n"
	       "%s\n"
	       "Units = %s of %d * 512 bytes\n\n"),
	       disk_device, heads, sectors, cylinders,
	       SGI_SSWAP16(sgiparam.pcylcount),
	       SGI_SSWAP16(sgiparam.sparecyl),
	       SGI_SSWAP16(sgiparam.ilfact),
	       (char *)sgilabel,
	       str_units(PLURAL), units_per_sector);
    } else {
	printf( _("\nDisk %s (SGI disk label): "
		"%d heads, %d sectors, %d cylinders\n"
		"Units = %s of %d * 512 bytes\n\n"),
		disk_device, heads, sectors, cylinders,
		str_units(PLURAL), units_per_sector );
    }

    w = strlen(disk_device);
    wd = strlen(_("Device"));
    if (w < wd)
	w = wd;

    printf(_("----- partitions -----\n"
	   "Pt# %*s  Info     Start       End   Sectors  Id  System\n"),
	    w + 2, _("Device"));
    for (i = 0 ; i < partitions; i++) {
	    if( sgi_get_num_sectors(i) || debug ) {
	    uint32_t start = sgi_get_start_sector(i);
	    uint32_t len = sgi_get_num_sectors(i);
	    kpi++;              /* only count nonempty partitions */
	    printf(
		"%2d: %s %4s %9ld %9ld %9ld  %2x  %s\n",
/* fdisk part number */   i+1,
/* device */              partname(disk_device, kpi, w+3),
/* flags */               (sgi_get_swappartition() == i) ? "swap" :
/* flags */               (sgi_get_bootpartition() == i) ? "boot" : "    ",
/* start */               (long) scround(start),
/* end */                 (long) scround(start+len)-1,
/* no odd flag on end */  (long) len,
/* type id */             sgi_get_sysid(i),
/* type name */           partition_type(sgi_get_sysid(i)));
	}
    }
    printf(_("----- Bootinfo -----\nBootfile: %s\n"
	     "----- Directory Entries -----\n"),
	       sgilabel->boot_file);
	for (i = 0 ; i < sgi_volumes; i++) {
	    if (sgilabel->directory[i].vol_file_size) {
	    uint32_t start = SGI_SSWAP32(sgilabel->directory[i].vol_file_start);
	    uint32_t len = SGI_SSWAP32(sgilabel->directory[i].vol_file_size);
	    char*name = sgilabel->directory[i].vol_file_name;

	    printf(_("%2d: %-10s sector%5u size%8u\n"),
		    i, name, (unsigned int) start, (unsigned int) len);
	}
    }
}

static void
sgi_set_bootpartition( int i )
{
    sgilabel->boot_part = SGI_SSWAP16(((short)i));
}

static unsigned int
sgi_get_lastblock(void) {
    return heads * sectors * cylinders;
}

static void
sgi_set_swappartition( int i ) {
    sgilabel->swap_part = SGI_SSWAP16(((short)i));
}

static int
sgi_check_bootfile(const char* aFile) {

	if (strlen(aFile) < 3) /* "/a\n" is minimum */ {
		printf(_("\nInvalid Bootfile!\n"
		"\tThe bootfile must be an absolute non-zero pathname,\n"
			 "\te.g. \"/unix\" or \"/unix.save\".\n"));
	return 0;
	} else {
		if (strlen(aFile) > 16) {
			printf(_("\n\tName of Bootfile too long:  "
				 "16 bytes maximum.\n"));
	return 0;
		} else {
			if (aFile[0] != '/') {
				printf(_("\n\tBootfile must have a "
					 "fully qualified pathname.\n"));
	return 0;
    }
		}
	}
	if (strncmp(aFile, sgilabel->boot_file, 16)) {
		printf(_("\n\tBe aware, that the bootfile is not checked for existence.\n\t"
			 "SGI's default is \"/unix\" and for backup \"/unix.save\".\n"));
	/* filename is correct and did change */
	return 1;
    }
    return 0;   /* filename did not change */
}

static const char *
sgi_get_bootfile(void) {
	return sgilabel->boot_file;
}

static void
sgi_set_bootfile(const char* aFile) {
    int i = 0;

    if (sgi_check_bootfile(aFile)) {
	while (i < 16) {
	    if ((aFile[i] != '\n')  /* in principle caught again by next line */
			    &&  (strlen(aFile) > i))
		sgilabel->boot_file[i] = aFile[i];
	    else
		sgilabel->boot_file[i] = 0;
	    i++;
	}
	printf(_("\n\tBootfile is changed to \"%s\".\n"), sgilabel->boot_file);
    }
}

static void
create_sgiinfo(void)
{
    /* I keep SGI's habit to write the sgilabel to the second block */
    sgilabel->directory[0].vol_file_start = SGI_SSWAP32(2);
    sgilabel->directory[0].vol_file_size = SGI_SSWAP32(sizeof(sgiinfo));
    strncpy(sgilabel->directory[0].vol_file_name, "sgilabel", 8);
}

static sgiinfo *fill_sgiinfo(void);

static void
sgi_write_table(void) {
    sgilabel->csum = 0;
     sgilabel->csum = SGI_SSWAP32(two_s_complement_32bit_sum(
				 (unsigned int*)sgilabel,
					sizeof(*sgilabel)));
     assert(two_s_complement_32bit_sum(
		(unsigned int*)sgilabel, sizeof(*sgilabel)) == 0);
     if (lseek(fd, 0, SEEK_SET) < 0)
	fdisk_fatal(unable_to_seek);
     if (write(fd, sgilabel, SECTOR_SIZE) != SECTOR_SIZE)
	fdisk_fatal(unable_to_write);
     if (! strncmp(sgilabel->directory[0].vol_file_name, "sgilabel", 8)) {
	/*
	 * keep this habit of first writing the "sgilabel".
	 * I never tested whether it works without (AN 981002).
	 */
	 sgiinfo *info = fill_sgiinfo();
	 int infostartblock = SGI_SSWAP32(sgilabel->directory[0].vol_file_start);
	 if (lseek(fd, infostartblock*SECTOR_SIZE, SEEK_SET) < 0)
	    fdisk_fatal(unable_to_seek);
	 if (write(fd, info, SECTOR_SIZE) != SECTOR_SIZE)
	    fdisk_fatal(unable_to_write);
	 free(info);
    }
}

static int
compare_start(int *x, int *y) {
    /*
     * sort according to start sectors
     * and prefers largest partition:
     * entry zero is entire disk entry
     */
    unsigned int i = *x;
    unsigned int j = *y;
    unsigned int a = sgi_get_start_sector(i);
    unsigned int b = sgi_get_start_sector(j);
    unsigned int c = sgi_get_num_sectors(i);
    unsigned int d = sgi_get_num_sectors(j);

    if (a == b)
	return (d > c) ? 1 : (d == c) ? 0 : -1;
    return (a > b) ? 1 : -1;
}


static int
verify_sgi(int verbose)
{
    int Index[16];      /* list of valid partitions */
    int sortcount = 0;  /* number of used partitions, i.e. non-zero lengths */
    int entire = 0, i = 0;
    unsigned int start = 0;
    long long gap = 0;      /* count unused blocks */
    unsigned int lastblock = sgi_get_lastblock();

    clearfreelist();
    for (i=0; i<16; i++) {
	if (sgi_get_num_sectors(i) != 0) {
	    Index[sortcount++]=i;
	    if (sgi_get_sysid(i) == ENTIRE_DISK) {
		if (entire++ == 1) {
		    if (verbose)
			printf(_("More than one entire disk entry present.\n"));
		}
	    }
	}
    }
    if (sortcount == 0) {
	if (verbose)
	    printf(_("No partitions defined\n"));
	       return (lastblock > 0) ? 1 : (lastblock == 0) ? 0 : -1;
    }
    qsort(Index, sortcount, sizeof(Index[0]), (void*)compare_start);
    if (sgi_get_sysid(Index[0]) == ENTIRE_DISK) {
	if ((Index[0] != 10) && verbose)
	    printf(_("IRIX likes when Partition 11 covers the entire disk.\n"));
	    if ((sgi_get_start_sector(Index[0]) != 0) && verbose)
		printf(_("The entire disk partition should start "
				"at block 0,\n"
				"not at diskblock %d.\n"),
			      sgi_get_start_sector(Index[0]));
		if (debug)      /* I do not understand how some disks fulfil it */
		       if ((sgi_get_num_sectors(Index[0]) != lastblock) && verbose)
			       printf(_("The entire disk partition is only %d diskblock large,\n"
		    "but the disk is %d diskblocks long.\n"),
				      sgi_get_num_sectors(Index[0]), lastblock);
		lastblock = sgi_get_num_sectors(Index[0]);
    } else {
	    if (verbose)
		printf(_("One Partition (#11) should cover the entire disk.\n"));
	    if (debug>2)
		printf("sysid=%d\tpartition=%d\n",
			      sgi_get_sysid(Index[0]), Index[0]+1);
    }
    for (i=1, start=0; i<sortcount; i++) {
	int cylsize = sgi_get_nsect() * sgi_get_ntrks();

	    if ((sgi_get_start_sector(Index[i]) % cylsize) != 0) {
		if (debug)      /* I do not understand how some disks fulfil it */
		    if (verbose)
			printf(_("Partition %d does not start on cylinder boundary.\n"),
					      Index[i]+1);
	    }
	    if (sgi_get_num_sectors(Index[i]) % cylsize != 0) {
		if (debug)      /* I do not understand how some disks fulfil it */
		    if (verbose)
			printf(_("Partition %d does not end on cylinder boundary.\n"),
					      Index[i]+1);
	}
	/* We cannot handle several "entire disk" entries. */
	    if (sgi_get_sysid(Index[i]) == ENTIRE_DISK) continue;
	    if (start > sgi_get_start_sector(Index[i])) {
		if (verbose)
		    printf(_("The Partition %d and %d overlap by %d sectors.\n"),
			Index[i-1]+1, Index[i]+1,
				start - sgi_get_start_sector(Index[i]));
		if (gap >  0) gap = -gap;
		if (gap == 0) gap = -1;
	    }
	    if (start < sgi_get_start_sector(Index[i])) {
		if (verbose)
		    printf(_("Unused gap of %8u sectors - sectors %8u-%u\n"),
				sgi_get_start_sector(Index[i]) - start,
				start, sgi_get_start_sector(Index[i])-1);
		gap += sgi_get_start_sector(Index[i]) - start;
		add2freelist(start, sgi_get_start_sector(Index[i]));
	    }
	    start = sgi_get_start_sector(Index[i])
		       + sgi_get_num_sectors(Index[i]);
	    if (debug > 1) {
		if (verbose)
		    printf("%2d:%12d\t%12d\t%12d\n", Index[i],
			sgi_get_start_sector(Index[i]),
			sgi_get_num_sectors(Index[i]),
				sgi_get_sysid(Index[i]));
	}
    }
    if (start < lastblock) {
	if (verbose)
		printf(_("Unused gap of %8u sectors - sectors %8u-%u\n"),
			    lastblock - start, start, lastblock-1);
	gap += lastblock - start;
	add2freelist(start, lastblock);
    }
    /*
     * Done with arithmetics
     * Go for details now
     */
    if (verbose) {
	if (!sgi_get_num_sectors(sgi_get_bootpartition())) {
	    printf(_("\nThe boot partition does not exist.\n"));
	}
	if (!sgi_get_num_sectors(sgi_get_swappartition())) {
	    printf(_("\nThe swap partition does not exist.\n"));
	} else {
	    if ((sgi_get_sysid(sgi_get_swappartition()) != SGI_SWAP)
			&&  (sgi_get_sysid(sgi_get_swappartition()) != LINUX_SWAP))
		printf(_("\nThe swap partition has no swap type.\n"));
	}
	if (sgi_check_bootfile("/unix"))
	    printf(_("\tYou have chosen an unusual boot file name.\n"));
    }
    return (gap > 0) ? 1 : (gap == 0) ? 0 : -1;
}

static int
sgi_gaps(void) {
    /*
     * returned value is:
     *  = 0 : disk is properly filled to the rim
     *  < 0 : there is an overlap
     *  > 0 : there is still some vacant space
     */
    return verify_sgi(0);
}

static void
sgi_change_sysid( int i, int sys )
{
    if( sgi_get_num_sectors(i) == 0 ) /* caught already before, ... */
    {
	printf(_("Sorry You may change the Tag of non-empty partitions.\n"));
	return;
    }
    if( ((sys != ENTIRE_DISK ) && (sys != SGI_VOLHDR))
     && (sgi_get_start_sector(i)<1) )
    {
	read_chars(
	_("It is highly recommended that the partition at offset 0\n"
	"is of type \"SGI volhdr\", the IRIX system will rely on it to\n"
	"retrieve from its directory standalone tools like sash and fx.\n"
	"Only the \"SGI volume\" entire disk section may violate this.\n"
	"Type YES if you are sure about tagging this partition differently.\n"));
	if (strcmp (line_ptr, _("YES\n")))
		    return;
    }
    sgilabel->partitions[i].id = SGI_SSWAP32(sys);
}

/* returns partition index of first entry marked as entire disk */
static int
sgi_entire(void) {
    int i;

    for(i=0; i<16; i++)
	if(sgi_get_sysid(i) == SGI_VOLUME)
	    return i;
    return -1;
}

static void
sgi_set_partition(int i, unsigned int start, unsigned int length, int sys) {

    sgilabel->partitions[i].id = SGI_SSWAP32(sys);
    sgilabel->partitions[i].num_sectors = SGI_SSWAP32(length);
    sgilabel->partitions[i].start_sector = SGI_SSWAP32(start);
    set_changed(i);
    if (sgi_gaps() < 0)     /* rebuild freelist */
	printf(_("Do You know, You got a partition overlap on the disk?\n"));
}

static void
sgi_set_entire(void) {
    int n;

    for(n=10; n < partitions; n++) {
	if(!sgi_get_num_sectors(n) ) {
	    sgi_set_partition(n, 0, sgi_get_lastblock(), SGI_VOLUME);
	    break;
	}
    }
}

static void
sgi_set_volhdr(void)
{
    int n;
    for( n=8; n<partitions; n++ )
    {
	if(!sgi_get_num_sectors( n ) )
	{
	    /*
	     * 5 cylinders is an arbitrary value I like
	     * IRIX 5.3 stored files in the volume header
	     * (like sash, symmon, fx, ide) with ca. 3200
	     * sectors.
	     */
	    if( heads * sectors * 5 < sgi_get_lastblock() )
		sgi_set_partition( n, 0, heads * sectors * 5, SGI_VOLHDR );
	    break;
	}
    }
}

static void
sgi_delete_partition( int i )
{
    sgi_set_partition( i, 0, 0, 0 );
}

static void
sgi_add_partition( int n, int sys )
{
    char mesg[256];
    unsigned int first=0, last=0;

    if( n == 10 ) {
	sys = SGI_VOLUME;
    } else if ( n == 8 ) {
	sys = 0;
    }
    if(sgi_get_num_sectors(n)) {
	printf(_("Partition %d is already defined.  Delete "
		"it before re-adding it.\n"), n + 1);
	return;
    }
    if( (sgi_entire() == -1) &&  (sys != SGI_VOLUME) ) {
	printf(_("Attempting to generate entire disk entry automatically.\n"));
	sgi_set_entire();
	sgi_set_volhdr();
    }
    if( (sgi_gaps() == 0) &&  (sys != SGI_VOLUME) ) {
	printf(_("The entire disk is already covered with partitions.\n"));
	return;
    }
    if(sgi_gaps() < 0) {
	printf(_("You got a partition overlap on the disk. Fix it first!\n"));
	return;
    }
    snprintf(mesg, sizeof(mesg), _("First %s"), str_units(SINGULAR));
    for(;;) {
	if(sys == SGI_VOLUME) {
	    last = sgi_get_lastblock();
	    first = read_int(0, 0, last-1, 0, mesg);
	    if( first != 0 ) {
		printf(_("It is highly recommended that eleventh partition\n"
		       "covers the entire disk and is of type `SGI volume'\n"));
	    }
	} else {
	    first = freelist[0].first;
	    last  = freelist[0].last;
	    first = read_int(scround(first), scround(first), scround(last)-1,
			     0, mesg);
	}
	if (display_in_cyl_units)
	    first *= units_per_sector;
	else
	    first = first; /* align to cylinder if you know how ... */
	if( !last )
	    last = isinfreelist(first);
	if( last == 0 ) {
	    printf(_("You will get a partition overlap on the disk. "
		    "Fix it first!\n"));
	} else
	    break;
    }
    snprintf(mesg, sizeof(mesg), _(" Last %s"), str_units(SINGULAR));
    last = read_int(scround(first), scround(last)-1, scround(last)-1,
		    scround(first), mesg)+1;
    if (display_in_cyl_units)
	last *= units_per_sector;
    else
	last = last; /* align to cylinder if You know how ... */
    if( (sys == SGI_VOLUME) && ( first != 0 || last != sgi_get_lastblock() ) )
	printf(_("It is highly recommended that eleventh partition\n"
		"covers the entire disk and is of type `SGI volume'\n"));
    sgi_set_partition( n, first, last-first, sys );
}

#ifdef CONFIG_FEATURE_FDISK_ADVANCED
static void
create_sgilabel(void)
{
    struct hd_geometry geometry;
    struct {
	unsigned int start;
	unsigned int nsect;
	int sysid;
    } old[4];
    int i=0;
    long longsectors;               /* the number of sectors on the device */
    int res;                        /* the result from the ioctl */
    int sec_fac;                    /* the sector factor */

    sec_fac = sector_size / 512;    /* determine the sector factor */

    fprintf( stderr,
	_("Building a new SGI disklabel. Changes will remain in memory only,\n"
	"until you decide to write them. After that, of course, the previous\n"
	"content will be unrecoverably lost.\n\n"));

    sgi_other_endian = (BYTE_ORDER == LITTLE_ENDIAN);
    res = ioctl(fd, BLKGETSIZE, &longsectors);
    if (!ioctl(fd, HDIO_GETGEO, &geometry)) {
	heads = geometry.heads;
	sectors = geometry.sectors;
	if (res == 0) {
	    /* the get device size ioctl was successful */
	    cylinders = longsectors / (heads * sectors);
	    cylinders /= sec_fac;
	} else {
	    /* otherwise print error and use truncated version */
	cylinders = geometry.cylinders;
	    fprintf(stderr,
		   _("Warning:  BLKGETSIZE ioctl failed on %s.  "
		     "Using geometry cylinder value of %d.\n"
		     "This value may be truncated for devices"
		     " > 33.8 GB.\n"), disk_device, cylinders);
    }
    }
    for (i = 0; i < 4; i++) {
	old[i].sysid = 0;
	if(valid_part_table_flag(MBRbuffer)) {
	    if(get_part_table(i)->sys_ind) {
		old[i].sysid = get_part_table(i)->sys_ind;
		old[i].start = get_start_sect(get_part_table(i));
		old[i].nsect = get_nr_sects(get_part_table(i));
		printf(_("Trying to keep parameters of partition %d.\n"), i);
		if (debug)
		    printf(_("ID=%02x\tSTART=%d\tLENGTH=%d\n"),
			old[i].sysid, old[i].start, old[i].nsect);
	    }
	}
    }

    memset(MBRbuffer, 0, sizeof(MBRbuffer));
    sgilabel->magic = SGI_SSWAP32(SGI_LABEL_MAGIC);
    sgilabel->boot_part = SGI_SSWAP16(0);
    sgilabel->swap_part = SGI_SSWAP16(1);

    /* sizeof(sgilabel->boot_file) = 16 > 6 */
    memset(sgilabel->boot_file, 0, 16);
    strcpy(sgilabel->boot_file, "/unix");

    sgilabel->devparam.skew                     = (0);
    sgilabel->devparam.gap1                     = (0);
    sgilabel->devparam.gap2                     = (0);
    sgilabel->devparam.sparecyl                 = (0);
    sgilabel->devparam.pcylcount                = SGI_SSWAP16(geometry.cylinders);
    sgilabel->devparam.head_vol0                = SGI_SSWAP16(0);
    sgilabel->devparam.ntrks                    = SGI_SSWAP16(geometry.heads);
						/* tracks/cylinder (heads) */
    sgilabel->devparam.cmd_tag_queue_depth      = (0);
    sgilabel->devparam.unused0                  = (0);
    sgilabel->devparam.unused1                  = SGI_SSWAP16(0);
    sgilabel->devparam.nsect                    = SGI_SSWAP16(geometry.sectors);
						/* sectors/track */
    sgilabel->devparam.bytes                    = SGI_SSWAP16(512);
    sgilabel->devparam.ilfact                   = SGI_SSWAP16(1);
    sgilabel->devparam.flags                    = SGI_SSWAP32(TRACK_FWD|
							IGNORE_ERRORS|RESEEK);
    sgilabel->devparam.datarate                 = SGI_SSWAP32(0);
    sgilabel->devparam.retries_on_error         = SGI_SSWAP32(1);
    sgilabel->devparam.ms_per_word              = SGI_SSWAP32(0);
    sgilabel->devparam.xylogics_gap1            = SGI_SSWAP16(0);
    sgilabel->devparam.xylogics_syncdelay       = SGI_SSWAP16(0);
    sgilabel->devparam.xylogics_readdelay       = SGI_SSWAP16(0);
    sgilabel->devparam.xylogics_gap2            = SGI_SSWAP16(0);
    sgilabel->devparam.xylogics_readgate        = SGI_SSWAP16(0);
    sgilabel->devparam.xylogics_writecont       = SGI_SSWAP16(0);
    memset( &(sgilabel->directory), 0, sizeof(struct volume_directory)*15 );
    memset( &(sgilabel->partitions), 0, sizeof(struct sgi_partition)*16 );
    sgi_label  =  1;
    partitions = 16;
    sgi_volumes    = 15;
    sgi_set_entire();
    sgi_set_volhdr();
    for (i = 0; i < 4; i++) {
	if(old[i].sysid) {
	    sgi_set_partition(i, old[i].start, old[i].nsect, old[i].sysid);
	}
    }
}

static void
sgi_set_xcyl(void)
{
    /* do nothing in the beginning */
}
#endif /* CONFIG_FEATURE_FDISK_ADVANCED */

/* _____________________________________________________________
 */

static sgiinfo *
fill_sgiinfo(void)
{
    sgiinfo *info = calloc(1, sizeof(sgiinfo));

    info->magic=SGI_SSWAP32(SGI_INFO_MAGIC);
    info->b1=SGI_SSWAP32(-1);
    info->b2=SGI_SSWAP16(-1);
    info->b3=SGI_SSWAP16(1);
    /* You may want to replace this string !!!!!!! */
    strcpy( info->scsi_string, "IBM OEM 0662S12         3 30" );
    strcpy( info->serial, "0000" );
    info->check1816 = SGI_SSWAP16(18*256 +16 );
    strcpy( info->installer, "Sfx version 5.3, Oct 18, 1994" );
    return info;
}
#endif /* SGI_LABEL */


#ifdef CONFIG_FEATURE_SUN_LABEL
/*
 * fdisksunlabel.c
 *
 * I think this is mostly, or entirely, due to
 *      Jakub Jelinek (jj@sunsite.mff.cuni.cz), July 1996
 *
 * Merged with fdisk for other architectures, aeb, June 1998.
 *
 * Sat Mar 20 EST 1999 Arnaldo Carvalho de Melo <acme@conectiva.com.br>
 *      Internationalization
 */


static int     sun_other_endian;
static int     scsi_disk;
static int     floppy;

#ifndef IDE0_MAJOR
#define IDE0_MAJOR 3
#endif
#ifndef IDE1_MAJOR
#define IDE1_MAJOR 22
#endif

static void guess_device_type(void) {
	struct stat bootstat;

	if (fstat (fd, &bootstat) < 0) {
		scsi_disk = 0;
		floppy = 0;
	} else if (S_ISBLK(bootstat.st_mode)
		   && (major(bootstat.st_rdev) == IDE0_MAJOR ||
		       major(bootstat.st_rdev) == IDE1_MAJOR)) {
		scsi_disk = 0;
		floppy = 0;
	} else if (S_ISBLK(bootstat.st_mode)
		   && major(bootstat.st_rdev) == FLOPPY_MAJOR) {
		scsi_disk = 0;
		floppy = 1;
	} else {
		scsi_disk = 1;
		floppy = 0;
	}
}

static const struct systypes sun_sys_types[] = {
/* 0            */  {"\x00" "Empty"        },
/* 1            */  {"\x01" "Boot"         },
/* 2            */  {"\x02" "SunOS root"   },
/* SUNOS_SWAP   */  {"\x03" "SunOS swap"   },
/* 4            */  {"\x04" "SunOS usr"    },
/* WHOLE_DISK   */  {"\x05" "Whole disk"   },
/* 6            */  {"\x06" "SunOS stand"  },
/* 7            */  {"\x07" "SunOS var"    },
/* 8            */  {"\x08" "SunOS home"   },
/* LINUX_SWAP   */  {"\x82" "Linux swap"   },
/* LINUX_NATIVE */  {"\x83" "Linux native" },
/* 0x8e         */  {"\x8e" "Linux LVM"    },
/* New (2.2.x) raid partition with autodetect using persistent superblock */
/* 0xfd         */  {"\xfd" "Linux raid autodetect" },
		    { NULL }
};


static void
set_sun_partition(int i, uint start, uint stop, int sysid) {
	sunlabel->infos[i].id = sysid;
	sunlabel->partitions[i].start_cylinder =
		SUN_SSWAP32(start / (heads * sectors));
	sunlabel->partitions[i].num_sectors =
		SUN_SSWAP32(stop - start);
	set_changed(i);
}

static void
sun_nolabel(void) {
	sun_label = 0;
	sunlabel->magic = 0;
	partitions = 4;
}

static int
check_sun_label(void) {
	unsigned short *ush;
	int csum;

	if (sunlabel->magic != SUN_LABEL_MAGIC &&
	    sunlabel->magic != SUN_LABEL_MAGIC_SWAPPED) {
		sun_label = 0;
		sun_other_endian = 0;
		return 0;
	}
	sun_other_endian = (sunlabel->magic == SUN_LABEL_MAGIC_SWAPPED);
	ush = ((unsigned short *) (sunlabel + 1)) - 1;
	for (csum = 0; ush >= (unsigned short *)sunlabel;) csum ^= *ush--;
	if (csum) {
		fprintf(stderr,_("Detected sun disklabel with wrong checksum.\n"
				"Probably you'll have to set all the values,\n"
				"e.g. heads, sectors, cylinders and partitions\n"
				"or force a fresh label (s command in main menu)\n"));
	} else {
		heads = SUN_SSWAP16(sunlabel->ntrks);
		cylinders = SUN_SSWAP16(sunlabel->ncyl);
		sectors = SUN_SSWAP16(sunlabel->nsect);
	}
	update_units();
	sun_label = 1;
	partitions = 8;
	return 1;
}

static const struct sun_predefined_drives {
	const char *vendor;
	const char *model;
	unsigned short sparecyl;
	unsigned short ncyl;
	unsigned short nacyl;
	unsigned short pcylcount;
	unsigned short ntrks;
	unsigned short nsect;
	unsigned short rspeed;
} sun_drives[] = {
{"Quantum","ProDrive 80S",1,832,2,834,6,34,3662},
{"Quantum","ProDrive 105S",1,974,2,1019,6,35,3662},
{"CDC","Wren IV 94171-344",3,1545,2,1549,9,46,3600},
{"IBM","DPES-31080",0,4901,2,4903,4,108,5400},
{"IBM","DORS-32160",0,1015,2,1017,67,62,5400},
{"IBM","DNES-318350",0,11199,2,11474,10,320,7200},
{"SEAGATE","ST34371",0,3880,2,3882,16,135,7228},
{"","SUN0104",1,974,2,1019,6,35,3662},
{"","SUN0207",4,1254,2,1272,9,36,3600},
{"","SUN0327",3,1545,2,1549,9,46,3600},
{"","SUN0340",0,1538,2,1544,6,72,4200},
{"","SUN0424",2,1151,2,2500,9,80,4400},
{"","SUN0535",0,1866,2,2500,7,80,5400},
{"","SUN0669",5,1614,2,1632,15,54,3600},
{"","SUN1.0G",5,1703,2,1931,15,80,3597},
{"","SUN1.05",0,2036,2,2038,14,72,5400},
{"","SUN1.3G",6,1965,2,3500,17,80,5400},
{"","SUN2.1G",0,2733,2,3500,19,80,5400},
{"IOMEGA","Jaz",0,1019,2,1021,64,32,5394},
};

static const struct sun_predefined_drives *
sun_autoconfigure_scsi(void) {
    const struct sun_predefined_drives *p = NULL;

#ifdef SCSI_IOCTL_GET_IDLUN
    unsigned int id[2];
    char buffer[2048];
    char buffer2[2048];
    FILE *pfd;
    char *vendor;
    char *model;
    char *q;
    int i;

    if (!ioctl(fd, SCSI_IOCTL_GET_IDLUN, &id)) {
	sprintf(buffer,
	    "Host: scsi%d Channel: %02d Id: %02d Lun: %02d\n",
#if 0
	    ((id[0]>>24)&0xff)-/*PROC_SCSI_SCSI+PROC_SCSI_FILE*/33,
#else
	    /* This is very wrong (works only if you have one HBA),
	       but I haven't found a way how to get hostno
	       from the current kernel */
	    0,
#endif
	    (id[0]>>16)&0xff,
	    id[0]&0xff,
	    (id[0]>>8)&0xff);
	pfd = fopen("/proc/scsi/scsi","r");
	if (pfd) {
	    while (fgets(buffer2,2048,pfd)) {
		if (!strcmp(buffer, buffer2)) {
		    if (fgets(buffer2,2048,pfd)) {
			q = strstr(buffer2,"Vendor: ");
			if (q) {
			    q += 8;
			    vendor = q;
			    q = strstr(q," ");
			    *q++ = 0;   /* truncate vendor name */
			    q = strstr(q,"Model: ");
			    if (q) {
				*q = 0;
				q += 7;
				model = q;
				q = strstr(q," Rev: ");
				if (q) {
				    *q = 0;
				    for (i = 0; i < SIZE(sun_drives); i++) {
					if (*sun_drives[i].vendor && strcasecmp(sun_drives[i].vendor, vendor))
					    continue;
					if (!strstr(model, sun_drives[i].model))
					    continue;
					printf(_("Autoconfigure found a %s%s%s\n"),sun_drives[i].vendor,(*sun_drives[i].vendor) ? " " : "",sun_drives[i].model);
					p = sun_drives + i;
					break;
				    }
				}
			    }
			}
		    }
		    break;
		}
	    }
	    fclose(pfd);
	}
    }
#endif
    return p;
}

static void create_sunlabel(void)
{
	struct hd_geometry geometry;
	unsigned int ndiv;
	int i;
	unsigned char c;
	const struct sun_predefined_drives *p = NULL;

	fprintf(stderr,
	_("Building a new sun disklabel. Changes will remain in memory only,\n"
	"until you decide to write them. After that, of course, the previous\n"
	"content won't be recoverable.\n\n"));
#if BYTE_ORDER == LITTLE_ENDIAN
	sun_other_endian = 1;
#else
	sun_other_endian = 0;
#endif
	memset(MBRbuffer, 0, sizeof(MBRbuffer));
	sunlabel->magic = SUN_SSWAP16(SUN_LABEL_MAGIC);
	if (!floppy) {
	    puts(_("Drive type\n"
		 "   ?   auto configure\n"
		 "   0   custom (with hardware detected defaults)"));
	    for (i = 0; i < SIZE(sun_drives); i++) {
		printf("   %c   %s%s%s\n",
		       i + 'a', sun_drives[i].vendor,
		       (*sun_drives[i].vendor) ? " " : "",
		       sun_drives[i].model);
	    }
	    for (;;) {
		c = read_char(_("Select type (? for auto, 0 for custom): "));
		if (c >= 'a' && c < 'a' + SIZE(sun_drives)) {
		    p = sun_drives + c - 'a';
		    break;
		} else if (c >= 'A' && c < 'A' + SIZE(sun_drives)) {
		    p = sun_drives + c - 'A';
		    break;
		} else if (c == '0') {
		    break;
		} else if (c == '?' && scsi_disk) {
		    p = sun_autoconfigure_scsi();
		    if (!p)
			printf(_("Autoconfigure failed.\n"));
		    else
			break;
		}
	    }
	}
	if (!p || floppy) {
	    if (!ioctl(fd, HDIO_GETGEO, &geometry)) {
		heads = geometry.heads;
		sectors = geometry.sectors;
		cylinders = geometry.cylinders;
	    } else {
		heads = 0;
		sectors = 0;
		cylinders = 0;
	    }
	    if (floppy) {
		sunlabel->nacyl = 0;
		sunlabel->pcylcount = SUN_SSWAP16(cylinders);
		sunlabel->rspeed = SUN_SSWAP16(300);
		sunlabel->ilfact = SUN_SSWAP16(1);
		sunlabel->sparecyl = 0;
	    } else {
		heads = read_int(1,heads,1024,0,_("Heads"));
		sectors = read_int(1,sectors,1024,0,_("Sectors/track"));
		if (cylinders)
		    cylinders = read_int(1,cylinders-2,65535,0,_("Cylinders"));
		else
		    cylinders = read_int(1,0,65535,0,_("Cylinders"));
		sunlabel->nacyl =
			SUN_SSWAP16(read_int(0,2,65535,0,
					 _("Alternate cylinders")));
		sunlabel->pcylcount =
			SUN_SSWAP16(read_int(0,cylinders+SUN_SSWAP16(sunlabel->nacyl),
					 65535,0,_("Physical cylinders")));
		sunlabel->rspeed =
			SUN_SSWAP16(read_int(1,5400,100000,0,
					 _("Rotation speed (rpm)")));
		sunlabel->ilfact =
			SUN_SSWAP16(read_int(1,1,32,0,_("Interleave factor")));
		sunlabel->sparecyl =
			SUN_SSWAP16(read_int(0,0,sectors,0,
					 _("Extra sectors per cylinder")));
	    }
	} else {
	    sunlabel->sparecyl = SUN_SSWAP16(p->sparecyl);
	    sunlabel->ncyl = SUN_SSWAP16(p->ncyl);
	    sunlabel->nacyl = SUN_SSWAP16(p->nacyl);
	    sunlabel->pcylcount = SUN_SSWAP16(p->pcylcount);
	    sunlabel->ntrks = SUN_SSWAP16(p->ntrks);
	    sunlabel->nsect = SUN_SSWAP16(p->nsect);
	    sunlabel->rspeed = SUN_SSWAP16(p->rspeed);
	    sunlabel->ilfact = SUN_SSWAP16(1);
	    cylinders = p->ncyl;
	    heads = p->ntrks;
	    sectors = p->nsect;
	    puts(_("You may change all the disk params from the x menu"));
	}

	snprintf(sunlabel->info, sizeof(sunlabel->info),
		 "%s%s%s cyl %d alt %d hd %d sec %d",
		 p ? p->vendor : "", (p && *p->vendor) ? " " : "",
		 p ? p->model
		   : (floppy ? _("3,5\" floppy") : _("Linux custom")),
		cylinders, SUN_SSWAP16(sunlabel->nacyl), heads, sectors);

	sunlabel->ntrks = SUN_SSWAP16(heads);
	sunlabel->nsect = SUN_SSWAP16(sectors);
	sunlabel->ncyl = SUN_SSWAP16(cylinders);
	if (floppy)
	    set_sun_partition(0, 0, cylinders * heads * sectors, LINUX_NATIVE);
	else {
	    if (cylinders * heads * sectors >= 150 * 2048) {
		ndiv = cylinders - (50 * 2048 / (heads * sectors)); /* 50M swap */
	    } else
		ndiv = cylinders * 2 / 3;
	    set_sun_partition(0, 0, ndiv * heads * sectors, LINUX_NATIVE);
	    set_sun_partition(1, ndiv * heads * sectors, cylinders * heads * sectors, LINUX_SWAP);
	    sunlabel->infos[1].flags |= 0x01; /* Not mountable */
	}
	set_sun_partition(2, 0, cylinders * heads * sectors, WHOLE_DISK);
	{
		unsigned short *ush = (unsigned short *)sunlabel;
		unsigned short csum = 0;
		while(ush < (unsigned short *)(&sunlabel->csum))
			csum ^= *ush++;
		sunlabel->csum = csum;
	}

	set_all_unchanged();
	set_changed(0);
	get_boot(create_empty_sun);
}

static void
toggle_sunflags(int i, unsigned char mask) {
	if (sunlabel->infos[i].flags & mask)
		sunlabel->infos[i].flags &= ~mask;
	else sunlabel->infos[i].flags |= mask;
	set_changed(i);
}

static void
fetch_sun(uint *starts, uint *lens, uint *start, uint *stop) {
	int i, continuous = 1;
	*start = 0; *stop = cylinders * heads * sectors;
	for (i = 0; i < partitions; i++) {
		if (sunlabel->partitions[i].num_sectors
		    && sunlabel->infos[i].id
		    && sunlabel->infos[i].id != WHOLE_DISK) {
			starts[i] = SUN_SSWAP32(sunlabel->partitions[i].start_cylinder) * heads * sectors;
			lens[i] = SUN_SSWAP32(sunlabel->partitions[i].num_sectors);
			if (continuous) {
				if (starts[i] == *start)
					*start += lens[i];
				else if (starts[i] + lens[i] >= *stop)
					*stop = starts[i];
				else
					continuous = 0;
					/* There will be probably more gaps
					  than one, so lets check afterwards */
			}
		} else {
			starts[i] = 0;
			lens[i] = 0;
		}
	}
}

static uint *verify_sun_starts;

static int
verify_sun_cmp(int *a, int *b) {
    if (*a == -1) return 1;
    if (*b == -1) return -1;
    if (verify_sun_starts[*a] > verify_sun_starts[*b]) return 1;
    return -1;
}

static void
verify_sun(void) {
    uint starts[8], lens[8], start, stop;
    int i,j,k,starto,endo;
    int array[8];

    verify_sun_starts = starts;
    fetch_sun(starts,lens,&start,&stop);
    for (k = 0; k < 7; k++) {
	for (i = 0; i < 8; i++) {
	    if (k && (lens[i] % (heads * sectors))) {
		printf(_("Partition %d doesn't end on cylinder boundary\n"), i+1);
	    }
	    if (lens[i]) {
		for (j = 0; j < i; j++)
		    if (lens[j]) {
			if (starts[j] == starts[i]+lens[i]) {
			    starts[j] = starts[i]; lens[j] += lens[i];
			    lens[i] = 0;
			} else if (starts[i] == starts[j]+lens[j]){
			    lens[j] += lens[i];
			    lens[i] = 0;
			} else if (!k) {
			    if (starts[i] < starts[j]+lens[j] &&
				starts[j] < starts[i]+lens[i]) {
				starto = starts[i];
				if (starts[j] > starto)
					starto = starts[j];
				endo = starts[i]+lens[i];
				if (starts[j]+lens[j] < endo)
					endo = starts[j]+lens[j];
				printf(_("Partition %d overlaps with others in "
				       "sectors %d-%d\n"), i+1, starto, endo);
			    }
			}
		    }
	    }
	}
    }
    for (i = 0; i < 8; i++) {
	if (lens[i])
	    array[i] = i;
	else
	    array[i] = -1;
    }
    qsort(array,SIZE(array),sizeof(array[0]),
	  (int (*)(const void *,const void *)) verify_sun_cmp);
    if (array[0] == -1) {
	printf(_("No partitions defined\n"));
	return;
    }
    stop = cylinders * heads * sectors;
    if (starts[array[0]])
	printf(_("Unused gap - sectors 0-%d\n"),starts[array[0]]);
    for (i = 0; i < 7 && array[i+1] != -1; i++) {
	printf(_("Unused gap - sectors %d-%d\n"),starts[array[i]]+lens[array[i]],starts[array[i+1]]);
    }
    start = starts[array[i]]+lens[array[i]];
    if (start < stop)
	printf(_("Unused gap - sectors %d-%d\n"),start,stop);
}

static void
add_sun_partition(int n, int sys) {
	uint start, stop, stop2;
	uint starts[8], lens[8];
	int whole_disk = 0;

	char mesg[256];
	int i, first, last;

	if (sunlabel->partitions[n].num_sectors && sunlabel->infos[n].id) {
		printf(_("Partition %d is already defined.  Delete "
			"it before re-adding it.\n"), n + 1);
		return;
	}

	fetch_sun(starts,lens,&start,&stop);
	if (stop <= start) {
		if (n == 2)
			whole_disk = 1;
		else {
			printf(_("Other partitions already cover the whole disk.\nDelete "
			       "some/shrink them before retry.\n"));
			return;
		}
	}
	snprintf(mesg, sizeof(mesg), _("First %s"), str_units(SINGULAR));
	for (;;) {
		if (whole_disk)
			first = read_int(0, 0, 0, 0, mesg);
		else
			first = read_int(scround(start), scround(stop)+1,
					 scround(stop), 0, mesg);
		if (display_in_cyl_units)
			first *= units_per_sector;
		else
			/* Starting sector has to be properly aligned */
			first = (first + heads * sectors - 1) / (heads * sectors);
		if (n == 2 && first != 0)
			printf ("\
It is highly recommended that the third partition covers the whole disk\n\
and is of type `Whole disk'\n");
		/* ewt asks to add: "don't start a partition at cyl 0"
		   However, edmundo@rano.demon.co.uk writes:
		   "In addition to having a Sun partition table, to be able to
		   boot from the disc, the first partition, /dev/sdX1, must
		   start at cylinder 0. This means that /dev/sdX1 contains
		   the partition table and the boot block, as these are the
		   first two sectors of the disc. Therefore you must be
		   careful what you use /dev/sdX1 for. In particular, you must
		   not use a partition starting at cylinder 0 for Linux swap,
		   as that would overwrite the partition table and the boot
		   block. You may, however, use such a partition for a UFS
		   or EXT2 file system, as these file systems leave the first
		   1024 bytes undisturbed. */
		/* On the other hand, one should not use partitions
		   starting at block 0 in an md, or the label will
		   be trashed. */
		for (i = 0; i < partitions; i++)
			if (lens[i] && starts[i] <= first
				    && starts[i] + lens[i] > first)
				break;
		if (i < partitions && !whole_disk) {
			if (n == 2 && !first) {
			    whole_disk = 1;
			    break;
			}
			printf(_("Sector %d is already allocated\n"), first);
		} else
			break;
	}
	stop = cylinders * heads * sectors;
	stop2 = stop;
	for (i = 0; i < partitions; i++) {
		if (starts[i] > first && starts[i] < stop)
			stop = starts[i];
	}
	snprintf(mesg, sizeof(mesg),
		 _("Last %s or +size or +sizeM or +sizeK"),
		 str_units(SINGULAR));
	if (whole_disk)
		last = read_int(scround(stop2), scround(stop2), scround(stop2),
				0, mesg);
	else if (n == 2 && !first)
		last = read_int(scround(first), scround(stop2), scround(stop2),
				scround(first), mesg);
	else
		last = read_int(scround(first), scround(stop), scround(stop),
				scround(first), mesg);
	if (display_in_cyl_units)
		last *= units_per_sector;
	if (n == 2 && !first) {
		if (last >= stop2) {
		    whole_disk = 1;
		    last = stop2;
		} else if (last > stop) {
		    printf (
   _("You haven't covered the whole disk with the 3rd partition, but your value\n"
     "%d %s covers some other partition. Your entry has been changed\n"
     "to %d %s\n"),
			scround(last), str_units(SINGULAR),
			scround(stop), str_units(SINGULAR));
		    last = stop;
		}
	} else if (!whole_disk && last > stop)
		last = stop;

	if (whole_disk) sys = WHOLE_DISK;
	set_sun_partition(n, first, last, sys);
}

static void
sun_delete_partition(int i) {
	unsigned int nsec;

	if (i == 2 && sunlabel->infos[i].id == WHOLE_DISK &&
	    !sunlabel->partitions[i].start_cylinder &&
	    (nsec = SUN_SSWAP32(sunlabel->partitions[i].num_sectors))
	      == heads * sectors * cylinders)
		printf(_("If you want to maintain SunOS/Solaris compatibility, "
		       "consider leaving this\n"
		       "partition as Whole disk (5), starting at 0, with %u "
		       "sectors\n"), nsec);
	sunlabel->infos[i].id = 0;
	sunlabel->partitions[i].num_sectors = 0;
}

static void
sun_change_sysid(int i, int sys) {
	if (sys == LINUX_SWAP && !sunlabel->partitions[i].start_cylinder) {
	    read_chars(
	      _("It is highly recommended that the partition at offset 0\n"
	      "is UFS, EXT2FS filesystem or SunOS swap. Putting Linux swap\n"
	      "there may destroy your partition table and bootblock.\n"
	      "Type YES if you're very sure you would like that partition\n"
	      "tagged with 82 (Linux swap): "));
	    if (strcmp (line_ptr, _("YES\n")))
		    return;
	}
	switch (sys) {
	case SUNOS_SWAP:
	case LINUX_SWAP:
		/* swaps are not mountable by default */
		sunlabel->infos[i].flags |= 0x01;
		break;
	default:
		/* assume other types are mountable;
		   user can change it anyway */
		sunlabel->infos[i].flags &= ~0x01;
		break;
	}
	sunlabel->infos[i].id = sys;
}

static void
sun_list_table(int xtra) {
	int i, w;

	w = strlen(disk_device);
	if (xtra)
		printf(
		_("\nDisk %s (Sun disk label): %d heads, %d sectors, %d rpm\n"
		"%d cylinders, %d alternate cylinders, %d physical cylinders\n"
		"%d extra sects/cyl, interleave %d:1\n"
		"%s\n"
		"Units = %s of %d * 512 bytes\n\n"),
		       disk_device, heads, sectors, SUN_SSWAP16(sunlabel->rspeed),
		       cylinders, SUN_SSWAP16(sunlabel->nacyl),
		       SUN_SSWAP16(sunlabel->pcylcount),
		       SUN_SSWAP16(sunlabel->sparecyl),
		       SUN_SSWAP16(sunlabel->ilfact),
		       (char *)sunlabel,
		       str_units(PLURAL), units_per_sector);
	else
		printf(
	_("\nDisk %s (Sun disk label): %d heads, %d sectors, %d cylinders\n"
	"Units = %s of %d * 512 bytes\n\n"),
		       disk_device, heads, sectors, cylinders,
		       str_units(PLURAL), units_per_sector);

	printf(_("%*s Flag    Start       End    Blocks   Id  System\n"),
	       w + 1, _("Device"));
	for (i = 0 ; i < partitions; i++) {
		if (sunlabel->partitions[i].num_sectors) {
			uint32_t start = SUN_SSWAP32(sunlabel->partitions[i].start_cylinder) * heads * sectors;
			uint32_t len = SUN_SSWAP32(sunlabel->partitions[i].num_sectors);
			printf(
			    "%s %c%c %9ld %9ld %9ld%c  %2x  %s\n",
/* device */              partname(disk_device, i+1, w),
/* flags */               (sunlabel->infos[i].flags & 0x01) ? 'u' : ' ',
			  (sunlabel->infos[i].flags & 0x10) ? 'r' : ' ',
/* start */               (long) scround(start),
/* end */                 (long) scround(start+len),
/* odd flag on end */     (long) len / 2, len & 1 ? '+' : ' ',
/* type id */             sunlabel->infos[i].id,
/* type name */           partition_type(sunlabel->infos[i].id));
		}
	}
}

#ifdef CONFIG_FEATURE_FDISK_ADVANCED

static void
sun_set_alt_cyl(void) {
	sunlabel->nacyl =
		SUN_SSWAP16(read_int(0,SUN_SSWAP16(sunlabel->nacyl), 65535, 0,
				 _("Number of alternate cylinders")));
}

static void
sun_set_ncyl(int cyl) {
	sunlabel->ncyl = SUN_SSWAP16(cyl);
}

static void
sun_set_xcyl(void) {
	sunlabel->sparecyl =
		SUN_SSWAP16(read_int(0, SUN_SSWAP16(sunlabel->sparecyl), sectors, 0,
				 _("Extra sectors per cylinder")));
}

static void
sun_set_ilfact(void) {
	sunlabel->ilfact =
		SUN_SSWAP16(read_int(1, SUN_SSWAP16(sunlabel->ilfact), 32, 0,
				 _("Interleave factor")));
}

static void
sun_set_rspeed(void) {
	sunlabel->rspeed =
		SUN_SSWAP16(read_int(1, SUN_SSWAP16(sunlabel->rspeed), 100000, 0,
				 _("Rotation speed (rpm)")));
}

static void
sun_set_pcylcount(void) {
	sunlabel->pcylcount =
		SUN_SSWAP16(read_int(0, SUN_SSWAP16(sunlabel->pcylcount), 65535, 0,
				 _("Number of physical cylinders")));
}
#endif /* CONFIG_FEATURE_FDISK_ADVANCED */

static void
sun_write_table(void) {
	unsigned short *ush = (unsigned short *)sunlabel;
	unsigned short csum = 0;

	while(ush < (unsigned short *)(&sunlabel->csum))
		csum ^= *ush++;
	sunlabel->csum = csum;
	if (lseek(fd, 0, SEEK_SET) < 0)
		fdisk_fatal(unable_to_seek);
	if (write(fd, sunlabel, SECTOR_SIZE) != SECTOR_SIZE)
		fdisk_fatal(unable_to_write);
}
#endif /* SUN_LABEL */

/* DOS partition types */

static const struct systypes i386_sys_types[] = {
	{"\x00" "Empty"},
	{"\x01" "FAT12"},
	{"\x04" "FAT16 <32M"},
	{"\x05" "Extended"},         /* DOS 3.3+ extended partition */
	{"\x06" "FAT16"},            /* DOS 16-bit >=32M */
	{"\x07" "HPFS/NTFS"},        /* OS/2 IFS, eg, HPFS or NTFS or QNX */
	{"\x0a" "OS/2 Boot Manager"},/* OS/2 Boot Manager */
	{"\x0b" "Win95 FAT32"},
	{"\x0c" "Win95 FAT32 (LBA)"},/* LBA really is `Extended Int 13h' */
	{"\x0e" "Win95 FAT16 (LBA)"},
	{"\x0f" "Win95 Ext'd (LBA)"},
	{"\x11" "Hidden FAT12"},
	{"\x12" "Compaq diagnostics"},
	{"\x14" "Hidden FAT16 <32M"},
	{"\x16" "Hidden FAT16"},
	{"\x17" "Hidden HPFS/NTFS"},
	{"\x1b" "Hidden Win95 FAT32"},
	{"\x1c" "Hidden Win95 FAT32 (LBA)"},
	{"\x1e" "Hidden Win95 FAT16 (LBA)"},
	{"\x3c" "PartitionMagic recovery"},
	{"\x41" "PPC PReP Boot"},
	{"\x42" "SFS"},
	{"\x63" "GNU HURD or SysV"}, /* GNU HURD or Mach or Sys V/386 (such as ISC UNIX) */
	{"\x80" "Old Minix"},        /* Minix 1.4a and earlier */
	{"\x81" "Minix / old Linux"},/* Minix 1.4b and later */
	{"\x82" "Linux swap"},       /* also Solaris */
	{"\x83" "Linux"},
	{"\x84" "OS/2 hidden C: drive"},
	{"\x85" "Linux extended"},
	{"\x86" "NTFS volume set"},
	{"\x87" "NTFS volume set"},
	{"\x8e" "Linux LVM"},
	{"\x9f" "BSD/OS"},           /* BSDI */
	{"\xa0" "IBM Thinkpad hibernation"},
	{"\xa5" "FreeBSD"},          /* various BSD flavours */
	{"\xa6" "OpenBSD"},
	{"\xa8" "Darwin UFS"},
	{"\xa9" "NetBSD"},
	{"\xab" "Darwin boot"},
	{"\xb7" "BSDI fs"},
	{"\xb8" "BSDI swap"},
	{"\xbe" "Solaris boot"},
	{"\xeb" "BeOS fs"},
	{"\xee" "EFI GPT"},          /* Intel EFI GUID Partition Table */
	{"\xef" "EFI (FAT-12/16/32)"},/* Intel EFI System Partition */
	{"\xf0" "Linux/PA-RISC boot"},/* Linux/PA-RISC boot loader */
	{"\xf2" "DOS secondary"},    /* DOS 3.3+ secondary */
	{"\xfd" "Linux raid autodetect"},/* New (2.2.x) raid partition with
					    autodetect using persistent
					    superblock */
#ifdef CONFIG_WEIRD_PARTITION_TYPES
	{"\x02" "XENIX root"},
	{"\x03" "XENIX usr"},
	{"\x08" "AIX"},              /* AIX boot (AIX -- PS/2 port) or SplitDrive */
	{"\x09" "AIX bootable"},     /* AIX data or Coherent */
	{"\x10" "OPUS"},
	{"\x18" "AST SmartSleep"},
	{"\x24" "NEC DOS"},
	{"\x39" "Plan 9"},
	{"\x40" "Venix 80286"},
	{"\x4d" "QNX4.x"},
	{"\x4e" "QNX4.x 2nd part"},
	{"\x4f" "QNX4.x 3rd part"},
	{"\x50" "OnTrack DM"},
	{"\x51" "OnTrack DM6 Aux1"}, /* (or Novell) */
	{"\x52" "CP/M"},             /* CP/M or Microport SysV/AT */
	{"\x53" "OnTrack DM6 Aux3"},
	{"\x54" "OnTrackDM6"},
	{"\x55" "EZ-Drive"},
	{"\x56" "Golden Bow"},
	{"\x5c" "Priam Edisk"},
	{"\x61" "SpeedStor"},
	{"\x64" "Novell Netware 286"},
	{"\x65" "Novell Netware 386"},
	{"\x70" "DiskSecure Multi-Boot"},
	{"\x75" "PC/IX"},
	{"\x93" "Amoeba"},
	{"\x94" "Amoeba BBT"},       /* (bad block table) */
	{"\xa7" "NeXTSTEP"},
	{"\xbb" "Boot Wizard hidden"},
	{"\xc1" "DRDOS/sec (FAT-12)"},
	{"\xc4" "DRDOS/sec (FAT-16 < 32M)"},
	{"\xc6" "DRDOS/sec (FAT-16)"},
	{"\xc7" "Syrinx"},
	{"\xda" "Non-FS data"},
	{"\xdb" "CP/M / CTOS / ..."},/* CP/M or Concurrent CP/M or
					Concurrent DOS or CTOS */
	{"\xde" "Dell Utility"},     /* Dell PowerEdge Server utilities */
	{"\xdf" "BootIt"},           /* BootIt EMBRM */
	{"\xe1" "DOS access"},       /* DOS access or SpeedStor 12-bit FAT
					extended partition */
	{"\xe3" "DOS R/O"},          /* DOS R/O or SpeedStor */
	{"\xe4" "SpeedStor"},        /* SpeedStor 16-bit FAT extended
					partition < 1024 cyl. */
	{"\xf1" "SpeedStor"},
	{"\xf4" "SpeedStor"},        /* SpeedStor large partition */
	{"\xfe" "LANstep"},          /* SpeedStor >1024 cyl. or LANstep */
	{"\xff" "BBT"},              /* Xenix Bad Block Table */
#endif
	{ 0 }
};



/* A valid partition table sector ends in 0x55 0xaa */
static unsigned int
part_table_flag(const char *b) {
	return ((uint) b[510]) + (((uint) b[511]) << 8);
}


#ifdef CONFIG_FEATURE_FDISK_WRITABLE
static void
write_part_table_flag(char *b) {
	b[510] = 0x55;
	b[511] = 0xaa;
}

/* start_sect and nr_sects are stored little endian on all machines */
/* moreover, they are not aligned correctly */
static void
store4_little_endian(unsigned char *cp, unsigned int val) {
	cp[0] = (val & 0xff);
	cp[1] = ((val >> 8) & 0xff);
	cp[2] = ((val >> 16) & 0xff);
	cp[3] = ((val >> 24) & 0xff);
}
#endif /* CONFIG_FEATURE_FDISK_WRITABLE */

static unsigned int
read4_little_endian(const unsigned char *cp) {
	return (uint)(cp[0]) + ((uint)(cp[1]) << 8)
		+ ((uint)(cp[2]) << 16) + ((uint)(cp[3]) << 24);
}

#ifdef CONFIG_FEATURE_FDISK_WRITABLE
static void
set_start_sect(struct partition *p, unsigned int start_sect) {
	store4_little_endian(p->start4, start_sect);
}
#endif

static unsigned int
get_start_sect(const struct partition *p) {
	return read4_little_endian(p->start4);
}

#ifdef CONFIG_FEATURE_FDISK_WRITABLE
static void
set_nr_sects(struct partition *p, unsigned int nr_sects) {
	store4_little_endian(p->size4, nr_sects);
}
#endif

static unsigned int
get_nr_sects(const struct partition *p) {
	return read4_little_endian(p->size4);
}

/* normally O_RDWR, -l option gives O_RDONLY */
static int type_open = O_RDWR;


static int ext_index,               /* the prime extended partition */
	listing,                    /* no aborts for fdisk -l */
	dos_compatible_flag = ~0;
#ifdef CONFIG_FEATURE_FDISK_WRITABLE
static int dos_changed;
static int nowarn;            /* no warnings for fdisk -l/-s */
#endif



static uint    user_cylinders, user_heads, user_sectors;
static uint    pt_heads, pt_sectors;
static uint    kern_heads, kern_sectors;

static uint extended_offset;            /* offset of link pointers */

static unsigned long long total_number_of_sectors;


static jmp_buf listingbuf;

static void fdisk_fatal(enum failure why) {
	const char *message;

	if (listing) {
		close(fd);
		longjmp(listingbuf, 1);
	}

	switch (why) {
		case unable_to_open:
			message = "Unable to open %s\n";
			break;
		case unable_to_read:
			message = "Unable to read %s\n";
			break;
		case unable_to_seek:
			message = "Unable to seek on %s\n";
			break;
		case unable_to_write:
			message = "Unable to write %s\n";
			break;
		case ioctl_error:
			message = "BLKGETSIZE ioctl failed on %s\n";
			break;
		default:
			message = "Fatal error\n";
	}

	fputc('\n', stderr);
	fprintf(stderr, message, disk_device);
	exit(1);
}

static void
seek_sector(uint secno) {
	off_t offset = secno * sector_size;
	if (lseek(fd, offset, SEEK_SET) == (off_t) -1)
		fdisk_fatal(unable_to_seek);
}

#ifdef CONFIG_FEATURE_FDISK_WRITABLE
static void
write_sector(uint secno, char *buf) {
	seek_sector(secno);
	if (write(fd, buf, sector_size) != sector_size)
		fdisk_fatal(unable_to_write);
}
#endif

/* Allocate a buffer and read a partition table sector */
static void
read_pte(struct pte *pe, uint offset) {

	pe->offset = offset;
	pe->sectorbuffer = (char *) xmalloc(sector_size);
	seek_sector(offset);
	if (read(fd, pe->sectorbuffer, sector_size) != sector_size)
		fdisk_fatal(unable_to_read);
#ifdef CONFIG_FEATURE_FDISK_WRITABLE
	pe->changed = 0;
#endif
	pe->part_table = pe->ext_pointer = NULL;
}

static unsigned int
get_partition_start(const struct pte *pe) {
	return pe->offset + get_start_sect(pe->part_table);
}

#ifdef CONFIG_FEATURE_FDISK_WRITABLE
/*
 * Avoid warning about DOS partitions when no DOS partition was changed.
 * Here a heuristic "is probably dos partition".
 * We might also do the opposite and warn in all cases except
 * for "is probably nondos partition".
 */
static int
is_dos_partition(int t) {
	return (t == 1 || t == 4 || t == 6 ||
		t == 0x0b || t == 0x0c || t == 0x0e ||
		t == 0x11 || t == 0x12 || t == 0x14 || t == 0x16 ||
		t == 0x1b || t == 0x1c || t == 0x1e || t == 0x24 ||
		t == 0xc1 || t == 0xc4 || t == 0xc6);
}

static void
menu(void) {
#ifdef CONFIG_FEATURE_SUN_LABEL
	if (sun_label) {
	   puts(_("Command action"));
	   puts(_("\ta\ttoggle a read only flag"));           /* sun */
	   puts(_("\tb\tedit bsd disklabel"));
	   puts(_("\tc\ttoggle the mountable flag"));         /* sun */
	   puts(_("\td\tdelete a partition"));
	   puts(_("\tl\tlist known partition types"));
	   puts(_("\tm\tprint this menu"));
	   puts(_("\tn\tadd a new partition"));
	   puts(_("\to\tcreate a new empty DOS partition table"));
	   puts(_("\tp\tprint the partition table"));
	   puts(_("\tq\tquit without saving changes"));
	   puts(_("\ts\tcreate a new empty Sun disklabel"));  /* sun */
	   puts(_("\tt\tchange a partition's system id"));
	   puts(_("\tu\tchange display/entry units"));
	   puts(_("\tv\tverify the partition table"));
	   puts(_("\tw\twrite table to disk and exit"));
#ifdef CONFIG_FEATURE_FDISK_ADVANCED
	   puts(_("\tx\textra functionality (experts only)"));
#endif
	} else
#endif
#ifdef CONFIG_FEATURE_SGI_LABEL
	if (sgi_label) {
	   puts(_("Command action"));
	   puts(_("\ta\tselect bootable partition"));    /* sgi flavour */
	   puts(_("\tb\tedit bootfile entry"));          /* sgi */
	   puts(_("\tc\tselect sgi swap partition"));    /* sgi flavour */
	   puts(_("\td\tdelete a partition"));
	   puts(_("\tl\tlist known partition types"));
	   puts(_("\tm\tprint this menu"));
	   puts(_("\tn\tadd a new partition"));
	   puts(_("\to\tcreate a new empty DOS partition table"));
	   puts(_("\tp\tprint the partition table"));
	   puts(_("\tq\tquit without saving changes"));
	   puts(_("\ts\tcreate a new empty Sun disklabel"));  /* sun */
	   puts(_("\tt\tchange a partition's system id"));
	   puts(_("\tu\tchange display/entry units"));
	   puts(_("\tv\tverify the partition table"));
	   puts(_("\tw\twrite table to disk and exit"));
	} else
#endif
#ifdef CONFIG_FEATURE_AIX_LABEL
	if (aix_label) {
	   puts(_("Command action"));
	   puts(_("\tm\tprint this menu"));
	   puts(_("\to\tcreate a new empty DOS partition table"));
	   puts(_("\tq\tquit without saving changes"));
	   puts(_("\ts\tcreate a new empty Sun disklabel"));  /* sun */
	} else
#endif
	{
	   puts(_("Command action"));
	   puts(_("\ta\ttoggle a bootable flag"));
	   puts(_("\tb\tedit bsd disklabel"));
	   puts(_("\tc\ttoggle the dos compatibility flag"));
	   puts(_("\td\tdelete a partition"));
	   puts(_("\tl\tlist known partition types"));
	   puts(_("\tm\tprint this menu"));
	   puts(_("\tn\tadd a new partition"));
	   puts(_("\to\tcreate a new empty DOS partition table"));
	   puts(_("\tp\tprint the partition table"));
	   puts(_("\tq\tquit without saving changes"));
	   puts(_("\ts\tcreate a new empty Sun disklabel"));  /* sun */
	   puts(_("\tt\tchange a partition's system id"));
	   puts(_("\tu\tchange display/entry units"));
	   puts(_("\tv\tverify the partition table"));
	   puts(_("\tw\twrite table to disk and exit"));
#ifdef CONFIG_FEATURE_FDISK_ADVANCED
	   puts(_("\tx\textra functionality (experts only)"));
#endif
	}
}
#endif /* CONFIG_FEATURE_FDISK_WRITABLE */


#ifdef CONFIG_FEATURE_FDISK_ADVANCED
static void
xmenu(void) {
#ifdef CONFIG_FEATURE_SUN_LABEL
	if (sun_label) {
	   puts(_("Command action"));
	   puts(_("\ta\tchange number of alternate cylinders"));      /*sun*/
	   puts(_("\tc\tchange number of cylinders"));
	   puts(_("\td\tprint the raw data in the partition table"));
	   puts(_("\te\tchange number of extra sectors per cylinder"));/*sun*/
	   puts(_("\th\tchange number of heads"));
	   puts(_("\ti\tchange interleave factor"));                  /*sun*/
	   puts(_("\to\tchange rotation speed (rpm)"));               /*sun*/
	   puts(_("\tm\tprint this menu"));
	   puts(_("\tp\tprint the partition table"));
	   puts(_("\tq\tquit without saving changes"));
	   puts(_("\tr\treturn to main menu"));
	   puts(_("\ts\tchange number of sectors/track"));
	   puts(_("\tv\tverify the partition table"));
	   puts(_("\tw\twrite table to disk and exit"));
	   puts(_("\ty\tchange number of physical cylinders"));       /*sun*/
	}  else
#endif
#ifdef CONFIG_FEATURE_SGI_LABEL
	if (sgi_label) {
	   puts(_("Command action"));
	   puts(_("\tb\tmove beginning of data in a partition")); /* !sun */
	   puts(_("\tc\tchange number of cylinders"));
	   puts(_("\td\tprint the raw data in the partition table"));
	   puts(_("\te\tlist extended partitions"));          /* !sun */
	   puts(_("\tg\tcreate an IRIX (SGI) partition table"));/* sgi */
	   puts(_("\th\tchange number of heads"));
	   puts(_("\tm\tprint this menu"));
	   puts(_("\tp\tprint the partition table"));
	   puts(_("\tq\tquit without saving changes"));
	   puts(_("\tr\treturn to main menu"));
	   puts(_("\ts\tchange number of sectors/track"));
	   puts(_("\tv\tverify the partition table"));
	   puts(_("\tw\twrite table to disk and exit"));
	} else
#endif
#ifdef CONFIG_FEATURE_AIX_LABEL
	if (aix_label) {
	   puts(_("Command action"));
	   puts(_("\tb\tmove beginning of data in a partition")); /* !sun */
	   puts(_("\tc\tchange number of cylinders"));
	   puts(_("\td\tprint the raw data in the partition table"));
	   puts(_("\te\tlist extended partitions"));          /* !sun */
	   puts(_("\tg\tcreate an IRIX (SGI) partition table"));/* sgi */
	   puts(_("\th\tchange number of heads"));
	   puts(_("\tm\tprint this menu"));
	   puts(_("\tp\tprint the partition table"));
	   puts(_("\tq\tquit without saving changes"));
	   puts(_("\tr\treturn to main menu"));
	   puts(_("\ts\tchange number of sectors/track"));
	   puts(_("\tv\tverify the partition table"));
	   puts(_("\tw\twrite table to disk and exit"));
	}  else
#endif
	{
	   puts(_("Command action"));
	   puts(_("\tb\tmove beginning of data in a partition")); /* !sun */
	   puts(_("\tc\tchange number of cylinders"));
	   puts(_("\td\tprint the raw data in the partition table"));
	   puts(_("\te\tlist extended partitions"));          /* !sun */
	   puts(_("\tf\tfix partition order"));               /* !sun, !aix, !sgi */
#ifdef CONFIG_FEATURE_SGI_LABEL
	   puts(_("\tg\tcreate an IRIX (SGI) partition table"));/* sgi */
#endif
	   puts(_("\th\tchange number of heads"));
	   puts(_("\tm\tprint this menu"));
	   puts(_("\tp\tprint the partition table"));
	   puts(_("\tq\tquit without saving changes"));
	   puts(_("\tr\treturn to main menu"));
	   puts(_("\ts\tchange number of sectors/track"));
	   puts(_("\tv\tverify the partition table"));
	   puts(_("\tw\twrite table to disk and exit"));
	}
}
#endif /* ADVANCED mode */

#ifdef CONFIG_FEATURE_FDISK_WRITABLE
static const struct systypes *
get_sys_types(void) {
	return (
#ifdef CONFIG_FEATURE_SUN_LABEL
		sun_label ? sun_sys_types :
#endif
#ifdef CONFIG_FEATURE_SGI_LABEL
		sgi_label ? sgi_sys_types :
#endif
		i386_sys_types);
}
#else
#define get_sys_types() i386_sys_types
#endif /* CONFIG_FEATURE_FDISK_WRITABLE */

static const char *partition_type(unsigned char type)
{
	int i;
	const struct systypes *types = get_sys_types();

	for (i=0; types[i].name; i++)
		if (types[i].name[0] == type)
			return types[i].name + 1;

	return _("Unknown");
}


#ifdef CONFIG_FEATURE_FDISK_WRITABLE
static int
get_sysid(int i) {
	return (
#ifdef CONFIG_FEATURE_SUN_LABEL
		sun_label ? sunlabel->infos[i].id :
#endif
#ifdef CONFIG_FEATURE_SGI_LABEL
		sgi_label ? sgi_get_sysid(i) :
#endif
		ptes[i].part_table->sys_ind);
}

void list_types(const struct systypes *sys)
{
	uint last[4], done = 0, next = 0, size;
	int i;

	for (i = 0; sys[i].name; i++);
	size = i;

	for (i = 3; i >= 0; i--)
		last[3 - i] = done += (size + i - done) / (i + 1);
	i = done = 0;

	do {
		printf("%c%2x  %-15.15s", i ? ' ' : '\n',
			sys[next].name[0], partition_type(sys[next].name[0]));
		next = last[i++] + done;
		if (i > 3 || next >= last[i]) {
			i = 0;
			next = ++done;
		}
	} while (done < last[0]);
	putchar('\n');
}
#endif /* CONFIG_FEATURE_FDISK_WRITABLE */

static int
is_cleared_partition(const struct partition *p) {
	return !(!p || p->boot_ind || p->head || p->sector || p->cyl ||
		 p->sys_ind || p->end_head || p->end_sector || p->end_cyl ||
		 get_start_sect(p) || get_nr_sects(p));
}

static void
clear_partition(struct partition *p) {
	if (!p)
		return;
	memset(p, 0, sizeof(struct partition));
}

#ifdef CONFIG_FEATURE_FDISK_WRITABLE
static void
set_partition(int i, int doext, uint start, uint stop, int sysid) {
	struct partition *p;
	uint offset;

	if (doext) {
		p = ptes[i].ext_pointer;
		offset = extended_offset;
	} else {
		p = ptes[i].part_table;
		offset = ptes[i].offset;
	}
	p->boot_ind = 0;
	p->sys_ind = sysid;
	set_start_sect(p, start - offset);
	set_nr_sects(p, stop - start + 1);
	if (dos_compatible_flag && (start/(sectors*heads) > 1023))
		start = heads*sectors*1024 - 1;
	set_hsc(p->head, p->sector, p->cyl, start);
	if (dos_compatible_flag && (stop/(sectors*heads) > 1023))
		stop = heads*sectors*1024 - 1;
	set_hsc(p->end_head, p->end_sector, p->end_cyl, stop);
	ptes[i].changed = 1;
}
#endif

static int
test_c(const char **m, const char *mesg) {
	int val = 0;
	if (!*m)
		fprintf(stderr, _("You must set"));
	else {
		fprintf(stderr, " %s", *m);
		val = 1;
	}
	*m = mesg;
	return val;
}

static int
warn_geometry(void) {
	const char *m = NULL;
	int prev = 0;

	if (!heads)
		prev = test_c(&m, _("heads"));
	if (!sectors)
		prev = test_c(&m, _("sectors"));
	if (!cylinders)
		prev = test_c(&m, _("cylinders"));
	if (!m)
		return 0;

	fprintf(stderr, "%s%s.\n"
#ifdef CONFIG_FEATURE_FDISK_WRITABLE
			"You can do this from the extra functions menu.\n"
#endif
		, prev ? _(" and ") : " ", m);

	return 1;
}

static void update_units(void)
{
	int cyl_units = heads * sectors;

	if (display_in_cyl_units && cyl_units)
		units_per_sector = cyl_units;
	else
		units_per_sector = 1;   /* in sectors */
}

#ifdef CONFIG_FEATURE_FDISK_WRITABLE
static void
warn_cylinders(void) {
	if (dos_label && cylinders > 1024 && !nowarn)
		fprintf(stderr, _("\n"
"The number of cylinders for this disk is set to %d.\n"
"There is nothing wrong with that, but this is larger than 1024,\n"
"and could in certain setups cause problems with:\n"
"1) software that runs at boot time (e.g., old versions of LILO)\n"
"2) booting and partitioning software from other OSs\n"
"   (e.g., DOS FDISK, OS/2 FDISK)\n"),
			cylinders);
}
#endif

static void
read_extended(int ext) {
	int i;
	struct pte *pex;
	struct partition *p, *q;

	ext_index = ext;
	pex = &ptes[ext];
	pex->ext_pointer = pex->part_table;

	p = pex->part_table;
	if (!get_start_sect(p)) {
		fprintf(stderr,
			_("Bad offset in primary extended partition\n"));
		return;
	}

	while (IS_EXTENDED (p->sys_ind)) {
		struct pte *pe = &ptes[partitions];

		if (partitions >= MAXIMUM_PARTS) {
			/* This is not a Linux restriction, but
			   this program uses arrays of size MAXIMUM_PARTS.
			   Do not try to `improve' this test. */
			struct pte *pre = &ptes[partitions-1];
#ifdef CONFIG_FEATURE_FDISK_WRITABLE
			fprintf(stderr,
				_("Warning: deleting partitions after %d\n"),
				partitions);
			pre->changed = 1;
#endif
			clear_partition(pre->ext_pointer);
			return;
		}

		read_pte(pe, extended_offset + get_start_sect(p));

		if (!extended_offset)
			extended_offset = get_start_sect(p);

		q = p = pt_offset(pe->sectorbuffer, 0);
		for (i = 0; i < 4; i++, p++) if (get_nr_sects(p)) {
			if (IS_EXTENDED (p->sys_ind)) {
				if (pe->ext_pointer)
					fprintf(stderr,
						_("Warning: extra link "
						  "pointer in partition table"
						  " %d\n"), partitions + 1);
				else
					pe->ext_pointer = p;
			} else if (p->sys_ind) {
				if (pe->part_table)
					fprintf(stderr,
						_("Warning: ignoring extra "
						  "data in partition table"
						  " %d\n"), partitions + 1);
				else
					pe->part_table = p;
			}
		}

		/* very strange code here... */
		if (!pe->part_table) {
			if (q != pe->ext_pointer)
				pe->part_table = q;
			else
				pe->part_table = q + 1;
		}
		if (!pe->ext_pointer) {
			if (q != pe->part_table)
				pe->ext_pointer = q;
			else
				pe->ext_pointer = q + 1;
		}

		p = pe->ext_pointer;
		partitions++;
	}

#ifdef CONFIG_FEATURE_FDISK_WRITABLE
	/* remove empty links */
 remove:
	for (i = 4; i < partitions; i++) {
		struct pte *pe = &ptes[i];

		if (!get_nr_sects(pe->part_table) &&
		    (partitions > 5 || ptes[4].part_table->sys_ind)) {
			printf("omitting empty partition (%d)\n", i+1);
			delete_partition(i);
			goto remove;    /* numbering changed */
		}
	}
#endif
}

#ifdef CONFIG_FEATURE_FDISK_WRITABLE
static void
create_doslabel(void) {
	int i;

	fprintf(stderr,
	_("Building a new DOS disklabel. Changes will remain in memory only,\n"
	  "until you decide to write them. After that, of course, the previous\n"
	  "content won't be recoverable.\n\n"));
#ifdef CONFIG_FEATURE_SUN_LABEL
	sun_nolabel();  /* otherwise always recognised as sun */
#endif
#ifdef CONFIG_FEATURE_SGI_LABEL
	sgi_nolabel();  /* otherwise always recognised as sgi */
#endif
#ifdef CONFIG_FEATURE_AIX_LABEL
	aix_label = 0;
#endif
#ifdef CONFIG_FEATURE_OSF_LABEL
	osf_label = 0;
	possibly_osf_label = 0;
#endif
	partitions = 4;

	for (i = 510-64; i < 510; i++)
		MBRbuffer[i] = 0;
	write_part_table_flag(MBRbuffer);
	extended_offset = 0;
	set_all_unchanged();
	set_changed(0);
	get_boot(create_empty_dos);
}
#endif /* CONFIG_FEATURE_FDISK_WRITABLE */

static void
get_sectorsize(void) {
	if (!user_set_sector_size &&
	    get_kernel_revision() >= MAKE_VERSION(2,3,3)) {
		int arg;
		if (ioctl(fd, BLKSSZGET, &arg) == 0)
			sector_size = arg;
		if (sector_size != DEFAULT_SECTOR_SIZE)
			printf(_("Note: sector size is %d (not %d)\n"),
			       sector_size, DEFAULT_SECTOR_SIZE);
	}
}

static inline void
get_kernel_geometry(void) {
	struct hd_geometry geometry;

	if (!ioctl(fd, HDIO_GETGEO, &geometry)) {
		kern_heads = geometry.heads;
		kern_sectors = geometry.sectors;
		/* never use geometry.cylinders - it is truncated */
	}
}

static void
get_partition_table_geometry(void) {
	const unsigned char *bufp = MBRbuffer;
	struct partition *p;
	int i, h, s, hh, ss;
	int first = 1;
	int bad = 0;

	if (!(valid_part_table_flag(bufp)))
		return;

	hh = ss = 0;
	for (i=0; i<4; i++) {
		p = pt_offset(bufp, i);
		if (p->sys_ind != 0) {
			h = p->end_head + 1;
			s = (p->end_sector & 077);
			if (first) {
				hh = h;
				ss = s;
				first = 0;
			} else if (hh != h || ss != s)
				bad = 1;
		}
	}

	if (!first && !bad) {
		pt_heads = hh;
		pt_sectors = ss;
	}
}

void
get_geometry(void) {
	int sec_fac;
	unsigned long long bytes;       /* really u64 */

	get_sectorsize();
	sec_fac = sector_size / 512;
#ifdef CONFIG_FEATURE_SUN_LABEL
	guess_device_type();
#endif
	heads = cylinders = sectors = 0;
	kern_heads = kern_sectors = 0;
	pt_heads = pt_sectors = 0;

	get_kernel_geometry();
	get_partition_table_geometry();

	heads = user_heads ? user_heads :
		pt_heads ? pt_heads :
		kern_heads ? kern_heads : 255;
	sectors = user_sectors ? user_sectors :
		pt_sectors ? pt_sectors :
		kern_sectors ? kern_sectors : 63;
	if (ioctl(fd, BLKGETSIZE64, &bytes) == 0) {
		/* got bytes */
	} else {
		unsigned long longsectors;

	if (ioctl(fd, BLKGETSIZE, &longsectors))
		longsectors = 0;
			bytes = ((unsigned long long) longsectors) << 9;
	}

	total_number_of_sectors = (bytes >> 9);

	sector_offset = 1;
	if (dos_compatible_flag)
		sector_offset = sectors;

	cylinders = total_number_of_sectors / (heads * sectors * sec_fac);
	if (!cylinders)
		cylinders = user_cylinders;
}

/*
 * Read MBR.  Returns:
 *   -1: no 0xaa55 flag present (possibly entire disk BSD)
 *    0: found or created label
 *    1: I/O error
 */
int
get_boot(enum action what) {
	int i;

	partitions = 4;

	for (i = 0; i < 4; i++) {
		struct pte *pe = &ptes[i];

		pe->part_table = pt_offset(MBRbuffer, i);
		pe->ext_pointer = NULL;
		pe->offset = 0;
		pe->sectorbuffer = MBRbuffer;
#ifdef CONFIG_FEATURE_FDISK_WRITABLE
		pe->changed = (what == create_empty_dos);
#endif
	}

#ifdef CONFIG_FEATURE_SUN_LABEL
	if (what == create_empty_sun && check_sun_label())
		return 0;
#endif

	memset(MBRbuffer, 0, 512);

#ifdef CONFIG_FEATURE_FDISK_WRITABLE
	if (what == create_empty_dos)
		goto got_dos_table;             /* skip reading disk */

	if ((fd = open(disk_device, type_open)) < 0) {
	    if ((fd = open(disk_device, O_RDONLY)) < 0) {
		if (what == try_only)
		    return 1;
		fdisk_fatal(unable_to_open);
	    } else
		printf(_("You will not be able to write "
			 "the partition table.\n"));
	}

	if (512 != read(fd, MBRbuffer, 512)) {
		if (what == try_only)
			return 1;
		fdisk_fatal(unable_to_read);
	}
#else
	if ((fd = open(disk_device, O_RDONLY)) < 0)
		return 1;
	if (512 != read(fd, MBRbuffer, 512))
		return 1;
#endif

	get_geometry();

	update_units();

#ifdef CONFIG_FEATURE_SUN_LABEL
	if (check_sun_label())
		return 0;
#endif

#ifdef CONFIG_FEATURE_SGI_LABEL
	if (check_sgi_label())
		return 0;
#endif

#ifdef CONFIG_FEATURE_AIX_LABEL
	if (check_aix_label())
		return 0;
#endif

#ifdef CONFIG_FEATURE_OSF_LABEL
	if (check_osf_label()) {
		possibly_osf_label = 1;
		if (!valid_part_table_flag(MBRbuffer)) {
			osf_label = 1;
			return 0;
		}
		printf(_("This disk has both DOS and BSD magic.\n"
			 "Give the 'b' command to go to BSD mode.\n"));
	}
#endif

#ifdef CONFIG_FEATURE_FDISK_WRITABLE
got_dos_table:
#endif

	if (!valid_part_table_flag(MBRbuffer)) {
#ifndef CONFIG_FEATURE_FDISK_WRITABLE
		return -1;
#else
		switch(what) {
		case fdisk:
			fprintf(stderr,
				_("Device contains neither a valid DOS "
				  "partition table, nor Sun, SGI or OSF "
				  "disklabel\n"));
#ifdef __sparc__
#ifdef CONFIG_FEATURE_SUN_LABEL
			create_sunlabel();
#endif
#else
			create_doslabel();
#endif
			return 0;
		case try_only:
			return -1;
		case create_empty_dos:
#ifdef CONFIG_FEATURE_SUN_LABEL
		case create_empty_sun:
#endif
			break;
		default:
			fprintf(stderr, _("Internal error\n"));
			exit(1);
		}
#endif /* CONFIG_FEATURE_FDISK_WRITABLE */
	}

#ifdef CONFIG_FEATURE_FDISK_WRITABLE
	warn_cylinders();
#endif
	warn_geometry();

	for (i = 0; i < 4; i++) {
		struct pte *pe = &ptes[i];

		if (IS_EXTENDED (pe->part_table->sys_ind)) {
			if (partitions != 4)
				fprintf(stderr, _("Ignoring extra extended "
					"partition %d\n"), i + 1);
			else
				read_extended(i);
		}
	}

	for (i = 3; i < partitions; i++) {
		struct pte *pe = &ptes[i];

		if (!valid_part_table_flag(pe->sectorbuffer)) {
			fprintf(stderr,
				_("Warning: invalid flag 0x%04x of partition "
				"table %d will be corrected by w(rite)\n"),
				part_table_flag(pe->sectorbuffer), i + 1);
#ifdef CONFIG_FEATURE_FDISK_WRITABLE
			pe->changed = 1;
#endif
		}
	}

	return 0;
}

#ifdef CONFIG_FEATURE_FDISK_WRITABLE
/*
 * Print the message MESG, then read an integer between LOW and HIGH (inclusive).
 * If the user hits Enter, DFLT is returned.
 * Answers like +10 are interpreted as offsets from BASE.
 *
 * There is no default if DFLT is not between LOW and HIGH.
 */
static uint
read_int(uint low, uint dflt, uint high, uint base, char *mesg)
{
	uint i;
	int default_ok = 1;
	static char *ms = NULL;
	static int mslen = 0;

	if (!ms || strlen(mesg)+100 > mslen) {
		mslen = strlen(mesg)+200;
		ms = xrealloc(ms,mslen);
	}

	if (dflt < low || dflt > high)
		default_ok = 0;

	if (default_ok)
		snprintf(ms, mslen, _("%s (%u-%u, default %u): "),
			 mesg, low, high, dflt);
	else
		snprintf(ms, mslen, "%s (%u-%u): ",
			 mesg, low, high);

	while (1) {
		int use_default = default_ok;

		/* ask question and read answer */
		while (read_chars(ms) != '\n' && !isdigit(*line_ptr)
		       && *line_ptr != '-' && *line_ptr != '+')
			continue;

	        if (*line_ptr == '+' || *line_ptr == '-') {
		       int minus = (*line_ptr == '-');
		       int absolute = 0;

		       i = atoi(line_ptr+1);

		       while (isdigit(*++line_ptr))
			       use_default = 0;
	
		       switch (*line_ptr) {
			       case 'c':
			       case 'C':
					if (!display_in_cyl_units)
						i *= heads * sectors;
					break;
			       case 'K':
					absolute = 1024;
					break;
				case 'k':
				       absolute = 1000;
				       break;
			       case 'm':
			       case 'M':
				       absolute = 1000000;
				       break;
			       case 'g':
			       case 'G':
				       absolute = 1000000000;
				       break;
			       default:
				       break;
		       }
		       if (absolute) {
			       unsigned long long bytes;
			       unsigned long unit;

			       bytes = (unsigned long long) i * absolute;
			       unit = sector_size * units_per_sector;
			       bytes += unit/2;	/* round */
			       bytes /= unit;
			       i = bytes;
			}
		       if (minus)
			       i = -i;
		       i += base;
	        } else {
			i = atoi(line_ptr);
			while (isdigit(*line_ptr)) {
				line_ptr++;
				use_default = 0;
			}
		}
		if (use_default)
			printf(_("Using default value %u\n"), i = dflt);
		if (i >= low && i <= high)
			break;
		else
			printf(_("Value out of range.\n"));
	}
	return i;
}

int
get_partition(int warn, int max) {
	struct pte *pe;
	int i;

	i = read_int(1, 0, max, 0, _("Partition number")) - 1;
	pe = &ptes[i];

	if (warn) {
		if ((!sun_label && !sgi_label && !pe->part_table->sys_ind)
#ifdef CONFIG_FEATURE_SUN_LABEL
		    || (sun_label &&
			(!sunlabel->partitions[i].num_sectors ||
			 !sunlabel->infos[i].id))
#endif
#ifdef CONFIG_FEATURE_SGI_LABEL
		    || (sgi_label && (!sgi_get_num_sectors(i)))
#endif
		   )
			fprintf(stderr,
				_("Warning: partition %d has empty type\n"),
				i+1);
	}
	return i;
}

static int
get_existing_partition(int warn, int max) {
	int pno = -1;
	int i;

	for (i = 0; i < max; i++) {
		struct pte *pe = &ptes[i];
		struct partition *p = pe->part_table;

		if (p && !is_cleared_partition(p)) {
			if (pno >= 0)
				goto not_unique;
			pno = i;
		}
	}
	if (pno >= 0) {
		printf(_("Selected partition %d\n"), pno+1);
		return pno;
	}
	printf(_("No partition is defined yet!\n"));
	return -1;

 not_unique:
	return get_partition(warn, max);
}

static int
get_nonexisting_partition(int warn, int max) {
	int pno = -1;
	int i;

	for (i = 0; i < max; i++) {
		struct pte *pe = &ptes[i];
		struct partition *p = pe->part_table;

		if (p && is_cleared_partition(p)) {
			if (pno >= 0)
				goto not_unique;
			pno = i;
		}
	}
	if (pno >= 0) {
		printf(_("Selected partition %d\n"), pno+1);
		return pno;
	}
	printf(_("All primary partitions have been defined already!\n"));
	return -1;

 not_unique:
	return get_partition(warn, max);
}


void change_units(void)
{
	display_in_cyl_units = !display_in_cyl_units;
	update_units();
	printf(_("Changing display/entry units to %s\n"),
		str_units(PLURAL));
}

static void
toggle_active(int i) {
	struct pte *pe = &ptes[i];
	struct partition *p = pe->part_table;

	if (IS_EXTENDED (p->sys_ind) && !p->boot_ind)
		fprintf(stderr,
			_("WARNING: Partition %d is an extended partition\n"),
			i + 1);
	p->boot_ind = (p->boot_ind ? 0 : ACTIVE_FLAG);
	pe->changed = 1;
}

static void
toggle_dos_compatibility_flag(void) {
	dos_compatible_flag = ~dos_compatible_flag;
	if (dos_compatible_flag) {
		sector_offset = sectors;
		printf(_("DOS Compatibility flag is set\n"));
	}
	else {
		sector_offset = 1;
		printf(_("DOS Compatibility flag is not set\n"));
	}
}

static void
delete_partition(int i) {
	struct pte *pe = &ptes[i];
	struct partition *p = pe->part_table;
	struct partition *q = pe->ext_pointer;

/* Note that for the fifth partition (i == 4) we don't actually
 * decrement partitions.
 */

	if (warn_geometry())
		return;         /* C/H/S not set */
	pe->changed = 1;

#ifdef CONFIG_FEATURE_SUN_LABEL
	if (sun_label) {
		sun_delete_partition(i);
		return;
	}
#endif
#ifdef CONFIG_FEATURE_SGI_LABEL
	if (sgi_label) {
		sgi_delete_partition(i);
		return;
	}
#endif

	if (i < 4) {
		if (IS_EXTENDED (p->sys_ind) && i == ext_index) {
			partitions = 4;
			ptes[ext_index].ext_pointer = NULL;
			extended_offset = 0;
		}
		clear_partition(p);
		return;
	}

	if (!q->sys_ind && i > 4) {
		/* the last one in the chain - just delete */
		--partitions;
		--i;
		clear_partition(ptes[i].ext_pointer);
		ptes[i].changed = 1;
	} else {
		/* not the last one - further ones will be moved down */
		if (i > 4) {
			/* delete this link in the chain */
			p = ptes[i-1].ext_pointer;
			*p = *q;
			set_start_sect(p, get_start_sect(q));
			set_nr_sects(p, get_nr_sects(q));
			ptes[i-1].changed = 1;
		} else if (partitions > 5) {    /* 5 will be moved to 4 */
			/* the first logical in a longer chain */
			pe = &ptes[5];

			if (pe->part_table) /* prevent SEGFAULT */
				set_start_sect(pe->part_table,
					       get_partition_start(pe) -
					       extended_offset);
			pe->offset = extended_offset;
			pe->changed = 1;
		}

		if (partitions > 5) {
			partitions--;
			while (i < partitions) {
				ptes[i] = ptes[i+1];
				i++;
			}
		} else
			/* the only logical: clear only */
			clear_partition(ptes[i].part_table);
	}
}

static void
change_sysid(void) {
	int i, sys, origsys;
	struct partition *p;

#ifdef CONFIG_FEATURE_SGI_LABEL
	/* If sgi_label then don't use get_existing_partition,
	   let the user select a partition, since get_existing_partition()
	   only works for Linux like partition tables. */
	if (!sgi_label) {
	i = get_existing_partition(0, partitions);
	} else {
		i = get_partition(0, partitions);
	}
#else
	i = get_existing_partition(0, partitions);
#endif
	if (i == -1)
		return;
	p = ptes[i].part_table;
	origsys = sys = get_sysid(i);

	/* if changing types T to 0 is allowed, then
	   the reverse change must be allowed, too */
	if (!sys && !sgi_label && !sun_label && !get_nr_sects(p))
		printf(_("Partition %d does not exist yet!\n"), i + 1);
	else while (1) {
		sys = read_hex (get_sys_types());

		if (!sys && !sgi_label && !sun_label) {
			printf(_("Type 0 means free space to many systems\n"
			       "(but not to Linux). Having partitions of\n"
			       "type 0 is probably unwise. You can delete\n"
			       "a partition using the `d' command.\n"));
			/* break; */
		}

		if (!sun_label && !sgi_label) {
			if (IS_EXTENDED (sys) != IS_EXTENDED (p->sys_ind)) {
				printf(_("You cannot change a partition into"
				       " an extended one or vice versa\n"
				       "Delete it first.\n"));
				break;
			}
		}

		if (sys < 256) {
#ifdef CONFIG_FEATURE_SUN_LABEL
			if (sun_label && i == 2 && sys != WHOLE_DISK)
				printf(_("Consider leaving partition 3 "
				       "as Whole disk (5),\n"
				       "as SunOS/Solaris expects it and "
				       "even Linux likes it.\n\n"));
#endif
#ifdef CONFIG_FEATURE_SGI_LABEL
			if (sgi_label && ((i == 10 && sys != ENTIRE_DISK)
					  || (i == 8 && sys != 0)))
				printf(_("Consider leaving partition 9 "
				       "as volume header (0),\nand "
				       "partition 11 as entire volume (6)"
				       "as IRIX expects it.\n\n"));
#endif
			if (sys == origsys)
				break;
#ifdef CONFIG_FEATURE_SUN_LABEL
			if (sun_label) {
				sun_change_sysid(i, sys);
			} else
#endif
#ifdef CONFIG_FEATURE_SGI_LABEL
			if (sgi_label) {
				sgi_change_sysid(i, sys);
			} else
#endif
				p->sys_ind = sys;
			printf (_("Changed system type of partition %d "
				"to %x (%s)\n"), i + 1, sys,
				partition_type(sys));
			ptes[i].changed = 1;
			if (is_dos_partition(origsys) ||
			    is_dos_partition(sys))
				dos_changed = 1;
			break;
		}
	}
}
#endif /* CONFIG_FEATURE_FDISK_WRITABLE */


/* check_consistency() and long2chs() added Sat Mar 6 12:28:16 1993,
 * faith@cs.unc.edu, based on code fragments from pfdisk by Gordon W. Ross,
 * Jan.  1990 (version 1.2.1 by Gordon W. Ross Aug. 1990; Modified by S.
 * Lubkin Oct.  1991). */

static void long2chs(ulong ls, uint *c, uint *h, uint *s) {
	int     spc = heads * sectors;

	*c = ls / spc;
	ls = ls % spc;
	*h = ls / sectors;
	*s = ls % sectors + 1;  /* sectors count from 1 */
}

static void check_consistency(const struct partition *p, int partition) {
	uint    pbc, pbh, pbs;          /* physical beginning c, h, s */
	uint    pec, peh, pes;          /* physical ending c, h, s */
	uint    lbc, lbh, lbs;          /* logical beginning c, h, s */
	uint    lec, leh, les;          /* logical ending c, h, s */

	if (!heads || !sectors || (partition >= 4))
		return;         /* do not check extended partitions */

/* physical beginning c, h, s */
	pbc = (p->cyl & 0xff) | ((p->sector << 2) & 0x300);
	pbh = p->head;
	pbs = p->sector & 0x3f;

/* physical ending c, h, s */
	pec = (p->end_cyl & 0xff) | ((p->end_sector << 2) & 0x300);
	peh = p->end_head;
	pes = p->end_sector & 0x3f;

/* compute logical beginning (c, h, s) */
	long2chs(get_start_sect(p), &lbc, &lbh, &lbs);

/* compute logical ending (c, h, s) */
	long2chs(get_start_sect(p) + get_nr_sects(p) - 1, &lec, &leh, &les);

/* Same physical / logical beginning? */
	if (cylinders <= 1024 && (pbc != lbc || pbh != lbh || pbs != lbs)) {
		printf(_("Partition %d has different physical/logical "
			"beginnings (non-Linux?):\n"), partition + 1);
		printf(_("     phys=(%d, %d, %d) "), pbc, pbh, pbs);
		printf(_("logical=(%d, %d, %d)\n"),lbc, lbh, lbs);
	}

/* Same physical / logical ending? */
	if (cylinders <= 1024 && (pec != lec || peh != leh || pes != les)) {
		printf(_("Partition %d has different physical/logical "
			"endings:\n"), partition + 1);
		printf(_("     phys=(%d, %d, %d) "), pec, peh, pes);
		printf(_("logical=(%d, %d, %d)\n"),lec, leh, les);
	}

#if 0
/* Beginning on cylinder boundary? */
	if (pbh != !pbc || pbs != 1) {
		printf(_("Partition %i does not start on cylinder "
			"boundary:\n"), partition + 1);
		printf(_("     phys=(%d, %d, %d) "), pbc, pbh, pbs);
		printf(_("should be (%d, %d, 1)\n"), pbc, !pbc);
	}
#endif

/* Ending on cylinder boundary? */
	if (peh != (heads - 1) || pes != sectors) {
	        printf(_("Partition %i does not end on cylinder boundary.\n"),
			partition + 1);
#if 0
		printf(_("     phys=(%d, %d, %d) "), pec, peh, pes);
		printf(_("should be (%d, %d, %d)\n"),
		pec, heads - 1, sectors);
#endif
	}
}

static void
list_disk_geometry(void) {
	long long bytes = (total_number_of_sectors << 9);
	long megabytes = bytes/1000000;

	if (megabytes < 10000)
		printf(_("\nDisk %s: %ld MB, %lld bytes\n"),
		       disk_device, megabytes, bytes);
	else
		printf(_("\nDisk %s: %ld.%ld GB, %lld bytes\n"),
		       disk_device, megabytes/1000, (megabytes/100)%10, bytes);
	printf(_("%d heads, %d sectors/track, %d cylinders"),
	       heads, sectors, cylinders);
	if (units_per_sector == 1)
		printf(_(", total %llu sectors"),
		       total_number_of_sectors / (sector_size/512));
	printf(_("\nUnits = %s of %d * %d = %d bytes\n\n"),
	       str_units(PLURAL),
	       units_per_sector, sector_size, units_per_sector * sector_size);
}

/*
 * Check whether partition entries are ordered by their starting positions.
 * Return 0 if OK. Return i if partition i should have been earlier.
 * Two separate checks: primary and logical partitions.
 */
static int
wrong_p_order(int *prev) {
	const struct pte *pe;
	const struct partition *p;
	uint last_p_start_pos = 0, p_start_pos;
	int i, last_i = 0;

	for (i = 0 ; i < partitions; i++) {
		if (i == 4) {
			last_i = 4;
			last_p_start_pos = 0;
		}
		pe = &ptes[i];
		if ((p = pe->part_table)->sys_ind) {
			p_start_pos = get_partition_start(pe);

			if (last_p_start_pos > p_start_pos) {
				if (prev)
					*prev = last_i;
				return i;
			}

			last_p_start_pos = p_start_pos;
			last_i = i;
		}
	}
	return 0;
}

#ifdef CONFIG_FEATURE_FDISK_ADVANCED
/*
 * Fix the chain of logicals.
 * extended_offset is unchanged, the set of sectors used is unchanged
 * The chain is sorted so that sectors increase, and so that
 * starting sectors increase.
 *
 * After this it may still be that cfdisk doesnt like the table.
 * (This is because cfdisk considers expanded parts, from link to
 * end of partition, and these may still overlap.)
 * Now
 *   sfdisk /dev/hda > ohda; sfdisk /dev/hda < ohda
 * may help.
 */
static void
fix_chain_of_logicals(void) {
	int j, oj, ojj, sj, sjj;
	struct partition *pj,*pjj,tmp;

	/* Stage 1: sort sectors but leave sector of part 4 */
	/* (Its sector is the global extended_offset.) */
 stage1:
	for (j = 5; j < partitions-1; j++) {
		oj = ptes[j].offset;
		ojj = ptes[j+1].offset;
		if (oj > ojj) {
			ptes[j].offset = ojj;
			ptes[j+1].offset = oj;
			pj = ptes[j].part_table;
			set_start_sect(pj, get_start_sect(pj)+oj-ojj);
			pjj = ptes[j+1].part_table;
			set_start_sect(pjj, get_start_sect(pjj)+ojj-oj);
			set_start_sect(ptes[j-1].ext_pointer,
				       ojj-extended_offset);
			set_start_sect(ptes[j].ext_pointer,
				       oj-extended_offset);
			goto stage1;
		}
	}

	/* Stage 2: sort starting sectors */
 stage2:
	for (j = 4; j < partitions-1; j++) {
		pj = ptes[j].part_table;
		pjj = ptes[j+1].part_table;
		sj = get_start_sect(pj);
		sjj = get_start_sect(pjj);
		oj = ptes[j].offset;
		ojj = ptes[j+1].offset;
		if (oj+sj > ojj+sjj) {
			tmp = *pj;
			*pj = *pjj;
			*pjj = tmp;
			set_start_sect(pj, ojj+sjj-oj);
			set_start_sect(pjj, oj+sj-ojj);
			goto stage2;
		}
	}

	/* Probably something was changed */
	for (j = 4; j < partitions; j++)
		ptes[j].changed = 1;
}


static void
fix_partition_table_order(void) {
	struct pte *pei, *pek;
	int i,k;

	if (!wrong_p_order(NULL)) {
		printf(_("Nothing to do. Ordering is correct already.\n\n"));
		return;
	}

	while ((i = wrong_p_order(&k)) != 0 && i < 4) {
		/* partition i should have come earlier, move it */
		/* We have to move data in the MBR */
		struct partition *pi, *pk, *pe, pbuf;
		pei = &ptes[i];
		pek = &ptes[k];

		pe = pei->ext_pointer;
		pei->ext_pointer = pek->ext_pointer;
		pek->ext_pointer = pe;

		pi = pei->part_table;
		pk = pek->part_table;

		memmove(&pbuf, pi, sizeof(struct partition));
		memmove(pi, pk, sizeof(struct partition));
		memmove(pk, &pbuf, sizeof(struct partition));

		pei->changed = pek->changed = 1;
	}

	if (i)
		fix_chain_of_logicals();

	printf("Done.\n");

}
#endif

static void
list_table(int xtra) {
	const struct partition *p;
	int i, w;

#ifdef CONFIG_FEATURE_SUN_LABEL
	if (sun_label) {
		sun_list_table(xtra);
		return;
	}
#endif

#ifdef CONFIG_FEATURE_SGI_LABEL
	if (sgi_label) {
		sgi_list_table(xtra);
		return;
	}
#endif

	list_disk_geometry();

#ifdef CONFIG_FEATURE_OSF_LABEL
	if (osf_label) {
		xbsd_print_disklabel(xtra);
		return;
	}
#endif

	/* Heuristic: we list partition 3 of /dev/foo as /dev/foo3,
	   but if the device name ends in a digit, say /dev/foo1,
	   then the partition is called /dev/foo1p3. */
	w = strlen(disk_device);
	if (w && isdigit(disk_device[w-1]))
		w++;
	if (w < 5)
		w = 5;

	printf(_("%*s Boot    Start       End    Blocks   Id  System\n"),
	       w+1, _("Device"));

	for (i = 0; i < partitions; i++) {
		const struct pte *pe = &ptes[i];

		p = pe->part_table;
		if (p && !is_cleared_partition(p)) {
			unsigned int psects = get_nr_sects(p);
			unsigned int pblocks = psects;
			unsigned int podd = 0;

			if (sector_size < 1024) {
				pblocks /= (1024 / sector_size);
				podd = psects % (1024 / sector_size);
			}
			if (sector_size > 1024)
				pblocks *= (sector_size / 1024);
			printf(
			    "%s  %c %11lu %11lu %11lu%c  %2x  %s\n",
			partname(disk_device, i+1, w+2),
/* boot flag */         !p->boot_ind ? ' ' : p->boot_ind == ACTIVE_FLAG
			? '*' : '?',
/* start */             (unsigned long) cround(get_partition_start(pe)),
/* end */               (unsigned long) cround(get_partition_start(pe) + psects
				- (psects ? 1 : 0)),
/* odd flag on end */   (unsigned long) pblocks, podd ? '+' : ' ',
/* type id */           p->sys_ind,
/* type name */         partition_type(p->sys_ind));
			check_consistency(p, i);
		}
	}

	/* Is partition table in disk order? It need not be, but... */
	/* partition table entries are not checked for correct order if this
	   is a sgi, sun or aix labeled disk... */
	if (dos_label && wrong_p_order(NULL)) {
		printf(_("\nPartition table entries are not in disk order\n"));
	}
}

#ifdef CONFIG_FEATURE_FDISK_ADVANCED
static void
x_list_table(int extend) {
	const struct pte *pe;
	const struct partition *p;
	int i;

	printf(_("\nDisk %s: %d heads, %d sectors, %d cylinders\n\n"),
		disk_device, heads, sectors, cylinders);
	printf(_("Nr AF  Hd Sec  Cyl  Hd Sec  Cyl    Start     Size ID\n"));
	for (i = 0 ; i < partitions; i++) {
		pe = &ptes[i];
		p = (extend ? pe->ext_pointer : pe->part_table);
		if (p != NULL) {
			printf("%2d %02x%4d%4d%5d%4d%4d%5d%11u%11u %02x\n",
				i + 1, p->boot_ind, p->head,
				sector(p->sector),
				cylinder(p->sector, p->cyl), p->end_head,
				sector(p->end_sector),
				cylinder(p->end_sector, p->end_cyl),
				get_start_sect(p), get_nr_sects(p), p->sys_ind);
			if (p->sys_ind)
				check_consistency(p, i);
		}
	}
}
#endif

#ifdef CONFIG_FEATURE_FDISK_WRITABLE
static void
fill_bounds(uint *first, uint *last) {
	int i;
	const struct pte *pe = &ptes[0];
	const struct partition *p;

	for (i = 0; i < partitions; pe++,i++) {
		p = pe->part_table;
		if (!p->sys_ind || IS_EXTENDED (p->sys_ind)) {
			first[i] = 0xffffffff;
			last[i] = 0;
		} else {
			first[i] = get_partition_start(pe);
			last[i] = first[i] + get_nr_sects(p) - 1;
		}
	}
}

static void
check(int n, uint h, uint s, uint c, uint start) {
	uint total, real_s, real_c;

	real_s = sector(s) - 1;
	real_c = cylinder(s, c);
	total = (real_c * sectors + real_s) * heads + h;
	if (!total)
		fprintf(stderr, _("Warning: partition %d contains sector 0\n"), n);
	if (h >= heads)
		fprintf(stderr,
			_("Partition %d: head %d greater than maximum %d\n"),
			n, h + 1, heads);
	if (real_s >= sectors)
		fprintf(stderr, _("Partition %d: sector %d greater than "
			"maximum %d\n"), n, s, sectors);
	if (real_c >= cylinders)
		fprintf(stderr, _("Partitions %d: cylinder %d greater than "
			"maximum %d\n"), n, real_c + 1, cylinders);
	if (cylinders <= 1024 && start != total)
		fprintf(stderr,
			_("Partition %d: previous sectors %d disagrees with "
			"total %d\n"), n, start, total);
}

static void
verify(void) {
	int i, j;
	uint total = 1;
	uint first[partitions], last[partitions];
	struct partition *p;

	if (warn_geometry())
		return;

#ifdef CONFIG_FEATURE_SUN_LABEL
	if (sun_label) {
		verify_sun();
		return;
	}
#endif
#ifdef CONFIG_FEATURE_SGI_LABEL
	if (sgi_label) {
		verify_sgi(1);
		return;
	}
#endif

	fill_bounds(first, last);
	for (i = 0; i < partitions; i++) {
		struct pte *pe = &ptes[i];

		p = pe->part_table;
		if (p->sys_ind && !IS_EXTENDED (p->sys_ind)) {
			check_consistency(p, i);
			if (get_partition_start(pe) < first[i])
				printf(_("Warning: bad start-of-data in "
					"partition %d\n"), i + 1);
			check(i + 1, p->end_head, p->end_sector, p->end_cyl,
				last[i]);
			total += last[i] + 1 - first[i];
			for (j = 0; j < i; j++)
			if ((first[i] >= first[j] && first[i] <= last[j])
			 || ((last[i] <= last[j] && last[i] >= first[j]))) {
				printf(_("Warning: partition %d overlaps "
					"partition %d.\n"), j + 1, i + 1);
				total += first[i] >= first[j] ?
					first[i] : first[j];
				total -= last[i] <= last[j] ?
					last[i] : last[j];
			}
		}
	}

	if (extended_offset) {
		struct pte *pex = &ptes[ext_index];
		uint e_last = get_start_sect(pex->part_table) +
			get_nr_sects(pex->part_table) - 1;

		for (i = 4; i < partitions; i++) {
			total++;
			p = ptes[i].part_table;
			if (!p->sys_ind) {
				if (i != 4 || i + 1 < partitions)
					printf(_("Warning: partition %d "
						"is empty\n"), i + 1);
			}
			else if (first[i] < extended_offset ||
					last[i] > e_last)
				printf(_("Logical partition %d not entirely in "
					"partition %d\n"), i + 1, ext_index + 1);
		}
	}

	if (total > heads * sectors * cylinders)
		printf(_("Total allocated sectors %d greater than the maximum "
			"%d\n"), total, heads * sectors * cylinders);
	else if ((total = heads * sectors * cylinders - total) != 0)
		printf(_("%d unallocated sectors\n"), total);
}

static void
add_partition(int n, int sys) {
	char mesg[256];         /* 48 does not suffice in Japanese */
	int i, readed = 0;
	struct partition *p = ptes[n].part_table;
	struct partition *q = ptes[ext_index].part_table;
	long long llimit;
	uint start, stop = 0, limit, temp,
		first[partitions], last[partitions];

	if (p && p->sys_ind) {
		printf(_("Partition %d is already defined.  Delete "
			 "it before re-adding it.\n"), n + 1);
		return;
	}
	fill_bounds(first, last);
	if (n < 4) {
		start = sector_offset;
		if (display_in_cyl_units || !total_number_of_sectors)
			llimit = heads * sectors * cylinders - 1;
		else
			llimit = total_number_of_sectors - 1;
		limit = llimit;
		if (limit != llimit)
			limit = 0x7fffffff;
		if (extended_offset) {
			first[ext_index] = extended_offset;
			last[ext_index] = get_start_sect(q) +
				get_nr_sects(q) - 1;
		}
	} else {
		start = extended_offset + sector_offset;
		limit = get_start_sect(q) + get_nr_sects(q) - 1;
	}
	if (display_in_cyl_units)
		for (i = 0; i < partitions; i++)
			first[i] = (cround(first[i]) - 1) * units_per_sector;

	snprintf(mesg, sizeof(mesg), _("First %s"), str_units(SINGULAR));
	do {
		temp = start;
		for (i = 0; i < partitions; i++) {
			int lastplusoff;

			if (start == ptes[i].offset)
				start += sector_offset;
			lastplusoff = last[i] + ((n<4) ? 0 : sector_offset);
			if (start >= first[i] && start <= lastplusoff)
				start = lastplusoff + 1;
		}
		if (start > limit)
			break;
		if (start >= temp+units_per_sector && readed) {
			printf(_("Sector %d is already allocated\n"), temp);
			temp = start;
			readed = 0;
		}
		if (!readed && start == temp) {
			uint saved_start;

			saved_start = start;
			start = read_int(cround(saved_start), cround(saved_start), cround(limit),
					 0, mesg);
			if (display_in_cyl_units) {
				start = (start - 1) * units_per_sector;
				if (start < saved_start) start = saved_start;
			}
			readed = 1;
		}
	} while (start != temp || !readed);
	if (n > 4) {                    /* NOT for fifth partition */
		struct pte *pe = &ptes[n];

		pe->offset = start - sector_offset;
		if (pe->offset == extended_offset) { /* must be corrected */
			pe->offset++;
			if (sector_offset == 1)
				start++;
		}
	}

	for (i = 0; i < partitions; i++) {
		struct pte *pe = &ptes[i];

		if (start < pe->offset && limit >= pe->offset)
			limit = pe->offset - 1;
		if (start < first[i] && limit >= first[i])
			limit = first[i] - 1;
	}
	if (start > limit) {
		printf(_("No free sectors available\n"));
		if (n > 4)
			partitions--;
		return;
	}
	if (cround(start) == cround(limit)) {
		stop = limit;
	} else {
		snprintf(mesg, sizeof(mesg),
			 _("Last %s or +size or +sizeM or +sizeK"),
			 str_units(SINGULAR));
		stop = read_int(cround(start), cround(limit), cround(limit),
				cround(start), mesg);
		if (display_in_cyl_units) {
			stop = stop * units_per_sector - 1;
			if (stop >limit)
				stop = limit;
		}
	}

	set_partition(n, 0, start, stop, sys);
	if (n > 4)
		set_partition(n - 1, 1, ptes[n].offset, stop, EXTENDED);

	if (IS_EXTENDED (sys)) {
		struct pte *pe4 = &ptes[4];
		struct pte *pen = &ptes[n];

		ext_index = n;
		pen->ext_pointer = p;
		pe4->offset = extended_offset = start;
		pe4->sectorbuffer = xcalloc(1, sector_size);
		pe4->part_table = pt_offset(pe4->sectorbuffer, 0);
		pe4->ext_pointer = pe4->part_table + 1;
		pe4->changed = 1;
		partitions = 5;
	}
}

static void
add_logical(void) {
	if (partitions > 5 || ptes[4].part_table->sys_ind) {
		struct pte *pe = &ptes[partitions];

		pe->sectorbuffer = xcalloc(1, sector_size);
		pe->part_table = pt_offset(pe->sectorbuffer, 0);
		pe->ext_pointer = pe->part_table + 1;
		pe->offset = 0;
		pe->changed = 1;
		partitions++;
	}
	add_partition(partitions - 1, LINUX_NATIVE);
}

static void
new_partition(void) {
	int i, free_primary = 0;

	if (warn_geometry())
		return;

#ifdef CONFIG_FEATURE_SUN_LABEL
	if (sun_label) {
		add_sun_partition(get_partition(0, partitions), LINUX_NATIVE);
		return;
	}
#endif
#ifdef CONFIG_FEATURE_SGI_LABEL
	if (sgi_label) {
		sgi_add_partition(get_partition(0, partitions), LINUX_NATIVE);
		return;
	}
#endif
#ifdef CONFIG_FEATURE_AIX_LABEL
	if (aix_label) {
		printf(_("\tSorry - this fdisk cannot handle AIX disk labels."
			 "\n\tIf you want to add DOS-type partitions, create"
			 "\n\ta new empty DOS partition table first. (Use o.)"
			 "\n\tWARNING: "
			 "This will destroy the present disk contents.\n"));
		return;
	}
#endif

	for (i = 0; i < 4; i++)
		free_primary += !ptes[i].part_table->sys_ind;

       if (!free_primary && partitions >= MAXIMUM_PARTS) {
	        printf(_("The maximum number of partitions has been created\n"));
	        return;
       }

	if (!free_primary) {
		if (extended_offset)
			add_logical();
		else
			printf(_("You must delete some partition and add "
				 "an extended partition first\n"));
	} else {
		char c, line[LINE_LENGTH];
		snprintf(line, sizeof(line), "%s\n   %s\n   p   primary "
						"partition (1-4)\n",
			 "Command action", (extended_offset ?
			 "l   logical (5 or over)" : "e   extended"));
		while (1) {
			if ((c = read_char(line)) == 'p' || c == 'P') {
				i = get_nonexisting_partition(0, 4);
				if (i >= 0)
					add_partition(i, LINUX_NATIVE);
				return;
			}
			else if (c == 'l' && extended_offset) {
				add_logical();
				return;
			}
			else if (c == 'e' && !extended_offset) {
				i = get_nonexisting_partition(0, 4);
				if (i >= 0)
					add_partition(i, EXTENDED);
				return;
			}
			else
				printf(_("Invalid partition number "
					 "for type `%c'\n"), c);
		}
	}
}

static void
write_table(void) {
	int i;

	if (dos_label) {
		for (i=0; i<3; i++)
			if (ptes[i].changed)
				ptes[3].changed = 1;
		for (i = 3; i < partitions; i++) {
			struct pte *pe = &ptes[i];

			if (pe->changed) {
				write_part_table_flag(pe->sectorbuffer);
				write_sector(pe->offset, pe->sectorbuffer);
			}
		}
	}
#ifdef CONFIG_FEATURE_SGI_LABEL
	else if (sgi_label) {
		/* no test on change? the printf below might be mistaken */
		sgi_write_table();
	}
#endif
#ifdef CONFIG_FEATURE_SUN_LABEL
	  else if (sun_label) {
		int needw = 0;

		for (i=0; i<8; i++)
			if (ptes[i].changed)
				needw = 1;
		if (needw)
			sun_write_table();
	}
#endif

	printf(_("The partition table has been altered!\n\n"));
	reread_partition_table(1);
}

void
reread_partition_table(int leave) {
	int error = 0;
	int i;

	printf(_("Calling ioctl() to re-read partition table.\n"));
	sync();
	sleep(2);
	if ((i = ioctl(fd, BLKRRPART)) != 0) {
		error = errno;
	} else {
		/* some kernel versions (1.2.x) seem to have trouble
		   rereading the partition table, but if asked to do it
		   twice, the second time works. - biro@yggdrasil.com */
		sync();
		sleep(2);
		if ((i = ioctl(fd, BLKRRPART)) != 0)
			error = errno;
	}

	if (i) {
		printf(_("\nWARNING: Re-reading the partition table "
			 "failed with error %d: %s.\n"
			 "The kernel still uses the old table.\n"
			 "The new table will be used "
			 "at the next reboot.\n"),
			error, strerror(error));
	}

	if (dos_changed)
	    printf(
		_("\nWARNING: If you have created or modified any DOS 6.x\n"
		"partitions, please see the fdisk manual page for additional\n"
		"information.\n"));

	if (leave) {
		close(fd);

		printf(_("Syncing disks.\n"));
		sync();
		sleep(4);               /* for sync() */
		exit(!!i);
	}
}
#endif /* CONFIG_FEATURE_FDISK_WRITABLE */

#ifdef CONFIG_FEATURE_FDISK_ADVANCED
#define MAX_PER_LINE    16
static void
print_buffer(char pbuffer[]) {
	int     i,
		l;

	for (i = 0, l = 0; i < sector_size; i++, l++) {
		if (l == 0)
			printf("0x%03X:", i);
		printf(" %02X", (unsigned char) pbuffer[i]);
		if (l == MAX_PER_LINE - 1) {
			printf("\n");
			l = -1;
		}
	}
	if (l > 0)
		printf("\n");
	printf("\n");
}


static void
print_raw(void) {
	int i;

	printf(_("Device: %s\n"), disk_device);
#if defined(CONFIG_FEATURE_SGI_LABEL) || defined(CONFIG_FEATURE_SUN_LABEL)
	if (sun_label || sgi_label)
		print_buffer(MBRbuffer);
	else
#endif
		for (i = 3; i < partitions; i++)
			print_buffer(ptes[i].sectorbuffer);
}

static void
move_begin(int i) {
	struct pte *pe = &ptes[i];
	struct partition *p = pe->part_table;
	uint new, first;

	if (warn_geometry())
		return;
	if (!p->sys_ind || !get_nr_sects(p) || IS_EXTENDED (p->sys_ind)) {
		printf(_("Partition %d has no data area\n"), i + 1);
		return;
	}
	first = get_partition_start(pe);
	new = read_int(first, first, first + get_nr_sects(p) - 1, first,
		       _("New beginning of data")) - pe->offset;

	if (new != get_nr_sects(p)) {
		first = get_nr_sects(p) + get_start_sect(p) - new;
		set_nr_sects(p, first);
		set_start_sect(p, new);
		pe->changed = 1;
	}
}

static void
xselect(void) {
	char c;

	while(1) {
		putchar('\n');
		c = tolower(read_char(_("Expert command (m for help): ")));
		switch (c) {
		case 'a':
#ifdef CONFIG_FEATURE_SUN_LABEL
			if (sun_label)
				sun_set_alt_cyl();
#endif
			break;
		case 'b':
			if (dos_label)
				move_begin(get_partition(0, partitions));
			break;
		case 'c':
			user_cylinders = cylinders =
				read_int(1, cylinders, 1048576, 0,
					 _("Number of cylinders"));
#ifdef CONFIG_FEATURE_SUN_LABEL
			if (sun_label)
				sun_set_ncyl(cylinders);
#endif
			if (dos_label)
				warn_cylinders();
			break;
		case 'd':
			print_raw();
			break;
		case 'e':
#ifdef CONFIG_FEATURE_SGI_LABEL
			if (sgi_label)
				sgi_set_xcyl();
			 else
#endif
#ifdef CONFIG_FEATURE_SUN_LABEL
			 if (sun_label)
				sun_set_xcyl();
			 else
#endif
			if (dos_label)
				x_list_table(1);
			break;
		case 'f':
			if (dos_label)
				fix_partition_table_order();
			break;
		case 'g':
#ifdef CONFIG_FEATURE_SGI_LABEL
			create_sgilabel();
#endif
			break;
		case 'h':
			user_heads = heads = read_int(1, heads, 256, 0,
					 _("Number of heads"));
			update_units();
			break;
		case 'i':
#ifdef CONFIG_FEATURE_SUN_LABEL
			if (sun_label)
				sun_set_ilfact();
#endif
			break;
		case 'o':
#ifdef CONFIG_FEATURE_SUN_LABEL
			if (sun_label)
				sun_set_rspeed();
#endif
			break;
		case 'p':
#ifdef CONFIG_FEATURE_SUN_LABEL
			if (sun_label)
				list_table(1);
			else
#endif
				x_list_table(0);
			break;
		case 'q':
			close(fd);
			printf("\n");
			exit(0);
		case 'r':
			return;
		case 's':
			user_sectors = sectors = read_int(1, sectors, 63, 0,
					   _("Number of sectors"));
			if (dos_compatible_flag) {
				sector_offset = sectors;
				fprintf(stderr, _("Warning: setting "
					"sector offset for DOS "
					"compatiblity\n"));
			}
			update_units();
			break;
		case 'v':
			verify();
			break;
		case 'w':
			write_table();  /* does not return */
			break;
		case 'y':
#ifdef CONFIG_FEATURE_SUN_LABEL
			if (sun_label)
				sun_set_pcylcount();
#endif
			break;
		default:
			xmenu();
		}
	}
}
#endif /* ADVANCED mode */

static int
is_ide_cdrom_or_tape(const char *device) {
	FILE *procf;
	char buf[100];
	struct stat statbuf;
	int is_ide = 0;

	/* No device was given explicitly, and we are trying some
	   likely things.  But opening /dev/hdc may produce errors like
	   "hdc: tray open or drive not ready"
	   if it happens to be a CD-ROM drive. It even happens that
	   the process hangs on the attempt to read a music CD.
	   So try to be careful. This only works since 2.1.73. */

	if (strncmp("/dev/hd", device, 7))
		return 0;

	snprintf(buf, sizeof(buf), "/proc/ide/%s/media", device+5);
	procf = fopen(buf, "r");
	if (procf != NULL && fgets(buf, sizeof(buf), procf))
		is_ide = (!strncmp(buf, "cdrom", 5) ||
			  !strncmp(buf, "tape", 4));
	else
		/* Now when this proc file does not exist, skip the
		   device when it is read-only. */
		if (stat(device, &statbuf) == 0)
			is_ide = ((statbuf.st_mode & 0222) == 0);

	if (procf)
		fclose(procf);
	return is_ide;
}

static void
try(const char *device, int user_specified) {
	int gb;

	disk_device = device;
	if (setjmp(listingbuf))
		return;
	if (!user_specified)
		if (is_ide_cdrom_or_tape(device))
			return;
	if ((fd = open(disk_device, type_open)) >= 0) {
		gb = get_boot(try_only);
		if (gb > 0) {   /* I/O error */
			close(fd);
		} else if (gb < 0) { /* no DOS signature */
			list_disk_geometry();
			if (aix_label)
				return;
#ifdef CONFIG_FEATURE_OSF_LABEL
			if (btrydev(device) < 0)
#endif
				fprintf(stderr,
					_("Disk %s doesn't contain a valid "
					  "partition table\n"), device);
			close(fd);
		} else {
			close(fd);
			list_table(0);
#ifdef CONFIG_FEATURE_FDISK_WRITABLE
			if (!sun_label && partitions > 4)
				delete_partition(ext_index);
#endif
		}
	} else {
		/* Ignore other errors, since we try IDE
		   and SCSI hard disks which may not be
		   installed on the system. */
		if (errno == EACCES) {
			fprintf(stderr, _("Cannot open %s\n"), device);
			return;
		}
	}
}

/* for fdisk -l: try all things in /proc/partitions
   that look like a partition name (do not end in a digit) */
static void
tryprocpt(void) {
	FILE *procpt;
	char line[100], ptname[100], devname[120], *s;
	int ma, mi, sz;

	procpt = bb_wfopen(PROC_PARTITIONS, "r");

	while (fgets(line, sizeof(line), procpt)) {
		if (sscanf (line, " %d %d %d %[^\n ]",
			    &ma, &mi, &sz, ptname) != 4)
			continue;
		for (s = ptname; *s; s++);
		if (isdigit(s[-1]))
			continue;
		sprintf(devname, "/dev/%s", ptname);
		try(devname, 0);
	}
#ifdef CONFIG_FEATURE_CLEAN_UP
	fclose(procpt);
#endif
}

#ifdef CONFIG_FEATURE_FDISK_WRITABLE
static void
unknown_command(int c) {
	printf(_("%c: unknown command\n"), c);
}
#endif

int fdisk_main(int argc, char **argv) {
	int c;
#ifdef CONFIG_FEATURE_FDISK_WRITABLE
	int optl = 0;
#endif
#ifdef CONFIG_FEATURE_FDISK_BLKSIZE
	int opts = 0;
#endif
	/*
	 * Calls:
	 *  fdisk -v
	 *  fdisk -l [-b sectorsize] [-u] device ...
	 *  fdisk -s [partition] ...
	 *  fdisk [-b sectorsize] [-u] device
	 *
	 * Options -C, -H, -S set the geometry.
	 *
	 */
	while ((c = getopt(argc, argv, "b:C:H:lS:uvV"
#ifdef CONFIG_FEATURE_FDISK_BLKSIZE
					"s"
#endif
						)) != -1) {
		switch (c) {
		case 'b':
			/* Ugly: this sector size is really per device,
			   so cannot be combined with multiple disks,
			   and te same goes for the C/H/S options.
			*/
			sector_size = atoi(optarg);
			if (sector_size != 512 && sector_size != 1024 &&
			    sector_size != 2048)
				bb_show_usage();
			sector_offset = 2;
			user_set_sector_size = 1;
			break;
		case 'C':
			user_cylinders = atoi(optarg);
			break;
		case 'H':
			user_heads = atoi(optarg);
			if (user_heads <= 0 || user_heads >= 256)
				user_heads = 0;
			break;
		case 'S':
			user_sectors = atoi(optarg);
			if (user_sectors <= 0 || user_sectors >= 64)
				user_sectors = 0;
			break;
		case 'l':
#ifdef CONFIG_FEATURE_FDISK_WRITABLE
			optl = 1;
#endif
			break;
#ifdef CONFIG_FEATURE_FDISK_BLKSIZE
		case 's':
			opts = 1;
			break;
#endif
		case 'u':
			display_in_cyl_units = 0;
			break;
		case 'V':
		case 'v':
			printf("fdisk v" UTIL_LINUX_VERSION "\n");
			return 0;
		default:
			bb_show_usage();
		}
	}

#if 0
	printf(_("This kernel finds the sector size itself - "
		 "-b option ignored\n"));
#else
	if (user_set_sector_size && argc-optind != 1)
		printf(_("Warning: the -b (set sector size) option should"
			 " be used with one specified device\n"));
#endif

#ifdef CONFIG_FEATURE_FDISK_WRITABLE
	if (optl) {
		nowarn = 1;
#endif
		type_open = O_RDONLY;
		if (argc > optind) {
			int k;
#if __GNUC__
			/* avoid gcc warning:
			   variable `k' might be clobbered by `longjmp' */
			(void)&k;
#endif
			listing = 1;
			for (k=optind; k<argc; k++)
				try(argv[k], 1);
		} else {
			/* we no longer have default device names */
			/* but, we can use /proc/partitions instead */
			tryprocpt();
		}
		return 0;
#ifdef CONFIG_FEATURE_FDISK_WRITABLE
	}
#endif

#ifdef CONFIG_FEATURE_FDISK_BLKSIZE
	if (opts) {
		long size;
		int j;

		nowarn = 1;
		type_open = O_RDONLY;

		opts = argc - optind;
		if (opts <= 0)
			bb_show_usage();

		for (j = optind; j < argc; j++) {
			disk_device = argv[j];
			if ((fd = open(disk_device, type_open)) < 0)
				fdisk_fatal(unable_to_open);
			if (ioctl(fd, BLKGETSIZE, &size))
				fdisk_fatal(ioctl_error);
			close(fd);
			if (opts == 1)
				printf("%ld\n", size/2);
			else
				printf("%s: %ld\n", argv[j], size/2);
		}
		return 0;
	}
#endif

#ifdef CONFIG_FEATURE_FDISK_WRITABLE
	if (argc-optind == 1)
		disk_device = argv[optind];
	else
		bb_show_usage();

	get_boot(fdisk);

#ifdef CONFIG_FEATURE_OSF_LABEL
	if (osf_label) {
		/* OSF label, and no DOS label */
		printf(_("Detected an OSF/1 disklabel on %s, entering "
			 "disklabel mode.\n"),
		       disk_device);
		bselect();
		osf_label = 0;
		/* If we return we may want to make an empty DOS label? */
	}
#endif

	while (1) {
		putchar('\n');
		c = tolower(read_char(_("Command (m for help): ")));
		switch (c) {
		case 'a':
			if (dos_label)
				toggle_active(get_partition(1, partitions));
#ifdef CONFIG_FEATURE_SUN_LABEL
			else if (sun_label)
				toggle_sunflags(get_partition(1, partitions),
						0x01);
#endif
#ifdef CONFIG_FEATURE_SGI_LABEL
			else if (sgi_label)
				sgi_set_bootpartition(
					get_partition(1, partitions));
#endif
			else
				unknown_command(c);
			break;
		case 'b':
#ifdef CONFIG_FEATURE_SGI_LABEL
			if (sgi_label) {
				printf(_("\nThe current boot file is: %s\n"),
				       sgi_get_bootfile());
				if (read_chars(_("Please enter the name of the "
					       "new boot file: ")) == '\n')
					printf(_("Boot file unchanged\n"));
				else
					sgi_set_bootfile(line_ptr);
			} else
#endif
#ifdef CONFIG_FEATURE_OSF_LABEL
				bselect();
#endif
			break;
		case 'c':
			if (dos_label)
				toggle_dos_compatibility_flag();
#ifdef CONFIG_FEATURE_SUN_LABEL
			else if (sun_label)
				toggle_sunflags(get_partition(1, partitions),
						0x10);
#endif
#ifdef CONFIG_FEATURE_SGI_LABEL
			else if (sgi_label)
				sgi_set_swappartition(
						get_partition(1, partitions));
#endif
			else
				unknown_command(c);
			break;
		case 'd':
			{
				int j;
#ifdef CONFIG_FEATURE_SGI_LABEL
			/* If sgi_label then don't use get_existing_partition,
			   let the user select a partition, since
			   get_existing_partition() only works for Linux-like
			   partition tables */
				if (!sgi_label) {
					j = get_existing_partition(1, partitions);
				} else {
					j = get_partition(1, partitions);
				}
#else
				j = get_existing_partition(1, partitions);
#endif
				if (j >= 0)
					delete_partition(j);
			}
			break;
		case 'i':
#ifdef CONFIG_FEATURE_SGI_LABEL
			if (sgi_label)
				create_sgiinfo();
			else
#endif
				unknown_command(c);
		case 'l':
			list_types(get_sys_types());
			break;
		case 'm':
			menu();
			break;
		case 'n':
			new_partition();
			break;
		case 'o':
			create_doslabel();
			break;
		case 'p':
			list_table(0);
			break;
		case 'q':
			close(fd);
			printf("\n");
			return 0;
		case 's':
#ifdef CONFIG_FEATURE_SUN_LABEL
			create_sunlabel();
#endif
			break;
		case 't':
			change_sysid();
			break;
		case 'u':
			change_units();
			break;
		case 'v':
			verify();
			break;
		case 'w':
			write_table();          /* does not return */
			break;
#ifdef CONFIG_FEATURE_FDISK_ADVANCED
		case 'x':
#ifdef CONFIG_FEATURE_SGI_LABEL
			if (sgi_label) {
				fprintf(stderr,
					_("\n\tSorry, no experts menu for SGI "
					"partition tables available.\n\n"));
			} else
#endif

				xselect();
			break;
#endif
		default:
			unknown_command(c);
			menu();
		}
	}
	return 0;
#endif /* CONFIG_FEATURE_FDISK_WRITABLE */
}
