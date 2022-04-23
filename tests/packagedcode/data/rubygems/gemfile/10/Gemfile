source 'https://rubygems.org'

git_source(:github) do |repo_name|
  repo_name = "#{repo_name}/#{repo_name}" unless repo_name.include?("/")
  "https://github.com/#{repo_name}.git"
end

gem 'nokogiri', '~> 1.12', '< 1.13' ### TEMPORARY PIN 1.13 requires ruby > 2.5

gem 'rails', '~> 5.2'
gem 'dotenv-deployment'
gem 'dotenv-rails'

# Required gems for QA and linked data access
gem 'qa_server', '~> 7.9'
gem 'qa', '~> 5.5'
gem 'linkeddata'

# Other gems
gem 'coffee-rails', '~> 4.2'
gem 'concurrent-ruby'
gem 'jbuilder', '~> 2.5'
gem 'lograge'
gem 'mysql2'
gem 'puma', '~> 4.3'
gem 'sass-rails', '~> 5.0'
gem 'turbolinks', '~> 5'
gem 'tzinfo-data', platforms: [:mingw, :mswin, :x64_mingw, :jruby] # Windows does not include zoneinfo files, so bundle the tzinfo-data gem
gem 'uglifier', '>= 1.3.0'

group :development, :test do
  gem 'byebug'
  gem 'coveralls', require: false
  gem 'database_cleaner'
  gem 'factory_bot_rails', '~> 4.4', require: false
  gem 'faker'
  gem 'listen'
  gem 'rails-controller-testing'
end

group :development do
  gem 'better_errors' # add command line in browser when errors
  gem 'binding_of_caller' # deeper stack trace used by better errors
  gem 'bixby', '~> 1.0.0' # style guide enforcement with rubocop
  gem 'rubocop'
  gem 'rubocop-checkstyle_formatter', require: false
  gem 'spring' # Spring speeds up development by keeping your application running in the background.
  gem 'web-console', '~> 3.0' # access to IRB console on exception pages
  gem 'xray-rails'
end

group :test do
  gem 'rspec-rails'
  gem 'rspec-activemodel-mocks'
  gem 'sqlite3'
end

gem 'swagger-docs'
