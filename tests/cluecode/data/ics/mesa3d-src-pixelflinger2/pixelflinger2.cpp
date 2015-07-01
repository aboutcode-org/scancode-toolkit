/**
 **
 ** Copyright 2010, The Android Open Source Project
 **
 ** Licensed under the Apache License, Version 2.0 (the "License");

static inline GGLBlendState::GGLBlendFactor GLBlendFactor(const GLenum factor)
{
#define SWITCH_LINE(c) case c: return GGLBlendState::G##c;
   switch (factor)
   {