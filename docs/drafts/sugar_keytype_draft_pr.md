# Draft PR: Replace DSA with RSA‑2048 for new profiles; preserve identity and mixed‑peer collaboration

## Summary
Replace deprecated DSA with RSA‑2048 for new profiles; keep existing identities stable and ensure collaboration continues across mixed DSA/RSA peers. Focus key handling in toolkit layers, keep Sugar change minimal.

## Rationale
- OpenSSH 10.0 removes DSA support, completing deprecation begun in 2015 (release 2025‑04‑09).
- RSA‑2048 provides good interoperability and performance for low‑powered devices.
- Ed25519 can follow as an opt‑in improvement once assumptions tied to ssh‑rsa are audited.

## Scope
- Sugar: switch new key generation from DSA → RSA‑2048 (no change if keys already exist).
- sugar‑toolkit‑gtk3 and gtk4:
  - Load/advertise multiple public keys when present; prefer RSA when available.
  - Preserve `privkey_hash` for existing profiles (identity continuity).
  - Keep `get_pubkey()` behavior for call‑sites; add a helper (e.g., `get_pubkeys()`) when multiple keys are exposed.
- Activities: rely on presence/share APIs; no direct key management expected.

## Migration & Compatibility
- On OpenSSH ≥10.0, if a profile has only DSA:
  - Generate an additional RSA‑2048 keypair (do not delete DSA).
  - Keep `privkey_hash` stable.
  - Advertise/accept both keys; negotiate RSA when both sides support it.

## Tests (Telepathy, 2–3 VMs on private network)
- Matrix:
  - A (DSA‑only, OpenSSH <10) ↔ B (RSA‑only, OpenSSH ≥10)
  - A (DSA‑only) ↔ C (DSA+RSA)
  - B (RSA‑only) ↔ C (DSA+RSA)
- Verify: presence, invites, join shared activity, file transfer.
- Collect: Sugar logs, Telepathy logs, any key‑type errors, timings (keygen, join).

## Acceptance
- No regression across the matrix.
- No destructive migration; identities remain stable.
- Clear follow‑up path to add Ed25519 option after assumption audit.

## Notes
- Minimal testbed scaffold included under `testbeds/sugar-collab/` (Vagrant, 3 VMs); GUI Telepathy tests recommended with full desktop VMs.
- Open questions addressed by test results: mixed peers behavior and performance on low‑spec devices.
