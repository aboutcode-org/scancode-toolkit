# Sugar Collaboration Testbed (Vagrant)

This testbed creates three VMs (vm-a, vm-b, vm-c) on a private network to verify Sugar collaboration across mixed key types (DSA legacy vs RSA-2048) after OpenSSH 10.0 removed DSA.

## Prerequisites
- VirtualBox installed
- Vagrant installed

## Bring up VMs
```bash
vagrant up
```

Override the base box (defaults to `generic/fedora40`):
```bash
BOX=bento/ubuntu-22.04 vagrant up
```

## Inside each VM (CLI sanity checks)
```bash
ssh -V
mkdir -p ~/.sugar-test/keys
ssh-keygen -q -t rsa -b 2048 -f ~/.sugar-test/keys/id_rsa -N "" -C ""
ls -l ~/.sugar-test/keys
```

If testing a legacy DSA path on older OpenSSH (<10.0), generate DSA where available:
```bash
ssh-keygen -q -t dsa -f ~/.sugar-test/keys/id_dsa -N "" -C ""
```

## Telepathy + Sugar GUI tests (recommended)
Use full desktop VMs with Sugar and Telepathy installed/enabled. Test matrix:
- A (DSA-only) ↔ B (RSA-only)
- A (DSA-only) ↔ C (DSA+RSA)
- B (RSA-only) ↔ C (DSA+RSA)

Verify: presence, invites, join shared activity, file transfer.
Collect: Sugar logs, Telepathy logs, any key-type errors, timing for keygen and join.

## Logs (examples, adjust per distro/service names)
```bash
journalctl --user -u sugar --since "10 min ago" -o short-precise
journalctl -u telepathy-gabble --since "10 min ago" -o short-precise
journalctl -u telepathy-salut --since "10 min ago" -o short-precise
journalctl -u avahi-daemon --since "10 min ago" -o short-precise
```

## Cleanup
```bash
vagrant destroy -f
```
