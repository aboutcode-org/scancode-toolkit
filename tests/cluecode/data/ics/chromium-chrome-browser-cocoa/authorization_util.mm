// Copyright (c) 2009 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
                             kAuthorizationFlagExtendRights |
                             kAuthorizationFlagPreAuthorize;

  status = AuthorizationCopyRights(authorization,
                                   &rights,
                                   &environment,
                                   NULL);
  if (status != errAuthorizationSuccess) {
    if (status != errAuthorizationCanceled) {
      LOG(ERROR) << "AuthorizationCopyRights: " << status;
    }
    return NULL;