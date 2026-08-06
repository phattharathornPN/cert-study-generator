#!/usr/bin/env bash
# Bootstrap a 24/7 Linux box to run the generators.
#
# Run this ON the remote host, as the user that will own the runs:
#     ./deploy/remote_setup.sh
#
# It is idempotent -- re-run it after a git pull to top up dependencies.
#
# What it deliberately does NOT do: copy credentials. Auth lives in
# ~/.notebooklm/profiles/*/storage_state.json (Google session cookies) and is
# pushed separately from an already-signed-in machine by seed_remote.sh, so
# secrets never pass through the repo.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

say() { printf '\n== %s\n' "$*"; }

say "system packages"
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update -qq
  # Chromium's shared libraries are needed even in headless mode: `auth
  # refresh` drives a real browser, and without them Playwright fails with an
  # unhelpful "browser closed unexpectedly".
  sudo apt-get install -y -qq git curl tmux python3-venv
elif command -v dnf >/dev/null 2>&1; then
  sudo dnf install -y -q git curl tmux python3
else
  echo "unsupported package manager -- install git, curl, tmux, python3 by hand" >&2
fi

say "uv"
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

say "virtualenv + notebooklm"
uv venv .venv
uv pip install --python .venv 'notebooklm-py[browser]'

say "playwright chromium"
# --with-deps pulls the distro libraries Chromium needs on a headless server.
./.venv/bin/python -m playwright install --with-deps chromium

say "sanity check"
./ccnp doctor

cat <<'NEXT'

== next steps

1. From the machine that is already signed in, push credentials and the
   finished CCNA summaries:

       ./deploy/seed_remote.sh <user>@<host>

2. Confirm auth landed:

       ./ccnp auth list
       ./ccnp auth check

3. CCNP v2 reuses the v1 notebook, which still holds the derived [SRC]
   sources from the v1 pack. Drop them before the fresh build or v2 slides
   will quote v1 content:

       CERT=ccnp_v2 ./ccnp clean-src          # dry run first
       CERT=ccnp_v2 ./ccnp clean-src --yes

4. Install the services (see deploy/README.md), or just start a tmux session:

       IDLE_GIVE_UP=0 CERT=ccnp_v2 ./ccnp summary-fast 4

NEXT
