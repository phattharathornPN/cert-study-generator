# -*- coding: utf-8 -*-
"""Build dist/ -- deploy-ready copy of the site.

Copies index.html + output/ into dist/, skipping slide.pptx (not used by
the website, and roughly doubles the deploy size for nothing).

Run this AFTER build_site.py, right before `wrangler pages deploy dist`.
"""
import os
import shutil

DIST_DIR = "dist"
OUTPUT_DIR = "output"
SKIP_FILES = {"slide.pptx"}

if os.path.exists(DIST_DIR):
    shutil.rmtree(DIST_DIR)
os.makedirs(DIST_DIR)

shutil.copy("index.html", os.path.join(DIST_DIR, "index.html"))

dist_output = os.path.join(DIST_DIR, OUTPUT_DIR)
total_bytes = 0
n_files = 0

for root, dirs, files in os.walk(OUTPUT_DIR):
    rel = os.path.relpath(root, OUTPUT_DIR)
    dest_dir = os.path.join(dist_output, rel) if rel != "." else dist_output
    os.makedirs(dest_dir, exist_ok=True)
    for fname in files:
        if fname in SKIP_FILES:
            continue
        src = os.path.join(root, fname)
        dst = os.path.join(dest_dir, fname)
        shutil.copy(src, dst)
        total_bytes += os.path.getsize(src)
        n_files += 1

print(f"dist/ built: {n_files} files, {total_bytes / 1024 / 1024:.1f} MB")
print("Deploy with: npx wrangler pages deploy dist --project-name ccnp-encor-study")
