/*
 * Copyright (C) 2008 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// This file is a nearly line-for-line copy of bspatch.c from the
// bsdiff-4.3 distribution; the primary differences being how the
// input and output data are read and the error handling.  Running
// applypatch with the -l option will display the bsdiff license
// notice.

#include <stdio.h>
#include <sys/stat.h>
#include <errno.h>
#include <unistd.h>
#include <string.h>

#include <bzlib.h>

#include "mincrypt/sha.h"
#include "applypatch.h"

void ShowBSDiffLicense() {
    puts("The bsdiff library used herein is:\n"
         "\n"
         "Copyright 2003-2005 Colin Percival\n"
         "All rights reserved\n"
         "\n"
         "Redistribution and use in source and binary forms, with or without\n"
         "modification, are permitted providing that the following conditions\n"
         "are met:\n"
         "1. Redistributions of source code must retain the above copyright\n"
         "   notice, this list of conditions and the following disclaimer.\n"
         "2. Redistributions in binary form must reproduce the above copyright\n"
         "   notice, this list of conditions and the following disclaimer in the\n"
         "   documentation and/or other materials provided with the distribution.\n"
         "\n"
         "THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR\n"
         "IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED\n"
         "WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE\n"
         "ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY\n"
         "DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL\n"
         "DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS\n"
         "OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)\n"
         "HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,\n"
         "STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING\n"
         "IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE\n"
         "POSSIBILITY OF SUCH DAMAGE.\n"
         "\n------------------\n\n"
         "This program uses Julian R Seward's \"libbzip2\" library, available\n"
         "from http://www.bzip.org/.\n"
        );
}

static off_t offtin(u_char *buf)
{
    off_t y;

    y=buf[7]&0x7F;
    y=y*256;y+=buf[6];
    y=y*256;y+=buf[5];
    y=y*256;y+=buf[4];
    y=y*256;y+=buf[3];
    y=y*256;y+=buf[2];
    y=y*256;y+=buf[1];
    y=y*256;y+=buf[0];

    if(buf[7]&0x80) y=-y;

    return y;
}

int FillBuffer(unsigned char* buffer, int size, bz_stream* stream) {
    stream->next_out = (char*)buffer;
    stream->avail_out = size;
    while (stream->avail_out > 0) {
        int bzerr = BZ2_bzDecompress(stream);
        if (bzerr != BZ_OK && bzerr != BZ_STREAM_END) {
            printf("bz error %d decompressing\n", bzerr);
            return -1;
        }
        if (stream->avail_out > 0) {
            printf("need %d more bytes\n", stream->avail_out);
        }
    }
    return 0;
}

int ApplyBSDiffPatch(const unsigned char* old_data, ssize_t old_size,
                     const Value* patch, ssize_t patch_offset,
                     SinkFn sink, void* token, SHA_CTX* ctx) {

    unsigned char* new_data;
    ssize_t new_size;
    if (ApplyBSDiffPatchMem(old_data, old_size, patch, patch_offset,
                            &new_data, &new_size) != 0) {
        return -1;
    }

    if (sink(new_data, new_size, token) < new_size) {
        printf("short write of output: %d (%s)\n", errno, strerror(errno));
        return 1;
    }
    if (ctx) {
        SHA_update(ctx, new_data, new_size);
    }
    free(new_data);

    return 0;
}

int ApplyBSDiffPatchMem(const unsigned char* old_data, ssize_t old_size,
                        const Value* patch, ssize_t patch_offset,
                        unsigned char** new_data, ssize_t* new_size) {
    // Patch data format:
    //   0       8       "BSDIFF40"
    //   8       8       X
    //   16      8       Y
    //   24      8       sizeof(newfile)
    //   32      X       bzip2(control block)
    //   32+X    Y       bzip2(diff block)
    //   32+X+Y  ???     bzip2(extra block)
    // with control block a set of triples (x,y,z) meaning "add x bytes
    // from oldfile to x bytes from the diff block; copy y bytes from the
    // extra block; seek forwards in oldfile by z bytes".

    unsigned char* header = (unsigned char*) patch->data + patch_offset;
    if (memcmp(header, "BSDIFF40", 8) != 0) {
        printf("corrupt bsdiff patch file header (magic number)\n");
        return 1;
    }

    ssize_t ctrl_len, data_len;
    ctrl_len = offtin(header+8);
    data_len = offtin(header+16);
    *new_size = offtin(header+24);

    if (ctrl_len < 0 || data_len < 0 || *new_size < 0) {
        printf("corrupt patch file header (data lengths)\n");
        return 1;
    }

    int bzerr;

    bz_stream cstream;
    cstream.next_in = patch->data + patch_offset + 32;
    cstream.avail_in = ctrl_len;
    cstream.bzalloc = NULL;
    cstream.bzfree = NULL;
    cstream.opaque = NULL;
    if ((bzerr = BZ2_bzDecompressInit(&cstream, 0, 0)) != BZ_OK) {
        printf("failed to bzinit control stream (%d)\n", bzerr);
    }

    bz_stream dstream;
    dstream.next_in = patch->data + patch_offset + 32 + ctrl_len;
    dstream.avail_in = data_len;
    dstream.bzalloc = NULL;
    dstream.bzfree = NULL;
    dstream.opaque = NULL;
    if ((bzerr = BZ2_bzDecompressInit(&dstream, 0, 0)) != BZ_OK) {
        printf("failed to bzinit diff stream (%d)\n", bzerr);
    }

    bz_stream estream;
    estream.next_in = patch->data + patch_offset + 32 + ctrl_len + data_len;
    estream.avail_in = patch->size - (patch_offset + 32 + ctrl_len + data_len);
    estream.bzalloc = NULL;
    estream.bzfree = NULL;
    estream.opaque = NULL;
    if ((bzerr = BZ2_bzDecompressInit(&estream, 0, 0)) != BZ_OK) {
        printf("failed to bzinit extra stream (%d)\n", bzerr);
    }

    *new_data = malloc(*new_size);
    if (*new_data == NULL) {
        printf("failed to allocate %ld bytes of memory for output file\n",
               (long)*new_size);
        return 1;
    }

    off_t oldpos = 0, newpos = 0;
    off_t ctrl[3];
    off_t len_read;
    int i;
    unsigned char buf[24];
    while (newpos < *new_size) {
        // Read control data
        if (FillBuffer(buf, 24, &cstream) != 0) {
            printf("error while reading control stream\n");
            return 1;
        }
        ctrl[0] = offtin(buf);
        ctrl[1] = offtin(buf+8);
        ctrl[2] = offtin(buf+16);

        // Sanity check
        if (newpos + ctrl[0] > *new_size) {
            printf("corrupt patch (new file overrun)\n");
            return 1;
        }

        // Read diff string
        if (FillBuffer(*new_data + newpos, ctrl[0], &dstream) != 0) {
            printf("error while reading diff stream\n");
            return 1;
        }

        // Add old data to diff string
        for (i = 0; i < ctrl[0]; ++i) {
            if ((oldpos+i >= 0) && (oldpos+i < old_size)) {
                (*new_data)[newpos+i] += old_data[oldpos+i];
            }
        }

        // Adjust pointers
        newpos += ctrl[0];
        oldpos += ctrl[0];

        // Sanity check
        if (newpos + ctrl[1] > *new_size) {
            printf("corrupt patch (new file overrun)\n");
            return 1;
        }

        // Read extra string
        if (FillBuffer(*new_data + newpos, ctrl[1], &estream) != 0) {
            printf("error while reading extra stream\n");
            return 1;
        }

        // Adjust pointers
        newpos += ctrl[1];
        oldpos += ctrl[2];
    }

    BZ2_bzDecompressEnd(&cstream);
    BZ2_bzDecompressEnd(&dstream);
    BZ2_bzDecompressEnd(&estream);
    return 0;
}
