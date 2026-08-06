# -*- coding: utf-8 -*-
"""Re-run ONE topic end-to-end: summary -> pinned source -> slide.

Use this after adding new sources to the notebook, when you want a single
topic regenerated against the richer source pool rather than re-running the
whole list (summary_only.py has no --end-id, so it would run to the end).

The old summary/slides are moved to <folder>/_prev/ instead of being
overwritten, so you can compare the before/after.

Usage:
  python rerun_topic.py 01_23
  python rerun_topic.py 01_23 --summary-only    # skip slide generation
"""
import asyncio
import os
import shutil
import sys
from datetime import datetime

from notebooklm import NotebookLMClient
from notebooklm.rpc.types import SlideDeckFormat, SlideDeckLength

from run import NOTEBOOK_ID, OUTPUT_DIR, topic_to_slug
from nlm_common import AuthExpiredError, run_with_retry
from summary_only import build_focus_prompt
from topics import TOPICS

ARTIFACTS = ("summary_th.md", "slide.pdf", "slide.pptx")


def archive_previous(folder: str) -> str | None:
    """Move existing artifacts into _prev/<timestamp>/ so nothing is lost."""
    present = [f for f in ARTIFACTS if os.path.exists(os.path.join(folder, f))]
    if not present:
        return None
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(folder, "_prev", stamp)
    os.makedirs(dest, exist_ok=True)
    for f in present:
        shutil.move(os.path.join(folder, f), os.path.join(dest, f))
    print(f"  Archived previous {', '.join(present)} -> {dest}")
    return dest


async def regenerate_summary(client, tid: str, topic: str, folder: str):
    print("  Prompting detailed summary (uses ALL notebook sources)...")
    result = await run_with_retry(
        lambda: client.chat.ask(NOTEBOOK_ID, build_focus_prompt(topic)),
        "chat.ask",
    )
    if not result:
        print("  ERROR: summary generation failed")
        return False

    path = os.path.join(folder, "summary_th.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {topic}\n\n{result.answer}")
    print(f"  OK: summary_th.md ({os.path.getsize(path)} bytes)")

    await run_with_retry(
        lambda: client.notes.create(
            NOTEBOOK_ID, title=f"[Focus] {topic}", content=result.answer
        ),
        "notes.create",
    )
    return True


async def refresh_pinned_source(client, tid: str, topic: str, folder: str):
    """Replace the [SRC <tid>] source so the slide pins to the NEW summary."""
    title = f"[SRC {tid}] {topic}"
    existing = await run_with_retry(
        lambda: client.sources.list(NOTEBOOK_ID), "sources.list"
    ) or []

    for s in existing:
        if s.title == title:
            print(f"  Deleting stale pinned source: {title}")
            await run_with_retry(
                lambda sid=s.id: client.sources.delete(NOTEBOOK_ID, sid),
                "sources.delete",
            )

    with open(os.path.join(folder, "summary_th.md"), encoding="utf-8") as f:
        content = f.read()

    src = await run_with_retry(
        lambda: client.sources.add_text(NOTEBOOK_ID, title, content, wait=True),
        "sources.add_text",
    )
    if src:
        print(f"  Pinned source rebuilt: {title}")
        return src.id
    return None


async def regenerate_slide(client, topic: str, folder: str, source_id: str):
    instructions = (
        f'สร้างสไลด์เฉพาะหัวข้อ "{topic}" จากเนื้อหา {EXAM_NAME} เท่านั้น '
        f"ไม่ต้องพูดถึงหัวข้ออื่น โดยครอบคลุม: "
        f"1) แนวคิดหลักและความสำคัญ 2) การทำงาน (How it works) "
        f"3) ตัวอย่าง config จริง (Cisco IOS / IOS-XE) ถ้ามี "
        f"4) Key points ที่ต้องจำสำหรับสอบ"
    )

    print("  Generating slide...")
    status = await run_with_retry(
        lambda: client.artifacts.generate_slide_deck(
            NOTEBOOK_ID,
            source_ids=[source_id],
            language="th",
            instructions=instructions,
            slide_format=SlideDeckFormat.DETAILED_DECK,
            slide_length=SlideDeckLength.DEFAULT,
        ),
        "generate_slide",
    )
    if not status:
        print("  ERROR: slide generation failed to start")
        return

    done = await run_with_retry(
        lambda: client.artifacts.wait_for_completion(
            NOTEBOOK_ID, status.task_id, timeout=600
        ),
        "wait_for_completion (slide)",
    )
    if not (done and done.is_complete):
        print(f"  ERROR: slide did not complete (status={done.status if done else 'n/a'})")
        return

    for fmt in ("pdf", "pptx"):
        await run_with_retry(
            lambda f=fmt: client.artifacts.download_slide_deck(
                NOTEBOOK_ID,
                os.path.join(folder, f"slide.{f}"),
                artifact_id=status.task_id,
                output_format=f,
            ),
            f"download slide {fmt.upper()}",
        )
    print("  OK: slide.pdf + slide.pptx")


async def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("Usage: python rerun_topic.py <topic-id> [--summary-only]")
        sys.exit(1)

    tid = args[0]
    summary_only = "--summary-only" in sys.argv

    match = next((t for t in TOPICS if t["id"] == tid), None)
    if not match:
        print(f"ERROR: no topic with id {tid} in topics.py")
        sys.exit(1)

    topic = match["topic"]
    folder = os.path.join(OUTPUT_DIR, f"{tid}_{topic_to_slug(topic)}")
    os.makedirs(folder, exist_ok=True)

    print(f"\n{'=' * 60}")
    print(f"[{tid}] {topic}")
    print(f"{'=' * 60}")

    archive_previous(folder)

    async with NotebookLMClient.from_storage() as client:
        try:
            if not await regenerate_summary(client, tid, topic, folder):
                return
            if summary_only:
                print("\n--summary-only given, stopping before slide generation.")
                return
            source_id = await refresh_pinned_source(client, tid, topic, folder)
            if not source_id:
                print("  ERROR: could not rebuild pinned source, skipping slide")
                return
            await regenerate_slide(client, topic, folder, source_id)
        except AuthExpiredError as e:
            print(f"\n  STOPPED: {e}")
            return

    print(f"\nDone. Compare against {os.path.join(folder, '_prev')}/")


if __name__ == "__main__":
    asyncio.run(main())
