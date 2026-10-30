================
ScanCode Toolkit
================

ScanCode Toolkit is a set of code scanning tools that detect the origin (copyrights), license and vulnerabilities of code,
packages and dependencies in a codebase. ScanCode Toolkit is an `AboutCode project <https://aboutcode.org>`_.

Why Use ScanCode Toolkit?
=========================

ScanCode Toolkit is the leading tool in scanning depth and accuracy,
used by hundreds of software teams. You can use ScanCode Toolkit
as a command line tool or as a library.

Getting Started
===============

Instructions to get you up and running on your local machine are at `Getting Started <https://scancode-toolkit.readthedocs.io/en/stable/getting-started/index.html>`_

The ScanCode Toolkit documentation also provides:

- prerequisites for installing the software.
- instructions guiding you to start scanning code.
- a comprehensive guide to the command line options.
- tutorials that provide hands-on guidance to ScanCode features.
- how to expand ScanCode Licenses and Detection Rules with your own data.
- how to generate Attribution from a ScanCode scan.
- guidelines for contributing to code development.

Build and tests status
======================

We run 30,000+ tests on each commit on multiple CIs to ensure a good platform
compabitility with multiple versions of Windows, Linux and macOS.

+------------+--------------+-------------------------+----------------------------+
| **Azure**  | **RTD Build**| **GitHub actions Docs** | **GitHub actions Release** |
+============+==============+=========================+============================+
|  |azure|   | |docs-rtd|   |  |docs-github-actions|  |  |release-github-actions|  |
+------------+--------------+-------------------------+----------------------------+

Benefits of ScanCode
====================

- ScanCode is heavily **tested** with an automated test suite of over **30,000 tests**.

- ScanCode is **used by several projects and organizations** such as
  the `Eclipse Foundation <https://www.eclipse.org>`_,
  `OpenEmbedded.org <https://www.openembedded.org>`_,
  the `FSFE <https://www.fsfe.org>`_,
  the `FSF <https://www.fsf.org>`_,
  `OSS Review Toolkit <http://oss-review-toolkit.org>`_,
  `ClearlyDefined.io <https://clearlydefined.io/>`_,
  `RedHat Fabric8 analytics <https://github.com/fabric8-analytics>`_,
  and many more.

- You can also organize and run ScanCode server-side with the
  companion `ScanCode.io web app <https://github.com/aboutcode-org/scancode.io>`_
  to organize and store multiple scan projects including scripted scanning pipelines.

- As a **standalone command-line tool**, ScanCode is **easy to install**, run,
  and embed in your CI/CD processing pipeline.
  It runs on **Windows, macOS, and Linux**.

- ScanCode detects licenses, copyrights, package manifests, direct dependencies,
  and more both in **source code** and **binary** files and is considered as the
  best-in-class and reference tool in this domain, re-used as the core tools for
  software composition data collection by several open source tools.

- ScanCode provides the **most accurate license detection engine** and does a
  full comparison (also known as diff or red line comparison) between a database
  of license texts and your code instead of relying only on approximate regex
  patterns or probabilistic search, edit distance or machine learning.

- Written in Python, ScanCode is **easy to extend with plugins** to contribute
  new and improved scanners, data summarization, package manifest parsers, and
  new outputs.

- You can save your scan results as **JSON, YAML, HTML, CycloneDX or SPDX** or
  even create your own format with Jinja templates.

- ScanCode can process packages, build manifest and lockfile formats to collect
  Package URLs and extract metadata. See all available `package parsers
  <https://scancode-toolkit.readthedocs.io/en/stable/reference/index.html>`_
  for the exhaustive list.

Support
=======

If you have a specific problem, suggestion or bug, please submit a
`GitHub issue <https://github.com/aboutcode-org/scancode-toolkit/issues>`_.

For quick questions or socializing, join the AboutCode community discussions on `Slack <https://join.slack.com/t/aboutcode-org/shared_invite/zt-3li3bfs78-mmtKG0Qhv~G2dSlNCZW2pA>`_.

Interested in commercial suppport? Contact the `AboutCode team <mailto:hello@aboutcode.org>`_.

License
=======

* `Apache-2.0 <apache-2.0.LICENSE>`_ is the overall license.
* `CC-BY-4.0 <cc-by-4.0.LICENSE>`_ applies to reference datasets.
* There are multiple secondary permissive or copyleft licenses (LGPL, MIT,
  BSD, GPL 2/3, etc.) for third-party components and test suite code and data.

See the `NOTICE file <NOTICE>`_ and the `.ABOUT files <https://github.com/search?q=repo%3Aaboutcode-org%2Fscancode-toolkit+path%3A*.ABOUT&type=code>`_ that document the origin and license of
the third-party code used in ScanCode for more details.

.. |azure| image:: https://dev.azure.com/nexB/scancode-toolkit/_apis/build/status/nexB.scancode-toolkit?branchName=develop
    :target: https://dev.azure.com/nexB/scancode-toolkit/_build/latest?definitionId=1&branchName=develop
    :alt: Azure tests status (Linux, macOS, Windows)

.. |docs-rtd| image:: https://readthedocs.org/projects/scancode-toolkit/badge/?version=latest
    :target: https://scancode-toolkit.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |docs-github-actions| image:: https://github.com/nexB/scancode-toolkit/actions/workflows/docs-ci.yml/badge.svg?branch=develop
    :target: https://github.com/nexB/scancode-toolkit/actions/workflows/docs-ci.yml
    :alt: Documentation Tests

.. |release-github-actions| image:: https://github.com/nexB/scancode-toolkit/actions/workflows/scancode-release.yml/badge.svg?event=push
    :target: https://github.com/nexB/scancode-toolkit/actions/workflows/scancode-release.yml
    :alt: Release tests


Acknowledgements, Funding, Support and Sponsoring
=================================================

This project is funded, supported and sponsored by:

- Generous support and contributions from users like you!
- the European Commission NGI programme
- the NLnet Foundation
- the Swiss State Secretariat for Education, Research and Innovation (SERI)
- Google, including the Google Summer of Code and the Google Seasons of Doc programmes
- Mercedes-Benz Group
- Microsoft and Microsoft Azure
- AboutCode ASBL
- nexB Inc.


|europa|   |dgconnect|

|ngi|   |nlnet|

|aboutcode|  |nexb|


This project was funded through the NGI0 Discovery Fund, a fund established by NLnet with financial
support from the European Commission's Next Generation Internet programme, under the aegis of DG
Communications Networks, Content and Technology under grant agreement No 825322.

|ngidiscovery| https://nlnet.nl/project/vulnerabilitydatabase/


This project was funded through the NGI0 Entrust Fund, a fund established by NLnet with financial
support from the European Commission's Next Generation Internet programme, under the aegis of DG
Communications Networks, Content and Technology under grant agreement No 101069594.

|ngizeroentrust| https://nlnet.nl/project/Back2source/


This project was funded through the NGI0 Core Fund, a fund established by NLnet with financial
support from the European Commission's Next Generation Internet programme, under the aegis of DG
Communications Networks, Content and Technology under grant agreement No 101092990.

|ngizerocore| https://nlnet.nl/project/Back2source-next/


This project was funded through the NGI0 Core Fund, a fund established by NLnet with financial
support from the European Commission's Next Generation Internet programme, under the aegis of DG
Communications Networks, Content and Technology under grant agreement No 101092990.

|ngizerocore| https://nlnet.nl/project/FastScan/


This project was funded through the NGI0 Commons Fund, a fund established by NLnet with financial
support from the European Commission's Next Generation Internet programme, under the aegis of DG
Communications Networks, Content and Technology under grant agreement No 101135429. Additional
funding is made available by the Swiss State Secretariat for Education, Research and Innovation
(SERI).

|ngizerocommons| |swiss| https://nlnet.nl/project/MassiveFOSSscan/

This project was funded through the NGI0 Entrust Fund, a fund established by NLnet with financial
support from the European Commission's Next Generation Internet programme, under the aegis of DG
Communications Networks, Content and Technology under grant agreement No 101069594.

|ngizeroentrust| https://nlnet.nl/project/purl2sym/


.. |nlnet| image:: https://nlnet.nl/logo/banner.png
    :target: https://nlnet.nl
    :height: 50
    :alt: NLnet foundation logo

.. |ngi| image:: https://ngi.eu/wp-content/uploads/thegem-logos/logo_8269bc6efcf731d34b6385775d76511d_1x.png
    :target: https://ngi.eu35
    :height: 50
    :alt: NGI logo

.. |nexb| image:: https://nexb.com/wp-content/uploads/2022/04/nexB.svg
    :target: https://nexb.com
    :height: 30
    :alt: nexB logo

.. |europa| image:: https://ngi.eu/wp-content/uploads/sites/77/2017/10/bandiera_stelle.png
    :target: http://ec.europa.eu/index_en.htm
    :height: 40
    :alt: Europa logo

.. |aboutcode| image:: https://aboutcode.org/wp-content/uploads/2023/10/AboutCode.svg
    :target: https://aboutcode.org/
    :height: 30
    :alt: AboutCode logo

.. |swiss| image:: https://www.sbfi.admin.ch/sbfi/en/_jcr_content/logo/image.imagespooler.png/1493119032540/logo.png
    :target: https://www.sbfi.admin.ch/sbfi/en/home/seri/seri.html
    :height: 40
    :alt: Swiss logo

.. |dgconnect| image:: https://commission.europa.eu/themes/contrib/oe_theme/dist/ec/images/logo/positive/logo-ec--en.svg
    :target: https://commission.europa.eu/about-european-commission/departments-and-executive-agencies/communications-networks-content-and-technology_en
    :height: 40
    :alt: EC DG Connect logo

.. |ngizerocore| image:: https://nlnet.nl/image/logos/NGI0_tag.svg
    :target: https://nlnet.nl/core
    :height: 40
    :alt: NGI Zero Core Logo

.. |ngizerocommons| image:: https://nlnet.nl/image/logos/NGI0_tag.svg
    :target: https://nlnet.nl/commonsfund/
    :height: 40
    :alt: NGI Zero Commons Logo

.. |ngizeropet| image:: https://nlnet.nl/image/logos/NGI0PET_tag.svg
    :target: https://nlnet.nl/PET
    :height: 40
    :alt: NGI Zero PET logo

.. |ngizeroentrust| image:: https://nlnet.nl/image/logos/NGI0Entrust_tag.svg
    :target: https://nlnet.nl/entrust
    :height: 38
    :alt: NGI Zero Entrust logo

.. |ngiassure| image:: https://nlnet.nl/image/logos/NGIAssure_tag.svg
    :target: https://nlnet.nl/image/logos/NGIAssure_tag.svg
    :height: 32
    :alt: NGI Assure logo

.. |ngidiscovery| image:: https://nlnet.nl/image/logos/NGI0Discovery_tag.svg
    :target: https://nlnet.nl/discovery/
    :height: 40
    :alt: NGI Discovery logo

**End of ScanCode Toolkit README**
