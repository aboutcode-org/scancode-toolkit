/***********************************************************************/
/* Open Visualization Data Explorer                                    */
/* (C) Copyright IBM Corp. 1989,1999                                   */
/* ALL RIGHTS RESERVED                                                 */
/* This code licensed under the                                        */
/*    "IBM PUBLIC LICENSE - Open Visualization Data Explorer"          */
/***********************************************************************/

#include <dxconfig.h>


/* this has to be before the ifdef, because it defines DXD_LICENSED_VERSION 
 * if this arch supports the license manager.
 */
#include <dx/dx.h>

#if defined(HAVE_CRYPT_H)
#include <crypt.h>
#endif

#if defined(HAVE_TIME_H)
#include <time.h>
#endif

#include <stdio.h>

#if defined(HAVE_STRING_H)
#include <string.h>
#define DXD_STLIB_INCLUDES
#endif

#if defined(HAVE_TIME_H)
#include <time.h>
#endif

#if defined(HAVE_STDLIB_H)
#include <stdlib.h>
#endif

#if defined(HAVE_STRING_H)
#include <string.h>
#endif

#if defined(HAVE_SYS_STAT_H)
#include <sys/stat.h>
#endif

#if defined(HAVE_SYS_TYPES_H)
#include <sys/types.h>
#endif

#if defined(HAVE_SYS_TIMEB_H)
#include <sys/timeb.h>
#endif

#if defined(HAVE_SYS_TIME_H)
#include <sys/time.h>
#endif

#include "config.h"

#ifdef DXD_LICENSED_VERSION
#include "license.h"

#define NL_LIC  1
#define CON_LIC 2

static int shadow_fd_dxlic = -1;
static int shadow_fd_mplic = -1;
static int trial_file_exists  = FALSE; 
static int MPlic_tried	   = FALSE;
struct lic_info {
    int child;
    int type;
};
struct lic_info dxlic = {-1, -1};
struct lic_info mplic = {-1, -1};

static Error system_hostname(char *buf);
static Error checkexp(char *root, lictype ltype);
static char messagebuf[1024];

int _dxfCheckLicenseChild(int child)
{
    if ( child == dxlic.child) {
      if(dxlic.type == NL_LIC)
          return(0);
      return(child);
    }
    else if ( child == mplic.child) {
      if(mplic.type == NL_LIC)
          return(0);
      return(child);
    }
    else
        return(-1);
}

Error ExLicenseDied(int fd, Pointer junk)
{
    /* We should only be called if dxshadow dies,  */
    /* then send UNAUTHORIZED MESSAGE to UI        */
    /* or die if were in script mode 		 */
    

    DXRegisterInputHandler(NULL, fd, NULL);

    if ( fd == shadow_fd_dxlic)
      DXMessage("License Error: Exec lost DX license and is terminating\n");
    else if ( fd == shadow_fd_mplic)
      DXMessage("License Error: Exec lost MP license and is terminating\n");
    else
      DXMessage("License Error: unknown license error\n");

    _dxd_ExHasLicense = FALSE;
    if (_dxd_exRemote) {
	DXUIMessage("LICENSE","UNAUTHORIZED");
	return OK;
    }
    
    if(_dxd_exTerminating) {
        *_dxd_exTerminating = TRUE;
        return (-1);
    }
    /* when _dxd_exTerminating is NULL we are being called from the */
    /* developer's kit, just exit */
    exit(-1);
    
    /* NOTREACHED */
}

void _dxf_ExReleaseLicense()
{
    if(shadow_fd_dxlic >= 0)
        close(shadow_fd_dxlic);
    if(shadow_fd_mplic >= 0)
        close(shadow_fd_mplic);
}


Error ExGetLicense(lictype ltype, int forceNetLS)
{
    int i;
    int child;
    int pid;
    int in[2],out[2];
    char remname[256];
    char auth_msg[AUTH_MSG_LEN];
    char ckey[9];
    char c_buf[32],p_buf[32];	/* hold crypted msgs for comaparison */
    static char envbuf[32];	/* static 'cause it goes into the env */
    char salt[3];
    time_t timenow;
   
 
    char *root = getenv ("DXEXECROOT");
    if (root == NULL) 
	root = getenv ("DXROOT");
    if (root == NULL)
	root = "/usr/local/dx";

    if (ltype == MPLIC) {
	MPlic_tried = TRUE;
	forceNetLS = FALSE;
    }
    

    strcpy(messagebuf,"");

    if (checkexp (root, ltype))    /* check for an old syle trial license */
	return OK;
    else if ( ltype == MPLIC && trial_file_exists )  /* don't try to get an MP floating lic if DX lic */ 
	return ERROR;				/* is a uniprocessor nodelocked */  
	
    /* didn't find a trial license so spawn the NetLS licensing process */
    
    /* Set up two pipes */
    if (pipe(in) < 0) {
	perror("pipe(in)");
	exit (-1);
    }
    if (pipe(out) < 0) {
	perror("pipe(out)");
	exit (-1);
    }
    
    timenow = time(NULL);
    
    sprintf(envbuf,"_DX_%d=", getpid());
    sprintf(c_buf,"%x", timenow);
    strcat(envbuf, c_buf+4);
    putenv(envbuf);
   
#if DXD_HAS_VFORK
    /* if it's available, use vfork() so we don't copy the entire data
     * segment when forking - we are going to exec right away
     * anyway so we aren't going to use anything from the data seg.
     */
    pid = vfork();
#else
    pid = fork();
#endif
    child = 0xFFFF & pid;       /* force "child id" to be < 4 hex chars */
	
    if (pid == 0) {	/* Child */
	char arg1[32], arg3[32];
		
	if (in[1])
	    close (in[1]);
	if (out[0])
	    close (out[0]);
	if (dup2(in[0], 0) < 0) {
	    perror("dup2");
	    exit (-1);
	}
	if (dup2(out[1], 1) < 0) {
	    perror("dup2");
	    exit (-1);
	}
	
	/* should we close other file descriptors here ? */
	
	if (getenv("DXSHADOW")) 
	    strcpy(remname,getenv("DXSHADOW"));
	else 
	    sprintf(remname,"%s/bin_%s/dxshadow",root,DXD_ARCHNAME);

	switch (ltype) {
	    case MPLIC:	strcpy(arg1,"-mp");	break;
	    case DXLIC:	strcpy(arg1,"-dev");	break;
	    case RTLIC:	strcpy(arg1,"-rt");	break;
	    case RTLIBLIC:	strcpy(arg1,"-rtlib");	break;
	    default:    sprintf(arg1,"%d",ltype); break;
	}
	if (forceNetLS)
	    strcat(arg1,"only");

	sprintf(arg3,"%d.%d.%d", DXD_VERSION, DXD_RELEASE, DXD_MODIFICATION);
	execlp(remname, "dxshadow", arg1 , "-version", arg3 ,NULL);

	perror("Could not execute license process");
	exit (-1);
    }
    else if (pid > 0) {   /* parent */
 	int netls_type;
	const char *lic_name;
	if (in[0]) 
	    close (in[0]);
	if (out[1]) 
	    close (out[1]);

	/* wait for response from the child */
	i = read (out[0], auth_msg, AUTH_MSG_LEN);
	if (i != AUTH_MSG_LEN) {
	    perror ("License Error:Bad message read from dxshadow");
	    exit (-1);
	}
	
        if (ltype == MPLIC) 
            mplic.child = child;
        else
            dxlic.child = child;

	/* decipher license message here */
	
	child = (child < 4096) ? (child+4096)
	                       : (child);       /* forces to be 4 0x chars */
	
	strcpy(ckey, c_buf+4);
	sprintf(ckey+4, "%x", child);
	
	salt[0] = '7';
	salt[1] = 'q';
	salt[2] = '\0';
	
	strcpy(p_buf, crypt(ckey, salt));;
	
	for(i=0;i<13;i++)
	    c_buf[i] = auth_msg[(i*29)+5];
	c_buf[13] = '\0';
	
	if (strcmp(c_buf, p_buf)) {
	    /* Bad message from child */
	    perror("License Error: invalid message from license process.");
	    exit (-1);
	}

	/* valid message so we extract license type */
	for(i=0; i<8; i++)
	    c_buf[i] = auth_msg[(i*3)+37];
	
	c_buf[8] = '\0';
	sscanf(c_buf, "%x", &i);
	netls_type = 0xffff & (i^child);
	i = i >> 16;
	ltype = 0xffff & (i^child);
#if LIC_DEBUG 
	fprintf(stderr,"Received...\n"
		"c_buf = '%s', ltype = 0x%x, netls_type = 0x%x, mask = 0x%x\n",
				c_buf,ltype,netls_type,child);
#endif

   	switch (ltype) {
	    case DXLIC: lic_name = "DX development"; break;
	    case RTLIC: lic_name = "DX run-time"; break;
	    case MPLIC: lic_name = "MP"; break;
	    case RTLIBLIC: lic_name = "DX Library run-time"; break;
	    default: return FALSE; break;	/* bad license */ 
  	}

	switch (netls_type) {
	    
	  case GOT_NODELOCKED:
	   
	    if (ltype == MPLIC) {
		sprintf(messagebuf,"Exec got nodelocked %s license.",lic_name);
                mplic.type = NL_LIC;
	    } else {
		DXMessage("Exec got nodelocked %s license.", lic_name);
                dxlic.type = NL_LIC;
		_dxd_ExHasLicense = TRUE;
	    }
	    return OK;
		
	  case GOT_CONCURRENT:
	    /* do concurrent stuff here */
        
	    if (ltype == MPLIC) {
	        shadow_fd_mplic = out[0];
		sprintf(messagebuf,"Exec got concurrent use %s license.",
							lic_name);	
		/* we save message and will register input handler 
		 * in ExLicenseFinish 
		 * after it's safe to call DX routines 
		 */
                mplic.type = CON_LIC;
	    } else {
		DXMessage("Exec got concurrent use %s license.",lic_name);
	        shadow_fd_dxlic = out[0];
		DXRegisterInputHandler(ExLicenseDied,shadow_fd_dxlic,NULL);
                dxlic.type = CON_LIC;
		_dxd_ExHasLicense = TRUE;
   	    }

	    return OK;
	    
	  case GOT_NONE:
	    
	    if (ltype == MPLIC)
	      sprintf(messagebuf,"Exec could not get a %s license,"
				" running in uniprocessor mode.",lic_name);
            else 
	      DXMessage("Exec could not get a %s license.",lic_name);
	    return ERROR;
	    
	  default:
	    /* invalid license type */
	    perror("License Error: Invalid message from license process.");
	    exit (-1);
	}
    }
    else {
	perror("fork");
	exit (-1);
    }

    /* NOTREACHED */
}  


/* finish the stuff that needs to happen after DXinit */
/* this is because GetLicense(MPLIC) is called before */
/* DXinit					      */

Error ExLicenseFinish() 
{

	if(!MPlic_tried)
	  return OK;
	
	if (shadow_fd_mplic >= 0)
	  DXRegisterInputHandler(ExLicenseDied,shadow_fd_mplic,NULL);

	if(_dxd_exRemoteSlave)
	  DXMessage("Host %s:%s",_dxd_exHostName,messagebuf);
	else
	  DXMessage(messagebuf);

	return OK;
}

Error ExGetPrimaryLicense()
{
    lictype lic;
    int force;

    if (_dxd_exForcedLicense == NOLIC) {
	lic = DXLIC;
	force = FALSE;
    } else {
	lic = _dxd_exForcedLicense;
	force = TRUE;
    }
    return ExGetLicense(lic,force);
}


static Error checkexp(char *root, lictype ltype)
{
    char   key[KEY_LEN];
    char   cryptHost[HOST_LEN];
    char   cryptTime[HOST_LEN];
    char   host[HOST_LEN];
    time_t timeOut;
    int    i;
    char  *myCryptHost;
    int    host_match;
    time_t timenow;
    char   fileName[HOST_LEN];
    char  *key_location, key_location_buf[1024];
    char  *cp;
    int    suppresslicmsg = 0;
    FILE   *f;
    
    for (i = 0; i < sizeof(key); ++i)
	key[i] = '\0';
    
    if (!system_hostname(host))
	return ERROR;

    timenow = time(NULL);
    
    /* if the DXSTARTUP env var is set to one, we are running
     * with a temp oneday trial key created by the startup ui.
     * suppress the messages about a trial key or when it expires
     * so the user can't tell how we are doing this.
     */
    cp = getenv("DXSTARTUP");
    if (cp && (atoi(cp) == 1))
	suppresslicmsg++;

  if (getenv("DXTRIALKEY")) {
        char *k = getenv("DXTRIALKEY");
	key_location = "DXTRIALKEY environment variable";
        strncpy(key,k,27);
        key[27] = '\0'; /* Make sure it is terminated */
  } else {
      char *fname;
      fname = getenv("DXTRIALKEYFILE");
      if (!fname) {
          sprintf(fileName, "%s/expiration", root);
          fname = fileName;
      }
      f = fopen(fname, "r");
      if (f)  {
	sprintf(key_location_buf,"file %s",fname);	
	key_location = key_location_buf;
        fgets(key, 27, f);
        fclose(f);
      } else {
        return ERROR;
      }
  }

    if (!trial_file_exists) {
        if (ltype == MPLIC) {
	  char buf[1024];
	  sprintf(buf,"Found Data Explorer trial password in %s.\n",
							key_location);
	  if (!suppresslicmsg)
	      strcat(messagebuf,buf);
	  trial_file_exists = TRUE;
	} else {
	    if (!suppresslicmsg)
	       DXMessage("Found Data Explorer trial password in %s.",key_location);
	}
    }
    
    
    if (strlen(key) != 26) {
        if (ltype == MPLIC) 
	  strcat(messagebuf,"You are running an expired Trial version of Data Explorer.\n");
	else
	  DXMessage("You are running an expired Trial version of Data Explorer.");

	return ERROR;
    }
    
    for (i = 0; i < 13; ++i) {
	cryptHost[i] = key[2 * i];
	cryptTime[i] = key[2 * i + 1];
    }
    cryptHost[i] = key[2 * i] = '\0';
    cryptTime[i] = key[2 * i + 1] = '\0';
    


    if (ltype == MPLIC) {
    	if (cryptTime[0] != 'A' ||
	    cryptTime[10] != '9' ||
	    cryptTime[12] != 'D') {
	    strcat(messagebuf,"You are running an Expired trial version of Data Explorer.\n");
	    return ERROR;
    	}
    	if (cryptTime[1] != 'm' ||
	    cryptTime[11] != 'l' ) { 
	    strcat(messagebuf,"Single processor trial key found, MP will not be enabled.\n");
	    return ERROR;
	}
    }
    else if (cryptTime[0] != 'A' || 
	cryptTime[10] != '9' || 
	cryptTime[12] != 'D') {
	DXMessage("You are running an Expired trial version of Data Explorer.");
	return ERROR;
    }
    
    myCryptHost = crypt(host, KEY1);
    host_match = strcmp(cryptHost, myCryptHost) == 0;
    if (!host_match) {
        myCryptHost = crypt(ANYWHERE_HOSTID, KEY1);
        host_match = strcmp(cryptHost, myCryptHost) == 0;
    }
    if (!host_match) {
        if (ltype == MPLIC)
	  strcat(messagebuf,
		"you are running a trial version of Data Explorer"
		" on an unlicensed host\n");
	else
	  DXMessage("You are running a trial version of Data Explorer"
		" on an unlicensed host.");
	return ERROR;

    }
    
    if(cryptTime[1]=='s')
      sscanf(cryptTime, "As%08x95D", &timeOut); 
    else if (cryptTime[1]=='m')
      sscanf(cryptTime, "Am%08x9lD", &timeOut);
      

    timeOut ^= 0x12345678;
    
    if (timenow > timeOut) {
        if (ltype == MPLIC) { 
	  strcat(messagebuf,
	    "You are running an expired trial version of Data Explorer.\n");
	} else {
	  DXMessage("You are running an expired trial version of Data "
			"Explorer.");
    	  DXMessage("This trial key expired on %s", ctime(&timeOut));
	}
	return ERROR;
    }
    
    if (ltype != MPLIC) {
	if (!suppresslicmsg)
	    DXMessage("This trial key expires on %s", ctime(&timeOut));
        _dxd_ExHasLicense = TRUE;
    }

    return OK;
}




/* system specific way to return the hostname we use for the license
 */

#if defined(alphax)
#include <stdio.h>              /* standard I/O */
#include <errno.h>              /* error numbers */
#endif

#if defined(HAVE_SYS_IOCTL_H)
#include <sys/ioctl.h>          /* ioctls */
#endif

#if defined(HAVE_NET_IF_H)
#include <net/if.h>             /* generic interface structures */
#endif

#if defined(HAVE_SYS_SYSTEMINFO_H)
#include <sys/systeminfo.h>     /* maybe someday this will be implemented ...arg! */
#endif


#if defined(aviion) || defined(solaris) 
#include <sys/systeminfo.h>
#endif
#if defined(ibm6000) || defined(hp700)
#include <sys/utsname.h>
#endif

static Error system_hostname(char *host)
{

#if defined(ibm6000) || defined(hp700)
    struct utsname name;
#endif
#if defined(indigo) || defined(sun4) ||  defined(sgi) 
    long   name;
#endif

#if ibm6000
#define FOUND_ID 1
    uname(&name);
    name.machine[10] = '\0';
    strcpy(host, name.machine+2);
#endif
#if hp700
#define FOUND_ID 1
    uname(&name);
    name.idnumber[10] = '\0';
    strcpy(host, name.idnumber+2);
#endif
#if indigo || sgi        /* sgi does not like #if...#elif..#endif construct */
#define FOUND_ID 1
    name = sysid(NULL);
    sprintf(host, "%d", name);
    strcpy(host, host+2);
#endif
#if sun4 
#define FOUND_ID 1
    name = gethostid();
    sprintf(host, "%x", name);
#endif
#if aviion
#define FOUND_ID 1
    sysinfo(SI_HW_SERIAL,host,301);
#endif
#if solaris
#define FOUND_ID 1
    sysinfo(SI_HW_SERIAL,host,301);
    sprintf(host, "%x", atol(host));
#endif
#if alphax
#define FOUND_ID 1
    {
    char *device;
    char *dflt_devices[] = {"tu0","ln0", NULL };
    int s,i				/* On Alpha OSF/1 we use ethernet */;

    /* Get a socket */
    s = socket(AF_INET,SOCK_DGRAM,0);
    strcpy(host,"");
    if (s < 0) {
        perror("socket");
    } else {
	for (i=0, device=(char*)getenv("DXKEYDEVICE"); dflt_devices[i]; i++) {
	    static   struct  ifdevea  devea;  /* MAC address from and ioctl()*/
	    char *dev, buf[32];
	    if (!device) 
		dev = dflt_devices[i];
	    else
		dev = device;
	    strcpy(devea.ifr_name,dev);
	    if (ioctl(s,SIOCRPHYSADDR,&devea) >= 0)  {
		strcpy(host,"");
		for (i = 2; i < 6; i++){
		    sprintf(buf,"%x", devea.default_pa[i] );
		    strcat(host,buf);
		}
		break;
	    } 
	    if (device) break;
	}
	close(s);
    }
  }
#endif

#if !defined(FOUND_ID)
    /* Trial version not supported on this architecture */
    return ERROR;
#else
# undef FOUND_ID
#endif
    
    return OK;
}

#endif /* DXD_LICENSED_VERSION */
