// Copyright 2011 Google Inc.
//
// This code is licensed under the same terms as WebM:
//-----------------------------------------------------------------------------
// luma 4x4 prediction

#define AVG3(a, b, c) (((a) + 2 * (b) + (c) + 2) >> 2)
#define AVG2(a, b) (((a) + (b) + 1) >> 1)
