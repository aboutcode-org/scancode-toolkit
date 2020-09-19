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

from itertools import chain

import click


class FileOptionType(click.File):
    """
    A click.File subclass that ensures that a file name is not set to an
    existing option parameter to avoid mistakes.
    """

    def convert(self, value, param, ctx):
        known_opts = set(chain.from_iterable(
            p.opts for p in ctx.command.params if isinstance(p, click.Option)))
        if value in known_opts:
            self.fail(
                'Illegal file name conflicting with an option name: %s. '
                'Use the special "-" file name to print results on screen/stdout.'
                % (click.types.filename_to_ui(value),
            ), param, ctx)
        return click.File.convert(self, value, param, ctx)

