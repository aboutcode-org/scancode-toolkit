# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
import os

import attr
import saneyaml
from commoncode.text import python_safe_name
from licensedcode.cache import get_spdx_symbols


@attr.s
class Test(object):
    location = attr.ib(None)
    filename = attr.ib(None)
    license_key = attr.ib(default=None)
    text = attr.ib(default=None)
    coverage = attr.ib(default=0)
    notes = attr.ib(default=None)


def collect_tests(location):

    for filename in os.listdir(location):
        if filename in ('README', 'ccurls.t1'):
            continue
        loc = os.path.join(location, filename)
        data = open(loc).read()
        header, _, text = data.partition('\n\n')

        expected_lic = None
        coverage = 0
        comments = []

        for line in header.splitlines(False):
            if line.startswith('#'):
                comments.append(line.strip('#'))
            elif line.endswith('%'):
                coverage = float(line.strip('%'))
            else:
                expected_lic, _, _ = line.partition(' ')
                expected_lic = expected_lic.strip()

        test = Test(
            location=loc,
            filename=filename,
            coverage=coverage,
            license_key=expected_lic,
            text=text,
            notes='\n'.join(c.strip() for c in comments),
        )

        yield test


def collect_url_tests(location):
    # the urls file 'ccurls.t1' is special
    ccurl = 'ccurls.t1'
    data = open(os.path.join(location, '..', ccurl)).read()
    lics, _, urls = data.partition('\n\n')

    lics = (e for e in lics.splitlines(False) if not e.endswith('%'))

    for i, lic in enumerate(lics):
        expected_lic, offsets, _ = lic.split()
        start, end = offsets.split(',')
        text = urls[int(start):int(end)]
        expected_lic = expected_lic.strip()
        fn = python_safe_name(expected_lic)

        yield Test(
            location=os.path.join(location, f'url_{fn}_{i}.txt'),
            filename=ccurl,
            text=text,
            license_key=expected_lic,
            notes='This is a URL test extracted from ccurls.t1.'
        )


# a bunh of non-spadx license keys
extra_license_keys = {
    'aladdin-9': 'afpl-9.0',
    'anti996': '996-icu-1.0',
    'bsd-1-clause-clear': 'unknown',
    'bsd-3-clause-notrademark': 'unknown',
    'commonsclause': 'unknown',
    'cc-by-nc-sa-3.0-us': 'unknown',
    'lgpl-2.0-or-3.0': 'unknown',
    'googlepatentclause': 'unknown',
    'googlepatentsfile': 'unknown',
    'mit-noad': 'unknown',
    'prosperity-3.0.0': 'unknown',
}


def generate_license_tests(location):

    # map their keys to ours
    license_mapping = {spdx: l.key for spdx, l in get_spdx_symbols().items()}
    license_mapping.update(extra_license_keys)

    for test in list(collect_tests(location)) + list(collect_url_tests(location)):
        loc = test.location

        print(f'Processing: {loc}')

        with open(loc, 'w') as txt:
            txt.write(test.text)

        lickey = test.license_key
        lickey = lickey and lickey.lower() or None
        lickey = license_mapping.get(lickey)
        lickey = lickey or 'unknown'

        url = f'https://raw.githubusercontent.com/google/licensecheck/v0.3.1/testdata/{test.filename}'
        with open(loc + '.yml', 'w') as td:
            data = dict(
                license_expressions=[lickey],
                notes=(
                    f'License test derived from a file of the BSD-licensed repository at:\n' +
                    f'{url}\n' +
                    f'originally expected to be detected as {test.license_key}\n' +
                    f'with coverage of {test.coverage}\n' +
                    (test.notes or '')
                )
            )
            td.write(saneyaml.dump(data))


if __name__ == '__main__':
    import sys
    generate_license_tests(sys.argv[1])

