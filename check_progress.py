import os
from run import TOPICS, topic_to_slug

OUTPUT_DIR = "output"
missing = []
done = 0

for t in TOPICS:
    folder = os.path.join(OUTPUT_DIR, f"{t['id']}_{topic_to_slug(t['topic'])}")
    if os.path.exists(os.path.join(folder, "slide.pdf")):
        done += 1
    else:
        missing.append(t)

print(f"Done: {done} / {len(TOPICS)}")
print(f"Missing: {len(missing)}")
for t in missing:
    print(f"  {t['id']}  {t['topic']}")
