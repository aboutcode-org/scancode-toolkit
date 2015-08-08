#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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

from __future__ import print_function, absolute_import


import codecs
from collections import OrderedDict
from collections import defaultdict
from itertools import chain
import logging
import os
from os.path import exists
from os.path import join

from licensedcode import saneyaml

from commoncode import fileutils
from licensedcode import licenses_data_dir, rules_data_dir
from licensedcode import index
from textcode import analysis


"""
Model objects for license and rule persisted as YAML and text files.
"""

logger = logging.getLogger(__name__)
# import sys
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# logger.setLevel(logging.DEBUG)


# special magic key for rules pointing to non-license text
not_a_license_key = 'not-a-license'

class License(object):
    """
    A license consists of these files, where <key> is the license key:
        - <key>.yml : the license data in YAML
        - <key>.LICENSE: the license text
        - <key>.SPDX: the SPDX license text
    """
    def __init__(self, key=None, src_dir=licenses_data_dir):
        # unique key: lower case ASCII characters, digits, underscore and dots.
        self.key = key or ''
        self.src_dir = src_dir

        # commonly used short name, often abbreviated.
        self.short_name = ''
        # full name.
        self.name = ''

        # Attribution, Copyleft, etc
        self.category = ''

        self.owner = ''
        self.homepage_url = ''
        self.notes = ''

        self.spdx_license_key = ''
        self.spdx_full_name = ''
        self.spdx_url = ''
        self.spdx_notes = ''

        self.text_urls = []
        self.osi_url = ''
        self.faq_url = ''
        self.other_urls = []

        self.data_file = join(self.src_dir, self.key + '.yml')
        self.text_file = join(self.src_dir, self.key + '.LICENSE')
        self.spdx_file = join(self.src_dir, self.key + '.SPDX')

        if src_dir:
            self.load(src_dir)

    @property
    def text(self):
        """
        License text, re-loaded on demand.
        """
        return self._read_text(self.text_file)

    @property
    def spdx_license_text(self):
        """
        SPDX license text, re-loaded on demand.
        """
        if self.spdx_license_key:
            return self._read_text(self.spdx_file)
        else:
            return u''

    def asdict(self):
        """
        Return an OrderedDict of license data (excluding texts).
        Empty values are not included.
        """
        data = OrderedDict()

        data['key'] = self.key
        if self.short_name:
            data['short_name'] = self.short_name
        if self.name:
            data['name'] = self.name

        data['category'] = self.category

        if self.owner:
            data['owner'] = self.owner
        if self.homepage_url:
            data['homepage_url'] = self.homepage_url
        if self.notes:
            data['notes'] = self.notes

        if self.spdx_license_key:
            data['spdx_license_key'] = self.spdx_license_key
            data['spdx_full_name'] = self.spdx_full_name
            data['spdx_url'] = self.spdx_url
            if self.spdx_notes:
                data['spdx_notes'] = self.spdx_notes

        if self.text_urls:
            data['text_urls'] = self.text_urls
        if self.osi_url:
            data['osi_url'] = self.osi_url
        if self.faq_url:
            data['faq_url'] = self.faq_url
        if self.other_urls:
            data['other_urls'] = self.other_urls
        return data

    def dump(self):
        """
        Dump a representation of self as multiple files named
        this way:
         - <key>.yml : the license data in YAML
         - <key>.LICENSE: the license text
         - <key>.SPDX: the SPDX license text
        """
        as_yaml = saneyaml.dump(self.asdict())
        self._write(self.data_file, as_yaml)
        if self.text:
            self._write(self.text_file, self.text)
        if self.spdx_license_text:
            self._write(self.spdx_file, self.spdx_license_text)

    def _write(self, f, d):
        with codecs.open(f, 'wb', encoding='utf-8') as of:
            of.write(d)

    def load(self, src_dir):
        """
        Populate license data from a YAML file stored in of src_dir.
        Does not load text files.
        """
        with codecs.open(join(src_dir, self.data_file), encoding='utf-8') as f:
            data = f.read()
        for k, v in saneyaml.load(data).items():
            setattr(self, k, v)

    def _read_text(self, location):
        if not exists(location):
            text = u''
        else:
            with codecs.open(location, encoding='utf-8') as f:
                text = f.read()
        return text


# cache license objects in a map by license key
_LICENSES_BY_KEY = {}


def get_licenses_by_key():
    """
    Return a mapping of license key -> license object.
    """
    global _LICENSES_BY_KEY
    if not _LICENSES_BY_KEY :
        _LICENSES_BY_KEY = load_licenses()
    return _LICENSES_BY_KEY


def get_license(key):
    """
    Return a license object for this key.
    Raise a KeyError if the license does not exists.
    """
    return get_licenses_by_key()[key]


def load_licenses(license_dir=licenses_data_dir):
    """
    Return a mapping of key -> license objects, loaded from license files.
    """
    licenses = {}

    # TODO: add check for unknown files
    for top, _, files in os.walk(license_dir):
        for yfile in files:
            if not yfile.endswith('.yml'):
                continue
            key = yfile.replace('.yml', '')
            yfile = join(top, yfile)
            src_dir = os.path.dirname(yfile)
            licenses[key] = License(key, src_dir)

    return licenses


def get_rules_from_license_texts(licenses_list=None):
    """
    Return an iterable of rules built from license texts and spdx texts from
    in the `licenses_list` license objects iterable.

    Load the reference list list from disk if list_list is not provided.
    """
    if not licenses_list:
        licenses_list = get_licenses_by_key()

    for license_key, license_obj in licenses_list.items():
        text = license_obj.text
        spdx_text = license_obj.spdx_license_text
        if text:
            yield Rule(
                text_file=join(license_obj.src_dir, license_obj.text_file),
                licenses=[license_key],
            )

        if spdx_text:
            yield Rule(
                text_file=join(license_obj.src_dir, license_obj.spdx_file),
                licenses=[license_key],
            )


text_tknzr, template_tknzr, _ = index.tokenizers()

def get_tokens(location, template):
    """
    Return a list of tokens from a from a file at location using the tokenizer
    function.
    """
    location = os.path.abspath(location)
    if not exists(location):
        return []

    tokenizr = template_tknzr if template else text_tknzr
    lines = analysis.unicode_text_lines(location)
    return list(tokenizr(lines))


class Rule(object):
    """
    Base class for detection rules.
    """
    def __init__(self, data_file=None, text_file=None,
                 licenses=None, license_choice=False,
                 template=False, notes=None):

        self.licenses = licenses or []
        self.license_choice = license_choice
        self.notes = notes

        self.template = template

        self.data_file = data_file
        if data_file:
            self.load()

        self.text_file = text_file

        self.tokens = None  # a list
        self.tokens_count = 0

    def get_tokens(self):
        if self.tokens is None:
            self.tokens = get_tokens(self.text_file, self.template)
            self.tokens_count = len(self.tokens)
        return self.tokens

    @property
    def text(self):
        if not exists(self.text_file):
            text = u''
        else:
            with codecs.open(self.text_file, encoding='utf-8') as f:
                text = f.read()
        return text

    @property
    def identifier(self):
        return fileutils.file_name(self.text_file)

    def __repr__(self):
        rt = self.template
        idf = self.identifier
        text = self.text[:10] + '...'
        return 'Rule(%(idf)r, template=%(rt)r, text=%(text)r)' % locals()

    def asdict(self):
        """
        Return an OrderedDict of self, excluding texts.
        Empty values are not included.
        """
        data = OrderedDict()
        if self.licenses:
            data['licenses'] = self.licenses
        if self.license_choice:
            data['license_choice'] = self.license_choice
        if self.template:
            data['template'] = self.template
        if self.notes:
            data['notes'] = self.note
        return data

    def dump(self):
        """
        Dump a representation of self to tgt_dir using two files:
         - a .yml for the rule data in YAML block format
         - a .RULE: the rule text as a UTF-8 file
        """
        if self.data_file:
            as_yaml = saneyaml.dump(self.asdict())
            with codecs.open(self.data_file, 'wb', encoding='utf-8') as df:
                df.write(as_yaml)
            with codecs.open(self.text_file, 'wb', encoding='utf-8') as tf:
                tf.write(self.text)

    def load(self, load_notes=False):
        """
        Load self from a .RULE YAML file stored in self.data_file.
        Does not load the rule text file.
        """
        with codecs.open(self.data_file, encoding='utf-8') as f:
            data = saneyaml.load(f.read())
        self.licenses = data.get('licenses', [])
        self.license_choice = data.get('license_choice', False)
        self.template = data.get('template', False)
        # these are purely informational and not used at run time
        if load_notes:
            self.notes = data.get('notes')
        return self


def load_rules(rule_dir=rules_data_dir):
    """
    Return a list of rules, loaded from rules files.
    FIXME: return an iterable instead
    """
    rules = []

    seen_files = set()
    processed_files = set()
    for top, _, files in os.walk(rule_dir):
        for yfile in files:
            if yfile.endswith('.yml'):
                data_file = join(top, yfile)
                base_name = fileutils.file_base_name(yfile)
                text_file = join(top, base_name + '.RULE')
                rule = Rule(data_file=data_file, text_file=text_file)
                rules.append(rule)
                processed_files.add(data_file)
                processed_files.add(text_file)

            seen_file = join(top, yfile)
            seen_files.add(seen_file)

    unknown_files = seen_files - processed_files
    if unknown_files:
        print(unknown_files)
        files = '\n'.join(sorted(unknown_files))
        msg = 'Unknown files in rule directory: %(rule_dir)r\n%(files)s'
        raise Exception(msg % locals())
    return rules


def get_all_rules(_use_cache=False):
    """
    Return an iterable of all unique rules loaded from licenses and rules files.
    """
    rules = chain(get_rules_from_license_texts(), load_rules())
    unique = unique_rules(rules)
    verify_rules_license(unique)
    return unique


class MissingLicense(Exception):
    pass


def verify_rules_license(rules):
    """
    Ensure that every rules license is a valid license. Raise a MissingLicense
    exception with a message containing the list of rule files that do not have
    a corresponding existing license.
    """
    invalid_rules = defaultdict(list)
    for rule in rules:
        for key in rule.licenses:
            try:
                get_license(key)
            except KeyError:
                invalid_rules[rule.data_file].append(key)
    if invalid_rules:
        invalid_rules = (data_file + ': ' + ' '.join(keys)
                         for data_file, keys in invalid_rules.iteritems())
        msg = 'Rules data file with missing licenses:\n' + '\n'.join(invalid_rules)
        raise MissingLicense(msg)


def unique_rules(rules):
    """
    Return a list of unique rules.
    FIXME: return an iterable instead
    """
    seen = set()
    uniques = []
    for rule in rules:
        ridt = rule_identifier(rule)
        if ridt in seen:
            continue
        else:
            seen.add(ridt)
            uniques.append(rule)
    return uniques


def rule_identifier(rule):
    """
    Return a string used to compare similar rules.
    """
    comparable = rule.text.strip().lower().split()
    comparable.append(repr(rule.license_choice))
    comparable.append(repr(rule.template))
    comparable.extend(sorted(rule.licenses))
    return u''.join([t for t in comparable if t])
