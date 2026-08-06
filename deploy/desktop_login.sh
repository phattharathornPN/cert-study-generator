#!/usr/bin/env bash
# Sign a profile in on the box's own desktop, then hand the session to root.
#
#     ./deploy/desktop_login.sh [profile]        (default: "default")
#
# Run as root over SSH; a browser window appears on the physical console for
# someone sitting at it to complete the Google login.
#
# Three things this encodes, each of which cost an hour to find:
#
#  1. The browser must run as the user who owns the X session, not as root.
#     Chrome started by root on someone else's display opens a window and
#     paints nothing -- a capture of it is a single flat black colour. It is
#     not a GPU, compositor or window-size problem; running the same binary
#     as the session owner renders correctly straight away.
#  2. Chrome opens at 1288x851 on this 1280x720 console, so the window lands
#     partly off-screen and looks like a stray title bar. The console cannot
#     go bigger (RRSetScreenSize -> BadMatch: the VM's video RAM is set too
#     low in ESXi), so the window is resized after it appears.
#  3. patch_login_domain.py must be applied to the *desktop user's* venv too.
#     Without it, accounts served from notebook.google.com log in fine but
#     the CLI never notices and reports "Login not detected within 5 minutes".
#
# Sessions created this way are native to this machine. Cookies copied in
# from another machine have twice died about 1h45m later.
set -uo pipefail

PROFILE="${1:-default}"
DESK_USER="${DESK_USER:-admindtc}"
DESK_HOME="$(getent passwd "$DESK_USER" | cut -d: -f6)"
DESK_VENV="$DESK_HOME/nlm"
OUT="$DESK_HOME/ss_$PROFILE.json"
DEST="/root/.notebooklm/profiles/$PROFILE/storage_state.json"

[[ $EUID -eq 0 ]] || { echo "run as root" >&2; exit 1; }

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export DISPLAY="${DISPLAY:-:0}"
export XAUTHORITY="$DESK_HOME/.Xauthority"

as_desk() { sudo -u "$DESK_USER" env DISPLAY="$DISPLAY" XAUTHORITY="$XAUTHORITY" HOME="$DESK_HOME" "$@"; }

# --- one-time setup for the desktop user ------------------------------------
if [[ ! -x "$DESK_VENV/bin/python" ]]; then
  echo "== creating $DESK_USER's notebooklm venv"
  sudo -u "$DESK_USER" bash -lc "cd \$HOME && \
    (command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh) && \
    export PATH=\$HOME/.local/bin:\$PATH && \
    uv venv \$HOME/nlm -q && uv pip install --python \$HOME/nlm -q 'notebooklm-py[browser]'" || exit 1
fi

# patch_login_domain.py finds a venv by globbing, and ".venv next to cwd" is
# the pattern that matches here.
if [[ ! -e "$DESK_HOME/.venv" ]]; then
  sudo -u "$DESK_USER" ln -s nlm "$DESK_HOME/.venv"
fi
install -m 644 "$ROOT/patch_login_domain.py" /tmp/patch_login_domain.py
sudo -u "$DESK_USER" bash -lc "cd \$HOME && \$HOME/nlm/bin/python /tmp/patch_login_domain.py" | tail -1

# --- launch -----------------------------------------------------------------
rm -f "$OUT"
echo "== opening Google login for profile '$PROFILE' on $DISPLAY"
# --fresh wipes the cached browser profile first. Without it the window opens
# already signed in as whoever logged in last, the CLI captures that account
# immediately, and you end up with two profile names bound to one session --
# useless as a failover spare, because both die together.
as_desk setsid nohup "$DESK_VENV/bin/python" -m notebooklm login \
  --storage "$OUT" --browser chrome --fresh > /tmp/desktop_login.log 2>&1 < /dev/null &

# Give the window time to map, then pull it fully on-screen.
sleep 12
for w in $(xdotool search --name "." 2>/dev/null); do
  name="$(xdotool getwindowname "$w" 2>/dev/null)" || continue
  case "$name" in
    *Chrome*) wmctrl -i -r "$w" -e 0,0,0,1272,688; xdotool windowraise "$w"
              echo "   window fitted: $name" ;;
  esac
done

echo "== waiting for the login to be detected (up to 5 min)"
for _ in $(seq 1 60); do
  [[ -s "$OUT" ]] && break
  sleep 5
done

if [[ ! -s "$OUT" ]]; then
  echo "FAILED -- no session written. Last lines:" >&2
  tail -5 /tmp/desktop_login.log >&2
  exit 1
fi

# --- hand over to root ------------------------------------------------------
GOT="$(grep -m1 '^Account: ' /tmp/desktop_login.log | sed 's/^Account: //')"
echo "== captured: ${GOT:-unknown}"
# Two profiles pointing at one Google account look like redundancy and are
# not: a single revocation takes both out at once.
if [[ -n "$GOT" ]]; then
  clash="$(grep -rl "\"email\": \"$GOT\"" /root/.notebooklm/profiles/*/context.json 2>/dev/null \
           | xargs -r -n1 dirname | xargs -r -n1 basename | grep -v "^$PROFILE$" | tr '\n' ' ')"
  [[ -n "$clash" ]] && echo "   WARNING: $GOT is already bound to: $clash" >&2
fi

mkdir -p "$(dirname "$DEST")"
[[ -f "$DEST" ]] && cp "$DEST" "$DEST.dead-$(date +%Y%m%d-%H%M)"
install -o root -g root -m 600 "$OUT" "$DEST"
rm -f "$OUT"

cd "$ROOT"
if timeout 120 ./ccnp auth check "${PROFILE#default}" 2>/dev/null | grep -q '"status": "ok"'; then
  echo "== profile '$PROFILE' is live"
  systemctl start cert-handover.service
  echo "== handover triggered; work resumes on its own"
else
  echo "session was written but auth check failed -- inspect manually" >&2
  exit 1
fi
