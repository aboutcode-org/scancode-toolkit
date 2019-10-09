#
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import, print_function, division

from collections import defaultdict
from itertools import imap, izip
import math

from bitarray import bitarray
from bitarray import bitdiff

from commoncode import codec

from hash.hash import commoncode_hash


"""
Halo is a family of hash functions that have the un-common property that mostly
similar -- but not identical -- inputs will hash to very similar outputs. This
type of hash function is sometimes called a locality-sensitive hash function,
because it is sensitive to the locality of the data being hashed.

The purpose of these hashes is to quickly compare a large number of elements
that are likely to be similar to find candidates and then compute a more
comprehensive similarity only on the candidates. This includes goals such as
identifying near-duplicates of things or to group very similar things together
(a.k.a. clustering), as well as to detect similarities between inputs or perform
quick comparisons under a certain threshold.

For traditional 'good' hash function, small changes in the input will yield very
different hash outputs (through diffusion and avalanche effect). For instance,
cryptographic hashes such as SHA1 or MD5. If you hash two bit strings with a
SHA1 function, and there is only one bit of difference between these two
strings, the resulting hashes will be very different. On average, each time one
bit is added to the input, good hash functions have half of the output bits
switched from 0 to 1.

A Halo hash instead hashes similar inputs to the same hash or to a hash that
differs only by a few bits. The similarity between two hashes becomes an
indication of the similarity between two inputs.

Therefore, the similarity between the two inputs can be approximated by the
similarity between hashed inputs. Hashes are fixed size and much smaller than
the hashed input supporting more efficient and predictable processing of
comparisons.

The hamming distance or number of common bits between two hashes outputs is
roughly proportional to the similarity between the two inputs and can be used to
compute similarity scores between hashes without having access to the full
input.

Halo hashes come in a few varieties:

Bucketed:
---------

The bucket hashes are based on hashing each feature in the input, then grouping
the hash by a subset of the bits of these hashes using the left most or high
bits as a grouping key, similar to hash table buckets. The number of high bits
determines the number of buckets and will determine the size of the resulting
hash (i.e. using the left most 8 high bits will yield a 2**8 or 256 positions
hash). The set of low bits of hashes in each bucket is then further processed
to yield on or more bits. The bits of each bucket are then concatenated
to form the output bit string. Note that this is a form of content partitioning.
Some buckets can be empty for small inputs.

Bit matrix:
-----------

The bit matrix hashes use a bit matrix representation of all the hashes of the
feature, where each row is a feature and each column a bit in the hash for this
feature. For each column of that matrix it computes the sum and then compare
this to averages or quartiles. 

It starts by hashing each feature in the input. The size of these hashes
determines the size of the resulting hash. (i.e. a 128 bits hash function will
yield a 128 bits bit-averaged hash or a 256bits hash when using quartiles). The
hashes are assembled in a bit matrix. For each column in the matrix, bits are
summed. This sum is either compared to the average to yield a 0 below average or
a 1 above average; or it is used to assign a 2 bit value based on quartiles with
00 for q1, 01 for q2, 10 for q3 and 11 for q4. These bits are then concatenated
to form the output bit string.


Bucketed and bit-averaged:
--------------------------

This is a bucket hash where each bucket is bit-averaged. Its starts
with bucketing procedure, then the low bits in each bucket are are transformed
in a Bit Average. If a bucket is empty, then the bit average hash for this bucket is
a sequence of 0 as long as the number of low bits considered for the hash.


Matching and similarity computation:
------------------------------------

Halo hashes can be used as a proxy for similarity computations between two
inputs. For files, the hash size will be smaller than the file itself (except
for small files). This smaller size means that less space and eventually less
computation is needed for the comparisons. Using a fixed hash size enables also
simpler and optimized computations.

To score the similarity, the hamming distance (a bitwise XOR) of every pair of
hashes bit stringshould be computed. This requires O(n^2) comparisons with n
being the number of hashes.

The number of comparisons can be reduced when considering only similarity above
a certain threshold using various pre-filtering techniques.

These include using replicated lookup tables or prefix matching. For instance,
say you create a 384 bit (48 bytes) Bit Average hash, split the hash in 12
32bits chunks. Create a hash table using each 32bit chunk as key and the full
hash as value. It can be proven that hashes that share at least one 32 bit chunk
have 11 or less bits in common. So the matching procedure could be: lookup in
the hash table, then compute the pairwise distance similarity only for matched
hash.

There a few other recent techniques that provide similar and improve matching
usually referred to as  "similarity joins" or "all-pairs".

Averaging halo hashes that work on single bits positions (Bucket average, Bit
Average) also have the uncommon property that parts of the hashes can be used as
approximation for the longer hash with decreasing accuracy. Therefore  matching
accuracy can be tuned after hashing.

For instance , with a 512 bits bit average hash, you could use the first 32 bits
or last 64 bits for doing initial crude exact matches, then doing a pair wise
hamming distance computation only for the smaller number of matching pairs. 

For the bucket hash, the matching can be based on hash table lookups, where
the key contains the individual hashes of each buckets in a hash, and the value
contains the the full hash. Having one or a few bucket hash matched is usually
enough to consider the pair of inputs as near duplicates.

Also halo hashes can be combined in a resulting hash and further enhanced with
additional information such as a few bits from the previous or next input
features, the number of elements that have been hashed or the size of the input,
either for further disambiguation when using short hashes or to avoid doing less
interesting comparisons between input that have significantly different
characteristics such as very different sizes.

The Halo name is a play on what one of the hashing function does. A bucket
averaging hash keeps a bit based on the average of the sum of low hash bits
grouped by high bits, so the process can be summarized as: Group by High bits,
then Average LOw bits; and this gives the HALO acronym. Also a Halo name seems
to fit quite well: a halo is like a fuzzy, halo'ish representation of the input.

Some similar or alternative techniques and functions include:
- Broder et al. minhashing
- Moses Charikar Simhash using random projections and rounding
- Bill Pugh hashtable checksums

The bucket average function resembles Pugh's algorithm by using hash bucketing,
but is different from its usage of only of high and low hash bits, the usage or
averages of buckets and the bit arrays that are used for hamming distance
comparisons instead of checksums.

The bit average function resemble Charikar's algorithm by using each bits in an
array of hashes, but is somewhat different in the way bits are averaged, and the
fact a TF/IDF weighting is not used resulting in a simpler procedure.

Note that halo hashes are not restricted to a feature vector input and can use
rolling hashes (shingles) or straight hashes of features equally well.
Charikar's design is for instance geared towards the document vector space model
and requires a global term (the TF/IDF) whereas these hashes do not.
"""


class BaseHaloHash(object):
    """
    Base class for hashes.
    """
    def __init__(self):
        self.hashes = []
        self.hashmodule = lambda x: x

    def elements_count(self):
        return len(self.hashes)

    def __hashup(self, msg):
        self.hashes.append(self.hashmodule(msg))

    def update(self, msg):
        """
        Append a string or sequence of strings to the hash.
        """
        if not msg:
            return
        if isinstance(msg, basestring):
            self.__hashup(msg)
        else:
            for m in msg:
                self.__hashup(m)

    def hash(self, msg=None):
        """
        Return a bit array representing this hash. Optionally append the msg
        string or sequence of strings to the hash first.
        """
        self.update(msg)
        return self.compute()

    def compute(self):
        """
        Compute the hash and return a bit array.
        """
        raise NotImplementedError()

    def hexdigest(self):
        """
        Return a base64 "url safe"-encoded string representing this hash.

        Return the hex-encoded hash value.
        """
        return self.digest().encode('hex')

    def b64digest(self):
        """
        Return a base64 "url safe"-encoded string representing this hash.
        """
        return codec.b64encode(self.digest())

    def intdigest(self):
        """
        Return an integer or long representing this hash.
        """
        return bit_to_num(self.hash())

    def digest(self):
        """
        Return a binary string representing this hash.
        """
        return self.hash().tobytes()

    def distance(self, other):
        """
        Return the Hamming distance between this hash and another hash.
        """
        return int(bitdiff(self.hash(), other.hash()))


class BaseBucketHaloHash(BaseHaloHash):
    """
    Base class for bucket hashes.
    """
    def __init__(self, msg=None, size_in_bits=32):
        """
        Size in bits must be a power of two.
        """
        super(BaseBucketHaloHash, self).__init__()

        # we use a fixed size hash of 160 (aka sha1) internally
        self.hashmodule = commoncode_hash.get_hasher(160)
        self.hash_length = self.hashmodule().digest_size * 8

        # the number of high bits is the rounded log of the hash size in base 2
        self.high = int(math.log(size_in_bits, 2))
        self.number_of_buckets = 2 ** self.high
        assert self.high < self.hash_length

        # number of low bits: always a complement to the hash length
        self.low = self.hash_length - self.high

        # the maximum int value of one hash made of n low bits
        maxint = (2 ** self.low) - 1
        self.lowmax = maxint

        self.digest_size = size_in_bits // 8

        self.update(msg)

    def build_buckets(self):
        """
        Return a list of buckets splitting high and low using bit shifts and
        group by high.
        """
        hash_buckets = defaultdict(list)
        for h in self.hashes:
            hbv = bitarray_from_bytes(h.digest())
            hi = bit_to_num(hbv[0:self.high])
            lo = hbv[self.high:]
            hash_buckets[hi].append(lo)
        buckets = []
        # TODO: are we off by one on this range?
        for i in range(self.number_of_buckets):
            buck = hash_buckets[i]
            buckets.append(buck or None)
        return buckets


class BucketAverageHaloHash(BaseBucketHaloHash):
    """
    "Bucketize" then average each bucket.

    How the BucketAverageHaloHash works: Bucketize then compute a
    BitAverageHaloHash for each bucket: this is a combination of a bucket hash
    (for partitioning the content) and a bit average hash for combining all
    hashes in a bucket.

    The matching can be done on each bucket hash position, or on hamming
    distance on the whole hash, or a combination based on prefix matching for
    each bucket.

    The high level processing sketch looks like this:
    For an input string of:
        ["this" ,"is", "a", "rose", "great"]:

    * we first hash each list item to get something like
         [4, 15, 2, 12, 12] (with a very short hash function on 4 bits output)
        or as bits something like:
         ['0011', '1110', '0010' ,'1100', '1100']

    * say we consider 2 high bits (meaning an ouput hash on 4 bits), then we
        have something like that splitting the high and low bits for each hash:

       {  '0011':{high:'00',low:'11'}
          '1110':{high:'11',low:'10'}
          '0001':{high:'00',low:'10'}
          '1100':{high:'11',low:'00'}
          '1100':{high:'11',low:'00'}
        }

    * that gives us two groups: one with high:'00' and one with high:'11'

    * we now sum the values of low bits for each group and compute the mean for each group:
            high:'00'
            lowsum = low:'11' + low:'10' = 3 + 2 = 5
            mean = (max value for a low hash * # elements in this group )/2 = 4 *2 /2 = 4
            high:'11'
            lowsum =low:'10' + low:'00' + low:'00' = 3 + 0 +0 = 3
            mean = (max value for a low hash * # elements in this group )/2 = 4 * 3 /2 = 6

    * for each group we compare the sum with the mean for that group and yield a bit:
        if lowsum > mean yield 1 else yield 0
            high:'00'= position 1
            lowsum = 5 > mean = 4 , then bit 1
            high:'01' = position 2
            no hash in that group, hence bit 0
            high:'1' = position 3
            no hash in that group, hence bit 0
            high:'11'== position 3
            lowsum = 3 < mean = 6 , then bit 0

    * our hash for that input and the hash function, low and high bits used is therefore:
         pos 1 + pos2 + pos3 + pos4 = '1000'

    In general, this hash seem to show a good accuracy and little sensitivity
    with small string and small inputs variations. The input needs to be long
    enough to have some chance to fill all the hash buckets with some entries.

    Some usage examples:

    >>> a = BucketAverageHaloHash(size_in_bits=2**5)
    >>> z = [a.update(x) for x in '''The value specified for size must be at
    ... least as large as for the smallest bit vector possible for intVal'''.split()]
    >>> b = BucketAverageHaloHash(size_in_bits=2**5)
    >>> z = [b.update(x) for x in '''The value specified for size must be no
    ... more larger than the smallest bit vector possible for intVal'''.split()]
    >>> a.distance(b)
    5
    >>> b.distance(a)
    5
    >>> a.hexdigest()
    '08200010'
    >>> a = BucketAverageHaloHash(size_in_bits=2**6)
    >>> z = [a.update(x) for x in '''The value specified for size must be at
    ... least as large as for the smallest bit vector possible for intVal'''.split()]
    >>> b = BucketAverageHaloHash(size_in_bits=2**6)
    >>> z = [b.update(x) for x in '''The value specified for size must be no
    ... more larger than the smallest bit vector possible for intVal'''.split()]
    >>> a.distance(b)
    5
    >>> a = BucketAverageHaloHash(size_in_bits=2**7)
    >>> z = [a.update(x) for x in '''The value specified for size must be at
    ... least as large as for the smallest bit vector possible for intVal'''.split()]
    >>> b = BucketAverageHaloHash(size_in_bits=2**7)
    >>> z = [b.update(x) for x in '''The value specified for size must be no
    ... more larger than the smallest bit vector possible for intVal'''.split()]
    >>> a.distance(b)
    5
    >>> a = BucketAverageHaloHash(size_in_bits=2**8)
    >>> z = [a.update(x) for x in '''The value specified for size must be at
    ... least as large as for the smallest bit vector possible for intVal'''.split()]
    >>> b = BucketAverageHaloHash(size_in_bits=2**8)
    >>> z = [b.update(x) for x in '''The value specified for size must be no
    ... more larger than the smallest bit vector possible for intVal'''.split()]
    >>> a.distance(b)
    5
    >>> a = BucketAverageHaloHash('''The value specified for size must be at least
    ...  as large as for the smallest bit vector possible for intVal'''.split(), size_in_bits=2**9)
    >>> b = BucketAverageHaloHash('''The value specified for size must be no more
    ...  larger than the smallest bit vector possible for intVal'''.split(), size_in_bits=2**9)
    >>> a.distance(b)
    4
    >>> a = BucketAverageHaloHash('''The value specified for size must be at least
    ...  as large as for the smallest bit vector possible for intVal'''.split(), size_in_bits=2**9)
    >>> b = BucketAverageHaloHash('''The value specified for size must be at least
    ...  as large as for the smallest bit vector possible for intVal'''.split(), size_in_bits=2**9)
    >>> a.distance(b)
    0
    >>> assert a.intdigest() == b.intdigest()
    >>> a = BucketAverageHaloHash(size_in_bits=2**10)
    >>> z = [a.update(x) for x in '''The value specified for size must be at
    ... least as large as for the smallest bit vector possible for intVal'''.split()]
    >>> b = BucketAverageHaloHash(size_in_bits=2**10)
    >>> z = [b.update(x) for x in '''The value specified for size must be no
    ... more larger than the smallest bit vector possible for intVal'''.split()]
    >>> a.distance(b)
    4
    """
    def compute(self):
        """
        Compute the bucket average hash and return a bit array.
        """
        hashes_buckets = self.build_buckets()
        hashvector = bitarray()

        for lo in hashes_buckets:
            if lo:
                low = map(bit_to_num, lo)
                low_mean = len(low) * self.lowmax / 2
                total = low and sum(low) or 0
                if total > low_mean:
                    hashvector.append(1)
                else:
                    hashvector.append(0)
            else:
                hashvector.append(0)
        return hashvector


class BaseBitMatrixHaloHash(BaseHaloHash):
    """
    Base class for hash using bit matrices.
    """
    def __init__(self, msg=None, size_in_bits=128):
        super(BaseBitMatrixHaloHash, self).__init__()
        try:
            self.hashmodule = commoncode_hash.get_hasher(size_in_bits)
        except:
            raise Exception('No available hash module for the requested '
                            'hash size in bits: %(size_in_bits)d' % locals())
        self.update(msg)
        self.digest_size = size_in_bits // 8

    def sum_columns(self):
        """
        Return an iterable of the sum of bits for each column.
        """
        arrays = (bitarray_from_bytes(h.digest()) for h in self.hashes)
        # reorg the bit matrix in columns
        # TODO: numpy likely can sum columns alright
        transposed = izip(*arrays)
        # we want a zero to substract 1 and a 1 to add 1 to our sum for a given bit column
        normalized = (normalize(column) for column in transposed)
        summed = imap(sum, normalized)
        return summed


def normalize(iterable):
    return (-1 if v else 1 for v in iterable)


class BitAverageHaloHash(BaseBitMatrixHaloHash):
    """
    A bit matrix averaging hash.

    The high level processing sketch looks like this:
    For an input of:
        ['this' ,'is', 'a', 'rose', 'great']:
    
    * we first hash each list item to get something like
        [4, 15, 2, 12, 12] (for instance with a very short hash function of 4 bits output)
    
    or as bits this would be something like this:
    
          ['0011',
           '1110',
           '0010',
           '1100',
           '1100']
    
    * we sum up each bit positions/columns together:
          ['0011',
           '1110',
           '0010',
           '1100',
           '1100']
           -------
            3331
    
    or stated otherwise: pos1=3, pos2=3, pos3=3, pos4=1
    
    * The mean value for a column is number of hashes/2 (2 because we use bits).
      Here mean = 5 hashes/2 = 2.5
    
    * We compare the sum of each position with the mean and yield a bit:
        if pos sum > mean yield 1 else yield 0
            position1 = 3 > mean = 2.5 , then bit=1
            position2 = 3 > mean = 2.5 , then bit=1
            position3 = 3 > mean = 2.5 , then bit=1
            position4 = 1 < mean = 2.5 , then bit=0
    
    * We build a hash by concatenating the resulting bits:
         pos 1 + pos2 + pos3 + pos4 = '1110'
    
    In general, this hash seems to show a lower accuracy and higher sensitivity
    with small string and small inputs variations than the bucket average hash.
    But it works better on shorter inputs.

    Some usage examples:

    >>> z = '''The value specified for size must be at
    ... least as large as for the smallest bit vector possible for intVal'''.split()
    >>> a = BitAverageHaloHash(z, size_in_bits=256)
    >>> len(a.hash())
    256
    >>> z = '''The value specified for size must be no
    ... more larger than the smallest bit vector possible for intVal'''.split()
    >>> b = BitAverageHaloHash(z, size_in_bits=256)
    >>> a.distance(b)
    57
    >>> b.distance(a)
    57
    >>> a = BitAverageHaloHash(size_in_bits=160)
    >>> z = [a.update(x) for x in '''The value specified for size must be at
    ... least as large as for the smallest bit vector possible for intVal'''.split()]
    >>> a.hexdigest()
    '2c10223104c43470e10b1157e6415b2f730057d0'
    >>> b = BitAverageHaloHash(size_in_bits=160)
    >>> z = [b.update(x) for x in '''The value specified for size must be no
    ... more larger than the smallest bit vector possible for intVal'''.split()]
    >>> b.hexdigest()
    '2c912433c4c624e0b03b34576641df8fe00017d0'
    >>> a.distance(b)
    29
    >>> a = BitAverageHaloHash(size_in_bits=128)
    >>> z =[a.update(x) for x in '''The value specified for size must be at
    ... least as large as for the smallest bit vector possible for intVal'''.split()]
    >>> a.hexdigest()
    '028b1699c0c5310cd1b566a893d12f10'
    >>> b = BitAverageHaloHash(size_in_bits=128)
    >>> z = [b.update(x) for x in '''The value specified for size must be no
    ... more larger than the smallest bit vector possible for intVal'''.split()]
    >>> b.hexdigest()
    '0002969060d5b344d1b7602cd9e127b0'
    >>> a.distance(b)
    27
    >>> a = BitAverageHaloHash(size_in_bits=64)
    >>> z = [a.update(x) for x in '''The value specified for size must be at
    ... least as large as for the smallest bit vector possible for intVal'''.split()]
    >>> a.hexdigest()
    '028b1699c0c5310c'
    >>> b = BitAverageHaloHash(size_in_bits=64)
    >>> z = [b.update(x) for x in '''The value specified for size must be no
    ... more larger than the smallest bit vector possible for intVal'''.split()]
    >>> b.hexdigest()
    '0002969060d5b344'
    >>> a.distance(b)
    14
    >>> a = BitAverageHaloHash(size_in_bits=32)
    >>> z = [a.update(x) for x in '''The value specified for size must be at
    ... least as large as for the smallest bit vector possible for intVal'''.split()]
    >>> b = BitAverageHaloHash(size_in_bits=32)
    >>> z = [b.update(x) for x in '''The value specified for size must be at
    ... least as large as for the smallest bit vector possible by intVal'''.split()]
    >>> a.distance(b)
    5
    >>> a = BitAverageHaloHash(size_in_bits=512)
    >>> z = [a.update(x) for x in '''The value specified for size must be at
    ... least as large as for the smallest bit vector possible for intVal'''.split()]
    >>> b = BitAverageHaloHash(size_in_bits=512)
    >>> z = [b.update(x) for x in '''The value specified for size must be at
    ... least as large as for the smallest bit vector possible by intVal'''.split()]
    >>> a.distance(b)
    46
    """
    def compute(self):
        """
        Compute the hash and return a bit array representing it.

        Note that the mean/average is global to a hash as it depends on the
        number of hashed values. Since we use bit, the mean and median are the
        same.
        """
        col_sums = self.sum_columns()
        return bitarray(compute_avg(col_sums))


def compute_avg(col_sums):
    """
    Given an iterable of columns sums, yield an iteable of bits as 0 or 1
    """
    for col_sum in col_sums:
        if col_sum > 0:
            yield 1
        else:
            yield 0


class BitQuartileHaloHash(BaseBitMatrixHaloHash):
    """
    A bit matrix averaging hash using quartiles rather than plain average.

    The high level processing sketch looks like this:
    For an input of:
        ['this' ,'is', 'a', 'rose', 'great']:
    
    * we first hash each list item to get something like
        [4, 15, 2, 12, 12] (for instance with a very short hash function of 4 bits output)
    
    or as bits this would be something like this:
    
          ['0011',
           '1110',
           '0010',
           '1100',
           '1100']
    
    * for each position, we compute the sum of the bit in that column:
          ['0011',
           '1110',
           '0010',
           '1100',
           '1100']
           -------
            3331
    
    or stated otherwise: pos1=3, pos2=3, pos3=3, pos4=1
    
    * Based on the number of items we define the four quartiles rounded down.
      Here we have 5 items, so each quartile is for values:
      - 0 <= Q1 <= 1
      - 1 <  Q2 <= 2
      - 2 <  Q3 <= 3
      - 3 <  Q4
      
    * The sum of each column quartile yields a two bit value:
     - Q1: 00
     - Q2: 01
     - Q3: 10
     - Q4: 11
     
    * We build a hash by concatenating the resulting bits:
         pos 1 + pos2 + pos3 + pos4 = '1110'
      Here for 3331 this yields: 11 11 11 00
    
    Some usage examples:
    Some usage examples:

    >>> z = '''The value specified for size must be at
    ... least as large as for the smallest bit vector possible for intVal'''.split()
    >>> a = BitQuartileHaloHash(z, size_in_bits=256)
    >>> len(a.hash())
    256
    >>> z = '''The value specified for size must be no
    ... more larger than the smallest bit vector possible for intVal'''.split()
    >>> b = BitQuartileHaloHash(z, size_in_bits=256)
    >>> a.distance(b)
    16
    >>> b.distance(a)
    16
    >>> a = BitQuartileHaloHash(size_in_bits=320)
    >>> z = [a.update(x) for x in '''The value specified for size must be at
    ... least as large as for the smallest bit vector possible for intVal'''.split()]
    >>> a.hexdigest()
    '042001000408020000101020002014004000000400001101041000010041040a2000000010080100'
    >>> b = BitQuartileHaloHash(size_in_bits=320)
    >>> z = [b.update(x) for x in '''The value specified for size must be no
    ... more larger than the smallest bit vector possible for intVal'''.split()]
    >>> a.distance(b)
    35
    >>> a = BitQuartileHaloHash(size_in_bits=128)
    >>> z =[a.update(x) for x in '''The value specified for size must be at
    ... least as large as for the smallest bit vector possible for intVal'''.split()]
    >>> b = BitQuartileHaloHash(size_in_bits=128)
    >>> z = [b.update(x) for x in '''The value specified for size must be no
    ... more larger than the smallest bit vector possible for intVal'''.split()]
    >>> b.hexdigest()
    '00000000020000000000801100000010'
    >>> a.distance(b)
    6
    >>> a = BitQuartileHaloHash(size_in_bits=64)
    >>> z = [a.update(x) for x in '''The value specified for size must be at
    ... least as large as for the smallest bit vector possible for intVal'''.split()]
    >>> b = BitQuartileHaloHash(size_in_bits=64)
    >>> z = [b.update(x) for x in '''The value specified for size must be no
    ... more larger than the smallest bit vector possible for intVal'''.split()]
    >>> a.distance(b)
    2
    >>> a = BitQuartileHaloHash(size_in_bits=32)
    >>> z = [a.update(x) for x in '''The value specified for size must be at
    ... least as large as for the smallest bit vector possible for intVal'''.split()]
    >>> b = BitQuartileHaloHash(size_in_bits=32)
    >>> z = [b.update(x) for x in '''The value specified for size must be at
    ... least as large as for the smallest bit vector possible by intVal'''.split()]
    >>> a.distance(b)
    0
    >>> a = BitQuartileHaloHash(size_in_bits=512)
    >>> z = [a.update(x) for x in '''The value specified for size must be at
    ... least as large as for the smallest bit vector possible for intVal'''.split()]
    >>> b = BitQuartileHaloHash(size_in_bits=512)
    >>> z = [b.update(x) for x in '''The value specified for size must be at
    ... least as large as for the smallest bit vector possible by intVal'''.split()]
    >>> a.distance(b)
    15
    """

    def __init__(self, msg=None, size_in_bits=128):
        # we use 2 bits per column, so we use half the size for hashing
        super(BitQuartileHaloHash, self).__init__(msg, size_in_bits=size_in_bits / 2)
        # but we will still return the proper size
        self.digest_size = size_in_bits // 8
        self.size_in_bits = size_in_bits

    def compute(self):
        """
        Compute the hash and return a bit array representing it.
        """
        col_sums = self.sum_columns()

        # assign two bit value to each column based on sum quartiles
        q1, q2, q3 = self.quartiles()
        quartiled = [0] * self.size_in_bits
        for pos, total in enumerate(col_sums):
            if total < q1:
                # values are already set to zero
                continue

            # left and right bit positions
            left = pos * 2
            right = left + 1

            if total < q2:
                quartiled[right] = 1
                continue
            if total < q3:
                quartiled[left] = 1
                continue
            # else: total >= q3: this is q4
            quartiled[left] = 1
            quartiled[right] = 1

        return bitarray(quartiled)

    def quartiles(self):
        """
        Return a three tuple for the boundaries of each quartile, computed based
        on the number of hashed elements.
        """
        quart = len(self.hashes) / 4
        return quart, quart * 2, quart * 3


def bitarray_from_bytes(b):
    """
    Return a bitarray built from a byte string b. 
    """
    a = bitarray()
    a.frombytes(b)
    return a


def hamming_distance(bv1, bv2):
    """
    Return the Hamming distance between `bv1` and `bv2`  bitvectors as the
    number of equal bits for all positions. (e.g. the count of bits set to one
    in an XOR between two bit strings.)

    `bv1` and `bv2` must both be  either hash-like Halohash instances (with a
    hash() function) or bit array instances (that can be manipulated as-is).

    See http://en.wikipedia.org/wiki/Hamming_distance

    For example:

    >>> b1 = bitarray('0001010111100001111')
    >>> b2 = bitarray('0001010111100001111')
    >>> hamming_distance(b1, b2)
    0
    >>> b1 = bitarray('11110000')
    >>> b2 = bitarray('00001111')
    >>> hamming_distance(b1, b2)
    8
    >>> b1 = bitarray('11110000')
    >>> b2 = bitarray('00110011')
    >>> hamming_distance(b1, b2)
    4
    """
    return int(bitdiff(bv1, bv2))


def slices(s, size):
    """
    Given a sequence s, return a sequence of non-overlapping slices of `size`.
    Raise an AssertionError if the sequence length is not a multiple of `size`.

    For example:
    >>> slices([1, 2, 3, 4, 5, 6], 2)
    [(1, 2), (3, 4), (5, 6)]
    >>> slices([1, 2, 3, 4, 5, 6], 3)
    [(1, 2, 3), (4, 5, 6)]
    >>> try:
    ...    slices([1, 2, 3, 4, 5, 6], 4)
    ... except AssertionError:
    ...    pass
    """
    length = len(s)
    assert length % size == 0, 'Invalid slice size: len(%(s)r) is not a multiple of %(size)r' % locals()
    # TODO: time alternative
    # return [s[index:index + size] for index in range(0, length, size)]
    chunks = [iter(s)] * size
    return list(izip(*chunks))


def common_chunks(h1, h2, chunk_bytes_length=4):
    """
    Compute the number of common chunks of byte length `chunk_bytes_length` between to
    hashes h1 and h2 using the digest.

    Note that chunks that are all set to zeroes are matched too: they are be
    significant such as empty buckets of bucket hashes.

    For example:

    >>> m1 = 'The value specified for size must be at least as large'.split()
    >>> m2 = 'The value specific for size must be at least as large'.split()
    >>> a = BitAverageHaloHash(msg=m1, size_in_bits=256)
    >>> b = BitAverageHaloHash(msg=m2, size_in_bits=256)
    >>> common_chunks(a, b, 2)
    1
    >>> hamming_distance(a.hash(), b.hash())
    32
    """
    h1_slices = slices(h1.digest(), chunk_bytes_length)
    h2_slices = slices(h2.digest(), chunk_bytes_length)
    commons = (1 for h1s, h2s in izip(h1_slices, h2_slices) if h1s == h2s)
    return sum(commons)


def bit_to_num(bits):
    """
    Return an int (or long) for a bit array.
    
    For example:
    TODO: test
    """
    return int(bits.to01(), 2)


# TODO: add test!
def decode_vector(b64_str):
    """
    Return a bit array from an encoded string representation.
    """
    decoded = codec.urlsafe_b64decode(b64_str)
    return bitarray_from_bytes(decoded)
