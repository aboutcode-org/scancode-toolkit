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
from __future__ import unicode_literals

from collections import OrderedDict
import sys

from pluggy import HookimplMarker
from pluggy import HookspecMarker
from pluggy import PluginManager


scan_output_spec = HookspecMarker('scan_output_writer')
scan_output_writer = HookimplMarker('scan_output_writer')


# FIXME: simplify the hooskpec
@scan_output_spec
def write_output(files_count, version, notice, scanned_files, options, input, output_file, _echo):
    """
    Write the `scanned_files` scan results in the format supplied by
    the --format command line option.
    Parameters:
     - `file_count`: the number of files and directories scanned.
     - `version`: ScanCode version
     - `notice`: ScanCode notice
     - `scanned_files`: an iterable of scan results for each file
     - `options`: a mapping of key by command line option to a flag True
        if this option was enabled.
     - `input`: the original input path scanned.
     - `output_file`: an opened, file-like object to write the output to.
     - `_echo`: a funtion to echo strings to stderr. This will be removedd in the future.
    """
    pass


output_plugins = PluginManager('scan_output_writer')
output_plugins.add_hookspecs(sys.modules[__name__])


def initialize():
    """
    NOTE: this defines the entry points for use in setup.py
    """
    output_plugins.load_setuptools_entrypoints('scancode_output_writers')


def get_format_plugins():
    """
    Return an ordered mapping of format name --> plugin callable for all
    the output plugins. The mapping is ordered by sorted key.
    This is the main API for other code to access format plugins.
    """
    return OrderedDict(sorted(output_plugins.list_name_plugin()))
