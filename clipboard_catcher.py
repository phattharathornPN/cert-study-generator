# -*- coding: utf-8 -*-
"""Watches your clipboard and auto-appends every new copy to a transcript
file -- so you can copy Udemy transcripts one lecture at a time without
alt-tabbing to paste each one manually.

Nothing touches Udemy or the browser at all. It only reads the clipboard
(the same thing any paste operation does) on your own machine.

Usage:
  python clipboard_catcher.py 01_architecture

  Then just Ctrl+C each lecture's transcript on Udemy as normal -- every
  new clipboard capture gets appended to udemy_transcripts/01_architecture.txt
  automatically, separated by a line for you to fill in the lecture title.

  Press Ctrl+C in THIS terminal window (not on the Udemy page) to stop.
"""
import os
import sys
import time

import pyperclip

TRANSCRIPTS_DIR = "udemy_transcripts"
POLL_INTERVAL = 1.0  # seconds
MIN_LENGTH = 40       # ignore tiny copies (accidental clicks, UI text, etc.)


def main():
    if len(sys.argv) < 2:
        print("Usage: python clipboard_catcher.py <section-name>")
        print("  e.g. python clipboard_catcher.py 01_architecture")
        sys.exit(1)

    section = sys.argv[1]
    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
    out_path = os.path.join(TRANSCRIPTS_DIR, f"{section}.txt")

    print(f"Watching clipboard -> appending to {out_path}")
    print("Copy each lecture's transcript on Udemy now (Ctrl+C there as usual).")
    print("Press Ctrl+C HERE (this terminal) when you're done with this section.\n")

    last_seen = pyperclip.paste()
    captured = 0

    try:
        while True:
            time.sleep(POLL_INTERVAL)
            current = pyperclip.paste()
            if current != last_seen and len(current.strip()) >= MIN_LENGTH:
                captured += 1
                with open(out_path, "a", encoding="utf-8") as f:
                    f.write(f"\n\n## Lecture (fill in title) -- captured #{captured}\n")
                    f.write(current.strip())
                    f.write("\n")
                print(f"  [{captured}] captured {len(current)} chars")
            last_seen = current
    except KeyboardInterrupt:
        print(f"\nStopped. {captured} transcript(s) saved to {out_path}")
        print("Open the file and fill in real lecture titles where it says "
              "'(fill in title)', then run upload_transcripts.py when ready.")


if __name__ == "__main__":
    main()
