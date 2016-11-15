#
# Copyright (c) 2016 nexB Inc. and others. All rights reserved.
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

from __future__ import print_function, absolute_import, division


###########################################################################
# Monkeypatch Pool iterators so that Ctrl-C interrupts everything properly
# based from https://gist.github.com/aljungberg/626518
# FIXME: unknown license
###########################################################################
from multiprocessing.pool import IMapIterator, IMapUnorderedIterator

def wrapped(func):
    def wrap(self, timeout=None):
        return func(self, timeout=timeout or 1e10)
    return wrap

IMapIterator.next = wrapped(IMapIterator.next)
IMapIterator.__next__ = IMapIterator.next
IMapUnorderedIterator.next = wrapped(IMapUnorderedIterator.next)
IMapUnorderedIterator.__next__ = IMapUnorderedIterator.next

from multiprocessing import Pool
###########################################################################


from collections import OrderedDict
from functools import partial
import os
from os.path import expanduser
from os.path import abspath
import sys
import traceback
from types import GeneratorType

import click
from click.termui import style
import simplejson as json
from time import time

from commoncode import ignore
from commoncode import fileutils
from commoncode import filetype

from scancode import __version__ as version

from scancode.interrupt import interruptible
from scancode.interrupt import time_and_ram_interruptible
from scancode import utils

from scancode.cache import get_scans_cache_class

from scancode.format import as_template
from scancode.format import as_html_app
from scancode.format import create_html_app_assets
from scancode.format import HtmlAppAssetCopyWarning
from scancode.format import HtmlAppAssetCopyError

from scancode.api import get_copyrights
from scancode.api import get_emails
from scancode.api import get_file_infos
from scancode.api import get_licenses
from scancode.api import get_package_infos
from scancode.api import get_urls


info_text = '''
ScanCode scans code and other files for origin and license.
Visit https://github.com/nexB/scancode-toolkit/ for support and download.
'''

# FIXME: we should load NOTICE instead
notice_text = '''
Software license
================

Copyright (c) 2016 nexB Inc. and others. All rights reserved.
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

To extract archives, see the 'extractcode' command instead.
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


class ScanCommand(utils.BaseCommand):
    short_usage_help = '''
Try 'scancode --help' for help on options and arguments.'''


formats = ('json', 'html', 'html-app',)

def validate_formats(ctx, param, value):
    value_lower = value.lower()
    if value_lower in formats:
        return value_lower
    # render using a user-provided custom format template
    if not os.path.isfile(value):
        raise click.BadParameter('Invalid template file: "%(value)s" does not exists or is not readable.' % locals())
    return value

@click.command(name='scancode', epilog=epilog_text, cls=ScanCommand)
@click.pass_context

@click.argument('input', metavar='<input>', type=click.Path(exists=True, readable=True))
@click.argument('output_file', default='-', metavar='<output_file>', type=click.File('wb'))

@click.option('-c', '--copyright', is_flag=True, default=False, help='Scan <input> for copyrights. [default]')
@click.option('-l', '--license', is_flag=True, default=False, help='Scan <input> for licenses. [default]')
@click.option('-p', '--package', is_flag=True, default=False, help='Scan <input> for packages. [default]')
@click.option('--email', is_flag=True, default=False, help='Scan <input> for emails.')
@click.option('--url', is_flag=True, default=False, help='Scan <input> for urls.')
@click.option('-i', '--info', is_flag=True, default=False, help='Scan <input> for files information.')
@click.option('--license-score', is_flag=False, default=0, type=int, show_default=True,
              help='Matches with scores lower than this score are not returned. A number between 0 and 100.')

@click.option('-f', '--format', is_flag=False, default='json', show_default=True, metavar='<style>',
              help=('Set <output_file> format <style> to one of the standard formats: %s '
                    'or the path to a custom template' % ' or '.join(formats)),
              callback=validate_formats)
@click.option('--verbose', is_flag=True, default=False, help='Print verbose file-by-file progress messages.')
@click.option('--quiet', is_flag=True, default=False, help='Do not print any progress message.')
@click.option('-n', '--processes', is_flag=False, default=1, type=int, help='Scan <input> using n parallel processes.')

@click.help_option('-h', '--help')
@click.option('--examples', is_flag=True, is_eager=True, callback=print_examples, help=('Show command examples and exit.'))
@click.option('--about', is_flag=True, is_eager=True, callback=print_about, help='Show information about ScanCode and licensing and exit.')
@click.option('--version', is_flag=True, is_eager=True, callback=print_version, help='Show the version and exit.')

def scancode(ctx, input, output_file, copyright, license, package,
             email, url, info, license_score, format, verbose, quiet, processes,
             *args, **kwargs):
    """scan the <input> file or directory for origin clues and license and save results to the <output_file>.

    The scan results are printed on terminal if <output_file> is not provided.
    """
    possible_scans = [copyright, license, package, email, url, info]
    # Default scan when no options is provided
    if not any(possible_scans):
        copyright = True
        license = True
        package = True

    scans_cache_class = get_scans_cache_class()
    try:
        to_stdout = output_file == sys.stdout

        files_count, results = scan(input, copyright, license, package, email, url, info, license_score,
                                    verbose, quiet, processes, scans_cache_class, to_stdout)
        save_results(files_count, results, format, input, output_file)
    finally:
        # cleanup
        cache = scans_cache_class()
        cache.clear()


def scan(input_path, copyright=True, license=True, package=True,
         email=False, url=False, info=True, license_score=0,
         verbose=False, quiet=False, processes=1,
         scans_cache_class=None, to_stdout=False):
    """
    Return a tuple of (file_count, indexing_time, scan_results) where
    scan_results is an iterable. Run each requested scan proper: each individual file
    scan is cached on disk to free memory. Then the whole set of scans is loaded from
    the cache and streamed at the end.
    """
    assert scans_cache_class
    scan_summary = OrderedDict()
    scan_summary['scanned_path'] = input_path
    scan_summary['processes'] = processes
    get_licenses_with_score = partial(get_licenses, min_score=license_score)

    # note: "flag and function" expressions return the function if flag is True
    # note: the order of the scans matters to show things in logical order
    scanners = OrderedDict([
        ('licenses' , license and get_licenses_with_score),
        ('copyrights' , copyright and get_copyrights),
        ('packages' , package and get_package_infos),
        ('emails' , email and get_emails),
        ('urls' , url and get_urls),
    ])

    # Display scan start details
    ############################
    scans = info and ['infos'] or []
    scans.extend([k for k, v in scanners.items() if v])
    _scans = ', '.join(scans)
    click.secho('Scanning files for: %(_scans)s with %(processes)d processes...' % locals(), err=to_stdout)

    scan_summary['scans'] = scans[:]
    scan_start = time()
    indexing_time = 0
    if license:
        # build index outside of the main loop
        click.secho('Building license detection index...', err=to_stdout, fg='green')
        from licensedcode.index import get_index
        get_index()
        indexing_time = time() - scan_start

    scan_summary['indexing_time'] = indexing_time

    # TODO: handle pickling errors as in ./scancode -cilp   samples/ -n3: note they are only caused by the FanoutCache
    # TODO: handle other exceptions properly to avoid any hanging

    # maxtasksperchild helps with recycling processes in case of leaks
    pool = Pool(processes=processes, maxtasksperchild=1000)
    resources = resource_paths(input_path)
    scanit = partial(_scanit, scanners=scanners, scans_cache_class=scans_cache_class)
    # chunksize is documented as much more efficient.
    # Yet 1 still provides a more progressive feedback
    # results are returned as soon as ready out of order
    scanned_files = pool.imap_unordered(scanit, resources, chunksize=1)

    def scan_event(item):
        """Progress event displayed each time a file is scanned"""
        if item:
            _scan_success, _scanned_path = item
            _progress_line = verbose and _scanned_path or fileutils.file_name(_scanned_path)
            return style('Scanning: ') + style(_progress_line, fg=_scan_success and 'green' or 'red')

    scanning_errors = []
    files_count = 0
    with utils.progressmanager(scanned_files, item_show_func=scan_event, show_pos=True, verbose=verbose, quiet=quiet) as scanned:
        while True:
            try:
                result = scanned.next()
                scan_sucess, scanned_rel_path = result
                if not scan_sucess:
                    scanning_errors.append(scanned_rel_path)
                files_count += 1
            except StopIteration:
                break
            except KeyboardInterrupt:
                print('\nAborted!')
                pool.terminate()
                break

    # Compute stats
    ##########################
    scan_summary['files_count'] = files_count
    scan_summary['files_with_errors'] = scanning_errors
    total_time = time() - scan_start
    scanning_time = total_time - indexing_time
    scan_summary['total_time'] = total_time
    scan_summary['scanning_time'] = scanning_time
    files_scanned_per_second = round(float(files_count) / scanning_time , 2)
    scan_summary['files_scanned_per_second'] = files_scanned_per_second

    # Display stats
    ##########################
    click.secho('Scanning done.' % locals(), fg=scanning_errors and 'red' or 'green', err=to_stdout)
    if scanning_errors:
        click.secho('Some files failed to scan:', fg='red', err=to_stdout)
        for errored_path in scanning_errors:
            click.secho(' ' + errored_path, fg='red', err=to_stdout)

    click.secho('Scan statistics: %(files_count)d files scanned in %(total_time)ds.' % locals(), err=to_stdout)
    click.secho('Scan options:    %(_scans)s with %(processes)d processe(s).' % locals(), err=to_stdout)
    click.secho('Scanning speed:  {:.2} files per sec.'.format(files_scanned_per_second), err=to_stdout)
    click.secho('Scanning time:   %(scanning_time)ds.' % locals(), err=to_stdout, reset=True,)
    click.secho('Indexing time:   %(indexing_time)ds.' % locals(), err=to_stdout)

    # finally return an iterator on cached results
    cached_scan = scans_cache_class()
    return files_count, cached_scan.iterate(with_infos=info)


TEST_TIMEOUT = 0
MAX_SCAN_TIMEOUT = 600

TEST_MAX_MEMORY = 0 #1024 * 1024 * 1024 * 80  # 100MB
MAX_SCAN_MEMORY = 1024 * 1024 * 1024 * 1024  # 1GB

SCANCODE_EXPERIMENTAL_MAX_MEMORY = os.environ.get('SCANCODE_EXPERIMENTAL_MAX_MEMORY', False)


def scan_timeout(size):
    """
    Return a scan timeout in seconds computed based on a file size.
    """
    # at least 60 seconds
    timeout = 60
    if size > 1024 * 1024 * 1024:
        # add extra seconds for each megabyte
        timeout += (size / 1024 * 1024 * 1024) * 30

    timeout = min((timeout, MAX_SCAN_TIMEOUT))
    return timeout


def scan_max_memory(size):
    """
    Return a scan not-to-exceed maximum memory in bytes computed based on a file size.
    """

    max_memory = 1024 * 1024 * 1024 * 700  # 700MB
    if size > 1024 * 1024 * 1024:
        # add extra quota for each byte: 5x
        max_memory += size * 5

    max_memory = min((max_memory, MAX_SCAN_MEMORY))
    return max_memory


def _scanit(paths, scanners, scans_cache_class):
    """
    Run scans and cache results. Used as an execution unit for parallel processing.
    Return True on success, False on error.
    """
    abs_path, rel_path = paths
    # always fetch infos and cache.
    infos = scan_infos(abs_path)
    scans_cache = None
    success = True
    try:
        # build a local instance of a cache
        scans_cache = scans_cache_class()
        is_cached = scans_cache.put_infos(rel_path, infos)

        # Skip other scans if already cached
        # ENSURE we only do tghis for files not directories
        if not is_cached:
            # run the scan as an interruptiple task
            scans_runner = partial(scan_one, abs_path, scanners)

            file_size = infos.get('size', 0)
            # use TEST_TIMEOUT for tests if provided
            timeout = TEST_TIMEOUT or scan_timeout(file_size)
            # feature switch
            if SCANCODE_EXPERIMENTAL_MAX_MEMORY:
                # use TEST_MAX_MEMORY for tests if provided
                max_memory = TEST_MAX_MEMORY or scan_max_memory(file_size)
                success, scan_result = time_and_ram_interruptible(scans_runner, timeout=timeout, max_memory=max_memory)
            else: 
                success, scan_result = interruptible(scans_runner, timeout=timeout)                
            if not success:
                # Use scan errors as the scan result for that file on failure
                scan_result = dict(scan_errors=[scan_result, ''])
            scans_cache.put_scan(rel_path, infos, scan_result)

            # do not report success if some other errors happened
            if scan_result.get('scan_errors'):
                success = False
    finally:
        if scans_cache:
            scans_cache.close()

    return success, rel_path


def resource_paths(input_path):
    """
    Yield tuples of (absolute path, base_path-relative path) for all the files found
    at absolute_path (either a directory or file) given a base_path (used for
    relative path resolution). Only yield Files, not directories. All outputs are
    POSIX paths.
    """
    base_path = os.path.abspath(os.path.normpath(os.path.expanduser(input_path)))
    base_is_dir = filetype.is_dir(base_path)
    len_base_path = len(base_path)
    ignored = partial(ignore.is_ignored, ignores=ignore.ignores_VCS, unignores={})
    resources = fileutils.resource_iter(base_path, ignored=ignored)

    for abs_path in resources:
        # fix paths: keep the path as relative to the original base_path
        rel_path = utils.get_relative_path(abs_path, len_base_path, base_is_dir)
        yield abs_path, rel_path


def scan_infos(input_file):
    """
    Scan one file or directory and return file_infos data.
    This always contains an extra 'errors' key with a list of error messages,
    possibly empty.
    """
    infos = OrderedDict()
    errors = []
    try:
        infos = get_file_infos(input_file, as_list=False)
    except Exception, e:
        # never fail but instead add an error message.
        errors = dict(infos=(e.message, traceback.format_exc(),))
    # put errors last
    infos['scan_errors'] = errors
    return infos


def scan_one(input_file, scans):
    """
    Scan one file or directory and return a scanned data, calling every scan in
    the `scans` mapping of (scan name -> scan function). This may contain an
    'errors' key with a list of error messages.
    """
    scan_result = OrderedDict()
    errors = []
    for scan_name, scan_func in scans.items():
        if not scan_func:
            continue
        scan_errors = dict()
        try:
            scan_details = scan_func(input_file)
            # consume generators
            if isinstance(scan_details, GeneratorType):
                scan_details = list(scan_details)
            scan_result[scan_name] = scan_details
        except Exception, e:
            # never fail but instead add an error message and keep an empty scan:
            scan_result[scan_name] = []
            scan_errors[scan_name] = (e.message, traceback.format_exc(),)
            errors.append(scan_errors)
    # put errors last
    scan_result['scan_errors'] = errors
    return scan_result


def save_results(files_count, scanned_files, format, input, output_file):
    """
    Save results to file or screen.
    """
    if output_file != sys.stdout:
        parent_dir = os.path.dirname(output_file.name)
        if parent_dir:
            fileutils.create_dir(abspath(expanduser(parent_dir)))

    if format and format not in formats:
        # render using a user-provided custom format template
        if not os.path.isfile(format):
            click.secho('\nInvalid template passed.', err=True, fg='red')
        else:
            output_file.write(as_template(scanned_files, template=format))

    elif format == 'html':
        output_file.write(as_template(scanned_files))

    elif format == 'html-app':
        output_file.write(as_html_app(input, output_file))
        try:
            create_html_app_assets(scanned_files, output_file)
        except HtmlAppAssetCopyWarning:
            click.secho('\nHTML app creation skipped when printing to terminal.',
                       err=True, fg='yellow')
        except HtmlAppAssetCopyError:
            click.secho('\nFailed to create HTML app.', err=True, fg='red')

    elif format == 'json':
        meta = OrderedDict()
        meta['scancode_notice'] = acknowledgment_text_json
        meta['scancode_version'] = version
        meta['files_count'] = files_count
        # TODO: add scanning options to meta
        meta['files'] = scanned_files
        # json.dump(meta, output_file, indent=2)
        json.dump(meta, output_file, indent=2 * ' ', iterable_as_array=True)
        output_file.write('\n')
    else:
        raise Exception('unknown format')
