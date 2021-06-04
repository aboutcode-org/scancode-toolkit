//////////////////////////////////////////////////////
//
// Projet TFTPD32. Mai 98 Ph.jounin - Jan 2003
// File async_log.c: Asynchronous multithread Log management
//
// source released under European Union Public License
//
//////////////////////////////////////////////////////


#include "headers.h"
#include <stdio.h>
#include <stdlib.h>

#include "threading.h"
#include "..\_libs\event_log\eventlog.h"


///////////////////////////////
//
// LOG function
// add an entry into the log window
//
// The LOG function may be called by any thread
// it adds an entry into the linked list (using semaphore protected Push function)
// then set an event to wake up the console thread
//
///////////////////////////////


static int AppendToFile (const char *filename, const char *szLog, int len)
{
int Ark;
HANDLE hLog;
int dummy=0;
DWORD dwPos;
// Loop since the file may be already opened by another thread
Ark=0 ;
do
{
Ark++;
hLog = CreateFile ( filename,
GENERIC_WRITE,
FILE_SHARE_READ, // permit read operations
NULL,
OPEN_ALWAYS, // open or create
FILE_ATTRIBUTE_NORMAL,
NULL );
if (hLog==INVALID_HANDLE_VALUE) Sleep (50);
}
while (hLog==INVALID_HANDLE_VALUE && Ark<3);

if (hLog!=INVALID_HANDLE_VALUE)
{
dwPos = SetFilePointer (hLog, 0, NULL, FILE_END);
if (dwPos != INVALID_SET_FILE_POINTER)
{
WriteFile (hLog, szLog, len, & dummy, NULL);
WriteFile (hLog, "\r\n", 2, & dummy, NULL);
// probably not necessary, just in case...
FlushFileBuffers (hLog);
}
CloseHandle (hLog);
} // append log
return dummy;
} // LogToFile


// LOG window can be called concurrently by every worker thread or background window
void __cdecl LOG (int DebugLevel, const char *szFmt, ...)
{
va_list marker;
char szBuf [LOGSIZE], *lpTxt=szBuf;
SYSTEMTIME sTime;
int ThreadPriority;
time_t dNow;
static struct S_Pacing
{
time_t time;
int count;
} sPacing;

if (DebugLevel > sSettings.LogLvl || tThreads[TH_CONSOLE].hEv==INVALID_HANDLE_VALUE) return;

// PJO 2017: add a poor man pacing to avoid flooding GUI
#define PER_THREAD_PER_SEC_MAX_MSG 100
time (&dNow);
if (dNow == sPacing.time)
{
++sPacing.count;
if ( sPacing.count> PER_THREAD_PER_SEC_MAX_MSG/2 )
{
// let the GUI run (otherwise it may either freeze the GUI or create a buffer overflow)
// bug found by Peter Baris
ThreadPriority = GetThreadPriority (GetCurrentThread());
SetThreadPriority (GetCurrentThread(), THREAD_PRIORITY_IDLE);
Sleep (1); // pass the hand
SetThreadPriority (GetCurrentThread(), ThreadPriority);
}
if ( sPacing.count> PER_THREAD_PER_SEC_MAX_MSG ) return;
}
else
{
sPacing.time = dNow;
sPacing.count = 0;
}

// format the string with wsprintf and timestamp
szBuf [sizeof szBuf - 1] = 0;
GetLocalTime (&sTime);
va_start( marker, szFmt ); /* Initialize variable arguments. */
#ifdef MSVC
lpTxt += vsprintf_s (lpTxt,
szBuf + sizeof szBuf - lpTxt -1 ,
szFmt,
marker);
sprintf_s ( lpTxt,
szBuf + sizeof szBuf - lpTxt -1 ,
" [%02d/%02d %02d:%02d:%02d.%03d]",
sTime.wDay, sTime.wMonth,
sTime.wHour, sTime.wMinute, sTime.wSecond, sTime.wMilliseconds );
#else
lpTxt += vsprintf (lpTxt, szFmt, marker);
wsprintf (lpTxt, " [%02d/%02d %02d:%02d:%02d.%03d]",
sTime.wDay, sTime.wMonth,
sTime.wHour, sTime.wMinute, sTime.wSecond, sTime.wMilliseconds );
#endif
lpTxt += sizeof (" [00/00 00:00:00.000]");

// push the message into queue
SendMsgRequest ( C_LOG, szBuf, (int) (lpTxt - szBuf), FALSE, FALSE );
// Add the log into the file
if (sSettings.szTftpLogFile[0]!=0)
{
AppendToFile (sSettings.szTftpLogFile, szBuf, (int) (lpTxt - szBuf - 1));
} // Log into file

} // LOG


///////////////////////////////
// Synchronous send
///////////////////////////////

// Report an error to the GUI, also goes into the event log
void __cdecl SVC_ERROR (const char *szFmt, ...)
{
va_list marker;
char szBuf [LOGSIZE];

szBuf[LOGSIZE-1]=0;
va_start( marker, szFmt ); /* Initialize variable arguments. */
#ifdef MSVC
vsprintf_s (szBuf,
sizeof szBuf -1 ,
szFmt,
marker);
#else
vsprintf (szBuf, szFmt, marker);
#endif

// push the message into queue -> don't block thread but retain msg
SendMsgRequest ( C_ERROR, szBuf, lstrlen (szBuf), FALSE, TRUE );
va_end (marker);

if (sSettings.bEventLog)
WriteIntoEventLog (szBuf, C_ERROR);
} // SVC_ERROR


// Report an warning to the GUI
void __cdecl SVC_WARNING (const char *szFmt, ...)
{
va_list marker;
char szBuf [LOGSIZE];

szBuf[LOGSIZE-1]=0;
va_start( marker, szFmt ); /* Initialize variable arguments. */
#ifdef MSVC
vsprintf_s (szBuf,
sizeof szBuf -1 ,
szFmt,
marker);
#else
vsprintf (szBuf, szFmt, marker);
#endif

// push the message into queue -> block until msg sent
SendMsgRequest ( C_WARNING, szBuf, lstrlen (szBuf), FALSE, FALSE );
va_end (marker);
} // SVC_WARNING
