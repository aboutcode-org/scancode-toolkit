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

from collections import defaultdict

import attr
import click

from commoncode.fileset import get_matches as get_fileset_matches
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
Assign a facet to a file.

A facet is defined by zero or more glob/fnmatch expressions. Multiple facets can
be assigned to a file. The facets definition is a list of (facet, pattern) and a
file is assigned all thye facets that have a pattern defintion that match their
path.

Once all files have been assigned a facet, files without a facet are assigned to
the core facet.

The known facets are:

    - core - core files of a package. Used as default if no other facet apply.
    - data - data files of a package (such as CSV, etc).
    - dev - files used at development time (e.g. build scripts, dev tools, etc)
    - docs - Documentation files.
    - examples - Code example files.
    - tests - Test files and tools.
    - thirdparty - Embedded code from a third party (aka. vendored or bundled)

See also https://github.com/clearlydefined/clearlydefined/blob/8f58a9a216cf7c129fe2cf6abe1cc6f960535e0b/docs/clearly.md#facets
"""

FACET_CORE = 'core'
FACET_DEV = 'dev'
FACET_TESTS = 'tests'
FACET_DOCS = 'docs'
FACET_DATA = 'data'
FACET_EXAMPLES = 'examples'

FACETS = (
    FACET_CORE,
    FACET_DEV,
    FACET_TESTS,
    FACET_DOCS,
    FACET_DATA,
    FACET_EXAMPLES,
)


def validate_facets(ctx, param, value):
    """
    Return the facets if valid or raise a UsageError otherwise.
    Validate facets values against the list of known facets.
    """
    if not value:
        return

    _facet_patterns, invalid_facet_definitions = build_facets(value)
    if invalid_facet_definitions:
        known_msg = ', '.join(FACETS)
        uf = '\n'.join(sorted('  ' + x for x in invalid_facet_definitions))
        msg = ('Invalid --facet option(s):\n'
               '{uf}\n'
               'Valid <facet> values are: {known_msg}.\n'.format(**locals()))
        raise click.UsageError(msg)
    return value


@pre_scan_impl
class AddFacet(PreScanPlugin):
    """
    Assign one or more "facet" to each file (and NOT to directories). Facets are
    a way to qualify that some part of the scanned code may be core code vs.
    test vs. data, etc.
    """

    resource_attributes = dict(facets=attr.ib(default=attr.Factory(list)))

    sort_order = 20

    options = [
        CommandLineOption(('--facet',),
           multiple=True,
           metavar='<facet>=<pattern>',
           callback=validate_facets,
           help='Add the <facet> to files with a path matching <pattern>.',
           help_group=PRE_SCAN_GROUP,
           sort_order=80,
        )
    ]

    def is_enabled(self, facet, **kwargs):
        if TRACE:
            logger_debug('is_enabled: facet:', facet)

        return bool(facet)

    def process_codebase(self, codebase, facet=(), **kwargs):
        """
        Add facets to file resources using the `facet` definition of facets.
        Each entry in the `facet` sequence is a string as in <facet>:<pattern>
        """

        if not facet:
            return

        facet_definitions, _invalid_facet_definitions = build_facets(facet)

        if TRACE:
            logger_debug('facet_definitions:', facet_definitions)

        # Walk the codebase and set the facets for each file (and only files)
        for resource in codebase.walk(topdown=True):
            if not resource.is_file:
                continue
            facets = compute_path_facets(resource.path, facet_definitions)
            if facets:
                resource.facets = facets
            else:
                resource.facets = [FACET_CORE]
            resource.save(codebase)


def compute_path_facets(path, facet_definitions):
    """
    Return a sorted list of unique facet strings for `path` using the
    `facet_definitions` mapping of {pattern: [facet, facet]}.
    """

    if not path or not path.strip() or not facet_definitions:
        return []

    facets = set()
    for matches in get_fileset_matches(path, facet_definitions, all_matches=True):
        facets.update(matches)
    return sorted(facets)


def build_facets(facets, known=FACETS):
    """
    Return:
        - a mapping for known facet_patterns as {pattern: [facet, facet, ...]}
        - a set of invalid_facet_definitions given a `facets` definitions as
        list of strings in the form ['facet: pattern error message', ].
    Use the `known` facets set of known facets for validation.
    """
    invalid_facet_definitions = set()
    facet_patterns = defaultdict(list)
    for facet_def in facets:
        facet, _, pattern = facet_def.partition('=')
        if not pattern:
            invalid_facet_definitions.add(
                'missing <pattern> in "{facet_def}".'.format(**locals()))
            continue

        if not facet:
            invalid_facet_definitions.add(
                'missing <facet> in "{facet_def}".'.format(**locals()))
            continue

        if facet not in known:
            invalid_facet_definitions.add(
                'unknown <facet> in "{facet_def}".'.format(**locals()))
        else:
            facet_patterns[pattern].append(facet)

    return facet_patterns, invalid_facet_definitions
