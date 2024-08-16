# Iron

[![Build Status](https://secure.travis-ci.org/iron/iron.svg?branch=master)](https://travis-ci.org/iron/iron)
[![Crates.io Status](http://meritbadge.herokuapp.com/iron)](https://crates.io/crates/iron)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/iron/iron/master/LICENSE)

> Extensible, Concurrency Focused Web Development in Rust.

## Overview

Iron is a high level web framework built in and for Rust, built on
[hyper](https://github.com/hyperium/hyper). Iron is designed to take advantage
of Rust's greatest features - its excellent type system and its principled
approach to ownership in both single threaded and multi threaded contexts.

Iron is highly concurrent and can scale horizontally on more machines behind a
load balancer or by running more threads on a more powerful machine. Iron
avoids the bottlenecks encountered in highly concurrent code by avoiding shared
writes and locking in the core framework.

Iron is 100% safe code:

```sh
$ rg unsafe src | wc
       0       0       0
```

## Performance

Iron averages [72,000+ requests per second for hello world](https://github.com/iron/iron/wiki/How-to-Benchmark-hello.rs-Example)
and is mostly IO-bound, spending over 70% of its time in the kernel send-ing or
recv-ing data.\*

\* _Numbers from profiling on my OS X machine, your mileage may vary._

## Core Extensions

Iron aims to fill a void in the Rust web stack - a high level framework that is
_extensible_ and makes organizing complex server code easy.

Extensions are painless to build. Some important ones are:

Middleware:

- [Routing](https://github.com/iron/router)
- [Mounting](https://github.com/iron/mount)
- [Static File Serving](https://github.com/iron/staticfile)
- [Logging](https://github.com/iron/logger)

Plugins:

- [JSON Body Parsing](https://github.com/iron/body-parser)
- [URL Encoded Data Parsing](https://github.com/iron/urlencoded)
- [All-In-One (JSON, URL, & Form Data) Parameter Parsing](https://github.com/iron/params)

Both:

- [Shared Memory (also used for Plugin configuration)](https://github.com/iron/persistent)
- [Sessions](https://github.com/iron/iron-sessionstorage)

## Underlying HTTP Implementation

Iron is based on and uses [`hyper`](https://github.com/hyperium/hyper) as its
HTTP implementation, and lifts several types from it, including its header
representation, status, and other core HTTP types. It is usually unnecessary to
use `hyper` directly when using Iron, since Iron provides a facade over
`hyper`'s core facilities, but it is sometimes necessary to depend on it as
well.



## License

MIT
