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

from collections import OrderedDict
import sys

from pluggy import HookimplMarker
from pluggy import HookspecMarker
from pluggy import PluginManager


pre_scan_spec = HookspecMarker('pre_scan')
pre_scan_impl = HookimplMarker('pre_scan')

@pre_scan_spec
class PreScanPlugin(object):
    """
    A pre-scan plugin layout class to be extended by the pre_scan plugins.
    Docstring of a plugin class will be used as the plugin option's help text
    """

    # attributes to be used while creating the option for this plugin.
    option_attrs = {}

    def __init__(self, user_input):
        self.user_input = user_input

    def process_resources(self, resources):
        """
        Yield the absolute paths after processing.
         - `resources`: a generator with absolute paths of files to be scanned.
        """
        return resources

    def get_ignores(self):
        """
        Return a dict of ignores to be used when processing resources
        """
        return {}


pre_scan_plugins = PluginManager('pre_scan')
pre_scan_plugins.add_hookspecs(sys.modules[__name__])


def initialize():
    # NOTE: this defines the entry points for use in setup.py
    pre_scan_plugins.load_setuptools_entrypoints('scancode_pre_scan')
    for name, plugin in get_pre_scan_plugins().items():
        if not issubclass(plugin, PreScanPlugin):
            raise Exception('Invalid pre-scan plugin "%(name)s": does not extend "plugincode.pre_scan.PreScanPlugin".' % locals())

def get_pre_scan_plugins():
    """
    Return an ordered mapping of CLI option name --> plugin callable
    for all the pre_scan plugins. The mapping is ordered by sorted key.
    This is the main API for other code to access pre_scan plugins.
    """
    return OrderedDict(sorted(pre_scan_plugins.list_name_plugin()))
