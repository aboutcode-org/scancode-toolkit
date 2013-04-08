/*                                                                                                            
 * Copyright (c) Members of the EGEE Collaboration. 2004.
 * See http://eu-egee.org/partners/ for details on the copyright holders.
 * For license conditions see the license file or
 * http://eu-egee.org/license.html
 */

/*                                                                                                            
 * Copyright (c) 2001 EU DataGrid.                                                                             
 * For license conditions see http://www.eu-datagrid.org/license.html                                          
 *
 * Copyright (c) 2008 by
 *     Oscar Koeroo <okoeroo@nikhef.nl>,
 *     David Groep <davidg@nikhef.nl>,
 *     NIKHEF Amsterdam, the Netherlands
 */

/*!
    \file   scar_log.h
    \brief  Logging API for the SCAR plugins and SCAR itself
    \author Oscar Koeroo for EGEE

    This header contains the declarations of the SCAR logging functions
    The SCAR plugins can use this API to write output to the SCAR logging
    devices.
    -# scar_log(): Log to SCAR logging devices.
    -# scar_log_debug(): Produce debugging output.
    \ingroup APIforLcmapsPlugins
*/

#ifndef SCAR_LOG_H
#define SCAR_LOG_H

/******************************************************************************
                             Include header files
******************************************************************************/
#include <syslog.h>

/******************************************************************************
 *                            Module definition
 *****************************************************************************/

#define MAX_TIME_STRING_SIZE 64


#define MAX_LOG_BUFFER_SIZE 2048 /*!< Maximum logging buffer size, length of log
                                      may not exceed this number \internal */

#define DO_USRLOG           ((unsigned short)0x0001) /*!< flag to indicate that
                                      user logging has to be done \internal */
#define DO_SYSLOG           ((unsigned short)0x0002) /*!< flag to indicate that
                                      syslogging has to be done \internal */
#define DO_ERRLOG           ((unsigned short)0x0004) /*!< flag to indicate that
                                      stderr logging has to be done \internal */

/******************************************************************************
Function:       scar_log()
Description:    Log information to file and or syslog
Parameters:
                prty:    syslog priority (if 0 don't syslog)
                fmt:     string format
Returns:        0 succes
                1 failure
******************************************************************************/
extern int scar_log(
        int prty,
        char * fmt,
        ...
);

/******************************************************************************
Function:       scar_log_debug()
Description:    Print debugging information
Parameters:
                debug_lvl: debugging level
                fmt:       string format
Returns:        0 succes
                1 failure
******************************************************************************/
extern int scar_log_debug(
        int debug_lvl,
        char * fmt,
        ...
);

/******************************************************************************
Function:       scar_log_time()
Description:    Log information to file and or syslog with a timestamp
Parameters:
                prty:    syslog priority (if 0 don't syslog)
                fmt:     string format
Returns:        0 succes
                1 failure
******************************************************************************/
extern int scar_log_time(
        int prty, 
        char * fmt, 
        ...
);

/******************************************************************************
Function:       scar_log_a_string()
Description:    Log a string according to the passed format to file and or syslog
Parameters:
                prty:       syslog priority (if 0 don't syslog)
                fmt:        string format
                the_string: the string
Returns:        0 succes
                1 failure
******************************************************************************/
extern int scar_log_a_string(
        int prty,
        char * fmt,
        char * the_string
);

/******************************************************************************
Function:       scar_log_a_string_debug()
Description:    Print debugging information
Parameters:
                debug_lvl:  debugging level
                fmt:        string format
                the_string: the string
Returns:        0 succes
                1 failure
******************************************************************************/
extern int scar_log_a_string_debug(
        int debug_lvl,
        char * fmt,
        char * the_string
);


/******************************************************************************
Function:       scas_log_set_time_indicator()
Description:    Resets the log indicator to the current time
                When set, the logstring will be prefixed by this string
Parameters:
Returns:        
                
******************************************************************************/
int scar_log_set_time_indicator (void);


/******************************************************************************
Function:       scar_get_log_file_pointer()
Description:    Get the opened file pointer
Parameters:
Returns:        0 succes
                1 failure
******************************************************************************/
extern FILE * scar_get_log_file_pointer(void);


/******************************************************************************
Function:       scar_get_log_type (void);
Description:    Get the log type identification number
Parameters:
Returns:        0 succes
                1 failure
******************************************************************************/
extern unsigned short scar_get_log_type (void);


/******************************************************************************
Function:       scar_set_log_line_prefix (char * prefix)
Description:    Get the log type identification number
Parameters:
Returns:        0 succes
                1 failure
******************************************************************************/
void scar_set_log_line_prefix (char * prefix);


#endif /* SCAR_LOG_H */

