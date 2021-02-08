#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import sys


def rename_archives(target_directory, suffix):
    """
    Rename all the archives found in the `target_directory` to include a
    distinguishing `suffix` in their file names (typically a python version and
    operating system name).

    For example, if `target_directory` contains "foo.tar.gz" initially, with the
    suffix="_py36-macos", then "foo.tar.gz" will be renamed to "foo_py36-macos.tar.gz"
    """
    supported_extensions = '.tar.gz', '.tar.bz2', '.zip', '.tar.xz',
    renameable = [
        fn for fn in os.listdir(target_directory)
        if fn.endswith(supported_extensions)
    ]
    for old_name in renameable:
        if old_name.endswith('.zip'):
            name, extension, _ = old_name.rpartition('.zip')
        else:
            # all the tar.xx
            name, extension, compression = old_name.rpartition('.tar')
            extension = extension + compression

        # do not rename twice
        if name.endswith(suffix):
            return

        os.rename(
            os.path.join(target_directory, old_name),
            os.path.join(target_directory, f'{name}{suffix}{extension}'),
        )


if __name__ == '__main__':
    args = sys.argv[1:]
    target_directory, suffix = args
    rename_archives(target_directory=target_directory, suffix=suffix)
