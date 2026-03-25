#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
#

import os
import pytest

from packagedcode.publiccode import PubliccodeYmlHandler

TESTDATA_DIR = os.path.join(os.path.dirname(__file__), 'data', 'publiccode')


def test_publiccode_yml_basic():
    location = os.path.join(TESTDATA_DIR, 'publiccode.yml')
    packages = list(PubliccodeYmlHandler.parse(location))
    assert len(packages) == 1
    pkg = packages[0]

    assert pkg.name == 'Medusa'
    assert pkg.version == '1.0.3'
    assert pkg.vcs_url == 'https://example.com/italia/medusa.git'
    assert pkg.homepage_url == 'https://example.com/medusa'
    assert pkg.declared_license_expression == 'AGPL-3.0-or-later'
    assert pkg.copyright == 'City of Example'
    assert 'financial-reporting' in pkg.keywords
    assert len(pkg.parties) == 1
    assert pkg.parties[0].name == 'Francesco Rossi'
    assert pkg.parties[0].email == 'f.rossi@example.com'
    assert pkg.parties[0].role == 'maintainer'


def test_publiccode_yml_no_version_key_returns_nothing(tmp_path):
    """A YAML file without publiccodeYmlVersion should yield nothing."""
    f = tmp_path / 'publiccode.yml'
    f.write_text('name: something\nversion: 1.0\n')
    packages = list(PubliccodeYmlHandler.parse(str(f)))
    assert packages == []


def test_publiccode_yml_path_patterns():
    assert PubliccodeYmlHandler.path_patterns == (
        '*/publiccode.yml',
        '*/publiccode.yaml',
    )
