# -*- coding: utf-8 -*-
"""Generate summaries with several topics in flight at once.

summary_only.py walks the list one topic at a time, so a full run is
~136 x 100s = 4+ hours of mostly waiting on the server. NotebookLM publishes
no per-minute rate limit (only a daily chat quota), so overlapping a handful
of requests is the single biggest speedup available.

Two other differences from summary_only.py:

* Topics that already have a non-empty summary_th.md are skipped, so this is
  restartable by just running it again -- no --start-id bookkeeping, which
  does not survive out-of-order completion anyway.
* notes.create is off by default. Nothing in this repo reads those notes back
  and each one is an extra round-trip per topic; pass --notes to keep them.

Usage:
  python summary_parallel.py                  # 4 workers
  python summary_parallel.py --workers 6
  python summary_parallel.py --notes           # also create NotebookLM notes
  python summary_parallel.py --only 01_06,02_03
"""
import asyncio
import os
import sys

from notebooklm import NotebookLMClient

# TOPICS comes via run.py (cert_config), not straight from topics.py, so
# CERT=ccna actually switches the list instead of silently reusing CCNP's.
from run import NOTEBOOK_ID, OUTPUT_DIR, TOPICS, topic_to_slug
from nlm_common import AuthExpiredError, is_auth_error
from summary_only import CITATION_RE, build_focus_prompt, strip_citations

DEFAULT_WORKERS = 4
RETRY_LIMIT = 2
SLEEP_BETWEEN_TOPICS = 3


def arg_value(flag: str, default=None):
    if flag in sys.argv:
        return sys.argv[sys.argv.index(flag) + 1]
    return default


async def ask_with_retry(client, topic: str):
    """chat.ask with retry. Auth failures abort the whole run immediately."""
    rate_limit_retries = 2
    attempt = 0
    while True:
        try:
            return await client.chat.ask(NOTEBOOK_ID, build_focus_prompt(topic))
        except Exception as e:
            if is_auth_error(e):
                raise AuthExpiredError(f"chat.ask ({topic}): session expired") from e
            if "RateLimit" in type(e).__name__ or "RateLimitError" in str(e):
                if rate_limit_retries > 0:
                    rate_limit_retries -= 1
                    print(f"  [{topic}] rate limited, backing off 60s...", flush=True)
                    await asyncio.sleep(60)
                    continue
                print(f"  [{topic}] SKIPPED (rate limit exhausted)", flush=True)
                return None
            if attempt < RETRY_LIMIT:
                attempt += 1
                print(f"  [{topic}] failed ({str(e)[:70]}), retry {attempt}...", flush=True)
                await asyncio.sleep(5)
                continue
            print(f"  [{topic}] SKIPPED: {str(e)[:90]}", flush=True)
            return None


async def process_topic(client, t: dict, sem: asyncio.Semaphore, want_notes: bool,
                        counter: dict):
    tid, topic = t["id"], t["topic"]
    folder = os.path.join(OUTPUT_DIR, f"{tid}_{topic_to_slug(topic)}")

    async with sem:
        print(f"-> [{tid}] {topic}", flush=True)
        result = await ask_with_retry(client, topic)
        if result is None:
            counter["failed"] += 1
            return

        os.makedirs(folder, exist_ok=True)
        answer = strip_citations(result.answer)
        stripped = len(CITATION_RE.findall(result.answer)) - len(CITATION_RE.findall(answer))
        with open(os.path.join(folder, "summary_th.md"), "w", encoding="utf-8") as f:
            f.write(f"# {topic}\n\n{answer}")

        if want_notes:
            try:
                await client.notes.create(NOTEBOOK_ID, title=f"[Focus] {topic}",
                                          content=answer)
            except Exception as e:
                print(f"  [{tid}] note failed (summary kept): {str(e)[:60]}", flush=True)

        counter["done"] += 1
        print(f"OK [{tid}] {len(answer):,} chars, {stripped} citations stripped "
              f"({counter['done']}/{counter['total']} done)", flush=True)
        await asyncio.sleep(SLEEP_BETWEEN_TOPICS)


def pending_topics(only: str | None):
    wanted = set(only.split(",")) if only else None
    out = []
    for t in TOPICS:
        if wanted and t["id"] not in wanted:
            continue
        path = os.path.join(OUTPUT_DIR, f"{t['id']}_{topic_to_slug(t['topic'])}",
                            "summary_th.md")
        if os.path.exists(path) and os.path.getsize(path) > 0:
            continue
        out.append(t)
    return out


async def main():
    workers = int(arg_value("--workers", DEFAULT_WORKERS))
    profile = arg_value("--profile")
    want_notes = "--notes" in sys.argv
    todo = pending_topics(arg_value("--only"))

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not todo:
        print("Nothing to do -- every requested topic already has a summary.")
        return

    print(f"{len(todo)} topic(s) pending, {workers} in parallel, "
          f"notes {'on' if want_notes else 'off'}"
          f"{f', profile {profile}' if profile else ''}\n")

    sem = asyncio.Semaphore(workers)
    counter = {"done": 0, "failed": 0, "total": len(todo)}

    async with NotebookLMClient.from_storage(profile=profile) as client:
        tasks = [
            asyncio.create_task(process_topic(client, t, sem, want_notes, counter))
            for t in todo
        ]
        try:
            await asyncio.gather(*tasks)
        except AuthExpiredError as e:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            print(f"\nSTOPPED: {e}")
            print(f"  {counter['done']} finished this pass.")
            print("  Refresh auth and run again -- finished topics are skipped:")
            print("      ./ccnp summary-fast")
            sys.exit(2)

    print(f"\nDone: {counter['done']} written, {counter['failed']} failed, "
          f"{len(pending_topics(None))} still pending overall.")


if __name__ == "__main__":
    asyncio.run(main())
