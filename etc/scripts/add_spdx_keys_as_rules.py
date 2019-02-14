# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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
from __future__ import unicode_literals
from __future__ import print_function

import os.path

import click
click.disable_unicode_literals_warning = True

import synclic

from licensedcode.models import load_licenses
from licensedcode.models import Rule
from licensedcode.models import rules_data_dir


def is_matched(text, license_key):
    """
    Return True if the `text` string is matched exactly and entirely as a license with license_key.
    """
    from licensedcode.cache import get_index
    idx = get_index()

    matches = list(idx.match(query_string=text))
    if not matches:
#         click.echo('No match for '+ text)
        return False

    if len(matches) != 1:
        click.echo('Multiple matches for ' + text)
        for match in matches:
            click.echo(repr(match))
        return False

    match = matches[0]

    click.echo('One match for ' + text)
    click.echo(repr(match))

    matched_key = match.rule.license_expression

    if (match.matcher == '1-hash'
        and license_key == matched_key):
        return True


def add_rule(spdx_text, license_obj):
    """
    Add a new rule with text `spdx_text` for the `license_obj` License.
    """
    rule_base_name = 'spdx_license_id_' + spdx_text.lower() + '_for_' + license_obj.key
    text_file = os.path.join(rules_data_dir, rule_base_name + '.RULE')
    data_file = os.path.join(rules_data_dir, rule_base_name + '.yml')
    if os.path.exists(text_file) or os.path.exists(data_file):
        raise Exception('Cannot create new SPDX rules text file for {text}. '
                        'File already exists at: {text_file}'.format(**locals()))

    with open(text_file, 'wb') as tf:
        tf.write(spdx_text)

    rule = Rule(
        text_file=text_file,
        license_expression=license_obj.key,
        relevance=80,
        minimum_coverage=100,
        notes='Used to detect a bare SPDX license id',
    )
    rule.data_file = data_file
    rule.dump()
    click.echo('Added new rule: ' + repr(rule))


# these key would create too many false positives if added. We ignore these
very_common_ids = set([
    'aal',
    'abstyles',
    'adsl',
    'afmparse',
    'aladdin',
    'aml',
    'ampas',
    'apache-1.0',
    'bahyph',
    'barr',
    'borceux',
    'bsl-1.0',
    'bzip2-1.0.5',
    'bzip2-1.0.6',
    'caldera',
    'crossword',
    'crystalstacker',
    'cube',
    'curl',
    'diffmark',
    'divpdfm',
    'doc',
    'dotseqn',
    'dsdp',
    'egenix',
    'entessa',
    'eurosym',
    'fair',
    'freeimage',
    'ftl',
    'gl2ps',
    'gnuplot',
    'haskellreport',
    'hpnd',
    'ibm-pibs',
    'icu',
    'ijg',
    'imagemagick',
    'imatix',
    'info-zip',
    'intel',
    'intel-acpi',
    'interbase-1.0',
    'ipa',
    'isc',
    'jasper-2.0',
    'json',
    'latex2e',
    'leptonica',
    'libpng',
    'libtiff',
    'linux-openib',
    'llvm-exception',
    'lzma-exception',
    'makeindex',
    'miros',
    'mit',
    'mpich2'
    'mtll',
    'multics',
    'mup',
    'naumen',
    'ncsa',
    'netcdf',
    'net-snmp',
    'newletr',
    'ngpl',
    'nlpl',
    'nokia',
    'nrl',
    'ntp',
    'nunit',
    'oml',
    'openssl',
    'php-3.0',
    'php-3.01',
    'plexus',
    'postgresql',
    'psfrag',
    'psutils',
    'python-2.0',
    'qhull',
    'rdisc',
    'rsa-md',
    'rscpl',
    'ruby',
    'saxpath',
    'scea',
    'sendmail',
    'sleepycat',
    'smlnj',
    'smppl',
    'snia',
    'swl',
    'tcl',
    'tcp-wrappers',
    'tmate',
    'tosl',
    'vim',
    'vostrom',
    'w3c',
    'wsuipa',
    'wxwindows',
    'x11',
    'xerox',
    'xinetd',
    'xnet',
    'xpp',
    'xskat',
    'zed',
    'zend-2.0',
    'zlib',
])


@click.command()
@click.help_option('-h', '--help')
def add_spdx_key_rules():
    """
    Check that every known SPDX license key is properly detected exactly by a license rule.
    If not, create a new rule

    """
    by_key = load_licenses(with_deprecated=True)
    by_spdx_key = synclic.get_licenses_by_spdx_key(by_key.values(), include_other=True)

    click.echo('Checking all SPDX ids.')
    # first accumulate non-matches
    unmatched_licenses = {}
    for spdx_key, license_obj in sorted(by_spdx_key.items()):
#         click.echo('.', nl=False)

        if spdx_key in very_common_ids:
            continue

        if is_matched(spdx_key, license_obj.key):
            continue

        unmatched_licenses[spdx_key] = license_obj

    click.echo('')
    click.echo('{} SPDX ids not matched.'.format(len(unmatched_licenses)))

    # then create all rules at once
    for spdx_key, license_obj in sorted(unmatched_licenses.items()):
        add_rule(spdx_key, license_obj)


if __name__ == '__main__':
    add_spdx_key_rules()
