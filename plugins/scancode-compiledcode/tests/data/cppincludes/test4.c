
























#include <config.h>

#if HAVE_STDLIB_H
#include <stdlib.h>
#endif
#if HAVE_UNISTD_H
#include <unistd.h>
#endif
#if HAVE_STRING_H
#include <string.h>
#else
#include <strings.h>
#endif
#include <sys/types.h>
#if HAVE_SYS_WAIT_H
#include <sys/wait.h>
#endif
#if HAVE_WINSOCK_H
#include <winsock.h>
#else
#include <sys/socket.h>
#endif
#if HAVE_SYS_SOCKIO_H
#include <sys/sockio.h>
#endif
#if HAVE_NETINET_IN_H
#include <netinet/in.h>
#endif
#include <stdio.h>
#if HAVE_SYS_TIME_H
# include <sys/time.h>
# if TIME_WITH_SYS_TIME
#  include <time.h>
# endif
#else
# include <time.h>
#endif
#if HAVE_SYS_SELECT_H
#include <sys/select.h>
#endif
#if HAVE_SYS_PARAM_H
#include <sys/param.h>
#endif
#if HAVE_SYSLOG_H
#include <syslog.h>
#endif
#if HAVE_SYS_IOCTL_H
#include <sys/ioctl.h>
#endif
#if HAVE_NET_IF_H
#include <net/if.h>
#endif
#if HAVE_NETDB_H
#include <netdb.h>
#endif
#if HAVE_ARPA_INET_H
#include <arpa/inet.h>
#endif
#if HAVE_FCNTL_H
#include <fcntl.h>
#endif
#if HAVE_PROCESS_H  
#include <process.h>
#endif
#include <signal.h>
#include <errno.h>

#include <getopt.h>

#include "asn1.h"
#include "snmp_api.h"
#include "snmp_impl.h"
#include "snmp_client.h"
#include "mib.h"
#include "snmp.h"
#include "system.h"
#include "version.h"
#include "snmptrapd_handlers.h"
#include "snmptrapd_log.h"
#include "read_config.h"
#include "snmp_debug.h"
#include "snmp_logging.h"
#include "callback.h"
#include "snmpusm.h"
#include "tools.h"
#include "lcd_time.h"
#include "transform_oids.h"
#include "snmpv3.h"
#include "default_store.h"

#define DS_APP_NUMERIC_IP  1

#ifndef BSD4_3
#define BSD4_2
#endif

#ifndef FD_SET

typedef long	fd_mask;
#define NFDBITS	(sizeof(fd_mask) * NBBY)	

#define	FD_SET(n, p)	((p)->fds_bits[(n)/NFDBITS] |= (1 << ((n) % NFDBITS)))
#define	FD_CLR(n, p)	((p)->fds_bits[(n)/NFDBITS] &= ~(1 << ((n) % NFDBITS)))
#define	FD_ISSET(n, p)	((p)->fds_bits[(n)/NFDBITS] & (1 << ((n) % NFDBITS)))
#define FD_ZERO(p)      memset((p), 0, sizeof(*(p)))
#endif

char *logfile = 0;
int Print = 0;
int Syslog = 0;
int Event = 0;
int dropauth = 0;
int running = 1;
int reconfig = 0;

const char *trap1_std_str = "%.4y-%.2m-%.2l %.2h:%.2j:%.2k %B [%b] (via %A [%a]): %N\n\t%W Trap (%q) Uptime: %#T\n%v\n",
	   *trap2_std_str = "%.4y-%.2m-%.2l %.2h:%.2j:%.2k %B [%b]:\n%v\n";
char       *trap1_fmt_str = NULL,
           *trap2_fmt_str = NULL; 




#ifndef LOG_CONS
#define LOG_CONS	0	
#endif
#ifndef LOG_PID
#define LOG_PID		0	
#endif
#ifndef LOG_LOCAL0
#define LOG_LOCAL0	0
#endif
#ifndef LOG_LOCAL1
#define LOG_LOCAL1	0
#endif
#ifndef LOG_LOCAL2
#define LOG_LOCAL2	0
#endif
#ifndef LOG_LOCAL3
#define LOG_LOCAL3	0
#endif
#ifndef LOG_LOCAL4
#define LOG_LOCAL4	0
#endif
#ifndef LOG_LOCAL5
#define LOG_LOCAL5	0
#endif
#ifndef LOG_LOCAL6
#define LOG_LOCAL6	0
#endif
#ifndef LOG_LOCAL7
#define LOG_LOCAL7	0
#endif
#ifndef LOG_DAEMON
#define LOG_DAEMON	0
#endif



int Facility = LOG_LOCAL0;

struct timeval Now;

void init_syslog(void);

void update_config (void);

#ifdef WIN32
void openlog(const char *app, int options, int fac) {
}

void syslog(int level, const char *fmt, ...) {
}
#endif

const char *
trap_description(int trap)
{
    switch(trap){
	case SNMP_TRAP_COLDSTART:
	    return "Cold Start";
	case SNMP_TRAP_WARMSTART:
	    return "Warm Start";
	case SNMP_TRAP_LINKDOWN:
	    return "Link Down";
	case SNMP_TRAP_LINKUP:
	    return "Link Up";
	case SNMP_TRAP_AUTHFAIL:
	    return "Authentication Failure";
	case SNMP_TRAP_EGPNEIGHBORLOSS:
	    return "EGP Neighbor Loss";
	case SNMP_TRAP_ENTERPRISESPECIFIC:
	    return "Enterprise Specific";
	default:
	    return "Unknown Type";
    }
}


struct snmp_pdu *
snmp_clone_pdu2(struct snmp_pdu *pdu,
		int command)
{
    struct snmp_pdu *newpdu = snmp_clone_pdu(pdu);
    if (newpdu) newpdu->command = command;
    return newpdu;
}

static oid risingAlarm[] = {1, 3, 6, 1, 6, 3, 2, 1, 1, 3, 1};
static oid fallingAlarm[] = {1, 3, 6, 1, 6, 3, 2, 1, 1, 3, 2};
static oid unavailableAlarm[] = {1, 3, 6, 1, 6, 3, 2, 1, 1, 3, 3};

void
event_input(struct variable_list *vp)
{
    int eventid;
    oid variable[MAX_OID_LEN];
    int variablelen;
    u_long destip;
    int sampletype;
    int value;
    int threshold;

    oid *op;

    vp = vp->next_variable;	
    if (vp->val_len != sizeof(risingAlarm)
	|| !memcmp(vp->val.objid, risingAlarm, sizeof(risingAlarm)))
	eventid = 1;
    else if (vp->val_len != sizeof(risingAlarm)
	|| !memcmp(vp->val.objid, fallingAlarm, sizeof(fallingAlarm)))
	eventid = 2;
    else if (vp->val_len != sizeof(risingAlarm)
	|| !memcmp(vp->val.objid, unavailableAlarm, sizeof(unavailableAlarm)))
	eventid = 3;
    else {
	fprintf(stderr, "unknown event\n");
	eventid = 0;
    }

    vp = vp->next_variable;
    memmove(variable, vp->val.objid, vp->val_len * sizeof(oid));
    variablelen = vp->val_len;
    op = vp->name + 22;
    destip = 0;
    destip |= (*op++) << 24;
    destip |= (*op++) << 16;
    destip |= (*op++) << 8;
    destip |= *op++;

    vp = vp->next_variable;
    sampletype = *vp->val.integer;

    vp = vp->next_variable;
    value= *vp->val.integer;

    vp = vp->next_variable;
    threshold = *vp->val.integer;

    printf("%d: 0x%02lX %d %d %d\n", eventid, destip, sampletype, value, threshold);

}

void send_handler_data(FILE *file, struct hostent *host,
		       struct snmp_pdu *pdu)
{
  struct variable_list tmpvar, *vars;
  struct sockaddr_in *pduIp = (struct sockaddr_in *)&(pdu->address);
  static oid trapoids[] = {1,3,6,1,6,3,1,1,5,0};
  static oid snmpsysuptime[] = {1,3,6,1,2,1,1,3,0};
  static oid snmptrapoid[] = {1,3,6,1,6,3,1,1,4,1,0};
  static oid snmptrapent[] = {1,3,6,1,6,3,1,1,4,3,0};
  static oid snmptrapaddr[] = {1,3,6,1,6,3,18,1,3,0};
  static oid snmptrapcom[] = {1,3,6,1,6,3,18,1,4,0};
  oid enttrapoid[MAX_OID_LEN];
  int enttraplen = pdu->enterprise_length;
  char varbuf[2048];

  fprintf(file,"%s\n%s\n",
      host ? host->h_name : inet_ntoa(pduIp->sin_addr),
      inet_ntoa(pduIp->sin_addr));
  if (pdu->command == SNMP_MSG_TRAP){
  

      tmpvar.val.integer = (long *) &pdu->time;
      tmpvar.val_len = sizeof(pdu->time);
      tmpvar.type = ASN_TIMETICKS;
      sprint_variable(varbuf, snmpsysuptime, sizeof(snmpsysuptime)/sizeof(snmpsysuptime[0]), &tmpvar);
      fprintf(file,"%s\n",varbuf);
      tmpvar.type = ASN_OBJECT_ID;
      if (pdu->trap_type == SNMP_TRAP_ENTERPRISESPECIFIC) {
	  memcpy(enttrapoid, pdu->enterprise, sizeof(oid)*enttraplen);
	  if (enttrapoid[enttraplen-1] != 0) enttrapoid[enttraplen++] = 0;
	  enttrapoid[enttraplen++] = pdu->specific_type;
	  tmpvar.val.objid = enttrapoid;
	  tmpvar.val_len = enttraplen*sizeof(oid);
      }
      else {
	  trapoids[9] = pdu->trap_type+1;
	  tmpvar.val.objid = trapoids;
	  tmpvar.val_len = 10*sizeof(oid);
      }
      sprint_variable(varbuf, snmptrapoid, sizeof(snmptrapoid)/sizeof(snmptrapoid[0]), &tmpvar);
      fprintf(file,"%s\n",varbuf);
  }
  
  for(vars = pdu->variables; vars; vars = vars->next_variable) {
      sprint_variable(varbuf, vars->name, vars->name_length, vars);
      fprintf(file,"%s\n",varbuf);
  }
  if (pdu->command == SNMP_MSG_TRAP){
  

      tmpvar.val.string = (u_char *)&((struct sockaddr_in*)&pdu->agent_addr)->sin_addr.s_addr;
      tmpvar.val_len = 4;
      tmpvar.type = ASN_IPADDRESS;
      sprint_variable(varbuf, snmptrapaddr, sizeof(snmptrapaddr)/sizeof(snmptrapaddr[0]), &tmpvar);
      fprintf(file,"%s\n",varbuf);
      tmpvar.val.string = pdu->community;
      tmpvar.val_len = pdu->community_len;
      tmpvar.type = ASN_OCTET_STR;
      sprint_variable(varbuf, snmptrapcom, sizeof(snmptrapcom)/sizeof(snmptrapcom[0]), &tmpvar);
      fprintf(file,"%s\n",varbuf);
      tmpvar.val.objid = pdu->enterprise;
      tmpvar.val_len = pdu->enterprise_length*sizeof(oid);
      tmpvar.type = ASN_OBJECT_ID;
      sprint_variable(varbuf, snmptrapent, sizeof(snmptrapent)/sizeof(snmptrapent[0]), &tmpvar);
      fprintf(file,"%s\n",varbuf);
  }
}

void do_external(char *cmd,
		 struct hostent *host,
		 struct snmp_pdu *pdu)
{
  FILE *file;
  int oldquick, result;

  DEBUGMSGTL(("snmptrapd", "Running: %s\n", cmd));
  oldquick = snmp_get_quick_print();
  snmp_set_quick_print(1);
  if (cmd) {
#ifndef WIN32
    int fd[2];
    int pid;

    if (pipe(fd)) {
      snmp_log_perror("pipe");
    }
    if ((pid = fork()) == 0) {
      
      close(0);
      if (dup(fd[0]) != 0) {
        snmp_log_perror("dup");
      }
      close(fd[1]);
      close(fd[0]);
      system(cmd);
      exit(0);
    } else if (pid > 0) {
      file = fdopen(fd[1],"w");
      send_handler_data(file, host, pdu);
      fclose(file);
      close(fd[0]);
      close(fd[1]);
      if (waitpid(pid, &result,0) < 0) {
        snmp_log_perror("waitpid");
      }
    } else {
      snmp_log_perror("fork");
    }
#else
    char command_buf[128];
    char file_buf[L_tmpnam];

    tmpnam(file_buf);
    file = fopen(file_buf, "w");
    if (!file) {
	fprintf(stderr, "fopen: %s: %s\n", file_buf, strerror(errno));
    }
    else {
        send_handler_data(file, host, pdu);
        fclose(file);
	sprintf(command_buf, "%s < %s", cmd, file_buf);
        result = system(command_buf);
	if (result == -1)
	    fprintf(stderr, "system: %s: %s\n", command_buf, strerror(errno));
	else if (result)
	    fprintf(stderr, "system: %s: %d\n", command_buf, result);
        remove(file_buf);
    }
#endif	
  }
  snmp_set_quick_print(oldquick);
}

int snmp_input(int op,
	       struct snmp_session *session,
	       int reqid,
	       struct snmp_pdu *pdu,
	       void *magic)
{
    char out_bfr[SPRINT_MAX_LEN];
    struct variable_list *vars;
    struct sockaddr_in *pduIp   = (struct sockaddr_in *)&(pdu->address);
    char buf[64], oid_buf [SPRINT_MAX_LEN], *cp;
    struct snmp_pdu *reply;
    struct hostent *host;
    int varbufidx;
    char varbuf[SPRINT_MAX_LEN];
    static oid trapoids[10] = {1,3,6,1,6,3,1,1,5};
    static oid snmptrapoid2[11] = {1,3,6,1,6,3,1,1,4,1,0};
    struct variable_list tmpvar;
    char *Command = NULL;
    tmpvar.type = ASN_OBJECT_ID;

    if (op == RECEIVED_MESSAGE){
	if (pdu->command == SNMP_MSG_TRAP){
	    oid trapOid[MAX_OID_LEN];
	    int trapOidLen = pdu->enterprise_length;
	    struct sockaddr_in *agentIp = (struct sockaddr_in *)&pdu->agent_addr;
		if( ds_get_boolean(DS_APPLICATION_ID, DS_APP_NUMERIC_IP) )
			host = NULL;
		else
	    host = gethostbyaddr ((char *)&agentIp->sin_addr,
				  sizeof (agentIp->sin_addr), AF_INET);
	    if (pdu->trap_type == SNMP_TRAP_ENTERPRISESPECIFIC) {
		memcpy(trapOid, pdu->enterprise, sizeof(oid)*trapOidLen);
		if (trapOid[trapOidLen-1] != 0) trapOid[trapOidLen++] = 0;
		trapOid[trapOidLen++] = pdu->specific_type;
	    }
	    if (Print && (pdu->trap_type != SNMP_TRAP_AUTHFAIL || dropauth == 0)) {
	        if (trap1_fmt_str == NULL || trap1_fmt_str[0] == '\0')
	            (void) format_plain_trap (out_bfr, SPRINT_MAX_LEN, pdu);
	        else
		    (void) format_trap (out_bfr, SPRINT_MAX_LEN, trap1_fmt_str, pdu);
                snmp_log(LOG_INFO, "%s", out_bfr);
	    }
	    if (Syslog && (pdu->trap_type != SNMP_TRAP_AUTHFAIL || dropauth == 0)) {
	    	varbufidx=0;
	    	varbuf[varbufidx++]=','; varbuf[varbufidx++]=' ';
	    	varbuf[varbufidx]='\0';

	    	for(vars = pdu->variables; vars; vars = vars->next_variable) {
		    sprint_variable(varbuf+varbufidx, vars->name,
				    vars->name_length, vars);
		    

		    varbufidx += strlen(varbuf+varbufidx);
		    
		    varbuf[varbufidx++]=',';
		    varbuf[varbufidx++]=' ';
		    varbuf[varbufidx]='\0';
	    	}
	    	if ( varbufidx ) {
			varbufidx -= 2; varbuf[varbufidx]='\0';
	    	}
		if (pdu->trap_type == SNMP_TRAP_ENTERPRISESPECIFIC) {
		    sprint_objid(oid_buf, trapOid, trapOidLen);
		    cp = strrchr(oid_buf, '.');
		    if (cp) cp++;
		    else cp = oid_buf;
		    syslog(LOG_WARNING, "%s: %s Trap (%s) Uptime: %s%s",
                           inet_ntoa(agentIp->sin_addr),
                           trap_description(pdu->trap_type), cp,
                           uptime_string(pdu->time, buf), varbuf);
		} else {
		    syslog(LOG_WARNING, "%s: %s Trap (%ld) Uptime: %s%s",
                           inet_ntoa(agentIp->sin_addr),
                           trap_description(pdu->trap_type), pdu->specific_type,
                           uptime_string(pdu->time, buf), varbuf);
		}
	    }
	    if (pdu->trap_type == SNMP_TRAP_ENTERPRISESPECIFIC)
		Command = snmptrapd_get_traphandler(trapOid, trapOidLen);
	    else {
		trapoids[9] = pdu->trap_type+1;
		Command = snmptrapd_get_traphandler(trapoids, 10);
	    }
            if (Command)
		do_external(Command, host, pdu);
	} else if (pdu->command == SNMP_MSG_TRAP2
		   || pdu->command == SNMP_MSG_INFORM){
		if( ds_get_boolean(DS_APPLICATION_ID, DS_APP_NUMERIC_IP) )
			host = NULL;
		else
	    host = gethostbyaddr ((char *)&pduIp->sin_addr,
				  sizeof (pduIp->sin_addr), AF_INET);
	    if (Print) {
	        if (trap2_fmt_str == NULL || trap2_fmt_str[0] == '\0')
                    (void) format_trap (out_bfr, SPRINT_MAX_LEN,
                                        trap2_std_str, pdu);
                else
                    (void) format_trap (out_bfr, SPRINT_MAX_LEN,
                                        trap2_fmt_str, pdu);
                snmp_log(LOG_INFO, "%s", out_bfr);
	    }
	    if (Syslog) {
	    	varbufidx=0;
	    	varbuf[varbufidx]='\0';

	    	for (vars = pdu->variables; vars; vars = vars->next_variable) {
		    sprint_variable(varbuf+varbufidx, vars->name,
				    vars->name_length, vars);
		    

		    varbufidx += strlen(varbuf+varbufidx);
		    
		    varbuf[varbufidx++]=',';
		    varbuf[varbufidx++]=' ';
		    varbuf[varbufidx]='\0';
	    	}
	    	if ( varbufidx ) {
		    varbufidx -= 2; varbuf[varbufidx]='\0';
	    	}
		if( ds_get_boolean(DS_APPLICATION_ID, DS_APP_NUMERIC_IP) )
			host = NULL;
		else
		host = gethostbyaddr ((char *)&pduIp->sin_addr,
				      sizeof (pduIp->sin_addr), AF_INET);
		syslog(LOG_WARNING, "%s [%s]: Trap %s",
		       host ? host->h_name : inet_ntoa(pduIp->sin_addr),
		       inet_ntoa(pduIp->sin_addr), varbuf);
	    }
	    if (Event) {
		event_input(pdu->variables);
	    }
            for(vars = pdu->variables;
                vars &&
                snmp_oid_compare(vars->name, vars->name_length, snmptrapoid2,
                         sizeof(snmptrapoid2)/sizeof(oid));
                vars = vars->next_variable);
            if (vars && vars->type == ASN_OBJECT_ID) {
		Command = snmptrapd_get_traphandler(vars->val.objid,
						    vars->val_len/sizeof(oid));
		if (Command)
		    do_external(Command, host, pdu);
            }
	    if (pdu->command == SNMP_MSG_INFORM){
		if (!(reply = snmp_clone_pdu2(pdu, SNMP_MSG_RESPONSE))){
		    fprintf(stderr, "Couldn't clone PDU for response\n");
		    return 1;
		}
		reply->errstat = 0;
		reply->errindex = 0;
		reply->address = pdu->address;
		if (!snmp_send(session, reply)){
                    snmp_sess_perror("snmptrapd: Couldn't respond to inform pdu", session);
		    snmp_free_pdu(reply);
		}
	    }
	}
    } else if (op == TIMED_OUT){
	fprintf(stderr, "Timeout: This shouldn't happen!\n");
    }
    return 1;
}


static void parse_trap1_fmt(const char *token, char *line)
{
    trap1_fmt_str = strdup(line);
}


static void free_trap1_fmt(void)
{
    if (trap1_fmt_str != trap1_std_str) free ((char *)trap1_fmt_str);
    trap1_fmt_str = NULL;
}


static void parse_trap2_fmt(const char *token, char *line)
{
    trap2_fmt_str = strdup(line);
}


static void free_trap2_fmt(void)
{
    if (trap2_fmt_str != trap2_std_str) free ((char *)trap2_fmt_str);
    trap2_fmt_str = NULL;
}


void usage(void)
{
    fprintf(stderr,"Usage: snmptrapd [-h|-H|-V] [-D] [-p #] [-P] [-s] [-f] [-l [d0-7]] [-e] [-d] [-n] [-a] [-m <MIBS>] [-M <MIBDIRS]\n");
    fprintf(stderr,"UCD-snmp version: %s\n", VersionInfo);
    fprintf(stderr, "\n\
  -h        Print this help message and exit\n\
  -H        Read what can show up in config file\n\
  -V        Print version and exit\n\
  -q        Quick print mib display\n\
  -D[TOKEN,...] turn on debugging output, optionally by the list of TOKENs.\n\
  -p <port> Local port to listen from\n\
  -P        Print to standard output\n\
  -F \"...\" Use custom format for logging to standard output\n\
  -u PIDFILE create PIDFILE with process id\n\
  -e        Print Event # (rising/falling alarm], etc.\n\
  -s        Log syslog\n\
  -f        Stay in foreground (don't fork)\n\
  -l [d0-7 ]  Set syslog Facility to log daemon[d], log local 0(default) [1-7]\n\
  -d        Dump input/output packets\n\
  -n        Use numeric IP addresses instead of host names (no DNS)\n\
  -a        Ignore Authentication Failture traps.\n\
  -c CONFFILE Read CONFFILE as a configuration file.\n\
  -C        Don't read the default configuration files.\n\
  -m <MIBS>     Use MIBS list instead of the default mib list.\n\
  -M <MIBDIRS>  Use MIBDIRS as the location to look for mibs.\n\
  -O <OUTOPTS>  Toggle various options controlling output display\n");
  snmp_out_toggle_options_usage("\t\t  ", stderr);
}

RETSIGTYPE term_handler(int sig)
{
    running = 0;
}

#ifdef SIGHUP
RETSIGTYPE hup_handler(int sig)
{
    reconfig = 1;
    signal(SIGHUP, hup_handler);
}
#endif

int main(int argc, char *argv[])
{
    struct snmp_session sess, *session = &sess, *ss;
    int	arg;
    int count, numfds, block;
    fd_set fdset;
    struct timeval timeout, *tvp;
    int local_port = SNMP_TRAP_PORT;
    int dofork=1;
    char *cp;
    int tcp=0;
    char *trap1_fmt_str_remember = NULL;
#if HAVE_GETPID
	FILE           *PID;
        char *pid_file = NULL;
#endif

#ifdef notused
    in_addr_t myaddr;
    oid src[MAX_OID_LEN], dst[MAX_OID_LEN], context[MAX_OID_LEN];
    int srclen, dstlen, contextlen;
    char ctmp[300];
#endif

    
    register_config_handler("snmptrapd", "traphandle",
			    snmptrapd_traphandle, NULL,
			    "oid|\"default\" program [args ...] ");
    register_config_handler("snmptrapd", "createUser",
			    usm_parse_create_usmUser, NULL,
			    "username (MD5|SHA) passphrase [DES passphrase]");
    register_config_handler("snmptrapd", "usmUser",
                            usm_parse_config_usmUser, NULL, NULL);
    register_config_handler("snmptrapd", "format1",
			    parse_trap1_fmt, free_trap1_fmt,
			    "format");
    register_config_handler("snmptrapd", "format2",
			    parse_trap2_fmt, free_trap2_fmt,
			    "format");

  
  snmp_register_callback(SNMP_CALLBACK_LIBRARY, SNMP_CALLBACK_STORE_DATA,
                         usm_store_users, NULL);

#ifdef WIN32
    setvbuf (stdout, NULL, _IONBF, BUFSIZ);
#else
    setvbuf (stdout, NULL, _IOLBF, BUFSIZ);
#endif
    


    while ((arg = getopt(argc, argv, "VdnqRD:p:m:M:Po:O:esSafl:Hu:c:CF:T:")) != EOF){
	switch(arg) {
	case 'V':
            fprintf(stderr,"UCD-snmp version: %s\n", VersionInfo);
            exit(0);
            break;
	case 'd':
	    snmp_set_dump_packet(1);
	    break;
	case 'q':
	    snmp_set_quick_print(1);
	    break;
	case 'D':
            debug_register_tokens(optarg);
            snmp_set_do_debugging(1);
	    break;
        case 'p':
            local_port = atoi(optarg);
            break;
	case 'm':
	    setenv("MIBS", optarg, 1);
	    break;
	case 'M':
	    setenv("MIBDIRS", optarg, 1);
	    break;
        case 'T':
            if (strcasecmp(optarg,"TCP") == 0) {
                tcp = 1;
            } else if (strcasecmp(optarg,"UDP") == 0) {
                tcp = 0;
            } else {
                fprintf(stderr,"Unknown transport \"%s\" after -T flag.\n", optarg);
                exit(1);
            }
            break;
	case 'O':
	    cp = snmp_out_toggle_options(optarg);
	    if (cp != NULL) {
		fprintf(stderr, "Unknow output option passed to -O: %c\n", *cp);
		usage();
		exit(1);
	    }
	    break;
	case 'P':
            dofork = 0;
            snmp_enable_stderrlog();
	    Print++;
	    break;

        case 'o':
	    Print++;
            logfile = optarg;
            snmp_enable_filelog(optarg, 0);
            break;
            
	case 'e':
	    Event++;
	    break;
	case 's':
	    Syslog++;
	    break;
	case 'S':
	    snmp_set_suffix_only(2);
	    break;
	case 'a':
	    dropauth = 1;
	    break;
        case 'f':
	    dofork = 0;
	    break;
	case 'l':
	    switch(*optarg) {
	    case 'd':
		Facility = LOG_DAEMON; break;
	    case '0':
		Facility = LOG_LOCAL0; break;
	    case '1':
		Facility = LOG_LOCAL1; break;
	    case '2':
		Facility = LOG_LOCAL2; break;
	    case '3':
		Facility = LOG_LOCAL3; break;
	    case '4':
		Facility = LOG_LOCAL4; break;
	    case '5':
		Facility = LOG_LOCAL5; break;
	    case '6':
		Facility = LOG_LOCAL6; break;
	    case '7':
		Facility = LOG_LOCAL7; break;
	    default:
		fprintf(stderr,"invalid  syslog facility: -l %c\n", *optarg);
		usage();
		exit (1);
		break;
	    }
	    break;
        case 'H':
            init_snmp("snmptrapd");
            fprintf(stderr, "Configuration directives understood:\n");
	    read_config_print_usage("  ");
            exit(0);

#if HAVE_GETPID
        case 'u':
          pid_file = optarg;
          break;
#endif

        case 'c':
            ds_set_string(DS_LIBRARY_ID, DS_LIB_OPTIONALCONFIG, optarg);
            break;

        case 'C':
            ds_set_boolean(DS_LIBRARY_ID, DS_LIB_DONT_READ_CONFIGS, 1);
            break;

        case 'n':
            ds_set_boolean(DS_APPLICATION_ID, DS_APP_NUMERIC_IP, 1);
            break;

	case 'F':
	    trap1_fmt_str_remember = optarg;
	    break;

	default:
	    fprintf(stderr,"invalid option: -%c\n", arg);
	    usage();
	    exit (1);
	    break;
	}
    }

    if (optind != argc) {
	usage();
	exit(1);
    }

    if (!Print) Syslog = 1;

    
    init_snmp("snmptrapd");
    if (trap1_fmt_str_remember) {
        free_trap1_fmt();
        trap1_fmt_str = strdup(trap1_fmt_str_remember);
    }

#ifndef WIN32
    
    if (dofork) {
      int fd;

      switch (fork()) {
	case -1:
		fprintf(stderr,"bad fork - %s\n",strerror(errno));
		_exit(1);

	case 0:
		
		if (setsid() == -1) {
			fprintf(stderr,"bad setsid - %s\n",strerror(errno));
			_exit(1);
		}

        
		fd=open("/dev/null", O_RDWR);
		dup2(fd, STDIN_FILENO);
		dup2(fd, STDOUT_FILENO);
		dup2(fd, STDERR_FILENO);
		close(fd);
		break;

	default:
		_exit(0);
      }
    }
#endif	
#if HAVE_GETPID
    if (pid_file != NULL) {
        if ((PID = fopen(pid_file, "w")) == NULL) {
            snmp_log_perror("fopen");
            exit(1);
        }
        fprintf(PID, "%d\n", (int)getpid());
        fclose(PID);
    }
#endif

    if (Syslog) {
	
	init_syslog();
    }
    if (Print) {
	struct tm *tm;
	time_t timer;
	time (&timer);
	tm = localtime (&timer);
        snmp_log(LOG_INFO,
                 "%.4d-%.2d-%.2d %.2d:%.2d:%.2d UCD-snmp version %s Started.\n",
                 tm->tm_year+1900, tm->tm_mon+1, tm->tm_mday,
                 tm->tm_hour, tm->tm_min, tm->tm_sec,
                 VersionInfo);
    }


    snmp_sess_init(session);
    session->peername = SNMP_DEFAULT_PEERNAME; 
    session->version = SNMP_DEFAULT_VERSION;

    session->community_len = SNMP_DEFAULT_COMMUNITY_LEN;

    session->retries = SNMP_DEFAULT_RETRIES;
    session->timeout = SNMP_DEFAULT_TIMEOUT;

    session->local_port = local_port;

    session->callback = snmp_input;
    session->callback_magic = NULL;
    session->authenticator = NULL;
    sess.isAuthoritative = SNMP_SESS_UNKNOWNAUTH;
    if (tcp)
        session->flags |= SNMP_FLAGS_STREAM_SOCKET;

    SOCK_STARTUP;
    ss = snmp_open( session );
    if (ss == NULL){
        snmp_sess_perror("snmptrapd", session);
        if (Syslog) {
	    syslog(LOG_ERR,"couldn't open snmp - %m");
	}
	SOCK_CLEANUP;
	exit(1);
    }

    signal(SIGTERM, term_handler);
#ifdef SIGHUP
    signal(SIGHUP, hup_handler);
#endif
    signal(SIGINT, term_handler);

    while (running) {
	if (reconfig) {
	    if (Print) {
		struct tm *tm;
		time_t timer;
		time (&timer);
		tm = localtime (&timer);
		printf("%.4d-%.2d-%.2d %.2d:%.2d:%.2d UCD-snmp version %s Reconfigured.\n",
		       tm->tm_year+1900, tm->tm_mon+1, tm->tm_mday,
		       tm->tm_hour, tm->tm_min, tm->tm_sec,
		       VersionInfo);
	    }
	    if (Syslog)
		syslog(LOG_INFO, "Snmptrapd reconfiguring");
	    update_config();
            if (trap1_fmt_str_remember) {
                free_trap1_fmt();
                trap1_fmt_str = strdup(trap1_fmt_str_remember);
            }
	    reconfig = 0;
	}
	numfds = 0;
	FD_ZERO(&fdset);
	block = 0;
	tvp = &timeout;
	timerclear(tvp);
	tvp->tv_sec = 5;
	snmp_select_info(&numfds, &fdset, tvp, &block);
	if (block == 1)
	    tvp = NULL;	
	count = select(numfds, &fdset, 0, 0, tvp);
	gettimeofday(&Now, 0);
	if (count > 0){
	    snmp_read(&fdset);
	} else switch(count){
	    case 0:
		snmp_timeout();
		break;
	    case -1:
		if (errno == EINTR)
			continue;
	        snmp_log_perror("select");
		running = 0;
		break;
	    default:
		fprintf(stderr, "select returned %d\n", count);
		running = 0;
	}
    }

    if (Print) {
	struct tm *tm;
	time_t timer;
	time (&timer);
	tm = localtime (&timer);
	printf("%.4d-%.2d-%.2d %.2d:%.2d:%.2d UCD-snmp version %s Stopped.\n",
	       tm->tm_year+1900, tm->tm_mon+1, tm->tm_mday,
	       tm->tm_hour, tm->tm_min, tm->tm_sec,
	       VersionInfo);
    }
    if (Syslog)
	syslog(LOG_INFO, "Stopping snmptrapd");

    snmp_close(ss);
    snmp_shutdown("snmptrapd");
    SOCK_CLEANUP;
    return 0;
}

void
init_syslog(void)
{
    



    openlog("snmptrapd", LOG_CONS|LOG_PID, Facility);
    syslog(LOG_INFO, "Starting snmptrapd %s", VersionInfo);
}








void update_config(void)
{
    free_config();
    read_configs();
}


#if !defined(HAVE_GETDTABLESIZE) && !defined(WIN32)
#include <sys/resource.h>
int getdtablesize(void)
{
  struct rlimit rl;
  getrlimit(RLIMIT_NOFILE, &rl);
  return( rl.rlim_cur );
}
#endif
