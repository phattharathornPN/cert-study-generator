import asyncio
import os
import re
import sys
from notebooklm import NotebookLMClient

NOTEBOOK_ID = os.environ.get("NOTEBOOK_ID")
if not NOTEBOOK_ID:
    print("ERROR: NOTEBOOK_ID environment variable not set (see .env.example).")
    sys.exit(1)
OUTPUT_DIR = "output"
SLEEP_BETWEEN_TOPICS = 10
RETRY_LIMIT = 2

from run import TOPICS  # noqa: E402  (reuse the same 68-topic list)

# Reuse the hardened auth handling from slides_only.py rather than keeping a
# second, weaker copy here: is_auth_error walks the exception chain (library
# errors bury the real "Unauthenticated" RPCError in .cause), and the
# keepalive refreshes the token immediately then every ~13 min, which a
# multi-hour summary run needs just as much as a slide run does.
from slides_only import (  # noqa: E402
    AuthExpiredError,
    auth_keepalive_loop,
    is_auth_error,
)


def topic_to_slug(topic: str) -> str:
    slug = topic.lower()
    slug = re.sub(r"[^a-z0-9\s]", "", slug)
    slug = re.sub(r"\s+", "_", slug.strip())
    return slug[:40]


def build_focus_prompt(topic: str) -> str:
    return f"""ฉันต้องการเรียนเฉพาะหัวข้อนี้จากเนื้อหา CCNP ENCOR 350-401 แบบละเอียดที่สุด:

หัวข้อ: {topic}

กรุณาสรุปเฉพาะหัวข้อนี้เป็นภาษาไทยแบบละเอียด (เขียนยาวได้เต็มที่ ไม่ต้องสั้น) โดยเรียงตามนี้:

0. **TL;DR — สรุป 30 วินาที** (ขึ้นก่อนเพื่อนสุด) เขียน 3-5 bullet ที่ถ้าอ่านแค่นี้ก่อนเข้าห้องสอบก็ยังได้ประเด็นหลักครบ
1. แนวคิดหลักและความสำคัญ — อธิบายว่ามันคืออะไร ใช้แก้ปัญหาอะไร และสำคัญต่อ enterprise network อย่างไร
2. การทำงานโดยละเอียด (How it works) — อธิบายทุกขั้นตอน/state/process ที่เกี่ยวข้อง พร้อมยกตัวอย่างสถานการณ์จริงประกอบ ถ้าเป็นกระบวนการหลายขั้นให้เขียนเป็นลำดับเลข 1-2-3 พร้อมค่าจำลองจริง (IP/MAC/เลข port) ไม่ใช่พูดลอย ๆ
3. ตัวอย่าง config จริงบน Cisco IOS / IOS-XE (ถ้ามี) — ใส่คำสั่งจริงพร้อมอธิบายแต่ละบรรทัดว่าทำอะไร และคำสั่ง verify/troubleshoot ที่เกี่ยวข้อง (show command, debug command)
4. ข้อแตกต่าง/เปรียบเทียบกับเทคโนโลยีใกล้เคียง (ถ้ามี) — เช่นถ้าเป็น protocol ให้เทียบกับ protocol อื่นในกลุ่มเดียวกัน
5. ข้อผิดพลาดที่พบบ่อย (Common pitfalls) ที่มักทำให้ติดตอนสอบหรือตอนทำงานจริง
6. Key points ที่ต้องจำสำหรับสอบ CCNP ENCOR 350-401 — สรุปเป็น bullet สั้นกระชับท้ายสุด

รูปแบบการเขียน (สำคัญมาก ทำตามให้ครบ):
- **ห้ามใส่เลขอ้างอิงท้ายประโยคเด็ดขาด** เช่น [1], [2, 3], [6-13] — เขียนเป็นเนื้อความล้วน ๆ ให้อ่านลื่น
- **ข้อ 4 (เปรียบเทียบ) ต้องทำเป็นตาราง Markdown เสมอ** คอลัมน์แรกคือหัวข้อที่เทียบ แล้วแยกคอลัมน์ตามเทคโนโลยี ห้ามเขียนเป็น bullet ยาว ๆ
- ที่ไหนมีค่าตัวเลข/ตัวเปรียบเทียบหลายตัว (timer, port, metric, AD, LSA type, state) ให้ใช้ตาราง Markdown แทนการร่ายเป็นย่อหน้า
- config ทุกชุดใส่ใน fenced code block ```cisco เสมอ พร้อม comment `!` อธิบายบรรทัดสำคัญ
- ศัพท์เทคนิคคงภาษาอังกฤษไว้ วงเล็บไทยกำกับครั้งแรกที่เจอ แล้วครั้งต่อไปใช้อังกฤษล้วน ไม่ต้องวงเล็บซ้ำทุกครั้ง

ตอบเฉพาะหัวข้อ "{topic}" เท่านั้น ไม่ต้องพูดถึงหัวข้ออื่น ไม่ต้องสรุปย่อเกินไป เขียนแบบเข้าใจง่ายสำหรับคนไทยที่เรียน CCNP"""


CITATION_RE = re.compile(r"[ \t]*\[\d+(?:\s*[,–-]\s*\d+)*\]")


def strip_citations(text: str) -> str:
    """Remove NotebookLM's inline [1] / [2, 3] / [6-13] citation markers.

    The prompt asks for them to be left out, but grounded generation still
    emits them most of the time -- roughly 66 per topic in the previous run,
    which is what made the Thai prose hard to read. Fenced code blocks are
    left untouched so bracket syntax inside configs survives.
    """
    out = []
    in_fence = False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            # Strip the fence line too -- a trailing "``` [16, 19, 20]" both
            # leaves visible noise and corrupts the fence's info string.
            in_fence = not in_fence
            out.append(CITATION_RE.sub("", line))
            continue
        out.append(line if in_fence else CITATION_RE.sub("", line))
    return "\n".join(out)


async def run_with_retry(coro_fn, label: str):
    for attempt in range(RETRY_LIMIT + 1):
        try:
            return await coro_fn()
        except Exception as e:
            if is_auth_error(e):
                raise AuthExpiredError(
                    f"{label}: session expired. Run 'notebooklm auth refresh' or "
                    f"'notebooklm login', then resume with --start-id."
                ) from e
            if attempt < RETRY_LIMIT:
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

    print("  Prompting detailed summary...")
    result = await run_with_retry(
        lambda: client.chat.ask(NOTEBOOK_ID, build_focus_prompt(topic)),
        "chat.ask"
    )
    if result:
        answer = strip_citations(result.answer)
        removed = len(CITATION_RE.findall(result.answer)) - len(CITATION_RE.findall(answer))
        with open(os.path.join(folder, "summary_th.md"), "w", encoding="utf-8") as f:
            f.write(f"# {topic}\n\n{answer}")
        await run_with_retry(
            lambda: client.notes.create(
                NOTEBOOK_ID,
                title=f"[Focus] {topic}",
                content=answer
            ),
            "notes.create"
        )
        print(f"  OK: summary_th.md saved + note created ({removed} citation markers stripped)")
    else:
        print("  ERROR: summary generation failed entirely for this topic")


async def main():
    start_id = None
    if "--start-id" in sys.argv:
        start_id = sys.argv[sys.argv.index("--start-id") + 1]

    profile = None
    if "--profile" in sys.argv:
        profile = sys.argv[sys.argv.index("--profile") + 1]

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    keepalive_task = asyncio.create_task(auth_keepalive_loop(profile))

    try:
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
                    await process_topic(client, t)
                except AuthExpiredError as e:
                    profile_flag = f" --profile {profile}" if profile else ""
                    print(f"\n  STOPPED: {e}")
                    print(f"  Run: python -m notebooklm{profile_flag} auth refresh   (or 'login' if that fails)")
                    print(f"  Then resume with: python summary_only.py{profile_flag} --start-id {t['id']}")
                    return

                remaining = total - i - 1
                print(f"\n  {remaining} topics remaining. Sleeping {SLEEP_BETWEEN_TOPICS}s...")
                if remaining > 0:
                    await asyncio.sleep(SLEEP_BETWEEN_TOPICS)

        print("\nAll topic summaries complete!")
    finally:
        keepalive_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
