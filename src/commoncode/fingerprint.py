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
import hashlib


def generate_fingerprint(location):
    """
        Return fingerprint of the file at `location`.
    """
    token_list = get_tokenlist(location)
    weighted_list = get_weightedlist(token_list)
    fingerprint = process_weightedlist(weighted_list)

    return "".join(str(x) for x in fingerprint)


def get_tokenlist(location):
    """
       Return a list of tokens for the file at `location`.
    """
    results = []

    with open(location, 'r') as f:
        for line in f:
            for token in line.split():
                results.append(token)

    return results


def get_weightedlist(token_list):
    """
        Return a weighted array from the word token list.
    """
    result = [0] * 128
    shingle_length = 3
    length = len(token_list) - shingle_length

    for index in range(length):
        shingle = token_list[index] + token_list[index + 1] + token_list[index + 2]
        process_shingles(shingle, result)

    return result


def process_weightedlist(weighted_list):
    """
        Return fingerprint from a weighted array.
    """
    result = []

    for item in weighted_list:
        if item > 0:
            result.append(1)
        else:
            result.append(0)

    return result


def process_shingles(shingle, weighted_list):
    """
        modify weighted list wrt to shingle
    """
    result = hashlib.md5(shingle.encode()).hexdigest()
    hash_length = 128
    binary_hash = bin(int(result, 16))[2:].zfill(hash_length)
    for bit in range(hash_length):
        if binary_hash[bit] == '1':
            weighted_list[bit] += 1
        else:
            weighted_list[bit] -= 1

    return weighted_list
