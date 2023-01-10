# Coding conventions in the Samba tree

## Quick Start

Coding style guidelines are about reducing the number of unnecessary
reformatting patches and making things easier for developers to work
together.
You don't have to like them or even agree with them, but once put in place
we all have to abide by them (or vote to change them).  However, coding
style should never outweigh coding itself and so the guidelines
described here are hopefully easy enough to follow as they are very
common and supported by tools and editors.

The basic style for C code is the Linux kernel coding style (See
Documentation/CodingStyle in the kernel source tree). This closely matches
what most Samba developers use already anyways, with a few exceptions as
mentioned below.

The coding style for Python code is documented in
[PEP8](https://www.python.org/dev/peps/pep-0008/). New Python code
should be compatible with Python 3.6 onwards.

But to save you the trouble of reading the Linux kernel style guide, here
are the highlights.

* Maximum Line Width is 80 Characters
  The reason is not about people with low-res screens but rather sticking
  to 80 columns prevents you from easily nesting more than one level of
  if statements or other code blocks.  Use [source3/script/count_80_col.pl](source3/script/count_80_col.pl)
  to check your changes.

* Use 8 Space Tabs to Indent
  No whitespace fillers.

* No Trailing Whitespace
  Use [source3/script/strip_trail_ws.pl](source3/script/strip_trail_ws.pl) to clean up your files before
  committing.

* Follow the K&R guidelines.  We won't go through all of them here. Do you
  have a copy of "The C Programming Language" anyways right? You can also use
  the [format_indent.sh script found in source3/script/](source3/script/format_indent.sh) if all else fails.



## Editor Hints

### Emacs

Add the follow to your $HOME/.emacs file:

```
  (add-hook 'c-mode-hook
	(lambda ()
		(c-set-style "linux")
		(c-toggle-auto-state)))
```


### Vi

(Thanks to SATOH Fumiyasu <fumiyas@osstech.jp> for these hints):

For the basic vi editor included with all variants of \*nix, add the
following to $HOME/.exrc:

```
  set tabstop=8
  set shiftwidth=8
```

For Vim, the following settings in $HOME/.vimrc will also deal with
displaying trailing whitespace:

```
  if has("syntax") && (&t_Co > 2 || has("gui_running"))
	syntax on
	function! ActivateInvisibleCharIndicator()
		syntax match TrailingSpace "[ \t]\+$" display containedin=ALL
		highlight TrailingSpace ctermbg=Red
	endf
	autocmd BufNewFile,BufRead * call ActivateInvisibleCharIndicator()
  endif
  " Show tabs, trailing whitespace, and continued lines visually
  set list listchars=tab:»·,trail:·,extends:…

  " highlight overly long lines same as TODOs.
  set textwidth=80
  autocmd BufNewFile,BufRead *.c,*.h exec 'match Todo /\%>' . &textwidth . 'v.\+/'
```

### How to use clang-format

Install 'git-format-clang' which is part of the clang suite (Fedora:
git-clang-format, openSUSE: clang-tools).

Now do your changes and stage them with `git add`. Once they are staged
format the code using `git clang-format` before you commit.

Now the formatting changed can be viewed with `git diff` against the
staged changes.

## FAQ & Statement Reference

### Comments

Comments should always use the standard C syntax.  C++
style comments are not currently allowed.

The lines before a comment should be empty. If the comment directly
belongs to the following code, there should be no empty line
after the comment, except if the comment contains a summary
of multiple following code blocks.

This is good:

```
	...
	int i;

	/*
	 * This is a multi line comment,
	 * which explains the logical steps we have to do:
	 *
	 * 1. We need to set i=5, because...
	 * 2. We need to call complex_fn1
	 */

	/* This is a one line comment about i = 5. */
	i = 5;

	/*
	 * This is a multi line comment,
	 * explaining the call to complex_fn1()
	 */
	ret = complex_fn1();
	if (ret != 0) {
	...

	/**
	 * @brief This is a doxygen comment.
	 *
	 * This is a more detailed explanation of
	 * this simple function.
	 *
	 * @param[in]   param1     The parameter value of the function.
	 *
	 * @param[out]  result1    The result value of the function.
	 *
	 * @return              0 on success and -1 on error.
	 */
	int example(int param1, int *result1);
```

This is bad:

```
	...
	int i;
	/*
	 * This is a multi line comment,
	 * which explains the logical steps we have to do:
	 *
	 * 1. We need to set i=5, because...
	 * 2. We need to call complex_fn1
	 */
	/* This is a one line comment about i = 5. */
	i = 5;
	/*
	 * This is a multi line comment,
	 * explaining the call to complex_fn1()
	 */
	ret = complex_fn1();
	if (ret != 0) {
	...

	/*This is a one line comment.*/

	/* This is a multi line comment,
	   with some more words...*/

	/*
	 * This is a multi line comment,
	 * with some more words...*/
```

### Indention & Whitespace & 80 columns

To avoid confusion, indentations have to be tabs with length 8 (not 8
' ' characters).  When wrapping parameters for function calls,
align the parameter list with the first parameter on the previous line.
Use tabs to get as close as possible and then fill in the final 7
characters or less with whitespace.  For example,

```
	var1 = foo(arg1, arg2,
		   arg3);
```

The previous example is intended to illustrate alignment of function
parameters across lines and not as encourage for gratuitous line
splitting.  Never split a line before columns 70 - 79 unless you
have a really good reason. Be smart about formatting.

One exception to the previous rule is function calls, declarations, and
definitions. In function calls, declarations, and definitions, either the
declaration is a one-liner, or each parameter is listed on its own
line. The rationale is that if there are many parameters, each one
should be on its own line to make tracking interface changes easier.


## If, switch, & Code blocks

Always follow an `if` keyword with a space but don't include additional
spaces following or preceding the parentheses in the conditional.
This is good:

```
	if (x == 1)
```

This is bad:

```
	if ( x == 1 )
```

Yes we have a lot of code that uses the second form and we are trying
to clean it up without being overly intrusive.

Note that this is a rule about parentheses following keywords and not
functions.  Don't insert a space between the name and left parentheses when
invoking functions.

Braces for code blocks used by `for`, `if`, `switch`, `while`, `do..while`, etc.
should begin on the same line as the statement keyword and end on a line
of their own. You should always include braces, even if the block only
contains one statement.  NOTE: Functions are different and the beginning left
brace should be located in the first column on the next line.

If the beginning statement has to be broken across lines due to length,
the beginning brace should be on a line of its own.

The exception to the ending rule is when the closing brace is followed by
another language keyword such as else or the closing while in a `do..while`
loop.

Good examples:

```
	if (x == 1) {
		printf("good\n");
	}

	for (x=1; x<10; x++) {
		print("%d\n", x);
	}

	for (really_really_really_really_long_var_name=0;
	     really_really_really_really_long_var_name<10;
	     really_really_really_really_long_var_name++)
	{
		print("%d\n", really_really_really_really_long_var_name);
	}

	do {
		printf("also good\n");
	} while (1);
```

Bad examples:

```
	while (1)
	{
		print("I'm in a loop!\n"); }

	for (x=1;
	     x<10;
	     x++)
	{
		print("no good\n");
	}

	if (i < 10)
		print("I should be in braces.\n");
```


### Goto

While many people have been academically taught that `goto`s are
fundamentally evil, they can greatly enhance readability and reduce memory
leaks when used as the single exit point from a function. But in no Samba
world what so ever is a goto outside of a function or block of code a good
idea.

Good Examples:

```
	int function foo(int y)
	{
		int *z = NULL;
		int ret = 0;

		if (y < 10) {
			z = malloc(sizeof(int) * y);
			if (z == NULL) {
				ret = 1;
				goto done;
			}
		}

		print("Allocated %d elements.\n", y);

	 done:
		if (z != NULL) {
			free(z);
		}

		return ret;
	}
```


### Primitive Data Types

Samba has large amounts of historical code which makes use of data types
commonly supported by the C99 standard. However, at the time such types
as boolean and exact width integers did not exist and Samba developers
were forced to provide their own.  Now that these types are guaranteed to
be available either as part of the compiler C99 support or from
lib/replace/, new code should adhere to the following conventions:

  * Booleans are of type `bool` (not `BOOL`)
  * Boolean values are `true` and `false` (not `True` or `False`)
  * Exact width integers are of type `[u]int[8|16|32|64]_t`

Most of the time a good name for a boolean variable is 'ok'. Here is an
example we often use:

```
	bool ok;

	ok = foo();
	if (!ok) {
		/* do something */
	}
```

It makes the code more readable and is easy to debug.

### Typedefs

Samba tries to avoid `typedef struct { .. } x_t;` so we do always try to use
`struct x { .. };`. We know there are still such typedefs in the code,
but for new code, please don't do that anymore.

### Initialize pointers

All pointer variables MUST be initialized to NULL. History has
demonstrated that uninitialized pointer variables have lead to various
bugs and security issues.

Pointers MUST be initialized even if the assignment directly follows
the declaration, like pointer2 in the example below, because the
instructions sequence may change over time.

Good Example:

```
	char *pointer1 = NULL;
	char *pointer2 = NULL;

	pointer2 = some_func2();

	...

	pointer1 = some_func1();
```

Bad Example:

```
	char *pointer1;
	char *pointer2;

	pointer2 = some_func2();

	...

	pointer1 = some_func1();
```

### Make use of helper variables

Please try to avoid passing function calls as function parameters
in new code. This makes the code much easier to read and
it's also easier to use the "step" command within gdb.

Good Example:

```
	char *name = NULL;
	int ret;

	name = get_some_name();
	if (name == NULL) {
		...
	}

	ret = some_function_my_name(name);
	...
```


Bad Example:

```
	ret = some_function_my_name(get_some_name());
	...
```

Please try to avoid passing function return values to if- or
while-conditions. The reason for this is better handling of code under a
debugger.

Good example:

```
	x = malloc(sizeof(short)*10);
	if (x == NULL) {
		fprintf(stderr, "Unable to alloc memory!\n");
	}
```

Bad example:

```
	if ((x = malloc(sizeof(short)*10)) == NULL ) {
		fprintf(stderr, "Unable to alloc memory!\n");
	}
```

There are exceptions to this rule. One example is walking a data structure in
an iterator style:

```
	while ((opt = poptGetNextOpt(pc)) != -1) {
		   ... do something with opt ...
	}
```

Another exception: DBG messages for example printing a SID or a GUID:
Here we don't expect any surprise from the printing functions, and the
main reason of this guideline is to make debugging easier. That reason
rarely exists for this particular use case, and we gain some
efficiency because the DBG_ macros don't evaluate their arguments if
the debuglevel is not high enough.

```
	if (!NT_STATUS_IS_OK(status)) {
		struct dom_sid_buf sid_buf;
		struct GUID_txt_buf guid_buf;
		DBG_WARNING(
		    "objectSID [%s] for GUID [%s] invalid\n",
		    dom_sid_str_buf(objectsid, &sid_buf),
		    GUID_buf_string(&cache->entries[idx], &guid_buf));
	}
```

But in general, please try to avoid this pattern.


### Control-Flow changing macros

Macros like `NT_STATUS_NOT_OK_RETURN` that change control flow
(`return`/`goto`/etc) from within the macro are considered bad, because
they look like function calls that never change control flow. Please
do not use them in new code.

The only exception is the test code that depends repeated use of calls
like `CHECK_STATUS`, `CHECK_VAL` and others.


### Error and out logic

Don't do this:

```
	frame = talloc_stackframe();

	if (ret == LDB_SUCCESS) {
		if (result->count == 0) {
			ret = LDB_ERR_NO_SUCH_OBJECT;
		} else {
			struct ldb_message *match =
				get_best_match(dn, result);
			if (match == NULL) {
				TALLOC_FREE(frame);
				return LDB_ERR_OPERATIONS_ERROR;
			}
			*msg = talloc_move(mem_ctx, &match);
		}
	}

	TALLOC_FREE(frame);
	return ret;
```

It should be:

```
	frame = talloc_stackframe();

	if (ret != LDB_SUCCESS) {
		TALLOC_FREE(frame);
		return ret;
	}

	if (result->count == 0) {
		TALLOC_FREE(frame);
		return LDB_ERR_NO_SUCH_OBJECT;
	}

	match = get_best_match(dn, result);
	if (match == NULL) {
		TALLOC_FREE(frame);
		return LDB_ERR_OPERATIONS_ERROR;
	}

	*msg = talloc_move(mem_ctx, &match);
	TALLOC_FREE(frame);
	return LDB_SUCCESS;
```


### DEBUG statements

Use these following macros instead of DEBUG:

```
DBG_ERR         log level 0		error conditions
DBG_WARNING     log level 1		warning conditions
DBG_NOTICE      log level 3		normal, but significant, condition
DBG_INFO        log level 5		informational message
DBG_DEBUG       log level 10		debug-level message
```

Example usage:

```
DBG_ERR("Memory allocation failed\n");
DBG_DEBUG("Received %d bytes\n", count);
```

The messages from these macros are automatically prefixed with the
function name.



### PRINT format specifiers PRIuxx

Use %PRIu32 instead of %u for uint32_t. Do not assume that this is valid:

/usr/include/inttypes.h
104:# define PRIu32             "u"

It could be possible to have a platform where "unsigned" is 64-bit. In theory
even 16-bit. The point is that "unsigned" being 32-bit is nowhere specified.
The PRIuxx specifiers are standard.

Example usage:

```
D_DEBUG("Resolving %"PRIu32" SID(s).\n", state->num_sids);
```

Note:

Do not use PRIu32 for uid_t and gid_t, they do not have to be uint32_t.
