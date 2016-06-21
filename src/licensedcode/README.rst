License detection overview and key design elements
==================================================

License detection is about finding common texts between the text of a query file
being scanned and the texts of the indexed license texts and rule texts. The
process strives to be correct first and fast second.

Ideally we want to find the best alignment possible between two texts so we know
exactly where they match. We settle for good alignments rather than optimal
alignments by still returning accurate and correct matches in a reasonable
amount of time.

Correctness is essential but efficiency too: both in terms of speed and memory
usage. One key to efficient matching is to process not characters but whole
words and use internally not strings but integers.


Rules and licenses
------------------

The detection uses an index of reference license texts and a set of "rules"
which are common notices or mentions of these licenses. The things that makes
detection sometimes difficult is that a license reference can be very short as
in "this is GPL" or very long as a full license text. To cope with this we use
different matching strategies and also compute the resemblance and containment
of rules in matches.



Words as integers
-----------------

A dictionary mapping words to a unique integer is used to transform query and
indexed words to numbers. This is possible because we have a limited number of
words across all the license texts (about 15K). We further assign these ids to
words such that very common words have a low id and less common, more
discriminant words have a higher id. And define a thresholds for this ids range
such that very common words below that threshold cannot possible form a license
mention together.

Once that mapping is applied, we then only deal with integers in two dimensions:
 - the token ids (and whether they are in the high or low range).
 - their positions in the query (qpos) and the indexed rule (ipos).

We also use an integer id for a rule, and we identify a gap in a rule template
by the position of its start.

All operations are from then on dealing with list, arrays or sets of integers in
defined ranges.

Matches are reduced to three sets of integers we call "Spans":
- matched positions on the query side
- matched positions on the index side
- matched positions of token ids in the high range on the index side, which is a
  subset of all matched index positions and is used for quality check of the
  matches.

By using integers in known ranges throughout, several operations are reduced to
integer and integer sets or lists comparisons and intersection. This operations
are faster and more readily optimizable.

With integers, we use less memory:
- we can use arrays of unsigned 16 bits ints stored each on two bytes rather than larger lists of ints.
- we can replace dictionaries by sparse lists or arrays where the index is an integer key.
- we can use succinct, bit level representations (e.g. bitmaps) of integer sets.

Smaller data structures also means faster processing as the processor needs to
move less data in memory.

With integers we can also be faster:
- a dict key lookup is slower than a list of array index lookup,
- processing large list of small structures is faster (such as bitmaps, etc).
- we can leverage libraries that speed up integer set operations.


Common/junk tokens
------------------

The quality and speed of detection is supported by classifying each word as
either good or common/junk. Junk tokens are either very frequent of tokesn that
take together together cannot form some valid license mention. When a numeric id
is assigned to a token during indexing, junk tokens are assigned a lower id than
good tokens. These are then called low or junk tokens and high or good tokens.


Query processing
----------------

When a file is scanned it converted to a query object which is a list of integer
token ids. A query is further broken down in slices (a.k.a. query run) based on
heuristics.

While the query is processed a set of matchable positions for for high and low
token ids is kept to track what is left to do in matching.


Matching pipeline
-----------------

The matching pipeline consist of:

 - matching the whole query at once against hashes and a cache.
 
 - subtracting from the query any exact match to "negative rules" which are
 texts that are not containing license information but may match otherwise to
 existing rules

 - matching the whole query for exact matches using an automaton (Aho-Corasick)

 - then each query run is processed:
  - the best matching rules are foudn with an approximate set match
  - we perform a pair-wise sequence matching between these candidates and the query run
  
 - finally the matches are merged, refined and filtered to yield the final results   

