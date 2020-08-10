*Before generating requirement tools and uploading asset make sure you've installed the prerequisites properly. This mainly :*
  - pip-tools
  - github-release-retry

Instruction for generating requirement tools:
=============================================
- For this you must run on your terminal:
 
  ``pip pip install -r etc/scripts/req_tools.txt``

- Then run ``python etc/scripts/freeze_and_update_reqs.py --help`` on terminal

From this you get the guidelines how to generate requirement tools.

Instruction for uploading assets:
=================================

- Just run ``python etc/scripts/github_release.py --help``
- From this you get the guidelines how to upload asset to github repositotory as an asset.

This directory contains miscellaneous scripts of some use with ScanCode.

- json2csv: convert a scan JSON to a CSV.
