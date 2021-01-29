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


def rename_archives(target_directory, python_version, operating_system):
    """
    Rename all the archives found in the `target_directory` to include a
    python_version and operating_system name in their file names.

    For example, if `target_directory` contains "foo.tar.gz" initially, and the
    python_version="36 and operating_system="macos", then  "foo.tar.gz" will be
    renamed to "foo-py36-macos.tar.gz"
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

        pyos = f'py{python_version}-{operating_system}'
        new_name = f'{name}-{pyos}{extension}'

        # do not rename twice
        if not name.endswith(pyos):
            os.rename(
                os.path.join(target_directory, old_name),
                os.path.join(target_directory, new_name),
            )


if __name__ == '__main__':
    args = sys.argv[1:]
    target_directory, python_version, operating_system = args
    rename_archives(target_directory, python_version, operating_system)
