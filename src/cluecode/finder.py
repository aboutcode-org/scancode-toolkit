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

from __future__ import absolute_import, print_function

import re
import string
import logging

try:
    import urlparse
except ImportError:
    # For Python 3
    import urllib.parse as urlparse

import url as urlpy
import ipaddress

from textcode import analysis
from cluecode import finder_data


LOG = logging.getLogger(__name__)

DEBUG = False

if DEBUG:
    from pprint import pformat  # @UnusedImport


def find(location, patterns):
    """
    Yield match and matched lines for patterns found in file at location. as a
    tuple of (key, found text, text line). Pattern is list of tuples (key,
    compiled regex).

    Note: the location can be a list of lines for testing convenience.
    """
    if DEBUG:
        loc = pformat(location)
        print('find(location=%(loc)r,\n  patterns=%(patterns)r)' % locals())

    for line in analysis.text_lines(location):
        for key, pattern in patterns:
            for match in pattern.findall(line):

                if DEBUG:
                    print('find: yielding match: key=%(key)r, '
                          'match=%(match)r,\n    line=%(line)r' % locals())
                yield key, unicode(match), line


def unique_filter(matches):
    """
    Iterate over matches and yield unique matches.
    """
    uniques = set()
    for key, match, line in matches:
        if (key, match,) not in uniques:
            uniques.add((key, match,))
            yield key, match, line


def apply_filters(matches, *filters):
    """
    Apply filters to a `matches` iterable. Return a new matches iterable.

    A filter must accept a single arg: an iterable of tuples of (key, match,
    line) and must return an iterable of tuples of (key, match, line).
    """
    for filt in filters:
        matches = filt(matches)
    return matches


def build_regex_filter(pattern):
    """
    Return a filter function using regex pattern, filtering out matches
    matching this regex. The pattern should be text, not a compiled re.
    """
    def re_filt(matches):
        for key, match, line in matches:
            if re.match(regex, match):
                if DEBUG:
                    print('build_regex_filter(pattern=%(pattern)r: '
                          'filtering match: %(match)r' % locals())
                continue
            yield key, match, line


    regex = re.compile(pattern, re.UNICODE | re.I)
    return re_filt


# A good reference page of email address regex is:
# http://fightingforalostcause.net/misc/2006/compare-email-regex.php email
# regex from http://www.regular-expressions.info/regexbuddy/email.html


def emails_regex():
    return re.compile(r'\b[A-Z0-9._%-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b', re.I)


def find_emails(location):
    """
    Yield emails found in file at location.
    """
    patterns = [('emails', emails_regex(),)]
    matches = find(location, patterns)
    email_filters = (junk_email_domains_filter, unique_filter,)
    matches = apply_filters(matches, *email_filters)
    for _key, email, _line in matches:
        yield email


def junk_email_domains_filter(matches):
    """
    Given an iterable of email matches, return an iterable where email with
    common uninteresting domains have been removed, such as local, non public
    or example.com emails.
    """
    for key, email, line in matches:
        domain = email.split('@')[-1]
        if not is_good_host(domain):
            continue
        yield key, email, line


def uninteresting_emails_filter(matches):
    """
    Given an iterable of emails matches, return an iterable where common
    uninteresting emails have been removed.
    """
    for key, email, line in matches:
        good_email = finder_data.classify_email(email)
        if not good_email:
            continue
        yield key, email, line


# TODO: consider: http://www.regexguru.com/2008/11/detecting-urls-in-a-block-of-text/
def urls_regex():
    return re.compile(r'('
                      r'(?:http|ftp|sftp)[s]?://[^\s<>\[\]"]+'
                      r'|(?:www|ftp)\.[^\s<>\[\]"]+'
                      r')', re.UNICODE | re.I)


INVALID_URLS_PATTERN = '(ht|f)tp[s]?://([$%*/_])+'

def find_urls(location):
    """
    Yield urls found in file at location.
    """
    patterns = [('urls', urls_regex(),)]
    matches = find(location, patterns)

    url_filters = (
        verbatim_crlf_url_cleaner,
        end_of_url_cleaner,
        empty_urls_filter,
        scheme_adder,
        user_pass_cleaning_filter,
        build_regex_filter(INVALID_URLS_PATTERN),
        canonical_url_cleaner,
        junk_url_hosts_filter,
        junk_urls_filter,
        unique_filter,
    )


    # the order of filters IS important
    matches = apply_filters(matches, url_filters)
    for _key, url, _line in matches:
        yield unicode(url)


EMPTY_URLS = set(['https', 'http', 'ftp', 'www', ])


def empty_urls_filter(matches):
    """
    Given an iterable of URL matches, return an iterable without empty URLs.
    """
    for key, match, line in matches:
        junk = match.lower().strip(string.punctuation).strip()
        if not junk or junk in EMPTY_URLS:
            if DEBUG:
                print('empty_urls_filter: filtering match: %(match)r'
                      % locals())
            continue
        yield key, match, line


def verbatim_crlf_url_cleaner(matches):
    """
    Given an iterable of URL matches, return an iterable where literal end of
    lines and carriage return characters that may show up as-is, un-encoded in
    a URL have been removed.
    """
    # FIXME: when is this possible and could happen?
    for key, url, line in matches:
        if not url.endswith('/'):
            url = url.replace(r'\n', '')
            url = url.replace(r'\r', '')
        yield key, url, line


def end_of_url_cleaner(matches):
    """
    Given an iterable of URL matches, return an iterable where junk characters
    commonly found at the end of a URL are removed.
    """
    for key, url, line in matches:
        if not url.endswith('/'):
            url = url.replace(u'&lt;', u'<')
            url = url.replace(u'&gt;', u'>')
            url = url.replace(u'&amp;', u'&')
            url = url.rstrip(string.punctuation)
            url = url.split(u'\\')[0]
            url = url.split(u'<')[0]
            url = url.split(u'>')[0]
            url = url.split(u'(')[0]
            url = url.split(u')')[0]
            url = url.split(u'[')[0]
            url = url.split(u']')[0]
            url = url.split(u'"')[0]
            url = url.split(u"'")[0]
        yield key, url, line


def scheme_adder(matches):
    """
    Add a fake http:// scheme if there was none.
    """
    for key, match, line in matches:
        match = add_fake_scheme(match)
        yield key, match, line


def add_fake_scheme(url):
    """
    Add a fake http:// scheme to URL if has none.
    """
    parsed = urlparse.urlparse(url)
    if not parsed.scheme:
        url = u'http://' + url.lstrip(u':/').strip()
    return url


def has_scheme(url):
    """
    Return True if url has a scheme.
    """
    # TODO: IMPLEMENT ME!!


def user_pass_cleaning_filter(matches):
    """
    Given an iterable of URL matches, return an iterable where user and
    password are removed from the URLs host.
    """
    for key, match, line in matches:
        host, _domain = url_host_domain(match)
        if not host:
            if DEBUG:
                print('user_pass_cleaning_filter: '
                      'filtering match(no host): %(match)r' % locals())
            continue
        if '@' in host:
            # strips any user/pass
            host = host.split(u'@')[-1]
        yield key, match, line


def canonical_url(uri):
    """
    Return the canonical representation of a given URI.
    This assumes the `uri` has a scheme.
    
    * When a default port corresponding for the scheme is explicitly declared
      (such as port 80 for http), the port will be removed from the output.
    * Fragments '#' are not removed. 
     * Params and query string arguments are not reordered.
    """
    normalized = urlpy.parse(uri).sanitize().punycode()
    if normalized._port == urlpy.PORTS.get(normalized._scheme, None):
        normalized._port = None
    return normalized.utf8()


def canonical_url_cleaner(matches):
    """
    Given an iterable of URL matches, return an iterable where URLs have been
    canonicalized.
    """
    for key, match, line in matches:
        canonic = canonical_url(match)
        if DEBUG:
            print('canonical_url_cleaner: '
                  'match=%(match)r, canonic=%(canonic)r' % locals())
        yield key, canonic , line


IP_V4_RE = r'^(\d{1,3}\.){0,3}\d{1,3}$'

def is_ip_v4(s):
    return re.compile(IP_V4_RE).match(s)


IP_V6_RE = (
    r'^([0-9a-f]{0,4}:){2,7}[0-9a-f]{0,4}$'
    '|'
    r'^([0-9a-f]{0,4}:){2,6}(\d{1,3}\.){0,3}\d{1,3}$'
)


def is_ip_v6(s):
    """
    Return True is string s is an IP V6 ADDRESS
    """
    return re.compile(IP_V6_RE).match(s)


def is_ip(s):
    """
    Return True is string s is an IP ADDRESS
    """
    return is_ip_v4(s) or is_ip_v6(s)


def get_ip(s):
    """
    Return True is string s is an IP ADDRESS
    """
    if not is_ip(s):
        return False

    try:
        ip = ipaddress.ip_address(unicode(s))
        return ip
    except ValueError:
        return False


def is_private_ip(ip):
    """
    Return true if ip object is a private or local IP.
    """
    if ip:
        if isinstance(ip, ipaddress.IPv4Address):
            private = (
                ip.is_reserved
                or ip.is_private
                or ip.is_multicast
                or ip.is_unspecified
                or ip.is_loopback
                or ip.is_link_local
            )
        else:
            private(
                ip.is_multicast
                or ip.is_reserved
                or ip.is_link_local
                or ip.is_site_local
                or ip.is_private
                or ip.is_unspecified
                or ip.is_loopback
            )
        return private


def is_good_host(host):
    """
    Return True if the host is not some local or uninteresting host.
    """
    if not host:
        return False

    ip = get_ip(host)
    if ip:
        if is_private_ip(ip):
            return False
        return finder_data.classify_ip(host)


    # at this stage we have a host name, not an IP

    if '.' not in host:
        # private hostnames not in a domain, including localhost
        return False

    good_host = finder_data.classify_host(host)
    return good_host


def url_host_domain(url):
    """
    Return a tuple of the (host, domain) of a URL or None. Assumes that the
    URL has a scheme.
    """
    parsed = urlpy.parse(url)
    host = parsed._host
    if not host:
        return None, None
    host = host.lower()
    domain = parsed.pld().lower()
    return host, domain


def junk_url_hosts_filter(matches):
    """
    Given an iterable of URL matches, return an iterable where URLs with
    common uninteresting hosts or domains have been removed, such as local,
    non public or example.com URLs.
    """
    for key, match, line in matches:
        host, domain = url_host_domain(match)
        if not is_good_host(host):
            if DEBUG:
                print('junk_url_hosts_filter: '
                      '!is_good_host:%(host)r): %(match)r' % locals())
            continue
        elif not is_good_host(domain) and not is_ip(host):
            if DEBUG:
                print('junk_url_hosts_filter: ''!is_good_host:%(domain)r '
                      'and !is_ip:%(host)r: %(match)r' % locals())
            continue
        yield key, match, line


def junk_urls_filter(matches):
    """
    Given an iterable of URL matches, return an iterable where URLs with
    common uninteresting URLs, or uninteresting URL hosts or domains have been
    removed, such as local, non public or example.com URLs.
    """
    for key, match, line in matches:
        good_url = finder_data.classify_url(match)
        if not good_url:
            if DEBUG:
                print('junk_url_filter: %(match)r' % locals())
            continue
        yield key, match, line


def find_pattern(location, pattern):
    """
    Find regex pattern in the text lines of file at location.
    Return all match groups joined as one unicode string.
    """
    pattern = re.compile(pattern, re.UNICODE | re.I)
    found = find(location, [(None, pattern,)])
    for _key, match , _line in found:
        yield match
