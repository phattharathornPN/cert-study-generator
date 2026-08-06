import os
import asyncio
from notebooklm.rpc.types import (
    AudioFormat,
    AudioLength,
    QuizQuantity,
    SlideDeckFormat,
    SlideDeckLength,
)

from src.config import (
    build_focus_prompt,
    build_slide_instructions,
    build_audio_instructions,
    build_flashcards_instructions,
)
from src.notebooklm_client import ResilientNotebookClient

SLEEP_BETWEEN_ARTIFACTS = 15
SLEEP_AFTER_AUDIO = 30
SLEEP_BETWEEN_TOPICS = 20

class TopicGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    def is_artifact_exists(self, filepath: str) -> bool:
        return os.path.exists(filepath) and os.path.getsize(filepath) > 0

    async def process_topic(self, client: ResilientNotebookClient, topic_data: dict, force: bool = False, skip_audio: bool = False, skip_flashcards: bool = False, skip_slides: bool = False) -> bool:
        tid = topic_data["id"]
        topic = topic_data["topic"]
        slug = topic_data["slug"]
        
        folder_name = f"{tid}_{slug}"
        folder_path = os.path.join(self.output_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        print(f"\n{'=' * 60}")
        print(f"[{tid}] {topic}")
        print(f"{'=' * 60}")

        made_api_calls = False

        # 1. Focused Summary & Note
        summary_path = os.path.join(folder_path, "summary_th.md")
        if not self.is_artifact_exists(summary_path) or force:
            print("  Generating focused summary...")
            result = await client.ask(build_focus_prompt(topic))
            if result:
                with open(summary_path, "w", encoding="utf-8") as f:
                    f.write(f"# {topic}\n\n{result.answer}")
                await client.create_note(title=f"[Focus] {topic}", content=result.answer)
                print("  OK: summary_th.md saved + note created")
            made_api_calls = True
            await asyncio.sleep(SLEEP_BETWEEN_ARTIFACTS)
        else:
            print("  SKIP: summary_th.md already exists")

        # 2. Slide Deck
        slide_pdf_path = os.path.join(folder_path, "slide.pdf")
        slide_pptx_path = os.path.join(folder_path, "slide.pptx")
        if skip_slides:
            print("  SKIP: slides (skipped by user)")
        elif not (self.is_artifact_exists(slide_pdf_path) and self.is_artifact_exists(slide_pptx_path)) or force:
            print("  Generating slide...")
            status = await client.generate_slide_deck(
                language="th",
                instructions=build_slide_instructions(topic),
                slide_format=SlideDeckFormat.DETAILED_DECK,
                slide_length=SlideDeckLength.DEFAULT,
            )
            if status:
                done = await client.wait_for_completion(status.task_id)
                if done and done.is_complete:
                    await client.download_slide_deck(slide_pdf_path, artifact_id=status.task_id, output_format="pdf")
                    await client.download_slide_deck(slide_pptx_path, artifact_id=status.task_id, output_format="pptx")
                    print("  OK: slide.pdf + slide.pptx")
                elif done:
                    print(f"  ERROR: slide generation did not complete (status={done.status})")
            else:
                print("  ERROR: slide generation failed to start")
            made_api_calls = True
            await asyncio.sleep(SLEEP_BETWEEN_ARTIFACTS)
        else:
            print("  SKIP: slide.pdf and slide.pptx already exist")

        # 3. Audio
        audio_path = os.path.join(folder_path, "audio.mp3")
        if skip_audio:
            print("  SKIP: audio (skipped by user)")
        elif not self.is_artifact_exists(audio_path) or force:
            print("  Generating audio...")
            status = await client.generate_audio(
                language="th",
                instructions=build_audio_instructions(topic),
                audio_format=AudioFormat.DEEP_DIVE,
                audio_length=AudioLength.DEFAULT,
            )
            if status:
                done = await client.wait_for_completion(status.task_id)
                if done and done.is_complete:
                    await client.download_audio(audio_path, artifact_id=status.task_id)
                    print("  OK: audio.mp3")
                elif done:
                    print(f"  ERROR: audio generation did not complete (status={done.status})")
            else:
                print("  ERROR: audio generation failed to start")
            made_api_calls = True
            await asyncio.sleep(SLEEP_AFTER_AUDIO)
        else:
            print("  SKIP: audio.mp3 already exists")

        # 4. Flashcards
        flashcards_path = os.path.join(folder_path, "flashcards.json")
        if skip_flashcards:
            print("  SKIP: flashcards (skipped by user)")
        elif not self.is_artifact_exists(flashcards_path) or force:
            print("  Generating flashcards...")
            status = await client.generate_flashcards(
                instructions=build_flashcards_instructions(topic),
                quantity=QuizQuantity.MORE,
            )
            if status:
                done = await client.wait_for_completion(status.task_id)
                if done and done.is_complete:
                    await client.download_flashcards(flashcards_path, artifact_id=status.task_id, output_format="json")
                    print("  OK: flashcards.json")
                elif done:
                    print(f"  ERROR: flashcards generation did not complete (status={done.status})")
            else:
                print("  ERROR: flashcards generation failed to start")
            made_api_calls = True
            await asyncio.sleep(SLEEP_BETWEEN_ARTIFACTS)
        else:
            print("  SKIP: flashcards.json already exists")
            
        return made_api_calls

