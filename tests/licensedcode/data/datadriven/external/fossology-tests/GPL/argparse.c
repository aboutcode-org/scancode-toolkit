/* [argparse.c wk 17.06.97] Argument Parser for option handling
 * Copyright (C) 1998, 1999, 2000, 2001, 2003, 2004, 2005, 2006, 2007,
 *               2008, 2010, 2012 Free Software Foundation, Inc.
 *
 * This file is part of GnuPG.
 *
 * GnuPG is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * GnuPG is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, see <http://www.gnu.org/licenses/>.
 */

#include <config.h>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

#include "util.h"
#include "i18n.h"


/*********************************
 * @Summary arg_parse
 *  #include <wk/lib.h>
 *
 *  typedef struct {
 *	char *argc;		  pointer to argc (value subject to change)
 *	char ***argv;		  pointer to argv (value subject to change)
 *	unsigned flags; 	  Global flags (DO NOT CHANGE)
 *	int err;		  print error about last option
 *				  1 = warning, 2 = abort
 *	int r_opt;		  return option
 *	int r_type;		  type of return value (0 = no argument found)
 *	union {
 *	    int   ret_int;
 *	    long  ret_long
 *	    ulong ret_ulong;
 *	    char *ret_str;
 *	} r;			  Return values
 *	struct {
 *	    int idx;
 *	    const char *last;
 *	    void *aliases;
 *	} internal;		  DO NOT CHANGE
 *  } ARGPARSE_ARGS;
 *
 *  typedef struct {
 *	int	    short_opt;
 *	const char *long_opt;
 *	unsigned flags;
 *  } ARGPARSE_OPTS;
 *
 *  int arg_parse( ARGPARSE_ARGS *arg, ARGPARSE_OPTS *opts );
 *
 * @Description
 *  This is my replacement for getopt(). See the example for a typical usage.
 *  Global flags are:
 *     Bit 0 : Do not remove options form argv
 *     Bit 1 : Do not stop at last option but return other args
 *	       with r_opt set to -1.
 *     Bit 2 : Assume options and real args are mixed.
 *     Bit 3 : Do not use -- to stop option processing.
 *     Bit 4 : Do not skip the first arg.
 *     Bit 5 : allow usage of long option with only one dash
 *     Bit 6 : ignore --version and --help
 *     all other bits must be set to zero, this value is modified by the
 *     function, so assume this is write only.
 *  Local flags (for each option):
 *     Bit 2-0 : 0 = does not take an argument
 *		 1 = takes int argument
 *		 2 = takes string argument
 *		 3 = takes long argument
 *		 4 = takes ulong argument
 *     Bit 3 : argument is optional (r_type will the be set to 0)
 *     Bit 4 : allow 0x etc. prefixed values.
 *     Bit 7 : this is a command and not an option
 *  You stop the option processing by setting opts to NULL, the function will
 *  then return 0.
 * @Return Value
 *   Returns the args.r_opt or 0 if ready
 *   r_opt may be -2/-7 to indicate an unknown option/command.
 * @See Also
 *   ArgExpand
 * @Notes
 *  You do not need to process the options 'h', '--help' or '--version'
 *  because this function includes standard help processing; but if you
 *  specify '-h', '--help' or '--version' you have to do it yourself.
 *  The option '--' stops argument processing; if bit 1 is set the function
 *  continues to return normal arguments.
 *  To process float args or unsigned args you must use a string args and do
 *  the conversion yourself.
 * @Example
 *
 *     ARGPARSE_OPTS opts[] = {
 *     { 'v', "verbose",   0 },
 *     { 'd', "debug",     0 },
 *     { 'o', "output",    2 },
 *     { 'c', "cross-ref", 2|8 },
 *     { 'm', "my-option", 1|8 },
 *     { 500, "have-no-short-option-for-this-long-option", 0 },
 *     {0} };
 *     ARGPARSE_ARGS pargs = { &argc, &argv, 0 }
 *
 *     while( ArgParse( &pargs, &opts) ) {
 *	   switch( pargs.r_opt ) {
 *	     case 'v': opt.verbose++; break;
 *	     case 'd': opt.debug++; break;
 *	     case 'o': opt.outfile = pargs.r.ret_str; break;
 *	     case 'c': opt.crf = pargs.r_type? pargs.r.ret_str:"a.crf"; break;
 *	     case 'm': opt.myopt = pargs.r_type? pargs.r.ret_int : 1; break;
 *	     case 500: opt.a_long_one++;  break
 *	     default : pargs.err = 1; break; -- force warning output --
 *	   }
 *     }
 *     if( argc > 1 )
 *	   log_fatal( "Too many args");
 *
 */

typedef struct alias_def_s *ALIAS_DEF;
struct alias_def_s {
    ALIAS_DEF next;
    char *name;   /* malloced buffer with name, \0, value */
    const char *value; /* ptr into name */
};

static int  set_opt_arg(ARGPARSE_ARGS *arg, unsigned flags, char *s);
static void show_help(ARGPARSE_OPTS *opts, unsigned flags);
static void show_version(void);

static void
initialize( ARGPARSE_ARGS *arg, const char *filename, unsigned *lineno )
{
    if( !(arg->flags & (1<<15)) ) { /* initialize this instance */
	arg->internal.idx = 0;
	arg->internal.last = NULL;
	arg->internal.inarg = 0;
	arg->internal.stopped = 0;
	arg->internal.aliases = NULL;
	arg->internal.cur_alias = NULL;
	arg->err = 0;
	arg->flags |= 1<<15; /* mark initialized */
	if( *arg->argc < 0 )
	    log_bug("Invalid argument for ArgParse\n");
    }


    if( arg->err ) { /* last option was erroneous */

	if( filename ) {
	    if( arg->r_opt == -6 )
	      log_error("%s:%u: argument not expected\n", filename, *lineno );
	    else if( arg->r_opt == -5 )
	      log_error("%s:%u: read error\n", filename, *lineno );
	    else if( arg->r_opt == -4 )
	      log_error("%s:%u: keyword too long\n", filename, *lineno );
	    else if( arg->r_opt == -3 )
	      log_error("%s:%u: missing argument\n", filename, *lineno );
	    else if( arg->r_opt == -7 )
	      log_error("%s:%u: invalid command\n", filename, *lineno );
	    else if( arg->r_opt == -10 )
	      log_error("%s:%u: invalid alias definition\n",filename,*lineno);
	    else
	      log_error("%s:%u: invalid option\n", filename, *lineno );
	}
	else {
	    if( arg->r_opt == -3 )
	      log_error("Missing argument for option \"%.50s\"\n",
			arg->internal.last? arg->internal.last:"[??]" );
	    else if( arg->r_opt == -6 )
	      log_error("Option \"%.50s\" does not expect an argument\n",
			arg->internal.last? arg->internal.last:"[??]" );
	    else if( arg->r_opt == -7 )
	      log_error("Invalid command \"%.50s\"\n",
			arg->internal.last? arg->internal.last:"[??]" );
	    else if( arg->r_opt == -8 )
	      log_error("Option \"%.50s\" is ambiguous\n",
			arg->internal.last? arg->internal.last:"[??]" );
	    else if( arg->r_opt == -9 )
	      log_error("Command \"%.50s\" is ambiguous\n",
			arg->internal.last? arg->internal.last:"[??]" );
	    else
	      log_error("Invalid option \"%.50s\"\n",
			arg->internal.last? arg->internal.last:"[??]" );
	}
	if( arg->err != 1 || arg->r_opt == -5 )
	    exit(2);
	arg->err = 0;
    }

    /* clearout the return value union */
    arg->r.ret_str = NULL;
    arg->r.ret_long= 0;
}


static void
store_alias( ARGPARSE_ARGS *arg, char *name, char *value )
{
    /* TODO: replace this dummy function with a rea one
     * and fix the probelms IRIX has with (ALIAS_DEV)arg..
     * used as lvalue
     */
#if 0
    ALIAS_DEF a = xmalloc( sizeof *a );
    a->name = name;
    a->value = value;
    a->next = (ALIAS_DEF)arg->internal.aliases;
    (ALIAS_DEF)arg->internal.aliases = a;
#endif
}

/****************
 * Get options from a file.
 * Lines starting with '#' are comment lines.
 * Syntax is simply a keyword and the argument.
 * Valid keywords are all keywords from the long_opt list without
 * the leading dashes. The special keywords "help", "warranty" and "version"
 * are not valid here.
 * The special keyword "alias" may be used to store alias definitions,
 * which are later expanded like long options.
 * Caller must free returned strings.
 * If called with FP set to NULL command line args are parse instead.
 *
 * Q: Should we allow the syntax
 *     keyword = value
 *    and accept for boolean options a value of 1/0, yes/no or true/false?
 * Note: Abbreviation of options is here not allowed.
 */
int
optfile_parse( FILE *fp, const char *filename, unsigned *lineno,
	       ARGPARSE_ARGS *arg, ARGPARSE_OPTS *opts)
{
    int state, i, c;
    int idx=0;
    char keyword[100];
    char *buffer = NULL;
    size_t buflen = 0;
    int inverse=0;
    int in_alias=0;

    if( !fp ) /* same as arg_parse() in this case */
	return arg_parse( arg, opts );

    initialize( arg, filename, lineno );

    /* find the next keyword */
    state = i = 0;
    for(;;) {
	c=getc(fp);
	if( c == '\n' || c== EOF ) {
	    if( c != EOF )
		++*lineno;
	    if( state == -1 )
		break;
	    else if( state == 2 ) {
		keyword[i] = 0;
		for(i=0; opts[i].short_opt; i++ )
		    if( opts[i].long_opt && !strcmp( opts[i].long_opt, keyword) )
			break;
		idx = i;
		arg->r_opt = opts[idx].short_opt;
		if( inverse ) /* this does not have an effect, hmmm */
		    arg->r_opt = -arg->r_opt;
		if( !opts[idx].short_opt )   /* unknown command/option */
		    arg->r_opt = (opts[idx].flags & 256)? -7:-2;
		else if( !(opts[idx].flags & 7) ) /* does not take an arg */
		    arg->r_type = 0;	       /* okay */
		else if( (opts[idx].flags & 8) )  /* argument is optional */
                    arg->r_type = 0;	       /* okay */
		else			       /* required argument */
		    arg->r_opt = -3;	       /* error */
		break;
	    }
	    else if( state == 3 ) {	       /* no argument found */
		if( in_alias )
		    arg->r_opt = -3;	       /* error */
		else if( !(opts[idx].flags & 7) ) /* does not take an arg */
		    arg->r_type = 0;	       /* okay */
		else if( (opts[idx].flags & 8) )  /* no optional argument */
		    arg->r_type = 0;	       /* okay */
		else			       /* no required argument */
		    arg->r_opt = -3;	       /* error */
		break;
	    }
	    else if( state == 4 ) {	/* have an argument */
		if( in_alias ) {
		    if( !buffer )
			arg->r_opt = -6;
		    else {
			char *p;

			buffer[i] = 0;
			p = strpbrk( buffer, " \t" );
			if( p ) {
			    *p++ = 0;
			    trim_spaces( p );
			}
			if( !p || !*p ) {
			    xfree( buffer );
			    arg->r_opt = -10;
			}
			else {
			    store_alias( arg, buffer, p );
			}
		    }
		}
		else if( !(opts[idx].flags & 7) )  /* does not take an arg */
		    arg->r_opt = -6;	    /* error */
		else {
		    char *p;
		    if( !buffer ) {
			keyword[i] = 0;
			buffer = xstrdup(keyword);
		    }
		    else
			buffer[i] = 0;

		    trim_spaces( buffer );
		    p = buffer;
		    /* remove quotes if they totally enclose the
                       string, and do not occur within the string */
		    if( *p == '"' && p[strlen(p)-1]=='"') {
		        char *p2=p;

			while(*(++p2))
			  if(*p2=='"')
			    break;

			if(*p2=='"' && *(p2+1)=='\0') {
			  p[strlen(p)-1] = 0;
			  p++;
			}
		    }
		    if( !set_opt_arg(arg, opts[idx].flags, p) )
			xfree(buffer);
		}
		break;
	    }
	    else if( c == EOF ) {
		if( ferror(fp) )
		    arg->r_opt = -5;   /* read error */
		else
		    arg->r_opt = 0;    /* eof */
		break;
	    }
	    state = 0;
	    i = 0;
	}
	else if( state == -1 )
	    ; /* skip */
	else if( !state && isspace(c) )
	    ; /* skip leading white space */
	else if( !state && c == '#' )
	    state = 1;	/* start of a comment */
	else if( state == 1 )
	    ; /* skip comments */
	else if( state == 2 && isspace(c) ) {
	    keyword[i] = 0;
	    for(i=0; opts[i].short_opt; i++ )
		if( opts[i].long_opt && !strcmp( opts[i].long_opt, keyword) )
		    break;
	    idx = i;
	    arg->r_opt = opts[idx].short_opt;
	    if( !opts[idx].short_opt ) {
		if( !strcmp( keyword, "alias" ) ) {
		    in_alias = 1;
		    state = 3;
		}
		else {
		    arg->r_opt = (opts[idx].flags & 256)? -7:-2;
		    state = -1;        /* skip rest of line and leave */
		}
	    }
	    else
		state = 3;
	}
	else if( state == 3 ) { /* skip leading spaces of the argument */
	    if( !isspace(c) ) {
		i = 0;
		keyword[i++] = c;
		state = 4;
	    }
	}
	else if( state == 4 ) { /* collect the argument */
	    if( buffer ) {
		if( i < buflen-1 )
		    buffer[i++] = c;
		else {
		    buflen += 50;
		    buffer = xrealloc(buffer, buflen);
		    buffer[i++] = c;
		}
	    }
	    else if( i < DIM(keyword)-1 )
		keyword[i++] = c;
	    else {
		buflen = DIM(keyword)+50;
		buffer = xmalloc(buflen);
		memcpy(buffer, keyword, i);
		buffer[i++] = c;
	    }
	}
	else if( i >= DIM(keyword)-1 ) {
	    arg->r_opt = -4;   /* keyword to long */
	    state = -1;        /* skip rest of line and leave */
	}
	else {
	    keyword[i++] = c;
	    state = 2;
	}
    }

    return arg->r_opt;
}



static int
find_long_option( ARGPARSE_ARGS *arg,
		  ARGPARSE_OPTS *opts, const char *keyword )
{
    int i;
    size_t n;

    /* Would be better if we can do a binary search, but it is not
       possible to reorder our option table because we would mess
       up our help strings - What we can do is: Build a nice option
       lookup table wehn this function is first invoked */
    if( !*keyword )
	return -1;
    for(i=0; opts[i].short_opt; i++ )
	if( opts[i].long_opt && !strcmp( opts[i].long_opt, keyword) )
	    return i;
#if 0
    {
	ALIAS_DEF a;
	/* see whether it is an alias */
	for( a = args->internal.aliases; a; a = a->next ) {
	    if( !strcmp( a->name, keyword) ) {
		/* todo: must parse the alias here */
		args->internal.cur_alias = a;
		return -3; /* alias available */
	    }
	}
    }
#endif
    /* not found, see whether it is an abbreviation */
    /* aliases may not be abbreviated */
    n = strlen( keyword );
    for(i=0; opts[i].short_opt; i++ ) {
	if( opts[i].long_opt && !strncmp( opts[i].long_opt, keyword, n ) ) {
	    int j;
	    for(j=i+1; opts[j].short_opt; j++ ) {
		if( opts[j].long_opt
		    && !strncmp( opts[j].long_opt, keyword, n ) )
		    return -2;	/* abbreviation is ambiguous */
	    }
	    return i;
	}
    }
    return -1;
}

int
arg_parse( ARGPARSE_ARGS *arg, ARGPARSE_OPTS *opts)
{
    int idx;
    int argc;
    char **argv;
    char *s, *s2;
    int i;

    initialize( arg, NULL, NULL );
    argc = *arg->argc;
    argv = *arg->argv;
    idx = arg->internal.idx;

    if( !idx && argc && !(arg->flags & (1<<4)) ) { /* skip the first entry */
	argc--; argv++; idx++;
    }

  next_one:
    if( !argc ) { /* no more args */
	arg->r_opt = 0;
	goto leave; /* ready */
    }

    s = *argv;
    arg->internal.last = s;

    if( arg->internal.stopped && (arg->flags & (1<<1)) ) {
	arg->r_opt = -1;  /* not an option but a argument */
	arg->r_type = 2;
	arg->r.ret_str = s;
	argc--; argv++; idx++; /* set to next one */
    }
    else if( arg->internal.stopped ) { /* ready */
	arg->r_opt = 0;
	goto leave;
    }
    else if( *s == '-' && s[1] == '-' ) { /* long option */
	char *argpos;

	arg->internal.inarg = 0;
	if( !s[2] && !(arg->flags & (1<<3)) ) { /* stop option processing */
	    arg->internal.stopped = 1;
	    argc--; argv++; idx++;
	    goto next_one;
	}

	argpos = strchr( s+2, '=' );
	if( argpos )
	    *argpos = 0;
	i = find_long_option( arg, opts, s+2 );
	if( argpos )
	    *argpos = '=';

	if( i < 0 && !strcmp( "help", s+2) ) {
	    if( !(arg->flags & (1<<6)) ) {
		show_help(opts, arg->flags);
	    }
	}
	else if( i < 0 && !strcmp( "version", s+2) ) {
	    if( !(arg->flags & (1<<6)) ) {
		show_version();
		exit(0);
	    }
	}
	else if( i < 0 && !strcmp( "warranty", s+2) ) {
	    puts( strusage(16) );
	    exit(0);
	}
	else if( i < 0 && !strcmp( "dump-options", s+2) ) {
	    for(i=0; opts[i].short_opt; i++ ) {
		if( opts[i].long_opt )
		    printf( "--%s\n", opts[i].long_opt );
	    }
	    fputs("--dump-options\n--help\n--version\n--warranty\n", stdout );
	    exit(0);
	}

	if( i == -2 ) /* ambiguous option */
	    arg->r_opt = -8;
	else if( i == -1 ) {
	    arg->r_opt = -2;
	    arg->r.ret_str = s+2;
	}
	else
	    arg->r_opt = opts[i].short_opt;
	if( i < 0 )
	    ;
	else if( (opts[i].flags & 7) ) {
	    if( argpos ) {
		s2 = argpos+1;
		if( !*s2 )
		    s2 = NULL;
	    }
	    else
		s2 = argv[1];
	    if( !s2 && (opts[i].flags & 8) ) { /* no argument but it is okay*/
		arg->r_type = 0;	       /* because it is optional */
	    }
	    else if( !s2 ) {
		arg->r_opt = -3; /* missing argument */
	    }
	    else if( !argpos && *s2 == '-' && (opts[i].flags & 8) ) {
		/* the argument is optional and the next seems to be
		 * an option. We do not check this possible option
		 * but assume no argument */
		arg->r_type = 0;
	    }
	    else {
		set_opt_arg(arg, opts[i].flags, s2);
		if( !argpos ) {
		    argc--; argv++; idx++; /* skip one */
		}
	    }
	}
	else { /* does not take an argument */
	    if( argpos )
		arg->r_type = -6; /* argument not expected */
	    else
		arg->r_type = 0;
	}
	argc--; argv++; idx++; /* set to next one */
    }
    else if( (*s == '-' && s[1]) || arg->internal.inarg ) { /* short option */
	int dash_kludge = 0;
	i = 0;
	if( !arg->internal.inarg ) {
	    arg->internal.inarg++;
	    if( arg->flags & (1<<5) ) {
		for(i=0; opts[i].short_opt; i++ )
		    if( opts[i].long_opt && !strcmp( opts[i].long_opt, s+1)) {
			dash_kludge=1;
			break;
		    }
	    }
	}
	s += arg->internal.inarg;

	if( !dash_kludge ) {
	    for(i=0; opts[i].short_opt; i++ )
		if( opts[i].short_opt == *s )
		    break;
	}

	if( !opts[i].short_opt && ( *s == 'h' || *s == '?' ) ) {
	    if( !(arg->flags & (1<<6)) ) {
		show_help(opts, arg->flags);
	    }
	}

	arg->r_opt = opts[i].short_opt;
	if( !opts[i].short_opt ) {
	    arg->r_opt = (opts[i].flags & 256)? -7:-2;
	    arg->internal.inarg++; /* point to the next arg */
	    arg->r.ret_str = s;
	}
	else if( (opts[i].flags & 7) ) {
	    if( s[1] && !dash_kludge ) {
		s2 = s+1;
		set_opt_arg(arg, opts[i].flags, s2);
	    }
	    else {
		s2 = argv[1];
		if( !s2 && (opts[i].flags & 8) ) { /* no argument but it is okay*/
		    arg->r_type = 0;		   /* because it is optional */
		}
		else if( !s2 ) {
		    arg->r_opt = -3; /* missing argument */
		}
		else if( *s2 == '-' && s2[1] && (opts[i].flags & 8) ) {
		    /* the argument is optional and the next seems to be
		     * an option. We do not check this possible option
		     * but assume no argument */
		    arg->r_type = 0;
		}
		else {
		    set_opt_arg(arg, opts[i].flags, s2);
		    argc--; argv++; idx++; /* skip one */
		}
	    }
	    s = "x"; /* so that !s[1] yields false */
	}
	else { /* does not take an argument */
	    arg->r_type = 0;
	    arg->internal.inarg++; /* point to the next arg */
	}
	if( !s[1] || dash_kludge ) { /* no more concatenated short options */
	    arg->internal.inarg = 0;
	    argc--; argv++; idx++;
	}
    }
    else if( arg->flags & (1<<2) ) {
	arg->r_opt = -1;  /* not an option but a argument */
	arg->r_type = 2;
	arg->r.ret_str = s;
	argc--; argv++; idx++; /* set to next one */
    }
    else {
	arg->internal.stopped = 1; /* stop option processing */
	goto next_one;
    }

  leave:
    *arg->argc = argc;
    *arg->argv = argv;
    arg->internal.idx = idx;
    return arg->r_opt;
}



static int
set_opt_arg(ARGPARSE_ARGS *arg, unsigned flags, char *s)
{
    int base = (flags & 16)? 0 : 10;

    switch( arg->r_type = (flags & 7) ) {
      case 1: /* takes int argument */
	arg->r.ret_int = (int)strtol(s,NULL,base);
	return 0;
      case 3: /* takes long argument   */
	arg->r.ret_long= strtol(s,NULL,base);
	return 0;
      case 4: /* takes ulong argument  */
	arg->r.ret_ulong= strtoul(s,NULL,base);
	return 0;
      case 2: /* takes string argument */
      default:
	arg->r.ret_str = s;
	return 1;
    }
}


static size_t
long_opt_strlen( ARGPARSE_OPTS *o )
{
    size_t n = strlen(o->long_opt);

    if( o->description && *o->description == '|' ) {
	const char *s;

	s=o->description+1;
	if( *s != '=' )
	    n++;
	for(; *s && *s != '|'; s++ )
	    n++;
    }
    return n;
}

/****************
 * Print formatted help. The description string has some special
 * meanings:
 *  - A description string which is "@" suppresses help output for
 *    this option
 *  - a description,ine which starts with a '@' and is followed by
 *    any other characters is printed as is; this may be used for examples
 *    ans such.
 *  - A description which starts with a '|' outputs the string between this
 *    bar and the next one as arguments of the long option.
 */
static void
show_help( ARGPARSE_OPTS *opts, unsigned flags )
{
    const char *s;

    show_version();
    putchar('\n');
    s = strusage(41);
    puts(s);
    if( opts[0].description ) { /* auto format the option description */
	int i,j, indent;
	/* get max. length of long options */
	for(i=indent=0; opts[i].short_opt; i++ ) {
	    if( opts[i].long_opt )
		if( !opts[i].description || *opts[i].description != '@' )
		    if( (j=long_opt_strlen(opts+i)) > indent && j < 35 )
			 indent = j;
	}
	/* example: " -v, --verbose   Viele Sachen ausgeben" */
	indent += 10;
	if( *opts[0].description != '@' )
	    puts("Options:");
	for(i=0; opts[i].short_opt; i++ ) {
	    s = _( opts[i].description );
	    if( s && *s== '@' && !s[1] ) /* hide this line */
		continue;
	    if( s && *s == '@' ) { /* unindented comment only line */
		for(s++; *s; s++ ) {
		    if( *s == '\n' ) {
			if( s[1] )
			    putchar('\n');
		    }
		    else
			putchar(*s);
		}
		putchar('\n');
		continue;
	    }

	    j = 3;
	    if( opts[i].short_opt < 256 ) {
		printf(" -%c", opts[i].short_opt );
		if( !opts[i].long_opt ) {
		    if(s && *s == '|' ) {
			putchar(' '); j++;
			for(s++ ; *s && *s != '|'; s++, j++ )
			    putchar(*s);
			if( *s )
			    s++;
		    }
		}
	    }
	    else
		fputs("   ", stdout);
	    if( opts[i].long_opt ) {
		j += printf("%c --%s", opts[i].short_opt < 256?',':' ',
				       opts[i].long_opt );
		if(s && *s == '|' ) {
		    if( *++s != '=' ) {
			putchar(' ');
			j++;
		    }
		    for( ; *s && *s != '|'; s++, j++ )
			putchar(*s);
		    if( *s )
			s++;
		}
		fputs("   ", stdout);
		j += 3;
	    }
	    for(;j < indent; j++ )
		putchar(' ');
	    if( s ) {
		if( *s && j > indent ) {
		    putchar('\n');
		    for(j=0;j < indent; j++ )
			putchar(' ');
		}
		for(; *s; s++ ) {
		    if( *s == '\n' ) {
			if( s[1] ) {
			    putchar('\n');
			    for(j=0;j < indent; j++ )
				putchar(' ');
			}
		    }
		    else
			putchar(*s);
		}
	    }
	    putchar('\n');
	}
	if( flags & 32 )
	    puts("\n(A single dash may be used instead of the double ones)");
    }
    if( (s=strusage(19)) ) {  /* bug reports to ... */
	putchar('\n');
	fputs(s, stdout);
    }
    fflush(stdout);
    exit(0);
}

static void
show_version()
{
    const char *s;
    int i;
    /* version line */
    fputs(strusage(11), stdout);
    if( (s=strusage(12)) )
	printf(" (%s)", s );
    printf(" %s\n", strusage(13) );
    /* additional version lines */
    for(i=20; i < 30; i++ )
	if( (s=strusage(i)) )
	    printf("%s\n", s );
    /* copyright string */
    if( (s=strusage(14)) )
	printf("%s\n", s );
    /* Licence string.  */
    if( (s=strusage (10)) )
        printf("%s\n", s );
    /* copying conditions */
    if( (s=strusage(15)) )
	fputs(s, stdout);
    /* thanks */
    if( (s=strusage(18)) )
	fputs(s, stdout);
    /* additional program info */
    for(i=30; i < 40; i++ )
	if( (s=strusage(i)) )
	    fputs( (const byte*)s, stdout);
    fflush(stdout);
}


void
usage( int level )
{
    if( !level ) {
	fprintf(stderr,"%s %s; %s\n", strusage(11), strusage(13),
						     strusage(14) );
	fflush(stderr);
    }
    else if( level == 1 ) {
	fputs(strusage(40),stderr);
	exit(2);
    }
    else if( level == 2 ) {
	puts(strusage(41));
	exit(0);
    }
}

/* Level
 *     0: Copyright String auf stderr ausgeben
 *     1: Kurzusage auf stderr ausgeben und beenden
 *     2: Langusage auf stdout ausgeben und beenden
 *    10: Return license info string
 *    11: name of program
 *    12: optional name of package which includes this program.
 *    13: version  string
 *    14: copyright string
 *    15: Short copying conditions (with LFs)
 *    16: Long copying conditions (with LFs)
 *    17: Optional printable OS name
 *    18: Optional thanks list	 (with LFs)
 *    19: Bug report info
 *20..29: Additional lib version strings.
 *30..39: Additional program info (with LFs)
 *    40: short usage note (with LF)
 *    41: long usage note (with LF)
 */
const char *
default_strusage( int level )
{
    const char *p = NULL;
    switch( level ) {
        break;
      case 11: p = "foo"; break;
      case 13: p = "0.0"; break;
      case 14: p = "Copyright (C) 2012 Free Software Foundation, Inc."; break;
      case 15: p =
"This is free software: you are free to change and redistribute it.\n"
"There is NO WARRANTY, to the extent permitted by law.\n";
        break;
      case 16:	p =
"This is free software; you can redistribute it and/or modify\n"
"it under the terms of the GNU General Public License as published by\n"
"the Free Software Foundation; either version 3 of the License, or\n"
"(at your option) any later version.\n\n"
"It is distributed in the hope that it will be useful,\n"
"but WITHOUT ANY WARRANTY; without even the implied warranty of\n"
"MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n"
"GNU General Public License for more details.\n\n"
"You should have received a copy of the GNU General Public License\n"
"along with this software.  If not, see <http://www.gnu.org/licenses/>.\n";
	break;
      case 40: /* short and long usage */
      case 41: p = ""; break;
    }

    return p;
}



#ifdef TEST
static struct {
    int verbose;
    int debug;
    char *outfile;
    char *crf;
    int myopt;
    int echo;
    int a_long_one;
}opt;

int
main(int argc, char **argv)
{
    ARGPARSE_OPTS opts[] = {
    { 'v', "verbose",   0 , "Laut sein"},
    { 'e', "echo"   ,   0 , "Zeile ausgeben, damit wir sehen, was wir einegegeben haben"},
    { 'd', "debug",     0 , "Debug\nfalls mal etasws\nSchief geht"},
    { 'o', "output",    2   },
    { 'c', "cross-ref", 2|8, "cross-reference erzeugen\n" },
    { 'm', "my-option", 1|8 },
    { 500, "a-long-option", 0 },
    {0} };
    ARGPARSE_ARGS pargs = { &argc, &argv, 2|4|32 };
    int i;

    while( ArgParse( &pargs, opts) ) {
	switch( pargs.r_opt ) {
	  case -1 : printf( "arg=`%s'\n", pargs.r.ret_str); break;
	  case 'v': opt.verbose++; break;
	  case 'e': opt.echo++; break;
	  case 'd': opt.debug++; break;
	  case 'o': opt.outfile = pargs.r.ret_str; break;
	  case 'c': opt.crf = pargs.r_type? pargs.r.ret_str:"a.crf"; break;
	  case 'm': opt.myopt = pargs.r_type? pargs.r.ret_int : 1; break;
	  case 500: opt.a_long_one++;  break;
	  default : pargs.err = 1; break; /* force warning output */
	}
    }
    for(i=0; i < argc; i++ )
	printf("%3d -> (%s)\n", i, argv[i] );
    puts("Options:");
    if( opt.verbose )
	printf("  verbose=%d\n", opt.verbose );
    if( opt.debug )
	printf("  debug=%d\n", opt.debug );
    if( opt.outfile )
	printf("  outfile=`%s'\n", opt.outfile );
    if( opt.crf )
	printf("  crffile=`%s'\n", opt.crf );
    if( opt.myopt )
	printf("  myopt=%d\n", opt.myopt );
    if( opt.a_long_one )
	printf("  a-long-one=%d\n", opt.a_long_one );
    if( opt.echo       )
	printf("  echo=%d\n", opt.echo );
    return 0;
}
#endif

/**** bottom of file ****/
