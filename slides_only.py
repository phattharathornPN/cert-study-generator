import asyncio
import json
import os
import re
import sys
from notebooklm import NotebookLMClient
from notebooklm.rpc.types import SlideDeckFormat, SlideDeckLength

from run import TOPICS  # noqa: E402  (reuse the same 90-topic list)

AUTH_REFRESH_INTERVAL = 780  # seconds (~13 min), under the 15-20 min recommended cadence

NOTEBOOK_ID = os.environ.get("NOTEBOOK_ID")
if not NOTEBOOK_ID:
    print("ERROR: NOTEBOOK_ID environment variable not set (see .env.example).")
    sys.exit(1)
OUTPUT_DIR = "output"
INSTRUCTIONS_FILE = "slide_instructions.json"
SLEEP_BETWEEN_TOPICS = 20
RETRY_LIMIT = 1


def load_topic_checklists() -> dict:
    """Per-topic bespoke checklists produced by generate_slide_instructions.py."""
    if os.path.exists(INSTRUCTIONS_FILE):
        with open(INSTRUCTIONS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


TOPIC_CHECKLISTS = load_topic_checklists()


def topic_to_slug(topic: str) -> str:
    slug = topic.lower()
    slug = re.sub(r"[^a-z0-9\s]", "", slug)
    slug = re.sub(r"\s+", "_", slug.strip())
    return slug[:40]


class AuthExpiredError(Exception):
    pass


def is_auth_error(exc: Exception) -> bool:
    """True if exc (or anything it wraps) is an expired-session failure.

    Library errors like SourceAddError bury the real RPCError in .cause /
    __cause__ and replace the message, so a plain str(e) check on the outer
    exception misses them and the run silently skips every remaining topic.
    """
    seen: set[int] = set()
    cur: BaseException | None = exc
    while cur is not None and id(cur) not in seen:
        seen.add(id(cur))
        text = str(cur)
        if "Unauthenticated" in text or "Authentication expired" in text:
            return True
        if getattr(cur, "rpc_code", None) in (16, "16"):
            return True
        cur = cur.__cause__ or getattr(cur, "cause", None)
    return False


async def run_with_retry(coro_fn, label: str):
    rate_limit_retries = 5
    attempt = 0
    while True:
        try:
            return await coro_fn()
        except Exception as e:
            if is_auth_error(e):
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


async def get_or_create_topic_source(client, tid: str, topic: str, folder: str,
                                     source_cache: dict):
    """Upload this topic's summary_th.md as its own source (once) and return its id.

    Slide generation is then pinned to this single source so NotebookLM cannot
    pull in content from other topics.
    """
    title = f"[SRC {tid}] {topic}"
    if title in source_cache:
        return source_cache[title]

    md_path = os.path.join(folder, "summary_th.md")
    if not os.path.exists(md_path):
        print(f"  ERROR: {md_path} not found -- cannot scope source")
        return None
    with open(md_path, encoding="utf-8") as f:
        content = f.read()

    src = await run_with_retry(
        lambda: client.sources.add_text(NOTEBOOK_ID, title, content, wait=True),
        "sources.add_text"
    )
    if src is None:
        return None
    source_cache[title] = src.id
    return src.id


def build_slide_instructions(topic: str) -> str:
    """Slide-deck instructions shared with slides_parallel.py."""
    return (
        f'สร้างสไลด์เฉพาะหัวข้อ "{topic}" จากเนื้อหา CCNP ENCOR 350-401 เท่านั้น '
        f"ไม่ต้องพูดถึงหัวข้ออื่น โดยครอบคลุม: "
        f"1) แนวคิดหลักและความสำคัญ 2) การทำงาน (How it works) "
        f"3) ตัวอย่าง config จริง (Cisco IOS / IOS-XE) ถ้ามี "
        f"4) ตัวอย่างเดินข้อมูลแบบ step-by-step ด้วยค่าจำลองจริง (IP/MAC/เลข) "
        f"อย่างน้อย 1 หน้าเต็ม แสดงลำดับขั้นตอนทั้งหมดในสถานการณ์เดียว ไม่ใช่แค่ diagram นามธรรม "
        f"5) Key points ที่ต้องจำสำหรับสอบ "
        f"ข้อควรระวังสำคัญ: ถ้าเนื้อหาอธิบายกลไกที่ทำงานโดยไม่พึ่ง CPU/Control Plane "
        f"(เช่น hardware forwarding, ASIC, wire-speed, fast path) ห้ามวาด diagram ที่มีเส้นทาง "
        f"ข้อมูลผ่าน CPU หรือ Route Processor เด็ดขาด เพราะจะขัดแย้งกับเนื้อหาที่อธิบายไว้เอง "
        f"ตรวจสอบว่าทุก diagram สื่อสารตรงกับข้อความที่อธิบายจริง"
    )


async def process_topic(client, t: dict, source_cache: dict):
    tid = t["id"]
    topic = t["topic"]
    slug = topic_to_slug(topic)
    folder = os.path.join(OUTPUT_DIR, f"{tid}_{slug}")
    os.makedirs(folder, exist_ok=True)

    out_pdf = os.path.join(folder, "slide.pdf")
    if os.path.exists(out_pdf):
        print(f"[{tid}] {topic} -- SKIP (slide.pdf already exists)")
        return False

    print(f"\n{'=' * 60}")
    print(f"[{tid}] {topic}")
    print(f"{'=' * 60}")

    source_id = await get_or_create_topic_source(client, tid, topic, folder, source_cache)
    if not source_id:
        print("  ERROR: could not prepare per-topic source, skipping")
        return True  # attempted -> still worth the inter-topic sleep
    print(f"  Source pinned: [SRC {tid}]")

    base_instructions = build_slide_instructions(topic)

    # Bespoke checklists (slide_instructions.json) disabled by default --
    # user preferred the original output style. Re-enable with --use-checklist.
    entry = TOPIC_CHECKLISTS.get(tid) if "--use-checklist" in sys.argv else None
    if entry and entry.get("checklist"):
        checklist_text = " ".join(
            f"({n}) {item}" for n, item in enumerate(entry["checklist"], 1)
        )
        instructions = (
            f"{base_instructions} "
            f"ข้อบังคับเพิ่มเติมที่ต้องมีในสไลด์ชุดนี้ (ห้ามข้ามข้อใดข้อหนึ่ง): {checklist_text} "
            f"ทุก diagram ต้องสื่อสารตรงกับข้อความที่อธิบายจริง ห้ามขัดแย้งกันเอง"
        )
        print(f"  Using bespoke checklist ({len(entry['checklist'])} items)")
    else:
        instructions = base_instructions

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
                    NOTEBOOK_ID, out_pdf,
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
    return True


async def auth_keepalive_loop(profile: str | None):
    # Invoke via `python -m notebooklm` rather than the notebooklm.exe shim --
    # Windows Smart App Control blocks the unsigned .exe on some machines.
    profile_args = ["-p", profile] if profile else []
    first = True
    while True:
        # Refresh immediately on the first pass: the token may already be
        # stale when the run starts (e.g. the notebook sat idle for a while),
        # and sleeping first would let the whole run fail before we ever fix it.
        if not first:
            await asyncio.sleep(AUTH_REFRESH_INTERVAL)
        first = False
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "notebooklm", *profile_args, "auth", "refresh", "--quiet",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()
            if proc.returncode == 0:
                print("  [auth-keepalive] token refreshed OK")
            else:
                print(f"  [auth-keepalive] refresh failed: {stderr.decode(errors='ignore').strip()}")
        except Exception as e:
            print(f"  [auth-keepalive] error: {e}")


async def main():
    start_id = None
    if "--start-id" in sys.argv:
        start_id = sys.argv[sys.argv.index("--start-id") + 1]

    end_id = None
    if "--end-id" in sys.argv:
        end_id = sys.argv[sys.argv.index("--end-id") + 1]

    profile = None
    if "--profile" in sys.argv:
        profile = sys.argv[sys.argv.index("--profile") + 1]

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    keepalive_task = asyncio.create_task(auth_keepalive_loop(profile))

    try:
        async with NotebookLMClient.from_storage(profile=profile) as client:
            # Pre-load existing "[SRC xx_yy]" sources so resuming never re-uploads
            source_cache = {}
            existing = await run_with_retry(
                lambda: client.sources.list(NOTEBOOK_ID), "sources.list"
            ) or []
            for s in existing:
                if s.title and s.title.startswith("[SRC "):
                    source_cache[s.title] = s.id
            print(f"Found {len(source_cache)} existing per-topic sources")

            started = start_id is None
            total = len(TOPICS)

            for i, t in enumerate(TOPICS):
                if not started:
                    if t["id"] == start_id:
                        started = True
                    else:
                        continue

                if end_id is not None and t["id"] > end_id:
                    print(f"\nReached end-id {end_id}, stopping this worker.")
                    break

                try:
                    did_work = await process_topic(client, t, source_cache)
                except AuthExpiredError as e:
                    profile_flag = f" --profile {profile}" if profile else ""
                    print(f"\n  STOPPED: {e}")
                    print(f"  Run: python -m notebooklm{profile_flag} auth refresh   (or 'login' if that fails)")
                    print(f"  Then resume with: python slides_only.py{profile_flag} --start-id {t['id']}")
                    return

                remaining = total - i - 1
                if did_work and remaining > 0:
                    await asyncio.sleep(SLEEP_BETWEEN_TOPICS)

        print("\nAll slide decks complete!")
    finally:
        keepalive_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
