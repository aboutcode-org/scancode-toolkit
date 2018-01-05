#
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

from __future__ import absolute_import
from __future__ import unicode_literals

from commoncode import fileset
from commoncode.fileutils import parent_directory
from commoncode.system import on_linux
from plugincode.pre_scan import PreScanPlugin
from plugincode.pre_scan import pre_scan_impl
from scancode.cli import ScanOption


def is_ignored(location, ignores):
    """
    Return a tuple of (pattern , message) if a file at location is ignored or
    False otherwise. `ignores` is a mappings of patterns to a reason.
    """
    return fileset.match(location, includes=ignores, excludes={})


@pre_scan_impl
class ProcessIgnore(PreScanPlugin):
    """
    Ignore files matching the supplied pattern.
    """

    def __init__(self, selected_options, active_scan_names=None):
        PreScanPlugin.__init__(
            self, selected_options, active_scan_names=active_scan_names)

        ignores = []
        for se in selected_options:
            if se.name == 'ignore':
                ignores = se.value or []

        self.ignores = {
            pattern: 'User ignore: Supplied by --ignore' for pattern in ignores
        }


    @classmethod
    def get_plugin_options(cls):
        return [
            ScanOption(('--ignore',),
                   multiple=True,
                   metavar='<pattern>',
                   help='Ignore files matching <pattern>.')
        ]

    def process_resources(self, resources):
        # FIXME: this is hacksih at best
        ignored_paths = set()
        seps = b'/\\' if on_linux else '/\\'
        for resource in resources:
            abs_path = resource.abs_path.strip(seps)
            if is_ignored(abs_path, ignores=self.ignores):
                ignored_paths.add(abs_path)
            else:
                parent = parent_directory(abs_path).strip(seps)
                if parent not in ignored_paths:
                    yield resource

    def is_enabled(self):
        return any(se.value for se in self.selected_options
                   if se.name == 'ignore')
