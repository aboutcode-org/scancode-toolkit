#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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

from collections import deque
import os
import re

# importand: this sets re._MAXCACHE
import commoncode
from textcode import analysis
from cluecode import copyrights_hint

# Tracing flags
TRACE = False or os.environ.get('SCANCODE_DEBUG_COPYRIGHT', False)
# set to 1 to enable nltk deep tracing
TRACE_DEEP = 0
if os.environ.get('SCANCODE_DEBUG_COPYRIGHT_DEEP'):
    TRACE_DEEP = 1


# Tracing flags
def logger_debug(*args):
    pass


if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, unicode) and a or repr(a) for a in args))

"""
Detect and collect copyright statements.

The process consists in:
 - prepare and cleanup text
 - identify regions of text that may contain copyright (using hints)
 - tag the text for parts-of-speech (POS) to identify various copyright
   statements parts such as dates, names ("named entities"), etc. This is done
   using NLTK POS tagging
 - feed the tagged text to a parsing grammar describing actual copyright
   statements
 - yield copyright statements, years, holder and authors with start and end line
   from the parse tree, eventually performing some minor cleanups.
"""


def detect_copyrights(location):
    """
    Yield tuples of:
    (copyrights list, authors list, years list, holders list, start line, end line)
    detected in file at location.
    """
    detector = CopyrightDetector()
    for numbered_lines in candidate_lines(analysis.text_lines(location, demarkup=True)):
        detected = detector.detect(numbered_lines)
        cp, auth, yr, hold, _start, _end = detected
        if any([cp, auth, yr, hold]):
            yield detected


def detect(location):
    """
    Return lists of detected copyrights, authors, years and holders
    in file at location.
    WARNING: Deprecated legacy entry point.
    """
    copyrights = []
    copyrights_extend = copyrights.extend
    authors = []
    authors_extend = authors.extend
    years = []
    years_extend = years.extend
    holders = []
    holders_extend = holders.extend

    for cp, auth, yr, hold, _start, _end in detect_copyrights(location):
        copyrights_extend(cp)
        authors_extend(auth)
        years_extend(yr)
        holders_extend(hold)
    return copyrights, authors, years, holders


_YEAR = (r'('
    '19[6-9][0-9]'  # 1960 to 1999
    '|'
    '20[0-1][0-9]'  # 2000 to 2019
')')

_YEAR_SHORT = (r'('
    '[6-9][0-9]'  # 19-60 to 19-99
    '|'
    '[0-1][0-9]'  # 20-00 to 20-19
')')

_YEAR_YEAR = (r'('
              # fixme   v ....the underscore below is suspicious
    '19[6-9][0-9][\.,\-]_[6-9][0-9]'  # 1960-99
    '|'
    '19[6-9][0-9][\.,\-]+[0-9]'  # 1998-9
    '|'
    '20[0-1][0-9][\.,\-]+[0-1][0-9]'  # 2001-16 or 2012-04
    '|'
    '200[0-9][\.,\-]+[0-9]'  # 2001-4 not 2012
')')

_PUNCT = (r'('
    '['
        '\W'  # not a word (word includes underscore)
        '\D'  # not a digit
        '\_'  # underscore
        'i'  # oddity
        '\?'
    ']'
    '|'
    '\&nbsp'  # html entity sometimes are double escaped
')*')  # repeated 0 or more times

_YEAR_PUNCT = _YEAR + _PUNCT
_YEAR_YEAR_PUNCT = _YEAR_YEAR + _PUNCT
_YEAR_SHORT_PUNCT = _YEAR_SHORT + _PUNCT

_YEAR_OR_YEAR_YEAR_WITH_PUNCT = (r'(' +
    _YEAR_PUNCT +
    '|' +
    _YEAR_YEAR_PUNCT +
')')

_YEAR_THEN_YEAR_SHORT = (r'(' +
    _YEAR_OR_YEAR_YEAR_WITH_PUNCT +
    '(' +
    _YEAR_SHORT_PUNCT +
    ')*' +
')')

pats = [
    _YEAR,
    _YEAR_SHORT,
    _YEAR_YEAR,
    _PUNCT,
    _YEAR_OR_YEAR_YEAR_WITH_PUNCT
    ]

# FIXME: multi-tokens patterns are likely not behaving as expected
# FIXME: patterns could be greatly simplified

patterns = [
    # TODO: this needs to be simplified:
    # TODO: in NLTK 3.0 this will fail because of this bug:
    # https://github.com/nltk/nltk/issues/1025

    # JUNK are things to ignore
    # All Rights Reserved. should be a terminator/delimiter.
    (r'^([Aa]ll [Rr]ights? [Rr]eserved|ALL RIGHTS? RESERVED|[Aa]ll|ALL)$', 'JUNK'),
    (r'^([Rr]eserved|RESERVED)[,]?$', 'JUNK'),

    # found in crypto certificates and LDAP
    (r'^(O=?|OU=?|XML)$', 'JUNK'),
    (r'^(Parser|Dual|Crypto|NO|PART|[Oo]riginall?y?|[Rr]epresentations?\.?)$', 'JUNK'),

    (r'^(Refer|Apt|Agreement|Usage|Please|Based|Upstream|Files?|Filename:?|'
     r'Description:?|[Pp]rocedures?|You|Everyone)$', 'JUNK'),
    (r'^(Rights?|Unless|rant|Subject|Acknowledgements?|Special)$', 'JUNK'),
    (r'^(LICEN[SC]E[EDS]?|Licen[sc]e[eds]?)$', 'TOIGNORE'),
    (r'^(Derivative|Work|[Ll]icensable|[Ss]ince|[Ll]icen[cs]e[\.d]?|'
     r'[Ll]icen[cs]ors?|under)$', 'JUNK'),
    (r'^(TCK|Use|[Rr]estrictions?|[Ii]ntrodu`ction)$', 'JUNK'),
    (r'^([Ii]ncludes?|[Vv]oluntary|[Cc]ontributions?|[Mm]odifications?)$', 'JUNK'),
    (r'^(Company:|For|File|Last|[Rr]eleased?|[Cc]opyrighting)$', 'JUNK'),
    (r'^Authori.*$', 'JUNK'),
    (r'^[Bb]uild$', 'JUNK'),
    (r'^[Ss]tring$', 'JUNK'),
    (r'^Implementation-Vendor$', 'JUNK'),
    (r'^(dnl|rem|REM)$', 'JUNK'),
    (r'^Implementation-Vendor$', 'JUNK'),
    (r'^Supports|Separator$', 'JUNK'),
    (r'^\.byte|Idata$', 'JUNK'),
    (r'^[Cc]ontributed?$', 'JUNK'),
    (r'^[Ff]unctions?$', 'JUNK'),
    (r'^[Nn]otices?|[Mm]ust$', 'JUNK'),
    (r'^ISUPPER?|ISLOWER$', 'JUNK'),
    (r'^AppPublisher$', 'JUNK'),
    (r'^DISCLAIMS?|SPECIFICALLY|WARRANT(Y|I)E?S?$', 'JUNK'),
    (r'^(hispagestyle|Generic|Change|Add|Generic|Average|Taken|LAWS\.?|design|Driver)$', 'JUNK'),
    (r'^[Cc]ontribution\.?', 'JUNK'),
    (r'(DeclareUnicodeCharacter|Language-Team|Last-Translator|OMAP730|Law\.)$', 'JUNK'),
    (r'^dylid|BeOS|Generates?|Thanks?', 'JUNK'),

    (r'^(([A-Z][a-z]+){3,}[A-Z]+[,]?)$', 'JUNK'),
    (r'^(([A-Z][a-z]+){3,}[A-Z]+[0-9]+[,]?)$', 'JUNK'),

    # RCS keywords
    (r'^(Header|Id|Locker|Log|RCSfile|Revision)$', 'NN'),

    # Various NN, exceptions to NNP or CAPS
    (r'^(Send|It|Mac|Support|Confidential|Information|Various|Mouse|Wheel'
      r'|Vendor|Commercial|Indemnified|Luxi|These|Several|GnuPG|WPA|Supplicant'
      r'|TagSoup|Contact|IA64|Foreign|Data|Atomic|Pentium|Note|Delay|Separa.*|Added'
      r'|Glib|Gnome|Gaim|Open|Possible|In|Read|Permissions?|New|MIT'
      r')$', 'NN'),

    # Various non CAPS
    (r'^(OR)$', 'NN'),

    # Various rare non CAPS but NNP, treated as full names
    (r'^(FSF[\.,]?)$', 'NAME'),

    # Windows XP
    (r'^(Windows|XP|SP1|SP2|SP3|SP4|assembly)$', 'JUNK'),

    (r'^example\.com$', 'JUNK'),

    # Java
    (r'^.*Servlet,?|class$', 'JUNK'),

    # C/C++
    (r'^(template|struct|typedef|type|next|typename|namespace|type_of|begin|end)$', 'JUNK'),

    # various trailing words that are junk
    (r'^(?:Copyleft|LegalCopyright|AssemblyCopyright|Distributed|Report|'
     r'Available|true|false|node|jshint|node\':true|node:true|this|Act,?|'
     r'[Ff]unctionality|bgcolor|F+|Rewrote|Much|remains?,?|Implementation|earlier'
     r'|al.|is|laws|url|[Ss]ee)$', 'JUNK'),

    # Some mixed case junk
    (r'^LastModified$', 'JUNK'),

    # Some font names
    (r'^Lucida$', 'JUNK'),

    # various trailing words that are junk
    (r'^(?:CVS|EN-IE|Info|GA|unzip)$', 'JUNK'),

    # this is not Copr.
    (r'Coproduct,?', 'JUNK'),

    # Places: TODO: these are NOT NNPs~
    (r'^\(?(?:Cambridge|Stockholm|Davis|Sweden[\)\.]?|Massachusetts|Oregon|California'
     r'|Norway|UK|Berlin|CONCORD|Manchester|MASSACHUSETTS|Finland|Espoo|Munich'
     r'|Germany|Italy|Spain|Europe)[\),\.]?$', 'NNP'),

    # Date/Day/Month text references
    (r'^(Date|am|pm|AM|PM)$', 'NN'),
    (r'^(January|February|March|April|May|June|July|August|September|October|November|December)$', 'NN'),

    # Jan and Jun are common enough first names
    (r'^(Feb|Mar|Apr|May|Jul|Aug|Sep|Oct|Nov|Dec)$', 'NN'),
    (r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)$', 'NN'),
    (r'^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)$', 'NN'),

    (r'^\$?LastChangedDate\$?$', 'YR'),

    # Misc corner cases that are NNP
    (r'^Software,\',|\(Royal|PARADIGM|nexB|okunishinishi|yiminghe|Antill\',$', 'NNP'),

    # rarer caps
    # EPFL-LRC/ICA
    (r'^[A-Z]{3,6}-[A-Z]{3,6}/[A-Z]{3,6}', 'NNP'),

    # exceptions to composed proper nouns, mostly debian copyright-related
    # FIXME: may be lowercase instead?
    (r'^(Title:?|Debianized-By:?|Upstream-Maintainer:?|Content-MD5)$', 'JUNK'),
    (r'^(Upstream-Author:?|Packaged-By:?)$', 'JUNK'),

    # NOT a copyright symbol (ie. "copyrighted."): treat as NN
    (r'^[Cc](opyright(s|ed)?|OPYRIGHT(S|ED))\.$', 'NN'),
    # copyright word or symbol
    # note the leading @ .... this may be a source of problems
    (r'.?(@?([Cc]opyright)s?:?|[Cc]opr\.?|[(][Cc][)]|(COPYRIGHT)S?:?)', 'COPY'),

    # copyright in markup, until we strip markup: apache'>Copyright or left'>Copyright
    (r'[A-Za-z0-9]+[\'">]+[Cc]opyright', 'COPY'),

    # AT&T (the company), needs special handling
    (r'^AT\&T[\.,]?$', 'COMP'),

    # company suffix:     Tech.,ltd
    (r'^([A-Z][a-z]+[\.,]+[Ll][Tt][Dd]).?$', 'COMP'),

    # company suffix
    (r'^([Ii]nc[.]?|[I]ncorporated|[Cc]ompany|Limited|LIMITED).?$', 'COMP'),
    # company suffix
    (r'^(INC(ORPORATED|[.])?|CORP(ORATION|[.])?|FOUNDATION|GROUP|COMPANY|'
     r'[(]tm[)]).?$|[Ff]orum.?', 'COMP'),
    # company suffix
    (r'^([cC]orp(oration|[\.,])?|[cC]orporations?[\.,]?|[fF]oundation|[Aa]lliance|Working|[Gg]roup|'
     r'[Tt]echnolog(y|ies)|[Cc]ommunit(y|ies)|[Mm]icrosystems.?|[Pp]roject|'
     r'[Tt]eams?|[Tt]ech).?$', 'COMP'),
    (r"^Limited'?,?$", 'COMP'),

    # company suffix : LLC, LTD, LLP followed by one extra char
    (r'^([Ll][Ll][CcPp]|[Ll][Tt][Dd])\.,$', 'COMP'),
    (r'^([Ll][Ll][CcPp]|[Ll][Tt][Dd])\.?,?$', 'COMP'),
    (r'^([Ll][Ll][CcPp]|[Ll][Tt][Dd])\.$', 'COMP'),
    (r'^L\.P\.$', 'COMP'),
    (r'^[Ss]ubsidiar(y|ies)$', 'COMP'),
    (r'^[Ss]ubsidiary\(\-ies\)$', 'COMP'),
    # company suffix : SA, SAS, AS, AG, AB, AS, CO, labs followed by a dot
    (r'^(S\.?A\.?S?\.?|Sas\.?|sas\.?|AS\.?|AG\.?|AB\.?|Labs?\.?|[Cc][Oo]\.?|Research|INRIA|Societe).?$', 'COMP'),
    # (german) company suffix
    (r'^[Gg][Mm][Bb][Hh].?$', 'COMP'),
    # (italian) company suffix
    (r'^[sS]\.[pP]\.[aA]\.?$', 'COMP'),
    # (Laboratory) company suffix
    (r'^(Labs?|Laboratory|Laboratories|Laboratoire)\.?,?$', 'COMP'),
    # (dutch and belgian) company suffix
    (r'^[Bb]\.?[Vv]\.?|BVBA$', 'COMP'),
    # university
    (r'^\(?[Uu]niv(?:[.]|ersit(?:y|e|at?|ad?))\)?\.?$', 'UNI'),
    # Academia/ie
    (r'^[Ac]cademi[ae]s?$', 'UNI'),
    # institutes
    (r'INSTITUTE', 'COMP'),
    (r'^[Ii]nstitut(s|o|os|e|es|et|a|at|as|u|i)?$', 'COMP'),
    # Facility
    (r'Tecnologia', 'COMP'),
    (r'Facility', 'COMP'),

    # "holders" is considered Special
    (r'^HOLDER\(S\)$', 'JUNK'),
    (r'^([Hh]olders?|HOLDERS?)$', 'HOLDER'),

    # not NNPs
    (r'^([Rr]espective|JavaScript)$', 'NN'),

    # affiliates or "and its affiliate(s)."
    (r'^[Aa]ffiliate(s|\(s\))?\.?$', 'NNP'),

    # OU as in Org unit, found in some certficates
    (r'^OU$', 'OU'),

    (r'^(CONTRIBUTORS?|OTHERS?|Contributors?\:)[,\.]?$', 'JUNK'),
    # "authors" or "contributors" is interesting, and so a tag of its own
    (r'^[Aa]uthor\.?$', 'AUTH'),
    (r'^[Aa]uthors\.?$', 'AUTHS'),
    (r'^[Aa]uthor\(s\)\.?$', 'AUTHS'),
    (r'^[Cc]ontribut(ors?|ing)\.?$', 'CONTRIBUTORS'),

    # commiters is interesting, and so a tag of its own
    (r'[Cc]ommitters\.??', 'COMMIT'),
    # same for maintainers, developers, admins.
    (r'^([Aa]dmins?|[Mm]aintainers?\.?|co-maintainers?|[Dd]evelopers?\.?)$', 'MAINT'),

    # same for developed, etc...
    (r'^(([Rr]e)?[Cc]oded|[Mm]odified|[Mm]ai?nt[ea]ine(d|r)|[Ww]ritten|[Dd]eveloped)$', 'AUTH2'),
    # author
    (r'@author', 'AUTH'),
    # Offer
    (r'^Offer$', 'NNP'),

    # of
    (r'^[Oo][Ff]|[Dd][Eei]$', 'OF'),
    # in
    (r'^(in|en)$', 'IN'),
    # by
    (r'^by|BY|By$', 'BY'),
    # following
    (r'^following$', 'FOLLOW'),

    # conjunction: and
    (r'^([Aa]nd|&|[Uu]nd|ET|[Ee]t|at|and/or)$', 'CC'),

    # conjunction: or. Even though or is not conjunctive ....
    # (r'^or$', 'CC'),
    # conjunction: or. Even though or is not conjunctive ....
    # (r'^,$', 'CC'),
    # ie. in things like "Copyright (c) 2012 John Li and others"
    (r'^[Oo]ther?s[\.,]?$', 'OTH'),
    # in year ranges: dash, or 'to': "1990-1995", "1990/1995" or "1990 to 1995"
    (r'^([-/]|to)$', 'DASH'),

    # explicitly ignoring these words: FIXME: WHY?
    (r'^([Tt]his|THIS|[Pp]ermissions?|PERMISSIONS?|All)$', 'NN'),

    # Portions copyright .... are worth keeping
    (r'[Pp]ortions?', 'PORTIONS'),

    # in dutch/german names, like Marco van Basten, or Klemens von Metternich
    # and Spanish/French Da Siva and De Gaulle
    (r'^(([Vv][ao]n)|[Dd][aeu])$', 'VAN'),

    # rare cases of trailing + signon years
    (r'^20[0-1][0-9]\+$', 'YR-PLUS'),

    # year or year ranges
    # plain year with various leading and trailing punct
    # dual or multi years 1994/1995. or 1994-1995
    # 1987,88,89,90,91,92,93,94,95,96,98,99,2000,2001,2002,2003,2004,2006
    # multi years
    # dual years with second part abbreviated
    # 1994/95. or 2002-04 or 1991-9
    (r'^' + _PUNCT + _YEAR_OR_YEAR_YEAR_WITH_PUNCT + '+' +
        '(' +
            _YEAR_OR_YEAR_YEAR_WITH_PUNCT +
        '|' +
            _YEAR_THEN_YEAR_SHORT +
        ')*' + '$', 'YR'),

    (r'^' + _PUNCT + _YEAR_OR_YEAR_YEAR_WITH_PUNCT + '+' +
        '(' +
            _YEAR_OR_YEAR_YEAR_WITH_PUNCT +
        '|' +
            _YEAR_THEN_YEAR_SHORT +
        '|' +
            _YEAR_SHORT_PUNCT +
        ')*' + '$', 'YR'),

    # 88, 93, 94, 95, 96: this is a pattern mostly used in FSF copyrights
    (r'^[8-9][0-9],$', 'YR'),

    # cardinal numbers
    (r'^-?[0-9]+(.[0-9]+)?.?$', 'CD'),

    # exceptions to proper nouns
    (r'^(The|Commons|[Ii]ntltool|[Tt]ext|software|Permissions?|Natural'
     r'|Docs?|Jsunittest|Asset|Packaging|Tool|Android|Win32|Do|Xalan'
     r'|Programming|Objects|Material|Improvement|Example|COPYING'
     r'|Experimental|Additional)$', 'NN'),

    # composed proper nouns, ie. Jean-Claude or ST-Microelectronics
    # FIXME: what about a variant with spaces around the dash?
    (r'^[A-Z][a-zA-Z]*\s?[\-]\s?[A-Z]?[a-zA-Z]+.?$', 'NNP'),

    # Countries abbreviations
    (r'^U\.S\.A\.?$', 'NNP'),

    # Dotted ALL CAPS initials
    # (r'^[A-Z]\.[A-Z]\.$', 'NNP'),

    # Dotted ALL CAPS initials
    (r'^([A-Z]\.){1,3}$', 'NNP'),

    # LaTeX3 Project
    (r'^LaTeX3$', 'NNP'),

    (r'^Meridian\'93|Xiph.Org|iClick,?$', 'NNP'),

    # This_file_is_part_of_KDE
    (r'^[Tt]his_file_is_part_of_KDE$', 'NNP'),

    # Corner cases of lowercased NNPs
    (r'^(suzuki|toshiya\.?|leethomason|finney|sean|chris|ulrich'
     r'|wadim|dziedzic)$', 'NNP'),

    # proper nouns with digits
    (r'^([A-Z][a-z0-9]+){1,2}.?$', 'NNP'),
    # saxon genitive, ie. Philippe's
    (r"^[A-Z][a-z]+[']s$", 'NNP'),
    # Uppercase dotted name, ie. P.
    (r"^([A-Z][.]?|[A-Z]+[\.])$", 'PN'),
    # proper noun with some separator and trailing comma
    (r"^[A-Z]+[.][A-Z][a-z]+[,]?$", 'NNP'),

    # proper noun with apostrophe ': D'Orleans, D'Arcy, T'so, Ts'o
    (r"^[A-Z][[a-z]?['][A-Z]?[a-z]+[,.]?$", 'NNP'),

    # proper noun with apostrophe ': d'Itri
    (r"^[a-z]['][A-Z]?[a-z]+[,\.]?$", 'NNP'),

    # all CAPS word, at least 1 char long such as MIT, including an optional trailing comma or dot
    (r'^[A-Z0-9]+[,]?$', 'CAPS'),
    # (r'^[A-Z0-9]+[,\.]?$', 'CAPS'),
    # all caps word 3 chars and more, enclosed in parens
    (r'^\([A-Z0-9]{2,}\)$', 'CAPS'),

    # proper noun:first CAP, including optional trailing comma
    (r'^(([A-Z][a-zA-Z0-9]+){,2}[,]?)$', 'NNP'),

    # all CAPS word, all letters including an optional trailing single quote
    (r"^[A-Z]{2,}\'?$", 'CAPS'),

    # email eventually in parens or brackets with some trailing punct.
    (r'^[\<\(]?[a-zA-Z0-9]+[a-zA-Z0-9\+_\-\.\%]*(@|at)[a-zA-Z0-9][a-zA-Z0-9\+_\-\.\%]+\.[a-zA-Z]{2,5}?[\>\)\.\,]*$', 'EMAIL'),

    # URLS such as <(http://fedorahosted.org/lohit)>
    (r'[<\(]https?:.*[>\)]', 'URL'),
    # URLS such as ibm.com
    (r'\s?[a-z0-9A-Z\-\.\_]+\.(com|net|info|org|us|mil|io|edu|co\.[a-z][a-z]|eu|biz)\s?\.?$', 'URL2'),
    # TODO: add more extensions?
    # URL wrapped in ()
    (r'[\(<]+\s?[a-z0-9A-Z\-\.\_]+\.(com|net|info|org|us|mil|io|edu|co\.[a-z][a-z]|eu|biz)\s?[\.\)>]+$', 'URL'),
    (r'<?a?.(href)?.\(?[a-z0-9A-Z\-\.\_]+\.(com|net|info|org|us|mil|io|edu|co\.[a-z][a-z]|eu|biz)[\.\)>]?$', 'URL'),
    # derived from regex in cluecode.finder
    (r'<?a?.(href)?.('
     r'(?:http|ftp|sftp)s?://[^\s<>\[\]"]+'
     r'|(?:www|ftp)\.[^\s<>\[\]"]+'
     r')\.?>?', 'URL'),

    (r'^\(?<?https?://[a-zA-Z0-9_\-]+(\.([a-zA-Z0-9_\-])+)+.?\)?>?$', 'URL'),

    # URLS with trailing/ such as http://fedorahosted.org/lohit/
    # URLS with leading( such as (http://qbnz.com/highlighter/
    (r'\(?https?:.*/', 'URL'),

    # K.K. (a company suffix), needs special handling
    (r'^K.K.,?$', 'NAME'),

    # comma as a conjunction
    (r'^,$', 'CC'),

    # .\" is not a noun
    (r'^\.\\\?"?$', 'JUNK'),

    # Mixed cap nouns (rare) LeGrande
    (r'^[A-Z][a-z]+[A-Z][a-z]+[\.\,]?$', 'MIXEDCAP'),

    # weird year
    (r'today.year', 'YR'),

    # communications
    (r'communications', 'NNP'),

    # Code variable names including snake case
    (r'^.*(_.*)+$', 'JUNK'),

    # nouns (default)
    (r'.+', 'NN'),
]

# Comments in the Grammar are lines that start with #
grammar = """
    YR-RANGE: {<YR>+ <CC>+ <YR>}        #20
    YR-RANGE: {<YR> <DASH>* <YR|CD>+}        #30
    YR-RANGE: {<CD>? <YR>+}        #40
    YR-RANGE: {<YR>+ }        #50
    YR-AND: {<CC>? <YR>+ <CC>+ <YR>}        #60
    YR-RANGE: {<YR-AND>+}        #70

    NAME: {<NAME><NNP>} #75

    NAME: {<NN|NNP> <CC> <URL|URL2>} #80

    # the Tor Project, Inc.
    COMP: {<COMP> <COMP>+} #81

    # Laboratory for Computer Science Research Computing Facility
    COMPANY: {<COMP> <NN> <NNP> <NNP> <COMP> <NNP> <COMP>} #83
    COMPANY: {<COMP> <NN> <NNP> <NNP> <COMP>} #82

    # E. I. du Pont de Nemours and Company
    COMPANY: {<NNP>  <NNP>  <VAN>  <NNP>  <OF>  <NNP>  <CC>  <COMP>}             #1010

    #  Robert A. van Engelen OR NetGroup, Politecnico di Torino (Italy)
    NAME: {<NNP>+ <VAN|OF>  <NNP>+} #88

    NAME: {<NNP> <VAN|OF> <NN*> <NNP>}        #90

    NAME: {<NNP> <PN> <VAN> <NNP>}        #100

    # by the netfilter coreteam <coreteam@netfilter.org>
    NAME: {<BY> <NN>+ <EMAIL>}        #110

    # Kaleb S. KEITHLEY
    NAME: {<NNP> <PN> <CAPS>}        #120

    # Trolltech AS, Norway.
    NAME: {<NNP> <CAPS> <NNP>}        #121

    # BY GEORGE J. CARRETTE
    NAME: {<BY> <CAPS> <PN> <CAPS>} #85

    DASHCAPS: {<DASH> <CAPS>}
   # INRIA - CIRAD - INRA
    COMPANY: { <COMP> <DASHCAPS>+}        #1280

    # Project Admins leethomason
    COMPANY: { <COMP> <MAINT> <NNP>+}        #1281

    # the Regents of the University of California
    COMPANY: {<BY>? <NN> <NNP> <OF> <NN> <UNI> <OF> <COMPANY|NAME|NAME2|NAME3><COMP>?}        #130

   # Free Software Foundation, Inc.
    COMPANY: {<NNP> <NNP> <COMP> <COMP>}       #135

   #  Mediatrix Telecom, inc. <ericb@mediatrix.com>
    COMPANY: {<NNP>+ <COMP> <EMAIL>}       #136

   # Corporation/COMP for/NN  National/NNP Research/COMP Initiatives/NNP
    COMPANY: {<COMP> <NN> <NNP> <COMP> <NNP>}       #140

    # Sun Microsystems, Inc. Mountain View
    COMPANY: {<COMP> <COMP> <NNP><NNP>}       #144
    # AT&T Laboratories, Cambridge
    COMPANY: {<COMP> <COMP> <NNP>}       #145

    # rare "Software in the public interest, Inc."
    COMPANY: {<COMP> <CD> <COMP>}        #170
    COMPANY: {<NNP> <IN><NN> <NNP> <NNP>+<COMP>?}        #180

    # Commonwealth Scientific and Industrial Research Organisation (CSIRO)
    COMPANY: {<NNP> <NNP>  <CC>  <NNP>  <COMP>  <NNP> <CAPS>}

    COMPANY: {<NNP> <CC> <NNP> <COMP> <NNP>?}        #200

    # Android Open Source Project, 3Dfx Interactive, Inc.
    COMPANY: {<NN>?  <NN>  <NNP>  <COMP>}        #205

    NAME: {<NNP>  <NNP>  <COMP>  <CONTRIBUTORS>  <URL|URL2>} #206

    # Thai Open Source Software Center Ltd
    COMPANY: {<NNP>  <NN>  <NNP>  <NNP>  <NNP>  <COMP>} #207

    COMPANY: {<NNP|CAPS> <NNP|CAPS>? <NNP|CAPS>? <NNP|CAPS>? <NNP|CAPS>? <NNP|CAPS>? <COMP> <COMP>?}        #210
    COMPANY: {<UNI|NNP> <VAN|OF> <NNP>+ <UNI>?}        #220
    COMPANY: {<NNP>+ <UNI>}        #230
    COMPANY: {<UNI> <OF> <NN|NNP>}        #240
    COMPANY: {<COMPANY> <CC> <COMPANY>}        #250

    # University of Southern California, Information Sciences Institute (ISI)
    COMPANY: {<COMPANY>  <COMPANY>  <CAPS>} #251

    # GNOME i18n Project for Vietnamese
    COMPANY: {<CAPS>  <NN>  <COMP>  <NN>  <NNP>} #253

    COMPANY: {<CAPS>  <NN>  <COMP>}        #255

    # Project contributors
    COMPANY: {<COMP>  <CONTRIBUTORS>}   #256

    COMPANY: {<COMP>+}        #260

    # Nokia Corporation and/or its subsidiary(-ies)
    COMPANY: {<COMPANY>  <CC>  <NN>  <COMPANY>}   #265

    COMPANY: {<COMPANY> <CC> <NNP>+}        #270
    # AIRVENT SAM s.p.a - RIMINI(ITALY)
    COMPANY: {<COMPANY> <DASH> <NNP|NN> <EMAIL>?}        #290

    # Typical names
    #John Robert LoVerso
    NAME: {<NNP> <NNP> <MIXEDCAP>}        #340

    # Kaleb S. KEITHLEY
    NAME: {<NNP>  <NNP>  <CAPS>} #345

    # Academy of Motion Picture Arts and Sciences
    NAME: {<NNP|PN>+ <CC>? <NNP>+}        #350
    NAME: {<NNP> <PN>? <NNP>+}        #360
    NAME: {<NNP> <NNP>}        #370

    NAME: {<NNP> <NN|NNP> <EMAIL>}        #390
    NAME: {<NNP> <PN|VAN>? <PN|VAN>? <NNP>}        #400
    NAME: {<NNP> <NN> <NNP>}        #410
    NAME: {<NNP> <COMMIT>}        #420
    # the LGPL VGABios developers Team
    NAME: {<NN>? <NNP> <MAINT> <COMP>}        #440
    # Debian Qt/KDE Maintainers
    NAME: {<NNP> <NN>? <MAINT>}        #460
    NAME: {<NN> <NNP> <ANDCO>}        #470
    NAME: {<NN>? <NNP> <CC> <NAME>}        #480
    NAME: {<NN>? <NNP> <OF> <NN>? <NNP> <NNP>?}        #490
    NAME: {<NAME> <CC> <NAME>}        #500
    COMPANY: {<NNP> <IN> <NN>? <COMPANY>}        #510

    # and Josh MacDonald.
    NAME: {<CC> <NNP> <MIXEDCAP>}        #480

    NAME: {<NAME>  <UNI>}        #483

    # Kungliga Tekniska Hogskolan (Royal Institute of Technology, Stockholm, Sweden)
    COMPANY: { <COMPANY>  <OF>  <COMPANY>  <NAME> } #529

    # Instituto Nokia de Tecnologia
    COMPANY: { <COMPANY>  <NNP>  <OF>  <COMPANY>} #    5391

    # Laboratoire MASI - Institut Blaise Pascal
    COMPANY: { <COMPANY>  <CAPS>  <DASH>  <COMPANY>  <NAME>} #5292

    # Nara Institute of Science and Technology.
    COMPANY: { <COMPANY>  <OF>  <NNP>  <CC>  <COMPANY> } #5293

    NAME2: {<NAME> <EMAIL>}        #530

    NAME3: {<YR-RANGE> <NAME2|COMPANY>+}        #535
    NAME3: {<YR-RANGE> <NAME2|COMPANY>+ <CC> <YR-RANGE>}        #540
    NAME: {<NAME|NAME2>+ <OF> <NNP> <OF> <NN>? <COMPANY>}        #550
    NAME: {<NAME|NAME2>+ <CC|OF>? <NAME|NAME2|COMPANY>}        #560

    NAME3: {<YR-RANGE>  <NNP>+ <CAPS>?} #5610

    #Academy of Motion Picture Arts and Sciences
    NAME: { <NAME>  <CC>  <NNP>} # 561

    # Adam Weinberger and the GNOME Foundation
    NAME: {<CC>  <NN>  <COMPANY>} # 565

    NAME3: {<YR-RANGE> <NAME>+ <CONTRIBUTORS>?}        #570
    NAME: {<NNP> <OF> <NNP>}        #580
    NAME: {<NAME> <NNP>}        #590
    NAME: {<NN|NNP|CAPS>+ <CC> <OTH>}        #600
    NAME: {<NNP> <CAPS>}        #610
    NAME: {<CAPS> <DASH>? <NNP|NAME>}        #620
    NAME: {<NNP> <CD> <NNP>}        #630
    NAME: {<COMP> <NAME>+}        #640

    # and other contributors
    NAME: {<CC> <NN>? <CONTRIBUTORS>}        #644

    NAME: {<NNP|CAPS>+ <AUTHS|CONTRIBUTORS>}        #660

    NAME: {<VAN|OF> <NAME>}        #680
    NAME: {<NAME3> <COMP|COMPANY>}        #690
    # more names
    NAME: {<NNP> <NAME>}        #710
    NAME: {<CC>? <IN> <NAME|NNP>}        #720
    NAME: {<NAME><UNI>}        #730
    NAME: { <NAME> <IN> <NNP> <CC|IN>+ <NNP>}        #740
    # by BitRouter <www.BitRouter.com>
    NAME: { <BY>  <NNP>  <URL>}        #741

    # Philippe http//nexb.com joe@nexb.com
    NAME: { <NNP>  <URL>  <EMAIL>}        #742

    # Companies
    COMPANY: {<NAME|NAME2|NAME3|NNP>+ <OF> <NN>? <COMPANY|COMP> <NNP>?}        #770
    COMPANY: {<NNP> <COMP|COMPANY> <COMP|COMPANY>}        #780
    COMPANY: {<NN>? <COMPANY|NAME|NAME2> <CC> <COMPANY|NAME|NAME2>}        #790
    COMPANY: {<COMP|COMPANY|NNP> <NN> <COMPANY|COMPANY> <NNP>+}        #800

    # by the Institute of Electrical and Electronics Engineers, Inc.
    COMPANY: {<BY>  <NN>  <COMPANY>  <OF>  <NNP>  <CC>  <COMPANY>}
    COMPANY: {<COMPANY> <CC> <AUTH|CONTRIBUTORS|AUTHS>}        #810
    COMPANY: {<NN> <COMP|COMPANY>+}        #820
    COMPANY: {<URL|URL2>}        #830
    COMPANY: {<COMPANY> <COMP|COMPANY>}        #840


    # The Regents of the University of California
    NAME: {<NN> <NNP> <OF> <NN> <COMPANY>}        #870

    # Trailing Authors
    COMPANY: {<NAME|NAME2|NNP>+ <CONTRIBUTORS>}        #900

    # Jeffrey C. Foo
    COMPANY: {<PN> <COMP|COMPANY>}        #910

    # "And" some name
    ANDCO: {<CC> <NNP> <NNP>+}        #930
    ANDCO: {<CC> <OTH>}        #940
    ANDCO: {<CC> <NN> <NAME>+}        #950
    ANDCO: {<CC> <COMPANY|NAME|NAME2|NAME3>+}          #960
    COMPANY: {<COMPANY|NAME|NAME2|NAME3> <ANDCO>+}     #970
    NAME: {<NNP> <ANDCO>+}                             #980

    NAME: {<BY> <NN> <AUTH|CONTRIBUTORS|AUTHS>}        #1000

# NetGroup, Politecnico di Torino (Italy)
    COMPANY: {<NNP> <COMPANY> <NN|NNP>}        #1030

# Arizona Board of Regents (University of Arizona)
    NAME: {<COMPANY> <OF> <NN|NNP>}        #1060

# The Regents of the University of California
    NAME: {<NAME> <COMPANY>}        #1090

    # John Doe and Myriam Doe
    NAME: {<NAME|NNP> <CC> <NNP|NAME>}        #1120


    # International Business Machines Corporation and others
    COMPANY: {<COMPANY> <CC> <OTH>}        #1150
    COMPANY: {<NAME3> <CC> <OTH>}        #1160

    # Nara Institute of Science and Technology.
    COMPANY: {<NNP> <COMPANY> <CC> <COMP>}        #1190

    # Commonwealth Scientific and Industrial Research Organisation (CSIRO)
    COMPANY: {<NNP> <COMPANY> <NAME>}        #1220

    #The Android Open Source Project
    COMPANY: {<NN><NN><NN> <COMPANY>}        #1250

    # Bio++ Development Team
    COMPANY: {<NN> <NNP> <COMPANY>}        #1251

    # Institut en recherche ....
    COMPANY: {<NNP> <IN> <NN>+ <COMPANY>}        #1310

    #  OU OISTE Foundation
    COMPANY: {<OU> <COMPANY>}        #1340

    # NETLABS, Temple University
    COMPANY: {<CAPS> <COMPANY>}        #1370

    # XZY emails
    COMPANY: {<COMPANY> <EMAIL>+}        #1400

    # by the a href http wtforms.simplecodes.com WTForms Team
    COMPANY: {<BY> <NN>+ <COMP|COMPANY>}        #1420

    # the Regents of the University of California, Sun Microsystems, Inc., Scriptics Corporation
    COMPANY: {<NN> <NNP> <OF> <NN> <UNI> <OF> <COMPANY>+}

    # "And" some name
    ANDCO: {<CC>+ <NN> <NNP>+<UNI|COMP>?}        #1430
    ANDCO: {<CC>+ <NNP> <NNP>+<UNI|COMP>?}        #1440
    ANDCO: {<CC>+ <COMPANY|NAME|NAME2|NAME3>+<UNI|COMP>?}        #1450
    COMPANY: {<COMPANY|NAME|NAME2|NAME3> <ANDCO>+}        #1460

    COMPANY: {<COMPANY><COMPANY>+}        #1480

    # Copyright (c) 2002 World Wide Web Consortium, (Massachusetts Institute of Technology, Institut National de Recherche en Informatique et en Automatique, Keio University).
    COMPANY: {<CC> <IN> <COMPANY>}       #1490

    # Oracle and/or its affiliates.
    NAME: {<NNP> <ANDCO>}        #1410

    # the University of California, Berkeley and its contributors.
    COMPANY: {<COMPANY> <CC> <NN> <CONTRIBUTORS>} #1411

    # UC Berkeley and its contributors
    NAME: {<NAME> <CC> <NN> <CONTRIBUTORS>} #1412

    #copyrighted by Douglas C. Schmidt and his research group at Washington University, University of California, Irvine, and Vanderbilt University, Copyright (c) 1993-2008,
    COMPANY: {<NAME> <CC> <NN> <COMPANY>+} #1413

    # The University of Utah and the Regents of the University of California
    COMPANY: {<NN>  <COMPANY>  <CC>  <NN>  <COMPANY>}      #1414

    # by the Massachusetts Institute of Technology
    COMPANY: { <BY>  <COMPANY>  <OF>  <COMPANY>}  #1415

    # Computer Systems and Communication Lab, Institute of Information Science, Academia Sinica.
    COMPANY: { <NNP>  <COMPANY>  <OF>  <COMPANY>  <NNP>} #1416

    # Copyright 2007-2010 the original author or authors.
    # Copyright (c) 2007-2010 the original author or authors.
    NAME: {<NN> <JUNK> <AUTH|CONTRIBUTORS|AUTHS> <NN> <AUTH|CONTRIBUTORS|AUTHS>}        #1960


#######################################
# Various forms of copyright statements
#######################################

    COPYRIGHT: {<COPY> <NAME> <COPY> <YR-RANGE>}        #1510

    COPYRIGHT: {<COPY> <COPY>? <BY>? <COMPANY|NAME*|YR-RANGE>* <BY>? <EMAIL>+}        #1530

    COPYRIGHT: {<COPY> <COPY>? <NAME|NAME2|NAME3> <CAPS> <YR-RANGE>}        #1550

    #Copyright . 2008 Mycom Pany, inc.
    COPYRIGHT: {<COPY> <NN> <NAME3>}        #1560

    COPYRIGHT: {<COPY> <COPY>? <NAME|NAME2|NAME3>+ <YR-RANGE>*}        #1570

    COPYRIGHT: {<COPY> <COPY>? <CAPS|NNP>+ <CC> <NN> <COPY> <YR-RANGE>?}        #1590

    COPYRIGHT: {<COPY> <COPY>? <BY>? <COMPANY|NAME*|NAME2*>+ <YR-RANGE>*}        #1610

    COPYRIGHT: {<NNP>? <COPY> <COPY>? (<YR-RANGE>+ <BY>? <NN>? <COMPANY|NAME|NAME2>+ <EMAIL>?)+}        #1630

    COPYRIGHT: {<COPY> <COPY>? <NN> <NAME> <YR-RANGE>}        #1650

    COPYRIGHT: {<COPY>+ <BY> <NAME|NAME2|NAME3>+}        #1670

    COPYRIGHT: {<COPY> <COPY> <COMP>+}        #1690

    COPYRIGHT: {<COPY> <COPY> <NN>+ <COMPANY|NAME|NAME2>+}        #1710

    COPYRIGHT: {<COPY> <COPY>? <NN> <NN>? <COMP> <YR-RANGE>?}        #1730

    COPYRIGHT: {<COPY> <COPY>? <NN> <NN>? <COMP> <YR-RANGE>?}        #1750
    COPYRIGHT: {<COPY> <NN> <NN>? <COMPANY> <YR-RANGE>?}        #1760

    COPYRIGHT: {<COPY> <COPY>? <YR-RANGE|NNP> <CAPS|BY>? <NNP|YR-RANGE|NAME>+}        #1780

    COPYRIGHT: {<COPY> <COPY> <NNP>+}        #1800

    # Copyright (c) 2003+ Evgeniy Polyakov <johnpol@2ka.mxt.ru>
    COPYRIGHT: {<COPY> <COPY> <YR-PLUS> <NAME|NAME2|NAME3>+}        #1801

    # Copyright (c) 2016 Project Admins foobar
    COPYRIGHT2: {<COPY> <COPY> <YR-RANGE>+ <COMP> <NNP> <NN>}        #1830

    # Copyright (c) 1995, 1996 The President and Fellows of Harvard University
    COPYRIGHT2: {<COPY> <COPY> <YR-RANGE> <NN> <NNP> <ANDCO>}        #1860

    COPYRIGHT2: {<COPY> <COPY> <YR-RANGE> <NN> <AUTH|CONTRIBUTORS|AUTHS>}        #1880

    # Copyright 1999, 2000 - D.T.Shield.
    # Copyright (c) 1999, 2000 - D.T.Shield.
    COPYRIGHT2: {<COPY> <COPY>? <YR-RANGE> <DASH> <NN>}        #1920

    #(c) 2017 The Chromium Authors
    COPYRIGHT2: {<COPY> <COPY>? <YR-RANGE> <NN> <NNP> <NN>}        #1990

    # Copyright (C) Research In Motion Limited 2010. All rights reserved.
    COPYRIGHT2: {<COPYRIGHT> <COMPANY> <YR-RANGE>}        #2020

    #  Copyright (c) 1999 Computer Systems and Communication Lab,
    #                    Institute of Information Science, Academia Sinica.
    COPYRIGHT2: {<COPYRIGHT> <COMPANY> <COMPANY>}        #2060

    COPYRIGHT2: {<COPY> <COPY> <YR-RANGE> <BY> <NN> <NN> <NAME>}        #2080
    COPYRIGHT2: {<COPY> <YR-RANGE> <BY> <NN> <NN> <NAME>}        #2090

    COPYRIGHT2: {<COPY> <COPY><NN>? <COPY> <YR-RANGE> <BY> <NN>}        #2110

    # Copyright (c) 1992-2002 by P.J. Plauger.
    COPYRIGHT2: {<COPY> <NN>? <COPY> <YR-RANGE> <BY> <NN> <NNP>?}        #2115

    COPYRIGHT2: {<COPY> <COPY>? <NN> <YR-RANGE> <BY> <NAME>}        #2140

    COPYRIGHT2: {<COPY> <COPY>? <YR-RANGE> <DASH> <BY>? <NAME2|NAME>}        #2160

    COPYRIGHT2: {<COPY> <COPY>? <YR-RANGE> <NNP> <NAME>}        #2180

    # Copyright (c) 2012-2016, Project contributors
    COPYRIGHT2: {<COPY> <COPY>? <YR-RANGE> <COMP> <AUTHS|CONTRIBUTORS>}        #2210

    COPYRIGHT2: {<COPY>+ <YR-RANGE> <COMP>}        #2230
    COPYRIGHT2: {<COPY> <COPY> <YR-RANGE>+ <CAPS>? <MIXEDCAP>}        #2240

    COPYRIGHT2: {<NAME> <COPY> <YR-RANGE>}        #2260

    # Copyright 2008 TJ <linux@tjworld.net>
    COPYRIGHT2: {<COPY>  <YR-RANGE>  <CAPS>  <EMAIL>} #2270

    # (c) Copyright 1985-1999 SOME TECHNOLOGY SYSTEMS
    COPYRIGHT2: {<COPY>  <COPY>  <YR-RANGE>  <CAPS>  <CAPS>  <CAPS>? <CAPS>?} #2271

    # Daisy (c) 1998
    NAME4: {<NNP>  <COPY>} #2272
    COPYRIGHT2: {<NAME4> <YR-RANGE>}  #2273

    # Scilab (c)INRIA-ENPC.
    COPYRIGHT: {<NAME4>  <NNP>} #2274

    COPYRIGHT2: {<COPY> <COPY>? <NN|CAPS>? <YR-RANGE>+ <PN>*}        #2280

    COPYRIGHT2: {<COPY> <COPY>? <NN|CAPS>? <YR-RANGE>+ <NN|CAPS>* <COMPANY>?}        #2300

    COPYRIGHT2: {<COPY> <COPY>? <NN|CAPS>? <YR-RANGE>+ <NN|CAPS>* <DASH> <COMPANY>}        #2320

    COPYRIGHT2: {<NNP|NAME|COMPANY> <COPYRIGHT2>}        #2340

    COPYRIGHT: {<COPYRIGHT> <NN> <COMPANY>}        #2360

    COPYRIGHT: {<COPY> <COPY>? <BY>? <NN> <COMPANY>}        #2380

    COPYRIGHT: {<COMPANY> <NN> <NAME> <COPYRIGHT2>}        #2400
    COPYRIGHT: {<COPYRIGHT2> <COMP> <COMPANY>}        #2410
    COPYRIGHT: {<COMPANY> <NN> <COPYRIGHT2>}        #2420
    COPYRIGHT: {<COPYRIGHT2> <NNP> <CC> <COMPANY>}        #2430

    COPYRIGHT: {<COPYRIGHT2> <NAME|NAME2|NAME3>+}        #2860

    # Copyright (c) 1996 Adrian Rodriguez (adrian@franklins-tower.rutgers.edu) Laboratory for Computer Science Research Computing Facility
    COPYRIGHT: {<COPYRIGHT>  <NAME>} #2400


# copyrights in the style of Scilab/INRIA
    COPYRIGHT: {<NNP> <NN> <COPY> <NNP>}        #2460
    COPYRIGHT: {<NNP> <COPY> <NNP>}        #2470

    # Copyright or Copr. 2006 INRIA - CIRAD - INRA
    COPYRIGHT: {<COPY> <NN> <COPY> <YR-RANGE>+ <COMPANY>+}        #2500

    COPYRIGHT: {<COPYRIGHT|COPYRIGHT2> <COMPANY>+ <NAME>*}        #2580

    # iClick, Inc., software copyright (c) 1999
    COPYRIGHT: {<ANDCO> <NN>? <COPYRIGHT|COPYRIGHT2>}        #2590

    # portions copyright
    COPYRIGHT: {<PORTIONS> <COPYRIGHT|COPYRIGHT2>}        #2610

    #copyright notice (3dfx Interactive, Inc. 1999), (notice is JUNK)
    COPYRIGHT: {<COPY> <JUNK> <COMPANY> <YR-RANGE>}       #2620

    # Copyright (C) <2013>, GENIVI Alliance, Inc.
    COPYRIGHT: {<COPYRIGHT2> <ANDCO>}       #2625

    #  copyright C 1988 by the Institute of Electrical and Electronics Engineers, Inc.
    COPYRIGHT: {<COPY> <PN> <YR-RANGE> <BY> <COMPANY> }       #2630

    # Copyright 1996-2004, John LoVerso.
    COPYRIGHT: {<COPYRIGHT> <MIXEDCAP> }       #2632

    # Copyright (C) 1992, 1993, 1994, 1995 Remy Card (card@masi.ibp.fr) Laboratoire MASI - Institut Blaise Pascal
    COPYRIGHT: {<COPYRIGHT> <DASH> <NAME>}       #2634

    # Copyright 2002, 2003 University of Southern California, Information Sciences Institute
    COPYRIGHT: {<COPYRIGHT> <NN> <NAME>}       #2635

    # Copyright 2008 TJ <linux@tjworld.net>
    COPYRIGHT: {<COPYRIGHT2> <EMAIL>}       #2636

    COPYRIGHT: {<COPYRIGHT> <CAPS> <NAME2>}       #2637

    # maintainer Norbert Tretkowski <nobse@debian.org> 2005-04-16
    AUTHOR: {<BY|MAINT> <NAME2> <YR-RANGE>?}  #26382

    # Russ Dill <Russ.Dill@asu.edu> 2001-2003
    COPYRIGHT: {<NAME2> <YR-RANGE>}       #2638

    # (C) 2001-2009, <s>Takuo KITAME, Bart Martens, and  Canonical, LTD</s>
    COPYRIGHT: {<COPYRIGHT> <NNP> <COMPANY>}       #26381

    #Copyright Holders Kevin Vandersloot <kfv101@psu.edu> Erik Johnsson <zaphod@linux.nu>
    COPYRIGHT: {<COPY> <HOLDER> <NAME>}       #26383

    #Copyright (c) 1995, 1996 - Blue Sky Software Corp.
    COPYRIGHT: {<COPYRIGHT2> <DASH> <COMPANY>}       #2639

    #copyright 2000-2003 Ximian, Inc. , 2003 Gergo Erdi
    COPYRIGHT: {<COPYRIGHT> <NNP> <NAME3>}        #1565

    #2004+ Copyright (c) Evgeniy Polyakov <zbr@ioremap.net>
    COPYRIGHT: {<YR-PLUS> <COPYRIGHT>}        #1566

    # Copyright (c) 1992 David Giller, rafetmad@oxy.edu 1994, 1995 Eberhard Moenkeberg, emoenke@gwdg.de 1996 David van Leeuwen, david@tm.tno.nl
    COPYRIGHT: {<COPYRIGHT> <EMAIL>}        #2000

    COPYRIGHT: {<COPYRIGHT> <NAME3>}        #2001

    # copyright by M.I.T. or by MIT
    COPYRIGHT: {<COPY> <BY> <NNP|CAPS>}        #2002

    # Copyright property of CompuServe Incorporated.
    COPYRIGHT: {<COPY> <NN> <OF> <COMPANY>}        #2003

    # Copyright (c) 2005 DMTF.
    COPYRIGHT: {<COPY> <YR-RANGE> <PN>}        #2004

    # Copyright (c) YEAR This_file_is_part_of_KDE
    COPYRIGHT: {<COPY> <COPY> <CAPS>}        #2005

    # copyright by the Free Software Foundation
    COPYRIGHT: {<COPY> <BY> <NN>? <NNP>? <COMPANY>}        #2006

    # copyright C 1988 by the Institute of Electrical and Electronics Engineers, Inc
    COPYRIGHT: {<COPY>  <PN>?  <YR-RANGE>  <BY>  <NN>  <NAME>}   #2007

    # COPYRIGHT (c) 2006 - 2009 DIONYSOS
    COPYRIGHT: {<COPYRIGHT2>  <CAPS>} # 2008
    # Copyright (C) 2000 See Beyond Communications Corporation
    COPYRIGHT2: {<COPYRIGHT2> <JUNK> <COMPANY>} # 2010

    # copyright C 1988 by the Institute of Electrical and Electronics Engineers, Inc.
    COPYRIGHT: {<COPY>  <PN>  <YR-RANGE>  <COMPANY>}

    COPYRIGHT2: {<NAME4> <COPYRIGHT2>}  #2274

    #Copyright or Copr. CNRS
    NAME5: {<CAPS>+}        #2530
    #Copyright or Copr. CNRS
    COPYRIGHT: {<COPY> <NN> <COPY> <COPYRIGHT|NAME5>}        #2560
    COPYRIGHT: {<COPYRIGHT2>  <BY>  <NAME5>} #2561

# Authors
    AUTH: {<AUTH2>+ <BY>}        #2645
    AUTHOR: {<AUTH|CONTRIBUTORS|AUTHS>+ <NN>? <COMPANY|NAME|YR-RANGE>* <BY>? <EMAIL>+}        #2650
    AUTHOR: {<AUTH|CONTRIBUTORS|AUTHS>+ <NN>? <COMPANY|NAME|NAME2>+ <YR-RANGE>*}        #2660
    AUTHOR: {<AUTH|CONTRIBUTORS|AUTHS>+ <YR-RANGE>+ <BY>? <COMPANY|NAME|NAME2>+}        #2670
    AUTHOR: {<AUTH|CONTRIBUTORS|AUTHS>+ <YR-RANGE|NNP> <NNP|YR-RANGE>+}        #2680
    AUTHOR: {<AUTH|CONTRIBUTORS|AUTHS>+ <NN|CAPS>? <YR-RANGE>+}        #2690
    AUTHOR: {<COMPANY|NAME|NAME2>+ <AUTH|CONTRIBUTORS|AUTHS>+ <YR-RANGE>+}        #2700
    AUTHOR: {<YR-RANGE> <NAME|NAME2>+}        #2710
    AUTHOR: {<BY> <CC>? <NAME2>+}        #2720
    AUTHOR: {<AUTH|CONTRIBUTORS|AUTHS>+ <NAME2>+}        #2720
    AUTHOR: {<AUTHOR> <CC> <NN>? <AUTH|AUTHS>}        #2730
    AUTHOR: {<BY> <EMAIL>}        #2740
    ANDAUTH: {<CC> <AUTH|NAME|CONTRIBUTORS>+}        #2750
    AUTHOR: {<AUTHOR> <ANDAUTH>+}        #2760

    # developed by Mitsubishi and NTT.
    AUTHOR: {<AUTH|AUTHS|AUTH2> <BY>? <NNP> <CC> <PN>}

    # Compounded statements usings authors
    # found in some rare cases with a long list of authors.
    COPYRIGHT: {<COPY> <BY> <AUTHOR>+ <YR-RANGE>*}        #2800

    COPYRIGHT: {<AUTHOR> <COPYRIGHT2>}        #2820
    COPYRIGHT: {<AUTHOR> <YR-RANGE>}        #2830
"""


def strip_numbers(s):
    """
    Return a string removing words made only of numbers. If there is an
    exception or s is not a string, return s as-is.
    """
    if s:
        s = u' '.join([x for x in s.split(' ') if not x.isdigit()])
    return s


def strip_some_punct(s):
    """
    Return a string stripped from some leading and trailing punctuations.
    """
    if s:
        s = s.strip(''','"}{-_:;&''')
        s = s.lstrip('.>)]')
        s = s.rstrip('<([')
    return s


def fix_trailing_space_dot(s):
    """
    Return a string stripped from some leading and trailing punctuations.
    """
    if s and s.endswith(' .'):
        s = s[:-2] + '.'
    return s


def strip_unbalanced_parens(s, parens='()'):
    """
    Return a string where unbalanced parenthesis are replaced with a space.
    `paren` is a pair of characters to balance  such as (), <>, [] , {}.

    For instance:
    >>> strip_unbalanced_parens('This is a super string', '()')
    'This is a super string'

    >>> strip_unbalanced_parens('This is a super(c) string', '()')
    'This is a super(c) string'

    >>> strip_unbalanced_parens('This ((is a super(c) string))', '()')
    'This ((is a super(c) string))'

    >>> strip_unbalanced_parens('This )(is a super(c) string)(', '()')
    'This  (is a super(c) string) '

    >>> strip_unbalanced_parens(u'This )(is a super(c) string)(', '()')
    u'This  (is a super(c) string) '

    >>> strip_unbalanced_parens('This )(is a super(c) string)(', '()')
    'This  (is a super(c) string) '

    >>> strip_unbalanced_parens('This )((is a super(c) string)((', '()')
    'This   (is a super(c) string)  '

    >>> strip_unbalanced_parens('This ) is', '()')
    'This   is'

    >>> strip_unbalanced_parens('This ( is', '()')
    'This   is'

    >>> strip_unbalanced_parens('This )) is', '()')
    'This    is'

    >>> strip_unbalanced_parens('This (( is', '()')
    'This    is'

    >>> strip_unbalanced_parens('(', '()')
    ' '

    >>> strip_unbalanced_parens(')', '()')
    ' '
    """
    start, end = parens
    if not start in s and not end in s:
        return s

    unbalanced = []
    unbalanced_append = unbalanced.append

    stack = []
    stack_append = stack.append
    stack_pop = stack.pop

    for i, c in enumerate(s):
        if c == start:
            stack_append((i, c,))
        elif c == end:
            try:
                stack_pop()
            except IndexError:
                unbalanced_append((i, c,))

    unbalanced.extend(stack)
    pos_to_del = set([i for i, c in unbalanced])
    cleaned = [c if i not in pos_to_del else ' ' for i, c in enumerate(s)]
    return type(s)('').join(cleaned)


def strip_all_unbalanced_parens(s):
    """
    Return a string where unbalanced parenthesis are replaced with a space.
    Strips (), <>, [] and {}.
    """
    c = strip_unbalanced_parens(s, '()')
    c = strip_unbalanced_parens(c, '<>')
    c = strip_unbalanced_parens(c, '[]')
    c = strip_unbalanced_parens(c, '{}')
    return c


def refine_copyright(c):
    """
    Refine a detected copyright string.
    FIXME: the grammar should not allow this to happen.
    """
    c = strip_some_punct(c)
    c = fix_trailing_space_dot(c)
    c = strip_all_unbalanced_parens(c)
    # FIXME: this should be in the grammar, but is hard to get there right
    # these are often artifacts of markup
    c = c.replace('COPYRIGHT Copyright', 'Copyright')
    c = c.replace('Copyright Copyright', 'Copyright')
    c = c.replace('Copyright copyright', 'Copyright')
    c = c.replace('copyright copyright', 'Copyright')
    c = c.replace('copyright Copyright', 'Copyright')
    c = c.replace('copyright\'Copyright', 'Copyright')
    c = c.replace('copyright"Copyright', 'Copyright')
    c = c.replace('copyright\' Copyright', 'Copyright')
    c = c.replace('copyright" Copyright', 'Copyright')

    c = c.replace('<p>', ' ')

    prefixes = set([
        'by',
    ])

    s = strip_prefixes(c, prefixes)

    s = s.split()

    # fix traliing garbage, captured by the grammar
    last_word = s[-1]
    if last_word.lower() in ('parts', 'any', '0', '1'):
        s = s[:-1]
    # this is hard to catch otherwise, unless we split the author
    # vs copyright grammar in two. Note that AUTHOR and Authors should be kept
    last_word = s[-1]
    if last_word.lower() == 'author' and last_word not in ('AUTHOR', 'AUTHORS', 'Authors',) :
        s = s[:-1]

    s = u' '.join(s)
    return s


prefixes = frozenset([
    '?',
    '????',
    '(insert',
    'then',
    'current',
    'year)',
    'maintained',
    'by',
    'developed',
    'written',
    'created',
    '$year',
    'year',
    'uref',
    'owner',
    'from',
    'and',
    'of',
    'to',
    'for',
    '<p>',
])


def _refine_names(s, prefixes=prefixes):
    """
    Refine a detected holder.
    FIXME: the grammar should not allow this to happen.
    """
    s = strip_some_punct(s)
    s = strip_numbers(s)
    s = strip_all_unbalanced_parens(s)
    s = strip_some_punct(s)

    return strip_prefixes(s, prefixes)


JUNK_HOLDERS = frozenset([
    'property',
    'licensing@',
    'c',
    'works',
    'http',
    'the',
    'are',
    '?',
    'cppyright',
    'parts',
    'disclaimed',
    'or',
])


def refine_holder(s, prefixes=prefixes):
    """
    Refine a detected holder.
    FIXME: the grammar should not allow this to happen.
    """
    refined = _refine_names(s, prefixes)
    if refined.lower() not in JUNK_HOLDERS:
        return refined


def refine_author(s, prefixes=prefixes.union(frozenset([
        'contributor', 'contributors', 'contributor(s)',
        'author', 'authors', 'author(s)', 'authored', ])
        )):
    """
    Refine a detected author.
    FIXME: the grammar should not allow this to happen.
    """
    # FIXME: also split comma separated lists: gthomas, sorin@netappi.com, andrew.lunn@ascom.che.g.
    return _refine_names(s, prefixes)


def strip_prefixes(s, prefixes=()):
    """
    Return the `s` string with any of the string in the `prefixes` set
    striped. Normalize and strip spacing.
    """
    s = s.split()
    # strip prefixes.
    # NOTE: prefixes are hard to catch otherwise, unless we split the
    # author vs copyright grammar in two
    while s and s[0].lower() in prefixes:
        s = s[1:]
    s = u' '.join(s)
    return s


def refine_date(c):
    """
    Refine a detected date or date range.
    FIXME: the grammar should not allow this to happen.
    """
    return strip_some_punct(c)


# note: this must be lowercase
junk = frozenset([
    'full copyright statement',
    'copyrighted by their authors',
    'copyrighted by their authors.',
    'copyright holder or other authorized',
    'copyright holder who authorizes',
    'copyright holder has authorized',
    'copyright holder nor the author',
    'copyright holder(s) or the author(s)',
    'copyright holders and contributors',
    'copyright owner or entity authorized',
    'copyright owner or contributors',
    'copyright and license, contributing',
    'copyright for a new language file should be exclusivly the authors',
    'copyright (c) year',
    'copyright (c) year your name',
    'copyright holder or said author',
    'copyright holder, or any author',
    'copyrighted material, only this license, or another one contracted with the authors',
    'copyright notices, authorship',
    'copyright holder means the original author(s)',
    "copyright notice. timevar.def's author",
    'copyright copyright and',
    "copyright holder or simply that it is author-maintained'.",
    "copyright holder or simply that is author-maintained'.",
    '(c) if you bring a patent claim against any contributor',
    'copyright-check writable-files m4-check author_mark_check',
    # 'copyrighting it yourself or claiming authorship'
    "copyright of uc berkeley's berkeley software distribution",
    '(c) any recipient',
    '(c) each recipient',
])


def is_junk(c):
    """
    Return True if string `c` is a junk copyright that cannot be resolved
    otherwise by parsing with a grammar.
    It would be best not to have to resort to this, but this is practical.
    """
    return c.lower() in junk


class CopyrightDetector(object):
    """
    Class to detect copyrights and authorship.
    """

    def __init__(self):
        from nltk import RegexpTagger
        from nltk import RegexpParser
        self.tagger = RegexpTagger(patterns)
        self.chunker = RegexpParser(grammar, trace=TRACE_DEEP)

    @classmethod
    def as_str(cls, node, ignores=()):
        """
        Return a parse tree node as a space-normalized string.
        Optionally filters node labels provided in the ignores tuple or set.
        """
        if ignores:
            leaves = (leaf_text for leaf_text, leaf_label in node.leaves()
                                            if leaf_label not in ignores)
        else:
            leaves = (leaf_text for leaf_text, leaf_label in node.leaves())

        node_string = ' '.join(leaves).strip()
        return u' '.join(node_string.split())

    def detect(self, numbered_lines):
        """
        Return a sequence of tuples (copyrights, authors, years, holders)
        detected in a sequence of numbered line tuples.
        """
        from nltk.tree import Tree
        numbered_lines = list(numbered_lines)
        numbers = [n for n, _l in numbered_lines]
        start_line = min(numbers)
        end_line = max(numbers)
        tokens = self.get_tokens(numbered_lines)
        if TRACE:
            logger_debug('CopyrightDetector:detect:tokens:', tokens)

        # we accumulate detected items in these synchronized lists
        # this could be a single list of namedtuples
        # or a list of dicts instead
        copyrights, authors, years, holders = [], [], [], []

        if not tokens:
            return copyrights, authors, years, holders, None, None

        # OPTIMIZED
        copyrights_append = copyrights.append
        authors_append = authors.append
        years_append = years.append
        holders_append = holders.append

        # first, POS tag each token using token regexes
        tagged_text = self.tagger.tag(tokens)
        if TRACE: logger_debug('CopyrightDetector:tagged_text: ' + str(tagged_text))

        # then build a parse tree based on tagged tokens
        tree = self.chunker.parse(tagged_text)
        if TRACE: logger_debug('CopyrightDetector:parse tree: ' + str(tree))

        CopyrightDetector_as_str = CopyrightDetector.as_str

        def collect_holders(detected_copyright):
            """
            Walk the parse sub-tree starting with the `detected_copyright`
            node collecting all holders.
            """
            for copyhold in detected_copyright:
                if isinstance(copyhold, Tree):
                    holder_label = copyhold.label()
                    if TRACE: logger_debug(u'Tree with label:', holder_label)
                    if holder_label.startswith('NAME') or 'COMPANY' in holder_label :
                        if TRACE: logger_debug(u' NAME or COMPANY')
                        # FIXME : this may wreck things like 23andme
                        # where a company name contains numbers
                        node_text = CopyrightDetector_as_str(copyhold, ignores=('YR-RANGE', 'EMAIL', 'YR', 'URL', 'COPY', 'YR'))
                        if TRACE: logger_debug(u'   holder raw:', node_text)
                        node_text = refine_holder(node_text)
                        if TRACE: logger_debug(u'      holder refined:', node_text)
                        if node_text:
                            holders_append(node_text)
                    else:
                        if TRACE: logger_debug(u' other label')
                        collect_holders(copyhold)

                elif isinstance(copyhold, tuple):
                    if TRACE: logger_debug(u'Tuple:', copyhold)
                    hvalue, hlabel = copyhold
                    if hlabel in ('CAPS', 'NNP', 'NN', 'CONTRIBUTORS') and hvalue:
                        if TRACE: logger_debug(u' CAPS or NNP or NN:', hvalue)
                        hvalue = refine_holder(hvalue)
                        if TRACE: logger_debug(u'      holder refined:', hvalue)
                        if hvalue:
                            holders_append(hvalue)

        def collect_years(detected_copyright):
            """
            Walk the a parse sub-tree starting with the `detected_copyright`
            node collecting all years.
            """
            for copyyear in detected_copyright:
                if not isinstance(copyyear, Tree):
                    continue
                copyyear_label = copyyear.label()
                if TRACE: logger_debug('node: ' + str(copyyear) + ' label: ' + copyyear_label)
                if 'YR-RANGE' in copyyear_label :
                    if TRACE: logger_debug('node is YEAR')
                    node_text = CopyrightDetector_as_str(copyyear)
                    years_append(refine_date(node_text))
                else:
                    collect_years(copyyear)

        # then walk the parse tree, collecting copyrights, years and authors
        for tree_node in tree:
            if isinstance(tree_node, Tree):
                node_text = CopyrightDetector_as_str(tree_node)
                tree_node_label = tree_node.label()
                if 'COPYRIGHT' in tree_node_label:
                    if node_text and node_text.strip():
                        refined = refine_copyright(node_text)
                        if not is_junk(refined):
                            copyrights_append(refined)
                            collect_years(tree_node)
                            collect_holders(tree_node)
                elif tree_node_label == 'AUTHOR':
                    authors_append(refine_author(node_text))

        return copyrights, authors, years, holders, start_line, end_line

    def get_tokens(self, numbered_lines):
        """
        Return an iterable of tokens from lines of text.
        """
        tokens = []
        tokens_append = tokens.append

        # simple tokenization: spaces and some punctuation
        splitter = re.compile('[\\t =;]+').split

        for _line_number, line in numbered_lines:
            line = line.strip()
            if line:
                line = prepare_text_line(line)
            if line :
                line = strip_markup(line)
            if line and line.strip():
                for tok in splitter(line):
                    # strip trailing quotes and ignore empties
                    tok = tok.strip("' ")
                    if not tok:
                        continue
                    # strip trailing colons: why?
                    tok = tok.rstrip(':').strip()
                    # strip leading @: : why?
                    tok = tok.lstrip('@').strip()
                    if tok and tok not in (':',):
                        tokens_append(tok)
        if TRACE: logger_debug('CopyrightDetector:tokens: ' + repr(tokens))
        return tokens


def prep_line(line):
    """
    Return a tuple of (line, line with only chars) from a line of text prepared
    for candidate and other checks or None.
    """
    line = prepare_text_line(line.lower())
    chars_only = re.sub(r'[^a-z0-9]', '', line)

    return line.strip(), chars_only.strip()


def is_candidate(prepped_line):
    """
    Return True if a prepped line is a candidate line for copyright detection
    """
    if not prepped_line:
        return False
    if copyrights_hint.years(prepped_line):
        # if TRACE: logger_debug('is_candidate: year in line:\n%(line)r' % locals())
        return True
    else:
        pass
        # if TRACE: logger_debug('is_candidate: NOT year in line:\n%(line)r' % locals())

    for marker in copyrights_hint.statement_markers:
        if marker in prepped_line:
            # if TRACE: logger_debug('is_candidate: %(marker)r in line:\n%(line)r' % locals())
            return True


def is_eol_copyright_line(chars_only_line):
    """
    Return True if a prepped line contains the copyright word
    """
    if TRACE: logger_debug('is_eol_copyright_line: ' + repr(chars_only_line))
    copyrs = ('copyright', 'copyrights', 'copyrightby')
    return chars_only_line and chars_only_line.endswith(copyrs)


def is_all_rights_reserved(chars_only_line):
    """
    Return True if a line ends with "all rights reserved"-like statements.
    """
    return chars_only_line and chars_only_line.endswith(('rightreserved', 'rightsreserved'))


def candidate_lines(lines):
    """
    Yield lists of candidate lines where each list element is a tuple of
    (line number,  line text).

    A candidate line is a line of text that may contain copyright statements.
    A few lines before and after a candidate line are also included.
    """
    candidates = deque()
    candidates_append = candidates.append
    candidates_clear = candidates.clear

    previous = None
    previous_chars_only_line = None
    # used as a state and line counter
    in_copyright = 0
    for line_number, line in enumerate(lines):
        if TRACE:
            logger_debug('candidate_lines: ' + repr(line))
        # the first line number is ONE, not zero
        numbered_line = (line_number + 1, line)
        prepped_line, chars_only_line = prep_line(line)
        if is_candidate(prepped_line):
            # the state is now "in copyright"
            in_copyright = 2
            # we keep one line before a candidate line if any
            if previous:
                candidates_append(previous)
                previous = None
                previous_chars_only_line = None
            # we keep the candidate line and yield if we reached the end
            # of a statement
            candidates_append(numbered_line)
            if is_all_rights_reserved(chars_only_line):
                yield list(candidates)
                candidates_clear()
                in_copyright = 0
            if is_eol_copyright_line(chars_only_line):
                previous_chars_only_line = chars_only_line
            else:
                previous_chars_only_line = None
        else:
            if in_copyright:
                # if the previous line was a candidate
                # then we keep one line after that candidate line
                if chars_only_line:
                    candidates_append(numbered_line)
                    # and decrement our state
                    in_copyright -= 1
                else:
                    if is_eol_copyright_line(previous_chars_only_line):
                        in_copyright -= 1
                        continue
                    if candidates:
                        yield list(candidates)
                        candidates_clear()
                    in_copyright = 0
            else:
                # if are neither a candidate line nor the line just after
                # then we yield the accumulated lines if any
                if candidates:
                    yield list(candidates)
                    candidates_clear()
                # and we keep track of this line as "previous" if not empty
                if chars_only_line:
                    previous = numbered_line
                    previous_chars_only_line = chars_only_line

                else:
                    previous = None
                    previous_chars_only_line = None
    # finally
    if candidates:
        yield list(candidates)


def strip_markup(text):
    """
    Strip markup tags from text.
    """
    html_tag_regex = re.compile(
        r'<'
        r'[(--)\?\!\%\/]?'
        r'[a-gi-vx-zA-GI-VX-Z][a-zA-Z#\"\=\s\.\;\:\%\&?!,\+\*\-_\/]*'
        r'[a-zA-Z0-9#\"\=\s\.\;\:\%\&?!,\+\*\-_\/]+'
        r'\/?>',
        re.MULTILINE | re.UNICODE
    )
    if text:
        text = re.sub(html_tag_regex, ' ', text)
        text = text.replace('</s>', '').replace('<s>', '')
    return text


COMMON_WORDS = set([
    'Unicode',
    'Modified',
    'NULL',
    'FALSE', 'False',
    'TRUE', 'True',
    'Last',
    'Predefined',
    'If',
    'Standard',
    'Version', 'Versions',
    'Package', 'PACKAGE',
    'Powered',
    'Licensed', 'License', 'License.' 'Licensee', 'License:', 'License-Alias:',
    'Legal',
    'Entity',
    'Indemnification.',
    'IS',
    'This',
    'Java',
    'DoubleClick',
    'DOM', 'SAX', 'URL',
    'Operating System',
    'Original Software',
    'Berkeley Software Distribution',
    'Software Release', 'Release',
    'IEEE Std',
    'BSD',
    'POSIX',
    'Derivative Works',
    'Intellij IDEA',
    'README', 'NEWS',
    'ChangeLog', 'CHANGElogger', 'Changelog',
    'Redistribution',
])


def lowercase_well_known_word(text):
    """
    Return text with certain words lowercased.
    Rationale: some common words can start with a capital letter and be mistaken
    for a named entity because capitalized words are often company names.
    """
    lines = []
    lines_append = lines.append
    for line in text.splitlines(True):
        words = []
        words_append = words.append
        for word in line.split():
            if word in COMMON_WORDS:
                word = word.lower()
            words_append(word)
        lines_append(' '.join(words))
    return '\n'.join(lines)

# FIXME: instead of using functions, use plain re and let the re cache do its work


def IGNORED_PUNCTUATION_RE():
    return re.compile(r'[*#"%\[\]\{\}`]+', re.I | re.M | re.U)


def ASCII_LINE_DECO_RE():
    return re.compile(r'[-_=!\\*]{2,}')


def ASCII_LINE_DECO2_RE():
    return re.compile(r'/{3,}')


def WHITESPACE_RE():
    return re.compile(r' +')


def MULTIQUOTES_RE():
    return re.compile(r"\'{2,}")


# TODO: add debian <s> </s> POS name taggings
def DEBIAN_COPYRIGHT_TAGS_RE():
    return re.compile(r"(\<s\>|\<s\\/>)")


def prepare_text_line(line):
    """
    Prepare a line of text for copyright detection.
    """
    # FIXME: maintain the original character positions
    re_sub = re.sub

    # strip whitespace
    line = line.strip()
    # FIXME: how did we get line returns in this????
    line = line.replace('\n', ' ')

    # remove some junk in man pages: \(co
    line = line.replace(r'\\ co', ' ')
    line = line.replace(r'\ co', ' ')
    line = line.replace(r'(co ', ' ')

    # replace ('
    line = line.replace(r'("', ' ')

    # un common comment line prefix in dos
    line = re_sub('^rem\s+', ' ', line)
    line = re_sub('^\@rem\s+', ' ', line)
    # less common comment line prefix in autotools am/in
    line = re_sub('^dnl\s+', ' ', line)
    # un common comment line prefix in man pages
    line = re_sub('^\.\\\\"', ' ', line)
    # un common pipe chars in some ascii art
    line = line.replace('|', ' ')

    # normalize copyright signs and spacing around them
    line = line.replace('(C)', ' (c) ')
    line = line.replace('(c)', ' (c) ')
    # the case of \251 is tested by 'weirdencoding.h'
    line = line.replace(u'\251', u' (c) ')
    line = line.replace('&copy;', ' (c) ')
    line = line.replace('&#169;', ' (c) ')
    line = line.replace('&#xa9;', ' (c) ')
    line = line.replace('&#XA9;', ' (c) ')
    line = line.replace(u'\xa9', ' (c) ')
    line = line.replace(u'\XA9', ' (c) ')
    # FIXME: what is \xc2???
    line = line.replace(u'\xc2', '')

    # TODO: add more HTML entities replacements
    # see http://www.htmlhelp.com/reference/html40/entities/special.html
    # convert html entities &#13;&#10; CR LF to space
    line = line.replace(u'&#13;&#10;', ' ')
    line = line.replace(u'&#13;', ' ')
    line = line.replace(u'&#10;', ' ')
    # spaces
    line = line.replace(u'&ensp;', ' ')
    line = line.replace(u'&emsp;', ' ')
    line = line.replace(u'&thinsp;', ' ')

    # common named entities
    line = line.replace(u'&quot;', '"').replace(u'&#34;', '"')
    line = line.replace(u'&amp;', '&').replace(u'&#38;', '&')
    line = line.replace(u'&gt;', '>').replace(u'&#62;', '>')
    line = line.replace(u'&lt;', '<').replace(u'&#60;', '<')

    # normalize (possibly repeated) quotes to unique single quote '
    # backticks ` and "
    line = line.replace(u'`', "'")
    line = line.replace(u'"', "'")
    line = re.sub(MULTIQUOTES_RE(), "'", line)
    # quotes to space?  but t'so will be wrecked
    # line = line.replace(u"'", ' ')

    # treat explicit CR, LF and tabs as space
    line = line.replace("\\n", ' ')
    line = line.replace("\\r", ' ')
    line = line.replace("\\t", ' ')

    # remove backslash
    line = line.replace("\\", ' ')

    # some trailing garbage ')
    line = line.replace("')", '  ')

    # note that we do not replace the debian tag by a space:  we remove it
    # TODO: use POS tag:     (r'^(?:\<s\>).*(?:\<s\\/>)$', 'NAME'),
    line = re_sub(DEBIAN_COPYRIGHT_TAGS_RE(), '', line)

    line = re_sub(IGNORED_PUNCTUATION_RE(), ' ', line)

    # tabs to spaces
    line = line.replace('\t', ' ')

    # normalize spaces around commas
    line = line.replace(' , ', ', ')

    # remove ASCII "line decorations"
    # such as in --- or === or !!! or *****
    line = re_sub(ASCII_LINE_DECO_RE(), ' ', line)
    line = re_sub(ASCII_LINE_DECO2_RE(), ' ', line)

    # Replace escaped literal \0 \n \r \t that may exist as-is by a space
    # such as in code literals: a="\\n some text"
    line = line.replace('\\r', ' ')
    line = line.replace('\\n', ' ')
    line = line.replace('\\t', ' ')
    line = line.replace('\\0', ' ')

    # in apache'>Copyright replace ">" by "> "
    line = line.replace('>', '> ')
    line = line.replace('>  ', '> ')
    line = line.replace('<', ' <')
    line = line.replace('  <', ' <')

    # TODO: Why?
    # replace contiguous spaces with only one occurrence
    # line = re.sub(WHITESPACE_RE(), ' ', text)

    # normalize to ascii text
    line = commoncode.text.toascii(line)
    # if TRACE: logger_debug("ascii_only_text: " + text)

    # strip verbatim back slash and comment signs again at both ends of a line
    # FIXME: this is done at the start of this function already
    line = line.strip('\\/*#%;')

    # normalize to use only LF as line endings so we can split correctly
    # and keep line endings
    line = commoncode.text.unixlinesep(line)
    # why?
    line = lowercase_well_known_word(line)

    # strip comment markers
    # common comment characters
    line = line.strip('\\/*#%;')

    return line
