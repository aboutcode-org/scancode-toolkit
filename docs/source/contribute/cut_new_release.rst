How to cut a new release:
=========================

- run bumpversion with major, minor or patch to bump the version in:

    - ``src/scancode/__init__.py``
    - ``setup.py``
    - Update the CHANGELOG.rst

- commit changes and push changes to develop:

    - ``git commit -m "commit message"``
    - ``git push --set-upstream origin develop``

- merge develop branch in master and tag the release.

    - ``git checkout master``
    - ``git merge develop``
    - ``git tag -a v1.6.1 -m "Release v1.6.1"``
    - ``git push --set-upstream origin master``
    - ``git push --set-upstream origin v1.6.1``

- draft a new release in GitHub, using the previous release blurb as a base. Highlight new and
  noteworthy changes from the CHANGELOG.rst.

- run ``etc/release/release.sh`` locally.

- upload the release archives created in the ``dist/`` directory to the GitHub release page.

- save the release as a draft. Use the previous release notes to create notes in the same style.
  Ensure that the link to third-party source code is present.

- test the downloads.

- publish the release on GitHub

- then build and publish the released wheel on Pypi. For this you need your own Pypi credentials
  (and get authorized to publish Pypi release: ask @pombredanne) and you need to have the ``twine``
  package installed and configured.

    - Build a ``.whl`` with ``python setup.py bdist_wheel``
    - Run twine with ``twine upload dist/<path to the built wheel>``
    - Once uploaded check the published release at https://pypi.python.org/pypi/scancode-toolkit/
    - Then create a new fresh local virtualenv and test the wheel installation with:
      ``pip install scancode-toolkit``
