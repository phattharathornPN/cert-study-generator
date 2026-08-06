# -*- coding: utf-8 -*-
"""CCNP ENCOR 350-401 -- the original study pack.

Every value here reproduces what the scripts hardcoded before the per-cert
config layer existed, so the CCNP pipeline behaves identically with or
without CERT set.
"""

# Topic list stays in the top-level topics.py so existing imports and any
# in-flight runs keep working untouched.
from topics import TOPICS  # noqa: F401

EXAM_NAME = "CCNP ENCOR 350-401"
OUTPUT_DIR = "output"
SITE_DIR = "."       # index.html at the repo root
DIST_DIR = "dist"
NOTEBOOK_ENV = "NOTEBOOK_ID"

# The website reads slide.pdf; slide.pptx is kept for offline editing.
SLIDE_FORMATS = ("pdf", "pptx")

SECTION_TITLES = {
    "01": "Enterprise LAN Architecture",
    "02": "Enterprise Routing Network",
    "03": "Virtualization Technologies",
    "04": "Enterprise Wireless Architecture",
    "05": "Network Services",
    "06": "Enterprise Security Architecture",
    "07": "Automation and Assurance",
    "08": "Network Programmability",
}
