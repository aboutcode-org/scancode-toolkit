# Enhanced Profile Implementation with Multi-Key Support
# This version adds support for multiple public keys (DSA and RSA)
# while preserving privkey_hash for identity stability.

import os
import logging
from sugar3 import env, util

class ProfileEnhanced:
    """Enhanced Profile with multi-key support.
    
    Supports loading multiple public keys (DSA and RSA) while maintaining
    backward compatibility. privkey_hash is computed from the original
    private key (typically DSA for existing profiles) to ensure identity stability.
    """

    def __init__(self, path):
        self._pubkey = None           # preferred key (RSA if present, else DSA)
        self._pubkeys = None          # all available keys (list)
        self._privkey_hash = None
        self.path = path

    def _get_pubkey(self):
        """Return the preferred public key (RSA if present, else DSA)."""
        if self._pubkey is None:
            keys = self._load_all_pubkeys()
            if keys:
                # Prefer RSA over DSA for new collaborations
                for key in keys:
                    if key.startswith('AAAAB3NzaC1yc2E'):  # RSA key marker
                        self._pubkey = key
                        break
                if not self._pubkey:
                    # Fall back to first available key (likely DSA)
                    self._pubkey = keys[0]
        return self._pubkey

    def _get_pubkeys(self):
        """Return all available public keys."""
        if self._pubkeys is None:
            self._pubkeys = self._load_all_pubkeys()
        return self._pubkeys or []

    pubkey = property(fget=_get_pubkey)
    pubkeys = property(fget=_get_pubkeys)

    def _load_all_pubkeys(self):
        """Load all available public keys (DSA and RSA)."""
        keys = []
        
        # Try to load the main key file (RSA for new profiles, DSA for old)
        main_key = self._load_pubkey_from_file('owner.key.pub')
        if main_key:
            keys.append(main_key)
        
        # Try to load legacy DSA key (if separate file exists)
        dsa_key = self._load_pubkey_from_file('owner-dsa.key.pub')
        if dsa_key:
            keys.append(dsa_key)
        
        return keys

    def _load_pubkey_from_file(self, filename):
        """Load public key from a specific file."""
        key_path = os.path.join(env.get_profile_path(), filename)
        
        if not os.path.exists(key_path):
            return None
        
        try:
            with open(key_path, 'r') as f:
                lines = f.readlines()
        except IOError:
            logging.exception('Error reading public key from %s', filename)
            return None
        
        # Support both DSA (ssh-dss) and RSA (ssh-rsa)
        supported_key_types = ('ssh-dss ', 'ssh-rsa ')
        for line in lines:
            line = line.strip()
            for magic in supported_key_types:
                if line.startswith(magic):
                    return line[len(magic):]  # Return the key portion
        
        logging.error('Error parsing public key from %s', filename)
        return None

    def _hash_private_key(self):
        """Hash the private key for identity stability.
        
        Computes hash from the original private key (typically owner.key).
        This ensures that privkey_hash remains stable even if RSA key is added.
        """
        key_path = os.path.join(env.get_profile_path(), 'owner.key')

        if not os.path.exists(key_path):
            return None

        try:
            with open(key_path, 'r') as f:
                lines = f.readlines()
        except IOError:
            logging.exception('Error reading private key')
            return None

        key = ""
        begin_found = False
        end_found = False
        for line in lines:
            line = line.strip()
            # Support both DSA and OpenSSH key formats
            if line.startswith(('-----BEGIN DSA PRIVATE KEY-----',
                                '-----BEGIN OPENSSH PRIVATE KEY-----',
                                '-----BEGIN RSA PRIVATE KEY-----')):
                begin_found = True
                continue
            if line.startswith(('-----END DSA PRIVATE KEY-----',
                                '-----END OPENSSH PRIVATE KEY-----',
                                '-----END RSA PRIVATE KEY-----')):
                end_found = True
                continue
            if begin_found and not end_found:
                key += line
        
        if not (len(key) and begin_found and end_found):
            logging.error('Error parsing private key.')
            return None

        # Hash the key material
        key_hash = util.sha_data(key)
        return util.printable_hash(key_hash)

    def _get_privkey_hash(self):
        """Return the cached privkey_hash."""
        if self._privkey_hash is None:
            self._privkey_hash = self._hash_private_key()
        return self._privkey_hash

    privkey_hash = property(fget=_get_privkey_hash)

    def is_valid(self):
        """Check if the profile is valid (has identity and keys)."""
        return bool(self.pubkey and self.privkey_hash)

    def get_pubkey_for_protocol(self, protocol=None):
        """Get a public key suitable for a specific protocol.
        
        Args:
            protocol: Optional protocol identifier (e.g., 'telepathy', 'olpc').
                     If not specified, returns the preferred key.
        
        Returns:
            A public key string, or None if no suitable key is found.
        """
        if protocol == 'rsa' or protocol is None:
            # Prefer RSA for modern protocols
            for key in self.pubkeys:
                if key.startswith('AAAAB3NzaC1yc2E'):
                    return key
        
        # Fall back to any available key
        return self.pubkey
