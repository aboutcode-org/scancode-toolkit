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

import re
import logging

from cluecode import finder


LOG = logging.getLogger(__name__)


# TODO: beef up.
# add detailed annotation for each of the common MODULE_XXX macros
# add support for checking the GPL symbols GPLONLY and so on
# add support for finding the init_module and module_init functions defs
# add separate support for finding all linux includes
LKM_REGEXES = [
    # ('lkm-header-include', 'include[^\n]*<linux\/kernel\.h>'),
    ('lkm-header-include', 'include[^\n]*<linux\/module\.h>'),
    ('lkm-make-flag', '\-DMODULE'),
    ('lkm-make-flag', '\_\_KERNEL\_\_'),
    ('lkm-license', 'MODULE_LICENSE.*\("(.*)"\);'),
    ('lkm-symbol', 'EXPORT_SYMBOL.*\("(.*)"\);'),
    ('lkm-symbol-gpl', 'EXPORT_SYMBOL_GPL.*\("(.*)"\);'),
]


def lkm_patterns():
    return [(key, re.compile(regex),) for key, regex in LKM_REGEXES]


def find_lkms(location):
    """
    Yield possible LKM-related clues found in file at location.
    """
    matches = finder.find(location, lkm_patterns())
    matches = finder.apply_filters(matches, finder.unique_filter)
    for key, lkm_clue, _line, _lineno in matches:
        yield key, lkm_clue
