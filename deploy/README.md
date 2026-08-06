# รันบนเครื่อง 24 ชม.

เหตุผลที่ย้าย: quota ของ NotebookLM ผูกกับ **notebook** และ refill เป็นช่วงๆ
(reset ประมาณตี 2–3) เครื่องที่เปิดค้างไว้จะรับ quota รอบใหม่ได้ทันทีโดยไม่ต้อง
มีคนมานั่งกดรันใหม่ — ไม่ได้ทำให้ quota เยอะขึ้น แค่ไม่เสียรอบเปล่า

## ติดตั้งครั้งแรก

**1. บนเครื่องปลายทาง** (หลังเปิด sshd แล้ว)

```bash
git clone https://github.com/phattharathornPN/cert-study-generator.git
cd cert-study-generator
./deploy/remote_setup.sh
```

**2. จาก workstation** — ส่ง `.env` + summary ที่ทำไปแล้ว (ไม่มี auth)

```bash
./deploy/seed_remote.sh user@192.168.2.153
```

ส่งแค่ `.env` กับ `CCNA/output/` (3 MB) — **ไม่ส่ง** `output/` ของ CCNP v1 (2.7 GB)
เพราะรอบนี้ CCNP สร้างใหม่ทั้งหมดจาก topic list v2 ลง `output_v2/`

**2.5 login บนเครื่องนั้นเอง** (ต้องมีคนอยู่หน้าจอ/console)

```bash
sudo ./deploy/desktop_login.sh default        # ทำซ้ำกับ account2..5 ถ้าต้องการตัวสำรอง
```

⚠️ **ห้าม copy `storage_state.json` จากเครื่องอื่นมาใช้** — session ที่ copy ข้ามเครื่อง
ตายภายใน ~1 ชม. 45 นาทีทุกครั้ง (วัดมาแล้ว 2 ครั้งเมื่อ 2026-08-02 เสียเวลาไปคืนหนึ่งเต็มๆ)
ตัดสาเหตุอื่นออกหมดแล้ว ทั้งการใช้พร้อมกันสองเครื่อง, IP ขาออก และ quota
ส่วน session ที่สร้างบนเครื่องเองรันยาว 3.5 ชม. โดยไม่มี auth error เลยแม้แต่ครั้งเดียว

**3. ล้าง source เก่าก่อนเริ่ม CCNP v2**

`certs/ccnp_v2.py` ใช้ notebook เดียวกับ v1 ซึ่งยังมี `[SRC xx_yy]` ที่ derive จาก
summary ของ v1 ค้างอยู่ ถ้าไม่ลบ สไลด์ v2 จะดึงเนื้อหา v1 มาปนและกิน source limit

```bash
CERT=ccnp_v2 ./ccnp clean-src          # dry run -- ดูก่อนว่าจะลบอะไร
CERT=ccnp_v2 ./ccnp clean-src --yes
```

**4. ติดตั้ง service**

```bash
sudo cp deploy/cert-*@.service /etc/systemd/system/
sudo sed -i "s|__USER__|$USER|; s|__REPO__|$PWD|" /etc/systemd/system/cert-*@.service
sudo systemctl daemon-reload
sudo systemctl enable --now cert-summary@ccna       # ต่อจาก 190/226
sudo systemctl enable --now cert-summary@ccnp_v2    # เริ่มใหม่ 0/266
```

## สลับ summary → slides อัตโนมัติ

```bash
sudo cp deploy/cert-handover.{service,timer} /etc/systemd/system/
sudo sed -i "s|__USER__|$USER|; s|__REPO__|$PWD|" /etc/systemd/system/cert-handover.service
sudo systemctl daemon-reload
sudo systemctl enable --now cert-handover.timer
```

`handover.sh` เช็คทุก 15 นาทีว่าเครื่องควรทำอะไรอยู่ แบ่งเป็น 2 เฟส:

**เฟส A — summary ของทุก cert พร้อมกัน** (ถูก เร็ว และเป็นวัตถุดิบของทุกอย่าง)

| สภาพที่เจอ | ทำอะไร |
|---|---|
| summary ยังไม่ครบ + unit หยุด | start กลับ (กันกรณี crash แล้วเงียบข้ามคืน) |
| summary ครบ | ปิด unit ของ cert นั้น |

**เฟส B — slides ทีละ cert ตาม `SLIDE_ORDER` และเริ่มต่อเมื่อ summary ครบทุก cert**

ค่า default คือ `SLIDE_ORDER="ccnp_v2 ccna"` → CCNP v2 ได้คิวก่อน CCNA รอ
เหตุผลที่ต้องเรียงคิวไม่ใช่รันขนาน: artifact rate limit ไม่ได้แยกตาม notebook
สะอาดๆ สองสายจะแย่งกันจนได้ครึ่งๆ ทั้งคู่ ทำทีละตัวได้ pack ที่ใช้งานได้จริงเร็วกว่า

ถ้าจะสลับคิว แก้ที่ `Environment=SLIDE_ORDER=...` ใน `cert-handover.service`

### auth ตาย → สลับบัญชีเอง

handover ตรวจ auth ก่อน restart ทุกครั้งที่เจอ unit ตายทั้งที่ยังมีงานค้าง ถ้า session
ของบัญชีที่ใช้อยู่เสีย มันจะไล่หาบัญชีอื่นใน `~/.notebooklm/profiles/` ที่ยัง `ok`
แล้วเขียนลง `.active-profile` + restart unit ที่กำลังรันให้ใช้บัญชีใหม่

```
profile 'account2' failed auth -- looking for a live account
!!! FAILOVER: 'account2' is dead, switching to 'default'
ccnp_v2: summaries stopped with 194 left -- restarting
```

unit อ่านไฟล์นี้ผ่าน `EnvironmentFile=-<repo>/.active-profile` แล้วส่งต่อเป็น argument
(`./ccnp summary-fast 4 default`) ถ้าไม่มีไฟล์ = ใช้ profile default ตามเดิม

**เสียเวลาแค่ 1 timer tick (15 นาที) แทนที่จะค้างทั้งคืน** — จะพังยาวก็ต่อเมื่อตายครบทุกบัญชี
ซึ่งเป็นตอนเดียวที่ยังต้องมีคนมา re-login

### ถ้าตายครบทุกบัญชี

session หมดอายุกับ quota หมด หน้าตาเหมือนกันจากมุมของ systemd — CLI เจอ `auth refresh`
fail แล้ว `break` ออกมาด้วย exit 0 ทำให้ `Restart=on-failure` ไม่ทำงาน เครื่องเลยดูเหมือน
ยังยุ่งอยู่ทั้งที่ restart แล้วพังใน 3 วินาทีทุก 15 นาที (เสียไป 8 ชม. เมื่อ 2026-08-02)

ถ้าไล่ครบทุก profile แล้วไม่มีตัวไหนผ่าน handover จะไม่ restart ให้เปล่าๆ
แต่เขียนเตือนลง journal แทน:

```bash
journalctl -u cert-handover.service | grep "AUTH DEAD"
```

พอ re-login แล้ว copy `storage_state.json` ขึ้นมา timer รอบถัดไปเดินต่อเอง ไม่ต้องสั่งอะไร

เหตุผลที่ไม่ตั้งเป็นเวลาตายตัว (เช่น ตี 5): ถ้าเดาเร็วไป slides จะไปแย่ rate limit กับ
summary ของ notebook เดียวกัน แล้วตัวตรวจ "ไม่มี progress = quota หมด" จะอ่านผิด
ถ้าเดาช้าไปเครื่องก็ว่างเปล่าหลาย ชม. — นับไฟล์เอาไม่มีทางผิด

ทั้ง `cert-summary@` และ `cert-slides@` ใช้ `Restart=on-failure` (ไม่ใช่ `always`)
เพื่อให้ตอนทำครบแล้ว unit หยุดสนิท แล้ว handover เป็นคนพาไป stage ถัดไป

## กติกาการรันพร้อมกัน

- **cert เดียวกัน ห้ามรัน summary กับ slides พร้อมกัน** — แย่ง rate limit ของ notebook
  เดียวกัน และทำให้ตัวตรวจ "ไม่มี progress = quota หมด" อ่านผิด
- **cert คนละตัว รันพร้อมกันได้** — CCNA ใช้ `NOTEBOOK_ID_CCNA`, CCNP ใช้ `NOTEBOOK_ID`
  คนละ quota pool
- เสร็จ summary ของ cert ไหนแล้วค่อยสลับไป slides ของ cert นั้น:

```bash
sudo systemctl disable --now cert-summary@ccna
sudo systemctl enable  --now cert-slides@ccna
```

## ดูความคืบหน้า

```bash
CERT=ccnp_v2 ./ccnp status
journalctl -u cert-summary@ccnp_v2 -f
tail -f logs/summary_fast_*.log
```

## ดึงผลลัพธ์กลับมา build เว็บ

เครื่อง 24 ชม. เป็นเจ้าของ output ตัวจริง เวลาจะ deploy ค่อยดึงกลับ:

```bash
rsync -az user@192.168.2.153:~/cert-study-generator/output_v2/ ./output_v2/
rsync -az user@192.168.2.153:~/cert-study-generator/CCNA/output/ ./CCNA/output/
```

## หมายเหตุ

- `IDLE_GIVE_UP=0` ใน unit = ไม่ยอมแพ้ ต่อให้ quota หมดข้ามวัน (ค่า default 48 pass
  ≈ 24 ชม. เหมาะกับเครื่องที่ปิดๆ เปิดๆ ไม่ใช่เครื่องนี้)
- `Restart=on-failure` เผื่อ crash/OOM/รีบูต — loop ของ CLI จัดการ quota กับ auth refresh
  เองอยู่แล้ว ส่วนตอนทำงานครบ unit ต้องหยุดสนิทเพื่อให้ handover พาไป stage ถัดไป
  (ถ้าใช้ `always` จะ restart วนไม่รู้จบและไม่มีวันสลับไป slides)
- ไฟล์ `~/.notebooklm/profiles/*/storage_state.json` คือ session cookie ของ Google
  `seed_remote.sh` ตั้ง `chmod go-rwx` ให้แล้ว อย่าเอาขึ้น repo หรือ share
