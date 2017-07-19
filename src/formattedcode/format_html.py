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
from __future__ import division
from __future__ import unicode_literals

import codecs
import os

import simplejson as json

from commoncode import fileutils
from plugincode.scan_output_hooks import scan_output

from formattedcode import templated


"""
Output plugins to write scan results as HTML.
"""


@scan_output
def write_html(scanned_files, output_file, _echo, *args, **kwargs):
    """
    Write scan output formatted as plain HTML page.
    """
    for template_chunk in templated.as_template(scanned_files):
        try:
            output_file.write(template_chunk)
        except Exception as e:
            extra_context = 'ERROR: Failed to write output to HTML for: ' + repr(template_chunk)
            _echo(extra_context, fg='red')


@scan_output
def write_html_app(scanned_files, input, output_file, _echo, *args, **kwargs):
    """
    Write scan output formatted as a mini HTML application.
    """
    output_file.write(as_html_app(input, output_file))
    try:
        create_html_app_assets(scanned_files, output_file)
    except HtmlAppAssetCopyWarning:
        _echo('\nHTML app creation skipped when printing to stdout.', fg='yellow')
    except HtmlAppAssetCopyError:
        _echo('\nFailed to create HTML app.', fg='red')


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
        assets_dir = os.path.join(templated.get_template_dir('html-app'), 'assets')

        # delete old assets
        tgt_dirs = get_html_app_files_dirs(output_file)
        target_dir = os.path.join(*tgt_dirs)
        if os.path.exists(target_dir):
            fileutils.delete(target_dir)

        # copy assets
        fileutils.copytree(assets_dir, target_dir)

        # write json data
        root_path, assets_dir = get_html_app_files_dirs(output_file)
        with codecs.open(os.path.join(root_path, assets_dir, 'data.json'), 'wb', encoding='utf-8') as f:
            f.write('data=')
            json.dump(results, f, iterable_as_array=True)

        # create help file
        with codecs.open(os.path.join(root_path, assets_dir, 'help.html'), 'wb', encoding='utf-8') as f:
            f.write(get_html_app_help(os.path.basename(output_file.name)))
    except HtmlAppAssetCopyWarning, w:
        raise w
    except Exception, e:
        raise HtmlAppAssetCopyError(e)


def as_html_app(scanned_path, output_file):
    """
    Return an HTML string built from a list of results and the html-app template.
    """
    template = templated.get_template(templated.get_template_dir('html-app'))
    _, assets_dir = get_html_app_files_dirs(output_file)

    return template.render(assets_dir=assets_dir, scanned_path=scanned_path)


def get_html_app_help(output_filename):
    """
    Return an HTML string containing html-app help page with a reference back
    to the main app
    """
    template = templated.get_template(templated.get_template_dir('html-app'), template_name='help_template.html')

    return template.render(main_app=output_filename)


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
    parent_dir = os.path.dirname(file_name)
    dir_name = fileutils.file_base_name(file_name) + '_files'
    return parent_dir, dir_name
