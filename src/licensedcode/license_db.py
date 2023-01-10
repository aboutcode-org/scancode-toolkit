# SPDX-License-Identifier: CC-BY-4.0 AND Apache-2.0
#
# https://github.com/nexB/scancode-licensedb
# Copyright 2020 nexB Inc. and others.
# ScanCode is a trademark of nexB Inc.
#
# ScanCode LicenseDB data is licensed under the Creative Commons Attribution
# License 4.0 (CC-BY-4.0).
# Some licenses, such as the GNU GENERAL PUBLIC LICENSE, are subject to other licenses.
# See the corresponding license text for the specific license conditions.
#
# ScanCode LicenseDB software is licensed under the Apache License version 2.0.
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# ScanCode LicenseDB is generated with ScanCode Toolkit. The database and its contents
# are provided on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.
# No content from ScanCode LicenseDB should be considered or used as legal advice.
# Consult an attorney for any legal advice.

import os
import json
import pathlib
from datetime import datetime
from os.path import dirname
from os.path import join
from distutils.dir_util import copy_tree

import saneyaml
from jinja2 import Environment, FileSystemLoader
from licensedcode.models import load_licenses
from licensedcode.models import licenses_data_dir
from scancode_config import __version__ as scancode_version


TEMPLATES_DIR = os.path.join(dirname(__file__), 'templates')
STATIC_DIR = os.path.join(dirname(__file__), 'static')


def write_file(path, filename, content):
    path.joinpath(filename).open("w").write(content)


def now():
    return datetime.now().strftime("%b %d, %Y")


base_context = {
    "scancode_version": scancode_version,
    "now": now(),
}


base_context_test = {
    "scancode_version": "32.0.0b1",
    "now": "Dec 22, 2022",
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
            "text": lic.text,
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
    if test:
        base_context_mapping = base_context_test
    else:
        base_context_mapping = base_context
    license_details_template = environment.get_template("license_details.html")
    for lic in licenses.values():
        license_data = lic.to_dict(include_text=True)
        html = license_details_template.render(
            **base_context_mapping,
            license=lic,
            license_data=license_data,
        )
        write_file(output_path, f"{lic.key}.html", html)
        write_file(
            output_path,
            f"{lic.key}.yml",
            saneyaml.dump(license_data, indent=2)
        )
        write_file(
            output_path,
            f"{lic.key}.json",
            json.dumps(license_data, indent=2, sort_keys=False)
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


def dump_license_data(ctx, param, value):
    """
    Dump license data from scancode licenses to the directory ``value`` passed
    in from command line.

    Dumps data in JSON, YAML and HTML formats and also dumps the .LICENSE file
    with the license text and the data as YAML frontmatter.
    """
    if not value or ctx.resilient_parsing:
        return

    import click
    click.secho(f'Dumping license data to: {value}', err=True)
    count = generate(build_location=value)
    click.secho(f'Done dumping #{count} licenses.', err=True)
    ctx.exit(0)
