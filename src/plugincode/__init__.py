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
    A base class for all scancode plugins.
    """
    # a short string describing this plugin. Subclass must override
    name = None

    def __init__(self, selected_options):
        """
        Initialize a new plugin with a mapping of user selected options.
        """
        self.selected_options = selected_options

    def process_one(self, resource):
        """
        Yield zero, one or more Resource objects from a single `resource`
        Resource object.
        """
        yield resource

    def process_resources(self, resources):
        """
        Return an iterable of Resource objects, possibly transformed, filtered
        or enhanced by this plugin from  a `resources` iterable of Resource
        objects.
        """
        for resource in resources:
            for res in self.process_one(resource):
                if res:
                    yield res

    @classmethod
    def get_plugin_options(cls):
        """
        Return a list of `ScanOption` objects for this plugin.
        Subclass must override.
        """
        return []


