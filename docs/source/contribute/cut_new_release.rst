.. _release_process:

How to cut a new release
========================

Update version
--------------

- Bump version to update major, minor or patch version in ``setup.cfg``
  ``setup-mini.cfg`` and ``src/scancode_config.py``. Note that this is SemVer,
  though we used CalVer previously, we have switched back to SemVer.

- If scancode output data format is changed, increment manually the major,
  minor or patch version to bump the version in ``src/scancode_config.py``.
  Note that this is SemVer.

See our :ref:``versioning`` for more details.

Tag and publish
---------------

- Changes for a release should also be pushed to a branch and a Pull
  Request should be created for it, for review.

- Update the CHANGELOG.rst with detailed documentation of updates
  and API/CLI option changes, or any significant changes.

- Commit these changes and push changes to develop (here we use an
  example tag ``v1.6.1``):

    - ``git commit -s``
    - ``git push --set-upstream origin release-prep-v1.6.1``

- Merge this ``release-prep-v1.6.1`` branch in develop after review approval
  and tag the release:

    - ``git tag -a v1.6.1 -m "Release v1.6.1"``
    - ``git push --set-upstream origin release-prep-v1.6.1``
    - ``git push --set-upstream origin v1.6.1``

Automated Release Process
-------------------------

- We have an `automated release script <https://github.com/aboutcode-org/scancode-toolkit/actions/workflows/scancode-release.yml>`_
  triggered by a pushed tag, where jobs run to:

  - Build pypi wheels and sdist archives
  - Build app release archives for linux/mac/windows
  - This happens for all supported python versions
  - Test these wheels and app archives in linux/mac/windows for all supported
    versions of python
  - Create a GitHub release (draft by default) with all wheels, sdists and app archives
    (for all os/python combinations)
  - Upload sdists and wheels (all python versions) and publish a release
    (This won't be a stable release for beta/release-candidate tags)

- Populate the draft GitHub release by clicking the ``Generate Release Notes`` button
  and this pre-populates the release notes with PRs and contributors.

- Add more details to the release notes talking about the key features and changes in the
  release.

- Publish the release on GitHub
  (Note the ``Set as a pre-release`` vs ``Set as the latest release`` checkboxes)

- Announce in public channels and chats about the release

- Do test the release archives yourself.
