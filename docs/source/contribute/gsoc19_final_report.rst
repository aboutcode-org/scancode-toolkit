Google Summer of Code 2019 - Final report
=========================================

Project: **scancode-toolkit** to Python 3
-----------------------------------------

**Owner:** `Abhishek Kumar <https://github.com/Abhishek-Dev09>`_

**Mentor:** `Philippe Ombredanne <https://github.com/pombredanne>`_

Overview
--------

**Problem:** Since Python 2.7 will retire in few months and will not be maintained any longer.

**Solution:** `Scancode <https://github.com/nexB/scancode-toolkit/>`__ needs to be ported to
python 3 and all test suites must pass on both version of Python. The main difference that
makes Python 3 better than Python 2.x is that the support for unicode is greatly improved in
Python 3. This will also be useful for scancode as scancode has users in more than 100 languages
and it's easy to translate strings from unicode to other languages.

**Objective**: To make scancode-toolkit installable on on Python 3.6 and higher, as presently it
installs with Python 2.7 only.

Implementation
--------------

- It was started in development mode(editable mode) and then it was moved to work in virtual
  environments.
- I have worked module by module according to the order of hierarchy of modules. For example :All
  module is dependent on commoncode, so it must be ported first. In this way we have created the
  Porting order:

   1.  commoncode
   2.  plugincode
   3.  typecode
   4.  extractcode
   5.  textcode
   6.  scancode basics (some tests are integration tests and will have to wait to be ported)
   7.  formattedcode, starting with JSON (some tests are integration tests and will have to wait
       to be ported)
   8.  cluecode
   9.  licensedcode
   10. packagedcode (depends on licensecode)
   11. summarycode
   12. fixup the remaining bits and tests

After porting each module, I have marked these modules as ported ``scanpy3`` with help of
**conffest** plugin (created by `@pombredanne <https://github.com/pombredanne>`_). **Conffest**
plugin is heart of this project. Without this, it was very difficult to do. Dependencies was fixed
at the time of porting the module where it was used.

Challenging part of Project
---------------------------

It is very difficult to deal with paths on different operating systems.The issue is around
macOS/Windows/Linux. The first two OS handle unicode paths comfortably on Python 2 and 3 but not
completely on macOS Mojave because its filesystem encoding is APFS. Linux paths are bytes and
os.listdir is broken on Python 2. As a result you can only sanely handle Linux paths as bytes
on Python 2. But on Python 3 path seems to be corrected as ``unicode`` on Linux.

For more details visit here :

- https://vstinner.github.io/painful-history-python-filesystem-encoding.html
- `jaraco/path.py#130 <https://github.com/jaraco/path.py/issues/130>`__

We came with various Solution:

- To use pathlib which generally handle paths correctly across platforms. And for backports we use
  pathlib 2. But this solution also fails because pathlib 2 does not work as expected wrt unicode
  vs bytes. And os.listdir also doesn't work properly.

- To use `path.py <https://pypi.org/project/path.py/>`__ which handles the paths across all the
  platforms even on macOS Mojave .

- Use ``bytes`` on linux and python 3 and ``unicode`` everywhere.

We choose the third solution because it is most fundamental and simple and easy to use.

Project was tracked in this ticket `nexB/scancode-toolkit#295 <https://github.com/nexB/scancode-toolkit/issues/295>`__

**Project link :** `Port Scancode to Python 3 <https://summerofcode.withgoogle.com/organizations/6118953540124672/>`__

..
    [Org Link] https://summerofcode.withgoogle.com/organizations/6118953540124672/
    [Project Link] https://summerofcode.withgoogle.com/projects/#5969926387400704

**My contribution :** `List of Commits <https://github.com/nexB/scancode-toolkit/commits?author=Abhishek-Dev09>`__

**Note :** Please give your feedback `here <https://github.com/nexB/scancode-toolkit/issues/295>`_

Outcome
-------

Now we have liftoff on Python 3 . We are able to run basic scans without errors on develop branch.
You check it by running ``scancode -clipeu samples/ --json-pp - -n4`` .

At last I would like to thanks my Mentor **@pombredanne** aka
`Philippe Ombredanne <https://github.com/pombredanne>`__ . He has helped lot in completing this
project. He is very supportive and responsive. I have learned a lot from him. By his encouragement
and motivation, I am very improving day by day, building and developing my skills. I have completed
all the tasks that were in the scope of this GSoC project.
