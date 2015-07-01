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
_STLP_TEMPLATE_NULL
struct _WCharIndexT<true> {
  static bool in_range(wchar_t c, size_t upperBound) {
    return c >= 0 && size_t(c) < upperBound;
  }
};
_STLP_TEMPLATE_NULL
struct _WCharIndexT<false> {
  static bool in_range(wchar_t c, size_t upperBound) {
    return size_t(c) < upperBound;
  }
};