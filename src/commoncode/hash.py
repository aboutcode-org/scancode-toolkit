#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/aboutcode-org/commoncode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import binascii
import hashlib
import os
import sys
from functools import partial

from commoncode import filetype
from commoncode.codec import bin_to_num
from commoncode.codec import urlsafe_b64encode

"""
Hashes and checksums.

Low level hash functions using standard crypto hashes used to construct hashes
of various lengths. Hashes that are smaller than 128 bits are based on a
truncated md5. Other length use SHA hashes.

Checksums are operating on files.
"""

# This is ~16 MB
FILE_CHUNK_SIZE = 2**24


def _hash_mod(bitsize, hmodule):
    """
    Return a hasher class that returns hashes with a ``bitsize`` bit length. The interface of this
    class is similar to the hash module API.
    """

    class hasher(Hashable):
        """A hasher class that behaves like a hashlib module."""

        def __init__(self, msg=None, **kwargs):
            """
            Return a hasher, populated with an initial ``msg`` bytes string.
            Close on the bitsize and hmodule
            """
            # length of binary digest for this hash
            self.digest_size = bitsize // 8

            # binh = binary hasher module
            self.binh = hmodule()

            # msg_len = length in bytes of the message hashed
            self.msg_len = 0

            if msg:
                self.update(msg)

        def update(self, msg=None):
            """
            Update this hash with a ``msg`` bytes string.
            """
            if msg:
                self.binh.update(msg)
                self.msg_len += len(msg)

    return hasher


class Hashable:
    """
    A mixin for hashers that provides the base methods.
    """

    def digest(self):
        """
        Return a bytes string digest for this hash.
        """
        if not self.msg_len:
            return
        return self.binh.digest()[: self.digest_size]

    def hexdigest(self):
        """
        Return a string hex digest for this hash.
        """
        return self.msg_len and binascii.hexlify(self.digest()).decode("utf-8")

    def b64digest(self):
        """
        Return a string base64 digest for this hash.
        """
        return self.msg_len and urlsafe_b64encode(self.digest()).decode("utf-8")

    def intdigest(self):
        """
        Return a int digest for this hash.
        """
        return self.msg_len and int(bin_to_num(self.digest()))


# for FIPS support, we declare that "usedforsecurity" is False
sys_v0 = sys.version_info[0]
sys_v1 = sys.version_info[1]
md5_hasher = partial(hashlib.md5, usedforsecurity=False)


# Base hashers for each bit size
_hashmodules_by_bitsize = {
    # md5-based
    32: _hash_mod(32, md5_hasher),
    64: _hash_mod(64, md5_hasher),
    128: _hash_mod(128, md5_hasher),
    # sha-based
    160: _hash_mod(160, hashlib.sha1),
    256: _hash_mod(256, hashlib.sha256),
    384: _hash_mod(384, hashlib.sha384),
    512: _hash_mod(512, hashlib.sha512),
}


def get_hasher(bitsize):
    """
    Return a hasher for a given size in bits of the resulting hash.
    """
    return _hashmodules_by_bitsize[bitsize]


class sha1_git_hasher(Hashable):
    """
    Hash content using the git blob SHA1 convention.
    See https://git-scm.com/book/en/v2/Git-Internals-Git-Objects#_object_storage
    """

    def __init__(self, msg=None, total_length=0, **kwargs):
        """
        Initialize a sha1_git_hasher with an optional ``msg`` byte string. The ``total_length`` of
        all content that will be hashed, combining the ``msg`` length plus any later call to
        update() with additional messages.

        Here ``total_length`` is total length in bytes of all the messages (chunks) hashed
        in contrast to  ``msg_len`` which is the length in bytes for the optional message.
        """
        self.digest_size = 160 // 8
        self.msg_len = 0

        if msg:
            self.msg_len = msg_len = len(msg)

            if not total_length:
                total_length = msg_len
            else:
                if total_length < msg_len:
                    raise ValueError(
                        f"Initial msg length: {msg_len} "
                        f"cannot be larger than the the total_length: {self.total_length}"
                    )

        if not total_length:
            raise ValueError("total_length cannot be zero")

        self.total_length = total_length
        self.binh = get_hasher(bitsize=160)(total_length=total_length)

        self._hash_header()
        if msg:
            self.update(msg)

    def _hash_header(self):
        # note: bytes interpolation is new in Python 3.5
        git_blob_header = b"blob %d\0" % (self.total_length)
        self.binh.update(msg=git_blob_header)

    def update(self, msg=None):
        """
        Update this hash with a ``msg`` bytes string.
        """
        if msg:
            msg_len = len(msg)
            if (msg_len + self.msg_len) > self.total_length:
                raise ValueError(
                    f"Actual combined msg lengths: initial: {self.msg_len} plus added: {msg_len} "
                    f"cannot be larger than the the total_length: {self.total_length}"
                )

            self.binh.update(msg)
            self.msg_len += msg_len


_hashmodules_by_name = {
    "md5": get_hasher(128),
    "sha1": get_hasher(160),
    "sha1_git": sha1_git_hasher,
    "sha256": get_hasher(256),
    "sha384": get_hasher(384),
    "sha512": get_hasher(512),
}


def get_hasher_instance_by_name(name, total_length=0):
    """
    Return a hasher instance for a checksum algorithm ``name`` with a planned ``total_length`` of
    bytes to hash.
    """
    try:
        hm = _hashmodules_by_name[name]
        return hm(total_length=total_length)
    except KeyError:
        raise ValueError(f"Unknown checksum algorithm: {name!r}")


def get_file_size(location):
    return os.path.getsize(location)


def checksum(location, name, base64=False):
    """
    Return a checksum from the content of the file at ``location`` using the ``name`` checksum
    algorithm. The checksum is a string as a hexdigest or is base64-encoded is ``base64`` is True.

    Return None if ``location`` is not a file or an empty file.
    """
    if not filetype.is_file(location):
        return

    total_length = get_file_size(location)
    chunks = binary_chunks(location)
    return checksum_from_chunks(chunks=chunks, total_length=total_length, name=name, base64=base64)


def checksum_from_chunks(chunks, name, total_length=0, base64=False):
    """
    Return a checksum from the content of the iterator of byte strings ``chunks`` with a
    ``total_length`` combined length using the ``name`` checksum algorithm. The returned checksum is
    a string as a hexdigest or is base64-encoded is ``base64`` is True.
    """
    hasher = get_hasher_instance_by_name(name=name, total_length=total_length)
    for chunk in chunks:
        hasher.update(chunk)
    if base64:
        return hasher.b64digest()
    return hasher.hexdigest()


def binary_chunks(location, size=FILE_CHUNK_SIZE):
    """
    Read file at ``location`` as binary and yield bytes of up to ``size`` length in bytes,
    defaulting to 2**24 bytes, e.g., about 16 MB.
    """
    with open(location, "rb") as f:
        while True:
            chunk = f.read(size)
            if not chunk:
                break
            yield chunk


def md5(location):
    return checksum(location, name="md5", base64=False)


def sha1(location):
    return checksum(location, name="sha1", base64=False)


def b64sha1(location):
    return checksum(location, name="sha1", base64=True)


def sha256(location):
    return checksum(location, name="sha256", base64=False)


def sha512(location):
    return checksum(location, name="sha512", base64=False)


def sha1_git(location):
    return checksum(location, name="sha1_git", base64=False)


def multi_checksums(location, checksum_names=("md5", "sha1", "sha256", "sha512", "sha1_git")):
    """
    Return a mapping of hexdigest checksum strings keyed by checksum algorithm name from hashing the
    content of the file at ``location``. Use the ``checksum_names`` list of checksum names. The
    mapping is guaranted to contains all the requested names as keys. If the location is not a file,
    or if the file is empty, the values are None.

    The purpose of this function is to avoid read the same file multiple times
    to compute different checksums.
    """
    if not filetype.is_file(location):
        return {name: None for name in checksum_names}
    file_size = get_file_size(location)
    if file_size == 0:
        return {name: None for name in checksum_names}

    hashers = {
        name: get_hasher_instance_by_name(name=name, total_length=file_size)
        for name in checksum_names
    }

    for chunk in binary_chunks(location):
        for hasher in hashers.values():
            hasher.update(msg=chunk)

    return {name: hasher.hexdigest() for name, hasher in hashers.items()}
