#!/usr/bin/python
# Copyright (c) 2009 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import string

HEADER = """\
// Copyright (c) 2009 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
// arguments (like Callback) - hence the name. :-)
//
// DispatchToMethod/Function supports two sets of arguments: pre-bound (P) and
// call-time (C). The arguments as well as the return type are templatized.
// DispatchToMethod/Function will also try to call the selected method or
// function even if provided pre-bound arguments does not match exactly with