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

# Import first because this import has monkey-patching side effects
from scancode.pool import get_pool

from collections import OrderedDict
from functools import partial
from itertools import imap
from os.path import abspath
from os.path import dirname
from os.path import join
import sys
from time import time
import traceback

import click
click.disable_unicode_literals_warning = True

# import early
from scancode_config import __version__ as scancode_version
from scancode_config import scancode_temp_dir, scancode_cache_dir

from commoncode.fileutils import PATH_TYPE
from commoncode.timeutils import time2tstamp

from plugincode import CommandLineOption
from plugincode import PluginManager

# these are important to register plugin managers
from plugincode import pre_scan
from plugincode import scan
from plugincode import post_scan
from plugincode import output_filter
from plugincode import output

from scancode import CORE_GROUP
from scancode import DOC_GROUP
from scancode import MISC_GROUP
from scancode import OTHER_SCAN_GROUP
from scancode import OUTPUT_GROUP
from scancode import OUTPUT_FILTER_GROUP
from scancode import OUTPUT_CONTROL_GROUP
from scancode import POST_SCAN_GROUP
from scancode import PRE_SCAN_GROUP
from scancode import SCAN_GROUP
from scancode import SCAN_OPTIONS_GROUP
from scancode import Scanner
from scancode import validate_option_dependencies
from scancode.api import get_file_info
from scancode.interrupt import DEFAULT_TIMEOUT
from scancode.interrupt import fake_interruptible
from scancode.interrupt import interruptible
from scancode.resource import Codebase
from scancode.utils import BaseCommand
from scancode.utils import path_progress_message
from scancode.utils import progressmanager

# Python 2 and 3 support
try:
    # Python 2
    unicode
    str_orig = str
    bytes = str  # NOQA
    str = unicode  # NOQA
except NameError:
    # Python 3
    unicode = str  # NOQA


# Tracing flags
TRACE = False
TRACE_DEEP = False

def logger_debug(*args):
    pass

if TRACE or TRACE_DEEP:
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, unicode)
                                     and a or repr(a) for a in args))


echo_stderr = partial(click.secho, err=True)


info_text = '''
ScanCode scans code and other files for origin and license.
Visit https://github.com/nexB/scancode-toolkit/ for support and download.

'''

notice_path = join(abspath(dirname(__file__)), 'NOTICE')
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


# FIXME: this should be pushed out in some external help or pushed down in plugins.
# FIXME: the glob story is very weird!!!
examples_text = '''
Scancode command lines examples:

(Note for Windows: use '\\' back slash instead of '/' forward slash for paths.)

Scan a single file for copyrights. Print scan results to stdout as JSON:

    scancode --copyright samples/zlib/zlib.h --json

Scan a single file for licenses, print verbose progress to stderr as each
file is scanned. Save scan to a JSON file:

    scancode --license --verbose samples/zlib/zlib.h --json licenses.json

Scan a directory explicitly for licenses and copyrights. Redirect JSON scan
results to a file:

    scancode --json -l -c samples/zlib/ > scan.json

Scan a directory while ignoring a single file.
Print scan results to stdout as JSON:

    scancode --json  --ignore README samples/

Scan a directory while ignoring all files with .txt extension.
Print scan results to stdout as JSON.
It is recommended to use quotes around glob patterns to prevent pattern
expansion by the shell:

    scancode --json --ignore "*.txt" samples/

Special characters supported in GLOB pattern:
- *       matches everything
- ?       matches any single character
- [seq]   matches any character in seq
- [!seq]  matches any character not in seq

For a literal match, wrap the meta-characters in brackets.
For example, '[?]' matches the character '?'.
For details on GLOB patterns see https://en.wikipedia.org/wiki/Glob_(programming).

Note: Glob patterns cannot be applied to path as strings.
For example, this will not ignore "samples/JGroups/licenses".

    scancode --json --ignore "samples*licenses" samples/


Scan a directory while ignoring multiple files (or glob patterns).
Print the scan results to stdout as JSON:

    scancode --json --ignore README --ignore "*.txt" samples/

Scan the 'samples' directory for licenses and copyrights. Save scan results to
an HTML app file for interactive scan results navigation. When the scan is done,
open 'scancode_result.html' in your web browser. Note that additional app files
are saved in a directory named 'scancode_result_files':

    scancode --output-html-app scancode_result.html samples/

Scan a directory for licenses and copyrights. Save scan results to an
HTML file:

    scancode --output-html scancode_result.html samples/zlib

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
    click.echo('ScanCode version ' + scancode_version)
    ctx.exit()


# FIXME: this should be pushed out in some external help or pushed down in plugins.
epilog_text = '''Examples (use --examples for more):

\b
Scan the 'samples' directory for licenses and copyrights.
Save scan results to the 'scancode_result.json' JSON file:

    scancode --license --copyright --json=scancode_result.json samples

\b
Scan the 'samples' directory for licenses and package manifests. Print scan
results on screen as pretty-formatted JSON (using the special '-' FILE to print
to on screen/to stdout):

    scancode --json-pp - --license --package  samples

Note: when you run scancode, a progress bar is displayed with a counter of the
number of files processed. Use --verbose to display file-by-file progress.
'''


class ScanCommand(BaseCommand):
    """
    A command class that is aware of ScanCode options that provides enhanced
    help where each option is grouped by group.
    """

    short_usage_help = '''
Try 'scancode --help' for help on options and arguments.'''

    def __init__(self, name, context_settings=None, callback=None, params=None,
                 help=None,  # NOQA
                 epilog=None, short_help=None,
                 options_metavar='[OPTIONS]', add_help_option=True,
                 plugin_options=()):
        """
        Create a new ScanCommand using the `plugin_options` list of
        CommandLineOption instances.
        """

        super(ScanCommand, self).__init__(name, context_settings, callback,
             params, help, epilog, short_help, options_metavar, add_help_option)

        # this makes the options "known" to the command
        self.params.extend(plugin_options)

    def format_options(self, ctx, formatter):
        """
        Overridden from click.Command to write all options into the formatter in
        help_groups they belong to. If a group is not specified, add the option
        to MISC_GROUP group.
        """
        # this mapping defines the CLI help presentation order
        help_groups = OrderedDict([
            (SCAN_GROUP, []),
            (OTHER_SCAN_GROUP, []),
            (SCAN_OPTIONS_GROUP, []),
            (OUTPUT_GROUP, []),
            (OUTPUT_FILTER_GROUP, []),
            (OUTPUT_CONTROL_GROUP, []),
            (PRE_SCAN_GROUP, []),
            (POST_SCAN_GROUP, []),
            (CORE_GROUP, []),
            (MISC_GROUP, []),
            (DOC_GROUP, []),
        ])

        for param in self.get_params(ctx):
            # Get the list of option's name and help text
            help_record = param.get_help_record(ctx)
            if not help_record:
                continue
            # organize options by group
            help_group = getattr(param, 'help_group', MISC_GROUP)
            sort_order = getattr(param, 'sort_order', 100)
            help_groups[help_group].append((sort_order, help_record))

        with formatter.section('Options'):
            for group, help_records in help_groups.items():
                if not help_records:
                    continue
                with formatter.section(group):
                    sorted_records = [help_record for _, help_record in sorted(help_records)]
                    formatter.write_dl(sorted_records)


# IMPORTANT: this discovers, loads and validates all available plugins
plugin_classes, plugin_options = PluginManager.setup_all()


def print_plugins(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    for plugin_cls in sorted(plugin_classes, key=lambda pc: (pc.stage, pc.name)):
        click.echo('--------------------------------------------')
        click.echo('Plugin: scancode_{self.stage}:{self.name}'.format(self=plugin_cls), nl=False)
        click.echo('  class: {self.__module__}:{self.__name__}'.format(self=plugin_cls))
        requires = ', '.join(plugin_cls.requires)
        click.echo('  requires: {}'.format(requires), nl=False)
        needs_info = getattr(plugin_cls, 'needs_info', False)
        if needs_info:
            click.echo(' needs_info: yes')
        else:
            click.echo('')
        click.echo('  doc: {self.__doc__}'.format(self=plugin_cls))
        click.echo('  options:'.format(self=plugin_cls))
        for option in plugin_cls.options:
            name = option.name
            opts = ', '.join(option.opts)
            help_group = option.help_group
            help_txt = option.help  # noqa
            click.echo('    help_group: {help_group!s}, name: {name!s}: {opts}\n      help: {help_txt!s}'.format(**locals()))
        click.echo('')
    ctx.exit()


@click.command(name='scancode',
    epilog=epilog_text,
    cls=ScanCommand,
    plugin_options=plugin_options)

@click.pass_context

# ensure that the input path is bytes on Linux, unicode elsewhere
@click.argument('input', metavar='<input> <OUTPUT FORMAT OPTION(s)>',
    type=click.Path(exists=True, readable=True, path_type=PATH_TYPE))

@click.option('-i', '--info',
    is_flag=True,
    help='Scan <input> for file information (size, type, checksums, etc).',
    help_group=OTHER_SCAN_GROUP, sort_order=10, cls=CommandLineOption)

@click.option('--strip-root',
    is_flag=True,
    conflicts=['full_root'],
    help='Strip the root directory segment of all paths. The default is to '
         'always include the last directory segment of the scanned path such '
         'that all paths have a common root directory.',
    help_group=OUTPUT_CONTROL_GROUP, cls=CommandLineOption)

@click.option('--full-root',
    is_flag=True,
    conflicts=['strip_root'],
    help='Report full, absolute paths. The default is to always '
         'include the last directory segment of the scanned path such that all '
         'paths have a common root directory.',
    help_group=OUTPUT_CONTROL_GROUP, cls=CommandLineOption)

@click.option('-n', '--processes',
    type=int, default=1,
    metavar='INT',
    help='Set the number of parallel processes to use. '
         'Disable parallel processing if 0. Also disable threading if -1. [default: 1]',
    help_group=CORE_GROUP, sort_order=10, cls=CommandLineOption)

@click.option('--timeout',
    type=float, default=DEFAULT_TIMEOUT,
    metavar='<secs>',
    help='Stop an unfinished file scan after a timeout in seconds.  '
         '[default: %d seconds]' % DEFAULT_TIMEOUT,
    help_group=CORE_GROUP, sort_order=10, cls=CommandLineOption)

@click.option('--quiet',
    is_flag=True,
    conflicts=['verbose'],
    help='Do not print summary or progress.',
    help_group=CORE_GROUP, sort_order=20, cls=CommandLineOption)

@click.option('--verbose',
    is_flag=True,
    conflicts=['quiet'],
    help='Print progress  as file-by-file path instead of a progress bar. '
         'Print a verbose scan summary.',
    help_group=CORE_GROUP, sort_order=20, cls=CommandLineOption)

@click.option('--cache-dir',
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True,
        readable=True, path_type=PATH_TYPE),
    default=scancode_cache_dir,
    metavar='DIR',
    sort_order=210,

    help='Set the path to an existing directory where ScanCode can cache '
         'files available across runs.'

         'If not set, the value of the `SCANCODE_CACHE` environment variable is '
         'used if available. If `SCANCODE_CACHE` is not set, a default '
         'sub-directory in the user home directory is used instead. '
         '[default: ~/.cache/scancode-tk/version]',
    help_group=CORE_GROUP,
    cls=CommandLineOption)

@click.option('--temp-dir',
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True,
        readable=True, path_type=PATH_TYPE),
    default=scancode_temp_dir,
    show_default=False,
    metavar='DIR',
    sort_order=210,
    help='Set the path to an existing directory where ScanCode can create '
         'temporary files. '
         'If not set, the value of the `SCANCODE_TMP` environment variable is '
         'used if available. If `SCANCODE_TMP` is not set, a default '
         'sub-directory in the system temp directory is used instead.  '
         '[default: TMP/scancode-tk-<key>]',
    help_group=CORE_GROUP,
    cls=CommandLineOption)

@click.option('--timing',
    is_flag=True,
    help='Collect scan timing for each scan/scanned file.',
    help_group=CORE_GROUP, sort_order=250, cls=CommandLineOption)

@click.option('--on-disk-results',
    is_flag=True, default=True,
    show_default=True,
    help='Save intermediate scan results in temporary files. Uses less memory.',
    help_group=CORE_GROUP, sort_order=300, cls=CommandLineOption)

@click.help_option('-h', '--help',
    help_group=DOC_GROUP, sort_order=10, cls=CommandLineOption)

@click.option('--about',
    is_flag=True, is_eager=True,
    callback=print_about,
    help='Show information about ScanCode and licensing and exit.',
    help_group=DOC_GROUP, sort_order=20, cls=CommandLineOption)

@click.option('--version',
    is_flag=True, is_eager=True,
    callback=print_version,
    help='Show the version and exit.',
    help_group=DOC_GROUP, sort_order=20, cls=CommandLineOption)

@click.option('--examples',
    is_flag=True, is_eager=True,
    callback=print_examples,
    help=('Show command examples and exit.'),
    help_group=DOC_GROUP, sort_order=50, cls=CommandLineOption)

@click.option('--plugins',
    is_flag=True, is_eager=True,
    callback=print_plugins,
    help='Show the list of available ScanCode plugins and exit.',
    help_group=DOC_GROUP, cls=CommandLineOption)

@click.option('--test-mode',
    is_flag=True, default=False,
    # not yet supported in Click 6.7 but added in CommandLineOption
    hidden=True,
    help='Run ScanCode in a special "test mode". Only for testing.',
    help_group=MISC_GROUP, sort_order=1000, cls=CommandLineOption)

def scancode(ctx, input, #NOQA
             info,
             strip_root, full_root,
             processes, timeout,
             quiet, verbose,
             cache_dir, temp_dir,
             timing,
             on_disk_results,
             test_mode,
             *args, **kwargs):
    """scan the <input> file or directory for license, origin and packages and save results to FILE(s) using one or more ouput format option.

    Error and progress are printed to stderr.
    """

    # notes: the above docstring of this function is used in the CLI help Here is
    # it's actual docstring:
    """
    This function is the main ScanCode CLI entry point.

    Return a return code of 0 on success or a positive integer on error from
    running all the scanning "stages" with the `input` file or
    directory.

    The scanning stages are:

    - `inventory`: collect the codebase inventory resources tree for the
      `input`. This is a built-in stage that does not accept plugins.

    - `setup`: as part of the plugins system, each plugin is loaded and
      its `setup` method is called if it is enabled.

    - `pre-scan`: each enabled pre-scan plugin `process_codebase(codebase)`
      method is called to update/transforme the whole codebase.

    - `scan`: the codebase is walked and each enabled scan plugin
      `get_scanner()(resource.location)` scanner function is called once for
      each codebase resource.

    - `post-scan`: each enabled post-scan plugin `process_codebase(codebase)`
      method is called to update/transforme the whole codebase.

    - `output_filter`: the `process_resource` method of each enabled
      output_filter plugin is called on each resource to determine if the
      resource should be kept or not in the output stage.

    - `output`: each enabled output plugin `process_codebase(codebase)`
      method is called to create an output for the codebase filtered resources.

    Beside `input`, the other arguments are:

    - `strip_root` and `full_root`: boolean flags: In the outputs, strip the
      first path segment of a file if `strip_root` is True unless the `input` is
      a single file. If `full_root` is True report the path as an absolute path.
      These options are mutually exclusive.

    - `processes`: int: run the scan using up to this number of processes in
      parallel. If 0, disable the multiprocessing machinery. if -1 also
      disable the multithreading machinery.

    - `timeout`: float: intterup the scan of a file if it does not finish within
      `timeout` seconds. This applied to each file and scan individually (e.g.
      if the license scan is interrupted they other scans may complete, each
      withing the timeout)

    - `quiet` and `verbose`: boolean flags: Do not display any message if
      `quiet` is True. Otherwise, display extra verbose messages if `quiet` is
      False and `verbose` is True. These two options are mutually exclusive.

    - `cache_dir` and `temp_dir`: paths to alternative directories for caching
      and temporary files.

    - `timing`: boolean flag: collect per-scan and per-file scan timings if
      True.

    - `on_disk_results`: boolean flag: default to True to enable on-disk saving
      of intermediate scan results.

    - `temp_dir`: path to a non-default temporary directory fo caching and other
      temporary files. If not provided, the default is used.

    Other **kwargs are passed down to plugins as CommandOption indirectly
    through Click context machinery.
    """

    # build mappings of all kwargs to pass down to plugins
    standard_kwargs = dict(
        input=input,
        info=info,
        strip_root=strip_root, full_root=full_root,
        processes=processes, timeout=timeout,
        quiet=quiet, verbose=verbose,
        cache_dir=cache_dir, temp_dir=temp_dir,
        timing=timing,
        on_disk_results=on_disk_results,
        test_mode=test_mode
    )
    kwargs.update(standard_kwargs)

    success = True
    codebase = None
    processing_start = time()

    # UTC start timestamp
    scan_start = time2tstamp()

    try:

        if not processes and not quiet:
            echo_stderr('Disabling multi-processing for debugging.', fg='yellow')
        if processes == -1  and not quiet:
            echo_stderr('Disabling multi-processing and multi-threading for debugging.', fg='yellow')

        ########################################################################
        # 1. get command options and create all plugin instances
        ########################################################################
        validate_option_dependencies(ctx)

        if TRACE_DEEP:
            ctx_params = sorted(ctx.params.items())
            logger_debug('scancode: ctx.params:')
            for co in ctx.params:
                logger_debug('  scancode: ctx.params:', co)

        enabled_plugins = OrderedDict()

        for stage, manager in PluginManager.managers.items():
            enabled_plugins[stage] = stage_plugins = OrderedDict()
            for name, plugin_cls in manager.plugin_classes.items():
                try:
                    plugin = plugin_cls(**kwargs)
                    if plugin.is_enabled(**kwargs):
                        # Set special test mode flag that plugins can leverage
                        plugin._test_mode = test_mode
                        stage_plugins[name] = plugin
                except:
                    msg = 'ERROR: failed to load plugin: %(stage)s:%(name)s:' % locals()
                    echo_stderr(msg, fg='red')
                    echo_stderr(traceback.format_exc())
                    ctx.exit(2)

        # these are plugin instances, not classes
        pre_scan_plugins = enabled_plugins[pre_scan.stage]
        scanner_plugins = enabled_plugins[scan.stage]
        post_scan_plugins = enabled_plugins[post_scan.stage]
        output_filter_plugins = enabled_plugins[output_filter.stage]
        output_plugins = enabled_plugins[output.stage]

        if not output_plugins:
            msg = ('Missing output option(s): at least one output '
                   'option is needed to save scan results.')
            raise click.UsageError(msg)

        # Use default info scan when no other scan options are requested
        if not scanner_plugins and not info:
            # add info scan as scan option/kwarg/locals()
            info = ctx.params['info'] = kwargs['info'] = True

        # TODO: check for plugin dependencies and if a plugin is ACTIVE!!!

        ########################################################################
        # 2. setup enabled plugins
        ########################################################################

        setup_timings = OrderedDict()
        plugins_setup_start = time()

        if not quiet and not verbose:
            echo_stderr('Setup plugins...', fg='green')

        # TODO: add progress indicator
        for stage, stage_plugins in enabled_plugins.items():
            for name, plugin in stage_plugins.items():
                plugin_setup_start = time()
                if verbose:
                    echo_stderr(' Setup plugin: %(stage)s:%(name)s...' % locals(),
                                fg='green')
                try:
                    plugin.setup(**kwargs)
                except:
                    msg = 'ERROR: failed to setup plugin: %(stage)s:%(name)s:' % locals()
                    echo_stderr(msg, fg='red')
                    echo_stderr(traceback.format_exc())
                    ctx.exit(2)

                timing_key = 'setup_%(stage)s:%(name)s' % locals()
                setup_timings[timing_key] = time() - plugin_setup_start

        setup_timings['setup'] = time() - plugins_setup_start

        ########################################################################
        # 3. collect codebase inventory
        ########################################################################

        inventory_start = time()

        if not quiet:
            echo_stderr('Collect file inventory...', fg='green')

        # TODO: add progress indicator
        # note: inventory timing collection is built in Codebase initialization
        try:
            codebase = Codebase(
                location=input, use_cache=on_disk_results, temp_dir=temp_dir)
        except:
            msg = 'ERROR: failed to collect codebase at: %(input)r' % locals()
            echo_stderr(msg, fg='red')
            echo_stderr(traceback.format_exc())
            ctx.exit(2)

        if TRACE:
            logger_debug('scancode: codebase.use_cache:', codebase.use_cache)

        codebase.timings.update(setup_timings)

        codebase.timings['inventory'] = time() - inventory_start

        files_count, dirs_count, size_count = codebase.compute_counts()
        codebase.summary['initial_files_count'] = files_count
        codebase.summary['initial_dirs_count'] = dirs_count
        codebase.summary['initial_size_count'] = size_count

        ########################################################################
        # 4. if any prescan plugins needs_info run an info scan first
        ########################################################################

        # do we need to collect info before prescan?
        pre_scan_needs_info = any(p.needs_info for p in pre_scan_plugins.values())

        info_is_collected = False

        if pre_scan_needs_info:
            # add info scan as scan option/kwarg/locals()
            info = ctx.params['info'] = kwargs['info'] = True

            info_start = time()

            progress_manager = None
            if not quiet:
                echo_stderr('Collect file information for pre-scans '
                            'with %(processes)d process(es)...' % locals())
                item_show_func = partial(path_progress_message, verbose=verbose)
                progress_manager = partial(progressmanager,
                    item_show_func=item_show_func, verbose=verbose, file=sys.stderr)

            scanners = [Scanner(key='infos', function=get_file_info)]
            # TODO: add CLI option to bypass cache entirely
            info_success = scan_codebase(codebase, scanners, processes, timeout,
                with_timing=timing, progress_manager=progress_manager)

            info_is_collected = True
            codebase.timings['collect-info'] = time() - info_start

            success = success and info_success

        ########################################################################
        # 5. run prescans
        ########################################################################

        # TODO: add progress indicator
        run_plugins(ctx, plugins=pre_scan_plugins, stage='pre-scan',
                    codebase=codebase, kwargs=kwargs,
                    quiet=quiet, verbose=verbose,
                    stage_msg='Run %(stage)ss...',
                    plugin_msg=' Run %(stage)s: %(name)s...')

        ########################################################################
        # 6. run scans.
        ########################################################################

        scan_start = time()
        scanners = []

        if not info:
            next_stages = (post_scan_plugins.values()
                           + output_filter_plugins.values()
                           + output_plugins.values())

            next_stages_need_info = any(p.needs_info for p in next_stages)
            # add info is requested or needed but not yet collected
            if next_stages_need_info:
                # add info scan as scan option
                info = True
                ctx.params['info'] = info

        if info and not info_is_collected:
            scanners = [Scanner(key='infos', function=get_file_info)]

        scan_sorter = lambda s: (s.sort_order, s.name)
        for scanner in sorted(scanner_plugins.values(), key=scan_sorter):
            func = scanner.get_scanner(**kwargs)
            scanners.append(Scanner(key=scanner.name, function=func))

        if TRACE_DEEP: logger_debug('scancode: scanners:', scanners)

        if scanners:
            scan_names = ', '.join(s.key for s in scanners)

            if not quiet:
                echo_stderr('Scan files for: %(scan_names)s '
                            'with %(processes)d process(es)...' % locals())

            progress_manager = None
            if not quiet:
                item_show_func = partial(path_progress_message, verbose=verbose)
                progress_manager = partial(progressmanager,
                    item_show_func=item_show_func,
                    verbose=verbose, file=sys.stderr)

            # TODO: add CLI option to bypass cache entirely?
            scan_success = scan_codebase(
                codebase, scanners, processes, timeout,
                with_timing=timing, progress_manager=progress_manager)

            scanned_fc, scanned_dc, scanned_sc = codebase.compute_counts()

            codebase.summary['scan_names'] = scan_names
            codebase.summary['scanned_files_count'] = scanned_fc
            codebase.summary['scanned_dirs_count'] = scanned_dc
            codebase.summary['scanned_size_count'] = scanned_sc
            codebase.timings['scan'] = time() - scan_start

            success = success and scan_success

        ########################################################################
        # 7. run postscans
        ########################################################################

        # TODO: add progress indicator
        run_plugins(ctx, plugins=post_scan_plugins, stage='post-scan',
                    codebase=codebase, kwargs=kwargs,
                    quiet=quiet, verbose=verbose,
                    stage_msg='Run %(stage)ss...',
                    plugin_msg=' Run %(stage)s: %(name)s...')

        ########################################################################
        # 8. apply output filters
        ########################################################################

        # TODO: add progress indicator
        run_plugins(ctx, plugins=output_filter_plugins, stage='output-filter',
                    codebase=codebase, kwargs=kwargs,
                    quiet=quiet, verbose=verbose,
                    stage_msg='Apply %(stage)ss...',
                    plugin_msg=' Apply %(stage)s: %(name)s...')

        ########################################################################
        # 9. run outputs
        ########################################################################

        # TODO: cleanup kwargs vs. codebase attrs
        files_count, dirs_count, size_count = codebase.compute_counts(
            skip_root=strip_root, skip_filtered=True)

        codebase.summary['final_files_count'] = files_count
        codebase.summary['final_dirs_count'] = dirs_count
        codebase.summary['final_size_count'] = size_count

        kwargs['files_count'] = files_count
        kwargs['pretty_options'] = get_pretty_params(ctx, info=info, generic_paths=test_mode)
        kwargs['scancode_notice'] = notice
        kwargs['scancode_version'] = scancode_version

        # TODO: add progress indicator
        run_plugins(ctx, plugins=output_plugins, stage='output',
                    codebase=codebase, kwargs=kwargs,
                    quiet=quiet, verbose=verbose,
                    stage_msg='Save scan results...',
                    plugin_msg=' Save scan results as: %(name)s...',
                    exit_on_fail=False)

        ########################################################################
        # 9. display summary
        ########################################################################
        codebase.timings['total'] = time() - processing_start

        # TODO: compute summary for output plugins too??
        if not quiet:
            echo_stderr('Scanning done.', fg='green' if success else 'red')
            display_summary(codebase, scan_names, processes, verbose=verbose)
    finally:
        # cleanup including cache cleanup
        if codebase:
            codebase.clear()

    rc = 0 if success else 1
    ctx.exit(rc)


def run_plugins(ctx, stage, plugins, codebase, kwargs, quiet, verbose,
                stage_msg='', plugin_msg='', exit_on_fail=True):
    """
    Run the `stage` `plugins` (a mapping of {name: plugin} on `codebase`.
    Display errors.
    Exit the CLI on failure if `exit_on_fail` is True.
    """
    stage_start = time()
    if verbose and plugins:
        echo_stderr(stage_msg % locals(), fg='green')

    # TODO: add progress indicator
    for name, plugin in plugins.items():
        plugin_start = time()

        if verbose:
            echo_stderr(plugin_msg % locals(), fg='green')

        try:
            if TRACE_DEEP:
                from pprint import pformat
                logger_debug('run_plugins: kwargs passed to %(stage)s:%(name)s' % locals())
                logger_debug(pformat(sorted(kwargs.item())))
                logger_debug()

            plugin.process_codebase(codebase, **kwargs)

        except:
            msg = 'ERROR: failed to run %(stage)s plugin: %(name)s:' % locals()
            echo_stderr(msg, fg='red')
            echo_stderr(traceback.format_exc())
            if exit_on_fail:
                ctx.exit(2)

        timing_key = '%(stage)s:%(name)s' % locals()
        codebase.timings[timing_key] = time() - plugin_start

    codebase.timings[stage] = time() - stage_start


def scan_codebase(codebase, scanners, processes=1, timeout=DEFAULT_TIMEOUT,
                  with_timing=False, progress_manager=None):
    """
    Run the `scanners` Scanner object on the `codebase` Codebase. Return True on
    success or False otherwise.

    Run the `scanners` ing multiprocessing with `processes` number of
    processes allocating one process per scanned `codebase` Resource.

    Run each scanner function for up to `timeout` seconds and fail it otherwise.

    If `with_timing` is True, per-scanner execution time (as a float in seconds)
    is added to the `scan_timings` mapping of each Resource as {scanner.key:
    execution time}.

    Provide optional progress feedback in the UI using the `progress_manager`
    callable that accepts an iterable of tuple of (location, rid, scan_errors,
    scan_result ) as argument.
    """

    # FIXME: this path computation is super inefficient
    # tuples of  (absolute location, resource id)
    # TODO: should we walk topdown or not???

    resources = ((r.get_path(absolute=True), r.rid) for r in codebase.walk())

    runner = partial(scan_resource, scanners=scanners,
                     timeout=timeout, with_timing=with_timing,
                     with_threading=processes >= 0)

    if TRACE:
        logger_debug('scan_codebase: scanners:', '\n'.join(repr(s) for s in scanners))

    get_resource = codebase.get_resource

    success = True
    pool = None
    scans = None
    try:
        if processes >= 1:
            # maxtasksperchild helps with recycling processes in case of leaks
            pool = get_pool(processes=processes, maxtasksperchild=1000)
            # Using chunksize is documented as much more efficient in the Python doc.
            # Yet "1" still provides a better and more progressive feedback.
            # With imap_unordered, results are returned as soon as ready and out of order.
            scans = pool.imap_unordered(runner, resources, chunksize=1)
            pool.close()
        else:
            # no multiprocessing with processes=0 or -1
            scans = imap(runner, resources)

        if progress_manager:
            scans = progress_manager(scans)
            # hack to avoid using a context manager
            if hasattr(scans, '__enter__'):
                scans.__enter__()

        while True:
            try:
                location, rid, scan_errors, scan_time, scan_result, scan_timings = scans.next()

                if TRACE_DEEP: logger_debug(
                    'scan_codebase: location:', location, 'results:', scan_result)

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

                # always set info directly on resources
                infos = scan_result.pop('infos', [])
                if TRACE: logger_debug('scan_codebase: infos:', infos)
                if infos:
                    resource.set_info(infos)

                if TRACE: logger_debug('scan_codebase: scan_timings:', scan_timings)
                if with_timing and scan_timings:
                    if resource.scan_timings:
                        resource.scan_timings.update(scan_timings)
                    else:
                        resource.scan_timings = scan_timings

                saved_scans = resource.put_scans(scan_result, update=True)
                if TRACE: logger_debug('scan_codebase: saved_scans:', saved_scans)

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


def scan_resource(location_rid, scanners, timeout=DEFAULT_TIMEOUT,
                  with_timing=False, with_threading=True):
    """
    Return a tuple of (location, rid, errors, scan_time, scan_results, timings)
    by running the `scanners` Scanner objects for the file or directory resource
    with id `rid` at `location` provided as a `location_rid` tuple of (location,
    rid) for up to `timeout` seconds.
    If `with_threading` is False, threading is disabled.

    The returned tuple has these values (:
    - `location` and `rid` are the orginal arguments.
    - `errors` is a list of error strings.
    - `scan_results` is a mapping of scan results keyed by scanner.key.
    - `scan_time` is the duration in seconds to run all scans for this resource.
    - `timings` is a mapping of scan {scanner.key: execution time in seconds}
      tracking the execution duration each each scan individually.
      `timings` is empty unless `with_timing` is True.

    All these values MUST be serializable/pickable because of the way multi-
    processing/threading works.
    """
    scan_time = time()

    timings = None
    if with_timing:
        timings = OrderedDict((scanner.key, 0) for scanner in scanners)

    if not with_threading:
        interruptor= fake_interruptible
    else:
        interruptor = interruptible

    location, rid = location_rid
    errors = []
    results = OrderedDict((scanner.key, []) for scanner in scanners)

    # run each scanner in sequence in its own interruptible
    for scanner, scanner_result in zip(scanners, results.values()):
        if with_timing:
            start = time()

        try:
            runner = partial(scanner.function, location)
            error, value = interruptor(runner, timeout=timeout)
            if error:
                msg = 'ERROR: for scanner: ' + scanner.key + ':\n' + error
                errors.append(msg)
            if value:
                # a scanner function MUST return a sequence
                scanner_result.extend(value)

        except Exception:
            msg = 'ERROR: for scanner: ' + scanner.key + ':\n' + traceback.format_exc()
            errors.append(msg)
        finally:
            if with_timing:
                timings[scanner.key] = time() - start

    scan_time = time() - scan_time

    return location, rid, errors, scan_time, results, timings


def display_summary(codebase, scan_names, processes, verbose):
    """
    Display a scan summary.
    """

    initial_files_count = codebase.summary.get('initial_files_count', 0)
    initial_dirs_count = codebase.summary.get('initial_dirs_count', 0)
    initial_res_count = initial_files_count + initial_dirs_count
    initial_size_count = codebase.summary.get('initial_size_count', 0)
    if initial_size_count:
        initial_size_count = format_size(initial_size_count)
        initial_size_count = 'for %(initial_size_count)s' % locals()
    else:
        initial_size_count = ''

    final_files_count = codebase.summary.get('final_files_count', 0)
    final_dirs_count = codebase.summary.get('final_dirs_count', 0)
    final_res_count = final_files_count + final_dirs_count
    final_size_count = codebase.summary.get('final_size_count', 0)
    if final_size_count:
        final_size_count = format_size(final_size_count)
        final_size_count = 'for %(final_size_count)s' % locals()
    else:
        final_size_count = ''

    top_errors = codebase.errors
    path_and_errors = [(r.get_path(decode=True, posix=True), r.errors)
                       for r in codebase.walk() if r.errors]

    has_errors = top_errors or path_and_errors

    errors_count = 0
    if has_errors:
        echo_stderr('Some files failed to scan properly:', fg='red')
        for error in top_errors:
            echo_stderr(error)
            errors_count += 1

        for errored_path, errors in path_and_errors:
            echo_stderr('Path: ' + errored_path, fg='red')
            if not verbose:
                continue
            for error in errors:
                for emsg in error.splitlines(False):
                    echo_stderr('  ' + emsg, fg='red')
                errors_count += 1

    scan_time = codebase.timings.get('scan', 0.)

    scanned_size_count = codebase.summary.get('scanned_size_count', 0)
    if scanned_size_count:
        scan_size_speed = format_size(scanned_size_count / scan_time)
        scan_size_speed = '%(scan_size_speed)s/sec.' % locals()
    else:
        scan_size_speed = ''

    scanned_files_count = codebase.summary.get('scanned_files_count', 0)
    scan_file_speed = round(float(scanned_files_count) / scan_time , 2)

    echo_stderr('Summary:        %(scan_names)s with %(processes)d process(es)' % locals())
    echo_stderr('Errors count:   %(errors_count)d' % locals())
    echo_stderr('Scan Speed:     %(scan_file_speed).2f files/sec. %(scan_size_speed)s' % locals())

    echo_stderr('Initial counts: %(initial_res_count)d resource(s): '
                                '%(initial_files_count)d file(s) '
                                'and %(initial_dirs_count)d directorie(s) '
                                '%(initial_size_count)s' % locals())

    echo_stderr('Final counts:   %(final_res_count)d resource(s): '
                                '%(final_files_count)d file(s) '
                                'and %(final_dirs_count)d directorie(s) '
                                '%(final_size_count)s' % locals())

    echo_stderr('Timings:')
    for key, value, in codebase.timings.items():
        if value > 0.1:
            echo_stderr('  %(key)s: %(value).2fs' % locals())
    # TODO: if timing was requested display per-scan/per-file stats


def format_size(size):
    """
    Return a human-readable value for the `size` int or float.

    For example:
    >>> format_size(0)
    u'0 Byte'
    >>> format_size(1)
    u'1 Byte'
    >>> format_size(0.123)
    u'0.1 Byte'
    >>> format_size(123)
    u'123 Bytes'
    >>> format_size(1023)
    u'1023 Bytes'
    >>> format_size(1024)
    u'1 KB'
    >>> format_size(2567)
    u'2.51 KB'
    >>> format_size(2567000)
    u'2.45 MB'
    >>> format_size(1024*1024)
    u'1 MB'
    >>> format_size(1024*1024*1024)
    u'1 GB'
    >>> format_size(1024*1024*1024*12.3)
    u'12.30 GB'
    """
    if not size:
        return '0 Byte'
    if size < 1:
        return '%(size).1f Byte' % locals()
    if size == 1:
        return '%(size)d Byte' % locals()
    size = float(size)
    for symbol in ('Bytes', 'KB', 'MB', 'GB', 'TB'):
        if size < 1024:
            if int(size) == float(size):
                return '%(size)d %(symbol)s' % locals()
            return '%(size).2f %(symbol)s' % locals()
        size = size / 1024.
    return '%(size).2f %(symbol)s' % locals()


def get_pretty_params(ctx, info=False, generic_paths=False):
    """
    Return a sorted mapping of {CLI option: pretty value string} for the
    `ctx` Click.context, putting arguments first then options:

        {"input": ~/some/path, "--license": True}

    Skip options that are not set or hidden.

    If `generic_paths` is True, click.File and click.Path parameters are made
    "generic" replacing their value with a placeholder. This is used mostly for
    testing.
    """

    if TRACE:
        logger_debug('get_pretty_params: generic_paths', generic_paths)
    args = []
    # hack since info option can be changed to True if default
    options = [('--info', info)] if info else []

    param_values = ctx.params
    for param in ctx.command.params:
        name = param.name
        value = param_values.get(name)

        if param.is_eager:
            continue
        # This attribute is not yet in Click 6.7 but in head
        if getattr(param, 'hidden', False):
            continue

        if value == param.default:
            continue
        if value is None:
            continue
        if value in (tuple(), [],):
            # option with multiple values, the value is a tuple
            continue

        if isinstance(param.type, click.Path) and generic_paths:
            value = '<path>'

        if isinstance(param.type, click.File):
            if generic_paths:
                value = '<file>'
            else:
                # the value cannot be displayed as-is as this may be an opened file-
                # like object
                vname = getattr(value, 'name', None)
                if vname:
                    value = vname
                else:
                    value = '<file>'

        # coerce to string for non-basic supported types
        if not (value in (True, False, None)
            or isinstance(value, (str, unicode, bytes, tuple, list, dict, OrderedDict))):
            value = repr(value)

        # opts is a list of CLI options as in "--strip-root": the last opt is
        # the CLI option long form by convention
        cli_opt = param.opts[-1]

        if isinstance(param, click.Argument):
            args.append((cli_opt, value))
        else:
            options.append((cli_opt, value))

    return OrderedDict(sorted(args) + sorted(options))

