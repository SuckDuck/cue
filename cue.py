from keyboardinput import KeyboardInput
from talker import Talker
import sys, json, time, textwrap, shutil
import subprocess
from pathlib import Path
import re

NEXT_SHORTCUT = ["d"]

MODEL = Path("en_US-lessac-medium.onnx")
CONFIG = Path("en_US-lessac-medium.onnx.json")

YELLOW = "\033[93m"
RESET = "\033[0m"

def main() -> int:
    if sys.stdin.isatty():
        print("Usage: python cue.py < your_script.json", file=sys.stderr)
        return 1

    script = json.load(sys.stdin)

    if not MODEL.exists() or not CONFIG.exists():
        subprocess.run([
            sys.executable, "-m", "piper.download_voices",
            "en_US-lessac-medium"
        ], check=True)

    keyboard = KeyboardInput()
    talker = Talker()

    section_index = 0
    paragraph_index = 0
    done_speaking = False

    try:
        while True:
            section = script[section_index]

            print("\033[2J\033[H", end="")
            print(f"Press [{'+'.join(NEXT_SHORTCUT).upper()}] to play the next line")
            print("=" * shutil.get_terminal_size().columns + "\n")

            label = section.get("label")
            if label:
                print(f"== {label} ==\n")

            width = max(10, shutil.get_terminal_size().columns - 4)

            for i, paragraph in enumerate(section["content"]):
                marker = ">" if i == paragraph_index else " "
                lines = textwrap.wrap(paragraph, width=width)

                if lines:
                    print(f"{marker} {lines[0]}")
                    for line in lines[1:]:
                        print(f"  {line}")
                else:
                    print(marker)

                print("\n")

            if paragraph_index == len(section["content"]) - 1:
                if section_index + 1 < len(script):
                    next_text = script[section_index + 1]["content"][0]
                    print(f"{YELLOW}NEXT: {next_text}{RESET}")

            if keyboard.is_pressed(*NEXT_SHORTCUT):
                if talker.is_speaking():
                    pass

                elif not done_speaking:
                    text = section["content"][paragraph_index]
                    text = re.sub(r"\(.*?\)", "", text, flags=re.DOTALL)
                    talker.speak(text)
                    done_speaking = True

                else:
                    if paragraph_index + 1 < len(section["content"]):
                        paragraph_index += 1
                    elif section_index + 1 < len(script):
                        section_index += 1
                        paragraph_index = 0
                    else:
                        break

                    done_speaking = False
                    text = script[section_index]["content"][paragraph_index]
                    text = re.sub(r"\(.*?\)", "", text, flags=re.DOTALL)
                    talker.speak(text)
                    done_speaking = True

            keyboard.update()
            time.sleep(1 / 30)

    finally:
        print("\033[2J\033[H", end="")
        keyboard.close()
        talker.stop()

    return 0

if __name__ == "__main__":
    sys.exit(main())