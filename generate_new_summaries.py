# -*- coding: utf-8 -*-
"""Generate summary_th.md for topics that don't have one yet (the 19 newly
added deep-dive / gap-fill topics from the 90 -> 109 expansion).

Does NOT touch slides -- run slides_only.py afterwards to pin sources and
generate slide decks for these same topics.

Usage:
  python generate_new_summaries.py [--profile NAME] [--start-id xx_yy]
"""
import asyncio
import os
import re
import sys
from notebooklm import NotebookLMClient

from run import TOPICS, topic_to_slug, build_focus_prompt

NOTEBOOK_ID = os.environ.get("NOTEBOOK_ID")
if not NOTEBOOK_ID:
    print("ERROR: NOTEBOOK_ID environment variable not set (see .env.example).")
    sys.exit(1)
OUTPUT_DIR = "output"
SLEEP_BETWEEN_TOPICS = 15
RETRY_LIMIT = 1


class AuthExpiredError(Exception):
    pass


async def run_with_retry(coro_fn, label: str):
    rate_limit_retries = 5
    attempt = 0
    while True:
        try:
            return await coro_fn()
        except Exception as e:
            if "Unauthenticated" in str(e) or "Authentication expired" in str(e):
                raise AuthExpiredError(
                    f"{label}: session expired. Run 'python -m notebooklm auth refresh' "
                    f"then resume with --start-id."
                ) from e
            if "RateLimitError" in str(e) or "RateLimit" in type(e).__name__:
                if rate_limit_retries > 0:
                    rate_limit_retries -= 1
                    print(f"  WARNING: {label} rate limited, waiting 90s before retry...")
                    await asyncio.sleep(90)
                    continue
                print(f"  ERROR: {label} skipped (rate limit exhausted): {e}")
                return None
            if attempt < RETRY_LIMIT:
                attempt += 1
                print(f"  WARNING: {label} failed ({e}), retrying...")
                await asyncio.sleep(5)
            else:
                print(f"  ERROR: {label} skipped: {e}")
                return None


async def process_topic(client, t: dict):
    tid = t["id"]
    topic = t["topic"]
    slug = topic_to_slug(topic)
    folder = os.path.join(OUTPUT_DIR, f"{tid}_{slug}")
    md_path = os.path.join(folder, "summary_th.md")

    if os.path.exists(md_path):
        print(f"[{tid}] {topic} -- SKIP (summary_th.md already exists)")
        return False

    os.makedirs(folder, exist_ok=True)
    print(f"\n{'=' * 60}")
    print(f"[{tid}] {topic}")
    print(f"{'=' * 60}")
    print("  Prompting focused summary...")

    result = await run_with_retry(
        lambda: client.chat.ask(NOTEBOOK_ID, build_focus_prompt(topic)),
        "chat.ask"
    )
    if result:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# {topic}\n\n{result.answer}")
        print("  OK: summary_th.md saved")
        return True
    else:
        print("  ERROR: summary generation failed (see warnings above)")
        return True  # still attempted -> still worth the inter-topic sleep


async def main():
    start_id = None
    if "--start-id" in sys.argv:
        start_id = sys.argv[sys.argv.index("--start-id") + 1]

    profile = None
    if "--profile" in sys.argv:
        profile = sys.argv[sys.argv.index("--profile") + 1]

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    async with NotebookLMClient.from_storage(profile=profile) as client:
        started = start_id is None
        total = len(TOPICS)

        for i, t in enumerate(TOPICS):
            if not started:
                if t["id"] == start_id:
                    started = True
                else:
                    continue

            try:
                did_work = await process_topic(client, t)
            except AuthExpiredError as e:
                print(f"\n  STOPPED: {e}")
                print(f"  Then resume with: python generate_new_summaries.py --start-id {t['id']}")
                return

            if did_work:
                await asyncio.sleep(SLEEP_BETWEEN_TOPICS)

    print("\nDone -- all missing summaries generated (or attempted).")


if __name__ == "__main__":
    asyncio.run(main())
