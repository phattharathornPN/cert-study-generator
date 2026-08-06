import argparse
import asyncio
import os
import sys

from src.config import TOPICS, OUTPUT_DIR, get_notebook_id
from src.notebooklm_client import ResilientNotebookClient, AuthExpiredError
from src.generator import TopicGenerator, SLEEP_BETWEEN_TOPICS

async def main():
    parser = argparse.ArgumentParser(description="NotebookLM Generator CLI")
    parser.add_argument("--run-all", action="store_true", help="Run the generator for all topics")
    parser.add_argument("--run-topic", type=str, help="Run the generator for a specific topic ID (e.g. 01_01)")
    parser.add_argument("--resume", action="store_true", help="Resume generation (skips existing artifacts)")
    parser.add_argument("--force", action="store_true", help="Force regenerate artifacts even if they exist")
    parser.add_argument("--output-dir", type=str, default=OUTPUT_DIR, help="Output directory")
    parser.add_argument("--skip-slides", action="store_true", help="Skip generating slides")
    parser.add_argument("--skip-audio", action="store_true", help="Skip generating audio")
    parser.add_argument("--skip-flashcards", action="store_true", help="Skip generating flashcards")

    args = parser.parse_args()

    if not (args.run_all or args.run_topic or args.resume):
        parser.print_help()
        sys.exit(1)

    notebook_id = get_notebook_id()
    
    # We will resolve output path relative to this script or current working dir.
    # To keep things clean, lets use absolute path if provided or relative to where main is run
    output_path = os.path.abspath(args.output_dir)
    os.makedirs(output_path, exist_ok=True)
    
    generator = TopicGenerator(output_dir=output_path)
    
    target_topics = []
    if args.run_topic:
        target_topics = [t for t in TOPICS if t["id"] == args.run_topic]
        if not target_topics:
            print(f"ERROR: Topic ID '{args.run_topic}' not found.")
            sys.exit(1)
    else:
        target_topics = TOPICS

    async with ResilientNotebookClient(notebook_id) as client:
        total = len(target_topics)
        for i, t in enumerate(target_topics):
            generated_any = False
            try:
                # With args.resume, the logic inside process_topic skips existing artifacts natively if force is False
                generated_any = await generator.process_topic(
                    client, t, force=args.force,
                    skip_slides=args.skip_slides,
                    skip_audio=args.skip_audio,
                    skip_flashcards=args.skip_flashcards
                )
            except AuthExpiredError as e:
                print(f"\n  STOPPED: {e}")
                sys.exit(1)
            except Exception as e:
                print(f"  ERROR: topic {t['id']} failed entirely: {e}")

            remaining = total - i - 1
            if remaining > 0 and not args.run_topic:
                if generated_any:
                    print(f"\n  {remaining} topics remaining. Sleeping {SLEEP_BETWEEN_TOPICS}s...")
                    await asyncio.sleep(SLEEP_BETWEEN_TOPICS)
                else:
                    print(f"\n  {remaining} topics remaining. (No API calls made, skipping sleep)")

    print("\nGeneration complete!")

if __name__ == "__main__":
    asyncio.run(main())
