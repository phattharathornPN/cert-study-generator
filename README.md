# เครื่องมือสร้างสื่อเรียนสอบเซอร์ (Cert Study Pack Generator)

แปลงเอกสารสอบกองใหญ่ให้กลายเป็นเว็บอ่านทีละหัวข้อ: สรุปเนื้อหา, สไลด์สร้างโดย AI,
และเว็บอ่านค้นหาได้พร้อม dark mode, จดโน้ต, รองรับมือถือ — deploy ขึ้นเว็บได้ฟรี

พัฒนาและทดสอบจริงกับ CCNP ENCOR 350-401 แต่ตัว pipeline ไม่ได้ผูกกับ CCNP เลย
แค่เพิ่ม cert ใหม่ใน `certs/` ก็เอาไปใช้กับเซอร์อื่นได้ทันที (ดูตัวอย่าง `certs/ccna.py`)

## หลักการทำงาน

```
เอกสารต้นทางของคุณ (PDF/เอกสาร)
        │  (คุณอัปโหลดเข้า NotebookLM notebook เอง)
        ▼
NotebookLM notebook  ──►  ถามทีละหัวข้อ  ──►  summary_th.md
        │
        ▼
slides_v2.py  ──►  อัปโหลด summary เป็น source เฉพาะหัวข้อ (กันเนื้อหาปนกัน)
        │           สั่งสร้างสไลด์ + จด task_id ลง v2/ledger.json ทันที
        │           (แยกเฟส: สั่ง / เก็บ / เก็บกวาด — ครัชกลางทางไม่เสียของ)
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
generate ออกมาขึ้น repo สาธารณะถ้ามันมาจากเอกสารที่คุณไม่มีสิทธิ์เผยแพร่ต่อ —
เพราะเหตุผลนี้ทุกโฟลเดอร์ที่ชื่อ `output*/` ถูกใส่ไว้ใน `.gitignore` เป็นค่าเริ่มต้น

## สิ่งที่ต้องมีก่อน

- Python 3.12+
- บัญชี Google ที่ใช้ [NotebookLM](https://notebooklm.google.com) ได้
  (ฟรีก็ใช้ได้ แต่ artifact quota — สไลด์/เสียง/วิดีโอ — น้อยกว่า Pro มาก และไม่มี
  วิธีเช็คว่าเหลือเท่าไหร่ ต้องยิงจนโดนปฏิเสธแล้วนับเอา)
- [`uv`](https://docs.astral.sh/uv/) สำหรับติดตั้ง NotebookLM CLI
- Node.js **22+** + npm (สำหรับ `wrangler` ใช้ตอน deploy เท่านั้น — เวอร์ชันเก่ากว่านี้
  ใช้ไม่ได้ ขึ้น error ตรงๆ ว่าต้องการ Node เท่าไหร่)
- บัญชี [Cloudflare](https://dash.cloudflare.com) (ฟรี) — ใช้เฉพาะถ้าอยากได้ URL
  สาธารณะ ถ้าไม่ deploy เว็บก็เปิดดูในเครื่องได้ปกติ

## ติดตั้ง

### 1. ติดตั้ง NotebookLM CLI

```bash
uv tool install "notebooklm-py[browser]"
notebooklm login
notebooklm auth check --test --json   # ต้องเห็น "status": "ok"
```

> **ผู้ใช้ Windows ที่เปิด Smart App Control:** ถ้า `notebooklm.exe` โดนบล็อก
> ให้เรียกผ่าน `python -m notebooklm ...` แทน — สคริปต์ทุกตัวใน repo นี้ทำแบบนี้
> อยู่แล้วภายใน ไม่ต้องแก้อะไรเพิ่ม

> **Google รีแบรนด์ NotebookLM → notebook.google.com:** ถ้าเจอ "Login not
> detected within 5 minutes" ทั้งที่ล็อกอินสำเร็จ รัน `python patch_login_domain.py`
> ก่อน login ครั้งแรก

### 2. สร้าง notebook แล้วอัปโหลดเอกสารต้นทาง

เปิด notebooklm.google.com สร้าง notebook ใหม่ อัปโหลด PDF/เอกสาร/ลิงก์ที่
ครอบคลุมเนื้อหาสอบของคุณ แล้วคัดลอก notebook ID จาก URL:

```
https://notebooklm.google.com/notebook/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
                                        └────────── ส่วนนี้แหละ ──────────┘
```

### 3. ตั้งค่า notebook ID

```bash
cp .env.example .env
# แก้ .env: ใส่ NOTEBOOK_ID_<CERT> ของคุณ เช่น NOTEBOOK_ID_CCNP_V2=...
```

`./ccnp` อ่านจาก `.env` ให้เอง ไม่ต้อง export เอง — แต่ถ้าเรียกสคริปต์ python
ตรงๆ (ไม่ผ่าน `./ccnp`) ต้อง export เข้า shell ก่อน เพราะสคริปต์อ่านจาก
environment variable จริง ไม่ได้ใช้ library dotenv

### 4. เพิ่ม cert ของตัวเอง

Cert แต่ละตัวคือไฟล์เดียวใน `certs/` — ดู `certs/ccnp_v2.py` เป็นตัวอย่าง แล้ว
สร้างไฟล์ใหม่ให้ตัวเอง:

```python
# certs/mycert.py
EXAM_NAME = "ชื่อข้อสอบของคุณ"
OUTPUT_DIR = "mycert/output"      # ต้องซ้อนอยู่ใต้ SITE_DIR เสมอ
SITE_DIR = "mycert"
DIST_DIR = "mycert/dist"
NOTEBOOK_ENV = "NOTEBOOK_ID_MYCERT"
SLIDE_FORMATS = ("pdf", "pptx")

SECTION_TITLES = {"01": "ชื่อ section แรก"}
TOPICS = [
    {"id": "01_01", "topic": "หัวข้อแรก"},
    {"id": "01_02", "topic": "หัวข้อสอง"},
]
```

⚠️ **`OUTPUT_DIR` ต้องอยู่ใต้ `SITE_DIR`** (เช่น `mycert/output` ใต้ `mycert/`)
ไม่ใช่แยกกันคนละที่ — `build_dist.py` คำนวณ path ของสไลด์เทียบกับ `SITE_DIR`
ถ้าซ้อนผิด dist จะได้แต่ `index.html` เปล่าๆ ไม่มีสไลด์ติดไปด้วย

แนะนำอิงหัวข้อจาก **เอกสาร official exam topics** ของเซอร์นั้นๆ (มักหาโหลดฟรีจาก
เว็บผู้จัดสอบ) และแบ่งให้ **1 topic สอน 1 กลไก** — อย่าใส่ list ในชื่อหัวข้อเดียว
(เช่น "RSTP, MSTP, PortFast, BPDU Guard" ควรแยกเป็น 4 topic) ไม่งั้น summary ที่
ได้จะไล่ศัพท์แทนสอนจริง แล้ว topic ที่ทับซ้อนกันจะได้เนื้อหาคล้ายกัน 50%+ โดยไม่รู้ตัว

รันด้วย `CERT=mycert ./ccnp ...` — ดูหัวข้อ [ใช้กับ cert อื่น](#ใช้กับ-cert-อื่น) ด้านล่าง

## Generate เนื้อหา

```bash
# 1. สรุปทุกหัวข้อก่อน (เรียก NotebookLM 1 ครั้งต่อหัวข้อ, ไม่ติด artifact quota)
./ccnp summary-fast          # 4 หัวข้อพร้อมกัน, resume เองถ้าหยุดกลางทาง
# หรือทีละหัวข้อ (ช้ากว่าแต่กันชนกันแน่นอนกว่า):
./ccnp summary

# 2. สร้างสไลด์ (นี่คือส่วนที่ติด quota — อ่านหัวข้อถัดไปก่อนรัน)
./ccnp slides
```

**`./ccnp slides` คือหนึ่งรอบ ไม่ใช่ลูปยาว** — มันจะ:
1. อ่าน `v2/ledger.json` + ไฟล์ที่มีอยู่จริง ว่าหัวข้อไหนเหลืออะไร
2. **สั่งสร้าง** สไลด์ที่ยังไม่มี (จดหมายเลขงาน `task_id` ลง ledger ทันทีที่สั่งสำเร็จ — ก่อนขอไฟล์ด้วยซ้ำ)
3. **เก็บ** สไลด์ที่สั่งไปก่อนหน้าและตอนนี้สร้างเสร็จแล้ว
4. **เก็บกวาด** source/artifact ชั่วคราวที่ใช้จบแล้ว

หัวข้อที่สร้างไม่เสร็จภายในรอบนี้จะถูกเก็บในรอบถัดไปโดยอัตโนมัติ — **ไม่มีการสั่งซ้ำ**
เพราะเช็ค ledger ก่อนสั่งทุกครั้ง ต่อให้ปิดโปรแกรมกลางทางหรือไฟดับก็แค่เสียรอบนั้นรอบเดียว

### Rate limit เป็นเรื่องจริง ไม่มีวิธีเช็ค quota ที่เหลือ

NotebookLM ไม่มี API บอกโควตาที่เหลือ ต้องยิงจนโดนปฏิเสธแล้วนับเอา artifact
quota (สไลด์/เสียง/วิดีโอ) น้อยกว่า chat/summary มาก และ **บัญชี Standard (ฟรี)
ได้โควตาสไลด์ต่ำกว่า Pro มาก** — วัดได้ว่า Pro ~15-20 ใบ/วัน ส่วน Standard ได้
~2-3 ใบ/วันต่อบัญชี

รันได้หลายบัญชีพร้อมกันเพื่อเพิ่มความเร็ว (quota แยกตามบัญชี ไม่ใช่ตาม notebook):

```bash
./ccnp slides "default,account2,account3"
```

ระบบจะไล่ทีละบัญชีจนกว่าจะถูกปฏิเสธ 2 ครั้งติด แล้วสลับไปบัญชีถัดไปเอง — **อย่ายิง
หลายบัญชีพร้อมกันในโปรเซสเดียว** (เคยลองแล้วดูดโควตาที่เพิ่งเติมหมดใน 30 วินาที
แล้วทุกบัญชีก็ตันพร้อมกัน ได้ผลแย่กว่าไล่ทีละตัว)

### รันอัตโนมัติทุก 20 นาที (แนะนำถ้ามีเครื่องเปิดค้างไว้)

quota เติมกลับทีละนิดตลอดเวลา ไม่ใช่รีเซ็ตครั้งเดียวต่อวัน — เครื่องที่เปิดค้างไว้
คว้าโควตาได้ทันทีที่มันเติม ดีกว่ารอคนมานั่งกดรันเอง ดู [`deploy/README.md`](deploy/README.md)

## Build และดูเว็บ

```bash
python build_site.py         # สแกน <cert>/output/ แล้วสร้าง index.html
python -m http.server 8000   # เปิดเซิร์ฟเวอร์ในเครื่อง
# เปิด http://localhost:8000
```

เว็บจะแสดงตามสิ่งที่มีอยู่จริง — ทำไปครึ่งทางก็เปิดดูได้ปกติ

## Deploy ขึ้นเว็บสาธารณะ

**Windows:** ใช้ [`deploy-site.ps1`](deploy-site.ps1) — ทำครบทั้ง build + deploy
รวมถึงจัดการปัญหา "wrangler ต้องการ Node ≥22" ให้เอง ต่อให้ shell หลักของคุณตั้ง
Node เวอร์ชันเก่าไว้ก็ไม่กระทบ (มันเรียก Node เวอร์ชันใหม่แค่ใน process ตัวเอง):

```powershell
./deploy-site.ps1                    # cert เริ่มต้น (ccnp_v2)
./deploy-site.ps1 -Cert mycert        # cert อื่น
./deploy-site.ps1 -SkipPull           # ไม่ต้องดึงจากเครื่องรีโมท แค่ build+deploy ของที่มี
```

**Mac/Linux หรือรันมือ:**

```bash
npm install -D wrangler
python build_dist.py   # คัดลอกเฉพาะไฟล์ที่เว็บใช้ (ตัด slide.pptx ทิ้ง)
npx wrangler pages project create ชื่อโปรเจกต์ของคุณ
npx wrangler pages deploy dist --project-name ชื่อโปรเจกต์ของคุณ --branch main
```

⚠️ **ห้ามลืม `--branch main`** ถ้า production branch ของโปรเจกต์ตั้งเป็น `main`
แต่คุณ deploy โดยไม่ระบุ branch มันจะไปลงเป็น Preview เงียบๆ เว็บหลักไม่อัปเดต
เช็คว่าไปโปรดักชันจริงด้วย `npx wrangler pages deployment list --project-name ...`

## สิ่งที่ได้ในตัวเว็บอ่าน

- Sidebar จัดกลุ่มตาม section พับ/กางได้ มีช่องค้นหา + แถบ progress
- ตัวแสดงสไลด์ (เรนเดอร์ด้วย PDF.js ไม่ใช่ iframe — เลื่อนได้จริงบนมือถือ ซูมแล้วคมชัด)
- แท็บสรุป (แสดงผล markdown)
- พื้นที่จดโน้ต — พิมพ์หรือวางรูป (Ctrl+V) คู่กับสไลด์ได้เลย บันทึกแยกต่อหัวข้อ
  ในเบราว์เซอร์ (IndexedDB) มีปุ่ม export/import เป็นไฟล์ JSON
- Dark mode, กดคีย์บอร์ด ← → เปลี่ยนหัวข้อ, จำหัวข้อล่าสุดที่อ่านไว้

## ใช้กับ cert อื่น

Repo นี้รองรับหลาย cert พร้อมกันผ่าน `certs/*.py` — สลับด้วย environment
variable `CERT` หรือใช้ wrapper ที่มีให้:

```bash
./ccnp status              # cert เริ่มต้น (CCNP v2)
CERT=ccna ./ccnp status     # ระบุตรง -- ccna ไม่มี wrapper ของตัวเอง (ดูหมายเหตุด้านล่าง)
./cc status                 # หรือใช้ wrapper สั้นที่มีอยู่แล้ว: ccnp1, ccnp2, cc, secplus, cissp
```

wrapper ที่มีอยู่แล้วในนี้: `ccnp` (v2), `ccnp1` (v1/136 topics), `ccnp2` (=v2),
`cc` (ISC2 Certified in Cybersecurity), `secplus` (CompTIA Security+ SY0-701),
`cissp` (ISC2 CISSP)

**CCNA ไม่มี wrapper แบบ `./ccna`** — ชื่อนั้นชนกับโฟลเดอร์ข้อมูลจริงของ CCNA
(`ccna/`, มี source PDF + output อยู่ข้างใน; บน filesystem ที่ไม่สนตัวพิมพ์เล็ก-ใหญ่
มันคือโฟลเดอร์เดียวกับ `certs/ccna.py`'s `SITE_DIR = "CCNA"`) สร้างไฟล์ชื่อ `ccna`
ทับไม่ได้ ใช้ `CERT=ccna ./ccnp <คำสั่ง>` แทน

**`sec`** ยังอยู่แต่เป็น **legacy** — ชี้ไปที่ `certs/security.py` ซึ่งเป็น pack
รวม CC+Security+/CISSP แบบเดิมที่ถูกแทนที่ด้วย `cc`/`secplus`/`cissp` แยกกันแล้ว
(เหตุผล: สอนทุกอย่างที่ระดับความลึกเดียวกันหมดทำให้ผู้สอบ CC เจอเนื้อหาระดับ CISSP)
เก็บไว้เผื่อ output เก่าที่ deploy ไปแล้วยังอยากอ้างอิง ไม่แนะนำให้ generate เพิ่ม

## โครงสร้างไฟล์ในโปรเจกต์

| ไฟล์ | หน้าที่ |
|---|---|
| `certs/*.py` | **เพิ่ม cert ใหม่ที่นี่** — topic list + path + notebook env var ของแต่ละเซอร์ |
| `cert_config.py` | โหลด cert ตาม `$CERT`, export ให้สคริปต์อื่นใช้ |
| `run.py` | resolve `NOTEBOOK_ID`/`TOPICS`/`OUTPUT_DIR` จาก cert ที่เลือก |
| `summary_only.py` / `summary_parallel.py` | สร้างสรุปข้อความ ทีละตัว/หลายตัวพร้อมกัน |
| `slides_v2.py` | สร้างสไลด์ — ระบบ ledger กันสั่งซ้ำ, หมุนหลายบัญชี, กันรันซ้อน |
| `nlm_common.py` | auth helper กลาง (`is_auth_error`, `run_with_retry`, keepalive) |
| `build_site.py` | สร้าง `index.html` จากสิ่งที่มีอยู่ใน `<cert>/output/` |
| `build_dist.py` | คัดลอกไฟล์ที่พร้อม deploy ไปที่ `<cert>/dist/` |
| `deploy-site.ps1` | (Windows) ดึงจากเครื่องรีโมท → build → deploy ในคำสั่งเดียว |
| `ccnp`, `ccnp1`, `ccnp2`, `cc`, `secplus`, `cissp`, `sec` (legacy) | CLI wrapper ต่อ cert |
| `deploy/` | รัน 24 ชม. บนเครื่องอื่น — ดู `deploy/README.md` |
| `clean_src_sources.py` | ลบ `[SRC ...]` source ชั่วคราวที่ค้างอยู่ (ปกติ `slides_v2.py` จัดการเองแล้ว ใช้กรณีฉุกเฉิน) |

## License

โค้ดในนี้ให้ใช้แบบ as-is ปรับแก้ได้ตามต้องการ ตัวมันเองไม่ได้สร้างเนื้อหาอะไรขึ้นมาเอง
— เนื้อหาทั้งหมดมาจากเอกสารที่คุณเลือกอัปโหลดเข้า NotebookLM ของตัวเอง และคุณ
เป็นผู้รับผิดชอบเรื่องสิทธิ์ในการใช้เอกสารนั้นด้วยตัวเอง
