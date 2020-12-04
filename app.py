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
#
# Visit https://github.com/nexB/scancode-licensedb for support.
#
# ScanCode Toolkit is a free Software Composition Analysis tool from nexB Inc. and
# others.
# Visit https://github.com/nexB/scancode-toolkit for support and download.

import json
import pathlib
from datetime import datetime

import saneyaml
from jinja2 import Environment, PackageLoader
from licensedcode.models import load_licenses
from scancode_config import __version__ as scancode_version

licenses = load_licenses(with_deprecated=True)

# GitHub Pages support only /(root) or docs/ for the source
BUILD_LOCATION = "docs"

env = Environment(
    loader=PackageLoader("app", "templates"),
    autoescape=True,
)


def write_file(path, filename, content):
    path.joinpath(filename).open("w").write(content)


def now():
    return datetime.now().strftime("%b %d, %Y")


base_context = {
    "scancode_version": scancode_version,
    "now": now(),
}


def generate_indexes(output_path):
    license_list_template = env.get_template("license_list.html")
    index_html = license_list_template.render(
        **base_context,
        licenses=licenses,
    )
    write_file(output_path, "index.html", index_html)

    index = [
        {
            "license_key": key,
            "json": f"{key}.json",
            "yml": f"{key}.yml",
            "html": f"{key}.html",
            "text": f"{key}.LICENSE",
        }
        for key in licenses.keys()
    ]
    write_file(output_path, "index.json", json.dumps(index))
    write_file(output_path, "index.yml", saneyaml.dump(index))


def generate_details(output_path):
    license_details_template = env.get_template("license_details.html")
    for license in licenses.values():
        license_data = license.to_dict()
        yml = saneyaml.dump(license_data)
        html = license_details_template.render(
            **base_context,
            license=license,
            license_data=yml,
        )
        write_file(output_path, f"{license.key}.html", html)
        write_file(output_path, f"{license.key}.yml", yml)
        write_file(output_path, f"{license.key}.json", json.dumps(license_data))
        write_file(output_path, f"{license.key}.LICENSE", license.text)


def generate_help(output_path):
    template = env.get_template("help.html")
    html = template.render(**base_context)
    write_file(output_path, "help.html", html)


def generate():
    root_path = pathlib.Path(BUILD_LOCATION)
    root_path.mkdir(parents=False, exist_ok=True)

    generate_indexes(root_path)
    generate_details(root_path)
    generate_help(root_path)


if __name__ == "__main__":
    generate()
