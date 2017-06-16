#
# Copyright (c) 2016 nexB Inc. and others. All rights reserved.
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

from __future__ import print_function
from __future__ import absolute_import

from os.path import dirname
from os.path import abspath
from os.path import getsize
from os.path import getmtime
from os.path import join
from os.path import exists

from commoncode import fileutils


scan_src_dir = abspath(dirname(__file__))
src_dir = dirname(scan_src_dir)
root_dir = dirname(src_dir)
cache_dir = join(root_dir, '.cache')
scans_cache_dir = join(cache_dir, 'scan_results_caches')

if not exists(scans_cache_dir):
    fileutils.create_dir(scans_cache_dir)


from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution('scancode-toolkit').version
except DistributionNotFound:
    # package is not installed ??
    __version__ = '2.0.0rc3'
