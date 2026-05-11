# render.py

from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1920
HEIGHT = 1080

BACKGROUND = (20, 20, 30)
TEXT = (240, 240, 240)
ACCENT = (120, 200, 255)

# Use absolute paths to work correctly when called from subprocess
PROJECT_DIR = Path(__file__).parent.resolve()
TODO_FILE = PROJECT_DIR / "todos.json"
OUTPUT = PROJECT_DIR / "wallpaper.png"


def load_todos() -> list[str]:
    if not TODO_FILE.exists():
        save_todos([])
        return []

    try:
        with open(TODO_FILE, "r", encoding="utf-8") as file:
            content = file.read().strip()
            if not content:
                save_todos([])
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        save_todos([])
        return []


def save_todos(todos: list[str]) -> None:
    with open(TODO_FILE, "w", encoding="utf-8") as file:
        json.dump(todos, file, indent=2)


def render_wallpaper(todos: list[str]) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)

    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        36,
    )

    title_font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        54,
    )

    draw.text(
        (80, 60),
        "TODO",
        fill=ACCENT,
        font=title_font,
    )

    y = 180

    for index, todo in enumerate(todos, start=1):
        draw.text(
            (100, y),
            f"{index}. {todo}",
            fill=TEXT,
            font=font,
        )

        y += 60

    image.save(OUTPUT)


def main() -> None:
    try:
        todos = load_todos()
        render_wallpaper(todos)
        print(f"✓ Wallpaper rendered ({len(todos)} todos)")
    except FileNotFoundError as e:
        print(f"✗ Font not found: {e}")
        print("  Install DejaVuSans font: sudo apt install fonts-dejavu")
        exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()