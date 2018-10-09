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

import attr

from plugincode.pre_scan import PreScanPlugin
from plugincode.pre_scan import pre_scan_impl
from scancode import CommandLineOption
from scancode import PRE_SCAN_GROUP

# Tracing flag
TRACE = False


def logger_debug(*args):
    pass


if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, unicode) and a or repr(a) for a in args))

"""
Assign a category to a file.

A category is defined by functions that can check for multiple things such as:
- file type information (form info)
- file content
... and assign a

The known categories are:
    -
"""

KNOWN_CATEGORIES = set([
    'source',
    'script',
    'binary',
    'compiled',
    'toplevel',
    'metadata',
    'build',
    'tool',
    'doc',
    'data',
    'test',
    'thirdparty',
    'legal',
    'generated',
])


@pre_scan_impl
class Categorize(PreScanPlugin):
    """
    Assign one or more categories to each file or directory.
    """

    resource_attributes = dict(categories=attr.ib(default=attr.Factory(list)))

    sort_order = 25

    options = [
        CommandLineOption(('--categorize',),
           is_flag=True,
           help='Add categories to files using built-in rules.',
           help_group=PRE_SCAN_GROUP,
           sort_order=85,
        )
    ]

    def is_enabled(self, categorize, **kwargs):
        if TRACE:
            logger_debug('is_enabled: categorize:', categorize)
        return categorize

    def process_codebase(self, codebase, categorize, **kwargs):
        """
        Add categories to resources
        """

        if not categorize:
            return

        def update_categories(res, cats):
            """Update the `res` Resource categories with the `cats` categories."""
            if res.is_file:
                updated_categories = set(res.categories)
                updated_categories.update(cats)
                updated_categories = sorted(updated_categories)
                if res.categories != updated_categories:
                    res.categories = updated_categories
                    res.save(codebase)

        # Walk the codebase and set the categories for each resource
        for resource in codebase.walk(topdown=True):
            categories = get_categories(resource)
            if not categories:
                continue

            update_categories(resource, categories)

            for child in resource.children(codebase, categories):
                update_categories(child)


def get_categories(resource, categorizers=()):
    """
    Return a sorted list of unique facet strings for `path` using the
    `facet_definitions` mapping of {pattern: [facet, facet]}.
    """

    categories = []
    for categorizer in categorizers:
        categories.extend(categorizer(resource))
    return categories