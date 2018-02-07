/* Daisy Confidential. Copyright (c) 2008 Daisy Ltd.  http://www.daisy.com */

/*
 * P e a F l o w e r
 * =================
 *
 * FOR DETAILS ON THE PeaFlower FUNCTIONS, PLEASE SEE THE PeaFlower MANUAL
 * OR INCLUDED HELP FILES.
 *
 * This file may not be distributed, it may only be used for development
 * or evaluation purposes. The only exception is distribution to Linux.
 * For details refer to \PeaFlower\docs\license.txt.
 *
 * Web site: http://www.daisy.com
 * Email:    support@daisy.com
 */
#ifndef _PEAPODS_H_
#define _PEAPODS_H_
#if defined(__cplusplus)
extern "C" {
#endif
	
	...
	
#define PF_VER_STR  PF_PROD_NAME " v" PF_VERSION_STR \
" Daisy (c) 1997 - 2008 Build Date: " __DATE__ \
PF_CPU_SPEC PF_DATA_MODEL PF_FILE_FORMAT
	
#if !defined(UNIX) && (defined(LINUX) || defined(STARGATE) || defined(PEAPODS))
#define UNIX
#endif
