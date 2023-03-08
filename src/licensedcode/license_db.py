#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import json
import pathlib
from datetime import datetime
from os.path import dirname
from os.path import join
from distutils.dir_util import copy_tree

import click
import saneyaml

from commoncode.cliutils import MISC_GROUP
from commoncode.cliutils import PluggableCommandLineOption
from jinja2 import Environment, FileSystemLoader
from licensedcode.models import load_licenses
from licensedcode.models import licenses_data_dir
from scancode_config import __version__ as scancode_version
from scancode_config import spdx_license_list_version

TEMPLATES_DIR = os.path.join(dirname(__file__), 'templates')
STATIC_DIR = os.path.join(dirname(__file__), 'static')


def write_file(path, filename, content):
    path.joinpath(filename).open("w").write(content)


def now():
    return datetime.utcnow().strftime('%Y-%m-%d')

base_context = {
    "scancode_version": scancode_version,
    "now": now(),
    "spdx_license_list_version": spdx_license_list_version,
}


base_context_test = {
    "scancode_version": "32.0.0b1",
    "now": "Dec 22, 2022",
    "spdx_license_list_version": "3.20",
}


def generate_indexes(output_path, environment, licenses, test=False):
    """
    Generates the license index and the static website at ``output_path``.

    ``environment`` is a jinja Environment object used to generate the webpage
    and ``licenses`` is a mapping with scancode license data.
    """
    if test:
        base_context_mapping = base_context_test
    else:
        base_context_mapping = base_context
    static_dest_dir = join(output_path, 'static')
    if not os.path.exists(static_dest_dir):
        os.makedirs(static_dest_dir)

    copy_tree(STATIC_DIR, static_dest_dir)

    license_list_template = environment.get_template("license_list.html")
    index_html = license_list_template.render(
        **base_context_mapping,
        licenses=licenses,
    )
    write_file(output_path, "index.html", index_html)

    index = [
        {
            "license_key": key,
            "category": lic.category,
            "spdx_license_key": lic.spdx_license_key,
            "other_spdx_license_keys": lic.other_spdx_license_keys,
            "is_exception": lic.is_exception,
            "is_deprecated": lic.is_deprecated,
            "json": f"{key}.json",
            "yaml": f"{key}.yml",
            "html": f"{key}.html",
            "license": f"{key}.LICENSE",
        }
        for key, lic in licenses.items()
    ]

    write_file(
        output_path,
        "index.json",
        json.dumps(index, indent=2, sort_keys=False)
    )
    write_file(
        output_path,
        "index.yml",
        saneyaml.dump(index, indent=2)
    )
    return len(index)


def generate_details(output_path, environment, licenses, test=False):
    """
    Dumps data at ``output_path`` in JSON, YAML and HTML formats and also dumps
    the .LICENSE file with the license text and the data as YAML frontmatter.

    ``environment`` is a jinja Environment object used to generate the webpage
    and ``licenses`` is a mapping with scancode license data.

    ``test`` is to generate a stable output for testing only
    """
    from licensedcode.cache import get_cache
    include_builtin = get_cache().has_additional_licenses

    if test:
        base_context_mapping = base_context_test
    else:
        base_context_mapping = base_context
    license_details_template = environment.get_template("license_details.html")
    for lic in licenses.values():
        license_data = lic.to_dict(include_text=False, include_builtin=include_builtin)
        license_data_with_text = lic.to_dict(include_text=True, include_builtin=include_builtin)
        html = license_details_template.render(
            **base_context_mapping,
            license=lic,
            license_data=license_data,
        )
        write_file(output_path, f"{lic.key}.html", html)
        write_file(
            output_path,
            f"{lic.key}.yml",
            saneyaml.dump(license_data_with_text, indent=2)
        )
        write_file(
            output_path,
            f"{lic.key}.json",
            json.dumps(license_data_with_text, indent=2, sort_keys=False)
        )
        lic.dump(output_path)


def generate_help(output_path, environment, test=False):
    """
    Generate a help.html with help text at ``output_path`` ``environment`` is a
    jinja Environment object used to generate the webpage. ``test`` is to
    generate a stable output for testing only
    """
    if test:
        base_context_mapping = base_context_test
    else:
        base_context_mapping = base_context
    template = environment.get_template("help.html")
    html = template.render(**base_context_mapping)
    write_file(output_path, "help.html", html)


def generate(
    build_location,
    template_dir=TEMPLATES_DIR,
    licenses_data_dir=licenses_data_dir,
    test=False,
):
    """
    Generate a licenseDB static website and dump license data at
    ``build_location`` given a license directory ``licenses_data_dir`` using
    templates from ``template_dir``. ``test`` is to generate a stable output for
    testing only
    """

    if not os.path.exists(build_location):
        os.makedirs(build_location)

    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=True,
    )
    licenses = dict(sorted(
        load_licenses(licenses_data_dir=licenses_data_dir, with_deprecated=True).items()
    ))

    root_path = pathlib.Path(build_location)
    root_path.mkdir(parents=False, exist_ok=True)

    count = generate_indexes(output_path=root_path, environment=env, licenses=licenses, test=test)
    generate_details(output_path=root_path, environment=env, licenses=licenses, test=test)
    generate_help(output_path=root_path, environment=env, test=test)
    return count


def scancode_license_data(path):
    """
    Dump license data from scancode licenses to the directory ``path`` passed
    in from command line.

    Dumps data in JSON, YAML and HTML formats and also dumps the .LICENSE file
    with the license text and the data as YAML frontmatter.
    """
    click.secho(f'Dumping license data to: {path}', err=True)
    count = generate(build_location=path)
    click.secho(f'Done dumping #{count} licenses.', err=True)


@click.command(name='scancode-license-data')
@click.option(
    '--path',
    type=click.Path(exists=False, writable=True, file_okay=False, resolve_path=True, path_type=str),
    metavar='DIR',
    help='Dump the license data in this directory in the LicenseDB format and exit. '
            'Creates the directory if it does not exist. ',
    help_group=MISC_GROUP,
    cls=PluggableCommandLineOption,
)
@click.help_option('-h', '--help')
def dump_scancode_license_data(
    path,
    *args,
    **kwargs,
):
    """
    Dump scancode license data in various formats, and the licenseDB static website at `path`.
    """
    scancode_license_data(path=path)


if __name__ == '__main__':
    dump_scancode_license_data()
