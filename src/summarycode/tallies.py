#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from collections import Counter
import attr
from commoncode.cliutils import POST_SCAN_GROUP, PluggableCommandLineOption
from plugincode.post_scan import PostScanPlugin, post_scan_impl
from summarycode.utils import (get_resource_tallies, set_resource_tallies,
                               sorted_counter)

@post_scan_impl
class Tallies(PostScanPlugin):
    run_order = 15
    sort_order = 15
    codebase_attributes = dict(tallies=attr.ib(default=attr.Factory(dict)))
    options = [
        PluggableCommandLineOption(('--tallies',),
            is_flag=True, default=False,
            help='Compute tallies for license, copyright and other scans.',
            help_group=POST_SCAN_GROUP)
    ]
    def is_enabled(self, tallies, **kwargs):
        return tallies
    def process_codebase(self, codebase, tallies, **kwargs):
        tallies = compute_codebase_tallies(codebase, keep_details=False, **kwargs)
        codebase.attributes.tallies.update(tallies)

@post_scan_impl
class TalliesWithDetails(PostScanPlugin):
    codebase_attributes = dict(tallies=attr.ib(default=attr.Factory(dict)))
    resource_attributes = dict(tallies=attr.ib(default=attr.Factory(dict)))
    run_order = 100
    sort_order = 100
    options = [
        PluggableCommandLineOption(('--tallies-with-details',),
            is_flag=True, default=False,
            help='Compute tallies keeping intermediate details.',
            help_group=POST_SCAN_GROUP)
    ]
    def is_enabled(self, tallies_with_details, **kwargs):
        return tallies_with_details
    def process_codebase(self, codebase, tallies_with_details, **kwargs):
        tallies = compute_codebase_tallies(codebase, keep_details=True, **kwargs)
        codebase.attributes.tallies.update(tallies)

@post_scan_impl
class KeyFilesTallies(PostScanPlugin):
    run_order = 150
    sort_order = 150
    codebase_attributes = dict(tallies_of_key_files=attr.ib(default=attr.Factory(dict)))
    options = [
        PluggableCommandLineOption(('--tallies-key-files',),
            is_flag=True, default=False,
            help='Compute tallies for key files.',
            help_group=POST_SCAN_GROUP,
            required_options=['classify', 'tallies'])
    ]
    def is_enabled(self, tallies_key_files, **kwargs):
        return tallies_key_files
    def process_codebase(self, codebase, tallies_key_files, **kwargs):
        pass

@post_scan_impl
class FacetTallies(PostScanPlugin):
    run_order = 200
    sort_order = 200
    codebase_attributes = dict(tallies_by_facet=attr.ib(default=attr.Factory(list)))
    options = [
        PluggableCommandLineOption(('--tallies-by-facet',),
            is_flag=True, default=False,
            help='Compute tallies grouped by facet.',
            help_group=POST_SCAN_GROUP,
            required_options=['facet', 'tallies'])
    ]
    def is_enabled(self, tallies_by_facet, **kwargs):
        return tallies_by_facet
    def process_codebase(self, codebase, tallies_by_facet, **kwargs):
        pass

def size_weighted_tally(resource, children, key, keep_details=False):
    scores = {}
    
    # Get the file size; we look at .size and fallback to 1 only as a last resort
    # We use max(..., 1) to ensure even empty files have some presence
    current_size = getattr(resource, 'size', 0) or 0
    weight = int(current_size) if current_size > 0 else 1

    values = getattr(resource, key, [])

    if resource.is_file and values:
        if not isinstance(values, list):
            values = [values]
        for val in values:
            if isinstance(val, dict):
                singular_map = {'copyrights': 'copyright', 'holders': 'holder', 'authors': 'author'}
                singular_key = singular_map.get(key, 'value')
                actual_val = val.get(singular_key, val.get('value', str(val)))
            else:
                actual_val = val
            if actual_val:
                scores[actual_val] = scores.get(actual_val, 0) + weight

    # Aggregate from children
    for child in children:
        child_tallies = get_resource_tallies(child, key=key, as_attribute=keep_details) or []
        for child_tally in child_tallies:
             val = child_tally.get('value')
             # IMPORTANT: child_tally['count'] is already a size-sum from the lower level
             scores[val] = scores.get(val, 0) + child_tally.get('count', 0)

    tallied = [{'value': v, 'count': c} for v, c in scores.items()]
    tallied.sort(key=lambda x: x['count'], reverse=True)
    set_resource_tallies(resource, key=key, value=tallied, as_attribute=keep_details)
    return tallied

def compute_codebase_tallies(codebase, keep_details, **kwargs):
    attrib_summarizers = [
        ('detected_license_expression', license_tallies),
        ('copyrights', lambda r, c, **k: size_weighted_tally(r, c, 'copyrights', **k)),
        ('holders', lambda r, c, **k: size_weighted_tally(r, c, 'holders', **k)),
        ('authors', lambda r, c, **k: size_weighted_tally(r, c, 'authors', **k)),
        ('programming_language', lambda r, c, **k: size_weighted_tally(r, c, 'programming_language', **k)),
        ('packages', package_tallies),
    ]
    root = codebase.root
    summarizers = [s for a, s in attrib_summarizers if hasattr(root, a)]
    for resource in codebase.walk(topdown=False):
        children = resource.children(codebase)
        for summarizer in summarizers:
            summarizer(resource, children, keep_details=keep_details)
        codebase.save_resource(resource)
    
    return root.tallies if keep_details else root.extra_data.get('tallies', {})

def license_tallies(resource, children, keep_details=False):
    LIC_EXP = 'detected_license_expression'
    license_expressions = []
    for attr_name in ['license_detections', 'license_clues']:
        for detection in getattr(resource, attr_name, []):
            license_expressions.append(detection["license_expression"])
    if not license_expressions and resource.is_file:
        license_expressions.append(None)
    for child in children:
        child_tallies = get_resource_tallies(child, key=LIC_EXP, as_attribute=keep_details) or []
        for child_tally in child_tallies:
            license_expressions.extend([child_tally.get('value')] * child_tally['count'])
    tallied = sorted_counter(Counter(license_expressions))
    set_resource_tallies(resource, key=LIC_EXP, value=tallied, as_attribute=keep_details)
    return tallied

def package_tallies(resource, children, keep_details=False):
    packages = []
    for package in (getattr(resource, 'packages') or []):
        files = package['files'] = package.get('files') or []
        fil = resource.to_dict(skinny=True)
        if fil not in files: files.append(fil)
        packages.append(package)
    for child in children:
        packages.extend(get_resource_tallies(child, key='packages', as_attribute=False) or [])
    set_resource_tallies(resource, key='packages', value=packages, as_attribute=False)
    return packages