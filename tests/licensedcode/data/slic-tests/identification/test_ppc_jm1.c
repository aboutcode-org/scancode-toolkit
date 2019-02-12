
/* HOW TO COMPILE FOR SWITCHBACK:

   gcc -O -c test_ppc_jm1.c -mregnames -Wall

*/

#undef  HAS_ALTIVEC
#define NO_FLOAT
#undef  IS_PPC405


/*
 * test-ppc.c:
 * PPC tests for qemu-PPC CPU emulation checks
 * 
 * Copyright (c) 2005 Jocelyn Mayer
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License V2
 * as published by the Free Software Foundation.
 */

/*
 * Theory of operations:
 * a few registers are reserved for the test program:
 * r14 => r18
 * f14 => f18
 * I do preload test values in r14 thru r17 (or less, depending on the number
 * of register operands needed), patch the test opcode if any immediate
 * operands are required, execute the tested opcode.
 * XER, CCR and FPSCR are cleared before every test.
 * I always get the result in r17 and also save XER and CCR for fixed-point
 * operations. I also check FPSCR for floating points operations.
 *
 * Improvments:
 * a more cleaver FPSCR management is needed: for now, I always test
 * the round-to-zero case. Other rounding modes also need to be tested.
 */

#include <stdint.h>
//#include <stdlib.h>
//#include <stdio.h>
//#include <string.h>
//#include <unistd.h>
//#include <fcntl.h>
//#include <ctype.h>
//#include <math.h>
//#include <fenv.h>

#define NULL ((void*)0)

//#include "test-ppc.h"

// BEGIN #include "test-ppc.h"
/*
 * test-ppc.h:
 * PPC tests for qemu-PPC CPU emulation checks - definitions
 * 
 * Copyright (c) 2005 Jocelyn Mayer
 * 
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License V2
 * as published by the Free Software Foundation.
 */

#if !defined (__TEST_PPC_H__)
#define __TEST_PPC_H__

typedef void (*test_func_t) (void);
typedef struct test_t test_t;
typedef struct test_table_t test_table_t;
struct test_t {
    test_func_t func;
    const unsigned char *name;
};

struct test_table_t {
    test_t *tests;
    const unsigned char *name;
    int flags;
};

typedef void (*test_loop_t) (const unsigned char *name, test_func_t func);

enum test_flags {
    /* Nb arguments */
    PPC_ONE_ARG    = 0x00000001,
    PPC_TWO_ARGS   = 0x00000002,
    PPC_THREE_ARGS = 0x00000003,
    PPC_CMP_ARGS   = 0x00000004,
    PPC_CMPI_ARGS  = 0x00000005,
    PPC_TWO_I16    = 0x00000006,
    PPC_SPECIAL    = 0x00000007,
    PPC_NB_ARGS    = 0x0000000F,
    /* Type */
    PPC_ARITH      = 0x00000100,
    PPC_LOGICAL    = 0x00000200,
    PPC_COMPARE    = 0x00000300,
    PPC_CROP       = 0x00000400,
    PPC_TYPE       = 0x00000F00,
    /* Family */
    PPC_INTEGER    = 0x00010000,
    PPC_FLOAT      = 0x00020000,
    PPC_405        = 0x00030000,
    PPC_ALTIVEC    = 0x00040000,
    PPC_FALTIVEC   = 0x00050000,
    PPC_FAMILY     = 0x000F0000,
    /* Flags */
    PPC_CR         = 0x01000000,
};

#endif /* !defined (__TEST_PPC_H__) */

// END #include "test-ppc.h"




//#define DEBUG_ARGS_BUILD
#if defined (DEBUG_ARGS_BUILD)
#define AB_DPRINTF(fmt, args...) do { vexxx_printf(fmt , ##args); } while (0)
#else
#define AB_DPRINTF(fmt, args...) do { } while (0)
#endif

//#define DEBUG_FILTER
#if defined (DEBUG_FILTER)
#define FDPRINTF(fmt, args...) do { vexxx_printf(fmt , ##args); } while (0)
#else
#define FDPRINTF(fmt, args...) do { } while (0)
#endif

#if !defined (NO_FLOAT)
register double f14 __asm__ ("f14");
register double f15 __asm__ ("f15");
register double f16 __asm__ ("f16");
register double f17 __asm__ ("f17");
register double f18 __asm__ ("f18");
#endif
register uint32_t r14 __asm__ ("r14");
register uint32_t r15 __asm__ ("r15");
register uint32_t r16 __asm__ ("r16");
register uint32_t r17 __asm__ ("r17");
register uint32_t r18 __asm__ ("r18");


/////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////

/* Something which has the same size as void* on the host.  That is,
   it is 32 bits on a 32-bit host and 64 bits on a 64-bit host, and so
   it can safely be coerced to and from a pointer type on the host
   machine. */
typedef  unsigned long HWord;
typedef  char          HChar;
typedef  signed int    Int;
typedef  unsigned int  UInt;
typedef  unsigned char UChar;

typedef    signed long long int   Long;
typedef  unsigned long long int   ULong;

typedef unsigned char   Bool;
#define True  ((Bool)1)
#define False ((Bool)0)


//#include "/home/sewardj/VEX/trunk/pub/libvex_basictypes.h"

static HWord (*serviceFn)(HWord,HWord) = 0;

static Bool my_isspace ( UChar c )
{
   return c == ' ' 
          || c == '\f'
          || c == '\n'
          || c == '\r'
          || c == '\t'
          || c == '\v';
}

#if 0 // unused
static char* my_strcpy ( char* dest, const char* src )
{
   char* dest_orig = dest;
   while (*src) *dest++ = *src++;
   *dest = 0;
   return dest_orig;
}

static void* my_memcpy ( void *dest, const void *src, int sz )
{
   const char *s = (const char *)src;
   char *d = (char *)dest;

   while (sz--)
      *d++ = *s++;

   return dest;
}

static void* my_memmove( void *dst, const void *src, unsigned int len )
{
    register char *d;
    register char *s;
    if ( dst > src ) {
        d = (char *)dst + len - 1;
        s = (char *)src + len - 1;
        while ( len >= 4 ) {
            *d-- = *s--;
            *d-- = *s--;
            *d-- = *s--;
            *d-- = *s--;
            len -= 4;
        }
        while ( len-- ) {
            *d-- = *s--;
        }
    } else if ( dst < src ) {
        d = (char *)dst;
        s = (char *)src;
        while ( len >= 4 ) {
            *d++ = *s++;
            *d++ = *s++;
            *d++ = *s++;
            *d++ = *s++;
            len -= 4;
        }
        while ( len-- ) {
            *d++ = *s++;
        }
    }
    return dst;
}
#endif

char* my_strcat ( char* dest, const char* src )
{
   char* dest_orig = dest;
   while (*dest) dest++;
   while (*src) *dest++ = *src++;
   *dest = 0;
   return dest_orig;
}

int my_strcmp ( const char* s1, const char* s2 )
{
   register unsigned char c1;
   register unsigned char c2;
   while (True) {
      c1 = *(unsigned char *)s1;
      c2 = *(unsigned char *)s2;
      if (c1 != c2) break;
      if (c1 == 0) break;
      s1++; s2++;
   }
   if ((unsigned char)c1 < (unsigned char)c2) return -1;
   if ((unsigned char)c1 > (unsigned char)c2) return 1;
   return 0;
}


int my_memcmp ( const void *s1V, const void *s2V, int n )
{
   int res;
   unsigned char a0;
   unsigned char b0;
   unsigned char* s1 = (unsigned char*)s1V;
   unsigned char* s2 = (unsigned char*)s2V;

   while (n != 0) {
      a0 = s1[0];
      b0 = s2[0];
      s1 += 1;
      s2 += 1;
      res = ((int)a0) - ((int)b0);
      if (res != 0)
         return res;
      n -= 1;
   }
   return 0;
}

char* my_strchr ( const char* s, int c )
{
   UChar  ch = (UChar)((UInt)c);
   UChar* p  = (UChar*)s;
   while (True) {
      if (*p == ch) return p;
      if (*p == 0) return NULL;
      p++;
   }
}

void* my_malloc ( int n )
{
  void* r = (void*) (*serviceFn)(2,n);
  return r;
}


/////////////////////////////////////////////////////////////////////

static void vexxx_log_bytes ( char* p, int n )
{
   int i;
   for (i = 0; i < n; i++)
      (*serviceFn)( 1, (int)p[i] );
}

/*---------------------------------------------------------*/
/*--- vexxx_printf                                        ---*/
/*---------------------------------------------------------*/

/* This should be the only <...> include in the entire VEX library.
   New code for vex_util.c should go above this point. */
#include <stdarg.h>

static HChar vexxx_toupper ( HChar c )
{
   if (c >= 'a' && c <= 'z')
      return c + ('A' - 'a');
   else
      return c;
}

static Int vexxx_strlen ( const HChar* str )
{
   Int i = 0;
   while (str[i] != 0) i++;
   return i;
}

Bool vexxx_streq ( const HChar* s1, const HChar* s2 )
{
   while (True) {
      if (*s1 == 0 && *s2 == 0)
         return True;
      if (*s1 != *s2)
         return False;
      s1++;
      s2++;
   }
}

/* Some flags.  */
#define VG_MSG_SIGNED    1 /* The value is signed. */
#define VG_MSG_ZJUSTIFY  2 /* Must justify with '0'. */
#define VG_MSG_LJUSTIFY  4 /* Must justify on the left. */
#define VG_MSG_PAREN     8 /* Parenthesize if present (for %y) */
#define VG_MSG_COMMA    16 /* Add commas to numbers (for %d, %u) */

/* Copy a string into the buffer. */
static UInt
myvprintf_str ( void(*send)(HChar), Int flags, Int width, HChar* str, 
                Bool capitalise )
{
#  define MAYBE_TOUPPER(ch) (capitalise ? vexxx_toupper(ch) : (ch))
   UInt ret = 0;
   Int i, extra;
   Int len = vexxx_strlen(str);

   if (width == 0) {
      ret += len;
      for (i = 0; i < len; i++)
         send(MAYBE_TOUPPER(str[i]));
      return ret;
   }

   if (len > width) {
      ret += width;
      for (i = 0; i < width; i++)
         send(MAYBE_TOUPPER(str[i]));
      return ret;
   }

   extra = width - len;
   if (flags & VG_MSG_LJUSTIFY) {
      ret += extra;
      for (i = 0; i < extra; i++)
         send(' ');
   }
   ret += len;
   for (i = 0; i < len; i++)
      send(MAYBE_TOUPPER(str[i]));
   if (!(flags & VG_MSG_LJUSTIFY)) {
      ret += extra;
      for (i = 0; i < extra; i++)
         send(' ');
   }

#  undef MAYBE_TOUPPER

   return ret;
}

/* Write P into the buffer according to these args:
 *  If SIGN is true, p is a signed.
 *  BASE is the base.
 *  If WITH_ZERO is true, '0' must be added.
 *  WIDTH is the width of the field.
 */
static UInt
myvprintf_int64 ( void(*send)(HChar), Int flags, Int base, Int width, ULong pL)
{
   HChar buf[40];
   Int   ind = 0;
   Int   i, nc = 0;
   Bool  neg = False;
   HChar *digits = "0123456789ABCDEF";
   UInt  ret = 0;
   UInt  p = (UInt)pL;

   if (base < 2 || base > 16)
      return ret;
 
   if ((flags & VG_MSG_SIGNED) && (Int)p < 0) {
      p   = - (Int)p;
      neg = True;
   }

   if (p == 0)
      buf[ind++] = '0';
   else {
      while (p > 0) {
         if ((flags & VG_MSG_COMMA) && 10 == base &&
             0 == (ind-nc) % 3 && 0 != ind) 
         {
            buf[ind++] = ',';
            nc++;
         }
         buf[ind++] = digits[p % base];
         p /= base;
      }
   }

   if (neg)
      buf[ind++] = '-';

   if (width > 0 && !(flags & VG_MSG_LJUSTIFY)) {
      for(; ind < width; ind++) {
	//vassert(ind < 39);
         buf[ind] = ((flags & VG_MSG_ZJUSTIFY) ? '0': ' ');
      }
   }

   /* Reverse copy to buffer.  */
   ret += ind;
   for (i = ind -1; i >= 0; i--) {
      send(buf[i]);
   }
   if (width > 0 && (flags & VG_MSG_LJUSTIFY)) {
      for(; ind < width; ind++) {
	 ret++;
         send(' ');  // Never pad with zeroes on RHS -- changes the value!
      }
   }
   return ret;
}


/* A simple vprintf().  */
static 
UInt vprintf_wrk ( void(*send)(HChar), const HChar *format, va_list vargs )
{
   UInt ret = 0;
   int i;
   int flags;
   int width;
   Bool is_long;

   /* We assume that vargs has already been initialised by the 
      caller, using va_start, and that the caller will similarly
      clean up with va_end.
   */

   for (i = 0; format[i] != 0; i++) {
      if (format[i] != '%') {
         send(format[i]);
	 ret++;
         continue;
      }
      i++;
      /* A '%' has been found.  Ignore a trailing %. */
      if (format[i] == 0)
         break;
      if (format[i] == '%') {
         /* `%%' is replaced by `%'. */
         send('%');
	 ret++;
         continue;
      }
      flags = 0;
      is_long = False;
      width = 0; /* length of the field. */
      if (format[i] == '(') {
	 flags |= VG_MSG_PAREN;
	 i++;
      }
      /* If ',' follows '%', commas will be inserted. */
      if (format[i] == ',') {
         flags |= VG_MSG_COMMA;
         i++;
      }
      /* If '-' follows '%', justify on the left. */
      if (format[i] == '-') {
         flags |= VG_MSG_LJUSTIFY;
         i++;
      }
      /* If '0' follows '%', pads will be inserted. */
      if (format[i] == '0') {
         flags |= VG_MSG_ZJUSTIFY;
         i++;
      }
      /* Compute the field length. */
      while (format[i] >= '0' && format[i] <= '9') {
         width *= 10;
         width += format[i++] - '0';
      }
      while (format[i] == 'l') {
         i++;
         is_long = True;
      }

      switch (format[i]) {
         case 'd': /* %d */
            flags |= VG_MSG_SIGNED;
            if (is_long)
               ret += myvprintf_int64(send, flags, 10, width, 
				      (ULong)(va_arg (vargs, Long)));
            else
               ret += myvprintf_int64(send, flags, 10, width, 
				      (ULong)(va_arg (vargs, Int)));
            break;
         case 'u': /* %u */
            if (is_long)
               ret += myvprintf_int64(send, flags, 10, width, 
				      (ULong)(va_arg (vargs, ULong)));
            else
               ret += myvprintf_int64(send, flags, 10, width, 
				      (ULong)(va_arg (vargs, UInt)));
            break;
         case 'p': /* %p */
	    ret += 2;
            send('0');
            send('x');
            ret += myvprintf_int64(send, flags, 16, width, 
				   (ULong)((HWord)va_arg (vargs, void *)));
            break;
         case 'x': /* %x */
            if (is_long)
               ret += myvprintf_int64(send, flags, 16, width, 
				      (ULong)(va_arg (vargs, ULong)));
            else
               ret += myvprintf_int64(send, flags, 16, width, 
				      (ULong)(va_arg (vargs, UInt)));
            break;
         case 'c': /* %c */
	    ret++;
            send((va_arg (vargs, int)));
            break;
         case 's': case 'S': { /* %s */
            char *str = va_arg (vargs, char *);
            if (str == (char*) 0) str = "(null)";
            ret += myvprintf_str(send, flags, width, str, 
                                 (format[i]=='S'));
            break;
	 }
#        if 0
	 case 'y': { /* %y - print symbol */
	    Char buf[100];
	    Char *cp = buf;
	    Addr a = va_arg(vargs, Addr);

	    if (flags & VG_MSG_PAREN)
	       *cp++ = '(';
	    if (VG_(get_fnname_w_offset)(a, cp, sizeof(buf)-4)) {
	       if (flags & VG_MSG_PAREN) {
		  cp += VG_(strlen)(cp);
		  *cp++ = ')';
		  *cp = '\0';
	       }
	       ret += myvprintf_str(send, flags, width, buf, 0);
	    }
	    break;
	 }
#        endif
         default:
            break;
      }
   }
   return ret;
}


/* A general replacement for printf().  Note that only low-level 
   debugging info should be sent via here.  The official route is to
   to use vg_message().  This interface is deprecated.
*/
static HChar myprintf_buf[1000];
static Int   n_myprintf_buf;

static void add_to_myprintf_buf ( HChar c )
{
   if (c == '\n' || n_myprintf_buf >= 1000-10 /*paranoia*/ ) {
      (*vexxx_log_bytes)( myprintf_buf, vexxx_strlen(myprintf_buf) );
      n_myprintf_buf = 0;
      myprintf_buf[n_myprintf_buf] = 0;      
   }
   myprintf_buf[n_myprintf_buf++] = c;
   myprintf_buf[n_myprintf_buf] = 0;
}

static UInt vexxx_printf ( const char *format, ... )
{
   UInt ret;
   va_list vargs;
   va_start(vargs,format);
   
   n_myprintf_buf = 0;
   myprintf_buf[n_myprintf_buf] = 0;      
   ret = vprintf_wrk ( add_to_myprintf_buf, format, vargs );

   if (n_myprintf_buf > 0) {
      (*vexxx_log_bytes)( myprintf_buf, n_myprintf_buf );
   }

   va_end(vargs);

   return ret;
}

/*---------------------------------------------------------------*/
/*--- end                                          vex_util.c ---*/
/*---------------------------------------------------------------*/


/////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////

// BEGIN #include "ops-ppc.c"
/*
 * WARNING:
 * This file has been auto-generated by './gen-ppc' program
 * Please don't edit by hand
 */


//BEGIN #include "test-ppc.h"
/*
 * test-ppc.h:
 * PPC tests for qemu-PPC CPU emulation checks - definitions
 * 
 * Copyright (c) 2005 Jocelyn Mayer
 * 
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License V2
 * as published by the Free Software Foundation.
 */

#if !defined (__TEST_PPC_H__)
#define __TEST_PPC_H__

typedef void (*test_func_t) (void);
typedef struct test_t test_t;
typedef struct test_table_t test_table_t;
struct test_t {
    test_func_t func;
    const unsigned char *name;
};

struct test_table_t {
    test_t *tests;
    const unsigned char *name;
    int flags;
};

typedef void (*test_loop_t) (const unsigned char *name, test_func_t func);

enum test_flags {
    /* Nb arguments */
    PPC_ONE_ARG    = 0x00000001,
    PPC_TWO_ARGS   = 0x00000002,
    PPC_THREE_ARGS = 0x00000003,
    PPC_CMP_ARGS   = 0x00000004,
    PPC_CMPI_ARGS  = 0x00000005,
    PPC_TWO_I16    = 0x00000006,
    PPC_SPECIAL    = 0x00000007,
    PPC_NB_ARGS    = 0x0000000F,
    /* Type */
    PPC_ARITH      = 0x00000100,
    PPC_LOGICAL    = 0x00000200,
    PPC_COMPARE    = 0x00000300,
    PPC_CROP       = 0x00000400,
    PPC_TYPE       = 0x00000F00,
    /* Family */
    PPC_INTEGER    = 0x00010000,
    PPC_FLOAT      = 0x00020000,
    PPC_405        = 0x00030000,
    PPC_ALTIVEC    = 0x00040000,
    PPC_FALTIVEC   = 0x00050000,
    PPC_FAMILY     = 0x000F0000,
    /* Flags */
    PPC_CR         = 0x01000000,
};

#endif /* !defined (__TEST_PPC_H__) */

//END #include "test-ppc.h"

static void test_add (void)
{
    __asm__ __volatile__ ("add          17, 14, 15");
}

static void test_addo (void)
{
    __asm__ __volatile__ ("addo         17, 14, 15");
}

static void test_addc (void)
{
    __asm__ __volatile__ ("addc         17, 14, 15");
}

static void test_addco (void)
{
    __asm__ __volatile__ ("addco        17, 14, 15");
}

static void test_adde (void)
{
    __asm__ __volatile__ ("adde         17, 14, 15");
}

static void test_addeo (void)
{
    __asm__ __volatile__ ("addeo        17, 14, 15");
}

static void test_divw (void)
{
    __asm__ __volatile__ ("divw         17, 14, 15");
}

static void test_divwo (void)
{
    __asm__ __volatile__ ("divwo        17, 14, 15");
}

static void test_divwu (void)
{
    __asm__ __volatile__ ("divwu        17, 14, 15");
}

static void test_divwuo (void)
{
    __asm__ __volatile__ ("divwuo       17, 14, 15");
}

static void test_mulhw (void)
{
    __asm__ __volatile__ ("mulhw        17, 14, 15");
}

static void test_mulhwu (void)
{
    __asm__ __volatile__ ("mulhwu       17, 14, 15");
}

static void test_mullw (void)
{
    __asm__ __volatile__ ("mullw        17, 14, 15");
}

static void test_mullwo (void)
{
    __asm__ __volatile__ ("mullwo       17, 14, 15");
}

static void test_subf (void)
{
    __asm__ __volatile__ ("subf         17, 14, 15");
}

static void test_subfo (void)
{
    __asm__ __volatile__ ("subfo        17, 14, 15");
}

static void test_subfc (void)
{
    __asm__ __volatile__ ("subfc        17, 14, 15");
}

static void test_subfco (void)
{
    __asm__ __volatile__ ("subfco       17, 14, 15");
}

static void test_subfe (void)
{
    __asm__ __volatile__ ("subfe        17, 14, 15");
}

static void test_subfeo (void)
{
    __asm__ __volatile__ ("subfeo       17, 14, 15");
}

static test_t tests_ia_ops_two[] = {
    { &test_add             , "         add", },
    { &test_addo            , "        addo", },
    { &test_addc            , "        addc", },
    { &test_addco           , "       addco", },
    { &test_adde            , "        adde", },
    { &test_addeo           , "       addeo", },
    { &test_divw            , "        divw", },
    { &test_divwo           , "       divwo", },
    { &test_divwu           , "       divwu", },
    { &test_divwuo          , "      divwuo", },
    { &test_mulhw           , "       mulhw", },
    { &test_mulhwu          , "      mulhwu", },
    { &test_mullw           , "       mullw", },
    { &test_mullwo          , "      mullwo", },
    { &test_subf            , "        subf", },
    { &test_subfo           , "       subfo", },
    { &test_subfc           , "       subfc", },
    { &test_subfco          , "      subfco", },
    { &test_subfe           , "       subfe", },
    { &test_subfeo          , "      subfeo", },
    { NULL,                   NULL,           },
};

static void test_add_ (void)
{
    __asm__ __volatile__ ("add.         17, 14, 15");
}

static void test_addo_ (void)
{
    __asm__ __volatile__ ("addo.        17, 14, 15");
}

static void test_addc_ (void)
{
    __asm__ __volatile__ ("addc.        17, 14, 15");
}

static void test_addco_ (void)
{
    __asm__ __volatile__ ("addco.       17, 14, 15");
}

static void test_adde_ (void)
{
    __asm__ __volatile__ ("adde.        17, 14, 15");
}

static void test_addeo_ (void)
{
    __asm__ __volatile__ ("addeo.       17, 14, 15");
}

static void test_divw_ (void)
{
    __asm__ __volatile__ ("divw.        17, 14, 15");
}

static void test_divwo_ (void)
{
    __asm__ __volatile__ ("divwo.       17, 14, 15");
}

static void test_divwu_ (void)
{
    __asm__ __volatile__ ("divwu.       17, 14, 15");
}

static void test_divwuo_ (void)
{
    __asm__ __volatile__ ("divwuo.      17, 14, 15");
}

static void test_subf_ (void)
{
    __asm__ __volatile__ ("subf.        17, 14, 15");
}

static void test_subfo_ (void)
{
    __asm__ __volatile__ ("subfo.       17, 14, 15");
}

static void test_subfc_ (void)
{
    __asm__ __volatile__ ("subfc.       17, 14, 15");
}

static void test_subfco_ (void)
{
    __asm__ __volatile__ ("subfco.      17, 14, 15");
}

static void test_subfe_ (void)
{
    __asm__ __volatile__ ("subfe.       17, 14, 15");
}

static void test_subfeo_ (void)
{
    __asm__ __volatile__ ("subfeo.      17, 14, 15");
}

static test_t tests_iar_ops_two[] = {
    { &test_add_            , "        add.", },
    { &test_addo_           , "       addo.", },
    { &test_addc_           , "       addc.", },
    { &test_addco_          , "      addco.", },
    { &test_adde_           , "       adde.", },
    { &test_addeo_          , "      addeo.", },
    { &test_divw_           , "       divw.", },
    { &test_divwo_          , "      divwo.", },
    { &test_divwu_          , "      divwu.", },
    { &test_divwuo_         , "     divwuo.", },
    { &test_subf_           , "       subf.", },
    { &test_subfo_          , "      subfo.", },
    { &test_subfc_          , "      subfc.", },
    { &test_subfco_         , "     subfco.", },
    { &test_subfe_          , "      subfe.", },
    { &test_subfeo_         , "     subfeo.", },
    { NULL,                   NULL,           },
};

static void test_and (void)
{
    __asm__ __volatile__ ("and          17, 14, 15");
}

static void test_andc (void)
{
    __asm__ __volatile__ ("andc         17, 14, 15");
}

static void test_eqv (void)
{
    __asm__ __volatile__ ("eqv          17, 14, 15");
}

static void test_nand (void)
{
    __asm__ __volatile__ ("nand         17, 14, 15");
}

static void test_nor (void)
{
    __asm__ __volatile__ ("nor          17, 14, 15");
}

static void test_or (void)
{
    __asm__ __volatile__ ("or           17, 14, 15");
}

static void test_orc (void)
{
    __asm__ __volatile__ ("orc          17, 14, 15");
}

static void test_xor (void)
{
    __asm__ __volatile__ ("xor          17, 14, 15");
}

static void test_slw (void)
{
    __asm__ __volatile__ ("slw          17, 14, 15");
}

static void test_sraw (void)
{
    __asm__ __volatile__ ("sraw         17, 14, 15");
}

static void test_srw (void)
{
    __asm__ __volatile__ ("srw          17, 14, 15");
}

static test_t tests_il_ops_two[] = {
    { &test_and             , "         and", },
    { &test_andc            , "        andc", },
    { &test_eqv             , "         eqv", },
    { &test_nand            , "        nand", },
    { &test_nor             , "         nor", },
    { &test_or              , "          or", },
    { &test_orc             , "         orc", },
    { &test_xor             , "         xor", },
    { &test_slw             , "         slw", },
    { &test_sraw            , "        sraw", },
    { &test_srw             , "         srw", },
    { NULL,                   NULL,           },
};

static void test_and_ (void)
{
    __asm__ __volatile__ ("and.         17, 14, 15");
}

static void test_andc_ (void)
{
    __asm__ __volatile__ ("andc.        17, 14, 15");
}

static void test_eqv_ (void)
{
    __asm__ __volatile__ ("eqv.         17, 14, 15");
}

static void test_mulhw_ (void)
{
    __asm__ __volatile__ ("mulhw.       17, 14, 15");
}

static void test_mulhwu_ (void)
{
    __asm__ __volatile__ ("mulhwu.      17, 14, 15");
}

static void test_mullw_ (void)
{
    __asm__ __volatile__ ("mullw.       17, 14, 15");
}

static void test_mullwo_ (void)
{
    __asm__ __volatile__ ("mullwo.      17, 14, 15");
}

static void test_nand_ (void)
{
    __asm__ __volatile__ ("nand.        17, 14, 15");
}

static void test_nor_ (void)
{
    __asm__ __volatile__ ("nor.         17, 14, 15");
}

static void test_or_ (void)
{
    __asm__ __volatile__ ("or.          17, 14, 15");
}

static void test_orc_ (void)
{
    __asm__ __volatile__ ("orc.         17, 14, 15");
}

static void test_xor_ (void)
{
    __asm__ __volatile__ ("xor.         17, 14, 15");
}

static void test_slw_ (void)
{
    __asm__ __volatile__ ("slw.         17, 14, 15");
}

static void test_sraw_ (void)
{
    __asm__ __volatile__ ("sraw.        17, 14, 15");
}

static void test_srw_ (void)
{
    __asm__ __volatile__ ("srw.         17, 14, 15");
}

static test_t tests_ilr_ops_two[] = {
    { &test_and_            , "        and.", },
    { &test_andc_           , "       andc.", },
    { &test_eqv_            , "        eqv.", },
    { &test_mulhw_          , "      mulhw.", },
    { &test_mulhwu_         , "     mulhwu.", },
    { &test_mullw_          , "      mullw.", },
    { &test_mullwo_         , "     mullwo.", },
    { &test_nand_           , "       nand.", },
    { &test_nor_            , "        nor.", },
    { &test_or_             , "         or.", },
    { &test_orc_            , "        orc.", },
    { &test_xor_            , "        xor.", },
    { &test_slw_            , "        slw.", },
    { &test_sraw_           , "       sraw.", },
    { &test_srw_            , "        srw.", },
    { NULL,                   NULL,           },
};

static void test_cmp (void)
{
    __asm__ __volatile__ ("cmp          2, 14, 15");
}

static void test_cmpl (void)
{
    __asm__ __volatile__ ("cmpl         2, 14, 15");
}

static test_t tests_icr_ops_two[] = {
    { &test_cmp             , "         cmp", },
    { &test_cmpl            , "        cmpl", },
    { NULL,                   NULL,           },
};

static void test_cmpi (void)
{
    __asm__ __volatile__ ("cmpi         2, 14, 15");
}

static void test_cmpli (void)
{
    __asm__ __volatile__ ("cmpli        2, 14, 15");
}

static test_t tests_icr_ops_two_i16[] = {
    { &test_cmpi            , "        cmpi", },
    { &test_cmpli           , "       cmpli", },
    { NULL,                   NULL,           },
};

static void test_addi (void)
{
    __asm__ __volatile__ ("addi         17, 14, 0");
}

static void test_addic (void)
{
    __asm__ __volatile__ ("addic        17, 14, 0");
}

static void test_addis (void)
{
    __asm__ __volatile__ ("addis        17, 14, 0");
}

static void test_mulli (void)
{
    __asm__ __volatile__ ("mulli        17, 14, 0");
}

static void test_subfic (void)
{
    __asm__ __volatile__ ("subfic       17, 14, 0");
}

static test_t tests_ia_ops_two_i16[] = {
    { &test_addi            , "        addi", },
    { &test_addic           , "       addic", },
    { &test_addis           , "       addis", },
    { &test_mulli           , "       mulli", },
    { &test_subfic          , "      subfic", },
    { NULL,                   NULL,           },
};

static void test_addic_ (void)
{
    __asm__ __volatile__ ("addic.       17, 14, 0");
}

static test_t tests_iar_ops_two_i16[] = {
    { &test_addic_          , "      addic.", },
    { NULL,                   NULL,           },
};

static void test_ori (void)
{
    __asm__ __volatile__ ("ori          17, 14, 0");
}

static void test_oris (void)
{
    __asm__ __volatile__ ("oris         17, 14, 0");
}

static void test_xori (void)
{
    __asm__ __volatile__ ("xori         17, 14, 0");
}

static void test_xoris (void)
{
    __asm__ __volatile__ ("xoris        17, 14, 0");
}

static test_t tests_il_ops_two_i16[] = {
    { &test_ori             , "         ori", },
    { &test_oris            , "        oris", },
    { &test_xori            , "        xori", },
    { &test_xoris           , "       xoris", },
    { NULL,                   NULL,           },
};

static void test_andi_ (void)
{
    __asm__ __volatile__ ("andi.        17, 14, 0");
}

static void test_andis_ (void)
{
    __asm__ __volatile__ ("andis.       17, 14, 0");
}

static test_t tests_ilr_ops_two_i16[] = {
    { &test_andi_           , "       andi.", },
    { &test_andis_          , "      andis.", },
    { NULL,                   NULL,           },
};

static void test_crand (void)
{
    __asm__ __volatile__ ("crand        17, 14, 15");
}

static void test_crandc (void)
{
    __asm__ __volatile__ ("crandc       17, 14, 15");
}

static void test_creqv (void)
{
    __asm__ __volatile__ ("creqv        17, 14, 15");
}

static void test_crnand (void)
{
    __asm__ __volatile__ ("crnand       17, 14, 15");
}

static void test_crnor (void)
{
    __asm__ __volatile__ ("crnor        17, 14, 15");
}

static void test_cror (void)
{
    __asm__ __volatile__ ("cror         17, 14, 15");
}

static void test_crorc (void)
{
    __asm__ __volatile__ ("crorc        17, 14, 15");
}

static void test_crxor (void)
{
    __asm__ __volatile__ ("crxor        17, 14, 15");
}

static test_t tests_crl_ops_two[] = {
    { &test_crand           , "       crand", },
    { &test_crandc          , "      crandc", },
    { &test_creqv           , "       creqv", },
    { &test_crnand          , "      crnand", },
    { &test_crnor           , "       crnor", },
    { &test_cror            , "        cror", },
    { &test_crorc           , "       crorc", },
    { &test_crxor           , "       crxor", },
    { NULL,                   NULL,           },
};

static void test_addme (void)
{
    __asm__ __volatile__ ("addme        17, 14");
}

static void test_addmeo (void)
{
    __asm__ __volatile__ ("addmeo       17, 14");
}

static void test_addze (void)
{
    __asm__ __volatile__ ("addze        17, 14");
}

static void test_addzeo (void)
{
    __asm__ __volatile__ ("addzeo       17, 14");
}

static void test_subfme (void)
{
    __asm__ __volatile__ ("subfme       17, 14");
}

static void test_subfmeo (void)
{
    __asm__ __volatile__ ("subfmeo      17, 14");
}

static void test_subfze (void)
{
    __asm__ __volatile__ ("subfze       17, 14");
}

static void test_subfzeo (void)
{
    __asm__ __volatile__ ("subfzeo      17, 14");
}

static test_t tests_ia_ops_one[] = {
    { &test_addme           , "       addme", },
    { &test_addmeo          , "      addmeo", },
    { &test_addze           , "       addze", },
    { &test_addzeo          , "      addzeo", },
    { &test_subfme          , "      subfme", },
    { &test_subfmeo         , "     subfmeo", },
    { &test_subfze          , "      subfze", },
    { &test_subfzeo         , "     subfzeo", },
    { NULL,                   NULL,           },
};

static void test_addme_ (void)
{
    __asm__ __volatile__ ("addme.       17, 14");
}

static void test_addmeo_ (void)
{
    __asm__ __volatile__ ("addmeo.      17, 14");
}

static void test_addze_ (void)
{
    __asm__ __volatile__ ("addze.       17, 14");
}

static void test_addzeo_ (void)
{
    __asm__ __volatile__ ("addzeo.      17, 14");
}

static void test_subfme_ (void)
{
    __asm__ __volatile__ ("subfme.      17, 14");
}

static void test_subfmeo_ (void)
{
    __asm__ __volatile__ ("subfmeo.     17, 14");
}

static void test_subfze_ (void)
{
    __asm__ __volatile__ ("subfze.      17, 14");
}

static void test_subfzeo_ (void)
{
    __asm__ __volatile__ ("subfzeo.     17, 14");
}

static test_t tests_iar_ops_one[] = {
    { &test_addme_          , "      addme.", },
    { &test_addmeo_         , "     addmeo.", },
    { &test_addze_          , "      addze.", },
    { &test_addzeo_         , "     addzeo.", },
    { &test_subfme_         , "     subfme.", },
    { &test_subfmeo_        , "    subfmeo.", },
    { &test_subfze_         , "     subfze.", },
    { &test_subfzeo_        , "    subfzeo.", },
    { NULL,                   NULL,           },
};

static void test_cntlzw (void)
{
    __asm__ __volatile__ ("cntlzw       17, 14");
}

static void test_extsb (void)
{
    __asm__ __volatile__ ("extsb        17, 14");
}

static void test_extsh (void)
{
    __asm__ __volatile__ ("extsh        17, 14");
}

static void test_neg (void)
{
    __asm__ __volatile__ ("neg          17, 14");
}

static void test_nego (void)
{
    __asm__ __volatile__ ("nego         17, 14");
}

static test_t tests_il_ops_one[] = {
    { &test_cntlzw          , "      cntlzw", },
    { &test_extsb           , "       extsb", },
    { &test_extsh           , "       extsh", },
    { &test_neg             , "         neg", },
    { &test_nego            , "        nego", },
    { NULL,                   NULL,           },
};

static void test_cntlzw_ (void)
{
    __asm__ __volatile__ ("cntlzw.      17, 14");
}

static void test_extsb_ (void)
{
    __asm__ __volatile__ ("extsb.       17, 14");
}

static void test_extsh_ (void)
{
    __asm__ __volatile__ ("extsh.       17, 14");
}

static void test_neg_ (void)
{
    __asm__ __volatile__ ("neg.         17, 14");
}

static void test_nego_ (void)
{
    __asm__ __volatile__ ("nego.        17, 14");
}

static test_t tests_ilr_ops_one[] = {
    { &test_cntlzw_         , "     cntlzw.", },
    { &test_extsb_          , "      extsb.", },
    { &test_extsh_          , "      extsh.", },
    { &test_neg_            , "        neg.", },
    { &test_nego_           , "       nego.", },
    { NULL,                   NULL,           },
};

static void test_rlwimi (void)
{
    __asm__ __volatile__ ("rlwimi       17, 14, 0, 0, 0");
}

static void test_rlwinm (void)
{
    __asm__ __volatile__ ("rlwinm       17, 14, 0, 0, 0");
}

static void test_rlwnm (void)
{
    __asm__ __volatile__ ("rlwnm        17, 14, 15, 0, 0");
}

static void test_srawi (void)
{
    __asm__ __volatile__ ("srawi        17, 14, 0");
}

static test_t tests_il_ops_spe[] = {
    { &test_rlwimi          , "      rlwimi", },
    { &test_rlwinm          , "      rlwinm", },
    { &test_rlwnm           , "       rlwnm", },
    { &test_srawi           , "       srawi", },
    { NULL,                   NULL,           },
};

static void test_rlwimi_ (void)
{
    __asm__ __volatile__ ("rlwimi.      17, 14, 0, 0, 0");
}

static void test_rlwinm_ (void)
{
    __asm__ __volatile__ ("rlwinm.      17, 14, 0, 0, 0");
}

static void test_rlwnm_ (void)
{
    __asm__ __volatile__ ("rlwnm.       17, 14, 15, 0, 0");
}

static void test_srawi_ (void)
{
    __asm__ __volatile__ ("srawi.       17, 14, 0");
}

static test_t tests_ilr_ops_spe[] = {
    { &test_rlwimi_         , "     rlwimi.", },
    { &test_rlwinm_         , "     rlwinm.", },
    { &test_rlwnm_          , "      rlwnm.", },
    { &test_srawi_          , "      srawi.", },
    { NULL,                   NULL,           },
};

#if !defined (NO_FLOAT)
static void test_fsel (void)
{
    __asm__ __volatile__ ("fsel         17, 14, 15, 16");
}

static void test_fmadd (void)
{
    __asm__ __volatile__ ("fmadd        17, 14, 15, 16");
}

static void test_fmadds (void)
{
    __asm__ __volatile__ ("fmadds       17, 14, 15, 16");
}

static void test_fmsub (void)
{
    __asm__ __volatile__ ("fmsub        17, 14, 15, 16");
}

static void test_fmsubs (void)
{
    __asm__ __volatile__ ("fmsubs       17, 14, 15, 16");
}

static void test_fnmadd (void)
{
    __asm__ __volatile__ ("fnmadd       17, 14, 15, 16");
}

static void test_fnmadds (void)
{
    __asm__ __volatile__ ("fnmadds      17, 14, 15, 16");
}

static void test_fnmsub (void)
{
    __asm__ __volatile__ ("fnmsub       17, 14, 15, 16");
}

static void test_fnmsubs (void)
{
    __asm__ __volatile__ ("fnmsubs      17, 14, 15, 16");
}

static test_t tests_fa_ops_three[] = {
    { &test_fsel            , "        fsel", },
    { &test_fmadd           , "       fmadd", },
    { &test_fmadds          , "      fmadds", },
    { &test_fmsub           , "       fmsub", },
    { &test_fmsubs          , "      fmsubs", },
    { &test_fnmadd          , "      fnmadd", },
    { &test_fnmadds         , "     fnmadds", },
    { &test_fnmsub          , "      fnmsub", },
    { &test_fnmsubs         , "     fnmsubs", },
    { NULL,                   NULL,           },
};
#endif /* !defined (NO_FLOAT) */

#if !defined (NO_FLOAT)
static void test_fsel_ (void)
{
    __asm__ __volatile__ ("fsel.        17, 14, 15, 16");
}

static void test_fmadd_ (void)
{
    __asm__ __volatile__ ("fmadd.       17, 14, 15, 16");
}

static void test_fmadds_ (void)
{
    __asm__ __volatile__ ("fmadds.      17, 14, 15, 16");
}

static void test_fmsub_ (void)
{
    __asm__ __volatile__ ("fmsub.       17, 14, 15, 16");
}

static void test_fmsubs_ (void)
{
    __asm__ __volatile__ ("fmsubs.      17, 14, 15, 16");
}

static void test_fnmadd_ (void)
{
    __asm__ __volatile__ ("fnmadd.      17, 14, 15, 16");
}

static void test_fnmadds_ (void)
{
    __asm__ __volatile__ ("fnmadds.     17, 14, 15, 16");
}

static void test_fnmsub_ (void)
{
    __asm__ __volatile__ ("fnmsub.      17, 14, 15, 16");
}

static void test_fnmsubs_ (void)
{
    __asm__ __volatile__ ("fnmsubs.     17, 14, 15, 16");
}

static test_t tests_far_ops_three[] = {
    { &test_fsel_           , "       fsel.", },
    { &test_fmadd_          , "      fmadd.", },
    { &test_fmadds_         , "     fmadds.", },
    { &test_fmsub_          , "      fmsub.", },
    { &test_fmsubs_         , "     fmsubs.", },
    { &test_fnmadd_         , "     fnmadd.", },
    { &test_fnmadds_        , "    fnmadds.", },
    { &test_fnmsub_         , "     fnmsub.", },
    { &test_fnmsubs_        , "    fnmsubs.", },
    { NULL,                   NULL,           },
};
#endif /* !defined (NO_FLOAT) */

#if !defined (NO_FLOAT)
static void test_fadd (void)
{
    __asm__ __volatile__ ("fadd         17, 14, 15");
}

static void test_fadds (void)
{
    __asm__ __volatile__ ("fadds        17, 14, 15");
}

static void test_fsub (void)
{
    __asm__ __volatile__ ("fsub         17, 14, 15");
}

static void test_fsubs (void)
{
    __asm__ __volatile__ ("fsubs        17, 14, 15");
}

static void test_fmul (void)
{
    __asm__ __volatile__ ("fmul         17, 14, 15");
}

static void test_fmuls (void)
{
    __asm__ __volatile__ ("fmuls        17, 14, 15");
}

static void test_fdiv (void)
{
    __asm__ __volatile__ ("fdiv         17, 14, 15");
}

static void test_fdivs (void)
{
    __asm__ __volatile__ ("fdivs        17, 14, 15");
}

static test_t tests_fa_ops_two[] = {
    { &test_fadd            , "        fadd", },
    { &test_fadds           , "       fadds", },
    { &test_fsub            , "        fsub", },
    { &test_fsubs           , "       fsubs", },
    { &test_fmul            , "        fmul", },
    { &test_fmuls           , "       fmuls", },
    { &test_fdiv            , "        fdiv", },
    { &test_fdivs           , "       fdivs", },
    { NULL,                   NULL,           },
};
#endif /* !defined (NO_FLOAT) */

#if !defined (NO_FLOAT)
static void test_fadd_ (void)
{
    __asm__ __volatile__ ("fadd.        17, 14, 15");
}

static void test_fadds_ (void)
{
    __asm__ __volatile__ ("fadds.       17, 14, 15");
}

static void test_fsub_ (void)
{
    __asm__ __volatile__ ("fsub.        17, 14, 15");
}

static void test_fsubs_ (void)
{
    __asm__ __volatile__ ("fsubs.       17, 14, 15");
}

static void test_fmul_ (void)
{
    __asm__ __volatile__ ("fmul.        17, 14, 15");
}

static void test_fmuls_ (void)
{
    __asm__ __volatile__ ("fmuls.       17, 14, 15");
}

static void test_fdiv_ (void)
{
    __asm__ __volatile__ ("fdiv.        17, 14, 15");
}

static void test_fdivs_ (void)
{
    __asm__ __volatile__ ("fdivs.       17, 14, 15");
}

static test_t tests_far_ops_two[] = {
    { &test_fadd_           , "       fadd.", },
    { &test_fadds_          , "      fadds.", },
    { &test_fsub_           , "       fsub.", },
    { &test_fsubs_          , "      fsubs.", },
    { &test_fmul_           , "       fmul.", },
    { &test_fmuls_          , "      fmuls.", },
    { &test_fdiv_           , "       fdiv.", },
    { &test_fdivs_          , "      fdivs.", },
    { NULL,                   NULL,           },
};
#endif /* !defined (NO_FLOAT) */

#if !defined (NO_FLOAT)
static void test_fcmpo (void)
{
    __asm__ __volatile__ ("fcmpo        2, 14, 15");
}

static void test_fcmpu (void)
{
    __asm__ __volatile__ ("fcmpu        2, 14, 15");
}

static test_t tests_fcr_ops_two[] = {
    { &test_fcmpo           , "       fcmpo", },
    { &test_fcmpu           , "       fcmpu", },
    { NULL,                   NULL,           },
};
#endif /* !defined (NO_FLOAT) */

#if !defined (NO_FLOAT)
static void test_fres (void)
{
    __asm__ __volatile__ ("fres         17, 14");
}

static void test_frsqrte (void)
{
    __asm__ __volatile__ ("frsqrte      17, 14");
}

static void test_frsp (void)
{
    __asm__ __volatile__ ("frsp         17, 14");
}

static void test_fctiw (void)
{
    __asm__ __volatile__ ("fctiw        17, 14");
}

static void test_fctiwz (void)
{
    __asm__ __volatile__ ("fctiwz       17, 14");
}

static void test_fmr (void)
{
    __asm__ __volatile__ ("fmr          17, 14");
}

static void test_fneg (void)
{
    __asm__ __volatile__ ("fneg         17, 14");
}

static void test_fabs (void)
{
    __asm__ __volatile__ ("fabs         17, 14");
}

static void test_fnabs (void)
{
    __asm__ __volatile__ ("fnabs        17, 14");
}

static test_t tests_fa_ops_one[] = {
    { &test_fres            , "        fres", },
    { &test_frsqrte         , "     frsqrte", },
    { &test_frsp            , "        frsp", },
    { &test_fctiw           , "       fctiw", },
    { &test_fctiwz          , "      fctiwz", },
    { &test_fmr             , "         fmr", },
    { &test_fneg            , "        fneg", },
    { &test_fabs            , "        fabs", },
    { &test_fnabs           , "       fnabs", },
    { NULL,                   NULL,           },
};
#endif /* !defined (NO_FLOAT) */

#if !defined (NO_FLOAT)
static void test_fres_ (void)
{
    __asm__ __volatile__ ("fres.        17, 14");
}

static void test_frsqrte_ (void)
{
    __asm__ __volatile__ ("frsqrte.     17, 14");
}

static void test_frsp_ (void)
{
    __asm__ __volatile__ ("frsp.        17, 14");
}

static void test_fctiw_ (void)
{
    __asm__ __volatile__ ("fctiw.       17, 14");
}

static void test_fctiwz_ (void)
{
    __asm__ __volatile__ ("fctiwz.      17, 14");
}

static void test_fmr_ (void)
{
    __asm__ __volatile__ ("fmr.         17, 14");
}

static void test_fneg_ (void)
{
    __asm__ __volatile__ ("fneg.        17, 14");
}

static void test_fabs_ (void)
{
    __asm__ __volatile__ ("fabs.        17, 14");
}

static void test_fnabs_ (void)
{
    __asm__ __volatile__ ("fnabs.       17, 14");
}

static test_t tests_far_ops_one[] = {
    { &test_fres_           , "       fres.", },
    { &test_frsqrte_        , "    frsqrte.", },
    { &test_frsp_           , "       frsp.", },
    { &test_fctiw_          , "      fctiw.", },
    { &test_fctiwz_         , "     fctiwz.", },
    { &test_fmr_            , "        fmr.", },
    { &test_fneg_           , "       fneg.", },
    { &test_fabs_           , "       fabs.", },
    { &test_fnabs_          , "      fnabs.", },
    { NULL,                   NULL,           },
};
#endif /* !defined (NO_FLOAT) */

#if !defined (NO_FLOAT)
static test_t tests_fl_ops_spe[] = {
    { NULL,                   NULL,           },
};
#endif /* !defined (NO_FLOAT) */

#if !defined (NO_FLOAT)
static test_t tests_flr_ops_spe[] = {
    { NULL,                   NULL,           },
};
#endif /* !defined (NO_FLOAT) */

#if defined (HAS_ALTIVEC)
static void test_vmhaddshs (void)
{
    __asm__ __volatile__ ("vmhaddshs    17, 14, 15, 16");
}

static void test_vmhraddshs (void)
{
    __asm__ __volatile__ ("vmhraddshs   17, 14, 15, 16");
}

static void test_vmladduhm (void)
{
    __asm__ __volatile__ ("vmladduhm    17, 14, 15, 16");
}

static void test_vmsumubm (void)
{
    __asm__ __volatile__ ("vmsumubm     17, 14, 15, 16");
}

static void test_vmsumuhm (void)
{
    __asm__ __volatile__ ("vmsumuhm     17, 14, 15, 16");
}

static void test_vmsumshs (void)
{
    __asm__ __volatile__ ("vmsumshs     17, 14, 15, 16");
}

static void test_vmsumuhs (void)
{
    __asm__ __volatile__ ("vmsumuhs     17, 14, 15, 16");
}

static void test_vmsummbm (void)
{
    __asm__ __volatile__ ("vmsummbm     17, 14, 15, 16");
}

static void test_vmsumshm (void)
{
    __asm__ __volatile__ ("vmsumshm     17, 14, 15, 16");
}

static test_t tests_aa_ops_three[] = {
    { &test_vmhaddshs       , "   vmhaddshs", },
    { &test_vmhraddshs      , "  vmhraddshs", },
    { &test_vmladduhm       , "   vmladduhm", },
    { &test_vmsumubm        , "    vmsumubm", },
    { &test_vmsumuhm        , "    vmsumuhm", },
    { &test_vmsumshs        , "    vmsumshs", },
    { &test_vmsumuhs        , "    vmsumuhs", },
    { &test_vmsummbm        , "    vmsummbm", },
    { &test_vmsumshm        , "    vmsumshm", },
    { NULL,                   NULL,           },
};
#endif /* defined (HAS_ALTIVEC) */

#if defined (HAS_ALTIVEC)
static void test_vperm (void)
{
    __asm__ __volatile__ ("vperm        17, 14, 15, 16");
}

static void test_vsel (void)
{
    __asm__ __volatile__ ("vsel         17, 14, 15, 16");
}

static test_t tests_al_ops_three[] = {
    { &test_vperm           , "       vperm", },
    { &test_vsel            , "        vsel", },
    { NULL,                   NULL,           },
};
#endif /* defined (HAS_ALTIVEC) */

#if defined (HAS_ALTIVEC)
static void test_vaddubm (void)
{
    __asm__ __volatile__ ("vaddubm      17, 14, 15");
}

static void test_vadduhm (void)
{
    __asm__ __volatile__ ("vadduhm      17, 14, 15");
}

static void test_vadduwm (void)
{
    __asm__ __volatile__ ("vadduwm      17, 14, 15");
}

static void test_vaddubs (void)
{
    __asm__ __volatile__ ("vaddubs      17, 14, 15");
}

static void test_vadduhs (void)
{
    __asm__ __volatile__ ("vadduhs      17, 14, 15");
}

static void test_vadduws (void)
{
    __asm__ __volatile__ ("vadduws      17, 14, 15");
}

static void test_vaddsbs (void)
{
    __asm__ __volatile__ ("vaddsbs      17, 14, 15");
}

static void test_vaddshs (void)
{
    __asm__ __volatile__ ("vaddshs      17, 14, 15");
}

static void test_vaddsws (void)
{
    __asm__ __volatile__ ("vaddsws      17, 14, 15");
}

static void test_vaddcuw (void)
{
    __asm__ __volatile__ ("vaddcuw      17, 14, 15");
}

static void test_vsububm (void)
{
    __asm__ __volatile__ ("vsububm      17, 14, 15");
}

static void test_vsubuhm (void)
{
    __asm__ __volatile__ ("vsubuhm      17, 14, 15");
}

static void test_vsubuwm (void)
{
    __asm__ __volatile__ ("vsubuwm      17, 14, 15");
}

static void test_vsububs (void)
{
    __asm__ __volatile__ ("vsububs      17, 14, 15");
}

static void test_vsubuhs (void)
{
    __asm__ __volatile__ ("vsubuhs      17, 14, 15");
}

static void test_vsubuws (void)
{
    __asm__ __volatile__ ("vsubuws      17, 14, 15");
}

static void test_vsubcuw (void)
{
    __asm__ __volatile__ ("vsubcuw      17, 14, 15");
}

static void test_vmuloub (void)
{
    __asm__ __volatile__ ("vmuloub      17, 14, 15");
}

static void test_vmulouh (void)
{
    __asm__ __volatile__ ("vmulouh      17, 14, 15");
}

static void test_vmulosb (void)
{
    __asm__ __volatile__ ("vmulosb      17, 14, 15");
}

static void test_vmulosh (void)
{
    __asm__ __volatile__ ("vmulosh      17, 14, 15");
}

static void test_vmuleub (void)
{
    __asm__ __volatile__ ("vmuleub      17, 14, 15");
}

static void test_vmuleuh (void)
{
    __asm__ __volatile__ ("vmuleuh      17, 14, 15");
}

static void test_vmulesb (void)
{
    __asm__ __volatile__ ("vmulesb      17, 14, 15");
}

static void test_vmulesh (void)
{
    __asm__ __volatile__ ("vmulesh      17, 14, 15");
}

static void test_vsumsws (void)
{
    __asm__ __volatile__ ("vsumsws      17, 14, 15");
}

static void test_vsum2sws (void)
{
    __asm__ __volatile__ ("vsum2sws     17, 14, 15");
}

static void test_vsum4ubs (void)
{
    __asm__ __volatile__ ("vsum4ubs     17, 14, 15");
}

static void test_vsum4sbs (void)
{
    __asm__ __volatile__ ("vsum4sbs     17, 14, 15");
}

static void test_vsum4shs (void)
{
    __asm__ __volatile__ ("vsum4shs     17, 14, 15");
}

static void test_vavgub (void)
{
    __asm__ __volatile__ ("vavgub       17, 14, 15");
}

static void test_vavguh (void)
{
    __asm__ __volatile__ ("vavguh       17, 14, 15");
}

static void test_vavguw (void)
{
    __asm__ __volatile__ ("vavguw       17, 14, 15");
}

static void test_vavgsb (void)
{
    __asm__ __volatile__ ("vavgsb       17, 14, 15");
}

static void test_vavgsh (void)
{
    __asm__ __volatile__ ("vavgsh       17, 14, 15");
}

static void test_vavgsw (void)
{
    __asm__ __volatile__ ("vavgsw       17, 14, 15");
}

static void test_vmaxub (void)
{
    __asm__ __volatile__ ("vmaxub       17, 14, 15");
}

static void test_vmaxuh (void)
{
    __asm__ __volatile__ ("vmaxuh       17, 14, 15");
}

static void test_vmaxuw (void)
{
    __asm__ __volatile__ ("vmaxuw       17, 14, 15");
}

static void test_vmaxsb (void)
{
    __asm__ __volatile__ ("vmaxsb       17, 14, 15");
}

static void test_vmaxsh (void)
{
    __asm__ __volatile__ ("vmaxsh       17, 14, 15");
}

static void test_vmaxsw (void)
{
    __asm__ __volatile__ ("vmaxsw       17, 14, 15");
}

static void test_vminub (void)
{
    __asm__ __volatile__ ("vminub       17, 14, 15");
}

static void test_vminuh (void)
{
    __asm__ __volatile__ ("vminuh       17, 14, 15");
}

static void test_vminuw (void)
{
    __asm__ __volatile__ ("vminuw       17, 14, 15");
}

static void test_vminsb (void)
{
    __asm__ __volatile__ ("vminsb       17, 14, 15");
}

static void test_vminsh (void)
{
    __asm__ __volatile__ ("vminsh       17, 14, 15");
}

static void test_vminsw (void)
{
    __asm__ __volatile__ ("vminsw       17, 14, 15");
}

static test_t tests_aa_ops_two[] = {
    { &test_vaddubm         , "     vaddubm", },
    { &test_vadduhm         , "     vadduhm", },
    { &test_vadduwm         , "     vadduwm", },
    { &test_vaddubs         , "     vaddubs", },
    { &test_vadduhs         , "     vadduhs", },
    { &test_vadduws         , "     vadduws", },
    { &test_vaddsbs         , "     vaddsbs", },
    { &test_vaddshs         , "     vaddshs", },
    { &test_vaddsws         , "     vaddsws", },
    { &test_vaddcuw         , "     vaddcuw", },
    { &test_vsububm         , "     vsububm", },
    { &test_vsubuhm         , "     vsubuhm", },
    { &test_vsubuwm         , "     vsubuwm", },
    { &test_vsububs         , "     vsububs", },
    { &test_vsubuhs         , "     vsubuhs", },
    { &test_vsubuws         , "     vsubuws", },
    { &test_vsubcuw         , "     vsubcuw", },
    { &test_vmuloub         , "     vmuloub", },
    { &test_vmulouh         , "     vmulouh", },
    { &test_vmulosb         , "     vmulosb", },
    { &test_vmulosh         , "     vmulosh", },
    { &test_vmuleub         , "     vmuleub", },
    { &test_vmuleuh         , "     vmuleuh", },
    { &test_vmulesb         , "     vmulesb", },
    { &test_vmulesh         , "     vmulesh", },
    { &test_vsumsws         , "     vsumsws", },
    { &test_vsum2sws        , "    vsum2sws", },
    { &test_vsum4ubs        , "    vsum4ubs", },
    { &test_vsum4sbs        , "    vsum4sbs", },
    { &test_vsum4shs        , "    vsum4shs", },
    { &test_vavgub          , "      vavgub", },
    { &test_vavguh          , "      vavguh", },
    { &test_vavguw          , "      vavguw", },
    { &test_vavgsb          , "      vavgsb", },
    { &test_vavgsh          , "      vavgsh", },
    { &test_vavgsw          , "      vavgsw", },
    { &test_vmaxub          , "      vmaxub", },
    { &test_vmaxuh          , "      vmaxuh", },
    { &test_vmaxuw          , "      vmaxuw", },
    { &test_vmaxsb          , "      vmaxsb", },
    { &test_vmaxsh          , "      vmaxsh", },
    { &test_vmaxsw          , "      vmaxsw", },
    { &test_vminub          , "      vminub", },
    { &test_vminuh          , "      vminuh", },
    { &test_vminuw          , "      vminuw", },
    { &test_vminsb          , "      vminsb", },
    { &test_vminsh          , "      vminsh", },
    { &test_vminsw          , "      vminsw", },
    { NULL,                   NULL,           },
};
#endif /* defined (HAS_ALTIVEC) */

#if defined (HAS_ALTIVEC)
static void test_vand (void)
{
    __asm__ __volatile__ ("vand         17, 14, 15");
}

static void test_vor (void)
{
    __asm__ __volatile__ ("vor          17, 14, 15");
}

static void test_vxor (void)
{
    __asm__ __volatile__ ("vxor         17, 14, 15");
}

static void test_vandc (void)
{
    __asm__ __volatile__ ("vandc        17, 14, 15");
}

static void test_vnor (void)
{
    __asm__ __volatile__ ("vnor         17, 14, 15");
}

static void test_vrlb (void)
{
    __asm__ __volatile__ ("vrlb         17, 14, 15");
}

static void test_vrlh (void)
{
    __asm__ __volatile__ ("vrlh         17, 14, 15");
}

static void test_vrlw (void)
{
    __asm__ __volatile__ ("vrlw         17, 14, 15");
}

static void test_vslb (void)
{
    __asm__ __volatile__ ("vslb         17, 14, 15");
}

static void test_vslh (void)
{
    __asm__ __volatile__ ("vslh         17, 14, 15");
}

static void test_vslw (void)
{
    __asm__ __volatile__ ("vslw         17, 14, 15");
}

static void test_vsrb (void)
{
    __asm__ __volatile__ ("vsrb         17, 14, 15");
}

static void test_vsrh (void)
{
    __asm__ __volatile__ ("vsrh         17, 14, 15");
}

static void test_vsrw (void)
{
    __asm__ __volatile__ ("vsrw         17, 14, 15");
}

static void test_vsrab (void)
{
    __asm__ __volatile__ ("vsrab        17, 14, 15");
}

static void test_vsrah (void)
{
    __asm__ __volatile__ ("vsrah        17, 14, 15");
}

static void test_vsraw (void)
{
    __asm__ __volatile__ ("vsraw        17, 14, 15");
}

static void test_vpkuhum (void)
{
    __asm__ __volatile__ ("vpkuhum      17, 14, 15");
}

static void test_vpkuwum (void)
{
    __asm__ __volatile__ ("vpkuwum      17, 14, 15");
}

static void test_vpkuhus (void)
{
    __asm__ __volatile__ ("vpkuhus      17, 14, 15");
}

static void test_vpkuwus (void)
{
    __asm__ __volatile__ ("vpkuwus      17, 14, 15");
}

static void test_vpkshus (void)
{
    __asm__ __volatile__ ("vpkshus      17, 14, 15");
}

static void test_vpkswus (void)
{
    __asm__ __volatile__ ("vpkswus      17, 14, 15");
}

static void test_vpkshss (void)
{
    __asm__ __volatile__ ("vpkshss      17, 14, 15");
}

static void test_vpkswss (void)
{
    __asm__ __volatile__ ("vpkswss      17, 14, 15");
}

static void test_vpkpx (void)
{
    __asm__ __volatile__ ("vpkpx        17, 14, 15");
}

static void test_vmrghb (void)
{
    __asm__ __volatile__ ("vmrghb       17, 14, 15");
}

static void test_vmrghh (void)
{
    __asm__ __volatile__ ("vmrghh       17, 14, 15");
}

static void test_vmrghw (void)
{
    __asm__ __volatile__ ("vmrghw       17, 14, 15");
}

static void test_vmrglb (void)
{
    __asm__ __volatile__ ("vmrglb       17, 14, 15");
}

static void test_vmrglh (void)
{
    __asm__ __volatile__ ("vmrglh       17, 14, 15");
}

static void test_vmrglw (void)
{
    __asm__ __volatile__ ("vmrglw       17, 14, 15");
}

static void test_vsl (void)
{
    __asm__ __volatile__ ("vsl          17, 14, 15");
}

static void test_vsr (void)
{
    __asm__ __volatile__ ("vsr          17, 14, 15");
}

static void test_vslo (void)
{
    __asm__ __volatile__ ("vslo         17, 14, 15");
}

static void test_vsro (void)
{
    __asm__ __volatile__ ("vsro         17, 14, 15");
}

static test_t tests_al_ops_two[] = {
    { &test_vand            , "        vand", },
    { &test_vor             , "         vor", },
    { &test_vxor            , "        vxor", },
    { &test_vandc           , "       vandc", },
    { &test_vnor            , "        vnor", },
    { &test_vrlb            , "        vrlb", },
    { &test_vrlh            , "        vrlh", },
    { &test_vrlw            , "        vrlw", },
    { &test_vslb            , "        vslb", },
    { &test_vslh            , "        vslh", },
    { &test_vslw            , "        vslw", },
    { &test_vsrb            , "        vsrb", },
    { &test_vsrh            , "        vsrh", },
    { &test_vsrw            , "        vsrw", },
    { &test_vsrab           , "       vsrab", },
    { &test_vsrah           , "       vsrah", },
    { &test_vsraw           , "       vsraw", },
    { &test_vpkuhum         , "     vpkuhum", },
    { &test_vpkuwum         , "     vpkuwum", },
    { &test_vpkuhus         , "     vpkuhus", },
    { &test_vpkuwus         , "     vpkuwus", },
    { &test_vpkshus         , "     vpkshus", },
    { &test_vpkswus         , "     vpkswus", },
    { &test_vpkshss         , "     vpkshss", },
    { &test_vpkswss         , "     vpkswss", },
    { &test_vpkpx           , "       vpkpx", },
    { &test_vmrghb          , "      vmrghb", },
    { &test_vmrghh          , "      vmrghh", },
    { &test_vmrghw          , "      vmrghw", },
    { &test_vmrglb          , "      vmrglb", },
    { &test_vmrglh          , "      vmrglh", },
    { &test_vmrglw          , "      vmrglw", },
    { &test_vsl             , "         vsl", },
    { &test_vsr             , "         vsr", },
    { &test_vslo            , "        vslo", },
    { &test_vsro            , "        vsro", },
    { NULL,                   NULL,           },
};
#endif /* defined (HAS_ALTIVEC) */

#if defined (HAS_ALTIVEC)
static void test_vupkhsb (void)
{
    __asm__ __volatile__ ("vupkhsb      17, 14");
}

static void test_vupkhsh (void)
{
    __asm__ __volatile__ ("vupkhsh      17, 14");
}

static void test_vupkhpx (void)
{
    __asm__ __volatile__ ("vupkhpx      17, 14");
}

static void test_vupklsb (void)
{
    __asm__ __volatile__ ("vupklsb      17, 14");
}

static void test_vupklsh (void)
{
    __asm__ __volatile__ ("vupklsh      17, 14");
}

static void test_vupklpx (void)
{
    __asm__ __volatile__ ("vupklpx      17, 14");
}

static test_t tests_al_ops_one[] = {
    { &test_vupkhsb         , "     vupkhsb", },
    { &test_vupkhsh         , "     vupkhsh", },
    { &test_vupkhpx         , "     vupkhpx", },
    { &test_vupklsb         , "     vupklsb", },
    { &test_vupklsh         , "     vupklsh", },
    { &test_vupklpx         , "     vupklpx", },
    { NULL,                   NULL,           },
};
#endif /* defined (HAS_ALTIVEC) */

#if defined (HAS_ALTIVEC)
static void test_vcmpgtub (void)
{
    __asm__ __volatile__ ("vcmpgtub     17, 14, 15");
}

static void test_vcmpgtuh (void)
{
    __asm__ __volatile__ ("vcmpgtuh     17, 14, 15");
}

static void test_vcmpgtuw (void)
{
    __asm__ __volatile__ ("vcmpgtuw     17, 14, 15");
}

static void test_vcmpgtsb (void)
{
    __asm__ __volatile__ ("vcmpgtsb     17, 14, 15");
}

static void test_vcmpgtsh (void)
{
    __asm__ __volatile__ ("vcmpgtsh     17, 14, 15");
}

static void test_vcmpgtsw (void)
{
    __asm__ __volatile__ ("vcmpgtsw     17, 14, 15");
}

static void test_vcmpequb (void)
{
    __asm__ __volatile__ ("vcmpequb     17, 14, 15");
}

static void test_vcmpequh (void)
{
    __asm__ __volatile__ ("vcmpequh     17, 14, 15");
}

static void test_vcmpequw (void)
{
    __asm__ __volatile__ ("vcmpequw     17, 14, 15");
}

static test_t tests_ac_ops_two[] = {
    { &test_vcmpgtub        , "    vcmpgtub", },
    { &test_vcmpgtuh        , "    vcmpgtuh", },
    { &test_vcmpgtuw        , "    vcmpgtuw", },
    { &test_vcmpgtsb        , "    vcmpgtsb", },
    { &test_vcmpgtsh        , "    vcmpgtsh", },
    { &test_vcmpgtsw        , "    vcmpgtsw", },
    { &test_vcmpequb        , "    vcmpequb", },
    { &test_vcmpequh        , "    vcmpequh", },
    { &test_vcmpequw        , "    vcmpequw", },
    { NULL,                   NULL,           },
};
#endif /* defined (HAS_ALTIVEC) */

#if defined (HAS_ALTIVEC)
static void test_vcmpgtub_ (void)
{
    __asm__ __volatile__ ("vcmpgtub.    17, 14, 15");
}

static void test_vcmpgtuh_ (void)
{
    __asm__ __volatile__ ("vcmpgtuh.    17, 14, 15");
}

static void test_vcmpgtuw_ (void)
{
    __asm__ __volatile__ ("vcmpgtuw.    17, 14, 15");
}

static void test_vcmpgtsb_ (void)
{
    __asm__ __volatile__ ("vcmpgtsb.    17, 14, 15");
}

static void test_vcmpgtsh_ (void)
{
    __asm__ __volatile__ ("vcmpgtsh.    17, 14, 15");
}

static void test_vcmpgtsw_ (void)
{
    __asm__ __volatile__ ("vcmpgtsw.    17, 14, 15");
}

static void test_vcmpequb_ (void)
{
    __asm__ __volatile__ ("vcmpequb.    17, 14, 15");
}

static void test_vcmpequh_ (void)
{
    __asm__ __volatile__ ("vcmpequh.    17, 14, 15");
}

static void test_vcmpequw_ (void)
{
    __asm__ __volatile__ ("vcmpequw.    17, 14, 15");
}

static test_t tests_acr_ops_two[] = {
    { &test_vcmpgtub_       , "   vcmpgtub.", },
    { &test_vcmpgtuh_       , "   vcmpgtuh.", },
    { &test_vcmpgtuw_       , "   vcmpgtuw.", },
    { &test_vcmpgtsb_       , "   vcmpgtsb.", },
    { &test_vcmpgtsh_       , "   vcmpgtsh.", },
    { &test_vcmpgtsw_       , "   vcmpgtsw.", },
    { &test_vcmpequb_       , "   vcmpequb.", },
    { &test_vcmpequh_       , "   vcmpequh.", },
    { &test_vcmpequw_       , "   vcmpequw.", },
    { NULL,                   NULL,           },
};
#endif /* defined (HAS_ALTIVEC) */

#if defined (HAS_ALTIVEC)
static void test_vmaddfp (void)
{
    __asm__ __volatile__ ("vmaddfp      17, 14, 15, 16");
}

static void test_vnmsubfp (void)
{
    __asm__ __volatile__ ("vnmsubfp     17, 14, 15, 16");
}

static test_t tests_afa_ops_three[] = {
    { &test_vmaddfp         , "     vmaddfp", },
    { &test_vnmsubfp        , "    vnmsubfp", },
    { NULL,                   NULL,           },
};
#endif /* defined (HAS_ALTIVEC) */

#if defined (HAS_ALTIVEC)
static void test_vaddfp (void)
{
    __asm__ __volatile__ ("vaddfp       17, 14, 15");
}

static void test_vsubfp (void)
{
    __asm__ __volatile__ ("vsubfp       17, 14, 15");
}

static void test_vmaxfp (void)
{
    __asm__ __volatile__ ("vmaxfp       17, 14, 15");
}

static void test_vminfp (void)
{
    __asm__ __volatile__ ("vminfp       17, 14, 15");
}

static test_t tests_afa_ops_two[] = {
    { &test_vaddfp          , "      vaddfp", },
    { &test_vsubfp          , "      vsubfp", },
    { &test_vmaxfp          , "      vmaxfp", },
    { &test_vminfp          , "      vminfp", },
    { NULL,                   NULL,           },
};
#endif /* defined (HAS_ALTIVEC) */

#if defined (HAS_ALTIVEC)
static void test_vrfin (void)
{
    __asm__ __volatile__ ("vrfin        17, 14");
}

static void test_vrfiz (void)
{
    __asm__ __volatile__ ("vrfiz        17, 14");
}

static void test_vrfip (void)
{
    __asm__ __volatile__ ("vrfip        17, 14");
}

static void test_vrfim (void)
{
    __asm__ __volatile__ ("vrfim        17, 14");
}

static void test_vrefp (void)
{
    __asm__ __volatile__ ("vrefp        17, 14");
}

static void test_vrsqrtefp (void)
{
    __asm__ __volatile__ ("vrsqrtefp    17, 14");
}

static void test_vlogefp (void)
{
    __asm__ __volatile__ ("vlogefp      17, 14");
}

static void test_vexptefp (void)
{
    __asm__ __volatile__ ("vexptefp     17, 14");
}

static test_t tests_afa_ops_one[] = {
    { &test_vrfin           , "       vrfin", },
    { &test_vrfiz           , "       vrfiz", },
    { &test_vrfip           , "       vrfip", },
    { &test_vrfim           , "       vrfim", },
    { &test_vrefp           , "       vrefp", },
    { &test_vrsqrtefp       , "   vrsqrtefp", },
    { &test_vlogefp         , "     vlogefp", },
    { &test_vexptefp        , "    vexptefp", },
    { NULL,                   NULL,           },
};
#endif /* defined (HAS_ALTIVEC) */

#if defined (HAS_ALTIVEC)
static void test_vcmpgtfp (void)
{
    __asm__ __volatile__ ("vcmpgtfp     17, 14, 15");
}

static void test_vcmpeqfp (void)
{
    __asm__ __volatile__ ("vcmpeqfp     17, 14, 15");
}

static void test_vcmpgefp (void)
{
    __asm__ __volatile__ ("vcmpgefp     17, 14, 15");
}

static void test_vcmpbfp (void)
{
    __asm__ __volatile__ ("vcmpbfp      17, 14, 15");
}

static test_t tests_afc_ops_two[] = {
    { &test_vcmpgtfp        , "    vcmpgtfp", },
    { &test_vcmpeqfp        , "    vcmpeqfp", },
    { &test_vcmpgefp        , "    vcmpgefp", },
    { &test_vcmpbfp         , "     vcmpbfp", },
    { NULL,                   NULL,           },
};
#endif /* defined (HAS_ALTIVEC) */

#if defined (HAS_ALTIVEC)
static void test_vcmpgtfp_ (void)
{
    __asm__ __volatile__ ("vcmpgtfp.    17, 14, 15");
}

static void test_vcmpeqfp_ (void)
{
    __asm__ __volatile__ ("vcmpeqfp.    17, 14, 15");
}

static void test_vcmpgefp_ (void)
{
    __asm__ __volatile__ ("vcmpgefp.    17, 14, 15");
}

static void test_vcmpbfp_ (void)
{
    __asm__ __volatile__ ("vcmpbfp.     17, 14, 15");
}

static test_t tests_afcr_ops_two[] = {
    { &test_vcmpgtfp_       , "   vcmpgtfp.", },
    { &test_vcmpeqfp_       , "   vcmpeqfp.", },
    { &test_vcmpgefp_       , "   vcmpgefp.", },
    { &test_vcmpbfp_        , "    vcmpbfp.", },
    { NULL,                   NULL,           },
};
#endif /* defined (HAS_ALTIVEC) */

#if defined (IS_PPC405)
static void test_macchw (void)
{
    __asm__ __volatile__ ("macchw       17, 14, 15");
}

static void test_macchwo (void)
{
    __asm__ __volatile__ ("macchwo      17, 14, 15");
}

static void test_macchws (void)
{
    __asm__ __volatile__ ("macchws      17, 14, 15");
}

static void test_macchwso (void)
{
    __asm__ __volatile__ ("macchwso     17, 14, 15");
}

static void test_macchwsu (void)
{
    __asm__ __volatile__ ("macchwsu     17, 14, 15");
}

static void test_macchwsuo (void)
{
    __asm__ __volatile__ ("macchwsuo    17, 14, 15");
}

static void test_macchwu (void)
{
    __asm__ __volatile__ ("macchwu      17, 14, 15");
}

static void test_macchwuo (void)
{
    __asm__ __volatile__ ("macchwuo     17, 14, 15");
}

static void test_machhw (void)
{
    __asm__ __volatile__ ("machhw       17, 14, 15");
}

static void test_machhwo (void)
{
    __asm__ __volatile__ ("machhwo      17, 14, 15");
}

static void test_machhws (void)
{
    __asm__ __volatile__ ("machhws      17, 14, 15");
}

static void test_machhwso (void)
{
    __asm__ __volatile__ ("machhwso     17, 14, 15");
}

static void test_machhwsu (void)
{
    __asm__ __volatile__ ("machhwsu     17, 14, 15");
}

static void test_machhwsuo (void)
{
    __asm__ __volatile__ ("machhwsuo    17, 14, 15");
}

static void test_machhwu (void)
{
    __asm__ __volatile__ ("machhwu      17, 14, 15");
}

static void test_machhwuo (void)
{
    __asm__ __volatile__ ("machhwuo     17, 14, 15");
}

static void test_maclhw (void)
{
    __asm__ __volatile__ ("maclhw       17, 14, 15");
}

static void test_maclhwo (void)
{
    __asm__ __volatile__ ("maclhwo      17, 14, 15");
}

static void test_maclhws (void)
{
    __asm__ __volatile__ ("maclhws      17, 14, 15");
}

static void test_maclhwso (void)
{
    __asm__ __volatile__ ("maclhwso     17, 14, 15");
}

static void test_maclhwsu (void)
{
    __asm__ __volatile__ ("maclhwsu     17, 14, 15");
}

static void test_maclhwsuo (void)
{
    __asm__ __volatile__ ("maclhwsuo    17, 14, 15");
}

static void test_maclhwu (void)
{
    __asm__ __volatile__ ("maclhwu      17, 14, 15");
}

static void test_maclhwuo (void)
{
    __asm__ __volatile__ ("maclhwuo     17, 14, 15");
}

static void test_mulchw (void)
{
    __asm__ __volatile__ ("mulchw       17, 14, 15");
}

static void test_mulchwu (void)
{
    __asm__ __volatile__ ("mulchwu      17, 14, 15");
}

static void test_mulhhw (void)
{
    __asm__ __volatile__ ("mulhhw       17, 14, 15");
}

static void test_mulhhwu (void)
{
    __asm__ __volatile__ ("mulhhwu      17, 14, 15");
}

static void test_mullhw (void)
{
    __asm__ __volatile__ ("mullhw       17, 14, 15");
}

static void test_mullhwu (void)
{
    __asm__ __volatile__ ("mullhwu      17, 14, 15");
}

static void test_nmacchw (void)
{
    __asm__ __volatile__ ("nmacchw      17, 14, 15");
}

static void test_nmacchwo (void)
{
    __asm__ __volatile__ ("nmacchwo     17, 14, 15");
}

static void test_nmacchws (void)
{
    __asm__ __volatile__ ("nmacchws     17, 14, 15");
}

static void test_nmacchwso (void)
{
    __asm__ __volatile__ ("nmacchwso    17, 14, 15");
}

static void test_nmachhw (void)
{
    __asm__ __volatile__ ("nmachhw      17, 14, 15");
}

static void test_nmachhwo (void)
{
    __asm__ __volatile__ ("nmachhwo     17, 14, 15");
}

static void test_nmachhws (void)
{
    __asm__ __volatile__ ("nmachhws     17, 14, 15");
}

static void test_nmachhwso (void)
{
    __asm__ __volatile__ ("nmachhwso    17, 14, 15");
}

static void test_nmaclhw (void)
{
    __asm__ __volatile__ ("nmaclhw      17, 14, 15");
}

static void test_nmaclhwo (void)
{
    __asm__ __volatile__ ("nmaclhwo     17, 14, 15");
}

static void test_nmaclhws (void)
{
    __asm__ __volatile__ ("nmaclhws     17, 14, 15");
}

static void test_nmaclhwso (void)
{
    __asm__ __volatile__ ("nmaclhwso    17, 14, 15");
}

static test_t tests_p4m_ops_two[] = {
    { &test_macchw          , "      macchw", },
    { &test_macchwo         , "     macchwo", },
    { &test_macchws         , "     macchws", },
    { &test_macchwso        , "    macchwso", },
    { &test_macchwsu        , "    macchwsu", },
    { &test_macchwsuo       , "   macchwsuo", },
    { &test_macchwu         , "     macchwu", },
    { &test_macchwuo        , "    macchwuo", },
    { &test_machhw          , "      machhw", },
    { &test_machhwo         , "     machhwo", },
    { &test_machhws         , "     machhws", },
    { &test_machhwso        , "    machhwso", },
    { &test_machhwsu        , "    machhwsu", },
    { &test_machhwsuo       , "   machhwsuo", },
    { &test_machhwu         , "     machhwu", },
    { &test_machhwuo        , "    machhwuo", },
    { &test_maclhw          , "      maclhw", },
    { &test_maclhwo         , "     maclhwo", },
    { &test_maclhws         , "     maclhws", },
    { &test_maclhwso        , "    maclhwso", },
    { &test_maclhwsu        , "    maclhwsu", },
    { &test_maclhwsuo       , "   maclhwsuo", },
    { &test_maclhwu         , "     maclhwu", },
    { &test_maclhwuo        , "    maclhwuo", },
    { &test_mulchw          , "      mulchw", },
    { &test_mulchwu         , "     mulchwu", },
    { &test_mulhhw          , "      mulhhw", },
    { &test_mulhhwu         , "     mulhhwu", },
    { &test_mullhw          , "      mullhw", },
    { &test_mullhwu         , "     mullhwu", },
    { &test_nmacchw         , "     nmacchw", },
    { &test_nmacchwo        , "    nmacchwo", },
    { &test_nmacchws        , "    nmacchws", },
    { &test_nmacchwso       , "   nmacchwso", },
    { &test_nmachhw         , "     nmachhw", },
    { &test_nmachhwo        , "    nmachhwo", },
    { &test_nmachhws        , "    nmachhws", },
    { &test_nmachhwso       , "   nmachhwso", },
    { &test_nmaclhw         , "     nmaclhw", },
    { &test_nmaclhwo        , "    nmaclhwo", },
    { &test_nmaclhws        , "    nmaclhws", },
    { &test_nmaclhwso       , "   nmaclhwso", },
    { NULL,                   NULL,           },
};
#endif /* defined (IS_PPC405) */

#if defined (IS_PPC405)
static void test_macchw_ (void)
{
    __asm__ __volatile__ ("macchw.      17, 14, 15");
}

static void test_macchwo_ (void)
{
    __asm__ __volatile__ ("macchwo.     17, 14, 15");
}

static void test_macchws_ (void)
{
    __asm__ __volatile__ ("macchws.     17, 14, 15");
}

static void test_macchwso_ (void)
{
    __asm__ __volatile__ ("macchwso.    17, 14, 15");
}

static void test_macchwsu_ (void)
{
    __asm__ __volatile__ ("macchwsu.    17, 14, 15");
}

static void test_macchwsuo_ (void)
{
    __asm__ __volatile__ ("macchwsuo.   17, 14, 15");
}

static void test_macchwu_ (void)
{
    __asm__ __volatile__ ("macchwu.     17, 14, 15");
}

static void test_macchwuo_ (void)
{
    __asm__ __volatile__ ("macchwuo.    17, 14, 15");
}

static void test_machhw_ (void)
{
    __asm__ __volatile__ ("machhw.      17, 14, 15");
}

static void test_machhwo_ (void)
{
    __asm__ __volatile__ ("machhwo.     17, 14, 15");
}

static void test_machhws_ (void)
{
    __asm__ __volatile__ ("machhws.     17, 14, 15");
}

static void test_machhwso_ (void)
{
    __asm__ __volatile__ ("machhwso.    17, 14, 15");
}

static void test_machhwsu_ (void)
{
    __asm__ __volatile__ ("machhwsu.    17, 14, 15");
}

static void test_machhwsuo_ (void)
{
    __asm__ __volatile__ ("machhwsuo.   17, 14, 15");
}

static void test_machhwu_ (void)
{
    __asm__ __volatile__ ("machhwu.     17, 14, 15");
}

static void test_machhwuo_ (void)
{
    __asm__ __volatile__ ("machhwuo.    17, 14, 15");
}

static void test_maclhw_ (void)
{
    __asm__ __volatile__ ("maclhw.      17, 14, 15");
}

static void test_maclhwo_ (void)
{
    __asm__ __volatile__ ("maclhwo.     17, 14, 15");
}

static void test_maclhws_ (void)
{
    __asm__ __volatile__ ("maclhws.     17, 14, 15");
}

static void test_maclhwso_ (void)
{
    __asm__ __volatile__ ("maclhwso.    17, 14, 15");
}

static void test_maclhwsu_ (void)
{
    __asm__ __volatile__ ("maclhwsu.    17, 14, 15");
}

static void test_maclhwsuo_ (void)
{
    __asm__ __volatile__ ("maclhwsuo.   17, 14, 15");
}

static void test_maclhwu_ (void)
{
    __asm__ __volatile__ ("maclhwu.     17, 14, 15");
}

static void test_maclhwuo_ (void)
{
    __asm__ __volatile__ ("maclhwuo.    17, 14, 15");
}

static void test_mulchw_ (void)
{
    __asm__ __volatile__ ("mulchw.      17, 14, 15");
}

static void test_mulchwu_ (void)
{
    __asm__ __volatile__ ("mulchwu.     17, 14, 15");
}

static void test_mulhhw_ (void)
{
    __asm__ __volatile__ ("mulhhw.      17, 14, 15");
}

static void test_mulhhwu_ (void)
{
    __asm__ __volatile__ ("mulhhwu.     17, 14, 15");
}

static void test_mullhw_ (void)
{
    __asm__ __volatile__ ("mullhw.      17, 14, 15");
}

static void test_mullhwu_ (void)
{
    __asm__ __volatile__ ("mullhwu.     17, 14, 15");
}

static void test_nmacchw_ (void)
{
    __asm__ __volatile__ ("nmacchw.     17, 14, 15");
}

static void test_nmacchwo_ (void)
{
    __asm__ __volatile__ ("nmacchwo.    17, 14, 15");
}

static void test_nmacchws_ (void)
{
    __asm__ __volatile__ ("nmacchws.    17, 14, 15");
}

static void test_nmacchwso_ (void)
{
    __asm__ __volatile__ ("nmacchwso.   17, 14, 15");
}

static void test_nmachhw_ (void)
{
    __asm__ __volatile__ ("nmachhw.     17, 14, 15");
}

static void test_nmachhwo_ (void)
{
    __asm__ __volatile__ ("nmachhwo.    17, 14, 15");
}

static void test_nmachhws_ (void)
{
    __asm__ __volatile__ ("nmachhws.    17, 14, 15");
}

static void test_nmachhwso_ (void)
{
    __asm__ __volatile__ ("nmachhwso.   17, 14, 15");
}

static void test_nmaclhw_ (void)
{
    __asm__ __volatile__ ("nmaclhw.     17, 14, 15");
}

static void test_nmaclhwo_ (void)
{
    __asm__ __volatile__ ("nmaclhwo.    17, 14, 15");
}

static void test_nmaclhws_ (void)
{
    __asm__ __volatile__ ("nmaclhws.    17, 14, 15");
}

static void test_nmaclhwso_ (void)
{
    __asm__ __volatile__ ("nmaclhwso.   17, 14, 15");
}

static test_t tests_p4mc_ops_two[] = {
    { &test_macchw_         , "     macchw.", },
    { &test_macchwo_        , "    macchwo.", },
    { &test_macchws_        , "    macchws.", },
    { &test_macchwso_       , "   macchwso.", },
    { &test_macchwsu_       , "   macchwsu.", },
    { &test_macchwsuo_      , "  macchwsuo.", },
    { &test_macchwu_        , "    macchwu.", },
    { &test_macchwuo_       , "   macchwuo.", },
    { &test_machhw_         , "     machhw.", },
    { &test_machhwo_        , "    machhwo.", },
    { &test_machhws_        , "    machhws.", },
    { &test_machhwso_       , "   machhwso.", },
    { &test_machhwsu_       , "   machhwsu.", },
    { &test_machhwsuo_      , "  machhwsuo.", },
    { &test_machhwu_        , "    machhwu.", },
    { &test_machhwuo_       , "   machhwuo.", },
    { &test_maclhw_         , "     maclhw.", },
    { &test_maclhwo_        , "    maclhwo.", },
    { &test_maclhws_        , "    maclhws.", },
    { &test_maclhwso_       , "   maclhwso.", },
    { &test_maclhwsu_       , "   maclhwsu.", },
    { &test_maclhwsuo_      , "  maclhwsuo.", },
    { &test_maclhwu_        , "    maclhwu.", },
    { &test_maclhwuo_       , "   maclhwuo.", },
    { &test_mulchw_         , "     mulchw.", },
    { &test_mulchwu_        , "    mulchwu.", },
    { &test_mulhhw_         , "     mulhhw.", },
    { &test_mulhhwu_        , "    mulhhwu.", },
    { &test_mullhw_         , "     mullhw.", },
    { &test_mullhwu_        , "    mullhwu.", },
    { &test_nmacchw_        , "    nmacchw.", },
    { &test_nmacchwo_       , "   nmacchwo.", },
    { &test_nmacchws_       , "   nmacchws.", },
    { &test_nmacchwso_      , "  nmacchwso.", },
    { &test_nmachhw_        , "    nmachhw.", },
    { &test_nmachhwo_       , "   nmachhwo.", },
    { &test_nmachhws_       , "   nmachhws.", },
    { &test_nmachhwso_      , "  nmachhwso.", },
    { &test_nmaclhw_        , "    nmaclhw.", },
    { &test_nmaclhwo_       , "   nmaclhwo.", },
    { &test_nmaclhws_       , "   nmaclhws.", },
    { &test_nmaclhwso_      , "  nmaclhwso.", },
    { NULL,                   NULL,           },
};
#endif /* defined (IS_PPC405) */

static test_table_t all_tests[] = {
    {
        tests_ia_ops_two      ,
        "PPC integer arithmetic instructions with two arguments",
        0x00010102,
    },
    {
        tests_iar_ops_two     ,
        "PPC integer instructions with two arguments with flags update",
        0x01010102,
    },
    {
        tests_il_ops_two      ,
        "PPC integer logical instructions with two arguments",
        0x00010202,
    },
    {
        tests_ilr_ops_two     ,
        "PPC integer logical instructions with two arguments with flags update",
        0x01010202,
    },
    {
        tests_icr_ops_two     ,
        "PPC integer compare instructions (two arguents)",
        0x01010304,
    },
    {
        tests_icr_ops_two_i16 ,
        "PPC integer compare with immediate instructions (two arguents)",
        0x01010304,
    },
    {
        tests_ia_ops_two_i16  ,
        "PPC integer arithmetic instructions\n    with one register + one 16 bits immediate arguments",
        0x00010106,
    },
    {
        tests_iar_ops_two_i16 ,
        "PPC integer arithmetic instructions\n    with one register + one 16 bits immediate arguments with flags update",
        0x01010106,
    },
    {
        tests_il_ops_two_i16  ,
        "PPC integer logical instructions\n    with one register + one 16 bits immediate arguments",
        0x00010206,
    },
    {
        tests_ilr_ops_two_i16 ,
        "PPC integer logical instructions\n    with one register + one 16 bits immediate arguments with flags update",
        0x01010206,
    },
    {
        tests_crl_ops_two     ,
        "PPC condition register logical instructions - two operands",
        0x01000602,
    },
    {
        tests_ia_ops_one      ,
        "PPC integer arithmetic instructions with one argument",
        0x00010101,
    },
    {
        tests_iar_ops_one     ,
        "PPC integer arithmetic instructions with one argument with flags update",
        0x01010101,
    },
    {
        tests_il_ops_one      ,
        "PPC integer logical instructions with one argument",
        0x00010201,
    },
    {
        tests_ilr_ops_one     ,
        "PPC integer logical instructions with one argument with flags update",
        0x01010201,
    },
    {
        tests_il_ops_spe      ,
        "PPC logical instructions with special forms",
        0x00010207,
    },
    {
        tests_ilr_ops_spe     ,
        "PPC logical instructions with special forms with flags update",
        0x01010207,
    },
#if !defined (NO_FLOAT)
    {
        tests_fa_ops_three    ,
        "PPC floating point arithmetic instructions with three arguments",
        0x00020103,
    },
#endif /* !defined (NO_FLOAT) */
#if !defined (NO_FLOAT)
    {
        tests_far_ops_three   ,
        "PPC floating point arithmetic instructions\n    with three arguments with flags update",
        0x01020103,
    },
#endif /* !defined (NO_FLOAT) */
#if !defined (NO_FLOAT)
    {
        tests_fa_ops_two      ,
        "PPC floating point arithmetic instructions with two arguments",
        0x00020102,
    },
#endif /* !defined (NO_FLOAT) */
#if !defined (NO_FLOAT)
    {
        tests_far_ops_two     ,
        "PPC floating point arithmetic instructions\n    with two arguments with flags update",
        0x01020102,
    },
#endif /* !defined (NO_FLOAT) */
#if !defined (NO_FLOAT)
    {
        tests_fcr_ops_two     ,
        "PPC floating point compare instructions (two arguments)",
        0x01020304,
    },
#endif /* !defined (NO_FLOAT) */
#if !defined (NO_FLOAT)
    {
        tests_fa_ops_one      ,
        "PPC floating point arithmetic instructions with one argument",
        0x00020101,
    },
#endif /* !defined (NO_FLOAT) */
#if !defined (NO_FLOAT)
    {
        tests_far_ops_one     ,
        "PPC floating point arithmetic instructions\n    with one argument with flags update",
        0x01020101,
    },
#endif /* !defined (NO_FLOAT) */
#if !defined (NO_FLOAT)
    {
        tests_fl_ops_spe      ,
        "PPC floating point status register manipulation instructions",
        0x00020207,
    },
#endif /* !defined (NO_FLOAT) */
#if !defined (NO_FLOAT)
    {
        tests_flr_ops_spe     ,
        "PPC floating point status register manipulation instructions\n  with flags update",
        0x01020207,
    },
#endif /* !defined (NO_FLOAT) */
#if defined (HAS_ALTIVEC)
    {
        tests_aa_ops_three    ,
        "PPC altivec integer arithmetic instructions with three arguments",
        0x00040103,
    },
#endif /* defined (HAS_ALTIVEC) */
#if defined (HAS_ALTIVEC)
    {
        tests_al_ops_three    ,
        "PPC altivec integer logical instructions with three arguments",
        0x00040203,
    },
#endif /* defined (HAS_ALTIVEC) */
#if defined (HAS_ALTIVEC)
    {
        tests_aa_ops_two      ,
        "PPC altivec integer arithmetic instructions with two arguments",
        0x00040102,
    },
#endif /* defined (HAS_ALTIVEC) */
#if defined (HAS_ALTIVEC)
    {
        tests_al_ops_two      ,
        "PPC altivec integer logical instructions with two arguments",
        0x00040202,
    },
#endif /* defined (HAS_ALTIVEC) */
#if defined (HAS_ALTIVEC)
    {
        tests_al_ops_one      ,
        "PPC altivec integer logical instructions with one argument",
        0x00040201,
    },
#endif /* defined (HAS_ALTIVEC) */
#if defined (HAS_ALTIVEC)
    {
        tests_ac_ops_two      ,
        "Altivec integer compare instructions",
        0x00040302,
    },
#endif /* defined (HAS_ALTIVEC) */
#if defined (HAS_ALTIVEC)
    {
        tests_acr_ops_two     ,
        "Altivec integer compare instructions with flags update",
        0x01040302,
    },
#endif /* defined (HAS_ALTIVEC) */
#if defined (HAS_ALTIVEC)
    {
        tests_afa_ops_three   ,
        "Altivec floating point arithmetic instructions with three arguments",
        0x00050103,
    },
#endif /* defined (HAS_ALTIVEC) */
#if defined (HAS_ALTIVEC)
    {
        tests_afa_ops_two     ,
        "Altivec floating point arithmetic instructions with two arguments",
        0x00050102,
    },
#endif /* defined (HAS_ALTIVEC) */
#if defined (HAS_ALTIVEC)
    {
        tests_afa_ops_one     ,
        "Altivec floating point arithmetic instructions with one argument",
        0x00050101,
    },
#endif /* defined (HAS_ALTIVEC) */
#if defined (HAS_ALTIVEC)
    {
        tests_afc_ops_two     ,
        "Altivec floating point compare instructions",
        0x00050302,
    },
#endif /* defined (HAS_ALTIVEC) */
#if defined (HAS_ALTIVEC)
    {
        tests_afcr_ops_two    ,
        "Altivec floating point compare instructions with flags update",
        0x01050302,
    },
#endif /* defined (HAS_ALTIVEC) */
#if defined (IS_PPC405)
    {
        tests_p4m_ops_two     ,
        "PPC 405 mac instructions with three arguments",
        0x00030102,
    },
#endif /* defined (IS_PPC405) */
#if defined (IS_PPC405)
    {
        tests_p4mc_ops_two    ,
        "PPC 405 mac instructions with three arguments with flags update",
        0x01030102,
    },
#endif /* defined (IS_PPC405) */
    { NULL,                   NULL,               0x00000000, },
};

// END #include "ops-ppc.c"


static int verbose = 0;

static double *fargs;
static int nb_fargs;
static uint32_t *iargs;
static int nb_iargs;
static uint16_t *ii16;
static int nb_ii16;

static inline void register_farg (void *farg,
                                  int s, uint16_t _exp, uint64_t mant)
{
    uint64_t tmp;

    tmp = ((uint64_t)s << 63) | ((uint64_t)_exp << 52) | mant;
    *(uint64_t *)farg = tmp;
    AB_DPRINTF("%d %03x %013llx => %016llx %0e\n",
               s, _exp, mant, *(uint64_t *)farg, *(double *)farg);
}

static void build_fargs_table (void)
{
    /* Sign goes from zero to one
     * Exponent goes from 0 to ((1 << 12) - 1)
     * Mantissa goes from 1 to ((1 << 52) - 1)
     * + special values:
     * +0.0      : 0 0x000 0x0000000000000
     * -0.0      : 1 0x000 0x0000000000000
     * +infinity : 0 0x7FF 0x0000000000000
     * -infinity : 1 0x7FF 0x0000000000000
     * +SNaN     : 0 0x7FF 0x7FFFFFFFFFFFF
     * -SNaN     : 1 0x7FF 0x7FFFFFFFFFFFF
     * +QNaN     : 0 0x7FF 0x8000000000000
     * -QNaN     : 1 0x7FF 0x8000000000000
     * (8 values)
     */
    uint64_t mant;
    uint16_t _exp, e0, e1;
    int s;
    int i;

    fargs = my_malloc(200 * sizeof(double));
    i = 0;
    for (s = 0; s < 2; s++) {
        for (e0 = 0; e0 < 2; e0++) {
            for (e1 = 0x000; ; e1 = ((e1 + 1) << 2) + 6) {
                if (e1 >= 0x400)
                    e1 = 0x3fe;
                _exp = (e0 << 10) | e1;
                for (mant = 0x0000000000001ULL; mant < (1ULL << 52);
                     /* Add 'random' bits */
                     mant = ((mant + 0x4A6) << 13) + 0x359) {
                    register_farg(&fargs[i++], s, _exp, mant);
                }
                if (e1 == 0x3fe)
                    break;
            }
        }
    }
    /* Special values */
    /* +0.0      : 0 0x000 0x0000000000000 */
    s = 0;
    _exp = 0x000;
    mant = 0x0000000000000ULL;
    register_farg(&fargs[i++], s, _exp, mant);
    /* -0.0      : 1 0x000 0x0000000000000 */
    s = 1;
    _exp = 0x000;
    mant = 0x0000000000000ULL;
    register_farg(&fargs[i++], s, _exp, mant);
    /* +infinity : 0 0x7FF 0x0000000000000  */
    s = 0;
    _exp = 0x7FF;
    mant = 0x0000000000000ULL;
    register_farg(&fargs[i++], s, _exp, mant);
    /* -infinity : 1 0x7FF 0x0000000000000 */
    s = 1;
    _exp = 0x7FF;
    mant = 0x0000000000000ULL;
    register_farg(&fargs[i++], s, _exp, mant);
    /* +SNaN     : 0 0x7FF 0x7FFFFFFFFFFFF */
    s = 0;
    _exp = 0x7FF;
    mant = 0x7FFFFFFFFFFFFULL;
    register_farg(&fargs[i++], s, _exp, mant);
    /* -SNaN     : 1 0x7FF 0x7FFFFFFFFFFFF */
    s = 1;
    _exp = 0x7FF;
    mant = 0x7FFFFFFFFFFFFULL;
    register_farg(&fargs[i++], s, _exp, mant);
    /* +QNaN     : 0 0x7FF 0x8000000000000 */
    s = 0;
    _exp = 0x7FF;
    mant = 0x8000000000000ULL;
    register_farg(&fargs[i++], s, _exp, mant);
    /* -QNaN     : 1 0x7FF 0x8000000000000 */
    s = 1;
    _exp = 0x7FF;
    mant = 0x8000000000000ULL;
    register_farg(&fargs[i++], s, _exp, mant);
    AB_DPRINTF("Registered %d floats values\n", i);
    nb_fargs = i;
}

static void build_iargs_table (void)
{
    uint64_t tmp;
    int i;

    iargs = my_malloc(400 * sizeof(uint32_t));
    i = 0;
    for (tmp = 0; ; tmp = tmp + 1 + (tmp>>1)+(tmp>>2)+(tmp>>3)) {
        if (tmp >= 0x100000000ULL)
            tmp = 0xFFFFFFFF;
        iargs[i++] = tmp;
        AB_DPRINTF("val %08llx\n", tmp);
        if (tmp == 0xFFFFFFFF)
            break;
    }
    AB_DPRINTF("Registered %d ints values\n", i);
    nb_iargs = i;
}

static void build_ii16_table (void)
{
    uint32_t tmp;
    int i;

    ii16 = my_malloc(200 * sizeof(uint32_t));
    i = 0;
    for (tmp = 0; ; tmp = tmp + 1 + (tmp>>1)+(tmp>>2)+(tmp>>3)) {
        if (tmp >= 0x10000)
            tmp = 0xFFFF;
        ii16[i++] = tmp;
        AB_DPRINTF("val %08llx\n", tmp);
        if (tmp == 0xFFFF)
            break;
    }
    AB_DPRINTF("Registered %d ints values\n", i);
    nb_ii16 = i;
}

static void test_int_three_args (const unsigned char *name, test_func_t func)
{
    uint32_t res, flags, xer;
    int i, j, k;

    if (verbose > 1)
        vexxx_printf( "Test instruction %s\n", name);
    for (i = 0; i < nb_iargs; i++) {
        for (j = 0; j < nb_iargs; j++) {
            for (k = 0;k < nb_iargs; k++) {
                r14 = iargs[i];
                r15 = iargs[j];
                r16 = iargs[k];
                r18 = 0;
                __asm__ __volatile__ ("mtcr 18");
                __asm__ __volatile__ ("mtxer 18");
                (*func)();
                __asm__ __volatile__ ("mfcr 18");
                flags = r18;
                __asm__ __volatile__ ("mfxer 18");
                xer = r18;
                res = r17;
                vexxx_printf("%s %08x, %08x, %08x => %08x (%08x %08x)\n",
                       name, iargs[i], iargs[j], iargs[k], res, flags, xer);
            }
            vexxx_printf("\n");
        }
        vexxx_printf("\n");
    }
    vexxx_printf("\n");
}

static void test_int_two_args (const unsigned char *name, test_func_t func)
{
    uint32_t res, flags, xer;
    int i, j;

    if (verbose > 1)
        vexxx_printf( "Test instruction %s\n", name);
    for (i = 0; i < nb_iargs; i++) {
        for (j = 0; j < nb_iargs; j++) {
            r14 = iargs[i];
            r15 = iargs[j];
            r18 = 0;
            __asm__ __volatile__ ("mtcr 18");
            __asm__ __volatile__ ("mtxer 18");
            (*func)();
            __asm__ __volatile__ ("mfcr 18");
            flags = r18;
            __asm__ __volatile__ ("mfxer 18");
            xer = r18;
            res = r17;
            vexxx_printf("%s %08x, %08x => %08x (%08x %08x)\n",
                   name, iargs[i], iargs[j], res, flags, xer);
        }
        vexxx_printf("\n");
    }
    vexxx_printf("\n");
}

static void test_int_one_arg (const unsigned char *name, test_func_t func)
{
    uint32_t res, flags, xer;
    int i;

    if (verbose > 1)
        vexxx_printf( "Test instruction %s\n", name);
    for (i = 0; i < nb_iargs; i++) {
        r14 = iargs[i];
        r18 = 0;
        __asm__ __volatile__ ("mtcr 18");
//        r18 = 0x20000000;                // set xer_ca
        __asm__ __volatile__ ("mtxer 18");
        (*func)();
        res = r17;
        __asm__ __volatile__ ("mfcr 18");
        flags = r18;
        __asm__ __volatile__ ("mfxer 18");
        xer = r18;
        vexxx_printf("%s %08x => %08x (%08x %08x)\n",
               name, iargs[i], res, flags, xer);
    }
    vexxx_printf("\n");
}

static inline void _patch_op_imm (void *out, void *in,
                                  uint16_t imm, int sh, int len)
{
    volatile uint32_t *p, *q;

    p = out;
    q = in;
    *p = (*q & ~(((1 << len) - 1) << sh)) | ((imm & ((1 << len) - 1)) << sh);
}

static inline void patch_op_imm (void *out, void *in,
                                 uint16_t imm, int sh, int len)
{
    volatile uint32_t *p;

    p = out;
    _patch_op_imm(out, in, imm, sh, len);
    __asm__ __volatile__ ("dcbf 0, %0 ; icbi 0, %0 ; isync" ::"r"(p));
}

static inline void patch_op_imm16 (void *out, void *in, uint16_t imm)
{
    patch_op_imm(out, in, imm, 0, 16);
}

static void test_int_one_reg_imm16 (const unsigned char *name,
                                    test_func_t func)
{
    uint32_t func_buf[2], *p;
    uint32_t res, flags, xer;
    int i, j;

    if (verbose > 1)
        vexxx_printf( "Test instruction %s\n", name);
    for (i = 0; i < nb_iargs; i++) {
        for (j = 0; j < nb_ii16; j++) {
            p = (void *)func;
#if 0
            vexxx_printf("copy func %s from %p to %p (%08x %08x)\n",
                   name, func, func_buf, p[0], p[1]);
#endif
            func_buf[1] = p[1];
            patch_op_imm16(func_buf, p, ii16[j]);
            func = (void *)func_buf;
#if 0
            vexxx_printf(" =>  func %s from %p to %p (%08x %08x)\n",
                   name, func, func_buf, func_buf[0], func_buf[1]);
#endif
            r14 = iargs[i];
            r18 = 0;
            __asm__ __volatile__ ("mtcr 18");
            __asm__ __volatile__ ("mtxer 18");
            (*func)();
            __asm__ __volatile__ ("mfcr 18");
            flags = r18;
            __asm__ __volatile__ ("mfxer 18");
            xer = r18;
            res = r17;
            vexxx_printf("%s %08x, %08x => %08x (%08x %08x)\n",
                   name, iargs[i], ii16[j], res, flags, xer);
        }
        vexxx_printf("\n");
    }
    vexxx_printf("\n");
}

/* Special test cases for:
 * rlwimi
 * rlwinm
 * rlwnm
 * srawi
 * mcrf
 * mcrfs
 * mffs
 * mtfsb0
 * mtfsb1
 */

static void rlwi_cb (const unsigned char *name, test_func_t func)
{
    uint32_t func_buf[2], *p;
    uint32_t res, flags, xer;
    int i, j, k, l;

    if (verbose > 1)
        vexxx_printf( "Test instruction %s\n", name);
    for (i = 0;;) {
        if (i >= nb_iargs)
            i = nb_iargs - 1;
        for (j = 0; j < 32; j++) {
            for (k = 0; k < 32; k++) {
                for (l = 0; l < 32; l++) {
                    p = (void *)func;
                    func_buf[1] = p[1];
                    _patch_op_imm(func_buf, p, j, 11, 5);
                    _patch_op_imm(func_buf, p, k, 6, 5);
                    patch_op_imm(func_buf, p, l, 1, 5);
                    func = (void *)func_buf;
                    r14 = iargs[i];
                    r18 = 0;
                    __asm__ __volatile__ ("mtcr 18");
                    __asm__ __volatile__ ("mtxer 18");
                    (*func)();
                    __asm__ __volatile__ ("mfcr 18");
                    flags = r18;
                    __asm__ __volatile__ ("mfxer 18");
                    xer = r18;
                    res = r17;
                    vexxx_printf("%s %08x, %d, %d, %d => %08x (%08x %08x)\n",
                           name, iargs[i], j, k, l, res, flags, xer);
                }
                vexxx_printf("\n");
            }
            vexxx_printf("\n");
        }
        vexxx_printf("\n");
        if (i == 0)
            i = 1;
        else if (i == nb_iargs - 1)
            break;
        else
            i += 3;
    }
    vexxx_printf("\n");
}

static void rlwnm_cb (const unsigned char *name, test_func_t func)
{
    uint32_t func_buf[2], *p;
    uint32_t res, flags, xer;
    int i, j, k, l;

    if (verbose > 1)
        vexxx_printf( "Test instruction %s\n", name);
    for (i = 0; i < nb_iargs; i++) {
        for (j = 0; j < 64; j++) {
            for (k = 0; k < 32; k++) {
                for (l = 0; l < 32; l++) {
                    p = (void *)func;
                    func_buf[1] = p[1];
                    _patch_op_imm(func_buf, p, k, 6, 5);
                    patch_op_imm(func_buf, p, l, 1, 5);
                    func = (void *)func_buf;
                    r14 = iargs[i];
                    r15 = j;
                    r18 = 0;
                    __asm__ __volatile__ ("mtcr 18");
                    __asm__ __volatile__ ("mtxer 18");
                    (*func)();
                    __asm__ __volatile__ ("mfcr 18");
                    flags = r18;
                    __asm__ __volatile__ ("mfxer 18");
                    xer = r18;
                    res = r17;
                    vexxx_printf("%s %08x, %08x, %d, %d => %08x (%08x %08x)\n",
                           name, iargs[i], j, k, l, res, flags, xer);
                }
                vexxx_printf("\n");
            }
            vexxx_printf("\n");
        }
        vexxx_printf("\n");
    }
    vexxx_printf("\n");
}

static void srawi_cb (const unsigned char *name, test_func_t func)
{
    uint32_t func_buf[2], *p;
    uint32_t res, flags, xer;
    int i, j;

    if (verbose > 1)
        vexxx_printf( "Test instruction %s\n", name);
    for (i = 0; i < nb_iargs; i++) {
        for (j = 0; j < 32; j++) {
            p = (void *)func;
            func_buf[1] = p[1];
            patch_op_imm(func_buf, p, j, 11, 5);
            func = (void *)func_buf;
            r14 = iargs[i];
            r18 = 0;
            __asm__ __volatile__ ("mtcr 18");
            __asm__ __volatile__ ("mtxer 18");
            (*func)();
            __asm__ __volatile__ ("mfcr 18");
            flags = r18;
            __asm__ __volatile__ ("mfxer 18");
            xer = r18;
            res = r17;
            vexxx_printf("%s %08x, %d => %08x (%08x %08x)\n",
                   name, iargs[i], j, res, flags, xer);
        }
        vexxx_printf("\n");
    }
    vexxx_printf("\n");
}

typedef struct special_t special_t;
struct special_t {
    const unsigned char *name;
    void (*test_cb)(const unsigned char *name, test_func_t func);
};

static void test_special (special_t *table,
                          const unsigned char *name, test_func_t func)
{
    const unsigned char *tmp;
    int i;

    for (tmp = name; my_isspace(*tmp); tmp++)
        continue;
    for (i = 0; table[i].name != NULL; i++) {
#if 0
        vexxx_printf( "look for handler for '%s' (%s)\n", name,
                table[i].name);
#endif
        if (my_strcmp(table[i].name, tmp) == 0) {
            (*table[i].test_cb)(name, func);
            return;
        }
    }
    vexxx_printf( "ERROR: no test found for op '%s'\n", name);
}

static special_t special_int_ops[] = {
#if 0
    {
        "rlwimi", /* One register + 3 5 bits immediate arguments */
        &rlwi_cb,
    },
    {
        "rlwimi.", /* One register + 3 5 bits immediate arguments */
        &rlwi_cb,
    },
    {
        "rlwinm", /* One register + 3 5 bits immediate arguments */
        &rlwi_cb,
    },
    {
        "rlwinm.", /* One register + 3 5 bits immediate arguments */
        &rlwi_cb,
    },
    {
        "rlwnm",  /* Two registers + 3 5 bits immediate arguments */
        &rlwnm_cb,
    },
    {
        "rlwnm.",  /* Two registers + 3 5 bits immediate arguments */
        &rlwnm_cb,
    },
    {
        "srawi",  /* One register + 1 5 bits immediate arguments */
        &srawi_cb,
    },
    {
        "srawi.",  /* One register + 1 5 bits immediate arguments */
        &srawi_cb,
    },
#endif
#if 0
    {
        "mcrf",  /* 2 3 bits immediate arguments */
        &mcrf_cb,
    },
    {
        "mcrf",  /* 2 3 bits immediate arguments */
        &mcrf_cb,
    },
#endif
    {
        NULL,
        NULL,
    },
};

static void test_int_special (const unsigned char *name, test_func_t func)
{
    test_special(special_int_ops, name, func);
}

static test_loop_t int_loops[] = {
    &test_int_one_arg,
    &test_int_two_args,
    &test_int_three_args,
    &test_int_two_args,
    &test_int_one_reg_imm16,
    &test_int_one_reg_imm16,
    &test_int_special,
};

#if !defined (NO_FLOAT)
static void test_float_three_args (const unsigned char *name, test_func_t func)
{
    double res;
    uint64_t u0, u1, u2, ur;
    uint32_t flags;
    int i, j, k;

    if (verbose > 1)
        vexxx_printf( "Test instruction %s\n", name);
    for (i = 0; i < nb_fargs; i++) {
        for (j = 0; j < nb_fargs; j++) {
            for (k = 0;k < nb_fargs; k++) {
                u0 = *(uint64_t *)(&fargs[i]);
                u1 = *(uint64_t *)(&fargs[j]);
                u2 = *(uint64_t *)(&fargs[k]);
                f14 = fargs[i];
                f15 = fargs[j];
                f16 = fargs[k];
                r18 = 0;
                __asm__ __volatile__ ("mtcr 18");
                __asm__ __volatile__ ("mtxer 18");
                f18 = +0.0;
                __asm__ __volatile__ ("mtfsf 0xFF, 18");
                (*func)();
                __asm__ __volatile__ ("mfcr 18");
                flags = r18;
                res = f17;
                ur = *(uint64_t *)(&res);
                vexxx_printf("%s %016llx, %016llx, %016llx => %016llx (%08x)\n",
                       name, u0, u1, u2, ur, flags);
            }
            vexxx_printf("\n");
        }
        vexxx_printf("\n");
    }
    vexxx_printf("\n");
}

static void test_float_two_args (const unsigned char *name, test_func_t func)
{
    double res;
    uint64_t u0, u1, ur;
    uint32_t flags;
    int i, j;

    if (verbose > 1)
        vexxx_printf( "Test instruction %s\n", name);
    for (i = 0; i < nb_fargs; i++) {
        for (j = 0; j < nb_fargs; j++) {
            u0 = *(uint64_t *)(&fargs[i]);
            u1 = *(uint64_t *)(&fargs[j]);
            f14 = fargs[i];
            f15 = fargs[j];
            r18 = 0;
            __asm__ __volatile__ ("mtcr 18");
            __asm__ __volatile__ ("mtxer 18");
            f18 = +0.0;
            __asm__ __volatile__ ("mtfsf 0xFF, 18");
            (*func)();
            __asm__ __volatile__ ("mfcr 18");
            flags = r18;
            res = f17;
            ur = *(uint64_t *)(&res);
            vexxx_printf("%s %016llx, %016llx => %016llx (%08x)\n",
                   name, u0, u1, ur, flags);
        }
        vexxx_printf("\n");
    }
    vexxx_printf("\n");
}

static void test_float_one_arg (const unsigned char *name, test_func_t func)
{
    double res;
    uint64_t u0, ur;
    uint32_t flags;
    int i;

    if (verbose > 1)
        vexxx_printf( "Test instruction %s\n", name);
    for (i = 0; i < nb_fargs; i++) {
        u0 = *(uint64_t *)(&fargs[i]);
        f14 = fargs[i];
        r18 = 0;
        __asm__ __volatile__ ("mtcr 18");
        __asm__ __volatile__ ("mtxer 18");
        f18 = +0.0;
        __asm__ __volatile__ ("mtfsf 0xFF, 18");
        (*func)();
        __asm__ __volatile__ ("mfcr 18");
        flags = r18;
        res = f17;
        ur = *(uint64_t *)(&res);
        vexxx_printf("%s %016llx => %016llx (%08x)\n", name, u0, ur, flags);
    }
    vexxx_printf("\n");
}

static special_t special_float_ops[] = {
#if 0
    {
        "mffs",   /* One 5 bits immediate argument */
        &mffs_cb,
    },
    {
        "mffs.",   /* One 5 bits immediate argument */
        &mffs_cb,
    },
    {
        "mtfsb0", /* One 5 bits immediate argument */
        &mffs_cb,
    },
    {
        "mtfsb0.", /* One 5 bits immediate argument */
        &mffs_cb,
    },
    {
        "mtfsb1", /* One 5 bits immediate argument */
        &mffs_cb,
    },
    {
        "mtfsb1.", /* One 5 bits immediate argument */
        &mffs_cb,
    },
    {
        "mtfsf",  /* One register + 1 8 bits immediate argument */
        &mtfsf_cb,
    },
    {
        "mtfsf.",  /* One register + 1 8 bits immediate argument */
        &mtfsf_cb,
    },
    {
        "mtfsfi", /* One 5 bits argument + 1 5 bits argument */
        &mtfsfi_cb,
    },
    {
        "mtfsfi.", /* One 5 bits argument + 1 5 bits argument */
        &mtfsfi_cb,
    },
#endif
    {
        NULL,
        NULL,
    },
};

static void test_float_special (const unsigned char *name, test_func_t func)
{
    test_special(special_float_ops, name, func);
}

static test_loop_t float_loops[] = {
    &test_float_one_arg,
    &test_float_two_args,
    &test_float_three_args,
    &test_float_two_args,
    NULL,
    NULL,
    &test_float_special,
};
#endif /* !defined (NO_FLOAT) */


#if defined (HAS_ALTIVEC) /* XXX: TODO */
#endif /* defined (HAS_ALTIVEC) */

#if defined (IS_PPC405)
static void test_ppc405 (const unsigned char *name, test_func_t func)
{
    uint32_t res, flags, xer;
    int i, j, k;

    if (verbose > 1)
        vexxx_printf( "Test instruction %s\n", name);
    for (i = 0; i < nb_iargs; i++) {
        for (j = 0; j < nb_iargs; j++) {
            for (k = 0;k < nb_iargs; k++) {
                r14 = iargs[i];
                r15 = iargs[j];
                 /* Beware: the third argument and the result
                  * are in the same register
                  */
                r17 = iargs[k];
                r18 = 0;
                __asm__ __volatile__ ("mtcr 18");
                __asm__ __volatile__ ("mtxer 18");
                (*func)();
                __asm__ __volatile__ ("mfcr 18");
                flags = r18;
                __asm__ __volatile__ ("mfxer 18");
                xer = r18;
                res = r17;
                vexxx_printf("%s %08x, %08x, %08x => %08x (%08x %08x)\n",
                       name, iargs[i], iargs[j], iargs[k], res, flags, xer);
            }
            vexxx_printf("\n");
        }
        vexxx_printf("\n");
    }
    vexxx_printf("\n");
}
#endif /* defined (IS_PPC405) */

static int check_filter (unsigned char *filter)
{
    unsigned char *c;
    int ret = 1;

    if (filter != NULL) {
        c = my_strchr(filter, '*');
        if (c != NULL) {
            *c = '\0';
            ret = 0;
        }
    }

    return ret;
}

static int check_name (const unsigned char *name, const unsigned char *filter,
                       int exact)
{
    int nlen, flen;
    int ret = 0;

    if (filter != NULL) {
        for (; my_isspace(*name); name++)
            continue;
        FDPRINTF("Check '%s' againt '%s' (%s match)\n",
                 name, filter, exact ? "exact" : "starting");
        nlen = vexxx_strlen(name);
        flen = vexxx_strlen(filter);
        if (exact) {
            if (nlen == flen && my_memcmp(name, filter, flen) == 0)
                ret = 1;
        } else {
            if (flen <= nlen && my_memcmp(name, filter, flen) == 0)
                ret = 1;
        }
    } else {
        ret = 1;
    }

    return ret;
}

static void do_tests (int one_arg, int two_args, int three_args,
                      int arith, int logical, int compare,
                      int integer, int floats, int p405,
                      int altivec, int faltivec,
                      int cr, unsigned char *filter)
{
#if defined (IS_PPC405)
    test_loop_t tmpl;
#endif
    test_loop_t *loop;
    test_t *tests;
    int nb_args, type, family;
    int i, j, n;
    int exact;

    exact = check_filter(filter);
    n = 0;
    for (i = 0; all_tests[i].name != NULL; i++) {
        nb_args = all_tests[i].flags & PPC_NB_ARGS;
        /* Check number of arguments */
        if ((nb_args == 1 && !one_arg) ||
            (nb_args == 2 && !two_args) ||
            (nb_args == 3 && !three_args))
            continue;
        /* Check instruction type */
        type = all_tests[i].flags & PPC_TYPE;
        if ((type == PPC_ARITH && !arith) ||
            (type == PPC_LOGICAL && !logical) ||
            (type == PPC_COMPARE && !compare))
            continue;
        /* Check instruction family */
        family = all_tests[i].flags & PPC_FAMILY;
        if ((family == PPC_INTEGER && !integer) ||
            (family == PPC_FLOAT && !floats) ||
            (family == PPC_405 && !p405) ||
            (family == PPC_ALTIVEC && !altivec) ||
            (family == PPC_FALTIVEC && !faltivec))
            continue;
        /* Check flags update */
        if (((all_tests[i].flags & PPC_CR) && cr == 0) ||
            (!(all_tests[i].flags & PPC_CR) && cr == 1))
            continue;
        /* All passed, do the tests */
        tests = all_tests[i].tests;
        /* Select the test loop */
        switch (family) {
        case PPC_INTEGER:
            loop = &int_loops[nb_args - 1];
            break;
        case PPC_FLOAT:
#if !defined (NO_FLOAT)
            loop = &float_loops[nb_args - 1];
            break;
#else
            vexxx_printf( "Sorry. "
                    "PPC floating point instructions tests "
                    "are disabled on your host\n");
#endif /* !defined (NO_FLOAT) */

        case PPC_405:
#if defined (IS_PPC405)
            tmpl = &test_ppc405;
            loop = &tmpl;
            break;
#else
            vexxx_printf( "Sorry. "
                    "PPC405 instructions tests are disabled on your host\n");
            continue;
#endif /* defined (IS_PPC405) */
        case PPC_ALTIVEC:
#if defined (HAS_ALTIVEC)
#if 0
            loop = &altivec_int_loops[nb_args - 1];
            break;
#else
            vexxx_printf( "Sorry. "
                    "Altivec instructions tests are not yet implemented\n");
            continue;
#endif
#else
            vexxx_printf( "Sorry. "
                    "Altivec instructions tests are disabled on your host\n");
            continue;
#endif
        case PPC_FALTIVEC:
#if defined (HAS_ALTIVEC)
#if 0
            loop = &altivec_float_loops[nb_args - 1];
            break;
#else
            vexxx_printf( "Sorry. "
                    "Altivec instructions tests are not yet implemented\n");
            continue;
#endif
#else
            vexxx_printf( "Sorry. "
                    "Altivec float instructions tests "
                    "are disabled on your host\n");
#endif
            continue;
        default:
            vexxx_printf("ERROR: unknown insn family %08x\n", family);
            continue;
        }
        if (verbose > 0)
            vexxx_printf( "%s:\n", all_tests[i].name);
        for (j = 0; tests[j].name != NULL; j++) {
            if (check_name(tests[j].name, filter, exact))
                (*loop)(tests[j].name, tests[j].func);
            n++;
        }
        vexxx_printf("\n");
    }
    vexxx_printf( "All done. Tested %d different instructions\n", n);
}

#if 0 // unused
static void usage (void)
{
    vexxx_printf(
            "test-ppc [-1] [-2] [-3] [-*] [-t <type>] [-f <family>] [-u] "
            "[-n <filter>] [-x] [-h]\n"
            "\t-1: test opcodes with one argument\n"
            "\t-2: test opcodes with two arguments\n"
            "\t-3: test opcodes with three arguments\n"
            "\t-*: launch test without checking the number of arguments\n"
            "\t-t: launch test for instructions of type <type>\n"
            "\t    recognized types:\n"
            "\t\tarith (or a)\n"
            "\t\tlogical (or l)\n"
            "\t\tcompare (or c)\n"
            "\t-f: launch test for instructions of family <family>\n"
            "\t    recognized families:\n"
            "\t\tinteger (or i)\n"
            "\t\tfloat (or f)\n"
            "\t\tppc405 (or mac)\n"
            "\t\taltivec (or a)\n"
            "\t-u: test instructions that update flags\n"
            "\t-n: filter instructions with <filter>\n"
            "\t    <filter> can be in two forms:\n"
            "\t\tname  : filter functions that exactly match <name>\n"
            "\t\tname* : filter functions that start with <name>\n"
            "\t-h: print this help\n"
            );
}
#endif

int _main (int argc, char **argv)
{
    unsigned char /* *tmp, */ *filter = NULL;
    int one_arg = 0, two_args = 0, three_args = 0;
    int arith = 0, logical = 0, compare = 0;
    int integer = 0, floats = 0, p405 = 0, altivec = 0, faltivec = 0;
    int cr = -1;
    //int c;
    
    //    while ((c = getopt(argc, argv, "123t:f:n:uvh")) != -1) {
    //        switch (c) {
    //        case '1':
    //            one_arg = 1;
    //            break;
    //        case '2':
    //            two_args = 1;
    //            break;
    //        case '3':
    //            three_args = 1;
    //            break;
    //        case 't':
    //            tmp = optarg;
    //            if (my_strcmp(tmp, "arith") == 0 || my_strcmp(tmp, "a") == 0) {
    //                arith = 1;
    //            } else if (my_strcmp(tmp, "logical") == 0 || my_strcmp(tmp, "l") == 0) {
    //                logical = 1;
    //            } else if (my_strcmp(tmp, "compare") == 0 || my_strcmp(tmp, "c") == 0) {
    //                compare = 1;
    //            } else {
    //                goto bad_arg;
    //            }
    //            break;
    //        case 'f':
    //            tmp = optarg;
    //            if (my_strcmp(tmp, "integer") == 0 || my_strcmp(tmp, "i") == 0) {
    //                integer = 1;
    //            } else if (my_strcmp(tmp, "float") == 0 || my_strcmp(tmp, "f") == 0) {
    //                floats = 1;
    //            } else if (my_strcmp(tmp, "ppc405") == 0 || my_strcmp(tmp, "mac") == 0) {
    //                p405 = 1;
    //            } else if (my_strcmp(tmp, "altivec") == 0 || my_strcmp(tmp, "a") == 0) {
    //                altivec = 1;
    //                faltivec = 1;
    //            } else {
    //                goto bad_arg;
    //            }
    //            break;
    //        case 'n':
    //            filter = optarg;
    //            break;
    //        case 'u':
    //            cr = 1;
    //            break;
    //        case 'h':
    //            usage();
    //            return 0;
    //        case 'v':
    //            verbose++;
    //            break;
    //        default:
    //            usage();
    //            vexxx_printf( "Unknown argument: '%c'\n", c);
    //            return 1;
    //        bad_arg:
    //            usage();
    //            vexxx_printf( "Bad argument for '%c': '%s'\n", c, tmp);
    //            return 1;
    //        }
    //    }
    //    if (argc != optind) {
    //        usage();
    //        vexxx_printf( "Bad number of arguments\n");
    //        return 1;
    //    }

    if (one_arg == 0 && two_args == 0 && three_args == 0) {
        one_arg = 1;
        two_args = 1;
        three_args = 1;
    }
    if (arith == 0 && logical == 0 && compare == 0) {
        arith = 1;
        logical = 1;
        compare = 1;
    }
    if (integer == 0 && floats == 0 && altivec == 0 && faltivec == 0 &&
        p405 == 0) {
        integer = 1;
        floats = 1;
        altivec = 1;
        faltivec = 1;
        p405 = 1;
    }
    if (cr == -1)
        cr = 2;
    build_iargs_table();
    build_fargs_table();
    build_ii16_table();

#if 1
    one_arg=1; 
    two_args=1; 
    three_args=1;

    arith=1;
    logical=1;
    compare=1;

    integer=1;
    floats=0;

    p405=0;
    altivec=0;
    faltivec=0;
#endif

    do_tests(one_arg, two_args, three_args,
             arith, logical, compare,
             integer, floats, p405, altivec, faltivec,
             cr, filter);

    return 0;
}


void entry ( HWord(*service)(HWord,HWord) )
{
   char* argv[2] = { NULL, NULL };
   serviceFn = service;
   _main(0, argv);
   (*service)(0,0);
}
