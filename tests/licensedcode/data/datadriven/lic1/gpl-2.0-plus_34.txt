static const char CVSID[] = "$Id: windowTitle.c,v 1.12 2004/07/18 22:31:00 yooden Exp $";
/*******************************************************************************
*                                                                              *
* windowTitle.c -- Nirvana Editor window title customization                   *
*                                                                              *
* Copyright (C) 2001, Arne Forlie                                              *
*                                                                              *
* This is free software; you can redistribute it and/or modify it under the    *
* terms of the GNU General Public License as published by the Free Software    *
* Foundation; either version 2 of the License, or (at your option) any later   *
* version.                                                                     *
*                                                                              *
* This software is distributed in the hope that it will be useful, but WITHOUT *
* ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        *
* FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License *
* for more details.                                                            *
*                                                                              *
* You should have received a copy of the GNU General Public License along with *
* software; if not, write to the Free Software Foundation, Inc., 59 Temple     *
* Place, Suite 330, Boston, MA  02111-1307 USA                                 *
*                                                                              *
* Nirvana Text Editor                                                          *
* July 31, 2001                                                                *
*                                                                              *
* Written by Arne Forlie, http://arne.forlie.com                               *
*                                                                              *
*******************************************************************************/

#ifdef HAVE_CONFIG_H
#include "../config.h"
#endif

#include "windowTitle.h"
#include "textBuf.h"
#include "nedit.h"
#include "preferences.h"
#include "help.h"
#include "../util/prefFile.h"
#include "../util/misc.h"
#include "../util/DialogF.h"
#include "../util/utils.h"
#include "../util/fileUtils.h"

#include <stdlib.h>
#include <stdio.h>
#include <ctype.h>
#include <string.h>
#ifdef VMS
#include "../util/VMSparam.h"
#else
#ifndef __MVS__
#include <sys/param.h>
#endif
#include "../util/clearcase.h"
#endif /*VMS*/

#include <Xm/Xm.h>
#include <Xm/SelectioB.h>
#include <Xm/Form.h>
#include <Xm/List.h>
#include <Xm/SeparatoG.h>
#include <Xm/LabelG.h>
#include <Xm/PushBG.h>
#include <Xm/PushB.h>
#include <Xm/ToggleBG.h>
#include <Xm/ToggleB.h>
#include <Xm/RowColumn.h>
#include <Xm/CascadeBG.h>
#include <Xm/Frame.h>
#include <Xm/Text.h>
#include <Xm/TextF.h>

#ifdef HAVE_DEBUG_H
#include "../debug.h"
#endif


#define WINDOWTITLE_MAX_LEN 500

/* Customize window title dialog information */
static struct {
    Widget      form;
    Widget      shell;
    WindowInfo* window;
    Widget      previewW;
    Widget      formatW;
    
    Widget      ccW;
    Widget      fileW;
    Widget      hostW;
    Widget      dirW;
    Widget      statusW;
    Widget      shortStatusW;
    Widget      serverW;
    Widget      nameW;
    Widget      mdirW;
    Widget      ndirW;
    
    Widget      oDirW;
    Widget      oCcViewTagW;
    Widget      oServerNameW;
    Widget      oFileChangedW;
    Widget      oFileLockedW;
    Widget      oFileReadOnlyW;
    Widget      oServerEqualViewW;
    
    char	filename[MAXPATHLEN];
    char	path[MAXPATHLEN];
    char	viewTag[MAXPATHLEN];
    char	serverName[MAXPATHLEN];
    int         isServer;
    int         filenameSet;
    int         lockReasons;
    int         fileChanged;
    
    int 	suppressFormatUpdate;
} etDialog = {NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,
              NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,
              NULL,NULL,"","","","",0,0,0,0,0};



static char* removeSequence(char* sourcePtr, char c)
{
    while (*sourcePtr == c) {
        sourcePtr++;
    }
    return(sourcePtr);
}


/*
** Two functions for performing safe insertions into a finite
** size buffer so that we don't get any memory overruns.
*/
static char* safeStrCpy(char* dest, char* destEnd, const char* source)
{
   int len = (int)strlen(source);
   if (len <= (destEnd - dest)) {
       strcpy(dest, source);
       return(dest + len);
   }
   else {
       strncpy(dest, source, destEnd - dest);
       *destEnd = '\0';
       return(destEnd);
   }
}

static char* safeCharAdd(char* dest, char* destEnd, char c)
{
   if (destEnd - dest > 0)
   {
      *dest++ = c;
      *dest = '\0';
   }
   return(dest);
}

/*
** Remove empty paranthesis pairs and multiple spaces in a row
** with one space.
** Also remove leading and trailing spaces and dashes.
*/
static void compressWindowTitle(char *title)
{
    /* Compress the title */
    int modified;
    do {
        char *sourcePtr = title;
        char *destPtr   = sourcePtr;
        char c = *sourcePtr++;

        modified = False;

        /* Remove leading spaces and dashes */
        while (c == ' ' || c == '-') {
            c= *sourcePtr++;
        }

        /* Remove empty constructs */
        while (c != '\0') {
            switch (c) {
                /* remove sequences */
                case ' ':
                case '-':
                    sourcePtr = removeSequence(sourcePtr, c);
                    *destPtr++ = c; /* leave one */
                    break;

                /* remove empty paranthesis pairs */
                case '(':
                    if (*sourcePtr == ')') {
                        modified = True;
                        sourcePtr++;
                    }
                    else *destPtr++ = c;
                    sourcePtr = removeSequence(sourcePtr, ' ');
                    break;

                case '[':
                    if (*sourcePtr == ']') {
                        modified = True;
                        sourcePtr++;
                    }
                    else *destPtr++ = c;
                    sourcePtr = removeSequence(sourcePtr, ' ');
                    break;

                case '{':
                    if (*sourcePtr == '}') {
                        modified = True;
                        sourcePtr++;
                    }
                    else *destPtr++ = c;
                    sourcePtr = removeSequence(sourcePtr, ' ');
                    break;
                    
                default:
                    *destPtr++ = c;
                    break;
            }
            c = *sourcePtr++;
            *destPtr = '\0';
        }

        /* Remove trailing spaces and dashes */
        while (destPtr-- > title) {
            if (*destPtr != ' ' && *destPtr != '-')
                break;
            *destPtr = '\0';
        }
    } while (modified == True);
}


/*
** Format the windows title using a printf like formatting string.
** The following flags are recognised:
**  %c    : ClearCase view tag
**  %s    : server name
**  %[n]d : directory, with one optional digit specifying the max number
**          of trailing directory components to display. Skipped components are
**          replaced by an ellipsis (...).
**  %f    : file name
**  %h    : host name
**  %S    : file status
**  %u    : user name
**
**  if the ClearCase view tag and server name are identical, only the first one
**  specified in the formatting string will be displayed. 
*/
char *FormatWindowTitle(const char* filename,
                        const char* path,
                        const char* clearCaseViewTag,
                        const char* serverName,
                        int isServer,
                        int filenameSet,
                        int lockReasons,
                        int fileChanged,
                        const char* titleFormat)
{
    static char title[WINDOWTITLE_MAX_LEN];
    char *titlePtr = title;
    char* titleEnd = title + WINDOWTITLE_MAX_LEN - 1;
    
    
    /* Flags to supress one of these if both are specified and they are identical */
    int serverNameSeen = False;
    int clearCaseViewTagSeen = False;
    
    int fileNamePresent = False;
    int hostNamePresent = False;
    int userNamePresent = False;
    int serverNamePresent = False;
    int clearCasePresent = False;
    int fileStatusPresent = False;
    int dirNamePresent = False;
    int noOfComponents = -1;
    int shortStatus = False;
    
    *titlePtr = '\0';  /* always start with an empty string */

    while (*titleFormat != '\0' && titlePtr < titleEnd) {
        char c = *titleFormat++;
        if (c == '%') {
            c = *titleFormat++;
            if (c == '\0')
            {
                titlePtr = safeCharAdd(titlePtr, titleEnd, '%');
                break;
            }  
            switch (c) {
                case 'c': /* ClearCase view tag */
		    clearCasePresent = True;
                    if (clearCaseViewTag != NULL) {
                        if (serverNameSeen == False ||
                            strcmp(serverName, clearCaseViewTag) != 0) {
                            titlePtr = safeStrCpy(titlePtr, titleEnd, clearCaseViewTag);
                            clearCaseViewTagSeen = True;
                        }
                    }
                    break;
                   
                case 's': /* server name */
		    serverNamePresent = True;
                    if (isServer && serverName[0] != '\0') { /* only applicable for servers */ 
                        if (clearCaseViewTagSeen == False ||
                            strcmp(serverName, clearCaseViewTag) != 0) {
                            titlePtr = safeStrCpy(titlePtr, titleEnd, serverName);
                            serverNameSeen = True;
                        }
                    }
                    break;
                   
                case 'd': /* directory without any limit to no. of components */
		    dirNamePresent = True;
                    if (filenameSet) {
                       titlePtr = safeStrCpy(titlePtr, titleEnd, path);
                    }
                    break;
                    
               case '0': /* directory with limited no. of components */
               case '1':
               case '2':
               case '3':
               case '4':
               case '5':
               case '6':
               case '7':
               case '8':
               case '9':
                   if (*titleFormat == 'd') {
                       dirNamePresent = True;
                       noOfComponents = c - '0';
                       titleFormat++; /* delete the argument */

                       if (filenameSet) {
                           const char* trailingPath = GetTrailingPathComponents(path,
                                                                                noOfComponents);

                           /* prefix with ellipsis if components were skipped */
                           if (trailingPath > path) {
                               titlePtr = safeStrCpy(titlePtr, titleEnd, "...");
                           }
                           titlePtr = safeStrCpy(titlePtr, titleEnd, trailingPath);
                       }
                    }
                    break;
                    
                case 'f': /* file name */
		    fileNamePresent = True;
                    titlePtr = safeStrCpy(titlePtr, titleEnd, filename);
                    break;
                    
                case 'h': /* host name */
		    hostNamePresent = True;
		    titlePtr = safeStrCpy(titlePtr, titleEnd, GetNameOfHost());
                    break;
		    
                case 'S': /* file status */
                    fileStatusPresent = True;
                    if (IS_ANY_LOCKED_IGNORING_USER(lockReasons) && fileChanged)
                       titlePtr = safeStrCpy(titlePtr, titleEnd, "read only, modified");
                    else if (IS_ANY_LOCKED_IGNORING_USER(lockReasons))
                       titlePtr = safeStrCpy(titlePtr, titleEnd, "read only");
                    else if (IS_USER_LOCKED(lockReasons) && fileChanged)
                       titlePtr = safeStrCpy(titlePtr, titleEnd, "locked, modified");
                    else if (IS_USER_LOCKED(lockReasons))
                       titlePtr = safeStrCpy(titlePtr, titleEnd, "locked");
                    else if (fileChanged)
                       titlePtr = safeStrCpy(titlePtr, titleEnd, "modified");
                    break;
                    
                case 'u': /* user name */
		    userNamePresent = True;
                    titlePtr = safeStrCpy(titlePtr, titleEnd, GetUserName());
                    break;
                   
                case '%': /* escaped % */
                    titlePtr = safeCharAdd(titlePtr, titleEnd, '%');
                    break;
                   
		case '*': /* short file status ? */
                    fileStatusPresent = True;
		    if (*titleFormat && *titleFormat == 'S')
		    {
			++titleFormat;
			shortStatus = True;
			if (IS_ANY_LOCKED_IGNORING_USER(lockReasons) && fileChanged)
                	   titlePtr = safeStrCpy(titlePtr, titleEnd, "RO*");
                	else if (IS_ANY_LOCKED_IGNORING_USER(lockReasons))
                	   titlePtr = safeStrCpy(titlePtr, titleEnd, "RO");
                	else if (IS_USER_LOCKED(lockReasons) && fileChanged)
                	   titlePtr = safeStrCpy(titlePtr, titleEnd, "LO*");
                	else if (IS_USER_LOCKED(lockReasons))
                	   titlePtr = safeStrCpy(titlePtr, titleEnd, "LO");
                	else if (fileChanged)
                	   titlePtr = safeStrCpy(titlePtr, titleEnd, "*");
			break;
		    }
                    /* fall-through */
                default:
                    titlePtr = safeCharAdd(titlePtr, titleEnd, c);
                    break;
            }
        }
        else {
            titlePtr = safeCharAdd(titlePtr, titleEnd, c);
        }
    }
    
    compressWindowTitle(title);
    
    if (title[0] == 0)
    {
	sprintf(&title[0], "<empty>"); /* For preview purposes only */
    }

    if (etDialog.form)
    {
	/* Prevent recursive callback loop */
        etDialog.suppressFormatUpdate = True;
	
	/* Sync radio buttons with format string (in case the user entered
	   the format manually) */
        XmToggleButtonSetState(etDialog.fileW,   fileNamePresent,   False);
        XmToggleButtonSetState(etDialog.statusW, fileStatusPresent, False);
        XmToggleButtonSetState(etDialog.serverW, serverNamePresent, False);
#ifndef VMS
        XmToggleButtonSetState(etDialog.ccW,     clearCasePresent,  False);
#endif /* VMS */
        XmToggleButtonSetState(etDialog.dirW,    dirNamePresent,    False);
        XmToggleButtonSetState(etDialog.hostW,   hostNamePresent,   False);
        XmToggleButtonSetState(etDialog.nameW,   userNamePresent,   False);
	
        XtSetSensitive(etDialog.shortStatusW,    fileStatusPresent);
	if (fileStatusPresent)
	{
	    XmToggleButtonSetState(etDialog.shortStatusW, shortStatus, False);
	}
	
	/* Directory components are also sensitive to presence of dir */
        XtSetSensitive(etDialog.ndirW,    dirNamePresent);
        XtSetSensitive(etDialog.mdirW,    dirNamePresent);
	
        if (dirNamePresent) /* Avoid erasing number when not active */
        {
    	   if (noOfComponents >= 0)
	   {
               char* value = XmTextGetString(etDialog.ndirW);
               char buf[2];
               sprintf(&buf[0], "%d", noOfComponents);
               if (strcmp(&buf[0], value)) /* Don't overwrite unless diff. */
       	           SetIntText(etDialog.ndirW, noOfComponents);
               XtFree(value);
	   }
	   else
	   {
	       XmTextSetString(etDialog.ndirW, "");
	   }
        }
	
	/* Enable/disable test buttons, depending on presence of codes */
        XtSetSensitive(etDialog.oFileChangedW,  fileStatusPresent);
        XtSetSensitive(etDialog.oFileReadOnlyW, fileStatusPresent);
        XtSetSensitive(etDialog.oFileLockedW,   fileStatusPresent &&
						!IS_PERM_LOCKED(etDialog.lockReasons));
	    
        XtSetSensitive(etDialog.oServerNameW, serverNamePresent);
	
#ifndef VMS
        XtSetSensitive(etDialog.oCcViewTagW,       clearCasePresent);
        XtSetSensitive(etDialog.oServerEqualViewW, clearCasePresent &&
	                                           serverNamePresent);
#endif  /* VMS */      
	
        XtSetSensitive(etDialog.oDirW,    dirNamePresent);
	
        etDialog.suppressFormatUpdate = False;
    }        
    
    return(title);
}



/* a utility that sets the values of all toggle buttons */
static void setToggleButtons(void)
{
    XmToggleButtonSetState(etDialog.oDirW,
    	    	etDialog.filenameSet == True, False);
    XmToggleButtonSetState(etDialog.oFileChangedW,
    	    	etDialog.fileChanged == True, False);
    XmToggleButtonSetState(etDialog.oFileReadOnlyW,
    	    	IS_PERM_LOCKED(etDialog.lockReasons), False);
    XmToggleButtonSetState(etDialog.oFileLockedW,
    	    	IS_USER_LOCKED(etDialog.lockReasons), False);
    /* Read-only takes precedence on locked */
    XtSetSensitive(etDialog.oFileLockedW, !IS_PERM_LOCKED(etDialog.lockReasons));

#ifdef VMS
    XmToggleButtonSetState(etDialog.oServerNameW, etDialog.isServer, False);
#else
    XmToggleButtonSetState(etDialog.oCcViewTagW,
    	    	GetClearCaseViewTag() != NULL, False);
    XmToggleButtonSetState(etDialog.oServerNameW,
    	    	etDialog.isServer, False);

    if (GetClearCaseViewTag() != NULL &&
        etDialog.isServer &&
        GetPrefServerName()[0] != '\0' &&  
        strcmp(GetClearCaseViewTag(), GetPrefServerName()) == 0) {
        XmToggleButtonSetState(etDialog.oServerEqualViewW,
    	    	    True, False);
     } else {
        XmToggleButtonSetState(etDialog.oServerEqualViewW,
    	    	    False, False);
    }
#endif /* VMS */
}    

static void formatChangedCB(Widget w, XtPointer clientData, XtPointer callData)
{
    char *format;
    int  filenameSet = XmToggleButtonGetState(etDialog.oDirW);
    char *title;
    const char* serverName;
    
    if (etDialog.suppressFormatUpdate)
    {
	return; /* Prevent recursive feedback */
    }
    
    format = XmTextGetString(etDialog.formatW);
    
#ifndef VMS
    if (XmToggleButtonGetState(etDialog.oServerEqualViewW) &&
	XmToggleButtonGetState(etDialog.ccW)) {
       serverName = etDialog.viewTag;
    } else
#endif /* VMS */
    {
       serverName = XmToggleButtonGetState(etDialog.oServerNameW) ?
                                       etDialog.serverName : "";
    }

    title = FormatWindowTitle(
                  etDialog.filename,
                  etDialog.filenameSet == True ?
                                   etDialog.path :
                                   "/a/very/long/path/used/as/example/",
#ifdef VMS
		  NULL,
#else
                  XmToggleButtonGetState(etDialog.oCcViewTagW) ?
                                   etDialog.viewTag : NULL,
#endif /* VMS */
                  serverName,
                  etDialog.isServer,
                  filenameSet,
                  etDialog.lockReasons,
                  XmToggleButtonGetState(etDialog.oFileChangedW),
                  format);
    XtFree(format);
    XmTextFieldSetString(etDialog.previewW, title);
}

#ifndef VMS
static void ccViewTagCB(Widget w, XtPointer clientData, XtPointer callData)
{
    if (XmToggleButtonGetState(w) == False) {
        XmToggleButtonSetState(etDialog.oServerEqualViewW, False, False);
    }
    formatChangedCB(w, clientData, callData);
}
#endif /* VMS */

static void serverNameCB(Widget w, XtPointer clientData, XtPointer callData)
{
    if (XmToggleButtonGetState(w) == False) {
        XmToggleButtonSetState(etDialog.oServerEqualViewW, False, False);
    }
    etDialog.isServer = XmToggleButtonGetState(w);
    formatChangedCB(w, clientData, callData);
}
      
static void fileChangedCB(Widget w, XtPointer clientData, XtPointer callData)
{        
    etDialog.fileChanged = XmToggleButtonGetState(w);
    formatChangedCB(w, clientData, callData);
}

static void fileLockedCB(Widget w, XtPointer clientData, XtPointer callData)
{        
    SET_USER_LOCKED(etDialog.lockReasons, XmToggleButtonGetState(w));
    formatChangedCB(w, clientData, callData);
}

static void fileReadOnlyCB(Widget w, XtPointer clientData, XtPointer callData)
{        
    SET_PERM_LOCKED(etDialog.lockReasons, XmToggleButtonGetState(w));
    formatChangedCB(w, clientData, callData);
}

#ifndef VMS
static void serverEqualViewCB(Widget w, XtPointer clientData, XtPointer callData)
{
    if (XmToggleButtonGetState(w) == True) {
        XmToggleButtonSetState(etDialog.oCcViewTagW,  True, False);
        XmToggleButtonSetState(etDialog.oServerNameW, True, False);
        etDialog.isServer = True;
    }
    formatChangedCB(w, clientData, callData);
}         
#endif /* VMS */

static void applyCB(Widget w, XtPointer clientData, XtPointer callData)
{
    char *format = XmTextGetString(etDialog.formatW);

    /* pop down the dialog */
/*    XtUnmanageChild(etDialog.form); */
   
    if (strcmp(format, GetPrefTitleFormat()) != 0) {
        SetPrefTitleFormat(format);
    }
    XtFree(format);
}

static void closeCB(Widget w, XtPointer clientData, XtPointer callData)
{
    /* pop down the dialog */
    XtUnmanageChild(etDialog.form);
}

static void restoreCB(Widget w, XtPointer clientData, XtPointer callData)
{
    XmTextSetString(etDialog.formatW, "{%c} [%s] %f (%S) - %d");
}

static void helpCB(Widget w, XtPointer clientData, XtPointer callData)
{
    Help(HELP_CUSTOM_TITLE_DIALOG);
}

static void wtDestroyCB(Widget w, XtPointer clientData, XtPointer callData)
{
    if (w == etDialog.form) /* Prevent disconnecting the replacing dialog */
        etDialog.form = NULL;
}

static void wtUnmapCB(Widget w, XtPointer clientData, XtPointer callData)
{
    if (etDialog.form == w)  /* Prevent destroying the replacing dialog */
        XtDestroyWidget(etDialog.form);
}

static void appendToFormat(const char* string)
{
    char *format = XmTextGetString(etDialog.formatW);
    char *buf = XtMalloc(strlen(string) + strlen(format) + 1);
    strcpy(buf, format);
    strcat(buf, string);
    XmTextSetString(etDialog.formatW, buf);
    XtFree(format);
    XtFree(buf);
}

static void removeFromFormat(const char* string)
{
    char *format = XmTextGetString(etDialog.formatW);
    char* pos;
    
    /* There can be multiple occurences */
    while ((pos = strstr(format, string)))
    {
	/* If the string is preceded or followed by a brace, include 
	   the brace(s) for removal */
	char* start = pos;
	char* end = pos + strlen(string);
	char post = *end;
	
	if (post == '}' || post == ')' || post == ']' || post == '>')
        {
	    end += 1;
	    post = *end;
	}
	
	if (start > format)
	{
	    char pre = *(start-1);
	    if (pre == '{' || pre == '(' || pre == '[' || pre == '<')
		start -= 1;
	}
	if (start > format)
	{
	    char pre = *(start-1);
	    /* If there is a space in front and behind, remove one space 
	       (there can be more spaces, but in that case it is likely
	       that the user entered them manually); also remove trailing
	       space */
	    if (pre == ' ' && post == ' ')
	    {
		end += 1;
	    }
	    else if (pre == ' ' && post == (char)0)
	    {
		/* Remove (1) trailing space */
		start -= 1; 
	    }
	}
	
	/* Contract the string: move end to start */
	strcpy(start, end);
    }
    
    /* Remove leading and trailing space */
    pos = format;
    while (*pos == ' ') ++pos;
    strcpy(format, pos);
    
    pos = format + strlen(format) - 1;
    while (pos >= format && *pos == ' ')
    {
	--pos;
    }
    *(pos+1) = (char)0;
    
    XmTextSetString(etDialog.formatW, format);
    XtFree(format);
}


static void toggleFileCB(Widget w, XtPointer clientData, XtPointer callData)
{
    if (XmToggleButtonGetState(etDialog.fileW))
	appendToFormat(" %f");
    else
	removeFromFormat("%f");
}

static void toggleServerCB(Widget w, XtPointer clientData, XtPointer callData)
{
    if (XmToggleButtonGetState(etDialog.serverW))
	appendToFormat(" [%s]");
    else
	removeFromFormat("%s");
}

static void toggleHostCB(Widget w, XtPointer clientData, XtPointer callData)
{
    if (XmToggleButtonGetState(etDialog.hostW))
	appendToFormat(" [%h]");
    else
	removeFromFormat("%h");
}

#ifndef VMS
static void toggleClearCaseCB(Widget w, XtPointer clientData, XtPointer callData)
{
    if (XmToggleButtonGetState(etDialog.ccW))
	appendToFormat(" {%c}");
    else
	removeFromFormat("%c");
}
#endif /* VMS */

static void toggleStatusCB(Widget w, XtPointer clientData, XtPointer callData)
{
    if (XmToggleButtonGetState(etDialog.statusW))
    {
	if (XmToggleButtonGetState(etDialog.shortStatusW))
	    appendToFormat(" (%*S)");
	else
	    appendToFormat(" (%S)");
    }
    else
    {
	removeFromFormat("%S");
	removeFromFormat("%*S");
    }
}

static void toggleShortStatusCB(Widget w, XtPointer clientData, XtPointer callData)
{
    char *format, *pos;
    
    if (etDialog.suppressFormatUpdate)
    {
	return;
    }
    
    format = XmTextGetString(etDialog.formatW);
    
    if (XmToggleButtonGetState(etDialog.shortStatusW))
    {
	/* Find all %S occurrences and replace them by %*S */
	do
	{
	    pos = strstr(format, "%S");
	    if (pos)
	    {
     	        char* tmp = (char*)XtMalloc((strlen(format)+2)*sizeof(char));
		strncpy(tmp, format, (size_t)(pos-format+1));
		tmp[pos-format+1] = 0;
		strcat(tmp, "*");
		strcat(tmp, pos+1);
		XtFree(format);
		format = tmp;
	    }
	}
	while (pos);
    }    
    else
    {
	/* Replace all %*S occurences by %S */
	do
	{
            pos = strstr(format, "%*S");
	    if (pos)
	    {
		strcpy(pos+1, pos+2);
	    }
	}
	while(pos);
    }
    
    XmTextSetString(etDialog.formatW, format);
    XtFree(format);
}

static void toggleUserCB(Widget w, XtPointer clientData, XtPointer callData)
{
    if (XmToggleButtonGetState(etDialog.nameW))
	appendToFormat(" %u");
    else
	removeFromFormat("%u");
}

static void toggleDirectoryCB(Widget w, XtPointer clientData, XtPointer callData)
{
    if (XmToggleButtonGetState(etDialog.dirW))
    {
        char buf[20];
	int maxComp;
        char *value = XmTextGetString(etDialog.ndirW);
	if (*value)
	{
	   if (sscanf(value, "%d", &maxComp) > 0)
	   {
	      sprintf(&buf[0], " %%%dd ", maxComp);
           }   
	   else
	   {
   	      sprintf(&buf[0], " %%d "); /* Should not be necessary */
 	   }
        }
	else
	{
	   sprintf(&buf[0], " %%d ");
	}
	XtFree(value);
        appendToFormat(buf);
    }
    else
    {
	int i;
	removeFromFormat("%d");
	for (i=0; i<=9; ++i)
	{
	    char buf[20];
	    sprintf(&buf[0], "%%%dd", i);
	    removeFromFormat(buf);
	}
    }
}

static void enterMaxDirCB(Widget w, XtPointer clientData, XtPointer callData)
{
    int maxComp = -1;
    char *format;
    char *value;
    
    if (etDialog.suppressFormatUpdate)
    {
	return;
    }
	
    format = XmTextGetString(etDialog.formatW);
    value = XmTextGetString(etDialog.ndirW);
    
    if (*value)
    {
	if (sscanf(value, "%d", &maxComp) <= 0)
	{
	   /* Don't allow non-digits to be entered */
	   XBell(XtDisplay(w), 0);
	   XmTextSetString(etDialog.ndirW, "");
	}
    }
    
    if (maxComp >= 0)
    {
	char *pos;
	int found = False;
	char insert[2];
        insert[0] = (char)('0' + maxComp);
        insert[1] = (char)0; /* '0' digit and 0 char ! */
	
	/* Find all %d and %nd occurrences and replace them by the new value */
	do
	{
	    int i;
	    found = False;
	    pos = strstr(format, "%d");
	    if (pos)
	    {
     	        char* tmp = (char*)XtMalloc((strlen(format)+2)*sizeof(char));
		strncpy(tmp, format, (size_t)(pos-format+1));
		tmp[pos-format+1] = 0;
		strcat(tmp, &insert[0]);
		strcat(tmp, pos+1);
		XtFree(format);
		format = tmp;
		found = True;
	    }
	      
	    for (i=0; i<=9; ++i)
	    {
        	char buf[20];
		sprintf(&buf[0], "%%%dd", i);
		if (i != maxComp)
		{
		    pos = strstr(format, &buf[0]);
		    if (pos)
		    {
			*(pos+1) = insert[0];
			found = True;
		    }
		}
	    }
	}
	while (found);
    }    
    else
    {
	int found = True;
	
	/* Replace all %nd occurences by %d */
	do
	{
   	    int i;
	    found = False;
	    for (i=0; i<=9; ++i)
	    {
        	char buf[20];
		char *pos;
		sprintf(&buf[0], "%%%dd", i);
		pos = strstr(format, &buf[0]);
		if (pos)
		{
		    strcpy(pos+1, pos+2);
		    found = True;
		}
	    }
	}
	while(found);
    }
    
    XmTextSetString(etDialog.formatW, format);
    XtFree(format);
    XtFree(value);
}

static void createEditTitleDialog(Widget parent)
{
#define LEFT_MARGIN_POS 2
#define RIGHT_MARGIN_POS 98
#define V_MARGIN 5
#define RADIO_INDENT 3

    Widget buttonForm, formatLbl, previewFrame;
    Widget previewForm, previewBox, selectFrame, selectBox, selectForm;
    Widget testLbl, selectLbl;
    Widget applyBtn, closeBtn, restoreBtn, helpBtn;
    XmString s1;
    XmFontList fontList;
    Arg args[20];
    int defaultBtnOffset;
    Dimension	shadowThickness;
    Dimension	radioHeight, textHeight;
    Pixel background;
    
    int ac = 0;
    XtSetArg(args[ac], XmNautoUnmanage, False); ac++;
    XtSetArg(args[ac], XmNtitle, "Customize Window Title"); ac++;
    etDialog.form = CreateFormDialog(parent, "customizeTitle", args, ac);

    /*
     * Destroy the dialog every time it is unmapped (otherwise it 'sticks'
     * to the window for which it was created originally).
     */
    XtAddCallback(etDialog.form, XmNunmapCallback, wtUnmapCB, NULL);
    XtAddCallback(etDialog.form, XmNdestroyCallback, wtDestroyCB, NULL);
    
    etDialog.shell = XtParent(etDialog.form);
    
    /* Definition form */
    selectFrame = XtVaCreateManagedWidget("selectionFrame", xmFrameWidgetClass,
	    etDialog.form,
	    XmNleftAttachment, XmATTACH_POSITION,
	    XmNleftPosition, LEFT_MARGIN_POS,
	    XmNtopAttachment, XmATTACH_FORM,
	    XmNtopOffset, V_MARGIN,
	    XmNrightAttachment, XmATTACH_POSITION,
	    XmNrightPosition, RIGHT_MARGIN_POS, NULL);

    XtVaCreateManagedWidget("titleLabel", xmLabelGadgetClass,
    	    selectFrame,
    	    XmNlabelString,
	    s1=XmStringCreateSimple("Title definition"),
	    XmNchildType, XmFRAME_TITLE_CHILD,
	    XmNchildHorizontalAlignment, XmALIGNMENT_BEGINNING, NULL);
    XmStringFree(s1);
    
    selectForm = XtVaCreateManagedWidget("selectForm", xmFormWidgetClass,
	    selectFrame ,
	    XmNleftAttachment, XmATTACH_POSITION,
	    XmNleftPosition, LEFT_MARGIN_POS,
	    XmNtopAttachment, XmATTACH_FORM,
	    XmNtopOffset, V_MARGIN,
	    XmNrightAttachment, XmATTACH_POSITION,
	    XmNrightPosition, RIGHT_MARGIN_POS, NULL);
    
    selectLbl = XtVaCreateManagedWidget("selectLabel", xmLabelGadgetClass,
    	    selectForm,
    	    XmNlabelString, s1=XmStringCreateSimple("Select title components to include:  "),
	    XmNleftAttachment, XmATTACH_POSITION,
	    XmNleftPosition, LEFT_MARGIN_POS,
	    XmNtopOffset, 5,
	    XmNbottomOffset, 5,
	    XmNtopAttachment, XmATTACH_FORM, NULL);
    XmStringFree(s1);

    selectBox = XtVaCreateManagedWidget("selectBox", xmFormWidgetClass,
    	    selectForm,
    	    XmNorientation, XmHORIZONTAL,
    	    XmNpacking, XmPACK_TIGHT,
    	    XmNradioBehavior, False,
	    XmNleftAttachment, XmATTACH_FORM,
	    XmNrightAttachment, XmATTACH_FORM,
	    XmNtopOffset, 5,
	    XmNtopAttachment, XmATTACH_WIDGET,
	    XmNtopWidget, selectLbl,
	    NULL);
    
    etDialog.fileW = XtVaCreateManagedWidget("file", 
    	    xmToggleButtonWidgetClass, selectBox,
	    XmNleftAttachment, XmATTACH_POSITION,
	    XmNleftPosition, RADIO_INDENT,
	    XmNtopAttachment, XmATTACH_FORM,
    	    XmNlabelString, s1=XmStringCreateSimple("File name (%f)"),
    	    XmNmnemonic, 'F', NULL);
    XtAddCallback(etDialog.fileW, XmNvalueChangedCallback, toggleFileCB, NULL);
    XmStringFree(s1);

    etDialog.statusW = XtVaCreateManagedWidget("status", 
    	    xmToggleButtonWidgetClass, selectBox,
	    XmNleftAttachment, XmATTACH_POSITION,
	    XmNleftPosition, RADIO_INDENT,
	    XmNtopAttachment, XmATTACH_WIDGET,
	    XmNtopWidget, etDialog.fileW,
    	    XmNlabelString, s1=XmStringCreateSimple("File status (%S) "),
    	    XmNmnemonic, 't', NULL);
    XtAddCallback(etDialog.statusW, XmNvalueChangedCallback, toggleStatusCB, NULL);
    XmStringFree(s1);

    etDialog.shortStatusW = XtVaCreateManagedWidget("shortStatus", 
    	    xmToggleButtonWidgetClass, selectBox,
	    XmNleftAttachment, XmATTACH_WIDGET,
	    XmNleftWidget, etDialog.statusW,
	    XmNtopAttachment, XmATTACH_WIDGET,
	    XmNtopWidget, etDialog.fileW,
    	    XmNlabelString, s1=XmStringCreateSimple("brief"),
    	    XmNmnemonic, 'b', NULL);
    XtAddCallback(etDialog.shortStatusW, XmNvalueChangedCallback, toggleShortStatusCB, NULL);
    XmStringFree(s1);

    etDialog.ccW = XtVaCreateManagedWidget("ccView", 
    	    xmToggleButtonWidgetClass, selectBox,
	    XmNleftAttachment, XmATTACH_POSITION,
	    XmNleftPosition, RADIO_INDENT,
	    XmNtopAttachment, XmATTACH_WIDGET,
	    XmNtopWidget, etDialog.statusW,
    	    XmNlabelString, s1=XmStringCreateSimple("ClearCase view tag (%c) "),
    	    XmNmnemonic, 'C', NULL);
#ifdef VMS
    XtSetSensitive(etDialog.ccW, False);
#else
    XtAddCallback(etDialog.ccW, XmNvalueChangedCallback, toggleClearCaseCB, NULL);
#endif /* VMS */
    XmStringFree(s1);

    etDialog.dirW = XtVaCreateManagedWidget("directory", 
    	    xmToggleButtonWidgetClass, selectBox,
	    XmNleftAttachment, XmATTACH_POSITION,
	    XmNleftPosition, RADIO_INDENT,
	    XmNtopAttachment, XmATTACH_WIDGET,
	    XmNtopWidget, etDialog.ccW,
    	    XmNlabelString, s1=XmStringCreateSimple("Directory (%d),"),
    	    XmNmnemonic, 'D', NULL);
    XtAddCallback(etDialog.dirW, XmNvalueChangedCallback, toggleDirectoryCB, NULL);
    XmStringFree(s1);
    
    XtVaGetValues(etDialog.fileW, XmNheight, &radioHeight, NULL);
    etDialog.mdirW = XtVaCreateManagedWidget("componentLab", 
    	    xmLabelGadgetClass, selectBox,
	    XmNheight, radioHeight,
	    XmNleftAttachment, XmATTACH_WIDGET,
	    XmNleftWidget, etDialog.dirW,
	    XmNtopAttachment, XmATTACH_WIDGET,
	    XmNtopWidget, etDialog.ccW,
    	    XmNlabelString, s1=XmStringCreateSimple("max. components: "),
    	    XmNmnemonic, 'x', NULL);
    XmStringFree(s1);
    
    etDialog.ndirW = XtVaCreateManagedWidget("dircomp", 
    	    xmTextWidgetClass, selectBox,
   	    XmNcolumns, 1,
   	    XmNmaxLength, 1,
	    XmNleftAttachment, XmATTACH_WIDGET,
	    XmNleftWidget, etDialog.mdirW,
	    XmNtopAttachment, XmATTACH_WIDGET,
	    XmNtopWidget, etDialog.ccW,
    	    NULL);
    XtAddCallback(etDialog.ndirW, XmNvalueChangedCallback, enterMaxDirCB, NULL);
    RemapDeleteKey(etDialog.ndirW);
    XtVaSetValues(etDialog.mdirW, XmNuserData, etDialog.ndirW, NULL); /* mnemonic processing */
    
    XtVaGetValues(etDialog.ndirW, XmNheight, &textHeight, NULL);
    XtVaSetValues(etDialog.dirW,  XmNheight, textHeight, NULL);
    XtVaSetValues(etDialog.mdirW, XmNheight, textHeight, NULL);
    
    etDialog.hostW = XtVaCreateManagedWidget("host", 
    	    xmToggleButtonWidgetClass, selectBox,
	    XmNleftAttachment, XmATTACH_POSITION,
	    XmNleftPosition, 50 + RADIO_INDENT,
	    XmNtopAttachment, XmATTACH_FORM,
    	    XmNlabelString, s1=XmStringCreateSimple("Host name (%h)"),
    	    XmNmnemonic, 'H', NULL);
    XtAddCallback(etDialog.hostW, XmNvalueChangedCallback, toggleHostCB, NULL);
    XmStringFree(s1);

    etDialog.nameW = XtVaCreateManagedWidget("name", 
    	    xmToggleButtonWidgetClass, selectBox,
	    XmNleftAttachment, XmATTACH_POSITION,
	    XmNleftPosition, 50 + RADIO_INDENT,
	    XmNtopAttachment, XmATTACH_WIDGET,
	    XmNtopWidget, etDialog.hostW,
    	    XmNlabelString, s1=XmStringCreateSimple("User name (%u)"),
    	    XmNmnemonic, 'U', NULL);
    XtAddCallback(etDialog.nameW, XmNvalueChangedCallback, toggleUserCB, NULL);
    XmStringFree(s1);

    etDialog.serverW = XtVaCreateManagedWidget("server", 
    	    xmToggleButtonWidgetClass, selectBox,
	    XmNleftAttachment, XmATTACH_POSITION,
	    XmNleftPosition, 50 + RADIO_INDENT,
	    XmNtopAttachment, XmATTACH_WIDGET,
	    XmNtopWidget, etDialog.nameW,
    	    XmNlabelString, s1=XmStringCreateSimple("NEdit server name (%s)"),
    	    XmNmnemonic, 's', NULL);
    XtAddCallback(etDialog.serverW, XmNvalueChangedCallback, toggleServerCB, NULL);
    XmStringFree(s1);

    formatLbl = XtVaCreateManagedWidget("formatLbl", xmLabelGadgetClass,
    	    selectForm,
    	    XmNlabelString, s1=XmStringCreateSimple("Format:  "),
    	    XmNmnemonic, 'r',
	    XmNleftAttachment, XmATTACH_POSITION,
	    XmNleftPosition, LEFT_MARGIN_POS,
	    XmNtopAttachment, XmATTACH_WIDGET,
	    XmNtopWidget, selectBox,
	    XmNbottomAttachment, XmATTACH_FORM, NULL);
    XmStringFree(s1);
    etDialog.formatW = XtVaCreateManagedWidget("format", xmTextWidgetClass,
    	    selectForm,
	    XmNmaxLength, WINDOWTITLE_MAX_LEN,
	    XmNtopAttachment, XmATTACH_WIDGET,
	    XmNtopWidget, selectBox,
	    XmNtopOffset, 5,
	    XmNleftAttachment, XmATTACH_WIDGET,
	    XmNleftWidget, formatLbl,
	    XmNrightAttachment, XmATTACH_POSITION,
	    XmNrightPosition, RIGHT_MARGIN_POS,
	    XmNbottomAttachment, XmATTACH_FORM, 
	    XmNbottomOffset, 5, NULL);
    RemapDeleteKey(etDialog.formatW);
    XtVaSetValues(formatLbl, XmNuserData, etDialog.formatW, NULL);
    XtAddCallback(etDialog.formatW, XmNvalueChangedCallback, formatChangedCB, NULL);

    XtVaGetValues(etDialog.formatW, XmNheight, &textHeight, NULL);
    XtVaSetValues(formatLbl,  XmNheight, textHeight, NULL);
    
    previewFrame = XtVaCreateManagedWidget("previewFrame", xmFrameWidgetClass,
	    etDialog.form,
	    XmNtopAttachment, XmATTACH_WIDGET,
	    XmNtopWidget, selectFrame,
	    XmNleftAttachment, XmATTACH_POSITION,
	    XmNleftPosition, LEFT_MARGIN_POS,
	    XmNrightAttachment, XmATTACH_POSITION, 
	    XmNrightPosition, RIGHT_MARGIN_POS, NULL);

    XtVaCreateManagedWidget("previewLabel", xmLabelGadgetClass,
    	    previewFrame,
    	    XmNlabelString, s1=XmStringCreateSimple("Preview"),
	    XmNchildType, XmFRAME_TITLE_CHILD,
	    XmNchildHorizontalAlignment, XmALIGNMENT_BEGINNING, NULL);
    XmStringFree(s1);
    
    previewForm = XtVaCreateManagedWidget("previewForm", xmFormWidgetClass,
	    previewFrame,
	    XmNleftAttachment, XmATTACH_FORM,
	    XmNleftPosition, LEFT_MARGIN_POS,
	    XmNtopAttachment, XmATTACH_FORM,
	    XmNtopOffset, V_MARGIN,
	    XmNrightAttachment, XmATTACH_FORM,
	    XmNrightPosition, RIGHT_MARGIN_POS, NULL);
    
    /* Copy a variable width font from one of the labels to use for the
       preview (no editing is allowed, and with a fixed size font the
       preview easily gets partially obscured). Also copy the form background
       color to make it clear that this field is not editable */
    XtVaGetValues(formatLbl, XmNfontList, &fontList, NULL);
    XtVaGetValues(previewForm, XmNbackground, &background, NULL);
    
    etDialog.previewW = XtVaCreateManagedWidget("sample",
            xmTextFieldWidgetClass, previewForm,
            XmNeditable, False,
            XmNcursorPositionVisible, False,
            XmNtopAttachment, XmATTACH_FORM,
            XmNleftAttachment, XmATTACH_FORM,
            XmNleftOffset, V_MARGIN,
            XmNrightAttachment, XmATTACH_FORM,
            XmNrightOffset, V_MARGIN,
            XmNfontList, fontList,
            XmNbackground, background,
            NULL);
    
    previewBox = XtVaCreateManagedWidget("previewBox", xmFormWidgetClass,
    	    previewForm,
    	    XmNorientation, XmHORIZONTAL,
    	    XmNpacking, XmPACK_TIGHT,
    	    XmNradioBehavior, False,
	    XmNleftAttachment, XmATTACH_FORM,
	    XmNrightAttachment, XmATTACH_FORM,
	    XmNtopAttachment, XmATTACH_WIDGET,
	    XmNtopWidget, etDialog.previewW, NULL);
    
    testLbl = XtVaCreateManagedWidget("testLabel", xmLabelGadgetClass,
    	    previewBox,
    	    XmNlabelString, s1=XmStringCreateSimple("Test settings:  "),
	    XmNleftAttachment, XmATTACH_POSITION,
	    XmNleftPosition, LEFT_MARGIN_POS,
	    XmNtopOffset, 5,
	    XmNbottomOffset, 5,
	    XmNtopAttachment, XmATTACH_FORM, NULL);
    XmStringFree(s1);

    etDialog.oFileChangedW = XtVaCreateManagedWidget("fileChanged", 
    	    xmToggleButtonWidgetClass, previewBox,
	    XmNleftAttachment, XmATTACH_POSITION,
	    XmNleftPosition, RADIO_INDENT,
	    XmNtopAttachment, XmATTACH_WIDGET,
	    XmNtopWidget, testLbl,
    	    XmNlabelString, s1=XmStringCreateSimple("File modified"),
    	    XmNmnemonic, 'o', NULL);
    XtAddCallback(etDialog.oFileChangedW, XmNvalueChangedCallback, fileChangedCB, NULL);
    XmStringFree(s1);
    
    etDialog.oFileReadOnlyW = XtVaCreateManagedWidget("fileReadOnly", 
    	    xmToggleButtonWidgetClass, previewBox,
	    XmNleftAttachment, XmATTACH_WIDGET,
	    XmNleftWidget, etDialog.oFileChangedW,
	    XmNtopAttachment, XmATTACH_WIDGET,
	    XmNtopWidget, testLbl,
    	    XmNlabelString, s1=XmStringCreateSimple("File read only"),
    	    XmNmnemonic, 'n', NULL);
    XtAddCallback(etDialog.oFileReadOnlyW, XmNvalueChangedCallback, fileReadOnlyCB, NULL);
    XmStringFree(s1);
    
    etDialog.oFileLockedW = XtVaCreateManagedWidget("fileLocked", 
    	    xmToggleButtonWidgetClass, previewBox,
	    XmNleftAttachment, XmATTACH_WIDGET,
	    XmNleftWidget, etDialog.oFileReadOnlyW,
	    XmNtopAttachment, XmATTACH_WIDGET,
	    XmNtopWidget, testLbl,
    	    XmNlabelString, s1=XmStringCreateSimple("File locked"),
    	    XmNmnemonic, 'l', NULL);
    XtAddCallback(etDialog.oFileLockedW, XmNvalueChangedCallback, fileLockedCB, NULL);
    XmStringFree(s1);

    etDialog.oServerNameW = XtVaCreateManagedWidget("servernameSet", 
    	    xmToggleButtonWidgetClass, previewBox,
	    XmNleftAttachment, XmATTACH_POSITION,
	    XmNleftPosition, RADIO_INDENT,
	    XmNtopAttachment, XmATTACH_WIDGET,
	    XmNtopWidget, etDialog.oFileChangedW,
    	    XmNlabelString, s1=XmStringCreateSimple("Server name present"),
    	    XmNmnemonic, 'v', NULL);
    XtAddCallback(etDialog.oServerNameW, XmNvalueChangedCallback, serverNameCB, NULL);
    XmStringFree(s1);

    etDialog.oCcViewTagW = XtVaCreateManagedWidget("ccViewTagSet", 
    	    xmToggleButtonWidgetClass, previewBox,
	    XmNleftAttachment, XmATTACH_POSITION,
	    XmNleftPosition, RADIO_INDENT,
	    XmNtopAttachment, XmATTACH_WIDGET,
	    XmNtopWidget, etDialog.oServerNameW,
    	    XmNlabelString, s1=XmStringCreateSimple("CC view tag present"),
#ifdef VMS
   	    XmNset, False,
#else
   	    XmNset, GetClearCaseViewTag() != NULL,
#endif /* VMS */
    	    XmNmnemonic, 'w', NULL);
#ifdef VMS
    XtSetSensitive(etDialog.oCcViewTagW, False);
#else
    XtAddCallback(etDialog.oCcViewTagW, XmNvalueChangedCallback, ccViewTagCB, NULL);
#endif /* VMS */
    XmStringFree(s1);

    etDialog.oServerEqualViewW = XtVaCreateManagedWidget("serverEqualView", 
    	    xmToggleButtonWidgetClass, previewBox,
	    XmNleftAttachment, XmATTACH_WIDGET,
    	    XmNleftWidget, etDialog.oCcViewTagW,
	    XmNtopAttachment, XmATTACH_WIDGET,
	    XmNtopWidget, etDialog.oServerNameW,
    	    XmNlabelString, s1=XmStringCreateSimple("Server name equals CC view tag  "),
    	    XmNmnemonic, 'q', NULL);
#ifdef VMS
    XtSetSensitive(etDialog.oServerEqualViewW, False);
#else
    XtAddCallback(etDialog.oServerEqualViewW, XmNvalueChangedCallback, serverEqualViewCB, NULL);
#endif /* VMS */
    XmStringFree(s1);

    etDialog.oDirW = XtVaCreateManagedWidget("pathSet", 
    	    xmToggleButtonWidgetClass, previewBox,
	    XmNleftAttachment, XmATTACH_POSITION,
	    XmNleftPosition, RADIO_INDENT,
	    XmNtopAttachment, XmATTACH_WIDGET,
	    XmNtopWidget, etDialog.oCcViewTagW,
    	    XmNlabelString, s1=XmStringCreateSimple("Directory present"),
    	    XmNmnemonic, 'i', NULL);
    XtAddCallback(etDialog.oDirW, XmNvalueChangedCallback, formatChangedCB, NULL);
    XmStringFree(s1);

    /* Button box */
    buttonForm = XtVaCreateManagedWidget("buttonForm", xmFormWidgetClass,
	    etDialog.form,
	    XmNleftAttachment, XmATTACH_POSITION,
	    XmNleftPosition, LEFT_MARGIN_POS,
	    XmNtopAttachment, XmATTACH_WIDGET,
	    XmNtopWidget, previewFrame,
	    XmNtopOffset, V_MARGIN,
	    XmNbottomOffset, V_MARGIN,
	    XmNbottomAttachment, XmATTACH_FORM,
	    XmNrightAttachment, XmATTACH_POSITION,
	    XmNrightPosition, RIGHT_MARGIN_POS, NULL);

    applyBtn = XtVaCreateManagedWidget("apply", xmPushButtonWidgetClass,
            buttonForm,
    	    XmNhighlightThickness, 2,
            XmNlabelString, s1=XmStringCreateSimple("Apply"),
            XmNshowAsDefault, (short)1,
    	    XmNleftAttachment, XmATTACH_POSITION,
    	    XmNleftPosition, 6,
    	    XmNrightAttachment, XmATTACH_POSITION,
    	    XmNrightPosition, 25,
    	    XmNbottomAttachment, XmATTACH_FORM,
	    NULL);
    XtAddCallback(applyBtn, XmNactivateCallback, applyCB, NULL);
    XmStringFree(s1);
    XtVaGetValues(applyBtn, XmNshadowThickness, &shadowThickness, NULL);
    defaultBtnOffset = shadowThickness + 4;

    closeBtn = XtVaCreateManagedWidget("close", xmPushButtonWidgetClass,
            buttonForm,
    	    XmNhighlightThickness, 2,
    	    XmNlabelString, s1=XmStringCreateSimple("Close"),
    	    XmNleftAttachment, XmATTACH_POSITION,
    	    XmNleftPosition, 52,
    	    XmNrightAttachment, XmATTACH_POSITION,
    	    XmNrightPosition, 71,
    	    XmNbottomAttachment, XmATTACH_FORM,
            XmNbottomOffset, defaultBtnOffset,
	    NULL);
    XtAddCallback(closeBtn, XmNactivateCallback, closeCB, NULL);
    XmStringFree(s1);

    restoreBtn = XtVaCreateManagedWidget("restore", xmPushButtonWidgetClass,
            buttonForm,
    	    XmNhighlightThickness, 2,
    	    XmNlabelString, s1=XmStringCreateSimple("Default"),
    	    XmNleftAttachment, XmATTACH_POSITION,
    	    XmNleftPosition, 29,
    	    XmNrightAttachment, XmATTACH_POSITION,
    	    XmNrightPosition, 48,
    	    XmNbottomAttachment, XmATTACH_FORM,
            XmNbottomOffset, defaultBtnOffset,
	    XmNmnemonic, 'e', NULL);
    XtAddCallback(restoreBtn, XmNactivateCallback, restoreCB, NULL);
    XmStringFree(s1);

    helpBtn = XtVaCreateManagedWidget("help", xmPushButtonWidgetClass,
            buttonForm,
    	    XmNhighlightThickness, 2,
    	    XmNlabelString, s1=XmStringCreateSimple("Help"),
    	    XmNleftAttachment, XmATTACH_POSITION,
    	    XmNleftPosition, 75,
    	    XmNrightAttachment, XmATTACH_POSITION,
    	    XmNrightPosition, 94,
    	    XmNbottomAttachment, XmATTACH_FORM,
            XmNbottomOffset, defaultBtnOffset,
	    XmNmnemonic, 'p', NULL);
    XtAddCallback(helpBtn, XmNactivateCallback, helpCB, NULL);
    XmStringFree(s1);

    /* Set initial default button */
    XtVaSetValues(etDialog.form, XmNdefaultButton, applyBtn, NULL);
    XtVaSetValues(etDialog.form, XmNcancelButton, closeBtn, NULL);

    /* Handle mnemonic selection of buttons and focus to dialog */
    AddDialogMnemonicHandler(etDialog.form, FALSE);
    
    etDialog.suppressFormatUpdate = FALSE;
}

void EditCustomTitleFormat(WindowInfo *window)
{
    /* copy attributes from current window so that we can use as many
     * 'real world' defaults as possible when testing the effect
     * of different formatting strings.
     */
    strcpy(etDialog.path, window->path);
    strcpy(etDialog.filename, window->filename);
#ifndef VMS
    strcpy(etDialog.viewTag, GetClearCaseViewTag() != NULL ?
                             GetClearCaseViewTag() :
                             "viewtag");
#endif /* VMS */
    strcpy(etDialog.serverName, IsServer ?
                             GetPrefServerName() :
                             "servername");
    etDialog.isServer    = IsServer;
    etDialog.filenameSet = window->filenameSet;
    etDialog.lockReasons = window->lockReasons;
    etDialog.fileChanged = window->fileChanged;
    
    if (etDialog.window != window && etDialog.form)
    {
       /* Destroy the dialog owned by the other window. 
          Note: don't rely on the destroy event handler to reset the
                form. Events are handled asynchronously, so the old dialog
                may continue to live for a while. */
       XtDestroyWidget(etDialog.form);
       etDialog.form = NULL;
    }
    
    etDialog.window      = window;
    
    /* Create the dialog if it doesn't already exist */
    if (etDialog.form == NULL)
    {
        createEditTitleDialog(window->shell);
    }
    else
    {
        /* If the window is already up, just pop it to the top */
        if (XtIsManaged(etDialog.form)) {
           
	    RaiseShellWindow(XtParent(etDialog.form));

            /* force update of the dialog */
            setToggleButtons();
            formatChangedCB(0, 0, 0);
	    return;
        }
    }
    
    /* set initial value of format field */
    XmTextSetString(etDialog.formatW, (char *)GetPrefTitleFormat());
        
    /* force update of the dialog */
    setToggleButtons();
    formatChangedCB(0, 0, 0);
    
    /* put up dialog and wait for user to press ok or cancel */
    ManageDialogCenteredOnPointer(etDialog.form);
}
