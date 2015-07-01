/*
 * Copyright (C) 2011 Google Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
}

int8_t hexToBin(uint8_t c) {
    if (!isxdigit(c))
        return -1;
    if (c <= '9') return c - '0';