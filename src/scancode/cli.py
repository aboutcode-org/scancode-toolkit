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

import json

import click

from commoncode.fileutils import file_walk

from scancode import __version__ as version
from scancode.api import as_html
from scancode.api import as_html_app
from scancode.api import create_html_app_assets
from scancode.api import get_extract
from scancode.api import get_copyrights
from scancode.api import get_licenses
from scancode.api import HtmlAppAssetCopyWarning
from scancode.api import HtmlAppAssetCopyError
import textwrap


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
    click.echo(info_text + notice_text + acknowledgment_text +extra_notice_text)
    ctx.exit()


examples_text = '''
Scancode command lines examples:

(Note for Windows: use '\' backward slashes instead of '/' forward slashes.)

Scan a directory for licenses and copyrights. Save scan results to an HTML app
file for interactive scan results navigation. Additional app files are saved in
the directory 'scancode_result_files':
    scancode --format html-app mydir/ scancode_result.html

Scan a directory for licenses and copyrights (default). Save scan results to an
HTML file:
    scancode --format html mydir/ scancode_result.html

Scan a single file for copyrights. Print scan results on terminal as JSON:
    scancode -copyright myfile.c

Scan a directory for licenses and copyrights. Redirect scan results to a file:
    scancode -f json code-dir > scan.json

Scan a single file for licenses. Save scan to a JSON file:
    scancode -l myfile.c licenses.json

Extract all archives found in the 'mydir' directory tree.
    scancode --extract mydir
Note: The extraction is recursive: if an archive contains other archives, all
will be extracted. Extraction is performed directly in 'mydir', side-by-side
with each archive. Files are extracted in a directory named after the archive
with an '-extract' suffix added. This directory is created side-by-side with
each archive file.

Extract a single archive. Files are extracted in the directory
'mydir/zlib-1.2.8.tar.gz-extract/':
    scancode --extract mydir/zlib-1.2.8.tar.gz
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
Scan 'mydir' directory for licenses and copyrights. Save scan results to a JSON file:

    scancode --format json mydir scancode_result.json

\b
Scan 'mydir' directory for licenses and copyrights. Save scan results to an
HTML app file for interactive web browser results navigation. Additional app
files are saved to the 'myscan_files' directory:

    scancode --format html-app mydir myscan.html
'''


formats = ['json', 'html', 'html-app']

class ScanCommand(click.Command):
    """
    Workaround click 4.0 bug https://github.com/mitsuhiko/click/issues/365
    """
    def get_usage(self, ctx):
        formatted = '''Usage: scancode [OPTIONS] <input> <output_file>
Try 'scancode --help' for more information'''
        return formatted


@click.command(name='scancode', epilog=epilog_text, cls=ScanCommand)
@click.argument('input', metavar='<input>', type=click.Path(exists=True, readable=True))
@click.argument('output_file', default='-', metavar='<output_file>', type=click.File('wb'))
@click.option('-c', '--copyright', is_flag=True, default=False, help='Scan <input> for copyrights. [default]')
@click.option('-l', '--license', is_flag=True, default=False, help='Scan <input> for licenses. [default]')
@click.option('-f', '--format', metavar='<style>', type=click.Choice(formats),
              default='json', show_default=True,
              help='Set format <style> to one of: %s' % '|'.join(formats),
              )
@click.option('-e', '--extract', is_flag=True, default=False, is_eager=True,
              help=('Extract archives found in <input> recursively, ignoring other options.'))
@click.help_option('-h', '--help')
@click.option('--examples', is_flag=True, is_eager=True, callback=print_examples,
              help=('Show command examples and exit.'))
@click.option('--about', is_flag=True, is_eager=True, callback=print_about,
              help=('Show ScanCode and licensing information and exit.'))
@click.option('--verbose', is_flag=True, default=False, help='Show verbose scan progress messages.')
@click.option('--version', is_flag=True, is_eager=True, callback=print_version,
              help=('Show the version and exit.'))
def scancode(input, output_file, extract, copyright, license, format, verbose, *args, **kwargs):
    """scan the <input> file or directory for origin and license and save results to the <output_file>.

    The scan results are printed on terminal if <output_file> is not provided.
    """
    if extract:
        click.secho('Extracting archives...', fg='green')
        extract_errors = get_extract(input)
        if extract_errors:
            # FIXME: Provide a better way to report errors and we need to report progress
            click.secho('\n'.join(extract_errors), fg='red')
        click.secho('Extracting done.', fg='green')
        # exclusive, ignoring other options.
        return

    # Default scan when no options is provided
    if not any((copyright, license)):
        copyright = True
        license = True

    if copyright or license:
        click.secho('Scanning files...', fg='green')
        results = []

        if not verbose:
            # only display a progress bar
            with click.progressbar(file_walk(input), show_pos=True) as files:
                for input_file in files:
                    results.append(scan_one(input_file,copyright, license, verbose))
        else:
            for input_file in file_walk(input):
                results.append(scan_one(input_file, copyright, license, verbose))

        if format == 'html':
            output_file.write(as_html(results))

        elif format == 'html-app':
            output_file.write(as_html_app(results, input, output_file))
            try:
                create_html_app_assets(output_file)
            except HtmlAppAssetCopyWarning:
                click.secho('\nHTML app creation skipped when printing to terminal.', fg='yellow')
            except HtmlAppAssetCopyError:
                click.secho('\nFailed to create HTML app.', fg='red')

        elif format == 'json':
            meta = {
                'count': len(results),
                'notice': acknowledgment_text_json,
                'results': results,
                'version': version,
            }
            output_file.write(json.dumps(meta, indent=2, sort_keys=True))
        else:
            # This should never happen by construction
            raise Exception('Unknown format: ' + repr(format))
        click.secho('Scanning done.', fg='green')


def scan_one(input_file, copyright, license, verbose=False):
    """
    Scan one file and return scanned data.
    """
    if verbose:
        click.secho('Scanning: %(input_file)s: ' % locals(), nl=False, fg='blue')
    data = {'location': input_file}
    if copyright:
        if verbose:
            click.secho('copyrights. ', nl=False, fg='green')
        data['copyrights'] = list(get_copyrights(input_file))
    if license:
        if verbose:
            click.secho('licenses. ', nl=False, fg='green')
        data['licenses'] = list(get_licenses(input_file))
    if verbose:
        click.secho('', nl=True)
    return data
