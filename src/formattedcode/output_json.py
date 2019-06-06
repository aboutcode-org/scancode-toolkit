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

from collections import OrderedDict

import simplejson
from six import string_types

from plugincode.output import output_impl
from plugincode.output import OutputPlugin
from scancode import CommandLineOption
from scancode import FileOptionType
from scancode import OUTPUT_GROUP

"""
Output plugins to write scan results as JSON.
"""

# Tracing flags
TRACE = False


def logger_debug(*args):
    pass


if TRACE:
    import sys
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, unicode)
                                     and a or repr(a) for a in args))


@output_impl
class JsonCompactOutput(OutputPlugin):

    options = [
        CommandLineOption(('--json', 'output_json',),
            type=FileOptionType(mode='wb', lazy=True),
            metavar='FILE',
            help='Write scan output as compact JSON to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order=10),
    ]

    def is_enabled(self, output_json, **kwargs):
        return output_json

    def process_codebase(self, codebase, output_json, **kwargs):
        results = get_results(codebase, as_list=False, **kwargs)
        write_json(results, output_file=output_json, pretty=False)


@output_impl
class JsonPrettyOutput(OutputPlugin):

    options = [
        CommandLineOption(('--json-pp', 'output_json_pp',),
            type=FileOptionType(mode='wb', lazy=True),
            metavar='FILE',
            help='Write scan output as pretty-printed JSON to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order=10),
    ]

    def is_enabled(self, output_json_pp, **kwargs):
        return output_json_pp

    def process_codebase(self, codebase, output_json_pp, **kwargs):
        results = get_results(codebase, as_list=False, **kwargs)
        write_json(results, output_file=output_json_pp, pretty=True)


def get_opened_file(output_file):
    if isinstance(output_file, string_types()):
        return open(output_file, 'wb')


def write_json(results, output_file, pretty=False, **kwargs):
    """
    Write `results` to the `output_file` opened file-like object.
    """
    # NOTE: we write as encoded, binary bytes, not as unicode, decoded text
    kwargs = dict(iterable_as_array=True, encoding='utf-8')
    if pretty:
        kwargs.update(dict(indent=2 * b' '))
    else:
        kwargs.update(dict(separators=(b',', b':',)))

    close_of = False
    try:
        if isinstance(output_file, string_types):
            output_file = open(output_file, 'wb')
            close_of = True
        output_file.write(simplejson.dumps(results, **kwargs))
        output_file.write(b'\n')
    finally:
        if close_of:
            output_file.close()


def get_results(codebase, as_list=False, **kwargs):
    """
    Return an ordered mapping of scan results collected from a `codebase`.
    if `as_list` consume the "files" iterator in a list sequence.
    """

    codebase.add_files_count_to_current_header()
    results = OrderedDict([('headers', codebase.get_headers()), ])

    # add codebase toplevel attributes such as summaries
    if codebase.attributes:
        results.update(codebase.attributes.to_dict())

    files = OutputPlugin.get_files(codebase, **kwargs)
    if as_list:
        files = list(files)
    results['files'] = files

    if TRACE:
        logger_debug('get_results: files')
        files = list(files)
        from pprint import pformat
        logger_debug(pformat(files))

    return results

