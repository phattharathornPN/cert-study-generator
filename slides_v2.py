# -*- coding: utf-8 -*-
"""Slide generation that survives the API lying to it.

The rule this file is built on: **the disk is the truth and the API is only
advice.** Every earlier runner did the opposite -- it believed
`wait_for_completion` when it said an artifact had disappeared, believed a
refusal meant the day's quota was gone, and kept nothing on disk that could
contradict either. Three days of that produced 46 decks, re-requested some
topics four times over, and left 324 orphaned sources behind.

So the work is split into phases that each finish before the next begins, and
every state change is written to the ledger *before* the API call it describes:

    PLAN     read the disk and the ledger; decide what is missing. No network.
    KICKOFF  per topic: upload the summary as a pinned source, request the
             deck, and record its task_id immediately. Never waits.
    COLLECT  per recorded task: try to download it. Success writes the files,
             then deletes the artifact and the pinned source. Failure is left
             alone for the next cycle -- collection never re-requests anything.

Why the split matters: a crash, a power cut or a poll that times out can no
longer lose a task_id, and because COLLECT has no ability to call generate, a
broken poll can never again turn into a duplicate request. Quota is the
expensive resource here; spending it twice on one topic is the worst failure
mode available.

Two things fall out of keeping task ids on disk:

  * artifacts can be deleted by id, so the notebook never accumulates the
    backlog that makes LIST_ARTIFACTS time out (which is what killed v1);
  * a pinned source whose upload timed out is still known by title, so it can
    be swept even though the reply carrying its id was lost.

Accounts are worked in turn, not together. The allowance is per Google
account, so five accounts are five allowances -- but asking concurrently just
means five callers finding the same empty bucket at the same moment. Each
account is drained until it refuses eight in a row, then the next takes over.

Usage:
    python slides_v2.py                     one cycle: kickoff, collect, sweep
    python slides_v2.py --kickoff-only
    python slides_v2.py --collect-only
    python slides_v2.py --profiles default,account2,account3
    python slides_v2.py --max-kickoff 20    stop after N requests this cycle
    python slides_v2.py --only 02_05,02_06
"""
import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone

from notebooklm import NotebookLMClient
from notebooklm.artifacts import with_rate_limit_retry
from notebooklm.exceptions import (
    ArtifactNotFoundError,
    ArtifactNotReadyError,
    AuthError,
    RateLimitError,
)
from notebooklm.rpc.types import SlideDeckFormat, SlideDeckLength

from run import NOTEBOOK_ID, OUTPUT_DIR, SLIDE_FORMATS, TOPICS, topic_to_slug
from cert_config import EXAM_NAME, SITE_DIR, SLIDE_INSTRUCTIONS


def is_auth_error(exc: BaseException) -> bool:
    """True if exc, or anything it wraps, is an expired-session failure.

    Library errors such as SourceAddError bury the real RPCError in .cause /
    __cause__ and replace the message, so checking str() on the outer
    exception misses them -- which is how one run silently skipped 19 topics
    instead of stopping.
    """
    seen: set[int] = set()
    cur: BaseException | None = exc
    while cur is not None and id(cur) not in seen:
        seen.add(id(cur))
        text = str(cur)
        if "Unauthenticated" in text or "Authentication expired" in text:
            return True
        if getattr(cur, "rpc_code", None) in (16, "16"):
            return True
        cur = cur.__cause__ or getattr(cur, "cause", None)
    return False


# Slide instructions come from the active cert (certs/<cert>.py), not from
# here. This used to be a single hardcoded template asking every cert for
# "Cisco IOS / IOS-XE" config examples -- harmless for CCNP/CCNA, but it told
# the AI to hunt for Cisco configs on CISSP governance topics too, since
# Security shared this file. Each cert now owns the kind of worked example
# that actually fits its exam.

LEDGER_PATH = os.path.join(SITE_DIR, "ledger.json")
LOCK_PATH = os.path.join(SITE_DIR, ".slides.lock")

# with_rate_limit_retry backs off 60s, then 120s. One retry is enough here
# because patience lives in the timer, not inside a topic: the cycle runs
# again in twenty minutes regardless, so waiting twelve minutes on one topic
# only means the whole cycle overruns and gets killed mid-request -- which is
# exactly what happened with four retries, leaving sources stranded behind
# entries stuck in "requesting".
RATE_LIMIT_RETRIES = 1
SLEEP_BETWEEN_TOPICS = 20      # deliberate pacing; the docs ask for it
COLLECT_GIVE_UP_AFTER = 12     # cycles before a task is written off


# --------------------------------------------------------------------------
# ledger
# --------------------------------------------------------------------------

def load_ledger() -> dict:
    if not os.path.exists(LEDGER_PATH):
        return {}
    with open(LEDGER_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_ledger(ledger: dict) -> None:
    """Write atomically -- a half-written ledger is worse than none."""
    os.makedirs(os.path.dirname(LEDGER_PATH) or ".", exist_ok=True)
    tmp = LEDGER_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(ledger, f, ensure_ascii=False, indent=2, sort_keys=True)
    os.replace(tmp, LEDGER_PATH)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def record(ledger: dict, tid: str, **fields) -> None:
    """Update one topic's entry and flush. Called BEFORE the API call it describes."""
    entry = ledger.setdefault(tid, {})
    entry.update(fields)
    entry["updated_at"] = now()
    save_ledger(ledger)


# --------------------------------------------------------------------------
# single instance
# --------------------------------------------------------------------------

class AlreadyRunning(RuntimeError):
    pass


def acquire_lock() -> None:
    """Refuse to start when another cycle owns this pack.

    Three runners once shared one notebook and handed each other the same
    topics; one of them also swept the sources the others were mid-way
    through using. A pid file is enough here -- the contenders are always on
    the same host.
    """
    os.makedirs(os.path.dirname(LOCK_PATH) or ".", exist_ok=True)
    if os.path.exists(LOCK_PATH):
        try:
            with open(LOCK_PATH, encoding="utf-8") as f:
                pid = int(f.read().strip())
        except (ValueError, OSError):
            pid = -1
        if pid > 0 and _pid_alive(pid):
            raise AlreadyRunning(f"another cycle is running (pid {pid})")
        print(f"clearing stale lock from pid {pid}", flush=True)
    with open(LOCK_PATH, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))


def release_lock() -> None:
    try:
        os.unlink(LOCK_PATH)
    except OSError:
        pass


def _pid_alive(pid: int) -> bool:
    if os.name == "nt":
        import subprocess
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"],
                             capture_output=True, text=True).stdout
        return str(pid) in out
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


# --------------------------------------------------------------------------
# plan
# --------------------------------------------------------------------------

def folder_for(t: dict) -> str:
    return os.path.join(OUTPUT_DIR, f"{t['id']}_{topic_to_slug(t['topic'])}")


def slides_on_disk(t: dict) -> bool:
    folder = folder_for(t)
    return all(
        os.path.exists(os.path.join(folder, f"slide.{fmt}"))
        and os.path.getsize(os.path.join(folder, f"slide.{fmt}")) > 0
        for fmt in SLIDE_FORMATS
    )


def has_summary(t: dict) -> bool:
    p = os.path.join(folder_for(t), "summary_th.md")
    return os.path.exists(p) and os.path.getsize(p) > 0


def plan(ledger: dict, only: set | None):
    """Split the topic list by what the disk says, then what the ledger says."""
    done, awaiting, to_kick, no_summary = [], [], [], []
    for t in TOPICS:
        if only and t["id"] not in only:
            continue
        if slides_on_disk(t):
            done.append(t)
            continue
        if not has_summary(t):
            no_summary.append(t)
            continue
        entry = ledger.get(t["id"], {})
        if entry.get("task_id") and entry.get("state") != "written_off":
            awaiting.append(t)
        else:
            to_kick.append(t)
    return done, awaiting, to_kick, no_summary


# --------------------------------------------------------------------------
# kickoff
# --------------------------------------------------------------------------

async def kickoff_one(client, t: dict, ledger: dict) -> str:
    """Request one deck. Returns 'ok', 'refused', or 'skipped'."""
    tid, topic = t["id"], t["topic"]
    folder = folder_for(t)
    title = f"[SRC {tid}] {topic}"

    with open(os.path.join(folder, "summary_th.md"), encoding="utf-8") as f:
        content = f.read()

    # Write the title first. An add_text that times out still creates the
    # source server-side while the reply carrying its id is lost -- 308 of
    # those left 324 strays and pushed the notebook past its 300-source cap.
    # Knowing the title is enough to sweep it later.
    record(ledger, tid, state="sourcing", source_title=title, topic=topic)

    src = await client.sources.add_text(NOTEBOOK_ID, title, content, wait=True)
    record(ledger, tid, state="sourced", source_id=src.id)

    record(ledger, tid, state="requesting")
    status = await with_rate_limit_retry(
        lambda: client.artifacts.generate_slide_deck(
            NOTEBOOK_ID,
            source_ids=[src.id],
            language="th",
            instructions=SLIDE_INSTRUCTIONS(topic),
            slide_format=SlideDeckFormat.DETAILED_DECK,
            slide_length=SlideDeckLength.DEFAULT,
        ),
        max_retries=RATE_LIMIT_RETRIES,
    )

    # A refusal comes back as a status with an empty task_id rather than an
    # exception on this path. Treat it as a refusal, not as a task to poll:
    # polling an id that was never issued is what generated the phantom
    # "artifact removed" verdicts and hammered LIST_ARTIFACTS until it broke.
    task_id = getattr(status, "task_id", "") if status else ""
    if not task_id:
        err = (getattr(status, "error", "") or "")[:70]
        print(f"  [{tid}] refused -- {err}", flush=True)
        record(ledger, tid, state="refused", last_error=err)
        await drop_source(client, ledger, tid, "refused request")
        return "refused"

    record(ledger, tid, state="kicked", task_id=task_id,
           kicked_at=now(), collect_attempts=0)
    print(f"  [{tid}] requested, task {task_id[:8]}", flush=True)
    return "ok"


# --------------------------------------------------------------------------
# collect
# --------------------------------------------------------------------------

async def collect_one(client, t: dict, ledger: dict) -> str:
    """Try to download an already-requested deck. Never requests anything."""
    tid = t["id"]
    entry = ledger.get(tid, {})
    task_id = entry.get("task_id")
    folder = folder_for(t)
    os.makedirs(folder, exist_ok=True)

    got = []
    for fmt in SLIDE_FORMATS:
        out = os.path.join(folder, f"slide.{fmt}")
        if os.path.exists(out) and os.path.getsize(out) > 0:
            got.append(fmt)
            continue
        try:
            await client.artifacts.download_slide_deck(
                NOTEBOOK_ID, out, artifact_id=task_id, output_format=fmt)
            got.append(fmt)
        except (ArtifactNotReadyError, ArtifactNotFoundError, RateLimitError) as e:
            # Still building, or the server is busy. Neither is a reason to
            # spend quota again -- leave the task alone and come back.
            attempts = entry.get("collect_attempts", 0) + 1
            record(ledger, tid, collect_attempts=attempts,
                   last_error=f"{type(e).__name__}: {str(e)[:60]}")
            if attempts >= COLLECT_GIVE_UP_AFTER:
                print(f"  [{tid}] no deck after {attempts} tries -- will re-request",
                      flush=True)
                record(ledger, tid, state="written_off", task_id=None)
                await drop_source(client, ledger, tid, "written off")
                return "written_off"
            return "pending"

    record(ledger, tid, state="collected", collected_at=now())
    print(f"  [{tid}] collected " + " + ".join(f"slide.{f}" for f in got), flush=True)

    # The artifact has served its purpose. Deleting it by id keeps the
    # notebook's artifact list short -- v1's grew until LIST_ARTIFACTS timed
    # out at 30s and every subsequent generation looked like a failure. This
    # is only possible because the id is on disk; listing to find it is the
    # very call that breaks.
    try:
        await client.artifacts.delete(NOTEBOOK_ID, task_id)
    except Exception as e:
        print(f"  [{tid}] could not delete artifact: {str(e)[:60]}", flush=True)

    await drop_source(client, ledger, tid, "collected")
    return "ok"


# --------------------------------------------------------------------------
# sweep
# --------------------------------------------------------------------------

async def drop_source(client, ledger: dict, tid: str, why: str) -> None:
    """Delete a topic's pinned source; it scopes one deck and nothing else."""
    entry = ledger.get(tid, {})
    sid = entry.get("source_id")
    if not sid:
        return
    try:
        await client.sources.delete(NOTEBOOK_ID, sid)
        record(ledger, tid, source_id=None, source_dropped=why)
    except Exception as e:
        print(f"  [{tid}] could not drop source: {str(e)[:60]}", flush=True)


async def sweep_orphan_sources(client, ledger: dict) -> None:
    """Remove [SRC] sources no live ledger entry still needs.

    Catches the ones whose upload timed out before an id came back, which no
    amount of per-topic bookkeeping can delete directly.
    """
    live = {e.get("source_id") for e in ledger.values() if e.get("source_id")}
    keep_titles = {e.get("source_title") for e in ledger.values()
                   if e.get("source_id")}
    try:
        sources = await client.sources.list(NOTEBOOK_ID)
    except Exception as e:
        print(f"sweep skipped: {str(e)[:70]}", flush=True)
        return
    stale = [s for s in sources
             if (s.title or "").startswith("[SRC ")
             and s.id not in live and s.title not in keep_titles]
    if not stale:
        return
    print(f"sweeping {len(stale)} orphan source(s)", flush=True)
    for s in stale:
        try:
            await client.sources.delete(NOTEBOOK_ID, s.id)
        except Exception as e:
            print(f"  could not sweep {s.title}: {str(e)[:50]}", flush=True)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def arg(flag, default=None):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default


# Two refusals is enough to call an account dry. Eight was chosen when a
# refusal was cheap; with a 60s backoff behind each one it meant eight
# minutes per account and forty for a full sweep of five, so the cycle
# overran its slot and got killed part-way through a request. A dry account
# refuses the first thing it is asked, every time -- there is nothing to
# learn from asking six more.
REFUSALS_BEFORE_NEXT_ACCOUNT = 2


async def collect_all(client, awaiting, ledger) -> int | None:
    """Download everything already requested. Returns 2 if the session died."""
    for t in awaiting:
        try:
            await collect_one(client, t, ledger)
        except Exception as e:
            if is_auth_error(e) or isinstance(e, AuthError):
                return 2
            print(f"  [{t['id']}] collect error: {str(e)[:70]}", flush=True)
    return None


async def kickoff_with(client, queue, ledger, label) -> str:
    """Request decks on one account until it starts refusing.

    Returns why it stopped: 'empty', 'spent', or 'auth'.
    """
    refused_in_a_row = 0
    while queue:
        t = queue[0]
        try:
            outcome = await kickoff_one(client, t, ledger)
        except Exception as e:
            if is_auth_error(e) or isinstance(e, AuthError):
                # Never walk silently past this -- treating an expired session
                # as a per-topic error once skipped 19 topics without a word.
                print(f"  {label}: session expired", flush=True)
                return "auth"
            print(f"  [{t['id']}] error: {str(e)[:70]}", flush=True)
            await drop_source(client, ledger, t["id"], "error")
            outcome = "refused"

        if outcome == "refused":
            # Leave it in the queue -- rotate it to the back rather than
            # discarding it. A topic this account was refused on is exactly
            # the kind of work the NEXT account should get a shot at; popping
            # unconditionally here meant a refusal permanently removed the
            # topic from this cycle's queue, so once the queue held no more
            # topics than REFUSALS_BEFORE_NEXT_ACCOUNT, the "allowance spent,
            # try the next account" handoff below had nothing left to hand
            # over -- every account after the first was rotated through with
            # an empty queue. That is why the last two topics of CCNP v2 sat
            # refused by "default" alone for hours after account6 was added:
            # accounts 2-6 were never actually tried on them.
            refused_in_a_row += 1
            queue.append(queue.pop(0))
        else:
            refused_in_a_row = 0
            queue.pop(0)

        if refused_in_a_row >= REFUSALS_BEFORE_NEXT_ACCOUNT:
            print(f"  {label}: {refused_in_a_row} refusals in a row -- allowance spent",
                  flush=True)
            return "spent"
        if queue:
            await asyncio.sleep(SLEEP_BETWEEN_TOPICS)
    return "empty"


async def main() -> int:
    # Accounts are drained in turn, not in parallel. The limit is per Google
    # account, so five accounts really are five allowances -- but running them
    # concurrently only means five callers discovering the same empty bucket
    # at once. One at a time, each until it refuses, uses the same capacity
    # without the noise.
    raw = arg("--profiles") or arg("--profile") or ""
    profiles = [p.strip() or None for p in raw.split(",")] if raw else [None]
    only = set(arg("--only").split(",")) if arg("--only") else None
    max_kickoff = int(arg("--max-kickoff", "0")) or None
    do_kick = "--collect-only" not in sys.argv
    do_collect = "--kickoff-only" not in sys.argv

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ledger = load_ledger()

    # The disk outranks the ledger: anything already downloaded is finished,
    # whatever the ledger believes.
    for t in TOPICS:
        if slides_on_disk(t) and ledger.get(t["id"], {}).get("state") not in (None, "collected"):
            record(ledger, t["id"], state="collected", note="found on disk")

    # A cycle that was killed part-way leaves entries frozen mid-request. They
    # carry a source_id but no task_id, so nothing can collect them and the
    # sweep -- which spares any source the ledger still claims -- would keep
    # their sources alive forever. Releasing the claim lets the sweep take
    # them and the topic be requested again. Losing one request is the right
    # trade: the alternative leaks a source per interruption, and that cap is
    # what took the notebook out of service once already.
    stranded = [tid for tid, e in ledger.items()
                if e.get("state") in ("sourcing", "sourced", "requesting", "interrupted")]
    for tid in stranded:
        record(ledger, tid, state="interrupted", source_id=None,
               note="cycle ended mid-request; source released to the sweep")
    if stranded:
        print(f"releasing {len(stranded)} interrupted request(s): {', '.join(sorted(stranded))}")

    done, awaiting, to_kick, no_summary = plan(ledger, only)
    shown = ", ".join(p or "default" for p in profiles)
    print(f"{EXAM_NAME}: {len(done)} done, {len(awaiting)} awaiting collection, "
          f"{len(to_kick)} to request"
          + (f", {len(no_summary)} without a summary" if no_summary else "")
          + f"  [accounts: {shown}]")

    if not awaiting and not to_kick:
        print("Nothing to do.")
        return 0

    queue = to_kick[:max_kickoff] if max_kickoff else list(to_kick)
    collected = False
    swept = False
    dead_accounts = 0

    for profile in profiles:
        label = profile or "default"
        if not queue and collected and swept:
            break
        try:
            async with NotebookLMClient.from_storage(profile=profile) as client:
                # Collect once, on the first account that opens -- artifacts
                # belong to the notebook, not to whoever requested them.
                if do_collect and awaiting and not collected:
                    print(f"\n== collecting {len(awaiting)} requested deck(s) [{label}]")
                    if await collect_all(client, awaiting, ledger) == 2:
                        print(f"  {label}: session expired during collection")
                        dead_accounts += 1
                        continue
                    collected = True

                if do_kick and queue:
                    print(f"\n== requesting on {label} ({len(queue)} left)")
                    why = await kickoff_with(client, queue, ledger, label)
                    if why == "auth":
                        dead_accounts += 1
                        continue

                if not swept:
                    await sweep_orphan_sources(client, ledger)
                    swept = True
        except Exception as e:
            print(f"== skipping {label}: {str(e)[:80]}", flush=True)
            dead_accounts += 1
            continue

    if dead_accounts == len(profiles):
        print("\nSTOPPED: every account failed to authenticate -- sign in again.")
        save_ledger(ledger)
        return 2

    save_ledger(ledger)
    done, awaiting, to_kick, _ = plan(ledger, only)
    print(f"\nNow: {len(done)} on disk, {len(awaiting)} awaiting collection, "
          f"{len(to_kick)} still to request.")
    return 0


if __name__ == "__main__":
    try:
        acquire_lock()
    except AlreadyRunning as e:
        print(f"STOPPED: {e}")
        sys.exit(1)
    try:
        sys.exit(asyncio.run(main()))
    finally:
        release_lock()
