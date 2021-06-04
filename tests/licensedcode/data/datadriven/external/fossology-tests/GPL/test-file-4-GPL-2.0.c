/***************************************************************
 Copyright (C) 2006-2011 Hewlett-Packard Development Company, L.P.

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU General Public License
 version 2 as published by the Free Software Foundation.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License along
 with this program; if not, write to the Free Software Foundation, Inc.,
 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

 ***************************************************************/
/**
 * \file process.c
 * \brief some common functions that process the files for scanning
 */

#include "nomos.h"
#include "process.h"
#include "licenses.h"
#include "util.h"
#include "list.h"

#ifdef	MEMSTATS
extern void memStats();
#endif	/* MEMSTATS */

#define	BOGUS_MD5	"wwww0001xxxx0002yyyy0004zzzz0008"


/**
 * processNonPackageFiles
 *
 * \callgraph
 */
static void processNonPackagedFiles()
{
  /* item_t *p;  doesn't look like this is used */

#if defined(PROC_TRACE) || defined(UNPACK_DEBUG)
  traceFunc("== processNonPackagedFiles()\n");
#endif  /* PROC_TRACE || UNPACK_DEBUG */

  /*
   * If there are unused/unreferenced source archives, they need to be
   * processed indivudually.  Create the global 'unused archives' list
   * and hand it off to be processed.
   */
#ifdef	UNPACK_DEBUG
  listDump(&cur.regfList, NO);
#endif	/* UNPACK_DEBUG */
  if (!cur.regfList.used) {
    printf("No-data!\n");
    return;
  } else {
    /* CDB *cur.basename = NULL_CHAR; */
    processRegularFiles();
    /* since p isn't used, reduce the following to just the listGetItem
     since it mods the global cur
	p = listGetItem(&cur.fLicFoundMap, BOGUS_MD5);
	p->buf = copyString(cur.compLic, MTAG_COMPLIC);
	p->refCount++;
	p->buf = copyString(BOGUS_MD5, MTAG_MD5SUM);
     */
    listGetItem(&cur.fLicFoundMap, BOGUS_MD5);
  }
  return;
}



#ifdef notdef
/**
 * \brief Remove the line at textp+offset from the buffer
 */
void stripLine(char *textp, int offset, int size)
{
  char *start, *end;
  extern char *findBol();

#ifdef	PROC_TRACE
  traceFunc("== stripLine(%s, %d, %d)\n", textp, offset, size);
#endif	/* PROC_TRACE */

  if ((end = findEol((char *)(textp+offset))) == NULL_STR) {
    Assert(NO, "No EOL found!");
  }
  if ((start = findBol((char *)(textp+offset), textp)) == NULL_STR) {
    Assert(NO, "No BOL found!");
  }
#ifdef	DEBUG
  printf("Textp %p start %p end %p\n", textp, start, end);
  printf("@START(%d): %s", strlen(start), start);
  printf("@END+1(%d): %s", strlen(end+1), end+1);
#endif	/* DEBUG */
  if (*(end+1) == NULL_CHAR) {	/* EOF */
    *start = NULL_CHAR;
  }
  else {
#ifdef	DEBUG
    printf("MOVE %d bytes\n", size-(end-textp));
#endif	/* DEBUG */
    (void) memmove(start, (char *)(end+1),
        (size_t)((size)-(end-textp)));
  }
#ifdef	DEBUG
  printf("FINISH: @START(%d): %s", strlen(start), start);
#endif	/* DEBUG */
  return;
}
#endif /* notdef */


/**
 * processRawSource
 *
 * \callgraph
 *
 */
void processRawSource()
{
#ifdef	PROC_TRACE
  traceFunc("== processRawSource()\n");
#endif	/* PROC_TRACE */

#ifdef	PACKAGE_DEBUG
  listDump(&cur.regfList, NO);
#endif	/* PACKAGE_DEBUG */

  processNonPackagedFiles();
  return;
}

/**
 * processRegularFiles
 * \brief Process a list of regular files.
 *
 *  \callgraph
  CDB - This really isn't a list, there should only be a single file in
  regfList. 
 */
void processRegularFiles()
{
#ifdef  PROC_TRACE
  traceFunc("== processRegularFiles()\n");
#endif  /* PROC_TRACE */

  /* CDB (void) sprintf(cur.basename, "misc-files"); */
  /* loop through the list here -- and delete files with link-count >1? */
  licenseScan(&cur.regfList);
  return;
}

