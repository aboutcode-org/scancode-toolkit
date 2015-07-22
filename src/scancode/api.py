#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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

from __future__ import print_function, absolute_import

from collections import OrderedDict
from operator import itemgetter
from os.path import dirname
from os.path import exists
from os.path import join

from commoncode import fileutils


def extract_archives(location=None, verbose=False):
    """
    Extract recursively any archives found at location and yield an iterable of
    ExtractEvents.
    If verbose is False, only the "done" event is returned at extraction
    completion.
    If verbose is True, both "start" and "done" events are returned.
    """
    from extractcode.extract import extract
    from extractcode import default_kinds

    for xevent in extract(location, kinds=default_kinds, recurse=True):
        if xevent.done:
            yield xevent
        else:
            if verbose and not xevent.done:
                yield xevent


def get_copyrights(location=None):
    """
    Yield dictionaries of copyright data detected in the file at location.
    Each item contains a list of copyright statements and a start and end line.
    """
    from cluecode.copyrights import detect_copyrights

    for copyrights, _, _, _, start_line, end_line in detect_copyrights(location):
        if not copyrights:
            continue
        yield {
            'statements': copyrights,
            'start_line': start_line,
            'end_line': end_line,
        }


DEJACODE_LICENSE_URL = 'https://enterprise.dejacode.com/license_library/Demo/{}/'


def get_licenses(location=None):
    """
    Yield dictionaries of license data detected in the file at location for
    each detected license.
    """
    from licensedcode.models import get_license
    from licensedcode.detect import get_license_matches

    for match in get_license_matches(location):
        for license_key in match.rule.licenses:
            license = get_license(license_key)

            yield {
                'key': license.key,
                'short_name': license.short_name,
                'category': license.category,
                'owner': license.owner,
                'homepage_url': license.homepage_url,
                'text_url': license.text_urls[0] if license.text_urls else '',
                'dejacode_url': DEJACODE_LICENSE_URL.format(license.key),
                'spdx_license_key': license.spdx_license_key,
                'spdx_url': license.spdx_url,
                'start_line': match.query_position.start_line,
                'end_line': match.query_position.end_line,
            }


def get_html_template(format):
    """
    Given a format string corresponding to a template directory, load and return
    the template.html file found in that directory.
    """
    from jinja2 import Environment, FileSystemLoader
    templates_dir = get_template_dir(format)
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template('template.html')
    return template


def get_template_dir(format):
    """
    Given a format string return the corresponding template directory.
    """
    return join(dirname(__file__), 'templates', format)


def as_html_app(detected_data, scanned_path, output_file):
    """
    Return an HTML string built from a list of results and the html-app template.
    """
    template = get_html_template('html-app')
    import json
    html_dirs = get_html_app_files_dirs(output_file)
    if html_dirs:
        _, assets_dir = html_dirs
    else:
        assets_dir= ''
    return template.render(results=json.dumps(detected_data), 
                           assets_dir=assets_dir,
                           scanned_path=scanned_path)


class HtmlAppAssetCopyWarning(Exception):
    pass


class HtmlAppAssetCopyError(Exception):
    pass


def get_html_app_files_dirs(output_file):
    """
    Return a tuple of (parent_dir, dir_name) directory named after the
    `output_file` file object file_base_name (stripped from extension) and a
    `_files` suffix Return None if output is to stdout.
    """
    file_name = output_file.name
    if file_name == '<stdout>':
        return
    parent_dir = dirname(file_name)
    dir_name = fileutils.file_base_name(file_name) + '_files'
    return parent_dir, dir_name


def create_html_app_assets(output_file):
    """
    Given an html-app output_file, create the corresponding `_files` directory
    and copy the assets to this directory. The target directory is deleted if it
    exists.

    Raise HtmlAppAssetCopyWarning if the output_file is <stdout> or
    HtmlAppAssetCopyError if the copy was not possible.
    """
    try:
        assets_dir = join(get_template_dir('html-app'), 'assets')
        tgt_dirs = get_html_app_files_dirs(output_file)
        if not tgt_dirs:
            raise HtmlAppAssetCopyWarning()
        target_dir = join(*tgt_dirs)
        if exists(target_dir):
            fileutils.delete(target_dir)
        fileutils.copytree(assets_dir, target_dir)
    except HtmlAppAssetCopyWarning, w:
        raise w
    except Exception, e:
        raise HtmlAppAssetCopyError(e)


def as_html(detected_data):
    """
    Return an HTML string built from a list of results and the html template.
    """
    template = get_html_template('html')

    converted = OrderedDict()
    licenses = {}

    # Create a dict keyed by location
    for resource in detected_data:
        location = resource['location']
        results = []
        if 'copyrights' in resource:
            for entry in resource['copyrights']:
                results.append({
                    'start': entry['start_line'],
                    'end': entry['end_line'],
                    'what': 'copyright',
                    # NOTE: we display one statement per line.
                    'value': '\n'.join(entry['statements']),
                })
        if 'licenses' in resource:
            for entry in resource['licenses']:
                results.append({
                    'start': entry['start_line'],
                    'end': entry['end_line'],
                    'what': 'license',
                    'value': entry['key'],
                })

                if entry['key'] not in licenses:
                    licenses[entry['key']] = entry

        if results:
            converted[location] = sorted(results, key=itemgetter('start'))

        licenses = OrderedDict(sorted(licenses.items()))

    return template.render(results=converted, licenses=licenses)
