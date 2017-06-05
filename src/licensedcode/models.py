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
from __future__ import division

import codecs
from collections import Counter
from collections import defaultdict
from collections import namedtuple
from collections import OrderedDict
from copy import copy
from itertools import chain
from operator import itemgetter
from os.path import exists
from os.path import join

from commoncode.fileutils import file_base_name
from commoncode.fileutils import file_name
from commoncode.fileutils import file_iter
from textcode.analysis import text_lines

from licensedcode import MIN_MATCH_LENGTH
from licensedcode import MIN_MATCH_HIGH_LENGTH
from licensedcode import licenses_data_dir
from licensedcode import rules_data_dir
from licensedcode import saneyaml
from licensedcode.tokenize import rule_tokenizer
from licensedcode.tokenize import query_tokenizer
from commoncode import fileutils


"""
Reference License and license Rule structures persisted as a combo of a YAML
data file and one or more text files containing license or notice texts.
"""

# Set to True to print detailed representations of objects when tracing
TRACE_REPR = False


class License(object):
    """
    A license consists of these files, where <key> is the license key:
        - <key>.yml : the license data in YAML
        - <key>.LICENSE: the license text
    """
    # we do not really need slots but they help keep the attributes in check
    __slots__ = (
        'key',
        'src_dir',
        'is_deprecated',
        'short_name',
        'name',
        'category',
        'owner',
        'homepage_url',
        'notes',
        'is_exception',
        'next_version',
        'is_or_later',
        'base_license',
        'spdx_license_key',
        'text_urls',
        'osi_url',
        'faq_url',
        'other_urls',
        'data_file',
        'text_file',
        'minimum_coverage',
        'standard_notice',
    )

    def __init__(self, key=None, src_dir=licenses_data_dir):
        """
        Initialize a License for a `key` and data stored in the `src_dir`
        directory. Key is a lower-case unique ascii string.
        """
        # unique key: lower case ASCII characters, digits, underscore and dots.
        self.key = key or ''
        self.src_dir = src_dir

        # if this is a deprecated license, add also notes explaining why
        self.is_deprecated = False

        # commonly used short name, often abbreviated.
        self.short_name = ''
        # full name.
        self.name = ''

        # Permissive, Copyleft, etc
        self.category = ''

        self.owner = ''
        self.homepage_url = ''
        self.notes = ''

        # if this is a license exception, the license key this exception applies to
        self.is_exception = False

        # license key for the next version of this license if any
        self.next_version = ''
        # True if this license allows later versions to be used
        self.is_or_later = False
        # If is_or_later is True, license key for the not "or later" variant if any
        self.base_license = ''

        # SPDX key for SPDX licenses
        self.spdx_license_key = ''

        # Various URLs for info
        self.text_urls = []
        self.osi_url = ''
        self.faq_url = ''
        self.other_urls = []

        self.minimum_coverage = 0
        self.standard_notice = ''

        # data file paths and known extensions
        self.data_file = ''
        self.text_file = ''
        if self.src_dir:
            self.set_file_paths()

            if exists(self.data_file):
                self.load(src_dir)

    def set_file_paths(self):
        self.data_file = join(self.src_dir, self.key + '.yml')
        self.text_file = join(self.src_dir, self.key + '.LICENSE')

    def relocate(self, src_dir):
        """
        Return a copy of this license object relocated to a new `src_dir`.
        Also copy the LICENSE file.
        """
        newl = copy(self)
        newl.src_dir = src_dir
        newl.set_file_paths()
        if self.text:
            fileutils.copyfile(self.text_file, newl.text_file)
        return newl

    def update(self, mapping):
        for k, v in mapping.items():
            setattr(self, k, v)

    def __copy__(self):
        oldl = self.to_dict()
        newl = License(key=self.key)
        newl.update(oldl)
        return newl

    @property
    def text(self):
        """
        License text, re-loaded on demand.
        """
        return self._read_text(self.text_file)

    def to_dict(self):
        """
        Return an OrderedDict of license data (excluding texts).
        Fields with empty values are not included.
        """
        data = OrderedDict()

        data['key'] = self.key
        if self.short_name:
            data['short_name'] = self.short_name
        if self.name:
            data['name'] = self.name

        if self.is_deprecated:
            data['is_deprecated'] = self.is_deprecated

        if self.category:
            data['category'] = self.category

        if self.owner:
            data['owner'] = self.owner
        if self.homepage_url:
            data['homepage_url'] = self.homepage_url
        if self.notes:
            data['notes'] = self.notes

        if self.is_exception:
            data['is_exception'] = self.is_exception

        if self.next_version:
            data['next_version'] = self.next_version

        if self.is_or_later:
            data['is_or_later'] = self.is_or_later
            if self.base_license:
                data['base_license'] = self.base_license

        if self.spdx_license_key:
            data['spdx_license_key'] = self.spdx_license_key

        if self.text_urls:
            data['text_urls'] = self.text_urls
        if self.osi_url:
            data['osi_url'] = self.osi_url
        if self.faq_url:
            data['faq_url'] = self.faq_url
        if self.other_urls:
            data['other_urls'] = self.other_urls
        if self.minimum_coverage:
            data['minimum_coverage'] = int(self.minimum_coverage)
        if self.standard_notice:
            data['standard_notice'] = self.standard_notice
        return data

    def dump(self):
        """
        Dump a representation of self as multiple files named
        this way:
         - <key>.yml : the license data in YAML
         - <key>.LICENSE: the license text
        """
        as_yaml = saneyaml.dump(self.to_dict())
        self._write(self.data_file, as_yaml)
        if self.text:
            self._write(self.text_file, self.text)

    def _write(self, f, d):
        with codecs.open(f, 'wb', encoding='utf-8') as of:
            of.write(d)

    def load(self, src_dir):
        """
        Populate license data from a YAML file stored in of src_dir.
        Does not load text files.
        Unknown fields are ignored and not bound to the License object.
        """
        try:
            with codecs.open(self.data_file, encoding='utf-8') as f:
                data = saneyaml.load(f.read())
        except Exception, e:
            # this is a rare case: fail loudly
            print()
            print('#############################')
            print('INVALID LICENSE YAML FILE:', self.data_file)
            print('#############################')
            print(e)
            print('#############################')
            raise

        numeric_keys = ('minimum_coverage',)
        for k, v in data.items():
            if k in numeric_keys:
                v = int(v)

            if k == 'key':
                assert self.key == v, 'Inconsistent YAML key and file names for %r' % self.key

            setattr(self, k, v)

    def _read_text(self, location):
        if not exists(location):
            text = ''
        else:
            with codecs.open(location, encoding='utf-8') as f:
                text = f.read()
        return text

    @staticmethod
    def validate(licenses, verbose=False, no_dupe_urls=False):
        """
        Check that licenses are valid. `licenses` is a mapping of key ->
        License. Return dictionaries of infos, errors and warnings mapping a
        license key to validation issue messages. Print messages if verbose is
        True.
        """
        infos = defaultdict(list)
        warnings = defaultdict(list)
        errors = defaultdict(list)

        # used for global dedupe of texts
        by_spdx_key = defaultdict(list)
        by_text = defaultdict(list)

        for key, lic in licenses.items():
            err = errors[key].append
            warn = warnings[key].append
            info = infos[key].append

            # names
            if not lic.short_name:
                warn('No short name')
            if not lic.name:
                warn('No name')
            if not lic.category:
                warn('No category')

            if lic.next_version and lic.next_version not in licenses:
                err('License next version is unknown')

            if (lic.is_or_later and
                lic.base_license and
                lic.base_license not in licenses):
                err('Base license for an "or later" license is unknown')

            # URLS dedupe and consistency
            if no_dupe_urls:
                if lic.text_urls and not all(lic.text_urls):
                    warn('Some empty license text_urls')

                if lic.other_urls and not all(lic.other_urls):
                    warn('Some empty license other_urls')

                # redundant URLs used multiple times
                if lic.homepage_url:
                    if lic.homepage_url in lic.text_urls:
                        warn('Homepage URL also in text_urls')
                    if lic.homepage_url in lic.other_urls:
                        warn('Homepage URL also in other_urls')
                    if lic.homepage_url == lic.faq_url:
                        warn('Homepage URL same as faq_url')
                    if lic.homepage_url == lic.osi_url:
                        warn('Homepage URL same as osi_url')

                if lic.osi_url or lic.faq_url:
                    if lic.osi_url == lic.faq_url:
                        warn('osi_url same as faq_url')

                all_licenses = lic.text_urls + lic.other_urls
                for url in lic.osi_url, lic.faq_url, lic.homepage_url:
                    if url: all_licenses.append(url)

                if not len(all_licenses) == len(set(all_licenses)):
                    warn('Some duplicated URLs')

            # local text consistency
            text = lic.text

            license_qtokens = tuple(query_tokenizer(text, lower=True))
            license_rtokens = tuple(rule_tokenizer(text, lower=True))
            if license_qtokens != license_rtokens:
                info('License text contains rule templated region with  {{}}')
            if not license_qtokens:
                info('No license text')
            else:
                # for global dedupe
                by_text[license_qtokens].append(key + ': TEXT')


            # SPDX consistency
            if lic.spdx_license_key:
                by_spdx_key[lic.spdx_license_key].append(key)

        # global SPDX consistency
        multiple_spdx_keys_used = {k: v for k, v in by_spdx_key.items() if len(v) > 1}
        if multiple_spdx_keys_used:
            for k, lkeys in multiple_spdx_keys_used.items():
                infos['GLOBAL'].append('SPDX key: ' + k + ' used in multiple licenses: ' + ', '.join(sorted(lkeys)))

        # global text dedupe
        multiple_texts = {k: v for k, v in by_text.items() if len(v) > 1}
        if multiple_texts:
            for k, msgs in multiple_texts.items():
                errors['GLOBAL'].append('Duplicate texts in multiple licenses:' + ', '.join(sorted(msgs)))

        errors = {k: v for k, v in errors.items() if v}
        warnings = {k: v for k, v in warnings.items() if v}
        infos = {k: v for k, v in infos.items() if v}

        if verbose:
            print('Licenses validation errors:')
            for key, msgs in sorted(errors.items()):
                print('ERRORS for:', key, ':', '\n'.join(msgs))

            print('Licenses validation warnings:')
            for key, msgs in sorted(warnings.items()):
                print('WARNINGS for:', key, ':', '\n'.join(msgs))

            print('Licenses validation infos:')
            for key, msgs in sorted(infos.items()):
                print('INFOS for:', key, ':', '\n'.join(msgs))

        return errors, warnings, infos


def load_licenses(licenses_data_dir=licenses_data_dir , with_deprecated=False):
    """
    Return a mapping of key -> license objects, loaded from license files.
    """
    licenses = {}
    for data_file in file_iter(licenses_data_dir):
        if not data_file.endswith('.yml'):
            continue
        key = file_base_name(data_file)
        lic = License(key, licenses_data_dir)
        if not with_deprecated and lic.is_deprecated:
            continue
        licenses[key] = lic
    return licenses


def get_rules(licenses_data_dir=licenses_data_dir, rules_data_dir=rules_data_dir):
    """
    Return a mapping of key->license and an iterable of license detection
    rules loaded from licenses and rules files. Raise a MissingLicenses
    exceptions if a rule references unknown license keys.
    """
    from licensedcode.cache import get_licenses_db
    licenses = get_licenses_db(licenses_data_dir=licenses_data_dir)
    rules = list(load_rules(rules_data_dir=rules_data_dir))
    check_rules_integrity(rules, licenses)

    licenses_as_rules = build_rules_from_licenses(licenses)
    return chain(licenses_as_rules, rules)


class MissingLicenses(Exception):
    pass


def check_rules_integrity(rules, licenses):
    """
    Given a lists of rules, check that all the rule license keys
    reference a known license from a mapping of licenses (key->license).
    Raise a MissingLicense exception with a message containing the list
    of rule files without a corresponding license.
    """
    invalid_rules = defaultdict(set)
    for rule in rules:
        unknown_keys = [key for key in rule.licenses if key not in licenses]
        if unknown_keys:
            invalid_rules[rule.data_file].update(unknown_keys)

    if invalid_rules:
        invalid_rules = (data_file + ': ' + ' '.join(keys)
                         for data_file, keys in invalid_rules.iteritems() if keys)
        msg = 'Rules referencing missing licenses:\n' + '\n'.join(sorted(invalid_rules))
        raise MissingLicenses(msg)


def build_rules_from_licenses(licenses):
    """
    Return an iterable of rules built from each license text from a `licenses`
    iterable of license objects. Use the reference list if `licenses` is not
    provided.

    Load the reference license list from disk if `licenses` is not provided.
    """
    for license_key, license_obj in licenses.iteritems():
        text_file = join(license_obj.src_dir, license_obj.text_file)
        minimum_coverage = license_obj.minimum_coverage

        if exists(text_file):
            yield Rule(text_file=text_file, licenses=[license_key],
                       minimum_coverage=minimum_coverage, is_license=True)


def load_rules(rules_data_dir=rules_data_dir):
    """
    Return an iterable of rules loaded from rule files.
    """
    # TODO: OPTIMIZE: create a graph of rules to account for containment and similarity clusters?
    # TODO: we should assign the rule id at that stage
    seen_files = set()
    processed_files = set()
    lower_case_files = set()
    case_problems = set()
    for data_file in file_iter(rules_data_dir):
        if data_file.endswith('.yml'):
            base_name = file_base_name(data_file)
            rule_file = join(rules_data_dir, base_name + '.RULE')
            yield Rule(data_file=data_file, text_file=rule_file)

            # accumulate sets to ensures we do not have illegal names or extra
            # orphaned files
            data_lower = data_file.lower()
            if data_lower in lower_case_files:
                case_problems.add(data_lower)
            else:
                lower_case_files.add(data_lower)

            rule_lower = rule_file.lower()
            if rule_lower in lower_case_files:
                case_problems.add(rule_lower)
            else:
                lower_case_files.add(rule_lower)

            processed_files.update([data_file, rule_file])

        if not data_file.endswith('~'):
            seen_files.add(data_file)

    unknown_files = seen_files - processed_files
    if unknown_files or case_problems:
        if unknown_files:
            files = '\n'.join(sorted(unknown_files))
            msg = 'Orphaned files in rule directory: %(rule_dir)r\n%(files)s'

        if case_problems:
            files = '\n'.join(sorted(case_problems))
            msg += '\nRule files with non-unique name ignoring casein rule directory: %(rule_dir)r\n%(files)s'

        raise Exception(msg % locals())


Thresholds = namedtuple('Thresholds', ['high_len', 'low_len', 'length', 'small', 'min_high', 'min_len'])


class Rule(object):
    """
    A detection rule object is a text to use for detection and corresponding
    detected licenses and metadata. A rule text can contain variable parts
    marked with double curly braces {{ }}.
    """
    __slots__ = ('rid', 'identifier',
                 'licenses', 'license_choice', 'license', 'licensing_identifier',
                 'false_positive',
                 'notes',
                 'data_file', 'text_file', '_text',
                 'length', 'low_length', 'high_length', '_thresholds',
                 'length_unique', 'low_unique', 'high_unique', '_thresholds_unique',
                 'minimum_coverage', 'relevance', 'has_stored_relevance',
                 'is_license'
                 )

    def __init__(self, data_file=None, text_file=None, licenses=None,
                 license_choice=False, notes=None, minimum_coverage=0,
                 is_license=False, _text=None):

        ###########
        # FIXME: !!! TWO RULES MAY DIFFER BECAUSE THEY ARE UPDATED BY INDEXING
        ###########

        # optional rule id int typically assigned at indexing time
        self.rid = None

        if not text_file:
            assert _text
            self.identifier = '_tst_' + str(len(_text))
        else:
            self.identifier = file_name(text_file)

        # list of valid license keys
        self.licenses = licenses or []
        # True if the rule is for a choice of all licenses. default to False
        self.license_choice = license_choice

        # License expression
        # TODO: implement me.
        self.license = ''

        # is this rule text a false positive when matched? (filtered out) FIXME: this
        # should be unified with the relevance: a false positive match is a a match
        # with a relevance of zero
        self.false_positive = False

        # is this rule text only to be matched with a minimum coverage?
        self.minimum_coverage = minimum_coverage

        # optional, free text
        self.notes = notes

        # what is the relevance of a match to this rule text? a float between 0 and
        # 100 where 100 means highly relevant and 0 menas not relevant at all.
        # For instance a match to the "gpl" or the "cpol" words have a fairly low
        # relevance as they are a weak indication of an actual license and could be
        # a false positive. In somce cases, this may even be used to discard obvious
        # false positive matches automatically.
        self.relevance = 100
        self.has_stored_relevance = False

        # set to True if the rule is built from a .LICENSE full text
        self.is_license = is_license

        # path to the YAML data file for this rule
        self.data_file = data_file
        if data_file:
            try:
                self.load()
            except Exception as e:
                message = 'While loading: %(data_file)r' % locals() + e.message
                print(message)
                raise Exception(message)

        # licensing identifier: TODO: replace with a license expression
        self.licensing_identifier = tuple(self.licenses) + (license_choice,)

        # path to the rule text file
        self.text_file = text_file

        # for testing only, when we do not use a file
        self._text = _text

        # These attributes are computed upon text loading or setting the thresholds
        ###########################################################################

        # length in number of token strings
        self.length = 0

        # lengths in token ids, including high/low token counts, set in indexing
        self.high_length = 0
        self.low_length = 0
        self._thresholds = None

        # lengths in token ids, including high/low token counts, set in indexing
        self.high_unique = 0
        self.low_unique = 0
        self.length_unique = 0
        self._thresholds_unique = None

    def tokens(self, lower=True):
        """
        Return an iterable of token strings for this rule. Length is recomputed as a
        side effect. Tokens inside double curly braces (eg. {{ignored}}) are skipped
        and ignored.
        """
        length = 0
        text = self.text()
        text = text.strip()

        # FIXME: this is weird:
        # We tag this rule as being a bare URL if it starts with a scheme and is on one line: this is used to determine a matching approach
        if text.startswith(('http://', 'https://', 'ftp://')) and '\n' not in text[:1000]:
            self.minimum_coverage = 100

        for token in rule_tokenizer(self.text(), lower=lower):
            length += 1
            yield token

        self.length = length
        self.compute_relevance()

    def text(self):
        """
        Return the rule text loaded from its file.
        """
        # used for test only
        if self._text:
            return self._text

        elif self.text_file and exists(self.text_file):
            # IMPORTANT: use the same process as query text loading for symmetry
            lines = text_lines(self.text_file, demarkup=False)
            return ' '.join(lines)
        else:
            raise Exception('Inconsistent rule text for:', self.identifier)

    def __repr__(self):
        idf = self.identifier
        ird = self.rid
        if TRACE_REPR:
            text = self.text()
        else:
            text = self.text()
        if text:
            text = text[:20] + '...'
        keys = self.licenses
        choice = self.license_choice
        fp = self.false_positive
        minimum_coverage = self.minimum_coverage
        return 'Rule(%(idf)r, lics=%(keys)r, fp=%(fp)r, minimum_coverage=%(minimum_coverage)r, %(text)r)' % locals()

    def same_licensing(self, other):
        """
        Return True if the other rule has a the same licensing as this rule.
        """
        # TODO: include license expressions
        return self.licensing_identifier == other.licensing_identifier

    def licensing_contains(self, other):
        """
        Return True if the other rule licensing is contained in this rule licensing.
        """
        # TODO: include license expressions
        return set(self.licensing_identifier).issuperset(other.licensing_identifier)

    def negative(self):
        """
        Return True if this Rule does not point to real licenses and is
        therefore a "negative" rule denoting that a match to this rule should be
        ignored.
        """
        return not self.licenses and not self.false_positive

    def small(self):
        """
        Is this a small rule? It needs special handling for detection.
        """
        SMALL_RULE = 15
        return self.length < SMALL_RULE or self.minimum_coverage == 100

    def thresholds(self):
        """
        Return a Thresholds tuple considering every token occurrence.
        """
        if not self._thresholds:
            min_high = min([self.high_length, MIN_MATCH_HIGH_LENGTH])
            min_len = MIN_MATCH_LENGTH

            # note: we cascade ifs from largest to smallest lengths
            if self.length < 30:
                min_len = self.length // 2

            if self.length < 10:
                min_high = self.high_length
                min_len = self.length
                self.minimum_coverage = 80

            if self.length < 3:
                min_high = self.high_length
                min_len = self.length
                self.minimum_coverage = 100

            if self.minimum_coverage == 100:
                min_high = self.high_length
                min_len = self.length

            self._thresholds = Thresholds(
                self.high_length, self.low_length, self.length,
                self.small(), min_high, min_len
            )
        return self._thresholds

    def thresholds_unique(self):
        """
        Return a Thresholds tuple considering only unique token occurrence.
        """
        if not self._thresholds_unique:
            highu = (int(self.high_unique // 2)) or self.high_unique
            min_high = min([highu, MIN_MATCH_HIGH_LENGTH])
            min_len = MIN_MATCH_LENGTH
            # note: we cascade IFs from largest to smallest lengths
            if self.length < 20:
                min_high = self.high_unique
                min_len = min_high

            if self.length < 10:
                min_high = self.high_unique
                if self.length_unique < 2:
                    min_len = self.length_unique
                else:
                    min_len = self.length_unique - 1

            if self.length < 5:
                min_high = self.high_unique
                min_len = self.length_unique

            if self.minimum_coverage == 100:
                min_high = self.high_unique
                min_len = self.length_unique

            self._thresholds_unique = Thresholds(
                self.high_unique, self.low_unique, self.length_unique,
                self.small(), min_high, min_len)
        return self._thresholds_unique

    def to_dict(self):
        """
        Return an OrderedDict of self, excluding texts. Used for serialization.
        Empty values are not included.
        """
        data = OrderedDict()
        if self.licenses:
            data['licenses'] = self.licenses
        if self.license_choice:
            data['license_choice'] = self.license_choice
        if self.license:
            data['license'] = self.license
        if self.false_positive:
            data['false_positive'] = self.false_positive
        if self.has_stored_relevance:
            data['relevance'] = self.relevance
        if self.minimum_coverage:
            data['minimum_coverage'] = self.minimum_coverage
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
            as_yaml = saneyaml.dump(self.to_dict())
            with codecs.open(self.data_file, 'wb', encoding='utf-8') as df:
                df.write(as_yaml)
            with codecs.open(self.text_file, 'wb', encoding='utf-8') as tf:
                tf.write(self.text())

    def load(self, load_notes=False):
        """
        Load self from a .RULE YAML file stored in self.data_file.
        Does not load the rule text file.
        Unknown fields are ignored and not bound to the Rule object.
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
        self.license = data.get('license')
        self.false_positive = data.get('false_positive', False)
        relevance = data.get('relevance')
        if relevance is not None:
            # Keep track if we have a stored relevance of not.
            self.has_stored_relevance = True
            self.relevance = float(relevance)
        self.minimum_coverage = float(data.get('minimum_coverage', 0))

        # these are purely informational and not used at run time
        if load_notes:
            notes = data.get('notes')
            if notes:
                self.notes = notes.strip()
        return self

    def compute_relevance(self):
        """
        Compute and set the `relevance` attribute for this rule. The relevance is a
        float between 0 and 100 where 100 means highly relevant and 0 means not
        relevant at all.

        It is either defined in the rule YAML data file or computed here using this
        approach:

        - a rule of length up to 20 receives 5 relevance points per token (so a rule
          of length 1 has a 5 relevance and a rule of length 20 has a 100 relevance)
        - a rule of length over 20 has a 100 relevance
        - a false positive rule has a relevance of zero.

        For instance a match to the "gpl" or the "cpol" words have a fairly low
        relevance as they are a weak indication of an actual license and could be a
        false positive and should therefore be assigned a low relevance. In contrast
        a match to most or all of the apache-2.0 license text is highly relevant. The
        Rule relevance is used as the basis to compute a match score.
        """
        if self.has_stored_relevance:
            return

        # case for false positive: they do not have licenses and their matches are
        # never returned. Relevance is zero.
        if self.false_positive:
            self.relevance = 0
            return

        # case for negative rules with no license (and are not an FP)
        # they do not have licenses and their matches are never returned
        if self.negative():
            self.relevance = 0
            return

        # general case
        length = self.length
        if length >= 20:
            self.relevance = 100
        else:
            self.relevance = length * 5


def _print_rule_stats():
    """
    Print rules statistics.
    """
    from licensedcode.cache import get_index
    idx = get_index()
    rules = idx.rules_by_rid
    sizes = Counter(r.length for r in rules)
    print('Top 15 lengths: ', sizes.most_common(15))
    print('15 smallest lengths: ', sorted(sizes.iteritems(),
                                          key=itemgetter(0))[:15])

    high_sizes = Counter(r.high_length for r in rules)
    print('Top 15 high lengths: ', high_sizes.most_common(15))
    print('15 smallest high lengths: ', sorted(high_sizes.iteritems(),
                                               key=itemgetter(0))[:15])
