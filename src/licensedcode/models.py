#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import sys
import traceback
from collections import Counter
from collections import defaultdict
from collections import OrderedDict
from hashlib import sha1
from itertools import chain
from operator import itemgetter
from os.path import abspath
from os.path import dirname
from os.path import exists
from os.path import join
from pathlib import Path

from licensedcode._vendor import attr
from license_expression import ExpressionError
from license_expression import Licensing
from saneyaml import load as saneyaml_load
from saneyaml import dump as saneyaml_dump

from commoncode.fileutils import file_base_name
from commoncode.fileutils import file_name
from commoncode.fileutils import resource_iter
from commoncode.text import python_safe_name
from licensedcode import MIN_MATCH_HIGH_LENGTH
from licensedcode import MIN_MATCH_LENGTH
from licensedcode import SMALL_RULE
from licensedcode.frontmatter import dumps_frontmatter
from licensedcode.frontmatter import load_frontmatter
from licensedcode.languages import LANG_INFO as known_languages
from licensedcode.tokenize import index_tokenizer
from licensedcode.tokenize import index_tokenizer_with_stopwords
from licensedcode.tokenize import query_lines
from scancode.api import SCANCODE_LICENSEDB_URL
from scancode.api import SCANCODE_LICENSE_URL
from scancode.api import SCANCODE_RULE_URL
from scancode.api import SPDX_LICENSE_URL

"""
Reference License and license Rule structures persisted as a combo of a YAML
data file and one or more text files containing license or notice texts.
"""

# Tracing flags
TRACE = False or os.environ.get('SCANCODE_DEBUG_LICENSE_MODELS', False)

# Set to True to print more detailed representations of objects when tracing
TRACE_REPR = False


def logger_debug(*args):
    pass


if TRACE:

    use_print = True

    if use_print:
        printer = print
    else:
        import logging

        logger = logging.getLogger(__name__)
        # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
        logging.basicConfig(stream=sys.stdout)
        logger.setLevel(logging.DEBUG)
        printer = logger.debug

    def logger_debug(*args):
        return printer(' '.join(isinstance(a, str) and a or repr(a) for a in args))

# these are globals but always side-by-side with the code so do no not move them around
data_dir = join(abspath(dirname(__file__)), 'data')
licenses_data_dir = join(data_dir, 'licenses')
rules_data_dir = join(data_dir, 'rules')

FOSS_CATEGORIES = set([
    'Copyleft',
    'Copyleft Limited',
    'Patent License',
    'Permissive',
    'Public Domain',
    'CLA',
])

OTHER_CATEGORIES = set([
    'Commercial',
    'Proprietary Free',
    'Free Restricted',
    'Source-available',
    'Unstated License',
])

CATEGORIES = FOSS_CATEGORIES | OTHER_CATEGORIES


@attr.s(slots=True)
class License:
    """
    A license consists of the following file, where <key> is the license key:
        - <key>.LICENSE: the license text and the license data in YAML frontmatter

    A License object is identified by a unique `key` and its data stored in the
    `src_dir` directory. Key is a lower-case unique ascii string.
    """

    key = attr.ib(
        repr=True,
        metadata=dict(
            help='Mandatory unique key: this is a lower case string with only '
            'ASCII characters, digits, underscore or dots.')
    )

    is_deprecated = attr.ib(
        default=False,
        repr=False,
        metadata=dict(
            help='Flag set to True if this is a deprecated license. '
            'The policy is to never delete a license key once attributed. '
            'Instead it can be marked as deprecated and will be ignored for '
            'detection. When marking a license as deprecated, add notes '
            'explaining why this is deprecated. And all license rules must be '
            'updated accordingly to point to a new license expression.')
    )

    language = attr.ib(
        default='en',
        repr=False,
        metadata=dict(
            help='Two-letter ISO 639-1 language code if this license text is '
            'not in English. See https://en.wikipedia.org/wiki/ISO_639-1 . '
            'NOTE: each translation of a license text MUST have a different '
            'license key. By convention, we append the language code to the '
            'license key')
        )

    short_name = attr.ib(
        default=None,
        repr=False,
        metadata=dict(
            help='Commonly used license short name, often abbreviated.')
    )

    name = attr.ib(
        default=None,
        repr=False,
        metadata=dict(
            help='License full name')
    )

    category = attr.ib(
        default=None,
        repr=False,
        metadata=dict(
            help='Category for this license. Use "Unstated License" if unknown. '
            'One of: ' + ', '.join(sorted(CATEGORIES)))
    )

    owner = attr.ib(
        default=None,
        repr=False,
        metadata=dict(
            help='Required owner or author for this license. '
            'Use "Unspecified" if unknown.')
    )

    homepage_url = attr.ib(
        default=None,
        repr=False,
        metadata=dict(
            help='Homepage URL for this license')
    )

    notes = attr.ib(
        default=None,
        repr=False,
        metadata=dict(
            help='Free text notes.')
    )

    is_builtin = attr.ib(
        default=True,
        repr=False,
        metadata=dict(
            help='Flag set to True if this is a builtin standard license.')
    )

    # TODO: add the license key(s) this exception applies to
    is_exception = attr.ib(
        default=False,
        repr=False,
        metadata=dict(
            help='Flag set to True if this is a license exception')
    )

    is_unknown = attr.ib(
        default=False,
        repr=False,
        metadata=dict(
            help='Flag set to True if this license is for some unknown licensing')
    )

    is_generic = attr.ib(
        default=False,
        repr=False,
        metadata=dict(
            help='Flag set to True if this license if for a generic, unnamed license')
    )

    spdx_license_key = attr.ib(
        default=None,
        repr=False,
        metadata=dict(
            help='SPDX short form license identifier. '
            'Use a LicenseRef-scancode-<license key> for licenses not listed in '
            'the SPDX licenses list')
    )

    other_spdx_license_keys = attr.ib(
        default=attr.Factory(list),
        repr=False,
        metadata=dict(
            help='List of other SPDX keys, such as the id of a deprecated '
            'license or alternative LicenseRef identifiers')
    )
    osi_license_key = attr.ib(
        default=None,
        repr=False,
        metadata=dict(
            help='OSI License key if available')
    )

    text_urls = attr.ib(
        default=attr.Factory(list),
        repr=False,
        metadata=dict(
            help='Text URL for this license')
    )

    osi_url = attr.ib(
        default=None,
        repr=False,
        metadata=dict(
            help='OpenSource.org URL for this license')
    )

    faq_url = attr.ib(
        default=None,
        repr=False,
        metadata=dict(
            help='Frequently Asked Questions page URL for this license')
    )

    other_urls = attr.ib(
        default=attr.Factory(list),
        repr=False,
        metadata=dict(
            help='A list of other interesting URLs for this license')
    )

    key_aliases = attr.ib(
        default=attr.Factory(list),
        repr=False,
        metadata=dict(
            help='List of alternative license keys for this license')
    )

    minimum_coverage = attr.ib(
        default=0,
        repr=False,
        metadata=dict(
            help='Can this license text be matched only with a minimum coverage e.g., '
            'when a minimum proportion of tokens have been matched? This is as a '
            'float between 0 and 100 where 100 means that all tokens must be '
            'matched and a smaller value means a smaller proportion of matched '
            'tokens is acceptable. This is mormally computed at indexing time based on '
            'the length of a license. Providing a stored value in the license data '
            'file overrides this default computed value. For example, a short '
            'license notice such as "MIT license" must be matched with all its words, '
            'e.g., a 100 minimum_coverage. Otherwise matching only "mit" or '
            '"license" is not a strong enough licensing clue.')
    )

    standard_notice = attr.ib(
        default=None,
        repr=False,
        metadata=dict(
            help='Standard notice text for this license.')
    )

    ###########################################################################
    # lists of clues that can be ignored when detected in this license as they
    # are part of the license or rule text itself

    ignorable_copyrights = attr.ib(
        default=attr.Factory(list),
        repr=False,
        metadata=dict(
            help='List of copyrights that can be ignored when detected in this '
            'text as they are part of the license or rule text proper and can'
            'optionally be excluded from the copyrights detection')
    )

    ignorable_holders = attr.ib(
        default=attr.Factory(list),
        repr=False,
        metadata=dict(
            help='List of holders that can be ignored when detected in this '
            'text as they are part of the license or rule text proper and can'
            'optionally be excluded from the holders detection')
    )

    ignorable_authors = attr.ib(
        default=attr.Factory(list),
        repr=False,
        metadata=dict(
            help='List of authors that can be ignored when detected in this '
            'text as they are part of the license or rule text proper and can'
            'optionally be excluded from the authors detection')
    )

    ignorable_urls = attr.ib(
        default=attr.Factory(list),
        repr=False,
        metadata=dict(
            help='List of holders that can be ignored when detected in this '
            'text as they are part of the license or rule text proper and can'
            'optionally be excluded from the holders detection')
    )

    ignorable_emails = attr.ib(
        default=attr.Factory(list),
        repr=False,
        metadata=dict(
            help='List of emails that can be ignored when detected in this '
            'text as they are part of the license or rule text proper and can'
            'optionally be excluded from the emails detection')
    )

    text = attr.ib(
        default=None,
        repr=False,
        metadata=dict(
            help='License text.')
    )

    @classmethod
    def from_dir(cls, key, licenses_data_dir=licenses_data_dir, check_consistency=True, is_builtin=True):
        """
        Return a new License object for a license ``key`` and load its attribute
        from a data file stored in ``licenses_data_dir``.
        """
        lic = cls(key=key, is_builtin=is_builtin)
        license_file = lic.license_file(licenses_data_dir=licenses_data_dir)
        lic.load(license_file=license_file, check_consistency=check_consistency)
        return lic

    @property
    def scancode_url(self):
        if self.is_builtin:
            return SCANCODE_LICENSE_URL.format(self.key)

    @property
    def licensedb_url(self):
        if self.is_builtin:
            return SCANCODE_LICENSEDB_URL.format(self.key)

    @property
    def spdx_url(self):
        """
        Return a URL to the SPDX license either at SPDX, ScanCode or None.
        """
        if self.is_builtin:
            spdx_license_key = self.spdx_license_key
            if not spdx_license_key:
                return

            slkl = spdx_license_key.lower()
            is_licenseref = slkl.startswith('licenseref-')

            if is_licenseref:
                return SCANCODE_LICENSE_URL.format(self.key)
            else:
                # TODO: Is this replacing spdx_key???
                spdx_license_key = spdx_license_key.rstrip('+')
                return SPDX_LICENSE_URL.format(spdx_license_key)

    def license_file(self, licenses_data_dir=licenses_data_dir):
        return join(licenses_data_dir, f'{self.key}.LICENSE')

    def update(self, mapping):
        for k, v in mapping.items():
            setattr(self, k, v)

    def __copy__(self):
        oldl = self.to_dict()
        newl = License(key=self.key)
        newl.update(oldl)
        return newl

    def _to_dict(self, include_field):
        """
        Return a mapping of license data.
        ``include_field(name, value)`` is a callable that will be called with
        each name, value pair and returns True to include the field or False
        to filter it.
        """
        data = {}
        for name, value in attr.asdict(self).items():
            if not include_field(name, value):
                continue
            data[name] = value
        return data

    def to_dict(
        self,
        include_ignorables=True,
        include_text=False,
        include_builtin=True,
    ):
        """
        Return a mapping of license data. Skip fields with empty values.
        Optionally include:
        - the "ignorable*" attributes if ``include_ignorables`` is True.
        - the text ``include_text`` is True.
        - the ``is_builtin`` flag if ``include_builtin`` is True.
        """

        # do not include false, epties and paths
        def include_field(name, value):
            if not value:
                return False
            if isinstance(value, str) and not value.strip():
                return False
            # default to English which is implied
            if name == 'language' and value == 'en':
                return False
            if name == 'minimum_coverage' and value == 100:
                return False
            if not include_builtin and name == 'is_builtin':
                return False
            if not include_ignorables and  name.startswith('ignorable_'):
                return False
            if not include_text and  name == 'text':
                return False

            return True

        return self._to_dict(include_field=include_field)

    def to_reference(self):
        """
        Return a mapping of license reference data.
        """
        # include everything
        data = self._to_dict(include_field=lambda k, v: True)
        data.pop('is_deprecated', None)
        data['scancode_url'] = self.scancode_url
        data['licensedb_url'] = self.licensedb_url
        data['spdx_url'] = self.spdx_url
        return data

    def dump(self, licenses_data_dir):
        """
        Dump a representation of this license as a .LICENSE file with:
         - the license data as YAML frontmatter
         - the license text
        """
        metadata = self.to_dict(include_builtin=False)
        content = self.text
        # We add a space to empty newlines to make this text YAML safe
        content = get_yaml_safe_text(content)
        output = dumps_frontmatter(content=content, metadata=metadata)
        license_file = self.license_file(licenses_data_dir=licenses_data_dir)
        with open(license_file, 'w') as of:
            of.write(output)

    def load(self, license_file, check_consistency=True):
        """
        Populate license data from a .LICENSE file stored as a YAML frontmatter.
        Does not load text files yet.
        Unknown fields are ignored and not bound to the License object.
        """
        try:
            content, data = load_frontmatter(license_file)
            if check_consistency:
                if not data:
                    raise InvalidLicense(
                        f'Cannot load License with empty YAML frontmatter: '
                        f'{self}: file://{license_file}'
                    )

            if not content:
                if check_consistency:
                    if not any(
                        attribute in data
                        for attribute in ('is_deprecated', 'is_generic', 'is_unknown')
                    ):
                        raise InvalidLicense(
                            f'Cannot load License with empty text: '
                            f'only deprecated, generic or unknown licenses can exist without text '
                            f'{self}: file://{license_file}'
                        )

                self.text = ''
            else:
                self.text = content.lstrip("\n")

            for k, v in data.items():
                if k == 'minimum_coverage':
                    v = as_int(v)

                if k == 'key':
                    assert self.key == v, (
                        'The license "key" attribute in the YAML frontmatter MUST ' +
                        'be the same as the base name of this .LICENSE ' +
                        'license file. ' +
                        f'Yet file name = {self.key} and license key = {v}'
                    )

                setattr(self, k, v)

        except Exception as e:
            # this is a rare case: fail loudly
            print()
            print('#############################')
            print('INVALID LICENSE YAML FILE:', f'file://{self.license_file}')
            print('#############################')
            print(traceback.format_exc())
            print('#############################')
            raise e
        return self

    def spdx_keys(self):
        """
        Yield SPDX keys for this license.
        """
        if self.spdx_license_key:
            yield self.spdx_license_key
        for key in self.other_spdx_license_keys:
            yield key

    @staticmethod
    def validate(licenses, verbose=False, no_dupe_urls=False, thorough=False):
        """
        Check that the ``licenses`` a mapping of {key: License} are valid.
        Return dictionaries of infos, errors and warnings mapping a license key
        to validation issue messages. Print messages if ``verbose`` is True.

        NOTE: we DO NOT run this validation as part of loading or constructing
        License objects. Instead this is invoked ONLY as part of the test suite.
        """
        infos = defaultdict(list)
        warnings = defaultdict(list)
        errors = defaultdict(list)

        # used for global dedupe of texts
        by_spdx_key_lowered = defaultdict(list)
        by_text = defaultdict(list)
        by_short_name_lowered = defaultdict(list)
        by_name_lowered = defaultdict(list)

        for key, lic in licenses.items():
            warn = warnings[key].append
            info = infos[key].append
            error = errors[key].append
            if lic.name:
                by_name_lowered[lic.name.lower()].append(lic)
            else:
                by_name_lowered[lic.name].append(lic)
            if lic.short_name:
                by_short_name_lowered[lic.short_name.lower()].append(lic)
            else:
                by_short_name_lowered[lic.short_name].append(lic)

            if lic.key != lic.key.lower():
                error('Incorrect license key case: must be all lowercase.')

            if len(lic.key) > 50:
                error('key must be 50 characters or less.')

            if '_'in lic.key:
                error('key cannot contain an underscore: this is not valid in SPDX.')

            if not lic.short_name:
                error('No short name')
            elif len(lic.short_name) > 50:
                error('short name must be 50 characters or less.')

            if not lic.name:
                error('No name')

            if not lic.category:
                error('No category: Use "Unstated License" if not known.')
            if lic.category and lic.category not in CATEGORIES:
                cats = '\n'.join(sorted(CATEGORIES))
                error(
                    f'Unknown license category: {lic.category}.\n' +
                    f'Use one of these valid categories:\n{cats}'
                )

            if not lic.owner:
                error('No owner: Use "Unspecified" if not known.')

            if lic.language not in known_languages:
                error(f'Unknown language: {lic.language}')

            if lic.is_unknown:
                if not 'unknown' in lic.key and lic.key != 'no-license':
                    error(
                        'is_unknown can be true only for licenses with '
                        '"unknown " in their key string.'
                    )

            if lic.is_generic and lic.is_unknown:
                error('is_generic and is_unknown flags are incompatible')

            # URLS dedupe and consistency
            if no_dupe_urls:
                if lic.text_urls and not all(lic.text_urls):
                    warn('Some empty text_urls values')

                if lic.other_urls and not all(lic.other_urls):
                    warn('Some empty other_urls values')

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
                    if url:
                        all_licenses.append(url)

                if not len(all_licenses) == len(set(all_licenses)):
                    warn('Some duplicated URLs')

            text = lic.text
            if thorough:
                # local text consistency
                data = {"text": text}
                # We are testing whether we can dump as yaml and load from yaml
                # without failing (i.e. whether the text is yaml safe)
                # Using saneyaml
                try:
                    yaml_string = saneyaml_dump(data)
                    loaded_yaml = saneyaml_load(yaml_string)
                except Exception:
                    errors['GLOBAL'].append(
                        f'Error invalid YAML text at: {lic.key}, failed during saneyaml.load()'
                        'Run scancode-reindex-licenses --load-dump to fix this.'
                    )
                # This fails because of missing line break at text end, added by saneyaml_dump
                # assert text == loaded_yaml["text"]

            license_itokens = tuple(index_tokenizer(text))
            if not license_itokens:
                info('No license text')
            else:
                # for global dedupe
                by_text[license_itokens].append(f'{key}: TEXT')

            # SPDX consistency
            if lic.spdx_license_key:
                if len(lic.spdx_license_key) > 50:
                    error('spdx_license_key must be 50 characters or less.')

                by_spdx_key_lowered[lic.spdx_license_key.lower()].append(key)
            else:
                # SPDX license key is now mandatory
                error('No SPDX license key')

            for oslk in lic.other_spdx_license_keys:
                by_spdx_key_lowered[oslk].append(key)

        # global SPDX consistency
        multiple_spdx_keys_used = {
            k: v for k, v in by_spdx_key_lowered.items()
            if len(v) > 1
        }

        if multiple_spdx_keys_used:
            for k, lkeys in multiple_spdx_keys_used.items():
                errors['GLOBAL'].append(
                    f'SPDX key: {k} used in multiple licenses: ' +
                    ', '.join(sorted(lkeys)))

        # global text dedupe
        multiple_texts = {k: v for k, v in by_text.items() if len(v) > 1}
        if multiple_texts:
            for k, msgs in multiple_texts.items():
                errors['GLOBAL'].append(
                    'Duplicate texts in multiple licenses: ' +
                    ', '.join(sorted(msgs))
                )

        # global short_name dedupe
        for short_name, licenses in by_short_name_lowered.items():
            if len(licenses) == 1:
                continue
            errors['GLOBAL'].append(
                f'Duplicate short name (ignoring case): {short_name} in licenses: ' +
                ', '.join(sorted(l.key for l in licenses))
            )

        # global name dedupe
        for name, licenses in by_name_lowered.items():
            if len(licenses) == 1:
                continue
            errors['GLOBAL'].append(
                f'Duplicate name (ignoring case): {name} in licenses: ' +
                ', '.join(sorted(l.key for l in licenses))
            )

        errors = {k: v for k, v in errors.items() if v}
        warnings = {k: v for k, v in warnings.items() if v}
        infos = {k: v for k, v in infos.items() if v}

        if verbose:
            print('Licenses validation errors:')
            for key, msgs in sorted(errors.items()):
                print(f'ERRORS for: {key}:', '\n'.join(msgs))

            print('Licenses validation warnings:')
            for key, msgs in sorted(warnings.items()):
                print(f'WARNINGS for: {key}:', '\n'.join(msgs))

            print('Licenses validation infos:')
            for key, msgs in sorted(infos.items()):
                print(f'INFOS for: {key}:', '\n'.join(msgs))

        return errors, warnings, infos


def get_yaml_safe_text(text):
    """
    Given a `text` string return a YAML-safe version of the
    string suitable for use in a YAML output, i.e. that would not
    produce a invalid yaml if used in the output.

    This is done by trying to dump and load the text inside a data
    dictionary and if it fails, padding all the empty newlines with
    a space.
    """
    data = {"text": text}
    yaml_string = saneyaml_dump(data)
    try:
        loaded_yaml = saneyaml_load(yaml_string)
    except Exception:
        text = text.replace('\n\n', '\n \n')
    return text


def ignore_editor_tmp_files(location):
    return location.endswith('.swp')


def load_licenses(
    licenses_data_dir=licenses_data_dir,
    with_deprecated=False,
    check_consistency=True,
    is_builtin=True,
):
    """
    Return a mapping of {key: License} loaded from license data and text files
    found in ``licenses_data_dir``. Raise Exceptions if there are dangling or
    orphaned files.
    Optionally include deprecated license if ``with_deprecated`` is True.
    Optionally check for dangling orphaned files if ``check_dangling`` is True.
    """

    all_files = list(resource_iter(
        location=licenses_data_dir,
        ignored=ignore_editor_tmp_files,
        with_dirs=False,
        follow_symlinks=True,
    ))

    licenses = {}

    for license_file in all_files:
        if license_file.endswith('.LICENSE'):
            if TRACE:
                logger_debug('load_licenses: license_file:', license_file)

            key = file_base_name(license_file)

            try:
                lic = License.from_dir(
                    key=key,
                    licenses_data_dir=licenses_data_dir,
                    check_consistency=check_consistency,
                    is_builtin=is_builtin,
                )
            except Exception as e:
                msg = (
                    f'Failed to load license: {key} from: '
                    f'file://{licenses_data_dir}/{key}.LICENSE with error: {e}'
                )
                raise InvalidLicense(msg) from e

            if not with_deprecated and lic.is_deprecated:
                continue

            licenses[key] = lic

    if not licenses:
        msg = (
            'No licenses were loaded. Check to see if the license data files '
            f'are available at "{licenses_data_dir}".'
        )
        raise InvalidLicense(msg)

    return licenses


def get_rules(
    licenses_db=None,
    licenses_data_dir=licenses_data_dir,
    rules_data_dir=rules_data_dir,
    validate=False,
    validate_thorough=False,
    is_builtin=True,
):
    """
    Yield Rule objects loaded from a ``licenses_db`` and license files found in
    ``licenses_data_dir`` and rule files found in `rules_data_dir`. Raise an
    Exception if a rule is inconsistent or incorrect.

    If ``validate`` flag is True, we validate all the license rules for consistency
    and if ``validate_thorough`` is True we perform additional validation tests
    (like whether it would produce valid YAML) which is skipped normally because these
    are expensive operations.
    """
    licenses_db = licenses_db or load_licenses(
        licenses_data_dir=licenses_data_dir,
    )

    rules = list(load_rules(
        rules_data_dir=rules_data_dir,
        is_builtin=is_builtin,
    ))

    if validate:
        validate_rules(rules=rules, licenses_by_key=licenses_db, thorough=validate_thorough)

    licenses_as_rules = build_rules_from_licenses(licenses_db)
    return chain(licenses_as_rules, rules)


def load_dump_licenses():
    """
    Loads all licenses and rules and dumps them in the same file.
    This is used to do minor formatting changes consistently across
    all licenses/rules.
    """
    licenses = load_licenses(licenses_data_dir=licenses_data_dir)
    for lic in licenses.values():
        lic.dump(licenses_data_dir)

    rules = list(load_rules(rules_data_dir=rules_data_dir))
    for rule in rules:
        rule.dump(rules_data_dir=rules_data_dir)


def get_license_dirs(additional_dirs):
    """
    Return a list of all subdirectories containing license files within the
    input list of additional directories. These directories do not have to be absolute paths.
    """
    return [f"{str(Path(path).absolute())}/licenses" for path in additional_dirs]


def get_rule_dirs(additional_dirs):
    """
    Return a list of all subdirectories containing rule files within the
    input list of additional directories. These directories do not have to be absolute paths.
    """
    return [f"{str(Path(path).absolute())}/rules" for path in additional_dirs]


def get_paths_to_installed_licenses_and_rules():
    """
    Return a list of paths to externally packaged licenses or rules that the user has
    installed. Gets a list of all of these licenses (installed as plugins) and
    then gets the plugins containing licenses by checking that their names start
    with a common prefix.
    """
    from importlib_metadata import entry_points
    from licensedcode.additional_license_location_provider import get_location
    installed_plugins = entry_points(group='scancode_additional_license_location_provider')
    paths = []
    for plugin in installed_plugins:
        # get path to directory of licenses and/or rules
        paths.append(get_location(plugin.name))
    return paths


def load_licenses_from_multiple_dirs(
    builtin_license_data_dir,
    additional_license_data_dirs,
    with_deprecated=False,
):
    """
    Return a mapping of {key: License} combining a list of
    ``additional_license_data_dirs`` containing additional licenses with the
    builtin ``builtin_license_data_dir`` licenses into the same mapping.
    """
    combined_licenses = load_licenses(
        licenses_data_dir=builtin_license_data_dir,
        with_deprecated=with_deprecated,
        is_builtin=True,
    )
    for license_dir in additional_license_data_dirs:
        additional_licenses = load_licenses(
            licenses_data_dir=license_dir,
            with_deprecated=with_deprecated,
            is_builtin=False,
        )

        # validate that additional licenses keys do not exist as builtin
        duplicate_keys = set(combined_licenses).intersection(set(additional_licenses))
        if duplicate_keys:
            dupes = ', '.join(sorted(duplicate_keys))
            message = f'Duplicate licenses found when loading additional licenses from: {license_dir}: {dupes}'
            raise ValueError(message)

        combined_licenses.update(additional_licenses)

    return combined_licenses


def get_rules_from_multiple_dirs(
    licenses_db,
    builtin_rule_data_dir,
    additional_rules_data_dirs,
):
    """
    Yield Rule(s) built from:
    - A ``license_db`` mapping of {key: License}
    - The ``builtin_rule_data_dir`` of builtin license rules
    - The list of ``additional_rules_data_dirs`` containing additional rules.
    """
    # first load all builtin
    combined_rules = list(get_rules(
        licenses_db=licenses_db,
        rules_data_dir=builtin_rule_data_dir,
    ))

    # load additional rules
    for rules_dir in additional_rules_data_dirs or []:
        combined_rules.extend(load_rules(
            rules_data_dir=rules_dir,
            is_builtin=False,
        ))

    validate_rules(rules=combined_rules, licenses_by_key=licenses_db, thorough=False)

    return combined_rules


def validate_additional_license_data(additional_directories, scancode_license_dir):
    """
    Raises an exception if there are any invalid licenses in the directories of
    additional licenses.
    """
    licenses = load_licenses_from_multiple_dirs(
        additional_license_data_dirs=additional_directories,
        builtin_license_data_dir=scancode_license_dir
    )
    errors, _, _ = License.validate(
        licenses,
        verbose=False,
    )
    if errors:
        message = ['Errors while validating licenses:']
        for key, msgs in errors.items():
            message.append('')
            message.append(f'License: {key}')
            for msg in msgs:
                message.append(f'  {msg!r}')
        raise InvalidLicense('\n'.join(message))


def _ignorable_clue_error(rule, rules_dir):
    """
    Return a pair of the result of validating a rule's ignorable clues and expected ignorable clues
    if there is an error. Otherwise, returns None.
    """
    result = get_ignorables(rule.rule_file(rules_data_dir=rules_dir))
    expected = get_normalized_ignorables(rule)
    if result != expected:
        rule_file = rule.rule_file(rules_data_dir=rules_dir)

        result['files'] = [
            f'file://{rule_file}',
        ]
        return result, expected


def validate_ignorable_clues(rule_directories, is_builtin):
    """
    Raises an exception if any ignorable clues declared in a Rule are improperly detected
    in the rule text file.
    """
    messages = ['Errors while validating ignorable rules:']
    error_present = False
    for rules_dir in rule_directories:
        r = list(load_rules(
            rules_data_dir=rules_dir,
            is_builtin=is_builtin,
        ))
        for rule in r:
            if _ignorable_clue_error(rule, rules_dir):
                error_present = True
                result, expected = _ignorable_clue_error(rule, rules_dir)
                messages.append('')
                messages.append(f'{rule!r}')
                messages.append('Result:')
                messages.append(result)
                messages.append('Expected:')
                messages.append(expected)
    if error_present:
        raise InvalidRule('\n'.join(messages))


class InvalidRule(Exception):
    pass


class InvalidLicense(Exception):
    pass


def _validate_all_rules(rules, licenses_by_key, thorough=False):
    """
    Return a mapping of {error message: [list of Rule]} from validating a list
    of ``rules`` Rule integrity and correctness using known licenses from a
    mapping of ``licenses_by_key`` {key: License}`.
    """
    licensing = Licensing(symbols=licenses_by_key.values())
    errors = defaultdict(list)

    for rule in rules:
        for err_msg in rule.validate(licensing, thorough=thorough):
            errors[err_msg].append(rule)
    return errors


def validate_rules(rules, licenses_by_key, with_text=False, rules_data_dir=rules_data_dir, thorough=False):
    """
    Return a mapping of {error message: [list of Rule]) from validating a list
    of ``rules`` Rule integrity and correctness using known licenses from a
    mapping of ``licenses_by_key`` {key: License}`.
    """
    errors = _validate_all_rules(rules=rules, licenses_by_key=licenses_by_key, thorough=thorough)
    if errors:
        message = ['Errors while validating rules:']
        for msg, rules in errors.items():
            message.append('')
            message.append(msg)
            for rule in rules:
                message.append(f'  {rule!r}')

                if rule.identifier:
                    rule_file = rule.rule_file(rules_data_dir=rules_data_dir)
                    if rule_file and exists(rule_file):
                        message.append(f'    file://{rule_file}')

                if with_text:
                    txt = rule.text[:100].strip()
                    message.append(f'       {txt}...')
        raise InvalidRule('\n'.join(message))


def build_rules_from_licenses(licenses_by_key):
    """
    Return an iterable of rules built from each license text from a
    ``licenses_by_key`` mapping of {key: License}.
    """
    for license_obj in licenses_by_key.values():
        rule = build_rule_from_license(license_obj=license_obj)
        if rule:
            yield rule


def build_rule_from_license(license_obj):
    """
    Return a Rule built from a ``license_obj`` License object, or None.
    """
    if license_obj.text:
        minimum_coverage = license_obj.minimum_coverage or 0
        rule = Rule(
            license_expression=license_obj.key,
            identifier=f'{license_obj.key}.LICENSE',
            text=get_rule_text(text=license_obj.text),
            # a license text is always 100% relevant
            has_stored_relevance=True,
            relevance=100,

            has_stored_minimum_coverage=bool(minimum_coverage),
            minimum_coverage=minimum_coverage,

            is_builtin=license_obj.is_builtin,
            is_from_license=True,
            is_license_text=True,

            ignorable_copyrights=license_obj.ignorable_copyrights,
            ignorable_holders=license_obj.ignorable_holders,
            ignorable_authors=license_obj.ignorable_authors,
            ignorable_urls=license_obj.ignorable_urls,
            ignorable_emails=license_obj.ignorable_emails,
        )
        rule.setup()
        return rule


def get_rule_text(location=None, text=None):
    """
    Return the rule ``text`` prepared for indexing.
    ###############
    # IMPORTANT: we use the same process as used to load query text for symmetry
    ###############
    """
    numbered_lines = query_lines(location=location, query_string=text, plain_text=True)
    return '\n'.join(l.strip() for _, l in numbered_lines)


def get_all_spdx_keys(licenses_db):
    """
    Return an iterable of SPDX license keys collected from a `licenses_db`
    mapping of {key: License} objects.
    """
    for lic in licenses_db.values():
        for spdx_key in lic.spdx_keys():
            yield spdx_key


def get_essential_spdx_tokens():
    """
    Yield essential SPDX tokens.
    """
    yield from ('spdx', 'license', 'licence', 'identifier', 'licenseref',)


def get_all_spdx_key_tokens(licenses_db):
    """
    Yield SPDX token strings collected from a ``licenses_db`` mapping of {key:
    License} objects.
    """
    for tok in get_essential_spdx_tokens():
        yield tok

    for spdx_key in get_all_spdx_keys(licenses_db):
        for token in index_tokenizer(spdx_key):
            yield token


def get_license_tokens():
    """
    Yield key license tokens.
    """
    yield 'license'
    yield 'licence'
    yield 'licensed'


def load_rules(
    rules_data_dir=rules_data_dir,
    with_checks=True,
    is_builtin=True,
    with_depreacted=False,
):
    """
    Return an iterable of rules loaded from rule files in ``rules_data_dir``.
    Optionally check for consistency if ``with_checks`` is True.
    """
    # TODO: OPTIMIZE: create a graph of rules to account for containment and
    # similarity clusters?
    seen_files = set()
    processed_files = set()
    lower_case_files = set()
    case_problems = set()
    space_problems = []
    model_errors = []

    for rule_file in resource_iter(location=rules_data_dir, with_dirs=False):
        if rule_file.endswith('.RULE'):
            base_name = file_base_name(rule_file)

            if with_checks and ' ' in base_name:
                space_problems.append(rule_file)

            try:
                rule = Rule.from_file(rule_file=rule_file)
                if not with_depreacted and rule.is_deprecated:
                    continue 
                else:
                    yield rule

            except Exception as re:
                if with_checks:
                    model_errors.append(str(re))

            if with_checks:
                # accumulate sets to ensures we do not have illegal names or extra
                # orphaned files
                rule_file_lower = rule_file.lower()
                if rule_file_lower in lower_case_files:
                    case_problems.add(rule_file_lower)
                else:
                    lower_case_files.add(rule_file_lower)

                processed_files.add(rule_file)

        if with_checks and not rule_file.endswith('~'):
            seen_files.add(rule_file)

    if with_checks:
        unknown_files = seen_files - processed_files
        if unknown_files or case_problems or model_errors or space_problems:
            msg = ''

            if model_errors:
                errors = '\n'.join(model_errors)
                msg += (
                    '\nInvalid rule files: '
                    f'{rules_data_dir!r}\n'
                    f'{errors!r}\n'
                )

            if unknown_files:
                files = '\n'.join(sorted(f'file://{f}"' for f in unknown_files))
                msg += (
                    '\nOrphaned files in rule directory: '
                    f'{rules_data_dir!r}\n'
                    f'{files!r}\n'
                )

            if case_problems:
                files = '\n'.join(sorted(f'"file://{f}"' for f in case_problems))
                msg += (
                    '\nRule files with non-unique name in rule directory: '
                    f'{rules_data_dir!r}\n'
                    f'{files!r}\n'
                )

            if space_problems:
                files = '\n'.join(sorted(f'"file://{f}"' for f in space_problems))
                msg += (
                    '\nRule filename cannot contain spaces: '
                    f'{rules_data_dir!r}\n'
                    f'{files!r}\n'
                )

            raise InvalidRule(msg)


@attr.s(slots=True)
class BasicRule:
    """
    A detection rule object is a text to use for detection and corresponding
    detected licenses and metadata. This is a basic metadata object that does
    not have specific support for data and text files.
    """
    licensing = Licensing()

    rid = attr.ib(
        default=None,
        repr=TRACE_REPR,
        metadata=dict(
            help='Internal rule id number, assigned automatically at indexing '
            'time')
    )

    identifier = attr.ib(
        default=None,
        metadata=dict(
            help='Unique identifier for this rule, assigned automatically at '
            'indexing time. It is typically the rule ''text file name such as '
            '"gpl-2.0_12.RULE" or the license text file name such as '
            '"gpl-2.0.LICENSE". For dynamically generated rules (such as for '
            'SPDX identifier expressions, this is a string compued based on the '
            'expression')
    )

    license_expression = attr.ib(
        default=None,
        metadata=dict(
            help='License expression string to report when this rule is matched '
            'using the SPDX license expression syntax and ScanCode license keys.')
    )

    license_expression_object = attr.ib(
        default=None,
        repr=False,
        metadata=dict(
            help='license_expression LicenseExpression object, computed and '
            'cached automatically at creation time from the license_expression '
            'string.')
    )

    is_builtin = attr.ib(
        default=True,
        repr=False,
        metadata=dict(
            help='Flag set to True if this is a builtin standard rule.')
    )

    # The is_license_xxx flags below are an indication of what this rule
    # represents and its relative importance is, e.g., how important is the rule
    # text when detected as a licensing clue as one of several "is_license_xxx"
    # flags. These flags are mutually exclusive and a license rule can only have
    # one of these as flags with a True value.

    is_license_text = attr.ib(
        default=False,
        repr=False,
        metadata=dict(
            help='True if this is rule text is a license full text: full texts '
            'provide the highest level of confidence when detected because they '
            'are longer and more explicit. Mutually exclusive from any other '
            'is_license_* flag')
    )

    is_license_notice = attr.ib(
        default=False,
        repr=False,
        metadata=dict(
            help='True if this is rule text is a license notice: notices '
            'are explicit texts such as "Licensed under the MIT license" that '
            'are not actual license texts and provide a strong level of '
            'confidence when detected because they explicit. Mutually exclusive '
            'from any other is_license_* flag')
    )

    is_license_reference = attr.ib(
        default=False,
        repr=False,
        metadata=dict(
            help='True if this is rule text is a mre reference to a license: '
            'short license references such as a license bare name or license '
            'or a URL provide a weaker clue and level of confidence when '
            'detected because they are shorter and may not always represent a '
            'clear licensing statment or notice. Mutually exclusive from any other '
            'is_license_* flag')
    )

    is_license_tag = attr.ib(
        default=False,
        repr=False,
        metadata=dict(
            help='True if this is rule text is for a license tag: tags '
            'for a structured licensing tag such as a package manifest medata '
            'or an SPDX license identifier and similar tag conventions used in '
            'code or documentation. When detected, a tag provides a strong clue '
            'with high confidence even though it may be very short. '
            'Mutually exclusive from any other is_license_* flag')
    )

    is_license_intro = attr.ib(
        default=False,
        repr=False,
        metadata=dict(
            help='True if this is rule text is a license introduction: '
            'An intro is a short introductory statement placed just before an '
            'actual license text, notice or reference that it introduces. For '
            'instance "Licensed under ..." would be an intro text typically '
            'followed by some license notice. An "intro" is a weak clue that '
            'there may be some license statement afterwards. It should be '
            'considered in the context of the detection that it precedes. '
            'Ideally it should be merged with the license detected immediately '
            'after. Mutually exclusive from any other is_license_* flag')
    )

    is_license_clue = attr.ib(
        default=False,
        repr=False,
        metadata=dict(
            help='True if this is rule text is a clue to a license '
            'but cannot be considered in a proper license detection '
            'as a license text/notice/reference/tag/intro as it is'
            'merely a clue and does not actually point to or refer to '
            'the actual license directly. This is still valuable information '
            'useful in determining the license/origin of a file, but this '
            'should not be summarized/present in the license expression for '
            'a package or a file, nor its list of license detections. '
            'considered in the context of the detection that it precedes. '
            'Mutually exclusive from any other is_license_* flag')
    )

    is_false_positive = attr.ib(
        default=False,
        repr=False,
        metadata=dict(
            help='True if this rule text a false positive when matched exactly '
            '(ignoring unknown or stopwords) If set, matches to this rule will '
            'be discarded out at the end of the matching pipeline, except when '
            'contained in a larger match. When using this flag, a rule can only '
            'have notes explaining why this is a false positive and no other '
            'fields. This is useful in some cases when some text looks like a '
            'license text, notice or tag but is not actually it. '
            'Mutually exclusive from any is_license_* flag')
    )

    language = attr.ib(
        default='en',
        repr=False,
        metadata=dict(
            help='Two-letter ISO 639-1 language code if this license text is '
            'not in English. See https://en.wikipedia.org/wiki/ISO_639-1 .')
        )

    minimum_coverage = attr.ib(
        default=0,
        metadata=dict(
            help='Can this rule text be matched only with a minimum coverage e.g., '
            'when a minimum proportion of tokens have been matched? This is as a '
            'float between 0 and 100 where 100 means that all tokens must be '
            'matched and a smaller value means a smaller proportion of matched '
            'tokens is acceptable. This is computed at indexing time based on '
            'the length of a rule. Providing a stored value in the rule data '
            'file overrides this default computed value. For example, a short '
            'rule such as "MIT license" must be matched with all its words, '
            'e.g., a 100 minimum_coverage. Otherwise matching only "mit" or '
            '"license" is not a strong enough licensing clue.')
    )

    has_stored_minimum_coverage = attr.ib(
        default=False,
        repr=False,
        metadata=dict(
            help='Computed flag set to True if the "minimum_coverage" field is stored '
            'in this rule data file. The default is to have "minimum_coverage" computed'
            'and not stored.')
    )

    _minimum_containment = attr.ib(
        default=0,
        repr=False,
        metadata=dict(
            help='Internal cached field; a float computed from minimum_coverage, '
            'divided by 100.')
    )

    is_continuous = attr.ib(
        default=False,
        metadata=dict(
            help='Can this rule be matched if there are any gaps between matched '
            'words in its matched range? The default is to allow non-continuous '
            'approximate matches. Any extra unmatched known or unknown word is '
            'considered to break a match continuity. This attribute is either '
            'stored or computed when the whole rule text is a {{key phrase}}.')
    )

    relevance = attr.ib(
        default=100,
        metadata=dict(
            help='What is the relevance of a match to this rule text? This is a '
            'float between 0 and 100 where 100 means highly relevant and 0 means '
            'not relevant at all. For instance a match to the "gpl" or the '
            '"cpol" words have a fairly low relevance as they are a weak '
            'indication of an actual license and could be a false positive. '
            'In some cases, this may even be used to discard obvious false '
            'positive matches automatically. The default is to consider a rule '
            'as highly relevant and the relevance is further computed and '
            'adjusted at indexing time automatically based on the length of a '
            'rule. This field is to override the computed defaults.')
    )

    has_stored_relevance = attr.ib(
        default=False,
        metadata=dict(
            help='Computed flag set to True if the "relevance" field is stored '
            'in this rule data file. The default is to have "relevance" computed'
            'and not stored.')
    )

    referenced_filenames = attr.ib(
        default=attr.Factory(list),
        repr=False,
        metadata=dict(
            help='List of file names of file paths found in the rule text that '
            'point to a file that contains license text, such as in "See file COPYING"')
    )

    notes = attr.ib(
        default=None,
        repr=False,
        metadata=dict(
            help='Free text notes. Notes are mandatory for false positive rules.')
    )

    is_from_license = attr.ib(
        default=False,
        repr=False,
        metadata=dict(
            help='Computed flag set to True if this rule is built from a '
            '.LICENSE full text.')
    )

    is_synthetic = attr.ib(
        default=False,
        repr=False,
        metadata=dict(
            help='Flag set to True if this rule is a synthetic rule dynamically '
            'built at runtime, such as an SPDX license rule.')
    )

    is_deprecated = attr.ib(
        default=False,
        repr=False,
        metadata=dict(
            help='Flag set to True if this rule is deleted, '
            'and not to be used anymore in license detection. '
            'This happens usually when a rule is renamed/assigned '
            'to a seperate license-expression, promoted to being a '
            'license text or just plain retired. This is used to '
            'preserve the link to the rule, and therefore make links '
            'to rules as permanent.')
    )

    ###########################################################################
    # lists of clues that can be ignored when detected in this license as they
    # are part of the license or rule text itself

    ignorable_copyrights = attr.ib(
        default=attr.Factory(list),
        repr=False,
        metadata=dict(
            help='List of copyrights that can be ignored when detected in this '
            'text as they are part of the license or rule text proper and can'
            'optionally be excluded from the copyrights detection')
    )

    ignorable_holders = attr.ib(
        default=attr.Factory(list),
        repr=False,
        metadata=dict(
            help='List of holders that can be ignored when detected in this '
            'text as they are part of the license or rule text proper and can'
            'optionally be excluded from the holders detection')
    )

    ignorable_authors = attr.ib(
        default=attr.Factory(list),
        repr=False,
        metadata=dict(
            help='List of authors that can be ignored when detected in this '
            'text as they are part of the license or rule text proper and can'
            'optionally be excluded from the authors detection')
    )

    ignorable_urls = attr.ib(
        default=attr.Factory(list),
        repr=False,
        metadata=dict(
            help='List of holders that can be ignored when detected in this '
            'text as they are part of the license or rule text proper and can'
            'optionally be excluded from the holders detection')
    )

    ignorable_emails = attr.ib(
        default=attr.Factory(list),
        repr=False,
        metadata=dict(
            help='List of emails that can be ignored when detected in this '
            'text as they are part of the license or rule text proper and can'
            'optionally be excluded from the emails detection')
    )

    ###########################################################################

    starts_with_license = attr.ib(
        default=False,
        repr=False,
        metadata=dict(
            help='Computed flag set to True if the rule starts with the word'
            '"license" or a few similar words')
    )

    ends_with_license = attr.ib(
        default=False,
        repr=False,
        metadata=dict(
            help='Computed flag set to True if the rule ends with the word'
            '"license" or a few similar words')
    )

    text = attr.ib(
        default=None,
        repr=False,
        metadata=dict(
            help='Text of this rule')
    )

    key_phrase_spans = attr.ib(
        default=attr.Factory(list),
        repr=False,
        metadata=dict(
            help='List of spans representing key phrases for this rule. These are Spans '
            'of rule text position spans that must be present for this rule to be matched. '
            'Key phrases are enclosed in {{double curly braces}} in the rule text.'
        )
    )

    # These thresholds attributes are computed upon text loading or calling the
    # thresholds function explicitly
    ###########################################################################

    length = attr.ib(
        default=0,
        metadata=dict(
            help='Computed length of a rule text in number of tokens aka. words,'
            'ignoring unknown words and stopwords')
    )

    min_matched_length = attr.ib(
        default=0,
        repr=TRACE_REPR,
        metadata=dict(
            help='Internal computed field representing the minimum matched '
            'length in tokens for a match to this rule to be considered as valid.')
    )

    high_length = attr.ib(
        default=0,
        repr=TRACE_REPR,
        metadata=dict(
            help='Internal computed field representing the length of higher '
            'relevance tokens (from the "legalese" list) in this rule text.')
    )

    min_high_matched_length = attr.ib(
        default=0,
        repr=TRACE_REPR,
        metadata=dict(
            help='Internal computed field representing the minimum matched '
            'length in higher relevance tokens (from the "legalese" list) '
            'for a match to this rule to be considered as valid.')
    )

    length_unique = attr.ib(
        default=0,
        repr=TRACE_REPR,
        metadata=dict(
            help='Internal computed field representing the length of unique '
            'tokens in this rule text.')
    )

    min_matched_length_unique = attr.ib(
        default=0,
        repr=TRACE_REPR,
        metadata=dict(
            help='Internal computed field representing the minimum matched '
            'length in unique tokens for a match to this rule to be considered '
            'as valid.')
    )

    high_length_unique = attr.ib(
        default=0,
        repr=TRACE_REPR,
        metadata=dict(
            help='Internal computed field representing the length of unique '
            'higher relevance tokens (from the "legalese" list) in this rule text.')
    )

    min_high_matched_length_unique = attr.ib(
        default=0,
        repr=TRACE_REPR,
        metadata=dict(
            help='Internal computed field representing the minimum matched '
            'length in unique higher relevance tokens (from the "legalese" list) '
            'for a match to this rule to be considered as valid.')
    )

    is_small = attr.ib(
        default=False,
        repr=TRACE_REPR,
        metadata=dict(
            help='Internal computed flag set to True if this rule is "small"')
    )

    has_computed_thresholds = attr.ib(
        default=False,
        repr=False,
        metadata=dict(
            help='Internal computed flag set to True when the thresholds flag '
            'above have been computed for this rule')
    )

    # TODO: use the actual words and not just a count
    stopwords_by_pos = attr.ib(
        default=attr.Factory(dict),
        repr=False,
        metadata=dict(
            help='Index of rule token positions to a number of stopword '
            'tokens after this position. For stopwords at the start, the '
            'position is using the magic -1 key.')
    )

    @property
    def rule_url(self):
        """
        Return a string with the permanent URL to this rule on
        scancode-toolkit github repository.
        """
        if self.is_synthetic or not self.is_builtin:
            return None

        if self.is_from_license:
            # license expression is single key
            return SCANCODE_LICENSE_URL.format(self.license_expression)
        else:
            return SCANCODE_RULE_URL.format(self.identifier)

    def rule_file(
        self,
        rules_data_dir=rules_data_dir,
        licenses_data_dir=licenses_data_dir,
    ):
        """
        Return the path to the rule file for this rule object, given the
        `rules_data_dir` directory or `licenses_data_dir` if a license rule.
        Return None if the Rule does not have yet an identifier or is synthetic.
        """
        if self.is_synthetic or not self.identifier:
            return None

        if self.is_from_license:
            return join(licenses_data_dir, self.identifier)

        return join(rules_data_dir, self.identifier)

    def __attrs_post_init__(self, *args, **kwargs):
        self.setup()

    def setup(self):
        """
        Setup a few basic computed attributes after instance creation.
        """
        self.relevance = as_int(float(self.relevance or 100))
        self.minimum_coverage = as_int(float(self.minimum_coverage or 0))

        if self.license_expression:
            try:
                expression = self.licensing.parse(self.license_expression)
            except Exception as e:
                exp = self.license_expression
                trace = traceback.format_exc()
                raise InvalidRule(
                    f'Unable to parse Rule license expression: {exp!r} '
                    f'for: file://{self.identifier}\n{trace}'
                ) from e

            if expression is None:
                raise InvalidRule(
                    f'Invalid rule License expression parsed to empty: '
                    f'{self.license_expression!r} for: file://{self.identifier}'
                )

            self.license_expression = expression.render()
            self.license_expression_object = expression

    @property
    def has_unknown(self):
        """
        Return True if any of this rule licenses is an unknown license.
        """
        # TODO: consider using the license_expression_object and the is_unknown
        # license flag instead
        return self.license_expression and 'unknown' in self.license_expression

    def validate(self, licensing=None, thorough=False):
        """
        Validate this rule using the provided ``licensing`` Licensing and yield
        one error message for each type of error detected.
        """
        is_false_positive = self.is_false_positive

        license_flags = (
            self.is_license_notice,
            self.is_license_text,
            self.is_license_reference,
            self.is_license_tag,
            self.is_license_intro,
            self.is_license_clue,
        )

        has_license_flags = any(license_flags)
        has_many_license_flags = len([l for l in license_flags if l]) != 1

        license_expression = self.license_expression

        ignorables = (
            self.ignorable_copyrights,
            self.ignorable_holders,
            self.ignorable_authors,
            self.ignorable_urls,
            self.ignorable_emails,
        )

        if is_false_positive:
            if not self.notes:
                yield 'is_false_positive rule must have notes.'

            if self.is_continuous:
                yield 'is_false_positive rule cannot be is_continuous.'

            if has_license_flags:
                yield 'is_false_positive rule cannot have is_license_* flags.'

            if license_expression:
                yield 'is_false_positive rule cannot have a license_expression.'

            if self.has_stored_relevance:
                yield 'is_false_positive rule cannot have a stored relevance.'

            if self.referenced_filenames:
                yield 'is_false_positive rule cannot have referenced_filenames.'

            if any(ignorables):
                yield 'is_false_positive rule cannot have ignorable_* attributes.'

        if self.language not in known_languages:
            yield f'Unknown language: {self.language}'

        if not is_false_positive:
            if not (0 <= self.minimum_coverage <= 100):
                yield 'Invalid rule minimum_coverage. Should be between 0 and 100.'

            if not (0 <= self.relevance <= 100):
                yield 'Invalid rule relevance. Should be between 0 and 100.'

            if has_many_license_flags:
                yield 'Invalid rule is_license_* flags. Only one allowed.'

            if not has_license_flags:
                yield 'At least one is_license_* flag is needed.'

            if not check_is_list_of_strings(self.referenced_filenames):
                yield 'referenced_filenames must be a list of strings'

            if not all(check_is_list_of_strings(i) for i in ignorables):
                yield 'ignorables must be a list of strings'

            if not license_expression:
                yield 'Missing license_expression.'
            else:
                if not has_only_lower_license_keys(license_expression):
                    yield (
                        f'Invalid license_expression: {license_expression} ,'
                        'keys should be lowercase.'
                    )

                if licensing:
                    try:
                        licensing.parse(license_expression, validate=True, simple=True)
                    except ExpressionError as e:
                        yield (
                            f'Failed to parse and validate license_expression: '
                            f'{license_expression} with error: {e}'
                        )

            if self.referenced_filenames:
                if len(set(self.referenced_filenames)) != len(self.referenced_filenames):
                    yield 'referenced_filenames cannot contain duplicates.'

        if thorough:
            text = self.text
            data = {"text": text}
            # We are testing whether we can dump as yaml and load from yaml
            # without failing (i.e. whether the text is yaml safe)
            try:
                yaml_string = saneyaml_dump(data)
                loaded_yaml = saneyaml_load(yaml_string)
            except Exception:
                yield (f'Error invalid YAML text at: {self.identifier}, failed during saneyaml.load()')

    def license_keys(self, unique=True):
        """
        Return a list of license keys for this rule.
        """
        if not self.license_expression:
            return []
        return self.licensing.license_keys(
            self.license_expression_object,
            unique=unique,
        )

    def same_licensing(self, other):
        """
        Return True if the other rule has the same licensing as this rule.
        """
        if self.license_expression and other.license_expression:
            return self.licensing.is_equivalent(
                self.license_expression_object,
                other.license_expression_object,
            )

    def licensing_contains(self, other):
        """
        Return True if this rule licensing contains the other rule licensing.
        """
        if self.license_expression and other.license_expression:
            return self.licensing.contains(
                expression1=self.license_expression_object,
                expression2=other.license_expression_object,
            )

    def spdx_license_expression(self):
        from licensedcode.cache import build_spdx_license_expression
        from licensedcode.cache import get_cache
        return str(build_spdx_license_expression(self.license_expression, licensing=get_cache().licensing))

    def get_length(self, unique=False):
        return self.length_unique if unique else self.length

    def get_min_matched_length(self, unique=False):
        return (self.min_matched_length_unique if unique
                else self.min_matched_length)

    def get_high_length(self, unique=False):
        return self.high_length_unique if unique else self.high_length

    def get_min_high_matched_length(self, unique=False):
        return (self.min_high_matched_length_unique if unique
                else self.min_high_matched_length)

    def get_flags_mapping(self):
        """
        Return a list of boolean attributes for a rule which are set to True.
        """

        rule_boolean_attributes = [
            'is_license_text',
            'is_license_notice',
            'is_license_reference',
            'is_license_tag',
            'is_license_intro',
            'is_license_clue',
            'is_continuous',
        ]

        mapping = {}
        for attribute in rule_boolean_attributes:
            value = getattr(self, attribute)
            if value:
                mapping[attribute] = True

        return mapping

    def to_reference(self):
        """
        Return a mapping of reference data for this Rule object.
        """
        data = {}
        data['license_expression'] = self.license_expression
        data['identifier'] = self.identifier
        data['language'] = self.language
        data['rule_url'] = self.rule_url
        data['is_license_text'] = self.is_license_text
        data['is_license_notice'] = self.is_license_notice
        data['is_license_reference'] = self.is_license_reference
        data['is_license_tag'] = self.is_license_tag
        data['is_license_intro'] = self.is_license_intro
        data['is_license_clue'] = self.is_license_clue
        data['is_continuous'] = self.is_continuous
        data['is_builtin'] = self.is_builtin
        data['is_from_license'] = self.is_from_license
        data['is_synthetic'] = self.is_synthetic
        data['length'] = self.length
        data['relevance'] = as_int(self.relevance)
        data['minimum_coverage'] = as_int(self.minimum_coverage)
        data['referenced_filenames'] = self.referenced_filenames
        data['notes'] = self.notes
        data['ignorable_copyrights'] = self.ignorable_copyrights
        data['ignorable_holders'] = self.ignorable_holders
        data['ignorable_authors'] = self.ignorable_authors
        data['ignorable_urls'] = self.ignorable_urls
        data['ignorable_emails'] = self.ignorable_emails
        data['text'] = self.text
        return data

    def to_dict(self, include_text=False):
        """
        Return an ordered mapping of self, excluding texts unless
        ``include_text`` is True. Used for serialization. Empty values are not
        included.
        """
        data = {}

        is_false_positive = self.is_false_positive

        if self.license_expression:
            data['license_expression'] = self.license_expression

        flags = (
            'is_false_positive',
            'is_license_text',
            'is_license_notice',
            'is_license_reference',
            'is_license_tag',
            'is_license_intro',
            'is_license_clue',
            'is_continuous',
            'is_deprecated'
        )

        # default to English which is implied
        if self.language != 'en':
            data['language'] = self.language

        for flag in flags:
            tag_value = getattr(self, flag, False)
            if tag_value:
                data[flag] = tag_value

        if self.has_stored_relevance and self.relevance and not is_false_positive:
            data['relevance'] = as_int(self.relevance)

        if self.has_stored_minimum_coverage and self.minimum_coverage > 0 and not is_false_positive:
            data['minimum_coverage'] = as_int(self.minimum_coverage)

        if self.referenced_filenames and not is_false_positive:
            data['referenced_filenames'] = self.referenced_filenames

        if self.notes:
            data['notes'] = self.notes

        if include_text and self.text:
            data['text'] = self.text

        if not is_false_positive:
            ignorables = (
                'ignorable_copyrights',
                'ignorable_holders',
                'ignorable_authors',
                'ignorable_urls',
                'ignorable_emails',
            )

            for igno in ignorables:
                tag_value = getattr(self, igno, False)
                if tag_value:
                    data[igno] = tag_value

        return data


def has_only_lower_license_keys(license_expression, licensing=Licensing()):
    """
    Return True if all license keys of ``license_expression`` are lowercase.
    """
    return all(
        k == k.lower()
        for k in licensing.license_keys(license_expression, unique=False)
    )


def check_is_list_of_strings(l):
    """
    Return True if `l` is a list of strings or an empty list, False otherwise.
    """
    if isinstance(l, list):
        if l:
            return all(isinstance(i, str) for i in l)
        return True
    return False


def as_int(num):
    """
    Convert ``num`` to int if ``num`` is not an int and this would not lead to
    loss of information, e.g. when ``num`` is an int stored as a float type.
    """
    if isinstance(num, str):
        num = float(num)
    if isinstance(num, float):
        n = int(num)
        if n == num:
            return n
    return num


@attr.s(slots=True)
class Rule(BasicRule):
    """
    A detection rule object with support for data and text files.
    """

    def __attrs_post_init__(self, *args, **kwargs):
        self.setup()

    @classmethod
    def from_file(cls, rule_file, is_builtin=True):
        """
        Return a new Rule object loaded from a file stored at
        ``rule_file`` with the text and it's data as with YAML frontmatter.
        """
        rule = Rule(is_builtin=is_builtin)
        rule.load_data(rule_file=rule_file)
        return rule

    @property
    def pysafe_expression(self):
        """
        Return a python safe identifier, for use in rule identifiers"""
        return python_safe_name(self.license_expression)

    def load_data(self, rule_file):
        """
        Load data from ``rule_file`` which has both the text and the data (as YAML forntmatter).
        Check presence of text file to determine if this is a special synthetic rule.
        """
        if self.is_synthetic:
            if not self.text:
                raise InvalidRule(
                    f'Invalid synthetic rule without text: {self}: {self.text!r}')
            return self

        if not rule_file:
            raise InvalidRule(
                f'Cannot load rule without its corresponding rule_file: '
                f'{self}: file://{rule_file}')

        self.identifier = file_name(rule_file)

        try:
            self.load(rule_file=rule_file)
        except Exception:
            trace = traceback.format_exc()
            raise InvalidRule(f'While loading: file://{rule_file}\n{trace}')

        return self

    def tokens(self):
        """
        Return a sequence of token strings for this rule text.

        SIDE EFFECT: Computed attributes such as "length", "relevance",
        "is_continuous",  "minimum_coverage" and "stopword_by_pos" are
        recomputed as a side effect.
        """

        text = self.text
        # We tag this rule as being a bare URL if it starts with a scheme and is
        # on one line: this is used to determine a matching approach

        if (
            text.startswith(('http://', 'https://', 'ftp://'))
            and '\n' not in text[:1000]
        ):
            self.minimum_coverage = 100

        toks, stopwords_by_pos = index_tokenizer_with_stopwords(text)
        self.length = len(toks)
        self.stopwords_by_pos = stopwords_by_pos
        self.set_relevance()

        # set key phrase spans that must be present for the rule
        # to pass through refinement
        self.key_phrase_spans = self.build_key_phrase_spans()
        self._set_continuous()

        return toks

    def _set_continuous(self):
        """
        Set the "is_continuous" flag if this rule must be matched exactly
        without gaps, stopwords or unknown words. Must run after
        key_phrase_spans computation.
        """
        if (
            not self.is_continuous
            and self.key_phrase_spans
            and len(self.key_phrase_spans) == 1
            and len(self.key_phrase_spans[0]) == self.length
        ):
            self.is_continuous = True

    def build_key_phrase_spans(self):
        """
        Return a list of Spans marking key phrases token positions of that must
        be present for this rule to be matched.
        """
        from licensedcode.required_phrases import get_key_phrase_spans
        if self.is_from_license:
            return []
        try:
            return list(get_key_phrase_spans(self.text))
        except Exception as e:
            raise InvalidRule(f'Invalid rule: {self}') from e

    def compute_thresholds(self, small_rule=SMALL_RULE):
        """
        Compute and set thresholds either considering the occurrence of all
        tokens or the occurence of unique tokens.
        """
        min_cov, self.min_matched_length, self.min_high_matched_length = (
            compute_thresholds_occurences(
                self.minimum_coverage,
                self.length,
                self.high_length,
            )
        )
        if not self.has_stored_minimum_coverage:
            self.minimum_coverage = min_cov

        self._minimum_containment = self.minimum_coverage / 100

        self.min_matched_length_unique, self.min_high_matched_length_unique = (
            compute_thresholds_unique(
                self.minimum_coverage,
                self.length,
                self.length_unique, self.high_length_unique,
            )
        )

        self.is_small = self.length < small_rule

    def dump(self, rules_data_dir):
        """
        Dump a representation of this rule as a .RULE file stored in
        ``rules_data_dir`` as a UTF-8 file having:
         - the rule data as YAML frontmatter
         - the rule text
        and this is a `rule_file`.

        Does nothing if this rule was created from a License (e.g.,
        `is_from_license` is True)
        """
        if self.is_from_license or self.is_synthetic:
            return

        rule_file = self.rule_file(rules_data_dir=rules_data_dir)

        metadata = self.to_dict()
        content = self.text
        output = dumps_frontmatter(content=content, metadata=metadata)
        with open(rule_file, 'w') as of:
            of.write(output)

    def load(self, rule_file, with_checks=True):
        """
        Load self from a .RULE file with YAMl frontmatter stored in rule_file.
        Unknown fields are ignored and not bound to the Rule object.
        Optionally check for consistency if ``with_checks`` is True.
        """
        try:
            content, data = load_frontmatter(rule_file)
            if not content:
                raise InvalidRule(
                    f'Cannot load rule with empty text: '
                    f'{self}: file://{rule_file}'
                )

            self.text = content.lstrip()

        except Exception as e:
            print('#############################')
            print('INVALID LICENSE RULE FILE:', f'file://{rule_file}')
            print('#############################')
            print(e)
            print('#############################')
            # this is a rare case, but yes we abruptly stop.
            raise e

        known_attributes = set(attr.fields_dict(self.__class__))
        data_file_attributes = set(data)
        if with_checks:
            unknown_attributes = data_file_attributes.difference(known_attributes)
            if unknown_attributes:
                unknown_attributes = ', '.join(sorted(unknown_attributes))
                msg = 'License rule {} data file has unknown attributes: {}'
                raise InvalidRule(msg.format(self, unknown_attributes))

        self.license_expression = data.get('license_expression')

        self.is_false_positive = data.get('is_false_positive', False)

        relevance = as_int(float(data.get('relevance') or 0))
        # Keep track if we have a stored relevance of not.
        if relevance:
            self.relevance = relevance
            self.has_stored_relevance = True
        else:
            self.relevance = 100
            self.has_stored_relevance = False

        minimum_coverage = as_int(float(data.get('minimum_coverage') or 0))
        self._minimum_containment = minimum_coverage / 100
        if minimum_coverage:
            # Keep track if we have a stored minimum_coverage of not.
            self.minimum_coverage = minimum_coverage
            self.has_stored_minimum_coverage = True
        else:
            self.minimum_coverage = 0
            self.has_stored_minimum_coverage = False

        self.is_license_text = data.get('is_license_text', False)
        self.is_license_notice = data.get('is_license_notice', False)
        self.is_license_tag = data.get('is_license_tag', False)
        self.is_license_reference = data.get('is_license_reference', False)
        self.is_license_intro = data.get('is_license_intro', False)
        self.is_license_clue = data.get('is_license_clue', False)
        self.is_continuous = data.get('is_continuous', False)
        self.is_deprecated = data.get('is_deprecated', False)

        self.referenced_filenames = data.get('referenced_filenames', []) or []

        # these are purely informational and not used at run time
        notes = data.get('notes')
        if notes:
            self.notes = notes.strip()

        self.ignorable_copyrights = data.get('ignorable_copyrights', [])
        self.ignorable_holders = data.get('ignorable_holders', [])
        self.ignorable_authors = data.get('ignorable_authors', [])
        self.ignorable_urls = data.get('ignorable_urls', [])
        self.ignorable_emails = data.get('ignorable_emails', [])

        self.language = data.get('language') or 'en'
        self.setup()
        return self

    def set_relevance(self):
        """
        Set the ``relevance`` attribute to a computed value for this rule. The
        relevance is a float between 0 and 100 where 100 means highly relevant
        and 0 means not relevant at all.

        The relevance is computed using this approach:

        - pre-defined, stored relevance is used as-is
        - false positive or SPDX rules have 100 relevance.
        - relevance is computed based on the rule length
        """

        if self.is_false_positive:
            self.relevance = 100
            self.has_stored_relevance = True
            return

        computed_relevance = compute_relevance(self.length)

        if self.has_stored_relevance:
            if self.relevance == computed_relevance:
                self.has_stored_relevance = False
        else:
            self.relevance = computed_relevance

    @staticmethod
    def from_match_data(license_match_mapping):
        """
        Return a Rule object from a ``license_match_mapping`` mapping of
        LicenseMatch data.
        """
        rule_identifier = license_match_mapping["rule_identifier"]

        rule_subclass_by_identifier_prefix = {
            "spdx-license-identifier": SpdxRule,
            "license-detection-unknown": UnknownRule,
            "package-manifest": UnDetectedRule,
        }

        prefixes = tuple(rule_subclass_by_identifier_prefix.keys())
        if rule_identifier.startswith(prefixes):
            for prefix, klass in rule_subclass_by_identifier_prefix.items():
                if rule_identifier.startswith(prefix):
                    return klass(
                        license_expression=license_match_mapping["license_expression"],
                        text=license_match_mapping.get("matched_text", None),
                        length=license_match_mapping["matched_length"],
                    )
        else:
            from licensedcode.cache import get_index
            return get_index().rules_by_id[rule_identifier]


def compute_relevance(length):
    """
    Return a computed ``relevance`` given a ``length`` and a threshold.
    The relevance is a integer between 0 and 100 where 100 means highly
    relevant and 0 means not relevant at all.

    The relevance is computed base on the rule or detection ``length`` using
    a relevance schedule based on the ``length``

    For instance a match to the "gpl" or the "cpol" words have a fairly low
    relevance as they are a weak indication of an actual license and could
    be a false positive and should therefore be assigned a low relevance. In
    contrast a match to most or all of the apache-2.0 license text is highly
    relevant. The relevance is used as the basis to compute a LicenseMatch
    and LicenseDetection score.

    For example::
    >>> compute_relevance(0)
    0
    >>> compute_relevance(1)
    5
    >>> compute_relevance(17)
    94
    >>> compute_relevance(18)
    100
    >>> compute_relevance(19)
    100
    >>> compute_relevance(100)
    100
    """
    if length > 18:
        return 100
    return {
        0: 0,
        1: 5,
        2: 11,
        3: 16,
        4: 22,
        5: 27,
        6: 33,
        7: 38,
        8: 44,
        9: 50,
        10: 55,
        11: 61,
        12: 66,
        13: 72,
        14: 77,
        15: 83,
        16: 88,
        17: 94,
        18: 100,
    }[length]


def compute_thresholds_occurences(
    minimum_coverage,
    length,
    high_length,
    _MIN_MATCH_HIGH_LENGTH=MIN_MATCH_HIGH_LENGTH,
    _MIN_MATCH_LENGTH=MIN_MATCH_LENGTH,
):
    """
    Compute and return thresholds considering the occurrence of all tokens.
    """
    if minimum_coverage == 100:
        min_matched_length = length
        min_high_matched_length = high_length
        return minimum_coverage, min_matched_length, min_high_matched_length

    if length < 3:
        min_high_matched_length = high_length
        min_matched_length = length
        minimum_coverage = 100

    elif length < 10:
        min_matched_length = length
        min_high_matched_length = high_length
        minimum_coverage = 80

    elif length < 30:
        min_matched_length = length // 2
        min_high_matched_length = min(high_length, _MIN_MATCH_HIGH_LENGTH)
        minimum_coverage = 50

    elif length < 200:
        min_matched_length = _MIN_MATCH_LENGTH
        min_high_matched_length = min(high_length, _MIN_MATCH_HIGH_LENGTH)
        # minimum_coverage = max(15, int(length//10))

    else:  # if length >= 200:
        min_matched_length = length // 10
        min_high_matched_length = high_length // 10
        # minimum_coverage = int(length//10)

    return minimum_coverage, min_matched_length, min_high_matched_length


def compute_thresholds_unique(
    minimum_coverage,
    length,
    length_unique,
    high_length_unique,
    _MIN_MATCH_HIGH_LENGTH=MIN_MATCH_HIGH_LENGTH,
    _MIN_MATCH_LENGTH=MIN_MATCH_LENGTH,
):
    """
    Compute and set thresholds considering the occurrence of only unique tokens.
    """
    if minimum_coverage == 100:
        min_matched_length_unique = length_unique
        min_high_matched_length_unique = high_length_unique
        return min_matched_length_unique, min_high_matched_length_unique

    if length > 200:
        min_matched_length_unique = length // 10
        min_high_matched_length_unique = high_length_unique // 10

    elif length < 5:
        min_matched_length_unique = length_unique
        min_high_matched_length_unique = high_length_unique

    elif length < 10:
        if length_unique < 2:
            min_matched_length_unique = length_unique
        else:
            min_matched_length_unique = length_unique - 1
        min_high_matched_length_unique = high_length_unique

    elif length < 20:
        min_matched_length_unique = high_length_unique
        min_high_matched_length_unique = high_length_unique

    else:
        min_matched_length_unique = _MIN_MATCH_LENGTH
        highu = (int(high_length_unique // 2)) or high_length_unique
        min_high_matched_length_unique = min(highu, _MIN_MATCH_HIGH_LENGTH)

    return min_matched_length_unique, min_high_matched_length_unique


class SynthethicRule(Rule):
    """
    A specialized rule subclass for synthethic rules generated at runtime.
    They do not have backing files.
    """

    @property
    def _unique_id(self):
        """
        Return a computed unique id string based on this rule content.

        This is used to compute unique identifiers for synthetic rules.
        (This is a SHA1 checksum of the expression and text, but this is an
        implementation detail)
        """
        content = f'{self.license_expression!r}{self.text!r}'
        return sha1(content.encode('utf-8')).hexdigest()

    def load(self):
        raise NotImplementedError

    def dump(self):
        raise NotImplementedError

    def rule_file(
        self,
        rules_data_dir=rules_data_dir,
        licenses_data_dir=licenses_data_dir,
    ):
        # synthetic rules have no file
        return ""


@attr.s(slots=True, repr=False)
class SpdxRule(SynthethicRule):
    """
    A specialized rule object that is used for the special case of SPDX license
    expressions.

    Since we may have an infinite possible number of SPDX expressions and these
    are not backed by a traditional rule text file, we use this class to handle
    the specifics of these how rules that are built at matching time: one rule
    is created for each detected SPDX license expression.
    """

    def __attrs_post_init__(self, *args, **kwargs):
        self.identifier = f'spdx-license-identifier-{self.pysafe_expression}-{self._unique_id}'
        self.setup()

        if not self.license_expression:
            raise InvalidRule(f'Empty license expression: {self.identifier}')

        self.is_license_tag = True
        self.is_small = False
        self.relevance = 100
        self.has_stored_relevance = True
        self.is_synthetic = True


UNKNOWN_LICENSE_KEY = 'unknown'


@attr.s(slots=True, repr=False)
class UnknownRule(SynthethicRule):
    """
    A specialized rule object that is used for the special case of unknown
    license detection.

    Since we may have an infinite number of possible unknown licenses and these
    are not backed by a traditional rule text file, we use this class to handle
    the specifics of these how such rules are built at matching time: one new
    synthetic rule is created for each detected unknown license match.
    """

    def __attrs_post_init__(self, *args, **kwargs):
        # We craft a UNIQUE identifier for the matched content
        self.identifier = f'license-detection-unknown-{self._unique_id}'

        self.license_expression = UNKNOWN_LICENSE_KEY
        #TODO: that this could be shared across rules as an optimization
        self.license_expression_object = self.licensing.parse(UNKNOWN_LICENSE_KEY)
        self.is_license_notice = True
        self.notes = 'Unknown license based on a composite of license words.'
        self.is_synthetic = True
        self.setup()


@attr.s(slots=True, repr=False)
class UnDetectedRule(SynthethicRule):
    """
    A specialized rule object that is used for the special case of extracted
    license statements without any valid license detection.

    Since there is a license where there is a non empty extracted license
    statement (typically found in a package manifest), if there is no license
    detected by scancode, it would be incorrect to not point out that there
    is a license (though undetected).
    """

    def __attrs_post_init__(self, *args, **kwargs):
        self.identifier = f'package-manifest-{self.pysafe_expression}-{self._unique_id}'
        expression = self.licensing.parse(self.license_expression)
        self.license_expression = expression.render()
        self.license_expression_object = expression
        self.is_license_tag = True
        self.is_small = False
        self.relevance = 100
        self.has_stored_relevance = True


@attr.s(slots=True, repr=False)
class DebianUnknownRule(Rule):
    """
    A specialized rule object that is used for the special case of unknown
    matches in debian copyright files.

    Since there can be a lot of unknown licenses in a debian copyright file, the
    rule and the LicenseMatch objects for these are built at matching time.
    """

    def __attrs_post_init__(self, *args, **kwargs):
        self.identifier = 'debian-' + self.license_expression
        expression = self.licensing.parse(self.license_expression)
        self.license_expression = expression.render()
        self.license_expression_object = expression
        self.is_license_tag = True
        self.is_small = False
        self.relevance = 100
        self.has_stored_relevance = True

    def load(self):
        raise NotImplementedError

    def dump(self):
        raise NotImplementedError


def _print_rule_stats():
    """
    Print rules statistics.
    """
    from licensedcode.cache import get_index
    idx = get_index()
    rules = idx.rules_by_rid
    sizes = Counter(r.length for r in rules)
    print('Top 15 lengths: ', sizes.most_common(15))
    print(
        '15 smallest lengths: ',
        sorted(sizes.items(),
        key=itemgetter(0))[:15],
    )

    high_sizes = Counter(r.high_length for r in rules)
    print('Top 15 high lengths: ', high_sizes.most_common(15))
    print(
        '15 smallest high lengths: ',
        sorted(high_sizes.items(),
        key=itemgetter(0))[:15],
    )


def update_ignorables(licensish, verbose=False):
    """
    Update ignorables and return the ``licensish`` Rule or License using the
    latest values detected in its text.

    Display progress messages if ``verbose`` is True.
    """

    if verbose:
        print(f'Processing:', licensish.identifier)

    text = licensish.text
    if text:
        ignorables = get_ignorables(text=text, verbose=verbose)
        set_ignorables(licensish=licensish, ignorables=ignorables, verbose=verbose)
    return licensish


def set_ignorables(licensish, ignorables, verbose=False):
    """
    Update ``licensish`` Rule or License using the mapping of ``ignorables``
    attributes.

    Display progress messages if ``verbose`` is True.
    """
    for key, value in ignorables.items():
        if verbose:
            existing = getattr(licensish, key, None)
            print(f'Updating ignorable: {key} from: {existing!r} to: {value!r}')
        setattr(licensish, key, value)
    return licensish


def get_ignorables(text, verbose=False):
    """
    Return a mapping of ignorable clues lists found in a ``text`` for
    copyrights, holders, authors, urls, emails. Do not include items with empty
    values.

    Display progress messages if ``verbose`` is True.
    """
    from cluecode.copyrights import detect_copyrights_from_lines
    from cluecode.copyrights import Detection

    from cluecode.finder import find_urls
    from cluecode.finder import find_emails

    text_lines = text.splitlines()

    # Redundant clues found in a license or rule text can be ignored.
    # Therefdore we collect and set ignorable copyrights, holders and authors
    detections = detect_copyrights_from_lines(numbered_lines=enumerate(text.splitlines(), 1))
    copyrights, holders, authors = Detection.split_values(detections)

    if verbose:
        for detection in (copyrights + holders + authors):
            print(f'  Found ignorable: {detection}')

    copyrights = set(copyrights)
    holders = set(holders)
    authors = set(authors)

    # collect and set ignorable emails and urls
    urls = set(u for (u, _ln) in find_urls(location=text_lines) if u)
    if verbose:
        print(f'  Found urls: {urls}')

    emails = set(e for (e, _ln) in find_emails(text_lines) if e)
    if verbose:
        print(f'  Found emails: {emails}')

    ignorables = build_ignorables_mapping(
        copyrights=copyrights,
        holders=holders,
        authors=authors,
        urls=urls,
        emails=emails,
    )

    if verbose:
        print(f'  Found ignorables: {ignorables}')
    return ignorables


def get_normalized_ignorables(licensish):
    """
    Return a sorted mapping of ignorables built from a licensish Rule or License.
    """
    return build_ignorables_mapping(
        copyrights=licensish.ignorable_copyrights,
        holders=licensish.ignorable_holders,
        authors=licensish.ignorable_authors,
        urls=licensish.ignorable_urls,
        emails=licensish.ignorable_emails,
    )


def build_ignorables_mapping(copyrights, holders, authors, urls, emails):
    """
    Return a sorted mapping of ignorables built from lists of ignorable clues.
    """
    ignorables = dict(
        ignorable_copyrights=sorted(copyrights or []),
        ignorable_holders=sorted(holders or []),
        ignorable_authors=sorted(authors or []),
        ignorable_urls=sorted(urls or []),
        ignorable_emails=sorted(emails or []),
    )

    return {k: v for k, v in sorted(ignorables.items()) if v}


def find_rule_base_location(name_prefix, rules_directory=rules_data_dir):
    """
    Return a new, unique and non-existing base location in ``rules_directory``
    with a file name but without an extension suitable to create a new rule
    without overwriting any existing rule. Use the ``name_prefix`` string as a
    prefix for this name.
    """

    cleaned = (
        name_prefix
        .lower()
        .strip()
        .replace(' ', '_')
        .replace('(', '')
        .replace(')', '')
        .strip('_-')
    )
    template = cleaned + '_{idx}'

    idx = 1
    while True:
        base_name = template.format(idx=idx)
        base_loc = join(rules_directory, base_name)
        if not exists(f'{base_loc}.RULE'):
            return base_loc
        idx += 1


def get_rules_by_expression(rules_data_dir=rules_data_dir):
    """
    Get a dictionary (sorted by license_expression) of {license_expression: rules}
    where `rules` is a list of all rule objects having the `license_expression`.
    """
    rules = list(load_rules(rules_data_dir=rules_data_dir))

    rules_by_identifier = {
        rule.identifier: rule
        for rule in rules
    }

    rules_by_expression = defaultdict(list)

    for rule in rules_by_identifier.values():
        # Only return rules with license_expression (i.e. skip false positives)
        if rule.license_expression:
            rules_by_expression[rule.license_expression].append(rule)

    return OrderedDict(sorted(rules_by_expression.items()))
