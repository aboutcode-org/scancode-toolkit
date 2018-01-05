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

from collections import namedtuple
from collections import OrderedDict
from functools import partial
from itertools import imap
import os
from os.path import expanduser
from os.path import abspath
import sys
from time import time
import traceback
from types import GeneratorType

import click
click.disable_unicode_literals_warning = True
from click.termui import style

from commoncode.filetype import is_dir
from commoncode.fileutils import as_posixpath
from commoncode.fileutils import create_dir
from commoncode.fileutils import file_name
from commoncode.fileutils import parent_directory
from commoncode.fileutils import PATH_TYPE
from commoncode.fileutils import path_to_bytes
from commoncode.fileutils import path_to_unicode
from commoncode.fileutils import resource_iter
from commoncode import ignore
from commoncode.system import on_linux
from commoncode.text import toascii

import plugincode.output
import plugincode.post_scan
import plugincode.pre_scan

from scancode import __version__ as version
from scancode import ScanOption
from scancode.api import DEJACODE_LICENSE_URL
from scancode.api import _empty_file_infos
from scancode.api import get_copyrights
from scancode.api import get_emails
from scancode.api import get_file_infos
from scancode.api import get_licenses
from scancode.api import get_package_infos
from scancode.api import get_urls
from scancode.api import Resource
from scancode.cache import get_scans_cache_class
from scancode.interrupt import DEFAULT_TIMEOUT
from scancode.interrupt import fake_interruptible
from scancode.interrupt import interruptible
from scancode.interrupt import TimeoutError
from scancode.utils import BaseCommand
from scancode.utils import compute_fn_max_len
from scancode.utils import fixed_width_file_name
from scancode.utils import progressmanager


echo_stderr = partial(click.secho, err=True)


# Python 2 and 3 support
try:
    # Python 2
    unicode
    str_orig = str
    bytes = str
    str = unicode
except NameError:
    # Python 3
    unicode = str


# this will init the plugins
plugincode.pre_scan.initialize()
plugincode.output.initialize()
plugincode.post_scan.initialize()


CommandOption = namedtuple('CommandOption', 'group, name, option, value, default')
Scanner = namedtuple('Scanner', 'name function is_enabled')


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

# CLI help groups
SCANS = 'scans'
OUTPUT = 'output'
PRE_SCAN = 'pre-scan'
POST_SCAN = 'post-scan'
MISC = 'misc'
CORE = 'core'


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

Scan a directory while ignoring a single file. Print scan results to stdout as JSON:

    scancode --ignore README samples/

Scan a directory while ignoring all files with txt extension. Print scan results to
stdout as JSON (It is recommended to use quoted glob patterns to prevent pattern
expansion by the shell):

    scancode --ignore "*.txt" samples/

Special characters supported in GLOB pattern:
*       matches everything
?       matches any single character
[seq]   matches any character in seq
[!seq]  matches any character not in seq

For a literal match, wrap the meta-characters in brackets. For example, '[?]' matches the character '?'.
For glob see https://en.wikipedia.org/wiki/Glob_(programming).

Note: Glob patterns cannot be applied to path as strings, for e.g.
    scancode --ignore "samples*licenses" samples/
will not ignore "samples/JGroups/licenses".

Scan a directory while ignoring multiple files (or glob patterns). Print the scan
results to stdout as JSON:

    scancode --ignore README --ignore "*.txt" samples/

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


def reindex_licenses(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    from licensedcode import cache
    click.echo('Checking and rebuilding the license index...')
    cache.reindex()
    click.echo('Done.')
    ctx.exit()


epilog_text = '''Examples (use --examples for more):

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


class ScanCommand(BaseCommand):
    """
    A command class that is aware of ScanCode plugins and provides help where
    each option is grouped by group.
    """
    short_usage_help = '''
Try 'scancode --help' for help on options and arguments.'''

    def __init__(self, name, context_settings=None, callback=None,
                 params=None, help=None, epilog=None, short_help=None,
                 options_metavar='[OPTIONS]', add_help_option=True,
                 plugins_by_group=()):

        super(ScanCommand, self).__init__(name, context_settings, callback,
                 params, help, epilog, short_help, options_metavar, add_help_option)

        for group, plugins in plugins_by_group:
            for pname, plugin in sorted(plugins.items()):
                for option in plugin.get_plugin_options():
                    if not isinstance(option, ScanOption):
                        raise Exception(
                            'Invalid plugin option "%(pname)s": option is not '
                            'an instance of "ScanOption".' % locals())

                    # normalize the help text, which may otherwise be messy
                    option.help = option.help and ' '.join(option.help.split())
                    option.group = group
                    # this makes the plugin options "known" from the command
                    self.params.append(option)

    def format_options(self, ctx, formatter):
        """
        Overridden from click.Command to write all options into the formatter in
        groups they belong to. If a group is not specified, add the option to
        MISC group.
        """
        # this mapping defines the CLI help presentation order
        groups = OrderedDict([
            (SCANS, []),
            (OUTPUT, []),
            (PRE_SCAN, []),
            (POST_SCAN, []),
            (MISC, []),
            (CORE, []),
        ])

        for param in self.get_params(ctx):
            # Get the list of option's name and help text
            help_record = param.get_help_record(ctx)
            if help_record:
                if getattr(param, 'group', None):
                    groups[param.group].append(help_record)
                else:
                    # use the misc group if no group is defined
                    groups['misc'].append(help_record)

        with formatter.section('Options'):
            for group, option in groups.items():
                if option:
                    with formatter.section(group):
                        formatter.write_dl(option)


def validate_formats(ctx, param, value):
    """
    Validate formats and template files. Raise a BadParameter on errors.
    """
    value_lower = value.lower()
    if value_lower in plugincode.output.get_format_plugins():
        return value_lower
    # render using a user-provided custom format template
    if not os.path.isfile(value):
        raise click.BadParameter(
            'Unknwow <format> or invalid template file path: "%(value)s" '
            'does not exist or is not readable.' % locals())
    return value


def validate_exclusive(ctx, exclusive_options):
    """
    Validate mutually exclusive options.
    Raise a UsageError with on errors.
    """
    ctx_params = ctx.params
    selected_options = [ctx_params[eop] for eop in exclusive_options if ctx_params[eop]]
    if len(selected_options) > 1:
        msg = ' and '.join('`' + eo.replace('_', '-') + '`' for eo in exclusive_options)
        msg += ' are mutually exclusion options. You can use only one of them.'
        raise click.UsageError(msg)


# collect plugins for each group and add plugins options to the command
# params
_plugins_by_group = [
    (PRE_SCAN, plugincode.pre_scan.get_pre_scan_plugins()),
    (POST_SCAN, plugincode.post_scan.get_post_scan_plugins()),
]

@click.command(name='scancode', epilog=epilog_text, cls=ScanCommand, plugins_by_group=_plugins_by_group)
@click.pass_context

# ensure that the input path is bytes on Linux, unicode elsewhere
@click.argument('input', metavar='<input>', type=click.Path(exists=True, readable=True, path_type=PATH_TYPE))
@click.argument('output_file', default='-', metavar='<output_file>', type=click.File(mode='wb', lazy=False))

# Note that click's 'default' option is set to 'false' here despite these being documented to be enabled by default in
# order to more elegantly enable all of these (see code below) if *none* of the command line options are specified.
@click.option('-c', '--copyright', '--copyrights', is_flag=True, default=False, help='Scan <input> for copyrights. [default]', group=SCANS, cls=ScanOption)
@click.option('-l', '--license', '--licenses', is_flag=True, default=False, help='Scan <input> for licenses. [default]', group=SCANS, cls=ScanOption)
@click.option('-p', '--package', '--packages', is_flag=True, default=False, help='Scan <input> for packages. [default]', group=SCANS, cls=ScanOption)

@click.option('-e', '--email', '--emails', is_flag=True, default=False, help='Scan <input> for emails.', group=SCANS, cls=ScanOption)
@click.option('-u', '--url', '--urls', is_flag=True, default=False, help='Scan <input> for urls.', group=SCANS, cls=ScanOption)
@click.option('-i', '--info', '--infos', is_flag=True, default=False, help='Include information such as size, type, etc.', group=SCANS, cls=ScanOption)

@click.option('--license-score', is_flag=False, default=0, type=int, show_default=True,
              help='Do not return license matches with scores lower than this score. A number between 0 and 100.', group=SCANS, cls=ScanOption)
@click.option('--license-text', is_flag=True, default=False,
              help='Include the detected licenses matched text. Has no effect unless --license is requested.', group=SCANS, cls=ScanOption)
@click.option('--license-url-template', is_flag=False, default=DEJACODE_LICENSE_URL, show_default=True,
              help='Set the template URL used for the license reference URLs. In a template URL, curly braces ({}) are replaced by the license key.', group=SCANS, cls=ScanOption)
@click.option('--strip-root', is_flag=True, default=False,
              help='Strip the root directory segment of all paths. The default is to always '
                   'include the last directory segment of the scanned path such that all paths have a common root directory. '
                   'This cannot be combined with `--full-root` option.', group=OUTPUT, cls=ScanOption)
@click.option('--full-root', is_flag=True, default=False,
              help='Report full, absolute paths. The default is to always '
                   'include the last directory segment of the scanned path such that all paths have a common root directory. '
                   'This cannot be combined with the `--strip-root` option.', group=OUTPUT, cls=ScanOption)

@click.option('-f', '--format', is_flag=False, default='json', show_default=True, metavar='<format>',
              help=('Set <output_file> format to one of: %s or use <format> '
                    'as the path to a custom template file' % ', '.join(plugincode.output.get_format_plugins())),
                     callback=validate_formats, group=OUTPUT, cls=ScanOption)

@click.option('--verbose', is_flag=True, default=False, help='Print verbose file-by-file progress messages.', group=OUTPUT, cls=ScanOption)
@click.option('--quiet', is_flag=True, default=False, help='Do not print summary or progress messages.', group=OUTPUT, cls=ScanOption)

@click.help_option('-h', '--help', group=CORE, cls=ScanOption)
@click.option('-n', '--processes', is_flag=False, default=1, type=int, show_default=True, help='Scan <input> using n parallel processes.', group=CORE, cls=ScanOption)
@click.option('--examples', is_flag=True, is_eager=True, callback=print_examples, help=('Show command examples and exit.'), group=CORE, cls=ScanOption)
@click.option('--about', is_flag=True, is_eager=True, callback=print_about, help='Show information about ScanCode and licensing and exit.', group=CORE, cls=ScanOption)
@click.option('--version', is_flag=True, is_eager=True, callback=print_version, help='Show the version and exit.', group=CORE, cls=ScanOption)

@click.option('--diag', is_flag=True, default=False, help='Include additional diagnostic information such as error messages or result details.', group=CORE, cls=ScanOption)
@click.option('--timeout', is_flag=False, default=DEFAULT_TIMEOUT, type=float, show_default=True, help='Stop scanning a file if scanning takes longer than a timeout in seconds.', group=CORE, cls=ScanOption)
@click.option('--reindex-licenses', is_flag=True, default=False, is_eager=True, callback=reindex_licenses, help='Force a check and possible reindexing of the cached license index.', group=MISC, cls=ScanOption)

def scancode(ctx, input, output_file, *args, **kwargs):
    """scan the <input> file or directory for license, origin and packages and save results to <output_file(s)>.

    The scan results are printed to stdout if <output_file> is not provided.
    Error and progress is printed to stderr.
    """
    validate_exclusive(ctx, ['strip_root', 'full_root'])

    # ## TODO: FIX when plugins are used everywhere
    copyrights = kwargs.get('copyrights')
    licenses = kwargs.get('licenses')
    packages = kwargs.get('packages')
    emails = kwargs.get('emails')
    urls = kwargs.get('urls')
    infos = kwargs.get('infos')

    strip_root = kwargs.get('strip_root')
    full_root = kwargs.get('full_root')
    format = kwargs.get('format')

    verbose = kwargs.get('verbose')
    quiet = kwargs.get('quiet')
    processes = kwargs.get('processes')
    diag = kwargs.get('diag')
    timeout = kwargs.get('timeout')
    # ## TODO: END FIX when plugins are used everywhere

    # Use default scan options when no scan option is provided
    # FIXME: this should be removed?
    use_default_scans = not any([infos, licenses, copyrights, packages, emails, urls])

    # FIXME: A hack to force info being exposed for SPDX output in order to
    # reuse calculated file SHA1s.
    is_spdx = format in ('spdx-tv', 'spdx-rdf')

    get_licenses_with_score = partial(get_licenses,
        diag=diag,
        min_score=kwargs.get('license_score'),
        include_text=kwargs.get('license_text'),
        license_url_template=kwargs.get('license_url_template'))

    scanners = [
        # FIXME: For "infos" there is no separate scan function, they are always
        # gathered, though not always exposed.
        Scanner('infos', None, infos or is_spdx),
        Scanner('licenses', get_licenses_with_score, licenses or use_default_scans),
        Scanner('copyrights', get_copyrights, copyrights or use_default_scans),
        Scanner('packages', get_package_infos, packages or use_default_scans),
        Scanner('emails', get_emails, emails),
        Scanner('urls', get_urls, urls)
    ]

    ignored_options = 'verbose', 'quiet', 'processes', 'timeout'
    all_options = list(get_command_options(ctx, ignores=ignored_options, skip_no_group=True))

    # FIXME: this is terribly hackish :|
    # FIXUP OPTIONS FOR DEFAULT SCANS
    options = []
    enabled_scans = {sc.name: sc.is_enabled for sc in scanners}
    for opt in all_options:
        if enabled_scans.get(opt.name):
            options.append(opt._replace(value=True))
            continue

        # do not report option set to defaults or with an empty list value
        if isinstance(opt.value, (list, tuple)):
            if opt.value:
                options.append(opt)
            continue
        if opt.value != opt.default:
            options.append(opt)

    # Find all scans that are both enabled and have a valid function
    # reference. This deliberately filters out the "info" scan
    # (which always has a "None" function reference) as there is no
    # dedicated "infos" key in the results that "plugin_only_findings.has_findings()"
    # could check.
    active_scans = [scan.name for scan in scanners if scan.is_enabled]


    # FIXME: Prescan should happen HERE not as part of the per-file scan
    pre_scan_plugins = []
    for name, plugin in plugincode.pre_scan.get_pre_scan_plugins().items():
        if plugin.is_enabled:
            pre_scan_plugins.append(plugin(all_options, active_scans))

    # TODO: new loop
    # 1. collect minimally the whole files tree in memory as a Resource tree
    # 2. apply the pre scan plugins to this tree
    # 3. run the scan proper, save scan details on disk
    # 4. apply the post scan plugins to this tree, lazy load as needed the scan
    # details from disk. save back updated details on disk

    scans_cache_class = get_scans_cache_class()
    try:
        files_count, results, success = scan_all(
            input_path=input,
            scanners=scanners,
            verbose=verbose, quiet=quiet,
            processes=processes, timeout=timeout, diag=diag,
            scans_cache_class=scans_cache_class,
            strip_root=strip_root, full_root=full_root,
            # FIXME: this should not be part of the of scan_all!!!!
            pre_scan_plugins=pre_scan_plugins)

        # FIXME!!!
        for pname, plugin in plugincode.post_scan.get_post_scan_plugins().items():
            plug = plugin(all_options, active_scans)
            if plug.is_enabled():
                if not quiet:
                    echo_stderr('Running post-scan plugin: %(pname)s...' % locals(), fg='green')
                # FIXME: we should always catch errors from plugins properly
                results = plug.process_resources(results)

        # FIXME: computing len needs a list and therefore needs loading it all ahead of time
        # this should NOT be needed with a better cache architecture!!!
        results = list(results)
        files_count = len(results)

        if not quiet:
            echo_stderr('Saving results.', fg='green')

        # FIXME: we should have simpler args: a scan "header" and scan results
        save_results(scanners, files_count, results, format, options, input, output_file)

    finally:
        # cleanup
        cache = scans_cache_class()
        cache.clear()

    rc = 0 if success else 1
    ctx.exit(rc)


def scan_all(input_path, scanners,
         verbose=False, quiet=False, processes=1, timeout=DEFAULT_TIMEOUT,
         diag=False, scans_cache_class=None,
         strip_root=False, full_root=False,
         pre_scan_plugins=None):
    """
    Return a tuple of (files_count, scan_results, success) where
    scan_results is an iterable and success is a boolean.

    Run each requested scan proper: each individual file scan is cached
    on disk to free memory. Then the whole set of scans is loaded from
    the cache and streamed at the end.
    """
    assert scans_cache_class
    scan_summary = OrderedDict()
    scan_summary['scanned_path'] = input_path
    scan_summary['processes'] = processes

    # Display scan start details
    ############################
    scans = [scan.name for scan in scanners if scan.is_enabled]
    _scans = ', '.join(scans)
    if not quiet:
        echo_stderr('Scanning files for: %(_scans)s with %(processes)d process(es)...' % locals())

    scan_summary['scans'] = scans[:]
    scan_start = time()
    indexing_time = 0

    # FIXME:  THIS SHOULD NOT TAKE PLACE HERE!!!!!!
    with_licenses = any(sc for sc in scanners if sc.name == 'licenses' and sc.is_enabled)
    if with_licenses:
        # build index outside of the main loop for speed
        # REALLY????? this also ensures that forked processes will get the index on POSIX naturally
        if not quiet:
            echo_stderr('Building license detection index...', fg='green', nl=False)
        from licensedcode.cache import get_index
        get_index(False)
        indexing_time = time() - scan_start
        if not quiet:
            echo_stderr('Done.', fg='green', nl=True)

    scan_summary['indexing_time'] = indexing_time

    pool = None

    resources = get_resources(input_path, diag, scans_cache_class)

    # FIXME: we should try/catch here
    for plugin in pre_scan_plugins:
        resources = plugin.process_resources(resources)

    resources = list(resources)

    paths_with_error = []
    files_count = 0

    scanit = partial(_scanit, scanners=scanners, scans_cache_class=scans_cache_class,
                     diag=diag, timeout=timeout, processes=processes)

    max_file_name_len = compute_fn_max_len()
    # do not display a file name in progress bar if there is less than 5 chars available.
    display_fn = bool(max_file_name_len > 10)
    try:
        if processes:
            # maxtasksperchild helps with recycling processes in case of leaks
            pool = get_pool(processes=processes, maxtasksperchild=1000)
            # Using chunksize is documented as much more efficient in the Python doc.
            # Yet "1" still provides a better and more progressive feedback.
            # With imap_unordered, results are returned as soon as ready and out of order.
            scanned_files = pool.imap_unordered(scanit, resources, chunksize=1)
            pool.close()
        else:
            # no multiprocessing with processes=0
            scanned_files = imap(scanit, resources)
            if not quiet:
                echo_stderr('Disabling multi-processing and multi-threading...', fg='yellow')

        if not quiet:
            echo_stderr('Scanning files...', fg='green')

        def scan_event(item):
            """Progress event displayed each time a file is scanned"""
            if quiet or not item or not display_fn:
                return ''
            _scan_success, _scanned_path = item
            _scanned_path = unicode(toascii(_scanned_path))
            if verbose:
                _progress_line = _scanned_path
            else:
                _progress_line = fixed_width_file_name(_scanned_path, max_file_name_len)
            return style('Scanned: ') + style(_progress_line, fg=_scan_success and 'green' or 'red')

        scanning_errors = []
        files_count = 0
        with progressmanager(
            scanned_files, item_show_func=scan_event, show_pos=True,
            verbose=verbose, quiet=quiet, file=sys.stderr) as scanned:
            while True:
                try:
                    result = scanned.next()
                    scan_success, scanned_rel_path = result
                    if not scan_success:
                        paths_with_error.append(scanned_rel_path)
                    files_count += 1
                except StopIteration:
                    break
                except KeyboardInterrupt:
                    print('\nAborted with Ctrl+C!')
                    if pool:
                        pool.terminate()
                    break
    finally:
        if pool:
            # ensure the pool is really dead to work around a Python 2.7.3 bug:
            # http://bugs.python.org/issue15101
            pool.terminate()

    # TODO: add stats to results somehow

    # Compute stats
    ##########################
    scan_summary['files_count'] = files_count
    scan_summary['files_with_errors'] = paths_with_error
    total_time = time() - scan_start
    scanning_time = total_time - indexing_time
    scan_summary['total_time'] = total_time
    scan_summary['scanning_time'] = scanning_time

    files_scanned_per_second = round(float(files_count) / scanning_time , 2)
    scan_summary['files_scanned_per_second'] = files_scanned_per_second

    if not quiet:
        # Display stats
        ##########################
        echo_stderr('Scanning done.', fg=paths_with_error and 'red' or 'green')
        if paths_with_error:
            if diag:
                echo_stderr('Some files failed to scan properly:', fg='red')
                # iterate cached results to collect all scan errors
                cached_scan = scans_cache_class()
                root_dir = _get_root_dir(input_path, strip_root, full_root)
                resource_paths = (r.rel_path for r in resources)
                scan_results = cached_scan.iterate(resource_paths, scans, root_dir, paths_subset=paths_with_error)
                for scan_result in scan_results:
                    errored_path = scan_result.get('path', '')
                    echo_stderr('Path: ' + errored_path, fg='red')
                    for error in scan_result.get('scan_errors', []):
                        for emsg in error.splitlines(False):
                            echo_stderr('  ' + emsg)
                    echo_stderr('')
            else:
                echo_stderr('Some files failed to scan properly. Use the --diag option for additional details:', fg='red')
                for errored_path in paths_with_error:
                    echo_stderr(' ' + errored_path, fg='red')

        echo_stderr('Scan statistics: %(files_count)d files scanned in %(total_time)ds.' % locals())
        echo_stderr('Scan options:    %(_scans)s with %(processes)d process(es).' % locals())
        echo_stderr('Scanning speed:  %(files_scanned_per_second)s files per sec.' % locals())
        echo_stderr('Scanning time:   %(scanning_time)ds.' % locals())
        echo_stderr('Indexing time:   %(indexing_time)ds.' % locals(), reset=True)

    success = not paths_with_error
    # finally return an iterator on cached results
    cached_scan = scans_cache_class()
    root_dir = _get_root_dir(input_path, strip_root, full_root)
    #############################################
    #############################################
    #############################################
    # FIXME: we must return Resources here!!!!
    #############################################
    #############################################
    #############################################
    resource_paths = (r.rel_path for r in resources)
    return files_count, cached_scan.iterate(resource_paths, scans, root_dir), success


def _get_root_dir(input_path, strip_root=False, full_root=False):
    """
    Return a root dir name or None.
    On Windows, the path uses POSIX (forward slash) separators.
    """
    if strip_root:
        return

    scanned_path = os.path.abspath(os.path.normpath(os.path.expanduser(input_path)))
    scanned_path = as_posixpath(scanned_path)
    if is_dir(scanned_path):
        root_dir = scanned_path
    else:
        root_dir = parent_directory(scanned_path)
        root_dir = as_posixpath(root_dir)

    if full_root:
        return root_dir
    else:
        return file_name(root_dir)


def _scanit(resource, scanners, scans_cache_class, diag, timeout=DEFAULT_TIMEOUT, processes=1):
    """
    Run scans and cache results on disk. Return a tuple of (success, scanned relative
    path) where sucess is True on success, False on error. Note that this is really
    only a wrapper function used as an execution unit for parallel processing.
    """
    success = True
    scans_cache = scans_cache_class()

    if processes:
        interrupter = interruptible
    else:
        # fake, non inteerrupting used for debugging when processes=0
        interrupter = fake_interruptible

    scanners = [scanner for scanner in scanners
                if scanner.is_enabled and scanner.function]
    if not scanners:
        return success, resource.rel_path

    # Skip other scans if already cached
    # FIXME: ENSURE we only do this for files not directories
    if not resource.is_cached:
        # run the scan as an interruptiple task
        scans_runner = partial(scan_one, resource.abs_path, scanners, diag)
        success, scan_result = interrupter(scans_runner, timeout=timeout)
        if not success:
            # Use scan errors as the scan result for that file on failure this is
            # a top-level error not attachedd to a specific scanner, hence the
            # "scan" key is used for these errors
            scan_result = {'scan_errors': [scan_result]}

        scans_cache.put_scan(resource.rel_path, resource.get_info(), scan_result)

        # do not report success if some other errors happened
        if scan_result.get('scan_errors'):
            success = False

    return success, resource.rel_path


def get_resources(base_path, diag, scans_cache_class):
    """
    Yield `Resource` objects for all the files found at base_path (either a
    directory or file) given an absolute base_path.
    """
    if on_linux:
        base_path = base_path and path_to_bytes(base_path)
    else:
        base_path = base_path and path_to_unicode(base_path)

    base_path = os.path.abspath(os.path.normpath(os.path.expanduser(base_path)))
    base_is_dir = is_dir(base_path)
    len_base_path = len(base_path)

    ignores = ignore.ignores_VCS
    if on_linux:
        ignores = {path_to_bytes(k): v for k, v in ignores.items()}
    else:
        ignores = {path_to_unicode(k): v for k, v in ignores.items()}
    ignorer = partial(ignore.is_ignored, ignores=ignores, unignores={}, skip_special=True)

    locations = resource_iter(base_path, ignored=ignorer, with_dirs=True)
    for abs_path in locations:
        resource = Resource(scans_cache_class, abs_path, base_is_dir, len_base_path)
        # FIXME: they should be kept in memory instead
        # always fetch infos and cache them.
        infos = scan_infos(abs_path, diag=diag)
        resource.put_info(infos)
        yield resource


def scan_infos(input_file, diag=False):
    """
    Scan one file or directory and return file_infos data. This always
    contains an extra 'errors' key with a list of error messages,
    possibly empty. If `diag` is True, additional diagnostic messages
    are included.
    """
    # FIXME: WE SHOULD PROCESS THIS IS MEMORY AND AS PART OF THE SCAN PROPER... and BOTTOM UP!!!!
    # THE PROCESSING TIME OF SIZE AGGREGATION ON DIRECTORY IS WAY WAY TOO HIGH!!!
    errors = []
    try:
        infos = get_file_infos(input_file)
    except Exception as e:
        # never fail but instead add an error message.
        infos = _empty_file_infos()
        errors = ['ERROR: infos: ' + e.message]
        if diag:
            errors.append('ERROR: infos: ' + traceback.format_exc())
    # put errors last
    infos['scan_errors'] = errors
    return infos


def scan_one(location, scanners, diag=False):
    """
    Scan one file or directory at `location` and return a scan result
    mapping, calling every scanner callable in the `scanners` list of Scanners.

    The scan result mapping contain a 'scan_errors' key with a list of
    error messages. If `diag` is True, 'scan_errors' error messages also
    contain detailed diagnostic information such as a traceback if
    available.
    """
    if on_linux:
        location = path_to_bytes(location)
    else:
        location = path_to_unicode(location)

    scan_result = OrderedDict()
    scan_errors = []
    for scanner in scanners:
        try:
            scan_details = scanner.function(location)
            # consume generators
            if isinstance(scan_details, GeneratorType):
                scan_details = list(scan_details)
            scan_result[scanner.name] = scan_details
        except TimeoutError:
            raise
        except Exception as e:
            # never fail but instead add an error message and keep an empty scan:
            scan_result[scanner.name] = []
            messages = ['ERROR: ' + scanner.name + ': ' + e.message]
            if diag:
                messages.append('ERROR: ' + scanner.name + ': ' + traceback.format_exc())
            scan_errors.extend(messages)

    # put errors last, after scans proper
    scan_result['scan_errors'] = scan_errors
    return scan_result


def save_results(scanners, files_count, results, format, options, input, output_file):
    """
    Save scan results to file or screen.
    """

    # note: in tests, sys.stdout is not used, but is instead some io
    # wrapper with no name attributes. We use this to check if this is a
    # real filesystem file or not.
    # note: sys.stdout.name == '<stdout>' so it has a name.
    is_real_file = hasattr(output_file, 'name')

    if output_file != sys.stdout and is_real_file:
        # we are writing to a real filesystem file: create directories!
        parent_dir = os.path.dirname(output_file.name)
        if parent_dir:
            create_dir(abspath(expanduser(parent_dir)))

    # Write scan results to file or screen as a formatted output ...
    # ... using a user-provided custom format template
    format_plugins = plugincode.output.get_format_plugins()
    if format not in format_plugins:
        # format may be a custom template file path
        if not os.path.isfile(format):
            # this check was done before in the CLI validation, but this
            # is done again if the function is used directly
            echo_stderr('\nInvalid template: must be a file.', fg='red')
        else:
            from formattedcode import format_templated
            # FIXME: carrying an echo function does not make sense
            format_templated.write_custom(
                results, output_file, _echo=echo_stderr, version=version, template_path=format)

    # ... or  using the selected format plugin
    else:
        writer = format_plugins[format]
        # FIXME: carrying an echo function does not make sense
        # FIXME: do not use input as a variable name
        # FIXME: do NOT pass options around, but a header instead
        opts = OrderedDict([(o.option, o.value) for o in options])
        writer(files_count=files_count, version=version, notice=notice,
               scanned_files=results,
               options=opts,
               input=input, output_file=output_file, _echo=echo_stderr)


def get_command_options(ctx, ignores=(), skip_default=False, skip_no_group=False):
    """
    Yield CommandOption tuples for each Click option in the `ctx` Click context.
    Ignore:
    - eager flags,
    - Parameter with a "name" listed in the `ignores` sequence
    - Parameters whose value is the default if `skip_default` is True
    - Parameters without a group if `skip_no_group` is True
    """
    param_values = ctx.params
    for param in ctx.command.params:

        if param.is_eager:
            continue

        group = getattr(param, 'group', None)
        if skip_no_group and not group:
            continue

        name = param.name
        if ignores and name in ignores:
            continue

        # opts is a list, the last one is the long form by convention
        option = param.opts[-1]

        value = param_values.get(name)
        # for opened file args that may have a name
        if value and hasattr(value, 'name'):
            value = getattr(value, 'name', None)

        default = param.default

        if skip_default and value == default:
            continue

        yield CommandOption(group, name, option, value, default)
