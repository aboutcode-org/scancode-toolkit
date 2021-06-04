# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
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
