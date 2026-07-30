# -*- coding: utf-8 -*-
"""Restore slide.pdf / slide.pptx from output_backup_pre_136/ into output/.

Matches folders by SLUG (the part after the "SS_NN_" id prefix) rather than
by full folder name, because the 116 -> 136 renumber shifted 43 ids -- the
same topic lives under a different id in the backup than it does now.

Run with --apply to actually copy; default is a dry run.
"""
import os
import shutil
import sys

OUTPUT_DIR = "output"
BACKUP_DIR = "output_backup_pre_136"
FILES = ("slide.pdf", "slide.pptx")


def slug_of(folder_name: str) -> str:
    # "05_07_introducing_qos" -> "introducing_qos"
    parts = folder_name.split("_", 2)
    return parts[2] if len(parts) == 3 else folder_name


def main():
    apply = "--apply" in sys.argv

    backup_by_slug = {}
    for name in os.listdir(BACKUP_DIR):
        path = os.path.join(BACKUP_DIR, name)
        if os.path.isdir(path):
            backup_by_slug.setdefault(slug_of(name), name)

    restored = 0
    already_ok = 0
    no_source = []

    for name in sorted(os.listdir(OUTPUT_DIR)):
        dest_dir = os.path.join(OUTPUT_DIR, name)
        if not os.path.isdir(dest_dir):
            continue
        if os.path.exists(os.path.join(dest_dir, "slide.pdf")):
            already_ok += 1
            continue

        src_name = backup_by_slug.get(slug_of(name))
        if not src_name:
            no_source.append(name)
            continue
        src_dir = os.path.join(BACKUP_DIR, src_name)
        if not os.path.exists(os.path.join(src_dir, "slide.pdf")):
            no_source.append(name)
            continue

        for fname in FILES:
            src = os.path.join(src_dir, fname)
            if os.path.exists(src):
                if apply:
                    shutil.copy2(src, os.path.join(dest_dir, fname))
        print(f"{'RESTORED' if apply else 'WOULD RESTORE'}: {src_name}  ->  {name}")
        restored += 1

    print(f"\nAlready had slides: {already_ok}")
    print(f"{'Restored' if apply else 'Would restore'}: {restored}")
    print(f"No backup source (genuinely new topics): {len(no_source)}")
    for n in no_source:
        print(f"  - {n}")
    if not apply:
        print("\nDry run only. Re-run with --apply to copy for real.")


if __name__ == "__main__":
    main()
