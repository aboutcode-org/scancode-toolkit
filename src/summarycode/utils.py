#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#
# Visit https://aboutcode.org and https://github.com/nexB/scancode-toolkit for
# support and download. ScanCode is a trademark of nexB Inc.
#
# The ScanCode software is licensed under the Apache License version 2.0.
# The ScanCode open data is licensed under CC-BY-4.0.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#



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
            summary = dict([(key, value)])
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
        return -count, value or ''

    summarized = [
        dict([('value', value), ('count', count)])
        for value, count in sorted(counter.items(), key=by_count_value)]
    return summarized
