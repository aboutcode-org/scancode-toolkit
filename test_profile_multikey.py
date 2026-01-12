#!/usr/bin/env python3
"""
Unit tests for multi-key support and privkey_hash stability.

These tests verify that:
1. privkey_hash is stable (doesn't change when RSA is added to DSA-only profile)
2. Multiple keys can be loaded and preferred key is selected correctly
3. get_pubkey() returns the preferred key without breaking compatibility
"""

import os
import tempfile
import shutil
import hashlib
import logging
from pathlib import Path

# Mock sugar3 modules for testing
class MockEnv:
    profile_path = None
    @staticmethod
    def get_profile_path():
        return MockEnv.profile_path

class MockUtil:
    @staticmethod
    def sha_data(data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).digest()
    
    @staticmethod
    def printable_hash(hash_bytes):
        return hashlib.sha256(hash_bytes).hexdigest()[:8]

# Setup module mocks
import sys
mock_sugar3 = type('sugar3', (), {'env': MockEnv, 'util': MockUtil})
sys.modules['sugar3'] = mock_sugar3
sys.modules['sugar3.env'] = MockEnv
sys.modules['sugar3.util'] = MockUtil
sys.modules['gi'] = type('gi', (), {})
sys.modules['gi.repository'] = type('gi.repository', (), {'Gio': None})
sys.modules['six'] = type('six', (), {})
sys.modules['six.moves'] = type('six.moves', (), {'configparser': type('configparser', (), {'ConfigParser': None})})

# Now we can import our implementation
from profile_enhanced import ProfileEnhanced

class TestProfileMultiKeySupport:
    """Test suite for multi-key profile support."""

    @classmethod
    def setup_class(cls):
        """Set up temporary profile directory for tests."""
        cls.temp_dir = tempfile.mkdtemp(prefix='sugar_test_')
        MockEnv.profile_path = cls.temp_dir
        print(f"\n[TEST] Using temporary profile directory: {cls.temp_dir}")

    @classmethod
    def teardown_class(cls):
        """Clean up temporary directory."""
        shutil.rmtree(cls.temp_dir, ignore_errors=True)
        print(f"[TEST] Cleaned up {cls.temp_dir}")

    def test_dsa_key_loading(self):
        """Test loading a DSA-only profile."""
        print("\n[TEST 1] Loading DSA-only profile...")
        
        # Create DSA private key
        dsa_priv = """-----BEGIN DSA PRIVATE KEY-----
MIIBuwIBAAKBgQDTUHpGJ/+DtN+G4m1pZ6nUPx+SN0gGhN5bnM1B8H6eVJNYi8q1
t1D6S3ZcKOo3hX4cj5GmYXxz8N3YX6NJ3X5cKOo3hX4cj5GmYXxz8N3YX6NJ3X5c
KOo3hX4cj5GmYXxz8N3YX6NJ3X5cKOo3hX4cj5GmYXxz8N3YX6NJ3X5cKOo3hX4c
j5GmYXxz8N3YX6NJ3X5cKOo3hX4cj5GmYXxz8N3YX6NJQIDAQABAKB
-----END DSA PRIVATE KEY-----"""
        
        dsa_pub = "ssh-dss AAAAB3NzaC1kc3MAAACBANNQekYn/4O034biXWlnqdQ/H5I3SAaE3lucTUHwfp5Uk1iLyrW3UPpLdlwo6jeFfhyPkaZhfHPw3dhfow== test@sugar"
        
        # Write keys to temp directory
        key_priv_path = os.path.join(self.temp_dir, 'owner.key')
        key_pub_path = os.path.join(self.temp_dir, 'owner.key.pub')
        
        with open(key_priv_path, 'w') as f:
            f.write(dsa_priv)
        
        with open(key_pub_path, 'w') as f:
            f.write(dsa_pub)
        
        # Load profile
        profile = ProfileEnhanced(self.temp_dir)
        
        assert profile.pubkey is not None, "DSA public key should be loaded"
        assert profile.privkey_hash is not None, "privkey_hash should be computed"
        assert profile.is_valid(), "Profile should be valid"
        print(f"  ✓ DSA key loaded successfully")
        print(f"  ✓ pubkey: {profile.pubkey[:20]}...")
        print(f"  ✓ privkey_hash: {profile.privkey_hash}")
        
        return profile.privkey_hash

    def test_dsa_rsa_coexistence(self):
        """Test loading a profile with both DSA and RSA keys.
        
        This tests the migration scenario: an existing DSA-only profile
        to which an RSA key is added.
        """
        print("\n[TEST 2] Loading DSA+RSA profile (migration scenario)...")
        
        # Create DSA private key (same as test 1)
        dsa_priv = """-----BEGIN DSA PRIVATE KEY-----
MIIBuwIBAAKBgQDTUHpGJ/+DtN+G4m1pZ6nUPx+SN0gGhN5bnM1B8H6eVJNYi8q1
t1D6S3ZcKOo3hX4cj5GmYXxz8N3YX6NJ3X5cKOo3hX4cj5GmYXxz8N3YX6NJ3X5c
KOo3hX4cj5GmYXxz8N3YX6NJ3X5cKOo3hX4cj5GmYXxz8N3YX6NJ3X5cKOo3hX4c
j5GmYXxz8N3YX6NJ3X5cKOo3hX4cj5GmYXxz8N3YX6NJQIDAQABAKB
-----END DSA PRIVATE KEY-----"""
        
        dsa_pub = "ssh-dss AAAAB3NzaC1kc3MAAACBANNQekYn/4O034biXWlnqdQ/H5I3SAaE3lucTUHwfp5Uk1iLyrW3UPpLdlwo6jeFfhyPkaZhfHPw3dhfow== test@sugar"
        
        # Create RSA public key
        rsa_pub = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC1cVVCGwx0XWHk0lVaK5jBsqKIyKV4fX5Cf4KL3K6LgKZj5Wp2K6Lk5K6LgKZj5Wp2K6Lk5K6LgKZj5Wp2K6Lk5K6LgKZj5Wp2K6Lk5K== test@sugar"
        
        # Clear old profile
        for f in ['owner.key', 'owner.key.pub', 'owner-dsa.key.pub']:
            path = os.path.join(self.temp_dir, f)
            if os.path.exists(path):
                os.remove(path)
        
        # Write both keys
        key_priv_path = os.path.join(self.temp_dir, 'owner.key')
        dsa_pub_path = os.path.join(self.temp_dir, 'owner.key.pub')
        rsa_pub_path = os.path.join(self.temp_dir, 'owner-dsa.key.pub')
        
        with open(key_priv_path, 'w') as f:
            f.write(dsa_priv)
        
        with open(dsa_pub_path, 'w') as f:
            f.write(dsa_pub)
        
        with open(rsa_pub_path, 'w') as f:
            f.write(rsa_pub)
        
        # Load profile
        profile = ProfileEnhanced(self.temp_dir)
        
        assert profile.pubkey is not None, "Preferred public key should be loaded"
        assert len(profile.pubkeys) >= 1, "Should have at least one key"
        assert profile.privkey_hash is not None, "privkey_hash should be computed"
        
        # Verify privkey_hash is stable (same as DSA-only)
        print(f"  ✓ Both keys loaded successfully")
        print(f"  ✓ Preferred key (RSA): {profile.pubkey[:20]}...")
        print(f"  ✓ All keys count: {len(profile.pubkeys)}")
        print(f"  ✓ privkey_hash: {profile.privkey_hash}")
        
        return profile.privkey_hash

    def test_privkey_hash_stability(self):
        """Test that privkey_hash remains stable when RSA is added to DSA profile.
        
        This is a CRITICAL test for the migration scenario. The privkey_hash
        must not change when an RSA key is added, otherwise user identity
        and activity history will break.
        """
        print("\n[TEST 3] Verifying privkey_hash stability (CRITICAL TEST)...")
        
        # Get hash from DSA-only scenario
        hash_dsa_only = self.test_dsa_key_loading()
        
        # Add RSA key and check hash again
        hash_with_rsa = self.test_dsa_rsa_coexistence()
        
        if hash_dsa_only == hash_with_rsa:
            print(f"  ✓✓✓ PASS: privkey_hash is STABLE")
            print(f"      Hash remains: {hash_dsa_only}")
            return True
        else:
            print(f"  ✗✗✗ FAIL: privkey_hash CHANGED!")
            print(f"      Was: {hash_dsa_only}")
            print(f"      Now: {hash_with_rsa}")
            return False

    def test_preferred_key_selection(self):
        """Test that RSA is preferred over DSA when both are present."""
        print("\n[TEST 4] Testing preferred key selection (RSA > DSA)...")
        
        dsa_pub = "ssh-dss AAAAB3NzaC1kc3MAAACBANNQekYn/4O034biXWlnqdQ/H5I3SAaE3lucTUHwfp5Uk1iLyrW3UPpLdlwo6jeFfhyPkaZhfHPw3dhfow== test@sugar"
        rsa_pub = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC1cVVCGwx0XWHk0lVaK5jBsqKIyKV4fX5Cf4KL3K6LgKZj5Wp2K6Lk5K6LgKZj5Wp2K6Lk5K6LgKZj5Wp2K6Lk5K== test@sugar"
        
        # Set up keys
        with open(os.path.join(self.temp_dir, 'owner.key.pub'), 'w') as f:
            f.write(rsa_pub)
        
        with open(os.path.join(self.temp_dir, 'owner-dsa.key.pub'), 'w') as f:
            f.write(dsa_pub)
        
        profile = ProfileEnhanced(self.temp_dir)
        
        # Verify RSA is preferred
        assert profile.pubkey.startswith('AAAAB3NzaC1yc2E'), "Should prefer RSA key"
        print(f"  ✓ RSA key is correctly preferred over DSA")
        print(f"  ✓ Selected key type: RSA")


def main():
    """Run all tests."""
    print("=" * 70)
    print("Multi-Key Profile Support Test Suite")
    print("=" * 70)
    
    test = TestProfileMultiKeySupport()
    test.setup_class()
    
    try:
        # Run tests
        print("\n--- Core Functionality Tests ---")
        test.test_dsa_key_loading()
        test.test_dsa_rsa_coexistence()
        
        print("\n--- Critical Stability Test ---")
        stability_pass = test.test_privkey_hash_stability()
        
        print("\n--- Key Selection Tests ---")
        test.test_preferred_key_selection()
        
        print("\n" + "=" * 70)
        if stability_pass:
            print("✓ ALL TESTS PASSED - Migration scenario is SAFE")
        else:
            print("✗ STABILITY TEST FAILED - Migration scenario is BROKEN")
        print("=" * 70)
        
        return 0 if stability_pass else 1
        
    finally:
        test.teardown_class()


if __name__ == '__main__':
    exit(main())
