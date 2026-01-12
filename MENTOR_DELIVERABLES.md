# Sugar DSA → RSA-2048: Mentor Deliverables Summary

## ✅ Completed

### 1. Code Audit & Analysis
- Located and analyzed Sugar keygen code (`src/jarabe/intro/window.py` line 82).
- Identified toolkit layer (`sugar-toolkit-gtk3/src/sugar3/profile.py`) key usage patterns.
- Confirmed activities rely on presence/share APIs (no direct key handling needed).
- Documented all files modified and rationale in `MIGRATION_DSA_TO_RSA.md`.

### 2. First Code Change: Sugar RSA Keygen
**File**: `sugar/src/jarabe/intro/window.py` (line 82)
```diff
- cmd = "ssh-keygen -q -t dsa -f %s -C '' -N ''" % (keypath, )
+ cmd = "ssh-keygen -q -t rsa -b 2048 -f %s -C '' -N ''" % (keypath, )
```
✅ **Status**: DONE and committed to the workspace.

### 3. Comprehensive Issue Comment
- Answers all open mentor questions:
  - ✅ Existing key replacement strategy (preserve DSA, add RSA alongside).
  - ✅ Why RSA-2048 (performance on low-powered devices).
  - ✅ Mixed-peer collaboration behavior (graceful degradation).
- Proposes full scope (Sugar + toolkit-gtk3/gtk4 + activities).
- Outlines testing matrix and acceptance criteria.
- Ready to post to the issue.
- **File**: `ISSUE_COMMENT_DSA_TO_RSA.md`

### 4. Migration & Rationale Document
- Explains OpenSSH 10.0 change and impact.
- Details migration strategy for existing profiles.
- Justifies RSA-2048 over alternatives (4096, Ed25519).
- Provides clear next steps and file mapping.
- **File**: `MIGRATION_DSA_TO_RSA.md`

---

## 🔄 In Progress / Remaining

### 1. Toolkit Changes (sugar-toolkit-gtk3 & gtk4)
**What needs doing**:
- Update `profile.py` to load/advertise multiple public keys.
- Keep `get_pubkey()` returning preferred key (RSA if present, else DSA).
- Ensure `privkey_hash` remains stable (not recalculated when RSA is added).
- Add preference logic to use RSA for new collaborations.

**Acceptance**: Activities continue to work; no breaking changes to callers.

### 2. Testing: Telepathy Collaboration Matrix
**What needs doing**:
- Set up 2–3 VMs on a private network with Telepathy.
- Run test matrix:
  - DSA-only ↔ DSA+RSA (expect success)
  - RSA-only ↔ DSA+RSA (expect success)
  - DSA-only ↔ RSA-only (expect graceful failure; document why)
- Collect Sugar logs, Telepathy logs, timing data.

**Acceptance**: No regression in the "expect success" cases.

### 3. Draft PR
**What needs doing**:
- Create a PR in sugar repo with the line 82 change.
- PR description links to or includes the analysis and testing plan.
- Mark as draft; outline toolkit changes and tests as follow-up tasks.

**Acceptance**: Mentor reviews and confirms direction before full implementation.

---

## 📋 How to Proceed

### Immediately (this session):
1. **Post the issue comment** (use `ISSUE_COMMENT_DSA_TO_RSA.md` text).
2. **Show the mentor**:
   - The code change (line 82).
   - The migration strategy (existing keys preserved, RSA added alongside).
   - The testing plan and matrix.
   - Answers to their three open questions.

### Next (after mentor feedback):
1. Finalize toolkit changes (if mentor approves direction).
2. Run Telepathy tests and post logs to the draft PR.
3. Adjust based on mentor feedback (e.g., key size, test matrix adjustments).

---

## 📁 Key Files in This Workspace

- **Code change**: `sugar/src/jarabe/intro/window.py` (line 82) — ✅ DONE
- **Analysis**: `sugar/MIGRATION_DSA_TO_RSA.md` — For PR or internal reference
- **Issue comment**: `sugar/ISSUE_COMMENT_DSA_TO_RSA.md` — Ready to post
- **VM testbed**: `testbeds/sugar-collab/` — Vagrant scaffold and scripts (from earlier work)

---

## 🎯 What the Mentor Wants (Checklist)

✅ Evidence that you understand the problem (OpenSSH 10.0, DSA removal, impact on Sugar).
✅ Migration plan for existing profiles (don't delete DSA; add RSA alongside; preserve `privkey_hash`).
✅ Explanation of mixed-peer behavior (graceful degradation, shared key types work).
✅ Rationale for key size choice (RSA-2048: performance on low-powered devices).
✅ Scope across Sugar + toolkits + activities (no activity code changes).
✅ Testing plan (Telepathy matrix with logs).
✅ Code change that's minimal and safe (line 82: dsa → rsa -b 2048).

**Result**: A thoughtful, evidence-driven solution that respects existing users and collaborations.

---

## 🚀 Ready to Post?

Yes! All materials are prepared. You can:
1. Copy `ISSUE_COMMENT_DSA_TO_RSA.md` and post it to the GitHub issue.
2. Link to the analysis in `MIGRATION_DSA_TO_RSA.md` if asked.
3. Show the code change and explain it's the first step; toolkit and tests follow.

The mentor will see you've done the homework: audit, rationale, migration plan, testing strategy—and you're asking for feedback before diving into toolkit changes and VMs.
