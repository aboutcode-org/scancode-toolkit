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
 
# Dump to stdout a JSON representation of the marshal-formatted
# Rubygems index.
# See https://blog.engineyard.com/2014/new-rubygems-index-format
# The output file is in the form: name, version, platform
# [
#   ["capistrano-rsync-scm","0.0.3","ruby"],
#   ["drpentode-scrivener","0.0.3","ruby"]
# ]

require 'rubygems/package'
require 'json'
 
 
def gemindex(rubygems_index_file)
  idx = Marshal.load(Gem.gunzip(File.read(rubygems_index_file)))
  puts JSON.pretty_generate(idx)
end
 
if __FILE__ == $PROGRAM_NAME
  rubygems_index_file = ARGV[0]
  gemindex(rubygems_index_file)
end
