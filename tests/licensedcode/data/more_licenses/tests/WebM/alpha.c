// Copyright 2011 Google Inc.
//
// This code is licensed under the same terms as WebM:
//  Software License Agreement:  http://www.webmproject.org/license/software/
//  Additional IP Rights Grant:  http://www.webmproject.org/license/additional/
// -----------------------------------------------------------------------------
//
// Alpha-plane compression.
//
// Author: Skal (pascal.massimino@gmail.com)

#include <assert.h>
#include <stdlib.h>
#include "vp8enci.h"

#ifdef WEBP_EXPERIMENTAL_FEATURES
#include "zlib.h"
#endif

#if defined(__cplusplus) || defined(c_plusplus)
extern "C" {
#endif

#ifdef WEBP_EXPERIMENTAL_FEATURES

#define CHUNK_SIZE 8192

//-----------------------------------------------------------------------------

static int CompressAlpha(const uint8_t* data, size_t data_size,
                         uint8_t** output, size_t* output_size,
                         int algo) {
  int ret = Z_OK;
  z_stream strm;
  unsigned char chunk[CHUNK_SIZE];

  *output = NULL;
  *output_size = 0;
  memset(&strm, 0, sizeof(strm));
  if (deflateInit(&strm, algo ? Z_BEST_SPEED : Z_BEST_COMPRESSION) != Z_OK) {
    return 0;
  }
  strm.next_in = (unsigned char*)data;
  strm.avail_in = data_size;
  do {
    size_t size_out;

    strm.next_out = chunk;
    strm.avail_out = CHUNK_SIZE;
    ret = deflate(&strm, Z_FINISH);
    if (ret == Z_STREAM_ERROR) {
      break;
    }
    size_out = CHUNK_SIZE - strm.avail_out;
    if (size_out) {
      size_t new_size = *output_size + size_out;
      uint8_t* new_output = realloc(*output, new_size);
      if (new_output == NULL) {
        ret = Z_MEM_ERROR;
        break;
      }
      memcpy(new_output + *output_size, chunk, size_out);
      *output_size = new_size;
      *output = new_output;
    }
  } while (ret != Z_STREAM_END || strm.avail_out == 0);

  deflateEnd(&strm);
  if (ret != Z_STREAM_END) {
    free(*output);
    output_size = 0;
    return 0;
  }
  return 1;
}

#endif    /* WEBP_EXPERIMENTAL_FEATURES */

void VP8EncInitAlpha(VP8Encoder* enc) {
  enc->has_alpha_ = (enc->pic_->a != NULL);
  enc->alpha_data_ = NULL;
  enc->alpha_data_size_ = 0;
}

void VP8EncCodeAlphaBlock(VP8EncIterator* it) {
  (void)it;
  // Nothing for now. We just ZLIB-compress in the end.
}

int VP8EncFinishAlpha(VP8Encoder* enc) {
  if (enc->has_alpha_) {
#ifdef WEBP_EXPERIMENTAL_FEATURES
    const WebPPicture* pic = enc->pic_;
    assert(pic->a);
    if (!CompressAlpha(pic->a, pic->width * pic->height,
                       &enc->alpha_data_, &enc->alpha_data_size_,
                       enc->config_->alpha_compression)) {
      return 0;
    }
#endif
  }
  return 1;
}

void VP8EncDeleteAlpha(VP8Encoder* enc) {
  free(enc->alpha_data_);
  enc->alpha_data_ = NULL;
  enc->alpha_data_size_ = 0;
  enc->has_alpha_ = 0;
}

#if defined(__cplusplus) || defined(c_plusplus)
}    // extern "C"
#endif
