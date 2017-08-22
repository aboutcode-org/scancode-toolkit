#
# Copyright (c) 2016 nexB Inc. and others. All rights reserved.
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
from __future__ import division
from __future__ import unicode_literals

import sys

import click
from click.utils import echo
from click._termui_impl import ProgressBar

from commoncode import fileutils
from commoncode.text import as_unicode


"""
Various CLI UI utilities, many related to Click and progress reporting.
"""

# Python 2 and 3 support
try:
    # Python 2
    unicode
except NameError:
    # Python 3
    unicode = str


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


class NoOpProgressBar(EnhancedProgressBar):
    """
    A ProgressBar-like object that does not show any progress.
    """
    def __init__(self, *args, **kwargs):
        super(NoOpProgressBar, self).__init__(*args, **kwargs)
        self.is_hidden = True


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
                    show_percent=None, show_pos=False, item_show_func=None,
                    fill_char='#', empty_char='-', bar_template=None,
                    info_sep=BAR_SEP, width=BAR_WIDTH, file=None, color=None,
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
        bar_template = ('[%(bar)s]' + BAR_SEP + '%(info)s'
                        if bar_template is None else bar_template)

    return progress_class(iterable=iterable, length=length, show_eta=show_eta,
                          show_percent=show_percent, show_pos=show_pos,
                          item_show_func=item_show_func, fill_char=fill_char,
                          empty_char=empty_char, bar_template=bar_template,
                          info_sep=info_sep, file=file, label=label,
                          width=width, color=color)


def get_fs_encoding():
    """
    Return the current filesystem encoding or default encoding
    """
    return sys.getfilesystemencoding() or sys.getdefaultencoding()


def path_as_unicode(path):
    """
    Return path as unicode.
    """
    if isinstance(path, unicode):
        return path
    try:
        return path.decode(get_fs_encoding())
    except UnicodeDecodeError:
        return as_unicode(path)


def get_relative_path(path, len_base_path, base_is_dir):
    """
    Return a posix relative path from the posix 'path' relative to a
    base path of `len_base_path` length where the base is a directory if
    `base_is_dir` True or a file otherwise.
    """
    path = path_as_unicode(path)
    if base_is_dir:
        rel_path = path[len_base_path:]
    else:
        rel_path = fileutils.file_name(path)

    return rel_path.lstrip('/')


def fixed_width_file_name(path, max_length=25):
    """
    Return a fixed width file name of at most `max_length` characters
    extracted from the `path` string and usable for fixed width display.
    If the file_name is longer than `max_length`, it is truncated in the
    middle with using three dots "..." as an ellipsis and the extension
    is kept.

    For example:
    >>> short = fixed_width_file_name('0123456789012345678901234.c')
    >>> assert '0123456789...5678901234.c' == short
    """
    if not path:
        return ''

    filename = fileutils.file_name(path)
    if len(filename) <= max_length:
        return filename
    base_name, extension = fileutils.splitext(filename)
    number_of_dots = 3
    len_extension = len(extension)
    remaining_length = max_length - len_extension - number_of_dots

    if remaining_length < (len_extension + number_of_dots) or remaining_length < 5:
        return ''

    prefix_and_suffix_length = abs(remaining_length // 2)
    prefix = base_name[:prefix_and_suffix_length]
    ellipsis = number_of_dots * '.'
    suffix = base_name[-prefix_and_suffix_length:]
    return "{prefix}{ellipsis}{suffix}{extension}".format(**locals())


def compute_fn_max_len(used_width=BAR_WIDTH + BAR_SEP_LEN + 7 + BAR_SEP_LEN + 8 + BAR_SEP_LEN):
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
    The space usage is therefore: BAR_WIDTH + BAR_SEP_LEN + 7 + BAR_SEP_LEN + 8 + BAR_SEP_LEN + the file name length
    """
    term_width, _height = click.get_terminal_size()
    max_filename_length = term_width - used_width
#     if term_width < 70:
#         # if we have a small term width that is less than 70 column, we
#         # may spill over and damage the progress bar...
#         max_filename_length = 10
    return max_filename_length
