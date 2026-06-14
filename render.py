from pathlib import Path
import json
import os
import platform

from PIL import Image, ImageDraw, ImageFont

from paths import TODO_FILE, OUTPUT, ensure_migration

WIDTH = 1920
HEIGHT = 1080

BACKGROUND = (205, 235, 205)
TEXT = (30, 55, 45)
ACCENT = (35, 115, 80)

ensure_migration(Path(__file__).parent.resolve())


def _migrate_data(raw_data) -> dict:
    if isinstance(raw_data, list):
        return {"tasks": raw_data, "wallpaper_path": None}
    if isinstance(raw_data, dict):
        if "tasks" not in raw_data:
            return {"tasks": [], "wallpaper_path": None}
        return raw_data
    return {"tasks": [], "wallpaper_path": None}


def _load_raw_data() -> dict:
    if not TODO_FILE.exists():
        return {"tasks": [], "wallpaper_path": None}

    try:
        with open(TODO_FILE, "r", encoding="utf-8") as file:
            content = file.read().strip()
            if not content:
                return {"tasks": [], "wallpaper_path": None}
            return _migrate_data(json.loads(content))
    except json.JSONDecodeError:
        return {"tasks": [], "wallpaper_path": None}


def load_todos() -> list[str]:
    return _load_raw_data().get("tasks", [])


def _font_candidates() -> list[Path]:
    system = platform.system()
    if system == "Windows":
        windir = os.environ.get("WINDIR", r"C:\Windows")
        fonts = Path(windir) / "Fonts"
        return [
            fonts / "arial.ttf",
            fonts / "segoeui.ttf",
            fonts / "calibri.ttf",
        ]

    if system == "Darwin":
        return [
            Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
            Path("/Library/Fonts/Arial.ttf"),
        ]

    return [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/TTF/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
    ]


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in _font_candidates():
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def render_wallpaper(todos: list[str]) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)

    font = load_font(36)
    title_font = load_font(54)

    draw.text((80, 60), "TODO", fill=ACCENT, font=title_font)

    y = 180
    for index, todo in enumerate(todos, start=1):
        draw.text((100, y), f"{index}. {todo}", fill=TEXT, font=font)
        y += 60

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT)


def render_all_tasks_done() -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)

    title_font = load_font(72)
    subtitle_font = load_font(48)

    draw.text((960, 300), "All Tasks Done!", fill=ACCENT, font=title_font, anchor="mm")
    draw.text(
        (960, 500),
        "Take a break, you've earned it!",
        fill=TEXT,
        font=subtitle_font,
        anchor="mm",
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT)


def main() -> None:
    try:
        import sys

        if len(sys.argv) > 1 and sys.argv[1] == "--done":
            render_all_tasks_done()
            print("'All Tasks Done!' image rendered")
        else:
            todos = load_todos()
            render_wallpaper(todos)
            print(f"Wallpaper rendered ({len(todos)} todos)")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
