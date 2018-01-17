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


stage = 'housekeeping'
entrypoint = 'scancode_housekeeping'

housekeeping_spec = HookspecMarker(project_name=stage)
housekeeping_impl = HookimplMarker(project_name=stage)


@housekeeping_spec
class HousekeepingPlugin(BasePlugin):
    """
    Base plugin class for miscellaneous housekeeping plugins that are executed
    eagerly and exclusively of all other options.
    They must define only eager option flags that run with a Click callback
    options. They scan nothing.
    """
    pass

    def is_enabled(self):
        """
        By design and because they are executed eagerly through a callback, an
        HousekeepingPlugin is never "enabled" during scan processing.
        """
        return False


housekeeping_plugins = PluginManager(
    stage=stage,
    module_qname=__name__,
    entrypoint=entrypoint,
    plugin_base_class=HousekeepingPlugin
)
