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
import posixpath


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
    Enhanced Click progressbar adding custom first and last messages on enter
    and exit.
    """
    def __init__(self, iterable, length=None, fill_char='#', empty_char=' ',
                 bar_template='%(bar)s', info_sep='  ', show_eta=True,
                 show_percent=None, show_pos=False, item_show_func=None,
                 label=None, file=None, color=None, width=30,  # @ReservedAssignment
                 start_show_func=None, finish_show_func=None):
        """
        New parameters added on top of ProgressBar: start_show_func and
        finish_show_func to drive some display at the start and finish of a
        progression.
        """
        ProgressBar.__init__(self, iterable, length=length, fill_char=fill_char,
                             empty_char=empty_char, bar_template=bar_template,
                             info_sep=info_sep, show_eta=show_eta,
                             show_percent=show_percent, show_pos=show_pos,
                             item_show_func=item_show_func, label=label,
                             file=file, color=color, width=width)
        self.start_show_func = start_show_func
        self.finish_show_func = finish_show_func

    def __enter__(self):
        self.render_start()
        return ProgressBar.__enter__(self)

    def render_start(self):
        if self.is_hidden:
            return
        if self.start_show_func is not None:
            text = self.start_show_func()
            if text:
                echo(text, file=self.file, color=self.color)
                self.file.flush()

    def render_finish(self):
        if self.is_hidden:
            return
        super(EnhancedProgressBar, self).render_finish()
        self.show_finish()

    def show_finish(self):
        if self.finish_show_func is not None:
            text = self.finish_show_func()
            if text:
                echo(text, file=self.file, color=self.color)
                self.file.flush()

    def render_progress(self):
        if not self.is_hidden:
            return ProgressBar.render_progress(self)


class ProgressLogger(EnhancedProgressBar):
    """
    A subclass of Click ProgressBar providing a simpler and more verbose line-
    by-line progress reporting.

    In contrast with the progressbar the label, percent, ETA, pos, bar_template
    and other formatting options are ignored.

    Progress information are printed as-is and no LF is added. The caller must
    provide an intem_show_func to display some content and this must terminated
    with a line feed if needed.

    If no item_show_func is provided a simple dot is printed for each event.
    """

    def render_progress(self):
        if self.is_hidden:
            return
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

    def render_finish(self):
        if self.is_hidden:
            return
        # display a new line after the 'dots' IFF we do not have a show func
        nl = not bool(self.item_show_func)
        echo(None, file=self.file, nl=nl, color=self.color)
        self.show_finish()


class NoOpProgressBar(EnhancedProgressBar):
    """
    A ProgressBar-like object that does not show any progress.
    """
    def __init__(self, *args, **kwargs):
        EnhancedProgressBar.__init__(self, *args, **kwargs)
        self.is_hidden = True


def progressmanager(iterable=None, length=None, label=None, show_eta=True,
                    show_percent=None, show_pos=False, item_show_func=None,
                    fill_char='#', empty_char='-', bar_template=None,
                    info_sep='  ', width=36, file=None, color=None,  # @ReservedAssignment
                    verbose=False, start_show_func=None, finish_show_func=None,
                    quiet=False):

    """This function creates an iterable context manager showing progress as a
    bar (default) or line-by-line log (if verbose is True) while iterating.

    Its arguments are similar to Click.termui.progressbar with
    these new arguments added at the end of the signature:

    :param verbose:          if False, display a progress bar, otherwise a progress log
    :param start_show_func:  a function called at the start of iteration that
                             can return a string to display as an
                             introduction text before the progress.
    :param finish_show_func: a function called at the end of iteration that
                             can return a string to display after the
                             progress.
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
                          width=width, color=color,
                          start_show_func=start_show_func,
                          finish_show_func=finish_show_func)


def get_relative_path(base, base_resolved, path):
    """
    Compute a new posix path based on 'path' relative to the base in original
    format or a fully resolved posix format.
    """
    # this takes care of a single file or a top level directory
    if base_resolved == path:
        return base
    relative = posixpath.join(base, path[len(base_resolved):].lstrip('/'))
    return relative
