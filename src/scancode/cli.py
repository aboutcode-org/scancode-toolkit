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

from collections import OrderedDict
from functools import partial
import json
import os

import click

from commoncode import ignore, fileutils
from commoncode.fileutils import resource_iter

from scancode import __version__ as version
from scancode.api import as_html
from scancode.api import as_html_app
from scancode.api import create_html_app_assets
from scancode.api import extract_archives
from scancode.api import get_copyrights
from scancode.api import get_licenses
from scancode.api import HtmlAppAssetCopyWarning
from scancode.api import HtmlAppAssetCopyError
from scancode.api import get_file_infos


info_text = '''
ScanCode scans code and other files for origin and license.
Visit https://github.com/nexB/scancode-toolkit/ for support and download.
'''

# FIXME: we should load NOTICE instead
notice_text = '''
Software license
================

Copyright (c) 2015 nexB Inc. and others. All rights reserved.
http://nexb.com and https://github.com/nexB/scancode-toolkit/
The ScanCode software is licensed under the Apache License version 2.0.
Data generated with ScanCode require an acknowledgment.
ScanCode is a trademark of nexB Inc.

You may not use this software except in compliance with the License.
You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

When you publish or redistribute any data created with ScanCode or any ScanCode
derivative work, you must accompany this data with the following acknowledgment:
'''


acknowledgment_text = '''
  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
  ScanCode should be considered or used as legal advice. Consult an Attorney
  for any legal advice.
  ScanCode is a free software code scanning tool from nexB Inc. and others.
  Visit https://github.com/nexB/scancode-toolkit/ for support and download.
'''

acknowledgment_text_json = acknowledgment_text.strip().replace('  ', '')


extra_notice_text = '''

Third-party software licenses
=============================

ScanCode embeds third-party free and open source software packages under various
licenses including copyleft licenses. Some of the third-party software packages
are delivered as pre-built binaries. The origin and license of these packages is
documented by .ABOUT files.

The corresponding source code for pre-compiled third-party software is available
for immediate download from the same release page where you obtained ScanCode at:
https://github.com/nexB/scancode-toolkit/
or https://github.com/nexB/scancode-thirdparty-src/

You may also contact us to request the source code by email at info@nexb.com or
by postal mail at:
  nexB Inc., ScanCode open source code request
  735 Industrial Road, Suite #101, 94070 San Carlos, CA, USA
Please indicate in your communication the ScanCode version for which you are
requesting source code.


License for ScanCode datasets
=============================

ScanCode includes datasets (e.g. for license detection) that are dedicated
to the Public Domain using the Creative Commons CC0 1.0 Universal (CC0 1.0)
Public Domain Dedication: http://creativecommons.org/publicdomain/zero/1.0/
'''


def print_about(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(info_text + notice_text + acknowledgment_text + extra_notice_text)
    ctx.exit()


examples_text = '''
Scancode command lines examples:

(Note for Windows: use '\\' back slash instead of '/' forward slash for paths.)

Scan the 'samples' directory for licenses and copyrights. Save scan results to
an HTML app file for interactive scan results navigation. When the scan is done,
open 'scancode_result.html' in your web browser. Note that additional app files
are saved in a directory named 'scancode_result_files':

    scancode --format html-app samples/ scancode_result.html

Scan a directory for licenses and copyrights. Save scan results to an
HTML file:

    scancode --format html samples/zlib scancode_result.html

Scan a single file for copyrights. Print scan results on terminal as JSON:

    scancode --copyright samples/zlib/zlib.h

Scan a single file for licenses, print verbose progress on terminal as each file
is scanned. Save scan to a JSON file:

    scancode --license --verbose samples/zlib/zlib.h licenses.json

Scan a directory explicitly for licenses and copyrights. Redirect JSON scan
results to a file:

    scancode -f json -l -c samples/zlib/ > scan.json

Extract all archives found in the 'samples' directory tree:

    scancode --extract samples

Note: If an archive contains other archives, all contained archives will be
extracted recursively. Extraction is done directly in the 'samples' directory,
side-by-side with each archive. Files are extracted in a directory named after
the archive with an '-extract' suffix added to its name, created side-by-side
with the corresponding archive file.

Extract a single archive. Files are extracted in the directory
'samples/arch/zlib.tar.gz-extract/':

    scancode --extract samples/arch/zlib.tar.gz
'''


def print_examples(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(examples_text)
    ctx.exit()


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('ScanCode version ' + version)
    ctx.exit()


epilog_text = '''\b\bExamples (use --examples for more):

\b
Scan the 'samples' directory for licenses and copyrights.
Save scan results to a JSON file:

    scancode --format json samples scancode_result.json

\b
Scan the 'samples' directory for licenses and copyrights. Save scan results to
an HTML app file for interactive web browser results navigation. Additional app
files are saved to the 'myscan_files' directory:

    scancode --format html-app samples myscan.html

Note: when you run scancode, a progress bar is displayed with a counter of the
number of files processed. Use --verbose to display file-by-file progress.
'''


short_help = '''
Try 'scancode --help' for help on options and arguments.'''


formats = ['json', 'html', 'html-app']


class ScanCommand(click.Command):
    def get_usage(self, ctx):
        """
        Ensure that usage points to the --help option explicitly.
        Workaround click issue https://github.com/mitsuhiko/click/issues/393
        """
        return click.Command.get_usage(self, ctx) + short_help

    def main(self, args=None, prog_name=None, complete_var=None,
             standalone_mode=True, **extra):
        """
        Workaround click 4.0 bug https://github.com/mitsuhiko/click/issues/365
        """
        return click.Command.main(self, args=args, prog_name=self.name,
                                  complete_var=complete_var,
                                  standalone_mode=standalone_mode, **extra)


@click.command(name='scancode', epilog=epilog_text, cls=ScanCommand)
@click.pass_context
@click.argument('input', metavar='<input>', type=click.Path(exists=True, readable=True))
@click.argument('output_file', default='-', metavar='<output_file>', type=click.File('wb'))
@click.option('-c', '--copyright', is_flag=True, default=False, help='Scan <input> for copyrights. [default]')
@click.option('-l', '--license', is_flag=True, default=False, help='Scan <input> for licenses. [default]')
@click.option('-i', '--info', is_flag=True, default=False, help='Collect files information from  <input>.')
@click.option('-f', '--format', metavar='<style>', type=click.Choice(formats),
              default='json', show_default=True,
              help='Set <output_file> format <style> to one of: %s' % ' or '.join(formats),
              )
@click.option('-e', '--extract', is_flag=True, default=False, is_eager=True,
              help=('Extract any archives and compressed files found in <input> recursively, in-place, ignoring other scan options. Use this before scanning proper, as an <input> preparation step.'))
@click.option('--verbose', is_flag=True, default=False, help='Print verbose file-by-file progress messages.')
@click.help_option('-h', '--help')
@click.option('--examples', is_flag=True, is_eager=True, callback=print_examples,
              help=('Show command examples and exit.'))
@click.option('--about', is_flag=True, is_eager=True, callback=print_about,
              help=('Show information about ScanCode and licensing and exit.'))
@click.option('--version', is_flag=True, is_eager=True, callback=print_version,
              help=('Show the version and exit.'))
def scancode(ctx, input, output_file, extract, copyright, license, info, format, verbose, *args, **kwargs):  # @ReservedAssignment
    """scan the <input> file or directory for origin and license and save results to the <output_file>.

    The scan results are printed on terminal if <output_file> is not provided.
    """
    abs_input = os.path.abspath(os.path.expanduser(input))
    scans = [copyright, license, info]
    if extract:
        if any(scans):
            # exclusive, ignoring other options.
            # FIXME: this should turned into  a sub-command
            ctx.fail('''The '--extract' option cannot be combined with other scanning options.
Use the '--extract' option alone to extract archives found in  <input>.
then run scancode again to scan the extracted files.''')
            ctx.exit(1)

        click.secho('Extracting archives...', fg='green')
        extract_with_progress(abs_input, verbose)
        click.secho('Extracting done.', fg='green')
        return

    # Default scan when no options is provided
    if not any(scans):
        copyright = True  # @ReservedAssignment
        license = True  # @ReservedAssignment

    if copyright or license or info:
        click.secho('Scanning files...', fg='green')
        results = []

        ignored = partial(ignore.is_ignored, ignores=ignore.ignores_VCS, unignores={})
        files = resource_iter(abs_input, ignored=ignored)

        if not verbose:
            # only display a progress bar
            with click.progressbar(files, show_pos=True) as files:
                for input_file in files:
                    input_file = fileutils.as_posixpath(input_file)
                    results.append(scan_one(input_file, copyright, license, info, verbose))
        else:
            for input_file in files:
                input_file = fileutils.as_posixpath(input_file)
                results.append(scan_one(input_file, copyright, license, info, verbose))

        if format == 'html':
            output_file.write(as_html(results))

        elif format == 'html-app':
            output_file.write(as_html_app(results, input, output_file))
            try:
                create_html_app_assets(output_file)
            except HtmlAppAssetCopyWarning:
                click.secho('\nHTML app creation skipped when printing to terminal.',
                            fg='yellow')
            except HtmlAppAssetCopyError:
                click.secho('\nFailed to create HTML app.', fg='red')

        elif format == 'json':
            meta = OrderedDict()
            meta['scancode_notice'] = acknowledgment_text_json
            meta['scancode_version'] = version
            meta['resource_count'] = len(results)
            meta['results'] = results
            output_file.write(json.dumps(meta, indent=2))
        else:
            # This should never happen by construction
            raise Exception('Unknown format: ' + repr(format))
        click.secho('Scanning done.', fg='green')


def scan_one(input_file, copyright, license, info, verbose=False):  # @ReservedAssignment
    """
    Scan one file and return scanned data.
    """
    if verbose:
        click.secho('Scanning: %(input_file)s: ' % locals(), nl=False, fg='blue')
    data = OrderedDict()
    data['location'] = input_file
    if copyright:
        if verbose:
            click.secho('copyrights. ', nl=False, fg='green')
        data['copyrights'] = list(get_copyrights(input_file))
    if license:
        if verbose:
            click.secho('licenses. ', nl=False, fg='green')
        data['licenses'] = list(get_licenses(input_file))
    if info:
        if verbose:
            click.secho('infos. ', nl=False, fg='green')
        data['infos'] = get_file_infos(input_file)

    if verbose:
        click.secho('', nl=True)
    return data


def extract_with_progress(input, verbose=False):  # @ReservedAssignment
    """
    Extract archives and display progress.
    """
    if verbose:
        for xev in extract_archives(input, verbose=verbose):
            if not xev.done:
                click.secho('Extracting: ' + xev.source + ': ', nl=False, fg='green')
            else:
                if xev.warnings or xev.errors:
                    click.secho('done.', fg='red' if xev.errors else 'yellow')
                    display_extract_event(xev)
                else:
                    click.secho('done.', fg='green')
    else:
        extract_results = []
        # only display a progress bar
        with click.progressbar(extract_archives(input, verbose=verbose), show_pos=True) as extractions:
            for xevent in extractions:
                extract_results.append(xevent)
        # display warnings/errors at the end
        for xev in extract_results:
            if xev.warnings or xev.errors:
                if xev.warnings or xev.errors:
                    click.secho('Extracting: ' + xev.source + ': ', nl=False, fg='green')
                    click.secho('done.', fg='red' if xev.errors else 'yellow')
                    display_extract_event(xev)


def display_extract_event(xev):
    for e in xev.errors:
        click.secho('  ERROR: ' + e, fg='red')
    for warn in xev.warnings:
        click.secho('  WARNING: ' + warn, fg='yellow')
