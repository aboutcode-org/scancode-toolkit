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

from collections import OrderedDict
import codecs
from operator import itemgetter
import os

import simplejson as json

from commoncode import fileutils
from plugincode.output import scan_output_writer


"""
Output plugins to write scan results using templates such as HTML.

Also contains a builtin to write scan results using a custom template
which is NOT a plugin
"""


@scan_output_writer
def write_html(scanned_files, output_file, _echo, version, *args, **kwargs):
    """
    Write scan output formatted as plain HTML page.
    """
    _write_templated(scanned_files, output_file, _echo, version, template_or_format='html', raise_ex=False)


def write_custom(scanned_files, output_file, _echo, version, template_path):
    """
    Write scan output formatted with a custom template.
    NOTE: this is NOT a plugin, but a built-in
    """
    _write_templated(scanned_files, output_file, _echo, version, template_or_format=template_path, raise_ex=True)


def _write_templated(scanned_files, output_file, _echo, version, template_or_format, raise_ex=False):
    """
    Write scan output using a template or a format.
    Optionally raise an exception on errors.
    """

    for template_chunk in as_template(scanned_files, version, template=template_or_format):
        try:
            output_file.write(template_chunk)
        except Exception:
            import traceback
            extra_context = 'ERROR: Failed to write output for: ' + repr(template_chunk)
            extra_context += '\n' + traceback.format_exc()
            _echo(extra_context, fg='red')
            if raise_ex:
                # NOTE: this is a tad brutal to raise here, but helps
                # the template authors
                raise


@scan_output_writer
def write_html_app(scanned_files, input, output_file, _echo, version, *args, **kwargs):
    """
    Write scan output formatted as a mini HTML application.
    """
    output_file.write(as_html_app(input, version, output_file))
    try:
        create_html_app_assets(scanned_files, output_file)
    except HtmlAppAssetCopyWarning:
        _echo('\nHTML app creation skipped when printing to stdout.', fg='yellow')
    except HtmlAppAssetCopyError:
        _echo('\nFailed to create HTML app.', fg='red')


def create_html_app_assets(results, output_file):
    """
    Given an html-app output_file, create the corresponding `_files`
    directory and copy the assets to this directory. The target
    directory is deleted if it exists.

    Raise HtmlAppAssetCopyWarning if the output_file is <stdout> or
    HtmlAppAssetCopyError if the copy was not possible.
    """
    try:
        if is_stdout(output_file):
            raise HtmlAppAssetCopyWarning()
        assets_dir = os.path.join(get_template_dir('html-app'), 'assets')

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


def as_html_app(scanned_path, version, output_file):
    """
    Return an HTML string built from a list of results and the html-app template.
    """
    template = get_template(get_template_dir('html-app'))
    _, assets_dir = get_html_app_files_dirs(output_file)

    return template.render(assets_dir=assets_dir, scanned_path=scanned_path, version=version)


def get_html_app_help(output_filename):
    """
    Return an HTML string containing the html-app help page with a
    reference back to the main app page.
    """
    template = get_template(get_template_dir('html-app'),
                            template_name='help_template.html')

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


#
# Common utilities for templated scans outputs: html, html-app and
# custom templates.
#

# FIXME: no HTML default!
def get_template(templates_dir, template_name='template.html'):
    """
    Given a template directory, load and return the template file in the template_name
    file found in that directory.
    """
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template(template_name)
    return template


def get_template_dir(format):
    """
    Given a format string return the corresponding standard template
    directory.
    """
    return os.path.join(os.path.dirname(__file__), 'templates', format)


# FIXME: no HTML default!
def as_template(scanned_files, version, template):
    """
    Return an string built from a list of `scanned_files` results and
    the provided `template` identifier. The template defaults to the standard HTML
    template format or can point to the path of a custom template file.
    """
    # FIXME: This code is highly coupled with actual scans and may not
    # support adding new scans at all

    from licensedcode.cache import get_licenses_db

    # FIXME: factor out the html vs custom from this function: we should get a template path
    if template == 'html':
        template = get_template(get_template_dir('html'))
    else:
        # load a custom template
        tpath = fileutils.as_posixpath(os.path.abspath(os.path.expanduser(template)))
        assert os.path.isfile(tpath)
        tdir = fileutils.parent_directory(tpath)
        tfile = fileutils.file_name(tpath)
        template = get_template(tdir, tfile)

    converted = OrderedDict()
    converted_infos = OrderedDict()
    converted_packages = OrderedDict()
    licenses = {}

    # Create a flattened data dict keyed by path
    for scanned_file in scanned_files:
        path = scanned_file['path']
        results = []
        if 'copyrights' in scanned_file:
            for entry in scanned_file['copyrights']:
                results.append({
                    'start': entry['start_line'],
                    'end': entry['end_line'],
                    'what': 'copyright',
                    # NOTE: we display one statement per line.
                    'value': '\n'.join(entry['statements']),
                })
        if 'licenses' in scanned_file:
            for entry in scanned_file['licenses']:
                results.append({
                    'start': entry['start_line'],
                    'end': entry['end_line'],
                    'what': 'license',
                    'value': entry['key'],
                })

                # FIXME: we hsould NOT rely on license objects: only use what is in the JSON instead
                if entry['key'] not in licenses:
                    licenses[entry['key']] = entry
                    entry['object'] = get_licenses_db().get(entry['key'])
        if results:
            converted[path] = sorted(results, key=itemgetter('start'))

        # TODO: this is klunky: we need to drop templates entirely or we
        # should rather just pass a the list of files from the scan
        # results and let the template handle this rather than
        # denormalizing the list here??
        converted_infos[path] = OrderedDict()
        for name, value in scanned_file.items():
            if name in ('licenses', 'packages', 'copyrights', 'emails', 'urls'):
                continue
            converted_infos[path][name] = value

        if 'packages' in scanned_file:
            converted_packages[path] = scanned_file['packages']

        licenses = OrderedDict(sorted(licenses.items()))

    files = {
        'license_copyright': converted,
        'infos': converted_infos,
        'packages': converted_packages
    }

    return template.generate(files=files, licenses=licenses, version=version)
