# -*- coding: utf-8 -*-
"""Resolve which certification the current run belongs to.

Selected by the ``CERT`` environment variable; defaults to ``ccnp`` so every
existing command, script and in-flight run behaves exactly as it did before
this module existed.

    CERT=ccna python summary_parallel.py

Scripts should read EXAM_NAME / OUTPUT_DIR / TOPICS from here rather than
hardcoding them.
"""
import importlib
import os
import sys

CERT = os.environ.get("CERT", "ccnp").strip().lower() or "ccnp"

try:
    _cfg = importlib.import_module(f"certs.{CERT}")
except ModuleNotFoundError as exc:
    if getattr(exc, "name", "") == f"certs.{CERT}":
        here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs")
        known = sorted(
            f[:-3] for f in os.listdir(here)
            if f.endswith(".py") and not f.startswith("__")
        )
        print(f"ERROR: unknown CERT '{CERT}'. Available: {', '.join(known)}")
        sys.exit(1)
    raise

EXAM_NAME = _cfg.EXAM_NAME
OUTPUT_DIR = _cfg.OUTPUT_DIR
SITE_DIR = _cfg.SITE_DIR
DIST_DIR = _cfg.DIST_DIR
SECTION_TITLES = _cfg.SECTION_TITLES
SLIDE_FORMATS = _cfg.SLIDE_FORMATS
TOPICS = _cfg.TOPICS
NOTEBOOK_ENV = _cfg.NOTEBOOK_ENV

# Each cert names the kind of worked example that actually makes sense for
# it -- a Cisco config walkthrough teaches nothing on a CISSP governance
# topic, and a policy scenario is no substitute for seeing a real forwarding
# path on a networking exam. This was hardcoded to the Cisco/networking
# phrasing inside slides_v2.py until 2026-08-10, so every non-networking cert
# (Security) was quietly told to hunt for "Cisco IOS / IOS-XE" examples on
# topics like professional ethics. Required: every certs/*.py must set this,
# there is no networking-flavored fallback to silently inherit anymore.
SLIDE_INSTRUCTIONS = _cfg.SLIDE_INSTRUCTIONS

# Same story, same date, other end of the pipeline: this was hardcoded inside
# summary_only.py (with a literal "CCNP" in the closing line, not even
# EXAM_NAME) and produced a fabricated Cisco-config section in 354 of
# Security's first 357 summaries. Required, no fallback, same as above.
SUMMARY_PROMPT = _cfg.SUMMARY_PROMPT


def notebook_id() -> str:
    """Notebook ID for the active cert, or exit with a usable message."""
    value = os.environ.get(NOTEBOOK_ENV)
    if not value:
        print(f"ERROR: {NOTEBOOK_ENV} is not set (needed for {EXAM_NAME}).")
        print(f"  Add it to .env:  echo '{NOTEBOOK_ENV}=<notebook-id>' >> .env")
        sys.exit(1)
    return value
