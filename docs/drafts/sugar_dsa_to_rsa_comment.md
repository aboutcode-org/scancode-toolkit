Hi all, quick update with answers and a concrete plan:

- What changed in OpenSSH 10.0: The release explicitly “removes support for the weak DSA signature algorithm,” completing the deprecation begun in 2015 (OpenSSH 10.0 release notes, 2025‑04‑09).
- Key size choice: I propose RSA‑2048 for now. It balances security and performance on low‑powered devices, is widely interoperable, and avoids the extra CPU/memory cost of 4096‑bit RSA. The crypto here protects peer identity/trust for collaboration (invites, presence, file transfer), so responsiveness matters. Ed25519 would be an even better default long‑term (smaller/faster), but several code paths and strings currently assume “ssh‑rsa”; I can follow up to add Ed25519 support once we finish the audit.
- Existing keys: No automatic destructive replacement. On first run with OpenSSH ≥10.0, if a profile has only DSA:
  - Generate a new RSA‑2048 keypair alongside the existing DSA key.
  - Keep the existing privkey_hash so identity/buddy relationships remain stable.
  - Publish/accept both public key types in the profile/toolkit layer, preferring RSA when both sides support it.
- Mixed peers (DSA vs RSA): With the above, collaboration should continue; RSA‑capable peers use RSA, and older peers that still accept DSA can proceed. OpenSSH 10.0 peers won’t accept DSA, so the RSA key ensures forward compatibility. I’ll verify this end‑to‑end with Telepathy.

Scope and locations (no broad churn):
- Sugar: stop generating DSA for new profiles (use RSA‑2048).
- sugar‑toolkit‑gtk3 (and gtk4): load/advertise multiple pubkeys when present, and keep privkey_hash stable; ensure get_pubkey() callers continue to work or add a compatible helper if multiple keys are present.
- Activities: no direct key handling found; they rely on presence/share APIs, so no activity code changes expected.

Minimal test plan (per guidance):
- Two or three VMs on a virtual network with Telepathy.
- Matrix:
  - VM A (existing DSA profile, OpenSSH <10) ↔ VM B (new RSA profile, OpenSSH ≥10).
  - VM A with upgraded Sugar generating RSA alongside DSA ↔ VM C (legacy).
- Verify: presence, invites, joining shared activities, file transfer; capture Sugar logs, Telepathy logs, and any “unknown key type” errors.
- Performance spot check on low‑powered VM: measure profile creation time and a simple collaboration join.

If this direction sounds acceptable, I’ll:
1) Keep the RSA‑2048 generation change in Sugar,
2) Finalize toolkit changes to advertise/accept multiple keys and preserve identity,
3) Post results of the Telepathy matrix tests,
4) Propose a follow‑up to add optional Ed25519 once string/assumption checks are complete.

Reference: OpenSSH 10.0 release notes (2025‑04‑09).