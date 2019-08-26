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

from __future__ import absolute_import, print_function

import logging
import os

from commoncode import command
from commoncode import fileutils
from commoncode.functional import flatten

from plugincode.location_provider import get_location


SCANCODE_CTAGS_EXE = 'scancode.ctags.exe'
SCANCODE_CTAGS_LIB = 'scancode.ctags.lib'

""" 
A set of functions and objects to extract information from source code files
"""
LOG = logging.getLogger(__name__)

bin_dir = os.path.join(os.path.dirname(__file__), 'bin')


class Source(object):
    """
    Source code object.
    """
    def __init__(self, sourcefile):
        # yield nothing if we do not have a proper command
        self.sourcefile = sourcefile
        
        self.cmd_loc = get_location(SCANCODE_CTAGS_EXE)
        self.lib_loc = get_location(SCANCODE_CTAGS_LIB)

        # nb: those attributes names are api and expected when fingerprinting
        # a list of sources files names (not path)
        self.files = []
        self.files.append(fileutils.file_name(sourcefile))
        # a list of function names
        self.local_functions = []
        self.global_functions = []

        self._collect_and_parse_tags()

    def symbols(self):
        glocal = flatten([self.local_functions, self.global_functions])
        return sorted(glocal)

    def _collect_and_parse_tags(self):
        ctags_args = ['--fields=K',
                      '--c-kinds=fp',
                      '-f', '-',
                      self.sourcefile
                      ]
        ctags_temp_dir = fileutils.get_temp_dir(base_dir='ctags')
        envt = {'TMPDIR': ctags_temp_dir}
        try:
            rc, stdo, err = command.execute2(cmd_loc=self.cmd_loc, ctags_args, env=envt,
                                             lib_dir=self.lib_loc, to_files=True)
            
            if rc != 0:
                raise Exception(open(err).read())

            with open(stdo, 'rb') as lines:
                for line in lines:
                    if 'cannot open temporary file' in line:
                        raise Exception('ctags: cannot open temporary file '
                                        ': Permission denied')

                    if line.startswith('!'):
                        continue

                    line = line.strip()
                    if not line:
                        continue

                    splitted = line.split('\t')

                    if (line.endswith('function\tfile:')
                        or line.endswith('prototype\tfile:')):
                        self.local_functions.append(splitted[0])

                    elif (line.endswith('function')
                          or line.endswith('prototype')):
                        self.global_functions.append(splitted[0])
        finally:
            fileutils.delete(ctags_temp_dir)
