Scan Options 
============

.. _scan_options_min_coverage:

--min-coverage COVERAGE, -C COVERAGE
------------------------------------

**Purpose:** A quality filter used to filter license/copyright detection matches.

**Syntax:**
  ``--min-coverage 60``
  ``scancode -C 80 /path/to/code``

This filter limits the license and copyright detections by only reporting detections 
on reference rules that contain at least `COVERAGE%` of the reference text as found 
in that rule.

**How the filter works:** 
Every rule includes a reference text (for example, 500 characters) so, if the match 
found was 300 characters, this would represent a 'coverage' of 60%.

``--min-coverage 60`` = **INCLUDED**

``--min-coverage 70`` = **EXCLUDED** (300/500 = 60% < 70%)

**Default:** ``0`` (reports all matches regardless of coverage)
**Valid range:** ``0-100``

**Use Cases:**

**1. Reduce "Noise" (Recommended)**
  ``scancode --license --copyright --min-coverage 70 ./src/``

  Limits false positives while maintaining high-confidence detections.

**2. Strict analysis**
  ``scancode --license --min-coverage 85 ./proprietary/``

  Only highest confidence license matches for legal review.

**3. Debugging all matches**
  ``scancode --license --min-coverage 0 ./src/``

  Shows everything (default behavior).

**Output Comparison:**

**No Filter (noisy):**
::
  license  mit       45%  23/51  ./file.js
  license  mit       28%  14/51  ./file.js
  license  apache-2.0 12%  8/67  ./file.js

**With --min-coverage 70 (clean):**
::
  license  mit       85%  43/51  ./file.js

**Pro tip:** Start with ``70%`` and adjust based on false positive rate.

**Performance:** Minimal overhead - filtering occurs post-detection.
