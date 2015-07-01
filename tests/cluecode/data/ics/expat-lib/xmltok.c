/* Copyright (c) 1998, 1999 Thai Open Source Software Center Ltd
   See the file COPYING for copying permission.
*/
static int FASTCALL
isSpace(int c)
{
  switch (c) {
  case 0x20:
  case 0xD:
      *nameEndPtr = ptr;
      break;
    }
    if (isSpace(c)) {
      *nameEndPtr = ptr;
      do {
  }
  ptr += enc->minBytesPerChar;
  c = toAscii(enc, ptr, end);
  while (isSpace(c)) {
    ptr += enc->minBytesPerChar;
    c = toAscii(enc, ptr, end);
{
  const struct unknown_encoding *uenc = AS_UNKNOWN_ENCODING(enc);
  int c = uenc->convert(uenc->userData, p);
  return (c & ~0xFFFF) || checkCharRefNumber(c) < 0;
}

      e->utf8[i][1] = (char)c;
      e->utf16[i] = (unsigned short)(c == 0 ? 0xFFFF : c);
    }
    else if (checkCharRefNumber(c) < 0) {
      e->normal.type[i] = BT_NONXML;
      /* This shouldn't really get used. */