# Copyright (c) 2014-2019 Security Innovation, Inc
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# * Neither the name of the {organization} nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""
A regular expression to parse a PGP signed message in its parts.
"""

import re

# copied from
# https://github.com/SecurityInnovation/PGPy/blob/e2893da8b2f5ce0694257caddd8d852aece546ff/pgpy/types.py#L57
# the re.VERBOSE flag allows for:
#  - whitespace is ignored except when in a character class or escaped
#  - anything after a '#' that is not escaped or in a character class is ignored, allowing for comments
pgp_signed = re.compile(r"""# This capture group is optional because it will only be present in signed cleartext messages
                     (^-{5}BEGIN\ PGP\ SIGNED\ MESSAGE-{5}(?:\r?\n)
                      (Hash:\ (?P<hashes>[A-Za-z0-9\-,]+)(?:\r?\n){2})?
                      (?P<cleartext>(.*\r?\n)*(.*(?=\r?\n-{5})))(?:\r?\n)
                     )?
                     # armor header line; capture the variable part of the magic text
                     ^-{5}BEGIN\ PGP\ (?P<magic>[A-Z0-9 ,]+)-{5}(?:\r?\n)
                     # try to capture all the headers into one capture group
                     # if this doesn't match, m['headers'] will be None
                     (?P<headers>(^.+:\ .+(?:\r?\n))+)?(?:\r?\n)?
                     # capture all lines of the body, up to 76 characters long,
                     # including the newline, and the pad character(s)
                     (?P<body>([A-Za-z0-9+/]{1,76}={,2}(?:\r?\n))+)
                     # capture the armored CRC24 value
                     ^=(?P<crc>[A-Za-z0-9+/]{4})(?:\r?\n)
                     # finally, capture the armor tail line, which must match the armor header line
                     ^-{5}END\ PGP\ (?P=magic)-{5}(?:\r?\n)?
                     """, flags=re.MULTILINE | re.VERBOSE).search


def unsign(text):
    """
    Return `text` stripped from a PGP signature if any.
    """
    if not text:
        return text
    signed =  pgp_signed(text)
    if not signed:
        return text
    unsigned = signed.groupdict().get('cleartext')
    return unsigned