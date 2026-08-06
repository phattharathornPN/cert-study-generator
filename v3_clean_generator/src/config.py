import os
import sys

def load_env_file(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip("\"'")

# Load .env from the parent project directory
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
load_env_file(env_path)

# Attempt to load topics
try:
    import src.ccnp_topics as ccnp_topics
    TOPICS = ccnp_topics.TOPICS
except ImportError:
    TOPICS = []

EXAM_NAME = "CCNP ENCOR 350-401"
NOTEBOOK_ENV_VAR = "NOTEBOOK_ID_CCNP_V2"
OUTPUT_DIR = "output"

def get_notebook_id() -> str:
    """Retrieve Notebook ID from environment variables."""
    nid = os.environ.get(NOTEBOOK_ENV_VAR) or os.environ.get("NOTEBOOK_ID")
    if not nid:
        print(f"ERROR: Notebook ID environment variable '{NOTEBOOK_ENV_VAR}' is not set.")
        sys.exit(1)
    return nid

def build_focus_prompt(topic: str) -> str:
    return f"""ฉันต้องการเรียนเฉพาะหัวข้อนี้จากเนื้อหา {EXAM_NAME}:

หัวข้อ: {topic}

กรุณาสรุปเฉพาะหัวข้อนี้เป็นภาษาไทย โดยครอบคลุม:
1. แนวคิดหลักและความสำคัญ
2. การทำงาน (How it works)
3. ตัวอย่าง config จริง (Cisco IOS / IOS-XE) ถ้ามี
4. Key points ที่ต้องจำสำหรับสอบ {EXAM_NAME}

ตอบเฉพาะหัวข้อ "{topic}" เท่านั้น ไม่ต้องพูดถึงหัวข้ออื่น"""

def build_slide_instructions(topic: str) -> str:
    return (
        f'สร้างสไลด์เฉพาะหัวข้อ "{topic}" จากเนื้อหา {EXAM_NAME} เท่านั้น '
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

def build_audio_instructions(topic: str) -> str:
    return (
        f'อธิบายเฉพาะหัวข้อ "{topic}" จากเนื้อหา {EXAM_NAME} เป็นภาษาไทย '
        f"แบบเข้าใจง่าย ไม่ต้องพูดถึงหัวข้ออื่น โดยครอบคลุม: "
        f"1) แนวคิดหลักและความสำคัญ 2) การทำงาน (How it works) "
        f"3) ตัวอย่าง config จริง (Cisco IOS / IOS-XE) ถ้ามี "
        f"4) Key points ที่ต้องจำสำหรับสอบ"
    )

def build_flashcards_instructions(topic: str) -> str:
    return f"สร้างแฟลชการ์ดเป็นภาษาไทยสำหรับหัวข้อ {topic}"
