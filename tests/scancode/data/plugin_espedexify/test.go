// Copyright 2017 Google Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.


// Package licenseclassifier provides methods to identify the open source
// license that most closely matches an unknown license.
package licenseclassifier

import (
        "archive/tar"
        "bytes"
        "compress/gzip"
        "fmt"
        "html"
        "io"
        "math"
        "regexp"
        "sort"
        "strings"
        "sync"
        "unicode"

        "github.com/google/licenseclassifier/stringclassifier"
        "github.com/google/licenseclassifier/stringclassifier/searchset"
)

