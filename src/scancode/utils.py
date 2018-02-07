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

import click
click.disable_unicode_literals_warning = True
from click.utils import echo
from click.termui import style
from click._termui_impl import ProgressBar

from commoncode.fileutils import file_name
from commoncode.fileutils import splitext
from commoncode.text import toascii

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

"""
Command line UI utilities for help and and progress reporting.
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
            return super(EnhancedProgressBar, self).render_progress()


class ProgressLogger(ProgressBar):
    """
    A subclass of Click ProgressBar providing a verbose line-by-line progress
    reporting.

    In contrast with the progressbar the label, percent, ETA, pos, bar_template
    and other formatting options are ignored.

    Progress information are printed as-is and no LF is added. The caller must
    provide an item_show_func to display some content and this must terminated
    with a line feed if needed.

    If no item_show_func is provided a simple dot is printed for each event.
    """

    def __init__(self, *args, **kwargs):
        super(ProgressLogger, self).__init__(*args, **kwargs)
        self.is_hidden = False

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

    def render_finish(self):
        self.file.flush()


BAR_WIDTH = 20
BAR_SEP = ' '
BAR_SEP_LEN = len(BAR_SEP)


def progressmanager(iterable=None, length=None, label=None, show_eta=True,
                    show_percent=None, show_pos=True, item_show_func=None,
                    fill_char='#', empty_char='-', bar_template=None,
                    info_sep=BAR_SEP, width=BAR_WIDTH, file=None, color=None,  # NOQA
                    verbose=False):

    """
    Return an iterable context manager showing progress as a progress bar
    (default) or item-by-item log (if verbose is True) while iterating.

    Its arguments are similar to Click.termui.progressbar with these new
    arguments added at the end of the signature:

    :param verbose:  if True, display a progress log. Otherwise, a progress bar.
    """
    if verbose:
        progress_class = ProgressLogger
    else:
        progress_class = EnhancedProgressBar
        bar_template = ('[%(bar)s]' + BAR_SEP + '%(info)s'
                        if bar_template is None else bar_template)

    return progress_class(iterable=iterable, length=length,
            show_eta=show_eta, show_percent=show_percent, show_pos=show_pos,
            item_show_func=item_show_func, fill_char=fill_char,
            empty_char=empty_char, bar_template=bar_template, info_sep=info_sep,
            file=file, label=label, width=width, color=color)


def fixed_width_file_name(path, max_length=25):
    """
    Return a fixed width file name of at most `max_length` characters computed
    from the `path` string and usable for fixed width display. If the `path`
    file name is longer than `max_length`, the file name is truncated in the
    middle using three dots "..." as an ellipsis and the ext is kept.

    For example:
    >>> fwfn = fixed_width_file_name('0123456789012345678901234.c')
    >>> assert '0123456789...5678901234.c' == fwfn
    >>> fwfn = fixed_width_file_name('some/path/0123456789012345678901234.c')
    >>> assert '0123456789...5678901234.c' == fwfn
    >>> fwfn = fixed_width_file_name('some/sort.c')
    >>> assert 'sort.c' == fwfn
    >>> fwfn = fixed_width_file_name('some/123456', max_length=5)
    >>> assert '' == fwfn
    """
    if not path:
        return ''

    # get the path as unicode for display!
    filename = file_name(path)
    if len(filename) <= max_length:
        return filename
    base_name, ext = splitext(filename)
    dots = 3
    len_ext = len(ext)
    remaining_length = max_length - len_ext - dots

    if remaining_length < 5  or remaining_length < (len_ext + dots):
        return ''

    prefix_and_suffix_length = abs(remaining_length // 2)
    prefix = base_name[:prefix_and_suffix_length]
    ellipsis = dots * '.'
    suffix = base_name[-prefix_and_suffix_length:]
    return '{prefix}{ellipsis}{suffix}{ext}'.format(**locals())


def file_name_max_len(used_width=BAR_WIDTH + BAR_SEP_LEN + 7 + BAR_SEP_LEN + 8 + BAR_SEP_LEN):
    """
    Return the max length of a path given the current terminal width.

    A progress bar is composed of these elements:
      [-----------------------------------#]  1667  Scanned: tu-berlin.yml
    - the bar proper which is BAR_WIDTH characters
    - one BAR_SEP
    - the number of files. We set it to 7 chars, eg. 9 999 999 files
    - one BAR_SEP
    - the word Scanned: 8 chars
    - one BAR_SEP
    - the file name proper
    The space usage is therefore:
        BAR_WIDTH + BAR_SEP_LEN + 7 + BAR_SEP_LEN + 8 + BAR_SEP_LEN
        + the file name length
    """
    term_width, _height = click.get_terminal_size()
    max_filename_length = term_width - used_width
    return max_filename_length


def path_progress_message(item, verbose=False, prefix='Scanned: '):
    """
    Return a styled message suitable for progress display when processing a path
    for an `item` tuple of (location, rid, scan_errors, *other items)
    """
    if not item:
        return ''
    location = item[0]
    errors = item[2]
    location = unicode(toascii(location))
    progress_line = location
    if not verbose:
        max_file_name_len = file_name_max_len()
        # do not display a file name in progress bar if there is no space available
        if max_file_name_len <= 10:
            return ''
        progress_line = fixed_width_file_name(location, max_file_name_len)

    color = 'red' if errors else 'green'
    return style(prefix) + style(progress_line, fg=color)
