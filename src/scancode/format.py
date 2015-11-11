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


"""
Format scans outputs.
"""


def get_html_template(format):  # @ReservedAssignment
    """
    Given a format string corresponding to a template directory, load and return
    the template.html file found in that directory.
    """
    from jinja2 import Environment, FileSystemLoader
    templates_dir = get_template_dir(format)
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template('template.html')
    return template


def get_template_dir(format):  # @ReservedAssignment
    """
    Given a format string return the corresponding template directory.
    """
    return join(dirname(__file__), 'templates', format)


def as_html_app(scanned_path, output_file):
    """
    Return an HTML string built from a list of results and the html-app template.
    """
    template = get_html_template('html-app')
    _, assets_dir = get_html_app_files_dirs(output_file)

    return template.render(assets_dir=assets_dir, scanned_path=scanned_path)


class HtmlAppAssetCopyWarning(Exception):
    pass


class HtmlAppAssetCopyError(Exception):
    pass


def is_stdout(output_file):
    return output_file.name == '<stdout>'


def get_html_app_files_dirs(output_file):
    """
    Return a tuple of (parent_dir, dir_name) directory named after the
    `output_file` file object file_base_name (stripped from extension) and a
    `_files` suffix Return empty strings if output is to stdout.
    """
    if is_stdout(output_file):
        return '', ''

    file_name = output_file.name
    parent_dir = dirname(file_name)
    dir_name = fileutils.file_base_name(file_name) + '_files'
    return parent_dir, dir_name


def create_html_app_assets(results, output_file):
    """
    Given an html-app output_file, create the corresponding `_files` directory
    and copy the assets to this directory. The target directory is deleted if it
    exists.

    Raise HtmlAppAssetCopyWarning if the output_file is <stdout> or
    HtmlAppAssetCopyError if the copy was not possible.
    """
    try:
        if is_stdout(output_file):
            raise HtmlAppAssetCopyWarning()
        assets_dir = join(get_template_dir('html-app'), 'assets')

        tgt_dirs = get_html_app_files_dirs(output_file)
        target_dir = join(*tgt_dirs)
        if exists(target_dir):
            fileutils.delete(target_dir)
        fileutils.copytree(assets_dir, target_dir)

        # write json data
        import json
        root_path, assets_dir = get_html_app_files_dirs(output_file)
        with open(join(root_path, assets_dir, 'data.json'), 'w') as f:
            f.write('data=' + json.dumps(results))
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
    converted_infos = OrderedDict()
    converted_packages = OrderedDict()
    licenses = {}

    # Create a dict keyed by location
    for scan_result in detected_data:
        location = scan_result['location']
        results = []
        if 'copyrights' in scan_result:
            for entry in scan_result['copyrights']:
                results.append({
                    'start': entry['start_line'],
                    'end': entry['end_line'],
                    'what': 'copyright',
                    # NOTE: we display one statement per line.
                    'value': '\n'.join(entry['statements']),
                })
        if 'licenses' in scan_result:
            for entry in scan_result['licenses']:
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

        if 'infos' in scan_result:
            converted_infos[location] = scan_result['infos']

        if 'packages' in scan_result:
            converted_packages[location] = scan_result['packages']

        licenses = OrderedDict(sorted(licenses.items()))

    results = {
        "license_copyright": converted,
        "infos": converted_infos,
        "packages": converted_packages
    }

    return template.render(results=results, licenses=licenses)

