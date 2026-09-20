#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json
import logging
import os

from pathlib import Path

from packagedcode import models

"""
Handle pip wheel cache directories with origin.json metadata.

When pip downloads wheels, it caches them in .cache/pip/wheels/ with an
origin.json file containing metadata about the original download URL.

See: https://pip.pypa.io/en/latest/reference/pip_install/#caching
"""

TRACE = os.environ.get('SCANCODE_DEBUG_PACKAGE', False)

logger = logging.getLogger(__name__)


def parse_origin_json(file_path):
    """
    Parse a pip cache origin.json file and extract package metadata.

    Returns a dictionary with:
        - type: "pypi"
        - download_url: extracted URL from origin.json

    Returns None if the file is missing, invalid, or does not contain required fields.

    Args:
        file_path: Path to origin.json file

    Example:
        >>> result = parse_origin_json("/path/to/origin.json")
        >>> if result:
        ...     print(result['download_url'])
    """
    try:
        origin_file = Path(file_path)

        # Check if file exists
        if not origin_file.exists():
            if TRACE:
                logger.debug(f"origin.json not found: {file_path}")
            return None

        # Read and parse JSON
        with open(origin_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract URL from origin.json
        url = data.get('url')
        if not url:
            if TRACE:
                logger.debug(f"No 'url' field found in: {file_path}")
            return None

        return {
            'type': 'pypi',
            'download_url': url,
        }

    except (json.JSONDecodeError, IOError, OSError) as e:
        # Handle missing file, read errors, or invalid JSON gracefully
        if TRACE:
            logger.debug(f"Error parsing origin.json at {file_path}: {type(e).__name__}: {e}")
        return None


def parse_pip_cache(location):
    """
    Parse a pip cache directory and extract package metadata.

    Takes a directory path (e.g., .cache/pip/wheels/ab/cdef123/) and looks for
    an origin.json file inside it. Returns parsed metadata or None.

    Args:
        location: Path to a pip cache directory

    Returns:
        Dictionary with type and download_url, or None if not found/invalid
    """
    try:
        loc_path = Path(location)
        origin_json_path = loc_path / 'origin.json'
        return parse_origin_json(str(origin_json_path))
    except (OSError, ValueError):
        return None


def detect_pip_cache_directory(location):
    """
    Check if a directory contains an origin.json file indicating a pip cache.

    Args:
        location: Path to a directory

    Returns:
        True if location is a directory and contains origin.json, False otherwise
    """
    try:
        loc_path = Path(location)
        if loc_path.is_dir():
            origin_json = loc_path / 'origin.json'
            return origin_json.exists()
    except (OSError, ValueError):
        pass
    return False


class PipCacheOriginJsonHandler(models.DatafileHandler):
    """
    Detect and parse pip wheel cache directories containing origin.json metadata.

    These are typically found in:
    - ~/.cache/pip/wheels/<version>/<first_two_chars_of_hash>/<rest_of_hash>/
    - All subdirectories contain .whl files and an origin.json with metadata
    """

    datasource_id = 'pip_cache_origin_json'
    datasource_type = 'app'

    default_package_type = 'pypi'
    default_primary_language = 'Python'

    # This handler works on directories, not individual files
    path_patterns = (
        '*/origin.json',
    )

    description = 'pip cache origin.json'
    documentation_url = 'https://pip.pypa.io/en/latest/reference/pip_install/#caching'

    @classmethod
    def is_datafile(cls, location, filetypes=tuple(), _bare_filename=False):
        """
        Return True if location is an origin.json file in a pip cache directory.
        """
        # Check if this is an origin.json file path
        if not location:
            return False

        loc_name = os.path.basename(location)
        if loc_name != 'origin.json':
            return False

        # For testing with bare filenames (no real files)
        if _bare_filename:
            return True

        # Verify it's a real file
        try:
            if os.path.isfile(location):
                return True
        except (OSError, ValueError):
            pass

        return False

    @classmethod
    def parse(cls, location, package_only=False):
        """
        Parse a pip cache origin.json file and yield PackageData.

        Args:
            location: Path to origin.json file
            package_only: If True, only return package metadata (ignored for this handler)

        Yields:
            PackageData: A single PackageData object with parsed metadata
        """
        try:
            origin_data = parse_origin_json(location)

            if not origin_data:
                # No valid data extracted - yield nothing or handle gracefully
                return

            # Extract the download URL to derive package name/version if possible
            download_url = origin_data.get('download_url', '')

            # Try to extract package info from URL
            # URL format is typically: https://files.pythonhosted.org/packages/.../package-version.tar.gz
            package_name = None
            package_version = None

            if download_url:
                # Extract filename from URL
                url_path = download_url.split('/')[-1]
                # Remove extension (.tar.gz, .tar.bz2, .zip, etc.)
                for ext in ['.tar.gz', '.tar.bz2', '.tar.xz', '.zip', '.whl']:
                    if url_path.endswith(ext):
                        url_path = url_path[:-len(ext)]
                        break

                # Try to split name and version (format: name-version)
                # This is a best-effort approach as names can contain hyphens
                if url_path:
                    parts = url_path.rsplit('-', 1)
                    if len(parts) == 2:
                        package_name, package_version = parts
                    else:
                        package_name = url_path

            # Create PackageData
            package_data = models.PackageData(
                type=origin_data['type'],
                name=package_name,
                version=package_version,
                download_location=download_url,
                extra_data={
                    'origin_json_path': location,
                    'pip_cache_url': download_url,
                },
            )

            if TRACE:
                logger.debug(
                    f"Parsed pip cache: name={package_name}, version={package_version}, "
                    f"url={download_url}"
                )

            yield package_data

        except Exception as e:
            # Log but don't crash on unexpected errors
            if TRACE:
                logger.debug(f"Error parsing pip cache {location}: {type(e).__name__}: {e}")
            return


class PipCacheWheelHandler(models.DatafileHandler):
    """
    Detect and parse pip wheel cache directories that may contain .whl files.

    This handler complements PipCacheOriginJsonHandler by detecting .whl files
    in pip cache directories and linking them to their origin.json metadata.
    """

    datasource_id = 'pip_cache_wheel'
    datasource_type = 'app'

    default_package_type = 'pypi'
    default_primary_language = 'Python'

    path_patterns = (
        '*/.whl',  # wheels in pip cache typically have .whl extension
    )

    is_lockfile = False
    description = 'pip cache wheel file'
    documentation_url = 'https://pip.pypa.io/en/latest/reference/pip_install/#caching'

    @classmethod
    def is_datafile(cls, location, filetypes=tuple(), _bare_filename=False):
        """
        Return True if location is a .whl file (wheel package).
        """
        if not location:
            return False

        # Check for .whl extension
        if not location.lower().endswith('.whl'):
            return False

        if _bare_filename:
            return True

        try:
            # Verify it's a real file
            if os.path.isfile(location):
                return True
        except (OSError, ValueError):
            pass

        return False

    @classmethod
    def parse(cls, location, package_only=False):
        """
        Parse a .whl file in a pip cache and yield PackageData.

        This attempts to find and use the corresponding origin.json if available.

        Args:
            location: Path to a .whl file
            package_only: If True, only return package metadata

        Yields:
            PackageData: Package data from wheel metadata or origin.json
        """
        try:
            # Get the directory containing this wheel
            wheel_dir = os.path.dirname(location)
            origin_json_path = os.path.join(wheel_dir, 'origin.json')

            # Try to get metadata from origin.json
            origin_data = parse_origin_json(origin_json_path)

            if origin_data:
                # Extract wheel filename without extension
                wheel_filename = os.path.basename(location)
                wheel_name = wheel_filename[:-4]  # Remove .whl extension

                # Parse wheel filename (format: {distribution}-{version}(-{build})?-{python}-{abi}-{platform}.whl)
                # Simplified parsing
                parts = wheel_name.split('-')
                if len(parts) >= 2:
                    package_name = parts[0]
                    package_version = parts[1]
                else:
                    package_name = wheel_name
                    package_version = None

                package_data = models.PackageData(
                    type='pypi',
                    name=package_name,
                    version=package_version,
                    download_location=origin_data.get('download_url'),
                    extra_data={
                        'wheel_file': location,
                        'origin_json_path': origin_json_path,
                    },
                )

                if TRACE:
                    logger.debug(
                        f"Parsed pip cache wheel: name={package_name}, version={package_version}"
                    )

                yield package_data

        except Exception as e:
            if TRACE:
                logger.debug(f"Error parsing pip cache wheel {location}: {type(e).__name__}: {e}")
            return
