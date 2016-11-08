# -*- coding: utf-8 -*-
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


years = u'''
01
02
03
04
05
06
07
08
09
10
11
12
13
14
15
16
17
18
19
20
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
1960
1961
1962
1963
1964
1965
1966
1967
1968
1969
1970
1971
1972
1973
1974
1975
1976
1977
1978
1979
1980
1981
1982
1983
1984
1985
1986
1987
1988
1989
1990
1991
1992
1993
1994
1995
1996
1997
1998
1999
2000
2001
2002
2003
2004
2005
2006
2007
2008
2009
2010
2011
2012
2013
2014
2015
2016
2017
2018
2019
'''.split()


statement_markers = u'''
©
cop
169
A9
251
\251
(c)
right
reserv
left
auth
by
devel
'''.split() + years


# (various copyright/copyleft signs tm, r etc) http://en.wikipedia.org/wiki/Copyright_symbol

# ™ U+2122 TRADE MARK SIGN, decimal: 8482, HTML: &#8482;, UTF-8: 0xE2 0x84 0xA2, block: Letterlike Symbols, decomposition: <super> U+0054 U+004D
# © U+00A9 COPYRIGHT SIGN, decimal: 169, HTML: &#169;, UTF-8: 0xC2 0xA9, block: Latin-1 Supplement
# �  U+00A9 (169)
#      �     U+00AE (174)
#     �     U+2122 (8482)


'''HTML Entity (decimal)     &#169;
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


end_of_statement = '''
rights reserve
right reserve
'''.split()


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
reserve
right
sa
team
tech
tm
univ
upstream
write
'''.split()
