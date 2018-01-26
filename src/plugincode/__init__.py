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

from collections import OrderedDict
import sys

from pluggy import HookimplMarker
from pluggy import HookspecMarker
from pluggy import PluginManager as PluggyPluginManager
from scancode import CommandLineOption


class BasePlugin(object):
    """
    A base class for all ScanCode plugins.
    """
    # List of stage:name strings that this plugin requires to run before it
    # runs.
    # Subclasses should set this as needed
    requires = []

    # List of CommandLineOption CLI options for this plugin.
    # Subclasses should set this as needed
    options = []

    # flag set to True once this plugin class has been initialized by calling it
    # setup() class method.
    # This is set automatically when a plugin class is loaded in its manager.
    # Subclasses must not set this.
    initialized = False

    # stage string for this plugin.
    # This is set automatically when a plugin class is loaded in its manager.
    # Subclasses must not set this.
    stage = None

    # name string under which this plugin is registered.
    # This is set automatically when a plugin class is loaded in its manager.
    # Subclasses must not set this.
    name = None

    def __init__(self, *args, **kwargs):
        """
        Initialize a new plugin with a user kwargs.
        Plugins can override as needed (still calling super).
        """
        self.options_by_name = {o.name: o for o in self.options}

        self.kwargs = kwargs

        # mapping of scan summary data and statistics.
        # This is populated automatically on the plugin instance.
        # Subclasses must not set this.
        self.summary = OrderedDict()

    # TODO: pass own command options name/values as concrete kwargs
    def is_enabled(self, **kwargs):
        """
        Return True is this plugin is enabled by user-selected options.
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

    @property
    def qname(self):
        """
        Return the qualified name of this plugin.
        """
        return '{self.stage}:{self.name}'.format(self=self)

    def get_option(self, name):
        """
        Return the CommandLineOption of this plugin with `name` or None.
        """
        return self.options_by_name.get(name)

    def is_active(self, plugins, *args, **kwargs):
        """
        Return True is this plugin is enabled meaning it is enabled and all its
        required plugins are enabled.
        """
        return (self.is_enabled()
                and all(p.is_enabled() for p in self.requirements(plugins)))

    def requirements(self, plugins, resolved=None):
        """
        Return a tuple of (original list of `plugins` arg, as-is, list of unique
        required plugins by this plugin recursively) given a `plugins` list of all
        plugins and an optional list of already `resolved` plugins.

        Raise an Exception if there are inconsistencies in the plugins graph,
        such as self-referencing plugins, missing plugins or requirements
        cycles.
        """
        if  resolved is None:
            resolved = []

        qname = self.qname
        required_qnames = unique(qn for qn in self.requires if qn != qname)
        plugins_by_qname = {p.qname: p for p in plugins}
        resolved_by_qname = {p.qname: p for p in resolved}

        direct_requirements = []
        for required_qname in self.requires:

            if required_qname == self.name:
                raise Exception(
                    'Plugin %(qname)r cannot require itself.' % locals())

            if required_qname not in plugins_by_qname:
                raise Exception(
                    'Missing required plugin %(required_qname)r '
                    'for plugin %(qname)r.' % locals())

            if required_qname in resolved_by_qname:
                # already satisfied
                continue

            required = plugins_by_qname[required_qname]
            direct_requirements.append(required)
            resolved.append(required)

        for required in direct_requirements:
            plugins, resolved = required.walk_requirements(plugins, resolved)

            if self in resolved:
                req_chain = ' -> '.join(p.qname for p in resolved)
                raise Exception(
                    'Requirements for plugin %(qname)r are circular: '
                    '%(req_chain)s.' % locals())

        return plugins, resolved


class CodebasePlugin(BasePlugin):
    """
    Base class for plugins that process a whole codebase at once.
    """
    # flag set to True if this plugin needs file information available to run.
    # Subclasses should set this as needed.
    needs_info = False

    def process_codebase(self, codebase, **kwargs):
        """
        Process a `codebase` Codebase object updating its Reousrce as needed.
        Subclasses should override.
        This receives all the ScanCode call arguments as kwargs.
        """
        raise NotImplementedError


def unique(iterable):
    """
    Return a sequence of unique items in `iterable` keeping their original order.
    """
    seen = set()
    uni = []
    for item in iterable:
        if item in seen:
            continue
        uni.append(item)
        seen.add(item)
    return uni


class PluginManager(object):
    """
    A PluginManager class for plugins.
    """

    # a global managers cache as a mapping of {stage: manager instance}
    managers = {}

    def __init__(self, stage, module_qname, entrypoint, plugin_base_class):
        """
        Initialize this manager for the `stage` string in
        module `module_qname` with plugins loaded from the setuptools
        `entrypoint` that must subclass `plugin_base_class`.
        """
        self.manager = PluggyPluginManager(project_name=stage)
        self.managers[stage] = self

        self.stage = stage
        self.entrypoint = entrypoint
        self.plugin_base_class = plugin_base_class
        self.manager.add_hookspecs(sys.modules[module_qname])

        # set to True once this manager is initialized by running its setup()
        self.initialized = False

        # mapping of {plugin.name: plugin_class} for all the plugins of this
        # manager
        self.plugin_classes = OrderedDict()

    @classmethod
    def setup_all(cls):
        """
        Setup the plugins enviroment.
        Must be called once to initialize all the plugins of all managers.
        """
        plugin_classes = []
        plugin_options = []
        for _stage, manager in cls.managers.items():
            mplugin_classes, mplugin_options = manager.setup()
            plugin_classes.extend(mplugin_classes)
            plugin_options.extend(mplugin_options)
        return plugin_classes, plugin_options

    def setup(self):
        """
        Return a tuple of (list of all plugin classes, list of all options of
        all plugin classes).

        Load and validate available plugins for this PluginManager from its
        assigned `entrypoint`. Raise an Exception if a plugin is not valid such
        that when it does not subcclass the manager `plugin_base_class`.
        Must be called once to setup the plugins if this manager.
        """
        if self.initialized:
            return

        entrypoint = self.entrypoint
        self.manager.load_setuptools_entrypoints(entrypoint)
        stage = self.stage

        plugin_options = []
        for name, plugin_class in self.manager.list_name_plugin():

            if not issubclass(plugin_class, self.plugin_base_class):
                qname = '%(entrypoint)s:%(name)s' % locals()
                raise Exception(
                    'Invalid plugin: %(qname)r: %(plugin_class)r '
                    'must extend %(plugin_base_class)r.' % locals())

            for option in plugin_class.options:
                if not isinstance(option, CommandLineOption):
                    qname = '%(entrypoint)s:%(name)s' % locals()
                    oname = option.name
                    clin = CommandLineOption
                    raise Exception(
                        'Invalid plugin: %(qname)r: option %(oname)r '
                        'must extend %(clin)r.' % locals())
                plugin_options.append(option)

            plugin_class.stage = stage
            plugin_class.name = name

            self.plugin_classes[name] = plugin_class

        self.initialized = True
        return self.plugin_classes.values(), plugin_options
