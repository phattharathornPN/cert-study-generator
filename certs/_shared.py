# -*- coding: utf-8 -*-
"""Prompt templates shared by the networking certs (CCNP, CCNP v2, CCNA).

Extracted 2026-08-10 after the same "ask for Cisco IOS / IOS-XE config"
wording -- appropriate for every networking cert -- had been copy-pasted into
security.py's slide instructions and was already the single hardcoded prompt
every cert's *summaries* went through. When Security ran on it, 354 of 357
generated summaries came back with a fabricated Cisco-config section on
topics like "Confidentiality" that have nothing to do with routers.

The fix for the immediate bug was giving Security its own prompts. This
module is the fix for the bug *class*: one copy of the networking template,
so the next networking cert reuses it instead of copy-pasting a fourth time,
and a security-flavored cert never inherits it by accident again.
"""


def networking_slide_instructions(exam_name: str, topic: str) -> str:
    return (
        f'สร้างสไลด์เฉพาะหัวข้อ "{topic}" จากเนื้อหา {exam_name} เท่านั้น '
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


def networking_summary_prompt(exam_name: str, topic: str) -> str:
    return f"""ฉันต้องการเรียนเฉพาะหัวข้อนี้จากเนื้อหา {exam_name} แบบละเอียดที่สุด:

หัวข้อ: {topic}

กรุณาสรุปเฉพาะหัวข้อนี้เป็นภาษาไทยแบบละเอียด (เขียนยาวได้เต็มที่ ไม่ต้องสั้น) โดยเรียงตามนี้:

0. **TL;DR — สรุป 30 วินาที** (ขึ้นก่อนเพื่อนสุด) เขียน 3-5 bullet ที่ถ้าอ่านแค่นี้ก่อนเข้าห้องสอบก็ยังได้ประเด็นหลักครบ
1. แนวคิดหลักและความสำคัญ — อธิบายว่ามันคืออะไร ใช้แก้ปัญหาอะไร และสำคัญต่อ enterprise network อย่างไร
2. การทำงานโดยละเอียด (How it works) — อธิบายทุกขั้นตอน/state/process ที่เกี่ยวข้อง พร้อมยกตัวอย่างสถานการณ์จริงประกอบ ถ้าเป็นกระบวนการหลายขั้นให้เขียนเป็นลำดับเลข 1-2-3 พร้อมค่าจำลองจริง (IP/MAC/เลข port) ไม่ใช่พูดลอย ๆ
3. ตัวอย่าง config จริงบน Cisco IOS / IOS-XE (ถ้ามี) — ใส่คำสั่งจริงพร้อมอธิบายแต่ละบรรทัดว่าทำอะไร และคำสั่ง verify/troubleshoot ที่เกี่ยวข้อง (show command, debug command)
4. ข้อแตกต่าง/เปรียบเทียบกับเทคโนโลยีใกล้เคียง (ถ้ามี) — เช่นถ้าเป็น protocol ให้เทียบกับ protocol อื่นในกลุ่มเดียวกัน
5. ข้อผิดพลาดที่พบบ่อย (Common pitfalls) ที่มักทำให้ติดตอนสอบหรือตอนทำงานจริง
6. Key points ที่ต้องจำสำหรับสอบ {exam_name} — สรุปเป็น bullet สั้นกระชับท้ายสุด

รูปแบบการเขียน (สำคัญมาก ทำตามให้ครบ):
- **ห้ามใส่เลขอ้างอิงท้ายประโยคเด็ดขาด** เช่น [1], [2, 3], [6-13] — เขียนเป็นเนื้อความล้วน ๆ ให้อ่านลื่น
- **ข้อ 4 (เปรียบเทียบ) ต้องทำเป็นตาราง Markdown เสมอ** คอลัมน์แรกคือหัวข้อที่เทียบ แล้วแยกคอลัมน์ตามเทคโนโลยี ห้ามเขียนเป็น bullet ยาว ๆ
- ที่ไหนมีค่าตัวเลข/ตัวเปรียบเทียบหลายตัว (timer, port, metric, AD, LSA type, state) ให้ใช้ตาราง Markdown แทนการร่ายเป็นย่อหน้า
- config ทุกชุดใส่ใน fenced code block ```cisco เสมอ พร้อม comment `!` อธิบายบรรทัดสำคัญ
- ศัพท์เทคนิคคงภาษาอังกฤษไว้ วงเล็บไทยกำกับครั้งแรกที่เจอ แล้วครั้งต่อไปใช้อังกฤษล้วน ไม่ต้องวงเล็บซ้ำทุกครั้ง

ตอบเฉพาะหัวข้อ "{topic}" เท่านั้น ไม่ต้องพูดถึงหัวข้ออื่น ไม่ต้องสรุปย่อเกินไป เขียนแบบเข้าใจง่ายสำหรับคนไทยที่เรียน {exam_name}"""
