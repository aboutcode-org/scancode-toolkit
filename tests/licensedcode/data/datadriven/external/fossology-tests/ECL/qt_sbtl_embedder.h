/**
 *  Copyright 2009, 2010 The Regents of the University of California
 *  Licensed under the Educational Community License, Version 2.0
 *  (the "License"); you may not use this file except in compliance
 *  with the License. You may obtain a copy of the License at
 *
 *  http://www.osedu.org/licenses/ECL-2.0
 *
 *  Unless required by applicable law or agreed to in writing,
 *  software distributed under the License is distributed on an "AS IS"
 *  BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
 *  or implied. See the License for the specific language governing
 *  permissions and limitations under the License.
 *
 */

#ifndef QT_SBTL_EMBEDDER_H_
#define QT_SBTL_EMBEDDER_H_

#include <mp4v2/mp4v2.h>

// track flags
#define TRACK_DISABLED 0x0
#define TRACK_ENABLED 0x1
#define TRACK_IN_MOVIE 0x2

// buffer size for text lines
#define BUFFER_SIZE 4096

// maximum number of subtitles
#define MAX_SBTL 25

// Custom structures

// structure that holds subtitle files
typedef struct _sub_file {
  char* filepath;
  char* language;
  int valid;
} sub_file;

// structure that holds program parameters
typedef struct _program_parameters {
  char* qt_filepath;
  sub_file* subtitle_files[MAX_SBTL];
  int sub_number;
  char* output_file;
  int track_height;
  int font_height;
  int bottom_offset;
  int optimize;
  int verbosity;
} program_parameters;

// SRT processing functions

int check_srt_file(char* srt_filepath);
int parse_srt_file(char* srt_filepath, MP4FileHandle handle, MP4TrackId track_id);
int parse_srt_time(char* srt_time);

// QT processing functions

int copy_qt_file(char* source, char* destination);

// mp4v2 library functions

MP4FileHandle open_qt_file(char* qt_file, int verbosity);
MP4TrackId create_subtitle_track(MP4FileHandle handle, char* language,
  unsigned int track_height, unsigned int font_height, unsigned int bottom_offset);
int add_caption_block(MP4FileHandle handle, MP4TrackId track_id, char* caption,
  unsigned int duration);
void remove_track(MP4FileHandle handle, MP4TrackId track_id);
void close_qt_file(MP4FileHandle handle);
void optimize_qt_file(char* filename);

// general

program_parameters* parse_parameters(int argc, char* argv[]);
void print_usage(char* program_name);

#endif /* QT_SBTL_EMBEDDER_H_ */
