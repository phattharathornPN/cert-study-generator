# รันบนเครื่อง 24 ชม.

เหตุผล: NotebookLM quota **เติมกลับทีละนิดตลอดเวลา** ไม่ใช่รีเซ็ตครั้งเดียวต่อวัน
(วัดได้ประมาณ 2-6 หัวข้อ/ชั่วโมง ต่อบัญชี ขึ้นกับ tier) เครื่องที่เปิดค้างไว้จะคว้า
โควตาได้ทันทีที่มันเติม — ไม่ได้ทำให้ quota เยอะขึ้น แค่ไม่เสียรอบเปล่า

ตัวรันคือ [`slides_v2.py`](../slides_v2.py): เขียน `task_id` ลง
`<cert>/ledger.json` **ก่อน**ขอไฟล์เสมอ ต่อให้เครื่องดับหรือรอบถูกฆ่ากลางทาง
ก็ไม่มีการสั่งซ้ำ ระบบนี้ถูกออกแบบมาแทนของเดิม (`slides_only.py` /
`slides_parallel.py`, ถูกลบไปแล้ว) ที่เชื่อคำตอบจาก API มากกว่าไฟล์บนดิสก์ —
ผลคือ `wait_for_completion` timeout แล้วรายงานว่า artifact "หายไป" ทั้งที่
สร้างสำเร็จ แล้วไปสั่งซ้ำหัวข้อเดิม 3-4 ครั้ง เผาโควตาที่แพงที่สุดไปกับของที่มีอยู่แล้ว

## ติดตั้งครั้งแรก

**1. บนเครื่องปลายทาง** (หลังเปิด sshd แล้ว)

```bash
git clone https://github.com/phattharathornPN/cert-study-generator.git
cd cert-study-generator
./deploy/remote_setup.sh
```

**2. จาก workstation** — ส่ง `.env` (ไม่มี auth ในนั้น)

```bash
./deploy/seed_remote.sh user@remote-host
```

**3. login บนเครื่องนั้นเอง** (ต้องมีคนอยู่หน้าจอ/console จริงๆ)

```bash
sudo ./deploy/desktop_login.sh default
sudo ./deploy/desktop_login.sh account2   # ทำซ้ำถ้าจะใช้หลายบัญชี
```

⚠️ **ห้าม copy `~/.notebooklm/profiles/*/storage_state.json` จากเครื่องอื่นมาวาง**
— session ที่ถูก copy ข้ามเครื่องตายภายใน ~1-2 ชั่วโมงทุกครั้ง (วัดซ้ำ 2 ครั้งแล้ว
ผลตรงกัน) ส่วน session ที่ login บนเครื่องนั้นเองอยู่ได้เป็นวัน — ต้อง login ใหม่
ทุกเครื่อง ไม่มีทางลัด

**4. ล้าง source เก่าถ้า notebook เคยใช้กับ pack อื่นมาก่อน**

`[SRC <id>]` เป็น source ชั่วคราวที่ผูกสไลด์กับหัวข้อเดียว — ถ้า notebook เคยมี
sources จาก topic list เก่าที่ไม่ตรงกับตัวปัจจุบัน ต้องเคลียร์ก่อน ไม่งั้นสไลด์ใหม่
อาจดึงเนื้อหาเก่ามาปน:

```bash
CERT=ccnp_v2 ./ccnp clean-src          # dry run -- ดูก่อนว่าจะลบอะไร
CERT=ccnp_v2 ./ccnp clean-src --yes
```

(ปกติไม่ต้องทำเอง — `slides_v2.py` กวาด source ที่ใช้จบแล้วทุกรอบอัตโนมัติ ข้อนี้
ใช้แค่ตอนตั้งเครื่องใหม่ครั้งแรกหรือ notebook มีของเก่าปนมา)

**5. ติดตั้ง service + timer**

```bash
sudo cp deploy/slides-cycle@.{service,timer} /etc/systemd/system/
sudo sed -i "s|__USER__|$USER|; s|__REPO__|$PWD|" /etc/systemd/system/slides-cycle@.service
sudo systemctl daemon-reload
sudo systemctl enable --now slides-cycle@ccnp_v2.timer
```

ตั้งได้หลาย cert พร้อมกัน (คนละ notebook คนละ quota pool, ไม่แย่งกัน):

```bash
sudo systemctl enable --now slides-cycle@ccna.timer
```

## กลไกการทำงาน

`slides-cycle@.timer` ยิง `slides-cycle@.service` ทุก 20 นาที (`OnBootSec=5min`,
`Persistent=true` — พลาดรอบเพราะเครื่องดับก็ยิงชดเชยทันทีที่บูตกลับมา) แต่ละรอบ
เป็น **oneshot** ไม่ใช่ daemon ค้าง: อ่านดิสก์ + ledger ใหม่ทุกครั้ง ไม่มี state
ในหน่วยความจำที่หายได้ ทำ 4 อย่างแล้วจบ:

1. **ปล่อยของค้าง** — ถ้ารอบก่อนถูกฆ่ากลางทาง (`state=requesting`/`sourcing`)
   ปล่อย source นั้นคืนให้ sweep เก็บ แล้วอนุญาตให้สั่งใหม่
2. **สั่งสร้าง** — ไล่ทีละบัญชีจนถูกปฏิเสธ 2 ครั้งติด แล้วสลับบัญชีถัดไป จด
   `task_id` ลง ledger ทันทีที่สั่งสำเร็จ (ก่อนขอไฟล์)
3. **เก็บสไลด์** — โหลดไฟล์ของหัวข้อที่มี `task_id` ค้างจากรอบก่อนๆ
   ยังไม่พร้อมก็ปล่อยไว้ ไม่สั่งใหม่ ไม่ถามซ้ำเกินจำเป็น
4. **เก็บกวาด** — ลบ `[SRC]` source กับ artifact ที่ใช้จบแล้ว

**ทำไมทีละบัญชี ไม่ใช่หลายบัญชีพร้อมกัน:** ลองแล้วพบว่ายิงพร้อมกันดูดโควตาที่
เพิ่งเติมหมดใน 30 วินาที แล้วทุกบัญชีตันพร้อมกัน — ทีละบัญชีได้โควตารวมเท่ากัน
แต่ไม่มีการแย่งกันเปล่าๆ

## กติกาการรันพร้อมกัน

- **notebook เดียวกัน ห้ามมีมากกว่า 1 process ยิงพร้อมกัน** — `slides_v2.py` มี lock
  ไฟล์ (`<cert>/.slides.lock`) กันเรื่องนี้อยู่แล้ว ถ้าเจอ process ที่ pid ตายแล้วจริง
  lock จะถูกเคลียร์อัตโนมัติในรอบถัดไป
- **cert คนละตัว (คนละ notebook) รันพร้อมกันได้** — ไม่แย่ง quota กัน
- **อย่ารัน `./ccnp slides` มือ พร้อมกับที่ timer ยังทำงานอยู่** — หยุด timer ก่อน:
  ```bash
  sudo systemctl stop slides-cycle@ccnp_v2.timer slides-cycle@ccnp_v2.service
  # ... รันมือ ...
  sudo systemctl start slides-cycle@ccnp_v2.timer
  ```

## ดูความคืบหน้า / เช็คสุขภาพ

```bash
# มีกี่ใบแล้ว
ls <cert>/output/*/slide.pdf | wc -l

# กำลังทำอะไรอยู่ บัญชีไหน
journalctl -u slides-cycle@ccnp_v2 --since -30min --no-pager

# รอบถัดไปกี่โมง
systemctl list-timers slides-cycle@ccnp_v2.timer --no-pager

# ledger กับ source ต้องตรงกัน (ถ้าไม่ตรง = มีอะไรรั่ว)
python3 -c "
import json, collections
d = json.load(open('v2/ledger.json'))
print(dict(collections.Counter(v.get('state') for v in d.values())))
print('live sources:', sum(1 for v in d.values() if v.get('source_id')))
"
CERT=ccnp_v2 ./ccnp sources
```

**เกณฑ์ปกติ:** `live sources` ในคำสั่งบนต้องเท่ากับ `[SRC] derived` ในคำสั่งล่าง
ถ้าไม่ตรงหรือ `total` ไต่ขึ้นเรื่อยๆ (ควรนิ่งใกล้ตัวเลข reference material) ให้รัน
`CERT=ccnp_v2 ./ccnp clean-src --yes` เพื่อล้าง

## Auth ตายกลางทาง

ถ้าทุกบัญชีถูกปฏิเสธจนหมด service จะจบรอบตามปกติโดยไม่ได้อะไร (ไม่ใช่ error —
เป็นแค่ "ยังไม่มีโควตา" ) แต่ถ้า **session หมดอายุจริง** (ไม่ใช่แค่โควตาหมด)
`slides_v2.py` จะ log ชัดเจนว่าบัญชีไหน auth พังและหยุดพยายามกับบัญชีนั้นในรอบนั้น
ถ้าตายครบทุกบัญชี ต้อง login ใหม่ตามขั้นตอนข้อ 3 ด้านบน — เข้าเครื่องเองเท่านั้น
ทำจากระยะไกลด้วย copied cookies ไม่ได้ (อ่านเหตุผลด้านบน)

## ดึงผลลัพธ์กลับมา build เว็บ

เครื่อง 24 ชม. เป็นเจ้าของ output ตัวจริง เวลาจะ deploy ค่อยดึงกลับ — ถ้าใช้
Windows มี [`deploy-site.ps1`](../deploy-site.ps1) ทำให้ทั้งหมดในคำสั่งเดียว
(ดึง + build + deploy) ไม่ต้องทำตามด้านล่าง:

```bash
rsync -az user@remote-host:~/cert-study-generator/v2/output/ ./v2/output/
python build_site.py && python build_dist.py
npx wrangler pages deploy v2/dist --project-name your-project --branch main
```

## หมายเหตุ

- `TimeoutStartSec=3h` ใน service เป็นตาข่ายกันค้าง ไม่ใช่ตัวคุมจังหวะ — รอบปกติ
  จบใน 10-15 นาทีเสมอ (2 refusal × ~90 วิ ต่อบัญชี × จำนวนบัญชี) ถ้ารอบไหนกิน
  เวลาเป็นชั่วโมงคือมีอะไรผิดปกติ ให้เช็ค journal
- ไฟล์ `~/.notebooklm/profiles/*/storage_state.json` คือ session cookie ของ Google
  — อย่าเอาขึ้น repo หรือแชร์ให้ใคร
