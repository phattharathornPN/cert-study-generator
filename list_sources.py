import asyncio
import os
import sys
from notebooklm import NotebookLMClient

NOTEBOOK_ID = os.environ.get("NOTEBOOK_ID")
if not NOTEBOOK_ID:
    print("ERROR: NOTEBOOK_ID environment variable not set (see .env.example).")
    sys.exit(1)


async def main():
    async with NotebookLMClient.from_storage() as client:
        sources = await client.sources.list(NOTEBOOK_ID)
        topic_srcs = [s for s in sources if s.title and s.title.startswith("[SRC ")]
        other_srcs = [s for s in sources if not (s.title and s.title.startswith("[SRC "))]
        print(f"Total sources: {len(sources)} / 300")
        print(f"\n-- Original sources ({len(other_srcs)}):")
        for s in other_srcs:
            print(f"  - {s.title}")
        print(f"\n-- Per-topic [SRC] sources ({len(topic_srcs)}):")
        ids = sorted((s.title or "")[5:10] for s in topic_srcs)
        print("  " + ", ".join(ids))


asyncio.run(main())
