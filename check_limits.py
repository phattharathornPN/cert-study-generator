"""Check NotebookLM account tier + limits (notebook/source count caps).

Note: this does NOT expose the per-day "generate artifact" (slide/audio/
flashcard) quota -- NotebookLM does not return that number via any RPC the
library wraps. The only way to know that quota is empty is the
RateLimitError you already see when generate_slide_deck() is called.
This script just shows what IS queryable: your plan tier and notebook/
source limits.
"""
import asyncio
import os
import sys
from notebooklm import NotebookLMClient

NOTEBOOK_ID = os.environ.get("NOTEBOOK_ID")
if not NOTEBOOK_ID:
    print("ERROR: NOTEBOOK_ID environment variable not set (see .env.example).")
    sys.exit(1)


async def main():
    async with NotebookLMClient.from_storage() as client:
        tier = await client.settings.get_account_tier()
        limits = await client.settings.get_account_limits()
        sources = await client.sources.list(NOTEBOOK_ID)

        print(f"Account tier:     {tier}")
        print(f"Notebook limit:   {limits.notebook_limit}")
        print(f"Source limit:     {limits.source_limit}")
        print(f"Sources in notebook: {len(sources)} / {limits.source_limit}")


asyncio.run(main())
