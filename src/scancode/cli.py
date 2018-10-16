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
import sys
from time import time
import traceback

import click
click.disable_unicode_literals_warning = True

# import early
from scancode_config import __version__ as scancode_version
from scancode_config import scancode_cache_dir
from scancode_config import scancode_temp_dir

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
from scancode import notice
from scancode import print_about
from scancode import Scanner
from scancode import validate_option_dependencies
from scancode.interrupt import DEFAULT_TIMEOUT
from scancode.interrupt import fake_interruptible
from scancode.interrupt import interruptible
from scancode.resource import Codebase
from scancode.resource import VirtualCodebase
from scancode.utils import BaseCommand
from scancode.utils import path_progress_message
from scancode.utils import progressmanager
from scancode.help import examples_text
from scancode.help import epilog_text

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


try:
    # IMPORTANT: this discovers, loads and validates all available plugins
    plugin_classes, plugin_options = PluginManager.load_plugins()
except ImportError, e:
    echo_stderr('========================================================================')
    echo_stderr('ERROR: Unable to import ScanCode plugins.'.upper())
    echo_stderr('Check your installation configuration (setup.py) or re-install/re-configure ScanCode.')
    echo_stderr('The following plugin(s) are referenced and cannot be loaded/imported:')
    echo_stderr(str(e), color='red')
    echo_stderr('========================================================================')
    raise e


def print_plugins(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    for plugin_cls in sorted(plugin_classes, key=lambda pc: (pc.stage, pc.name)):
        click.echo('--------------------------------------------')
        click.echo('Plugin: scancode_{self.stage}:{self.name}'.format(self=plugin_cls), nl=False)
        click.echo('  class: {self.__module__}:{self.__name__}'.format(self=plugin_cls))
        if hasattr(plugin_cls, 'requires'):
            requires = ', '.join(plugin_cls.requires)
            click.echo('  requires: {}'.format(requires), nl=False)
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


def print_options(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    values = ctx.params
    click.echo('Options:')

    for name, val in sorted(values.items()):
        click.echo('  {name}: {val}'.format(**locals()))
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
    help='Report full, absolute paths.',
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
    help='Print progress as file-by-file path instead of a progress bar. '
         'Print verbose scan counters.',
    help_group=CORE_GROUP, sort_order=20, cls=CommandLineOption)

@click.option('--from-json',
    is_flag=True,
    help='Load codebase from an existing JSON scan',
    help_group=CORE_GROUP, sort_order=25, cls=CommandLineOption)

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

@click.option('--max-in-memory',
    type=int, default=10000,
    show_default=True,
    help=
    'Maximum number of files and directories scan details kept in memory '
    'during a scan. Additional files and directories scan details above this '
    'number are cached on-disk rather than in memory. '
    'Use 0 to use unlimited memory and disable on-disk caching. '
    'Use -1 to use only on-disk caching.',
    help_group=CORE_GROUP, sort_order=300, cls=CommandLineOption)

@click.help_option('-h', '--help',
    help_group=DOC_GROUP, sort_order=10, cls=CommandLineOption)

@click.option('--about',
    is_flag=True, is_eager=True, expose_value=False,
    callback=print_about,
    help='Show information about ScanCode and licensing and exit.',
    help_group=DOC_GROUP, sort_order=20, cls=CommandLineOption)

@click.option('--version',
    is_flag=True, is_eager=True, expose_value=False,
    callback=print_version,
    help='Show the version and exit.',
    help_group=DOC_GROUP, sort_order=20, cls=CommandLineOption)

@click.option('--examples',
    is_flag=True, is_eager=True, expose_value=False,
    callback=print_examples,
    help=('Show command examples and exit.'),
    help_group=DOC_GROUP, sort_order=50, cls=CommandLineOption)

@click.option('--plugins',
    is_flag=True, is_eager=True, expose_value=False,
    callback=print_plugins,
    help='Show the list of available ScanCode plugins and exit.',
    help_group=DOC_GROUP, cls=CommandLineOption)

@click.option('--test-mode',
    is_flag=True, default=False,
    # not yet supported in Click 6.7 but added in CommandLineOption
    hidden=True,
    help='Run ScanCode in a special "test mode". Only for testing.',
    help_group=MISC_GROUP, sort_order=1000, cls=CommandLineOption)

@click.option('--print-options',
    is_flag=True,
    expose_value=False,
    callback=print_options,
    help='Show the list of selected options and exit. (used in debug only)',
    help_group=DOC_GROUP, cls=CommandLineOption)
def scancode(ctx, input,  # NOQA
             strip_root, full_root,
             processes, timeout,
             quiet, verbose,
             from_json,
             cache_dir, temp_dir,
             timing,
             max_in_memory,
             test_mode,
             *args, **kwargs):
    """scan the <input> file or directory for license, origin and packages and save results to FILE(s) using one or more output format option.

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
      `get_scanner()` scanner function is called once for each codebase
       resource receiving the `resource.location` as an argument.

    - `post-scan`: each enabled post-scan plugin `process_codebase(codebase)`
      method is called to update/transform the whole codebase.

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
        strip_root=strip_root,
        full_root=full_root,
        processes=processes,
        timeout=timeout,
        quiet=quiet,
        verbose=verbose,
        from_json=from_json,
        cache_dir=cache_dir,
        temp_dir=temp_dir,
        timing=timing,
        max_in_memory=max_in_memory,
        test_mode=test_mode
    )
    kwargs.update(standard_kwargs)

    success = True
    codebase = None
    processing_start = time()

    start_timestamp = time2tstamp()

    if not quiet:
        if not processes:
            echo_stderr('Disabling multi-processing for debugging.', fg='yellow')
        elif processes == -1:
            echo_stderr('Disabling multi-processing '
                        'and multi-threading for debugging.', fg='yellow')

    try:
        ########################################################################
        # 1. create all plugin instances
        ########################################################################
        # FIXME:
        validate_option_dependencies(ctx)

        if TRACE_DEEP:
            ctx_params = sorted(ctx.params.items())
            logger_debug('scancode: ctx.params:')
            for co in ctx.params:
                logger_debug('  scancode: ctx.params:', co)

        # NOTE and FIXME: this is a two level nested mapping, which is TOO
        # complicated
        enabled_plugins_by_stage = OrderedDict()

        for stage, manager in PluginManager.managers.items():
            enabled_plugins_by_stage[stage] = stage_plugins = []
            for plugin_cls in manager.plugin_classes:
                try:
                    name = plugin_cls.name
                    plugin = plugin_cls(**kwargs)
                    if plugin.is_enabled(**kwargs):
                        stage_plugins.append(plugin)
                except:
                    msg = 'ERROR: failed to load plugin: %(stage)s:%(name)s:' % locals()
                    echo_stderr(msg, fg='red')
                    echo_stderr(traceback.format_exc())
                    ctx.exit(2)

        # NOTE: these are list of plugin instances, not classes!
        pre_scan_plugins = enabled_plugins_by_stage[pre_scan.stage]
        scanner_plugins = enabled_plugins_by_stage[scan.stage]
        post_scan_plugins = enabled_plugins_by_stage[post_scan.stage]
        output_filter_plugins = enabled_plugins_by_stage[output_filter.stage]
        output_plugins = enabled_plugins_by_stage[output.stage]

        if from_json and scanner_plugins:
            msg = ('Data loaded from JSON: no scan options can be selected.')
            raise click.UsageError(msg)

        if not output_plugins:
            msg = ('Missing output option(s): at least one output '
                   'option is required to save scan results.')
            raise click.UsageError(msg)

        # TODO: check for plugin dependencies and if a plugin is ACTIVE!!!

        ########################################################################
        # 2. setup enabled plugins
        ########################################################################

        setup_timings = OrderedDict()
        plugins_setup_start = time()

        if not quiet and not verbose:
            echo_stderr('Setup plugins...', fg='green')

        # TODO: add progress indicator
        for stage, stage_plugins in enabled_plugins_by_stage.items():
            for plugin in stage_plugins:
                plugin_setup_start = time()
                name = plugin.name
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
        # 2.5. Collect Resource attributes requested for this scan
        ########################################################################
        # Craft a new Resource class with the attributes contributed by plugins
        sortable_resource_attributes = []

        # mapping of {"plugin stage:name": [list of attribute keys]}
        # also available as a kwarg entry for plugin
        kwargs['resource_attributes_by_plugin'] = resource_attributes_by_plugin = {}
        for stage, stage_plugins in enabled_plugins_by_stage.items():
            for plugin in stage_plugins:
                name = plugin.name
                try:
                    sortable_resource_attributes.append(
                        (plugin.sort_order, name, plugin.resource_attributes,)
                    )
                    resource_attributes_by_plugin[plugin.qname] = plugin.resource_attributes.keys()
                except:
                    msg = ('ERROR: failed to collect resource_attributes for plugin: '
                           '%(stage)s:%(name)s:' % locals())
                    echo_stderr(msg, fg='red')
                    echo_stderr(traceback.format_exc())
                    ctx.exit(2)

        resource_attributes = OrderedDict()
        for _, name, attribs in sorted(sortable_resource_attributes):
            resource_attributes.update(attribs)

        # FIXME: workaround for https://github.com/python-attrs/attrs/issues/339
        # we reset the _CountingAttribute internal ".counter" to a proper value
        # that matches our ordering
        for order, attrib in enumerate(resource_attributes.values(), 100):
            attrib.counter = order

        if TRACE_DEEP:
            logger_debug('scancode:resource_attributes')
            for a in resource_attributes.items():
                logger_debug(a)

        ########################################################################
        # 2.7. Collect Codebase attributes requested for this run
        ########################################################################
        # Craft a new Codebase class with the attributes contributed by plugins
        sortable_codebase_attributes = []

        # mapping of {"plugin stage:name": [list of attribute keys]}
        # also available as a kwarg entry for plugin
        kwargs['codebase_attributes_by_plugin'] = codebase_attributes_by_plugin = {}
        for stage, stage_plugins in enabled_plugins_by_stage.items():
            for plugin in stage_plugins:
                name = plugin.name
                try:
                    sortable_codebase_attributes.append(
                        (plugin.sort_order, name, plugin.codebase_attributes,)
                    )
                    codebase_attributes_by_plugin[plugin.qname] = plugin.codebase_attributes.keys()
                except:
                    msg = ('ERROR: failed to collect codebase_attributes for plugin: '
                           '%(stage)s:%(name)s:' % locals())
                    echo_stderr(msg, fg='red')
                    echo_stderr(traceback.format_exc())
                    ctx.exit(2)

        codebase_attributes = OrderedDict()
        for _, name, attribs in sorted(sortable_codebase_attributes):
            codebase_attributes.update(attribs)

        # FIXME: workaround for https://github.com/python-attrs/attrs/issues/339
        # we reset the _CountingAttribute internal ".counter" to a proper value
        # that matches our ordering
        for order, attrib in enumerate(codebase_attributes.values(), 100):
            attrib.counter = order

        if TRACE_DEEP:
            logger_debug('scancode:codebase_attributes')
            for a in codebase_attributes.items():
                logger_debug(a)

        ########################################################################
        # 3. collect codebase inventory
        ########################################################################

        inventory_start = time()

        if not quiet:
            echo_stderr('Collect file inventory...', fg='green')

        if from_json:
            codebase_class = VirtualCodebase
            codebase_load_error_msg = 'ERROR: failed to load codebase from scan file at: %(input)r'
        else:
            codebase_class = Codebase
            codebase_load_error_msg = 'ERROR: failed to collect codebase at: %(input)r'

        # TODO: add progress indicator
        # Note: inventory timing collection is built in Codebase initialization
        # TODO: this should also collect the basic size/dates
        try:
            codebase = codebase_class(
                location=input,
                resource_attributes=resource_attributes,
                codebase_attributes=codebase_attributes,
                full_root=full_root,
                strip_root=strip_root,
                temp_dir=temp_dir,
                max_in_memory=max_in_memory
            )
        except:
            msg = 'ERROR: failed to collect codebase at: %(input)r' % locals()
            echo_stderr(msg, fg='red')
            echo_stderr(traceback.format_exc())
            ctx.exit(2)

        cle = codebase.get_current_log_entry()
        cle.start_timestamp = start_timestamp

        # TODO: this is weird: may be the timings should NOT be stored on the
        # codebase, since they exist in abstract of it??
        codebase.timings.update(setup_timings)
        codebase.timings['inventory'] = time() - inventory_start
        files_count, dirs_count, size_count = codebase.compute_counts()
        codebase.counters['initial:files_count'] = files_count
        codebase.counters['initial:dirs_count'] = dirs_count
        codebase.counters['initial:size_count'] = size_count

        ########################################################################
        # 4. prescan scans: run the early scans required by prescan plugins
        ########################################################################
        # FIXME: this stage is extremely convoluted and needs cleaning!

        # resolve pre-scan plugin requirements that require a scan first
        early_scan_plugins = pre_scan.PreScanPlugin.get_all_required(
            pre_scan_plugins, scanner_plugins)

        pre_scan_scan_success = run_scanners(
            ctx, stage='pre-scan-scan', plugins=early_scan_plugins, codebase=codebase,
            processes=processes, timeout=timeout, timing=timing,
            quiet=quiet, verbose=verbose, kwargs=kwargs)
        success = success and pre_scan_scan_success

        ########################################################################
        # 5. run prescans
        ########################################################################

        # TODO: add progress indicator
        pre_scan_success = run_codebase_plugins(
            ctx, stage='pre-scan', plugins=pre_scan_plugins, codebase=codebase,
            stage_msg='Run %(stage)ss...',
            plugin_msg=' Run %(stage)s: %(name)s...',
            quiet=quiet, verbose=verbose, kwargs=kwargs,
        )
        success = success and pre_scan_success

        ########################################################################
        # 6. run scans.
        ########################################################################

        # do not rerun scans already done in early scans
        scan_proper_plugins = [p for p in scanner_plugins if p not in early_scan_plugins]

        scan_success = run_scanners(
            ctx, stage='scan', plugins=scan_proper_plugins, codebase=codebase,
            processes=processes, timeout=timeout, timing=timeout,
            quiet=quiet, verbose=verbose, kwargs=kwargs,
        )
        success = success and scan_success

        ########################################################################
        # 7. run postscans
        ########################################################################

        # TODO: add progress indicator
        post_scan_success = run_codebase_plugins(
            ctx, stage='post-scan', plugins=post_scan_plugins, codebase=codebase,
            stage_msg='Run %(stage)ss...', plugin_msg=' Run %(stage)s: %(name)s...',
            quiet=quiet, verbose=verbose, kwargs=kwargs,
        )
        success = success and post_scan_success

        ########################################################################
        # 8. apply output filters
        ########################################################################

        # TODO: add progress indicator
        output_filter_success = run_codebase_plugins(
            ctx, stage='output-filter', plugins=output_filter_plugins, codebase=codebase,
            stage_msg='Apply %(stage)ss...', plugin_msg=' Apply %(stage)s: %(name)s...',
            quiet=quiet, verbose=verbose, kwargs=kwargs,
        )
        success = success and output_filter_success

        ########################################################################
        # 9. save outputs
        ########################################################################

        counts = codebase.compute_counts(skip_root=strip_root, skip_filtered=True)
        files_count, dirs_count, size_count = counts

        codebase.counters['final:files_count'] = files_count
        codebase.counters['final:dirs_count'] = dirs_count
        codebase.counters['final:size_count'] = size_count
        cle.end_timestamp = time2tstamp()
        cle.tool = 'scancode-toolkit'
        cle.tool_version = scancode_version
        cle.notice = notice
        cle.options = get_pretty_params(ctx, generic_paths=test_mode)

        # TODO: add progress indicator
        output_success = run_codebase_plugins(
            ctx, stage='output', plugins=output_plugins, codebase=codebase,
            stage_msg='Save scan results...',
            plugin_msg=' Save scan results as: %(name)s...',
            quiet=quiet, verbose=verbose, kwargs=kwargs,
        )
        success = success and output_success

        ########################################################################
        # 9. display summary
        ########################################################################
        codebase.timings['total'] = time() - processing_start

        # TODO: compute summary for output plugins too??
        if not quiet:
            scan_names = ', '.join(p.name for p in scanner_plugins)
            echo_stderr('Scanning done.', fg='green' if success else 'red')
            display_summary(codebase, scan_names, processes, verbose=verbose)
    finally:
        # cleanup including cache cleanup
        if codebase:
            codebase.clear()

    rc = 0 if success else 1
    ctx.exit(rc)


def run_codebase_plugins(ctx, stage, plugins, codebase,
                         stage_msg='', plugin_msg='',
                         quiet=False, verbose=False, kwargs=None):
    """
    Run the list of `stage` `plugins` on `codebase`.
    Display errors and messages based on the `stage_msg`and `plugin_msg` strings
    and the `quiet` and `verbose` flags.
    Return True on success and False otherwise.
    Kwargs are passed down when calling the process_codebase method of each
    plugin.
    """
    kwargs = kwargs or {}

    stage_start = time()
    if verbose and plugins:
        echo_stderr(stage_msg % locals(), fg='green')

    success = True
    # TODO: add progress indicator
    for plugin in plugins:
        name = plugin.name
        plugin_start = time()

        if verbose:
            echo_stderr(plugin_msg % locals(), fg='green')

        try:
            if TRACE_DEEP:
                from pprint import pformat
                logger_debug('run_codebase_plugins: kwargs passed to %(stage)s:%(name)s' % locals())
                logger_debug(pformat(sorted(kwargs.items())))
                logger_debug()

            plugin.process_codebase(codebase, **kwargs)

        except Exception as _e:
            msg = 'ERROR: failed to run %(stage)s plugin: %(name)s:' % locals()
            echo_stderr(msg, fg='red')
            tb = traceback.format_exc()
            echo_stderr(tb)
            codebase.errors.append(msg + '\n' + tb)
            success = False

        timing_key = '%(stage)s:%(name)s' % locals()
        codebase.timings[timing_key] = time() - plugin_start

    codebase.timings[stage] = time() - stage_start
    return success


def run_scanners(ctx, stage, plugins, codebase,
                 processes, timeout, timing,
                 quiet=False, verbose=False, kwargs=None):
    """
    Run the list of `stage` ScanPlugin `plugins` on `codebase`.
    Use multiple `processes` and limit the runtime of a single scanner function
    to `timeout` seconds.
    Compute detailed timings if `timing` is True.
    Display progress and errors based on the `quiet` and `verbose` flags.
    Update the codebase with computed counts and scan results.
    Return True on success and False otherwise.
    Kwargs are passed down when calling the process_codebase method of each
    plugin.
    """

    kwargs = kwargs or {}

    scan_start = time()

    scanners = []
    for plugin in plugins:
        func = plugin.get_scanner(**kwargs)
        scanners.append(Scanner(name=plugin.name, function=func))

    if TRACE_DEEP: logger_debug('run_scanners: scanners:', scanners)
    if not scanners:
        return True

    scan_names = ', '.join(s.name for s in scanners)

    progress_manager = None
    if not quiet:
        echo_stderr('Scan files for: %(scan_names)s '
                    'with %(processes)d process(es)...' % locals())
        item_show_func = partial(path_progress_message, verbose=verbose)
        progress_manager = partial(progressmanager,
            item_show_func=item_show_func,
            verbose=verbose, file=sys.stderr)

    # TODO: add CLI option to bypass cache entirely?
    scan_success = scan_codebase(
        codebase, scanners, processes, timeout,
        with_timing=timing, progress_manager=progress_manager)

    # TODO: add progress indicator
    # run the process codebase of each scan plugin (most often a no-op)
    scan_process_codebase_success = run_codebase_plugins(
        ctx, stage, plugins, codebase,
        stage_msg='Filter %(stage)ss...',
        plugin_msg=' Filter %(stage)s: %(name)s...',
        quiet=quiet, verbose=verbose, kwargs=kwargs,
    )

    scan_success = scan_success and scan_process_codebase_success
    codebase.timings[stage] = time() - scan_start
    scanned_fc = scanned_dc = scanned_sc = 0
    try:
        scanned_fc, scanned_dc, scanned_sc = codebase.compute_counts()
    except:
        msg = 'ERROR: in run_scanners, failed to compute codebase counts:\n' + traceback.format_exc()
        codebase.errors.append(msg)
        scan_success = False

    codebase.counters[stage + ':scanners'] = scan_names
    codebase.counters[stage + ':files_count'] = scanned_fc
    codebase.counters[stage + ':dirs_count'] = scanned_dc
    codebase.counters[stage + ':size_count'] = scanned_sc

    return scan_success


def scan_codebase(codebase, scanners, processes=1, timeout=DEFAULT_TIMEOUT,
                  with_timing=False, progress_manager=None):
    """
    Run the `scanners` Scanner objects on the `codebase` Codebase. Return True
    on success or False otherwise.

    Use multiprocessing with `processes` number of processes. Disable
    multiprocessing  is processes <=0. Disable threading is processes is < 0

    Run each scanner function for up to `timeout` seconds and fail it otherwise.

    If `with_timing` is True, each Resource is updated with per-scanner
    execution time (as a float in seconds). This is added to the `scan_timings`
    mapping of each Resource as {scanner.name: execution time}.

    Provide optional progress feedback in the UI using the `progress_manager`
    callable that accepts an iterable of tuple of (location, rid, scan_errors,
    scan_result ) as argument.
    """

    # FIXME: this path computation is super inefficient tuples of  (absolute
    # location, resource id)

    # NOTE: we never scan directories
    resources = ((r.location, r.rid) for r in codebase.walk() if r.is_file)

    use_threading = (processes >= 0)
    runner = partial(scan_resource, scanners=scanners,
                     timeout=timeout, with_timing=with_timing,
                     with_threading=use_threading)

    if TRACE:
        logger_debug('scan_codebase: scanners:', ', '.join(s.name for s in scanners))

    get_resource = codebase.get_resource

    success = True
    pool = None
    scans = None
    try:
        if processes >= 1:
            # maxtasksperchild helps with recycling processes in case of leaks
            pool = get_pool(processes=processes, maxtasksperchild=1000)
            # Using chunksize is documented as much more efficient in the Python
            # doc. Yet "1" still provides a better and more progressive
            # feedback. With imap_unordered, results are returned as soon as
            # ready and out of order so we never know exactly what is processing
            # until completed.
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

                if TRACE_DEEP:
                    logger_debug(
                    'scan_codebase: location:', location, 'results:', scan_result)

                resource = get_resource(rid)

                if not resource:
                    # this should never happen
                    msg = ('ERROR: Internal error in scan_codebase: Resource '
                           'at %(rid)r is missing from codebase.\n'
                           'Scan result not saved:\n%(scan_result)r.' % locals())
                    codebase.errors.append(msg)
                    success = False
                    continue

                if scan_errors:
                    success = False
                    resource.scan_errors.extend(scan_errors)

                if TRACE: logger_debug('scan_codebase: scan_timings:', scan_timings)
                if with_timing and scan_timings:
                    if scan_timings:
                        resource.scan_timings.update(scan_timings)

                # NOTE: here we effectively single threaded the saving a
                # Resource to the cache! .... not sure this is a good or bad
                # thing for scale. Likely not
                # FIXME: should we instead store these in the Plugin resource_attributes?
                # these should be matched
                for key, value in scan_result.items():
                    if not value:
                        # the scan attribute will have a default value
                        continue
                    if key.startswith('extra_data.'):
                        key = key.replace('extra_data.', '')
                        resource.extra_data[key] = value
                    else:
                        setattr(resource, key, value)
                codebase.save_resource(resource)

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
    Return a tuple of (location, rid, scan_errors, scan_time, scan_results,
    timings) by running the `scanners` Scanner objects for the file or directory
    resource with id `rid` at `location` provided as a `location_rid` tuple of
    (location, rid) for up to `timeout` seconds. If `with_threading` is False,
    threading is disabled.

    The returned tuple has these values (:
    - `location` and `rid` are the orginal arguments.
    - `scan_errors` is a list of error strings.
    - `scan_results` is a mapping of scan results from all scanners.
    - `scan_time` is the duration in seconds to run all scans for this resource.
    - `timings` is a mapping of scan {scanner.name: execution time in seconds}
      tracking the execution duration each each scan individually.
      `timings` is empty unless `with_timing` is True.

    All these values MUST be serializable/pickable because of the way multi-
    processing/threading works.
    """
    scan_time = time()
    location, rid = location_rid
    results = OrderedDict()
    scan_errors = []
    timings = OrderedDict() if with_timing else None

    if not with_threading:
        interruptor = fake_interruptible
    else:
        interruptor = interruptible

    # run each scanner in sequence in its own interruptible
    for scanner in scanners:
        if with_timing:
            start = time()

        try:
            runner = partial(scanner.function, location)
            error, values_mapping = interruptor(runner, timeout=timeout)
            if error:
                msg = 'ERROR: for scanner: ' + scanner.name + ':\n' + error
                scan_errors.append(msg)
            # the return value of a scanner fun MUST be a mapping
            if values_mapping:
                results.update(values_mapping)

        except Exception:
            msg = 'ERROR: for scanner: ' + scanner.name + ':\n' + traceback.format_exc()
            scan_errors.append(msg)
        finally:
            if with_timing:
                timings[scanner.name] = time() - start

    scan_time = time() - scan_time

    return location, rid, scan_errors, scan_time, results, timings


def display_summary(codebase, scan_names, processes, verbose):
    """
    Display a scan summary.
    """
    initial_files_count = codebase.counters.get('initial:files_count', 0)
    initial_dirs_count = codebase.counters.get('initial:dirs_count', 0)
    initial_res_count = initial_files_count + initial_dirs_count
    initial_size_count = codebase.counters.get('initial:size_count', 0)
    if initial_size_count:
        initial_size_count = format_size(initial_size_count)
        initial_size_count = 'for %(initial_size_count)s' % locals()
    else:
        initial_size_count = ''

    ######################################################################
    prescan_scan_time = codebase.timings.get('pre-scan-scan', 0.)

    if prescan_scan_time:
        prescan_scan_files_count = codebase.counters.get('pre-scan-scan:files_count', 0)
        prescan_scan_file_speed = round(float(prescan_scan_files_count) / prescan_scan_time , 2)

        prescan_scan_size_count = codebase.counters.get('pre-scan-scan:size_count', 0)

        if prescan_scan_size_count:
            prescan_scan_size_speed = format_size(prescan_scan_size_count / prescan_scan_time)
            prescan_scan_size_speed = '%(prescan_scan_size_speed)s/sec.' % locals()

            prescan_scan_size_count = format_size(prescan_scan_size_count)
            prescan_scan_size_count = 'for %(prescan_scan_size_count)s' % locals()
        else:
            prescan_scan_size_count = ''
            prescan_scan_size_speed = ''

    ######################################################################
    scan_time = codebase.timings.get('scan', 0.)

    scan_files_count = codebase.counters.get('scan:files_count', 0)

    if scan_time:
        scan_file_speed = round(float(scan_files_count) / scan_time , 2)
    else:
        scan_file_speed = 0

    scan_size_count = codebase.counters.get('scan:size_count', 0)

    if scan_size_count:
        if scan_time:
            scan_size_speed = format_size(scan_size_count / scan_time)
        else:
            scan_size_speed = 0

        scan_size_speed = '%(scan_size_speed)s/sec.' % locals()

        scan_size_count = format_size(scan_size_count)
        scan_size_count = 'for %(scan_size_count)s' % locals()
    else:
        scan_size_count = ''
        scan_size_speed = ''

    ######################################################################
    final_files_count = codebase.counters.get('final:files_count', 0)
    final_dirs_count = codebase.counters.get('final:dirs_count', 0)
    final_res_count = final_files_count + final_dirs_count
    final_size_count = codebase.counters.get('final:size_count', 0)
    if final_size_count:
        final_size_count = format_size(final_size_count)
        final_size_count = 'for %(final_size_count)s' % locals()
    else:
        final_size_count = ''
    ######################################################################

    top_errors = codebase.errors
    path_and_errors = [(r.path, r.scan_errors)
                       for r in codebase.walk() if r.scan_errors]

    has_errors = top_errors or path_and_errors

    errors_count = 0
    if has_errors:
        echo_stderr('Some files failed to scan properly:', fg='red')
        for error in top_errors:
            echo_stderr(error)
            errors_count += 1

        for errored_path, errors in path_and_errors:
            echo_stderr('Path: ' + errored_path, fg='red')
            errors_count += 1
            if not verbose:
                continue

            for error in errors:
                for emsg in error.splitlines(False):
                    echo_stderr('  ' + emsg, fg='red')

    ######################################################################

    echo_stderr('Summary:        %(scan_names)s with %(processes)d process(es)' % locals())
    echo_stderr('Errors count:   %(errors_count)d' % locals())
    echo_stderr('Scan Speed:     %(scan_file_speed).2f files/sec. %(scan_size_speed)s' % locals())
    if prescan_scan_time:
        echo_stderr('Early Scanners Speed:     %(prescan_scan_file_speed).2f '
                    'files/sec. %(prescan_scan_size_speed)s' % locals())

    echo_stderr('Initial counts: %(initial_res_count)d resource(s): '
                                '%(initial_files_count)d file(s) '
                                'and %(initial_dirs_count)d directorie(s) '
                                '%(initial_size_count)s' % locals())

    echo_stderr('Final counts:   %(final_res_count)d resource(s): '
                                '%(final_files_count)d file(s) '
                                'and %(final_dirs_count)d directorie(s) '
                                '%(final_size_count)s' % locals())

    echo_stderr('Timings:')

    cle = codebase.get_current_log_entry().to_dict()
    echo_stderr('  scan_start: {start_timestamp}'.format(**cle))
    echo_stderr('  scan_end: {end_timestamp}'.format(**cle))

    for name, value, in codebase.timings.items():
        if value > 0.1:
            echo_stderr('  %(name)s: %(value).2fs' % locals())

    # TODO: if timing was requested display top per-scan/per-file stats?


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


def get_pretty_params(ctx, generic_paths=False):
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
    options = []

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
