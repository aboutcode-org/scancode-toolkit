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

from plugincode import BasePlugin
from plugincode import PluginManager
from plugincode import HookimplMarker
from plugincode import HookspecMarker


stage = 'scan'
entrypoint = 'scancode_scan'

scan_spec = HookspecMarker(stage)
scan_impl = HookimplMarker(stage)


@scan_spec
class ScanPlugin(BasePlugin):
    """
    A scan plugin base class that all scan plugins must extend. A scan plugin
    provides a single `get_scanner()` method that returns a scanner function.
    The key under which scan results are retruned for a scanner is the plugin
    "name" attribute. This attribute is set automatically as the "entrypoint"
    name used for this plugin.
    """

    # a relative sort order number (integer or float). In scan results, results
    # from scanners are sorted by this sorted_order then by "key" which is the
    # scanner plugin name. This is also used in the CLI UI
    sort_order = 100

    # TODO: pass own command options name/values as concrete kwargs
    def get_scanner(self, **kwargs):
        """
        Return a scanner callable that takes a single `location` argument.
        This callable (typically a bare function) should carry as little state
        as possible as it may be executed through multiprocessing.
        Subclasses must override.
        """
        raise NotImplementedError


scan_plugins = PluginManager(
    stage=stage,
    module_qname=__name__,
    entrypoint=entrypoint,
    plugin_base_class=ScanPlugin
)
