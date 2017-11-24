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


post_scan_spec = HookspecMarker('post_scan')
post_scan_impl = HookimplMarker('post_scan')


@post_scan_spec
class PostScanPlugin(object):
    """
    A post-scan plugin layout class to be extended by the post_scan plugins.
    """

    def __init__(self, option, user_input):
        self.option = option
        self.user_input = user_input

    def process_results(self, results, active_scans):
        """
        Return an iterable of results (eventually transformed or filtered) based on the results iterable.

        results - an iterable of resources
        active_scans - iterable of scanners that were used to obtain the results (e.g. "copyrights", "licenses")
        """
        return results

    @staticmethod
    def get_click_options():
        """
        Return an iterable of `click.Option` objects to be
        used for calling the plugin.
        """
        return ()


post_scan_plugins = PluginManager('post_scan')
post_scan_plugins.add_hookspecs(sys.modules[__name__])


def initialize():
    """
    NOTE: this defines the entry points for use in setup.py
    """
    post_scan_plugins.load_setuptools_entrypoints('scancode_post_scan')
    for name, plugin in get_post_scan_plugins().items():
        if not issubclass(plugin, PostScanPlugin):
            raise Exception('Invalid post-scan plugin "%(name)s": does not extend "plugincode.post_scan.PostScanPlugin".' % locals())


def get_post_scan_plugins():
    """
    Return an ordered mapping of
        "command line option name" --> "plugin callable"
    for all the post_scan plugins. The mapping is sorted by option name.
    This is the main API for other code to access post_scan plugins.
    """
    return OrderedDict(sorted(post_scan_plugins.list_name_plugin()))
