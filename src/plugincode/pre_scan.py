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

from plugincode import CodebasePlugin
from plugincode import PluginManager
from plugincode import HookimplMarker
from plugincode import HookspecMarker


stage = 'pre_scan'
entrypoint = 'scancode_pre_scan'

pre_scan_spec = HookspecMarker(stage)
pre_scan_impl = HookimplMarker(stage)


@pre_scan_spec
class PreScanPlugin(CodebasePlugin):
    """
    A pre-scan plugin base class that all pre-scan plugins must extend.
    """

    # List of scanner name strings that this plugin requires to run first
    # before this pres-scan plugin runs.
    # Subclasses should set this as needed
    requires = []

    def get_required(self, scanner_plugins):
        """
        Return a list of unique required scanner plugin instances that are
        direct requirements of self. `scanner_plugins` is a list of enabled
        scanner plugins.
        """
        required = []
        for name in self.requires:
            required_plugin = scanner_plugins.get(name)
            if not required_plugin:
                qname = self.qname
                raise Exception(
                    'Missing required scan plugin: %(name)r '
                    'for plugin: %(qname)r.' % locals())
            required.append(required_plugin)
        return unique(required)

    @classmethod
    def get_all_required(self, prescan_plugins, scanner_plugins):
        """
        Return a list of unique required scanner plugin instances that are
        direct requirements of any of the `prescan_plugins` pre-scan plugin
        instances. `prescan_plugins` is a list of enabled pre-scan plugins.
        `scanner_plugins` is a list of enabled scanner plugins.
        """
        required = []
        scanner_plugins_ny_name = {p.name: p for p in scanner_plugins}
        for plugin in prescan_plugins:
            required.extend(plugin.get_required(scanner_plugins_ny_name))
        return unique(required)


def unique(iterable):
    """
    Return a sequence of unique items in `iterable` keeping their
    original order.
    Note: this can be very slow for large sequences as this is using lists.
    """
    uniques = []
    for item in iterable:
        if item not in uniques:
            uniques.append(item)
    return uniques


pre_scan_plugins = PluginManager(
    stage=stage,
    module_qname=__name__,
    entrypoint=entrypoint,
    plugin_base_class=PreScanPlugin
)
