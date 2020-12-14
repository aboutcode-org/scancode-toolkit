#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

import click

import release_utils


@click.command()

@click.option('--python-version',
    type=click.Choice(release_utils.PYTHON_VERSIONS),
    default='36',
    show_default=True,
    help='Python version to use for this build.',
)
@click.option('--platform',
    type=click.Choice(release_utils.PLATFORMS),
    default='linux',
    show_default=True,
    help='Platform to use for this build: one of linux, mac or windows.',
)
@click.option('--thirdparty-dir',
    type=click.Path(exists=True, readable=True, path_type=str, file_okay=False),
    default=release_utils.THIRDPARTY_DIR,
    help='Path to the thirdparty directory.',
)
@click.option('--links-url',
    type=str,
    metavar='URL',
    default=release_utils.LINKS_URL,
    show_default=True,
    help='URL of HTML page where to find links to packages and files. '
        'Can also point to a local file:/// directory',
)
@click.option('--requirement',
    type=click.Path(exists=True, readable=True, path_type=str, dir_okay=False),
    metavar='FILE',
    default='requirements.txt',
    show_default=True,
    help='Path to the requirements file to use for thirdparty packages.',
)
@click.option('--strict',
    is_flag=True,
    help='Fail if any ABOUT, license or notice is missing.',
)
@click.option('--include-source',
    is_flag=True,
    help='Also download source archives.',
)
@click.option('--use-pip',
    is_flag=True,
    help='Use "pip download" to download wheels and source distributions.',
)
@click.help_option('-h', '--help')
def fetch_deps(
    python_version,
    platform,
    thirdparty_dir,
    links_url,
    requirement,
    include_source=False,
    include_virtualenv=True,
    strict=False,
    use_pip=False,
):
    """
    Fetch all the dependencies found in the `--requirement` FILE requirements
    file only for the provided `--python-version` and `--platform`.

    Also fetch the corresponding ABOUT files and licenses.

    Save it all in the `--thirdparty-dir` DIRECTORY

    Use the `--links-url` URL to an HTML page containing the listing of all
    available archives and files to find the download URLs of each fetched file.

    The source distribution are fetched too with the `--include-source` option.
    And a virtualenv pyz app is always included.
    """
    fetch_thirparties(
        python_version=python_version,
        platform=platform,
        thirdparty_dir=thirdparty_dir,
        links_url=links_url,
        requirement=requirement,
        include_source=include_source,
        include_virtualenv=include_virtualenv,
        strict=strict,
        use_pip=use_pip,
    )


def fetch_thirparties(
    python_version,
    platform,
    thirdparty_dir,
    links_url,
    requirement,
    include_source=False,
    include_virtualenv=True,
    strict=False,
    use_pip=False,
):

    platforms = release_utils.PLATFORMS[platform]
    environment = release_utils.Environment.from_pyplat(python_version, platforms)

    paths_or_urls = release_utils.get_paths_or_urls(links_url)

    if use_pip:
        release_utils.fetch_dependencies_using_pip(
            environment=environment,
            requirement=requirement,
            dest_dir=thirdparty_dir,
            links_url=links_url,
        )

        if include_source:
            release_utils.fetch_dependency_sources_using_pip(
                requirement=requirement,
                dest_dir=thirdparty_dir,
                links_url=links_url
            )
    else:
        release_utils.fetch_dependencies(
            environment=environment,
            requirement=requirement,
            dest_dir=thirdparty_dir,
            paths_or_urls=paths_or_urls,
            include_source=include_source,
        )

    if include_virtualenv:
        virtualenv_pyz = 'virtualenv.pyz'
        release_utils.fetch_and_save_using_paths_or_urls(
            file_name=virtualenv_pyz,
            dest_dir=thirdparty_dir,
            paths_or_urls=paths_or_urls,
            as_text=False,
        )

    release_utils.fetch_abouts_and_licenses(
        dest_dir=thirdparty_dir,
        paths_or_urls=paths_or_urls,
        strict=strict,
    )


if __name__ == '__main__':
    fetch_deps()
