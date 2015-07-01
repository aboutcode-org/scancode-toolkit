/*
 * Copyright (c) 1999
 * Silicon Graphics Computer Systems, Inc.
 *
 * Copyright (c) 1999
 * Boris Fomitchev
 *
 * without fee, provided the above notices are retained on all copies.
 * Permission to modify the code and to distribute modified code is granted,
 * provided the above notices are retained, and a notice that the code was
 * modified is included with the above copyright notice.
 *
 */
  char c;
  /* We might never reach 128 when char is signed. */
  for (c = 0; /* c != 128 */; ++c) {
    if (isalpha(c)) ctable[(unsigned char)c] |= _Locale_ALPHA;
    if (iscntrl(c)) ctable[(unsigned char)c] |= _Locale_CNTRL;
    if (isdigit(c)) ctable[(unsigned char)c] |= _Locale_DIGIT;
    if (isprint(c)) ctable[(unsigned char)c] |= _Locale_PRINT;
    if (ispunct(c)) ctable[(unsigned char)c] |= _Locale_PUNCT;
    if (isspace(c)) ctable[(unsigned char)c] |= _Locale_SPACE;
    if (isxdigit(c)) ctable[(unsigned char)c] |= _Locale_XDIGIT;
    if (isupper(c)) ctable[(unsigned char)c] |= _Locale_UPPER;
    if (islower(c)) ctable[(unsigned char)c] |= _Locale_LOWER;
    if (c == 127) break;
  }
}

int _Locale_toupper(struct _Locale_ctype*lctype, int c)
{ return toupper(c); }

int _Locale_tolower(struct _Locale_ctype*lctype, int c)
{ return tolower(c); }

#ifndef _STLP_NO_WCHAR_T