
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from packagedcode import citation
from packages_test_utils import PackageTester


class TestCitation(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_is_datafile_citation_cff(self):
        test_file = self.get_test_loc('citation/minimal/CITATION.cff')
        assert citation.CitationFileHandler.is_datafile(test_file)

    def test_is_datafile_case_insensitive(self):
        test_file = self.get_test_loc('citation/case-test/citation.cff')
        assert citation.CitationFileHandler.is_datafile(test_file)

    def test_parse_minimal_citation_cff(self):
        test_file = self.get_test_loc('citation/minimal/CITATION.cff')
        packages = list(citation.CitationFileHandler.parse(test_file))
        
        assert len(packages) == 1
        package = packages[0]
        
        assert package.name == 'Minimal Citation Example'
        assert package.type == 'generic'
        assert package.version is None
        assert package.description is None
        assert package.extracted_license_statement is None
        assert not package.parties
        assert package.homepage_url is None
        assert package.vcs_url is None
        assert 'cff_version' in package.extra_data
        assert package.extra_data['cff_version'] == '1.2.0'

    def test_parse_full_citation_cff(self):
        test_file = self.get_test_loc('citation/full/CITATION.cff')
        packages = list(citation.CitationFileHandler.parse(test_file))
        
        assert len(packages) == 1
        package = packages[0]
        
        assert package.name == 'Full Citation Example'
        assert package.version == '1.0.0'
        assert package.extracted_license_statement == 'MIT'
        assert package.homepage_url == 'https://example.org/project'
        assert package.vcs_url == 'https://github.com/example/project'
        
        # Parties
        assert len(package.parties) == 1
        assert package.parties[0]['name'] == 'John Doe'
        assert package.parties[0]['email'] == 'john.doe@example.org'
        
        # Keywords - set-based assertion (order-independent, normalization-proof)
        assert set(package.keywords) >= {'software', 'citation', 'metadata'}
        
        # Extra data - assert keys exist, not full equality
        assert 'cff_version' in package.extra_data
        assert 'doi' in package.extra_data
        assert 'date_released' in package.extra_data
        assert 'cff_type' in package.extra_data

    def test_parse_multiple_authors(self):
        test_file = self.get_test_loc('citation/multiple-authors/CITATION.cff')
        packages = list(citation.CitationFileHandler.parse(test_file))
        
        assert len(packages) == 1
        package = packages[0]
        
        # Should have 5 authors (malformed entry skipped)
        assert len(package.parties) == 5
        
        # Map by name for semantic assertions (order-independent)
        authors = {p['name']: p for p in package.parties}
        
        # family+given with ORCID
        assert 'Jane Smith' in authors
        assert authors['Jane Smith']['email'] == 'jane@example.org'
        assert 'orcid' in authors['Jane Smith']['extra_data']
        assert authors['Jane Smith']['extra_data']['orcid'] == 'https://orcid.org/0000-0001-2345-6789'
        
        # name-only
        assert 'Bob Johnson' in authors
        
        # family-names only
        assert 'Williams' in authors
        
        # given-names only
        assert 'Alice' in authors
        
        # with affiliation
        assert 'Charlie Brown' in authors
        assert 'affiliation' in authors['Charlie Brown']['extra_data']
        
        # Explicitly assert malformed entry was skipped (no author with empty/invalid name)
        author_names = [p['name'] for p in package.parties]
        assert 'invalid_entry_should_be_skipped' not in ' '.join(author_names)

    def test_parse_invalid_yaml(self):
        test_file = self.get_test_loc('citation/invalid-yaml/CITATION.cff')
        packages = list(citation.CitationFileHandler.parse(test_file))
        
        # Should return nothing, no exception
        assert len(packages) == 0

    def test_parse_missing_cff_version(self):
        test_file = self.get_test_loc('citation/missing-cff-version/CITATION.cff')
        packages = list(citation.CitationFileHandler.parse(test_file))
        
        # Should return nothing, no exception
        assert len(packages) == 0

    def test_parse_backward_compat_v1_0_0(self):
        test_file = self.get_test_loc('citation/cff-v1.0.0/CITATION.cff')
        packages = list(citation.CitationFileHandler.parse(test_file))
        
        assert len(packages) == 1
        package = packages[0]
        
        assert package.name == 'Backward Compatibility Test'
        assert package.version == '0.1.0'
        assert package.extra_data['cff_version'] == '1.0.0'
