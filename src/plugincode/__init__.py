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
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict
from collections import OrderedDict
import sys

import click
from click.types import BoolParamType
from pluggy import HookimplMarker
from pluggy import HookspecMarker
from pluggy import PluginManager as PluggyPluginManager
from six import string_types

# Tracing flags
TRACE = False


def logger_debug(*args):
    pass


if TRACE:
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, string_types)
                                     and a or repr(a) for a in args))


class PlugincodeError(Exception):
    """Base exception for plugincode errors"""


class BasePlugin(object):
    """
    A base class for all ScanCode plugins.
    """
    # stage string for this plugin.
    # This is set automatically when a plugin class is loaded in its manager.
    # Subclasses must not set this.
    stage = None

    # name string under which this plugin is registered.
    # This is set automatically when a plugin class is loaded in its manager.
    # Subclasses must not set this.
    name = None

    # An ordered mapping of attr attributes that specifies the Codebase
    # attributes data returned by this plugin. These attributes will be added to
    # a Codebase class. The position of these attributes in the returned
    # serialized data is determined by the sort_order then the plugin name
    codebase_attributes = OrderedDict()

    # An ordered mapping of attr attributes that specifies the Resource data
    # returned by this plugin. These attributes will be added to a Resource
    # subclass. The position of these attributes in the returned serialized data
    # is determined by the sort_order then the plugin name
    resource_attributes = OrderedDict()

    # List of PluggableCommandLineOption CLI options for this plugin.
    # Subclasses should set this as needed
    options = []

    # List of stage:name plugins that this plugin requires.
    # required plugins are guaranteed to be loaded and initialized before
    # a plugin is called to run.
    # Subclasses should set this as needed
    required_plugins = []

    # A list of Codebase attribute name strings that this plugin need to
    # be able to run.
    # A ScanCode run will fail with an error if these attributes are not
    # provided either as part of the scan data if resuing an existing scan or by
    # another plugin.
    # Subclasses should set this as needed.
    required_codebase_attributes = []

    # A list of Resource attribute name strings that this plugin need to
    # be able to run.
    # A ScanCode run will fail with an error if these attributes are not
    # provided either as part of the scan data if resuing an existing scan or by
    # another plugin.
    # Subclasses should set this as needed.
    required_resource_attributes = []

    # A relative sort order number (integer or float).
    # This is used to compute the order in which a plugin runs before
    # another plugin in a given stage
    # This is also used in scan results, results from scanners are sorted by
    # this sort_order then by plugin "name".
    sort_order = 100

    # flag set to True once this plugin class has been initialized by calling it
    # setup() class method.
    # This is set automatically when a plugin class is loaded in its manager.
    # Subclasses must not set this.
    initialized = False

    def __init__(self, *args, **kwargs):
        pass

    # TODO: pass own command options name/values as concrete kwargs
    def is_enabled(self, **kwargs):
        """
        Return True if this plugin is enabled by user-selected options.
        Subclasses must override.
        This receives all the ScanCode call arguments as kwargs.
        """
        raise NotImplementedError

    # TODO: pass own command options name/values as concrete kwargs
    def setup(self, **kwargs):
        """
        Execute some setup for this plugin. This is guaranteed to be called
        exactly one time at initialization if this plugin is enabled.
        Must raise an Exception on failure.
        Subclasses can override as needed.
        This receives all the ScanCode call arguments as kwargs.
        """
        pass

    # NOTE: Other methods below should NOT be overriden.

    @classmethod
    def qname(cls):
        """
        Return the qualified name of this plugin.
        """
        return '{cls.stage}:{cls.name}'.format(cls=cls)

    def __repr__(self, *args, **kwargs):
        return self.qname()


class CodebasePlugin(BasePlugin):
    """
    Base class for plugins that process a whole codebase at once.
    """

    def process_codebase(self, codebase, **kwargs):
        """
        Process a `codebase` Codebase object updating its Resources as needed.
        Subclasses should override.
        This receives all the ScanCode call arguments as kwargs.
        """
        raise NotImplementedError


class PluginManager(object):
    """
    A PluginManager class for scanning-related plugins.
    """

    # a global managers cache as a mapping of {stage: manager instance}
    managers = {}

    def __init__(self, stage, module_qname, entrypoint, plugin_base_class):
        """
        Initialize this plugin manager for the `stage` specified in the fully
        qualified Python module name `module_qname` with plugins loaded from the
        setuptools `entrypoint` that must subclass `plugin_base_class`.
        """
        self.manager = PluggyPluginManager(project_name=stage)
        self.managers[stage] = self

        self.stage = stage
        self.entrypoint = entrypoint
        self.plugin_base_class = plugin_base_class
        self.manager.add_hookspecs(sys.modules[module_qname])

        # set to True once this manager is initialized by running its setup()
        self.initialized = False

        # list of plugin_class for all the plugins of this manager
        self.plugin_classes = []

    @classmethod
    def load_plugins(cls):
        """
        Setup the plugins enviroment.
        Must be called once to initialize all the plugins of all managers.
        """
        plugin_classes = []
        plugin_options = []
        for stage, manager in cls.managers.items():
            mgr_setup = manager.setup()
            if not mgr_setup:
                msg = 'Cannot load plugins for stage: %(stage)s' % locals()
                raise PlugincodeError(msg)
            mplugin_classes, mplugin_options = mgr_setup
            plugin_classes.extend(mplugin_classes)
            plugin_options.extend(mplugin_options)
        return plugin_classes, plugin_options

    def setup(self):
        """
        Return a tuple of (list of all plugin classes, list of all options of
        all plugin classes).

        Load and validate available plugins for this PluginManager from its
        assigned `entrypoint`. Raise a PlugincodeError if a plugin is not valid such
        that when it does not subcclass the manager `plugin_base_class`.
        Must be called once to setup the plugins of this manager.
        """
        if self.initialized:
            return

        entrypoint = self.entrypoint
        try:
            self.manager.load_setuptools_entrypoints(entrypoint)
        except ImportError as e:
            raise e
        stage = self.stage

        plugin_options = []
        plugin_classes = []
        required_plugins = set()
        for name, plugin_class in self.manager.list_name_plugin():

            if not issubclass(plugin_class, self.plugin_base_class):
                qname = '%(stage)s:%(name)s' % locals()
                plugin_base_class = self.plugin_base_class
                raise PlugincodeError(
                    'Invalid plugin: %(qname)r: %(plugin_class)r '
                    'must extend %(plugin_base_class)r.' % locals())

            for option in plugin_class.options:
                if not isinstance(option, PluggableCommandLineOption):
                    qname = '%(stage)s:%(name)s' % locals()
                    oname = option.name
                    clin = PluggableCommandLineOption
                    raise PlugincodeError(
                        'Invalid plugin: %(qname)r: option %(oname)r '
                        'must extend %(clin)r.' % locals())
                plugin_options.append(option)

            plugin_class.stage = stage
            plugin_class.name = name

            plugin_classes.append(plugin_class)

        self.plugin_classes = sorted(plugin_classes, key=lambda c: (c.sort_order, c.name))
        self.initialized = True
        return self.plugin_classes, plugin_options


# CLI help groups
SCAN_GROUP = 'primary scans'
SCAN_OPTIONS_GROUP = 'scan options'
OTHER_SCAN_GROUP = 'other scans'
OUTPUT_GROUP = 'output formats'
OUTPUT_CONTROL_GROUP = 'output control'
OUTPUT_FILTER_GROUP = 'output filters'
PRE_SCAN_GROUP = 'pre-scan'
POST_SCAN_GROUP = 'post-scan'
MISC_GROUP = 'miscellaneous'
DOC_GROUP = 'documentation'
CORE_GROUP = 'core'


class PluggableCommandLineOption(click.Option):
    """
    An option with extra args and attributes to control CLI help options
    grouping, co-required and conflicting options (e.g. mutually exclusive).
    This option is also pluggable e.g. providable by a plugin.
    """

    # args are from Click 6.7
    def __init__(
        self,
        param_decls=None,
        show_default=False,
        prompt=False,
        confirmation_prompt=False,
        hide_input=False,
        is_flag=None,
        flag_value=None,
        multiple=False,
        count=False,
        allow_from_autoenv=True,
        type=None,  # NOQA
        help=None,  # NOQA
        # custom additions #
        # a string that set the CLI help group for this option
        help_group=MISC_GROUP,
        # a relative sort order number (integer or float) for this
        # option within a help group: the sort is by increasing
        # sort_order then by option declaration.
        sort_order=100,
        # a sequence of other option name strings that this option
        # requires to be set
        required_options=(),
        # a sequence of other option name strings that this option
        # conflicts with if they are set
        conflicting_options=(),
        # a flag set to True if this option should be hidden from the CLI help
        hidden=False,
        **attrs,
    ):

        super(PluggableCommandLineOption, self).__init__(param_decls, show_default,
                     prompt, confirmation_prompt,
                     hide_input, is_flag, flag_value,
                     multiple, count, allow_from_autoenv,
                     type, help, **attrs)

        self.help_group = help_group
        self.sort_order = sort_order
        self.required_options = required_options
        self.conflicting_options = conflicting_options
        self.hidden = hidden

    def __repr__(self, *args, **kwargs):
        name = self.name
        opt = self.opts[-1]
        help_group = self.help_group
        required_options = self.required_options
        conflicting_options = self.conflicting_options

        return ('PluggableCommandLineOption<name=%(name)r, '
                'required_options=%(required_options)r, conflicting_options=%(conflicting_options)r>' % locals())

    def validate_dependencies(self, ctx, value):
        """
        Validate `value` against declared `required_options` or `conflicting_options` dependencies.
        """
        _validate_option_dependencies(ctx, self, value, self.required_options, required=True)
        _validate_option_dependencies(ctx, self, value, self.conflicting_options, required=False)

    def get_help_record(self, ctx):
        if not self.hidden:
            return click.Option.get_help_record(self, ctx)


def validate_option_dependencies(ctx):
    """
    Validate all PluggableCommandLineOption dependencies in the `ctx` Click context.
    Ignore eager flags.
    """
    values = ctx.params
    if TRACE:
        logger_debug('validate_option_dependencies: values:')
        for va in sorted(values.items()):
            logger_debug('  ', va)

    for param in ctx.command.params:
        if param.is_eager:
            continue
        if not isinstance(param, PluggableCommandLineOption):
            if TRACE:
                logger_debug('  validate_option_dependencies: skip param:', param)
            continue
        value = values.get(param.name)
        if TRACE:
            logger_debug('  validate_option_dependencies: param:', param, 'value:', value)
        param.validate_dependencies(ctx, value)


def _validate_option_dependencies(ctx, param, value,
                                  other_option_names, required=False):
    """
    Validate the `other_option_names` option dependencies and return a
    UsageError if the `param` `value` is set to a not-None non-default value and
    if:
    - `required` is True and the `other_option_names` options are not set with a
       not-None value in the `ctx` context.
    - `required` is False and any of the `other_option_names` options are set
       with a not-None, non-default value in the `ctx` context.
    """
    if not other_option_names:
        return

    def _is_set(_value, _param):
        if _param.type in (bool, BoolParamType):
            return _value

        if _param.multiple:
            empty = (_value and len(_value) == 0) or not _value
        else:
            empty = _value is None

        return bool(not empty and _value != _param.default)

    is_set = _is_set(value, param)

    if TRACE:
        logger_debug()
        logger_debug('Checking param:', param)
        logger_debug('  value:', value, 'is_set:' , is_set)

    if not is_set:
        return

    oparams_by_name = {oparam.name: oparam for oparam in ctx.command.params}
    oparams = []
    missing_onames = []

    for oname in other_option_names:
        oparam = oparams_by_name.get(oname)
        if not oparam:
            missing_onames.append(oparam)
        else:
            oparams.append(oparam)

    if TRACE:
        logger_debug()
        logger_debug('  Available other params:')
        for oparam in oparams:
            logger_debug('    other param:', oparam)
            logger_debug('      value:', ctx.params.get(oparam.name))
        if required:
            logger_debug('    missing names:', missing_onames)

    if required and missing_onames:
        opt = param.opts[-1]
        oopts = [oparam.opts[-1] for oparam in oparams]
        omopts = ['--' + oname.replace('_', '-') for oname in missing_onames]
        oopts.extend(omopts)
        oopts = ', '.join(oopts)
        msg = ('The option %(opt)s requires the option(s) %(all_opts)s.'
               'and is missing %(omopts)s. '
               'You must set all of these options if you use this option.' % locals())
        raise click.UsageError(msg)

    if TRACE:
        logger_debug()
        logger_debug('  Checking other params:')

    opt = param.opts[-1]

    for oparam in oparams:
        ovalue = ctx.params.get(oparam.name)
        ois_set = _is_set(ovalue, oparam)

        if TRACE:
            logger_debug('    Checking oparam:', oparam)
            logger_debug('      value:', ovalue, 'ois_set:' , ois_set)

        # by convention the last opt is the long form
        oopt = oparam.opts[-1]
        oopts = ', '.join(oparam.opts[-1] for oparam in oparams)
        all_opts = '%(opt)s and %(oopts)s' % locals()
        if required and not ois_set:
            msg = ('The option %(opt)s requires the option(s) %(oopts)s '
                   'and is missing %(oopt)s. '
                   'You must set all of these options if you use this option.' % locals())
            raise click.UsageError(msg)

        if not required  and ois_set:
            msg = ('The option %(opt)s cannot be used together with the %(oopts)s option(s) '
                   'and %(oopt)s is used. '
                   'You can set only one of these options at a time.' % locals())
            raise click.UsageError(msg)

