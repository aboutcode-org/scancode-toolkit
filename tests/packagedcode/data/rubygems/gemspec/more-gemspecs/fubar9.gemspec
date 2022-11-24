# frozen_string_literal: true
Gem::Specification.new do |spec|
  spec.name         = "fubar"
  spec.version      = "0.4.2"
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

  spec.add_dependency 'activesupport', '>= 4.0'
  spec.add_dependency "bundler", ">= 1.12.0"
  spec.add_dependency "excon", "~> 0.55"
  spec.add_dependency "gemnasium-parser", "~> 0.1"
  spec.add_dependency "gems", "~> 1.0"
  spec.add_dependency "gitlab", "~> 4.1"
  spec.add_dependency "octokit", "~> 4.6"

  spec.add_development_dependency "rake"
  spec.add_development_dependency "rspec", "~> 3.5.0"
  spec.add_development_dependency "rspec-its", "~> 1.2.0"
  spec.add_development_dependency "rubocop-packaging", "~> 0.48.0"
  spec.add_development_dependency "webmock", "~> 2.3.1"

end

