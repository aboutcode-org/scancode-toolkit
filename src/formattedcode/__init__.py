#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
from itertools import chain

import click


class FileOptionType(click.File):
    """
    A click.File subclass that ensures that a file name is not set to an
    existing option parameter to avoid mistakes.
    """

    def convert(self, value, param, ctx):
        known_opts = set(chain.from_iterable(
            p.opts for p in ctx.command.params if isinstance(p, click.Option)))
        if value in known_opts:
            self.fail(
                'Illegal file name conflicting with an option name: '
                f'{os.fsdecode(value)!r}. '
                'Use the special "-" file name to print results on screen/stdout.',
                param,
                ctx,
            )

        try:
            validate_output_file_path(location=value)
        except Exception as e:
            self.fail(str(e), param, ctx)

        return click.File.convert(self, value, param, ctx)


class InvalidScanCodeOutputFileError(Exception):
    pass


def validate_output_file_path(location):
    """
    Raise an InvalidScanCodeOutputFileError if the output file is invalid.
    """
    if location != "-":
        from pathlib import Path
        from commoncode.filetype import is_writable

        path = Path(location)

        if path.is_dir():
            raise InvalidScanCodeOutputFileError(
                f'output file is a directory, not a file: {os.fsdecode(location)!r}',
            )

        if path.is_fifo() or path.is_socket() or path.is_block_device() or path.is_char_device():
            raise InvalidScanCodeOutputFileError(
                f'output file cannot be a special/char/device/fifo/pipe file: {os.fsdecode(location)!r}',
            )

        if path.exists():
            if not path.is_file():
                raise InvalidScanCodeOutputFileError(
                    f'output file exists and is not a file: {os.fsdecode(location)!r}',
                )
            if not is_writable(location):
                raise InvalidScanCodeOutputFileError(
                    f'output file exists and is not writable: {os.fsdecode(location)!r}',
                )

        else:
            parent = path.parent
            if not parent.exists() or not parent.is_dir():
                raise InvalidScanCodeOutputFileError(
                    f'output file parent is not a directory or does not exists: {os.fsdecode(location)!r}',
                )

            if not is_writable(str(parent)):
                raise InvalidScanCodeOutputFileError(
                    f'output file parent is not a writable directory: {os.fsdecode(location)!r}',
                )
