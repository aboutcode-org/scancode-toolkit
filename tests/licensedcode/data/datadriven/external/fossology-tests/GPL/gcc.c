/* Compiler driver program that can handle many languages.
   Copyright (C) 1987, 1989, 1992, 1993, 1994, 1995, 1996, 1997, 1998,
   1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 Free Software Foundation,
   Inc.

This file is part of GCC.

GCC is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation; either version 2, or (at your option) any later
version.

GCC is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License
along with GCC; see the file COPYING.  If not, write to the Free
Software Foundation, 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301, USA.

This paragraph is here to try to keep Sun CC from dying.
The number of chars here seems crucial!!!!  */

/* This program is the user interface to the C compiler and possibly to
other compilers.  It is used because compilation is a complicated procedure
which involves running several programs and passing temporary files between
them, forwarding the users switches to those programs selectively,
and deleting the temporary files at the end.

CC recognizes how to compile each input file by suffixes in the file names.
Once it knows which kind of compilation to perform, the procedure for
compilation is specified by a string called a "spec".  */

/* A Short Introduction to Adding a Command-Line Option.

   Before adding a command-line option, consider if it is really
   necessary.  Each additional command-line option adds complexity and
   is difficult to remove in subsequent versions.

   In the following, consider adding the command-line argument
   `--bar'.

   1. Each command-line option is specified in the specs file.  The
   notation is described below in the comment entitled "The Specs
   Language".  Read it.

   2. In this file, add an entry to "option_map" equating the long
   `--' argument version and any shorter, single letter version.  Read
   the comments in the declaration of "struct option_map" for an
   explanation.  Do not omit the first `-'.

   3. Look in the "specs" file to determine which program or option
   list should be given the argument, e.g., "cc1_options".  Add the
   appropriate syntax for the shorter option version to the
   corresponding "const char *" entry in this file.  Omit the first
   `-' from the option.  For example, use `-bar', rather than `--bar'.

   4. If the argument takes an argument, e.g., `--baz argument1',
   modify either DEFAULT_SWITCH_TAKES_ARG or
   DEFAULT_WORD_SWITCH_TAKES_ARG in gcc.h.  Omit the first `-'
   from `--baz'.

   5. Document the option in this file's display_help().  If the
   option is passed to a subprogram, modify its corresponding
   function, e.g., cppinit.c:print_help() or toplev.c:display_help(),
   instead.

   6. Compile and test.  Make sure that your new specs file is being
   read.  For example, use a debugger to investigate the value of
   "specs_file" in main().  */

#include "config.h"
#include "system.h"
#include "coretypes.h"
#include "multilib.h" /* before tm.h */
#include "tm.h"
#include <signal.h>
#if ! defined( SIGCHLD ) && defined( SIGCLD )
#  define SIGCHLD SIGCLD
#endif
#include "xregex.h"
#include "obstack.h"
#include "intl.h"
#include "prefix.h"
#include "gcc.h"
#include "flags.h"
#include "opts.h"

/* By default there is no special suffix for target executables.  */
/* FIXME: when autoconf is fixed, remove the host check - dj */
#if defined(TARGET_EXECUTABLE_SUFFIX) && defined(HOST_EXECUTABLE_SUFFIX)
#define HAVE_TARGET_EXECUTABLE_SUFFIX
#endif

/* By default there is no special suffix for host executables.  */
#ifdef HOST_EXECUTABLE_SUFFIX
#define HAVE_HOST_EXECUTABLE_SUFFIX
#else
#define HOST_EXECUTABLE_SUFFIX ""
#endif

/* By default, the suffix for target object files is ".o".  */
#ifdef TARGET_OBJECT_SUFFIX
#define HAVE_TARGET_OBJECT_SUFFIX
#else
#define TARGET_OBJECT_SUFFIX ".o"
#endif

static const char dir_separator_str[] = { DIR_SEPARATOR, 0 };

/* Most every one is fine with LIBRARY_PATH.  For some, it conflicts.  */
#ifndef LIBRARY_PATH_ENV
#define LIBRARY_PATH_ENV "LIBRARY_PATH"
#endif

#ifndef HAVE_KILL
#define kill(p,s) raise(s)
#endif

/* If a stage of compilation returns an exit status >= 1,
   compilation of that file ceases.  */

#define MIN_FATAL_STATUS 1

/* Flag set by cppspec.c to 1.  */
int is_cpp_driver;

/* Flag saying to pass the greatest exit code returned by a sub-process
   to the calling program.  */
static int pass_exit_codes;

/* Definition of string containing the arguments given to configure.  */
#include "configargs.h"

/* Flag saying to print the directories gcc will search through looking for
   programs, libraries, etc.  */

static int print_search_dirs;

/* Flag saying to print the full filename of this file
   as found through our usual search mechanism.  */

static const char *print_file_name = NULL;

/* As print_file_name, but search for executable file.  */

static const char *print_prog_name = NULL;

/* Flag saying to print the relative path we'd use to
   find libgcc.a given the current compiler flags.  */

static int print_multi_directory;

/* Flag saying to print the relative path we'd use to
   find OS libraries given the current compiler flags.  */

static int print_multi_os_directory;

/* Flag saying to print the list of subdirectories and
   compiler flags used to select them in a standard form.  */

static int print_multi_lib;

/* Flag saying to print the command line options understood by gcc and its
   sub-processes.  */

static int print_help_list;

/* Flag indicating whether we should print the command and arguments */

static int verbose_flag;

/* Flag indicating whether we should ONLY print the command and
   arguments (like verbose_flag) without executing the command.
   Displayed arguments are quoted so that the generated command
   line is suitable for execution.  This is intended for use in
   shell scripts to capture the driver-generated command line.  */
static int verbose_only_flag;

/* Flag indicating to print target specific command line options.  */

static int target_help_flag;

/* Flag indicating whether we should report subprocess execution times
   (if this is supported by the system - see pexecute.c).  */

static int report_times;

/* Nonzero means place this string before uses of /, so that include
   and library files can be found in an alternate location.  */

#ifdef TARGET_SYSTEM_ROOT
static const char *target_system_root = TARGET_SYSTEM_ROOT;
#else
static const char *target_system_root = 0;
#endif

/* Nonzero means pass the updated target_system_root to the compiler.  */

static int target_system_root_changed;

/* Nonzero means append this string to target_system_root.  */

static const char *target_sysroot_suffix = 0;

/* Nonzero means append this string to target_system_root for headers.  */

static const char *target_sysroot_hdrs_suffix = 0;

/* Nonzero means write "temp" files in source directory
   and use the source file's name in them, and don't delete them.  */

static int save_temps_flag;

/* Nonzero means pass multiple source files to the compiler at one time.  */

static int combine_flag = 0;

/* Nonzero means use pipes to communicate between subprocesses.
   Overridden by either of the above two flags.  */

static int use_pipes;

/* The compiler version.  */

static const char *compiler_version;

/* The target version specified with -V */

static const char *const spec_version = DEFAULT_TARGET_VERSION;

/* The target machine specified with -b.  */

static const char *spec_machine = DEFAULT_TARGET_MACHINE;

/* Nonzero if cross-compiling.
   When -b is used, the value comes from the `specs' file.  */

#ifdef CROSS_COMPILE
static const char *cross_compile = "1";
#else
static const char *cross_compile = "0";
#endif

#ifdef MODIFY_TARGET_NAME

/* Information on how to alter the target name based on a command-line
   switch.  The only case we support now is simply appending or deleting a
   string to or from the end of the first part of the configuration name.  */

static const struct modify_target
{
  const char *const sw;
  const enum add_del {ADD, DELETE} add_del;
  const char *const str;
}
modify_target[] = MODIFY_TARGET_NAME;
#endif

/* The number of errors that have occurred; the link phase will not be
   run if this is nonzero.  */
static int error_count = 0;

/* Greatest exit code of sub-processes that has been encountered up to
   now.  */
static int greatest_status = 1;

/* This is the obstack which we use to allocate many strings.  */

static struct obstack obstack;

/* This is the obstack to build an environment variable to pass to
   collect2 that describes all of the relevant switches of what to
   pass the compiler in building the list of pointers to constructors
   and destructors.  */

static struct obstack collect_obstack;

/* Forward declaration for prototypes.  */
struct path_prefix;
struct prefix_list;

static void init_spec (void);
static void store_arg (const char *, int, int);
static char *load_specs (const char *);
static void read_specs (const char *, int);
static void set_spec (const char *, const char *);
static struct compiler *lookup_compiler (const char *, size_t, const char *);
static char *build_search_list (const struct path_prefix *, const char *,
				bool, bool);
static void putenv_from_prefixes (const struct path_prefix *, const char *,
				  bool);
static int access_check (const char *, int);
static char *find_a_file (const struct path_prefix *, const char *, int, bool);
static void add_prefix (struct path_prefix *, const char *, const char *,
			int, int, int);
static void add_sysrooted_prefix (struct path_prefix *, const char *,
				  const char *, int, int, int);
static void translate_options (int *, const char *const **);
static char *skip_whitespace (char *);
static void delete_if_ordinary (const char *);
static void delete_temp_files (void);
static void delete_failure_queue (void);
static void clear_failure_queue (void);
static int check_live_switch (int, int);
static const char *handle_braces (const char *);
static inline bool input_suffix_matches (const char *, const char *);
static inline bool switch_matches (const char *, const char *, int);
static inline void mark_matching_switches (const char *, const char *, int);
static inline void process_marked_switches (void);
static const char *process_brace_body (const char *, const char *, const char *, int, int);
static const struct spec_function *lookup_spec_function (const char *);
static const char *eval_spec_function (const char *, const char *);
static const char *handle_spec_function (const char *);
static char *save_string (const char *, int);
static void set_collect_gcc_options (void);
static int do_spec_1 (const char *, int, const char *);
static int do_spec_2 (const char *);
static void do_option_spec (const char *, const char *);
static void do_self_spec (const char *);
static const char *find_file (const char *);
static int is_directory (const char *, bool);
static const char *validate_switches (const char *);
static void validate_all_switches (void);
static inline void validate_switches_from_spec (const char *);
static void give_switch (int, int);
static int used_arg (const char *, int);
static int default_arg (const char *, int);
static void set_multilib_dir (void);
static void print_multilib_info (void);
static void perror_with_name (const char *);
static void fatal_ice (const char *, ...) ATTRIBUTE_PRINTF_1 ATTRIBUTE_NORETURN;
static void notice (const char *, ...) ATTRIBUTE_PRINTF_1;
static void display_help (void);
static void add_preprocessor_option (const char *, int);
static void add_assembler_option (const char *, int);
static void add_linker_option (const char *, int);
static void process_command (int, const char **);
static int execute (void);
static void alloc_args (void);
static void clear_args (void);
static void fatal_error (int);
#if defined(ENABLE_SHARED_LIBGCC) && !defined(REAL_LIBGCC_SPEC)
static void init_gcc_specs (struct obstack *, const char *, const char *,
			    const char *);
#endif
#if defined(HAVE_TARGET_OBJECT_SUFFIX) || defined(HAVE_TARGET_EXECUTABLE_SUFFIX)
static const char *convert_filename (const char *, int, int);
#endif

static const char *if_exists_spec_function (int, const char **);
static const char *if_exists_else_spec_function (int, const char **);
static const char *replace_outfile_spec_function (int, const char **);
static const char *version_compare_spec_function (int, const char **);
static const char *include_spec_function (int, const char **);

/* The Specs Language

Specs are strings containing lines, each of which (if not blank)
is made up of a program name, and arguments separated by spaces.
The program name must be exact and start from root, since no path
is searched and it is unreliable to depend on the current working directory.
Redirection of input or output is not supported; the subprograms must
accept filenames saying what files to read and write.

In addition, the specs can contain %-sequences to substitute variable text
or for conditional text.  Here is a table of all defined %-sequences.
Note that spaces are not generated automatically around the results of
expanding these sequences; therefore, you can concatenate them together
or with constant text in a single argument.

 %%	substitute one % into the program name or argument.
 %i     substitute the name of the input file being processed.
 %b     substitute the basename of the input file being processed.
	This is the substring up to (and not including) the last period
	and not including the directory.
 %B	same as %b, but include the file suffix (text after the last period).
 %gSUFFIX
	substitute a file name that has suffix SUFFIX and is chosen
	once per compilation, and mark the argument a la %d.  To reduce
	exposure to denial-of-service attacks, the file name is now
	chosen in a way that is hard to predict even when previously
	chosen file names are known.  For example, `%g.s ... %g.o ... %g.s'
	might turn into `ccUVUUAU.s ccXYAXZ12.o ccUVUUAU.s'.  SUFFIX matches
	the regexp "[.0-9A-Za-z]*%O"; "%O" is treated exactly as if it
	had been pre-processed.  Previously, %g was simply substituted
	with a file name chosen once per compilation, without regard
	to any appended suffix (which was therefore treated just like
	ordinary text), making such attacks more likely to succeed.
 %|SUFFIX
	like %g, but if -pipe is in effect, expands simply to "-".
 %mSUFFIX
        like %g, but if -pipe is in effect, expands to nothing.  (We have both
	%| and %m to accommodate differences between system assemblers; see
	the AS_NEEDS_DASH_FOR_PIPED_INPUT target macro.)
 %uSUFFIX
	like %g, but generates a new temporary file name even if %uSUFFIX
	was already seen.
 %USUFFIX
	substitutes the last file name generated with %uSUFFIX, generating a
	new one if there is no such last file name.  In the absence of any
	%uSUFFIX, this is just like %gSUFFIX, except they don't share
	the same suffix "space", so `%g.s ... %U.s ... %g.s ... %U.s'
	would involve the generation of two distinct file names, one
	for each `%g.s' and another for each `%U.s'.  Previously, %U was
	simply substituted with a file name chosen for the previous %u,
	without regard to any appended suffix.
 %jSUFFIX
        substitutes the name of the HOST_BIT_BUCKET, if any, and if it is
        writable, and if save-temps is off; otherwise, substitute the name
        of a temporary file, just like %u.  This temporary file is not
        meant for communication between processes, but rather as a junk
        disposal mechanism.
 %.SUFFIX
        substitutes .SUFFIX for the suffixes of a matched switch's args when
        it is subsequently output with %*. SUFFIX is terminated by the next
        space or %.
 %d	marks the argument containing or following the %d as a
	temporary file name, so that that file will be deleted if CC exits
	successfully.  Unlike %g, this contributes no text to the argument.
 %w	marks the argument containing or following the %w as the
	"output file" of this compilation.  This puts the argument
	into the sequence of arguments that %o will substitute later.
 %V	indicates that this compilation produces no "output file".
 %W{...}
	like %{...} but mark last argument supplied within
	as a file to be deleted on failure.
 %o	substitutes the names of all the output files, with spaces
	automatically placed around them.  You should write spaces
	around the %o as well or the results are undefined.
	%o is for use in the specs for running the linker.
	Input files whose names have no recognized suffix are not compiled
	at all, but they are included among the output files, so they will
	be linked.
 %O	substitutes the suffix for object files.  Note that this is
        handled specially when it immediately follows %g, %u, or %U
	(with or without a suffix argument) because of the need for
	those to form complete file names.  The handling is such that
	%O is treated exactly as if it had already been substituted,
	except that %g, %u, and %U do not currently support additional
	SUFFIX characters following %O as they would following, for
	example, `.o'.
 %I	Substitute any of -iprefix (made from GCC_EXEC_PREFIX), -isysroot
	(made from TARGET_SYSTEM_ROOT), -isystem (made from COMPILER_PATH
	and -B options) and -imultilib as necessary.
 %s     current argument is the name of a library or startup file of some sort.
        Search for that file in a standard list of directories
	and substitute the full name found.
 %eSTR  Print STR as an error message.  STR is terminated by a newline.
        Use this when inconsistent options are detected.
 %nSTR  Print STR as a notice.  STR is terminated by a newline.
 %x{OPTION}	Accumulate an option for %X.
 %X	Output the accumulated linker options specified by compilations.
 %Y	Output the accumulated assembler options specified by compilations.
 %Z	Output the accumulated preprocessor options specified by compilations.
 %a     process ASM_SPEC as a spec.
        This allows config.h to specify part of the spec for running as.
 %A	process ASM_FINAL_SPEC as a spec.  A capital A is actually
	used here.  This can be used to run a post-processor after the
	assembler has done its job.
 %D	Dump out a -L option for each directory in startfile_prefixes.
	If multilib_dir is set, extra entries are generated with it affixed.
 %l     process LINK_SPEC as a spec.
 %L     process LIB_SPEC as a spec.
 %G     process LIBGCC_SPEC as a spec.
 %R     Output the concatenation of target_system_root and
        target_sysroot_suffix.
 %S     process STARTFILE_SPEC as a spec.  A capital S is actually used here.
 %E     process ENDFILE_SPEC as a spec.  A capital E is actually used here.
 %C     process CPP_SPEC as a spec.
 %1	process CC1_SPEC as a spec.
 %2	process CC1PLUS_SPEC as a spec.
 %*	substitute the variable part of a matched option.  (See below.)
	Note that each comma in the substituted string is replaced by
	a single space.
 %<S    remove all occurrences of -S from the command line.
        Note - this command is position dependent.  % commands in the
        spec string before this one will see -S, % commands in the
        spec string after this one will not.
 %<S*	remove all occurrences of all switches beginning with -S from the
        command line.
 %:function(args)
	Call the named function FUNCTION, passing it ARGS.  ARGS is
	first processed as a nested spec string, then split into an
	argument vector in the usual fashion.  The function returns
	a string which is processed as if it had appeared literally
	as part of the current spec.
 %{S}   substitutes the -S switch, if that switch was given to CC.
	If that switch was not specified, this substitutes nothing.
	Here S is a metasyntactic variable.
 %{S*}  substitutes all the switches specified to CC whose names start
	with -S.  This is used for -o, -I, etc; switches that take
	arguments.  CC considers `-o foo' as being one switch whose
	name starts with `o'.  %{o*} would substitute this text,
	including the space; thus, two arguments would be generated.
 %{S*&T*} likewise, but preserve order of S and T options (the order
	of S and T in the spec is not significant).  Can be any number
	of ampersand-separated variables; for each the wild card is
	optional.  Useful for CPP as %{D*&U*&A*}.

 %{S:X}   substitutes X, if the -S switch was given to CC.
 %{!S:X}  substitutes X, if the -S switch was NOT given to CC.
 %{S*:X}  substitutes X if one or more switches whose names start
          with -S was given to CC.  Normally X is substituted only
          once, no matter how many such switches appeared.  However,
          if %* appears somewhere in X, then X will be substituted
          once for each matching switch, with the %* replaced by the
          part of that switch that matched the '*'.
 %{.S:X}  substitutes X, if processing a file with suffix S.
 %{!.S:X} substitutes X, if NOT processing a file with suffix S.

 %{S|T:X} substitutes X if either -S or -T was given to CC.  This may be
	  combined with !, ., and * as above binding stronger than the OR.
	  If %* appears in X, all of the alternatives must be starred, and
	  only the first matching alternative is substituted.
 %{S:X;   if S was given to CC, substitutes X;
   T:Y;   else if T was given to CC, substitutes Y;
    :D}   else substitutes D.  There can be as many clauses as you need.
          This may be combined with ., !, |, and * as above.

 %(Spec) processes a specification defined in a specs file as *Spec:
 %[Spec] as above, but put __ around -D arguments

The conditional text X in a %{S:X} or similar construct may contain
other nested % constructs or spaces, or even newlines.  They are
processed as usual, as described above.  Trailing white space in X is
ignored.  White space may also appear anywhere on the left side of the
colon in these constructs, except between . or * and the corresponding
word.

The -O, -f, -m, and -W switches are handled specifically in these
constructs.  If another value of -O or the negated form of a -f, -m, or
-W switch is found later in the command line, the earlier switch
value is ignored, except with {S*} where S is just one letter; this
passes all matching options.

The character | at the beginning of the predicate text is used to indicate
that a command should be piped to the following command, but only if -pipe
is specified.

Note that it is built into CC which switches take arguments and which
do not.  You might think it would be useful to generalize this to
allow each compiler's spec to say which switches take arguments.  But
this cannot be done in a consistent fashion.  CC cannot even decide
which input files have been specified without knowing which switches
take arguments, and it must know which input files to compile in order
to tell which compilers to run.

CC also knows implicitly that arguments starting in `-l' are to be
treated as compiler output files, and passed to the linker in their
proper position among the other output files.  */

/* Define the macros used for specs %a, %l, %L, %S, %C, %1.  */

/* config.h can define ASM_SPEC to provide extra args to the assembler
   or extra switch-translations.  */
#ifndef ASM_SPEC
#define ASM_SPEC ""
#endif

/* config.h can define ASM_FINAL_SPEC to run a post processor after
   the assembler has run.  */
#ifndef ASM_FINAL_SPEC
#define ASM_FINAL_SPEC ""
#endif

/* config.h can define CPP_SPEC to provide extra args to the C preprocessor
   or extra switch-translations.  */
#ifndef CPP_SPEC
#define CPP_SPEC ""
#endif

/* config.h can define CC1_SPEC to provide extra args to cc1 and cc1plus
   or extra switch-translations.  */
#ifndef CC1_SPEC
#define CC1_SPEC ""
#endif

/* config.h can define CC1PLUS_SPEC to provide extra args to cc1plus
   or extra switch-translations.  */
#ifndef CC1PLUS_SPEC
#define CC1PLUS_SPEC ""
#endif

/* config.h can define LINK_SPEC to provide extra args to the linker
   or extra switch-translations.  */
#ifndef LINK_SPEC
#define LINK_SPEC ""
#endif

/* config.h can define LIB_SPEC to override the default libraries.  */
#ifndef LIB_SPEC
#define LIB_SPEC "%{!shared:%{g*:-lg} %{!p:%{!pg:-lc}}%{p:-lc_p}%{pg:-lc_p}}"
#endif

/* mudflap specs */
#ifndef MFWRAP_SPEC
/* XXX: valid only for GNU ld */
/* XXX: should exactly match hooks provided by libmudflap.a */
#define MFWRAP_SPEC " %{static: %{fmudflap|fmudflapth: \
 --wrap=malloc --wrap=free --wrap=calloc --wrap=realloc\
 --wrap=mmap --wrap=munmap --wrap=alloca\
} %{fmudflapth: --wrap=pthread_create\
}} %{fmudflap|fmudflapth: --wrap=main}"
#endif
#ifndef MFLIB_SPEC
#define MFLIB_SPEC "%{fmudflap|fmudflapth: -export-dynamic}"
#endif

/* config.h can define LIBGCC_SPEC to override how and when libgcc.a is
   included.  */
#ifndef LIBGCC_SPEC
#if defined(REAL_LIBGCC_SPEC)
#define LIBGCC_SPEC REAL_LIBGCC_SPEC
#elif defined(LINK_LIBGCC_SPECIAL_1)
/* Have gcc do the search for libgcc.a.  */
#define LIBGCC_SPEC "libgcc.a%s"
#else
#define LIBGCC_SPEC "-lgcc"
#endif
#endif

/* config.h can define STARTFILE_SPEC to override the default crt0 files.  */
#ifndef STARTFILE_SPEC
#define STARTFILE_SPEC  \
  "%{!shared:%{pg:gcrt0%O%s}%{!pg:%{p:mcrt0%O%s}%{!p:crt0%O%s}}}"
#endif

/* config.h can define SWITCHES_NEED_SPACES to control which options
   require spaces between the option and the argument.  */
#ifndef SWITCHES_NEED_SPACES
#define SWITCHES_NEED_SPACES ""
#endif

/* config.h can define ENDFILE_SPEC to override the default crtn files.  */
#ifndef ENDFILE_SPEC
#define ENDFILE_SPEC ""
#endif

#ifndef LINKER_NAME
#define LINKER_NAME "collect2"
#endif

/* Define ASM_DEBUG_SPEC to be a spec suitable for translating '-g'
   to the assembler.  */
#ifndef ASM_DEBUG_SPEC
# if defined(DBX_DEBUGGING_INFO) && defined(DWARF2_DEBUGGING_INFO) \
     && defined(HAVE_AS_GDWARF2_DEBUG_FLAG) && defined(HAVE_AS_GSTABS_DEBUG_FLAG)
#  define ASM_DEBUG_SPEC					\
      (PREFERRED_DEBUGGING_TYPE == DBX_DEBUG			\
       ? "%{gdwarf-2*:--gdwarf2}%{!gdwarf-2*:%{g*:--gstabs}}"	\
       : "%{gstabs*:--gstabs}%{!gstabs*:%{g*:--gdwarf2}}")
# else
#  if defined(DBX_DEBUGGING_INFO) && defined(HAVE_AS_GSTABS_DEBUG_FLAG)
#   define ASM_DEBUG_SPEC "%{g*:--gstabs}"
#  endif
#  if defined(DWARF2_DEBUGGING_INFO) && defined(HAVE_AS_GDWARF2_DEBUG_FLAG)
#   define ASM_DEBUG_SPEC "%{g*:--gdwarf2}"
#  endif
# endif
#endif
#ifndef ASM_DEBUG_SPEC
# define ASM_DEBUG_SPEC ""
#endif

/* Here is the spec for running the linker, after compiling all files.  */

/* This is overridable by the target in case they need to specify the
   -lgcc and -lc order specially, yet not require them to override all
   of LINK_COMMAND_SPEC.  */
#ifndef LINK_GCC_C_SEQUENCE_SPEC
#define LINK_GCC_C_SEQUENCE_SPEC "%G %L %G"
#endif

#ifndef LINK_SSP_SPEC
#ifdef TARGET_LIBC_PROVIDES_SSP
#define LINK_SSP_SPEC "%{fstack-protector:}"
#else
#define LINK_SSP_SPEC "%{fstack-protector|fstack-protector-all:-lssp_nonshared -lssp}"
#endif
#endif

	{
	  /* translate_options () has turned --version into -fversion.  */
	  printf (_("%s (GCC) %s\n"), programname, version_string);
	  printf ("Copyright %s 2007 Free Software Foundation, Inc.\n",
		  _("(C)"));
	  fputs (_("This is free software; see the source for copying conditions.  There is NO\n\
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.\n\n"),
		 stdout);
	  exit (0);
	}
      else if (strcmp (argv[i], "-fhelp") == 0)
	{
	  /* translate_options () has turned --help into -fhelp.  */
	  print_help_list = 1;

	  /* We will be passing a dummy file on to the sub-processes.  */
	  n_infiles++;
	  n_switches++;

	  /* CPP driver cannot obtain switch from cc1_options.  */
	  if (is_cpp_driver)
	    add_preprocessor_option ("--help", 6);
	  add_assembler_option ("--help", 6);
	  add_linker_option ("--help", 6);
	}
      else if (strcmp (argv[i], "-ftarget-help") == 0)
	{
	  /* translate_options() has turned --target-help into -ftarget-help.  */
	  target_help_flag = 1;

	  /* We will be passing a dummy file on to the sub-processes.  */
	  n_infiles++;
	  n_switches++;

	  /* CPP driver cannot obtain switch from cc1_options.  */
	  if (is_cpp_driver)
	    add_preprocessor_option ("--target-help", 13);
	  add_assembler_option ("--target-help", 13);
	  add_linker_option ("--target-help", 13);
	}
      else if (! strcmp (argv[i], "-pass-exit-codes"))
	{
	  pass_exit_codes = 1;
	  n_switches++;
	}
      else if (! strcmp (argv[i], "-print-search-dirs"))
	print_search_dirs = 1;
      else if (! strcmp (argv[i], "-print-libgcc-file-name"))
	print_file_name = "libgcc.a";
      else if (! strncmp (argv[i], "-print-file-name=", 17))
	print_file_name = argv[i] + 17;
      else if (! strncmp (argv[i], "-print-prog-name=", 17))
	print_prog_name = argv[i] + 17;
      else if (! strcmp (argv[i], "-print-multi-lib"))
	print_multi_lib = 1;
      else if (! strcmp (argv[i], "-print-multi-directory"))
	print_multi_directory = 1;
      else if (! strcmp (argv[i], "-print-multi-os-directory"))
	print_multi_os_directory = 1;
      else if (! strncmp (argv[i], "-Wa,", 4))
	{
	  int prev, j;
	  /* Pass the rest of this option to the assembler.  */

