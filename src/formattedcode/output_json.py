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

import jsonstreams
from six import string_types

from commoncode.system import py2
from commoncode.system import py3
from formattedcode import FileOptionType
from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import OUTPUT_GROUP
from plugincode.output import output_impl
from plugincode.output import OutputPlugin


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
        return logger.debug(' '.join(isinstance(a, string_types)
                                     and a or repr(a) for a in args))


if py2:
    mode = 'wb'
    space = b' '
    comma = b','
    colon = b':'
    eol = b'\n'

if py3:
    mode = 'w'
    space = u' '
    comma = u','
    colon = u':'
    eol = u'\n'


@output_impl
class JsonCompactOutput(OutputPlugin):

    options = [
        PluggableCommandLineOption(('--json', 'output_json',),
            type=FileOptionType(mode=mode, lazy=True),
            metavar='FILE',
            help='Write scan output as compact JSON to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order=10),
    ]

    def is_enabled(self, output_json, **kwargs):
        return output_json

    def process_codebase(self, codebase, output_json, **kwargs):
        write_results(codebase, output_file=output_json, pretty=False, **kwargs)


@output_impl
class JsonPrettyOutput(OutputPlugin):

    options = [
        PluggableCommandLineOption(('--json-pp', 'output_json_pp',),
            type=FileOptionType(mode=mode, lazy=True),
            metavar='FILE',
            help='Write scan output as pretty-printed JSON to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order=10),
    ]

    def is_enabled(self, output_json_pp, **kwargs):
        return output_json_pp

    def process_codebase(self, codebase, output_json_pp, **kwargs):
        write_results(codebase, output_file=output_json_pp, pretty=True, **kwargs)


def write_results(codebase, output_file, pretty=False, **kwargs):
    """
    Write headers, files, and other attributes from `codebase` to `output_file`

    Enable JSON indentation if `pretty` is True
    """
    # Set indentation for JSON output if `pretty` is True
    # We use a separate dict for jsonstream kwargs since we are passing
    # this function's kwargs as arguments to OutputPlugin.get_files()
    if pretty:
        jsonstreams_kwargs = dict(indent=2, pretty=True)
    else:
        jsonstreams_kwargs = dict()

    # If `output_file` is a path string, open the file at path `output_file` and use it as `output_file`
    close_stream = False
    s = None
    try:
        if isinstance(output_file, string_types):
            output_file = open(output_file, mode)
            close_stream = True

        # Begin writing JSON to `output_file`
        s = jsonstreams.Stream(jsonstreams.Type.object, fd=output_file, **jsonstreams_kwargs)

        # Write headers
        codebase.add_files_count_to_current_header()
        codebase_headers = codebase.get_headers()
        s.write('headers', codebase_headers)

        # Write attributes
        if codebase.attributes:
            for attribute_key, attribute_value in codebase.attributes.to_dict().items():
                s.write(attribute_key, attribute_value)

        # Write files
        codebase_files = OutputPlugin.get_files(codebase, **kwargs)
        s.write('files', codebase_files)

    finally:
        # FIXME: This is a hack. The final `}` of the json is written when the
        # jsonstreams.Stream.close() method is run. In some cases, we keep the json
        # file descriptor open and close it later, after we have left the
        # jsonstreams context and the output json plugin, so the final `}` is never
        # written and we cannot parse the results.
        #
        # The jsonstreams.Stream.close() method consists of two method calls,
        # - self.__inst.close()
        # - self.__fd.close()
        #
        # self.__inst.close() closes the written json object by writing the final
        # `}` to the file
        #
        # self.__fd.close() just closes the file descriptor
        #
        # To finish writing the json and keep the file open, we manually call
        # s._Stream__inst.close() (_Stream__inst is the same as __inst, for some
        # reason it is called _Stream__inst on the instantiated Stream object)
        if s:
            if not close_stream:
                s._Stream__inst.close()
                s._Stream__fd.flush()
            else:
                s._Stream__fd.flush()
                s.close()
