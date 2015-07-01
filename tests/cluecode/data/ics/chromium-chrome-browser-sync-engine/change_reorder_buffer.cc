// Copyright (c) 2006-2009 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
  // Step 1: Iterate through the operations, doing three things:
  // (a) Push deleted items straight into the |changelist|.
  // (b) Construct a traversal spanning all non-deleted items.
  // (c) Construct a set of all parent nodes of any position changes.
  set<int64> parents_of_position_changes;
  Traversal traversal;