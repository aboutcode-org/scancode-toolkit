#!/usr/bin/env bash
set -euo pipefail

echo "OpenSSH version:" && ssh -V || true

mkdir -p "$HOME/.sugar-test/keys"
if [ ! -f "$HOME/.sugar-test/keys/id_rsa" ]; then
  echo "Generating RSA-2048 test key..."
  ssh-keygen -q -t rsa -b 2048 -f "$HOME/.sugar-test/keys/id_rsa" -N "" -C ""
fi

ls -l "$HOME/.sugar-test/keys"
echo "Done."
