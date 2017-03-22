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
from __future__ import division
from __future__ import unicode_literals

# Import early because this import has monkey-patching side effects
from scancode.pool import get_pool


from collections import OrderedDict
from functools import partial
import os
from os.path import expanduser
from os.path import abspath
import sys
from time import time
import traceback
from types import GeneratorType

import click
from click.termui import style

from commoncode import filetype
from commoncode import fileutils
from commoncode import ignore

from scancode import __version__ as version

from scancode.api import get_copyrights
from scancode.api import get_emails
from scancode.api import get_file_infos
from scancode.api import get_licenses
from scancode.api import get_package_infos
from scancode.api import get_urls
from scancode.api import _empty_file_infos

from scancode.cache import ScanFileCache
from scancode.cache import get_scans_cache_class

from formattedcode.writers import write_formatted_output
from formattedcode.format import as_template

from scancode.interrupt import interruptible
from scancode.interrupt import DEFAULT_TIMEOUT

from scancode import utils

echo_stderr = partial(click.secho, err=True)


info_text = '''
ScanCode scans code and other files for origin and license.
Visit https://github.com/nexB/scancode-toolkit/ for support and download.

'''

notice_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'NOTICE')
notice_text = open(notice_path).read()

delimiter = '\n\n\n'
[notice_text, extra_notice_text] = notice_text.split(delimiter, 1)
extra_notice_text = delimiter + extra_notice_text

delimiter = '\n\n  '
[notice_text, acknowledgment_text] = notice_text.split(delimiter, 1)
acknowledgment_text = delimiter + acknowledgment_text

notice = acknowledgment_text.strip().replace('  ', '')


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

Scan a single file for copyrights. Print scan results to stdout as JSON:

    scancode --copyright samples/zlib/zlib.h

Scan a single file for licenses, print verbose progress to stderr as each
file is scanned. Save scan to a JSON file:

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


formats = ('json', 'json-pp', 'html', 'html-app', 'spdx-tv', 'spdx-rdf')

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
@click.argument('output_file', default='-', metavar='<output_file>', type=click.File('w', encoding='utf-8'))

# Note that click's 'default' option is set to 'false' here despite these being documented to be enabled by default in
# order to more elegantly enable all of these (see code below) if *none* of the command line options are specified.
@click.option('-c', '--copyright', is_flag=True, default=False, help='Scan <input> for copyrights. [default]')
@click.option('-l', '--license', is_flag=True, default=False, help='Scan <input> for licenses. [default]')
@click.option('-p', '--package', is_flag=True, default=False, help='Scan <input> for packages. [default]')

@click.option('-e', '--email', is_flag=True, default=False, help='Scan <input> for emails.')
@click.option('-u', '--url', is_flag=True, default=False, help='Scan <input> for urls.')
@click.option('-i', '--info', is_flag=True, default=False, help='Include information such as size, type, etc.')

@click.option('--license-score', is_flag=False, default=0, type=int, show_default=True,
              help='Do not return license matches with scores lower than this score. A number between 0 and 100.')
@click.option('--license-text', is_flag=True, default=False,
              help='Include the detected licenses matched text. Has no effect unless --license is requested.')
@click.option('--only-findings', is_flag=True, default=False,
              help='Only return files or directories with findings for the requested scans. Files without findings are omitted.')
@click.option('--strip-root', is_flag=True, default=False,
              help='Strip the root directory segment of all paths. The default is to always '
                   'include the last directory segment of the scanned path such that all paths have a common root directory.')

@click.option('-f', '--format', is_flag=False, default='json', show_default=True, metavar='<style>',
              help=('Set <output_file> format <style> to one of the standard formats: %s '
                    'or the path to a custom template' % ' or '.join(formats)),
              callback=validate_formats)
@click.option('--verbose', is_flag=True, default=False, help='Print verbose file-by-file progress messages.')
@click.option('--quiet', is_flag=True, default=False, help='Do not print summary or progress messages.')
@click.option('-n', '--processes', is_flag=False, default=1, type=int, show_default=True, help='Scan <input> using n parallel processes.')

@click.help_option('-h', '--help')
@click.option('--examples', is_flag=True, is_eager=True, callback=print_examples, help=('Show command examples and exit.'))
@click.option('--about', is_flag=True, is_eager=True, callback=print_about, help='Show information about ScanCode and licensing and exit.')
@click.option('--version', is_flag=True, is_eager=True, callback=print_version, help='Show the version and exit.')

@click.option('--diag', is_flag=True, default=False, help='Include additional diagnostic information such as error messages or result details.')
@click.option('--timeout', is_flag=False, default=DEFAULT_TIMEOUT, type=int, show_default=True, help='Stop scanning a file if scanning takes longer than a timeout in seconds.')

def scancode(ctx,
             input, output_file,
             copyright, license, package,
             email, url, info,
             license_score, license_text, only_findings, strip_root,
             format, verbose, quiet, processes,
             diag, timeout, *args, **kwargs):
    """scan the <input> file or directory for origin clues and license and save results to the <output_file>.

    The scan results are printed to stdout if <output_file> is not provided.
    Error and progress is printed to stderr.
    """

    possible_scans = OrderedDict([
        ('infos', info),
        ('licenses', license),
        ('copyrights', copyright),
        ('packages', package),
        ('emails', email),
        ('urls', url)
    ])

    options = OrderedDict([
        ('--copyright', copyright),
        ('--license', license),
        ('--package', package),
        ('--email', email),
        ('--url', url),
        ('--info', info),
        ('--license-score', license_score),
        ('--license-text', license_text),
        ('--only-findings', only_findings),
        ('--strip-root', strip_root),
        ('--format', format),
        ('--diag', diag),
    ])

    # Use default scan options when no options are provided on the command line.
    if not any(possible_scans.values()):
        possible_scans['copyrights'] = True
        possible_scans['licenses'] = True
        possible_scans['packages'] = True
        options['--copyright'] = True
        options['--license'] = True
        options['--package'] = True

    # A hack to force info being exposed for SPDX output in order to reuse calculated file SHA1s.
    if format in ('spdx-tv', 'spdx-rdf'):
        possible_scans['infos'] = True

    for key in options:
        if key == "--license-score":
            continue
        if options[key] == False:
            del options[key]

    get_licenses_with_score = partial(get_licenses, min_score=license_score, include_text=license_text, diag=diag)

    # List of scan functions in the same order as "possible_scans".
    scan_functions = [
        None,  # For "infos" there is no separate scan function, they are always gathered, though not always exposed.
        get_licenses_with_score,
        get_copyrights,
        get_package_infos,
        get_emails,
        get_urls
    ]

    # FIXME: this is does not make sense to use tuple and positional values
    scanners = OrderedDict(zip(possible_scans.keys(), zip(possible_scans.values(), scan_functions)))

    scans_cache_class = get_scans_cache_class()

    try:
        files_count, results = scan(input_path=input,
                                    scanners=scanners,
                                    license_score=license_score,
                                    license_text=license_text,
                                    verbose=verbose,
                                    quiet=quiet,
                                    processes=processes,
                                    timeout=timeout,
                                    diag=diag,
                                    scans_cache_class=scans_cache_class,
                                    strip_root=strip_root)
        if not quiet:
            echo_stderr('Saving results.', fg='green')

        save_results(scanners, only_findings, files_count, results, format, options, input, output_file)

    finally:
        # cleanup
        cache = scans_cache_class()
        cache.clear()

    # TODO: add proper return code
    # rc = 1 if has__errors else 0
    # ctx.exit(rc)


def scan(input_path,
         scanners,
         license_score=0, license_text=False,
         verbose=False, quiet=False,
         processes=1, timeout=DEFAULT_TIMEOUT,
         diag=False,
         scans_cache_class=None,
         strip_root=False):
    """
    Return a tuple of (files_count, scan_results) where
    scan_results is an iterable. Run each requested scan proper: each individual file
    scan is cached on disk to free memory. Then the whole set of scans is loaded from
    the cache and streamed at the end.
    """
    assert scans_cache_class
    scan_summary = OrderedDict()
    scan_summary['scanned_path'] = input_path
    scan_summary['processes'] = processes
    get_licenses_with_score = partial(get_licenses, min_score=license_score, include_text=license_text, diag=diag)

    # Display scan start details
    ############################
    # FIXME: this is does not make sense to use tuple and positional values
    scans = [k for k, v in scanners.items() if v[0]]
    _scans = ', '.join(scans)
    if not quiet:
        echo_stderr('Scanning files for: %(_scans)s with %(processes)d process(es)...' % locals())

    scan_summary['scans'] = scans[:]
    scan_start = time()
    indexing_time = 0
    # FIXME: this is does not make sense to use tuple and positional values
    with_licenses, _ = scanners.get('licenses', (False, ''))
    if with_licenses:
        # build index outside of the main loop
        # this also ensures that forked processes will get the index on POSIX naturally
        if not quiet:
            echo_stderr('Building license detection index...', fg='green', nl=False)
        from licensedcode.index import get_index
        _idx = get_index()
        indexing_time = time() - scan_start
        if not quiet:
            echo_stderr('Done.', fg='green', nl=True)

    scan_summary['indexing_time'] = indexing_time

    # TODO: handle pickling errors as in ./scancode -cilp   samples/ -n3: note they are only caused by a FanoutCache
    # TODO: handle other exceptions properly to avoid any hanging

    # maxtasksperchild helps with recycling processes in case of leaks
    pool = get_pool(processes=processes, maxtasksperchild=1000)
    resources = resource_paths(input_path)
    logfile_path = scans_cache_class().cache_files_log
    with open(logfile_path, 'wb') as logfile_fd:

        logged_resources = _resource_logger(logfile_fd, resources)

        scanit = partial(_scanit, scanners=scanners, scans_cache_class=scans_cache_class,
                         diag=diag, timeout=timeout)

        try:
            # Using chunksize is documented as much more efficient in the Python doc.
            # Yet "1" still provides a better and more progressive feedback.
            # With imap_unordered, results are returned as soon as ready and out of order.
            scanned_files = pool.imap_unordered(scanit, logged_resources, chunksize=1)
            pool.close()

            if not quiet:
                echo_stderr('Scanning files...', fg='green')

            def scan_event(item):
                """Progress event displayed each time a file is scanned"""
                if quiet:
                    return ''
                if item:
                    _scan_success, _scanned_path = item
                    _progress_line = verbose and _scanned_path or fileutils.file_name(_scanned_path)
                    if not verbose:
                    	_progress_line = shorten_filename(_progress_line)
                    return style('Scanned: ') + style(_progress_line, fg=_scan_success and 'green' or 'red')

            scanning_errors = []
            files_count = 0
            with utils.progressmanager(scanned_files, item_show_func=scan_event,
                                       show_pos=True, verbose=verbose, quiet=quiet,
                                       file=sys.stderr) as scanned:
                while True:
                    try:
                        result = scanned.next()
                        scan_success, scanned_rel_path = result
                        if not scan_success:
                            scanning_errors.append(scanned_rel_path)
                        files_count += 1
                    except StopIteration:
                        break
                    except KeyboardInterrupt:
                        print('\nAborted with Ctrl+C!')
                        pool.terminate()
                        break
        finally:
            # ensure the pool is really dead to work around a Python 2.7.3 bug:
            # http://bugs.python.org/issue15101
            pool.terminate()

    # TODO: add stats to results somehow

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

    if not quiet:
        # Display stats
        ##########################
        echo_stderr('Scanning done.', fg=scanning_errors and 'red' or 'green')
        if scanning_errors:
            echo_stderr('Some files failed to scan properly. See scan for details:', fg='red')
            for errored_path in scanning_errors:
                echo_stderr(' ' + errored_path, fg='red')

        echo_stderr('Scan statistics: %(files_count)d files scanned in %(total_time)ds.' % locals())
        echo_stderr('Scan options:    %(_scans)s with %(processes)d process(es).' % locals())
        echo_stderr('Scanning speed:  %(files_scanned_per_second)s files per sec.' % locals())
        echo_stderr('Scanning time:   %(scanning_time)ds.' % locals())
        echo_stderr('Indexing time:   %(indexing_time)ds.' % locals(), reset=True)

    # finally return an iterator on cached results
    cached_scan = scans_cache_class()
    root_dir = _get_root_dir(input_path, strip_root)
    return files_count, cached_scan.iterate(scans, root_dir)


def shorten_filename(filename, max_length=25):
    """
    Return a truncated `filename` usable for fixed width display if `filename` is longer than `max_length`.
    """
    if filename is None:
        return ''
    filename = fileutils.file_name(filename)
    if len(filename) <= max_length:
        return filename
    base_name, extension = fileutils.splitext(filename)
    number_of_dots = 3
    remaining_length = max_length - len(extension) - number_of_dots
    prefix_and_suffix_length = abs(remaining_length // 2)
    prefix = base_name[:prefix_and_suffix_length]
    ellipsis = number_of_dots*'.'
    suffix = base_name[-prefix_and_suffix_length:]
    shortened_filename = "{prefix}{ellipsis}{suffix}{extension}".format(**locals())
    return shortened_filename


def _get_root_dir(input_path, strip_root=False):
    """
    Return a root dir name or None.
    """
    if strip_root:
        root_dir = None
    else:
        _scanned_path = os.path.abspath(os.path.normpath(os.path.expanduser(input_path)))
        if filetype.is_dir(_scanned_path):
            root_dir = _scanned_path
        else:
            root_dir = fileutils.parent_directory(_scanned_path)
        root_dir = fileutils.file_name(root_dir)

    return root_dir


def _resource_logger(logfile_fd, resources):
    """
    Log file path to the logfile_fd opened file descriptor for each resource and
    yield back the resources.
    """
    file_logger = ScanFileCache.log_file_path
    for posix_path, rel_path in resources:
        file_logger(logfile_fd, rel_path)
        yield posix_path, rel_path


def _scanit(paths, scanners, scans_cache_class, diag, timeout=DEFAULT_TIMEOUT):
    """
    Run scans and cache results on disk. Return a tuple of (success, scanned relative
    path) where sucess is True on success, False on error. Note that this is really
    only a wrapper function used as an execution unit for parallel processing.
    """
    abs_path, rel_path = paths
    # always fetch infos and cache.
    infos = OrderedDict()
    infos['path'] = rel_path
    infos.update(scan_infos(abs_path, diag=diag))

    success = True
    scans_cache = scans_cache_class()
    is_cached = scans_cache.put_info(rel_path, infos)

    # note: "flag and function" expressions return the function if flag is True
    # note: the order of the scans matters to show things in logical order
    scanner_functions = map(lambda t : t[0] and t[1], scanners.values())
    scanners = OrderedDict(zip(scanners.keys(), scanner_functions))

    if any(scanner_functions):
        # Skip other scans if already cached
        # FIXME: ENSURE we only do this for files not directories
        if not is_cached:
            # run the scan as an interruptiple task
            scans_runner = partial(scan_one, abs_path, scanners, diag)
            # quota keyword args for interruptible
            success, scan_result = interruptible(scans_runner, timeout=timeout)
            if not success:
                # Use scan errors as the scan result for that file on failure this is
                # a top-level error not attachedd to a specific scanner, hence the
                # "scan" key is used for these errors
                scan_result = {'scan_errors': [scan_result]}

            scans_cache.put_scan(rel_path, infos, scan_result)

            # do not report success if some other errors happened
            if scan_result.get('scan_errors'):
                success = False

    return success, rel_path


def resource_paths(base_path):
    """
    Yield tuples of (absolute path, base_path-relative path) for all the files found
    at base_path (either a directory or file) given an absolute base_path. Only yield
    Files, not directories.
    absolute path is a native OS path.
    base_path-relative path is a POSIX path.

    The relative path is guaranted to be unicode and may be URL-encoded and may not
    be suitable to address an actual file.
    """
    base_path = os.path.abspath(os.path.normpath(os.path.expanduser(base_path)))
    base_is_dir = filetype.is_dir(base_path)
    len_base_path = len(base_path)
    ignored = partial(ignore.is_ignored, ignores=ignore.ignores_VCS, unignores={})
    resources = fileutils.resource_iter(base_path, ignored=ignored)

    for abs_path in resources:
        posix_path = fileutils.as_posixpath(abs_path)
        # fix paths: keep the path as relative to the original base_path
        rel_path = utils.get_relative_path(posix_path, len_base_path, base_is_dir)
        yield abs_path, rel_path


def scan_infos(input_file, diag=False):
    """
    Scan one file or directory and return file_infos data.
    This always contains an extra 'errors' key with a list of error messages,
    possibly empty.
    """
    errors = []
    try:
        infos = get_file_infos(input_file, as_list=False)
    except Exception as e:
        # never fail but instead add an error message.
        infos = _empty_file_infos()
        errors = ['ERROR: infos: ' + e.message]
        if diag:
            errors.append('ERROR: infos: ' + traceback.format_exc())
    # put errors last
    infos['scan_errors'] = errors
    return infos


def scan_one(input_file, scanners, diag=False):
    """
    Scan one file or directory and return a scanned data, calling every scan in
    the `scans` mapping of (scan name -> scan function). Scan data contain a
    'scan_errors' key with a list of error messages.
    If `diag` is True, 'scan_errors' error messages also contain detailed diagnostic
    information such as a traceback if available.
    """
    scan_result = OrderedDict()
    scan_errors = []
    for scan_name, scan_func in scanners.items():
        if not scan_func:
            continue
        try:
            scan_details = scan_func(input_file)
            # consume generators
            if isinstance(scan_details, GeneratorType):
                scan_details = list(scan_details)
            scan_result[scan_name] = scan_details
        except Exception as e:
            # never fail but instead add an error message and keep an empty scan:
            scan_result[scan_name] = []
            messages = ['ERROR: ' + scan_name + ': ' + e.message]
            if diag:
                messages.append('ERROR: ' + scan_name + ': ' + traceback.format_exc())
            scan_errors.extend(messages)
    # put errors last, after scans proper
    scan_result['scan_errors'] = scan_errors
    return scan_result


def has_findings(active_scans, file_data):
    """
    Return True if the file_data has findings for any of the `active_scans` names list.
    """
    return any(file_data.get(scan_name) for scan_name in active_scans)


def save_results(scanners, only_findings, files_count, results, format, options, input, output_file):
    """
    Save scan results to file or screen.
    """

    if only_findings:
        # Find all scans that are both enabled and have a valid function reference.
        # This deliberately filters out the "info" scan (which always has a "None"
        # function reference) as there is no dedicated "infos" key in the results
        # that "has_findings()" could check.
        active_scans = [k for k, v in scanners.items() if v[0] and v[1]]

        # FIXME: this is forcing all the scan results to be loaded in memory
        # and defeats lazy loading from cache
        results = [file_data for file_data in results if has_findings(active_scans, file_data)]
        # FIXME: computing len before hand will need a list and therefore need loding
        # it all aheaed of time
        files_count = len(results)

    # note: in tests, sys.stdout is not used, but some io wrapper with no name
    # attributes
    is_real_file = hasattr(output_file, 'name')

    if output_file != sys.stdout and is_real_file:
        parent_dir = os.path.dirname(output_file.name)
        if parent_dir:
            fileutils.create_dir(abspath(expanduser(parent_dir)))

    if format not in formats:
        # render using a user-provided custom format template
        if not os.path.isfile(format):
            echo_stderr('\nInvalid template passed.', fg='red')
        else:
            for template_chunk in as_template(results, template=format):
                try:
                    output_file.write(template_chunk)
                except Exception as e:
                    extra_context = 'ERROR: Failed to write output to HTML for: ' + repr(template_chunk)
                    echo_stderr(extra_context, fg='red')
                    e.args += (extra_context,)
                    raise e
        return

    write_formatted_output(scanners, files_count, version, notice, results, format, options, input, output_file, echo_stderr)
