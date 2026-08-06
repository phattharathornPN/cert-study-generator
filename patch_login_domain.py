# -*- coding: utf-8 -*-
"""Teach notebooklm-py's browser login about Google's "Gemini Notebook" rebrand.

Google now serves newer accounts from notebook.google.com and permanently
redirects notebooklm.google.com there. notebooklm-py (0.7.3 and 0.8.0rc1)
still waits for the *old* host during interactive login:

    page.wait_for_url(f"{get_base_url()}/**", ...)   # notebooklm.google.com

so for an account on the new domain the wait can never succeed and every
`notebooklm login --browser chrome` ends in "Login not detected within 5
minutes" -- even though sign-in actually worked.

This widens *only* the host comparison used to detect a completed login.
get_base_url() is left untouched, because the RPC API still lives on
notebooklm.google.com and the captured cookies are .google.com-scoped, so
they authenticate fine either way.

Re-run this after any notebooklm-py upgrade; it is idempotent.

  python patch_login_domain.py          # apply
  python patch_login_domain.py --check  # report status only
"""
import glob
import sys

NEW_HOST = "notebook.google.com"

OLD_FN = '''def url_matches_base_host(url: str) -> bool:
    """Return True when ``url`` is on the configured NotebookLM host."""
    current_host = (urlparse(url).hostname or "").lower()
    return current_host == get_base_host().lower()'''

NEW_FN = '''def url_matches_base_host(url: str) -> bool:
    """Return True when ``url`` is on the configured NotebookLM host.

    LOCAL PATCH (patch_login_domain.py): also accept notebook.google.com, the
    host Google's "Gemini Notebook" rebrand redirects to. Only this comparison
    is widened -- get_base_url() still points at notebooklm.google.com for the
    API, and the cookies are .google.com-scoped either way.
    """
    current_host = (urlparse(url).hostname or "").lower()
    return current_host in {get_base_host().lower(), "notebook.google.com"}'''

# 0.7.3+ passes wait_until="commit"; 0.7.2 does not. Handle both.
WAIT_VARIANTS = [
    ('page.wait_for_url(f"{get_base_url()}/**", wait_until="commit", timeout=300_000)',
     'page.wait_for_url(url_matches_base_host, wait_until="commit", timeout=300_000)'),
    ('page.wait_for_url(f"{get_base_url()}/**", timeout=300_000)',
     'page.wait_for_url(url_matches_base_host, timeout=300_000)'),
]


def target_files():
    """Login modules in every notebooklm-py install we can find.

    Covers the Linux uv-tool env, a project .venv, and -- because this repo
    is driven from Windows too -- the Windows uv-tool env, whose site-packages
    lives under Lib/ (capital L) with no python* version directory.
    """
    import os

    home = os.path.expanduser("~")
    roots = [
        # Linux uv tool
        f"{home}/.local/share/uv/tools/notebooklm-py/lib/python*/site-packages",
        "/home/jetdream/.local/share/uv/tools/notebooklm-py/lib/python*/site-packages",
        # project venv (either layout)
        ".venv/lib/python*/site-packages",
        ".venv/Lib/site-packages",
        # Windows uv tool
        f"{home}/AppData/Roaming/uv/tools/notebooklm-py/Lib/site-packages",
        os.path.join(os.environ.get("APPDATA", ""), "uv/tools/notebooklm-py/Lib/site-packages"),
    ]
    modules = [
        "notebooklm/cli/services/playwright_login.py",
        "notebooklm/_auth/browser_capture.py",
    ]

    found = []
    for root in roots:
        if not root.strip("/"):
            continue
        for mod in modules:
            found.extend(glob.glob(f"{root}/{mod}"))
    # same file can match two patterns (e.g. $HOME vs $APPDATA) -- dedupe
    return sorted({os.path.realpath(p) for p in found})


def main():
    check_only = "--check" in sys.argv
    files = target_files()
    if not files:
        print("No notebooklm login module found -- is notebooklm-py installed?")
        sys.exit(1)

    for path in files:
        with open(path, encoding="utf-8") as f:
            src = f.read()

        already = NEW_HOST in src
        can_fn = OLD_FN in src
        wait_hit = next(((o, n) for o, n in WAIT_VARIANTS if o in src), None)

        short = path.replace("/home/jetdream", "~").replace("\\", "/")
        if already and not (can_fn or wait_hit):
            print(f"  already patched : {short}")
            continue
        if not (can_fn or wait_hit):
            print(f"  NO MATCH (upstream changed?) : {short}")
            continue
        if check_only:
            print(f"  needs patch : {short}")
            continue

        out = src
        if can_fn:
            out = out.replace(OLD_FN, NEW_FN)
        if wait_hit:
            out = out.replace(wait_hit[0], wait_hit[1])
        with open(path, "w", encoding="utf-8") as f:
            f.write(out)
        bits = []
        if can_fn:
            bits.append("host check")
        if wait_hit:
            bits.append("wait_for_url")
        print(f"  patched ({', '.join(bits)}) : {short}")

    if not check_only:
        print("\nNow run:  notebooklm -p <profile> login --browser chrome")


if __name__ == "__main__":
    main()
