#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import click


@click.command(name='scancode-reindex-licenses')
@click.option(
    '--all-languages',
    is_flag=True,
    help='[EXPERIMENTAL] Rebuild the license index including texts all '
            'languages (and not only English) and exit.',
)
@click.option(
    '--additional-directory',
    type=click.Path(exists=True, readable=True, file_okay=False, resolve_path=True, path_type=str),
    metavar='DIR',
    help='Include this directory with additional custom licenses and license rules '
            'in the license detection index.',
)
@click.help_option('-h', '--help')
def reindex_licenses(
    all_languages,
    additional_directory,
    *args,
    **kwargs,
):
    """Reindex scancode licenses and exit"""

    from licensedcode.cache import get_index
    click.echo('Rebuilding the license index...')
    get_index(force=True, index_all_languages=bool(all_languages), additional_directory=additional_directory)
    click.echo('Done.')


if __name__ == '__main__':
    reindex_licenses()
