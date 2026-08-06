#!/usr/bin/env bash
# Copy the things that cannot come from git to the remote box.
#
#     ./deploy/seed_remote.sh user@192.168.2.153 [remote-repo-path]
#
#   .env             notebook ids
#   CCNA/output/     finished summaries (~3 MB)
#
# CCNP v1's output/ is deliberately excluded: the remote box rebuilds CCNP
# from the v2 topic list into output_v2/, so shipping 2.7 GB of v1 artefacts
# there would accomplish nothing.
#
# *** This script no longer copies auth, and must not be made to again. ***
#
# Google sessions copied onto another machine die roughly 1h45m later, every
# time -- measured twice on 2026-08-02 (seeded 23:35 -> dead 01:27; reseeded
# 10:12 -> dead 11:56), costing an 8-hour overnight stall. Concurrent use,
# egress IP and quota were each ruled out; the only remaining variable was
# that the session had been created elsewhere. A session created on the box
# itself ran 3.5 hours straight with no auth error at all.
#
# So sign in on the box: ./deploy/desktop_login.sh [profile]
set -euo pipefail

DEST="${1:?usage: seed_remote.sh user@host [remote-repo-path]}"
RPATH="${2:-~/cert-study-generator}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== .env"
scp .env "$DEST:$RPATH/.env"

echo "== CCNA summaries"
if command -v rsync >/dev/null 2>&1; then
  rsync -az --info=stats1 CCNA/output/ "$DEST:$RPATH/CCNA/output/"
else
  ssh "$DEST" "mkdir -p '$RPATH/CCNA'"
  scp -rq CCNA/output "$DEST:$RPATH/CCNA/"
fi

echo
echo "done. Auth is NOT part of this step -- sign in on the box itself:"
echo "    ssh $DEST 'cd $RPATH && ./deploy/desktop_login.sh default'"
