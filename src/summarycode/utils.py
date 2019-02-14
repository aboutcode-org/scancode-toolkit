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
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict

def get_resource_summary(resource, key, as_attribute=False):
    """
    Return the "summary" value as mapping for the `key` summary attribute of a
    resource.

    This is collected either from a direct Resource.summary attribute if
    `as_attribute` is True or as a Resource.extra_data summary item otherwise.
    """
    if as_attribute:
        summary = resource.summary
    else:
        summary = resource.extra_data.get('summary', {})
    summary = summary or {}
    return summary.get(key) or None


def set_resource_summary(resource, key, value, as_attribute=False):
    """
    Set `value` as the "summary" value for the `key` summary attribute of a
    resource

    This is set either in a direct Resource.summary attribute if `as_attribute`
    is True or as a Resource.extra_data summary item otherwise.
    """
    if as_attribute:
        resource.summary[key] = value
    else:
        summary = resource.extra_data.get('summary')
        if not summary:
            summary = OrderedDict([(key, value)])
            resource.extra_data['summary'] = summary
        summary[key] = value


def sorted_counter(counter):
    """
    Return a list of ordered mapping of {value:val, count:cnt} built from a
    `counter` mapping of {value: count} and sortedd by decreasing count then by
    value.
    """

    def by_count_value(value_count):
        value, count = value_count
        return -count, value

    summarized = [OrderedDict([('value', value), ('count', count)])
                  for value, count in sorted(counter.items(), key=by_count_value)]
    return summarized
