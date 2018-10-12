# -*- coding: utf-8 -*-
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

from commoncode.text import toascii
from commoncode.text import unixlinesep
from cluecode import copyrights_hint
from textcode import analysis


# Tracing flags
TRACE = False or os.environ.get('SCANCODE_DEBUG_COPYRIGHT', False)
# set to 1 to enable nltk deep tracing
TRACE_DEEP = 0
if os.environ.get('SCANCODE_DEBUG_COPYRIGHT_DEEP'):
    TRACE_DEEP = 1


# Tracing flags
def logger_debug(*args):
    pass


if TRACE or TRACE_DEEP:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, (unicode, str)) and a or repr(a) for a in args))

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
 - yield copyright statements,holder and authors with start and end line
   from the parse tree with some post-detection cleanups.
"""


def detect_copyrights(location, copyrights=True, holders=True, authors=True, include_years=True):
    """
    Yield tuples of (detection type, detected string, start line, end line)
    detected in file at `location`.
    Include years in copyrights if include_years is True.
    Valid detection types are: copyrights, authors, holders.
    These are included in the yielded tuples based on the values of `copyrights=True`, `holders=True`, `authors=True`,
    """
    detector = CopyrightDetector()
    numbered_lines = analysis.numbered_text_lines(location, demarkup=True)
    numbered_lines = list(numbered_lines)
    if TRACE:
        numbered_lines = list(numbered_lines)
        for nl in numbered_lines:
            logger_debug('numbered_line:', repr(nl))

    for candidates in candidate_lines(numbered_lines):
        for detection in detector.detect(candidates, copyrights, holders, authors, include_years):
            # tuple of type, string, start, end
            yield detection


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
    # various programming constructs
    (r'^(var|this|return|function|thats?|xmlns|file)$', 'JUNK'),

    (r'^(([A-Z][a-z]+){3,}[A-Z]+[,]?)$', 'JUNK'),
    (r'^(([A-Z][a-z]+){3,}[A-Z]+[0-9]+[,]?)$', 'JUNK'),

    # multiple parens (at least two (x) groups) is a sign of junk
    # such as in (1)(ii)(OCT
    (r'^.*\(.*\).*\(.*\).*$', 'JUNK'),

    # neither and nor conjunctions and some common licensing words are NOT part
    # of a copyright statement
    (r'^(neither|nor|providing|Execute|NOTICE|passes|LAWS\,?|Should'
     r'|Licensing|Disclaimer|Law|Some|Derived|Limitations?|Nothing|Policy'
     r'|available|Recipient\.?|LICENSEE|Application|Receiving|Party|interfaces'
     r'|owner|Sui|Generis|Conditioned|Disclaimer|Warranty|Represents|Sufficient|Each'
     r'|Partially|Limitation|Liability|Named|Use.|EXCEPT|OWNER\.?|Comments\.?'
     r')$', 'JUNK'),

    # various trailing words that are junk
    (r'^(?:Copyleft|LegalCopyright|AssemblyCopyright|Distributed|Report|'
     r'Available|true|false|node|jshint|node\':true|node:true|this|Act,?|'
     r'[Ff]unctionality|bgcolor|F+|Rewrote|Much|remains?,?|Implementation|earlier'
     r'|al.|is|[lL]aws?|Insert|url|[Ss]ee|[Pp]ackage\.?|'
     r'|Covered|date|practices'
     r'|fprintf.*'
     r')$', 'JUNK'),

    # some copyright templates in licenses
    (r'^\$(date-of-software|date-of-document)$', 'JUNK'),

    # NOT A CAPS
    # [YEAR] W3C® (MIT, ERCIM, Keio, Beihang)."
    (r'^YEAR', 'NN'),

    # RCS keywords
    (r'^(Header|Id|Locker|Log|RCSfile|Revision)$', 'NN'),

    # this trigger otherwise "copyright ownership. The ASF" in Apache license headers
    (r'^([Oo]wnership\.?)$', 'JUNK'),

    # names with a slash that are NNP
    # Research/Unidata , LCS/Telegraphics.
    (r'^([A-Z]([a-z]|[A-Z])+/[A-Z][a-z]+[\.,]?)$', 'NNP'),

    # Various NN, exceptions to NNP or CAPS
    (r'^(Send|It|Mac|Support|Information|Various|Mouse|Wheel'
      r'|Vendor|Commercial|Indemnified|Luxi|These|Several|GnuPG|WPA|Supplicant'
      r'|TagSoup|Contact|IA64|Foreign|Data|Atomic|Pentium|Note|Delay|Separa.*|Added'
      r'|Glib|Gnome|Gaim|Open|Possible|In|Read|Permissions?|New|MIT'
      r'|Agreement\.?|Immediately|Any|Custom|Reference|Each'
      r'|Education|AIRTM|Copying|Updated|Source|Code|Website'
      r')$', 'NN'),
    # |Products\.?

    # MORE NN exceptions to NNP or CAPS
    # 'Berkeley Software Distribution',??
    (r'^(Unicode|Modified|NULL|FALSE|False|TRUE|True|Last|Predefined|If|Standard'
      r'|Versions?\.?|Package|PACKAGE|Powered|License[d\.e\:]?|License-Alias\:?|Legal'
      r'|Entity|Indemnification\.?|IS|This|Java|DoubleClick|DOM|SAX|URL|Operating'
      r'|Original|Release|IEEE|Std|BSD|POSIX|Derivative|Works|Intellij|IDEA|README'
      r'|NEWS|CHANGELOG|Change[lL]og|CHANGElogger|Redistribution|Reserved\.?'
      r')$', 'NN'),

    # MORE NN exceptions to CAPS
    (r'^(OR|VALUE|END)$', 'NN'),

    # Various rare non CAPS but NNP, treated as full names
    (r'^(FSF[\.,]?)$', 'NAME'),

    # Windows XP
    (r'^(Windows|XP|SP1|SP2|SP3|SP4|assembly)$', 'JUNK'),

    (r'^example\.com$', 'JUNK'),

    # Java
    (r'^.*Servlet,?|class$', 'JUNK'),

    # C/C++
    (r'^(template|struct|typedef|type|next|typename|namespace|type_of|begin|end)$', 'JUNK'),

    # Some mixed case junk
    (r'^LastModified$', 'JUNK'),

    # Some font names
    (r'^Lucida$', 'JUNK'),

    # various trailing words that are junk
    (r'^(?:CVS|EN-IE|Info|GA|unzip)$', 'JUNK'),

    # this is not Copr.
    (r'Coproduct,?', 'JUNK'),

    # Places: TODO: these are NOT NNPs but we treat them as such for now
    (r'^\(?(?:Cambridge|Stockholm|Davis|Sweden[\)\.]?|Massachusetts|Oregon|California'
     r'|Norway|UK|Berlin|CONCORD|Manchester|MASSACHUSETTS|Finland|Espoo|Munich'
     r'|Germany|Italy|Spain|Europe'
     r'|Lafayette|Indiana'
     r')[\),\.]?$', 'NNP'),

    # Date/Day/Month text references
    (r'^(Date|am|pm|AM|PM)$', 'NN'),
    (r'^(January|February|March|April|May|June|July|August|September|October|November|December)$', 'NN'),

    # Jan and Jun are common enough first names
    (r'^(Feb|Mar|Apr|May|Jul|Aug|Sep|Oct|Nov|Dec)$', 'NN'),
    (r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)$', 'NN'),
    (r'^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)$', 'NN'),

    (r'^\$?LastChangedDate\$?$', 'YR'),

    # Misc corner case combos ?(mixed or CAPS) that are NNP
    (r'^Software,\',|\(Royal|PARADIGM|nexB|D\.T\.Shield\.?|Antill\',$', 'NNP'),

    # Corner cases of lowercased NNPs
    (r'^(suzuki|toshiya\.?|leethomason|finney|sean|chris|ulrich'
     r'|wadim|dziedzic|okunishinishi|yiminghe|daniel|wirtz'
     r'|vonautomatisch|werkstaetten\.?|werken|various\.?)$', 'NNP'),

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

    # A copyright line in .Net meta files
    (r'^AssemblyCopyright$', 'COPY'),

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
    (r'^([Ll][Ll][CcPp]|[Ll][Tt][Dd])\.?,?$', 'COMP'),
    (r'^L\.P\.?$', 'COMP'),
    (r'^[Ss]ubsidiar(y|ies)$', 'COMP'),
    (r'^[Ss]ubsidiary\(\-ies\)\.?$', 'COMP'),
    # company suffix : SA, SAS, AS, AG, AB, AS, CO, labs followed by a dot
    (r'^(S\.?A\.?S?\.?|Sas\.?|sas\.?|AS\.?|AG\.?|AB\.?|Labs?\.?|[Cc][Oo]\.?|Research|Center|INRIA|Societe).?$', 'COMP'),
    # (german) company suffix
    (r'^[Gg][Mm][Bb][Hh].?$', 'COMP'),
    # ( e.V. german) company suffix
    (r'^[eV]\.[vV]\.?$', 'COMP'),
    # (italian) company suffix
    (r'^[sS]\.[pP]\.[aA]\.?$', 'COMP'),
    # sweedish company suffix : ASA followed by a dot
    (r'^ASA.?$', 'COMP'),
    # czech company suffix: JetBrains s.r.o.
    (r'^s\.r\.o\.?$', 'COMP'),
    # (Laboratory) company suffix
    (r'^(Labs?|Laboratory|Laboratories|Laboratoire)\.?,?$', 'COMP'),
    # (dutch and belgian) company suffix
    (r'^[Bb]\.?[Vv]\.?|BVBA$', 'COMP'),
    # university
    (r'^\(?[Uu]niv(?:[.]|ersit(?:y|e|at?|ad?))\)?\.?$', 'UNI'),
    (r'^(UNIVERSITY|College)$', 'UNI'),
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
    (r'^(([Rr]e)?[Cc]oded|[Mm]odified|[Mm]ai?nt[ea]ine(d|r)|[Cc]reated|[Ww]ritten|[Dd]eveloped)$', 'AUTH2'),
    # author
    (r'@author', 'AUTH'),

    # of
    (r'^[Oo][Ff]$', 'OF'),

    # of
    (r'^[Dd][Eei]$', 'OF'),

    # in
    (r'^(in|en)$', 'IN'),

    # by
    (r'^by|BY|By$', 'BY'),

    # FIXMEL following is used NOWHERE
    (r'^following$', 'FOLLOW'),

    # conjunction: and
    (r'^([Aa]nd|&|[Uu]nd|ET|[Ee]t|at|and/or)$', 'CC'),

    # conjunction: or. Even though or is not conjunctive ....
    # (r'^or$', 'CC'),

    # ie. in things like "Copyright (c) 2012 John Li and others"
    # or et.al.
    (r'^[Oo]ther?s|et\.al[\.,]?$', 'OTH'),
    # in year ranges: dash, or 'to': "1990-1995", "1990/1995" or "1990 to 1995"
    (r'^([-/]|to)$', 'DASH'),

    # explicitly ignoring these words: FIXME: WHY?
    (r'^([Tt]his|THIS|[Pp]ermissions?|PERMISSIONS?|All)$', 'NN'),

    # Portions copyright .... are worth keeping
    (r'[Pp]ortions?|[Pp]arts?', 'PORTIONS'),

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
    (r'^([A-Z]\.){1,3}$', 'NNP'),

    # misc corner cases such LaTeX3 Project and other
    (r'^LaTeX3$', 'NNP'),
    (r'^Meridian\'93|Xiph.Org|iClick,?$', 'NNP'),

    # This_file_is_part_of_KDE
    (r'^[Tt]his_file_is_part_of_KDE$', 'NNP'),

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
    # all caps word 3 chars and more, enclosed in parens
    (r'^\([A-Z0-9]{2,}\)$', 'CAPS'),

    # proper noun: first CAP, including optional trailing comma
    # note: this also captures a bare comma as an NNP ... this is a bug
    (r'^(([A-Z][a-zA-Z0-9]+){,2},?)$', 'NNP'),

    # all CAPS word, all letters including an optional trailing single quote
    (r"^[A-Z]{2,}\'?$", 'CAPS'),

    # email eventually in parens or brackets with some trailing punct.
    (r'^[\<\(]?[a-zA-Z0-9]+[a-zA-Z0-9\+_\-\.\%]*(@|at)[a-zA-Z0-9][a-zA-Z0-9\+_\-\.\%]+\.[a-zA-Z]{2,5}?[\>\)\.\,]*$', 'EMAIL'),

    # URLS such as <(http://fedorahosted.org/lohit)>
    (r'[<\(]https?:.*[>\)]', 'URL'),
    # URLS such as ibm.com
    (r'\s?[a-z0-9A-Z\-\.\_]+\.(com|net|info|org|us|mil|io|edu|co\.[a-z][a-z]|eu|ch|biz)\s?\.?$', 'URL2'),
    # TODO: add more extensions?
    # URL wrapped in ()
    (r'[\(<]+\s?[a-z0-9A-Z\-\.\_]+\.(com|net|info|org|us|mil|io|edu|co\.[a-z][a-z]|eu|ch|biz)\s?[\.\)>]+$', 'URL'),
    (r'<?a?.(href)?.\(?[a-z0-9A-Z\-\.\_]+\.(com|net|info|org|us|mil|io|edu|co\.[a-z][a-z]|eu|ch|biz)[\.\)>]?$', 'URL'),
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

#######################################
# YEARS
#######################################

    YR-RANGE: {<YR>+ <CC>+ <YR>}        #20
    YR-RANGE: {<YR> <DASH>* <YR|CD>+}        #30
    YR-RANGE: {<CD>? <YR>+}        #40
    YR-RANGE: {<YR>+ }        #50
    YR-AND: {<CC>? <YR>+ <CC>+ <YR>}        #60
    YR-RANGE: {<YR-AND>+}        #70
    YR-RANGE: {<YR-RANGE>+ <DASH>?}        #72

#######################################
# NAMES and COMPANIES
#######################################

    NAME: {<NAME><NNP>} #75

    NAME: {<NN|NNP> <CC> <URL|URL2>} #80

    # the Tor Project, Inc.
    COMP: {<COMP> <COMP>+} #81

    # Laboratory for Computer Science Research Computing Facility
    COMPANY: {<COMP> <NN> <NNP> <NNP> <COMP> <NNP> <COMP>} #83
    COMPANY: {<COMP> <NN> <NNP> <NNP> <COMP>} #82

    # E. I. du Pont de Nemours and Company
    COMPANY: {<NNP> <NNP> <VAN> <NNP> <OF> <NNP> <CC> <COMP>}             #1010

    #  Robert A. van Engelen OR NetGroup, Politecnico di Torino (Italy)
    NAME: {<NNP>+ <VAN|OF> <NNP>+} #88

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
    COMPANY: {<NNP> <NNP> <CC> <NNP> <COMP> <NNP> <CAPS>}

    COMPANY: {<NNP> <CC> <NNP> <COMP> <NNP>?}        #200

    # Android Open Source Project, 3Dfx Interactive, Inc.
    COMPANY: {<NN>? <NN> <NNP>  <COMP>}        #205

    NAME: {<NNP> <NNP> <COMP> <CONTRIBUTORS> <URL|URL2>} #206

    # Thai Open Source Software Center Ltd
    # NNP  NN   NNP    NNP      COMP   COMP')
    COMPANY: {<NNP> <NN> <NNP> <NNP> <COMP>+} #207

    # was:     COMPANY: {<NNP|CAPS> <NNP|CAPS>? <NNP|CAPS>? <NNP|CAPS>? <NNP|CAPS>? <NNP|CAPS>? <COMP> <COMP>?}        #210
    COMPANY: {<NNP|CAPS>+ <COMP>+}        #210
    COMPANY: {<UNI|NNP> <VAN|OF> <NNP>+ <UNI>?}        #220
    COMPANY: {<NNP>+ <UNI>}        #230
    COMPANY: {<UNI> <OF> <NN|NNP>}        #240
    COMPANY: {<COMPANY> <CC> <COMPANY>}        #250

    # University of Southern California, Information Sciences Institute (ISI)
    COMPANY: {<COMPANY> <COMPANY> <CAPS>} #251

    # GNOME i18n Project for Vietnamese
    COMPANY: {<CAPS> <NN> <COMP> <NN> <NNP>} #253

    COMPANY: {<CAPS> <NN> <COMP>}        #255

    # Project contributors
    COMPANY: {<COMP> <CONTRIBUTORS>}   #256

    COMPANY: {<COMP>+}        #260

    # Nokia Corporation and/or its subsidiary(-ies)
    COMPANY: {<COMPANY> <CC> <NN> <COMPANY>}   #265

    COMPANY: {<COMPANY> <CC> <NNP>+}        #270
    # AIRVENT SAM s.p.a - RIMINI(ITALY)
    COMPANY: {<COMPANY> <DASH> <NNP|NN> <EMAIL>?}        #290

    # Typical names
    #John Robert LoVerso
    NAME: {<NNP> <NNP> <MIXEDCAP>}        #340

    # Kaleb S. KEITHLEY
    NAME: {<NNP> <NNP> <CAPS>} #345

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

    NAME: {<NAME> <UNI>}        #483

    # Kungliga Tekniska Hogskolan (Royal Institute of Technology, Stockholm, Sweden)
    COMPANY: { <COMPANY> <OF> <COMPANY> <NAME> } #529

    # Instituto Nokia de Tecnologia
    COMPANY: { <COMPANY> <NNP> <OF> <COMPANY>} #    5391

    # Laboratoire MASI - Institut Blaise Pascal
    COMPANY: { <COMPANY> <CAPS> <DASH> <COMPANY> <NAME>} #5292

    # Nara Institute of Science and Technology.
    COMPANY: { <COMPANY> <OF> <NNP> <CC> <COMPANY> } #5293

    NAME2: {<NAME> <EMAIL>}        #530

    NAME3: {<YR-RANGE> <NAME2|COMPANY>+}        #535
    NAME3: {<YR-RANGE> <NAME2|COMPANY>+ <CC> <YR-RANGE>}        #540
    NAME: {<NAME|NAME2>+ <OF> <NNP> <OF> <NN>? <COMPANY>}        #550
    NAME: {<NAME|NAME2>+ <CC|OF>? <NAME|NAME2|COMPANY>}        #560

    # FIXME HIGHLY LIKELY SCREWED LAST MOD
    # strip Software from Copyright (c) Ian Darwin 1995. Software
    NAME3: {<NAME>+ <YR-RANGE>}        #5611

    NAME3: {<YR-RANGE> <NNP>+ <CAPS>?} #5612

    #Academy of Motion Picture Arts and Sciences
    NAME: { <NAME> <CC> <NNP>} # 561

    # Adam Weinberger and the GNOME Foundation
    NAME: {<CC> <NN> <COMPANY>} # 565

    # (c) 1991-1992, Thomas G. Lane , Part of the Independent JPEG Group's
    NAME: {<PORTIONS> <OF> <NN> <NAME>+} #566

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
    NAME: { <BY> <NNP> <URL>}        #741

    # Philippe http//nexb.com joe@nexb.com
    NAME: { <NNP> <URL> <EMAIL>}        #742

    # Companies
    COMPANY: {<NAME|NAME2|NAME3|NNP>+ <OF> <NN>? <COMPANY|COMP> <NNP>?}        #770
    COMPANY: {<NNP> <COMP|COMPANY> <COMP|COMPANY>}        #780
    COMPANY: {<NN>? <COMPANY|NAME|NAME2> <CC> <COMPANY|NAME|NAME2>}        #790
    COMPANY: {<COMP|COMPANY|NNP> <NN> <COMPANY|COMPANY> <NNP>+}        #800

    # by the Institute of Electrical and Electronics Engineers, Inc.
    COMPANY: {<BY> <NN> <COMPANY> <OF> <NNP> <CC> <COMPANY>}
    COMPANY: {<COMPANY> <CC> <AUTH|CONTRIBUTORS|AUTHS>}        #810
    COMPANY: {<NN> <COMP|COMPANY>+}        #820
    COMPANY: {<URL|URL2>}        #830

    COMPANY: {<COMPANY> <COMP|COMPANY>}        #840

    # University Corporation for Advanced Internet Development, Inc.
    COMPANY: {<UNI> <COMPANY>}        #845

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

    # (The) Android Open Source Project
    COMPANY: {<NN><NN><NN>? <COMPANY>}        #1250

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

    # Copyright (c) 1998-2000 University College London
    COMPANY: {<UNI> <UNI> <NNP>}

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
    COMPANY: {<NN> <COMPANY> <CC> <NN> <COMPANY>}      #1414

    # by the Massachusetts Institute of Technology
    COMPANY: { <BY> <COMPANY> <OF> <COMPANY>}  #1415

    # Computer Systems and Communication Lab, Institute of Information Science, Academia Sinica.
    COMPANY: { <NNP> <COMPANY> <OF> <COMPANY> <NNP>} #1416

    # Copyright 2007-2010 the original author or authors.
    # Copyright (c) 2007-2010 the original author or authors.
    NAME: {<NN> <JUNK> <AUTH|CONTRIBUTORS|AUTHS> <NN> <AUTH|CONTRIBUTORS|AUTHS>}        #1960


#######################################
# VARIOUS FORMS OF COPYRIGHT
#######################################

    COPYRIGHT: {<COPY> <NAME> <COPY> <YR-RANGE>}        #1510

    COPYRIGHT: {<COPY>+ <BY>? <COMPANY|NAME*|YR-RANGE>* <BY>? <EMAIL>+}        #1530

    COPYRIGHT: {<COPY>+ <NAME|NAME2|NAME3> <CAPS> <YR-RANGE>}        #1550

    #Copyright . 2008 Mycom Pany, inc.
    COPYRIGHT: {<COPY>+ <NN> <NAME3>}        #1560

    COPYRIGHT: {<COPY> <COPY>? <NAME|NAME2|NAME3>+ <YR-RANGE>*}        #1570

    COPYRIGHT: {<COPY>+ <CAPS|NNP>+ <CC> <NN> <COPY> <YR-RANGE>?}        #1590

    COPYRIGHT: {<COPY>+ <BY>? <COMPANY|NAME*|NAME2*>+ <YR-RANGE>*}        #1610

    COPYRIGHT: {<NNP>? <COPY>+ (<YR-RANGE>+ <BY>? <NN>? <COMPANY|NAME|NAME2>+ <EMAIL>?)+}        #1630

    COPYRIGHT: {<COPY>+ <NN> <NAME> <YR-RANGE>}        #1650

    COPYRIGHT: {<COPY>+ <BY> <NAME|NAME2|NAME3>+}        #1670

    COPYRIGHT: {<COPY> <COPY> <COMP>+}        #1690

    COPYRIGHT: {<COPY> <COPY> <NN>+ <COMPANY|NAME|NAME2>+}        #1710

    COPYRIGHT: {<COPY>+ <NN> <NN>? <COMP> <YR-RANGE>?}        #1730

    COPYRIGHT: {<COPY>+ <NN> <NN>? <COMP> <YR-RANGE>?}        #1750
    COPYRIGHT: {<COPY> <NN> <NN>? <COMPANY> <YR-RANGE>?}        #1760

    COPYRIGHT: {<COPY>+ <YR-RANGE|NNP> <CAPS|BY>? <NNP|YR-RANGE|NAME>+}        #1780

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
    COPYRIGHT2: {<COPY>+ <YR-RANGE> <DASH> <NN>}        #1920

    #(c) 2017 The Chromium Authors
    COPYRIGHT2: {<COPY>+ <YR-RANGE> <NN> <NNP> <NN>}        #1990

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

    COPYRIGHT2: {<COPY>+ <NN> <YR-RANGE> <BY> <NAME>}        #2140

    COPYRIGHT2: {<COPY>+ <YR-RANGE> <DASH> <BY>? <NAME2|NAME>}        #2160

    COPYRIGHT2: {<COPY>+ <YR-RANGE> <NNP> <NAME>}        #2180

    # Copyright (c) 2012-2016, Project contributors
    COPYRIGHT2: {<COPY>+ <YR-RANGE> <COMP> <AUTHS|CONTRIBUTORS>}        #2210

    COPYRIGHT2: {<COPY>+ <YR-RANGE> <COMP>}        #2230
    COPYRIGHT2: {<COPY> <COPY> <YR-RANGE>+ <CAPS>? <MIXEDCAP>}        #2240

    COPYRIGHT2: {<NAME> <COPY> <YR-RANGE>}        #2260

    # Copyright 2008 TJ <linux@tjworld.net>
    COPYRIGHT2: {<COPY> <YR-RANGE> <CAPS> <EMAIL>} #2270

    # (c) Copyright 1985-1999 SOME TECHNOLOGY SYSTEMS
    COPYRIGHT2: {<COPY> <COPY> <YR-RANGE> <CAPS> <CAPS> <CAPS>? <CAPS>?} #2271

    # Daisy (c) 1998
    NAME4: {<NNP> <COPY>} #2272
    COPYRIGHT2: {<NAME4> <YR-RANGE>}  #2273

    # Scilab (c)INRIA-ENPC.
    COPYRIGHT: {<NAME4> <NNP>} #2274

    # Copyright 1994-2007 (c) RealNetworks, Inc.
    COPYRIGHT: {<COPY>+ <YR-RANGE> <COPYRIGHT>} #2274

    # Copyright (c) 2017 Contributors et.al.
    COPYRIGHT: { <COPY>  <COPY>  <YR-RANGE>  <CONTRIBUTORS>  <OTH> } #2276

    COPYRIGHT2: {<COPY>+ <NN|CAPS>? <YR-RANGE>+ <PN>*}        #2280

    COPYRIGHT2: {<COPY>+ <NN|CAPS>? <YR-RANGE>+ <NN|CAPS>* <COMPANY>?}        #2300

    COPYRIGHT2: {<COPY>+ <NN|CAPS>? <YR-RANGE>+ <NN|CAPS>* <DASH> <COMPANY>}        #2320

    COPYRIGHT2: {<NNP|NAME|COMPANY> <COPYRIGHT2>}        #2340

    COPYRIGHT: {<COPYRIGHT> <NN> <COMPANY>}        #2360

    COPYRIGHT: {<COPY>+ <BY>? <NN> <COMPANY>}        #2380

    COPYRIGHT: {<COMPANY> <NN> <NAME> <COPYRIGHT2>}        #2400
    COPYRIGHT: {<COPYRIGHT2> <COMP> <COMPANY>}        #2410
    COPYRIGHT: {<COMPANY> <NN> <COPYRIGHT2>}        #2420
    COPYRIGHT: {<COPYRIGHT2> <NNP> <CC> <COMPANY>}        #2430

    COPYRIGHT: {<COPYRIGHT2> <NAME|NAME2|NAME3>+}        #2860

    # Copyright (c) 1996 Adrian Rodriguez (adrian@franklins-tower.rutgers.edu) Laboratory for Computer Science Research Computing Facility
    COPYRIGHT: {<COPYRIGHT> <NAME>} #2400

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

    COPYRIGHT: {<COPYRIGHT> <NAME|NAME3>+}        #2001

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
    COPYRIGHT: {<COPY> <PN>?  <YR-RANGE> <BY> <NN> <NAME>}   #2007

    # COPYRIGHT (c) 2006 - 2009 DIONYSOS
    COPYRIGHT: {<COPYRIGHT2> <CAPS>} # 2008
    # Copyright (C) 2000 See Beyond Communications Corporation
    COPYRIGHT2: {<COPYRIGHT2> <JUNK> <COMPANY>} # 2010

    # copyright C 1988 by the Institute of Electrical and Electronics Engineers, Inc.
    COPYRIGHT: {<COPY> <PN> <YR-RANGE> <COMPANY>}

    COPYRIGHT2: {<NAME4> <COPYRIGHT2>}  #2274

    # (C) COPYRIGHT 2004 UNIVERSITY OF CHICAGO
    COPYRIGHT: {<COPYRIGHT2> <UNI> <OF> <CAPS>} #2276

    #Copyright or Copr. CNRS
    NAME5: {<CAPS>+}        #2530
    #Copyright or Copr. CNRS
    COPYRIGHT: {<COPY> <NN> <COPY> <COPYRIGHT|NAME5>}        #2560
    COPYRIGHT: {<COPYRIGHT2> <BY> <NAME5>} #2561
    # Copyright (c) 2004, The Codehaus
    COPYRIGHT: {<COPYRIGHT2> <NN> <NNP>} #2562

# Authors
    # Created by XYZ
    AUTH: {<AUTH2>+ <BY>}        #2645
    AUTHOR: {<AUTH|CONTRIBUTORS|AUTHS>+ <NN>? <COMPANY|NAME|YR-RANGE>* <BY>? <EMAIL>+}        #2650
    AUTHOR: {<AUTH|CONTRIBUTORS|AUTHS>+ <NN>? <COMPANY|NAME|NAME2|NAME3>+ <YR-RANGE>*}        #2660
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
    # this catches trailing slashes in URL for consistency
    c = c.strip('/ ')
    c = fix_trailing_space_dot(c)
    c = strip_all_unbalanced_parens(c)
    # from .net assemblies
    c = c.replace('AssemblyCopyright', 'Copyright')
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


PREFIXES = frozenset([
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
    'recoded',
    'coded',
    'modified',
    'maintained'
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
    'or',
    '<p>',
])


def _refine_names(s, prefixes=PREFIXES):
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

HOLDERS_PREFIXES = frozenset(set.union(
    set(PREFIXES),
    set([
        'ou',
        'portions',
        'portion',
        'notice',
        'holders',
        'holder',
        'property',
        'parts',
        'part',
        'at',
        'cppyright',
        'assemblycopyright',
        'c',
        'works',
        'present',
        'at',
    ])
))

HOLDERS_SUFFIXES = frozenset([
    'http',
    'and',
    'email',
    'licensing@',
    '(minizip)',
    'website',
])


def refine_holder(s, prefixes=HOLDERS_PREFIXES, junk_holders=JUNK_HOLDERS,
                  suffixes=HOLDERS_SUFFIXES):
    """
    Refine a detected holder.
    FIXME: the grammar should not allow this to happen.
    """
    refined = _refine_names(s, prefixes)
    refined = strip_suffixes(refined, suffixes)
    refined = refined.strip()
    if refined and refined.lower() not in junk_holders:
        return refined


JUNK_AUTHORS = frozenset([
    # in GNU licenses
    'james hacker.',
    'james random hacker.',
])

AUTHORS_PREFIXES = frozenset(set.union(
    set(PREFIXES),
    set(['contributor', 'contributors', 'contributor(s)',
        'author', 'authors', 'author(s)', 'authored', 'created'
        ])
))


def refine_author(s, prefixes=AUTHORS_PREFIXES, junk_authors=JUNK_AUTHORS):
    """
    Refine a detected author.
    FIXME: the grammar should not allow this to happen.
    """
    # FIXME: we could consider to split comma separated lists such as
    # gthomas, sorin@netappi.com, andrew.lunn@ascom.che.g.
    refined = _refine_names(s, prefixes)
    refined = refined.strip()
    if refined and refined.lower() not in junk_authors:
        return refined


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


def strip_suffixes(s, suffixes=()):
    """
    Return the `s` string with any of the string in the `suffixes` set
    striped. Normalize and strip spacing.
    """
    s = s.split()
    while s and s[-1].lower() in suffixes:
        s = s[:-1]
    s = u' '.join(s)
    return s


def refine_date(c):
    """
    Refine a detected date or date range.
    FIXME: the grammar should not allow this to happen.
    """
    return strip_some_punct(c)


# Set of statements that get detected and are junk/false positive
# note: this must be lowercase and be kept to a minimum.
# A junk copyright cannot be resolved otherwise by parsing with a grammar.
# It would be best not to have to resort to this, but this is practical.
JUNK_COPYRIGHTS = frozenset([
    '(c)',
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
    'copyright holder and contributor',
    'copyright-holder and its contributors',
    'copyright holders and contributors.',

    'copyrighted material, only this license, or another one contracted with the authors',
    'copyright notices, authorship',
    'copyright holder means the original author(s)',
    "copyright notice. timevar.def's author",
    'copyright copyright and',
    "copyright holder or simply that it is author-maintained'.",
    "copyright holder or simply that is author-maintained'.",
    '(c) if you bring a patent claim against any contributor',
    'copyright-check writable-files m4-check author_mark_check',
    "copyright of uc berkeley's berkeley software distribution",
    '(c) any recipient',
    '(c) each recipient',
    'copyright in section',
    'u.s. copyright act',
    # from a WROX license text
    'copyright john wiley & sons, inc. year',
    'copyright holders and contributing',
    '(c) individual use.',
    'copyright, license, and disclaimer',
    '(c) forums',
    # from the rare LATEX licenses
    'copyright 2005 m. y. name',
    'copyright 2003 m. y. name',
    'copyright 2001 m. y. name',
    'copyright. united states',
    '(c) source code',
    'copyright, designs and patents',
    '(c) software activation.',
    '(c) cockroach enterprise edition',
    'attn copyright agent',
    'code copyright grant',
    # seen in a weird Adobe license
    'copyright redistributions',
    'copyright neither',
    'copyright including, but not limited',
    'copyright not limited',

])

# simple tokenization: spaces and some punctuation
splitter = re.compile('[\\t =;]+').split


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
    def as_str(cls, node, ignores=frozenset()):
        """
        Return a parse tree node as a space-normalized string.
        Optionally filters node labels provided in the ignores set.
        """
        if ignores:
            leaves = (leaf_text for leaf_text, leaf_label in node.leaves()
                                            if leaf_label not in ignores)
        else:
            leaves = (leaf_text for leaf_text, leaf_label in node.leaves())

        node_string = ' '.join(leaves)
        return u' '.join(node_string.split())

    def detect(self, numbered_lines,
                copyrights=True, holders=True, authors=True, include_years=True,
                _junk=JUNK_COPYRIGHTS):
        """
        Yield tuples of (detection type, detected value, start_line, end_line)
        where the type is one of copyrights, authors, holders. Use an iterable
        of `numbered_lines` tuples of (line number,  line text).
        If `include_years` is False, the copyright statement do not have years
        or year range information.
        """
        from nltk.tree import Tree
        numbered_lines = list(numbered_lines)
        start_line = numbered_lines[0][0]
        end_line = numbered_lines[-1][0]
        tokens = self.get_tokens(numbered_lines)

        if not tokens:
            return

        # first, POS tag each token using token regexes
        tagged_text = self.tagger.tag(tokens)
        if TRACE: logger_debug('CopyrightDetector:tagged_text: ' + str(tagged_text))

        # then build a parse tree based on tagged tokens
        tree = self.chunker.parse(tagged_text)
        if TRACE: logger_debug('CopyrightDetector:parse tree: ' + str(tree))

        CopyrightDetector_as_str = CopyrightDetector.as_str

        if include_years:
            year_labels = ()
        else:
            year_labels = frozenset(['YR-RANGE', 'YR', 'YR-AND', 'YR-PLUS', ])

        non_holder_labels = frozenset([
            'COPY',
            'YR-RANGE', 'YR-AND', 'YR', 'YR-PLUS',
            'EMAIL', 'URL',
            'HOLDER', 'AUTHOR',
            ])

        # then walk the parse tree, collecting copyrights, years and authors
        for tree_node in tree:
            if not isinstance(tree_node, Tree):
                continue

            node_text = CopyrightDetector_as_str(tree_node, ignores=year_labels)
            tree_node_label = tree_node.label()

            if 'COPYRIGHT' in tree_node_label:
                if TRACE: logger_debug('CopyrightDetector:Copyright tree node: ' + str(tree_node))
                if node_text and node_text.strip():
                    refined = refine_copyright(node_text)
                    # checking for junk is a last resort
                    if refined.lower() not in _junk:

                        if copyrights:
                            if TRACE: logger_debug('CopyrightDetector: detected copyrights:', refined, start_line, end_line)
                            yield 'copyrights', refined, start_line, end_line

                        if holders:
                            holder = CopyrightDetector_as_str(tree_node, ignores=non_holder_labels)
                            refined_holder = refine_holder(holder)
                            if refined_holder and refined_holder.strip():
                                yield 'holders', refined_holder, start_line, end_line
                                if TRACE: logger_debug('CopyrightDetector: detected holders:', refined_holder, start_line, end_line)

            elif authors and tree_node_label == 'AUTHOR':
                refined_auth = refine_author(node_text)
                if refined_auth:
                    if TRACE: logger_debug('CopyrightDetector: detected authors:', refined_auth, start_line, end_line)
                    yield 'authors', refined_auth, start_line, end_line

    def get_tokens(self, numbered_lines):
        """
        Return an iterable of tokens from lines of text.
        """
        tokens = []
        tokens_append = tokens.append

        for _line_number, line in numbered_lines:
            line = prepare_text_line(line)
            for tok in splitter(line):
                # strip trailing single quotes and ignore empties
                tok = tok.strip("' ")
                # strip trailing colons: why?
                tok = tok.rstrip(':').strip()
                # strip leading @: : why?
                tok = tok.lstrip('@').strip()
                if tok and tok not in (':',):
                    tokens_append(tok)
        if TRACE: logger_debug('CopyrightDetector:tokens: ' + repr(tokens))
        return tokens


remove_non_chars = re.compile(r'[^a-z0-9]').sub


def prep_line(line):
    """
    Return a tuple of (line, line with only chars) from a line of text prepared
    for candidate and other checks or None.
    """
    line = prepare_text_line(line.lower())
    chars_only = remove_non_chars('', line)
    return line, chars_only.strip()


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
        # if TRACE: logger_debug('is_candidate: NOT year in line:\n%(line)r' % locals())
        pass

    for marker in copyrights_hint.statement_markers:
        if marker in prepped_line:
            # if TRACE: logger_debug('is_candidate: %(marker)r in line:\n%(line)r' % locals())
            return True


def is_inside_statement(chars_only_line):
    """
    Return True if a line ends with some strings that indicate we are still
    inside a statement.
    """
    markers = ('copyright', 'copyrights', 'copyrightby',) + copyrights_hint.all_years
    return chars_only_line and chars_only_line.endswith(markers)


def is_end_of_statement(chars_only_line):
    """
    Return True if a line ends with some strings that indicate we are at the end
    of a statement.
    """
    return chars_only_line and chars_only_line.endswith(('rightreserved', 'rightsreserved'))


def candidate_lines(numbered_lines):
    """
    Yield lists of candidate lines where each list element is a tuple of
    (line number,  line text) given an iterable of numbered_lines as tuples of
    (line number,  line text) .

    A candidate line is a line of text that may contain copyright statements.
    A few lines before and after a candidate line are also included.
    """
    candidates = deque()
    candidates_append = candidates.append
    candidates_clear = candidates.clear

    # used as a state and line counter
    in_copyright = 0

    # the previous line (chars only)
    previous_chars = None
    for numbered_line in numbered_lines:
        if TRACE: logger_debug('# candidate_lines: evaluating line:' + repr(numbered_line))
        line_number, line = numbered_line

        # FIXME: we shoud, get the prepared text from here and return effectively pre-preped lines
        prepped, chars_only = prep_line(line)

        if is_end_of_statement(chars_only):
            candidates_append(numbered_line)

            if TRACE:
                cands = list(candidates)
                logger_debug('   candidate_lines: is EOS: yielding candidates\n    %(cands)r\n\n' % locals())

            yield list(candidates)
            candidates_clear()
            in_copyright = 0
            previous_chars = None
            continue
        elif is_candidate(prepped):
            # the state is now "in copyright"
            in_copyright = 2
            candidates_append(numbered_line)
            previous_chars = chars_only
            if TRACE: logger_debug('   candidate_lines: line is candidate')
        elif in_copyright > 0:
            if ((not chars_only)
            and (not previous_chars.endswith(('copyright', 'copyrights', 'copyrightsby', 'copyrightby',)))):
                # completely empty or only made of punctuations
                if TRACE:
                    cands = list(candidates)
                    logger_debug('   candidate_lines: empty: yielding candidates\n    %(cands)r\n\n' % locals())

                yield list(candidates)
                candidates_clear()
                in_copyright = 0
                previous_chars = None
            else:

                candidates_append(numbered_line)
                # and decrement our state
                in_copyright -= 1
                if TRACE: logger_debug('   candidate_lines: line is in copyright')
        elif candidates:
            if TRACE:
                cands = list(candidates)
                logger_debug('    candidate_lines: not in COP: yielding candidates\n    %(cands)r\n\n' % locals())
            yield list(candidates)
            candidates_clear()
            in_copyright = 0
            previous_chars = None

    # finally
    if candidates:
        if TRACE:
            cands = list(candidates)
            logger_debug('candidate_lines: finally yielding candidates\n    %(cands)r\n\n' % locals())

        yield list(candidates)


# this catches tags but not does not remove the text inside tags
remove_tags = re.compile(
        r'<'
        r'[(--)\?\!\%\/]?'
        r'[a-gi-vx-zA-GI-VX-Z][a-zA-Z#\"\=\s\.\;\:\%\&?!,\+\*\-_\/]*'
        r'[a-zA-Z0-9#\"\=\s\.\;\:\%\&?!,\+\*\-_\/]+'
        r'\/?>',
        re.MULTILINE | re.UNICODE
    ).sub


def strip_markup(text):
    """
    Strip markup tags from text.
    """
    text = remove_tags(' ', text)
    # Debian copyright file markup
    return text.replace('</s>', '').replace('<s>', '').replace('<s/>', '')


# this catches the common C-style percent string formatting codes
remove_printf_format_codes = re.compile(r' [\#\%][a-zA-Z] ').sub

remove_punctuation = re.compile(r'[\*#"%\[\]\{\}`]+').sub

remove_ascii_decorations = re.compile(r'[-_=!\\*]{2,}|/{3,}').sub

fold_consecutive_quotes = re.compile(r"\'{2,}").sub

# less common rem comment line prefix in dos
# less common dnl comment line prefix in autotools am/in
remove_comment_markers = re.compile(r'^(rem|\@rem|dnl)\s+').sub

# common comment line prefix in man pages
remove_man_comment_markers = re.compile(r'.\\"').sub


def prepare_text_line(line):
    """
    Prepare a unicode `line` of text for copyright detection.
    """
    # remove some junk in man pages: \(co
    line = line.replace(r'\\ co', ' ')
    line = line.replace(r'\ co', ' ')
    line = line.replace(r'(co ', ' ')

    line = remove_printf_format_codes(' ', line)

    # un common comment line prefixes
    line = remove_comment_markers(' ', line)
    line = remove_man_comment_markers(' ', line)
    # C and C++ style markers
    line = line.replace('^//', ' ')
    line = line.replace('/*', ' ').replace('*/', ' ')

    # un common pipe chars in some ascii art
    line = line.replace('|', ' ')

    # normalize copyright signs and spacing around them
    line = line.replace('"Copyright', '" Copyright')
    line = line.replace('( C)', ' (c) ')
    line = line.replace('(C)', ' (c) ')
    line = line.replace('(c)', ' (c) ')
    # the case of \251 is tested by 'weirdencoding.h'
    line = line.replace(u'©', u' (c) ')
    line = line.replace(u'\251', u' (c) ')
    line = line.replace('&copy;', ' (c) ')
    line = line.replace('&#169;', ' (c) ')
    line = line.replace('&#xa9;', ' (c) ')
    line = line.replace('&#XA9;', ' (c) ')
    line = line.replace(u'\xa9', ' (c) ')
    line = line.replace(u'\XA9', ' (c) ')
    # FIXME: what is \xc2???
    line = line.replace(u'\xc2', '')

    # not really a dash
    # # MIT
    line = line.replace(u'–', '-')

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
    # keep only one quote
    line = fold_consecutive_quotes("'", line)

    # treat some escaped literal CR, LF, tabs, \00 as new lines
    # such as in code literals: a="\\n some text"
    line = line.replace('\\t', ' ')
    line = line.replace('\\n', ' ')
    line = line.replace('\\r', ' ')
    line = line.replace('\\0', ' ')

    # TODO: why backslashes?
    line = line.replace('\\', ' ')

    # replace ('
    line = line.replace(r'("', ' ')
    # some trailing garbage ')
    line = line.replace("')", ' ')
    line = line.replace("],", ' ')

    # note that we do not replace the debian tag by a space:  we remove it
    line = strip_markup(line)

    line = remove_punctuation(' ', line)

    # normalize spaces around commas
    line = line.replace(' , ', ', ')

    # remove ASCII "line decorations"
    # such as in --- or === or !!! or *****
    line = remove_ascii_decorations(' ', line)

    # in apache'>Copyright replace ">" by "> "
    line = line.replace('>', '> ')
    line = line.replace('<', ' <')

    # normalize to ascii text
    line = toascii(line, translit=True)

    # normalize to use only LF as line endings so we can split correctly
    # and keep line endings
    line = unixlinesep(line)

    # strip verbatim back slash and comment signs again at both ends of a line
    # FIXME: this is done at the start of this function already
    line = line.strip('\\/*#%;')

    # normalize spaces
    line = ' '.join(line.split())

    return line
