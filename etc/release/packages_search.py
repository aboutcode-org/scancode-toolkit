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

import argparse
import fnmatch
import sys

from commoncode.fileutils import resource_iter


def search_package(package_name, target, version=None):
    """
    Search `package_name` (with an optional `version`) in the `target` directory.
    Print results on screen.
    """

    if version:
        package_name = '*{}-{}*'.format(package_name, version)
    else:
        package_name = '*{}*'.format(package_name)

    target_files = resource_iter(target, with_dirs=False)

    package_files = [f for f in target_files if fnmatch.fnmatchcase(f, package_name)]

    print()
    if package_files :
        print('Found package files:')
        for package_file in package_files:
            print(package_file)
    else:
        print('Package does not exist')


def cli(args):
    parser = argparse.ArgumentParser(
        description=(
            'Search PACKAGE_NAME (with an optional VERSION_OF_PACKAGE) in the '
            'TARGET_DIR directory.Print results on screen.'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '--package_name',
        help='Name of the package to search in the TARGET_DIR directory',
        type=str,
        required=True,
    )

    parser.add_argument(
        '--directory',
        help='Directory to search for package wheels and tarballs. [default: thirdparty]',
        type=str,
        default='thirdparty',
    )

    parser.add_argument(
        '--version',
        help='Optional package version to search.',
        type=str,
        default=None,
    )

    args = parser.parse_args()

    search_package(
        package_name=args.package_name,
        directory=args.directory,
        version=args.version,
    )


if __name__ == '__main__':
    cli(sys.argv[1:])
