/*
 * libjingle
 * Copyright 2004--2007, Google Inc.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 *  1. Redistributions of source code must retain the above copyright notice,
 *     this list of conditions and the following disclaimer.
 *  2. Redistributions in binary form must reproduce the above copyright notice,
 *     this list of conditions and the following disclaimer in the documentation
 *     and/or other materials provided with the distribution.
  }

  VideoEncoderConfig(const VideoCodec& c)
      : max_codec(c),
        num_threads(kDefaultMaxThreads),
        cpu_profile(kDefaultCpuProfile) {
  }

  VideoEncoderConfig(const VideoCodec& c, int t, int p)
      : max_codec(c),
        num_threads(t),
        cpu_profile(p) {