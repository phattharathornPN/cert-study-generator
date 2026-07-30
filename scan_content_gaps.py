# -*- coding: utf-8 -*-
"""Scan every topic's summary_th.md for concepts that are name-dropped but
never actually explained -- the "TCAM problem": a term shows up in a Key
Points bullet with zero explanation of how it actually works.

Two passes:
  1. Per-topic scan (Gemini Flash, cheap/fast): for each of the 116
     existing topics, list terms mentioned but under-explained.
  2. Consolidation (Gemini Pro): merge the ~116 raw lists into a single
     deduplicated, prioritized list of candidate new deep-dive topics
     (the same term often gets flagged by multiple source topics).

Output: content_gaps_report.json (raw findings) and prints a final
prioritized markdown table to stdout / content_gaps_report.md.

This does NOT touch NotebookLM or generate any slides -- pure analysis.
"""
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

from google import genai

from topics import TOPICS

OUTPUT_DIR = "output"
RAW_FILE = "content_gaps_raw.json"
REPORT_JSON = "content_gaps_report.json"
REPORT_MD = "content_gaps_report.md"
SCAN_MODEL = "gemini-3.1-flash-lite"
CONSOLIDATE_MODEL = "gemini-3.1-pro-preview"

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("ERROR: GEMINI_API_KEY environment variable not set.")
    sys.exit(1)

client = genai.Client(
    api_key=API_KEY,
    http_options={"timeout": 180_000},  # 180s in ms -- consolidation sends a much bigger
                                         # prompt (all raw findings at once) than a single-topic scan
)

EXISTING_TOPIC_TITLES = "\n".join(f"- {t['topic']}" for t in TOPICS)

SCAN_PROMPT_TEMPLATE = """คุณเป็นผู้เชี่ยวชาญ CCNP ENCOR 350-401 กำลังตรวจสอบเนื้อหาสรุปหัวข้อ
"{topic}" ด้านล่าง เพื่อหา "จุดโหว่การอธิบาย" (the TCAM problem): คำศัพท์/กลไก/
โปรโตคอลที่ถูก **เอ่ยชื่อผ่านๆ** (เช่น ใน bullet เดียว หรือใน parenthesis) แต่
**ไม่มีการอธิบายว่ามันทำงานยังไงจริงๆ** ทำให้คนอ่านจำชื่อได้แต่ไม่เข้าใจกลไก

เนื้อหาสรุป:
---
{summary}
---

ห้ามเสนอคำที่ตรงหรือใกล้เคียงกับหัวข้อที่มีอยู่แล้วในคอร์สนี้ (เพราะมันถูกอธิบาย
เต็มที่ในหัวข้อของตัวเองอยู่แล้ว) รายการหัวข้อที่มีอยู่แล้วทั้งหมด:
{existing_topics}

ตอบเป็น JSON เท่านั้น ในรูปแบบ:
{{
  "gaps": [
    {{
      "term": "ชื่อคำศัพท์/กลไกที่ถูกเอ่ยผ่านๆ",
      "mentioned_as": "ประโยคหรือ bullet ที่เอ่ยถึงมันแบบผิวเผิน (คัดจากเนื้อหาจริง)",
      "why_it_matters": "ทำไมการไม่เข้าใจกลไกนี้ถึงเป็นปัญหาตอนสอบ",
      "suggested_topic_title": "ชื่อหัวข้อใหม่ที่ควรแยกออกมา (ภาษาอังกฤษ ตรงกับ style หัวข้ออื่นในคอร์ส)"
    }}
  ]
}}

ถ้าเนื้อหานี้อธิบายครบดีอยู่แล้วไม่มีจุดโหว่ ให้ตอบ {{"gaps": []}}
เกณฑ์ให้เข้มงวด: เสนอเฉพาะจุดที่ถ้าออกข้อสอบถามลึกจะตอบไม่ได้จริงๆ ไม่ใช่แค่
"อยากรู้เพิ่ม" ทั่วไป จำกัดไม่เกิน 3 จุดต่อหัวข้อ (เอาที่สำคัญสุด)"""

CONSOLIDATE_PROMPT_TEMPLATE = """ด้านล่างคือรายการ "จุดโหว่การอธิบาย" ที่พบจากการสแกนเนื้อหาสรุป CCNP ENCOR
350-401 ทั้งคอร์ส (116 หัวข้อ) แต่ละจุดมาจากหัวข้อต้นทางที่ต่างกัน และมีจุดซ้ำกัน
เยอะ (คำเดียวกันถูกเอ่ยผ่านๆ ในหลายหัวข้อ)

ข้อมูลดิบ:
---
{raw_findings}
---

หน้าที่ของคุณ:
1. รวมจุดที่เป็นเรื่องเดียวกัน (เช่น "ASIC" ที่ถูกเอ่ยถึงใน 5 หัวข้อ ให้รวมเป็น
   1 รายการ พร้อมระบุว่ามันถูกเอ่ยถึงในหัวข้อไหนบ้าง)
2. จัดลำดับความสำคัญ: high = คำนี้เกี่ยวกับกลไกที่ข้อสอบชอบถามเจาะจริง,
   medium = มีประโยชน์แต่ไม่ critical, low = รู้ไว้ก็ดีแต่ไม่จำเป็น
3. เสนอชื่อหัวข้อใหม่ที่ควรแยกออกมา (ภาษาอังกฤษ)

ตอบเป็น JSON เท่านั้น ในรูปแบบ:
{{
  "consolidated_gaps": [
    {{
      "term": "ชื่อคำศัพท์/กลไก",
      "priority": "high|medium|low",
      "mentioned_in_topics": ["ชื่อหัวข้อที่เอ่ยถึงคำนี้", "..."],
      "why_it_matters": "สรุปทำไมสำคัญ",
      "suggested_topic_title": "ชื่อหัวข้อใหม่ที่ควรแยกออกมา"
    }}
  ]
}}

เรียงจาก high priority ไปหา low priority"""


def topic_to_slug(topic: str) -> str:
    import re
    slug = topic.lower()
    slug = re.sub(r"[^a-z0-9\s]", "", slug)
    slug = re.sub(r"\s+", "_", slug.strip())
    return slug[:40]


def scan_topic(topic: str, summary: str) -> dict:
    prompt = SCAN_PROMPT_TEMPLATE.format(
        topic=topic, summary=summary, existing_topics=EXISTING_TOPIC_TITLES
    )
    response = client.models.generate_content(
        model=SCAN_MODEL,
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )
    result = json.loads(response.text)
    if isinstance(result, list):
        if len(result) == 1 and isinstance(result[0], dict):
            result = result[0]
        else:
            result = {"gaps": []}
    if not isinstance(result, dict) or "gaps" not in result:
        raise ValueError(f"unexpected shape: {type(result).__name__}")
    if not isinstance(result["gaps"], list):
        raise ValueError("'gaps' is not a list")
    return result


def run_scan_pass():
    raw = {}
    if os.path.exists(RAW_FILE):
        with open(RAW_FILE, encoding="utf-8") as f:
            raw = json.load(f)

    for t in TOPICS:
        tid = t["id"]
        topic = t["topic"]
        if tid in raw:
            continue

        folder = os.path.join(OUTPUT_DIR, f"{tid}_{topic_to_slug(topic)}")
        md_path = os.path.join(folder, "summary_th.md")
        if not os.path.exists(md_path):
            print(f"[{tid}] {topic} -- SKIP (no summary_th.md)")
            continue

        with open(md_path, encoding="utf-8") as f:
            summary = f.read()

        result = None
        for attempt in range(2):
            try:
                result = scan_topic(topic, summary)
                break
            except Exception as e:
                print(f"  [{tid}] attempt {attempt + 1} failed: {e}")
                time.sleep(3)

        if result is None:
            print(f"[{tid}] {topic} -- ERROR (giving up)")
            continue

        n_gaps = len(result["gaps"])
        print(f"[{tid}] {topic} -- {n_gaps} gap(s) found")
        for g in result["gaps"]:
            print(f"    - {g.get('term')}: {g.get('suggested_topic_title')}")

        raw[tid] = {"topic": topic, "gaps": result["gaps"]}
        with open(RAW_FILE, "w", encoding="utf-8") as f:
            json.dump(raw, f, ensure_ascii=False, indent=2)
        time.sleep(2)

    return raw


def run_consolidation(raw: dict):
    lines = []
    for tid, entry in sorted(raw.items()):
        for g in entry["gaps"]:
            lines.append(
                f"[from: {entry['topic']}] term={g.get('term')} | "
                f"mentioned_as=\"{g.get('mentioned_as')}\" | "
                f"why={g.get('why_it_matters')} | "
                f"suggested={g.get('suggested_topic_title')}"
            )
    raw_text = "\n".join(lines)
    print(f"\nConsolidating {len(lines)} raw findings across {len(raw)} topics...")

    prompt = CONSOLIDATE_PROMPT_TEMPLATE.format(raw_findings=raw_text)

    result = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=CONSOLIDATE_MODEL,
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            result = json.loads(response.text)
            break
        except Exception as e:
            print(f"  consolidation attempt {attempt + 1} failed: {e}")
            time.sleep(5)

    if result is None:
        raise RuntimeError("consolidation failed after 3 attempts")

    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


def write_markdown_report(consolidated: dict):
    gaps = consolidated.get("consolidated_gaps", [])
    lines = ["# Content Gap Scan Report", ""]
    lines.append(f"พบทั้งหมด {len(gaps)} จุดที่ควรพิจารณาแยกเป็น topic ใหม่\n")

    for priority in ["high", "medium", "low"]:
        group = [g for g in gaps if g.get("priority") == priority]
        if not group:
            continue
        label = {"high": "🔴 High Priority", "medium": "🟡 Medium Priority", "low": "🟢 Low Priority"}[priority]
        lines.append(f"## {label} ({len(group)})\n")
        lines.append("| คำศัพท์ | หัวข้อที่แนะนำ | เอ่ยถึงในหัวข้อไหนบ้าง | ทำไมสำคัญ |")
        lines.append("|---|---|---|---|")
        for g in group:
            mentioned = ", ".join(g.get("mentioned_in_topics", []))
            lines.append(
                f"| {g.get('term')} | {g.get('suggested_topic_title')} | {mentioned} | {g.get('why_it_matters')} |"
            )
        lines.append("")

    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nWrote {REPORT_MD}")


def main():
    print("=== Pass 1: scanning all topics for content gaps ===")
    raw = run_scan_pass()

    total_gaps = sum(len(e["gaps"]) for e in raw.values())
    print(f"\n=== Pass 1 done: {total_gaps} raw findings across {len(raw)} topics ===")

    if total_gaps == 0:
        print("No gaps found -- nothing to consolidate.")
        return

    print("\n=== Pass 2: consolidating into a deduplicated, prioritized list ===")
    consolidated = run_consolidation(raw)
    write_markdown_report(consolidated)

    print(f"\nDone. See {REPORT_MD} for the final report.")


if __name__ == "__main__":
    main()
