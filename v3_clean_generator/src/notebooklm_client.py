import asyncio
from notebooklm import NotebookLMClient

class AuthExpiredError(Exception):
    pass

class ResilientNotebookClient:
    def __init__(self, notebook_id: str, retry_limit: int = 2):
        self.notebook_id = notebook_id
        self.retry_limit = retry_limit

    async def _run_with_retry(self, coro_fn, label: str):
        rate_limit_retries = 5
        attempt = 0
        while True:
            try:
                return await coro_fn()
            except Exception as e:
                err_str = str(e)
                if "Unauthenticated" in err_str or "Authentication expired" in err_str:
                    raise AuthExpiredError(
                        f"{label}: session expired. Run 'notebooklm auth refresh' or "
                        f"'notebooklm login', then resume with --start-id."
                    ) from e
                if "RateLimitError" in err_str or "RateLimit" in type(e).__name__:
                    if rate_limit_retries > 0:
                        rate_limit_retries -= 1
                        print(f"  WARNING: {label} rate limited, waiting 90s before retry...")
                        await asyncio.sleep(90)
                        continue
                    print(f"  ERROR: {label} skipped (rate limit exhausted): {e}")
                    return None
                if attempt < self.retry_limit:
                    attempt += 1
                    print(f"  WARNING: {label} failed ({e}), retrying {attempt}/{self.retry_limit}...")
                    await asyncio.sleep(5)
                else:
                    print(f"  ERROR: {label} skipped after {self.retry_limit} retries: {e}")
                    return None

    # Context manager implementation to wrap NotebookLMClient
    async def __aenter__(self):
        self.ctx = NotebookLMClient.from_storage()
        self.client = await self.ctx.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.ctx.__aexit__(exc_type, exc_val, exc_tb)

    async def ask(self, prompt: str):
        return await self._run_with_retry(
            lambda: self.client.chat.ask(self.notebook_id, prompt),
            "chat.ask"
        )

    async def create_note(self, title: str, content: str):
        return await self._run_with_retry(
            lambda: self.client.notes.create(self.notebook_id, title=title, content=content),
            "notes.create"
        )

    async def generate_slide_deck(self, language: str, instructions: str, slide_format, slide_length):
        return await self._run_with_retry(
            lambda: self.client.artifacts.generate_slide_deck(
                self.notebook_id,
                language=language,
                instructions=instructions,
                slide_format=slide_format,
                slide_length=slide_length,
            ),
            "generate_slide"
        )

    async def generate_audio(self, language: str, instructions: str, audio_format, audio_length):
        return await self._run_with_retry(
            lambda: self.client.artifacts.generate_audio(
                self.notebook_id,
                language=language,
                instructions=instructions,
                audio_format=audio_format,
                audio_length=audio_length,
            ),
            "generate_audio"
        )

    async def generate_flashcards(self, instructions: str, quantity):
        return await self._run_with_retry(
            lambda: self.client.artifacts.generate_flashcards(
                self.notebook_id,
                instructions=instructions,
                quantity=quantity,
            ),
            "generate_flashcards"
        )

    async def wait_for_completion(self, task_id: str, timeout: int = 600):
        return await self._run_with_retry(
            lambda: self.client.artifacts.wait_for_completion(self.notebook_id, task_id, timeout=timeout),
            "wait_for_completion"
        )

    async def download_slide_deck(self, output_path: str, artifact_id: str, output_format: str):
        return await self._run_with_retry(
            lambda: self.client.artifacts.download_slide_deck(
                self.notebook_id, output_path, artifact_id=artifact_id, output_format=output_format
            ), f"download slide {output_format}"
        )

    async def download_audio(self, output_path: str, artifact_id: str):
        return await self._run_with_retry(
            lambda: self.client.artifacts.download_audio(
                self.notebook_id, output_path, artifact_id=artifact_id
            ), "download audio"
        )

    async def download_flashcards(self, output_path: str, artifact_id: str, output_format: str):
        return await self._run_with_retry(
            lambda: self.client.artifacts.download_flashcards(
                self.notebook_id, output_path, artifact_id=artifact_id, output_format=output_format
            ), f"download flashcards {output_format}"
        )
