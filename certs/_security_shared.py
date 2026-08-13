# -*- coding: utf-8 -*-
"""Prompt templates shared by the security certs (CC, Security+, CISSP).

Same reason certs/_shared.py exists for the networking certs: the three
security packs need *almost* the same prompt, and the one thing that must
never drift between them is the guard that stopped the original bug -- the
explicit ban on Cisco/router config examples, which a networking-flavoured
template silently injected into 354 security summaries before it was caught.
Keeping one copy here means a fix lands in all three at once.

What legitimately differs between the three is depth and persona, so that is
passed in rather than copy-pasted:

  CC        an entry-level candidate who must recognise and define
  Security+ a hands-on practitioner who must pick the right control or tool
  CISSP     a manager/advisor who must justify a risk-based decision

Everything else -- section order, the citation ban, the table rules, the
no-network-config guard -- is identical on purpose.
"""

# The one rule that must be byte-identical across all three packs. Every
# security topic is governance/operations content; a device config example is
# always wrong here, and this is the exact sentence whose absence caused the
# original contamination.
_NO_NETWORK_CONFIG = (
    "ห้ามยกตัวอย่าง config อุปกรณ์เครือข่าย (Cisco IOS หรืออื่นๆ) หรือ diagram เส้นทาง"
    "ข้อมูลผ่าน router/switch เด็ดขาด เพราะเนื้อหานี้เป็นการบริหารความมั่นคงสารสนเทศ ไม่ใช่วิชาเครือข่าย"
)


def security_slide_instructions(
    exam_name: str,
    topic: str,
    *,
    persona: str,
    worked_example: str,
    exam_wording: str,
) -> str:
    """Slide instructions for one security topic.

    persona        -- how the candidate is expected to think (one clause)
    worked_example -- what section 3's worked example should actually be
    exam_wording   -- the exam-specific trap wording to warn about
    """
    return (
        f'สร้างสไลด์เฉพาะหัวข้อ "{topic}" จากเนื้อหา {exam_name} เท่านั้น '
        f"ไม่ต้องพูดถึงหัวข้ออื่น โดยครอบคลุม: "
        f"1) แนวคิดหลักและความสำคัญ ทำไมข้อสอบถึงถามเรื่องนี้ "
        f"2) กลไก/หลักการทำงาน อธิบายว่ามันทำงานหรือถูกนำไปใช้อย่างไรจริง "
        f"3) {worked_example} "
        f"4) Key points ที่ต้องจำสำหรับสอบ {exam_wording} "
        f"มุมมองที่ต้องใช้ตอบ: {persona} "
        f"ข้อควรระวังสำคัญ: {_NO_NETWORK_CONFIG} "
        f"ตรวจสอบว่าทุกตัวอย่างสื่อสารตรงกับข้อความที่อธิบายจริง"
    )


def security_summary_prompt(
    exam_name: str,
    topic: str,
    *,
    persona: str,
    worked_example: str,
    exam_wording: str,
    compare_hint: str,
) -> str:
    """Detailed Thai summary prompt for one security topic.

    compare_hint -- what section 4 should compare against, phrased for this
                    exam (CC compares definitions; CISSP compares decisions).
    """
    return f"""ฉันต้องการเรียนเฉพาะหัวข้อนี้จากเนื้อหา {exam_name} แบบละเอียดที่สุด:

หัวข้อ: {topic}

กรุณาสรุปเฉพาะหัวข้อนี้เป็นภาษาไทยแบบละเอียด (เขียนยาวได้เต็มที่ ไม่ต้องสั้น) โดยเรียงตามนี้:

0. **TL;DR — สรุป 30 วินาที** (ขึ้นก่อนเพื่อนสุด) เขียน 3-5 bullet ที่ถ้าอ่านแค่นี้ก่อนเข้าห้องสอบก็ยังได้ประเด็นหลักครบ
1. แนวคิดหลักและความสำคัญ — อธิบายว่ามันคืออะไร ใช้แก้ปัญหาอะไร และทำไมข้อสอบถึงถามเรื่องนี้
2. กลไก/หลักการทำงานโดยละเอียด — อธิบายทุกขั้นตอน/กระบวนการที่เกี่ยวข้อง ถ้าเป็นกระบวนการหลายขั้นให้เขียนเป็นลำดับเลข 1-2-3 พร้อมตัวอย่างประกอบที่จับต้องได้ ไม่ใช่พูดลอย ๆ
3. {worked_example}
4. ข้อแตกต่าง/เปรียบเทียบกับแนวคิดใกล้เคียงที่ข้อสอบชอบเอามาสับสนกัน (ถ้ามี) — {compare_hint}
5. ข้อผิดพลาดที่พบบ่อย (Common pitfalls) ที่มักทำให้ติดตอนสอบหรือตอนทำงานจริง {exam_wording}
6. Key points ที่ต้องจำสำหรับสอบ {exam_name} — สรุปเป็น bullet สั้นกระชับท้ายสุด

มุมมองที่ต้องใช้ตอบ: {persona}

รูปแบบการเขียน (สำคัญมาก ทำตามให้ครบ):
- **ห้ามใส่เลขอ้างอิงท้ายประโยคเด็ดขาด** เช่น [1], [2, 3], [6-13] — เขียนเป็นเนื้อความล้วน ๆ ให้อ่านลื่น
- **ข้อ 4 (เปรียบเทียบ) ต้องทำเป็นตาราง Markdown เสมอ** คอลัมน์แรกคือหัวข้อที่เทียบ แล้วแยกคอลัมน์ตามแนวคิด ห้ามเขียนเป็น bullet ยาว ๆ
- ที่ไหนมีค่าตัวเลขหรือตัวเปรียบเทียบหลายตัว ให้ใช้ตาราง Markdown แทนการร่ายเป็นย่อหน้า
- **{_NO_NETWORK_CONFIG}**
- ศัพท์เทคนิคคงภาษาอังกฤษไว้ วงเล็บไทยกำกับครั้งแรกที่เจอ แล้วครั้งต่อไปใช้อังกฤษล้วน ไม่ต้องวงเล็บซ้ำทุกครั้ง

ตอบเฉพาะหัวข้อ "{topic}" เท่านั้น ไม่ต้องพูดถึงหัวข้ออื่น ไม่ต้องสรุปย่อเกินไป เขียนแบบเข้าใจง่ายสำหรับคนไทยที่เตรียมสอบ {exam_name}"""
