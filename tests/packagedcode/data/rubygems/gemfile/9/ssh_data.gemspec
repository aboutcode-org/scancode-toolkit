$:.unshift File.expand_path('../lib', __FILE__)
require "ssh_data/version"

Gem::Specification.new do |s|
  s.name = "ssh_data"
  s.summary = "Library for parsing SSH certificates"
  s.version = SSHData::VERSION
  s.license = "MIT"
  s.homepage = "https://github.com/github/ssh_data"
  s.authors = ["mastahyeti"]
  s.email = "opensource+ssh_data@github.com"
  s.required_ruby_version = ">= 2.3"
  s.files = Dir["./lib/**/*.rb"] + ["./LICENSE.md"]

  s.add_development_dependency "ed25519", "~> 1.2"
  s.add_development_dependency "pry", "~> 0.14"
  s.add_development_dependency "rspec", "~> 3.10"
  s.add_development_dependency "rspec-mocks", "~> 3.10"
end
