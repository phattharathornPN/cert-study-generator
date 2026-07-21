import re

with open("run.py", encoding="utf-8") as f:
    content = f.read()

m = re.search(r"TOPICS = \[(.*?)\n\]", content, re.S)
topics_block = m.group(1)
pattern = re.compile(r'\{"id":\s*"([^"]+)",\s*"topic":\s*"([^"]+)"\}')
topics = pattern.findall(topics_block)

SLIDE_TEMPLATE = (
    'สร้างสไลด์เฉพาะหัวข้อ "{topic}" จากเนื้อหา CCNP ENCOR 350-401 เท่านั้น '
    "ไม่ต้องพูดถึงหัวข้ออื่น โดยครอบคลุม: "
    "1) แนวคิดหลักและความสำคัญ 2) การทำงาน (How it works) "
    "3) ตัวอย่าง config จริง (Cisco IOS / IOS-XE) ถ้ามี "
    "4) Key points ที่ต้องจำสำหรับสอบ"
)

AUDIO_TEMPLATE = (
    'อธิบายเฉพาะหัวข้อ "{topic}" จากเนื้อหา CCNP ENCOR 350-401 เป็นภาษาไทย '
    "แบบเข้าใจง่าย ไม่ต้องพูดถึงหัวข้ออื่น โดยครอบคลุม: "
    "1) แนวคิดหลักและความสำคัญ 2) การทำงาน (How it works) "
    "3) ตัวอย่าง config จริง (Cisco IOS / IOS-XE) ถ้ามี "
    "4) Key points ที่ต้องจำสำหรับสอบ"
)

FLASHCARD_TEMPLATE = "สร้างแฟลชการ์ดเป็นภาษาไทยสำหรับหัวข้อ {topic}"

with open("PROMPTS_FOR_NOTEBOOKLM.md", "w", encoding="utf-8") as out:
    out.write("# Prompts สำหรับ Generate ผ่านเว็บ NotebookLM (copy-paste ทีละ topic)\n\n")
    out.write(f"รวม {len(topics)} topics — เปิด notebook แล้ววางใน custom instructions ตอนกด Generate\n\n")
    for tid, topic in topics:
        out.write(f"---\n\n")
        out.write(f"## [{tid}] {topic}\n\n")
        out.write(f"**Slide deck instructions:**\n```\n{SLIDE_TEMPLATE.format(topic=topic)}\n```\n\n")
        out.write(f"**Audio overview instructions:**\n```\n{AUDIO_TEMPLATE.format(topic=topic)}\n```\n\n")
        out.write(f"**Flashcards instructions:**\n```\n{FLASHCARD_TEMPLATE.format(topic=topic)}\n```\n\n")

print(f"Wrote {len(topics)} topics to PROMPTS_FOR_NOTEBOOKLM.md")
