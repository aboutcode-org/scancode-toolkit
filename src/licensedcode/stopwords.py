# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#


"""
A set of common words that are ignored from matching such as HTML tags.
"""

STOPWORDS = frozenset({
# common XML character references as &quot;
    'amp',
    'apos',
    'gt',
    'lt',
    'nbsp',
    'quot',

# common html tags as <a href=https://link ...> dfsdfsdf</a>
    'a',
    'alt',
    'blockquote',
    'body',
    'br',
    'class',
    'div',
    'em',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'hr',
    'href',
    'img',
    'li',
    'ol',
    'p',
    'pre',
    'rel',
    'script',
    'span',
    'src',
    'td',
    'th',
    'tr',
    'ul',


# comment line markers
    # batch files
    'rem',
    # autotools
    'dnl',

# doc book tags as <para>
    'para',
    'ulink',

# Some HTML punctuations and entities all as &emdash;

        'bdquo',
    'bull',
    'bullet',
    'colon',
    'comma',
    'emdash',  # rare and weird
    'emsp',
    'ensp',
    'ge',
    'hairsp',
    'ldquo',
    'ldquor',
    'le',
    'lpar',
    'lsaquo',
    'lsquo',
    'lsquor',
    'mdash',
    'ndash',
    'numsp',
    'period',
    'puncsp',
    'raquo',
    'rdquo',
    'rdquor',
    'rpar',
    'rsaquo',
    'rsquo',
    'rsquor',
    'sbquo',
    'semi',
    'thinsp',
    'tilde',
    # some xml char entities
    'x3c',
    'x3e',

    # seen in many CSS
    'lists',
    'side', 'nav',
    'height',
    'auto',
    'border',
    'padding',
    'width',

    # seen in Perl PODs
    'head1',
    'head2',
    'head3',

    # seen in RTF markup
    # this may be a solution to https://github.com/nexB/scancode-toolkit/issues/1548
    # 'par',

    # common in C literals
    'printf',

    # common in shell
    'echo',

})


# query breaks
# in Android generated NOTICE.html files
breaks = {
    '<pre class="license-text">',
    '</pre><!-- license-text -->',
    '-------------------------------------------------------------------',
    '==============================================================================',
}


# TODO: use me?
# translations of HTML entities to words or letters
{
    '&eacute': 'e',
    '&copy': '(c)',
}
