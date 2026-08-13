import asyncio
import os
import re
import sys
from notebooklm import NotebookLMClient
from notebooklm.rpc.types import (
    AudioFormat,
    AudioLength,
    QuizQuantity,
    SlideDeckFormat,
    SlideDeckLength,
)

# Which exam this run belongs to comes from cert_config (CERT env var,
# default "ccnp"). Downstream scripts import NOTEBOOK_ID / OUTPUT_DIR /
# TOPICS from here, so wiring it up once at this level makes the whole
# pipeline cert-aware without every script growing its own lookup.
from cert_config import (  # noqa: F401  (re-exported for downstream scripts)
    EXAM_NAME,
    OUTPUT_DIR,
    SLIDE_FORMATS,
    SLIDE_INSTRUCTIONS,
    SUMMARY_PROMPT,
    TOPICS,
    notebook_id,
)

NOTEBOOK_ID = notebook_id()
SLEEP_BETWEEN_ARTIFACTS = 15
SLEEP_AFTER_AUDIO = 30
SLEEP_BETWEEN_TOPICS = 20
RETRY_LIMIT = 1


def topic_to_slug(topic: str) -> str:
    slug = topic.lower()
    slug = re.sub(r"[^a-z0-9\s]", "", slug)
    slug = re.sub(r"\s+", "_", slug.strip())
    return slug[:40]


# Delegates to the active cert -- see cert_config.SUMMARY_PROMPT for why
# this file no longer carries its own (shorter, also Cisco-hardcoded) copy.
def build_focus_prompt(topic: str) -> str:
    return SUMMARY_PROMPT(topic)


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
                    f"{label}: session expired. Run 'notebooklm auth refresh' or "
                    f"'notebooklm login', then resume with --start-id."
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
    os.makedirs(folder, exist_ok=True)

    print(f"\n{'=' * 60}")
    print(f"[{tid}] {topic}")
    print(f"{'=' * 60}")

    # Step 1: Focused prompt -> summary_th.md + save note
    print("  Prompting focused summary...")
    result = await run_with_retry(
        lambda: client.chat.ask(NOTEBOOK_ID, build_focus_prompt(topic)),
        "chat.ask"
    )
    if result:
        with open(os.path.join(folder, "summary_th.md"), "w", encoding="utf-8") as f:
            f.write(f"# {topic}\n\n{result.answer}")
        await run_with_retry(
            lambda: client.notes.create(
                NOTEBOOK_ID,
                title=f"[Focus] {topic}",
                content=result.answer
            ),
            "notes.create"
        )
        print("  OK: summary_th.md saved + note created")
    await asyncio.sleep(SLEEP_BETWEEN_ARTIFACTS)

    # Step 2: Slide
    print("  Generating slide...")
    status = await run_with_retry(
        lambda: client.artifacts.generate_slide_deck(
            NOTEBOOK_ID,
            language="th",
            instructions=SLIDE_INSTRUCTIONS(topic),
            slide_format=SlideDeckFormat.DETAILED_DECK,
            slide_length=SlideDeckLength.DEFAULT,
        ),
        "generate_slide"
    )
    if status:
        done = await run_with_retry(
            lambda: client.artifacts.wait_for_completion(NOTEBOOK_ID, status.task_id, timeout=600),
            "wait_for_completion (slide)"
        )
        if done and done.is_complete:
            await run_with_retry(
                lambda: client.artifacts.download_slide_deck(
                    NOTEBOOK_ID, os.path.join(folder, "slide.pdf"),
                    artifact_id=status.task_id, output_format="pdf"
                ), "download slide PDF"
            )
            await run_with_retry(
                lambda: client.artifacts.download_slide_deck(
                    NOTEBOOK_ID, os.path.join(folder, "slide.pptx"),
                    artifact_id=status.task_id, output_format="pptx"
                ), "download slide PPTX"
            )
            print("  OK: slide.pdf + slide.pptx")
        elif done:
            print(f"  ERROR: slide generation did not complete (status={done.status})")
    else:
        print("  ERROR: slide generation failed to start (see warnings above)")
    await asyncio.sleep(SLEEP_BETWEEN_ARTIFACTS)

    # Step 3: Audio
    print("  Generating audio...")
    status = await run_with_retry(
        lambda: client.artifacts.generate_audio(
            NOTEBOOK_ID,
            language="th",
            # No per-cert AUDIO_INSTRUCTIONS hook exists (audio isn't part of
            # any cert's active workflow) -- reusing SLIDE_INSTRUCTIONS keeps
            # this cert-correct without inventing unused infrastructure.
            instructions=SLIDE_INSTRUCTIONS(topic),
            audio_format=AudioFormat.DEEP_DIVE,
            audio_length=AudioLength.DEFAULT,
        ),
        "generate_audio"
    )
    if status:
        done = await run_with_retry(
            lambda: client.artifacts.wait_for_completion(NOTEBOOK_ID, status.task_id, timeout=600),
            "wait_for_completion (audio)"
        )
        if done and done.is_complete:
            await run_with_retry(
                lambda: client.artifacts.download_audio(
                    NOTEBOOK_ID, os.path.join(folder, "audio.mp3"),
                    artifact_id=status.task_id
                ), "download audio"
            )
            print("  OK: audio.mp3")
        elif done:
            print(f"  ERROR: audio generation did not complete (status={done.status})")
    else:
        print("  ERROR: audio generation failed to start (see warnings above)")
    await asyncio.sleep(SLEEP_AFTER_AUDIO)

    # Step 4: Flashcard
    print("  Generating flashcards...")
    status = await run_with_retry(
        lambda: client.artifacts.generate_flashcards(
            NOTEBOOK_ID,
            instructions=f"สร้างแฟลชการ์ดเป็นภาษาไทยสำหรับหัวข้อ {topic}",
            quantity=QuizQuantity.MORE,
        ),
        "generate_flashcards"
    )
    if status:
        done = await run_with_retry(
            lambda: client.artifacts.wait_for_completion(NOTEBOOK_ID, status.task_id, timeout=600),
            "wait_for_completion (flashcards)"
        )
        if done and done.is_complete:
            await run_with_retry(
                lambda: client.artifacts.download_flashcards(
                    NOTEBOOK_ID,
                    os.path.join(folder, "flashcards.json"),
                    artifact_id=status.task_id,
                    output_format="json"
                ), "download flashcards"
            )
            print("  OK: flashcards.json")
        elif done:
            print(f"  ERROR: flashcards generation did not complete (status={done.status})")
    else:
        print("  ERROR: flashcards generation failed to start (see warnings above)")
    await asyncio.sleep(SLEEP_BETWEEN_ARTIFACTS)


async def main():
    # Resume support: python run.py --start-id 03_05
    start_id = None
    if "--start-id" in sys.argv:
        start_id = sys.argv[sys.argv.index("--start-id") + 1]

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    async with NotebookLMClient.from_storage() as client:
        started = start_id is None
        total = len(TOPICS)

        for i, t in enumerate(TOPICS):
            if not started:
                if t["id"] == start_id:
                    started = True
                else:
                    continue

            try:
                await process_topic(client, t)
            except AuthExpiredError as e:
                print(f"\n  STOPPED: {e}")
                print(f"  Run: notebooklm auth refresh   (or 'notebooklm login' if that fails)")
                print(f"  Then resume with: python run.py --start-id {t['id']}")
                return
            except Exception as e:
                print(f"  ERROR: topic {t['id']} failed entirely: {e}")

            remaining = total - i - 1
            print(f"\n  {remaining} topics remaining. Sleeping {SLEEP_BETWEEN_TOPICS}s...")
            if remaining > 0:
                await asyncio.sleep(SLEEP_BETWEEN_TOPICS)

    print("\nAll topics complete!")


if __name__ == "__main__":
    asyncio.run(main())
