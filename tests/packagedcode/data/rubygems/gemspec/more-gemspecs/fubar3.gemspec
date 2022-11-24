# version and other data from require
require 'fubar3/version'

Gem::Specification.new do |spec|
  spec.name         = "fubar3"
  spec.version      = Fubar3::VERSION
  spec.date         = Fubar3::DATE
  spec.summary      = "Fine Uber Archive"
  spec.description  = "A archive extraction library"

  spec.author       = "nexB"
  spec.email        = "info@nexb.com"
  spec.homepage     = "https://github.com/pombredanne/fubar"
  spec.license      = "ISC"

  spec.require_path = "lib"
  spec.files        = Dir["CHANGELOG.md", "LICENSE.md", "README.md",
                          "lib/**/*"]

  spec.required_ruby_version = ">= 2.4.1"
  spec.required_rubygems_version = ">= 2.6.12"

  spec.add_dependency 'foo', '1.0.0'
end

