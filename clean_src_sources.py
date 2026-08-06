# -*- coding: utf-8 -*-
"""Delete the derived "[SRC xx_yy] ..." sources from the notebook.

Those are not reference material -- slides_v2.py uploads each topic's own
summary_th.md back into the notebook so slide generation can be pinned to a
single source. That makes them self-referential: when chat.ask regenerates a
summary it reads back the model's own previous output alongside the real
Cisco documentation.

Before a full regeneration you want them gone, so summaries are built from
the actual reference sources only. They are recreated automatically on the
next slides_v2.py run.

Dry run (default -- shows what would go, deletes nothing):
  python clean_src_sources.py

Actually delete:
  python clean_src_sources.py --yes
"""
import asyncio
import sys

from notebooklm import NotebookLMClient

from run import NOTEBOOK_ID

PREFIX = "[SRC "


async def main():
    confirmed = "--yes" in sys.argv

    async with NotebookLMClient.from_storage() as client:
        sources = await client.sources.list(NOTEBOOK_ID)
        derived = [s for s in sources if s.title and s.title.startswith(PREFIX)]
        keep = [s for s in sources if not (s.title and s.title.startswith(PREFIX))]

        print(f"Total sources     : {len(sources)}")
        print(f"Derived [SRC ...] : {len(derived)}  <- target")
        print(f"Reference sources : {len(keep)}  <- kept")

        if not derived:
            print("\nNothing to clean.")
            return

        if not confirmed:
            print("\nWould delete:")
            for s in sorted(derived, key=lambda x: x.title):
                print(f"  {s.title}")
            print(f"\nDRY RUN -- nothing deleted. Re-run with --yes to delete {len(derived)}.")
            return

        print(f"\nDeleting {len(derived)} derived sources...")
        failed = 0
        for i, s in enumerate(sorted(derived, key=lambda x: x.title), 1):
            try:
                await client.sources.delete(NOTEBOOK_ID, s.id)
                print(f"  [{i}/{len(derived)}] deleted {s.title}")
            except Exception as e:
                failed += 1
                print(f"  [{i}/{len(derived)}] FAILED {s.title}: {e}")
            await asyncio.sleep(0.5)

        remaining = await client.sources.list(NOTEBOOK_ID)
        print(f"\nDone. {failed} failure(s). Notebook now has {len(remaining)} sources.")


if __name__ == "__main__":
    asyncio.run(main())
