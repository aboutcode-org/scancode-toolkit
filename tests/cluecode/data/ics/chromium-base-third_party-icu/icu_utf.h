/*
*******************************************************************************
*
*   Copyright (C) 1999-2004, International Business Machines
*   Corporation and others.  All Rights Reserved.
*
 * @return TRUE or FALSE
 * @stable ICU 2.4
 */
#define CBU_IS_UNICODE_NONCHAR(c) \
    ((c)>=0xfdd0 && \
     ((uint32)(c)<=0xfdef || ((c)&0xfffe)==0xfffe) && \
     (uint32)(c)<=0x10ffff)

/**
 * @return TRUE or FALSE
 * @stable ICU 2.4
 */
#define CBU_IS_UNICODE_CHAR(c) \
    ((uint32)(c)<0xd800 || \
        ((uint32)(c)>0xdfff && \
         (uint32)(c)<=0x10ffff && \
         !CBU_IS_UNICODE_NONCHAR(c)))

/**
 * @return TRUE or FALSE
 * @stable ICU 2.4
 */
#define CBU_IS_SURROGATE(c) (((c)&0xfffff800)==0xd800)

/**
 * Assuming c is a surrogate code point (U_IS_SURROGATE(c)),
 * is it a lead surrogate?
 * @param c 32-bit code point
 * @return TRUE or FALSE
 * @stable ICU 2.4
 */
#define CBU_IS_SURROGATE_LEAD(c) (((c)&0x400)==0)


 * @return TRUE or FALSE
 * @stable ICU 2.4
 */
#define CBU8_IS_SINGLE(c) (((c)&0x80)==0)

/**
 * @return TRUE or FALSE
 * @stable ICU 2.4
 */
#define CBU8_IS_LEAD(c) ((uint8)((c)-0xc0)<0x3e)

/**
 * @return TRUE or FALSE
 * @stable ICU 2.4
 */
#define CBU8_IS_TRAIL(c) (((c)&0xc0)==0x80)

/**
 * @return 1..4, or 0 if c is a surrogate or not a Unicode code point
 * @stable ICU 2.4
 */
#define CBU8_LENGTH(c) \
    ((uint32)(c)<=0x7f ? 1 : \
        ((uint32)(c)<=0x7ff ? 2 : \
            ((uint32)(c)<=0xd7ff ? 3 : \
                ((uint32)(c)<=0xdfff || (uint32)(c)>0x10ffff ? 0 : \
                    ((uint32)(c)<=0xffff ? 3 : 4)\
                ) \
            ) \
 * @stable ICU 2.4
 */
#define CBU8_NEXT(s, i, length, c) { \
    (c)=(s)[(i)++]; \
    if(((uint8)(c))>=0x80) { \
        if(CBU8_IS_LEAD(c)) { \
            (c)=base_icu::utf8_nextCharSafeBody((const uint8 *)s, &(i), (int32)(length), c, -1); \
        } else { \
            (c)=CBU_SENTINEL; \
        } \
    } \
 * @stable ICU 2.4
 */
#define CBU8_APPEND_UNSAFE(s, i, c) { \
    if((uint32)(c)<=0x7f) { \
        (s)[(i)++]=(uint8)(c); \
    } else { \
        if((uint32)(c)<=0x7ff) { \
            (s)[(i)++]=(uint8)(((c)>>6)|0xc0); \
        } else { \
            if((uint32)(c)<=0xffff) { \
                (s)[(i)++]=(uint8)(((c)>>12)|0xe0); \
            } else { \
                (s)[(i)++]=(uint8)(((c)>>18)|0xf0); \
                (s)[(i)++]=(uint8)((((c)>>12)&0x3f)|0x80); \
            } \
            (s)[(i)++]=(uint8)((((c)>>6)&0x3f)|0x80); \
        } \
        (s)[(i)++]=(uint8)(((c)&0x3f)|0x80); \
    } \
}
 * @return TRUE or FALSE
 * @stable ICU 2.4
 */
#define CBU16_IS_SINGLE(c) !CBU_IS_SURROGATE(c)

/**
 * @return TRUE or FALSE
 * @stable ICU 2.4
 */
#define CBU16_IS_LEAD(c) (((c)&0xfffffc00)==0xd800)

/**
 * @return TRUE or FALSE
 * @stable ICU 2.4
 */
#define CBU16_IS_TRAIL(c) (((c)&0xfffffc00)==0xdc00)

/**
 * @return TRUE or FALSE
 * @stable ICU 2.4
 */
#define CBU16_IS_SURROGATE(c) CBU_IS_SURROGATE(c)

/**
 * Assuming c is a surrogate code point (U16_IS_SURROGATE(c)),
 * is it a lead surrogate?
 * @param c 16-bit code unit
 * @return TRUE or FALSE
 * @stable ICU 2.4
 */
#define CBU16_IS_SURROGATE_LEAD(c) (((c)&0x400)==0)

/**
 * @return 1 or 2
 * @stable ICU 2.4
 */
#define CBU16_LENGTH(c) ((uint32)(c)<=0xffff ? 1 : 2)

/**
 * @stable ICU 2.4
 */
#define CBU16_NEXT(s, i, length, c) { \
    (c)=(s)[(i)++]; \
    if(CBU16_IS_LEAD(c)) { \
        uint16 __c2; \
        if((i)<(length) && CBU16_IS_TRAIL(__c2=(s)[(i)])) { \
            ++(i); \
            (c)=CBU16_GET_SUPPLEMENTARY((c), __c2); \
        } \
    } \
 * @stable ICU 2.4
 */
#define CBU16_APPEND_UNSAFE(s, i, c) { \
    if((uint32)(c)<=0xffff) { \
        (s)[(i)++]=(uint16)(c); \
    } else { \
        (s)[(i)++]=(uint16)(((c)>>10)+0xd7c0); \
        (s)[(i)++]=(uint16)(((c)&0x3ff)|0xdc00); \
    } \
}