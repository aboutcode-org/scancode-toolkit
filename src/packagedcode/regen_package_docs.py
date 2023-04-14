#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import pathlib
from os.path import dirname

import click

from commoncode.cliutils import MISC_GROUP
from commoncode.cliutils import PluggableCommandLineOption
from packagedcode.plugin_package import get_available_package_parsers
from jinja2 import Environment, FileSystemLoader


TEMPLATES_DIR = os.path.join(dirname(__file__), 'templates')

def write_file(file_path, content):
    file_path.open("w").write(content)


def regenerate(
    doc_location,
    template_dir=TEMPLATES_DIR,
):
    """
    Generate a licenseDB static website and dump license data at
    ``build_location`` given a license directory ``licenses_data_dir`` using
    templates from ``template_dir``. ``test`` is to generate a stable output for
    testing only
    """
    environment = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=True,
    )
    doc_path = pathlib.Path(doc_location)

    all_available_packages = get_available_package_parsers(docs=True)

    license_list_template = environment.get_template("available_package_parsers.rst")
    packages_doc = license_list_template.render(
        all_available_packages=all_available_packages,
    )
    write_file(file_path=doc_path, content=packages_doc)



@click.command(name='regen-package-docs')
@click.option(
    '--path',
    type=click.Path(exists=True, writable=True, file_okay=True, dir_okay=False, path_type=str),
    metavar='FILE',
    help='Regenerate a reStructuredText documentation page from scancode available package parsers data.',
    help_group=MISC_GROUP,
    cls=PluggableCommandLineOption,
)
@click.help_option('-h', '--help')
def regen_package_docs(
    path,
    *args,
    **kwargs,
):
    """
    Regenerate the scancode available packages documentation at `path`.
    """
    click.secho(f'Regenerating package docs at: {path}', err=True)
    regenerate(doc_location=path)
    click.secho(f'Documentation regeneration done.', err=True)


if __name__ == '__main__':
    regen_package_docs()
