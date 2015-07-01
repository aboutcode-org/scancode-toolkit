/*
 * Copyright (C) 2006 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
    #define SkScalarMul(a, b)       ((float)(a) * (b))
    /** Returns the product of two SkScalars plus a third SkScalar
    */
    #define SkScalarMulAdd(a, b, c) ((float)(a) * (b) + (c))
    /** Returns the product of a SkScalar and an int rounded to the nearest integer value
    */
    #define SkScalarMod(x,y)        sk_float_mod(x,y)
    /** Returns the product of the first two arguments, divided by the third argument
    */
    #define SkScalarMulDiv(a, b, c) ((float)(a) * (b) / (c))
    /** Returns the multiplicative inverse of the SkScalar (1/x)
    */