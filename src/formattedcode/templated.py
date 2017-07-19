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

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import OrderedDict
from operator import itemgetter
from os.path import abspath
from os.path import dirname
from os.path import expanduser
from os.path import isfile
from os.path import join

from commoncode import fileutils


"""
Common utilities for templated scans outputs: html, html-app and custom templates.
"""

def get_template(templates_dir, template_name='template.html'):  # @ReservedAssignment
    """
    Given a template directory, load and return the template file in the template_name
    file found in that directory.
    """
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template(template_name)
    return template


def get_template_dir(format):  # @ReservedAssignment
    """
    Given a format string return the corresponding standard template directory.
    """
    return join(dirname(__file__), 'templates', format)


def as_template(scanned_files, template='html'):
    """
    Return an string built from a list of results and the provided template.
    The template defaults to the standard HTML template format or can point to
    the path of a custom template file.
    """
    from licensedcode.cache import get_licenses_db

    if template == 'html':
        template = get_template(get_template_dir('html'))
    else:
        # load a custom template
        tpath = fileutils.as_posixpath(abspath(expanduser(template)))
        assert isfile(tpath)
        tdir = fileutils.parent_directory(tpath)
        tfile = fileutils.file_name(tpath)
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
    for scanned_file in scanned_files:
        path = scanned_file['path']
        results = []
        if COPYRIGHTS in scanned_file:
            for entry in scanned_file[COPYRIGHTS]:
                results.append({
                    'start': entry['start_line'],
                    'end': entry['end_line'],
                    'what': 'copyright',
                    # NOTE: we display one statement per line.
                    'value': '\n'.join(entry['statements']),
                })
        if LICENSES in scanned_file:
            for entry in scanned_file[LICENSES]:
                results.append({
                    'start': entry['start_line'],
                    'end': entry['end_line'],
                    'what': 'license',
                    'value': entry['key'],
                })

                if entry['key'] not in licenses:
                    licenses[entry['key']] = entry
                    entry['object'] = get_licenses_db().get(entry['key'])
        if results:
            converted[path] = sorted(results, key=itemgetter('start'))

        # this is klunky: we need to drop templates entirely
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

    return template.generate(files=files, licenses=licenses)
