// Copyright 2014 The Go Authors. All rights reserved.
// Use of this source code is governed by a BSD-style
// license that can be found in the LICENSE file.

// Package oauth2 provides support for making
// OAuth2 authorized and authenticated HTTP requests.
// It can additionally grant authorization with Bearer JWT.
package oauth2 // import "golang.org/x/oauth2"

import (
	"bytes"
	"errors"
	"net/http"
	"net/url"
	"strings"
	"sync"

	"golang.org/x/net/context"
	"golang.org/x/oauth2/internal"
)
