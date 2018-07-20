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

from collections import namedtuple
from itertools import chain
from os.path import dirname
from os.path import abspath
from os.path import getsize
from os.path import getmtime
from os.path import join
from os.path import exists
from types import BooleanType

import click
from click.types import BoolParamType

from commoncode import fileutils

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


def logger_debug(*args):
    pass


if TRACE:
    import logging
    import sys
    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, (unicode, str))
                                     and a or repr(a) for a in args))

# CLI help groups
SCAN_GROUP = 'primary scans'
SCAN_OPTIONS_GROUP = 'scan options'
OTHER_SCAN_GROUP = 'other scans'
OUTPUT_GROUP = 'output formats'
OUTPUT_FILTER_GROUP = 'output filters'
OUTPUT_CONTROL_GROUP = 'output control'
PRE_SCAN_GROUP = 'pre-scan'
POST_SCAN_GROUP = 'post-scan'
MISC_GROUP = 'miscellaneous'
DOC_GROUP = 'documentation'
CORE_GROUP = 'core'

# Holds a scan plugin result "key and the corresponding function.
# click.Parameter instance
Scanner = namedtuple('Scanner', 'name function')


class CommandLineOption(click.Option):
    """
    An option with extra args and attributes to control CLI help options
    grouping, co-required and conflicting options (e.g. mutually exclusive).
    """

    # args are from Click 6.7
    def __init__(self, param_decls=None, show_default=False,
                 prompt=False, confirmation_prompt=False,
                 hide_input=False, is_flag=None, flag_value=None,
                 multiple=False, count=False, allow_from_autoenv=True,
                 type=None, help=None,  # NOQA
                 # custom additions #
                 # a string that set the CLI help group for this option
                 help_group=MISC_GROUP,
                 # a relative sort order number (integer or float) for this
                 # option within a help group: the sort is by increasing
                 # sort_order then by option declaration.
                 sort_order=100,
                 # a sequence of other option name strings that this option
                 # requires to be set
                 requires=(),
                 # a sequence of other option name strings that this option
                 # conflicts with if they are set
                 conflicts=(),
                 # a flag set to True if this option should be hidden from the CLI help
                 hidden=False,
                 **attrs):

        super(CommandLineOption, self).__init__(param_decls, show_default,
                     prompt, confirmation_prompt,
                     hide_input, is_flag, flag_value,
                     multiple, count, allow_from_autoenv,
                     type, help, **attrs)

        self.help_group = help_group
        self.sort_order = sort_order
        self.requires = requires
        self.conflicts = conflicts
        self.hidden = hidden

    def __repr__(self, *args, **kwargs):
        name = self.name
        opt = self.opts[-1]
        help_group = self.help_group
        requires = self.requires
        conflicts = self.conflicts

        return ('CommandLineOption<name=%(name)r, '
                'requires=%(requires)r, conflicts=%(conflicts)r>' % locals())

    def validate_dependencies(self, ctx, value):
        """
        Validate `value` against declared `requires` or `conflicts` dependencies.
        """
        _validate_option_dependencies(ctx, self, value, self.requires, required=True)
        _validate_option_dependencies(ctx, self, value, self.conflicts, required=False)


def validate_option_dependencies(ctx):
    """
    Validate all CommandLineOption dependencies in the `ctx` Click context.
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
        if not isinstance(param, CommandLineOption):
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
        if _param.type in (BooleanType, BoolParamType):
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


class FileOptionType(click.File):
    """
    A click.File subclass that ensures that a file name is not set to an
    existing option parameter to avoid mistakes.
    """

    def convert(self, value, param, ctx):
        known_opts = set(chain.from_iterable(p.opts for p in ctx.command.params
                                             if isinstance(p, click.Option)))
        if value in known_opts:
            self.fail('Illegal file name conflicting with an option name: %s. '
                      'Use the special "-" file name to print results on screen/stdout.'
                % (click.types.filename_to_ui(value),
            ), param, ctx)
        return click.File.convert(self, value, param, ctx)


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
    """
    Click callback to print a notice.
    """
    if not value or ctx.resilient_parsing:
        return
    click.echo(info_text + notice_text + acknowledgment_text + extra_notice_text)
    ctx.exit()
