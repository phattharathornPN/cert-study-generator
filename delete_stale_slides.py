# -*- coding: utf-8 -*-
"""Delete slide.pdf / slide.pptx in folders whose summary_th.md is NEWER than
the slide -- i.e. the summary was regenerated (with better sources) but the
slide still reflects the old summary, so the slide must be regenerated.

Run with --apply to actually delete; default is a dry run.
Backup at output_backup_pre_136/ still holds every old slide if needed.
"""
import os
import sys

OUTPUT_DIR = "output"
FILES = ("slide.pdf", "slide.pptx")


def main():
    apply = "--apply" in sys.argv
    stale = []

    for name in sorted(os.listdir(OUTPUT_DIR)):
        d = os.path.join(OUTPUT_DIR, name)
        if not os.path.isdir(d):
            continue
        summary = os.path.join(d, "summary_th.md")
        pdf = os.path.join(d, "slide.pdf")
        if not (os.path.exists(summary) and os.path.exists(pdf)):
            continue
        if os.path.getmtime(summary) > os.path.getmtime(pdf):
            stale.append(name)

    for name in stale:
        d = os.path.join(OUTPUT_DIR, name)
        for fname in FILES:
            p = os.path.join(d, fname)
            if os.path.exists(p):
                if apply:
                    os.remove(p)
        print(f"{'DELETED' if apply else 'WOULD DELETE'} slides in: {name}")

    print(f"\n{'Deleted' if apply else 'Would delete'} slides in {len(stale)} folders")
    if not apply:
        print("Dry run only. Re-run with --apply to delete for real.")


if __name__ == "__main__":
    main()
