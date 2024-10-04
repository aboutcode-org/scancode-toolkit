# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from datetime import datetime
import re

# A regex to match a string that may contain a copyright year.
# This is a year between 1960 and today prefixed and suffixed with
# either a white-space or some punctuation.
from cluecode.normalizer import normalize_copyright_symbols

def detect_copyrights(file_path):
    # Read the content of the file
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Normalize the text before processing it
    normalized_text = normalize_copyright_symbols(text)

    # Save the normalized content back to the file (optional)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(normalized_text)

    return normalized_text

# Specify the path to your document directly here
file_path = "./copyright.py"

# Call the function and print the result
normalized_content = detect_copyrights(file_path)
print(normalized_content)


all_years = tuple(str(year) for year in range(1960, datetime.today().year))
years = r'[\(\.,\-\)\s]+(' + '|'.join(all_years) + r')([\(\.,\-\)\s]+|$)'

years = re.compile(years).findall

# Various copyright/copyleft signs tm, r etc: http://en.wikipedia.org/wiki/Copyright_symbol
# © U+00A9 COPYRIGHT SIGN
#  decimal: 169
#  HTML: &#169;
#  UTF-8: 0xC2 0xA9
#  block: Latin-1 Supplement
#  U+00A9 (169)
# visually similar: Ⓒ ⓒ
# 🄯 COPYLEFT SYMBOL
#  U+1F12F
# ℗ Sound recording copyright
#  HTML &#8471;
#  U+2117
# ® registered trademark
#  U+00AE (174)
# 🅪 Marque de commerce
#  U+1F16A
# ™ U+2122 TRADE MARK SIGN
#  decimal: 8482
#  HTML: &#8482;
#  UTF-8: 0xE2 0x84 0xA2
#  block: Letterlike Symbols
#  decomposition: <super> U+0054 U+004D
# Ⓜ  mask work

statement_markers = (
    '©',
    '(c)',
    '&#169',
    '&#xa9',
    '169',
    'xa9',
    'u00a9',
    '00a9',
    '\251',
    # have copyright but also (c)opyright and ©opyright
    'opyr',
    # have copyright but also (c)opyleft
    'opyl',
    'copr',
    'right',
    'reserv',
    'auth',
    'filecontributor',
    'devel',
    '<s>',
    '</s>',
    '<s/>',
    'by ',  # note the trailing space
)

'''
HTML Entity (decimal)     &#169;
HTML Entity (hex)     &#xa9;
HTML Entity (named)     &copy;
How to type in Microsoft Windows     Alt +00A9
Alt 0169
UTF-8 (hex)     0xC2 0xA9 (c2a9)
UTF-8 (binary)     11000010:10101001
UTF-16 (hex)     0x00A9 (00a9)
UTF-16 (decimal)     169
UTF-32 (hex)     0x000000A9 (00a9)
UTF-32 (decimal)     169
C/C++/Java source code     "\u00A9"
Python source code     u"\u00A9"
'''

end_of_statement = (
    'rights reserve',
    'right reserve',
    'rights reserved',
    'rights reserved.',
    'right reserved',
    'right reserved.',
    # in German
    'rechte vorbehalten',
    'rechte vorbehalten.'
    # in French
    'droits réservés',
    'droits réservés.'
    'droits reserves',
    'droits reserves.'
)

# others stuffs
'''
&reg;
&trade;
trad
regi
hawlfraint
AB
AG
AS
auth
co
code
commit
common
comp
contrib
copyl
copyr
Copr
corp
devel
found
GB
gmbh
grou
holder
inc
inria
Lab
left
llc
ltd
llp
maint
micro
modi
compan
forum
oth
pack
perm
proj
research
sa
team
tech
tm
univ
upstream
write
'''.split()
