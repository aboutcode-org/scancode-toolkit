#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#
# Visit https://aboutcode.org and https://github.com/nexB/scancode-toolkit for
# support and download. ScanCode is a trademark of nexB Inc.
#
# The ScanCode software is licensed under the Apache License version 2.0.
# The ScanCode open data is licensed under CC-BY-4.0.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
