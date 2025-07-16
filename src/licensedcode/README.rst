Overview
========

This `licensedcode` module have utilities to accurately detect a vast array
of open-source and proprietary licenses. It manages a comprehensive
database of license texts, patterns, and rules, enabling ScanCode to
perform scans and provide precise license conclusions.

Key Functionality
-----------------

- License Rule Management: Stores and manages a large collection of
  license rules, including full texts, snippets, and regular expressions.

- Pattern Matching: Implements sophisticated algorithms for matching
  detected code against known license patterns and texts.

- License Detection Logic: Contains the core logic for processing scan
  input, applying rules, and determining the presence and type of
  licenses.

- Rule-based Detection: Utilizes a robust system of rules to identify
  licenses even when only fragments or variations of license texts are
  present.

- License Expression Parsing: Supports the parsing and interpretation of
  complex license expressions (e.g., "MIT AND Apache-2.0").


How It Works (High-Level)
-------------------------

At a high level, the `licensedcode`` module operates by:

1. Loading License Data: It initializes by loading a curated set of
  license texts, short license identifiers, and detection rules from its
  internal data store.

2. Scanning Input: When ScanCode processes a file or directory, the
  content is converted into an internal representation (a "query").

3. Applying Rules: The module then applies its extensive set of rules and
  patterns to the input content through a multi-stage pipeline, looking
  for matches.

4. Reporting Detections: Upon successful matches, it reports the
  identified licenses, their confidence levels, and the exact locations
  (lines, characters) where they were found.

For a more in-depth understanding of the underlying technical principles
and the detection pipeline, please refer to the sections below.



ScanCode license detection overview and key design elements
-----------------------------------------------------------

License detection involves identifying commonalities between the text of a
scanned query file and the indexed license and rule texts. The process
prioritizes accuracy over speed.

Ideally, we want to find the best alignment possible between two texts so we know
exactly where they match: the scanned text and one or more of the many license texts.
We settle for good alignments rather than optimal alignments by still returning
accurate and correct matches in a reasonable amount of time.

Correctness is essential but efficiency matters too: both in terms of speed
and memory usage. One key to efficient matching is to process whole words
instead of characters, and to represent words internally using integers
rather than strings.


Rules and licenses
^^^^^^^^^^^^^^^^^^

The detection uses an index of reference license texts and along with a set
of "rules" that are common notices or mentions of these licenses. One
challenge in detection is that a license reference can be very short as in
"this is GPL" or very long as a full license text for the GPLv3. To cope
with this, we use different matching strategies and also compute both the
resemblance and containment of the matched texts.


Words as integers
^^^^^^^^^^^^^^^^^

A dictionary that maps words to a unique integer is used to transform a
scanned text "query" words, as well as the words in the indexed license
texts and rules, to numbers. This is possible because we have a limited
number of words across all the license texts (about 15K). We further assign
these ids to words such that very common words have a low id, while less
frequent, more distinctive words have a higher id. A thresholds is defined
for this ids range such that very common words below the threshold cannot,
by themselves, form a valid license text or reference.

Once that mapping is applied, the detection process deals only with integers in two
dimensions:

- the token ids (and whether they are in the high or low range).
- their positions in the query (qpos) and the indexed rule (ipos).

We also use an integer id for a rule.

From this point, all operations are performed on lists, arrays or sets of
integers in defined ranges.

Matches are reduced to sets of integers referred to as "Spans":

- matched positions on the query side
- matched positions on the index side

By using integers within known ranges throughout the process, several
operations are simplified to comparisons and intersections of integers,
integer sets, or lists. These operations are faster and more easily
optimized.

With integers, we use less memory:

- we can use arrays of unsigned 16 bits ints that store each number on two bytes
  rather than bigger lists of ints.
- we can replace dictionaries by sparse lists or arrays where the index is an integer key.
- we can use succinct, bit level representations (e.g. bitmaps) of integer sets.

Smaller data structures also mean faster processing, as processors need to move
less data in memory.

With integers, we can be faster:

- a dict key lookup is slower than a list of array index lookup.
- processing large list of small structures is faster (such as bitmaps, etc).
- we can leverage libraries that speed up integer set operations.


Common/junk tokens
^^^^^^^^^^^^^^^^^^

The quality and speed of detection is supported by classifying each word as
either good/discriminant or common/junk. Junk tokens are either very
frequent of tokens or ones that, even combined, cannot form a valid license
mention or notice. When a numeric id is assigned to a token during initial
indexing, junk tokens are assigned a lower id than good tokens. These are
referred to as low (junk) tokens and high (good) tokens.


Query processing
^^^^^^^^^^^^^^^^

When a file is scanned, it is first converted to a query object which is a list of
integer token ids. A query is further broken down in slices (a.k.a. query runs) based
on heuristics.

While the query is processed, a set of matched and matchable positions for
high and low token ids is kept to keep track what is left to do in
matching.


Matching pipeline
^^^^^^^^^^^^^^^^^

The matching pipeline consist of:

- we start by matching the whole query at once against hashes on the whole
  text looked up in a mapping from hash to license rule. The process exits
  if a match is found.

- then we match the whole query for exact matches using an automaton (Aho-Corasick).
  The process exits if a match is found.

- then each query run is processed in sequence:

  - the best potentially matching rules are found with two rounds of approximate
    "set" matching. This set matching uses a "bag of words" approach where the
    scanned text is transformed in a vector of integers based on the presence or
    absence of a word. It is then compared against the index of vectors. This is similar
    conceptually to a traditional inverted index search for information retrieval.
    The best matches are ranked using a resemblance and containment comparison. A
    second round is performed on the best matches using multisets which are set where
    the number of occurrence of each word is also taken into account. The best matches
    are ranked again using a resemblance and containment comparison and is more
    accurate than the previous set matching.

  - using the ranked potential candidate matches from the two previous rounds, we
    then perform a pair-wise local sequence alignment between these candidates and
    the query run. This sequence alignment is essentially an optimized diff working
    on integer sequences and takes advantage of the fact that some very frequent
    words are considered less discriminant: this speeds up the sequence alignment
    significantly. The number of multiple local sequence alignments that are required
    in this step is also made much smaller by the pre-matching done using sets.

- finally all the collected matches are merged, refined and filtered to
  yield the final results. The merging considers the ressemblance,
  containment and overlap between scanned texts and the matched texts and
  several secondary factors. Filtering is based on the density and length
  of matches as well as the number of good or frequent tokens matched.
  Lastly, each match receives a score calculated based on the sum of the
  underlying match scores, weighted by the length of the match relative to
  the overall detection length. Optionally we can also collect the exact
  matched texts and identify which portions were not matched for each
  instance.


Comparison with other tools approaches
--------------------------------------

Most tools use regular expressions. The problem is that creating these expressions
requires a lot of intimate knowledge of the data set and the relation between each
license texts. The maintenance effort is high. And regex matches typically need a
complex second pass of disambiguation for similar matches.

Some tools use an index of pre-defined sentences and match these as regex and then
reassemble possible matches. They tend to suffer from the same issues as a pure regex
based approach and require an intimate knowledge of the license texts and how they
relate to each other.

Some tools use pair-wise comparisons like ScanCode. But in doing so, they
usually perform poorly because a multiple local sequence alignment is an
expensisve computation. Say you scan 1000 files and you have 1000 reference
texts. You would need to perform multiple rounds of comparison ,1000 per
files, resulting in the equivalent of 100 million diffs or more to process
all files. Because of the progressive matching pipeline used in ScanCode,
sequence alignments are often unnecessary in common cases, and when they
are required, only a few are needed.

See also this list: https://wiki.debian.org/CopyrightReviewTools
