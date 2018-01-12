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
from __future__ import print_function
from __future__ import unicode_literals


class BasePlugin(object):
    """
    A base class for all ScanCode plugins.
    """
    # A short string describing this plugin, used for GUI display. The class
    # name is used if not provided. Subclass should override
    name = None

    # Tuple of scanner names that this plugin requires to run its own run
    requires = tuple()

    def __init__(self, command_options):
        """
        Initialize a new plugin with a list of user `command_options` (e.g.
        CommandOption tuples based on CLI keyword arguments).
        """
        self.command_options = command_options or []
 
    @classmethod
    def get_plugin_options(cls):
        """
        Return a list of `ScanOption` objects for this plugin.
        Subclasses must override and implement.
        """
        raise NotImplementedError

    def is_enabled(self):
        """
        Return True is this plugin is enabled by user-selected options.
        Subclasses must override.
        """
        raise NotImplementedError

    def setup(self):
        """
        Execute some setup for this plugin. This is guaranteed to be called
        exactly one time after initialization. Must return True on sucess or
        False otherwise. Subclasses can override as needed.
        """
        return True

    def teardown(self):
        """
        Execute some teardown for this plugin. This is guaranteed to be called
        exactly one time when ScanCode exists. Must return True on sucess or
        False otherwise. Subclasses can override as needed.
        """
        return True

    def process_resource(self, resource):
        """
        Process a single `resource` Resource object.
        Subclasses should override.
        """
        pass

    def process_codebase(self, codebase):
        """
        Process a `codebase` Codebase object updating its Reousrce as needed.
        Subclasses should override.
        """
        for resource in codebase.walk():
            self.process_resource(resource)
