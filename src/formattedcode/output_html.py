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
import io
from operator import itemgetter
from os.path import abspath
from os.path import basename
from os.path import dirname
from os.path import exists
from os.path import expanduser
from os.path import isfile
from os.path import join

import click
import simplejson

from commoncode.fileutils import PATH_TYPE
from commoncode.fileutils import as_posixpath
from commoncode.fileutils import copytree
from commoncode.fileutils import delete
from commoncode.fileutils import file_name
from commoncode.fileutils import file_base_name
from commoncode.fileutils import fsencode
from commoncode.fileutils import parent_directory
from commoncode.system import on_linux
from formattedcode.utils import get_headings
from plugincode.output import output_impl
from plugincode.output import OutputPlugin
from scancode import CommandLineOption
from scancode import FileOptionType
from scancode import OUTPUT_GROUP

"""
Output plugins to write scan results using templates such as HTML.

Also contains a builtin to write scan results using a custom template
which is NOT a plugin
"""


@output_impl
class HtmlOutput(OutputPlugin):

    options = [
        CommandLineOption(('--html',),
            type=FileOptionType(mode='wb', lazy=False),
            metavar='FILE',
            help='Write scan output as HTML to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order=50),
    ]

    def is_enabled(self, html, **kwargs):
        return html

    def process_codebase(self, codebase, html, **kwargs):
        results = self.get_results(codebase, **kwargs)
        _files_count, version, _notice, _scan_start, _options = get_headings(codebase)
        write_templated(html, results, version, template_or_format='html')


@output_impl
class CustomTemplateOutput(OutputPlugin):

    options = [
        CommandLineOption(('--custom-output',),
            type=FileOptionType(mode='wb', lazy=False),
            requires=['custom_template'],
            metavar='FILE',
            help='Write scan output to FILE formatted with '
                 'the custom Jinja template file.',
            help_group=OUTPUT_GROUP,
            sort_order=60),

        CommandLineOption(('--custom-template',),
            type=click.Path(
                exists=True, file_okay=True, dir_okay=False,
                readable=True, path_type=PATH_TYPE),
            requires=['custom_output'],
            metavar='FILE',
            help='Use this Jinja template FILE as a custom template.',
            help_group=OUTPUT_GROUP,
            sort_order=65),
    ]

    def is_enabled(self, custom_output, custom_template, **kwargs):
        return custom_output and custom_template

    def process_codebase(self, codebase, custom_output, custom_template, **kwargs):
        results = self.get_results(codebase, **kwargs)
        _files_count, version, _notice, _start, _options = get_headings(codebase)

        if on_linux:
            custom_template = fsencode(custom_template)

        write_templated(custom_output, results, version,
                        template_or_format=custom_template)


@output_impl
class HtmlAppOutput(OutputPlugin):
    """
    Write scan output as a mini HTML application.
    """
    options = [
        CommandLineOption(('--html-app',),
            type=FileOptionType(mode='wb', lazy=False),
            metavar='FILE',
            help='Write scan output as a mini HTML application to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order=70),
    ]

    def is_enabled(self, html_app, **kwargs):
        return html_app

    def process_codebase(self, codebase, input, html_app, **kwargs):  # NOQA
        results = self.get_results(codebase, **kwargs)
        _files_count, version, _notice, _start, _options = get_headings(codebase)
        html_app.write(as_html_app(html_app, input, version))
        create_html_app_assets(results, html_app)


def write_templated(output_file, results, version, template_or_format):
    """
    Write scan output using a template or a format.
    Optionally raise an exception on errors.
    """

    for template_chunk in as_template(results, version, template_or_format=template_or_format):
        try:
            output_file.write(template_chunk)
        except Exception:
            import traceback
            msg = 'ERROR: Failed to write output for: ' + repr(template_chunk)
            msg += '\n' + traceback.format_exc()
            raise Exception(msg)


def get_template(templates_dir, template_name='template.html'):
    """
    Given a `templates_dir` template directory, load and return the template
    file for the `template_name` file found in that directory.
    """
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template(template_name)
    return template


def get_template_dir(format_code):
    """
    Return the template directory of a built-in template for a `format_code`
    string.
    """
    return join(dirname(__file__), 'templates', format_code)


def as_template(results, version, template_or_format):
    """
    Return an string built from a list of `results` and the provided `template`
    identifier. The template_or_format is either a built-in template format code
    (e.g. "html") or the path of a custom template file.
    """
    # FIXME: This code is highly coupled with actual scans and may not
    # support adding new scans at all

    from licensedcode.cache import get_licenses_db

    # FIXME: factor out the html vs custom from this function: we should get a template path
    if template_or_format == 'html':
        template = get_template(get_template_dir('html'))
    else:
        # load a custom template
        tpath = as_posixpath(abspath(expanduser(template_or_format)))
        assert isfile(tpath)
        tdir = parent_directory(tpath)
        tfile = file_name(tpath)
        template = get_template(tdir, tfile)

    converted = OrderedDict()
    converted_infos = OrderedDict()
    converted_packages = OrderedDict()
    licenses = {}

    LICENSES = 'licenses'
    COPYRIGHTS = 'copyrights'
    PACKAGES = 'packages'
    URLS = 'urls'
    EMAILS = 'emails'

    # Create a flattened data dict keyed by path
    for scanned_file in results:
        scanned_file = OrderedDict(scanned_file)
        path = scanned_file['path']
        results = []
        if COPYRIGHTS in scanned_file:
            for entry in scanned_file[COPYRIGHTS]:
                results.append({
                    'start': entry['start_line'],
                    'end': entry['end_line'],
                    'what': 'copyright',
                    'value': entry['value'],
                })
        if LICENSES in scanned_file:
            for entry in scanned_file[LICENSES]:
                # make copy
                entry = dict(entry)
                entry_key = entry['key']
                results.append({
                    'start': entry['start_line'],
                    'end': entry['end_line'],
                    'what': 'license',
                    'value': entry_key,
                })

                # FIXME: we should NOT rely on license objects: only use what is in the JSON instead
                if entry_key not in licenses:
                    licenses[entry_key] = entry
                    # we were modifying the scan data in place ....
                    entry['object'] = get_licenses_db().get(entry_key)
        if results:
            converted[path] = sorted(results, key=itemgetter('start'))

        # TODO: this is klunky: we need to drop templates entirely or we
        # should rather just pass a the list of files from the scan
        # results and let the template handle this rather than
        # denormalizing the list here??
        converted_infos[path] = OrderedDict()
        for name, value in scanned_file.items():
            if name in (LICENSES, PACKAGES, COPYRIGHTS, EMAILS, URLS):
                continue
            converted_infos[path][name] = value

        if PACKAGES in scanned_file:
            converted_packages[path] = scanned_file[PACKAGES]

        licenses = OrderedDict(sorted(licenses.items()))

    files = {
        'license_copyright': converted,
        'infos': converted_infos,
        'packages': converted_packages
    }

    return template.generate(files=files, licenses=licenses, version=version)


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
        assets_dir = join(get_template_dir('html-app'), 'assets')

        # delete old assets
        tgt_dirs = get_html_app_files_dirs(output_file)
        target_dir = join(*tgt_dirs)
        if exists(target_dir):
            delete(target_dir)

        # copy assets
        copytree(assets_dir, target_dir)

        # write json data
        # FIXME: this should a regular JSON scan format
        root_path, assets_dir = get_html_app_files_dirs(output_file)
        with io.open(join(root_path, assets_dir, 'data.js'), 'wb') as f:
            f.write(b'data=')
            simplejson.dump(results, f, iterable_as_array=True)

        # create help file
        with io.open(join(root_path, assets_dir, 'help.html'), 'w', encoding='utf-8') as f:
            f.write(get_html_app_help(basename(output_file.name)))
    except HtmlAppAssetCopyWarning, w:
        raise w
    except Exception as e:  # NOQA
        import traceback
        msg = 'ERROR: cannot create HTML application.\n' + traceback.format_exc()
        raise HtmlAppAssetCopyError(msg)


def as_html_app(output_file, scanned_path, version,):
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
    `output_file` file-like object file_base_name (stripped from extension) and
    a `_files` suffix Return empty strings if output is to stdout.
    """
    if is_stdout(output_file):
        return '', ''

    # FIXME: what if there is no name attribute??
    file_name = output_file.name
    parent_dir = dirname(file_name)
    dir_name = file_base_name(file_name) + '_files'
    return parent_dir, dir_name
