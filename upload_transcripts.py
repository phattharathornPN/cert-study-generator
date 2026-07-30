# -*- coding: utf-8 -*-
"""Upload manually-copied Udemy lecture transcripts into your NotebookLM
notebook as text sources -- one source per file in udemy_transcripts/.

Workflow:
1. On Udemy, open each lecture's transcript panel, select all, copy.
2. Paste into a plain .txt file grouped by course section (not per-lecture --
   that'd be too many files). Separate lectures within the file with a
   "## Lecture N: Title" heading so it stays readable, e.g.:

     udemy_transcripts/01_architecture.txt
     udemy_transcripts/02_virtualization.txt
     ...

3. Run this script. It uploads each .txt file as its own source, titled
   "[Udemy] <filename>", skipping files it already uploaded (tracked by
   filename, safe to re-run after adding more files).

This is for your own private study notebook only -- don't redistribute
generated content derived from paid course material.
"""
import asyncio
import os
import sys

from notebooklm import NotebookLMClient

NOTEBOOK_ID = os.environ.get("NOTEBOOK_ID")
if not NOTEBOOK_ID:
    print("ERROR: NOTEBOOK_ID environment variable not set (see .env.example).")
    sys.exit(1)

TRANSCRIPTS_DIR = "udemy_transcripts"
TITLE_PREFIX = "[Udemy]"


async def main():
    if not os.path.isdir(TRANSCRIPTS_DIR):
        os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
        print(f"Created {TRANSCRIPTS_DIR}/ -- put your .txt transcript files there and re-run.")
        return

    files = sorted(f for f in os.listdir(TRANSCRIPTS_DIR) if f.endswith(".txt"))
    if not files:
        print(f"No .txt files found in {TRANSCRIPTS_DIR}/ yet.")
        return

    async with NotebookLMClient.from_storage() as client:
        existing = await client.sources.list(NOTEBOOK_ID)
        existing_titles = {s.title for s in existing if s.title}

        for fname in files:
            title = f"{TITLE_PREFIX} {fname}"
            if title in existing_titles:
                print(f"SKIP (already uploaded): {fname}")
                continue

            path = os.path.join(TRANSCRIPTS_DIR, fname)
            with open(path, encoding="utf-8") as f:
                content = f.read().strip()
            if not content:
                print(f"SKIP (empty file): {fname}")
                continue

            print(f"Uploading: {fname} ({len(content)} chars)...")
            try:
                await client.sources.add_text(NOTEBOOK_ID, title, content, wait=True)
                print(f"  OK")
            except Exception as e:
                print(f"  ERROR: {e}")

    print("\nDone. These sources now feed into every future summary/slide")
    print("generation for topics whose NotebookLM chat calls reference them.")


if __name__ == "__main__":
    asyncio.run(main())
