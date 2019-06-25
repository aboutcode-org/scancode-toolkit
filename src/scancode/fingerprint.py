#
# Copyright (c) nexB Inc. and others. All rights reserved.
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

import binascii
from bitarray import bitarray
from bitarray import bitdiff
from licensedcode.tokenize import ngrams
import hashlib

HASH_LENGTH = 128
SHINGLE_LENGTH = 3

class Simhash:
    """
    Fingerprint class to generate fingerprints for files used for similarity matching
    """
    def __init__(self):
        self.tokens = []


    def generate_fingerprint(self):
        """
        Return fingerprint as a bitarray
        """
        weighted_hash = self.get_weighted_hash()
        fingerprint = self.process_weighted_hash(weighted_hash)

        return fingerprint


    def hex_digest(self):
        """
        Return fingerprint as a hex string
        """
        result = None

        if len(self.tokens):
            fingerprint_binary = self.generate_fingerprint()
            result = binascii.hexlify(fingerprint_binary)
        return result


    def get_weighted_hash(self):
        """
        Return a weighted array from the word token list.
        """
        result = [0] * HASH_LENGTH
        length = len(self.tokens) - SHINGLE_LENGTH + 1
        shingles = ngrams(self.tokens, SHINGLE_LENGTH)

        if length > 0:
            for shingle in shingles:
                shingle = ''.join(shingle)
                self.process_shingles(shingle, result)
        else:
            self.process_shingles(''.join(self.tokens), result)

        return result


    def process_weighted_hash(self, weighted_hash):
        """
        Return fingerprint from a weighted array as a bitarray.
        """
        result = bitarray()

        for item in weighted_hash:
            if item > 0:
                result.append(1)
            else:
                result.append(0)

        return result

    @staticmethod
    def bitarray_from_bytes(b):
        """
        Return bitarray from a byte string, interpreted as machine values.
        """
        a = bitarray()
        a.frombytes(b)

        return a


    def process_shingles(self, shingle, weighted_list):
        """
        Modify weighted list wrt to shingle
        """
        hash = hashlib.md5(shingle.encode()).digest()
        result = self.bitarray_from_bytes(hash)

        for idx, bit in enumerate(result):
            if bit:
                weighted_list[idx] += 1
            else:
                weighted_list[idx] -= 1

        return weighted_list


    def update(self, string):
        """
        Update tokens by appending new tokens
        """
        new_tokens = string.split()
        self.tokens += new_tokens


    def bitarray_from_hex(self, fingerprint_hex):
        """
        Return bitarray from a hex string.
        """
        bytes = binascii.unhexlify(fingerprint_hex)
        result = self.bitarray_from_bytes(bytes)

        return result


    def hamming_distance(self, fingerprint1, fingerprint2):
        """
        Return hamming distance between two given fingerprints
        """
        distance = bitdiff(fingerprint1, fingerprint2)
        result = int(distance)

        return result
