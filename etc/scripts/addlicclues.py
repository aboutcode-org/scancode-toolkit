# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
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

from os import path

import click
click.disable_unicode_literals_warning = True

from cluecode.copyrights import detect_copyrights
from cluecode.finder import find_urls
from cluecode.finder import find_emails
from licensedcode import cache
from licensedcode import models


"""
Update licenses and rules with ignorable copyrights, URLs and emails.
"""

def copyright_detector(location):
    """
    Return sets of detected copyrights and authors in file at location.
    """
    copyrights = set()
    authors = set()
    for dtype, value, _start, _end in detect_copyrights(location):
        if dtype == 'copyrights':
            copyrights.add(value)
        elif dtype == 'authors':
            authors.add(value)

    return copyrights, authors


def update_ignorables(licensish):
    location = licensish.text_file
    print('Processing:', 'file://' + location)
    if not path.exists(location):
        print('!')
        return licensish
    copyrights, authors = copyright_detector(location)

    copyrights.update(licensish.ignorable_copyrights)
    licensish.ignorable_copyrights = sorted(copyrights)

    authors.update(licensish.ignorable_authors)
    licensish.ignorable_authors = sorted(authors)

    urls = set(u for (u, _ln) in find_urls(location) if u)
    urls.update(licensish.ignorable_urls)
    licensish.ignorable_urls = sorted(urls)

    emails = set(u for (u, _ln) in find_emails(location) if u)
    emails.update(licensish.ignorable_emails)
    licensish.ignorable_emails = sorted(emails)

    return licensish


@click.command()
@click.help_option('-h', '--help')
def cli(update=True):
    """
    Update licenses and rules with ignorable copyrights, URLs and emails.
    """
    for lic in cache.get_licenses_db().values():
        print('.', end='')
        if update:
            lic = update_ignorables(lic)
        lic.dump()

    for rule in models.load_rules():
        print('.', end='')
        if update:
            rule = update_ignorables(rule)
        rule.dump()


if __name__ == '__main__':
    cli()
