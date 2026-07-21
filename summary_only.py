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


def topic_to_slug(topic: str) -> str:
    slug = topic.lower()
    slug = re.sub(r"[^a-z0-9\s]", "", slug)
    slug = re.sub(r"\s+", "_", slug.strip())
    return slug[:40]


def build_focus_prompt(topic: str) -> str:
    return f"""ฉันต้องการเรียนเฉพาะหัวข้อนี้จากเนื้อหา CCNP ENCOR 350-401 แบบละเอียดที่สุด:

หัวข้อ: {topic}

กรุณาสรุปเฉพาะหัวข้อนี้เป็นภาษาไทยแบบละเอียด (เขียนยาวได้เต็มที่ ไม่ต้องสั้น) โดยครอบคลุม:

1. แนวคิดหลักและความสำคัญ — อธิบายว่ามันคืออะไร ใช้แก้ปัญหาอะไร และสำคัญต่อ enterprise network อย่างไร
2. การทำงานโดยละเอียด (How it works) — อธิบายทุกขั้นตอน/state/process ที่เกี่ยวข้อง พร้อมยกตัวอย่างสถานการณ์จริงประกอบ
3. ตัวอย่าง config จริงบน Cisco IOS / IOS-XE (ถ้ามี) — ใส่คำสั่งจริงพร้อมอธิบายแต่ละบรรทัดว่าทำอะไร และคำสั่ง verify/troubleshoot ที่เกี่ยวข้อง (show command, debug command)
4. ข้อแตกต่าง/เปรียบเทียบกับเทคโนโลยีใกล้เคียง (ถ้ามี) — เช่นถ้าเป็น protocol ให้เทียบกับ protocol อื่นในกลุ่มเดียวกัน
5. ข้อผิดพลาดที่พบบ่อย (Common pitfalls) ที่มักทำให้ติดตอนสอบหรือตอนทำงานจริง
6. Key points ที่ต้องจำสำหรับสอบ CCNP ENCOR 350-401 — สรุปเป็น bullet สั้นกระชับท้ายสุด

ตอบเฉพาะหัวข้อ "{topic}" เท่านั้น ไม่ต้องพูดถึงหัวข้ออื่น ไม่ต้องสรุปย่อเกินไป เขียนแบบเข้าใจง่ายสำหรับคนไทยที่เรียน CCNP"""


class AuthExpiredError(Exception):
    pass


async def run_with_retry(coro_fn, label: str):
    for attempt in range(RETRY_LIMIT + 1):
        try:
            return await coro_fn()
        except Exception as e:
            if "Unauthenticated" in str(e) or "Authentication expired" in str(e):
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
    else:
        print("  ERROR: summary generation failed entirely for this topic")


async def main():
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
                print(f"  Then resume with: python summary_only.py --start-id {t['id']}")
                return

            remaining = total - i - 1
            print(f"\n  {remaining} topics remaining. Sleeping {SLEEP_BETWEEN_TOPICS}s...")
            if remaining > 0:
                await asyncio.sleep(SLEEP_BETWEEN_TOPICS)

    print("\nAll topic summaries complete!")


if __name__ == "__main__":
    asyncio.run(main())
