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

from __future__ import print_function, absolute_import

import os

import click

from scancode.cli import version
from scancode.cli import print_about

from scancode.api import extract_archives
from scancode.utils import BaseCommand
from commoncode import fileutils
from scancode import utils
from click.termui import style
from commoncode.fileutils import as_posixpath


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.secho('ScanCode extractcode version ' + version)
    ctx.exit()


epilog_text = '''\b\bExamples:

(Note for Windows: use '\\' backslash instead of '/' slash for paths.)

\b
Extract all archives found in the 'samples' directory tree:

    extractcode samples

Note: If an archive contains other archives, all contained archives will be
extracted recursively. Extraction is done directly in the 'samples' directory,
side-by-side with each archive. Files are extracted in a directory named after
the archive with an '-extract' suffix added to its name, created side-by-side
with the corresponding archive file.

\b
Extract a single archive. Files are extracted in the directory
'samples/arch/zlib.tar.gz-extract/':

    extractcode samples/arch/zlib.tar.gz
'''


class ExtractCommand(BaseCommand):
    short_usage_help = '''
Try 'extractcode --help' for help on options and arguments.'''


@click.command(name='extractcode', epilog=epilog_text, cls=ExtractCommand)
@click.pass_context

@click.argument('input', metavar='<input>', type=click.Path(exists=True, readable=True))

@click.option('--verbose', is_flag=True, default=False, help='Print verbose file-by-file progress messages.')
@click.option('--quiet', is_flag=True, default=False, help='Do not print any progress message.')

@click.help_option('-h', '--help')
@click.option('--about', is_flag=True, is_eager=True, callback=print_about, help='Show information about ScanCode and licensing and exit.')
@click.option('--version', is_flag=True, is_eager=True, callback=print_version, help='Show the version and exit.')

def extractcode(ctx, input, verbose, quiet, *args, **kwargs):  # @ReservedAssignment
    """extract archives and compressed files found in the <input> file or directory tree.

    Use this command before scanning proper, as an <input> preparation step.
    Archives found inside an extracted archive are extracted recursively.
    Extraction is done in-place in a directory named '-extract' side-by-side with an archive.
    """

    original_input = fileutils.as_posixpath(input)
    abs_input = fileutils.as_posixpath(os.path.abspath(os.path.expanduser(input)))

    # note: we inline functions so they can close on local variables

    def extract_start():
        return style('Extracting archives...', fg='green')


    def extract_event(item):
        """
        Display an extract event.
        """
        if not item:
            return ''
        if verbose:
            if item.done:
                return ''
            line = utils.get_relative_path(original_input, abs_input, as_posixpath(item.source)) or ''
        else:
            line = fileutils.file_name(item.source) or ''
        return 'Extracting: %(line)s' % locals()


    def extract_end():
        """
        Display a summary of warnings and errors if any.
        """
        has_warnings = False
        has_errors = False
        summary = []
        for xev in extract_results:
            has_errors = has_errors or bool(xev.errors)
            has_warnings = has_warnings or bool(xev.warnings)
            source = as_posixpath(xev.source)
            source = utils.get_relative_path(original_input, abs_input, source)
            for e in xev.errors:
                summary.append(style('ERROR extracting: %(source)s: %(e)r' % locals(), fg='red', reset=False))
            for warn in xev.warnings:
                summary.append(style('WARNING extracting: %(source)s: %(warn)r' % locals(), fg='yellow', reset=False))

        summary_color = 'green'
        if has_warnings:
            summary_color = 'yellow'
        if has_errors:
            summary_color = 'red'

        summary.append(style('Extracting done.', fg=summary_color, reset=True))
        return '\n'.join(summary)


    extract_results = []
    has_extract_errors = False

    with utils.progressmanager(extract_archives(abs_input),
                               item_show_func=extract_event,
                               start_show_func=extract_start,
                               finish_show_func=extract_end,
                               verbose=verbose,
                               quiet=quiet,
                               ) as extraction_events:
        for xev in extraction_events:
            if xev.done and (xev.warnings or xev.errors):
                has_extract_errors = has_extract_errors or xev.errors
                extract_results.append(xev)

    rc = 1 if has_extract_errors else 0
    ctx.exit(rc)
