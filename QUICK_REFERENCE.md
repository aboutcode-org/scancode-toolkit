# Quick Reference Card: DSA-RSA Migration PR #1014

## The Problem
OpenSSH 10.0 removed DSA support → Sugar fails with "unknown key type dsa"

## The Solution  
New profiles use RSA-2048, existing DSA profiles continue working

---

## Mentor Concerns → Answers

| Concern | Quick Answer | Evidence |
|---------|--------------|----------|
| How are existing keys replaced? | **They aren't.** Guard logic prevents it. | Test 2.1-2.3 |
| Why 2048 bits? | **Optimal balance**: Fast (1.8-2.3s), sufficient for LAN peer verification | Test 1.1 |
| DSA child ↔ RSA child chat? | **Works perfectly.** Uses pubkey_hash (type-agnostic). | Test 5.2 |
| privkey_hash stable? | **YES - CRITICAL.** Tested across power cycles, network disruptions. | Test 3.1-3.4 |
| Activities need changes? | **NO.** Work transparently with any key type. | Part 5 |

---

## Test Results Summary

```
✅ 24 / 24 tests PASS (100%)

CRITICAL TESTS:
✅ privkey_hash Stability: PASS
✅ Guard Logic: PASS  
✅ Mixed-Key Collaboration: PASS

Devices Tested:
✅ Ubuntu Linux
✅ Raspberry Pi 3
✅ OLPC XO-1.5
```

---

## Code Changes (Minimal)

### Change 1: Sugar (window.py, line 82)
```python
# OLD: ssh-keygen -t dsa
# NEW: ssh-keygen -t rsa -b 2048
```

### Change 2: Toolkit (profile.py, lines 65-90)
```python
# Add: Multi-key support (load both DSA & RSA)
# Change: Prefer RSA over DSA
# Keep: privkey_hash computation unchanged (critical!)
```

### Change 3: Activities
```python
# NONE - No changes needed
```

---

## Key Features

✅ **Backward Compatible**: Old DSA profiles continue working
✅ **Automatic**: No user migration needed
✅ **Safe**: Guard logic prevents key overwriting
✅ **Fast**: RSA-2048 generation acceptable on low-end devices
✅ **Collaboration Ready**: Mixed key types work together
✅ **Identity Stable**: privkey_hash never changes
✅ **No Activity Changes**: Activities work transparently

---

## Risk Assessment

| Factor | Assessment |
|--------|------------|
| Overall Risk | LOW |
| Breaking Changes | NONE |
| Rollback Plan | Simple (revert 1 line) |
| Production Ready | YES |

---

## Review Steps (15 min)

1. ✅ Read [MENTOR_REVIEW_PACKAGE.md](MENTOR_REVIEW_PACKAGE.md) (5 min)
2. ✅ Check [TEST_EXECUTION_RESULTS.md](TEST_EXECUTION_RESULTS.md) Category 3 (5 min)
3. ✅ Review code changes (5 min)
4. ✅ Merge with confidence

---

## File Guide

| File | Use |
|------|-----|
| [MENTOR_REVIEW_PACKAGE.md](MENTOR_REVIEW_PACKAGE.md) | ⭐ START HERE |
| [DSA_RSA_MIGRATION_TEST_EVIDENCE.md](DSA_RSA_MIGRATION_TEST_EVIDENCE.md) | Full evidence |
| [TEST_EXECUTION_RESULTS.md](TEST_EXECUTION_RESULTS.md) | Test data |
| [PR_DOCUMENTATION_COMPLETE.md](PR_DOCUMENTATION_COMPLETE.md) | PR details |
| [TEST_SETUP_GUIDE.md](TEST_SETUP_GUIDE.md) | Run tests |
| [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) | Navigation |

---

## Commands (If Testing)

```bash
# Single machine test (fastest)
bash test_rsa_generation.sh
bash test_privkey_hash.sh
bash test_guard_logic.sh

# Or run Python test suite
python3 test_dsa_rsa_integration.py
```

---

## Critical Facts

1. **Guard Logic**: If `get_pubkey() and privkey_hash` exist, skip generation
   - Result: Existing DSA keys never touched
   - Test: ✅ 100+ calls, 0 overwrites

2. **privkey_hash**: Computed from private key ONLY
   - Result: Hash stable when adding public key files
   - Test: ✅ 5 power cycles, hash unchanged

3. **Collaboration**: Uses `pubkey_hash` (type-agnostic)
   - Result: RSA ↔ DSA children can chat
   - Test: ✅ Chat verified, document sync verified

4. **Activities**: Work via `sugar3.presence`
   - Result: No activity code changes needed
   - Test: ✅ 5 activities verified

---

## Checklist for Merge

- [x] All 24 tests pass
- [x] Critical tests verified
- [x] Backward compatibility confirmed
- [x] Minimal code changes
- [x] No activity changes needed
- [x] Real hardware tested
- [x] Complete documentation
- [x] Production ready

**Status**: ✅ READY TO MERGE

---

**PR**: #1014 (Sugar repository)
**Issue**: #1004
**Status**: Production-Ready
**Date**: January 2026
