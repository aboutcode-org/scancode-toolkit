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

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import codecs
from collections import defaultdict
from collections import namedtuple
from collections import OrderedDict
from itertools import chain
import os
from os import walk
from os.path import exists
from os.path import join

from commoncode.fileutils import file_base_name
from commoncode.fileutils import file_name
from commoncode.functional import memoize

from licensedcode import NGRAM_LENGTH
from licensedcode import MAX_GAP
from licensedcode import licenses_data_dir
from licensedcode import saneyaml
from licensedcode import src_dir
from licensedcode import rules_data_dir
from licensedcode.tokenize import rule_tokenizer
from licensedcode.tokenize import query_tokenizer


"""
Objects representing reference licenses and license detection rules persisted as
a combo of a YAML 'data' file and one or more text files containing license or
notice texts.
"""

# Set to True to print detailed representations of objects when tracing
TRACE_REPR = False


class License(object):
    """
    A license consists of these files, where <key> is the license key:
        - <key>.yml : the license data in YAML
        - <key>.LICENSE: the license text
        - <key>.SPDX: the SPDX license text
    """
    def __init__(self, key=None, src_dir=licenses_data_dir):
        # unique key: lower case ASCII characters, digits, underscore and dots.
        self.key = key or u''
        self.src_dir = src_dir

        # commonly used short name, often abbreviated.
        self.short_name = u''
        # full name.
        self.name = u''

        # Attribution, Copyleft, etc
        self.category = u''

        self.owner = u''
        self.homepage_url = u''
        self.notes = u''

        # an ordered list of license keys for all the versions of this license
        # Must be including this license key
        self.versions = []

        # True if this license allows later versions to be used
        self.or_later_version = False

        # True if this license allows any version to be used
        self.any_version = False
        # if any_version, what is the license key to pick by default?
        self.any_version_default = u''

        # if this is a license exception, license key this exception applies to
        self.exception_to = u''

        # a license cluster id, computed based on licenses similarities
        self.cluster = u''

        self.spdx_license_key = u''
        self.spdx_full_name = u''
        self.spdx_url = u''
        self.spdx_notes = u''

        self.text_urls = []
        self.osi_url = u''
        self.faq_url = u''
        self.other_urls = []

        self.data_file = join(self.src_dir, self.key + u'.yml')
        self.text_file = join(self.src_dir, self.key + u'.LICENSE')
        self.notice_file = join(self.src_dir, self.key + u'.NOTICE')
        self.spdx_file = join(self.src_dir, self.key + u'.SPDX')

        if src_dir:
            self.load(src_dir)

    @property
    def text(self):
        """
        License text, re-loaded on demand.
        """
        return self._read_text(self.text_file)

    @property
    def notice_text(self):
        """
        Notice text, re-loaded on demand.
        """
        return self._read_text(self.notice_file)

    @property
    def spdx_license_text(self):
        """
        SPDX license text, re-loaded on demand.

        Note that even though a license may be in the SPDX list, we only keep
        its text if it is different from our standard .LICENSE text.
        """
        return self.spdx_license_key and self._read_text(self.spdx_file) or u''

    def asdict(self):
        """
        Return an OrderedDict of license data (excluding texts).
        Empty values are not included.
        """
        data = OrderedDict()

        data[u'key'] = self.key
        if self.short_name:
            data[u'short_name'] = self.short_name
        if self.name:
            data[u'name'] = self.name

        if self.category:
            data[u'category'] = self.category

        if self.owner:
            data[u'owner'] = self.owner
        if self.homepage_url:
            data[u'homepage_url'] = self.homepage_url
        if self.notes:
            data[u'notes'] = self.notes

        if self.versions:
            data[u'versions'] = self.versions
            if self.or_later_version:
                data[u'or_later_version'] = self.or_later_version
            if self.any_version:
                data[u'any_version'] = self.any_version
            if self.any_version_default:
                data[u'any_version_default'] = self.any_version_default

        if self.exception_to:
            data[u'exception_to'] = self.exception_to

        if self.spdx_license_key:
            data[u'spdx_license_key'] = self.spdx_license_key
            data[u'spdx_full_name'] = self.spdx_full_name
            data[u'spdx_url'] = self.spdx_url
            if self.spdx_notes:
                data[u'spdx_notes'] = self.spdx_notes

        if self.text_urls:
            data[u'text_urls'] = self.text_urls
        if self.osi_url:
            data[u'osi_url'] = self.osi_url
        if self.faq_url:
            data[u'faq_url'] = self.faq_url
        if self.other_urls:
            data[u'other_urls'] = self.other_urls
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
        if self.notice_text:
            self._write(self.notice_file, self.notice_text)

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
            # this is a rare case: fail loudly
            print()
            print('#############################')
            print('INVALID LICENSE YAML FILE:', data_file)
            print('#############################')
            print(e)
            print('#############################')
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

    @staticmethod
    def validate(licenses, verbose=False):
        """
        Validate a mapping of key->lic for correctness. Return two
        dictionaries of errors and warnings listing validation messages by
        license_key. Print errors and warnings if verbose is True.
        """
        errors = defaultdict(list)
        warnings = defaultdict(list)
        infos = defaultdict(list)

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

            # keys consistency for exceptions and multiple versions
            if lic.exception_to:
                if not lic.exception_to in licenses:
                    err('Unknown exception_to license key')

            if lic.versions:
                if not any(lic.versions):
                    err('Empty versions list')
                if key not in lic.versions:
                    info('License key not in its own versions list')

                for vkey in lic.versions:
                    if  vkey not in licenses:
                        err('Unknown license in versions. Not a lic: ' + vkey)

                if lic.or_later_version or lic.any_version or lic.any_version_default:
                    warn('No additional flags or default defined with a versions list')
                if len(lic.versions) != len(set(lic.versions)):
                    warn('Duplicated license keys in versions list')

            if (lic.or_later_version or lic.any_version or lic.any_version_default) and not lic.versions:
                    err('Inconsistent or_later_version or any_version flag or any_version_default: no versions list')

            if not lic.any_version and lic.any_version_default:
                err('Inconsistent any_version_default: any_version flag not set')
            if lic.any_version_default and lic.any_version_default not in licenses:
                err('Unknown lic in any_version_default')
            if lic.any_version_default and lic.any_version_default not in lic.versions:
                err('Inconsistent any_version_default: not listed in versions')


            # URLS dedupe and consistency
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
            spdx_license_text = lic.spdx_license_text
            text = lic.text
            notice_text = lic.notice_text

            license_qtokens = tuple(query_tokenizer(text, lower=True))
            license_rtokens = tuple(rule_tokenizer(text, lower=True))
            if license_qtokens != license_rtokens:
                info('License text contains rule templated region with  {{}}')
            if not license_qtokens:
                info('No license text')
            else:
                # for global dedupe
                by_text[license_qtokens].append(key + ': TEXT')

            if spdx_license_text:
                spdx_qtokens = tuple(query_tokenizer(spdx_license_text, lower=True))
                spdx_rtokens = tuple(rule_tokenizer(spdx_license_text, lower=True))
                if spdx_qtokens:
                    if spdx_qtokens != spdx_rtokens:
                        info('SPDX text contains rule templated region with  {{}}')

                    if spdx_qtokens == license_qtokens:
                        err('License text same as SPDX text')
                    else:
                        by_text[spdx_qtokens].append(key + ': SPDX')

            if notice_text:
                notice_qtokens = tuple(query_tokenizer(notice_text, lower=True))
                notice_rtokens = tuple(rule_tokenizer(notice_text, lower=True))
                if notice_qtokens:
                    if notice_qtokens != notice_rtokens:
                        info('NOTICE text contains rule templated region with {{}}')
                    if notice_qtokens == license_qtokens:
                        err('License text same as NOTICE text')
                    else:
                        by_text[notice_qtokens].append(key + ': NOTICE')

            # SPDX consistency
            if not lic.spdx_license_key:
                if lic.spdx_full_name:
                    err('spdx_full_name defined with no spdx_license_key')
                if lic.spdx_url:
                    err('spdx_url defined with no spdx_license_key')
                if lic.spdx_notes:
                    err('spdx_notes defined with no spdx_license_key')
                if spdx_license_text:
                    err('spdx_license_text defined with no spdx_license_key')
            else:
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


# global cache of licenses as mapping of lic key -> lic object
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


Thresholds = namedtuple('Thresholds', ['high_len', 'low_len', 'length', 'small', 'min_high', 'min_len', 'max_gaps'])


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
                 'high_unique', 'low_unique',
                 'length_unique',
                 'gaps')

    def __init__(self, data_file=None, text_file=None, licenses=None,
                 license_choice=False, notes=None, _text=None):

        ###########
        # FIXME: !!! TWO RULES MAY DIFFER BECAUSE THEY ARE UPDATED BY INDEXING
        ###########

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

        # lengths in token ids, including high/low token counts, set in indexing
        self.high_unique = 0
        self.low_unique = 0
        self.length_unique = 0

        # set of pos followed by a gap, aka a template part
        self.gaps = set()

    def same(self, other):
        """
        Return True if all essential attributes of this rule are the same as for the other rule.
        """
        if not isinstance(other, Rule):
            return False

        self_data = (
            self.licensing_identifier(),
            self.license_choice,
            self.notes,
            list(self.tokens()),
            self.gaps
         )
        other_data = (
            other.licensing_identifier(),
            other.license_choice,
            other.notes,
            list(other.tokens()),
            other.gaps
         )
        return self_data == other_data

    def tokens(self, lower=True):
        """
        Return an iterable of token strings for this rule and keep track of gaps
        by position. Gaps and length are recomputed. Tokens inside gaps are
        tracked but not part of the returned stream.
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

    @memoize
    def identifier(self):
        """
        Return a computed rule identifier based on the rule file name.
        """
        # use dummy _tst_ identifier for test only
        return self.text_file and file_name(self.text_file) or '_tst_'

    def __repr__(self):
        idf = self.identifier()
        ird = self.rid
        if TRACE_REPR:
            text = self.text()
        else:
            text = self.text()[:10] + '...'
        keys = self.licenses
        choice = self.license_choice
        return 'Rule(%(idf)r, rid=%(ird)r, licenses=%(keys)r, choice=%(choice)r, text=%(text)r)' % locals()

    def licensing_identifier(self):
        return tuple(sorted(set(self.licenses))) + (self.license_choice,)

    def same_licensing(self, other):
        """
        Return True if the other rule has a the same licensing as this rule.
        """
        # TODO: include license expressions
        return self.licensing_identifier() == other.licensing_identifier()

    def licensing_contains(self, other):
        """
        Return True if the other rule licensing is contained in this rule licensing.
        """
        # TODO: include license expressions
        return set(self.licensing_identifier()).issuperset(other.licensing_identifier())

    def negative(self):
        """
        Return True if this Rule does not point to real licenses and is
        therefore a "negative" rule denoting that a match to this rule should be
        ignored.
        """
        return not self.licenses

    def small(self):
        return bool(self.length < 15 and not self.gaps)

    # TODO: memoize
    def thresholds(self):
        """
        Return a Thresholds tuple of matching thresholds for this rule
        considering every token occurrence.
        """
        if self.length < 5:
            # all tokens should be matched
            min_high = self.high_length
            min_len = self.length
            max_gaps = 0

        elif self.length < 10:
            # all high tokens should be matched
            min_high = self.high_length
            # most of the length should be matched
            min_len = self.length - 2
            max_gaps = 2

        elif self.length < 20:
            # 50% of high tokens should be matched
            min_high = min([self.high_length / 2, NGRAM_LENGTH])
            min_len = min_high
            max_gaps = 5

        else:
            min_high = min([self.high_length / 2, NGRAM_LENGTH])
            min_len = min_high
            max_gaps = MAX_GAP

        if self.gaps:
            gaps_count = len(self.gaps)

            if self.length < 10:
                max_gaps = gaps_count * 3

            elif self.length < 20:
                max_gaps = gaps_count * 4

            elif self.length < 30:
                max_gaps = gaps_count * 5

            else:
                max_gaps = gaps_count * 10

        return Thresholds(self.high_length, self.low_length, self.length, self.small(), min_high, min_len, max_gaps)

    # TODO: memoize
    def thresholds_unique(self):
        """
        Return a Thresholds tuple of matching thresholds for this rule
        considering only unique token occurrence.
        """
        if self.length < 5:
            # all tokens should be matched
            min_high = self.high_unique
            min_len = self.length_unique
            max_gaps = 0

        elif self.length < 10:
            # all high tokens should be matched
            min_high = self.high_unique
            # most of the length should be matched
            min_len = self.length_unique - 1
            max_gaps = 2

        elif self.length < 20:
            # 50% of high tokens should be matched
            min_high = min([self.high_unique // 2, NGRAM_LENGTH])
            min_len = min_high
            max_gaps = 5

        else:
            min_high = min([self.high_unique // 2, NGRAM_LENGTH])
            min_len = min_high
            max_gaps = MAX_GAP

        if self.gaps:
            gaps_count = len(self.gaps)

            if self.length < 10:
                max_gaps = gaps_count * 3

            elif self.length < 20:
                max_gaps = gaps_count * 4

            elif self.length < 30:
                max_gaps = gaps_count * 5

            else:
                max_gaps = gaps_count * 10

        return Thresholds(self.high_unique, self.low_unique, self.length_unique, self.small(), min_high, min_len, max_gaps)

    def min_density(self):
        """
        Return a float between 0 and 1 representing the minimum density that a
        match to this rule should have to be valid and significant.
        
        The rationale is that for some small rules with few tokens, it does not
        make sense to consider sparse matches at all unless their density is
        high. For larger rules, matches that are very sparse may not make sense
        either.
        
        For example, a rule with this text: 
            Apache-1.1
        should not be matched to this query:    
            This Apache component was released as v1.1 in 2015.
        """
        if not self.gaps:
            if self.length < 10:
                return 1.00
            elif self.length < 20:
                return 0.90
            elif self.length < 30:
                return 0.85
            elif self.length < 50:
                return 0.80
            else:
                return 0.75

        # with gaps:
        if self.length < 30:
            biggest_gap = 5
        else:
            biggest_gap = min([self.length / 10., MAX_GAP])

        gaps_count = len(self.gaps)
        dens = self.length / (self.length + (biggest_gap * gaps_count))
        return dens

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
