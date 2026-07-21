# Cert Study Pack Generator

Turn a pile of exam reference material into a topic-by-topic study site:
Thai/English summaries, AI-generated slide decks, and a searchable web
reader with dark mode, note-taking, and mobile support — all deployable
for free.

Built and battle-tested on CCNP ENCOR 350-401 (115 topics, 8 sections),
but nothing in the pipeline is CCNP-specific. Swap in your own topic list
and source material to reuse it for any certification.

## What this actually does

```
your source PDFs/docs
        │  (you upload these into a NotebookLM notebook yourself)
        ▼
NotebookLM notebook  ──►  script asks it one topic at a time
        │
        ├─► summary_th.md   (focused text summary per topic)
        └─► slide.pdf        (AI-generated slide deck per topic, pinned to
                               that topic's own source so content from other
                               topics can't leak in)
        ▼
build_site.py  ──►  index.html  (single-page reader: sidebar, search,
                                   dark mode, PDF viewer, notes panel)
        ▼
build_dist.py + wrangler  ──►  live URL on Cloudflare Pages (free)
```

## ⚠️ Before you start: copyright

This tool automates *asking questions about* material you upload — it does
not include, distribute, or bundle any textbook, course, or exam dump.
**You must have the right to use whatever source material you upload into
your own NotebookLM notebook.** Don't upload pirated PDFs. Don't commit
generated `output/` content to a public repo if it's derived from
copyrighted material you don't have redistribution rights to — that's
exactly why `output/` is gitignored by default.

## Prerequisites

- Python 3.12+
- A Google account with [NotebookLM](https://notebooklm.google.com) access
  (free tier works; Pro gets you a much higher daily generation quota)
- [`uv`](https://docs.astral.sh/uv/) for installing the NotebookLM CLI
- Node.js + npm (for `wrangler`, only needed if you want to deploy)
- A [Cloudflare](https://dash.cloudflare.com) account (free tier), only if
  you want a public URL — the site works perfectly served locally too

## Setup

### 1. Install the NotebookLM CLI

```bash
uv tool install "notebooklm-py[browser]"
notebooklm login
```

> **Windows + Smart App Control users:** if `notebooklm.exe` gets blocked,
> invoke it via `python -m notebooklm ...` instead using the venv's own
> Python (see `notebooklm auth check --test --json` to find the path) —
> every script in this repo already does this internally.

### 2. Create a notebook and upload your source material

Go to notebooklm.google.com, create a new notebook, upload the PDFs /
docs / links that cover your certification. Copy the notebook ID out of
the URL:

```
https://notebooklm.google.com/notebook/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
                                        └──────────── this part ───────────┘
```

### 3. Configure environment variables

```bash
cp .env.example .env
# edit .env: paste your NOTEBOOK_ID
```

Then actually export it in your shell (`.env` is documentation, these
scripts read real env vars — no dotenv library dependency):

```powershell
# PowerShell
$env:NOTEBOOK_ID = "your-notebook-id-here"
```
```bash
# bash
export NOTEBOOK_ID="your-notebook-id-here"
```

### 4. Write your topic list

Open [`topics.py`](topics.py) and replace `TOPICS` with your own exam's
breakdown. Keep the shape:

```python
TOPICS = [
    {"id": "01_01", "topic": "Your Topic Name Here"},
    {"id": "01_02", "topic": "Another Topic"},
    # id prefix "01_" groups topics into "Section 01" in the sidebar —
    # use whatever grouping makes sense for your exam's blueprint
]
```

Base this on the official exam topics document for your certification —
that's what determines what actually gets tested, and keeps the generated
content on-syllabus instead of wandering into whatever your source
material happens to emphasize.

## Generating content

```bash
# 1. Generate text summaries for every topic (one NotebookLM chat call each)
python run.py            # full pipeline: summary + slide + audio + flashcards
# -- or, if you only want summaries first (recommended, cheaper to redo) --
python summary_only.py

# 2. Generate slide decks (source-pinned so content can't bleed across topics)
python slides_only.py

# Both scripts resume automatically -- already-generated topics are skipped.
# If you hit a daily rate limit, just re-run the same command the next day.
python slides_only.py --start-id 03_05        # resume from a specific topic
python slides_only.py --profile work-account  # use a second NotebookLM account
```

Rate limits are real and NotebookLM doesn't expose your remaining quota —
`RateLimitError` showing up on *every* topic immediately (not just
occasionally) means you're done for the day. Come back tomorrow.

## Building and viewing the site

```bash
python build_site.py         # scans output/, generates index.html
python -m http.server 8000   # serve locally
# open http://localhost:8000
```

The site auto-detects whatever's in `output/` — partial progress renders
fine, finished topics just show more badges (📊 slide, 📝 summary, 🎧 audio).

## Deploying publicly (optional)

```bash
npm install -D wrangler
python build_dist.py   # copies only what the site needs (skips slide.pptx)
npx wrangler pages project create your-project-name
npx wrangler pages deploy dist --project-name your-project-name
```

Re-run `build_site.py` → `build_dist.py` → `wrangler pages deploy` after
generating more content to push updates. The URL stays the same across
deploys.

## What you get in the reader

- Sidebar grouped by section, collapsible, with a search box and a
  progress bar
- Slide viewer (PDF.js-rendered, not an iframe — actually scrolls on
  mobile, sharp on pinch-zoom)
- Summary tab (rendered markdown)
- Audio tab (if you generated audio overviews)
- Notes panel — type or paste screenshots (Ctrl+V) alongside the slide,
  saved per-topic in the browser (IndexedDB), with export/import to JSON
- Dark mode, keyboard navigation (←/→), remembers your last-read topic

## Repo layout

| File | What it does |
|---|---|
| `topics.py` | **Edit this** — your exam's topic list |
| `run.py` | Full pipeline: summary + slide + audio + flashcards per topic |
| `summary_only.py` | Just the text summaries |
| `slides_only.py` | Just the slide decks (source-pinned, resumable, multi-account) |
| `generate_new_summaries.py` | Fill in summaries for topics added after an initial run |
| `check_progress.py` | Prints how many topics have a slide.pdf yet |
| `check_limits.py` | Shows your NotebookLM account tier / limits |
| `build_site.py` | Generates `index.html` from whatever's in `output/` |
| `build_dist.py` | Copies deploy-ready files into `dist/` |
| `generate_slide_instructions.py` | Optional: Gemini-drafted per-topic slide checklists for higher-quality generation (needs `GEMINI_API_KEY`) |

## License

The code here is provided as-is for you to adapt. It generates nothing on
its own — all content comes from material you choose to upload into your
own NotebookLM notebook, and you're responsible for having the rights to
use it that way.
