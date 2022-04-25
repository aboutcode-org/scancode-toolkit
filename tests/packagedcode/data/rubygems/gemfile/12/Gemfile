# frozen_string_literal: true

source 'https://rubygems.org'

git_source(:github) do |repo_name|
  repo_name = "#{repo_name}/#{repo_name}" unless repo_name.include?("/")
  "https://github.com/#{repo_name}.git"
end

ruby ">= 2.7.2", "< 3.1"

git_source :github do |name|
  "https://github.com/#{name}.git"
end

gem 'mime-types', '~> 3.3', require: 'mime/types/columnar'

# Gems required in all environments
if ENV["RAILS_MASTER"] == '1'
  gem 'rails', git: 'https://github.com/rails/rails.git'
else
  gem 'rails', '6.1.4.1'
end

gem 'bluecloth'
gem 'dalli'
gem 'devise', github: "heartcombo/devise"
gem 'git_hub_bub'
gem 'jquery-rails'
gem 'local_time', '2.1.0'
gem 'maildown', '~> 3.3'
gem 'omniauth', '~> 2.0.4'
gem 'omniauth-rails_csrf_protection'
gem 'omniauth-github'
gem 'pg'
gem 'puma'
gem 'rack-timeout'
gem 'rrrretry'
gem 'valid_email'
gem 'warden', '1.2.9'
gem 'wicked'
gem 'will_paginate', '3.3.1'
# gem 'sass-rails', '6.0.0.beta1'
gem 'sassc'
gem 'sassc-rails'

gem 'autoprefixer-rails', '~> 10.2.4'
gem 'bourbon'
gem 'coffee-rails', '~> 5.0.0'
gem 'neat', '~> 1.7'
gem 'normalize-rails'
gem 'slim-rails'
gem 'uglifier', '>= 1.0.3'
gem 'render_async', '~> 2.1'

group :development do
  gem 'bullet', require: false, github: 'flyerhzm/bullet'
  gem 'foreman'
  gem 'listen'
  gem 'web-console'
  gem 'memory_profiler'
end

group :test do
  gem 'capybara', '3.35.3'
  # Not essential but helpful for save_and_open_page
  gem 'launchy'
  gem 'mocha', require: false
  gem 'rails-controller-testing'
  gem 'simplecov', require: false
  gem 'vcr'
  gem 'webmock'
  gem 'test-prof'
end

group :development, :test do
  gem 'derailed_benchmarks'
  gem 'dotenv-rails', '2.7.6'
  gem 'faker', require: false
  gem 'pry'
  gem 'rubocop', require: false
  gem 'rubocop-performance'
end

gem 'rack-mini-profiler'

gem 'the_lone_dyno'

gem 'sidekiq'
gem 'sinatra', '~> 2.1.0'

gem 'aws-sdk-s3', '~> 1.103.0'

gem 'mail', require: ['mail', 'mail/utilities', 'mail/parsers'] # parsers is used by `valid_email` and may be causing https://github.com/mikel/mail/issues/912#issuecomment-170121429

gem 'sprockets', github: "rails/sprockets"
gem 'sprockets-rails'

gem 'babel-transpiler'

gem 'scout_apm', '~> 4.1.2'
gem 'yard', '~> 0.9.26'

gem 'oj'
gem 'rack-canonical-host'
gem 'sentry-raven'

gem 'bootsnap', require: false
gem 'rbtrace'
gem 'redis-namespace'
gem 'stackprof'
gem 'flamegraph'
gem 'prawn'
gem 'skylight', '~> 5.1.1'

gem 'minitest', '5.14.4'
gem 'sitemap_generator'
gem 'premailer-rails'

# gem 'barnes'
gem 'puma_worker_killer'
gem 'rake'
gem 'rails_autoscale_agent', github: 'adamlogic/rails_autoscale_agent', branch: 'puma'
