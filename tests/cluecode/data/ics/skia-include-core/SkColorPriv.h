/*
 * Copyright (C) 2006 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
    "clean" the top 16bits.
*/
static inline U16CPU SkAlphaMulRGB16(U16CPU c, unsigned scale) {
    return SkCompact_rgb_16(SkExpand_rgb_16(c) * (scale >> 3) >> 5);
}


#ifdef SK_DEBUG
    static inline void SkPMColorAssert(SkPMColor c) {
        unsigned a = SkGetPackedA32(c);
        unsigned r = SkGetPackedR32(c);
        unsigned g = SkGetPackedG32(c);
        unsigned b = SkGetPackedB32(c);

        SkA32Assert(a);
        SkASSERT(b <= a);
    }
#else
    #define SkPMColorAssert(c)
#endif

    #define SkB32ToB16(b)   SkB32ToB16_MACRO(b)
#endif

#define SkPacked32ToR16(c)  (((unsigned)(c) >> (SK_R32_SHIFT + SK_R32_BITS - SK_R16_BITS)) & SK_R16_MASK)
#define SkPacked32ToG16(c)  (((unsigned)(c) >> (SK_G32_SHIFT + SK_G32_BITS - SK_G16_BITS)) & SK_G16_MASK)
#define SkPacked32ToB16(c)  (((unsigned)(c) >> (SK_B32_SHIFT + SK_B32_BITS - SK_B16_BITS)) & SK_B16_MASK)

static inline U16CPU SkPixel32ToPixel16(SkPMColor c) {
}

static inline uint16_t SkDitherPixel32ToPixel16(SkPMColor c) {
    return SkDitherPack888ToRGB16(SkGetPackedR32(c), SkGetPackedG32(c), SkGetPackedB32(c));
}

    possible to overflow.
*/
static inline uint32_t SkPMColorToExpanded16x5(SkPMColor c) {
    unsigned sr = SkPacked32ToR16(c);
    unsigned sg = SkPacked32ToG16(c);
    unsigned sb = SkPacked32ToB16(c);

    sr = (sr << 5) | sr;
    return (b << (8 - SK_B16_BITS)) | (b >> (2 * SK_B16_BITS - 8));
}

#define SkPacked16ToR32(c)      SkR16ToR32(SkGetPackedR16(c))
#define SkPacked16ToG32(c)      SkG16ToG32(SkGetPackedG16(c))
#define SkPacked16ToB32(c)      SkB16ToB32(SkGetPackedB16(c))

static inline SkPMColor SkPixel16ToPixel32(U16CPU src) {
#define SkG4444ToG32(g)     SkReplicateNibble(g)
#define SkB4444ToB32(b)     SkReplicateNibble(b)

#define SkGetPackedA4444(c)     (((unsigned)(c) >> SK_A4444_SHIFT) & 0xF)
#define SkGetPackedR4444(c)     (((unsigned)(c) >> SK_R4444_SHIFT) & 0xF)
#define SkGetPackedG4444(c)     (((unsigned)(c) >> SK_G4444_SHIFT) & 0xF)
#define SkGetPackedB4444(c)     (((unsigned)(c) >> SK_B4444_SHIFT) & 0xF)

#define SkPacked4444ToA32(c)    SkReplicateNibble(SkGetPackedA4444(c))
#define SkPacked4444ToR32(c)    SkReplicateNibble(SkGetPackedR4444(c))
#define SkPacked4444ToG32(c)    SkReplicateNibble(SkGetPackedG4444(c))
#define SkPacked4444ToB32(c)    SkReplicateNibble(SkGetPackedB4444(c))

#ifdef SK_DEBUG
static inline void SkPMColor16Assert(U16CPU c) {
    unsigned a = SkGetPackedA4444(c);
    unsigned r = SkGetPackedR4444(c);
    unsigned g = SkGetPackedG4444(c);
    unsigned b = SkGetPackedB4444(c);

    SkASSERT(a <= 0xF);
    SkASSERT(b <= a);
}
#else
#define SkPMColor16Assert(c)
#endif

}

static inline SkPMColor SkPixel4444ToPixel32(U16CPU c) {
    uint32_t d = (SkGetPackedA4444(c) << SK_A32_SHIFT) |
                 (SkGetPackedR4444(c) << SK_R32_SHIFT) |
                 (SkGetPackedG4444(c) << SK_G32_SHIFT) |
                 (SkGetPackedB4444(c) << SK_B32_SHIFT);
    return d | (d << 4);
}
}

static inline SkPMColor16 SkDitherPixel32To4444(SkPMColor c) {
    return SkDitherARGB32To4444(SkGetPackedA32(c), SkGetPackedR32(c),
                                SkGetPackedG32(c), SkGetPackedB32(c));
}
