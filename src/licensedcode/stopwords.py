# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#
# Visit https://aboutcode.org and https://github.com/nexB/scancode-toolkit for
# support and download. ScanCode is a trademark of nexB Inc.
#
# The ScanCode software is licensed under the Apache License version 2.0.
# The ScanCode open data is licensed under CC-BY-4.0.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


"""
A set of common words that are ignored from matching such as HTML tags.
"""

STOPWORDS = frozenset({
# common XML character references as &quot;
    'quot',
    'apos',
    'lt',
    'gt',
    'amp',
    'nbsp',

# common html tags as <a href=https://link ...> dfsdfsdf</a>
    'a',
    'href',
    'p',
    'br',
    'div',
    'em',
    'span',
    'class',
    'pre',
    'ul',
    'ol',
    'li',
    'hr',
    'tr',
    'td',
    'th',
    'img',
    'alt',
    'src',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'blockquote',
    'body',
    #'id',
    'script',
    'rel',

# debian copyright files <s> tags
    's',

# comment line markers
    # batch files
    'rem',
    # autotools
    'dnl',

# doc book tags as <para>
    'ulink',
    'para',

# Some HTML punctuations and entities all as &emdash;
    'ge',
    'le',
    'emdash',  # rare and weird
    'mdash',
    'ndash',
    'bdquo',
    'ldquo',
    'ldquor',
    'lsaquo',
    'lsquo',
    'lsquor',
    'raquo',
    'rdquo',
    'rdquor',
    'rsaquo',
    'rsquo',
    'rsquor',
    'sbquo',
    'lpar',
    'rpar',
    'comma',
    'period',
    'colon',
    'semi',
    'tilde',
    'emsp',
    'ensp',
    'numsp',
    'puncsp',
    'thinsp',
    'hairsp',
    'bull',
    'bullet',
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
    'f',
    'head1',
    'head2',
    'head3',

    # seen in RTF markup
    # this may be a solution to https://github.com/nexB/scancode-toolkit/issues/1548
    # 'par',

    # TODO: consider common english stop words (the of a ...)
    # 'the',
    # 'of',
    # 'a',

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
