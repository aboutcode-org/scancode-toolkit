"""
Tests for surrogate character handling in copyright detection.

See: https://github.com/aboutcode-org/scancode-toolkit/issues/4664
"""

import pytest
from cluecode.copyrights import sanitize_line_for_detection
from cluecode.copyrights import SURROGATE_PATTERN


class TestSurrogateSanitization:
    
    def test_sanitize_line_for_detection_removes_surrogates(self):
        """Test that surrogate characters are removed from text."""
        # Create text with surrogate characters using chr()
        surrogate_high = chr(0xD800)
        surrogate_low = chr(0xDC00)
        text = f"test {surrogate_high}{surrogate_low} text"
        result = sanitize_line_for_detection(text)
        assert surrogate_high not in result
        assert surrogate_low not in result
        assert result == "test  text"
    
    def test_sanitize_line_for_detection_preserves_normal_text(self):
        """Test that normal text including copyright symbols is preserved."""
        text = "Copyright (c) 2024 John Doe"
        result = sanitize_line_for_detection(text)
        assert result == text
    
    def test_sanitize_line_for_detection_preserves_unicode_text(self):
        """Test that valid Unicode text like Korean is preserved."""
        text = "한글 텍스트 Korean text"
        result = sanitize_line_for_detection(text)
        assert result == text
    
    def test_sanitize_line_for_detection_handles_empty_string(self):
        """Test that empty string is handled correctly."""
        assert sanitize_line_for_detection("") == ""
    
    def test_sanitize_line_for_detection_handles_none(self):
        """Test that None is handled correctly."""
        assert sanitize_line_for_detection(None) is None
    
    def test_surrogate_pattern_matches_high_surrogates(self):
        """Test that SURROGATE_PATTERN matches high surrogate range U+D800-U+DBFF."""
        for codepoint in [0xD800, 0xDA00, 0xDBFF]:
            char = chr(codepoint)
            assert SURROGATE_PATTERN.search(char) is not None
    
    def test_surrogate_pattern_matches_low_surrogates(self):
        """Test that SURROGATE_PATTERN matches low surrogate range U+DC00-U+DFFF."""
        for codepoint in [0xDC00, 0xDE00, 0xDFFF]:
            char = chr(codepoint)
            assert SURROGATE_PATTERN.search(char) is not None
    
    def test_surrogate_pattern_does_not_match_normal_chars(self):
        """Test that SURROGATE_PATTERN does not match normal characters."""
        normal_text = "Copyright (c) 2024 한글"
        assert SURROGATE_PATTERN.search(normal_text) is None
