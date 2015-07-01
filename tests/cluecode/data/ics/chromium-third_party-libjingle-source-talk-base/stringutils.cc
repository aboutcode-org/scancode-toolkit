/*
 * libjingle
 * Copyright 2004--2005, Google Inc.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 *  1. Redistributions of source code must retain the above copyright notice,
 *     this list of conditions and the following disclaimer.
 *  2. Redistributions in binary form must reproduce the above copyright notice,
 *     this list of conditions and the following disclaimer in the documentation
 *     and/or other materials provided with the distribution.

bool memory_check(const void* memory, int c, size_t count) {
  const char* char_memory = static_cast<const char*>(memory);
  char char_c = static_cast<char>(c);
  for (size_t i = 0; i < count; ++i) {
    if (char_memory[i] != char_c) {