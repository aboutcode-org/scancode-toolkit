/*
 * A tiny 'top' utility.
 *
 * This is written specifically for the linux /proc/<PID>/stat(m)
 * files format.

 * This reads the PIDs of all processes and their status and shows
 * the status of processes (first ones that fit to screen) at given
 * intervals.
 *
 * NOTES:
 * - At startup this changes to /proc, all the reads are then
 *   relative to that.
 *
 * (C) Eero Tamminen <oak at welho dot com>
 *
 * Rewroted by Vladimir Oleynik (C) 2002 <dzo@simtreas.ru>
 */

/* Original code Copyrights */
/*
 * Copyright (c) 1992 Branko Lankester
 * Copyright (c) 1992 Roger Binns
 * Copyright (C) 1994-1996 Charles L. Blake.
 * Copyright (C) 1992-1998 Michael K. Johnson
 * May be distributed under the conditions of the
 * GNU Library General Public License
 */

#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/ioctl.h>
/* get page info */
#include <asm/page.h>
#include "busybox.h"

//#define FEATURE_CPU_USAGE_PERCENTAGE  /* + 2k */

#ifdef FEATURE_CPU_USAGE_PERCENTAGE
#include <time.h>
#include <sys/time.h>
#include <fcntl.h>
#include <netinet/in.h>  /* htons */
#endif


typedef int (*cmp_t)(procps_status_t *P, procps_status_t *Q);

static procps_status_t *top;   /* Hehe */
static int ntop;


static int pid_sort (procps_status_t *P, procps_status_t *Q)
{
    int p = P->pid;
    int q = Q->pid;

    if( p < q ) return -1;
    if( p > q ) return  1;
    return 0;
}

static int mem_sort (procps_status_t *P, procps_status_t *Q)
{
    long p = P->rss;
    long q = Q->rss;

    if( p > q ) return -1;
    if( p < q ) return  1;
    return 0;
}

#ifdef FEATURE_CPU_USAGE_PERCENTAGE

#define sort_depth 3
static cmp_t sort_function[sort_depth];

static int pcpu_sort (procps_status_t *P, procps_status_t *Q)
{
    int p = P->pcpu;
    int q = Q->pcpu;

    if( p > q ) return -1;
    if( p < q ) return  1;
    return 0;
}

static int time_sort (procps_status_t *P, procps_status_t *Q)
{
    long p = P->stime;
    long q = Q->stime;

    p += P->utime;
    q += Q->utime;
    if( p > q ) return -1;
    if( p < q ) return  1;
    return 0;
}

int mult_lvl_cmp(void* a, void* b) {
    int i, cmp_val;

    for(i = 0; i < sort_depth; i++) {
	cmp_val = (*sort_function[i])(a, b);
	if (cmp_val != 0)
	    return cmp_val;
    }
    return 0;
}

/* This structure stores some critical information from one frame to
   the next. mostly used for sorting. Added cumulative and resident fields. */
struct save_hist {
    int ticks;
    int pid;
    int utime;
    int stime;
};

/*
 * Calculates percent cpu usage for each task.
 */

static struct save_hist *save_history;

static unsigned long Hertz;

/***********************************************************************
 * Some values in /proc are expressed in units of 1/HZ seconds, where HZ
 * is the kernel clock tick rate. One of these units is called a jiffy.
 * The HZ value used in the kernel may vary according to hacker desire.
 * According to Linus Torvalds, this is not true. He considers the values
 * in /proc as being in architecture-dependant units that have no relation
 * to the kernel clock tick rate. Examination of the kernel source code
 * reveals that opinion as wishful thinking.
 *
 * In any case, we need the HZ constant as used in /proc. (the real HZ value
 * may differ, but we don't care) There are several ways we could get HZ:
 *
 * 1. Include the kernel header file. If it changes, recompile this library.
 * 2. Use the sysconf() function. When HZ changes, recompile the C library!
 * 3. Ask the kernel. This is obviously correct...
 *
 * Linus Torvalds won't let us ask the kernel, because he thinks we should
 * not know the HZ value. Oh well, we don't have to listen to him.
 * Someone smuggled out the HZ value. :-)
 *
 * This code should work fine, even if Linus fixes the kernel to match his
 * stated behavior. The code only fails in case of a partial conversion.
 *
 */

#define FILE_TO_BUF(filename, fd) do{                           \
    if (fd == -1 && (fd = open(filename, O_RDONLY)) == -1) {    \
	bb_perror_msg_and_die("/proc not be mounted?");            \
    }                                                           \
    lseek(fd, 0L, SEEK_SET);                                    \
    if ((local_n = read(fd, buf, sizeof buf - 1)) < 0) {        \
	bb_perror_msg_and_die("%s", filename);                     \
    }                                                           \
    buf[local_n] = '\0';                                        \
}while(0)

#define FILE_TO_BUF2(filename, fd) do{                          \
    lseek(fd, 0L, SEEK_SET);                                    \
    if ((local_n = read(fd, buf, sizeof buf - 1)) < 0) {        \
	bb_perror_msg_and_die("%s", filename);                     \
    }                                                           \
    buf[local_n] = '\0';                                        \
}while(0)

static void init_Hertz_value(void) {
  unsigned long user_j, nice_j, sys_j, other_j;  /* jiffies (clock ticks) */
  double up_1, up_2, seconds;
  unsigned long jiffies, h;
  char buf[80];
  int uptime_fd = -1;
  int stat_fd = -1;

  long smp_num_cpus = sysconf(_SC_NPROCESSORS_CONF);

  if(smp_num_cpus<1) smp_num_cpus=1;
  do {
    int local_n;

    FILE_TO_BUF("uptime", uptime_fd);
    up_1 = strtod(buf, 0);
    FILE_TO_BUF("stat", stat_fd);
    sscanf(buf, "cpu %lu %lu %lu %lu", &user_j, &nice_j, &sys_j, &other_j);
    FILE_TO_BUF2("uptime", uptime_fd);
    up_2 = strtod(buf, 0);
  } while((long)( (up_2-up_1)*1000.0/up_1 )); /* want under 0.1% error */

  close(uptime_fd);
  close(stat_fd);

  jiffies = user_j + nice_j + sys_j + other_j;
  seconds = (up_1 + up_2) / 2;
  h = (unsigned long)( (double)jiffies/seconds/smp_num_cpus );
  /* actual values used by 2.4 kernels: 32 64 100 128 1000 1024 1200 */
  switch(h){
  case   30 ...   34 :  Hertz =   32; break; /* ia64 emulator */
  case   48 ...   52 :  Hertz =   50; break;
  case   58 ...   62 :  Hertz =   60; break;
  case   63 ...   65 :  Hertz =   64; break; /* StrongARM /Shark */
  case   95 ...  105 :  Hertz =  100; break; /* normal Linux */
  case  124 ...  132 :  Hertz =  128; break; /* MIPS, ARM */
  case  195 ...  204 :  Hertz =  200; break; /* normal << 1 */
  case  253 ...  260 :  Hertz =  256; break;
  case  295 ...  304 :  Hertz =  300; break; /* 3 cpus */
  case  393 ...  408 :  Hertz =  400; break; /* normal << 2 */
  case  495 ...  504 :  Hertz =  500; break; /* 5 cpus */
  case  595 ...  604 :  Hertz =  600; break; /* 6 cpus */
  case  695 ...  704 :  Hertz =  700; break; /* 7 cpus */
  case  790 ...  808 :  Hertz =  800; break; /* normal << 3 */
  case  895 ...  904 :  Hertz =  900; break; /* 9 cpus */
  case  990 ... 1010 :  Hertz = 1000; break; /* ARM */
  case 1015 ... 1035 :  Hertz = 1024; break; /* Alpha, ia64 */
  case 1095 ... 1104 :  Hertz = 1100; break; /* 11 cpus */
  case 1180 ... 1220 :  Hertz = 1200; break; /* Alpha */
  default:
    /* If 32-bit or big-endian (not Alpha or ia64), assume HZ is 100. */
    Hertz = (sizeof(long)==sizeof(int) || htons(999)==999) ? 100UL : 1024UL;
  }
}

static void do_stats(void)
{
    struct timeval t;
    static struct timeval oldtime;
    struct timezone timez;
    float elapsed_time;

    procps_status_t *cur;
    int total_time, i, n;
    static int prev_count;
    int systime, usrtime, pid;

    struct save_hist *New_save_hist;

    /*
     * Finds the current time (in microseconds) and calculates the time
     * elapsed since the last update.
     */
    gettimeofday(&t, &timez);
    elapsed_time = (t.tv_sec - oldtime.tv_sec)
	+ (float) (t.tv_usec - oldtime.tv_usec) / 1000000.0;
    oldtime.tv_sec  = t.tv_sec;
    oldtime.tv_usec = t.tv_usec;

    New_save_hist  = alloca(sizeof(struct save_hist)*ntop);
    /*
     * Make a pass through the data to get stats.
     */
    for(n = 0; n < ntop; n++) {
	cur = top + n;

	/*
	 * Calculate time in cur process.  Time is sum of user time
	 * (usrtime) plus system time (systime).
	 */
	systime = cur->stime;
	usrtime = cur->utime;
	pid = cur->pid;
	total_time = systime + usrtime;
	New_save_hist[n].ticks = total_time;
	New_save_hist[n].pid = pid;
	New_save_hist[n].stime = systime;
	New_save_hist[n].utime = usrtime;

	/* find matching entry from previous pass */
	for (i = 0; i < prev_count; i++) {
	    if (save_history[i].pid == pid) {
		total_time -= save_history[i].ticks;
		systime -= save_history[i].stime;
		usrtime -= save_history[i].utime;
		break;
	    }
	}

	/*
	 * Calculate percent cpu time for cur task.
	 */
	i = (total_time * 10 * 100/Hertz) / elapsed_time;
	if (i > 999)
	    i = 999;
	cur->pcpu = i;

    }

    /*
     * Save cur frame's information.
     */
    free(save_history);
    save_history = memcpy(xmalloc(sizeof(struct save_hist)*n), New_save_hist,
						sizeof(struct save_hist)*n);
    prev_count = n;
    qsort(top, n, sizeof(procps_status_t), (void*)mult_lvl_cmp);
}
#else
static cmp_t sort_function;
#endif /* FEATURE_CPU_USAGE_PERCENTAGE */

/* display generic info (meminfo / loadavg) */
static unsigned long display_generic(void)
{
	FILE *fp;
	char buf[80];
	float avg1, avg2, avg3;
	unsigned long total, used, mfree, shared, buffers, cached;
	unsigned int needs_conversion = 1;

	/* read memory info */
	fp = bb_xfopen("meminfo", "r");

	/*
	 * Old kernels (such as 2.4.x) had a nice summary of memory info that
	 * we could parse, however this is gone entirely in 2.6. Try parsing
	 * the old way first, and if that fails, parse each field manually.
	 *
	 * First, we read in the first line. Old kernels will have bogus
	 * strings we don't care about, whereas new kernels will start right
	 * out with MemTotal:
	 * 				-- PFM.
	 */
	if (fscanf(fp, "MemTotal: %lu %s\n", &total, buf) != 2) {
		fgets(buf, sizeof(buf), fp);	/* skip first line */

		fscanf(fp, "Mem: %lu %lu %lu %lu %lu %lu",
		   &total, &used, &mfree, &shared, &buffers, &cached);
	} else {
		/*
		 * Revert to manual parsing, which incidentally already has the
		 * sizes in kilobytes. This should be safe for both 2.4 and
		 * 2.6.
		 */
		needs_conversion = 0;

		fscanf(fp, "MemFree: %lu %s\n", &mfree, buf);

		/*
		 * MemShared: is no longer present in 2.6. Report this as 0,
		 * to maintain consistent behavior with normal procps.
		 */
		if (fscanf(fp, "MemShared: %lu %s\n", &shared, buf) != 2)
			shared = 0;

		fscanf(fp, "Buffers: %lu %s\n", &buffers, buf);
		fscanf(fp, "Cached: %lu %s\n", &cached, buf);

		used = total - mfree;
	}
	fclose(fp);

	/* read load average */
	fp = bb_xfopen("loadavg", "r");
	if (fscanf(fp, "%f %f %f", &avg1, &avg2, &avg3) != 3) {
		bb_error_msg_and_die("failed to read '%s'", "loadavg");
	}
	fclose(fp);

	if (needs_conversion) {
		/* convert to kilobytes */
		used /= 1024;
		mfree /= 1024;
		shared /= 1024;
		buffers /= 1024;
		cached /= 1024;
		total /= 1024;
	}

	/* output memory info and load average */
	/* clear screen & go to top */
	printf("\e[H\e[J" "Mem: "
	       "%ldK used, %ldK free, %ldK shrd, %ldK buff, %ldK cached\n",
	       used, mfree, shared, buffers, cached);
	printf("Load average: %.2f, %.2f, %.2f    "
			"(State: S=sleeping R=running, W=waiting)\n",
	       avg1, avg2, avg3);
	return total;
}


/* display process statuses */
static void display_status(int count, int col)
{
	procps_status_t *s = top;
	char rss_str_buf[8];
	unsigned long total_memory = display_generic();

#ifdef FEATURE_CPU_USAGE_PERCENTAGE
	/* what info of the processes is shown */
	printf("\n\e[7m  PID USER     STATUS   RSS  PPID %%CPU %%MEM COMMAND\e[0m\n");
#else
	printf("\n\e[7m  PID USER     STATUS   RSS  PPID %%MEM COMMAND\e[0m\n");
#endif

	while (count--) {
		char *namecmd = s->short_cmd;
		int pmem;

		pmem = 1000.0 * s->rss / total_memory;
		if (pmem > 999) pmem = 999;

		if(s->rss > 10*1024)
			sprintf(rss_str_buf, "%6ldM", s->rss/1024);
		else
			sprintf(rss_str_buf, "%7ld", s->rss);
#ifdef FEATURE_CPU_USAGE_PERCENTAGE
		printf("%5d %-8s %s  %s %5d %2d.%d %2u.%u ",
			s->pid, s->user, s->state, rss_str_buf, s->ppid,
			s->pcpu/10, s->pcpu%10, pmem/10, pmem%10);
#else
		printf("%5d %-8s %s  %s %5d %2u.%u ",
			s->pid, s->user, s->state, rss_str_buf, s->ppid,
			pmem/10, pmem%10);
#endif
			if(strlen(namecmd) > col)
				namecmd[col] = 0;
			printf("%s\n", namecmd);
		s++;
	}
}

static void clearmems(void)
{
	free(top);
	top = 0;
	ntop = 0;
}

#if defined CONFIG_FEATURE_USE_TERMIOS
#include <termios.h>
#include <sys/time.h>
#include <signal.h>


static struct termios initial_settings;

static void reset_term(void)
{
	tcsetattr(0, TCSANOW, (void *) &initial_settings);
#ifdef CONFIG_FEATURE_CLEAN_UP
	clearmems();
#ifdef FEATURE_CPU_USAGE_PERCENTAGE
	free(save_history);
#endif
#endif /* CONFIG_FEATURE_CLEAN_UP */
}

static void sig_catcher (int sig)
{
	reset_term();
}
#endif /* CONFIG_FEATURE_USE_TERMIOS */


int top_main(int argc, char **argv)
{
	int opt, interval, lines, col;
#if defined CONFIG_FEATURE_USE_TERMIOS
	struct termios new_settings;
	struct timeval tv;
	fd_set readfds;
	unsigned char c;
	struct sigaction sa;
#endif /* CONFIG_FEATURE_USE_TERMIOS */

	/* Default update rate is 5 seconds */
	interval = 5;

	/* do normal option parsing */
	while ((opt = getopt(argc, argv, "d:")) > 0) {
	    switch (opt) {
		case 'd':
		    interval = atoi(optarg);
		    break;
		default:
		    bb_show_usage();
	    }
	}

	/* Default to 25 lines - 5 lines for status */
	lines = 25 - 5;
	/* Default CMD format size */
#ifdef FEATURE_CPU_USAGE_PERCENTAGE
	col = 35 - 6;
#else
	col = 35;
#endif
	/* change to /proc */
	if (chdir("/proc") < 0) {
		bb_perror_msg_and_die("chdir('/proc')");
	}
#if defined CONFIG_FEATURE_USE_TERMIOS
	tcgetattr(0, (void *) &initial_settings);
	memcpy(&new_settings, &initial_settings, sizeof(struct termios));
	new_settings.c_lflag &= ~(ISIG | ICANON); /* unbuffered input */
	/* Turn off echoing */
	new_settings.c_lflag &= ~(ECHO | ECHONL);

	signal (SIGTERM, sig_catcher);
	sigaction (SIGTERM, (struct sigaction *) 0, &sa);
	sa.sa_flags |= SA_RESTART;
	sa.sa_flags &= ~SA_INTERRUPT;
	sigaction (SIGTERM, &sa, (struct sigaction *) 0);
	sigaction (SIGINT, &sa, (struct sigaction *) 0);
	tcsetattr(0, TCSANOW, (void *) &new_settings);
	atexit(reset_term);

	get_terminal_width_height(0, &col, &lines);
	if (lines > 4) {
	    lines -= 5;
#ifdef FEATURE_CPU_USAGE_PERCENTAGE
	    col = col - 80 + 35 - 6;
#else
	    col = col - 80 + 35;
#endif
	}
#endif /* CONFIG_FEATURE_USE_TERMIOS */
#ifdef FEATURE_CPU_USAGE_PERCENTAGE
	sort_function[0] = pcpu_sort;
	sort_function[1] = mem_sort;
	sort_function[2] = time_sort;
#else
	sort_function = mem_sort;
#endif
	while (1) {
		/* read process IDs & status for all the processes */
		procps_status_t * p;

#ifdef CONFIG_SELINUX
		while ((p = procps_scan(0, 0, NULL) ) != 0) {
#else
		while ((p = procps_scan(0)) != 0) {
#endif
			int n = ntop;

			top = xrealloc(top, (++ntop)*sizeof(procps_status_t));
			memcpy(top + n, p, sizeof(procps_status_t));
		}
		if (ntop == 0) {
		bb_perror_msg_and_die("scandir('/proc')");
	}
#ifdef FEATURE_CPU_USAGE_PERCENTAGE
		if(!Hertz) {
			init_Hertz_value();
			do_stats();
			sleep(1);
			clearmems();
			continue;
	}
		do_stats();
#else
		qsort(top, ntop, sizeof(procps_status_t), (void*)sort_function);
#endif
		opt = lines;
		if (opt > ntop) {
			opt = ntop;
		}
		/* show status for each of the processes */
		display_status(opt, col);
#if defined CONFIG_FEATURE_USE_TERMIOS
		tv.tv_sec = interval;
		tv.tv_usec = 0;
		FD_ZERO (&readfds);
		FD_SET (0, &readfds);
		select (1, &readfds, NULL, NULL, &tv);
		if (FD_ISSET (0, &readfds)) {
			if (read (0, &c, 1) <= 0) {   /* signal */
		return EXIT_FAILURE;
	}
			if(c == 'q' || c == initial_settings.c_cc[VINTR])
				return EXIT_SUCCESS;
			if(c == 'M') {
#ifdef FEATURE_CPU_USAGE_PERCENTAGE
				sort_function[0] = mem_sort;
				sort_function[1] = pcpu_sort;
				sort_function[2] = time_sort;
#else
				sort_function = mem_sort;
#endif
			}
#ifdef FEATURE_CPU_USAGE_PERCENTAGE
			if(c == 'P') {
				sort_function[0] = pcpu_sort;
				sort_function[1] = mem_sort;
				sort_function[2] = time_sort;
			}
			if(c == 'T') {
				sort_function[0] = time_sort;
				sort_function[1] = mem_sort;
				sort_function[2] = pcpu_sort;
			}
#endif
			if(c == 'N') {
#ifdef FEATURE_CPU_USAGE_PERCENTAGE
				sort_function[0] = pid_sort;
#else
				sort_function = pid_sort;
#endif
			}
		}
#else
		sleep(interval);
#endif                                  /* CONFIG_FEATURE_USE_TERMIOS */
		clearmems();
	}

	return EXIT_SUCCESS;
}
