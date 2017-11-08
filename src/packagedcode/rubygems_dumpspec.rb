#!/usr/bin/ruby
# -*- encoding: utf-8 -*-

#!/usr/bin/ruby

# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

# Dump a gemspec as JSON to stdout from a .gem file or a .gemspec file

require 'rubygems/package'
require 'json'

begin
  # only available in older rubygems 1.8.x 
  require 'rubygems/format'
  rescue LoadError
end


def gemspec(gem_or_spec)
  if gem_or_spec.end_with?('.gem')
    # try rubygems 2.x syntax then fallback to 1.8
    gem_spec = gem_spec = Gem::Package.new(gem_or_spec).spec rescue Gem::Format.from_file_by_path(gem_or_spec).spec 

  elsif gem_or_spec.end_with?('.gemspec')
    gem_spec = Gem::Specification.load(gem_or_spec)
  end

  spec_vars = {}
  gem_spec.instance_variables.each { |var| spec_vars[var.to_s.delete("@")] = gem_spec.instance_variable_get(var) }
  puts JSON.pretty_generate(spec_vars)
end

 
if __FILE__ == $PROGRAM_NAME
  gem_file = ARGV[0]
  gemspec(gem_file)
end
