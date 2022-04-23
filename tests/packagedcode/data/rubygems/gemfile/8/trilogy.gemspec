require File.expand_path("../lib/trilogy/version", __FILE__)

Gem::Specification.new do |s|
  s.name = "trilogy"
  s.version = Trilogy::VERSION
  s.authors = ["GitHub Engineering"]
  s.email = "opensource+trilogy@github.com"
  s.license = "MIT"
  s.homepage = "https://github.com/github/trilogy"
  s.summary = "A friendly MySQL-compatible library for Ruby, binding to libtrilogy"

  s.extensions = "ext/trilogy-ruby/extconf.rb"

  gem_files = %w[LICENSE README.md Rakefile trilogy.gemspec]
  gem_files += Dir.glob("lib/**/*.rb")
  gem_files += Dir.glob("ext/trilogy-ruby/*.c")
  gem_files += Dir.glob("ext/trilogy-ruby/*.h")
  gem_files += Dir.glob("ext/trilogy-ruby/src/**/*.c")
  gem_files += Dir.glob("ext/trilogy-ruby/inc/**/*.h")

  s.files = gem_files

  s.require_paths = ["lib"]

  s.add_development_dependency "rake-compiler", "~> 1.0"
  s.add_development_dependency "minitest", "~> 5.5"
end
