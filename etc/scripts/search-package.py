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
    thirdparty = resource_iter(target, with_dirs=False)
    dependency = [
        files for files in thirdparty if fnmatch.fnmatchcase(files, package_name)
    ]
    if dependency:
        whl = [files for files in dependency if files.endswith('.whl')]
        ## There are multiple version of same package So list of wheel will be considered.
        sdist = [files for files in dependency if files.endswith('.tar.gz')]
        about = [files for files in dependency if files.endswith('.ABOUT')]
        notice = [files for files in dependency if files.endswith('.NOTICE')]
        license = [files for files in dependency if files.endswith('.LICENSE')]
        print('\nSearched package wheel are:')
        print(*whl, sep='\n')
        if sdist:
            print('\nCorresponding sdist are:')
            print(*sdist, sep='\n')
        else:
            print('\nCorresponding sdist does not exits in target')
        if about:
            print('\nCorresponding .ABOUT are:')
            print(*about, sep='\n')
        else:
            print('\nCorresponding .ABOUT does not exits in target\n')
        if license:
            print('\nCorresponding .LICENSE are:')
            print(*licence, sep='\n')
        else:
            print('\nCorresponding .LICENSE does not exits in target')
        if notice:
            print('\nCorresponding .NOTICE are:')
            print(*notice, sep='\n')
        else:
            print('\nCorresponding .NOTICE does not exits in target\n')
    else:
        print('\nSpecified package does not exist\n')


def main_with_args(args: str) -> None:
    parser = argparse.ArgumentParser(
        description="""Search PACKAGE_NAME (with an optional VERSION_OF_PACKAGE) in the
        TARGET_DIR directory.Print results on screen.
        """,
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

    package_name = args.package_name
    directory = args.directory
    version = args.version
    search_package(package_name, directory, version)


def main() -> None:
    main_with_args(sys.argv[1:])


if __name__ == '__main__':
    main()
