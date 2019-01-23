$LOAD_PATH << File.expand_path('../lib', __FILE__)

require 'provider_dsl/gem_description'

Gem::Specification.new do |specification|
  specification.name = ProviderDSL::GemDescription::NAME
  specification.version = ProviderDSL::GemDescription::VERSION
  specification.authors = ProviderDSL::GemDescription::AUTHORS
  specification.email = ProviderDSL::GemDescription::EMAIL
  specification.homepage = ProviderDSL::GemDescription::PAGE
  specification.summary = ProviderDSL::GemDescription::SUMMARY
  specification.description = 'See the project home page for more information'
  specification.files = Dir['lib/**/*']
  specification.require_paths = %w(lib)
  specification.add_development_dependency 'rake', '~> 11.3'
  specification.add_development_dependency 'rubocop', '~> 0.44.1'
  specification.add_development_dependency 'rspec', '~> 3.5'
  specification.add_development_dependency 'rspec-mocks', '~> 3.5'
  specification.add_dependency 'ipaddress', '~> 0.8.3'
  specification.add_dependency 'gandi', '~> 3.3', '>= 3.3.27'
  specification.add_dependency 'gcloud', '~> 0.21.0'
  specification.add_dependency 'google-cloud-error_reporting', '~> 0.21.0'
  specification.add_dependency 'map', '~> 6.6'
end