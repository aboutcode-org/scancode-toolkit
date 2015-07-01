//*********************************************************************
//* Base64 - a simple base64 encoder and decoder.
//*
//*     Copyright (c) 1999, Bob Withers - bwit@pobox.com
//*
//* This code may be freely used for any purpose, either personal
//* or commercial, provided the authors copyright notice remains
//* intact.
//*
                                 data, len, &dpos, qbuf, &padded);
    c = (qbuf[0] << 2) | ((qbuf[1] >> 4) & 0x3);
    if (qlen >= 2) {
      result->push_back(c);
      c = ((qbuf[1] << 4) & 0xf0) | ((qbuf[2] >> 2) & 0xf);
      if (qlen >= 3) {
        result->push_back(c);
        c = ((qbuf[2] << 6) & 0xc0) | qbuf[3];
        if (qlen >= 4) {
          result->push_back(c);
          c = 0;
        }