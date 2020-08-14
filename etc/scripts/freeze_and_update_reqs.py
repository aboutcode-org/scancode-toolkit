# -*- coding: utf-8 -*-
#
# Copyright nexB Inc. and others. All rights reserved.
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

import argparse
from fnmatch import fnmatchcase
import os
from shutil import copy
from subprocess import run
import sys
import tempfile

from commoncode.fileutils import resource_iter

python_version = str(sys.version_info[0]) + str(sys.version_info[1])
py_abi = '{0}cp{1}{0}'.format('*', python_version)


def generate_req_text(find_links, req_file, package_name=None, upgrade=False):
    """
    Generate a requirement file as `req_file` of all dependencies wheels and 
    sdists present at the find_links.If a `package_name` is provided it will 
    be updated to its latest version and if upgrade option is called,it will 
    be updated all the wheels to the latest version.
    """
    thirdparty = resource_iter(find_links, with_dirs=False)
    dependencies = [
        files
        for files in thirdparty
        if fnmatchcase(files, '*py3*')
        or fnmatchcase(files, py_abi)
        or (
            fnmatchcase(files, '*tar.gz*')
            and not fnmatchcase(files, '*py2-ipaddress-3.4.1.tar.gz*')
        )
    ]
    with tempfile.TemporaryDirectory() as temp_dir:
        for deps in dependencies:
            copy(deps, temp_dir)
        pip_args = [
            'pip-compile',
            '--generate-hashes',
            '--find-links',
            temp_dir,
            '--output-file',
            req_file,
            '--allow-unsafe',
            '--no-emit-find-links',
            '--pip-args',
            '--no-index',
        ]
        if upgrade:
            pip_args.append('--upgrade')
        if package_name:
            pip_args.extend(['--upgrade-package', package_name])
        run(pip_args)


def main_with_args(args: str) -> None:
    parser = argparse.ArgumentParser(
        description="""Generate a requirement file as `requirement` of all dependencies wheels and 
sdists present at the find_links.If a `upgrade-package` option is called it 
will update provided `package_name` to its latest version and if upgrade 
option is called,it will be update all the wheels/sdist to the latest version.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '--find-links',
        help='Required: Look for archives in this directory or on this HTML page',
        type=str,
        required=True,
    )

    parser.add_argument(
        '--requirement',
        help='Required: Requirement file name.',
        type=str,
        required=True,
    )

    parser.add_argument(
        '--upgrade',
        help='Optional: Try to upgrade all dependencies to their latest versions',
        action='store_true',
    )

    parser.add_argument(
        '--upgrade-package',
        help='Optional: Specify particular packages to upgrade.',
        type=str,
        default=None,
    )

    args = parser.parse_args()

    find_links = args.find_links
    requirement = args.requirement
    upgrade_package = args.upgrade_package or None
    upgrade = args.upgrade or False
    generate_req_text(
        find_links=find_links,
        req_file=requirement,
        package_name=upgrade_package,
        upgrade=upgrade,
    )


def main() -> None:
    main_with_args(sys.argv[1:])


if __name__ == '__main__':
    main()
