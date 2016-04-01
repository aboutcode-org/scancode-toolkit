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
from collections import defaultdict
from collections import OrderedDict
from itertools import chain
import logging
import os
from os import walk
from os.path import exists
from os.path import join

from commoncode.fileutils import file_base_name
from commoncode.fileutils import file_name
from commoncode.functional import memoize

from licensedcode import licenses_data_dir
from licensedcode import saneyaml
from licensedcode import src_dir
from licensedcode import rules_data_dir
from licensedcode.tokenize import rule_tokenizer


"""
Model objects for license and rule persisted as YAML and text files.
"""

logger = logging.getLogger(__name__)
# import sys
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# logger.setLevel(logging.DEBUG)


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
        data_file = join(src_dir, self.data_file)
        try:
            with codecs.open(data_file, encoding='utf-8') as f:
                data = saneyaml.load(f.read())
        except Exception, e:
            print()
            print('#############################')
            print('INVALID LICENSE YAML FILE:', data_file)
            print('#############################')
            print(e)
            print('#############################')
            # this is a rare case
            raise

        for k, v in data.items():
            setattr(self, k, v)

    def _read_text(self, location):
        if not exists(location):
            text = u''
        else:
            with codecs.open(location, encoding='utf-8') as f:
                text = f.read()
        return text


# global cache of licenses as mapping of license key -> license object
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

    for top, _, files in os.walk(license_dir):
        for yfile in files:
            if not yfile.endswith('.yml'):
                continue
            key = yfile.replace('.yml', '')
            yfile = join(top, yfile)
            src_dir = os.path.dirname(yfile)
            licenses[key] = License(key, src_dir)

    return licenses


def get_rules(unique=False):
    """
    Return an iterable of all rules loaded from licenses and rules files.
    Check uniqueness if unique is True.
    """
    rls = chain(rules_from_licenses(), rules())
    if unique:
        rls = unique_rules(rls)
        check_licenses(rls)
    return rls


@memoize
def rules(rule_dir=rules_data_dir):
    return list(_rules(rule_dir))


def _rules(rule_dir=rules_data_dir):
    """
    Return an iterable of rules loaded from rules files.
    """
    # TODO: OPTIMIZE: break RULES with gaps in multiple sub-rules??
    # TODO: OPTIMIZE: create a graph of rules to account for containment and similarity clusters?
    seen_files = set()
    processed_files = set()
    for top, _, files in walk(rule_dir):
        for yfile in (f for f in files if f.endswith('.yml')):
            data_file = join(top, yfile)
            base_name = file_base_name(yfile)
            text_file = join(top, base_name + '.RULE')
            processed_files.add(data_file)
            processed_files.add(text_file)
            yield Rule(data_file=data_file, text_file=text_file)
            seen_files.add(join(top, yfile))

    unknown_files = seen_files - processed_files
    if unknown_files:
        print(unknown_files)
        files = '\n'.join(sorted(unknown_files))
        msg = 'Unknown files in rule directory: %(rule_dir)r\n%(files)s'
        raise Exception(msg % locals())


def rules_from_licenses(licenses=None):
    """
    Return an iterable of rules built from license and spdx texts from a
    `licenses` license objects iterable.

    Load the reference list from disk if `licenses` is not provided.
    """
    licenses = licenses or get_licenses_by_key()
    for license_key, license_obj in licenses.items():
        text = license_obj.text
        spdx_text = license_obj.spdx_license_text
        if text:
            tfile = join(license_obj.src_dir, license_obj.text_file)
            yield Rule(text_file=tfile, licenses=[license_key])
        if spdx_text:
            sfile = join(license_obj.src_dir, license_obj.spdx_file)
            yield Rule(text_file=sfile, licenses=[license_key])


class Rule(object):
    """
    A detection rule object is a text to use for detection and corresponding
    detected licenses and metadata. A rule text can contain variable parts
    marked with double curly braces {{ }}.
    """
    # OPTMIZED: use slot to increase attribute access speed wrt. namedtuple
    __slots__ = ('rid', 'licenses', 'license_choice', 'notes', 'data_file',
                 'text_file', '_text', 'length', 
                 'high_length', 'low_length', 
                 'gaps', 'gaps_count')

    def __init__(self, data_file=None, text_file=None, licenses=None,
                 license_choice=False, notes=None, _text=None):

        # optional rule id int typically assigned at indexing time
        self.rid = None

        # list of valid license keys
        self.licenses = licenses or []

        # True if the rule is for a choice of all licenses. default to False
        self.license_choice = license_choice

        self.notes = notes

        # path to the YAML data file for this rule
        self.data_file = data_file
        if data_file:
            self.load()

        # path to the rule text file
        self.text_file = text_file
        # for testing only, when we do not use a file
        self._text = _text

        # length in number of token strings
        self.length = 0

        # lengths in token ids, including high/low token counts, set in indexing
        self.high_length = 0
        self.low_length = 0

        # set of pos followed by a gap, aka a template part
        self.gaps = set()
        self.gaps_count = 0

    def tokens(self, lower=True):
        """
        Return an iterable of tokens and keep track of gaps by position. Gaps
        and length are recomputed. Tokens inside gaps are tracked but not part
        of the returned stream.
        """
        gaps = set()
        # Note: we track the pos instead of enumerating it because we create
        # positions abstracting gaps
        pos = 0
        length = 0
        for token in rule_tokenizer(self.text(), lower=lower):
            if token is None:
                gaps.add(pos - 1)
            else:
                length += 1
                yield token
                # only increment pos if we are not in a gap
                pos += 1

        self.length = length
        self.gaps = gaps
        self.gaps_count = len(gaps)

    def text(self):
        """
        Return the rule text loaded from its file.
        """
        # used for test only
        if self._text:
            return self._text
        
        elif self.text_file and exists(self.text_file):
            with codecs.open(self.text_file, encoding='utf-8') as f:
                return f.read()
        else:
            raise Exception('Inconsistent rule text for:', self.identifier())

    def identifier(self):
        """
        Return a computed rule identifier based on the rule file name.
        """
        # use dummy _tst_ identifier for test only
        return self.text_file and file_name(self.text_file) or '_tst_'

    def __repr__(self):
        idf = self.identifier()
        ird = self.rid
        text = self.text()[:10] + '...'
        keys = self.licenses
        choice = self.license_choice
        return 'Rule(%(idf)r, rid=%(ird)r, licenses=%(keys)r, choice=%(choice)r, text=%(text)r)' % locals()

    def licensing_identifier(self):
        return tuple(sorted(set(self.licenses))) + (self.license_choice,)

    def same_licensing(self, other):
        """
        Return True if other rule has a the same licensing as self.
        """
        # TODO: include license expressions
        return self.licensing_identifier() == other.licensing_identifier()

    def negative(self):
        """
        Return True if this Rule does not point to real licenses and is
        therefore a "negative" rule denoting that a match to this rule should be
        ignored.
        """
        return not self.licenses

    def _data(self):
        """
        Return a tuple of data used to check for uniqueness.
        """
        comparable = list(self.tokens())
        comparable.extend(sorted(self.gaps))
        comparable.append(self.license_choice)
        comparable.extend(sorted(self.licenses))
        return tuple(comparable)

    def asdict(self):
        """
        Return an OrderedDict of self, excluding texts. Used for serialization.
        Empty values are not included.
        """
        data = OrderedDict()
        if self.licenses:
            data['licenses'] = self.licenses
        if self.license_choice:
            data['license_choice'] = self.license_choice
        if self.notes:
            data['notes'] = self.note
        return data

    def dump(self):
        """
        Dump a representation of self to tgt_dir as two files:
         - a .yml for the rule data in YAML block format
         - a .RULE: the rule text as a UTF-8 file
        """
        if self.data_file:
            as_yaml = saneyaml.dump(self.asdict())
            with codecs.open(self.data_file, 'wb', encoding='utf-8') as df:
                df.write(as_yaml)
            with codecs.open(self.text_file, 'wb', encoding='utf-8') as tf:
                tf.write(self.text())

    def load(self, load_notes=False):
        """
        Load self from a .RULE YAML file stored in self.data_file.
        Does not load the rule text file.
        """
        try:
            with codecs.open(self.data_file, encoding='utf-8') as f:
                data = saneyaml.load(f.read())
        except Exception, e:
            print('#############################')
            print('INVALID LICENSE RULE FILE:', self.data_file)
            print('#############################')
            print(e)
            print('#############################')
            # this is a rare case, but yes we abruptly stop.
            raise e

        self.licenses = data.get('licenses', [])
        self.license_choice = data.get('license_choice', False)
        # these are purely informational and not used at run time
        if load_notes:
            self.notes = data.get('notes')
        return self


class MissingLicense(Exception):
    pass


def check_licenses(rules):
    """
    Given a lists of rules, check that all license keys reference a known
    license. Raise a MissingLicense exception with a message containing the list
    of rule files without a corresponding license.
    """
    invalid_rules = defaultdict(list)
    for rule in rules:
        for key in rule.licenses:
            try:
                get_license(key)
            except KeyError:
                invalid_rules[rule.data_file].append(key)
    if invalid_rules:
        invalid_rules = (data_file + ': ' + ' '.join(keys) for data_file, keys in invalid_rules.iteritems())
        msg = 'Rules data file with missing licenses:\n' + '\n'.join(invalid_rules)
        raise MissingLicense(msg)


def unique_rules(rules):
    """
    Yield an iterable of unique rules given an iterable of rules.
    """
    seen = {}
    for rule in rules:
        ridt = rule._data()
        if ridt in seen:
            print(rule.identifier(), 'is a duplicate of', seen[ridt])
            continue
        else:
            seen[ridt] = rule.identifier()
            yield rule
