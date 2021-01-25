#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#
# Visit https://aboutcode.org and https://github.com/nexB/scancode-toolkit for
# support and download. ScanCode is a trademark of nexB Inc.
#
# The ScanCode software is licensed under the Apache License version 2.0.
# The ScanCode open data is licensed under CC-BY-4.0.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
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

