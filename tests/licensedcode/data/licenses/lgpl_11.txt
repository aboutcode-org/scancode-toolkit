/* vi: set sw=4 ts=4: */
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
 * Rewritten by Vladimir Oleynik (C) 2002 <dzo@simtreas.ru>
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

#include "busybox.h"
#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/ioctl.h>

//#define CONFIG_FEATURE_TOP_CPU_USAGE_PERCENTAGE  /* + 2k */

#ifdef CONFIG_FEATURE_TOP_CPU_USAGE_PERCENTAGE
#include <time.h>
#include <fcntl.h>
#include <netinet/in.h>  /* htons */
#endif


typedef int (*cmp_t)(procps_status_t *P, procps_status_t *Q);

static procps_status_t *top;   /* Hehe */
static int ntop;

#ifdef CONFIG_FEATURE_USE_TERMIOS
static int pid_sort(procps_status_t *P, procps_status_t *Q)
{
	return (Q->pid - P->pid);
}
#endif

static int mem_sort(procps_status_t *P, procps_status_t *Q)
{
	return (int)(Q->rss - P->rss);
}

#ifdef CONFIG_FEATURE_TOP_CPU_USAGE_PERCENTAGE

#define sort_depth 3
static cmp_t sort_function[sort_depth];

static int pcpu_sort(procps_status_t *P, procps_status_t *Q)
{
	return (Q->pcpu - P->pcpu);
}

static int time_sort(procps_status_t *P, procps_status_t *Q)
{
	return (int)((Q->stime + Q->utime) - (P->stime + P->utime));
}

static int mult_lvl_cmp(void* a, void* b) {
	int i, cmp_val;

	for (i = 0; i < sort_depth; i++) {
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
};

/*
 * Calculates percent cpu usage for each task.
 */

static struct save_hist *prev_hist;
static int prev_hist_count;
/* static int hist_iterations; */


static unsigned total_pcpu;
/* static unsigned long total_rss; */

struct jiffy_counts {
	unsigned long long usr,nic,sys,idle,iowait,irq,softirq,steal;
	unsigned long long total;
	unsigned long long busy;
};
static struct jiffy_counts jif, prev_jif;

static void get_jiffy_counts(void)
{
	FILE* fp = bb_xfopen("stat", "r");
	prev_jif = jif;
	if (fscanf(fp, "cpu  %lld %lld %lld %lld %lld %lld %lld %lld",
			&jif.usr,&jif.nic,&jif.sys,&jif.idle,
			&jif.iowait,&jif.irq,&jif.softirq,&jif.steal) < 4) {
		bb_error_msg_and_die("failed to read 'stat'");
	}
	fclose(fp);
	jif.total = jif.usr + jif.nic + jif.sys + jif.idle
			+ jif.iowait + jif.irq + jif.softirq + jif.steal;
	/* procps 2.x does not count iowait as busy time */
	jif.busy = jif.total - jif.idle - jif.iowait;
}

static void do_stats(void)
{
	procps_status_t *cur;
	int pid, total_time, i, last_i, n;
	struct save_hist *new_hist;

	get_jiffy_counts();
	total_pcpu = 0;
	/* total_rss = 0; */
	new_hist = xmalloc(sizeof(struct save_hist)*ntop);
	/*
	 * Make a pass through the data to get stats.
	 */
	/* hist_iterations = 0; */
	i = 0;
	for (n = 0; n < ntop; n++) {
		cur = top + n;

		/*
		 * Calculate time in cur process.  Time is sum of user time
		 * and system time
		 */
		pid = cur->pid;
		total_time = cur->stime + cur->utime;
		new_hist[n].ticks = total_time;
		new_hist[n].pid = pid;

		/* find matching entry from previous pass */
		cur->pcpu = 0;
		/* do not start at index 0, continue at last used one
		 * (brought hist_iterations from ~14000 down to 172) */
		last_i = i;
		if (prev_hist_count) do {
			if (prev_hist[i].pid == pid) {
				cur->pcpu = total_time - prev_hist[i].ticks;
				break;
			}
			i = (i+1) % prev_hist_count;
			/* hist_iterations++; */
		} while (i != last_i);
		total_pcpu += cur->pcpu;
		/* total_rss += cur->rss; */
	}

	/*
	 * Save cur frame's information.
	 */
	free(prev_hist);
	prev_hist = new_hist;
	prev_hist_count = ntop;
}
#else
static cmp_t sort_function;
#endif /* CONFIG_FEATURE_TOP_CPU_USAGE_PERCENTAGE */

/* display generic info (meminfo / loadavg) */
static unsigned long display_generic(int scr_width)
{
	FILE *fp;
	char buf[80];
	char scrbuf[80];
	char *end;
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
	 *                              -- PFM.
	 */
	if (fscanf(fp, "MemTotal: %lu %s\n", &total, buf) != 2) {
		fgets(buf, sizeof(buf), fp);    /* skip first line */

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

	/* read load average as a string */
	fp = bb_xfopen("loadavg", "r");
	buf[0] = '\0';
	fgets(buf, sizeof(buf), fp);
	end = strchr(buf, ' ');
	if (end) end = strchr(end+1, ' ');
	if (end) end = strchr(end+1, ' ');
	if (end) *end = '\0';
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
	if (scr_width > sizeof(scrbuf))
		scr_width = sizeof(scrbuf);
	snprintf(scrbuf, scr_width,
		"Mem: %ldK used, %ldK free, %ldK shrd, %ldK buff, %ldK cached",
		used, mfree, shared, buffers, cached);
	printf("\e[H\e[J%s\n", scrbuf);
	snprintf(scrbuf, scr_width,
		"Load average: %s  (Status: S=sleeping R=running, W=waiting)", buf);
	printf("%s\n", scrbuf);

	return total;
}


/* display process statuses */
static void display_status(int count, int scr_width)
{
	enum {
		bits_per_int = sizeof(int)*8
	};

	procps_status_t *s = top;
	char rss_str_buf[8];
	unsigned long total_memory = display_generic(scr_width); /* or use total_rss? */
	unsigned pmem_shift, pmem_scale;

#ifdef CONFIG_FEATURE_TOP_CPU_USAGE_PERCENTAGE
	unsigned pcpu_shift, pcpu_scale;

	/* what info of the processes is shown */
	printf("\e[7m%.*s\e[0m", scr_width,
		"  PID USER     STATUS   RSS  PPID %CPU %MEM COMMAND");
#define MIN_WIDTH \
	sizeof( "  PID USER     STATUS   RSS  PPID %CPU %MEM C")
#else
	printf("\e[7m%.*s\e[0m", scr_width,
		"  PID USER     STATUS   RSS  PPID %MEM COMMAND");
#define MIN_WIDTH \
	sizeof( "  PID USER     STATUS   RSS  PPID %MEM C")
#endif

	/*
	 * MEM% = s->rss/MemTotal
	 */
	pmem_shift = bits_per_int-11;
	pmem_scale = 1000*(1U<<(bits_per_int-11)) / total_memory;
	/* s->rss is in kb. we want (s->rss * pmem_scale) to never overflow */
	while (pmem_scale >= 512) {
		pmem_scale /= 4;
		pmem_shift -= 2;
	}
#ifdef CONFIG_FEATURE_TOP_CPU_USAGE_PERCENTAGE
	/*
	 * CPU% = s->pcpu/sum(s->pcpu) * busy_cpu_ticks/total_cpu_ticks
	 * (pcpu is delta of sys+user time between samples)
	 */
	/* (jif.xxx - prev_jif.xxx) and s->pcpu are
	 * in 0..~64000 range (HZ*update_interval).
	 * we assume that unsigned is at least 32-bit.
	 */
	pcpu_shift = 6;
	pcpu_scale = (1000*64*(uint16_t)(jif.busy-prev_jif.busy) ? : 1);
	while (pcpu_scale < (1U<<(bits_per_int-2))) {
		pcpu_scale *= 4;
		pcpu_shift += 2;
	}
	pcpu_scale /= ( (uint16_t)(jif.total-prev_jif.total)*total_pcpu ? : 1);
	/* we want (s->pcpu * pcpu_scale) to never overflow */
	while (pcpu_scale >= 1024) {
		pcpu_scale /= 4;
		pcpu_shift -= 2;
	}
	/* printf(" pmem_scale=%u pcpu_scale=%u ", pmem_scale, pcpu_scale); */
#endif

	while (count--) {
		div_t pmem = div( (s->rss*pmem_scale) >> pmem_shift, 10);
		int col = scr_width+1;
		USE_FEATURE_TOP_CPU_USAGE_PERCENTAGE(div_t pcpu;)

		if (s->rss >= 100*1024)
			sprintf(rss_str_buf, "%6ldM", s->rss/1024);
		else
			sprintf(rss_str_buf, "%7ld", s->rss);
		USE_FEATURE_TOP_CPU_USAGE_PERCENTAGE(pcpu = div((s->pcpu*pcpu_scale) >> pcpu_shift, 10);)
		col -= printf("\n%5d %-8s %s  %s%6d%3u.%c" \
				USE_FEATURE_TOP_CPU_USAGE_PERCENTAGE("%3u.%c") " ",
				s->pid, s->user, s->state, rss_str_buf, s->ppid,
				USE_FEATURE_TOP_CPU_USAGE_PERCENTAGE(pcpu.quot, '0'+pcpu.rem,)
				pmem.quot, '0'+pmem.rem);
		if (col>0)
			printf("%.*s", col, s->short_cmd);
		/* printf(" %d/%d %lld/%lld", s->pcpu, total_pcpu,
			jif.busy - prev_jif.busy, jif.total - prev_jif.total); */
		s++;
	}
	/* printf(" %d", hist_iterations); */
	putchar('\r');
	fflush(stdout);
}

static void clearmems(void)
{
	free(top);
	top = 0;
	ntop = 0;
}

#ifdef CONFIG_FEATURE_USE_TERMIOS
#include <termios.h>
#include <signal.h>


static struct termios initial_settings;

static void reset_term(void)
{
	tcsetattr(0, TCSANOW, (void *) &initial_settings);
#ifdef CONFIG_FEATURE_CLEAN_UP
	clearmems();
#ifdef CONFIG_FEATURE_TOP_CPU_USAGE_PERCENTAGE
	free(prev_hist);
#endif
#endif /* CONFIG_FEATURE_CLEAN_UP */
}

static void sig_catcher(int sig ATTRIBUTE_UNUSED)
{
	reset_term();
	exit(1);
}
#endif /* CONFIG_FEATURE_USE_TERMIOS */


int top_main(int argc, char **argv)
{
	int opt, interval, lines, col;
	char *sinterval;
#ifdef CONFIG_FEATURE_USE_TERMIOS
	struct termios new_settings;
	struct timeval tv;
	fd_set readfds;
	unsigned char c;
#endif /* CONFIG_FEATURE_USE_TERMIOS */

	/* do normal option parsing */
	opt = bb_getopt_ulflags(argc, argv, "d:", &sinterval);
	if ((opt & 1)) {
		interval = atoi(sinterval);
	} else {
		/* Default update rate is 5 seconds */
		interval = 5;
	}

	/* change to /proc */
	bb_xchdir("/proc");
#ifdef CONFIG_FEATURE_USE_TERMIOS
	tcgetattr(0, (void *) &initial_settings);
	memcpy(&new_settings, &initial_settings, sizeof(struct termios));
	new_settings.c_lflag &= ~(ISIG | ICANON); /* unbuffered input */
	/* Turn off echoing */
	new_settings.c_lflag &= ~(ECHO | ECHONL);

	signal(SIGTERM, sig_catcher);
	signal(SIGINT, sig_catcher);
	tcsetattr(0, TCSANOW, (void *) &new_settings);
	atexit(reset_term);
#endif /* CONFIG_FEATURE_USE_TERMIOS */

#ifdef CONFIG_FEATURE_TOP_CPU_USAGE_PERCENTAGE
	sort_function[0] = pcpu_sort;
	sort_function[1] = mem_sort;
	sort_function[2] = time_sort;
#else
	sort_function = mem_sort;
#endif /* CONFIG_FEATURE_TOP_CPU_USAGE_PERCENTAGE */

	while (1) {
		procps_status_t *p;

		/* Default to 25 lines - 5 lines for status */
		lines = 24 - 3;
		col = 79;
#ifdef CONFIG_FEATURE_USE_TERMIOS
		get_terminal_width_height(0, &col, &lines);
		if (lines < 5 || col < MIN_WIDTH) {
			sleep(interval);
			continue;
		}
		lines -= 3;
#endif /* CONFIG_FEATURE_USE_TERMIOS */

		/* read process IDs & status for all the processes */
		while ((p = procps_scan(0)) != 0) {
			int n = ntop;

			top = xrealloc(top, (++ntop)*sizeof(procps_status_t));
			memcpy(top + n, p, sizeof(procps_status_t));
		}
		if (ntop == 0) {
			bb_error_msg_and_die("Can't find process info in /proc");
		}
#ifdef CONFIG_FEATURE_TOP_CPU_USAGE_PERCENTAGE
		if (!prev_hist_count) {
			do_stats();
			sleep(1);
			clearmems();
			continue;
		}
		do_stats();
		qsort(top, ntop, sizeof(procps_status_t), (void*)mult_lvl_cmp);
#else
		qsort(top, ntop, sizeof(procps_status_t), (void*)sort_function);
#endif /* CONFIG_FEATURE_TOP_CPU_USAGE_PERCENTAGE */
		opt = lines;
		if (opt > ntop) {
			opt = ntop;
		}
		/* show status for each of the processes */
		display_status(opt, col);
#ifdef CONFIG_FEATURE_USE_TERMIOS
		tv.tv_sec = interval;
		tv.tv_usec = 0;
		FD_ZERO(&readfds);
		FD_SET(0, &readfds);
		select(1, &readfds, NULL, NULL, &tv);
		if (FD_ISSET(0, &readfds)) {
			if (read(0, &c, 1) <= 0) {   /* signal */
				return EXIT_FAILURE;
			}
			if (c == 'q' || c == initial_settings.c_cc[VINTR])
				break;
			if (c == 'M') {
#ifdef CONFIG_FEATURE_TOP_CPU_USAGE_PERCENTAGE
				sort_function[0] = mem_sort;
				sort_function[1] = pcpu_sort;
				sort_function[2] = time_sort;
#else
				sort_function = mem_sort;
#endif
			}
#ifdef CONFIG_FEATURE_TOP_CPU_USAGE_PERCENTAGE
			if (c == 'P') {
				sort_function[0] = pcpu_sort;
				sort_function[1] = mem_sort;
				sort_function[2] = time_sort;
			}
			if (c == 'T') {
				sort_function[0] = time_sort;
				sort_function[1] = mem_sort;
				sort_function[2] = pcpu_sort;
			}
#endif
			if (c == 'N') {
#ifdef CONFIG_FEATURE_TOP_CPU_USAGE_PERCENTAGE
				sort_function[0] = pid_sort;
#else
				sort_function = pid_sort;
#endif
			}
		}
#else
		sleep(interval);
#endif /* CONFIG_FEATURE_USE_TERMIOS */
		clearmems();
	}
	if (ENABLE_FEATURE_CLEAN_UP)
		clearmems();
	putchar('\n');
	return EXIT_SUCCESS;
}
