#!/usr/bin/env bash
# Thin alias: same tool as ./ccnp, different exam config (certs/cc.py).
exec env CERT=cc "$(dirname "${BASH_SOURCE[0]}")/ccnp" "$@"
