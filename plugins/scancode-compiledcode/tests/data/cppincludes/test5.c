














#if TIME_WITH_SYS_TIME
# include <sys/time.h>
# include <time.h>
#else
# if HAVE_SYS_TIME_H
#  include <sys/time.h>
# else
#  include <time.h>
# endif
#endif





#include <ucd-snmp/ucd-snmp-config.h>
#include <ucd-snmp/ucd-snmp-includes.h>
#include <ucd-snmp/ucd-snmp-agent-includes.h>
#include "util_funcs.h"




#include "diskio.h"

#define CACHE_TIMEOUT 10
static time_t   cache_time = 0;

#ifdef solaris2
#include <kstat.h>

#define MAX_DISKS 128

static kstat_ctl_t *kc;
static kstat_t *ksp;
static kstat_io_t kio;
static int      cache_disknr = -1;
#endif                          

#if defined(aix4) || defined(aix5)



#include <libperfstat.h>
static perfstat_disk_t *ps_disk;	
static int ps_numdisks;			
#endif

#if defined(bsdi3) || defined(bsdi4)
#include <string.h>
#include <sys/param.h>
#include <sys/sysctl.h>
#include <sys/diskstats.h>
#endif                          

#if defined (freebsd4) || defined(freebsd5)
#include <sys/param.h>
#if __FreeBSD_version >= 500101
#include <sys/resource.h>       
#else
#include <sys/dkstat.h>
#endif
#include <devstat.h>

#include <math.h>

#define DISKIO_SAMPLE_INTERVAL 5

#endif                          

#if defined(freebsd5) && __FreeBSD_version >= 500107
  #define GETDEVS(x) devstat_getdevs(NULL, (x))
#else
  #define GETDEVS(x) getdevs((x))
#endif

#if defined (darwin)
#include <CoreFoundation/CoreFoundation.h>
#include <IOKit/IOKitLib.h>
#include <IOKit/storage/IOBlockStorageDriver.h>
#include <IOKit/storage/IOMedia.h>
#include <IOKit/IOBSD.h>

static mach_port_t masterPort;		
#endif                          

static char     type[20];
void            diskio_parse_config(const char *, char *);

#if defined (freebsd4) || defined(freebsd5)
void		devla_getstats(unsigned int regno, void *dummy);
#endif

FILE           *file;

         

















void
init_diskio(void)
{
    



    







    struct variable2 diskio_variables[] = {
        {DISKIO_INDEX, ASN_INTEGER, RONLY, var_diskio, 1, {1}},
        {DISKIO_DEVICE, ASN_OCTET_STR, RONLY, var_diskio, 1, {2}},
        {DISKIO_NREAD, ASN_COUNTER, RONLY, var_diskio, 1, {3}},
        {DISKIO_NWRITTEN, ASN_COUNTER, RONLY, var_diskio, 1, {4}},
        {DISKIO_READS, ASN_COUNTER, RONLY, var_diskio, 1, {5}},
        {DISKIO_WRITES, ASN_COUNTER, RONLY, var_diskio, 1, {6}},
	{DISKIO_LA1, ASN_INTEGER, RONLY, var_diskio, 1, {9}},
        {DISKIO_LA5, ASN_INTEGER, RONLY, var_diskio, 1, {10}},
        {DISKIO_LA15, ASN_INTEGER, RONLY, var_diskio, 1, {11}}
    };

    



    oid             diskio_variables_oid[] =
        { 1, 3, 6, 1, 4, 1, 2021, 13, 15, 1, 1 };

    










    REGISTER_MIB("diskio", diskio_variables, variable2,
                 diskio_variables_oid);

    


    snmpd_register_config_handler("diskio", diskio_parse_config,
                                  NULL, "diskio [device-type]");

#ifdef solaris2
    kc = kstat_open();

    if (kc == NULL)
        snmp_log(LOG_ERR, "diskio: Couln't open kstat\n");
#endif

#ifdef darwin
    


    IOMasterPort(bootstrap_port, &masterPort);
#endif

#if defined(aix4) || defined(aix5)
    


    ps_numdisks = 0;
    ps_disk = NULL;
#endif

#if defined (freebsd4) || defined(freebsd5)
	devla_getstats(0, NULL);
	
	snmp_alarm_register(DISKIO_SAMPLE_INTERVAL, SA_REPEAT, devla_getstats, NULL);
#endif

}

void
diskio_parse_config(const char *token, char *cptr)
{
    	
    copy_word(cptr, type);
}

#ifdef solaris2
int
get_disk(int disknr)
{
    time_t          now;
    int             i = 0;
    kstat_t *tksp;

    now = time(NULL);
    if (disknr == cache_disknr && cache_time + CACHE_TIMEOUT > now) {
        return 1;
    }

    





    for (tksp = kc->kc_chain; tksp != NULL; tksp = tksp->ks_next) {
        if (tksp->ks_type == KSTAT_TYPE_IO
            && !strcmp(tksp->ks_class, "disk")) {
            if (i == disknr) {
                if (kstat_read(kc, tksp, &kio) == -1)
                    snmp_log(LOG_ERR, "diskio: kstat_read failed\n");
		ksp = tksp;
                cache_time = now;
                cache_disknr = disknr;
                return 1;
            } else {
                i++;
            }
        }
    }
    return 0;
}


u_char         *
var_diskio(struct variable * vp,
           oid * name,
           size_t * length,
           int exact, size_t * var_len, WriteMethod ** write_method)
{
    


    static long     long_ret;

    if (header_simple_table
        (vp, name, length, exact, var_len, write_method, MAX_DISKS))
        return NULL;


    if (get_disk(name[*length - 1] - 1) == 0)
        return NULL;


    


    switch (vp->magic) {
    case DISKIO_INDEX:
        long_ret = (long) name[*length - 1];
        return (u_char *) & long_ret;
    case DISKIO_DEVICE:
        *var_len = strlen(ksp->ks_name);
        return (u_char *) ksp->ks_name;
    case DISKIO_NREAD:
        long_ret = (uint32_t) kio.nread;
        return (u_char *) & long_ret;
    case DISKIO_NWRITTEN:
        long_ret = (uint32_t) kio.nwritten;
        return (u_char *) & long_ret;
    case DISKIO_READS:
        long_ret = (uint32_t) kio.reads;
        return (u_char *) & long_ret;
    case DISKIO_WRITES:
        long_ret = (uint32_t) kio.writes;
        return (u_char *) & long_ret;

    default:
        ERROR_MSG("diskio.c: don't know how to handle this request.");
    }
    


    return NULL;
}
#endif                          

#if defined(bsdi3) || defined(bsdi4)
static int      ndisk;
static struct diskstats *dk;
static char   **dkname;

static int
getstats(void)
{
    time_t          now;
    int             mib[2];
    char           *t, *tp;
    int             size, dkn_size, i;

    now = time(NULL);
    if (cache_time + CACHE_TIMEOUT > now) {
        return 1;
    }
    mib[0] = CTL_HW;
    mib[1] = HW_DISKSTATS;
    size = 0;
    if (sysctl(mib, 2, NULL, &size, NULL, 0) < 0) {
        perror("Can't get size of HW_DISKSTATS mib");
        return 0;
    }
    if (ndisk != size / sizeof(*dk)) {
        if (dk)
            free(dk);
        if (dkname) {
            for (i = 0; i < ndisk; i++)
                if (dkname[i])
                    free(dkname[i]);
            free(dkname);
        }
        ndisk = size / sizeof(*dk);
        if (ndisk == 0)
            return 0;
        dkname = malloc(ndisk * sizeof(char *));
        mib[0] = CTL_HW;
        mib[1] = HW_DISKNAMES;
        if (sysctl(mib, 2, NULL, &dkn_size, NULL, 0) < 0) {
            perror("Can't get size of HW_DISKNAMES mib");
            return 0;
        }
        tp = t = malloc(dkn_size);
        if (sysctl(mib, 2, t, &dkn_size, NULL, 0) < 0) {
            perror("Can't get size of HW_DISKNAMES mib");
            return 0;
        }
        for (i = 0; i < ndisk; i++) {
            dkname[i] = strdup(tp);
            tp += strlen(tp) + 1;
        }
        free(t);
        dk = malloc(ndisk * sizeof(*dk));
    }
    mib[0] = CTL_HW;
    mib[1] = HW_DISKSTATS;
    if (sysctl(mib, 2, dk, &size, NULL, 0) < 0) {
        perror("Can't get HW_DISKSTATS mib");
        return 0;
    }
    cache_time = now;
    return 1;
}

u_char         *
var_diskio(struct variable * vp,
           oid * name,
           size_t * length,
           int exact, size_t * var_len, WriteMethod ** write_method)
{
    static long     long_ret;
    unsigned int    indx;

    if (getstats() == 0)
        return 0;

    if (header_simple_table
        (vp, name, length, exact, var_len, write_method, ndisk))
        return NULL;

    indx = (unsigned int) (name[*length - 1] - 1);
    if (indx >= ndisk)
        return NULL;

    switch (vp->magic) {
    case DISKIO_INDEX:
        long_ret = (long) indx + 1;
        return (u_char *) & long_ret;
    case DISKIO_DEVICE:
        *var_len = strlen(dkname[indx]);
        return (u_char *) dkname[indx];
    case DISKIO_NREAD:
        long_ret =
            (signed long) (dk[indx].dk_sectors * dk[indx].dk_secsize);
        return (u_char *) & long_ret;
    case DISKIO_NWRITTEN:
        return NULL;            
    case DISKIO_READS:
        long_ret = (signed long) dk[indx].dk_xfers;
        return (u_char *) & long_ret;
    case DISKIO_WRITES:
        return NULL;            

    default:
        ERROR_MSG("diskio.c: don't know how to handle this request.");
    }
    return NULL;
}
#endif                          

#if defined(freebsd4) || defined(freebsd5)



struct dev_la {
        struct timeval prev;
        double la1,la5,la15;
        char name[DEVSTAT_NAME_LEN+5];
        };

static struct dev_la *devloads = NULL;
static int ndevs = 0;

double devla_timeval_diff(struct timeval *t1, struct timeval *t2) {

        double dt1 = (double) t1->tv_sec + (double) t1->tv_usec * 0.000001;
        double dt2 = (double) t2->tv_sec + (double) t2->tv_usec * 0.000001;

        return dt2-dt1;

        }

void devla_getstats(unsigned int regno, void *dummy) {

        static struct statinfo *lastat = NULL;
        int i;
        double busy_time, busy_percent;
        static double expon1, expon5, expon15;
        char current_name[DEVSTAT_NAME_LEN+5];

	if (lastat == NULL) {
	    lastat = (struct statinfo *) malloc(sizeof(struct statinfo));
	    if (lastat != NULL)
		lastat->dinfo = (struct devinfo *) malloc(sizeof(struct devinfo));
	    if (lastat == NULL || lastat->dinfo == NULL) {
		    SNMP_FREE(lastat);
		    ERROR_MSG("Memory alloc failure - devla_getstats()\n");
		    return;
	    }
	}
	memset(lastat->dinfo, 0, sizeof(struct devinfo));

        if ((GETDEVS(lastat)) == -1) {
                ERROR_MSG("can't do getdevs()\n");
                return;
                }

        if (ndevs != 0) {
                for (i=0; i < ndevs; i++) {
                        snprintf(current_name, sizeof(current_name), "%s%d",
                                lastat->dinfo->devices[i].device_name, lastat->dinfo->devices[i].unit_number);
                        if (strcmp(current_name, devloads[i].name)) {
                                ndevs = 0;
                                free(devloads);
                                }
                        }
                }

        if (ndevs == 0) {
                ndevs = lastat->dinfo->numdevs;
                devloads = (struct dev_la *) malloc(ndevs * sizeof(struct dev_la));
                bzero(devloads, ndevs * sizeof(struct dev_la));
                for (i=0; i < ndevs; i++) {
                        memcpy(&devloads[i].prev, &lastat->dinfo->devices[i].busy_time, sizeof(struct timeval));
                        snprintf(devloads[i].name, sizeof(devloads[i].name), "%s%d",
                                lastat->dinfo->devices[i].device_name, lastat->dinfo->devices[i].unit_number);
                        }
                expon1  = exp(-(((double)DISKIO_SAMPLE_INTERVAL) / ((double)60)));
                expon5  = exp(-(((double)DISKIO_SAMPLE_INTERVAL) / ((double)300)));
                expon15 = exp(-(((double)DISKIO_SAMPLE_INTERVAL) / ((double)900)));
                }

        for (i=0; i<ndevs; i++) {
                busy_time = devla_timeval_diff(&devloads[i].prev, &lastat->dinfo->devices[i].busy_time);
                busy_percent = busy_time * 100 / DISKIO_SAMPLE_INTERVAL;
                devloads[i].la1 = devloads[i].la1 * expon1 + busy_percent * (1 - expon1);

                devloads[i].la5 = devloads[i].la5 * expon5 + busy_percent * (1 - expon5);
                devloads[i].la15 = devloads[i].la15 * expon15 + busy_percent * (1 - expon15);
                memcpy(&devloads[i].prev, &lastat->dinfo->devices[i].busy_time, sizeof(struct timeval));
                }

        }



static int      ndisk;
static struct statinfo *stat;
FILE           *file;

static int
getstats(void)
{
    time_t          now;
    int             i;

    now = time(NULL);
    if (cache_time + CACHE_TIMEOUT > now) {
        return 0;
    }
    if (stat == NULL) {
        stat = (struct statinfo *) malloc(sizeof(struct statinfo));
        if (stat != NULL)
            stat->dinfo = (struct devinfo *) malloc(sizeof(struct devinfo));
        if (stat == NULL || stat->dinfo == NULL) {
		SNMP_FREE(stat);
        	ERROR_MSG("Memory alloc failure - getstats\n");
		return 1;
	}
    }
    memset(stat->dinfo, 0, sizeof(struct devinfo));

    if (GETDEVS(stat) == -1) {
        fprintf(stderr, "Can't get devices:%s\n", devstat_errbuf);
        return 1;
    }
    ndisk = stat->dinfo->numdevs;
    
    for (i = 0; i < ndisk; i++) {
      char *cp = stat->dinfo->devices[i].device_name;
      int len = strlen(cp);
      if (len > DEVSTAT_NAME_LEN - 3)
        len -= 3;
      cp += len;
      sprintf(cp, "%d", stat->dinfo->devices[i].unit_number);
    }
    cache_time = now;
    return 0;
}

u_char         *
var_diskio(struct variable * vp,
           oid * name,
           size_t * length,
           int exact, size_t * var_len, WriteMethod ** write_method)
{
    static long     long_ret;
    unsigned int    indx;

    if (getstats() == 1) {
        return NULL;
    }


    if (header_simple_table
        (vp, name, length, exact, var_len, write_method, ndisk)) {
        return NULL;
    }

    indx = (unsigned int) (name[*length - 1] - 1);

    if (indx >= ndisk)
        return NULL;

    switch (vp->magic) {
    case DISKIO_INDEX:
        long_ret = (long) indx + 1;;
        return (u_char *) & long_ret;
    case DISKIO_DEVICE:
        *var_len = strlen(stat->dinfo->devices[indx].device_name);
        return (u_char *) stat->dinfo->devices[indx].device_name;
    case DISKIO_NREAD:
#if defined(freebsd5) && __FreeBSD_version >= 500107
        long_ret = (signed long) stat->dinfo->devices[indx].bytes[DEVSTAT_READ];
#else
        long_ret = (signed long) stat->dinfo->devices[indx].bytes_read;
#endif
        return (u_char *) & long_ret;
    case DISKIO_NWRITTEN:
#if defined(freebsd5) && __FreeBSD_version >= 500107
        long_ret = (signed long) stat->dinfo->devices[indx].bytes[DEVSTAT_WRITE];
#else
        long_ret = (signed long) stat->dinfo->devices[indx].bytes_written;
#endif
        return (u_char *) & long_ret;
    case DISKIO_READS:
#if defined(freebsd5) && __FreeBSD_version >= 500107
        long_ret = (signed long) stat->dinfo->devices[indx].operations[DEVSTAT_READ];
#else
        long_ret = (signed long) stat->dinfo->devices[indx].num_reads;
#endif
        return (u_char *) & long_ret;
    case DISKIO_WRITES:
#if defined(freebsd5) && __FreeBSD_version >= 500107
        long_ret = (signed long) stat->dinfo->devices[indx].operations[DEVSTAT_WRITE];
#else
        long_ret = (signed long) stat->dinfo->devices[indx].num_writes;
#endif
        return (u_char *) & long_ret;
    case DISKIO_LA1:
	long_ret = devloads[indx].la1;
	return (u_char *) & long_ret;
    case DISKIO_LA5:
        long_ret = devloads[indx].la5;
        return (u_char *) & long_ret;
    case DISKIO_LA15:
        long_ret = devloads[indx].la15;
        return (u_char *) & long_ret;

    default:
        ERROR_MSG("diskio.c: don't know how to handle this request.");
    }
    return NULL;
}
#endif                          


#ifdef linux

#define DISK_INCR 2

typedef struct linux_diskio
{
    int major;
    int  minor;
    unsigned long  blocks;
    char name[256];
    unsigned long  rio;
    unsigned long  rmerge;
    unsigned long  rsect;
    unsigned long  ruse;
    unsigned long  wio;
    unsigned long  wmerge;
    unsigned long  wsect;
    unsigned long  wuse;
    unsigned long  running;
    unsigned long  use;
    unsigned long  aveq;
} linux_diskio;

typedef struct linux_diskio_header
{
    linux_diskio* indices;
    int length;
    int alloc;
} linux_diskio_header;

static linux_diskio_header head;


int getstats(void)
{
    FILE* parts;
    time_t now;

    now = time(NULL);
    if (cache_time + CACHE_TIMEOUT > now) {
        return 0;
    }

    if (!head.indices) {
	head.alloc = DISK_INCR;
	head.indices = (linux_diskio *)malloc(head.alloc*sizeof(linux_diskio));
    }
    head.length  = 0;

    memset(head.indices, 0, head.alloc*sizeof(linux_diskio));

    
    parts = fopen("/proc/diskstats", "r");
    if (parts) {
	char buffer[1024];
	while (fgets(buffer, sizeof(buffer), parts)) {
	    linux_diskio* pTemp;
	    if (head.length == head.alloc) {
		head.alloc += DISK_INCR;
		head.indices = (linux_diskio *)realloc(head.indices, head.alloc*sizeof(linux_diskio));
	    }
	    pTemp = &head.indices[head.length];
	    sscanf (buffer, "%d %d", &pTemp->major, &pTemp->minor);
	    if (pTemp->minor == 0)
		sscanf (buffer, "%d %d %s %lu %lu %lu %lu %lu %lu %lu %lu %lu %lu %lu\n",
		    &pTemp->major, &pTemp->minor, pTemp->name,
		    &pTemp->rio, &pTemp->rmerge, &pTemp->rsect, &pTemp->ruse,
		    &pTemp->wio, &pTemp->wmerge, &pTemp->wsect, &pTemp->wuse,
		    &pTemp->running, &pTemp->use, &pTemp->aveq);
	    else
		sscanf (buffer, "%d %d %s %lu %lu %lu %lu\n",
		    &pTemp->major, &pTemp->minor, pTemp->name,
		    &pTemp->rio, &pTemp->rsect,
		    &pTemp->wio, &pTemp->wsect);
	    head.length++;
	}
	
	fclose(parts);
    }
    else {
	
	head.length = 0;	
	































    }

    cache_time = now;
    return 0;
}

u_char *
var_diskio(struct variable * vp,
	   oid * name,
	   size_t * length,
	   int exact,
	   size_t * var_len,
	   WriteMethod ** write_method)
{
    unsigned int indx;
    static unsigned long long_ret;

    if (getstats() == 1) {
	return NULL;
    }

 if (header_simple_table(vp, name, length, exact, var_len, write_method, head.length))
    {
	return NULL;
    }

  indx = (unsigned int) (name[*length - 1] - 1);

  if (indx >= head.length)
    return NULL;

  switch (vp->magic) {
    case DISKIO_INDEX:
      long_ret = indx+1;
      return (u_char *) &long_ret;
    case DISKIO_DEVICE:
      *var_len = strlen(head.indices[indx].name);
      return (u_char *) head.indices[indx].name;
    case DISKIO_NREAD:
      long_ret = head.indices[indx].rsect*512;
      return (u_char *) & long_ret;
    case DISKIO_NWRITTEN:
      long_ret = head.indices[indx].wsect*512;
      return (u_char *) & long_ret;
    case DISKIO_READS:
      long_ret = head.indices[indx].rio;
      return (u_char *) & long_ret;
    case DISKIO_WRITES:
      long_ret = head.indices[indx].wio;
      return (u_char *) & long_ret;

    default:
	snmp_log(LOG_ERR, "diskio.c: don't know how to handle %d request\n", vp->magic);
  }
  return NULL;
}
#endif  

#if defined(darwin)

#define MAXDRIVES	16	
#define MAXDRIVENAME	31	

#define kIDXBytesRead		0	
#define kIDXBytesWritten	1
#define kIDXNumReads		2
#define kIDXNumWrites		3
#define kIDXLast		3

struct drivestats {
    char name[MAXDRIVENAME + 1];
    long bsd_unit_number;
    long stats[kIDXLast+1];
};

static struct drivestats drivestat[MAXDRIVES];

static mach_port_t masterPort;		

static int num_drives;			

static int
collect_drive_stats(io_registry_entry_t driver, long *stats)
{
    CFNumberRef     number;
    CFDictionaryRef properties;
    CFDictionaryRef statistics;
    long            value;
    kern_return_t   status;
    int             i;


    



    for (i = 0; i < kIDXLast; i++) {
	stats[i] = 0;
    }

    
    status = IORegistryEntryCreateCFProperties(driver, (CFMutableDictionaryRef *)&properties,
					       kCFAllocatorDefault, kNilOptions);
    if (status != KERN_SUCCESS) {
	snmp_log(LOG_ERR, "diskio: device has no properties\n");

	return (1);
    }

    
    statistics = (CFDictionaryRef)CFDictionaryGetValue(properties,
						       CFSTR(kIOBlockStorageDriverStatisticsKey));
    if (statistics) {

	
	if ((number = (CFNumberRef)CFDictionaryGetValue(statistics,
						 CFSTR(kIOBlockStorageDriverStatisticsBytesReadKey)))) {
	    CFNumberGetValue(number, kCFNumberSInt32Type, &value);
	    stats[kIDXBytesRead] = value;
	}

	if ((number = (CFNumberRef)CFDictionaryGetValue(statistics,
						 CFSTR(kIOBlockStorageDriverStatisticsBytesWrittenKey)))) {
	    CFNumberGetValue(number, kCFNumberSInt32Type, &value);
	    stats[kIDXBytesWritten] = value;
	}

	if ((number = (CFNumberRef)CFDictionaryGetValue(statistics,
						 CFSTR(kIOBlockStorageDriverStatisticsReadsKey)))) {
	    CFNumberGetValue(number, kCFNumberSInt32Type, &value);
	    stats[kIDXNumReads] = value;
	}
	if ((number = (CFNumberRef)CFDictionaryGetValue(statistics,
						 CFSTR(kIOBlockStorageDriverStatisticsWritesKey)))) {
	    CFNumberGetValue(number, kCFNumberSInt32Type, &value);
	    stats[kIDXNumWrites] = value;
	}
    }
    
    CFRelease(properties);
    return (0);
}





static int
handle_drive(io_registry_entry_t drive, struct drivestats * dstat)
{
    io_registry_entry_t parent;
    CFDictionaryRef     properties;
    CFStringRef         name;
    CFNumberRef         number;
    kern_return_t       status;

    
    status = IORegistryEntryGetParentEntry(drive, kIOServicePlane, &parent);
    if (status != KERN_SUCCESS) {
	snmp_log(LOG_ERR, "diskio: device has no parent\n");

	return(1);
    }

    if (IOObjectConformsTo(parent, "IOBlockStorageDriver")) {

	
	status = IORegistryEntryCreateCFProperties(drive, (CFMutableDictionaryRef *)&properties,
					    kCFAllocatorDefault, kNilOptions);
	if (status != KERN_SUCCESS) {
	    snmp_log(LOG_ERR, "diskio: device has no properties\n");

	    return(1);
	}

	
	name = (CFStringRef)CFDictionaryGetValue(properties,
					  CFSTR(kIOBSDNameKey));
	number = (CFNumberRef)CFDictionaryGetValue(properties,
					    CFSTR(kIOBSDUnitKey));

	
	if (!collect_drive_stats(parent, dstat->stats)) {

	    CFStringGetCString(name, dstat->name, MAXDRIVENAME, CFStringGetSystemEncoding());
	    CFNumberGetValue(number, kCFNumberSInt32Type, &dstat->bsd_unit_number);
	    num_drives++;
	}

	
	CFRelease(properties);
	return(0);
    }

    
    IOObjectRelease(parent);
    return(1);
}

static int
getstats(void)
{
    time_t                 now;
    io_iterator_t          drivelist;
    io_registry_entry_t    drive;
    CFMutableDictionaryRef match;
    kern_return_t          status;

    now = time(NULL);	
    if (cache_time + CACHE_TIMEOUT > now) {
        return 0;
    }

    
    match = IOServiceMatching("IOMedia");
    CFDictionaryAddValue(match, CFSTR(kIOMediaWholeKey), kCFBooleanTrue);
    status = IOServiceGetMatchingServices(masterPort, match, &drivelist);
    if (status != KERN_SUCCESS) {
	snmp_log(LOG_ERR, "diskio: couldn't match whole IOMedia devices\n");

	return(1);
    }

    num_drives = 0;  
    while ((drive = IOIteratorNext(drivelist)) && (num_drives < MAXDRIVES)) {
	handle_drive(drive, &drivestat[num_drives]);
	IOObjectRelease(drive);
    }
    IOObjectRelease(drivelist);

    cache_time = now;
    return (0);
}

u_char         *
var_diskio(struct variable * vp,
           oid * name,
           size_t * length,
           int exact, size_t * var_len, WriteMethod ** write_method)
{
    static long     long_ret;
    unsigned int    indx;

    if (getstats() == 1) {
        return NULL;
    }


    if (header_simple_table
        (vp, name, length, exact, var_len, write_method, num_drives)) {
        return NULL;
    }

    indx = (unsigned int) (name[*length - 1] - 1);

    if (indx >= num_drives)
        return NULL;

    switch (vp->magic) {
	case DISKIO_INDEX:
	    long_ret = (long) drivestat[indx].bsd_unit_number;
	    return (u_char *) & long_ret;
	case DISKIO_DEVICE:
	    *var_len = strlen(drivestat[indx].name);
	    return (u_char *) drivestat[indx].name;
	case DISKIO_NREAD:
	    long_ret = (signed long) drivestat[indx].stats[kIDXBytesRead];
	    return (u_char *) & long_ret;
	case DISKIO_NWRITTEN:
	    long_ret = (signed long) drivestat[indx].stats[kIDXBytesWritten];
	    return (u_char *) & long_ret;
	case DISKIO_READS:
	    long_ret = (signed long) drivestat[indx].stats[kIDXNumReads];
	    return (u_char *) & long_ret;
	case DISKIO_WRITES:
	    long_ret = (signed long) drivestat[indx].stats[kIDXNumWrites];
	    return (u_char *) & long_ret;

	default:
	    ERROR_MSG("diskio.c: don't know how to handle this request.");
    }
    return NULL;
}
#endif                          


#if defined(aix4) || defined(aix5)



int
collect_disks(void)
{
    time_t          now;
    int             i;
    perfstat_id_t   first;

    
    now = time(NULL);
    if (ps_disk != NULL && cache_time + CACHE_TIMEOUT > now) {
        return 0;
    }

    
    i = perfstat_disk(NULL, NULL, sizeof(perfstat_disk_t), 0);
    if(i <= 0) return 1;

    
    if(i != ps_numdisks || ps_disk == NULL) {
        if(ps_disk != NULL) free(ps_disk);
        ps_numdisks = i;
        ps_disk = malloc(sizeof(perfstat_disk_t) * ps_numdisks);
        if(ps_disk == NULL) return 1;
    }

    
    strcpy(first.name, "");
    i = perfstat_disk(&first, ps_disk, sizeof(perfstat_disk_t), ps_numdisks);
    if(i != ps_numdisks) return 1;

    cache_time = now;
    return 0;
}


u_char         *
var_diskio(struct variable * vp,
           oid * name,
           size_t * length,
           int exact, size_t * var_len, WriteMethod ** write_method)
{
    static long     long_ret;
    unsigned int    indx;

    
    if (collect_disks())
        return NULL;

    if (header_simple_table
        (vp, name, length, exact, var_len, write_method, ps_numdisks))
        return NULL;

    indx = (unsigned int) (name[*length - 1] - 1);
    if (indx >= ps_numdisks)
        return NULL;

    
    switch (vp->magic) {
    case DISKIO_INDEX:
        long_ret = (long) indx;
        return (u_char *) & long_ret;
    case DISKIO_DEVICE:
        *var_len = strlen(ps_disk[indx].name);
        return (u_char *) ps_disk[indx].name;
    case DISKIO_NREAD:
        long_ret = (signed long) ps_disk[indx].rblks * ps_disk[indx].bsize;
        return (u_char *) & long_ret;
    case DISKIO_NWRITTEN:
        long_ret = (signed long) ps_disk[indx].wblks * ps_disk[indx].bsize;
        return (u_char *) & long_ret;
    case DISKIO_READS:
        long_ret = (signed long) ps_disk[indx].xfers;
        return (u_char *) & long_ret;
    case DISKIO_WRITES:
        long_ret = (signed long) 0;	
        return (u_char *) & long_ret;

    default:
        ERROR_MSG("diskio.c: don't know how to handle this request.");
    }

    
    return NULL;
}
#endif                          
