#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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

from __future__ import division
from __future__ import absolute_import

from collections import Counter
import math
import zlib


def entropy(location, length=5000):
    """
    Return the Shannon entropy of up to `length` bytes from the file at
    location.
    """
    with open(location, 'rb') as locf:
        data = locf.read(length)
    return shannon_entropy(data)


def shannon_entropy(seq):
    """
    Return the Shannon entropy of a `seq` sequence of items (typically a
    byte string).
    The entropy can be seen as the number of bits that would be required
    on average to encode seq optimally.
    See https://en.wikipedia.org/wiki/Entropy_(information_theory)
    See http://www.onlamp.com/pub/a/php/2005/01/06/entropy.html
    """

    if not seq:
        return 0.0

    log = math.log
    length = len(seq)
    frequencies = Counter(seq)
    probabilities = (freq / length for freq in frequencies.values())
    return -sum(p * log(p, 2) for p in probabilities)


def gzip_entropy(s):
    """
    Return the "GZIP" entropy of byte string `s`. This is the ratio of
    compressed length to the original length. Because of overhead this
    does not gives great results on short strings.
    """
    if not bytes:
        return 0

    length = len(s)
    if not length:
        return 0

    compressed = len(zlib.compress(s, 9))
    return compressed / length
