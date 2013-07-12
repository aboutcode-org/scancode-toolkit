/*++
/* NAME
/*	master_spawn 3
/* SUMMARY
/*	Postfix master - child process birth and death
/* SYNOPSIS
/*	#include "master.h"
/*
/*	void	master_spawn(serv)
/*	MASTER_SERV *serv;
/*
/*	void	master_reap_child()
/*
/*	void	master_delete_children(serv)
/*	MASTER_SERV *serv;
/* DESCRIPTION
/*	This module creates and cleans up child processes, and applies
/*	a process creation throttle in case of serious trouble.
/*	This module is the working horse for the master_avail(3) process
/*	creation policy module.
/*
/*	master_spawn() spawns off a child process for the specified service,
/*	making the child process available for servicing connection requests.
/*	It is an error to call this function then the specified service is
/*	throttled.
/*
/*	master_reap_child() cleans up all dead child processes.  One typically
/*	runs this function at a convenient moment after receiving a SIGCHLD
/*	signal. When a child process terminates abnormally after being used
/*	for the first time, process creation for that service is throttled
/*	for a configurable amount of time.
/*
/*	master_delete_children() deletes all child processes that provide
/*	the named service. Upon exit, the process creation throttle for that
/*	service is released.
/* DIAGNOSTICS
/*	Panic: interface violations, internal inconsistencies.
/*	Fatal errors: out of memory.  Warnings: throttle on/off.
/* BUGS
/* SEE ALSO
/*	master_avail(3), process creation policy.
/* LICENSE
/* .ad
/* .fi
/*	The Secure Mailer license must be distributed with this software.
/* AUTHOR(S)
/*	Wietse Venema
/*	IBM T.J. Watson Research
/*	P.O. Box 704
/*	Yorktown Heights, NY 10598, USA
/*--*/

/* System libraries. */

#include <sys_defs.h>
#include <sys/wait.h>
#include <stdlib.h>
#include <unistd.h>
#include <syslog.h>			/* closelog() */
#include <signal.h>
#include <stdarg.h>

/* Utility libraries. */

#include <msg.h>
#include <binhash.h>
#include <mymalloc.h>
#include <events.h>
#include <argv.h>
#include <syslog.h>

/* Application-specific. */

#include "master_proto.h"
#include "master.h"

BINHASH *master_child_table;
static void master_unthrottle(MASTER_SERV *serv);

/* master_unthrottle_wrapper - in case (char *) != (struct *) */

static void master_unthrottle_wrapper(int unused_event, char *ptr)
{
    MASTER_SERV *serv = (MASTER_SERV *) ptr;

    /*
     * This routine runs after expiry of the timer set in master_throttle(),
     * which gets called when it appears that the world is falling apart.
     */
    master_unthrottle(serv);
}

/* master_unthrottle - enable process creation */

static void master_unthrottle(MASTER_SERV *serv)
{

    /*
     * Enable process creation within this class. Disable the "unthrottle"
     * timer just in case we're being called directly from the cleanup
     * routine, instead of from the event manager.
     */
    if ((serv->flags & MASTER_FLAG_THROTTLE) != 0) {
	serv->flags &= ~MASTER_FLAG_THROTTLE;
	event_cancel_timer(master_unthrottle_wrapper, (char *) serv);
	if (msg_verbose)
	    msg_info("throttle released for command %s", serv->path);
	master_avail_listen(serv);		/* XXX interface botch */
    }
}

/* master_throttle - suspend process creation */

static void master_throttle(MASTER_SERV *serv)
{

    /*
     * Perhaps the command to be run is defective, perhaps some configuration
     * is wrong, or perhaps the system is out of resources. Disable further
     * process creation attempts for a while.
     */
    if ((serv->flags & MASTER_FLAG_THROTTLE) == 0) {
	serv->flags |= MASTER_FLAG_THROTTLE;
	event_request_timer(master_unthrottle_wrapper, (char *) serv,
			    serv->throttle_delay);
	if (msg_verbose)
	    msg_info("throttling command %s", serv->path);
    }
}

/* master_spawn - spawn off new child process if we can */

void    master_spawn(MASTER_SERV *serv)
{
    char   *myname = "master_spawn";
    MASTER_PROC *proc;
    MASTER_PID pid;
    int     n;

    if (master_child_table == 0)
	master_child_table = binhash_create(0);

    /*
     * Sanity checks. The master_avail module is supposed to know what it is
     * doing.
     */
    if (!MASTER_LIMIT_OK(serv->max_proc, serv->total_proc))
	msg_panic("%s: at process limit %d", myname, serv->total_proc);
    if (serv->avail_proc > 0)
	msg_panic("%s: processes available: %d", myname, serv->avail_proc);
    if (serv->flags & MASTER_FLAG_THROTTLE)
	msg_panic("%s: throttled service: %s", myname, serv->path);

    /*
     * Create a child process and connect parent and child via the status
     * pipe.
     */
    switch (pid = fork()) {

	/*
	 * Error. We're out of some essential resource. Best recourse is to
	 * try again later.
	 */
    case -1:
	msg_warn("%s: fork: %m -- throttling", myname);
	master_throttle(serv);
	return;

	/*
	 * Child process. Redirect child stdin/stdout to the parent-child
	 * connection and run the requested command. Leave child stderr
	 * alone. Disable exit handlers: they should be executed by the
	 * parent only.
	 */
    case 0:
	msg_cleanup((void (*) (void)) 0);	/* disable exit handler */
	closelog();				/* avoid filedes leak */

	if (master_flow_pipe[0] <= MASTER_FLOW_READ)
	    msg_fatal("%s: flow pipe read descriptor <= %d",
		      myname, MASTER_FLOW_READ);
	if (DUP2(master_flow_pipe[0], MASTER_FLOW_READ) < 0)
	    msg_fatal("%s: dup2: %m", myname);
	if (close(master_flow_pipe[0]) < 0)
	    msg_fatal("close %d: %m", master_flow_pipe[0]);

	if (master_flow_pipe[1] <= MASTER_FLOW_WRITE)
	    msg_fatal("%s: flow pipe read descriptor <= %d",
		      myname, MASTER_FLOW_WRITE);
	if (DUP2(master_flow_pipe[1], MASTER_FLOW_WRITE) < 0)
	    msg_fatal("%s: dup2: %m", myname);
	if (close(master_flow_pipe[1]) < 0)
	    msg_fatal("close %d: %m", master_flow_pipe[1]);

	close(serv->status_fd[0]);		/* status channel */
	if (serv->status_fd[1] <= MASTER_STATUS_FD)
	    msg_fatal("%s: status file descriptor collision", myname);
	if (DUP2(serv->status_fd[1], MASTER_STATUS_FD) < 0)
	    msg_fatal("%s: dup2 status_fd: %m", myname);
	(void) close(serv->status_fd[1]);

	for (n = 0; n < serv->listen_fd_count; n++) {
	    if (serv->listen_fd[n] <= MASTER_LISTEN_FD + n)
		msg_fatal("%s: listen file descriptor collision", myname);
	    if (DUP2(serv->listen_fd[n], MASTER_LISTEN_FD + n) < 0)
		msg_fatal("%s: dup2 listen_fd %d: %m",
			  myname, serv->listen_fd[n]);
	    (void) close(serv->listen_fd[n]);
	}
	execvp(serv->path, serv->args->argv);
	msg_fatal("%s: exec %s: %m", myname, serv->path);
	exit(1);
	/* NOTREACHED */

	/*
	 * Parent. Fill in a process member data structure and set up links
	 * between child and process. Say this process has become available.
	 * If this service has a wakeup timer that is turned on only when the
	 * service is actually used, turn on the wakeup timer.
	 */
    default:
	if (msg_verbose)
	    msg_info("spawn command %s; pid %d", serv->path, pid);
	proc = (MASTER_PROC *) mymalloc(sizeof(MASTER_PROC));
	proc->serv = serv;
	proc->pid = pid;
	proc->use_count = 0;
	proc->avail = 0;
	binhash_enter(master_child_table, (char *) &pid,
		      sizeof(pid), (char *) proc);
	serv->total_proc++;
	master_avail_more(serv, proc);
	if (serv->flags & MASTER_FLAG_CONDWAKE) {
	    serv->flags &= ~MASTER_FLAG_CONDWAKE;
	    master_wakeup_init(serv);
	    if (msg_verbose)
		msg_info("start conditional timer for %s", serv->name);
	}
	return;
    }
}

/* master_delete_child - destroy child process info */

static void master_delete_child(MASTER_PROC *proc)
{
    MASTER_SERV *serv;

    /*
     * Undo the things that master_spawn did. Stop the process if it still
     * exists, and remove it from the lookup tables. Update the number of
     * available processes.
     */
    serv = proc->serv;
    serv->total_proc--;
    if (proc->avail == MASTER_STAT_AVAIL)
	master_avail_less(serv, proc);
    else if (MASTER_LIMIT_OK(serv->max_proc, serv->total_proc)
	     && serv->avail_proc < 1)
	master_avail_listen(serv);
    binhash_delete(master_child_table, (char *) &proc->pid,
		   sizeof(proc->pid), (void (*) (char *)) 0);
    myfree((char *) proc);
}

/* master_reap_child - reap dead children */

void    master_reap_child(void)
{
    MASTER_SERV *serv;
    MASTER_PROC *proc;
    MASTER_PID pid;
    WAIT_STATUS_T status;

    /*
     * Pick up termination status of all dead children. When a process failed
     * on its first job, assume we see the symptom of a structural problem
     * (configuration problem, system running out of resources) and back off.
     */
    while ((pid = waitpid((pid_t) - 1, &status, WNOHANG)) > 0) {
	if (msg_verbose)
	    msg_info("master_reap_child: pid %d", pid);
	if ((proc = (MASTER_PROC *) binhash_find(master_child_table,
					(char *) &pid, sizeof(pid))) == 0) {
	    msg_panic("master_reap: unknown pid: %d", pid);
	    continue;
	}
	serv = proc->serv;
	if (!NORMAL_EXIT_STATUS(status)) {
	    if (WIFEXITED(status))
		msg_warn("process %s pid %d exit status %d",
			 serv->path, pid, WEXITSTATUS(status));
	    if (WIFSIGNALED(status))
		msg_warn("process %s pid %d killed by signal %d",
			 serv->path, pid, WTERMSIG(status));
	}
	if (!NORMAL_EXIT_STATUS(status) && proc->use_count == 0
	    && (serv->flags & MASTER_FLAG_THROTTLE) == 0) {
	    msg_warn("%s: bad command startup -- throttling", serv->path);
	    master_throttle(serv);
	}
	master_delete_child(proc);
    }
}

/* master_delete_children - delete all child processes of service */

void    master_delete_children(MASTER_SERV *serv)
{
    BINHASH_INFO **list;
    BINHASH_INFO **info;
    MASTER_PROC *proc;

    /*
     * XXX turn on the throttle so that master_reap_child() doesn't. Someone
     * has to turn off the throttle in order to stop the associated timer
     * request, so we might just as well do it at the end.
     */
    master_throttle(serv);
    for (info = list = binhash_list(master_child_table); *info; info++) {
	proc = (MASTER_PROC *) info[0]->value;
	if (proc->serv == serv)
	    (void) kill(proc->pid, SIGTERM);
    }
    while (serv->total_proc > 0)
	master_reap_child();
    myfree((char *) list);
    master_unthrottle(serv);
}
