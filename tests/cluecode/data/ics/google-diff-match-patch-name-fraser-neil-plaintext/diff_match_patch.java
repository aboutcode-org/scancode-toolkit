/*
 * Diff Match and Patch
 *
 * Copyright 2006 Google Inc.
 * http://code.google.com/p/google-diff-match-patch/
 *
    }
    int i = 0;
    for (char c : char_pattern) {
      s.put(c, s.get(c) | (1 << (pattern.length() - i - 1)));
      i++;
    }