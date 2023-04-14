#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import click

from commoncode.cliutils import PluggableCommandLineOption
from licensedcode.models import load_dump_licenses

@click.command(name='scancode-reindex-licenses')
@click.option(
    '--all-languages',
    is_flag=True,
    help='[EXPERIMENTAL] Rebuild the license index including texts all '
            'languages (and not only English) and exit.',
    cls=PluggableCommandLineOption,
)
@click.option(
    '--only-builtin',
    is_flag=True,
    help='Rebuild the license index excluding any additional '
         'license directory or additional license plugins which '
         'were added previously, i.e. with only builtin scancode '
         'license and rules.',
    conflicting_options=['additional_directory'],
    cls=PluggableCommandLineOption,
)
@click.option(
    '--load-dump',
    is_flag=True,
    help='Load all the license objects from file and then dump '
         'them back to their respective license files.',
    cls=PluggableCommandLineOption,
)
@click.option(
    '--additional-directory',
    type=click.Path(exists=True, readable=True, file_okay=False, resolve_path=True, path_type=str),
    metavar='DIR',
    help='Include this directory with additional custom licenses and license rules '
            'in the license detection index.',
    conflicting_options=['only_builtin'],
    cls=PluggableCommandLineOption,
)
@click.help_option('-h', '--help')
def reindex_licenses(
    only_builtin,
    all_languages,
    additional_directory,
    load_dump,
    *args,
    **kwargs,
):
    """Reindex scancode licenses and exit"""

    from licensedcode.cache import get_index
    click.echo('Rebuilding the license index...')
    if load_dump:
        load_dump_licenses()
    get_index(
        only_builtin=only_builtin,
        force=True,
        index_all_languages=bool(all_languages),
        additional_directory=additional_directory
    )
    click.echo('Done.')


if __name__ == '__main__':
    reindex_licenses()
