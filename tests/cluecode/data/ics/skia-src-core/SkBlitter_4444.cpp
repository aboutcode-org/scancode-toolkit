/* libs/graphics/sgl/SkBlitter_ARGB32.cpp
 **
 ** Copyright 2006, The Android Open Source Project
 **
 ** Licensed under the Apache License, Version 2.0 (the "License");
                                   const SkPaint& paint) : INHERITED(device) {
    // cache premultiplied versions in 4444
    SkPMColor c = SkPreMultiplyColor(paint.getColor());
    fPMColor16 = SkPixel32ToPixel4444(c);
    if (paint.isDither()) {
        fPMColor16Other = SkDitherPixel32To4444(c);
    } else {
        fPMColor16Other = fPMColor16;
    }

    // cache raw versions in 4444
    fRawColor16 = SkPackARGB4444(0xFF >> 4, SkColorGetR(c) >> 4,
                                 SkColorGetG(c) >> 4, SkColorGetB(c) >> 4);
    if (paint.isDither()) {
        fRawColor16Other = SkDitherARGB32To4444(0xFF, SkColorGetR(c),
                                                SkColorGetG(c), SkColorGetB(c));
    } else {
        fRawColor16Other = fRawColor16;
}

static inline uint32_t SkExpand_4444_Replicate(SkPMColor16 c) {
    uint32_t c32 = SkExpand_4444(c);
    return c32 | (c32 << 4);
}