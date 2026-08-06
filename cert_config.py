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


def notebook_id() -> str:
    """Notebook ID for the active cert, or exit with a usable message."""
    value = os.environ.get(NOTEBOOK_ENV)
    if not value:
        print(f"ERROR: {NOTEBOOK_ENV} is not set (needed for {EXAM_NAME}).")
        print(f"  Add it to .env:  echo '{NOTEBOOK_ENV}=<notebook-id>' >> .env")
        sys.exit(1)
    return value
