/*
 * Selective logging - alternative 4.4BSD <err.h> implementation.
 *
 * Written by Tony Finch <dot@dotat.at> <fanf2@cam.ac.uk>
 * at the University of Cambridge Computing Service.
 * You may do anything with this, at your own risk.
 *
 * $Cambridge: users/fanf2/selog/selog_err.c,v 1.6 2008/05/21 18:07:25 fanf2 Exp $
 */

#include <errno.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include <err.h>

#include "selog.h"

static const char ident[] =
"@(#) $Cambridge: users/fanf2/selog/selog_err.c,v 1.6 2008/05/21 18:07:25 fanf2 Exp $";

/*
 * This file contains a replacement implementation of the
 * 4.4BSD err.h API that writes via selog instead of stderr.
 * The err_set_file() function is not implemented.
 *
 * The err() functions report fatal errors and the warn() functions
 * report other errors, so their names do not match their selog
 * levels. We use selog_bufinit() because selog's standard preamble
 * would be redundant.
 */

void
err_set_file(void *p) {
	static selog_selector sel = SELINIT("err_set_file", SELOG_DEBUG);
	selog(sel, "output redirection ignored by selog");
	p = p;
}

static void
report(selog_selector sel, int code, const char *fmt, va_list ap) {
	selog_buffer buf;
	if(!selog_on(sel))
		return;
	selog_bufinit(buf, sel);
	if(fmt == NULL) {
		selog_add(buf, selog_level(sel));
	} else {
		selog_add(buf, "%s: ", selog_level(sel));
		selog_addv(buf, fmt, ap);
	}
	if(code != 0)
		selog_add(buf, ": %s", strerror(code));
	selog_write(buf);
}

static selog_selector sel_warn = SELINIT("warn", SELOG_ERROR);

void
warn(const char *fmt, ...) {
	va_list ap;
	va_start(ap, fmt);
	report(sel_warn, errno, fmt, ap);
	va_end(ap);
}

void
vwarn(const char *fmt , va_list ap) {
	report(sel_warn, errno, fmt, ap);
}

void
warnc(int code, const char *fmt, ...) {
	va_list ap;
	va_start(ap, fmt);
	report(sel_warn, code, fmt, ap);
	va_end(ap);
}

void
vwarnc(int code, const char *fmt, va_list ap) {
	report(sel_warn, code, fmt, ap);
}

void
warnx(const char *fmt, ...) {
	va_list ap;
	va_start(ap, fmt);
	report(sel_warn, 0, fmt, ap);
	va_end(ap);
}

void
vwarnx(const char *fmt, va_list ap) {
	report(sel_warn, 0, fmt, ap);
}

static void (*exit_fun)(int);
static int    exit_val;

void
err_set_exit(void (*f)(int)) {
	exit_fun = f;
}

static void
call_exit_fun(void) {
	if(exit_fun != NULL)
		exit_fun(exit_val);
}

#ifdef __GNUC__
static void reporter(int, int, const char *, va_list)
	__attribute__((__noreturn__));
#endif

static void
reporter(int e, int code, const char *fmt, va_list ap) {
	selog_selector sel = SELINIT("err", SELOG_FATAL(e));
	exit_val = e;
	atexit(call_exit_fun);
	report(sel, code, fmt, ap);
	exit(e);
}

void
err(int e, const char *fmt, ...) {
	va_list ap;
	va_start(ap, fmt);
	reporter(e, errno, fmt, ap);
	va_end(ap);
}

void
verr(int e, const char *fmt, va_list ap) {
	reporter(e, errno, fmt, ap);
}

void
errc(int e, int code, const char *fmt, ...) {
	va_list ap;
	va_start(ap, fmt);
	reporter(e, code, fmt, ap);
	va_end(ap);
}

void
verrc(int e, int code, const char *fmt, va_list ap) {
	reporter(e, code, fmt, ap);
}

void
errx(int e, const char *fmt, ...) {
	va_list ap;
	va_start(ap, fmt);
	reporter(e, 0, fmt, ap);
	va_end(ap);
}

void
verrx(int e, const char *fmt, va_list ap) {
	reporter(e, 0, fmt, ap);
}

/*
 *  eof selog_err.c
 *
 ********************************************************************/
