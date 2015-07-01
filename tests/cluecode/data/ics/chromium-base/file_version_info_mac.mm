// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
  return string16();
}

string16 FileVersionInfoMac::legal_copyright() {
  return GetString16Value(CFSTR("CFBundleGetInfoString"));
}