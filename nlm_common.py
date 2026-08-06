# -*- coding: utf-8 -*-
"""Shared auth handling for the generator scripts.

These used to live inside slides_only.py, which meant every summary script
imported a whole slide runner to get at four helpers -- and left two rival
slide runners in the tree, which is how three of them ended up racing each
other over one notebook. The slide runners are gone; the helpers are here.
"""
import asyncio
import sys

AUTH_REFRESH_INTERVAL = 780  # ~13 min, inside the 15-20 min recommended cadence
RETRY_LIMIT = 1


class AuthExpiredError(Exception):
    """The session died mid-run. Never swallow this into a per-topic skip."""


def is_auth_error(exc: BaseException) -> bool:
    """True if exc, or anything it wraps, is an expired-session failure.

    Library errors such as SourceAddError bury the real RPCError in .cause /
    __cause__ and replace the message, so checking str() on the outer
    exception alone misses them -- which is how one run silently skipped 19
    topics instead of stopping.
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


async def run_with_retry(coro_fn, label: str):
    """Retry transient failures; auth failures abort the caller."""
    rate_limit_retries = 5
    attempt = 0
    while True:
        try:
            return await coro_fn()
        except Exception as e:
            if is_auth_error(e):
                raise AuthExpiredError(
                    f"{label}: session expired. Run 'notebooklm auth refresh' or "
                    f"'notebooklm login', then resume with --start-id."
                ) from e
            if "RateLimitError" in str(e) or "RateLimit" in type(e).__name__:
                if rate_limit_retries > 0:
                    rate_limit_retries -= 1
                    print(f"  WARNING: {label} rate limited, waiting 90s before retry...")
                    await asyncio.sleep(90)
                    continue
                print(f"  ERROR: {label} skipped (rate limit exhausted): {e}")
                return None
            if attempt < RETRY_LIMIT:
                attempt += 1
                print(f"  WARNING: {label} failed ({e}), retrying...")
                await asyncio.sleep(5)
            else:
                print(f"  ERROR: {label} skipped: {e}")
                return None


async def auth_keepalive_loop(profile: str | None):
    """Refresh the token on a timer for the length of a long run.

    Invoked via `python -m notebooklm` rather than the notebooklm.exe shim --
    Windows Smart App Control blocks the unsigned .exe on some machines.
    """
    profile_args = ["-p", profile] if profile else []
    first = True
    while True:
        # Refresh immediately on the first pass: the token may already be
        # stale when the run starts, and sleeping first would let the whole
        # run fail before we ever fix it.
        if not first:
            await asyncio.sleep(AUTH_REFRESH_INTERVAL)
        first = False
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "notebooklm", *profile_args,
                "auth", "refresh", "--quiet",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()
            if proc.returncode == 0:
                print("  [auth-keepalive] token refreshed OK")
            else:
                print(f"  [auth-keepalive] refresh failed: "
                      f"{stderr.decode(errors='ignore').strip()}")
        except Exception as e:
            print(f"  [auth-keepalive] error: {e}")
