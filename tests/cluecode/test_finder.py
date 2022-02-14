# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import re
from unittest.case import expectedFailure

from commoncode.testcase import FileBasedTesting

from cluecode import finder
from cluecode import finder_data
from cluecode.finder import find
from cluecode.finder import urls_regex


def find_emails_tester(lines_or_location, with_lineno=False, unique=True):
    return _find_tester(finder.find_emails, lines_or_location, with_lineno, unique)


def find_urls_tester(lines_or_location, with_lineno=False, unique=True):
    return _find_tester(finder.find_urls, lines_or_location, with_lineno, unique)


def _find_tester(func, lines_or_location, with_lineno=False, unique=True):
    """
    Helper function for testing URLs or emails with or without line numbers.
    """
    result = list(func(lines_or_location, unique))
    if not with_lineno:
        result = [val for val, _ln in result]
    return result


class TestEmail(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_emails_regex(self):
        test_file = self.get_test_loc('finder/email/3w-xxxx.c')
        test_input = open(test_file).read()
        expected = [
            u'linux@3ware.com',
            u'linux@3ware.com',
            u'acme@conectiva.com.br',
            u'linux@3ware.com',
            u'andre@suse.com',
            u'andre@suse.com',
            u'linux@3ware.com'
        ]
        result = re.findall(finder.emails_regex(), test_input)
        assert result == expected

    def test_find_emails_in_c(self):
        test_file = self.get_test_loc('finder/email/3w-xxxx.c')
        expected = [
            'linux@3ware.com',
            'acme@conectiva.com.br',
            'andre@suse.com'
        ]
        result = find_emails_tester(test_file)
        assert result == expected

    def test_find_emails_in_python1(self):
        test_file = self.get_test_loc('finder/email/jardiff.py')
        expected = ['jp_py@demonseed.net']
        result = find_emails_tester(test_file)
        assert result == expected

    def test_find_emails_in_python2(self):
        test_file = self.get_test_loc('finder/email/thomas.py')
        expected = ['amir@divmod.org']
        result = find_emails_tester(test_file)
        assert result == expected

    def test_find_emails_does_not_return_bogus_emails(self):
        lines = [
            'gpt@40000a00',
            'xml.@summary',
            'xml.@detail',
            'xml.@loggedIn.toXMLString',
            'xml.@noPasswordExists',
            'historyDataGrid.selectedItem.@serialNumber',
            'constant.@name',
            'constant.@type',
            'dac.dacDataGrid.selectedItem.@dbUsername',
            'dac.dacDataGrid.selectedItem.@hostName',
            'dac.dacDataGrid.selectedItem.@name',
            'dac.dacDataGrid.selectedItem.@description',
            'dac.dacDataGrid.selectedItem.@dbPassword',
        ]
        expected = []
        result = find_emails_tester(lines)
        assert result == expected

    def test_find_emails_does_not_return_png(self):
        lines = ['navigation-logo@2x.png']
        expected = []
        result = find_emails_tester(lines)
        assert result == expected

    def test_find_emails_does_not_return_incomplete_emails_or_example_emails(self):
        lines = ['user@...', 'thomas@...', '*@example.com', 'user@localhost']
        expected = []
        result = find_emails_tester(lines)
        assert result == expected

    def test_find_emails_filters_unique_by_default(self):
        lines = ['user@me.com', 'user@me.com']
        expected = ['user@me.com']
        result = find_emails_tester(lines)
        assert result == expected

    def test_find_emails_does_not_filter_unique_if_requested(self):
        lines = ['user@me.com', 'user@me.com']
        expected = ['user@me.com', 'user@me.com']
        result = find_emails_tester(lines, unique=False)
        assert result == expected

    def test_find_emails_does_return_line_number(self):
        lines = ['user@me.com', 'user2@me.com']
        expected = [('user@me.com', 1), ('user2@me.com', 2)]
        result = find_emails_tester(lines, with_lineno=True)
        assert result == expected

    def test_find_emails_does_not_return_junk(self):
        lines = '''
            (akpm@linux-foundation.org) serves as a maintainer of last resort.
            of your patch set.  linux-kernel@vger.kernel.org functions as a list of
            Linux kernel.  His e-mail address is <torvalds@linux-foundation.org>.
            to security@kernel.org.  For severe bugs, a short embargo may be considered
              Cc: stable@vger.kernel.org
            linux-api@vger.kernel.org.
            trivial@kernel.org which collects "trivial" patches. Have a look
                Signed-off-by: Random J Developer <random@developer.example.org>
                Signed-off-by: Random J Developer <random@developer.example.org>
                [lucky@maintainer.example.org: struct foo moved from foo.c to foo.h]
                Signed-off-by: Lucky K Maintainer <lucky@maintainer.example.org>
                    From: Original Author <author@example.com>
        '''.splitlines(False)
        expected = [
            u'akpm@linux-foundation.org',
            u'linux-kernel@vger.kernel.org',
            u'torvalds@linux-foundation.org',
            u'security@kernel.org',
            u'stable@vger.kernel.org',
            u'linux-api@vger.kernel.org',
            u'trivial@kernel.org'
        ]
        result = find_emails_tester(lines, with_lineno=False)
        assert result == expected

    def test_emails_does_filter_junk_domains(self):
        test_file = self.get_test_loc('finder/email/Content.json')
        expected = []
        result = find_emails_tester(test_file)
        assert result == expected

    def test_emails_does_filter_junk_gibberish_domains(self):
        test_file = self.get_test_loc('finder/email/gibberish-bug-6H.txt')
        expected = []
        result = find_emails_tester(test_file)
        assert result == expected

    def test_finder_classify_host_as_ok_for_gibberish(self):
        assert finder_data.classify_host("FO.LwfT")

    def test_is_good_email_domain_classify_host_as_bad_for_gibberish(self):
        assert not finder.is_good_email_domain("foo@FO.LwfT")

    def test_emails_for_ignored_hosts(self):
        test_string = '''
        Perhaps an email host that should be ignored from ignored_hosts
        would be of the form <abc@something.com>. Another possible
        domain name that the filter should be ignored would probably be
        <xyz@any.com>. However, an email such as <efg@many.org> should
        not be filtered as spam.
        Adding more test cases, how about <abc@example.com> or a slightly
        more different email such as <diff@xyz@other.com>.
        '''.splitlines(False)
        expected = [
            u'efg@many.org'
        ]
        result = find_emails_tester(test_string, with_lineno=False)
        assert result == expected


class TestUrl(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_urls_regex_without_http(self):
        result = re.match(finder.urls_regex(),
                        u'www.something.domain.tld').group()
        expected = u'www.something.domain.tld'
        assert result == expected

    def test_urls_regex(self):
        test_file = self.get_test_loc('finder/url/BeautifulSoup.py')
        test_input = open(test_file).read()
        expected = [
            u'http://www.crummy.com/software/BeautifulSoup/',
            u'http://chardet.feedparser.org/',
            u'http://cjkpython.i18n.org/',
            u'http://www.crummy.com/software/BeautifulSoup/documentation.html',
            u'http://chardet.feedparser.org/',
            u'http://cjkpython.i18n.org/',
        ]
        assert re.findall(finder.urls_regex(), test_input) == expected

    def test_canonical_url(self):
        data = (
            ('http://www.nexb.com', 'http://www.nexb.com/'),
            ('http://www.nexb.com/#12', 'http://www.nexb.com/#12'),
            ('http://www.nexb.com/a/b/../../c/', 'http://www.nexb.com/c/'),
            ('http://www.nexb.com:80', 'http://www.nexb.com/'),
            ('https://www.nexb.com:443', 'https://www.nexb.com/'),
            ('http://www.nexb.com:443', 'http://www.nexb.com:443/'),
            ('https://www.nexb.com:80', 'https://www.nexb.com:80/'),
            ('http://www.nexb.com/A 0.0.1 Alpha/a_0_0_1.zip',
             'http://www.nexb.com/A%200.0.1%20Alpha/a_0_0_1.zip'),
        )

        for test, expected in data:
            assert finder.canonical_url(test) == expected

    def test_find_urls_returns_unique(self):
        lines = [
            r"http://alaphalinu.org').",
            r'http://alaphalinu.org/bridge.',
            r'http://alaphalinu.org.',
            r"http://alaphalinu.org''.",
            r"http://alaphalinu.org',",
            r'http://alaphalinu.org>',
            r'http://alaphalinu.org>;',
            r'http://alaphalinu.org>.',
            r'http://alaphalinu.org/.',
            r'http://alaphalinu.org/>',
            r'http://alaphalinu.org/)',
            r'http://alaphalinu.org/>)',
            r'http://alaphalinu.org/">)',
            r'http://alaphalinu.org/>),',
            r'http://alaphalinu.org/tst.htm]',
            r'http://alaphalinu.org/tst.html.',
            r'http://alaphalinu.org/isc\\fR.',
            r'http://alaphalinu.org/isc.txt,',
            r'http://alaphalinu.org/isc.html\\n',
            r'http://alaphalinu.org/somedir/\\n',
            r'http://kernelnewbies.org/</ulink>).',
            r'http://kernelnewbies.org/(ulink).',
            r'http://alaphalinu.org/isc\fR.',
            r'http://alaphalinu.org/isc.html\n',
            r'http://alaphalinu.org/somedir/\n'
        ]
        expected = [
            u'http://alaphalinu.org/',
            u'http://alaphalinu.org/bridge',
            u'http://alaphalinu.org/tst.htm',
            u'http://alaphalinu.org/tst.html',
            u'http://alaphalinu.org/isc',
            u'http://alaphalinu.org/isc.txt',
            u'http://alaphalinu.org/isc.html',
            u'http://alaphalinu.org/somedir/',
            u'http://kernelnewbies.org/',
        ]
        result = find_urls_tester(lines)
        assert result == expected

    def test_find_urls_does_not_return_local_urls(self):
        lines = [
            'http://localhost',
            'http://localhost/',
            'http://localhost:8080',
            'http://localhost/dir/page.html',
            'http://127.0.0.1',
            'http://127.0.0.1:4029',
            'http://127.0.0.1/dir',
            'http://127.0.0.1/',
            'http://127.0.0.1/page.htm',
        ]
        expected = []
        result = find_urls_tester(lines)
        assert result == expected

    def test_find_urls_does_not_return_local_ip(self):
        lines = [
            'http://localhost',
            'http://localhost/',
            'http://localhost:8080',
            'http://localhost/dir/page.html',
            'http://127.0.0.1',
            'http://127.0.0.1:4029',
            'http://127.0.0.1/dir',
            'http://127.0.0.1/',
            'http://127.0.0.1/page.htm',
            'http://192.168.0.1',
            'http://10.0.0.1',
            'http://10.255.255.124',
            'http://169.254.0.0',
            'http://172.16.0.0',
            'http://172.31.255.255',
            'http://172.32.120.155',
            'http://localhost',
            'http://fc00:ffff:ffff:ffff::',
        ]
        expected = [u'http://172.32.120.155/']
        result = find_urls_tester(lines)
        assert result == expected

    def test_is_good_host(self):
        assert finder.is_good_host('172.32.120.155')

    def test_url_host_domain(self):
        result = finder.url_host_domain('http://svn.codehaus.org')
        expected = ('svn.codehaus.org', 'codehaus.org',)
        assert result == expected

    def test_find_urls_filters_bogus_url(self):
        lines = [u'http://__________________']
        expected = []
        result = find_urls_tester(lines)
        assert result == expected

    def test_find_urls_with_square_brackets_from_trac_wiki_html(self):
        lines = ['title="Link: [http://www.somedo.com/ Example]"']
        expected = ['http://www.somedo.com/']
        result = find_urls_tester(lines)
        assert result == expected

    def test_find_urls_in_pom(self):
        lines = [
            'https://svn.codehaus.org/plexus/tags</tagBase>',
            'http://svn.codehaus.org/plexus-interactivity-api</developerConnection>',
            'https://svn.codehaus.org//plexus-container-default</developerConnection>',
            'https://svn.codehaus.org/plexus/trunk/plexus-utils</developerConnection>',
            'https://svn.codehaus.org/plexus/trunk</developerConnection>',
            'https://svn.codehaus.org/plexus/trunk</developerConnection>',
            'https://svn.codehaus.org/plexus/trunk</developerConnection>',
            'https://svn.codehaus.org/qdox/tags/qdox-1.9</connection>',
            'https://svn.codehaus.org/qdox/tags/qdox-1.9</developerConnection>',
            'https://svn.codehaus.org/qdox/tags</tagBase>',
            'https://svn.codehaus.org/xstream/tags/XSTREAM_1_2_2</connection>',
            'https://svn.codehaus.org/xstream/tags/XSTREAM_1_2_2</developerConnection>',
            'https://svn.codehaus.org/xstream/tags/XSTREAM_1_2_2</url>',
            'https://svn.codehaus.org/xstream/tags</tagBase>',
            'https://svn.sourceforge.net/svnroot/jtidy/trunk/jtidy/</connection>',
            'https://svn.sourceforge.net/svn/jtidy/trunk/jtidy/</developerConnection>'
        ]
        expected = [
            u'https://svn.codehaus.org/plexus/tags',
            u'http://svn.codehaus.org/plexus-interactivity-api',
            u'https://svn.codehaus.org/plexus-container-default',
            u'https://svn.codehaus.org/plexus/trunk/plexus-utils',
            u'https://svn.codehaus.org/plexus/trunk',
            u'https://svn.codehaus.org/qdox/tags/qdox-1.9',
            u'https://svn.codehaus.org/qdox/tags',
            u'https://svn.codehaus.org/xstream/tags/XSTREAM_1_2_2',
            u'https://svn.codehaus.org/xstream/tags',
            u'https://svn.sourceforge.net/svnroot/jtidy/trunk/jtidy/',
            u'https://svn.sourceforge.net/svn/jtidy/trunk/jtidy/',
        ]
        result = find_urls_tester(lines)
        assert result == expected

    def test_find_urls_in_file_with_markup_in_code(self):
        test_file = self.get_test_loc('finder/url/markup_in_code.c')
        expected = [
            u'http://xml.libexpat.org/dummy.ent',
            u'http://xml.libexpat.org/e',
            u'http://xml.libexpat.org/n',
            u'http://expat.sf.net/',
            u'http://xml.libexpat.org/',
            u'http://xml.libexpat.org/doc.dtd',
            u'http://xml.libexpat.org/entity.ent',
            u'http://xml.libexpat.org/ns1'
        ]
        result = find_urls_tester(test_file)
        assert result == expected

    def test_find_urls_does_not_return_duplicate_urls_by_default(self):
        test_file = self.get_test_loc('finder/url/nodupe.htm')
        expected = [
            u'http://nexb.com/',
            u'http://trac.edgewall.org/',
            u'http://www.edgewall.org/',
        ]
        result = find_urls_tester(test_file)
        assert result == expected

    def test_find_urls__does_not_return_junk_urls(self):
        test_file = self.get_test_loc('finder/url/junk_urls.c')
        expected = []
        result = find_urls_tester(test_file)
        assert result == expected

    def test_find_urls_detects_urls_correcty_in_html(self):
        test_file = self.get_test_loc('finder/url/some_html.htm')
        expected = [
            u'https://somesite.com/trac/instance/search',
            u'https://somesite.com/trac/instance/ticket/815',
            u'https://somesite.com/trac/instance/ticket/1679',
            u'https://somesite.com/trac/instance/wiki/TracGuide',
            u'https://somesite.com/trac/instance/ticket/816?format=csv',
            u'https://somesite.com/trac/instance/ticket/816?format=tab',
            u'https://somesite.com/trac/instance/ticket/816?format=rss',
            u'https://somesite.com/trac/instance/ticket/817',
            u'https://somesite.com/trac/instance/wiki',
            u'https://somesite.com/trac/instance/ticket/1',
            u'https://somesite.com/trac/instance/chrome/common/favicon.ico',
            u'https://somesite.com/trac/instance/search/opensearch',
            u'http://company.com/',
            u'https://somesite.com/trac/instance/logout',
            u'https://somesite.com/trac/instance/about',
            u'https://somesite.com/trac/instance/prefs',
            u'https://somesite.com/trac/instance/timeline',
            u'https://somesite.com/trac/instance/roadmap',
            u'https://somesite.com/trac/instance/browser',
            u'https://somesite.com/trac/instance/report',
            u'https://somesite.com/trac/instance/newticket',
            u'https://somesite.com/trac/instance/admin',
            u'https://somesite.com/trac/instance/importer',
            u'https://somesite.com/trac/instance/build',
            u'https://somesite.com/trac/instance/timeline?from=2009-04-28T18:46:08Z-0700&precision=second',
            u'https://somesite.com/trac/instance/timeline?from=2009-09-21T16:26:19Z-0700&precision=second',
            u'http://alaphalinu.org/',
            u'http://alaphalinu.org/bridge',
            u'http://alaphalinu.org/tst.htm',
            u'http://alaphalinu.org/tst.html',
            u'http://alaphalinu.org/isc',
            u'http://alaphalinu.org/isc.txt',
            u'http://alaphalinu.org/isc.html',
            u'http://alaphalinu.org/somedir/',
            u'http://kernelnewbies.org/',
            u'https://somesite.com/trac/instance/timeline?from=2009-04-28T18:46:50Z-0700&precision=second',
            u'https://somesite.com/trac/instance/timeline?from=2009-08-02T23:48:27Z-0700&precision=second',
            u'https://somesite.com/trac/instance/timeline?from=2009-08-03T21:13:02Z-0700&precision=second',
            u'http://alaphalinu.org/somedir',
            u'https://somesite.com/trac/instance/timeline?from=2009-09-15T14:58:31Z-0700&precision=second',
            u'https://somesite.com/trac/instance/timeline?from=2009-09-15T14:58:44Z-0700&precision=second',
            u'https://somesite.com/trac/instance/timeline?from=2009-09-18T15:22:56Z-0700&precision=second',
            u'https://somesite.com/trac/instance/changeset/3115',
            u'https://somesite.com/trac/instance/timeline?from=2009-09-21T16:26:08Z-0700&precision=second',
            u'https://somesite.com/trac/instance/changeset/3119',
            u'https://somesite.com/trac/instance/wiki/WikiFormatting',
            u'http://www.somesite.com/',
            u'https://somesite.com/trac/instance/wiki/TracTickets',
            u'http://trac.edgewall.org/',
            u'http://www.edgewall.org/'
        ]
        result = find_urls_tester(test_file)
        assert result == expected

    def test_find_urls_without_scheme_in_lines(self):
        lines = [
            "'http://RVL4.ecn.purdue.edu/~kak/dist/BitVector-1.5.1.html'",
            'http://docs.python.org/dist/dist.html',
            'www.programming-with-objects.com',
        ]
        expected = [
            u'http://rvl4.ecn.purdue.edu/~kak/dist/BitVector-1.5.1.html',
            u'http://docs.python.org/dist/dist.html',
            u'http://www.programming-with-objects.com/',
        ]
        result = find_urls_tester(lines)
        assert result == expected

    def test_find_urls_without_scheme_in_python(self):
        test_file = self.get_test_loc('finder/url/no-scheme.py')
        expected = [
            u'http://rvl4.ecn.purdue.edu/~kak/dist/BitVector-1.5.1.html',
            u'http://docs.python.org/dist/dist.html',
            u'http://www.programming-with-objects.com/',
        ]
        result = find_urls_tester(test_file)
        assert result == expected

    def test_find_urls_filters_invalid_urls(self):
        test_file = self.get_test_loc('finder/url/truncated_url')
        result = find_urls_tester(test_file)
        expected = []
        assert result == expected

    def test_find_urls_with_fragments(self):
        test_file = self.get_test_loc('finder/url/ABOUT')
        expected = [
            u'http://pygments.org/',
            u'http://pypi.python.org/packages/2.5/P/Pygments/Pygments-0.11.1-py2.5.egg#md5=fde2a28ca83e5fca16f5ee72a67af719',
            u'http://pypi.python.org/packages/source/P/Pygments/Pygments-0.11.1.tar.gz#md5=a7dc555f316437ba5241855ac306209a',
            u'http://pypi.python.org/packages/2.4/P/Pygments/Pygments-0.11.1-py2.4.egg#md5=52d7a46a91a4a426f8fbc681c5c6f1f5',
        ]
        result = find_urls_tester(test_file)
        assert result == expected

    def test_find_urls_in_python(self):
        test_file = self.get_test_loc('finder/url/BeautifulSoup.py')
        expected = [
            u'http://www.crummy.com/software/BeautifulSoup/',
            u'http://chardet.feedparser.org/',
            u'http://cjkpython.i18n.org/',
            u'http://www.crummy.com/software/BeautifulSoup/documentation.html',
        ]
        result = find_urls_tester(test_file)
        assert result == expected

    def test_find_urls_in_java(self):
        test_file = self.get_test_loc('finder/url/IMarkerActionFilter.java')
        expected = [u'http://www.eclipse.org/legal/epl-v10.html']
        result = find_urls_tester(test_file)
        assert result == expected

    def test_find_urls_filters_unique_by_default(self):
        lines = ['http://www.me.com', 'http://www.me.com']
        expected = ['http://www.me.com/']
        result = find_urls_tester(lines)
        assert result == expected

    def test_find_urls_does_not_filter_unique_if_requested(self):
        lines = ['http://www.me.com', 'http://www.me.com']
        expected = ['http://www.me.com/', 'http://www.me.com/']
        result = find_urls_tester(lines, unique=False)
        assert result == expected

    def test_find_urls_does_return_line_number(self):
        lines = ['http://www.me.com', 'http://www.me2.com']
        expected = [('http://www.me.com/', 1), ('http://www.me2.com/', 2)]
        result = find_urls_tester(lines, with_lineno=True)
        assert result == expected

    def test_find_urls_finds_git_urls(self):
        lines = ['git@github.com:christophercantu/pipeline.git', ]
        expected = ['git@github.com:christophercantu/pipeline.git']
        result = find_urls_tester(lines)
        assert result == expected

    def test_find_urls_does_not_crash_on_weird_urls(self):
        lines = [
            '    // This listener converts chrome-extension://.../http://...pdf to',
            '    // chrome-extension://.../content/web/viewer.html?file=http%3A%2F%2F...pdf'
        ]
        expected = []
        result = find_urls_tester(lines)
        assert result == expected

    def test_find_urls_in_classfiles_does_not_return_junk_urls(self):
        test_file = self.get_test_loc('finder/url/XMLConstants.class')
        result = find_urls_tester(test_file)
        assert result == []

    def test_misc_valid_urls(self):
        # set of good URLs from https://mathiasbynens.be/demo/url-regex
        urls = u'''
            http://foo.com/blah_blah
            http://foo.com/blah_blah/
            http://142.42.1.1/
            http://142.42.1.1:8080/
            http://code.google.com/events/#&product=browser
            ftp://foo.bar/baz
            http://foo.bar/?q=Test%20URL-encoded%20stuff
        '''
        for test in urls.split():
            result = [val for val, _ln in finder.find_urls([test])]
            assert result == [test]

    def test_misc_valid_urls_reported_with_trailing_slash(self):
        # set of good URLs from https://mathiasbynens.be/demo/url-regex
        # for these, we detect but report a canonical form with a trailing slash
        urls = u'''
            http://a.b-c.de
            http://j.mp
            http://1337.net
            http://223.255.255.254
        '''
        for test in urls.split():
            result = [val for val, _ln in finder.find_urls([test])]
            assert result == [test + u'/']

    @expectedFailure
    def test_misc_valid_unicode_or_punycode_urls_that_should_pass(self):
        # At least per this set of non URLs from https://mathiasbynens.be/demo/url-regex
        urls = u'''
            http://foo.com/unicode_(✪)_in_parens
            http://✪df.ws/123
            http://➡.ws/䨹
            http://⌘.ws
            http://⌘.ws/
            http://☺.damowmow.com/
            http://مثال.إختبار
            http://例子.测试
            http://उदाहरण.परीक्षा
        '''
        for test in urls.split():
            result = [val for val, _ln in finder.find_urls([test])]
            assert result == [test]

    @expectedFailure
    def test_misc_valid_urls_that_should_pass(self):
        # At least per this set of non URLs from https://mathiasbynens.be/demo/url-regex
        urls = u'''
            http://foo.com/blah_blah_(wikipedia)
            http://foo.com/blah_blah_(wikipedia)_(again)
            http://foo.com/blah_(wikipedia)#cite-1
            http://foo.com/blah_(wikipedia)_blah#cite-1
            http://foo.com/(something)?after=parens
        '''
        for test in urls.split():
            result = [val for val, _ln in finder.find_urls([test])]
            assert result == [test]

    def test_example_dot_com_valid_urls_return_nothing(self):
        urls = u'''
            https://www.example.com/foo/?bar=baz&inga=42&quux
            http://www.example.com/wpstyle/?p=364
            http://userid:password@example.com:8080
            http://userid:password@example.com:8080/
            http://userid@example.com
            http://userid@example.com/
            http://userid@example.com:8080
            http://userid@example.com:8080/
            http://userid:password@example.com
            http://userid:password@example.com/
            http://-.~_!$&'()*+,;=:%40:80%2f::::::@example.com
        '''
        for test in urls.split():
            result = [val for val, _ln in finder.find_urls([test])]
            assert result == []

    def test_misc_invalid_urls(self):
        # set of non URLs from https://mathiasbynens.be/demo/url-regex
        urls = u'''
            http://
            http://.
            http://..
            http://../
            http://?
            http://??
            http://??/
            http://#
            http://##
            http://##/
            //
            //a
            ///a
            ///
            http:///a
            foo.com
            rdar://1234
            h://test
            http:// shouldfail.com
            :// should fail
            http://-a.b.co
            http://0.0.0.0
            http://10.1.1.0
            http://10.1.1.255
            http://224.1.1.1
            http://3628126748
            http://10.1.1.1
        '''
        for test in (u.strip() for u in urls.splitlines(False) if u and u.strip()):
            result = [val for val, _ln in finder.find_urls([test])]
            assert not result, test

    def test_misc_invalid_urls_that_should_not_crash(self):
        # set of non URLs from https://mathiasbynens.be/demo/url-regex
        urls = u'''
            http://.www.foo.bar/
            http://.www.foo.bar./
        '''
        for test in urls.split():
            result = [val for val, _ln in finder.find_urls([test])]
            assert result == []

    def test_misc_invalid_urls_that_are_still_detected_and_may_not_be_really_invalid(self):
        # set of non URLs from https://mathiasbynens.be/demo/url-regex
        urls = u'''
            http://a.b--c.de/
            http://a.b-.co
            http://123.123.123
        '''
        for test in urls.split():
            result = [val for val, _ln in finder.find_urls([test])]
            assert result in ([test] , [test + u'/'])

    def test_misc_invalid_urls_that_are_still_detected_and_normalized(self):
        # set of non URLs from https://mathiasbynens.be/demo/url-regex
        urls = u'''
            http://www.foo.bar./
        '''
        for test in urls.split():
            result = [val for val, _ln in finder.find_urls([test])]
            assert result == [test]

    def test_invalid_urls_are_not_detected(self):
        # set of non URLs from https://mathiasbynens.be/demo/url-regex
        urls = u'''
            http://1.1.1.1.1
            http://-error-.invalid/
        '''
        for test in urls.split():
            result = [val for val, _ln in finder.find_urls([test])]
            assert result == []

    def test_misc_invalid_urls_that_should_not_be_detected(self):
        # At least per this set of non URLs from https://mathiasbynens.be/demo/url-regex
        urls = u'''
            http://foo.bar?q=Spaces should be encoded
            http://foo.bar/foo(bar)baz quux
            http://a.b--c.de/
        '''
        for test in (u.strip() for u in urls.splitlines(False) if u and u.strip()):
            result = [val for val, _ln in finder.find_urls([test])]
            assert result, test

    def test_misc_invalid_urls_that_should_not_be_detected_2(self):
        # At least per this set of non URLs from https://mathiasbynens.be/demo/url-regex
        urls = u'''
            ftps://foo.bar/
        '''
        for test in (u.strip() for u in urls.splitlines(False) if u and u.strip()):
            result = [val for val, _ln in finder.find_urls([test])]
            assert result, test


    def test_common_xml_ns_url_should_not_be_detected(self):
        url = u"http://www.w3.org/XML/1998/namespace%00%00%00%00xmlns%00%00%00http:/www.w3.org/2000/xmlns/%00%00%00ixmlElement_setTagName%00%00ixmlElement_findAttributeNode%00%00%00#document#text#cdata-sectionnnMap"
        result = [val for val, _ln in finder.find_urls([url])]
        assert not result

    def test_find_urls_in_go_does_not_crash_with_unicode_error(self):
        test_file = self.get_test_loc('finder/url/verify.go')
        expected = [
            'https://tools.ietf.org/html/rfc5280#section-4.2.1.6',
            'https://tools.ietf.org/html/rfc2821#section-4.1.2',
            'https://tools.ietf.org/html/rfc2822#section-4',
            'https://tools.ietf.org/html/rfc2822#section-3.2.4',
            'https://tools.ietf.org/html/rfc3696#section-3',
            'https://tools.ietf.org/html/rfc5280#section-4.2.1.10',
            'https://tools.ietf.org/html/rfc6125#appendix-B.2'
        ]
        result = find_urls_tester(test_file)
        assert result == expected

    def test_find_urls_does_not_crash_on_mojibake_bytes(self):
        lines = [
            '    // as defined in https://tools.ietf.org/html/rfc2821#section-4.1.2”.',
        ]
        expected = ['https://tools.ietf.org/html/rfc2821#section-4.1.2']
        result = find_urls_tester(lines)
        assert result == expected

    def test_find_in_go_does_not_crash_with_unicode_error(self):
        test_file = self.get_test_loc('finder/url/verify.go')
        patterns = [('urls', urls_regex(),)]
        for _key, url, _line, _lineno in find(test_file, patterns):
            assert str == type(url)


class TestSearch(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_search_is_non_unique_by_default(self):
        test_dir = self.get_test_loc('finder/search', copy=True)
        pattern = 'Copyright'
        tests = [
            (u'addr.c', [u'Copyright', u'Copyright']),
            (u'CommandLine.java', [u'Copyright', u'Copyright']),
            (u'CustomFileFilter.java', [u'Copyright', u'Copyright']),
            (u'diskio.c', [u'copyright', u'copyright', u'copyright', u'Copyright']),
            (u'getopt_long.c', [u'Copyright']),
        ]
        for test_file, expected in tests:
            location = os.path.join(test_dir, test_file)
            result = list(s for s, _ln in finder.find_pattern(location, pattern))
            assert result == expected

    def test_search_unique(self):
        test_dir = self.get_test_loc('finder/search', copy=True)
        pattern = 'Copyright'
        tests = [
            (u'addr.c', [u'Copyright']),
            (u'CommandLine.java', [u'Copyright']),
            (u'CustomFileFilter.java', [u'Copyright', ]),
            (u'diskio.c', [u'copyright', u'Copyright']),
            (u'getopt_long.c', [u'Copyright']),
        ]
        for test_file, expected in tests:
            location = os.path.join(test_dir, test_file)
            result = list(s for s, _ln in finder.find_pattern(location, pattern, unique=True))
            assert result == expected

    def test_search_in_binaries_with_line(self):
        test_file = self.get_test_loc('finder/binaries/gapi32.dll')
        pattern = r'This program ([\(\w\)\.\- ]+)'
        expected = [('cannot be run in DOS mode.', 1)]
        result = list(finder.find_pattern(test_file, pattern))
        assert result == expected
