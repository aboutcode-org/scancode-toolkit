# JSON implementation for Ruby

## Description

This is an implementation of the JSON specification according to RFC 7159
http://www.ietf.org/rfc/rfc7159.txt .

The JSON generator generate UTF-8 character sequences by default.
If an :ascii\_only option with a true value is given, they escape all
non-ASCII and control characters with \uXXXX escape sequences, and support
UTF-16 surrogate pairs in order to be able to generate the whole range of
unicode code points.

All strings, that are to be encoded as JSON strings, should be UTF-8 byte
sequences on the Ruby side.

## Author

Florian Frank <mailto:flori@ping.de>

## License

Ruby License, see https://www.ruby-lang.org/en/about/license.txt.

## Download

The latest version of this library can be downloaded at

* https://rubygems.org/gems/json

Online Documentation should be located at

* https://www.rubydoc.info/gems/json
