/* vi: set sw=4 ts=4: */
/*
 * tiny fuser implementation
 *
 * Copyright 2004 Tony J. White
 *
 * May be distributed under the conditions of the
 * GNU Library General Public License
 */

#include "busybox.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <limits.h>
#include <dirent.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <sys/sysmacros.h>

#define FUSER_PROC_DIR "/proc"
#define FUSER_MAX_LINE 255

#define FUSER_OPT_MOUNT  1
#define FUSER_OPT_KILL   2
#define FUSER_OPT_SILENT 4
#define FUSER_OPT_IP6    8
#define FUSER_OPT_IP4    16

typedef struct inode_list {
	ino_t inode;
	dev_t dev;
	struct inode_list *next;
} inode_list;

typedef struct pid_list {
	pid_t pid;
	struct pid_list *next;
} pid_list;

static int fuser_option(char *option)
{
	int opt = 0;

	if(!(strlen(option))) return 0;
	if(option[0] != '-') return 0;
	++option;
	while(*option != '\0') {
		if(*option == 'm') opt |= FUSER_OPT_MOUNT;
		else if(*option == 'k') opt |= FUSER_OPT_KILL;
		else if(*option == 's') opt |= FUSER_OPT_SILENT;
		else if(*option == '6') opt |= FUSER_OPT_IP6;
		else if(*option == '4') opt |= FUSER_OPT_IP4;
		else {
			bb_error_msg_and_die(
				"Unsupported option '%c'", *option);
		}
		++option;
	}
	return opt;
}

static int fuser_file_to_dev_inode(const char *filename,
	 dev_t *dev, ino_t *inode)
{
	struct stat f_stat;
	if((stat(filename, &f_stat)) < 0) return 0;
	*inode = f_stat.st_ino;
	*dev = f_stat.st_dev;
	return 1;
}

static int fuser_find_socket_dev(dev_t *dev)
{
	int fd = socket(PF_INET, SOCK_DGRAM,0);
	struct stat buf;

	if (fd >= 0 && (fstat(fd, &buf)) == 0) {
		*dev =  buf.st_dev;
		close(fd);
		return 1;
	}
	return 0;
}

static int fuser_parse_net_arg(const char *filename,
	const char **proto, int *port)
{
	char path[sizeof(FUSER_PROC_DIR)+12], tproto[5];

	if((sscanf(filename, "%d/%4s", port, tproto)) != 2) return 0;
	sprintf(path, "%s/net/%s", FUSER_PROC_DIR, tproto);
	if((access(path, R_OK)) != 0) return 0;
	*proto = bb_xstrdup(tproto);
	return 1;
}

static int fuser_add_pid(pid_list *plist, pid_t pid)
{
	pid_list *curr = NULL, *last = NULL;

	if(plist->pid == 0) plist->pid = pid;
	curr = plist;
	while(curr != NULL) {
		if(curr->pid == pid) return 1;
		last = curr;
		curr = curr->next;
	}
	curr = xmalloc(sizeof(pid_list));
	last->next = curr;
	curr->pid = pid;
	curr->next = NULL;
	return 1;
}

static int fuser_add_inode(inode_list *ilist, dev_t dev, ino_t inode)
{
	inode_list *curr = NULL, *last = NULL;

	if(!ilist->inode && !ilist->dev) {
		ilist->dev = dev;
		ilist->inode = inode;
	}
	curr = ilist;
	while(curr != NULL) {
		if(curr->inode == inode && curr->dev == dev) return 1;
		last = curr;
		curr = curr->next;
	}
	curr = xmalloc(sizeof(inode_list));
	last->next = curr;
	curr->dev = dev;
	curr->inode = inode;
	curr->next = NULL;
	return 1;
}

static int fuser_scan_proc_net(int opts, const char *proto,
	int port, inode_list *ilist)
{
	char path[sizeof(FUSER_PROC_DIR)+12], line[FUSER_MAX_LINE+1];
	char addr[128];
	ino_t tmp_inode;
	dev_t tmp_dev;
	long long  uint64_inode;
	int tmp_port;
	FILE *f;

	if(!fuser_find_socket_dev(&tmp_dev)) tmp_dev = 0;
	sprintf(path, "%s/net/%s", FUSER_PROC_DIR, proto);

	if (!(f = fopen(path, "r"))) return 0;
	while(fgets(line, FUSER_MAX_LINE, f)) {
		if(sscanf(line,
			"%*d: %64[0-9A-Fa-f]:%x %*x:%*x %*x %*x:%*x "
			"%*x:%*x %*x %*d %*d %llu",
			addr, &tmp_port, &uint64_inode) == 3) {
			if((strlen(addr) == 8) &&
				(opts & FUSER_OPT_IP6)) continue;
			else if((strlen(addr) > 8) &&
				(opts & FUSER_OPT_IP4)) continue;
			if(tmp_port == port) {
				tmp_inode = uint64_inode;
				fuser_add_inode(ilist, tmp_dev, tmp_inode);
			}
		}

	}
	fclose(f);
	return 1;
}

static int fuser_search_dev_inode(int opts, inode_list *ilist,
	dev_t dev, ino_t inode)
{
	inode_list *curr;
	curr = ilist;

	while(curr) {
		if((opts & FUSER_OPT_MOUNT) &&  curr->dev == dev)
			return 1;
		if(curr->inode == inode && curr->dev == dev)
			return 1;
		curr = curr->next;
	}
	return 0;
}

static int fuser_scan_pid_maps(int opts, const char *fname, pid_t pid,
	inode_list *ilist, pid_list *plist)
{
	FILE *file;
	char line[FUSER_MAX_LINE + 1];
	int major, minor;
	ino_t inode;
	long long uint64_inode;
	dev_t dev;

	if (!(file = fopen(fname, "r"))) return 0;
	while (fgets(line, FUSER_MAX_LINE, file)) {
		if(sscanf(line, "%*s %*s %*s %x:%x %llu",
			&major, &minor, &uint64_inode) != 3) continue;
		inode = uint64_inode;
		if(major == 0 && minor == 0 && inode == 0) continue;
		dev = makedev(major, minor);
		if(fuser_search_dev_inode(opts, ilist, dev, inode)) {
			fuser_add_pid(plist, pid);
		}

	}
	fclose(file);
	return 1;
}

static int fuser_scan_link(int opts, const char *lname, pid_t pid,
	inode_list *ilist, pid_list *plist)
{
	ino_t inode;
	dev_t dev;

	if(!fuser_file_to_dev_inode(lname, &dev, &inode)) return 0;
	if(fuser_search_dev_inode(opts, ilist, dev, inode))
		fuser_add_pid(plist, pid);
	return 1;
}

static int fuser_scan_dir_links(int opts, const char *dname, pid_t pid,
	inode_list *ilist, pid_list *plist)
{
	DIR *d;
	struct dirent *de;
	char *lname;

	if((d = opendir(dname))) {
		while((de = readdir(d)) != NULL) {
			lname = concat_subpath_file(dname, de->d_name);
			if(lname == NULL)
				continue;
			fuser_scan_link(opts, lname, pid, ilist, plist);
			free(lname);
		}
		closedir(d);
	}
	else return 0;
	return 1;

}

static int fuser_scan_proc_pids(int opts, inode_list *ilist, pid_list *plist)
{
	DIR *d;
	struct dirent *de;
	pid_t pid;
	char *dname;

	if(!(d = opendir(FUSER_PROC_DIR))) return 0;
	while((de = readdir(d)) != NULL) {
		pid = (pid_t)atoi(de->d_name);
		if(!pid) continue;
		dname = concat_subpath_file(FUSER_PROC_DIR, de->d_name);
		if(chdir(dname) < 0) {
			free(dname);
			continue;
		}
		free(dname);
		fuser_scan_link(opts, "cwd", pid, ilist, plist);
		fuser_scan_link(opts, "exe", pid, ilist, plist);
		fuser_scan_link(opts, "root", pid, ilist, plist);
		fuser_scan_dir_links(opts, "fd", pid, ilist, plist);
		fuser_scan_dir_links(opts, "lib", pid, ilist, plist);
		fuser_scan_dir_links(opts, "mmap", pid, ilist, plist);
		fuser_scan_pid_maps(opts, "maps", pid, ilist, plist);
		chdir("..");
	}
	closedir(d);
	return 1;
}

static int fuser_print_pid_list(pid_list *plist)
{
	pid_list *curr = plist;

	if(plist == NULL) return 0;
	while(curr != NULL) {
		if(curr->pid > 0) printf("%d ", curr->pid);
		curr = curr->next;
	}
	printf("\n");
	return 1;
}

static int fuser_kill_pid_list(pid_list *plist, int sig)
{
	pid_list *curr = plist;
	pid_t mypid = getpid();
	int success = 1;

	if(plist == NULL) return 0;
	while(curr != NULL) {
		if(curr->pid > 0 && curr->pid != mypid) {
			if (kill(curr->pid, sig) != 0) {
				bb_perror_msg(
					"Could not kill pid '%d'", curr->pid);
				success = 0;
			}
		}
		curr = curr->next;
	}
	return success;
}

int fuser_main(int argc, char **argv)
{
	int port, i, optn;
	int* fni; /* file name indexes of argv */
	int fnic = 0;  /* file name index count */
	const char *proto;
	static int opt = 0; /* FUSER_OPT_ */
	dev_t dev;
	ino_t inode;
	pid_list *pids;
	inode_list *inodes;
	int killsig = SIGTERM;
	int success = 1;

	if (argc < 2)
		bb_show_usage();

	fni = xmalloc(sizeof(int));
	for(i=1;i<argc;i++) {
		optn = fuser_option(argv[i]);
		if(optn) opt |= optn;
		else if(argv[i][0] == '-') {
			if(!(u_signal_names(argv[i]+1, &killsig, 0)))
				killsig = SIGTERM;
		}
		else {
			fni = xrealloc(fni, sizeof(int) * (fnic+2));
			fni[fnic++] = i;
		}
	}
	if(!fnic) return 1;

	pids = xmalloc(sizeof(pid_list));
	inodes = xmalloc(sizeof(inode_list));
	for(i=0;i<fnic;i++) {
		if(fuser_parse_net_arg(argv[fni[i]], &proto, &port)) {
			fuser_scan_proc_net(opt, proto, port, inodes);
		}
		else {
			if(!fuser_file_to_dev_inode(
				argv[fni[i]], &dev, &inode)) {
				free(pids);
				free(inodes);
				bb_perror_msg_and_die(
					"Could not open '%s'", argv[fni[i]]);
			}
			fuser_add_inode(inodes, dev, inode);
		}
	}
	success = fuser_scan_proc_pids(opt, inodes, pids);
	/* if the first pid in the list is 0, none have been found */
	if(pids->pid == 0) success = 0;
	if(success) {
		if(opt & FUSER_OPT_KILL) {
			success = fuser_kill_pid_list(pids, killsig);
		}
		else if(!(opt & FUSER_OPT_SILENT)) {
			success = fuser_print_pid_list(pids);
		}
	}
	free(pids);
	free(inodes);
	/* return 0 on (success == 1) 1 otherwise */
	return (success != 1);
}
