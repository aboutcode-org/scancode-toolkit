// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
/**
 * Returns true if a character is a ASCII character.
 */
function isAscii(c) {
  var charCode = c.charCodeAt(0);
  return 0x00 <= charCode && charCode <= 0x7F;