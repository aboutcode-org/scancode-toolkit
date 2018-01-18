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

from commoncode.fileutils import PATH_TYPE
from commoncode.timeutils import time2tstamp

from plugincode import CommandLineOption
from plugincode import PluginManager

# these are important to register plugin managers
from plugincode import housekeeping
from plugincode import pre_scan
from plugincode import scan
from plugincode import post_scan
from plugincode import output_filter
from plugincode import output

from scancode import __version__ as version
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
from scancode import get_command_options
from scancode import Scanner
from scancode import validate_option_dependencies
from scancode.api import get_file_info
from scancode.interrupt import DEFAULT_TIMEOUT
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
    bytes = str  # @ReservedAssignment
    str = unicode  # @ReservedAssignment
except NameError:
    # Python 3
    unicode = str  # @ReservedAssignment


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
    click.echo('ScanCode version ' + version)
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
                 help=None,  # @ReservedAssignment
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
            click.echo('    {help_group!s}, {name!s}: {opts}'.format(**locals()))
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
         'Disable parallel processing if 0.  [default: 1]',
    help_group=CORE_GROUP, sort_order=10, cls=CommandLineOption)

@click.option('--timeout',
    type=float, default=DEFAULT_TIMEOUT,
    metavar='<seconds>',
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

@click.option('--no-cache',
    is_flag=True,
    help='Do not use on-disk cache for intermediate results. Uses more memory.',
    help_group=CORE_GROUP, sort_order=200, cls=CommandLineOption)

@click.option('--timing',
    is_flag=True,
    help='Collect execution timing for each scan and scanned file.',
    help_group=CORE_GROUP, cls=CommandLineOption)

@click.option('--temp-dir',
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True,
        readable=True, path_type=PATH_TYPE),
    default=None, sort_order=200,
    metavar='DIR',
    help='Set the path to the temporary directory to use for ScanCode '
         'cache and temporary files.',
    help_group=CORE_GROUP,
    cls=CommandLineOption)

@click.help_option('-h', '--help',
    help_group=DOC_GROUP, sort_order= 10,cls=CommandLineOption)

@click.option('--examples',
    is_flag=True, is_eager=True,
    callback=print_examples,
    help=('Show command examples and exit.'),
    help_group=DOC_GROUP, sort_order= 50,cls=CommandLineOption)

@click.option('--about',
    is_flag=True, is_eager=True,
    callback=print_about,
    help='Show information about ScanCode and licensing and exit.',
    help_group=DOC_GROUP, sort_order= 20,cls=CommandLineOption)

@click.option('--version',
    is_flag=True, is_eager=True,
    callback=print_version,
    help='Show the version and exit.',
    help_group=DOC_GROUP, sort_order= 20,cls=CommandLineOption)

@click.option('--plugins',
    is_flag=True, is_eager=True,
    callback=print_plugins,
    help='Show the list of available ScanCode plugins and exit.',
    help_group=DOC_GROUP, cls=CommandLineOption)

@click.option('--test-mode',
    is_flag=True, default=False,
    # not yet supported in Click 6.7
    # hidden = True,
    help='Run ScanCode in a special "test mode". Only for testing.',
    help_group=MISC_GROUP, sort_order= 1000,cls=CommandLineOption)

def scancode(ctx, input, info,  # @ReservedAssignment
             strip_root, full_root,
             verbose, quiet,
             processes, timeout,
             no_cache,
             timing,
             temp_dir,
             test_mode,
             *args, **kwargs):
    """scan the <input> file or directory for license, origin and packages and save results to FILE(s) using one or more ouput format option.

    Error and progress is printed to stderr.
    """

    # notes: the above docstring of this function is used in the CLI help Here is
    # it's actual docstring:
    """
    Return a return code of 0 on success or 1 on error from running all the
    scanning "stages" in the `input` file and saving results inthe `format` format
    to `output_file`.
    The scanning stages are:

    - `inventory`: collect the codebase inventory resources tree for the `input`.
      This is a built-in stage that does not accept plugins.

    - `setup`: as part of the plugins system, each plugin is loaded and
      its `setup` class method is called if it is enabled.

    - `pre-scan`: each enabled pre-scan plugin `process_codebase(codebase)`
       method is called to update/transforme the whole codebase

    - `scan`: the codebase is walked and each enabled scan plugin
      `process_resource(resource.location)` method is called for each codebase
      resource.

    - `post-scan`: each enabled post-scan plugin `process_codebase(codebase)`
       method is called to update/transforme the whole codebase

    # !!!!!TODO: this is not yet true!!!!
    - `output`: each enabled output plugin `process_codebase(codebase)`
       method is called to create an output for the codebase

    This function is the main CLI entry point.

    The other arguments are:

    - `quiet` and `verbose`: boolean flags: Do not display any message if
      `quiet` is True. Otherwise, display extra verbose messages if `quiet` is
      False and `verbose` is True. These two options are mutually exclusive.

    - `strip_root` and `full_root`: boolean flags: In the outputs, strip the
      first path segment of a file if `strip_root` is True unless the `input` is
      a single file. If `full_root` is True report the path as an absolute path.
      These options are mutually exclusive.

    - `processes`: int: run the scan using up to this number of processes in
      parallel. If 0, disable the multiprocessing machinery.

    - `timeout`: float: intterup the scan of a file if it does not finish within
      `timeout` seconds. This applied to each file and scan individually (e.g.
      if the license scan is interrupted they other scans may complete, each
      withing the timeout)

    - `no_cache`: boolean flag: disable on-disk caching of intermediate scan
      results and store these in memory instead if True

    - `timing`: boolean flag: collect per-scan and per-file scan timings if
      True.

    - `temp_dir`: path to a non-default temporary directory fo caching and other
      temporary files. If not provided, the default is used.

    Other **kwargs are passed down to plugins as CommandOption indirectly
    through Click context machinery.
    """

    success = True
    codebase = None
    processing_start = time()

    # UTC start timestamp
    scan_start = time2tstamp()

    try:
        # validate_exclusive(ctx, ['strip_root', 'full_root'])

        if not processes and not quiet:
            echo_stderr('Disabling multi-processing.', fg='yellow')

        ############################################################################
        # 1. get command options and create all plugin instances
        ############################################################################
        validate_option_dependencies(ctx)
        command_options = sorted(get_command_options(ctx))
        if TRACE_DEEP:
            logger_debug('scancode: command_options:')
            for co in command_options:
                logger_debug('  scancode: command_option:', co)

        enabled_plugins = OrderedDict()

        for stage, manager in PluginManager.managers.items():
            if stage == housekeeping.stage:
                continue

            enabled_plugins[stage] = stage_plugins = OrderedDict()
            for name, plugin_cls in manager.plugin_classes.items():
                # TODO: manage errors: this will error out loudly if there are errors
                plugin = plugin_cls(command_options)
                if plugin.is_enabled():
                    # Set special test mode flag that plugins can leverage
                    plugin._test_mode = test_mode
                    stage_plugins[name] = plugin

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

        if not scanner_plugins and not info:
            # Use default info scan when no scan option is requested
            info = True
            for co in command_options:
                if co.name == 'info':
                    co._replace(value=True)

        # TODO: check for plugin dependencies and if a plugin is ACTIVE!!!

        ############################################################################
        # 2. setup enabled plugins
        ############################################################################

        setup_timings = OrderedDict()
        plugins_setup_start = time()
        # TODO: add progress indicator
        if not quiet and not verbose:
            echo_stderr('Setup plugins...', fg='green')
        for stage, stage_plugins in enabled_plugins.items():
            for name, plugin in stage_plugins.items():
                plugin_setup_start = time()
                if not quiet and verbose:
                    echo_stderr('Setup plugin: %(stage)s:%(name)s...' % locals(),
                                fg='green')
                plugin.setup()

                timing_key = 'setup_%(stage)s_%(name)s' % locals()
                setup_timings[timing_key] = time() - plugin_setup_start

        setup_timings['setup'] = time() - plugins_setup_start

        ############################################################################
        # 3. collect codebase inventory
        ############################################################################

        if not quiet:
            echo_stderr('Collect file inventory...', fg='green')

        # TODO: add progress indicator
        # note: inventory timing collection is built in Codebase initialization
        codebase = Codebase(location=input, use_cache=not no_cache)
        if TRACE: logger_debug('scancode: codebase.use_cache:', codebase.use_cache)

        codebase.strip_root = strip_root
        codebase.full_root = full_root

        codebase.timings.update(setup_timings)

        # TODO: thse are noy YET used in outputs!!
        codebase.summary['scancode_notice'] = notice
        codebase.summary['scancode_version'] = version
        # TODO: this is NOT the pretty options
        codebase.summary['scancode_options'] = command_options

        ############################################################################
        # 4. if any prescan plugins needs_info run an info scan first
        ############################################################################

        # do we need to collect info before prescan?
        pre_scan_needs_info = any(p.needs_info for p in pre_scan_plugins.values())

        info_is_collected = False

        if pre_scan_needs_info:
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
                with_timing=timing, with_info=True, progress_manager=progress_manager)

            codebase.timings['collect-info'] = time() - info_start
            info_is_collected = True

            success = success and info_success

        ############################################################################
        # 5. run prescans
        ############################################################################

        pre_scan_start = time()
        if not quiet and not verbose and pre_scan_plugins:
            echo_stderr('Run pre-scan plugins...', fg='green')

        # TODO: add progress indicator
        # FIXME: we should always catch errors from plugins properly
        for name, plugin in pre_scan_plugins.items():
            plugin_prescan_start = time()
            if verbose:
                echo_stderr('Run pre-scan plugin: %(name)s...' % locals(),
                            fg='green')

            plugin.process_codebase(codebase)
            codebase.update_counts()
            timing_key = 'prescan_%(name)s' % locals()
            setup_timings[timing_key] = time() - plugin_prescan_start

        codebase.timings['pre-scan'] = time() - pre_scan_start

        ############################################################################
        # 6. run scans.
        ############################################################################

        scan_start = time()
        scanners = []
        # add info is requested or needed but not yet collected
        stages_needs_info = any(p.needs_info for p in
            (post_scan_plugins.values() + output_plugins.values()))

        with_info = info or stages_needs_info
        codebase.with_info = with_info
        if not info_is_collected and with_info:
            scanners = [Scanner(key='infos', function=get_file_info)]

        scan_sorter = lambda s: (s.sort_order, s.name)
        for scanner in sorted(scanner_plugins.values(), key=scan_sorter):
            scanner_kwargs = scanner.get_own_command_options_kwargs()
            func = scanner.get_scanner(**scanner_kwargs)
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
                    item_show_func=item_show_func, verbose=verbose, file=sys.stderr)

            # TODO: add CLI option to bypass cache entirely
            scan_success = scan_codebase(codebase, scanners, processes, timeout,
                with_timing=timing, with_info=with_info, progress_manager=progress_manager)

            scanned_count, _, scanned_size = codebase.counts(
                update=True, skip_root=False)

            codebase.summary['scan_names'] = scan_names
            codebase.summary['scanned_count'] = scanned_count
            codebase.summary['scanned_size'] = scanned_size
            codebase.timings['scan'] = time() - scan_start

            success = success and scan_success

        ############################################################################
        # 7. run postscans
        ############################################################################

        post_scan_start = time()
        # TODO: add progress indicator
        # FIXME: we should always catch errors from plugins properly
        if not quiet and not verbose and post_scan_plugins:
            echo_stderr('Run post-scan plugins...', fg='green')
        for name, plugin in post_scan_plugins.items():
            if not quiet and verbose:
                echo_stderr('Run post-scan plugin: %(name)s...' % locals(), fg='green')

            plugin.process_codebase(codebase)
            codebase.update_counts()

        codebase.timings['post-scan'] = time() - post_scan_start

        ############################################################################
        # 8. apply output filters
        ############################################################################
        output_filter_start = time()
        # TODO: add progress indicator
        # FIXME: we should always catch errors from plugins properly
        if not quiet and not verbose and output_filter_plugins:
            echo_stderr('Run output filter plugins...', fg='green')

        filters = tuple(plugin.process_resource for plugin in output_filter_plugins.values())
        if filters:
            # This is a set of resource ids to filter out from the final outputs
            filtered_rids_add = codebase.filtered_rids.add
            for rid, resource in codebase.get_resources_with_rid():
                if all(to_keep(resource) for to_keep in filters):
                    continue
                filtered_rids_add(rid)

        codebase.timings['output-filter'] = time() - post_scan_start

        ############################################################################
        # 9. run outputs
        ############################################################################
        output_start = time()
        # TODO: add progress indicator
        # FIXME: we should always catch errors from plugins properly

        if not quiet and not verbose:
            echo_stderr('Save results...' , fg='green')

        for name, plugin in output_plugins.items():
            if not quiet and verbose:
                echo_stderr('Save results as: %(name)s...' % locals(), fg='green')

            plugin.process_codebase(codebase)
            codebase.update_counts()

        codebase.timings['output'] = time() - output_start

        ############################################################################
        # 9. display summary
        ############################################################################
        codebase.timings['total'] = time() - processing_start

        # TODO: compute summary for output plugins too??
        if not quiet:
            echo_stderr('Scanning done.', fg='green' if success else 'red')
            display_summary(codebase, scan_names, processes,
                skip_root=strip_root, verbose=verbose)

    finally:
        # cleanup including cache cleanup
        if codebase:
            codebase.clear()

    rc = 0 if success else 1
    ctx.exit(rc)


def scan_codebase(codebase, scanners, processes=1, timeout=DEFAULT_TIMEOUT,
                  with_timing=False, with_info=False, progress_manager=None):
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
    # TODO: should we alk topdown or not???

    resources = ((r.get_path(absolute=True), r.rid) for r in codebase.walk())

    runner = partial(scan_resource, scanners=scanners, timeout=timeout)

    has_info_scanner = with_info
    lscan = len(scanners)
    has_other_scanners = lscan > 1 if has_info_scanner else lscan
    if TRACE:
        logger_debug('scan_codebase: scanners:', '\n'.join(repr(s) for s in scanners))
        logger_debug('scan_codebase: has_other_scanners:', bool(has_other_scanners))

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
                if with_timing:
                    location, rid, scan_errors, scan_result, scan_time, scan_result, scan_timings = scans.next()
                else:
                    location, rid, scan_errors, scan_time, scan_result = scans.next()
                    if TRACE_DEEP: logger_debug('scan_codebase: results:', scan_result)
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
                    if TRACE: logger_debug('scan_codebase: set_info:', info)

                if has_other_scanners and scan_result:
                    resource.put_scans(scan_result, update=True)
                    if TRACE: logger_debug('scan_codebase: pu_scans:', scan_result)

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


def scan_resource(location_rid, scanners, timeout=DEFAULT_TIMEOUT, with_timing=False):
    """
    Return a tuple of (location, rid, errors, scan_time, scan_results)
    by running the `scanners` Scanner objects for the file or directory resource
    with id `rid` at `location` provided as a `location_rid` tuple of (location,
    rid) for up to `timeout` seconds.
    In the returned tuple:
    - `errors` is a list of error strings
    - `scan_time` is the duration in seconds as float to run all scans for this resource
    - `scan_results` is a mapping of scan results keyed by scanner name.

    If `with_timing` is True, the execution time of each scanner is also
    collected as a float in seconds and the returned tuple contains an extra
    trailing item as a mapping of {scanner.key: execution time}.
    """
    scan_time = time()

    if with_timing:
        timings = OrderedDict((scanner.key, 0) for scanner in scanners)

    location, rid = location_rid
    errors = []
    results = OrderedDict((scanner.key, []) for scanner in scanners)

    # run each scanner in sequence in its own interruptible
    for scanner, scanner_result in zip(scanners, results.values()):
        if with_timing:
            start = time()
        try:
            error, value = interruptible(
                partial(scanner.function, location), timeout=timeout)
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
            scan_time = time() - scan_time
            if with_timing:
                timings[scanner.key] = time() - start

    if with_timing:
        return location, rid, errors, scan_time, results, timings
    else:
        return location, rid, errors, scan_time, results


def display_summary(codebase, scan_names, processes, skip_root, verbose):
    """
    Display a scan summary.
    """
    counts = codebase.counts(update=False, skip_root=skip_root)

    initial_files_count = codebase.summary.get('initial_files_count', 0)
    initial_dirs_count = codebase.summary.get('initial_dirs_count', 0)
    initial_res_count = initial_files_count + initial_dirs_count

    final_files_count, final_dirs_count, final_size = counts
    final_res_count = final_files_count + final_dirs_count

    top_errors = codebase.errors
    path_errors = [(r.get_path(decode=True, posix=True), r.errors) for r in codebase.walk() if r.errors]

    has_errors = top_errors or path_errors

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

    scanned_size = codebase.summary.get('scanned_size', 0)
    scan_time = codebase.timings.get('scan', 0.)
    scan_size_speed = format_size(scanned_size / scan_time)
    scanned_count = codebase.summary.get('scanned_count', 0)
    scan_file_speed = round(float(scanned_count) / scan_time , 2)
    final_size = format_size(final_size)

    echo_stderr('Summary:        %(scan_names)s with %(processes)d process(es)' % locals())
    echo_stderr('Errors count:   %(errors_count)d' % locals())
    echo_stderr('Scan Speed:     %(scan_file_speed).2f files/sec. %(scan_size_speed)s/sec.' % locals())

    echo_stderr('Initial counts: %(initial_res_count)d resource(s): '
                                '%(initial_files_count)d file(s) '
                                'and %(initial_dirs_count)d directorie(s)' % locals())

    echo_stderr('Final counts:   %(final_res_count)d resource(s): '
                                '%(final_files_count)d file(s) '
                                'and %(final_dirs_count)d directorie(s) '
                                'for %(final_size)s' % locals())

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
