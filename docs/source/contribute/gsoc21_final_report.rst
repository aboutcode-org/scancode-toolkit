Google Summer of Code 2021 Final report
=========================================


Organisation - `AboutCode <https://www.aboutcode.org/>`_
---------------------------------------------------------

Akanksha Garg <akanksha.garg2k@gmail.com>

`GITHUB <https://github.com/akugarg>`_


Project: Detect Unknown Licenses and Indirect License References in ScanCode
----------------------------------------------------------------------------

`ScanCode-Toolkit <https://github.com/aboutcode-org/scancode-toolkit>`_

`Project Link <https://summerofcode.withgoogle.com/archive/2021/projects/6229596998991872>`_

`Proposal <https://docs.google.com/document/d/1Dp0Hgk38RIMwITTiS-kqfikpkHRi2rjtkotA9CLw8j0/edit?usp=sharing>`_


Description
------------

The main motive of this project was to improve license detection of unknown licenses
and follow references to indirect license references in ScanCode-Toolkit

**Improvement in the License Data Model Definition**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Unknown Licenses are the ones which are matched to a license rule tagged with 'unknown' license
key. Since these are some of the 'special' licenses , reporting them with special attributes
will provide more clarification. Now unknown licenses are tagged with a new flag **"is_unknown"**
to identify them beyond just the naming convention of having "unknown" as part of their name.

Rules that match at least one unknown license have a flag **"has_unknown"** set
in the returned match results.

`nexB/scancode-toolkit#2548 <https://github.com/aboutcode-org/scancode-toolkit/pull/2548>`_

**Reporting known and Unknown licenses separately**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We considered having a separate section for of scan results to report 'unknown licenses'
separately and not mixed with main license detection results. But after implementing
a separate section for unknown ones ,it doesn't seem to be good idea to have currently.

`nexB/scancode-toolkit#2578 <https://github.com/aboutcode-org/scancode-toolkit/pull/2578>`_

**Follow License References to another file**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some license references such as "see license in file LICENSE.txt" e.g. mentions to look
for license details in another file are reported as unknown license references and
we could instead follow the referenced file to find what was detected there. The approach
was to use already contained attribute ``refrenced_filenames`` in license RULE data files.
Since this was a ``process_codebase`` step in scan plugin , it was needed that our API function
should return ``refrenced_filenames`` to keep track of these files corresponding to licenses
detected. This was tracked in -

`nexB/scancode-toolkit#2632 <https://github.com/aboutcode-org/scancode-toolkit/pull/2632>`_

The ```process_codebase``` step is tracked in -

`nexB/scancode-toolkit#2616 <https://github.com/aboutcode-org/scancode-toolkit/pull/2616>`_

**Improve license detection of Unknown Licenses**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The approach was to use index of n-grams for detecting unknowns besides having our actual
detection of "unknown" license rules. Firstly matches were filtered after running our normal
procedure of license detection and the remaining spans are run through a automaton index
containing n-grams from all regular license texts and rules. This is tracked in -

`nexB/scancode-toolkit#2592 <https://github.com/aboutcode-org/scancode-toolkit/pull/2592>`_

**Addition of some new Licenses**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There were some licenses that were not present in ScanCode-Toolkit as for now.
They have been added now.

`nexB/scancode-toolkit#2625 <https://github.com/aboutcode-org/scancode-toolkit/pull/2625>`_


Pre-GSoC
--------

**Contributions**

- `nexB/scancode-toolkit#2423 <https://github.com/aboutcode-org/scancode-toolkit/pull/2423>`_
- `nexB/scancode-toolkit#2473 <https://github.com/aboutcode-org/scancode-toolkit/pull/2473>`_
- `nexB/scancode-toolkit#2464 <https://github.com/aboutcode-org/scancode-toolkit/pull/2464>`_
- `nexB/scancode-toolkit#2381 <https://github.com/aboutcode-org/scancode-toolkit/pull/2381>`_

I’ve had a wonderful summer during these 10 weeks journey and have learned plenty of things.
I am thankful to Google and Aboutcode for giving me this opportunity to work with such an amazing
community. I am fortunate to have mentors `Philippe Ombredanne <https://github.com/pombredanne>`_
and `Ayan Sinha Mahapatra <https://github.com/AyanSinhaMahapatra>`_ who helped me a lot throughout
my GSoC project and provided constant support.

