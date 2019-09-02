#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import
from __future__ import unicode_literals

from os.path import abspath
from os.path import dirname
from os.path import join

from plugincode.location_provider import LocationProviderPlugin
from plugincode.location_provider import location_provider_impl

import platform

class LibmagicPaths(LocationProviderPlugin):
	def get_locations(self):
	
		distribution = platform.linux_distribution()[0]		

		debian_based_distro = ['Ubuntu','Mint','debian']
		rpm_based_distro = ['Fedora','redhat']
		
		if distribution in debian_based_distro:
				
			data_dir = '/usr/lib/file'
			lib_dir = '/usr/lib/x86_64-linux-gnu'
		
		elif distribution in rpm_based_distro:
			
			data_dir = '/usr/share/misc'
			lib_dir = '/usr/lib64'

		else:
			data_dir = '/usr'
			lib_dir = '/usr'

		locations = {
			'typecode.libmagic.libdir': lib_dir,
			'typecode.libmagic.dll': join(lib_dir, 'libmagic.so.1'),
			'typecode.libmagic.db': join(data_dir, 'magic.mgc'),
			}
		return locations
