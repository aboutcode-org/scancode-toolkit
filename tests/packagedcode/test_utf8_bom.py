#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import pytest

from packagedcode import bower
from packagedcode import haxe
from packagedcode import npm
from packagedcode import phpcomposer


BOM = '﻿'

MANIFESTS = [
    (npm.NpmPackageJsonHandler, 'package.json',
     '{"name": "demo", "version": "1.0.0", "license": "MIT"}'),
    (bower.BowerJsonHandler, 'bower.json',
     '{"name": "demo", "version": "1.0.0", "license": "MIT"}'),
    (phpcomposer.PhpComposerJsonHandler, 'composer.json',
     '{"name": "acme/demo", "version": "1.0.0", "license": "MIT"}'),
    (haxe.HaxelibJsonHandler, 'haxelib.json',
     '{"name": "demo", "version": "1.0.0", "license": "MIT"}'),
]


@pytest.mark.parametrize(
    'handler, filename, content',
    MANIFESTS,
    ids=[filename for _, filename, _ in MANIFESTS],
)
def test_manifest_with_a_utf8_bom_is_parsed(handler, filename, content, tmp_path):
    """A BOM is legal in a package manifest and package managers accept one.

    Python's utf-8 codec does not consume it, it decodes the three bytes to
    U+FEFF and json.load then raises, so the whole package used to disappear
    from the scan.
    """
    location = tmp_path / filename
    location.write_text(BOM + content, encoding='utf-8')

    packages = list(handler.parse(location=str(location)))

    assert [(p.name, p.version) for p in packages] == [('demo', '1.0.0')]


@pytest.mark.parametrize(
    'handler, filename, content',
    MANIFESTS,
    ids=[filename for _, filename, _ in MANIFESTS],
)
def test_manifest_without_a_bom_is_unaffected(handler, filename, content, tmp_path):
    location = tmp_path / filename
    location.write_text(content, encoding='utf-8')

    packages = list(handler.parse(location=str(location)))

    assert [(p.name, p.version) for p in packages] == [('demo', '1.0.0')]
