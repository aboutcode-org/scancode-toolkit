# -*- coding: utf-8 -*-
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


import click

from licensedcode import cache
from licensedcode import models


"""
Update licenses and rules with ignorable copyrights, URLs and emails.
"""


def refresh_ignorables(licensishes):
    for i, lic in enumerate(sorted(licensishes)):
        print(i, end=' ')
        lic = models.update_ignorables(lic, verbose=True)
        lic.dump()


class _Nothing(object):
    pass



@click.command()
@click.argument('path',
    nargs=-1,
    type=click.Path(exists=False, allow_dash=False),
    metavar='PATH')


@click.help_option('-h', '--help')
def cli(path=(), update=True):
    """
    Update licenses and rules with ignorable copyrights, holders, authors URLs
    and emails.
    """
    licensish = list(cache.get_licenses_db().values()) + list(models.load_rules())

    if path:
        licensish = [l for l in licensish
            if l.text_file.endswith(path) or l.data_file.endswith(path)]
    refresh_ignorables(licensish)


if __name__ == '__main__':
    cli()
