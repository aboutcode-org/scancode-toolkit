// Copyright 2014, 2015, 2016, 2017 Simon Lydell
// (See LICENSE.)

var fs           = require("fs")
var util         = require("util")
var assert       = require("assert")
var jsTokensTmp  = require("../")
var jsTokens     = jsTokensTmp.default
var matchToToken = jsTokensTmp.matchToToken


suite("jsTokens", function() {

  test("is a regex", function() {
    assert(util.isRegExp(jsTokens))
  })

})
