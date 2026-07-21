# -*- coding: utf-8 -*-
"""Step 1-2 of the bespoke-instruction pipeline.

For each requested topic, reads its summary_th.md, asks Gemini to design a
topic-specific "must include" checklist for slide generation (concrete
tables/diagrams/worked-examples this exact content needs to prove real
understanding -- not a generic template), and saves the result to
slide_instructions.json for review before any NotebookLM quota is spent.

This script does NOT call NotebookLM / generate any slides.

Usage:
  python generate_slide_instructions.py 01_15 02_09 06_10
  python generate_slide_instructions.py --all-missing   # all topics without slide.pdf
"""
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

from google import genai

from run import TOPICS, topic_to_slug

OUTPUT_DIR = "output"
INSTRUCTIONS_FILE = "slide_instructions.json"
MODEL = "gemini-3.1-pro-preview"

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("ERROR: GEMINI_API_KEY environment variable not set.")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)

ANALYSIS_PROMPT_TEMPLATE = """คุณเป็นผู้เชี่ยวชาญออกแบบสื่อการสอน CCNP ENCOR 350-401 กำลังตรวจสอบเนื้อหาสรุปหัวข้อ
"{topic}" ด้านล่าง เพื่อออกแบบ "checklist บังคับ" สำหรับสั่งสร้างสไลด์ในขั้นตอนถัดไป

เนื้อหาสรุป:
---
{summary}
---

หน้าที่ของคุณ: วิเคราะห์ว่าเนื้อหานี้ **ต้องมีหลักฐานแบบไหนในสไลด์ถึงจะพิสูจน์ว่าเข้าใจจริง**
ไม่ใช่แค่ "อธิบายครบ" แบบนามธรรม โดยพิจารณาว่าเนื้อหานี้เข้าข่ายแบบไหน (อาจมากกว่า 1 แบบ):

- ถ้าเป็นกลไก hardware/data-path (เช่น forwarding, negotiation protocol): ต้องมีตัวอย่างเดินข้อมูล
  จริง 1 เคส มีค่า IP/MAC/พอร์ตครบ ทีละขั้นตอน และห้ามมี diagram ที่ขัดแย้งกับกลไกที่อธิบาย
  (เช่น ถ้าบอกว่าไม่พึ่ง CPU ห้ามวาดเส้นทางผ่าน CPU)
- ถ้าเป็น algorithm ภายใน (เช่น metric/cost/AD calculation): ต้องมีตัวอย่างตัวเลขจริงคำนวณให้ดูจบ
  ไม่ใช่แค่สูตร
- ถ้าเป็นหัวข้อเปรียบเทียบ 2 สิ่ง: ต้องบังคับให้เป็นตารางเทียบข้าง ๆ กันแบบ criteria-by-criteria
- ถ้าเป็น config/operational: ต้องมี running-config เต็มบล็อกจริง + output จากคำสั่ง verify จริง
- ถ้าเป็นสถาปัตยกรรม/concept กว้าง: ต้องการ taxonomy/list ชัดเจน + use-case สั้นที่จับต้องได้
- ถ้าเป็น protocol exchange (การแลกเปลี่ยนข้อความระหว่าง entity): ต้องมี sequence diagram ระบุชื่อ
  entity แต่ละฝั่ง เรียงลำดับขั้นตอนมีหมายเลขกำกับ

ตอบเป็น JSON เท่านั้น (ไม่ต้องมีคำอธิบายอื่นนอก JSON) ในรูปแบบ:
{{
  "archetype": "สั้น ๆ ว่าเนื้อหานี้เข้าข่ายแบบไหน (เช่น hardware-mechanism, comparison, algorithm)",
  "checklist": [
    "ข้อบังคับข้อที่ 1 เป็นประโยคสั่งการสั้น ชัดเจน ระบุค่าตัวอย่างที่ควรใช้ถ้าเกี่ยวข้อง",
    "ข้อบังคับข้อที่ 2 ...",
    "..."
  ]
}}

ข้อกำหนด: checklist มี 3-6 ข้อ แต่ละข้อต้องเจาะจงกับเนื้อหานี้จริง ๆ (อ้างอิงชื่อ protocol/ตัวเลข/
คำศัพท์ที่ปรากฏในเนื้อหาสรุปข้างบน) ห้ามเขียนกว้าง ๆ แบบ "อธิบายให้ครบถ้วน\""""


def analyze_topic(topic: str, summary: str) -> dict:
    prompt = ANALYSIS_PROMPT_TEMPLATE.format(topic=topic, summary=summary)
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )
    result = json.loads(response.text)
    if isinstance(result, list):
        # Gemini sometimes wraps the object in a list, or returns the bare
        # checklist as a list of strings -- coerce both shapes.
        if len(result) == 1 and isinstance(result[0], dict):
            result = result[0]
        elif result and all(isinstance(x, str) for x in result):
            result = {"archetype": "unspecified", "checklist": result}
    if not isinstance(result, dict) or "checklist" not in result:
        raise ValueError(f"unexpected response shape: {type(result).__name__}")
    if not isinstance(result.get("checklist"), list):
        raise ValueError("'checklist' field is not a list")
    return result


def load_instructions() -> dict:
    if os.path.exists(INSTRUCTIONS_FILE):
        with open(INSTRUCTIONS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_instructions(data: dict):
    with open(INSTRUCTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(dict(sorted(data.items())), f, ensure_ascii=False, indent=2)


def main():
    args = sys.argv[1:]
    topics_by_id = {t["id"]: t for t in TOPICS}

    if "--all" in args:
        target_ids = [t["id"] for t in TOPICS]
    elif "--all-missing" in args:
        target_ids = []
        for t in TOPICS:
            folder = os.path.join(OUTPUT_DIR, f"{t['id']}_{topic_to_slug(t['topic'])}")
            if not os.path.exists(os.path.join(folder, "slide.pdf")):
                target_ids.append(t["id"])
    else:
        target_ids = [a for a in args if a in topics_by_id]
        unknown = [a for a in args if a not in topics_by_id]
        if unknown:
            print(f"WARNING: unknown topic ids ignored: {unknown}")

    if not target_ids:
        print("No topic ids given. Usage: python generate_slide_instructions.py 01_15 02_09 06_10")
        return

    store = load_instructions()

    for tid in target_ids:
        t = topics_by_id[tid]
        topic = t["topic"]
        folder = os.path.join(OUTPUT_DIR, f"{tid}_{topic_to_slug(topic)}")
        md_path = os.path.join(folder, "summary_th.md")
        if not os.path.exists(md_path):
            print(f"[{tid}] {topic} -- SKIP (no summary_th.md found)")
            continue

        with open(md_path, encoding="utf-8") as f:
            summary = f.read()

        print(f"\n{'=' * 60}")
        print(f"[{tid}] {topic}")
        print(f"{'=' * 60}")
        result = None
        for attempt in range(2):
            try:
                result = analyze_topic(topic, summary)
                break
            except Exception as e:
                print(f"  WARNING: attempt {attempt + 1} failed: {e}")
                time.sleep(3)
        if result is None:
            print(f"  ERROR: giving up on {tid} after retry")
            continue

        store[tid] = result
        print(f"  archetype: {result.get('archetype')}")
        for item in result.get("checklist", []):
            print(f"  - {item}")

        save_instructions(store)  # save after every topic, not just at the end
        time.sleep(3)

    print(f"\nSaved {len(store)} topic instructions -> {INSTRUCTIONS_FILE}")


if __name__ == "__main__":
    main()
