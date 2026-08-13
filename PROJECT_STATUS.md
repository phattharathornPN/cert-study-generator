# Project status — snapshot from 2026-08-11

Read this when picking the project back up cold. Numbers here decay fast —
verify against the disk / the remote box before trusting them for anything
you're about to act on. See `CLAUDE.md` for durable rules, `README.md` /
`deploy/README.md` for how things work.

## Who's studying what, and why it matters for priority

User is working toward CCNP ENCOR 350-401, CCNA, and the three security certs
(ISC2 CC, CompTIA Security+ SY0-701, ISC2 CISSP). No exam date is booked for
any of them — priority is soft, not deadline-driven.

**Priority order as of 2026-08-11: CCNA first**, then the three security
packs. This reverses the earlier (2026-08-09) CCNP → Security → CCNA order;
CCNP v2 has since finished, and the user explicitly asked to start CCNA ahead
of the security work while the security packs were being restructured.

User works from the **workstation** (this machine, `D:\CCNP-Study`) day to
day — checking the site, running commands. The **192.168.2.153 box** is
where generation actually runs 24/7; the user rarely touches it directly and
mostly wants status reported, not raw SSH output.

## The security split (2026-08-11)

The combined `security` pack (357 topics, "CC + Security+ + CISSP" taught once
at CISSP depth) was **retired and replaced by three separate packs** at the
user's request. Reason: a CC candidate reading a CISSP-depth answer gets a
management decision essay where the exam only asks them to recognise a
definition. Depth and persona now differ per pack.

**Topic lists were then verified against the official exam outlines** (same
day) after the user asked what they were based on — the honest answer at that
point was "written from memory, never checked against a source." Findings:

| Pack | Cert file | Topics | Verified against | Result |
|---|---|---|---|---|
| CC | `certs/cc.py` | **67** (was 132) | isc2.org outline, fetched directly | Rewritten — the original had CISSP/Sec+-depth material (ABAC, digital signatures, biometric FAR/FRR/CER) that isn't in scope. Now maps 1:1 to the 17 official sub-objectives |
| Security+ | `certs/secplus.py` | 239 (was 231) | Official SY0-701 Exam Objectives v5.0 PDF | Already closely aligned; added ~12 explicitly-named items that were missing (blockchain, crypto attack types, GPO/SELinux, UBA, SD-WAN/SASE, 802.1X) |
| CISSP | `certs/cissp.py` | 293 (was 291) | Official ISC2 CISSP Exam Outline PDF (eff. 2024-04-15) | Already closely aligned; added the CIA/authenticity/non-repudiation fundamentals topic and Business Impact Analysis, both named explicitly in the outline but missing from the topic list |

Persona each pack's prompt asks for: CC = entry level (define/distinguish
terms only, no budget reasoning); Security+ = hands-on practitioner (which
tool/setting, PBQ-shaped); CISSP = manager (risk-based decision, MOST/BEST/FIRST).

All three **share `NOTEBOOK_ID_SECURITY`** — one uploaded source library covers
all three blueprints. One consequence worth remembering: `slides_v2.py`'s lock
is per *cert*, not per *notebook*, so **do not run slide cycles for two
security packs at once**.

Shared prompt scaffolding lives in `certs/_security_shared.py` (mirroring
`certs/_shared.py` for the networking certs). The no-network-config guard is
defined once there on purpose — see the Cisco contamination note below.

`certs/security.py` is left in the tree but is **superseded**; its output on
the box (`security/output`, 260 summaries + 39 slides) is orphaned. Nothing
was deleted — the user chose "start fresh" for the three new packs, not to
purge the old artefacts.

## Progress as of 2026-08-11 ~17:20

| Cert | Summary | Slides | Notebook env | Notes |
|---|---|---|---|---|
| CCNP v2 (`ccnp_v2`) | 266/266 ✅ | 266/266 ✅ | `NOTEBOOK_ID_CCNP_V2` | Complete |
| CCNA (`ccna`) | 226/226 ✅ | 15/226 | `NOTEBOOK_ID_CCNA` | `slides-cycle@ccna.timer` running; **deployed** to https://ccna-study-6u4.pages.dev (note the `-6u4` suffix — `ccna-study.pages.dev` was already taken globally). Re-run `./deploy-site.ps1 -Cert ccna -Project ccna-study` to push newer slides |
| CC (`cc`) | 67/67 ✅ | 0/67 | `NOTEBOOK_ID_SECURITY` | Complete, verified against the official ISC2 outline (see split section above) |
| Security+ (`secplus`) | in progress | 0/239 | `NOTEBOOK_ID_SECURITY` | Running now via `account2` (see quota-rotation note below) |
| CISSP (`cissp`) | 0/293 | 0/293 | `NOTEBOOK_ID_SECURITY` | Queued behind Security+ |

Live sites: **https://ccnp-encor-study.pages.dev** (CCNP v2),
**https://ccna-study-6u4.pages.dev** (CCNA), and
**https://security-study.pages.dev** (the retired combined pack, last deployed
with 260 summaries / 39 slides — orphaned, not being updated). cc/secplus/cissp
have no site yet.

## Known account issues (2026-08-11)

- **`account6` has no access to the CCNA notebook.** Confirmed via direct RPC
  test: `sources.list()` on CCNA's notebook returns `Permission denied` for
  `account6` specifically, while the same call succeeds for every account on
  the shared Security notebook. Its own login session is valid — it's a
  sharing/collaborator gap on that one notebook. **Fix requires the user**:
  open the CCNA notebook in NotebookLM with the owning account, Share →  add
  `phatpforb@gmail.com` (account6) as **Editor**. Not something a script can
  do. Until fixed, CCNA slide generation runs on 5/6 accounts.
- **Chat quota is per-account daily, same as slide artifact quota** — this
  was previously documented for slides only; confirmed the same is true for
  `chat.ask` on 2026-08-11 when `default` went completely dead mid-Security+
  generation (every single request rate-limited, even at 4 workers) while
  `account2` succeeded instantly on an identical topic. `summary_parallel.py`
  itself has no rotation logic (unlike `slides_v2.py`); the wrapper loop below
  now does this instead.

## `/root/security3_summary_loop.sh` — what it actually does now

Went through two real bugs before landing on the current version, worth
knowing if it needs touching again:

1. `summary_parallel.py` exits 0 on a clean pass **even when individual
   topics were skipped** after exhausting retries. A naive wrapper that
   treats exit-code-0 as "pack complete" will silently move to the next pack
   while dozens of topics have no `summary_th.md` at all — this is why
   Security+ looked "stuck at 15" instead of erroring.
2. Rotating profiles only *after* a full pass over every pending topic is far
   too slow to react to a dead account — a fully rate-limited account burns
   through 2 retries **per topic** (up to ~2 min each) before the loop even
   checks whether to switch, so detecting a dead `default` against ~220
   pending topics could take the better part of an hour.

Current design: for each cert, probe the current profile on just 3 pending
topics first. 0/3 succeeding means the account is treated as exhausted and
the loop rotates to the next of the 6 profiles immediately (~1 min to detect,
not ~15). Any success on the probe escalates to a full pass with that
profile. If all 6 profiles are dead in a row, it backs off 300s before
retrying the cycle. Log: `/root/security3_summary.log`.

## What's running right now, unattended

- `slides-cycle@ccna.timer` on .153 — every 20 min, drains CCNA's slide queue
  across 6 rotated accounts.
- `/root/security3_summary_loop.sh` (log: `/root/security3_summary.log`) —
  runs summaries for **cc → secplus → cissp in sequence**, 8 workers each,
  refreshing auth before every attempt and rerunning on failure (finished
  topics are skipped, so a rerun costs nothing). This exists because the
  NotebookLM session dies every hour or two and manual resume was the
  bottleneck.
- `slides-cycle@security.timer` is **disabled** — the pack it served is retired.

## Next steps, in priority order

1. **Let CCNA slides drain.** Nothing to do but wait for artifact quota to
   reset; the timer self-heals.
2. **Let the three security summary packs finish** (654 topics total). Check
   with `grep -c '^OK' /root/security3_summary.log` and the `===== pack X
   complete =====` markers.
3. **Enable slide timers for the security packs one at a time** — they share a
   notebook, so `slides-cycle@cc.timer`, then `@secplus`, then `@cissp`; never
   two at once.
4. **Create Pages projects** for cc / secplus / cissp when each has content
   worth publishing, then `./deploy-site.ps1 -Cert cc -Project <name>`.

## Hard-won facts that aren't obvious from the code

- **Prompt templates must live in `certs/<cert>.py`, never in a runner
  script.** `slides_v2.py`, `summary_only.py` and `run.py` each used to carry
  their own hardcoded CCNP-flavoured prompt, and the Security pack silently
  inherited them: 354 of its first 357 summaries contained a fabricated
  "ตัวอย่าง config จริงบน Cisco IOS" section, on topics like "Confidentiality".
  `cert_config.SLIDE_INSTRUCTIONS` / `SUMMARY_PROMPT` are now required per cert
  with **no fallback**, so a new cert fails loudly instead of inheriting the
  wrong flavour.
- `summary_parallel.py` did **not** call `auth_keepalive_loop` (unlike
  `summary_only.py`), which is why long parallel runs kept dying at 15-40
  topics. Fixed 2026-08-11; the wrapper loop above is belt-and-braces on top.
- **Cloudflare Pages rejects the entire deploy if any single file exceeds
  25 MiB.** One NotebookLM deck came back at 25.1 MiB and blocked the whole
  site. `build_dist.py` now skips oversized files with a warning instead.
- NotebookLM's artifact quota (slides/audio/video) is **per Google account,
  not per notebook** — chat/summary calls don't hit this limit at all, which
  is why summaries finish in hours while slides take days.
- Standard-tier Google accounts get much less slide quota than Pro (roughly
  2-3 decks/day vs 15-20), but still contribute — don't drop them from
  rotation.
- A NotebookLM session **created on the remote box** survives for days; one
  **copied in** via `storage_state.json` from another machine has died
  within 1-2 hours every time this was tried. Always use
  `deploy/desktop_login.sh` on the target box itself.
- `slides_v2.py`'s ledger (`<cert>/ledger.json`) is the only reason duplicate
  requests stopped happening. If you're ever tempted to "simplify" by trusting
  `wait_for_completion` again, don't.
- Deploying needs Node ≥22; this machine's shell often defaults to an older
  version via `nvm`. `deploy-site.ps1` works around it without changing the
  user's global Node version.
- On the box, both `ccna/` and `CCNA/` exist (Linux is case-sensitive).
  `certs/ccna.py` points at **`CCNA/output`** — the one with all 226 summaries.
  `ccna/output` is a stale 190-topic leftover.
