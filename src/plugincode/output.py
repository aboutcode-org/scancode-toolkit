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

from collections import OrderedDict
from functools import partial
from os.path import abspath
from os.path import dirname
from os.path import expanduser
from sys import stderr
from sys import stdout

from commoncode.fileutils import create_dir
from commoncode.fileutils import fsdecode
from commoncode.system import on_linux
from plugincode import CodebasePlugin
from plugincode import PluginManager
from plugincode import HookimplMarker
from plugincode import HookspecMarker
from scancode.resource import Resource


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
    logging.basicConfig(stream=stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, unicode)
                                     and a or repr(a) for a in args))


stage = 'output'
entrypoint = 'scancode_output'

output_spec = HookspecMarker(project_name=stage)
output_impl = HookimplMarker(project_name=stage)


@output_spec
class OutputPlugin(CodebasePlugin):
    """
    Base plugin class for scan output formatters all output plugins must extend.
    """

    # TODO: pass own command options name/values as concrete kwargs
    def process_codebase(self, codebase, **kwargs):
        """
        FIXME: this is a stopgap, intermediate implementation
        Write scan output for the `codebase`.
        """
        serializer = partial(Resource.to_dict,
            full_root=codebase.full_root,
            strip_root=codebase.strip_root,
            with_info=codebase.with_info)

        filtered_rids = codebase.filtered_rids
        if TRACE_DEEP:
            logger_debug('OutputPlugin.process_codebase: filtered_rids:', filtered_rids)
        resources = [res for res in codebase.walk(
            topdown=True, sort=True, skip_root=codebase.strip_root)
            # we apply any filter plugins here
            if res.rid not in filtered_rids
        ]
        # TODO: add dirs to results
        files_count, _dirs_count = codebase.resource_counts(resources)
        
        results = [serializer(res)
            for res in codebase.walk(topdown=True, sort=True, skip_root=codebase.strip_root)
            # we apply any filter plugins here
            if res.rid not in filtered_rids
        ]

        version = codebase.summary['scancode_version']
        notice = codebase.summary['scancode_notice']

        # TODO: consider getting this from the codebase?
        options = get_pretty_options(self.command_options, self._test_mode)

        return self.save_results(codebase, results, files_count, version, notice, options)

    def save_results(self, codebase, results, files_count, version, notice, options, *args, **kwargs):
        """
        FIXME: this is a stopgap, intermediate implementation
        Write scan `results` to `output_file`
        """
        raise NotImplementedError

    def create_parent_directory(self, output_file):
        """
        Create parent directory for the `output_file` file-like object if needed.
        """
        # FIXME: this IS NOT RIGHT!!!

        # We use this to check if this is a real filesystem file or not.
        # note: sys.stdout.name == '<stdout>' so it has a name.
        has_name = hasattr(output, 'name')
        output_is_real_file = output not in (stdout, stderr) and has_name
        if output_is_real_file:
            # we are writing to a real filesystem file: create directories!
            parent_dir = dirname(output_file.name)
            if parent_dir:
                create_dir(abspath(expanduser(parent_dir)))

    def setup_output_file(self, output_file):
        """
        Return `output_file` fully resolved and in the proper OS encoding.
        Create intermediate directoties if needed.
        """
        if on_linux:
            output_file = fsdecode(output_file)
        output_file = abspath(expanduser(output_file))
        self.create_parent_directory(output_file)
        return output_file


def get_pretty_options(command_options, generic_paths=False):
    """
    Return a sorted mapping of {CLI option: pretty value string} for the
    `command_options` list of CommandOption as in:
        {"--license": True, "input": ~some/path}

    Skip options with with None or empty seq values or a value set to its
    default. Skip eager and hidden options.

    If `generic_paths` is True, click.File and click.Path parameters are made
    "generic" replacing their value with a placeholder. This is used mostly for
    testing.
    """
    import click

    if TRACE:
        logger_debug('get_pretty_options: generic_paths', generic_paths)
    args = []
    options = []
    for option in command_options:
        value = option.value
        param = option.param
        if value == param.default:
            continue

        if param.is_eager:  
            continue

        if value is None:
            continue

        # not yet in Click 6.7 or param.hidden:
        if option.name == 'test_mode':
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


output_plugins = PluginManager(
    stage=stage,
    module_qname=__name__,
    entrypoint=entrypoint,
    plugin_base_class=OutputPlugin
)
