# -*- coding: utf-8 -*-
"""Build index.html — a single-page reader for all CCNP topics.

Scans output/ and generates index.html at the project root.
Run after new slides are generated:  python build_site.py
Then serve:                          python -m http.server 8000
"""
import json
import os

OUTPUT_DIR = "output"

SECTION_TITLES = {
    "01": "Enterprise LAN Architecture",
    "02": "Enterprise Routing Network",
    "03": "Virtualization Technologies",
    "04": "Enterprise Wireless Architecture",
    "05": "Network Services",
    "06": "Enterprise Security Architecture",
    "07": "Automation and Assurance",
    "08": "Network Programmability",
}

topics = []
for folder in sorted(os.listdir(OUTPUT_DIR)):
    fpath = os.path.join(OUTPUT_DIR, folder)
    if not os.path.isdir(fpath):
        continue
    md = os.path.join(fpath, "summary_th.md")
    title = folder
    if os.path.exists(md):
        with open(md, encoding="utf-8") as f:
            first = f.readline().strip()
        if first.startswith("# "):
            title = first[2:].strip()
    topics.append({
        "folder": folder,
        "id": folder[:5],
        "section": folder[:2],
        "title": title,
        "has_pdf": os.path.exists(os.path.join(fpath, "slide.pdf")),
        "has_md": os.path.exists(md),
        "has_audio": os.path.exists(os.path.join(fpath, "audio.mp3")),
    })

manifest = json.dumps({"sections": SECTION_TITLES, "topics": topics}, ensure_ascii=False)

html = """<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0f172a">
<title>CCNP ENCOR 350-401 — สรุปภาษาไทย</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.min.js"></script>
<script>pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.worker.min.js";</script>
<style>
  :root {
    --bg: #f1f5f9; --panel: #ffffff; --text: #0f172a; --muted: #64748b;
    --border: #e2e8f0; --accent: #2563eb; --accent-soft: #dbeafe;
    --sidebar-bg: #0f172a; --sidebar-text: #cbd5e1; --sidebar-muted: #64748b;
    --sidebar-hover: #1e293b; --pdf-bg: #334155; --code-bg: #f1f5f9;
    --shadow: 0 1px 3px rgba(15,23,42,.08), 0 4px 16px rgba(15,23,42,.06);
  }
  [data-theme="dark"] {
    --bg: #0b1120; --panel: #111a2e; --text: #e2e8f0; --muted: #94a3b8;
    --border: #1e293b; --accent: #3b82f6; --accent-soft: #1e3a8a;
    --sidebar-bg: #0b1120; --sidebar-text: #cbd5e1; --sidebar-muted: #64748b;
    --sidebar-hover: #16213a; --pdf-bg: #0b1120; --code-bg: #1e293b;
    --shadow: 0 1px 3px rgba(0,0,0,.4);
  }
  * { box-sizing: border-box; margin: 0; }
  html, body { height: 100%; }
  body {
    font-family: 'Leelawadee UI', 'Segoe UI', system-ui, sans-serif;
    display: flex; overflow: hidden; background: var(--bg); color: var(--text);
    transition: background .2s;
  }

  /* ---------- Sidebar ---------- */
  #sidebar {
    width: 320px; min-width: 320px; background: var(--sidebar-bg);
    color: var(--sidebar-text); display: flex; flex-direction: column;
    border-right: 1px solid var(--border);
  }
  #sidebar-head { padding: 16px 16px 10px; }
  #sidebar-head h1 { font-size: 16px; color: #fff; letter-spacing: .2px; }
  #sidebar-head .sub { font-size: 12px; color: var(--sidebar-muted); margin-top: 2px; }
  #progress-wrap { margin-top: 10px; }
  #progress-bar { height: 6px; background: #1e293b; border-radius: 99px; overflow: hidden; }
  #progress-fill { height: 100%; background: linear-gradient(90deg, #3b82f6, #22d3ee); border-radius: 99px; }
  #progress-label { font-size: 11px; color: var(--sidebar-muted); margin-top: 4px; }
  #search {
    margin: 10px 12px; padding: 10px 12px; border-radius: 8px; border: 1px solid #1e293b;
    background: #1e293b; color: #fff; font-size: 13px; font-family: inherit; outline: none;
  }
  #search:focus { border-color: var(--accent); }
  #search::placeholder { color: var(--sidebar-muted); }
  #topic-list { flex: 1; overflow-y: auto; padding-bottom: 24px; scrollbar-width: thin; }

  .section-header {
    display: flex; align-items: center; gap: 8px; padding: 10px 14px 6px;
    font-size: 11.5px; font-weight: 700; color: #7dd3fc; text-transform: uppercase;
    letter-spacing: .6px; cursor: pointer; user-select: none;
  }
  .section-header:hover { color: #bae6fd; }
  .section-header .chev { transition: transform .15s; font-size: 10px; }
  .section-header.collapsed .chev { transform: rotate(-90deg); }
  .section-header .count { margin-left: auto; font-weight: 500; color: var(--sidebar-muted); }

  .topic {
    display: flex; align-items: center; gap: 8px;
    padding: 9px 14px 9px 24px; font-size: 13px; cursor: pointer;
    border-left: 3px solid transparent; line-height: 1.4; color: var(--sidebar-text);
  }
  .topic:hover { background: var(--sidebar-hover); }
  .topic.active { background: var(--accent); color: #fff; border-left-color: #93c5fd; }
  .topic .t-id { font-size: 11px; color: var(--sidebar-muted); font-variant-numeric: tabular-nums; }
  .topic.active .t-id { color: #bfdbfe; }
  .topic .t-title { flex: 1; }
  .topic .badges { font-size: 10px; opacity: .85; white-space: nowrap; }
  .topic.done::after { content: ""; }

  /* ---------- Main ---------- */
  #main { flex: 1; display: flex; flex-direction: column; overflow: hidden; min-width: 0; }
  #topbar {
    background: var(--panel); border-bottom: 1px solid var(--border);
    padding: 10px 16px; display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
    box-shadow: var(--shadow); z-index: 5;
  }
  #hamburger { display: none; background: none; border: none; font-size: 22px; cursor: pointer; color: var(--text); padding: 4px 8px; }
  #topic-title { font-size: 16px; font-weight: 700; flex: 1; min-width: 180px; }
  .tabs { display: flex; gap: 4px; background: var(--bg); padding: 3px; border-radius: 10px; }
  .tab {
    padding: 7px 16px; border-radius: 8px; border: none; background: transparent;
    cursor: pointer; font-size: 13px; font-family: inherit; color: var(--muted);
  }
  .tab.active { background: var(--panel); color: var(--accent); font-weight: 700; box-shadow: var(--shadow); }
  .tab:disabled { opacity: .3; cursor: not-allowed; }
  #nav-btns { display: flex; gap: 6px; align-items: center; }
  .nav-btn {
    padding: 8px 14px; border-radius: 8px; border: 1px solid var(--border);
    background: var(--panel); color: var(--text); cursor: pointer; font-size: 13px; font-family: inherit;
  }
  .nav-btn:hover { border-color: var(--accent); color: var(--accent); }
  #theme-btn { padding: 8px 10px; }

  #content { flex: 1; overflow: hidden; position: relative; }
  #empty {
    height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 10px; color: var(--muted); font-size: 15px; text-align: center; padding: 24px;
  }
  #empty .big { font-size: 40px; }

  /* PDF view */
  #pdf-view { display: none; height: 100%; overflow-y: auto; background: var(--pdf-bg); padding: 14px 0 40px; -webkit-overflow-scrolling: touch; }
  #pdf-view canvas {
    display: block; margin: 0 auto 14px; max-width: calc(100% - 20px); height: auto !important;
    box-shadow: 0 4px 20px rgba(0,0,0,.45); border-radius: 6px; background: #fff;
  }
  #pdf-status { text-align: center; color: #cbd5e1; padding: 18px; font-size: 13.5px; }

  /* Markdown view */
  #md-view {
    display: none; height: 100%; overflow-y: auto; padding: 32px clamp(16px, 5vw, 48px) 80px;
    background: var(--panel); line-height: 1.8; font-size: 15px;
  }
  #md-view > * { max-width: 860px; }
  #md-view h1 { font-size: 25px; margin: 0 0 18px; color: var(--accent); }
  #md-view h2, #md-view h3 { margin: 26px 0 10px; color: var(--accent); font-size: 19px; }
  #md-view h4 { margin: 20px 0 8px; }
  #md-view p { margin: 0 0 12px; }
  #md-view ul, #md-view ol { margin: 0 0 14px 22px; }
  #md-view li { margin-bottom: 5px; }
  #md-view code { background: var(--code-bg); padding: 2px 6px; border-radius: 5px; font-size: 13px; }
  #md-view pre { background: #0f172a; color: #e2e8f0; padding: 16px; border-radius: 10px; overflow-x: auto; margin: 0 0 16px; }
  #md-view pre code { background: none; color: inherit; }
  #md-view table { border-collapse: collapse; margin: 0 0 16px; width: 100%; }
  #md-view th, #md-view td { border: 1px solid var(--border); padding: 8px 10px; text-align: left; font-size: 13.5px; }
  #md-view th { background: var(--code-bg); }
  #md-view blockquote { border-left: 4px solid var(--accent); padding: 4px 14px; color: var(--muted); margin: 0 0 12px; }

  #audio-view { display: none; padding: 48px 24px; }
  #audio-view audio { width: 100%; max-width: 640px; }

  #overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,.5); z-index: 9; backdrop-filter: blur(2px); }

  /* ---------- Notes panel ---------- */
  #notes-panel {
    position: absolute; top: 0; right: 0; height: 100%; width: 400px; max-width: 100%;
    background: var(--panel); border-left: 1px solid var(--border);
    display: none; flex-direction: column; z-index: 6; box-shadow: -6px 0 24px rgba(0,0,0,.15);
  }
  #notes-panel.open { display: flex; }
  #notes-head {
    display: flex; align-items: center; gap: 8px; padding: 10px 14px;
    border-bottom: 1px solid var(--border); font-size: 13.5px; font-weight: 700;
  }
  #notes-head .grow { flex: 1; }
  #notes-status { font-size: 11px; color: var(--muted); font-weight: 400; }
  .notes-btn {
    background: none; border: 1px solid var(--border); border-radius: 7px;
    padding: 5px 9px; cursor: pointer; font-size: 12px; color: var(--text); font-family: inherit;
  }
  .notes-btn:hover { border-color: var(--accent); color: var(--accent); }
  #notes-editor {
    flex: 1; overflow-y: auto; padding: 16px; outline: none;
    font-size: 14px; line-height: 1.7; color: var(--text);
  }
  #notes-editor:empty::before { content: attr(data-placeholder); color: var(--muted); }
  #notes-editor img { max-width: 100%; border-radius: 8px; margin: 6px 0; box-shadow: var(--shadow); display: block; }
  #notes-editor pre, #notes-editor code { background: var(--code-bg); border-radius: 5px; padding: 2px 5px; }
  #notes-hint { padding: 8px 14px; border-top: 1px solid var(--border); font-size: 11px; color: var(--muted); }
  .nav-btn.notes-active { border-color: var(--accent); color: var(--accent); background: var(--accent-soft); }

  @media (max-width: 900px) {
    #notes-panel { width: 100%; }
  }

  /* ---------- Mobile ---------- */
  @media (max-width: 768px) {
    #sidebar {
      position: fixed; z-index: 10; height: 100%; width: min(85vw, 340px);
      transform: translateX(-100%); transition: transform .22s ease;
      box-shadow: 4px 0 24px rgba(0,0,0,.35);
    }
    #sidebar.open { transform: none; }
    #overlay.open { display: block; }
    #hamburger { display: block; }
    #topbar { padding: 8px 10px; gap: 8px; }
    #topic-title { font-size: 13.5px; order: 5; width: 100%; min-width: 0; }
    .tabs { flex: 1; justify-content: center; }
    .tab { flex: 1; text-align: center; padding: 9px 6px; font-size: 12.5px; }
    .nav-btn { padding: 9px 12px; font-size: 13px; }
    #md-view { padding: 20px 16px 90px; font-size: 14.5px; }
    .topic { padding: 12px 14px 12px 22px; }
  }
</style>
</head>
<body>
<div id="overlay" onclick="closeSidebar()"></div>
<nav id="sidebar">
  <div id="sidebar-head">
    <h1>CCNP ENCOR 350-401</h1>
    <div class="sub">สรุปภาษาไทย · Slide · Audio</div>
    <div id="progress-wrap">
      <div id="progress-bar"><div id="progress-fill" style="width:0%"></div></div>
      <div id="progress-label"></div>
    </div>
  </div>
  <input id="search" placeholder="🔍 ค้นหาหัวข้อ...">
  <div id="topic-list"></div>
</nav>
<div id="main">
  <div id="topbar">
    <button id="hamburger" onclick="toggleSidebar()">☰</button>
    <div id="topic-title">เลือกหัวข้อจากเมนู</div>
    <div class="tabs">
      <button class="tab active" data-view="pdf" id="tab-pdf">📊 สไลด์</button>
      <button class="tab" data-view="md" id="tab-md">📝 สรุป</button>
      <button class="tab" data-view="audio" id="tab-audio">🎧 เสียง</button>
    </div>
    <div id="nav-btns">
      <button class="nav-btn" onclick="step(-1)" title="หัวข้อก่อนหน้า (←)">←</button>
      <button class="nav-btn" onclick="step(1)" title="หัวข้อถัดไป (→)">→</button>
      <button class="nav-btn" id="notes-btn" onclick="toggleNotes()" title="โน้ตของฉัน">📒</button>
      <button class="nav-btn" id="theme-btn" onclick="toggleTheme()" title="สลับโหมดสว่าง/มืด">🌙</button>
    </div>
  </div>
  <div id="content">
    <div id="empty">
      <div class="big">📚</div>
      <div>เลือกหัวข้อจากเมนูเพื่อเริ่มอ่าน</div>
      <div style="font-size:12.5px">มือถือ: แตะ ☰ · คีย์บอร์ด: ← → เปลี่ยนหัวข้อ</div>
    </div>
    <div id="pdf-view"><div id="pdf-status"></div><div id="pdf-pages"></div></div>
    <div id="md-view"></div>
    <div id="audio-view"><audio controls id="audio-el"></audio></div>
    <div id="notes-panel">
      <div id="notes-head">
        📒 โน้ตของฉัน
        <span id="notes-status"></span>
        <span class="grow"></span>
        <button class="notes-btn" onclick="exportNotes()" title="ดาวน์โหลดโน้ตทั้งหมดเป็นไฟล์">⬇ Export</button>
        <button class="notes-btn" onclick="document.getElementById('notes-import').click()" title="นำเข้าโน้ตจากไฟล์">⬆ Import</button>
        <input type="file" id="notes-import" accept=".json" style="display:none" onchange="importNotes(this)">
        <button class="notes-btn" onclick="toggleNotes()">✕</button>
      </div>
      <div id="notes-editor" contenteditable="true"
        data-placeholder="พิมพ์โน้ตของหัวข้อนี้ที่นี่... วางรูปด้วย Ctrl+V ได้เลย"></div>
      <div id="notes-hint">💡 โน้ตแยกต่อหัวข้อ บันทึกอัตโนมัติในเบราว์เซอร์เครื่องนี้ — กด Export เก็บไฟล์สำรองไว้ด้วย</div>
    </div>
  </div>
</div>
<script>
const DATA = __MANIFEST__;
const listEl = document.getElementById('topic-list');
let current = -1, view = 'pdf';
let collapsed = JSON.parse(localStorage.getItem('ccnp-collapsed') || '{}');

/* ---------- Theme ---------- */
function applyTheme(t) {
  document.documentElement.setAttribute('data-theme', t);
  document.getElementById('theme-btn').textContent = t === 'dark' ? '☀️' : '🌙';
  localStorage.setItem('ccnp-theme', t);
}
function toggleTheme() {
  applyTheme(document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
}
applyTheme(localStorage.getItem('ccnp-theme') ||
  (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));

/* ---------- Progress ---------- */
(function () {
  const done = DATA.topics.filter(t => t.has_pdf).length;
  const pct = Math.round(done / DATA.topics.length * 100);
  document.getElementById('progress-fill').style.width = pct + '%';
  document.getElementById('progress-label').textContent =
    'สไลด์พร้อมแล้ว ' + done + ' / ' + DATA.topics.length + ' หัวข้อ (' + pct + '%)';
})();

/* ---------- Sidebar render ---------- */
function render(filter) {
  listEl.innerHTML = '';
  const bySection = {};
  DATA.topics.forEach((t, i) => {
    const hay = (t.id + ' ' + t.title).toLowerCase();
    if (filter && !hay.includes(filter)) return;
    (bySection[t.section] = bySection[t.section] || []).push([t, i]);
  });
  Object.keys(bySection).sort().forEach(sec => {
    const items = bySection[sec];
    const isCollapsed = collapsed[sec] && !filter;
    const h = document.createElement('div');
    h.className = 'section-header' + (isCollapsed ? ' collapsed' : '');
    h.innerHTML = '<span class="chev">▼</span> Section ' + sec + ' — ' +
      (DATA.sections[sec] || '') +
      '<span class="count">' + items.filter(x => x[0].has_pdf).length + '/' + items.length + '</span>';
    h.onclick = () => { collapsed[sec] = !collapsed[sec];
      localStorage.setItem('ccnp-collapsed', JSON.stringify(collapsed)); render(filter); };
    listEl.appendChild(h);
    if (isCollapsed) return;
    items.forEach(([t, i]) => {
      const d = document.createElement('div');
      d.className = 'topic' + (i === current ? ' active' : '');
      const badges = [t.has_pdf ? '📊' : '', t.has_md ? '📝' : '', t.has_audio ? '🎧' : ''].join('');
      d.innerHTML = '<div style="flex:1"><span class="t-id">' + t.id + '</span> ' +
        '<span class="t-title">' + t.title + '</span></div>' +
        '<span class="badges">' + badges + '</span>';
      d.onclick = () => select(i);
      listEl.appendChild(d);
    });
  });
}

/* ---------- Selection ---------- */
function select(i, skipSave) {
  current = i;
  const t = DATA.topics[i];
  document.getElementById('topic-title').textContent = '[' + t.id + '] ' + t.title;
  document.getElementById('tab-pdf').disabled = !t.has_pdf;
  document.getElementById('tab-md').disabled = !t.has_md;
  document.getElementById('tab-audio').disabled = !t.has_audio;
  if (view === 'pdf' && !t.has_pdf) view = t.has_md ? 'md' : 'audio';
  if (view === 'md' && !t.has_md) view = t.has_pdf ? 'pdf' : 'audio';
  setView(view);
  render(document.getElementById('search').value.toLowerCase());
  const act = listEl.querySelector('.topic.active');
  if (act) act.scrollIntoView({ block: 'nearest' });
  if (!skipSave) localStorage.setItem('ccnp-last', t.id);
  if (document.getElementById('notes-panel').classList.contains('open')) loadNotesFor(t.id);
  closeSidebar();
}

function setView(v) {
  view = v;
  const t = DATA.topics[current];
  document.querySelectorAll('.tab').forEach(b => b.classList.toggle('active', b.dataset.view === v));
  document.getElementById('empty').style.display = 'none';
  document.getElementById('pdf-view').style.display = v === 'pdf' ? 'block' : 'none';
  document.getElementById('md-view').style.display = v === 'md' ? 'block' : 'none';
  document.getElementById('audio-view').style.display = v === 'audio' ? 'block' : 'none';
  if (!t) return;
  const base = 'output/' + t.folder + '/';
  if (v === 'pdf' && t.has_pdf) loadPdf(base + 'slide.pdf');
  if (v === 'md' && t.has_md) {
    fetch(base + 'summary_th.md').then(r => r.text()).then(md => {
      document.getElementById('md-view').innerHTML = marked.parse(md);
      document.getElementById('md-view').scrollTop = 0;
    });
  }
  if (v === 'audio' && t.has_audio) document.getElementById('audio-el').src = base + 'audio.mp3';
}

/* ---------- PDF ---------- */
let pdfLoadToken = 0, currentPdfUrl = null;
async function loadPdf(url) {
  if (url === currentPdfUrl) return;
  currentPdfUrl = url;
  const token = ++pdfLoadToken;
  const pagesEl = document.getElementById('pdf-pages');
  const statusEl = document.getElementById('pdf-status');
  pagesEl.innerHTML = '';
  statusEl.textContent = 'กำลังโหลดสไลด์...';
  document.getElementById('pdf-view').scrollTop = 0;
  try {
    const pdf = await pdfjsLib.getDocument(url).promise;
    if (token !== pdfLoadToken) return;
    const viewWidth = document.getElementById('pdf-view').clientWidth - 20;
    for (let n = 1; n <= pdf.numPages; n++) {
      if (token !== pdfLoadToken) return;
      statusEl.textContent = 'กำลังโหลดสไลด์... หน้า ' + n + ' / ' + pdf.numPages;
      const page = await pdf.getPage(n);
      const base = page.getViewport({ scale: 1 });
      const renderWidth = Math.min(Math.max(base.width, viewWidth) * 2.2, 1800);
      const vp = page.getViewport({ scale: renderWidth / base.width });
      const canvas = document.createElement('canvas');
      canvas.width = vp.width; canvas.height = vp.height;
      canvas.style.width = Math.min(viewWidth, base.width * 1.6) + 'px';
      pagesEl.appendChild(canvas);
      await page.render({ canvasContext: canvas.getContext('2d'), viewport: vp }).promise;
    }
    if (token === pdfLoadToken) statusEl.textContent = '';
  } catch (e) {
    if (token === pdfLoadToken) statusEl.textContent = 'โหลดสไลด์ไม่สำเร็จ: ' + e.message;
  }
}

/* ---------- Nav ---------- */
function step(d) {
  const i = current + d;
  if (i >= 0 && i < DATA.topics.length) select(i);
}
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('overlay').classList.toggle('open');
}
function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('overlay').classList.remove('open');
}

document.querySelectorAll('.tab').forEach(b =>
  b.onclick = () => { if (!b.disabled) setView(b.dataset.view); });
document.getElementById('search').oninput = e => render(e.target.value.toLowerCase());
document.addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT') return;
  if (e.key === 'ArrowLeft') step(-1);
  if (e.key === 'ArrowRight') step(1);
});

/* ---------- Notes (IndexedDB) ---------- */
const notesEditor = document.getElementById('notes-editor');
const notesStatus = document.getElementById('notes-status');
let notesDb = null, notesSaveTimer = null, notesLoadedFor = null;

function openNotesDb() {
  return new Promise((resolve, reject) => {
    if (notesDb) return resolve(notesDb);
    const req = indexedDB.open('ccnp-notes', 1);
    req.onupgradeneeded = () => req.result.createObjectStore('notes');
    req.onsuccess = () => { notesDb = req.result; resolve(notesDb); };
    req.onerror = () => reject(req.error);
  });
}
async function notesGet(key) {
  const db = await openNotesDb();
  return new Promise((res, rej) => {
    const r = db.transaction('notes').objectStore('notes').get(key);
    r.onsuccess = () => res(r.result || '');
    r.onerror = () => rej(r.error);
  });
}
async function notesSet(key, val) {
  const db = await openNotesDb();
  return new Promise((res, rej) => {
    const tx = db.transaction('notes', 'readwrite');
    tx.objectStore('notes').put(val, key);
    tx.oncomplete = res; tx.onerror = () => rej(tx.error);
  });
}
async function notesAll() {
  const db = await openNotesDb();
  return new Promise((res, rej) => {
    const out = {};
    const cur = db.transaction('notes').objectStore('notes').openCursor();
    cur.onsuccess = e => {
      const c = e.target.result;
      if (c) { out[c.key] = c.value; c.continue(); } else res(out);
    };
    cur.onerror = () => rej(cur.error);
  });
}

async function loadNotesFor(tid) {
  notesLoadedFor = tid;
  const html = await notesGet(tid);
  if (notesLoadedFor !== tid) return;   // switched again mid-load
  notesEditor.innerHTML = html;
  notesStatus.textContent = '';
}
function scheduleNotesSave() {
  if (current < 0) return;
  const tid = DATA.topics[current].id;
  notesStatus.textContent = 'กำลังบันทึก...';
  clearTimeout(notesSaveTimer);
  notesSaveTimer = setTimeout(async () => {
    await notesSet(tid, notesEditor.innerHTML);
    if (notesLoadedFor === tid) notesStatus.textContent = 'บันทึกแล้ว ✓';
  }, 600);
}
notesEditor.addEventListener('input', scheduleNotesSave);

/* paste images as data URLs so they persist */
notesEditor.addEventListener('paste', e => {
  const items = (e.clipboardData || {}).items || [];
  for (const item of items) {
    if (item.type && item.type.startsWith('image/')) {
      e.preventDefault();
      const file = item.getAsFile();
      const reader = new FileReader();
      reader.onload = () => {
        const img = document.createElement('img');
        img.src = reader.result;
        const sel = window.getSelection();
        if (sel.rangeCount && notesEditor.contains(sel.anchorNode)) {
          const range = sel.getRangeAt(0);
          range.collapse(false);
          range.insertNode(img);
          range.setStartAfter(img);
          sel.removeAllRanges(); sel.addRange(range);
        } else {
          notesEditor.appendChild(img);
        }
        scheduleNotesSave();
      };
      reader.readAsDataURL(file);
      return;
    }
  }
});

function toggleNotes() {
  const p = document.getElementById('notes-panel');
  const open = !p.classList.contains('open');
  p.classList.toggle('open', open);
  document.getElementById('notes-btn').classList.toggle('notes-active', open);
  localStorage.setItem('ccnp-notes-open', open ? '1' : '');
  if (open && current >= 0) loadNotesFor(DATA.topics[current].id);
}

async function exportNotes() {
  const all = await notesAll();
  const blob = new Blob([JSON.stringify(all)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'ccnp-notes-' + new Date().toISOString().slice(0, 10) + '.json';
  a.click();
  URL.revokeObjectURL(a.href);
}
function importNotes(input) {
  const file = input.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = async () => {
    try {
      const data = JSON.parse(reader.result);
      for (const [k, v] of Object.entries(data)) {
        const existing = await notesGet(k);
        await notesSet(k, existing && existing !== v ? existing + '<hr>' + v : v);
      }
      if (current >= 0) loadNotesFor(DATA.topics[current].id);
      notesStatus.textContent = 'นำเข้าแล้ว ✓';
    } catch (e) { alert('ไฟล์ไม่ถูกต้อง: ' + e.message); }
    input.value = '';
  };
  reader.readAsText(file);
}

render('');

/* restore last-read topic + notes panel state */
(function () {
  const last = localStorage.getItem('ccnp-last');
  if (last) {
    const idx = DATA.topics.findIndex(t => t.id === last);
    if (idx >= 0) select(idx, true);
  }
  if (localStorage.getItem('ccnp-notes-open')) toggleNotes();
})();
</script>
</body>
</html>
"""

html = html.replace("__MANIFEST__", manifest)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

n_pdf = sum(1 for t in topics if t["has_pdf"])
n_md = sum(1 for t in topics if t["has_md"])
n_audio = sum(1 for t in topics if t["has_audio"])
print(f"index.html generated: {len(topics)} topics ({n_pdf} slides, {n_md} summaries, {n_audio} audio)")
print("Serve with:  python -m http.server 8000")
print("Open:        http://localhost:8000")
