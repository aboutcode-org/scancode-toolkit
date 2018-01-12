#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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
from __future__ import division
from __future__ import print_function
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

import click
click.disable_unicode_literals_warning = True

from commoncode.fileutils import create_dir
from commoncode.fileutils import PATH_TYPE

import plugincode.output
import plugincode.post_scan
import plugincode.pre_scan

from scancode import __version__ as version
from scancode import ScanOption
from scancode.api import DEJACODE_LICENSE_URL
from scancode.api import get_copyrights
from scancode.api import get_emails
from scancode.api import get_file_info
from scancode.api import get_licenses
from scancode.api import get_package_infos
from scancode.api import get_urls
from scancode.interrupt import DEFAULT_TIMEOUT
from scancode.interrupt import interruptible
from scancode.resource import Codebase
from scancode.resource import Resource
from scancode.utils import BaseCommand
from scancode.utils import progressmanager
from scancode.utils import path_progress_message

# Python 2 and 3 support
try:
    # Python 2
    unicode
    str_orig = str
    bytes = str  # @ReservedAssignment
    str = unicode  # @ReservedAssignment
except NameError:
    # Python 3
    unicode = str  # @ReservedAssignment


echo_stderr = partial(click.secho, err=True)

# this discovers and validates avialable plugins
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

    def __init__(self, name, context_settings=None, callback=None, params=None,
                 help=None,  # @ReservedAssignment
                 epilog=None, short_help=None,
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
    if value_lower in plugincode.output.get_plugins():
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
    (PRE_SCAN, plugincode.pre_scan.get_plugins()),
    (POST_SCAN, plugincode.post_scan.get_plugins()),
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
                    'as the path to a custom template file' % ', '.join(plugincode.output.get_plugins())),
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
@click.option('--no-cache', is_flag=True, default=False, is_eager=False, help='Do not use on-disk cache for scan results. Faster but uses more memory.', group=CORE, cls=ScanOption)
@click.option('--reindex-licenses', is_flag=True, default=False, is_eager=True, callback=reindex_licenses, help='Force a check and possible reindexing of the cached license index.', group=MISC, cls=ScanOption)

def scancode(ctx,
             input,  # @ReservedAssignment
             output_file, infos,
             verbose, quiet, processes, diag, timeout, no_cache,
             *args, **kwargs):
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

    strip_root = kwargs.get('strip_root')
    full_root = kwargs.get('full_root')
    format = kwargs.get('format')  # @ReservedAssignment
    # ## TODO: END FIX when plugins are used everywhere

    get_licenses_with_score = partial(get_licenses,
        diag=diag,
        min_score=kwargs.get('license_score'),
        include_text=kwargs.get('license_text'),
        license_url_template=kwargs.get('license_url_template'))

    # Use default scan options when no scan option is provided
    # FIXME: this should be removed?
    use_default_scans = not any([infos, licenses, copyrights, packages, emails, urls])

    # FIXME: A hack to force info being exposed for SPDX output in order to
    # reuse calculated file SHA1s.
    is_spdx = format in ('spdx-tv', 'spdx-rdf')


    scanners = [scan for scan in [
            # FIXME: we enable infos at all times!!!
            Scanner('infos', get_file_info, True),
            Scanner('licenses', get_licenses_with_score, licenses or use_default_scans),
            Scanner('copyrights', get_copyrights, copyrights or use_default_scans),
            Scanner('packages', get_package_infos, packages or use_default_scans),
            Scanner('emails', get_emails, emails),
            Scanner('urls', get_urls, urls)]
        if scan.is_enabled
    ]

    ignored_options = 'verbose', 'quiet', 'processes', 'timeout'
    all_options = list(get_command_options(ctx, ignores=ignored_options, skip_no_group=True))

    scanner_names = [scan.name for scan in scanners if scan.is_enabled]
    scan_names = ', '.join(scanner_names)
    if not quiet:
        echo_stderr('Scanning files for: %(scan_names)s with %(processes)d process(es)...' % locals())

    if not quiet and not processes:
        echo_stderr('Disabling multi-processing and multi-threading...', fg='yellow')

    # FIXME: this is terribly hackish :|
    # FIXUP OPTIONS FOR DEFAULT SCANS
    options = []
    for opt in all_options:
        if opt.name in scanner_names:
            options.append(opt._replace(value=True))
            continue

        # do not report option set to defaults or with an empty list value
        if isinstance(opt.value, (list, tuple)):
            if opt.value:
                options.append(opt)
            continue
        if opt.value != opt.default:
            options.append(opt)

    processing_start = time()
    if not quiet:
        echo_stderr('Collecting file inventory...' % locals(), fg='green')
    # TODO: add progress indicator
    codebase = Codebase(location=input, use_cache=not no_cache)
    collect_time = time() - processing_start

    license_indexing_start = time()
    try:
        ###############################################################
        # SCANNERS SETUP
        ###############################################################
        license_indexing_time = 0
        # FIXME: this should be moved as the setup() for a license plugin
        with_licenses = any(sc for sc in scanners if sc.name == 'licenses' and sc.is_enabled)
        if with_licenses:
            # build index outside of the main loop for speed
            # FIXME: REALLY????? this also ensures that forked processes will get the index on POSIX naturally
            if not quiet:
                echo_stderr('Building/Loading license detection index...', fg='green', nl=False)
            # TODO: add progress indicator
            from licensedcode.cache import get_index
            get_index(False)
            license_indexing_time = time() - license_indexing_start
            if not quiet:
                echo_stderr('Done.', fg='green')

        ###############################################################
        # PRE-SCAN
        ###############################################################
        pre_scan_start = time()
        # TODO: add progress indicator
        for name, plugin in plugincode.pre_scan.get_plugins().items():
            plugin = plugin(all_options, scanner_names)
            if plugin.is_enabled():
                if not quiet:
                    name = name or plugin.__class__.__name__
                    echo_stderr('Running pre-scan plugin: %(name)s...' % locals(), fg='green')
                # FIXME: we should always catch errors from plugins properly
                plugin.process_codebase(codebase)
                codebase.update_counts()

        pre_scan_time = time() - pre_scan_start

        ###############################################################
        # SCANS RUN
        ###############################################################
        scan_start = time()
        if not quiet:
            echo_stderr('Scanning files...', fg='green')

        progress_manager = None
        if not quiet:
            item_show_func = partial(path_progress_message, verbose=verbose)
            progress_manager = partial(progressmanager,
                item_show_func=item_show_func, verbose=verbose, file=sys.stderr)

        # TODO: add CLI option to bypass cache entirely
        success = scan_codebase(codebase, scanners, processes, timeout,
                                progress_manager=progress_manager)

        scan_time = time() - scan_start

        scanned_count, _, scanned_size = codebase.counts(update=True, skip_root=False)

        ###############################################################
        # POST-SCAN
        ###############################################################
        # TODO: add progress indicator
        post_scan_start = time()

        for name, plugin in plugincode.post_scan.get_plugins().items():
            plugin = plugin(all_options, scanner_names)
            if plugin.is_enabled():
                if not quiet:
                    name = name or plugin.__class__.__name__
                    echo_stderr('Running post-scan plugin: %(name)s...' % locals(), fg='green')
                # FIXME: we should always catch errors from plugins properly
                plugin.process_codebase(codebase)
                codebase.update_counts()

        post_scan_time = time() - post_scan_start


        ###############################################################
        # SUMMARY
        ###############################################################
        total_time = time() - processing_start

        files_count, dirs_count, size = codebase.counts(
            update=True, skip_root=strip_root)

        if not quiet:
            display_summary(codebase, scan_names, processes,
                            total_time, license_indexing_time,
                            pre_scan_time,
                            scanned_count, scanned_size, scan_time,
                            post_scan_time,
                            files_count, dirs_count, size,
                            verbose)

        ###############################################################
        # FORMATTED REPORTS OUTPUT
        ###############################################################
        if not quiet:
            echo_stderr('Saving results...', fg='green')

        # FIXME: we should have simpler args: a scan "header" and scan results
        # FIXME: we should use Codebase.resources instead of results
        with_info = infos or is_spdx
        serializer = partial(Resource.to_dict, full_root=full_root, strip_root=strip_root, with_info=with_info)
        results = [serializer(res) for res in codebase.walk(topdown=True, sort=True, skip_root=strip_root)]
        save_results(results, files_count, format, options, input, output_file)

    finally:
        # cleanup
        codebase.clear()

    rc = 0 if success else 1
    ctx.exit(rc)


def display_summary(codebase, scan_names, processes,
                    total_time,
                    license_indexing_time,
                    pre_scan_time,
                    scanned_count, scanned_size, scan_time,
                    post_scan_time,
                    files_count, dirs_count, size,
                    verbose):
    """
    Display a scan summary.
    """
    top_errors = codebase.errors
    path_errors = [(r.get_path(decode=True, posix=True), r.errors) for r in codebase.walk() if r.errors]

    has_errors = top_errors or path_errors
    echo_stderr('Scanning done.', fg=has_errors and 'red' or 'green')

    errors_count = 0
    if has_errors:
        echo_stderr('Some files failed to scan properly:', fg='red')
        for error in top_errors:
            echo_stderr(error)
            errors_count += 1
        for errored_path, errors in path_errors:
            echo_stderr('Path: ' + errored_path, fg='red')
            if not verbose:
                continue
            for error in errors:
                for emsg in error.splitlines(False):
                    echo_stderr('  ' + emsg, fg='red')
                errors_count += 1

    sym = 'Bytes'
    if size >= 1024 * 1024 * 1024:
        sym = 'GB'
        size = size / (1024 * 1024 * 1024)
    elif size >= 1024 * 1024:
        sym = 'MB'
        size = size / (1024 * 1024)
    elif size >= 1024:
        sym = 'KB'
        size = size / 1024
    size = round(size, 2)

    scan_sym = 'Bytes'
    if scanned_size >= 1024 * 1024 * 1024:
        scan_sym = 'GB'
        scanned_size = scanned_size / (1024 * 1024 * 1024)
    elif scanned_size >= 1024 * 1024:
        scan_sym = 'MB'
        scanned_size = scanned_size / (1024 * 1024)
    elif scanned_size >= 1024:
        scan_sym = 'KB'
        scanned_size = scanned_size / 1024
    size_speed = round(scanned_size / scan_time, 2)
    scanned_size = round(scanned_size, 2)

    file_speed = round(float(scanned_count) / scan_time , 2)

    res_count = files_count + dirs_count
    echo_stderr('Summary:        %(scan_names)s with %(processes)d process(es)' % locals())
    echo_stderr('Total time:     %(scanned_count)d files, %(scanned_size).2f %(scan_sym)s '
                                 'scanned in %(total_time)d total (excluding format)' % locals())
    echo_stderr('Scan Speed:     %(file_speed).2f files/s, %(size_speed).2f %(scan_sym)s/s' % locals())
    echo_stderr('Results:        %(res_count)d resources: %(files_count)d files, %(dirs_count)d directories for %(size).2f %(sym)s' % locals())
    echo_stderr('Timings:        Indexing: %(license_indexing_time).2fs, '
                                'Pre-scan: %(pre_scan_time).2fs, '
                                'Scan: %(scan_time).2fs, '
                                'Post-scan: %(post_scan_time).2fs' % locals())
    echo_stderr('Errors count:   %(errors_count)d' % locals())


def scan_codebase(codebase, scanners, processes=1, timeout=DEFAULT_TIMEOUT,
                  progress_manager=None):
    """
    Run the `scanners` on the `codebase`. Return True on success or False
    otherwise. Provides optional progress feedback in the UI using the
    `progress_manager` callable that accepts an iterable of tuple of (location,
    rid, scan_errors, scan_result ) as argument.
    """

    # FIXME: this path computation is super inefficient
    # tuples of  (absolute location, resource id)
    # TODO: should we alk topdown or not???
    resources = ((r.get_path(absolute=True), r.rid) for r in codebase.walk())

    runner = partial(scan_resource, scanners=scanners, timeout=timeout)

    has_info_scanner = any(sc.name == 'infos' for sc in scanners)
    lscan = len(scanners)
    has_other_scanners = lscan > 1 if has_info_scanner else lscan

    get_resource = codebase.get_resource

    success = True
    pool = None
    scans = None
    try:
        if processes:
            # maxtasksperchild helps with recycling processes in case of leaks
            pool = get_pool(processes=processes, maxtasksperchild=1000)
            # Using chunksize is documented as much more efficient in the Python doc.
            # Yet "1" still provides a better and more progressive feedback.
            # With imap_unordered, results are returned as soon as ready and out of order.
            scans = pool.imap_unordered(runner, resources, chunksize=1)
            pool.close()
        else:
            # no multiprocessing with processes=0
            scans = imap(runner, resources)

        if progress_manager:
            scans = progress_manager(scans)
            # hack to avoid using a context manager
            if hasattr(scans, '__enter__'):
                scans.__enter__()

        while True:
            try:
                location, rid, scan_errors, scan_result = scans.next()

                resource = get_resource(rid)
                if not resource:
                    # this should never happen
                    msg = ('ERROR: Internal error in scan_codebase: Resource '
                           'at %(location)r is missing from codebase.\n'
                           'Scan result not saved:\n%(scan_result)r.' % locals())
                    codebase.errors.append(msg)
                    success = False
                    continue

                if scan_errors:
                    success = False
                    resource.errors.extend(scan_errors)

                if has_info_scanner:
                    # always set info directly on resources
                    info = scan_result.pop('infos', [])
                    resource.set_info(info)
                if has_info_scanner and scan_result:
                    resource.put_scans(scan_result, update=True)

            except StopIteration:
                break
            except KeyboardInterrupt:
                echo_stderr('\nAborted with Ctrl+C!', fg='red')
                success = False
                if pool:
                    pool.terminate()
                break

    finally:
        if pool:
            # ensure the pool is really dead to work around a Python 2.7.3 bug:
            # http://bugs.python.org/issue15101
            pool.terminate()

        if scans and hasattr(scans, 'render_finish'):
            # hack to avoid using a context manager
            scans.render_finish()
    return success


def scan_resource(location_rid, scanners, timeout=DEFAULT_TIMEOUT):
    """
    Return a tuple of (location, rid, list or errors, mapping of scan results) by running
    the `scanners` Scanner objects for the file or directory resource with id
    `rid` at `location` provided as a `location_rid` tuple (location, rid).
    """
    location, rid = location_rid
    errors = []
    results = OrderedDict((scanner.name, []) for scanner in scanners)

    # run each scanner in sequence in its own interruptible
    for scanner, scanner_result in zip(scanners, results.values()):
        try:
            runner = partial(scanner.function, location)
            error, value = interruptible(runner, timeout=timeout)
            if error:
                msg = 'ERROR: for scanner: ' + scanner.name + ':\n' + error
                errors.append(msg)
            if value:
                # a scanner function MUST return a sequence
                scanner_result.extend(value)
        except Exception:
            msg = 'ERROR: for scanner: ' + scanner.name + ':\n' + traceback.format_exc()
            errors.append(msg)
    return location, rid, errors, results


def save_results(results, files_count,
                 format,  # @ReservedAssignment
                 options,
                 input,  # @ReservedAssignment
                 output_file):
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
    format_plugins = plugincode.output.get_plugins()

    if format in format_plugins:
    # use the selected format plugin
        writer = format_plugins[format]
        # FIXME: carrying an echo function does not make sense
        # FIXME: do not use input as a variable name
        # FIXME: do NOT pass options around, but a header instead
        opts = OrderedDict([(o.option, o.value) for o in options])
        writer(files_count=files_count, version=version, notice=notice,
               scanned_files=results,
               options=opts,
               input=input, output_file=output_file, _echo=echo_stderr)
        return

    # format may be a custom template file path
    if not os.path.isfile(format):
        # this check was done before in the CLI validation, but this
        # is done again if the function is used directly
        echo_stderr('\nInvalid template: must be a file.', fg='red')
    else:
        from formattedcode import format_templated
        # FIXME: carrying an echo function does not make sense
        format_templated.write_custom(
            results, output_file,
            _echo=echo_stderr, version=version, template_path=format)


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
