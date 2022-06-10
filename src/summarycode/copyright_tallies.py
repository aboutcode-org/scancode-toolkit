#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from collections import defaultdict
import re

import attr
import fingerprints
from text_unidecode import unidecode

from cluecode.copyrights import CopyrightDetector
from commoncode.text import toascii
from summarycode.utils import sorted_counter
from summarycode.utils import get_resource_tallies
from summarycode.utils import set_resource_tallies

# Tracing flags
TRACE = False
TRACE_FP = False
TRACE_DEEP = False
TRACE_TEXT = False
TRACE_CANO = False


def logger_debug(*args):
    pass


if TRACE or TRACE_CANO:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))

# TODO: keep the original order of statements as much as possible


def copyright_tallies(resource, children, keep_details=False):
    return build_tallies(
        resource=resource,
        children=children,
        attributes_list='copyrights',
        attribute_value='copyright',
        tallier=tally_copyrights,
        keep_details=keep_details
    )


def holder_tallies(resource, children, keep_details=False):
    return build_tallies(
        resource=resource,
        children=children,
        attributes_list='holders',
        attribute_value='holder',
        tallier=tally_persons,
        keep_details=keep_details
    )


def author_tallies(resource, children, keep_details=False):
    return build_tallies(
        resource=resource,
        children=children,
        attributes_list='authors',
        attribute_value='author',
        tallier=tally_persons,
        keep_details=keep_details
    )


def build_tallies(
    resource,
    children,
    attributes_list,
    attribute_value,
    tallier,
    keep_details=False,
):
    """
    Update the ``resource`` Resource with a tally of scan fields from itself and its
    ``children``.

    Resources and this for the `attributes_list` values list key (such as
    copyrights, etc) and the ``attribute_value`` details key (such as copyright).

     - `attributes_list` is the name of the attribute values list
       ('copyrights', 'holders' etc.)

     - `attribute_value` is the name of the attribute value  key in this list
       ('copyright', 'holder' etc.)

     - `tallier` is a function that takes a list of texts and returns
        texts with counts
     """
    # Collect current data
    values = getattr(resource, attributes_list, [])

    no_detection_counter = 0

    if values:
        # keep current data as plain strings
        candidate_texts = [entry.get(attribute_value) for entry in values]
    else:
        candidate_texts = []
        if resource.is_file:
            no_detection_counter += 1

    # Collect direct children existing summaries
    for child in children:
        child_summaries = get_resource_tallies(
            child,
            key=attributes_list,
            as_attribute=keep_details
        ) or []

        for child_summary in child_summaries:
            count = child_summary['count']
            value = child_summary['value']
            if value:
                candidate_texts.append(Text(value, value, count))
            else:
                no_detection_counter += count

    # summarize proper using the provided function
    tallied = tallier(candidate_texts)

    # add back the counter of things without detection
    if no_detection_counter:
        tallied.update({None: no_detection_counter})

    tallied = sorted_counter(tallied)
    if TRACE:
        logger_debug('COPYRIGHT tallied:', tallied)

    set_resource_tallies(
        resource,
        key=attributes_list,
        value=tallied,
        as_attribute=keep_details,
    )
    return tallied


# keep track of an original text value and the corresponding clustering "key"
@attr.attributes(slots=True)
class Text(object):
    # cleaned, normalized, clustering text for a copyright holder
    key = attr.attrib()
    # original text for a copyright holder
    original = attr.attrib()
    # count of occurences of a text
    count = attr.attrib(default=1)

    def normalize(self):
        if TRACE_TEXT:
            logger_debug('Text.normalize:', self)
        key = self.key.lower()
        key = ' '.join(key.split())
        key = key.strip('.,').strip()
        key = clean(key)
        self.key = key.strip('.,').strip()

    def transliterate(self):
        self.key = toascii(self.key, translit=True)

    def fingerprint(self):
        key = self.key
        if not isinstance(key, str):
            key = unidecode(key)
        fp = fingerprints.generate(key)

        if TRACE_TEXT or TRACE_FP:
            logger_debug('Text.fingerprint:key: ', repr(self.key))
            logger_debug('Text.fingerprint:fp :    ', fingerprints.generate(unidecode(self.key)))

        self.key = fp


def tally_copyrights(texts, _detector=CopyrightDetector()):
    """
    Return a list of mapping of {value:string, count:int} given a
    list of copyright strings or Text() objects.
    """
    texts_to_tally = []
    no_detection_counter = 0
    for text in texts:
        if not text:
            no_detection_counter += 1
            continue
        # Keep Text objects as-is
        if isinstance(text, Text):
            texts_to_tally.append(text)
        else:
            # FIXME: redetect to strip year should not be needed!!
            statements_without_years = _detector.detect(
                [(1, text)],
                include_copyrights=True,
                include_holders=False,
                include_authors=False,
                include_copyright_years=False,
            )

            for detection in statements_without_years:
                copyr = detection.copyright
                texts_to_tally.append(Text(copyr, copyr))

    counter = tally(texts_to_tally)
    if no_detection_counter:
        counter[None] = no_detection_counter

    return counter


def tally_persons(texts):
    """
    Return a list of mapping of {value:string, count:int} given a
    list of holders strings or Text() objects.
    """
    texts_to_tally = []
    no_detection_counter = 0
    for text in texts:
        if not text:
            no_detection_counter += 1
            continue
        # Keep Text objects as-is
        if isinstance(text, Text):
            texts_to_tally.append(text)
        else:
            cano = canonical_holder(text)
            texts_to_tally.append(Text(cano, cano))

    counter = tally(texts_to_tally)

    if no_detection_counter:
        counter[None] = no_detection_counter

    return counter


def tally(summary_texts):
    """
    Return a mapping of {value: count} given a list of Text objects
    (representing either copyrights, holders or authors).
    """

    if TRACE:
        logger_debug('summarize: INITIAL texts:')
        for s in summary_texts:
            logger_debug('    ', s)

    for text in summary_texts:
        text.normalize()

    if TRACE_DEEP:
        logger_debug('summarize: NORMALIZED 1 texts:')
        for s in summary_texts:
            logger_debug('      ', s)

    texts = list(filter_junk(summary_texts))

    if TRACE_DEEP:
        logger_debug('summarize: DEJUNKED texts:')
        for s in summary_texts:
            logger_debug('        ', s)

    for t in texts:
        t.normalize()

    if TRACE_DEEP:
        logger_debug('summarize: NORMALIZED 2 texts:')
        for s in summary_texts:
            logger_debug('          ', s)

    # keep non-empties
    texts = list(t for t in texts if t.key)

    if TRACE_DEEP:
        logger_debug('summarize: NON-EMPTY 1 texts:')
        for s in summary_texts:
            logger_debug('            ', s)

    # convert to plain ASCII, then fingerprint
    for t in texts:
        t.transliterate()

    if TRACE_DEEP:
        logger_debug('summarize: ASCII texts:')
        for s in summary_texts:
            logger_debug('              ', s)

    for t in texts:
        t.fingerprint()

    if TRACE_DEEP or TRACE_FP:
        logger_debug('summarize: FINGERPRINTED texts:')
        for s in summary_texts:
            logger_debug('                ', s)

    # keep non-empties
    texts = list(t for t in texts if t.key)

    if TRACE_DEEP:
        logger_debug('summarize: NON-EMPTY 2 texts:')
        for s in summary_texts:
            logger_debug('                  ', s)

    # cluster
    clusters = cluster(texts)
    if TRACE_DEEP:
        clusters = list(clusters)
        logger_debug('summarize: CLUSTERS:')
        for c in clusters:
            logger_debug('                    ', c)

    counter = {text.original: count for text, count in clusters}

    if TRACE:
        logger_debug('summarize: FINAL SUMMARIZED:')
        for c in counter:
            logger_debug('      ', c)
    return counter


def cluster(texts):
    """
    Given a `texts` iterable of Text objects, group these objects when they have the
    same key. Yield a tuple of (Text object, count of its occurences).
    """
    clusters = defaultdict(list)
    for text in texts:
        clusters[text.key].append(text)

    for cluster_key, cluster_texts in clusters.items():
        try:
            # keep the longest as the representative value for a cluster
            cluster_texts.sort(key=lambda x:-len(x.key))
            representative = cluster_texts[0]
            count = sum(t.count for t in cluster_texts)
            if TRACE_DEEP:
                logger_debug('cluster: representative, count', representative, count)
            yield representative, count
        except Exception as e:
            msg = (
                f'Error in cluster(): cluster_key: {cluster_key!r}, '
                f'cluster_texts: {cluster_texts!r}\n'
            )
            import traceback
            msg += traceback.format_exc()
            raise Exception(msg) from e


def clean(text):
    """
    Return an updated and cleaned Text object from a `text` Text object
    normalizing some pucntuations around some name and acronyms.
    """
    if not text:
        return text
    text = text.replace('A. M.', 'A.M.')
    return text


# set of common prefixes that can be trimmed from a name
prefixes = frozenset([
    'his',
    'by',
    'from',
    'and',
    'of',
    'for',
    '<p>',
])


def strip_prefixes(s, prefixes=prefixes):
    """
    Return the `s` string with any of the string in the `prefixes` set
    striped from the left. Normalize and strip spaces.

    For example:
    >>> s = 'by AND for the Free Software Foundation'
    >>> strip_prefixes(s) == 'the Free Software Foundation'
    True
    """
    s = s.split()
    while s and s[0].lower().strip().strip('.,') in prefixes:
        s = s[1:]
    return ' '.join(s)


# set of suffixes that can be stripped from a name
suffixes = frozenset([
    '(minizip)',
])


def strip_suffixes(s, suffixes=suffixes):
    """
    Return the `s` string with any of the string in the `suffixes` set
    striped from the right. Normalize and strip spaces.

    For example:
    >>> s = 'RedHat Inc corp'
    >>> strip_suffixes(s, set(['corp'])) == 'RedHat Inc'
    True
    """
    s = s.split()
    while s and s[-1].lower().strip().strip('.,') in suffixes:
        s = s[:-1]
    return u' '.join(s)


# TODO: we need a gazeteer of places and or use usaddress and probablepeople or
# refine the POS tagging to catch these better
JUNK_HOLDERS = frozenset([
    'advanced computing',
    'inc',
    'llc',
    'ltd',
    'berlin',
    'munich',
    'massachusetts',
    'maynard',
    'cambridge',
    'norway',
    'and',
    'is',
    'a',
    'cedar rapids',
    'iowa',
    'u.s.a',
    'u.s.a.',
    'usa',
    'source code',
    'mountain view',
    'england',
    'web applications',
    'menlo park',
    'california',
    'irvine',
    'pune',
    'india',
    'stockholm',
    'sweden',
    'sweden)',
    'software',
    'france',
    'concord',
    'date here',
    'software',
    'not',
])


def filter_junk(texts):
    """
    Filter junk from an iterable of texts objects.
    """
    for text in texts:
        if not text.key:
            continue
        if text.key.lower() in JUNK_HOLDERS:
            continue
        if text.key.isdigit():
            continue
        if len(text.key) == 1:
            continue
        yield text


# Mapping of commonly abbreviated names to their expanded, canonical forms.
# This is mostly of use when these common names show as holders without their
# proper company suffix


COMMON_NAMES = {
    '3dfxinteractiveinc.': '3dfx Interactive',

    'cern': 'CERN - European Organization for Nuclear Research',

    'ciscosystemsinc': 'Cisco Systems',
    'ciscosystems': 'Cisco Systems',
    'cisco': 'Cisco Systems',

    'daisy': 'Daisy',
    'daisyltd': 'Daisy',

    'fsf': 'Free Software Foundation',
    'freesoftwarefoundation': 'Free Software Foundation',
    'freesoftwarefoundationinc': 'Free Software Foundation',
    'thefreesoftwarefoundation': 'Free Software Foundation',
    'thefreesoftwarefoundationinc': 'Free Software Foundation',

    'hp': 'Hewlett-Packard',
    'hewlettpackard': 'Hewlett-Packard',
    'hewlettpackardco': 'Hewlett-Packard',
    'hpcompany': 'Hewlett-Packard',
    'hpdevelopmentcompanylp': 'Hewlett-Packard',
    'hpdevelopmentcompany': 'Hewlett-Packard',
    'hewlettpackardcompany': 'Hewlett-Packard',

    'theandroidopensourceproject': 'Android Open Source Project',
    'androidopensourceproject': 'Android Open Source Project',

    'ibm': 'IBM',

    'redhat': 'Red Hat',
    'redhatinc': 'Red Hat',

    'softwareinthepublicinterest': 'Software in the Public Interest',
    'spiinc': 'Software in the Public Interest',

    'suse': 'SuSE',
    'suseinc': 'SuSE',

    'sunmicrosystems': 'Sun Microsystems',
    'sunmicrosystemsinc': 'Sun Microsystems',
    'sunmicro': 'Sun Microsystems',

    'thaiopensourcesoftwarecenter': 'Thai Open Source Software Center',

    'apachefoundation': 'The Apache Software Foundation',
    'apachegroup': 'The Apache Software Foundation',
    'apache': 'The Apache Software Foundation',
    'apachesoftwarefoundation': 'The Apache Software Foundation',
    'theapachegroup': 'The Apache Software Foundation',

    'eclipse': 'The Eclipse Foundation',
    'eclipsefoundation': 'The Eclipse Foundation',

    'regentsoftheuniversityofcalifornia': 'The Regents of the University of California',

    'borland': 'Borland',
    'borlandcorp': 'Borland',

    'microsoft': 'Microsoft',
    'microsoftcorp': 'Microsoft',
    'microsoftinc': 'Microsoft',
    'microsoftcorporation': 'Microsoft',

    'google': 'Google',
    'googlellc': 'Google',
    'googleinc': 'Google',

    'intel': 'Intel',
}

# Remove everything except letters and numbers
_keep_only_chars = re.compile('[_\\W]+', re.UNICODE).sub  # NOQA


def keep_only_chars(s):
    return _keep_only_chars('', s)


def canonical_holder(s):
    """
    Return a canonical holder for string `s` or s.
    """
    key = keep_only_chars(s).lower()
    cano = COMMON_NAMES.get(key)
    if TRACE_CANO:
        logger_debug('cano: for s:', s, 'with key:', key, 'is cano:', cano)
    s = cano or s
    s = strip_suffixes(s)
    return s
