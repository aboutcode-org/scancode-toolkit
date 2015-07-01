/*
 * Copyright (C) 2006-2008 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
    Sk64 rowBytes;
    rowBytes.setZero();

    switch (c) {
        case kNo_Config:
        case kRLE_Index8_Config:
        }
    }

    fConfig     = SkToU8(c);
    fWidth      = width;
    fHeight     = height;
    fRowBytes   = rowBytes;

    fBytesPerPixel = (uint8_t)ComputeBytesPerPixel(c);

    SkDEBUGCODE(this->validate();)
        }
        case SkBitmap::kIndex8_Config: {
            SkPMColor c = this->getIndex8Color(x, y);
            return SkUnPreMultiply::PMColorToColor(c);
        }
        case SkBitmap::kRGB_565_Config: {
        case SkBitmap::kARGB_4444_Config: {
            uint16_t* addr = this->getAddr16(x, y);
            SkPMColor c = SkPixel4444ToPixel32(addr[0]);
            return SkUnPreMultiply::PMColorToColor(c);
        }
        case SkBitmap::kARGB_8888_Config: {