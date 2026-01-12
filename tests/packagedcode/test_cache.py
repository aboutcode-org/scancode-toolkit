#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import fnmatch
import os

from packagedcode import cache
from commoncode.fileutils import as_posixpath

from packages_test_utils import PackageTester


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestMultiregexPatterns(PackageTester):
    test_data_dir = TEST_DATA_DIR

    def test_build_mappings_and_multiregex_patterns_works(self):
        from packagedcode.about import AboutFileHandler

        multiregexes = cache.build_mappings_and_multiregex_patterns(
            datafile_handlers=[AboutFileHandler],
        )
        assert multiregexes.patterns == [('(?s:.*\\.ABOUT)\\Z', ['.about'])]
        assert multiregexes.handler_by_regex == {'(?s:.*\\.ABOUT)\\Z': ['about_file']}

    def test_build_package_cache_works(self):
        from packagedcode.about import AboutFileHandler
        from packagedcode.bower import BowerJsonHandler

        package_cache_dir = self.get_test_loc('cache/')
        package_cache = cache.PkgManifestPatternsCache.load_or_build(
            packagedcode_cache_dir=package_cache_dir,
            application_package_datafile_handlers=[AboutFileHandler],
            system_package_datafile_handlers=[BowerJsonHandler],
            force=True,
        )
        test_path = "scancode-toolkit.ABOUT"

        assert not package_cache.system_package_matcher.match(test_path)
        assert package_cache.application_package_matcher.match(test_path)
        
        regex, _match = package_cache.all_package_matcher.match(test_path).pop()
        assert package_cache.handler_by_regex.get(regex.pattern).pop() == AboutFileHandler.datasource_id

    def test_empty_file_scan_works(self):

        test_file = self.get_test_loc('cache/.gitignore')
        package_path = as_posixpath(test_file)
        package_matcher = cache.get_cache()

        assert not package_matcher.all_package_matcher.match(package_path)

    def test_get_prematchers_from_glob_pattern(self):

        from packagedcode.pypi import PyprojectTomlHandler

        prematchers = cache.get_prematchers_from_glob_pattern(PyprojectTomlHandler.path_patterns[0])
        assert "pyproject.toml" in prematchers
