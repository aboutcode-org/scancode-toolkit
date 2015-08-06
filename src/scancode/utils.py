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
from click._compat import _default_text_stdout
from click._compat import isatty
from click.utils import echo
from click._compat import PY2


class BaseCommand(click.Command):
    # override with a command-specific message such as
    #Try 'scancode --help' for help on options and arguments.
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



"""
ProgressLogger is derived from Click progressbar code.
Copyright (c) 2014 by Armin Ronacher.
Some rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above
      copyright notice, this list of conditions and the following
      disclaimer in the documentation and/or other materials provided
      with the distribution.

    * The names of the contributors may not be used to endorse or
      promote products derived from this software without specific
      prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    :copyright: (c) 2014 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.

"""

def progresslogger(iterable, label_first=None, label_last=None,
                   item_show_func=None, file=None, color=None):  # @ReservedAssignment
    """This function creates an iterable context manager that can be used
    to iterate over something while showing a progress log. While iteration
    happens, this function will print a progress log to the given `file`
    (defaults to stdout). By default, this progress log will not be rendered if
    the file is not a terminal.

    The context manager creates the progress log.  When the context manager is
    entered the progress log is already displayed.  With every iteration over
    the progress log, the iterable passed to the logger is advanced and the log
    is updated.  When the context manager exits, a newline is printed and the
    progress log is finalized on screen.

    No printing must happen or the progress bar will be unintentionally
    destroyed.

    Example usage::

        with progresslog(items) as bar:
            for item in bar:
                do_something_with(item)

    :param iterable: an iterable to iterate over.
    :param label_first: the label to show as the first line of the progress log.
    :param label_last: the label to show as the last line of the progress log.
    :param item_show_func: a function called with the current item which
                           can return a string to show the current item
                           in the progress log.  Note that the current
                           item can be `None`!
    :param file: the file to write to.  If this is not a terminal then
                 only the label_first is printed.
    :param color: controls if the terminal supports ANSI colors or not.  The
                  default is autodetection.  This is only needed if ANSI
                  codes are included anywhere in the progress log output
                  which is not the case by default.
    """
    return ProgressLogger(iterable=iterable, label_first=label_first,
                          label=label_last, item_show_func=item_show_func,
                          file=file, color=color)


class ProgressLogger(object):
    def __init__(self, iterable, label_first=None, label_last=None,
                 item_show_func=None, file=None, color=None):  # @ReservedAssignment
        self.iter = iter(iterable)

        self.label_first = label_first or ''
        self.label_last = label_last or ''
        self.item_show_func = item_show_func
        if file is None:
            file = _default_text_stdout()  # @ReservedAssignment
        self.file = file
        self.color = color

        self.finished = False
        self.entered = False
        self.current_item = None
        self.is_hidden = not isatty(self.file)

    def __enter__(self):
        self.render_log()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.render_log()

    def __iter__(self):
        if not self.entered:
            raise RuntimeError('You need to use progress loggers in a with block.')
        self.render_log()
        return self

    def render_log(self):
        if self.is_hidden:
            return

        if self.entered and not self.current_item:
            self.file.write('\n')
            msg = self.label_first
        elif self.finished:
            msg = self.label_last
        else:
            if self.item_show_func is not None:
                msg = self.item_show_func(self.current_item)
            else:
                # this needs to be something printable
                msg = repr(self.current_item)
        echo(msg.rstrip(), file=self.file, nl=True, color=self.color)
        self.file.flush()

    def update(self):
        self.render_log()

    def next(self):
        if self.is_hidden:
            return next(self.iter)
        try:
            rv = next(self.iter)
            self.current_item = rv
        except StopIteration:
            self.finish()
            self.render_log()
            raise StopIteration()
        else:
            self.update()
            return rv

    if not PY2:
        __next__ = next
        del next
