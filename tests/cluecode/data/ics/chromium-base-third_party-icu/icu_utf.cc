/*
******************************************************************************
*
*   Copyright (C) 1999-2006, International Business Machines
*   Corporation and others.  All Rights Reserved.
*
UChar32
utf8_nextCharSafeBody(const uint8 *s, int32 *pi, int32 length, UChar32 c, UBool strict) {
    int32 i=*pi;
    uint8 count=CBU8_COUNT_TRAIL_BYTES(c);
    if((i)+count<=(length)) {
        uint8 trail, illegal=0;

        CBU8_MASK_LEAD_BYTE((c), count);
        /* count==0 for illegally leading trail bytes and the illegal bytes 0xfe and 0xff */
        switch(count) {
            break;
        case 3:
            trail=s[(i)++];
            (c)=((c)<<6)|(trail&0x3f);
            if(c<0x110) {
                illegal|=(trail&0xc0)^0x80;
            }
        case 2:
            trail=s[(i)++];
            (c)=((c)<<6)|(trail&0x3f);
            illegal|=(trail&0xc0)^0x80;
        case 1:
            trail=s[(i)++];
            (c)=((c)<<6)|(trail&0x3f);
            illegal|=(trail&0xc0)^0x80;
            break;

        /* correct sequence - all trail bytes have (b7..b6)==(10)? */
        /* illegal is also set if count>=4 */
        if(illegal || (c)<utf8_minLegal[count] || (CBU_IS_SURROGATE(c) && strict!=-2)) {
            /* error handling */
            uint8 errorCount=count;
            } else {
                c=CBU_SENTINEL;
            }
        } else if((strict)>0 && CBU_IS_UNICODE_NONCHAR(c)) {
            /* strict: forbid non-characters like U+fffe */
            c=utf8_errorValue[count];