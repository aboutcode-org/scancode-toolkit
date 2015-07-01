/*
 * Copyright (C) 2006 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
     not at least 1-byte per pixel, return 0, including for kNo_Config.
     */
    static int ComputeShiftPerPixel(Config c) {
        return ComputeBytesPerPixel(c) >> 1;
    }

        to be 0xFF. If the config is kA8_Config, then only the color's alpha value is used.
    */
    void eraseColor(SkColor c) const {
        this->eraseARGB(SkColorGetA(c), SkColorGetR(c), SkColorGetG(c),
                        SkColorGetB(c));
    }
