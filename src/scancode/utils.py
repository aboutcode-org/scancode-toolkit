#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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

from __future__ import print_function, absolute_import

import click
from click._termui_impl import ProgressBar
from click.utils import echo

from commoncode import fileutils


"""
Various CLI UI utilities, many related to Click and progress reporting.
"""


class BaseCommand(click.Command):
    """
    An enhanced click Command working around some Click quirk.
    """

    # override this in sub-classes with a command-specific message such as
    # "Try 'scancode --help' for help on options and arguments."
    short_usage_help = ''

    def get_usage(self, ctx):
        """
        Ensure that usage points to the --help option explicitly.
        Workaround click issue https://github.com/mitsuhiko/click/issues/393
        """
        return super(BaseCommand, self).get_usage(ctx) + self.short_usage_help

    def main(self, args=None, prog_name=None, complete_var=None,
             standalone_mode=True, **extra):
        """
        Workaround click 4.0 bug https://github.com/mitsuhiko/click/issues/365
        """
        return click.Command.main(self, args=args, prog_name=self.name,
                                  complete_var=complete_var,
                                  standalone_mode=standalone_mode, **extra)


class EnhancedProgressBar(ProgressBar):
    """
    Enhanced progressbar ensuring that nothing is displayed when the bar is hidden.
    """
    def render_progress(self):
        if not self.is_hidden:
            return ProgressBar.render_progress(self)


class NoOpProgressBar(EnhancedProgressBar):
    """
    A ProgressBar-like object that does not show any progress.
    """
    def __init__(self, *args, **kwargs):
        super(NoOpProgressBar, self).__init__(*args, **kwargs)
        self.is_hidden = True


class ProgressLogger(ProgressBar):
    """
    A subclass of Click ProgressBar providing a verbose line- by-line progress
    reporting.

    In contrast with the progressbar the label, percent, ETA, pos, bar_template
    and other formatting options are ignored.

    Progress information are printed as-is and no LF is added. The caller must
    provide an item_show_func to display some content and this must terminated
    with a line feed if needed.

    If no item_show_func is provided a simple dot is printed for each event.
    """

    def render_progress(self):
        line = self.format_progress_line()
        if line:
            # only add new lines if there is an item_show_func
            nl = bool(self.item_show_func)
            echo(line, file=self.file, nl=nl, color=self.color)
            self.file.flush()

    def format_progress_line(self):
        if self.item_show_func:
            item_info = self.item_show_func(self.current_item)
        else:
            item_info = '.'
        if item_info:
            return item_info


def progressmanager(iterable=None, length=None, label=None, show_eta=True,
                    show_percent=None, show_pos=False, item_show_func=None,
                    fill_char='#', empty_char='-', bar_template=None,
                    info_sep='  ', width=36, file=None, color=None,
                    verbose=False, quiet=False):

    """This function creates an iterable context manager showing progress as a
    bar (default) or line-by-line log (if verbose is True) while iterating.

    Its arguments are similar to Click.termui.progressbar with
    these new arguments added at the end of the signature:

    :param verbose:          if False, display a progress bar, otherwise a progress log
    :param quiet:            If True, do not display any progress message.
    """
    if quiet:
        progress_class = NoOpProgressBar
    elif verbose:
        progress_class = ProgressLogger
    else:
        progress_class = EnhancedProgressBar
        bar_template = ('%(label)s  [%(bar)s]  %(info)s'
                        if bar_template is None else bar_template)

    return progress_class(iterable=iterable, length=length, show_eta=show_eta,
                          show_percent=show_percent, show_pos=show_pos,
                          item_show_func=item_show_func, fill_char=fill_char,
                          empty_char=empty_char, bar_template=bar_template,
                          info_sep=info_sep, file=file, label=label,
                          width=width, color=color)


def get_relative_path(path, len_base_path, base_is_dir):
    """
    Compute a new posix path based on 'path' relative to the base in original
    format or a fully resolved posix format.
    """
    if base_is_dir:
        rel_path = path[len_base_path:]
    else:
        rel_path = fileutils.file_name(path)
    return rel_path.lstrip('/')
