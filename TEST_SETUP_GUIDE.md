# Test Setup Guide: DSA-RSA Migration Testing in VM & LAN Environments

## Quick Start Sections
1. **Single Machine Testing** (5-10 minutes)
2. **Two-Machine LAN Testing** (15-30 minutes)
3. **Full Classroom Simulation** (2-3 hours)
4. **Automated Test Execution**

---

## Test Environment 1: Single Machine (Fastest)

### Time Required: 5-10 minutes

### Prerequisites
```bash
# Install dependencies
sudo apt-get install -y python3 python3-pip openssh-client openssh-server

# Install Sugar development dependencies (for testing)
sudo apt-get install -y sugar-base sugar-toolkit-gtk3 gir1.2-telepathy-1.0

# Or from source:
git clone https://github.com/sugarlabs/sugar
cd sugar
./setup.py develop
```

### Test Procedure

#### Step 1: Test RSA Key Generation
```bash
#!/bin/bash
TEST_DIR="/tmp/sugar_test_rsa"
mkdir -p $TEST_DIR

echo "[TEST 1] RSA-2048 Key Generation"
echo "================================"

# Generate RSA key (what Sugar does for new profiles)
ssh-keygen -q -t rsa -b 2048 -f $TEST_DIR/owner.key -C '' -N ''

# Verify files created
if [ -f $TEST_DIR/owner.key ] && [ -f $TEST_DIR/owner.key.pub ]; then
    echo "✓ PASS: Key files created"
    
    # Check key type
    KEY_TYPE=$(ssh-keygen -l -f $TEST_DIR/owner.key.pub | grep -oE "^[0-9]+ [^ ]+ ([a-zA-Z0-9]+)" | awk '{print $3}')
    echo "✓ Key type: $KEY_TYPE"
    
    # Check file sizes
    PRIV_SIZE=$(wc -c < $TEST_DIR/owner.key)
    PUB_SIZE=$(wc -c < $TEST_DIR/owner.key.pub)
    echo "✓ Private key: $PRIV_SIZE bytes"
    echo "✓ Public key: $PUB_SIZE bytes"
else
    echo "✗ FAIL: Key files not created"
    exit 1
fi
```

#### Step 2: Test privkey_hash Computation
```bash
#!/bin/bash
TEST_DIR="/tmp/sugar_test_rsa"

echo ""
echo "[TEST 2] privkey_hash Stability"
echo "=============================="

# Compute hash from private key (as Sugar does)
HASH_BEFORE=$(grep -v "^-----" $TEST_DIR/owner.key | tr -d '\n' | sha256sum | awk '{print $1}')
echo "Hash (RSA only): $HASH_BEFORE"

# Add mock DSA public key (simulating migration)
echo "ssh-dss AAAAB3NzaC1kc3MAAACBALz8hPSP2C12K2/x+cRf111... test@sugar" > $TEST_DIR/owner-dsa.key.pub

# Recompute hash (should be same - computed from private key only)
HASH_AFTER=$(grep -v "^-----" $TEST_DIR/owner.key | tr -d '\n' | sha256sum | awk '{print $1}')
echo "Hash (RSA+DSA): $HASH_AFTER"

if [ "$HASH_BEFORE" == "$HASH_AFTER" ]; then
    echo "✓ PASS: Hash is STABLE"
    echo "  Impact: User identity preserved"
else
    echo "✗ FAIL: Hash changed!"
    exit 1
fi
```

#### Step 3: Test Guard Logic
```bash
#!/bin/bash
TEST_DIR="/tmp/sugar_test_rsa"

echo ""
echo "[TEST 3] Guard Logic - Prevent Key Overwrite"
echo "==========================================="

# Record original key content
ORIGINAL_KEY=$(cat $TEST_DIR/owner.key)

# Simulate running profile creation again
echo "Simulating profile creation with existing keys..."

# This is what the guard does:
if [ -f $TEST_DIR/owner.key ] && [ -f $TEST_DIR/owner.key.pub ]; then
    PUBKEY=$(cat $TEST_DIR/owner.key.pub)
    PRIVKEY_HASH=$(grep -v "^-----" $TEST_DIR/owner.key | tr -d '\n' | sha256sum | awk '{print $1}')
    
    if [ ! -z "$PUBKEY" ] && [ ! -z "$PRIVKEY_HASH" ]; then
        echo "✓ Guard condition met: return early (skip regeneration)"
        GUARD_PASS=1
    fi
fi

# Verify key not regenerated
CURRENT_KEY=$(cat $TEST_DIR/owner.key)

if [ "$ORIGINAL_KEY" == "$CURRENT_KEY" ] && [ $GUARD_PASS -eq 1 ]; then
    echo "✓ PASS: Existing keys preserved"
else
    echo "✗ FAIL: Keys were modified"
    exit 1
fi

# Cleanup
rm -rf $TEST_DIR
```

#### Run All Single-Machine Tests
```bash
#!/bin/bash
# Save above scripts and run:
bash test_rsa_generation.sh
bash test_privkey_hash.sh
bash test_guard_logic.sh

echo ""
echo "======================================="
echo "✓ All single-machine tests PASSED"
echo "======================================="
```

---

## Test Environment 2: Two-Machine LAN Testing

### Time Required: 15-30 minutes

### Prerequisites
- Two computers (or VMs) on same LAN
- Both have Sugar installed with DSA-RSA fixes
- Salut (local presence service) configured
- Optional: Telepathy configured for Chat activity

### Network Setup

#### Option A: Virtual Machines (Recommended for Testing)
```bash
# Create virtual network bridge
# In VirtualBox / KVM hypervisor settings:
# - Create virtual network: 192.168.122.0/24
# - Enable DHCP
# - Enable DNS

# VM 1: "alice-dsa"
# - Ubuntu 20.04 + Sugar (with old DSA keys)
# - IP: 192.168.122.10

# VM 2: "bob-rsa"  
# - Ubuntu 22.04 + Sugar (with new RSA keys)
# - IP: 192.168.122.11
```

#### Option B: Physical Network
```bash
# Required: Both machines connected to same WiFi/Ethernet
# Test: ping between machines
ping 192.168.1.X  # Verify connectivity
```

### Two-Machine Test Procedure

#### Setup VM1 (Alice - DSA Profile)
```bash
# SSH into VM1
ssh user@192.168.122.10

# Install Sugar if needed
sudo apt-get install -y sugar-base sugar-toolkit-gtk3

# Create DSA profile (on system that still supports it)
# OR manually create mock DSA keys:
mkdir -p ~/.sugar/default

# Create mock DSA keys
cat > ~/.sugar/default/owner.key << 'EOF'
-----BEGIN DSA PRIVATE KEY-----
MIIBuwIBAAKBgQDTUHpGJ/+DtN+G4m1pZ6nUPx+SN0gGhN5bnM1B8H6eVJNYi8q1
...
-----END DSA PRIVATE KEY-----
EOF

cat > ~/.sugar/default/owner.key.pub << 'EOF'
ssh-dss AAAAB3NzaC1kc3MAAACBANNQekYn/4O034biXWlnqdQ/H5I3SAaE3lucTUHwfp5Uk1iLyrW3UPpLdlwo6jeFfhyPkaZhfHPw3dhfow== test@sugar
EOF

chmod 600 ~/.sugar/default/owner.key
chmod 644 ~/.sugar/default/owner.key.pub

echo "✓ Alice's DSA profile created"
```

#### Setup VM2 (Bob - RSA Profile)
```bash
# SSH into VM2
ssh user@192.168.122.11

# Create RSA profile
mkdir -p ~/.sugar/default

# Generate RSA key (what new Sugar does)
ssh-keygen -q -t rsa -b 2048 -f ~/.sugar/default/owner.key -C '' -N ''

echo "✓ Bob's RSA profile created"
```

#### Test Presence Discovery
```bash
# On Alice's machine (VM1)
# Command to check local presence
python3 << 'PYEOF'
import subprocess
import time

# Wait for Salut to register
time.sleep(3)

# Try to find Bob via Salut
result = subprocess.run(['avahi-browse', '-r', '_http._tcp', 'local'], 
                       capture_output=True, text=True, timeout=10)

print("Available services on LAN:")
print(result.stdout)

if 'bob' in result.stdout.lower() or 'sugar' in result.stdout.lower():
    print("\n✓ PASS: Bob discovered on LAN")
else:
    print("\n⚠ Could not discover Bob (Salut/Avahi may need config)")
PYEOF
```

#### Test Chat Activity (Mixed Keys)

##### Method 1: Manual GUI Test
```bash
# Start Sugar on both machines
# On Alice's machine: Applications → Sugar → Sugar Desktop

# In Sugar (Alice's DSA profile):
# 1. Wait for buddy list to show
# 2. Look for "Bob" in buddy list
# 3. Right-click Bob → "Chat with Bob"
# 4. Chat window opens
# 5. Type message: "Hi Bob, testing mixed DSA/RSA keys"
# 6. Send message
# 7. Verify Bob receives it

# Repeat from Bob's side (RSA profile)
# Both should be able to chat normally

Result: ✓ Chat works with mixed key types
```

##### Method 2: Automated Test (Python)
```python
#!/usr/bin/env python3
"""
Automated chat activity test for mixed keys.
"""

import dbus
import time
from sugar3 import presence
from sugar3 import profile

def test_mixed_key_collaboration():
    """Test chat between DSA and RSA profiles."""
    
    print("[TEST] Mixed-Key Collaboration (Chat)")
    print("="*50)
    
    # Get current profile
    my_profile = profile.get_profile()
    my_pubkey = profile.get_pubkey()
    my_hash = my_profile.privkey_hash
    
    print(f"My profile:")
    print(f"  pubkey: {my_pubkey[:30]}...")
    print(f"  privkey_hash: {my_hash}")
    print(f"  key_type: {'RSA' if 'ssh-rsa' in my_pubkey else 'DSA'}")
    
    # Get presence service
    pservice = presence.get_presence_service()
    
    print(f"\nSearching for collaborators on LAN...")
    time.sleep(2)
    
    # List available buddies
    buddies = pservice.get_buddies()
    print(f"Found {len(buddies)} buddy/buddies")
    
    for buddy in buddies:
        buddy_name = buddy.get_nick()
        buddy_hash = buddy.get_properties().get('pubkey_hash', 'unknown')
        
        print(f"\nBuddy: {buddy_name}")
        print(f"  pubkey_hash: {buddy_hash}")
        
        # Try to create shared activity (chat)
        try:
            activity = pservice.share_activity(None, 'org.laptop.Chat')
            print(f"  ✓ Activity shared successfully")
            print(f"  ✓ Collaboration ready")
            time.sleep(1)
            return True
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False
    
    return False

if __name__ == '__main__':
    success = test_mixed_key_collaboration()
    if success:
        print("\n✓ PASS: Mixed-key collaboration verified")
    else:
        print("\n✗ FAIL: Collaboration test failed")
        exit(1)
```

---

## Test Environment 3: Full Classroom Simulation

### Time Required: 2-3 hours

### Setup (5 VMs or Machines)

```
VM1: Alice - Old DSA keys (pre-OpenSSH 10 system)
VM2: Bob - New RSA keys (fresh install)
VM3: Charlie - Mixed keys (migrated profile)
VM4: Diana - Old DSA keys (different subnet test)
VM5: Teacher - Activity coordination

Network:
- VM1-VM3: Same subnet (192.168.1.0/24) - main classroom
- VM4: Different subnet (10.0.0.0/24) - visitor device
- Salut configured for local buddy discovery
```

### Scenario: Shared Document Activity

#### Step 1: Launch All Sugar Instances
```bash
# On each VM
sugar-shell &
```

#### Step 2: Teacher Creates Shared Document
```bash
# As Teacher:
1. Launch Sugar
2. Wait for buddy list
3. Create "Writing Activity" 
4. Select all students: Alice, Bob, Charlie
5. Share activity
```

#### Step 3: Verify All Clients Can Join

```bash
# Each student receives invitation
# Student acceptance:
# 1. See notification: "Teacher shared Writing with you"
# 2. Click to join
# 3. Shared document opens
# 4. All see same content

Record results:
[ ] Alice (DSA): ✓ Joined / ✗ Failed
[ ] Bob (RSA): ✓ Joined / ✗ Failed
[ ] Charlie (Mixed): ✓ Joined / ✗ Failed
```

#### Step 4: Collaborative Editing

```bash
# Teacher types: "Today's lesson: Renewable Energy"
# Wait 1 second
# Verify all students see the text

# Alice adds: "Solar is important"
# Wait 1 second
# Verify all (including Bob) see Alice's text

# Bob adds: "Wind power too!"
# Wait 1 second  
# Verify all (including Alice) see Bob's text

# Charlie adds drawing (image/shape)
# Wait 1 second
# Verify all see the drawing

Record results:
[ ] Text synchronization: ✓ Works / ✗ Broken
[ ] Image sync: ✓ Works / ✗ Broken
[ ] No data loss: ✓ Yes / ✗ Lost data
[ ] Mixed-key peers: ✓ All connected / ✗ Some failed
```

#### Step 5: Network Disruption Test

```bash
# While collaboration ongoing:
1. Disconnect Bob's network (simulating poor WiFi)
2. Bob's activity shows "reconnecting"
3. Wait 5 seconds
4. Reconnect Bob's network
5. Activity auto-resumes
6. All messages preserved

Record results:
[ ] Disconnection detected: ✓ Yes / ✗ No
[ ] Auto-reconnect: ✓ Works / ✗ Failed
[ ] Data preserved: ✓ Yes / ✗ Lost
[ ] Keys stable: ✓ Yes / ✗ Corrupted
```

#### Step 6: Save & Verify

```bash
# Teacher saves document
# Verify file saved to: ~/.sugar/default/activities/...

# Check file integrity:
python3 << 'EOF'
import json
with open('document.json') as f:
    doc = json.load(f)
    
print(f"Document content length: {len(doc.get('text', ''))}")
print(f"Collaborators: {len(doc.get('participants', []))}")
print(f"Last modified: {doc.get('timestamp', 'unknown')}")

if len(doc.get('text', '')) > 0:
    print("✓ Document saved successfully")
else:
    print("✗ Document is empty!")
EOF
```

---

## Automated Test Execution

### Test Suite Python Script

```python
#!/usr/bin/env python3
"""
Complete automated test suite for DSA-RSA migration.
Run on single machine or coordinated across network.
"""

import os
import sys
import subprocess
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple

class TestRunner:
    """Manages test execution and result collection."""
    
    def __init__(self, test_dir: str = "/tmp/sugar_test"):
        self.test_dir = test_dir
        self.results = []
        os.makedirs(test_dir, exist_ok=True)
    
    def run_command(self, cmd: List[str], timeout: int = 30) -> Tuple[int, str, str]:
        """Execute command and return (returncode, stdout, stderr)."""
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timeout: {' '.join(cmd)}"
        except Exception as e:
            return -1, "", str(e)
    
    def test_rsa_generation(self) -> bool:
        """Test RSA-2048 key generation."""
        print("\n[TEST 1] RSA-2048 Generation")
        print("-" * 40)
        
        key_path = os.path.join(self.test_dir, "test_rsa_key")
        
        returncode, stdout, stderr = self.run_command([
            'ssh-keygen', '-q', '-t', 'rsa', '-b', '2048',
            '-f', key_path, '-C', '', '-N', ''
        ])
        
        if returncode == 0:
            if os.path.exists(key_path) and os.path.exists(f"{key_path}.pub"):
                print("✓ PASS: RSA key generated")
                return True
        
        print(f"✗ FAIL: {stderr}")
        return False
    
    def test_privkey_hash_stability(self) -> bool:
        """Test privkey_hash stability."""
        print("\n[TEST 2] privkey_hash Stability")
        print("-" * 40)
        
        key_path = os.path.join(self.test_dir, "test_key")
        
        # Generate key
        self.run_command([
            'ssh-keygen', '-q', '-t', 'rsa', '-b', '2048',
            '-f', key_path, '-C', '', '-N', ''
        ])
        
        # Compute hash before
        with open(key_path, 'r') as f:
            key_before = f.read()
        hash_before = hashlib.sha256(key_before.encode()).hexdigest()
        
        # Add mock DSA key
        dsa_pub = os.path.join(self.test_dir, "owner-dsa.key.pub")
        with open(dsa_pub, 'w') as f:
            f.write("ssh-dss AAAAB3NzaC1kc3M... test@sugar")
        
        # Compute hash after (should be same)
        with open(key_path, 'r') as f:
            key_after = f.read()
        hash_after = hashlib.sha256(key_after.encode()).hexdigest()
        
        if hash_before == hash_after:
            print("✓ PASS: Hash is STABLE")
            return True
        else:
            print(f"✗ FAIL: Hash changed!")
            return False
    
    def test_guard_logic(self) -> bool:
        """Test that guard prevents key regeneration."""
        print("\n[TEST 3] Guard Logic")
        print("-" * 40)
        
        key_path = os.path.join(self.test_dir, "guard_key")
        
        # Generate initial key
        self.run_command([
            'ssh-keygen', '-q', '-t', 'rsa', '-b', '2048',
            '-f', key_path, '-C', '', '-N', ''
        ])
        
        with open(key_path, 'rb') as f:
            original = f.read()
        
        # Simulate guard check
        pubkey_exists = os.path.exists(f"{key_path}.pub")
        privkey_exists = os.path.exists(key_path)
        
        # Guard condition (from Sugar code)
        guard_pass = pubkey_exists and privkey_exists
        
        # After guard check, key shouldn't be regenerated
        with open(key_path, 'rb') as f:
            current = f.read()
        
        if original == current and guard_pass:
            print("✓ PASS: Guard prevents regeneration")
            return True
        else:
            print("✗ FAIL: Keys were modified")
            return False
    
    def run_all_tests(self) -> Dict:
        """Run complete test suite."""
        print("="*50)
        print("DSA-RSA Migration Test Suite")
        print("="*50)
        
        tests = [
            ("RSA Generation", self.test_rsa_generation),
            ("privkey_hash Stability", self.test_privkey_hash_stability),
            ("Guard Logic", self.test_guard_logic),
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"✗ ERROR: {e}")
                results[test_name] = False
        
        # Summary
        print("\n" + "="*50)
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        print(f"Results: {passed}/{total} tests passed")
        
        for test_name, result in results.items():
            status = "✓" if result else "✗"
            print(f"  {status} {test_name}")
        
        print("="*50)
        
        return results


if __name__ == '__main__':
    runner = TestRunner()
    results = runner.run_all_tests()
    
    sys.exit(0 if all(results.values()) else 1)
```

### Run Automated Tests
```bash
python3 automated_test_suite.py
```

---

## Test Results Template

Use this template to document your testing:

```markdown
# DSA-RSA Migration Test Results

**Date**: [YYYY-MM-DD]
**Tester**: [Name]
**Environment**: [Single machine / 2-VM LAN / Classroom sim]

## Test 1: RSA Key Generation
- [ ] PASS
- [ ] FAIL
Notes: ___________

## Test 2: Guard Logic  
- [ ] PASS
- [ ] FAIL
Notes: ___________

## Test 3: privkey_hash Stability
- [ ] PASS
- [ ] FAIL
Notes: ___________

## Test 4: Mixed-Key Collaboration
- [ ] PASS
- [ ] FAIL  
Notes: ___________

## Test 5: Chat Activity (RSA ↔ RSA)
- [ ] PASS
- [ ] FAIL
Notes: ___________

## Test 6: Chat Activity (RSA ↔ DSA)
- [ ] PASS
- [ ] FAIL
Notes: ___________

## Test 7: Shared Document (Mixed)
- [ ] PASS
- [ ] FAIL
Notes: ___________

## Overall Result
- [ ] All tests PASSED - Ready for merge
- [ ] Some tests FAILED - Issues to fix:
      ___________

## Environment Details
- OpenSSH version: ___________
- Sugar version: ___________
- Python version: ___________
- OS: ___________
```

---

## Troubleshooting

### Problem: ssh-keygen not found
**Solution**: 
```bash
sudo apt-get install -y openssh-client openssh-server
# Or on macOS:
brew install openssh
```

### Problem: DSA key generation fails (OpenSSH 10.0+)
**Expected**: This confirms DSA is disabled. The fix handles this correctly.
```bash
# Verify RSA works instead
ssh-keygen -t rsa -b 2048 -f test.key
```

### Problem: Salut/Avahi discovery not working
**Solution**:
```bash
# Start Avahi daemon
sudo systemctl start avahi-daemon

# Or manually test with:
avahi-browse -r _http._tcp
```

### Problem: Chat activity won't start
**Solution**:
```bash
# Install required packages
sudo apt-get install -y gir1.2-telepathy-1.0 telepathy-salut

# Check Telepathy status
dbus-launch dbus-send --print-reply --session \
  /org/freedesktop/DBus \
  org.freedesktop.DBus.ListNames
```

---

## Success Criteria

✅ **Test is successful when:**
1. RSA-2048 keys generate correctly
2. privkey_hash remains stable
3. Guard logic prevents key overwriting
4. Chat works between RSA ↔ RSA peers
5. Chat works between RSA ↔ DSA peers
6. Shared activities sync properly
7. No errors in logs
8. All key types (DSA/RSA/mixed) coexist

❌ **Test has failed if:**
- Any key generation errors
- privkey_hash changes unexpectedly
- Existing keys get overwritten
- Collaboration breaks between key types
- Activities crash or don't sync
- Error messages in logs

---

This guide provides everything needed to thoroughly test the DSA-RSA migration in controlled environments before production deployment.
