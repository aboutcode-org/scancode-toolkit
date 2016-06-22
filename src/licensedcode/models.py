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
from collections import Counter
from collections import defaultdict
from collections import namedtuple
from collections import OrderedDict
from itertools import chain
from operator import itemgetter
from os.path import exists
from os.path import join

from commoncode.fileutils import file_base_name
from commoncode.fileutils import file_name
from commoncode.fileutils import file_iter

from licensedcode import MAX_GAP_SKIP
from licensedcode import MIN_MATCH_LENGTH
from licensedcode import MIN_MATCH_HIGH_LENGTH
from licensedcode import licenses_data_dir
from licensedcode import saneyaml
from licensedcode import rules_data_dir
from licensedcode.tokenize import rule_tokenizer
from licensedcode.tokenize import query_tokenizer


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
        - <key>.SPDX: the SPDX license text
    """
    # we do not really need slots but they help keep the attributes in check
    __slots__ = (
        'key',
        'src_dir',
        'deprecated',
        'short_name',
        'name',
        'category',
        'owner',
        'homepage_url',
        'notes',
        'versions',
        'or_later_version',
        'any_version',
        'any_version_default',
        'exception_to',
        'spdx_license_key',
        'spdx_full_name',
        'spdx_url',
        'spdx_notes',
        'text_urls',
        'osi_url',
        'faq_url',
        'other_urls',
        'data_file',
        'text_file',
        'notice_file',
        'spdx_file',
    )

    def __init__(self, key=None, src_dir=licenses_data_dir):
        """
        Initialize a License for a `key` and data stored in the `src_dir`
        directory. Key is a lower-case unique ascii string.
        """
        # unique key: lower case ASCII characters, digits, underscore and dots.
        self.key = key or u''
        self.src_dir = src_dir

        # if this is a deprecated license, contains notes explaining why
        self.deprecated = u''

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

        # if this is a license exception, the license key this exception applies to
        self.exception_to = u''

        # SPDX information if present for SPDX licenses
        self.spdx_license_key = u''
        self.spdx_full_name = u''
        self.spdx_url = u''
        self.spdx_notes = u''

        # Various URLs for info
        self.text_urls = []
        self.osi_url = u''
        self.faq_url = u''
        self.other_urls = []

        # data file paths and known extensions
        self.data_file = join(self.src_dir, self.key + u'.yml')
        self.text_file = join(self.src_dir, self.key + u'.LICENSE')
        # note: we do not keep a notice if there is no standard notice or if
        # this is the same as a the license text
        self.notice_file = join(self.src_dir, self.key + u'.NOTICE')
        # note: we do not keep the SPDX text if it is identical to the license
        # text
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
        Fields with empty values are not included.
        """
        data = OrderedDict()

        data[u'key'] = self.key
        if self.short_name:
            data[u'short_name'] = self.short_name
        if self.name:
            data[u'name'] = self.name

        if self.deprecated:
            data[u'deprecated'] = self.deprecated

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
         - <key>.NOTICE: the standard notice text if any
         - <key>.SPDX: the SPDX license text if any
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
        Unknown fields are ignored and not bound to the License object.
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

            if not lic.versions and (lic.or_later_version or lic.any_version or lic.any_version_default) :
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
_LICENSES = {}


def get_licenses():
    """
    Return a mapping of license key -> license object.
    """
    global _LICENSES
    if not _LICENSES :
        _LICENSES = load_licenses()
    return _LICENSES


def load_licenses(license_dir=licenses_data_dir , with_deprecated=False):
    """
    Return a mapping of key -> license objects, loaded from license files.
    """
    licenses = {}
    for data_file in file_iter(license_dir):
        if not data_file.endswith('.yml'):
            continue
        key = file_base_name(data_file)
        lic = License(key, license_dir)
        if not with_deprecated and lic.deprecated:
            continue
        licenses[key] = lic
    return licenses


def get_rules():
    """
    Return a list of all reference rules loaded from licenses and rules files.
    Raise a MissingLicenses exceptions if a rule references unknown license
    keys.
    """
    rls = list(chain(build_rules_from_licenses(), load_rules()))
    check_rules_integrity(rls)
    return rls


class MissingLicenses(Exception):
    pass


def check_rules_integrity(rules):
    """
    Given a lists of rules, check that all license keys reference a known
    license. Raise a MissingLicense exception with a message containing the list
    of rule files without a corresponding license.
    """
    invalid_rules = defaultdict(list)
    licenses = get_licenses()
    for rule in rules:
        for key in rule.licenses:
            if key not in licenses:
                invalid_rules[rule.data_file].append(key)
    if invalid_rules:
        invalid_rules = (data_file + ': ' + ' '.join(keys)
                         for data_file, keys in invalid_rules.iteritems())
        msg = 'Rules referencing missing licenses:\n' + '\n'.join(invalid_rules)
        raise MissingLicenses(msg)


def build_rules_from_licenses(licenses=None):
    """
    Return an iterable of rules built from each license text, notice and spdx
    text from a `licenses` iterable of license objects. Use the reference list
    if `licenses` is not provided.

    Load the reference license list from disk if `licenses` is not provided.
    """
    licenses = licenses or get_licenses()
    for license_key, license_obj in licenses.items():
        tfile = join(license_obj.src_dir, license_obj.text_file)
        if exists(tfile):
            yield Rule(text_file=tfile, licenses=[license_key])

        nfile = join(license_obj.src_dir, license_obj.notice_file)
        if exists(nfile):
            yield Rule(text_file=nfile, licenses=[license_key])

        sfile = join(license_obj.src_dir, license_obj.spdx_file)
        if exists(sfile):
            yield Rule(text_file=sfile, licenses=[license_key])


def load_rules(rule_dir=rules_data_dir):
    """
    Return an iterable of rules loaded from rule files.
    """
    # TODO: OPTIMIZE: create a graph of rules to account for containment and similarity clusters?
    # TODO: we should assign the rule id at that stage
    seen_files = set()
    processed_files = set()
    lower_case_files = set()
    case_problems = set()
    for data_file in file_iter(rule_dir):
        if data_file.endswith('.yml'):
            base_name = file_base_name(data_file)
            rule_file = join(rule_dir, base_name + '.RULE')
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
            msg = 'Unknown files in rule directory: %(rule_dir)r\n%(files)s'

        if case_problems:
            files = '\n'.join(sorted(case_problems))
            msg += '\nRule files with non-unique name ignoring casein rule directory: %(rule_dir)r\n%(files)s'

        raise Exception(msg % locals())


Thresholds = namedtuple('Thresholds',
                        ['high_len', 'low_len', 'length',
                         'small', 'min_high', 'min_len', 'max_gap_skip'])

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
                 'gaps', 'is_url'
                 )

    def __init__(self, data_file=None, text_file=None, licenses=None,
                 license_choice=False, notes=None, _text=None):

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
        self.license = u''

        # licensing identifier: TODO: replace with a license expression
        self.licensing_identifier = tuple(sorted(set(self.licenses))) + (license_choice,)

        # is this rule text a false positive when matched? (filtered out)
        self.false_positive = False

        # optional, free text
        self.notes = notes

        # path to the YAML data file for this rule
        self.data_file = data_file
        if data_file:
            self.load()

        # path to the rule text file
        self.text_file = text_file

        # for testing only, when we do not use a file
        self._text = _text

        # These attributes are computed when processing the rule text or during indexing

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

        # set of pos followed by a gap, aka a template part
        self.gaps = set()

        # is this rule text for a bare url? (needs exact matching)
        self.is_url = False

    def tokens(self, lower=True):
        """
        Return an iterable of token strings for this rule and keep track of gaps
        by position. Gaps and length are recomputed. Tokens inside gaps are
        tracked but not part of the returned stream.
        """
        # FIXME: we should cache these outside of the rule object, as a global
        gaps = set()
        # Note: we track the pos instead of enumerating it because we create
        # positions abstracting gaps
        pos = 0
        length = 0
        text = self.text()
        text = text.strip()

        # tag this rule as being a bare URL: this is used to determine a matching approach
        if text.startswith(('http://', 'https://', 'ftp://')) and '\n' not in text[:1000]:
            self.is_url = True

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
            raise Exception('Inconsistent rule text for:', self.identifier)

    def __repr__(self):
        idf = self.identifier
        ird = self.rid
        if TRACE_REPR:
            text = self.text()
        else:
            text = self.text()[:20] + '...'
        keys = self.licenses
        choice = self.license_choice
        fp = self.false_positive
        return 'Rule(%(idf)r, lics=%(keys)r, fp=%(fp)r, %(text)r)' % locals()

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
        return (not self.licenses) and (not self.false_positive)

    def small(self):
        """
        Is this a small rule? It needs special handling for detection.
        """
        SMALL_RULE = 15
        return self.length < SMALL_RULE or self.is_url

    def thresholds(self):
        """
        Return a Thresholds tuple considering every token occurrence.
        """
        if not self._thresholds:
            min_high = MIN_MATCH_HIGH_LENGTH
            min_len = MIN_MATCH_LENGTH
            max_gap_skip = MAX_GAP_SKIP

            # note: we cascade ifs from largest to smallest lengths
            if self.length < 30:
                min_high = self.high_length
                min_len = self.length // 2
                max_gap_skip = 1

            if self.length < 10:
                min_high = self.high_length
                min_len = self.length
                max_gap_skip = 1 if self.gaps else 0

            if self.is_url:
                min_high = self.high_length
                min_len = self.length
                max_gap_skip = 0

            self._thresholds = Thresholds(
                self.high_length, self.low_length, self.length,
                self.small(), min_high, min_len, max_gap_skip)
        return self._thresholds

    def thresholds_unique(self):
        """
        Return a Thresholds tuple considering only unique token occurrence.
        """
        if not self._thresholds_unique:
            min_high = int(min([self.high_unique // 2, MIN_MATCH_HIGH_LENGTH]))
            min_len = MIN_MATCH_LENGTH
            max_gap_skip = MAX_GAP_SKIP
            # note: we cascade IFs from largest to smallest lengths
            if self.length < 20:
                min_high = self.high_unique
                min_len = min_high
                max_gap_skip = 1

            if self.length < 10:
                min_high = self.high_unique
                if self.length_unique < 2:
                    min_len = self.length_unique
                else:
                    min_len = self.length_unique - 1
                max_gap_skip = 1 if self.gaps else 0

            if self.length < 5:
                min_high = self.high_unique
                min_len = self.length_unique
                max_gap_skip = 1 if self.gaps else 0

            if self.is_url:
                min_high = self.high_unique
                min_len = self.length_unique
                max_gap_skip = 0

            self._thresholds_unique = Thresholds(
                self.high_unique, self.low_unique, self.length_unique,
                self.small(), min_high, min_len, max_gap_skip)
        return self._thresholds_unique

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
        if self.license:
            data['license'] = self.license
        if self.false_positive:
            data['false_positive'] = self.false_positive
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
        # these are purely informational and not used at run time
        if load_notes:
            notes = data.get('notes')
            if notes:
                self.notes = notes.strip()
        return self


def _print_rule_stats():
    """
    Print rules statistics.
    """
    from licensedcode.index import get_index
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

    gaps = Counter(len(r.gaps) for r in rules if r.gaps)
    print('Top 15 gap counts: ', sorted(gaps.most_common(0),
                                        key=itemgetter(1), reverse=True))

    small_with_gaps = [(r.identifier, len(r.gaps)) for r in rules if r.gaps and r.small()]
    print('Small rules with gaps: ', small_with_gaps)
