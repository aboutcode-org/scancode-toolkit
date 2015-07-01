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

import hashlib

from commoncode import codec
from commoncode import filetype


"""
Hashes and checksums.

Low level hash functions using standard crypto hashes used to construct hashes
of various lengths. Hashes that are smaller than 128 bits are based on a
truncated md5. Other length use SHA hashes.

Checksums are operating on files.
"""

def hash_mod(bitsize, hmodule):
    """
    Return a hashing class returning hashes with a `bitsize` bit length. The
    interface of this class is similar to the hash module API.
    """
    class hash_cls(object):
        def __init__(self, msg=None):
            self.digest_size = size / 8
            if msg:
                self.hd = module(msg).digest()[-(self.digest_size):]
            else:
                self.hd = None

        def digest(self):
            return self.hd

        def hexdigest(self):
            if self.hd:
                return self.hd.encode('hex')

        def b64digest(self):
            if self.hd:
                return codec.urlsafe_b64encode(self.hd)

        def intdigest(self):
            if self.hd:
                return codec.bin_to_num(self.hd)

    size = bitsize
    module = hmodule
    return hash_cls

# Base hashers for each bit size
bitsizes = {
    # md5-based
    16: hashlib.md5, 24: hashlib.md5, 32: hashlib.md5, 48: hashlib.md5,
    64: hashlib.md5, 96: hashlib.md5, 128: hashlib.md5,
    # sha-based
    160: hashlib.sha1, 224: hashlib.sha224, 256: hashlib.sha256,
    384: hashlib.sha384, 512: hashlib.sha512
}


# All available hash modules keyed by the bit size of the hashed output.
hashmodules_by_bitsize = dict ((s, hash_mod(s, m),)
                               for s, m in bitsizes.items())


def get_hasher(bitsize):
    """
    Return a hasher for a given size in bits of the resulting hash.
    """
    return hashmodules_by_bitsize[bitsize]


def checksum(location, bitsize, base64=False):
    """
    Return a checksum of `bitsize` length from the content of the file at
    `location`. The checksum is a hexdigest or base64-encoded is `base64` is
    True.
    """
    if not filetype.is_file(location):
        return
    hasher = get_hasher(bitsize)

    # fixme: we should read in chunks
    with open(location, 'rb') as f:
        hashable = f.read()

    hashed = hasher(hashable)
    if base64:
        return hashed.b64digest()
    else:
        return hashed.hexdigest()


def md5(location):
    return checksum(location, bitsize=128, base64=False)


def sha1(location):
    return checksum(location, bitsize=160, base64=False)


def b64sha1(location):
    return checksum(location, bitsize=160, base64=True)
