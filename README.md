# เครื่องมือสร้างสื่อเรียนสอบเซอร์ (Cert Study Pack Generator)

แปลงเอกสารสอบกองใหญ่ให้กลายเป็นเว็บอ่านทีละหัวข้อ: สรุปเนื้อหา, สไลด์สร้างโดย AI,
และเว็บอ่านค้นหาได้พร้อม dark mode, จดโน้ต, รองรับมือถือ — deploy ขึ้นเว็บได้ฟรี

พัฒนาและทดสอบจริงกับ CCNP ENCOR 350-401 (115 หัวข้อ, 8 sections) แต่ตัว pipeline
ไม่ได้ผูกกับ CCNP เลย แค่เปลี่ยน topic list กับเอกสารต้นทาง ก็เอาไปใช้กับเซอร์อื่นได้ทันที

## หลักการทำงาน

```
เอกสารต้นทางของคุณ (PDF/เอกสาร)
        │  (คุณอัปโหลดเข้า NotebookLM notebook เอง)
        ▼
NotebookLM notebook  ──►  script ถามทีละหัวข้อ
        │
        ├─► summary_th.md   (สรุปเนื้อหาเฉพาะหัวข้อนั้น)
        └─► slide.pdf        (สไลด์ที่ AI สร้างต่อหัวข้อ ผูกกับ source
                               เฉพาะหัวข้อนั้น กันเนื้อหาหัวข้ออื่นปนกัน)
        ▼
build_site.py  ──►  index.html  (เว็บอ่านหน้าเดียว: sidebar, ค้นหา,
                                   dark mode, PDF viewer, พื้นที่จดโน้ต)
        ▼
build_dist.py + wrangler  ──►  URL จริงบน Cloudflare Pages (ฟรี)
```

## ⚠️ ก่อนเริ่ม: เรื่องลิขสิทธิ์

เครื่องมือนี้แค่ **automate การถามคำถามเกี่ยวกับเอกสารที่คุณอัปโหลด** — ไม่ได้แจก
หนังสือ คอร์ส หรือข้อสอบใดๆ มาให้ **คุณต้องมีสิทธิ์ในเอกสารต้นทางที่อัปโหลดเข้า
NotebookLM ของตัวเอง** ห้ามอัปโหลด PDF ละเมิดลิขสิทธิ์ และห้าม commit เนื้อหาที่
generate ออกมาใน `output/` ขึ้น repo สาธารณะถ้ามันมาจากเอกสารที่คุณไม่มีสิทธิ์
เผยแพร่ต่อ — เพราะเหตุผลนี้ `output/` เลยถูกใส่ไว้ใน `.gitignore` เป็นค่าเริ่มต้น

## สิ่งที่ต้องมีก่อน

- Python 3.12+
- บัญชี Google ที่ใช้ [NotebookLM](https://notebooklm.google.com) ได้
  (ฟรีก็ใช้ได้ แต่ Pro จะได้ quota generate ต่อวันเยอะกว่ามาก)
- [`uv`](https://docs.astral.sh/uv/) สำหรับติดตั้ง NotebookLM CLI
- Node.js + npm (สำหรับ `wrangler` ใช้ตอน deploy เท่านั้น)
- บัญชี [Cloudflare](https://dash.cloudflare.com) (ฟรี) — ใช้เฉพาะถ้าอยากได้ URL
  สาธารณะ ถ้าไม่ deploy เว็บก็เปิดดูในเครื่องได้ปกติ

## ติดตั้ง

### 1. ติดตั้ง NotebookLM CLI

```bash
uv tool install "notebooklm-py[browser]"
notebooklm login
```

> **ผู้ใช้ Windows ที่เปิด Smart App Control:** ถ้า `notebooklm.exe` โดนบล็อก
> ให้เรียกผ่าน `python -m notebooklm ...` แทน โดยใช้ python ของ venv ที่ลงไว้
> (เช็ค path ได้จาก `notebooklm auth check --test --json`) — สคริปต์ทุกตัวใน
> repo นี้ทำแบบนี้อยู่แล้วภายใน ไม่ต้องแก้อะไรเพิ่ม

### 2. สร้าง notebook แล้วอัปโหลดเอกสารต้นทาง

เปิด notebooklm.google.com สร้าง notebook ใหม่ อัปโหลด PDF/เอกสาร/ลิงก์ที่
ครอบคลุมเนื้อหาสอบของคุณ แล้วคัดลอก notebook ID จาก URL:

```
https://notebooklm.google.com/notebook/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
                                        └────────── ส่วนนี้แหละ ──────────┘
```

### 3. ตั้งค่า environment variables

```bash
cp .env.example .env
# แก้ .env: ใส่ NOTEBOOK_ID ของคุณ
```

จากนั้นต้อง export จริงในเชลล์ด้วย (ไฟล์ `.env` เป็นแค่เอกสารอ้างอิง สคริปต์อ่านจาก
environment variable จริง ไม่ได้ใช้ library dotenv):

```powershell
# PowerShell
$env:NOTEBOOK_ID = "notebook-id-ของคุณ"
```
```bash
# bash
export NOTEBOOK_ID="notebook-id-ของคุณ"
```

### 4. เขียน topic list ของตัวเอง

เปิด [`topics.py`](topics.py) แล้วแทนที่ `TOPICS` ด้วยหัวข้อสอบของคุณเอง
รูปแบบต้องเหมือนเดิม:

```python
TOPICS = [
    {"id": "01_01", "topic": "ชื่อหัวข้อของคุณ"},
    {"id": "01_02", "topic": "หัวข้ออื่น"},
    # เลขนำหน้า "01_" คือกลุ่ม Section 01 ใน sidebar
    # จัดกลุ่มตามโครง blueprint ของข้อสอบคุณเองได้เลย
]
```

แนะนำอิงจาก **เอกสาร official exam topics** ของเซอร์นั้นๆ (มักหาโหลดฟรีจาก
เว็บผู้จัดสอบ) เพราะเป็นตัวกำหนดว่าอะไรออกสอบจริง ช่วยให้เนื้อหาที่ generate ตรง
ประเด็น ไม่หลุดไปตามที่เอกสารต้นทางบังเอิญเน้น

## Generate เนื้อหา

```bash
# 1. สร้างสรุปข้อความทุกหัวข้อก่อน (เรียก NotebookLM 1 ครั้งต่อหัวข้อ)
python run.py            # full pipeline: สรุป + สไลด์ + เสียง + flashcard
# -- หรือถ้าอยากได้แค่สรุปก่อน (แนะนำ เพราะแก้/รันซ้ำถูกกว่า) --
python summary_only.py

# 2. สร้างสไลด์ (ผูก source เฉพาะหัวข้อ กันเนื้อหาปนกัน)
python slides_only.py

# ทั้งสองสคริปต์ resume อัตโนมัติ — หัวข้อที่ทำเสร็จแล้วจะถูกข้าม
# ถ้าเจอ rate limit วันนี้ ก็แค่รันคำสั่งเดิมซ้ำวันถัดไป
python slides_only.py --start-id 03_05        # เริ่มจากหัวข้อที่ระบุ
python slides_only.py --profile work-account  # ใช้บัญชี NotebookLM ที่ 2
```

Rate limit เป็นเรื่องจริง และ NotebookLM ไม่มีวิธีเช็ค quota ที่เหลือ —
ถ้าเจอ `RateLimitError` **ทันทีทุกหัวข้อ** (ไม่ใช่แค่บางครั้ง) แปลว่า quota
วันนี้หมดแล้ว รอพรุ่งนี้ค่อยรันต่อ

## Build และดูเว็บ

```bash
python build_site.py         # สแกน output/ แล้วสร้าง index.html
python -m http.server 8000   # เปิดเซิร์ฟเวอร์ในเครื่อง
# เปิด http://localhost:8000
```

เว็บจะแสดงตามสิ่งที่มีอยู่จริงใน `output/` — ทำไปครึ่งทางก็เปิดดูได้ปกติ
หัวข้อไหนเสร็จแล้วจะมี badge เพิ่ม (📊 สไลด์, 📝 สรุป, 🎧 เสียง)

## Deploy ขึ้นเว็บสาธารณะ (ทำหรือไม่ทำก็ได้)

```bash
npm install -D wrangler
python build_dist.py   # คัดลอกเฉพาะไฟล์ที่เว็บใช้ (ตัด slide.pptx ทิ้ง)
npx wrangler pages project create ชื่อโปรเจกต์ของคุณ
npx wrangler pages deploy dist --project-name ชื่อโปรเจกต์ของคุณ
```

พอ generate เนื้อหาเพิ่ม ให้รัน `build_site.py` → `build_dist.py` →
`wrangler pages deploy` ซ้ำเพื่ออัปเดตเว็บ — URL หลักจะเหมือนเดิมทุกรอบ deploy

## สิ่งที่ได้ในตัวเว็บอ่าน

- Sidebar จัดกลุ่มตาม section พับ/กางได้ มีช่องค้นหา + แถบ progress
- ตัวแสดงสไลด์ (เรนเดอร์ด้วย PDF.js ไม่ใช่ iframe — เลื่อนได้จริงบนมือถือ
  ซูมแล้วคมชัด)
- แท็บสรุป (แสดงผล markdown)
- แท็บเสียง (ถ้า generate audio overview ไว้)
- พื้นที่จดโน้ต — พิมพ์หรือวางรูป (Ctrl+V) คู่กับสไลด์ได้เลย บันทึกแยกต่อหัวข้อ
  ในเบราว์เซอร์ (IndexedDB) มีปุ่ม export/import เป็นไฟล์ JSON
- Dark mode, กดคีย์บอร์ด ← → เปลี่ยนหัวข้อ, จำหัวข้อล่าสุดที่อ่านไว้

## โครงสร้างไฟล์ในโปรเจกต์

| ไฟล์ | หน้าที่ |
|---|---|
| `topics.py` | **แก้ไฟล์นี้** — topic list ของข้อสอบคุณ |
| `run.py` | Pipeline เต็ม: สรุป + สไลด์ + เสียง + flashcard ต่อหัวข้อ |
| `summary_only.py` | สร้างเฉพาะสรุปข้อความ |
| `slides_only.py` | สร้างเฉพาะสไลด์ (ผูก source เฉพาะหัวข้อ, resume ได้, ใช้หลายบัญชีได้) |
| `generate_new_summaries.py` | เติมสรุปให้หัวข้อที่เพิ่มทีหลัง (หลังจากรัน pipeline หลักไปแล้ว) |
| `check_progress.py` | เช็คว่ามีกี่หัวข้อที่มีสไลด์แล้ว |
| `check_limits.py` | เช็ค tier/limit ของบัญชี NotebookLM |
| `build_site.py` | สร้าง `index.html` จากสิ่งที่มีอยู่ใน `output/` |
| `build_dist.py` | คัดลอกไฟล์ที่พร้อม deploy ไปที่ `dist/` |
| `generate_slide_instructions.py` | (ทำหรือไม่ทำก็ได้) ให้ Gemini ช่วยคิด checklist เฉพาะหัวข้อก่อน generate สไลด์ เพื่อคุณภาพที่ดีขึ้น (ต้องมี `GEMINI_API_KEY`) |

## License

โค้ดในนี้ให้ใช้แบบ as-is ปรับแก้ได้ตามต้องการ ตัวมันเองไม่ได้สร้างเนื้อหาอะไรขึ้นมาเอง
— เนื้อหาทั้งหมดมาจากเอกสารที่คุณเลือกอัปโหลดเข้า NotebookLM ของตัวเอง และคุณ
เป็นผู้รับผิดชอบเรื่องสิทธิ์ในการใช้เอกสารนั้นด้วยตัวเอง
